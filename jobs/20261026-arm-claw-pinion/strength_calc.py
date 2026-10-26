"""Strength check, round 2: jobs/20261026-arm-claw-pinion (20-tooth module-1 pinion on the claw MG90S).

Run from the project root:  python3 jobs/20261026-arm-claw-pinion/strength_calc.py
Plain python3 (no build123d): the parameters are read from claw_frame.py, this job's model.py and
tools/hobby_parts.py with the ast module, and the tooth outline comes from tools/gears.py's gear_outline /
rack_outline, whose source is executed on its own (they are pure math).

Method (strength-analyst): allowables are the strength-checks PLACEHOLDER PETG values (library/materials.csv has
no measured row), so NEEDS_TEST is the best verdict possible. The pinion prints axis vertical: tooth bending and
pocket bearing run along the layers.

Tooth stress, two methods:
  * "Lewis tip" (the designer's method): the whole normal load on one tooth at its tip, no fillet factor, the
    full 10 mm face. Reproduces the designer's SF 3.25.
  * "AGMA-type" (used for the verdict): the whole normal load on one tooth at the highest point of single-tooth
    contact (HPSTC, contact ratio 1.52), Dolan-Broghamer fillet factor Kf at the critical section, and the face
    width that can actually carry load: 10 - 0.25 (the rack's axial float in its guides) - 0.3 (the rack's bed
    chamfer at the same end as the pinion's 0.25 chamfer) = 9.45 mm.
"""
import ast
import math
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSY = ROOT / "jobs" / "20261025-robot-arm-assembly"
TOOLS = ROOT / "tools"
JAW = ROOT / "jobs" / "20261026-arm-claw-jaw"

# ---------------------------------------------------------------- parameters, read without importing build123d
SAFE = {"__builtins__": {}, "math": math, "min": min, "max": max, "abs": abs, "round": round}


def _ev(node, env, src):
    return eval(compile(ast.Expression(node), src, "eval"), SAFE, env)


def hobby_specs():
    """ServoSpec / BoxSpec constants and plain numbers of tools/hobby_parts.py."""
    env, box = {}, ["name", "length", "width", "height", "mass_g", "note"]
    for node in ast.parse((TOOLS / "hobby_parts.py").read_text()).body:
        if not (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)):
            continue
        name, v = node.targets[0].id, node.value
        try:
            fn = getattr(getattr(v, "func", None), "id", "")
            if fn in ("ServoSpec", "BoxSpec"):
                kw = {k.arg: _ev(k.value, env, "hobby_parts") for k in v.keywords}
                kw.update({f: _ev(a, env, "hobby_parts") for f, a in zip(box, v.args)})
                env[name] = SimpleNamespace(**kw)
            elif fn == "replace":
                d = dict(vars(env[v.args[0].id]))
                d.update({k.arg: _ev(k.value, env, "hobby_parts") for k in v.keywords})
                env[name] = SimpleNamespace(**d)
            else:
                env[name] = _ev(v, env, "hobby_parts")
        except Exception:
            pass
    return env


def consts(path, env):
    """Top-level NAME = expr and A, B = expr assignments of a .py file, evaluated in order (skips build123d ones)."""
    env = dict(env)
    for node in ast.parse(Path(path).read_text()).body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1):
            continue
        tgt = node.targets[0]
        try:
            val = _ev(node.value, env, str(path))
        except Exception:
            continue
        if isinstance(tgt, ast.Name):
            env[tgt.id] = val
        elif isinstance(tgt, ast.Tuple) and all(isinstance(e, ast.Name) for e in tgt.elts):
            env.update({e.id: v for e, v in zip(tgt.elts, val)})
    return env


HOBBY = hobby_specs()
HORN_DEPTH = HOBBY["HORN_DEPTH"]


def link_back_z(s, depth=HORN_DEPTH):          # = hobby_parts.link_back_z (horn face 0.6 above the spline top)
    return (s.total_h - s.tab_height) + 0.6 - depth


HOLE_COMP_DEFAULT = consts(TOOLS / "cadlib.py", {})["HOLE_COMP_DEFAULT"]
CF_ENV = consts(ASSY / "claw_frame.py", {**HOBBY, "link_back_z": link_back_z})
C = SimpleNamespace(**{k: v for k, v in CF_ENV.items() if k.isupper()})
P = SimpleNamespace(**{k: v for k, v in consts(HERE / "model.py", {**CF_ENV, "HOLE_COMP_DEFAULT": HOLE_COMP_DEFAULT,
                                                                  "HORN_DEPTH": HORN_DEPTH}).items() if k.isupper()})
J = SimpleNamespace(**{k: v for k, v in consts(JAW / "model.py", {**CF_ENV, "HOLE_COMP_DEFAULT": HOLE_COMP_DEFAULT}).items()
                       if k.isupper()})

# gear_outline / rack_outline from tools/gears.py (pure math; the module itself imports build123d)
_G = {"math": math}
for _n in ast.parse((TOOLS / "gears.py").read_text()).body:
    if isinstance(_n, ast.FunctionDef) and _n.name in ("_inv", "pitch_radius", "gear_outline", "rack_outline"):
        exec(compile(ast.Module(body=[_n], type_ignores=[]), "gears.py", "exec"), _G)
gear_outline, rack_outline = _G["gear_outline"], _G["rack_outline"]

# ---------------------------------------------------------------- allowables and required safety factors
ALLOW_XY = 25.0        # MPa, along the layers: strength-checks placeholder PETG (no library row) -> NEEDS_TEST at best
ALLOW_Z = 12.5         # across the layers: 0.5 x in-plane (placeholder)
SHEAR_XY = 12.5        # in-plane shear: 0.5 x normal (Tresca), as the arm and claw round-1 checks
BEARING = 25.0         # bearing / compression: the in-plane value
SF_SHORT, SF_CYCLIC = 3.0, 4.0
PRESSURE = math.radians(20.0)

# ---------------------------------------------------------------- loads
T_STALL = HOBBY["MG90S"].stall_torque_nmm      # 216 N.mm, MG90S at 6 V
F_CRASH = 13.0         # N at a fingertip in the arm plane (deep review 03 SYS-11: what the shoulder/elbow push)
F_YAW_Z = 1079.0 / (2 * 76.0)                  # 7.1 N: largest out-of-plane part of a yaw stall (F = 1079/R, R >= 76)
F_HAND = 5.0           # N hand push at a fingertip (spec)
PRELOAD_M2 = 100.0     # N, M2 x 12 clamp screw "snug" (assumption, as round 1 and the arm jobs)


def jaw_pry_ratio():
    """A sideways (claw z) push on jaw B's fingertip pitches the jaw about the front-bottom edge of its rack, which
    rests on the wrist plate (x X_P1, z T_W); the rear of the rack rises 0.40 mm onto the pinion before the neck
    (0.25 mm over slot B's strip, 5.25 mm in front of the pivot) can touch the strip: 0.040 rad against 0.048 rad.
    Pinion contact at the rack's rear end, past its 0.3 mm bed chamfer."""
    x_c = C.X_P0 + J.BED_CHAMFER
    return (C.X_TIP - C.X_P1) / (C.X_P1 - x_c)


ROWS, INFO = [], []


def row(case, section, d, stress, allow, sf_req, rows=ROWS):
    sf = allow / stress if stress > 1e-12 else float("inf")
    rows.append((case, section, d, stress, allow, sf, sf_req))
    return sf


# ---------------------------------------------------------------- tooth geometry and stress
def pinion_half(m, z, backlash, fillet, tip_relief):
    """+y half of tooth 0 (centred on +x): from the tip corner down the flank, round the root fillet, along the root
    to the gap centre. Points from gears.gear_outline at fine resolution."""
    pts = gear_outline(m, z, 20.0, backlash, 0.0, root_fillet=fillet, tip_relief=tip_relief, flank_pts=80,
                       fillet_pts=40, root_pts=8, tip_pts=6)
    pitch = 2 * math.pi / z
    ra = m * z / 2 + m - tip_relief
    i = max((k for k, (x, y) in enumerate(pts) if abs(math.hypot(x, y) - ra) < 1e-6 and y > 0
             and abs(math.atan2(y, x)) < pitch / 2), key=lambda k: math.atan2(pts[k][1], pts[k][0]))
    seq = []
    while math.atan2(pts[i % len(pts)][1], pts[i % len(pts)][0]) <= pitch / 2 + 1e-9:
        seq.append(pts[i % len(pts)])
        i += 1
    return seq


def _cross(seq, xs):
    out = None
    for (x0, y0), (x1, y1) in zip(seq, seq[1:]):
        if (x0 - xs) * (x1 - xs) <= 0 and x0 != x1:
            y = y0 + (y1 - y0) * (xs - x0) / (x1 - x0)
            out = y if out is None else min(out, y)
    return out


def _flank_point(seq, r):
    for (x0, y0), (x1, y1) in zip(seq, seq[1:]):
        r0, r1 = math.hypot(x0, y0), math.hypot(x1, y1)
        if (r0 - r) * (r1 - r) <= 0 and r0 != r1:
            t = (r - r0) / (r1 - r0)
            return x0 + t * (x1 - x0), y0 + t * (y1 - y0)
    raise ValueError(f"no flank point at r {r}")


def contact_geometry(m, z, tip_relief):
    rp, rb = m * z / 2, m * z / 2 * math.cos(PRESSURE)
    ra = rp + m - tip_relief
    path_p = math.sqrt(ra ** 2 - rb ** 2) - rp * math.sin(PRESSURE)      # pitch point -> pinion tip
    path_r = (m - tip_relief) / math.sin(PRESSURE)                        # rack tip -> pitch point
    pb = math.pi * m * math.cos(PRESSURE)
    L = path_p + path_r
    d = path_p - (L - pb)                                                 # HPSTC beyond the pitch point
    return dict(rp=rp, rb=rb, ra=ra, cr=L / pb, r_hpstc=math.sqrt(rb ** 2 + (rp * math.sin(PRESSURE) + d) ** 2))


def pinion_tooth(Wn, b, m=None, z=None, backlash=None, fillet=None, tip_relief=None, at="hpstc", kf=True):
    """Root bending stress of one pinion tooth carrying the normal load Wn (N) on face width b (mm).
    Returns (sigma MPa, section chord t, Kf, load radius)."""
    m = C.M if m is None else m
    z = C.Z_TEETH if z is None else z
    backlash = C.PINION_BACKLASH if backlash is None else backlash
    fillet = C.PINION_ROOT_FILLET * m / C.M if fillet is None else fillet
    tip_relief = C.TIP_RELIEF * m / C.M if tip_relief is None else tip_relief
    g = contact_geometry(m, z, tip_relief)
    seq = pinion_half(m, z, backlash, fillet, tip_relief)
    r_load = g["ra"] - 1e-6 if at == "tip" else g["r_hpstc"]
    xp, yp = _flank_point(seq, r_load)
    th_t = math.atan2(yp, xp) - math.acos(g["rb"] / r_load)       # tangent point of the line of action on the base circle
    Fx, Fy = Wn * math.sin(th_t), -Wn * math.cos(th_t)               # into the +y flank, along the line of action
    xc = xp - yp * Fx / Fy                                           # load line crosses the tooth centre line
    rf = g["rp"] - 1.25 * m
    r_fillet_top = math.sqrt((rf + fillet) ** 2 - fillet ** 2)      # where the fillet meets the radial flank
    xs0 = min(x for x, _ in seq)
    best = (0.0, 0.0, 1.0)
    for k in range(2500):
        xs = xs0 + (xp - xs0) * k / 2500
        h = _cross(seq, xs)
        if not h or h <= 0:
            continue
        t = 2 * h
        M = (xp - xs) * Fy - yp * Fx                                 # moment about the section centre (0 radial)
        s = 6 * abs(M) / (b * t * t)                                 # direct radial compression ignored (conservative)
        K = 1.0
        if kf and xs <= r_fillet_top:                                # Dolan-Broghamer (20 deg: H 0.18, L 0.15, M 0.45)
            K = 0.18 + (t / fillet) ** 0.15 * (t / max(xc - xs, 1e-3)) ** 0.45
        if s * K > best[0]:
            best = (s * K, t, K)
    return best[0], best[1], best[2], r_load


def rack_tooth(Wn, b, m=None, backlash=None, fillet=None, tip_relief=None, rp=None, at="hpstc", kf=True):
    """Root bending of one rack tooth (jaw) carrying Wn along the line of action, at its highest point of
    single-tooth contact (contact starts at the rack's tip, so the HPSTC is (L - pb) sin 20 deg below the tip) or at
    its tip; Dolan-Broghamer Kf in the root-fillet zone only. Returns (sigma, width at the critical section, Kf)."""
    m = C.M if m is None else m
    rp = C.R_P if rp is None else rp
    backlash = C.RACK_BACKLASH if backlash is None else backlash
    fillet = C.RACK_ROOT_FILLET * m / C.M if fillet is None else fillet
    tip_relief = C.TIP_RELIEF * m / C.M if tip_relief is None else tip_relief
    pts = rack_outline(m, -6 * m, 6 * m, 10.0, 20.0, backlash, phase=0.0, root_fillet=fillet, tip_relief=tip_relief,
                       fillet_pts=40)
    right = sorted([(x, y) for (x, y) in reversed(pts[2:]) if 0 <= x <= math.pi * m / 2 + 1e-9], key=lambda p: p[0])

    def half_w(y):
        out = None
        for (x0, y0), (x1, y1) in zip(right, right[1:]):
            if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
                x = x0 + (x1 - x0) * (y - y0) / (y1 - y0)
                out = x if out is None else min(out, x)
        return out
    g = contact_geometry(m, int(round(2 * rp / m)), tip_relief)
    pb = math.pi * m * math.cos(PRESSURE)
    L = g["cr"] * pb
    yt = m - tip_relief
    yl = yt if at == "tip" else yt - (L - pb) * math.sin(PRESSURE)    # load height above the pitch line
    xl = half_w(yl)
    Fx, Fy = -Wn * math.cos(PRESSURE), -Wn * math.sin(PRESSURE)
    yc = yl - xl * math.tan(PRESSURE)                                 # load line crosses the tooth centre line
    y_fil = -1.25 * m + fillet * 1.2                                  # top of the root-fillet zone
    best = (0.0, 0.0, 1.0)
    for k in range(2000):
        ys = -1.25 * m + (yl + 1.25 * m) * k / 2000
        h = half_w(ys)
        if not h:
            continue
        t = 2 * h
        M = (yl - ys) * Fx - xl * Fy
        s = 6 * abs(M) / (b * t * t)
        K = 1.0
        if kf and ys <= y_fil:
            K = 0.18 + (t / fillet) ** 0.15 * (t / max(yc - ys, 1e-3)) ** 0.45
        if s * K > best[0]:
            best = (s * K, t, K)
    return best


# ---------------------------------------------------------------- checks
rb = C.R_P * math.cos(PRESSURE)
W_ONE = T_STALL / rb                    # normal force with one jaw blocked (21.6 N tangential at the pitch circle)
W_BOTH = W_ONE / 2
W_CRASH = F_CRASH / math.cos(PRESSURE)   # 13 N along y on one finger, held by the claw servo (130 < 216 N.mm)
B_EFF = C.FACE_W - C.CLR - max(P.BED_CHAMFER, J.BED_CHAMFER)
geo = contact_geometry(C.M, C.Z_TEETH, C.TIP_RELIEF)

print(f"pinion m {C.M} z {C.Z_TEETH} face {C.FACE_W}, backlash pinion {C.PINION_BACKLASH} / rack {C.RACK_BACKLASH}, "
      f"root fillet {C.PINION_ROOT_FILLET}, tip relief {C.TIP_RELIEF}; r_p {C.R_P}, r_b {rb:.3f}, contact ratio "
      f"{geo['cr']:.2f}, HPSTC r {geo['r_hpstc']:.3f} (tip {geo['ra']:.3f})")
print(f"stall {T_STALL:.0f} N.mm -> {T_STALL / C.R_P:.1f} N tangential on one rack ({T_STALL / C.R_P / 2:.1f} per jaw with "
      f"both jaws), normal {W_ONE:.2f} N; effective face width {B_EFF:.2f} mm")

s_lw, t_lw, _, _ = pinion_tooth(W_ONE, C.FACE_W, at="tip", kf=False)
row("designer's method (info): one jaw blocked, Lewis tip load, no Kf, full face 10", f"tooth root chord {t_lw:.2f}",
    "XY", s_lw, ALLOW_XY, SF_SHORT, INFO)
s, t, K, r = pinion_tooth(W_ONE, C.FACE_W)
row("info: one jaw blocked, HPSTC + Kf, full face 10", f"fillet chord {t:.2f}, Kf {K:.2f}", "XY", s, ALLOW_XY, SF_SHORT,
    INFO)
s, t, K, r = pinion_tooth(W_ONE, B_EFF)
row(f"stall, one jaw blocked (or opening against an obstacle): {T_STALL / C.R_P:.1f} N on one mesh", f"tooth fillet: "
    f"HPSTC r {r:.2f}, chord {t:.2f}, Kf {K:.2f}, face {B_EFF:.2f}", "XY", s, ALLOW_XY, SF_SHORT)
s, t, K, r = pinion_tooth(W_BOTH, B_EFF)
row(f"stall, both jaws (every full-close grip, cyclic): {T_STALL / C.R_P / 2:.1f} N per mesh", "tooth fillet (as above)",
    "XY", s, ALLOW_XY, SF_CYCLIC)
s, t, K, r = pinion_tooth(W_CRASH, B_EFF)
row(f"crash: {F_CRASH:.0f} N along the jaw travel at one fingertip, held by the claw servo", "tooth fillet (as above)", "XY",
    s, ALLOW_XY, SF_SHORT)

# horn stubs: MG90S double-arm horn cut to HORN_TRIM_R; each arm side is ~flat from where it leaves the hub circle
H = C.PINION_HORN
r_hub = H.horn_d / 2


def arm_half_width(x):
    return r_hub + (H.horn_tip_d / 2 - r_hub) * x / H.horn_arm_len


x0 = next(x / 1000 for x in range(0, 5500) if math.hypot(x / 1000, arm_half_width(x / 1000)) > r_hub + 1e-3)
x1 = C.HORN_TRIM_R
lever = (x1 ** 2 - x0 ** 2) / (2 * (x1 - x0))       # uniform bearing on the flat: resultant arm
F_stub = T_STALL / (2 * lever)                      # two stubs, one flat each
p_stub = F_stub / ((x1 - x0) * H.horn_t)
row(f"horn stubs, stall torque {T_STALL:.0f} N.mm at every full-close grip (cyclic)", f"stub flat x {x0:.2f}..{x1:.2f} "
    f"x horn {H.horn_t} (mean bearing)", "XY", p_stub, BEARING, SF_CYCLIC)
r_pocket = C.HORN_TRIM_R + (P.POCKET_CLR + P.HOLE_COMP) / 2
r_root = C.R_P - 1.25 * C.M
wall = math.sqrt(r_root ** 2 - ((x0 + x1) / 2) ** 2) - (arm_half_width((x0 + x1) / 2) + (P.POCKET_CLR + P.HOLE_COMP) / 2)
tau_wall = F_stub / (2 * wall * HORN_DEPTH)
row("pocket wall ahead of a stub flat (cyclic): shear-out on 2 planes, wall to the root circle x pocket depth",
    f"wall {wall:.2f} x {HORN_DEPTH} (backed by the solid face behind)", "XY shear", tau_wall, SHEAR_XY, SF_CYCLIC)
backup = (r_root - r_pocket) / (2.25 * C.M)
INFO.append(("info: rim under the 2 mm pocket, backup ratio (r_root - r_pocket) / tooth height", f"{backup:.2f} >= 1.2: "
             "no rim factor", "-", 0, 0, float("inf"), 0))

# clamp screw head on the counterbore floor
cb_d = P.CB_D                                       # printed counterbore = washer seat; washer OD 6
hole_printed = H.horn_screw_clear_d                 # M2 clearance 2.4 printed (2.6 CAD)
A_washer = math.pi / 4 * (6.0 ** 2 - hole_printed ** 2)
row(f"assembly: M2 x 12 snug, {PRELOAD_M2:.0f} N, on the Ø6 washer (sustained)", f"washer annulus {A_washer:.1f} mm2 on "
    f"the {C.PINION_FLOOR} floor", "XY", PRELOAD_M2 / A_washer, BEARING, SF_CYCLIC)
p_max = A_washer * BEARING / SF_CYCLIC

# rack pry (jaw B pushed sideways): rack tooth tips bottom on the pinion's root lands before the flanks wedge
ratio = jaw_pry_ratio()
tip_clear = (C.R_P - 1.25 * C.M) - (C.R_P - C.M + C.TIP_RELIEF)
tip_clear = -tip_clear                                  # rack tip (9.15) to pinion root (8.75): 0.40
wedge = C.BACKLASH / (2 * math.tan(PRESSURE))
hw = (math.pi * C.M / 2 - C.RACK_BACKLASH / 2) / 2
tip_land = 2 * (hw - (C.M - C.TIP_RELIEF) * math.tan(PRESSURE))
L_contact = C.FACE_W / 3                                 # contact length along the face at the rack's rear end (assumed)
for name, F in (("yaw stall", F_YAW_Z), ("hand push", F_HAND)):
    Fp = ratio * F
    row(f"advisory: {name} {F:.1f} N sideways on jaw B's fingertip pries its rack onto the pinion: {Fp:.0f} N (lever "
        f"x{ratio:.2f}); compressive contact, a dent at worst", f"1 rack tip land {tip_land:.2f} x {L_contact:.1f} on the "
        f"root land (1-2 teeth, contact length assumed)", "XY", Fp / (tip_land * L_contact), BEARING, SF_SHORT, INFO)

# advisory: the flanks wedge instead (backlash closes first: print tolerance on the teeth +-0.05 each)
for name, F in (("yaw stall", F_YAW_Z), ("hand push", F_HAND)):
    Fp = ratio * F
    N = Fp / (2 * math.sin(PRESSURE))                   # normal force on each flank of the wedged rack tooth
    s, t, K, r = pinion_tooth(N, L_contact)
    row(f"advisory: {name}, if the flanks wedge instead (tip clearance {tip_clear:.2f} vs wedge at {wedge:.2f} radial; "
        f"tolerance can swap them): {N:.0f} N on one pinion flank", f"tooth fillet, contact length {L_contact:.1f}", "XY",
        s, ALLOW_XY, SF_SHORT, INFO)
# the mating rack teeth (jaw job), same method, for reference
s, t, K = rack_tooth(W_ONE, B_EFF)
row("info (jaw job): rack tooth, one jaw blocked, HPSTC + Kf, face 9.45", f"root width {t:.2f}, Kf {K:.2f}", "XY", s,
    ALLOW_XY, SF_SHORT, INFO)
s, t, K = rack_tooth(W_ONE, C.FACE_W, at="tip", kf=False)
row("info (jaw job): rack tooth, one jaw blocked, Lewis tip, no Kf, face 10 (the designer's method)", f"width {t:.2f}",
    "XY", s, ALLOW_XY, SF_SHORT, INFO)
# advisory: jaws forced by hand with the servo powered: it back-drives at an unmeasured 2-4 x stall
for k in (2.0, 4.0):
    s, *_ = pinion_tooth(k * W_ONE, B_EFF)
    row(f"advisory: jaws forced by hand, servo powered, back-drives at {k:.0f} x stall: {k * T_STALL / C.R_P:.0f} N on one "
        f"mesh", "tooth fillet", "XY", s, ALLOW_XY, SF_SHORT, INFO)


# ---------------------------------------------------------------- report
def table(rows, start=1):
    for i, (case, sec, d, s, a, sf, req) in enumerate(rows, start):
        ok = "" if not req else ("OK" if sf >= req else "**FAIL**")
        sf_s = "-" if sf == float("inf") else f"{sf:.2f}"
        print(f"| {i} | {case} | {sec} | {d} | {s:.2f} | {a:.2f} | {sf_s} | {req or '-'} | {ok} |")


print("\n| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |")
print("|---|---|---|---|---|---|---|---|---|")
table(ROWS)
print("\nInformation and advisory rows (not in the verdict):")
table(INFO, start=len(ROWS) + 1)
worst = min(ROWS, key=lambda r: r[5] / r[6])
print(f"\nlowest SF {worst[5]:.2f} (required {worst[6]:.0f}): {worst[0]} / {worst[1]}")
print(f"M2 clamp: preload for SF 4 on the washer <= {p_max:.0f} N (about {p_max * 0.2 * 2 / 1000:.3f} N.m with K 0.2)")
fails = [r for r in ROWS if r[5] < r[6]]
print("VERDICT (calculation):", "FAIL" if fails else "NEEDS_TEST (placeholder allowables)")

# ---------------------------------------------------------------- what-if lines for the required change
print("\nWhat-if (one jaw blocked, AGMA-type, effective face = FACE_W - 0.55; the rack teeth with the same split):")
cands = [("as drawn: backlash 0.20 / 0.50, face 10", dict(), dict()),
         ("backlash split 0.10 / 0.60 (total 0.35)", dict(backlash=0.10), dict(backlash=0.60)),
         ("backlash split 0.00 / 0.70 (total 0.35)", dict(backlash=0.0), dict(backlash=0.70)),
         ("face 12, backlash 0.20 / 0.50", dict(face=12.0), dict(face=12.0)),
         ("face 12, backlash 0.00 / 0.70", dict(face=12.0, backlash=0.0), dict(face=12.0, backlash=0.70)),
         ("z 22 (r_p 11), backlash 0.20 / 0.50", dict(z=22), dict(rp=11.0)),
         ("z 24 (r_p 12), backlash 0.20 / 0.50", dict(z=24), dict(rp=12.0)),
         ("face 12, backlash 0.10 / 0.70 (total 0.40)", dict(face=12.0, backlash=0.10), dict(face=12.0, backlash=0.70)),
         ("face 12, backlash 0.10 / 0.80 (total 0.45)", dict(face=12.0, backlash=0.10), dict(face=12.0, backlash=0.80)),
         ("face 12, backlash 0.20 / 0.70 (total 0.45)", dict(face=12.0, backlash=0.20), dict(face=12.0, backlash=0.70)),
         ("z 24, backlash 0.10 / 0.70 (total 0.40)", dict(z=24, backlash=0.10), dict(rp=12.0, backlash=0.70)),
         ("z 24, backlash 0.10 / 0.80 (total 0.45)", dict(z=24, backlash=0.10), dict(rp=12.0, backlash=0.80))]
for name, pk, rk in cands:
    face = pk.pop("face", C.FACE_W)
    z = pk.get("z", C.Z_TEETH)
    rp = C.M * z / 2
    Wn = T_STALL / (rp * math.cos(PRESSURE))
    b = face - C.CLR - max(P.BED_CHAMFER, J.BED_CHAMFER)
    s_p, *_ = pinion_tooth(Wn, b, **pk)
    rk.pop("face", None)
    s_r, *_ = rack_tooth(Wn, b, backlash=rk.get("backlash"), rp=rk.get("rp"))
    bl = pk.get("backlash", C.PINION_BACKLASH) + rk.get("backlash", C.RACK_BACKLASH)
    margin = bl / 2 / (2 * math.tan(PRESSURE)) - tip_clear
    print(f"  {name:42s}: pinion SF {ALLOW_XY / s_p:.2f} (cyclic both jaws {2 * ALLOW_XY / s_p:.2f}), "
          f"rack SF {ALLOW_XY / s_r:.2f}; rack force {T_STALL / rp:.1f} N; pry: tips bottom {margin:+.2f} mm before "
          f"the flanks close")
print("\nPry margin (rack tips bottom on the pinion's root lands before the flanks can wedge), total backlash j:")
for j in (0.35, 0.40, 0.45, 0.50, 0.60):
    print(f"  j {j:.2f}: flanks close after {j / (2 * math.tan(PRESSURE)):.2f} mm radial, tips bottom after "
          f"{tip_clear:.2f}: margin {j / (2 * math.tan(PRESSURE)) - tip_clear:+.2f} mm")

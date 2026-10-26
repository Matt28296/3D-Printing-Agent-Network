"""Strength check, round 3: jobs/20261026-arm-claw-jaw (rack + neck + finger, x2; face 12, grooves to x 70.6, bed chamfer 0.25).

Run from the project root:  python3 jobs/20261026-arm-claw-jaw/strength_calc.py      (add --cad to cross-check the
hand sections against the build123d solid; that needs the CAD venv)
Plain python3: parameters come from claw_frame.py, this job's model.py and tools/hobby_parts.py through the ast module;
the rack tooth outline from tools/gears.py's rack_outline (pure math, executed on its own).

The jaw prints standing on the rack's back end (claw x = print Z), so every normal stress along x in the neck and
the finger, and every shear on a plane x = const, acts ACROSS the layers: 12.5 MPa normal, 6.25 MPa shear. The rack
teeth are drawn in the bed plane: 25 MPa. Placeholder PETG allowables (no library row): NEEDS_TEST at best.

Method: the jaw is drawn as jaw A, closed, in claw frame G. At each section x (0.1 mm steps from the rack face to the
tip) the cross-section is the plan outline's y-range times the side outline's z-range (minus the grip face's V-notch
and, at the groove centres, the 0.6 mm V-groove depth): a polygon whose A, centroid and I_yy, I_zz, I_yz are exact.
Normal stress at every vertex from N, M_y, M_z (unsymmetric bending), with the stress concentration of the face the
vertex sits on; shear = torsion (Roark rectangle) + 1.5 V/A, added; across-layer interaction
(sigma/12.5)^2 + (tau/6.25)^2 = 1/SF^2 (as round 1).
"""
import ast
import math
import sys
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSY = ROOT / "jobs" / "20261025-robot-arm-assembly"
TOOLS = ROOT / "tools"

# ---------------------------------------------------------------- parameters, read without importing build123d
SAFE = {"__builtins__": {}, "math": math, "min": min, "max": max, "abs": abs, "round": round}


def _ev(node, env, src):
    return eval(compile(ast.Expression(node), src, "eval"), SAFE, env)


def hobby_specs():
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


def link_back_z(s, depth=HOBBY["HORN_DEPTH"]):
    return (s.total_h - s.tab_height) + 0.6 - depth


HOLE_COMP_DEFAULT = consts(TOOLS / "cadlib.py", {})["HOLE_COMP_DEFAULT"]
CF_ENV = consts(ASSY / "claw_frame.py", {**HOBBY, "link_back_z": link_back_z})
C = SimpleNamespace(**{k: v for k, v in CF_ENV.items() if k.isupper()})
P = SimpleNamespace(**{k: v for k, v in consts(HERE / "model.py", {**CF_ENV, "HOLE_COMP_DEFAULT": HOLE_COMP_DEFAULT}).items()
                       if k.isupper()})
_G = {"math": math}
for _n in ast.parse((TOOLS / "gears.py").read_text()).body:
    if isinstance(_n, ast.FunctionDef) and _n.name in ("_inv", "rack_outline"):
        exec(compile(ast.Module(body=[_n], type_ignores=[]), "gears.py", "exec"), _G)
rack_outline = _G["rack_outline"]

# ---------------------------------------------------------------- allowables and required safety factors
ALLOW_XY, ALLOW_Z = 25.0, 12.5        # placeholder PETG, along / across the layers
SHEAR_Z = 6.25                        # interlayer shear: 0.5 x the across-layer value (Tresca)
BEARING = 25.0
SF_SHORT, SF_CYCLIC = 3.0, 4.0
PRESSURE = math.radians(20.0)

# ---------------------------------------------------------------- loads
T_STALL = HOBBY["MG90S"].stall_torque_nmm
F1 = T_STALL / C.R_P                  # 21.6 N: one jaw blocked (or the claw opening against an obstacle)
F2 = F1 / 2                           # 10.8 N per jaw, both jaws on a free object
F_CRASH = 13.0                        # N, fingertip on the desk, in the arm plane, any direction (SYS-11)
F_YAW_Z = 1079.0 / (2 * 76.0)         # 7.1 N, largest out-of-plane part of a yaw stall at the fingertip
F_HAND = 5.0
X_MESH = (C.X_P0 + C.X_P1) / 2        # pinion force on the rack: mid-face

# ---------------------------------------------------------------- jaw outlines (jaw A, closed, frame G)
ZN0, ZN1 = C.ZS + C.NECK_Z[0], C.ZS + C.NECK_Z[1]
ZLO, ZHI = C.ZS - C.GRIP_HALF, C.ZS + C.GRIP_HALF


def y_out(x):
    """Outer face (negative y) from the plan outline: neck, 45-degree gusset, 12 mm root, taper, 6 mm tip, tip bevel."""
    if x <= C.NECK_X1:
        y = -C.NECK_Y
    elif x <= C.NECK_X1 + P.GUSSET:
        y = -C.NECK_Y + (x - C.NECK_X1)
    elif x <= C.TAPER_X0:
        y = -C.BLADE_T_ROOT
    elif x <= C.TAPER_X1:
        y = -C.BLADE_T_ROOT + (C.BLADE_T_ROOT - C.BLADE_T) * (x - C.TAPER_X0) / (C.TAPER_X1 - C.TAPER_X0)
    else:
        y = -C.BLADE_T
    # tip bevel: model.py cuts the triangle (X_TIP - 2 TIP_BEVEL - 2, -BLADE_T - 1), (X_TIP + 1, -BLADE_T - 1),
    # (X_TIP + 1, -BLADE_T + TIP_BEVEL + 0.5) off the outer face
    xa, ya = C.X_TIP - 2 * P.TIP_BEVEL - 2, -C.BLADE_T - 1
    xb, yb = C.X_TIP + 1, -C.BLADE_T + P.TIP_BEVEL + 0.5
    return max(y, ya + (yb - ya) * (x - xa) / (xb - xa)) if x > xa else y


def z_range(x):
    if x <= C.NECK_X1:
        lo = ZN0
    elif x <= C.NECK_X1 + (ZN0 - ZLO):
        lo = ZN0 - (x - C.NECK_X1)
    elif x <= C.X_TIP - P.TIP_CHAMFER:
        lo = ZLO
    else:
        lo = ZLO + (x - (C.X_TIP - P.TIP_CHAMFER))
    if x <= C.TOP_KINK_X:
        hi = ZN1
    elif x <= C.TOP_KINK_X + (ZN1 - ZHI):
        hi = ZN1 - (x - C.TOP_KINK_X)
    elif x <= C.X_TIP - P.TIP_CHAMFER:
        hi = ZHI
    else:
        hi = ZHI - (x - (C.X_TIP - P.TIP_CHAMFER))
    return lo, hi


GROOVES = []
_x = P.GROOVE_X[0]
while _x <= P.GROOVE_X[1] + 1e-9:
    GROOVES.append(_x)
    _x += P.GROOVE_PITCH
NOTCH_X0 = C.GRIP_X0 - 4


def groove_depth(x):
    return max([P.GROOVE_D - abs(x - g) for g in GROOVES if abs(x - g) < P.GROOVE_D] + [0.0])


def section(x):
    """Cross-section polygon (y, z) at x, counter-clockwise, with the face tag of every vertex."""
    y0, y1 = y_out(x), -groove_depth(x)
    z0, z1 = z_range(x)
    pts = [((y0, z0), ("out", "bot")), ((y1, z0), ("grip", "bot"))]
    w = P.NOTCH_D + y1                                   # 45-degree V-notch: half-width at the face y1
    if x >= NOTCH_X0 and w > 0 and z0 < C.ZS - w and z1 > C.ZS + w:
        pts += [((y1, C.ZS - w), ("grip", None)), ((-P.NOTCH_D, C.ZS), ("notch", None)), ((y1, C.ZS + w), ("grip", None))]
    pts += [((y1, z1), ("grip", "top")), ((y0, z1), ("out", "top"))]
    return pts


def props(pts):
    """Area, centroid and second moments (about the centroid) of a simple polygon in (y, z)."""
    A = Sy = Sz = Iyy = Izz = Iyz = 0.0          # Iyy = int z^2, Izz = int y^2 (about the origin first)
    n = len(pts)
    for i in range(n):
        (y0, z0), (y1, z1) = pts[i][0], pts[(i + 1) % n][0]
        c = y0 * z1 - y1 * z0
        A += c / 2
        Sy += (y0 + y1) * c / 6
        Sz += (z0 + z1) * c / 6
        Izz += (y0 * y0 + y0 * y1 + y1 * y1) * c / 12
        Iyy += (z0 * z0 + z0 * z1 + z1 * z1) * c / 12
        Iyz += (y0 * z1 + 2 * y0 * z0 + 2 * y1 * z1 + y1 * z0) * c / 24
    yc, zc = Sy / A, Sz / A
    return dict(A=A, yc=yc, zc=zc, Iyy=Iyy - A * zc * zc, Izz=Izz - A * yc * yc, Iyz=Iyz - A * yc * zc)


def kt_faces(x):
    """Stress concentration per face at section x (assumptions in strength.md):
    neck root at the rack face: r 4 fillets on the y faces (r/h 0.2: 1.7), the rack's teeth make a sharp 2.1 mm step
    under the neck's bottom face (2.5), its top face is flush with the rack's back (1.0);
    r 3 kinks: side (38.35, bottom, h 10: 1.5), top (64.6, top, h 20: 1.7), plan gusset end (46.35, outer, h 12: 1.5),
    taper end (73.35, outer, h 6: 1.5); 0.6 mm 90-degree V-grooves on the grip face, sharp root (printed r ~0.2):
    KT_GROOVE 2.5 (the skill's sharp-corner value; Peterson's V/U-notch charts give 2.5-2.8 at r/d 0.04)."""
    k = {"grip": 1.0, "out": 1.0, "bot": 1.0, "top": 1.0, "notch": 1.0}
    if x - C.X_P1 <= 0.5:
        k.update(grip=1.7, out=1.7, bot=2.5)
    if abs(x - C.NECK_X1) <= 2.0:
        k["bot"] = max(k["bot"], 1.5)
    if abs(x - (C.TOP_KINK_X + ZN1 - ZHI)) <= 2.0:
        k["top"] = max(k["top"], 1.7)
    if abs(x - (C.NECK_X1 + P.GUSSET)) <= 2.0 or abs(x - C.TAPER_X1) <= 2.0:
        k["out"] = max(k["out"], 1.5)
    if groove_depth(x) > 0.3:
        k["grip"] = max(k["grip"], KT_GROOVE)
    return k


KT_GROOVE = 2.5


def roark_tau(T, a, b):
    """Max torsional shear of a solid rectangle a x b (full side lengths)."""
    A_, B_ = max(a, b), min(a, b)
    r = B_ / A_
    return 3 * abs(T) / (A_ * B_ ** 2) * (1 + 0.6095 * r + 0.8865 * r ** 2 - 1.8023 * r ** 3 + 0.91 * r ** 4)


def section_sf(x, Q, F, use_kt=True):
    """SF of the section at x for force F (N) at point Q (claw G), across the layers. Returns (SF, sigma, tau)."""
    pts = section(x)
    p = props(pts)
    yc, zc = p["yc"], p["zc"]
    dx, dy, dz = Q[0] - x, Q[1] - yc, Q[2] - zc
    Mx = dy * F[2] - dz * F[1]
    My = dz * F[0] - dx * F[2]
    Mz = dx * F[1] - dy * F[0]
    N = F[0]
    D = p["Iyy"] * p["Izz"] - p["Iyz"] ** 2
    a = (My * p["Izz"] + Mz * p["Iyz"]) / D
    b = -(Mz * p["Iyy"] + My * p["Iyz"]) / D
    k = kt_faces(x) if use_kt else {}
    smax = -1e9
    for (y, z), (fy, fz) in pts:
        sz = a * (z - zc) * k.get(fz, 1.0)
        sy = b * (y - yc) * k.get(fy, 1.0)
        smax = max(smax, N / p["A"] + sz + sy)
    zlo, zhi = z_range(x)
    width = p["A"] / (zhi - zlo)                    # equivalent rectangle for torsion (notch spread over the height)
    tau = roark_tau(Mx, width, zhi - zlo) + 1.5 * math.hypot(F[1], F[2]) / p["A"]
    u = math.hypot(max(smax, 0.0) / ALLOW_Z, tau / SHEAR_Z)
    return (1 / u if u > 0 else float("inf")), smax, tau


def scan(Q, F, x0=C.X_P1, x1=None, step=0.1):
    x1 = Q[0] - 3.0 if x1 is None else x1
    best = (float("inf"), None, 0, 0)
    x = x0
    while x <= x1 + 1e-9:
        sf, s, t = section_sf(x, Q, F)
        if sf < best[0]:
            best = (sf, x, s, t)
        x += step
    return best


ROWS, INFO = [], []


def add(case, sf, sec, s_eq, allow, req, d="Z comb", rows=ROWS):
    rows.append((case, sec, d, s_eq, allow, sf, req))


def worst_over(cases):
    """cases: [(label, Q, F)] -> the worst (SF, label, x, sigma, tau)."""
    out = (float("inf"),)
    for lab, Q, F in cases:
        sf, x, s, t = scan(Q, F)
        if sf < out[0]:
            out = (sf, lab, x, s, t)
    return out


# ---------------------------------------------------------------- finger and neck cases
X_GRIP = C.X_TIP - 3.0     # spec: the grip force 3 mm from the tip (anywhere over the grip face's height there)


def grip_points(face, x_tip=X_GRIP):
    """Contact points on the grip face (face 'grip', y 0) or the outer face ('out'), over its full height."""
    pts = []
    for x in (50.0, 60.0, 70.0, x_tip):
        lo, hi = z_range(x)
        y = 0.0 if face == "grip" else y_out(x)
        for z in (lo + 0.5, C.ZS, hi - 0.5):
            pts.append((f"x {x:.2f} z {z - C.ZS:+.1f}", (x, y, z)))
    return pts


def report_case(name, cases, req):
    sf, lab, x, s, t = worst_over(cases)
    add(f"{name} [{lab}]", sf, f"x {x:.1f}: sigma {s:.2f}, tau {t:.2f}", ALLOW_Z / sf, ALLOW_Z, req)
    return sf


report_case(f"grip at stall, one jaw blocked, {F1:.1f} N on the grip face",
            [(lab, Q, (0, -F1, 0)) for lab, Q in grip_points("grip")], SF_SHORT)
report_case(f"grip at stall, both jaws, {F2:.1f} N each (every full-close grip, cyclic)",
            [(lab, Q, (0, -F2, 0)) for lab, Q in grip_points("grip")], SF_CYCLIC)
report_case(f"added: claw opening against an obstacle, {F1:.1f} N on the outer face",
            [(lab, Q, (0, F1, 0)) for lab, Q in grip_points("out")], SF_SHORT)
tip_pts = [(f"tip z {dz:+.0f}", (C.X_TIP, -P.TIP_BEVEL / 2 + 0.5, C.ZS + dz)) for dz in (-6.0, 0.0, 6.0)]
crash = [(f"{lab}, {ang} deg", Q, (F_CRASH * math.cos(math.radians(ang)), F_CRASH * math.sin(math.radians(ang)), 0.0))
         for lab, Q in tip_pts for ang in range(0, 360, 15)]
report_case(f"crash: {F_CRASH:.0f} N at the fingertip in the arm plane, any direction (wrist back-driven)", crash,
            SF_SHORT)
report_case(f"yaw stall: {F_YAW_Z:.1f} N out of the arm plane at the fingertip, either way",
            [(f"{lab}, along {'+' if sgn > 0 else '-'}z", Q, (0, 0, sgn * F_YAW_Z)) for lab, Q in tip_pts
             for sgn in (1, -1)], SF_SHORT)
report_case(f"handling: {F_HAND:.0f} N at the fingertip, any direction",
            [(f"{lab}, {ang} deg in plan, {el} deg elevation", Q,
              (F_HAND * math.cos(math.radians(ang)) * math.cos(math.radians(el)),
                                   F_HAND * math.sin(math.radians(ang)) * math.cos(math.radians(el)),
                                   F_HAND * math.sin(math.radians(el))))
             for lab, Q in tip_pts for ang in range(0, 360, 30) for el in (-90, -45, 0, 45, 90)], SF_SHORT)


# ---------------------------------------------------------------- round 3: the neck root and the last groove, named
def worst_in(cases, x0, x1):
    out = (float("inf"),)
    for lab, Q, F in cases:
        x1q = min(x1, Q[0] - 3.0)                      # only sections between the root and the load carry it
        if x1q < x0:
            continue
        sf, x, s, t = scan(Q, F, x0=x0, x1=x1q)
        if sf < out[0]:
            out = (sf, lab, x, s, t)
    return out


GRIP1 = [(lab, Q, (0, -F1, 0)) for lab, Q in grip_points("grip")]
OPEN1 = [(lab, Q, (0, F1, 0)) for lab, Q in grip_points("out")]
YAW = [(f"{lab}, along {'+' if sgn > 0 else '-'}z", Q, (0, 0, sgn * F_YAW_Z)) for lab, Q in tip_pts for sgn in (1, -1)]
for name, cases in ((f"neck root (x {C.X_P1}..{C.X_P1 + 0.5}, r 4 fillets, toothed bottom edge): one jaw blocked, "
                     f"{F1:.1f} N on the grip face", GRIP1),
                    (f"neck root: opening against an obstacle, {F1:.1f} N on the outer face", OPEN1),
                    (f"neck root: yaw stall {F_YAW_Z:.1f} N along z at the tip (bottom face, Kt 2.5)", YAW)):
    sf, lab, x, s, t = worst_in(cases, C.X_P1, C.X_P1 + 0.5)
    add(f"{name} [{lab}]", sf, f"x {x:.1f}: sigma {s:.2f}, tau {t:.2f}", ALLOW_Z / sf, ALLOW_Z, SF_SHORT)
g_last = GROOVES[-1]
sf, lab, x, s, t = worst_in(GRIP1, g_last - 1.0, g_last + 1.0)
add(f"last groove (x {g_last:.1f}, Kt {KT_GROOVE}): one jaw blocked, {F1:.1f} N on the grip face [{lab}]", sf,
    f"x {x:.1f}: sigma {s:.2f}, tau {t:.2f}", ALLOW_Z / sf, ALLOW_Z, SF_SHORT)
sf, lab, x, s, t = worst_in(GRIP1, g_last + 1.0, X_GRIP - 3.0)
add(f"ungrooved tip beyond the last groove (x {g_last + 1:.1f}..{X_GRIP - 3:.1f}): one jaw blocked [{lab}]", sf,
    f"x {x:.1f}: sigma {s:.2f}, tau {t:.2f}", ALLOW_Z / sf, ALLOW_Z, SF_SHORT)
# information: the torsional shear on the neck's bottom face where the rack's teeth leave a 2.1 mm step. The teeth are
# thin ribs (1.6..2.1 along y) with free faces normal to y, so they cannot carry the face's tau_xy and the step does not
# concentrate it (Kts ~1; the bending Kt 2.5 there stays). Bound: Kts 1.5 at the face's mid-point, where sigma from the
# grip's M_z is zero
p0 = props(section(C.X_P1))
Qg = (X_GRIP, 0.0, z_range(X_GRIP)[0] + 0.5)
Mx = (Qg[1] - p0["yc"]) * 0 - (Qg[2] - p0["zc"]) * (-F1)
tau_b = 1.5 * roark_tau(Mx, 20.0, 10.0) + 1.5 * F1 / p0["A"]
add("info: neck root's bottom face mid-point, grip torsion with a torsional Kts 1.5 bound (see strength.md)",
    SHEAR_Z / tau_b, f"tau {tau_b:.2f} (sigma 0 there)", tau_b, SHEAR_Z, SF_SHORT, d="Z shear", rows=INFO)


# ---------------------------------------------------------------- rack teeth (same method as the pinion job)
def contact_ratio(m, rp, tip_relief):
    rb = rp * math.cos(PRESSURE)
    ra = rp + m - tip_relief
    pb = math.pi * m * math.cos(PRESSURE)
    L = math.sqrt(ra ** 2 - rb ** 2) - rp * math.sin(PRESSURE) + (m - tip_relief) / math.sin(PRESSURE)
    return L, pb


def rack_tooth(Wn, b, backlash=None, at="hpstc", kf=True):
    m, fillet, tr = C.M, C.RACK_ROOT_FILLET, C.TIP_RELIEF
    backlash = C.RACK_BACKLASH if backlash is None else backlash
    pts = rack_outline(m, -6 * m, 6 * m, 10.0, 20.0, backlash, phase=0.0, root_fillet=fillet, tip_relief=tr,
                       fillet_pts=40)
    right = sorted([(x, y) for (x, y) in reversed(pts[2:]) if 0 <= x <= math.pi * m / 2 + 1e-9], key=lambda q: q[0])

    def half_w(y):
        out = None
        for (x0, y0), (x1, y1) in zip(right, right[1:]):
            if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
                xx = x0 + (x1 - x0) * (y - y0) / (y1 - y0)
                out = xx if out is None else min(out, xx)
        return out
    L, pb = contact_ratio(m, C.R_P, tr)
    yt = m - tr
    yl = yt if at == "tip" else yt - (L - pb) * math.sin(PRESSURE)
    xl = half_w(yl)
    Fx, Fy = -Wn * math.cos(PRESSURE), -Wn * math.sin(PRESSURE)
    yc = yl - xl * math.tan(PRESSURE)
    best = (0.0, 0.0, 1.0)
    for k in range(2000):
        ys = -1.25 * m + (yl + 1.25 * m) * k / 2000
        h = half_w(ys)
        if not h:
            continue
        t = 2 * h
        M = (yl - ys) * Fx - xl * Fy
        s = 6 * abs(M) / (b * t * t)
        K = 0.18 + (t / fillet) ** 0.15 * (t / max(yc - ys, 1e-3)) ** 0.45 if kf and ys <= -1.25 * m + 1.2 * fillet else 1.0
        if s * K > best[0]:
            best = (s * K, t, K)
    return best


B_EFF = C.FACE_W - C.CLR - P.BED_CHAMFER          # rack float 0.25 in its guides, 0.3 bed chamfer (and the pinion's 0.25)
Wn1 = T_STALL / (C.R_P * math.cos(PRESSURE))
for name, W, req in ((f"rack teeth, one jaw blocked ({F1:.1f} N), HPSTC + Kf, face {B_EFF:.2f}", Wn1, SF_SHORT),
                     (f"rack teeth, both jaws ({F2:.1f} N, cyclic), HPSTC + Kf", Wn1 / 2, SF_CYCLIC),
                     (f"rack teeth, crash {F_CRASH:.0f} N along y on one finger (held by the claw servo)",
                      F_CRASH / math.cos(PRESSURE), SF_SHORT)):
    s, t, K = rack_tooth(W, B_EFF)
    sf = ALLOW_XY / s
    add(name, sf, f"root width {t:.2f}, Kf {K:.2f}", s, ALLOW_XY, req, d="XY")
s, t, K = rack_tooth(Wn1, C.FACE_W, at="tip", kf=False)
add(f"info: rack teeth, one jaw blocked, Lewis tip load, no Kf, full face {C.FACE_W:.0f}", ALLOW_XY / s,
    f"width {t:.2f}", s, ALLOW_XY, SF_SHORT, d="XY", rows=INFO)


# ---------------------------------------------------------------- rack as a bar between its guide contacts
def thrust(F, x_grip):
    """Rack-end reactions (front plate at one end, lip/rail at the other) for a grip force F at x_grip: the couple
    F (x_grip - X_MESH) over the span between the contacts. Worst span: jaws fully open (rack end at the cover's edge)."""
    span_closed = C.RACK_Y[1] - C.RACK_Y[0]
    span_open = (C.RACK_Y[1] - C.STROKE) - (-C.HALF_Y)
    M = F * (x_grip - X_MESH)
    return M, M / span_closed, M / span_open


M_c, R_closed, R_open = thrust(F1, X_GRIP)
Z_rack = C.FACE_W * C.RACK_BACK ** 2 / 6                     # solid back only (the teeth add, ignored)
add(f"rack bar bending between its end contacts, one jaw blocked (couple {M_c:.0f} N.mm, stress along y: in the bed "
    f"plane)", ALLOW_XY / (M_c / Z_rack), f"solid back {C.FACE_W:.0f} x {C.RACK_BACK:.0f}", M_c / Z_rack, ALLOW_XY,
    SF_SHORT, d="XY")
A_end = 3.0 * (C.RACK_OUT - C.RACK_TIP - 2.1)               # 3 mm of the rack's end face over its solid back
add(f"rack end on the lip / front plate, thrust {R_open:.1f} N (jaws open; {R_closed:.1f} closed), compression across "
    f"the layers", BEARING / (R_open / A_end), f"3 mm x {C.RACK_OUT - C.RACK_TIP - 2.1:.1f} of the end face",
    R_open / A_end, BEARING, SF_SHORT, d="Z comp")

# ---------------------------------------------------------------- report
print(f"jaw: rack face {C.FACE_W}, back {C.RACK_BACK}, neck {C.NECK_Y} x {C.NECK_Z[1] - C.NECK_Z[0]} (r {C.NECK_FILLET}), "
      f"finger {C.BLADE_T_ROOT} -> {C.BLADE_T}, tip x {C.X_TIP}; grooves at {GROOVES[0]:.1f}..{GROOVES[-1]:.1f}")
print(f"loads: stall {F1:.1f} N one jaw / {F2:.1f} N both, crash {F_CRASH:.0f} N, yaw {F_YAW_Z:.1f} N, hand {F_HAND:.0f} N")
for x in (C.X_P1, 36.0, C.NECK_X1, 42.0, C.NECK_X1 + P.GUSSET, 55.0, C.TAPER_X0, 66.0, C.TAPER_X1, 80.0):
    p = props(section(x))
    print(f"  section x {x:5.2f}: A {p['A']:6.1f}  centroid y {p['yc']:6.2f} z {p['zc']:6.2f}  Iyy {p['Iyy']:8.0f}  "
          f"Izz {p['Izz']:7.0f}  Iyz {p['Iyz']:6.0f}")


def table(rows, start=1):
    for i, (case, sec, d, s, a, sf, req) in enumerate(rows, start):
        ok = "OK" if sf >= req else "**FAIL**"
        print(f"| {i} | {case} | {sec} | {d} | {s:.2f} | {a:.2f} | {sf:.2f} | {req:.0f} | {ok} |")


print("\n'Z comb' rows: across-layer normal stress and interlayer shear combined; stress column = 12.5 / SF.")
print("| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |")
print("|---|---|---|---|---|---|---|---|---|")
table(ROWS)
print("\nInformation rows (not in the verdict):")
table(INFO, start=len(ROWS) + 1)
worst = min(ROWS, key=lambda r: r[5] / r[6])
print(f"\nlowest SF {worst[5]:.2f} (required {worst[6]:.0f}): {worst[0]} / {worst[1]}")
print("VERDICT (calculation):", "FAIL" if any(r[5] < r[6] for r in ROWS) else "NEEDS_TEST (placeholder allowables)")

# references at the governing case
Q_corner = (X_GRIP, 0.0, z_range(X_GRIP)[0] + 0.5)
sf_nokt = min(section_sf(x / 10, Q_corner, (0, -F1, 0), use_kt=False)[0]
              for x in range(int(C.X_P1 * 10), int((X_GRIP - 3) * 10)))
print(f"reference: one-jaw grip at the tip's bottom corner with every Kt = 1: lowest SF {sf_nokt:.2f}")
sf_root = min(section_sf(C.X_P1 + d / 10, Q, (0, -F1, 0))[0] for _, Q in grip_points("grip") for d in range(0, 6))
print(f"reference: one-jaw grip, neck root (x {C.X_P1}-{C.X_P1 + 0.5}) only: lowest SF {sf_root:.2f}")


def governing_grip():
    return worst_over([(lab, Q, (0, -F1, 0)) for lab, Q in grip_points("grip")])


print("\nWhat-if, one jaw blocked at the grip face (the governing row):")
_save = (P.GROOVE_X, C.BLADE_T, KT_GROOVE)
for name, gx_end, bt, ktg in (("as drawn", None, None, None),
                              ("grooves stop at x 70 (none in the last 13 mm)", 70.0, None, None),
                              ("grooves stop at x 66", 66.0, None, None),
                              ("grooves with r 0.3 rounded roots (Kt 2.0)", None, None, 2.0),
                              ("tip 7 mm thick (BLADE_T 6 -> 7)", None, 7.0, None)):
    if gx_end is not None:
        P.GROOVE_X = (_save[0][0], gx_end)
    if bt is not None:
        C.BLADE_T = bt
    if ktg is not None:
        KT_GROOVE = ktg
    GROOVES[:] = []
    _x = P.GROOVE_X[0]
    while _x <= P.GROOVE_X[1] + 1e-9:
        GROOVES.append(_x)
        _x += P.GROOVE_PITCH
    sf, lab, x, s, t = governing_grip()
    print(f"  {name:48s}: lowest SF {sf:.2f} at x {x:.1f} [{lab}]")
    P.GROOVE_X, C.BLADE_T, KT_GROOVE = _save
GROOVES[:] = []
_x = P.GROOVE_X[0]
while _x <= P.GROOVE_X[1] + 1e-9:
    GROOVES.append(_x)
    _x += P.GROOVE_PITCH

# what-if: the pinion job's recommended change (face 12, backlash 0.10 / 0.80) on the rack teeth
b12 = 12.0 - C.CLR - P.BED_CHAMFER
for bl in (0.5, 0.7, 0.8):
    s, *_ = rack_tooth(Wn1, b12, backlash=bl)
    print(f"what-if rack teeth, face 12, rack backlash {bl:.2f}: SF {ALLOW_XY / s:.2f} (one jaw blocked)")

# ---------------------------------------------------------------- optional CAD cross-check of the hand sections
if "--cad" in sys.argv:
    import importlib.util
    sys.path.insert(0, str(TOOLS))
    sys.path.insert(0, str(ASSY))
    from build123d import Box, Pos
    spec = importlib.util.spec_from_file_location("jaw_model", HERE / "model.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    jaw = mod.design()
    for x in (C.X_P1 + 0.05, 36.0, 42.0, 50.0, 61.6, 70.0, 80.0):
        sl = jaw & (Pos(x, 0, 30) * Box(0.02, 200, 200))
        a_cad = sl.volume / 0.02
        print(f"CAD x {x:5.2f}: A {a_cad:6.1f}  hand {props(section(x))['A']:6.1f}")

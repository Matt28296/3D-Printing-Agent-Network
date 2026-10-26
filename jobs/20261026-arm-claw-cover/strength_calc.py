"""Strength check, round 2: jobs/20261026-arm-claw-cover (front plate in two pieces + tie, top wall, upper lip).

Run from the project root:  python3 jobs/20261026-arm-claw-cover/strength_calc.py
Plain python3: parameters come from claw_frame.py, this job's model.py and tools/hobby_parts.py (ast module).

The cover prints standing on its -y end: print Z = claw y. Bending of the front plate, the top wall, the lip and the
tie in the side profile (stresses along claw x or z) runs along the layers (25 MPa); beams along claw y (the strip
under slot B) bend across them (12.5 MPa). Placeholder PETG allowables (no library row): NEEDS_TEST at best.

The pinion pass-through and the two open-ended slots cut the front plate into two pieces:
  upper piece  y > ~7 (and over slot A's closed end): hangs from the top wall only;
  lower piece  the strip under slot B plus the -y region up to slot A: screwed to the wrist plate's front edge
               (2 x M2.5 at y +-24, z 3) and tied to the lip by the tie (post + web, y -32..-24).
Each rack reacts its finger's moment as a couple of x-forces at its two ends (it cocks in its 0.25 mm gaps): forward
on the front plate at one end, backward on the lip (rack A) or the frame's rail (rack B) at the other. A grip
(closing stall) puts rack A's forward contact on the upper piece near the top wall; anything that pushes a finger
TOWARDS closing (a desk crash on the lower finger, a hand, the claw opening against an obstacle) reverses the couple:
rack A then pushes the lower piece's top edge (z 36.25-38.25, the 2 mm strip under slot A) and rack B the upper
piece's bottom edge (z 16.25-18.1).
"""
import ast
import math
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSY = ROOT / "jobs" / "20261025-robot-arm-assembly"
TOOLS = ROOT / "tools"

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
JAW_BED_CHAMFER = consts(ROOT / "jobs" / "20261026-arm-claw-jaw" / "model.py",
                         {**CF_ENV, "HOLE_COMP_DEFAULT": HOLE_COMP_DEFAULT})["BED_CHAMFER"]

ALLOW_XY, ALLOW_Z = 25.0, 12.5
SHEAR_Z = 6.25
BEARING = 25.0
SF_SHORT, SF_CYCLIC = 3.0, 4.0
KT_SHARP, KT_FILLET = 2.5, 1.5

# ---------------------------------------------------------------- loads
T_STALL = HOBBY["MG90S"].stall_torque_nmm
F1 = T_STALL / C.R_P                  # 21.6 N
X_MESH = (C.X_P0 + C.X_P1) / 2
X_GRIP = C.X_TIP - 3.0
F_CRASH = 13.0
F_YAW_Z = 1079.0 / (2 * 76.0)
F_HAND = 5.0
SPAN_CLOSED = C.RACK_Y[1] - C.RACK_Y[0]                  # 56.5
SPAN_OPEN = (C.RACK_Y[1] - C.STROKE) - (-C.HALF_Y)       # 41.4 (rack end beyond the cover's edge)


def thrust(F, x_load, span):
    return F * (x_load - X_MESH) / span


ROWS, INFO = [], []


def row(case, sec, d, stress, allow, req, rows=ROWS):
    sf = allow / stress if stress > 1e-12 else float("inf")
    rows.append((case, sec, d, stress, allow, sf, req))
    return sf


# ================================================================ 1. lip wall behind rack A (cantilever from the top wall)
LIP_H = C.Z_TOP0 - (C.ZS + C.RAIL_IN)                    # 11.75
H_R = LIP_H / 2
PATCH = 2.0


def wall(case, R, e_edge, req, t=C.GUIDE_T, kt=KT_SHARP, rows=ROWS, lever=H_R, extra=0.0, label="lip root at the top "
         "wall, rack side"):
    b = PATCH + extra + lever + min(lever, e_edge)
    s = kt * 6 * R * lever / (b * t * t)
    return row(case, f"{label} (Kt {kt}): b_eff {b:.1f}, t {t:.1f}, lever {lever:.1f}", "XY", s, ALLOW_XY, req, rows)


R_go = thrust(F1, X_GRIP, SPAN_OPEN)
R_gc = thrust(F1, X_GRIP, SPAN_CLOSED)
wall(f"stall, one jaw blocked, jaws 44 open: rack A's -y end at the lip's end, R {R_go:.1f} N (the tie's prop "
     f"ignored)", R_go, 0.0, SF_SHORT)
wall(f"stall, one jaw blocked, jaws closed: rack A's -y end at y {C.RACK_Y[0]:.1f}, R {R_gc:.1f} N", R_gc,
     C.HALF_Y + C.RACK_Y[0], SF_SHORT)
wall(f"stall, both jaws (cyclic), jaws 44 open: R {R_go / 2:.1f} N at the lip's end", R_go / 2, 0.0, SF_CYCLIC)
R_cc = thrust(F_CRASH, C.X_TIP, SPAN_CLOSED)
R_co = thrust(F_CRASH, C.X_TIP, SPAN_OPEN)
e_plus_closed = C.HALF_Y - C.RACK_Y[1]                    # rack A's +y end at 31.4: 0.6 from the lip's end
wall(f"crash {F_CRASH:.0f} N pushes jaw A shut, jaws closed: rack A's +y end on the lip at y {C.RACK_Y[1]:.1f}, R "
     f"{R_cc:.1f} N", R_cc, e_plus_closed, SF_SHORT)
R_oc = thrust(F1, X_GRIP, SPAN_CLOSED)
wall(f"added: opening against an obstacle, jaw A, jaws nearly closed: rack A's +y end at y {C.RACK_Y[1]:.1f}, R "
     f"{R_oc:.1f} N", R_oc, e_plus_closed, SF_SHORT)

# ================================================================ 2. upper piece: hangs from the top wall
ZA0 = C.ZS + C.NECK_Z[0] - C.SLOT_CLR                    # 38.25
ZB1 = C.ZS - C.NECK_Z[0] + C.SLOT_CLR                    # 16.25
h_a = C.Z_TOP0 - ZA0
y_apex, z_apex = C.SLOT_A_END + h_a / 2, (ZA0 + C.Z_TOP0) / 2
b_apex = C.HALF_Y - (y_apex + P.APEX_R * 0)              # width beside slot A's V apex (to the +y edge)
b_top = C.HALF_Y - C.SLOT_A_END                          # width at the top-wall junction
z_rb = (ZB1 + (C.ZS - C.RACK_TIP)) / 2                   # rack B's teeth on the plate strip: z 16.25..18.1
T5 = C.FRONT_T


def upper_rows(case, R, req, rows=ROWS):
    out = []
    for sec, z, b, kt in ((f"beside slot A's V apex (z {z_apex:.1f}, r {P.APEX_R} apex)", z_apex, b_apex, KT_FILLET),
                          (f"top-wall junction (z {C.Z_TOP0}, r {C.CORNER_FILLET} fillet)", C.Z_TOP0, b_top, KT_FILLET)):
        M = R * (z - z_rb)
        out.append(row(case, f"{sec}: b {b:.1f} x {T5:.0f}, lever {z - z_rb:.1f}", "XY", kt * 6 * M / (b * T5 ** 2),
                       ALLOW_XY, req, rows))
    return out


upper_rows(f"crash {F_CRASH:.0f} N pushes jaw B shut, jaws 44 open: rack B's +y end at the plate's edge, R {R_co:.1f} "
           f"N on the bottom edge (z {z_rb:.1f})", R_co, SF_SHORT)
upper_rows(f"added: opening against an obstacle, jaw B, jaws 44 open: R {R_go:.1f} N on the bottom edge", R_go, SF_SHORT)
R_hand = thrust(F_HAND, C.X_TIP, SPAN_OPEN)
upper_rows(f"handling: {F_HAND:.0f} N pushes jaw B shut, jaws 44 open: R {R_hand:.1f} N", R_hand, SF_SHORT)
# grip: rack A's +y end presses the upper piece near the top wall (lever to the junction ~5)
lev = C.Z_TOP0 - (ZA0 + C.Z_TOP0) / 2
wall(f"stall, one jaw blocked: rack A's +y end on the upper piece near slot A's end, R {R_go:.1f} N", R_go, 0.0,
     SF_SHORT, t=T5, kt=KT_FILLET, lever=lev, label="front plate at the top wall")

# ================================================================ 3. lower piece and the tie (post + web), rack A reversed
TIE_W = C.TIE_Y[1] - C.TIE_Y[0]                          # 8
WEB_L = C.X_F0 - C.RAIL_X1                               # 10.5
WEB_H = 2 * C.TIE_Z                                      # 16
z_ra = ((C.ZS + C.RACK_TIP) + ZA0) / 2                   # rack A's teeth on the lower piece's top strip, ~37.3
z_web_top = C.ZS + C.TIE_Z                               # 35.25
z_post_top = C.ZS + C.RAIL_IN                            # 36.75: post meets the lip
SCREW_SHARE = 0.4      # share of the reversed thrust that reaches the M2.5 screws (stiffness estimate 0.2-0.35)


def tie_rows(case, R, req, rows=ROWS):
    out = []
    # strip above the web: 3 mm of plate between the web's top and slot A, the rack's teeth press it forward
    lev = z_ra - z_web_top
    b = TIE_W
    out.append(row(f"{case}: plate strip above the web", f"cantilever {lev:.1f} from the web top, b {b:.0f} x {T5:.0f}, Kt "
                   f"{KT_SHARP}", "XY", KT_SHARP * 6 * R * lev / (b * T5 ** 2), ALLOW_XY, req, rows))
    # web: tension R plus the bending of R's offset from the web's mid-height; sharp junctions
    e = z_ra - C.ZS
    s_web = R / (TIE_W * WEB_H) + 6 * R * e / (TIE_W * WEB_H ** 2)
    out.append(row(f"{case}: web, tension + bending at its junctions", f"{TIE_W:.0f} x {WEB_H:.0f}, offset {e:.1f}, Kt "
                   f"{KT_SHARP}", "XY", KT_SHARP * s_web, ALLOW_XY, req, rows))
    # post + lip: the tie force enters the lip's bottom edge at y -32..-24; the lip bends from the top wall
    lev = C.Z_TOP0 - z_post_top
    b = TIE_W + lev                                       # one-sided 45-degree spread (y -32 is a free edge)
    out.append(row(f"{case}: lip root above the post (the tie takes all of R)", f"b_eff {b:.1f} x {C.GUIDE_T:.0f}, lever "
                   f"{lev:.1f}, sharp roots Kt {KT_SHARP}", "XY", KT_SHARP * 6 * R * lev / (b * C.GUIDE_T ** 2),
                   ALLOW_XY, req, rows))
    # post just under the lip: section 4 x 8, the force R arrives at the web's top: lever to the lip ~1.5
    lev = z_post_top - z_web_top
    out.append(row(f"{case}: post between the web and the lip", f"{C.GUIDE_T:.0f} x {TIE_W:.0f}, lever {lev:.1f}, Kt "
                   f"{KT_SHARP}", "XY", KT_SHARP * 6 * R * lev / (TIE_W * C.GUIDE_T ** 2) + R / (TIE_W * C.GUIDE_T),
                   ALLOW_XY, req, rows))
    # screw path: the lower piece pivots on the wrist plate's bottom edge, the M2.5 3 mm above it holds it
    T_s = SCREW_SHARE * R * z_ra / C.FRONT_SCREWS[0][1]
    out.append(row(f"{case}: M2.5 at y -24 ({SCREW_SHARE:.0%} of R reaches it: {T_s:.0f} N), pull-out from the frame",
                   "M2.5, 7 engaged", "Z shear", T_s / (math.pi * 2.5 * 7.0), SHEAR_Z, req, rows))
    return out


tie_rows(f"crash {F_CRASH:.0f} N pushes jaw A shut, jaws 44 open: rack A's -y end at the cover's edge, R {R_co:.1f} N",
         R_co, SF_SHORT)
tie_rows(f"added: opening against an obstacle, jaw A, jaws 44 open: R {R_go:.1f} N", R_go, SF_SHORT)
tie_rows(f"handling: {F_HAND:.0f} N pushes jaw A shut: R {R_hand:.1f} N", R_hand, SF_SHORT)

# ================================================================ 4. strip under slot B (beam along y, across the layers)
ZB0 = C.ZS - C.NECK_Z[1] - C.SLOT_CLR                    # 5.75
STRIP_D = ZB0 - C.FRONT_Z0                               # 9.75
Z_strip = T5 * STRIP_D ** 2 / 6


def strip_moments(Fs, y0, y1, n=40):
    """Propped cantilever: fixed at slot B's closed end (y -SLOT_B_END), pinned at the M2.5 at y +24, overhang to +32.
    Uniform load Fs over the neck's y range [y0, y1] (clipped to the plate). Returns (M at the fixed end, M at the screw)."""
    yA, yB = -C.SLOT_B_END, C.FRONT_SCREWS[1][0]
    L = yB - yA
    MA = MB = 0.0
    y0, y1 = max(y0, yA), min(y1, C.HALF_Y)
    for k in range(n):
        y = y0 + (y1 - y0) * (k + 0.5) / n
        p = Fs / n
        if y <= yB:
            a, b = y - yA, yB - y
            MA += p * a * b * (L + b) / (2 * L * L)
        else:
            c = y - yB
            MB += p * c
            MA += p * c / 2                               # carry-over of the overhang moment to the fixed end
    return MA, MB


# A -z push on jaw B's tip pitches the jaw nose-down. The wrist plate and this strip can only push the jaw up (+z); the
# only force that can hold the jaw's rear down is the pinion, on the rack's teeth. So the strip carries the most when the
# rack has lifted off the plate: the jaw then pivots on the strip's front edge (x X_F1) while the pinion holds the rack's
# rear end (past its bed chamfer): S = F (X_TIP - x_r) / (X_F1 - x_r) = 4.0 F, and the pinion takes S - F = 3.0 F. With
# the rack on the plate and a rigid pinion the strip carries nothing: the rack's rear reaches the pinion first (0.040 rad
# against 0.048 rad for the neck to close its 0.25 gap), and the pinion takes 5.2 F (pinion job).
X_REAR = C.X_P0 + JAW_BED_CHAMFER
lever_strip = (C.X_TIP - X_REAR) / (C.X_F1 - X_REAR)
for name, F in ((f"yaw stall {F_YAW_Z:.1f} N", F_YAW_Z), (f"hand push {F_HAND:.0f} N", F_HAND)):
    Fs = lever_strip * F
    for pos, (y0, y1) in (("jaws closed", (0.0, C.NECK_Y)), ("jaws 44 open", (C.STROKE, C.STROKE + C.NECK_Y))):
        MA, MB = strip_moments(Fs, y0, y1)
        sA = 1.7 * MA / Z_strip                           # slot end, r 2 corner (r/h 0.21: Kt 1.7)
        d_net = STRIP_D - (C.M25_CLEAR + P.HOLE_COMP)
        sB = 2.0 * 6 * MB / (T5 * d_net ** 2)              # through the M2.5 hole (Kt 2)
        row(f"{name} on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to {Fs:.0f} N "
            f"(x{lever_strip:.2f}: the rack lifted off the plate, the pinion holding its rear), {pos}",
            f"strip {STRIP_D:.2f} x {T5:.0f}: slot end (Kt 1.7) / through the screw hole (Kt 2)", "Z", max(sA, sB),
            ALLOW_Z, SF_SHORT)

# ================================================================ 5. top wall
F_sep = F1 * math.tan(math.radians(20))
M_twist = F1 * ((C.ZS + C.R_P) - (C.ZS - 9.0))           # grip force 9 below the axis vs the pitch line: twists rack A
R_lift = F_sep / 2 + M_twist / SPAN_OPEN
span_tw = C.X_F0 - C.RAIL_X1
M_tw = R_lift * span_tw / 8                               # fixed-fixed, point load mid-span
b_tw = 2 * span_tw
row(f"rack A lift: separating {F_sep:.1f} N + grip twist {M_twist:.0f} N.mm -> {R_lift:.1f} N at the rack end",
    f"top wall between the lip and the front plate, span {span_tw:.1f}, b {b_tw:.0f} x {C.TOP_T:.0f}", "XY",
    KT_SHARP * 6 * M_tw / (b_tw * C.TOP_T ** 2), ALLOW_XY, SF_SHORT)
# camera mount pad: a USB tug tips the mount back over the cover's rear edge (the pad's rear edge bears on x 0..1)
M_tip = 10.0 * (C.CAM_ZC + 13.5 * math.cos(math.radians(C.CAM_TILT)) + 13.5 * math.sin(math.radians(C.CAM_TILT))
                - C.Z_TOP1)
F_edge = M_tip / (C.TOP_SCREWS[0][0] - C.PAD_X[0])
row(f"USB tug 10 N tips the camera mount back: {F_edge:.0f} N on the top wall's rear edge", "50 x 1 mm contact",
    "XY", F_edge / (C.MOUNT_Y[1] - C.MOUNT_Y[0]), BEARING, SF_SHORT)


# ---------------------------------------------------------------- report
def table(rows, start=1):
    for i, (case, sec, d, s, a, sf, req) in enumerate(rows, start):
        ok = "OK" if sf >= req else "**FAIL**"
        print(f"| {i} | {case} | {sec} | {d} | {s:.2f} | {a:.2f} | {sf:.2f} | {req:.0f} | {ok} |")


print(f"cover: front plate {C.FRONT_T} (z {C.FRONT_Z0}..{C.Z_TOP0}), top wall {C.TOP_T}, lip {C.GUIDE_T} x {LIP_H}; "
      f"slot A z {ZA0}..{C.Z_TOP0} (V apex y {y_apex:.2f}), slot B z {ZB0}..{ZB1}; tie y {C.TIE_Y}, web {WEB_L} x "
      f"{WEB_H}, post {C.GUIDE_T} x {TIE_W}")
print(f"rack thrust: grip one jaw {R_gc:.1f} (closed) / {R_go:.1f} N (open); crash {R_cc:.1f} / {R_co:.1f}; hand "
      f"{R_hand:.1f} (open)")
print("\n| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |")
print("|---|---|---|---|---|---|---|---|---|")
table(ROWS)
worst = min(ROWS, key=lambda r: r[5] / r[6])
print(f"\nlowest SF {worst[5]:.2f} (required {worst[6]:.0f}): {worst[0]} / {worst[1]}")
print("VERDICT (calculation):", "FAIL" if any(r[5] < r[6] for r in ROWS) else "NEEDS_TEST (placeholder allowables)")

# ---------------------------------------------------------------- what-if lines
print("\nWhat-if, lip (worst: stall at the lip's end, jaws open) and tie (opening stall, jaws open):")
for name, t, kt in (("as drawn: GUIDE_T 4, sharp roots", 4.0, KT_SHARP), ("GUIDE_T 8, sharp", 8.0, KT_SHARP),
                    ("GUIDE_T 10, sharp", 10.0, KT_SHARP), ("GUIDE_T 8 + r 2 fillets at the lip's roots", 8.0, KT_FILLET)):
    sf_lip = wall("w", R_go, 0.0, SF_SHORT, t=t, kt=kt, rows=[])
    lev = C.Z_TOP0 - z_post_top
    sf_tie = ALLOW_XY / (kt * 6 * R_go * lev / ((TIE_W + lev) * t * t))
    sf_post = ALLOW_XY / (KT_SHARP * 6 * R_go * (z_post_top - z_web_top) / (TIE_W * t * t) + R_go / (TIE_W * t))
    print(f"  {name:44s}: lip SF {sf_lip:.2f}; lip above the post {sf_tie:.2f}; post {sf_post:.2f}")
print("\nWhat-if, upper piece (worst: opening stall on jaw B, jaws open):")
for name, t in (("as drawn: FRONT_T 5", 5.0), ("FRONT_T 6", 6.0), ("FRONT_T 7", 7.0)):
    T5 = t
    print(f"  {name:22s}: SF {min(upper_rows('w', R_go, SF_SHORT, rows=[])):.2f} (crash only: "
          f"{min(upper_rows('w', R_co, SF_SHORT, rows=[])):.2f})")
T5 = C.FRONT_T
# a second tie at y 24..32 (same post and web, between the racks, outside every jaw path) joins the upper piece's lower
# half to the lip: rack B's reversed push at z 17.2 then enters the web 2 mm above it, as rack A's does on the lower piece
for name, t in (("second tie at y 24..32, GUIDE_T 4", 4.0), ("second tie at y 24..32, GUIDE_T 8", 8.0)):
    lev_s = (C.ZS - C.TIE_Z) - z_rb
    sf_strip = ALLOW_XY / (KT_SHARP * 6 * R_go * lev_s / (TIE_W * T5 ** 2))
    lev = C.Z_TOP0 - z_post_top
    sf_lip = ALLOW_XY / (KT_SHARP * 6 * R_go * lev / ((TIE_W + lev) * t * t))
    print(f"  {name:36s}: plate strip under the web SF {sf_strip:.2f}, lip above the post SF {sf_lip:.2f} (opening stall)")
print("\nWhat-if, strip under slot B (yaw stall, the worse of closed / open):")
for name, d in (("as drawn: 9.75 deep (FRONT_Z0 -4)", STRIP_D), ("10.75 deep (FRONT_Z0 -5)", STRIP_D + 1.0),
                ("11.75 deep (FRONT_Z0 -6)", STRIP_D + 2.0), ("13.75 deep (FRONT_Z0 -8)", STRIP_D + 4.0)):
    Zs = T5 * d ** 2 / 6
    worst_s = 0.0
    for (y0, y1) in ((0.0, C.NECK_Y), (C.STROKE, C.STROKE + C.NECK_Y)):
        MA, MB = strip_moments(lever_strip * F_YAW_Z, y0, y1)
        dn = d - (C.M25_CLEAR + P.HOLE_COMP)
        worst_s = max(worst_s, 1.7 * MA / Zs, 2.0 * 6 * MB / (T5 * dn ** 2))
    print(f"  {name:36s}: SF {ALLOW_Z / worst_s:.2f}")
print("  (or open slot B's bottom clearance 0.25 -> 0.6 so the rack's rear rests on the pinion first: the strip is then "
      "unloaded and the pry goes into the pinion's root lands; see the pinion job)")

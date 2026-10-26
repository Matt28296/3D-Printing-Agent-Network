"""Strength check, round 2: jobs/20261026-arm-claw-frame (wrist plate + servo bulkhead + rail wall).

Run from the project root:  python3 jobs/20261026-arm-claw-frame/strength_calc.py
Plain python3: parameters come from claw_frame.py, this job's model.py and tools/hobby_parts.py (ast module).

The frame prints back face down: layers are z = const planes. Wrist-plate bending runs along the layers (25 MPa);
bending of the bulkhead and of the rail wall about their roots (stress along z) runs across them (12.5 MPa);
pull-out and punching shear are taken as interlayer shear (6.25 MPa). Placeholder PETG allowables (no library row):
NEEDS_TEST at best.
"""
import ast
import math
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


def link_back_z(s, depth=HORN_DEPTH):
    return (s.total_h - s.tab_height) + 0.6 - depth


HOLE_COMP_DEFAULT = consts(TOOLS / "cadlib.py", {})["HOLE_COMP_DEFAULT"]
CF_ENV = consts(ASSY / "claw_frame.py", {**HOBBY, "link_back_z": link_back_z})
C = SimpleNamespace(**{k: v for k, v in CF_ENV.items() if k.isupper()})
P = SimpleNamespace(**{k: v for k, v in consts(HERE / "model.py", {**CF_ENV, "HOLE_COMP_DEFAULT": HOLE_COMP_DEFAULT}).items()
                       if k.isupper()})
S = C.SERVO                      # claw MG90S
W = C.WRIST_HORN                 # wrist MG90S single-arm horn
BRIO = HOBBY["BRIO_4K"]

# ---------------------------------------------------------------- allowables and required safety factors
ALLOW_XY, ALLOW_Z = 25.0, 12.5
SHEAR_XY, SHEAR_Z = 12.5, 6.25
BEARING = 25.0
SF_SHORT, SF_CYCLIC = 3.0, 4.0        # cyclic and sustained both 4
KT_SHARP, KT_FILLET = 2.5, 1.5

# ---------------------------------------------------------------- loads
G = 9.81e-3                           # N per g
T_STALL = S.stall_torque_nmm          # 216 N.mm, MG90S at 6 V (claw and wrist servos)
F1 = T_STALL / C.R_P                  # 21.6 N one jaw blocked; 10.8 N per jaw with both
X_MESH = (C.X_P0 + C.X_P1) / 2
X_GRIP = C.X_TIP - 3.0                # spec: grip 3 mm from the tip
F_CRASH = 13.0                        # N at a fingertip or at the camera (SYS-11's arm push; the wrist is back-driven)
F_TUG = 10.0                          # N USB cable tug at the camera (spec), any direction
EE_SOLID_G = 224.1                    # torque_budget.json, camera, solid parts (the spec's 224 g)
M_OVERHUNG = {0: 108.0, 50: 124.0}    # torque_budget.json overhung_moment_nmm, wrist, camera (SYS-04), sustained
MOVING = 1.3                          # torque_budget's moving factor on the sustained moment
CAM_G = BRIO.mass_g + 5.0 + 13.3 + 5.0     # Brio, thumb screw, mount (solid), cable allowance on the claw
PRELOAD_M2 = 100.0                    # N, M2 x 12 wrist clamp snug (assumption, as the pinion clamp and the arm jobs)


def cam_to_g(cx, cz):
    a = math.radians(C.CAM_TILT)
    return C.CAM_XC + cx * math.cos(a) + cz * math.sin(a), C.CAM_ZC - cx * math.sin(a) + cz * math.cos(a)


PLUG = cam_to_g(-BRIO.width / 2 - 8.0, BRIO.height / 2)     # right-angle plug's cable exit, 8 mm behind the back, mid-height
CAM_END = cam_to_g(0.0, BRIO.height / 2)                    # centre of the Brio's end face (y +-51)
CAM_CG = cam_to_g(0.0, BRIO.height / 2)
Y_PORT = 45.0                         # port position on the back: unmeasured (01 S5) -> anywhere within +-45 of the centre

ROWS, INFO = [], []


def row(case, sec, d, stress, allow, req, rows=ROWS):
    sf = allow / stress if stress > 1e-12 else float("inf")
    rows.append((case, sec, d, stress, allow, sf, req))
    return sf


# ================================================================ 1. wrist horn joint
Z_PIVOT = HORN_DEPTH                  # the frame rocks on the horn's outer face (pocket floor, z 2)
R_PIVOT = W.horn_d / 2                # 3.6: on the hub's edge (SYS-04 uses the hub radius too)
FLOOR = C.T_W + C.PAD_T - HORN_DEPTH  # 6.3 mm clamp floor
WASHER_OD = 6.0
HOLE_P = W.horn_screw_clear_d         # 2.4 printed (2.6 CAD)
A_WASHER = math.pi / 4 * (WASHER_OD ** 2 - HOLE_P ** 2)
A_PUNCH = math.pi * WASHER_OD * FLOOR


def clamp_rows(case, M_t, req, rows=ROWS, F_ax=0.0):
    """Transverse moment M_t on the joint, plus an axial pull F_ax: the clamp screw takes M_t / R_PIVOT + F_ax once that
    exceeds the preload."""
    T = max(PRELOAD_M2, M_t / R_PIVOT + F_ax)
    row(f"{case}: washer bearing (M_t {M_t:.0f} N.mm -> screw {T:.0f} N)", f"Ø{WASHER_OD:.0f} washer on the pad, "
        f"{A_WASHER:.1f} mm2", "Z comp", T / A_WASHER, BEARING, req, rows)
    row(f"{case}: floor punching under the washer", f"Ø{WASHER_OD:.0f} x {FLOOR:.1f} floor", "Z shear", T / A_PUNCH,
        SHEAR_Z, req, rows)


# transverse moments at the joint
M_tug = F_TUG * (PLUG[1] - Z_PIVOT)
M_camcrash = F_CRASH * (CAM_END[1] - Z_PIVOT)
M_fingercrash = F_CRASH * (C.ZS + 6.0 - Z_PIVOT)
M_sus = M_OVERHUNG[50] * MOVING
M_weight3 = 3 * M_OVERHUNG[50]
clamp_rows(f"USB tug {F_TUG:.0f} N at the plug (z {PLUG[1]:.1f}), across the shaft", M_tug, SF_SHORT)
clamp_rows(f"added: camera hits the desk, {F_CRASH:.0f} N at its end (z {CAM_END[1]:.1f})", M_camcrash, SF_SHORT)
clamp_rows(f"crash: {F_CRASH:.0f} N in the arm plane at the fingertip (z <= {C.ZS + 6:.1f})", M_fingercrash, SF_SHORT)
clamp_rows("weight x3 incl. the 250 deg/s2 ramp (cyclic): 3 x the 50 g overhung moment", M_weight3, SF_CYCLIC)
clamp_rows(f"SYS-04 overhung moment, 50 g, x{MOVING} moving (sustained)", M_sus, SF_CYCLIC)

# pocket bearing: single arm, triangular contact along its flank (peak at the arm's end)
r_in, r_out = W.horn_d / 2, W.horn_arm_len + W.horn_tip_d / 2
r_eff = r_in + 2 / 3 * (r_out - r_in)
A_arm = (r_out - r_in) * W.horn_t
for case, T, req in ((f"wrist stall {T_STALL:.0f} N.mm (cyclic)", T_STALL, SF_CYCLIC),
                     (f"crash: {F_CRASH:.0f} N at the fingertip x {C.X_TIP:.1f} back-drives the wrist "
                      f"({F_CRASH * C.X_TIP:.0f} N.mm, 5 x stall: the top of SYS-11's 3-5 x)", F_CRASH * C.X_TIP, SF_SHORT)):
    row(f"{case}: horn arm on the pocket wall", f"arm flank r {r_in:.1f}..{r_out:.1f} x {W.horn_t} (mean, resultant "
        f"at r {r_eff:.1f})", "XY", T / r_eff / A_arm, BEARING, req)
T_vice = F1 * X_GRIP
row(f"info: proof test, horn in a vice, one jaw blocked: {T_vice:.0f} N.mm through the pocket", "as above", "XY",
    T_vice / r_eff / A_arm, BEARING, SF_SHORT, INFO)

# ================================================================ 2. rail wall behind rack B
RAIL_H = C.ZS - C.RAIL_IN - C.T_W     # 11.75
H_R = RAIL_H / 2                      # thrust resultant at mid-height of the contact
PATCH = 2.0                           # contact patch along y at the cocked rack's end


def rail_rows(case, R, e_edge, req, t=C.GUIDE_T, kt=KT_SHARP, allow=ALLOW_Z, rows=ROWS, label="rail wall root, front"):
    """Cantilever wall t thick, R at H_R above its root, e_edge from the wall's free end (45-degree spread)."""
    b = PATCH + H_R + min(H_R, e_edge)
    s = kt * 6 * R * H_R / (b * t * t)
    return row(case, f"{label} (sharp, Kt {kt}): b_eff {b:.1f}, t {t:.1f}, lever {H_R:.1f}", "Z", s, allow, req, rows)


span_closed = C.RACK_Y[1] - C.RACK_Y[0]                   # 56.5: rack ends on the guides
span_open = (C.RACK_Y[1] - C.STROKE) - (-C.HALF_Y)        # 41.4: rack end beyond the frame/cover edge at 44 mm open
couple = lambda F, x: F * (x - X_MESH)
R_grip_open = couple(F1, X_GRIP) / span_open
R_grip_closed = couple(F1, X_GRIP) / span_closed
e_closed = C.HALF_Y - (-C.RACK_Y[0])                      # rack B's +y end at 25.1 closed: 6.9 from the frame's end
rail_rows(f"stall, one jaw blocked, jaws 44 open: rack B's +y end at the rail's end, R {R_grip_open:.1f} N",
          R_grip_open, 0.0, SF_SHORT)
rail_rows(f"stall, one jaw blocked, jaws closed: rack B's +y end at y {-C.RACK_Y[0]:.1f}, R {R_grip_closed:.1f} N",
          R_grip_closed, e_closed, SF_SHORT)
rail_rows(f"stall, both jaws (cyclic), jaws 44 open: R {R_grip_open / 2:.1f} N at the rail's end", R_grip_open / 2, 0.0,
          SF_CYCLIC)
R_crash_c = couple(F_CRASH, C.X_TIP) / span_closed
rail_rows(f"crash {F_CRASH:.0f} N pushes jaw B shut: rack B's -y end on the rail at y {-C.RACK_Y[1]:.1f}, R "
          f"{R_crash_c:.1f} N", R_crash_c, C.HALF_Y - C.RACK_Y[1], SF_SHORT)
R_open_stall = couple(F1, X_GRIP) / span_closed
rail_rows(f"added: opening against an obstacle, jaw B: rack B's -y end at y {-C.RACK_Y[1]:.1f}, R {R_open_stall:.1f} N",
          R_open_stall, C.HALF_Y - C.RACK_Y[1], SF_SHORT)

# ================================================================ 3. bulkhead
Z_ROOT = C.T_W + C.PAD_T              # 8.3: the pad's top meets the bulkhead's back face (sharp)
Z_WIN0 = C.ZS - (S.width + P.CLR + P.HOLE_COMP) / 2     # 20.85: window bottom
HW_WIN = (S.width + P.CLR + P.HOLE_COMP) / 2
ce = P.END_CLR + P.HOLE_COMP
y_w0 = -(S.length - S.shaft_from_end) - ce / 2          # -17.1
y_w1 = y_w0 + S.length + ce                             # 6.1
relief = (P.RELIEF_D + P.HOLE_COMP) / 2
b_neg = (y_w0 - relief) - (-C.HALF_Y)                   # -y strip at the window's bottom, through the relief
b_pos = C.HALF_Y - (y_w1 + relief)
Z_full = 2 * C.HALF_Y * C.BULK_T ** 2 / 6
# camera loads reach the bulkhead top through the two M3 screws (TOP_SCREWS); the bulkhead is taken to carry all of
# the moment (it is ~2.5 x stiffer than the cover's couple path through its lip and tie: see strength.md)
M_root_tug = F_TUG * (PLUG[1] - Z_ROOT)
row(f"USB tug {F_TUG:.0f} N along +x at the plug: bulkhead root above the pad", f"64 x {C.BULK_T} at z {Z_ROOT}, back "
    f"corner Kt {KT_SHARP}", "Z", KT_SHARP * M_root_tug / Z_full, ALLOW_Z, SF_SHORT)
# (a desk crash loads the camera along claw y, in the bulkhead's own plane: no bending row here; along x the
# fingertips reach the desk first)
M_root_w = 3 * CAM_G * G * (CAM_CG[1] - Z_ROOT)
row(f"camera package {CAM_G:.0f} g x3 along x (cyclic): bulkhead root above the pad", "as above", "Z",
    KT_SHARP * M_root_w / Z_full, ALLOW_Z, SF_CYCLIC)

# window-side strips under a tug along x at a port off the centre: the two top screws share F_x and the twist
(ys1, ys2) = (C.TOP_SCREWS[0][1], C.TOP_SCREWS[1][1])


def screw_x_forces(Fx, y_load):
    """x-forces at the two top screws (y ys1, ys2) for a force Fx along x applied at y_load."""
    F1_ = Fx * (ys2 - y_load) / (ys2 - ys1)
    return F1_, Fx - F1_


lever_top = C.Z_TOP0 - Z_WIN0
share_neg = b_neg / (b_neg + b_pos)                     # the moment of F_x about the window bottom, shared by width


def strip_Z(b, rib=None):
    """Section modulus (bending about y, tension at the farthest x fibre) of a window-side strip b wide x BULK_T
    (x X_B - BULK_T .. X_B), optionally with a rib behind it: rib = (width along y, depth behind the back face)."""
    rects = [(b, C.X_B - C.BULK_T, C.X_B)]
    if rib:
        rects.append((rib[0], C.X_B - C.BULK_T - rib[1], C.X_B - C.BULK_T))
    A = sum(w * (x1 - x0) for w, x0, x1 in rects)
    xc = sum(w * (x1 - x0) * (x0 + x1) / 2 for w, x0, x1 in rects) / A
    I = sum(w * (x1 - x0) ** 3 / 12 + w * (x1 - x0) * ((x0 + x1) / 2 - xc) ** 2 for w, x0, x1 in rects)
    c = max(xc - min(x0 for _, x0, _ in rects), max(x1 for _, _, x1 in rects) - xc)
    return I / c


def strip_rows(case, Fx, y_load, z_load, req, rows=ROWS, rib=None):
    f1, f2 = screw_x_forces(Fx, y_load)
    out = []
    for name, f, b, sh in (("-y strip", f1, b_neg, share_neg), ("+y strip", f2, b_pos, 1 - share_neg)):
        # each strip carries its own screw's x-force down from the top, plus its share of the moment above the top
        M = abs(f) * lever_top + sh * abs(Fx) * (z_load - C.Z_TOP0)
        out.append(row(f"{case}: {name}", f"{b:.1f} x {C.BULK_T} at the window's lower corner (Ø3 relief, Kt "
                       f"{KT_FILLET}), screw force {f:+.1f} N", "Z", KT_FILLET * M / strip_Z(b, rib), ALLOW_Z, req, rows))
    return out


for yp in (-Y_PORT, Y_PORT):
    strip_rows(f"USB tug {F_TUG:.0f} N along x, port at y {yp:+.0f} (twist {F_TUG * abs(yp):.0f} N.mm)", F_TUG, yp,
               PLUG[1], SF_SHORT)
strip_rows("info: same tug with the port at the centre", F_TUG, 0.0, PLUG[1], SF_SHORT, rows=INFO)
strip_rows(f"camera x3 along x (cyclic)", 3 * CAM_G * G, 0.0, CAM_CG[1], SF_CYCLIC)

# ================================================================ 4. MG90S tab pilots and the strips beside them
PILOT_CAD = S.screw_pilot_d + P.HOLE_COMP              # 1.7 CAD, 1.5 printed
x_body0 = -(S.length - S.shaft_from_end)
xm = x_body0 + S.length / 2
pilot_far, pilot_lead = xm - S.hole_dx / 2, xm + S.hole_dx / 2 + 1.3      # lead end moved 1.3 out (notch_shift_pilot)
notch_end = (y_w1 - ce / 2) + S.lead_notch_reach + P.HOLE_COMP / 2       # 7.5
strip_far_cad = (y_w0 - (pilot_far + PILOT_CAD / 2))
strip_lead_cad = (pilot_lead - PILOT_CAD / 2) - notch_end
STRIPS = {"lead-end pilot to the lead notch": strip_lead_cad, "far-end pilot to the window": strip_far_cad}
D_SCREW = 2.0                          # M2 x 8 self-tapping, major diameter
R_I = S.screw_pilot_d / 2              # printed pilot radius 0.75
L_ENG = 8.0 - S.tab_t                  # 5.5 mm engaged (spec: M2 x 8 through the 2.5 mm tab)
F_SNUG = 100.0                         # N clamp, driven snug (assumption)
T_FORM = 40.0                          # N.mm thread-forming torque of an M2 self-tapper in PETG (assumption)
MU = 0.25
p_form = 2 * T_FORM / (MU * math.pi * D_SCREW ** 2 * L_ENG)
p_clamp = F_SNUG * math.tan(math.radians(30)) / (math.pi * D_SCREW * L_ENG)
USER = []          # rows under the user's 26 Oct decision (strips kept, first-print check): reported, not in the verdict
F_t = T_STALL / (pilot_lead - pilot_far)                  # stall reaction torque on the 2 tab screws, along z
F_po = F1 * (X_MESH - C.X_B) / (pilot_lead - pilot_far)   # one jaw blocked: shaft load 17.6 mm in front of the tabs
p_po = F_po * math.tan(math.radians(30)) / (math.pi * D_SCREW * L_ENG)
for name, w_cad in STRIPS.items():
    w = w_cad + P.HOLE_COMP                             # both edges print HOLE_COMP/2 inside the CAD
    ro = R_I + w
    lame = (ro ** 2 + R_I ** 2) / (ro ** 2 - R_I ** 2)
    p = p_form + p_clamp
    row(f"screw driving, M2 x 8 snug ({F_SNUG:.0f} N) + thread forming ({T_FORM / 1000:.2f} N.m), sustained: {name}",
        f"strip {w_cad:.2f} CAD / {w:.2f} printed; hoop stress at the pilot edge (Lame peak), p {p:.1f} MPa", "Z",
        p * lame, ALLOW_Z, SF_CYCLIC, USER)
    row(f"same, mean hoop stress across the strip (p r / w): {name}", f"{w:.2f} printed", "Z", p * R_I / w, ALLOW_Z,
        SF_CYCLIC, USER)
    row(f"one jaw blocked: tab screw pulled with {F_po:.0f} N, its flank pressure added (short-term): {name}",
        f"Lame peak, p {p + p_po:.1f} MPa", "Z", (p + p_po) * lame, ALLOW_Z, SF_SHORT, USER)
    # far end only: the case's end bears on the window's end face, which the strip backs over the pilot's height
    if "far" in name:
        q = F1 / ((2 * HW_WIN) * C.BULK_T)                # 21.6 N on the window's end face (12.8 x 6.5)
        Mb = q * C.BULK_T * PILOT_CAD ** 2 / 12           # strip as a fixed-fixed bridge over the pilot, span 1.7
        row(f"one jaw blocked: the case's end bears on the window's end ({F1:.1f} N): {name}",
            f"bridge over the pilot, span {PILOT_CAD}, depth {w:.2f}", "Z", 6 * Mb / (C.BULK_T * w * w), ALLOW_Z,
            SF_SHORT, USER)
row(f"claw stall reaction {T_STALL:.0f} N.mm: {F_t:.1f} N per tab screw along z (the strips lie beside this path)",
    f"pilot wall bearing Ø{S.screw_pilot_d} x {L_ENG}", "XY", F_t / (S.screw_pilot_d * L_ENG), BEARING, SF_SHORT, USER)
row(f"one jaw blocked: tab screw pull-out {F_po:.0f} N (M2, {L_ENG} engaged)", "thread shear cylinder", "Z shear",
    F_po / (math.pi * D_SCREW * L_ENG), SHEAR_Z, SF_SHORT)

# ================================================================ 5. cover screws in the frame
L_M3 = 18.0 - (C.PAD_TOP - C.Z_TOP1) - C.TOP_T         # M3 x 18 through the 3.5 pad + 3 top wall: 11.5 engaged
# moment of a camera x-force above the bulkhead top, taken by the screws against the top's edge (lever 3.25)
M_top = F_TUG * (PLUG[1] - C.Z_TOP0)
T_m3 = M_top / (C.BULK_T / 2) / 2
row(f"USB tug {F_TUG:.0f} N along x at the plug: M3 x 18 pull-out from the bulkhead top, {T_m3:.0f} N per screw",
    f"M3, {L_M3:.1f} engaged", "Z shear", T_m3 / (math.pi * 3.0 * L_M3), SHEAR_Z, SF_SHORT)
# front M2.5 screws: the cover's lower front-plate piece pushed forward by rack B (one jaw blocked) pivots on the wrist
# plate's bottom edge; the screw 3 mm above it holds it (the tie takes a share: ignored here)
L_M25 = P.FRONT_PILOT_DEPTH - 3.0                      # 7 mm engaged (M2.5 x 12 through the 5 mm front plate)
z_rb = C.T_W + (C.RACK_BACK) / 2                       # rack B's solid back mid-height, 11
T_m25 = R_grip_open * z_rb / C.FRONT_SCREWS[0][1]
row(f"stall, one jaw blocked: rack B pushes the cover's lower piece forward ({R_grip_open:.1f} N at z {z_rb:.0f}): "
    f"M2.5 pull-out {T_m25:.0f} N", f"M2.5, {L_M25:.0f} engaged, 1.75 mm skins", "Z shear",
    T_m25 / (math.pi * 2.5 * L_M25), SHEAR_Z, SF_SHORT)
# added (as in the jaw and cover jobs): the yaw stall's out-of-plane part at a fingertip acts along the wrist axis, 83 mm
# from it: a moment across the shaft plus a pull on the clamp screw (pulling the claw off the horn is the worse sign)
F_YAW_Z = 1079.0 / (2 * 76.0)         # 7.1 N: largest out-of-plane part of a yaw stall at the fingertip (F = 1079/R, R >= 76)
clamp_rows(f"added: yaw stall {F_YAW_Z:.1f} N along the wrist axis at the fingertip (x {C.X_TIP:.1f}), pulling the claw "
           f"off the horn", F_YAW_Z * C.X_TIP, SF_SHORT, F_ax=F_YAW_Z)


# ---------------------------------------------------------------- report
def table(rows, start=1):
    for i, (case, sec, d, s, a, sf, req) in enumerate(rows, start):
        ok = "OK" if sf >= req else "**FAIL**"
        print(f"| {i} | {case} | {sec} | {d} | {s:.2f} | {a:.2f} | {sf:.2f} | {req:.0f} | {ok} |")


print(f"frame: plate {C.T_W} + pad {C.PAD_T} (floor {FLOOR}), bulkhead {C.BULK_T}, rail wall {C.GUIDE_T} x {RAIL_H}; "
      f"window y {y_w0:.2f}..{y_w1:.2f}, z {Z_WIN0:.2f}..{C.ZS + HW_WIN:.2f}; pilots y {pilot_far:.2f} / {pilot_lead:.2f}")
print(f"camera: plug exit G (x {PLUG[0]:.1f}, z {PLUG[1]:.1f}), end-face centre z {CAM_END[1]:.1f}; package {CAM_G:.0f} g")
print(f"joint moments: tug {M_tug:.0f}, camera crash {M_camcrash:.0f}, finger crash {M_fingercrash:.0f}, yaw stall "
      f"{F_YAW_Z * C.X_TIP:.0f} (+ {F_YAW_Z:.1f} N pull), weight x3 {M_weight3:.0f}, SYS-04 x1.3 {M_sus:.0f} N.mm; rack "
      f"thrust open {R_grip_open:.1f} / closed {R_grip_closed:.1f} N")
print(f"tab-pilot strips (CAD): lead {strip_lead_cad:.2f}, far {strip_far_cad:.2f}; p_form {p_form:.1f} MPa, p_clamp "
      f"{p_clamp:.1f} MPa")
print("\n| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |")
print("|---|---|---|---|---|---|---|---|---|")
table(ROWS)
print("\nInformation rows (not in the verdict):")
table(INFO, start=len(ROWS) + 1)
print("\nMG90S tab-pilot strips (user decision 26 Oct: strips kept, first-print screw-strip check, spec §8):")
table(USER, start=len(ROWS) + len(INFO) + 1)
print("(drop: this load set has no drop case)")
worst = min(ROWS, key=lambda r: r[5] / r[6])
print(f"\nlowest SF {worst[5]:.2f} (required {worst[6]:.0f}): {worst[0]} / {worst[1]}")
print("VERDICT (calculation):", "FAIL" if any(r[5] < r[6] for r in ROWS) else "NEEDS_TEST (placeholder allowables)")

# ---------------------------------------------------------------- what-if lines for the required changes
print("\nWhat-if, rail wall (rack B's +y end at the rail's end, one jaw blocked, the worst row):")
for name, t, kt in (("as drawn: 4 mm, sharp front root", 4.0, KT_SHARP),
                    ("8 mm wall, sharp", 8.0, KT_SHARP),
                    ("8 mm wall + r 2 front fillet (rack gets a 2.5 x 45 deg chamfer)", 8.0, KT_FILLET),
                    ("10 mm wall, sharp", 10.0, KT_SHARP),
                    ("block back to the bulkhead (x 10..22.35: 12.35 deep), sharp", C.RAIL_X1 - C.X_B, KT_SHARP)):
    sf = rail_rows("w", R_grip_open, 0.0, SF_SHORT, t=t, kt=kt, rows=[])
    sf_rev = rail_rows("w", R_open_stall, C.HALF_Y - C.RACK_Y[1], SF_SHORT, t=t, kt=kt, rows=[])
    print(f"  {name:62s}: SF {sf:.2f} (opening stall, jaw B: {sf_rev:.2f})")
print("\nWhat-if, wrist clamp (camera hits the desk, the worst joint row):")
for od, fl in ((6.0, FLOOR), (8.0, FLOOR), (8.0, 7.0), (10.0, 7.0)):
    T = max(PRELOAD_M2, M_camcrash / R_PIVOT)
    A_w = math.pi / 4 * (od ** 2 - HOLE_P ** 2)
    print(f"  washer Ø{od:.0f}, floor {fl:.1f}: bearing SF {BEARING / (T / A_w):.2f}, punching SF "
          f"{SHEAR_Z / (T / (math.pi * od * fl)):.2f}  (USB tug: {BEARING / (max(PRELOAD_M2, M_tug / R_PIVOT) / A_w):.2f} / "
          f"{SHEAR_Z / (max(PRELOAD_M2, M_tug / R_PIVOT) / (math.pi * od * fl)):.2f})")
print("\nWhat-if, window-side strips under the USB tug (worst of the port at -45 / +45):")
for name, rib in (("as drawn", None), ("6 mm rib behind each strip's outer edge, 8 mm deep", (6.0, 8.0)),
                  ("6 mm rib, 10 mm deep (x -6.5..3.5)", (6.0, 10.0)), ("8 mm rib, 10 mm deep", (8.0, 10.0))):
    sfs = [s for yp in (-Y_PORT, Y_PORT) for s in strip_rows("w", F_TUG, yp, PLUG[1], SF_SHORT, rows=[], rib=rib)]
    print(f"  {name:52s}: lowest SF {min(sfs):.2f}")
for yp in (10.0, 0.0):
    sfs = [s for sg in (-1, 1) for s in strip_rows("w", F_TUG, sg * yp, PLUG[1], SF_SHORT, rows=[])]
    print(f"  as drawn, port within +-{yp:.0f} mm of the centre: lowest SF {min(sfs):.2f}")
print("\nWhat-if, bulkhead root above the pad under the USB tug along +x:")
for name, kt, share in (("as drawn: sharp back corner, bulkhead takes the whole moment", KT_SHARP, 1.0),
                        ("r 1.5 fillet at the pad / bulkhead back corner (r/h 0.23: Kt 1.7)", 1.7, 1.0),
                        ("as drawn, cover's portal takes 30 % (stiffness estimate)", KT_SHARP, 0.7)):
    print(f"  {name:62s}: SF {ALLOW_Z / (kt * share * M_root_tug / Z_full):.2f}")

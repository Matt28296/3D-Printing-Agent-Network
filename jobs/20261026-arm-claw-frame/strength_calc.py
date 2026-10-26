"""Strength check, round 3: jobs/20261026-arm-claw-frame (wrist plate + servo bulkhead + rail block + ribs).

Run from the project root:  python3 jobs/20261026-arm-claw-frame/strength_calc.py
Plain python3: parameters come from claw_frame.py, this job's model.py, tools/hobby_parts.py (ast module) and the
assembly's torque_budget.json. No build123d needed. Section areas quoted as "probed" were measured on the round 3 solid
(design()) with thin slabs: z 8.35 A 1373, z 12..17.7 A 1323 (plate-top sections include the rail block), z 17.8 A 532
(bulkhead + ribs - relief), z 20 A 497 (window corner reliefs).

The frame prints back face down: layers are z = const planes. Wrist-plate bending runs along the layers (25 MPa);
bending of the bulkhead, the ribs and the rail block about their roots (stress along z) runs across them (12.5 MPa);
pull-out and punching shear are taken as interlayer shear (6.25 MPa). Placeholder PETG allowables (no library row):
NEEDS_TEST at best.
"""
import ast
import json
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
TB = json.loads((ASSY / "torque_budget.json").read_text())

# ---------------------------------------------------------------- allowables and required safety factors
ALLOW_XY, ALLOW_Z = 25.0, 12.5
SHEAR_XY, SHEAR_Z = 12.5, 6.25
BEARING = 25.0
SF_SHORT, SF_CYCLIC = 3.0, 4.0        # cyclic and sustained both 4
KT_SHARP, KT_FILLET, KT_R15 = 2.5, 1.5, 1.7

# ---------------------------------------------------------------- loads
G = 9.81e-3                           # N per g
T_STALL = S.stall_torque_nmm          # 216 N.mm, MG90S at 6 V (claw and wrist servos)
F1 = T_STALL / C.R_P                  # 21.6 N one jaw blocked; 10.8 N per jaw with both
X_MESH = (C.X_P0 + C.X_P1) / 2
X_GRIP = C.X_TIP - 3.0                # spec: grip 3 mm from the tip
F_CRASH = 13.0                        # N at a fingertip or at the camera (SYS-11's arm push; the wrist is back-driven)
F_TUG = 10.0                          # N USB cable tug at the camera (spec), any direction
EE_SOLID_G = TB["configs"]["camera, solid"]["end_effector_g"]            # 253.9 g (round 3)
OVER = TB["overhung_moment_nmm"]
M_OVERHUNG = {0: OVER["camera, payload 0 g"]["wrist"], 50: OVER["camera, payload 50 g"]["wrist"]}   # 116 / 133
MOVING = TB["moving_factor"] if isinstance(TB.get("moving_factor"), (int, float)) else 1.3
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


# ================================================================ 1. wrist horn joint (Ø8 x 0.8 washer, round 3)
Z_PIVOT = HORN_DEPTH                  # the frame rocks on the horn's outer face (pocket floor, z 2)
R_PIVOT = W.horn_d / 2                # 3.6: on the hub's edge (SYS-04 uses the hub radius too)
FLOOR = C.T_W + C.PAD_T - HORN_DEPTH  # 6.3 mm clamp floor
WASHER_OD = C.WRIST_WASHER_OD         # 8.0 (DIN 9021 M2.5 size)
WASHER_ID = 2.7                       # DIN 9021 M2.5 bore (claw_frame.py)
HOLE_P = W.horn_screw_clear_d         # 2.4 printed (2.6 CAD)
A_WASHER = math.pi / 4 * (WASHER_OD ** 2 - max(WASHER_ID, HOLE_P) ** 2)
A_PUNCH = math.pi * WASHER_OD * FLOOR


def clamp_rows(case, M_t, req, rows=ROWS, F_ax=0.0, od=WASHER_OD, floor=FLOOR):
    """Transverse moment M_t on the joint, plus an axial pull F_ax: the clamp screw takes M_t / R_PIVOT + F_ax once that
    exceeds the preload."""
    T = max(PRELOAD_M2, M_t / R_PIVOT + F_ax)
    a_w = math.pi / 4 * (od ** 2 - max(WASHER_ID, HOLE_P) ** 2)
    s1 = row(f"{case}: washer bearing (M_t {M_t:.0f} N.mm -> screw {T:.0f} N)", f"Ø{od:.0f} x {C.WRIST_WASHER_T} washer on "
             f"the pad, {a_w:.1f} mm2 (its Ø{WASHER_ID} bore)", "Z comp", T / a_w, BEARING, req, rows)
    s2 = row(f"{case}: floor punching under the washer", f"Ø{od:.0f} x {floor:.1f} floor", "Z shear",
             T / (math.pi * od * floor), SHEAR_Z, req, rows)
    return min(s1, s2)


M_tug = F_TUG * (PLUG[1] - Z_PIVOT)
M_camcrash = F_CRASH * (CAM_END[1] - Z_PIVOT)
M_fingercrash = F_CRASH * (C.ZS + 6.0 - Z_PIVOT)
M_sus = M_OVERHUNG[50] * MOVING
M_weight3 = 3 * M_OVERHUNG[50]
clamp_rows(f"USB tug {F_TUG:.0f} N at the plug (z {PLUG[1]:.1f}), across the shaft", M_tug, SF_SHORT)
clamp_rows(f"added: camera hits the desk, {F_CRASH:.0f} N at its end (z {CAM_END[1]:.1f})", M_camcrash, SF_SHORT)
clamp_rows(f"crash: {F_CRASH:.0f} N in the arm plane at the fingertip (z <= {C.ZS + 6:.1f})", M_fingercrash, SF_SHORT)
clamp_rows(f"weight x3 incl. the 250 deg/s2 ramp (cyclic): 3 x the 50 g overhung moment ({M_OVERHUNG[50]:.0f} N.mm, "
           f"torque_budget round 3)", M_weight3, SF_CYCLIC)
clamp_rows(f"SYS-04 overhung moment, 50 g, x{MOVING} moving (sustained)", M_sus, SF_CYCLIC)
F_YAW_Z = 1079.0 / (2 * 76.0)         # 7.1 N: largest out-of-plane part of a yaw stall at the fingertip
clamp_rows(f"added: yaw stall {F_YAW_Z:.1f} N along the wrist axis at the fingertip (x {C.X_TIP:.1f}), pulling the claw "
           f"off the horn", F_YAW_Z * C.X_TIP, SF_SHORT, F_ax=F_YAW_Z)

# the washer relief: the Ø9 relief starts on the pad's top face, so the washer lies flat on the pad and the 6.3 floor
# stays whole. Fit (not strength): washer radius 4.0 + 0.35 radial play on the M2 (bore 2.7) = 4.35 against the relief's
# printed radius 4.4: 0.05 to spare (reported in strength.md)
r_relief_pr = (P.WASHER_RELIEF_D - P.HOLE_COMP) / 2
washer_margin = r_relief_pr - (WASHER_OD / 2 + (WASHER_ID - 2.0) / 2)

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

# ================================================================ 2. rail block behind rack B (round 3)
RAIL_H = C.ZS - C.RAIL_IN - C.T_W     # 11.75
RAIL_D = C.RAIL_X1 - C.RAIL_X0        # 12.35: x 10..22.35, merged into the bulkhead's front face
H_R = RAIL_H / 2                      # thrust resultant at mid-height of the contact
PATCH = 2.0                           # contact patch along y at the cocked rack's end


def rail_rows(case, R, e_edge, req, t=RAIL_D, kt=KT_SHARP, allow=ALLOW_Z, rows=ROWS, label="rail block root, rack side",
              b_less=0.0):
    """The block as a cantilever from the wrist plate (conservative: its merge with the bulkhead is ignored), t deep along
    x, R at H_R above its root, e_edge from the block's free end (45-degree spread)."""
    b = PATCH + H_R + min(H_R, e_edge) - b_less
    s = kt * 6 * R * H_R / (b * t * t)
    return row(case, f"{label} (sharp, Kt {kt}): b_eff {b:.1f}, depth {t:.2f}, lever {H_R:.1f}", "Z", s, allow, req, rows)


span_closed = C.RACK_Y[1] - C.RACK_Y[0]                   # 56.5: rack ends on the guides
span_open = (C.RACK_Y[1] - C.STROKE) - (-C.HALF_Y)        # 41.4: rack end beyond the frame/cover edge at 44 mm open
couple = lambda F, x: F * (x - X_MESH)
R_grip_open = couple(F1, X_GRIP) / span_open
R_grip_closed = couple(F1, X_GRIP) / span_closed
e_closed = C.HALF_Y - (-C.RACK_Y[0])
rail_rows(f"stall, one jaw blocked, jaws 44 open: rack B's +y end at the block's end, R {R_grip_open:.1f} N",
          R_grip_open, 0.0, SF_SHORT)
rail_rows(f"stall, one jaw blocked, jaws closed: rack B's +y end at y {-C.RACK_Y[0]:.1f}, R {R_grip_closed:.1f} N",
          R_grip_closed, e_closed, SF_SHORT)
rail_rows(f"stall, both jaws (cyclic), jaws 44 open: R {R_grip_open / 2:.1f} N at the block's end", R_grip_open / 2, 0.0,
          SF_CYCLIC)
R_crash_c = couple(F_CRASH, C.X_TIP) / span_closed
rail_rows(f"crash {F_CRASH:.0f} N pushes jaw B shut: rack B's -y end on the block at y {-C.RACK_Y[1]:.1f}, R "
          f"{R_crash_c:.1f} N", R_crash_c, C.HALF_Y - C.RACK_Y[1], SF_SHORT)
R_open_stall = couple(F1, X_GRIP) / span_closed
rail_rows(f"added: opening against an obstacle, jaw B: rack B's -y end at y {-C.RACK_Y[1]:.1f}, R {R_open_stall:.1f} N",
          R_open_stall, C.HALF_Y - C.RACK_Y[1], SF_SHORT)
R_open_stall_o = couple(F1, X_GRIP) / span_open
rail_rows(f"added: opening against an obstacle, jaw B, jaws 44 open: rack B's -y end at y {-(C.RACK_Y[1] - C.STROKE):.1f}, "
          f"R {R_open_stall_o:.1f} N", R_open_stall_o, C.HALF_Y - (C.RACK_Y[1] - C.STROKE), SF_SHORT)
# the front M2.5 pilots (now 14 deep: x 20.85..34.85, top z 4.1) run under the block's rack-side root at y +-24; at the
# block's +y end the root's spread (y 24.1..32) reaches the pilot's edge (y 25.1): take that overlap off b_eff
y_pilot, d_pilot = C.FRONT_SCREWS[1][0], C.M25_PILOT + P.HOLE_COMP
overlap = max(0.0, (y_pilot + d_pilot / 2) - (C.HALF_Y - (PATCH + H_R)))
rail_rows(f"new path: the same (jaws 44 open, R {R_grip_open:.1f} N) where the 14 mm front pilot passes 1.9 under the root "
          f"(x 20.85..22.35, y {y_pilot:.0f})", R_grip_open, 0.0, SF_SHORT, b_less=overlap,
          label=f"rail block root less the pilot's {overlap:.1f} mm overlap")
# skin over a front pilot under rack B's track: separating force + the finger's pitching couple, all on the skin
F_sep = F1 * math.tan(math.radians(20))
pitch = F1 * ((C.ZS) - (C.T_W + C.RACK_BACK / 2)) / span_open
F_skin = F_sep + pitch
skin = C.T_W - (C.FRONT_SCREWS[0][1] + d_pilot / 2)
span_sk = 0.91 + 2 * 0.0                             # the flat top between the teardrop's 45-degree flanks (brief)
b_sk = C.FACE_W
M_sk = F_skin * d_pilot / 4
row(f"new path: rack B pressed down on the plate over a front pilot (separating {F_sep:.1f} N + pitch {pitch:.1f} N, all on "
    f"the skin)", f"skin {skin:.1f} over Ø{d_pilot:.1f}, b {b_sk:.0f} (rack face), simply supported", "XY",
    6 * M_sk / (b_sk * skin ** 2), ALLOW_XY, SF_SHORT)

# ================================================================ 3. bulkhead, ribs, fillet, washer relief (round 3)
Z_ROOT = C.T_W + C.PAD_T              # 8.3: the pad's top meets the bulkhead's back face (r 1.5 fillet, ribs, relief)
Z_BLOCK = C.ZS - C.RAIL_IN            # 17.75: the rail block's top meets the bulkhead's front face (sharp)
Z_WIN0 = C.ZS - (S.width + P.CLR + P.HOLE_COMP) / 2     # 20.85: window bottom
HW_WIN = (S.width + P.CLR + P.HOLE_COMP) / 2
XB0 = C.X_B - C.BULK_T                # 3.5: bulkhead back face
R_REL = P.WASHER_RELIEF_D / 2         # 4.5 (CAD)
# washer relief segment cut from the bulkhead's back face (|y| <= 2.83, 1.0 deep)
h_rel = R_REL - XB0
A_rel = R_REL ** 2 * math.acos((R_REL - h_rel) / R_REL) - (R_REL - h_rel) * math.sqrt(2 * R_REL * h_rel - h_rel ** 2)


def section(rects):
    """[(b along y, x0, x1)] -> A, centroid x, I about y (bending with stress along z)."""
    A = sum(b * (x1 - x0) for b, x0, x1 in rects)
    xc = sum(b * (x1 - x0) * (x0 + x1) / 2 for b, x0, x1 in rects) / A
    I = sum(b * (x1 - x0) ** 3 / 12 + b * (x1 - x0) * ((x0 + x1) / 2 - xc) ** 2 for b, x0, x1 in rects)
    return A, xc, I


BULK = (2 * C.HALF_Y, XB0, C.X_B)
RIBS = (2 * P.RIB_W, XB0 - P.RIB_D, XB0)
BLOCK = (2 * C.HALF_Y, C.RAIL_X0, C.RAIL_X1)
A_br, xc_br, I_br = section([BULK, RIBS])               # bulkhead + ribs
A_br -= A_rel                                          # (the relief's 3.85 mm2 near the centroid: area only)
A_bb, xc_bb, I_bb = section([BULK, RIBS, BLOCK])        # with the rail block (z 6..17.75)
X_RIB_BACK = XB0 - P.RIB_D                              # -6.5
M_root_tug = F_TUG * (PLUG[1] - Z_ROOT)
M_block_tug = F_TUG * (PLUG[1] - Z_BLOCK)
case_tug = f"USB tug {F_TUG:.0f} N along x at the plug"
row(f"{case_tug} (+x): rib roots on the pad (z {Z_ROOT}), rail block ignored", f"bulkhead + 2 ribs {P.RIB_W:.0f} x "
    f"{P.RIB_D:.0f}: A {A_br:.0f}, I {I_br:.0f}, centroid x {xc_br:.2f}; rib back x {X_RIB_BACK}, sharp Kt {KT_SHARP}", "Z",
    KT_SHARP * M_root_tug * (xc_br - X_RIB_BACK) / I_br, ALLOW_Z, SF_SHORT)
row(f"{case_tug} (+x): rib roots on the pad (z {Z_ROOT}), as built (the rail block is in the section)",
    f"+ block 64 x {RAIL_D:.2f}: A {A_bb:.0f} (probed 1373), I {I_bb:.0f}, centroid x {xc_bb:.2f}; Kt {KT_SHARP}", "Z",
    KT_SHARP * M_root_tug * (xc_bb - X_RIB_BACK) / I_bb, ALLOW_Z, SF_SHORT)
row(f"{case_tug} (+x): pad / bulkhead r {P.BACK_FILLET} fillet (z {Z_ROOT}, x {XB0}), rail block ignored",
    f"bulkhead + ribs, Kt {KT_R15} (r/h 0.23)", "Z", KT_R15 * M_root_tug * abs(xc_br - XB0) / I_br, ALLOW_Z, SF_SHORT)
row(f"{case_tug} (+x): washer relief's foot (z {Z_ROOT}, x {R_REL:.1f}), sharp, rail block ignored",
    f"bulkhead + ribs, Kt {KT_SHARP}", "Z", KT_SHARP * M_root_tug * abs(xc_br - R_REL) / I_br, ALLOW_Z, SF_SHORT)
row(f"{case_tug} (-x): rail block's top meets the bulkhead's front face (z {Z_BLOCK}, sharp)",
    f"bulkhead + ribs above the block, front face x {C.X_B}, Kt {KT_SHARP}", "Z",
    KT_SHARP * M_block_tug * (C.X_B - xc_br) / I_br, ALLOW_Z, SF_SHORT)
# above the block the ribs run on smooth; the port off-centre twists the bulkhead (450 N.mm about z), which the ribs take
# as opposite bending (restrained warping): flange force T / d over L_c tanh(L / L_c) (Vlasov, open section)
d_ribs = 2 * C.HALF_Y - P.RIB_W                          # 58: rib centre to rib centre
Iy_fl = P.RIB_W * (C.X_B - X_RIB_BACK) ** 3 / 12         # a rib with the bulkhead behind it as one flange, 6 x 16.5
Cw = Iy_fl * d_ribs ** 2 / 2
J = (2 * C.HALF_Y * C.BULK_T ** 3 + 2 * P.RIB_W * P.RIB_D ** 3) / 3
L_c = math.sqrt(Cw / (J / 2.6))                          # G = E / 2.6
L_tw = C.Z_TOP0 - Z_BLOCK
M_fl = F_TUG * Y_PORT * L_c / d_ribs * math.tanh(L_tw / L_c)
Z_fl = P.RIB_W * (C.X_B - X_RIB_BACK) ** 2 / 6
row(f"{case_tug} (+x), port at y +-{Y_PORT:.0f}: rib back above the block (z {Z_BLOCK}), bending + the twist's warping",
    f"global {M_block_tug:.0f} N.mm on bulkhead + ribs, + rib flange {M_fl:.0f} N.mm (L_c {L_c:.0f}), Kt 1 (smooth)", "Z",
    M_block_tug * (xc_br - X_RIB_BACK) / I_br + M_fl / Z_fl, ALLOW_Z, SF_SHORT)
M_root_w = 3 * CAM_G * G * (CAM_CG[1] - Z_ROOT)
row(f"camera package {CAM_G:.0f} g x3 along x (cyclic): rib roots, rail block ignored", "as above", "Z",
    KT_SHARP * M_root_w * (xc_br - X_RIB_BACK) / I_br, ALLOW_Z, SF_CYCLIC)

# the bulkhead's moment reaches the horn through the plate + bulkhead + block, as torsion about y along the frame's
# width (the ribs deliver it at y +-29): open-section J of plate 42.85 x 6, bulkhead 40 x 6.5 and the block (solid)
J_t = (C.X_F0 - C.X_REAR) * C.T_W ** 3 / 3 + (C.Z_TOP0 - Z_ROOT) * C.BULK_T ** 3 / 3 + 0.141 * RAIL_D * RAIL_H ** 3
row(f"new path: {case_tug}: the ribs' moment carried to the horn as torsion of plate + bulkhead + block (half each side)",
    f"J {J_t:.0f} mm4, plate 6 thick", "Z shear", (M_root_tug / 2) * C.T_W / J_t, SHEAR_Z, SF_SHORT)

# window-side strips under a tug along x at a port off the centre: the two top screws share F_x and the twist
ce = P.END_CLR + P.HOLE_COMP
y_w0 = -(S.length - S.shaft_from_end) - ce / 2          # -17.1
y_w1 = y_w0 + S.length + ce                             # 6.1
relief = (P.RELIEF_D + P.HOLE_COMP) / 2
b_neg = (y_w0 - relief) - (-C.HALF_Y)
b_pos = C.HALF_Y - (y_w1 + relief)
(ys1, ys2) = (C.TOP_SCREWS[0][1], C.TOP_SCREWS[1][1])


def screw_x_forces(Fx, y_load):
    F1_ = Fx * (ys2 - y_load) / (ys2 - ys1)
    return F1_, Fx - F1_


lever_top = C.Z_TOP0 - Z_WIN0
share_neg = b_neg / (b_neg + b_pos)


def strip_Z(b, rib=None):
    rects = [(b, C.X_B - C.BULK_T, C.X_B)]
    if rib:
        rects.append((rib[0], C.X_B - C.BULK_T - rib[1], C.X_B - C.BULK_T))
    A, xc, I = section(rects)
    c = max(xc - min(x0 for _, x0, _ in rects), max(x1 for _, _, x1 in rects) - xc)
    return I / c


RIB = (P.RIB_W, P.RIB_D)


def strip_rows(case, Fx, y_load, z_load, req, rows=ROWS, rib=RIB):
    f1, f2 = screw_x_forces(Fx, y_load)
    out = []
    for name, f, b, sh in (("-y strip", f1, b_neg, share_neg), ("+y strip", f2, b_pos, 1 - share_neg)):
        M = abs(f) * lever_top + sh * abs(Fx) * (z_load - C.Z_TOP0)
        out.append(row(f"{case}: {name} + its rib", f"{b:.1f} x {C.BULK_T} + rib {rib[0]:.0f} x {rib[1]:.0f} at the window's "
                       f"lower corner (Ø3 relief, Kt {KT_FILLET}), screw force {f:+.1f} N", "Z",
                       KT_FILLET * M / strip_Z(b, rib), ALLOW_Z, req, rows))
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
D_SCREW = 2.0
R_I = S.screw_pilot_d / 2
L_ENG = 8.0 - S.tab_t
F_SNUG = 100.0
T_FORM = 40.0
MU = 0.25
p_form = 2 * T_FORM / (MU * math.pi * D_SCREW ** 2 * L_ENG)
p_clamp = F_SNUG * math.tan(math.radians(30)) / (math.pi * D_SCREW * L_ENG)
USER = []
F_t = T_STALL / (pilot_lead - pilot_far)
F_po = F1 * (X_MESH - C.X_B) / (pilot_lead - pilot_far)
p_po = F_po * math.tan(math.radians(30)) / (math.pi * D_SCREW * L_ENG)
HW_WIN = (S.width + P.CLR + P.HOLE_COMP) / 2
for name, w_cad in STRIPS.items():
    w = w_cad + P.HOLE_COMP
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
    if "far" in name:
        q = F1 / ((2 * HW_WIN) * C.BULK_T)
        Mb = q * C.BULK_T * PILOT_CAD ** 2 / 12
        row(f"one jaw blocked: the case's end bears on the window's end ({F1:.1f} N): {name}",
            f"bridge over the pilot, span {PILOT_CAD}, depth {w:.2f}", "Z", 6 * Mb / (C.BULK_T * w * w), ALLOW_Z,
            SF_SHORT, USER)
row(f"claw stall reaction {T_STALL:.0f} N.mm: {F_t:.1f} N per tab screw along z (the strips lie beside this path)",
    f"pilot wall bearing Ø{S.screw_pilot_d} x {L_ENG}", "XY", F_t / (S.screw_pilot_d * L_ENG), BEARING, SF_SHORT, USER)
row(f"one jaw blocked: tab screw pull-out {F_po:.0f} N (M2, {L_ENG} engaged)", "thread shear cylinder", "Z shear",
    F_po / (math.pi * D_SCREW * L_ENG), SHEAR_Z, SF_SHORT)

# ================================================================ 5. cover screws in the frame
L_M3_CAM = 18.0 - (C.PAD_TOP - C.Z_TOP1) - C.TOP_T     # M3 x 18 through the 3.5 pad + 3 top wall: 11.5 engaged
L_M3_BARE = 10.0 - C.TOP_T                             # M3 x 10 without the camera mount: 7 engaged
M_top = F_TUG * (PLUG[1] - C.Z_TOP0)
T_m3 = M_top / (C.BULK_T / 2) / 2
row(f"USB tug {F_TUG:.0f} N along x at the plug: M3 x 18 pull-out from the bulkhead top, {T_m3:.0f} N per screw",
    f"M3, {L_M3_CAM:.1f} engaged", "Z shear", T_m3 / (math.pi * 3.0 * L_M3_CAM), SHEAR_Z, SF_SHORT)
# new path (cover strength round 3): a reversed rack-B push on the cover's upper piece (opening stall on jaw B, jaws open,
# 27 N at z 17.2) leaves the cover mostly through its top joint as built: bound = all of it, the moment R (50 - 17.2) as
# M3 tension against the bulkhead's rear edge (lever 3.25), both screws
z_rb = ((C.ZS - C.NECK_Z[0] + C.SLOT_CLR) + (C.ZS - C.RACK_TIP)) / 2
M_cov = R_grip_open * ((C.Z_TOP0 + C.Z_TOP1) / 2 - z_rb)
T_cov = M_cov / (C.BULK_T / 2) / 2
for lab, L_ in (("M3 x 10, no camera", L_M3_BARE), ("M3 x 18 with the camera mount", L_M3_CAM)):
    row(f"new path: opening stall on jaw B, jaws open ({R_grip_open:.1f} N on the cover's upper piece): the cover's "
        f"overturning moment {M_cov:.0f} N.mm on its top screws, {T_cov:.0f} N each ({lab}; the cover's anchored-post fix "
        f"removes it)", f"M3, {L_:.1f} engaged", "Z shear", T_cov / (math.pi * 3.0 * L_), SHEAR_Z, SF_SHORT)
# front M2.5 x 16 into 14 mm pilots: 11 engaged (round 3)
L_M25 = P.FRONT_PILOT_DEPTH - 3.0
z_rbg = (C.T_W + (C.ZS - C.RACK_TIP)) / 2               # 12.05: rack B's front face resultant
T_m25 = R_grip_open * z_rbg / C.FRONT_SCREWS[0][1]
row(f"stall, one jaw blocked: rack B pushes the cover's lower piece forward ({R_grip_open:.1f} N at z {z_rbg:.1f}): "
    f"M2.5 pull-out {T_m25:.0f} N (one screw)", f"M2.5 x 16, {L_M25:.0f} engaged (14 mm pilot), 1.9 mm skins", "Z shear",
    T_m25 / (math.pi * 2.5 * L_M25), SHEAR_Z, SF_SHORT)


# ---------------------------------------------------------------- report
def table(rows, start=1):
    for i, (case, sec, d, s, a, sf, req) in enumerate(rows, start):
        ok = "OK" if sf >= req else "**FAIL**"
        print(f"| {i} | {case} | {sec} | {d} | {s:.2f} | {a:.2f} | {sf:.2f} | {req:.0f} | {ok} |")


print(f"frame: plate {C.T_W} + pad {C.PAD_T} (floor {FLOOR:.1f}), bulkhead {C.BULK_T}, rail block x {C.RAIL_X0}..{C.RAIL_X1} "
      f"z {C.T_W}..{Z_BLOCK}; ribs {P.RIB_W} x {P.RIB_D}; window y {y_w0:.2f}..{y_w1:.2f}, z {Z_WIN0:.2f}..{C.ZS + HW_WIN:.2f}; "
      f"pilots y {pilot_far:.2f} / {pilot_lead:.2f}")
print(f"camera: plug exit G (x {PLUG[0]:.1f}, z {PLUG[1]:.1f}), end-face centre z {CAM_END[1]:.1f}; package {CAM_G:.0f} g; "
      f"end effector {EE_SOLID_G} g solid; overhung wrist moment {M_OVERHUNG[0]:.0f} / {M_OVERHUNG[50]:.0f} N.mm")
print(f"joint moments: tug {M_tug:.0f}, camera crash {M_camcrash:.0f}, finger crash {M_fingercrash:.0f}, yaw stall "
      f"{F_YAW_Z * C.X_TIP:.0f} (+ {F_YAW_Z:.1f} N pull), weight x3 {M_weight3:.0f}, SYS-04 x{MOVING} {M_sus:.0f} N.mm; rack "
      f"thrust open {R_grip_open:.1f} / closed {R_grip_closed:.1f} N")
print(f"washer Ø{WASHER_OD} x {C.WRIST_WASHER_T} (bore {WASHER_ID}): {A_WASHER:.1f} mm2; relief Ø{P.WASHER_RELIEF_D} CAD "
      f"(r {r_relief_pr:.2f} printed) vs washer r {WASHER_OD / 2} + play {(WASHER_ID - 2.0) / 2:.2f}: margin "
      f"{washer_margin:.2f} mm (fit, not strength)")
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

# ---------------------------------------------------------------- what-if lines
print("\nWhat-if, wrist clamp (camera hits the desk, the worst joint row):")
for od, fl in ((6.0, FLOOR), (8.0, FLOOR), (8.0, 7.0), (10.0, 7.0)):
    sf = clamp_rows("w", M_camcrash, SF_SHORT, rows=[], od=od, floor=fl)
    print(f"  washer Ø{od:.0f}, floor {fl:.1f}: lowest SF {sf:.2f}")
print("What-if, rail block depth (rack B's +y end at the block's end, one jaw blocked):")
for t in (4.0, 8.0, RAIL_D):
    print(f"  depth {t:5.2f}: SF {rail_rows('w', R_grip_open, 0.0, SF_SHORT, t=t, rows=[]):.2f}")
# the cover's required fix (cover strength.md, round 3) adds an M3 x 45 into a Ø2.7 x 14 pilot in this block's top at
# (x 18.35, y 28): the block's rack-side root with that hole in its b_eff (rack B's +y end at the block's end, jaws open)
d_h = C.M3_PILOT + P.HOLE_COMP
x_h = 18.35
b_e = PATCH + H_R
rects = [(b_e, C.RAIL_X0, C.RAIL_X1)]
A_s, xc_s, I_s = section(rects)
A_h, xc_h, I_h = section([(d_h, x_h - d_h / 2, x_h + d_h / 2)])
A_n = A_s - A_h
xc_n = (A_s * xc_s - A_h * xc_h) / A_n
I_n = I_s + A_s * (xc_s - xc_n) ** 2 - (I_h + A_h * (xc_h - xc_n) ** 2)
s_h = KT_SHARP * R_grip_open * H_R * (C.RAIL_X1 - xc_n) / I_n
print(f"What-if, the cover fix's M3 pilot (Ø{d_h:.1f} at x {x_h}, y 28) in the rail block: block root SF "
      f"{ALLOW_Z / s_h:.2f} (as built {rail_rows('w', R_grip_open, 0.0, SF_SHORT, rows=[]):.2f}); the frame's top-screw "
      f"rows under the cover's reversed push then fall away (the anchor takes ~25 of the 27 N into this block)")
print("What-if, window strips with ribs (worst of the port at -45 / +45):")
for name, rib in (("no ribs", (0.0, 0.0)), ("6 x 8 ribs", (6.0, 8.0)), ("6 x 10 ribs (as built)", RIB), ("8 x 10", (8.0, 10.0))):
    rr = rib if rib[0] else None
    sfs = [s for yp in (-Y_PORT, Y_PORT) for s in strip_rows("w", F_TUG, yp, PLUG[1], SF_SHORT, rows=[], rib=rr or (1e-6, 1e-6))]
    print(f"  {name:24s}: lowest SF {min(sfs):.2f}")

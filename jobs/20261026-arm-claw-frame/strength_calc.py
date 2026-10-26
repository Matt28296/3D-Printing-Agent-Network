"""Strength check for jobs/20261026-arm-claw-frame (claw v2 + Brio 4K, round 1). Run: python3 jobs/20261026-arm-claw-frame/strength_calc.py

strength-analyst, 2026-10-26. Plain python3 (no build123d needed): reads tools/hobby_parts.py, the shared claw layout
jobs/20261025-robot-arm-assembly/claw_frame.py and the jobs' model.py constants with ast, and masses from geometry.json.
The arm model and the yaw-stall / hand-push sweeps are the same as in the arm jobs' strength_calc.py (round 4), so the
fingertip forces here match the ones the arm links were checked for. Section properties are computed from the
parameters; the build123d sections they were cross-checked against (2026-10-26) are printed next to them.
"""
import math

# --- allowables -------------------------------------------------------------------
ALLOW_INPLANE_MPA = 25.0   # source: placeholder PETG (library/materials.csv has no measured row) -> verdict at best NEEDS_TEST
Z_RATIO = 0.5              # across-layer / in-plane; placeholder (skill: half the in-plane value)
SHEAR_RATIO = 0.5          # shear allowable = 0.5 x normal allowable (Tresca); assumption, stated in strength.md
SF_STATIC = 3.0            # short-term static
SF_SUSTAINED = 4.0         # sustained (creep) or cyclic
DYN = 2.0                  # dynamic factor on self-weight while the arm moves (as the spec uses)
G_N_PER_G = 9.81e-3        # N per gram
RHO_G_PER_MM3 = 1.27e-3    # PETG density

cases = []      # rows that set the verdict
advisory = []   # rows printed for information only (reason given in strength.md)


def allow_mpa(across, shear=False):
    a = ALLOW_INPLANE_MPA * (Z_RATIO if across else 1.0)
    return a * (SHEAR_RATIO if shear else 1.0)


def check(name, stress_mpa, across, sf_req, shear=False, Kt=1.0, info=False):
    """Record one check. across=True: the stress pulls layers apart (or shears them)."""
    s = Kt * stress_mpa
    a = allow_mpa(across, shear)
    sf = a / s if s > 1e-9 else float("inf")
    tag = ("Z" if across else "XY") + (" shear" if shear else "")
    (advisory if info else cases).append((name, tag, s, a, sf, sf_req))
    return sf


def bend(M_nmm, I_mm4, c_mm):
    return M_nmm * c_mm / I_mm4


def bearing(F_n, d_mm, t_mm):
    return F_n / (d_mm * t_mm)


def tearout(F_n, ligament_mm, t_mm):
    """Shear-out on two planes; ligament = edge distance minus hole radius."""
    return F_n / (2.0 * ligament_mm * t_mm)


def pullout(F_n, d_mm, L_mm):
    """Thread strip / pull-out of a self-tapping screw: shear on the pilot cylinder."""
    return F_n / (math.pi * d_mm * L_mm)


def torsion_thin(T_nmm, rects):
    """Open thin-walled section: J = sum b t^3/3 (1 - 0.63 t/b); tau_max = T t_max / J."""
    J = sum(b * t ** 3 / 3.0 * (1 - 0.63 * t / b) for b, t in rects)
    return T_nmm * max(t for _, t in rects) / J


def comp_section(rects):
    """rects: (width b along the neutral axis, depth d, centroid position y). Returns (A, ybar, I)."""
    A = sum(b * d for b, d, _ in rects)
    ybar = sum(b * d * y for b, d, y in rects) / A
    I = sum(b * d ** 3 / 12.0 + b * d * (y - ybar) ** 2 for b, d, y in rects)
    return A, ybar, I


def servo_screw_forces(T_nmm, holes):
    """Torque reacted by screws only (servo body bearing on the window ignored): F_i = T r_i / sum r^2."""
    r = [math.hypot(x, y) for x, y in holes]
    s = sum(ri ** 2 for ri in r)
    return [T_nmm * ri / s for ri in r]


def report(title):
    print(f"== {title} ==")
    print("| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |")
    print("|---|---|---|---|---|---|---|---|")
    for i, (n, d, s, a, sf, req) in enumerate(cases, 1):
        print(f"| {i} | {n} | {d} | {s:.2f} | {a:.2f} | {sf:.2f} | {req:.0f} | {'OK' if sf >= req else '**FAIL**'} |")
    if advisory:
        print("\nAdvisory (not in the verdict; see strength.md):")
        print("| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |")
        print("|---|---|---|---|---|---|")
        for n, d, s, a, sf, req in advisory:
            print(f"| {n} | {d} | {s:.2f} | {a:.2f} | {sf:.2f} | {req:.0f} |")
    worst = min(cases, key=lambda r: r[4] / r[5])
    fails = [r for r in cases if r[4] < r[5]]
    print(f"\nlowest SF {worst[4]:.2f} (required {worst[5]:.0f}) at: {worst[0]}")
    print("VERDICT:", "FAIL" if fails else "NEEDS_TEST (placeholder allowables; PASS not possible without measured data)")
    return worst, fails

# --- read the real parameters (model.py / tools/hobby_parts.py / geometry.json) ---------------------------
# model.py imports build123d, which plain python3 doesn't have, so its top-level constants are evaluated with
# ast against stand-ins for the hobby_parts names. Anything that can't be evaluated that way is skipped.
import ast
import json
import os
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
JOBS = os.path.join(ROOT, "jobs")
_SERVO_FIELDS = ["name", "length", "width", "case_top", "total_h", "tab_height", "tab_t", "tab_span", "hole_dx",
                 "hole_dy", "tab_hole_d", "screw_pilot_d", "shaft_from_end", "horn_kind", "horn_d", "horn_t"]
_SERVO_DEFAULTS = dict(horn_arm_len=0.0, horn_tip_d=0.0, horn_arms=1, horn_screw_clear_d=3.4, stall_torque_nmm=0.0,
                       mass_g=0.0)
_BOARD_FIELDS = ["name", "length", "width", "pcb_t", "pins_below", "parts_above", "usb_w", "usb_h"]
_BOX_FIELDS = ["name", "length", "width", "height", "mass_g", "note"]


def _lit(node):
    return ast.literal_eval(node)


def _read_hobby():
    tree = ast.parse(open(os.path.join(ROOT, "tools", "hobby_parts.py")).read())
    ns = {}
    for node in tree.body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)):
            continue
        name, v = node.targets[0].id, node.value
        fn = getattr(getattr(v, "func", None), "id", "")
        if fn == "ServoSpec":
            d = dict(_SERVO_DEFAULTS)
            d.update(zip(_SERVO_FIELDS, [_lit(a) for a in v.args]))
            d.update({kw.arg: _lit(kw.value) for kw in v.keywords})
            ns[name] = SimpleNamespace(**d)
        elif fn == "BoardSpec":
            ns[name] = SimpleNamespace(**dict(zip(_BOARD_FIELDS, [_lit(a) for a in v.args])))
        elif fn == "BoxSpec":
            d = dict(zip(_BOX_FIELDS, [_lit(a) for a in v.args]))
            d.update({kw.arg: _lit(kw.value) for kw in v.keywords})
            ns[name] = SimpleNamespace(**d)
        elif fn == "replace":
            d = dict(vars(ns[v.args[0].id]))
            d.update({kw.arg: _lit(kw.value) for kw in v.keywords})
            ns[name] = SimpleNamespace(**d)
        else:
            try:
                ns[name] = _lit(v)
            except Exception:
                pass
    cad = ast.parse(open(os.path.join(ROOT, "tools", "cadlib.py")).read())
    for node in cad.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "HOLE_COMP_DEFAULT":
            ns["HOLE_COMP_DEFAULT"] = _lit(node.value)
    return ns


HOBBY = _read_hobby()
MG996R, SG90 = HOBBY["MG996R"], HOBBY["SG90"]
HORN_DEPTH = HOBBY.get("HORN_DEPTH", 2.0)


def horn_face_z(s):
    return (s.total_h - s.tab_height) + 0.6          # same formula as tools/hobby_parts.py


def link_back_z(s, depth=HORN_DEPTH):
    return horn_face_z(s) - depth


def model_params(job):
    """Top-level constants of jobs/<job>/model.py, evaluated in order."""
    ns = dict(HOBBY, math=math, horn_face_z=horn_face_z, link_back_z=link_back_z, max=max, min=min, abs=abs)
    base = set(ns)
    tree = ast.parse(open(os.path.join(JOBS, job, "model.py")).read())
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        try:
            val = eval(compile(ast.Expression(node.value), "model.py", "eval"), ns)
        except Exception:
            continue
        t = node.targets[0]
        if isinstance(t, ast.Name):
            ns[t.id] = val
        elif isinstance(t, ast.Tuple) and all(isinstance(e, ast.Name) for e in t.elts):
            for e, v in zip(t.elts, val):
                ns[e.id] = v
    return SimpleNamespace(**{k: v for k, v in ns.items() if k not in base and not k.startswith("__")})


def volume_mm3(job):
    return json.load(open(os.path.join(JOBS, job, "geometry.json")))["volume_mm3"]


HOLE_COMP = HOBBY["HOLE_COMP_DEFAULT"]

# --- arm model, built from the jobs' model.py / geometry.json (assembly_plan.md frames) -------------------
# Round 4 (claw v2 + Brio, 2026-10-26): the end effector beyond the wrist horn is the rack-and-pinion claw (jobs
# 20261026-arm-claw-frame, -claw-cover, -claw-pinion, -claw-jaw x2) carrying the optional Brio 4K on
# 20261026-arm-camera-mount, and the wrist servo is an MG90S (SG90 body and horn, 216 N.mm stall, 13.4 g).
# Masses: each claw job's geometry.json volume x 1.27 g/cm3. Fingertip lever and camera pose: the shared layout
# jobs/20261025-robot-arm-assembly/claw_frame.py. Part centres of mass: build123d centre of mass of each design() in
# the claw frame G (measured 2026-10-26; the script warns if a part's volume has changed since).
def claw_frame_params():
    """Top-level constants of the shared claw layout (claw_frame.py), evaluated like model.py."""
    ns = dict(HOBBY, math=math, horn_face_z=horn_face_z, link_back_z=link_back_z, max=max, min=min, abs=abs)
    base = set(ns)
    tree = ast.parse(open(os.path.join(JOBS, "20261025-robot-arm-assembly", "claw_frame.py")).read())
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        try:
            val = eval(compile(ast.Expression(node.value), "claw_frame.py", "eval"), ns)
        except Exception:
            continue
        t = node.targets[0]
        if isinstance(t, ast.Name):
            ns[t.id] = val
        elif isinstance(t, ast.Tuple) and all(isinstance(e, ast.Name) for e in t.elts):
            for e, v in zip(t.elts, val):
                ns[e.id] = v
    return SimpleNamespace(**{k: v for k, v in ns.items() if k not in base and not k.startswith("__")})


UL = model_params("20261025-arm-upper-link")
FA = model_params("20261025-arm-forearm")
TT = model_params("20261025-arm-turntable")
CF = claw_frame_params()
MG90S, BRIO = HOBBY["MG90S"], HOBBY["BRIO_4K"]
WRIST = MG90S                           # wrist servo: MG90S (same body and horn as the SG90 the forearm is drawn for)
STALL_MG996R_NMM, STALL_SG90_NMM = MG996R.stall_torque_nmm, SG90.stall_torque_nmm
STALL_WRIST_NMM = WRIST.stall_torque_nmm
L1, L2 = UL.L, FA.L                     # shoulder->elbow, elbow->wrist
GRIP_DX, L3 = CF.X_P0, CF.X_TIP         # wrist -> claw-servo output (pinion back face), wrist -> fingertip (was 40 / 95)
SX, SZ = TT.XS, TT.ZS                   # shoulder axis X, Z
DESK_Z = -40.0
F_HAND_N = 5.0                          # handling case (spec 4): hand push out of the arm plane at the fingertip
CAMERA = True                           # optional Brio 4K fitted (the heavier case governs)
PAYLOAD_G = 50.0
HFZ_MG, HFZ_SG = horn_face_z(MG996R), horn_face_z(WRIST)
# world-Y stack: each link's back face sits HORN_DEPTH below the horn face; the next servo's tabs sit on its front face
Y_SH_HORN = TT.UP_Y + HFZ_MG
Y_UL_BACK = Y_SH_HORN - HORN_DEPTH
Y_EL_TAB = Y_UL_BACK + UL.T
Y_EL_HORN = Y_EL_TAB + HFZ_MG
Y_FA_BACK = Y_EL_HORN - HORN_DEPTH
Y_WR_TAB = Y_FA_BACK + FA.T
Y_WR_HORN = Y_WR_TAB + HFZ_SG
Y_CLAW = Y_WR_HORN - HORN_DEPTH        # claw frame back face (claw z = 0); claw +z = world +Y, claw +x = along the arm
Y_TIP = Y_CLAW + CF.ZS                  # fingertips and payload on the pinion-axis line
Y_HORN = {"shoulder": Y_SH_HORN, "elbow": Y_EL_HORN, "wrist": Y_WR_HORN, "gripper": Y_TIP}


def _servo_body(s):
    """Body-centre offsets in the servo frame: x along the body, z (case centre below the tab underside)."""
    return -(s.length - s.shaft_from_end) + s.length / 2, s.case_top / 2 - s.tab_height


def _plate_cg_x(x0, x1, w, win_x, win_a):
    a = (x1 - x0) * w
    return (a * (x0 + x1) / 2 - win_a * win_x) / (a - win_a)


_mx, _mz = _servo_body(MG996R)
_sx, _sz = _servo_body(WRIST)
M_UL, M_FA = volume_mm3("20261025-arm-upper-link") * RHO_G_PER_MM3, volume_mm3("20261025-arm-forearm") * RHO_G_PER_MM3
M_TT = volume_mm3("20261025-arm-turntable") * RHO_G_PER_MM3
CG_UL = _plate_cg_x(UL.X0, UL.X1, 2 * UL.HALF_W, UL.L + _mx, MG996R.length * MG996R.width)
CG_FA = _plate_cg_x(FA.X0, FA.X1, 2 * FA.HALF_W, FA.L + _sx, WRIST.length * WRIST.width)
# claw parts: (job, copies, volume when the CoG was measured, CoG (x, z) in claw frame G, joint index)
CLAW_PARTS = [("20261026-arm-claw-frame", 1, 24422.2, (10.96, 12.01), 3),
              ("20261026-arm-claw-cover", 1, 15434.92, (21.46, 30.47), 3),
              ("20261026-arm-claw-pinion", 1, 1765.53, (CF.X_P0 + 4.21, CF.ZS), 4),
              ("20261026-arm-claw-jaw", 2, 6898.26, (42.64, CF.ZS), 4),        # pair: jaw B = jaw A turned about the axis
              ("20261026-arm-camera-mount", 1, 8846.95, (-8.37, 50.73), 3)]
_ta = math.radians(CF.CAM_TILT)
CAM_CG = (CF.CAM_XC + BRIO.height / 2 * math.sin(_ta), CF.CAM_ZC + BRIO.height / 2 * math.cos(_ta))  # Brio box centre
SCREW14_CG = (CF.CAM_XC - (CF.SEAT_T + 4.0) * math.sin(_ta), CF.CAM_ZC - (CF.SEAT_T + 4.0) * math.cos(_ta))
_cx, _cz = _servo_body(MG90S)
CLAW_SERVO_CG = (CF.X_B + _cz, CF.ZS)  # claw MG90S: shaft along claw +x, case centre 4.55 behind the bulkhead face
EE = []                                 # (name, mass g, joint index, x from the wrist axis, claw z)
for job, n, v0, (x, z), k in CLAW_PARTS:
    if job == "20261026-arm-camera-mount" and not CAMERA:
        continue
    v = volume_mm3(job)
    if abs(v - v0) > 0.005 * v0:
        print(f"WARNING: {job} volume {v:.0f} differs from {v0:.0f} mm3 when its CoG was measured: re-measure the CoG")
    EE.append((job.split("arm-")[1], n * v * RHO_G_PER_MM3, k, x, z))
EE += [("claw MG90S", MG90S.mass_g, 3, CLAW_SERVO_CG[0], CLAW_SERVO_CG[1]),
       ("pinion horn (cut) + M2x10 clamp", 2.0, 4, CF.X_P0 + 1.0, CF.ZS),
       ("cover / tab screws", 6.0, 3, 14.0, 25.0)]   # 2 x M3x18 at x 7, 2 x M3x12 at the front, 2 x M2x8
if CAMERA:
    EE += [("Brio 4K", BRIO.mass_g, 3, CAM_CG[0], CAM_CG[1]), ("1/4-20 thumb screw", 4.0, 3, SCREW14_CG[0], SCREW14_CG[1])]
M_EE = sum(m for _, m, _, _, _ in EE)
X_EE = sum(m * x for _, m, _, x, _ in EE) / M_EE
Z_EE = sum(m * z for _, m, _, _, z in EE) / M_EE
# (name, mass g, rides beyond joint k: 0 yaw, 1 shoulder, 2 elbow, 3 wrist, 4 claw servo, s along the straight arm, world Y)
ITEMS = [
    ("shoulder MG996R", MG996R.mass_g, 0, -SX, TT.UP_Y + _mz),
    ("shoulder horn + clamp screw", 5.0, 1, 0.0, Y_SH_HORN - 1.4),
    ("upper link", M_UL, 1, CG_UL, Y_UL_BACK + UL.T / 2),
    ("elbow MG996R", MG996R.mass_g, 1, L1 + _mx, Y_EL_TAB + _mz),
    ("cable allowance 1", 6.0, 1, L1, Y_EL_TAB),
    ("elbow horn + clamp screw", 5.0, 2, L1, Y_EL_HORN - 1.4),
    ("forearm", M_FA, 2, L1 + CG_FA, Y_FA_BACK + FA.T / 2),
    ("wrist MG90S", WRIST.mass_g, 2, L1 + L2 + _sx, Y_WR_TAB + _sz),
    ("cable allowance 2", 4.0, 2, L1 + L2, Y_WR_TAB),
    ("wrist horn + clamp screw", 2.0, 3, L1 + L2, Y_WR_HORN - 0.8),
] + [(n, m, k, L1 + L2 + x, Y_CLAW + z) for n, m, k, x, z in EE] + [
    ("payload", PAYLOAD_G, 4, L1 + L2 + L3, Y_TIP),
]
S_JOINT = {0: -SX, 1: 0.0, 2: L1, 3: L1 + L2, 4: L1 + L2 + GRIP_DX}
print(f"arm model: Y horn faces {', '.join(f'{k} {v:.1f}' for k, v in Y_HORN.items() if k != 'gripper')}; claw back face "
      f"Y {Y_CLAW:.1f}, fingertip {L3:.2f} from the wrist at Y {Y_TIP:.1f}; masses UL {M_UL:.1f} FA {M_FA:.1f} "
      f"TT {M_TT:.1f} g; CG x UL {CG_UL:.1f} FA {CG_FA:.1f}")
print(f"end effector beyond the wrist horn ({'with' if CAMERA else 'without'} the Brio): {M_EE + 2.0:.1f} g incl. the wrist "
      f"horn, CoG {X_EE:.1f} in front of the wrist axis, {Z_EE:.1f} outboard of the claw back face (Y {Y_CLAW + Z_EE:.1f}); "
      f"Brio CoG x {CAM_CG[0]:.2f}, z {CAM_CG[1]:.2f} (Y {Y_CLAW + CAM_CG[1]:.1f}); payload {PAYLOAD_G:.0f} g at the fingertip")


def beyond(k):
    return [it for it in ITEMS if it[2] >= k]


def weight_inplane_nmm(k, s_ref=None):
    """Static moment of everything beyond joint k about an axis at s_ref (default the joint), arm straight and horizontal."""
    s0 = S_JOINT[k] if s_ref is None else s_ref
    return sum(m * G_N_PER_G * (s - s0) for _, m, _, s, _ in beyond(k))


def weight_oop_nmm(k, y_ref):
    """Out-of-plane moment (about world X) of the weight beyond joint k about the plane Y = y_ref; pose independent."""
    return sum(m * G_N_PER_G * (y - y_ref) for _, m, _, _, y in beyond(k))


def weight_n(k):
    return sum(m for _, m, _, _, _ in beyond(k)) * G_N_PER_G


def _pose(q1, q2, q3):
    t1 = math.radians(q1); t2 = t1 + math.radians(q2); t3 = t2 + math.radians(q3)
    S = (SX, Y_HORN["shoulder"], SZ)
    E = (S[0] + L1 * math.cos(t1), Y_HORN["elbow"], S[2] + L1 * math.sin(t1))
    W = (E[0] + L2 * math.cos(t2), Y_HORN["wrist"], E[2] + L2 * math.sin(t2))
    G = (W[0] + GRIP_DX * math.cos(t3), Y_HORN["gripper"], W[2] + GRIP_DX * math.sin(t3))
    P = (W[0] + L3 * math.cos(t3), Y_TIP, W[2] + L3 * math.sin(t3))
    return S, E, W, G, P, (t1, t2, t3)


def _moment(P, J, F):
    r = (P[0] - J[0], P[1] - J[1], P[2] - J[2])
    return (r[1] * F[2] - r[2] * F[1], r[2] * F[0] - r[0] * F[2], r[0] * F[1] - r[1] * F[0])


def sweep(points, mode):
    """Worst moments over the servo ranges (shoulder 0..180, elbow -90..90, wrist -90..90, 5 deg steps, joints above the desk).

    mode "yaw":  base-yaw servo stalls with the fingertip against a side obstacle: F = 1000/R, tangential (horizontal);
                 scaled down where a pitch servo (shoulder/elbow 1000, wrist MG90S 216) would backdrive first.
    mode "hand": F_HAND_N at the fingertip along +-Y (out of the arm plane); capped where the yaw servo would backdrive.
    points: {name: (where, link_angle_index or None, (lever_t, lever_T_per_screw) or None)}; where = a joint name
    "S"/"E"/"W"/"G", a fixed (x, y, z), or (joint, distance along the link, dY); "Fs" = worst horn-screw
    tension in the same pose, Mt/lever_t + T/lever_T. Returns {name: dict of max |M| components}.
    For a horn joint (index 0/1/2 = upper link/forearm/gripper), T = torsion about the link axis, Mt = transverse
    out-of-plane bending; for fixed points (None) Mx, My, Mz are world components.
    """
    out = {n: {"T": 0.0, "Mt": 0.0, "Mx": 0.0, "My": 0.0, "Mz": 0.0, "F": 0.0, "Fs": 0.0, "pose": None} for n in points}
    for q1 in range(0, 181, 5):
        for q2 in range(-90, 91, 5):
            for q3 in range(-90, 91, 5):
                S, E, W, G, P, th = _pose(q1, q2, q3)
                if min(E[2], W[2], G[2], P[2]) < DESK_Z:
                    continue
                if mode == "yaw":
                    R = math.hypot(P[0], P[1])
                    f = STALL_MG996R_NMM / R
                    F = (-P[1] / R * f, P[0] / R * f, 0.0)
                    s = 1.0
                    for J, st in ((S, STALL_MG996R_NMM), (E, STALL_MG996R_NMM), (W, STALL_WRIST_NMM)):
                        my = abs(_moment(P, J, F)[1])
                        if my > st:
                            s = min(s, st / my)
                    F = tuple(c * s for c in F)
                else:
                    f = F_HAND_N
                    if abs(P[0]) * f > STALL_MG996R_NMM:
                        f = STALL_MG996R_NMM / abs(P[0])
                    F = (0.0, f, 0.0)
                pts = {"S": S, "E": E, "W": W, "G": G}
                for n, (xyz, li, lev) in points.items():
                    if isinstance(xyz, str):
                        J = pts[xyz]
                    elif isinstance(xyz[0], str):          # (joint, distance along link li, Y offset)
                        J0 = pts[xyz[0]]; t = th[li]
                        J = (J0[0] + xyz[1] * math.cos(t), J0[1] + xyz[2], J0[2] + xyz[1] * math.sin(t))
                    else:
                        J = xyz
                    M = _moment(P, J, F)
                    o = out[n]
                    if li is not None:
                        t = th[li]
                        T = abs(M[0] * math.cos(t) + M[2] * math.sin(t))
                        Mt = abs(-M[0] * math.sin(t) + M[2] * math.cos(t))
                        if T > o["T"]: o["T"] = T
                        if Mt > o["Mt"]: o["Mt"] = Mt
                        if lev:
                            fs = Mt / lev[0] + T / lev[1]
                            if fs > o["Fs"]: o["Fs"] = fs
                    for k, v in (("Mx", abs(M[0])), ("My", abs(M[1])), ("Mz", abs(M[2]))):
                        if v > o[k]:
                            o[k] = v
                            if k == "Mx": o["pose"] = (q1, q2, q3)
                    o["F"] = max(o["F"], math.sqrt(sum(c * c for c in F)))
    return out


# --- clamped horn joints (round 2): centre screw + washer clamps link and horn onto the spline -------------
HS_D, HS_LEN = 1.6, 5.0       # anti-rotation screws through the horn arms: M2 self-tapping, drilled pilot 1.6,
                              # ~5 mm engaged (M2x8 through the 2.8 mm horn) - assumption
HS_R = {"MG996R": 15.0, "SG90": 7.0}       # arm hole used (outermost on the MG996R double arm, inner on the SG90)
WASHER_D = {"MG996R": 9.0, "SG90": 6.0}    # DIN 9021 washers specified for M3x16 / M2x12 clamp screws


def clamp_caps(kind, t_floor):
    """Allowable moments of a clamped horn joint (washer pull-through over the floor + arm screws, interlayer shear).

    cap_t: transverse (about the link's y axis, along the horn arms); cap_T: torsion (about the arm axis, pivot on the
    hub edge). The two paths are summed (PETG is ductile; both are bounded by the same allowable)."""
    s = MG996R if kind == "MG996R" else SG90
    a = allow_mpa(True, True)
    wash = math.pi * WASHER_D[kind] * t_floor
    arm = math.pi * HS_D * min(t_floor, HS_LEN)
    hub, arm_l, r = s.horn_d / 2, s.horn_arm_len, HS_R[kind]
    if s.horn_arms == 2:
        cap_T = a * (wash + 2 * arm) * hub
        cap_t = a * (wash * arm_l + arm * (r + arm_l))
    else:   # single arm: weak direction pivots on the hub's far edge, the other on the arm tip
        cap_T = a * (wash + arm) * hub
        cap_t = min(a * (wash * hub + arm * (r + hub)), a * (wash * arm_l + arm * (arm_l - r)))
    return cap_t, cap_T


def check_util(name, u, sf_req, info=False):
    """Record a utilisation-type check (u = demand / allowable capacity) as an equivalent interlayer shear stress."""
    return check(name, allow_mpa(True, True) * u, True, sf_req, shear=True, info=info)


def pocket_half_w(s, x):
    """Half width of the horn pocket at distance x along the arm (hull of discs, +0.5 clearance + HOLE_COMP)."""
    c = 0.5 + HOLE_COMP
    rh, rt = (s.horn_d + c) / 2, (s.horn_tip_d + c) / 2
    x = abs(x)
    if x <= s.horn_arm_len:
        return rh - (rh - rt) * x / s.horn_arm_len
    return math.sqrt(max(rt ** 2 - (x - s.horn_arm_len) ** 2, 0.0))


# --- claw helpers (claw v2, 2026-10-26) ---------------------------------------------------------------
def claw_model_params(job):
    """Top-level constants of a claw job's model.py, with the claw_frame.py names in scope."""
    ns = dict(HOBBY, math=math, horn_face_z=horn_face_z, link_back_z=link_back_z, max=max, min=min, abs=abs)
    ns.update(vars(CF))
    mine = set()                           # names assigned in model.py (some shadow claw_frame.py names, e.g. CLR)
    tree = ast.parse(open(os.path.join(JOBS, job, "model.py")).read())
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        try:
            val = eval(compile(ast.Expression(node.value), "model.py", "eval"), ns)
        except Exception:
            continue
        t = node.targets[0]
        if isinstance(t, ast.Name):
            ns[t.id] = val
            mine.add(t.id)
        elif isinstance(t, ast.Tuple) and all(isinstance(e, ast.Name) for e in t.elts):
            for e, v in zip(t.elts, val):
                ns[e.id] = v
                mine.add(e.id)
    return SimpleNamespace(**{k: ns[k] for k in mine})


def tip_forces(mode):
    """Fingertip force in CLAW axes (Fx along the fingers, Fy along the jaw travel, Fz outboard = world +Y) for every
    pose of sweep(), with the same force model: yaw stall F = 1000/R tangential, capped where a pitch servo backdrives;
    hand push F_HAND_N along world Y, capped where the yaw servo backdrives. Rounded and de-duplicated."""
    out = set()
    for q1 in range(0, 181, 5):
        for q2 in range(-90, 91, 5):
            for q3 in range(-90, 91, 5):
                S, E, W, G, P, th = _pose(q1, q2, q3)
                if min(E[2], W[2], G[2], P[2]) < DESK_Z:
                    continue
                if mode == "yaw":
                    R = math.hypot(P[0], P[1])
                    f = STALL_MG996R_NMM / R
                    F = (-P[1] / R * f, P[0] / R * f, 0.0)
                    s = 1.0
                    for J, st in ((S, STALL_MG996R_NMM), (E, STALL_MG996R_NMM), (W, STALL_WRIST_NMM)):
                        my = abs(_moment(P, J, F)[1])
                        if my > st:
                            s = min(s, st / my)
                    F = tuple(c * s for c in F)
                else:
                    f = F_HAND_N
                    if abs(P[0]) * f > STALL_MG996R_NMM:
                        f = STALL_MG996R_NMM / abs(P[0])
                    F = (0.0, f, 0.0)
                t3 = th[2]
                fx = F[0] * math.cos(t3) + F[2] * math.sin(t3)
                fy = F[0] * math.sin(t3) - F[2] * math.cos(t3)
                out.add((round(fx, 2), round(fy, 2), round(F[1], 2)))
    return sorted(out)


def unit_dirs(step_deg=3):
    """Unit vectors covering the sphere (for 'any direction' loads such as the USB-cable tug)."""
    out = []
    for i in range(0, 181, step_deg):
        th = math.radians(i)
        n = max(1, int(round(360 / step_deg * math.sin(th))))
        for j in range(n):
            ph = 2 * math.pi * j / n
            out.append((math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)))
    return out


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def rect_section(rects):
    """rects: (y0, y1, z0, z1) rectangles in a section plane. Returns A, ybar, zbar, Iyy=int z^2, Izz=int y^2, Iyz."""
    A = sum((y1 - y0) * (z1 - z0) for y0, y1, z0, z1 in rects)
    yb = sum((y1 - y0) * (z1 - z0) * (y0 + y1) / 2 for y0, y1, z0, z1 in rects) / A
    zb = sum((y1 - y0) * (z1 - z0) * (z0 + z1) / 2 for y0, y1, z0, z1 in rects) / A
    Iyy = Izz = Iyz = 0.0
    for y0, y1, z0, z1 in rects:
        b, h = y1 - y0, z1 - z0
        yc, zc = (y0 + y1) / 2 - yb, (z0 + z1) / 2 - zb
        Iyy += b * h ** 3 / 12 + b * h * zc ** 2
        Izz += h * b ** 3 / 12 + b * h * yc ** 2
        Iyz += b * h * yc * zc
    return A, yb, zb, Iyy, Izz, Iyz


def max_bending_stress(rects, My, Mz, N=0.0):
    """Largest |normal stress| over the rectangle corners for moments My (about the y axis: stress varies with z) and
    Mz (about the z axis: stress varies with y), unsymmetric bending, plus axial force N. Sign of the moments is
    irrelevant here: both signs are checked."""
    A, yb, zb, Iyy, Izz, Iyz = rect_section(rects)
    D = Iyy * Izz - Iyz ** 2
    worst = 0.0
    for sy in (1, -1):
        for sz in (1, -1):
            my, mz = sy * My, sz * Mz
            for y0, y1, z0, z1 in rects:
                for y in (y0, y1):
                    for z in (z0, z1):
                        s = ((my * Izz + mz * Iyz) * (z - zb) - (mz * Iyy + my * Iyz) * (y - yb)) / D
                        worst = max(worst, abs(s) + abs(N) / A)
    return worst


# ================================== 20261026-arm-claw-frame (round 1) ==================================
JOB = "20261026-arm-claw-frame"
P = claw_model_params(JOB)                 # CLR, END_CLR, TOP_PILOT_DEPTH, FRONT_PILOT_DEPTH, ...
ACC = 3.0                                  # spec 4: claw + camera weight x3 for arm accelerations (cyclic, SF 4)
TUG_N = 10.0                               # spec 4: Brio USB-cable tug at the camera end, any direction (short-term)
T_CLAW = MG90S.stall_torque_nmm            # claw MG90S stall, 216 N.mm at 6 V
F_RACK = T_CLAW / CF.R_P                   # 24 N into the racks (one jaw blocked)
F_SEP = F_RACK * math.tan(math.radians(20.0))   # gear separating force 8.7 N
X_MESH = (CF.X_P0 + CF.X_P1) / 2           # mid face width of pinion and racks (23.4)
X_LOAD = CF.X_TIP - 3.0                    # object pinched between the fingertips (assembly check's fingertip point)
T_FLOOR = CF.T_W - HORN_DEPTH              # wrist plate under the wrist-horn pocket (4)
HC = HOLE_COMP
CAM_END = (CAM_CG[0], 0.5 * BRIO.length, CAM_CG[1])   # USB socket: end of the Brio, mid height (claw frame G)


def wrist_pocket_half_w(x):
    """Half width of the MG90S single-arm horn pocket at x (hub circle behind the axis, hull of discs in front)."""
    rh = (WRIST.horn_d + 0.5 + HC) / 2
    return math.sqrt(max(rh ** 2 - x ** 2, 0.0)) if x < 0 else pocket_half_w(WRIST, x)


def tail_rects(x, half=CF.REAR_HALF, t=CF.T_W):
    """Wrist plate behind the bulkhead (y-z cut at x): plate minus the 2-deep horn pocket and the clamp hole."""
    wp = wrist_pocket_half_w(x)
    hy = math.sqrt(max(((WRIST.horn_screw_clear_d + HC) / 2) ** 2 - x ** 2, 0.0))   # clamp hole half chord
    r = [(-half, -wp, 0.0, t), (wp, half, 0.0, t)]
    r += [(-wp, -hy, HORN_DEPTH, t), (hy, wp, HORN_DEPTH, t)] if hy > 0 else [(-wp, wp, HORN_DEPTH, t)]
    return r


def tail_caps(half=CF.REAR_HALF, t=CF.T_W, x=0.0, Kt=2.0):
    """Moment capacities (at the allowables, SF 1) of the tail section: bending about y (in-plane, Kt 2 clamp hole) and
    torsion about x (conservatively interlayer shear, thin-strip J of the grooved section)."""
    r = tail_rects(x, half, t)
    A, yb, zb, Iyy, Izz, Iyz = rect_section(r)
    c = max(zb, t - zb)
    M_cap = allow_mpa(False) * Iyy / c / Kt
    J = sum((y1 - y0) * (z1 - z0) ** 3 / 3 for y0, y1, z0, z1 in r) * (1 - 0.63 * t / (2 * half))
    T_cap = allow_mpa(True, True) * J / t
    return M_cap, T_cap, Iyy, c, J, A


def wrist_moments(F, at):
    """(|Mx|, |My|, |Mz|) about the wrist horn (claw origin) of force F (claw axes) acting at point `at`."""
    return tuple(abs(m) for m in cross(at, F))


# --- sections (cross-checked against build123d sections of design(), 2026-10-26) ---------------------------
A0, _, zb0, I0, _, _ = rect_section(tail_rects(0.0))
A2, _, zb2, I2, _, _ = rect_section(tail_rects(2.0))
print(f"tail x 0: A {A0:.1f} Iyy {I0:.0f} c {max(zb0, CF.T_W - zb0):.2f} (CAD A 93.6, I 261, c 3.23); "
      f"x 2: A {A2:.1f} Iyy {I2:.0f} (CAD 104.8, 285)")
WIN_Y = (-(WRIST.length - WRIST.shaft_from_end) - (P.END_CLR + HC) / 2, WRIST.shaft_from_end + (P.END_CLR + HC) / 2)
STRIPS = [CF.HALF_Y + WIN_Y[0], CF.HALF_Y - WIN_Y[1]]          # bulkhead strips beside the servo window
PIL_W = WRIST.screw_pilot_d + HC + 0.4                           # tab pilot + outward slot (micro servo)
Z_BULK_ROOT = 2 * CF.HALF_Y * CF.BULK_T ** 2 / 6                 # above the rail (z 13..16)
Z_BULK_WIN = sum(STRIPS) * CF.BULK_T ** 2 / 6                    # beside the window
Z_BULK_PIL = (sum(STRIPS) - 2 * PIL_W) * CF.BULK_T ** 2 / 6      # through the tab pilots (z 22.5)
Z_STRIP = min(STRIPS) * CF.BULK_T ** 2 / 6
print(f"bulkhead Z about y: root {Z_BULK_ROOT:.0f} (CAD 384), window {Z_BULK_WIN:.0f} (CAD 247), pilots {Z_BULK_PIL:.0f} "
      f"(CAD 221), narrow strip {Z_STRIP:.0f}; window y {WIN_Y[0]:.2f}..{WIN_Y[1]:.2f}")

# 1. wrist stall through the horn pocket (MG90S single-arm horn, 2 deep)
F_arm = STALL_WRIST_NMM / (WRIST.horn_arm_len + WRIST.horn_tip_d / 2 - 2.0)
check("wrist stall 216 N.mm: horn-pocket wall bearing", bearing(F_arm, 4.0, HORN_DEPTH), False, SF_STATIC)

# 2. clamped wrist-horn joint (M2x12 + D6 washer from the front face, 1 arm screw; floor T_W - 2) and the tail
cap_t, cap_T = clamp_caps("SG90", T_FLOOR)
Mcap, Tcap, _, _, Jt, _ = tail_caps()
print(f"clamped wrist joint capacity (SF 1): transverse {cap_t:.0f}, torsion {cap_T:.0f} N.mm (floor {T_FLOOR:.0f}); "
      f"tail x 0: bending {Mcap:.0f} (Kt 2), torsion {Tcap:.0f} N.mm (J {Jt:.0f})")
pts = {"horn": ("W", 2, (cap_t, cap_T)), "tail": ("W", 2, (Mcap, Tcap))}
SW = {m: sweep(pts, m) for m in ("yaw", "hand")}
for m in SW:
    print(f"{m:4s} sweep at the wrist horn: T {SW[m]['horn']['T']:.0f}, Mt {SW[m]['horn']['Mt']:.0f} N.mm")
# weight x3 of everything beyond the wrist horn (claw, camera, 50 g payload), gravity anywhere in the claw x-y plane
EEP = [it for it in ITEMS if it[2] >= 3]
W_N = sum(m for _, m, _, _, _ in EEP) * G_N_PER_G
ZW = sum(m * (y - Y_CLAW) for _, m, _, _, y in EEP) / sum(m for _, m, _, _, _ in EEP)
w_util = max(abs(math.cos(a)) * ZW * ACC * W_N / cap_t + abs(math.sin(a)) * ZW * ACC * W_N / cap_T
             for a in [math.radians(i) for i in range(0, 360, 2)])
w_tail = max(abs(math.cos(a)) * ZW * ACC * W_N / Mcap + abs(math.sin(a)) * ZW * ACC * W_N / Tcap
             for a in [math.radians(i) for i in range(0, 360, 2)])
print(f"weight beyond the wrist horn {W_N / G_N_PER_G:.0f} g, CoG {ZW:.1f} outboard of the back face -> x{ACC:.0f}: "
      f"{ZW * ACC * W_N:.0f} N.mm transverse or torsion")
# USB tug at the camera end: worst direction; Mz (about the wrist axis) is not carried by the clamp (servo spline)
DIRS = unit_dirs(3)
tug = []
for sy in (1, -1):
    at = (CAM_END[0], sy * CAM_END[1], CAM_END[2])
    for d in DIRS:
        Mx, My, _ = wrist_moments(tuple(TUG_N * c for c in d), at)
        tug.append((My / cap_t + Mx / cap_T, My / Mcap + Mx / Tcap, Mx, My))
tug_joint = max(tug, key=lambda r: r[0])
tug_tail = max(tug, key=lambda r: r[1])
print(f"USB tug {TUG_N:.0f} N at the camera end {CAM_END[0]:.1f}, +-{CAM_END[1]:.0f}, {CAM_END[2]:.1f}: worst for the joint "
      f"Mx {tug_joint[2]:.0f} My {tug_joint[3]:.0f}; worst for the tail Mx {tug_tail[2]:.0f} My {tug_tail[3]:.0f} N.mm")
check_util("weight x3 (cyclic): clamped wrist-horn joint", w_util, SF_SUSTAINED)
check_util("weight x3 (cyclic): tail x 0 bending (Kt 2 clamp hole) + torsion", w_tail, SF_SUSTAINED)
for m, lbl in (("yaw", "yaw-stall sweep"), ("hand", "hand push 5 N")):
    check_util(f"{lbl}: clamped wrist-horn joint (D6 washer + arm screw, floor {T_FLOOR:.0f})", SW[m]["horn"]["Fs"], SF_STATIC)
    check_util(f"{lbl}: tail x 0 (20 wide) bending (Kt 2 clamp hole) + torsion", SW[m]["tail"]["Fs"], SF_STATIC)
check_util(f"USB tug {TUG_N:.0f} N, worst direction: clamped wrist-horn joint", tug_joint[0], SF_STATIC)
check_util(f"USB tug {TUG_N:.0f} N, worst direction: tail x 0 bending (Kt 2) + torsion", tug_tail[1], SF_STATIC)

# 3. claw-servo stall into the bulkhead: torque about x through the 2 tab screws (horizontal pilots in a wall)
TABS = [(-WRIST.hole_dx / 2 + (-(MG90S.length - MG90S.shaft_from_end) + MG90S.length / 2), 0.0),
        (WRIST.hole_dx / 2 + (-(MG90S.length - MG90S.shaft_from_end) + MG90S.length / 2), 0.0)]   # (y, z - ZS)
Fs = max(servo_screw_forces(T_CLAW, TABS))
L_TAB = min(CF.BULK_T, 8.0 - MG90S.tab_t)                    # M2x8 self-tapping through the 2.5 mm tab
LIG = min(abs(TABS[0][0]) - WIN_Y[0] * -1, TABS[1][0] - WIN_Y[1]) - (WRIST.screw_pilot_d + HC) / 2
check("claw stall 216 N.mm: tab-pilot bearing (compression)", bearing(Fs, MG90S.screw_pilot_d, L_TAB), False, SF_STATIC)
check(f"claw stall: pilot-to-window ligament {LIG:.2f} tear-out, full F toward the window (Z shear)",
      tearout(Fs, LIG, CF.BULK_T), True, SF_STATIC, shear=True)
# one jaw blocked: 24 N + 8.7 N on the output shaft at mid face width -> couple on the tabs
F_r = math.hypot(F_RACK, F_SEP)
M_tab_y = F_RACK * (X_MESH - CF.X_B)                          # about z: tabs couple along y (lever ~ 30)
M_tab_z = F_SEP * (X_MESH - CF.X_B)                           # about y: tab edge (servo half width) to the screw line
TAB_TIP = (MG90S.tab_span / 2 + (-(MG90S.length - MG90S.shaft_from_end) + MG90S.length / 2))
lev_y = min(TAB_TIP - TABS[0][0], TABS[1][0] + TAB_TIP - 2 * (-(MG90S.length - MG90S.shaft_from_end) + MG90S.length / 2))
F_pull = M_tab_y / lev_y + M_tab_z / (MG90S.width / 2) / 2
print(f"one jaw blocked: shaft load {F_r:.1f} N at {X_MESH - CF.X_B:.1f} mm in front of the tab face -> worst tab-screw pull "
      f"{F_pull:.1f} N (levers {lev_y:.1f} / {MG90S.width / 2:.1f})")
check(f"one jaw blocked: tab screw pull-out, {F_pull:.1f} N (M2x8, L {L_TAB:.1f}, Z shear)",
      pullout(F_pull, MG90S.screw_pilot_d, L_TAB), True, SF_STATIC, shear=True)
b_eff = 2 * (CF.ZS - (CF.ZS - CF.RAIL_IN))
check("one jaw blocked: bulkhead root above the rail, tab push (Z, Kt 2.5)",
      bend(M_tab_y / lev_y * (CF.ZS - (CF.ZS - CF.RAIL_IN)), b_eff * CF.BULK_T ** 3 / 12, CF.BULK_T / 2), True, SF_STATIC,
      Kt=2.5)

# 4. rack B thrust couple (one jaw blocked, jaw B): back contact on the lower rail; separating + twist on the plate
M_z = F_RACK * (X_LOAD - X_MESH)
D_MIN = (CF.RACK_Y[1] - CF.STROKE) - (-CF.HALF_Y)             # rack ends inside the guides at full opening
R_th = M_z / D_MIN
print(f"thrust couple (one jaw blocked): M {M_z:.0f} N.mm about z -> {R_th:.1f} N at each rack end (lever {D_MIN:.1f})")
check(f"rack B back thrust {R_th:.1f} N on the rail face (3 mm contact x rack height)", R_th / (3.0 * (CF.ZS - CF.RAIL_IN
      - CF.T_W - CF.CLR)), False, SF_STATIC)

# 5. bulkhead under the cover / camera loads (the cover takes the camera moment as a z-couple; the bulkhead gets the
#    x-shear at its top and the twist about the wrist axis, which the wrist servo limits to its stall torque)
F_inert = (sum(m for n, m, k, x, z in EE if n in ("camera-mount", "Brio 4K", "1/4-20 thumb screw"))
           + volume_mm3("20261026-arm-claw-cover") * RHO_G_PER_MM3) * G_N_PER_G * ACC
for lbl, Fx, req in ((f"camera + mount + cover weight x{ACC:.0f} along x (cyclic)", F_inert, SF_SUSTAINED),
                     (f"USB tug {TUG_N:.0f} N along x at the top screws", TUG_N, SF_STATIC)):
    Mz = STALL_WRIST_NMM if req == SF_STATIC else 0.0
    F_tw = Mz / (CF.TOP_SCREWS[1][1] - CF.TOP_SCREWS[0][1])
    h_win, h_root = CF.Z_TOP0 - (CF.ZS - (WRIST.width + P.CLR + HC) / 2), CF.Z_TOP0 - (CF.ZS - CF.RAIL_IN)
    check(f"{lbl}: bulkhead root above the rail (Z, Kt 2.5)", Fx * h_root / Z_BULK_ROOT, True, req, Kt=2.5)
    check(f"{lbl}{' + twist 216 on the narrow strip' if Mz else ''}: bulkhead at the window corners (Z, Kt 2.5)",
          Fx * h_win / Z_BULK_WIN + F_tw * h_win / Z_STRIP, True, req, Kt=2.5)

# 6. cover screws: front M3x12 into the wrist plate edge (horizontal pilots), top M3x18 into the bulkhead top
check(f"rack thrust {R_th:.1f} N on the front plate next to a front screw: M3x12 pull-out (L {P.FRONT_PILOT_DEPTH - 1:.0f})",
      pullout(R_th, CF.M3_PILOT, P.FRONT_PILOT_DEPTH - 1), True, SF_STATIC, shear=True)
F_top = TUG_N * (CAM_END[2] - CF.Z_TOP1) / (CF.TOP_SCREWS[0][0] - (CF.X_B - CF.BULK_T)) / 2
L_top = min(P.TOP_PILOT_DEPTH, 18.0 - (CF.PAD_TOP - CF.Z_TOP1) - CF.TOP_T)
check(f"USB tug tips the camera mount back over the cover's rear edge: top screw pull-out {F_top:.0f} N (M3x18, L {L_top:.1f})",
      pullout(F_top, CF.M3_PILOT, L_top), True, SF_STATIC, shear=True)

worst, fails = report(JOB)

# --- what-if: the changes recommended in strength.md ---------------------------------------------------------------
# The wrist plate behind the bulkhead (x -8..4) carries nothing else, so it can be widened to the full 64 mm and raised
# 2 mm on its front face (8 mm there, floor under the clamp washer 6 mm) without moving rack B's track (T_W stays 6).
print("\nWhat-if (advisory): SF of the failing rows with the candidate changes (sweeps: max T and max Mt combined)")
for half, t in ((CF.REAR_HALF, CF.T_W), (CF.HALF_Y, CF.T_W), (CF.HALF_Y, CF.T_W + 2.0)):
    ct, cT = clamp_caps("SG90", t - HORN_DEPTH)
    Mc, Tc, *_ = tail_caps(half, t)
    j = max(r[3] / ct + r[2] / cT for r in tug)
    tl = max(r[3] / Mc + r[2] / Tc for r in tug)
    wl = max(abs(math.cos(a)) * ZW * ACC * W_N / Mc + abs(math.sin(a)) * ZW * ACC * W_N / Tc
             for a in [math.radians(i) for i in range(0, 360, 2)])
    sw_t = max(SW[m]["tail"]["Mt"] / Mc + SW[m]["tail"]["T"] / Tc for m in SW)
    sw_j = max(SW[m]["horn"]["Mt"] / ct + SW[m]["horn"]["T"] / cT for m in SW)
    print(f"  wrist plate behind the bulkhead {2 * half:.0f} wide x {t:.0f} thick (clamp floor {t - HORN_DEPTH:.0f}): "
          f"tail: weight x3 SF {1 / wl:.2f} (req 4), sweeps {1 / sw_t:.2f}, USB tug {1 / tl:.2f}; "
          f"clamped joint: USB tug {1 / j:.2f}, sweeps {1 / sw_j:.2f}")
h_win = CF.Z_TOP0 - (CF.ZS - (WRIST.width + P.CLR + HC) / 2)
s_win = TUG_N * h_win / Z_BULK_WIN + STALL_WRIST_NMM / (CF.TOP_SCREWS[1][1] - CF.TOP_SCREWS[0][1]) * h_win / Z_STRIP
print(f"  servo window lower corners relieved (r >= 1.5 or D3 corner reliefs, Kt 2.5 -> 1.5): USB tug SF "
      f"{allow_mpa(True) / (1.5 * s_win):.2f}")

# --- static servo torques, arm straight out horizontally (spec: payloads 0 / 20 / 50 g, camera fitted) -------------
print("\nStatic servo torques, arm straight and horizontal (N.mm, % of stall):")
CAM_ITEMS = ("camera-mount", "Brio 4K", "1/4-20 thumb screw")
for cam in (True, False):
    for pay in (0.0, 20.0, 50.0):
        its = [it for it in ITEMS if (cam or it[0] not in CAM_ITEMS) and it[0] != "payload"]
        its.append(("payload", pay, 4, L1 + L2 + L3, Y_TIP))
        tq = {k: sum(m * G_N_PER_G * (s - S_JOINT[k]) for _, m, kk, s, _ in its if kk >= k) for k in (1, 2, 3)}
        print(f"  {'camera' if cam else 'no camera'}, payload {pay:2.0f} g: shoulder {tq[1]:4.0f} ({100 * tq[1] / STALL_MG996R_NMM:2.0f} %)"
              f"  elbow {tq[2]:4.0f} ({100 * tq[2] / STALL_MG996R_NMM:2.0f} %)  wrist {tq[3]:3.0f} ({100 * tq[3] / STALL_WRIST_NMM:2.0f} %)")
pay_max = {}
for cam in (True, False):
    its = [it for it in ITEMS if (cam or it[0] not in CAM_ITEMS) and it[0] != "payload"]
    t0 = sum(m * G_N_PER_G * (s - S_JOINT[1]) for _, m, kk, s, _ in its if kk >= 1)
    pay_max[cam] = (0.5 * STALL_MG996R_NMM - t0) / (G_N_PER_G * (L1 + L2 + L3))
print(f"payload at which the shoulder static torque reaches 50 % of stall (x2 dynamic = stall): camera "
      f"{pay_max[True]:.0f} g, no camera {pay_max[False]:.0f} g")

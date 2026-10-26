"""Strength check for jobs/20261026-arm-claw-jaw (claw v2 + Brio 4K, round 1). Run: python3 jobs/20261026-arm-claw-jaw/strength_calc.py

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


def check_sf(name, sf, sf_req, tag="Z comb", allow=None, info=False):
    """Record a combined check by its safety factor. 'Z comb': normal stress across the layers and interlayer shear,
    (sigma/12.5)^2 + (tau/6.25)^2 = (1/SF)^2; the stress column shows the equivalent across-layer stress 12.5/SF."""
    a = allow_mpa(True) if allow is None else allow
    (advisory if info else cases).append((name, tag, a / sf, a, sf, sf_req))
    return sf


# =================================== 20261026-arm-claw-jaw (round 1) ===================================
# Printed STANDING (claw +x = print Z): every normal stress along the finger (grip bending, sideways bending, axial)
# and the torsion/transverse shear on a section x = const act ACROSS the layers. The rack teeth are drawn in the bed
# plane, so tooth bending runs along the layers.
JOB = "20261026-arm-claw-jaw"
P = claw_model_params(JOB)                 # TIP_CHAMFER, TIP_BEVEL, GROOVE_D, GROOVE_PITCH, GROOVE_X, NOTCH_D, GUSSET
T_CLAW = MG90S.stall_torque_nmm
X_MESH = (CF.X_P0 + CF.X_P1) / 2
SIG_Z, TAU_Z = allow_mpa(True), allow_mpa(True, True)   # across-layer normal / interlayer shear allowables


def jaw_geom(**over):
    """Jaw A geometry, heights relative to the pinion axis ZS (claw frame G). Overrides give candidate redesigns."""
    g = dict(F_RACK=T_CLAW / CF.R_P, X_ROOT=CF.X_P1, NECK_X1=CF.NECK_X1, NECK_Y=CF.NECK_Y, NECK_Z=CF.NECK_Z,
             BLADE_T=lambda x: CF.BLADE_T, Z_TOP=CF.GRIP_HALF, GUSSET_FULL=False, X_TIP=CF.X_TIP,
             KT_ROOT=2.5, KT_KINK=2.0, KT_GROOVE=2.0, label="as modelled")
    g.update(over)
    return g


def jaw_rects(x, g):
    """Section of jaw A at x as (y0, y1, z0, z1) rectangles, z relative to ZS (blade + 45 deg flare, or the neck)."""
    zn0, zn1 = g["NECK_Z"]
    if x < g["NECK_X1"]:
        return [(-g["NECK_Y"], 0.0, zn0, zn1)], (1.0, 1.0)
    s = x - g["NECK_X1"]
    z_lo = max(-CF.GRIP_HALF, zn0 - s)                   # 45 deg lower edge from the neck down to the grip zone
    z_hi = max(g["Z_TOP"], zn1 - s) if g["Z_TOP"] < zn1 else zn1   # upper edge: 45 deg step down to the grip zone top
    xt = g["X_TIP"] - P.TIP_CHAMFER                      # 45 deg tip corners
    if x > xt:
        z_lo, z_hi = z_lo + (x - xt), z_hi - (x - xt)
    bt = g["BLADE_T"](x)
    bev = g["X_TIP"] - 2 * P.TIP_BEVEL - 2              # outer-face bevel to the thin tip
    if x > bev:
        bt = min(bt, bt - (x - bev) * (bt - 2.0) / (g["X_TIP"] - bev))
    groove = P.GROOVE_X[0] - P.GROOVE_D <= x <= P.GROOVE_X[1] + P.GROOVE_D
    y_face = -P.GROOVE_D if groove else 0.0             # section through a groove root (0.6 deep across the face)
    r = [(-bt, y_face, z_lo, z_hi)]
    if x >= CF.GRIP_X0 - 4:                               # V-notch along the grip face, on the centre line
        r = [(-bt, y_face, z_lo, -P.NOTCH_D / 2), (-bt, -P.NOTCH_D + y_face, -P.NOTCH_D / 2, P.NOTCH_D / 2),
             (-bt, y_face, P.NOTCH_D / 2, z_hi)]
    yf = -g["NECK_Y"] + s                                 # flare: 45 deg in plan from the neck into the blade
    if yf < -bt:
        f0, f1 = (z_lo, z_hi) if g["GUSSET_FULL"] else (max(zn0, z_lo), min(zn1, z_hi))
        if f1 > f0:
            r.append((yf, -bt, f0, f1))
    # stress concentrations at the re-entrant (225 deg) corners of the outline, per bending direction:
    # grip (about z, extreme fibres on the faces y): the flare / gusset end on the outer face; grooves on the grip face
    # sideways (about y, extreme fibres on the edges z): the neck bottom turning into the 45 deg lower edge, and the
    # 45 deg top edge turning flat; grooves on the grip face
    kz = g["KT_GROOVE"] if groove else (g["KT_KINK"] if abs(s - (g["NECK_Y"] - bt)) <= 1.0 else 1.0)
    ky = g["KT_GROOVE"] if groove else (g["KT_KINK"] if s <= 1.0 or (zn1 > g["Z_TOP"] and abs(s - (zn1 - g["Z_TOP"])) <= 1.0)
                                        else 1.0)
    return r, (ky, kz)


def sec_util(x, g, F, Q, req_sf=None):
    """SF at section x for force F (claw axes) at point Q (x, y, z rel. ZS): unsymmetric bending + axial (Kt) across the
    layers, torsion + transverse shear as interlayer shear, quadratic interaction."""
    if x < g["X_ROOT"] + 0.5:
        rects, (ky, kz) = jaw_rects(x, g)[0], (g["KT_ROOT"], g["KT_ROOT"])
    else:
        rects, (ky, kz) = jaw_rects(x, g)
    A, yb, zb, Iyy, Izz, Iyz = rect_section(rects)
    M = cross((Q[0] - x, Q[1] - yb, Q[2] - zb), F)
    # each bending direction with its own Kt; maxima added (they may sit at different corners: conservative)
    sig = (ky * max_bending_stress(rects, M[1], 0.0) + kz * max_bending_stress(rects, 0.0, M[2])
           + max(ky, kz) * abs(F[0]) / A)
    J = sum(max(y1 - y0, z1 - z0) * min(y1 - y0, z1 - z0) ** 3 / 3 * (1 - 0.63 * min(y1 - y0, z1 - z0) / max(y1 - y0, z1 - z0))
            for y0, y1, z0, z1 in rects)
    t_max = max(min(y1 - y0, z1 - z0) for y0, y1, z0, z1 in rects)
    tau = abs(M[0]) * t_max / J + 1.5 * math.hypot(F[1], F[2]) / A
    return 1.0 / math.sqrt((sig / SIG_Z) ** 2 + (tau / TAU_Z) ** 2), sig, tau


def scan(g, F, Q, x0=None, x1=None, step=0.25):
    x0 = g["X_ROOT"] + 0.01 if x0 is None else x0
    x1 = g["X_TIP"] - 6.0 if x1 is None else x1
    best = None
    x = x0
    while x <= x1:
        sf, s, t = sec_util(x, g, F, Q)
        if best is None or sf < best[0]:
            best = (sf, x, s, t)
        x += step
    return best


G0 = jaw_geom()
# section cross-check against the build123d sections of design() (2026-10-26)
for x, cad in ((27.5, (70.0, 1143.3, 145.8)), (34.15, (40.0, 337.4, 83.2)), (37.0, (51.5, 208.4, 278.0)),
               (49.15, (117.8, 345.5, 3999.2))):
    A, yb, zb, Iyy, Izz, Iyz = rect_section(jaw_rects(x, G0)[0])
    print(f"jaw section x {x:5.2f}: A {A:6.1f} I(grip, about z) {Izz:7.1f} I(side, about y) {Iyy:7.1f}   "
          f"CAD A {cad[0]}, {cad[1]}, {cad[2]}")

Q_GRIP = (CF.X_TIP - 3.0, 0.0, 0.0)          # object pinched between the fingertips, on the V-notch centre line
Q_TIP = (CF.X_TIP, -CF.BLADE_T / 2, 0.0)     # fingertip, for sideways and yaw-stall forces
F1 = T_CLAW / CF.R_P
TF = {m: tip_forces(m) for m in ("yaw", "hand")}
print(f"stall rack force {F1:.1f} N (one jaw blocked), {F1 / 2:.1f} N per jaw (both); fingertip forces from the sweeps: "
      f"yaw {len(TF['yaw'])} cases, max |Fz| {max(abs(f[2]) for f in TF['yaw']):.1f} N, max |Fy| "
      f"{max(abs(f[1]) for f in TF['yaw']):.1f} N; hand {max(abs(f[2]) for f in TF['hand']):.1f} N")


def jaw_cases(g, record=True):
    """All verdict rows of the jaw for geometry g. Returns [(name, sf, req)]."""
    F = g["F_RACK"]
    Q_GRIP = (g["X_TIP"] - 3.0, 0.0, 0.0)
    Q_TIP = (g["X_TIP"], -CF.BLADE_T / 2, 0.0)
    rows = []
    for lbl, f, req in ((f"grip at stall, one jaw blocked, {F:.0f} N", F, SF_STATIC),
                        (f"grip at stall, both jaws, {F / 2:.0f} N each (cyclic)", F / 2, SF_SUSTAINED)):
        for where, xa, xb in (("neck root at the rack face (Kt %.1f)" % g["KT_ROOT"], g["X_ROOT"] + 0.01, g["X_ROOT"] + 0.01),
                              ("neck + finger root (worst section)", g["X_ROOT"] + 0.6, None)):
            sf, x, s, t = scan(g, (0.0, -f, 0.0), Q_GRIP, xa, xb)
            rows.append((f"{lbl}: {where} x {x:.1f}, sigma {s:.1f} tau {t:.1f}", sf, req))
    for where, xa, xb in (("neck root (Kt %.1f)" % g["KT_ROOT"], g["X_ROOT"] + 0.01, g["X_ROOT"] + 0.01),
                          ("neck + finger root (worst section)", g["X_ROOT"] + 0.6, None)):
        best = None
        for f in TF["hand"]:
            for sgn in (1, -1):
                r = scan(g, tuple(sgn * c for c in f), Q_TIP, xa, xb, step=0.5)
                if best is None or r[0] < best[0]:
                    best = r
        rows.append((f"hand push 5 N at the fingertip: {where} x {best[1]:.1f}, sigma {best[2]:.1f} tau {best[3]:.1f}",
                     best[0], SF_STATIC))
        # yaw sweep: every pose's fingertip force on one finger, both signs (obstacle on either side)
        xs = [g["X_ROOT"] + 0.01] if xb is not None else sorted({round(scan(g, (0.0, 0.0, 1.0), Q_TIP, xa, xb)[1], 2),
                                                               round(scan(g, (0.0, 1.0, 0.0), Q_TIP, xa, xb)[1], 2)})
        best = None
        for f in TF["yaw"]:
            for sgn in (1, -1):
                for x in xs:
                    r = sec_util(x, g, tuple(sgn * c for c in f), Q_TIP)
                    if best is None or r[0] < best[0]:
                        best = (r[0], x, r[1], r[2])
        rows.append((f"yaw-stall sweep at the fingertip: {where} x {best[1]:.1f}, sigma {best[2]:.1f} tau {best[3]:.1f}",
                     best[0], SF_STATIC))
    return rows


for name, sf, req in jaw_cases(G0):
    check_sf(name, sf, req)

# rack teeth (profile in the bed plane: tooth bending along the layers)
a20 = math.radians(20.0)
hw = (math.pi * CF.M / 2 - CF.BACKLASH / 2) / 2
t_root = 2 * (hw + 1.25 * CF.M * math.tan(a20))
for lbl, f, req in (("one jaw blocked", F1, SF_STATIC), ("both jaws (cyclic)", F1 / 2, SF_SUSTAINED)):
    check(f"rack teeth, {lbl} {f:.0f} N: Lewis (rack Y 0.485), face {CF.FACE_W:.0f}", f / (CF.FACE_W * CF.M * 0.485), False, req)
    check(f"rack teeth, {lbl}: tooth root {t_root:.2f} wide, tip load 2.25 m above it", 6 * f * 2.25 * CF.M /
          (CF.FACE_W * t_root ** 2), False, req)
R_th = F1 * (Q_GRIP[0] - X_MESH) / ((CF.RACK_Y[1] - CF.STROKE) + CF.HALF_Y)
check(f"rack end bearing on the lip / front plate, thrust couple {R_th:.0f} N (3 mm x rack height)",
      R_th / (3.0 * (CF.RACK_OUT - CF.RACK_TIP)), False, SF_STATIC)

worst, fails = report(JOB)

# --- what-if: candidate redesigns (advisory) ------------------------------------------------------------------------
print("\nWhat-if (advisory): lowest SF of the jaw rows above for candidate redesigns")
CANDS = [
    jaw_geom(label="A: neck on the rack's solid back strip, 20 (y) x 6 (z) [NECK_Y 14 -> 20, NECK_Z (8, 13) -> (10.25, "
                   "16.25)], finger 10 thick to x 51 then 6 by x 61, full-height 45 deg gusset, top edge kept at the neck "
                   "top, r>=4 at the neck root, r>=3 at the 45 deg kinks and the gusset end",
             NECK_Y=20.0, NECK_Z=(CF.RACK_ROOT, CF.RACK_OUT), GUSSET_FULL=True, Z_TOP=CF.RACK_OUT, KT_ROOT=1.5,
             KT_KINK=1.5, BLADE_T=lambda x: 10.0 if x <= 51.15 else max(6.0, 10.0 - (x - 51.15) * 0.4)),
    jaw_geom(label="B: as A, rack 4 mm taller (RACK_BACK 6 -> 10) so the neck is 20 x 10",
             NECK_Y=20.0, NECK_Z=(CF.RACK_ROOT, CF.RACK_OUT + 4.0), GUSSET_FULL=True, Z_TOP=CF.RACK_OUT + 4.0,
             KT_ROOT=1.5, KT_KINK=1.5, BLADE_T=lambda x: 10.0 if x <= 51.15 else max(6.0, 10.0 - (x - 51.15) * 0.4)),
    jaw_geom(label="D: as C with the rack only 2 mm taller (RACK_BACK 6 -> 8): neck 20 x 8",
             NECK_Y=20.0, NECK_Z=(CF.RACK_ROOT, CF.RACK_OUT + 2.0), GUSSET_FULL=True, Z_TOP=CF.RACK_OUT + 2.0,
             KT_ROOT=1.5, KT_KINK=1.5, BLADE_T=lambda x: 12.0 if x <= 51.15 else max(6.0, 12.0 - (x - 51.15) * 0.4)),
    jaw_geom(label="C: as B, finger 12 thick to x 51 then 6 by x 66",
             NECK_Y=20.0, NECK_Z=(CF.RACK_ROOT, CF.RACK_OUT + 4.0), GUSSET_FULL=True, Z_TOP=CF.RACK_OUT + 4.0,
             KT_ROOT=1.5, KT_KINK=1.5, BLADE_T=lambda x: 12.0 if x <= 51.15 else max(6.0, 12.0 - (x - 51.15) * 0.4)),
    jaw_geom(label="C5: C with the cover's front plate 5 thick (FRONT_T 3 -> 5): neck 2 mm longer, fingertip at x 78.15",
             NECK_Y=20.0, NECK_Z=(CF.RACK_ROOT, CF.RACK_OUT + 4.0), GUSSET_FULL=True, Z_TOP=CF.RACK_OUT + 4.0,
             KT_ROOT=1.5, KT_KINK=1.5, NECK_X1=CF.NECK_X1 + 2.0, X_TIP=CF.X_TIP + 2.0,
             BLADE_T=lambda x: 12.0 if x <= 53.15 else max(6.0, 12.0 - (x - 53.15) * 0.4)),
    jaw_geom(label="D5: D with FRONT_T 5",
             NECK_Y=20.0, NECK_Z=(CF.RACK_ROOT, CF.RACK_OUT + 2.0), GUSSET_FULL=True, Z_TOP=CF.RACK_OUT + 2.0,
             KT_ROOT=1.5, KT_KINK=1.5, NECK_X1=CF.NECK_X1 + 2.0, X_TIP=CF.X_TIP + 2.0,
             BLADE_T=lambda x: 12.0 if x <= 53.15 else max(6.0, 12.0 - (x - 53.15) * 0.4)),
]
for g in CANDS:
    rows = jaw_cases(g)
    lo = min(rows, key=lambda r: r[1] / r[2])
    print(f"  {g['label']}:\n    lowest SF {lo[1]:.2f} (req {lo[2]:.0f}) at {lo[0]}; "
          + "; ".join(f"{r[1]:.2f}" for r in rows))

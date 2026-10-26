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

# --- generic flat link on an MG996R double-arm horn, round 2 (upper link / forearm) -----------------------
def link_oop(T, half_w, x=None, cut_w=0.0, horn=MG996R):
    """Out-of-plane I and c (stress along x varies with z). x given -> section over the horn pocket."""
    if x is not None:
        wp = 2 * pocket_half_w(horn, x)
        rects = [(2 * half_w - wp, T, T / 2), (wp, T - HORN_DEPTH, HORN_DEPTH + (T - HORN_DEPTH) / 2)]
    else:
        rects = [(2 * half_w - cut_w, T, T / 2)]
    A, zb, I = comp_section(rects)
    return I, max(zb, T - zb)


def link_checks(job, P, far, far_name, far_stall, far_holes, far_lig, far_pilot, far_screw_L, far_levers, M_win,
                win_w, k, horn_name, li, joint, cad):
    T, HW = P.T, P.HALF_W
    t_floor = T - HORN_DEPTH
    row_x = P.L + far_holes[0][0]           # the tab-pilot row nearer the horn
    cap_t, cap_T = clamp_caps("MG996R", t_floor)
    pts = {"horn": (joint, li, (cap_t, cap_T)), "x15": ((joint, 15.0, 0.0), li, None), "x30": ((joint, 30.0, 0.0), li, None),
           "row": ((joint, row_x, 0.0), li, None), "far": ((joint, P.L, 0.0), li, far_levers)}
    SW = {m: sweep(pts, m) for m in ("yaw", "hand")}
    for m in SW:
        print(f"{m:4s} sweep: " + "; ".join(f"{n} T={o['T']:.0f} Mt={o['Mt']:.0f}" for n, o in SW[m].items()))
    w_in, w_oop = weight_inplane_nmm(k), weight_oop_nmm(k, Y_HORN[horn_name])
    print(f"weight beyond the {horn_name} horn: in-plane {w_in:.0f} N.mm (arm straight, horizontal), out-of-plane {w_oop:.0f}")
    I15, c15 = link_oop(T, HW, 15.0)
    If, cf = link_oop(T, HW)
    n_row = 2 if len(far_holes) == 4 else 1          # pilots in the row nearer the horn
    Ir, cr = link_oop(T, HW, cut_w=n_row * (far_pilot + HOLE_COMP))
    Iw, cw = link_oop(T, HW, cut_w=win_w)
    print(f"sections: oop I x15 {I15:.0f}, full {If:.0f}, pilot row {Ir:.0f}, window {Iw:.0f} (CAD {cad})")
    # 1. horn stall through the pocket walls (still 2 mm deep)
    s = MG996R
    F_arm = STALL_MG996R_NMM / (2 * (s.horn_arm_len + s.horn_tip_d / 2 - 2.5))
    check(f"{horn_name} stall 1000 N.mm: horn-pocket wall bearing", bearing(F_arm, 5.0, HORN_DEPTH), False, SF_STATIC)
    # 2. in-plane bending (strong axis), bounded by the horn-servo stall
    Iin = lambda cut: T * ((2 * HW) ** 3 - cut ** 3) / 12.0
    check("stall 1000 N.mm: in-plane bending, full section x30", bend(STALL_MG996R_NMM, Iin(0.0), HW), False, SF_STATIC)
    check(f"stall: in-plane bending at the {far_name} window, M {M_win:.0f} (Kt 2.5)", bend(M_win, Iin(win_w), HW), False,
          SF_STATIC, Kt=2.5)
    check("weight x2 (sustained): in-plane bending, full section", bend(DYN * w_in, Iin(0.0), HW), False, SF_SUSTAINED)
    # 3. far servo stall into its tab pilots (vertical pilots: in-plane bearing and tear-out)
    Fs = max(servo_screw_forces(far_stall, far_holes))
    check(f"{far_name} stall: tab-pilot bearing", bearing(Fs, far_pilot, T), False, SF_STATIC)
    check(f"{far_name} stall: pilot-to-window ligament {far_lig:.2f} tear-out (full F toward the window)",
          tearout(Fs, far_lig, T), False, SF_STATIC, shear=True)
    # 4. clamped horn joint
    check_util(f"weight x2 (sustained): clamped {horn_name}-horn joint (torsion)", DYN * abs(w_oop) / cap_T, SF_SUSTAINED)
    for m, lbl in (("yaw", "yaw-stall sweep"), ("hand", "hand push 5 N")):
        check_util(f"{lbl}: clamped {horn_name}-horn joint (D9 washer + arm screws, floor {t_floor:.0f})",
                   SW[m]["horn"]["Fs"], SF_STATIC)
    # 5. out-of-plane bending and torsion of the plate (along the layers; torsion conservatively as interlayer shear)
    for m, lbl, req in (("w", "weight x2 (sustained)", SF_SUSTAINED), ("yaw", "yaw-stall sweep", SF_STATIC),
                        ("hand", "hand push 5 N", SF_STATIC)):
        M = (lambda n: DYN * abs(w_oop)) if m == "w" else (lambda n, m=m: SW[m][n]["Mt"])
        check(f"{lbl}: out-of-plane bending x15 over the pocket (Kt 2 arm-screw hole)", bend(M("x15"), I15, c15), False, req,
              Kt=2.0)
        check(f"{lbl}: out-of-plane bending x30, full section", bend(M("x30"), If, cf), False, req)
        check(f"{lbl}: out-of-plane bending at the {far_name} pilot row x{row_x:.1f} (Kt 2)", bend(M("row"), Ir, cr), False,
              req, Kt=2.0)
        if m != "w":
            check(f"{lbl}: plate torsion, full width (Z shear)", torsion_thin(SW[m]["x30"]["T"], [(2 * HW, T)]), True, req,
                  shear=True)
            check(f"{lbl}: {far_name} tab screws pull-out (L {far_screw_L:.1f})",
                  pullout(SW[m]["far"]["Fs"], far_pilot, far_screw_L), True, req, shear=True)
            check(f"{lbl}: {far_name} window rails alone, servo case ignored (Kt 2.5)", bend(SW[m]["row"]["Mt"], Iw, cw),
                  False, req, Kt=2.5, info=True)
    return SW

# --- 20261025-arm-forearm (round 2) ----------------------------------------------------------------------
P = FA
WIN_W = WRIST.width + P.CLR + HOLE_COMP
PILOT = WRIST.screw_pilot_d                        # printed pilot 1.5 (CAD 1.7)
WRIST_SCREW = 12.0                                 # spec 2 / BUILD_GUIDE: 2 x M2x12 self-tapping (not the bag screws)
WRIST_L = min(P.T, WRIST_SCREW - WRIST.tab_t)      # engaged length in the forearm
# printed ligament: pilot inner edge (8.55 - 0.75) to the window end (5.9 + END_CLR / 2)
LIG = (WRIST.hole_dx / 2 + (-(WRIST.length - WRIST.shaft_from_end) + WRIST.length / 2)) - PILOT / 2 \
    - (WRIST.shaft_from_end + P.END_CLR / 2)
M_WIN = STALL_MG996R_NMM * (L2 + L3 - (P.L - (WRIST.length - WRIST.shaft_from_end))) / (L2 + L3)
SW = link_checks("20261025-arm-forearm", P, "W", "wrist MG90S", STALL_WRIST_NMM, [(-19.25, 0.0), (8.55, 0.0)], LIG,
                 PILOT, WRIST_L, (WRIST.hole_dx, 2 * WRIST.width / 2), M_WIN, WIN_W, 2, "elbow", 1, "E",
                 "x15 1927, x30 2163, x70.75 2021, window 1113")
check("claw + camera weight x2 + 1 N along x: MG90S pilot ligament tear-out", tearout(DYN * weight_n(3) + 1.0, LIG, P.T),
      False,
      SF_STATIC, shear=True)
worst, fails = report("20261025-arm-forearm")
print(f"wrist MG90S tab screws: M2x{WRIST_SCREW:.0f} through the {WRIST.tab_t} mm tab -> {WRIST_L:.1f} mm engaged"
      f" (bag screws would give ~5 mm: yaw-stall SF "
      f"{allow_mpa(True, True) / pullout(SW['yaw']['far']['Fs'], PILOT, 5.0):.2f})")

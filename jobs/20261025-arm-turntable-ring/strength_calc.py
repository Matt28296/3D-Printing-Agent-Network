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
UL = model_params("20261025-arm-upper-link")
FA = model_params("20261025-arm-forearm")
GB = model_params("20261025-arm-gripper-base")
JW = model_params("20261025-arm-gripper-jaw")
TT = model_params("20261025-arm-turntable")
STALL_MG996R_NMM, STALL_SG90_NMM = MG996R.stall_torque_nmm, SG90.stall_torque_nmm
L1, L2 = UL.L, FA.L                     # shoulder->elbow, elbow->wrist
GRIP_DX, L3 = GB.GRIP_X, GB.JAW_X1      # wrist -> gripper servo axis, wrist -> fingertip
SX, SZ = TT.XS, TT.ZS                   # shoulder axis X, Z
DESK_Z = -40.0
F_HAND_N = 5.0                          # handling case (spec 4): hand push out of the arm plane at the fingertip
HFZ_MG, HFZ_SG = horn_face_z(MG996R), horn_face_z(SG90)
# world-Y stack: each link's back face sits HORN_DEPTH below the horn face; the next servo's tabs sit on its front face
Y_SH_HORN = TT.UP_Y + HFZ_MG
Y_UL_BACK = Y_SH_HORN - HORN_DEPTH
Y_EL_TAB = Y_UL_BACK + UL.T
Y_EL_HORN = Y_EL_TAB + HFZ_MG
Y_FA_BACK = Y_EL_HORN - HORN_DEPTH
Y_WR_TAB = Y_FA_BACK + FA.T
Y_WR_HORN = Y_WR_TAB + HFZ_SG
Y_GB_BACK = Y_WR_HORN - HORN_DEPTH
Y_GR_TAB = Y_GB_BACK + GB.T
Y_GR_HORN = Y_GR_TAB + HFZ_SG
Y_JW_BACK = Y_GR_HORN - HORN_DEPTH
Y_HORN = {"shoulder": Y_SH_HORN, "elbow": Y_EL_HORN, "wrist": Y_WR_HORN, "gripper": Y_GR_HORN}
Y_TIP = Y_JW_BACK + JW.T / 2            # payload / fingertip: middle of the moving-jaw band


def _servo_body(s):
    """Body-centre offsets in the servo frame: x along the body, z (case centre below the tab underside)."""
    return -(s.length - s.shaft_from_end) + s.length / 2, s.case_top / 2 - s.tab_height


def _plate_cg_x(x0, x1, w, win_x, win_a):
    a = (x1 - x0) * w
    return (a * (x0 + x1) / 2 - win_a * win_x) / (a - win_a)


_mx, _mz = _servo_body(MG996R)
_sx, _sz = _servo_body(SG90)
M_UL, M_FA = volume_mm3("20261025-arm-upper-link") * RHO_G_PER_MM3, volume_mm3("20261025-arm-forearm") * RHO_G_PER_MM3
M_GB, M_JW = volume_mm3("20261025-arm-gripper-base") * RHO_G_PER_MM3, volume_mm3("20261025-arm-gripper-jaw") * RHO_G_PER_MM3
M_TT = volume_mm3("20261025-arm-turntable") * RHO_G_PER_MM3
CG_UL = _plate_cg_x(UL.X0, UL.X1, 2 * UL.HALF_W, UL.L + _mx, MG996R.length * MG996R.width)
CG_FA = _plate_cg_x(FA.X0, FA.X1, 2 * FA.HALF_W, FA.L + _sx, SG90.length * SG90.width)
_a_pl = (GB.X1 - GB.X0) * (GB.Y1 - GB.Y0) * GB.T
_a_jb = (GB.JAW_X1 - GB.JAW_X0) * (GB.JAW_Y1 - GB.JAW_Y0) * (GB.JAW_TOP - GB.T)
_a_wn = SG90.length * SG90.width * GB.T
CG_GB = ((_a_pl * (GB.X0 + GB.X1) / 2 + _a_jb * (GB.JAW_X0 + GB.JAW_X1) / 2 - _a_wn * (GB.GRIP_X + _sx))
         / (_a_pl + _a_jb - _a_wn))
CGZ_GB = (_a_pl * GB.T / 2 + _a_jb * (GB.T + GB.JAW_TOP) / 2 - _a_wn * GB.T / 2) / (_a_pl + _a_jb - _a_wn)
_a_hub, _a_bar = math.pi * JW.HUB_R ** 2, (JW.BAR_X1 + 4.0) * (JW.BAR_Y1 - JW.BAR_Y0)
CG_JW = (_a_bar * (JW.BAR_X1 - 4.0) / 2) / (_a_hub + _a_bar)
# (name, mass g, rides beyond joint k: 0 yaw, 1 shoulder, 2 elbow, 3 wrist, 4 gripper, s along the straight arm, world Y)
ITEMS = [
    ("shoulder MG996R", MG996R.mass_g, 0, -SX, TT.UP_Y + _mz),
    ("shoulder horn + clamp screw", 5.0, 1, 0.0, Y_SH_HORN - 1.4),
    ("upper link", M_UL, 1, CG_UL, Y_UL_BACK + UL.T / 2),
    ("elbow MG996R", MG996R.mass_g, 1, L1 + _mx, Y_EL_TAB + _mz),
    ("cable allowance 1", 6.0, 1, L1, Y_EL_TAB),
    ("elbow horn + clamp screw", 5.0, 2, L1, Y_EL_HORN - 1.4),
    ("forearm", M_FA, 2, L1 + CG_FA, Y_FA_BACK + FA.T / 2),
    ("wrist SG90", SG90.mass_g, 2, L1 + L2 + _sx, Y_WR_TAB + _sz),
    ("cable allowance 2", 4.0, 2, L1 + L2, Y_WR_TAB),
    ("wrist horn + clamp screw", 2.0, 3, L1 + L2, Y_WR_HORN - 0.8),
    ("gripper base", M_GB, 3, L1 + L2 + CG_GB, Y_GB_BACK + CGZ_GB),
    ("gripper SG90", SG90.mass_g, 3, L1 + L2 + GRIP_DX + _sx, Y_GR_TAB + _sz),
    ("gripper horn + clamp screw", 2.0, 4, L1 + L2 + GRIP_DX, Y_GR_HORN - 0.8),
    ("moving jaw", M_JW, 4, L1 + L2 + GRIP_DX + CG_JW, Y_JW_BACK + JW.T / 2),
    ("payload", 50.0, 4, L1 + L2 + L3, Y_TIP),
]
S_JOINT = {0: -SX, 1: 0.0, 2: L1, 3: L1 + L2, 4: L1 + L2 + GRIP_DX}
print(f"arm model: Y horn faces {', '.join(f'{k} {v:.1f}' for k, v in Y_HORN.items())}; fingertip Y {Y_TIP:.1f}; "
      f"masses UL {M_UL:.1f} FA {M_FA:.1f} GB {M_GB:.1f} JW {M_JW:.1f} TT {M_TT:.1f} g; "
      f"CG x UL {CG_UL:.1f} FA {CG_FA:.1f} GB {CG_GB:.1f} (z {CGZ_GB:.1f}) JW {CG_JW:.1f}")


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
                 scaled down where a pitch servo (shoulder/elbow 1000, wrist 160) would backdrive first.
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
                    for J, st in ((S, STALL_MG996R_NMM), (E, STALL_MG996R_NMM), (W, STALL_SG90_NMM)):
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



# --- 20261025-arm-turntable-ring (round 2) ---------------------------------------------------------------
P = model_params("20261025-arm-turntable-ring")
WALL = P.R_OUT - P.R_IN
RING_R = (P.R_IN + P.R_OUT) / 2
CONTACT_ARC = 10.0          # contact length where the tilted turntable lands on the ring (assumed)
MU = 0.3
P_CLAMP = 100.0             # snug M3x6 self-tapper (build guide), no washer (assumed)
HEAD_D = 5.5
SEG = 2 * P.H               # wall segment that bends edgewise (45 deg spread over the height)
pts = {"disk": ((0, 0, TT.Z0), None, None)}
SW = {m: sweep(pts, m) for m in ("yaw", "hand")}
R_cases = [("20 N on the rim (spec)", 20.0), ("50 N proof on the rim (spec 8)", 50.0)] + \
    [(f"{lbl} ring catch", SW[m]["disk"]["Mx"] / (RING_R - MG996R.horn_d / 2))
     for m, lbl in (("yaw", "yaw-stall"), ("hand", "hand-push 5 N"))]
for lbl, R in R_cases:
    info = lbl.startswith("50 N")
    req = 1.5 if info else SF_STATIC
    check(f"{lbl}: ring wall bearing, R {R:.1f} N (compression)", R / (WALL * CONTACT_ARC), False, req, info=info)
    check(f"{lbl}: wall edgewise bending from friction {MU}R, {SEG:.0f} mm segment (Z, Kt 2.5)",
          6 * MU * R * P.H / (WALL * SEG ** 2), True, req, Kt=2.5, info=info)
    check(f"{lbl}: interlayer shear in the wall from friction", 1.5 * MU * R / (WALL * SEG), True, req, shear=True, info=info)
    check(f"{lbl}: tab bearing on the M3 shank from friction (one tab)", bearing(MU * R, 3.0, P.TAB_T), False, req, info=info)
    check(f"{lbl}: tab tear-out to its edge (e {P.TAB_D / 2})",
          tearout(MU * R, P.TAB_D / 2 - (P.TAB_HOLE + HOLE_COMP) / 2, P.TAB_T), False, req, shear=True, info=info)
A_head = math.pi / 4 * (HEAD_D ** 2 - (P.TAB_HOLE + HOLE_COMP) ** 2)
check(f"assembly: screw-head clamp {P_CLAMP:.0f} N on the tab, no washer (compression)", P_CLAMP / A_head, False, SF_STATIC)
worst, fails = report("20261025-arm-turntable-ring")

"""Strength check for jobs/20261025-arm-turntable-ring. Run: python3 jobs/20261025-arm-turntable-ring/strength_calc.py

strength-analyst, 2026-10-25. Plain python3 (no build123d): geometry is copied from model.py, and the section
properties were cross-checked against build123d sections of design() (printed "CAD" values).
Turntable ring: catch force when the turntable rocks onto it (spec 20 N, yaw-stall and hand-push cases), friction,
tab bearing and tear-out, screw clamp.
Units: N, mm, MPa, N.mm. Allowables are PETG placeholders (no measured row in library/materials.csv), so the best
possible verdict is NEEDS_TEST. Directions: "XY" = stress along the layers, "Z" = across the layers (or shearing them).
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

# --- arm model (assembly frame, yaw 0; assembly_plan.md) -----------------------------
# Servo datasheet values (tools/hobby_parts.py): MG996R 1000 N.mm / 55 g, SG90 160 N.mm / 9 g.
STALL_MG996R_NMM, STALL_SG90_NMM = 1000.0, 160.0
L1, L2, L3 = 100.0, 90.0, 95.0          # shoulder->elbow, elbow->wrist, wrist->fingertip
GRIP_DX = 40.0                          # wrist axis -> gripper servo axis
SX, SZ = 10.15, 60.5                    # shoulder axis X, Z
DESK_Z = -40.0
Y_HORN = {"shoulder": 11.5, "elbow": 32.0, "wrist": 46.4, "gripper": 60.8}   # horn faces (world Y)
Y_TIP = 61.3                            # fingertip / payload plane (jaw band Y 58.8-63.8)
F_HAND_N = 5.0                          # added handling case: hand push out of the arm plane at the fingertip
# Part masses = CAD volume (geometry.json) x 1.27 g/cm3; CG from design() (build123d centre of mass).
# (name, mass g, rides beyond joint k: 0 yaw, 1 shoulder, 2 elbow, 3 wrist, 4 gripper,
#  s = distance along the straight horizontal arm from the shoulder axis (mm), world Y (mm))
ITEMS = [
    ("shoulder MG996R", 55.0, 0, -10.15, -13.75),
    ("shoulder horn + screws", 4.0, 1, 0.0, 10.0),
    ("upper link", 21245.89 * RHO_G_PER_MM3, 1, 40.57, 12.56),
    ("elbow MG996R", 55.0, 1, 89.85, 6.75),
    ("cable allowance 1", 6.0, 1, 100.0, 20.0),
    ("elbow horn + screws", 4.0, 2, 100.0, 30.6),
    ("forearm", 12046.19 * RHO_G_PER_MM3, 2, 136.13, 32.57),
    ("wrist SG90", 9.0, 2, 184.65, 30.45),
    ("cable allowance 2", 4.0, 2, 190.0, 35.0),
    ("wrist horn + screw", 1.5, 3, 190.0, 45.6),
    ("gripper base", 15634.5 * RHO_G_PER_MM3, 3, 244.03, 49.77),
    ("gripper SG90", 9.0, 3, 224.65, 44.85),
    ("gripper horn + screw", 1.5, 4, 230.0, 60.0),
    ("moving jaw", 3390.04 * RHO_G_PER_MM3, 4, 254.47, 61.38),
    ("payload", 50.0, 4, 285.0, Y_TIP),
]
S_JOINT = {0: -SX, 1: 0.0, 2: L1, 3: L1 + L2, 4: L1 + L2 + GRIP_DX}   # joint positions along s


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



# --- 20261025-arm-turntable-ring: parameters copied from model.py ---------------------------------
R_IN, R_OUT, H = 41.0, 44.5, 13.0
TAB_R, TAB_D, TAB_T, TAB_HOLE = 48.0, 9.0, 3.0, 3.4
WALL = R_OUT - R_IN
RING_R = (R_IN + R_OUT) / 2
CONTACT_ARC = 10.0          # assumed contact length where the tilted turntable lands on the ring
MU = 0.3
P_CLAMP = 100.0             # snug M3 self-tapper, no washer (assumed)
HEAD_D = 5.5

pts = {"disk": ((0, 0, 14.5), None, None)}
SW = {m: sweep(pts, m) for m in ("yaw", "hand")}
R_cases = [("20 N on the rim (spec)", 20.0)] + \
    [(f"{lbl} ring catch", SW[m]["disk"]["Mx"] / (RING_R - 5.5)) for m, lbl in (("yaw", "yaw-stall"), ("hand", "hand-push 5 N"))]
for lbl, R in R_cases:
    print(f"{lbl}: R = {R:.1f} N")
    check(f"{lbl}: ring wall bearing (compression across layers), R {R:.1f} N", R / (WALL * CONTACT_ARC), False, SF_STATIC)
    # friction from the yawing turntable is tangential, i.e. in the plane of the wall: a 13 mm deep wall segment
    # (26 mm of arc, 45 deg spread) bends edgewise; stress along Z at the segment ends = across layers
    check(f"{lbl}: wall edgewise bending from friction {MU}R, 26 mm segment (Z, Kt 2.5)",
          6 * MU * R * H / (WALL * 26.0 ** 2), True, SF_STATIC, Kt=2.5)
    check(f"{lbl}: interlayer shear in the wall from friction (Z shear)", 1.5 * MU * R / (WALL * 26.0), True, SF_STATIC,
          shear=True)
    check(f"{lbl}: tab bearing on the M3 shank from friction (one tab)", bearing(MU * R, 3.0, TAB_T), False, SF_STATIC)
    check(f"{lbl}: tab tear-out to its edge (e 4.5)", tearout(MU * R, TAB_D / 2 - TAB_HOLE / 2, TAB_T), False, SF_STATIC,
          shear=True)
A_head = math.pi / 4 * (HEAD_D ** 2 - TAB_HOLE ** 2)
check(f"assembly: screw-head clamp {P_CLAMP:.0f} N on the tab, no washer (compression)", P_CLAMP / A_head, False, SF_STATIC)
worst, fails = report("20261025-arm-turntable-ring")

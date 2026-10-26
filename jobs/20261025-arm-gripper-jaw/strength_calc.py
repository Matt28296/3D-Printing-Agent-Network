"""Strength check for jobs/20261025-arm-gripper-jaw. Run: python3 jobs/20261025-arm-gripper-jaw/strength_calc.py

strength-analyst, 2026-10-25. Plain python3 (no build123d): geometry is copied from model.py, and the section
properties were cross-checked against build123d sections of design() (printed "CAD" values).
Moving jaw: horn-pocket bearing, bar in-plane bending under grip, horn arm-screw pull-out and out-of-plane bending
(yaw-stall sweep, 5 N hand push); what-if.
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



# --- 20261025-arm-gripper-jaw: parameters copied from model.py -----------------------------------
T, HUB_R_JAW, BAR_X1, BAR_Y0, BAR_Y1 = 5.0, 8.0, 55.0, -6.0, 5.5
HORN_DEPTH = 2.0
SG_HUB_R, SG_ARM_L, SG_TIP_R = 3.6, 14.0, 2.1         # SG90 single-arm horn
HS_D, HS_R = 1.6, 7.0          # horn arm screw: M2 self-tapping, pilot 1.6, innermost arm hole r 7 (assumed)
WASHER_D = 6.0
LEV_T = min(HS_R + SG_HUB_R, SG_ARM_L - HS_R)   # 7.0
LEV_TOR = SG_HUB_R
BW = BAR_Y1 - BAR_Y0                            # 11.5


def jaw_oop(x, t=T, bw=BW):
    """Out-of-plane I, c at x (CAD sections of design(): x8 Iyy 82 c 2.89, x16.5 Iyy 119)."""
    if x < SG_ARM_L + SG_TIP_R + 0.25:
        rh, rt = SG_HUB_R + 0.25, SG_TIP_R + 0.25
        wp = 2 * (rh - (rh - rt) * x / SG_ARM_L)
        rects = [(bw - wp, t, t / 2), (wp, t - HORN_DEPTH, HORN_DEPTH + (t - HORN_DEPTH) / 2)]
    else:
        rects = [(bw, t, t / 2)]
    A, zb, I = comp_section(rects)
    return I, max(zb, t - zb)


print(f"jaw_oop x8 {jaw_oop(8)[0]:.0f} (CAD 82), x16.5 {jaw_oop(16.5)[0]:.0f} (CAD 119)")
pts = {"horn": ("G", 2, (LEV_T, LEV_TOR)), "x8": (("G", 8.0, 0.0), 2, None), "x16": (("G", 16.5, 0.0), 2, None)}
SW = {m: sweep(pts, m) for m in ("yaw", "hand")}
for m in SW:
    print(f"{m:4s} sweep: " + "; ".join(f"{n} T={o['T']:.0f} Mt={o['Mt']:.0f} Fs={o['Fs']:.1f}" for n, o in SW[m].items()))

# 1. gripper stall into the single-arm pocket
F = STALL_SG90_NMM / (SG_ARM_L + SG_TIP_R - 2.0)
check("gripper stall 160 N.mm: horn-pocket wall bearing", bearing(F, 4.0, HORN_DEPTH), False, SF_STATIC)
# 2. in-plane bending of the bar by the grip force (fingertip 2.9 N or root 10.7 N)
F_tip, F_root = STALL_SG90_NMM / BAR_X1, STALL_SG90_NMM / 15.0
M8 = max(F_tip * (BAR_X1 - 8.0), F_root * (15.0 - 8.0))
check("gripper stall: bar in-plane bending x8 over the pocket (Kt 2.5)", bend(M8, 596.0, 5.81), False, SF_STATIC, Kt=2.5)
check("gripper stall: bar in-plane bending x16.5 pocket tip (Kt 1.5)", bend(F_tip * (BAR_X1 - 16.5), 631.0, 5.75), False,
      SF_STATIC, Kt=1.5)
check("10 N proof squeeze at the tip: bar in-plane bending x8 (Kt 2.5)", bend(10.0 * (BAR_X1 - 8.0), 596.0, 5.81), False,
      1.5, Kt=2.5, info=True)
# 3. horn joint (one arm screw; the centre screw head bears on the horn, not the jaw)
t_floor = T - HORN_DEPTH
check("grip reaction 2.9 N at the tip (in-plane, carried by the pocket walls)",
      bearing(F_tip * BAR_X1 / (SG_ARM_L + SG_TIP_R - 2.0), 4.0, HORN_DEPTH), False, SF_STATIC)
for m, lbl in (("yaw", "yaw-stall sweep"), ("hand", "hand push 5 N")):
    check(f"{lbl}: gripper horn arm-screw pull-out (floor {t_floor:.0f}, lever {LEV_T:.0f})",
          pullout(SW[m]["horn"]["Fs"], HS_D, t_floor), True, SF_STATIC, shear=True)
    I8, c8 = jaw_oop(8.0)
    I16, c16 = jaw_oop(16.5)
    check(f"{lbl}: out-of-plane bending x8 over the pocket (Kt 2 arm-screw hole)", bend(SW[m]["x8"]["Mt"], I8, c8),
          False, SF_STATIC, Kt=2.0)
    check(f"{lbl}: out-of-plane bending x16.5 at the pocket tip (Kt 1.5)", bend(SW[m]["x16"]["Mt"], I16, c16),
          False, SF_STATIC, Kt=1.5)

worst, fails = report("20261025-arm-gripper-jaw")

print("\nWHAT-IF  T 5->8 (floor 3->6), BAR_Y1 5.5->8.0 (bar 11.5->14 wide, matches the hub r 8) and the horn clamped by"
      " its centre screw (access hole 6.5 -> 2.4, M2x12 + OD6 washer):")
t2, bw2 = 8.0, 14.0
tf = t2 - HORN_DEPTH
a = allow_mpa(True, True)
cap_t = min(a * (math.pi * WASHER_D * tf * SG_HUB_R + math.pi * HS_D * tf * (HS_R + SG_HUB_R)),
            a * (math.pi * WASHER_D * tf * SG_ARM_L + math.pi * HS_D * tf * (SG_ARM_L - HS_R)))
cap_T = a * (math.pi * WASHER_D * tf + math.pi * HS_D * tf) * SG_HUB_R
pts2 = dict(pts)
pts2["horn"] = ("G", 2, (cap_t, cap_T))
wi = []
for m in ("yaw", "hand"):
    S = sweep(pts2, m)
    wi.append((f"{m}: clamped gripper horn joint", 1 / S["horn"]["Fs"]))
    for n, x, kt in (("x8", 8.0, 2.0), ("x16", 16.5, 1.5)):
        I, c = jaw_oop(x, t2, bw2)
        wi.append((f"{m}: out-of-plane bending {n}", allow_mpa(False) / (kt * bend(S[n]["Mt"], I, c))))
for n, sf in wi:
    print(f"  {n:40s} SF {sf:5.2f} {'OK' if sf >= 3 else 'FAIL'}")
print(f"  what-if lowest SF {min(sf for _, sf in wi):.2f}")

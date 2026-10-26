"""Strength check for jobs/20261025-arm-turntable. Run: python3 jobs/20261025-arm-turntable/strength_calc.py

strength-analyst, 2026-10-25. Plain python3 (no build123d): geometry is copied from model.py, and the section
properties were cross-checked against build123d sections of design() (printed "CAD" values).
Turntable: base-horn slot bearing, upright torsion and in-plane/out-of-plane bending (root, window bottom, lower
tab-pilot row), shoulder tab pilots, disk bending in front of the upright, base-horn arm-screw pull-out; what-if.
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



# --- geometry, copied from model.py (model.py needs build123d; this script runs on plain python3) -------
DISK_R, DISK_T, Z0 = 48.0, 5.0, 14.5
UP_T, UP_W, UP_Y = 5.0, 66.0, -5.0
GUSSET_T, GUSSET_X, GUSSET_LEN, GUSSET_H = 4.0, 30.5, 30.0, 50.0
ZS = 60.5
WIN_HALF_L = (40.7 + 0.4) / 2          # 20.55: window half length along X
WIN_HALF_H = (19.7 + 0.4) / 2          # 10.05: window half height (Z)
LIG_W = UP_W / 2 - WIN_HALF_L          # 12.45: ligament beside the window
LIG_XC = WIN_HALF_L + LIG_W / 2        # 26.78
PILOT_D, PILOT_X, PILOT_DZ = 2.6, 24.25, 5.0   # shoulder tab pilots (horizontal, along Y)
PILOT_LIG = PILOT_X - PILOT_D / 2 - WIN_HALF_L  # 2.40: pilot-to-window ligament
TAB_EDGE = 19.7 / 2                    # tab edge from the shoulder axis (Z)
HORN_DEPTH = 2.0
HUB_R, ARM_L, TIP_R = 5.5, 17.5, 2.75   # MG996R double-arm horn
# fastener assumptions (stated in strength.md)
HS_D, HS_R = 1.6, 15.0                  # horn arm screws: M2 self-tapping, pilot 1.6, in the outermost arm hole r 15
WASHER_D = 9.0                          # what-if clamp: M3 x 12 centre screw + DIN 9021 washer OD 9
RING_R = 42.75                          # ring mid radius
TOP = Z0 + DISK_T                       # 19.5: disk top
ROOT_Z = TOP + 0.1
MG_HOLES = [(-34.4, 5.0), (-34.4, -5.0), (14.1, 5.0), (14.1, -5.0)]   # tab holes rel. shaft (hobby_parts)


def gusset_len(z, top=TOP, g_h=GUSSET_H):
    return max(0.0, GUSSET_LEN * (1 - (z - top) / g_h))


def upright_x_section(z, up_t=UP_T, top=TOP, g_h=GUSSET_H):
    """Bending about X (stress varies with Y). Returns A, ybar, I, c_front, c_back (to the gusset toe)."""
    w = UP_W
    if ZS - WIN_HALF_H <= z <= ZS + WIN_HALF_H:
        w = 2 * LIG_W
        for zp in (ZS - PILOT_DZ, ZS + PILOT_DZ):
            if abs(z - zp) < PILOT_D / 2:
                w -= 2 * 2 * math.sqrt((PILOT_D / 2) ** 2 - (z - zp) ** 2)
    Lg = gusset_len(z, top, g_h)
    rects = [(w, up_t, UP_Y - up_t / 2)]
    if Lg > 0:
        rects.append((2 * GUSSET_T, Lg, UP_Y - up_t - Lg / 2))
    A, yb, I = comp_section(rects)
    return A, yb, I, UP_Y - yb, yb - (UP_Y - up_t - Lg)


def upright_y_I(z, up_t=UP_T, top=TOP, g_h=GUSSET_H):
    """In-plane bending about Y (stress along Z varies with X), c = 33."""
    Lg = gusset_len(z, top, g_h)
    if ZS - WIN_HALF_H <= z <= ZS + WIN_HALF_H:
        I = 2 * (up_t * LIG_W ** 3 / 12 + up_t * LIG_W * LIG_XC ** 2)
    else:
        I = up_t * UP_W ** 3 / 12
    I += 2 * (Lg * GUSSET_T ** 3 / 12 + Lg * GUSSET_T * GUSSET_X ** 2)
    return I


# CAD cross-check (build123d section of design(), 2026-10-25): Z19.6 A 569.5 I 60937 ybar -14.85; Z51 A 213.3 I 4530; Z56 A 165.3 I 2254
for z, cad in ((19.6, 60937), (51.0, 4530), (56.0, 2254)):
    A, yb, I, cf, cb = upright_x_section(z)
    print(f"section Z={z}: A={A:.1f} ybar={yb:.2f} Ixx={I:.0f} (CAD {cad}) c_front={cf:.2f} c_toe={cb:.2f}")
print(f"root Iyy={upright_y_I(19.6):.0f} (CAD 342923); window Iyy(60.5)={upright_y_I(60.5):.0f} (CAD 131107)")

# --- loads ---------------------------------------------------------------------------------
T_STALL = STALL_MG996R_NMM
X_TIP_MIN = 91.0     # nearest fingertip-on-desk reach (assembly plan)
M_SH_STALL = T_STALL * X_TIP_MIN / (X_TIP_MIN - SX) + weight_n(0) * SX   # shoulder stalls pressing the fingertip on the desk
M_W_YAW = sum(m * G_N_PER_G * (SX + s) for _, m, _, s, _ in beyond(0))    # arm weight about the yaw axis, horizontal arm
TT_MASS = 60649.79 * RHO_G_PER_MM3
TT_CG_Y = -4.36
F_PROOF = 9.81       # spec 8: 1 kg at the elbow axis
M_PROOF_Y = F_PROOF * (SX + L1) + M_W_YAW
print(f"M_y shoulder stall on desk = {M_SH_STALL:.0f} N.mm; arm weight about yaw axis = {M_W_YAW:.0f} N.mm static;"
      f" proof test about the base horn = {M_PROOF_Y:.0f} N.mm")

zf = lambda z: upright_x_section(z)[1]
pts = {"root": ((0, zf(ROOT_Z), ROOT_Z), None, None), "z51": ((0, zf(51.0), 51.0), None, None),
       "z55": ((0, zf(56.0), 55.5), None, None), "disk": ((0, 0, Z0), None, None)}
SW = {m: sweep(pts, m) for m in ("yaw", "hand")}
for m in SW:
    print(f"{m:4s} sweep: " + "; ".join(f"{n} Mx={o['Mx']:.0f} My={o['My']:.0f} Mz={o['Mz']:.0f}" for n, o in SW[m].items())
          + f"; max fingertip force {SW[m]['root']['F']:.2f} N")
W_OOP = {n: weight_oop_nmm(0, pts[n][0][1]) for n in pts}   # arm + shoulder servo; the turntable's own CG is below the sections

# 1. base-yaw stall: horn slot walls in bearing (outer 5 mm of each arm, 2 mm deep)
F_arm = T_STALL / (2 * (ARM_L + TIP_R - 2.5))
check("base stall 1000 N.mm: horn-slot wall bearing", bearing(F_arm, 5.0, HORN_DEPTH), False, SF_STATIC)
# 2. torsion of the upright (yaw stall, or yaw servo driving the arm into an obstacle)
check("yaw stall: upright torsion at root (open section)",
      torsion_thin(T_STALL, [(UP_W, UP_T), (GUSSET_LEN, GUSSET_T), (GUSSET_LEN, GUSSET_T)]), True, SF_STATIC, shear=True)
A, yb, I51, cf51, cb51 = upright_x_section(51.0)
F_lig = T_STALL / (2 * LIG_XC)
check("yaw stall: window ligament pair, Z51 toe", bend(F_lig * (ZS - 51.0), I51 / 2, cb51), True, SF_STATIC)
# 3. in-plane bending of the upright (stress along Z = across layers)
for lbl, M in (("shoulder stall on desk", M_SH_STALL), ("yaw sweep", SW["yaw"]["root"]["My"])):
    check(f"{lbl}: upright in-plane bending, root (Kt 2.5)", bend(M, upright_y_I(ROOT_Z), UP_W / 2), True, SF_STATIC, Kt=2.5)
    check(f"{lbl}: upright in-plane bending, window Z60.5 (Kt 2.5)", bend(M, upright_y_I(60.5), UP_W / 2), True, SF_STATIC, Kt=2.5)
# 4. out-of-plane bending of the upright (about X, stress along Z = across layers)
_, _, Ir, cfr, cbr = upright_x_section(ROOT_Z)
_, _, I56, cf56, cb56 = upright_x_section(56.0)
FR_FRONT56 = (ZS + TAB_EDGE - 56.0) / (ZS + TAB_EDGE - (ZS - PILOT_DZ))   # tab couple: push at Z70.35, pull at Z55.5
FR_BACK56 = (ZS + PILOT_DZ - 56.0) / (ZS + PILOT_DZ - (ZS - TAB_EDGE))   # pull at Z65.5, push at Z50.65
loads_x = [("weight x2 (sustained)", {n: DYN * abs(W_OOP[n]) for n in pts}, SF_SUSTAINED),
           ("yaw-stall sweep", {n: SW["yaw"][n]["Mx"] for n in pts}, SF_STATIC),
           ("hand push 5 N", {n: SW["hand"][n]["Mx"] for n in pts}, SF_STATIC)]
for lbl, M, req in loads_x:
    myr = SW["yaw"]["root"]["My"] if lbl.startswith("yaw") else 0.0
    sy = bend(myr, upright_y_I(ROOT_Z), UP_W / 2)   # same-load in-plane stress added at the corner (conservative)
    check(f"{lbl}: upright root, front face (Kt 2.5)", bend(M["root"], Ir, cfr) + sy, True, req, Kt=2.5)
    check(f"{lbl}: upright root, gusset toe (Kt 2.5)", bend(M["root"], Ir, cbr) + sy, True, req, Kt=2.5)
    check(f"{lbl}: Z51 window bottom, front face (Kt 2.5)", bend(M["z51"], I51, cf51), True, req, Kt=2.5)
    check(f"{lbl}: Z51 window bottom, gusset toe", bend(M["z51"], I51, cb51), True, req)
    check(f"{lbl}: Z56 lower tab-pilot row, front face (Kt 2 hole)", bend(FR_FRONT56 * M["z55"], I56, cf56), True, req, Kt=2.0)
    check(f"{lbl}: Z56 lower tab-pilot row, gusset toe", bend(FR_BACK56 * M["z51"], I56, cb56), True, req)
    # tab screws pulled out of the upright (horizontal pilots, threads shear the layers)
    check(f"{lbl}: shoulder tab screws pull-out (2 screws, L {UP_T:.0f})",
          pullout(M["z51"] / (PILOT_DZ + TAB_EDGE) / 2, PILOT_D, UP_T),
          True, req, shear=True)
    # disk plate bending in front of the upright (forward tip; the ring/hub supports are in front)
    check(f"{lbl}: disk at upright front face, b 66 (Kt 2.5)", M["disk"] / (UP_W * DISK_T ** 2 / 6), False, req, Kt=2.5)
# 5. shoulder-servo stall reaction into the upright pilots
Fs = max(servo_screw_forces(T_STALL, MG_HOLES))
check("shoulder stall: tab-pilot bearing (compression)", bearing(Fs, PILOT_D, UP_T), False, SF_STATIC)
check("shoulder stall: pilot-to-window ligament tear-out", tearout(Fs, PILOT_LIG, UP_T), True, SF_STATIC, shear=True)
# 6. base-horn joint: disk held on the horn only by the 2 arm screws (centre screw head sits on the horn)
t_floor = DISK_T - HORN_DEPTH
lev_y, lev_x = HS_R + ARM_L, 2 * HUB_R
for lbl, My, Mx, req in (("weight x2 (sustained)", DYN * M_W_YAW, DYN * abs(W_OOP["disk"]), SF_SUSTAINED),
                          ("shoulder stall on desk", M_SH_STALL, 0.0, SF_STATIC),
                          ("yaw-stall sweep", SW["yaw"]["disk"]["My"], SW["yaw"]["disk"]["Mx"], SF_STATIC),
                          ("hand push 5 N", 0.0, SW["hand"]["disk"]["Mx"], SF_STATIC)):
    F = My / lev_y + Mx / lev_x
    check(f"{lbl}: base-horn arm screw pull-out (floor {t_floor:.0f})", pullout(F, HS_D, t_floor), True, req, shear=True)
check("proof test (1 kg at elbow): base-horn arm screw", pullout(M_PROOF_Y / lev_y, HS_D, t_floor), True, 1.0, shear=True, info=True)
R_RING = max(SW[m]["disk"]["Mx"] for m in SW) / (RING_R - HUB_R)
print(f"ring catch force if the disk rocks onto the ring: {R_RING:.1f} N (used in the ring and base checks)")

worst, fails = report("20261025-arm-turntable")

# --- WHAT-IF: recommended geometry --------------------------------------------------------
print("\nWHAT-IF  DISK_T 5->8, UP_T 5->7, GUSSET_H 50->70, base horn clamped by its centre screw"
      " (access hole 6.5 -> 3.4, M3x12 + OD9 washer):")
dt, ut, gh = 8.0, 7.0, 70.0
top2 = Z0 + dt
rz = top2 + 0.1
yb2 = lambda z: upright_x_section(z, ut, top2, gh)[1]
pts2 = {"root": ((0, yb2(rz), rz), None, None), "z51": ((0, yb2(51.0), 51.0), None, None),
        "z55": ((0, yb2(56.0), 55.5), None, None), "disk": ((0, 0, Z0), None, None)}
SW2 = {m: sweep(pts2, m) for m in ("yaw", "hand")}
tf2 = dt - HORN_DEPTH
cap_x = allow_mpa(True, True) * (math.pi * WASHER_D * tf2 + 2 * math.pi * HS_D * tf2) * HUB_R
cap_y = allow_mpa(True, True) * (math.pi * WASHER_D * tf2 * ARM_L + math.pi * HS_D * tf2 * (HS_R + ARM_L))
wi = []
for m, req in (("yaw", SF_STATIC), ("hand", SF_STATIC)):
    S2 = SW2[m]
    _, _, Ir2, cf2, cb2 = upright_x_section(rz, ut, top2, gh)
    _, _, I512, cf512, cb512 = upright_x_section(51.0, ut, top2, gh)
    _, _, I562, cf562, _ = upright_x_section(56.0, ut, top2, gh)
    sy = bend(S2["root"]["My"], upright_y_I(rz, ut, top2, gh), UP_W / 2)
    rows = [("root front (Kt2.5)", 2.5 * (bend(S2["root"]["Mx"], Ir2, cf2) + sy), allow_mpa(True)),
            ("root toe (Kt2.5)", 2.5 * (bend(S2["root"]["Mx"], Ir2, cb2) + sy), allow_mpa(True)),
            ("Z51 front (Kt2.5)", 2.5 * bend(S2["z51"]["Mx"], I512, cf512), allow_mpa(True)),
            ("Z51 toe", bend(S2["z51"]["Mx"], I512, cb512), allow_mpa(True)),
            ("Z56 front (Kt2)", 2.0 * bend(FR_FRONT56 * S2["z55"]["Mx"], I562, cf562), allow_mpa(True)),
            ("disk at upright (Kt2.5)", 2.5 * S2["disk"]["Mx"] / (UP_W * dt ** 2 / 6), allow_mpa(False))]
    for n, s, a in rows:
        wi.append((f"{m}: {n}", a / s, req))
    u = S2["disk"]["My"] / cap_y + S2["disk"]["Mx"] / cap_x
    wi.append((f"{m}: clamped base-horn joint", 1 / u, req))
wi.append(("shoulder stall on desk: clamped base-horn joint", cap_y / M_SH_STALL, SF_STATIC))
u_w = DYN * M_W_YAW / cap_y + DYN * abs(W_OOP["disk"]) / cap_x
wi.append(("weight x2 (sustained): clamped base-horn joint", 1 / u_w, SF_SUSTAINED))
for n, sf, req in wi:
    print(f"  {n:50s} SF {sf:5.2f} (req {req:.0f}) {'OK' if sf >= req else 'FAIL'}")
print(f"  what-if lowest SF {min(sf for _, sf, _ in wi):.2f}")

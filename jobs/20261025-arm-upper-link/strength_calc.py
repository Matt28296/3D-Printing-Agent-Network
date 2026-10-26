"""Strength check for jobs/20261025-arm-upper-link. Run: python3 jobs/20261025-arm-upper-link/strength_calc.py

strength-analyst, 2026-10-25. Plain python3 (no build123d): geometry is copied from model.py, and the section
properties were cross-checked against build123d sections of design() (printed "CAD" values).
Upper link: shoulder-horn slot bearing, in-plane bending, elbow tab pilots, shoulder-horn arm-screw pull-out,
out-of-plane bending and torsion (yaw-stall sweep, 5 N hand push, weight); what-if.
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



# --- generic flat link on an MG996R double-arm horn (upper link / forearm) ----------------------------
HORN_DEPTH = 2.0
HUB_R, ARM_L, TIP_R = 5.5, 17.5, 2.75      # MG996R double-arm horn (hobby_parts)
HS_D, HS_R = 1.6, 15.0                     # horn arm screws: M2 self-tapping, drilled pilot 1.6, outermost arm hole r 15
WASHER_D = 9.0                             # what-if: M3 x 12 centre screw through a 3.4 hole + DIN 9021 washer OD 9


def r_pocket(x):
    """Half width of the double-arm horn pocket at distance x from the axis (hull of discs, +0.5 clearance)."""
    rh, rt = HUB_R + 0.25, TIP_R + 0.25
    x = abs(x)
    return max(rh - (rh - rt) * x / ARM_L, 0.0) if x <= ARM_L else (math.sqrt(max(rt ** 2 - (x - ARM_L) ** 2, 0)))


def oop_section(T, half_w, kind, x=0.0, slot_w=0.0, win_w=0.0):
    """Out-of-plane bending (about the link y axis, stress along x varies with z). Returns (I, c)."""
    if kind == "pocket":
        wp = 2 * r_pocket(x)
        rects = [(2 * half_w - wp, T, T / 2), (wp, T - HORN_DEPTH, HORN_DEPTH + (T - HORN_DEPTH) / 2)]
    elif kind == "slot":
        rects = [(2 * half_w - slot_w, T, T / 2)]
    elif kind == "window":
        rects = [(2 * half_w - win_w, T, T / 2)]
    else:
        rects = [(2 * half_w, T, T / 2)]
    A, zb, I = comp_section(rects)
    return I, max(zb, T - zb)


def inplane_I(T, half_w, cut_w=0.0):
    return T * ((2 * half_w) ** 3 - cut_w ** 3) / 12.0


def link_checks(P):
    """P: dict of link parameters. Adds rows to `cases`/`advisory`; returns data for the what-if."""
    T, HW = P["T"], P["HALF_W"]
    t_floor = T - HORN_DEPTH
    li = P["link_index"]
    J = P["joint"]
    pts = {"horn": (J, li, (HS_R + ARM_L, 2 * HUB_R)),
           "x15": ((J, 15.0, 0.0), li, None),
           "slot": ((J, P["LIGHT"][0], 0.0), li, None),
           "far": ((J, P["L"], 0.0), li, P["far_levers"]),
           "farrow": ((J, P["far_row_x"], 0.0), li, None)}
    SW = {m: sweep(pts, m) for m in ("yaw", "hand")}
    for m in SW:
        print(f"{m:4s} sweep: " + "; ".join(f"{n} T={o['T']:.0f} Mt={o['Mt']:.0f} Fs={o['Fs']:.1f}" for n, o in SW[m].items()))
    w_oop = weight_oop_nmm(P["k"], Y_HORN[P["horn_name"]])
    w_in = weight_inplane_nmm(P["k"])
    print(f"weight beyond the horn: in-plane {w_in:.0f} N.mm (horizontal), out-of-plane {w_oop:.0f} N.mm (pose independent)")

    # 1. horn stall through the slot walls
    F_arm = STALL_MG996R_NMM / (2 * (ARM_L + TIP_R - 2.5))
    check(f"{P['horn_name']} stall 1000 N.mm: horn-slot wall bearing", bearing(F_arm, 5.0, HORN_DEPTH), False, SF_STATIC)
    # 2. in-plane bending (strong axis) - bounded by the horn servo stall
    x0, x1, sw_ = P["LIGHT"]
    check(f"stall 1000 N.mm: in-plane bending at lightening slot (Kt 2)",
          bend(STALL_MG996R_NMM, inplane_I(T, HW, sw_), HW), False, SF_STATIC, Kt=2.0)
    check(f"stall: in-plane bending at the {P['far_name']} window, M {P['M_win']:.0f} (Kt 2.5)",
          bend(P["M_win"], inplane_I(T, HW, P["WIN_W"]), HW), False, SF_STATIC, Kt=2.5)
    check(f"weight x2 (sustained): in-plane bending at slot (Kt 2)",
          bend(DYN * w_in, inplane_I(T, HW, sw_), HW), False, SF_SUSTAINED, Kt=2.0)
    # 3. far servo stall reaction into its tab pilots (vertical pilots: bearing and tear-out are in-plane)
    Fs = max(servo_screw_forces(P["far_stall"], P["far_holes"]))
    check(f"{P['far_name']} stall: tab-pilot bearing", bearing(Fs, P["far_pilot"], T), False, SF_STATIC)
    check(f"{P['far_name']} stall: pilot-to-window ligament {P['far_lig']:.2f} tear-out (full F toward window)",
          tearout(Fs, P["far_lig"], T), False, SF_STATIC, shear=True)
    # 4. horn joint: link held on the horn only by its arm screws (centre screw head bears on the horn)
    check(f"weight x2 (sustained): horn arm-screw pull-out (floor {t_floor:.0f}, torsion lever {HUB_R})",
          pullout(DYN * abs(w_oop) / (2 * HUB_R), HS_D, t_floor), True, SF_SUSTAINED, shear=True)
    for m, lbl in (("yaw", "yaw-stall sweep"), ("hand", "hand push 5 N")):
        check(f"{lbl}: horn arm-screw pull-out (floor {t_floor:.0f})", pullout(SW[m]["horn"]["Fs"], HS_D, t_floor),
              True, SF_STATIC, shear=True)
    # 5. out-of-plane bending of the plate (weak axis; flat print -> stress along the layers)
    Ip, cp = oop_section(T, HW, "pocket", 15.0)
    Is, cs = oop_section(T, HW, "slot", slot_w=sw_)
    If, cf = oop_section(T, HW, "full")
    for m, lbl, req in (("w", "weight x2 (sustained)", SF_SUSTAINED), ("yaw", "yaw-stall sweep", SF_STATIC),
                        ("hand", "hand push 5 N", SF_STATIC)):
        Mx15 = DYN * abs(w_oop) if m == "w" else SW[m]["x15"]["Mt"]
        Msl = DYN * abs(w_oop) if m == "w" else SW[m]["slot"]["Mt"]
        Mfr = DYN * abs(w_oop) if m == "w" else SW[m]["farrow"]["Mt"]
        check(f"{lbl}: out-of-plane bending x15 over the pocket (Kt 2 arm-screw hole)", bend(Mx15, Ip, cp), False, req, Kt=2.0)
        check(f"{lbl}: out-of-plane bending at the lightening slot x{x0:.0f} (Kt 2)", bend(Msl, Is, cs), False, req, Kt=2.0)
        check(f"{lbl}: out-of-plane bending at the {P['far_name']} screw row x{P['far_row_x']:.1f} (Kt 2)",
              bend(Mfr, If * P["row_I_ratio"], cf), False, req, Kt=2.0)
        if m != "w":
            check(f"{lbl}: plate torsion at the slot (2 rails, Z shear)",
                  torsion_thin(SW[m]["slot"]["T"], [((2 * HW - sw_) / 2, T)] * 2), True, req, shear=True)
            check(f"{lbl}: {P['far_name']} tab screws pull-out", pullout(SW[m]["far"]["Fs"], P["far_pilot"], T),
                  True, req, shear=True)
            Iw, cw = oop_section(T, HW, "window", win_w=P["WIN_W"])
            Mw = SW[m]["farrow"]["Mt"]
            check(f"{lbl}: {P['far_name']} window rails alone, servo case ignored (Kt 2.5)", bend(Mw, Iw, cw), False, req,
                  Kt=2.5, info=True)
    return SW, pts


def link_whatif(P, T_new, clamp=True, slot=True):
    """Re-run the governing checks for a thicker plate and/or a centre-screw clamp at the horn."""
    T, HW = T_new, P["HALF_W"]
    tf = T - HORN_DEPTH
    a = allow_mpa(True, True)
    cap_T = a * ((math.pi * WASHER_D * tf if clamp else 0) + 2 * math.pi * HS_D * tf) * HUB_R
    cap_t = a * ((math.pi * WASHER_D * tf * ARM_L if clamp else 0) + math.pi * HS_D * tf * (HS_R + ARM_L))
    li, J = P["link_index"], P["joint"]
    pts = {"horn": (J, li, (cap_t, cap_T)), "x15": ((J, 15.0, 0.0), li, None),
           "slot": ((J, P["LIGHT"][0], 0.0), li, None), "farrow": ((J, P["far_row_x"], 0.0), li, None),
           "far": ((J, P["L"], 0.0), li, P["far_levers"])}
    rows = []
    for m in ("yaw", "hand"):
        S = sweep(pts, m)
        Ip, cp = oop_section(T, HW, "pocket", 15.0)
        rows.append((f"{m}: horn joint{' (clamped)' if clamp else ''}", 1.0 / S["horn"]["Fs"]))
        rows.append((f"{m}: x15 over pocket (Kt2)", allow_mpa(False) / (2 * bend(S["x15"]["Mt"], Ip, cp))))
        if slot:
            Is, cs = oop_section(T, HW, "slot", slot_w=P["LIGHT"][2])
            rows.append((f"{m}: lightening slot (Kt2)", allow_mpa(False) / (2 * bend(S["slot"]["Mt"], Is, cs))))
            rows.append((f"{m}: slot torsion", allow_mpa(True, True) /
                         torsion_thin(S["slot"]["T"], [((2 * HW - P["LIGHT"][2]) / 2, T)] * 2)))
        else:
            If, cf = oop_section(T, HW, "full")
            rows.append((f"{m}: x{P['LIGHT'][0]:.0f} no slot (Kt1)", allow_mpa(False) / bend(S["slot"]["Mt"], If, cf)))
            rows.append((f"{m}: torsion full width", allow_mpa(True, True) / torsion_thin(S["slot"]["T"], [(2 * HW, T)])))
        If, cf = oop_section(T, HW, "full")
        rows.append((f"{m}: {P['far_name']} screw row (Kt2)",
                     allow_mpa(False) / (2 * bend(S["farrow"]["Mt"], If * P["row_I_ratio"], cf))))
        rows.append((f"{m}: {P['far_name']} tab screws pull-out", allow_mpa(True, True) / pullout(S["far"]["Fs"], P["far_pilot"], T)))
    return rows

# --- 20261025-arm-upper-link: parameters copied from model.py --------------------------------------
P = dict(T=6.0, HALF_W=17.0, L=100.0, LIGHT=(26.0, 56.0, 14.0), WIN_W=20.1, link_index=0, joint="S", k=1,
         horn_name="shoulder", far_name="elbow MG996R", far_stall=STALL_MG996R_NMM,
         far_holes=[(-34.4, 5.0), (-34.4, -5.0), (14.1, 5.0), (14.1, -5.0)], far_pilot=2.6, far_lig=2.40,
         far_row_x=100.0 - 34.4, far_levers=(2 * 48.5, 2 * 14.85), row_I_ratio=523.0 / 612.0, M_win=STALL_MG996R_NMM)
# CAD cross-check (sections of design()): out-of-plane Iyy x14.5 549, slot 360, full 612, x66 523, window 250;
# in-plane Izz slot 18280, window 15592.
print(f"oop I x15 {oop_section(6, 17, 'pocket', 15.0)[0]:.0f} (CAD x14.5 549); slot {oop_section(6, 17, 'slot', slot_w=14)[0]:.0f} (CAD 360);"
      f" in-plane slot {inplane_I(6, 17, 14):.0f} (CAD 18280), window {inplane_I(6, 17, 20.1):.0f} (CAD 15592)")
SW, pts = link_checks(P)
worst, fails = report("20261025-arm-upper-link")
for lbl, Tn, clamp, slot in (("A: T 6->9, no lightening slot, centre-screw clamp", 9.0, True, False),
                             ("B: T 6->10, no lightening slot, centre-screw clamp", 10.0, True, False)):
    rows = link_whatif(P, Tn, clamp, slot)
    print(f"\nWHAT-IF {lbl}:")
    for n, sf in rows:
        print(f"  {n:40s} SF {sf:5.2f} {'OK' if sf >= 3 else 'FAIL'}")
    print(f"  what-if lowest SF {min(sf for _, sf in rows):.2f}")

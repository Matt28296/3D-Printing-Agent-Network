"""Strength check for jobs/20261025-arm-esp32-cradle. Run: python3 jobs/20261025-arm-esp32-cradle/strength_calc.py

strength-analyst, 2026-10-25. Plain python3 (no build123d): geometry is copied from model.py, and the section
properties were cross-checked against build123d sections of design() (printed "CAD" values).
ESP32 cradle: USB insertion into the far block and screws, jumper pull on the ledges and walls; what-if.
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

# --- 20261025-arm-esp32-cradle: parameters copied from model.py -----------------------------------
TOP, BOT, WALL, CLR = -10.0, -16.0, 2.5, 0.6
PCB_BOT = -11.6
HOLE = 3.4
FAR_X, FAR_BLOCK_X0 = 51.0 - 54.4, -13.0
USB_END_X = 51.0
H_FRAME = TOP - BOT                  # 6
LEDGE_H = PCB_BOT - BOT              # 4.4
F_USB = 20.0                         # micro-USB insertion (spec max 35 N; typical 10-20 N) - assumed
F_JUMPER = 10.0                      # pulling a bundle of female jumpers off the pins - assumed (spec: 5 N)
BOARD_G = 10.0

# 1. USB insertion pushes the board -X into the far block
check(f"USB insertion {F_USB:.0f} N: PCB edge bearing on the far block (1.6 x 28)", F_USB / (1.6 * 28.0), False, SF_STATIC)
check(f"USB insertion: M3 shank bearing in the far-block holes (2 of 3 share)", bearing(F_USB / 2, 3.0, H_FRAME), False,
      SF_STATIC)
check("USB insertion: far-block hole tear-out toward the pocket (e-r 3.7)", tearout(F_USB / 2, 3.7, H_FRAME), False,
      SF_STATIC, shear=True)
# 2. jumper pull-off pulls the board down onto the ledges
F_end = F_JUMPER / 2
# USB-end ledge: a 1.6 (x) x 4.4 (z) strip from the -Y wall (y 13.25) to y 42.5; the +Y wall stops at x 44 (pillar).
# The centre spine (8 x 4, 55 mm cantilever from the far block, k ~1.4 N/mm) is ~13x softer than the strip
# (k ~18 N/mm at y 28), so the strip works as a 29 mm cantilever from the -Y wall. PCB contact y 13.85-41.75.
STRIP_W, STRIP_L, STRIP_ARM = 1.6, 42.5 - 13.25, (41.75 + 13.85) / 2 - 13.25
for lbl, F in ((f"spec 5 N pull", 2.5), (f"jumper pull {F_JUMPER:.0f} N", F_end)):
    check(f"{lbl}, {F:.1f} N on the USB end: USB-end ledge strip, cantilever from the -Y wall (Kt 2.5)",
          F * STRIP_ARM / (STRIP_W * LEDGE_H ** 2 / 6), False, SF_STATIC, Kt=2.5)
# -Y wall (2.5 x 6) cantilevered from the x40 screw pad (edge x44.5) to the USB ledge centroid x50.2
check(f"jumper pull: -Y wall cantilever from the x40 pad (Kt 2.5)",
      6 * F_end * (50.2 - 44.5) / (WALL * H_FRAME ** 2), False, SF_STATIC, Kt=2.5)
# far ledge: a 2.8 mm step (4.4 tall) on the full-height far block, loaded along its 29.5 mm length
check("jumper pull: far-ledge root on the far block (cantilever 2.8, b 29.5, Kt 2.5)",
      6 * F_end * 1.4 / (29.5 * LEDGE_H ** 2), False, SF_STATIC, Kt=2.5)
# 3. sustained: board weight on the ledges (trivial) -> listed for completeness
check("board weight x2 (sustained): USB-end ledge strip", DYN * BOARD_G * G_N_PER_G / 2 * STRIP_ARM / (STRIP_W * LEDGE_H ** 2 / 6),
      False, SF_SUSTAINED, Kt=2.5)
worst, fails = report("20261025-arm-esp32-cradle")
print("\nWHAT-IF  USB-end ledge x 51-1.6 -> 51-2.8 (2.8 wide, still clear of the end-pin housings at x <= 48.0)"
      " and BOT -16 -> -20 (ledges 4.4 -> 8.4 tall; PCB_BOT unchanged):")
for lbl, F in (("spec 5 N pull", 2.5), (f"jumper pull {F_JUMPER:.0f} N", F_end)):
    sf = allow_mpa(False) / (2.5 * F * STRIP_ARM / (2.8 * 8.4 ** 2 / 6))
    print(f"  {lbl}: USB-end ledge strip SF {sf:.2f} {'OK' if sf >= 3 else 'FAIL'}")
print("note: M3x8 through the 6 mm frame leaves ~2 mm of thread in the base boss -> use M3x12 (boss pilot is 6 deep)")

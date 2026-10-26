"""Strength check for jobs/20261026-rover-lid (tracked rover, PETG), round 3.

Run from the project root with the CAD venv active (build123d, numpy):
    source /home/claude/.venv-cad/bin/activate
    python3 jobs/20261026-rover-lid/strength_calc.py

Round 3: the lid screws into heat-set inserts in the chassis columns (M3 x 8), carries the MTS-102 toggle (moved from
the rear wall) and has two cable slots either side of a 3 mm zip-tie bar instead of the Ø10 hole. The tie bar and the
rails are measured on the build123d solid. The lid only rests on the wall tops between its 4 corner screws, so a press
at a free edge (the window edge with its rail, a cable-slot edge) is checked with the classical plate-strip solution
(Kirchhoff plate, Lévy / Fourier series in x): free edge with an edge beam, simply supported at the wall. Rows tagged as
drop rows scale linearly with the drop height.
"""
# ===================== shared rover block, round 3 (identical in all six rover strength_calc.py) =====================
import json
import math
import os
import sys
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
JOBS = os.path.join(ROOT, "jobs")
ASM = os.path.join(JOBS, "20261026-rover-assembly")
for _p in (os.path.join(ROOT, "tools"), ASM):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import hobby_parts as HP  # noqa: E402  (needs the CAD venv: build123d)
import rover_frame as F   # noqa: E402  (the shared rover frame every rover model.py imports)

# --- allowables: library/materials.csv has only its header row, so the skill's placeholders apply ---------------------
ALLOW_INPLANE_MPA = 25.0   # PETG placeholder, already knocked down (strength-checks skill) -> best verdict NEEDS_TEST
Z_RATIO = 0.5              # across layers / in-plane (placeholder)
SHEAR_RATIO = 0.5          # shear allowable = 0.5 x normal allowable (Tresca; rounds 1-2 convention)
E_PETG_MPA, NU_PETG = 1800.0, 0.35
G_PETG_MPA = E_PETG_MPA / (2 * (1 + NU_PETG))
SF_STATIC, SF_CYCLIC, SF_METAL, SF_PROOF = 3.0, 4.0, 1.5, 1.0   # SF_PROOF: a proof load must not damage a good part
SY_129_MPA, SY_88_MPA, SY_A2_70_MPA = 1080.0, 640.0, 450.0
SY_ROD_MPA = 350.0         # unspecified steel rod and the N20 shaft: conservative yield (rounds 1-2 convention)
E_STEEL_MPA = 200000.0
G_MS2 = 9.81
D3_M3 = 2.387              # M3 minor diameter (fully threaded bolts bend on their thread)

# --- shared loads (round 3) -----------------------------------------------------------------------------------------
MASS_DESIGN_G = 649.0      # spec §4 of all six jobs. Round-3 estimate 618 g at the print_requirements minima (printed
                           # 315 g + bought 304 g; chassis strength_calc.py recomputes it); 713 g if every part were solid
T0_N = 5.0                 # pretension per run, sustained (spec §4). Deep review S-16: the guide's 3-5 mm sag over a
                           # 40 mm span is about 0.1 N, so 5 N is an over-tension bound, conservative for strength
T_DESIGN_NMM = 160.0       # spec §4 design stall; above the most a gated motor gives at the sketch's 6.0 V cap (130)
T_PROOF_NMM = 182.0        # chassis §8 gate: <= 371 g on a 50 mm arm at 100 % PWM on a fresh pack (stall proof tests)
V_CAP, V_FULL = 6.0, 8.4   # rover_test.ino: MOTOR_V 6.0, pwmCap = 255 x 6.0 / V_pack (182/255 on a full pack)
T_GATED_NMM = T_PROOF_NMM * V_CAP / V_FULL      # 130: a motor that passes the gate, at the sketch's cap
S08_6V_NMM = (("Pololu 150:1 LP 6V", 108.0), ("project N20_100RPM", HP.N20_100RPM.stall_torque_nmm),
              ("Phipps GA12-N20 6V 100 rpm", 196.0))   # deep review 04 S-08 (stall at 6 V)
OLD_CAP = 0.8 * V_FULL / V_CAP                  # S-08's 80 % cap on a full pack, relative to 6 V
MU_LONG = 1.0              # everyday pull, traction-limited (grousers on carpet; conservative)
SIDE_N = 3.0               # spec side drag per track; S-15 pivot turn on carpet needs <= 1.43 N per track half
H_DROP_MM = float(F.DROP_MM)
DELTA_MM, DELTA_STIFF_MM = 5.0, 2.5   # stopping distance (rounds 1-2 convention, spec §4) and its sensitivity

cases = []      # verdict rows: (name, dir, stress, allowable, SF, SF required, drop?)
advisory = []   # bounds, what-ifs, fixes, proof loads, bought parts: printed, not in the verdict


def allow_mpa(across, shear=False):
    return ALLOW_INPLANE_MPA * (Z_RATIO if across else 1.0) * (SHEAR_RATIO if shear else 1.0)


def check(name, stress_mpa, across, sf_req, shear=False, Kt=1.0, info=False, drop=False):
    """Printed PETG. across=True when the stress pulls layers apart or shears along a layer interface."""
    s = Kt * stress_mpa
    a = allow_mpa(across, shear)
    sf = a / s if s > 1e-9 else float("inf")
    (advisory if info else cases).append((name, ("Z" if across else "XY") + (" shear" if shear else ""), s, a, sf, sf_req,
                                          drop))
    return sf


def check_metal(name, stress_mpa, sy_mpa, sf_req=SF_METAL, info=False, drop=False):
    sf = sy_mpa / stress_mpa if stress_mpa > 1e-9 else float("inf")
    (advisory if info else cases).append((name, f"steel σy {sy_mpa:.0f}", stress_mpa, sy_mpa, sf, sf_req, drop))
    return sf


def check_custom(name, demand, capacity, tag, sf_req, info=False, drop=False):
    sf = capacity / demand if demand > 1e-9 else float("inf")
    (advisory if info else cases).append((name, tag, demand, capacity, sf, sf_req, drop))
    return sf


def bend_rect(M, b, h):
    return 6.0 * M / (b * h * h)


def bend_round(M, d):
    return 32.0 * M / (math.pi * d ** 3)


def bearing(Fn, d, t):
    return Fn / (d * t)


def tearout(Fn, ligament, t):
    return Fn / (2.0 * ligament * t)


def plate_boss_moment_stress(M, a, t, Kt=1.0):
    """Wall bending round a rigid boss of radius a carrying a moment M (rigid inclusion in a large plate):
    m_max = M / (2 pi a), sigma = Kt 6 m / t^2 (rounds 1-2 model)."""
    return Kt * 6.0 * (M / (2.0 * math.pi * a)) / (t * t)


def bef_beta(k, E, I):
    """Beam on elastic foundation: beta = (k / 4EI)^(1/4)."""
    return (k / (4.0 * E * I)) ** 0.25


def report(title):
    print(f"\n== {title} ==")
    print("| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |")
    print("|---|---|---|---|---|---|---|---|")
    for i, (n, d, s, a, sf, req, _) in enumerate(cases, 1):
        print(f"| {i} | {n} | {d} | {s:.2f} | {a:.1f} | {sf:.2f} | {req:.1f} | {'OK' if sf >= req else '**FAIL**'} |")
    if advisory:
        print("\nAdvisory (not in the verdict: bounds, what-ifs, fixes, proof loads, bought parts):")
        print("| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |")
        print("|---|---|---|---|---|---|---|")
        for n, d, s, a, sf, req, _ in advisory:
            print(f"| {n} | {d} | {s:.2f} | {a:.1f} | {sf:.2f} | {req:.1f} | {'OK' if sf >= req else 'no'} |")
    worst = min(cases, key=lambda r: r[4] / r[5])
    fails = [r for r in cases if r[4] < r[5]]
    print(f"\nlowest SF {worst[4]:.2f} (required {worst[5]:.1f}) at: {worst[0]}")
    drops = [r for r in cases if r[6]]
    if drops:
        lim = min(drops, key=lambda r: r[4] / r[5])
        h = H_DROP_MM * lim[4] / lim[5]
        print(f"drop rows scale with the height: all of them meet their SF up to a {h / 10:.1f} cm drop (design"
              f" {H_DROP_MM / 10:.0f} cm) on the {DELTA_MM:.0f} mm stopping-distance convention, limited by: {lim[0]}")
    print(f"{len(fails)} of {len(cases)} verdict rows below their required SF")
    print("VERDICT:", "FAIL" if fails else "NEEDS_TEST (placeholder allowables: PASS is not possible without measured data)")
    return worst, fails


def rover_loads(verbose=True):
    W = MASS_DESIGN_G * 1e-3 * G_MS2
    rp = F.RP
    L = SimpleNamespace(W=W, m_g=MASS_DESIGN_G)
    L.F_stall = T_DESIGN_NMM / rp                 # 9.89 N
    L.F_proof = T_PROOF_NMM / rp                  # 11.25 N
    L.F_gated = T_GATED_NMM / rp                  # 8.03 N
    L.T_tight_stall = T0_N + L.F_stall            # upper bound (slack-side relief ignored)
    L.T_tight_proof = T0_N + L.F_proof
    L.R_stall = L.T_tight_stall + T0_N            # sprocket: tight run + slack run
    L.R_idler_stall = 2 * L.T_tight_stall         # idler in reverse: both of its runs tight (spec §4)
    L.R_idler_proof = 2 * L.T_tight_proof
    L.F_trac = MU_LONG * W / 2.0                  # everyday pull per track
    L.T_tight_cyc = T0_N + L.F_trac
    L.R_cyc = L.T_tight_cyc + T0_N
    L.R_idler_cyc = 2 * L.T_tight_cyc
    L.R_sus = 2 * T0_N
    L.side = SIDE_N
    E = W * H_DROP_MM                             # N*mm
    L.E_drop = E
    L.drop_total = 2 * E / DELTA_MM               # linear spring, whole rover
    L.drop_flat_wheel = L.drop_total / 4          # flat: only the 4 road wheels touch (S-15: sprocket/idler 1.29 mm up)
    L.drop_corner = E / (2 * DELTA_MM)            # corner: half the mass on 2 axles
    L.drop = max(L.drop_flat_wheel, L.drop_corner)                  # 31.8 N: the per-axle drop load for every axle
    L.drop_stiff = L.drop * DELTA_MM / DELTA_STIFF_MM
    v = math.sqrt(2 * G_MS2 * H_DROP_MM * 1e-3)
    k_bolt = 3 * E_STEEL_MPA * (math.pi * D3_M3 ** 4 / 64) / (F.Y_T - F.HALF_W_OUT) ** 3   # N/mm, one M3 axle
    L.drop_elastic = v * math.sqrt(2 * k_bolt * 1e3 * MASS_DESIGN_G * 1e-3 / 2) / 2      # rigid floor, axles only
    L.s08 = [(n, t, t / rp, t * OLD_CAP / rp) for n, t in S08_6V_NMM]
    if verbose:
        print("== Shared rover loads (round 3) ==")
        print(f"mass {MASS_DESIGN_G:.0f} g (spec §4; round-3 estimate 618 g at the print minima, 713 g if solid): W = {W:.2f} N")
        print(f"stall: design {T_DESIGN_NMM:.0f} N*mm -> pull {L.F_stall:.2f} N at RP {rp:.2f}; proof {T_PROOF_NMM:.0f} N*mm ->"
              f" {L.F_proof:.2f} N; gated motor at the sketch's {V_CAP:.1f} V cap {T_GATED_NMM:.0f} N*mm -> {L.F_gated:.2f} N")
        print("S-08 motors (6 V stall -> pull at the 6.0 V cap / at the old 80 % cap on a full pack): "
              + "; ".join(f"{n} {t:.0f} N*mm -> {a:.1f} / {b:.1f} N" for n, t, a, b in L.s08))
        print(f"pretension T0 {T0_N:.0f} N/run (sustained); tight run at stall {L.T_tight_stall:.1f} N (proof"
              f" {L.T_tight_proof:.1f}), everyday {L.T_tight_cyc:.1f} N; sprocket radial stall {L.R_stall:.1f} / cyclic"
              f" {L.R_cyc:.1f} / sustained {L.R_sus:.0f} N; idler (reverse: both runs tight) stall {L.R_idler_stall:.1f}"
              f" (proof {L.R_idler_proof:.1f}) / cyclic {L.R_idler_cyc:.1f} / sustained {L.R_sus:.0f} N; side {SIDE_N:.0f} N")
        print(f"drop {H_DROP_MM / 10:.0f} cm: E {E / 1000:.3f} J, stopping distance {DELTA_MM:.0f} mm -> {L.drop_total:.0f} N in all;"
              f" flat on the 4 road wheels {L.drop_flat_wheel:.1f} N each, corner {L.drop_corner:.1f} N per axle -> {L.drop:.1f} N"
              f" per axle (any axle); {DELTA_STIFF_MM} mm -> {L.drop_stiff:.1f} N. Elastic check (rigid floor, M3 axles the"
              f" only spring, k {k_bolt:.0f} N/mm): about {L.drop_elastic:.0f} N per axle at a corner, so the convention relies on"
              f" floor, track, wheel and body compliance; the drop test is the evidence for the 5 cm rating")
    return L
# ===================== end of the shared block ========================================================================

# ==================================================================================================================
JOB = "20261026-rover-lid"
L = rover_loads()

import runpy  # noqa: E402

import numpy as np  # noqa: E402
from build123d import Vector  # noqa: E402

lns = runpy.run_path(os.path.join(JOBS, JOB, "model.py"), run_name="model")
p = SimpleNamespace(**{k: v for k, v in lns.items() if k.isupper()})
LID = lns["design"]()                                # rover world frame; deck underside at TOP_Z
TB, BB, BUCK = HP.TB6612_CARRIER, HP.MINI_BREADBOARD, HP.MP1584_BUCK

t = p.T
wall_in = F.HALF_W_OUT - F.WALL                      # 33.5: the lid rests on the wall tops
span = 2 * (F.HALF_W_OUT - F.WALL / 2)               # 71.5 between the side-wall centre lines
win_x0, win_x1 = p.USB_END_X + p.END_LEDGE, p.USB_END_X + p.LONG - p.END_LEDGE
win_len = win_x1 - win_x0                            # 49.6: free length of the window's long edges
cant = wall_in - p.HALF                              # strip beside the ESP32 window
rail_h = p.LEDGE_H + 1.6 + 0.5                       # rail height above the deck top
zm = F.TOP_Z + t / 2
# tie bar between the two cable slots, measured on the solid: |y| <= bar half width, x CABLE_X
bar_w = 2 * max(y for y in [i * 0.01 for i in range(300)] if LID.is_inside(Vector(sum(p.CABLE_X) / 2, y, zm)))
bar_L = p.CABLE_X[1] - p.CABLE_X[0] + p.HOLE_COMP
# rail cross-section on the solid at mid-window: |y| range of material above the deck top
z_rail = F.TOP_Z + t + rail_h / 2
ys_rail = [y for y in [p.HALF - 1 + i * 0.01 for i in range(600)] if LID.is_inside(Vector((win_x0 + win_x1) / 2, y, z_rail))]
print(f"\nlid: {t} mm deck on the {F.WALL} mm wall tops (span {span:.1f}); ESP32 window x {win_x0:.1f}..{win_x1:.1f}, strip beside"
      f" it {cant:.1f}; rails {p.RAIL_W} x {rail_h:.1f} (solid at mid-window: y {min(ys_rail):.2f}..{max(ys_rail):.2f}); tie bar"
      f" {bar_w:.2f} x {t} spanning {bar_L:.1f} (solid); screws at {p.SCREWS} into chassis inserts; toggle at {p.SWITCH}")

# --- the deck beside the window and the cable slots: plate strip with a free edge (classical Lévy / Fourier solution) ---
# The lid only rests on the wall tops between the 4 corner screws, so the deck can't cantilever from a side wall: it is
# simply supported there. A press at a free edge (the window edge with its rail, or a cable-slot edge) goes along the
# edge (x bending) and through plate twist to the wall. Model: Kirchhoff plate strip 0 <= y <= b, y = 0 the free edge
# carrying an edge beam (the rail), y = b simply supported on the wall centre line (conservative, as in L3).
D_DECK = E_PETG_MPA * t ** 3 / (12 * (1 - NU_PETG ** 2))


def _strip_W0(k, b, EIb, Pk, D=D_DECK):
    """Edge-deflection amplitude of one Fourier wave (wavenumber k). W(y) = (a1 + a2 y) e^-ky + (a3 + a4 (b-y)) e^-k(b-y);
    y = 0: M_y = 0 and edge beam D [W''' - (2 - nu) k^2 W'] + EIb k^4 W = Pk; y = b: W = 0, W'' = 0."""
    q, n = math.exp(-k * b), NU_PETG
    W, W1 = (1.0, 0.0, q, q * b), (-k, 1.0, q * k, q * (k * b - 1))
    W3 = (-k ** 3, 3 * k * k, q * k ** 3, q * (k ** 3 * b - 3 * k * k))
    A = np.array([[k * k * (1 - n), -2 * k, q * k * k * (1 - n), q * (k * k * b * (1 - n) - 2 * k)],
                  [D * (W3[i] - (2 - n) * k * k * W1[i]) + EIb * k ** 4 * W[i] for i in range(4)],
                  [q, q * b, 1.0, 0.0],
                  [q * k * k, q * (k * k * b - 2 * k), k * k, -2 * k]])
    a = np.linalg.solve(A, np.array([0.0, Pk, 0.0, 0.0]))
    return a[0] + q * (a[2] + a[3] * b)


def edge_curvature(P, b, EIb, c, a=None, mmax=4001, D=D_DECK):
    """Curvature of the free edge under the load P spread over |x| <= c. a=None: infinitely long strip (Fourier
    integral), i.e. no help from the deck beyond the ends of the free edge. a: strip simply supported across its whole
    width at x = 0 and a, load at a/2 (sine series), i.e. rigid ends."""
    def sinc(k):
        return math.sin(k * c) / (k * c) if c > 0 else 1.0
    if a is None:
        ks = np.geomspace(1e-7 / b, 2000.0 / b, 6000)
        return float(np.trapezoid([k * k * _strip_W0(k, b, EIb, P * sinc(k), D) for k in ks], ks)) / math.pi
    kap = 0.0
    for m in range(1, mmax, 2):
        k = m * math.pi / a
        s = math.sin(k * a / 2)
        kap += k * k * _strip_W0(k, b, EIb, 2 * P / a * s * sinc(k), D) * s
    return kap


def rail_section(w):
    """Rail w x rail_h standing on the deck, acting with a deck flange w + 2t: I, neutral-axis height, and the edge-beam
    stiffness the rail adds to the plate (the flange's own plate stiffness is already in the strip)."""
    bf = w + 2 * t
    A1, z1, A2, z2 = bf * t, t / 2, w * rail_h, t + rail_h / 2
    zb = (A1 * z1 + A2 * z2) / (A1 + A2)
    I = bf * t ** 3 / 12 + A1 * (zb - z1) ** 2 + w * rail_h ** 3 / 12 + A2 * (z2 - zb) ** 2
    return I, zb, E_PETG_MPA * (I - bf * t ** 3 / 12)


b_s = span / 2 - p.HALF                              # 20.9: window edge to the side-wall centre line
c_f = 2.5                                            # 5 mm fingertip contact along the edge (a 20 N fingertip spreads ~10 mm)
# model checks: (1) a very stiff edge beam must reproduce the 1-D model in which the strip turns rigidly about the wall
# (beam EI + D b/3, twist 2 D (1 - nu) / b); (2) with no plate the rigid-ends case must give the beam's P a / 4.
EI_chk = 1e7
lam = math.sqrt(2 * D_DECK * (1 - NU_PETG) / b_s / (EI_chk + D_DECK * b_s / 3))
k_ritz = 20.0 / (2 * lam) / (EI_chk + D_DECK * b_s / 3)
M_beam = EI_chk * edge_curvature(20.0, b_s, EI_chk, 0.0, a=win_len, D=1e-6)
print(f"plate-strip model checks: stiff edge beam / rigid-rotation model = {edge_curvature(20.0, b_s, EI_chk, 0.0) / k_ritz:.3f};"
      f" beam alone with rigid ends M = {M_beam:.1f} N*mm (P a / 4 = {20.0 * win_len / 4:.1f})")

F_hand = 20.0
I_r, zb_r, EIb_r = rail_section(p.RAIL_W)
ct_r = t + rail_h - zb_r
kap1 = edge_curvature(F_hand, b_s, EIb_r, c_f)
kap1_rigid = edge_curvature(F_hand, b_s, EIb_r, c_f, a=win_len)
kap1_pt = edge_curvature(F_hand, b_s, EIb_r, 0.0)
print(f"rail edge beam: composite I {I_r:.1f} mm^4, neutral axis {zb_r:.2f} above the deck bottom, rail top at {ct_r:.2f} from it;"
      f" strip width to the wall centre line {b_s:.2f}")
check(f"L1 rail at mid-window, hand {F_hand:.0f} N (5 mm fingertip): rail top, edge beam of a plate strip, window ends"
      f" ignored", E_PETG_MPA * kap1 * ct_r, False, SF_STATIC)
check(f"L1b deck bottom under the rail, same case (tension)", E_PETG_MPA * kap1 * zb_r, False, SF_STATIC)
M_end = F_hand * win_len / 8                         # rail edge beam fully fixed at the window ends, no plate share
check(f"L1c window corner (sharp, Kt 2.5): rail edge beam fixed at the window ends, PL/8 = {M_end:.0f} N*mm",
      M_end * max(zb_r, t + p.LEDGE_H - zb_r) / I_r, False, SF_STATIC, Kt=2.5)
a_slot = p.CABLE_X[1] - p.CABLE_X[0] + p.HOLE_COMP
b_slot = span / 2 - (p.CABLE_Y[1] + p.HOLE_COMP / 2)
kap2 = edge_curvature(F_hand, b_slot, 0.0, c_f, a=a_slot, mmax=20001)
check(f"L2 deck at a cable-slot edge, hand {F_hand:.0f} N (5 mm fingertip): free edge, slot ends ({a_slot:.1f} apart)"
      f" simply supported", E_PETG_MPA * kap2 * t / 2, False, SF_STATIC)
check(f"L3 deck at the breadboard centre, hand {F_hand:.0f} N (one-way, b_eff span/2)", bend_rect(F_hand * span / 4, span / 2, t),
      False, SF_STATIC)
check(f"L4 end-ledge bearing, {F_hand:.0f} N on the ESP32", (F_hand / 2) / (p.END_LEDGE * 2 * p.HALF), False, SF_STATIC)
# far end of the window: the deck between the far ledge and the cable slots carries the far ledge's share of a press on
# the seated ESP32 (spec: 20 N at mid-span -> 10 N per end ledge, spread over the board width) across to the side walls.
# One-way slab across the side walls (span 71.5) with b_eff = span/2 centred on the ledge (the L3 convention), net of
# the window and the slot openings, at the weakest band: |y| just past the tongue (ROW_KEEP), through the slots.
x_c = p.USB_END_X + p.LONG - p.END_LEDGE / 2 + p.CLR / 2          # far-ledge centre (67.5)
y_band = p.ROW_KEEP + 1.0
xs_probe = [x_c - span / 4 + i * 0.05 for i in range(int(span / 2 / 0.05) + 1)]


def _runs(z):
    """Material intervals along x at (y_band, z) on the solid, as (x0, x1) pairs."""
    inside = [LID.is_inside(Vector(x, y_band, z)) for x in xs_probe]
    runs, x0 = [], None
    for x, ins in zip(xs_probe, inside):
        if ins and x0 is None:
            x0 = x
        if not ins and x0 is not None:
            runs.append((x0, x)); x0 = None
    if x0 is not None:
        runs.append((x0, xs_probe[-1]))
    return runs


deck_runs = _runs(F.TOP_Z + t / 2)
ledge_runs = _runs(F.TOP_Z + t + p.LEDGE_H / 2)


def net_section(rects):
    """rects: (width, z0, z1) side by side in x, bending about a horizontal axis: I, neutral axis, extreme fibre."""
    A = sum(w * (z1 - z0) for w, z0, z1 in rects)
    zb = sum(w * (z1 - z0) * (z0 + z1) / 2 for w, z0, z1 in rects) / A
    I = sum(w * (z1 - z0) ** 3 / 12 + w * (z1 - z0) * ((z0 + z1) / 2 - zb) ** 2 for w, z0, z1 in rects)
    return I, max(max(z1 for _, _, z1 in rects) - zb, zb)


rects = [(b1 - a1, 0.0, t) for a1, b1 in deck_runs] + [(b1 - a1, t, t + p.LEDGE_H) for a1, b1 in ledge_runs]
I_n, c_n = net_section(rects)
strip_runs = [r for r in deck_runs if r[0] < x_c + 5]              # the strip behind the slots only
rects_A = [(b1 - a1, 0.0, t) for a1, b1 in strip_runs] + [(b1 - a1, t, t + p.LEDGE_H) for a1, b1 in ledge_runs]
I_A, c_A = net_section(rects_A)
w_board = 2 * (p.HALF - p.CLR - p.HOLE_COMP / 2)
F_ledge = F_hand / 2
y_m = p.ROW_KEEP                                     # the band starts at the tongue's edge: largest moment in it
M_band = F_ledge / 2 * (span / 2 - y_m) - F_ledge / w_board * (w_board / 2 - y_m) ** 2 / 2
print(f"far end, section probed at |y| {y_band:.1f}, x {xs_probe[0]:.1f}..{xs_probe[-1]:.1f} on the solid: deck {[(round(a, 1), round(b, 1)) for a, b in deck_runs]},"
      f" ledge {[(round(a, 1), round(b, 1)) for a, b in ledge_runs]}; I {I_n:.1f} mm^4 (strip alone {I_A:.1f}); M at |y| {y_m:.1f} {M_band:.0f} N*mm")
check(f"L4b deck between the far ledge and the cable slots, ESP32 press ({F_ledge:.0f} N on the far ledge): one-way slab,"
      f" b_eff span/2 net of the window and slots", M_band * c_n / I_n, False, SF_STATIC)
F_usb = 10.0
check(f"L5 window end face bearing, USB {F_usb:.0f} N (2 header strips 2.5 x 2.5)", F_usb / (2 * 2.5 * 2.5), False, SF_STATIC)
check(f"L6 side rail root, sideways jumper pull {F_usb:.0f} N over {p.SHORT / 2:.0f} mm (Z, Kt 2.5 sharp root)",
      bend_rect(F_usb * rail_h, p.SHORT / 2, p.RAIL_W), True, SF_STATIC, Kt=2.5)
lig = (p.HALF + p.RAIL_W + 1.5) - p.HALF            # 4.0: deck strip between the window edge and a tie slot (under the rail)
check(f"L7 zip-tie slot ligament ({lig:.1f} mm) shear, 20 N tie load", 20.0 / (2 * lig * t), False, SF_STATIC, shear=True)
F_bundle = 10.0
check(f"L8 tie bar, wire bundle pulled {F_bundle:.0f} N at mid-span (fixed ends, Kt 1.5 r{p.CABLE_R} corners)",
      bend_rect(F_bundle * bar_L / 8, bar_w, t), False, SF_STATIC, Kt=1.5)
F_scr = 2 * L.W / 4
A_head = math.pi / 4 * (F.SCREW_HEAD[0] ** 2 - (p.SCREW_D + p.HOLE_COMP) ** 2)
check(f"L9 screw-head bearing, rover lifted by the lid ({F_scr:.1f} N per M3 x 8)", F_scr / A_head, False, SF_STATIC)
check("L10 screw-hole push-through (plug shear, Z), lifted by the lid", F_scr / (math.pi * F.SCREW_HEAD[0] * t), True, SF_STATIC,
      shear=True)
# toggle: about 5 N at the lever tip, 13 mm above the deck; two M6 nuts clamp the deck round a Ø6.2 hole
M_tog = 5.0 * 13.0
check(f"L11 deck round the toggle bushing, flick {M_tog:.0f} N*mm (nut Ø10 boss in a plate, Kt 2 at the hole), cyclic",
      plate_boss_moment_stress(M_tog, 5.0, t, 2.0), False, SF_CYCLIC)
m_deck = json.load(open(os.path.join(JOBS, JOB, "geometry.json")))["volume_mm3"] * 1.27e-3
m_el = 10.0 + BB.mass_g + 3.0 + 2.5 + 6.0           # ESP32, breadboard, TB6612, buck, toggle
a_g = 2 * H_DROP_MM / DELTA_MM
q = (m_deck + m_el) * 1e-3 * G_MS2 * a_g / ((F.X_FRONT_OUT - F.X_REAR_OUT) * 2 * F.HALF_W_OUT)
check(f"L12 deck under its own and the electronics' inertia, 5 cm ({m_deck + m_el:.0f} g x {a_g:.0f} g)",
      bend_rect(q * span ** 2 / 8, 1.0, t), False, SF_STATIC, drop=True)
F_esp = 10.0e-3 * G_MS2 * a_g
check(f"L13 end ledge to deck, ESP32 inertia {F_esp:.1f} N, 5 cm (Z shear)", F_esp / (2 * p.END_LEDGE * 2 * p.HALF), True,
      SF_STATIC, shear=True, drop=True)
check(f"L14 screw-head bearing, deck inertia 5 cm ({(m_deck + m_el) * 1e-3 * G_MS2 * a_g / 4:.1f} N per screw)",
      (m_deck + m_el) * 1e-3 * G_MS2 * a_g / 4 / A_head, False, SF_STATIC, drop=True)

# advisory: bounds, proof loads (spec §8), the fix, assembly
check("L1 with rigid window ends (strip simply supported across x 16.4 and 66.0): upper bound of the end help",
      E_PETG_MPA * kap1_rigid * ct_r, False, SF_STATIC, info=True)
check("L1 with a point load on the rail (no fingertip spread)", E_PETG_MPA * kap1_pt * ct_r, False, SF_STATIC, info=True)
check("L4b with the strip behind the slots alone (no help from the deck in front of the slots)", M_band * c_A / I_A, False,
      SF_STATIC, info=True)
check("L2 with 2 mm contact (a fingernail or a tool edge, not a hand press)",
      E_PETG_MPA * edge_curvature(F_hand, b_slot, 0.0, 1.0, a=a_slot, mmax=20001) * t / 2, False, SF_STATIC, info=True)
check("proof (§8 test 1a) 40 N on the rail at mid-window (5 mm contact): rail top", 2 * E_PETG_MPA * kap1 * ct_r, False,
      SF_PROOF, info=True)
check("proof (§8 test 1b) 40 N at the breadboard centre", bend_rect(40.0 * span / 4, span / 2, t), False, SF_PROOF, info=True)
check("proof (§8 test 2) 20 N sideways on the seated ESP32: rail root", bend_rect(20.0 * rail_h, p.SHORT / 2, p.RAIL_W), True,
      SF_PROOF, Kt=2.5, info=True)
for w_fix in (3.5, 4.0, 4.5):
    I_f, zb_f, EIb_f = rail_section(w_fix)
    ct_f = t + rail_h - zb_f
    k_f = edge_curvature(F_hand, b_s, EIb_f, c_f)
    check(f"FIX RAIL_W {w_fix} (rails widen outward, tie slots move with them): L1 rail top", E_PETG_MPA * k_f * ct_f, False,
          SF_STATIC, info=True)
    if w_fix == 4.5:
        check(f"FIX RAIL_W {w_fix}: L1 with a point load", E_PETG_MPA * edge_curvature(F_hand, b_s, EIb_f, 0.0) * ct_f, False,
              SF_STATIC, info=True)
        check(f"FIX RAIL_W {w_fix}: L1b deck bottom under the rail", E_PETG_MPA * k_f * zb_f, False, SF_STATIC, info=True)
        check(f"FIX RAIL_W {w_fix}: L1c window corner (Kt 2.5)", M_end * max(zb_f, t + p.LEDGE_H - zb_f) / I_f, False,
              SF_STATIC, Kt=2.5, info=True)
        check(f"FIX RAIL_W {w_fix}: L6 rail root, sideways pull {F_usb:.0f} N", bend_rect(F_usb * rail_h, p.SHORT / 2, w_fix), True,
              SF_STATIC, Kt=2.5, info=True)
        check(f"FIX RAIL_W {w_fix}: L7 tie-slot ligament", 20.0 / (2 * (w_fix + 1.5) * t), False, SF_STATIC, shear=True, info=True)
        check(f"FIX RAIL_W {w_fix}: proof 40 N on the rail at mid-window", 2 * E_PETG_MPA * k_f * ct_f, False, SF_PROOF, info=True)
for T_nm, lab, A in ((0.15, "M3 x 8 lid screw, no washer", A_head), (0.5, "M3 x 8 lid screw, no washer", A_head),
                     (0.5, "M3 x 8 with an ISO 7089 washer", math.pi / 4 * (F.WASHER[0] ** 2 - 3.6 ** 2))):
    P_t = T_nm * 1000 / (0.2 * 3.0)
    check(f"assembly: {lab} at {T_nm} N*m (P {P_t:.0f} N), bearing on the deck", P_t / A, False, SF_STATIC, info=True)
A_nut6 = 10.0 ** 2 * math.sqrt(3) / 2 - math.pi / 4 * 6.4 ** 2
P6 = 0.6 * 1000 / (0.2 * 6.0)
check(f"assembly: toggle M6 nut at 0.6 N*m (P {P6:.0f} N) on the deck ({A_nut6:.0f} mm²)", P6 / A_nut6, False, SF_STATIC, info=True)
print(f"round-2 model of L1 for comparison (strip cantilevered from the side wall, 45° spread): {bend_rect(F_hand * cant, 2 * cant, t):.2f}"
      f" MPa. It needs a clamped root, and the deck only rests on the wall top there, so it isn't used")
z_esp_top = p.LEDGE_H + 1.6 + 4.0
print(f"note: ESP32 module and USB top {z_esp_top:.1f} mm above the deck against rails {rail_h:.1f}: an upside-down landing hits"
      f" the ESP32 first (not a design case at 5 cm the right way up)")

report(f"{JOB} strength checks")

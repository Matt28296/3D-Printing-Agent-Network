"""Strength check for jobs/20261026-rover-lid (tracked rover, PETG), round 4.

Run from the project root with the CAD venv active (build123d, numpy, scipy):
    source /home/claude/.venv-cad/bin/activate
    python3 jobs/20261026-rover-lid/strength_calc.py

Round 4 (strength round 3's required change): the window rails widen outward, RAIL_W 2.5 -> 4.5 (|y| 14.85-19.35), and
the ESP32 zip-tie slots move out with them to |y| 20.85-22.65, into the deck strip that carries a rail press to the wall.
Every round-3 case is re-run on the round-4 solid, and the slots are part of the checks:
- the rail press (L1) keeps round 3's verdict basis, the classical plate strip with the window ends ignored (Kirchhoff
  plate, Lévy / Fourier series in x, free edge carrying the rail as an edge beam, simply supported at the wall), times
  the factor by which cutting the tie-slot zones out of the strip raises the rail stress. That factor comes from the
  1-D rigid-rotation model of the same strip (round 3's model check), solved by finite differences;
- a press on the rail beside the tie slots (L1e) credits the window-end ledges at a lower-bound stiffness;
- a press on the deck outboard of the wider rail (L1d) uses the same plate strip with an interior load;
- the zip-tie strap (L7a-L7d) is checked at the tension that the spec's 20 N push from below puts in a nearly flat strap;
- the ligaments from the tie slots to the rail and to the wall, and the deck bands through the slots, are checked under
  the hand press, the ESP32 press and the drop.
Rows tagged as drop rows scale linearly with the drop height.
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
from scipy.sparse import diags  # noqa: E402
from scipy.sparse.linalg import splu  # noqa: E402

lns = runpy.run_path(os.path.join(JOBS, JOB, "model.py"), run_name="model")
p = SimpleNamespace(**{k: v for k, v in lns.items() if k.isupper()})
LID = lns["design"]()                                # rover world frame; deck underside at TOP_Z
TB, BB, BUCK = HP.TB6612_CARRIER, HP.MINI_BREADBOARD, HP.MP1584_BUCK

t = p.T
wall_in = F.HALF_W_OUT - F.WALL                      # 33.5: the lid rests on the wall tops
span = 2 * (F.HALF_W_OUT - F.WALL / 2)               # 71.5 between the side-wall centre lines
win_x0, win_x1 = p.USB_END_X + p.END_LEDGE, p.USB_END_X + p.LONG - p.END_LEDGE
win_len = win_x1 - win_x0                            # 49.6: free length of the window's long edges
x_mid = (win_x0 + win_x1) / 2                        # 41.2: mid-window
rail_h = p.LEDGE_H + 1.6 + 0.5                       # rail height above the deck top
rail_x0, rail_x1 = p.USB_END_X - p.CLR, p.USB_END_X + p.LONG + p.CLR     # 13.4, 69.0: the rails and the end ledges
zm = F.TOP_Z + t / 2


def solid(x, y, z=zm):
    return LID.is_inside(Vector(x, y, z))


# tie bar between the two cable slots, measured on the solid: |y| <= bar half width, x CABLE_X
bar_w = 2 * max(y for y in [i * 0.01 for i in range(300)] if solid(sum(p.CABLE_X) / 2, y))
bar_L = p.CABLE_X[1] - p.CABLE_X[0] + p.HOLE_COMP
# rail cross-section on the solid at mid-window: |y| range of material above the deck top
z_rail = F.TOP_Z + t + rail_h / 2
ys_rail = [y for y in [p.HALF - 1 + i * 0.01 for i in range(800)] if solid(x_mid, y, z_rail)]
# ESP32 zip-tie slots (round 4: 1.5 outside the wider rails). The 30- and 38-pin boards' far-end slots overlap, so they
# merge into one slot; each zone is confirmed on the solid (open through the deck, material either side of it).
tie_y0 = p.HALF + p.RAIL_W + 1.5                     # 20.85: slot inner edge
tie_y1 = tie_y0 + p.TIE_SLOT[1]                      # 22.65: slot outer edge
tie_xs = (p.USB_END_X + p.TIE_FROM_END, p.USB_END_X + p.SHORT - p.TIE_FROM_END, p.USB_END_X + p.LONG - p.TIE_FROM_END)
slot_zones = []
for xa, xb in sorted((x - p.TIE_SLOT[0] / 2, x + p.TIE_SLOT[0] / 2) for x in tie_xs):
    if slot_zones and xa <= slot_zones[-1][1]:
        slot_zones[-1] = (slot_zones[-1][0], max(xb, slot_zones[-1][1]))
    else:
        slot_zones.append((xa, xb))
y_tm = (tie_y0 + tie_y1) / 2
for xa, xb in slot_zones:
    for s in (1, -1):
        for xx in (xa + 0.05, (xa + xb) / 2, xb - 0.05):
            assert not solid(xx, s * y_tm) and solid(xx, s * (tie_y0 - 0.05)) and solid(xx, s * (tie_y1 + 0.05)), (xx, s)
        assert solid(xa - 0.05, s * y_tm) and solid(xb + 0.05, s * y_tm), (xa, xb, s)
lig_in = tie_y0 - p.HALF                             # 6.0: window edge to a tie slot (deck under the rail and beside it)
lig_rail = tie_y0 - (p.HALF + p.RAIL_W)              # 1.5: the rail's outer face to a tie slot
lig_wall = wall_in - tie_y1                          # 10.85: a tie slot to the wall's inner face
# the far slot zone runs past the window's far end: beside the open window the rail and its 6.0 mm deck strip form a
# "bridge" with the window inside it and the slot outside it, between the plate (x < 62.7) and the far ledge (x > 66.0)
bridge = [(max(xa, win_x0), min(xb, win_x1)) for xa, xb in slot_zones if min(xb, win_x1) - max(xa, win_x0) > 1.0][0]
x_tie30 = tie_xs[1]                                  # 64.3: the 30-pin board's far tie crosses the bridge
assert bridge[0] < x_tie30 < bridge[1]
assert solid(x_tie30, p.HALF + 0.05) and solid(x_tie30, tie_y0 - 0.05) and not solid(x_tie30, p.HALF - 0.3) \
    and not solid(x_tie30, tie_y0 + 0.3)
print(f"\nlid: {t} mm deck on the {F.WALL} mm wall tops (span {span:.1f}); ESP32 window x {win_x0:.1f}..{win_x1:.1f}; rails"
      f" {p.RAIL_W} x {rail_h:.1f} on the deck, x {rail_x0:.1f}..{rail_x1:.1f} (solid at mid-window: y {min(ys_rail):.2f}.."
      f"{max(ys_rail):.2f}); tie bar {bar_w:.2f} x {t} spanning {bar_L:.1f} (solid); screws at {p.SCREWS}; toggle at {p.SWITCH}")
print(f"tie slots (solid-checked): |y| {tie_y0:.2f}..{tie_y1:.2f}, x zones {[(round(a, 2), round(b, 2)) for a, b in slot_zones]}"
      f" (ties at x {', '.join(f'{x:.1f}' for x in tie_xs)}); ligaments: window edge to slot {lig_in:.2f}, rail to slot"
      f" {lig_rail:.2f}, slot to wall {lig_wall:.2f}; far-end bridge x {bridge[0]:.2f}..{bridge[1]:.2f}")

# --- the deck beside the window: plate strip with a free edge (classical Lévy / Fourier solution, round 3) ---------------
# The lid only rests on the wall tops between the 4 corner screws, so the deck can't cantilever from a side wall: it is
# simply supported there. A press at a free edge goes along the edge (x bending) and through plate twist to the wall.
# Model: Kirchhoff plate strip 0 <= y <= b, y = 0 the free edge carrying an edge beam (the rail), y = b simply supported
# on the wall centre line (conservative, as in L3).
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


def _g(s, k, n):
    """n-th derivative in s of e^-ks and of s e^-ks."""
    e = math.exp(-k * s)
    return {0: (e, s * e), 1: (-k * e, (1 - k * s) * e), 2: (k * k * e, (k * k * s - 2 * k) * e),
            3: (-k ** 3 * e, (3 * k * k - k ** 3 * s) * e)}[n]


def _rows(y, region, k, y0, b):
    """W, W', W'', W''' at y as rows over 8 coefficients. Region 1 (0..y0): (a1 + a2 y) e^-ky + (a3 + a4 (y0 - y))
    e^-k(y0 - y); region 2 (y0..b): (a5 + a6 (y - y0)) e^-k(y - y0) + (a7 + a8 (b - y)) e^-k(b - y)."""
    out = []
    for n in range(4):
        r = [0.0] * 8
        if region == 1:
            r[0], r[1] = _g(y, k, n)
            r[2], r[3] = [(-1) ** n * v for v in _g(y0 - y, k, n)]
        else:
            r[4], r[5] = _g(y - y0, k, n)
            r[6], r[7] = [(-1) ** n * v for v in _g(b - y, k, n)]
        out.append(np.array(r))
    return out


def interior_press(P, y0, b, EIb, c, D=D_DECK):
    """The same strip with the edge beam unloaded and the load P spread over |x| <= c on the line y = y0 (from the free
    edge; no spread across y, which is conservative for M_y): plate moments M_y, M_x (N*mm/mm) under the load centre and
    the free-edge curvature. Conditions: the round-3 edge conditions at y = 0 (no load), W, W', W'' continuous and
    D [W'''] = load at y0, W = W'' = 0 at y = b."""
    ks = np.geomspace(1e-6 / b, 4000.0 / b, 8000)
    My, Mx, kap = [], [], []
    for k in ks:
        Qk = P * math.sin(k * c) / (k * c)
        W0, W1, W2, W3 = _rows(0.0, 1, k, y0, b)
        r1, r2, rb = _rows(y0, 1, k, y0, b), _rows(y0, 2, k, y0, b), _rows(b, 2, k, y0, b)
        A = np.array([W2 - NU_PETG * k * k * W0, D * (W3 - (2 - NU_PETG) * k * k * W1) + EIb * k ** 4 * W0,
                      r2[0] - r1[0], r2[1] - r1[1], r2[2] - r1[2], D * (r2[3] - r1[3]), rb[0], rb[2]])
        a = np.linalg.solve(A, np.array([0.0, 0.0, 0.0, 0.0, 0.0, Qk, 0.0, 0.0]))
        Wy, W2y = r2[0] @ a, r2[2] @ a
        My.append(-D * (W2y - NU_PETG * k * k * Wy))
        Mx.append(-D * (-k * k * Wy + NU_PETG * W2y))
        kap.append(k * k * (W0 @ a))
    return tuple(float(np.trapezoid(v, ks)) / math.pi for v in (My, Mx, kap))


def rail_section(w):
    """Rail w x rail_h standing on the deck, acting with a deck flange w + 2t: I, neutral-axis height, and the edge-beam
    stiffness the rail adds to the plate (the flange's own plate stiffness is already in the strip)."""
    bf = w + 2 * t
    A1, z1, A2, z2 = bf * t, t / 2, w * rail_h, t + rail_h / 2
    zb = (A1 * z1 + A2 * z2) / (A1 + A2)
    I = bf * t ** 3 / 12 + A1 * (zb - z1) ** 2 + w * rail_h ** 3 / 12 + A2 * (z2 - zb) ** 2
    return I, zb, E_PETG_MPA * (I - bf * t ** 3 / 12)


def comp_section(w_rail, flange):
    """Rail on a deck strip `flange` wide, as one beam: I and neutral-axis height above the deck bottom."""
    A1, z1, A2, z2 = flange * t, t / 2, w_rail * rail_h, t + rail_h / 2
    zb = (A1 * z1 + A2 * z2) / (A1 + A2)
    return flange * t ** 3 / 12 + A1 * (zb - z1) ** 2 + w_rail * rail_h ** 3 / 12 + A2 * (z2 - zb) ** 2, zb


b_s = span / 2 - p.HALF                              # 20.9: window edge to the side-wall centre line
c_f = 2.5                                            # 5 mm fingertip contact along the edge (a 20 N fingertip spreads ~10 mm)
F_hand = 20.0
I_r, zb_r, EIb_r = rail_section(p.RAIL_W)
ct_r = t + rail_h - zb_r
I_g, zb_g = comp_section(p.RAIL_W, lig_in)           # beside a tie slot: the rail on its 6.0 mm deck strip only
ct_g = t + rail_h - zb_g
# model checks (round 3): a very stiff edge beam reproduces the 1-D model in which the strip turns rigidly about the wall
# (beam EI + D b/3, twist 2 D (1 - nu) / b); with no plate the rigid-ends case gives the beam's P a / 4
EI_chk = 1e7
lam_chk = math.sqrt(2 * D_DECK * (1 - NU_PETG) / b_s / (EI_chk + D_DECK * b_s / 3))
k_ritz = 20.0 / (2 * lam_chk) / (EI_chk + D_DECK * b_s / 3)
M_beam = EI_chk * edge_curvature(20.0, b_s, EI_chk, 0.0, a=win_len, D=1e-6)
print(f"plate-strip model checks: stiff edge beam / rigid-rotation model = {edge_curvature(20.0, b_s, EI_chk, 0.0) / k_ritz:.3f};"
      f" beam alone with rigid ends M = {M_beam:.1f} N*mm (P a / 4 = {20.0 * win_len / 4:.1f})")
kap1 = edge_curvature(F_hand, b_s, EIb_r, c_f)
kap1_rigid = edge_curvature(F_hand, b_s, EIb_r, c_f, a=win_len)
kap1_pt = edge_curvature(F_hand, b_s, EIb_r, 0.0)
s_levy = E_PETG_MPA * kap1 * ct_r                    # round 3's verdict basis: window ends ignored, no tie slots
print(f"rail edge beam: composite I {I_r:.1f} mm^4, neutral axis {zb_r:.2f} above the deck bottom, rail top at {ct_r:.2f} from it;"
      f" beside a tie slot (6.0 mm deck strip) I {I_g:.1f}, neutral axis {zb_g:.2f}, rail top at {ct_g:.2f}; strip width"
      f" to the wall centre line {b_s:.2f}")
_, _, kap_i0 = interior_press(F_hand, 0.05, b_s, EIb_r, c_f)
print(f"interior-load model check: the load 0.05 mm inside the free edge gives a rail-top stress {E_PETG_MPA * kap_i0 * ct_r:.3f}"
      f" MPa against {s_levy:.3f} with the load on the edge beam (ratio {kap_i0 / kap1:.4f})")

# --- 1-D model of the window strip, with the tie-slot zones cut out ----------------------------------------------------
# The strip turns about the wall line, so its edge deflection v(x) obeys (EI v'')'' - (S v')' = p (round 3's model
# check): EI = the rail edge beam + the strip's own x-bending (D b/3), S = 2 D (1 - nu) / b from the plate's twist.
# Where a tie slot cuts the strip (|y| 20.85-22.65) nothing outboard of it is joined to the rail: EI = the rail on its
# 6.0 mm deck strip, S = 0. Finite differences, 0.1 mm, v = 0 1.5 m away (the infinite strip of the verdict basis).
EI_strip = EIb_r + D_DECK * b_s / 3
S_strip = 2 * D_DECK * (1 - NU_PETG) / b_s
EI_gap = E_PETG_MPA * I_g
lam = math.sqrt(S_strip / EI_strip)
H1D = 0.1
x1 = np.arange(-1500.0, 1600.0 + H1D / 2, H1D)
on_rail = (x1 >= rail_x0) & (x1 <= rail_x1)


class Strip1D:
    def __init__(self, gaps=(), springs=()):
        n = len(x1)
        EI = np.full(n, EI_strip)
        S = np.full(n - 1, S_strip)
        xm = 0.5 * (x1[1:] + x1[:-1])
        gap = np.zeros(n, bool)
        for g0, g1 in gaps:
            gap |= (x1 >= g0 - 1e-9) & (x1 <= g1 + 1e-9)
            S[(xm >= g0) & (xm <= g1)] = 0.0
        EI[gap] = EI_gap
        D2 = diags([np.ones(n - 2), -2 * np.ones(n - 2), np.ones(n - 2)], [0, 1, 2], shape=(n - 2, n))
        D1 = diags([-np.ones(n - 1), np.ones(n - 1)], [0, 1], shape=(n - 1, n))
        K = ((D2.T @ diags(EI[1:-1]) @ D2) / H1D ** 3 + (D1.T @ diags(S) @ D1) / H1D).tolil()
        for xs, k in springs:
            K[int(np.argmin(np.abs(x1 - xs))), int(np.argmin(np.abs(x1 - xs)))] += k
        self.lu = splu(K.tocsc()[1:-1][:, 1:-1])
        self.EI = EI
        self.c_top = np.where(gap, ct_g, ct_r)

    def press(self, x0, P=F_hand, c=c_f):
        """Curvature and moment along x for a press P spread over |x - x0| <= c (c = 0: point load)."""
        load = np.where(np.abs(x1 - x0) <= c, P / (2 * c), 0.0) if c > 0 else np.where(
            np.arange(len(x1)) == np.argmin(np.abs(x1 - x0)), P / H1D, 0.0)
        v = np.zeros(len(x1))
        v[1:-1] = self.lu.solve(load[1:-1] * H1D)
        kap = np.zeros(len(x1))
        kap[1:-1] = (v[:-2] - 2 * v[1:-1] + v[2:]) / H1D ** 2
        return kap, self.EI * kap

    def rail_top(self, x0, P=F_hand, c=c_f):
        """Largest rail-top stress along the rail and where it is."""
        kap, _ = self.press(x0, P, c)
        sig = np.where(on_rail, np.abs(E_PETG_MPA * kap * self.c_top), 0.0)
        i = int(np.argmax(sig))
        return float(sig[i]), float(x1[i])


win_zones = [(max(a, win_x0), min(b, win_x1)) for a, b in slot_zones if min(b, win_x1) > max(a, win_x0)]
w_led = p.END_LEDGE + p.CLR                         # 3.0: each end ledge's length in x (x 13.4-16.4 and 66.0-69.0)
A1l, A2l = w_led * t, w_led * p.LEDGE_H
zl = (A1l * t / 2 + A2l * (t + p.LEDGE_H / 2)) / (A1l + A2l)
I_led = w_led * t ** 3 / 12 + A1l * (zl - t / 2) ** 2 + w_led * p.LEDGE_H ** 3 / 12 + A2l * (t + p.LEDGE_H / 2 - zl) ** 2
a_led = span / 2 - (p.HALF + p.RAIL_W / 2)           # 18.65: wall centre line to the rail centre line
k_led = 3 * E_PETG_MPA * I_led * span / (a_led ** 2 * (span - a_led) ** 2)
led_x = ((rail_x0 + win_x0) / 2, (win_x1 + rail_x1) / 2)        # 14.9, 67.5: the end ledges' centres
m_uni, m_gap, m_gapw = Strip1D(), Strip1D(slot_zones), Strip1D(win_zones)
m_led = Strip1D(slot_zones, [(xl, k_led) for xl in led_x])
k_an = F_hand / (2 * lam * EI_strip)
kap_pt, _ = m_uni.press(x_mid, c=0.0)
print(f"1-D strip: EI {EI_strip:.0f} N*mm^2 (beside a slot {EI_gap:.0f}), S {S_strip:.1f} N, decay length 1/lambda"
      f" {1 / lam:.1f} mm; point-load check: finite differences / analytic P/(2 lambda EI) ="
      f" {abs(kap_pt[np.argmin(np.abs(x1 - x_mid))]) / k_an:.4f}")
s_uni = m_uni.rail_top(x_mid)[0]
f_cal = max(1.0, s_levy / s_uni)                     # Lévy / 1-D at mid-window: applied to every 1-D result
f_slot = m_gap.rail_top(x_mid)[0] / s_uni            # tie-slot zones cut over their full length
f_slot_w = m_gapw.rail_top(x_mid)[0] / s_uni         # cut only where they lie beside the open window
print(f"1-D strip at mid-window: {s_uni:.3f} MPa (plate strip {s_levy:.3f}, factor {f_cal:.4f} applied to 1-D results); tie-slot"
      f" zones {[(round(a, 1), round(b, 1)) for a, b in slot_zones]} cut: x {f_slot:.4f} (only beside the window"
      f" {[(round(a, 1), round(b, 1)) for a, b in win_zones]}: x {f_slot_w:.4f})")
_, M_led_mid = m_led.press(x_mid)
M_corner = {xc: float(M_led_mid[np.argmin(np.abs(x1 - xc))]) for xc in (win_x0, win_x1)}
print(f"end ledges as springs (ledge {w_led:.1f} x {p.LEDGE_H:.0f} on the deck, I {I_led:.2f} mm^4, spanning the walls, load at |y|"
      f" {p.HALF + p.RAIL_W / 2:.2f}): {k_led:.2f} N/mm each at x {led_x[0]:.1f} and {led_x[1]:.1f} (a lower bound: the closed"
      f" deck beyond each window end is ignored); mid-window press: rail moment {abs(M_led_mid[np.argmin(np.abs(x1 - x_mid))]):.0f}"
      f" N*mm at mid-window (infinite strip {abs(m_uni.press(x_mid)[1][np.argmin(np.abs(x1 - x_mid))]):.0f}), at the window"
      f" corners {', '.join(f'{v:+.0f}' for v in M_corner.values())} N*mm (opposite sign: hogging), against P L/8 ="
      f" {F_hand * win_len / 8:.0f} used for L1c")

# --- L1 family: hand press on the rail beside the window ----------------------------------------------------------------
s_L1 = s_levy * f_slot
check(f"L1 rail at mid-window, hand {F_hand:.0f} N (5 mm fingertip): rail top, plate strip with the window ends ignored"
      f" (round 3 basis), tie-slot zones cut (x {f_slot:.3f})", s_L1, False, SF_STATIC)
check("L1b deck bottom under the rail, same case (tension)", E_PETG_MPA * kap1 * zb_r * f_slot, False, SF_STATIC)
M_end = F_hand * win_len / 8                         # rail fixed at the window ends, no plate share: bounds the corner moment
corner_I = [(I_g, zb_g) if any(a <= xc <= b for a, b in slot_zones) else (I_r, zb_r) for xc in (win_x0, win_x1)]
s_L1c = max(M_end * max(zb, t + p.LEDGE_H - zb) / I for I, zb in corner_I)
check(f"L1c window corners (sharp, Kt 2.5): rail fixed at the window ends, P L/8 = {M_end:.0f} N*mm, on the rail with its"
      f" {lig_in:.1f} mm deck strip (the tie slots run past both corners)", s_L1c, False, SF_STATIC, Kt=2.5)
y0s = np.arange(p.RAIL_W + 0.5, b_s - 0.9, 1.0)
L1d = []
for y0 in y0s:
    My, Mx, kp = interior_press(F_hand, float(y0), b_s, EIb_r, c_f)
    L1d.append((6 * max(abs(My), abs(Mx)) / t ** 2, float(y0), E_PETG_MPA * kp * ct_r))
s_L1d, y_L1d, s_L1d_rail = max(L1d)
check(f"L1d deck outboard of the rail at mid-window, hand {F_hand:.0f} N (5 mm fingertip), worst position |y|"
      f" {p.HALF + y_L1d:.1f}: plate moment under the load (rail top {s_L1d_rail:.2f} MPa)", s_L1d, False, SF_STATIC)
L1e = []
for a, b in slot_zones:
    for x0 in np.arange(max(rail_x0 + c_f, a - 8.0), min(rail_x1 - c_f, b + 2.0) + 1e-9, 0.25):
        L1e.append(m_led.rail_top(float(x0)) + (float(x0),))
s_L1e, x_L1e_max, x_L1e = max(L1e)
check(f"L1e rail beside the tie slots, hand {F_hand:.0f} N anywhere from 8 mm before a slot zone to its end (worst: press at x"
      f" {x_L1e:.1f}): slot zones cut, end ledges as lower-bound springs", s_L1e * f_cal, False, SF_STATIC)

# --- cable slots, breadboard, ESP32 seat (round 3 rows) and the tie-slot ligaments --------------------------------------
a_slot = p.CABLE_X[1] - p.CABLE_X[0] + p.HOLE_COMP
b_slot = span / 2 - (p.CABLE_Y[1] + p.HOLE_COMP / 2)
kap2 = edge_curvature(F_hand, b_slot, 0.0, c_f, a=a_slot, mmax=20001)
check(f"L2 deck at a cable-slot edge, hand {F_hand:.0f} N (5 mm fingertip): free edge, slot ends ({a_slot:.1f} apart)"
      f" simply supported", E_PETG_MPA * kap2 * t / 2, False, SF_STATIC)
a_tie = max(b - a for a, b in slot_zones)            # 6.1: the merged far-end tie slot
b_tie = span / 2 - tie_y1                            # 13.1: tie slot's outer edge to the wall centre line
c_tie = min(c_f, a_tie / 2)
kap2b = edge_curvature(F_hand, b_tie, 0.0, c_tie, a=a_tie, mmax=20001)
check(f"L2b slot-to-wall ligament ({lig_wall:.2f} mm to the wall face): hand {F_hand:.0f} N at a tie slot's outer edge, free"
      f" edge, slot ends ({a_tie:.1f} apart) simply supported", E_PETG_MPA * kap2b * t / 2, False, SF_STATIC)
check(f"L3 deck at the breadboard centre, hand {F_hand:.0f} N (one-way, b_eff span/2)", bend_rect(F_hand * span / 4, span / 2, t),
      False, SF_STATIC)
check(f"L4 end-ledge bearing, {F_hand:.0f} N on the ESP32", (F_hand / 2) / (p.END_LEDGE * 2 * p.HALF), False, SF_STATIC)
# far end of the window: the deck between the far ledge and the cable slots carries the far ledge's share of a press on
# the seated ESP32 (spec: 20 N at mid-span -> 10 N per end ledge, spread over the board width) across to the side walls.
# One-way slab across the side walls (span 71.5) with b_eff = span/2 centred on the ledge (the L3 convention), net of
# the window and the slot openings, at the weakest band (|y| just past the tongue) and at the tie-slot band.
x_c = p.USB_END_X + p.LONG - p.END_LEDGE / 2 + p.CLR / 2          # far-ledge centre (67.5)
xs_probe = [x_c - span / 4 + i * 0.05 for i in range(int(span / 2 / 0.05) + 1)]


def _runs(y, z):
    """Material intervals along x at (y, z) on the solid, as (x0, x1) pairs."""
    inside = [solid(x, y, z) for x in xs_probe]
    runs, x0 = [], None
    for x, ins in zip(xs_probe, inside):
        if ins and x0 is None:
            x0 = x
        if not ins and x0 is not None:
            runs.append((x0, x)); x0 = None
    if x0 is not None:
        runs.append((x0, xs_probe[-1]))
    return runs


def net_section(rects):
    """rects: (width, z0, z1) side by side in x, bending about a horizontal axis: I, neutral axis, extreme fibre."""
    A = sum(w * (z1 - z0) for w, z0, z1 in rects)
    zb = sum(w * (z1 - z0) * (z0 + z1) / 2 for w, z0, z1 in rects) / A
    I = sum(w * (z1 - z0) ** 3 / 12 + w * (z1 - z0) * ((z0 + z1) / 2 - zb) ** 2 for w, z0, z1 in rects)
    return I, max(max(z1 for _, _, z1 in rects) - zb, zb)


y_band = p.ROW_KEEP + 1.0
deck_runs = _runs(y_band, F.TOP_Z + t / 2)
ledge_runs = _runs(y_band, F.TOP_Z + t + p.LEDGE_H / 2)
rects = [(b1 - a1, 0.0, t) for a1, b1 in deck_runs] + [(b1 - a1, t, t + p.LEDGE_H) for a1, b1 in ledge_runs]
I_n, c_n = net_section(rects)
strip_runs = [r for r in deck_runs if r[0] < x_c + 5]              # the strip behind the slots only
rects_A = [(b1 - a1, 0.0, t) for a1, b1 in strip_runs] + [(b1 - a1, t, t + p.LEDGE_H) for a1, b1 in ledge_runs]
I_A, c_A = net_section(rects_A)
w_board = 2 * (p.HALF - p.CLR - p.HOLE_COMP / 2)
F_ledge = F_hand / 2
y_m = p.ROW_KEEP                                     # the band starts at the tongue's edge: largest moment in it
M_band = F_ledge / 2 * (span / 2 - y_m) - F_ledge / w_board * (w_board / 2 - y_m) ** 2 / 2
tie_runs = _runs(y_tm, F.TOP_Z + t / 2)
I_t4, c_t4 = net_section([(b1 - a1, 0.0, t) for a1, b1 in tie_runs])
M_tie = F_ledge / 2 * (span / 2 - tie_y0)            # outside the board's width the moment falls linearly to the wall
print(f"far end, sections probed on the solid over x {xs_probe[0]:.1f}..{xs_probe[-1]:.1f}: at |y| {y_band:.1f} deck"
      f" {[(round(a, 1), round(b, 1)) for a, b in deck_runs]}, ledge {[(round(a, 1), round(b, 1)) for a, b in ledge_runs]},"
      f" I {I_n:.1f} mm^4 (strip alone {I_A:.1f}), M at |y| {y_m:.1f} {M_band:.0f} N*mm; through the tie slots (|y| {y_tm:.2f})"
      f" deck {[(round(a, 1), round(b, 1)) for a, b in tie_runs]}, I {I_t4:.1f}, M at |y| {tie_y0:.2f} {M_tie:.0f} N*mm")
check(f"L4b deck between the far ledge and the cable slots, ESP32 press ({F_ledge:.0f} N on the far ledge): one-way slab,"
      f" b_eff span/2 net of the window and slots", M_band * c_n / I_n, False, SF_STATIC)
check(f"L4c same press, deck band through the far tie slots (Kt 2.5 at the square slot ends)", M_tie * c_t4 / I_t4, False,
      SF_STATIC, Kt=2.5)
F_usb = 10.0
check(f"L5 window end face bearing, USB {F_usb:.0f} N (2 header strips 2.5 x 2.5)", F_usb / (2 * 2.5 * 2.5), False, SF_STATIC)
check(f"L6 side rail root, sideways jumper pull {F_usb:.0f} N over {p.SHORT / 2:.0f} mm (Z, Kt 2.5 sharp root)",
      bend_rect(F_usb * rail_h, p.SHORT / 2, p.RAIL_W), True, SF_STATIC, Kt=2.5)

# --- the ESP32 zip-tie strap (L7): spec §4 "jumpers pushed on from below, 20 N" -----------------------------------------
# Each tie runs over the board's end, over both rails, down through a tie slot, under the deck to the other slot. The
# board's highest part under the far tie (the module's 0.8 mm antenna PCB, about 0.3 mm above the rail tops) leaves the
# strap almost flat, so a push P from below is held by T = P / (2 sin phi): the board lifts until the tie's stretch has
# raised phi enough. Assumptions: ESP32-WROOM module 18 mm wide; micro-USB receptacle about 2.5 mm tall and 7.8 wide at
# the USB end; a 2.5 x 1.0 mm PA66 strap (E 2500 MPa) pulled snug by hand (25 N); the whole push on one tie.
P_push = 20.0
W_TIE, TH_TIE, E_NYLON, T0_TIE = 2.5, 1.0, 2500.0, 25.0
T_TIE_RATED = 80.0                                   # 2.5 mm miniature ties: 18 lb (8 kg) rated loop strength
dz_side = math.hypot(lig_rail, rail_h)               # rail's outer top corner to the slot's top inner edge
L_loop = 2 * p.HALF + 2 * p.RAIL_W + 2 * (dz_side + t) + 2 * tie_y0
k_tie = E_NYLON * W_TIE * TH_TIE / L_loop


def strap_tension(P, h0, a):
    """Strap held h0 above the rail tops by the board, reaching the rail corner a away: tension and angle at which the
    push P is held. Below 2 T0 sin(phi0) the board doesn't lift and the strap stays at T0."""
    s0 = math.hypot(a, h0)

    def held(d):
        s = math.hypot(a, h0 + d)
        T = T0_TIE + k_tie * 2 * (s - s0)
        return 2 * T * (h0 + d) / s, T, math.atan2(h0 + d, a)
    if held(0.0)[0] >= P:
        return T0_TIE, 0.0, held(0.0)[2]
    lo, hi = 0.0, 20.0
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if held(mid)[0] < P else (lo, mid)
    return held(hi)[1], hi, held(hi)[2]


top_board = p.LEDGE_H + 1.6                          # PCB top above the deck top (rails at rail_h)
T_far, d_far, phi_far = strap_tension(P_push, top_board + 0.8 - rail_h, p.HALF - 9.0)
T_usb, d_usb, phi_usb = strap_tension(P_push, top_board + 2.5 - rail_h, p.HALF - 3.9)
T_strap = max(T_far, T_usb)
print(f"zip-tie strap: loop {L_loop:.0f} mm, k {k_tie:.0f} N/mm, snug {T0_TIE:.0f} N; a {P_push:.0f} N push lifts the board"
      f" {d_far:.2f} mm at the far end (strap at {math.degrees(phi_far):.1f}°, T {T_far:.1f} N) and {d_usb:.2f} mm at the USB end"
      f" ({math.degrees(phi_usb):.1f}°, T {T_usb:.1f} N): design tension {T_strap:.1f} N ({T_strap / P_push:.1f} x the push); the"
      f" tie itself breaks at about {T_TIE_RATED:.0f} N")
# forces on one side (+y), z from the deck bottom: rail inner top corner, rail outer top corner, slot top and bottom
# inner edges. The strap pulls the slot's inner side inward with (1 + uy) T and the whole side inward with T (1 + cos phi).
uy, uz = lig_rail / dz_side, -rail_h / dz_side
bA_d, bA_r = lig_in * t, p.RAIL_W * rail_h           # bridge: the deck strip and the rail on it
by_d, by_r = p.HALF + lig_in / 2, p.HALF + p.RAIL_W / 2
bz_d, bz_r = t / 2, t + rail_h / 2
y_c = (bA_d * by_d + bA_r * by_r) / (bA_d + bA_r)
z_c = (bA_d * bz_d + bA_r * bz_r) / (bA_d + bA_r)
Iz_b = t * lig_in ** 3 / 12 + bA_d * (by_d - y_c) ** 2 + rail_h * p.RAIL_W ** 3 / 12 + bA_r * (by_r - y_c) ** 2
cy_b = max(y_c - p.HALF, tie_y0 - y_c)


def strap_torque(T, phi):
    pts = (((p.HALF, t + rail_h), (1 - math.cos(phi), math.sin(phi))), ((p.HALF + p.RAIL_W, t + rail_h), (-1 + uy, uz)),
           ((tie_y0, t), (-uy, -uz - 1)), ((tie_y0, 0.0), (-1.0, 1.0)))
    return T * sum((y - y_c) * fz - (z - z_c) * fy for (y, z), (fy, fz) in pts)


def rect_torsion(b, h):
    """Rectangle b >= h: (alpha, beta, short-side / long-side stress) for tau_max = T / (alpha b h^2), J = beta b h^3."""
    r = max(b, h) / min(b, h)
    tab = ((1.0, 0.208, 0.141, 1.0), (1.5, 0.231, 0.196, 0.859), (2.0, 0.246, 0.229, 0.795), (3.0, 0.267, 0.263, 0.753),
           (4.0, 0.282, 0.281, 0.745), (10.0, 0.312, 0.312, 0.742), (1e9, 0.333, 0.333, 0.742))
    for (r0, a0, b0, s0), (r1, a1, b1, s1) in zip(tab, tab[1:]):
        if r0 <= r <= r1:
            f = (r - r0) / (r1 - r0)
            return a0 + f * (a1 - a0), b0 + f * (b1 - b0), s0 + f * (s1 - s0)


parts = [(max(lig_in, t), min(lig_in, t)), (max(p.RAIL_W, rail_h), min(p.RAIL_W, rail_h))]
J_parts = [rect_torsion(b, h)[1] * b * h ** 3 for b, h in parts]
a_b, b_b = x_tie30 - bridge[0], bridge[1] - x_tie30
L_b = bridge[1] - bridge[0]


def bridge_rows(T, tag, sf_req, info):
    F_in = 2 * T                                     # both strands pull the slot's side inward (cos phi taken as 1)
    check(f"L7a{tag} tie-slot ligament ({lig_in:.1f} mm, window edge to slot, deck only) shear-out, strap pull 2 x {T:.0f} N",
          tearout(F_in, lig_in, t), False, sf_req, shear=True, info=info)
    M_fix = F_in * max(a_b * b_b ** 2, a_b ** 2 * b_b) / L_b ** 2
    M_mid = 2 * F_in * a_b ** 2 * b_b ** 2 / L_b ** 3
    check(f"L7b{tag} far-end bridge (x {bridge[0]:.1f}-{bridge[1]:.1f}: rail on the {lig_in:.1f} mm strip) bent in-plane by the"
          f" 30-pin tie's 2 x {T:.0f} N, fixed ends, Kt 2.5 at the sharp corners", max(2.5 * M_fix, M_mid) * cy_b / Iz_b, False,
          sf_req, info=info)
    if not info:
        Mt = max(abs(strap_torque(T, phi_far)), abs(strap_torque(T, math.atan2(top_board + 0.8 - rail_h, p.HALF - 9.0))))
        Mt_end = Mt * max(a_b, b_b) / L_b
        tau = [Mt_end * Jp / sum(J_parts) / (rect_torsion(b, h)[0] * b * h * h) for (b, h), Jp in zip(parts, J_parts)]
        tau_z = [tp * rect_torsion(b, h)[2] for (b, h), tp in zip(parts, tau)]
        check(f"L7c bridge twisted by the strap's wrap ({Mt:.1f} N*mm, {Mt_end:.1f} at one end): long faces", max(tau), False,
              sf_req, shear=True)
        check("L7c' same, short faces (shear along the layers)", max(tau_z), True, sf_req, shear=True)
    check(f"L7d{tag} strap bearing on a tie slot's inner wall ({1 + uy:.2f} x {T:.0f} N on {W_TIE} x {t:.0f})",
          bearing((1 + uy) * T, W_TIE, t), False, sf_req, info=info)


bridge_rows(T_strap, "", SF_STATIC, False)
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
check(f"L12b same, at the tie slots' inner edge (|y| {tie_y0:.2f}), net of the {a_tie:.1f} mm slot in a span/2 band, Kt 2.5",
      bend_rect(q / 2 * ((span / 2) ** 2 - tie_y0 ** 2), 1.0, t) * (span / 2) / (span / 2 - a_tie), False, SF_STATIC, Kt=2.5,
      drop=True)
F_esp = 10.0e-3 * G_MS2 * a_g
check(f"L13 end ledge to deck, ESP32 inertia {F_esp:.1f} N, 5 cm (Z shear)", F_esp / (2 * p.END_LEDGE * 2 * p.HALF), True,
      SF_STATIC, shear=True, drop=True)
check(f"L14 screw-head bearing, deck inertia 5 cm ({(m_deck + m_el) * 1e-3 * G_MS2 * a_g / 4:.1f} N per screw)",
      (m_deck + m_el) * 1e-3 * G_MS2 * a_g / 4 / A_head, False, SF_STATIC, drop=True)

# --- advisory: bounds, what-ifs, proof loads (spec §8), the tie's own strength, assembly ----------------------------------
check("L1 round 3's basis on the round-4 rails, no tie slots (for comparison)", s_levy, False, SF_STATIC, info=True)
check(f"L1 with the tie-slot zones cut only beside the open window (x {f_slot_w:.3f})", s_levy * f_slot_w, False, SF_STATIC,
      info=True)
check("L1 with rigid window ends (strip simply supported across x 16.4 and 66.0): upper bound of the end help",
      E_PETG_MPA * kap1_rigid * ct_r, False, SF_STATIC, info=True)
check(f"L1 with the end ledges as lower-bound springs ({k_led:.1f} N/mm) and the slot zones cut, mid-window",
      m_led.rail_top(x_mid)[0] * f_cal, False, SF_STATIC, info=True)
far_nl = max(m_gap.rail_top(float(x0)) + (float(x0),) for x0 in np.arange(bridge[0] - 8.0, bridge[1] + 1e-9, 0.25))
check(f"L1e with no credit for the far ledge (infinite strip, slot zones cut): press at x {far_nl[2]:.1f}", far_nl[0] * f_cal,
      False, SF_STATIC, info=True)
usb_nl = max(m_gap.rail_top(float(x0)) + (float(x0),) for x0 in np.arange(rail_x0 + c_f, win_x0 + 3.0 + 1e-9, 0.25))
print(f"note: with no credit for the USB-end ledge, the same model puts a press at x {usb_nl[2]:.2f} (fingertip x"
      f" {usb_nl[2] - c_f:.2f}..{usb_nl[2] + c_f:.2f}, partly over the ledge, which ends at {win_x0:.1f}) at {usb_nl[0] * f_cal:.2f} MPa"
      f" (SF {ALLOW_INPLANE_MPA / (usb_nl[0] * f_cal):.2f}): the ledge the model ignores is under the finger, so this isn't"
      f" a credible bound (L1e credits it)")
check("L1 with a point load on the rail (no fingertip spread), tie-slot zones cut", E_PETG_MPA * kap1_pt * ct_r * f_slot, False,
      SF_STATIC, info=True)
check("L4b with the strip behind the slots alone (no help from the deck in front of the slots)", M_band * c_A / I_A, False,
      SF_STATIC, info=True)
check("L2 with 2 mm contact (a fingernail or a tool edge, not a hand press)",
      E_PETG_MPA * edge_curvature(F_hand, b_slot, 0.0, 1.0, a=a_slot, mmax=20001) * t / 2, False, SF_STATIC, info=True)
check("proof (§8 test 1a) 40 N on the rail at mid-window (5 mm contact): rail top", 2 * s_L1, False, SF_PROOF, info=True)
check("proof (§8 test 1b) 40 N at the breadboard centre", bend_rect(40.0 * span / 4, span / 2, t), False, SF_PROOF, info=True)
check("proof (§8 test 2) 20 N sideways on the seated ESP32: rail root", bend_rect(20.0 * rail_h, p.SHORT / 2, p.RAIL_W), True,
      SF_PROOF, Kt=2.5, info=True)
bridge_rows(T_TIE_RATED, " at the tie's rated strength (it must break first)", SF_PROOF, True)
P_pf = 1.5 * P_push                                  # proposed §8 test 6: 3 kg push from below beside one tie
T_pf = max(strap_tension(P_pf, top_board + 0.8 - rail_h, p.HALF - 9.0)[0],
           strap_tension(P_pf, top_board + 2.5 - rail_h, p.HALF - 3.9)[0])
check(f"proof (§8 test 6, proposed) {P_pf:.0f} N push from below beside one tie: strap {T_pf:.0f} N, slot inner wall bearing",
      bearing((1 + uy) * T_pf, W_TIE, t), False, SF_PROOF, info=True)
print(f"strap: L7d reaches SF {SF_STATIC:.0f} at a tension of {ALLOW_INPLANE_MPA * W_TIE * t / (SF_STATIC * (1 + uy)):.1f} N;"
      f" a {P_pf:.0f} N push (proposed proof test) gives {T_pf:.1f} N")
for T_nm, lab, A in ((0.15, "M3 x 8 lid screw, no washer", A_head), (0.5, "M3 x 8 lid screw, no washer", A_head),
                     (0.5, "M3 x 8 with an ISO 7089 washer", math.pi / 4 * (F.WASHER[0] ** 2 - 3.6 ** 2))):
    P_t = T_nm * 1000 / (0.2 * 3.0)
    check(f"assembly: {lab} at {T_nm} N*m (P {P_t:.0f} N), bearing on the deck", P_t / A, False, SF_STATIC, info=True)
A_nut6 = 10.0 ** 2 * math.sqrt(3) / 2 - math.pi / 4 * 6.4 ** 2
P6 = 0.6 * 1000 / (0.2 * 6.0)
check(f"assembly: toggle M6 nut at 0.6 N*m (P {P6:.0f} N) on the deck ({A_nut6:.0f} mm²)", P6 / A_nut6, False, SF_STATIC, info=True)
z_esp_top = p.LEDGE_H + 1.6 + 4.0
print(f"note: ESP32 module and USB top {z_esp_top:.1f} mm above the deck against rails {rail_h:.1f}: an upside-down landing hits"
      f" the ESP32 first (not a design case at 5 cm the right way up)")

report(f"{JOB} strength checks (round 4)")

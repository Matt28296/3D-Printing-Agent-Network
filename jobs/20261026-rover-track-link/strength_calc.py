"""Strength check for jobs/20261026-rover-track-link (tracked rover, PETG), round 3.

Run from the project root with the CAD venv active (build123d):
    source /home/claude/.venv-cad/bin/activate
    python3 jobs/20261026-rover-track-link/strength_calc.py

Round 3: the centre-knuckle running hole opened to Ø2.5 CAD (PIN_RUN_CLR 0.3, about Ø2.3 printed), so its tear-out
ligament is 1.75 mm; the outer knuckles still grip the Ø2 steel dowel in Ø2.2 CAD (about Ø2.0 printed). The ligaments
are probed on the build123d solid. Rows tagged as drop rows scale linearly with the drop height.
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
JOB = "20261026-rover-track-link"
L = rover_loads()

import runpy  # noqa: E402

from build123d import Vector  # noqa: E402

lns = runpy.run_path(os.path.join(JOBS, JOB, "model.py"), run_name="model")
p = SimpleNamespace(**{k: v for k, v in lns.items() if k.isupper()})
LINK = lns["design"]()                               # link frame: hinges on x 0 and x 10, mid-plane z 0

d_pin = F.PIN_D                                      # Ø2 steel dowel
hole_c = d_pin + p.PIN_RUN_CLR + p.HOLE_COMP         # 2.5 CAD (about 2.3 printed): centre knuckle, the pin runs
hole_o = d_pin + p.PIN_GRIP_CLR + p.HOLE_COMP        # 2.2 CAD (about 2.0 printed): outer knuckles grip the pin
A_pin = math.pi / 4 * d_pin ** 2
Lc = 2 * p.CENTRE_HALF                               # 13.5
Lo = p.HALF_W - p.OUTER_IN                           # 4.75 each
gap = p.OUTER_IN - p.CENTRE_HALF                     # 0.5


lig_c = p.KN_R - hole_c / 2                          # 1.75 (CAD hole: the smaller ligament)
lig_o = p.KN_R - hole_o / 2                          # 1.90
# confirm on the solid: material behind the centre-knuckle hole toward -x and ahead of the outer-knuckle hole toward +x
lig_c_solid = sum(LINK.is_inside(Vector(-(hole_c / 2) - (i + 0.5) * 0.01, 0.0, 0.0)) for i in range(400)) * 0.01
lig_o_solid = sum(LINK.is_inside(Vector(p.P + hole_o / 2 + (i + 0.5) * 0.01, 9.5, 0.0)) for i in range(400)) * 0.01
beta = bef_beta(0.5 * E_PETG_MPA, E_STEEL_MPA, math.pi * d_pin ** 4 / 64)
print(f"\nlink: Ø{d_pin} steel pin (σy {SY_ROD_MPA:.0f}, conservative) running in Ø{hole_c:.1f} CAD (centre) and gripped in"
      f" Ø{hole_o:.1f} CAD (outer); knuckles {Lc} + 2 x {Lo}, gaps {gap}; ligaments {lig_c:.2f} / {lig_o:.2f}"
      f" (on the solid: {lig_c_solid:.2f} / {lig_o_solid:.2f}); stiff pin: 1/beta {1 / beta:.1f} mm")


def pin_moment(Fp):
    """Stiff-pin clevis, uniform pressure: M = F/2 (a/2 + g + b/4)."""
    return Fp / 2 * (Lo / 2 + gap + Lc / 4)


def tension(label, T, sf, info=False):
    check_metal(f"{label}: pin bending (stiff-pin clevis), {T:.1f} N", bend_round(pin_moment(T), d_pin), SY_ROD_MPA,
                SF_PROOF if sf == SF_PROOF else SF_METAL, info=info)
    check_custom(f"{label}: pin shear (2 planes)", T / (2 * A_pin), 0.5 * SY_ROD_MPA, "steel τy 175",
                 SF_PROOF if sf == SF_PROOF else SF_METAL, info=info)
    check(f"{label}: centre-knuckle bearing", bearing(T, d_pin, Lc), False, sf, info=info)
    check(f"{label}: outer-knuckle bearing (each T/2)", bearing(T / 2, d_pin, Lo), False, sf, info=info)
    check(f"{label}: centre-knuckle tear-out (ligament {lig_c:.2f})", tearout(T, lig_c, Lc), True, sf, shear=True, info=info)
    check(f"{label}: outer-knuckle tear-out (each T/2, ligament {lig_o:.2f})", tearout(T / 2, lig_o, Lo), True, sf, shear=True,
          info=info)


tension(f"K1 stall tight run", L.T_tight_stall, SF_STATIC)
tension(f"K2 everyday tight run", L.T_tight_cyc, SF_CYCLIC)
check(f"K3 outer-knuckle bearing, pretension {T0_N:.0f} N sustained (creep)", bearing(T0_N / 2, d_pin, Lo), False, SF_CYCLIC)
check("K4 outer-knuckle tear-out, pretension sustained (creep)", tearout(T0_N / 2, lig_o, Lo), True, SF_CYCLIC, shear=True)
A_net = 2 * (p.CENTRE_HALF - p.NOTCH_HALF) * F.LINK_T
check("K5 body net section at the notch root (Kt 2.5), stall", L.T_tight_stall / A_net, False, SF_STATIC, Kt=2.5)
clr = p.KN_R + p.KN_GAP
check("K6 bridge shear, centre lands to outer lands, stall", 1.5 * (L.T_tight_stall / 2) / ((F.P - 2 * clr) * F.LINK_T), False,
      SF_STATIC, shear=True)
share = Lc / F.TRACK_W                               # a road-wheel rim landing on a hinge: the centre knuckle's share


def drop(label, Fax, sf=SF_STATIC, info=False, d=False):
    Fp = share * Fax
    check_metal(f"{label}: pin bending on a hinge (clevis), {Fax:.1f} N/axle", bend_round(pin_moment(Fp), d_pin), SY_ROD_MPA,
                SF_PROOF if sf == SF_PROOF else SF_METAL, info=info, drop=d)
    check(f"{label}: centre-knuckle bearing", bearing(Fp, d_pin, Lc), False, sf, info=info, drop=d)
    check(f"{label}: outer-knuckle bearing (each Fp/2)", bearing(Fp / 2, d_pin, Lo), False, sf, info=info, drop=d)
    g_area = 2 * (p.GROUSER_X[1] - p.GROUSER_X[0]) * ((p.HALF_W - 0.5) - (p.OUTER_IN + 0.25))
    check(f"{label}: grouser compression", Fax / g_area, False, sf, info=info, drop=d)


drop(f"K7 5 cm drop, wheel on a hinge", L.drop, d=True)
check(f"K8 side drag {L.side:.1f} N on an outer-knuckle end face", L.side / (0.5 * (F.P - clr) * F.LINK_T), False, SF_CYCLIC)

# advisory
tension(f"proof (§8 test 2) 4.5 kg on a 5-link chain", 4.5 * G_MS2, SF_PROOF, info=True)
drop("proof (§8 test 3) 5 kg road wheel pressed on a hinge", 5.0 * G_MS2, SF_PROOF, info=True)
drop(f"5 cm drop, stiff landing ({L.drop_stiff:.0f} N)", L.drop_stiff, info=True)
tension(f"stall proof (100 % PWM, fresh pack)", L.T_tight_proof, SF_STATIC, info=True)
T08 = T0_N + L.s08[-1][2]
check_metal(f"S-08 ungated 196 N*mm motor: pin bending, tight run {T08:.1f} N", bend_round(pin_moment(T08), d_pin), SY_ROD_MPA,
            info=True)
check(f"S-08 ungated motor: outer-knuckle tear-out", tearout(T08 / 2, lig_o, Lo), True, SF_STATIC, shear=True, info=True)
r_i, r_o = d_pin / 2, p.KN_R
ring = (r_o ** 2 + r_i ** 2) / (r_o ** 2 - r_i ** 2)
for interf in (0.02, 0.05):
    p_fit = E_PETG_MPA * (interf / 2 / r_i) / (ring + NU_PETG)
    check(f"pin press fit {interf} mm (grip tolerance -0.05): hoop at the outer knuckle's ligament, strain"
          f" {interf / d_pin * 100:.1f} %", p_fit * ring, True, SF_PROOF, info=True)
print("press fit: the hoop stress is secondary (self-limiting: it yields or creeps the hole wall); the risk is a knuckle"
      " splitting along its layer line while the pin is pressed in, which spec §8 test 1 checks on a 5-link chain")

report(f"{JOB} strength checks")

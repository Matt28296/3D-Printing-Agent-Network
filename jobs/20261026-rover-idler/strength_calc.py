"""Strength check for jobs/20261026-rover-idler (tracked rover, PETG), rover round 5 (the idler's round 4).

Run from the project root with the CAD venv's interpreter (build123d):
    /home/claude/.venv-cad/bin/python3 jobs/20261026-rover-idler/strength_calc.py

The idler runs the sprocket model with BORE = "round": the same 10-tooth disc on a Ø10 hub with a Ø3.5 printed running
bore on its M3 x 40 bolt (class 12.9, fully threaded), held in the chassis's ±4 mm slot by an M3 jack screw at the bolt
head. Round 5 (chassis strength round 4's fix, user-approved): the chassis's nut plate, a Ø9 washer and the wall nut now sit
outside the wall (|y| 38-43.2), so the hub starts at |y| 43.7 (rover_frame.IDLER_HUB_Y0) and the part is 14.8 tall instead
of 20: the bore is 14.8 long (L/D 4.9 on the Ø3 bolt), so the idler can cock 1.94° on its bolt instead of 1.43°. The disc,
teeth, track plane and the bolt stack beyond the disc don't move. This script re-runs round 3's rows on the round-5 part and
adds: the bore's peak bearing (rigid bore on the bolt), the bore's end edges with the idler cocked by the side drag, the
hub's root, and a tooth pushed sideways by a link. The idler's bolt, slot, plates and jack screw belong to the chassis check.
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
JOB = "20261026-rover-idler"
L = rover_loads()

import runpy  # noqa: E402

from build123d import Face, Plane  # noqa: E402
from OCP.BRepGProp import BRepGProp  # noqa: E402
from OCP.GProp import GProp_GProps  # noqa: E402

ins = runpy.run_path(os.path.join(JOBS, JOB, "model.py"), run_name="model")
IDL = ins["design"]()                                # idler frame = sprocket frame (axis +Z out, track plane z 0)
sp = SimpleNamespace(**{k: v for k, v in ins["_sp"].items() if k.isupper()})
pr = json.load(open(os.path.join(JOBS, JOB, "print_requirements.json")))["min"]
bb_all = IDL.bounding_box()
bore_cad = ins["ROUND_BORE"] + sp.HOLE_COMP          # 3.7 CAD, about 3.5 printed: 0.5 running clearance on the M3 threads
d_bolt = 3.0
clear_d = ins["ROUND_BORE"] - d_bolt                 # 0.5 diametral running clearance (printed bore on the bolt)
THREAD_F = 0.5                                       # crest contact on the threads: half the projected area (rounds 1-2)
L_bore = F.DISC_HALF - sp.HUB_Z0_ROUND               # 14.8 (round 5; 20 before)
assert abs((bb_all.max.Z - bb_all.min.Z) - L_bore) < 0.01, "the bore runs the part's full height"
assert abs(F.Y_T + sp.HUB_Z0_ROUND - F.IDLER_HUB_Y0) < 1e-9 and abs(F.IDLER_HUB_Y0 - 43.7) < 1e-9
L_hub = -F.DISC_HALF - sp.HUB_Z0_ROUND               # 7.8: hub from the disc's inner face to its inner end
L_disc = 2 * F.DISC_HALF + (F.HUB_D - bore_cad) / 2  # disc plus a 45° spread into the hub: 10.15
L_eff = THREAD_F * min(L_disc, L_bore)
perim_t = pr["perimeters"] * 0.45
# tooth section from the solid (same teeth as the sprocket)
r_root = sp.DISC_R + sp.ROOT_CHAMFER
cut = (IDL & Face.make_rect(6.0, 12.0, Plane(origin=(r_root, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0)))).faces()
g = GProp_GProps()
BRepGProp.SurfaceProperties_s(cut[0].wrapped, g)
bb = cut[0].bounding_box()
Z_t = g.MatrixOfInertia().Value(3, 3) / ((bb.max.Y - bb.min.Y) / 2)
w_root = bb.max.Y - bb.min.Y                         # tangential width of the tooth section at the chamfer top
t_tooth = bb.max.Z - bb.min.Z                        # its axial thickness (the disc's 7 mm)
arm = F.RP - r_root
KT_CH = 1.8
KT_SHARP = 2.5
# cock: the 0.5 mm clearance over the bore length lets the idler tilt on its bolt
cock = clear_d / L_bore
cock_r4 = clear_d / 20.0
tip_side = sp.TOOTH_TIP_R * cock
print(f"\nidler (round 5): part {bb_all.max.Z - bb_all.min.Z:.1f} tall (solid), bore Ø{bore_cad:.1f} CAD on the M3 threads, bore"
      f" {L_bore:.1f} long (L/D {L_bore / d_bolt:.1f}), hub Ø{F.HUB_D:.0f} x {L_hub:.1f} from |y| {F.IDLER_HUB_Y0}; effective"
      f" bearing {L_eff:.2f} mm (disc {L_disc:.2f} x thread factor {THREAD_F}); {pr['perimeters']} perimeters; tooth Z"
      f" {Z_t:.2f} mm³, root {w_root:.2f} x {t_tooth:.2f} (solid)")
print(f"cock on the bolt: {clear_d} / {L_bore:.1f} = {cock * 1000:.1f} mrad = {math.degrees(cock):.2f}° (round 4's 20 mm bore:"
      f" {math.degrees(cock_r4):.2f}°); tooth tips (r {sp.TOOTH_TIP_R:.1f}) then {tip_side:.2f} mm sideways against the link notch's"
      f" 0.5 a side: the links straighten it as the teeth enter (free play, no stiffness, so no force beyond the side drag)")


def bore(R):
    return bearing(R, d_bolt, L_eff)


def bore_peak(R):
    """Rigid bore on the bolt as a Winkler foundation (round 3's rigid-pin model): the radial load acts at the track plane,
    DISC_HALF from the bore's outer end; the contact runs over 3 x that (10.5 mm) if the bore is that long, triangular, so
    its peak at the outer end is 2R / (thread factor x d x 10.5)."""
    e_out = F.DISC_HALF
    if L_bore >= 3 * e_out:
        return 2 * R / (THREAD_F * d_bolt * 3 * e_out), 3 * e_out
    raise ValueError("bore shorter than the contact: use the trapezoid")


def cock_edge(S):
    """The idler cocked on its bolt by a side force S at the pitch circle: the couple S x RP bears on the bore's two end
    edges, F_e = S RP / L_bore each, over an assumed 1.0 mm of bore length (edge contact) at the thread factor."""
    Fe = S * F.RP / L_bore
    return Fe, Fe / (THREAD_F * d_bolt * 1.0)


def tooth_root(Fn, Kt=KT_CH):
    return Kt * Fn * arm / Z_t


F_drag = 0.3 * L.R_idler_stall * (d_bolt / 2) / F.RP  # a free idler's teeth carry only its bearing drag
check(f"I1 bore bearing on the M3 threads (mean, effective {L_eff:.2f} mm), reverse stall {L.R_idler_stall:.1f} N",
      bore(L.R_idler_stall), False, SF_STATIC)
check(f"I2 bore bearing (mean), cyclic {L.R_idler_cyc:.1f} N", bore(L.R_idler_cyc), False, SF_CYCLIC)
check(f"I3 bore bearing (mean), pretension {L.R_sus:.0f} N sustained (creep)", bore(L.R_sus), False, SF_CYCLIC)
check(f"I4 bore bearing (mean), 5 cm front corner {L.drop:.1f} N", bore(L.drop), False, SF_STATIC, drop=True)
pk, Lc = bore_peak(1.0)
check(f"I1p bore bearing PEAK at the outer end (rigid bore, triangular over {Lc:.1f} of the {L_bore:.1f} mm bore), reverse"
      f" stall", pk * L.R_idler_stall, False, SF_STATIC)
check(f"I3p bore bearing PEAK, pretension {L.R_sus:.0f} N sustained (creep)", pk * L.R_sus, False, SF_CYCLIC)
check(f"I4p bore bearing PEAK, 5 cm front corner", pk * L.drop, False, SF_STATIC, drop=True)
Fe, p_e = cock_edge(L.side)
for lab, R, sf in ((f"everyday {L.R_idler_cyc:.1f} N cyclic", L.R_idler_cyc, SF_CYCLIC),
                   (f"reverse stall {L.R_idler_stall:.1f} N", L.R_idler_stall, SF_STATIC)):
    check(f"I8 bore's outer end edge, idler cocked {math.degrees(cock):.2f}° by the side drag {L.side:.0f} N at r {F.RP:.2f}"
          f" (edge force {Fe:.2f} N on 1 mm) + the radial PEAK, {lab}", p_e + pk * R, False, sf)
check("I5 disc rim bearing under a link, 5 cm front corner", L.drop / (2 * F.DISC_HALF * 2 * perim_t), False, SF_STATIC,
      drop=True)
check(f"I6 tooth root (chamfer top), bearing drag {F_drag:.2f} N (Kt {KT_CH})", tooth_root(F_drag), False, SF_CYCLIC)
arm_tip = sp.TOOTH_TIP_R - r_root
check(f"I9 tooth pushed sideways by a link at its tip (side drag {L.side:.0f} N on one tooth): root bending, Kt {KT_CH}",
      bend_rect(L.side * arm_tip, w_root, t_tooth), False, SF_CYCLIC, Kt=KT_CH)
A_wash = math.pi * ((F.WASHER[0] / 2) ** 2 - (bore_cad / 2) ** 2)
check(f"I7 hub end face on its running washer (Ø{F.WASHER[0]:.0f} on the wall nut: r {bore_cad / 2:.2f}-{F.WASHER[0] / 2},"
      f" {A_wash:.1f} mm²), side {L.side:.0f} N", L.side / A_wash, False, SF_CYCLIC)
# hub root: the Ø10 hub meets the disc's inner face at a sharp corner (Kt 2.5); its axis is the print Z, so its bending
# stress runs ACROSS the layers. Loads: the cock couple's inner edge force at the hub's inner end (arm L_hub), plus the part
# of the radial triangle that falls in the hub (beyond the 7 mm disc)
Z_hub = math.pi * (F.HUB_D ** 4 - bore_cad ** 4) / (32 * F.HUB_D)
s_d = 2 * F.DISC_HALF


def hub_moment(R, S):
    Lc_ = 3 * F.DISC_HALF
    share = max(0.0, (Lc_ - s_d) / Lc_) ** 2               # triangle's load beyond the disc
    cen = (Lc_ - s_d) / 3                                 # its centroid from the hub root
    return S * F.RP / L_bore * L_hub + R * share * cen


for lab, R, S, sf, dr in ((f"everyday {L.R_idler_cyc:.1f} N + side {L.side:.0f} N cyclic", L.R_idler_cyc, L.side, SF_CYCLIC,
                           False),
                          (f"reverse stall {L.R_idler_stall:.1f} N + side {L.side:.0f} N", L.R_idler_stall, L.side, SF_STATIC,
                           False),
                          (f"5 cm front corner {L.drop:.1f} N + side {L.side:.0f} N", L.drop, L.side, SF_STATIC, True)):
    check(f"I10 hub root (Ø{F.HUB_D:.0f} / Ø{bore_cad:.1f}, {L_hub:.1f} long) bending across layers, sharp corner (Kt"
          f" {KT_SHARP}), {lab}", hub_moment(R, S) / Z_hub, True, sf, Kt=KT_SHARP, drop=dr)

# advisory
check(f"proof (§8 test 1): 4.5 kg ({4.5 * G_MS2:.0f} N) rearward, bore bearing (mean)", bore(4.5 * G_MS2), False, SF_PROOF,
      info=True)
check(f"proof (§8 test 1): 4.5 kg rearward, bore bearing PEAK", pk * 4.5 * G_MS2, False, SF_PROOF, info=True)
check(f"proof: reverse stall at 100 % PWM on a fresh pack {L.R_idler_proof:.1f} N, bore bearing (mean)", bore(L.R_idler_proof),
      False, SF_PROOF, info=True)
check(f"proof: 5 kg (49 N) hung from the idler (chassis §8 test 1), bore bearing PEAK", pk * 5 * G_MS2, False, SF_PROOF,
      info=True)
check(f"jam: stall pull {L.F_stall:.2f} N on one idler tooth (Kt {KT_CH})", tooth_root(L.F_stall), False, SF_STATIC, info=True)
check(f"bore bearing (mean), 5 cm corner, stiff landing ({L.drop_stiff:.0f} N)", bore(L.drop_stiff), False, SF_STATIC, info=True)
check(f"bore bearing PEAK, 5 cm corner, stiff landing ({L.drop_stiff:.0f} N)", pk * L.drop_stiff, False, SF_STATIC, info=True)
F_s08 = 2 * (T0_N + L.s08[-1][2])
check(f"S-08 ungated 196 N*mm motor at the 6.0 V cap: reverse stall {F_s08:.1f} N, bore bearing (mean)", bore(F_s08), False,
      SF_STATIC, info=True)
Fe4 = L.side * F.RP / 20.0
check(f"round 4's 20 mm bore for comparison: I8 at the reverse stall (edge force {Fe4:.2f} N)",
      Fe4 / (THREAD_F * d_bolt) + pk * L.R_idler_stall, False, SF_STATIC, info=True)
# the chassis clamp's yaw no longer reaches the idler's hub face: chassis round 5 strength_calc gives the bolt body's yaw at
# the reverse stall as <= 2.43 mrad (printed there), far inside the idler's own free cock, so the hub face is never the
# backstop that round 3 checked (that row is retired)
THETA_CLAMP_R5 = 2.43e-3
check_custom(f"chassis clamp yaw at the reverse stall ({THETA_CLAMP_R5 * 1000:.2f} mrad, chassis round 5) against the idler's"
             f" free cock ({cock * 1000:.1f} mrad): the hub face doesn't become a backstop", THETA_CLAMP_R5 * 1000,
             cock * 1000, "mrad",
             SF_STATIC, info=True)
d3 = D3_M3
for lab, Fb in ((f"reverse stall {L.R_idler_stall:.1f} N", L.R_idler_stall), (f"5 cm corner {L.drop:.1f} N", L.drop)):
    check_metal(f"M3 x 40 class 12.9 bending at the wall face (chassis-owned): {lab} x {F.Y_T - F.HALF_W_OUT:.0f}",
                bend_round(Fb * (F.Y_T - F.HALF_W_OUT), d3), SY_129_MPA, info=True)
print(f"stack (rover_frame / assembly_check): nut plate {F.HALF_W_OUT:.0f}-{F.HALF_W_OUT + F.PLATE_T:.0f}, Ø9 washer"
      f" -{F.HALF_W_OUT + F.PLATE_T + F.WASHER_WIDE[1]:.1f}, wall nut -{F.HALF_W_OUT + F.PLATE_T + F.WASHER_WIDE[1] + F.NUT[1]:.1f},"
      f" running washer -{F.IDLER_HUB_Y0:.1f}, idler {F.IDLER_HUB_Y0:.1f}-{F.Y_T + F.DISC_HALF:.1f}")

report(f"{JOB} strength checks")

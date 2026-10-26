"""Strength check for jobs/20261026-rover-chassis (tracked rover, PETG), round 5.

Run from the project root with the CAD venv's interpreter (build123d, trimesh, scipy), about 1-2 min:
    /home/claude/.venv-cad/bin/python3 jobs/20261026-rover-chassis/strength_calc.py

Round 5 = the round-5 geometry (model.py, rover_frame.py) with round 4's method and loads. Round 5 made strength round 4's
fix only (user-approved):
- the 9 x 15 x 4.6 idler nut slot is deleted: 8.0 mm of solid PETG between the head-plate recess floor (|y| 30) and the
  wall's outer face (|y| 38), with only the bolt slot through it;
- the nut plate is the head plate's twin (20.6 x 10 x 2, slot 3.4 x 12 from 6 to 18 mm along), flat on the outer face on a
  printed seat: a lip under its bottom edge (top Z_A - 5.2, 1.0 proud, 45° underside) and an end stop at each end (inner
  faces x 108 and 129, STOP_W 1.5, up to Z_A + 5.2; the designer's addition);
- a Ø9 x 0.8 DIN 9021 washer under the wall nut; the idler's hub 5.2 mm shorter (idler job).

The clamp is round 4's contact model (no friction and no preload credited, DFM round 4 S2), generalised so that the
plates' and the PETG's z-bands come from the round-5 geometry (probed on the solid) instead of round 4's symmetric FIX
idealisation, and checked against round 4's FIX numbers. New rows: the head plate's top edge on the 45° roof (B4, now all
of the drop shear), the end stops and the lip (B18/B19; friction as a DEMAND only), the head plate on its recess end.
Rows tagged as drop rows scale linearly with the drop height; report() prints the height at which the first of them
reaches its required SF.
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
JOB = "20261026-rover-chassis"
L = rover_loads()

import runpy  # noqa: E402

import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from build123d import Face, Plane, Vector  # noqa: E402
from OCP.BRepGProp import BRepGProp  # noqa: E402
from OCP.GProp import GProp_GProps  # noqa: E402
from scipy import ndimage, sparse  # noqa: E402
from scipy.sparse.linalg import spsolve  # noqa: E402

ns = runpy.run_path(os.path.join(JOBS, JOB, "model.py"), run_name="model")
WORLD = ns["design"]()                       # round-5 chassis in the rover world frame
p = SimpleNamespace(**{k: v for k, v in ns.items() if k.isupper()})
M = F.MOTOR
HC = p.HOLE_COMP


def section(y=None, x=None, window=None):
    """Area, centroid and second moments of the chassis cut by the plane y = const (or x = const) inside window
    (u0, u1, v0, v1) in that plane's (x or y, z) coordinates. Returns a list of (area, centroid, I_u, I_v) per face,
    I about the face centroid: I_u = integral v^2 dA (bending about the u axis), I_v = integral u^2 dA."""
    if y is not None:
        pl = Plane(origin=(0, y, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    else:
        pl = Plane(origin=(x, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    u0, u1, v0, v1 = window
    rect = Face.make_rect(u1 - u0, v1 - v0, pl.shift_origin(pl.from_local_coords(((u0 + u1) / 2, (v0 + v1) / 2))))
    out = []
    for f in (WORLD & rect).faces():
        g = GProp_GProps()
        BRepGProp.SurfaceProperties_s(f.wrapped, g)
        c, m = g.CentreOfMass(), g.MatrixOfInertia()
        if y is not None:     # plane normal Y: I about X = int z^2, I about Z = int x^2
            out.append((g.Mass(), (c.X(), c.Y(), c.Z()), m.Value(1, 1), m.Value(3, 3)))
        else:                 # plane normal X: I about Y = int z^2, I about Z = int y^2
            out.append((g.Mass(), (c.X(), c.Y(), c.Z()), m.Value(2, 2), m.Value(3, 3)))
    return out


def solid_at(x, y, z):
    return WORLD.is_inside(Vector(x, y, z))


# ---- 0. mass check (deep review 04 S-18 method: voxel shell + infill at the print_requirements minima) ------------------
def printed_mass_g(job, qty, pitch):
    mesh = trimesh.load(os.path.join(JOBS, job, "part.stl"), force="mesh")
    r = json.load(open(os.path.join(JOBS, job, "print_requirements.json")))["min"]
    lo, hi = mesh.bounds
    n = [int(math.ceil((hi[i] - lo[i]) / pitch)) + 2 for i in range(3)]
    xs, ys, zs = [lo[i] - pitch + (np.arange(n[i]) + 0.5) * pitch for i in range(3)]
    grid = np.zeros(n, dtype=bool)
    for k, z in enumerate(zs):
        if not lo[2] < z < hi[2]:
            continue
        segs = trimesh.intersections.mesh_plane(mesh, [0, 0, 1], [0, 0, z])
        if len(segs) == 0:
            continue
        x1, y1, x2, y2 = segs[:, 0, 0], segs[:, 0, 1], segs[:, 1, 0], segs[:, 1, 1]
        ylo, yhi = np.minimum(y1, y2), np.maximum(y1, y2)
        for j, yy in enumerate(ys):
            sel = (ylo <= yy) & (yhi > yy)
            if not sel.any():
                continue
            t = (yy - y1[sel]) / (y2[sel] - y1[sel])
            xc = np.sort(x1[sel] + t * (x2[sel] - x1[sel]))
            for a, b in zip(xc[0::2], xc[1::2]):
                i0, i1 = int(np.ceil((a - xs[0]) / pitch)), int(np.floor((b - xs[0]) / pitch))
                if i1 >= i0:
                    grid[max(i0, 0):i1 + 1, j, k] = True
    t_xy, t_z = r["perimeters"] * 0.45, max(r["top_solid_layers"], r["bottom_solid_layers"]) * 0.2
    d = ndimage.distance_transform_edt(np.pad(grid, 1), sampling=(pitch / t_xy, pitch / t_xy, pitch / t_z))[1:-1, 1:-1, 1:-1]
    shell, core = grid & (d <= 1.0), grid & (d > 1.0)
    scale = mesh.volume / (grid.sum() * pitch ** 3)
    g = RHO_PETG * scale * (shell.sum() + r["fill_density"] / 100 * core.sum()) * pitch ** 3
    return g * qty, mesh.volume * RHO_PETG * qty


RHO_PETG = 1.27e-3
RHO_STEEL = 7.85e-3
printed = {"chassis": ("20261026-rover-chassis", 1, 0.4), "lid": ("20261026-rover-lid", 1, 0.4),
           "sprocket": ("20261026-rover-sprocket", 2, 0.2), "idler": ("20261026-rover-idler", 2, 0.2),
           "wheel": ("20261026-rover-wheel", 4, 0.2), "link": ("20261026-rover-track-link", 2 * F.N_LINKS, 0.12)}
pm = {k: printed_mass_g(*v) for k, v in printed.items()}
m_pin = math.pi / 4 * F.PIN_D ** 2 * 24.0 * 7.85e-3
A_PLATE_SLOT = (F.PLATE_SLOT[1] - F.PLATE_SLOT[0]) * F.PLATE_SLOT[0] + math.pi / 4 * F.PLATE_SLOT[0] ** 2
m_head_plate = (F.IDLER_PLATE[0] * F.IDLER_PLATE[1] - A_PLATE_SLOT) * F.PLATE_T * RHO_STEEL
m_nut_plate = (F.NUT_PLATE[0] * F.NUT_PLATE[1] - A_PLATE_SLOT) * F.PLATE_T * RHO_STEEL
BOM = [  # round-5 BUILD_GUIDE §1, grams (bought-part masses: hobby_parts where given, else typical catalogue values)
    ("2 x N20 gear motor", 2 * M.mass_g), ("2 x Pololu #1996 hub", 2 * F.HUB.mass_g), ("8 x M3x12 screw", 8 * 0.9),
    ("4 x M3x50 + 2 x M3x40 fully threaded", 4 * 2.5 + 2 * 2.1), ("2 x M3x20 set screw", 2 * 0.85),
    ("6 nuts, 6 nylocs, 26 washers, 4 DIN 9021", 6 * 0.25 + 6 * 0.3 + 26 * 0.12 + 4 * 0.35),
    ("2 head + 2 nut steel plates (round 5: all 20.6 x 10)", 2 * (m_head_plate + m_nut_plate)),
    ("4 heat-set inserts + 4 x M3x8", 4 * 0.4 + 4 * 0.65), (f"{2 * F.N_LINKS} steel pins Ø2 x 24", 2 * F.N_LINKS * m_pin),
    ("battery: 2 protected 18650 + holder", HP.BATT_2X18650_LONG.mass_g), ("ESP32 DevKit", 10.0),
    ("mini breadboard + TB6612 + MP1584", HP.MINI_BREADBOARD.mass_g + 3.0 + 2.5), ("HC-SR04", HP.HCSR04.mass_g),
    ("MTS-102 toggle + nuts", 6.0), ("wires, jumpers, capacitors, resistors, diode", 20.0),
    ("velcro strap, zip ties, foam tape, glue", 8.0)]
m_printed = sum(v[0] for v in pm.values())
m_solid = sum(v[1] for v in pm.values())
m_bought = sum(g for _, g in BOM)
m_est = m_printed + m_bought
print("\nmass check (round 5): printed at the print_requirements minima: "
      + ", ".join(f"{k} {v[0]:.1f} g" for k, v in pm.items()) + f" = {m_printed:.0f} g (all solid {m_solid:.0f} g)")
print("  bought (BUILD_GUIDE §1): " + ", ".join(f"{n} {g:.1f}" for n, g in BOM) + f" = {m_bought:.0f} g")
print(f"  rover {m_est:.0f} g at the print minima ({m_solid + m_bought:.0f} g if every printed part were solid);"
      f" design mass {MASS_DESIGN_G:.0f} g covers it by {100 * (MASS_DESIGN_G / m_est - 1):.1f} %")
assert MASS_DESIGN_G >= m_est, "design mass below the estimate: raise MASS_DESIGN_G in all six rover scripts"

# ---- geometry ---------------------------------------------------------------------------------------------------------
t_w = F.WALL                                         # 4.5
y_in_face = F.HALF_W_OUT - t_w                       # 33.5: wall inner face
y_mid = F.HALF_W_OUT - t_w / 2                       # 35.75
arm_w = F.Y_T - y_mid                                # 19.25: track plane to the wall mid-plane
arm_bolt = F.Y_T - F.HALF_W_OUT                      # 17: track plane to the outer face (nut)
y_boss = y_in_face - F.BOSS_IN                       # 28.0: boss / idler-block face
KT_CHAMFER = 1.6       # 1.5 x 45° collar or strip (JOIN) on a 4.5 mm wall: leg 1.5 ~ r 1.1 = 0.25 t -> 1.5 (skill), +0.1
                       # because a chamfer is a little worse than a fillet (round 2's tooth-root reasoning)
KT_SHARP = 2.5         # sharp internal corner (skill; coordinator: >= 2 at the buttress, nacelle and web roots)
nut_t = F.NUT[1]                                     # 2.4
nut_recess = p.NUT_DEPTH - nut_t                     # 0.2: nut face below the outer face
s_nut0, s_nut1 = nut_recess, p.NUT_DEPTH             # nut zone, measured inward from the outer face
L_emb = F.HALF_W_OUT - y_boss                        # 10: wall + boss
nut_flat = F.NUT[0] / math.sqrt(3)                   # 3.175: hex flat length
print(f"\nchassis: wall {t_w}, boss/idler-block face |y| {y_boss}, road bosses Ø{2 * p.ROAD_BOSS_R:.0f} with a {p.JOIN} x 45°"
      f" collar (Kt {KT_CHAMFER}); pocket {2 * p.POCKET_HX:.1f} x {2 * p.POCKET_HY:.1f} CAD rolled 45°, nacelle walls"
      f" {F.NACELLE_WALL}, skin {F.SKIN} at |y| {F.MOTOR_FACE_Y}-{F.MOTOR_FACE_Y + F.SKIN}, shaft arm {F.SHAFT_ARM}")


def rigid_pin(Fn, e, zones):
    """Rigid bolt in a Winkler foundation (bearing pressure = k x displacement): load Fn at e outboard of the outer face
    (s = 0), embedded zones (s0, s1, width) measured inward. Returns (w0, theta) with p(s) = Fn (w0 + theta s) [MPa]."""
    a11 = sum(b * (s1 - s0) for s0, s1, b in zones)
    a12 = sum(b * (s1 ** 2 - s0 ** 2) / 2 for s0, s1, b in zones)
    a22 = sum(b * (s1 ** 3 - s0 ** 3) / 3 for s0, s1, b in zones)
    det = a11 * a22 - a12 ** 2
    return (a22 + a12 * e) / det, (-a11 * e - a12) / det


def pin_bearing(Fn, e, nut_w):
    """Mean bearing on the nut flat (outer zone) and on the inner hole edge (zone of reversed pressure), and the peaks."""
    zones = [(s_nut0, s_nut1, nut_w), (s_nut1, L_emb, 3.0)]
    w0, th = rigid_pin(Fn, e, zones)
    s_zero = -w0 / th
    R_nut = Fn * nut_w * (w0 * (s_nut1 - s_nut0) + th * (s_nut1 ** 2 - s_nut0 ** 2) / 2)
    R_in = -Fn * 3.0 * (w0 * (L_emb - s_zero) + th * (L_emb ** 2 - s_zero ** 2) / 2)
    return (R_nut / (nut_w * (s_nut1 - s_nut0)), R_in / (3.0 * (L_emb - s_zero)), Fn * (w0 + th * s_nut0),
            -Fn * (w0 + th * L_emb), R_nut, R_in, s_zero)


# ---- A. road-wheel axles: Ø26 boss + 1.5 x 45° collar, BOSS_IN 5.5, nut trap, M3 x 50 class 12.9 fully threaded ----------
a_road = p.ROAD_BOSS_R
wh = runpy.run_path(os.path.join(JOBS, "20261026-rover-wheel", "model.py"), run_name="wheel")
r_flange = wh["RIM_R"] + wh["CONE_RISE"]
check(f"A1 road-wheel boss: wall bending at the collar, 5 cm drop {L.drop:.1f} N (Kt {KT_CHAMFER})",
      plate_boss_moment_stress(L.drop * arm_w, a_road, t_w, KT_CHAMFER), True, SF_STATIC, drop=True)
N_wheel = 0.3 * L.W                                  # rear wheels carry 54 % (S-18): 0.27 W each; 0.3 W used
check(f"A2 road-wheel boss: weight share {N_wheel:.1f} N sustained (Kt {KT_CHAMFER})",
      plate_boss_moment_stress(N_wheel * arm_w, a_road, t_w, KT_CHAMFER), True, SF_CYCLIC)
check(f"A3 road-wheel boss: side drag {L.side:.0f} N at the flange r{r_flange:.1f} (Kt {KT_CHAMFER})",
      plate_boss_moment_stress(L.side * r_flange, a_road, t_w, KT_CHAMFER), True, SF_CYCLIC)
nb, ib, nb_pk, ib_pk, Rn, Ri, s0 = pin_bearing(L.drop, arm_bolt, F.NUT[0])
check(f"A4 road-wheel nut-trap bearing (rigid bolt on PETG, mean over the nut), 5 cm drop", nb, False, SF_STATIC, drop=True)
check(f"A5 road-wheel inner hole-edge bearing (mean over the loaded {L_emb - s0:.1f} mm), 5 cm drop", ib, False, SF_STATIC,
      drop=True)
check_metal(f"A6 M3 x 50 class 12.9 bending at the outer face, 5 cm drop x {arm_bolt:.0f}",
            bend_round(L.drop * arm_bolt, D3_M3), SY_129_MPA, drop=True)


# ---- B. idler mount: 30 x 24 block (face |y| 28), ±4 slot with hull, jack screw at the head, round-5 steel plates --------
xi1 = F.X_FRONT_OUT - t_w
bl = min(F.AXLE_DX + p.IDLER_BLOCK[0] / 2, xi1) - (F.AXLE_DX - p.IDLER_BLOCK[0] / 2)     # 25.5 (runs into the front wall)
a_idler = math.sqrt(bl * p.IDLER_BLOCK[1] / math.pi)
check(f"B1 idler block: wall bending, 5 cm front corner {L.drop:.1f} N (Kt {KT_CHAMFER} top strip)",
      plate_boss_moment_stress(L.drop * arm_w, a_idler, t_w, KT_CHAMFER), True, SF_STATIC, drop=True)
check(f"B2 idler block: wall bending, reverse stall {L.R_idler_stall:.1f} N (Kt {KT_SHARP}: sharp rear corner)",
      plate_boss_moment_stress(L.R_idler_stall * arm_w, a_idler, t_w, KT_SHARP), False, SF_STATIC)
check(f"B3 idler block: wall bending, pretension {L.R_sus:.0f} N sustained (Kt {KT_SHARP})",
      plate_boss_moment_stress(L.R_sus * arm_w, a_idler, t_w, KT_SHARP), False, SF_CYCLIC)

# --- the round-5 clamp, as built (model.py / rover_frame.py), and probes of the solid ---------------------------------
ZA = F.Z_A
r_s = (p.BOLT_D + HC) / 2                                  # 1.8: CAD radius of the idler slot
SLOT_LO, SLOT_HI = -r_s, r_s * math.sqrt(2)                # PETG bolt-slot band about Z_A (CAD): -1.80 .. +2.55
BS = (F.AXLE_DX - F.IDLER_SLOT - r_s, F.AXLE_DX + F.IDLER_SLOT + r_s)   # 114.2-125.8: PETG bolt slot along X
assert tuple(F.NUT_PLATE) == tuple(F.IDLER_PLATE), "round 5: the nut plate is the head plate's twin"
P_LEN, P_H = F.IDLER_PLATE                                 # both plates 20.6 x 10
H0 = 0.5 * (p.PLATE_RECESS_X[0] + p.PLATE_RECESS_X[1]) - P_LEN / 2   # 108.2: head plate, centred in its recess
N0 = 0.5 * (p.NUT_PLATE_X[0] + p.NUT_PLATE_X[1]) - P_LEN / 2         # 108.2: nut plate, centred between its stops
HS = (H0 + F.PLATE_SLOT_FROM, H0 + F.PLATE_SLOT_FROM + F.PLATE_SLOT[1])   # 114.2-126.2 (6 to 18 mm along, BUILD_GUIDE §1)
NS = (N0 + F.PLATE_SLOT_FROM, N0 + F.PLATE_SLOT_FROM + F.PLATE_SLOT[1])
PLATE_Z0 = -p.PLATE_RECESS_Z                               # -5.2: the head plate stands on the recess floor ...
assert abs(-p.LIP_DZ - PLATE_Z0) < 1e-9, "... and the nut plate on the lip at the same height"
PLATE_MID = PLATE_Z0 + P_H / 2                             # -0.2: both plates Z_A - 5.2 .. + 4.8, slot band -1.9 .. +1.5
BAND = F.PLATE_SLOT[0] / 2                                 # 1.7: the plates' slot half width (slot on the plate's centre line)
BOLT_Z = -p.BOLT_D / 2 + 1.5                               # -0.2: the M3 (Ø3) rests on the printed slot floor (Ø3.4: -1.7)
WASHER_R = F.WASHER_WIDE[0] / 2                            # 4.5: Ø9 x 0.8 DIN 9021 under the head and, round 5, under the nut
y_rec = y_boss + p.PLATE_RECESS_D                          # 30: recess floor = head plate's bearing face
y_out = F.HALF_W_OUT                                       # 38: wall's outer face = nut plate's bearing face
WEB_T = y_out - y_rec                                      # 8.0: PETG between the plates
TP_MIN = 1.9                                               # 14-gauge plate (the BOM's first choice; metric 2.0 is stiffer)
STOP_H = (ZA + p.LIP_DZ) - (ZA - p.LIP_DZ - p.LIP_FACE / 2)   # 10.9: end stop height (Z_A - 5.7 .. + 5.2)
probe = {"8 mm PETG solid at (120, 30.1, Z_A+3.5)": solid_at(120.0, 30.1, ZA + 3.5),
         "8 mm PETG solid at (120, 34.0, Z_A+3.5) (round 4's nut slot gone)": solid_at(120.0, 34.0, ZA + 3.5),
         "8 mm PETG solid at (120, 37.9, Z_A+4.4)": solid_at(120.0, 37.9, ZA + 4.4),
         "8 mm PETG solid at (120, 36.0, Z_A-4.4)": solid_at(120.0, 36.0, ZA - 4.4),
         "recess void at (120, 29.9, Z_A+3.5)": not solid_at(120.0, 29.9, ZA + 3.5),
         "recess void at (120, 29.9, Z_A-5.1), floor solid at Z_A-5.3": not solid_at(120.0, 29.9, ZA - 5.1)
         and solid_at(120.0, 29.9, ZA - 5.3),
         "outside the wall void at (120, 38.1, Z_A+3.5)": not solid_at(120.0, 38.1, ZA + 3.5),
         "bolt slot void at (120, 34, Z_A+2.45) and (120, 34, Z_A-1.7)": not solid_at(120.0, 34.0, ZA + 2.45)
         and not solid_at(120.0, 34.0, ZA - 1.7),
         "bolt slot edges solid at (120, 34, Z_A+2.65) and (120, 34, Z_A-1.9)": solid_at(120.0, 34.0, ZA + 2.65)
         and solid_at(120.0, 34.0, ZA - 1.9),
         "uncut PETG beside the bolt slot at (113.5, 34, Z_A) and (126.5, 34, Z_A)": solid_at(113.5, 34.0, ZA)
         and solid_at(126.5, 34.0, ZA),
         "lip: solid (118, 38.5, Z_A-5.3), void above it (118, 38.5, Z_A-5.1)": solid_at(118.0, 38.5, ZA - 5.3)
         and not solid_at(118.0, 38.5, ZA - 5.1),
         "lip: 1.0 proud (void at (118, 39.05, Z_A-5.5)), face to Z_A-6.2": not solid_at(118.0, 39.05, ZA - 5.5)
         and solid_at(118.0, 38.95, ZA - 6.15) and not solid_at(118.0, 38.95, ZA - 6.3),
         "lip: 45° underside (solid at (118, 38.05, Z_A-7.15), void at (118, 38.05, Z_A-7.3))":
         solid_at(118.0, 38.05, ZA - 7.15) and not solid_at(118.0, 38.05, ZA - 7.3),
         "rear stop x 106.5-108: solid (107, 38.5, Z_A), void (108.1, 38.5, Z_A), void (106.4, 38.5, Z_A)":
         solid_at(107.0, 38.5, ZA) and not solid_at(108.1, 38.5, ZA) and not solid_at(106.4, 38.5, ZA),
         "front stop x 129-130.5: solid (130, 38.5, Z_A), void (128.9, 38.5, Z_A)": solid_at(130.0, 38.5, ZA)
         and not solid_at(128.9, 38.5, ZA),
         "stops up to Z_A+5.2: solid (107, 38.5, Z_A+5.1), void (107, 38.5, Z_A+5.3)": solid_at(107.0, 38.5, ZA + 5.1)
         and not solid_at(107.0, 38.5, ZA + 5.3),
         "nut plate's space clear (120, 39.5, Z_A)": not solid_at(120.0, 39.5, ZA)}
assert all(probe.values()), f"idler clamp geometry differs from the round-5 model: {probe}"
print(f"idler clamp (probed on the solid): head plate and nut plate both {P_LEN} x {P_H} x {F.PLATE_T} (checked at"
      f" {TP_MIN} for 14 ga) at x {H0:.1f}-{H0 + P_LEN:.1f} (slot {HS[0]:.1f}-{HS[1]:.1f}), z Z_A {PLATE_Z0:+.1f}..{PLATE_Z0 + P_H:+.1f}"
      f" (slot band {PLATE_MID - BAND:+.1f}..{PLATE_MID + BAND:+.1f}); head plate on the recess floor |y| {y_rec:.0f}, nut plate"
      f" on the outer face |y| {y_out:.0f} on its lip (top Z_A {-p.LIP_DZ:+.1f}, {p.LIP_OUT} proud) between stops x"
      f" {p.NUT_PLATE_X[0] - p.STOP_W:.1f}-{p.NUT_PLATE_X[0]:.1f} and {p.NUT_PLATE_X[1]:.1f}-{p.NUT_PLATE_X[1] + p.STOP_W:.1f};"
      f" {WEB_T:.1f} mm of PETG between them, cut only by the bolt slot x {BS[0]:.1f}-{BS[1]:.1f}, z {SLOT_LO:+.2f}..{SLOT_HI:+.2f};"
      f" bolt axis at Z_A {BOLT_Z:+.1f} (on the printed slot floor)")

# --- clamp model (round 4's method, generalised to the round-5 stack) --------------------------------------------------
# Everything is in the BOLT frame (z measured from the bolt axis at Z_A - 0.2). In it the steel is exactly symmetric: both
# plates +-5.0, their slot bands +-1.7, both Ø9 washers r 4.5 about the bolt. The PETG is not: the band between the plates
# (8.0 mm thick) reaches up to the recess roof's start at +5.4 and down to the recess floor / lip top at -5.0, and the PETG
# bolt slot runs from -1.6 to +2.75. So the PETG strips beside the bolt slot are 2.65 (top) and 3.4 (bottom) tall, rooted at
# +5.4 and -5.0. Their roots: inner face, top = the recess wall turning into its 45° roof (135°), bottom = the recess floor's
# sharp 90° edge; outer face, top = the flat wall face (no corner), bottom = the lip's top face (sharp 90°). Kt 2.5 is used
# at all four (conservative at the two top roots; advisory rows show Kt 1.0 at the flat one).
E_ST = E_STEEL_MPA
SY_PLATE_MPA = 200.0     # hand-cut 14 ga (1.9) / 2 mm mild steel sheet or flat bar: conservative yield (A36 250, CR 1008 ~200)
ROOT_SOFT = 1.3          # strip root rotation adds ~30 % to the Timoshenko cantilever compliance (round 4)
K_END = 30000.0          # N/mm per mm: the uncut 8 mm band beside the bolt slot, out of plane (round 4 FIX; 10000 as sensitivity)
KB_BOLT = 70000.0        # N/mm: M3 between head and nut, with head and nut compliance (round 4)
KP = 2.0e5               # N/mm^3 contact penalty (steel on steel, plate on PETG faces)
R_HOLE_W = 1.6           # DIN 9021 M3 hole Ø3.2


def strip_k(a, t):
    """Out-of-plane stiffness per unit length (N/mm per mm) of a PETG strip cantilevered from its root, load at arm a
    (Timoshenko beam: bending + shear, kappa 5/6)."""
    EI = E_PETG_MPA * t ** 3 / 12.0
    kGA = 5.0 / 6.0 * G_PETG_MPA * t
    return 1.0 / (a ** 3 / (3 * EI) + a / kGA)


def _cut(segs, a, b):
    out = []
    for s0, s1 in segs:
        if s1 <= a or s0 >= b:
            out.append((s0, s1))
            continue
        if s0 < a:
            out.append((s0, a))
        if s1 > b:
            out.append((b, s1))
    return out


def _clip(segs, lo, hi):
    return [(max(a, lo), min(b, hi)) for a, b in segs if min(b, hi) > max(a, lo)]


def _w(segs):
    return sum(b - a for a, b in segs)


def _hermite(EI, Lh):
    return EI / Lh ** 3 * np.array([[12, 6 * Lh, -12, 6 * Lh], [6 * Lh, 4 * Lh * Lh, -6 * Lh, 2 * Lh * Lh],
                                    [-12, -6 * Lh, 12, -6 * Lh], [6 * Lh, 2 * Lh * Lh, -6 * Lh, 4 * Lh * Lh]])


def plate_segs(g, x, slot):
    """z-segments (bolt frame) of a plate at x: +-hz about its mid (offset po), minus its slot band where its slot is."""
    hz, po = g["hz"], g["po"]
    s = [(po - hz, po + hz)]
    return _cut(s, po - BAND, po + BAND) if slot[0] <= x <= slot[1] else s


def washer_width(g, r, d, x, slot):
    """z-width of a Ø2r washer (centred on the bolt) that bears on a plate at dx = d from the bolt."""
    if abs(d) >= r:
        return 0.0
    c = math.sqrt(r * r - d * d)
    s = _clip(plate_segs(g, x, slot), -c, c)
    if abs(d) < R_HOLE_W:
        ch = math.sqrt(R_HOLE_W ** 2 - d * d)
        s = _cut(s, -ch, ch)
    return _w(s)


def arms(g):
    """Arm from each PETG strip's root to the middle of the band where a plate bears on it: (top, bottom)."""
    hz, po = g["hz"], g["po"]
    t0, t1 = max(po + BAND, g["sh"]), min(po + hz, g["rt"])
    b0, b1 = max(BAND - po, g["sl"]), min(hz - po, g["rb"])
    return g["rt"] - (t0 + t1) / 2, g["rb"] - (b0 + b1) / 2


def clamp_yaw(g, xb, Mz, P0=0.0, r_e=None, root_soft=ROOT_SOFT, k_end=None, h=0.1):
    """Idler clamp under the yaw moment Mz (about Z) on the bolt body, bolt at slot position xb. Everything along X: head
    plate and nut plate (steel Hermite beams), the PETG between them as two face nodes and a mid node per station (through-
    thickness springs, out-of-plane ground spring: the strips beside the bolt slot as cantilevers from their roots, the uncut
    band elsewhere), rigid bolt body (v_h, v_n, theta) touching the plates through the two Ø9 washers, bolt axial spring with
    an initial stretch for the preload P0. Compression-only contacts, active-set iteration. Round 4's model, with the
    plates' z-bands and the PETG band taken from the round-5 geometry."""
    k_end = g["k_end"] if k_end is None else k_end
    r_h = g["r_wh"] if r_e is None else r_e
    r_n = g["r_wn"] if r_e is None else r_e
    wt, tp = g["web_t"], g["tp"]
    (Ha, Hb), (Na, Nb), (Wa, Wb) = g["H"], g["N"], g["W"]
    assert Wa <= min(Ha, Na) + 1e-9 and Wb >= max(Hb, Nb) - 1e-9, "both plates bear on the 8 mm band only"
    x0, x1 = min(Ha, Na), max(Hb, Nb)
    xs = np.round(np.arange(x0, x1 + 1e-9, h), 6)
    n = len(xs)
    inH = (xs >= Ha - 1e-9) & (xs <= Hb + 1e-9)
    inN = (xs >= Na - 1e-9) & (xs <= Nb + 1e-9)
    iH, iN = np.nonzero(inH)[0], np.nonzero(inN)[0]
    a_top, a_bot = arms(g)
    k_top = strip_k(max(a_top, 0.05), wt) / root_soft
    k_bot = strip_k(max(a_bot, 0.05), wt) / root_soft
    wH, wN, wwa, wnu, bweb = (np.zeros(n) for _ in range(5))
    for k, x in enumerate(xs):
        inbs = BS[0] <= x <= BS[1]
        if inH[k]:
            sH = plate_segs(g, x, g["Hs"])
            wH[k] = _w(_clip(_cut(sH, -g["sl"], g["sh"]) if inbs else sH, -g["rb"], g["rt"]))
            wwa[k] = washer_width(g, r_h, x - xb, x, g["Hs"])
        if inN[k]:
            sN = plate_segs(g, x, g["Ns"])
            wN[k] = _w(_clip(_cut(sN, -g["sl"], g["sh"]) if inbs else sN, -g["rb"], g["rt"]))
            wnu[k] = washer_width(g, r_n, x - xb, x, g["Ns"])
        bweb[k] = (g["rt"] + g["rb"]) - ((g["sh"] + g["sl"]) if inbs else 0.0)
    is_strip = (xs >= BS[0]) & (xs <= BS[1])
    kg = np.where(is_strip, k_top + k_bot, k_end)
    kc_half = 2 * E_PETG_MPA * bweb / wt
    mapH = {k: j for j, k in enumerate(iH)}
    mapN = {k: j for j, k in enumerate(iN)}
    oH, oN = 0, 2 * len(iH)
    oW = oN + 2 * len(iN)
    oB = oW + 3 * n
    ndof = oB + 3
    vh, vn, th = oB, oB + 1, oB + 2
    K0 = np.zeros((ndof, ndof))
    f = np.zeros(ndof)

    def EI_of(slot):
        return lambda x: E_ST * (2 * g["hz"] - (2 * BAND if slot[0] <= x <= slot[1] else 0.0)) * tp ** 3 / 12

    EI_H, EI_N = EI_of(g["Hs"]), EI_of(g["Ns"])
    for off, idx, EI in ((oH, iH, EI_H), (oN, iN, EI_N)):
        for e in range(len(idx) - 1):
            Lh = xs[idx[e + 1]] - xs[idx[e]]
            dd = [off + 2 * e + j for j in range(4)]
            K0[np.ix_(dd, dd)] += _hermite(EI(0.5 * (xs[idx[e]] + xs[idx[e + 1]])), Lh)
    lump = np.full(n, h)
    lump[0] = lump[-1] = h / 2
    for k in range(n):
        ui, um, uo = oW + 3 * k, oW + 3 * k + 1, oW + 3 * k + 2
        for a, b in ((ui, um), (um, uo)):
            kk = kc_half[k] * lump[k]
            K0[a, a] += kk
            K0[b, b] += kk
            K0[a, b] -= kk
            K0[b, a] -= kk
        K0[um, um] += kg[k] * lump[k]
    K0[vh, vh] += KB_BOLT
    K0[vn, vn] += KB_BOLT
    K0[vh, vn] -= KB_BOLT
    K0[vn, vh] -= KB_BOLT
    D0 = P0 / KB_BOLT
    f[vh] += KB_BOLT * D0
    f[vn] -= KB_BOLT * D0
    f[th] += Mz
    K0 += np.eye(ndof) * 1e-6
    contacts = []
    for k in range(n):
        x, Lk = xs[k], lump[k]
        if inH[k] and wH[k] > 0:
            contacts.append(("Hw", k, KP * wH[k] * Lk, [oH + 2 * mapH[k], oW + 3 * k], [1.0, -1.0]))
        if inN[k] and wN[k] > 0:
            contacts.append(("Nw", k, KP * wN[k] * Lk, [oW + 3 * k + 2, oN + 2 * mapN[k]], [1.0, -1.0]))
        if inH[k] and wwa[k] > 0:
            contacts.append(("W", k, KP * wwa[k] * Lk, [vh, th, oH + 2 * mapH[k]], [1.0, x - xb, -1.0]))
        if inN[k] and wnu[k] > 0:
            contacts.append(("Nut", k, KP * wnu[k] * Lk, [oN + 2 * mapN[k], vn, th], [1.0, -1.0, -(x - xb)]))
    active = np.ones(len(contacts), dtype=bool)
    rows_, cols_, vals_ = [], [], []
    for c, (_, _, _, dd, co) in enumerate(contacts):
        rows_ += [c] * len(dd)
        cols_ += list(dd)
        vals_ += list(co)
    Cm = sparse.csr_matrix((vals_, (rows_, cols_)), shape=(len(contacts), ndof))
    kk_all = np.array([c[2] for c in contacts])
    K0s = sparse.csc_matrix(K0)
    for it in range(300):
        K = (K0s + Cm.T @ sparse.diags(kk_all * active) @ Cm).tocsc()
        u = spsolve(K, f)
        gap = Cm @ u
        new = gap > 0
        if np.array_equal(new, active):
            break
        active = new
    else:
        raise RuntimeError("clamp contact iteration did not converge")
    q = {t: np.zeros(n) for t in ("Hw", "Nw", "W", "Nut")}
    for c, (t, k, kk, _, _) in enumerate(contacts):
        if active[c]:
            q[t][k] += kk * gap[c]
    r = SimpleNamespace(xs=xs, q=q, T=KB_BOLT * (D0 + u[vn] - u[vh]), theta=float(u[th]), xb=xb)
    r.lever = (float(((xs - xb) * q["W"]).sum()) - float(((xs - xb) * q["Nut"]).sum())) / max(r.T, 1e-9)

    def zone_mean(force, width):
        pr = np.where(width > 0, force / (np.maximum(width, 1e-9) * lump), 0.0)
        i = int(np.argmax(pr))
        j0, j1 = i, i
        while j0 > 0 and pr[j0 - 1] > 0.5 * pr[i]:
            j0 -= 1
        while j1 < n - 1 and pr[j1 + 1] > 0.5 * pr[i]:
            j1 += 1
        return force[j0:j1 + 1].sum() / (width[j0:j1 + 1] * lump[j0:j1 + 1]).sum(), pr[i], xs[i]

    r.pH = zone_mean(q["Hw"], wH)                            # head plate on the recess floor: zone mean, peak, x
    r.pN = zone_mean(q["Nw"], wN)                            # nut plate on the wall's outer face
    gw = np.array([kg[k] * u[oW + 3 * k + 1] for k in range(n)])   # ground reaction per unit x (- = pushed -y by the nut plate)
    st = is_strip
    share_top = k_top / (k_top + k_bot)
    qt, qb = gw * share_top, gw * (1 - share_top)
    t2 = wt ** 2
    sig_out = np.where(gw < 0, np.maximum(6 * np.abs(qt) * a_top * g["kt_out_top"], 6 * np.abs(qb) * a_bot * g["kt_out_bot"])
                       / t2, 0.0)
    sig_in = np.where(gw > 0, np.maximum(6 * qt * a_top * g["kt_in_top"], 6 * qb * a_bot * g["kt_in_bot"]) / t2, 0.0)
    r.sig_strip = float(max(sig_out[st].max(initial=0.0), sig_in[st].max(initial=0.0)))
    r.tau_strip = float(1.5 * np.maximum(np.abs(qt), np.abs(qb))[st].max(initial=0.0) / wt)
    r.q_strip = float(np.abs(gw[st]).max(initial=0.0))

    def plate_sigma(off, idx, EI, slot):
        best = 0.0
        for e in range(len(idx) - 1):
            x0_, x1_ = xs[idx[e]], xs[idx[e + 1]]
            Lh = x1_ - x0_
            we = u[off + 2 * e: off + 2 * e + 4]
            xm = 0.5 * (x0_ + x1_)
            Z = (2 * g["hz"] - (2 * BAND if slot[0] <= xm <= slot[1] else 0.0)) * tp ** 2 / 6
            for xi in (0.0, 1.0):
                d2 = np.array([(-6 + 12 * xi) / Lh ** 2, (-4 + 6 * xi) / Lh, (6 - 12 * xi) / Lh ** 2, (-2 + 6 * xi) / Lh])
                best = max(best, abs(EI(xm) * (d2 @ we)) / Z)
        return best

    r.sig_H = plate_sigma(oH, iH, EI_H, g["Hs"])
    r.sig_N = plate_sigma(oN, iN, EI_N, g["Ns"])
    a_nw = float((wnu * lump).sum())
    r.p_nut = r.T / a_nw if a_nw > 0 else 0.0                 # nut-side Ø9 washer on the nut plate: mean steel bearing
    a_wa = float((wwa * lump).sum())
    r.p_washer = r.T / a_wa if a_wa > 0 else 0.0              # head-side Ø9 washer on the head plate
    return r


def bef_line(xs, EI, k, p_):
    """Beam on a Winkler foundation k(x) (N/mm per mm) under a line load p(x) (N/mm), free ends; returns w(x)."""
    n = len(xs)
    K = np.zeros((2 * n, 2 * n))
    f = np.zeros(2 * n)
    for e in range(n - 1):
        Lh = xs[e + 1] - xs[e]
        dd = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        K[np.ix_(dd, dd)] += _hermite(EI[e], Lh)
        km, pm_ = 0.5 * (k[e] + k[e + 1]) * Lh, 0.5 * (p_[e] + p_[e + 1]) * Lh
        for i in (2 * e, 2 * e + 2):
            K[i, i] += km / 2
            f[i] += pm_ / 2
    return np.linalg.solve(K + np.eye(2 * n) * 1e-9, f)[0::2]


def washer_beyond(g, r, up):
    """Washer contact beyond the plate's slot band, above it (up) or below it: (half-width profile f(dx), z-centroid
    distance from the bolt). Uniform pressure: a smaller lever than an edge-loaded contact, so the prying T comes out high."""
    po = g["po"]
    edge = (po + BAND) if up else (BAND - po)

    def hw(dx):
        return max(0.0, math.sqrt(max(0.0, r * r - dx * dx)) - edge)

    hh = 0.005
    A = Az = 0.0
    for i in range(int(2 * r / hh)):
        x = -r + (i + 0.5) * hh
        c = math.sqrt(max(0.0, r * r - x * x))
        if c > edge:
            A += (c - edge) * hh
            Az += (c * c - edge * edge) / 2 * hh
    return hw, Az / A


def clamp_tilt(g, xb, Fz, up=True, root_soft=ROOT_SOFT, k_end=None, h=0.05):
    """A vertical load Fz at the track plane tilts the bolt about X. With no friction and no preload the tilt couple is the
    prying couple T (z_h + z_n) = Fz (Y_T - y_c), y_c = the head plate's bearing face (the innermost place the shear can
    react: the largest moment). Up (5 cm front-corner drop): the nut washer's top pushes the nut plate's top strip into the
    PETG top strip (outer face), the head washer's bottom pushes the head plate's bottom strip into the PETG bottom strip
    (inner face). Down (the §8 5 kg hang): the other two. Each plate strip is a beam on the PETG strip (and the uncut band)."""
    k_end = g["k_end"] if k_end is None else k_end
    wt, tp = g["web_t"], g["tp"]
    hwN, zN = washer_beyond(g, g["r_wn"], up)
    hwH, zH = washer_beyond(g, g["r_wh"], not up)
    T = Fz * (F.Y_T - g["y_c"]) / (zN + zH)
    a_top, a_bot = arms(g)
    out = SimpleNamespace(T=T, lever=zN + zH)
    for side, (Xa, Xb), slot, hwf, a, kt in (
            ("N", g["N"], g["Ns"], hwN, a_top if up else a_bot, g["kt_out_top"] if up else g["kt_out_bot"]),
            ("H", g["H"], g["Hs"], hwH, a_bot if up else a_top, g["kt_in_bot"] if up else g["kt_in_top"])):
        xs = np.round(np.arange(Xa, Xb + 1e-9, h), 6)
        EI = np.array([E_ST * ((g["hz"] - BAND) if slot[0] <= 0.5 * (a_ + b_) <= slot[1] else g["hz"]) * tp ** 3 / 12
                       for a_, b_ in zip(xs[:-1], xs[1:])])
        st = (xs >= BS[0]) & (xs <= BS[1])
        k = np.where(st, strip_k(max(a, 0.05), wt) / root_soft, k_end / 2)
        pz = np.array([hwf(x - xb) for x in xs])
        pz = pz / (pz.sum() * h) * T
        w = bef_line(xs, EI, k, pz)
        qmax = float((k * w)[st].max())
        setattr(out, "q" + side, qmax)
        setattr(out, "sig_" + side, 6 * qmax * a / wt ** 2 * kt)
        setattr(out, "tau_" + side, 1.5 * qmax / wt)
    return out


CLAMP_R5 = dict(name="round 5 as built", H=(H0, H0 + P_LEN), Hs=HS, N=(N0, N0 + P_LEN), Ns=NS,
                W=(min(H0, N0), max(H0, N0) + P_LEN), hz=P_H / 2, po=PLATE_MID - BOLT_Z,
                rt=p.PLATE_RECESS_Z - BOLT_Z, rb=p.PLATE_RECESS_Z + BOLT_Z, sh=SLOT_HI - BOLT_Z, sl=-SLOT_LO + BOLT_Z,
                web_t=WEB_T, tp=TP_MIN, k_end=K_END, r_wh=WASHER_R, r_wn=WASHER_R, kt_out_top=KT_SHARP,
                kt_out_bot=KT_SHARP, kt_in_top=KT_SHARP, kt_in_bot=KT_SHARP, y_c=y_rec)
# round 4's FIX as it was modelled there (plates Z_A +-5, bolt on Z_A, PETG band +-5.2, slot -1.8..+2.55, plate 2.0): the
# same function must give back round 4's FIX rows (3.02 / 3.05 / 3.42 in the drop, 6.45 at the reverse stall)
CLAMP_R4FIX = dict(CLAMP_R5, name="round 4 FIX model", po=0.0, rt=5.2, rb=5.2, sh=2.55, sl=1.8, tp=2.0)
a_top5, a_bot5 = arms(CLAMP_R5)
XB = [F.AXLE_DX + d for d in (-F.IDLER_SLOT, -F.IDLER_SLOT / 2, 0.0, F.IDLER_SLOT / 2, F.IDLER_SLOT)]
X_FRONT = XB[-1]                                     # the slot's front end (§8 test 1 position)
ARM_YAW = F.Y_T - p.JACK_Y                           # 29.6: the jack screw pushes the head at |y| 25.4
print(f"round-5 clamp in the bolt frame: plates +-{CLAMP_R5['hz']:.1f} (offset {CLAMP_R5['po']:+.2f}), slot band"
      f" +-{BAND}; PETG band {-CLAMP_R5['rb']:+.2f}..{CLAMP_R5['rt']:+.2f}, bolt slot {-CLAMP_R5['sl']:+.2f}..{CLAMP_R5['sh']:+.2f};"
      f" strips {CLAMP_R5['rt'] - CLAMP_R5['sh']:.2f} (top) and {CLAMP_R5['rb'] - CLAMP_R5['sl']:.2f} (bottom) tall, plates bear"
      f" at arms {a_top5:.3f} / {a_bot5:.3f} from their roots (round 4 FIX: {arms(CLAMP_R4FIX)[0]:.3f} / {arms(CLAMP_R4FIX)[1]:.3f})")


def yaw_worst(g, R, P0s=(0.0,), xbs=None, **kw):
    """Worst value of each clamp result over the slot positions (and preloads)."""
    res = [clamp_yaw(g, xb, R * ARM_YAW, P0=P0, **kw) for xb in (xbs or XB) for P0 in P0s]
    pick = SimpleNamespace()
    for key in ("T", "sig_strip", "tau_strip", "q_strip", "sig_H", "sig_N", "p_nut", "p_washer"):
        setattr(pick, key, max(getattr(r, key) for r in res))
    pick.theta = max(abs(r.theta) for r in res)
    pick.T_min = min(r.T for r in res)
    pick.pH = max((r.pH + (r.xb,) for r in res), key=lambda t: t[0])
    pick.pN = max((r.pN + (r.xb,) for r in res), key=lambda t: t[0])
    pick.x_strip = max(res, key=lambda r: r.sig_strip).xb
    pick.lever = min(r.lever for r in res)
    pick.res = res
    return pick


def tilt_worst(g, Fz, up=True, xbs=None, **kw):
    res = [(xb, clamp_tilt(g, xb, Fz, up=up, **kw)) for xb in (xbs or XB)]
    pick = SimpleNamespace(T=res[0][1].T, lever=res[0][1].lever)
    for key in ("sig_N", "tau_N", "sig_H", "tau_H", "qN", "qH"):
        setattr(pick, key, max(getattr(r, key) for _, r in res))
    pick.x_H = max(res, key=lambda t: t[1].sig_H)[0]
    pick.x_N = max(res, key=lambda t: t[1].sig_N)[0]
    return pick


# yaw at the idler (no friction, no preload credited): sustained pretension, everyday reverse, reverse stall
yS = yaw_worst(CLAMP_R5, L.R_sus, P0s=(0.0, 80.0))
yC = yaw_worst(CLAMP_R5, L.R_idler_cyc)
yR = yaw_worst(CLAMP_R5, L.R_idler_stall)
print(f"idler clamp yaw (no friction, no preload credited; worst of x {XB[0]:.0f}-{XB[-1]:.0f}): reverse stall"
      f" {L.R_idler_stall:.1f} N -> M {L.R_idler_stall * ARM_YAW:.0f} N*mm, prying bolt tension T {yR.T_min:.0f}-{yR.T:.0f} N"
      f" (lever >= {yR.lever:.2f} mm between the washers' resultants), strips up to {yR.q_strip:.2f} N/mm out of plane, bolt"
      f" body yaw <= {yR.theta * 1000:.2f} mrad; steel plates {yR.sig_H:.0f} / {yR.sig_N:.0f} MPa")
for tag, y, sf in (("pretension 10 N sustained (P 0 or 80 N)", yS, SF_CYCLIC),
                   (f"everyday reverse {L.R_idler_cyc:.1f} N cyclic", yC, SF_CYCLIC),
                   (f"reverse stall {L.R_idler_stall:.1f} N", yR, SF_STATIC)):
    check(f"B5 idler head plate on the recess floor (zone mean, peak {y.pH[1]:.1f} at x {y.pH[2]:.1f}, bolt at x"
          f" {y.pH[3]:.0f}), {tag}", y.pH[0], False, sf)
    check(f"B6 idler nut plate on the wall's outer face (zone mean, peak {y.pN[1]:.1f} at x {y.pN[2]:.1f}, bolt at x"
          f" {y.pN[3]:.0f}), {tag}", y.pN[0], False, sf)
    check(f"B12 8.0 mm PETG between the plates: strip root beside the bolt slot, bending across layers (Kt {KT_SHARP} at"
          f" every root), {tag}", y.sig_strip, True, sf)
    check(f"B13 strip root, shear along the layer, {tag}", y.tau_strip, True, sf, shear=True)
# drop: the 5 cm front corner tilts the idler bolt about X
tD = tilt_worst(CLAMP_R5, L.drop, up=True)
print(f"idler clamp tilt, 5 cm front corner {L.drop:.1f} N up at the track plane: prying T {tD.T:.0f} N (lever"
      f" {tD.lever:.2f}); top strip (nut side) {tD.qN:.2f} N/mm, bottom strip (head side) {tD.qH:.2f} N/mm out of plane")
print(f"  drop worst bolt positions: nut side x {tD.x_N:.0f}, head side x {tD.x_H:.0f}")
check(f"B15 top strip root under the nut plate (outer face; Kt {KT_SHARP}), across layers, 5 cm front corner", tD.sig_N, True,
      SF_STATIC, drop=True)
check(f"B15 bottom strip root under the head plate (inner face: the recess floor's sharp edge, Kt {KT_SHARP}), 5 cm front"
      f" corner", tD.sig_H, True, SF_STATIC, drop=True)
check("B15 strip root, shear along the layer, 5 cm front corner", max(tD.tau_N, tD.tau_H), True, SF_STATIC, shear=True,
      drop=True)
# the drop's shear: the nut plate has nothing over it (no roof, the stops only locate X), and the bolt is 1.05 mm under the
# PETG slot's top, so the head plate's slot edge takes the shear and its top back edge meets the recess's 45° roof after 0.4
check(f"B4 head plate's top back edge on the recess's 45° roof (all of the drop shear on a 0.3 mm wide line, {P_LEN} long),"
      f" 5 cm front corner", L.drop / (P_LEN * 0.3), False, SF_STATIC, drop=True)
# steel plates and steel bearing (reverse stall)
check_metal(f"B16 steel head plate bending (slotted section, {TP_MIN} thick), reverse stall", yR.sig_H, SY_PLATE_MPA)
check_metal(f"B16 steel nut plate bending (slotted section, {TP_MIN} thick), reverse stall", yR.sig_N, SY_PLATE_MPA)
check_metal(f"B17 Ø9 washer on the nut plate: mean steel bearing at T {yR.T:.0f} N, reverse stall", yR.p_nut, SY_PLATE_MPA)
check_metal(f"B17 Ø9 washer on the head plate: mean steel bearing at T {yR.T:.0f} N, reverse stall", yR.p_washer, SY_PLATE_MPA)
A_NUT_FACE = math.pi / 4 * (F.NUT[0] ** 2 - (2 * R_HOLE_W) ** 2)
check_metal(f"B17 M3 nut's face on its Ø9 washer (Ø{F.NUT[0]} - Ø{2 * R_HOLE_W}) at T {yR.T:.0f} N, reverse stall",
            yR.T / A_NUT_FACE, SY_PLATE_MPA)

# --- the nut plate's seat: end stops and lip (round 5, the designer's addition) ----------------------------------------
# What reaches them. Nothing in the clamp rows above is credited to friction. But friction is a DEMAND on the stops: the
# bolt body yaws about the jack screw's tip (the theta above), so the nut-side washer, 14.6 mm from the jack line, wants to
# slide rearward on the nut plate by theta x 14.6 (about 0.01-0.03 mm), far more than a 1 mm PETG stop needs to build up
# the full friction force. So the washer drags the plate into its rear stop with mu (T + P), capped by R (friction can't
# carry more than the bolt receives; the jack screw carries the rest). Oiled steel (mu 0.2, BUILD_GUIDE step 3) with the
# step-3 snug still present (P 89 N, S1) is used, as in S1. Credit is taken neither for the PETG face's friction behind
# the plate nor for the jack screw's share. While tensioning, the jack pushes the bolt forward and the washer drags the plate
# into its FRONT stop with mu P. The head plate's ends bear on the solid recess ends (x 108: the buttress face; x 129).
T_SNUG_NMM, K_OIL, MU_OIL, K_DRY, MU_DRY = 40.0, 0.15, 0.2, 0.2, 0.6
P_snug = T_SNUG_NMM / (K_OIL * 3.0)                  # 89 N (S1)
STOP_ARM = p.LIP_OUT / 2                             # 0.5: plate end bears on the stop's face over |y| 38-39
STOP_BEAR = min(p.LIP_OUT, TP_MIN) * P_H             # 10 mm²: 1.0 of the plate's thickness x its 10 mm height


def stop_rows(tag, Fx, sf, info=False, stop_w=None):
    w = p.STOP_W if stop_w is None else stop_w
    check(f"B18 nut plate's end on its end stop: bearing ({min(p.LIP_OUT, TP_MIN):.1f} x {P_H:.0f}), {tag}",
          Fx / STOP_BEAR, False, sf, info=info)
    check(f"B18 end stop root ({w} x {STOP_H:.1f} at the wall face, plate at arm {STOP_ARM}): bending (Kt {KT_SHARP}, sharp"
          f" corner on the loaded face), {tag}", bend_rect(Fx * STOP_ARM, STOP_H, w), False, sf, Kt=KT_SHARP, info=info)
    check(f"B18 end stop root: shear, {tag}", 1.5 * Fx / (w * STOP_H), False, sf, shear=True, info=info)


def stop_demand(R, T):
    return min(R, MU_OIL * (T + P_snug))


yS0 = yaw_worst(CLAMP_R5, L.R_sus)                   # prying T with no preload (the snug's P is added in stop_demand)
stop_cases = ((f"pretension {L.R_sus:.0f} N sustained", L.R_sus, yS0.T, SF_CYCLIC),
              (f"everyday reverse {L.R_idler_cyc:.1f} N cyclic", L.R_idler_cyc, yC.T, SF_CYCLIC),
              (f"reverse stall {L.R_idler_stall:.1f} N", L.R_idler_stall, yR.T, SF_STATIC))
for tag, R, T, sf in stop_cases:
    Fx = stop_demand(R, T)
    stop_rows(f"rear stop, friction drag min(R, mu (T + P)) = min({R:.1f}, {MU_OIL} x ({T:.0f} + {P_snug:.0f})) ="
              f" {Fx:.1f} N, {tag}", Fx, sf)
F_tens = MU_OIL * P_snug
stop_rows(f"front stop, tensioning (the jack slides the snug bolt forward; the washer drags the plate, mu P {F_tens:.1f} N)",
          F_tens, SF_STATIC)
check(f"B18h head plate's end on the recess end (x 108, solid buttress; {TP_MIN} x {P_H:.0f}), reverse stall"
      f" {stop_demand(L.R_idler_stall, yR.T):.1f} N", stop_demand(L.R_idler_stall, yR.T) / (TP_MIN * P_H), False, SF_STATIC)
# lip: in service it holds only the plate's own weight. The bolt rests on the PETG slot floor (Z_A - 1.7 printed), 0.2 above
# the plates' slot bottoms, so downward bolt loads go to the PETG, not to the plates; upward ones lift the plate off its lip
# (it then rises at most 0.4, to Z_A + 5.2: still between the stops, which reach Z_A + 5.2).
LIP_ROOT_H = p.LIP_FACE + p.LIP_OUT                   # 2.0: lip depth at the wall face (1.0 face + 45° underside)
LIP_BEAR = min(p.LIP_OUT, TP_MIN) * P_LEN            # 20.6 mm²: the plate's bottom edge on the lip, 1.0 of its thickness
F_lip_drop = m_nut_plate * 1e-3 * G_MS2 * (2 * H_DROP_MM / DELTA_MM)
check(f"B19 lip under the nut plate, root bending (Kt {KT_SHARP}): the plate's own mass at the drop's"
      f" {2 * H_DROP_MM / DELTA_MM:.0f} g ({F_lip_drop:.2f} N)", bend_rect(F_lip_drop * STOP_ARM, P_LEN, LIP_ROOT_H), False,
      SF_STATIC, Kt=KT_SHARP, drop=True)

# jack screw: self-tapped M3 in the Ø2.6 printed pilot through the 6.5 mm buttress; teardrop leaves 270° of thread
L_jack = p.JACK_X[1] - p.JACK_X[0]
A_strip = math.pi * 3.0 * L_jack * 0.5 * 0.75        # thread-fill 0.5 (rounds 1-2), teardrop 270°
F_JACK_CAP = A_strip * allow_mpa(True, True)         # 143.6 N at the across-layer shear allowable (DFM's "142 N")
check(f"B7 jack-screw thread strip-out ({L_jack:.1f} mm, Ø{p.JACK_PILOT} pilot), reverse stall {L.R_idler_stall:.1f} N",
      L.R_idler_stall / A_strip, True, SF_STATIC, shear=True)
check(f"B8 jack-screw thread, pretension {L.R_sus:.0f} N sustained", L.R_sus / A_strip, True, SF_CYCLIC, shear=True)
# S1: tensioning slides the snugged bolt: the head's Ø9 washer on the head plate and the nut's Ø9 washer on the nut plate,
# both oiled steel on steel (BUILD_GUIDE step 3): 2 mu P + 2 T0
F_slide = 2 * MU_OIL * P_snug + L.R_sus
check(f"B7t jack-screw thread while tensioning: snug {T_SNUG_NMM / 1000:.2f} N*m (K {K_OIL}: P {P_snug:.0f} N), oiled plates"
      f" (mu {MU_OIL}): thrust {F_slide:.0f} N", F_slide / A_strip, True, SF_STATIC, shear=True)
h_btr = p.JACK_TOP - (F.FLOOR_Z + F.FLOOR_T)          # 14
lug = y_boss - p.JACK_Y                               # 2.6: jack axis to the solid block/column face
check(f"B9 buttress lug at the block face (y {y_boss:.0f}): bending, reverse stall (Kt {KT_SHARP})",
      bend_rect(L.R_idler_stall * lug, h_btr, L_jack), False, SF_STATIC, Kt=KT_SHARP)
check_metal(f"B10 idler M3 x 40 class 12.9: bending at the head face (y {y_boss:.0f}), reverse stall x {F.Y_T - y_boss:.0f}",
            bend_round(L.R_idler_stall * (F.Y_T - y_boss), D3_M3), SY_129_MPA)
check_metal(f"B11 idler M3 x 40 class 12.9: bending at the outer face, 5 cm front corner x {arm_bolt:.0f}",
            bend_round(L.drop * arm_bolt, D3_M3), SY_129_MPA, drop=True)


# ---- C. drivetrain concept C: N20 rolled 45° in the diamond pocket; nacelle 2 mm, skin 2 mm, track plane 11 mm out ------
hx, hy = (M.gb_w + p.GB_CLR) / 2, (M.gb_h + p.GB_CLR) / 2     # printed pocket half sizes 6.1 x 5.1 (CAD + HOLE_COMP)
y_face = F.MOTOR_FACE_Y
y_house = F.HALF_W_OUT + F.HOUSING_OUT                # 42: housing face = nacelle root
y_can_end = y_face - M.gb_len - M.can_len            # 19.5
e_c = 0.3                                            # contact line inside the gearbox face (its edge radius): assumption
L_c = y_face - y_house - e_c                         # 1.7: nacelle wall from its root to the contact line
t_n, t_s = F.NACELLE_WALL, F.SKIN
y_b = y_can_end + (y_face - y_can_end) / 3           # resultant of a triangular trough reaction along the motor
lev_v = (F.Y_T - y_b) / (y_face - y_b)               # 1.67: vertical (drop) loads, can on the open V-trough
y_pin = y_in_face                                    # pocket inner end in the wall (spec §4 lever)
lev_h = (F.Y_T - y_pin) / (y_face - y_pin)           # 2.05: horizontal loads (the open trough can't push sideways)
ring = section(y=(y_house + y_face) / 2, window=(-25, 25, 8, 49))[0]
A_ring, I_ring = ring[0], ring[2]
c_ring = max(abs(z) for z in (F.Z_A + ns["NACELLE"][1][1], F.Z_A + ns["NACELLE"][3][1])) - F.Z_A
w_mid = 2 * hy * math.sqrt(2)                        # pocket width at the axis height (printed)
d_hole = p.BOSS_HOLE_D                               # Ø4.5 printed
A_cut = (w_mid - d_hole) * t_s
xl = (d_hole / 2 + w_mid / 2) / 2                    # ligament centre
h_eff = (hx * math.sqrt(2) - xl) - (xl - hy * math.sqrt(2))   # skin height at the ligament centre
b_face = min(M.gb_w, M.gb_h)                         # loaded width: the narrower gearbox face (10)
b_walls = (2 * hx + t_n) + (2 * hy + t_n)            # both upper walls at mid-thickness


def k_wall(Lc):
    """Vertical stiffness of the two upper nacelle walls as cantilever plates from the housing face (bending + shear)."""
    kb = 1.0 / (4 * Lc ** 3 / (E_PETG_MPA * t_n ** 3) + Lc / (5 / 6 * G_PETG_MPA * t_n))
    return kb * b_walls * 0.5


k_skin = 2 * A_cut * G_PETG_MPA / h_eff              # skin as a shear panel between its upper and lower edges
print(f"motor pocket: lever {lev_v:.2f} R vertical (trough reaction at y {y_b:.1f}), {lev_h:.2f} R horizontal (spec §4 still"
      f" says 1.87 R: stale since the face moved to {y_face}); nacelle ring A {A_ring:.1f} mm², I {I_ring:.0f} mm^4"
      f" (build123d), c {c_ring:.2f}; skin cut {A_cut:.2f} mm² (width {w_mid:.2f} - hole {d_hole}) x {t_s}, h_eff {h_eff:.2f};"
      f" k_walls {k_wall(L_c):.0f} N/mm (L {L_c:.1f}), k_skin {k_skin:.0f} N/mm")
sh_skin = k_skin / (k_skin + k_wall(L_c))
sh_wall = 1.5 * k_wall(L_c) / (1.5 * k_wall(L_c) + 0.6 * k_skin)


def skin_tau(Ft, share=None, ts=t_s):
    s = sh_skin if share is None else share
    return 1.5 * (s * Ft / 2) / ((w_mid - d_hole) * ts)


def wall_sigma(Ft, share=None, Lc=L_c):
    s = sh_wall if share is None else share
    N = s * Ft / (2 * math.cos(math.radians(45)))
    return bend_rect(N * Lc, b_face, t_n)


Ft_drop = lev_v * L.drop
check(f"C1 skin ({t_s:.0f} mm) diaphragm shear across layers, 5 cm rear corner: nacelle reaction {Ft_drop:.1f} N, skin share"
      f" {sh_skin * 100:.0f} %", skin_tau(Ft_drop), True, SF_STATIC, shear=True, drop=True)
check(f"C2 nacelle wall root bending (pocket face in tension, no notch), 5 cm rear corner, wall share {sh_wall * 100:.0f} %",
      wall_sigma(Ft_drop), False, SF_STATIC, drop=True)
check(f"C3 nacelle root, tube bending (sharp outer corner in tension, Kt {KT_SHARP}), 5 cm rear corner",
      Ft_drop * L_c * c_ring / I_ring, False, SF_STATIC, Kt=KT_SHARP, drop=True)
check("C4 nacelle root, tube shear (2 V/A), 5 cm rear corner", 2 * Ft_drop / A_ring, True, SF_STATIC, shear=True, drop=True)
check("C5 gearbox front edge bearing on the pocket faces (1 mm x face width), 5 cm rear corner",
      Ft_drop / (2 * math.cos(math.radians(45))) / (b_face * 1.0), False, SF_STATIC, drop=True)
for lab, R, sf in ((f"stall {L.R_stall:.1f} N", L.R_stall, SF_STATIC), (f"pretension {L.R_sus:.0f} N sustained", L.R_sus, SF_CYCLIC)):
    check(f"C6 skin diaphragm shear, track {lab} (horizontal, {lev_h:.2f} R)", skin_tau(lev_h * R), True, sf, shear=True)
    check(f"C7 nacelle wall root bending, track {lab}", wall_sigma(lev_h * R), False, sf)
T_corner = T_DESIGN_NMM / M.gb_w                     # gearbox corners bear on the long faces: couple arm 12
check(f"C8 reaction torque {T_DESIGN_NMM:.0f} N*mm: gearbox corner bearing ({T_corner:.1f} N over {M.gb_len:.0f} x 1 mm)",
      T_corner / (M.gb_len * 1.0), False, SF_STATIC)


def annular_plate(a, b, loads, nu=NU_PETG, n=400):
    """Annular plate, outer edge r = a clamped, inner edge r = b free; loads = [(r0, P)] ring loads (N).
    Returns max |M_r| at the clamped edge and max |M_theta| over the plate (N*mm/mm). D cancels."""
    r = np.linspace(b, a, n)
    Mr = np.zeros(n)
    Mt = np.zeros(n)
    for r0, P in loads:
        c4 = P / (8 * math.pi)
        lr0 = math.log(r0)
        Am = np.zeros((6, 6))
        rhs = np.zeros(6)
        Am[0, 1], Am[0, 2] = 2 * (1 + nu), -(1 - nu) / b ** 2
        Am[1, :] = [1, r0 ** 2, lr0, -1, -r0 ** 2, -lr0]
        rhs[1] = c4 * r0 ** 2 * lr0
        Am[2, :] = [0, 2 * r0, 1 / r0, 0, -2 * r0, -1 / r0]
        rhs[2] = c4 * (2 * r0 * lr0 + r0)
        Am[3, :] = [0, 2, -1 / r0 ** 2, 0, -2, 1 / r0 ** 2]
        rhs[3] = c4 * (2 * lr0 + 3)
        la = math.log(a)
        Am[4, 3:] = [1, a ** 2, la]
        rhs[4] = -c4 * a ** 2 * la
        Am[5, 3:] = [0, 2 * a, 1 / a]
        rhs[5] = -c4 * (2 * a * la + a)
        A1, A2, A3, B1, B2, B3 = np.linalg.solve(Am, rhs)
        inner = r <= r0
        w1 = np.where(inner, 2 * A2 * r + A3 / r, 2 * B2 * r + B3 / r + c4 * (2 * r * np.log(r) + r))
        w2 = np.where(inner, 2 * A2 - A3 / r ** 2, 2 * B2 - B3 / r ** 2 + c4 * (2 * np.log(r) + 3))
        Mr += -(w2 + nu * w1 / r)
        Mt += -(w1 / r + nu * w2)
    return abs(Mr[-1]), float(np.max(np.abs(Mt))), float(np.max(np.abs(Mr)))


a_eq = math.sqrt(4 * hx * hy / math.pi)              # skin: area-equivalent clamped circle of the printed pocket
b_in = d_hole / 2
r_wash = 2.4                                         # thrust washer bears near the hole edge (stiff washer, soft skin)


def skin_out_of_plane(P, inward, ts=t_s):
    if inward:   # thrust washer, ring near the hole; tension at the clamped edge on the outer face (smooth)
        mr_edge, mt, mr = annular_plate(a_eq, b_in, [(r_wash, P)])
        return 6 * max(mr_edge, mt, mr) / ts ** 2, 1.0
    rings = np.linspace(b_in + 0.05, a_eq - 0.05, 40)  # gearbox face: uniform pressure; tension at the edge on the
    w = rings / rings.sum()                            # inner face, i.e. the sharp pocket corner (Kt 2.5)
    mr_edge, mt, mr = annular_plate(a_eq, b_in, [(r0, P * wi) for r0, wi in zip(rings, w)])
    return 6 * max(mr_edge, mt, mr) / ts ** 2, KT_SHARP


s_in, k_in = skin_out_of_plane(L.side, True)
s_out, k_out = skin_out_of_plane(L.side, False)
check(f"C9 skin out of plane: side {L.side:.0f} N inward on the thrust washer (annular plate a {a_eq:.2f}, hole r {b_in})",
      s_in, True, SF_CYCLIC, Kt=k_in)
check(f"C10 skin out of plane: side {L.side:.0f} N outward on the gearbox face, the motor's outward stop (Kt {KT_SHARP} at"
      f" the pocket corner)", s_out, True, SF_CYCLIC, Kt=k_out)
Ft_house = lev_v * L.drop
check(f"C11 wall bending round the motor housing (Ø{2 * p.HOUSING_HALF_X:.1f} equivalent, Kt {KT_CHAMFER}), 5 cm rear corner",
      plate_boss_moment_stress(Ft_house * (y_face - e_c - y_mid), p.HOUSING_HALF_X, t_w, KT_CHAMFER), True, SF_STATIC,
      drop=True)
F_in_h = (lev_h - 1) * L.R_stall
F_tie = F_in_h + 30.0
z_tun = F.Z_A - M.can_d / 2 - 0.2                   # tunnel top: the cheeks bridge it
cheeks = section(y=p.TIE_Y, window=(-14, 14, z_tun + 0.05, F.Z_A))
cheek = min(cheeks, key=lambda c: c[0])
h_ch = p.TROUGH_TOP - z_tun                          # cheek depth above the tunnel
b_ch = cheek[0] / h_ch
check(f"C12 trough cheek bridge over the tie tunnel: tie {F_tie:.0f} N (can rear reaction {F_in_h:.1f} N + 30 N preload)",
      bend_rect(F_tie / 2 * p.TIE_W / 8, b_ch, h_ch), False, SF_STATIC)
# N20 shaft (bought steel): D-section Ø3, flat 2.5 from the far side; minimum section modulus over every bending direction.
# Target: steel, so SF 1.5 on yield for short-term static loads (rounds 1-3 convention; the printed-part 3 and 4 don't
# apply); the Architect's own limit is SF 2 at stall. Rotating bending under the track tension is checked for fatigue below.
gs = 600
hh = M.shaft_d / gs
pts = [(-M.shaft_d / 2 + (i + 0.5) * hh, -M.shaft_d / 2 + (j + 0.5) * hh) for i in range(gs) for j in range(gs)]
pts = np.array([q for q in pts if q[0] ** 2 + q[1] ** 2 <= (M.shaft_d / 2) ** 2 and q[1] <= M.shaft_flat - M.shaft_d / 2])
cx, cy = pts.mean(axis=0)
Zmin = 1e9
for ang in np.linspace(0, math.pi, 181):
    uu = (pts[:, 0] - cx) * math.cos(ang) + (pts[:, 1] - cy) * math.sin(ang)
    Zmin = min(Zmin, (uu ** 2).sum() * hh * hh / (np.abs(uu).max() + hh / 2))
check_metal(f"C13 N20 shaft (bought steel), arm {F.SHAFT_ARM:.1f}, Z_min {Zmin:.3f} mm³: stall {L.R_stall:.1f} N (target 1.5"
            f" on yield; the Architect's 2 also met)", L.R_stall * F.SHAFT_ARM / Zmin, SY_ROD_MPA)
check_metal(f"C13 N20 shaft, arm {F.SHAFT_ARM:.1f}: 5 cm corner {L.drop:.1f} N", L.drop * F.SHAFT_ARM / Zmin, SY_ROD_MPA,
            drop=True)

# ---- D. floor under the battery (5 cm drop) ---------------------------------------------------------------------------
inner_span = 2 * y_in_face
BATT = HP.BATT_2X18650_LONG
a_drop_g = 2 * H_DROP_MM / DELTA_MM
F_batt = BATT.mass_g * 1e-3 * G_MS2 * a_drop_g
c_b = BATT.width
check(f"D1 floor mid-span under the battery, 5 cm ({a_drop_g:.0f} g x {BATT.mass_g:.0f} g)",
      bend_rect(F_batt / 2 * (inner_span / 2 - c_b / 4) / BATT.length, 1.0, F.FLOOR_T), False, SF_STATIC, drop=True)
check(f"D2 floor at the strap slots |y| {p.STRAP_Y} (Kt 2.5, square ends), 5 cm",
      bend_rect(F_batt / 2 * (inner_span / 2 - p.STRAP_Y) / (BATT.length - p.STRAP_L), 1.0, F.FLOOR_T), False, SF_STATIC,
      Kt=2.5, drop=True)
# ---- E. lid columns with heat-set inserts: rover lifted by the lid (2 x weight on 4 screws) ----------------------------
F_scr = 2 * L.W / 4
ins_len = 5.7
check(f"E1 insert knurl shear-out of the column, lifted by the lid {F_scr:.1f} N per insert",
      F_scr / (math.pi * p.INSERT_D * ins_len), True, SF_STATIC, shear=True)
A_col = math.pi / 4 * (p.COLUMN_D ** 2 - p.INSERT_D ** 2)
check("E2 column tension (Z) round the insert, lifted by the lid", F_scr / A_col, True, SF_STATIC)

# ---- advisory: bounds, sensitivities, proof loads, S1 table, the FIX ---------------------------------------------------
check(f"A4/A5 Winkler peaks: nut edge {nb_pk:.1f}, inner hole edge (peak), 5 cm drop", ib_pk, False, SF_STATIC, info=True)
F_prf = 5.0 * G_MS2
check(f"proof 5 kg ({F_prf:.0f} N) at the wheel rim centre: boss collar", plate_boss_moment_stress(F_prf * arm_w, a_road, t_w,
      KT_CHAMFER), True, SF_PROOF, info=True)
check("proof 5 kg at the wheel rim centre: nut-trap bearing", pin_bearing(F_prf, arm_bolt, F.NUT[0])[0], False, SF_PROOF,
      info=True)
check_metal("proof 5 kg at the rim centre: M3 class 12.9 at the outer face", bend_round(F_prf * arm_bolt, D3_M3), SY_129_MPA,
            SF_PROOF, info=True)
check_metal("if A2-70 (fully threaded stainless) bolts are fitted instead: 5 cm drop", bend_round(L.drop * arm_bolt, D3_M3),
            SY_A2_70_MPA, info=True)
# clamp (round 5): peaks, corner factors, sensitivities, the §8 proof loads, the round-4 FIX cross-check, options
check(f"B5 head plate on PETG, reverse stall: PEAK (at a width step of the 1-D model) {yR.pH[1]:.1f} at x {yR.pH[2]:.1f}",
      yR.pH[1], False, SF_STATIC, info=True)
check(f"B6 nut plate on PETG, reverse stall: PEAK {yR.pN[1]:.1f} at x {yR.pN[2]:.1f}", yR.pN[1], False, SF_STATIC, info=True)
check("B15 bottom strip root under the head plate, 5 cm front corner, WITHOUT the corner Kt (nominal)", tD.sig_H / KT_SHARP,
      True, SF_STATIC, info=True)
tK = tilt_worst(dict(CLAMP_R5, kt_out_top=1.0), L.drop, up=True)
check("B15 top strip root under the nut plate with Kt 1.0 (the outer face is flat at that root), 5 cm front corner", tK.sig_N,
      True, SF_STATIC, info=True)


def bolt_frame(bz):
    """CLAMP_R5 with the bolt axis at Z_A + bz instead of on the printed slot floor."""
    return dict(CLAMP_R5, po=PLATE_MID - bz, rt=p.PLATE_RECESS_Z - bz, rb=p.PLATE_RECESS_Z + bz, sh=SLOT_HI - bz,
                sl=-SLOT_LO + bz)


for lab, g_, kw in (("roots rigid (root_soft 1.0)", CLAMP_R5, dict(root_soft=1.0)),
                    ("roots twice as soft (2.0)", CLAMP_R5, dict(root_soft=2.0)),
                    ("uncut band 3x softer (k_end 10000)", CLAMP_R5, dict(k_end=10000.0)),
                    ("uncut band 3x stiffer (k_end 90000)", CLAMP_R5, dict(k_end=90000.0)),
                    ("metric 2.0 mm plates", dict(CLAMP_R5, tp=2.0), {}),
                    ("bolt on the CAD slot floor (Z_A - 0.3)", bolt_frame(-0.3), {}),
                    ("bolt up against the plates' slot tops (Z_A + 0.0)", bolt_frame(0.0), {})):
    yy = yaw_worst(g_, L.R_idler_stall, **kw)
    tt = tilt_worst(g_, L.drop, up=True, **kw)
    check(f"sensitivity, {lab}: strip root (Kt {KT_SHARP}), reverse stall", yy.sig_strip, True, SF_STATIC, info=True)
    check(f"sensitivity, {lab}: strip roots (Kt {KT_SHARP}), 5 cm front corner", max(tt.sig_N, tt.sig_H), True, SF_STATIC,
          info=True)
    check(f"sensitivity, {lab}: strip shear, 5 cm front corner", max(tt.tau_N, tt.tau_H), True, SF_STATIC, shear=True,
          info=True)
ye = yaw_worst(CLAMP_R5, L.R_idler_stall, r_e=3.55)
check("sensitivity, washers bearing only to r 3.55 (head/nut edge + 45° through the washer): head plate on PETG (zone"
      " mean), reverse stall", ye.pH[0], False, SF_STATIC, info=True)
check("sensitivity, washers bearing only to r 3.55: strip root, reverse stall", ye.sig_strip, True, SF_STATIC, info=True)

# spec §8 proof loads (SF_PROOF 1.0: a proof load must not damage a good part), at the slot's front end (where §8 test 1
# puts the idler bolt) and at the worst slot position
R44 = 4.5 * G_MS2
for lab, xbs in ((f"bolt at the slot's front end (x {X_FRONT:.0f})", [X_FRONT]), ("worst slot position", None)):
    yP = yaw_worst(CLAMP_R5, L.R_idler_proof, xbs=xbs)
    y44 = yaw_worst(CLAMP_R5, R44, xbs=xbs)
    t5 = tilt_worst(CLAMP_R5, F_prf, up=False, xbs=xbs)
    print(f"  proof, {lab}: 44 N pull worst at x {y44.x_strip:.0f} (strip) / {y44.pH[3]:.0f} (head plate); 49 N hang worst at"
          f" x {t5.x_N:.0f} (nut side) / {t5.x_H:.0f} (head side)")
    check(f"proof {L.R_idler_proof:.1f} N reverse stall (§8 test 2), {lab}: strip root (Kt {KT_SHARP})", yP.sig_strip, True,
          SF_PROOF, info=True)
    check(f"proof {L.R_idler_proof:.1f} N reverse stall, {lab}: head plate on PETG (zone mean)", yP.pH[0], False, SF_PROOF,
          info=True)
    check(f"proof {R44:.0f} N rearward pull (§8 test 1), {lab}: strip root (Kt {KT_SHARP})", y44.sig_strip, True, SF_PROOF,
          info=True)
    check(f"proof {R44:.0f} N rearward pull, {lab}: strip shear", y44.tau_strip, True, SF_PROOF, shear=True, info=True)
    check(f"proof {R44:.0f} N rearward pull, {lab}: head plate on PETG (zone mean)", y44.pH[0], False, SF_PROOF, info=True)
    check(f"proof {R44:.0f} N rearward pull, {lab}: nut plate on PETG (zone mean)", y44.pN[0], False, SF_PROOF, info=True)
    check(f"proof {F_prf:.0f} N hung from the idler (§8 test 1, pulls down), {lab}: bottom strip root under the nut plate"
          f" (the lip's corner, Kt {KT_SHARP})", t5.sig_N, True, SF_PROOF, info=True)
    check(f"proof {F_prf:.0f} N hang, {lab}: top strip root under the head plate (Kt {KT_SHARP})", t5.sig_H, True, SF_PROOF,
          info=True)
    check(f"proof {F_prf:.0f} N hang, {lab}: strip shear", max(t5.tau_N, t5.tau_H), True, SF_PROOF, shear=True, info=True)
y44w = yaw_worst(CLAMP_R5, R44)
stop_rows(f"proof {R44:.0f} N rearward pull (§8 test 1), rear stop, min(R, mu (T + P)) {stop_demand(R44, y44w.T):.1f} N",
          stop_demand(R44, y44w.T), SF_PROOF, info=True)
check(f"proof {F_prf:.0f} N hang: the nut plate's bottom edge on its lip (bound: all of it, {LIP_BEAR:.1f} mm²)",
      F_prf / LIP_BEAR, False, SF_PROOF, info=True)
check(f"proof {F_prf:.0f} N hang: lip root bending (bound: all of it, Kt {KT_SHARP})",
      bend_rect(F_prf * STOP_ARM, P_LEN, LIP_ROOT_H), False, SF_PROOF, Kt=KT_SHARP, info=True)
check(f"proof {F_prf:.0f} N hang: the bolt on the PETG slot floor (Ø3 x {WEB_T:.0f})", F_prf / (3.0 * WEB_T), False, SF_PROOF,
      info=True)
check_metal(f"proof 5 kg on the idler bolt: M3 class 12.9 at the outer face", bend_round(F_prf * arm_bolt, D3_M3),
            SY_129_MPA, SF_PROOF, info=True)
# end stops: what the friction demand would be with dry plates, and with the plate's end bearing only on the stop's tip
P_dry = T_SNUG_NMM / (K_DRY * 3.0)
stop_rows(f"if the plates are dry (mu {MU_DRY}): rear stop, reverse stall, min(R, mu (T + P)) "
          f"{min(L.R_idler_stall, MU_DRY * (yR.T + P_dry)):.1f} N", min(L.R_idler_stall, MU_DRY * (yR.T + P_dry)), SF_STATIC,
          info=True)
check(f"end stop root bending with the plate bearing on the stop's outer edge only (arm {p.LIP_OUT}), reverse stall"
      f" {stop_demand(L.R_idler_stall, yR.T):.1f} N (Kt {KT_SHARP})",
      bend_rect(stop_demand(L.R_idler_stall, yR.T) * p.LIP_OUT, STOP_H, p.STOP_W), False, SF_STATIC, Kt=KT_SHARP, info=True)
check(f"end stop root bending if the merged lip under it is counted (section {p.STOP_W} x {STOP_H + LIP_ROOT_H - p.LIP_FACE / 2:.1f}),"
      f" reverse stall (Kt {KT_SHARP})", bend_rect(stop_demand(L.R_idler_stall, yR.T) * STOP_ARM,
                                                   STOP_H + LIP_ROOT_H - p.LIP_FACE / 2, p.STOP_W), False, SF_STATIC,
      Kt=KT_SHARP, info=True)
stop_rows(f"if the snug has crept away (P 0, prying T up to {yR.T:.0f} N only): rear stop, reverse stall"
          f" {min(L.R_idler_stall, MU_OIL * yR.T):.1f} N", min(L.R_idler_stall, MU_OIL * yR.T), SF_STATIC, info=True)
# assembly: BUILD_GUIDE step 3 holds the nut and turns the head, so the nut-side washer doesn't turn on the nut plate. If the
# nut were turned instead, its washer would try to turn the plate (mu P r_m) and the lip would react it at the plate's end
# nearer the bolt (lever >= 7.8 mm at the slot's rear end), on the plate's corner (taken over 2 mm of lip, root over 4 mm)
r_m = 2 / 3 * (WASHER_R ** 3 - R_HOLE_W ** 3) / (WASHER_R ** 2 - R_HOLE_W ** 2)
lev_lip = XB[0] - N0
for lab, mu, Pq in (("oiled", MU_OIL, P_snug), ("dry", MU_DRY, T_SNUG_NMM / (K_DRY * 3.0))):
    F_c = mu * Pq * r_m / lev_lip
    check(f"assembly, if the nut is turned instead of the head ({lab}, mu {mu}, P {Pq:.0f} N): plate corner on the lip"
          f" ({F_c:.1f} N on 2 x {p.LIP_OUT})", F_c / (2.0 * min(p.LIP_OUT, TP_MIN)), False, SF_STATIC, info=True)
    check(f"assembly, if the nut is turned instead of the head ({lab}): lip root bending over 4 mm (Kt {KT_SHARP})",
          bend_rect(F_c * STOP_ARM, 4.0, LIP_ROOT_H), False, SF_STATIC, Kt=KT_SHARP, info=True)
# the smallest fix for the end stops: STOP_W 1.5 -> 2.0 (inner faces unchanged at x 108 / 129: stops x 106.0-108, 129-131)
for tag, R, T, sf in stop_cases:
    Fx = stop_demand(R, T)
    check(f"FIX STOP_W 2.0: end stop root bending (Kt {KT_SHARP}), {tag} ({Fx:.1f} N)", bend_rect(Fx * STOP_ARM, STOP_H, 2.0),
          False, sf, Kt=KT_SHARP, info=True)
check(f"FIX STOP_W 2.0: end stop root bending, the plate on the stop's outer edge only (arm {p.LIP_OUT}), reverse stall",
      bend_rect(stop_demand(L.R_idler_stall, yR.T) * p.LIP_OUT, STOP_H, 2.0), False, SF_STATIC, Kt=KT_SHARP, info=True)
check(f"FIX+ STOP_W 2.5 (more margin): end stop root bending, the plate on the stop's outer edge only (arm {p.LIP_OUT}),"
      f" reverse stall", bend_rect(stop_demand(L.R_idler_stall, yR.T) * p.LIP_OUT, STOP_H, 2.5), False, SF_STATIC,
      Kt=KT_SHARP, info=True)
check(f"FIX STOP_W 2.0: end stop root bending, proof {R44:.0f} N pull", bend_rect(stop_demand(R44, y44w.T) * STOP_ARM, STOP_H,
      2.0), False, SF_PROOF, Kt=KT_SHARP, info=True)
f_fs = 129.0 + 2.0
y_fillet = F.HALF_W_OUT - p.CORNER_R + math.sqrt(p.CORNER_R ** 2 - (f_fs - (F.X_FRONT_OUT - p.CORNER_R)) ** 2)
print(f"FIX STOP_W 2.0 fit: the front stop then ends at x {f_fs:.1f}, where the r{p.CORNER_R:.0f} corner fillet's face is at"
      f" |y| {y_fillet:.2f}: the stop (from |y| {F.HALF_W_OUT - 1.0:.0f}) still joins it; the rear stop ends at x"
      f" {p.NUT_PLATE_X[0] - 2.0:.1f}, on the flat outer face")
# option offered in round 4 and not taken: 1 x 45° chamfer on the recess floor's edge (Kt 1.6 there)
tC = tilt_worst(dict(CLAMP_R5, kt_in_bot=1.6), L.drop, up=True)
check("option (not required): 1 x 45° chamfer on the recess floor's edge (Kt 1.6): bottom strip root, 5 cm front corner",
      tC.sig_H, True, SF_STATIC, info=True)
# round 4's FIX model recomputed with this script's functions (must give round 4's predictions back)
fR4 = yaw_worst(CLAMP_R4FIX, L.R_idler_stall)
fD4 = tilt_worst(CLAMP_R4FIX, L.drop, up=True)
check("round 4 FIX model, recomputed: head plate on PETG (zone mean), reverse stall (round 4: 6.45)", fR4.pH[0], False,
      SF_STATIC, info=True)
check("round 4 FIX model, recomputed: bottom strip under the head plate, 5 cm front corner (round 4: 3.02)", fD4.sig_H, True,
      SF_STATIC, info=True)
check("round 4 FIX model, recomputed: strip shear, 5 cm front corner (round 4: 3.05)", max(fD4.tau_N, fD4.tau_H), True,
      SF_STATIC, shear=True, info=True)
check("round 4 FIX model, recomputed: top strip under the nut plate, 5 cm front corner (round 4: 3.42)", fD4.sig_N, True,
      SF_STATIC, info=True)

# S1: snug torque against the jack-screw thread (capacity at the allowable: F_JACK_CAP)
for T_nm in (0.02, 0.04, 0.05, 0.1, 0.3):
    for lab, Kk, mu in (("oiled", K_OIL, MU_OIL), ("dry", K_DRY, MU_DRY)):
        P_s = T_nm * 1000 / (Kk * 3.0)
        F_s = 2 * mu * P_s + L.R_sus
        check_custom(f"S1 tensioning: snug {T_nm:.2f} N*m, {lab} plates (K {Kk}, mu {mu}): P {P_s:.0f} N, jack thrust {F_s:.0f} N"
                     f" vs thread capacity {F_JACK_CAP:.0f} N", F_s, F_JACK_CAP, "jack N", SF_STATIC, info=True)
# N20 shaft fatigue: rotating bending under the track tension while driving (unknown steel: sigma_y 350 -> UTS >= 450,
# Se' 0.5 UTS, ground surface 0.94, size 1.0, 90 % reliability 0.897 -> Se 190 MPa; Kf 1.5 at the D-flat run-out)
Se_shaft = 0.5 * 450.0 * 0.94 * 1.0 * 0.897
for lab, R in ((f"everyday pull {L.R_cyc:.1f} N", L.R_cyc), (f"pretension {L.R_sus:.0f} N", L.R_sus)):
    check_custom(f"N20 shaft fatigue, rotating bending at {lab}, arm {F.SHAFT_ARM:.0f}, Kf 1.5 (endurance limit estimated for"
                 f" an unknown steel)", 1.5 * R * F.SHAFT_ARM / Zmin, Se_shaft, f"steel Se {Se_shaft:.0f}", SF_METAL, info=True)
check("C1 BOUND skin carries all (rigid diaphragm), 5 cm rear corner", skin_tau(Ft_drop, 1.0), True, SF_STATIC, shear=True,
      info=True)
check("C2 BOUND walls carry all (no skin), 5 cm rear corner", wall_sigma(Ft_drop, 1.0), False, SF_STATIC, info=True)
check(f"C2 at the spec's horizontal lever {lev_h:.2f} R applied to the drop, 5 cm rear corner", wall_sigma(lev_h * L.drop), False,
      SF_STATIC, info=True)
mu_drop = 0.3
s_in_d, _ = skin_out_of_plane(mu_drop * L.drop, True)
check(f"C9 skin, sideways friction in a corner drop (mu {mu_drop} x {L.drop:.1f} N) on the thrust washer", s_in_d, True,
      SF_STATIC, info=True)
F_s08 = S08_6V_NMM[-1][1] / F.RP
check(f"S-08 ungated 196 N*mm motor: skin shear, track stall ({lev_h:.2f} x {T0_N * 2 + F_s08:.1f} N)",
      skin_tau(lev_h * (2 * T0_N + F_s08)), True, SF_STATIC, shear=True, info=True)
print(f"round-5 clamp: T {yR.T_min:.0f}-{yR.T:.0f} N at the reverse stall (bolt yaw <= {yR.theta * 1000:.2f} mrad); drop T"
      f" {tD.T:.0f} N, strips {tD.qN:.2f} / {tD.qH:.2f} N/mm; plates {yR.sig_H:.0f} / {yR.sig_N:.0f} MPa; strip arms"
      f" {a_top5:.3f} / {a_bot5:.3f}")
print(f"inserts: Ø{p.INSERT_D} holes have no HOLE_COMP and print about Ø{p.INSERT_D - HC:.1f} (round 3 note, unchanged)")

report(f"{JOB} strength checks")

"""Strength check for jobs/20261026-rover-chassis (tracked rover, PETG), round 4.

Run from the project root with the CAD venv active (build123d, trimesh, scipy):
    source /home/claude/.venv-cad/bin/activate
    python3 jobs/20261026-rover-chassis/strength_calc.py

Round 4 = the round-4 geometry (model.py, rover_frame.py) with the round-3 method and loads. Round 4 made strength round 3's
changes 1 and 2 only:
- SKIN 1.0 -> 2.0: gearbox face |y| 44, shaft arm 11.0 (the nacelle, hub and track plane did not move);
- idler clamp: a steel head plate 20.6 x 10 x 2 let flush into a 2 mm recess in each idler-block face (x 108-129), and a
  steel nut plate 14 x 8 x 2 on the bottom of an idler nut slot opened to 9 x 15 x 4.6 deep. Between the recess (|y| 28-30)
  and the slot (|y| 33.4-38) only a 3.4 mm PETG web is left, and the bolt slot cuts it into two strips.

New in this round:
- The idler clamp is solved as a contact problem along X: head plate and nut plate as steel Hetenyi beams on elastic
  foundations, the 3.4 mm web between them as through-thickness springs grounded by the out-of-plane stiffness of its
  strips and end pieces, and the rigid bolt body (head + washer, nut) joined by the bolt's axial spring. Compression-only
  contacts, active-set iteration. No friction and no clamp preload are credited (DFM round 4, note S2): the bolt tension
  that resists the yaw moment is the prying force the moment itself creates.
- The 5 cm front-corner drop and the spec section 8 5 kg hang tilt the idler bolt about X: the same couple pushes one plate
  strip into one web strip (beam on elastic foundation).
- The step-3 snug against the self-tapped jack-screw thread (DFM round 4, note S1), the section 8 proof loads, and the FIX.
The script builds the chassis with build123d (section properties, probes) and recomputes the rover mass from every rover
part.stl at its print_requirements minima. Rows tagged as drop rows scale linearly with the drop height; report() prints
the height at which the first of them reaches its required SF.
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
from scipy import ndimage  # noqa: E402

ns = runpy.run_path(os.path.join(JOBS, JOB, "model.py"), run_name="model")
WORLD = ns["design"]()                       # round-4 chassis in the rover world frame
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
BOM = [  # round-4 BUILD_GUIDE §1, grams (bought-part masses: hobby_parts where given, else typical catalogue values)
    ("2 x N20 gear motor", 2 * M.mass_g), ("2 x Pololu #1996 hub", 2 * F.HUB.mass_g), ("8 x M3x12 screw", 8 * 0.9),
    ("4 x M3x50 + 2 x M3x40 fully threaded", 4 * 2.5 + 2 * 2.1), ("2 x M3x20 set screw", 2 * 0.85),
    ("6 nuts, 6 nylocs, 26 washers, 2 DIN 9021", 6 * 0.25 + 6 * 0.3 + 26 * 0.12 + 2 * 0.35),
    ("2 head + 2 nut steel plates (round 4)", 2 * (m_head_plate + m_nut_plate)),
    ("4 heat-set inserts + 4 x M3x8", 4 * 0.4 + 4 * 0.65), (f"{2 * F.N_LINKS} steel pins Ø2 x 24", 2 * F.N_LINKS * m_pin),
    ("battery: 2 protected 18650 + holder", HP.BATT_2X18650_LONG.mass_g), ("ESP32 DevKit", 10.0),
    ("mini breadboard + TB6612 + MP1584", HP.MINI_BREADBOARD.mass_g + 3.0 + 2.5), ("HC-SR04", HP.HCSR04.mass_g),
    ("MTS-102 toggle + nuts", 6.0), ("wires, jumpers, capacitors, resistors, diode", 20.0),
    ("velcro strap, zip ties, foam tape, glue", 8.0)]
m_printed = sum(v[0] for v in pm.values())
m_solid = sum(v[1] for v in pm.values())
m_bought = sum(g for _, g in BOM)
m_est = m_printed + m_bought
print("\nmass check (round 4): printed at the print_requirements minima: "
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

# ---- B. idler mount: 30 x 24 block (face |y| 28), ±4 slot with hull, jack screw at the head, round-4 steel plates --------
xi1 = F.X_FRONT_OUT - t_w
bl = min(F.AXLE_DX + p.IDLER_BLOCK[0] / 2, xi1) - (F.AXLE_DX - p.IDLER_BLOCK[0] / 2)     # 25.5 (runs into the front wall)
a_idler = math.sqrt(bl * p.IDLER_BLOCK[1] / math.pi)
check(f"B1 idler block: wall bending, 5 cm front corner {L.drop:.1f} N (Kt {KT_CHAMFER} top strip)",
      plate_boss_moment_stress(L.drop * arm_w, a_idler, t_w, KT_CHAMFER), True, SF_STATIC, drop=True)
check(f"B2 idler block: wall bending, reverse stall {L.R_idler_stall:.1f} N (Kt {KT_SHARP}: sharp rear corner)",
      plate_boss_moment_stress(L.R_idler_stall * arm_w, a_idler, t_w, KT_SHARP), False, SF_STATIC)
check(f"B3 idler block: wall bending, pretension {L.R_sus:.0f} N sustained (Kt {KT_SHARP})",
      plate_boss_moment_stress(L.R_sus * arm_w, a_idler, t_w, KT_SHARP), False, SF_CYCLIC)

# --- the round-4 clamp, as built (model.py / rover_frame.py), and probes of the solid ---------------------------------
r_s = (p.BOLT_D + HC) / 2                                  # 1.8: CAD radius of the idler slot
Z_LO, Z_HI = -r_s, r_s * math.sqrt(2)                      # PETG bolt-slot band about Z_A: hull to the teardrop tips
BS = (F.AXLE_DX - F.IDLER_SLOT - r_s, F.AXLE_DX + F.IDLER_SLOT + r_s)   # 114.2-125.8: PETG bolt slot along X
BAND = F.PLATE_SLOT[0] / 2                                 # 1.7: plate slots |z| < 1.7
H_LEN, H_H = F.IDLER_PLATE                                 # head plate 20.6 x 10
H0 = 0.5 * (p.PLATE_RECESS_X[0] + p.PLATE_RECESS_X[1]) - H_LEN / 2   # 108.2 (assembly_check head_plate_x)
HS = (H0 + 6.0, H0 + 6.0 + F.PLATE_SLOT[1])                # its slot from 6 to 18 mm along (BUILD_GUIDE §1): 114.2-126.2
N_LEN, N_H = F.NUT_PLATE                                   # nut plate 14 x 8, slot in the middle
N0 = F.AXLE_DX - N_LEN / 2
NS = (F.AXLE_DX - F.PLATE_SLOT[1] / 2, F.AXLE_DX + F.PLATE_SLOT[1] / 2)
W_X = (F.AXLE_DX - p.NUT_SLOT_L / 2, F.AXLE_DX + p.NUT_SLOT_L / 2)    # nut slot = the web's footprint: 112.5-127.5
y_rec = y_boss + p.PLATE_RECESS_D                          # 30: recess bottom = head plate's bearing face
y_slot = F.HALF_W_OUT - p.NUT_SLOT_D                       # 33.4: nut-slot bottom = nut plate's bearing face
WEB_T = y_slot - y_rec                                     # 3.4
ZA = F.Z_A
probe = {"web solid at (120, 31.7, Z_A+3.5)": solid_at(120.0, 31.7, ZA + 3.5),
         "recess void at (120, 29.9, Z_A+3.5)": not solid_at(120.0, 29.9, ZA + 3.5),
         "web solid at (120, 30.1, Z_A+3.5)": solid_at(120.0, 30.1, ZA + 3.5),
         "web solid at (120, 33.3, Z_A+3.5)": solid_at(120.0, 33.3, ZA + 3.5),
         "nut slot void at (120, 33.5, Z_A+3.5)": not solid_at(120.0, 33.5, ZA + 3.5),
         "nut slot void at (120, 34.4, Z_A+4.4)": not solid_at(120.0, 34.4, ZA + 4.4),
         "roof solid at (120, 34.4, Z_A+4.6)": solid_at(120.0, 34.4, ZA + 4.6),
         "bolt slot void at (120, 31.7, Z_A+2.4)": not solid_at(120.0, 31.7, ZA + 2.4),
         "web end piece solid at (113.5, 31.7, Z_A)": solid_at(113.5, 31.7, ZA),
         "solid behind the head plate at (110, 36, Z_A)": solid_at(110.0, 36.0, ZA)}
assert all(probe.values()), f"idler clamp geometry differs from the round-4 model: {probe}"
print(f"idler clamp (probed on the solid): head plate {H_LEN} x {H_H} x {F.PLATE_T} at x {H0:.1f}-{H0 + H_LEN:.1f} (slot"
      f" {HS[0]:.1f}-{HS[1]:.1f}) on the recess bottom |y| {y_rec}; nut plate {N_LEN} x {N_H} x {F.PLATE_T} at x {N0:.1f}-"
      f"{N0 + N_LEN:.1f} on the nut-slot bottom |y| {y_slot}; web |y| {y_rec}-{y_slot} = {WEB_T:.1f} mm over x {W_X[0]}-{W_X[1]},"
      f" z ±{p.NUT_SLOT_H / 2}; PETG bolt slot x {BS[0]:.1f}-{BS[1]:.1f}, z {Z_LO:+.2f}..{Z_HI:+.2f}: strips"
      f" {p.NUT_SLOT_H / 2 - Z_HI:.2f} (top) and {p.NUT_SLOT_H / 2 + Z_LO:.2f} (bottom) tall, roots at sharp corners")

# --- clamp model ----------------------------------------------------------------------------------------------------
E_ST = E_STEEL_MPA
SY_PLATE_MPA = 200.0     # hand-cut 14 ga (1.9) / 2 mm mild steel sheet or flat bar: conservative yield (A36 250, CR 1008 ~200)
KS_PETG = 200.0          # N/mm^3: PETG foundation under a 10 mm wide plate on thick solid (E/(B(1-nu^2)), Vesic ~165)
ROOT_SOFT = 1.3          # web-strip root rotation adds ~30 % to the Timoshenko cantilever compliance
K_END = 11000.0          # N/mm per mm: web end pieces (1.7 x 9 x 3.4, attached on 3 sides) as cantilevers from the slot end
WASHER_R = F.WASHER_WIDE[0] / 2                    # 4.5: Ø9 x 0.8 DIN 9021 tilting with the head (3.55 as a bound)
KB_BOLT = 70000.0        # N/mm: M3 between head and nut (8.2 mm grip, stress area 5.03 mm²) with head and nut compliance
KP = 2.0e5               # N/mm^3 contact penalty (steel on steel, plate on web faces)


def strip_k(a, t):
    """Out-of-plane stiffness per unit length (N/mm per mm) of a web strip cantilevered from its root, load at arm a
    (Timoshenko beam: bending + shear, kappa 5/6)."""
    EI = E_PETG_MPA * t ** 3 / 12.0
    kGA = 5.0 / 6.0 * G_PETG_MPA * t
    return 1.0 / (a ** 3 / (3 * EI) + a / kGA)


def _segs(hz, slot, band, x):
    """z-segments of a plate (half height hz) at x, minus its slot band where its slot is."""
    return [(-hz, -band), (band, hz)] if slot[0] <= x <= slot[1] else [(-hz, hz)]


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


def _w(segs, lo=-1e9, hi=1e9):
    return sum(max(0.0, min(b, hi) - max(a, lo)) for a, b in segs)


def _hermite(EI, Lh):
    return EI / Lh ** 3 * np.array([[12, 6 * Lh, -12, 6 * Lh], [6 * Lh, 4 * Lh * Lh, -6 * Lh, 2 * Lh * Lh],
                                    [-12, -6 * Lh, 12, -6 * Lh], [6 * Lh, 2 * Lh * Lh, -6 * Lh, 4 * Lh * Lh]])


def nut_half_height(dx):
    """M3 nut (5.5 AF) with its flats on top and bottom (corners along X: the smaller lever, conservative)."""
    rc = F.NUT[0] / math.sqrt(3)
    return 0.0 if abs(dx) >= rc else min(F.NUT[0] / 2, (rc - abs(dx)) * math.sqrt(3))


def nut_side_half_height(g, dx):
    """Half height (z) of what bears on the nut plate at dx from the bolt: the nut, or a washer under it (g['nut_washer'])."""
    rw = g.get("nut_washer")
    if rw:
        return math.sqrt(max(0.0, rw ** 2 - dx * dx))
    return nut_half_height(dx)


def arms(g):
    zs = g["zs"]
    a_top_N = zs - (Z_HI + min(g["Nh"] / 2, zs)) / 2
    a_bot_N = zs - (-Z_LO + min(g["Nh"] / 2, zs)) / 2
    a_top_H = zs - (Z_HI + min(g["Hh"] / 2, zs)) / 2
    a_bot_H = zs - (-Z_LO + min(g["Hh"] / 2, zs)) / 2
    return a_top_N, a_bot_N, a_top_H, a_bot_H


def clamp_yaw(g, xb, Mz, P0=0.0, r_e=WASHER_R, ks=KS_PETG, root_soft=ROOT_SOFT, k_end=None, h=0.1):
    """Idler clamp under the yaw moment Mz (about Z) on the bolt body, bolt at slot position xb. Everything along X:
    head plate and nut plate (steel Hermite beams), the web as two face nodes and a mid node per station (through-
    thickness springs, out-of-plane ground spring), the head plate also on solid PETG where there is no web behind it,
    rigid bolt body (v_h, v_n, theta) touching the plates through the washer and the nut, bolt axial spring with an
    initial stretch for the preload P0. Compression-only contacts, active-set iteration."""
    k_end = g["k_end"] if k_end is None else k_end
    zs, wt, tp = g["zs"], g["web_t"], F.PLATE_T
    (Ha, Hb), (Na, Nb), (Wa, Wb) = g["H"], g["N"], g["W"]
    xs = np.round(np.arange(Ha, Hb + 1e-9, h), 6)
    n = len(xs)
    inN = (xs >= Na - 1e-9) & (xs <= Nb + 1e-9)
    inW = (xs >= Wa - 1e-9) & (xs <= Wb + 1e-9)
    iN, iW = np.nonzero(inN)[0], np.nonzero(inW)[0]
    a_top_N, a_bot_N, a_top_H, a_bot_H = arms(g)
    k_top = strip_k(max(a_top_N, 0.05), wt) / root_soft
    k_bot = strip_k(max(a_bot_N, 0.05), wt) / root_soft
    wHw, wHs, wN, wwa, wnu, bweb = (np.zeros(n) for _ in range(6))
    for k, x in enumerate(xs):
        sH = _segs(g["Hh"] / 2, g["Hs"], BAND, x)
        if BS[0] <= x <= BS[1]:
            sH = _cut(sH, Z_LO, Z_HI)
        if inW[k]:
            wHw[k] = _w(sH, -zs, zs)
            wHs[k] = (_w(sH) - wHw[k]) if g["H_solid"] else 0.0
        else:
            wHs[k] = _w(sH) if g["H_solid"] else 0.0
        if inN[k] and inW[k]:
            sN = _segs(g["Nh"] / 2, g["Ns"], BAND, x)
            if BS[0] <= x <= BS[1]:
                sN = _cut(sN, Z_LO, Z_HI)
            wN[k] = _w(sN, -zs, zs)
        d = x - xb
        if abs(d) < r_e:
            c = math.sqrt(r_e ** 2 - d * d)
            wwa[k] = 2 * max(0.0, c - BAND) if g["Hs"][0] <= x <= g["Hs"][1] else 2 * (c - math.sqrt(max(0.0, 1.6 ** 2 - d * d)))
        if inN[k]:
            hz = nut_side_half_height(g, d)
            if hz > 0:
                wnu[k] = 2 * max(0.0, hz - BAND) if g["Ns"][0] <= x <= g["Ns"][1] else 2 * (hz - math.sqrt(max(0.0, 1.65 ** 2 - d * d)))
        bweb[k] = (2 * zs - (Z_HI - Z_LO)) if BS[0] <= x <= BS[1] else 2 * zs
    is_strip = (xs >= BS[0]) & (xs <= BS[1])
    kg = np.where(is_strip, k_top + k_bot, k_end)
    kc_half = 2 * E_PETG_MPA * bweb / wt
    nH = 2 * n
    oN = nH
    oW = oN + 2 * len(iN)
    oB = oW + 3 * len(iW)
    ndof = oB + 3
    vh, vn, th = oB, oB + 1, oB + 2
    mapN = {k: j for j, k in enumerate(iN)}
    mapW = {k: j for j, k in enumerate(iW)}
    K0 = np.zeros((ndof, ndof))
    f = np.zeros(ndof)

    def EI_of(slot, hz):
        return lambda x: E_ST * (2 * hz - (2 * BAND if slot[0] <= x <= slot[1] else 0.0)) * tp ** 3 / 12

    EI_H, EI_N = EI_of(g["Hs"], g["Hh"] / 2), EI_of(g["Ns"], g["Nh"] / 2)
    for off, idx, EI in ((0, np.arange(n), EI_H), (oN, iN, EI_N)):
        for e in range(len(idx) - 1):
            Lh = xs[idx[e + 1]] - xs[idx[e]]
            dd = [off + 2 * e + j for j in range(4)]
            K0[np.ix_(dd, dd)] += _hermite(EI(0.5 * (xs[idx[e]] + xs[idx[e + 1]])), Lh)
    lump = np.full(n, h)
    lump[0] = lump[-1] = h / 2
    for k in iW:
        j = mapW[k]
        ui, um, uo = oW + 3 * j, oW + 3 * j + 1, oW + 3 * j + 2
        Lk = lump[k] if k not in (iW[0], iW[-1]) else h / 2
        for a, b in ((ui, um), (um, uo)):
            kk = kc_half[k] * Lk
            K0[a, a] += kk
            K0[b, b] += kk
            K0[a, b] -= kk
            K0[b, a] -= kk
        K0[um, um] += kg[k] * Lk
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
        if wHs[k] > 0:
            contacts.append(("Hs", k, ks * wHs[k] * Lk, [2 * k], [1.0]))
        if inW[k] and wHw[k] > 0:
            contacts.append(("Hw", k, KP * wHw[k] * Lk, [2 * k, oW + 3 * mapW[k]], [1.0, -1.0]))
        if inN[k] and inW[k] and wN[k] > 0:
            contacts.append(("Nw", k, KP * wN[k] * Lk, [oW + 3 * mapW[k] + 2, oN + 2 * mapN[k]], [1.0, -1.0]))
        if wwa[k] > 0:
            contacts.append(("W", k, KP * wwa[k] * Lk, [vh, th, 2 * k], [1.0, x - xb, -1.0]))
        if inN[k] and wnu[k] > 0:
            contacts.append(("Nut", k, KP * wnu[k] * Lk, [oN + 2 * mapN[k], vn, th], [1.0, -1.0, -(x - xb)]))
    active = np.ones(len(contacts), dtype=bool)
    for it in range(300):
        K = K0.copy()
        for c, (_, _, kk, dd, co) in enumerate(contacts):
            if active[c]:
                co = np.array(co)
                K[np.ix_(dd, dd)] += kk * np.outer(co, co)
        u = np.linalg.solve(K, f)
        gap = np.array([sum(cc * u[d] for d, cc in zip(dd, co)) for (_, _, _, dd, co) in contacts])
        new = gap > 0
        if np.array_equal(new, active):
            break
        active = new
    else:
        raise RuntimeError("clamp contact iteration did not converge")
    q = {t: np.zeros(n) for t in ("Hs", "Hw", "Nw", "W", "Nut")}
    for c, (t, k, kk, _, _) in enumerate(contacts):
        if active[c]:
            q[t][k] += kk * gap[c]
    r = SimpleNamespace(xs=xs, q=q, T=KB_BOLT * (D0 + u[vn] - u[vh]), theta=u[th])
    r.M_check = float(((xs - xb) * q["W"]).sum() - ((xs - xb) * q["Nut"]).sum())
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

    r.pH = zone_mean(q["Hs"] + q["Hw"], wHs + wHw)          # head plate on PETG (solid + web): zone mean, peak, x
    r.pN = zone_mean(q["Nw"], wN)                           # nut plate on the web
    # web out-of-plane: ground reaction per unit x at the mid node (negative = pushed -y by the nut plate)
    gw = np.array([kg[k] * u[oW + 3 * mapW[k] + 1] for k in iW])
    xw = xs[iW]
    st = (xw >= BS[0]) & (xw <= BS[1])
    share_top = k_top / (k_top + k_bot)
    qt, qb = gw * share_top, gw * (1 - share_top)
    t2 = wt ** 2
    dz, t_sec, kt_c = g["in_corner"]
    # N's push (-y): tension on the outer face at the strip roots (sharp corners on the round-4 nut slot)
    sig_out = np.where(gw < 0, np.maximum(6 * np.abs(qt) * a_top_N, 6 * np.abs(qb) * a_bot_N) / t2, 0.0) * g["kt_out"]
    # H's push (+y): tension on the inner face at the root (no corner there as built) and at the recess corner beyond it
    sig_in = np.where(gw > 0, np.maximum(np.maximum(6 * qt * a_top_H, 6 * qb * a_bot_H) / t2 * g["kt_in_root"],
                                         6 * qb * (a_bot_H + dz) / t_sec ** 2 * kt_c), 0.0)
    r.sig_strip = float(max(sig_out[st].max(initial=0.0), sig_in[st].max(initial=0.0)))
    r.sig_strip_out = float(sig_out[st].max(initial=0.0))
    r.tau_strip = float(1.5 * np.maximum(np.abs(qt), np.abs(qb))[st].max(initial=0.0) / wt)
    r.q_strip = float(np.abs(gw[st]).max(initial=0.0))
    # web end pieces (round 4 only): cantilevers in X from the nut-slot ends; sharp corner on the outer face
    r.sig_end, r.tau_end, r.V_end = 0.0, 0.0, 0.0
    if g.get("end_pieces"):
        for sel, x_att in (((xw < BS[0]), Wa), ((xw > BS[1]), Wb)):
            V = float(gw[sel].sum() * h)
            Mep = float((gw[sel] * np.abs(xw[sel] - x_att)).sum() * h)
            kt = g["kt_out"] if V < 0 else 1.0
            r.sig_end = max(r.sig_end, kt * 6 * abs(Mep) / (2 * zs * t2))
            r.tau_end = max(r.tau_end, 1.5 * abs(V) / (2 * zs * wt))
            r.V_end = max(r.V_end, abs(V))
    # plate bending (Hermite curvature at element ends)

    def plate_sigma(off, idx, EI, hz, slot):
        best = 0.0
        for e in range(len(idx) - 1):
            x0, x1 = xs[idx[e]], xs[idx[e + 1]]
            Lh = x1 - x0
            we = u[off + 2 * e: off + 2 * e + 4]
            xm = 0.5 * (x0 + x1)
            Z = (2 * hz - (2 * BAND if slot[0] <= xm <= slot[1] else 0.0)) * tp ** 2 / 6
            for xi in (0.0, 1.0):
                d2 = np.array([(-6 + 12 * xi) / Lh ** 2, (-4 + 6 * xi) / Lh, (6 - 12 * xi) / Lh ** 2, (-2 + 6 * xi) / Lh])
                best = max(best, abs(EI(xm) * (d2 @ we)) / Z)
        return best

    r.sig_H = plate_sigma(0, np.arange(n), EI_H, g["Hh"] / 2, g["Hs"])
    r.sig_N = plate_sigma(oN, iN, EI_N, g["Nh"] / 2, g["Ns"])
    a_nut = float((wnu * lump).sum())
    r.p_nut = r.T / a_nut if a_nut > 0 else 0.0              # mean steel bearing of the nut on the nut plate
    a_wa = float((wwa * lump).sum())
    r.p_washer = r.T / a_wa if a_wa > 0 else 0.0
    return r


def bef_line(xs, EI, k, p):
    """Beam on a Winkler foundation k(x) (N/mm per mm) under a line load p(x) (N/mm), free ends; returns w(x)."""
    n = len(xs)
    K = np.zeros((2 * n, 2 * n))
    f = np.zeros(2 * n)
    for e in range(n - 1):
        Lh = xs[e + 1] - xs[e]
        dd = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        K[np.ix_(dd, dd)] += _hermite(EI[e], Lh)
        km, pm = 0.5 * (k[e] + k[e + 1]) * Lh, 0.5 * (p[e] + p[e + 1]) * Lh
        for i in (2 * e, 2 * e + 2):
            K[i, i] += km / 2
            f[i] += pm / 2
    return np.linalg.solve(K + np.eye(2 * n) * 1e-9, f)[0::2]


def contact_centroid_z(half_height, reach):
    """z-centroid (from the bolt axis) of a contact beyond the 1.7 plate-slot band, profile half_height(dx) for |dx| < reach,
    uniform pressure. Washer + nut centroids are the lever of the bolt body's tilt couple about X; uniform pressure gives a
    smaller lever than the edge-loaded contact of a tilting part, so the prying force T comes out high (conservative)."""
    hh = 0.01
    A = Az = 0.0
    for i in range(int(2 * reach / hh)):
        x = -reach + (i + 0.5) * hh
        hz = half_height(x)
        if hz > BAND:
            A += (hz - BAND) * hh
            Az += (hz ** 2 - BAND ** 2) / 2 * hh
    return Az / A


ZH_TILT = contact_centroid_z(lambda dx: math.sqrt(max(0.0, WASHER_R ** 2 - dx * dx)), WASHER_R)   # Ø9 washer on the head plate
ZN_TILT = contact_centroid_z(nut_half_height, F.NUT[0] / math.sqrt(3))                          # nut on the nut plate


def zn_tilt(g):
    rw = g.get("nut_washer")
    return contact_centroid_z(lambda dx: math.sqrt(max(0.0, rw ** 2 - dx * dx)), rw) if rw else ZN_TILT


def clamp_tilt(g, xb, Fz, up=True, y_c=None, ks=KS_PETG, root_soft=ROOT_SOFT, k_end=None, h=0.05):
    """Vertical load Fz at the track plane tilts the bolt about X. With no friction and no preload, the tilt couple is the
    prying couple T (z_h + z_n) = Fz (Y_T - y_c); y_c = the head plate's bearing face (the innermost place the shear can
    react, so the largest moment). Upward load (drop on the front corner): the nut's top edge pushes the nut plate's top
    strip into the web's top strip, the head's bottom edge pushes the head plate's bottom strip into the web's bottom
    strip. Each plate strip is a beam on the web strip (and the stiffer end regions / solid PETG)."""
    k_end = g["k_end"] if k_end is None else k_end
    y_c = g["y_face_H"] if y_c is None else y_c
    zs, wt, tp = g["zs"], g["web_t"], F.PLATE_T
    T = Fz * (F.Y_T - y_c) / (ZH_TILT + zn_tilt(g))
    a_top_N, a_bot_N, a_top_H, a_bot_H = arms(g)
    out = SimpleNamespace(T=T)
    # nut side
    Na, Nb = g["N"]
    xs = np.round(np.arange(Na, Nb + 1e-9, h), 6)
    hzN = g["Nh"] / 2
    EI = np.array([E_ST * ((hzN - BAND) if g["Ns"][0] <= 0.5 * (a + b) <= g["Ns"][1] else hzN) * tp ** 3 / 12
                   for a, b in zip(xs[:-1], xs[1:])])
    aN = a_top_N if up else a_bot_N
    k = np.where((xs >= BS[0]) & (xs <= BS[1]), strip_k(max(aN, 0.05), wt) / root_soft, k_end / 2)
    pz = np.array([max(0.0, nut_side_half_height(g, x - xb) - BAND) for x in xs])
    pz = pz / (pz.sum() * h) * T
    w = bef_line(xs, EI, k, pz)
    qn = k * w
    st = (xs >= BS[0]) & (xs <= BS[1])
    out.qN = float(qn[st].max())
    out.sig_N_side = 6 * out.qN * aN / wt ** 2 * g["kt_out"]
    out.tau_N_side = 1.5 * out.qN / wt
    # head side: the head plate's strip on the opposite web strip (inner face in tension) and on solid PETG
    Ha, Hb = g["H"]
    xs = np.round(np.arange(Ha, Hb + 1e-9, h), 6)
    hzH = g["Hh"] / 2
    EI = np.array([E_ST * ((hzH - BAND) if g["Hs"][0] <= 0.5 * (a + b) <= g["Hs"][1] else hzH) * tp ** 3 / 12
                   for a, b in zip(xs[:-1], xs[1:])])
    aH = a_bot_H if up else a_top_H
    inW = (xs >= g["W"][0]) & (xs <= g["W"][1])
    st = (xs >= BS[0]) & (xs <= BS[1])
    k_web = np.where(st, strip_k(max(aH, 0.05), wt) / root_soft, np.where(inW, k_end / 2, 0.0))
    k_sol = np.where(inW, ks * max(0.0, hzH - zs), ks * hzH) if g["H_solid"] else np.zeros(len(xs))
    pz = np.array([max(0.0, math.sqrt(max(0.0, WASHER_R ** 2 - (x - xb) ** 2)) - BAND) for x in xs])
    pz = pz / (pz.sum() * h) * T
    w = bef_line(xs, EI, k_web + k_sol, pz)
    qh = k_web * w
    out.qH = float(qh[st].max())
    dz, t_sec, kt_c = g["in_corner"]
    out.sig_H_side = max(6 * out.qH * aH / wt ** 2 * g["kt_in_root"], 6 * out.qH * (aH + dz) / t_sec ** 2 * kt_c)
    out.tau_H_side = 1.5 * out.qH / wt
    out.p_H_solid = float((k_sol * w).max() / max(hzH - (zs if g["H_solid"] else 0.0), 1e-9)) if g["H_solid"] else 0.0
    return out


CLAMP_R4 = dict(name="round 4 as built", H=(H0, H0 + H_LEN), Hs=HS, Hh=H_H, N=(N0, N0 + N_LEN), Ns=NS, Nh=N_H, W=W_X,
                zs=p.NUT_SLOT_H / 2, web_t=WEB_T, k_end=K_END, H_solid=True, end_pieces=True, kt_out=KT_SHARP,
                kt_in_root=1.0, in_corner=(p.PLATE_RECESS_Z - p.NUT_SLOT_H / 2, 8.0, KT_SHARP), y_face_H=y_rec)
# FIX: the nut plate leaves the wall. It becomes a second 20.6 x 10 x 2 plate (the head plate's twin) on the wall's flat
# OUTER face at x 108.2-128.8, Z_A ± 5, held by a printed lip under its bottom edge (no recess, so nothing thins the PETG
# behind it); a Ø9 x 0.8 DIN 9021 washer goes under the wall nut, as under the head; the 9 x 15 x 4.6 idler nut slot is
# deleted (the bolt slot stays). PETG between the plates: |y| 30-38 = 8.0 mm, no slot behind either plate. The idler's hub
# then starts at |y| 38 + 2 + 0.8 + 2.4 + 0.5 = 43.7 instead of 38.5 (5.2 mm shorter; idler job). Kt 2.5 is kept at both
# faces' roots (the head-plate recess floor edge inside, the lip's corner outside).
CLAMP_FIX = dict(name="FIX nut plate on the outer face", H=(H0, H0 + H_LEN), Hs=HS, Hh=H_H, N=(H0, H0 + H_LEN), Ns=HS,
                 Nh=H_H, W=(H0, H0 + H_LEN), zs=p.PLATE_RECESS_Z, web_t=F.HALF_W_OUT - y_rec, k_end=30000.0,
                 H_solid=False, end_pieces=False, kt_out=KT_SHARP, kt_in_root=KT_SHARP,
                 in_corner=(0.0, F.HALF_W_OUT - y_rec, KT_SHARP), y_face_H=y_rec, nut_washer=WASHER_R)
# the same move without the washer under the nut, and with a 0.5 mm locating recess instead of the lip (not enough)
CLAMP_FIX_NOWASHER = dict(CLAMP_FIX, nut_washer=None)
CLAMP_FIX_RECESS = dict(CLAMP_FIX, web_t=F.HALF_W_OUT - 0.5 - y_rec, in_corner=(0.0, F.HALF_W_OUT - 0.5 - y_rec, KT_SHARP))
IDLER_HUB_SHORTER = F.PLATE_T + F.WASHER_WIDE[1] + F.NUT[1]       # 5.2 mm: the stack that moves outside the wall
XB = [F.AXLE_DX + d for d in (-F.IDLER_SLOT, -F.IDLER_SLOT / 2, 0.0, F.IDLER_SLOT / 2, F.IDLER_SLOT)]
ARM_YAW = F.Y_T - p.JACK_Y                           # 29.6: the jack screw pushes the head at |y| 25.4


def yaw_worst(g, R, P0s=(0.0,), **kw):
    """Worst value of each clamp result over the slot positions (and preloads)."""
    res = [clamp_yaw(g, xb, R * ARM_YAW, P0=P0, **kw) for xb in XB for P0 in P0s]
    pick = SimpleNamespace()
    for key in ("T", "sig_strip", "sig_strip_out", "tau_strip", "q_strip", "sig_end", "tau_end", "V_end", "sig_H", "sig_N",
                "p_nut", "p_washer"):
        setattr(pick, key, max(getattr(r, key) for r in res))
    pick.pH = max((r.pH for r in res), key=lambda t: t[0])
    pick.pN = max((r.pN for r in res), key=lambda t: t[0])
    pick.res = res
    pick.lever = min(r.lever for r in res)
    return pick


def tilt_worst(g, Fz, up=True, **kw):
    res = [clamp_tilt(g, xb, Fz, up=up, **kw) for xb in XB]
    pick = SimpleNamespace(T=res[0].T)
    for key in ("sig_N_side", "tau_N_side", "sig_H_side", "tau_H_side", "qN", "qH", "p_H_solid"):
        setattr(pick, key, max(getattr(r, key) for r in res))
    return pick


# vertical loads, round-3 method (rigid pin on a Winkler foundation in z): the nut no longer touches PETG (9 mm slot);
# the nut plate's top edge (14 x 2) bears on the flat roof, the bolt on the web's hole, the head plate's bottom edge on the
# recess floor. A bound: the clamp couple below carries the moment in fact, and only the shear reaches the roofs.
z_zones = [(F.HALF_W_OUT - y_slot - F.PLATE_T, F.HALF_W_OUT - y_slot, N_LEN), (F.HALF_W_OUT - y_slot, F.HALF_W_OUT - y_rec, 3.0),
           (F.HALF_W_OUT - y_rec, F.HALF_W_OUT - y_boss, H_LEN)]
w0z, thz = rigid_pin(L.drop, arm_bolt, z_zones)
R_np = L.drop * N_LEN * (w0z * F.PLATE_T + thz * (z_zones[0][1] ** 2 - z_zones[0][0] ** 2) / 2)
check(f"B4 idler nut plate's top edge ({N_LEN:.0f} x {F.PLATE_T:.0f}) on the flat slot roof (rigid pin, round-4 zones; the nut"
      f" no longer touches PETG), 5 cm front corner", R_np / (N_LEN * F.PLATE_T), False, SF_STATIC, drop=True)

# yaw at the idler (no friction, no preload): B5 sustained pretension, B5c everyday reverse, B6 reverse stall
yS = yaw_worst(CLAMP_R4, L.R_sus, P0s=(0.0, 80.0))
yC = yaw_worst(CLAMP_R4, L.R_idler_cyc)
yR = yaw_worst(CLAMP_R4, L.R_idler_stall)
print(f"idler clamp yaw (no friction, no preload credited; worst of x {XB[0]:.0f}-{XB[-1]:.0f}): reverse stall"
      f" {L.R_idler_stall:.1f} N -> M {L.R_idler_stall * ARM_YAW:.0f} N*mm, prying bolt tension T {yR.T:.0f} N (lever"
      f" {yR.lever:.2f} mm between the washer's and the nut's resultants), web strips up to {yR.q_strip:.1f} N/mm out of plane,"
      f" end pieces up to {yR.V_end:.0f} N; steel plates {yR.sig_H:.0f} / {yR.sig_N:.0f} MPa")
for tag, y, R, sf in (("pretension 10 N sustained (P 0 or 80 N)", yS, L.R_sus, SF_CYCLIC),
                      (f"everyday reverse {L.R_idler_cyc:.1f} N cyclic", yC, L.R_idler_cyc, SF_CYCLIC),
                      (f"reverse stall {L.R_idler_stall:.1f} N", yR, L.R_idler_stall, SF_STATIC)):
    check(f"B5/B6 idler head plate on PETG (zone mean, peak {y.pH[1]:.1f} at x {y.pH[2]:.1f}), {tag}", y.pH[0], False, sf)
    check(f"B5/B6 idler nut plate on the 3.4 mm web (zone mean, peak {y.pN[1]:.1f} at x {y.pN[2]:.1f}), {tag}", y.pN[0], False,
          sf)
    check(f"B12 web strip root, bending across layers at the nut slot's sharp corner (Kt {KT_SHARP}), {tag}", y.sig_strip,
          True, sf)
    check(f"B13 web strip root, shear along the layer at the strip root, {tag}", y.tau_strip, True, sf, shear=True)
    check(f"B14 web end piece, bending at the nut slot's end corner (Kt {KT_SHARP} when the nut plate pushes), {tag}",
          y.sig_end, False, sf)
# drop: the 5 cm front corner tilts the idler bolt about X
tD = tilt_worst(CLAMP_R4, L.drop, up=True)
print(f"idler clamp tilt, 5 cm front corner {L.drop:.1f} N up at the track plane: prying T {tD.T:.0f} N (lever z"
      f" {ZH_TILT:.2f} + {ZN_TILT:.2f}); web top strip {tD.qN:.1f} N/mm, bottom strip {tD.qH:.1f} N/mm out of plane")
check(f"B15 web top strip root under the nut plate's top strip, across layers (Kt {KT_SHARP}), 5 cm front corner",
      tD.sig_N_side, True, SF_STATIC, drop=True)
check("B15 web top strip root, shear along the layer, 5 cm front corner", tD.tau_N_side, True, SF_STATIC, shear=True,
      drop=True)
check("B15 web bottom strip under the head plate (inner face; recess-floor corner), 5 cm front corner", tD.sig_H_side, True,
      SF_STATIC, drop=True)
# steel plates and steel bearing (reverse stall; drop)
check_metal("B16 steel head plate bending (slotted section), reverse stall", yR.sig_H, SY_PLATE_MPA)
check_metal("B16 steel nut plate bending (slotted section), reverse stall", yR.sig_N, SY_PLATE_MPA)
check_metal(f"B17 nut on the nut plate's two strips: mean steel bearing at T {yR.T:.0f} N, reverse stall", yR.p_nut,
            SY_PLATE_MPA)
check_metal(f"B17 Ø9 washer on the head plate: mean steel bearing at T {yR.T:.0f} N", yR.p_washer, SY_PLATE_MPA)
# jack screw: self-tapped M3 in the Ø2.6 printed pilot through the 6.5 mm buttress; teardrop leaves 270° of thread
L_jack = p.JACK_X[1] - p.JACK_X[0]
A_strip = math.pi * 3.0 * L_jack * 0.5 * 0.75        # thread-fill 0.5 (rounds 1-2), teardrop 270°
F_JACK_CAP = A_strip * allow_mpa(True, True)         # 143.6 N at the across-layer shear allowable (DFM's "142 N")
check(f"B7 jack-screw thread strip-out ({L_jack:.1f} mm, Ø{p.JACK_PILOT} pilot), reverse stall {L.R_idler_stall:.1f} N",
      L.R_idler_stall / A_strip, True, SF_STATIC, shear=True)
check(f"B8 jack-screw thread, pretension {L.R_sus:.0f} N sustained", L.R_sus / A_strip, True, SF_CYCLIC, shear=True)
# S1: tensioning slides the snugged bolt over two oiled steel faces (washer on head plate, nut on nut plate): 2 mu P + 2 T0
T_SNUG_NMM, K_OIL, MU_OIL, K_DRY, MU_DRY = 40.0, 0.15, 0.2, 0.2, 0.6
P_snug = T_SNUG_NMM / (K_OIL * 3.0)
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
# clamp: peaks, bounds and sensitivities of the governing rows
check(f"B6 head plate on PETG, reverse stall: PEAK (at a width step of the 1-D model) {yR.pH[1]:.1f} at x {yR.pH[2]:.1f}",
      yR.pH[1], False, SF_STATIC, info=True)
check(f"B6n nut plate on the web, reverse stall: PEAK {yR.pN[1]:.1f} at x {yR.pN[2]:.1f}", yR.pN[1], False, SF_STATIC,
      info=True)
check("B12 web strip root, reverse stall, WITHOUT the corner Kt (nominal)", yR.sig_strip_out / KT_SHARP, True, SF_STATIC,
      info=True)
check("B15 web top strip root, 5 cm front corner, WITHOUT the corner Kt (nominal)", tD.sig_N_side / KT_SHARP, True, SF_STATIC,
      info=True)
for lab, kw in (("washer bearing only to r 3.55 (head edge + 45° through the washer)", dict(r_e=3.55)),
                ("PETG foundation 500 N/mm³", dict(ks=500.0)), ("root fully rigid (root_soft 1.0)", dict(root_soft=1.0)),
                ("roots twice as soft (2.0)", dict(root_soft=2.0)), ("end pieces 3x stiffer", dict(k_end=3 * K_END)),
                ("end pieces half as stiff", dict(k_end=K_END / 2))):
    ys = yaw_worst(CLAMP_R4, L.R_idler_stall, **kw)
    check(f"B12 sensitivity, {lab}: web strip root (Kt {KT_SHARP}), reverse stall", ys.sig_strip, True, SF_STATIC, info=True)
# spec §8 proof loads on the round-4 clamp (SF_PROOF 1.0: must not damage a good part)
yP = yaw_worst(CLAMP_R4, L.R_idler_proof)
check(f"proof: reverse stall at 100 % PWM fresh pack ({L.R_idler_proof:.1f} N, §8 test 2): web strip root (Kt {KT_SHARP})",
      yP.sig_strip, True, SF_PROOF, info=True)
R44 = 4.5 * G_MS2
y44 = yaw_worst(CLAMP_R4, R44)
check(f"proof: 4.5 kg ({R44:.0f} N) rearward pull on the idler (§8 test 1): web strip root (Kt {KT_SHARP})", y44.sig_strip,
      True, SF_PROOF, info=True)
check(f"proof: 4.5 kg rearward pull: web end piece (Kt {KT_SHARP})", y44.sig_end, False, SF_PROOF, info=True)
t5 = tilt_worst(CLAMP_R4, F_prf, up=False)
check(f"proof: 5 kg ({F_prf:.0f} N) hung from the idler (§8 test 1, pulls down): web bottom strip root (Kt {KT_SHARP})",
      t5.sig_N_side, True, SF_PROOF, info=True)
check_metal(f"proof 5 kg on the idler bolt: M3 class 12.9 at the outer face", bend_round(F_prf * arm_bolt, D3_M3),
            SY_129_MPA, SF_PROOF, info=True)
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
check(f"head plate's top edge on the recess's 45° roof (all the drop shear on a 0.3 mm wide line, {H_LEN} long), 5 cm front"
      f" corner", L.drop / (H_LEN * 0.3), False, SF_STATIC, info=True)
# FIX: nut plate on the wall's flat outer face with a Ø9 washer under the nut (CLAMP_FIX): every clamp row again, and its
# proof loads. All FIX rows are advisory; they are the evidence for the required change in strength.md.
fS = yaw_worst(CLAMP_FIX, L.R_sus, P0s=(0.0, 80.0))
fC = yaw_worst(CLAMP_FIX, L.R_idler_cyc)
fR = yaw_worst(CLAMP_FIX, L.R_idler_stall)
fP = yaw_worst(CLAMP_FIX, L.R_idler_proof)
f44 = yaw_worst(CLAMP_FIX, R44)
fD = tilt_worst(CLAMP_FIX, L.drop, up=True)
f5 = tilt_worst(CLAMP_FIX, F_prf, up=False)
fT = CLAMP_FIX["web_t"]
for tag, y, sf in (("pretension sustained (P 0 or 80 N)", fS, SF_CYCLIC), ("everyday reverse cyclic", fC, SF_CYCLIC),
                   ("reverse stall", fR, SF_STATIC)):
    check(f"FIX head plate on PETG (zone mean), {tag}", y.pH[0], False, sf, info=True)
    check(f"FIX nut plate on the wall's outer face (zone mean), {tag}", y.pN[0], False, sf, info=True)
    check(f"FIX {fT:.1f} mm PETG between the plates: strip root across layers (Kt {KT_SHARP} at both faces), {tag}",
          y.sig_strip, True, sf, info=True)
    check(f"FIX strip root, shear along the layer, {tag}", y.tau_strip, True, sf, shear=True, info=True)
check(f"FIX top strip root under the nut plate (Kt {KT_SHARP}), 5 cm front corner", fD.sig_N_side, True, SF_STATIC, info=True)
check(f"FIX bottom strip root under the head plate, recess floor edge (Kt {KT_SHARP}), 5 cm front corner", fD.sig_H_side, True,
      SF_STATIC, info=True)
check("FIX strip root, shear along the layer, 5 cm front corner", max(fD.tau_N_side, fD.tau_H_side), True, SF_STATIC,
      shear=True, info=True)
check_metal("FIX steel plates bending, reverse stall (both 20.6 x 10 x 2)", max(fR.sig_H, fR.sig_N), SY_PLATE_MPA, info=True)
check_metal(f"FIX jack screw unchanged; idler M3 x 40 at the outer face, 5 cm front corner x {arm_bolt:.0f}",
            bend_round(L.drop * arm_bolt, D3_M3), SY_129_MPA, info=True)
check(f"FIX proof {L.R_idler_proof:.1f} N reverse stall (§8 test 2): strip root", fP.sig_strip, True, SF_PROOF, info=True)
check(f"FIX proof {R44:.0f} N rearward pull (§8 test 1): strip root", f44.sig_strip, True, SF_PROOF, info=True)
check(f"FIX proof {R44:.0f} N rearward pull: head plate on PETG (zone mean)", f44.pH[0], False, SF_PROOF, info=True)
check(f"FIX proof {F_prf:.0f} N hung from the idler (§8 test 1): strip root under the nut plate", f5.sig_N_side, True, SF_PROOF,
      info=True)
check(f"FIX proof {F_prf:.0f} N hung from the idler: shear along the layer", max(f5.tau_N_side, f5.tau_H_side), True,
      SF_PROOF, shear=True, info=True)
check(f"FIX nut plate's bottom edge on its lip ({H_LEN} x {F.PLATE_T}), {F_prf:.0f} N hang", F_prf / (H_LEN * F.PLATE_T),
      False, SF_STATIC, info=True)
fRs = yaw_worst(CLAMP_FIX, L.R_idler_stall, k_end=10000.0, root_soft=1.0)
check("FIX sensitivity (wall beyond the bolt slot 3x softer, rigid roots): strip root, reverse stall", fRs.sig_strip, True,
      SF_STATIC, info=True)
fDs = tilt_worst(CLAMP_FIX, L.drop, up=True, root_soft=1.0)
check("FIX sensitivity (rigid roots): strip root shear, 5 cm front corner", max(fDs.tau_N_side, fDs.tau_H_side), True,
      SF_STATIC, shear=True, info=True)
fDn = tilt_worst(CLAMP_FIX_NOWASHER, L.drop, up=True)
check("NOT ENOUGH: the same move without the washer under the nut: shear along the layer, 5 cm front corner",
      max(fDn.tau_N_side, fDn.tau_H_side), True, SF_STATIC, shear=True, info=True)
fDr = tilt_worst(CLAMP_FIX_RECESS, L.drop, up=True)
check("NOT ENOUGH: the nut plate in a 0.5 mm locating recess instead of on a lip: shear along the layer, 5 cm front corner",
      max(fDr.tau_N_side, fDr.tau_H_side), True, SF_STATIC, shear=True, info=True)
# thickening the web inside the wall instead (keeps the nut slot and its sharp root corners)
for lab, wt in (("web 5.4: idler-block face 2 mm inward (needs JACK_Y 23.4, JACK_Y_IN 20, JACK_X from 102.5)", 5.4),
                ("web 4.0: DIN 439 thin nut (1.8), nut slot 0.6 shallower", 4.0)):
    gw_ = dict(CLAMP_R4, web_t=wt)
    check(f"NOT ENOUGH: {lab}: web strip root (Kt {KT_SHARP}), reverse stall", yaw_worst(gw_, L.R_idler_stall).sig_strip, True,
          SF_STATIC, info=True)
    check(f"NOT ENOUGH: {lab}: web top strip root (Kt {KT_SHARP}), 5 cm front corner",
          tilt_worst(gw_, L.drop, up=True).sig_N_side, True, SF_STATIC, info=True)
print(f"FIX clamp: T {fR.T:.0f} N at the reverse stall; strips up to {fR.q_strip:.1f} N/mm; drop T {fD.T:.0f} N, strips"
      f" {fD.qN:.1f} / {fD.qH:.1f} N/mm; plates {fR.sig_H:.0f} / {fR.sig_N:.0f} MPa; idler hub {IDLER_HUB_SHORTER:.1f} mm shorter")
print(f"inserts: Ø{p.INSERT_D} holes have no HOLE_COMP and print about Ø{p.INSERT_D - HC:.1f} (round 3 note, unchanged)")

report(f"{JOB} strength checks")

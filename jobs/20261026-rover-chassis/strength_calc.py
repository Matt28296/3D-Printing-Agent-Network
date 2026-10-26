"""Strength check for jobs/20261026-rover-chassis (tracked rover, PETG), round 3.

Run from the project root with the CAD venv active (build123d, trimesh, scipy):
    source /home/claude/.venv-cad/bin/activate
    python3 jobs/20261026-rover-chassis/strength_calc.py

Round 3 = the round-3 geometry (model.py, rover_frame.py) with the round-1/2 method and the round-3 loads:
- drivetrain concept C: N20 rolled 45° in a diamond pocket through the wall, housing and a 2 mm nacelle, gearbox face on
  a 1 mm skin at |y| 45, Pololu hub on the shaft 10 mm from the track plane;
- idler bolt in a ±4 slot held by an M3 jack screw at its head; fully threaded class-12.9 axle bolts; insert columns.
The script builds the chassis with build123d for section properties (nacelle ring, trough cheeks) and recomputes the
rover mass from every rover part.stl at its print_requirements minima. Rows tagged as drop rows scale linearly with
the drop height; report() prints the height at which the first of them reaches its required SF.
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
WORLD = ns["design"]()                       # round-3 chassis in the rover world frame
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
printed = {"chassis": ("20261026-rover-chassis", 1, 0.4), "lid": ("20261026-rover-lid", 1, 0.4),
           "sprocket": ("20261026-rover-sprocket", 2, 0.2), "idler": ("20261026-rover-idler", 2, 0.2),
           "wheel": ("20261026-rover-wheel", 4, 0.2), "link": ("20261026-rover-track-link", 2 * F.N_LINKS, 0.12)}
pm = {k: printed_mass_g(*v) for k, v in printed.items()}
m_pin = math.pi / 4 * F.PIN_D ** 2 * 24.0 * 7.85e-3
BOM = [  # round-3 BUILD_GUIDE §1, grams (bought-part masses: hobby_parts where given, else typical catalogue values)
    ("2 x N20 gear motor", 2 * M.mass_g), ("2 x Pololu #1996 hub", 2 * F.HUB.mass_g), ("8 x M3x12 screw", 8 * 0.9),
    ("4 x M3x50 + 2 x M3x40 fully threaded", 4 * 2.5 + 2 * 2.1), ("2 x M3x20 set screw", 2 * 0.85),
    ("6 nuts, 6 nylocs, 26 washers, 2 DIN 9021", 6 * 0.25 + 6 * 0.3 + 26 * 0.12 + 2 * 0.35),
    ("4 heat-set inserts + 4 x M3x8", 4 * 0.4 + 4 * 0.65), (f"{2 * F.N_LINKS} steel pins Ø2 x 24", 2 * F.N_LINKS * m_pin),
    ("battery: 2 protected 18650 + holder", HP.BATT_2X18650_LONG.mass_g), ("ESP32 DevKit", 10.0),
    ("mini breadboard + TB6612 + MP1584", HP.MINI_BREADBOARD.mass_g + 3.0 + 2.5), ("HC-SR04", HP.HCSR04.mass_g),
    ("MTS-102 toggle + nuts", 6.0), ("wires, jumpers, capacitors, resistors, diode", 20.0),
    ("velcro strap, zip ties, foam tape, glue", 8.0)]
m_printed = sum(v[0] for v in pm.values())
m_solid = sum(v[1] for v in pm.values())
m_bought = sum(g for _, g in BOM)
m_est = m_printed + m_bought
print("\nmass check (round 3): printed at the print_requirements minima: "
      + ", ".join(f"{k} {v[0]:.1f} g" for k, v in pm.items()) + f" = {m_printed:.0f} g (all solid {m_solid:.0f} g)")
print("  bought (BUILD_GUIDE §1): " + ", ".join(f"{n} {g:.1f}" for n, g in BOM) + f" = {m_bought:.0f} g")
print(f"  rover {m_est:.0f} g at the print minima ({m_solid + m_bought:.0f} g if every printed part were solid);"
      f" design mass {MASS_DESIGN_G:.0f} g covers it by {100 * (MASS_DESIGN_G / m_est - 1):.0f} %")
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
KT_SHARP = 2.5         # sharp internal corner (skill; coordinator: >= 2 at the buttress and nacelle roots)
nut_t = F.NUT[1]                                     # 2.4
nut_recess = p.NUT_DEPTH - nut_t                     # 0.2: nut face below the outer face
s_nut0, s_nut1 = nut_recess, p.NUT_DEPTH             # nut zone, measured inward from the outer face
L_emb = F.HALF_W_OUT - y_boss                        # 10: wall + boss
nut_flat = F.NUT[0] / math.sqrt(3)                   # 3.175: hex flat length
print(f"\nchassis: wall {t_w}, boss/idler-block face |y| {y_boss}, road bosses Ø{2 * p.ROAD_BOSS_R:.0f} with a {p.JOIN} x 45°"
      f" collar (Kt {KT_CHAMFER}); pocket {2 * p.POCKET_HX:.1f} x {2 * p.POCKET_HY:.1f} CAD rolled 45°, nacelle walls"
      f" {F.NACELLE_WALL}, skin {F.SKIN} at |y| {F.MOTOR_FACE_Y}-{F.MOTOR_FACE_Y + F.SKIN}")


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
# ---- B. idler mount: 30 x 24 block (face |y| 28), ±4 slot with hull, sliding nut, jack screw at the head ----------------
xi1 = F.X_FRONT_OUT - t_w
bl = min(F.AXLE_DX + p.IDLER_BLOCK[0] / 2, xi1) - (F.AXLE_DX - p.IDLER_BLOCK[0] / 2)     # 25.5 (runs into the front wall)
a_idler = math.sqrt(bl * p.IDLER_BLOCK[1] / math.pi)
check(f"B1 idler block: wall bending, 5 cm front corner {L.drop:.1f} N (Kt {KT_CHAMFER} top strip)",
      plate_boss_moment_stress(L.drop * arm_w, a_idler, t_w, KT_CHAMFER), True, SF_STATIC, drop=True)
check(f"B2 idler block: wall bending, reverse stall {L.R_idler_stall:.1f} N (Kt {KT_SHARP}: sharp rear corner)",
      plate_boss_moment_stress(L.R_idler_stall * arm_w, a_idler, t_w, KT_SHARP), False, SF_STATIC)
check(f"B3 idler block: wall bending, pretension {L.R_sus:.0f} N sustained (Kt {KT_SHARP})",
      plate_boss_moment_stress(L.R_sus * arm_w, a_idler, t_w, KT_SHARP), False, SF_CYCLIC)
# vertical loads: the sliding nut bears on the flat roof of its slot with its top flat only (3.175 long), not 5.5
nb_i, ib_i, nb_i_pk, _, Rn_i, Ri_i, s0_i = pin_bearing(L.drop, arm_bolt, nut_flat)
check(f"B4 idler sliding nut on its slot roof (flat {nut_flat:.2f} x {nut_t}), 5 cm front corner", nb_i, False, SF_STATIC,
      drop=True)
# horizontal loads: the slot has no x-edges, so the bolt's moment about z goes through the clamp faces. The jack screw at
# the head (|y| 25.4) takes the force but adds to the moment: M = R (Y_T - JACK_Y). The Ø9 washer bears on the block face
# above and below the slot (hull to Z_A + 2.55); the nut only on two strips beside the slot.
r_s = (p.BOLT_D + HC) / 2
z_lo, z_hi = -r_s, r_s * math.sqrt(2)


def footprint(shape, n=600):
    """Area and I about the bolt's z axis (integral x^2 dA) of a washer/nut footprint minus the slot band."""
    A = Ix2 = 0.0
    xm = 0.0
    R = 7.0
    h = 2 * R / n
    for i in range(n):
        x = -R + (i + 0.5) * h
        for j in range(n):
            z = -R + (j + 0.5) * h
            if z_lo <= z <= z_hi or not shape(x, z):
                continue
            A += h * h
            Ix2 += x * x * h * h
            xm = max(xm, abs(x))
    return A, Ix2, xm


wd = F.WASHER_WIDE[0]
A_w, I_w, xm_w = footprint(lambda x, z: x * x + z * z <= (wd / 2) ** 2 and x * x + z * z >= 1.6 ** 2)
af = F.NUT[0]
A_n, I_n, xm_n = footprint(lambda x, z: abs(z) <= af / 2 and abs(x) <= af / math.sqrt(3) - abs(z) / math.sqrt(3)
                           and x * x + z * z >= 1.6 ** 2)
P_creep = 100.0                                      # clamp left after PETG creep (round 2's assumption)
arm_yaw = F.Y_T - p.JACK_Y                           # 29.6
share_head = I_w / (I_w + I_n)
print(f"idler clamp: Ø{wd} washer on the slotted block face A {A_w:.1f} mm², I_z {I_w:.1f} mm^4, x_max {xm_w:.2f};"
      f" nut strips A {A_n:.1f} mm², I_z {I_n:.1f}; the head carries {share_head * 100:.0f} % of the yaw moment"
      f" R x {arm_yaw:.1f} (jack screw at the head); opening moment at P {P_creep:.0f} N: {P_creep * I_w / (A_w * xm_w):.0f} N*mm")


def yaw_edge(R):
    Mh = share_head * R * arm_yaw
    return P_creep / A_w + Mh * xm_w / I_w


check(f"B5 idler clamp yaw: Ø{wd} washer edge on PETG, pretension {L.R_sus:.0f} N sustained (P {P_creep:.0f} N)",
      yaw_edge(L.R_sus), False, SF_CYCLIC)
check(f"B6 idler clamp yaw: washer edge, reverse stall {L.R_idler_stall:.1f} N", yaw_edge(L.R_idler_stall), False, SF_STATIC)
# jack screw: self-tapped M3 in the Ø2.6 printed pilot through the 6.5 mm buttress; teardrop leaves 270° of thread
L_jack = p.JACK_X[1] - p.JACK_X[0]
A_strip = math.pi * 3.0 * L_jack * 0.5 * 0.75        # thread-fill 0.5 (rounds 1-2), teardrop 270°
check(f"B7 jack-screw thread strip-out ({L_jack:.1f} mm, Ø{p.JACK_PILOT} pilot), reverse stall {L.R_idler_stall:.1f} N",
      L.R_idler_stall / A_strip, True, SF_STATIC, shear=True)
check(f"B8 jack-screw thread, pretension {L.R_sus:.0f} N sustained", L.R_sus / A_strip, True, SF_CYCLIC, shear=True)
h_btr = p.JACK_TOP - (F.FLOOR_Z + F.FLOOR_T)          # 14
lug = y_boss - p.JACK_Y                               # 2.6: jack axis to the solid block/column face
check(f"B9 buttress lug at the block face (y {y_boss:.0f}): bending, reverse stall (Kt {KT_SHARP})",
      bend_rect(L.R_idler_stall * lug, h_btr, L_jack), False, SF_STATIC, Kt=KT_SHARP)
check_metal(f"B10 idler M3 x 40 class 12.9: bending at the head face (y {y_boss:.0f}), reverse stall x {F.Y_T - y_boss:.0f}",
            bend_round(L.R_idler_stall * (F.Y_T - y_boss), D3_M3), SY_129_MPA)
check_metal(f"B11 idler M3 x 40 class 12.9: bending at the outer face, 5 cm front corner x {arm_bolt:.0f}",
            bend_round(L.drop * arm_bolt, D3_M3), SY_129_MPA, drop=True)

# ---- C. drivetrain concept C: N20 rolled 45° in the diamond pocket; nacelle 2 mm, skin 1 mm, track plane 10 mm out ------
hx, hy = (M.gb_w + p.GB_CLR) / 2, (M.gb_h + p.GB_CLR) / 2     # printed pocket half sizes 6.1 x 5.1 (CAD + HOLE_COMP)
y_face = F.MOTOR_FACE_Y
y_house = F.HALF_W_OUT + F.HOUSING_OUT                # 42: housing face = nacelle root
y_can_end = y_face - M.gb_len - M.can_len            # 20.5
e_c = 0.3                                            # contact line inside the gearbox face (its edge radius): assumption
L_c = y_face - y_house - e_c                         # 2.7: nacelle wall from its root to the contact line
t_n, t_s = F.NACELLE_WALL, F.SKIN
y_b = y_can_end + (y_face - y_can_end) / 3           # resultant of a triangular trough reaction along the motor
lev_v = (F.Y_T - y_b) / (y_face - y_b)               # 1.61: vertical (drop) loads, can on the open V-trough
y_pin = y_in_face                                    # pocket inner end in the wall (spec §4 lever)
lev_h = (F.Y_T - y_pin) / (y_face - y_pin)           # 1.87: horizontal loads (the open trough can't push sideways)
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
print(f"motor pocket: lever {lev_v:.2f} R vertical (trough reaction at y {y_b:.1f}), {lev_h:.2f} R horizontal (spec);"
      f" nacelle ring A {A_ring:.1f} mm², I {I_ring:.0f} mm^4 (build123d), c {c_ring:.2f}; skin cut {A_cut:.2f} mm²"
      f" (width {w_mid:.2f} - hole {d_hole}), h_eff {h_eff:.2f}; k_walls {k_wall(L_c):.0f} N/mm, k_skin {k_skin:.0f} N/mm")
# load split between the walls (plate bending to the housing) and the skin (diaphragm to the lower walls): each row
# uses the end of the stiffness range that is worse for it (walls x 1-1.5 for fold-line restraint, skin x 0.6-1 for
# its bending and the hole)
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
check(f"C1 skin (1 mm) diaphragm shear across layers, 5 cm rear corner: nacelle reaction {Ft_drop:.1f} N, skin share"
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
        # unknowns A1 A2 A3 (b..r0), B1 B2 B3 (r0..a)
        Am = np.zeros((6, 6))
        rhs = np.zeros(6)
        # M_r(b) = 0  -> 2 A2 (1 + nu) - A3 (1 - nu) / b^2 = 0
        Am[0, 1], Am[0, 2] = 2 * (1 + nu), -(1 - nu) / b ** 2
        # continuity of w, w', w'' at r0 (w'' with w' continuous = M_r continuous)
        Am[1, :] = [1, r0 ** 2, lr0, -1, -r0 ** 2, -lr0]
        rhs[1] = c4 * r0 ** 2 * lr0
        Am[2, :] = [0, 2 * r0, 1 / r0, 0, -2 * r0, -1 / r0]
        rhs[2] = c4 * (2 * r0 * lr0 + r0)
        Am[3, :] = [0, 2, -1 / r0 ** 2, 0, -2, 1 / r0 ** 2]
        rhs[3] = c4 * (2 * lr0 + 3)
        # w(a) = 0, w'(a) = 0
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
check(f"C10 skin out of plane: side {L.side:.0f} N outward on the gearbox face (Kt {KT_SHARP} at the pocket corner)", s_out,
      True, SF_CYCLIC, Kt=k_out)
Ft_house = lev_v * L.drop
check(f"C11 wall bending round the motor housing (Ø{2 * p.HOUSING_HALF_X:.1f} equivalent, Kt {KT_CHAMFER}), 5 cm rear corner",
      plate_boss_moment_stress(Ft_house * (y_face - e_c - y_mid), p.HOUSING_HALF_X, t_w, KT_CHAMFER), True, SF_STATIC,
      drop=True)
# trough: the can's rear reaction under a horizontal (track) load rides up the 45° V face; the zip tie holds it down and
# pulls up on the two cheek bridges over the 4 mm tunnel (fixed-fixed, span TIE_W); tie preload 30 N assumed
F_in_h = (lev_h - 1) * L.R_stall
F_tie = F_in_h + 30.0
z_tun = F.Z_A - M.can_d / 2 - 0.2                   # tunnel top: the cheeks bridge it
cheeks = section(y=p.TIE_Y, window=(-14, 14, z_tun + 0.05, F.Z_A))
cheek = min(cheeks, key=lambda c: c[0])
h_ch = p.TROUGH_TOP - z_tun                          # cheek depth above the tunnel
b_ch = cheek[0] / h_ch
check(f"C12 trough cheek bridge over the tie tunnel: tie {F_tie:.0f} N (can rear reaction {F_in_h:.1f} N + 30 N preload)",
      bend_rect(F_tie / 2 * p.TIE_W / 8, b_ch, h_ch), False, SF_STATIC)

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

# ---- advisory: bounds, sensitivities, the spec's lever, proof loads, fixes ----------------------------------------------
check(f"A4/A5 Winkler peaks: nut edge {nb_pk:.1f}, inner hole edge (peak), 5 cm drop", ib_pk, False, SF_STATIC, info=True)
check("A4 round-2 lever model (inner contact 1.5 mm at the boss face), nut bearing, 5 cm drop",
      L.drop * (F.Y_T - (y_boss + 0.75)) / ((F.HALF_W_OUT - p.NUT_DEPTH / 2) - (y_boss + 0.75)) / (nut_t * F.NUT[0]), False,
      SF_STATIC, info=True)
F_prf = 5.0 * G_MS2
check(f"proof 5 kg ({F_prf:.0f} N) at the wheel rim centre: boss collar", plate_boss_moment_stress(F_prf * arm_w, a_road, t_w,
      KT_CHAMFER), True, SF_PROOF, info=True)
check("proof 5 kg at the wheel rim centre: nut-trap bearing", pin_bearing(F_prf, arm_bolt, F.NUT[0])[0], False, SF_PROOF,
      info=True)
check_metal(f"proof 5 kg at the rim centre: M3 class 12.9 at the outer face", bend_round(F_prf * arm_bolt, D3_M3), SY_129_MPA,
            SF_PROOF, info=True)
check_metal(f"if A2-70 (fully threaded stainless) bolts are fitted instead: 5 cm drop", bend_round(L.drop * arm_bolt, D3_M3),
            SY_A2_70_MPA, info=True)
check_metal(f"if A2-70 bolts are fitted: proof 5 kg at the rim centre", bend_round(F_prf * arm_bolt, D3_M3), SY_A2_70_MPA,
            SF_PROOF, info=True)
check(f"proof 5 kg on the idler bolt (chassis §8 test 1): sliding nut on its slot roof", pin_bearing(F_prf, arm_bolt,
      nut_flat)[0], False, SF_PROOF, info=True)
check(f"idler clamp yaw at the reverse-stall proof ({L.R_idler_proof:.1f} N, 100 % PWM fresh pack)",
      yaw_edge(L.R_idler_proof), False, SF_PROOF, info=True)
check(f"idler clamp yaw if the preload held 350 N (joint just closed at T0): washer edge, pretension sustained",
      350.0 / A_w + share_head * L.R_sus * arm_yaw * xm_w / I_w, False, SF_CYCLIC, info=True)
check(f"idler sliding nut on its slot bottom under {P_creep:.0f} N clamp ({A_n:.1f} mm² beside the slot): creeps",
      P_creep / A_n, False, SF_CYCLIC, info=True)
check(f"jack-screw thread, reverse-stall proof {L.R_idler_proof:.1f} N", L.R_idler_proof / A_strip, True, SF_PROOF, shear=True,
      info=True)
L_btr = p.JACK_X[1] - p.JACK_X[0]
check(f"BOUND buttress as a column off the floor only ({L_btr:.1f} x {p.HALF_W_OUT - t_w - p.JACK_Y_IN:.1f}, Kt {KT_SHARP}),"
      f" reverse stall", bend_rect(L.R_idler_stall * (F.Z_A - (F.FLOOR_Z + F.FLOOR_T)), y_in_face - p.JACK_Y_IN, L_btr), True,
      SF_STATIC, Kt=KT_SHARP, info=True)
check("C1 BOUND skin carries all (rigid diaphragm), 5 cm rear corner", skin_tau(Ft_drop, 1.0), True, SF_STATIC, shear=True,
      info=True)
check("C2 central split (walls x1, skin x1), 5 cm rear corner", wall_sigma(Ft_drop, 1 - sh_skin), False, SF_STATIC, info=True)
check("C2 BOUND walls carry all (no skin), 5 cm rear corner", wall_sigma(Ft_drop, 1.0), False, SF_STATIC, info=True)
check(f"C1 at the spec's lever {lev_h:.2f} R (rear reaction at the pocket's inner end), 5 cm rear corner",
      skin_tau(lev_h * L.drop), True, SF_STATIC, shear=True, info=True)
check(f"C2 at the spec's lever {lev_h:.2f} R, 5 cm rear corner", wall_sigma(lev_h * L.drop), False, SF_STATIC, info=True)
mu_drop = 0.3
s_in_d, _ = skin_out_of_plane(mu_drop * L.drop, True)
check(f"C9 skin, sideways friction in a corner drop (mu {mu_drop} x {L.drop:.1f} N) on the thrust washer", s_in_d, True,
      SF_STATIC, info=True)
check(f"C8 reaction torque at the proof {T_PROOF_NMM:.0f} N*mm", T_PROOF_NMM / M.gb_w / (M.gb_len * 1.0), False, SF_PROOF,
      info=True)
# S-08 sensitivity: an ungated 2 kg*cm motor (Phipps 196 N*mm) at the sketch's 6.0 V cap
F_s08 = S08_6V_NMM[-1][1] / F.RP
R_i08 = 2 * (T0_N + F_s08)
check(f"S-08 ungated 196 N*mm motor: jack-screw thread, reverse stall {R_i08:.1f} N", R_i08 / A_strip, True, SF_STATIC,
      shear=True, info=True)
check(f"S-08 ungated 196 N*mm motor: idler clamp yaw, reverse stall", yaw_edge(R_i08), False, SF_STATIC, info=True)
check(f"S-08 ungated 196 N*mm motor: skin shear, track stall ({lev_h:.2f} x {T0_N * 2 + F_s08:.1f} N)",
      skin_tau(lev_h * (2 * T0_N + F_s08)), True, SF_STATIC, shear=True, info=True)
# N20 shaft (bought): D-section Ø3, flat 2.5 from the far side; minimum section modulus over every bending direction
gs = 600
hh = M.shaft_d / gs
pts = [(-M.shaft_d / 2 + (i + 0.5) * hh, -M.shaft_d / 2 + (j + 0.5) * hh) for i in range(gs) for j in range(gs)]
pts = np.array([q for q in pts if q[0] ** 2 + q[1] ** 2 <= (M.shaft_d / 2) ** 2 and q[1] <= M.shaft_flat - M.shaft_d / 2])
cx, cy = pts.mean(axis=0)
Zmin = 1e9
for ang in np.linspace(0, math.pi, 181):
    u = (pts[:, 0] - cx) * math.cos(ang) + (pts[:, 1] - cy) * math.sin(ang)
    Zmin = min(Zmin, (u ** 2).sum() * hh * hh / (np.abs(u).max() + hh / 2))
for lab, R in ((f"stall {L.R_stall:.1f} N", L.R_stall), (f"5 cm corner {L.drop:.1f} N", L.drop)):
    check_metal(f"N20 shaft (bought), arm {F.SHAFT_ARM:.0f}, Z_min {Zmin:.3f} mm³: {lab}", R * F.SHAFT_ARM / Zmin, SY_ROD_MPA,
                info=True)
# FIX rows
for ts in (1.5, 2.0):
    Lc2 = L_c - (ts - t_s)
    kw2 = k_wall(Lc2)
    ks2 = k_skin * ts / t_s
    sh_s = ks2 / (ks2 + kw2)
    sh_w = 1.5 * kw2 / (1.5 * kw2 + 0.6 * ks2)
    arm2 = F.SHAFT_ARM + (ts - t_s)
    check(f"FIX SKIN {t_s:.0f} -> {ts} (gearbox face |y| {y_face - (ts - t_s):.1f}, shaft arm {arm2:.1f}): skin shear, 5 cm corner",
          skin_tau(Ft_drop, sh_s, ts), True, SF_STATIC, shear=True, info=True)
    check(f"FIX SKIN {t_s:.0f} -> {ts}: rigid-diaphragm bound", skin_tau(Ft_drop, 1.0, ts), True, SF_STATIC, shear=True, info=True)
    check(f"FIX SKIN {t_s:.0f} -> {ts}: nacelle wall root, 5 cm corner (L {Lc2:.1f})", wall_sigma(Ft_drop, sh_w, Lc2), False,
          SF_STATIC, info=True)
    check_metal(f"FIX SKIN {t_s:.0f} -> {ts}: N20 shaft at the 5 cm corner (arm {arm2:.1f})", L.drop * arm2 / Zmin, SY_ROD_MPA,
                info=True)
    check_metal(f"FIX SKIN {t_s:.0f} -> {ts}: N20 shaft at stall (arm {arm2:.1f}; Architect's criterion SF >= 2)",
                L.R_stall * arm2 / Zmin, SY_ROD_MPA, 2.0, info=True)
def plate_fix(Lp, Hp, band=None):
    """Steel plate (Lp x Hp) bearing on PETG, the bolt-slot band cut out: A, I about the bolt's z axis, x_max."""
    bnd = (z_hi - z_lo) if band is None else band
    return Lp * (Hp - bnd), (Hp - bnd) * Lp ** 3 / 12, Lp / 2


# the yaw moment needs a stiff footprint on BOTH clamp faces: the head side resists it, the nut side must carry the clamp
# and prying tension. Package that passes: inner plate 21 x 10 x 2 (x 108-129, clear of the buttress and front strip),
# outer nut plate 14 x 8 x 2 in a nut slot opened to 9 mm tall and 2 mm deeper, both slotted 3.4 x 12
A1, I1, x1 = plate_fix(21.0, 10.0)
A2, I2, x2 = plate_fix(14.0, 8.0)
sh1 = I1 / (I1 + I2)
W_need_rev = SF_STATIC * 0 + share_head * L.R_idler_stall * arm_yaw / (ALLOW_INPLANE_MPA / SF_STATIC - P_creep / A1)
print(f"idler clamp fix: inner plate A {A1:.0f} mm², I/x {I1 / x1:.0f} mm³; nut plate A {A2:.0f} mm², I/x {I2 / x2:.0f} mm³;"
      f" needed on the head side for SF 3 at the reverse stall: I/x >= {W_need_rev:.0f} mm³ (Ø9 washer: {I_w / xm_w:.0f})")
for R, sf, tag in ((L.R_idler_stall, SF_STATIC, "reverse stall"), (L.R_sus, SF_CYCLIC, "pretension sustained")):
    Mz = R * arm_yaw
    check(f"FIX idler clamp, inner steel plate 21 x 10 x 2: PETG edge pressure, {tag}", P_creep / A1 + sh1 * Mz * x1 / I1, False,
          sf, info=True)
    # bolt tension = clamp left after creep + prying once the head-side moment exceeds the inner plate's opening moment
    T_bolt = P_creep + max(0.0, sh1 * Mz - P_creep * I1 / (A1 * x1)) / x1
    check(f"FIX idler clamp, outer nut plate 14 x 8 x 2 (nut slot 9 tall): PETG edge pressure, {tag} (bolt {T_bolt:.0f} N)",
          T_bolt / A2 + (1 - sh1) * Mz * x2 / I2, False, sf, info=True)
w0p, thp = rigid_pin(L.drop, arm_bolt, [(s_nut0, s_nut1, nut_flat), (s_nut1, s_nut1 + 2.0, 14.0), (s_nut1 + 2.0, L_emb, 3.0)])
R_pl = L.drop * 14.0 * (w0p * 2.0 + thp * ((s_nut1 + 2.0) ** 2 - s_nut1 ** 2) / 2)
check("FIX idler nut plate's top edge (14 x 2) on the slot roof, 5 cm front corner", R_pl / (14.0 * 2.0), False, SF_STATIC,
      info=True)
check("FIX idler sliding nut alone: DIN 557 square nut 5.5 x 2.4 (full 5.5 top face), 5 cm front corner",
      pin_bearing(L.drop, arm_bolt, F.NUT[0])[0], False, SF_STATIC, info=True)
check("NOT ENOUGH: DIN 9021 M4 Ø12 washer under the head, reverse stall", P_creep / footprint(lambda x, z: 1.6 ** 2 <= x * x + z * z
      <= 36.0)[0] + L.R_idler_stall * arm_yaw * 6.0 / footprint(lambda x, z: 1.6 ** 2 <= x * x + z * z <= 36.0)[1], False,
      SF_STATIC, info=True)
# assembly: axle-bolt tightening into PETG (the design relies on no preload; over-tightening crushes the nut trap)
A_trap = 3 * math.sqrt(3) / 2 * (F.NUT[0] / math.sqrt(3)) ** 2 - math.pi / 4 * (p.BOLT_D) ** 2
for T_nm in (0.15, 0.5):
    P_t = T_nm * 1000 / (0.2 * 3.0)
    check(f"assembly: road-wheel bolt tightened to {T_nm} N*m (P {P_t:.0f} N): nut on the trap bottom ({A_trap:.1f} mm²)",
          P_t / A_trap, False, SF_STATIC, info=True)
print(f"inserts: Ø{p.INSERT_D} holes have no HOLE_COMP and print about Ø{p.INSERT_D - HC:.1f}: an M3 x {ins_len} insert"
      f" (knurl ~Ø4.6) then displaces {math.pi / 4 * (4.6 ** 2 - (p.INSERT_D - HC) ** 2) * ins_len:.0f} mm³ instead of"
      f" {math.pi / 4 * (4.6 ** 2 - p.INSERT_D ** 2) * ins_len:.0f}: more melt rises round the insert (scrape it flush), the"
      f" grip is not reduced, and the column wall left is {(p.COLUMN_D - 4.6) / 2:.1f} mm")

report(f"{JOB} strength checks")

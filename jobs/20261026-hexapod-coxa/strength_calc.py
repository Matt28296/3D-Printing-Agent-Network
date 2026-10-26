"""Strength check for jobs/20261026-hexapod-coxa (round 3). Run from the project root:
    python3 jobs/20261026-hexapod-coxa/strength_calc.py
It needs build123d, trimesh and scipy, like cad_checks.py (CAD venv: /home/claude/.venv-cad). Takes 0.5-2 min:
it builds all five hexapod parts to get the robot's printed mass.

strength-analyst, round 3, 2026-10-26. Hand calculations (strength-checks skill) on placeholder PETG allowables.
Section properties come from the build123d solid, sampled on the printed layers: perimeters and top/bottom solid
layers count as solid, the gyroid infill core as a cellular solid (stiffness rho^2, strength rho^1.5), as in the
rover-wheel review. The block between the ==== lines at the top is identical in all five hexapod strength_calc.py.
"""
# ==== shared hexapod round-3 load model (identical block in all five round-3 strength_calc.py) =================
# Needs the CAD venv (build123d, trimesh, scipy). Reads hex_frame.py, tools/hobby_parts.py, each hexapod model.py
# (built with build123d) and print_requirements.json. Writes nothing.
import json
import math
import os
import runpy
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
JOBS = os.path.join(ROOT, "jobs")
ASM = os.path.join(JOBS, "20261026-hexapod-assembly")
sys.path[:0] = [os.path.join(ROOT, "tools"), ASM]
import hex_frame as H  # noqa: E402
from hobby_parts import HORN_DEPTH, LIPO_2S_1000, PCA9685_BOARD  # noqa: E402,F401

T0 = time.time()
JOB = {k: "20261026-hexapod-" + k for k in ("body-bottom", "body-top", "coxa", "femur", "tibia")}
QTY = {"body-bottom": 1, "body-top": 1, "coxa": 6, "femur": 6, "tibia": 6}
SERVO = H.SERVO
STALL = SERVO.stall_torque_nmm                    # 216 N.mm at 6 V (TowerPro)

# --- allowables: library/materials.csv has no rows, inputs/ has no datasheet -> skill placeholders, NEEDS_TEST at best
ALLOW_XY = 25.0          # MPa, PETG along the layers (strength-checks placeholder, already knocked down)
Z_RATIO = 0.5            # across the layers / along (placeholder)
SHEAR_RATIO = 0.5        # shear / normal (Tresca), as every earlier hexapod, arm and rover check
E_MPA = 1800.0           # placeholder PETG modulus
SF_STATIC, SF_CYCLIC = 3.0, 4.0
T_SERVICE_C, T_SOFTEN_C = 40.0, 70.0
RHO = 1.27e-3            # g/mm3 PETG (the slicer's filament profile)
G = 9.81e-3              # N per gram

# --- printed construction: PrusaSlicer 0.20 mm QUALITY @MK3 + each job's print_requirements.json ----------------
LAYER = 0.2
W_EXT = 0.45                                       # external perimeter width (profile)
SPACING = 0.45 - LAYER * (1 - math.pi / 4)         # 0.407: perimeter spacing at 0.2 mm layers (PrusaSlicer)
MASS_CAL = 1.045         # slicer filament_g / layer-model mass on the four round-2 slices: 1.014-1.045 -> the max


def core_stiff(fill):    # infill core as a cellular solid (Gibson-Ashby, as in the rover-wheel review): E * rho^2
    return fill ** 2


def core_strength(fill):  # its strength (crush, shear): the solid allowable * rho^1.5
    return fill ** 1.5


def allow(across, shear=False):
    a = ALLOW_XY * (Z_RATIO if across else 1.0)
    return a * (SHEAR_RATIO if shear else 1.0)


def print_settings(part):
    req = json.load(open(os.path.join(JOBS, JOB[part], "print_requirements.json")))["min"]
    return dict(perimeters=req["perimeters"], top=req["top_solid_layers"], bottom=req["bottom_solid_layers"],
                fill=req["fill_density"] / 100.0)


def build_part(part):
    ns = runpy.run_path(os.path.join(JOBS, JOB[part], "model.py"), run_name="model")
    return ns["build"](), ns


# --- printed-material field: a slicer-like layer model --------------------------------------------------------------
class PrintField:
    """The part's 0.2 mm layers rasterised (pitch mm, print frame) and classified as the slicer builds them:
    1 perimeter band (0.45 + (n-1) x 0.407 mm inside each layer outline, holes included), 2 top/bottom solid (not
    covered by every layer within n layers above and below), 3 infill, 0 void."""

    def __init__(self, solid, perimeters, top, bottom, fill, pitch=0.1):
        import trimesh
        from scipy import ndimage
        v, f = solid.tessellate(0.005, 0.1)
        mesh = trimesh.Trimesh(np.array([(q.X, q.Y, q.Z) for q in v]), np.array(f), process=True)
        lo, hi = mesh.bounds
        self.p, self.fill, self.perimeters = pitch, fill, perimeters
        self.band = W_EXT + (perimeters - 1) * SPACING
        self.x0, self.y0, self.z0 = lo[0] - 2 * pitch, lo[1] - 2 * pitch, lo[2]
        self.nx, self.ny = int((hi[0] - self.x0) / pitch) + 3, int((hi[1] - self.y0) / pitch) + 3
        self.nz = int(round((hi[2] - lo[2]) / LAYER))
        masks = [self._raster(trimesh.intersections.mesh_plane(mesh, (0, 0, 1), (0, 0, self.z0 + (k + 0.5) * LAYER)))
                 for k in range(self.nz)]
        self.cls, self.solid_v, self.infill_v = [], 0.0, 0.0
        for k in range(self.nz):
            if masks[k] is None:
                self.cls.append(None)
                continue
            mm, ((j0, j1), (i0, i1)) = masks[k]
            d = ndimage.distance_transform_edt(np.pad(mm, 1))[1:-1, 1:-1] * pitch
            per = mm & (d <= self.band + 0.5 * pitch)
            cov = mm.copy()
            for kk in list(range(k + 1, k + top + 1)) + list(range(k - bottom, k)):
                cov &= self._crop(masks[kk] if 0 <= kk < self.nz else None, j0, j1, i0, i1)
            c = np.zeros(mm.shape, np.uint8)
            c[mm] = 2
            c[mm & cov] = 3
            c[per] = 1
            self.cls.append(((j0, i0), c))
            self.solid_v += ((c == 1) | (c == 2)).sum() * pitch * pitch * LAYER
            self.infill_v += (c == 3).sum() * pitch * pitch * LAYER
        self.mass_g = MASS_CAL * RHO * (self.solid_v + fill * self.infill_v)

    def _raster(self, seg):
        if len(seg) == 0:
            return None
        p = self.p
        a, b = seg[:, 0, :2], seg[:, 1, :2]
        keep = np.abs(b[:, 1] - a[:, 1]) > 1e-12
        a, b = a[keep], b[keep]
        ylo, yhi = np.minimum(a[:, 1], b[:, 1]), np.maximum(a[:, 1], b[:, 1])
        j0 = np.ceil((ylo - self.y0) / p - 0.5).astype(int)
        j1 = np.ceil((yhi - self.y0) / p - 0.5).astype(int)
        n = np.clip(j1 - j0, 0, None)
        idx = np.repeat(np.arange(len(a)), n)
        rows = np.repeat(j0, n) + (np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n))
        yc = self.y0 + (rows + 0.5) * p
        xc = a[idx, 0] + (yc - a[idx, 1]) * (b[idx, 0] - a[idx, 0]) / (b[idx, 1] - a[idx, 1])
        col = np.clip(np.ceil((xc - self.x0) / p - 0.5).astype(int), 0, self.nx)
        tog = np.zeros((self.ny, self.nx + 1), np.int32)
        np.add.at(tog, (rows, col), 1)
        m = (np.cumsum(tog, axis=1)[:, :self.nx] % 2) == 1
        rr, cc = np.nonzero(m.any(axis=1))[0], np.nonzero(m.any(axis=0))[0]
        if len(rr) == 0:
            return None
        return m[rr[0]:rr[-1] + 1, cc[0]:cc[-1] + 1].copy(), ((rr[0], rr[-1] + 1), (cc[0], cc[-1] + 1))

    @staticmethod
    def _crop(m, j0, j1, i0, i1):
        out = np.zeros((j1 - j0, i1 - i0), bool)
        if m is None:
            return out
        mm, ((a0, a1), (b0, b1)) = m
        r0, r1, c0, c1 = max(j0, a0), min(j1, a1), max(i0, b0), min(i1, b1)
        if r0 < r1 and c0 < c1:
            out[r0 - j0:r1 - j0, c0 - i0:c1 - i0] = mm[r0 - a0:r1 - a0, c0 - b0:c1 - b0]
        return out

    def cls_at(self, x, y, z):
        """Material class at print-frame points (arrays of equal shape)."""
        x, y, z = np.broadcast_arrays(np.asarray(x, float), np.asarray(y, float), np.asarray(z, float))
        out = np.zeros(x.shape, np.uint8)
        k = np.floor((z - self.z0) / LAYER).astype(int)
        i = np.floor((x - self.x0) / self.p).astype(int)
        j = np.floor((y - self.y0) / self.p).astype(int)
        for kk in np.unique(k):
            if kk < 0 or kk >= self.nz or self.cls[kk] is None:
                continue
            (j0, i0), c = self.cls[kk]
            sel = k == kk
            jj, ii = j[sel] - j0, i[sel] - i0
            ok = (jj >= 0) & (jj < c.shape[0]) & (ii >= 0) & (ii < c.shape[1])
            vals = np.zeros(sel.sum(), np.uint8)
            vals[ok] = c[jj[ok], ii[ok]]
            out[sel] = vals
        return out

    def weights(self, x, y, z, kind="stiff"):
        c = self.cls_at(x, y, z)
        core = core_stiff(self.fill) if kind == "stiff" else core_strength(self.fill)
        return np.where((c == 1) | (c == 2), 1.0, np.where(c == 3, core, 0.0))


def plane_samples(origin, u, v, u_rng, v_rng, du, dv):
    """Grid on the plane origin + s u + t v (print frame): points (3 x N), s, t, cell area."""
    s = np.arange(u_rng[0] + du / 2, u_rng[1], du)
    t = np.arange(v_rng[0] + dv / 2, v_rng[1], dv)
    S, T = np.meshgrid(s, t, indexing="ij")
    o, u, v = (np.asarray(a, float) for a in (origin, u, v))
    P = o[:, None] + np.outer(u, S.ravel()) + np.outer(v, T.ravel())
    return P, S.ravel(), T.ravel(), du * dv


def _hull(pts):
    """Convex-hull vertices of 2D points (the extreme bending stress of a section lies on them)."""
    if len(pts) < 4:
        return pts
    from scipy.spatial import ConvexHull
    try:
        return pts[ConvexHull(pts).vertices]
    except Exception:
        return pts


def sec_props(w, s, t, dA):
    """Area, centroid, second moments about the centroid (Iss = int (s-sc)^2 dA: stress varying along s), largest
    distances to material, and the hull of the full-strength points ('hs') and of the infill-core points ('hc')."""
    A = w.sum() * dA
    if A <= 0:
        return dict(A=0.0)
    sc, tc = (w * s).sum() * dA / A, (w * t).sum() * dA / A
    on, full = w > 0, w >= 0.999
    core = on & ~full
    return dict(A=A, sc=sc, tc=tc, Iss=(w * (s - sc) ** 2).sum() * dA, Itt=(w * (t - tc) ** 2).sum() * dA,
                Ist=(w * (s - sc) * (t - tc)).sum() * dA, cs=np.abs(s[on] - sc).max(), ct=np.abs(t[on] - tc).max(),
                s_lo=s[on].min(), s_hi=s[on].max(), t_lo=t[on].min(), t_hi=t[on].max(),
                hs=_hull(np.column_stack([s[full], t[full]])), hc=_hull(np.column_stack([s[core], t[core]])),
                w_core=float(w[core].max()) if core.any() else 0.0)


def bend_stress(props, N, Ms, Mt):
    """Largest normal stress (MPa) on a section (s, t, n right-handed; Ms, Mt the moments about s and t at the
    centroid, N along n): unsymmetric biaxial bending, evaluated on the hulls. Infill-core points carry rho^2 of
    the strain stress against rho^1.5 of the allowable, so they count at stress x rho^0.5 (never governing when
    the skin is further out, but checked)."""
    Iss, Itt, Ist = props["Iss"], props["Itt"], props["Ist"]
    det = Ist * Ist - Iss * Itt
    a = (Ms * Ist + Mt * Itt) / det          # sigma = N/A + a (s - sc) + b (t - tc)
    b = -(Ms * Iss + Mt * Ist) / det
    out = np.zeros(np.shape(N))
    for pts, fac in ((props["hs"], 1.0), (props["hc"], props["w_core"] ** 0.25 if props["w_core"] > 0 else 0.0)):
        for (ss, tt) in pts:
            out = np.maximum(out, fac * np.abs(N / props["A"] + a * (ss - props["sc"]) + b * (tt - props["tc"])))
    return out


def section(field, origin, u, v, u_rng, v_rng, du=0.1, dv=None, kind="stiff"):
    """Section on a plane through the printed part: (solid properties, as-printed properties). As printed:
    perimeters and solid layers weigh 1, the infill core rho^2 (kind 'stiff') or rho^1.5 (kind 'strength')."""
    dv = LAYER if dv is None else dv
    P, s, t, dA = plane_samples(origin, u, v, u_rng, v_rng, du, dv)
    c = field.cls_at(*P)
    w = field.weights(*P, kind=kind)
    return sec_props((c > 0).astype(float), s, t, dA), sec_props(w, s, t, dA)


def exact_section(solid, origin, normal, xdir):
    """Exact section of the build123d solid on a plane: area, centroid and inertia matrix about the centroid."""
    from build123d import Face, Plane
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps
    face = Face.make_rect(600.0, 600.0, Plane(origin=origin, x_dir=xdir, z_dir=normal))
    com = BRepAlgoAPI_Common(solid.wrapped, face.wrapped)
    com.Build()
    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(com.Shape(), props)
    c, M = props.CentreOfMass(), props.MatrixOfInertia()
    return props.Mass(), (c.X(), c.Y(), c.Z()), [[M.Value(i, j) for j in (1, 2, 3)] for i in (1, 2, 3)]


# --- robot mass -------------------------------------------------------------------------------------------------------
# Bought parts as BUILD_GUIDE.md section 1 lists them (round 3). Unit masses: hobby_parts where it has one, deep
# review 05 (DR05) where it gave one, otherwise an upper-typical estimate (est.).
BOUGHT = [
    ("18 x MG90S (hobby_parts, 13.4 g)", 18 * SERVO.mass_g),
    ("18 single-arm horns (est. 0.35 g)", 18 * 0.35),
    ("2 x PCA9685 (hobby_parts, 9 g)", 2 * PCA9685_BOARD.mass_g),
    ("ESP32 DevKit (DR05)", 10.0),
    ("2S 1000 mAh LiPo (hobby_parts)", LIPO_2S_1000.mass_g),
    ("UBEC 6 V 5-10 A (DR05: 21 g at 5 A; est. for 8-10 A)", 25.0),
    ("MP1584 buck (hobby_parts)", 2.0),
    ("main switch, 12 mm-bushing toggle >= 10 A (est.)", 15.0),
    ("7.5 A blade fuse + inline holder (est.)", 6.0),
    ("XT30 pigtail, 18 AWG (est.)", 5.0),
    ("LiPo voltage alarm (est.)", 7.0),
    ("2 x 1000 uF 10 V, divider, Schottky (est.)", 5.6),
    ("12 servo extensions, 15 cm (DR05: 3 g each)", 36.0),
    ("screws, washers, nuts (30 M2x12-14, 12 M2x10, 12 M2x8, 18 M1.7x5, 4 M3x8, 8 M2.5x6, 36 washers, 6 penny "
     "washers, 12 nuts; est.)", 33.4),
    ("zip ties, velcro strap, tape (est.)", 10.0),
    ("power harness, I2C and power jumpers (DR05: 17 g; est.)", 20.0),
]
M_BOUGHT = sum(m for _, m in BOUGHT)
FIELD, MODEL, SOLID = {}, {}, {}
for _k in QTY:
    SOLID[_k], MODEL[_k] = build_part(_k)
    FIELD[_k] = PrintField(SOLID[_k], **print_settings(_k))
M_PART = {k: FIELD[k].mass_g for k in QTY}
M_PART_SOLID = {k: SOLID[k].volume * RHO for k in QTY}
M_PRINTED = sum(QTY[k] * M_PART[k] for k in QTY)
M_TOTAL = M_PRINTED + M_BOUGHT
W_N = M_TOTAL * G
M_DECK = M_PART["body-top"] + 2 * PCA9685_BOARD.mass_g + 10.0 + 2.0 + 15.0 + 10.0   # deck, 2 boards, ESP32, buck,
#                                                      switch, half the harness (the UBEC stands on the bottom plate)
# robot mass with the round-3 required changes made (coxa printed solid; body-bottom MARGIN 8 and O10 columns, whose
# +13 g the body-bottom strength_calc.py computes): the basis of every change-set row
M_COXA_FIX = MASS_CAL * RHO * SOLID["coxa"].volume
BOTTOM_FIX_G = 13.0
W_ALL_FIX = W_N + (6 * (M_COXA_FIX - M_PART["coxa"]) + BOTTOM_FIX_G) * G

# --- leg poses, servo torques, tripod shares -----------------------------------------------------------------------
class Pose:
    """One leg (leg 0's mount; a leg's internal loads depend only on its own joint angles) in (coxa, femur, tibia),
    leg_frames' convention. Foot force f (world) = B @ (radial, tangential, up), radial/tangential along C x/y.
    Servo torques (coxa about C z, femur about S1 z, knee about S2 z) = Gw @ f."""

    def __init__(self, angles):
        self.angles = tuple(float(a) for a in angles)
        self.fr, self.foot = H.leg_frames(*H.LEG_MOUNTS[0], *self.angles)
        C = self.fr["C"][:3, :3]
        self.B = np.column_stack([C[:, 0], C[:, 1], [0.0, 0.0, 1.0]])
        self.Gw = np.array([np.cross(self.fr[k][:3, 2], self.foot - self.fr[k][:3, 3]) for k in ("C", "S1", "S2")])

    def force(self, radial, tangential, up):
        return self.B @ np.array([radial, tangential, up], float)

    def torques(self, f):
        return self.Gw @ np.asarray(f, float)

    def local(self, key, f):
        """Foot position and foot force (rows of f: N x 3, world) in frame `key` (C, F, T, S0, ...)."""
        A = self.fr[key]
        R, o = A[:3, :3], A[:3, 3]
        return R.T @ (self.foot - o), np.atleast_2d(f) @ R


CG_BOX = 3.0             # centre of gravity anywhere within +-3 mm of the body centre (legs swing; DR05 found 1 mm)


def max_shares(feet_xy):
    best = np.zeros(3)
    A = np.vstack([np.ones(3), feet_xy[:, 0], feet_xy[:, 1]])
    for dx in (-CG_BOX, 0.0, CG_BOX):
        for dy in (-CG_BOX, 0.0, CG_BOX):
            best = np.maximum(best, np.linalg.solve(A, np.array([1.0, dx, dy])))
    return best


NEUTRAL = (0.0, *H.sketch_to_frames(H.NEUTRAL_FEMUR, H.NEUTRAL_TIBIA))
POSES = []               # (leg, angles, max share) for each planted foot of every tripod-only frame + the neutral tripods
_feet0 = np.array(H.neutral_feet())
for _tri in (H.TRIPOD_A, H.TRIPOD_B):
    for _k, _i in enumerate(_tri):
        POSES.append((_i, NEUTRAL, max_shares(_feet0[list(_tri), :2])[_k]))
for _stride in (30.0, 40.0):
    for _fr in range(H.CYCLE_FRAMES):
        _ang, _ft, _down = H.gait_pose(_fr, _stride)
        _pl = [i for i in range(6) if _down[i]]
        if len(_pl) == 3:
            _s = max_shares(np.array([_ft[i][:2] for i in _pl]))
            POSES += [(_i, tuple(_ang[_i]), _s[_k]) for _k, _i in enumerate(_pl)]
SHARE_MAX = max(p[2] for p in POSES)
F_SUST = SHARE_MAX * W_N                 # sustained: stopped on a tripod (or one foot 2 mm high)
DYN = 2.0                                # walking dynamic factor (part specs, DR05)
F_WALK = DYN * F_SUST
MU = 0.5                                 # foot friction (specs; DR05: 0.3 hard floor, 0.6-0.8 carpet)
SHOVE_N = 3.0
BACKDRIVE = 2.0                          # a powered MG90S is back-driven at ~2 x stall (specs, DR05): assumption
T_BD = BACKDRIVE * STALL

KEY = {"stance": Pose(NEUTRAL)}
for _j, _n in enumerate(("coxa", "femur", "tibia")):
    KEY[f"{_n} min"] = Pose(min(POSES, key=lambda p: p[1][_j])[1])
    KEY[f"{_n} max"] = Pose(max(POSES, key=lambda p: p[1][_j])[1])
_GAIT_POSES = {}
for _i, _a, _s in POSES:
    _GAIT_POSES.setdefault(_a, Pose(_a))


def _dirs(n):
    return [(math.cos(2 * math.pi * d / n), math.sin(2 * math.pi * d / n)) for d in range(n)]


def envelope(pose, up_max, mu, t_cap, up_min=0.0, n_up=13, n_dir=24, n_mag=6):
    """Foot forces (world, N x 3): up from up_min to up_max, horizontal (C axes) up to mu x up in any direction,
    every servo torque within t_cap."""
    ups = np.linspace(up_min, up_max, n_up) if n_up > 1 else np.array([up_max])
    comps = [(0.0, 0.0, u) for u in ups]
    for u in ups:
        for cx, cy in _dirs(n_dir):
            comps += [(mu * u * m / n_mag * cx, mu * u * m / n_mag * cy, u) for m in range(1, n_mag + 1)]
    f = np.array([pose.force(*c) for c in comps])
    ok = np.abs(f @ pose.Gw.T).max(axis=1) <= t_cap * 1.0001
    return f[ok]


def cap_up(pose, t_cap, mu=MU):
    """Largest upward foot force the servos carry within t_cap, with any horizontal friction up to mu x up."""
    best = 0.0
    for cx, cy in _dirs(72):
        for m in np.linspace(0.0, 1.0, 21):
            g = np.abs(pose.Gw @ pose.force(mu * m * cx, mu * m * cy, 1.0)).max()
            best = max(best, t_cap / g)
    return best


def stall_set(pose, f_up, t_cap=STALL):
    """The spec's stall case, one servo at a time: a vertical foot force either way until the first servo stalls;
    a radial or tangential foot force (C axes) either way until the first servo stalls, on top of f_up."""
    out = []
    for d in (pose.force(0, 0, 1), pose.force(0, 0, -1)):
        out.append(d * t_cap / np.abs(pose.Gw @ d).max())
    base = pose.force(0, 0, f_up)
    for d in (pose.force(1, 0, 0), pose.force(-1, 0, 0), pose.force(0, 1, 0), pose.force(0, -1, 0)):
        lo, hi = 0.0, 100.0
        for _ in range(50):
            h = (lo + hi) / 2
            lo, hi = (h, hi) if np.abs(pose.Gw @ (base + h * d)).max() <= t_cap else (lo, h)
        out.append(base + lo * d)
    return np.array(out)


def stall_polytope(pose, t_cap=STALL, n=24):
    """Every 3D foot-force direction scaled until a servo reaches t_cap: any combination of stalled servos."""
    out = []
    for i in range(n):
        th = math.pi * (i + 0.5) / n
        for cx, cy in _dirs(2 * n):
            d = pose.B @ np.array([math.sin(th) * cx, math.sin(th) * cy, math.cos(th)])
            out.append(d * t_cap / max(np.abs(pose.Gw @ d).max(), 1e-9))
    return np.array(out)


CAP = {n: cap_up(p, T_BD) for n, p in KEY.items()}
F_CAP = CAP["stance"]


def cases_at(w_n, drop_dirs=2):
    """Load cases for a robot weight w_n (N): key -> (label, [(Pose, forces N x 3, world)], SF required). The drop
    takes radial friction only (drop_dirs 2: the spec's case, up + inward/outward); drop_dirs 24 = any direction."""
    f_s = SHARE_MAX * w_n
    return {
        "sust": (f"sustained: stopped on a tripod, up to {f_s:.2f} N up",
                 [(_GAIT_POSES[a], np.array([[0.0, 0.0, s * w_n]])) for _, a, s in POSES], SF_CYCLIC),
        "walk": (f"walking x{DYN:.0f}: up to {DYN * f_s:.2f} N up",
                 [(_GAIT_POSES[a], np.array([[0.0, 0.0, DYN * s * w_n]])) for _, a, s in POSES], SF_CYCLIC),
        "scrub": (f"foot friction: {f_s:.2f} N up + mu {MU} any direction, servos within stall",
                  [(p, envelope(p, f_s, MU, STALL, up_min=f_s, n_up=1)) for p in KEY.values()], SF_CYCLIC),
        "shove": (f"shove {SHOVE_N:.0f} N any direction with 0..{f_s:.2f} N up",
                  [(p, np.array([p.force(SHOVE_N * cx, SHOVE_N * cy, u) for cx, cy in _dirs(36)
                                 for u in (0.0, f_s / 2, f_s)])) for p in KEY.values()], SF_STATIC),
        "stall": (f"servo stall, one at a time: 216 N.mm, vertical either way or radial/tangential with {f_s:.2f} N up",
                  [(p, stall_set(p, f_s)) for p in KEY.values()], SF_STATIC),
        "drop": (f"20 cm drop: up to {F_CAP:.1f} N up (back-drive cap {BACKDRIVE:.0f} x stall) + "
                 f"{'radial' if drop_dirs == 2 else 'any-direction'} friction mu {MU}",
                 [(p, envelope(p, CAP[n], MU, T_BD, n_up=25, n_dir=drop_dirs)) for n, p in KEY.items()], SF_STATIC),
    }


CASES = cases_at(W_N)
ADV_CASES = {"stall": ("ADVISORY any combination of stalled servos (beyond the spec)",
                       [(p, stall_polytope(p)) for p in KEY.values()], SF_STATIC),
             "drop": ("ADVISORY drop with friction in any direction (beyond the spec)",
                      cases_at(W_N, drop_dirs=24)["drop"][1], SF_STATIC)}


def worst(case, fn, cases=None):
    """Largest value of fn(pose, forces N x 3) -> array, over every pose and force of a load case."""
    return max(float(np.max(fn(p, f))) for p, f in (CASES if cases is None else cases)[case][1])


# --- checks and report ---------------------------------------------------------------------------------------------
rows, advisory = [], []


def check(name, stress, across, sf_req, shear=False, Kt=1.0, info=False, allow_mpa=None, tag=None):
    s = Kt * abs(stress)
    a = allow(across, shear) if allow_mpa is None else allow_mpa
    sf = a / s if s > 1e-12 else float("inf")
    tag = tag or (("Z" if across else "XY") + (" shear" if shear else ""))
    (advisory if info else rows).append((name, tag, s, a, sf, sf_req))
    return sf


def report(title):
    print(f"\n== {title} ==")
    print("| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |")
    print("|---|---|---|---|---|---|---|---|")
    for i, (n, d, s, a, sf, req) in enumerate(rows, 1):
        print(f"| {i} | {n} | {d} | {s:.2f} | {a:.2f} | {sf:.2f} | {req:.0f} | {'OK' if sf >= req else '**FAIL**'} |")
    if advisory:
        print("\nAdvisory and change-set rows (not in the verdict):")
        print("| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |")
        print("|---|---|---|---|---|---|---|")
        for n, d, s, a, sf, req in advisory:
            print(f"| {n} | {d} | {s:.2f} | {a:.2f} | {sf:.2f} | {req:.0f} | {'OK' if sf >= req else 'below'} |")
    w = min(rows, key=lambda r: r[4] / r[5])
    fails = [r for r in rows if r[4] < r[5]]
    print(f"\nlowest SF {w[4]:.2f} (required {w[5]:.0f}) at: {w[0]}")
    print("VERDICT:", "FAIL" if fails else "NEEDS_TEST (placeholder allowables: a PASS needs measured data)")
    print(f"({time.time() - T0:.0f} s)")
    return w, fails


def print_load_model():
    print(f"robot mass {M_TOTAL:.0f} g ({W_N:.2f} N): printed {M_PRINTED:.0f} g (layer model x {MASS_CAL}; solid "
          f"{sum(QTY[k] * M_PART_SOLID[k] for k in QTY):.0f} g) + bought {M_BOUGHT:.0f} g")
    for k in QTY:
        ps = print_settings(k)
        print(f"   {k}: {QTY[k]} x {M_PART[k]:.1f} g printed ({M_PART_SOLID[k]:.1f} g solid; {ps['perimeters']} "
              f"perimeters, {ps['fill']:.0%} gyroid)")
    for n, m in BOUGHT:
        print(f"   {n}: {m:.1f} g")
    print(f"tripod share (CG within +-{CG_BOX:.0f} mm): max {SHARE_MAX:.3f} over {len(POSES)} planted feet; "
          f"F_sust {F_SUST:.2f} N, F_walk {F_WALK:.2f} N")
    print(f"key poses (coxa, femur, tibia in leg_frames' angles), foot in C, drop cap at T_bd {T_BD:.0f} N.mm:")
    for n, p in KEY.items():
        fc = p.local("C", np.zeros(3))[0]
        print(f"   {n:10s} {tuple(round(a, 1) for a in p.angles)}; foot ({fc[0]:.1f}, {fc[1]:.1f}, {fc[2]:.1f});"
              f" cap {CAP[n]:.1f} N")
    print("forces per case: " + ", ".join(f"{k} {sum(len(f) for _, f in v[1])}" for k, v in CASES.items()))
    print_servo_summary()


def coxa_shaft_moment(pose, f):
    """Bending moment (N.mm) the leg puts on the coxa servo's output shaft: foot force about the coxa axis at the
    horn face, horizontal components (deep review SYS-6)."""
    p, fl = pose.local("C", f)
    m = np.cross(p - np.array([0.0, 0.0, HORN_DEPTH]), fl)
    return np.hypot(m[:, 0], m[:, 1])


def print_servo_summary():
    """Static servo torques and coxa-shaft bending over the gait (compare stance_torques.json and DR05)."""
    tf = tk = cs = 0.0
    for _, a, s in POSES:
        p = _GAIT_POSES[a]
        f = np.array([[0.0, 0.0, s * W_N]])
        t = np.abs(p.torques(f[0]))
        tf, tk = max(tf, t[1]), max(tk, t[2])
        cs = max(cs, float(coxa_shaft_moment(p, f)[0]))
    cd = worst("drop", coxa_shaft_moment)
    print(f"servos at {M_TOTAL:.0f} g, CG box +-{CG_BOX:.0f} mm, static over the 30/40 mm gaits: femur {tf:.0f} N.mm "
          f"({tf / STALL:.0%} of stall), knee {tk:.0f} ({tk / STALL:.0%}); x{DYN:.0f} walking femur {DYN * tf:.0f}, knee "
          f"{DYN * tk:.0f}; coxa-shaft bending {cs:.0f} N.mm static, {DYN * cs:.0f} walking, {cd:.0f} in the drop")
# ==== end of shared block =========================================================================================


# ==== 20261026-hexapod-coxa (frame C = print frame: x radial, y = z x x, z up in print / down in the robot) =====
P = MODEL["coxa"]
F = FIELD["coxa"]
S = SOLID["coxa"]
s = SERVO
ps = print_settings("coxa")
WIN_X, WIN_HALF = P["WIN_X"], P["WIN_HALF"]
WIN_Z0 = H.Z_F - WIN_HALF                                   # 13.6 window floor
YM = H.Y_F - H.T_V / 2                                      # -18.5 plate mid-plane
PIL_X = [H.L_C + px for px in P["PILOT_X"]]                 # 12.6, 41.7 (outboard pilot moved 1.3 mm)
S_SCR = PIL_X[1] - PIL_X[0]
HB = H.Z_F - WIN_Z0                                         # screw line above the post root: 6.4
TAB_HALF = s.width / 2                                      # tab edge to the screw line: 6.1
VX = P["VPLATE_X"]
print_load_model()
print(f"\ncoxa: window x {WIN_X[0]:.2f}..{WIN_X[1]:.2f}, floor z {WIN_Z0:.2f}; posts {WIN_X[0] - VX[0]:.1f} / "
      f"{VX[1] - WIN_X[1]:.1f} x {H.T_V}; pilots x {PIL_X[0]:.2f} / {PIL_X[1]:.2f}; floor under the horn "
      f"{H.T_C - HORN_DEPTH:.0f}; printed {ps['perimeters']} perimeters (band {F.band:.2f} mm), {ps['fill']:.0%} gyroid")


def at_point(pose, f, q):
    """Force and moment (N x 3 each, C axes) of the foot forces f (world) about the point q (C)."""
    p, fl = pose.local("C", f)
    return fl, np.cross(p - np.asarray(q, float), fl)


# --- the femur servo on its two tab screws: posts and pilot row ------------------------------------------------------
def post_props(z, side):
    """Solid and as-printed properties of one post at height z (side 0 inner, 1 outer): area, out-of-plane modulus
    (bending about C x: stress across the 10 mm thickness), in-plane modulus (about C y: across the post width)."""
    x_rng = (VX[0] - 9, WIN_X[0] + 0.05) if side == 0 else (WIN_X[1] - 0.05, VX[1] + 1)
    out = []
    for p_ in section(F, (0, 0, z), (1, 0, 0), (0, 1, 0), x_rng, (-25, -12), du=0.05, dv=0.05):
        out.append(dict(A=p_["A"], Zoop=p_["Itt"] / p_["ct"], Zip=p_["Iss"] / p_["cs"], w=p_["s_hi"] - p_["s_lo"]))
    return out


Z_ROOT = WIN_Z0 + 0.1
POST = {side: post_props(Z_ROOT, side) for side in (0, 1)}
POST_PIL = {side: post_props(H.Z_F, side) for side in (0, 1)}
_ex = exact_section(S, (0, 0, Z_ROOT), (0, 0, 1), (1, 0, 0))
print(f"post roots z {Z_ROOT:.1f}: area exact {_ex[0]:.1f} mm2, raster {POST[0][0]['A'] + POST[1][0]['A']:.1f}; "
      f"inner {POST[0][0]['w']:.2f} wide (the ramp), outer {POST[1][0]['w']:.2f}; as printed / solid: out-of-plane "
      f"modulus {POST[0][1]['Zoop'] / POST[0][0]['Zoop']:.3f}, in-plane {POST[0][1]['Zip'] / POST[0][0]['Zip']:.3f}")
print(f"pilot row z {H.Z_F:.0f}: inner A {POST_PIL[0][0]['A']:.1f} mm2, outer A {POST_PIL[1][0]['A']:.1f} mm2 (pilots, "
      f"lead notch)")


def servo_loads(pose, f):
    fl, m = at_point(pose, f, ((PIL_X[0] + PIL_X[1]) / 2, YM, H.Z_F))
    return fl.T, m.T


def posts(pose, f, props=POST, Kt=2.0, pilot=False):
    """Post stresses (MPa, across the layers): the femur servo is a rigid body on its two tab screws (predecessor's
    model, round-3 numbers). Its rocking moment about the screw line (taken at the root) splits between the posts
    by width; its yaw acts as opposite y-forces at the screws, HB above the root; the radial force bends each post
    in-plane; the in-plane moment and any pull along +z load them axially. The pilot row takes the rocking moment
    only when the tab pivots on its far edge (Mx > 0). Returns [solid, as printed], worst post."""
    (Fx, Fy, Fz), (Mx, My, Mz) = servo_loads(pose, f)
    f_yaw = np.abs(Mz) / S_SCR
    n_ax = np.abs(My) / S_SCR + np.maximum(Fz, 0.0) / 2
    w0, w1 = props[0][0]["w"], props[1][0]["w"]
    res = []
    for k in (0, 1):
        out = np.zeros(len(Fx))
        for side, w in ((0, w0), (1, w1)):
            pr, share = props[side][k], w / (w0 + w1)
            if pilot:
                m_oop = share * np.maximum(Mx, 0.0) + f_yaw * TAB_HALF / 2
                m_ip = np.abs(Fx) / 4 * HB
            else:
                m_oop = share * np.abs(Mx - HB * Fy) + f_yaw * HB
                m_ip = np.abs(Fx) / 2 * HB
            out = np.maximum(out, Kt * (m_oop / pr["Zoop"] + m_ip / pr["Zip"] + n_ax / pr["A"]))
        res.append(out)
    return res


def screw_tension(pose, f):
    (Fx, Fy, Fz), (Mx, My, Mz) = servo_loads(pose, f)
    return np.abs(Mx) / (2 * TAB_HALF) + np.abs(Mz) / S_SCR + np.maximum(Fy, 0.0) / 2


def pilot_force(pose, f):
    (Fx, Fy, Fz), (Mx, My, Mz) = servo_loads(pose, f)
    return np.hypot(np.abs(Fx) / 2, np.abs(My) / S_SCR + np.abs(Fz) / 2), np.abs(Fx)


# --- horn clamp: the O10 penny washer pulled through the floor, the joint tipping on the horn hub's edge -------------
R_W = 5.0                                     # O10 x 1 penny washer (spec section 2)
R_HUB = s.horn_d / 2                          # 3.6: the clamped joint tips on the horn hub's edge (predecessor)
CLAMP_D = s.horn_screw_clear_d + P["HOLE_COMP"]
A_WASHER = math.pi / 4 * ((2 * R_W) ** 2 - CLAMP_D ** 2)


def plug_area(field, r, z0, z1, n_th=720):
    """Shear area of the cylinder r round the coxa axis, z0..z1: (solid, as printed with the core at rho^1.5)."""
    th = np.linspace(0, 2 * np.pi, n_th, endpoint=False)
    TH, ZZ = np.meshgrid(th, np.arange(z0 + LAYER / 2, z1, LAYER), indexing="ij")
    x, y, z = r * np.cos(TH.ravel()), r * np.sin(TH.ravel()), ZZ.ravel()
    dA = r * (2 * np.pi / n_th) * LAYER
    return (field.cls_at(x, y, z) > 0).sum() * dA, field.weights(x, y, z, kind="strength").sum() * dA


A_PLUG_SOLID, A_PLUG = plug_area(F, R_W, 0.0, H.T_C)
P_CAP = {"solid": allow(True, True) * A_PLUG_SOLID, "printed": allow(True, True) * A_PLUG}
# under the washer: the clamp hole's perimeter ring (solid) inside, the top skin over the infill core outside
_rr = np.linspace(CLAMP_D / 2, R_W, 200)
_cls = F.cls_at(_rr, np.zeros_like(_rr), np.full_like(_rr, H.T_C - 2.5))
R_RING = float(_rr[_cls == 3].min()) if (_cls == 3).any() else R_W
A_RING = math.pi * (R_RING ** 2 - (CLAMP_D / 2) ** 2)
A_OVER_CORE = A_WASHER - A_RING
T_SKIN = ps["top"] * LAYER
print(f"horn clamp: plug cylinder r {R_W} through z 0..{H.T_C:.0f}: solid {A_PLUG_SOLID:.0f} mm2, as printed "
      f"{A_PLUG:.0f} mm2 equivalent -> pull-through {P_CAP['solid']:.0f} / {P_CAP['printed']:.0f} N, moment on the "
      f"r {R_HUB} pivot {P_CAP['solid'] * R_HUB:.0f} / {P_CAP['printed'] * R_HUB:.0f} N.mm; under the washer: "
      f"solid ring to r {R_RING:.2f} ({A_RING:.0f} mm2), skin over infill {A_OVER_CORE:.0f} mm2")


def clamp_demand(pose, f):
    """Clamp-screw force (N): horizontal moment at the horn face over the hub-edge pivot, plus any pull-off."""
    fl, m = at_point(pose, f, (0.0, 0.0, HORN_DEPTH))
    return np.hypot(m[:, 0], m[:, 1]) / R_HUB + np.maximum(fl[:, 2], 0.0)


def washer_pressure_core(P_n, fill):
    """Pressure on the infill core under the washer: a rigid washer on the solid ring (stiffness E / t_floor) and
    the skin-over-core region (skin and core in series), sharing by stiffness."""
    t_f = H.T_C - HORN_DEPTH
    k_ring = 1.0 / t_f
    k_core = 1.0 / (T_SKIN + (t_f - T_SKIN) / core_stiff(fill))
    p_core = P_n / (A_RING * k_ring / k_core + A_OVER_CORE)
    return p_core, p_core * k_ring / k_core


# --- hub + plate section outboard of the horn (x = const) and the band under the window (z = const) ----------------
def lsec_stress(pose, f, x, props):
    fl, m = at_point(pose, f, (x, props["sc"], props["tc"]))
    return bend_stress(props, fl[:, 0], m[:, 1], m[:, 2])          # s = C y, t = C z, n = +x


X_HUB = 6.0
HUB = section(F, (X_HUB, 0, 0), (0, 1, 0), (0, 0, 1), (-26, 10), (0, 42))
Z_BAND = WIN_Z0 - 0.6
BAND = section(F, (0, 0, Z_BAND), (1, 0, 0), (0, 1, 0), (-12, 56), (-26, -6), du=0.1, dv=0.1)


def band_stress(pose, f, props):
    fl, m = at_point(pose, f, (props["sc"], props["tc"], Z_BAND))
    return bend_stress(props, fl[:, 2], m[:, 0], m[:, 1])          # s = x, t = y, n = +z


def horn_bearing_mpa(torque=STALL):
    return torque / (s.horn_arm_len + s.horn_tip_d / 2 - 2.5) / (5.0 * HORN_DEPTH)


L_TAB = min(H.T_V, 10.0 - s.tab_t)            # M2 x 10 through the 2.5 mm tab: 7.5 mm engaged
LIG_OUT = PIL_X[1] - (s.screw_pilot_d + P["HOLE_COMP"]) / 2 - (H.L_C + s.shaft_from_end + s.lead_notch_reach
                                                                + P["HOLE_COMP"] / 2)
PRELOAD_SNUG, PRELOAD_FIRM = 125.0, 250.0     # M2 clamp screw at 0.05 / 0.1 N.m (F = T / (0.2 d)), assumption


def coxa_rows(tag, k, P_cap, fill, cases, info, prefix=""):
    """Every row for one print configuration: k 0 solid / 1 as printed, P_cap the clamp pull-through (N)."""
    for key, (lab, sets, req) in cases.items():
        u = worst(key, lambda p, f: clamp_demand(p, f) / P_cap, cases)
        check(f"{prefix}{lab}: horn clamp, O10 washer pulled through the floor ({tag})", allow(True, True) * u, True,
              req, shear=True, info=info)
    dem = max(worst("drop", clamp_demand, cases), PRELOAD_SNUG)
    p_core, p_ring = washer_pressure_core(dem, fill)
    if fill < 0.999:
        check(f"{prefix}drop: O10 washer ({dem:.0f} N) on the floor's skin over the {fill:.0%} infill core ({tag})",
              p_core, False, SF_STATIC, allow_mpa=ALLOW_XY * core_strength(fill), tag="crush", info=info)
        check(f"{prefix}drop: O10 washer ({dem:.0f} N) on the clamp hole's perimeter ring ({tag})", p_ring, False,
              SF_STATIC, tag="bearing", info=info)
    else:
        check(f"{prefix}drop: O10 washer bearing ({dem:.0f} N over {A_WASHER:.0f} mm2; {tag})", dem / A_WASHER, False,
              SF_STATIC, tag="bearing", info=info)
    for key, (lab, sets, req) in cases.items():
        check(f"{prefix}{lab}: post roots z {Z_ROOT:.1f} (R1 reliefs, Kt 2.0; {tag})",
              worst(key, lambda p, f: posts(p, f)[k], cases), True, req, info=info)
    for key in ("shove", "stall", "drop"):
        lab, sets, req = cases[key]
        check(f"{prefix}{lab}: post net section at the pilot row z {H.Z_F:.0f} (Kt 2; {tag})",
              worst(key, lambda p, f: posts(p, f, props=POST_PIL, pilot=True)[k], cases), True, req, info=info)
    for key in ("sust", "walk", "scrub", "shove", "stall", "drop"):
        lab, sets, req = cases[key]
        check(f"{prefix}{lab}: femur-servo tab screw pull-out (M2x10, {L_TAB:.1f} mm in the pilot's perimeters)",
              worst(key, lambda p, f: screw_tension(p, f) / (math.pi * s.screw_pilot_d * L_TAB), cases), True, req,
              shear=True, info=info)
    check(f"{prefix}drop: tab pilot bearing (radial force, in-plane moment, vertical load)",
          worst("drop", lambda p, f: pilot_force(p, f)[0] / (s.screw_pilot_d * H.T_V), cases), False, SF_STATIC,
          info=info)
    check(f"{prefix}drop: outboard pilot to lead-notch ligament {LIG_OUT:.2f} CAD, whole radial force on one screw",
          worst("drop", lambda p, f: pilot_force(p, f)[1] / (2 * LIG_OUT * H.T_V), cases), True, SF_STATIC,
          shear=True, info=info)
    for key in ("walk", "shove", "drop"):
        lab, sets, req = cases[key]
        check(f"{prefix}{lab}: band under the window z {Z_BAND:.1f}, through the reliefs (Kt 2; {tag})",
              worst(key, lambda p, f: band_stress(p, f, BAND[k]), cases), True, req, Kt=2.0, info=info)
    for key in ("walk", "drop"):
        lab, sets, req = cases[key]
        check(f"{prefix}{lab}: hub + plate section x {X_HUB:.0f}, outboard of the horn pivot (Kt 1.5; {tag})",
              worst(key, lambda p, f: lsec_stress(p, f, X_HUB, HUB[k]), cases), False, req, Kt=1.5, info=info)
    check(f"{prefix}assembly: horn clamp screw snug 0.05 N.m ({PRELOAD_SNUG:.0f} N): washer pull-through ({tag})",
          allow(True, True) * PRELOAD_SNUG / P_cap, True, SF_STATIC, shear=True, info=info)


# ================================ verdict rows: the design as specified, as printed =================================
check("coxa stall 216 N.mm: horn-arm bearing on the pocket wall (perimeters)", horn_bearing_mpa(), False, SF_STATIC)
coxa_rows(f"as printed, {ps['fill']:.0%}", 1, P_CAP["printed"], ps["fill"], CASES, False)

# ================================ advisory: beyond the spec, and the solid-section comparison =======================
for key, (lab, sets, req) in ADV_CASES.items():
    adv = {key: ADV_CASES[key]}
    check(f"{lab}: horn clamp (as printed)", allow(True, True) * worst(key, lambda p, f: clamp_demand(p, f) /
                                                                         P_CAP["printed"], adv), True, req, shear=True,
          info=True)
    check(f"{lab}: post roots (as printed)", worst(key, lambda p, f: posts(p, f)[1], adv), True, req, info=True)
    check(f"{lab}: pilot row (as printed)", worst(key, lambda p, f: posts(p, f, props=POST_PIL, pilot=True)[1], adv),
          True, req, info=True)
    check(f"{lab}: tab screw pull-out", worst(key, lambda p, f: screw_tension(p, f) / (math.pi * s.screw_pilot_d *
                                                                                       L_TAB), adv), True, req,
          shear=True, info=True)
check("SOLID SECTIONS (the predecessor's basis) drop: horn clamp", allow(True, True) * worst(
    "drop", lambda p, f: clamp_demand(p, f) / P_CAP["solid"]), True, SF_STATIC, shear=True, info=True)
check(f"assembly: horn clamp screw 'firm' 0.1 N.m ({PRELOAD_FIRM:.0f} N): washer pull-through (as printed)",
      allow(True, True) * PRELOAD_FIRM / P_CAP["printed"], True, SF_STATIC, shear=True, info=True)

# ================================ change set: print the coxa at 100 % infill =========================================
CASES_FIX = cases_at(W_ALL_FIX)
print(f"\nchange set: coxa fill_density 50 -> 100 %: {M_COXA_FIX:.1f} g each; robot with every round-3 change "
      f"{W_ALL_FIX / G:.0f} g")
coxa_rows("100 % infill", 0, P_CAP["solid"], 1.0, CASES_FIX, True, prefix="FIX ")
for key, (lab, sets, req) in ADV_CASES.items():
    adv = {key: ADV_CASES[key]}
    check(f"FIX {lab}: pilot row (100 %)", worst(key, lambda p, f: posts(p, f, props=POST_PIL, pilot=True)[0], adv),
          True, req, info=True)
    check(f"FIX {lab}: post roots (100 %)", worst(key, lambda p, f: posts(p, f)[0], adv), True, req, info=True)
    check(f"FIX {lab}: horn clamp (100 %)", allow(True, True) * worst(key, lambda p, f: clamp_demand(p, f) /
                                                                        P_CAP["solid"], adv), True, req, shear=True,
          info=True)

# ================================ proof-test equivalence ============================================================
class HornLoad:
    """A load already in C, applied at a point of the bracket's leg (for the proof-test equivalence)."""

    def __init__(self, point):
        self.point = np.asarray(point, float)

    def local(self, key, f):
        return self.point, np.atleast_2d(np.asarray(f, float))


F_TEST = 2 * DYN * SHARE_MAX * W_ALL_FIX            # 2 x the walking foot load (proof load, skill: 1.5-2 x service)
_st = KEY["stance"]
_foot = np.array([[0.0, 0.0, F_TEST]])
HORN_PT = (H.L_C, H.Y_F + (s.total_h - s.tab_height) + 0.6 - s.horn_t / 2, H.Z_F)       # mid-horn: C (32, 0.3, 20)
_unit = np.array([[0.0, 0.0, -1.0]])                 # 1 N along -C z: the ground's direction with the leg inverted
_h = HornLoad(HORN_PT)
need = {"post roots": posts(_st, _foot)[0][0] / posts(_h, _unit)[0][0],
        "tab screws": screw_tension(_st, _foot)[0] / screw_tension(_h, _unit)[0],
        "horn clamp": clamp_demand(_st, _foot)[0] / clamp_demand(_h, _unit)[0]}
P_HANG = max(need.values())
print(f"\nproof load: 2 x walking at the stance foot = {F_TEST:.1f} N ({F_TEST / 9.81:.2f} kg). Hung from the femur-servo "
      f"horn at C {tuple(round(v, 1) for v in HORN_PT)} instead (femur off, coxa servo clamped shaft-up), the same "
      f"post, tab-screw and clamp loads need: " + ", ".join(f"{k} {v:.1f} N" for k, v in need.items())
      + f" -> hang {P_HANG / 9.81:.2f} kg")
check(f"PROOF hang {P_HANG / 9.81:.1f} kg on the femur-servo horn (100 % infill): post roots", posts(_h, P_HANG * _unit)[0][0],
      True, 1.0, info=True)
check(f"PROOF hang {P_HANG / 9.81:.1f} kg on the femur-servo horn (100 % infill): horn clamp",
      allow(True, True) * clamp_demand(_h, P_HANG * _unit)[0] / P_CAP["solid"], True, 1.0, shear=True, info=True)

report(JOB["coxa"])

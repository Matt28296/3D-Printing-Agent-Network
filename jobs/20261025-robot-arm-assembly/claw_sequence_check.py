"""Claw assembly-sequence and running-fit check with exact solids (deep review 03 SYS-01, SYS-08).

The claw goes together in this order (BUILD_GUIDE §4) and comes apart in the reverse order:

  1. claw MG90S into the frame from the FRONT, case bottom first, its lead through the window's notch
     (then its two tab screws);
  2. cover lowered onto the frame (then 2 x M2.5 front, 2 x M3 top);
  3. camera mount lowered onto the cover (optional; the M3 top screws then go through both);
  4. jaw A slid in along +y from the open (-y) end of slot A, to fully open (gap 44);
  5. jaw B slid in along -y from the open (+y) end of slot B, to fully open;
  6. pinion, with its trimmed horn in its back pocket, pushed axially (-x) through the cover's
     pass-through onto the spline, with the servo at the 44 mm angle (firmware `g 44`).

Checks, in the claw frame G with the model.py solids (build123d / OCC booleans):
  - every insertion path, in steps: the moving part against everything already fitted;
  - the pinion's path as ONE exact swept solid: a gear is a prism along its axis, so its outline
    extruded along the path is exactly the space it passes through (plus its own back slice);
  - the running stroke 0..44 mm every 1 mm (every pair with a moving part), plus one tooth pitch
    of travel in 0.1 mm steps (pinion against both racks);
  - each mesh's backlash, measured: the pinion turned each way until it touches the rack, the
    jaw held still.
An overlap over STRICT_TOL (0.001 mm³) is a clash, except on the declared contact planes in
CONTACTS (faces that rest or slide on each other by design: the rack backs on their guides, the
servo tabs on the bulkhead, the cover on the frame): an overlap there must lie within
CONTACT_BAND of the plane.

Run from the project root (writes claw_sequence_check.json; assembly_check.py calls run() too):
    .venv/bin/python jobs/20261025-robot-arm-assembly/claw_sequence_check.py
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE))
from build123d import Align, Box, BuildPart, BuildSketch, Cylinder, Plane, Polygon, Pos, Rot, extrude  # noqa: E402
from build123d.topology import Shape  # noqa: E402
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform  # noqa: E402
from OCP.gp import gp_Trsf  # noqa: E402

import claw_frame as C  # noqa: E402
from gears import gear_outline  # noqa: E402
from hobby_parts import HORN_DEPTH, servo_dummy  # noqa: E402

STRICT_TOL = 0.001          # mm³
CONTACT_BAND = 1e-3         # mm
GAP_OPEN = 2 * C.STROKE     # 44
PATH_STEP = 0.5             # mm, servo and jaw paths
COVER_STEP = 1.0            # mm, cover and camera-mount descent
FINE_STEP = 0.1             # mm of gap, one tooth pitch of jaw travel
BACKLASH_TOL = 1e-7         # mm³: "touching" for the backlash bisection
PINION_TRAVEL = 70.0        # the pinion starts in front of the fingertips (X_TIP - X_P0 = 60.8)
JAW_TRAVEL = 45.0           # each jaw starts wholly outside the claw (|y| > HALF_Y)
SERVO_TRAVEL = 20.0         # the servo starts wholly in front of the bulkhead
COVER_LIFT = 56.0           # the cover starts wholly above the frame
M25_HEAD = (5.0, 1.75)      # front screws: M2.5 pan head (ISO 7045 dk 5.0, k 1.75)
JOBS = {"claw_frame": "20261026-arm-claw-frame", "claw_cover": "20261026-arm-claw-cover",
        "claw_pinion": "20261026-arm-claw-pinion", "claw_jaw": "20261026-arm-claw-jaw",
        "camera_mount": "20261026-arm-camera-mount"}

# declared contact planes (G frame): unordered pair -> [(axis, value, what)]
CONTACTS = {
    frozenset({"servo", "claw_frame"}): [("x", C.X_B, "servo tabs on the bulkhead's front face")],
    frozenset({"claw_cover", "claw_frame"}): [("x", C.X_F0, "front plate on the wrist plate's front edge"),
                                              ("z", C.Z_TOP0, "top wall on the bulkhead top"),
                                              ("x", C.X_B, "lip against the bulkhead's front face")],
    frozenset({"camera_mount", "claw_cover"}): [("z", C.Z_TOP1, "mount pad on the top wall")],
    frozenset({"front_screws", "claw_cover"}): [("x", C.X_F1, "screw heads on the front plate")],
    frozenset({"jaw_a", "claw_cover"}): [("z", C.Z_TOP0, "rack A's back (and neck top) under the top wall")],
    frozenset({"jaw_b", "claw_frame"}): [("z", C.T_W, "rack B's back on the wrist plate")],
    frozenset({"jaw_a", "jaw_b"}): [("y", 0.0, "fingers closed (gap 0 only)")],
}
AXIS = {"x": 0, "y": 1, "z": 2}


# --- transforms --------------------------------------------------------------------------
def T(x=0.0, y=0.0, z=0.0):
    m = np.eye(4); m[:3, 3] = (x, y, z); return m


def Rx(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    m = np.eye(4); m[1:3, 1:3] = [[c, -s], [s, c]]; return m


def Rz(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    m = np.eye(4); m[:2, :2] = [[c, -s], [s, c]]; return m


def frame(origin, x_dir, z_dir):
    x = np.array(x_dir, float); x /= np.linalg.norm(x)
    z = np.array(z_dir, float); z /= np.linalg.norm(z)
    m = np.eye(4); m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = x, np.cross(z, x), z, origin
    return m


def place_shape(shape, m):
    tr = gp_Trsf()
    tr.SetValues(*[float(m[i, j]) for i in range(3) for j in range(4)])
    return Shape.cast(BRepBuilderAPI_Transform(shape.wrapped, tr, True).Shape())


SERVO_IN_G = frame((C.X_B, 0, C.ZS), (0, 1, 0), (1, 0, 0))     # as frame model.py's SERVO_LOC
PINION_IN_G = frame((C.X_P0, 0, C.ZS), (0, 0, 1), (1, 0, 0))   # pinion +Z along claw +x, +X along claw +z
TURN_B = T(0, 0, C.ZS) @ Rx(180) @ T(0, 0, -C.ZS)             # jaw B = jaw A turned about the pinion axis


def pinion_deg(gap):
    return math.degrees(gap / 2.0 / C.R_P)


def jaw_a_at(gap):
    return T(0, -gap / 2.0, 0)


def jaw_b_at(gap):
    return TURN_B @ T(0, -gap / 2.0, 0)


# --- parts -------------------------------------------------------------------------------
def load_model(job):
    spec = importlib.util.spec_from_file_location(f"cs_{job.replace('-', '_')}", ROOT / "jobs" / job / "model.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def servo_with_lead():
    """Claw MG90S (servo frame) plus its lead: a lead_w x lead_t ribbon leaving the case end nearest the
    shaft (+x) lead_z above the case bottom and lying along that end face past the case bottom, the way
    it trails when the servo goes in case bottom first."""
    s = C.SERVO
    x1 = s.shaft_from_end
    z_exit = -s.tab_height + s.lead_z + s.lead_t / 2
    lead = Pos(x1, -s.lead_w / 2, -s.tab_height - 30.0) * Box(s.lead_t, s.lead_w, z_exit + s.tab_height + 30.0,
                                                               align=(Align.MIN,) * 3)
    return servo_dummy(s, with_horn=False) + lead


def front_screw_heads():
    d, k = M25_HEAD
    heads = None
    for (y, z) in C.FRONT_SCREWS:
        h = Pos(C.X_F1, y, z) * Rot(0, 90, 0) * Cylinder(d / 2, k, align=(Align.CENTER, Align.CENTER, Align.MIN))
        heads = h if heads is None else heads + h
    return heads


def pinion_swept(pinion):
    """Exact space the pinion passes through on its way in, in the PINION frame: the pinion itself
    (its back slice, horn pocket open) plus its outline swept from the pocket floor to PINION_TRAVEL
    beyond its front face. The pocket and the clamp hole are inside the outline, so the sweep is a
    superset only inside the Ø2.6 hole (nothing reaches in there)."""
    pts = gear_outline(C.M, C.Z_TEETH, backlash=C.PINION_BACKLASH, phase_deg=0.0, root_fillet=C.PINION_ROOT_FILLET,
                       tip_relief=C.TIP_RELIEF)
    with BuildPart() as bp:
        with BuildSketch(Plane.XY.offset(HORN_DEPTH)):
            Polygon(*pts, align=None)
        extrude(amount=C.FACE_W - HORN_DEPTH + PINION_TRAVEL)
    return pinion + bp.part


# --- overlaps ----------------------------------------------------------------------------
def _bb(shape):
    b = shape.bounding_box()
    return np.array([b.min.X, b.min.Y, b.min.Z]), np.array([b.max.X, b.max.Y, b.max.Z])


def _bb_hit(a, b, pad=0.01):
    return bool(np.all(a[0] <= b[1] + pad) and np.all(b[0] <= a[1] + pad))


def overlap(ka, sa, kb, sb, bba=None, bbb=None, gap=None):
    """(volume counted as a clash, volume on declared contact planes) of two placed solids."""
    bba = _bb(sa) if bba is None else bba
    bbb = _bb(sb) if bbb is None else bbb
    if not _bb_hit(bba, bbb):
        return 0.0, 0.0
    inter = sa & sb
    if inter is None:
        return 0.0, 0.0
    planes = CONTACTS.get(frozenset({ka, kb}), [])
    if frozenset({ka, kb}) == frozenset({"jaw_a", "jaw_b"}) and gap not in (0, 0.0):
        planes = []
    bad = touch = 0.0
    for s in inter.solids():
        v = s.volume
        lo, hi = _bb(s)
        on_plane = any(hi[AXIS[a]] - lo[AXIS[a]] <= CONTACT_BAND and abs((lo[AXIS[a]] + hi[AXIS[a]]) / 2 - val)
                       <= CONTACT_BAND for a, val, _ in planes)
        if on_plane:
            touch += v
        else:
            bad += v
    return bad, touch


def sweep_path(label, key, shape, placements, fixed, gap=None):
    """Move `shape` through `placements` [(t, 4x4)] against the placed `fixed` {key: shape}."""
    fb = {k: _bb(s) for k, s in fixed.items()}
    worst, clashes, touches = {}, [], {}
    for t, m in placements:
        s = place_shape(shape, m)
        sb = _bb(s)
        for k, o in fixed.items():
            bad, touch = overlap(key, s, k, o, sb, fb[k], gap=gap)
            worst[k] = max(worst.get(k, 0.0), bad)
            touches[k] = max(touches.get(k, 0.0), touch)
            if bad > STRICT_TOL:
                clashes.append([round(t, 2), k, round(bad, 5)])
    return {"path": label, "positions": len(placements), "step_mm": round(placements[1][0] - placements[0][0], 3)
            if len(placements) > 1 else None,
            "worst_clash_mm3": {k: round(v, 6) for k, v in worst.items()},
            "contact_mm3": {k: round(v, 6) for k, v in touches.items() if v > 0},
            "clashes": clashes[:20], "clash_count": len(clashes)}


def _steps(t0, t1, step):
    n = int(round(abs(t1 - t0) / step))
    return [t0 + (t1 - t0) * i / n for i in range(n + 1)]


# --- the check ---------------------------------------------------------------------------
def run(solids=None, log=print):
    t_start = time.time()
    if solids is None:
        solids = {k: load_model(j).design() for k, j in JOBS.items()}
    elif "camera_mount" not in solids:
        solids = dict(solids, camera_mount=load_model(JOBS["camera_mount"]).design())
    frame_s, cover_s, pinion_s, jaw_s, mount_s = (solids[k] for k in ("claw_frame", "claw_cover", "claw_pinion",
                                                                     "claw_jaw", "camera_mount"))
    servo_s = place_shape(servo_with_lead(), SERVO_IN_G)
    screws_s = front_screw_heads()
    rep = {"strict_tol_mm3": STRICT_TOL, "contact_band_mm": CONTACT_BAND,
           "declared_contacts": [{"pair": sorted(k), "plane": f"{a} = {v:g}", "what": w}
                                 for k, lst in CONTACTS.items() for a, v, w in lst],
           "order": ["claw servo from the front (-x), case bottom first, lead through the window notch",
                     "cover lowered (-z) onto the frame; 2 x M2.5 front, 2 x M3 top",
                     "camera mount lowered onto the cover (optional)",
                     "jaw A slid in along +y from slot A's open end to fully open (44 mm)",
                     "jaw B slid in along -y from slot B's open end to fully open",
                     "pinion + trimmed horn pushed axially (-x) through the pass-through onto the spline at g 44"],
           "service": "the reverse: pinion out first (claw at g 44), then jaw B, jaw A, camera mount, cover, servo; "
                      "each part leaves along the path it came in by, so the same sweeps cover it",
           "paths": {}}

    def note(name, r):
        rep["paths"][name] = r
        log(f"  {name:42s} {r['positions']:4d} positions  clashes {r['clash_count']}  worst "
            f"{max(r['worst_clash_mm3'].values(), default=0.0):.5f} mm3", flush=True)

    # 1. servo from the front
    note("1 servo in from the front", sweep_path(
        "servo + lead, +SERVO_TRAVEL -> seated along -x", "servo", servo_with_lead(),
        [(t, T(t, 0, 0) @ SERVO_IN_G) for t in _steps(SERVO_TRAVEL, 0.0, PATH_STEP)], {"claw_frame": frame_s}))
    # 2. cover lowered
    note("2 cover lowered onto the frame", sweep_path(
        "cover, +COVER_LIFT -> seated along -z", "claw_cover", cover_s,
        [(t, T(0, 0, t)) for t in _steps(COVER_LIFT, 0.0, COVER_STEP)], {"claw_frame": frame_s, "servo": servo_s}))
    # 3. camera mount lowered
    note("3 camera mount lowered onto the cover", sweep_path(
        "camera mount, +10 -> seated along -z", "camera_mount", mount_s,
        [(t, T(0, 0, t)) for t in _steps(10.0, 0.0, COVER_STEP)],
        {"claw_frame": frame_s, "servo": servo_s, "claw_cover": cover_s}))
    fixed = {"claw_frame": frame_s, "servo": servo_s, "claw_cover": cover_s, "camera_mount": mount_s,
             "front_screws": screws_s}
    # 4. jaw A from -y, 5. jaw B from +y, both to fully open
    note("4 jaw A slid in to fully open", sweep_path(
        "jaw A, y -JAW_TRAVEL -> fully open along +y", "jaw_a", jaw_s,
        [(t, T(0, -t, 0) @ jaw_a_at(GAP_OPEN)) for t in _steps(JAW_TRAVEL, 0.0, PATH_STEP)], fixed))
    jaw_a_open = place_shape(jaw_s, jaw_a_at(GAP_OPEN))
    note("5 jaw B slid in to fully open", sweep_path(
        "jaw B, y +JAW_TRAVEL -> fully open along -y", "jaw_b", jaw_s,
        [(t, T(0, t, 0) @ jaw_b_at(GAP_OPEN)) for t in _steps(JAW_TRAVEL, 0.0, PATH_STEP)],
        dict(fixed, jaw_a=jaw_a_open)))
    jaw_b_open = place_shape(jaw_s, jaw_b_at(GAP_OPEN))
    # 6. pinion pushed in axially: one exact swept solid
    swept = place_shape(pinion_swept(pinion_s), PINION_IN_G @ Rz(pinion_deg(GAP_OPEN)))
    sw_bb = _bb(swept)
    pin = {}
    for k, o in dict(fixed, jaw_a=jaw_a_open, jaw_b=jaw_b_open).items():
        bad, touch = overlap("pinion", swept, k, o, sw_bb)
        pin[k] = round(bad, 6)
    r_pass = (C.ACCESS_D + 0.2) / 2
    rep["paths"]["6 pinion pushed in axially at 44 mm open"] = {
        "path": f"pinion outline swept from {PINION_TRAVEL:g} mm in front of its seat (beyond the fingertips) to "
                "seated, at the 44 mm angle; one exact solid",
        "overlap_mm3": pin, "clash_count": sum(1 for v in pin.values() if v > STRICT_TOL),
        "pass_through_radial_clearance_mm": {"cad": round(r_pass - C.R_TIP, 3),
                                             "printed": round(C.ACCESS_D / 2 - C.R_TIP, 3)}}
    log(f"  {'6 pinion pushed in axially (swept solid)':42s} overlaps {pin}", flush=True)
    # smallest opening at which the pinion can still come out (service)
    out_gap = None
    for g in range(0, 45, 2):
        a, b = place_shape(jaw_s, jaw_a_at(g)), place_shape(jaw_s, jaw_b_at(g))
        sw = place_shape(pinion_swept(pinion_s), PINION_IN_G @ Rz(pinion_deg(g)))
        if all(overlap("pinion", sw, k, o)[0] <= STRICT_TOL for k, o in (("jaw_a", a), ("jaw_b", b))):
            out_gap = g
            break
    rep["pinion_removable_from_gap_mm"] = out_gap
    log(f"  pinion can come out axially once the claw is open >= {out_gap} mm", flush=True)

    # running stroke: every 1 mm, every pair with a moving part
    worst, clashes, touches = {}, [], {}
    for gap in range(0, 45):
        P = {"claw_pinion": place_shape(pinion_s, PINION_IN_G @ Rz(pinion_deg(gap))),
             "jaw_a": place_shape(jaw_s, jaw_a_at(gap)), "jaw_b": place_shape(jaw_s, jaw_b_at(gap))}
        allp = dict(fixed, **P)
        bbs = {k: _bb(s) for k, s in allp.items()}
        keys = list(allp)
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                if a not in P and b not in P:
                    continue
                bad, touch = overlap(a, allp[a], b, allp[b], bbs[a], bbs[b], gap=gap)
                pk = f"{a} / {b}"
                worst[pk] = max(worst.get(pk, 0.0), bad)
                if touch > 0:
                    touches[pk] = max(touches.get(pk, 0.0), touch)
                if bad > STRICT_TOL:
                    clashes.append([gap, a, b, round(bad, 5)])
    rep["stroke"] = {"gaps_mm": [0, 44, 1], "worst_clash_mm3": {k: round(v, 6) for k, v in worst.items()},
                     "contact_mm3": {k: round(v, 6) for k, v in touches.items()},
                     "clashes": clashes[:40], "clash_count": len(clashes)}
    log(f"  {'running stroke 0..44 every 1 mm':42s} clashes {len(clashes)}  worst "
        f"{max(worst.values(), default=0.0):.6f} mm3", flush=True)
    # one tooth pitch of travel in fine steps: pinion against both racks
    g0 = 20.0
    fine_worst, fine_clashes = {"jaw_a": 0.0, "jaw_b": 0.0}, []
    n = int(round(2 * C.P_CIRC / FINE_STEP))
    for i in range(n + 1):
        g = g0 + 2 * C.P_CIRC * i / n
        p = place_shape(pinion_s, PINION_IN_G @ Rz(pinion_deg(g)))
        for k, m in (("jaw_a", jaw_a_at(g)), ("jaw_b", jaw_b_at(g))):
            bad, _ = overlap("claw_pinion", p, k, place_shape(jaw_s, m))
            fine_worst[k] = max(fine_worst[k], bad)
            if bad > STRICT_TOL:
                fine_clashes.append([round(g, 3), k, round(bad, 6)])
    rep["mesh_fine"] = {"gaps_mm": [g0, round(g0 + 2 * C.P_CIRC, 3), FINE_STEP], "positions": n + 1,
                        "worst_mm3": {k: round(v, 7) for k, v in fine_worst.items()},
                        "clashes": fine_clashes[:20], "clash_count": len(fine_clashes)}
    log(f"  {'one tooth pitch in 0.1 mm steps':42s} clashes {len(fine_clashes)}  worst {fine_worst}", flush=True)

    # backlash: turn the pinion each way until it touches the held rack
    def free(gap, dtheta, jaw_m):
        p = place_shape(pinion_s, PINION_IN_G @ Rz(pinion_deg(gap) + dtheta))
        inter = p & place_shape(jaw_s, jaw_m)
        return inter is None or sum(s.volume for s in inter.solids()) <= BACKLASH_TOL

    bl = {}
    for gap in (2.0, 22.0, 42.0):
        row = {}
        for k, m in (("rack_a", jaw_a_at(gap)), ("rack_b", jaw_b_at(gap))):
            play = 0.0
            for sign in (1.0, -1.0):
                lo, hi = 0.0, 4.0
                if not free(gap, 0.0, m) or free(gap, sign * hi, m):
                    play = float("nan")
                    break
                for _ in range(18):
                    mid = (lo + hi) / 2
                    lo, hi = (mid, hi) if free(gap, sign * mid, m) else (lo, mid)
                play += C.R_P * math.radians(lo)
            row[k] = round(play, 3)
        row["jaw_gap_play"] = round(row["rack_a"] + row["rack_b"], 3)
        bl[f"gap {gap:g}"] = row
    rep["backlash_mm"] = {"definition": "free turn of the pinion between the two flanks of one rack, as arc length "
                                        "on the pitch circle (rack held); jaw_gap_play = both meshes, servo held",
                          "design": C.BACKLASH, **bl}
    log(f"  backlash (pitch-circle arc per mesh): {bl}", flush=True)

    rep["ok"] = (all(p.get("clash_count", 0) == 0 for p in rep["paths"].values())
                 and rep["stroke"]["clash_count"] == 0 and rep["mesh_fine"]["clash_count"] == 0)
    rep["run_s"] = round(time.time() - t_start, 1)
    return rep


def main():
    print("claw sequence check (exact solids) ...", flush=True)
    rep = run()
    (HERE / "claw_sequence_check.json").write_text(json.dumps(rep, indent=1))
    print("ok" if rep["ok"] else "CLASHES", f"({rep['run_s']} s) -> claw_sequence_check.json")


if __name__ == "__main__":
    main()

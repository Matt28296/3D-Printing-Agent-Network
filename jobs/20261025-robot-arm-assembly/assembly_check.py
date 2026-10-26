"""Assembly interference and reach check for the desktop robot arm.

Places every printed part (each model.py's design(), in its joint frame) plus servo, ESP32 and
camera dummies (the Brio carries a right-angle USB-C plug on its back and the thumb screw under
its seat) in the world frame for a set of joint poses, then measures the overlap volume of every
pair of bodies. Overlaps under TOL mm³ count as touching (tabs resting on plates, horns in
pockets). Then:
- joint sweeps, one joint at a time. The ELBOW and WRIST windows count only that joint's own
  self-collisions (the parts beyond the joint against the link and servo it hangs on), which no
  other joint can change. Hits against the turntable, base, ring and desk depend on the other
  joints; they are listed, and the firmware's guard keeps the arm out of them (deep review 02 A4);
- the desk search: poses with the fingertips 0-8 mm above the desk, nearest and farthest
  collision-free, for any claw angle and with the claw within 5° of straight down. "pick from
  desk" and the two "desk ..." poses come from it;
- the viewer's demo poses (viz_export.DEMO): collision-free and above the desk;
- the claw: claw_sequence_check.run(), its assembly sequence and running fit with exact solids
  (deep review 03 SYS-01 / SYS-08).
Writes assembly_check.json and renders assembly_*.png.

Run from the project root:  .venv/bin/python jobs/20261025-robot-arm-assembly/assembly_check.py
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import math
import sys
import tempfile
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from build123d import Align, Box, Cylinder, Pos, export_stl  # noqa: E402
from hobby_parts import (BRIO_4K, ESP32_DEVKIT_38, MG90S, MG996R, link_back_z,  # noqa: E402
                         servo_dummy)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import claw_frame as C  # noqa: E402
import claw_sequence_check as CS  # noqa: E402

HERE = Path(__file__).resolve().parent
TOL = 1.0  # mm³ (meshes; resting contacts and servo dummies in their pockets)
EXPECTED = [{"base", "desk"}, {"cradle", "esp32"}, {"camera_mount", "brio"}]   # resting contacts
JOBS = {
    "base": "20261025-arm-base", "ring": "20261025-arm-turntable-ring",
    "turntable": "20261025-arm-turntable", "upper": "20261025-arm-upper-link",
    "forearm": "20261025-arm-forearm", "cradle": "20261025-arm-esp32-cradle",
    # parallel claw + Brio 4K mount (claw v2, 2026-10-26; replaces gripper-base / gripper-jaw)
    "claw_frame": "20261026-arm-claw-frame", "claw_cover": "20261026-arm-claw-cover",
    "claw_pinion": "20261026-arm-claw-pinion", "claw_jaw": "20261026-arm-claw-jaw",
    "camera_mount": "20261026-arm-camera-mount",
}
# parts that never move against each other: their pairs are checked in the named poses only
RIGID = [{"base", "ring", "cradle", "esp32", "servo_base", "desk"}, {"turntable", "servo_shoulder"},
         {"upper", "servo_elbow"}, {"forearm", "servo_wrist"},
         {"claw_frame", "claw_cover", "camera_mount", "brio", "servo_grip"}]
CLAW_SET = {"claw_frame", "claw_cover", "claw_pinion", "claw_jaw", "claw_jaw_b", "servo_grip", "camera_mount", "brio"}
BEYOND = {"elbow": {"forearm", "servo_wrist"} | CLAW_SET, "wrist": CLAW_SET}   # parts carried by the joint ...
ON = {"elbow": {"upper", "servo_elbow"}, "wrist": {"forearm", "servo_wrist"}}   # ... and what they hang on
DESK_Z = -40.0
# q = (yaw, shoulder, elbow, wrist in degrees, claw gap in mm). shoulder 0 = upper link horizontal
# towards +X, + = up; elbow/wrist 0 = straight, + = up; gap 0 = closed, 44 = open.
# Servo travel 0..180 for every joint (sketch LIMITS). Shoulder: servo 90 = upper link upright.
# Elbow: the horn is fitted at servo 90 with the forearm 60° below the upper link (towards +X), so
# servo 0..180 = elbow -150..+30 (deep review 03 SYS-03, BUILD_GUIDE §4). Wrist: servo 90 = straight.
TRAVEL = {"shoulder": (0, 180), "elbow": (-150, 30), "wrist": (-90, 90)}


def load_model(job):
    spec = importlib.util.spec_from_file_location(f"m_{job.replace('-', '_')}", ROOT / "jobs" / job / "model.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def to_mesh(shape) -> trimesh.Trimesh:
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "s.stl"
        export_stl(shape, str(p), tolerance=0.05, angular_tolerance=0.2)
        return trimesh.load(p, force="mesh")


# --- 4x4 transforms ---------------------------------------------------------------------
def T(x=0.0, y=0.0, z=0.0):
    m = np.eye(4); m[:3, 3] = (x, y, z); return m


def Rz(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    m = np.eye(4); m[:2, :2] = [[c, -s], [s, c]]; return m


def Ry(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    m = np.eye(4); m[0, 0], m[0, 2], m[2, 0], m[2, 2] = c, s, -s, c; return m


def frame(origin, x_dir, z_dir):
    x = np.array(x_dir, float); x /= np.linalg.norm(x)
    z = np.array(z_dir, float); z /= np.linalg.norm(z)
    y = np.cross(z, x)
    m = np.eye(4); m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = x, y, z, origin
    return m


def chain(mods):
    """The arm's kinematic chain: returns place(q) -> ({body: 4x4 world transform}, fingertip xyz).
    q = (yaw, shoulder, elbow, wrist in degrees, claw gap in mm); see TRAVEL for the conventions."""
    tt = mods["turntable"]
    lb_mg, lb_sg = link_back_z(MG996R), link_back_z(MG90S)
    xs, zs, up_y = tt.XS, tt.ZS, tt.UP_Y
    t_up, t_fa = mods["upper"].T, mods["forearm"].T
    l_up, l_fa = mods["upper"].L, mods["forearm"].L
    servo_in_g = frame((C.X_B, 0, C.ZS), (0, 1, 0), (1, 0, 0))
    pinion_in_g = frame((C.X_P0, 0, C.ZS), (0, 0, 1), (1, 0, 0))
    turn_b = T(0, 0, C.ZS) @ CS.Rx(180) @ T(0, 0, -C.ZS)            # jaw B = jaw A turned about the pinion axis
    cam_in_g = T(C.CAM_XC, 0, C.CAM_ZC) @ Ry(C.CAM_TILT)

    def place(q):
        yaw, sh, el, wr, gap = q            # gap = jaw opening in mm (0 = closed, 44 = open)
        W = Rz(yaw)
        P = {"base": np.eye(4), "ring": np.eye(4), "cradle": np.eye(4), "esp32": np.eye(4), "desk": np.eye(4),
             "servo_base": np.eye(4), "turntable": W}
        P["servo_shoulder"] = W @ frame((xs, up_y, zs), (1, 0, 0), (0, 1, 0))
        U = W @ frame((xs, up_y + lb_mg, zs), (math.cos(math.radians(sh)), 0, math.sin(math.radians(sh))), (0, 1, 0))
        P["upper"] = U
        P["servo_elbow"] = U @ T(l_up, 0, t_up)
        F = U @ T(l_up, 0, t_up + lb_mg) @ Rz(-el)       # + = elbow up
        P["forearm"] = F
        P["servo_wrist"] = F @ T(l_fa, 0, t_fa)
        G = F @ T(l_fa, 0, t_fa + lb_sg) @ Rz(-wr)        # + = wrist up
        d = gap / 2.0
        P["claw_frame"] = P["claw_cover"] = P["camera_mount"] = G
        P["servo_grip"] = G @ servo_in_g
        P["claw_pinion"] = G @ pinion_in_g @ Rz(math.degrees(d / C.R_P))
        P["claw_jaw"] = G @ T(0, -d, 0)
        P["claw_jaw_b"] = G @ turn_b @ T(0, -d, 0)
        P["brio"] = G @ cam_in_g
        tip = G @ np.array([C.X_TIP - 3.0, 0.0, C.ZS, 1.0])      # between the fingertips
        return P, tip[:3]

    return place


def brio_with_plug():
    """Brio 4K in its camera frame (origin at the thread on the bottom face, +X lens, +Y long axis),
    plus a right-angle USB-C plug on the BACK face (deep review 01 S5: ≈12 out × 8 thick × 25 along
    the camera, port assumed centred on the back above the mount's 6 mm lip), plus the thumb
    screw's knurled head (Ø16 × 5) under the 4 mm seat."""
    w, l, h = BRIO_4K.width, BRIO_4K.length, BRIO_4K.height
    body = Box(w, l, h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    plug = Pos(-w / 2 - 6.0, 8.5, h / 2) * Box(12.0, 25.0, 8.0)
    thumb = Pos(0, 0, -C.SEAT_T) * Cylinder(8.0, 5.0, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return body + plug + thumb


def main():
    mods = {k: load_model(v) for k, v in JOBS.items()}
    tt = mods["turntable"]
    print("tessellating parts ...", flush=True)
    solid = {k: mods[k].design() for k in ("claw_frame", "claw_cover", "claw_pinion", "claw_jaw", "camera_mount")}
    mesh = {k: to_mesh(solid[k] if k in solid else m.design()) for k, m in mods.items()}
    mesh["claw_jaw_b"] = mesh["claw_jaw"].copy()
    mesh["servo_base"] = to_mesh(servo_dummy(MG996R, with_horn=False))
    mesh["servo_shoulder"] = mesh["servo_base"].copy()
    mesh["servo_elbow"] = mesh["servo_base"].copy()
    mesh["servo_wrist"] = to_mesh(servo_dummy(MG90S, with_horn=False))
    mesh["servo_grip"] = mesh["servo_wrist"].copy()
    mesh["brio"] = to_mesh(brio_with_plug())
    b = ESP32_DEVKIT_38
    x1 = mods["cradle"].USB_END_X
    yc = mods["cradle"].YC
    pcb = Pos(x1 - b.length / 2, yc, -11.6 + b.pcb_t / 2) * Box(b.length, b.width, b.pcb_t)
    shield = Pos(x1 - b.length + 9, yc, -10 + 3.2 / 2) * Box(18, 16, 3.2)     # WROOM module can
    mesh["esp32"] = to_mesh(pcb + shield)
    mesh["desk"] = to_mesh(Pos(0, 0, DESK_Z - 5) * Box(800, 800, 10))   # desk top at Z = -40

    place = chain(mods)
    zs = tt.ZS

    def overlaps(P, rigid=True):
        """Overlapping pairs over TOL. rigid=False skips pairs that never move against each other."""
        placed = {k: mesh[k].copy().apply_transform(P[k]) for k in P}
        hits = []
        for a, c in itertools.combinations(sorted(placed), 2):
            if {a, c} in EXPECTED or (not rigid and any(a in g and c in g for g in RIGID)):
                continue
            ma, mc = placed[a], placed[c]
            lo = np.maximum(ma.bounds[0], mc.bounds[0]); hi = np.minimum(ma.bounds[1], mc.bounds[1])
            if np.any(hi - lo <= 0):
                continue
            try:
                v = trimesh.boolean.intersection([ma, mc], engine="manifold").volume
            except Exception:  # empty result
                v = 0.0
            if v > TOL:
                hits.append((a, c, round(float(v), 1)))
        return hits, placed

    def own(hits, joint):
        return [h for h in hits if (h[0] in BEYOND[joint] and h[1] in ON[joint])
                or (h[1] in BEYOND[joint] and h[0] in ON[joint])]

    def in_travel(q):
        return all(lo <= v <= hi for (lo, hi), v in zip(TRAVEL.values(), q[1:4]))

    report = {"tol_mm3": TOL, "servo_travel_deg": TRAVEL, "poses": {}, "sweeps": {}}

    # desk search: fingertips 0-8 mm above the desk (yaw 0), on a 5° / 5° / 10° grid
    on_desk = []
    for sh in range(TRAVEL["shoulder"][0], TRAVEL["shoulder"][1] + 1, 5):
        for el in range(TRAVEL["elbow"][0], TRAVEL["elbow"][1] + 1, 5):
            for wr in range(TRAVEL["wrist"][0], TRAVEL["wrist"][1] + 1, 10):
                _, tip = place((0, sh, el, wr, 0))
                if DESK_Z <= tip[2] <= DESK_Z + 8:
                    on_desk.append((math.hypot(tip[0], tip[1]), float(tip[0]), (0, sh, el, wr, 0)))
    down = [c for c in on_desk if abs(c[2][1] + c[2][2] + c[2][3] + 90) <= 5]

    def first_clear(cands, limit=300):
        for r, x, q in cands[:limit]:
            if not overlaps(place(q)[0], rigid=False)[0]:
                return {"radius_mm": round(r, 1), "in_plane_x_mm": round(x, 1), "q_deg": q}
        return None

    desk = {}
    for label, cands in (("any claw angle", on_desk), ("claw within 5° of straight down", down)):
        near = sorted([c for c in cands if c[0] >= 60.0])     # r < 60 is over the base itself
        desk[label] = {"candidates": len(cands), "nearest": first_clear(near), "farthest": first_clear(near[::-1])}
        print(f"desk reach, {label}: {desk[label]}", flush=True)
    # "pick from desk": claw down, fingertips on the desk about 150 mm out, claw open 20 mm (opening moves the
    # fingers along G y, which tilts with the claw: the check must see the open claw)
    pick = first_clear([(r, x, q[:4] + (20,)) for r, x, q in sorted(down, key=lambda c: abs(c[0] - 150.0))])
    report["desk_reach"] = desk

    poses = {
        "home (reach out, horizontal)": (0, 0, 0, 0, 0),
        "upright (park, r)": (0, 90, 0, 0, 0),
        "elbow up 30": (0, 30, 30, 0, 0),
        "elbow down 90": (0, 90, -90, 0, 0),
        "elbow folded -150": (0, 90, -150, 0, 0),
        "wrist +90": (0, 30, -30, 90, 0),
        "wrist -90": (0, 30, -30, -90, 0),
        "gripper open 44": (45, 45, -45, 0, 44),
        "pick from desk": tuple(pick["q_deg"]),
        "desk, nearest (claw down)": desk["claw within 5° of straight down"]["nearest"]["q_deg"],
        "desk, farthest (any angle)": desk["any claw angle"]["farthest"]["q_deg"],
        "camera looking down": (0, 80, -90, -60, 10),
    }
    for name, q in poses.items():
        assert in_travel(q), f"pose {name!r} {q} is outside the servo travel {TRAVEL}"
    half_width = 0.0
    renders = {"home (reach out, horizontal)": "assembly_home.png", "pick from desk": "assembly_pick.png",
               "elbow up 30": "assembly_elbow.png", "upright (park, r)": "assembly_upright.png"}
    for name, q in poses.items():
        P, tip = place(q)
        hits, placed = overlaps(P)
        if q[0] == 0:       # yaw 0: world Y is across the arm plane (SYS-17 keep-out width)
            half_width = max(half_width, float(placed["brio"].bounds[1][1]), float(placed["camera_mount"].bounds[1][1]))
        report["poses"][name] = {"q_deg": list(q), "fingertip_mm": [round(float(v), 1) for v in tip], "collisions": hits}
        print(f"{name:36s} tip {np.round(tip, 0)}  collisions: {hits or 'none'}", flush=True)
        if name in renders:
            report["poses"][name]["render"] = renders[name]
            _render(placed, HERE / renders[name], name)
    report["camera_outboard_y_mm"] = round(half_width, 1)

    # viewer demo poses (viz_export.DEMO): inside the travel, collision-free, fingertips above the desk
    import viz_export
    demo = []
    for q in viz_export.DEMO:
        q = tuple(q)
        P, tip = place(q)
        hits = overlaps(P, rigid=False)[0]
        demo.append({"q": list(q), "in_travel": in_travel(q), "fingertip_z_mm": round(float(tip[2]), 1),
                     "collisions": hits})
    report["viewer_demo"] = demo
    print("viewer demo:", [(d["q"], d["in_travel"], d["fingertip_z_mm"], d["collisions"]) for d in demo], flush=True)

    # joint sweeps (one joint at a time, the others at a neutral pose)
    def sweep(idx, values, base_q, joint=None):
        rows = []
        for v in values:
            q = list(base_q); q[idx] = v
            hits = overlaps(place(tuple(q))[0], rigid=False)[0]
            rows.append((v, hits, own(hits, joint) if joint else hits))
        return {"tested": values, "base_q": list(base_q),
                "collision_free": [v for v, h, _ in rows if not h],
                "own_collision_free": [v for v, _, o in rows if not o],
                "hits": [(v, h) for v, h, _ in rows if h][:12]}

    def window(s, step):
        free, best, run = s["own_collision_free"], [], []
        for v in s["tested"]:
            run = run + [v] if v in free and (not run or v - run[-1] == step) else ([v] if v in free else [])
            best = run if len(run) > len(best) else best
        return [best[0], best[-1]] if best else None

    report["sweeps"]["shoulder (elbow 0)"] = sweep(1, list(range(0, 181, 10)), (0, 0, 0, 0, 0))
    report["sweeps"]["elbow (shoulder 90)"] = sweep(2, list(range(-150, 31, 5)), (0, 90, 0, 0, 0), "elbow")
    report["sweeps"]["elbow (shoulder 60)"] = sweep(2, list(range(-150, 31, 10)), (0, 60, 0, 0, 0), "elbow")
    report["sweeps"]["wrist (shoulder 45, elbow -45)"] = sweep(3, list(range(-90, 91, 10)), (0, 45, -45, 0, 0), "wrist")
    report["sweeps"]["claw opening mm"] = sweep(4, list(range(0, 45, 4)), (0, 45, -45, 0, 0))
    report["elbow_window_deg"] = window(report["sweeps"]["elbow (shoulder 90)"], 5)
    report["wrist_window_deg"] = window(report["sweeps"]["wrist (shoulder 45, elbow -45)"], 10)
    for k, s in report["sweeps"].items():
        print(f"{k:32s} free: {s['collision_free']}")
        if s["hits"]:
            print(f"{'':32s} hits: {s['hits']}")
    print("elbow window", report["elbow_window_deg"], " wrist window", report["wrist_window_deg"], flush=True)

    _, tip = place((0, 0, 0, 0, 0))
    report["reach_horizontal_mm"] = round(float(math.hypot(tip[0], tip[1])), 1)
    report["shoulder_height_above_desk_mm"] = round(zs - DESK_Z, 1)

    # claw internals: assembly sequence, running stroke, backlash (exact solids)
    print("claw sequence check (exact solids) ...", flush=True)
    report["claw_internal"] = CS.run(solid)
    print("claw:", "clear" if report["claw_internal"]["ok"] else "CLASHES", flush=True)
    (HERE / "assembly_check.json").write_text(json.dumps(report, indent=1))
    print("reach", report["reach_horizontal_mm"], "-> assembly_check.json")


def _render(placed, out, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import render as R
    m = trimesh.util.concatenate([v for k, v in placed.items() if k != "desk"])
    fig, axes = plt.subplots(1, 2, figsize=(14, 7.4), dpi=100)
    for ax, (vname, (elev, azim)) in zip(axes, (("iso", R.VIEWS["iso"]), ("front", R.VIEWS["front"]))):
        img, _ = R.render_view(m, elev, azim, with_bed=False)
        ax.imshow(img, interpolation="antialiased"); ax.set_axis_off(); ax.set_title(vname)
    fig.suptitle(f"robot arm · {title} · parts + servo/ESP32/camera dummies", fontsize=13)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


if __name__ == "__main__":
    main()

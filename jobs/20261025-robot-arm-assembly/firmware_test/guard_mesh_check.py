"""Check the sketch's guard against the CAD meshes over the whole joint box. Slow (about 10 minutes); run it by
hand after any change to the arm's CAD, the elbow window or the guard's part boxes:

    .venv/bin/python jobs/20261025-robot-arm-assembly/firmware_test/guard_mesh_check.py [--coarse]

It places every part with assembly_check.py's chain (each job's design()), then for each pose in shoulder
0..180, elbow ELBOW_MIN..ELBOW_MAX, wrist -90..90 (5/5/10 deg steps; --coarse: 15/15/30), claw closed and open:
  * the lowest point of every moving part (its mesh's convex hull) against the desk;
  * contacts with the base box, the support ring and the turntable disk at yaw 0, +-45 and +-90 (point clouds);
and compares them with the guard (pc/arm_pc_control.guard_margins, which test_firmware.py proves equal to the
sketch's). It must let no contact through. Prints a summary; writes nothing.
"""
from __future__ import annotations

import argparse
import importlib.util
import math
import sys
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np
import trimesh

JOB = Path(__file__).resolve().parents[1]
ROOT = JOB.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(JOB))
from build123d import Align, Box, export_stl  # noqa: E402
from hobby_parts import BRIO_4K, MG90S, MG996R, link_back_z, servo_dummy  # noqa: E402
import claw_frame as C  # noqa: E402

JOBS = {"turntable": "20261025-arm-turntable", "upper": "20261025-arm-upper-link", "forearm": "20261025-arm-forearm",
        "base": "20261025-arm-base", "claw_frame": "20261026-arm-claw-frame", "claw_cover": "20261026-arm-claw-cover",
        "claw_pinion": "20261026-arm-claw-pinion", "claw_jaw": "20261026-arm-claw-jaw",
        "camera_mount": "20261026-arm-camera-mount"}
MOVING = ("upper", "servo_elbow", "forearm", "servo_wrist", "claw_frame", "claw_cover", "camera_mount",
          "claw_pinion", "claw_jaw", "claw_jaw_b", "servo_grip", "brio")
YAWS = (0, 45, 90, -45, -90)
DESK = -40.0


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def to_mesh(shape):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "s.stl"
        export_stl(shape, str(p), tolerance=0.05, angular_tolerance=0.2)
        return trimesh.load(p, force="mesh")


def T(x=0.0, y=0.0, z=0.0):
    m = np.eye(4); m[:3, 3] = (x, y, z); return m


def Rz(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d)); m = np.eye(4); m[:2, :2] = [[c, -s], [s, c]]; return m


def Rx(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d)); m = np.eye(4); m[1:3, 1:3] = [[c, -s], [s, c]]; return m


def Ry(d):
    c, s = math.cos(math.radians(d)), math.sin(math.radians(d)); m = np.eye(4)
    m[0, 0], m[0, 2], m[2, 0], m[2, 2] = c, s, -s, c
    return m


def frame(o, xd, zd):
    x = np.array(xd, float); x /= np.linalg.norm(x); z = np.array(zd, float); z /= np.linalg.norm(z)
    m = np.eye(4); m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = x, np.cross(z, x), z, o
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coarse", action="store_true", help="15/15/30 deg steps (a minute) instead of 5/5/10")
    args = ap.parse_args()
    step = (15, 15, 30) if args.coarse else (5, 5, 10)
    pc = load(JOB / "pc" / "arm_pc_control.py", "arm_pc_control")
    el_lo, el_hi = pc.LIMITS[2]
    mods = {k: load(ROOT / "jobs" / v / "model.py", "m_" + k) for k, v in JOBS.items()}
    tt = mods["turntable"]
    print("building meshes ...", flush=True)
    mesh = {k: to_mesh(mods[k].design()) for k in ("upper", "forearm", "claw_frame", "claw_cover", "claw_pinion",
                                                    "claw_jaw", "camera_mount")}
    mesh["claw_jaw_b"] = mesh["claw_jaw"]
    mesh["servo_elbow"] = to_mesh(servo_dummy(MG996R, with_horn=False))
    mesh["servo_wrist"] = mesh["servo_grip"] = to_mesh(servo_dummy(MG90S, with_horn=False))
    mesh["brio"] = to_mesh(Box(BRIO_4K.width, BRIO_4K.length, BRIO_4K.height, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    hull = {k: mesh[k].convex_hull.vertices for k in MOVING}
    rng = np.random.default_rng(0)

    def cloud(m, n=2500):
        pts = np.vstack([m.vertices, m.triangles_center])
        if len(pts) > n:
            pts = pts[rng.choice(len(pts), n, replace=False)]
        if len(m.vertices) < 100:
            lo, hi = m.bounds
            g = np.stack(np.meshgrid(*[np.linspace(lo[i], hi[i], 9) for i in range(3)], indexing="ij"), -1).reshape(-1, 3)
            pts = np.vstack([pts, g])
        return pts
    cl = {k: cloud(mesh[k]) for k in MOVING}
    lb_mg, lb_sg = link_back_z(MG996R), link_back_z(MG90S)
    bx, by = mods["base"].BX / 2, mods["base"].BY / 2
    servo_in_g = frame((C.X_B, 0, C.ZS), (0, 1, 0), (1, 0, 0))
    pinion_in_g = frame((C.X_P0, 0, C.ZS), (0, 0, 1), (1, 0, 0))
    turn_b = T(0, 0, C.ZS) @ Rx(180) @ T(0, 0, -C.ZS)
    cam_in_g = T(C.CAM_XC, 0, C.CAM_ZC) @ Ry(C.CAM_TILT)

    def place(q):                               # assembly_check.py place(), moving parts only
        yaw, sh, el, wr, gap = q
        U = Rz(yaw) @ frame((tt.XS, tt.UP_Y + lb_mg, tt.ZS), (math.cos(math.radians(sh)), 0, math.sin(math.radians(sh))), (0, 1, 0))
        F = U @ T(100, 0, mods["upper"].T + lb_mg) @ Rz(-el)
        G = F @ T(90, 0, mods["forearm"].T + lb_sg) @ Rz(-wr)
        d = gap / 2.0
        return {"upper": U, "servo_elbow": U @ T(100, 0, mods["upper"].T), "forearm": F,
                "servo_wrist": F @ T(90, 0, mods["forearm"].T), "claw_frame": G, "claw_cover": G, "camera_mount": G,
                "servo_grip": G @ servo_in_g, "claw_pinion": G @ pinion_in_g @ Rz(math.degrees(d / C.R_P)),
                "claw_jaw": G @ T(0, -d, 0), "claw_jaw_b": G @ turn_b @ T(0, -d, 0), "brio": G @ cam_in_g}, \
            (G @ np.array([C.X_TIP - 3.0, 0, C.ZS, 1.0]))[:3]

    def static_hit(p, yaw):
        if ((np.abs(p[:, 0]) < bx) & (np.abs(p[:, 1]) < by) & (p[:, 2] < 0) & (p[:, 2] > DESK)).any():
            return "base"
        r = np.hypot(p[:, 0], p[:, 1])
        if ((r > 41.0) & (r < 44.0) & (p[:, 2] > 0) & (p[:, 2] < 15.0)).any():
            return "ring"
        if ((r < tt.DISK_R) & (p[:, 2] > tt.Z0) & (p[:, 2] < tt.Z0 + tt.DISK_T)).any():
            return "disk"
        return None

    n = blocked_ok = 0
    let_through = Counter()
    per_yaw = {y: Counter() for y in YAWS}
    picks = {y: [] for y in YAWS}
    for gap in (0.0, 44.0):
        for sh in range(0, 181, step[0]):
            for el in range(int(el_lo), int(el_hi) + 1, step[1]):
                for wr in range(-90, 91, step[2]):
                    P, tip = place((0, sh, el, wr, gap))
                    low = min(float((hull[k] @ P[k][:3, :3].T + P[k][:3, 3])[:, 2].min()) for k in MOVING)
                    desk_m, _ = pc.guard_margins((0, sh, el, wr, gap))
                    n += 1
                    if desk_m >= 0 and low < DESK + pc.GUARD_CLEAR - 1e-6:
                        let_through["desk: closer than 8 mm"] += 1
                    if desk_m < 0 and low >= DESK + pc.GUARD_CLEAR:
                        blocked_ok += 1
                    for yaw in YAWS:
                        Py, _ = place((yaw, sh, el, wr, gap))
                        hit = None
                        for k in MOVING:
                            if k != "upper":
                                hit = hit or static_hit(cl[k] @ Py[k][:3, :3].T + Py[k][:3, 3], yaw)
                        dm, bm = pc.guard_margins((yaw, sh, el, wr, gap))
                        if hit:
                            per_yaw[yaw]["contact"] += 1
                            if dm >= 0 and bm >= 0:
                                let_through[f"{hit} at yaw {yaw}"] += 1
                        elif dm >= 0 and bm < 0:
                            per_yaw[yaw]["base keep-out blocks a clean pose"] += 1
                        if abs(sh + el + wr + 90) <= 20 and tip[2] <= DESK + 15 and low >= DESK and not hit \
                                and dm >= 0 and bm >= 0:
                            picks[yaw].append(tip[0])
        print(f"gap {gap:.0f}: {n} poses so far", flush=True)
    print(f"\n{n} poses (shoulder 0..180, elbow {el_lo:.0f}..{el_hi:.0f}, wrist -90..90; steps {step}; claw 0 and 44 mm)")
    print(f"desk: the guard blocks {blocked_ok} poses ({100 * blocked_ok / n:.1f} %) that clear it by 8 mm or more")
    for yaw in YAWS:
        c = per_yaw[yaw]
        xs = picks[yaw]
        print(f"yaw {yaw:4d}: {c['contact']} poses touch the base, ring or disk; the keep-out also blocks "
              f"{c['base keep-out blocks a clean pose']} clean ones; top-down picks (claw within 20 deg of vertical, "
              f"tips <= 15 mm up) at in-plane x {min(xs) if xs else 0:.0f}..{max(xs) if xs else 0:.0f} mm")
    print("LET THROUGH:", dict(let_through) if let_through else "nothing")
    sys.exit(1 if let_through else 0)


if __name__ == "__main__":
    main()

"""Check the sketch's guard against the CAD meshes over the whole joint box. Slow (about 20 minutes); run it by
hand after any change to the arm's CAD, the elbow window or the guard's part boxes:

    .venv/bin/python jobs/20261025-robot-arm-assembly/firmware_test/guard_mesh_check.py [--coarse]

It places every part with assembly_check.py's own chain() and meshes (the Brio with its right-angle plug and
thumb screw, assembly_check.brio_with_plug()), then for each pose in shoulder 0..180, elbow ELBOW_MIN..ELBOW_MAX,
wrist -90..90 (5/5/10 deg steps; --coarse: 15/15/30), claw closed and open:
  * the lowest point of every moving part (its mesh's convex hull) against the desk, and the guard's verdict;
  * contacts with the base box, the support ring and the turntable disk at yaw 0, +-45 and +-90 (point clouds
    against the parts' own dimensions);
  * the upper link's closest approach to the disk top and the base top, which the guard leaves out;
and compares them with the guard (pc/arm_pc_control.guard_margins, which test_firmware.py proves equal to the
sketch's). The guard must let no pose closer than 8 mm to the desk, and no contact, through. Prints a summary;
writes nothing.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import trimesh

JOB = Path(__file__).resolve().parents[1]
ROOT = JOB.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(JOB))
import assembly_check as AC  # noqa: E402
from hobby_parts import MG90S, MG996R, servo_dummy  # noqa: E402

MOVING = ("upper", "servo_elbow", "forearm", "servo_wrist", "claw_frame", "claw_cover", "camera_mount",
          "claw_pinion", "claw_jaw", "claw_jaw_b", "servo_grip", "brio")
YAWS = (0, 45, 90, -45, -90)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coarse", action="store_true", help="15/15/30 deg steps (a minute) instead of 5/5/10")
    args = ap.parse_args()
    step = (15, 15, 30) if args.coarse else (5, 5, 10)
    spec = importlib.util.spec_from_file_location("arm_pc_control", JOB / "pc" / "arm_pc_control.py")
    pc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pc)
    el_lo, el_hi = pc.LIMITS[2]
    mods = {k: AC.load_model(v) for k, v in AC.JOBS.items()}
    place = AC.chain(mods)
    tt, ring, base = mods["turntable"], mods["ring"], mods["base"]
    desk = AC.DESK_Z
    print("building meshes ...", flush=True)
    mesh = {k: AC.to_mesh(mods[k].design()) for k in ("upper", "forearm", "claw_frame", "claw_cover", "claw_pinion",
                                                       "claw_jaw", "camera_mount")}
    mesh["claw_jaw_b"] = mesh["claw_jaw"]
    mesh["servo_elbow"] = AC.to_mesh(servo_dummy(MG996R, with_horn=False))
    mesh["servo_wrist"] = mesh["servo_grip"] = AC.to_mesh(servo_dummy(MG90S, with_horn=False))
    mesh["brio"] = AC.to_mesh(AC.brio_with_plug())
    hull = {k: mesh[k].convex_hull.vertices for k in MOVING}
    rng = np.random.default_rng(0)

    def cloud(m, n_vertices=2000, n_surface=5000):
        """Points on the part: its vertices plus points spread evenly over its surface (about 2 mm apart on the
        Brio), so a large flat face can't slide into the base or the ring between two sample points."""
        v = m.vertices if len(m.vertices) <= n_vertices else m.vertices[rng.choice(len(m.vertices), n_vertices, replace=False)]
        s, _ = trimesh.sample.sample_surface(m, n_surface, seed=0)
        return np.vstack([v, s])
    cl = {k: cloud(mesh[k]) for k in MOVING}
    bx, by = base.BX / 2, base.BY / 2
    disk_top = tt.Z0 + tt.DISK_T

    def static_hit(p):
        r = np.hypot(p[:, 0], p[:, 1])
        if ((np.abs(p[:, 0]) < bx) & (np.abs(p[:, 1]) < by) & (p[:, 2] < 0) & (p[:, 2] > desk)).any():
            return "base"
        if ((r > ring.R_IN) & (r < ring.R_OUT) & (p[:, 2] > 0) & (p[:, 2] < ring.H)).any():
            return "ring"
        if ((r < tt.DISK_R) & (p[:, 2] > tt.Z0) & (p[:, 2] < disk_top)).any():
            return "disk"
        return None

    n = blocked_clear = 0
    let_through = Counter()
    per_yaw = {y: Counter() for y in YAWS}
    upper_gap = {"disk top": 1e9, "base top": 1e9}
    for gap in (0.0, 44.0):
        for sh in range(0, 181, step[0]):
            for el in range(int(el_lo), int(el_hi) + 1, step[1]):
                for wr in range(-90, 91, step[2]):
                    P, tip = place((0, sh, el, wr, gap))
                    low = min(float((hull[k] @ P[k][:3, :3].T + P[k][:3, 3])[:, 2].min()) for k in MOVING)
                    desk_m, _ = pc.guard_margins((0, sh, el, wr, gap))
                    n += 1
                    if desk_m >= 0 and low < desk + pc.GUARD_CLEAR - 1e-6:
                        let_through[f"desk: within 8 mm (lowest {low - desk:.1f} mm up) at {(sh, el, wr, gap)}"] += 1
                    if desk_m < 0 and low >= desk + pc.GUARD_CLEAR:
                        blocked_clear += 1
                    for yaw in YAWS:
                        Py, _ = place((yaw, sh, el, wr, gap))
                        hit = None
                        for k in MOVING:
                            p = cl[k] @ Py[k][:3, :3].T + Py[k][:3, 3]
                            if k == "upper":
                                r = np.hypot(p[:, 0], p[:, 1])
                                if (r < tt.DISK_R).any():
                                    upper_gap["disk top"] = min(upper_gap["disk top"], float(p[r < tt.DISK_R, 2].min()) - disk_top)
                                inb = (np.abs(p[:, 0]) < bx) & (np.abs(p[:, 1]) < by)
                                if inb.any():
                                    upper_gap["base top"] = min(upper_gap["base top"], float(p[inb, 2].min()))
                                continue
                            hit = hit or static_hit(p)
                        dm, bm = pc.guard_margins((yaw, sh, el, wr, gap))
                        if hit:
                            per_yaw[yaw]["contact"] += 1
                            if dm >= 0 and bm >= 0:
                                let_through[f"{hit} at yaw {yaw}"] += 1
                        elif dm >= 0 and bm < 0:
                            per_yaw[yaw]["clean, blocked by the keep-out"] += 1
        print(f"gap {gap:.0f}: {n} poses so far", flush=True)
    print(f"\n{n} poses (shoulder 0..180, elbow {el_lo:.0f}..{el_hi:.0f}, wrist -90..90; steps {step}; claw 0 and 44 mm)")
    print(f"desk: the guard blocks {blocked_clear} poses ({100 * blocked_clear / n:.1f} %) that clear it by 8 mm or more")
    for yaw in YAWS:
        c = per_yaw[yaw]
        print(f"yaw {yaw:4d}: {c['contact']} poses touch the base, ring or disk; the keep-out also blocks "
              f"{c['clean, blocked by the keep-out']} that touch nothing")
    print("upper link (left out of the base checks): closest to the disk top {:.1f} mm, to the base top {:.1f} mm".format(
        upper_gap["disk top"], upper_gap["base top"]))
    if upper_gap["disk top"] < pc.GUARD_CLEAR or upper_gap["base top"] < pc.GUARD_CLEAR:
        let_through["upper link within 8 mm of the turntable or base"] += 1
    print("LET THROUGH:", dict(let_through) if let_through else "nothing")
    sys.exit(1 if let_through else 0)


if __name__ == "__main__":
    main()

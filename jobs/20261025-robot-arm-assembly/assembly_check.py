"""Assembly interference and reach check for the desktop robot arm.

Places every printed part (each model.py's design(), in its joint frame) plus servo and
ESP32 dummies in the world frame for a set of joint poses, then measures the overlap
volume of every pair of bodies. Overlaps under TOL mm³ count as touching (tabs resting on
plates, horns in pockets). Writes assembly_check.json and renders assembly_*.png.

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
from build123d import Box, Pos, export_stl  # noqa: E402
from hobby_parts import (ESP32_DEVKIT_38, MG996R, SG90, link_back_z,  # noqa: E402
                         servo_dummy)

HERE = Path(__file__).resolve().parent
TOL = 1.0  # mm³
EXPECTED = [{"base", "desk"}, {"cradle", "esp32"}]   # resting contacts, not interference
JOBS = {
    "base": "20261025-arm-base", "ring": "20261025-arm-turntable-ring",
    "turntable": "20261025-arm-turntable", "upper": "20261025-arm-upper-link",
    "forearm": "20261025-arm-forearm", "gripper_base": "20261025-arm-gripper-base",
    "jaw": "20261025-arm-gripper-jaw", "cradle": "20261025-arm-esp32-cradle",
}


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


def frame(origin, x_dir, z_dir):
    x = np.array(x_dir, float); x /= np.linalg.norm(x)
    z = np.array(z_dir, float); z /= np.linalg.norm(z)
    y = np.cross(z, x)
    m = np.eye(4); m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = x, y, z, origin
    return m


def main():
    mods = {k: load_model(v) for k, v in JOBS.items()}
    tt = mods["turntable"]
    print("tessellating parts ...", flush=True)
    mesh = {k: to_mesh(m.design()) for k, m in mods.items()}
    mesh["servo_base"] = to_mesh(servo_dummy(MG996R, with_horn=False))
    mesh["servo_shoulder"] = mesh["servo_base"].copy()
    mesh["servo_elbow"] = mesh["servo_base"].copy()
    mesh["servo_wrist"] = to_mesh(servo_dummy(SG90, with_horn=False))
    mesh["servo_grip"] = mesh["servo_wrist"].copy()
    b = ESP32_DEVKIT_38
    x1 = mods["cradle"].USB_END_X
    yc = mods["cradle"].YC
    pcb = Pos(x1 - b.length / 2, yc, -11.6 + b.pcb_t / 2) * Box(b.length, b.width, b.pcb_t)
    shield = Pos(x1 - b.length + 9, yc, -10 + 3.2 / 2) * Box(18, 16, 3.2)     # WROOM module can
    mesh["esp32"] = to_mesh(pcb + shield)
    mesh["desk"] = to_mesh(Pos(0, 0, -45) * Box(800, 800, 10))   # desk top at Z = -40

    lb_mg, lb_sg = link_back_z(MG996R), link_back_z(SG90)
    xs, zs, up_y = tt.XS, tt.ZS, tt.UP_Y
    t_up, t_fa, t_gb = mods["upper"].T, mods["forearm"].T, mods["gripper_base"].T
    t_jaw = mods["jaw"].T

    def place(q):
        yaw, sh, el, wr, gr = q
        W = Rz(yaw)
        P = {"base": np.eye(4), "ring": np.eye(4), "cradle": np.eye(4), "esp32": np.eye(4), "desk": np.eye(4),
             "servo_base": np.eye(4), "turntable": W}
        P["servo_shoulder"] = W @ frame((xs, up_y, zs), (1, 0, 0), (0, 1, 0))
        U = W @ frame((xs, up_y + lb_mg, zs), (math.cos(math.radians(sh)), 0, math.sin(math.radians(sh))), (0, 1, 0))
        P["upper"] = U
        P["servo_elbow"] = U @ T(100, 0, t_up)
        F = U @ T(100, 0, t_up + lb_mg) @ Rz(-el)       # + = elbow up
        P["forearm"] = F
        P["servo_wrist"] = F @ T(90, 0, t_fa)
        G = F @ T(90, 0, t_fa + lb_sg) @ Rz(-wr)        # + = wrist up
        P["gripper_base"] = G
        P["servo_grip"] = G @ T(40, 0, t_gb)
        P["jaw"] = G @ T(40, 0, t_gb + lb_sg) @ Rz(gr)  # + = open
        tip = G @ np.array([95.0, -6.0, t_gb + lb_sg + t_jaw / 2, 1.0])
        return P, tip[:3]

    def overlaps(P):
        placed = {k: mesh[k].copy().apply_transform(P[k]) for k in P}
        hits = []
        for a, c in itertools.combinations(sorted(placed), 2):
            ma, mc = placed[a], placed[c]
            lo = np.maximum(ma.bounds[0], mc.bounds[0]); hi = np.minimum(ma.bounds[1], mc.bounds[1])
            if np.any(hi - lo <= 0) or {a, c} in EXPECTED:
                continue
            try:
                v = trimesh.boolean.intersection([ma, mc], engine="manifold").volume
            except Exception as e:  # empty result
                v = 0.0
            if v > TOL:
                hits.append((a, c, round(float(v), 1)))
        return hits, placed

    desk_z = -40.0
    # q = (yaw, shoulder, elbow, wrist, gripper) in degrees. shoulder 0 = upper link
    # horizontal towards +X, + = up; elbow/wrist 0 = straight, + = up; gripper 0 = closed.
    poses = {
        "home (reach out, horizontal)": (0, 0, 0, 0, 0),
        "upright": (0, 90, 0, 0, 0),
        "elbow up 90": (0, 30, 90, 0, 0),
        "elbow folded up 150": (0, 30, 150, 0, 0),
        "elbow folded down 150": (0, 60, -150, 0, 0),
        "wrist +90": (0, 30, -30, 90, 0),
        "wrist -90": (0, 30, -30, -90, 0),
        "gripper open 30": (45, 45, -45, 0, 30),
        "pick from desk": (-30, 70, -120, -40, 20),
    }
    report = {"tol_mm3": TOL, "poses": {}, "sweeps": {}}
    for name, q in poses.items():
        P, tip = place(q)
        hits, placed = overlaps(P)
        report["poses"][name] = {"q_deg": q, "fingertip_mm": [round(float(v), 1) for v in tip],
                                 "collisions": hits}
        print(f"{name:32s} tip {np.round(tip, 0)}  collisions: {hits or 'none'}", flush=True)
        if name in ("home (reach out, horizontal)", "pick from desk", "elbow up 90", "upright"):
            scene = trimesh.Scene(list(placed.values()))
            report["poses"][name]["render"] = f"assembly_{name.split()[0]}.png"
            _render(placed, HERE / report["poses"][name]["render"], name)

    # joint-range sweeps (one joint at a time, others at a neutral pose)
    def sweep(idx, values, base_q):
        ok = []
        for v in values:
            q = list(base_q); q[idx] = v
            hits, _ = overlaps(place(tuple(q))[0])
            ok.append((v, not hits, hits))
        free = [v for v, good, _ in ok if good]
        return {"tested": values, "collision_free": free,
                "first_hits": [(v, h) for v, g, h in ok if not g][:4]}
    report["sweeps"]["shoulder (elbow 0)"] = sweep(1, list(range(-40, 181, 10)), (0, 0, 0, 0, 0))
    report["sweeps"]["elbow (shoulder 60)"] = sweep(2, list(range(-170, 171, 10)), (0, 60, 0, 0, 0))
    report["sweeps"]["wrist (shoulder 45, elbow -45)"] = sweep(3, list(range(-150, 151, 10)), (0, 45, -45, 0, 0))
    report["sweeps"]["gripper"] = sweep(4, list(range(-20, 61, 5)), (0, 45, -45, 0, 0))
    for k, s in report["sweeps"].items():
        print(f"{k:32s} free: {s['collision_free']}")
        if s["first_hits"]:
            print(f"{'':32s} hits: {s['first_hits']}")
    # desk workspace: grid-search poses whose fingertip is 0-8 mm above the desk, then
    # confirm the nearest and farthest ones are collision-free
    on_desk = []
    for sh in range(-30, 181, 5):
        for el in range(-160, 141, 5):
            for wr in range(-120, 121, 10):
                _, tip = place((0, sh, el, wr, 0))
                if -40 <= tip[2] <= -32:
                    on_desk.append((math.hypot(tip[0], tip[1]), (0, sh, el, wr, 0)))
    on_desk.sort()
    found = {}
    for label, seq in (("nearest", on_desk), ("farthest", on_desk[::-1])):
        for r, q in seq[:400]:
            if r < 60 and label == "nearest":
                continue  # inside the base footprint
            if not overlaps(place(q)[0])[0]:
                found[label] = {"radius_mm": round(r, 1), "q_deg": q}
                break
    report["desk_reach"] = found
    print("desk reach", found)
    # reach: fingertip radius from the yaw axis at full extension
    _, tip = place((0, 0, 0, 0, 0))
    report["reach_horizontal_mm"] = round(float(math.hypot(tip[0], tip[1])), 1)
    report["shoulder_height_above_desk_mm"] = round(zs - desk_z, 1)
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
    fig.suptitle(f"robot arm · {title} · parts + servo/ESP32 dummies", fontsize=13)
    fig.tight_layout()
    fig.savefig(out)
    plt.close(fig)


if __name__ == "__main__":
    main()

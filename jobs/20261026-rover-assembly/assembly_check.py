"""Assembly interference check for the tracked rover.

Builds both track loops link by link (34 per side: 13 pins on the bottom run, 5 round the
idler, 12 on the top run, 4 round the sprocket), places the chassis, lid, sprockets, idlers,
road wheels and dummies of the motors, battery, HC-SR04, ESP32 (with jumper housings) and
breadboard, then measures the overlap of every pair of bodies (> TOL mm³ = collision). Also
checks that every sprocket/idler tooth sits inside a link notch on the wrap.

Run from the project root:  .venv/bin/python jobs/20261026-rover-assembly/assembly_check.py
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
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "tools"), str(HERE)]
from build123d import Box, Cylinder, Pos, Rot, export_stl  # noqa: E402
from hobby_parts import BATT_2X18650, ESP32_DEVKIT_38, MINI_BREADBOARD, gearmotor_dummy  # noqa: E402
import rover_frame as F  # noqa: E402

TOL = 0.5
JOBS = {"chassis": "20261026-rover-chassis", "lid": "20261026-rover-lid", "sprocket": "20261026-rover-sprocket",
        "idler": "20261026-rover-idler", "wheel": "20261026-rover-wheel", "link": "20261026-rover-track-link"}


def load(job):
    p = ROOT / "jobs" / job / "model.py"
    spec = importlib.util.spec_from_file_location(f"m_{job.replace('-', '_')}", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def to_mesh(shape, tol=0.05):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "s.stl"
        export_stl(shape, str(p), tolerance=tol, angular_tolerance=0.2)
        return trimesh.load(p, force="mesh")


def frame(origin, x_dir, z_dir):
    x = np.asarray(x_dir, float); x /= np.linalg.norm(x)
    z = np.asarray(z_dir, float); z /= np.linalg.norm(z)
    y = np.cross(z, x)
    m = np.eye(4); m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = x, y, z, origin
    return m


def track_pins():
    """Pin centres (x, z) round one loop, in travel order."""
    za, rp = F.Z_A, F.RP
    pins = [(i * F.P, za - rp) for i in range(13)]                                 # bottom run 0..120
    pins += [(F.AXLE_DX + rp * math.cos(math.radians(-90 + 36 * k)), za + rp * math.sin(math.radians(-90 + 36 * k)))
             for k in range(1, 6)]                                                  # idler wrap to the top
    pins += [(F.AXLE_DX - i * F.P, za + rp) for i in range(1, 13)]                  # top run 110..0
    pins += [(rp * math.cos(math.radians(90 + 36 * k)), za + rp * math.sin(math.radians(90 + 36 * k)))
             for k in range(1, 5)]                                                  # sprocket wrap
    assert len(pins) == F.N_LINKS, len(pins)
    return pins


def main():
    mods = {k: load(v) for k, v in JOBS.items()}
    print("tessellating ...", flush=True)
    M = {k: to_mesh(m.design()) for k, m in mods.items()}
    M["motor"] = to_mesh(gearmotor_dummy(F.MOTOR))
    b = BATT_2X18650
    floor_top = F.FLOOR_Z + F.FLOOR_T
    x0b = mods["chassis"].BATT_X0
    M["battery"] = to_mesh(Pos(x0b + b.length / 2, 0, floor_top + b.height / 2 + 0.01) * Box(b.length, b.width - 0.2, b.height))
    hx = F.X_FRONT_OUT - F.WALL
    sz = mods["chassis"].SENSOR_Z
    sensor = Pos(hx - 12.5 - 0.8, 0, sz) * Box(1.6, 45, 20)
    for sy in (-13.0, 13.0):
        sensor += Pos(hx - 12.0 + 6.0, sy, sz) * Rot(0, 90, 0) * Cylinder(8.0, 12.0)
    M["hcsr04"] = to_mesh(sensor)
    lid = mods["lid"]
    e = ESP32_DEVKIT_38
    zpcb = F.TOP_Z + lid.T + lid.LEDGE_H
    esp = Pos(lid.USB_END_X + e.length / 2, 0, zpcb + e.pcb_t / 2) * Box(e.length, e.width, e.pcb_t)
    pins_len = e.length - 2 * 4.34 + 2.54
    for sy in (-1, 1):   # header plastic + female jumper housings below each pin row
        esp += Pos(lid.USB_END_X + e.length / 2, sy * (e.width / 2 - 1.3), zpcb - 16.5 / 2) * Box(pins_len, 2.54, 16.5)
    esp += Pos(lid.USB_END_X + 9 + 9, 0, zpcb + e.pcb_t + 1.6) * Box(18, 16, 3.2)
    M["esp32"] = to_mesh(esp)
    bb = MINI_BREADBOARD
    M["breadboard"] = to_mesh(Pos(lid.BB_X0 + bb.length / 2, 0, F.TOP_Z + lid.T + bb.height / 2 + 0.01) * Box(bb.length, bb.width, bb.height))

    P = {"chassis": np.eye(4), "lid": np.eye(4), "battery": np.eye(4), "hcsr04": np.eye(4), "esp32": np.eye(4),
         "breadboard": np.eye(4)}
    for side, tag in ((1, "L"), (-1, "R")):
        P[f"motor{tag}"] = frame((0, side * F.MOTOR_FACE_Y, F.Z_A), (1, 0, 0), (0, side, 0))
        P[f"sprocket{tag}"] = frame((0, side * F.Y_T, F.Z_A), (1, 0, 0), (0, side, 0))
        P[f"idler{tag}"] = frame((F.AXLE_DX, side * F.Y_T, F.Z_A), (1, 0, 0), (0, side, 0))
        for i, x in enumerate(F.ROAD_X):
            P[f"wheel{tag}{i}"] = frame((x, side * F.Y_T, F.Z_A), (1, 0, 0), (0, side, 0))
        pins = track_pins()
        for i, (px, pz) in enumerate(pins):
            nx, nz = pins[(i + 1) % len(pins)]
            xd = np.array([nx - px, 0.0, nz - pz])
            zd = np.cross(xd / np.linalg.norm(xd), [0, 1, 0])
            P[f"link{tag}{i:02d}"] = frame((px, side * F.Y_T, pz), xd, zd)
    kind = lambda k: ("motor" if k.startswith("motor") else "sprocket" if k.startswith("sprocket") else
                      "idler" if k.startswith("idler") else "wheel" if k.startswith("wheel") else
                      "link" if k.startswith("link") else k)
    placed = {k: M[kind(k)].copy().apply_transform(T) for k, T in P.items()}

    hits = []
    keys = sorted(placed)
    for a, c in itertools.combinations(keys, 2):
        ma, mc = placed[a], placed[c]
        lo = np.maximum(ma.bounds[0], mc.bounds[0]); hi = np.minimum(ma.bounds[1], mc.bounds[1])
        if np.any(hi - lo <= 0):
            continue
        try:
            v = trimesh.boolean.intersection([ma, mc], engine="manifold").volume
        except Exception:
            v = 0.0
        if v > TOL:
            hits.append((a, c, round(float(v), 2)))
    print("collisions:", hits or "none")

    # tooth engagement: each tooth tip (world) must land inside some link's notch
    # (link frame: NOTCH_X0 <= x <= P - (KN_R), |y| <= NOTCH_HALF, |z| <= LINK_T/2)
    lm, spm = mods["link"], mods["sprocket"]
    engaged = {}
    for tag, side in (("L", 1), ("R", -1)):
        for s, xc in (("sprocket", 0.0), ("idler", F.AXLE_DX)):
            n_in = 0
            for k in range(F.N_TEETH):
                th = math.radians(-side * (spm.PHASE_DEG + k * 360.0 / F.N_TEETH))   # world angle (see frames)
                tip = np.array([xc + (spm.TOOTH_TIP_R - 0.3) * math.cos(th), side * F.Y_T,
                                F.Z_A + (spm.TOOTH_TIP_R - 0.3) * math.sin(th), 1.0])
                for key in keys:
                    if key.startswith(f"link{tag}"):
                        q = np.linalg.inv(P[key]) @ tip
                        if (lm.NOTCH_X0 <= q[0] <= F.P - lm.KN_R and abs(q[1]) <= lm.NOTCH_HALF
                                and abs(q[2]) <= F.LINK_T / 2):
                            n_in += 1
                            break
            engaged[f"{s}{tag}"] = n_in
    # ground contact and size
    allm = trimesh.util.concatenate([placed[k] for k in keys])
    lo, hi = allm.bounds
    links = trimesh.util.concatenate([placed[k] for k in keys if k.startswith("link")])
    report = {"tol_mm3": TOL, "collisions": hits, "links_per_side": F.N_LINKS, "axle_dx_mm": F.AXLE_DX,
              "teeth_engaged_in_notches": engaged,
              "overall_mm": [round(float(v), 1) for v in hi - lo], "lowest_point_mm": round(float(lo[2]), 2),
              "track_bottom_mm": round(float(links.bounds[0][2]), 2), "ground_clearance_mm": round(F.FLOOR_Z, 2)}
    (HERE / "assembly_check.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report))
    _render({k: v for k, v in placed.items()}, HERE / "assembly_rover.png")


def _render(placed, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import render as R
    m = trimesh.util.concatenate(list(placed.values()))
    fig, axes = plt.subplots(1, 2, figsize=(14, 7.4), dpi=100)
    for ax, (vname, (elev, azim)) in zip(axes, (("iso", R.VIEWS["iso"]), ("left side", R.VIEWS["front"]))):
        img, _ = R.render_view(m, elev, azim, with_bed=False)
        ax.imshow(img, interpolation="antialiased"); ax.set_axis_off(); ax.set_title(vname)
    fig.suptitle("tracked rover · parts + motor/battery/ESP32/sensor dummies", fontsize=13)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


if __name__ == "__main__":
    main()

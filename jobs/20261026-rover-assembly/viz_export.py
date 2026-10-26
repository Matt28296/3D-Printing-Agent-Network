"""Export the fully built tracked rover (printed parts + every bought part) as a GLB, plus the
viewer config (track path, spinners, parts list, page text).

Run from the project root:  .venv/bin/python jobs/20261026-rover-assembly/viz_export.py <out_dir>
Writes <out_dir>/robot.glb and <out_dir>/robot.json. Track links are direct children of the
root; the viewer moves them along the pitch path (tracks config) and spins the wheels.
"""
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "tools"), str(HERE)]
import assembly_viz as V  # noqa: E402
from hobby_parts import BATT_2X18650, ESP32_DEVKIT_38, MINI_BREADBOARD  # noqa: E402
import rover_frame as F  # noqa: E402

JOBS = {"chassis": "20261026-rover-chassis", "lid": "20261026-rover-lid", "sprocket": "20261026-rover-sprocket",
        "idler": "20261026-rover-idler", "wheel": "20261026-rover-wheel", "link": "20261026-rover-track-link"}
LABELS = {"chassis": "Chassis (tub)", "lid": "Lid / electronics deck", "sprocket": "Drive sprocket",
          "idler": "Idler", "wheel": "Road wheel", "link": "Track link"}
QTY = {"chassis": 1, "lid": 1, "sprocket": 2, "idler": 2, "wheel": 4, "link": 68}
PLATES = {"link": 2}            # 34 links per plate
PETG = "petg_olive"
STAMPS = [{"text": "Round 2 in review", "kind": "warn"}, {"text": "Assembly check clean", "kind": "pass"},
          {"text": "Not sliced yet", "kind": "note"}]
BOLT_L = {"wheel": 45.0, "idler": 35.0}   # head on the boss inner face (|y| 32); nyloc just past the hub


def load(job):
    spec = importlib.util.spec_from_file_location(f"m_{job.replace('-', '_')}", ROOT / "jobs" / job / "model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def frame(origin, x_dir, z_dir):
    x = np.asarray(x_dir, float); x /= np.linalg.norm(x)
    z = np.asarray(z_dir, float); z /= np.linalg.norm(z)
    y = np.cross(z, x)
    m = np.eye(4); m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = x, y, z, origin
    return m


def printed(mod):
    return [V._mat(V.shape_to_mesh(mod.design()), PETG)]


def stats(job):
    p = ROOT / "jobs" / job / "slice_stats.json"
    return json.loads(p.read_text()) if p.exists() else {}


def main(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    mods = {k: load(v) for k, v in JOBS.items()}
    ch, lid = mods["chassis"], mods["lid"]
    S = V.VizScene()
    root = S.group("rover")

    # --- body: chassis, lid, battery, sensor, switch, electronics ----------------------------
    S.add("p_chassis", printed(ch), root, label=LABELS["chassis"], info=JOBS["chassis"])
    S.add("p_lid", printed(lid), root, label=LABELS["lid"], info=JOBS["lid"])
    floor_top = F.FLOOR_Z + F.FLOOR_T
    b = BATT_2X18650
    S.add("batt", V.holder_2x18650_parts(b.length, b.width, b.height), root,
          matrix=V.T(ch.BATT_X0 + b.length / 2, 0, floor_top), label="2 × 18650 cells in a holder (7.4 V)", category="power")
    S.add("hcsr04", V.hcsr04_parts(), root, matrix=V.T(F.X_FRONT_OUT - F.WALL - 12.5, 0, ch.SENSOR_Z),
          label="HC-SR04 ultrasonic sensor", category="electronics")
    S.add("toggle", V.toggle_switch_parts(), root, matrix=V.T(F.X_REAR_OUT, 0, ch.SWITCH_Z) @ V.Rz(180),
          label="MTS-102 mini toggle switch", category="power")
    e = ESP32_DEVKIT_38
    zpcb = F.TOP_Z + lid.T + lid.LEDGE_H
    S.add("esp32", V.esp32_parts(e), root, matrix=V.T(lid.USB_END_X, 0, zpcb), label="ESP32-DevKitC (38-pin)",
          category="electronics")
    bb = MINI_BREADBOARD
    bbx, bbz = lid.BB_X0 + bb.length / 2, F.TOP_Z + lid.T
    S.add("breadboard", V.breadboard_parts(bb.length, bb.width, bb.height), root, matrix=V.T(bbx, 0, bbz),
          label="Mini breadboard (170 points)", category="electronics")
    S.add("tb6612", V.tb6612_parts(), root, matrix=V.T(bbx - 11, -4, bbz + bb.height + 2.5),
          label="TB6612FNG motor driver", category="electronics")
    S.add("buck", V.buck_parts(), root, matrix=V.T(bbx + 11, 6, bbz + bb.height + 2.5) @ V.Rz(90),
          label="MP1584 buck, set to 5.0 V", category="power")
    for (x, y) in lid.SCREWS:
        S.add("m3x10", V.screw_parts(3, 10, "pan"), root, matrix=V.T(x, y, F.TOP_Z + lid.T),
              label="M3 × 10 self-tapping (lid)", category="hardware")

    # --- per side: motor, sprocket, idler, road wheels, bolts, nuts ----------------------------
    spinners = []
    y_in = F.HALF_W_OUT - F.WALL - ch.BOSS_IN          # bolt heads on the boss inner faces
    for side, tag in ((1, "L"), (-1, "R")):
        S.add("n20", V.n20_parts(F.MOTOR), root, matrix=frame((0, side * F.MOTOR_FACE_Y, F.Z_A), (1, 0, 0), (0, side, 0)),
              label="N20 gear motor, 6 V 100 rpm", category="actuator")
        hubs = [("sprocket", 0.0, F.RP), ("idler", F.AXLE_DX, F.RP)] + [("wheel", x, mods["wheel"].RIM_R) for x in F.ROAD_X]
        for k, (kind, x, r) in enumerate(hubs):
            node = f"J_{kind}{tag}{k}"
            S.group(node, root, frame((x, side * F.Y_T, F.Z_A), (1, 0, 0), (0, side, 0)))
            S.add(f"p_{kind}", printed(mods[kind]), node, label=LABELS[kind], info=JOBS[kind])
            spinners.append({"node": node, "per_mm": round(-side / r, 5)})   # rad per mm of track travel
            if kind == "sprocket":
                continue
            # M3 x 45 axle bolt: head inside, shank outwards; nut flush in the trap; washers; nyloc
            rot = V.Rx(90 if side > 0 else -90)          # screw -Z -> outward
            L = BOLT_L[kind]
            S.add(f"m3x{L:.0f}", V.screw_parts(3, L, "pan"), root, matrix=V.T(x, side * y_in, F.Z_A) @ rot,
                  label=f"M3 × {L:.0f} axle bolt", category="hardware")
            S.add("m3nut", V.nut_parts(3), root, matrix=V.T(x, side * (F.HALF_W_OUT - 2.4), F.Z_A) @ V.Rx(-90 * side),
                  label="M3 nut (in the wall trap)", category="hardware")
            S.add("washer3s", V.washer_parts(3, 7.0), root, matrix=V.T(x, side * F.HALF_W_OUT, F.Z_A) @ V.Rx(-90 * side),
                  label="M3 washer", category="hardware")
            hub_out = F.Y_T + (mods["wheel"].RIM_HALF + 3.7 if kind == "wheel" else mods["sprocket"].DISC_HALF)
            y_out = hub_out + 0.5
            S.add("washer3s", V.washer_parts(3, 7.0), root, matrix=V.T(x, side * y_out, F.Z_A) @ V.Rx(-90 * side),
                  label="M3 washer", category="hardware")
            S.add("m3nyloc", V.nut_parts(3, nyloc=True), root, matrix=V.T(x, side * (y_out + 0.5), F.Z_A) @ V.Rx(-90 * side),
                  label="M3 nyloc nut", category="hardware")

    # --- tracks: 34 links per side with their steel pins (placed by the viewer) ----------------
    link_mesh = printed(mods["link"])
    pin = [V.cyl(F.PIN_D / 2, -11.75, 11.75, "steel", x=F.P, axis="y")]
    for m in pin:   # cyl(axis='y') ignores x: move the pin to the link's front hinge
        m.apply_translation((F.P, 0, 0))
    sides = []
    for side, tag in ((1, "L"), (-1, "R")):
        names = []
        for i in range(F.N_LINKS):
            n = f"link{tag}{i:02d}"
            S.group(n, root)
            S.add("p_link", link_mesh, n, label=LABELS["link"], info=JOBS["link"])
            S.add("pin2", pin, n, label="Ø2 × 23.5 steel pin", category="hardware")
            names.append(n)
        sides.append({"y": side * F.Y_T, "links": names})

    size = S.export(out_dir / "robot.glb")
    parts = []
    for k, job in JOBS.items():
        st = stats(job)
        parts.append({"label": LABELS[k], "job": job, "qty": QTY[k], "plates": PLATES.get(k, 1),
                      "hours": st.get("print_time_h"), "grams": st.get("filament_g")})
    path_r = (F.N_LINKS * F.P - 2 * F.AXLE_DX) / (2 * math.pi)      # circular wrap that matches 34 × 10 mm
    cfg = {
        "robot": "rover", "ground_z": 0.0, "petg": "#6c7c3a",
        "camera": {"pos": [300, -330, 220], "target": [58, 0, 30]},
        "tracks": {"x1": F.AXLE_DX, "za": F.Z_A, "r": round(path_r, 4), "P": F.P, "dir": -1, "sides": sides,
                   "spinners": spinners},
        "nodes": S.meta, "printed_parts": parts, "glb_bytes": size,
        "page": {
            "title": "Tracked Rover",
            "eyebrow": "MK3 AutoPrint · robot 2 of 3 · fully assembled",
            "pose_title": "Drive",
            "lede": ("A skid-steer tracked rover printed in PETG. Two N20 gear motors drive a 10-tooth sprocket on each side; "
                     "the sprocket hubs run in journals in the chassis walls, so the motor shafts carry only torque. Each track "
                     "is 34 printed links on 2 mm steel pins. An ESP32 and a TB6612FNG driver ride on the lid, two 18650 cells "
                     "sit in the tub, and an HC-SR04 looks out of the front."),
            "meta": [["Printed parts", str(sum(QTY.values()))],
                     ["Print time", f"{sum((p['hours'] or 0) * p['plates'] for p in parts):.1f} h"],
                     ["PETG", f"{sum((p['grams'] or 0) * p['plates'] for p in parts):.0f} g"], ["Size", "160 × 142 × 60 mm"]],
            "stamps": STAMPS,
            "facts": [["Controller", "ESP32 DevKit (38- or 30-pin) pins-down on the lid"],
                      ["Drive", "2 × N20 6 V 100 rpm, TB6612FNG on a mini breadboard; ≈10 N of track pull per side"],
                      ["Tracks", "34 links per side, 10 mm pitch, 2 mm steel pins; 10-tooth sprocket and idler"],
                      ["Power", "2 × 18650 (7.4 V) with a toggle switch; MP1584 buck to 5 V for the ESP32"],
                      ["Sensor", "HC-SR04 behind the front wall"],
                      ["Ground clearance", f"{F.FLOOR_Z:.1f} mm"],
                      ["Drop rating", f"{F.DROP_MM // 10} cm onto a hard floor"],
                      ["Files", "jobs/20261026-rover-* in Matt28296/3D-Printing-Agent-Network"]],
        },
    }
    (out_dir / "robot.json").write_text(json.dumps(cfg, indent=1))
    print(f"robot.glb {size/1e6:.2f} MB, {len(S.meta)} part nodes")


if __name__ == "__main__":
    main(Path(sys.argv[1]))

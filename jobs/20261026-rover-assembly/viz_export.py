"""Export the fully built tracked rover (printed parts + every bought part) as a GLB, plus the
viewer config (track path, spinners, parts list, page text).

Run from the project root:  .venv/bin/python jobs/20261026-rover-assembly/viz_export.py <out_dir>
Writes <out_dir>/robot.glb and <out_dir>/robot.json. Track links are direct children of the
root; the viewer moves them along the pitch path (tracks config) and spins the wheels.
Bought parts sit where assembly_check.py puts them (round 4): N20s rolled 45° with their gearbox
faces on the 2 mm skins at |y| 44, Pololu hubs with the sprocket screws, fully threaded axle bolts with
their head washers, wall nuts and nylocs, the idler jack screws, the idlers' steel head and nut plates,
the toggle on the lid and the buck under it.
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
from build123d import Box, Cylinder, Pos, Rot  # noqa: E402
from hobby_parts import BATT_2X18650_LONG, ESP32_DEVKIT_38, MINI_BREADBOARD, mounting_hub_dummy  # noqa: E402
import rover_frame as F  # noqa: E402

JOBS = {"chassis": "20261026-rover-chassis", "lid": "20261026-rover-lid", "sprocket": "20261026-rover-sprocket",
        "idler": "20261026-rover-idler", "wheel": "20261026-rover-wheel", "link": "20261026-rover-track-link"}
LABELS = {"chassis": "Chassis (tub)", "lid": "Lid / electronics deck", "sprocket": "Drive sprocket",
          "idler": "Idler", "wheel": "Road wheel", "link": "Track link"}
QTY = {"chassis": 1, "lid": 1, "sprocket": 2, "idler": 2, "wheel": 4, "link": 70}   # 68 links + 2 spares
PLATES = {"link": 2}            # 34 links per plate (+ the 2 spares on one of them)
PETG = "petg_olive"
STAMPS = [{"text": "Round 4: printability passed", "kind": "pass"}, {"text": "Chassis strength review running", "kind": "warn"},
          {"text": "Slicing in progress", "kind": "note"}]
RESLICE = ("chassis", "lid", "sprocket", "idler", "wheel", "link")   # their slice_stats.json are from round 2: empty this
                                                                 # (or drop a part) once its round 4 slice is merged
BUCK_X0 = 85.0                  # buck under the lid, x 85-107 (as in assembly_check.py)
JACK_L = 20.0                   # M3 × 20 set screw (idler jack screw)


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


def plate_parts(length, height, slot_dx=0.0):
    """Idler clamp plate (round 4): length (x) × PLATE_T (y) × height (z), centred, with its slot at x = slot_dx
    (same shape as assembly_check.py's plate_dummy)."""
    w, sl = F.PLATE_SLOT
    cut = Pos(slot_dx, 0, 0) * Box(sl - w, F.PLATE_T + 2, w)
    for sx in (-1, 1):
        cut += Pos(slot_dx + sx * (sl - w) / 2, 0, 0) * Rot(90, 0, 0) * Cylinder(w / 2, F.PLATE_T + 2)
    return [V._mat(V.shape_to_mesh(Box(length, F.PLATE_T, height) - cut), "steel")]


def stats(job):
    p = ROOT / "jobs" / job / "slice_stats.json"
    return json.loads(p.read_text()) if p.exists() else {}


def main(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    mods = {k: load(v) for k, v in JOBS.items()}
    ch, lid, spm, wm = mods["chassis"], mods["lid"], mods["sprocket"], mods["wheel"]
    S = V.VizScene()
    root = S.group("rover")

    # --- body: chassis, lid, battery, sensor, switch, electronics ----------------------------
    S.add("p_chassis", printed(ch), root, label=LABELS["chassis"], info=JOBS["chassis"])
    S.add("p_lid", printed(lid), root, label=LABELS["lid"], info=JOBS["lid"])
    floor_top = F.FLOOR_Z + F.FLOOR_T
    b = BATT_2X18650_LONG
    S.add("batt", V.holder_2x18650_parts(b.length, b.width, b.height), root,
          matrix=V.T(ch.BATT_X0 + b.length / 2, 0, floor_top), label="2 × 18650 cells in a holder (7.4 V)", category="power")
    S.add("hcsr04", V.hcsr04_parts(), root, matrix=V.T(F.X_FRONT_OUT - F.WALL - 12.5, 0, ch.SENSOR_Z),
          label="HC-SR04 ultrasonic sensor (pins bent back, leads soldered)", category="electronics")
    sw_x, sw_y = lid.SWITCH
    S.add("toggle", V.toggle_switch_parts(), root, matrix=V.T(sw_x, sw_y, F.TOP_Z + lid.T) @ V.Rz(90) @ V.Ry(-90),
          label="MTS-102 mini toggle switch (on the lid, lever up)", category="power")
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
    S.add("buck", V.buck_parts(), root, matrix=V.T(BUCK_X0 + 11, 0, F.TOP_Z - 1.0) @ V.Rx(180),
          label="MP1584 buck, set to 5.0 V (under the lid, foam tape)", category="power")
    for (x, y) in lid.SCREWS:
        S.add("insert", [V.cyl(2.0, -5.7, 0.0, "brass")], root, matrix=V.T(x, y, F.TOP_Z),
              label="M3 heat-set insert", category="hardware")
        S.add("m3x8", V.screw_parts(3, 8, "socket"), root, matrix=V.T(x, y, F.TOP_Z + lid.T),
              label="M3 × 8 lid screw", category="hardware")

    # --- per side: motor, hub, sprocket, idler, road wheels, axle hardware, jack screw ----------------
    spinners = []
    hub_mesh = [V._mat(V.shape_to_mesh(mounting_hub_dummy(F.HUB, hole_angle_deg=spm.SLOT_ANGLE0)), "shield")]
    wheel_h = wm.RIM_HALF + wm.CONE_RISE + wm.FLANGE_FLAT                 # 16.0: wheel half width
    y_trap = F.HALF_W_OUT - ch.NUT_DEPTH                                  # wall nut pulled to the trap bottom
    axle = {"wheel": (F.HALF_W_OUT - F.WALL - F.BOSS_IN - F.WASHER[1], F.ROAD_BOLT_L, F.WASHER, F.Y_T + wheel_h),
            "idler": (ch.IDLER_HEAD_Y1, F.IDLER_BOLT_L, F.WASHER_WIDE, F.Y_T + spm.DISC_HALF)}
    # idler clamp plates (round 4), fixed to the chassis: head plate in its block-face recess, nut plate in the nut slot
    x_head_plate = sum(ch.PLATE_RECESS_X) / 2
    y_head_plate = F.HALF_W_OUT - F.WALL - F.BOSS_IN + F.PLATE_T / 2
    y_nut_plate = F.HALF_W_OUT - ch.NUT_SLOT_D + F.PLATE_T / 2
    head_plate = plate_parts(*F.IDLER_PLATE, slot_dx=F.AXLE_DX - x_head_plate)
    nut_plate = plate_parts(*F.NUT_PLATE)
    for side, tag in ((1, "L"), (-1, "R")):
        out = V.Rx(-90 * side)                        # local +Z -> outward (washers, nuts)
        S.add("n20", V.n20_parts(F.MOTOR), root,
              matrix=frame((0, side * F.MOTOR_FACE_Y, F.Z_A), F.motor_x_dir(side), (0, side, 0)),
              label=F.MOTOR.name, category="actuator")
        hubs = [("sprocket", 0.0, F.RP), ("idler", F.AXLE_DX, F.RP)] + [("wheel", x, wm.RIM_R) for x in F.ROAD_X]
        for k, (kind, x, r) in enumerate(hubs):
            node = f"J_{kind}{tag}{k}"
            S.group(node, root, frame((x, side * F.Y_T, F.Z_A), (1, 0, 0), (0, side, 0)))
            S.add(f"p_{kind}", printed(mods[kind]), node, label=LABELS[kind], info=JOBS[kind])
            spinners.append({"node": node, "per_mm": round(-side / r, 5)})   # rad per mm of track travel
            if kind == "sprocket":
                # in the sprocket's node frame: +z outward, z = 0 on the track plane
                S.add("hub", hub_mesh, node, matrix=V.T(0, 0, F.HUB_Y0 - F.Y_T), label=F.HUB.name, category="hardware")
                S.add("washer7", V.washer_parts(3, F.WASHER[0], F.WASHER[1]), node,
                      matrix=V.T(0, 0, F.MOTOR_FACE_Y + F.SKIN - F.Y_T), label="M3 thrust washer", category="hardware")
                for j in range(F.HUB.n_holes):
                    a = math.radians(spm.SLOT_ANGLE0 + j * 360.0 / F.HUB.n_holes)
                    px, py = F.HUB.bolt_circle_r * math.cos(a), F.HUB.bolt_circle_r * math.sin(a)
                    S.add("washer7", V.washer_parts(3, F.WASHER[0], F.WASHER[1]), node, matrix=V.T(px, py, spm.DISC_HALF),
                          label="M3 washer", category="hardware")
                    S.add("m3x12", V.screw_parts(3, F.HUB_SCREW_L, "socket", "black_oxide"), node,
                          matrix=V.T(px, py, spm.DISC_HALF + F.WASHER[1]), label="M3 × 12 hub screw", category="hardware")
                continue
            # axle bolt (class 12.9, fully threaded): head inside on its washer, shank outward through
            # the wall nut; running washers each side of the part; nyloc outside
            y_head, L, (hw_od, hw_t), part_out = axle[kind]
            S.add(f"m3x{L:.0f}", V.screw_parts(3, L, "socket", "black_oxide"), root,
                  matrix=V.T(x, side * y_head, F.Z_A) @ V.Rx(90 if side > 0 else -90),
                  label=f"M3 × {L:.0f} axle bolt, 12.9, fully threaded", category="hardware")
            S.add(f"washer{hw_od:.0f}", V.washer_parts(3, hw_od, hw_t), root, matrix=V.T(x, side * y_head, F.Z_A) @ out,
                  label="M3 washer (DIN 9021) under the head" if kind == "idler" else "M3 washer under the head",
                  category="hardware")
            S.add("m3nut", V.nut_parts(3), root, matrix=V.T(x, side * y_trap, F.Z_A) @ out,
                  label="M3 nut (in the wall trap)", category="hardware")
            for y_w in (F.HALF_W_OUT, part_out):
                S.add("washer7", V.washer_parts(3, F.WASHER[0], F.WASHER[1]), root, matrix=V.T(x, side * y_w, F.Z_A) @ out,
                      label="M3 washer", category="hardware")
            S.add("m3nyloc", V.nut_parts(3, nyloc=True), root, matrix=V.T(x, side * (part_out + F.WASHER[1]), F.Z_A) @ out,
                  label="M3 nyloc nut", category="hardware")
            if kind == "idler":
                x_tip = x - F.SCREW_HEAD[0] / 2 - 0.05
                S.add("jack", [V.cyl(1.5, 0.0, JACK_L, "black_oxide", axis="x")], root,
                      matrix=V.T(x_tip - JACK_L, side * ch.JACK_Y, F.Z_A), label="M3 × 20 jack screw (idler stop)",
                      category="hardware")
                S.add("plate_head", head_plate, root, matrix=V.T(x_head_plate, side * y_head_plate, F.Z_A),
                      label=f"Idler head plate, 2 mm steel {F.IDLER_PLATE[0]:g} × {F.IDLER_PLATE[1]:g} (under the Ø9 washer)",
                      category="hardware")
                S.add("plate_nut", nut_plate, root, matrix=V.T(F.AXLE_DX, side * y_nut_plate, F.Z_A),
                      label=f"Idler nut plate, 2 mm steel {F.NUT_PLATE[0]:g} × {F.NUT_PLATE[1]:g} (under the wall nut)",
                      category="hardware")

    # --- tracks: 34 links per side with their steel pins (placed by the viewer) ----------------
    link_mesh = printed(mods["link"])
    pin = [V.cyl(F.PIN_D / 2, -12.0, 12.0, "steel", x=F.P, axis="y")]
    for m in pin:   # cyl(axis='y') ignores x: move the pin to the link's front hinge
        m.apply_translation((F.P, 0, 0))
    sides = []
    for side, tag in ((1, "L"), (-1, "R")):
        names = []
        for i in range(F.N_LINKS):
            n = f"link{tag}{i:02d}"
            S.group(n, root)
            S.add("p_link", link_mesh, n, label=LABELS["link"], info=JOBS["link"])
            S.add("pin2", pin, n, label="Ø2 × 24 steel dowel pin", category="hardware")
            names.append(n)
        sides.append({"y": side * F.Y_T, "links": names})

    size = S.export(out_dir / "robot.glb")
    parts = []
    for k, job in JOBS.items():
        st = {} if k in RESLICE else stats(job)
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
            "lede": ("A skid-steer tracked rover printed in PETG. Two N20 gear motors, each rolled 45° into a nacelle inside "
                     "its track, drive a 10-tooth sprocket bolted to an aluminium hub on the motor shaft, so the torque path "
                     "is metal and the shaft overhang is 11 mm. Each track is 34 printed links on 2 mm steel pins, held "
                     "tight by an M3 jack screw at the idler, whose bolt is clamped between two steel plates. An ESP32, a "
                     "TB6612FNG driver and the power switch ride on the "
                     "lid, two 18650 cells sit in the tub, and an HC-SR04 looks out of the front."),
            "meta": [["Printed parts", str(sum(QTY.values()))],
                     ["Print time", f"{sum(p['hours'] * p['plates'] for p in parts):.1f} h"
                      if all(p['hours'] is not None for p in parts) else "slicing in progress"],
                     ["PETG", f"{sum(p['grams'] * p['plates'] for p in parts):.0f} g"
                      if all(p['grams'] is not None for p in parts) else "slicing in progress"], ["Size", "160 × 155 × 73 mm"]],
            "stamps": STAMPS,
            "facts": [["Controller", "ESP32 DevKit (38- or 30-pin) pins-down on the lid"],
                      ["Drive", "2 × N20 6 V 100 rpm (150:1, LP/MP, 3 mm D-shaft 10 mm long) on Pololu aluminium hubs; "
                                "TB6612FNG on a mini breadboard; ≈10 N of track pull per side"],
                      ["Tracks", "34 links per side, 10 mm pitch, Ø2 × 24 steel dowel pins; 10-tooth sprocket and idler; "
                                 "jack-screw tensioner; the idler bolt clamped between 2 mm steel plates"],
                      ["Power", "2 × 18650 (7.4 V), toggle switch on the lid; MP1584 buck to 5 V under the lid"],
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

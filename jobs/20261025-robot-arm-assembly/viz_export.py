"""Export the fully built desktop robot arm (printed parts + every bought part) as a GLB with
a joint hierarchy, plus the viewer config (joints, parts list, stats).

Run from the project root:  .venv/bin/python jobs/20261025-robot-arm-assembly/viz_export.py <out_dir>
Writes <out_dir>/robot.glb and <out_dir>/robot.json.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import assembly_viz as V  # noqa: E402
from hobby_parts import ESP32_DEVKIT_38, MG996R, SG90, link_back_z  # noqa: E402

JOBS = {"base": "20261025-arm-base", "ring": "20261025-arm-turntable-ring", "turntable": "20261025-arm-turntable",
        "upper": "20261025-arm-upper-link", "forearm": "20261025-arm-forearm", "gripper_base": "20261025-arm-gripper-base",
        "jaw": "20261025-arm-gripper-jaw", "cradle": "20261025-arm-esp32-cradle"}
LABELS = {"base": "Base", "ring": "Turntable support ring", "turntable": "Turntable + shoulder upright",
          "upper": "Upper link", "forearm": "Forearm", "gripper_base": "Gripper base + fixed jaw", "jaw": "Moving jaw",
          "cradle": "ESP32 cradle"}
PETG = "petg_orange"


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


def printed(mod, key):
    m = V.shape_to_mesh(mod.design())
    return [V._mat(m, PETG)]


def stats(job):
    p = ROOT / "jobs" / job / "slice_stats.json"
    return json.loads(p.read_text()) if p.exists() else {}


def main(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    mods = {k: load(v) for k, v in JOBS.items()}
    tt, base_m, cradle_m = mods["turntable"], mods["base"], mods["cradle"]
    S = V.VizScene()
    root = S.group("arm")
    lb_mg, lb_sg = link_back_z(MG996R), link_back_z(SG90)

    # --- static: base, ring, cradle, base servo, electronics, power, desk screws -------------
    for k in ("base", "ring", "cradle"):
        S.add(f"p_{k}", printed(mods[k], k), root, label=LABELS[k], category="printed", info=JOBS[k])
    S.add("mg996r_body", V.servo_parts(MG996R, with_horn=False), root, label="MG996R servo (base yaw)", category="actuator")
    e = ESP32_DEVKIT_38
    S.add("esp32", V.esp32_parts(e), root, matrix=V.T(cradle_m.USB_END_X, cradle_m.YC, cradle_m.PCB_BOT) @ V.Rz(180),
          label="ESP32-DevKitC (38-pin)", category="electronics")
    S.add("dcjack", V.dc_jack_parts(), root, matrix=V.T(-base_m.BX / 2, base_m.JACK_Y, base_m.JACK_Z) @ V.Rz(180),
          label="5.5 × 2.1 mm DC jack", category="power")
    S.add("cap1000", V.capacitor_parts(10, 16), root, matrix=V.T(-38, -38, -40), label="1000 µF capacitor", category="power")
    px = base_m.BX / 2 - base_m.WALL - base_m.PILLAR_D / 2 + 1.5
    py = base_m.BY / 2 - base_m.WALL - base_m.PILLAR_D / 2 + 1.5
    for sx in (-1, 1):
        for sy in (-1, 1):
            S.add("m3x50", V.screw_parts(3, 50, "pan"), root, matrix=V.T(sx * px, sy * py, 0), label="M3 × 50 wood screw (desk)",
                  category="hardware")
    import math
    ring = mods["ring"]
    for a in ring.TAB_ANG:
        S.add("m3x6", V.screw_parts(3, 6, "pan"), root,
              matrix=V.T(ring.TAB_R * math.cos(math.radians(a)), ring.TAB_R * math.sin(math.radians(a)), ring.TAB_T),
              label="M3 × 6 self-tapping (ring)", category="hardware")
    for (x, y) in cradle_m.SCREWS:
        S.add("m3x10", V.screw_parts(3, 10, "pan"), root, matrix=V.T(x, y, cradle_m.BOT + cradle_m.CBORE_DEPTH) @ V.Rx(180),
              label="M3 × 10 self-tapping (cradle)", category="hardware")

    # --- yaw ----------------------------------------------------------------------------------
    S.group("J_yaw", root)
    S.add("horn_mg996r", V.merge_by_material(V.horn_parts(MG996R)), "J_yaw", label="MG996R double-arm horn", category="actuator")
    S.add("p_turntable", printed(tt, "turntable"), "J_yaw", label=LABELS["turntable"], info=JOBS["turntable"])
    ztop = tt.Z0 + tt.DISK_T
    S.add("washer3", V.washer_parts(3, 9.0), "J_yaw", matrix=V.T(0, 0, ztop), label="M3 washer Ø9", category="hardware")
    S.add("m3x16", V.screw_parts(3, 16, "socket"), "J_yaw", matrix=V.T(0, 0, ztop + 0.5), label="M3 × 16 horn clamp screw",
          category="hardware")
    F_sh = frame((tt.XS, tt.UP_Y, tt.ZS), (1, 0, 0), (0, 1, 0))
    S.add("mg996r_body", V.servo_parts(MG996R, with_horn=False), "J_yaw", matrix=F_sh, label="MG996R servo (shoulder)",
          category="actuator")

    # --- shoulder (joint frame = shoulder servo frame) -----------------------------------------
    S.group("M_shoulder", "J_yaw", F_sh)
    S.group("J_shoulder", "M_shoulder")
    up = mods["upper"]
    S.add("horn_mg996r", V.merge_by_material(V.horn_parts(MG996R)), "J_shoulder", label="MG996R double-arm horn", category="actuator")
    S.add("p_upper", printed(up, "upper"), "J_shoulder", matrix=V.T(0, 0, lb_mg), label=LABELS["upper"], info=JOBS["upper"])
    S.add("washer3", V.washer_parts(3, 9.0), "J_shoulder", matrix=V.T(0, 0, lb_mg + up.T), label="M3 washer Ø9", category="hardware")
    S.add("m3x16", V.screw_parts(3, 16, "socket"), "J_shoulder", matrix=V.T(0, 0, lb_mg + up.T + 0.5), label="M3 × 16 horn clamp screw",
          category="hardware")
    F_el = V.T(0, 0, lb_mg) @ V.T(up.L, 0, up.T)
    S.add("mg996r_body", V.servo_parts(MG996R, with_horn=False), "J_shoulder", matrix=F_el, label="MG996R servo (elbow)",
          category="actuator")

    # --- elbow ---------------------------------------------------------------------------------
    S.group("M_elbow", "J_shoulder", F_el)
    S.group("J_elbow", "M_elbow")
    fa = mods["forearm"]
    S.add("horn_mg996r", V.merge_by_material(V.horn_parts(MG996R)), "J_elbow", label="MG996R double-arm horn", category="actuator")
    S.add("p_forearm", printed(fa, "forearm"), "J_elbow", matrix=V.T(0, 0, lb_mg), label=LABELS["forearm"], info=JOBS["forearm"])
    S.add("washer3", V.washer_parts(3, 9.0), "J_elbow", matrix=V.T(0, 0, lb_mg + fa.T), label="M3 washer Ø9", category="hardware")
    S.add("m3x16", V.screw_parts(3, 16, "socket"), "J_elbow", matrix=V.T(0, 0, lb_mg + fa.T + 0.5), label="M3 × 16 horn clamp screw",
          category="hardware")
    F_wr = V.T(0, 0, lb_mg) @ V.T(fa.L, 0, fa.T)
    S.add("sg90_body", V.servo_parts(SG90, with_horn=False), "J_elbow", matrix=F_wr, label="SG90 servo (wrist)", category="actuator")

    # --- wrist ---------------------------------------------------------------------------------
    S.group("M_wrist", "J_elbow", F_wr)
    S.group("J_wrist", "M_wrist")
    gb = mods["gripper_base"]
    S.add("horn_sg90", V.merge_by_material(V.horn_parts(SG90)), "J_wrist", label="SG90 single-arm horn", category="actuator")
    S.add("p_gripper_base", printed(gb, "gripper_base"), "J_wrist", matrix=V.T(0, 0, lb_sg), label=LABELS["gripper_base"],
          info=JOBS["gripper_base"])
    S.add("washer2", V.washer_parts(2, 6.0), "J_wrist", matrix=V.T(0, 0, lb_sg + gb.T), label="M2 washer Ø6", category="hardware")
    S.add("m2x12", V.screw_parts(2, 12, "pan"), "J_wrist", matrix=V.T(0, 0, lb_sg + gb.T + 0.5), label="M2 × 12 horn clamp screw",
          category="hardware")
    F_gr = V.T(0, 0, lb_sg) @ V.T(gb.GRIP_X, 0, gb.T)
    S.add("sg90_body", V.servo_parts(SG90, with_horn=False), "J_wrist", matrix=F_gr, label="SG90 servo (gripper)", category="actuator")

    # --- gripper -------------------------------------------------------------------------------
    S.group("M_grip", "J_wrist", F_gr)
    S.group("J_grip", "M_grip")
    jw = mods["jaw"]
    S.add("horn_sg90", V.merge_by_material(V.horn_parts(SG90)), "J_grip", label="SG90 single-arm horn", category="actuator")
    S.add("p_jaw", printed(jw, "jaw"), "J_grip", matrix=V.T(0, 0, lb_sg), label=LABELS["jaw"], info=JOBS["jaw"])
    S.add("washer2", V.washer_parts(2, 6.0), "J_grip", matrix=V.T(0, 0, lb_sg + jw.T), label="M2 washer Ø6", category="hardware")
    S.add("m2x12", V.screw_parts(2, 12, "pan"), "J_grip", matrix=V.T(0, 0, lb_sg + jw.T + 0.5), label="M2 × 12 horn clamp screw",
          category="hardware")

    size = S.export(out_dir / "robot.glb")

    # --- viewer config ---------------------------------------------------------------------------
    parts = []
    for k, job in JOBS.items():
        st = stats(job)
        parts.append({"label": LABELS[k], "job": job, "qty": 1, "hours": st.get("print_time_h"), "grams": st.get("filament_g")})
    cfg = {
        "robot": "arm", "ground_z": -40.0, "petg": "#ec6b25",
        "camera": {"pos": [420, -380, 300], "target": [90, 0, 60]},
        "joints": [
            {"node": "J_yaw", "label": "Base yaw", "sign": 1, "min": -90, "max": 90, "value": 25},
            {"node": "J_shoulder", "label": "Shoulder", "sign": -1, "min": 0, "max": 180, "value": 62},
            {"node": "J_elbow", "label": "Elbow", "sign": -1, "min": -90, "max": 90, "value": -72},
            {"node": "J_wrist", "label": "Wrist", "sign": -1, "min": -90, "max": 90, "value": -35},
            {"node": "J_grip", "label": "Gripper", "sign": 1, "min": 0, "max": 60, "value": 25},
        ],
        "demo": [[25, 62, -72, -35, 25], [-35, 40, -95, -40, 40], [-35, 30, -105, -45, 3], [-35, 70, -60, -20, 3],
                 [40, 70, -60, -20, 3], [40, 35, -100, -40, 3], [40, 35, -100, -40, 40], [25, 62, -72, -35, 25]],
        "nodes": S.meta, "printed_parts": parts, "glb_bytes": size,
        "page": {
            "title": "Desktop Robot Arm",
            "eyebrow": "MK3 AutoPrint · robot 1 of 3 · fully assembled",
            "pose_title": "Pose",
            "lede": ("A four-joint desktop arm with a gripper, printed in PETG on the MK3S. Three MG996R servos drive the base, "
                     "shoulder and elbow; two SG90s drive the wrist and the gripper. An ESP32 sits in a cradle inside the base, and "
                     "a 6 V 5 A adapter feeds the servos through a panel jack. Every part below is placed exactly where the CAD and "
                     "the assembly check put it: drag the sliders to pose it, or play the demo."),
            "meta": [["Printed parts", "8"], ["Print time", f"{sum(p['hours'] or 0 for p in parts):.1f} h"],
                     ["PETG", f"{sum(p['grams'] or 0 for p in parts):.0f} g"], ["Reach", "304 mm"]],
            "stamps": [{"text": "DFM pass", "kind": "pass"}, {"text": "Strength: proof tests", "kind": "warn"},
                       {"text": "G-code audited", "kind": "pass"}, {"text": "Awaiting your approval", "kind": "note"}],
            "facts": [["Controller", "ESP32 DevKit (38- or 30-pin) in a cradle in the base"],
                      ["Servos", "3 × MG996R (base, shoulder, elbow), 2 × SG90 (wrist, gripper)"],
                      ["Power", "6 V 5 A adapter, 5.5 × 2.1 mm jack, 1000 µF across the rail"],
                      ["Horn joints", "M3 × 16 / M2 × 12 clamp screws through each link into the spline"],
                      ["Reach", "304 mm; fingertip on the desk from 75 to 236 mm out"],
                      ["Joint ranges", "shoulder 0–180°, elbow and wrist ±90°, gripper 0–60°"],
                      ["Mounting", "screw the base down: with the arm out it tips over"],
                      ["Files", "jobs/20261025-arm-* in Matt28296/3D-Printing-Agent-Network"]],
        },
    }
    (out_dir / "robot.json").write_text(json.dumps(cfg, indent=1))
    print(f"robot.glb {size/1e6:.2f} MB, {len(S.meta)} part nodes")


if __name__ == "__main__":
    main(Path(sys.argv[1]))

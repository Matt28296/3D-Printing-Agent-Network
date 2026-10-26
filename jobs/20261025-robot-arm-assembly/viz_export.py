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
from hobby_parts import ESP32_DEVKIT_38, MG90S, MG996R, link_back_z  # noqa: E402

sys.path.insert(0, str(HERE))
import claw_frame as C  # noqa: E402

JOBS = {"base": "20261025-arm-base", "ring": "20261025-arm-turntable-ring", "turntable": "20261025-arm-turntable",
        "upper": "20261025-arm-upper-link", "forearm": "20261025-arm-forearm", "cradle": "20261025-arm-esp32-cradle",
        "claw_frame": "20261026-arm-claw-frame", "claw_cover": "20261026-arm-claw-cover",
        "claw_pinion": "20261026-arm-claw-pinion", "claw_jaw": "20261026-arm-claw-jaw",
        "camera_mount": "20261026-arm-camera-mount"}
LABELS = {"base": "Base", "ring": "Turntable support ring", "turntable": "Turntable + shoulder upright",
          "upper": "Upper link", "forearm": "Forearm", "cradle": "ESP32 cradle", "claw_frame": "Claw frame",
          "claw_cover": "Claw cover", "claw_pinion": "Claw pinion (18 teeth)", "claw_jaw": "Claw jaw (rack + finger)",
          "camera_mount": "Brio 4K camera mount"}
QTY = {"claw_jaw": 2}
# review status shown on the page (update after each gate)
STAMPS = [{"text": "Claw: in review", "kind": "warn"}, {"text": "Arm: G-code audited", "kind": "pass"},
          {"text": "Awaiting your approval", "kind": "note"}]
PAYLOAD = "20 g at full reach with the camera (strength re-check pending)"
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
    lb_mg, lb_sg = link_back_z(MG996R), link_back_z(MG90S)

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
    S.add("mg90s_body", V.servo_parts(MG90S, with_horn=False, body_mat="servo_black"), "J_elbow", matrix=F_wr,
          label="MG90S servo (wrist)", category="actuator")

    # --- wrist: claw frame on the MG90S horn (claw frame G = wrist link frame at lb) -------------
    S.group("M_wrist", "J_elbow", F_wr)
    S.group("J_wrist", "M_wrist")
    G = V.T(0, 0, lb_sg)
    S.add("horn_mg90s", V.merge_by_material(V.horn_parts(MG90S)), "J_wrist", label="MG90S single-arm horn", category="actuator")
    for k in ("claw_frame", "claw_cover", "camera_mount"):
        S.add(f"p_{k}", printed(mods[k], k), "J_wrist", matrix=G, label=LABELS[k], info=JOBS[k])
    S.add("washer2", V.washer_parts(2, 6.0), "J_wrist", matrix=G @ V.T(0, 0, C.T_W), label="M2 washer Ø6", category="hardware")
    S.add("m2x12", V.screw_parts(2, 12, "pan"), "J_wrist", matrix=G @ V.T(0, 0, C.T_W + 0.5), label="M2 × 12 wrist clamp screw",
          category="hardware")
    servo_g = G @ frame((C.X_B, 0, C.ZS), (0, 1, 0), (1, 0, 0))
    S.add("mg90s_body", V.servo_parts(MG90S, with_horn=False, body_mat="servo_black"), "J_wrist", matrix=servo_g,
          label="MG90S servo (claw)", category="actuator")
    for px in (-19.25, 8.55):
        S.add("m2x8", V.screw_parts(2, 8, "pan"), "J_wrist", matrix=servo_g @ V.T(px, 0, 2.5), label="M2 × 8 servo tab screw",
              category="hardware")
    for (x, y) in C.TOP_SCREWS:
        S.add("m3x18", V.screw_parts(3, 18, "pan", mat="black_oxide"), "J_wrist", matrix=G @ V.T(x, y, C.PAD_TOP),
              label="M3 × 18 button head (cover + camera mount)", category="hardware")
    for (y, z) in C.FRONT_SCREWS:
        S.add("m3x12", V.screw_parts(3, 12, "pan", mat="black_oxide"), "J_wrist", matrix=G @ V.T(C.X_F1, y, z) @ V.Ry(90),
              label="M3 × 12 self-tapping (cover front)", category="hardware")
    cam = G @ V.T(C.CAM_XC, 0, C.CAM_ZC) @ V.Ry(C.CAM_TILT)
    S.add("brio", V.brio4k_parts(), "J_wrist", matrix=cam, label="Logitech Brio 4K webcam (clip removed)", category="electronics")
    S.add("thumb14", V.thumb_screw_parts(), "J_wrist", matrix=cam @ V.T(0, 0, -C.SEAT_T),
          label='1/4"-20 × 3/8" knurled thumb screw', category="hardware")

    # --- claw: pinion turns, jaws slide (one "Claw" control drives all three) --------------------
    S.group("J_pinion", "J_wrist", G @ frame((C.X_P0, 0, C.ZS), (0, 0, 1), (1, 0, 0)))
    S.add("p_claw_pinion", printed(mods["claw_pinion"], "claw_pinion"), "J_pinion", label=LABELS["claw_pinion"],
          info=JOBS["claw_pinion"])
    lbz = link_back_z(MG90S)        # pinion back face in the servo frame: the horn's face sits 2 mm in
    S.add("horn_trim", V.trimmed_horn_parts(C.PINION_HORN, C.HORN_TRIM_R), "J_pinion", matrix=V.T(0, 0, -lbz),
          label="MG90S double-arm horn, arms cut to 5.5 mm", category="actuator")
    S.add("m2x10", V.screw_parts(2, 10, "pan"), "J_pinion", matrix=V.T(0, 0, C.FACE_W - 1.6),
          label="M2 × 10 pinion clamp screw", category="hardware")
    S.group("J_jawA", "J_wrist", G)
    S.add("p_claw_jaw", printed(mods["claw_jaw"], "claw_jaw"), "J_jawA", label=LABELS["claw_jaw"] + " A", info=JOBS["claw_jaw"])
    turn_b = V.T(0, 0, C.ZS) @ V.Rx(180) @ V.T(0, 0, -C.ZS)
    S.group("M_jawB", "J_wrist", G @ turn_b)
    S.group("J_jawB", "M_jawB")
    S.add("p_claw_jaw", printed(mods["claw_jaw"], "claw_jaw"), "J_jawB", label=LABELS["claw_jaw"] + " B", info=JOBS["claw_jaw"])

    size = S.export(out_dir / "robot.glb")

    # --- viewer config ---------------------------------------------------------------------------
    parts = []
    for k, job in JOBS.items():
        st = stats(job)
        parts.append({"label": LABELS[k], "job": job, "qty": QTY.get(k, 1), "hours": st.get("print_time_h"),
                      "grams": st.get("filament_g")})
    cfg = {
        "robot": "arm", "ground_z": -40.0, "petg": "#ec6b25",
        "camera": {"pos": [420, -380, 300], "target": [90, 0, 60]},
        "joints": [
            {"node": "J_yaw", "label": "Base yaw", "sign": 1, "min": -90, "max": 90, "value": 25},
            {"node": "J_shoulder", "label": "Shoulder", "sign": -1, "min": 0, "max": 180, "value": 62},
            {"node": "J_elbow", "label": "Elbow", "sign": -1, "min": -90, "max": 90, "value": -72},
            {"node": "J_wrist", "label": "Wrist", "sign": -1, "min": -90, "max": 90, "value": -35},
            {"node": "J_claw", "label": "Claw", "unit": "mm", "min": 0, "max": 44, "value": 20,
             "drives": [{"node": "J_pinion", "rot": round(C.DEG_PER_MM_GAP, 4)},
                        {"node": "J_jawA", "move": [0, -0.5, 0]}, {"node": "J_jawB", "move": [0, -0.5, 0]}]},
        ],
        "demo": [[25, 62, -72, -35, 20], [-35, 40, -95, -40, 40], [-35, 30, -105, -45, 8], [-35, 70, -60, -20, 8],
                 [40, 70, -60, -20, 8], [40, 35, -100, -40, 8], [40, 35, -100, -40, 40], [25, 62, -72, -35, 20]],
        "nodes": S.meta, "printed_parts": parts, "glb_bytes": size,
        "page": {
            "title": "Desktop Robot Arm",
            "eyebrow": "MK3 AutoPrint · robot 1 of 3 · fully assembled",
            "pose_title": "Pose",
            "lede": ("A four-joint desktop arm with a parallel claw and a wrist camera, printed in PETG on the MK3S. Three "
                     "MG996R servos drive the base, shoulder and elbow; two MG90S drive the wrist and the claw, whose pinion "
                     "slides two racks so the fingers stay parallel. A Logitech Brio 4K rides on the claw, tilted 30° at the "
                     "fingertips, and plugs into your PC; an ESP32 in the base drives the servos. Every part is placed where the "
                     "CAD and the assembly check put it: drag the sliders to pose it, or play the demo."),
            "meta": [["Printed parts", str(sum(p["qty"] for p in parts))],
                     ["Print time", f"{sum(p['hours'] or 0 for p in parts):.1f} h"],
                     ["PETG", f"{sum(p['grams'] or 0 for p in parts):.0f} g"], ["Reach", "284 mm"]],
            "stamps": STAMPS,
            "facts": [["Controller", "ESP32 DevKit (38- or 30-pin) in a cradle in the base"],
                      ["Servos", "3 × MG996R (base, shoulder, elbow), 2 × MG90S (wrist, claw)"],
                      ["Claw", "rack and pinion, fingers stay parallel; 0–44 mm, ≈12 N per finger at stall"],
                      ["Camera", "Brio 4K on the claw, 30° down at the fingertips; USB to your PC, not the ESP32"],
                      ["Power", "6 V 5 A adapter, 5.5 × 2.1 mm jack, 1000 µF across the rail"],
                      ["Reach", "284 mm; fingertip on the desk from 76 to 260 mm out"],
                      ["Joint ranges", "shoulder 0–180°, elbow and wrist ±90°, claw 0–44 mm"],
                      ["Payload", PAYLOAD],
                      ["Mounting", "screw the base down: with the arm out it tips over"],
                      ["Files", "jobs/2026102*-arm-* in Matt28296/3D-Printing-Agent-Network"]],
        },
    }
    (out_dir / "robot.json").write_text(json.dumps(cfg, indent=1))
    print(f"robot.glb {size/1e6:.2f} MB, {len(S.meta)} part nodes")


if __name__ == "__main__":
    main(Path(sys.argv[1]))

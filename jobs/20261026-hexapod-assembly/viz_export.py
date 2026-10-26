"""Export the fully built hexapod (printed parts + every bought part) as a GLB with a joint
hierarchy per leg, plus the viewer config (gait, parts list, page text).

Run from the project root:  .venv/bin/python jobs/20261026-hexapod-assembly/viz_export.py <out_dir>
Writes <out_dir>/robot.glb and <out_dir>/robot.json.
Leg hierarchy (frames as in assembly_check.leg_frames, neutral stance = every joint node at 0):
  M_coxa{i} (static, coxa joint frame) → J_coxa{i} (turns) → coxa bracket, femur servo,
  M_femur{i} → J_femur{i} → femur, tibia servo, M_tibia{i} (with the tibia's -90°) → J_tibia{i} → tibia.
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
from hobby_parts import ESP32_DEVKIT_38, LIPO_2S_1000  # noqa: E402
import hex_frame as H  # noqa: E402

JOBS = {"bottom": "20261026-hexapod-body-bottom", "top": "20261026-hexapod-body-top",
        "coxa": "20261026-hexapod-coxa", "femur": "20261026-hexapod-femur", "tibia": "20261026-hexapod-tibia"}
LABELS = {"bottom": "Bottom body plate", "top": "Top plate / electronics deck", "coxa": "Coxa bracket",
          "femur": "Femur", "tibia": "Tibia"}
QTY = {"bottom": 1, "top": 1, "coxa": 6, "femur": 6, "tibia": 6}
PETG = "petg_white"
STAMPS = [{"text": "Round 2 in review", "kind": "warn"}, {"text": "Assembly check clean", "kind": "pass"},
          {"text": "Not sliced yet", "kind": "note"}]
LEG_NAMES = ["left front", "left middle", "left rear", "right front", "right middle", "right rear"]


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
    top = mods["top"]
    S = V.VizScene()
    root = S.group("hexapod")
    zt = H.STANCE_Z_TAB
    z0 = H.T_BODY + H.COLUMN_H                         # top plate underside above the tab plane

    # --- body ------------------------------------------------------------------------------
    S.add("p_bottom", printed(mods["bottom"]), root, matrix=V.T(0, 0, zt), label=LABELS["bottom"], info=JOBS["bottom"])
    S.add("p_top", printed(top), root, matrix=V.T(0, 0, zt + z0), label=LABELS["top"], info=JOBS["top"])
    lp = LIPO_2S_1000
    S.add("lipo", V.lipo_parts(lp.length, lp.width, lp.height), root, matrix=V.T(0, 0, zt + H.T_BODY),
          label="2S 1000 mAh LiPo", category="power")
    S.add("ubec", V.ubec_parts(), root, matrix=V.T(-11.5, 31.0, zt + H.T_BODY + 10.0) @ V.Rx(90),
          label="6 V 5 A UBEC (on its side beside the LiPo)", category="power")
    zdeck = zt + z0 + H.T_TOP
    e = ESP32_DEVKIT_38
    S.add("esp32", V.esp32_parts(e), root, matrix=V.T(top.USB_END_X, 0, zdeck + top.LEDGE_H),
          label="ESP32-DevKitC (38-pin)", category="electronics")
    for s in (1, -1):
        S.add("pca9685", V.pca9685_parts(), root, matrix=V.T(0, s * top.PCA_Y, zdeck + top.POST_H) @ V.Rz(0 if s > 0 else 180),
              label=f"PCA9685 servo driver ({'0x40' if s > 0 else '0x41'})", category="electronics")
    S.add("buck", V.buck_parts(), root, matrix=V.T(40.0, 0, zdeck) @ V.Rz(90), label="MP1584 buck, set to 5.0 V",
          category="power")
    S.add("cap1000", V.capacitor_parts(10, 16), root, matrix=V.T(-40.0, 0, zdeck), label="1000 µF capacitor", category="power")
    for (x, y) in H.COLUMNS:
        S.add("m3x8", V.screw_parts(3, 8, "pan"), root, matrix=V.T(x, y, zdeck), label="M3 × 8 self-tapping (top plate)",
              category="hardware")

    # --- legs --------------------------------------------------------------------------------
    gait_legs = []
    for i, (mx, my, a) in enumerate(H.LEG_MOUNTS):
        S0 = frame((mx, my, zt), (math.cos(math.radians(a)), math.sin(math.radians(a)), 0), (0, 0, -1))
        S.add("mg90s_body", V.servo_parts(H.SERVO, with_horn=False, body_mat="servo_black"), root, matrix=S0,
              label="MG90S servo (coxa)", category="actuator")
        S.group(f"M_coxa{i}", root, S0 @ V.T(0, 0, H.LB))
        S.group(f"J_coxa{i}", f"M_coxa{i}")
        jc = f"J_coxa{i}"
        S.add("horn_mg90s", V.merge_by_material(V.horn_parts(H.SERVO)), jc, matrix=V.T(0, 0, -H.LB), label="MG90S single-arm horn",
              category="actuator")
        S.add("p_coxa", printed(mods["coxa"]), jc, label=LABELS["coxa"], info=JOBS["coxa"])
        S.add("washer2", V.washer_parts(2, 6.0), jc, matrix=V.T(0, 0, H.T_C), label="M2 washer Ø6", category="hardware")
        S.add("m2x10", V.screw_parts(2, 10, "pan"), jc, matrix=V.T(0, 0, H.T_C + 0.5), label="M2 × 10 horn clamp screw (coxa)",
              category="hardware")
        S1 = frame((H.L_C, H.Y_F, H.Z_F), (1, 0, 0), (0, 1, 0))
        S.add("mg90s_body", V.servo_parts(H.SERVO, with_horn=False, body_mat="servo_black"), jc, matrix=S1,
              label="MG90S servo (femur)", category="actuator")
        S.group(f"M_femur{i}", jc, S1 @ V.T(0, 0, H.LB))
        S.group(f"J_femur{i}", f"M_femur{i}")
        jf = f"J_femur{i}"
        S.add("horn_mg90s", V.merge_by_material(V.horn_parts(H.SERVO)), jf, matrix=V.T(0, 0, -H.LB), label="MG90S single-arm horn",
              category="actuator")
        S.add("p_femur", printed(mods["femur"]), jf, label=LABELS["femur"], info=JOBS["femur"])
        S.add("washer2", V.washer_parts(2, 6.0), jf, matrix=V.T(0, 0, H.T_F), label="M2 washer Ø6", category="hardware")
        S.add("m2x12", V.screw_parts(2, 12, "pan"), jf, matrix=V.T(0, 0, H.T_F + 0.5), label="M2 × 12 horn clamp screw",
              category="hardware")
        S2 = V.T(H.L_F, 0, H.T_F)
        S.add("mg90s_body", V.servo_parts(H.SERVO, with_horn=False, body_mat="servo_black"), jf, matrix=S2,
              label="MG90S servo (tibia)", category="actuator")
        S.group(f"M_tibia{i}", jf, S2 @ V.T(0, 0, H.LB) @ V.Rz(-90))
        S.group(f"J_tibia{i}", f"M_tibia{i}")
        jt = f"J_tibia{i}"
        S.add("horn_mg90s", V.merge_by_material(V.horn_parts(H.SERVO)), jt, matrix=V.T(0, 0, -H.LB), label="MG90S single-arm horn",
              category="actuator")
        S.add("p_tibia", printed(mods["tibia"]), jt, label=LABELS["tibia"], info=JOBS["tibia"])
        S.add("washer2", V.washer_parts(2, 6.0), jt, matrix=V.T(0, 0, H.T_T), label="M2 washer Ø6", category="hardware")
        S.add("m2x12", V.screw_parts(2, 12, "pan"), jt, matrix=V.T(0, 0, H.T_T + 0.5), label="M2 × 12 horn clamp screw",
              category="hardware")
        # tripod gait: legs 0, 2, 4 (left front, left rear, right middle) swing together, 1, 3, 5 half a cycle later
        left = my > 0
        gait_legs.append({"coxa": jc, "femur": jf, "tibia": jt, "dir": 1 if left else -1,
                          "tripod": i in (1, 3, 5), "show": i == 1, "name": LEG_NAMES[i]})

    size = S.export(out_dir / "robot.glb")
    parts = []
    for k, job in JOBS.items():
        st = stats(job)
        parts.append({"label": LABELS[k], "job": job, "qty": QTY[k], "hours": st.get("print_time_h"),
                      "grams": st.get("filament_g")})
    cfg = {
        "robot": "hexapod", "ground_z": 0.0, "petg": "#e8e6e0",
        "camera": {"pos": [380, -420, 330], "target": [0, 0, 80]},
        "joints": [
            {"node": "J_coxa1", "label": "Coxa", "sign": 1, "min": -45, "max": 45, "value": 0},
            {"node": "J_femur1", "label": "Femur", "sign": 1, "min": -70, "max": 90, "value": 0},
            {"node": "J_tibia1", "label": "Tibia", "sign": 1, "min": -80, "max": 90, "value": 0},
        ],
        "gait": {"period": 1.6, "swing": 14, "lift": 24, "tuck": 18, "legs": gait_legs},
        "nodes": S.meta, "printed_parts": parts, "glb_bytes": size,
        "page": {
            "title": "Hexapod",
            "eyebrow": "MK3 AutoPrint · robot 3 of 3 · fully assembled",
            "pose_title": "Legs",
            "lede": ("A six-legged walker printed in PETG: 18 MG90S metal-gear servos, three per leg, driven by two PCA9685 boards "
                     "and an ESP32 on the top deck, with a 2S LiPo between the body plates. Press Walk for a tripod gait in place, "
                     "or stop it and pose the left middle leg with the sliders."),
            "meta": [["Printed parts", str(sum(QTY.values()))], ["Print time", f"{sum(p['hours'] or 0 for p in parts):.1f} h"],
                     ["PETG", f"{sum(p['grams'] or 0 for p in parts):.0f} g"], ["Stance", "277 × 282 × 160 mm"]],
            "stamps": STAMPS,
            "facts": [["Controller", "ESP32 DevKit + 2 × PCA9685 (0x40, 0x41) on I²C"],
                      ["Servos", "18 × MG90S: coxa, femur, tibia per leg"],
                      ["Legs", f"coxa {H.L_C:.0f} mm, femur {H.L_F:.0f} mm, tibia {H.L_T:.0f} mm"],
                      ["Power", "2S 1000 mAh LiPo; 6 V 5 A UBEC for the servos, MP1584 5 V for the ESP32"],
                      ["Ground clearance", "≈49 mm under the body in the neutral stance"],
                      ["Joint ranges", "coxa ±45°, femur −70…+90°, tibia −170…0° (assembly check)"],
                      ["Files", "jobs/20261026-hexapod-* in Matt28296/3D-Printing-Agent-Network"]],
        },
    }
    (out_dir / "robot.json").write_text(json.dumps(cfg, indent=1))
    print(f"robot.glb {size/1e6:.2f} MB, {len(S.meta)} part nodes")


if __name__ == "__main__":
    main(Path(sys.argv[1]))

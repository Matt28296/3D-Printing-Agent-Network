"""Export the fully built hexapod (printed parts + every bought part) as a GLB with a joint
hierarchy per leg, plus the viewer config (gait, parts list, page text).

Run from the project root:  .venv/bin/python jobs/20261026-hexapod-assembly/viz_export.py <out_dir>
Writes <out_dir>/robot.glb and <out_dir>/robot.json.
Leg hierarchy (frames from hex_frame.leg_frames; joint nodes at 0 = servo centre, femur level, tibia
perpendicular; the export starts every leg in the walking stance hex_frame.NEUTRAL_*):
  M_coxa{i} (static, coxa joint frame) → J_coxa{i} (turns) → coxa bracket, femur servo,
  M_femur{i} → J_femur{i} → femur, tibia servo, M_tibia{i} (with the tibia's -90°) → J_tibia{i} → tibia.
The gait is the firmware's straight-line tripod gait (hex_frame.gait_pose, 30 mm stride, 20 mm lift),
exported as joint keyframes for every leg, one cycle in 0.5 s (20 frames of 25 ms).
Round 3: coxa and tibia servos are mounted reversed (B1 option 2), the femur servo normally with its
lead through the notch (option 1); each servo's lead leaves its case at the shaft end.
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
STAMPS = [{"text": "Awaiting your approval", "kind": "pass"}, {"text": "Assembly check clean", "kind": "pass"},
          {"text": "Sliced and audited", "kind": "pass"}]
LEG_NAMES = ["left front", "left middle", "left rear", "right front", "right middle", "right rear"]
GAIT_STRIDE, GAIT_LIFT, FRAME_S = 30.0, 20.0, 0.025
RESLICE = ()   # every part was re-sliced on 26 Oct 2026 after round 4; list a part here again if its geometry changes
               # after its last slice (slice_stats.json has no STL hash).
UBEC_AT = (0.0, 22.5)            # as assembly_check.py: x centre, y of its LiPo-side face (on its side)


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


def servo_body():
    """MG90S without horn or tab screws; its lead leaves the case at the SHAFT end (deep review 01, B1)."""
    s = H.SERVO
    parts = V.servo_parts(s, with_horn=False, with_screws=False, lead_len=0.0, body_mat="servo_black")
    x1, zl = s.shaft_from_end, -s.tab_height + s.lead_z
    for i, c in enumerate(("wire_brown", "wire_red", "wire_orange")):
        yy = (i - 1) * 1.15
        parts.append(V.box(x1 - 0.5, x1 + 24.0, yy - 0.5, yy + 0.5, zl - 0.5, zl + 0.5, c))
    return V.merge_by_material(parts)


def pilots(shift=0.0):
    s = H.SERVO
    xm = -(s.length - s.shaft_from_end) + s.length / 2
    return [xm - s.hole_dx / 2, xm + s.hole_dx / 2 + shift]


def main(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    mods = {k: load(v) for k, v in JOBS.items()}
    top = mods["top"]
    S = V.VizScene()
    root = S.group("hexapod")
    zp = H.STANCE_Z_PU                                  # bottom-plate underside in the stance
    z0 = H.T_BODY + H.COLUMN_H                          # top plate underside above the plate underside
    servo = servo_body()

    # --- body ------------------------------------------------------------------------------
    S.add("p_bottom", printed(mods["bottom"]), root, matrix=V.T(0, 0, zp), label=LABELS["bottom"], info=JOBS["bottom"])
    S.add("p_top", printed(top), root, matrix=V.T(0, 0, zp + z0), label=LABELS["top"], info=JOBS["top"])
    lp = LIPO_2S_1000
    S.add("lipo", V.lipo_parts(lp.length, lp.width, lp.height), root, matrix=V.T(0, 0, zp + H.T_BODY),
          label="2S 1000 mAh LiPo", category="power")
    S.add("ubec", V.ubec_parts(), root, matrix=V.T(UBEC_AT[0], UBEC_AT[1] + 9.0, zp + H.T_BODY + 10.0) @ V.Rx(90),
          label="UBEC, on its side beside the LiPo", category="power")
    zdeck = zp + z0 + H.T_TOP
    e = ESP32_DEVKIT_38
    S.add("esp32", V.esp32_parts(e), root, matrix=V.T(top.USB_END_X, 0, zdeck + top.LEDGE_H),
          label="ESP32-DevKitC (38-pin)", category="electronics")
    for s in (1, -1):
        S.add("pca9685", V.pca9685_parts(), root, matrix=V.T(0, s * top.PCA_Y, zdeck + top.POST_H) @ V.Rz(0 if s > 0 else 180),
              label=f"PCA9685 servo driver ({'0x40' if s > 0 else '0x41'})", category="electronics")
    S.add("buck", V.buck_parts(), root, matrix=V.T(40.0, 0, zdeck) @ V.Rz(90), label="MP1584 buck, set to 5.0 V",
          category="power")
    S.add("cap1000", V.capacitor_parts(10, 16), root, matrix=V.T(-36.0, 0, zdeck), label="1000 µF capacitor", category="power")
    S.add("switch", V.toggle_switch_parts(), root, matrix=V.T(*top.SWITCH_XY, zdeck) @ V.Ry(-90),
          label="Main switch in the deck (12 mm toggle, ≥ 10 A DC)", category="power")
    for (x, y) in H.COLUMNS:
        S.add("m3x8", V.screw_parts(3, 8, "pan"), root, matrix=V.T(x, y, zdeck), label="M3 × 8 self-tapping (top plate)",
              category="hardware")

    # --- legs --------------------------------------------------------------------------------
    f_s, t_s = H.NEUTRAL_FEMUR, H.NEUTRAL_TIBIA
    gait_legs, frames = [], []
    gait = [H.gait_pose(k, GAIT_STRIDE, GAIT_LIFT)[0] for k in range(H.CYCLE_FRAMES)]
    for i, (mx, my, a) in enumerate(H.LEG_MOUNTS):
        S0 = frame((mx, my, zp + H.S0_Z), (math.cos(math.radians(a)), math.sin(math.radians(a)), 0), (0, 0, -1))
        S.add("mg90s_body", servo, root, matrix=S0, label="MG90S servo (coxa, mounted reversed)", category="actuator")
        for px in pilots():      # coxa tabs: M2 × 14 from below, washer + Nyloc on the tab inside the body (round 4)
            S.add("washer2_5", V.washer_parts(2, 5.0, 0.3), root, matrix=S0 @ V.T(px, 0, H.S0_Z), label="M2 washer", category="hardware")
            S.add("m2x14", V.screw_parts(2, 14, "pan"), root, matrix=S0 @ V.T(px, 0, H.S0_Z + 0.3),
                  label="M2 × 14 machine screw (coxa servo tab, snug)", category="hardware")
            S.add("washer2_5", V.washer_parts(2, 5.0, 0.3), root, matrix=S0 @ V.T(px, 0, 0) @ V.Rx(180), label="M2 washer",
                  category="hardware")
            S.add("nyloc2", V.nut_parts(2.0, nyloc=True), root, matrix=S0 @ V.T(px, 0, -0.3) @ V.Rx(180), label="M2 Nyloc nut",
                  category="hardware")
        S.group(f"M_coxa{i}", root, S0 @ V.T(0, 0, H.LB))
        S.group(f"J_coxa{i}", f"M_coxa{i}")
        jc = f"J_coxa{i}"
        S.add("horn_mg90s", V.merge_by_material(V.horn_parts(H.SERVO)), jc, matrix=V.T(0, 0, -H.LB), label="MG90S single-arm horn",
              category="actuator")
        S.add("p_coxa", printed(mods["coxa"]), jc, label=LABELS["coxa"], info=JOBS["coxa"])
        S.add("washer_penny", V.washer_parts(2, 10.0, 1.0), jc, matrix=V.T(0, 0, H.T_C), label="M3 penny washer Ø10 × 1",
              category="hardware")
        S.add("m2x12", V.screw_parts(2, 12, "pan"), jc, matrix=V.T(0, 0, H.T_C + 1.0), label="M2 × 12 horn clamp screw (coxa)",
              category="hardware")
        S1 = frame((H.L_C, H.S1_Y, H.Z_F), (1, 0, 0), (0, 1, 0))
        S.add("mg90s_body", servo, jc, matrix=S1, label="MG90S servo (femur)", category="actuator")
        for px in pilots(1.3):   # option 1: the outboard pilot sits 1.3 mm further out
            S.add("m2x10", V.screw_parts(2, 10, "pan"), jc, matrix=S1 @ V.T(px, 0, H.TAB_T),
                  label="M2 × 10 self-tapping (femur servo tab)", category="hardware")
        S.group(f"M_femur{i}", jc, S1 @ V.T(0, 0, H.LB))
        S.group(f"J_femur{i}", f"M_femur{i}", V.Rz(f_s))
        jf = f"J_femur{i}"
        S.add("horn_mg90s", V.merge_by_material(V.horn_parts(H.SERVO)), jf, matrix=V.T(0, 0, -H.LB), label="MG90S single-arm horn",
              category="actuator")
        S.add("p_femur", printed(mods["femur"]), jf, label=LABELS["femur"], info=JOBS["femur"])
        S.add("washer2", V.washer_parts(2, 6.0), jf, matrix=V.T(0, 0, H.T_F), label="M2 washer Ø6", category="hardware")
        S.add("m2x12", V.screw_parts(2, 12, "pan"), jf, matrix=V.T(0, 0, H.T_F + 0.5), label="M2 × 12 horn clamp screw",
              category="hardware")
        S2 = V.T(H.L_F, 0, H.S2_Z)
        S.add("mg90s_body", servo, jf, matrix=S2, label="MG90S servo (tibia, mounted reversed)", category="actuator")
        for px in pilots():      # reversed: screw heads on the tabs' case side
            S.add("m2x8", V.screw_parts(2, 8, "pan"), jf, matrix=S2 @ V.T(px, 0, 0) @ V.Rx(180),
                  label="M2 × 8 self-tapping (tibia servo tab)", category="hardware")
        S.group(f"M_tibia{i}", jf, S2 @ V.T(0, 0, H.LB) @ V.Rz(-90))
        S.group(f"J_tibia{i}", f"M_tibia{i}", V.Rz(t_s))
        jt = f"J_tibia{i}"
        S.add("horn_mg90s", V.merge_by_material(V.horn_parts(H.SERVO)), jt, matrix=V.T(0, 0, -H.LB), label="MG90S single-arm horn",
              category="actuator")
        S.add("p_tibia", printed(mods["tibia"]), jt, label=LABELS["tibia"], info=JOBS["tibia"])
        S.add("washer2", V.washer_parts(2, 6.0), jt, matrix=V.T(0, 0, H.T_T), label="M2 washer Ø6", category="hardware")
        S.add("m2x12", V.screw_parts(2, 12, "pan"), jt, matrix=V.T(0, 0, H.T_T + 0.5), label="M2 × 12 horn clamp screw",
              category="hardware")
        gait_legs.append({"coxa": jc, "femur": jf, "tibia": jt, "dir": 1 if my > 0 else -1,
                          "tripod": i in H.TRIPOD_B, "show": i == 1, "name": LEG_NAMES[i]})
        frames.append([[round(c, 2), round(f, 2), round(t + 90.0, 2)] for (c, f, t) in (g[i] for g in gait)])

    size = S.export(out_dir / "robot.glb")
    parts = []
    for k, job in JOBS.items():
        st = {} if k in RESLICE else stats(job)
        plan = ROOT / "jobs" / job / "slice_plan.json"
        per = json.loads(plan.read_text()).get("copies", 1) if plan.exists() else 1
        parts.append({"label": LABELS[k], "job": job, "qty": QTY[k], "plates": -(-QTY[k] // per),
                      "hours": st.get("print_time_h"), "grams": st.get("filament_g")})   # per plate
    sliced = all(p["hours"] is not None for p in parts)
    chk = json.loads((HERE / "assembly_check.json").read_text())
    lim = chk["joint_limits"]
    ov = chk["stance"]["overall_mm"]
    cfg = {
        "robot": "hexapod", "ground_z": 0.0, "petg": "#e8e6e0",
        "camera": {"pos": [380, -420, 330], "target": [0, 0, 80]},
        "joints": [
            {"node": "J_coxa1", "label": "Coxa", "sign": 1, "min": lim["coxa"]["free_sweep"][0],
             "max": lim["coxa"]["free_sweep"][1], "value": 0},
            {"node": "J_femur1", "label": "Femur", "sign": 1, "min": lim["femur"]["free_sweep"][0],
             "max": lim["femur"]["free_sweep"][1], "value": round(f_s)},
            {"node": "J_tibia1", "label": "Tibia", "sign": 1, "min": lim["tibia"]["free_sweep"][0],
             "max": lim["tibia"]["free_sweep"][1], "value": round(t_s)},
        ],
        "gait": {"period": H.CYCLE_FRAMES * FRAME_S, "stride_mm": GAIT_STRIDE, "lift_mm": GAIT_LIFT,
                 "frames": frames, "legs": gait_legs},
        "nodes": S.meta, "printed_parts": parts, "glb_bytes": size,
        "page": {
            "title": "Hexapod",
            "eyebrow": "MK3 AutoPrint · robot 3 of 3 · fully assembled",
            "pose_title": "Legs",
            "lede": ("A six-legged walker printed in PETG: 18 MG90S metal-gear servos, three per leg, driven by two PCA9685 boards "
                     "and an ESP32 on the top deck, with a 2S LiPo between the body plates. Press Walk for the straight-line "
                     f"tripod gait in place ({GAIT_STRIDE:.0f} mm stride, {GAIT_LIFT:.0f} mm lift, the tibias tucked "
                     f"{-(f_s + t_s):.1f}° in), or stop it and pose the left middle leg with the sliders."),
            "meta": [["Printed parts", str(sum(QTY.values()))],
                     ["Print time", f"{sum(p['hours'] * p['plates'] for p in parts):.1f} h" if sliced else "re-slice pending"],
                     ["PETG", f"{sum(p['grams'] * p['plates'] for p in parts):.0f} g" if sliced else "re-slice pending"],
                     ["Stance", f"{ov[0]:.0f} × {ov[1]:.0f} × {ov[2]:.0f} mm"]],
            "stamps": STAMPS,
            "facts": [["Controller", "ESP32 DevKit + 2 × PCA9685 (0x40, 0x41) on I²C"],
                      ["Servos", "18 × MG90S: coxa, femur, tibia per leg"],
                      ["Legs", f"coxa {H.L_C:.0f} mm, femur {H.L_F:.0f} mm, tibia {H.L_T:.0f} mm"],
                      ["Mass", "≈ 0.91 kg (round 4: solid coxa brackets, bigger bottom plate)"],
                      ["Power", "2S 1000 mAh LiPo; 6 V UBEC for the servos, MP1584 5 V for the ESP32"],
                      ["Ground clearance", f"≈ {chk['stance']['lowest_point_mm'][0]:.0f} mm under the coxa brackets; "
                                           f"the body plate is {H.STANCE_Z_PU:.0f} mm up"],
                      ["Joint ranges", f"coxa {lim['coxa']['free_sweep'][0]}…{lim['coxa']['free_sweep'][1]}°, femur "
                                       f"{lim['femur']['free_sweep'][0]}…{lim['femur']['free_sweep'][1]}°, tibia "
                                       f"{lim['tibia']['free_sweep'][0]}…{lim['tibia']['free_sweep'][1]}° (assembly check)"],
                      ["Files", "jobs/20261026-hexapod-* in Matt28296/3D-Printing-Agent-Network"]],
        },
    }
    (out_dir / "robot.json").write_text(json.dumps(cfg, indent=1))
    print(f"robot.glb {size/1e6:.2f} MB, {len(S.meta)} part nodes")


if __name__ == "__main__":
    main(Path(sys.argv[1]))

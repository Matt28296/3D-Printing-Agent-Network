"""Gravity torque budget and payload by reach for the desktop robot arm (deep review 03 SYS-02 /
SYS-04 method, re-run for the round-3 claw and the -150..+30 elbow window).

Mass model:
- printed parts: CAD volume x PETG 1.27 g/cm³ ("solid", the upper bound), and the same volume
  x each job's sliced/solid ratio from its last slice ("sliced est.": the claw parts were
  redesigned after slicing, so their ratio comes from the old geometry); centre of mass from
  the CAD solid;
- bought parts and allowances as deep review 03 assumed: MG996R 55 g, MG90S 13.4 g, Brio 63 g
  (box centre), horn + clamp per MG996R joint 4.2 g, wrist horn + clamp 1.2 g, pinion horn +
  screw 1.0 g, claw and mount screws 5 g, thumb screw 5 g, cable on the claw / forearm / upper
  link 5 / 7 / 9 g with the camera, 2 / 3 / 5 g without;
- payload 10 mm behind the fingertips, on the claw axis.
Torques: static gravity torque about each pitch axis from everything beyond it (yaw 0), over
the servo travel in 5° steps. Limits from the 6 V stall (MG996R 1079 N·mm, MG90S 216 N·mm):
<= 50 % for short holds, x1.3 while moving, <= 1/3 for continuous holding.
Overhung moments (SYS-04): weight beyond each pitch joint about the servo's case-top plane,
perpendicular to the shaft (the same in every pose, because gravity is always across the shafts).

Run from the project root:  .venv/bin/python jobs/20261025-robot-arm-assembly/torque_budget.py
Writes torque_budget.json.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(HERE))
import assembly_check as AC  # noqa: E402
import claw_frame as C  # noqa: E402
from build123d import CenterOf  # noqa: E402
from hobby_parts import BRIO_4K, MG90S, MG996R, _body_x0  # noqa: E402

RHO = 1.27e-3                 # g/mm³
GN = 9.81e-3                  # N per g
STALL = {"shoulder": 1079.0, "elbow": 1079.0, "wrist": 216.0}
MOVING = 1.3
PRINTED = ["upper", "forearm", "claw_frame", "claw_cover", "claw_pinion", "claw_jaw", "claw_jaw_b", "camera_mount"]
BEYOND = {"shoulder": ["upper", "servo_elbow", "forearm", "servo_wrist"] + ["claw"],
          "elbow": ["forearm", "servo_wrist", "claw"], "wrist": ["claw"]}
CLAW = ["claw_frame", "claw_cover", "claw_pinion", "claw_jaw", "claw_jaw_b", "camera_mount", "servo_grip", "brio"]
# sliced/solid ratio of each job's last slice (filament per copy / (old CAD volume x 1.27))
SLICED_RATIO = {"upper": 0.672, "forearm": 0.672, "claw_frame": 0.748, "claw_cover": 0.920, "claw_pinion": 1.035,
                "claw_jaw": 0.946, "claw_jaw_b": 0.946, "camera_mount": 0.999}
# links round 5: the 6 mm back-face rail ribs (upper link +4.6 cm³, forearm +3.6 cm³ incl. its cross-rib) print about 80 %
# dense (5 perimeters a side on a 6.6-6.85 mm rib, 40 % gyroid core), against the plates' 0.672 from the round-2 slice:
# about 0.685 for each whole link until it is sliced again
SLICED_RATIO.update({"upper": 0.685, "forearm": 0.685})


def servo_com(s):
    return np.array([_body_x0(s) + s.length / 2, 0.0, -s.tab_height + s.case_top / 2, 1.0])


_PROPS: dict[str, tuple[float, np.ndarray]] = {}


def props(mods, k):
    """(volume mm³, centre of mass in the part's design frame) of a printed part, cached."""
    src = "claw_jaw" if k == "claw_jaw_b" else k
    if src not in _PROPS:
        part = mods[src].design()
        com = part.center(CenterOf.MASS)
        _PROPS[src] = (part.volume, np.array([com.X, com.Y, com.Z, 1.0]))
    return _PROPS[src]


def masses(mods, mass_model, camera):
    """[(body key, mass g, com in that body's frame)]"""
    items = []
    for k in PRINTED:
        if k == "camera_mount" and not camera:
            continue
        vol, com = props(mods, k)
        items.append((k, vol * RHO * (SLICED_RATIO[k] if mass_model == "sliced est." else 1.0), com))
    items += [("servo_elbow", MG996R.mass_g, servo_com(MG996R)), ("servo_wrist", MG90S.mass_g, servo_com(MG90S)),
              ("servo_grip", MG90S.mass_g, servo_com(MG90S))]
    # allowances, in the frame of the body they ride on
    lb = (mods["upper"].T + 0.0)
    items += [("forearm", 4.2, np.array([0.0, 0.0, -2.0, 1.0])),                 # elbow horn + clamp (on the axis)
              ("claw_frame", 1.2, np.array([0.0, 0.0, 2.0, 1.0])),               # wrist horn + clamp
              ("claw_pinion", 1.0, np.array([0.0, 0.0, 3.0, 1.0])),              # pinion horn + screw
              ("claw_frame", 5.0, np.array([8.0, 0.0, 30.0, 1.0]))]              # claw (and mount) screws
    if camera:
        items += [("brio", BRIO_4K.mass_g, np.array([0.0, 0.0, BRIO_4K.height / 2, 1.0])),
                  ("brio", 5.0, np.array([0.0, 0.0, -C.SEAT_T - 3.0, 1.0]))]     # thumb screw
    cables = (5.0, 7.0, 9.0) if camera else (2.0, 3.0, 5.0)
    items += [("claw_frame", cables[0], np.array([0.0, 0.0, 30.0, 1.0])),
              ("forearm", cables[1], np.array([mods["forearm"].L / 2, 0.0, lb / 2, 1.0])),
              ("upper", cables[2], np.array([mods["upper"].L / 2, 0.0, lb / 2, 1.0]))]
    return items


def group_of(k):
    return "claw" if k in CLAW else k


def main():
    mods = {k: AC.load_model(v) for k, v in AC.JOBS.items()}
    place = AC.chain(mods)
    out = {"stall_nmm": STALL, "moving_factor": MOVING, "travel_deg": AC.TRAVEL, "configs": {}}
    sh_v = np.arange(AC.TRAVEL["shoulder"][0], AC.TRAVEL["shoulder"][1] + 1, 5)
    el_v = np.arange(AC.TRAVEL["elbow"][0], AC.TRAVEL["elbow"][1] + 1, 5)
    wr_v = np.arange(AC.TRAVEL["wrist"][0], AC.TRAVEL["wrist"][1] + 1, 5)
    payload_pt = np.array([C.X_TIP - 10.0, 0.0, C.ZS, 1.0])
    tip_pt = np.array([C.X_TIP - 3.0, 0.0, C.ZS, 1.0])

    # one pass over the travel: joint axes, body transforms -> per pose: torque of each item about each joint
    poses = [(sh, el, wr) for sh in sh_v for el in el_v for wr in wr_v]
    for mass_model in ("solid", "sliced est."):
        for camera in (True, False):
            items = masses(mods, mass_model, camera)
            key = f"{'camera' if camera else 'no camera'}, {mass_model}"
            m_total = {g: sum(m for k, m, _ in items if group_of(k) == g) for g in ("claw",)}
            tau0 = {j: [] for j in STALL}
            lever = {j: [] for j in STALL}
            tip_xz = []
            for sh, el, wr in poses:
                P, _ = place((0, float(sh), float(el), float(wr), 0))
                axis_x = {"shoulder": P["upper"][0, 3], "elbow": P["forearm"][0, 3], "wrist": P["claw_frame"][0, 3]}
                xs = {}
                for k, m, com in items:
                    xs.setdefault(group_of(k), []).append((m, (P[k] @ com)[0]))
                pay_x = (P["claw_frame"] @ payload_pt)[0]
                tp = P["claw_frame"] @ tip_pt
                tip_xz.append((tp[0], tp[2]))
                for j in STALL:
                    t = 0.0
                    for g in BEYOND[j]:
                        t += sum(m * (x - axis_x[j]) for m, x in xs.get(g, []))
                    tau0[j].append(GN * t)
                    lever[j].append(GN * (pay_x - axis_x[j]))
            tau0 = {j: np.array(v) for j, v in tau0.items()}
            lever = {j: np.array(v) for j, v in lever.items()}
            tip_xz = np.array(tip_xz)
            cfg = {"end_effector_g": round(m_total["claw"], 1), "worst_static_torque_nmm": {}}
            for pay in (0.0, 20.0, 50.0):
                row = {}
                for j in STALL:
                    t = np.abs(tau0[j] + pay * lever[j])
                    i = int(np.argmax(t))
                    row[j] = {"nmm": round(float(t[i]), 0), "pct_stall": round(100 * float(t[i]) / STALL[j], 0),
                              "pose": [int(v) for v in poses[i]]}
                cfg["worst_static_torque_nmm"][f"payload {pay:g} g"] = row

            def allowed(idx, limit_frac, factor):
                """Largest payload (g) at pose idx with every joint within limit_frac x stall / factor."""
                best = math.inf
                for j in STALL:
                    lim = limit_frac * STALL[j] / factor
                    t0, lv = tau0[j][idx], lever[j][idx]
                    if abs(t0) > lim:
                        return 0.0
                    if abs(lv) < 1e-9:
                        continue
                    hi = (lim - t0) / lv if lv > 0 else (-lim - t0) / lv
                    best = min(best, hi)
                return max(0.0, best)

            straight = poses.index((0, 0, 0))
            cfg["payload_arm_straight_out_g"] = {
                "<=50% stall static": round(allowed(straight, 0.5, 1.0), 0),
                "<=50% stall x1.3 moving": round(allowed(straight, 0.5, MOVING), 0),
                "<=1/3 stall continuous": round(allowed(straight, 1 / 3, 1.0), 0)}
            # top-down carry: claw within 5° of straight down, fingertips 20-60 mm above the desk
            down = [i for i, (sh, el, wr) in enumerate(poses) if abs(sh + el + wr + 90) <= 5
                    and AC.DESK_Z + 20 <= tip_xz[i][1] <= AC.DESK_Z + 60]
            bands = {}
            for x0 in range(60, 280, 20):
                idx = [i for i in down if x0 <= tip_xz[i][0] < x0 + 20]
                if not idx:
                    continue
                bands[f"x {x0}-{x0 + 20}"] = {
                    "<=50% stall static": round(max(allowed(i, 0.5, 1.0) for i in idx), 0),
                    "<=50% stall x1.3 moving": round(max(allowed(i, 0.5, MOVING) for i in idx), 0),
                    "<=1/3 stall continuous": round(max(allowed(i, 1 / 3, 1.0) for i in idx), 0),
                    "poses": len(idx)}
            cfg["payload_top_down_carry_g"] = bands
            out["configs"][key] = cfg
            print(key, json.dumps(cfg["worst_static_torque_nmm"]), cfg["payload_arm_straight_out_g"], flush=True)
            for b, v in bands.items():
                print("   ", b, v)

    # SYS-04: overhung moment about each pitch servo's case-top plane (world Y), pose-independent
    P, _ = place((0, 0.0, 0.0, 0.0, 0))
    mg, mu = MG996R, MG90S
    case_top_y = {"shoulder": P["servo_shoulder"][1, 3] + (mg.case_top - mg.tab_height),
                  "elbow": P["servo_elbow"][1, 3] + (mg.case_top - mg.tab_height),
                  "wrist": P["servo_wrist"][1, 3] + (mu.case_top - mu.tab_height)}
    up_mid_y = mods["turntable"].UP_Y - mods["turntable"].UP_T / 2
    over = {}
    for camera in (True, False):
        items = masses(mods, "solid", camera)
        for pay in (0.0, 50.0):
            row = {}
            for j in STALL:
                ys = [(m, (P[k] @ com)[1]) for k, m, com in items if group_of(k) in BEYOND[j]]
                ys.append((pay, (P["claw_frame"] @ payload_pt)[1]))
                row[j] = round(GN * sum(m * (y - case_top_y[j]) for m, y in ys), 0)
            ys = [(m, (P[k] @ com)[1]) for k, m, com in items if group_of(k) in BEYOND["shoulder"]]
            ys.append((pay, (P["claw_frame"] @ payload_pt)[1]))
            row["turntable upright mid-plane"] = round(GN * sum(m * (y - up_mid_y) for m, y in ys), 0)
            over[f"{'camera' if camera else 'no camera'}, payload {pay:g} g"] = row
    out["overhung_moment_nmm"] = over
    out["case_top_plane_y_mm"] = {k: round(float(v), 1) for k, v in case_top_y.items()}

    # SYS-05: moment on the base servo's output (everything on the turntable), about the horn face's
    # centre, arm straight out and upright, yaw 0; split into the components about world X and Y
    vol, com = props(mods, "turntable")
    z_face = mods["turntable"].Z0
    yaw = {}
    for camera in (True, False):
        items = masses(mods, "solid", camera) + [("turntable", vol * RHO, com),
                                                 ("servo_shoulder", MG996R.mass_g, servo_com(MG996R))]
        for name, q in (("arm straight out", (0, 0.0, 0.0, 0.0, 0)), ("arm upright", (0, 90.0, 0.0, 0.0, 0))):
            Pq, _ = place(q)
            for pay in (0.0, 50.0):
                pts = [(m, Pq[k] @ c) for k, m, c in items] + [(pay, Pq["claw_frame"] @ payload_pt)]
                mx = GN * sum(m * p[1] for m, p in pts)        # about +X (from the arm's sideways offset)
                my = GN * sum(m * p[0] for m, p in pts)        # about Y (reach)
                yaw[f"{'camera' if camera else 'no camera'}, {name}, payload {pay:g} g"] = {
                    "total_nmm": round(math.hypot(mx, my), 0), "about_x_nmm": round(mx, 0), "about_y_nmm": round(my, 0),
                    "axial_n": round(GN * sum(m for m, _ in pts), 2)}
    out["yaw_output_moment_nmm"] = yaw
    out["yaw_output_note"] = (f"moments of everything on the turntable about the base horn face (Z {z_face}), "
                              "solid masses; about_x comes from the arm's sideways offset and is there in every pose")
    print("yaw output moments:", json.dumps(yaw, indent=1))

    # SYS-12: free-standing stability, arm straight out, whole robot (sliced estimate for the printed parts)
    base_items = [(k, props(mods, k)[0] * RHO * r, props(mods, k)[1]) for k, r in
                  (("base", 0.857), ("ring", 0.889), ("cradle", 0.740))]
    base_items += [("servo_base", MG996R.mass_g, servo_com(MG996R)), ("base", 35.0, np.array([0, 0, -20.0, 1.0]))]
    stab = {}
    for camera in (True, False):
        items = masses(mods, "sliced est.", camera) + base_items + [
            ("turntable", props(mods, "turntable")[0] * RHO * 0.678, props(mods, "turntable")[1]),
            ("servo_shoulder", MG996R.mass_g, servo_com(MG996R))]
        for yaw_deg in (0, 90):
            for pay in (0.0, 50.0):
                Pq, _ = place((yaw_deg, 0.0, 0.0, 0.0, 0))
                pts = [(m, Pq[k] @ c) for k, m, c in items] + [(pay, Pq["claw_frame"] @ payload_pt)]
                mt = sum(m for m, _ in pts)
                cx = sum(m * p[0] for m, p in pts) / mt
                cy = sum(m * p[1] for m, p in pts) / mt
                edge = mods["base"].BX / 2 if yaw_deg == 0 else mods["base"].BY / 2
                c_out = cx if yaw_deg == 0 else cy
                out_of = [(m, (p[0] if yaw_deg == 0 else p[1])) for m, p in pts]
                m_over = sum(m * (u - edge) for m, u in out_of if u > edge)          # g·mm about the base edge
                m_rest = sum(m * (edge - u) for m, u in out_of if u <= edge)
                ballast = max(0.0, (1.5 * m_over - m_rest) / edge)                # at the base centre, for SF 1.5
                b_edge, b_mass = 100.0, 400.0                                       # 200 x 200 board, 0.4 kg
                b_over = sum(m * (u - b_edge) for m, u in out_of if u > b_edge)
                b_rest = sum(m * (b_edge - u) for m, u in out_of if u <= b_edge) + b_mass * b_edge
                stab[f"{'camera' if camera else 'no camera'}, yaw {yaw_deg}, payload {pay:g} g"] = {
                    "robot_g": round(mt, 0), "com_out_mm": round(c_out, 1), "base_edge_mm": edge,
                    "past_edge_mm": round(c_out - edge, 1), "sf_free_standing": round(m_rest / m_over, 2),
                    "ballast_for_sf_1_5_g": round(ballast, 0),
                    "board_200_04kg_sf": round(b_rest / b_over, 2) if b_over > 0 else None}
    out["stability_arm_straight_out"] = stab
    out["stability_note"] = ("whole robot incl. base, ring, cradle, ESP32 + wiring allowance 35 g; centre of mass "
                             "along the arm vs the base edge (55 mm at yaw 0, 52 at yaw 90), positive = tips over; "
                             "SF = restoring / overturning moment about the edge; ballast at the base centre; the "
                             "board is 200 x 200 mm, 0.4 kg, centred under the base")
    print("stability:", json.dumps(stab, indent=1))
    print("overhung moments (solid):", json.dumps(over, indent=1))
    (HERE / "torque_budget.json").write_text(json.dumps(out, indent=1))
    print("-> torque_budget.json")


if __name__ == "__main__":
    main()

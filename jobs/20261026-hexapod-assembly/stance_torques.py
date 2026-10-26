"""Static servo torques for candidate walking stances (deep review SYS-1, round 3).

For each stance (femur, tibia in the firmware's angles), walks the round-3 tripod gait (hex_frame.gait_pose:
straight-line feet, 20 mm sine lift, 40 % swing) at 30 and 40 mm stride, solves the three vertical foot loads
exactly for every tripod-only frame (centre of gravity on the body centre), and takes the largest femur and
knee torque of any planted leg. Also the neutral stance on a tripod, on six legs, and the bending moment at
the coxa horn (SYS-6). Torques are static; the ×2 walking factor would double them.

Run from the project root:  .venv/bin/python jobs/20261026-hexapod-assembly/stance_torques.py
Writes stance_torques.json next to this file.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "tools"), str(HERE)]
import hex_frame as H  # noqa: E402

STALL = H.SERVO.stall_torque_nmm          # 216 N·mm at 6 V
MASS_G = {   # robot mass (g): the strength reviews' basis, and round 3 (new volumes, see assembly_plan.md "Mass")
    "strength round 1 basis (683 g)": 683.0,
    "round 3, printed estimate (812 g)": 812.0,
    "round 3, solid parts, upper bound (877 g)": 877.0,
    "round 4, strength round 3's itemised mass with the round-4 changes (906 g)": 906.0,
}
STANCES = {
    "SYS-1: tibias tucked 15° (femur -3.0, tibia -12.0)": (-3.0, -12.0),
    "strength: tibia 18.7° in, same height (femur -4.7, tibia -14.0)": (-4.7, -14.0),
    "strength as written: femur 0, tibia -18.7 (body 3.7 mm lower)": (0.0, -18.7),
    "servo centre (femur 0, tibia 0)": (0.0, 0.0),
}


def shares(feet_xy, cg=(0.0, 0.0)):
    """Vertical load fractions on three feet carrying a weight at cg (exact, statically determinate)."""
    A = np.vstack([np.ones(3), feet_xy[:, 0], feet_xy[:, 1]])
    return np.linalg.solve(A, np.array([1.0, cg[0], cg[1]]))


def joint_torques(i, angles, z_pu, F):
    """Femur and knee torque magnitudes (N·mm) and coxa-horn bending (N·mm) for an upward foot force F (N)."""
    fr, foot = H.leg_frames(*H.LEG_MOUNTS[i], *angles, z_pu=z_pu)
    f = np.array([0.0, 0.0, F])
    out = {}
    for name, key in (("femur", "S1"), ("knee", "S2")):
        o, ax = fr[key][:3, 3], fr[key][:3, 2]
        out[name] = abs(float(np.cross(foot - o, f) @ ax))
    m = np.cross(foot - fr["C"][:3, 3], f)
    out["coxa_bending"] = float(np.hypot(m[0], m[1]))
    return out


def evaluate(femur_s, tibia_s, W):
    z_pu = H.stance_z_pu(femur_s, tibia_s)
    f, t = H.sketch_to_frames(femur_s, tibia_s)
    res = {"femur_s": femur_s, "tibia_s": tibia_s, "body_underside_mm": round(z_pu, 1)}
    feet = np.array(H.neutral_feet(z_pu, femur_s, tibia_s))
    neutral = [(0.0, f, t)] * 6
    tq6 = [joint_torques(i, neutral[i], z_pu, W / 6) for i in range(6)]
    six = {k: max(t[k] for t in tq6) for k in tq6[0]}
    worst = {"femur": 0, "knee": 0, "coxa_bending": 0, "share": 0}
    for trip in (H.TRIPOD_A, H.TRIPOD_B):
        s = shares(feet[list(trip), :2])
        for k, i in enumerate(trip):
            tq = joint_torques(i, neutral[i], z_pu, s[k] * W)
            for key in ("femur", "knee", "coxa_bending"):
                worst[key] = max(worst[key], tq[key])
            worst["share"] = max(worst["share"], s[k])
    res["six_legs"] = {k: round(v, 1) for k, v in six.items()}
    res["neutral_tripod"] = {k: round(v, 3 if k == "share" else 1) for k, v in worst.items()}
    for stride in (30.0, 40.0):
        w = {"femur": 0, "knee": 0, "coxa_bending": 0, "share": 0}
        rng = {"coxa": [99, -99], "femur": [99, -99], "tibia": [99, -99]}
        for fr_i in range(H.CYCLE_FRAMES):
            ang, ft, down = H.gait_pose(fr_i, stride, femur_s=femur_s, tibia_s=tibia_s)
            for i in range(6):
                for key, v in zip(("coxa", "femur", "tibia"), (ang[i][0], ang[i][1], ang[i][2] + 90.0)):
                    rng[key] = [min(rng[key][0], v), max(rng[key][1], v)]
            planted = [i for i in range(6) if down[i]]
            if len(planted) != 3:
                continue                      # double support: six feet share the load
            s = shares(np.array([ft[i][:2] for i in planted]))
            for k, i in enumerate(planted):
                tq = joint_torques(i, ang[i], z_pu, s[k] * W)
                for key in ("femur", "knee", "coxa_bending"):
                    w[key] = max(w[key], tq[key])
                w["share"] = max(w["share"], s[k])
        res[f"gait_{stride:.0f}mm"] = {k: round(v, 3 if k == "share" else 1) for k, v in w.items()}
        res[f"gait_{stride:.0f}mm"]["ranges_sketch_deg"] = {k: [round(a, 1), round(b, 1)] for k, (a, b) in rng.items()}
    return res


def main():
    out = {"stall_nmm": STALL, "note": "static torques; peak over the tripod-only frames of one gait cycle", "cases": {}}
    for mlabel, m in MASS_G.items():
        W = m * 9.81e-3
        out["cases"][mlabel] = {}
        for label, (fs, ts) in STANCES.items():
            r = evaluate(fs, ts, W)
            out["cases"][mlabel][label] = r
            g30, g40, nt = r["gait_30mm"], r["gait_40mm"], r["neutral_tripod"]
            print(f"{mlabel} | {label}: underside {r['body_underside_mm']} | tripod femur {nt['femur']:.0f} knee "
                  f"{nt['knee']:.0f} | 30 mm {g30['femur']:.0f} ({g30['femur'] / STALL:.0%}) / {g30['knee']:.0f} "
                  f"({g30['knee'] / STALL:.0%}) | 40 mm {g40['femur']:.0f} ({g40['femur'] / STALL:.0%}) / "
                  f"{g40['knee']:.0f} ({g40['knee'] / STALL:.0%}) | share {g40['share']:.3f} | coxa bend "
                  f"{g40['coxa_bending']:.0f} | ranges {g40['ranges_sketch_deg']}")
    (HERE / "stance_torques.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

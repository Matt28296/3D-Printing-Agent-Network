"""Assembly interference and joint-range check for the hexapod.

Places both body plates, six legs (coxa bracket, femur, tibia + three MG90S dummies each) and
dummies of the LiPo, ESP32 (with jumper housings) and both PCA9685 boards, in the neutral stance
(femur horizontal, tibia vertical, foot tips on the ground), then sweeps the joints:
  - every coxa together, and neighbouring legs turned towards each other
  - one leg's femur and tibia through their ranges
Overlap of any pair of bodies > TOL mm³ counts as a collision. Writes assembly_check.json and
assembly_hexapod.png.

Run from the project root:  .venv/bin/python jobs/20261026-hexapod-assembly/assembly_check.py
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
from build123d import Box, Pos, export_stl  # noqa: E402
from hobby_parts import ESP32_DEVKIT_38, LIPO_2S_1000, PCA9685_BOARD, servo_dummy  # noqa: E402
import hex_frame as H  # noqa: E402

TOL = 1.0
JOBS = {"bottom": "20261026-hexapod-body-bottom", "top": "20261026-hexapod-body-top",
        "coxa": "20261026-hexapod-coxa", "femur": "20261026-hexapod-femur", "tibia": "20261026-hexapod-tibia"}


def load(job):
    spec = importlib.util.spec_from_file_location(f"m_{job.replace('-', '_')}", ROOT / "jobs" / job / "model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def to_mesh(shape):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "s.stl"
        export_stl(shape, str(p), tolerance=0.05, angular_tolerance=0.2)
        return trimesh.load(p, force="mesh")


def T(x=0.0, y=0.0, z=0.0):
    m = np.eye(4); m[:3, 3] = (x, y, z); return m


def Rz(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    m = np.eye(4); m[:2, :2] = [[c, -s], [s, c]]; return m


def frame(origin, x_dir, z_dir):
    x = np.asarray(x_dir, float); x /= np.linalg.norm(x)
    z = np.asarray(z_dir, float); z /= np.linalg.norm(z)
    y = np.cross(z, x)
    m = np.eye(4); m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = x, y, z, origin
    return m


def leg_frames(mx, my, a, coxa=0.0, femur=0.0, tibia=-90.0, z_tab=H.STANCE_Z_TAB):
    """Joint angles in degrees: coxa about world -Z (+ = clockwise seen from above), femur + = up,
    tibia relative to the femur, -90 = straight down when the femur is horizontal."""
    S0 = frame((mx, my, z_tab), (math.cos(math.radians(a)), math.sin(math.radians(a)), 0), (0, 0, -1))
    C = S0 @ T(0, 0, H.LB) @ Rz(coxa)
    S1 = C @ frame((H.L_C, H.Y_F, H.Z_F), (1, 0, 0), (0, 1, 0))
    F = S1 @ T(0, 0, H.LB) @ Rz(femur)
    S2 = F @ T(H.L_F, 0, H.T_F)
    Tt = S2 @ T(0, 0, H.LB) @ Rz(tibia)
    foot = Tt @ np.array([H.L_T, 0, H.T_T / 2, 1.0])
    return {"S0": S0, "C": C, "S1": S1, "F": F, "S2": S2, "T": Tt}, foot[:3]


def main():
    mods = {k: load(v) for k, v in JOBS.items()}
    print("tessellating ...", flush=True)
    M = {k: to_mesh(m.design()) for k, m in mods.items()}
    M["servo"] = to_mesh(servo_dummy(H.SERVO, with_horn=False))
    lp = LIPO_2S_1000
    M["lipo"] = to_mesh(Pos(0, 0, H.T_BODY + lp.height / 2 + 0.01) * Box(lp.length, lp.width, lp.height))
    top = mods["top"]
    e = ESP32_DEVKIT_38
    z0 = H.T_BODY + H.COLUMN_H                  # top plate underside (body frame, tab plane = 0)
    zp = z0 + H.T_TOP + top.LEDGE_H
    esp = Pos(top.USB_END_X + e.length / 2, 0, zp + e.pcb_t / 2) * Box(e.length, e.width, e.pcb_t)
    pins_len = e.length - 2 * 4.34 + 2.54
    for sy in (-1, 1):   # female jumper housings (16.5) + 10 mm for the leads to bend (DFM round 1)
        esp += Pos(top.USB_END_X + e.length / 2, sy * (e.width / 2 - 1.3), zp - 26.5 / 2) * Box(pins_len, 2.54, 26.5)
    pca = PCA9685_BOARD
    for sy in (-1, 1):
        esp += Pos(0, sy * top.PCA_Y, z0 + H.T_TOP + top.POST_H + pca.height / 2 + 0.01) * Box(pca.length, pca.width, pca.height)
    M["electronics"] = to_mesh(esp)

    zt = H.STANCE_Z_TAB
    def place(angles):
        P = {"bottom": T(0, 0, zt), "top": T(0, 0, zt + z0), "lipo": T(0, 0, zt), "electronics": T(0, 0, zt)}
        feet = []
        for i, (mx, my, a) in enumerate(H.LEG_MOUNTS):
            c, f, t = angles[i]
            fr, foot = leg_frames(mx, my, a, c, f, t)
            P[f"L{i}_coxa_servo"], P[f"L{i}_coxa"] = fr["S0"], fr["C"]
            P[f"L{i}_femur_servo"], P[f"L{i}_femur"] = fr["S1"], fr["F"]
            P[f"L{i}_tibia_servo"], P[f"L{i}_tibia"] = fr["S2"], fr["T"]
            feet.append(foot)
        return P, feet

    def kind(k):
        return "servo" if k.endswith("_servo") else k.split("_")[-1] if k.startswith("L") else k

    def overlaps(P):
        placed = {k: M[kind(k)].copy().apply_transform(v) for k, v in P.items()}
        hits = []
        for a_, c_ in itertools.combinations(sorted(placed), 2):
            ma, mc = placed[a_], placed[c_]
            lo = np.maximum(ma.bounds[0], mc.bounds[0]); hi = np.minimum(ma.bounds[1], mc.bounds[1])
            if np.any(hi - lo <= 0):
                continue
            try:
                v = trimesh.boolean.intersection([ma, mc], engine="manifold").volume
            except Exception:
                v = 0.0
            if v > TOL:
                hits.append((a_, c_, round(float(v), 1)))
        return hits, placed

    stance = [(0.0, 0.0, -90.0)] * 6
    report = {"tol_mm3": TOL, "stance_z_tab_mm": round(zt, 2)}
    P, feet = place(stance)
    hits, placed = overlaps(P)
    lo, hi = trimesh.util.concatenate(list(placed.values())).bounds
    report["stance"] = {"collisions": hits, "feet_z_mm": [round(float(f[2]), 2) for f in feet],
                        "feet_xy_mm": [[round(float(f[0]), 1), round(float(f[1]), 1)] for f in feet],
                        "overall_mm": [round(float(v), 1) for v in hi - lo],
                        "body_underside_clearance_mm": round(float(min(placed[k].bounds[0][2] for k in placed
                                                                       if not k.endswith("tibia"))), 1)}
    print("stance", report["stance"], flush=True)
    _render(placed, HERE / "assembly_hexapod.png")

    sweeps = {}
    # all coxae together
    res = []
    for c in range(-45, 46, 5):
        h, _ = overlaps(place([(c, 0.0, -90.0)] * 6)[0])
        res.append((c, h[:3]))
    sweeps["all coxae together"] = {"free": [c for c, h in res if not h], "hits": [r for r in res if r[1]][:4]}
    # neighbours towards each other: legs 0/1 and 3/4 converge, 2 stays
    res = []
    for c in range(0, 46, 5):
        ang = [(-c, 0, -90), (c, 0, -90), (0, 0, -90), (c, 0, -90), (-c, 0, -90), (0, 0, -90)]
        h, _ = overlaps(place(ang)[0])
        res.append((c, h[:3]))
    sweeps["front and middle legs converge"] = {"free": [c for c, h in res if not h], "hits": [r for r in res if r[1]][:4]}
    res = []
    for c in range(0, 46, 5):
        ang = [(0, 0, -90), (-c, 0, -90), (c, 0, -90), (0, 0, -90), (c, 0, -90), (-c, 0, -90)]
        h, _ = overlaps(place(ang)[0])
        res.append((c, h[:3]))
    sweeps["middle and rear legs converge"] = {"free": [c for c, h in res if not h], "hits": [r for r in res if r[1]][:4]}
    # one leg: femur, tibia
    res = []
    for f in range(-70, 91, 10):
        ang = list(stance); ang[1] = (0, f, -90)
        h, _ = overlaps(place(ang)[0])
        res.append((f, h[:3]))
    sweeps["middle-left femur (tibia -90)"] = {"free": [f for f, h in res if not h], "hits": [r for r in res if r[1]][:4]}
    res = []
    for t in range(-170, 1, 10):
        ang = list(stance); ang[1] = (0, 30, t)
        h, _ = overlaps(place(ang)[0])
        res.append((t, h[:3]))
    sweeps["middle-left tibia (femur +30)"] = {"free": [t for t, h in res if not h], "hits": [r for r in res if r[1]][:4]}
    report["sweeps"] = sweeps
    for k, s in sweeps.items():
        print(f"{k:34s} free {s['free']}")
        if s["hits"]:
            print(f"{'':34s} hits {s['hits'][:2]}")
    (HERE / "assembly_check.json").write_text(json.dumps(report, indent=1))


def _render(placed, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import render as R
    m = trimesh.util.concatenate(list(placed.values()))
    fig, axes = plt.subplots(1, 2, figsize=(14, 7.4), dpi=100)
    for ax, (vname, (elev, azim)) in zip(axes, (("iso", R.VIEWS["iso"]), ("front", R.VIEWS["right"]))):
        img, _ = R.render_view(m, elev, azim, with_bed=False)
        ax.imshow(img, interpolation="antialiased"); ax.set_axis_off(); ax.set_title(vname)
    fig.suptitle("hexapod · neutral stance · parts + servo/LiPo/ESP32/PCA9685 dummies", fontsize=13)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


if __name__ == "__main__":
    main()

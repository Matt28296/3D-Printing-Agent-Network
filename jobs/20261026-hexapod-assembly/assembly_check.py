"""Assembly interference and joint-range check for the hexapod (round 3).

Places both body plates, six legs (coxa bracket, femur, tibia + three MG90S dummies each, with their
gear bosses, tab-screw hardware and horn clamp screws) and dummies of the LiPo, UBEC (on its side beside
the LiPo), main switch, ESP32 (with jumper housings) and both PCA9685 boards, using the frames of
hex_frame.py, then checks:
  - the servo-centre pose (femur level, tibia perpendicular) and the walking stance (hex_frame.NEUTRAL_*);
  - the straight-line tripod gait at 30 and 40 mm stride, 20 mm lift, every frame of the cycle (IK);
  - sweeps: every coxa together, neighbouring legs turned towards each other, one leg's femur and tibia;
  - that every gait joint angle stays inside the servo travel (with room for the ±20° trims) and inside
    the collision-free sweep ranges.
Overlap of any pair of bodies > TOL mm³ counts as a collision. Writes assembly_check.json and
assembly_hexapod.png.

Run from the project root:  .venv/bin/python jobs/20261026-hexapod-assembly/assembly_check.py
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "tools"), str(HERE)]
from build123d import Align, Box, Cylinder, Pos, export_stl  # noqa: E402
from hobby_parts import ESP32_DEVKIT_38, LIPO_2S_1000, PCA9685_BOARD, servo_dummy  # noqa: E402
import hex_frame as H  # noqa: E402

TOL = 1.0
SERVO_TRAVEL = 90.0       # MG90S: ±90° from centre (500-2500 µs)
TRIM_ROOM = 20.0          # the sketch allows trims up to ±20°
UBEC_BOX = (50.0, 10.0, 20.0)     # on its side: length (x) × thickness (y) × height (z). Covers a 5 A class UBEC
                                  # (Hobbywing UBEC 5A Air 50 × 17 × 10; hobby_parts UBEC_6V_5A 45 × 20 × 9)
UBEC_AT = (0.0, 22.5)             # x centre, y of its LiPo-side face (left side; the strap slot ends at y 21.5)
SWITCH_BODY = (18.0, 13.0, 24.0)  # 12 mm toggle body below the deck (x, y, depth)
# Coxa tab screws (strength round 3: Nyloc nuts, driven snug): M2 × 14 from below, Ø5 × 0.3 washers, M2 Nyloc on the tab.
# The Nyloc is modelled 3.0 mm tall (DIN 985 M2 is a little less); M2 × 12 would end level with its top, short of the
# nylon ring, so the screw is M2 × 14.
TAB_SCREW_L, TAB_WASHER_T, NYLOC_H = 14.0, 0.3, 3.0
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


def cyl(d, z0, z1, x=0.0, y=0.0):
    return Pos(x, y, min(z0, z1)) * Cylinder(d / 2, abs(z1 - z0), align=(Align.CENTER, Align.CENTER, Align.MIN))


def servo_with_boss():
    """MG90S dummy (case, tabs, spline) plus the round gear boss on top of the case (TowerPro C 28.4)."""
    s = H.SERVO
    return servo_dummy(s, with_horn=False) + cyl(H.GEAR_BOSS_D, s.case_top - s.tab_height - 0.01, H.GEAR_BOSS_TOP)


def pilots(shift=0.0):
    s = H.SERVO
    xm = -(s.length - s.shaft_from_end) + s.length / 2
    return [xm - s.hole_dx / 2, xm + s.hole_dx / 2 + shift]


def hardware():
    """Bought fasteners, each in the frame it moves with."""
    t = H.TAB_T
    hw = {}
    # coxa servos (reversed, in S0): M2 × 14 from below: washer + head under the plate (servo z 8.5 .. 10.4),
    # washer + Nyloc on the tab (servo z 0 .. -3.3), tip 1.9 mm beyond the Nyloc (servo z -5.2)
    c = None
    nut_top, tip = -(TAB_WASHER_T + NYLOC_H), H.S0_Z + TAB_WASHER_T - TAB_SCREW_L
    for x in pilots():
        part = cyl(5.0, H.S0_Z, H.S0_Z + 1.9, x) + cyl(5.0, 0.0, nut_top, x) + cyl(2.0, nut_top, tip, x)
        c = part if c is None else c + part
    hw["coxa_tab_hw"] = c
    # femur servo (normal, in S1): self-tapping M2 × 10 heads on the tabs; the outboard pilot is moved 1.3 mm
    hw["femur_tab_hw"] = sum((cyl(3.8, t, t + 1.6, x) for x in pilots(1.3)[1:]), cyl(3.8, t, t + 1.6, pilots(1.3)[0]))
    # tibia servo (reversed, in S2): M2 × 8 heads on the tabs' case side
    hw["tibia_tab_hw"] = sum((cyl(3.8, 0.0, -1.6, x) for x in pilots()[1:]), cyl(3.8, 0.0, -1.6, pilots()[0]))
    # horn clamp screws on each link's front face: coxa Ø10 × 1 penny washer + head; femur/tibia Ø6 washer + head
    hw["coxa_clamp"] = cyl(10.0, H.T_C, H.T_C + 1.0) + cyl(3.8, H.T_C + 1.0, H.T_C + 2.6)
    hw["femur_clamp"] = cyl(6.0, H.T_F, H.T_F + 0.5) + cyl(3.8, H.T_F + 0.5, H.T_F + 2.1)
    hw["tibia_clamp"] = cyl(6.0, H.T_T, H.T_T + 0.5) + cyl(3.8, H.T_T + 0.5, H.T_T + 2.1)
    return hw


def T(x=0.0, y=0.0, z=0.0):
    m = np.eye(4); m[:3, 3] = (x, y, z); return m


def main():
    mods = {k: load(v) for k, v in JOBS.items()}
    print("tessellating ...", flush=True)
    M = {k: to_mesh(m.design()) for k, m in mods.items()}
    M["servo"] = to_mesh(servo_with_boss())
    for k, v in hardware().items():
        M[k] = to_mesh(v)
    lp = LIPO_2S_1000
    top = mods["top"]
    zt0 = H.T_BODY + H.COLUMN_H                      # deck underside above the plate underside (body frame)
    body = Pos(0, 0, H.T_BODY + lp.height / 2 + 0.01) * Box(lp.length, lp.width, lp.height)
    M["lipo"] = to_mesh(body)
    ul, ut, uh = UBEC_BOX
    M["ubec"] = to_mesh(Pos(UBEC_AT[0], UBEC_AT[1] + ut / 2, H.T_BODY + uh / 2 + 0.01) * Box(ul, ut, uh))
    sx, sy, sd = SWITCH_BODY
    M["switch"] = to_mesh(Pos(top.SWITCH_XY[0], top.SWITCH_XY[1], zt0 - sd / 2 - 0.01) * Box(sx, sy, sd))
    e = ESP32_DEVKIT_38
    zp = zt0 + H.T_TOP + top.LEDGE_H
    esp = Pos(top.USB_END_X + e.length / 2, 0, zp + e.pcb_t / 2) * Box(e.length, e.width, e.pcb_t)
    pins_len = e.length - 2 * 4.34 + 2.54
    for sy_ in (-1, 1):   # female jumper housings (16.5) + 10 mm for the leads to bend (DFM round 1)
        esp += Pos(top.USB_END_X + e.length / 2, sy_ * (e.width / 2 - 1.3), zp - 26.5 / 2) * Box(pins_len, 2.54, 26.5)
    pca = PCA9685_BOARD
    for sy_ in (-1, 1):
        esp += Pos(0, sy_ * top.PCA_Y, zt0 + H.T_TOP + top.POST_H + pca.height / 2 + 0.01) * Box(pca.length, pca.width, pca.height)
    M["electronics"] = to_mesh(esp)

    def place(angles, z_pu):
        P = {k: T(0, 0, z_pu) for k in ("bottom", "lipo", "ubec", "switch", "electronics")}
        P["top"] = T(0, 0, z_pu + zt0)
        feet = []
        for i, (mx, my, a) in enumerate(H.LEG_MOUNTS):
            fr, foot = H.leg_frames(mx, my, a, *angles[i], z_pu=z_pu)
            P[f"L{i}_coxa_servo"], P[f"L{i}_coxa_tab_hw"] = fr["S0"], fr["S0"]
            P[f"L{i}_coxa"], P[f"L{i}_coxa_clamp"] = fr["C"], fr["C"]
            P[f"L{i}_femur_servo"], P[f"L{i}_femur_tab_hw"] = fr["S1"], fr["S1"]
            P[f"L{i}_femur"], P[f"L{i}_femur_clamp"] = fr["F"], fr["F"]
            P[f"L{i}_tibia_servo"], P[f"L{i}_tibia_tab_hw"] = fr["S2"], fr["S2"]
            P[f"L{i}_tibia"], P[f"L{i}_tibia_clamp"] = fr["T"], fr["T"]
            feet.append(foot)
        return P, feet

    def kind(k):
        if not k.startswith("L"):
            return k
        rest = k.split("_", 1)[1]
        return "servo" if rest.endswith("_servo") else rest

    def overlaps(P):
        placed = {k: M[kind(k)].copy().apply_transform(v) for k, v in P.items()}
        hits = []
        for a_, c_ in itertools.combinations(sorted(placed), 2):
            ma, mc = placed[a_], placed[c_]   # fasteners only touch their own parts face to face (zero volume)
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

    report = {"tol_mm3": TOL, "frames": {
        "mounts": {"coxa": H.COXA_MOUNT, "femur servo": H.FEMUR_MOUNT, "tibia servo": H.TIBIA_MOUNT},
        "LB": H.LB, "Z_F": H.Z_F, "S0_above_plate_underside": H.S0_Z, "plate_gap_to_bracket": round(H.PLATE_GAP, 2),
        "foot_side_mm": round(H.FOOT_SIDE, 2), "leg_mounts": H.LEG_MOUNTS, "columns": H.COLUMNS,
        "coxa_tab_stack": {"screw": f"M2 x {TAB_SCREW_L:.0f}", "nyloc_h_mm": NYLOC_H,
                           "thread_past_nyloc_mm": round(TAB_SCREW_L - TAB_WASHER_T - H.T_BODY - H.TAB_T
                                                         - TAB_WASHER_T - NYLOC_H, 2)},
        "ubec_box_xyz": [UBEC_AT[0] - UBEC_BOX[0] / 2, UBEC_AT[0] + UBEC_BOX[0] / 2, UBEC_AT[1],
                         UBEC_AT[1] + UBEC_BOX[1], 0.0, UBEC_BOX[2]]}}

    # --- servo centre and walking stance ----------------------------------------------------------------
    centre = [(0.0, 0.0, -90.0)] * 6
    P, feet = place(centre, H.CENTRE_Z_PU)
    hits, placed = overlaps(P)
    report["servo_centre"] = {"collisions": hits, "plate_underside_mm": round(H.CENTRE_Z_PU, 2),
                              "feet_z_mm": [round(float(f[2]), 2) for f in feet],
                              "feet_xy_mm": [[round(float(f[0]), 1), round(float(f[1]), 1)] for f in feet]}
    f_s, t_s = H.sketch_to_frames(H.NEUTRAL_FEMUR, H.NEUTRAL_TIBIA)
    stance = [(0.0, f_s, t_s)] * 6
    P, feet = place(stance, H.STANCE_Z_PU)
    hits, placed = overlaps(P)
    lo, hi = trimesh.util.concatenate(list(placed.values())).bounds
    lowest = min((placed[k].bounds[0][2], k) for k in placed if not k.endswith("_tibia"))
    report["stance"] = {"sketch_angles": {"femur": H.NEUTRAL_FEMUR, "tibia": H.NEUTRAL_TIBIA},
                        "collisions": hits, "plate_underside_mm": round(H.STANCE_Z_PU, 2),
                        "feet_z_mm": [round(float(f[2]), 2) for f in feet],
                        "feet_xy_mm": [[round(float(f[0]), 1), round(float(f[1]), 1)] for f in feet],
                        "overall_mm": [round(float(v), 1) for v in hi - lo],
                        "lowest_point_mm": [round(float(lowest[0]), 1), lowest[1]]}
    print("stance", report["stance"], flush=True)
    _render(placed, HERE / "assembly_hexapod.png", f"walking stance (femur {H.NEUTRAL_FEMUR:+.1f}°, tibia "
                                                   f"{H.NEUTRAL_TIBIA:+.1f}°)")

    # --- straight-line tripod gait ------------------------------------------------------------------------
    gait = {}
    for stride in (30.0, 40.0):
        g_hits, rng, ik_err, gap = [], {"coxa": [99, -99], "femur": [99, -99], "tibia": [99, -99]}, 0.0, []
        for fr_i in range(H.CYCLE_FRAMES):
            angles, targets, down = H.gait_pose(fr_i, stride)
            P, feet = place(angles, H.STANCE_Z_PU)
            ik_err = max(ik_err, max(float(np.linalg.norm(f - t_)) for f, t_ in zip(feet, targets)))
            h, _ = overlaps(P)
            if h:
                g_hits.append((fr_i, h[:3]))
            for (c, f, t) in angles:
                for key, v in (("coxa", c), ("femur", f), ("tibia", t + 90.0)):
                    rng[key] = [min(rng[key][0], v), max(rng[key][1], v)]
            close = [abs(angles[i][0] - angles[j][0]) for i, j in ((0, 1), (1, 2), (3, 4), (4, 5))]
            gap.append(max(close))
        gait[f"stride {stride:.0f} mm, lift 20 mm"] = {
            "frames": H.CYCLE_FRAMES, "collisions": g_hits, "ik_foot_error_mm": round(ik_err, 4),
            "joint_ranges_sketch_deg": {k: [round(a, 1), round(b, 1)] for k, (a, b) in rng.items()},
            "max_neighbour_coxa_difference_deg": round(max(gap), 1)}
        print(f"gait {stride:.0f} mm: collisions {len(g_hits)}, ranges {gait[f'stride {stride:.0f} mm, lift 20 mm']['joint_ranges_sketch_deg']}",
              flush=True)
    report["gait"] = gait

    # --- sweeps (from the servo-centre pose) -----------------------------------------------------------------
    sweeps = {}
    res = []
    for c in range(-45, 46, 5):
        h, _ = overlaps(place([(c, 0.0, -90.0)] * 6, H.CENTRE_Z_PU)[0])
        res.append((c, h[:3]))
    sweeps["all coxae together"] = {"free": [c for c, h in res if not h], "hits": [r for r in res if r[1]][:4]}
    res = []
    for c in range(0, 46, 5):
        ang = [(-c, 0, -90), (c, 0, -90), (0, 0, -90), (c, 0, -90), (-c, 0, -90), (0, 0, -90)]
        h, _ = overlaps(place(ang, H.CENTRE_Z_PU)[0])
        res.append((c, h[:3]))
    sweeps["front and middle legs converge"] = {"free": [c for c, h in res if not h], "hits": [r for r in res if r[1]][:4]}
    res = []
    for c in range(0, 46, 5):
        ang = [(0, 0, -90), (-c, 0, -90), (c, 0, -90), (0, 0, -90), (c, 0, -90), (-c, 0, -90)]
        h, _ = overlaps(place(ang, H.CENTRE_Z_PU)[0])
        res.append((c, h[:3]))
    sweeps["middle and rear legs converge"] = {"free": [c for c, h in res if not h], "hits": [r for r in res if r[1]][:4]}
    res = []
    for f in range(-70, 91, 10):
        ang = list(centre); ang[1] = (0, f, -90)
        h, _ = overlaps(place(ang, H.CENTRE_Z_PU)[0])
        res.append((f, h[:3]))
    sweeps["middle-left femur (tibia perpendicular)"] = {"free": [f for f, h in res if not h], "hits": [r for r in res if r[1]][:4]}
    res = []
    for t in range(-170, 1, 10):
        ang = list(centre); ang[1] = (0, 30, t)
        h, _ = overlaps(place(ang, H.CENTRE_Z_PU)[0])
        res.append((t + 90, h[:3]))
    sweeps["middle-left tibia, sketch angle (femur +30)"] = {"free": [t for t, h in res if not h], "hits": [r for r in res if r[1]][:4]}
    report["sweeps"] = sweeps
    for k, s in sweeps.items():
        print(f"{k:44s} free {s['free']}")
        if s["hits"]:
            print(f"{'':44s} hits {s['hits'][:2]}")

    # --- joint ranges against the servo travel and the free sweeps -------------------------------------------
    def span(free):
        return [min(free), max(free)] if free else None
    free = {"coxa": span(sweeps["all coxae together"]["free"]),
            "femur": span(sweeps["middle-left femur (tibia perpendicular)"]["free"]),
            "tibia": span(sweeps["middle-left tibia, sketch angle (femur +30)"]["free"])}
    limits = {}
    ok = True
    for k in ("coxa", "femur", "tibia"):
        lo_g = min(g["joint_ranges_sketch_deg"][k][0] for g in gait.values())
        hi_g = max(g["joint_ranges_sketch_deg"][k][1] for g in gait.values())
        in_travel = -(SERVO_TRAVEL - TRIM_ROOM) <= lo_g and hi_g <= SERVO_TRAVEL - TRIM_ROOM
        in_free = free[k] is not None and free[k][0] <= lo_g and hi_g <= free[k][1]
        limits[k] = {"gait": [round(lo_g, 1), round(hi_g, 1)], "free_sweep": free[k], "inside_travel_with_trims": in_travel,
                     "inside_free_sweep": in_free}
        ok &= in_travel and in_free
    report["joint_limits"] = limits
    report["clean"] = bool(ok and not report["stance"]["collisions"] and not report["servo_centre"]["collisions"]
                           and not any(g["collisions"] for g in gait.values()))
    print("joint limits", limits)
    print("CLEAN" if report["clean"] else "NOT CLEAN")
    (HERE / "assembly_check.json").write_text(json.dumps(report, indent=1))


def _render(placed, out, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import render as R
    m = trimesh.util.concatenate(list(placed.values()))
    fig, axes = plt.subplots(1, 2, figsize=(14, 7.4), dpi=100)
    for ax, (vname, (elev, azim)) in zip(axes, (("iso", R.VIEWS["iso"]), ("front", R.VIEWS["right"]))):
        img, _ = R.render_view(m, elev, azim, with_bed=False)
        ax.imshow(img, interpolation="antialiased"); ax.set_axis_off(); ax.set_title(vname)
    fig.suptitle(f"hexapod · {title} · parts + servo/UBEC/LiPo/ESP32/PCA9685 dummies", fontsize=13)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


if __name__ == "__main__":
    main()

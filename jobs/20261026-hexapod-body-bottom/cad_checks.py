"""jobs/20261026-hexapod-body-bottom/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261026-hexapod-body-bottom/cad_checks.py
Exit code 0 = every check passed. Body frame, plate underside at Z = 0.
"""
import math
import runpy
import sys
from pathlib import Path

JOB = Path(__file__).resolve().parent
sys.path.insert(0, str(JOB.parents[1] / "tools"))
from cadlib import bbox, measure_holes  # noqa: E402

ns = runpy.run_path(str(JOB / "model.py"), run_name="model")
part = ns["build"]()
size = bbox(part)["size"]
holes = measure_holes(part)
failures = []


def check(name, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok:
        failures.append(name)


def solid(*p):
    return part.is_inside(p)


T, w = ns["T_BODY"], ns["to_world"]
zm = T / 2
mounts = ns["LEG_MOUNTS"]
pil = [-(22.8 - 5.9) + 22.8 / 2 - 27.8 / 2, -(22.8 - 5.9) + 22.8 / 2 + 27.8 / 2]   # -19.4, 8.4 (servo x)

# ---- CHECKS: one line per critical dimension in design_brief.md -----------------
check("overall size 154.8 × 138.8 × 46.0", all(abs(a - b) < 0.05 for a, b in zip(size, [154.8, 138.8, 46.0])), size)
check("plate T_BODY 6.0 (strength round 1)", solid(0, 0, 0.1) and solid(0, 0, 5.9) and not solid(0, 0, 6.1), "probe at the centre")
ok_w = all(not solid(*w(mx, my, a, u, v), zm) for (mx, my, a) in mounts for (u, v) in ((-17.05, 6.35), (6.05, -6.35), (-5.5, 0)))
ok_e = all(solid(*w(mx, my, a, u, v), zm) for (mx, my, a) in mounts for (u, v) in ((-17.15, 0), (6.15, 0), (-5.5, 6.45)))
check("six coxa windows 23.2 × 12.8 CAD (MG90S 22.8 × 12.2 + 0.2 end / 0.4 side + HOLE_COMP)", ok_w and ok_e,
      "corners void, 0.05 beyond solid")
ok_p = all(not solid(*w(mx, my, a, u, dv), zm) and solid(*w(mx, my, a, u, dv * 1.1), zm)
           for (mx, my, a) in mounts for u in pil for dv in (-1.15, 1.15))
check("tab-screw clearance holes Ø2.2 + HOLE_COMP (M2 machine screws), 12", ok_p, "±1.15 void, ±1.27 solid")
lig = min(math.dist((-17.1, 0), (pil[0], 0)), math.dist((6.1, 0), (pil[1], 0))) - 1.2
check("ligament window → clearance hole >= 1.0 CAD", lig >= 1.0 - 1e-6, round(lig, 2))
cols = [h for h in holes if abs(h["diameter"] - 2.8) < 0.01]
check("4 columns Ø8 at (±36, ±25) with Ø2.6 + HOLE_COMP pilots", len(cols) == 4 and sorted(
      (round(h["point_on_axis"][0]), round(h["point_on_axis"][1])) for h in cols) == [(-36, -25), (-36, 25), (36, -25), (36, 25)]
      and solid(36 + 3.9, 25, 30) and not solid(36 + 4.1, 25, 30), [h["point_on_axis"][:2] for h in cols])
check("column height 40 above the plate top", solid(36, 25 + 3, T + 39.9) and not solid(36, 25 + 3, T + 40.1), "top at z 46")
tie = [w(mx, my, a, *ns["TIE_UV"]) for (mx, my, a) in mounts]
check("SYS-5 tie slots beside each window", all(not solid(x, y, zm) for x, y in tie), [tuple(round(c, 1) for c in t) for t in tie])
check("tie slots >= 3 mm inside the outline", all(solid(*w(mx, my, a, ns["TIE_UV"][0], ns["TIE_UV"][1] - 3.9), zm)
                                                    for (mx, my, a) in mounts), "solid 3.9 mm further out")
check("LiPo strap slots 22 × 3 at y ±20", not solid(0, 20, zm) and not solid(0, -20, zm) and solid(0, 22, zm), "")
check("middle legs at y ±56 (hex_frame)", not solid(0, 56 - 5.5, zm) and not solid(0, -56 + 5.5, zm), "window centres")
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)

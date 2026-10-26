"""jobs/20261025-arm-upper-link/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261025-arm-upper-link/cad_checks.py
Exit code 0 = every check passed. Size and holes on build() (print frame: front face on the bed);
point probes on design() (frame U: back face z 0, front face z 10, ribs z -6 .. 0; see model.py).
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
d = ns["design"]()
failures = []


def check(name, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok:
        failures.append(name)


def solid(x, y, z):
    return d.is_inside((x, y, z))


def run(p0, p1, step=0.01):
    """Length of solid along the segment p0 -> p1 (sampled)."""
    n = max(1, int(math.dist(p0, p1) / step))
    return sum(math.dist(p0, p1) / n for i in range(n)
               if solid(*(a + (b - a) * (i + 0.5) / n for a, b in zip(p0, p1))))


T, HW, RIB_H = ns["T"], ns["HALF_W"], ns["RIB_H"]
WX0, WX1, WHW = ns["WIN_X0"], ns["WIN_X1"], ns["WIN_HW"]
RX0, RX1, TAPER = ns["RIB_X0"], ns["RIB_X1"], ns["RIB_TAPER"]
YR = (WHW + HW) / 2                                   # mid-rail, 13.6

# ---- CHECKS: one line per critical dimension in design_brief.md -----------------
check("overall size 146 × 34 × 16 (10 plate + 6 rib)", all(abs(a - b) < 0.01 for a, b in zip(size, [146.0, 34.0, 16.0])),
      size)
clamp = [h for h in holes if abs(h["diameter"] - 3.6) < 0.01 and abs(h["point_on_axis"][0]) < 0.01]
pil = sorted((round(h["point_on_axis"][0], 2), round(abs(h["point_on_axis"][1]), 2)) for h in holes
             if abs(h["diameter"] - 2.8) < 0.01)
check("shoulder clamp hole Ø3.4 + HOLE_COMP on the shoulder axis", len(clamp) == 1, [h["diameter"] for h in clamp])
check("4 elbow tab pilots Ø2.6 + HOLE_COMP at x 65.6 / 114.1, y ±5 (axis distance L 100)",
      pil == [(65.6, 5.0), (65.6, 5.0), (114.1, 5.0), (114.1, 5.0)], pil)
check("elbow window 41.3 × 20.3 CAD (41.1 × 20.1 printed)",
      abs((WX1 - WX0) - 41.3) < 0.01 and not solid(WX0 + 0.05, 6, 5) and solid(WX0 - 0.05, 6, 5)
      and not solid(WX1 - 0.05, 6, 5) and solid(WX1 + 0.05, 6, 5) and not solid(90, WHW - 0.05, 5)
      and solid(90, WHW + 0.05, 5), f"x {WX0:.2f}-{WX1:.2f}, y ±{WHW:.2f}")
check("lead notches 4.6 × 2.1 CAD at both case ends, through plate (4.4 × 2.0 printed)",
      not solid(67.45, 2.25, 5) and solid(67.33, 0, 5) and solid(68.0, 2.35, 5)
      and not solid(112.25, -2.25, 5) and solid(112.37, 0, 5), "far x 67.39-69.5, near x 110.2-112.31, y ±2.3")
lig = min(run((67.39, sy * 2.3, z), (65.6, sy * 5.0, z)) for sy in (1, -1) for z in (0.5, 9.5))
check("notch -> nearest pilot ligament >= 1.8 CAD (DFM round 4: 1.839)", lig >= 1.8, round(lig, 3))
check("plate T 10 between the pocket and the ribs", solid(30, 0, 0.05) and solid(30, 0, 9.95)
      and not solid(30, 0, -0.05) and not solid(30, 0, 10.05), "probe x 30, y 0")
check("horn pocket 2 deep on the back face, 8 mm floor", not solid(10, 0, 1.0) and solid(10, 0, 2.1) and solid(10, 0, 9.9),
      "probe on the arm slot, x 10")
check("rail ribs 6 deep on the back face (rails 6.85 × 16 at the window's far end)",
      all(solid(x, sy * YR, -RIB_H + 0.05) and not solid(x, sy * YR, -RIB_H - 0.05)
          for x in (WX0 + 0.2, 90.0, WX1 - 0.2) for sy in (1, -1))
      and abs(run((WX0 + 0.1, YR, -RIB_H - 0.5), (WX0 + 0.1, YR, T + 0.5)) - (T + RIB_H)) < 0.05,
      f"rail depth at x {WX0 + 0.1:.1f}: {run((WX0 + 0.1, YR, -RIB_H - 0.5), (WX0 + 0.1, YR, T + 0.5)):.2f}")
rail_w = run((90, 0, -3), (90, HW + 1, -3))
check("ribs exactly as wide as the rails: window wall to plate edge (6.85)", abs(rail_w - (HW - WHW)) < 0.03,
      f"rib at x 90: y {WHW:.2f}-{HW:g}, {rail_w:.2f} wide")
check("ribs full depth from 5 mm before the window (x 64.2) to x 117",
      solid(RX0 + 0.1, YR, -RIB_H + 0.05) and solid(RX1 - 0.1, 12.0, -RIB_H + 0.05)
      and not solid(RX1 + 0.1, 12.0, -1.0), f"x {RX0:.1f}-{RX1:g}")
check("45° run-out towards the shoulder, back face at x 58.2",
      solid(RX0 - 3.0, YR, -2.95) and not solid(RX0 - 3.0, YR, -3.05) and not solid(RX0 - TAPER - 0.1, YR, -0.05),
      "depth 3 at x 61.2, 0 at x 58.2")
check("nothing on the back face between the ribs (elbow servo case and its lead)",
      not any(solid(x, y, -0.5) for x in (60.0, 68.0, 90.0, 112.0, 116.0) for y in (0.0, 5.0, -9.9)),
      "probes at z -0.5, |y| <= 9.9")
check("no rib at the shoulder end (horn pocket, upright side)",
      not any(solid(x, y, -0.5) for x in (-20.0, 0.0, 20.0, 50.0) for y in (0.0, 13.6, -13.6)), "probes x <= 50")
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)

"""jobs/20261025-arm-forearm/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261025-arm-forearm/cad_checks.py
Exit code 0 = every check passed. Size and holes on build() (print frame: front face on the bed);
point probes on design() (frame F: back face z 0, front face z 10, ribs and cross-rib z -6 .. 0).
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
PX, BX0, RX1, TAPER = ns["FAR_PILOT_X"], ns["BOSS_X0"], ns["RIB_X1"], ns["TAPER"]
LPX, PD = ns["LEAD_PILOT_X"], ns["PILOT_D"]
X1 = ns["X1"]
YR = (WHW + HW) / 2                                   # mid-rail, 9.7

# ---- CHECKS: one line per critical dimension in design_brief.md -----------------
check("overall size 129 × 26 × 16 (10 plate + 6 rib)", all(abs(a - b) < 0.01 for a, b in zip(size, [129.0, 26.0, 16.0])),
      size)
clamp = [h for h in holes if abs(h["diameter"] - 3.6) < 0.01 and abs(h["point_on_axis"][0]) < 0.01]
check("elbow clamp hole Ø3.4 + HOLE_COMP on the elbow axis", len(clamp) == 1, [h["diameter"] for h in holes])
check("MG90S window 23.2 × 12.8 CAD at x 72.9-96.1 (23.0 × 12.6 printed; wrist axis L 90)",
      abs((WX1 - WX0) - 23.2) < 0.01 and abs(2 * WHW - 12.8) < 0.01 and not solid(WX0 + 0.05, 4, 5)
      and solid(WX0 - 0.05, 4, 5) and not solid(WX1 - 0.05, 4, 5) and solid(WX1 + 0.05, 4, 5)
      and not solid(85, WHW - 0.05, 5) and solid(85, WHW + 0.05, 5), f"x {WX0:.2f}-{WX1:.2f}, y ±{WHW:.2f}")
check("lead notch 4.4 × 1.6 CAD at the shaft end (4.2 × 1.5 printed)", not solid(97.45, 0, 5) and not solid(97.45, 2.15, 5)
      and solid(97.6, 0, 5) and solid(96.5, 2.25, 5), "x 95.9-97.51, y ±2.2")
s_lead = run((97.0, 0, 5), (99.7, 0, 5))
s_far = run((PX, 0, 5), (WX0 + 0.5, 0, 5))
s_far_rib = run((PX, 0, -3), (WX0 + 0.5, 0, -3))
check("screw strips as the user decided on 26 Oct (lead end 1.34, far end 1.45 CAD; spec §8 first-print check)",
      abs(s_lead - 1.34) < 0.02 and abs(s_far - 1.45) < 0.02 and abs(s_far_rib - 1.45) < 0.02,
      f"lead end {s_lead:.3f}, far end {s_far:.3f} (plate) / {s_far_rib:.3f} (cross-rib)")
pil = sorted((round(h["point_on_axis"][0], 2), round(abs(h["point_on_axis"][1]), 2)) for h in holes
             if abs(h["diameter"] - 1.7) < 0.01 and h["arc_deg"] > 300)
check("both MG90S tab pilots ROUND Ø1.5 + HOLE_COMP = Ø1.7 CAD at x 70.6 / 99.7, y 0 (links strength round 5)",
      abs(PD - 1.7) < 1e-9 and pil == [(70.6, 0.0), (99.7, 0.0)], pil)
r = PD / 2
lead_out = run((LPX + r - 0.3, 0, 5), (LPX + r + 0.8, 0, 5))
far_out = min(run((PX - r - 0.8, 0, z), (PX - r + 0.3, 0, z)) for z in (-5.9, -3, 5))
check("no outward slot: solid from the pilot edge outward (lead end x 100.55, far end x 69.75)",
      abs(lead_out - 0.8) < 0.02 and abs(far_out - 0.8) < 0.02 and not solid(LPX + r - 0.05, 0, 5)
      and not solid(PX - r + 0.05, 0, -3), f"solid beyond the edge: lead {lead_out:.2f} / 0.80, far {far_out:.2f} / 0.80")
check("lead-end pilot moved 1.3 mm out: x 99.7, round, 3.45 CAD to the plate end",
      abs(LPX - 99.7) < 1e-9 and not solid(99.7, 0, 5) and solid(99.7, r + 0.05, 5)
      and abs(run((LPX, 0, 5), (X1 + 1, 0, 5)) - (X1 - LPX - r)) < 0.02,
      f"x {LPX - r:.2f}-{LPX + r:.2f}, plate end x {X1:g}: {run((LPX, 0, 5), (X1 + 1, 0, 5)):.2f}")
far_depth = run((PX, 0, -RIB_H - 1), (PX, 0, T + 1))
check("far pilot open through plate + cross-rib (16 deep: M2 × 16, 13.5 engaged; strength asks >= 14)",
      far_depth < 0.01 and not solid(PX, r - 0.05, -5.9) and solid(PX, r + 0.05, -5.9),
      f"solid on the axis z -7..11: {far_depth:.3f}")
wall = run((BX0 - 0.5, 0, -RIB_H + 0.01), (PX, 0, -RIB_H + 0.01))
check("cross-rib wall beyond the far pilot >= 2.4 at full depth (x 66.9-69.75: 2.85 since the pilot is round)",
      wall >= 2.4 and abs(wall - (PX - r - BX0)) < 0.03, round(wall, 2))
check("cross-rib full width, full depth from x 66.9 to the window (x 72.9)",
      all(solid(x, y, -RIB_H + 0.05) for x in (BX0 + 0.1, 68.0, WX0 - 0.1) for y in (-11.0, -3.0, 0.5, 3.0, 11.0) if
          not (abs(y) < 1.0 and PX - 1.4 < x < PX + 1.0)) and not solid(BX0 + 0.1, 0, -RIB_H - 0.05),
      f"x {BX0:.2f}-{WX0:.2f}")
check("rail ribs 6 deep, as wide as the rails (6.6), rails 6.6 × 16 at the window's far end",
      all(solid(x, sy * YR, -RIB_H + 0.05) and not solid(x, sy * YR, -RIB_H - 0.05)
          for x in (WX0 + 0.2, 85.0, WX1 - 0.2) for sy in (1, -1))
      and abs(run((85, 0, -3), (85, HW + 1, -3)) - (HW - WHW)) < 0.03
      and abs(run((WX0 + 0.1, YR, -RIB_H - 0.5), (WX0 + 0.1, YR, T + 0.5)) - (T + RIB_H)) < 0.05,
      f"rib at x 85: {run((85, 0, -3), (85, HW + 1, -3)):.2f} wide")
check("ribs run 5 mm past the window's lead end (x 101.1), then stop",
      solid(RX1 - 0.1, 9.0, -RIB_H + 0.05) and not solid(RX1 + 0.1, 9.0, -1.0), f"x {RX1:.1f}")
check("lead end open between the ribs (the MG90S lead leaves the case end 3.4 below the back face)",
      not any(solid(x, y, z) for x in (96.5, 98.0, 100.0, 101.0) for y in (0.0, 3.0, -6.3) for z in (-0.5, -3.4, -5.9)),
      "probes x 96.5-101, |y| <= 6.3, z -0.5 .. -5.9")
check("45° run-out towards the elbow, back face at x 60.9",
      solid(BX0 - 3.0, 0, -2.95) and not solid(BX0 - 3.0, 0, -3.05) and not solid(BX0 - TAPER - 0.1, 0, -0.05),
      "depth 3 at x 63.9")
check("nothing else on the back face (horn pocket end)", not any(solid(x, y, -0.5) for x in (-20.0, 0.0, 30.0, 59.0)
                                                                  for y in (0.0, 9.0, -9.0)), "probes x <= 59")
check("horn pocket 2 deep on the back face, 8 mm floor", not solid(10, 0, 1.0) and solid(10, 0, 2.1) and solid(10, 0, 9.9),
      "probe on the arm slot, x 10")
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)

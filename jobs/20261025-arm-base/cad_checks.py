"""jobs/20261025-arm-base/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261025-arm-base/cad_checks.py
Exit code 0 = every check passed. Size and holes on build() (print frame: upside down, top plate on
the bed); point probes on design() (assembly frame: top-plate top Z 0, plate Z -4 .. 0, desk Z -40).
The ESP32 and cradle envelopes come from the cradle's model.py and tools/hobby_parts.py, as
assembly_check.py places them.
"""
import math
import runpy
import sys
from pathlib import Path

JOB = Path(__file__).resolve().parent
sys.path.insert(0, str(JOB.parents[1] / "tools"))
from cadlib import bbox, measure_holes  # noqa: E402
from hobby_parts import ESP32_DEVKIT_30, ESP32_DEVKIT_38  # noqa: E402

ns = runpy.run_path(str(JOB / "model.py"), run_name="model")
cr = runpy.run_path(str(JOB.parent / "20261025-arm-esp32-cradle" / "model.py"), run_name="model")
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


def grid(x0, x1, y0, y1, z0, z1, n=6):
    return [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * j / n, z0 + (z1 - z0) * k / n)
            for i in range(n + 1) for j in range(n + 1) for k in range(n + 1)]


PT, TF, TN = ns["PLATE_T"], ns["PAD_T_FAR"], ns["PAD_T_NEAR"]
XF, XN = ns["TAB_X_FAR"], ns["TAB_X_NEAR"]
fx0, fx1, fy0, fy1 = ns["PAD_FAR"]
nx0, nx1, ny0, ny1 = ns["PAD_NEAR"]

# ---- CHECKS: one line per critical dimension in design_brief.md -----------------
check("overall size 110 × 104 × 40", all(abs(a - b) < 0.01 for a, b in zip(size, [110.0, 104.0, 40.0])), size)
d28 = sorted((round(h["point_on_axis"][0], 2), round(abs(h["point_on_axis"][1]), 2)) for h in holes
             if abs(h["diameter"] - 2.8) < 0.01)
check("10 pilots Ø2.6 + HOLE_COMP: 4 servo tabs (48.5 × 10 pattern), 3 ring (r 47.5), 3 cradle", len(d28) == 10
      and [p for p in d28 if p in ((-34.4, 5.0), (14.1, 5.0))] == [(-34.4, 5.0)] * 2 + [(14.1, 5.0)] * 2, d28)
check("4 desk holes Ø3.4 + HOLE_COMP, DC jack Ø11.4 + HOLE_COMP", sorted(h["diameter"] for h in holes
                                                                       if h["diameter"] > 3)
      == [3.6, 3.6, 3.6, 3.6, 11.6], sorted(h["diameter"] for h in holes if h["diameter"] > 3))
check("top plate 4 mm away from the servo", solid(0, 30, -PT + 0.05) and not solid(0, 30, -PT - 0.05)
      and solid(-30, -30, -PT + 0.05) and not solid(-30, -30, -PT - 0.05), "probes (0, 30), (-30, -30)")
check("far-tab pad: plate 7.5 thick round the far tab (x -52 .. -19.4, |y| <= 20.5)",
      all(solid(x, y, -TF + 0.05) and not solid(x, y, -TF - 0.05)
          for x, y in ((-45, 0), (-40, 15), (-40, -15), (-25, 15), (-25, -15), (-50, 20)))
      and solid(fx1 - 0.1, 15, -TF + 0.1) and not solid(fx1 + 0.1, 15, -TF + 0.1)
      and solid(-40, fy1 - 0.1, -TF + 0.1) and not solid(-40, fy1 + 0.1, -TF + 0.1)
      and not solid(-40, fy0 - 0.1, -TF + 0.1), f"x {fx0}..{fx1}, y {fy0}..{fy1}")
check("pad >= 15 mm round both far bosses (x -34.4, y ±5)", fx1 - XF >= 14.99 and fy1 - 5 >= 15 and -fy0 - 5 >= 15
      and XF - (-52.0) >= 15, f"to x {fx1}, y ±{fy1}, wall at x -52")
check("near-tab pad: plate 5.5 thick round the near tab (x -0.9 .. 29.1, y -20 .. 18)",
      all(solid(x, y, -TN + 0.05) and not solid(x, y, -TN - 0.05) for x, y in ((25, 0), (20, 15), (5, -15), (25, -19)))
      and solid(nx1 - 0.1, 0, -TN + 0.1) and not solid(nx1 + 0.1, 0, -TN + 0.1)
      and solid(20, ny1 - 0.1, -TN + 0.1) and not solid(20, ny1 + 0.1, -TN + 0.1)
      and solid(20, ny0 + 0.1, -TN + 0.1) and not solid(20, ny0 - 0.1, -TN + 0.1), f"x {nx0}..{nx1}, y {ny0}..{ny1}")
check("pad >= 15 mm round the near bosses (x 14.1, y ±5) except towards the ESP32 (+y: 13)",
      nx1 - XN >= 14.99 and XN - nx0 >= 14.99 and -ny0 - 5 >= 15 and ny1 - 5 >= 13, f"x {nx0}..{nx1}, y {ny0}..{ny1}")
check("servo window 41.3 × 20.3 CAD through plate, pads and bosses", not solid(-30.6, 6, -TF + 0.2)
      and solid(-30.8, 6, -TF + 0.2) and not solid(10.3, 6, -TN + 0.2) and solid(10.5, 6, -TN + 0.2)
      and not solid(0, 10.1, -2) and solid(0, 10.2, -2), "x -30.7..10.4, y ±10.15")
check("lead notches 4.6 × 2.1 CAD at both case ends, through plate + pad (4.4 × 2.0 printed)",
      all(not solid(x, y, z) for x in (-32.55, 12.25) for y in (0, 2.25, -2.25) for z in (-0.1, -3.9, -5.4))
      and not solid(-32.55, 0, -TF + 0.1) and solid(-32.7, 0, -TF + 0.1) and solid(12.4, 0, -TN + 0.1)
      and solid(-31.5, 2.4, -6.0) and solid(11.5, -2.4, -5.0), "far x -32.61..-30.5, near x 10.2..12.31, y ±2.3")
lig = min(run((sx_n, sy * 2.3, z), (sx_p, sy * 5.0, z))
          for sx_n, sx_p, zs in ((-32.61, XF, (-1.0, -3.0, -6.5)), (12.31, XN, (-1.0, -3.0, -5.0)))
          for sy in (1, -1) for z in zs)
check("notch -> nearest pilot ligament >= 1.8 CAD in plate and pads (DFM round 4: 1.839)", lig >= 1.8, round(lig, 3))
check("servo tab pilots open through plate, pad and boss (10 deep: M3 × 12 + washer, 9 engaged)",
      all(run((x, y, 0.5), (x, y, -10.5)) < 0.01 for x in (XF, XN) for y in (5, -5))
      and solid(XF, 5 + 1.6, -9.9) and solid(XN, 5 + 1.6, -9.9), "on the 4 pilot axes Z 0.5 .. -10.5")
cp = [run((x, y, -10.5), (x, y, 0)) for x, y in ns["CRADLE_PILOTS"]]
check("cradle pilots Ø2.8 CAD from the boss end (Z -10) to Z -3: 7 deep, 3 mm of plate left (M3 × 10: 1 mm margin)",
      all(abs(c - 3.0) < 0.03 for c in cp) and all(not solid(x, y, -3.1) and solid(x, y, -2.9) and not solid(x, y, -9.9)
                                                  for x, y in ns["CRADLE_PILOTS"]), f"solid above each pilot: {cp}")
# clearances to the ESP32 cradle, the board on it and its USB slot (assembly_check places the same envelopes)
yc, x_usb, top = cr["YC"], cr["USB_END_X"], cr["TOP"]
b = max((ESP32_DEVKIT_38, ESP32_DEVKIT_30), key=lambda s: s.length)
board = grid(x_usb - b.length, x_usb, yc - b.width / 2, yc + b.width / 2, -11.6, -10.0 + b.parts_above)
can = grid(x_usb - b.length, x_usb - b.length + 18, yc - 8, yc + 8, -10.0, -6.8)
hit_board = [p for p in board if solid(*p)]
check("ESP32 envelope (PCB + parts 4 mm above it, Z -11.6 .. -6) is free of base material", not hit_board and not
      [p for p in can if solid(*p)], f"{len(board)} probes, {len(hit_board)} hit")
gap_can = min(math.hypot(0, (yc - 8) - ny1), 99.0)
check("near pad stops >= 2 mm short of the module can (y >= 20) and 4.5 above the cradle's frame (Z -10)",
      gap_can >= 2.0 and (-TN) - top >= 4.5, f"pad edge y {ny1}, can from y {yc - 8:g}; pad underside Z {-TN}, frame top Z {top}")
check("cradle bosses (Ø7, Z -4 .. -10) stand clear of both pads",
      all(not solid(x + 3.6 * math.cos(a), y + 3.6 * math.sin(a), -4.5)
          for x, y in ns["CRADLE_PILOTS"] for a in [i * math.pi / 8 for i in range(16)]),
      "a ring of probes 0.1 outside each boss, Z -4.5")
check("USB slot 13 × 7 in the +X wall at (y 28, Z -8.5) open", not solid(53.5, 28, -8.5) and not solid(53.5, 22, -6)
      and not solid(53.5, 34, -11) and solid(53.5, 20.5, -8.5), "probes in the wall, x 53.5")
check("cable slot (-40, -36) and ring pilots open, clear of the far pad", not solid(-40, -36, -2)
      and not solid(-41.14, 23.75, -2) and not solid(41.14, 23.75, -2) and not solid(0, -47.5, -2)
      and not solid(-41.14, 21.6, -4.5), "pad edge y 20.5, 150° pilot from y 22.35")
check("DC jack teardrop open, clear of the far pad", not solid(-53.5, -28, -20) and not solid(-50, -21.0, -6.0),
      "jack at y -28, Z -20")
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)

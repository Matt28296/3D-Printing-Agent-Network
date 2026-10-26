"""jobs/20261026-arm-claw-frame/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261026-arm-claw-frame/cad_checks.py
Exit code 0 = every check passed. Probes use design(), in claw frame G (= print frame: back face on the bed).
"""
import runpy
import sys
from pathlib import Path

JOB = Path(__file__).resolve().parent
sys.path.insert(0, str(JOB.parents[1] / "tools"))
from build123d import Vector  # noqa: E402
from cadlib import bbox, measure_holes  # noqa: E402

ns = runpy.run_path(str(JOB / "model.py"), run_name="model")
part = ns["build"]()
d = ns["design"]()
size = bbox(part)["size"]
holes = measure_holes(part)
failures = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok:
        failures.append(name)


def solid(x, y, z):
    return d.is_inside(Vector(x, y, z))


# ---- CHECKS: one line per critical dimension in design_brief.md -----------------
check("overall size 42.85 x 64 x 48.45 (bulkhead top 48.45 since round 6)",
      all(abs(a - b) < 0.01 for a, b in zip(size, [42.85, 64.0, 48.45])), size)
check("one solid", len(part.solids()) == 1, len(part.solids()))
dia = sorted(round(h["diameter"], 2) for h in holes)
check("holes: clamp Ø2.6, 3 x M3 pilot Ø2.7 (2 top + the cover's anchor), 2 x M2.5 pilot Ø2.2",
      dia == [2.2, 2.2, 2.6, 2.7, 2.7, 2.7], dia)
anc = [h for h in holes if abs(h["diameter"] - 2.7) < 0.01 and abs(h["point_on_axis"][0] - 18.35) < 0.01
       and abs(h["point_on_axis"][1] - 28.0) < 0.01 and abs(abs(h["axis"][2]) - 1) < 1e-6]
check("anchor M3 pilot Ø2.5 + HOLE_COMP = Ø2.7 CAD, vertical, at (18.35, 28) in the rail block (claw strength round 3)",
      len(anc) == 1, [(h["point_on_axis"], h["arc_deg"]) for h in anc])
check("anchor pilot 14 deep from the block's top (z 17.75 -> 3.75), floor below it",
      not solid(18.35, 28, 17.0) and not solid(18.35, 28, 3.85) and solid(18.35, 28, 3.65)
      and not solid(18.35 + 1.3, 28, 10) and solid(18.35 + 1.4, 28, 10) and not solid(18.35, 28 + 1.3, 10)
      and solid(18.35, 28 + 1.4, 10), "Ø2.7, z 3.75..17.75")
check("rail block keeps 2.65 round the anchor pilot (front face x 22.35, +y end y 32; frame strength: root SF 5.93)",
      solid(18.35 + 1.4, 28, 12) and solid(22.3, 28, 12) and not solid(22.4, 28, 12)
      and solid(18.35, 29.4, 12) and solid(18.35, 31.9, 12) and not solid(18.35, 32.1, 12)
      and solid(14.6, 28, 12) and solid(18.35, 26.6, 12), "x 19.7..22.35, y 29.35..32 at z 12")
check("anchor pilot clear of the +y front M2.5 pilot (x >= 20.85, y 22.9..25.1, z 1.4..3.6 since round 7)",
      solid(20.9, 25.6, 3.0) and solid(19.7, 26.0, 3.9) and solid(20.3, 25.0, 3.0) and solid(20.3, 26.7, 3.7),
      "solid between them")
zf_ = ns["FRONT_SCREWS"][0][1]
check("front M2.5 pilots Ø2.2 CAD at y +-24, z 2.5 (round 7: 3 -> 2.5), 14 deep from x 34.85 (to x 20.85), flat top at "
      "z 3.6: 2.4 skin to rack B's track (z 6), 1.4 to the back face (z 0)",
      abs(zf_ - 2.5) < 1e-9 and all(not solid(x, y, 2.5) and not solid(x, y, 3.55) and solid(x, y, 3.65)
                                    and not solid(x, y, 1.45) and solid(x, y, 1.35)
                                    and not solid(x, y + 1.05, 2.5) and solid(x, y + 1.15, 2.5)
                                    for y in (-24.0, 24.0) for x in (21.0, 28.0, 34.8))
      and all(solid(20.75, y, 2.5) and solid(28.0, y, 5.95) and solid(28.0, y, 0.05) for y in (-24.0, 24.0)),
      f"z {zf_}")
xc, zb = ns["VSEAT_XC"], 17.75 - ns["VSEAT_D"]
check("V-groove (round 5) in the rail block's top: 90°, 0.8 deep (bottom z 16.95) on x 15.25, x 14.45..16.05 at z 17.75, "
      "y 23.5..32 open at +y", abs(xc - 15.25) < 1e-9 and abs(zb - 16.95) < 1e-9
      and all(not solid(xc + s * (z - zb - 0.05), y, z) and solid(xc + s * (z - zb + 0.05), y, z)
              for s in (-1, 1) for z in (17.1, 17.4, 17.7) for y in (23.6, 28.0, 31.9))
      and solid(xc, 28, 16.9) and not solid(xc, 28, 17.0) and solid(xc, 23.4, 17.5) and not solid(xc, 23.6, 17.5)
      and solid(14.4, 28, 17.7) and solid(16.1, 28, 17.7), "flanks probed ±0.05 at z 17.1 / 17.4 / 17.7, y 23.6 / 28 / 31.9")
check("0.95 of block between the groove and the anchor pilot at the top (x 16.05..17.0), widening downward",
      solid(16.1, 28, 17.7) and solid(16.95, 28, 17.7) and not solid(17.05, 28, 17.7) and solid(16.4, 28, 17.4)
      and not solid(15.95, 28, 17.7), "x 16.05..17.0 at z 17.7")
check("wrist plate top (rack B's guide) z 6.0", solid(30, 0, 5.9) and not solid(30, 0, 6.1))
check("wrist plate front edge x 34.85", solid(34.8, 0, 3) and not solid(34.9, 0, 3))
check("rail block from the bulkhead's front face (x 10) to x 22.35, z 6..17.75", solid(10.1, 0, 12) and solid(22.3, 31.9, 17.7)
      and not solid(22.4, 0, 12) and not solid(15, 0, 17.85))
bt = ns["BULK_TOP"]
check("bulkhead x 3.5..10, top z 48.45 (BULK_TOP, round 6; the cover's top wall stays at 48.5, 0.05 over it in CAD)",
      abs(bt - 48.45) < 1e-9 and solid(3.6, 20, 45) and solid(9.9, 20, 45) and not solid(10.1, 20, 45)
      and solid(6.75, 20, bt - 0.02) and not solid(6.75, 20, bt + 0.02)
      and all(solid(-6.4, s * 29, bt - 0.02) and not solid(-6.4, s * 29, bt + 0.02) for s in (-1, 1)),
      "bulkhead and both ribs probed ±0.02 about 48.45")
# PrusaSlicer slices every 0.2 mm layer at its mid-height (first layer 0.2): slice planes at 0.1 + 0.2 k. A horizontal
# face ON a slice plane prints a layer high or low by floating-point rounding (round 5: 48.5 printed at 48.4).
d_plane = min(abs(bt - (0.1 + 0.2 * k)) for k in range(400))
check("bulkhead top off the 0.2 mm slice planes (>= 0.04 to the nearest; prints at 48.4 with 0.05 to 48.3 and 48.5)",
      d_plane >= 0.04 - 1e-9, f"nearest slice plane {d_plane:.3f} away")
check("top M3 pilots Ø2.7 CAD, 14 deep below the bulkhead top (floor z 34.45)",
      all(not solid(x, y, bt - 1) and not solid(x, y, 34.55) and solid(x, y, 34.35) for x, y in ns["TOP_SCREWS"]),
      f"{ns['TOP_SCREWS']}")
check("clamp floor 6.3: pocket ceiling z 2.0, pad top z 8.3 (washer seat whole)", not solid(5.0, 0, 1.9) and solid(5.0, 0, 2.1)
      and solid(0, 3.5, 8.2) and solid(3.3, 0, 8.2) and not solid(0, 3.5, 8.4))
check("Ø8 washer relief: r 4.5 into the bulkhead's back face, pad to top", not solid(4.4, 0, 9.0) and not solid(4.4, 0, 15)
      and not solid(4.4, 0, 45) and solid(4.6, 0, 15) and solid(3.6, 3.0, 15))
check("r 1.5 fillet at the pad / bulkhead back corner (outside the relief)", solid(3.3, 10, 8.45) and solid(3.0, 10, 8.6)
      and not solid(2.5, 10, 9.0) and not solid(3.4, 10, 9.9) and not solid(1.9, 10, 8.4))
check("ribs 6 x 10 behind the bulkhead's outer edges, pad to top", all(solid(-6.4, s * 29, z) for s in (-1, 1) for z in (8.5, 48.4))
      and not solid(-6.6, 29, 30) and not solid(-3, -25.9, 30) and not solid(-3, 25.9, 30))
check("MG90S window 23.2 x 12.8 CAD: y -17.1..6.1, z 20.85..33.65", not solid(6.75, -17.0, 27.25) and solid(6.75, -17.3, 27.25)
      and not solid(6.75, 0, 20.9) and solid(6.75, -5, 20.7))
check("lead notch y 6.1..7.5, z 25.05..29.45 with a 45° top (y + z - 27.25 < 9.7)", not solid(6.75, 7.4, 26) and solid(6.75, 7.6, 26)
      and not solid(6.75, 6.5, 29.8) and solid(6.75, 7.3, 30.0) and not solid(6.75, 6.3, 30.6))
check("claw-servo axis y 0, z 27.25: tab pilots at y -19.4 and +9.7 (slots 0.4 outwards)",
      not solid(6.75, -19.4, 27.25) and not solid(6.75, 9.7, 27.25) and solid(6.75, -18.4, 27.25) and solid(6.75, 8.75, 27.25))
check("window roof 45°, flat at z 40.65", not solid(6.75, -5, 40.6) and solid(6.75, -5, 40.7))
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)

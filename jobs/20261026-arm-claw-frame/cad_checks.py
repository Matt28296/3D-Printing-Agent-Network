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
check("overall size 42.85 x 64 x 48.5", all(abs(a - b) < 0.01 for a, b in zip(size, [42.85, 64.0, 48.5])), size)
check("one solid", len(part.solids()) == 1, len(part.solids()))
dia = sorted(round(h["diameter"], 2) for h in holes)
check("holes: clamp Ø2.6, 2 x M3 pilot Ø2.7, 2 x M2.5 pilot Ø2.2", dia == [2.2, 2.2, 2.6, 2.7, 2.7], dia)
check("wrist plate top (rack B's guide) z 6.0", solid(30, 0, 5.9) and not solid(30, 0, 6.1))
check("wrist plate front edge x 34.85", solid(34.8, 0, 3) and not solid(34.9, 0, 3))
check("rail block from the bulkhead's front face (x 10) to x 22.35, z 6..17.75", solid(10.1, 0, 12) and solid(22.3, 31.9, 17.7)
      and not solid(22.4, 0, 12) and not solid(15, 0, 17.85))
check("bulkhead x 3.5..10, top z 48.5", solid(3.6, 20, 45) and solid(9.9, 20, 45) and not solid(10.1, 20, 45)
      and not solid(6.75, 20, 48.6))
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

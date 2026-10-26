"""jobs/20261026-rover-idler/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261026-rover-idler/cad_checks.py
Exit code 0 = every check passed. Probes use design() (idler frame = sprocket frame).
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


def check(name, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok:
        failures.append(name)


def solid(x, y, z):
    return d.is_inside(Vector(x, y, z))


# ---- CHECKS: one line per critical dimension in design_brief.md -----------------
check("overall size Ø35.8 tips × 20.0", all(abs(a - b) < 0.02 for a, b in zip(size, [35.777, 34.52, 20.0])), size)
check("running bore Ø3.7 CAD (3.5 printed, 0.5 clearance on M3), through", [h["diameter"] for h in holes] == [3.7], holes)
check("hub Ø10 from the wall washer (z -16.5) to the disc", solid(4.9, 0, -16.4) and not solid(5.1, 0, -10)
      and not solid(3.0, 0, -16.6), "")
check("disc ±3.5 and teeth to r 17.9 (same as the sprocket)", solid(17.8, 0, 0) and not solid(18.0, 0, 0)
      and not solid(11.0, 3.6, 3.55), "")
check("the sprocket's spacer and slots are not on the idler", solid(6.35 * 0.7071, 6.35 * 0.7071, -3.0), "")
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)

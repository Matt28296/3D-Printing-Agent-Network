"""jobs/20261026-rover-track-link/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261026-rover-track-link/cad_checks.py
Exit code 0 = every check passed. Probes use design() (link frame: hinges on x 0 and x 10, mid-plane z 0).
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
holes = measure_holes(d)
failures = []


def check(name, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok:
        failures.append(name)


def solid(x, y, z):
    return d.is_inside(Vector(x, y, z))


run = [h for h in holes if abs(h["point_on_axis"][0]) < 0.01]
grip = [h for h in holes if abs(h["point_on_axis"][0] - 10.0) < 0.01]
# ---- CHECKS: one line per critical dimension in design_brief.md -----------------
check("overall size 16 × 24 × 7.5", all(abs(a - b) < 0.02 for a, b in zip(size, [16.0, 24.0, 7.5])), size)
check("pitch 10.00 (hinge axes x 0 and x 10)", bool(run) and bool(grip), [h["point_on_axis"] for h in holes])
check("centre-knuckle running hole Ø2.5 CAD (PIN_RUN_CLR 0.3: ~Ø2.3 printed on a Ø2.0 pin)",
      [h["diameter"] for h in run] == [2.5], run)
check("outer-knuckle grip holes Ø2.2 CAD (~Ø2.0 printed)", [h["diameter"] for h in grip] == [2.2], grip)
check("knuckle wall round the running hole 3.0 - 1.25 = 1.75 (>= 4 lines at 0.41 spacing: 1.68); "
      "the teardrop side (-z here, up in print) keeps 3.0 - 1.77 = 1.23",
      solid(0, 0, 1.30) and not solid(0, 0, 1.20) and solid(0, 0, 2.95) and 3.0 - 1.25 >= 0.45 + 3 * 0.41
      and not solid(0, 0, -1.70) and solid(0, 0, -1.85), "")
check("knuckle gaps: 0.5 axial at |y| 6.75-7.25", not solid(10.0, 7.0, 2.0) and solid(10.0, 7.4, 2.0), "")
check("tooth notch |y| <= 4 open towards the front", not solid(6.0, 3.9, 0) and solid(6.0, 4.1, 0), "")
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)

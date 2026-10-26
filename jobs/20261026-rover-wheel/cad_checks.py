"""jobs/20261026-rover-wheel/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261026-rover-wheel/cad_checks.py
Exit code 0 = every check passed. Bed-face probes use build() (print frame, bed at z 0, axis at x = y = 0).
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
size = bbox(part)["size"]
holes = measure_holes(part)
failures = []
bb = part.bounding_box()
cx, cy = (bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2


def check(name, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok:
        failures.append(name)


def solid(r, z):
    return part.is_inside(Vector(cx + r, cy, z))


# ---- CHECKS: one line per critical dimension in design_brief.md -----------------
check("overall size Ø32.2 × 32.5", all(abs(a - b) < 0.02 for a, b in zip(size, [32.201, 32.201, 32.5])), size)
check("running bore Ø3.7 CAD (3.5 printed)", [h["diameter"] for h in holes] == [3.7], holes)
check("rim radius 13.1 at mid-width", solid(13.0, 16.0) and not solid(13.2, 16.0), "")
check("0.4 × 45° chamfer on the outer flange's bed edge", not solid(16.0, 0.1) and solid(15.6, 0.1) and solid(16.0, 0.6), "")
check("0.4 × 45° chamfer at the bore mouth on the bed", not solid(2.05, 0.1) and solid(2.05, 0.6), "")
check("bed face is the outer flange (min z 0)", abs(bb.min.Z) < 1e-6, round(bb.min.Z, 4))
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)

"""jobs/20261026-hexapod-body-top/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261026-hexapod-body-top/cad_checks.py
Exit code 0 = every check passed. Body frame, deck underside at Z = 0.
"""
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


def holes_d(d):
    return sorted((round(h["point_on_axis"][0], 1), round(h["point_on_axis"][1], 1)) for h in holes if abs(h["diameter"] - d) < 0.01)


zm = ns["T_TOP"] / 2

# ---- CHECKS: one line per critical dimension in design_brief.md -----------------
check("overall size 130 × 104 × 8", all(abs(a - b) < 0.05 for a, b in zip(size, [130.0, 104.0, 8.0])), size)
check("4 deck screw holes Ø3.4 + HOLE_COMP on the columns (±36, ±25)",
      holes_d(3.6) == [(-36.0, -25.0), (-36.0, 25.0), (36.0, -25.0), (36.0, 25.0)], holes_d(3.6))
check("8 PCA9685 post pilots Ø2.2 + HOLE_COMP on 56 × 19 at y ±34.5",
      holes_d(2.4) == sorted((x, y) for x in (-28.0, 28.0) for y in (-44.0, -25.0, 25.0, 44.0)), holes_d(2.4))
check("ESP32 pocket width 29.7 CAD (28.3 board + 2 × 0.6 + HOLE_COMP)", abs(2 * ns["HALF"] - 29.7) < 0.01, 2 * ns["HALF"])
check("SYS-10 switch hole Ø12 + HOLE_COMP at (-50, 0)", holes_d(12.2) == [(-50.0, 0.0)], holes_d(12.2))
ok = all(not solid(x, s * 50.0, zm) and solid(x, s * 46.5, zm) for x in (-40.0, 0.0, 40.0) for s in (-1, 1))
check("SYS-4 lead notches 10 × 5 at x -40, 0, 40 in both long edges", ok, "void at y ±50, solid at ±46.5")
tie = [(x - 8.5 if x > 0 else x + 8.5, s * 49.5) for x in (-40.0, 0.0, 40.0) for s in (-1, 1)]
check("tie slot beside each lead notch", all(not solid(x, y, zm) for x, y in tie), tie)
check("screw heads (Ø6) clear of the PCA9685 boards (x ±31.25) by >= 1.7",min(abs(x) for x, _ in ns["SCREWS"]) - 3.0 - 31.25 >= 1.7,
      min(abs(x) for x, _ in ns["SCREWS"]) - 3.0 - 31.25)
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)

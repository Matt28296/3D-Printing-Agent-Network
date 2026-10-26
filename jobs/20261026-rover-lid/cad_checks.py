"""jobs/20261026-rover-lid/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261026-rover-lid/cad_checks.py
Exit code 0 = every check passed. Probes use design() in the rover world frame.
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
F = sys.modules["rover_frame"]
zm = F.TOP_Z + ns["T"] / 2


def check(name, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok:
        failures.append(name)


def solid(x, y, z=zm):
    return d.is_inside(Vector(x, y, z))


screws = sorted(tuple(round(v, 2) for v in h["point_on_axis"][:2]) for h in holes if abs(h["diameter"] - 3.6) < 0.02)
# ---- CHECKS: one line per critical dimension in design_brief.md -----------------
check("overall size 154 × 76 × 7.1", all(abs(a - b) < 0.02 for a, b in zip(size, [154.0, 76.0, 7.1])), size)
check("4 screw holes Ø3.6 CAD (M3 clearance) on the chassis insert columns",
      screws == sorted(tuple(float(v) for v in p) for p in F.LID_SCREWS), screws)
sw = [h for h in holes if abs(h["diameter"] - 6.4) < 0.02]
check("toggle-switch hole Ø6.4 CAD (6.2 printed, M6 bushing) at (0, -23)",
      len(sw) == 1 and abs(sw[0]["point_on_axis"][0]) < 0.01 and abs(sw[0]["point_on_axis"][1] + 23) < 0.01, sw)
check("ESP32 pocket width 29.7", not solid(30, 14.8, zm + 3.5) and solid(30, 14.9, zm + 3.5), "")
for s in (1, -1):
    check(f"cable slot {'left' if s > 0 else 'right'}: open over x 71-81, |y| 1.5-12",
          not solid(76, s * 2.0) and not solid(76, s * 11.5) and not solid(71.5, s * 6) and not solid(80.5, s * 6), "")
check("3 mm tie bar between the slots (|y| <= 1.4 CAD)", solid(76, 0) and solid(76, 1.3) and not solid(76, 1.5), "")
check("slots clear of the ESP32 seat (x <= 69) and the breadboard (x >= 84)", solid(70.5, 6) and solid(83, 6), "")
check("old Ø10 cable hole gone", not [h for h in holes if abs(h["diameter"] - 10.2) < 0.05], "")
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)

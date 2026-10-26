"""jobs/20261026-hexapod-femur/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261026-hexapod-femur/cad_checks.py
Exit code 0 = every check passed. Frame F, z up in print (the back face, z 0, is on the bed).
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


L_F, zm = ns["L_F"], ns["T_F"] / 2
wx0, wx1 = L_F - 16.9 - 0.2, L_F + 5.9 + 0.2           # window 27.9 … 51.1
vert = sorted(round(h["diameter"], 2) for h in holes if abs(h["axis"][2]) > 0.99)

# ---- CHECKS: one line per critical dimension in design_brief.md -----------------
check("overall size 64.9 × 19.0 × 7.0", all(abs(a - b) < 0.05 for a, b in zip(size, [64.9, 19.0, 7.0])), size)
check("femur axis → knee 45.0 (window from the MG90S spec, 23.2 × 12.8 CAD)",
      not solid(wx0 + 0.05, 6.35, zm) and solid(wx0 - 0.05, 0, zm) and not solid(wx1 - 0.05, -6.35, zm)
      and solid(wx1 + 0.05, 0, zm) and solid(L_F, 6.45, zm), f"window x {wx0:.1f}-{wx1:.1f}, y ±6.4")
check("horn clamp hole Ø2.4 + HOLE_COMP on the femur axis", vert == [2.6], vert)
check("pilots Ø1.5 + HOLE_COMP at x 25.6 and 53.4 (slotted 0.4 outward)",
      all(not solid(x, dy, zm) and solid(x, dy * 1.12, zm) for x in (25.6, 53.4) for dy in (-0.8, 0.8))
      and solid(26.6, 0, zm) and solid(52.4, 0, zm), "probes at ±0.8 void, ±0.9 solid")
check("5 mm floor under the 2 mm horn pocket", not solid(0, 3, 1.0) and solid(0, 3, 2.3), "pocket z 0-2 on the bed face")
check("SYS-5 tie slot 3.2 × 1.8 at (20, -6)", not solid(20, -6, zm) and solid(20, -8.3, zm) and solid(20, -3.7, zm), "through")
check("side walls beside the window >= 3.0", solid(L_F, 6.5, zm) and solid(L_F, 9.4, zm) and solid(L_F, -9.4, zm), "HALF_W 9.5 - 6.4")
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)

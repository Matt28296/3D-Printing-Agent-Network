"""jobs/20261026-arm-claw-pinion/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261026-arm-claw-pinion/cad_checks.py
Exit code 0 = every check passed. Probes use design() (pinion frame: axis +Z from the back face at z 0, tooth 0 on
+X); the bed chamfer is checked on the tooth outline's 2D inset (tools/gears.py), which must keep every edge.
"""
import math
import runpy
import sys
from pathlib import Path

JOB = Path(__file__).resolve().parent
ROOT = JOB.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "jobs" / "20261025-robot-arm-assembly"))
from build123d import Kind, Vector, Wire  # noqa: E402
from cadlib import bbox, measure_holes  # noqa: E402

import claw_frame as C  # noqa: E402
import gears  # noqa: E402

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
check("size Ø21.70 x 12 (FACE_W 12)", all(abs(a - b) < 0.01 for a, b in zip(size, [21.70, 21.70, 12.0])), size)
check("one solid", len(part.solids()) == 1, len(part.solids()))
dia = sorted(round(h["diameter"], 2) for h in holes)
check("clamp hole Ø2.6 and counterbore Ø6.4", dia == [2.6, 6.4], dia)
check("tooth 0 tip at r 10.85 on +X, root circle r 8.75", solid(10.8, 0, 6) and not solid(10.9, 0, 6)
      and not solid(8.7 * math.cos(math.radians(9)) + 0.15, 8.7 * math.sin(math.radians(9)) + 0.15, 6))
hw = (math.pi / 2 - C.PINION_BACKLASH / 2) / 2 / C.R_P               # half tooth angle at the pitch circle
check("tooth 0.05 thinner at the pitch line (PINION_BACKLASH 0.1)",
      solid(C.R_P * math.cos(hw - 0.003), C.R_P * math.sin(hw - 0.003), 6)
      and not solid(C.R_P * math.cos(hw + 0.003), C.R_P * math.sin(hw + 0.003), 6))
check("counterbore 3.7 deep: floor z 8.3, 6.3 above the horn face (pocket top z 2.0)", solid(3.0, 0, 8.2)
      and not solid(3.0, 0, 8.4) and not solid(3.0, 0, 1.9) and solid(0, 4.5, 2.1))
check("horn pocket: hub Ø7.5 CAD, stubs to r 5.65, 2 deep", not solid(0, 3.7, 1.0) and solid(0, 3.85, 1.0)
      and not solid(5.6, 0, 1.0) and solid(5.75, 0, 1.0))
check("pocket mouth chamfer 0.2 x 45°: 0.15 wider at z 0.05", not solid(0, 3.85, 0.05) and solid(0, 4.0, 0.05)
      and solid(0, 3.85, 0.3))
pts = gears.gear_outline(C.M, C.Z_TEETH, 20.0, C.PINION_BACKLASH, 0.0, root_fillet=C.PINION_ROOT_FILLET,
                         tip_relief=C.TIP_RELIEF)
w = Wire.make_polygon([(x, y, 0.0) for x, y in pts], close=True)
ins = w.offset_2d(-ns["BED_CHAMFER"], kind=Kind.INTERSECTION)
ins = ins[0] if isinstance(ins, list) else ins
check("bed chamfer 0.25: inset outline keeps every edge (true 45° loft)", len(ins.edges()) == len(w.edges()),
      (len(w.edges()), len(ins.edges())))
check("bed chamfer 0.25 on the tooth tip: tip 0.2 in at z 0.05", solid(10.6, 0, 0.05) and not solid(10.7, 0, 0.05))
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)

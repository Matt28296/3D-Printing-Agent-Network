"""jobs/20261026-arm-claw-jaw/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261026-arm-claw-jaw/cad_checks.py
Exit code 0 = every check passed. Probes use design() (jaw A, closed, claw frame G); the bed chamfer is checked on the
tooth outline's 2D inset (tools/gears.py), which must keep every edge of the outline (a true 45° loft).
"""
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


ZS = C.ZS
# ---- CHECKS: one line per critical dimension in design_brief.md -----------------
check("printed size 31.25 x 56.55 x 60.75 (rack x 22.6 .. tip x 83.35)",
      all(abs(a - b) < 0.02 for a, b in zip(size, [31.25, 56.55, 60.75])), size)
check("one solid, no holes", len(part.solids()) == 1 and not holes, (len(part.solids()), holes))
check("rack face x 22.6..34.6 (FACE_W 12)", solid(22.7, 10, 45) and solid(34.5, 10, 45) and not solid(34.7, 10, 45))
check("rack back face z 48.5 (pitch line to back 11.25)", solid(28, 10, 48.4) and not solid(28, 10, 48.6))
check("teeth: tip line z 36.4 (topped 0.15), a gap over the pinion axis, a tooth at y pi/2",
      solid(28, C.P_CIRC / 2, 36.45) and not solid(28, C.P_CIRC / 2, 36.35) and not solid(28, 0.0, 36.45))
check("tooth 0.35 thinner at the pitch line: half width 0.6104 at z 37.25",
      solid(28, C.P_CIRC / 2 + 0.60, ZS + C.R_P) and not solid(28, C.P_CIRC / 2 + 0.62, ZS + C.R_P))
check("neck 20 x 10: y -20..0, z 38.5..48.5, to x 40.35", solid(39.5, -19.9, 43) and solid(39.5, -0.1, 38.6)
      and not solid(39.5, -20.1, 43) and not solid(39.5, 0.1, 43) and solid(37, 0.1, 43))   # r 4 root fillet at x 37
check("grip face on y 0", solid(63.6, -0.1, ZS + 5) and not solid(63.6, 0.1, ZS + 5))
check("grooves at x 62.6..70.6 only (none in the last 12.7 mm)", not solid(70.6, -0.3, ZS + 5) and not solid(62.6, -0.3, ZS + 5)
      and solid(72.6, -0.3, ZS + 5) and solid(76.6, -0.3, ZS + 5))
check("fingertip x 83.35, 6 thick", solid(83.2, -2.0, ZS + 2) and not solid(83.5, -2.0, ZS + 2) and solid(75.5, -5.9, ZS + 2)
      and not solid(75.5, -6.1, ZS + 2))
# bed chamfer: the 0.25 inset of the rack outline keeps every edge, so gears.py's loft is a true 45° band
pts = gears.rack_outline(C.M, C.RACK_Y[0], C.RACK_Y[1], C.RACK_BACK, 20.0, C.RACK_BACKLASH, C.P_CIRC / 2,
                         root_fillet=C.RACK_ROOT_FILLET, tip_relief=C.TIP_RELIEF)
w = Wire.make_polygon([(x, y, 0.0) for x, y in pts], close=True)
ins = w.offset_2d(-ns["BED_CHAMFER"], kind=Kind.INTERSECTION)
ins = ins[0] if isinstance(ins, list) else ins
check("bed chamfer 0.25: inset outline keeps every edge (true 45° loft)", len(ins.edges()) == len(w.edges()),
      (len(w.edges()), len(ins.edges())))
check("bed chamfer 0.25 at the rack's back edge: 0.2 in at x 22.65", solid(22.65, 10, 48.25) and not solid(22.65, 10, 48.35))
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)

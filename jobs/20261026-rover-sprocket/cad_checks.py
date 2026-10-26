"""jobs/20261026-rover-sprocket/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261026-rover-sprocket/cad_checks.py
Exit code 0 = every check passed. Probes use design() (sprocket frame: +z away from the chassis,
z = 0 on the track plane, world Y = 55 + z).
"""
import math
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
F = sys.modules["rover_frame"]


def check(name, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok:
        failures.append(name)


def solid(r, ang, z):
    a = math.radians(ang)
    return d.is_inside(Vector(r * math.cos(a), r * math.sin(a), z))


# ---- CHECKS: one line per critical dimension in design_brief.md -----------------
check("overall size Ø35.8 tips × 7.0 (disc only: it seats straight on the hub)",
      all(abs(a - b) < 0.02 for a, b in zip(size, [35.777, 34.52, 7.0])), size)
check("one round hole only: the Ø3.6 CAD shaft-clearance hole on the axis (no D-bore, no set screw)",
      [h["diameter"] for h in holes] == [3.6] and abs(holes[0]["axis"][2]) > 0.99, holes)
check("pitch radius 16.18 from rover_frame (10 teeth, 10 mm pitch)", abs(F.RP - 16.18) < 0.01, round(F.RP, 3))
check("tooth tip r 17.9, disc r 11.9", solid(17.8, 0, 0) and not solid(18.0, 0, 0) and solid(11.8, 18, 0)
      and not solid(12.0, 18, 0), "")
check("disc ±3.5 about the track plane", solid(11.0, 18, 3.45) and not solid(11.0, 18, 3.55) and solid(11.0, 18, -3.45), "")
z0 = ns["HUB_FACE_Z"]
check("disc's inner face seats on the hub at world Y 51.5 (z -3.5); nothing printed inboard of it",
      abs(z0 - (F.HUB_Y1 - F.Y_T)) < 1e-9 and solid(9.5, 0, z0 + 0.05) and not solid(9.5, 0, z0 - 0.05)
      and not solid(3.0, 0, z0 - 0.05), round(z0, 3))
check("no printed tube and no radial hole (strength round 2): the part is the 7 mm disc", abs(size[2] - 7.0) < 0.02, size[2])
r0, r1 = ns["SLOT_R"]
for k in range(4):
    ang = 45 + 90 * k
    check(f"M3 slot {k} at {ang}°: open over r {r0}-{r1} (any hole circle in range), walls to the centre hole and rim",
          not solid(r0, ang, -2.0) and not solid(r1, ang, -2.0) and not solid(r0, ang, 2.0) and not solid(r1, ang, 2.0)
          and not solid(6.35, ang, 0.0) and solid(r0 - 1.95, ang, 0.0) and solid(r1 + 1.95, ang, 0.0), "")
check("slot width Ø3.6 CAD (M3 clearance 3.4 printed)", not solid(6.0, 45 + math.degrees(1.75 / 6.0), 0.0)
      and solid(6.0, 45 + math.degrees(1.85 / 6.0), 0.0), "")
check("no material on the hub's bolt circle r 6.35 in any slot", all(not solid(6.35, 45 + 90 * k, z0 + 0.5) for k in range(4)), "")
check("disc material round the slots to r 11.9 (Ø17.5 hub face fully covered)", solid(8.8, 45, 0.0) and solid(11.8, 45, 0.0), "")
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)

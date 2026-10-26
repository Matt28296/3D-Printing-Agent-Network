"""jobs/20261025-arm-turntable-ring/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261025-arm-turntable-ring/cad_checks.py
Exit code 0 = every check passed. Printed as modelled (tabs on the bed, Z 0 = base top plate), so
build() and design() share the frame; probes on design().
"""
import math
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
d = ns["design"]()
base = runpy.run_path(str(JOB.parent / "20261025-arm-base" / "model.py"), run_name="model")
tt = runpy.run_path(str(JOB.parent / "20261025-arm-turntable" / "model.py"), run_name="model")
failures = []


def check(name, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok:
        failures.append(name)


def polar(r, a_deg, z):
    return (r * math.cos(math.radians(a_deg)), r * math.sin(math.radians(a_deg)), z)


def solid(p):
    return d.is_inside(p)


def run_r(a, z, r0, r1, step=0.01):
    n = int((r1 - r0) / step)
    return sum(step for i in range(n) if solid(polar(r0 + (i + 0.5) * step, a, z)))


R_IN, R_OUT, H, GAP = ns["R_IN"], ns["R_OUT"], ns["H"], ns["RUN_GAP"]
TR, TT_, ANG = ns["TAB_R"], ns["TAB_T"], ns["TAB_ANG"]
RW = ns["WASHER_D"] / 2

# ---- CHECKS: one line per critical dimension in design_brief.md -----------------
check("overall size 91.3 × 96 × 16.1", all(abs(a - b) < 0.01 for a, b in zip(size, [91.272, 96.0, 16.1])), size)
check("ring height 16.1 = turntable underside 16.5 - 0.4 running gap (spec §3: 16.1 ±0.15)",
      abs(H - (tt["Z0"] - GAP)) < 1e-9 and abs(H - 16.1) < 1e-9 and solid(polar(42.5, 90, H - 0.05))
      and not solid(polar(42.5, 90, H + 0.05)), f"H {H}, turntable underside {tt['Z0']}, gap {GAP}")
wall = run_r(90, 8.0, R_IN - 1, R_OUT + 1)
check("ring wall r 41 .. 44, 3.0 thick away from the tabs", abs(wall - 3.0) < 0.03 and solid(polar(R_IN + 0.05, 90, 8))
      and not solid(polar(R_IN - 0.05, 90, 8)) and not solid(polar(R_OUT + 0.05, 90, 8)), round(wall, 2))
tabs = sorted((round(math.degrees(math.atan2(h["point_on_axis"][1], h["point_on_axis"][0])) % 360),
               round(math.hypot(h["point_on_axis"][0], h["point_on_axis"][1]), 2)) for h in holes
              if abs(h["diameter"] - 3.6) < 0.01)
check("3 tab holes Ø3.4 + HOLE_COMP at r 47.5, 30° / 150° / 270° (match the base's ring pilots)",
      tabs == [(30, 47.5), (150, 47.5), (270, 47.5)] and base["RING_PILOT_R"] == TR and tuple(base["RING_PILOT_ANG"]) == ANG,
      tabs)
ok_relief, detail = True, []
for a in ANG:
    c = polar(TR, a, 0)
    w_in = run_r(a, 8.0, R_IN - 1, R_OUT + 1)
    # the Ø7 washer's edge, centred on the screw, and 0.45 mm beyond it towards the ring: all free of the wall
    free = all(not solid((c[0] + (RW + e) * math.cos(t), c[1] + (RW + e) * math.sin(t), z))
               for e in (0.0, 0.45) for t in [math.radians(a + 180 + k) for k in range(-60, 61, 10)]
               for z in (TT_ + 0.05, TT_ + 0.6, TT_ + 3.0))
    seat = all(solid((c[0] + rr * math.cos(math.radians(a + 180)), c[1] + rr * math.sin(math.radians(a + 180)), TT_ - 0.05))
               for rr in (2.0, 3.0, 3.4))
    ok_relief &= abs(w_in - 2.5) < 0.03 and free and seat
    detail.append(f"{a:g}°: wall {w_in:.2f}, washer free {free}, seat {seat}")
check("Ø7 × 0.5 washer under each tab screw sits flat on the tab, >= 0.5 mm clear of the wall (relief Ø8, wall 2.5)",
      ok_relief, "; ".join(detail))
check("tabs 3 thick on the bed, Ø9 round the screw", all(solid(polar(TR + 4.4, a, TT_ - 0.05)) and
                                                         not solid(polar(TR + 4.6, a, 1.5)) and not solid(polar(TR, a, TT_ + 0.05))
                                                         for a in ANG), "r 47.5 ± 4.5")
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)

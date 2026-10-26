"""jobs/20261026-hexapod-coxa/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261026-hexapod-coxa/cad_checks.py
Exit code 0 = every check passed. Frame C, z up in print (see model.py).
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


def run_x(y, z, x0, x1, step=0.05):
    """Length of solid along x at (y, z) between x0 and x1."""
    n = int((x1 - x0) / step)
    return sum(step for i in range(n) if solid(x0 + (i + 0.5) * step, y, z))


Y_F, T_V, T_C, Z_F = ns["Y_F"], ns["T_V"], ns["T_C"], ns["Z_F"]
ym = Y_F - T_V / 2                                     # mid-plane of the vertical plate
wx0, wx1 = ns["WIN_X"]
floor = Z_F - ns["WIN_HALF"]

# ---- CHECKS: one line per critical dimension in design_brief.md -----------------
check("overall size 60.1 × 30.5 × 41.0", all(abs(a - b) < 0.05 for a, b in zip(size, [60.1, 30.5, 41.0])), size)
clamp = [h for h in holes if abs(h["axis"][2]) > 0.99 and abs(h["point_on_axis"][0]) < 0.01 and abs(h["point_on_axis"][1]) < 0.01]
check("horn clamp hole Ø2.4 + HOLE_COMP on the coxa axis", len(clamp) == 1 and abs(clamp[0]["diameter"] - 2.6) < 0.01,
      [h["diameter"] for h in clamp])
check("6 mm floor under the 2 mm horn pocket (T_C 8)", not solid(0, 3, 1.0) and solid(0, 3, 2.3) and solid(0, 3, 7.9)
      and not solid(0, 3, 8.1), "pocket z 0-2, floor z 2-8")
check("vertical plate T_V 10, y -23.5 … -13.5", solid(8, Y_F - T_V + 0.05, 30) and solid(8, Y_F - 0.05, 30)
      and not solid(8, Y_F - T_V - 0.05, 30) and not solid(8, Y_F + 0.05, 30), f"probe x 8, z 30")
check("femur axis 32 out, 20 below the back face (window centre)", not solid(32, ym, Z_F) and solid(32, ym, floor - 0.3),
      f"window x {wx0:.1f}-{wx1:.1f}, floor z {floor:.1f}")
check("window 23.2 long (22.8 + 0.2 + HOLE_COMP 0.2)", abs((wx1 - wx0) - 23.2) < 0.01 and not solid(wx0 + 0.05, ym, Z_F - 5)
      and solid(wx0 - 0.05, ym, Z_F - 5) and not solid(wx1 - 0.05, ym, Z_F - 5) and solid(wx1 + 0.05, ym, Z_F - 5), wx1 - wx0)
post_in = run_x(ym, floor + 1.5, ns["VPLATE_X"][0] - 0.5, wx0)
post_out = run_x(ym, floor + 1.5, wx1, ns["VPLATE_X"][1] + 0.5)
check("posts >= 12.5 wide at the window floor (strength)", post_in >= 12.5 and post_out >= 12.5, (round(post_in, 2), round(post_out, 2)))
check("R1 T-bone reliefs at the window floor's corners", not solid(wx0 + 1.0, ym, floor - 0.8) and not solid(wx1 - 1.0, ym, floor - 0.8)
      and solid(wx0 + 1.0, ym, floor - 1.2), "Ø2, tangent to the post faces")
nx0 = 32 + 5.9                                          # case end (servo shaft end)
check("B1 lead notch at the outboard end: 4.4 wide, to 1.6 beyond the case end",
      not solid(nx0 + 1.5, ym, Z_F + 2.1) and not solid(nx0 + 1.5, ym, Z_F - 2.1) and solid(nx0 + 1.7, ym, Z_F)
      and solid(nx0 + 1.7, ym, Z_F + 2.4), "probes at x 39.4 / 39.6, z 20 ± 2.1; solid at (39.6, z 22.4)")
check("lead notch roof at 45°: 4.4 at the end wall, opening to 5.8 at the window face (DFM round 3)",
      not solid(38.4, ym, 23.2) and solid(39.3, ym, 22.5), "void (38.4, 23.2), solid (39.3, 22.5)")
px = 32 + (-(22.8 - 5.9) + 22.8 / 2 + 27.8 / 2) + 1.3   # 41.7: outboard pilot moved 1.3 mm out
check("outboard pilot moved 1.3 mm out (x 41.7), Ø1.7 teardrop", not solid(px, ym, Z_F) and solid(px - 1.0, ym, Z_F)
      and not solid(px, ym, Z_F + 1.0), f"x {px:.2f}")
lig = run_x(ym, Z_F, nx0 + 1.6, px)
check("ligament notch → moved pilot >= 1.3 CAD (1.5 printed)", lig >= 1.3, round(lig, 2))
check("45° ramp >= 8 mm at the plate's inner end", solid(-5.0, ym, T_C + 0.5) and not solid(-5.0, ym, T_C + 1.6)
      and solid(1.0, ym, T_C + 6.5) and not solid(1.0, ym, T_C + 7.5), "foot x -6.1 at z 8, top x 1.9 at z 16")
check("full-length 45° gusset on the tab side", all(solid(x, Y_F + 2.0, T_C + 2.0) for x in (2.5, 26.5, 50.5))
      and not solid(26.5, Y_F + 2.0, T_C + 3.5), "y -13.5 … -8.6")
check("SYS-5 tie slot through the outer post (1.8 × 3.2, roofed)", not solid(47.5, ym, 30.0) and not solid(47.5, ym, 32.3)
      and solid(47.5, ym, 33.5), "at (47.5, z 30)")
check("arm clears the femur's plane (y >= -0.9) by >= 5", not any(solid(x, -6.0, 4.0) for x in (25, 35, 45)), "arm y <= -6.5")
check("outer top corner cut 6 mm at 45° (reversed tibia servo, femur -40…-60°)", not solid(50.5, ym, 40.0)
      and solid(49.0, ym, 37.0) and solid(44.0, ym, 40.5), "x + z <= 86.1")
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)

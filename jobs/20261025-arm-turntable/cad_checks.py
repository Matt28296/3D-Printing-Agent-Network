"""jobs/20261025-arm-turntable/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261025-arm-turntable/cad_checks.py
Exit code 0 = every check passed. Size and holes on build() (print frame: disk on the bed);
point probes on design() (assembly frame at yaw 0: disk Z 16.5 .. 24.5, upright Y -12 .. -5).
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
failures = []


def check(name, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok:
        failures.append(name)


def solid(x, y, z):
    return d.is_inside((x, y, z))


Z0, DT, UT, UY = ns["Z0"], ns["DISK_T"], ns["UP_T"], ns["UP_Y"]
TOP, UP_TOP, ZS, XS = Z0 + DT, ns["UP_TOP"], ns["ZS"], ns["XS"]
GX, GT, GL, GH = ns["GUSSET_X"], ns["GUSSET_T"], ns["GUSSET_LEN"], ns["GUSSET_H"]
YB = UY - UT                                             # -12: upright back face


def g_len(z):
    return GL * (1 - (z - TOP) / GH)


# ---- CHECKS: one line per critical dimension in design_brief.md -----------------
check("overall size 96 × 96 × 80.8 (gussets end level with the upright)",
      all(abs(a - b) < 0.01 for a, b in zip(size, [96.0, 96.0, 80.8])), size)
clamp = [h for h in holes if abs(h["diameter"] - 3.6) < 0.01]
pil = sorted((round(abs(h["point_on_axis"][0]), 2), round(h["point_on_axis"][2], 2)) for h in holes
             if abs(h["diameter"] - 2.8) < 0.01)
check("clamp hole Ø3.4 + HOLE_COMP on the yaw axis", len(clamp) == 1 and abs(clamp[0]["point_on_axis"][0]) < 0.01
      and abs(clamp[0]["point_on_axis"][1]) < 0.01, [h["diameter"] for h in clamp])
check("4 shoulder tab pilots Ø2.6 + HOLE_COMP (teardrops) at X ±24.25, Z 55.5 / 65.5",
      pil == [(24.25, 39.0), (24.25, 39.0), (24.25, 49.0), (24.25, 49.0)], f"print-frame (|x|, z): {pil}")
check("disk underside Z 16.5, disk 8 thick", solid(30, 30, Z0 + 0.05) and not solid(30, 30, Z0 - 0.05)
      and solid(30, 30, TOP - 0.05) and not solid(30, 30, TOP + 0.05), f"Z {Z0} .. {TOP}")
r0, r1 = ns["ANTI_ROT_ZONE"]
zone = [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), z)
        for r in (r0, 5.5, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, r1) for a in range(0, 360, 15)
        for z in (Z0 + 0.05, Z0 + 3.0, Z0 + ns["ANTI_ROT_PILOT_DEPTH"] + 0.5)]
holes_in_zone = [p for p in zone if not solid(*p)]
check("disc-horn anti-rotation zone plain solid: r 4-13, from the underside to 6.5 deep (4 × M2 × 8 pilots drilled "
      "6 deep anywhere on the disc's hole circles)", not holes_in_zone, f"{len(zone)} probes, {len(holes_in_zone)} void")
check("clamp hole open through the disk, plain disk from r 2", not solid(0, 0, Z0 + 1) and not solid(0, 0, TOP - 0.5)
      and solid(2.0, 0, Z0 + 4), "Ø3.6 CAD")
check("upright 7 thick (Y -12 .. -5), 66 wide", solid(-26, UY - 0.05, 40) and not solid(-26, UY + 0.05, 40)
      and solid(-26, YB + 0.05, 40) and not solid(-26, YB - 0.05, 40) and solid(-32.9, -8, 40) and not solid(-33.1, -8, 40),
      "probes at Z 40")
check("shoulder window 41.3 × 20.3 CAD round the axis (X 10.15 servo frame -> body centred on X 0), 45° roof",
      not solid(0, -8.5, ZS) and not solid(20.6, -8.5, ZS - 5) and solid(20.75, -8.5, ZS - 5)
      and not solid(0, -8.5, ZS - 10.1) and solid(0, -8.5, ZS - 10.25) and not solid(0, -8.5, 90.0)
      and solid(0, -8.5, 91.6), f"window X ±20.65, Z {ZS - 10.15:.2f}..{ZS + 10.15:.2f}, roof apex Z 91.3")
check("lead notches 4.6 × 2.1 CAD at both case ends (4.4 × 2.0 printed), 45° tops reaching the notch end",
      all(not solid(sx * 22.4, -8.5, ZS + dz) for sx in (1, -1) for dz in (-2.2, 0, 2.2))
      and all(solid(sx * 22.55, -8.5, ZS) for sx in (1, -1))
      and all(not solid(sx * 21.0, -8.5, 64.0) and solid(sx * 21.0, -8.5, 64.6) for sx in (1, -1))
      and all(not solid(sx * 22.4, -8.5, ZS + 2.32) and solid(sx * 22.4, -8.5, ZS + 2.45) for sx in (1, -1)),
      "end wall X ±22.46 up to Z 62.8, then 45° to the window")
check("gussets 4 thick at |X| 28.5 .. 32.5 behind the upright", all(solid(sx * GX, YB - 3, 40) and solid(sx * (GX - GT / 2 + 0.05), YB - 3, 40)
      and not solid(sx * (GX - GT / 2 - 0.05), YB - 3, 40) and not solid(sx * (GX + GT / 2 + 0.05), YB - 3, 40)
      for sx in (1, -1)), f"X ±{GX}")
gz = [(TOP + 0.1, g_len(TOP + 0.1)), (ZS, g_len(ZS)), (UP_TOP - 0.1, g_len(UP_TOP - 0.1))]
check("gussets GUSSET_H 90 (strength: was 70): 23 deep at the disk, 13.8 at the shoulder axis, 4.4 at the top (Z 97.3)",
      all(solid(sx * GX, YB - L + 0.15, z) and not solid(sx * GX, YB - L - 0.15, z) for z, L in gz for sx in (1, -1))
      and abs(g_len(UP_TOP) - 4.4) < 0.01, [(round(z, 1), round(L, 2)) for z, L in gz])
check("gussets cut off level with the upright's top", all(solid(sx * GX, YB - 2, UP_TOP - 0.05) and
                                                          not solid(sx * GX, YB - 2, UP_TOP + 0.05) for sx in (1, -1)),
      f"Z {UP_TOP:.1f}")
toe = math.hypot(GX + GT / 2, YB - GL)
check("gusset toe inside the disk (r <= 48, DFM round 1)", toe <= ns["DISK_R"], round(toe, 2))
check("front root wedge stops at |X| >= 6 (Ø9 clamp washer seats flat)", not solid(3.0, UY + 1.0, TOP + 0.5)
      and solid(10.0, UY + 1.0, TOP + 0.5), "probes at Y -4, Z 25")
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)

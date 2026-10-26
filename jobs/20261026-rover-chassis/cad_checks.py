"""jobs/20261026-rover-chassis/cad_checks.py: prove the critical dimensions on the built geometry.

Run from the project root: python3 jobs/20261026-rover-chassis/cad_checks.py
Exit code 0 = every check passed. Size and holes come from build() (print frame, z = world z - 8.68);
the point probes use design() in the rover world frame (rover_frame.py), both sides.
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
world = ns["design"]()
size = bbox(part)["size"]
holes = measure_holes(part)
failures = []
F = sys.modules["rover_frame"]
Z = F.Z_A


def check(name, ok, detail):
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")
    if not ok:
        failures.append(name)


def solid(x, y, z):
    return world.is_inside(Vector(x, y, z))


def both(name, fn):
    res = [fn(1), fn(-1)]
    check(name, all(res), f"left/right {res}")


def hole_d(d, tol=0.02):
    return [h for h in holes if abs(h["diameter"] - d) < tol]


# ---- CHECKS: one line per critical dimension in design_brief.md -----------------
check("overall size 154 × 92 × 40 (nacelles to |y| 46)", all(abs(a - b) < 0.02 for a, b in zip(size, [154.0, 92.0, 40.0])), size)
# measure_holes merges coaxial holes, so the left and right holes on one Y axis count once
check("M3 bolt holes Ø3.6 CAD (printed 3.4) on the road-wheel axes x 40, 80",
      sorted(round(h["point_on_axis"][0]) for h in hole_d(3.6) if abs(h["axis"][1]) > 0.99) == [40, 80],
      sorted(h["point_on_axis"][0] for h in hole_d(3.6)))
check("skin holes round the N20 bearing boss Ø4.7 CAD (printed 4.5) on the sprocket axis x 0",
      [round(h["point_on_axis"][0]) for h in hole_d(4.7)] == [0], [h["point_on_axis"] for h in hole_d(4.7)])
check("jack-screw pilots Ø2.8 CAD along X (printed 2.6): 2", len([h for h in hole_d(2.8) if abs(h["axis"][0]) > 0.99]) == 2,
      [h["point_on_axis"] for h in hole_d(2.8)])
check("heat-set insert holes Ø4.0 (maker's size, no comp): 4", len([h for h in hole_d(4.0) if abs(h["axis"][2]) > 0.99]) == 4,
      [h["point_on_axis"][:2] for h in hole_d(4.0)])
check("HC-SR04 holes Ø16.6 CAD: 2", len(hole_d(16.6)) == 2, [h["point_on_axis"] for h in hole_d(16.6)])
check("no switch hole in the rear wall (moved to the lid)", not hole_d(6.4), hole_d(6.4))

yf, sk = F.MOTOR_FACE_Y, F.SKIN
# round 4: SKIN 2.0 (strength round 3 change 2) moves the gearbox face inward to |y| 44; the shaft arm is then 11
check("round 4 stack-up: SKIN 2.0, gearbox face |y| 44.0, thrust washer 46.0, hub 46.5, shaft arm 11.0",
      (sk, yf, yf + sk, F.HUB_Y0, F.SHAFT_ARM) == (2.0, 44.0, 46.0, 46.5, 11.0), (sk, yf, yf + sk, F.HUB_Y0, F.SHAFT_ARM))
# diamond pocket (motor rolled 45°): the 12 mm faces lie on x + z' = ±8.77, the 10 mm faces on z' - x = ±7.35
# (6.2 and 5.2 from the axis: gearbox 12 × 10 + 0.2 + HOLE_COMP), z' = z - Z_A
both("gearbox pocket open from the trough to the skin (x 0, Z_A)", lambda s: not solid(0, s * 20.0, Z)
     and not solid(0, s * 34.0, Z) and not solid(0, s * (yf - 0.1), Z + 3))
both("pocket 12 mm faces 6.2 from the axis (lower-left, in the wall)", lambda s: solid(-4.43, s * 36, Z - 4.43)
     and not solid(-4.33, s * 36, Z - 4.33) and solid(4.43, s * 36, Z + 4.43) and not solid(4.33, s * 36, Z + 4.33))
both("pocket 10 mm faces 5.2 from the axis (lower-right, in the wall)", lambda s: solid(3.73, s * 36, Z - 3.73)
     and not solid(3.63, s * 36, Z - 3.63) and solid(-3.73, s * 36, Z + 3.73) and not solid(-3.63, s * 36, Z + 3.63))
both("skin 2.0 thick in front of the gearbox face (|y| 44-46): the pocket ends at 44",
     lambda s: not solid(4.0, s * (yf - 0.05), Z) and solid(4.0, s * (yf + 0.05), Z) and solid(4.0, s * (yf + sk / 2), Z)
     and solid(4.0, s * (yf + sk - 0.05), Z) and not solid(4.0, s * (yf + sk + 0.05), Z)
     and solid(-4.0, s * (yf + 1.0), Z - 2.0) and solid(0.0, s * (yf + 1.0), Z + 5.0))
both("skin hole clears the Ø4 bearing boss", lambda s: not solid(2.2, s * (yf + 0.5), Z) and solid(2.5, s * (yf + 0.5), Z - 0.3))
both("housing outer face at |y| 42.0 = links' inner edge 43 - 1 (outside the nacelle)",
     lambda s: solid(10.5, s * 41.95, Z - 5) and not solid(10.5, s * 42.05, Z - 5))
both("nacelle inside the wrap: r <= 10.9 (links' inner faces at r >= 12.39)", lambda s: solid(0.6, s * 44, Z + 10.6)
     and not solid(0.6, s * 44, Z + 11.0) and not solid(-11.0, s * 44, Z - 0.6) and not solid(-0.6, s * 44, Z - 11.0))
both("nacelle walls 2.0 round the pocket (pocket face x + z' = -8.77, outer face -11.60; pocket in the nacelle y 42-44)",
     lambda s: solid(-5.1, s * 43, Z - 5.1) and not solid(-4.3, s * 43, Z - 4.3) and not solid(-5.9, s * 43, Z - 5.9))
both("housing roof over the pocket's top vertex (Z_A + 8.06 .. 12.5)", lambda s: not solid(0.7, s * 40, Z + 7.9)
     and solid(0.7, s * 40, Z + 8.3) and solid(5.0, s * 40, Z + 12.4) and not solid(5.0, s * 40, Z + 12.6))
both("V-trough walls >= 4 thick at their top edge (left 4.1, right 5.6)", lambda s: solid(-8.1, s * 28, Z - 0.9)
     and not solid(-7.8, s * 28, Z - 0.9) and solid(6.6, s * 28, Z - 0.9) and not solid(6.3, s * 28, Z - 0.9)
     and solid(-12.0, s * 20, Z - 2) and not solid(-12.2, s * 20, Z - 2) and solid(12.0, s * 20, Z - 2)
     and not solid(12.2, s * 20, Z - 2))
both("V-trough top at the gearbox's lower side vertex (Z_A - 0.71)", lambda s: solid(10, s * 28, Z - 0.8)
     and not solid(10, s * 28, Z - 0.6))
cy0 = ns["CRADLE_Y0"]
both(f"trough reaches back to y {cy0:.1f} (an 11 mm gearbox fits; 1 mm further in with the gearbox face)",
     lambda s: abs(cy0 - 16.5) < 1e-9 and solid(10, s * (cy0 + 0.1), Z - 3) and not solid(10, s * (cy0 - 0.1), Z - 3))
both("zip-tie tunnel through both trough walls under the can (|y| 22-26)", lambda s: not solid(-10, s * 24, Z - 7.2)
     and not solid(10, s * 24, Z - 7.2) and solid(-10, s * 24, Z - 5.5) and solid(-10, s * 21.5, Z - 7.2))
for x in F.ROAD_X:
    both(f"road-wheel boss x {x:.0f}: Ø26, face at |y| 28 (BOSS_IN 5.5)",
         lambda s, x=x: solid(x, s * 30.5, Z + 12.8) and not solid(x, s * 30.5, Z + 13.2) and solid(x + 5, s * 28.1, Z)
         and not solid(x + 5, s * 27.9, Z))
    both(f"road-wheel boss x {x:.0f}: r1.5 rim fillet (corner cut back)", lambda s, x=x: not solid(x, s * 28.15, Z + 12.85))
    both(f"road-wheel boss x {x:.0f}: 45° collar at the wall", lambda s, x=x: solid(x, s * 33.0, Z + 13.3) and not solid(x, s * 31.8, Z + 13.3))
both("idler block face at |y| 28 (BOSS_IN 5.5; probed above the plate recess)",
     lambda s: solid(110, s * 28.1, Z + 9) and not solid(110, s * 27.9, Z + 9))
# round 4, strength round 3 change 1: steel clamp plates (sizes and PLATE_T in rover_frame)
pt, (rx0, rx1), rz = F.PLATE_T, ns["PLATE_RECESS_X"], ns["PLATE_RECESS_Z"]
check("head-plate recess depth = PLATE_T = 2.0, so the plate is flush: head on its Ø9 washer still at |y| 27.2, jack line 25.4",
      (ns["PLATE_RECESS_D"], pt, ns["IDLER_HEAD_Y1"], ns["JACK_Y"]) == (2.0, 2.0, 27.2, 25.4),
      (ns["PLATE_RECESS_D"], pt, ns["IDLER_HEAD_Y1"], ns["JACK_Y"]))
both("head-plate recess 2.0 deep in the idler-block face (|y| 28-30)", lambda s: not solid(110, s * 28.5, Z + 3)
     and not solid(110, s * 29.9, Z + 3) and solid(110, s * 30.1, Z + 3) and not solid(126, s * 29.9, Z - 4))
both("recess x 108-129: from the buttress face to the front 45° strip, cutting neither",
     lambda s: (rx0, rx1) == (108.0, 129.0) and not solid(108.1, s * 29, Z) and solid(107.9, s * 29, Z)
     and not solid(128.9, s * 29, Z - 4) and solid(129.1, s * 29, Z - 4)
     and solid(107.9, s * 27.9, Z - 3) and solid(130.0, s * 27.6, Z) and solid(129.6, s * 27.7, Z + 3))
both("recess bottom Z_A ± 5.2 (10 mm plate + 0.2 a side), 45° roof up to Z_A + 7.2 at the block face",
     lambda s: abs(rz - 5.2) < 1e-9 and not solid(118, s * 29.9, Z - 5.1) and solid(118, s * 29.9, Z - 5.3)
     and not solid(118, s * 29.9, Z + 5.2) and solid(118, s * 29.9, Z + 5.45)
     and not solid(118, s * 28.1, Z + 7.0) and solid(118, s * 28.1, Z + 7.25))
# round 5 (strength round 4's fix): no idler nut slot; the nut plate (the head plate's twin) lies on the outer face
both("round 5: no idler nut slot: 8.0 mm of solid PETG from the recess floor (|y| 30) to the outer face (38), above and"
     " below the bolt slot, over the plates' whole footprint",
     lambda s: all(solid(x, s * y, Z + dz) for x in (108.5, 113, 116, 120, 124, 128.5) for y in (30.1, 32, 34, 36, 37.9)
                   for dz in (-4.9, -3.5, -2.2, 3.0, 4.5))
     and not solid(113, s * 29.9, Z + 3.5) and not solid(113, s * 38.1, Z + 3.5))
both("bolt slot runs through the outer face (|y| 37.9) at x 116-124", lambda s: not solid(116, s * 37.9, Z)
     and not solid(124, s * 37.9, Z) and not solid(120, s * 37.9, Z + 2.4) and solid(120, s * 37.9, Z + 2.7))
check("nut plate = the head plate's twin (20.6 × 10 × 2, slot from 6 to 18 mm along), seat = the recess's x and floor",
      (F.NUT_PLATE, F.IDLER_PLATE, F.PLATE_SLOT_FROM, ns["NUT_PLATE_X"], ns["LIP_DZ"], ns["LIP_OUT"])
      == ((20.6, 10.0), (20.6, 10.0), 6.0, (108.0, 129.0), 5.2, 1.0),
      (F.NUT_PLATE, F.PLATE_SLOT_FROM, ns["NUT_PLATE_X"], ns["LIP_DZ"], ns["LIP_OUT"]))
both("lip under the nut plate: top Z_A - 5.2, 1.0 proud (|y| 38-39), 1.0 face, then 45° back into the wall",
     lambda s: solid(118, s * 38.5, Z - 5.3) and not solid(118, s * 38.5, Z - 5.1) and solid(118, s * 38.95, Z - 6.1)
     and not solid(118, s * 39.05, Z - 5.6) and solid(118, s * 38.5, Z - 6.6) and not solid(118, s * 38.5, Z - 6.8)
     and not solid(118, s * 38.05, Z - 7.3) and solid(107, s * 38.5, Z - 5.5) and solid(130, s * 38.5, Z - 5.5))
both("end stops: inner faces x 108 and 129 (21.0 CAD, as the recess), 1.0 proud, up to Z_A + 5.2",
     lambda s: solid(107.9, s * 38.5, Z) and not solid(108.1, s * 38.5, Z) and not solid(128.9, s * 38.5, Z)
     and solid(129.1, s * 38.5, Z) and solid(107, s * 38.5, Z + 5.1) and not solid(107, s * 38.5, Z + 5.3)
     and solid(130, s * 38.95, Z) and not solid(130, s * 39.05, Z))
# round 6 (strength round 5's FIX): STOP_W 1.5 -> 2.0, inner faces unchanged, so the stops span x 106-108 and 129-131
both("round 6: STOP_W 2.0: rear stop x 106-108, front stop x 129-131 (1.0 proud, Z_A - 5.7 .. + 5.2)",
     lambda s: ns["STOP_W"] == 2.0 and solid(106.1, s * 38.5, Z) and not solid(105.9, s * 38.5, Z)
     and solid(130.9, s * 38.5, Z) and not solid(131.1, s * 38.5, Z)
     and all(solid(x, s * 38.95, z) for x in (106.1, 107.9, 129.1, 130.9) for z in (Z - 5.6, Z, Z + 5.1)))
# the front stop ends at x 131, where the r6 corner fillet's face is at |y| 37.66 (the stop starts at |y| 37): no gap
both("round 6: front stop joins the r6 corner fillet: solid from the fillet face out to |y| 39 at x 130.95",
     lambda s: all(solid(130.95, s * y, z) for y in (37.0, 37.5, 37.7, 38.0, 38.5, 38.95) for z in (Z - 5.6, Z, Z + 5.1)))
both("round 6: lip, stops and seat stay 4.0 inboard of the links (|y| 43): nothing at |y| > 39 from x 105 to 132",
     lambda s: not any(solid(x, s * y, Z + dz) for x in (105.5, 106.1, 107, 107.9, 129.1, 130, 130.9, 131.5)
                       for y in (39.05, 40.0, 42.9) for dz in (-6.5, -5.6, 0.0, 5.1)))
both("nut plate's space clear: x 108.05-128.95, |y| 38.05-40, Z_A - 5.15 .. + 5.15 (plate rests at Z_A - 5.2 .. + 4.8)",
     lambda s: not any(solid(x, s * y, Z + dz) for x in (108.05, 112, 118, 124, 128.95) for y in (38.05, 39.0, 39.95)
                       for dz in (-5.15, -2.0, 0.0, 3.0, 5.15)))
both("idler slot hull up to the teardrop tips (Z_A + 2.55)", lambda s: not solid(120, s * 31, Z + 2.45) and solid(120, s * 31, Z + 2.7))
both("idler slot ±4 (bolt centres x 116-124)", lambda s: not solid(116, s * 31, Z) and not solid(124, s * 31, Z) and solid(126.5, s * 31, Z))
both("jack pilot on |y| 25.4 at Z_A through the buttress", lambda s: not solid(105, s * 25.4, Z) and solid(105, s * 25.4, Z + 2.5))
both("buttress inner face |y| 22 (battery holder |y| 20.5)", lambda s: solid(105, s * 22.1, Z - 3) and not solid(105, s * 21.9, Z - 3))
both("buttress rear face x 101.5 (jack socket stays outside it)", lambda s: solid(101.6, s * 24, Z - 3) and not solid(101.4, s * 24, Z - 3))
both("idler-bolt head path clear of the buttress (x >= 111.5)", lambda s: not solid(108.5, s * 25, Z))
for (x, y) in ns["COLUMNS"]:
    check(f"column ({x:.0f}, {y:.1f}) Ø10 with Ø4.0 insert hole", solid(x + 4.8, y, F.TOP_Z - 10) and not solid(x + 5.2, y, F.TOP_Z - 10)
          and not solid(x + 1.9, y, F.TOP_Z - 3) and solid(x + 2.1, y, F.TOP_Z - 3), "")
both("strap slots at |y| 26 (3 wide)", lambda s: not solid(62, s * 26, F.FLOOR_Z + 1) and solid(62, s * 28, F.FLOOR_Z + 1))
check("wall 4.5 and floor 2.5", solid(60, 33.6, 30) and solid(60, 37.9, 30) and not solid(60, 33.4, 30)
      and solid(60, 0, F.FLOOR_Z + 2.4) and not solid(60, 0, F.FLOOR_Z + 2.6), "")
# ---------------------------------------------------------------------------------

sys.exit(1 if failures else 0)

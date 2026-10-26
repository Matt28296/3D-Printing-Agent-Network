"""Tracked rover chassis: open-top tub (154 × 76 × 40) that carries both N20 drive motors, the
road-wheel and idler bolts, the 2 × 18650 holder, the power switch and an HC-SR04 sensor.

Design frame = rover world frame (see ../20261026-rover-assembly/rover_frame.py): X forward,
Y left, Z up, ground at Z = 0, drive-sprocket axis at X = 0, Z = Z_A. Printed floor down:
every hole in a wall is horizontal, so each gets a 45° point (teardrop) or a 45° roof, and every
inward boss runs down to the floor (no overhanging boss undersides).

Round 2 (DFM + strength round 1):
- 4.5 mm walls; Ø20 road-wheel bosses and a 30 × 24 idler block, all down to the floor.
- The sprocket hub runs in a 6 mm journal in the wall (Ø10 hub), so track loads go into the wall,
  not the N20 shaft. The N20 sits in a cradle with side cheeks, a rear stop and a zip-tie tunnel,
  gearbox face 0.5 mm inside the journal boss (no face screws).
- Lid columns joined to the walls, front pair moved behind the idler slot (bolt heads clear).
- Idler slot ends are teardrops; strap slots at |y| 27.5; 3 mm 45° fillets along the floor.
- Mini toggle switch (threaded bushing, Ø6.2 hole) instead of a snap-in rocker (4.5 mm wall).
Bolts: road wheels run on M3 × 45 and idlers on M3 × 35 bolts whose heads sit inside the tub and whose
nuts sit in traps in the wall's outer face (flush), so the wheels run right next to the wall.
"""
import sys
from pathlib import Path

from build123d import (Align, Axis, Box, BuildPart, BuildSketch, Cylinder, Plane, Polygon, Pos, Rot, extrude,
                       fillet)
from cadlib import HOLE_COMP_DEFAULT, hex_nut_pocket, teardrop_cutter, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-rover-assembly"))
from rover_frame import (AXLE_DX, FLOOR_T, FLOOR_Z, HALF_W_OUT, HUB_D, IDLER_SLOT, JOURNAL_BOSS, MOTOR,  # noqa: E402
                         MOTOR_FACE_Y, ROAD_X, TOP_Z, WALL, X_FRONT_OUT, X_REAR_OUT, Z_A)

from hobby_parts import BATT_2X18650, HCSR04_TX_D, HCSR04_TX_DX, chamfer_plane_edges  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT
CORNER_R = 6.0
BED_CHAMFER = 0.4
BOLT_D = 3.4                  # M3 clearance (printed)
NUT_AF, NUT_CLR, NUT_DEPTH = 5.5, 0.3, 2.6    # M3 nut trap from the outer face (nut flush)
BOSS_IN = 1.5                 # inward boss at every bolt and at the journal: wall + boss = 6
ROAD_BOSS_R = 10.0            # Ø20 road-wheel bosses (strength round 1)
IDLER_BLOCK = (30.0, 24.0)    # x length, height above the floor (strength round 1)
JOURNAL_CLR = 0.5             # sprocket-hub running clearance in the journal (printed, diametral)
JOURNAL_BOSS_HALF = 10.0      # journal boss block ±x, from the floor to Z_A + 10
CRADLE_HALF_X = 7.0           # motor cradle under the gearbox and can
CHEEK_T, CHEEK_TOP = 2.0, 3.0 # cradle cheeks (x 6.3-8.3) up to Z_A + 3: hold the motor against its reaction torque
TIE_W, TIE_H = 4.0, 2.0       # zip-tie tunnel through the cradle, 1 mm under the can
REAR_STOP = (2.0, 2.5)        # posts behind the can's end cap (y length, x half-width offset from the terminals)
COLUMN_D, LID_PILOT, PILOT_DEPTH = 8.0, 2.6, 12.0
COLUMNS = [(-13.0, 30.0), (-13.0, -30.0), (100.0, 30.0), (100.0, -30.0)]   # joined to the walls
BATT_X0 = 22.0                # battery holder from x 22 (77 long)
STRAP_W, STRAP_L, STRAP_Y = 3.0, 22.0, 27.5   # velcro strap slots beside the holder
FLOOR_FILLET = 3.0            # 45° fillet along the inside of every wall at the floor
SWITCH_D, SWITCH_Z = 6.2, 32.0   # MTS-102 mini toggle (M6 bushing) in the rear wall
SENSOR_Z = 30.0               # HC-SR04 transducer centres (front wall)
SENSOR_CLR = 0.4


def _box(x0, x1, y0, y1, z0, z1):
    return Pos(min(x0, x1), min(y0, y1), min(z0, z1)) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0),
                                                            align=(Align.MIN,) * 3)


def _x_prism(pts_yz, x0, length):
    with BuildPart() as bp:
        with BuildSketch(Plane.YZ.offset(x0)):
            Polygon(*pts_yz, align=None)
        extrude(amount=length)
    return bp.part


def _y_prism(pts_xz, y0, length):
    """Polygon in (x, z), from Y = y0 towards +Y by `length`."""
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ.offset(-y0)):
            Polygon(*pts_xz, align=None)
        extrude(amount=-length)
    return bp.part


def _nut_trap(x, side, slot=0.0):
    """Hex nut trap (vertices along ±X, flats top/bottom) from the outer face inward; stretched into
    a slot of length `slot` along X for the idler."""
    af = NUT_AF + NUT_CLR + HOLE_COMP
    y_out = side * HALF_W_OUT
    trap = None
    for dx in ((-slot / 2, slot / 2) if slot else (0.0,)):
        h = Pos(x + dx, y_out + side * 0.01, Z_A) * Rot(90 * side, 0, 0) * hex_nut_pocket(af, NUT_DEPTH + 0.01, clearance=0)
        trap = h if trap is None else trap + h
    if slot:
        trap += _box(x - slot / 2, x + slot / 2, y_out + side * 0.01, y_out - side * NUT_DEPTH, Z_A - af / 2, Z_A + af / 2)
    return trap


def design():
    bx0, bx1 = X_REAR_OUT, X_FRONT_OUT
    outer = _box(bx0, bx1, -HALF_W_OUT, HALF_W_OUT, FLOOR_Z, TOP_Z)
    outer = fillet(outer.edges().filter_by(Axis.Z), radius=CORNER_R)
    outer = chamfer_plane_edges(outer, FLOOR_Z, BED_CHAMFER)
    xi0, xi1, yi = bx0 + WALL, bx1 - WALL, HALF_W_OUT - WALL
    floor_top = FLOOR_Z + FLOOR_T
    tub = outer - _box(xi0, xi1, -yi, yi, floor_top, TOP_Z + 1)
    f = FLOOR_FILLET
    for s in (1, -1):   # floor fillets along the side walls and the end walls
        tub += _x_prism([(s * yi, floor_top - 0.01), (s * (yi - f), floor_top - 0.01), (s * yi, floor_top + f)], xi0, xi1 - xi0)
    tub += _y_prism([(xi0, floor_top - 0.01), (xi0 + f, floor_top - 0.01), (xi0, floor_top + f)], -yi, 2 * yi)
    tub += _y_prism([(xi1, floor_top - 0.01), (xi1 - f, floor_top - 0.01), (xi1, floor_top + f)], -yi, 2 * yi)
    yb = yi - BOSS_IN   # boss inner face

    for side in (1, -1):
        # journal boss for the sprocket hub, down to the floor
        tub += _box(-JOURNAL_BOSS_HALF, JOURNAL_BOSS_HALF, side * yb, side * (yi + 0.01), floor_top - 0.01, Z_A + 10)
        # motor cradle: block under gearbox + can, side cheeks, rear stop posts, zip-tie tunnel
        y_face = MOTOR_FACE_Y
        y_can_end = y_face - MOTOR.gb_len - MOTOR.can_len
        cz = Z_A - MOTOR.gb_h / 2
        tub += _box(-CRADLE_HALF_X, CRADLE_HALF_X, side * (y_can_end - REAR_STOP[0]), side * (yb + 0.01), floor_top - 0.01, cz)
        for sx in (-1, 1):
            tub += _box(sx * (MOTOR.gb_w / 2 + 0.3), sx * (MOTOR.gb_w / 2 + 0.3 + CHEEK_T),
                        side * y_can_end, side * (yb + 0.01), cz - 0.01, Z_A + CHEEK_TOP)
            tub += _box(sx * 3.0, sx * (MOTOR.gb_w / 2 + 0.3 + CHEEK_T), side * (y_can_end - REAR_STOP[0]), side * (y_can_end - 0.3),
                        cz - 0.01, Z_A + CHEEK_TOP)
        yc = side * (y_face - MOTOR.gb_len - MOTOR.can_len / 2)
        tub -= _box(-CRADLE_HALF_X - CHEEK_T - 2, CRADLE_HALF_X + CHEEK_T + 2, yc - TIE_W / 2, yc + TIE_W / 2,
                    cz - 1.0 - TIE_H, cz - 1.0)
        # road-wheel bosses Ø20 (round top, block to the floor) and the idler block
        for x in ROAD_X:
            tub += Pos(x, side * (yb + (BOSS_IN + 0.01) / 2), Z_A) * Rot(90, 0, 0) * Cylinder(ROAD_BOSS_R, BOSS_IN + 0.01)
            tub += _box(x - ROAD_BOSS_R, x + ROAD_BOSS_R, side * yb, side * (yi + 0.01), floor_top - 0.01, Z_A)
        bl, bh = IDLER_BLOCK
        tub += _box(AXLE_DX - bl / 2, min(AXLE_DX + bl / 2, xi1 + 0.01), side * yb, side * (yi + 0.01),
                    floor_top - 0.01, floor_top + bh)
    for (x, y) in COLUMNS:
        tub += Pos(x, y, floor_top - 0.01) * Cylinder(COLUMN_D / 2, TOP_Z - floor_top + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
        tub -= Pos(x, y, TOP_Z - PILOT_DEPTH) * Cylinder((LID_PILOT + HOLE_COMP) / 2, PILOT_DEPTH + 1,
                                                         align=(Align.CENTER, Align.CENTER, Align.MIN))

    for side in (1, -1):
        y_mid = side * (yb + HALF_W_OUT) / 2
        span = HALF_W_OUT - yb + 2
        # sprocket journal (Ø10 hub + 0.5 running clearance), teardrop pointing up
        tub -= teardrop_cutter(HUB_D + JOURNAL_CLR + HOLE_COMP, span, axis="Y", center=(0.0, y_mid, Z_A))
        # road-wheel bolts + nut traps
        for x in ROAD_X:
            tub -= teardrop_cutter(BOLT_D + HOLE_COMP, span, axis="Y", center=(x, y_mid, Z_A))
            tub -= _nut_trap(x, side)
        # idler bolt slot: teardrop ends + 8 mm flat top (bridges < 10) + nut slot
        r = (BOLT_D + HOLE_COMP) / 2
        for dx in (-IDLER_SLOT, IDLER_SLOT):
            tub -= teardrop_cutter(BOLT_D + HOLE_COMP, span, axis="Y", center=(AXLE_DX + dx, y_mid, Z_A))
        tub -= _box(AXLE_DX - IDLER_SLOT, AXLE_DX + IDLER_SLOT, side * (yb - 1), side * (HALF_W_OUT + 1), Z_A - r, Z_A + r)
        tub -= _nut_trap(AXLE_DX, side, slot=2 * IDLER_SLOT)
        # battery strap slots
        xc = BATT_X0 + BATT_2X18650.length / 2
        ys = side * STRAP_Y
        tub -= _box(xc - STRAP_L / 2, xc + STRAP_L / 2, ys - STRAP_W / 2, ys + STRAP_W / 2, FLOOR_Z - 1, floor_top + FLOOR_FILLET + 1)

    # toggle switch in the rear wall (teardrop), HC-SR04 transducers through the front wall
    tub -= teardrop_cutter(SWITCH_D + HOLE_COMP, WALL + 2, axis="X", center=(bx0 + WALL / 2, 0.0, SWITCH_Z))
    for sy in (-1, 1):
        tub -= teardrop_cutter(HCSR04_TX_D + SENSOR_CLR + HOLE_COMP, WALL + 2, axis="X",
                               center=(bx1 - WALL / 2, sy * HCSR04_TX_DX / 2, SENSOR_Z))
    return tub


def build():
    return to_bed(design())

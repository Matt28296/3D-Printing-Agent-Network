"""Tracked rover chassis: open-top tub (154 × 76 × 40) that carries both N20 drive motors, the
road-wheel and idler bolts, the 2 × 18650 holder, the power switch and an HC-SR04 sensor.

Design frame = rover world frame (see ../20261026-rover-assembly/rover_frame.py): X forward,
Y left, Z up, ground at Z = 0, drive-sprocket axis at X = 0, Z = Z_A. Printed floor down:
every hole in a wall is horizontal, so each gets a 45° point (teardrop) or a 45° roof.
Bolts: road wheels and idlers run on M3 bolts whose heads sit inside the tub and whose nuts sit
in traps in the wall's outer face (flush), so the wheels can run right next to the wall.
"""
import sys
from pathlib import Path

from build123d import (Align, Axis, Box, BuildPart, BuildSketch, Cylinder, Location, Plane, Polygon, Pos, Rot,
                       extrude, fillet)
from cadlib import HOLE_COMP_DEFAULT, hex_nut_pocket, teardrop_cutter, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-rover-assembly"))
from rover_frame import (AXLE_DX, FLOOR_T, FLOOR_Z, HALF_W_OUT, IDLER_SLOT, MOTOR, MOTOR_FACE_Y, ROAD_X,  # noqa: E402
                         TOP_Z, WALL, X_FRONT_OUT, X_REAR_OUT, Z_A)

from hobby_parts import (BATT_2X18650, HCSR04_TX_D, HCSR04_TX_DX, KCD11_SWITCH_CUTOUT, chamfer_plane_edges,  # noqa: E402
                         gearmotor_wall_cutter)

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT
CORNER_R = 6.0
BED_CHAMFER = 0.4
BOLT_D = 3.4                  # M3 clearance (printed)
NUT_AF, NUT_CLR, NUT_DEPTH = 5.5, 0.3, 2.6    # M3 nut trap from the outer face (nut flush)
BOSS_T = 3.0                  # inward boss on the wall at each wheel bolt (wall + boss = 6)
BOSS_R = 6.5
IDLER_BOSS = (2 * (IDLER_SLOT + 7.0), 15.0)   # x length, z height of the idler boss
CRADLE_HALF_X = 7.0           # motor cradle under the gearbox and can
TIE_W, TIE_D = 4.0, 2.0       # zip-tie groove across the cradle top
COLUMN_D, LID_PILOT, PILOT_DEPTH = 8.0, 2.6, 12.0
COLUMNS = [(-11.5, 30.5), (-11.5, -30.5), (127.5, 30.5), (127.5, -30.5)]
BATT_X0 = 22.0                # battery holder from x 22 (77 long)
STRAP_W, STRAP_L = 3.0, 22.0  # velcro strap slots beside the holder
SWITCH_Z = 32.0               # rocker-switch cut-out centre (rear wall)
SENSOR_Z = 30.0               # HC-SR04 transducer centres (front wall)
SENSOR_CLR = 0.4


def _box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN,) * 3)


def _motor_loc(side):
    return Location(Plane(origin=(0, side * MOTOR_FACE_Y, Z_A), x_dir=(1, 0, 0), z_dir=(0, side, 0)))


def _y_prism(pts_xz, y0, y1):
    """Prism of a polygon given in (x, z), from Y = y0 to y1."""
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ.offset(-y0)):
            Polygon(*[(x, z) for x, z in pts_xz], align=None)
        extrude(amount=-(y1 - y0))
    return bp.part


def _nut_trap(x, side, slot=0.0):
    """Hex nut trap (vertices along ±X, flats top/bottom) from the outer face inward, optionally
    stretched along X into a slot of length `slot`."""
    af = NUT_AF + NUT_CLR + HOLE_COMP
    y_out = side * HALF_W_OUT
    trap = None
    for dx in ((-slot / 2, slot / 2) if slot else (0.0,)):
        h = Pos(x + dx, y_out + side * 0.01, Z_A) * Rot(90 * side, 0, 0) * hex_nut_pocket(af, NUT_DEPTH + 0.01, clearance=0)
        trap = h if trap is None else trap + h
    if slot:
        trap += _box(x - slot / 2, x + slot / 2, *sorted((y_out + side * 0.01, y_out - side * NUT_DEPTH)),
                     Z_A - af / 2, Z_A + af / 2)
    return trap


def design():
    bx0, bx1 = X_REAR_OUT, X_FRONT_OUT
    outer = _box(bx0, bx1, -HALF_W_OUT, HALF_W_OUT, FLOOR_Z, TOP_Z)
    outer = fillet(outer.edges().filter_by(Axis.Z), radius=CORNER_R)
    outer = chamfer_plane_edges(outer, FLOOR_Z, BED_CHAMFER)
    tub = outer - _box(bx0 + WALL, bx1 - WALL, -HALF_W_OUT + WALL, HALF_W_OUT - WALL, FLOOR_Z + FLOOR_T, TOP_Z + 1)
    floor_top = FLOOR_Z + FLOOR_T
    yi = HALF_W_OUT - WALL

    for side in (1, -1):
        # motor cradle and zip-tie groove
        y_end = MOTOR_FACE_Y - MOTOR.gb_len - MOTOR.can_len
        cz = Z_A - MOTOR.gb_h / 2
        tub += _box(-CRADLE_HALF_X, CRADLE_HALF_X, *sorted((side * y_end, side * yi)), floor_top - 0.01, cz)
        yc = side * (MOTOR_FACE_Y - MOTOR.gb_len - MOTOR.can_len / 2)
        tub -= _box(-CRADLE_HALF_X - 1, CRADLE_HALF_X + 1, yc - TIE_W / 2, yc + TIE_W / 2, cz - TIE_D, cz + 0.01)
        # wheel bolt bosses (road wheels round, idler a block)
        for x in ROAD_X:
            tub += Pos(x, side * (yi - BOSS_T / 2 + 0.005), Z_A) * Rot(90, 0, 0) * Cylinder(BOSS_R, BOSS_T + 0.01)
        bl, bh = IDLER_BOSS
        tub += _box(AXLE_DX - bl / 2, AXLE_DX + bl / 2, *sorted((side * (yi - BOSS_T), side * yi)), Z_A - bh / 2, Z_A + bh / 2)
        # lid columns
    for (x, y) in COLUMNS:
        tub += Pos(x, y, floor_top - 0.01) * Cylinder(COLUMN_D / 2, TOP_Z - floor_top + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
        tub -= Pos(x, y, TOP_Z - PILOT_DEPTH) * Cylinder((LID_PILOT + HOLE_COMP) / 2, PILOT_DEPTH + 1,
                                                         align=(Align.CENTER, Align.CENTER, Align.MIN))

    for side in (1, -1):
        # motor shaft/boss and face-screw holes (teardrops pointing up: motor -y = world +Z on the left)
        tub -= _motor_loc(side) * gearmotor_wall_cutter(MOTOR, WALL, hole_comp=HOLE_COMP,
                                                        teardrop="-y" if side > 0 else "+y")
        # road-wheel bolts + nut traps
        for x in ROAD_X:
            tub -= teardrop_cutter(BOLT_D + HOLE_COMP, 2 * (WALL + BOSS_T) + 2, axis="Y", center=(x, side * (yi - 1), Z_A))
            tub -= _nut_trap(x, side)
        # idler bolt slot (8 mm flat top bridges, < 10) + nut slot
        r = (BOLT_D + HOLE_COMP) / 2
        y0, y1 = sorted((side * (yi - BOSS_T - 1), side * (HALF_W_OUT + 1)))
        for dx in (-IDLER_SLOT, IDLER_SLOT):
            tub -= Pos(AXLE_DX + dx, (y0 + y1) / 2, Z_A) * Rot(90, 0, 0) * Cylinder(r, y1 - y0)
        tub -= _box(AXLE_DX - IDLER_SLOT, AXLE_DX + IDLER_SLOT, y0, y1, Z_A - r, Z_A + r)
        tub -= _nut_trap(AXLE_DX, side, slot=2 * IDLER_SLOT)
        # battery strap slots
        ys = side * (BATT_2X18650.width / 2 + 0.5 + STRAP_W / 2)
        xc = BATT_X0 + BATT_2X18650.length / 2
        tub -= _box(xc - STRAP_L / 2, xc + STRAP_L / 2, ys - STRAP_W / 2, ys + STRAP_W / 2, FLOOR_Z - 1, floor_top + 1)

    # power switch in the rear wall, with a 45° roof
    w, h = KCD11_SWITCH_CUTOUT
    sw = w + HOLE_COMP
    pts = [(-sw / 2, SWITCH_Z - h / 2), (sw / 2, SWITCH_Z - h / 2), (sw / 2, SWITCH_Z + h / 2),
           (0, SWITCH_Z + h / 2 + sw / 2), (-sw / 2, SWITCH_Z + h / 2)]
    with BuildPart() as bp:
        with BuildSketch(Plane.YZ.offset(bx0 - 1)):
            Polygon(*pts, align=None)
        extrude(amount=WALL + 2)
    tub -= bp.part
    # HC-SR04 transducers through the front wall
    for sy in (-1, 1):
        tub -= teardrop_cutter(HCSR04_TX_D + SENSOR_CLR + HOLE_COMP, 2 * WALL + 2, axis="X",
                               center=(bx1 - WALL / 2, sy * HCSR04_TX_DX / 2, SENSOR_Z))
    return tub


def build():
    return to_bed(design())

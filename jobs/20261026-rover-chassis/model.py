"""Tracked rover chassis: open-top tub (154 × 76 × 40) that carries both N20 drive motors, the
road-wheel and idler bolts, the 2 × 18650 holder and an HC-SR04 sensor.

Design frame = rover world frame (see ../20261026-rover-assembly/rover_frame.py): X forward,
Y left, Z up, ground at Z = 0, drive-sprocket axis at X = 0, Z = Z_A. Printed floor down:
every hole in a wall is horizontal, so each gets a 45° point (teardrop) or a 45° roof, and every
inward boss runs down to the floor (no overhanging boss undersides).

Round 3 (DFM + strength round 2, Architect's round-3 decisions, deep reviews 01 and 04):
- Drivetrain: no journal. Each N20, rolled 45° about its shaft (rover_frame.MOTOR_ROLL), slides
  from inside the tub along an open V-trough into a diamond pocket. The pocket runs through the
  wall, a housing on the wall's outer face (y 38-42, beside the links) and a nacelle that reaches
  into the track's wrap (y 42-46, r <= 10.9, inside the links' r >= 12.39), until the gearbox face
  stops on the nacelle's skin (2 mm since round 4, y 44-46). The rolled section makes every pocket
  face a 45° face, so the pocket prints without a gable. An aluminium hub on the shaft outside the
  skin carries the sprocket (sprocket job): shaft overhang 11 mm. The pocket sets the motor's height and takes its
  torque; the V-trough under the can (walls >= 4 mm, ±12.1) steadies it, and its zip tie holds it
  down. No rear stop: the motor is located by its gearbox face, so 9 and 11 mm gearboxes both fit.
- Road-wheel bosses Ø26 with an r1.5 rim fillet; BOSS_IN 5.5 at the road-wheel bosses and the
  idler block; 1.5 × 45° strips where the bosses, idler block, cradle and motor housing meet a wall.
- Idler: slot hull up to the teardrop tips (one 8 mm bridge on 45° flanks), Ø9 washer under the
  bolt head, and an M3 jack screw along +X (a set screw in a buttress behind the idler block)
  that bears on the bolt head and holds the track tension without friction.
- Lid columns Ø10 with M3 heat-set inserts, moved to |y| 32.5 so the jack screw's line is clear.
- Strap slots at |y| 26; the toggle switch moved to the lid (the lever no longer sticks out).
Axle bolts: M3 socket head cap screws, class 12.9, FULLY threaded (they must engage the nut
trapped in the wall's outer face): M3 × 50 for the road wheels, M3 × 40 for the idlers.

Round 4 (strength round 3, changes 1 and 2, approved by the user; nothing else changed):
- Skin 1.0 -> 2.0 (rover_frame.SKIN): the skin grows inward, so the gearbox face moves to y 44 and the
  pocket and trough follow it 1 mm inward; the nacelle, hub and track plane stay put.
- Idler clamp: a 2 mm steel head plate (rover_frame.IDLER_PLATE) let into a PLATE_T deep recess in each
  idler-block face between the buttress (x 108) and the front strip (x 129), under the Ø9 washer, so the
  head, JACK_Y and the buttress keep their places; and a 2 mm steel nut plate (rover_frame.NUT_PLATE) on
  the bottom of the idler nut slot, now 9 mm tall and PLATE_T deeper. Both have 45° roofs where they open
  (no flat ceiling to bridge), except the flat strip over the nut plate, which its top edge bears on.
"""
import sys
from pathlib import Path

from build123d import (Align, Axis, Box, BuildPart, BuildSketch, Cone, Cylinder, Plane, Polygon, Pos, Rot,
                       extrude, fillet)
from cadlib import HOLE_COMP_DEFAULT, hex_nut_pocket, teardrop_cutter, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-rover-assembly"))
from rover_frame import (AXLE_DX, BOSS_IN, CHORD_IN, FLOOR_T, FLOOR_Z, HALF_W_OUT, HOUSING_OUT,  # noqa: E402
                         IDLER_PLATE, IDLER_SLOT, LID_SCREWS, LINK_WALL_GAP, MOTOR, MOTOR_FACE_Y, NACELLE_WALL,
                         NUT_PLATE, PLATE_T, ROAD_X, SKIN, TOP_Z, WALL, WASHER_WIDE, X_FRONT_OUT, X_REAR_OUT, Z_A,
                         motor_diamond)

from hobby_parts import BATT_2X18650_LONG, HCSR04_TX_D, HCSR04_TX_DX, chamfer_plane_edges  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT  # +0.2 on hole diameters (fdm-design-rules default; no library row)
CORNER_R = 6.0
BED_CHAMFER = 0.4
BOLT_D = 3.4                  # M3 clearance (printed)
NUT_AF, NUT_CLR, NUT_DEPTH = 5.5, 0.3, 2.6    # M3 nut trap from the outer face (nut flush)
ROAD_BOSS_R = 13.0            # Ø26 road-wheel bosses (strength round 2, change 2)
BOSS_RIM_R = 1.5              # fillet round the road-wheel boss rim (strength round 2, change 2: Kt 1.5)
JOIN = 1.5                    # 1.5 × 45° strips where bosses, idler block, cradle and housing meet a wall (DFM r2 fix 3)
IDLER_BLOCK = (30.0, 24.0)    # x length, height above the floor (strength round 1)
# motor pocket, housing, nacelle and skin (rover_frame: MOTOR_FACE_Y 44.0, SKIN 2.0, HOUSING_OUT 4.0)
GB_CLR = 0.2                  # gearbox in its pocket: total clearance on each section dimension (+ HOLE_COMP)
POCKET_HX = (MOTOR.gb_w + GB_CLR + HOLE_COMP) / 2        # 6.2: along the motor's x (12 mm side)
POCKET_HY = (MOTOR.gb_h + GB_CLR + HOLE_COMP) / 2        # 5.2: along the motor's y (10 mm side)
POCKET = motor_diamond(POCKET_HX, POCKET_HY)             # (x, z - Z_A): rolled 45°, every face at 45°
POCKET_R = max((x * x + z * z) ** 0.5 for x, z in POCKET)                               # 8.09
NACELLE = motor_diamond(POCKET_HX + NACELLE_WALL, POCKET_HY + NACELLE_WALL)             # 2 mm walls
NACELLE_R = max((x * x + z * z) ** 0.5 for x, z in NACELLE)                             # 10.91
assert NACELLE_R <= CHORD_IN - LINK_WALL_GAP - 0.4, "nacelle must stay inside the track's wrap"
HOUSING_HALF_X, HOUSING_TOP = 11.2, Z_A + 12.5   # housing block round the pocket (y 38-42), floor to Z_A + 12.5;
#                               its 1.5 strips end at x -12.7, clear of the rear corner's r6 fillet (from x -13)
HOUSING_EDGE_R = 1.0          # round on the housing's top outer edge
BOSS_HOLE_D = MOTOR.boss_d + 0.5                         # skin hole round the N20 bearing boss (printed Ø4.5)
# V-trough cradle under the can (Architect round 3: 4 mm cheeks standing fully on the cradle; with the motor
# rolled 45° the cheeks are the trough's two walls, >= 4 mm thick at their thinnest, standing on the floor)
CHEEK_T = 4.0
CRADLE_HALF_X = round(max(abs(x) for x, _ in POCKET) + CHEEK_T, 1)                       # 12.1
TROUGH_TOP = Z_A + min(z for x, z in POCKET if abs(x) > POCKET_R * 0.9)                  # Z_A - 0.71: lower side vertex
CRADLE_Y0 = MOTOR_FACE_Y - 11.0 - MOTOR.can_len - 1.0    # 16.5: rear end, takes a motor with an 11 mm gearbox
TIE_W = 4.0                   # zip-tie tunnel through the trough walls, under the can (ties up to 3.6 wide)
TIE_Y = 24.0                  # tunnel centre |y|: under the can for 9 and 11 mm gearboxes, clear of the rear columns
# lid columns with M3 heat-set inserts (deep review 04 S-09, DFM round 2 R1)
COLUMN_D = 10.0
INSERT_D, INSERT_DEPTH = 4.0, 6.5    # M3 × 5.7 brass insert: maker's hole size (no HOLE_COMP), depth
COLUMNS = LID_SCREWS          # (-13, ±32.5), (102, ±32.5): the front pair overlaps the idler block by 2 mm
#                               (no tangent face) and leaves the jack screw's line (|y| 25.4) clear
# idler positive stop: M3 × 20 set screw along +X bearing on the idler-bolt head (Architect round 3)
IDLER_HEAD_Y1 = HALF_W_OUT - WALL - BOSS_IN - WASHER_WIDE[1]   # 27.2: idler-bolt head underside, on its Ø9 washer on the
#                               head plate (the plate is flush with the block face in its recess, so this is unchanged)
JACK_Y = IDLER_HEAD_Y1 - 1.5 - 0.3     # 25.4: jack axis; the screw clears the Ø9 washer by 0.3 and bears on 2.7 mm of head
JACK_PILOT = 2.6              # printed pilot for the self-tapped M3 set screw
JACK_X = (101.5, 108.0)       # buttress: the screw's socket stays outside it at every idler position
JACK_Y_IN = 22.0              # buttress inner face |y|: 1.5 mm from the battery holder (|y| 20.5)
JACK_TOP = Z_A + 4.5
# idler clamp plates (round 4, strength round 3 change 1; plate sizes and PLATE_T in rover_frame)
PLATE_RECESS_X = (JACK_X[1], X_FRONT_OUT - WALL - JOIN)   # (108.0, 129.0): head-plate recess from the buttress's front
#                               face to the start of the front 45° strip, cutting neither (21.0 CAD, about 20.8 printed)
PLATE_RECESS_Z = IDLER_PLATE[1] / 2 + 0.2                 # 5.2: recess bottom Z_A ± 5.2 (10 mm plate + 0.2 a side;
#                               a vertical size, so no HOLE_COMP), then a 45° roof up to the block face
PLATE_RECESS_D = PLATE_T                                  # 2.0: recess depth = plate thickness (|y| 28-30): the plate sits
#                               flush, so the head, its washer, JACK_Y and the buttress stay where they are
NUT_SLOT_H = 9.0              # idler nut slot height, Z_A ± 4.5 (strength round 3: 6.0 -> 9; 8 mm nut plate + 1)
NUT_SLOT_L = NUT_PLATE[0] + 1.0                           # 15.0: x 112.5-127.5 (14 mm plate + 0.5 a side CAD, ~0.4 printed)
NUT_SLOT_D = NUT_DEPTH + PLATE_T                          # 4.6: PLATE_T deeper (|y| 33.4-38): nut plate on the bottom, nut on it
BATT_X0 = 22.0                # battery holder from x 22 (77 mm standard, up to 80 for protected cells)
BATT_LEN = BATT_2X18650_LONG.length
STRAP_W, STRAP_L, STRAP_Y = 3.0, 22.0, 26.0   # velcro strap slots beside the holder (strength round 2: 26)
FLOOR_FILLET = 3.0            # 45° fillet along the inside of every wall at the floor
SENSOR_Z = 30.0               # HC-SR04 transducer centres (front wall)
SENSOR_CLR = 0.4


def _box(x0, x1, y0, y1, z0, z1):
    return Pos(min(x0, x1), min(y0, y1), min(z0, z1)) * Box(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0),
                                                            align=(Align.MIN,) * 3)


def _x_prism(pts_yz, x0, length):
    """Polygon in (y, z), from X = x0 towards +X by `length`."""
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


def _z_prism(pts_xy, z0, length):
    """Polygon in (x, y), from Z = z0 upwards by `length`."""
    with BuildPart() as bp:
        with BuildSketch(Plane.XY.offset(z0)):
            Polygon(*pts_xy, align=None)
        extrude(amount=length)
    return bp.part


def _strip_z(x, y, sx, sy, z0, z1, t=JOIN):
    """Vertical 45° strip in the concave corner at (x, y): legs t along sx and sy (±1)."""
    return _z_prism([(x, y), (x + sx * t, y), (x, y + sy * t)], z0, z1 - z0)


def _nut_trap(x, side):
    """Road-wheel hex nut trap (vertices along ±X, flats top/bottom: the roof is a short flat bridge
    between 60° faces) from the outer face inward. The idler's nut has its own slot (_idler_nut_slot)."""
    af = NUT_AF + NUT_CLR + HOLE_COMP
    y_out = side * HALF_W_OUT
    return Pos(x, y_out + side * 0.01, Z_A) * Rot(90 * side, 0, 0) * hex_nut_pocket(af, NUT_DEPTH + 0.01, clearance=0)


def _plate_recess(side):
    """Recess for the idler's steel head plate in the idler-block face (round 4): PLATE_RECESS_D deep, from the
    buttress's front face to the start of the front 45° strip, its bottom Z_A ± PLATE_RECESS_Z, and a 45° roof
    from the back of the recess up to the block face, so nothing over it needs bridging."""
    yb = HALF_W_OUT - WALL - BOSS_IN                       # 28: block face
    d, zb, zt = PLATE_RECESS_D, Z_A - PLATE_RECESS_Z, Z_A + PLATE_RECESS_Z
    pts = [(yb - 0.1, zb), (yb + d, zb), (yb + d, zt), (yb, zt + d), (yb - 0.1, zt + d)]
    c = _x_prism(pts, PLATE_RECESS_X[0], PLATE_RECESS_X[1] - PLATE_RECESS_X[0])
    return c if side > 0 else c.mirror(Plane.XZ)


def _idler_nut_slot(side):
    """Idler nut slot from the outer face (round 4): NUT_SLOT_D deep and NUT_SLOT_H tall, the steel nut plate
    on its bottom and the sliding nut on the plate. The roof is flat over the plate (its top edge bears there
    in a drop, strength B4), then rises at 45° to the outer face, so the nut zone has no flat ceiling."""
    y0 = HALF_W_OUT - NUT_SLOT_D                           # 33.4: slot bottom
    yp = y0 + PLATE_T                                      # 35.4: plate's outer face = nut seat
    yo = HALF_W_OUT + 0.1
    zb, zt = Z_A - NUT_SLOT_H / 2, Z_A + NUT_SLOT_H / 2
    pts = [(y0, zb), (yo, zb), (yo, zt + yo - yp), (yp, zt), (y0, zt)]
    c = _x_prism(pts, AXLE_DX - NUT_SLOT_L / 2, NUT_SLOT_L)
    return c if side > 0 else c.mirror(Plane.XZ)


def _housing(side):
    """Motor housing on the wall's outer face (y 38 .. 42, beside the links), floor to Z_A + 12.5, with
    rounded outer edges and 45° strips to the wall, plus the diamond nacelle (y 42 .. 46) that reaches
    into the track's wrap and ends in the 2 mm skin the gearbox face stops on."""
    y0, y1 = HALF_W_OUT - 0.01, HALF_W_OUT + HOUSING_OUT
    h = _box(-HOUSING_HALF_X, HOUSING_HALF_X, y0, y1, FLOOR_Z, HOUSING_TOP)
    top_edge = h.edges().filter_by_position(Axis.Y, y1 - 0.01, y1 + 0.01).filter_by_position(Axis.Z, HOUSING_TOP - 0.01,
                                                                                               HOUSING_TOP + 0.01)
    h = fillet(top_edge, radius=HOUSING_EDGE_R)
    for sx in (-1, 1):   # vertical strips at the wall
        h += _strip_z(sx * HOUSING_HALF_X, HALF_W_OUT, sx, 1, FLOOR_Z, HOUSING_TOP)
    h += _x_prism([(HALF_W_OUT - 0.01, HOUSING_TOP - 0.01), (HALF_W_OUT + JOIN, HOUSING_TOP - 0.01),
                   (HALF_W_OUT - 0.01, HOUSING_TOP + JOIN)], -HOUSING_HALF_X, 2 * HOUSING_HALF_X)
    h += _y_prism([(x, Z_A + z) for x, z in NACELLE], y1 - 0.01, MOTOR_FACE_Y + SKIN - y1 + 0.01)
    return h if side > 0 else h.mirror(Plane.XZ)


def _pocket(side, y_in):
    """Diamond gearbox pocket (every face at 45°) from y_in inside the tub to the skin's inner face."""
    c = _y_prism([(x, Z_A + z) for x, z in POCKET], y_in, MOTOR_FACE_Y - y_in)
    return c if side > 0 else c.mirror(Plane.XZ)


def _road_boss(x, side):
    """Ø26 road-wheel boss: round top, block to the floor, from the wall's inner face to the boss
    face at |y| 28, its rim filleted r1.5, and a 1.5 × 45° collar where it meets the wall."""
    yi = HALF_W_OUT - WALL
    yb = yi - BOSS_IN
    floor_top = FLOOR_Z + FLOOR_T
    r = ROAD_BOSS_R
    b = Pos(x, (yb + yi + 0.01) / 2, Z_A) * Rot(90, 0, 0) * Cylinder(r, yi + 0.01 - yb)
    b = b & _box(x - r - 1, x + r + 1, yb - 1, yi + 1, floor_top - 0.01, Z_A + r + 1)   # Ø26 reaches below the floor
    b += _box(x - r, x + r, yb, yi + 0.01, floor_top - 0.01, Z_A)
    rim = [e for e in b.edges().filter_by_position(Axis.Y, yb - 0.01, yb + 0.01)
           if e.bounding_box().min.Z > floor_top + 0.1 or e.bounding_box().max.Z > floor_top + 0.1]
    rim = [e for e in rim if not (abs(e.bounding_box().max.Z - e.bounding_box().min.Z) < 1e-6
                                  and abs(e.bounding_box().min.Z - (floor_top - 0.01)) < 1e-3)]
    b = fillet(rim, radius=BOSS_RIM_R)
    collar = Pos(x, yi - JOIN / 2 + 0.005, Z_A) * Rot(-90, 0, 0) * Cone(r, r + JOIN, JOIN + 0.01)
    collar = collar & _box(x - r - JOIN - 1, x + r + JOIN + 1, yi - JOIN - 1, yi + 1, Z_A, Z_A + r + JOIN + 1)
    b += collar
    for sx in (-1, 1):
        b += _strip_z(x + sx * r, yi, sx, -1, floor_top - 0.01, Z_A)
    return b if side > 0 else b.mirror(Plane.XZ)


def design():
    bx0, bx1 = X_REAR_OUT, X_FRONT_OUT
    xi0, xi1, yi = bx0 + WALL, bx1 - WALL, HALF_W_OUT - WALL
    floor_top = FLOOR_Z + FLOOR_T
    yb = yi - BOSS_IN   # boss inner face (28)

    # ---- outer body: box + the two motor housings, bed chamfer --------------------------------
    outer = _box(bx0, bx1, -HALF_W_OUT, HALF_W_OUT, FLOOR_Z, TOP_Z)
    outer = fillet(outer.edges().filter_by(Axis.Z), radius=CORNER_R)
    for side in (1, -1):
        outer += _housing(side)
    outer = chamfer_plane_edges(outer, FLOOR_Z, BED_CHAMFER)
    tub = outer - _box(xi0, xi1, -yi, yi, floor_top, TOP_Z + 1)

    # ---- floor fillets along the side walls and the end walls ---------------------------------
    f = FLOOR_FILLET
    for s in (1, -1):
        tub += _x_prism([(s * yi, floor_top - 0.01), (s * (yi - f), floor_top - 0.01), (s * yi, floor_top + f)], xi0, xi1 - xi0)
    tub += _y_prism([(xi0, floor_top - 0.01), (xi0 + f, floor_top - 0.01), (xi0, floor_top + f)], -yi, 2 * yi)
    tub += _y_prism([(xi1, floor_top - 0.01), (xi1 - f, floor_top - 0.01), (xi1, floor_top + f)], -yi, 2 * yi)

    for side in (1, -1):
        s = side
        # V-trough cradle under the can: a block up to the trough top (the pocket's diamond is cut through it
        # below), 45° strips where it meets the wall
        tub += _box(-CRADLE_HALF_X, CRADLE_HALF_X, s * CRADLE_Y0, s * (yi + 0.01), floor_top - 0.01, TROUGH_TOP)
        for sx in (-1, 1):
            tub += _strip_z(sx * CRADLE_HALF_X, s * yi, sx, -s, floor_top - 0.01, TROUGH_TOP)
        tub += _x_prism([(s * (yi + 0.01), TROUGH_TOP - 0.01), (s * (yi - JOIN), TROUGH_TOP - 0.01),
                         (s * (yi + 0.01), TROUGH_TOP + JOIN)], -CRADLE_HALF_X, 2 * CRADLE_HALF_X)
        # road-wheel bosses
        for x in ROAD_X:
            tub += _road_boss(x, side)
        # idler block, buttress for the jack screw, 45° strips at the side and front walls
        bl, bh = IDLER_BLOCK
        top = floor_top + bh
        tub += _box(AXLE_DX - bl / 2, xi1 + 0.01, s * yb, s * (yi + 0.01), floor_top - 0.01, top)
        tub += _x_prism([(s * (yi + 0.01), top - 0.01), (s * (yi - JOIN), top - 0.01), (s * (yi + 0.01), top + JOIN)],
                        AXLE_DX - bl / 2, xi1 - (AXLE_DX - bl / 2) + 0.01)
        tub += _strip_z(xi1, s * yb, -1, -s, floor_top - 0.01, top)
        tub += _y_prism([(xi1 + 0.01, top - 0.01), (xi1 - JOIN, top - 0.01), (xi1 + 0.01, top + JOIN)],
                        min(s * yb, s * (yi + 0.01)), yi + 0.01 - yb)
        tub += _box(JACK_X[0], JACK_X[1], s * JACK_Y_IN, s * (yi + 0.01), floor_top - 0.01, JACK_TOP)

    # ---- lid columns (joined to the walls) with heat-set insert holes -------------------------
    for (x, y) in COLUMNS:
        tub += Pos(x, y, floor_top - 0.01) * Cylinder(COLUMN_D / 2, TOP_Z - floor_top + 0.01,
                                                      align=(Align.CENTER, Align.CENTER, Align.MIN))
        tub -= Pos(x, y, TOP_Z - INSERT_DEPTH) * Cylinder(INSERT_D / 2, INSERT_DEPTH + 1,
                                                          align=(Align.CENTER, Align.CENTER, Align.MIN))

    # ---- cuts ------------------------------------------------------------------------------------
    for side in (1, -1):
        s = side
        y_mid = s * (yb + HALF_W_OUT) / 2
        span = HALF_W_OUT - yb + 2
        # diamond gearbox pocket from the trough's rear end through the wall, housing and nacelle;
        # skin hole for the N20 bearing boss and shaft
        tub -= _pocket(side, CRADLE_Y0 - 1.0)
        y_skin = s * (MOTOR_FACE_Y + SKIN / 2)
        tub -= teardrop_cutter(BOSS_HOLE_D + HOLE_COMP, SKIN + 2, axis="Y", center=(0.0, y_skin, Z_A))
        # zip-tie tunnel through the trough walls, under the can (the 2 mm gap between the can and the V's bottom)
        zb = Z_A + min(z for _, z in POCKET)
        tub -= _box(-CRADLE_HALF_X - 1, CRADLE_HALF_X + 1, s * (TIE_Y - TIE_W / 2), s * (TIE_Y + TIE_W / 2),
                    zb, Z_A - MOTOR.can_d / 2 - 0.2)
        # road-wheel bolts + nut traps
        for x in ROAD_X:
            tub -= teardrop_cutter(BOLT_D + HOLE_COMP, span, axis="Y", center=(x, y_mid, Z_A))
            tub -= _nut_trap(x, side)
        # idler bolt slot: teardrop ends + a hull up to the teardrop tips (8 mm bridge) + nut slot
        r = (BOLT_D + HOLE_COMP) / 2
        for dx in (-IDLER_SLOT, IDLER_SLOT):
            tub -= teardrop_cutter(BOLT_D + HOLE_COMP, span, axis="Y", center=(AXLE_DX + dx, y_mid, Z_A))
        tub -= _box(AXLE_DX - IDLER_SLOT, AXLE_DX + IDLER_SLOT, s * (yb - 1), s * (HALF_W_OUT + 1),
                    Z_A - r, Z_A + r * 2 ** 0.5)
        # steel clamp plates (round 4): head-plate recess in the block face, nut slot 9 tall and PLATE_T deeper
        tub -= _plate_recess(side)
        tub -= _idler_nut_slot(side)
        # jack-screw pilot along X through the buttress, teardrop pointing up
        tub -= teardrop_cutter(JACK_PILOT + HOLE_COMP, JACK_X[1] - JACK_X[0] + 6, axis="X",
                               center=((JACK_X[0] + JACK_X[1]) / 2, s * JACK_Y, Z_A))
        # battery strap slots
        xc = BATT_X0 + BATT_LEN / 2
        ys = s * STRAP_Y
        tub -= _box(xc - STRAP_L / 2, xc + STRAP_L / 2, ys - STRAP_W / 2, ys + STRAP_W / 2, FLOOR_Z - 1, floor_top + FLOOR_FILLET + 1)

    # HC-SR04 transducers through the front wall
    for sy in (-1, 1):
        tub -= teardrop_cutter(HCSR04_TX_D + SENSOR_CLR + HOLE_COMP, WALL + 2, axis="X",
                               center=(bx1 - WALL / 2, sy * HCSR04_TX_DX / 2, SENSOR_Z))
    return tub


def build():
    return to_bed(design())

"""Robot arm base: open-bottom box carrying the base-yaw MG996R, the ESP32 cradle and the DC jack.

Design frame = assembly frame (see ../20261025-robot-arm-assembly/assembly_plan.md):
origin on the base-servo shaft axis at the top-plate top surface, Z up, desk at Z = -40.
Printed upside down (top plate on the bed), so every opening in a wall gets a
45° roof pointing at the desk side, which faces up in print.
"""
from build123d import Align, Box, Cylinder, Pos, Rot
from cadlib import HOLE_COMP_DEFAULT, teardrop_cutter, to_bed
from hobby_parts import MG996R, chamfer_plane_edges, servo_mount_cutter

# --- parameters (mm) -----------------------------------------------------------
SERVO = MG996R            # nominal; replace with measured values (spec §3)
HOLE_COMP = HOLE_COMP_DEFAULT   # +0.2 mm on hole diameters, default from fdm-design-rules (no library row yet)
BED_CHAMFER = 0.4         # elephant's-foot relief on the bed face (top plate, printed upside down)
SERVO_CLR = 0.4           # base-servo window clearance (printed, 0.2/side), default from fdm-design-rules
BX, BY, H = 110.0, 104.0, 40.0   # outside size, height (desk to top-plate top)
WALL = 3.0                # 6-7 perimeters
PLATE_T = 4.0             # top plate
CORNER_R = 6.0            # outside corner rounding (vertical edges)
PILLAR_D, PILLAR_HOLE = 8.0, 3.4      # desk-screw pillars, M3 clearance (printed)
SERVO_BOSS_D, SERVO_BOSS_L = 6.5, 6.0  # under-plate bosses lengthening the servo screw grip
RING_PILOT_R, RING_PILOT_ANG = 47.5, (30.0, 150.0, 270.0)   # ring tab screws; at 270° the Ø2.8 pilot stops 0.1 mm short of the inner wall (y -49)
CRADLE_PILOTS = [(-9.4, 18.0), (-9.4, 38.0), (40.0, 7.9)]  # ESP32 cradle screws (x, y)
CRADLE_BOSS_D, CRADLE_BOSS_L = 7.0, 6.0   # boss Z -4..-10
PILOT = 2.6               # M3 self-tapping pilot (printed)
USB_SLOT = (13.0, 7.0)    # (width along Y, height) centred on y=28, z=-8.5, in the +X wall
USB_Y, USB_Z = 28.0, -8.5
JACK_D, JACK_Y, JACK_Z = 11.4, -28.0, -20.0   # 5.5x2.1 panel jack (Ø11 thread), in the -X wall (printed)
CABLE_SLOT = (14.0, 8.0, -40.0, -36.0)        # arm-servo leads through the top plate (w, h, x, y): outside the
                                              # ring (r >= 46) and 3 mm clear of the corner pillar


def _box(x, y, z, at=(0, 0, 0)):
    return Pos(*at) * Box(x, y, z, align=(Align.CENTER, Align.CENTER, Align.MIN))


def design():
    from build123d import fillet, Axis
    outer = _box(BX, BY, H, at=(0, 0, -H))
    outer = fillet(outer.edges().filter_by(Axis.Z), radius=CORNER_R)
    outer = chamfer_plane_edges(outer, 0.0, BED_CHAMFER)
    inner = _box(BX - 2 * WALL, BY - 2 * WALL, H - PLATE_T + 0.01, at=(0, 0, -H - 0.01))
    part = outer - inner

    # corner pillars (full height) with desk-screw holes
    px, py = BX / 2 - WALL - PILLAR_D / 2 + 1.5, BY / 2 - WALL - PILLAR_D / 2 + 1.5
    for sx in (-1, 1):
        for sy in (-1, 1):
            part += Pos(sx * px, sy * py, -H) * Cylinder(PILLAR_D / 2, H, align=(Align.CENTER, Align.CENTER, Align.MIN))
            part -= Pos(sx * px, sy * py, -H - 1) * Cylinder((PILLAR_HOLE + HOLE_COMP) / 2, H + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # bosses under the plate for the servo tab screws and the cradle screws
    xm = -(SERVO.length - SERVO.shaft_from_end) + SERVO.length / 2
    servo_holes = [(xm + dx, dy) for dx in (-SERVO.hole_dx / 2, SERVO.hole_dx / 2) for dy in (-SERVO.hole_dy / 2, SERVO.hole_dy / 2)]
    for (x, y) in servo_holes:
        part += Pos(x, y, -PLATE_T - SERVO_BOSS_L) * Cylinder(SERVO_BOSS_D / 2, SERVO_BOSS_L, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for (x, y) in CRADLE_PILOTS:
        part += Pos(x, y, -PLATE_T - CRADLE_BOSS_L) * Cylinder(CRADLE_BOSS_D / 2, CRADLE_BOSS_L, align=(Align.CENTER, Align.CENTER, Align.MIN))
        part -= Pos(x, y, -PLATE_T - CRADLE_BOSS_L - 1) * Cylinder((PILOT + HOLE_COMP) / 2, CRADLE_BOSS_L + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # servo window + tab pilot holes (through plate and bosses)
    part -= servo_mount_cutter(SERVO, PLATE_T + SERVO_BOSS_L, clearance=SERVO_CLR, hole_comp=HOLE_COMP)

    # turntable-ring tab pilots
    import math
    for a in RING_PILOT_ANG:
        x, y = RING_PILOT_R * math.cos(math.radians(a)), RING_PILOT_R * math.sin(math.radians(a))
        part -= Pos(x, y, -PLATE_T - 1) * Cylinder((PILOT + HOLE_COMP) / 2, PLATE_T + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # cable pass-through in the top plate
    w, h, cx, cy = CABLE_SLOT
    part -= Pos(cx, cy, -PLATE_T - 1) * Box(w, h, PLATE_T + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # USB slot in the +X wall, roof pointing -Z (up in print)
    sw, sh = USB_SLOT
    slot = Pos(BX / 2, USB_Y, USB_Z) * Box(WALL * 4, sw, sh)
    roof = Pos(BX / 2, USB_Y, USB_Z - sh / 2) * Rot(45, 0, 0) * Box(WALL * 4, sw / 2 ** 0.5, sw / 2 ** 0.5)
    part -= slot + roof

    # DC jack hole in the -X wall: teardrop with its point towards -Z (up in print)
    jack = teardrop_cutter(JACK_D + HOLE_COMP, WALL * 4, axis="X", center=(-BX / 2, JACK_Y, JACK_Z))
    part -= Rot(0, 0, 0) * _mirror_z(jack, JACK_Z)
    return part


def _mirror_z(shape, z0):
    """Mirror a cutter about the plane Z = z0 (turns an up-pointing teardrop to point down)."""
    from build123d import Plane, mirror
    return mirror(shape, about=Plane.XY.offset(z0))


def build():
    return to_bed(Rot(180, 0, 0) * design())

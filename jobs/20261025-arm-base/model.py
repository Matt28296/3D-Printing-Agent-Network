"""Robot arm base: open-bottom box carrying the base-yaw MG996R, the ESP32 cradle and the DC jack.

Design frame = assembly frame (see ../20261025-robot-arm-assembly/assembly_plan.md):
origin on the base-servo shaft axis at the top-plate top surface, Z up, desk at Z = -40.
Printed upside down (top plate on the bed), so every opening in a wall gets a
45° roof pointing at the desk side, which faces up in print.

Round 3 (deep review 01 B1): the servo window has a lead notch at each case end (4.4 x 2.0 mm
printed), so the MG996R's lead root can pass when the servo goes in case bottom first; 2.0 mm
printed ligament to the nearest tab pilot.

Round 5 (links strength round 4, SF 1.21 in the 4 mm plate round the tension-side tab boss):
local pads under the top plate round the base servo's tabs make the plate 7.5 mm thick round the
far tab (x -34.4) and 5.5 mm round the near tab (x 14.1), where the ESP32 below limits it. The
window, the lead notches and the tab pilots go through the pads; the notches now run through
the plate and the pad, so the lead's root still passes. The cradle pilots run 1 mm into the
plate (deep review 01 N7: the M3 x 10 gets 1 mm of depth margin).
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
CRADLE_PILOT_DEPTH = 7.0  # blind pilot from the boss end (Z -10) to Z -3: the M3 x 10 through the cradle's 4 mm clamp
                          # reaches Z -4, 1 mm short of the end (deep review 01 N7, DFM round 4 note 1); 3 mm of plate left
PILOT = 2.6               # M3 self-tapping pilot (printed)
# servo tab pads (links strength round 4 -> design round 5): the plate round the tension screw's boss
SERVO_XM = -(SERVO.length - SERVO.shaft_from_end) + SERVO.length / 2   # -10.15: servo body centre (x)
TAB_X_FAR = SERVO_XM - SERVO.hole_dx / 2      # -34.4: far tab pilots (y +-5), 65 % of the overturning moment
TAB_X_NEAR = SERVO_XM + SERVO.hole_dx / 2     # 14.1: near tab pilots, 35 %
PAD_T_FAR = 7.5           # plate + pad round the far tab: SF 3.39 at Kt 2.5 under the yaw stall (strength round 4 FIX)
PAD_T_NEAR = 5.5          # round the near tab: SF 3.39 at Kt 2.5; the ESP32 under the plate limits it
PAD_FAR = (-52.5, -19.4, -20.5, 20.5)    # x0, x1, y0, y1: from the -X wall to 15 mm past the far bosses, 15.5 mm round
                                         # them in y; 1.85 mm clear of the 150° ring pilot, 11.5 clear of the cable slot
PAD_NEAR = (-0.9, 29.1, -20.0, 18.0)     # 15 mm round the near bosses, except towards the ESP32 (+y): the pad stops at
                                         # y 18, 2 mm short of the WROOM module's can (y >= 20, top Z -6.8 or lower)
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
        part -= Pos(x, y, -PLATE_T - CRADLE_BOSS_L - 1) * Cylinder((PILOT + HOLE_COMP) / 2, CRADLE_PILOT_DEPTH + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # pads under the plate round the servo tabs (strength round 4 -> design round 5); they merge with the tab bosses
    for (x0, x1, y0, y1), t in ((PAD_FAR, PAD_T_FAR), (PAD_NEAR, PAD_T_NEAR)):
        part += Pos(x0, y0, -t) * Box(x1 - x0, y1 - y0, t - PLATE_T + 0.01, align=(Align.MIN,) * 3)

    # servo window, tab pilot holes and the lead notches at both case ends (deep review 01 B1), through the plate,
    # the pads and the bosses' depth (Z -11 .. 1). Below the pads the notch footprint is open: the ribbon passes
    # between the bosses, which stand >= 3 mm off the centreline at the case end; the notch's outer corners only
    # graze the Ø6.5 bosses (0.01 mm), so cutting the full depth leaves no 0.01 mm ledge on them (DFM round 4, #6)
    part -= servo_mount_cutter(SERVO, PLATE_T + SERVO_BOSS_L, clearance=SERVO_CLR, hole_comp=HOLE_COMP, lead="notch")

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

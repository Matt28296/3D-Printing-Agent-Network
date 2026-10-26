"""Turntable: Ø96 × 8 disk on the base-yaw horn, with the shoulder upright holding the shoulder MG996R.

Design frame = assembly frame at yaw 0 (see assembly_plan.md). The base servo's double-arm
horn sits FLAT on the disk underside (Z = 16.5, the bed face, so no bridged pocket); an M3
centre screw + washer from the top clamps disk and horn onto the spline, and two small screws
drilled through the horn's arm holes stop it turning. The shoulder servo hangs through the
upright (tabs on its +Y face, shaft +Y, body HORIZONTAL along X, centred on the yaw axis, so the
shoulder axis sits at X = +10.15): its tab screws sit beside the window, clear of the 45° roof.
Printed disk-down.
"""
from build123d import Align, Box, BuildPart, BuildSketch, Cylinder, Plane, Polygon, Pos, extrude
from cadlib import HOLE_COMP_DEFAULT, to_bed
from hobby_parts import MG996R, chamfer_plane_edges, horn_face_z, horn_pocket_cutter, servo_mount_cutter

# --- parameters (mm) -----------------------------------------------------------
SERVO = MG996R                 # both base and shoulder servos; nominal, see spec §3
HOLE_COMP = HOLE_COMP_DEFAULT  # +0.2 on hole diameters (default, fdm-design-rules)
Z0 = horn_face_z(SERVO)        # 16.5: disk underside = base horn face (horn flat on the disk)
DISK_R, DISK_T = 48.0, 8.0     # 8 mm: strength-analyst round 1 (clamp-screw floor, disk ahead of the upright)
CLR = 0.4                      # servo window clearance (printed)
UP_T, UP_W = 7.0, 66.0         # upright thickness (Y) and width (X): tab span 54 + 6 each side
UP_Y = -5.0                    # upright +Y face = shoulder servo tab underside plane
XS = SERVO.length / 2 - SERVO.shaft_from_end   # 10.15: shoulder axis X (servo body centred on X = 0)
ZS = 60.5                      # shoulder axis height (~100 mm above the desk)
WIN_HALF_H = (SERVO.width + CLR + HOLE_COMP) / 2
ROOF_H = (SERVO.length + CLR + HOLE_COMP) / 2   # 45° roof over the 41 mm window
UP_TOP = ZS + WIN_HALF_H + ROOF_H + 6.0         # 6 mm above the roof apex
GUSSET_T, GUSSET_X = 4.0, 30.5                  # |X| 28.5-32.5, outside the body (±20.4) and its cable
GUSSET_LEN, GUSSET_H = 23.0, 70.0               # toe at r 47.6 < disk r 48 (DFM round 1); 70 tall (strength)
ROOT_FILLET = 3.0              # 45° wedge both sides of the upright root (stress relief across layers)
BED_CHAMFER = 0.4


def shoulder_frame():
    """Location of the shoulder servo frame (servo x→+X, y→−Z, z→+Y)."""
    from build123d import Location
    return Location(Plane(origin=(XS, UP_Y, ZS), x_dir=(1, 0, 0), z_dir=(0, 1, 0)))


def _yz_prism(pts, x0, width):
    """Extrude a polygon given in (Y, Z) from X = x0 by `width` in +X."""
    with BuildPart() as g:
        with BuildSketch(Plane.YZ.offset(x0)):
            Polygon(*pts, align=None)
        extrude(amount=width)
    return g.part


def design():
    top = Z0 + DISK_T
    disk = Pos(0, 0, Z0) * Cylinder(DISK_R, DISK_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    disk = chamfer_plane_edges(disk, Z0, BED_CHAMFER)

    up_h = UP_TOP - top
    y_back = UP_Y - UP_T
    part = disk + Pos(0, UP_Y - UP_T / 2, top) * Box(UP_W, UP_T, up_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # root wedges (front and back) along the full upright width
    f = ROOT_FILLET
    part += _yz_prism([(UP_Y - 0.01, top), (UP_Y + f, top), (UP_Y - 0.01, top + f)], -UP_W / 2, UP_W)
    part += _yz_prism([(y_back + 0.01, top), (y_back - f, top), (y_back + 0.01, top + f)], -UP_W / 2, UP_W)
    # gussets behind the upright (−Y side), outside the servo body (|X| <= 20.4)
    for sx in (-1, 1):
        part += _yz_prism([(y_back + 0.01, top), (y_back - GUSSET_LEN, top), (y_back + 0.01, top + GUSSET_H)],
                          sx * GUSSET_X - GUSSET_T / 2, GUSSET_T)
    # base-horn clamp screw hole (M3 + washer from the top), no pocket
    part -= Pos(0, 0, Z0) * horn_pocket_cutter(SERVO, depth=0, link_t=DISK_T + 2, hole_comp=HOLE_COMP)
    # shoulder servo window (roof up: servo −y = world +Z), teardrop pilots pointing up, through the upright
    part -= shoulder_frame() * servo_mount_cutter(SERVO, UP_T, clearance=CLR, roof="-y", through=UP_T * 2 + 2,
                                                  hole_comp=HOLE_COMP, pilot_teardrop="-y")
    return part


def build():
    return to_bed(design())

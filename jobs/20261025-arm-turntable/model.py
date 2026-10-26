"""Turntable: Ø96 × 8 disk on the base-yaw horn, with the shoulder upright holding the shoulder MG996R.

Design frame = assembly frame at yaw 0 (see assembly_plan.md). The base servo's round Ø25 DISC
horn sits FLAT on the disk underside (Z = 16.5, the bed face, so no bridged pocket; deep review
03 SYS-05: the disc supports the disk ±12.5 mm in every direction, the double arm only on its
Ø11 hub across the arms); an M3 × 14 socket-head centre screw + Ø9 washer from the top clamps
disk and horn onto the spline, and four M2 × 8 self-tappers through four of the disc's holes
(round 5; was 2 × M2 × 6) stop it turning. Their pilots are drilled at assembly through the
horn's own holes, so they follow whatever hole circle the disc has: the disk is plain solid
plastic from r 4 to r 13 (print_requirements: 6 mm of solid bottom layers) for a 6 mm-deep
pilot anywhere on it. The shoulder servo hangs through the upright (tabs on its +Y face, shaft
+Y, body HORIZONTAL along X, centred on the yaw axis, so the shoulder axis sits at X = +10.15):
its tab screws sit beside the window, clear of the 45° roof. The window has a lead notch at
each case end (deep review 01 B1) with a 45° top, because it is a hole in a standing wall.
Round 5 (links strength round 4: upright window bottom SF 2.80, pilot row 2.83): the gussets
are 90 tall (was 70), cut off level with the upright's top (Z 97.3), where they are 4.4 deep.
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
GUSSET_LEN, GUSSET_H = 23.0, 90.0               # toe at r 47.6 < disk r 48 (DFM round 1); 90 tall (links strength
                                                # round 4: 70 -> 90, window bottom SF 2.80 -> 3.27, pilot row 2.83 -> 3.46),
                                                # cut off at UP_TOP: the outer face leans 14.3° from vertical
# base disc horn anti-rotation (links strength round 4: 2 x M2 x 6 SF 2.00 -> 4 x M2 x 8, 6.51 at r 9, 5.06 at r 7).
# Not modelled: the pilots are drilled at assembly through the disc's own holes (BUILD_GUIDE §4 step 3).
ANTI_ROT_N, ANTI_ROT_L = 4, 8.0   # 4 x M2 x 8 self-tappers: 8 - 2.8 (disc) = 5.2 mm in the disk
DISC_HOLE_R_MIN = 7.0             # use 4 holes in opposite pairs on one circle at r >= 7 (measure the disc, BUILD_GUIDE §2)
ANTI_ROT_PILOT_D, ANTI_ROT_PILOT_DEPTH = 1.5, 6.0   # drilled 6 mm into the 8 mm disk, inside its 6 mm of solid bottom
                                                    # layers (print_requirements.json bottom_solid_layers 30)
ANTI_ROT_ZONE = (4.0, 13.0)       # r range of the disk underside kept plain and solid for those pilots (cad_checks)
ROOT_FILLET = 3.0              # 45° wedge both sides of the upright root (stress relief across layers)
WASHER_CLEAR_X = 6.0           # front wedge stops at |X| >= 6 so the Ø9 clamp washer seats flat (DFM/strength round 2)
BED_CHAMFER = 0.4


def shoulder_frame():
    """Location of the shoulder servo frame (servo x→+X, y→−Z, z→+Y)."""
    from build123d import Location
    return Location(Plane(origin=(XS, UP_Y, ZS), x_dir=(1, 0, 0), z_dir=(0, 1, 0)))


def _notch_tops():
    """45° tops over the two lead notches, in the servo frame (servo -y = world +Z = up in print).
    servo_mount_cutter(lead="notch") cuts each notch nw wide, from the case end to `reach` beyond it;
    this adds a right triangle on its upper side so the notch has no flat ceiling."""
    s = SERVO
    nw = s.lead_notch_w + HOLE_COMP
    reach = s.lead_notch_reach + HOLE_COMP / 2
    tops = None
    for xe, e in ((s.shaft_from_end, 1), (-(s.length - s.shaft_from_end), -1)):
        # base 0.01 inside the notch, run 0.02 past its end so the 45° slope meets the notch box's outer top corner
        # (the cutter's box runs 0.01 past the reach): no flat ceiling at the notch end (DFM round 4 note 2)
        tri = [(xe, -nw / 2 + 0.01), (xe + e * (reach + 0.02), -nw / 2 + 0.01), (xe, -nw / 2 - reach - 0.01)]
        with BuildPart() as g:
            with BuildSketch(Plane.XY.offset(-UP_T - 1)):
                Polygon(*tri, align=None)
            extrude(amount=UP_T + 2)
        tops = g.part if tops is None else tops + g.part
    return tops


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
    for x0 in (-UP_W / 2, WASHER_CLEAR_X):   # front wedge in two pieces, clear of the clamp washer
        part += _yz_prism([(UP_Y - 0.01, top), (UP_Y + f, top), (UP_Y - 0.01, top + f)], x0, UP_W / 2 - WASHER_CLEAR_X)
    part += _yz_prism([(y_back + 0.01, top), (y_back - f, top), (y_back + 0.01, top + f)], -UP_W / 2, UP_W)
    # gussets behind the upright (−Y side), outside the servo body (|X| <= 20.4); cut off level with the upright's top
    g_top = min(top + GUSSET_H, UP_TOP)
    g_len_top = GUSSET_LEN * (1 - (g_top - top) / GUSSET_H)          # 4.4 deep at the top (0 if it ends below)
    prof = [(y_back + 0.01, top), (y_back - GUSSET_LEN, top)]
    prof += [(y_back - g_len_top, g_top), (y_back + 0.01, g_top)] if g_len_top > 0.01 else [(y_back + 0.01, g_top)]
    for sx in (-1, 1):
        part += _yz_prism(prof, sx * GUSSET_X - GUSSET_T / 2, GUSSET_T)
    # base-horn clamp screw hole (M3 + washer from the top), no pocket
    part -= Pos(0, 0, Z0) * horn_pocket_cutter(SERVO, depth=0, link_t=DISK_T + 2, hole_comp=HOLE_COMP)
    # shoulder servo window (roof up: servo −y = world +Z), teardrop pilots pointing up, through the upright;
    # lead notches at both case ends with 45° tops (deep review 01 B1)
    part -= shoulder_frame() * (servo_mount_cutter(SERVO, UP_T, clearance=CLR, roof="-y", through=UP_T * 2 + 2,
                                                   hole_comp=HOLE_COMP, pilot_teardrop="-y", lead="notch")
                                + _notch_tops())
    return part


def build():
    return to_bed(design())

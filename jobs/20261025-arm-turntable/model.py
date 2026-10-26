"""Turntable: Ø96 disk on the base-yaw horn, with the shoulder upright holding the shoulder MG996R.

Design frame = assembly frame at yaw 0 (see assembly_plan.md). The disk underside sits on
Z = 14.5, so the base servo's double-arm horn (face at Z = 16.5) sits 2 mm deep in its slot. The shoulder servo hangs through the upright (tabs on its
+Y face, shaft +Y, body length HORIZONTAL along X, centred on the yaw axis, so the shoulder
axis sits at X = +10.15). Horizontal, the tab screws sit beside the window, clear of its
45° roof (with the body vertical the roof cut through the top tab pilots). Printed disk-down.
"""
from build123d import Align, Box, BuildPart, BuildSketch, Cylinder, Plane, Polygon, Pos, Rot, extrude
from cadlib import chamfer_bottom, to_bed
from hobby_parts import HORN_DEPTH, MG996R, horn_pocket_cutter, link_back_z, servo_mount_cutter

# --- parameters (mm) -----------------------------------------------------------
SERVO = MG996R                 # both base and shoulder servos; nominal, see spec §3
Z0 = link_back_z(SERVO)        # 14.5: disk underside (horn face 16.5 sits 2 mm up in its pocket)
DISK_R, DISK_T = 48.0, 5.0
CLR = 0.4                      # servo window clearance
UP_T, UP_W = 5.0, 66.0         # upright thickness (Y) and width (X): tab span 54 + 6 each side
UP_Y = -5.0                    # upright +Y face = shoulder servo tab underside plane
XS = SERVO.length / 2 - SERVO.shaft_from_end   # 10.15: shoulder axis X (servo body centred on X = 0)
ZS = 60.5                      # shoulder axis height (~100 mm above the desk)
WIN_HALF_H = (SERVO.width + CLR) / 2           # window half height
ROOF_H = (SERVO.length + CLR) / 2              # 45° roof over the 41 mm window
UP_TOP = ZS + WIN_HALF_H + ROOF_H + 6.0        # 6 mm above the roof apex
GUSSET_T, GUSSET_X, GUSSET_LEN, GUSSET_H = 4.0, 30.5, 30.0, 50.0   # |X| 28.5-32.5, outside the body (±20.4) and its cable


def shoulder_frame():
    """Location of the shoulder servo frame (servo x→+X, y→−Z, z→+Y)."""
    from build123d import Location
    return Location(Plane(origin=(XS, UP_Y, ZS), x_dir=(1, 0, 0), z_dir=(0, 1, 0)))


def design():
    top = Z0 + DISK_T
    disk = Pos(0, 0, Z0) * Cylinder(DISK_R, DISK_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # horn slot on the underside (link frame: origin at the back face, +Z into the disk)
    disk -= Pos(0, 0, Z0) * horn_pocket_cutter(SERVO, depth=HORN_DEPTH, link_t=DISK_T + 2)

    up_h = UP_TOP - top
    upright = Pos(0, UP_Y - UP_T / 2, top) * Box(UP_W, UP_T, up_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    part = disk + upright
    # gussets behind the upright (−Y side), outside the servo body (|X| ≤ 20.4)
    for sx in (-1, 1):
        with BuildPart() as g:
            with BuildSketch(Plane.YZ.offset(sx * GUSSET_X - GUSSET_T / 2)):
                Polygon((UP_Y - UP_T, top), (UP_Y - UP_T - GUSSET_LEN, top), (UP_Y - UP_T, top + GUSSET_H), align=None)
            extrude(amount=GUSSET_T)
        part += g.part
    # shoulder servo window (roof up: servo −y = world +Z) and tab pilots, through the upright
    part -= shoulder_frame() * servo_mount_cutter(SERVO, UP_T, clearance=CLR, roof="-y", through=UP_T * 2 + 2)
    return part


def build():
    return to_bed(chamfer_bottom(design(), 0.4))

"""Gripper base: 5 mm plate on the wrist SG90 horn, carrying the gripper SG90 and the fixed jaw.
Printed flat, back face on the bed.

Design frame G: origin on the wrist axis at the plate's back face, +z away from the wrist
servo, +x towards the fingertips. The gripper SG90 sits at x = 40 so its body (radius >= 23.4
from the wrist axis) clears the wrist servo body (radius <= 17.7) through the whole wrist sweep.
The moving jaw (separate part, frame J) pivots on the gripper servo and closes against the
fixed jaw's face at y = -6, in the band z 14.4-19.4.
"""
from build123d import Align, Box, Pos
from cadlib import chamfer_bottom, to_bed
from hobby_parts import SG90, horn_pocket_cutter, link_back_z, rounded_plate, servo_mount_cutter

# --- parameters (mm) -----------------------------------------------------------
SERVO = SG90            # wrist horn and gripper servo; nominal, measure yours (spec §3)
T = 5.0
GRIP_X = 40.0           # gripper servo axis
X0, X1, Y0, Y1 = -9.0, 95.0, -16.0, 9.0
CORNER_R = 6.0
JAW_X0, JAW_X1 = 55.0, 95.0          # fixed jaw length (fingertip at x = 95)
JAW_Y0, JAW_Y1 = -14.0, -6.0         # jaw face at y = -6
JAW_TOP = T + link_back_z(SERVO) + 5.0   # = top of the moving jaw (19.4)
CLR = 0.4


def design():
    base = rounded_plate(X0, X1, Y0, Y1, T, r=CORNER_R)
    base += Pos(JAW_X0, JAW_Y0, T - 0.01) * Box(JAW_X1 - JAW_X0, JAW_Y1 - JAW_Y0, JAW_TOP - T + 0.01,
                                                 align=(Align.MIN,) * 3)
    base -= horn_pocket_cutter(SERVO, link_t=T)                    # wrist horn, back face
    base -= Pos(GRIP_X, 0, T) * servo_mount_cutter(SERVO, T, clearance=CLR, through=T * 2 + 2)
    return base


def build():
    return to_bed(chamfer_bottom(design(), 0.4))

"""Gripper base: 8 mm plate on the wrist SG90 horn, carrying the gripper SG90 and the fixed jaw.
Printed flat, back face on the bed (the SG90 horn pocket bridges < 8 mm).

Design frame G: origin on the wrist axis at the plate's back face, +z away from the wrist
servo, +x towards the fingertips. An M2 centre screw + washer from the front face clamps plate
and horn onto the wrist spline. The gripper SG90 sits at x = 40 so its body (radius >= 23.4
from the wrist axis) clears the wrist servo body (radius <= 17.7) through the whole wrist sweep.
The moving jaw (separate part, frame J) pivots on the gripper servo and closes against the
fixed jaw's face at y = -6.
"""
from build123d import Align, Box, Pos
from cadlib import HOLE_COMP_DEFAULT, to_bed
from hobby_parts import (SG90, chamfer_plane_edges, horn_pocket_cutter, link_back_z, rounded_plate,
                         servo_mount_cutter)

# --- parameters (mm) -----------------------------------------------------------
SERVO = SG90            # wrist horn and gripper servo; nominal, measure yours (spec §3)
HOLE_COMP = HOLE_COMP_DEFAULT   # +0.2 on hole diameters (default, fdm-design-rules)
T = 8.0                 # strength round 1: 5 -> 8
GRIP_X = 40.0           # gripper servo axis
X0, X1, Y0, Y1 = -9.0, 99.0, -16.0, 9.0   # X1 99: the jaw block (to x 95) stays off the rounded corner
CORNER_R = 6.0
JAW_X0, JAW_X1 = 55.0, 95.0          # fixed jaw length (fingertip at x = 95)
JAW_Y0, JAW_Y1 = -14.0, -6.0         # jaw face at y = -6
JAW_T = 8.0                          # moving-jaw thickness (must match the jaw job's T)
JAW_TOP = T + link_back_z(SERVO) + JAW_T   # = top of the moving jaw (25.4)
CLR, END_CLR = 0.4, 0.2              # SG90 window side / end clearance (printed)
BED_CHAMFER = 0.4


def design():
    base = rounded_plate(X0, X1, Y0, Y1, T, r=CORNER_R)
    base = chamfer_plane_edges(base, 0.0, BED_CHAMFER)
    base += Pos(JAW_X0, JAW_Y0, T - 0.01) * Box(JAW_X1 - JAW_X0, JAW_Y1 - JAW_Y0, JAW_TOP - T + 0.01,
                                                 align=(Align.MIN,) * 3)
    base -= horn_pocket_cutter(SERVO, link_t=T, hole_comp=HOLE_COMP)            # wrist horn, back face
    base -= Pos(GRIP_X, 0, T) * servo_mount_cutter(SERVO, T, clearance=CLR, end_clearance=END_CLR,
                                                   through=T * 2 + 2, hole_comp=HOLE_COMP)
    return base


def build():
    return to_bed(design())

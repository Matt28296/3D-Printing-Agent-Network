"""Forearm (elbow -> wrist, 90 mm): flat 5 mm plate, printed flat, back face on the bed.

Design frame F: origin on the elbow axis at the forearm's back face, +z away from the elbow
servo, +x along the forearm to the wrist. The elbow MG996R's double-arm horn sits in a 2 mm
slot pocket on the back face; the wrist SG90 hangs through a window at x = 90 (tabs on the
front face z = 5, shaft +z).
"""
from build123d import Pos
from cadlib import chamfer_bottom, to_bed
from hobby_parts import MG996R, SG90, horn_pocket_cutter, rounded_plate, servo_mount_cutter, slot_cutter

# --- parameters (mm) -----------------------------------------------------------
HORN_SERVO, WRIST = MG996R, SG90   # nominal; measure yours (spec §3)
L = 90.0                # elbow axis -> wrist axis
T = 5.0
HALF_W = 13.0
X0, X1 = -25.0, 104.0   # 4 mm past the horn-slot tip; 3 mm past the wrist tab end (100.75)
CORNER_R = 7.0
LIGHT = (22.0, 62.0, 12.0)   # clear of the wrist tabs (x >= 68.5)
CLR = 0.4


def design():
    arm = rounded_plate(X0, X1, -HALF_W, HALF_W, T, r=CORNER_R)
    arm -= horn_pocket_cutter(HORN_SERVO, link_t=T)
    arm -= Pos(L, 0, T) * servo_mount_cutter(WRIST, T, clearance=CLR, through=T * 2 + 2)
    x0, x1, w = LIGHT
    arm -= slot_cutter(x0, x1, 0.0, w, T)
    return arm


def build():
    return to_bed(chamfer_bottom(design(), 0.4))

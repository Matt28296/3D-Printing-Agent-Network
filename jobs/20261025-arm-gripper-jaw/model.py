"""Moving jaw: lever on the gripper SG90 horn. Printed flat, back face on the bed.

Design frame J: origin on the gripper servo axis at the jaw's back face (= gripper-base frame
(40, 0, 17.4)), +z away from the servo, +x towards the fingertip. Drawn CLOSED: the jaw face
(y = -6, x 15-55) touches the fixed jaw. Opening turns it about +z (towards +y); 30° opens the
fingertips about 27 mm. An M2 centre screw + washer clamps jaw and horn onto the spline.
Fingertip force ≈ 160 N·mm / 55 mm ≈ 2.9 N at stall (10.7 N near the jaw root): light objects only.
"""
from build123d import Align, Cylinder
from cadlib import HOLE_COMP_DEFAULT, to_bed
from hobby_parts import SG90, chamfer_plane_edges, horn_pocket_cutter, rounded_plate

# --- parameters (mm) -----------------------------------------------------------
SERVO = SG90
HOLE_COMP = HOLE_COMP_DEFAULT   # +0.2 on hole diameters (default, fdm-design-rules)
T = 8.0                 # strength round 1: 5 -> 8
HUB_R = 8.0
BAR_X1 = 55.0           # fingertip (gripper-base x = 95)
BAR_Y0, BAR_Y1 = -6.0, 8.0   # jaw face at y = -6; 14 mm wide bar (strength round 1)
BED_CHAMFER = 0.3


def design():
    jaw = Cylinder(HUB_R, T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    jaw += rounded_plate(-4.0, BAR_X1, BAR_Y0, BAR_Y1, T, r=3.0)
    jaw = chamfer_plane_edges(jaw, 0.0, BED_CHAMFER)   # outline first: the pocket's short edges defeat the chamfer
    jaw -= horn_pocket_cutter(SERVO, link_t=T, hole_comp=HOLE_COMP)
    return jaw


def build():
    return to_bed(design())

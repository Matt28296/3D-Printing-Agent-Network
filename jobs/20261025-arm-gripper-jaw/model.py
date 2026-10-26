"""Moving jaw: lever on the gripper SG90 horn. Printed flat, back face on the bed.

Design frame J: origin on the gripper servo axis at the jaw's back face (= gripper-base frame
(40, 0, 14.4)), +z away from the servo, +x towards the fingertip. Drawn CLOSED: the jaw face
(y = -6, x 15-55) touches the fixed jaw. Opening turns it about +z (towards +y); 30° opens the
fingertips about 27 mm. Fingertip force ≈ 160 N·mm / 55 mm ≈ 2.9 N at stall: light objects only.
"""
from build123d import Align, Cylinder
from cadlib import chamfer_bottom, to_bed
from hobby_parts import SG90, horn_pocket_cutter, rounded_plate

# --- parameters (mm) -----------------------------------------------------------
SERVO = SG90
T = 5.0
HUB_R = 8.0
BAR_X1 = 55.0           # fingertip (gripper-base x = 95)
BAR_Y0, BAR_Y1 = -6.0, 5.5   # jaw face at y = -6; +5.5 leaves >= 1.6 mm wall beside the horn-arm slot (hub r 3.85)


def design():
    jaw = Cylinder(HUB_R, T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    jaw += rounded_plate(-4.0, BAR_X1, BAR_Y0, BAR_Y1, T, r=3.0)
    jaw = chamfer_bottom(jaw, 0.3)   # outline first: the pocket's short edges defeat the chamfer
    jaw -= horn_pocket_cutter(SERVO, link_t=T)
    return jaw


def build():
    return to_bed(design())

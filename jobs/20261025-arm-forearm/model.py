"""Forearm (elbow -> wrist, 90 mm): flat 10 mm plate, printed flat, FRONT face on the bed
(so the horn pocket opens upward and needs no bridge).

Design frame F: origin on the elbow axis at the forearm's back face, +z away from the elbow
servo, +x along the forearm to the wrist. The elbow MG996R's double-arm horn sits in a 2 mm
slot pocket on the back face, clamped by an M3 × 14 centre screw + Ø9 washer from the front
face (8 mm floor: 4.6 mm into the spline). The wrist MG90S hangs through a window at x = 90
(tabs on the front face z = T, shaft +z).

Round 3 (deep review 01 B1, B2, S1): the wrist servo is the real MG90S (22.8 × 12.2 body, spline
top 14.0 above the tabs; was the SG90's 22.5 × 12.0 / 10.8). Its window has a lead notch at the
shaft end and that end's tab pilot moved 1.3 mm out (lead="notch_shift_pilot"): file that tab's
slit to 2.1 mm so the screw reaches it.
"""
from build123d import Pos, Rot
from cadlib import HOLE_COMP_DEFAULT, to_bed
from hobby_parts import MG90S, MG996R, chamfer_plane_edges, horn_pocket_cutter, rounded_plate, servo_mount_cutter

# --- parameters (mm) -----------------------------------------------------------
HORN_SERVO, WRIST = MG996R, MG90S  # nominal; measure yours (spec §3)
HOLE_COMP = HOLE_COMP_DEFAULT      # +0.2 on hole diameters (default, fdm-design-rules)
L = 90.0                # elbow axis -> wrist axis
T = 10.0                # strength round 1: 5 -> 10, no lightening slot
HALF_W = 13.0
X0, X1 = -25.0, 104.0   # 4.4 mm past the horn-slot tip; 3.4 mm past the wrist tab end (100.6) and 3.0 mm
                        # past the moved lead-end pilot slot (100.95)
CORNER_R = 7.0
CLR = 0.4               # MG90S window side clearance (printed)
END_CLR = 0.2           # MG90S window end clearance (printed): 1.65 mm printed wall to the far-end pilot
BED_CHAMFER = 0.4


def design():
    arm = rounded_plate(X0, X1, -HALF_W, HALF_W, T, r=CORNER_R)
    arm = chamfer_plane_edges(arm, T, BED_CHAMFER)
    arm -= horn_pocket_cutter(HORN_SERVO, link_t=T, hole_comp=HOLE_COMP)
    arm -= Pos(L, 0, T) * servo_mount_cutter(WRIST, T, clearance=CLR, end_clearance=END_CLR,
                                             through=T * 2 + 2, hole_comp=HOLE_COMP, lead="notch_shift_pilot")
    return arm


def build():
    return to_bed(Rot(180, 0, 0) * design())

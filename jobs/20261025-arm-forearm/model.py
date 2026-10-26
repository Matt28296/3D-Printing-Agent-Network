"""Forearm (elbow -> wrist, 90 mm): flat 10 mm plate, printed flat, FRONT face on the bed
(so the horn pocket and the back-face ribs open upward and need no support).

Design frame F: origin on the elbow axis at the forearm's back face, +z away from the elbow
servo, +x along the forearm to the wrist. The elbow MG996R's double-arm horn sits in a 2 mm
slot pocket on the back face, clamped by an M3 × 14 centre screw + Ø9 washer from the front
face (8 mm floor: 4.6 mm into the spline). The wrist MG90S hangs through a window at x = 90
(tabs on the front face z = T, shaft +z).

Round 3 (deep review 01 B1, B2, S1): the wrist servo is the real MG90S (22.8 × 12.2 body, spline
top 14.0 above the tabs; was the SG90's 22.5 × 12.0 / 10.8). Its window has a lead notch at the
shaft end and that end's tab pilot moved 1.3 mm out (lead="notch_shift_pilot"): file that tab's
slit to 2.1 mm so the screw reaches it. The strips beside the two tab pilots (1.34 / 1.45 mm CAD)
stay: the user's decision of 26 Oct 2026, with the first-print screw-strip check in spec §8.

Round 5 (links strength round 4: window rails SF 1.71, far tab screw pull-out 2.40):
- each 6.6 mm window rail gets a 6 mm rib on the back face, from 5 mm before the window to 5 mm
  past it, so the rails are 6.6 × 16 (the MG90S case already stands 8.5 mm out of the back face);
- a cross-rib joins the two ribs at the window's far end and carries the far pilot 16 mm deep, for
  an M2 × 16 with 13.5 mm engaged (the lead-end screw stays M2 × 12: its lead leaves the case end
  between the ribs, 3.4 mm below the back face);
- the cross-rib and ribs run out at 45° towards the elbow.
"""
from build123d import Align, Box, BuildPart, BuildSketch, Plane, Polygon, Pos, Rot, extrude
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
# MG90S window and far pilot as servo_mount_cutter cuts them (CAD): window x 72.9 .. 96.1, y +-6.4
WIN_HW = (WRIST.width + CLR + HOLE_COMP) / 2                                      # 6.4
WIN_X0 = L - (WRIST.length - WRIST.shaft_from_end) - (END_CLR + HOLE_COMP) / 2    # 72.9
WIN_X1 = L + WRIST.shaft_from_end + (END_CLR + HOLE_COMP) / 2                     # 96.1
FAR_PILOT_X = L - (WRIST.length - WRIST.shaft_from_end) + WRIST.length / 2 - WRIST.hole_dx / 2   # 70.6
# back-face ribs and far-pilot boss (links strength round 4 -> design round 5)
RIB_H = 6.0             # rails 6.6 x 10 -> 6.6 x 16: yaw-stall SF 1.71 -> 4.29 (4 mm gives 3.30)
RIB_PAST = 5.0          # ribs run >= 5 mm past each window end onto the full plate (strength)
RIB_X1 = WIN_X1 + RIB_PAST          # 101.1, where the r 7 corner still leaves the rib 5.3 wide
BOSS_X0 = FAR_PILOT_X - 0.4 - (WRIST.screw_pilot_d + HOLE_COMP) / 2 - 2.45   # 66.9: 2.45 wall beyond the far
                                    # pilot's outward slot (x 69.35); the cross-rib runs from here to the window
                                    # (x 72.9) across the full width: far pilot 10 + 6 = 16 deep (M2 x 16, 13.5
                                    # engaged: pull-out SF 2.40 -> 3.41; strength asks >= 14)
FAR_SCREW_L = 16.0      # M2 x 16 at the far tab (BUILD_GUIDE §1); the lead-end tab keeps its M2 x 12
TAPER = RIB_H           # 45° run-out of the cross-rib and ribs towards the elbow: back face at x 60.9


def back_ribs():
    """Rail ribs (x BOSS_X0 .. RIB_X1, |y| >= WIN_HW) and the cross-rib (x BOSS_X0 .. WIN_X0, full width) on the back
    face, z -RIB_H .. 0, inside the plate outline; the lead end between the ribs stays open."""
    with BuildPart() as g:
        with BuildSketch(Plane.XZ):                       # sketch (u, v) = (x, z)
            Polygon((BOSS_X0 - TAPER, 0.01), (BOSS_X0, -RIB_H), (RIB_X1, -RIB_H), (RIB_X1, 0.01), align=None)
        extrude(amount=HALF_W + 1, both=True)
    block = g.part & rounded_plate(X0, X1, -HALF_W, HALF_W, RIB_H + 0.02, r=CORNER_R, z0=-RIB_H - 0.01)
    return block - Pos(WIN_X0, -WIN_HW, -RIB_H - 1) * Box(RIB_X1 - WIN_X0 + 1, 2 * WIN_HW, RIB_H + 2,
                                                          align=(Align.MIN,) * 3)


def design():
    arm = rounded_plate(X0, X1, -HALF_W, HALF_W, T, r=CORNER_R)
    arm = chamfer_plane_edges(arm, T, BED_CHAMFER)
    arm += back_ribs()
    arm -= horn_pocket_cutter(HORN_SERVO, link_t=T, hole_comp=HOLE_COMP)
    arm -= Pos(L, 0, T) * servo_mount_cutter(WRIST, T + RIB_H, clearance=CLR, end_clearance=END_CLR,
                                             through=(T + RIB_H) * 2 + 2, hole_comp=HOLE_COMP,
                                             lead="notch_shift_pilot")
    return arm


def build():
    return to_bed(Rot(180, 0, 0) * design())

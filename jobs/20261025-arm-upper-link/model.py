"""Upper link (shoulder -> elbow, 100 mm): flat 10 mm plate, printed flat, FRONT face on the bed
(so the horn pocket and the back-face ribs open upward and need no support).

Design frame U (see assembly_plan.md): origin on the shoulder axis at the link's back face
(servo side), +z away from the shoulder servo (= world +Y), +x along the link to the elbow.
The shoulder MG996R's double-arm horn sits in a 2 mm slot pocket on the back face; an M3 centre
screw + washer from the front face clamps link and horn onto the spline. The elbow MG996R hangs
through a window at x = 100, tabs on the front face (z = T), shaft +z.
In-plane (gravity) bending runs about the 34 mm-deep section; sideways loads (yaw stall, a hand
push) bend the 10 mm thickness, which is why there is no lightening slot (strength round 1).
Round 3 (deep review 01 B1): the elbow window has a lead notch (4.4 × 2.0 mm printed) at each
case end, so the lead root passes when the servo goes in case bottom first from the front.
Round 5 (links strength round 4, SF 1.49): each 6.85 mm window rail gets a 6 mm rib on the back
face, so the rails are 6.85 × 16 from 5 mm before the window to past the near tab row. The ribs
continue the window's side walls (the elbow servo's case already stands 17 mm out of the back
face there) and run out at 45° towards the shoulder.
"""
from build123d import Align, Box, BuildPart, BuildSketch, Plane, Polygon, Pos, Rot, extrude
from cadlib import HOLE_COMP_DEFAULT, to_bed
from hobby_parts import MG996R, chamfer_plane_edges, horn_pocket_cutter, rounded_plate, servo_mount_cutter

# --- parameters (mm) -----------------------------------------------------------
SERVO = MG996R          # shoulder horn and elbow servo; nominal, measure yours (spec §3)
HOLE_COMP = HOLE_COMP_DEFAULT   # +0.2 on hole diameters (default, fdm-design-rules)
L = 100.0               # shoulder axis -> elbow axis
T = 10.0                # plate thickness (strength round 1: 6 -> 10)
HALF_W = 17.0           # half width
X0, X1 = -25.0, 121.0   # plate ends: 4.4 mm past the horn-slot tip, 4 mm past the elbow tab pilot
CORNER_R = 8.0
CLR = 0.4               # servo window clearance (printed)
BED_CHAMFER = 0.4
# elbow window as servo_mount_cutter cuts it (CAD): x 69.2 .. 110.5, y +-10.15
WIN_HW = (SERVO.width + CLR + HOLE_COMP) / 2                                  # 10.15
WIN_X0 = L - (SERVO.length - SERVO.shaft_from_end) - (CLR + HOLE_COMP) / 2    # 69.2
WIN_X1 = L + SERVO.shaft_from_end + (CLR + HOLE_COMP) / 2                     # 110.5
# back-face rail ribs (links strength round 4 -> design round 5: rails 6.85 x 10 SF 1.49; 6.85 x 16 SF 3.82 yaw, 4.84 hand)
RIB_H = 6.0             # rib depth below the back face (strength: 4 mm gives only 2.93)
RIB_PAST = 5.0          # full depth from >= 5 mm before the window's far end (strength: onto the full plate)
RIB_X0 = WIN_X0 - RIB_PAST     # 64.2: full depth from here ...
RIB_TAPER = RIB_H              # ... with a 45° run-out to the back face at x 58.2 (no step on the loaded plate)
RIB_X1 = 117.0          # elbow end: 6.5 mm past the window, 2.9 mm past the near pilot row (x 114.1), where the
                        # plate's r 8 corner still leaves the rib 5.8 wide (it would thin to a sliver at x 121)


def rail_ribs():
    """Ribs on both window rails, z -RIB_H .. 0 (back face), inside the plate outline, clear of the window."""
    with BuildPart() as g:
        with BuildSketch(Plane.XZ):                       # sketch (u, v) = (x, z)
            Polygon((RIB_X0 - RIB_TAPER, 0.01), (RIB_X0, -RIB_H), (RIB_X1, -RIB_H), (RIB_X1, 0.01), align=None)
        extrude(amount=HALF_W + 1, both=True)
    ribs = g.part & rounded_plate(X0, X1, -HALF_W, HALF_W, RIB_H + 0.02, r=CORNER_R, z0=-RIB_H - 0.01)
    return ribs - Pos(RIB_X0 - RIB_TAPER - 1, -WIN_HW, -RIB_H - 1) * Box(
        RIB_X1 - RIB_X0 + RIB_TAPER + 2, 2 * WIN_HW, RIB_H + 2, align=(Align.MIN,) * 3)


def design():
    link = rounded_plate(X0, X1, -HALF_W, HALF_W, T, r=CORNER_R)
    link = chamfer_plane_edges(link, T, BED_CHAMFER)                     # front face goes on the bed
    link += rail_ribs()
    link -= horn_pocket_cutter(SERVO, link_t=T, hole_comp=HOLE_COMP)    # shoulder horn, back face
    link -= Pos(L, 0, T) * servo_mount_cutter(SERVO, T + RIB_H, clearance=CLR, through=(T + RIB_H) * 2 + 2,
                                              hole_comp=HOLE_COMP,
                                              lead="notch")       # lead notch at both case ends (review 01 B1)
    return link


def build():
    return to_bed(Rot(180, 0, 0) * design())

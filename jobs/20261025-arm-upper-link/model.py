"""Upper link (shoulder -> elbow, 100 mm): flat 10 mm plate, printed flat, FRONT face on the bed
(so the horn pocket opens upward and needs no bridge).

Design frame U (see assembly_plan.md): origin on the shoulder axis at the link's back face
(servo side), +z away from the shoulder servo (= world +Y), +x along the link to the elbow.
The shoulder MG996R's double-arm horn sits in a 2 mm slot pocket on the back face; an M3 centre
screw + washer from the front face clamps link and horn onto the spline. The elbow MG996R hangs
through a window at x = 100, tabs on the front face (z = T), shaft +z.
In-plane (gravity) bending runs about the 34 mm-deep section; sideways loads (yaw stall, a hand
push) bend the 10 mm thickness, which is why there is no lightening slot (strength round 1).
"""
from build123d import Pos, Rot
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


def design():
    link = rounded_plate(X0, X1, -HALF_W, HALF_W, T, r=CORNER_R)
    link = chamfer_plane_edges(link, T, BED_CHAMFER)                     # front face goes on the bed
    link -= horn_pocket_cutter(SERVO, link_t=T, hole_comp=HOLE_COMP)    # shoulder horn, back face
    link -= Pos(L, 0, T) * servo_mount_cutter(SERVO, T, clearance=CLR, through=T * 2 + 2, hole_comp=HOLE_COMP)
    return link


def build():
    return to_bed(Rot(180, 0, 0) * design())

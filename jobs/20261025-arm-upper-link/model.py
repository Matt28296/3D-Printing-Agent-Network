"""Upper link (shoulder -> elbow, 100 mm): flat 6 mm plate, printed flat, back face on the bed.

Design frame U (see assembly_plan.md): origin on the shoulder axis at the link's back face
(servo side), +z away from the shoulder servo (= world +Y), +x along the link to the elbow.
The shoulder MG996R's double-arm horn sits in a 2 mm slot pocket on the back face.
The elbow MG996R hangs through a window at x = 100, tabs on the front face (z = 6), shaft +z.
Gravity bends the link in its own plane, about the 34 mm-deep section, which is its strong axis.
"""
from build123d import Pos
from cadlib import chamfer_bottom, to_bed
from hobby_parts import MG996R, horn_pocket_cutter, rounded_plate, servo_mount_cutter, slot_cutter

# --- parameters (mm) -----------------------------------------------------------
SERVO = MG996R          # shoulder horn and elbow servo; nominal, measure yours (spec §3)
L = 100.0               # shoulder axis -> elbow axis
T = 6.0                 # plate thickness: 4 mm left above the 2 mm horn pocket
HALF_W = 17.0           # half width
X0, X1 = -25.0, 121.0   # plate ends: 4 mm past the horn-slot tip and the elbow tab pilot
CORNER_R = 8.0
LIGHT = (26.0, 56.0, 14.0)   # lightening slot x0, x1, width (clear of the elbow tabs, x >= 62.9)
CLR = 0.4


def design():
    link = rounded_plate(X0, X1, -HALF_W, HALF_W, T, r=CORNER_R)
    link -= horn_pocket_cutter(SERVO, link_t=T)                       # shoulder horn, back face
    link -= Pos(L, 0, T) * servo_mount_cutter(SERVO, T, clearance=CLR, through=T * 2 + 2)   # elbow
    x0, x1, w = LIGHT
    link -= slot_cutter(x0, x1, 0.0, w, T)
    return link


def build():
    return to_bed(chamfer_bottom(design(), 0.4))

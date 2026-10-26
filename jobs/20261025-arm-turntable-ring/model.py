"""Turntable support ring: screws to the base top plate and catches the turntable when the
arm tips, so the base-yaw servo shaft isn't the only thing carrying the arm's moment. Round 3
(deep review 03 SYS-05): 0.4 mm running gap, PTFE tape on the top face, so it works as a
bearing under the arm's overturning moment instead of only after a knock.

Design frame = assembly frame; the ring sits on the base top plate (Z = 0).
Printed as modelled (tabs on the bed).
"""
import math

from build123d import Align, Box, Cylinder, Pos, Rot
from cadlib import HOLE_COMP_DEFAULT, chamfer_bottom, to_bed
from hobby_parts import MG996R, horn_face_z

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT  # +0.2 on hole diameters (default, fdm-design-rules)
R_IN, R_OUT = 41.0, 44.0      # inside the base-servo tabs (r <= 38.4); 0.75 mm clear of the tab-screw heads
TURNTABLE_Z = horn_face_z(MG996R)   # 16.5: turntable underside (the base horn sits flat on it, no pocket)
RUN_GAP = 0.4                 # running gap to the turntable (deep review 03 SYS-05: 1.5 -> 0.4, so the ring
                              # catches the disk after 0.5° of tilt instead of 1.95°); PTFE tape on the ring
                              # top (≈0.1 mm) leaves ≈0.3; sand to an even gap if it rubs
H = TURNTABLE_Z - RUN_GAP     # 16.1
TAB_R, TAB_ANG = 47.5, (30.0, 150.0, 270.0)   # must match the base's ring pilots
TAB_D, TAB_T, TAB_HOLE = 9.0, 3.0, 3.4        # tab Ø9 reaches r 52.0 = base edge; M3 clearance (printed)


def design():
    ring = Cylinder(R_OUT, H, align=(Align.CENTER, Align.CENTER, Align.MIN)) - \
        Pos(0, 0, -1) * Cylinder(R_IN, H + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for a in TAB_ANG:
        x, y = TAB_R * math.cos(math.radians(a)), TAB_R * math.sin(math.radians(a))
        # tab: a disc at the screw plus a web back to the ring
        ring += Pos(x, y, 0) * Cylinder(TAB_D / 2, TAB_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
        xm, ym = (R_IN + 1) * math.cos(math.radians(a)), (R_IN + 1) * math.sin(math.radians(a))
        web_len = TAB_R - R_IN - 1
        ring += Pos((x + xm) / 2, (y + ym) / 2, 0) * Rot(0, 0, a) * Box(web_len, TAB_D, TAB_T,
                                                                       align=(Align.CENTER, Align.CENTER, Align.MIN))
        ring -= Pos(x, y, -1) * Cylinder((TAB_HOLE + HOLE_COMP) / 2, TAB_T + 2,
                                         align=(Align.CENTER, Align.CENTER, Align.MIN))
    return ring


def build():
    return to_bed(chamfer_bottom(design(), 0.4))

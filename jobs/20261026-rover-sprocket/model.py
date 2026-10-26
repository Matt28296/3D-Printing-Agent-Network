"""Drive sprocket (×2): 10 teeth, D-bore on the N20 shaft, grub screw. Identical both sides.

Sprocket frame: axis = +Z pointing AWAY from the chassis, origin on the axis at the track
centre plane (world Y = ±55). The toothed disc spans z ±3.5; the hub runs back towards the
chassis to z = -16.5 (0.5 mm off the wall). The N20 shaft (world Y 35.8-45) sits in a 6.5 mm
D-bore at the hub end. Teeth sit at k·36° (mid-way between pins when pins sit at 18° + k·36°).
Printed outer disc face down, hub up.
"""
import math
import sys
from pathlib import Path

from build123d import Align, BuildPart, BuildSketch, Cylinder, Plane, Polygon, Pos, Rot, extrude
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-rover-assembly"))
from rover_frame import CHORD_IN, HALF_W_OUT, HUB_GAP, LINK_T, MOTOR, MOTOR_FACE_Y, N_TEETH, Y_T  # noqa: E402

from hobby_parts import d_shaft_bore_cutter  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT
DISC_HALF = 3.5                       # tooth/disc half width (link notch is ±4)
DISC_R = CHORD_IN - 0.5               # 11.9: under the links' inner faces
TOOTH_TIP_R = CHORD_IN + LINK_T - 0.5 # 17.9: stays inside the link (outer face 18.4)
TOOTH_BASE_W, TOOTH_TIP_W = 2.7, 1.6  # tangential width (gap between knuckles is ~3.9); assembly check round 1
PHASE_DEG = 0.0
HUB_D = 11.0
HUB_Z0 = -(Y_T - (HALF_W_OUT + HUB_GAP))        # -16.5: wall-side end of the hub
SHAFT_END_Z = (MOTOR_FACE_Y + MOTOR.shaft_len) - Y_T   # -10: where the shaft ends
BORE_DEPTH = SHAFT_END_Z - HUB_Z0 + 0.5         # 7.0 (shaft engages 6.5)
GRUB_PILOT = 1.6                      # M2 set screw / self-tapper, printed
BORE = "D"                            # "D" = motor shaft, "round" = idler on an M3 bolt
ROUND_BORE = 3.2                      # printed running bore for the idler bolt


def tooth():
    r0, r1 = DISC_R - 0.5, TOOTH_TIP_R
    pts = [(r0, -TOOTH_BASE_W / 2), (r1, -TOOTH_TIP_W / 2), (r1, TOOTH_TIP_W / 2), (r0, TOOTH_BASE_W / 2)]
    with BuildPart() as bp:
        with BuildSketch(Plane.XY.offset(-DISC_HALF)):
            Polygon(*pts, align=None)
        extrude(amount=2 * DISC_HALF)
    return bp.part


def design():
    s = Pos(0, 0, -DISC_HALF) * Cylinder(DISC_R, 2 * DISC_HALF, align=(Align.CENTER, Align.CENTER, Align.MIN))
    t = tooth()
    for k in range(N_TEETH):
        s += Rot(0, 0, PHASE_DEG + k * 360.0 / N_TEETH) * t
    s += Pos(0, 0, HUB_Z0) * Cylinder(HUB_D / 2, -DISC_HALF - HUB_Z0 + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
    if BORE == "D":
        s -= Pos(0, 0, HUB_Z0 - 0.01) * d_shaft_bore_cutter(MOTOR, BORE_DEPTH, hole_comp=HOLE_COMP)
        zg = HUB_Z0 + (SHAFT_END_Z - HUB_Z0) / 2
        s -= Pos(0, 0, zg) * Rot(-90, 0, 0) * Cylinder((GRUB_PILOT + HOLE_COMP) / 2, HUB_D,
                                                     align=(Align.CENTER, Align.CENTER, Align.MIN))
    else:
        s -= Pos(0, 0, HUB_Z0 - 1) * Cylinder((ROUND_BORE + HOLE_COMP) / 2, 40, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return s


def build():
    return to_bed(Rot(180, 0, 0) * design())    # outer disc face on the bed, hub up

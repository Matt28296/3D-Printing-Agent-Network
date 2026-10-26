"""Drive sprocket (×2): 10 teeth, Ø10 journal hub with a D-bore on the N20 shaft, grub screw.
Identical both sides.

Sprocket frame: axis = +Z pointing AWAY from the chassis, origin on the axis at the track centre
plane (world Y = ±55). The toothed disc spans z ±3.5. The hub (Ø10) runs back through the 6 mm
journal in the chassis wall to 0.5 mm from the N20 gearbox face: the wall carries the track
loads, the N20 shaft only the torque (strength round 1). The D-bore takes 9 mm of the shaft.
Teeth sit at k·36° (mid-way between pins when pins sit at 18° + k·36°), with 45° root chamfers.
Printed outer disc face down, hub up.
"""
import sys
from pathlib import Path

from build123d import Align, Box, BuildPart, BuildSketch, Cylinder, Plane, Polygon, Pos, Rot, extrude
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-rover-assembly"))
from rover_frame import (CHORD_IN, HALF_W_OUT, HUB_D, HUB_GAP, LINK_T, MOTOR, MOTOR_FACE_Y, N_TEETH,  # noqa: E402
                         Y_T)

from hobby_parts import chamfer_plane_edges, d_shaft_bore_cutter  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT
DISC_HALF = 3.5                       # tooth/disc half width (link notch is ±4)
DISC_R = CHORD_IN - 0.5               # 11.9: under the links' inner faces
TOOTH_TIP_R = CHORD_IN + LINK_T - 0.5 # 17.9: stays inside the link (outer face 18.4)
TOOTH_BASE_W, TOOTH_TIP_W = 2.7, 1.6  # tangential width (gap between knuckles is ~3.9); assembly check round 1
ROOT_CHAMFER = 0.5                    # 45° chamfer at each tooth root (DFM/strength round 1)
PHASE_DEG = 0.0
HUB_Z0_D = (MOTOR_FACE_Y + 0.5) - Y_T          # -23: hub end, 0.5 mm off the gearbox face (sprocket)
HUB_Z0_ROUND = -(Y_T - (HALF_W_OUT + HUB_GAP))  # -16.5: hub end at the washer outside the wall (idler)
SHAFT_END_Z = (MOTOR_FACE_Y + MOTOR.shaft_len) - Y_T   # -13.5: where the shaft ends
D_CLEARANCE = 0.0                     # D-bore press fit (prints ~Ø3.0 / flat 2.5 with HOLE_COMP)
GRUB_PILOT = 1.6                      # M2 set screw, printed pilot
GRUB_Y = 40.5                         # grub screw position (world Y): 2.5 mm outside the wall, on the shaft
BORE = "D"                            # "D" = motor shaft, "round" = idler on an M3 bolt
ROUND_BORE = 3.5                      # printed running bore for the idler bolt (0.5 mm running clearance)
BED_CHAMFER = 0.3


def tooth():
    r0, r1, f = DISC_R - 0.5, TOOTH_TIP_R, ROOT_CHAMFER
    b, t = TOOTH_BASE_W / 2, TOOTH_TIP_W / 2
    pts = [(r0, -b - f), (DISC_R, -b - f), (DISC_R + f, -b), (r1, -t), (r1, t), (DISC_R + f, b), (DISC_R, b + f), (r0, b + f)]
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
    s = chamfer_plane_edges(s, DISC_HALF, BED_CHAMFER)          # outer face goes on the bed
    hub_z0 = HUB_Z0_D if BORE == "D" else HUB_Z0_ROUND
    s += Pos(0, 0, hub_z0) * Cylinder(HUB_D / 2, -DISC_HALF - hub_z0 + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
    if BORE == "D":
        depth = SHAFT_END_Z - hub_z0 + 0.5
        s -= Pos(0, 0, hub_z0 - 0.01) * d_shaft_bore_cutter(MOTOR, depth, clearance=D_CLEARANCE, hole_comp=HOLE_COMP)
        zg = GRUB_Y - Y_T
        d = GRUB_PILOT + HOLE_COMP
        hole = Pos(0, 0, zg) * Rot(0, 90, 0) * Cylinder(d / 2, HUB_D, align=(Align.CENTER, Align.CENTER, Align.MIN))
        # teardrop point towards -z (up in print, the part is printed flipped)
        hole += Pos(HUB_D / 4, 0, zg - d / 2 / 2 ** 0.5) * Rot(45, 0, 0) * Box(HUB_D / 2, d / 2, d / 2)   # square about the hole axis (X)
        s -= hole
    else:
        s -= Pos(0, 0, hub_z0 - 1) * Cylinder((ROUND_BORE + HOLE_COMP) / 2, 40, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return s


def build():
    return to_bed(Rot(180, 0, 0) * design())    # outer disc face on the bed, hub up

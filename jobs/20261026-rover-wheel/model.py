"""Road wheel (×4, 2 per side): carries the rover on the bottom track run, with 45° V-flanges
that keep the track centred. Free on an M3 × 50 bolt (class 12.9, fully threaded) held in the
chassis wall's nut trap.

Wheel frame: axis = +Z away from the chassis, origin on the axis at the track centre plane.
The rim (r 13.1) meets the links' inner faces on the straight bottom run (13.18 below the axle).
Printed axis vertical, outer flange face on the bed: one cone faces up, the other is a 45° overhang.
Round 3: a 0.4 × 45° chamfer on every bed edge after the flip (outer flange edge and bore mouth;
DFM round 2 fix 1), plus elefant_foot_compensation 0.2 in print_requirements.json.
"""
import sys
from pathlib import Path

from build123d import Align, BuildPart, BuildSketch, Cylinder, Plane, Polygon, Pos, Rot, revolve, Axis
from cadlib import HOLE_COMP_DEFAULT, chamfer_bottom, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-rover-assembly"))
from rover_frame import HALF_W_OUT, HUB_GAP, STRAIGHT_IN, TRACK_W, Y_T  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT
RIM_R = STRAIGHT_IN - 0.08            # 13.1
RIM_HALF = TRACK_W / 2 + 0.3          # 12.3: 0.3 mm side clearance to the track edge
CONE_RISE = 3.0                       # 45° V-flange: r +3 over 3 mm
FLANGE_FLAT = 0.7
BORE = 3.5                            # printed running bore on the M3 bolt, 0.5 mm running clearance (DFM round 1)
HUB_R = 5.0                           # inner-side hub to the washer/nut
INNER_FACE_Z = -(Y_T - (HALF_W_OUT + HUB_GAP))   # -16.5: 0.5 mm off the wall (washer)
BED_CHAMFER = 0.4                     # 45° chamfer on the bed edges (DFM round 2 fix 1)


def design():
    h = RIM_HALF + CONE_RISE + FLANGE_FLAT       # 16.0
    r1 = RIM_R + CONE_RISE
    pts = [(0, -h), (r1, -h), (r1, -RIM_HALF - CONE_RISE), (RIM_R, -RIM_HALF), (RIM_R, RIM_HALF),
           (r1, RIM_HALF + CONE_RISE), (r1, h), (0, h)]
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ):
            Polygon(*pts, align=None)
        revolve(axis=Axis.Z)
    w = bp.part
    if INNER_FACE_Z < -h:
        w += Pos(0, 0, INNER_FACE_Z) * Cylinder(HUB_R, -h - INNER_FACE_Z + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
    w -= Pos(0, 0, INNER_FACE_Z - 1) * Cylinder((BORE + HOLE_COMP) / 2, 2 * h + 4, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return w


def build():
    return chamfer_bottom(to_bed(Rot(180, 0, 0) * design()), BED_CHAMFER)   # outer flange face on the bed, hub up

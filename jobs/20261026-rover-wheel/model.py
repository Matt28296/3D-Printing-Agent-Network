"""Road wheel (×4, 2 per side): carries the rover on the bottom track run, with 45° V-flanges
that keep the track centred. Free on an M3 bolt held in the chassis wall's nut trap.

Wheel frame: axis = +Z away from the chassis, origin on the axis at the track centre plane.
The rim (r 13.1) meets the links' inner faces on the straight bottom run (13.18 below the axle).
Printed axis vertical, outer flange face on the bed: one cone faces up, the other is a 45° overhang.
"""
import sys
from pathlib import Path

from build123d import Align, BuildPart, BuildSketch, Cylinder, Plane, Polygon, Pos, Rot, revolve, Axis
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-rover-assembly"))
from rover_frame import HALF_W_OUT, HUB_GAP, STRAIGHT_IN, TRACK_W, Y_T  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT
RIM_R = STRAIGHT_IN - 0.08            # 13.1
RIM_HALF = TRACK_W / 2 + 0.3          # 12.3: 0.3 mm side clearance to the track edge
CONE_RISE = 3.0                       # 45° V-flange: r +3 over 3 mm
FLANGE_FLAT = 0.7
BORE = 3.2                            # printed running bore on the M3 bolt
HUB_R = 5.0                           # inner-side hub to the washer/nut
INNER_FACE_Z = -(Y_T - (HALF_W_OUT + HUB_GAP))   # -16.5: 0.5 mm off the wall (washer)


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
    return to_bed(Rot(180, 0, 0) * design())    # outer flange face on the bed, hub up

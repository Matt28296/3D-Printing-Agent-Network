"""Hexapod tibia (×6): flat plate from the tibia MG90S horn to the foot tip.

Design frame T: origin on the knee axis at the tibia's back face (the tibia horn sits 2 mm deep
in a pocket there), x along the tibia to the foot tip at x = L_T. Tapers from the hub to a
rounded foot. In stance the foot load runs along the tibia (compression) with bending in the
plate's own plane. Printed flat, horn pocket on the bed (bridge < 8 mm).
"""
import sys
from pathlib import Path

from build123d import BuildPart, BuildSketch, Circle, Locations, Plane, Polygon, extrude
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-hexapod-assembly"))
from hex_frame import L_T, SERVO, T_T  # noqa: E402

from hobby_parts import chamfer_plane_edges, horn_pocket_cutter  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT
HUB_R = 9.0
FOOT_R = 4.5                     # rounded foot tip (a TPU sock or rubber tip can go over it)
BED_CHAMFER = 0.4


def design():
    xf = L_T - FOOT_R
    with BuildPart() as bp:
        with BuildSketch(Plane.XY):
            Circle(HUB_R)
            Polygon((0, HUB_R), (xf, FOOT_R), (xf, -FOOT_R), (0, -HUB_R), align=None)
            with Locations((xf, 0)):
                Circle(FOOT_R)
        extrude(amount=T_T)
    t = bp.part
    t = chamfer_plane_edges(t, 0.0, BED_CHAMFER)
    t -= horn_pocket_cutter(SERVO, link_t=T_T, hole_comp=HOLE_COMP)
    return t


def build():
    return to_bed(design())

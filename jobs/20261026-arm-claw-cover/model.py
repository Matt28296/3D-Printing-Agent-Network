"""Claw cover: front plate + top wall + upper lip. It closes the two rack channels and carries
the finger slots. Printed standing on its -y end (the profile on the bed, every channel face a
vertical wall).

Design frame = claw frame G (../20261025-robot-arm-assembly/claw_frame.py). Rack A (upper)
runs between the lip (behind it), the top wall (above it), the front plate (in front of it) and
the pinion (below it). Rack B rides on the frame's wrist plate, between the frame's lower rail
and this front plate. Each jaw's neck passes through a slot in the front plate: slot A (upper)
is open at the -y end, slot B (lower) at the +y end, so the jaws slide in from the ends after
the cover is screwed on. A Ø5 hole in front of the pinion reaches its clamp screw.
"""
import sys
from pathlib import Path

from build123d import Align, Box, Pos, Rot
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261025-robot-arm-assembly"))
from claw_frame import (ACCESS_D, BULK_T, FRONT_SCREWS, HALF_Y, M3_CLEAR, NECK_Z, RAIL_IN, RAIL_X1,  # noqa: E402
                        SLOT_CLR, TOP_SCREWS, X_B, X_F0, X_F1, Z_TOP0, Z_TOP1, ZS)

from hobby_parts import _teardrop_z, chamfer_plane_edges  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT  # +0.2 on hole diameters (default, fdm-design-rules)
BED_CHAMFER = 0.3
TO_PRINT = Rot(90, 0, 0)       # G +y -> print +Z (the -y end goes on the bed)


def _box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN,) * 3)


def _hole_along(axis, d, center, length):
    """Round hole along G x or z with a 45° point towards +y (up in print)."""
    if axis == "z":   # _teardrop_z runs along +Z with its point towards +y
        return Pos(center[0], center[1], center[2] - length / 2) * _teardrop_z(d, length, "+y")
    # along x: turn the +Z cutter onto +X (Rot about y keeps +y)
    return Pos(center[0] - length / 2, center[1], center[2]) * Rot(0, 90, 0) * _teardrop_z(d, length, "+y")


def design():
    c = _box(X_B - BULK_T, X_F1, -HALF_Y, HALF_Y, Z_TOP0, Z_TOP1)                # top wall
    c += _box(X_F0, X_F1, -HALF_Y, HALF_Y, 0.0, Z_TOP0 + 0.01)                   # front plate
    c += _box(X_B, RAIL_X1, -HALF_Y, HALF_Y, ZS + RAIL_IN, Z_TOP0 + 0.01)         # upper lip
    # bed chamfer on the -y end (done in print orientation, then turned back)
    c = TO_PRINT.inverse() * chamfer_plane_edges(TO_PRINT * c, -HALF_Y, BED_CHAMFER)
    za0, za1 = ZS + NECK_Z[0] - SLOT_CLR, ZS + NECK_Z[1] + SLOT_CLR
    c -= _box(X_F0 - 1, X_F1 + 1, -HALF_Y - 1, SLOT_CLR, za0, za1)              # slot A, open at -y
    c -= _box(X_F0 - 1, X_F1 + 1, -SLOT_CLR, HALF_Y + 1, 2 * ZS - za1, 2 * ZS - za0)   # slot B, open at +y
    c -= _hole_along("x", ACCESS_D + HOLE_COMP, (X_F0 + 1.5, 0.0, ZS), 8.0)        # pinion clamp screw access
    d = M3_CLEAR + HOLE_COMP
    for (x, y) in TOP_SCREWS:
        c -= _hole_along("z", d, (x, y, (Z_TOP0 + Z_TOP1) / 2), Z_TOP1 - Z_TOP0 + 2)
    for (y, z) in FRONT_SCREWS:
        c -= _hole_along("x", d, ((X_F0 + X_F1) / 2, y, z), X_F1 - X_F0 + 2)
    return c


def build():
    return to_bed(TO_PRINT * design())

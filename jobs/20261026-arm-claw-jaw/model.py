"""Claw jaw (x2, identical): rack + neck + finger blade in one piece. Printed standing on the
rack's back face, so the rack teeth are drawn in the bed plane and the finger grows upwards.

Design frame = claw frame G (../20261025-robot-arm-assembly/claw_frame.py), drawn as JAW A in
the CLOSED pose: the rack above the pinion with its teeth pointing down (-z), the neck through
the cover's slot A, the finger on the -y side with its grip face on y = 0. Jaw B is the same
part turned 180° about the pinion axis (the claw x axis through y 0, z 22.5).
Grip face: 0.6 mm V-grooves across the finger (they bite when an object slides out along x)
and a 1.5 mm V-notch along the finger's centre line for pens, rods and wires.
"""
import sys
from pathlib import Path

from build123d import (Align, Box, BuildPart, BuildSketch, Location, Plane, Polygon, Pos, Rot,
                       extrude)
from cadlib import to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261025-robot-arm-assembly"))
from claw_frame import (BACKLASH, BLADE_T, FACE_W, GRIP_HALF, GRIP_X0, M, NECK_X1, NECK_Y,  # noqa: E402
                        NECK_Z, P_CIRC, R_P, RACK_BACK, RACK_Y, X_P1, X_TIP, ZS)

from gears import rack_bar  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
TIP_CHAMFER = 4.0          # 45° corners at the fingertip (x-z outline)
TIP_BEVEL = 3.5            # outer-face bevel at the fingertip (thin tip for small parts)
GROOVE_D, GROOVE_PITCH = 0.6, 2.0
GROOVE_X = (GRIP_X0 + 1.0, X_TIP - TIP_CHAMFER - 1.5)   # stop short of the tip chamfers (no slivers)
NOTCH_D = 1.5
GUSSET = NECK_Y - BLADE_T  # 8: outer-face flare from the neck into the blade, 45°
# rack frame in G: rack_bar's X (teeth row) along +y, its tooth direction (+Y) along -z,
# its extrusion (+Z) along -x; pitch line on z = ZS + R_P. A tooth GAP sits over the pinion
# axis (y 0) in the closed pose, facing the pinion's tooth 0.
RACK_LOC = Location(Plane(origin=(X_P1, 0, ZS + R_P), x_dir=(0, 1, 0), z_dir=(-1, 0, 0)))


def _box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN,) * 3)


def _prism_xz(pts, y0, y1):
    """Polygon in the x-z plane, extruded from y0 to y1."""
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ.offset(-y1)):        # Plane.XZ's normal is -y: the sketch sits on
            Polygon(*pts, align=None)                  # y = y1 and extrudes towards -y, down to y0
        extrude(amount=y1 - y0)
    return bp.part


def _prism_xy(pts, z0, z1):
    with BuildPart() as bp:
        with BuildSketch(Plane.XY.offset(z0)):
            Polygon(*pts, align=None)
        extrude(amount=z1 - z0)
    return bp.part


def _prism_yz(pts, x0, x1):
    with BuildPart() as bp:
        with BuildSketch(Plane.YZ.offset(x0)):
            Polygon(*pts, align=None)
        extrude(amount=x1 - x0)
    return bp.part


def blade_outline():
    """Finger silhouette in the x-z plane: grows 45° down from the neck to the full grip height."""
    z_n0, z_n1 = ZS + NECK_Z[0], ZS + NECK_Z[1]
    z_lo, z_hi = ZS - GRIP_HALF, ZS + GRIP_HALF
    x0 = NECK_X1 - 0.01
    return [(x0, z_n0), (x0 + (z_n0 - z_lo), z_lo), (X_TIP - TIP_CHAMFER, z_lo), (X_TIP, z_lo + TIP_CHAMFER),
            (X_TIP, z_hi - TIP_CHAMFER), (X_TIP - TIP_CHAMFER, z_hi), (x0 + (z_n1 - z_hi), z_hi), (x0, z_n1)]


def design():
    rack = RACK_LOC * rack_bar(M, RACK_Y[0], RACK_Y[1], FACE_W, RACK_BACK, backlash=BACKLASH,
                               phase=P_CIRC / 2)
    j = rack
    j += _box(X_P1 - 0.01, NECK_X1, -NECK_Y, 0.0, ZS + NECK_Z[0], ZS + NECK_Z[1])          # neck
    j += _prism_xz(blade_outline(), -BLADE_T, 0.0)                                        # finger blade
    flare = _prism_xy([(NECK_X1 - 0.01, -NECK_Y), (NECK_X1 + GUSSET + 1, -BLADE_T + 1),    # 45° flare, meets
                       (NECK_X1 - 0.01, -BLADE_T + 1)], ZS + NECK_Z[0], ZS + NECK_Z[1])      # the face at x+8,
    j += flare & _prism_xz(blade_outline(), -NECK_Y - 1, 0.0)                                 # inside the outline
    # grip face: V-grooves across the finger (along z) ...
    x = GROOVE_X[0]
    while x <= GROOVE_X[1]:
        j -= _prism_xy([(x - GROOVE_D, 0.01), (x, -GROOVE_D), (x + GROOVE_D, 0.01)],
                       ZS - GRIP_HALF - 1, ZS + GRIP_HALF + 1)
        x += GROOVE_PITCH
    # ... and a V-notch along it, on the claw's centre line
    j -= _prism_yz([(0.01, ZS - NOTCH_D), (-NOTCH_D, ZS), (0.01, ZS + NOTCH_D)], GRIP_X0 - 4, X_TIP + 1)
    # thin fingertip: bevel the outer face
    # (cut line from (X_TIP - 2*TIP_BEVEL, outer face) to (X_TIP, outer face + TIP_BEVEL), extended
    # past both ends so it leaves no skin on the face)
    j -= _prism_xy([(X_TIP - TIP_BEVEL * 2 - 2, -BLADE_T - 1), (X_TIP + 1, -BLADE_T - 1),
                    (X_TIP + 1, -BLADE_T + TIP_BEVEL + 0.5)], ZS - GRIP_HALF - 1, ZS + GRIP_HALF + 1)
    return j



def build():
    return to_bed(Rot(0, -90, 0) * design())      # claw +x up: rack back face on the bed

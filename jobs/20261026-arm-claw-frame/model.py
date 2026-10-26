"""Claw frame: wrist plate on the wrist MG90S horn, bulkhead holding the claw MG90S with its
shaft along +x, and the lower rail behind rack B. Printed wrist plate down (back face on the bed).

Design frame = claw frame G (see ../20261025-robot-arm-assembly/claw_frame.py): origin on the
wrist axis at the back face, +x to the fingertips, +z outboard. The wrist horn sits 2 mm deep in
the back-face pocket, clamped by an M2 x 12 + washer from the front face at (0, 0). The claw
servo slides through the bulkhead window from behind; its tabs rest on the bulkhead's front face
(x = 10) with the shaft on the claw axis (y 0, z 22.5). Rack B slides on the wrist plate's top
face, backed by the lower rail. The cover screws on top (2 x M3 into the bulkhead top) and at the
front (2 x M3 into the wrist plate's front edge).
"""
import sys
from pathlib import Path

from build123d import Align, Box, BuildPart, BuildSketch, Cylinder, Location, Plane, Polygon, Pos, extrude
from cadlib import HOLE_COMP_DEFAULT, teardrop_cutter, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261025-robot-arm-assembly"))
from claw_frame import (BULK_T, FRONT_SCREWS, HALF_Y, M3_PILOT, RAIL_IN, RAIL_X1, REAR_HALF, SERVO,  # noqa: E402
                        T_W, TOP_SCREWS, WINDOW_ROOF, WRIST_HORN, X_B, X_F0, X_REAR, Z_TOP0, ZS)

from hobby_parts import _body_x0, chamfer_plane_edges, horn_pocket_cutter, servo_mount_cutter  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT  # +0.2 on hole diameters (default, fdm-design-rules)
CLR, END_CLR = 0.4, 0.2        # MG90S window side / end clearance (printed)
TOP_PILOT_DEPTH = 14.0         # M3 pilots in the bulkhead top (M3 x 10 cover, M3 x 18 with the camera)
FRONT_PILOT_DEPTH = 10.0       # M3 x 12 through the cover's front plate into the wrist plate
BED_CHAMFER = 0.4
# claw servo frame in G: shaft along +x at (X_B, 0, ZS); servo +x (long side) along +y,
# servo +y (width) along +z
SERVO_LOC = Location(Plane(origin=(X_B, 0, ZS), x_dir=(0, 1, 0), z_dir=(1, 0, 0)))


def _box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN,) * 3)


def _window_roof():
    """45° shoulders above the servo window (servo frame, +y side = up in print)."""
    c = CLR + HOLE_COMP
    ce = END_CLR + HOLE_COMP
    x0 = _body_x0(SERVO) - ce / 2
    x1 = x0 + SERVO.length + ce
    hw = (SERVO.width + c) / 2
    h = WINDOW_ROOF
    with BuildPart() as bp:
        with BuildSketch(Plane.XY.offset(-BULK_T - 1)):
            Polygon((x0, hw - 0.01), (x1, hw - 0.01), (x1 - h, hw + h), (x0 + h, hw + h), align=None)
        extrude(amount=BULK_T + 2)
    return bp.part


def design():
    plate = _box(X_REAR, X_F0, -HALF_Y, HALF_Y, 0, T_W)
    for s in (-1, 1):                                       # narrow tail behind the bulkhead
        y0, y1 = sorted((s * REAR_HALF, s * (HALF_Y + 1)))
        plate -= _box(X_REAR - 1, X_B - BULK_T, y0, y1, -1, T_W + 1)
    plate = chamfer_plane_edges(plate, 0.0, BED_CHAMFER)   # back face goes on the bed
    f = plate
    f += _box(X_B - BULK_T, X_B, -HALF_Y, HALF_Y, T_W - 0.01, Z_TOP0)           # bulkhead
    f += _box(X_B - 0.01, RAIL_X1, -HALF_Y, HALF_Y, T_W - 0.01, ZS - RAIL_IN)    # lower rail (behind rack B)
    win = servo_mount_cutter(SERVO, BULK_T, clearance=CLR, end_clearance=END_CLR, through=BULK_T * 2 + 2,
                             hole_comp=HOLE_COMP, pilot_teardrop="+y")
    f -= SERVO_LOC * (win + _window_roof())
    f -= horn_pocket_cutter(WRIST_HORN, link_t=T_W, hole_comp=HOLE_COMP)     # wrist horn, back face
    d = M3_PILOT + HOLE_COMP
    for (x, y) in TOP_SCREWS:                                                  # cover (+ camera mount) screws
        f -= Pos(x, y, Z_TOP0 - TOP_PILOT_DEPTH) * Cylinder(d / 2, TOP_PILOT_DEPTH + 1,
                                                          align=(Align.CENTER, Align.CENTER, Align.MIN))
    for (y, z) in FRONT_SCREWS:                                                # cover front screws (horizontal)
        f -= teardrop_cutter(d, 2 * FRONT_PILOT_DEPTH, axis="X", center=(X_F0, y, z))
    return f


def build():
    return to_bed(design())

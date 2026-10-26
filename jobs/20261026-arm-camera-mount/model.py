"""Camera mount: holds a Logitech Brio 4K (clip removed) on top of the claw, tilted 30° nose-down
so the jaws sit near the middle of the picture. Optional: the claw works without it.
Printed standing on its -y end (the side profile on the bed; every face a vertical wall).

Design frame = claw frame G (../20261025-robot-arm-assembly/claw_frame.py). The pad sits on the
cover's top wall over the bulkhead; the cover's two top screws, lengthened to M3 x 18 button
heads, go through pad + cover into the bulkhead. The camera's own 1/4"-20 thread (bottom
centre) takes a 1/4"-20 x 3/8" knurled thumb screw from under the seat; the slot allows ±4 mm
along the camera. The rear lip stops the camera turning about the screw.
Camera frame (BRIO_4K in tools/hobby_parts.py): origin at the thread on the bottom face,
+X = lens direction, +Y = long axis, +Z = up. Placed at (CAM_XC, 0, CAM_ZC), turned CAM_TILT
about +y (nose down).
"""
import math
import sys
from pathlib import Path

from build123d import Align, Box, BuildPart, BuildSketch, Location, Plane, Polygon, Pos, Rot, extrude
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261025-robot-arm-assembly"))
from claw_frame import (CAM_TILT, CAM_XC, CAM_ZC, LIP_CLR, LIP_H, LIP_T, M3_CLEAR, MOUNT_Y, PAD_TOP,  # noqa: E402
                        PAD_X, SEAT_T, TOP_SCREWS, Z_TOP1)

from hobby_parts import BRIO_4K, TRIPOD_SCREW_D, _teardrop_z  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT  # +0.2 on hole diameters (default, fdm-design-rules)
SCREW_CLR = 0.5                # 1/4"-20 clearance (printed)
SLOT_HALF = 4.0                # thread position tolerance along the camera
TO_PRINT = Rot(90, 0, 0)       # G +y -> print +Z (the -y end goes on the bed)
HALF_D = BRIO_4K.width / 2     # 13.5: camera depth (x) half
CAM_LOC = Location((CAM_XC, 0, CAM_ZC), (0, CAM_TILT, 0))   # camera frame -> G


def cam_to_g(cx: float, cz: float) -> tuple[float, float]:
    """Camera-frame (x, z) -> claw-frame (x, z) for the tilted camera."""
    a = math.radians(CAM_TILT)
    return (CAM_XC + cx * math.cos(a) + cz * math.sin(a), CAM_ZC - cx * math.sin(a) + cz * math.cos(a))


def profile():
    """Side profile (claw x-z) of the mount."""
    seat_front_top = cam_to_g(HALF_D, 0.0)
    pts = [(PAD_X[1], Z_TOP1), (PAD_X[1], PAD_TOP), (seat_front_top[0] + 0.3, PAD_TOP), seat_front_top,
           cam_to_g(-HALF_D - LIP_CLR, 0.0), cam_to_g(-HALF_D - LIP_CLR, LIP_H),
           cam_to_g(-HALF_D - LIP_CLR - LIP_T, LIP_H), cam_to_g(-HALF_D - LIP_CLR - LIP_T, -SEAT_T),
           cam_to_g(HALF_D, -SEAT_T), (PAD_X[0], Z_TOP1)]
    return pts


def design():
    y0, y1 = MOUNT_Y
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ.offset(-y1)):        # normal -y: sketch on y = y1, extrude down to y0
            Polygon(*profile(), align=None)
        extrude(amount=y1 - y0)
    m = bp.part
    # 1/4"-20 slot through the seat, along the camera's z; point towards +y (up in print)
    d = TRIPOD_SCREW_D + SCREW_CLR + HOLE_COMP
    slot = Pos(0, -SLOT_HALF, -SEAT_T - 1) * _teardrop_z(d, SEAT_T + 2, "+y")
    slot += Pos(0, SLOT_HALF, -SEAT_T - 1) * _teardrop_z(d, SEAT_T + 2, "+y")
    slot += Pos(0, 0, (-SEAT_T - 1 + 1) / 2) * Box(d, 2 * SLOT_HALF, SEAT_T + 4)
    m -= CAM_LOC * slot
    # M3 holes for the cover's top screws (shared with the cover)
    dm = M3_CLEAR + HOLE_COMP
    for (x, y) in TOP_SCREWS:
        m -= Pos(x, y, Z_TOP1 - 1) * _teardrop_z(dm, PAD_TOP - Z_TOP1 + 2, "+y")
    return m


def build():
    return to_bed(TO_PRINT * design())

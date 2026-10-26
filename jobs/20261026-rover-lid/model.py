"""Tracked rover lid / electronics deck: 3 mm plate screwed to the chassis's 4 corner columns.

On top: an ESP32 DevKit seat (38- or 30-pin, pins DOWN through a window into the tub, so female
jumpers fit every pin; the PCB rests on end ledges and is held by a zip tie), a flat area for a
170-point mini breadboard carrying the TB6612FNG motor driver (adhesive back), and a cable hole.
Design frame = rover world frame; the lid's underside is the chassis top (Z = TOP_Z).
Printed flat, underside on the bed; the seat rises from the top face.
"""
import sys
from pathlib import Path

from build123d import Align, Axis, Box, Cylinder, Pos, fillet
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-rover-assembly"))
from rover_frame import HALF_W_OUT, TOP_Z, X_FRONT_OUT, X_REAR_OUT  # noqa: E402

from hobby_parts import ESP32_DEVKIT_30, ESP32_DEVKIT_38, MINI_BREADBOARD, chamfer_plane_edges  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT
T = 3.0
CORNER_R = 6.0
SCREWS = [(-13.0, 30.0), (-13.0, -30.0), (100.0, 30.0), (100.0, -30.0)]   # = chassis COLUMNS (round 2)
SCREW_D = 3.4
BOARDS = (ESP32_DEVKIT_38, ESP32_DEVKIT_30)
USB_END_X = 14.0          # both boards' USB end (rear), so a cable reaches over the rear
LEDGE_H = 2.0             # PCB bottom this far above the lid top
CLR = 0.6                 # round the PCB (printed)
RAIL_W = 2.5
LONG = max(b.length for b in BOARDS)
SHORT = min(b.length for b in BOARDS)
HALF = max(b.width for b in BOARDS) / 2 + CLR + HOLE_COMP / 2
ROW_KEEP = 9.0            # tongue |y| < 9 sits between the pin rows
END_LEDGE = 2.4           # full-width ledge at each end, outside the pin housings
TIE_SLOT = (3.2, 1.8)     # zip-tie slots beside the board (x, y)
TIE_FROM_END = 1.2        # ties cross the board 1.2 mm from its ends, where there are no pins (DFM round 1)
BB_X0 = 84.0              # mini breadboard area (47 × 35) starts here
CABLE_HOLE = (76.0, 0.0, 10.0)    # x, y, Ø: motor, battery and sensor leads up from the tub
BED_CHAMFER = 0.4


def _box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN,) * 3)


def design():
    z0, z1 = TOP_Z, TOP_Z + T
    lid = _box(X_REAR_OUT, X_FRONT_OUT, -HALF_W_OUT, HALF_W_OUT, z0, z1)
    lid = fillet(lid.edges().filter_by(Axis.Z), radius=CORNER_R)
    lid = chamfer_plane_edges(lid, z0, BED_CHAMFER)
    # ESP32 seat
    xa, xb = USB_END_X - CLR, USB_END_X + LONG + CLR
    ztop = z1 + LEDGE_H
    lid += _box(xa, USB_END_X + END_LEDGE, -HALF, HALF, z1 - 0.01, ztop)                       # USB-end ledge
    lid += _box(USB_END_X + LONG - END_LEDGE, xb, -HALF, HALF, z1 - 0.01, ztop)               # far ledge (long board)
    lid += _box(USB_END_X + SHORT - 2.5, xb, -ROW_KEEP, ROW_KEEP, z1 - 0.01, ztop)            # tongue (short board)
    for s in (-1, 1):
        y0, y1 = sorted((s * HALF, s * (HALF + RAIL_W)))
        lid += _box(xa, xb, y0, y1, z1 - 0.01, ztop + 1.6 + 0.5)                               # side rails
    win = _box(USB_END_X + END_LEDGE, USB_END_X + LONG - END_LEDGE, -HALF, HALF, z0 - 1, ztop + 1)
    win -= _box(USB_END_X + SHORT - 2.5, xb, -ROW_KEEP, ROW_KEEP, z0 - 2, ztop + 2)
    lid -= win
    # zip ties over the board's pin-free ends: USB end, the 38-pin board's far end, the 30-pin board's far end
    for xm in (USB_END_X + TIE_FROM_END, USB_END_X + LONG - TIE_FROM_END, USB_END_X + SHORT - TIE_FROM_END):
        for s in (-1, 1):
            yc = s * (HALF + RAIL_W + 1.5 + TIE_SLOT[1] / 2)
            lid -= _box(xm - TIE_SLOT[0] / 2, xm + TIE_SLOT[0] / 2, yc - TIE_SLOT[1] / 2, yc + TIE_SLOT[1] / 2, z0 - 1, z1 + 1)
    # screws, cable hole
    for (x, y) in SCREWS:
        lid -= Pos(x, y, z0 - 1) * Cylinder((SCREW_D + HOLE_COMP) / 2, T + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cx, cy, cd = CABLE_HOLE
    lid -= Pos(cx, cy, z0 - 1) * Cylinder((cd + HOLE_COMP) / 2, T + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    assert BB_X0 + MINI_BREADBOARD.length <= X_FRONT_OUT - 3 and cx + cd / 2 < BB_X0
    return lid


def build():
    return to_bed(design())

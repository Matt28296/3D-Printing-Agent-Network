"""Hexapod top body plate / electronics deck, screwed onto the bottom plate's four columns.

Carries the ESP32 DevKit (pins down through a window, PCB on end ledges, zip tie), the two
PCA9685 servo-driver boards on M2.5 posts (servo headers facing out to each side), and room for
the 6 V UBEC; two cable slots per side let the 18 servo leads up from between the plates.
Design frame: hexapod body frame with the top plate's underside at Z = 0. Printed flat.
"""
import sys
from pathlib import Path

from build123d import Align, Axis, Box, Cylinder, Pos, fillet
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-hexapod-assembly"))
from hex_frame import T_TOP  # noqa: E402

from hobby_parts import ESP32_DEVKIT_30, ESP32_DEVKIT_38, PCA9685_BOARD, PCA9685_HOLES, chamfer_plane_edges  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT
SIZE = (130.0, 104.0)            # x × y
CORNER_R = 10.0
SCREWS = [(30.0, 25.0), (30.0, -25.0), (-30.0, 25.0), (-30.0, -25.0)]   # = bottom-plate columns
SCREW_D = 3.4
BOARDS = (ESP32_DEVKIT_38, ESP32_DEVKIT_30)
USB_END_X = -27.2                # boards centred on x; USB end towards the rear
LEDGE_H, CLR, RAIL_W = 2.0, 0.6, 2.5
LONG = max(b.length for b in BOARDS)
SHORT = min(b.length for b in BOARDS)
HALF = max(b.width for b in BOARDS) / 2 + CLR + HOLE_COMP / 2
ROW_KEEP, END_LEDGE = 9.0, 2.4
PCA_Y = 34.5                     # PCA9685 board centres at y ±34.5 (x 0)
POST_D, POST_H, POST_PILOT = 5.5, 5.0, 2.2   # M2.5 self-tapping posts
CABLE_SLOTS = [(-46.0, 12.0), (46.0, 12.0)]   # x centres; slot 20 × 8 at y ±(this)… see design()
TIE_SLOT = (3.2, 1.8)
BED_CHAMFER = 0.4


def _box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN,) * 3)


def design():
    sx, sy = SIZE
    t = T_TOP
    top = _box(-sx / 2, sx / 2, -sy / 2, sy / 2, 0, t)
    top = fillet(top.edges().filter_by(Axis.Z), radius=CORNER_R)
    top = chamfer_plane_edges(top, 0.0, BED_CHAMFER)
    # ESP32 seat (same scheme as the rover lid)
    xa, xb = USB_END_X - CLR, USB_END_X + LONG + CLR
    ztop = t + LEDGE_H
    top += _box(xa, USB_END_X + END_LEDGE, -HALF, HALF, t - 0.01, ztop)
    top += _box(USB_END_X + LONG - END_LEDGE, xb, -HALF, HALF, t - 0.01, ztop)
    top += _box(USB_END_X + SHORT - 2.5, xb, -ROW_KEEP, ROW_KEEP, t - 0.01, ztop)
    for s in (-1, 1):
        y0, y1 = sorted((s * HALF, s * (HALF + RAIL_W)))
        top += _box(xa, xb, y0, y1, t - 0.01, ztop + 1.6 + 0.5)
    win = _box(USB_END_X + END_LEDGE, USB_END_X + LONG - END_LEDGE, -HALF, HALF, -1, ztop + 1)
    win -= _box(USB_END_X + SHORT - 2.5, xb, -ROW_KEEP, ROW_KEEP, -2, ztop + 2)
    top -= win
    xm = USB_END_X + SHORT / 2
    for s in (-1, 1):
        yc = s * (HALF + RAIL_W + 1.5 + TIE_SLOT[1] / 2)
        top -= _box(xm - TIE_SLOT[0] / 2, xm + TIE_SLOT[0] / 2, yc - TIE_SLOT[1] / 2, yc + TIE_SLOT[1] / 2, -1, t + 1)
    # PCA9685 posts
    hx, hy = PCA9685_HOLES
    for s in (-1, 1):
        for dx in (-hx / 2, hx / 2):
            for dy in (-hy / 2, hy / 2):
                x, y = dx, s * PCA_Y + dy
                top += Pos(x, y, t - 0.01) * Cylinder(POST_D / 2, POST_H + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
                top -= Pos(x, y, t + POST_H - 6) * Cylinder((POST_PILOT + HOLE_COMP) / 2, 7, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # cable slots between the PCA boards' ends and the plate edge (front and rear, each side)
    for x in (-50.0, 50.0):
        for s in (-1, 1):
            top -= _box(x - 4, x + 4, s * 22 - 8, s * 22 + 8, -1, t + 1)
    for (x, y) in SCREWS:
        top -= Pos(x, y, -1) * Cylinder((SCREW_D + HOLE_COMP) / 2, t + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    assert PCA_Y - PCA9685_BOARD.width / 2 > HALF + RAIL_W + 3.0, "PCA board overlaps the ESP32 rails"
    return top


def build():
    return to_bed(design())

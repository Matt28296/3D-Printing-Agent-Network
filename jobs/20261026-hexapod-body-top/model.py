"""Hexapod top plate / electronics deck, screwed onto the bottom plate's four columns.

Carries the ESP32 DevKit (pins down through a window, PCB on end ledges, zip tie), the two
PCA9685 servo-driver boards on M2.5 posts (servo headers facing out to each side), the MP1584 buck
and the main switch. The UBEC is not on the deck: it stands on its side on the bottom plate, beside
the LiPo.

Round 3 (deep review 2026-10-26):
  - SYS-4: each leg's three leads come up the body's side beside that leg and over the deck edge to the
    headers: a lead notch in the deck edge per leg (front, middle, rear on each side), with a tie slot
    beside it. Two cable slots per side stay for leads that come up inside the body.
  - SYS-10: a Ø12 hole for the main switch (12 mm-bushing toggle, rated >= 10 A DC: deep review 02-H4)
    at the rear, behind the ESP32's USB end.
  - The columns moved to (±36, ±25) (hex_frame.COLUMNS), clear of the coxa servos' tabs on the bottom plate.
Design frame: hexapod body frame with the top plate's underside at Z = 0. Printed flat.
"""
import sys
from pathlib import Path

from build123d import Align, Axis, Box, Cylinder, Pos, fillet
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-hexapod-assembly"))
from hex_frame import COLUMNS, T_TOP  # noqa: E402

from hobby_parts import ESP32_DEVKIT_30, ESP32_DEVKIT_38, PCA9685_BOARD, PCA9685_HOLES, chamfer_plane_edges  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT    # +0.2 on every hole (fdm-design-rules default; no library row)
SIZE = (130.0, 104.0)            # x × y
CORNER_R = 10.0
SCREWS = COLUMNS                 # = bottom-plate columns (hex_frame.py)
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
CABLE_SLOTS = [(-50.0, 22.0), (50.0, 22.0)]  # cable slot centres (x, ±y), each CABLE_SLOT_SIZE, both sides
CABLE_SLOT_SIZE = (8.0, 16.0)    # x × y
LEAD_NOTCH_X = (-40.0, 0.0, 40.0)    # SYS-4: one lead notch per leg in each long edge (rear, middle, front)
LEAD_NOTCH = (10.0, 5.0, 1.5)    # width (x) × depth (y) × inner corner radius
TIE_SLOT = (3.2, 1.8)
NOTCH_TIE_DX = 8.5               # tie slot beside each notch, towards the deck's centre line (x 0)
SWITCH_D = 12.0                  # SYS-10: main switch, 12 mm bushing (>= 10 A DC, deep review 02-H4)
SWITCH_XY = (-50.0, 0.0)
BED_CHAMFER = 0.4


def _box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN,) * 3)


def _notch(xc, side, t):
    """Lead notch in the long edge at y = side × SIZE[1]/2: rounded inner corners, open to the edge."""
    w, d, r = LEAD_NOTCH
    y_edge = side * SIZE[1] / 2
    yi = y_edge - side * d                      # inner end of the notch
    y0, y1 = sorted((yi, y_edge + side * 1.0))
    n = _box(xc - w / 2 + r, xc + w / 2 - r, y0, y1, -1, t + 1)
    yr = yi + side * r
    y0, y1 = sorted((yr, y_edge + side * 1.0))
    n += _box(xc - w / 2, xc + w / 2, y0, y1, -1, t + 1)
    for dx in (-1, 1):
        n += Pos(xc + dx * (w / 2 - r), yr, -1) * Cylinder(r, t + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return n


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
    cw, cl = CABLE_SLOT_SIZE
    for (x, y) in CABLE_SLOTS:
        for s in (-1, 1):
            top -= _box(x - cw / 2, x + cw / 2, s * y - cl / 2, s * y + cl / 2, -1, t + 1)
    # SYS-4 lead notches in both long edges, with a tie slot beside each
    tw, th = TIE_SLOT
    for xc in LEAD_NOTCH_X:
        for s in (-1, 1):
            top -= _notch(xc, s, t)
            xt = xc - NOTCH_TIE_DX if xc > 0 else xc + NOTCH_TIE_DX
            yt = s * (SIZE[1] / 2 - LEAD_NOTCH[1] / 2)
            top -= _box(xt - (tw + HOLE_COMP) / 2, xt + (tw + HOLE_COMP) / 2, yt - (th + HOLE_COMP) / 2,
                        yt + (th + HOLE_COMP) / 2, -1, t + 1)
    # SYS-10 main switch
    top -= Pos(*SWITCH_XY, -1) * Cylinder((SWITCH_D + HOLE_COMP) / 2, t + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for (x, y) in SCREWS:
        top -= Pos(x, y, -1) * Cylinder((SCREW_D + HOLE_COMP) / 2, t + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    assert PCA_Y - PCA9685_BOARD.width / 2 > HALF + RAIL_W + 3.0, "PCA board overlaps the ESP32 rails"
    assert min(abs(x) for x, _ in SCREWS) - SCREW_D / 2 - 2.0 > PCA9685_BOARD.length / 2, "screw heads under a PCA board"
    return top


def build():
    return to_bed(design())

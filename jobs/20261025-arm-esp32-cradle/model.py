"""ESP32 cradle: open frame that hangs under the base top plate and holds an ESP32 DevKit
(38-pin 54.4 mm or 30-pin 51.5 mm) with its USB port in the base's +X wall slot.

Design frame = assembly/base frame (Z = 0 is the base top-plate top; the cradle screws up
into three bosses whose ends are at Z = -10). The board sits pins-DOWN with its PCB on two
end ledges, so female jumper wires can push onto every pin: nothing in the frame passes
under the two pin rows. Printed upright (Z = -20 on the bed); every ledge rises from the bed.
Screws: 3 × M3×10 from below, heads in 6 mm counterbores: 4 mm clamp + 6 mm into the 6 mm-deep boss pilots
(an M3×12 would bottom out 2 mm into undrilled plate; DFM round 2).
"""
from build123d import Align, Box, Cylinder, Pos
from cadlib import HOLE_COMP_DEFAULT, to_bed
from hobby_parts import ESP32_DEVKIT_30, ESP32_DEVKIT_38, chamfer_plane_edges

# --- parameters (mm) -----------------------------------------------------------
BOARDS = (ESP32_DEVKIT_38, ESP32_DEVKIT_30)
HOLE_COMP = HOLE_COMP_DEFAULT   # +0.2 on holes and the PCB pocket (default, fdm-design-rules)
USB_END_X = 51.0         # board USB end (base inner wall at x = 52)
YC = 28.0                # board centreline = base USB slot centre
PCB_BOT = -11.6          # PCB bottom; PCB top at -10 puts the USB centre at the slot (Z -8.5)
TOP, BOT = -10.0, -20.0  # frame top (touches the bosses) and bottom (bed); 10 tall (strength round 1)
CLR = 0.6                # around the PCB (printed)
WALL = 2.5
HALF = max(b.width for b in BOARDS) / 2 + CLR + HOLE_COMP / 2   # pocket half width (14.85)
ROW_KEEP = 11.0          # |y - YC| < 11 is clear of both pin-row headers (rows at ±12.65 ±1.27)
LONGEST = max(b.length for b in BOARDS)
SHORTEST = min(b.length for b in BOARDS)
FAR_X = USB_END_X - LONGEST         # -3.4: far end of the long board
FAR_X_SHORT = USB_END_X - SHORTEST  # -0.5: far end of the short board
USB_LEDGE_W = 2.8        # under the PCB end, beyond the last pin housings (x <= 47.9); strength round 1
USB_LEDGE_Y1 = 41.5      # stops 1 mm short of the base corner pillar (r 4 at (49.5, 46.5))
PILLAR_CLEAR_X = 44.0    # the +Y wall stops here, clear of the base corner pillar (x >= 45.5)
SCREWS = [(-9.4, 18.0), (-9.4, 38.0), (40.0, 7.9)]   # must match the base CRADLE_PILOTS
HOLE = 3.4               # M3 clearance (printed)
CBORE_D, CBORE_DEPTH = 6.5, 6.0   # screw-head counterbore from below: leaves a 4 mm clamp
PAD_R = 5.8              # third-screw pad radius: 2.45 mm wall round its counterbore
FAR_BLOCK_X0 = -15.5      # leaves 2.75 mm round the far counterbores (DFM: wall)
BED_CHAMFER = 0.4


def _blk(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN,) * 3)


def design():
    y_in0, y_in1 = YC - HALF, YC + HALF
    y_out0, y_out1 = y_in0 - WALL, y_in1 + WALL
    # far block with the two far screws (outside the PCB, full height)
    c = _blk(FAR_BLOCK_X0, FAR_X - CLR, y_out0, y_out1, BOT, TOP)
    # side walls guide the PCB edges (they stay outside the pin-row headers)
    c += _blk(FAR_BLOCK_X0, USB_END_X, y_out0, y_in0, BOT, TOP)
    c += _blk(FAR_BLOCK_X0, PILLAR_CLEAR_X, y_in1, y_out1, BOT, TOP)
    # far ledge: full width beyond the long board's first pins, plus a centre tongue under
    # the short board's end (between the rows only)
    c += _blk(FAR_X - CLR, FAR_X + 2.2, y_in0, y_in1, BOT, PCB_BOT)
    c += _blk(FAR_X - CLR, FAR_X_SHORT + 2.5, YC - ROW_KEEP + 1, YC + ROW_KEEP - 1, BOT, PCB_BOT)
    # USB-end ledge under the PCB end, beyond the last pin housings
    c += _blk(USB_END_X - USB_LEDGE_W, USB_END_X, y_in0, USB_LEDGE_Y1, BOT, PCB_BOT)
    # centre spine ties the ledges together, between the pin rows, 0.4 below the PCB
    c += _blk(FAR_X - CLR, USB_END_X, YC - 4, YC + 4, BOT, PCB_BOT - 0.4)
    # pad for the third screw, off the -Y wall
    sx, sy = SCREWS[2]
    c += _blk(sx - PAD_R, sx + PAD_R, sy, y_out0 + 0.01, BOT, TOP)
    c += Pos(sx, sy, BOT) * Cylinder(PAD_R, TOP - BOT, align=(Align.CENTER, Align.CENTER, Align.MIN))
    c = chamfer_plane_edges(c, BOT, BED_CHAMFER)
    for (x, y) in SCREWS:
        c -= Pos(x, y, BOT - 1) * Cylinder((HOLE + HOLE_COMP) / 2, TOP - BOT + 2,
                                           align=(Align.CENTER, Align.CENTER, Align.MIN))
        c -= Pos(x, y, BOT - 1) * Cylinder((CBORE_D + HOLE_COMP) / 2, CBORE_DEPTH + 1,
                                           align=(Align.CENTER, Align.CENTER, Align.MIN))
    return c


def build():
    return to_bed(design())

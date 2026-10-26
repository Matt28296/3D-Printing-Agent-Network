"""ESP32 cradle: open frame that hangs under the base top plate and holds an ESP32 DevKit
(38-pin 54.4 mm or 30-pin 51.5 mm) with its USB port in the base's +X wall slot.

Design frame = assembly/base frame (Z = 0 is the base top-plate top; the cradle screws up
into three bosses whose ends are at Z = -10). The board sits pins-DOWN with its PCB on two
end ledges, so female jumper wires can push onto every pin: nothing in the frame passes
under the two pin rows. Printed upright (Z = -16 on the bed); every ledge rises from the bed.
"""
from build123d import Align, Box, Cylinder, Pos
from cadlib import to_bed
from hobby_parts import ESP32_DEVKIT_30, ESP32_DEVKIT_38

# --- parameters (mm) -----------------------------------------------------------
BOARDS = (ESP32_DEVKIT_38, ESP32_DEVKIT_30)
USB_END_X = 51.0         # board USB end (base inner wall at x = 52)
YC = 28.0                # board centreline = base USB slot centre
PCB_BOT = -11.6          # PCB bottom; PCB top at -10 puts the USB centre at the slot (Z -8.5)
TOP, BOT = -10.0, -16.0  # frame top (touches the bosses) and bottom (bed)
CLR = 0.6                # around the PCB
WALL = 2.5
HALF = max(b.width for b in BOARDS) / 2 + CLR          # pocket half width (14.75)
ROW_KEEP = 11.0          # |y - YC| < 11 is clear of both pin-row headers (rows at ±12.65 ±1.27)
LONGEST = max(b.length for b in BOARDS)
SHORTEST = min(b.length for b in BOARDS)
FAR_X = USB_END_X - LONGEST        # -3.4: far end of the long board
FAR_X_SHORT = USB_END_X - SHORTEST  # -0.5: far end of the short board
PILLAR_CLEAR_X = 44.0     # the +Y wall stops here, clear of the base corner pillar (x >= 45.5)
SCREWS = [(-9.4, 18.0), (-9.4, 38.0), (40.0, 7.9)]   # must match the base CRADLE_PILOTS
HOLE = 3.4               # M3 clearance
FAR_BLOCK_X0 = -13.0


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
    # USB-end ledge: 1.6 mm strip under the PCB end, beyond the last pins (end pins >= 4.3 in)
    c += _blk(USB_END_X - 1.6, USB_END_X, y_in0, YC + ROW_KEEP + 3.5, BOT, PCB_BOT)
    # centre spine ties the ledges together, between the pin rows, 0.4 below the PCB
    c += _blk(FAR_X - CLR, USB_END_X, YC - 4, YC + 4, BOT, PCB_BOT - 0.4)
    # pad for the third screw, off the -Y wall
    sx, sy = SCREWS[2]
    c += _blk(sx - 4.5, sx + 4.5, sy - 4.0, y_out0 + 0.01, BOT, TOP)
    c += Pos(sx, sy, BOT) * Cylinder(4.5, TOP - BOT, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for (x, y) in SCREWS:
        c -= Pos(x, y, BOT - 1) * Cylinder(HOLE / 2, TOP - BOT + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return c


def build():
    return to_bed(design())

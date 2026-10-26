"""Hexapod bottom body plate: the six coxa MG90S servos hang below it (tabs on its underside,
bodies up through windows, shafts down), with four columns for the top plate and strap slots
for the 2S LiPo that sits on it between the servos.

Design frame: hexapod body frame (hex_frame.py) with the coxa tab plane at Z = 0 (in the
assembled robot it sits at the stance height). Each coxa servo frame: origin at its mount point
on Z = 0, x = radial outward, z = world -Z. Outline = convex hull of the six windows and their
pilots, plus a margin. Printed flat, underside (tab face) on the bed.
"""
import math
import sys
from pathlib import Path

from build123d import Align, BuildPart, BuildSketch, Cylinder, Location, Plane, Polygon, Pos, extrude
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-hexapod-assembly"))
from hex_frame import COLUMN_H, LEG_MOUNTS, SERVO, T_BODY  # noqa: E402

from hobby_parts import LIPO_2S_1000, chamfer_plane_edges, servo_mount_cutter  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT
CLR, END_CLR = 0.4, 0.2
MARGIN = 4.0                     # plate beyond each pilot / window
COLUMNS = [(30.0, 25.0), (30.0, -25.0), (-30.0, 25.0), (-30.0, -25.0)]
COLUMN_D, COLUMN_PILOT, PILOT_DEPTH = 8.0, 2.6, 10.0
STRAP = (3.0, 22.0)              # velcro slot w (y) × l (x), either side of the LiPo
BED_CHAMFER = 0.4


def servo_loc(x, y, a_deg):
    a = math.radians(a_deg)
    return Location(Plane(origin=(x, y, 0), x_dir=(math.cos(a), math.sin(a), 0), z_dir=(0, 0, -1)))


def _hull(pts):
    pts = sorted(set(pts))
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def outline_points():
    x0 = -(SERVO.length - SERVO.shaft_from_end) + SERVO.length / 2 - SERVO.hole_dx / 2 - MARGIN - 1.0
    x1 = -(SERVO.length - SERVO.shaft_from_end) + SERVO.length / 2 + SERVO.hole_dx / 2 + MARGIN + 1.0
    hw = SERVO.width / 2 + MARGIN + 1.0
    pts = []
    for (mx, my, a) in LEG_MOUNTS:
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        for (u, v) in ((x0, -hw), (x0, hw), (x1, -hw), (x1, hw)):
            pts.append((round(mx + u * c - v * s, 3), round(my + u * s + v * c, 3)))
    return _hull(pts)


def design():
    with BuildPart() as bp:
        with BuildSketch(Plane.XY):
            Polygon(*outline_points(), align=None)
        extrude(amount=T_BODY)
    plate = chamfer_plane_edges(bp.part, 0.0, BED_CHAMFER)
    for (x, y) in COLUMNS:
        plate += Pos(x, y, T_BODY - 0.01) * Cylinder(COLUMN_D / 2, COLUMN_H + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
        plate -= Pos(x, y, T_BODY + COLUMN_H - PILOT_DEPTH) * Cylinder((COLUMN_PILOT + HOLE_COMP) / 2, PILOT_DEPTH + 1,
                                                                       align=(Align.CENTER, Align.CENTER, Align.MIN))
    for (mx, my, a) in LEG_MOUNTS:
        plate -= servo_loc(mx, my, a) * servo_mount_cutter(SERVO, T_BODY, clearance=CLR, end_clearance=END_CLR,
                                                           through=2 * T_BODY + 2, hole_comp=HOLE_COMP)
    w, l = STRAP
    for s in (-1, 1):
        y = s * (LIPO_2S_1000.width / 2 + 1.0 + w / 2)
        plate -= Pos(-l / 2, y - w / 2, -1) * _box(l, w, T_BODY + 2)
    return plate


def _box(x, y, z):
    from build123d import Box
    return Box(x, y, z, align=(Align.MIN,) * 3)


def build():
    return to_bed(design())

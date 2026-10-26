"""Hexapod bottom body plate: the six coxa MG90S servos hang through it (shafts down), with four
columns for the top plate and strap slots for the 2S LiPo that sits on it between the servos.

Round 3 (deep review 2026-10-26, strength round 1):
  - B1 option 2: each coxa servo is mounted REVERSED: lowered in from above, spline first, its tabs
    resting on the plate's TOP face. The case and its lead stay inside the body, so the lead never
    crosses the plate (servo_mount_cutter lead="none"). The shaft and gear boss pass down through the
    window; the coxa bracket's back face is PLATE_GAP (4.1 mm) under the plate.
  - Strength: T_BODY 6 (was 4); the tab screws are M2 × 12 machine screws through Ø2.4 CAD clearance holes,
    head and washer on the underside, washer and nut on the tab inside the body.
  - Middle legs at y ±56 and columns at (±36, ±25) (hex_frame.py): clear of the tabs now on the plate top.
  - SYS-5: a 3.2 × 1.8 tie slot beside each window, on the side the femur and tibia leads come up.

Design frame: hexapod body frame with the plate's UNDERSIDE at Z = 0 (in the assembled robot it sits at
hex_frame.STANCE_Z_PU). Outline = convex hull of the six windows and their pilots, plus a margin.
Printed flat, underside on the bed.
"""
import math
import sys
from pathlib import Path

from build123d import Align, Box, BuildPart, BuildSketch, Cylinder, GeomType, Location, Plane, Polygon, Pos, Rot, extrude, fillet
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-hexapod-assembly"))
from hex_frame import COLUMN_H, COLUMNS, COXA_MOUNT, LEG_MOUNTS, SERVO, T_BODY  # noqa: E402

from hobby_parts import LIPO_2S_1000, chamfer_plane_edges, replace, servo_mount_cutter  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT    # +0.2 on every hole (fdm-design-rules default; no library row)
CLR, END_CLR = 0.4, 0.2          # coxa servo window side / end clearance (printed)
LEAD = "none"                    # B1 option 2: the servo is reversed, its lead never crosses the plate
TAB_SCREW_CLEAR = 2.2            # strength round 1: M2 machine screw clearance, printed (2.4 in CAD), slotted 0.4 outward
MARGIN = 4.0                     # plate beyond each pilot / window
COLUMN_D, COLUMN_PILOT, PILOT_DEPTH = 8.0, 2.6, 10.0
COLUMN_FILLET = 1.5              # root fillet (DFM round 1: the columns got 10 mm longer)
STRAP = (3.0, 22.0)              # velcro slot w (y) × l (x), either side of the LiPo
TIE_SLOT = (3.2, 1.8)            # SYS-5: lead tie slot, along × across the servo axis
TIE_UV = (4.0, -16.0)            # in each coxa servo frame (S0 x radial, S0 y): beside the window, on the leads' side
BED_CHAMFER = 0.4

TAB_SCREW_SPEC = replace(SERVO, screw_pilot_d=TAB_SCREW_CLEAR)


def servo_cutter_loc(x, y, a_deg):
    """Cutter frame for a coxa window: on the face the tabs rest on, z pointing away from the plate."""
    a = math.radians(a_deg)
    if COXA_MOUNT == "reversed":       # tabs on the top face, z = T_BODY, pointing up
        return Location(Plane(origin=(x, y, T_BODY), x_dir=(math.cos(a), math.sin(a), 0), z_dir=(0, 0, 1)))
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


def to_world(mx, my, a_deg, u, v):
    """Point (u, v) of a coxa servo frame S0 (x radial out, y = z × x with z down) in the body frame."""
    c, s = math.cos(math.radians(a_deg)), math.sin(math.radians(a_deg))
    return mx + u * c + v * s, my + u * s - v * c


def outline_points():
    x0 = -(SERVO.length - SERVO.shaft_from_end) + SERVO.length / 2 - SERVO.hole_dx / 2 - MARGIN - 1.0
    x1 = -(SERVO.length - SERVO.shaft_from_end) + SERVO.length / 2 + SERVO.hole_dx / 2 + MARGIN + 1.0
    hw = SERVO.width / 2 + MARGIN + 1.0
    pts = []
    for (mx, my, a) in LEG_MOUNTS:
        for (u, v) in ((x0, -hw), (x0, hw), (x1, -hw), (x1, hw)):
            pts.append(tuple(round(c, 3) for c in to_world(mx, my, a, u, v)))
    return _hull(pts)


def design():
    with BuildPart() as bp:
        with BuildSketch(Plane.XY):
            Polygon(*outline_points(), align=None)
        extrude(amount=T_BODY)
    plate = chamfer_plane_edges(bp.part, 0.0, BED_CHAMFER)
    for (x, y) in COLUMNS:
        plate += Pos(x, y, T_BODY - 0.01) * Cylinder(COLUMN_D / 2, COLUMN_H + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
    roots = [e for e in plate.edges()
             if e.geom_type == GeomType.CIRCLE and abs(e.radius - COLUMN_D / 2) < 1e-3
             and abs(e.center().Z - T_BODY) < 0.05]
    plate = fillet(roots, radius=COLUMN_FILLET)
    for (x, y) in COLUMNS:
        plate -= Pos(x, y, T_BODY + COLUMN_H - PILOT_DEPTH) * Cylinder((COLUMN_PILOT + HOLE_COMP) / 2, PILOT_DEPTH + 1,
                                                                       align=(Align.CENTER, Align.CENTER, Align.MIN))
    for (mx, my, a) in LEG_MOUNTS:
        plate -= servo_cutter_loc(mx, my, a) * servo_mount_cutter(TAB_SCREW_SPEC, T_BODY, clearance=CLR,
                                                                  end_clearance=END_CLR, through=2 * T_BODY + 2,
                                                                  hole_comp=HOLE_COMP, lead=LEAD)
        tx, ty = to_world(mx, my, a, *TIE_UV)
        plate -= Pos(tx, ty, -1) * Rot(0, 0, a) * Box(TIE_SLOT[0] + HOLE_COMP, TIE_SLOT[1] + HOLE_COMP, T_BODY + 2,
                                                       align=(Align.CENTER, Align.CENTER, Align.MIN))
    w, l = STRAP
    for s in (-1, 1):
        y = s * (LIPO_2S_1000.width / 2 + 1.0 + w / 2)
        plate -= Pos(-l / 2, y - w / 2, -1) * Box(l, w, T_BODY + 2, align=(Align.MIN,) * 3)
    return plate


def build():
    return to_bed(design())

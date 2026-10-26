"""Claw cover: front plate + top wall + upper lip. It closes the two rack channels, carries the
finger slots and lets the pinion through. Printed standing on its -y end (the side profile on
the bed, every channel face a vertical wall).

Design frame = claw frame G (../20261025-robot-arm-assembly/claw_frame.py). Rack A (upper)
runs between the lip (behind it), the top wall (above it, its back face riding there), the front
plate (in front of it) and the pinion (below it). Rack B rides on the frame's wrist plate,
between the frame's lower rail and this front plate. Each jaw's neck passes through a slot in
the front plate: slot A (upper) is open at the -y end, slot B (lower) at the +y end, so the jaws
slide in from the ends after the cover is screwed on.

Round 2 (deep review 03 SYS-01 fix A, claw DFM + strength round 1):
- a Ø22.6 (printed) pass-through on the pinion axis: the pinion goes in LAST, axially, with both
  jaws parked fully open, and comes out first for service. The plate slivers it would leave
  next to the slots are cut back to |y| 7 (CRESCENT_Y); its top (up in print) is a 45° teardrop;
- front plate 3 -> 5 thick and down to z -4, so the strip under slot B is 9.75 deep;
- slot A closes with a 45° roof (a ceiling in print), slot B with r 2 corners; both slots are
  cut before the bed chamfer, so slot A's mouth on the bed is chamfered too;
- r 2 fillet in the inner corner between the front plate and the top wall (beside slot A's end);
  3 mm 45° chamfer on the top-front outer edge so the camera sees the fingertips;
- top wall extended back to x 0 (carries the whole camera pad);
- the lip is a 4 mm wall (x 18.35..22.35) behind rack A, not a block back to the bulkhead: 8 g less
  at the end of the arm.
"""
import math
import sys
from pathlib import Path

from build123d import Align, Box, BuildPart, BuildSketch, Circle, Locations, Plane, Polygon, Pos, Rot, extrude
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261025-robot-arm-assembly"))
from claw_frame import (ACCESS_D, CORNER_FILLET, CORNER_FILLET_Y0, CRESCENT_Y, FRONT_SCREWS, FRONT_Z0, HALF_Y, M3_CLEAR,  # noqa: E402
                        M25_CLEAR, NECK_Z, RAIL_IN, RAIL_X0, RAIL_X1, SLOT_A_END, SLOT_B_END, SLOT_CLR, SLOT_FILLET,
                        TIE_X0, TIE_Y, TIE_Z, TOP_CHAMFER, TOP_SCREWS, TOP_X0, X_F0, X_F1, Z_TOP0, Z_TOP1, ZS)

from hobby_parts import _teardrop_z, chamfer_plane_edges  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT  # +0.2 on hole diameters (default, fdm-design-rules)
BED_CHAMFER = 0.3
TO_PRINT = Rot(90, 0, 0)       # G +y -> print +Z (the -y end goes on the bed)
APEX_R = 1.5                   # rounding at the apexes of slot A's roof and the pass-through teardrop
R_PASS = (ACCESS_D + HOLE_COMP) / 2          # 11.4 in CAD (11.3 printed): the pinion's tips reach 10.85
ZA0 = ZS + NECK_Z[0] - SLOT_CLR              # 38.25: slot A, side nearer the axis
ZA1 = Z_TOP0                                 # 48.5: slot A's outer edge is the top wall's underside
ZB0 = ZS - NECK_Z[1] - SLOT_CLR              # 5.75: slot B over the strip
ZB1 = ZS - NECK_Z[0] + SLOT_CLR              # 16.25
Z_CRES = math.sqrt(R_PASS ** 2 - CRESCENT_Y ** 2)   # 9.0: where the pass-through meets |y| = CRESCENT_Y


def _box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN,) * 3)


def _round(pts, corners, r, n=8):
    """Round the given corner indices of a closed polyline with arcs of radius r (tangent to both edges)."""
    out = []
    for i, p in enumerate(pts):
        if i not in corners:
            out.append(p)
            continue
        a, c = pts[i - 1], pts[(i + 1) % len(pts)]
        u = (a[0] - p[0], a[1] - p[1]); lu = math.hypot(*u); u = (u[0] / lu, u[1] / lu)
        v = (c[0] - p[0], c[1] - p[1]); lv = math.hypot(*v); v = (v[0] / lv, v[1] / lv)
        half = math.acos(max(-1.0, min(1.0, u[0] * v[0] + u[1] * v[1]))) / 2
        t = r / math.tan(half)
        b = (u[0] + v[0], u[1] + v[1]); lb = math.hypot(*b); b = (b[0] / lb, b[1] / lb)
        cen = (p[0] + b[0] * r / math.sin(half), p[1] + b[1] * r / math.sin(half))
        t0, t1 = (p[0] + u[0] * t, p[1] + u[1] * t), (p[0] + v[0] * t, p[1] + v[1] * t)
        a0, a1 = math.atan2(t0[1] - cen[1], t0[0] - cen[0]), math.atan2(t1[1] - cen[1], t1[0] - cen[0])
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        out += [(cen[0] + r * math.cos(a0 + da * k / n), cen[1] + r * math.sin(a0 + da * k / n)) for k in range(n + 1)]
    return out


def _yz_prism(pts, x0, x1):
    """Polygon in (y, z) extruded along +x from x0 to x1."""
    with BuildPart() as bp:
        with BuildSketch(Plane.YZ.offset(x0)):
            Polygon(*pts, align=None)
        extrude(amount=x1 - x0)
    return bp.part


def _xz_prism(pts, y0, y1):
    """Polygon in (x, z) extruded along y from y0 to y1."""
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ.offset(-y1)):   # Plane.XZ's normal is -y: sketch on y = y1, extrude to y0
            Polygon(*pts, align=None)
        extrude(amount=y1 - y0)
    return bp.part


def front_openings():
    """Slots A and B, the pinion pass-through and the sliver cut-backs, as (y, z) outlines."""
    h = ZA1 - ZA0
    slot_a = _round([(-HALF_Y - 1, ZA0), (SLOT_A_END, ZA0), (SLOT_A_END + h / 2, (ZA0 + ZA1) / 2), (SLOT_A_END, ZA1),
                     (-HALF_Y - 1, ZA1)], {2}, APEX_R)
    slot_a = _round(slot_a, {len(slot_a) - 2}, SLOT_FILLET)     # roof meets the top wall: r 2 (Kt)
    slot_b = _round([(-SLOT_B_END, ZB0), (HALF_Y + 1, ZB0), (HALF_Y + 1, ZB1), (-SLOT_B_END, ZB1)], {0}, SLOT_FILLET)
    k = R_PASS / math.sqrt(2)
    tear = _round([(0.0, ZS + k), (k, ZS + k), (2 * k, ZS), (k, ZS - k), (0.0, ZS - k)], {2}, APEX_R)
    cres_a = [(-CRESCENT_Y, ZS + Z_CRES), (SLOT_A_END, ZS + Z_CRES), (SLOT_A_END, ZA0 + 0.01), (-CRESCENT_Y, ZA0 + 0.01)]
    cres_b = [(-SLOT_B_END, ZB1 - 0.01), (CRESCENT_Y, ZB1 - 0.01), (CRESCENT_Y, ZS - Z_CRES), (-SLOT_B_END, ZS - Z_CRES)]
    return slot_a, slot_b, tear, cres_a, cres_b


def design():
    c = _box(TOP_X0, X_F1, -HALF_Y, HALF_Y, Z_TOP0, Z_TOP1)                     # top wall
    c += _box(X_F0, X_F1, -HALF_Y, HALF_Y, FRONT_Z0, Z_TOP0 + 0.01)              # front plate (down to z -4)
    c += _box(RAIL_X0, RAIL_X1, -HALF_Y, HALF_Y, ZS + RAIL_IN, Z_TOP0 + 0.01)    # upper lip: 4 mm wall behind rack A
    # tie between the two halves of the front plate (see claw_frame.py): post behind the racks + web between them
    c += _box(TIE_X0, RAIL_X1 + 0.01, TIE_Y[0], TIE_Y[1], ZS - TIE_Z, ZS + RAIL_IN + 0.01)
    c += _box(RAIL_X1, X_F0 + 0.01, TIE_Y[0], TIE_Y[1], ZS - TIE_Z, ZS + TIE_Z)
    # r 2 fillet in the inner corner front plate / top wall, beyond slot A's roof
    r = CORNER_FILLET
    arc = [(X_F0 - r + r * math.cos(t), Z_TOP0 - r + r * math.sin(t))
           for t in [math.pi / 2 - k * (math.pi / 2) / 12 for k in range(13)]]   # (X_F0-r, Z_TOP0) -> (X_F0, Z_TOP0-r)
    c += _xz_prism([(X_F0 + 0.01, Z_TOP0 + 0.01), (arc[0][0], Z_TOP0 + 0.01)] + arc + [(X_F0 + 0.01, arc[-1][1])],
                   CORNER_FILLET_Y0, HALF_Y)
    # 45° chamfer on the top-front outer edge (the camera looks over it)
    ch = TOP_CHAMFER
    c -= _xz_prism([(X_F1 - ch, Z_TOP1 + 0.01), (X_F1 + 0.01, Z_TOP1 + 0.01), (X_F1 + 0.01, Z_TOP1 - ch)],
                   -HALF_Y - 1, HALF_Y + 1)
    # openings through the front plate, cut BEFORE the bed chamfer (DFM fix 2)
    slot_a, slot_b, tear, cres_a, cres_b = front_openings()
    cut = _yz_prism(slot_a, X_F0 - 0.01, X_F1 + 1) + _yz_prism(slot_b, X_F0 - 0.01, X_F1 + 1)
    cut += _yz_prism(tear, X_F0 - 0.01, X_F1 + 1) + _yz_prism(cres_a, X_F0 - 0.01, X_F1 + 1)
    cut += _yz_prism(cres_b, X_F0 - 0.01, X_F1 + 1)
    with BuildPart() as bp:
        with BuildSketch(Plane.YZ.offset(X_F0 - 0.01)):
            with Locations((0, ZS)):
                Circle(R_PASS)
        extrude(amount=X_F1 - X_F0 + 1.01)
    cut += bp.part
    c -= cut
    # bed chamfer on the -y end (done in print orientation, then turned back)
    c = TO_PRINT.inverse() * chamfer_plane_edges(TO_PRINT * c, -HALF_Y, BED_CHAMFER)
    # screw holes: teardrops pointing +y (up in print)
    d = M3_CLEAR + HOLE_COMP
    for (x, y) in TOP_SCREWS:
        c -= Pos(x, y, Z_TOP0 - 1) * _teardrop_z(d, Z_TOP1 - Z_TOP0 + 2, "+y")
    d = M25_CLEAR + HOLE_COMP
    for (y, z) in FRONT_SCREWS:
        c -= Pos(X_F0 - 1, y, z) * Rot(0, 90, 0) * _teardrop_z(d, X_F1 - X_F0 + 2, "+y")
    return c


def build():
    return to_bed(TO_PRINT * design())

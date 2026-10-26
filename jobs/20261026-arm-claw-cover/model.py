"""Claw cover: front plate + top wall + upper lip. It closes the two rack channels, carries the
finger slots and lets the pinion through. Printed standing on its -y end (the side profile on
the bed, every channel face a vertical wall).

Design frame = claw frame G (../20261025-robot-arm-assembly/claw_frame.py). Rack A (upper)
runs between the lip (behind it), the top wall (above it, its back face riding there), the front
plate (in front of it) and the pinion (below it). Rack B rides on the frame's wrist plate,
between the frame's lower rail and this front plate. Each jaw's neck passes through a slot in
the front plate: slot A (upper) is open at the -y end, slot B (lower) at the +y end, so the jaws
slide in from the ends after the cover is screwed on.

Round 6 (cover round 5 independent review: as printed, the ridge's flanks, the foot's flats on the rail block and the
ridge's tip on the groove's closed first layer all stopped the cover at once, so the ridge's x play was set by print
tolerances, 0.08 mm RSS / 0.13 worst case, against 0.04 allowed): ridge-first contact. VSEAT_CLR 0 (claw_frame.py):
the ridge is the groove's own V, virtual apex 16.95. The foot's flats are decoupled from it and raised: TIE2_FOOT_Z =
ZS - RAIL_IN + FOOT_CLR = 18.05, and the ridge's 45° flanks run on up to them (base x 14.15..16.35, 2.2 wide: 0.2 behind
the post's back face and 0.2 from the anchor hole). RIDGE_TIP_Z 17.35, absolute (0.8 wide, 0.15 over the groove's
closed first layer). The frame's bulkhead top drops to 48.45 (BULK_TOP, frame only); this part's top wall stays at 48.5.

Round 5 (cover strength round 4: the anchor held the post's foot in x only by the preload's friction, against
fdm-design-rules §4; with the preload gone the top wall fell to SF 1.37): a 90° V-ridge under the post's foot sits in a
matching groove in the frame's rail block (0.1 clear per flank), so the foot is held in x by geometry and the M3 x 45 only
holds the flank's lift in tension. The foot's flats rise 0.1 (TIE2_FOOT_Z 17.85). A Ø7 x 0.5 washer goes under the
M3 x 45's head (BUILD_GUIDE).

Round 4 (claw strength round 3: the reversed rack-B push, opening stall or crash on jaw B, left the cover only through
the 3 mm top wall behind the lip, SF 1.23): the second tie's post is 8 thick (x 14.35..22.35), reaches down to the
frame's rail block (z 17.75) and is anchored there by one vertical M3 x 45 through the top wall, the lip and the post
(Ø3.6 hole at ANCHOR_XY (18.35, 28), a teardrop pointing +y in print).

Round 3 (claw DFM + strength round 2):
- lip 4 -> 8 thick (GUIDE_T 8, x 14.35..22.35), and the first tie's post with it;
- a second tie (post + web) at y 24..32 joins the upper piece to the lip (strength change 2); it is at the top of the
  print, so its undersides are 45° slopes from the lip and the front plate (second_tie());
- front plate down to z -6 (strength change 3: the strip under slot B 11.75 deep);
- the front plate cut by slot A, the pass-through and slot B leaves two pieces of the upper half that start in mid-air
  in print (DFM fix 1): build() adds a breakaway support pillar under each (supports()); design() is the cover as
  fitted, without them;
- FACE_W 12: the front plate is at x 34.85..39.85.

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

from build123d import Align, Box, BuildPart, BuildSketch, Circle, Keep, Locations, Plane, Polygon, Pos, Rot, extrude, split
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261025-robot-arm-assembly"))
from claw_frame import (ACCESS_D, ANCHOR_XY, CORNER_FILLET, CORNER_FILLET_Y0, CRESCENT_Y, FRONT_SCREWS, FRONT_Z0, HALF_Y, LIP_X0,  # noqa: E402
                        M3_CLEAR, M25_CLEAR, NECK_Z, RAIL_IN, RAIL_X1, SLOT_A_END, SLOT_B_END, SLOT_CLR, SLOT_FILLET,
                        TIE2_Y, TIE_X0, TIE_Y, TIE_Z, TOP_CHAMFER, TOP_SCREWS, TOP_X0, VSEAT_CLR, VSEAT_D, VSEAT_XC,
                        X_F0, X_F1, Z_TOP0, Z_TOP1, ZS)

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
# Breakaway support pillars (DFM fix 1). The pass-through (r 11.4 CAD for the pinion's r 10.85 tips) is wider than the
# necks' inner faces (r 11.25), so it must break into both slots, and slot A opens at the bed (-y) and slot B at the top
# (+y): the plate between the pass-through and each slot, above those breaks in print, can only start on support.
# Each pillar stands on the lower half below its piece and stops SUP_GAP short of it; snap both off before assembly.
SUP_X = (X_F0 + 0.5, X_F1 - 0.5)             # 4 mm along x, 0.5 in from both plate faces
SUP_A = (-8.0, SLOT_A_END, ZA0 - 1.45, ZA0 - 0.15)      # y from, piece starts at y, z 36.8..38.1: under the piece
SUP_B = (-8.0, CRESCENT_Y, ZB1 + 0.2, ZB1 + 1.8)        # beside slot A's end / beside slot B (z 16.45..18.05, 1.6
                                                        # thick, from y -8 where the plate is solid to z 19.13: carries
                                                        # piece (b)'s whole first layer; claw DFM round 3 fix 1)
SUP_GAP = 0.25                               # one layer (0.2) and a bit, under each piece
TIE2_POST_T = 8.0              # second tie's post, x 14.35..22.35 like the first tie's (claw strength round 3: 4 -> 8)
FOOT_CLR = 0.30                # the post's foot flats over the frame's CAD rail block top (17.75), round 6 (cover round 5
                               # review): the block prints at 17.8, so 0.25 as printed; the ridge, never the flats, stops
                               # the cover (round 5: 0.1, tied to VSEAT_CLR)
TIE2_FOOT_Z = ZS - RAIL_IN + FOOT_CLR   # 18.05: the post's foot flats (y 24..32); independent of VSEAT_CLR (round 5 17.85,
                                        # round 4 17.75, round 3 19.25); the ridge below them locates
# V-ridge under the post's foot (round 5, cover strength round 4; VSEAT_* in claw_frame.py): the frame groove's 90° V
# raised VSEAT_CLR (round 6: 0, its flanks line to line with the groove's in CAD), virtual apex z 16.95. Its 45° flanks
# run on up to the flats (z 18.05): base x 14.15..16.35, 2.2 wide, 0.2 behind the post's back face (x 14.35) and 0.2 from
# the anchor hole's edge (x 16.55). In print (G +y up) it is a vertical prism, its start a 45° lead-in that continues
# the post's underside. The tip is cut flat at RIDGE_TIP_Z: the groove's bottom 0.25 (z 16.95..17.2, a 0.3 mm slot at its
# first layer) will not print open in the frame, so a full-height ridge would bottom there and hold the cover up.
RIDGE_APEX_Z = ZS - RAIL_IN - VSEAT_D + VSEAT_CLR   # 16.95: virtual apex (= the groove's bottom with VSEAT_CLR 0)
RIDGE_TIP_Z = 17.35            # absolute (round 6): flat tip 0.8 wide, 0.15 over the groove's closed first layer (17.2)


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


def _halfspace(part, origin, normal):
    """The part's portion on the side of the plane (origin, normal) that the normal points into."""
    return split(part, bisect_by=Plane(origin=origin, z_dir=normal), keep=Keep.TOP)


def second_tie():
    """Post + web at y TIE2_Y joining the upper piece to the lip, between the racks (|z - ZS| <= TIE_Z) and outside
    the pinion. Printed at the top of the part (G +y up), so each underside is a 45° slope: the post grows from the lip
    (full depth at y >= TIE2_Y[0]); the web grows from the post (its back) and from the front plate (its front), whose
    material starts just above the pass-through's 45° teardrop flanks (apex y 2k = 16.12)."""
    z0, z1, zp = ZS - TIE_Z, ZS + TIE_Z, ZS + RAIL_IN           # 19.25, 35.25, 36.75 (the post meets the lip)
    yp = TIE2_Y[0] - (zp - z0)                                  # 6.5: where the web's growth from the post starts
    zf = TIE2_FOOT_Z                                            # 18.05: the post's foot flats, 0.3 over the rail block
    yf = TIE2_Y[0] - (zp - zf)                                  # 5.3: the post's 45° underside meets the lip here
    post = _yz_prism([(yf - 0.01, zp + 0.01), (HALF_Y, zp + 0.01), (HALF_Y, zf), (TIE2_Y[0], zf)], RAIL_X1 - TIE2_POST_T,
                     RAIL_X1 + 0.01)
    post += ridge()
    web = _box(RAIL_X1, X_F0 + 0.01, yp, HALF_Y, z0, z1)
    s2 = math.sqrt(0.5)
    k2 = 2 * R_PASS / math.sqrt(2)                              # 16.12: teardrop apex
    # from the post: y >= yp + (zp - z) + (x - RAIL_X1)
    from_post = _halfspace(web, (RAIL_X1, yp, zp), (-1, 1, 1))
    # from the front plate: y >= k2 - |z - ZS| + (X_F0 - x), one half-space per flank
    from_plate = (_halfspace(web, (X_F0, k2, ZS), (1, 1, 1)) + _halfspace(web, (X_F0, k2, ZS), (1, 1, -1)))
    return post + from_post + from_plate


def ridge():
    """The V-ridge under the second post's foot (round 5; round 6: VSEAT_CLR 0, flanks up to the flats at 18.05): the
    frame groove's 90° V raised VSEAT_CLR, cut flat at RIDGE_TIP_Z, along y from the foot's start to the cover's +y
    end. Its -y end is the post's 45° underside carried on down (y + z >= TIE2_Y[0] + TIE2_FOOT_Z), so in print it
    starts with a 45° lead-in over y 24..24.7."""
    zf, za, zt = TIE2_FOOT_Z, RIDGE_APEX_Z, RIDGE_TIP_Z
    top = zf + 0.01                                             # 0.01 into the post
    pts = [(VSEAT_XC - (top - za), top), (VSEAT_XC + (top - za), top), (VSEAT_XC + (zt - za), zt),
           (VSEAT_XC - (zt - za), zt)]
    r = _xz_prism(pts, TIE2_Y[0] - 1.0, HALF_Y)
    return _halfspace(r, (VSEAT_XC, TIE2_Y[0], zf), (0, 1, 1))


def supports():
    """Breakaway pillars under the two pieces that would start in mid-air (see SUP_A / SUP_B)."""
    out = None
    for y0, y_piece, z0, z1 in (SUP_A, SUP_B):
        pil = _box(SUP_X[0], SUP_X[1], y0, y_piece - SUP_GAP, z0, z1)
        out = pil if out is None else out + pil
    return out


def design():
    c = _box(TOP_X0, X_F1, -HALF_Y, HALF_Y, Z_TOP0, Z_TOP1)                     # top wall
    c += _box(X_F0, X_F1, -HALF_Y, HALF_Y, FRONT_Z0, Z_TOP0 + 0.01)              # front plate (down to z -4)
    c += _box(LIP_X0, RAIL_X1, -HALF_Y, HALF_Y, ZS + RAIL_IN, Z_TOP0 + 0.01)     # upper lip: 8 mm wall behind rack A
    # tie between the two halves of the front plate (see claw_frame.py): post behind the racks + web between them
    c += _box(TIE_X0, RAIL_X1 + 0.01, TIE_Y[0], TIE_Y[1], ZS - TIE_Z, ZS + RAIL_IN + 0.01)
    c += _box(RAIL_X1, X_F0 + 0.01, TIE_Y[0], TIE_Y[1], ZS - TIE_Z, ZS + TIE_Z)
    c += second_tie()
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
    # anchor M3 x 45 (round 4): down through the top wall, the lip and the second tie's post to the rail block
    d = M3_CLEAR + HOLE_COMP
    c -= Pos(ANCHOR_XY[0], ANCHOR_XY[1], TIE2_FOOT_Z) * _teardrop_z(d, Z_TOP1 - TIE2_FOOT_Z, "+y")
    return c


def build():
    """As printed: the cover plus its two breakaway support pillars."""
    return to_bed(TO_PRINT * (design() + supports()))

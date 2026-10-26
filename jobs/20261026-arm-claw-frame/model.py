"""Claw frame: wrist plate on the wrist MG90S horn, bulkhead holding the claw MG90S with its
shaft along +x, and the lower rail behind rack B. Printed wrist plate down (back face on the bed).

Design frame = claw frame G (see ../20261025-robot-arm-assembly/claw_frame.py): origin on the
wrist axis at the back face, +x to the fingertips, +z outboard. The wrist horn sits 2 mm deep in
the back-face pocket, clamped by an M2 x 12 + Ø6 washer from the pad's front face at (0, 0)
(floor 6.3 mm: the screw reaches 4.6 mm into the spline). The claw servo goes in from the FRONT,
case bottom first, its lead through the window's notch; its tabs rest on the bulkhead's front
face (x = 10) with the shaft on the claw axis (y 0, z ZS). Rack B rides on the wrist plate's top
face, backed by the lower rail. The cover screws on top (2 x M3 into the bulkhead top) and at
the front (2 x M2.5 into the wrist plate's front edge).

Round 7 (cover + frame round 6 independent review: at their snug preload the cover's bare M3 x 10 heads, their pull-out
from the bulkhead and the bare front M2.5 heads failed SF 4): hardware, plus the front pilots 0.5 lower. The cover's top
screws become M3 x 14 pan heads + Ø7 x 0.5 washers (10.5 engaged below the printed bulkhead; tip z 38.0 in the unchanged
14 mm pilots, floor 34.45). FRONT_SCREWS z 3 -> 2.5 (claw_frame.py) so the cover's new Ø6 x 0.5 washers under the M2.5
heads clear jaw B's neck: the flat-topped front pilots follow, keeping 2.4 to rack B's track (1.9 before) and 1.4 to the
back face. Nothing else changes.

Round 6 (frame round 5 independent review: the bulkhead top, z 48.5, lay exactly on the slice plane of layer 48.4..48.6
and printed at 48.4 by floating-point rounding): the bulkhead and its two ribs stop at BULK_TOP 48.45 (claw_frame.py).
They print at 48.4 as before, now with 0.05 to the slice planes on both sides. The cover's top wall stays at 48.5, so
it stands 0.05 over the bulkhead in CAD; the cover now rests on its ridge in the V-groove (ridge-first contact, VSEAT_CLR
0). The two M3 pilots keep their 14 mm depth below the new top (their floor moves down 0.05 with it). Nothing
else changes.

Round 5 (cover strength round 4: the anchor held the post's foot in x only by preload friction): a 90° V-groove, 0.8
deep, along y in the rail block's top (x 14.45..16.05 at z 17.75, y 23.5..32, open at +y); the cover's post has the
matching ridge, so the foot is held in x by geometry and the M3 x 45 only holds the flank's lift. 0.95 mm of block stays
between the groove and the anchor pilot at the top. The pilot is unchanged.

Round 4 (claw strength round 3, the cover's required fix): one Ø2.5 printed (Ø2.7 CAD) x 14 M3 pilot, vertical, in
the rail block's top at ANCHOR_XY (18.35, 28) for the M3 x 45 that anchors the cover's second-tie post on the block.
It is 2.65 mm from the block's front face and its +y end; the block's rack-side root keeps SF 5.93 (frame strength).

Round 3 (claw DFM + strength round 2):
- the rail behind rack B is a block from the bulkhead's front face (x 10..22.35), not a 4 mm wall: its root gave
  SF 0.65 under one jaw blocked (strength fix 1); RAIL_X0 = X_B in claw_frame.py;
- the lead notch has a 45° top, as the turntable's _notch_tops() (DFM fix 1);
- the wrist clamp takes an Ø8 x 0.8 washer (strength fix 2): a Ø9 vertical relief in the bulkhead's back face lets
  it down past the bulkhead (1.0 mm deep, |y| <= 2.9);
- r 1.5 fillet where the pad meets the bulkhead's back face (strength fix 3);
- two 6 x 10 mm ribs behind the bulkhead's outer edges (y +-26..32, x -6.5..3.5, pad to bulkhead top) carry the
  camera's USB-tug moment past the window strips (strength fix 4);
- the wrist plate reaches the cover's front plate at x 34.85 (FACE_W 12).

Round 2 (claw DFM + strength round 1, deep review 01 B1/B2):
- wrist plate full width behind the bulkhead (no 20 mm tail) with a 2.3 mm raised pad there;
- MG90S window for the real MG90S (22.8 x 12.2): lead notch at the shaft end, that end's tab pilot
  moved 1.3 mm out (lead="notch_shift_pilot"; file that tab's slit to 2.1 mm);
- window roof 7 mm (bridge 9.2), Ø3 teardrop reliefs at the window's lower corners;
- front pilots flat-topped (1.9 mm skin under rack B's track) and sized for M2.5;
- bulkhead 6.5 thick (1.9 mm walls beside the top pilots);
- the lower rail is a 4 mm wall (x 18.35..22.35) with an r 2 root fillet behind it, not a block back to
  the bulkhead: 8 g less at the end of the arm.
"""
import sys
from pathlib import Path

import math

from build123d import Align, Box, BuildPart, BuildSketch, Cylinder, Location, Plane, Polygon, Pos, extrude
from cadlib import HOLE_COMP_DEFAULT, teardrop_cutter, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261025-robot-arm-assembly"))
from claw_frame import (ANCHOR_PILOT_DEPTH, ANCHOR_XY, BULK_T, BULK_TOP, FRONT_SCREWS, HALF_Y, M3_PILOT, M25_PILOT,  # noqa: E402
                        PAD_T, RAIL_IN, RAIL_X0, RAIL_X1, SERVO, T_W, TOP_SCREWS, VSEAT_D, VSEAT_XC, VSEAT_Y0,
                        WINDOW_ROOF, WRIST_HORN, WRIST_WASHER_OD, X_B, X_F0, X_REAR, ZS)

from hobby_parts import _body_x0, _teardrop_z, chamfer_plane_edges, horn_pocket_cutter, servo_mount_cutter  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT  # +0.2 on hole diameters (default, fdm-design-rules)
CLR, END_CLR = 0.4, 0.2        # MG90S window side / end clearance (printed): 23.0 x 12.6 printed, 23.2 x 12.8 CAD
TOP_PILOT_DEPTH = 14.0         # M3 pilots in the bulkhead top, below BULK_TOP (round 7: M3 x 14 + Ø7 x 0.5 washer on the
                               # cover, tip z 38.0, 3.55 above the floor; M3 x 18 button heads with the camera, tip 37.5)
FRONT_PILOT_DEPTH = 14.0       # M2.5 x 16 + Ø6 x 0.5 washer through the cover's 5 mm front plate: 10.5 mm engaged
                               # (round 7; 11 without the washer; was x 12, 7 engaged: the cover's row 22, SF 2.56 -> 4.0)
BED_CHAMFER = 0.4
RELIEF_D = 3.0                 # teardrop reliefs at the window's lower corners (strength fix 2: Kt 2.5 -> 1.5)
BACK_FILLET = 1.5              # pad top / bulkhead back face, full width (strength fix 3: Kt 2.5 -> 1.7)
WASHER_RELIEF_D = WRIST_WASHER_OD + 2 * 0.4 + HOLE_COMP   # 9.0: the Ø8 washer goes down past the bulkhead's back face
RIB_W, RIB_D = 6.0, 10.0       # ribs behind the bulkhead's outer edges: y +-(26..32), x -6.5..3.5 (strength fix 4)
# V-groove for the cover's post (round 5; VSEAT_* in claw_frame.py): 90°, 0.8 deep, x 14.45..16.05 at the block top,
# y 23.5..32, open at +y. It opens upward in print (45° flanks facing up: no overhang, no bridge). Its bottom 0.25
# (z 16.95..17.2: a 0.3 mm slot at the first layer's mid-height) will not print open; the cover's ridge stops above it.
GROOVE_Y = (VSEAT_Y0, HALF_Y + 1.0)   # through the block's +y end
# claw servo frame in G: shaft along +x at (X_B, 0, ZS); servo +x (long side) along +y,
# servo +y (width) along +z
SERVO_LOC = Location(Plane(origin=(X_B, 0, ZS), x_dir=(0, 1, 0), z_dir=(1, 0, 0)))


def _box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN,) * 3)


def _window_xy():
    """Servo-frame window corners (CAD sizes): x0, x1 along the servo length, half width."""
    c = CLR + HOLE_COMP
    ce = END_CLR + HOLE_COMP
    x0 = _body_x0(SERVO) - ce / 2
    return x0, x0 + SERVO.length + ce, (SERVO.width + c) / 2


def _window_roof():
    """45° shoulders above the servo window (servo frame, +y side = up in print)."""
    x0, x1, hw = _window_xy()
    h = WINDOW_ROOF
    with BuildPart() as bp:
        with BuildSketch(Plane.XY.offset(-BULK_T - 1)):
            Polygon((x0, hw - 0.01), (x1, hw - 0.01), (x1 - h, hw + h), (x0 + h, hw + h), align=None)
        extrude(amount=BULK_T + 2)
    return bp.part


def _corner_reliefs():
    """Ø3 teardrop reliefs centred on the window's two lower corners (servo -y side), point up in print."""
    x0, x1, hw = _window_xy()
    d = RELIEF_D + HOLE_COMP
    return Pos(x0, -hw, -BULK_T) * _teardrop_z(d, BULK_T, "+y") + Pos(x1, -hw, -BULK_T) * _teardrop_z(d, BULK_T, "+y")


def _notch_top():
    """45° top over the lead notch (servo frame; servo +y = G +z = up in print), as the turntable's _notch_tops():
    servo_mount_cutter cuts the notch nw wide from the case end to `reach` beyond it; this adds a right triangle on its
    upper side, so the notch has no flat ceiling (DFM fix 1)."""
    nw = SERVO.lead_notch_w + HOLE_COMP
    reach = SERVO.lead_notch_reach + HOLE_COMP / 2
    xe = SERVO.shaft_from_end                       # the case end at the lead (shaft) end
    # hypotenuse through the notch's top corner (xe + reach, nw / 2): x + y = xe + reach + nw / 2
    tri = [(xe - 0.01, nw / 2 - 0.01), (xe + reach + 0.01, nw / 2 - 0.01), (xe - 0.01, nw / 2 + reach + 0.01)]
    with BuildPart() as bp:
        with BuildSketch(Plane.XY.offset(-BULK_T - 1)):
            Polygon(*tri, align=None)
        extrude(amount=BULK_T + 2)
    return bp.part


def _back_fillet():
    """r BACK_FILLET fillet between the pad's top face and the bulkhead's back face, full width."""
    r, xb, zp = BACK_FILLET, X_B - BULK_T, T_W + PAD_T
    arc = [(xb - r + r * math.sin(t), zp + r - r * math.cos(t)) for t in [k * (math.pi / 2) / 12 for k in range(13)]]
    pts = [(xb + 0.01, zp - 0.01), (xb - r, zp - 0.01)] + arc + [(xb + 0.01, zp + r)]
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ.offset(-HALF_Y)):   # normal -y: sketch on y = HALF_Y, extrude to -HALF_Y
            Polygon(*pts, align=None)
        extrude(amount=2 * HALF_Y)
    return bp.part


def _ribs():
    """RIB_W x RIB_D ribs behind the bulkhead's two outer edges, from the pad's top to the bulkhead's top."""
    xb, z0 = X_B - BULK_T, T_W + PAD_T - 0.01
    return (_box(xb - RIB_D, xb + 0.01, -HALF_Y, -HALF_Y + RIB_W, z0, BULK_TOP)
            + _box(xb - RIB_D, xb + 0.01, HALF_Y - RIB_W, HALF_Y, z0, BULK_TOP))


def _groove():
    """90° V-groove along y in the rail block's top (claw round 5): apex at z_blk - VSEAT_D on x VSEAT_XC, flanks at
    45°, from y VSEAT_Y0 out through the block's +y end. The cutter rises 0.5 over the block top so its mouth is clean."""
    z_blk = ZS - RAIL_IN
    za, h = z_blk - VSEAT_D, VSEAT_D + 0.5
    pts = [(VSEAT_XC, za), (VSEAT_XC + h, za + h), (VSEAT_XC - h, za + h)]
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ.offset(-GROOVE_Y[1])):   # Plane.XZ's normal is -y: sketch on y = y1, extrude to y0
            Polygon(*pts, align=None)
        extrude(amount=GROOVE_Y[1] - GROOVE_Y[0])
    return bp.part


def design():
    plate = _box(X_REAR, X_F0, -HALF_Y, HALF_Y, 0, T_W)                      # full width (strength fix 1)
    plate = chamfer_plane_edges(plate, 0.0, BED_CHAMFER)                     # back face goes on the bed
    f = plate
    f += _box(X_REAR, X_B - BULK_T + 0.01, -HALF_Y, HALF_Y, T_W - 0.01, T_W + PAD_T)   # raised pad (clamp floor)
    f += _box(X_B - BULK_T, X_B, -HALF_Y, HALF_Y, T_W - 0.01, BULK_TOP)         # bulkhead (top 48.45, round 6)
    f += _box(RAIL_X0 - 0.01, RAIL_X1, -HALF_Y, HALF_Y, T_W - 0.01, ZS - RAIL_IN)   # rail block behind rack B
    f += _back_fillet() + _ribs()
    win = servo_mount_cutter(SERVO, BULK_T, clearance=CLR, end_clearance=END_CLR, through=BULK_T * 2 + 2,
                             hole_comp=HOLE_COMP, pilot_teardrop="+y", lead="notch_shift_pilot")
    f -= SERVO_LOC * (win + _window_roof() + _corner_reliefs() + _notch_top())
    # Ø8 clamp washer: vertical relief in the bulkhead's back face (and the fillet) round the clamp axis, pad to top
    # (it starts ON the pad's top face: the washer seat and the 6.3 mm clamp floor stay whole)
    f -= Pos(0, 0, T_W + PAD_T) * Cylinder(WASHER_RELIEF_D / 2, BULK_TOP - T_W - PAD_T + 1.0,
                                           align=(Align.CENTER, Align.CENTER, Align.MIN))
    f -= horn_pocket_cutter(WRIST_HORN, link_t=T_W + PAD_T, hole_comp=HOLE_COMP)   # wrist horn, back face
    d = M3_PILOT + HOLE_COMP
    for (x, y) in TOP_SCREWS:                                                  # cover (+ camera mount) screws
        f -= Pos(x, y, BULK_TOP - TOP_PILOT_DEPTH) * Cylinder(d / 2, TOP_PILOT_DEPTH + 1,
                                                          align=(Align.CENTER, Align.CENTER, Align.MIN))
    d = M3_PILOT + HOLE_COMP                                                   # cover anchor M3 x 45 (round 4):
    z_blk = ZS - RAIL_IN                                                       # vertical in print, so a plain hole
    f -= Pos(ANCHOR_XY[0], ANCHOR_XY[1], z_blk - ANCHOR_PILOT_DEPTH) * Cylinder(
        d / 2, ANCHOR_PILOT_DEPTH + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    f -= _groove()                                                             # V-seat for the cover's post (round 5)
    d = M25_PILOT + HOLE_COMP
    for (y, z) in FRONT_SCREWS:                                                # cover front screws: flat-top teardrops
        td = teardrop_cutter(d, 2 * FRONT_PILOT_DEPTH, axis="X", center=(X_F0, y, z))
        f -= td & _box(X_F0 - FRONT_PILOT_DEPTH - 1, X_F0 + 1, y - d, y + d, z - d, z + d / 2)
    return f


def build():
    return to_bed(design())

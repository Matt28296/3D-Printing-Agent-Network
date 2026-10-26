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

from build123d import Align, Box, BuildPart, BuildSketch, Cylinder, Location, Plane, Polygon, Pos, extrude
from cadlib import HOLE_COMP_DEFAULT, teardrop_cutter, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261025-robot-arm-assembly"))
from claw_frame import (BULK_T, FRONT_SCREWS, HALF_Y, M3_PILOT, M25_PILOT, PAD_T, RAIL_IN, RAIL_X0,  # noqa: E402
                        RAIL_X1, SERVO, T_W, TOP_SCREWS, WINDOW_ROOF, WRIST_HORN, X_B, X_F0, X_REAR, Z_TOP0, ZS)

from hobby_parts import _body_x0, _teardrop_z, chamfer_plane_edges, horn_pocket_cutter, servo_mount_cutter  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT  # +0.2 on hole diameters (default, fdm-design-rules)
CLR, END_CLR = 0.4, 0.2        # MG90S window side / end clearance (printed): 23.0 x 12.6 printed, 23.2 x 12.8 CAD
TOP_PILOT_DEPTH = 14.0         # M3 pilots in the bulkhead top (M3 x 10 cover, M3 x 18 with the camera)
FRONT_PILOT_DEPTH = 10.0       # M2.5 x 12 through the cover's 5 mm front plate: 7 mm engaged
BED_CHAMFER = 0.4
RELIEF_D = 3.0                 # teardrop reliefs at the window's lower corners (strength fix 2: Kt 2.5 -> 1.5)
RAIL_FILLET = 2.0              # rail wall's back face / wrist plate top
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


def _rail_fillet():
    """r 2 fillet between the wrist plate's top face and the rail wall's back face, full width (the
    front face carries rack B's sliding fit, so it keeps a sharp corner)."""
    import math
    r, x0 = RAIL_FILLET, RAIL_X0
    arc = [(x0 - r + r * math.sin(t), T_W + r - r * math.cos(t)) for t in [k * (math.pi / 2) / 12 for k in range(13)]]
    pts = [(x0 + 0.01, T_W - 0.01), (x0 - r, T_W - 0.01)] + arc + [(x0 + 0.01, T_W + r)]
    with BuildPart() as bp:
        with BuildSketch(Plane.XZ.offset(-HALF_Y)):   # normal -y: sketch on y = HALF_Y, extrude to -HALF_Y
            Polygon(*pts, align=None)
        extrude(amount=2 * HALF_Y)
    return bp.part


def design():
    plate = _box(X_REAR, X_F0, -HALF_Y, HALF_Y, 0, T_W)                      # full width (strength fix 1)
    plate = chamfer_plane_edges(plate, 0.0, BED_CHAMFER)                     # back face goes on the bed
    f = plate
    f += _box(X_REAR, X_B - BULK_T + 0.01, -HALF_Y, HALF_Y, T_W - 0.01, T_W + PAD_T)   # raised pad (clamp floor)
    f += _box(X_B - BULK_T, X_B, -HALF_Y, HALF_Y, T_W - 0.01, Z_TOP0)           # bulkhead
    f += _box(RAIL_X0, RAIL_X1, -HALF_Y, HALF_Y, T_W - 0.01, ZS - RAIL_IN)      # lower rail wall (behind rack B)
    f += _rail_fillet()
    win = servo_mount_cutter(SERVO, BULK_T, clearance=CLR, end_clearance=END_CLR, through=BULK_T * 2 + 2,
                             hole_comp=HOLE_COMP, pilot_teardrop="+y", lead="notch_shift_pilot")
    f -= SERVO_LOC * (win + _window_roof() + _corner_reliefs())
    f -= horn_pocket_cutter(WRIST_HORN, link_t=T_W + PAD_T, hole_comp=HOLE_COMP)   # wrist horn, back face
    d = M3_PILOT + HOLE_COMP
    for (x, y) in TOP_SCREWS:                                                  # cover (+ camera mount) screws
        f -= Pos(x, y, Z_TOP0 - TOP_PILOT_DEPTH) * Cylinder(d / 2, TOP_PILOT_DEPTH + 1,
                                                          align=(Align.CENTER, Align.CENTER, Align.MIN))
    d = M25_PILOT + HOLE_COMP
    for (y, z) in FRONT_SCREWS:                                                # cover front screws: flat-top teardrops
        td = teardrop_cutter(d, 2 * FRONT_PILOT_DEPTH, axis="X", center=(X_F0, y, z))
        f -= td & _box(X_F0 - FRONT_PILOT_DEPTH - 1, X_F0 + 1, y - d, y + d, z - d, z + d / 2)
    return f


def build():
    return to_bed(design())

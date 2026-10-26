"""Drive sprocket (×2): 10 teeth, bolted with 4 × M3 to a Pololu #1996 aluminium hub that is
clamped to the N20's D-shaft by its own M3 set screw. Identical both sides.

Sprocket frame: axis = +Z pointing AWAY from the chassis, origin on the axis at the track centre
plane (world Y = ±55). The toothed disc spans z ±3.5. Round 3: the torque path is metal from the
shaft to the sprocket (strength round 2: no printed bore can carry the stall torque, and no
printed hub section may have a radial hole). The disc's inner face seats directly on the hub's
outer face (world Y 51.5): the motor sits 45° rolled in a nacelle that reaches into the track's
wrap, so the hub is already at the disc and no printed tube is needed. The four M3 holes are
short radial slots, because the hub's hole circle is not confirmed (drawing value r 6.35): they
take any circle from r 5.5 to 6.85. The shaft end (world Y 54 or 55 for a 9 or 10 mm shaft) runs
free in a Ø3.4 printed (Ø3.6 CAD) centre hole. No set screw and no D-bore in the print.
The idler (20261026-rover-idler) runs this model with BORE = "round": the same disc and teeth on a
Ø10 hub with a round running bore on its M3 bolt.
Teeth sit at k·36° (mid-way between pins when pins sit at 18° + k·36°), with 45° root chamfers that
start on the disc circle. Printed outer disc face down (the idler's hub up).
"""
import math
import sys
from pathlib import Path

from build123d import Align, BuildPart, BuildSketch, Cylinder, Plane, Polygon, Pos, Rot, extrude
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-rover-assembly"))
from rover_frame import (CHORD_IN, DISC_HALF, HALF_W_OUT, HUB, HUB_D, HUB_GAP, HUB_Y1, LINK_T, N_TEETH,  # noqa: E402
                         Y_T)

from hobby_parts import chamfer_plane_edges  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT         # +0.2 on hole diameters (fdm-design-rules default; no library row)
# DISC_HALF 3.5 (rover_frame): tooth/disc half width (link notch is ±4)
DISC_R = CHORD_IN - 0.5               # 11.9: under the links' inner faces
TOOTH_TIP_R = CHORD_IN + LINK_T - 0.5 # 17.9: stays inside the link (outer face 18.4)
TOOTH_BASE_W, TOOTH_TIP_W = 2.7, 1.6  # tangential width (gap between knuckles is ~3.9); assembly check round 1
ROOT_CHAMFER = 0.5                    # 45° chamfer at each tooth root (DFM/strength round 1)
PHASE_DEG = 0.0
BORE = "hub"                          # "hub" = drive sprocket on the metal hub; "round" = idler on an M3 bolt
# drive sprocket on the hub (rover_frame: hub outer face at world Y 51.5 = HUB_Y1 = the disc's inner face)
HUB_FACE_Z = HUB_Y1 - Y_T             # -3.5: the disc's inner face seats on the hub
assert abs(HUB_FACE_Z + DISC_HALF) < 1e-9
HUB_SCREW_D = 3.4                     # M3 clearance (printed)
SLOT_R = HUB.bolt_circle_r_range      # (5.5, 6.85): radial slots take any hole circle in this range
SLOT_ANGLE0 = 45.0                    # slot angles 45° + k·90°
SHAFT_CLEAR_D = HUB.bore + 0.4        # Ø3.4 printed centre hole: the shaft end (Y 51.0) runs free
# idler (BORE = "round")
HUB_Z0_ROUND = -(Y_T - (HALF_W_OUT + HUB_GAP))  # -16.5: hub end at the washer outside the wall (idler)
ROUND_BORE = 3.5                      # printed running bore for the idler bolt (0.5 mm running clearance)
BED_CHAMFER = 0.3


def tooth():
    r0, r1, f = DISC_R - 0.5, TOOTH_TIP_R, ROOT_CHAMFER
    b, t = TOOTH_BASE_W / 2, TOOTH_TIP_W / 2
    xr = math.sqrt(DISC_R ** 2 - (b + f) ** 2)       # chamfer starts on the disc circle (DFM round 2, R1)
    pts = [(r0, -b - f), (xr, -b - f), (DISC_R + f, -b), (r1, -t), (r1, t), (DISC_R + f, b), (xr, b + f), (r0, b + f)]
    with BuildPart() as bp:
        with BuildSketch(Plane.XY.offset(-DISC_HALF)):
            Polygon(*pts, align=None)
        extrude(amount=2 * DISC_HALF)
    return bp.part


def _slot(r0, r1, d, ang):
    """Vertical slot through everything, from radius r0 to r1 (hole centres) at angle `ang`."""
    a = math.radians(ang)
    c = None
    for r in (r0, r1):
        h = Pos(r * math.cos(a), r * math.sin(a), -30) * Cylinder(d / 2, 60, align=(Align.CENTER, Align.CENTER, Align.MIN))
        c = h if c is None else c + h
    with BuildPart() as bp:
        with BuildSketch(Plane.XY.offset(-30)):
            Polygon((r0, -d / 2), (r1, -d / 2), (r1, d / 2), (r0, d / 2), align=None)
        extrude(amount=60)
    return c + Rot(0, 0, ang) * bp.part


def design():
    s = Pos(0, 0, -DISC_HALF) * Cylinder(DISC_R, 2 * DISC_HALF, align=(Align.CENTER, Align.CENTER, Align.MIN))
    t = tooth()
    for k in range(N_TEETH):
        s += Rot(0, 0, PHASE_DEG + k * 360.0 / N_TEETH) * t
    s = chamfer_plane_edges(s, DISC_HALF, BED_CHAMFER)          # outer face goes on the bed
    if BORE == "hub":
        for k in range(HUB.n_holes):
            s -= _slot(SLOT_R[0], SLOT_R[1], HUB_SCREW_D + HOLE_COMP, SLOT_ANGLE0 + k * 360.0 / HUB.n_holes)
        s -= Pos(0, 0, -30) * Cylinder((SHAFT_CLEAR_D + HOLE_COMP) / 2, 60, align=(Align.CENTER, Align.CENTER, Align.MIN))
    else:
        s += Pos(0, 0, HUB_Z0_ROUND) * Cylinder(HUB_D / 2, -DISC_HALF - HUB_Z0_ROUND + 0.01,
                                                align=(Align.CENTER, Align.CENTER, Align.MIN))
        s -= Pos(0, 0, HUB_Z0_ROUND - 1) * Cylinder((ROUND_BORE + HOLE_COMP) / 2, 40, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return s


def build():
    return to_bed(Rot(180, 0, 0) * design())    # outer disc face on the bed (idler: hub up)

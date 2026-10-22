"""Cookbook: flat mounting plate with heat-set insert bosses, a rib and a captive nut.

Printed flat (as modelled): bosses grow straight up, insert holes are vertical
(no support), the rib stiffens the plate along X, and the nut pocket is
open to the top so the nut drops in. Copy to jobs/<id>/model.py and adapt.
"""
from build123d import Align, Axis, Box, Cylinder, Pos, fillet
from cadlib import chamfer_bottom, comp, hex_nut_pocket, vertical_hole_cutter

# --- parameters (mm) -----------------------------------------------------------
L, W, T = 60.0, 40.0, 4.0          # plate; 4 mm ≈ 20 layers at 0.2
BOSS_D, BOSS_H = 8.0, 8.0          # boss Ø ≥ 2 × insert OD (design-rules §4)
INSERT_HOLE_D = 4.1                # brass M3 insert: use the insert maker's hole size, no HOLE_COMP
INSERT_DEPTH = 6.0
BOSS_XY = [(8, 8), (52, 8), (8, 32), (52, 32)]
RIB_W, RIB_H = 3.0, 6.0            # rib along X, centred on Y
NUT_AF, NUT_T = 5.5, 2.6           # M3 nut, across flats and thickness
NUT_XY = (30.0, 8.0)
SCREW_D = 3.4                      # M3 clearance
HOLE_COMP = 0.2                    # default; replace with library/materials.csv hole_comp_mm
BOTTOM_CHAMFER = 0.4


def build():
    part = Box(L, W, T, align=(Align.MIN, Align.MIN, Align.MIN))
    for x, y in BOSS_XY:
        part += Pos(x, y, 0) * Cylinder(BOSS_D / 2, T + BOSS_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    part += Pos(BOSS_D, W / 2 - RIB_W / 2, 0) * Box(L - 2 * BOSS_D, RIB_W, T + RIB_H, align=(Align.MIN,) * 3)
    # soften the plate's vertical outer corners (load-free, cosmetic and handling)
    corners = part.edges().filter_by(Axis.Z).filter_by_position(Axis.Z, 0, T + 0.01)
    corners = [e for e in corners if e.length <= T + 0.01 and
               (abs(e.center().X) < 1e-6 or abs(e.center().X - L) < 1e-6) and
               (abs(e.center().Y) < 1e-6 or abs(e.center().Y - W) < 1e-6)]
    part = fillet(corners, radius=3)
    for x, y in BOSS_XY:
        part -= vertical_hole_cutter(INSERT_HOLE_D, INSERT_DEPTH, top_center=(x, y, T + BOSS_H))
    part -= vertical_hole_cutter(comp(SCREW_D, HOLE_COMP), T, top_center=(NUT_XY[0], NUT_XY[1], T))
    part -= hex_nut_pocket(NUT_AF, NUT_T, bottom_center=(NUT_XY[0], NUT_XY[1], T - NUT_T))
    return chamfer_bottom(part, BOTTOM_CHAMFER)

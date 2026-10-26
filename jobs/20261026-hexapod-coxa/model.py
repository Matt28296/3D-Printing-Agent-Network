"""Hexapod coxa bracket (×6): hangs from the coxa MG90S horn under the body and carries the
femur MG90S, whose axis is horizontal and tangential.

Design frame C (see ../20261026-hexapod-assembly/hex_frame.py): origin on the coxa axis at the
bracket's back face (the coxa horn sits 2 mm deep in a pocket there), x radial outward, z
pointing DOWN in the world, y = z × x. The bracket is an L in plan: a hub round the horn, and an
arm along y in [-18, -6.5] that stays outside the femur's swing plane (y -3.8 … 3.2), out to the
vertical plate that carries the femur servo (tab face at y = Y_F, shaft +y, body horizontal
along x so the window's 45° roof is on its long side).
Printed as modelled: the horizontal plate on the bed (horn pocket on the bed face, bridge < 8 mm),
the vertical plate standing, its window roof pointing up.
"""
import sys
from pathlib import Path

from build123d import Align, Box, BuildPart, BuildSketch, Location, Plane, Polygon, Pos, extrude
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-hexapod-assembly"))
from hex_frame import L_C, SERVO, T_C, T_V, Y_F, Z_F  # noqa: E402

from hobby_parts import chamfer_plane_edges, horn_pocket_cutter, rounded_plate, servo_mount_cutter  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT
CLR, END_CLR = 0.4, 0.2          # femur-servo window side / end clearance (printed)
HUB = (-9.0, 19.0, -18.0, 7.0)   # hub plate round the horn: x0, x1, y0, y1 (horn arm along +x to 16.5)
ARM_Y = (-18.0, -6.5)            # arm stays 2.7 mm outside the femur plane (y >= -3.8)
SHAFT_FROM_END = SERVO.shaft_from_end
PILOT_X = (-(SERVO.length - SERVO.shaft_from_end) + SERVO.length / 2 - SERVO.hole_dx / 2,
           -(SERVO.length - SERVO.shaft_from_end) + SERVO.length / 2 + SERVO.hole_dx / 2)   # -19.4, 8.4
VPLATE_X = (L_C + PILOT_X[0] - 3.5, L_C + PILOT_X[1] + 3.5)    # 9.1 … 43.9
WIN_HALF = (SERVO.width + CLR + HOLE_COMP) / 2                  # 6.4
ROOF = (SERVO.length + END_CLR + HOLE_COMP) / 2                 # 11.45
VPLATE_H = Z_F + WIN_HALF + ROOF + 3.0                          # 33.85
GUSSET = 6.0                     # 45° gussets inside the bracket corner (y > Y_F face is the tab side)
BED_CHAMFER = 0.4


def femur_servo_loc():
    """Femur servo frame in C: x = C x, z = C y (shaft +y), so servo y = C -z (up in print)."""
    return Location(Plane(origin=(L_C, Y_F, Z_F), x_dir=(1, 0, 0), z_dir=(0, 1, 0)))


def design():
    x0, x1, y0, y1 = HUB
    br = rounded_plate(x0, x1, y0, y1, T_C, r=5.0)
    br += rounded_plate(0.0, VPLATE_X[1], ARM_Y[0], ARM_Y[1], T_C, r=3.0)
    br = chamfer_plane_edges(br, 0.0, BED_CHAMFER)
    # vertical plate (normal y) from the arm, at y in [Y_F - T_V, Y_F]
    vp = Pos(VPLATE_X[0], Y_F - T_V, T_C - 0.01) * Box(VPLATE_X[1] - VPLATE_X[0], T_V, VPLATE_H - T_C + 0.01,
                                                        align=(Align.MIN,) * 3)
    br += vp
    # 45° fillet wedges along the plate root on the arm side (y > Y_F), outside the window's x range
    win_x0 = L_C - (SERVO.length - SHAFT_FROM_END) - (END_CLR + HOLE_COMP) / 2
    win_x1 = L_C + SHAFT_FROM_END + (END_CLR + HOLE_COMP) / 2
    for xa, xb in ((VPLATE_X[0] + 3.0, win_x0 - 3.0), (win_x1 + 3.0, VPLATE_X[1] - 3.0)):   # clear of the arm's r3 corners
        if xb - xa > 1:
            with BuildPart() as g:
                with BuildSketch(Plane.YZ.offset(xa)):
                    Polygon((Y_F - 0.01, T_C - 0.01), (min(Y_F + GUSSET, ARM_Y[1]), T_C - 0.01),
                            (Y_F - 0.01, T_C + GUSSET), align=None)
                extrude(amount=xb - xa)
            br += g.part
    br -= horn_pocket_cutter(SERVO, link_t=T_C, hole_comp=HOLE_COMP)
    br -= femur_servo_loc() * servo_mount_cutter(SERVO, T_V, clearance=CLR, end_clearance=END_CLR, roof="-y",
                                                 through=2 * T_V + 2, hole_comp=HOLE_COMP, pilot_teardrop="-y")
    return br


def build():
    return to_bed(design())

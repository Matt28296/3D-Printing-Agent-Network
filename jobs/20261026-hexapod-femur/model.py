"""Hexapod femur (×6): flat plate from the femur MG90S horn to the knee, carrying the tibia MG90S.

Design frame F: origin on the femur axis at the femur's back face (the femur horn sits 2 mm deep
in a pocket there), x along the femur to the knee, z away from the femur servo. The tibia servo
hangs through a window at x = L_F (tabs on the front face z = T_F, shaft +z, body back along the
femur). Body weight bends the femur in its own plane (19 mm deep section). Printed flat, horn
pocket on the bed (bridge < 8 mm).
"""
import sys
from pathlib import Path

from build123d import Pos
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-hexapod-assembly"))
from hex_frame import L_F, SERVO, T_F  # noqa: E402

from hobby_parts import chamfer_plane_edges, horn_pocket_cutter, rounded_plate, servo_mount_cutter  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT
HALF_W = 9.5                     # window ±6.4 + 3.1 mm side walls
X0 = -8.0                        # behind the horn hub
X1 = L_F + 8.4 + 3.5             # 3.5 mm past the outer tibia pilot
CLR, END_CLR = 0.4, 0.2
BED_CHAMFER = 0.4


def design():
    f = rounded_plate(X0, X1, -HALF_W, HALF_W, T_F, r=6.0)
    f = chamfer_plane_edges(f, 0.0, BED_CHAMFER)
    f -= horn_pocket_cutter(SERVO, link_t=T_F, hole_comp=HOLE_COMP)
    f -= Pos(L_F, 0, T_F) * servo_mount_cutter(SERVO, T_F, clearance=CLR, end_clearance=END_CLR,
                                               through=2 * T_F + 2, hole_comp=HOLE_COMP)
    return f


def build():
    return to_bed(design())

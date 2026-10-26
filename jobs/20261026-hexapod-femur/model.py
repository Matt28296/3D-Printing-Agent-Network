"""Hexapod femur (×6): flat plate from the femur MG90S horn to the knee, carrying the tibia MG90S.

Design frame F: origin on the femur axis at the femur's back face (the femur horn sits 2 mm deep
in a pocket there), x along the femur to the knee, z away from the femur servo. Body weight bends
the femur in its own plane (19 mm deep section). Printed flat, horn pocket on the bed (bridge < 8 mm).

Round 3 (deep review 2026-10-26):
  - B1 option 2: the tibia servo is mounted REVERSED: its tabs sit on the femur's BACK face (z = 0, the
    bed face), its upper case and spline go through the window towards the tibia, and its case and
    lead stay behind the femur, so the lead never crosses the plate (servo_mount_cutter lead="none").
    The window and pilots are through-cuts, so they are the same as before; only the servo turns round.
  - B2/S1: the MG90S's own spec (22.8 × 12.2 body): window 23.2 × 12.8 CAD.
  - SYS-5: a tie slot near the horn for the tibia lead.
"""
import sys
from pathlib import Path

from build123d import Align, Box, Location, Plane, Pos
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-hexapod-assembly"))
from hex_frame import L_F, SERVO, T_F, TIBIA_MOUNT  # noqa: E402

from hobby_parts import chamfer_plane_edges, horn_pocket_cutter, rounded_plate, servo_mount_cutter  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT    # +0.2 on every hole and pocket (fdm-design-rules default; no library row)
HALF_W = 9.5                     # window ±6.4 + 3.1 mm side walls
X0 = -8.0                        # behind the horn hub
PILOT_OUT = -(SERVO.length - SERVO.shaft_from_end) + SERVO.length / 2 + SERVO.hole_dx / 2   # 8.4: outer pilot (servo x)
X1 = L_F + PILOT_OUT + 3.5       # 56.9: 3.5 mm past the outer tibia pilot
CLR, END_CLR = 0.4, 0.2
LEAD = "none"                    # B1 option 2: the servo is reversed, its lead never crosses the plate
TIE_SLOT = (3.2, 1.8)            # SYS-5: tibia-lead tie slot (x × y), through the plate
TIE_XY = (20.0, -6.0)            # beyond the horn-arm pocket (ends at x 16.5), 1.8 mm before the tibia servo's tab
BED_CHAMFER = 0.4


def tibia_servo_cutter_loc():
    """Cutter frame for the tibia-servo window: origin on the knee axis on the face the tabs rest on, z
    pointing away from the plate (towards the tabs). Reversed: the back face z = 0, cutter z = -F z."""
    if TIBIA_MOUNT == "reversed":
        return Location(Plane(origin=(L_F, 0, 0), x_dir=(1, 0, 0), z_dir=(0, 0, -1)))
    return Location(Plane(origin=(L_F, 0, T_F), x_dir=(1, 0, 0), z_dir=(0, 0, 1)))


def design():
    f = rounded_plate(X0, X1, -HALF_W, HALF_W, T_F, r=6.0)
    f = chamfer_plane_edges(f, 0.0, BED_CHAMFER)
    f -= horn_pocket_cutter(SERVO, link_t=T_F, hole_comp=HOLE_COMP)
    f -= tibia_servo_cutter_loc() * servo_mount_cutter(SERVO, T_F, clearance=CLR, end_clearance=END_CLR,
                                                       through=2 * T_F + 2, hole_comp=HOLE_COMP, lead=LEAD)
    w, h = TIE_SLOT
    f -= Pos(TIE_XY[0], TIE_XY[1], -1) * Box(w + HOLE_COMP, h + HOLE_COMP, T_F + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return f


def build():
    return to_bed(design())

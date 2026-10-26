"""Hexapod coxa bracket (×6): hangs from the coxa MG90S horn under the body and carries the
femur MG90S, whose axis is horizontal and tangential.

Design frame C (see ../20261026-hexapod-assembly/hex_frame.py): origin on the coxa axis at the
bracket's back face (the coxa horn sits 2 mm deep in a pocket there), x radial outward, z
pointing DOWN in the world, y = z × x. The bracket is an L in plan: a hub round the horn, and an
arm along y in [-23.5, -6.5] that stays outside the femur's swing plane (y -0.9 … 6.1), out to the
vertical plate (y -23.5 … -13.5) that carries the femur servo (tab face at y = Y_F, shaft +y, body
horizontal along x so the window's 45° roof is on its long side).

Round 3 (strength round 1 + deep review 2026-10-26):
  - T_V 10 with 13 mm posts beside the window, T_C 8 (6 mm floor under the horn), a 45° ramp where the
    plate's inner end meets the hub, R1 T-bone reliefs at the window floor, a full-length gusset.
  - B1 option 1: the femur servo goes through the window case first (tabs on the +y face), so its lead
    needs the notch at the window's outboard end; the outboard pilot moves 1.3 mm out and the builder
    files that tab's slit to 2.1 mm (servo_mount_cutter lead="notch_shift_pilot").
  - SYS-5: a tie slot through the outer post, above the pilot row, for the femur and tibia leads.
Printed as modelled: the horizontal plate on the bed (horn pocket on the bed face, bridge < 8 mm),
the vertical plate standing; the window roof, pilot teardrops, reliefs and tie slot point up.
"""
import math
import sys
from pathlib import Path

from build123d import Axis, BuildPart, BuildSketch, Location, Plane, Polygon, extrude, fillet
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-hexapod-assembly"))
from hex_frame import L_C, SERVO, T_C, T_V, Y_F, Z_F  # noqa: E402

from hobby_parts import chamfer_plane_edges, horn_pocket_cutter, rounded_plate, servo_mount_cutter  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT    # +0.2 on every hole and pocket (fdm-design-rules default; no library row)
CLR, END_CLR = 0.4, 0.2          # femur-servo window side / end clearance (printed)
LEAD = "notch_shift_pilot"       # B1 option 1 (deep review 01): lead notch at the outboard end, pilot +1.3 mm
PILOT_X = (-(SERVO.length - SERVO.shaft_from_end) + SERVO.length / 2 - SERVO.hole_dx / 2,
           -(SERVO.length - SERVO.shaft_from_end) + SERVO.length / 2 + SERVO.hole_dx / 2 + 1.3)  # -19.4, 9.7 (servo x):
                                 # tab pilots; the outboard one moved 1.3 mm out by LEAD (hobby_parts pilot_shift)
POST_W = 13.0                    # strength round 1: posts >= 12.5 mm beside the window (out-of-plane bending)
WIN_X = (L_C - (SERVO.length - SERVO.shaft_from_end) - (END_CLR + HOLE_COMP) / 2,
         L_C + SERVO.shaft_from_end + (END_CLR + HOLE_COMP) / 2)               # 14.9 … 38.1 (window in C x)
VPLATE_X = (WIN_X[0] - POST_W, WIN_X[1] + POST_W)                             # 1.9 … 51.1
HUB = (-9.0, 19.0, Y_F - T_V, 7.0)       # hub plate round the horn: x0, x1, y0 (-23.5), y1 (horn arm along +x to 16.5)
HUB_R = 2.0                      # hub corner radius: the ramp's foot (x -6.1) must land on the hub at y -23.5
ARM_Y = (Y_F - T_V, -6.5)        # -23.5 … -6.5: clears the femur plane (y >= -0.9) by 5.6 mm
WIN_HALF = (SERVO.width + CLR + HOLE_COMP) / 2                  # 6.4
ROOF = (SERVO.length + END_CLR + HOLE_COMP) / 2                 # 11.6: 45° roof over the window's long side
VPLATE_H = Z_F + WIN_HALF + ROOF + 3.0                          # 41.0
GUSSET = Z_F - SERVO.width / 2 - 1.0 - T_C   # 4.9: 45° root gusset on the tab side, 1 mm under the femur tabs
RAMP = 8.0                       # strength round 1: 45° ramp >= 8 mm where the plate's inner end meets the hub
RELIEF_D = 2.0                   # DFM round 2 / strength: R1 T-bone reliefs at the window floor's corners
TIE_SLOT = (1.8, 3.2)            # SYS-5 tie slot through the outer post (x × z), with a 45° roof
TIE_XZ = (VPLATE_X[1] - 3.6, Z_F + 10.0)   # (47.5, 30): above the pilot row, where the post carries ~no load
CORNER_CUT = 6.0                 # 45° cut off the plate's outer top corner (print): the reversed tibia servo's case
                                 # passes there when the femur is down at -40…-60° (unloaded corner, above the tie slot)
HUB_ARM_FILLET = 2.5             # re-entrant corner where the arm leaves the hub (DFM round 1)
BED_CHAMFER = 0.4


def femur_servo_loc():
    """Femur servo frame in C: x = C x, z = C y (shaft +y), so servo y = C -z (up in print)."""
    return Location(Plane(origin=(L_C, Y_F, Z_F), x_dir=(1, 0, 0), z_dir=(0, 1, 0)))


def _prism_y(pts_xz, y0, y1):
    """A polygon in the C x-z plane, extruded from y = y0 to y = y1 (y0 < y1)."""
    with BuildPart() as p:
        with BuildSketch(Plane.XZ.offset(-y0)):        # Plane.XZ's normal is -y: offset -y0 puts it at y = y0
            Polygon(*pts_xz, align=None)
        extrude(amount=-(y1 - y0))                      # negative: towards +y
    return p.part


def _teardrop_xz(xc, zc, r, n=24):
    """Circle of radius r at (xc, zc) in the x-z plane with a 45° point towards +z (prints without support)."""
    pts = [(xc + r * math.cos(a), zc + r * math.sin(a))
           for a in (math.radians(135 + 270 * k / n) for k in range(n + 1))]   # 135° round the bottom to 405°
    return pts + [(xc, zc + r * math.sqrt(2))]


def design():
    x0, x1, y0, y1 = HUB
    br = rounded_plate(x0, x1, y0, y1, T_C, r=HUB_R)
    br += rounded_plate(0.0, VPLATE_X[1], ARM_Y[0], ARM_Y[1], T_C, r=0.5)   # far corners squared (DFM round 2)
    corner = [e for e in br.edges().filter_by(Axis.Z)
              if abs(e.center().X - x1) < 0.05 and abs(e.center().Y - ARM_Y[1]) < 0.05]
    br = fillet(corner, radius=HUB_ARM_FILLET)
    br = chamfer_plane_edges(br, 0.0, BED_CHAMFER)
    # vertical plate (normal y), y in [Y_F - T_V, Y_F], with the 45° ramp at its inner end
    br += _prism_y([(VPLATE_X[0] - RAMP, T_C - 0.01), (VPLATE_X[1], T_C - 0.01), (VPLATE_X[1], VPLATE_H - CORNER_CUT),
                    (VPLATE_X[1] - CORNER_CUT, VPLATE_H), (VPLATE_X[0], VPLATE_H), (VPLATE_X[0], T_C + RAMP)],
                   Y_F - T_V, Y_F)
    # 45° root gusset along the whole plate on the tab side (y > Y_F), 1 mm under the femur servo's tabs
    assert Y_F + GUSSET <= ARM_Y[1] and T_C + GUSSET <= Z_F - SERVO.width / 2 - 0.5
    with BuildPart() as g:
        with BuildSketch(Plane.YZ.offset(VPLATE_X[0])):
            Polygon((Y_F - 0.01, T_C - 0.01), (Y_F + GUSSET, T_C - 0.01), (Y_F - 0.01, T_C + GUSSET), align=None)
        extrude(amount=VPLATE_X[1] - VPLATE_X[0])
    br += g.part
    br -= horn_pocket_cutter(SERVO, link_t=T_C, hole_comp=HOLE_COMP)
    br -= femur_servo_loc() * servo_mount_cutter(SERVO, T_V, clearance=CLR, end_clearance=END_CLR, roof="-y",
                                                 through=2 * T_V + 2, hole_comp=HOLE_COMP, pilot_teardrop="-y",
                                                 lead=LEAD)
    # R1 T-bone reliefs: tangent to each post's inner face on the window floor line
    floor, r = Z_F - WIN_HALF, RELIEF_D / 2
    for xc in (WIN_X[0] + r, WIN_X[1] - r):
        br -= _prism_y(_teardrop_xz(xc, floor, r), Y_F - T_V - 1, Y_F + 1)
    # SYS-5 tie slot through the outer post: 1.8 × 3.2 with a 45° roof
    (tx, tz), (w, h) = TIE_XZ, TIE_SLOT
    br -= _prism_y([(tx - w / 2, tz - h / 2), (tx + w / 2, tz - h / 2), (tx + w / 2, tz + h / 2),
                    (tx, tz + h / 2 + w / 2), (tx - w / 2, tz + h / 2)], Y_F - T_V - 1, Y_F + 1)
    return br


def build():
    return to_bed(design())

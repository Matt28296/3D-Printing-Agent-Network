"""Track link (×68 for the rover, 34 per side), joined by 2 mm steel rod pins.

Link frame: rear hinge axis on x = 0, front hinge axis on x = P, both along Y, on the link's
mid-plane z = 0. +z = INNER face (towards the wheels), -z = outer face with the grousers.
Each link has a centre knuckle at its rear hinge (|y| <= 6.75) and two outer knuckles at its
front hinge (7.25 <= |y| <= 12): the next link's centre knuckle fits between them. The pin
runs free in the centre knuckle and is gripped by the outer knuckles, so it cannot walk out.
The centre notch (|y| <= 4, open towards the front) takes a sprocket tooth between this
link's body and the next link's knuckle. Printed inner face down (grousers up), many per plate;
the pin holes are teardrops pointing up in print.
"""
import sys
from pathlib import Path

from build123d import Align, Box, Cylinder, Pos, Rot
from cadlib import HOLE_COMP_DEFAULT, teardrop_cutter, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261026-rover-assembly"))
from rover_frame import LINK_T, P, PIN_D, TRACK_W  # noqa: E402

from hobby_parts import chamfer_plane_edges  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT   # +0.2 on hole diameters (default, fdm-design-rules)
PIN_RUN_CLR = 0.3               # centre knuckle: pin runs free, sliding fit (Ø2.5 CAD, prints ~Ø2.3 on a Ø2.0 pin;
                                # DFM round 2 fix 1). Knuckle wall 3.0 - 1.25 = 1.75: four 0.45 lines at 0.41 spacing
PIN_GRIP_CLR = 0.0              # outer knuckles: pin gripped (prints ~Ø2.0 on a Ø2.0 rod)
KN_R = LINK_T / 2               # knuckle radius 3.0 (1.8 mm wall round the running hole)
KN_GAP = 0.4                    # radial clearance round a neighbour's knuckle (cut radius 3.4)
CENTRE_HALF = 6.75              # centre knuckle |y|
OUTER_IN = 7.25                 # outer knuckles from |y| 7.25 (0.5 axial gap)
HALF_W = TRACK_W / 2            # 12
NOTCH_HALF = 4.0                # sprocket-tooth notch |y| <= 4
NOTCH_X0 = KN_R + 0.05          # notch starts at the centre knuckle's surface (assembly check round 1)
GROUSER_H, GROUSER_X = 1.5, (4.0, 9.0)
BED_CHAMFER = 0.3


def _box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN,) * 3)


def _knuckle(x, y0, y1):
    return Pos(x, (y0 + y1) / 2, 0) * Rot(90, 0, 0) * Cylinder(KN_R, y1 - y0)


def _pin_hole(x, d, y0, y1):
    """Teardrop pointing to -z (up in print: the link is printed flipped)."""
    return Pos(x, (y0 + y1) / 2, 0) * Rot(0, 180, 0) * teardrop_cutter(d, y1 - y0, axis="Y")


def design():
    clr = KN_R + KN_GAP
    t = LINK_T / 2
    link = _box(0, P - clr, -CENTRE_HALF, CENTRE_HALF, -t, t) + _knuckle(0, -CENTRE_HALF, CENTRE_HALF)
    for s in (-1, 1):
        y0, y1 = sorted((s * OUTER_IN, s * HALF_W))
        link += _box(clr, P, y0, y1, -t, t) + _knuckle(P, y0, y1)
    link += _box(clr, P - clr, -HALF_W, HALF_W, -t, t)                      # bridge, full width
    # inner face goes on the bed: 0.3 chamfer on its edges (the knuckles touch the bed
    # tangentially and are skipped). Done before the grousers, which the kernel trips on.
    link = chamfer_plane_edges(link, t, BED_CHAMFER)
    for s in (-1, 1):
        g0, g1 = sorted((s * (OUTER_IN + 0.25), s * (HALF_W - 0.5)))
        link += _box(GROUSER_X[0], GROUSER_X[1], g0, g1, -t - GROUSER_H, -t + 0.01)
    link -= _box(NOTCH_X0, P + 1, -NOTCH_HALF, NOTCH_HALF, -t - 2, t + 2)   # tooth notch
    link -= _pin_hole(0.0, PIN_D + PIN_RUN_CLR + HOLE_COMP, -CENTRE_HALF - 1, CENTRE_HALF + 1)
    link -= _pin_hole(P, PIN_D + PIN_GRIP_CLR + HOLE_COMP, -HALF_W - 1, HALF_W + 1)
    return link


def build():
    return to_bed(Rot(180, 0, 0) * design())     # inner face on the bed

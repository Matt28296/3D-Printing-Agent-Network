"""Claw pinion: 18-tooth module-1 spur gear on the claw MG90S. Drives both racks.
Printed back face down (horn pocket on the bed, teeth profile in the bed plane).

Pinion frame: origin on the shaft axis at the pinion's back face, +Z along the shaft (claw +x),
+X towards claw +z (rack A). Tooth 0 points at rack A when the claw is closed (model pose).
The servo's double-arm horn, both arms CUT 5.5 mm from the centre, sits 2 mm deep in the
back-face pocket; an M2 x 10 screw from the counterbored front face clamps pinion + horn onto
the spline (the stub flats carry the torque; a drop of CA glue in the pocket removes play).
"""
import sys
from pathlib import Path

from build123d import Align, Cylinder, Pos
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261025-robot-arm-assembly"))
from claw_frame import BACKLASH, FACE_W, HORN_TRIM_R, M, PINION_HORN, Z_TEETH  # noqa: E402

from gears import spur_gear  # noqa: E402
from hobby_parts import chamfer_plane_edges, horn_pocket_cutter  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT  # +0.2 on hole diameters (default, fdm-design-rules)
HEAD_D, HEAD_H = 4.2, 1.6      # M2 pan/cheese head counterbore (printed target, + HOLE_COMP)
POCKET_CLR = 0.3               # horn pocket clearance (tighter than links: gear backlash adds up)
BED_CHAMFER = 0.25


def design():
    g = spur_gear(M, Z_TEETH, FACE_W, backlash=BACKLASH, phase_deg=0.0)
    try:
        g = chamfer_plane_edges(g, 0.0, BED_CHAMFER)      # elephant's foot relief on the bed face
    except ValueError:
        pass                                              # kernel refused: rely on the slicer's EFC
    g -= horn_pocket_cutter(PINION_HORN, link_t=FACE_W, clearance=POCKET_CLR, hole_comp=HOLE_COMP,
                            trim_r=HORN_TRIM_R)
    g -= Pos(0, 0, FACE_W - HEAD_H) * Cylinder((HEAD_D + HOLE_COMP) / 2, HEAD_H + 1,
                                               align=(Align.CENTER, Align.CENTER, Align.MIN))
    return g


def build():
    return to_bed(design())

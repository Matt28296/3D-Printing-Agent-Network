"""Claw pinion: 20-tooth module-1 spur gear on the claw MG90S. Drives both racks.
Printed back face down (horn pocket on the bed, teeth profile in the bed plane).

Pinion frame: origin on the shaft axis at the pinion's back face, +Z along the shaft (claw +x),
+X towards claw +z (rack A). Tooth 0 points at rack A when the claw is closed (model pose).
The servo's double-arm horn, both arms CUT 5.5 mm from the centre with the ends filed round
(the horn then fits inside a Ø11 circle), sits 2 mm deep in the back-face pocket with a light
0.1 mm fit, so the pinion is centred on the spline (deep review 03 SYS-08). An M2 x 12 + Ø6
washer from the counterbored front face clamps pinion + horn onto the spline.

Round 3 (claw DFM + strength round 2): face 10 -> 12 and the teeth only 0.05 thinner at the pitch line
(PINION_BACKLASH 0.1; the racks' 0.35: 0.40 per mesh): tooth fillet SF 2.85 -> 3.61, the rack pry margin 0.08 ->
0.15 mm; counterbore 1.7 -> 3.7 deep (the floor stays 6.3); 0.2 mm 45° chamfer on the horn pocket's mouth.

Round 2 (pinion DFM + strength round 1, SYS-01, SYS-08):
- 20 teeth (was 18), face 10 (was 8), r 0.38 root fillets (tools/gears.py), tips topped 0.15,
  teeth 0.10 thinner at the pitch line (0.35 backlash per mesh with the racks' 0.25; the pinion
  keeps the thicker teeth because its radial-flank root is the weaker one): 21.6 N per rack at
  stall, 0-44 mm in 126° of servo;
- outside Ø21.7: it passes the cover's Ø22.6 pass-through, so it goes on LAST, axially;
- Ø6.2 x 1.7 counterbore for the M2 washer (head bearing); clamp floor 6.3 mm, so the M2 x 12
  reaches 4.6 mm into the spline like every other horn clamp screw on the arm;
- 0.25 x 45° chamfer on the bed face, tooth outline included (no silent fallback).
The neck of each jaw sits outside the pinion's tip circle (r 11.25 vs 10.85), so the pinion's
front face never rubs a neck (DFM fix 2 needs no relief any more).
"""
import sys
from pathlib import Path

from build123d import Align, Cylinder, GeomType, Kind, Pos, Solid
from cadlib import HOLE_COMP_DEFAULT, to_bed

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "20261025-robot-arm-assembly"))
from claw_frame import (FACE_W, HORN_TRIM_R, M, PINION_BACKLASH, PINION_CB_D, PINION_FLOOR, PINION_HORN,  # noqa: E402
                        PINION_ROOT_FILLET, TIP_RELIEF, Z_TEETH)

from gears import spur_gear  # noqa: E402
from hobby_parts import HORN_DEPTH, horn_pocket_cutter  # noqa: E402

# --- parameters (mm) -----------------------------------------------------------
HOLE_COMP = HOLE_COMP_DEFAULT  # +0.2 on hole diameters (default, fdm-design-rules)
POCKET_CLR = 0.1               # horn pocket: light fit that centres the pinion on the horn (SYS-08; was 0.3)
BED_CHAMFER = 0.25             # 45°, tooth outline included (a true 45° face up to 0.25 m: tools/gears.py)
CB_D = PINION_CB_D             # 6.2 printed: Ø6 M2 washer under the clamp-screw head (strength fix)
CB_H = FACE_W - HORN_DEPTH - PINION_FLOOR   # 3.7: leaves a 6.3 mm floor between the washer and the horn face
POCKET_CHAMFER = 0.2           # 45° on the horn pocket's mouth at the bed face (claw round 3, pinion DFM round 2 R1):
                               # no first-layer lip on the 0.1 mm fit; the horn plate sits at z 0.4..2.0, above it


def _pocket_mouth(pocket):
    """45° band round the pocket's outline at the bed face: a ruled loft from the outline grown by POCKET_CHAMFER
    (z 0) to the outline itself (z POCKET_CHAMFER). The pocket cutter's bottom face (z -0.5) gives the outline."""
    bottom = [f for f in pocket.faces() if f.geom_type == GeomType.PLANE and abs(f.center().Z + 0.5) < 1e-6]
    if len(bottom) != 1:
        raise ValueError(f"expected one pocket outline at z -0.5, found {len(bottom)}")
    w = bottom[0].outer_wire()
    grown = w.offset_2d(POCKET_CHAMFER, kind=Kind.INTERSECTION)
    grown = grown[0] if isinstance(grown, list) else grown
    band = Solid.make_loft([Pos(0, 0, 0.5) * grown, Pos(0, 0, 0.5 + POCKET_CHAMFER) * w], ruled=True)
    if not band.is_valid:
        raise ValueError("pocket mouth chamfer is not a valid solid")
    return Pos(0, 0, -0.01) * band


def design():
    g = spur_gear(M, Z_TEETH, FACE_W, backlash=PINION_BACKLASH, phase_deg=0.0, root_fillet=PINION_ROOT_FILLET,
                  tip_relief=TIP_RELIEF, chamfer=(BED_CHAMFER, 0.0))
    pocket = horn_pocket_cutter(PINION_HORN, link_t=FACE_W, clearance=POCKET_CLR, hole_comp=HOLE_COMP,
                                trim_r=HORN_TRIM_R)
    g -= pocket + _pocket_mouth(pocket)
    g -= Pos(0, 0, FACE_W - CB_H) * Cylinder((CB_D + HOLE_COMP) / 2, CB_H + 1,
                                             align=(Align.CENTER, Align.CENTER, Align.MIN))
    return g


def build():
    return to_bed(design())

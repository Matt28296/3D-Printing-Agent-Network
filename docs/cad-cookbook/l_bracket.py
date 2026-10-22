"""Cookbook: load-bearing L-bracket, printed ON ITS SIDE.

Why on its side: the L profile lies in the XY plane, so bending at the inner
corner runs along the layers instead of peeling them apart. The mounting holes
become horizontal, so they are teardrops (print without support).

Copy this to jobs/<id>/model.py and change the parameters.
"""
from build123d import Axis, BuildLine, BuildPart, BuildSketch, Polyline, extrude, fillet, make_face
from cadlib import chamfer_bottom, comp, teardrop_cutter

# --- parameters (mm) -----------------------------------------------------------
LEG = 40.0          # leg length, spec §3
T = 4.0             # leg thickness: 4 mm ≈ 9 perimeters of 0.45 mm
W = 20.0            # bracket width = print height (Z)
INNER_R = 3.0       # fillet at the loaded inner corner, design-rules §2
SCREW_D = 4.5       # M4 clearance, spec §3
HOLE_COMP = 0.2     # default; replace with library/materials.csv hole_comp_mm
HOLE_FROM_END = 15.0
BOTTOM_CHAMFER = 0.4


def build():
    with BuildPart() as bp:
        with BuildSketch():
            with BuildLine():
                Polyline((0, 0), (LEG, 0), (LEG, T), (T, T), (T, LEG), (0, LEG), close=True)
            make_face()
        extrude(amount=W)
        inner = (bp.edges().filter_by(Axis.Z)
                 .filter_by_position(Axis.X, T - 0.01, T + 0.01)
                 .filter_by_position(Axis.Y, T - 0.01, T + 0.01))
        fillet(inner, radius=INNER_R)
    part = bp.part
    d = comp(SCREW_D, HOLE_COMP)
    part -= teardrop_cutter(d, 3 * T, axis="Y", center=(LEG - HOLE_FROM_END, T / 2, W / 2))
    part -= teardrop_cutter(d, 3 * T, axis="X", center=(T / 2, LEG - HOLE_FROM_END, W / 2))
    return chamfer_bottom(part, BOTTOM_CHAMFER)

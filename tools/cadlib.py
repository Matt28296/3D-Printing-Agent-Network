"""Tested build123d helpers for FDM parts. Use in model.py with `from cadlib import *`.

tools/cad_build.py puts tools/ on the import path, so model.py can import these
directly. Every helper is covered by tests/test_cadlib.py. If a helper doesn't
fit, write the geometry in model.py and prove it in cad_checks.py.

Conventions: millimetres; Z is the build direction; the bed is Z = 0.
Cutters are solids you SUBTRACT, e.g. `part = part - teardrop_cutter(...)`.
"""
from __future__ import annotations

import math

from build123d import (Align, Axis, BuildPart, BuildSketch, Circle, Cylinder, GeomType, Part, Plane,
                       Polygon, Pos, RegularPolygon, Vector, chamfer, extrude)

HOLE_COMP_DEFAULT = 0.2  # mm on diameter; replace with library/materials.csv hole_comp_mm
SQRT2 = math.sqrt(2.0)
_AXIS_PLANES = {"X": Plane.YZ, "Y": Plane.XZ}


def comp(diameter: float, hole_comp: float = HOLE_COMP_DEFAULT) -> float:
    """Diameter to model so a printed vertical hole comes out at `diameter`."""
    return diameter + hole_comp


def teardrop_cutter(diameter: float, length: float, axis: str = "X",
                    center: tuple[float, float, float] = (0, 0, 0)) -> Part:
    """Cutter for a horizontal hole that prints without support.

    The 45° point faces +Z. `axis` is "X" or "Y". The cutter is centred on
    `center` and extends length/2 each way along the axis.
    """
    if axis not in _AXIS_PLANES:
        raise ValueError("teardrops are for horizontal holes: axis must be 'X' or 'Y'")
    r = diameter / 2
    k = r / SQRT2
    base = _AXIS_PLANES[axis]
    plane = Plane(origin=center, x_dir=base.x_dir, z_dir=base.z_dir)
    with BuildPart() as bp:
        with BuildSketch(plane):
            Circle(r)
            Polygon((-k, k), (0, r * SQRT2), (k, k), align=None)
        extrude(amount=length / 2, both=True)
    return bp.part


def vertical_hole_cutter(diameter: float, depth: float,
                         top_center: tuple[float, float, float]) -> Part:
    """Cylinder cutter drilled downward from `top_center` by `depth` (axis along Z)."""
    cyl = Cylinder(diameter / 2, depth, align=(Align.CENTER, Align.CENTER, Align.MAX))
    return Pos(*top_center) * cyl


def hex_nut_pocket(across_flats: float, depth: float, clearance: float = 0.25,
                   bottom_center: tuple[float, float, float] = (0, 0, 0)) -> Part:
    """Hex prism cutter for a captive nut, axis along Z, rising from `bottom_center`."""
    with BuildPart() as bp:
        with BuildSketch():
            RegularPolygon((across_flats + clearance) / 2, 6, major_radius=False)
        extrude(amount=depth)
    return Pos(*bottom_center) * bp.part


def chamfer_bottom(part: Part, size: float = 0.4) -> Part:
    """Chamfer every edge lying on the bed plane. Fails loudly if the kernel can't."""
    zmin = part.bounding_box().min.Z
    edges = [e for e in part.edges()
             if abs(e.bounding_box().min.Z - zmin) < 1e-6 and abs(e.bounding_box().max.Z - zmin) < 1e-6]
    if not edges:
        raise ValueError("no edges found on the bed plane")
    return chamfer(edges, length=size)


def to_bed(part: Part) -> Part:
    """Translate so the lowest point sits on Z = 0. Never rotates."""
    return Pos(0, 0, -part.bounding_box().min.Z) * part


def _angles_around(face, axis, samples: int = 72) -> list[float]:
    d = axis.direction.normalized()
    o = axis.position
    ref = Vector(1, 0, 0) if abs(d.X) < 0.9 else Vector(0, 1, 0)
    e1 = (ref - d * ref.dot(d)).normalized()
    e2 = d.cross(e1)
    out = []
    for i in range(samples + 1):
        p = face.position_at(i / samples, 0.5)
        v = p - o
        out.append(math.degrees(math.atan2(v.dot(e2), v.dot(e1))) % 360)
    return out


def _coverage(angles: list[float]) -> float:
    a = sorted(angles)
    gaps = [a[i + 1] - a[i] for i in range(len(a) - 1)] + [a[0] + 360 - a[-1]]
    return 360 - max(gaps)


def measure_holes(part: Part, min_arc_deg: float = 250) -> list[dict]:
    """Holes in the part: diameter, axis direction, a point on the axis, arc.

    Groups cylindrical faces that share an axis and radius (the kernel often
    splits a hole into two faces), keeps groups covering at least
    `min_arc_deg` (a teardrop's round part is about 270°; fillets are ≤180°),
    and keeps only concave faces: the outward face normal points toward the
    axis (a hole), not away from it (a boss or round outer edge).
    """
    groups: dict[tuple, dict] = {}
    for f in part.faces().filter_by(GeomType.CYLINDER):
        try:
            axis, radius = f.axis_of_rotation, f.radius
            p = f.position_at(0.5, 0.5)
            ad = axis.direction.normalized()
            radial = (p - axis.position) - ad * (p - axis.position).dot(ad)
            if f.normal_at(p).dot(radial) >= 0:
                continue  # convex: boss, pin or rounded outer edge
        except Exception:  # pragma: no cover - kernel edge cases
            continue
        d = axis.direction.normalized()
        if d.X < -1e-9 or (abs(d.X) < 1e-9 and (d.Y < -1e-9 or (abs(d.Y) < 1e-9 and d.Z < 0))):
            d = -d
        o = axis.position
        foot = o - d * o.dot(d)  # closest point of the axis line to the origin
        key = (round(radius, 3), round(d.X, 3), round(d.Y, 3), round(d.Z, 3),
               round(foot.X, 2), round(foot.Y, 2), round(foot.Z, 2))
        g = groups.setdefault(key, {"radius": radius, "dir": d, "origin": o, "faces": [], "angles": []})
        g["faces"].append(f)
        g["angles"] += _angles_around(f, axis)
    holes = []
    for g in groups.values():
        arc = _coverage(g["angles"])
        if arc < min_arc_deg:
            continue
        centers = [f.bounding_box().center() for f in g["faces"]]
        c = sum(centers, Vector(0, 0, 0)) / len(centers)
        d, o = g["dir"], g["origin"]
        on_axis = o + d * (c - o).dot(d)  # face centre projected onto the axis line
        holes.append({
            "diameter": round(2 * g["radius"], 4),
            "axis": [round(d.X, 4), round(d.Y, 4), round(d.Z, 4)],
            "point_on_axis": [round(on_axis.X, 3), round(on_axis.Y, 3), round(on_axis.Z, 3)],
            "arc_deg": round(arc, 1),
        })
    return sorted(holes, key=lambda h: (h["point_on_axis"], h["diameter"]))


def bbox(part: Part) -> dict:
    b = part.bounding_box()
    return {"min": [round(b.min.X, 4), round(b.min.Y, 4), round(b.min.Z, 4)],
            "size": [round(b.size.X, 4), round(b.size.Y, 4), round(b.size.Z, 4)]}


__all__ = ["HOLE_COMP_DEFAULT", "comp", "teardrop_cutter", "vertical_hole_cutter", "hex_nut_pocket",
           "chamfer_bottom", "to_bed", "measure_holes", "bbox"]

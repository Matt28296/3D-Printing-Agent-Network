"""Involute spur gears and racks for printed mechanisms (MK3, 0.4 mm nozzle).

Print gears with the tooth profile in the bed plane (axis vertical): the profile is then as
accurate as the XY motion, and the teeth bend along the layers. Keep the module >= 1.0 so a
tooth is several extrusion widths thick.

Conventions
-----------
- Standard full-depth teeth: addendum 1.0 m, dedendum 1.25 m (0.25 m tip clearance).
- `backlash` is the total circular backlash this member gives up: each tooth is
  `backlash / 2` thinner at the pitch line than pi*m/2. A gear and rack that each take
  0.1 mesh with 0.1 mm backlash at the nominal centre distance.
- Gear: axis = +Z, from z = 0 to `width`, centred on the origin. Tooth 0 is centred on
  the +X axis, rotated by `phase_deg`.
- Rack: teeth along +X, pointing +Y. Pitch line on y = 0, tooth tips at y = +m, roots at
  y = -1.25 m, back face at y = -(1.25 m + back). A tooth is centred on x = `phase`.
  The bar spans x from x0 to x1 and z from 0 to `width`.
- A rack meshes with a gear when its pitch line is tangent to the gear's pitch circle
  (centre distance = pitch radius), with a GAP of the rack facing a TOOTH of the gear.
"""
from __future__ import annotations

import math

from build123d import Align, Box, BuildPart, BuildSketch, Part, Plane, Polygon, Pos, extrude

__all__ = ["pitch_radius", "gear_outline", "spur_gear", "rack_outline", "rack_bar", "min_teeth_no_undercut"]


def pitch_radius(m: float, z: int) -> float:
    return m * z / 2.0


def min_teeth_no_undercut(pressure_deg: float = 20.0) -> float:
    """Fewest teeth a standard (unshifted) gear can have without undercut on a rack."""
    return 2.0 / math.sin(math.radians(pressure_deg)) ** 2


def _inv(a: float) -> float:
    return math.tan(a) - a


def gear_outline(m: float, z: int, pressure_deg: float = 20.0, backlash: float = 0.1,
                 phase_deg: float = 0.0, flank_pts: int = 10, tip_pts: int = 3,
                 root_pts: int = 4) -> list[tuple[float, float]]:
    """Closed CCW outline (x, y) of an involute spur gear."""
    if z < 6:
        raise ValueError("fewer than 6 teeth is not a usable gear")
    if m < 0.5:
        raise ValueError("module below 0.5 mm cannot be printed with a 0.4 mm nozzle")
    a = math.radians(pressure_deg)
    rp = pitch_radius(m, z)
    rb = rp * math.cos(a)
    ra = rp + m
    rf = rp - 1.25 * m
    s = math.pi * m / 2.0 - backlash / 2.0
    psi_p = s / (2.0 * rp)

    def half_angle(r: float) -> float:          # half tooth-thickness angle at radius r >= rb
        return psi_p + _inv(a) - _inv(math.acos(min(1.0, rb / r)))

    r0 = max(rb, rf)
    if half_angle(ra) <= 0:
        raise ValueError("teeth come to a point before the tip circle: raise the module or tooth count")
    radii = [r0 + (ra - r0) * i / flank_pts for i in range(flank_pts + 1)]
    pitch = 2.0 * math.pi / z
    ph = math.radians(phase_deg)
    pts: list[tuple[float, float]] = []

    def P(r, t):
        pts.append((r * math.cos(t), r * math.sin(t)))

    for k in range(z):
        c = ph + k * pitch
        h0 = half_angle(r0)
        if rf < rb:                       # radial flank below the base circle
            P(rf, c - h0)
        for r in radii:                   # leading (right) flank, going outwards
            P(r, c - half_angle(r))
        ha = half_angle(ra)
        for i in range(1, tip_pts):       # tip land
            P(ra, c - ha + 2 * ha * i / tip_pts)
        for r in reversed(radii):         # trailing (left) flank, going inwards
            P(r, c + half_angle(r))
        if rf < rb:
            P(rf, c + h0)
        gap0, gap1 = c + h0, c + pitch - h0
        for i in range(1, root_pts):      # root land
            P(rf, gap0 + (gap1 - gap0) * i / root_pts)
    return pts


def spur_gear(m: float, z: int, width: float, pressure_deg: float = 20.0, backlash: float = 0.1,
              phase_deg: float = 0.0) -> Part:
    """Spur gear blank (no bore): axis +Z, z 0..width."""
    with BuildPart() as bp:
        with BuildSketch(Plane.XY):
            Polygon(*gear_outline(m, z, pressure_deg, backlash, phase_deg), align=None)
        extrude(amount=width)
    return bp.part


def rack_outline(m: float, x0: float, x1: float, back: float, pressure_deg: float = 20.0,
                 backlash: float = 0.1, phase: float = 0.0) -> list[tuple[float, float]]:
    """Closed outline of a rack from x0 to x1 (teeth clipped at the ends)."""
    a = math.radians(pressure_deg)
    p = math.pi * m
    hw = (math.pi * m / 2.0 - backlash / 2.0) / 2.0     # half tooth width on the pitch line
    yt, yr = m, -1.25 * m
    wt, wr = hw - yt * math.tan(a), hw - yr * math.tan(a)   # half widths at tip and root
    if wt <= 0:
        raise ValueError("rack teeth come to a point: raise the module")
    yb = yr - back
    k0 = math.floor((x0 - phase) / p) - 1
    k1 = math.ceil((x1 - phase) / p) + 1
    prof: list[tuple[float, float]] = []                # left to right along the top
    for k in range(k0, k1 + 1):
        c = phase + k * p
        prof += [(c - wr, yr), (c - wt, yt), (c + wt, yt), (c + wr, yr)]

    def y_at(x: float) -> float:                          # profile height at x (piecewise linear)
        for (xa, ya), (xb, yb_) in zip(prof, prof[1:]):
            if xa <= x <= xb and xb > xa:
                return ya + (yb_ - ya) * (x - xa) / (xb - xa)
        return yr
    top = [(x0, y_at(x0))] + [q for q in prof if x0 < q[0] < x1] + [(x1, y_at(x1))]
    return [(x0, yb), (x1, yb)] + list(reversed(top))


def rack_bar(m: float, x0: float, x1: float, width: float, back: float, pressure_deg: float = 20.0,
             backlash: float = 0.1, phase: float = 0.0) -> Part:
    """Rack bar (profile in XY, extruded z 0..width)."""
    with BuildPart() as bp:
        with BuildSketch(Plane.XY):
            Polygon(*rack_outline(m, x0, x1, back, pressure_deg, backlash, phase), align=None)
        extrude(amount=width)
    return bp.part


def _demo():  # pragma: no cover - manual check
    g = spur_gear(1.0, 18, 8.0)
    r = Pos(-20, 9.0, 0) * rack_bar(1.0, 0, 40, 8.0, 6.0)
    print(g.volume, r.volume, Box(1, 1, 1, align=(Align.MIN,) * 3).volume)


if __name__ == "__main__":  # pragma: no cover
    _demo()

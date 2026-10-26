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
- `tip_relief` tops every tooth that much below the standard 1.0 m addendum (more tip
  clearance against centre-distance errors of printed parts, at a slightly lower contact ratio).
- `chamfer=(c0, c1)` puts a 45° chamfer of c0 on the z = 0 end and c1 on the z = width end
  (elephant's-foot relief on the bed face). It is a ruled loft from the outline to its 2D inset,
  which works where an edge chamfer of the many short outline edges (root fillets) fails; where
  the loft fails too (tooth tips that the inset collapses, e.g. 0.3 on module 1) it falls back
  to 0.1 mm stepped slices. Keep gear chamfers at 0.25 m or less to get the true 45° face.
"""
from __future__ import annotations

import math

from build123d import Align, Box, BuildPart, BuildSketch, Part, Plane, Polygon, Pos, extrude, insert

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
                 root_pts: int = 4, root_fillet: float = 0.0,
                 fillet_pts: int = 5, tip_relief: float = 0.0) -> list[tuple[float, float]]:
    """Closed CCW outline (x, y) of an involute spur gear.

    root_fillet > 0 rounds each tooth-root corner with an arc of that radius, tangent to the
    flank and to the root circle (a sharp root is a stress raiser; 0.25-0.38 m is usual). The
    arc stays inside the 0.25 m tip-clearance band, so a standard rack or gear still clears it.
    tip_relief > 0 tops the teeth: outside radius rp + m - tip_relief.
    """
    if z < 6:
        raise ValueError("fewer than 6 teeth is not a usable gear")
    if m < 0.5:
        raise ValueError("module below 0.5 mm cannot be printed with a 0.4 mm nozzle")
    if not 0.0 <= tip_relief < 0.5 * m:
        raise ValueError("tip_relief must be at least 0 and under 0.5 m")
    a = math.radians(pressure_deg)
    rp = pitch_radius(m, z)
    rb = rp * math.cos(a)
    ra = rp + m - tip_relief
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

    h0 = half_angle(r0)
    rho = float(root_fillet)
    if rho > 0:
        if rho > 0.4 * m:
            raise ValueError("root_fillet over 0.4 m would reach the mating tooth tips")
        big_r = rf + rho                              # fillet centres, tangent to the root circle
        d_ang = math.asin(rho / big_r)                # centre angle off the flank line
        r_t = math.sqrt(big_r ** 2 - rho ** 2)        # where the arc meets the (radial) flank
        if r_t > r0:
            raise ValueError("root_fillet is longer than the radial flank: lower it")
        if pitch - 2 * h0 - 2 * d_ang <= 0:
            raise ValueError("root fillets overlap in the tooth gap: lower root_fillet")

        def arc(theta_flank: float, side: int) -> list[tuple[float, float]]:
            """Fillet points from the flank tangent point to the root tangent point (side +1:
            trailing flank, arc runs CCW into the gap) or the reverse (side -1)."""
            phi = theta_flank + side * d_ang
            cx, cy = big_r * math.cos(phi), big_r * math.sin(phi)
            tx, ty = r_t * math.cos(theta_flank), r_t * math.sin(theta_flank)
            a0 = math.atan2(ty - cy, tx - cx)
            a1 = phi + math.pi
            da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi      # short way round
            seq = [(cx + rho * math.cos(a0 + da * i / fillet_pts), cy + rho * math.sin(a0 + da * i / fillet_pts))
                   for i in range(fillet_pts + 1)]
            return seq if side > 0 else list(reversed(seq))
    else:
        r_t = rf

    for k in range(z):
        c = ph + k * pitch
        if rf < rb:                       # radial flank below the base circle
            P(r_t, c - h0)
        for r in radii:                   # leading (right) flank, going outwards
            P(r, c - half_angle(r))
        ha = half_angle(ra)
        for i in range(1, tip_pts):       # tip land
            P(ra, c - ha + 2 * ha * i / tip_pts)
        for r in reversed(radii):         # trailing (left) flank, going inwards
            P(r, c + half_angle(r))
        gap0, gap1 = c + h0, c + pitch - h0
        if rho > 0:
            pts.extend(arc(gap0, +1))                       # trailing-flank fillet, ends on the root circle
            g0, g1 = gap0 + d_ang, gap1 - d_ang
            for i in range(1, root_pts):  # root land between the fillets
                P(rf, g0 + (g1 - g0) * i / root_pts)
            pts.extend(arc(gap1, -1)[:-1])                  # next tooth's leading fillet (its flank point comes next)
        else:
            if rf < rb:
                P(rf, c + h0)
            for i in range(1, root_pts):  # root land
                P(rf, gap0 + (gap1 - gap0) * i / root_pts)
    return pts


CHAMFER_STEP = 0.1   # mm: slice height of the stepped fallback chamfer (finer than a 0.2 mm layer)


def _chamfer_band(pts: list[tuple[float, float]], z_end: float, c: float, toward: int, method: str = "loft"):
    """45° chamfer band of height c at the end face z = z_end of an extruded outline; the band lies
    on the side `toward` (+1: z_end .. z_end + c, -1: z_end - c .. z_end) and the end face is the
    outline inset by c in 2D.
    method "loft": a ruled loft from the full outline to the inset outline (a true 45° face).
    method "steps": CHAMFER_STEP slices of outlines inset by each slice's mid depth (within
    CHAMFER_STEP / 2 of a 45° face); used when the loft fails (very narrow tooth tips)."""
    from build123d import Face, Kind, Solid, Wire

    wire = Wire.make_polygon([(x, y, 0.0) for x, y in pts], close=True)

    def inset_wire(d):
        o = wire.offset_2d(-d, kind=Kind.INTERSECTION)
        return o[0] if isinstance(o, list) else o

    z_full = z_end + toward * c
    if method == "loft":
        band = Solid.make_loft([Pos(0, 0, min(z_full, z_end)) * (wire if z_full < z_end else inset_wire(c)),
                                Pos(0, 0, max(z_full, z_end)) * (wire if z_full > z_end else inset_wire(c))],
                               ruled=True)
        if not band.is_valid:
            raise ValueError("chamfer loft is not a valid solid")
        return [band]
    n = max(2, math.ceil(c / CHAMFER_STEP - 1e-9))
    h = c / n
    out = []
    for k in range(n):            # k = 0 is the slice at the chamfered end face
        z0 = z_end + k * h if toward > 0 else z_end - (k + 1) * h
        out.append(Pos(0, 0, z0) * Solid.extrude(Face(inset_wire(c * (1 - (k + 0.5) / n))), (0, 0, h)))
    return out


def _extrude_chamfered(pts: list[tuple[float, float]], width: float,
                       chamfer: tuple[float, float] = (0.0, 0.0)) -> Part:
    """Extrude a closed outline along +Z from 0 to width, with 45° end chamfers: c0 at z = 0 and
    c1 at z = width. Each chamfer is a ruled loft from the outline to its 2D inset (OCC's edge
    chamfer fails on the many short edges of filleted tooth outlines; 2D insets do not), falling
    back to 0.1 mm stepped slices where the loft fails."""
    from build123d import Face, Solid, Wire

    c0, c1 = (float(c) for c in chamfer)
    if c0 < 0 or c1 < 0 or c0 + c1 >= width:
        raise ValueError("chamfers must be at least 0 and leave some straight face width")
    wire = Wire.make_polygon([(x, y, 0.0) for x, y in pts], close=True)
    body = Pos(0, 0, c0) * Solid.extrude(Face(wire), (0, 0, width - c0 - c1))
    for z_end, c, toward in ((0.0, c0, +1), (width, c1, -1)):
        if c <= 0:
            continue
        try:
            pieces = _chamfer_band(pts, z_end, c, toward, "loft")
        except Exception:     # OCC: the loft fails where the inset collapses tooth tips
            pieces = _chamfer_band(pts, z_end, c, toward, "steps")
        for p in pieces:
            body = body + p
    with BuildPart() as bp:      # return a Part, as the plain extrusion always did
        insert(body)
    return bp.part


def spur_gear(m: float, z: int, width: float, pressure_deg: float = 20.0, backlash: float = 0.1,
              phase_deg: float = 0.0, root_fillet: float = 0.0, tip_relief: float = 0.0,
              chamfer: tuple[float, float] = (0.0, 0.0)) -> Part:
    """Spur gear blank (no bore): axis +Z, z 0..width."""
    pts = gear_outline(m, z, pressure_deg, backlash, phase_deg, root_fillet=root_fillet, tip_relief=tip_relief)
    return _extrude_chamfered(pts, width, chamfer)


def rack_outline(m: float, x0: float, x1: float, back: float, pressure_deg: float = 20.0,
                 backlash: float = 0.1, phase: float = 0.0, root_fillet: float = 0.0,
                 fillet_pts: int = 5, tip_relief: float = 0.0) -> list[tuple[float, float]]:
    """Closed outline of a rack from x0 to x1 (teeth clipped at the ends).

    root_fillet > 0 rounds each root corner (flank to root land) with an arc of that radius.
    The arc stays below the depth a standard mating tooth tip reaches (1.0 m), so it is clear
    of the pinion for root_fillet up to about 0.38 m. tip_relief > 0 tops the teeth at
    y = m - tip_relief."""
    if not 0.0 <= tip_relief < 0.5 * m:
        raise ValueError("tip_relief must be at least 0 and under 0.5 m")
    a = math.radians(pressure_deg)
    p = math.pi * m
    hw = (math.pi * m / 2.0 - backlash / 2.0) / 2.0     # half tooth width on the pitch line
    yt, yr = m - tip_relief, -1.25 * m
    wt, wr = hw - yt * math.tan(a), hw - yr * math.tan(a)   # half widths at tip and root
    if wt <= 0:
        raise ValueError("rack teeth come to a point: raise the module")
    yb = yr - back
    k0 = math.floor((x0 - phase) / p) - 1
    k1 = math.ceil((x1 - phase) / p) + 1
    rho = float(root_fillet)
    fil: list[tuple[float, float]] = []                 # trailing-corner fillet for a tooth at x = 0
    if rho > 0:
        half_beta = (math.pi / 2 + a) / 2               # half the gap-side angle at the root corner
        tdist = rho / math.tan(half_beta)
        if tdist * math.cos(a) > 0.25 * m + 0.002 * m:
            raise ValueError("root_fillet would rise above the 0.25 m tip clearance: lower it")
        if 2 * tdist >= p - 2 * wr:
            raise ValueError("root fillets overlap on the root land: lower root_fillet")
        qx, qy = wr, yr
        uf, ur = (-math.sin(a), math.cos(a)), (1.0, 0.0)
        bx, by = uf[0] + ur[0], uf[1] + ur[1]
        bn = math.hypot(bx, by)
        dc = rho / math.sin(half_beta)
        cx, cy = qx + dc * bx / bn, qy + dc * by / bn
        tfx, tfy = qx + tdist * uf[0], qy + tdist * uf[1]
        trx, try_ = qx + tdist, qy
        a0, a1 = math.atan2(tfy - cy, tfx - cx), math.atan2(try_ - cy, trx - cx)
        da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        fil = [(cx + rho * math.cos(a0 + da * i / fillet_pts), cy + rho * math.sin(a0 + da * i / fillet_pts))
               for i in range(fillet_pts + 1)]
    prof: list[tuple[float, float]] = []                # left to right along the top
    for k in range(k0, k1 + 1):
        c = phase + k * p
        if rho > 0:
            prof += [(c - x, y) for (x, y) in reversed(fil)]    # leading corner (mirror image)
            prof += [(c - wt, yt), (c + wt, yt)]
            prof += [(c + x, y) for (x, y) in fil]              # trailing corner
        else:
            prof += [(c - wr, yr), (c - wt, yt), (c + wt, yt), (c + wr, yr)]

    def y_at(x: float) -> float:                          # profile height at x (piecewise linear)
        for (xa, ya), (xb, yb_) in zip(prof, prof[1:]):
            if xa <= x <= xb and xb > xa:
                return ya + (yb_ - ya) * (x - xa) / (xb - xa)
        return yr
    top = [(x0, y_at(x0))] + [q for q in prof if x0 < q[0] < x1] + [(x1, y_at(x1))]
    return [(x0, yb), (x1, yb)] + list(reversed(top))


def rack_bar(m: float, x0: float, x1: float, width: float, back: float, pressure_deg: float = 20.0,
             backlash: float = 0.1, phase: float = 0.0, root_fillet: float = 0.0, tip_relief: float = 0.0,
             chamfer: tuple[float, float] = (0.0, 0.0)) -> Part:
    """Rack bar (profile in XY, extruded z 0..width)."""
    pts = rack_outline(m, x0, x1, back, pressure_deg, backlash, phase, root_fillet=root_fillet, tip_relief=tip_relief)
    return _extrude_chamfered(pts, width, chamfer)


def _demo():  # pragma: no cover - manual check
    g = spur_gear(1.0, 18, 8.0)
    r = Pos(-20, 9.0, 0) * rack_bar(1.0, 0, 40, 8.0, 6.0)
    print(g.volume, r.volume, Box(1, 1, 1, align=(Align.MIN,) * 3).volume)


if __name__ == "__main__":  # pragma: no cover
    _demo()

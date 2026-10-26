"""Tests for tools/gears.py: involute outlines and a meshing interference check."""
import math

import pytest
from build123d import Pos, Rot

from gears import (CHAMFER_STEP, _chamfer_band, gear_outline, min_teeth_no_undercut, pitch_radius, rack_bar,
                   rack_outline, spur_gear)


def test_outline_radii_and_tooth_count():
    m, z = 1.0, 18
    pts = gear_outline(m, z)
    rs = [math.hypot(x, y) for x, y in pts]
    rp = pitch_radius(m, z)
    assert min(rs) == pytest.approx(rp - 1.25 * m, abs=1e-6)
    assert max(rs) == pytest.approx(rp + m, abs=1e-6)
    tips = sum(1 for r in rs if abs(r - (rp + m)) < 1e-6)
    assert tips % z == 0 and tips >= 2 * z            # every tooth has a tip land


def test_backlash_thins_teeth():
    a = spur_gear(1.0, 18, 5.0, backlash=0.0).volume
    b = spur_gear(1.0, 18, 5.0, backlash=0.2).volume
    assert b < a


def test_rejects_unprintable():
    with pytest.raises(ValueError):
        gear_outline(0.3, 18)
    with pytest.raises(ValueError):
        gear_outline(1.0, 4)


def test_rack_outline_is_closed_and_bounded():
    pts = rack_outline(1.0, -10.0, 20.0, back=5.0)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    assert min(xs) == pytest.approx(-10.0) and max(xs) == pytest.approx(20.0)
    assert max(ys) <= 1.0 + 1e-9 and min(ys) == pytest.approx(-6.25)


def test_18_teeth_have_no_undercut():
    assert 18 > min_teeth_no_undercut(20.0)


@pytest.mark.parametrize("deg", [0.0, 4.0, 9.0, 13.0, 20.0])
def test_pinion_and_rack_roll_without_interference(deg):
    """Rack above the pinion, pitch line tangent to the pitch circle; roll the pair together."""
    m, z, w = 1.0, 18, 4.0
    rp = pitch_radius(m, z)
    p = math.pi * m
    gear = Rot(0, 0, deg) * spur_gear(m, z, w, phase_deg=90.0)     # a tooth points at the rack (+Y)
    shift = -rp * math.radians(deg)                                 # CCW pinion moves the top rack -X
    rack = Pos(shift, rp, w) * Rot(180, 0, 0) * rack_bar(m, -25, 25, w, back=4.0, phase=p / 2)
    overlap = (gear & rack).volume
    assert overlap < 0.01, f"pinion and rack interfere by {overlap:.3f} mm³ at {deg}°"
    # and they really are in mesh: moving the rack 0.3 mm towards the pinion makes them collide
    tight = Pos(0, -0.3, 0) * rack
    assert (gear & tight).volume > 0.05


def test_root_fillets_round_the_roots_and_add_material():
    plain = spur_gear(1.0, 18, 5.0)
    filleted = spur_gear(1.0, 18, 5.0, root_fillet=0.38)
    assert filleted.is_valid and filleted.volume > plain.volume          # the corners are filled in
    pts = gear_outline(1.0, 18, root_fillet=0.38)
    rs = [math.hypot(x, y) for x, y in pts]
    assert min(rs) == pytest.approx(7.75, abs=1e-6) and max(rs) == pytest.approx(10.0, abs=1e-6)
    rack_plain = rack_bar(1.0, -10, 20, 5.0, 5.0)
    rack_fil = rack_bar(1.0, -10, 20, 5.0, 5.0, root_fillet=0.38)
    assert rack_fil.is_valid and rack_fil.volume > rack_plain.volume


def test_root_fillet_limits():
    with pytest.raises(ValueError):
        gear_outline(1.0, 18, root_fillet=0.5)        # would reach the mating tips
    with pytest.raises(ValueError):
        rack_outline(1.0, 0, 20, 5.0, root_fillet=0.45)


def test_tip_relief_tops_the_teeth():
    pts = gear_outline(1.0, 20, root_fillet=0.38, tip_relief=0.15)
    assert max(math.hypot(x, y) for x, y in pts) == pytest.approx(10.85, abs=1e-6)
    rpts = rack_outline(1.0, -10.0, 20.0, 5.0, root_fillet=0.3, tip_relief=0.15)
    assert max(y for _, y in rpts) == pytest.approx(0.85, abs=1e-9)
    with pytest.raises(ValueError):
        gear_outline(1.0, 20, tip_relief=0.6)


def test_end_chamfers_are_45_degree_faces_on_filleted_outlines():
    plain = spur_gear(1.0, 20, 10.0, root_fillet=0.38)
    g = spur_gear(1.0, 20, 10.0, root_fillet=0.38, chamfer=(0.25, 0.0))
    assert g.is_valid and len(g.solids()) == 1
    assert g.volume < plain.volume
    bb = g.bounding_box()
    assert bb.min.Z == pytest.approx(0.0, abs=1e-6) and bb.max.Z == pytest.approx(10.0, abs=1e-6)
    # true 45° face: the z = 0 face is the outline inset by the full chamfer, the full outline starts at z = c
    bottom = [v for v in g.vertices() if abs(v.Z) < 1e-6]
    assert max(math.hypot(v.X, v.Y) for v in bottom) == pytest.approx(11.0 - 0.25, abs=0.02)
    inner = [v for v in g.vertices() if abs(v.Z - 0.25) < 1e-6]
    assert max(math.hypot(v.X, v.Y) for v in inner) == pytest.approx(11.0, abs=0.02)
    # the claw's rack (claw_frame.py): ends in tooth gaps, 0.5 backlash, 0.25 chamfer, whose inset keeps every edge
    # (a clipped tooth tip or a short end land that collapses in the inset makes the loft refuse: see
    # test_chamfer_loft_refuses_an_inset_that_lost_edges_and_falls_back_to_steps)
    r = rack_bar(1.0, -8 * math.pi, 10 * math.pi, 10.0, 10.0, backlash=0.5, phase=math.pi / 2, root_fillet=0.3,
                 tip_relief=0.15, chamfer=(0.0, 0.25))
    assert r.is_valid and len(r.solids()) == 1
    top = [v for v in r.vertices() if abs(v.Z - 10.0) < 1e-6]
    assert max(v.Y for v in top) == pytest.approx(0.85 - 0.25, abs=0.02)   # tooth tips 0.85
    with pytest.raises(ValueError):
        spur_gear(1.0, 20, 1.0, chamfer=(0.6, 0.6))


def test_stepped_chamfer_fallback_stays_within_half_a_step():
    pts = rack_outline(1.0, -10.0, 20.0, 5.0, root_fillet=0.3)
    slices = _chamfer_band(pts, 0.0, 0.3, +1, method="steps")
    assert len(slices) == math.ceil(0.3 / CHAMFER_STEP - 1e-9)
    tops = [max(v.Y for v in s.vertices()) for s in slices]       # tooth tip line of each slice
    for k, t in enumerate(tops):
        inset = 1.0 - t
        assert abs(inset - 0.3 * (1 - (k + 0.5) / len(slices))) < 0.01
        assert abs(inset - (0.3 - (k + 0.5) * CHAMFER_STEP)) <= CHAMFER_STEP / 2 + 1e-6


def test_chamfer_loft_refuses_an_inset_that_lost_edges_and_falls_back_to_steps():
    """Module-1 rack, 0.5 backlash, 0.3 chamfer: two tooth tips collapse in the 0.3 inset (256 -> 254 edges), and a
    ruled loft between them twists (the claw jaw's DFM round 2). The loft must be refused and the bar built with the
    stepped band, whose volume is the true 45° band's within half a step."""
    pts = rack_outline(1.0, -8 * math.pi, 10 * math.pi, 10.0, 20.0, 0.5, math.pi / 2, root_fillet=0.3, tip_relief=0.15)
    with pytest.raises(ValueError, match="edges"):
        _chamfer_band(pts, 0.0, 0.3, +1, method="loft")
    steps = sum(s.volume for s in _chamfer_band(pts, 0.0, 0.3, +1, method="steps"))
    plain = rack_bar(1.0, -8 * math.pi, 10 * math.pi, 12.0, 10.0, backlash=0.5, phase=math.pi / 2, root_fillet=0.3,
                     tip_relief=0.15)
    bar = rack_bar(1.0, -8 * math.pi, 10 * math.pi, 12.0, 10.0, backlash=0.5, phase=math.pi / 2, root_fillet=0.3,
                   tip_relief=0.15, chamfer=(0.3, 0.0))
    assert bar.is_valid and len(bar.solids()) == 1
    band = plain.volume - bar.volume                       # what the chamfer took off the bar's first 0.3 mm
    slab = plain.volume * 0.3 / 12.0                       # the plain bar's first 0.3 mm
    assert band == pytest.approx(slab - steps, rel=0.01)   # the stepped band, not the 1.6 % lighter twisted loft
    # and at 0.25 (the jaw's value) the inset keeps every edge, so the true loft is used
    band25 = _chamfer_band(pts, 0.0, 0.25, +1, method="loft")[0]
    assert band25.is_valid


def _claw_pair(m=1.0, z=20, w=4.0, pinion_backlash=0.2, rack_backlash=0.5):
    """The claw's mesh (claw_frame.py): topped, filleted 20-tooth pinion, backlash split 0.2 / 0.5."""
    rp = pitch_radius(m, z)
    gear = spur_gear(m, z, w, phase_deg=90.0, root_fillet=0.38, tip_relief=0.15, backlash=pinion_backlash)
    rack = Pos(0, rp, w) * Rot(180, 0, 0) * rack_bar(m, -25, 25, w, back=4.0, phase=math.pi * m / 2, root_fillet=0.3,
                                                     tip_relief=0.15, backlash=rack_backlash)
    return rp, gear, rack


@pytest.mark.parametrize("deg", [0.0, 4.5, 9.0, 13.5, 18.0])
def test_topped_filleted_20_tooth_pinion_rolls_clear_with_backlash(deg):
    rp, gear, rack = _claw_pair()
    assert (Rot(0, 0, deg) * gear & Pos(-rp * math.radians(deg), 0, 0) * rack).volume < 1e-3


def test_backlash_is_the_play_per_mesh():
    """Each member is thinned by ITS backlash/2 at the pitch line, so the free turn of the pinion between the rack's
    flanks, as pitch-circle arc, is the mean of the two members' backlash: (0.2 + 0.5) / 2 = 0.35 for the claw."""
    rp, gear, rack = _claw_pair()

    def free(deg):
        return (Rot(0, 0, deg) * gear & rack).volume < 1e-7

    play = 0.0
    for sign in (1, -1):
        lo, hi = 0.0, 4.0
        assert free(0.0) and not free(sign * hi)
        for _ in range(16):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if free(sign * mid) else (lo, mid)
        play += rp * math.radians(lo)
    assert play == pytest.approx(0.35, abs=0.03)


@pytest.mark.parametrize("deg", [0.0, 2.5, 5.0, 7.5, 10.0, 12.5, 15.0, 17.5, 20.0])
def test_filleted_pinion_and_rack_still_roll_clear(deg):
    m, z, w = 1.0, 18, 4.0
    rp = pitch_radius(m, z)
    p = math.pi * m
    gear = Rot(0, 0, deg) * spur_gear(m, z, w, phase_deg=90.0, root_fillet=0.38)
    rack = Pos(-rp * math.radians(deg), rp, w) * Rot(180, 0, 0) * rack_bar(m, -25, 25, w, back=4.0, phase=p / 2,
                                                                          root_fillet=0.38)
    assert (gear & rack).volume < 0.01

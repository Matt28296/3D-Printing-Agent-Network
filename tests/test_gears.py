"""Tests for tools/gears.py: involute outlines and a meshing interference check."""
import math

import pytest
from build123d import Pos, Rot

from gears import gear_outline, min_teeth_no_undercut, pitch_radius, rack_bar, rack_outline, spur_gear


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


@pytest.mark.parametrize("deg", [0.0, 2.5, 5.0, 7.5, 10.0, 12.5, 15.0, 17.5, 20.0])
def test_filleted_pinion_and_rack_still_roll_clear(deg):
    m, z, w = 1.0, 18, 4.0
    rp = pitch_radius(m, z)
    p = math.pi * m
    gear = Rot(0, 0, deg) * spur_gear(m, z, w, phase_deg=90.0, root_fillet=0.38)
    rack = Pos(-rp * math.radians(deg), rp, w) * Rot(180, 0, 0) * rack_bar(m, -25, 25, w, back=4.0, phase=p / 2,
                                                                          root_fillet=0.38)
    assert (gear & rack).volume < 0.01

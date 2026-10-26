"""tools/hobby_parts.py: servo/horn geometry, cutters and dummies fit together.

Skipped when build123d isn't installed.
"""
from dataclasses import replace

import pytest

pytest.importorskip("build123d")

from build123d import Align, Box, Cylinder, Pos  # noqa: E402

import hobby_parts as hp  # noqa: E402


def _plate(s, t, margin=12.0):
    """A plate big enough for servo s, z in [-t, 0], in the servo frame."""
    x0 = -(s.length - s.shaft_from_end) - margin
    x1 = s.shaft_from_end + margin
    return Pos(x0, -s.width / 2 - margin, -t) * Box(x1 - x0, s.width + 2 * margin, t, align=(Align.MIN,) * 3)


@pytest.mark.parametrize("servo", [hp.MG996R, hp.SG90])
def test_servo_hangs_through_its_window_without_touching(servo):
    t = 5.0
    plate = _plate(servo, t) - hp.servo_mount_cutter(servo, t)
    dummy = hp.servo_dummy(servo, with_horn=False)
    assert (plate & dummy).volume < 1e-3          # body clears the window; tabs rest on z = 0
    # the tabs sit on the plate: lift the servo 0.2 mm into the plate and it must collide
    assert (plate & (Pos(0, 0, -0.2) * dummy)).volume > 1.0


@pytest.mark.parametrize("servo", [hp.MG996R, hp.SG90])
def test_pilot_holes_leave_material_under_the_tabs(servo):
    """Every tab hole lands outside the body window, so the screw has plastic to bite."""
    t = 5.0
    plate = _plate(servo, t)
    cut = plate - hp.servo_mount_cutter(servo, t)
    window_only = plate - hp.servo_mount_cutter(replace(servo, hole_dx=0.0, hole_dy=0.0, screw_pilot_d=0.01), t)
    removed_by_pilots = window_only.volume - cut.volume
    n = 4 if servo.hole_dy else 2
    assert removed_by_pilots > 0.8 * n * 3.1416 * (servo.screw_pilot_d / 2) ** 2 * t


@pytest.mark.parametrize("roof", ["+y", "-y"])
def test_window_roof_is_45_degrees(roof):
    s = hp.MG996R
    plain = hp.servo_mount_cutter(s, 5.0)
    roofed = hp.servo_mount_cutter(s, 5.0, roof=roof)
    win_l, win_w = s.length + 0.4, s.width + 0.4
    base = win_w if roof in ("+x", "-x") else win_l
    tri = base * (base / 2) / 2 * 7.0                      # triangle area × (plate_t + 2)
    assert roofed.volume - plain.volume == pytest.approx(tri, rel=0.02)


@pytest.mark.parametrize("servo", [hp.MG996R, hp.SG90])
def test_horn_sits_in_its_pocket_at_link_back_z(servo):
    """A link whose back face is at link_back_z holds the horn 2 mm deep, with clearance."""
    t = 6.0
    z0 = hp.link_back_z(servo)
    assert hp.horn_face_z(servo) - z0 == pytest.approx(hp.HORN_DEPTH)
    link = Pos(-30, -20, z0) * Box(60, 40, t, align=(Align.MIN,) * 3)
    link = link - Pos(0, 0, z0) * hp.horn_pocket_cutter(servo, link_t=t)
    dummy = hp.servo_dummy(servo, with_horn=True)
    assert (link & dummy).volume < 1e-3
    # without the pocket the horn would overlap the link by ~depth × horn area
    solid = Pos(-30, -20, z0) * Box(60, 40, t, align=(Align.MIN,) * 3)
    assert (solid & dummy).volume > 20.0


def test_double_arm_pocket_is_symmetric_and_narrow():
    c = hp.horn_pocket_cutter(hp.MG996R, link_t=6.0)
    bb = c.bounding_box()
    tip = hp.MG996R.horn_arm_len + (hp.MG996R.horn_tip_d + 0.5 + hp.HOLE_COMP_DEFAULT) / 2
    assert bb.min.X == pytest.approx(-tip, abs=0.05) and bb.max.X == pytest.approx(tip, abs=0.05)
    assert bb.max.Y - bb.min.Y <= 12.0                    # narrow side bridges < 12 mm
    single = hp.horn_pocket_cutter(hp.SG90, link_t=5.0).bounding_box()
    assert single.min.X == pytest.approx(-(hp.SG90.horn_d + 0.5 + hp.HOLE_COMP_DEFAULT) / 2, abs=0.05)


def test_disc_variant_and_replace():
    assert hp.MG996R_DISC.horn_kind == "disc" and hp.MG996R_DISC.horn_d == 25.0
    mine = hp.replace(hp.MG996R, shaft_from_end=10.6)
    assert mine.shaft_from_end == 10.6 and hp.MG996R.shaft_from_end == 10.2


def test_rounded_plate_and_slot():
    p = hp.rounded_plate(0, 50, 0, 20, 4, r=5)
    assert p.volume == pytest.approx((50 * 20 - (4 - 3.1416) * 25) * 4, rel=1e-3)
    s = hp.slot_cutter(10, 40, 10, 8, 4)
    assert (p - s).volume == pytest.approx(p.volume - (22 * 8 + 3.1416 * 16) * 4, rel=1e-3)


@pytest.mark.parametrize("servo", [hp.MG996R, hp.SG90])
@pytest.mark.parametrize("roof", ["+x", "-x"])
def test_roof_over_the_short_side_is_refused(servo, roof):
    """A roof on a short side swallows the tab pilots (found on the arm turntable)."""
    with pytest.raises(ValueError, match="roof"):
        hp.servo_mount_cutter(servo, 5.0, roof=roof)


@pytest.mark.parametrize("servo", [hp.MG996R, hp.SG90])
def test_long_side_roof_keeps_every_pilot(servo):
    t = 5.0
    plate = _plate(servo, t, margin=30)
    for roof in ("+y", "-y"):
        roofed = plate - hp.servo_mount_cutter(servo, t, roof=roof)
        no_pilots = plate - hp.servo_mount_cutter(
            replace(servo, screw_pilot_d=0.01), t, roof=roof)
        n = 4 if servo.hole_dy else 2
        assert no_pilots.volume - roofed.volume > 0.8 * n * 3.1416 * (servo.screw_pilot_d / 2) ** 2 * t


def test_hole_comp_is_applied_to_every_cutter():
    """fdm-design-rules: printed holes come out ~0.2 mm under, so cutters add HOLE_COMP."""
    s = hp.MG996R
    plain = hp.servo_mount_cutter(s, 5.0, hole_comp=0.0).bounding_box()
    comp = hp.servo_mount_cutter(s, 5.0, hole_comp=0.2).bounding_box()
    assert (comp.max.Y - comp.min.Y) - (plain.max.Y - plain.min.Y) == pytest.approx(0.2, abs=1e-3)
    a = hp.horn_pocket_cutter(s, link_t=6, hole_comp=0.0).bounding_box()
    b = hp.horn_pocket_cutter(s, link_t=6, hole_comp=0.2).bounding_box()
    assert (b.max.X - b.min.X) - (a.max.X - a.min.X) == pytest.approx(0.2, abs=1e-3)


def test_horn_clamp_hole_takes_the_centre_screw():
    """depth=0 gives only the clamp hole: M3 clearance for MG996R, M2 for SG90, plus HOLE_COMP."""
    for servo, d in ((hp.MG996R, 3.4), (hp.SG90, 2.4)):
        bb = hp.horn_pocket_cutter(servo, depth=0, link_t=8).bounding_box()
        assert bb.max.X - bb.min.X == pytest.approx(d + hp.HOLE_COMP_DEFAULT, abs=0.02)


def test_sg90_end_clearance_leaves_a_printed_1_8_mm_wall():
    """Printed wall between the SG90 window end and its tab pilot (both shrink by HOLE_COMP/2)."""
    s = hp.SG90
    end_clr, comp = 0.2, hp.HOLE_COMP_DEFAULT
    pilot_x = abs(s.hole_dx / 2)
    win_half_cad = (s.length + end_clr + comp) / 2
    wall_cad = pilot_x - (s.screw_pilot_d + comp) / 2 - win_half_cad
    assert wall_cad + comp >= 1.8 - 1e-6


def test_pilot_teardrop_points_the_right_way():
    s = hp.MG996R
    plain = hp.servo_mount_cutter(s, 5.0, through=12)
    tear = hp.servo_mount_cutter(s, 5.0, through=12, pilot_teardrop="-y")
    assert tear.volume > plain.volume
    assert tear.bounding_box().min.Y < plain.bounding_box().min.Y or tear.volume - plain.volume > 1.0


def test_n20_fits_its_wall_cutter_and_d_bore():
    """The N20 dummy clears its wall cutter (shaft, boss) and its shaft fits the D-bore with clearance."""
    m = hp.N20_100RPM
    wall = Pos(-15, -15, 0) * Box(30, 30, 3, align=(Align.MIN,) * 3)
    wall = wall - hp.gearmotor_wall_cutter(m, 3)
    assert (wall & hp.gearmotor_dummy(m)).volume < 1e-3
    hub = Pos(0, 0, 3.5) * Cylinder(5.5, 7, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hub = hub - Pos(0, 0, 3.5) * hp.d_shaft_bore_cutter(m, 7)
    assert (hub & hp.gearmotor_dummy(m)).volume < 1e-3
    # the flat must actually key the shaft: a round Ø3 shaft would not fit
    round_shaft = Pos(0, 0, 3.5) * Cylinder(1.5, 6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    assert (hub & round_shaft).volume > 0.5

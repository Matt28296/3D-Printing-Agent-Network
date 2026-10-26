"""Hobby robotics parts for MK3 jobs: servo, board and horn geometry, cutters and dummies.

Use in model.py with `from hobby_parts import *` (tools/ is on the import path).

All dimensions are NOMINAL datasheet values. Servo brands vary by up to ~1 mm,
so every spec is a dataclass you can copy and correct from your own caliper
measurements, e.g. `MY_MG996R = replace(MG996R, shaft_from_end=10.4)`.
Record measured values in the job's spec.md.

Servo frame (used by every function here):
  origin  = the output-shaft axis where it crosses the TAB UNDERSIDE plane
            (the face of your plate that the servo tabs rest on)
  +Z      = the shaft direction (output side)
  +X      = along the body length, towards the end NEAREST the shaft
  body    = x from -(length - shaft_from_end) to +shaft_from_end, y ±width/2,
            z from -tab_height (case bottom) to +(case_top - tab_height)
A plate the servo hangs through occupies z in [-plate_t, 0].
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from build123d import Align, Box, BuildPart, BuildSketch, Cylinder, Part, Plane, Polygon, Pos, Rot, extrude
from cadlib import HOLE_COMP_DEFAULT

__all__ = ["ServoSpec", "MG996R", "MG996R_DISC", "SG90", "BoardSpec", "ESP32_DEVKIT_38", "ESP32_DEVKIT_30",
           "servo_mount_cutter", "horn_pocket_cutter", "servo_dummy", "horn_face_z", "link_back_z", "HORN_DEPTH",
           "rounded_plate", "slot_cutter", "chamfer_plane_edges", "HOLE_COMP_DEFAULT", "replace"]


@dataclass(frozen=True)
class ServoSpec:
    name: str
    length: float          # body length (x)
    width: float           # body width (y)
    case_top: float        # case bottom -> top of case (without spline)
    total_h: float         # case bottom -> top of output spline
    tab_height: float      # case bottom -> underside of mounting tabs
    tab_t: float           # tab thickness
    tab_span: float        # tip-to-tip length over both tabs
    hole_dx: float         # tab hole spacing along x (centre to centre)
    hole_dy: float         # tab hole spacing across y (0 = one hole per tab, on the centreline)
    tab_hole_d: float      # hole diameter in the servo's tab
    screw_pilot_d: float   # PRINTED pilot for the self-tapping tab screw (cutters add hole_comp)
    shaft_from_end: float  # shaft axis to the nearest body end
    horn_kind: str         # "disc" or "arm"
    horn_d: float          # disc diameter, or arm hub diameter
    horn_t: float          # horn plate thickness
    horn_arm_len: float = 0.0   # arm horns: hub centre to tip centre
    horn_tip_d: float = 0.0     # arm horns: tip width
    horn_arms: int = 1          # arm horns: 1 = single arm along +x, 2 = double arm along ±x
    horn_screw_clear_d: float = 3.4   # clearance for the horn's centre screw, which clamps the LINK onto the spline
    stall_torque_nmm: float = 0.0  # datasheet stall torque at 6 V, N·mm
    mass_g: float = 0.0
    # Lead exit (deep review 2026-10-26, B1): the lead leaves the case END nearest the shaft (+x),
    # lead_z above the case bottom, as a flat ribbon lead_w × lead_t. A servo whose body passes
    # through a closed window must get its lead through too, so the window needs a notch there
    # (servo_mount_cutter lead="notch"/"notch_shift_pilot"), or the servo is mounted reversed.
    lead_z: float = 0.0
    lead_w: float = 0.0
    lead_t: float = 0.0
    lead_notch_w: float = 0.0      # printed notch width (lead + clearance)
    lead_notch_reach: float = 0.0  # printed notch depth beyond the case end


# TowerPro MG996R (standard size). Nominal: measure yours before printing.
# Horn: the double-arm horn from the servo's bag. Its slot pocket bridges across the narrow
# width (<10 mm) and carries torque on the slot walls; a Ø25 disc pocket would need a 25 mm bridge.
MG996R = ServoSpec(
    name="MG996R", length=40.7, width=19.7, case_top=36.5, total_h=42.9, tab_height=27.0,
    tab_t=2.5, tab_span=54.0, hole_dx=48.5, hole_dy=10.0, tab_hole_d=4.5, screw_pilot_d=2.6,
    shaft_from_end=10.2, horn_kind="arm", horn_d=11.0, horn_t=2.8, horn_arm_len=17.5,
    horn_tip_d=5.5, horn_arms=2, horn_screw_clear_d=3.4, stall_torque_nmm=1000.0, mass_g=55.0,
    lead_z=6.0, lead_w=4.0, lead_t=1.3, lead_notch_w=4.4, lead_notch_reach=2.0)   # lead end unverified: notch both ends

# Same servo with its round disc horn (Ø25), for parts printed pocket-side up.
MG996R_DISC = replace(MG996R, horn_kind="disc", horn_d=25.0, horn_arm_len=0.0, horn_tip_d=0.0, horn_arms=1)

# TowerPro SG90 (9 g micro). Nominal: measure yours before printing.
SG90 = ServoSpec(
    name="SG90", length=22.5, width=12.0, case_top=22.7, total_h=26.7, tab_height=15.9,
    tab_t=2.5, tab_span=32.2, hole_dx=27.8, hole_dy=0.0, tab_hole_d=2.0, screw_pilot_d=1.5,
    shaft_from_end=5.9, horn_kind="arm", horn_d=7.2, horn_t=1.6, horn_arm_len=14.0, horn_tip_d=4.2,
    horn_screw_clear_d=2.4, stall_torque_nmm=160.0, mass_g=9.0,
    lead_z=5.1, lead_w=3.6, lead_t=1.2, lead_notch_w=4.2, lead_notch_reach=1.5)


@dataclass(frozen=True)
class BoardSpec:
    name: str
    length: float
    width: float
    pcb_t: float
    pins_below: float      # header pins + solder below the PCB
    parts_above: float     # tallest part above the PCB (module shield, USB)
    usb_w: float
    usb_h: float


ESP32_DEVKIT_38 = BoardSpec("ESP32-DevKitC 38-pin", 54.4, 27.9, 1.6, 9.0, 4.0, 9.0, 4.0)
ESP32_DEVKIT_30 = BoardSpec("ESP32 DOIT DevKit 30-pin", 51.5, 28.3, 1.6, 9.0, 4.0, 9.0, 4.0)


HORN_DEPTH = 2.0   # default horn pocket depth in a link


def horn_face_z(s: ServoSpec) -> float:
    """Z of the horn's outer face in the servo frame (= the horn pocket's floor)."""
    return (s.total_h - s.tab_height) + 0.6


def link_back_z(s: ServoSpec, depth: float = HORN_DEPTH) -> float:
    """Z of a link's back face in the servo frame: the horn sits `depth` deep in its pocket."""
    return horn_face_z(s) - depth


def _body_x0(s: ServoSpec) -> float:
    return -(s.length - s.shaft_from_end)


def servo_mount_cutter(s: ServoSpec, plate_t: float, clearance: float = 0.4,
                       roof: str | None = None, through: float = 60.0,
                       hole_comp: float = HOLE_COMP_DEFAULT, end_clearance: float | None = None,
                       pilot_teardrop: str | None = None, lead: str = "none",
                       lead_both_ends: bool | None = None, min_ligament: float = 1.5,
                       pilot_shift: float = 1.3) -> Part:
    """Cutter for a plate the servo hangs through (tabs resting on the plate's z=0 face).

    Cuts the body window and the tab-screw pilots. Sizes are PRINTED targets plus
    `hole_comp` (vertical holes print ~0.2 mm under; fdm-design-rules, HOLE_COMP):
      window = body + clearance (+ end_clearance along x, default = clearance) + hole_comp
      pilot  = s.screw_pilot_d + hole_comp
    roof="+y"/"-y" adds a 45° pointed roof on that long side of the window, for windows
    printed in a vertical wall (the roof side must point up in print). Roofs on the short
    sides ("+x"/"-x") are refused when they would cut the tab pilots.
    pilot_teardrop="+x"/"-x"/"+y"/"-y" gives each pilot a 45° point that way (horizontal pilots).

    lead: how the servo's lead gets through the window when the body passes through it
    (deep review 2026-10-26, B1; the lead leaves the case end nearest the shaft, +x):
      "none"              no notch: only for a servo mounted reversed (tabs on the far face, so
                          the lead never crosses the plate) or a window that is open at +x.
      "notch"             a notch lead_notch_w wide reaching lead_notch_reach beyond the case end,
                          centred on the width; refused when it leaves under `min_ligament` to a pilot
                          (true for micro servos, whose pilots sit on the centreline).
      "notch_shift_pilot" micro servos: the +x pilot moves `pilot_shift` outward and the notch is cut.
                          The builder opens the slit from that tab's hole to the tab end to 2.1 mm with
                          a needle file so the screw reaches the moved pilot.
    lead_both_ends: notch the far end too (default: True for "notch", because the MG996R's lead end
    is unverified; False for "notch_shift_pilot").
    """
    c = clearance + hole_comp
    ce = (clearance if end_clearance is None else end_clearance) + hole_comp
    x0 = _body_x0(s) - ce / 2
    win_l, win_w = s.length + ce, s.width + c
    cutter = Pos(x0, -win_w / 2, -plate_t - 1) * Box(win_l, win_w, plate_t + 2, align=(Align.MIN,) * 3)
    if lead not in ("none", "notch", "notch_shift_pilot"):
        raise ValueError(f"lead must be 'none', 'notch' or 'notch_shift_pilot', not {lead!r}")
    shift = pilot_shift if lead == "notch_shift_pilot" else 0.0
    if lead != "none":
        if s.lead_notch_w <= 0:
            raise ValueError(f"{s.name} has no lead data (lead_notch_w); add it to its ServoSpec")
        both = (lead == "notch") if lead_both_ends is None else lead_both_ends
        nw = s.lead_notch_w + hole_comp
        reach = s.lead_notch_reach + hole_comp / 2
        ends = [1, -1] if both else [1]
        x_end = {1: x0 + win_l - ce / 2, -1: x0 + ce / 2}        # the case ends
        d = s.screw_pilot_d + hole_comp
        for e in ends:
            xa, xb = sorted((x_end[e], x_end[e] + e * reach))
            for (px, py) in _pilot_xy(s, shift):
                if (px - x_end[e]) * e <= 0:
                    continue                                      # pilot at the other end
                gx = max(xa - px, px - xb, 0.0)                   # gap from the notch box to the pilot centre
                gy = max(abs(py) - nw / 2, 0.0)
                lig = (gx ** 2 + gy ** 2) ** 0.5 - d / 2 + hole_comp   # as printed: both holes print ~HOLE_COMP/2 smaller
                if lig < min_ligament:
                    raise ValueError(
                        f"{s.name}: a lead notch at the {'+x' if e > 0 else '-x'} end leaves {lig:.2f} mm to the tab "
                        f"pilot as printed (need {min_ligament}). Use lead='notch_shift_pilot' (micro servos) or mount the "
                        f"servo reversed (tabs on the far face) with lead='none'.")
            cutter = cutter + Pos(min(xa, xb) - 0.01, -nw / 2, -plate_t - 1) * Box(abs(xb - xa) + 0.02, nw, plate_t + 2,
                                                                                   align=(Align.MIN,) * 3)
    if roof:
        bad = _roof_hits_pilots(s, c, roof)
        if bad:
            raise ValueError(
                f"{s.name}: a {roof} roof would cut through the tab pilot(s) at {bad}; the screws would "
                f"have nothing to bite. Turn the servo 90° in the wall so the roof is on a long side "
                f"(roof '+y' or '-y').")
        x1, y0, y1 = x0 + win_l, -win_w / 2, win_w / 2
        xm_, ym_ = (x0 + x1) / 2, 0.0
        tri = {
            "+x": [(x1, y0), (x1 + win_w / 2, ym_), (x1, y1)],
            "-x": [(x0, y0), (x0 - win_w / 2, ym_), (x0, y1)],
            "+y": [(x0, y1), (xm_, y1 + win_l / 2), (x1, y1)],
            "-y": [(x0, y0), (xm_, y0 - win_l / 2), (x1, y0)],
        }[roof]
        with BuildPart() as bp:
            with BuildSketch(Plane.XY.offset(-plate_t - 1)):
                Polygon(*tri, align=None)
            extrude(amount=plate_t + 2)
        cutter = cutter + bp.part
    d = s.screw_pilot_d + hole_comp
    for (px, py) in _pilot_xy(s, shift):
        hole = Pos(px, py, -through / 2) * Cylinder(d / 2, through)
        if s.hole_dy == 0:  # micro servos: slot elongated OUTWARD along x tolerates spacing error
            out = 0.4 if px > _body_x0(s) + s.length / 2 else -0.4
            hole = hole + Pos(px + out / 2, py, -through / 2) * Box(abs(out), d, through)
            hole = hole + Pos(px + out, py, -through / 2) * Cylinder(d / 2, through)
        if pilot_teardrop:
            r = d / 2
            ux, uy = {"+x": (1, 0), "-x": (-1, 0), "+y": (0, 1), "-y": (0, -1)}[pilot_teardrop]
            hole = hole + Pos(px + ux * r / 2 ** 0.5, py + uy * r / 2 ** 0.5, -through / 2) * Rot(0, 0, 45) * Box(r, r, through)
        cutter = cutter + hole
    return cutter


def _pilot_xy(s: ServoSpec, shift_lead_end: float = 0.0) -> list[tuple[float, float]]:
    """Tab pilot centres; `shift_lead_end` moves the +x (lead-end) pilot(s) outward."""
    xm = _body_x0(s) + s.length / 2
    ys = [0.0] if s.hole_dy == 0 else [-s.hole_dy / 2, s.hole_dy / 2]
    return [(xm + dx + (shift_lead_end if dx > 0 else 0.0), y) for dx in (-s.hole_dx / 2, s.hole_dx / 2) for y in ys]


def _roof_hits_pilots(s: ServoSpec, c: float, roof: str, wall: float = 1.0) -> list[tuple[float, float]]:
    """Pilot centres that lie inside the 45° roof triangle grown by pilot radius + wall."""
    x0 = _body_x0(s) - c / 2
    x1, hw, hl = x0 + s.length + c, (s.width + c) / 2, (s.length + c) / 2
    xm = (x0 + x1) / 2
    grow = s.screw_pilot_d / 2 + wall
    hits = []
    for (px, py) in _pilot_xy(s):
        if roof == "+x":   # apex at (x1 + hw, 0); inside if beyond x1 and below the 45° edges
            inside = px > x1 - grow and abs(py) < hw - (px - x1) + grow * 1.42
        elif roof == "-x":
            inside = px < x0 + grow and abs(py) < hw - (x0 - px) + grow * 1.42
        elif roof == "+y":
            inside = py > hw - grow and abs(px - xm) < hl - (py - hw) + grow * 1.42
        else:
            inside = py < -hw + grow and abs(px - xm) < hl - (-hw - py) + grow * 1.42
        if inside:
            hits.append((round(px, 2), round(py, 2)))
    return hits


def horn_pocket_cutter(s: ServoSpec, depth: float = 2.0, clearance: float = 0.5,
                       screw_access_d: float | None = None, link_t: float = 50.0,
                       hole_comp: float = HOLE_COMP_DEFAULT, trim_r: float | None = None) -> Part:
    """Cutter for the horn recess in a link, in LINK frame: origin on the shaft axis at the
    link's BACK face (servo side), +Z pointing away from the servo (into the link).
    Place the link's back face at `link_back_z(s, depth)` in the servo frame, so the horn's
    outer face lands on the pocket floor at z = depth.

    The pocket (z 0..depth) locates the horn and carries torque on its walls. The centre
    hole (default s.horn_screw_clear_d) takes a LONGER centre screw plus washer, put in from
    the link's front face, so the screw clamps link + horn onto the spline (the stock short
    screw would clamp only the horn). Pocket and hole get `hole_comp` added (printed sizes).
    depth=0 gives just the clamp hole (horn face flat on the link's back face). Screw the horn to the link first (its own small screws, pilot-drilled
    through the horn holes), then push the assembly onto the spline.
    trim_r: for a horn whose arms are CUT SHORT to fit a small part (a pinion): the pocket
    is clipped to a circle of trim_r (+ clearance) around the shaft. The user cuts each arm
    trim_r from the centre; the stubs' flat sides still carry the torque.
    """
    clearance = clearance + hole_comp
    access_d = (s.horn_screw_clear_d if screw_access_d is None else screw_access_d) + hole_comp
    access = Pos(0, 0, -0.5) * Cylinder(access_d / 2, link_t + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    if depth <= 0:
        return access
    if s.horn_kind == "disc":
        pocket = Pos(0, 0, -0.5) * Cylinder((s.horn_d + clearance) / 2, depth + 0.5,
                                            align=(Align.CENTER, Align.CENTER, Align.MIN))
    else:  # single-arm horn: hub + tapered arm along +x, made as a hull of overlapping discs
        r_hub = (s.horn_d + clearance) / 2
        r_tip = (s.horn_tip_d + clearance) / 2
        pocket = Pos(0, 0, -0.5) * Cylinder(r_hub, depth + 0.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
        n = 8
        for sgn in ((1,) if s.horn_arms == 1 else (1, -1)):
            for i in range(1, n + 1):
                t = i / n
                r = r_hub + (r_tip - r_hub) * t
                pocket = pocket + Pos(sgn * s.horn_arm_len * t, 0, -0.5) * Cylinder(
                    r, depth + 0.5, align=(Align.CENTER, Align.CENTER, Align.MIN))
    if trim_r is not None:
        if trim_r <= s.horn_d / 2:
            raise ValueError(f"trim_r {trim_r} leaves no arm stub outside the {s.horn_d} mm hub")
        pocket = pocket & (Pos(0, 0, -1) * Cylinder(trim_r + clearance / 2, depth + 2,
                                                    align=(Align.CENTER, Align.CENTER, Align.MIN)))
    return pocket + access


def servo_dummy(s: ServoSpec, with_horn: bool = True) -> Part:
    """Approximate servo solid in the servo frame, for assembly interference checks."""
    x0 = _body_x0(s)
    body = Pos(x0, -s.width / 2, -s.tab_height) * Box(s.length, s.width, s.case_top,
                                                      align=(Align.MIN,) * 3)
    xm = x0 + s.length / 2
    tabs = Pos(xm, 0, s.tab_t / 2) * Box(s.tab_span, s.width, s.tab_t)
    shaft_h = s.total_h - s.case_top
    shaft = Pos(0, 0, s.case_top - s.tab_height) * Cylinder(
        2.5 if s.horn_kind == "disc" else 2.4, shaft_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    out = body + tabs + shaft
    if with_horn:
        hz = horn_face_z(s)
        if s.horn_kind == "disc":
            out = out + Pos(0, 0, hz - s.horn_t) * Cylinder(s.horn_d / 2, s.horn_t,
                                                           align=(Align.CENTER, Align.CENTER, Align.MIN))
        else:
            out = out + Pos(0, 0, hz - s.horn_t) * Cylinder(s.horn_d / 2, s.horn_t,
                                                           align=(Align.CENTER, Align.CENTER, Align.MIN))
            for sgn in ((1,) if s.horn_arms == 1 else (1, -1)):
                out = out + Pos(sgn * s.horn_arm_len / 2, 0, hz - s.horn_t / 2) * Box(
                    s.horn_arm_len, s.horn_tip_d, s.horn_t)
                out = out + Pos(sgn * s.horn_arm_len, 0, hz - s.horn_t) * Cylinder(
                    s.horn_tip_d / 2, s.horn_t, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return out


def rounded_plate(x0: float, x1: float, y0: float, y1: float, t: float, r: float = 6.0, z0: float = 0.0) -> Part:
    """Flat plate x0..x1, y0..y1, z0..z0+t with its vertical edges rounded to r."""
    from build123d import Axis, fillet
    p = Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, t, align=(Align.MIN,) * 3)
    r = min(r, (x1 - x0) / 2 - 0.01, (y1 - y0) / 2 - 0.01)
    return fillet(p.edges().filter_by(Axis.Z), radius=r) if r > 0 else p


def slot_cutter(x0: float, x1: float, y: float, w: float, t: float, z0: float = 0.0) -> Part:
    """Through slot (stadium) from x0 to x1 (outer ends), width w, centred on y; cuts z0-1..z0+t+1."""
    r = w / 2
    c = Pos((x0 + x1) / 2, y, z0 - 1) * Box(x1 - x0 - w, w, t + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for x in (x0 + r, x1 - r):
        c = c + Pos(x, y, z0 - 1) * Cylinder(r, t + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return c


def _is_tangent_edge(edge, faces, tol_deg: float = 1.0) -> bool:
    """True when the two faces meeting at `edge` are tangent there (for example a cylinder
    resting on a plane). Such an edge has no corner to chamfer, and the kernel fails on it."""
    adj = [f for f in faces if any(edge.is_same(fe) for fe in f.edges())]
    if len(adj) != 2:
        return False
    p = edge.position_at(0.5)
    return adj[0].normal_at(p).get_angle(adj[1].normal_at(p)) < tol_deg


def chamfer_plane_edges(part: Part, z: float, size: float = 0.4) -> Part:
    """Chamfer every edge lying in the plane Z = z (use on the blank, before cutting holes,
    for the face that goes on the bed: elephant's-foot relief). Edges where a curved face is
    tangent to the plane (a knuckle or boss touching the bed along a line) are skipped: they
    have no corner, and a curved face leaves the bed on its own."""
    from build123d import chamfer
    faces = part.faces()
    edges = [e for e in part.edges()
             if abs(e.bounding_box().min.Z - z) < 1e-6 and abs(e.bounding_box().max.Z - z) < 1e-6
             and not _is_tangent_edge(e, faces)]
    if not edges:
        raise ValueError(f"no edges in the plane Z = {z}")
    return chamfer(edges, length=size)


# ----------------------------------------------------------------------------------------
# Small DC gear motors, power and sensor parts (tracked rover). Nominal: measure yours.
# ----------------------------------------------------------------------------------------

@dataclass(frozen=True)
class GearMotorSpec:
    """N20-style micro gear motor. Frame: origin on the shaft axis at the GEARBOX FACE,
    +Z = shaft direction (out of the gearbox), body towards -Z; the gearbox's 12 mm side
    (and the two face screw holes) along X."""
    name: str
    gb_w: float            # gearbox width (x), carries the face screw holes
    gb_h: float            # gearbox height (y)
    gb_len: float          # gearbox length (z)
    can_d: float           # motor can diameter
    can_flat: float        # across the can's flats (y)
    can_len: float         # can length incl. end cap
    term_len: float        # terminals behind the can
    shaft_d: float
    shaft_flat: float      # D-flat: distance from the flat to the far side of the shaft
    shaft_len: float       # from the gearbox face
    boss_d: float          # bearing boss round the shaft on the face
    boss_h: float
    face_hole_dx: float    # face screw spacing along x
    face_screw_d: float    # thread size (M1.6)
    stall_torque_nmm: float
    mass_g: float
    end_cap_len: float = 1.4    # plastic brush cap behind the can (detailed dummy only)
    end_cap_w: float = 9.0      # its width along x (its height is can_flat - 1.2)


# GA12-N20 (N20), 6 V, 100 rpm, about 150:1, LOW- or MEDIUM-power winding (stall <= 0.7 A at 6 V),
# 9 mm gearbox, 3 mm D-shaft 10 mm long. "N20 6 V 100 rpm" alone does not define one motor: the
# same label is sold with 150:1 and 298:1 boxes, 9 or 11 mm gearboxes, 9 or 10 mm shafts and
# high-power windings that stall at 1.6 A (rover deep review 01-S9). Nominal: measure yours.
N20_100RPM = GearMotorSpec(
    name="N20 6V 100rpm LP/MP (150:1, 9 mm gearbox, 3x10 D-shaft)", gb_w=12.0, gb_h=10.0, gb_len=9.0, can_d=12.0,
    can_flat=10.0, can_len=15.5, term_len=2.5, shaft_d=3.0, shaft_flat=2.5, shaft_len=10.0, boss_d=4.0, boss_h=0.8,
    face_hole_dx=9.0, face_screw_d=1.6, stall_torque_nmm=130.0, mass_g=10.0)


def gearmotor_dummy(m: GearMotorSpec, detailed: bool = False) -> Part:
    """Approximate N20 solid in its frame (gearbox, can with flats, terminals, boss, shaft).
    detailed=True adds the plastic end cap and the two solder tabs with solder blobs, the way
    the viewer's model has them, for assembly checks that must see the motor's real length."""
    from build123d import Box as _B
    gb = Pos(0, 0, -m.gb_len / 2) * _B(m.gb_w, m.gb_h, m.gb_len)
    can = Pos(0, 0, -m.gb_len - m.can_len / 2) * (Cylinder(m.can_d / 2, m.can_len)
                                                  & _B(m.can_d, m.can_flat, m.can_len))
    term = Pos(0, 0, -m.gb_len - m.can_len - m.term_len / 2) * _B(6.0, 4.0, m.term_len)
    boss = Cylinder(m.boss_d / 2, m.boss_h, align=(Align.CENTER, Align.CENTER, Align.MIN))
    shaft = Cylinder(m.shaft_d / 2, m.shaft_len, align=(Align.CENTER, Align.CENTER, Align.MIN))
    flat_y = m.shaft_flat - m.shaft_d / 2          # D-flat on +Y, like d_shaft_bore_cutter
    shaft = shaft & Pos(0, (flat_y - m.shaft_d / 2) / 2, 0) * _B(m.shaft_d, flat_y + m.shaft_d / 2, m.shaft_len,
                                                                  align=(Align.CENTER, Align.CENTER, Align.MIN))
    out = gb + can + term + boss + shaft
    if detailed:
        z_can = -m.gb_len - m.can_len
        cap_h = m.can_flat - 1.2
        out = out + Pos(0, 0, z_can - m.end_cap_len / 2) * _B(m.end_cap_w, cap_h, m.end_cap_len + 0.02)
        tab_l = m.term_len + m.end_cap_len
        for sx in (-1, 1):
            out = out + Pos(sx * 2.6, 0, z_can - tab_l / 2) * _B(1.2, 0.4, tab_l + 0.02)
            out = out + Pos(sx * 2.6, 0, z_can - tab_l + 0.6) * _B(2.0, 2.0, 2.0)     # solder blob + lead end
    return out


@dataclass(frozen=True)
class MountingHubSpec:
    """Flat metal hub that clamps a motor shaft with a radial set screw and carries a part on
    threaded holes. Frame: origin on the shaft axis at the hub's INNER face (motor side),
    +Z away from the motor, so the hub spans z 0..t. Hole 0 sits on +X; the set screw sits
    midway between two holes, at mid-thickness."""
    name: str
    od: float
    t: float
    bore: float
    n_holes: int
    hole_thread: float       # thread size of the mounting holes (M3 = 3.0)
    bolt_circle_r: float     # radius of the mounting-hole circle
    bolt_circle_r_range: tuple[float, float]   # range a mating part should accept if unconfirmed
    set_screw: float         # set-screw thread size
    mass_g: float


# Pololu Universal Aluminum Mounting Hub for 3 mm Shaft, M3 Holes (#1996, sold as a 2-pack with
# two M3 set screws and a 1.5 mm key; https://www.pololu.com/product/1996/specs): 17.5 mm
# diameter x 5 mm, 3 mm bore, 4 threaded M3 holes, 2.8 g. The hole circle is NOT stated in text;
# the dimension drawing (https://www.pololu.com/file/0J661/1996-3mm-m3-hub-dimensions.pdf) prints
# an unlabelled 6.35 [0.25] beside "4xM3", read here as the hole-circle radius (12.7 mm circle).
# Unconfirmed, so mating parts take radial slots covering r 5.5-6.85.
POLOLU_HUB_1996 = MountingHubSpec(
    name="Pololu 1996 universal aluminium hub, 3 mm shaft, M3 holes", od=17.5, t=5.0, bore=3.0, n_holes=4,
    hole_thread=3.0, bolt_circle_r=6.35, bolt_circle_r_range=(5.5, 6.85), set_screw=3.0, mass_g=2.8)


def mounting_hub_dummy(h: MountingHubSpec, hole_angle_deg: float = 0.0) -> Part:
    """Hub solid in its frame: disc with its bore and the mounting holes at their thread size,
    so a shaft and the screws sit in it without overlapping it."""
    import math
    out = Cylinder(h.od / 2, h.t, align=(Align.CENTER, Align.CENTER, Align.MIN))
    out = out - Pos(0, 0, -1) * Cylinder(h.bore / 2, h.t + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for k in range(h.n_holes):
        a = math.radians(hole_angle_deg + k * 360.0 / h.n_holes)
        out = out - Pos(h.bolt_circle_r * math.cos(a), h.bolt_circle_r * math.sin(a), -1) * Cylinder(
            h.hole_thread / 2, h.t + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return out


def gearmotor_wall_cutter(m: GearMotorSpec, wall_t: float, hole_comp: float = HOLE_COMP_DEFAULT,
                          teardrop: str | None = "+y", boss_clear: float = 0.6) -> Part:
    """Cutter for a wall the gearbox face bolts against (wall occupies z in [0, wall_t] in the
    motor frame): shaft/boss clearance hole and the two face-screw clearance holes."""
    d_boss = m.boss_d + boss_clear + hole_comp
    d_scr = m.face_screw_d + 0.4 + hole_comp
    c = _teardrop_z(d_boss, wall_t, teardrop)
    for sx in (-1, 1):
        c = c + Pos(sx * m.face_hole_dx / 2, 0, 0) * _teardrop_z(d_scr, wall_t, teardrop)
    return c


def d_shaft_bore_cutter(m: GearMotorSpec, depth: float, clearance: float = 0.1,
                        hole_comp: float = HOLE_COMP_DEFAULT) -> Part:
    """D-shaped bore for the motor shaft along +Z from z = 0 to depth (press fit + grub screw).
    The flat is on the +Y side."""
    d = m.shaft_d + clearance + hole_comp
    flat_y = m.shaft_flat - m.shaft_d / 2 + (clearance + hole_comp) / 2   # flat's distance from the axis
    bore = Cylinder(d / 2, depth, align=(Align.CENTER, Align.CENTER, Align.MIN))
    keep = Pos(0, -d / 2 + (d / 2 + flat_y) / 2, 0) * Box(d, d / 2 + flat_y, depth,
                                                         align=(Align.CENTER, Align.CENTER, Align.MIN))
    return bore & keep


def _teardrop_z(d: float, length: float, point: str | None) -> Part:
    """Round hole of diameter d along +Z (z 0..length, extended 1 mm each end), with an optional
    45° point towards +x/-x/+y/-y (the up direction when the wall is printed standing)."""
    r = d / 2
    h = Pos(0, 0, -1) * Cylinder(r, length + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    if point:
        ux, uy = {"+x": (1, 0), "-x": (-1, 0), "+y": (0, 1), "-y": (0, -1)}[point]
        h = h + Pos(ux * r / 2 ** 0.5, uy * r / 2 ** 0.5, -1) * Rot(0, 0, 45) * Box(
            r, r, length + 2, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return h


@dataclass(frozen=True)
class BoxSpec:
    """A stock component approximated by a box (and its notes)."""
    name: str
    length: float
    width: float
    height: float
    mass_g: float = 0.0
    note: str = ""


BATT_2X18650 = BoxSpec("2 × 18650 series holder", 77.0, 41.0, 21.0, 135.0,
                       "holder ~40 g + two cells ~47 g each; use protected cells or a 2S BMS")
# Holder made for PROTECTED button-top cells (~69.5 mm long): longer than the 65 mm-cell holder.
# The rover floor takes up to 80 mm (x 22-102), so CAD checks use this as the worst case.
BATT_2X18650_LONG = BoxSpec("2 × 18650 holder for protected (≈70 mm) cells", 80.0, 41.0, 21.0, 135.0,
                            "outside length up to 80 mm; measure yours")
TB6612_CARRIER = BoxSpec("TB6612FNG carrier (Pololu-size)", 20.3, 15.2, 3.0, 2.0)
MINI_BREADBOARD = BoxSpec("mini breadboard, 170 tie points", 47.0, 35.0, 8.5, 10.0, "adhesive back")
MP1584_BUCK = BoxSpec("MP1584 buck module", 22.0, 17.0, 4.0, 2.0, "set to 5.0 V before connecting the ESP32")
HCSR04 = BoxSpec("HC-SR04 ultrasonic", 45.0, 20.0, 15.0, 9.0,
                 "transducers Ø16 at ±13.0 mm from the board centre, 12 mm tall")
HCSR04_TX_D, HCSR04_TX_DX = 16.0, 26.0
KCD11_SWITCH_CUTOUT = (15.0, 10.0)    # mini rocker switch panel cut-out (w, h)

__all__ += ["GearMotorSpec", "N20_100RPM", "gearmotor_dummy", "gearmotor_wall_cutter", "d_shaft_bore_cutter",
            "MountingHubSpec", "POLOLU_HUB_1996", "mounting_hub_dummy",
            "BoxSpec", "BATT_2X18650", "BATT_2X18650_LONG", "TB6612_CARRIER", "MINI_BREADBOARD", "MP1584_BUCK", "HCSR04",
            "HCSR04_TX_D", "HCSR04_TX_DX", "KCD11_SWITCH_CUTOUT"]


# ----------------------------------------------------------------------------------------
# Hexapod parts. Nominal: measure yours.
# ----------------------------------------------------------------------------------------

# TowerPro MG90S (metal gears, ~2.2 kg·cm at 6 V), its own spec since the deep review of 2026-10-26:
#  - B2: the spline top is 14.0 mm above the tab underside (TowerPro table A 32.5 - F 18.5; MCAD's SG90
#    model agrees), not the 10.8 the SG90-derived spec gave: the old total_h was the gear boss, not the spline.
#  - S1: body 22.8 × 12.2 mm (TowerPro, Waveshare); case bottom 18.5 mm below the tabs.
# Nominal: measure yours (case bottom -> tab underside, tab underside -> spline top, length, width) and
# correct with replace(MG90S, ...) if anything differs by more than 0.1 mm.
MG90S = ServoSpec(
    name="MG90S", length=22.8, width=12.2, case_top=25.3, total_h=32.5, tab_height=18.5,
    tab_t=2.5, tab_span=32.2, hole_dx=27.8, hole_dy=0.0, tab_hole_d=2.0, screw_pilot_d=1.5,
    shaft_from_end=5.9, horn_kind="arm", horn_d=7.2, horn_t=1.6, horn_arm_len=14.0, horn_tip_d=4.2,
    horn_screw_clear_d=2.4, stall_torque_nmm=216.0, mass_g=13.4,
    lead_z=5.1, lead_w=3.6, lead_t=1.2, lead_notch_w=4.2, lead_notch_reach=1.5)

PCA9685_BOARD = BoxSpec("PCA9685 16-ch servo driver", 62.5, 25.4, 12.0, 9.0,
                        "4 × Ø2.5 mounting holes at 56 × 19 mm; servo headers along one long edge")
LIPO_2S_1000 = BoxSpec("2S 1000 mAh LiPo", 70.0, 35.0, 18.0, 65.0, "XT30 or JST lead; charge with a balance charger")
UBEC_6V_5A = BoxSpec("6 V 5 A UBEC (switching BEC)", 45.0, 20.0, 9.0, 15.0, "set to 6 V; feeds the servo rail")
PCA9685_HOLES = (56.0, 19.0)

__all__ += ["MG90S", "PCA9685_BOARD", "LIPO_2S_1000", "UBEC_6V_5A", "PCA9685_HOLES"]

# MG90S with its DOUBLE-arm horn (same arm size as the single arm, both ways along ±x).
MG90S_DOUBLE = replace(MG90S, horn_arms=2)

# Logitech Brio 4K webcam with its mounting clip REMOVED (Logitech 4K Pro quick-start guide:
# camera 27 H x 102 W x 27 D mm, 63 g; the clip is 44 g extra). A 1/4"-20 tripod thread sits
# in the middle of the bottom face. USB-C socket on the camera, 2.2 m USB-A cable.
# Frame used by the mounts: origin at the thread on the bottom face, +X = lens direction,
# +Y = long axis, +Z = up. The body spans x ±13.5, y ±51, z 0..27; lens at (13.5, 0, 13.5).
BRIO_4K = BoxSpec("Logitech Brio 4K webcam, clip removed", 102.0, 27.0, 27.0, 63.0,
                  "1/4-20 thread centred on the bottom; measure its depth before choosing the screw")
BRIO_EDGE_R = 6.0          # rounding of the long edges (estimated from photos: measure yours)
TRIPOD_SCREW_D = 6.35      # 1/4"-20 UNC major diameter
__all__ += ["MG90S_DOUBLE", "BRIO_4K", "BRIO_EDGE_R", "TRIPOD_SCREW_D"]

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


# TowerPro MG996R (standard size). Nominal: measure yours before printing.
# Horn: the double-arm horn from the servo's bag. Its slot pocket bridges across the narrow
# width (<10 mm) and carries torque on the slot walls; a Ø25 disc pocket would need a 25 mm bridge.
MG996R = ServoSpec(
    name="MG996R", length=40.7, width=19.7, case_top=36.5, total_h=42.9, tab_height=27.0,
    tab_t=2.5, tab_span=54.0, hole_dx=48.5, hole_dy=10.0, tab_hole_d=4.5, screw_pilot_d=2.6,
    shaft_from_end=10.2, horn_kind="arm", horn_d=11.0, horn_t=2.8, horn_arm_len=17.5,
    horn_tip_d=5.5, horn_arms=2, horn_screw_clear_d=3.4, stall_torque_nmm=1000.0, mass_g=55.0)

# Same servo with its round disc horn (Ø25), for parts printed pocket-side up.
MG996R_DISC = replace(MG996R, horn_kind="disc", horn_d=25.0, horn_arm_len=0.0, horn_tip_d=0.0, horn_arms=1)

# TowerPro SG90 (9 g micro). Nominal: measure yours before printing.
SG90 = ServoSpec(
    name="SG90", length=22.5, width=12.0, case_top=22.7, total_h=26.7, tab_height=15.9,
    tab_t=2.5, tab_span=32.2, hole_dx=27.8, hole_dy=0.0, tab_hole_d=2.0, screw_pilot_d=1.5,
    shaft_from_end=5.9, horn_kind="arm", horn_d=7.2, horn_t=1.6, horn_arm_len=14.0, horn_tip_d=4.2,
    horn_screw_clear_d=2.4, stall_torque_nmm=160.0, mass_g=9.0)


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
                       pilot_teardrop: str | None = None) -> Part:
    """Cutter for a plate the servo hangs through (tabs resting on the plate's z=0 face).

    Cuts the body window and the tab-screw pilots. Sizes are PRINTED targets plus
    `hole_comp` (vertical holes print ~0.2 mm under; fdm-design-rules, HOLE_COMP):
      window = body + clearance (+ end_clearance along x, default = clearance) + hole_comp
      pilot  = s.screw_pilot_d + hole_comp
    roof="+y"/"-y" adds a 45° pointed roof on that long side of the window, for windows
    printed in a vertical wall (the roof side must point up in print). Roofs on the short
    sides ("+x"/"-x") are refused when they would cut the tab pilots.
    pilot_teardrop="+x"/"-x"/"+y"/"-y" gives each pilot a 45° point that way (horizontal pilots).
    """
    c = clearance + hole_comp
    ce = (clearance if end_clearance is None else end_clearance) + hole_comp
    x0 = _body_x0(s) - ce / 2
    win_l, win_w = s.length + ce, s.width + c
    cutter = Pos(x0, -win_w / 2, -plate_t - 1) * Box(win_l, win_w, plate_t + 2, align=(Align.MIN,) * 3)
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
    for (px, py) in _pilot_xy(s):
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


def _pilot_xy(s: ServoSpec) -> list[tuple[float, float]]:
    xm = _body_x0(s) + s.length / 2
    ys = [0.0] if s.hole_dy == 0 else [-s.hole_dy / 2, s.hole_dy / 2]
    return [(xm + dx, y) for dx in (-s.hole_dx / 2, s.hole_dx / 2) for y in ys]


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
                       hole_comp: float = HOLE_COMP_DEFAULT) -> Part:
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


def chamfer_plane_edges(part: Part, z: float, size: float = 0.4) -> Part:
    """Chamfer every edge lying in the plane Z = z (use on the blank, before cutting holes,
    for the face that goes on the bed: elephant's-foot relief)."""
    from build123d import chamfer
    edges = [e for e in part.edges()
             if abs(e.bounding_box().min.Z - z) < 1e-6 and abs(e.bounding_box().max.Z - z) < 1e-6]
    if not edges:
        raise ValueError(f"no edges in the plane Z = {z}")
    return chamfer(edges, length=size)

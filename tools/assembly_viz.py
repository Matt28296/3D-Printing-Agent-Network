"""Visual models of bought parts and a GLB scene builder for whole-robot assembly viewers.

This is for *pictures*, not fit checks: the purchased parts (servos with horns and leads,
ESP32 boards with their chips and headers, servo/motor drivers, N20 motors, batteries,
regulators, sensors, switches, fasteners) are modelled from boxes and cylinders in their
real colours, in the SAME frames as tools/hobby_parts.py, so they drop straight into the
assembly frames used by each robot's assembly_check.py. Printed parts come from each job's
model.py design(), tessellated and smooth-shaded.

VizScene builds a node hierarchy (so a viewer can rotate joint nodes about their local Z),
reuses one mesh for repeated parts (track links, leg parts), writes a .glb and returns a
metadata dict (node -> label, category) for the viewer's part list.
"""
from __future__ import annotations

import math
import tempfile
from pathlib import Path

import numpy as np
import trimesh
from trimesh.visual import TextureVisuals
from trimesh.visual.material import PBRMaterial

from hobby_parts import BoardSpec, GearMotorSpec, ServoSpec, horn_face_z

# --- materials -----------------------------------------------------------------------------
# name: (rgba 0-255, metallic, roughness)
PALETTE = {
    "petg_orange": ((236, 107, 37, 255), 0.0, 0.45),
    "petg_olive": ((92, 108, 58, 255), 0.0, 0.5),
    "petg_white": ((232, 230, 224, 255), 0.0, 0.45),
    "petg_grey": ((120, 124, 128, 255), 0.0, 0.5),
    "servo_black": ((30, 31, 34, 255), 0.0, 0.55),
    "servo_blue": ((38, 102, 196, 235), 0.0, 0.3),
    "servo_label": ((215, 220, 226, 255), 0.0, 0.6),
    "horn_white": ((244, 244, 240, 255), 0.0, 0.5),
    "brass": ((201, 162, 74, 255), 0.9, 0.35),
    "steel": ((186, 190, 196, 255), 0.95, 0.3),
    "black_oxide": ((48, 50, 54, 255), 0.6, 0.45),
    "copper": ((196, 112, 64, 255), 0.9, 0.35),
    "gold": ((212, 175, 55, 255), 1.0, 0.3),
    "pcb_black": ((26, 31, 34, 255), 0.0, 0.6),
    "pcb_blue": ((30, 70, 160, 255), 0.0, 0.55),
    "pcb_red": ((176, 44, 40, 255), 0.0, 0.55),
    "pcb_module": ((24, 46, 92, 255), 0.0, 0.5),
    "shield": ((205, 209, 212, 255), 0.9, 0.25),
    "chip": ((22, 22, 24, 255), 0.0, 0.4),
    "plastic_black": ((24, 24, 26, 255), 0.0, 0.6),
    "plastic_white": ((240, 238, 232, 255), 0.0, 0.7),
    "terminal_green": ((44, 128, 74, 255), 0.0, 0.5),
    "terminal_blue": ((40, 92, 170, 255), 0.0, 0.5),
    "wire_brown": ((110, 66, 38, 255), 0.0, 0.6),
    "wire_red": ((200, 40, 36, 255), 0.0, 0.5),
    "wire_orange": ((236, 128, 32, 255), 0.0, 0.5),
    "wire_black": ((28, 28, 28, 255), 0.0, 0.6),
    "wire_yellow": ((230, 200, 40, 255), 0.0, 0.5),
    "cell_blue": ((44, 104, 180, 255), 0.0, 0.4),
    "cell_green": ((58, 128, 70, 255), 0.0, 0.4),
    "lipo_silver": ((170, 176, 184, 255), 0.6, 0.4),
    "lipo_label": ((34, 34, 38, 255), 0.0, 0.5),
    "heatshrink": ((32, 34, 38, 255), 0.0, 0.7),
    "led_red": ((255, 60, 50, 255), 0.0, 0.2),
    "transducer": ((198, 201, 204, 255), 0.85, 0.3),
    "mesh_black": ((36, 36, 38, 255), 0.0, 0.8),
    "pot_blue": ((40, 110, 210, 255), 0.0, 0.4),
    "rubber": ((40, 40, 40, 255), 0.0, 0.9),
}

CATEGORIES = {
    "printed": "Printed parts",
    "actuator": "Servos & motors",
    "electronics": "Boards & chips",
    "power": "Power",
    "hardware": "Screws, nuts & pins",
    "wiring": "Leads",
}


def _srgb_to_linear(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def material(name: str) -> PBRMaterial:
    """glTF base colours are LINEAR; the palette is written in sRGB (what the eye sees)."""
    rgba, metal, rough = PALETTE[name]
    lin = [_srgb_to_linear(v) for v in rgba[:3]] + [rgba[3] / 255.0]
    return PBRMaterial(name=name, baseColorFactor=lin, metallicFactor=metal, roughnessFactor=rough,
                       alphaMode="BLEND" if rgba[3] < 255 else "OPAQUE")


# --- primitive helpers (all return trimesh with a material) -----------------------------------
def _mat(m: trimesh.Trimesh, mat: str) -> trimesh.Trimesh:
    m.visual = TextureVisuals(material=material(mat))
    m.metadata["mat"] = mat
    return m


def box(x0, x1, y0, y1, z0, z1, mat):
    m = trimesh.creation.box(extents=(abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)))
    m.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    return _mat(m, mat)


def cyl(r, z0, z1, mat, x=0.0, y=0.0, sections=40, axis="z"):
    m = trimesh.creation.cylinder(radius=r, height=abs(z1 - z0), sections=sections)
    m.apply_translation((0, 0, (z0 + z1) / 2))
    if axis == "x":
        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, (0, 1, 0)))
    elif axis == "y":
        m.apply_transform(trimesh.transformations.rotation_matrix(-math.pi / 2, (1, 0, 0)))
    m.apply_translation((x, y, 0) if axis == "z" else (0, 0, 0))
    return _mat(m, mat)


def moved(m: trimesh.Trimesh, T) -> trimesh.Trimesh:
    m = m.copy()
    m.apply_transform(T)
    return m


def T(x=0.0, y=0.0, z=0.0):
    return trimesh.transformations.translation_matrix((x, y, z))


def Rz(deg):
    return trimesh.transformations.rotation_matrix(math.radians(deg), (0, 0, 1))


def Rx(deg):
    return trimesh.transformations.rotation_matrix(math.radians(deg), (1, 0, 0))


def Ry(deg):
    return trimesh.transformations.rotation_matrix(math.radians(deg), (0, 1, 0))


def merge_by_material(parts: list[trimesh.Trimesh]) -> list[trimesh.Trimesh]:
    """Concatenate pieces that share a material (fewer draw calls, smaller GLB)."""
    groups: dict[str, list] = {}
    for p in parts:
        groups.setdefault(p.metadata.get("mat", "steel"), []).append(p)
    out = []
    for mat, ms in groups.items():
        m = trimesh.util.concatenate(ms) if len(ms) > 1 else ms[0]
        out.append(_mat(m, mat))
    return out


def shape_to_mesh(shape, tol=0.08, ang=0.25, crease_deg=30.0) -> trimesh.Trimesh:
    """Tessellate a build123d shape and split vertices at sharp edges (crisp CAD shading)."""
    from build123d import export_stl
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "s.stl"
        export_stl(shape, str(p), tolerance=tol, angular_tolerance=ang)
        m = trimesh.load(p, force="mesh")
    m.merge_vertices()
    return trimesh.graph.smooth_shade(m, angle=math.radians(crease_deg))


# --- servos ---------------------------------------------------------------------------------
def servo_parts(s: ServoSpec, horn_angle: float = 0.0, body_mat: str | None = None, lead_len: float = 28.0,
                with_horn: bool = True, with_screws: bool = True) -> list[trimesh.Trimesh]:
    """Servo in the hobby_parts servo frame: origin on the shaft axis at the tab underside,
    +Z = shaft, +X towards the body end nearest the shaft."""
    big = s.length > 30
    body_mat = body_mat or ("servo_black" if big or s.name.startswith("MG9") else "servo_blue")
    x0, x1 = -(s.length - s.shaft_from_end), s.shaft_from_end
    zb, zt = -s.tab_height, s.case_top - s.tab_height
    xm = x0 + s.length / 2
    parts = [box(x0, x1, -s.width / 2, s.width / 2, zb, zt, body_mat),
             box(xm - s.tab_span / 2, xm + s.tab_span / 2, -s.width / 2, s.width / 2, 0, s.tab_t, body_mat)]
    # label band on both sides
    for sy in (-1, 1):
        y = sy * (s.width / 2 + 0.05)
        parts.append(box(x0 + 2, x1 - 2, y - 0.05, y + 0.05, zb + 0.35 * (zt - zb), zb + 0.75 * (zt - zb), "servo_label"))
    # top boss round the shaft and the output spline
    boss_r = min(s.width / 2 - 0.8, 6.0 if big else 3.6)
    spline_top = s.total_h - s.tab_height
    parts.append(cyl(boss_r, zt - 0.01, zt + 0.35 * (spline_top - zt), body_mat))
    parts.append(cyl(2.9 if big else 2.4, zt, spline_top, "brass" if (big or s.name.startswith("MG")) else "horn_white"))
    # tab screws
    if with_screws:
        ys = [0.0] if s.hole_dy == 0 else [-s.hole_dy / 2, s.hole_dy / 2]
        hr = 2.6 if big else 1.8
        for dx in (-s.hole_dx / 2, s.hole_dx / 2):
            for y in ys:
                parts.append(cyl(hr, s.tab_t, s.tab_t + (1.6 if big else 1.2), "steel", x=xm + dx, y=y, sections=20))
    # lead: brown/red/orange from the far end, low on the body
    zl = zb + (3.0 if big else 2.5)
    for i, c in enumerate(("wire_brown", "wire_red", "wire_orange")):
        yy = (i - 1) * 1.15
        parts.append(box(x0 - lead_len, x0 + 0.5, yy - 0.5, yy + 0.5, zl - 0.5, zl + 0.5, c))
    if with_horn:
        parts += [moved(p, Rz(horn_angle)) for p in horn_parts(s)]
    return merge_by_material(parts)


def horn_parts(s: ServoSpec) -> list[trimesh.Trimesh]:
    hz = horn_face_z(s)
    z0 = hz - s.horn_t
    parts = []
    if s.horn_kind == "disc":
        parts.append(cyl(s.horn_d / 2, z0, hz, "horn_white"))
    else:
        parts.append(cyl(s.horn_d / 2, z0, hz, "horn_white"))
        for sgn in ((1,) if s.horn_arms == 1 else (1, -1)):
            L = s.horn_arm_len
            n = 6
            for i in range(1, n + 1):
                t = i / n
                r = s.horn_d / 2 + (s.horn_tip_d / 2 - s.horn_d / 2) * t
                parts.append(cyl(r, z0, hz, "horn_white", x=sgn * L * t, sections=24))
            for k in range(1, 4):   # the horn's screw holes (dark dots)
                parts.append(cyl(0.55, hz - 0.01, hz + 0.02, "plastic_black", x=sgn * L * k / 3.5, sections=12))
    parts.append(cyl(1.1 if s.length < 30 else 1.6, hz - 0.01, hz + 0.05, "plastic_black", sections=16))   # centre screw
    return parts


# --- boards ---------------------------------------------------------------------------------
def esp32_parts(b: BoardSpec, n_pins: int | None = None, housings: bool = True) -> list[trimesh.Trimesh]:
    """ESP32 DevKit. Frame: x from 0 (USB end) to b.length, y centred, PCB bottom at z = 0,
    headers pointing down (-z)."""
    L, W, t = b.length, b.width, b.pcb_t
    n = n_pins or (19 if L > 53 else 15)
    p = [box(0, L, -W / 2, W / 2, 0, t, "pcb_black")]
    # WROOM-32 module at the far end: module PCB, can, antenna
    mx0 = L - 25.5
    p += [box(mx0, L, -9, 9, t, t + 0.8, "pcb_module"),
          box(mx0 + 0.6, mx0 + 18.0, -8.4, 8.4, t + 0.8, t + 3.1, "shield")]
    for k in range(5):     # antenna meander hint
        y = -6 + 3 * k
        p.append(box(mx0 + 19.0, L - 0.8, y - 0.25, y + 0.25, t + 0.8, t + 0.85, "gold"))
    # USB connector, USB-UART chip, regulator, buttons, LED
    p += [box(-0.6, 5.0, -3.9, 3.9, t, t + 2.7, "shield"),
          box(9.0, 14.0, 2.0, 7.0, t, t + 1.0, "chip"),
          box(7.5, 14.0, -8.5, -5.0, t, t + 1.6, "chip"), box(13.0, 14.0, -8.5, -5.0, t, t + 1.6, "steel"),
          box(1.5, 5.0, -11.0, -7.5, t, t + 1.6, "steel"), box(1.5, 5.0, 7.5, 11.0, t, t + 1.6, "steel"),
          box(2.6, 3.9, -9.9, -8.6, t + 1.6, t + 2.2, "plastic_black"), box(2.6, 3.9, 8.6, 9.9, t + 1.6, t + 2.2, "plastic_black"),
          box(17.0, 18.6, -4.0, -3.2, t, t + 0.6, "led_red")]
    # headers: plastic under the PCB, gold pins below and solder stubs above
    x_first = (L - (n - 1) * 2.54) / 2
    for sy in (-1, 1):
        y = sy * (W / 2 - 1.3)
        p.append(box(x_first - 1.27, x_first + (n - 1) * 2.54 + 1.27, y - 1.27, y + 1.27, -2.5, 0, "plastic_black"))
        for i in range(n):
            x = x_first + i * 2.54
            p.append(box(x - 0.32, x + 0.32, y - 0.32, y + 0.32, -8.5, t + 1.0, "gold"))
            if housings:
                p.append(box(x - 1.25, x + 1.25, y - 1.25, y + 1.25, -16.5, -2.6, "plastic_black"))
    return merge_by_material(p)


def pca9685_parts() -> list[trimesh.Trimesh]:
    """PCA9685 16-channel board. Frame: centre of the PCB bottom; x along 62.5, servo headers
    along +y, pins up."""
    L, W, t = 62.5, 25.4, 1.6
    p = [box(-L / 2, L / 2, -W / 2, W / 2, 0, t, "pcb_blue"),
         box(-5.0, 5.0, -7.5, -3.0, t, t + 1.2, "chip"),
         box(-L / 2 + 2, -L / 2 + 9.5, -6.0, 6.0, t, t + 10.0, "terminal_blue"),   # V+ terminal block
         box(-L / 2 + 3.0, -L / 2 + 5.5, -9.0, -7.0, t, t + 2.0, "led_red")]
    # 16 servo headers in 4 groups of 4, 3 rows (GND/V+/PWM), plus 6-pin headers at each end
    x = -22.0
    for g in range(4):
        for c in range(4):
            xc = x + c * 2.54
            p.append(box(xc - 1.27, xc + 1.27, W / 2 - 8.6, W / 2 - 1.0, t, t + 2.5, "plastic_black"))
            for r in range(3):
                yc = W / 2 - 7.3 + r * 2.54
                p.append(box(xc - 0.32, xc + 0.32, yc - 0.32, yc + 0.32, t, t + 8.5, "gold"))
        x += 4 * 2.54 + 2.6
    for sx in (-1, 1):
        xe = sx * (L / 2 - 2.5)
        p.append(box(xe - 1.27, xe + 1.27, -7.6, 7.6, t, t + 2.5, "plastic_black"))
        for r in range(6):
            yc = -6.35 + r * 2.54
            p.append(box(xe - 0.32, xe + 0.32, yc - 0.32, yc + 0.32, t, t + 8.5, "gold"))
    return merge_by_material(p)


def tb6612_parts() -> list[trimesh.Trimesh]:
    """TB6612FNG carrier (Pololu size) standing on a breadboard. Frame: PCB bottom centre."""
    L, W, t = 20.3, 15.2, 1.6
    p = [box(-L / 2, L / 2, -W / 2, W / 2, 0, t, "pcb_red"), box(-3.9, 3.9, -2.8, 2.8, t, t + 1.4, "chip")]
    for sy in (-1, 1):
        y = sy * (W / 2 - 1.27)
        p.append(box(-L / 2 + 0.2, L / 2 - 0.2, y - 1.27, y + 1.27, -2.5, 0, "plastic_black"))
        for i in range(8):
            x = -L / 2 + 1.27 + i * 2.54
            p.append(box(x - 0.32, x + 0.32, y - 0.32, y + 0.32, -8.5, t + 0.8, "gold"))
    return merge_by_material(p)


def breadboard_parts(L=47.0, W=35.0, H=8.5) -> list[trimesh.Trimesh]:
    """170-point mini breadboard. Frame: bottom centre."""
    p = [box(-L / 2, L / 2, -W / 2, W / 2, 0, H, "plastic_white"), box(-L / 2, L / 2, -1.0, 1.0, H - 0.6, H + 0.01, "steel")]
    for i in range(17):
        x = -L / 2 + 3.2 + i * 2.54
        for j in range(5):
            for sy in (-1, 1):
                y = sy * (2.6 + j * 2.54)
                p.append(box(x - 0.45, x + 0.45, y - 0.45, y + 0.45, H - 0.3, H + 0.02, "plastic_black"))
    return merge_by_material(p)


def buck_parts() -> list[trimesh.Trimesh]:
    """MP1584 buck module. Frame: PCB bottom centre, 22 × 17."""
    return merge_by_material([box(-11, 11, -8.5, 8.5, 0, 1.2, "pcb_blue"), box(-3, 3, -3, 3, 1.2, 4.2, "chip"),
                              box(5, 9, 2, 6, 1.2, 4.0, "pot_blue"), box(-9, -6, -6, -3, 1.2, 2.5, "plastic_black"),
                              box(-9, -6, 3, 6, 1.2, 2.5, "plastic_black")])


def ubec_parts() -> list[trimesh.Trimesh]:
    """6 V 5 A UBEC in heatshrink with leads. Frame: bottom centre, 45 × 20 × 9."""
    p = [box(-22.5, 22.5, -10, 10, 0, 9, "heatshrink")]
    for i, c in enumerate(("wire_red", "wire_black")):
        y = (i - 0.5) * 2.4
        p.append(box(22.5, 52.0, y - 0.9, y + 0.9, 3.6, 5.4, c))
        p.append(box(-52.0, -22.5, y - 0.9, y + 0.9, 3.6, 5.4, c))
    return merge_by_material(p)


def hcsr04_parts() -> list[trimesh.Trimesh]:
    """HC-SR04. Frame: PCB centre on its FRONT face; transducers point +X, PCB in the YZ plane."""
    p = [box(-1.6, 0, -22.5, 22.5, -10, 10, "pcb_blue"), box(0, 2.5, -3.0, 3.0, 4.5, 7.5, "transducer")]
    for sy in (-1, 1):
        p.append(cyl(8.0, 0, 12.0, "transducer", axis="x").apply_translation((0, sy * 13.0, 0)) or None)
    p = [q for q in p if q is not None]
    for sy in (-1, 1):
        d = cyl(6.8, 11.9, 12.05, "mesh_black", axis="x")
        d.apply_translation((0, sy * 13.0, 0))
        p.append(d)
    for i in range(4):
        y = -3.81 + i * 2.54
        p.append(box(-9.0, -1.6, y - 0.32, y + 0.32, -9.2, -8.6, "gold"))
    return merge_by_material(p)


# --- motors, power, switches -----------------------------------------------------------------
def n20_parts(m: GearMotorSpec, lead_len: float = 20.0) -> list[trimesh.Trimesh]:
    """N20 gear motor in its frame (origin at the gearbox face on the shaft axis, +Z out of the
    gearbox, gearbox 12 mm side along X)."""
    p = [box(-m.gb_w / 2, m.gb_w / 2, -m.gb_h / 2, m.gb_h / 2, -m.gb_len, 0, "brass"),
         box(-m.gb_w / 2 - 0.05, m.gb_w / 2 + 0.05, -m.gb_h / 2 - 0.05, m.gb_h / 2 + 0.05, -0.8, 0, "steel"),
         box(-m.gb_w / 2 - 0.05, m.gb_w / 2 + 0.05, -m.gb_h / 2 - 0.05, m.gb_h / 2 + 0.05, -m.gb_len, -m.gb_len + 0.8, "steel")]
    can = trimesh.creation.cylinder(radius=m.can_d / 2, height=m.can_len, sections=40)
    can = trimesh.boolean.intersection([can, trimesh.creation.box((m.can_d, m.can_flat, m.can_len + 1))], engine="manifold")
    can.apply_translation((0, 0, -m.gb_len - m.can_len / 2))
    p.append(_mat(can, "steel"))
    p.append(box(-4.5, 4.5, -m.can_flat / 2 + 0.6, m.can_flat / 2 - 0.6, -m.gb_len - m.can_len - 1.4, -m.gb_len - m.can_len,
                 "plastic_black"))
    for sx in (-1, 1):
        p.append(box(sx * 2.6 - 0.6, sx * 2.6 + 0.6, -0.2, 0.2, -m.gb_len - m.can_len - m.term_len - 1.4, -m.gb_len - m.can_len,
                     "copper"))
        p.append(box(sx * 2.6 - 0.6, sx * 2.6 + 0.6, -0.6, 0.6, -m.gb_len - m.can_len - m.term_len - 1.4 - lead_len,
                     -m.gb_len - m.can_len - m.term_len - 1.0, "wire_red" if sx > 0 else "wire_black"))
    p.append(cyl(m.boss_d / 2, 0, m.boss_h, "brass"))
    shaft = trimesh.creation.cylinder(radius=m.shaft_d / 2, height=m.shaft_len, sections=24)
    keep = trimesh.creation.box((m.shaft_d, m.shaft_flat, m.shaft_len + 1))
    keep.apply_translation((0, -(m.shaft_d - m.shaft_flat) / 2, 0))
    shaft = trimesh.boolean.intersection([shaft, keep], engine="manifold")
    shaft.apply_translation((0, 0, m.shaft_len / 2))
    p.append(_mat(shaft, "steel"))
    return merge_by_material(p)


def holder_2x18650_parts(L=77.0, W=41.0, H=21.0) -> list[trimesh.Trimesh]:
    """2 × 18650 holder with cells. Frame: bottom centre, cells along X."""
    p = [box(-L / 2, L / 2, -W / 2, W / 2, 0, 3.0, "plastic_black"),
         box(-L / 2, -L / 2 + 3, -W / 2, W / 2, 0, H, "plastic_black"),
         box(L / 2 - 3, L / 2, -W / 2, W / 2, 0, H, "plastic_black"),
         box(-L / 2, L / 2, -W / 2, -W / 2 + 1.5, 0, 12, "plastic_black"),
         box(-L / 2, L / 2, W / 2 - 1.5, W / 2, 0, 12, "plastic_black"),
         box(-L / 2, L / 2, -0.8, 0.8, 0, 12, "plastic_black")]
    for sy, mat in ((-1, "cell_blue"), (1, "cell_green")):
        y = sy * 10.0
        p.append(cyl(9.2, -32.5, 32.5, mat, axis="x").apply_translation((0, y, 3.0 + 9.2)) or None)
        p.append(cyl(4.0, 32.5, 33.5, "steel", axis="x").apply_translation((0, y, 3.0 + 9.2)) or None)
    p = [q for q in p if q is not None]
    for i, c in enumerate(("wire_red", "wire_black")):
        y = (i - 0.5) * 3.0
        p.append(box(L / 2, L / 2 + 25, y - 0.9, y + 0.9, 4, 5.8, c))
    return merge_by_material(p)


def lipo_parts(L=70.0, W=35.0, H=18.0) -> list[trimesh.Trimesh]:
    """2S LiPo pack with leads and an XT30. Frame: bottom centre, long side along X."""
    p = [box(-L / 2, L / 2, -W / 2, W / 2, 0, H, "lipo_silver"),
         box(-L / 2 + 6, L / 2 - 6, -W / 2 - 0.05, W / 2 + 0.05, 3, H - 3, "lipo_label")]
    for i, c in enumerate(("wire_red", "wire_black")):
        y = (i - 0.5) * 3.2
        p.append(box(L / 2, L / 2 + 30, y - 1.0, y + 1.0, H / 2 - 1, H / 2 + 1, c))
    p.append(box(L / 2 + 30, L / 2 + 40, -4, 4, H / 2 - 2.5, H / 2 + 2.5, "wire_yellow"))
    p.append(box(L / 2, L / 2 + 18, 9, 12, H / 2 - 1, H / 2 + 1, "plastic_white"))
    return merge_by_material(p)


def toggle_switch_parts() -> list[trimesh.Trimesh]:
    """MTS-102 mini toggle. Frame: on the panel's outer face, bushing along +X out of the panel."""
    return merge_by_material([cyl(3.0, -6.0, 9.0, "steel", axis="x"), cyl(4.6, 0.0, 2.2, "steel", axis="x", sections=6),
                              box(-6.0 - 10.0, -6.0, -6.5, 6.5, -4.0, 4.0, "plastic_black"),
                              moved(cyl(1.3, 9.0, 21.0, "steel", axis="x"), Rz(-15) @ T(0, 0, 0))])


def dc_jack_parts() -> list[trimesh.Trimesh]:
    """5.5 × 2.1 panel jack. Frame: on the panel's outer face, axis +X out of the panel."""
    return merge_by_material([cyl(5.5, -14.0, 2.0, "plastic_black", axis="x"), cyl(7.0, -4.8, -2.8, "steel", axis="x", sections=6),
                              cyl(3.0, 1.9, 2.05, "steel", axis="x")])


def capacitor_parts(d=10.0, h=16.0) -> list[trimesh.Trimesh]:
    return merge_by_material([cyl(d / 2, 0, h, "terminal_blue"), cyl(d / 2 - 0.6, h - 0.01, h + 0.05, "steel")])


# --- fasteners ------------------------------------------------------------------------------
def screw_parts(d: float, length: float, head="pan", mat="steel") -> list[trimesh.Trimesh]:
    """Screw along -Z from its head's underside at z = 0 (head above, z > 0)."""
    hd, hh = (d * 1.9, d * 0.7) if head == "pan" else (d * 1.6, d)
    return merge_by_material([cyl(hd / 2, 0, hh, mat, sections=24), cyl(d / 2 * 0.92, -length, 0.01, mat, sections=16)])


def nut_parts(d: float, mat="steel", nyloc=False) -> list[trimesh.Trimesh]:
    af = {2.0: 4.0, 2.5: 5.0, 3.0: 5.5}.get(d, d * 1.8)
    h = {2.0: 1.6, 2.5: 2.0, 3.0: 2.4}.get(d, d * 0.8) * (1.6 if nyloc else 1.0)
    nut = trimesh.creation.cylinder(radius=af / math.sqrt(3), height=h, sections=6)
    nut.apply_translation((0, 0, h / 2))
    hole = trimesh.creation.cylinder(radius=d / 2, height=h + 1, sections=16)
    hole.apply_translation((0, 0, h / 2))
    nut = trimesh.boolean.difference([nut, hole], engine="manifold")
    parts = [_mat(nut, mat)]
    if nyloc:
        parts.append(cyl(af / 2 - 0.3, h * 0.62, h + 0.05, "terminal_blue", sections=20))
    return merge_by_material(parts)


def washer_parts(d: float, od: float | None = None, t: float = 0.5) -> list[trimesh.Trimesh]:
    od = od or d * 2.1
    w = trimesh.creation.annulus(r_min=d / 2 + 0.1, r_max=od / 2, height=t, sections=32)
    w.apply_translation((0, 0, t / 2))
    return [_mat(w, "steel")]


def trimmed_horn_parts(s: ServoSpec, trim_r: float) -> list[trimesh.Trimesh]:
    """A double/single-arm horn with its arms cut `trim_r` from the centre (inside a pinion).
    Same frame as horn_parts (servo frame, horn face at horn_face_z)."""
    hz = horn_face_z(s)
    z0 = hz - s.horn_t
    parts = [cyl(s.horn_d / 2, z0, hz, "horn_white"), cyl(s.horn_d / 2 * 0.95, z0 - 2.0, z0, "horn_white")]  # hub + boss
    w = s.horn_d * 0.8
    for sgn in ((1,) if s.horn_arms == 1 else (1, -1)):
        parts.append(box(min(0, sgn * trim_r), max(0, sgn * trim_r), -w / 2, w / 2, z0, hz, "horn_white"))
    return merge_by_material(parts)


def brio4k_parts(cable_len: float = 30.0) -> list[trimesh.Trimesh]:
    """Logitech Brio 4K (clip removed). Frame: origin at the 1/4"-20 thread on the bottom face,
    +X = lens direction, +Y = long axis, +Z = up; body x ±13.5, y ±51, z 0..27."""
    from build123d import Axis, Box as BBox, Pos as BPos, fillet
    body = BPos(0, 0, 13.5) * BBox(27.0, 102.0, 27.0)
    body = fillet(body.edges().filter_by(Axis.Y), radius=6.0)
    body = fillet(body.edges().filter_by(Axis.X) + body.edges().filter_by(Axis.Z), radius=2.0)
    p = [_mat(shape_to_mesh(body, tol=0.05), "plastic_black")]
    p.append(box(13.45, 13.6, -40.0, 40.0, 6.0, 21.0, "chip"))                         # glossy front panel
    p.append(cyl(7.2, 13.5, 14.0, "black_oxide", y=0.0, axis="x").apply_translation((0, 0, 13.5)))   # lens ring
    p.append(cyl(5.0, 13.6, 14.1, "chip", axis="x").apply_translation((0, 0, 13.5)))                # lens glass
    for y in (-24.0, 24.0):                                                             # IR sensor windows
        p.append(cyl(2.4, 13.55, 13.7, "led_red", axis="x").apply_translation((0, y, 13.5)))
    p.append(cyl(0.9, 13.55, 13.75, "plastic_white", axis="x").apply_translation((0, 9.0, 13.5)))  # status LED
    p.append(box(-3.0, 3.0, 50.9, 51.1, 11.0, 16.0, "plastic_black"))                  # USB-C socket (+Y end)
    p.append(box(-3.5, 3.5, 51.0, 59.0, 10.0, 17.0, "plastic_black"))                  # USB-C plug
    p.append(cyl(2.0, 59.0, 59.0 + cable_len, "wire_black", axis="y").apply_translation((0, 0, 13.5)))  # cable stub
    return merge_by_material([q for q in p if q is not None])


def thumb_screw_parts(d: float = 6.35, length: float = 9.5, head_d: float = 16.0, head_h: float = 5.0) -> list[trimesh.Trimesh]:
    """Knurled thumb screw (1/4"-20 by default) along +Z from the head's top face at z = 0
    (head below, z < 0): for screwing UP into a camera from under its seat."""
    return merge_by_material([cyl(head_d / 2, -head_h, 0, "black_oxide", sections=36),
                              cyl(d / 2 * 0.92, 0, length, "steel", sections=20)])


# --- scene ----------------------------------------------------------------------------------
class VizScene:
    """Node hierarchy + reusable geometry -> GLB, plus metadata for the viewer."""

    def __init__(self):
        self.scene = trimesh.Scene()
        self.base = self.scene.graph.base_frame
        self.meta: dict[str, dict] = {}
        self._geom: set[str] = set()
        self._count = 0

    def group(self, name: str, parent: str | None = None, matrix=None) -> str:
        self.scene.graph.update(frame_from=parent or self.base, frame_to=name,
                                matrix=np.eye(4) if matrix is None else np.asarray(matrix, float))
        return name

    def add(self, key: str, meshes: list[trimesh.Trimesh], parent: str | None, matrix=None,
            label: str = "", category: str = "printed", node: str | None = None, info: str = "") -> str:
        """Add one part (a list of meshes, one per material) as a group node under `parent`.
        `key` names the reusable geometry: the same key reuses the meshes already stored."""
        self._count += 1
        node = node or f"{key}_{self._count:03d}"
        self.group(node, parent, matrix)
        for i, m in enumerate(meshes):
            gname = f"{key}__{i}"
            if gname not in self._geom:
                self.scene.add_geometry(m, geom_name=gname, node_name=f"{node}__{i}", parent_node_name=node)
                self._geom.add(gname)
            else:
                self.scene.graph.update(frame_from=node, frame_to=f"{node}__{i}", matrix=np.eye(4), geometry=gname)
        self.meta[node] = {"label": label or key, "category": category, "info": info}
        return node

    def export(self, path: Path) -> int:
        data = self.scene.export(file_type="glb", include_normals=True)
        Path(path).write_bytes(data)
        return len(data)

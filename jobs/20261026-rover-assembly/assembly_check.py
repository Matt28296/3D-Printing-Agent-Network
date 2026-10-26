"""Assembly check for the tracked rover (round 5).

Builds both 34-link track loops pin by pin (13 pins on the bottom run, 5 round the idler, 12 on the
top run, 4 round the sprocket) and places every printed part with the bought parts that meet it:
- each N20 as the detailed dummy (gearbox, can, end cap, solder tabs, the Ø4 × 0.8 bearing boss and
  the D-shaft), rolled 45° about its shaft, gearbox face on its skin at |y| 44 (round 4: 2 mm skin);
- the idler clamp's two 20.6 × 10 × 2 steel plates per side (round 5: twins, each slotted from 6 to
  18 mm along): a head plate resting on the floor of its idler-block recess under the Ø9 head washer,
  and a nut plate resting on its lip on the wall's outer face between its end stops, under a Ø9 washer
  and the wall nut. The plates stay put while the idler hardware is moved to both slot ends;
- the Pololu #1996 hub on the shaft (|y| 46.5-51.5), its thrust washer, and the 4 × M3 × 12 sprocket
  screws with their washers;
- the axle bolts as fitted: M3 socket-head screws (class 12.9, fully threaded), head on its washer on
  the boss face (ISO 7089 for the road wheels; DIN 9021 Ø9 on the head plate for the idlers), then
  for a road wheel: nut in the wall trap, washer, wheel, washer, nyloc (M3 × 50); for an idler (round
  5): head plate, wall, nut plate, Ø9 washer, wall nut, washer, idler (hub from |y| 43.7), washer,
  nyloc (M3 × 40);
- the M3 × 20 jack screws bearing on the idler-bolt heads;
- the battery holder at 80 mm (the longest allowed) with its velcro strap, the HC-SR04 with its four
  pins bent back and the leads soldered on, the ESP32 with jumper housings, the breadboard and TB6612,
  the buck under the lid, the toggle switch on the lid, the heat-set inserts and the lid screws.
Nothing is exempt: every pair of bodies is intersected, and more than TOL mm³ is a collision. Parts
that only touch (gearbox face on the skin, shaft in the hub bore, heads on washers) intersect in ~0.
Screw shanks are Ø2.8 proxies, the jack screw Ø2.7 (it forms its thread in a Ø2.8 CAD pilot) and the
hub bore Ø3.1, so tessellation can't fake a contact.
Also checked: tooth engagement; the fastener stacks (thread past each nyloc, wall-nut engagement for
fully and for partly threaded bolts, hub-screw and jack-screw engagement); the idler and its jack
screw at both slot ends; both idler plates' slots and Ø9 washers over the whole slot travel; a motor
with an 11 mm gearbox; the shortest allowed shaft (9.6 mm from the gearbox face) and the specified
10 mm; the tool paths for the jack screw and the hub set screw.

Run from the project root:  python jobs/20261026-rover-assembly/assembly_check.py
"""
from __future__ import annotations

import importlib.util
import itertools
import json
import math
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / "tools"), str(HERE)]
from build123d import Align, Box, Cylinder, Pos, Rot, export_stl  # noqa: E402
from cadlib import hex_nut_pocket  # noqa: E402
from hobby_parts import (BATT_2X18650_LONG, ESP32_DEVKIT_38, MINI_BREADBOARD, MP1584_BUCK, TB6612_CARRIER,  # noqa: E402
                         gearmotor_dummy, mounting_hub_dummy)
import rover_frame as F  # noqa: E402

TOL = 0.5
JOBS = {"chassis": "20261026-rover-chassis", "lid": "20261026-rover-lid", "sprocket": "20261026-rover-sprocket",
        "idler": "20261026-rover-idler", "wheel": "20261026-rover-wheel", "link": "20261026-rover-track-link"}
SHANK_D = 2.8                 # screw/bolt shank proxy (M3) in the collision model
C, MIN = Align.CENTER, Align.MIN
ISO4762_B = 18.0              # thread length of a partly threaded M3 ISO 4762 screw longer than ~25 mm
JACK_L = 20.0                 # M3 × 20 set screw (DIN 913)
JACK_PROXY_D = 2.7            # jack screw in the collision model (it taps its own thread in the Ø2.8 CAD pilot)
KEY_ANGLE = 25.0              # ball-end hex key: up to 25° off the screw axis


def load(job):
    p = ROOT / "jobs" / job / "model.py"
    spec = importlib.util.spec_from_file_location(f"m_{job.replace('-', '_')}", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def to_mesh(shape, tol=0.05):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "s.stl"
        export_stl(shape, str(p), tolerance=tol, angular_tolerance=0.2)
        return trimesh.load(p, force="mesh")


def frame(origin, x_dir, z_dir):
    x = np.asarray(x_dir, float); x /= np.linalg.norm(x)
    z = np.asarray(z_dir, float); z /= np.linalg.norm(z)
    y = np.cross(z, x)
    m = np.eye(4); m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = x, y, z, origin
    return m


def tr(x=0.0, y=0.0, z=0.0):
    m = np.eye(4); m[:3, 3] = (x, y, z)
    return m


def ax(x, y, s, outward=True):
    """Frame on a Y-axis at (x, y, Z_A): +z points outward (+sY) or inward."""
    return frame((x, y, F.Z_A), (1, 0, 0), (0, s if outward else -s, 0))


def track_pins():
    """Pin centres (x, z) round one loop, in travel order."""
    za, rp = F.Z_A, F.RP
    pins = [(i * F.P, za - rp) for i in range(13)]                                 # bottom run 0..120
    pins += [(F.AXLE_DX + rp * math.cos(math.radians(-90 + 36 * k)), za + rp * math.sin(math.radians(-90 + 36 * k)))
             for k in range(1, 6)]                                                  # idler wrap to the top
    pins += [(F.AXLE_DX - i * F.P, za + rp) for i in range(1, 13)]                  # top run 110..0
    pins += [(rp * math.cos(math.radians(90 + 36 * k)), za + rp * math.sin(math.radians(90 + 36 * k)))
             for k in range(1, 5)]                                                  # sprocket wrap
    assert len(pins) == F.N_LINKS, len(pins)
    return pins


# --- bought-part dummies (build123d, each in its own frame) -------------------------------------
def screw_dummy(length, head=F.SCREW_HEAD):
    """Socket-head screw: head z 0..k above its underside at z = 0, shank down to z = -length."""
    hd, hh = head
    return Cylinder(hd / 2, hh, align=(C, C, MIN)) + Pos(0, 0, -length) * Cylinder(SHANK_D / 2, length + 0.01, align=(C, C, MIN))


def washer_dummy(od, t, idd=3.2):
    return Cylinder(od / 2, t, align=(C, C, MIN)) - Pos(0, 0, -1) * Cylinder(idd / 2, t + 2, align=(C, C, MIN))


def nut_dummy(af, h):
    return hex_nut_pocket(af, h, clearance=0) - Pos(0, 0, -1) * Cylinder(1.5, h + 2, align=(C, C, MIN))


def rod_x(x0, x1, y, z, d):
    return Pos((x0 + x1) / 2, y, z) * Rot(0, 90, 0) * Cylinder(d / 2, abs(x1 - x0))


def plate_slot_dx(length):
    """x of a plate's slot centre from the plate's centre: the slot runs from PLATE_SLOT_FROM to PLATE_SLOT_FROM +
    PLATE_SLOT[1] along the plate, measured from its rear end (+1.7 on the 20.6 plates)."""
    return F.PLATE_SLOT_FROM + F.PLATE_SLOT[1] / 2 - length / 2


def plate_dummy(length, height, slot_dx=0.0):
    """Idler clamp plate: length (x) × PLATE_T (y) × height (z), centred on its origin, with the
    PLATE_SLOT slot (width along z, overall length along x) centred at x = slot_dx."""
    w, sl = F.PLATE_SLOT
    cut = Pos(slot_dx, 0, 0) * Box(sl - w, F.PLATE_T + 2, w)
    for sx in (-1, 1):
        cut += Pos(slot_dx + sx * (sl - w) / 2, 0, 0) * Rot(90, 0, 0) * Cylinder(w / 2, F.PLATE_T + 2)
    return Box(length, F.PLATE_T, height) - cut


def hcsr04_dummy(hx, sz):
    """HC-SR04 behind the front wall: PCB x hx-13.3..hx-11.7, transducers to the wall, crystal can,
    and its 4 header pins bent 90° rearward with the leads soldered on and heat-shrunk (about 10 mm
    behind the board), the leads then running up behind it."""
    x_pcb = hx - 12.5 - 0.8
    s = Pos(x_pcb, 0, sz) * Box(1.6, 45, 20)
    for sy in (-13.0, 13.0):
        s += Pos(hx - 12.0 + 6.0, sy, sz) * Rot(0, 90, 0) * Cylinder(8.0, 12.0)
    x_back, z_edge = x_pcb - 0.8, sz - 10.0
    s += Pos(x_back - 5.0 + 0.4, 0, z_edge - 1.25) * Box(10.8, 10.2, 3.5)       # pins bent back + solder + heat-shrink
    s += Pos(x_back - 8.5, 0, (z_edge + 0.5 + sz + 10.0) / 2) * Box(3.0, 10.2, sz + 10.0 - z_edge - 0.5)   # leads up
    return s


def toggle_dummy(x, y, z_top_face, deck_t):
    """MTS-102 on the lid, lever up: body under the deck, inner nut, bushing, outer nut, lever."""
    z0 = z_top_face
    s = Pos(x, y, z0 - 6.0 - 5.0) * Box(13.0, 8.0, 10.0)                    # body, 6 mm below the top face
    s += Pos(x, y, z0 - 16.0 - 2.0) * Box(8.0, 4.0, 4.0)                    # solder lugs
    s += Pos(x, y, z0 - deck_t - 2.2) * Cylinder(4.6, 2.2, align=(C, C, MIN))   # inner nut
    s += Pos(x, y, z0 - 6.0) * Cylinder(3.0, 15.0, align=(C, C, MIN))       # M6 bushing
    s += Pos(x, y, z0) * Cylinder(4.6, 2.2, align=(C, C, MIN))              # outer nut
    s += Pos(x, y, z0 + 9.0) * Cylinder(1.3, 12.0, align=(C, C, MIN))       # lever
    return s


def main():
    mods = {k: load(v) for k, v in JOBS.items()}
    ch, lid, spm, wm, lm = mods["chassis"], mods["lid"], mods["sprocket"], mods["wheel"], mods["link"]
    print("tessellating ...", flush=True)
    M = {k: to_mesh(m.design()) for k, m in mods.items()}
    M["motor"] = to_mesh(gearmotor_dummy(F.MOTOR, detailed=True), tol=0.02)
    hub = replace(F.HUB, bore=F.HUB.bore + 0.1)
    M["hub"] = to_mesh(mounting_hub_dummy(hub, hole_angle_deg=spm.SLOT_ANGLE0), tol=0.02)
    M["thrust_washer"] = to_mesh(washer_dummy(*F.WASHER), tol=0.02)
    M["hub_screw"] = to_mesh(screw_dummy(F.HUB_SCREW_L), tol=0.02)
    M["washer"] = to_mesh(washer_dummy(*F.WASHER), tol=0.02)
    M["washer_wide"] = to_mesh(washer_dummy(*F.WASHER_WIDE), tol=0.02)
    M["road_bolt"] = to_mesh(screw_dummy(F.ROAD_BOLT_L), tol=0.02)
    M["idler_bolt"] = to_mesh(screw_dummy(F.IDLER_BOLT_L), tol=0.02)
    M["nut"] = to_mesh(nut_dummy(*F.NUT), tol=0.02)
    M["nyloc"] = to_mesh(nut_dummy(*F.NYLOC), tol=0.02)
    M["insert"] = to_mesh(Cylinder(1.95, 5.7, align=(C, C, MIN)) - Pos(0, 0, -1) * Cylinder(1.5, 8, align=(C, C, MIN)), tol=0.02)
    M["lid_screw"] = to_mesh(screw_dummy(8.0), tol=0.02)
    # idler clamp plates (round 5): the head plate centred in its recess, the nut plate (its twin) centred between its
    # end stops on the wall's outer face; both rest on their floor / lip at Z_A - 5.2 and stay put while the bolt slides
    x_head_plate = sum(ch.PLATE_RECESS_X) / 2                     # 118.5: x 108.2-128.8
    x_nut_plate = sum(ch.NUT_PLATE_X) / 2                         # 118.5: x 108.2-128.8
    y_head_plate = F.HALF_W_OUT - F.WALL - F.BOSS_IN + F.PLATE_T / 2            # 29.0: recess |y| 28-30
    y_nut_plate = F.HALF_W_OUT + F.PLATE_T / 2                                  # 39.0: on the outer face, |y| 38-40
    z_head_plate = F.Z_A - ch.PLATE_RECESS_Z + F.IDLER_PLATE[1] / 2             # Z_A - 0.2: on the recess floor
    z_nut_plate = F.Z_A - ch.LIP_DZ + F.NUT_PLATE[1] / 2                        # Z_A - 0.2: on the lip
    M["plate_head"] = to_mesh(plate_dummy(*F.IDLER_PLATE, slot_dx=plate_slot_dx(F.IDLER_PLATE[0])), tol=0.02)
    M["plate_nut"] = to_mesh(plate_dummy(*F.NUT_PLATE, slot_dx=plate_slot_dx(F.NUT_PLATE[0])), tol=0.02)

    floor_top = F.FLOOR_Z + F.FLOOR_T
    b = BATT_2X18650_LONG
    x0b = ch.BATT_X0
    fixed = {}
    fixed["battery"] = to_mesh(Pos(x0b + b.length / 2, 0, floor_top + b.height / 2 + 0.01) * Box(b.length, b.width - 0.2, b.height))
    xs = ch.BATT_X0 + ch.BATT_LEN / 2
    top = floor_top + b.height + 0.02
    sy_in, sy_out = ch.STRAP_Y - 0.7, ch.STRAP_Y + 0.7      # 1.4 mm strap in the 3 mm floor slot
    half = [(sy_in, F.FLOOR_Z - 1.5), (sy_out, F.FLOOR_Z - 1.5), (sy_out, floor_top), (b.width / 2 + 1.5, top + 1.5),
            (0, top + 1.5), (0, top), (b.width / 2, top), (sy_in, floor_top)]   # up the slot, slanting to the holder's top edge
    from build123d import BuildPart, BuildSketch, Plane, Polygon, extrude
    strap = None
    for sy in (1, -1):
        with BuildPart() as bp:
            with BuildSketch(Plane.YZ.offset(xs - 10)):
                Polygon(*[(sy * yy, zz) for yy, zz in half], align=None)
            extrude(amount=20)
        strap = bp.part if strap is None else strap + bp.part
    strap += Pos(xs, 0, F.FLOOR_Z - 0.75) * Box(20, 2 * sy_out, 1.5)                    # under the floor
    fixed["strap"] = to_mesh(strap)
    hx = F.X_FRONT_OUT - F.WALL
    fixed["hcsr04"] = to_mesh(hcsr04_dummy(hx, ch.SENSOR_Z))
    e = ESP32_DEVKIT_38
    zpcb = F.TOP_Z + lid.T + lid.LEDGE_H
    esp = Pos(lid.USB_END_X + e.length / 2, 0, zpcb + e.pcb_t / 2) * Box(e.length, e.width, e.pcb_t)
    pins_len = e.length - 2 * 4.34 + 2.54
    for sy in (-1, 1):   # header plastic + female jumper housings below each pin row
        esp += Pos(lid.USB_END_X + e.length / 2, sy * (e.width / 2 - 1.3), zpcb - 16.5 / 2) * Box(pins_len, 2.54, 16.5)
    esp += Pos(lid.USB_END_X + 9 + 9, 0, zpcb + e.pcb_t + 1.6) * Box(18, 16, 3.2)
    fixed["esp32"] = to_mesh(esp)
    bb = MINI_BREADBOARD
    bbx, bbz = lid.BB_X0 + bb.length / 2, F.TOP_Z + lid.T
    fixed["breadboard"] = to_mesh(Pos(bbx, 0, bbz + bb.height / 2 + 0.01) * Box(bb.length, bb.width, bb.height))
    tb = TB6612_CARRIER
    fixed["tb6612"] = to_mesh(Pos(bbx - 11, -4, bbz + bb.height + 0.02 + 2.0) * Box(tb.width, tb.length, 4.0))
    bk = MP1584_BUCK
    BUCK_X0 = 85.0
    fixed["buck"] = to_mesh(Pos(BUCK_X0 + bk.length / 2, 0, F.TOP_Z - bk.height / 2 - 0.01) * Box(bk.length, bk.width, bk.height))
    sw_x, sw_y = lid.SWITCH
    fixed["toggle"] = to_mesh(toggle_dummy(sw_x, sw_y, F.TOP_Z + lid.T, lid.T))

    P = {"chassis": np.eye(4), "lid": np.eye(4)}
    for k in fixed:
        P[k] = np.eye(4)
    for i, (x, y) in enumerate(F.LID_SCREWS):
        P[f"insert{i}"] = tr(x, y, F.TOP_Z - 5.7)
        P[f"lid_screw{i}"] = tr(x, y, F.TOP_Z + lid.T)
    wheel_h = wm.RIM_HALF + wm.CONE_RISE + wm.FLANGE_FLAT          # 16.0: wheel half width
    y_head_road = F.HALF_W_OUT - F.WALL - F.BOSS_IN - F.WASHER[1]  # 27.5
    y_head_idler = ch.IDLER_HEAD_Y1                                # 27.2
    y_trap = F.HALF_W_OUT - ch.NUT_DEPTH                           # 35.4: road-wheel nut pulled to the trap bottom
    y_nut_washer_idler = F.HALF_W_OUT + F.PLATE_T                  # 40.0: Ø9 washer on the nut plate (round 5)
    y_nut_idler = y_nut_washer_idler + F.WASHER_WIDE[1]            # 40.8: idler wall nut on its Ø9 washer
    y_run_idler = y_nut_idler + F.NUT[1]                           # 43.2: running washer on the wall nut

    def axle_group(tag, kind, x, s):
        """Bolt, head washer, wall nut, washers, part and nyloc on one axle (+ the jack screw for idlers)."""
        g = {}
        if kind == "idler":
            yh, bolt, hw, part_out = y_head_idler, "idler_bolt", "washer_wide", F.Y_T + spm.DISC_HALF
            g[f"washer_wide_nut{tag}"] = ax(x, s * y_nut_washer_idler, s)
            y_nut, y_run = y_nut_idler, y_run_idler
        else:
            yh, bolt, hw, part_out = y_head_road, "road_bolt", "washer", F.Y_T + wheel_h
            y_nut, y_run = y_trap, F.HALF_W_OUT
        g[f"{bolt}{tag}"] = ax(x, s * yh, s, outward=False)
        g[f"{hw}_head{tag}"] = ax(x, s * yh, s)
        g[f"nut{tag}"] = ax(x, s * y_nut, s)
        g[f"washer_in{tag}"] = ax(x, s * y_run, s)
        g[f"{kind}{tag}"] = ax(x, s * F.Y_T, s)
        g[f"washer_out{tag}"] = ax(x, s * part_out, s)
        g[f"nyloc{tag}"] = ax(x, s * (part_out + F.WASHER[1]), s)
        return g

    def jack(x_bolt, s):
        x_tip = x_bolt - F.SCREW_HEAD[0] / 2 - 0.05
        return to_mesh(rod_x(x_tip - JACK_L, x_tip, s * ch.JACK_Y, F.Z_A, JACK_PROXY_D), tol=0.02), x_tip

    jack_meshes = {}
    for side, tag in ((1, "L"), (-1, "R")):
        s = side
        P[f"motor{tag}"] = frame((0, s * F.MOTOR_FACE_Y, F.Z_A), F.motor_x_dir(s), (0, s, 0))   # rolled 45°
        P[f"thrust_washer{tag}"] = ax(0, s * (F.MOTOR_FACE_Y + F.SKIN), s)
        P[f"hub{tag}"] = ax(0, s * F.HUB_Y0, s)
        P[f"sprocket{tag}"] = ax(0, s * F.Y_T, s)
        for k in range(F.HUB.n_holes):
            a = math.radians(spm.SLOT_ANGLE0 + k * 360.0 / F.HUB.n_holes)
            loc = tr(F.HUB.bolt_circle_r * math.cos(a), F.HUB.bolt_circle_r * math.sin(a), spm.DISC_HALF)
            P[f"washer_hs{tag}{k}"] = P[f"sprocket{tag}"] @ loc
            P[f"hub_screw{tag}{k}"] = P[f"sprocket{tag}"] @ loc @ tr(0, 0, F.WASHER[1])
        P.update(axle_group(f"{tag}i", "idler", F.AXLE_DX, s))
        P[f"plate_head{tag}"] = tr(x_head_plate, s * y_head_plate, z_head_plate)
        P[f"plate_nut{tag}"] = tr(x_nut_plate, s * y_nut_plate, z_nut_plate)
        for i, x in enumerate(F.ROAD_X):
            P.update(axle_group(f"{tag}{i}", "wheel", x, s))
        jack_meshes[f"jack{tag}"], _ = jack(F.AXLE_DX, s)
        P[f"jack{tag}"] = np.eye(4)
        pins = track_pins()
        for i, (px, pz) in enumerate(pins):
            nx, nz = pins[(i + 1) % len(pins)]
            xd = np.array([nx - px, 0.0, nz - pz])
            zd = np.cross(xd / np.linalg.norm(xd), [0, 1, 0])
            P[f"link{tag}{i:02d}"] = frame((px, s * F.Y_T, pz), xd, zd)

    def kind(k):
        for p in ("plate_head", "plate_nut", "washer_wide_head", "washer_wide_nut", "washer_head", "washer_in", "washer_out",
                  "washer_hs", "thrust_washer", "hub_screw", "road_bolt", "idler_bolt", "lid_screw", "insert", "nyloc", "nut",
                  "motor", "hub", "sprocket", "idler", "wheel", "link", "jack"):
            if k.startswith(p):
                return {"washer_wide_head": "washer_wide", "washer_wide_nut": "washer_wide", "washer_head": "washer",
                        "washer_in": "washer", "washer_out": "washer", "washer_hs": "washer"}.get(p, p)
        return k
    allm = {**M, **fixed, **jack_meshes}

    def mesh_of(k):
        return allm[k] if k in fixed or k.startswith("jack") else allm[kind(k)]
    placed = {k: mesh_of(k).copy().apply_transform(T) for k, T in P.items()}

    def collide(group, others=None, skip=lambda a, c: False):
        hits = []
        pairs = itertools.combinations(sorted(group), 2) if others is None else itertools.product(sorted(group), sorted(others))
        for a, c in pairs:
            if a == c or skip(a, c):
                continue
            ma, mc = group[a], (group if others is None else others)[c]
            lo = np.maximum(ma.bounds[0], mc.bounds[0]); hi = np.minimum(ma.bounds[1], mc.bounds[1])
            if np.any(hi - lo <= 0):
                continue
            try:
                v = trimesh.boolean.intersection([ma, mc], engine="manifold").volume
            except Exception as exc:   # report, never hide
                hits.append((a, c, f"boolean failed: {exc}"))
                continue
            if v > TOL:
                hits.append((a, c, round(float(v), 2)))
        return hits

    print(f"intersecting {len(placed)} bodies ...", flush=True)
    hits = collide(placed)
    print("collisions:", hits or "none", flush=True)

    # ---- idler (with its bolt, washers, nuts and jack screw) at both slot ends -------------------------
    no_links = {k: v for k, v in placed.items() if not k.startswith("link")}
    slot_hits, jack_rows = [], []
    for dx in (-F.IDLER_SLOT, 0.0, F.IDLER_SLOT):
        for side, tag in ((1, "L"), (-1, "R")):
            jm, x_tip = jack(F.AXLE_DX + dx, side)
            if dx:
                g = axle_group(f"{tag}i", "idler", F.AXLE_DX + dx, side)
                moved = {f"{k}@{dx:+.0f}": mesh_of(k).copy().apply_transform(T) for k, T in g.items()}
                moved[f"jack{tag}@{dx:+.0f}"] = jm
                rest = {k: v for k, v in no_links.items() if not (k.endswith(f"{tag}i") or k == f"jack{tag}")}
                slot_hits += collide(moved, rest)
            x_rear = x_tip - JACK_L
            jack_rows.append({"side": tag, "idler_dx": dx, "jack_rear_x": round(x_rear, 2), "jack_tip_x": round(x_tip, 2),
                              "thread_in_buttress_mm": round(min(x_tip, ch.JACK_X[1]) - max(x_rear, ch.JACK_X[0]), 2),
                              "socket_outside_buttress": bool(x_rear <= ch.JACK_X[0] + 1e-6)})
    print("idler + jack screw at both slot ends:", slot_hits or "clear", flush=True)

    # ---- idler clamp plates (round 5): both plates' slots and Ø9 washers over the bolt's whole travel, with each plate
    # anywhere in its locator's play (head plate: recess x 108-129; nut plate: end stops x 108-129) ----------------------
    w_sl, l_sl = F.PLATE_SLOT
    BOLT_MAJOR = 3.0                                          # M3 thread major diameter (nominal; 2.87-2.98 real)
    wr = F.WASHER_WIDE[0] / 2
    need = [F.AXLE_DX - F.IDLER_SLOT, F.AXLE_DX + F.IDLER_SLOT]

    def plate_report(name, size, loc_x, y_c, z_c, x_c, locator):
        L, H = size
        rear_ends = (loc_x[0], loc_x[1] - L)                 # plate pushed to the rear / front of its locator
        ranges = [[round(p0 + F.PLATE_SLOT_FROM + BOLT_MAJOR / 2, 2), round(p0 + F.PLATE_SLOT_FROM + l_sl - BOLT_MAJOR / 2, 2)]
                  for p0 in rear_ends]
        nominal = (x_c - L / 2, x_c + L / 2)
        margins = []
        for dx in (-F.IDLER_SLOT, 0.0, F.IDLER_SLOT):
            xb = F.AXLE_DX + dx
            worst = min(min(xb - wr - p0, p0 + L - (xb + wr)) for p0 in rear_ends)
            margins.append({"idler_dx": dx, "nominal_mm": round(min(xb - wr - nominal[0], nominal[1] - (xb + wr)), 2),
                            "plate_at_either_end_of_its_play_mm": round(worst, 2)})
        return {"plate": name, "size_mm": [L, H, F.PLATE_T], "slot_mm": [w_sl, l_sl],
                "slot_from_rear_end_mm": [F.PLATE_SLOT_FROM, F.PLATE_SLOT_FROM + l_sl], "locator": locator,
                "locator_x": list(loc_x), "play_x_mm_cad": round(loc_x[1] - loc_x[0] - L, 2),
                "x_nominal": [round(v, 2) for v in nominal], "y": [round(y_c - F.PLATE_T / 2, 2), round(y_c + F.PLATE_T / 2, 2)],
                "z_resting_rel_axle": [round(z_c - H / 2 - F.Z_A, 2), round(z_c + H / 2 - F.Z_A, 2)],
                "bolt_centre_range_in_its_slot_x": {"plate_at_rear": ranges[0], "plate_at_front": ranges[1]},
                "covers_slot_travel": bool(all(r[0] <= need[0] and r[1] >= need[1] for r in ranges)),
                "slot_band_z_rel_axle": [round(z_c - w_sl / 2 - F.Z_A, 2), round(z_c + w_sl / 2 - F.Z_A, 2)],
                "washer_d9_on_plate_margin_x": margins}

    head_rep = plate_report("head plate (inside, in the idler-block recess, under the Ø9 head washer)", F.IDLER_PLATE,
                            ch.PLATE_RECESS_X, y_head_plate, z_head_plate, x_head_plate, "2 mm recess, floor at Z_A - 5.2")
    nut_rep = plate_report("nut plate (outside, flat on the wall's outer face, under the Ø9 washer and the wall nut)",
                           F.NUT_PLATE, ch.NUT_PLATE_X, y_nut_plate, z_nut_plate, x_nut_plate,
                           f"lip (top Z_A - {ch.LIP_DZ}, {ch.LIP_OUT} proud) and end stops, nothing cut into the wall")
    petg_between = (F.HALF_W_OUT - (y_head_plate + F.PLATE_T / 2))
    plates = {
        "round": 5, "plate_t_mm": F.PLATE_T, "plates_identical": F.NUT_PLATE == F.IDLER_PLATE, "head": head_rep,
        "nut": nut_rep, "bolt_travel_x_needed": need, "petg_between_the_plates_mm": round(petg_between, 2),
        "nut_slot_in_wall": False,
        "outside_stack_y": {"nut_plate": [F.HALF_W_OUT, F.HALF_W_OUT + F.PLATE_T],
                            "washer_d9": [y_nut_washer_idler, round(y_nut_washer_idler + F.WASHER_WIDE[1], 2)],
                            "wall_nut": [round(y_nut_idler, 2), round(y_nut_idler + F.NUT[1], 2)],
                            "running_washer": [round(y_run_idler, 2), round(y_run_idler + F.WASHER[1], 2)],
                            "idler_hub_from": round(F.IDLER_HUB_Y0, 2)},
        "nut_plate_and_seat_inboard_of_links_mm": round(F.Y_T - F.TRACK_W / 2 - (F.HALF_W_OUT + F.PLATE_T), 2),
        "head_stack_unchanged": {"head_underside_y": ch.IDLER_HEAD_Y1, "washer_y": [ch.IDLER_HEAD_Y1, y_head_plate - F.PLATE_T / 2],
                                 "jack_axis_y": ch.JACK_Y,
                                 "jack_clears_head_washer_mm": round(ch.IDLER_HEAD_Y1 - (ch.JACK_Y + 1.5), 2),
                                 "jack_bears_on_head_mm": round((ch.JACK_Y + 1.5) - (ch.IDLER_HEAD_Y1 - F.SCREW_HEAD[1]), 2)},
    }
    plates["ok"] = bool(head_rep["covers_slot_travel"] and nut_rep["covers_slot_travel"]
                        and all(m["plate_at_either_end_of_its_play_mm"] >= 0 for r in (head_rep, nut_rep)
                                for m in r["washer_d9_on_plate_margin_x"])
                        and plates["nut_plate_and_seat_inboard_of_links_mm"] > 0
                        and abs(y_run_idler + F.WASHER[1] - F.IDLER_HUB_Y0) < 1e-9)
    print("idler clamp plates:", json.dumps(plates), flush=True)

    # ---- an 11 mm gearbox; the specified 10 mm shaft and the 9.6 mm minimum (sprocket strength round 4: a 9 mm
    # shaft is too short for the sprocket's centre hole, so it is no longer a variant) -------------------------------
    long_gb = to_mesh(gearmotor_dummy(replace(F.MOTOR, gb_len=11.0), detailed=True), tol=0.02)
    var_hits = []
    for side, tag in ((1, "L"), (-1, "R")):
        mm = {f"motor_gb11{tag}": long_gb.copy().apply_transform(P[f"motor{tag}"])}
        var_hits += collide(mm, {k: v for k, v in no_links.items() if k != f"motor{tag}"})
    SHAFT_MIN = 9.6                                       # shortest allowed shaft, from the gearbox face (sprocket H4/H5)
    shaft = {}
    for label, L in (("9.6 mm shaft (minimum)", SHAFT_MIN), (f"{F.MOTOR.shaft_len:g} mm shaft (specified)", F.MOTOR.shaft_len)):
        end = F.MOTOR_FACE_Y + L
        set_y = F.HUB_Y0 + F.HUB.t / 2
        shaft[label] = {"shaft_end_y": round(end, 2), "engaged_in_hub_mm": round(min(end, F.HUB_Y1) - F.HUB_Y0, 2),
                        "set_screw_y": set_y, "shaft_past_set_screw_mm": round(end - (set_y + F.HUB.set_screw / 2), 2),
                        "in_sprocket_centre_hole_mm": round(max(0.0, end - F.HUB_Y1), 2),
                        "ends_inside_the_disc": bool(end < F.Y_T + spm.DISC_HALF)}
    print("11 mm gearbox:", var_hits or "clear", "| shafts:", shaft, flush=True)

    # ---- fastener stacks -----------------------------------------------------------------------------------
    stacks = []
    idler_hub_y0 = round(F.Y_T + float(M["idler"].bounds[0][2]), 2)          # from the idler model itself
    for name, yh, L, part_out, y_nut, y_run, part_in in (
            ("road wheel M3 x %.0f" % F.ROAD_BOLT_L, y_head_road, F.ROAD_BOLT_L, F.Y_T + wheel_h, y_trap, F.HALF_W_OUT,
             round(F.Y_T + float(M["wheel"].bounds[0][2]), 2)),
            ("idler M3 x %.0f" % F.IDLER_BOLT_L, y_head_idler, F.IDLER_BOLT_L, F.Y_T + spm.DISC_HALF, y_nut_idler, y_run_idler,
             idler_hub_y0)):
        tip = yh + L
        ny0 = part_out + F.WASHER[1]
        ny1 = ny0 + F.NYLOC[1]
        stacks.append({"bolt": name, "head_underside_y": round(yh, 2), "wall_nut_y": [round(y_nut, 2), round(y_nut + F.NUT[1], 2)],
                       "running_washer_y": [round(y_run, 2), round(y_run + F.WASHER[1], 2)], "part_inner_face_y": part_in,
                       "part_seats_on_running_washer": bool(abs(part_in - (y_run + F.WASHER[1])) < 0.02),
                       "part_outer_face_y": round(part_out, 2), "nyloc_y": [round(ny0, 2), round(ny1, 2)], "tip_y": round(tip, 2),
                       "thread_past_nyloc_mm": round(tip - ny1, 2), "ok_past_nyloc": bool(tip - ny1 >= F.THREAD_PAST_NYLOC),
                       "fully_threaded_engages_wall_nut": bool(yh + 1.0 <= y_nut),
                       "iso4762_partly_threaded_thread_starts_y": round(tip - ISO4762_B, 2),
                       "iso4762_would_engage_wall_nut": bool(tip - ISO4762_B <= y_nut)})
    stacks[1]["idler_stack_y"] = {"head_washer_d9": [ch.IDLER_HEAD_Y1, round(ch.IDLER_HEAD_Y1 + F.WASHER_WIDE[1], 2)],
                                  "head_plate": [round(y_head_plate - F.PLATE_T / 2, 2), round(y_head_plate + F.PLATE_T / 2, 2)],
                                  "petg": [round(y_head_plate + F.PLATE_T / 2, 2), F.HALF_W_OUT],
                                  **plates["outside_stack_y"], "idler": [idler_hub_y0, round(part_out, 2)],
                                  "idler_bore_length_mm": round(part_out - idler_hub_y0, 2)}
    hs_head = F.Y_T + spm.DISC_HALF + F.WASHER[1]
    hs_tip = hs_head - F.HUB_SCREW_L
    hub_screw = {"screw": f"M3 x {F.HUB_SCREW_L:.0f}", "head_underside_y": hs_head, "tip_y": hs_tip,
                 "engaged_in_hub_mm": round(F.HUB_Y1 - max(hs_tip, F.HUB_Y0), 2),
                 "tip_inside_hub_mm": round(hs_tip - F.HUB_Y0, 2), "tip_to_skin_mm": round(hs_tip - (F.MOTOR_FACE_Y + F.SKIN), 2)}
    print("stacks:", json.dumps(stacks), "\nhub screws:", hub_screw, flush=True)

    # ---- tool paths (lid off; track off for the hub set screw) ------------------------------------------
    lid_off = {k: v for k, v in no_links.items() if k not in ("lid", "esp32", "breadboard", "tb6612", "buck", "toggle")
               and not k.startswith("lid_screw") and not k.startswith("jack") and not k.endswith(("Li", "Ri"))}
    # (the idler hardware sits in front of the jack screw and the key goes backwards: leave it out)
    tool_hits = []
    a = math.radians(KEY_ANGLE)
    for row in jack_rows:
        s = 1 if row["side"] == "L" else -1
        x0 = row["jack_rear_x"] - 0.3
        Lk = 110.0
        d = np.array([-math.cos(a), 0.0, math.sin(a)])
        c = np.array([x0, s * ch.JACK_Y, F.Z_A]) + d * Lk / 2
        key = trimesh.creation.cylinder(radius=1.0, height=Lk, sections=24)
        key.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], d))
        key.apply_translation(c)
        hit = collide({f"jack key {row['side']} idler {row['idler_dx']:+.0f}": key}, lid_off)
        tool_hits += hit
        row["key_path_clear"] = not hit
    for side, tag in ((1, "L"), (-1, "R")):
        r0 = F.HUB.od / 2
        key = trimesh.creation.cylinder(radius=1.0, height=60.0, sections=24)
        key.apply_translation((0, side * (F.HUB_Y0 + F.HUB.t / 2), F.Z_A + r0 + 30.0))
        tool_hits += collide({f"hub set-screw key {tag}": key}, lid_off, skip=lambda a_, c_: c_.startswith("hub"))
    print("tool paths:", tool_hits or "clear", flush=True)

    # ---- tooth engagement: each tooth tip (world) must land inside some link's notch ---------------------
    engaged = {}
    keys = sorted(placed)
    for tag, side in (("L", 1), ("R", -1)):
        for sname, xc in (("sprocket", 0.0), ("idler", F.AXLE_DX)):
            n_in = 0
            for k in range(F.N_TEETH):
                th = math.radians(-side * (spm.PHASE_DEG + k * 360.0 / F.N_TEETH))
                tip = np.array([xc + (spm.TOOTH_TIP_R - 0.3) * math.cos(th), side * F.Y_T,
                                F.Z_A + (spm.TOOTH_TIP_R - 0.3) * math.sin(th), 1.0])
                for key_ in keys:
                    if key_.startswith(f"link{tag}"):
                        q = np.linalg.inv(P[key_]) @ tip
                        if (lm.NOTCH_X0 <= q[0] <= F.P - lm.KN_R and abs(q[1]) <= lm.NOTCH_HALF and abs(q[2]) <= F.LINK_T / 2):
                            n_in += 1
                            break
            engaged[f"{sname}{tag}"] = n_in

    # ---- measured clearance between each track and the chassis (housing face beside the links, nacelle inside the wrap)
    clearance = {}
    chm = placed["chassis"]
    for side, tag in ((1, "L"), (-1, "R")):
        lk = trimesh.util.concatenate([placed[k] for k in keys if k.startswith(f"link{tag}")])
        fmask = np.any(side * chm.triangles[:, :, 1] > F.HALF_W_OUT - 0.1, axis=1)
        sub = chm.submesh([np.where(fmask)[0]], append=True)
        pts, _ = trimesh.sample.sample_surface_even(sub, 6000, seed=1)
        pts = np.vstack([pts, sub.vertices])
        _, dist, _ = trimesh.proximity.closest_point(lk, pts)
        i = int(np.argmin(dist))
        nac = side * pts[:, 1] > F.HALF_W_OUT + F.HOUSING_OUT + 0.05
        j = int(np.argmin(np.where(nac, dist, np.inf)))
        clearance[tag] = {"chassis_to_links_min_mm": round(float(dist[i]), 2), "at": [round(float(v), 1) for v in pts[i]],
                          "nacelle_to_links_min_mm": round(float(dist[j]), 2), "nacelle_at": [round(float(v), 1) for v in pts[j]]}
    print("track clearance:", clearance, flush=True)

    allmesh = trimesh.util.concatenate([placed[k] for k in keys])
    lo, hi = allmesh.bounds
    links = trimesh.util.concatenate([placed[k] for k in keys if k.startswith("link")])
    link_in = F.Y_T - F.TRACK_W / 2
    report = {
        "tol_mm3": TOL, "bodies": len(placed), "collisions": hits, "exempt_pairs": [],
        "idler_and_jack_at_slot_ends": slot_hits or "clear", "jack_screw": jack_rows,
        "motor_with_11mm_gearbox": var_hits or "clear", "shaft_variants": shaft,
        "axle_bolt_stacks": stacks, "hub_screws": hub_screw, "tool_paths": tool_hits or "clear",
        "idler_clamp_plates": plates, "skin_mm": F.SKIN, "gearbox_face_y": F.MOTOR_FACE_Y,
        "shaft_overhang_gearbox_face_to_track_plane_mm": F.SHAFT_ARM,
        "links_inner_edge_y": link_in, "housing_outer_face_y": F.HALF_W_OUT + F.HOUSING_OUT,
        "link_to_housing_gap_mm": round(link_in - (F.HALF_W_OUT + F.HOUSING_OUT), 2),
        "track_to_chassis_clearance_measured": clearance,
        "nacelle_max_radius_mm": round(max(math.hypot(x, z) for x, z in F.motor_diamond(
            ch.POCKET_HX + F.NACELLE_WALL, ch.POCKET_HY + F.NACELLE_WALL)), 2), "links_inner_face_min_radius_mm": round(F.CHORD_IN, 2),
        "links_per_side": F.N_LINKS, "axle_dx_mm": F.AXLE_DX, "teeth_engaged_in_notches": engaged,
        "overall_mm": [round(float(v), 1) for v in hi - lo], "overall_min_max_mm": [[round(float(v), 1) for v in lo],
                                                                                    [round(float(v), 1) for v in hi]],
        "lowest_point_mm": round(float(lo[2]), 2), "track_bottom_mm": round(float(links.bounds[0][2]), 2),
        "ground_clearance_mm": round(F.FLOOR_Z, 2), "battery_holder_mm": [b.length, b.width, b.height],
    }
    (HERE / "assembly_check.json").write_text(json.dumps(report, indent=1))
    print(json.dumps({k: report[k] for k in ("bodies", "collisions", "idler_and_jack_at_slot_ends", "motor_with_11mm_gearbox",
                                             "tool_paths", "teeth_engaged_in_notches", "overall_mm")}))
    _render(placed, HERE / "assembly_rover.png")


def _render(placed, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import render as R
    m = trimesh.util.concatenate(list(placed.values()))
    fig, axes = plt.subplots(1, 2, figsize=(14, 7.4), dpi=100)
    for axx, (vname, (elev, azim)) in zip(axes, (("iso", R.VIEWS["iso"]), ("left side", R.VIEWS["front"]))):
        img, _ = R.render_view(m, elev, azim, with_bed=False)
        axx.imshow(img, interpolation="antialiased"); axx.set_axis_off(); axx.set_title(vname)
    fig.suptitle("tracked rover round 5 · parts, motors on metal hubs, axle hardware and idler plates (nut plates outside), "
                 "battery/ESP32/sensor/switch dummies", fontsize=12)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)


if __name__ == "__main__":
    main()

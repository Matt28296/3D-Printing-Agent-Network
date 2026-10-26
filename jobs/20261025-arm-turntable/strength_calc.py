"""Strength check for jobs/20261025-arm-turntable: Turntable with shoulder upright (round 5, independent re-check, 2026-10-26).

Run from the project root:  python3 jobs/20261025-arm-turntable/strength_calc.py
Plain Python (no build123d). It reads the jobs' model.py, tools/hobby_parts.py, the shared claw_frame.py, each
geometry.json and the assembly's torque_budget.json, sweeps the arm's poses for the yaw-stall, hand-push and weight
cases, prints every check as a markdown table and ends with the verdict. strength.md explains every assumption.
"""
# ===== shared arm model: the same block in the five arm strength_calc.py files (base, turntable, ring, upper link, =====
# ===== forearm). Plain Python, no build123d: parameters from each job's model.py and the shared claw_frame.py     =====
# ===== (top-level constants evaluated with ast), servo and camera data from tools/hobby_parts.py, masses from     =====
# ===== each job's geometry.json volume. Checked against assembly_check.chain() and torque_budget.json (see below). =====
import ast
import json
import math
import os
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
JOBS = os.path.join(ROOT, "jobs")
ASM = os.path.join(JOBS, "20261025-robot-arm-assembly")

# --- allowables: library/materials.csv has no PETG row and no job has a datasheet in inputs/ -> NEEDS_TEST at best ---
ALLOW_XY_MPA = 25.0          # tension / bending along the layers: strength-checks placeholder, PETG
Z_RATIO = 0.5                # across the layers: placeholder (half the in-plane value)
SHEAR_RATIO = 0.5            # shear = 0.5 x the normal allowable (Tresca): my assumption
BEARING_MPA = 25.0           # bearing / compression in any direction (compression does not open the layers)
E_MPA, NU = 1800.0, 0.35     # PETG placeholder modulus (skill table); Poisson's ratio assumed
SF_STATIC, SF_SUSTAINED = 3.0, 4.0
SF_PROOF = SF_STATIC / 1.5   # at a proof load of 1.5 x service the part must still be inside the placeholder allowable
DYN = 2.0                    # dynamic factor on self-weight (the specs' x2; the 250 deg/s^2 ramps need about x1.1)
GN = 9.81e-3                 # N per gram
RHO = 1.27e-3                # g/mm^3: solid PETG, the upper bound ("camera, solid" in torque_budget.json)
STALL_MG996R_NMM = 1079.0    # 11 kgf.cm at 6 V, TowerPro datasheet (deep review 01 N1); hobby_parts and the specs say 1000
STALL_MG90S_NMM = 216.0      # 2.2 kgf.cm at 6 V
CLONE_FACTOR = 15.0 / 11.0   # listings that claim 15 kgf.cm (01 N1): printed as a sensitivity line only
F_HAND_N = 5.0               # spec: sideways hand push
PAYLOAD_G = 50.0             # spec: payload, put at the fingertips (torque_budget puts it 10 mm behind them)
DESK_Z = -40.0
STEP_DEG = 5                 # pose sweep step (assembly_check and torque_budget use 5)
PRELOAD_SNUG_N = 150.0       # assumed tension of a tab self-tapper (M2 or M3) driven "snug" by hand: no torque is
PRELOAD_TIGHT_N = 300.0      # specified; 300 N (over-tightened) is printed as a sensitivity line


def allow(across, shear=False):
    a = ALLOW_XY_MPA * (Z_RATIO if across else 1.0)
    return a * (SHEAR_RATIO if shear else 1.0)


# --- read tools/hobby_parts.py, tools/cadlib.py, model.py and claw_frame.py constants without build123d --------------
_SERVO_FIELDS = ["name", "length", "width", "case_top", "total_h", "tab_height", "tab_t", "tab_span", "hole_dx",
                 "hole_dy", "tab_hole_d", "screw_pilot_d", "shaft_from_end", "horn_kind", "horn_d", "horn_t"]
_SERVO_DEFAULTS = dict(horn_arm_len=0.0, horn_tip_d=0.0, horn_arms=1, horn_screw_clear_d=3.4, stall_torque_nmm=0.0,
                       mass_g=0.0, lead_z=0.0, lead_w=0.0, lead_t=0.0, lead_notch_w=0.0, lead_notch_reach=0.0)
_BOX_FIELDS = ["name", "length", "width", "height", "mass_g", "note"]


def _read_hobby():
    ns = {}
    for node in ast.parse(open(os.path.join(ROOT, "tools", "hobby_parts.py")).read()).body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)):
            continue
        name, v = node.targets[0].id, node.value
        fn = getattr(getattr(v, "func", None), "id", "")
        try:
            if fn == "ServoSpec":
                d = dict(_SERVO_DEFAULTS)
                d.update(zip(_SERVO_FIELDS, [ast.literal_eval(a) for a in v.args]))
                d.update({k.arg: ast.literal_eval(k.value) for k in v.keywords})
                ns[name] = SimpleNamespace(**d)
            elif fn == "BoxSpec":
                d = dict(zip(_BOX_FIELDS, [ast.literal_eval(a) for a in v.args]))
                d.update({k.arg: ast.literal_eval(k.value) for k in v.keywords})
                ns[name] = SimpleNamespace(**d)
            elif fn == "replace" and v.args[0].id in ns:
                d = dict(vars(ns[v.args[0].id]))
                d.update({k.arg: ast.literal_eval(k.value) for k in v.keywords})
                ns[name] = SimpleNamespace(**d)
            elif not fn:
                ns[name] = ast.literal_eval(v)
        except Exception:
            pass
    for node in ast.parse(open(os.path.join(ROOT, "tools", "cadlib.py")).read()).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "HOLE_COMP_DEFAULT":
            ns["HOLE_COMP_DEFAULT"] = ast.literal_eval(node.value)
    return ns


HOBBY = _read_hobby()
MG996R, MG90S, BRIO = HOBBY["MG996R"], HOBBY["MG90S"], HOBBY["BRIO_4K"]
HORN_DEPTH, HOLE_COMP = HOBBY["HORN_DEPTH"], HOBBY["HOLE_COMP_DEFAULT"]


def horn_face_z(s):
    return (s.total_h - s.tab_height) + 0.6          # tools/hobby_parts.py


def link_back_z(s, depth=HORN_DEPTH):
    return horn_face_z(s) - depth


def eval_constants(path):
    """Top-level constants of a model.py / claw_frame.py, evaluated in order; anything else is skipped."""
    ns = dict(HOBBY, math=math, horn_face_z=horn_face_z, link_back_z=link_back_z, max=max, min=min, abs=abs)
    base = set(ns)
    for node in ast.parse(open(path).read()).body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        try:
            val = eval(compile(ast.Expression(node.value), path, "eval"), ns)
        except Exception:
            continue
        t = node.targets[0]
        if isinstance(t, ast.Name):
            ns[t.id] = val
        elif isinstance(t, ast.Tuple) and all(isinstance(e, ast.Name) for e in t.elts):
            for e, x in zip(t.elts, val):
                ns[e.id] = x
    return SimpleNamespace(**{k: v for k, v in ns.items() if k not in base and not k.startswith("__")})


def job_params(job):
    return eval_constants(os.path.join(JOBS, job, "model.py"))


def volume_mm3(job):
    return json.load(open(os.path.join(JOBS, job, "geometry.json")))["volume_mm3"]


TT = job_params("20261025-arm-turntable")
UL = job_params("20261025-arm-upper-link")
FA = job_params("20261025-arm-forearm")
CF = eval_constants(os.path.join(ASM, "claw_frame.py"))
TB = json.load(open(os.path.join(ASM, "torque_budget.json")))
TRAVEL = TB["travel_deg"]                         # shoulder 0..180, elbow -150..30 (SYS-03 fitting), wrist -90..90

# --- masses: geometry.json volume x 1.27 g/cm^3; centres of mass from build123d (design() of each job, measured
# 2026-10-26 by this analyst, in each part's design frame). A volume change over 0.5 % prints a warning.
CAD = {"20261025-arm-turntable": (89196.5, (0.0, -3.799, 33.048)),
       "20261025-arm-upper-link": (39496.5, (39.615, 0.0, 5.064)),
       "20261025-arm-forearm": (29235.2, (35.755, 0.0, 5.087)),
       "20261026-arm-claw-frame": (34760.0, (10.033, 0.453, 13.988)),
       "20261026-arm-claw-cover": (22526.4, (27.291, -2.495, 32.778)),
       "20261026-arm-claw-pinion": (2773.4, (0.0, 0.0, 5.135)),        # pinion frame: its z = claw +x
       "20261026-arm-claw-jaw": (16126.7, (44.114, -2.705, 37.923)),     # jaw A at gap 0; jaw B is it turned
       "20261026-arm-camera-mount": (10479.9, (-8.231, -3.094, 66.085)),
       "20261025-arm-base": (89630.6, (0.534, 0.299, -12.615)),
       "20261025-arm-turntable-ring": (13333.5, (0.0, 0.0, 7.813)),
       "20261025-arm-esp32-cradle": (11498.6, (13.187, 26.581, -15.296))}
STALE = []
for _job, (_v0, _c) in CAD.items():
    _v = volume_mm3(_job)
    if abs(_v - _v0) > 0.005 * _v0:
        STALE.append(f"WARNING: {_job} volume {_v:.0f} mm3 differs from {_v0:.0f} when its CoG was measured")


def mass_g(job):
    return volume_mm3(job) * RHO


def com(job):
    return CAD[job][1]


def servo_com(s):
    """Body-box centre in the servo frame (origin on the shaft at the tab underside, +z = shaft)."""
    return (-(s.length - s.shaft_from_end) + s.length / 2, 0.0, -s.tab_height + s.case_top / 2)


LB_MG, LB_SG = link_back_z(MG996R), link_back_z(MG90S)         # 14.5, 12.6: link back faces above the tabs
XS, ZS, UP_Y = TT.XS, TT.ZS, TT.UP_Y
L1, L2, T1, T2 = UL.L, FA.L, UL.T, FA.T
_ta = math.radians(CF.CAM_TILT)


def cam_to_g(p):
    """Camera frame (origin at the thread, +x lens, +y long axis, +z up) -> claw frame G (assembly_check cam_in_g)."""
    x, y, z = p
    return (CF.CAM_XC + x * math.cos(_ta) + z * math.sin(_ta), y, CF.CAM_ZC - x * math.sin(_ta) + z * math.cos(_ta))


_cx, _cy, _cz = servo_com(MG90S)
_mx, _my, _mz = servo_com(MG996R)
_pin = com("20261026-arm-claw-pinion")
_jaw = com("20261026-arm-claw-jaw")
# (name, mass g, body, point in the body frame). Bodies: "TT" = turntable (world frame at yaw 0), "U" upper link,
# "F" forearm, "G" claw frame. The mass model of torque_budget.py ("camera, solid") plus the shoulder and base horns.
ITEMS = [
    ("turntable", mass_g("20261025-arm-turntable"), "TT", com("20261025-arm-turntable")),
    ("base disc horn + M3x14 clamp", 5.0, "TT", (0.0, 0.0, TT.Z0 - 1.5)),
    ("shoulder MG996R", MG996R.mass_g, "TT", (XS + _mx, UP_Y + _mz, ZS - _my)),
    ("shoulder horn + clamp", 4.2, "U", (0.0, 0.0, 0.6)),
    ("upper link", mass_g("20261025-arm-upper-link"), "U", com("20261025-arm-upper-link")),
    ("cable on the upper link", 9.0, "U", (L1 / 2, 0.0, T1 / 2)),
    ("elbow MG996R", MG996R.mass_g, "U", (L1 + _mx, _my, T1 + _mz)),
    ("elbow horn + clamp", 4.2, "F", (0.0, 0.0, -2.0)),
    ("forearm", mass_g("20261025-arm-forearm"), "F", com("20261025-arm-forearm")),
    ("cable on the forearm", 7.0, "F", (L2 / 2, 0.0, T1 / 2)),
    ("wrist MG90S", MG90S.mass_g, "F", (L2 + _cx, _cy, T2 + _cz)),
    ("wrist horn + clamp", 1.2, "G", (0.0, 0.0, 2.0)),
    ("claw frame", mass_g("20261026-arm-claw-frame"), "G", com("20261026-arm-claw-frame")),
    ("claw cover", mass_g("20261026-arm-claw-cover"), "G", com("20261026-arm-claw-cover")),
    ("claw pinion", mass_g("20261026-arm-claw-pinion"), "G", (CF.X_P0 + _pin[2], 0.0, CF.ZS)),
    ("claw jaw A", mass_g("20261026-arm-claw-jaw"), "G", _jaw),
    ("claw jaw B", mass_g("20261026-arm-claw-jaw"), "G", (_jaw[0], -_jaw[1], 2 * CF.ZS - _jaw[2])),
    ("claw MG90S", MG90S.mass_g, "G", (CF.X_B + _cz, _cx, CF.ZS + _cy)),
    ("pinion horn + screw", 1.0, "G", (CF.X_P0 + 3.0, 0.0, CF.ZS)),
    ("claw and mount screws", 5.0, "G", (8.0, 0.0, 30.0)),
    ("cable on the claw", 5.0, "G", (0.0, 0.0, 30.0)),
    ("camera mount", mass_g("20261026-arm-camera-mount"), "G", com("20261026-arm-camera-mount")),
    ("Brio 4K", BRIO.mass_g, "G", cam_to_g((0.0, 0.0, BRIO.height / 2))),
    ("thumb screw", 5.0, "G", cam_to_g((0.0, 0.0, -CF.SEAT_T - 3.0))),
]
TIP_G = (CF.X_TIP, 0.0, CF.ZS)                         # fingertips (claw closed), on the claw axis
PAYLOAD = ("payload", PAYLOAD_G, "G", TIP_G)
# where an obstacle or a hand can touch the arm: the fingertips and the two ends of the Brio (its long axis lies in the
# arm plane, +-51 mm from the claw axis), which give the largest twisting levers
CONTACTS = {"fingertip": TIP_G, "camera end +y": cam_to_g((0.0, BRIO.length / 2, BRIO.height / 2)),
            "camera end -y": cam_to_g((0.0, -BRIO.length / 2, BRIO.height / 2))}
DOWNSTREAM = {"TT": ("TT", "U", "F", "G"), "U": ("U", "F", "G"), "F": ("F", "G"), "G": ("G",)}
EE_G = sum(i[1] for i in ITEMS if i[2] == "G")          # end effector beyond the wrist horn (solid): 224.1 g


def frames(sh, el, wr):
    """Body frames at yaw 0, as assembly_check.chain(): origin and angle; x = (cos t, 0, sin t), y = (sin t, 0, -cos t),
    z = (0, 1, 0) (outboard). sh 0 = upper link along +X, + up; el / wr 0 = straight, + up."""
    t1 = math.radians(sh)
    t2 = t1 + math.radians(el)
    t3 = t2 + math.radians(wr)
    oU = (XS, UP_Y + LB_MG, ZS)
    oF = (oU[0] + L1 * math.cos(t1), oU[1] + T1 + LB_MG, oU[2] + L1 * math.sin(t1))
    oG = (oF[0] + L2 * math.cos(t2), oF[1] + T2 + LB_SG, oF[2] + L2 * math.sin(t2))
    return {"TT": ((0.0, 0.0, 0.0), None), "U": (oU, t1), "F": (oF, t2), "G": (oG, t3)}


def to_world(fr, p):
    o, t = fr
    if t is None:
        return p
    c, s = math.cos(t), math.sin(t)
    return (o[0] + p[0] * c + p[1] * s, o[1] + p[2], o[2] + p[0] * s - p[1] * c)


def to_local(fr, v):
    """World vector -> components along the body's x, y, z (world X, Y, Z for the turntable)."""
    t = fr[1]
    if t is None:
        return v
    c, s = math.cos(t), math.sin(t)
    return (v[0] * c + v[2] * s, v[0] * s - v[2] * c, v[1])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def lump(items):
    """(mass g, centre) of a list of (name, m, body, p) items on one body."""
    m = sum(i[1] for i in items)
    if m <= 0:
        return 0.0, (0.0, 0.0, 0.0)
    return m, tuple(sum(i[1] * i[3][k] for i in items) / m for k in range(3))


def link_beyond(body, job, x_cut, x0, x1, exclude=()):
    """Items on a link beyond a section at x_cut: the point items with x > x_cut, plus the link's own mass beyond the cut
    taken as uniform along x (it ignores the window, so it overstates the link's own weight beyond the cut)."""
    own = [i for i in ITEMS if i[2] == body and i[3][0] > x_cut and i[0] not in exclude]
    frac = (x1 - max(x_cut, x0)) / (x1 - x0)
    own.append(("link beyond the cut", mass_g(job) * frac, body, ((max(x_cut, x0) + x1) / 2, 0.0, 5.0)))
    return own


def poses():
    sh0, sh1 = TRAVEL["shoulder"]
    el0, el1 = TRAVEL["elbow"]
    wr0, wr1 = TRAVEL["wrist"]
    for sh in range(sh0, sh1 + 1, STEP_DEG):
        for el in range(el0, el1 + 1, STEP_DEG):
            for wr in range(wr0, wr1 + 1, STEP_DEG):
                yield sh, el, wr


def contact_forces(fr):
    """Per contact point: (world point, yaw-stall force, hand-push force (+Y; the -Y push is its mirror)).
    Yaw stall: F = 1079 / R tangential, scaled down where a pitch servo (shoulder / elbow 1079, wrist 216 N.mm)
    would back-drive first. Hand push: 5 N along +Y, capped where the yaw servo would back-drive (1079 / |x|)."""
    joints = ((fr["U"][0], STALL_MG996R_NMM), (fr["F"][0], STALL_MG996R_NMM), (fr["G"][0], STALL_MG90S_NMM))
    out = {}
    for name, pg in CONTACTS.items():
        P = to_world(fr["G"], pg)
        R = math.hypot(P[0], P[1])
        f = STALL_MG996R_NMM / R
        Fy = (-P[1] / R * f, P[0] / R * f, 0.0)
        s = 1.0
        for J, st in joints:
            my = abs((P[2] - J[2]) * Fy[0])          # (r x F)_y with F_z = 0
            if my > st:
                s = min(s, st / my)
        Fy = (Fy[0] * s, Fy[1] * s, 0.0)
        fh = F_HAND_N if abs(P[0]) * F_HAND_N <= STALL_MG996R_NMM else STALL_MG996R_NMM / abs(P[0])
        out[name] = (P, Fy, (0.0, fh, 0.0))
    return out


def above_desk(fr):
    pts = [fr["F"][0], fr["G"][0], to_world(fr["G"], TIP_G)]
    return min(p[2] for p in pts) >= DESK_Z


class Probe:
    """A section: body, centre point and the items beyond it. sweep() keeps, per load mode, the worst value of every
    check (a function of the section force F and moment M, both in the body's axes) and the pose it came from."""

    def __init__(self, name, body, point, own_items=(), checks=None):
        self.name, self.body, self.point = name, body, point
        self.lumps = []                                   # (body, mass g, centre in that body's frame)
        if own_items:
            m, c = lump(list(own_items))
            self.lumps.append((body, m, c))
        for b in DOWNSTREAM[body][1:]:
            m, c = lump([i for i in ITEMS if i[2] == b] + ([PAYLOAD] if b == "G" else []))
            self.lumps.append((b, m, c))
        self.checks = checks or {}
        self.worst = {}

    def loads(self, fr, P, F):
        p = to_world(fr[self.body], self.point)
        return to_local(fr[self.body], F), to_local(fr[self.body], cross(sub(P, p), F))

    def gravity(self, fr, factor):
        p = to_world(fr[self.body], self.point)
        Fw, Mw = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
        for b, m, c in self.lumps:
            W = (0.0, 0.0, -m * GN * factor)
            M = cross(sub(to_world(fr[b], c), p), W)
            Fw[2] += W[2]
            for k in range(3):
                Mw[k] += M[k]
        return to_local(fr[self.body], tuple(Fw)), to_local(fr[self.body], tuple(Mw))

    def record(self, mode, F, M, pose, contact=None):
        for cname, fn in self.checks.items():
            v = fn(F, M)
            key = (mode, cname)
            if v > self.worst.get(key, (-1.0,))[0]:
                self.worst[key] = (v, pose, contact, F, M)

    def get(self, mode, cname):
        """(worst value, pose, contact point, section force, section moment) of a check over the sweep."""
        return self.worst[(mode, cname)]


def sweep(probes):
    """Every pose inside the servo travel with the elbow, wrist and fingertips above the desk:
    - "weight": self-weight + 50 g payload x DYN (sustained);
    - "yaw":  base-yaw stall into a side obstacle at a fingertip or a camera end, plus the static weight (short-term);
    - "hand": 5 N sideways hand push at the same points, either way, plus the static weight (short-term).
    The contact and the weight are added component by component as magnitudes: the worse sign of each."""
    n = 0
    for pose in poses():
        fr = frames(*pose)
        if not above_desk(fr):
            continue
        n += 1
        cf = contact_forces(fr)
        for pr in probes:
            Fg, Mg = pr.gravity(fr, 1.0)
            pr.record("weight", tuple(DYN * c for c in Fg), tuple(DYN * c for c in Mg), pose)
            for cname, (P, Fy, Fh) in cf.items():
                for mode, Fc in (("yaw", Fy), ("hand", Fh)):
                    F, M = pr.loads(fr, P, Fc)
                    pr.record(mode, tuple(abs(a) + abs(b) for a, b in zip(F, Fg)),
                              tuple(abs(a) + abs(b) for a, b in zip(M, Mg)), pose, cname)
    return n


MODES = {"weight": ("weight x2 (sustained)", SF_SUSTAINED), "yaw": ("yaw-stall sweep", SF_STATIC),
         "hand": ("hand push 5 N", SF_STATIC)}


def where(pr, mode, cname):
    v, pose, contact = pr.get(mode, cname)[:3]
    return f"s{pose[0]} e{pose[1]} w{pose[2]}" + (f", {contact}" if contact else "")


# --- proof tests (spec §8 as this review would write them) -----------------------------------------------------------
# The assembled-arm test, shared by the turntable and the base: base screwed down, servos powered, base servo centred
# (yaw 0: the arm's plane is the X-Z plane, the arm reaching over the +X wall), arm straight up (shoulder 90, elbow 0,
# wrist 0), a luggage scale pushing along +-Y (out of the arm's plane) at the fingertips, 1 min each way. Every script
# prints, at its own critical checks, the test value over the yaw-stall service value, so the links can be seen not to
# be overloaded by it. (With the elbow at 90 the fingertips are 184 mm from the yaw axis and the base servo would slip
# at 1079 / 184 = 5.9 N, so that variant cannot reach a proof load.)
ARM_TESTS = {"arm up, +-Y at the fingertips": ((90, 0, 0), 11.5)}
PROOF_RATIO = 1.5                            # proof load = 1.5 x service (strength-checks: 1.5 to 2 x)


def test_loads(pr, pose, F_N, body="G", point=TIP_G, weight=True):
    """Section force and moment for a push of F_N along world +-Y at a point of a body, in pose (shoulder, elbow, wrist),
    plus the static weight (the worse sign of each component, as in the sweep). weight=False for bench tests where the
    part lies so that gravity acts in its own plane."""
    fr = frames(*pose)
    F, M = pr.loads(fr, to_world(fr[body], point), (0.0, F_N, 0.0))
    Fg, Mg = pr.gravity(fr, 1.0) if weight else ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
    return tuple(abs(a) + abs(b) for a, b in zip(F, Fg)), tuple(abs(a) + abs(b) for a, b in zip(M, Mg))


def test_ratio(pr, cname, pose, F_N, mode="yaw", **kw):
    """A check's value under the test over its worst service value in a load mode (yaw stall by default)."""
    return pr.checks[cname](*test_loads(pr, pose, F_N, **kw)) / pr.get(mode, cname)[0]


def force_for(fn, target, hi=500.0):
    """Smallest force F with fn(F) >= target (fn grows with F); bisection."""
    lo = 0.0
    if fn(hi) < target:
        return float("inf")
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if fn(mid) < target else (lo, mid)
    return hi


# --- servo mounts: windows, pilots, lead notches as servo_mount_cutter() cuts them (CAD sizes) -------------------------
def servo_mount(s, clearance, end_clearance=None, lead="notch", pilot_shift=0.0):
    c = clearance + HOLE_COMP
    ce = (clearance if end_clearance is None else end_clearance) + HOLE_COMP
    bx0 = -(s.length - s.shaft_from_end)
    xm = bx0 + s.length / 2
    m = SimpleNamespace(case_x=(bx0, s.shaft_from_end), win_x=(bx0 - ce / 2, s.shaft_from_end + ce / 2),
                        win_hw=(s.width + c) / 2, d_pilot=s.screw_pilot_d + HOLE_COMP, xm=xm)
    ys = [0.0] if s.hole_dy == 0 else [-s.hole_dy / 2, s.hole_dy / 2]
    m.pilots = [(xm + dx + (pilot_shift if dx > 0 else 0.0), y) for dx in (-s.hole_dx / 2, s.hole_dx / 2) for y in ys]
    nw, reach = s.lead_notch_w + HOLE_COMP, s.lead_notch_reach + HOLE_COMP / 2
    ends = (1, -1) if lead == "notch" else ((1,) if lead == "notch_shift_pilot" else ())
    m.notches = [(min(s.shaft_from_end, s.shaft_from_end + reach), s.shaft_from_end + reach, nw / 2) if e > 0 else
                 (bx0 - reach, bx0, nw / 2) for e in ends]
    lig = []
    for (px, py) in m.pilots:
        cand = []
        for (xa, xb, hw) in m.notches:
            gx = max(xa - px, px - xb, 0.0)
            gy = max(abs(py) - hw, 0.0)
            cand.append(math.hypot(gx, gy) - m.d_pilot / 2)
        if abs(py) < m.win_hw:                                  # straight to the window's end wall
            cand.append(min(abs(px - m.win_x[0]), abs(px - m.win_x[1])) - m.d_pilot / 2)
        lig.append(min(cand))
    m.ligaments = lig
    return m


def splitting(S_n, d_thread, d_mean, L, lig):
    """Hoop stress in a thin strip beside a tapped pilot. The thread's radial pressure is p = S tan30 / (pi d_mean L)
    (frictionless 60° thread); the strip is taken as the wall of a thick ring round the thread (Lamé):
    sigma = p (b^2 + a^2) / (b^2 - a^2), a = thread radius, b = a + strip. A ring that thin all round is weaker than a
    hole with only one thin side. The thread-forming interference itself is not modelled: the first-print check covers it."""
    p = S_n * math.tan(math.radians(30)) / (math.pi * d_mean * L)
    a = d_thread / 2
    b = a + lig
    return p * (b * b + a * a) / (b * b - a * a)


ROWS, ADVISORY = [], []


def row(case, section, direction, stress, allow_mpa, sf_req, info=False):
    sf = allow_mpa / stress if stress > 1e-9 else float("inf")
    (ADVISORY if info else ROWS).append((f"{case}: {section}", direction, stress, allow_mpa, sf, sf_req))
    return sf


def report(title):
    print(f"\n== {title} ==")
    print("| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |")
    print("|---|---|---|---|---|---|---|---|")
    for i, (n, d, s, a, sf, req) in enumerate(ROWS, 1):
        print(f"| {i} | {n} | {d} | {s:.2f} | {a:.2f} | {sf:.2f} | {req:g} | {'OK' if sf >= req else '**FAIL**'} |")
    if ADVISORY:
        print("\nAdvisory rows (not in the verdict; strength.md gives the reason for each):")
        print("| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |")
        print("|---|---|---|---|---|---|")
        for n, d, s, a, sf, req in ADVISORY:
            print(f"| {n} | {d} | {s:.2f} | {a:.2f} | {sf:.2f} | {req:g} |")
    worst = min(ROWS, key=lambda r: r[4] / r[5])
    fails = [r for r in ROWS if r[4] < r[5]]
    print(f"\nlowest SF {worst[4]:.2f} (required {worst[5]:g}) at: {worst[0]}")
    if fails:
        print(f"{len(fails)} row(s) under the required SF:")
        for r in sorted(fails, key=lambda r: r[4] / r[5]):
            print(f"  SF {r[4]:.2f} < {r[5]:g}: {r[0]}")
    print("VERDICT:", "FAIL" if fails else "NEEDS_TEST (placeholder allowables: PASS is not possible without measured data)")
    return worst, fails


def model_check():
    """The plain-Python model against torque_budget.json (made from the CAD by torque_budget.py)."""
    tb = TB["configs"]["camera, solid"]
    fr0 = frames(0, 0, 0)
    case_top = {"shoulder": UP_Y + (MG996R.case_top - MG996R.tab_height),
                "elbow": fr0["U"][0][1] + T1 + (MG996R.case_top - MG996R.tab_height),
                "wrist": fr0["F"][0][1] + T2 + (MG90S.case_top - MG90S.tab_height)}
    items = [i for i in ITEMS if i[0] not in ("shoulder horn + clamp", "base disc horn + M3x14 clamp")]
    oh = {j: sum(i[1] * GN * (to_world(fr0[i[2]], i[3])[1] - case_top[j]) for i in items if i[2] in b)
          for j, b in (("shoulder", "UFG"), ("elbow", "FG"), ("wrist", "G"))}
    pts = [(i[1], to_world(fr0[i[2]], i[3])) for i in items]
    my = GN * sum(m * p[0] for m, p in pts)
    mx = GN * sum(m * p[1] for m, p in pts)
    tbo = TB["overhung_moment_nmm"]["camera, payload 0 g"]
    tby = TB["yaw_output_moment_nmm"]["camera, arm straight out, payload 0 g"]
    print(f"model check (payload 0, solid): end effector {EE_G:.1f} g (torque_budget {tb['end_effector_g']}); "
          f"overhung shoulder / elbow / wrist {oh['shoulder']:.0f} / {oh['elbow']:.0f} / {oh['wrist']:.0f} N.mm "
          f"(torque_budget {tbo['shoulder']:.0f} / {tbo['elbow']:.0f} / {tbo['wrist']:.0f}); arm straight out on the base "
          f"horn {math.hypot(mx, my):.0f} N.mm (torque_budget {tby['total_nmm']:.0f})")
    for s in STALE:
        print(s)
# ===================================================== end of the shared block =====================================================

# ============================================= 20261025-arm-turntable (round 5) =============================================
JOB = "20261025-arm-turntable"
P = TT
SS = MG996R                                 # shoulder servo (and the base servo under the disk)
TOP = P.Z0 + P.DISK_T                       # 24.5: disk top
Y_BACK = P.UP_Y - P.UP_T                    # -12: upright back face
SM = servo_mount(SS, P.CLR, lead="notch")   # shoulder servo in the upright: servo x = world X, servo y = world -Z
WIN_HL = (SM.win_x[1] - SM.win_x[0]) / 2    # 20.65: window half-length along X (body centred on X 0)
WIN_Z = (P.ZS - SM.win_hw, P.ZS + SM.win_hw)   # 50.35 .. 70.65 (+ 45° roof above)
NOTCH_X1 = SM.notches[0][1] + XS                                      # 22.45: notch's outer end (|X|)
NOTCH_HZ = SM.notches[0][2]                                           # 2.3: notch half-width (Z)
PIL_X = SM.pilots[2][0] + XS                                          # 24.25
D_PIL_PRINT = SS.screw_pilot_d
D_THREAD = 2.9
D_MEAN = (D_THREAD + D_PIL_PRINT) / 2
L_ENG = min(12.0 - 0.5 - SS.tab_t, P.UP_T)  # M3 x 12 + washer: 9 mm long, but the upright is only 7 thick
L_BEAR = min(2 * D_THREAD, P.UP_T)
LIG_CAD = min(SM.ligaments)                 # notch -> pilot 1.85 CAD; the 45° notch top -> upper pilot ≈1.8 (brief)
LIG = min(LIG_CAD, 1.79) - max(D_THREAD - SM.d_pilot, 0.0) / 2
TAB_EDGE = SS.width / 2
TAB_LEVER_W = SS.hole_dy / 2 + TAB_EDGE     # 14.85
TAB_LEVER_L = SS.hole_dx / 2 + SS.tab_span / 2   # 51.25
TOR_SHARE = 0.6                             # the two tabs sit on similar columns: 60 % on the busier one (assumption)
R_FAR = math.hypot(SS.length - SS.shaft_from_end - SS.length / 2 + SS.hole_dx / 2, SS.hole_dy / 2)   # 34.76
R_NEAR = math.hypot(SS.hole_dx / 2 - (SS.length / 2 - SS.shaft_from_end), SS.hole_dy / 2)          # 14.96
SUM_R2 = 2 * (R_FAR ** 2 + R_NEAR ** 2)
# base disc horn -> disk: the disk's underside is flat on the Ø25 disc; anti-rotation screws through the disc's holes
DISC_R = 25.0 / 2
HORN_T = SS.horn_t                          # 2.8 (hobby_parts; the disc horn is not measured)
R_HOLES = 9.0                               # ASSUMED hole circle of the stock Ø25 disc horn's outer holes: unverified
N_ANTI, L_ANTI = 2, 6.0 - HORN_T            # 2 x M2 x 6 through the 2.8 mm horn: 3.2 mm in the disk
D_ANTI_PILOT = 1.5                          # BUILD_GUIDE §4 step 3: 1.5 mm pilot drilled through the horn into the disk
FLOOR = P.DISK_T                            # the clamp washer bears on the 8 mm disk
D_WASHER = 9.0
KT_WEDGE, KT_CORNER, KT_HOLE = 2.0, 2.5, 2.0
K_ANNULAR = 0.876                           # rigid central boss in a circular plate: sigma = K M / (b t^2) (b 12.5, a 40,
                                            # simply supported edge; derived for this review, clamped edge gives 0.785)


def upright_section(z, up_t=None, g_t=None, g_h=None, g_len=None, g_x=None):
    """Horizontal section of the upright at height z (above the root wedges): rectangles (x0, x1, y0, y1).
    up_t / g_t / g_h / g_len / g_x override UP_T / GUSSET_T / GUSSET_H / GUSSET_LEN / GUSSET_X for the what-if lines."""
    up_t = P.UP_T if up_t is None else up_t
    g_t = P.GUSSET_T if g_t is None else g_t
    g_h = P.GUSSET_H if g_h is None else g_h
    g_len = P.GUSSET_LEN if g_len is None else g_len
    g_x = P.GUSSET_X if g_x is None else g_x
    y_back = P.UP_Y - up_t
    xs = [(-P.UP_W / 2, P.UP_W / 2)]
    cuts = []
    if WIN_Z[0] <= z <= WIN_Z[1]:
        cuts.append((-WIN_HL, WIN_HL))
    if abs(z - P.ZS) <= NOTCH_HZ:
        cuts += [(-NOTCH_X1, -WIN_HL), (WIN_HL, NOTCH_X1)]
    for zp in (P.ZS - SS.hole_dy / 2, P.ZS + SS.hole_dy / 2):
        if abs(z - zp) < SM.d_pilot / 2:
            hw = math.sqrt((SM.d_pilot / 2) ** 2 - (z - zp) ** 2)
            cuts += [(-PIL_X - hw, -PIL_X + hw), (PIL_X - hw, PIL_X + hw)]
    for a, b in sorted(cuts):
        new = []
        for (x0, x1) in xs:
            if b <= x0 or a >= x1:
                new.append((x0, x1))
                continue
            if a > x0:
                new.append((x0, a))
            if b < x1:
                new.append((b, x1))
        xs = new
    rects = [(x0, x1, y_back, P.UP_Y) for x0, x1 in xs]
    gl = g_len * max(0.0, 1 - (z - TOP) / g_h)
    for sx in (-1, 1):
        rects.append((sx * g_x - g_t / 2, sx * g_x + g_t / 2, y_back - gl, y_back))
    A = sum((x1 - x0) * (y1 - y0) for x0, x1, y0, y1 in rects)
    yc = sum((x1 - x0) * (y1 - y0) * (y0 + y1) / 2 for x0, x1, y0, y1 in rects) / A
    Ixx = sum((x1 - x0) * (y1 - y0) ** 3 / 12 + (x1 - x0) * (y1 - y0) * ((y0 + y1) / 2 - yc) ** 2 for x0, x1, y0, y1 in rects)
    Iyy = sum((y1 - y0) * (x1 - x0) ** 3 / 12 + (x1 - x0) * (y1 - y0) * ((x0 + x1) / 2) ** 2 for x0, x1, y0, y1 in rects)
    J = sum(max(x1 - x0, y1 - y0) * min(x1 - x0, y1 - y0) ** 3 / 3 for x0, x1, y0, y1 in rects)
    return SimpleNamespace(A=A, yc=yc, Ixx=Ixx, Iyy=Iyy, J=J, c_front=P.UP_Y - yc, c_toe=yc - (y_back - gl), x_max=P.UP_W / 2)


# share of the shoulder servo's moment about X carried by a section between its tab edges (Z 50.65 .. 70.35). Each tab
# pries about one long edge with its two screws (levers 14.85 and 4.85) in tension: pivot on the upper edge is worse.
Z_EDGE_LO, Z_EDGE_HI = P.ZS - SS.width / 2, P.ZS + SS.width / 2
Z_S_LO, Z_S_HI = P.ZS - SS.hole_dy / 2, P.ZS + SS.hole_dy / 2
_l1, _l2 = TAB_LEVER_W, TAB_LEVER_W - SS.hole_dy           # 14.85, 4.85
_den = _l1 ** 2 + _l2 ** 2


def tab_share(z):
    if z <= Z_EDGE_LO:
        return 1.0
    a = _l1 / _den * max(Z_S_HI - z, 0.0) + _l2 / _den * max(Z_S_LO - z, 0.0)       # pivot on the lower edge
    b = (_l1 + _l2) / _den * max(Z_EDGE_HI - z, 0.0) - _l2 / _den * max(Z_S_HI - z, 0.0) - _l1 / _den * max(Z_S_LO - z, 0.0)
    return min(1.0, max(a, b))


def upright_stress(s, z, kt_f, kt_t, Mx, My, Mz):
    """Front-face and gusset-toe stress at the section s at height z. Between the tab edges only tab_share(z) of M_x
    passes; through the window the servo's twist (M_z) reaches the two columns as a couple of +-M_z / (2 x 24.25)."""
    f = tab_share(z)
    col = Mz / (2 * PIL_X) * max(P.ZS - z, 0.0) * s.c_front / (s.Ixx / 2) if z >= WIN_Z[0] else 0.0
    x_c = WIN_HL if z >= WIN_Z[0] else s.x_max          # in-plane bending, taken at the window corner
    front = kt_f * (f * Mx * s.c_front / s.Ixx + col + f * My * x_c / s.Iyy)
    toe = kt_t * f * Mx * s.c_toe / s.Ixx
    return front, toe, f


# (Z, Kt front, Kt toe). Root: the front wedge stops at |X| < 6 round the clamp washer, so the front face has a sharp
# corner there (Kt 2.5, governs; Kt 2.0 under the wedge); the gusset toe meets the disk in a sharp corner.
SECTIONS = {"root": (TOP + P.ROOT_FILLET + 0.5, KT_CORNER, KT_CORNER), "wb": (WIN_Z[0] + 0.25, KT_CORNER, 1.0),
            "pr": (P.ZS - SS.hole_dy / 2, KT_HOLE, 1.0), "notch": (P.ZS, KT_CORNER, 1.0)}
CAD_SEC = {"root": (35227.5, 7.46, 21.39), "wb": (10642.6, 7.79, 13.63), "pr": (7638.8, 7.80, 12.01),
           "notch": (6121.6, 6.93, 11.24)}                      # build123d sections at Z 28, 50.6, 55.5, 60.5
SEC = {k: upright_section(z) for k, (z, _, _) in SECTIONS.items()}
# what-if geometries for the window region (evaluated pose by pose like the drawn one). The gusset toe must stay on the
# disk (r <= 48, DFM round 1), so a thicker upright or gusset comes with a shorter or inboard gusset.
WHATIF = (("as drawn", {}),
          ("UP_T 7 -> 8, GUSSET_LEN 23 -> 22", {"up_t": 8.0, "g_len": 22.0}),
          ("GUSSET_T 4 -> 6, GUSSET_X 30.5 -> 29.5", {"g_t": 6.0, "g_x": 29.5}),
          ("GUSSET_H 70 -> 90", {"g_h": 90.0}),
          ("GUSSET_H 70 -> 100", {"g_h": 100.0}),
          ("GUSSET_H 90, UP_T 8, GUSSET_LEN 22", {"g_h": 90.0, "up_t": 8.0, "g_len": 22.0}))


def toe_r(kw):
    """Radius of the gusset toe's outer corner (it must stay inside the disk, r 48)."""
    return math.hypot(kw.get("g_x", P.GUSSET_X) + kw.get("g_t", P.GUSSET_T) / 2,
                      P.UP_Y - kw.get("up_t", P.UP_T) - kw.get("g_len", P.GUSSET_LEN))
TT_items = [i for i in ITEMS if i[2] == "TT"]
sh_servo = [i for i in TT_items if i[0] == "shoulder MG996R"]
UP_ABOVE_ROOT = ("upright above the root", 36.8, "TT", (0.0, -9.5, 62.0))   # ≈28 980 mm3 of the upright and gussets
UP_ABOVE_WIN = ("upright above the window bottom", 19.4, "TT", (0.0, -9.0, 75.0))
absM = lambda k: (lambda F, M: abs(M[k]))


def front_check(s, z, kt_f, kt_t, which=0):
    """Per-pose check: the section's front-face (which 0) or gusset-toe (which 1) stress from that pose's moments."""
    return lambda F, M: upright_stress(s, z, kt_f, kt_t, abs(M[0]), abs(M[1]), abs(M[2]))[which]


probes = {
    "horn": Probe("base-horn joint (disk underside)", "TT", (0.0, 0.0, P.Z0),
                  own_items=[i for i in TT_items if not i[0].startswith("base disc horn")],
                  checks={"Mh": lambda F, M: math.hypot(M[0], M[1]), "Mx": absM(0), "Mz": absM(2)}),
}
for k, (z, kt_f, kt_t) in SECTIONS.items():
    checks = {"Mx": absM(0), "My": absM(1), "Mz": absM(2), "front": front_check(SEC[k], z, kt_f, kt_t),
              "toe": front_check(SEC[k], z, kt_f, kt_t, 1)}
    if k != "root":
        for i, (_, kw) in enumerate(WHATIF):
            checks[f"wi{i}"] = front_check(upright_section(z, **kw), z, kt_f, kt_t)
    probes[k] = Probe(f"upright Z {z:.1f}", "TT", (0.0, SEC[k].yc, z),
                      own_items=sh_servo + [UP_ABOVE_ROOT if k == "root" else UP_ABOVE_WIN], checks=checks)
probes["tabs"] = Probe("shoulder tab plane", "TT", (0.0, P.UP_Y, P.ZS), own_items=sh_servo,
                       checks={"S": lambda F, M: TOR_SHARE * abs(M[0]) / TAB_LEVER_W + abs(M[2]) / (2 * TAB_LEVER_L)
                               + abs(F[1]) / 4})
model_check()
print(f"turntable: shoulder window X +-{WIN_HL:.2f}, Z {WIN_Z[0]:.2f}-{WIN_Z[1]:.2f}; notches to |X| {NOTCH_X1:.2f}; pilots "
      f"X +-{PIL_X:.2f}, Z {P.ZS - 5:.1f} / {P.ZS + 5:.1f}; notch -> pilot strip {LIG_CAD:.2f} CAD ({LIG:.2f} behind the thread)")
for k, (z, _, _) in SECTIONS.items():
    s, c = SEC[k], CAD_SEC[k]
    print(f"  section Z {z:5.2f}: A {s.A:6.1f}, Ixx {s.Ixx:8.0f} (CAD {c[0]:.0f}), c_front {s.c_front:.2f} (CAD {c[1]}), "
          f"c_toe {s.c_toe:.2f} (CAD {c[2]})")
n = sweep(list(probes.values()))
print(f"{n} poses swept (shoulder {TRAVEL['shoulder']}, elbow {TRAVEL['elbow']}, wrist {TRAVEL['wrist']}, {STEP_DEG} deg)")
for k, pr in probes.items():
    shown = [c for c in pr.checks if c in ("Mh", "Mx", "My", "Mz", "S")]
    print(f"  {pr.name}: " + "; ".join(f"{m} " + ", ".join(f"{c} {pr.get(m, c)[0]:.0f}" for c in shown)
                                     for m in ("weight", "yaw", "hand")))

# --- base-horn joint: torque and overturning ------------------------------------------------------------------------------
F_anti = STALL_MG996R_NMM / (N_ANTI * R_HOLES)
row("base stall 1079 N.mm (yaw stall)", f"disc-horn anti-rotation screws {N_ANTI} x M2 x 6 at r {R_HOLES:g} (assumed), "
    f"bearing in the disk, L {L_ANTI:.1f}, friction ignored", "bearing", F_anti / (D_ANTI_PILOT * L_ANTI), BEARING_MPA, SF_STATIC)
for mode, (lbl, req) in MODES.items():
    pr = probes["horn"]
    S = pr.get(mode, "Mh")[0] / DISC_R
    row(lbl, f"clamped base-horn joint: disk tips on the Ø25 disc's edge, clamp S {S:.0f} N, Ø{D_WASHER:g} washer pull-through, "
        f"floor {FLOOR:g} ({where(pr, mode, 'Mh')})", "Z shear", S / (math.pi * D_WASHER * FLOOR), allow(True, True), req)
for mode, (lbl, req) in MODES.items():
    pr = probes["horn"]
    Mh = pr.get(mode, "Mh")[0]
    row(lbl, f"disk at the disc horn's edge (rigid boss r {DISC_R:g}, t {P.DISK_T:g}; M {Mh:.0f})", "XY",
        K_ANNULAR * Mh / (DISC_R * P.DISK_T ** 2), ALLOW_XY_MPA, req)
    row(lbl, f"disk strip under the upright, b {P.UP_W:g} t {P.DISK_T:g} (Kt {KT_WEDGE}; M_x {pr.get(mode, 'Mx')[0]:.0f})", "XY",
        KT_WEDGE * 6 * pr.get(mode, "Mx")[0] / (P.UP_W * P.DISK_T ** 2), ALLOW_XY_MPA, req)

# --- upright sections (stress across the layers): M_x, M_y and M_z of the same pose, combined pose by pose -----------------
for k, (z, kt_f, kt_t) in SECTIONS.items():
    for mode, (lbl, req) in MODES.items():
        pr = probes[k]
        front, pose_txt = pr.get(mode, "front")[0], where(pr, mode, "front")
        Mx, My, Mz = (abs(c) for c in pr.get(mode, "front")[4])
        f = tab_share(z)
        where_txt = "front face at the washer gap |X| < 6, no wedge" if k == "root" else "front face"
        share = f", {f:.2f} of it between the tab screws" if f < 1 else ""
        row(lbl, f"upright Z {z:.1f}, {where_txt} (Kt {kt_f}; M_x {Mx:.0f}{share}, M_y {My:.0f}, M_z {Mz:.0f}; {pose_txt})",
            "Z", front, allow(True), req)
        if k == "wb" and mode == "yaw":
            WB_YAW = front
        if k == "root":
            row(lbl, f"upright Z {z:.1f}, gusset toe (Kt {kt_t}; {where(pr, mode, 'toe')})", "Z", pr.get(mode, "toe")[0],
                allow(True), req)
pr = probes["root"]
for mode, (lbl, req) in MODES.items():
    Mz = pr.get(mode, "Mz")[0]
    row(lbl, f"upright torsion at the root, open section (T {Mz:.0f})", "Z shear", Mz * P.UP_T / SEC["root"].J,
        allow(True, True), req)

# --- shoulder servo tabs, pilots and notch strips ---------------------------------------------------------------------------
F_stall = STALL_MG996R_NMM * R_FAR / SUM_R2
row("shoulder stall 1079 N.mm", f"far tab pilot bearing, F {F_stall:.1f} N", "bearing", F_stall / (D_PIL_PRINT * L_BEAR),
    BEARING_MPA, SF_STATIC)
row("shoulder stall 1079 N.mm", f"notch -> pilot strip {LIG:.2f}: tear-out (planes across the layers), F {F_stall:.1f} N",
    "Z shear", F_stall / (2 * LIG * L_BEAR), allow(True, True), SF_STATIC)
for mode, (lbl, req) in MODES.items():
    pr = probes["tabs"]
    S = pr.get(mode, "S")[0]
    row(lbl, f"shoulder MG996R tab screw pull-out, S {S:.0f} N (L {L_ENG:g}, Ø{D_PIL_PRINT:g}; {where(pr, mode, 'S')})",
        "Z shear", S / (math.pi * D_PIL_PRINT * L_ENG), allow(True, True), req)
    row(lbl, f"notch strip {LIG:.2f}: splitting, snug preload {PRELOAD_SNUG_N:.0f} N + {S:.0f} N (horizontal pilot in a "
        f"standing wall: taken across the layers)", "Z", splitting(PRELOAD_SNUG_N + S, D_THREAD, D_MEAN, L_ENG, LIG),
        allow(True), req)
row("spec §8: tab screws driven snug", f"notch strip {LIG:.2f}: splitting at {PRELOAD_SNUG_N:.0f} N (across the layers)", "Z",
    splitting(PRELOAD_SNUG_N, D_THREAD, D_MEAN, L_ENG, LIG), allow(True), SF_SUSTAINED)

# --- advisory ------------------------------------------------------------------------------------------------------------------
for r in (7.0, 10.5):
    row("base stall 1079 N.mm", f"anti-rotation screws {N_ANTI} x M2 x 6 at r {r:g} (hole-circle sensitivity)", "bearing",
        STALL_MG996R_NMM / (N_ANTI * r) / (D_ANTI_PILOT * L_ANTI), BEARING_MPA, SF_STATIC, info=True)
for n_, L_ in ((2, 8.0 - HORN_T), (4, 8.0 - HORN_T)):
    for r in (7.0, R_HOLES):
        row("base stall 1079 N.mm", f"FIX: {n_} x M2 x 8 at r {r:g}, L {L_:.1f}", "bearing",
            STALL_MG996R_NMM / (n_ * r) / (D_ANTI_PILOT * L_), BEARING_MPA, SF_STATIC, info=True)
mu, P_res = 0.2, 150.0
T_fric = mu * P_res * (2 / 3 * DISC_R + D_WASHER / 3)
row("base stall 1079 N.mm", f"2 x M2 x 6 at r 9 with clamp friction credited (μ {mu}, {P_res:.0f} N left of the preload: "
    f"{T_fric:.0f} N.mm)", "bearing", (STALL_MG996R_NMM - T_fric) / (N_ANTI * R_HOLES) / (D_ANTI_PILOT * L_ANTI), BEARING_MPA,
    SF_STATIC, info=True)
row(f"yaw-stall sweep with a {CLONE_FACTOR * 11:.0f} kgf.cm clone MG996R", "upright window bottom, front", "Z",
    WB_YAW * CLONE_FACTOR, allow(True), SF_STATIC, info=True)
row(f"yaw-stall sweep, tab screws over-tightened to {PRELOAD_TIGHT_N:.0f} N", f"notch strip {LIG:.2f}: splitting", "Z",
    splitting(PRELOAD_TIGHT_N + probes["tabs"].get("yaw", "S")[0], D_THREAD, D_MEAN, L_ENG, LIG), allow(True), SF_STATIC,
    info=True)

worst, fails = report(JOB)
print("\nWHAT-IF: upright window region, front face, pose by pose (yaw-stall sweep / hand push; SF 3 required):")
for i, (lbl_, kw) in enumerate(WHATIF):
    sfs = [f"{allow(True) / probes[k].get('yaw', f'wi{i}')[0]:.2f} / {allow(True) / probes[k].get('hand', f'wi{i}')[0]:.2f}"
           for k in ("wb", "pr", "notch")]
    print(f"  {lbl_:36s}: window bottom {sfs[0]}, pilot row {sfs[1]}, notch level {sfs[2]}; gusset toe at r "
          f"{toe_r(kw):.1f}" + (f", gussets cut off at the upright's top (Z {P.UP_TOP:.1f}), "
                                f"{kw.get('g_len', P.GUSSET_LEN) * (1 - (P.UP_TOP - TOP) / kw['g_h']):.1f} deep there"
                                if "g_h" in kw else ""))
print("\nWHAT-IF: anti-rotation screws (base stall, friction ignored):")
for n_ in (2, 4):
    for L_name, L_ in (("M2 x 6", 6.0 - HORN_T), ("M2 x 8", 8.0 - HORN_T)):
        print(f"  {n_} x {L_name} at r {R_HOLES:g}: SF {BEARING_MPA / (STALL_MG996R_NMM / (n_ * R_HOLES) / (D_ANTI_PILOT * L_)):.2f}"
              f"; at r 7: SF {BEARING_MPA / (STALL_MG996R_NMM / (n_ * 7.0) / (D_ANTI_PILOT * L_)):.2f}")

# --- proof tests (spec §8 as this review would write it) --------------------------------------------------------------------
print("\nPROOF TEST (spec §8 as this review would write it). Ratio = test value / yaw-stall service value at the same check;")
print("the test should reach 1.5 at the critical checks and stay under 2 elsewhere.")
PT = [("wb", "front", "window bottom, front"), ("pr", "front", "lower pilot row, front"), ("notch", "front", "notch level"),
      ("root", "front", "root front"), ("root", "toe", "gusset toe"), ("root", "Mz", "upright torsion"),
      ("horn", "Mh", "base-horn joint and disk"), ("horn", "Mx", "disk strip"), ("tabs", "S", "shoulder tab screw")]
for name, (pose, F_N) in ARM_TESTS.items():
    print(f"  {name}, {F_N:g} N (s{pose[0]} e{pose[1]} w{pose[2]}): "
          + ", ".join(f"{lbl} {test_ratio(probes[k], c, pose, F_N):.2f}" for k, c, lbl in PT))
    for k, c, lbl in PT[:2]:
        F15 = force_for(lambda F: test_ratio(probes[k], c, pose, F), PROOF_RATIO)
        print(f"    target {lbl}: {PROOF_RATIO:g} x the yaw-stall service value at {F15:.1f} N")
fr90 = frames(90, -90, 0)
P90 = to_world(fr90["G"], TIP_G)
print(f"  spec §8 (2), elbow at 90: the fingertips are {math.hypot(P90[0], P90[1]):.0f} mm from the yaw axis, so the base servo "
      f"slips at {STALL_MG996R_NMM / abs(P90[0]):.1f} N of +-Y push; the upright torsion it was meant to test has SF "
      f"{allow(True, True) * SEC['root'].J / (probes['root'].get('yaw', 'Mz')[0] * P.UP_T):.1f} under the yaw stall")
fr0 = frames(0, 0, 0)
arm = [i for i in ITEMS if i[2] in ("U", "F", "G")]
for lbl_, pose in (("forearm straight out", (0, 0, 0)), ("forearm and claw hanging down", (0, -90, 0))):
    fr = frames(*pose)
    m_sh = sum(i[1] * GN * (to_world(fr[i[2]], i[3])[0] - fr["U"][0][0]) for i in arm) + 9.81 * L1
    print(f"  spec §8 (1) as written ({lbl_}): 1 kg at the elbow axis + the arm's own weight = {m_sh:.0f} N.mm about the "
          f"shoulder, against the shoulder servo's {STALL_MG996R_NMM:.0f} N.mm stall")
F_slip = PROOF_RATIO * STALL_MG996R_NMM / P.DISK_R
print(f"  disc-horn test: {PROOF_RATIO:g} x the base stall = {F_slip:.0f} N tangential at the disk rim (r {P.DISK_R:g}); the "
      f"anti-rotation screws then carry {PROOF_RATIO:g} x their service load (friction ignored)")

"""Strength check for jobs/20261025-arm-base: Robot arm base (round 5, independent re-check, 2026-10-26).

Run from the project root:  python3 jobs/20261025-arm-base/strength_calc.py
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

# ================================================ 20261025-arm-base (round 5) ================================================
JOB = "20261025-arm-base"
P = job_params(JOB)
CR = job_params("20261025-arm-esp32-cradle")
RG = job_params("20261025-arm-turntable-ring")
BS = MG996R                                 # base-yaw servo, hanging through the 4 mm top plate
BM = servo_mount(BS, P.SERVO_CLR, lead="notch")
D_PIL_PRINT = BS.screw_pilot_d
D_THREAD = 2.9
D_MEAN = (D_THREAD + D_PIL_PRINT) / 2
L_ENG = 12.0 - 0.5 - BS.tab_t               # M3 x 12 + Ø7 washer through the 2.5 mm tab: 9 mm in plate + boss
L_BEAR = 2 * D_THREAD
LIG_CAD = min(BM.ligaments)                 # notch -> nearest pilot through the 4 mm plate: 1.84 CAD (2.05 printed)
LIG = LIG_CAD - max(D_THREAD - BM.d_pilot, 0.0) / 2
TAB_EDGE = BS.width / 2
TAB_LEVER_W = BS.hole_dy / 2 + TAB_EDGE     # 14.85
TOR_SHARE = 0.65                            # the far tab sits 15 mm from the -X wall and takes more (assumption)
R_FAR = math.hypot(BS.hole_dx / 2 + (BS.length / 2 - BS.shaft_from_end), BS.hole_dy / 2)     # 34.76
R_NEAR = math.hypot(BS.hole_dx / 2 - (BS.length / 2 - BS.shaft_from_end), BS.hole_dy / 2)    # 14.96
SUM_R2 = 2 * (R_FAR ** 2 + R_NEAR ** 2)
R_BOSS = P.SERVO_BOSS_D / 2                 # 3.25: the screw's pull enters the plate round its Ø6.5 boss
KT_PLATE = 2.0                              # the notch and the window corner sit right at the tab (sharp corners)
# ring path: the ring takes the whole overturning moment at its mid radius; the top plate under it is a strip from the
# nearest wall, widened by the ring (the ring spreads its load: b = 2a + 2 x ring height), minus the cable slot
R_RING = (RG.R_IN + RG.R_OUT) / 2
A_STRIP = 20.6                              # ring at 222° (beside the cable slot) to the -Y wall; 19.0 at 45°
B_STRIP = 2 * A_STRIP + 2 * RG.H - P.CABLE_SLOT[1]
MU_WORN = 0.3                               # PETG on PETG once the PTFE tape has worn through
RING_SCREW_L = 6.0 - RG.TAB_T               # M3 x 6 through the 3 mm ring tab: 3 mm in the 4 mm plate


def plate_at_tab(S, t=None):
    """Bending stress in the top plate round the tension screw's boss: Roark, load S over r0 = boss radius on a plate
    supported at the opposite tab edge (14.85 away, simply supported form, which is the higher of the two)."""
    t = P.PLATE_T if t is None else t
    return KT_PLATE * 3 * S / (2 * math.pi * t ** 2) * ((1 + NU) * math.log(TAB_LEVER_W / R_BOSS) + 1)


TT_items = [i for i in ITEMS if i[2] == "TT"]
probes = {
    "tabs": Probe("base-servo tab plane (Z 0)", "TT", (0.0, 0.0, 0.0), own_items=TT_items,
                  checks={"Mh": lambda F, M: math.hypot(M[0], M[1]), "Mz": lambda F, M: abs(M[2])}),
    "ring": Probe("disk underside (Z 16.5)", "TT", (0.0, 0.0, TT.Z0),
                  own_items=[i for i in TT_items if not i[0].startswith("base disc horn")],
                  checks={"Mh": lambda F, M: math.hypot(M[0], M[1])}),
    "desk": Probe("desk (Z -40)", "TT", (0.0, 0.0, -P.H), own_items=TT_items,
                  checks={"Mh": lambda F, M: math.hypot(M[0], M[1])}),
}
model_check()
print(f"base: MG996R window x {BM.win_x[0]:.2f}..{BM.win_x[1]:.2f}, y +-{BM.win_hw:.2f}; pilots "
      f"{[(round(x, 2), y) for x, y in BM.pilots]}; notch -> pilot strip {LIG_CAD:.2f} CAD ({LIG:.2f} behind the thread)")
n = sweep(list(probes.values()))
print(f"{n} poses swept (shoulder {TRAVEL['shoulder']}, elbow {TRAVEL['elbow']}, wrist {TRAVEL['wrist']}, {STEP_DEG} deg)")
for k, pr in probes.items():
    print(f"  {pr.name}: " + "; ".join(f"{m} " + ", ".join(f"{c} {pr.get(m, c)[0]:.0f}" for c in pr.checks)
                                     for m in ("weight", "yaw", "hand")))

# other moments on the base servo (spec §4): the shoulder pushing the fingertips into the desk, the 20 N rim knock
W_TT_N = sum(i[1] for i in ITEMS) * GN + PAYLOAD_G * GN
D_DESK = 60.0                                # nearest fingertip-on-desk reach from the shoulder axis (conservative)
M_SH_DESK = STALL_MG996R_NMM * (D_DESK + XS) / D_DESK + probes["tabs"].get("weight", "Mh")[0] / DYN
M_RIM = 20.0 * TT.DISK_R + probes["tabs"].get("weight", "Mh")[0] / DYN
EXTRA = {"shoulder stall on the desk": M_SH_DESK, "20 N on the turntable rim (spec)": M_RIM}

# --- base servo: stall, tab pilots and notch strips ------------------------------------------------------------------------
F_stall = STALL_MG996R_NMM * R_FAR / SUM_R2
row("base stall 1079 N.mm", f"far tab pilot bearing, F {F_stall:.1f} N", "bearing", F_stall / (D_PIL_PRINT * L_BEAR),
    BEARING_MPA, SF_STATIC)
row("base stall 1079 N.mm", f"notch -> pilot strip {LIG:.2f} in the 4 mm plate: tear-out, F {F_stall:.1f} N", "XY shear",
    F_stall / (2 * LIG * P.PLATE_T), allow(False, True), SF_STATIC)

# --- servo path: the whole overturning moment through the base servo's tabs (ring ignored) -----------------------------------
cases = [(lbl, req, probes["tabs"].get(mode, "Mh")[0], where(probes["tabs"], mode, "Mh")) for mode, (lbl, req) in MODES.items()]
cases += [(k, SF_STATIC, v, "") for k, v in EXTRA.items()]
for lbl, req, Mh, w in cases:
    S = TOR_SHARE * Mh / TAB_LEVER_W
    row(lbl, f"servo path: tab screw pull-out, M {Mh:.0f} N.mm on the weak axis, S {S:.0f} N (L {L_ENG:g}){'; ' + w if w else ''}",
        "Z shear", S / (math.pi * D_PIL_PRINT * L_ENG), allow(True, True), req)
    row(lbl, f"servo path: top plate {P.PLATE_T:g} mm round the tension screw's boss (Kt {KT_PLATE}: notch and window corner)",
        "XY", plate_at_tab(S), ALLOW_XY_MPA, req)
    row(lbl, f"notch strip {LIG:.2f}: splitting, snug preload {PRELOAD_SNUG_N:.0f} N + {S:.0f} N", "XY",
        splitting(PRELOAD_SNUG_N + S, D_THREAD, D_MEAN, L_ENG, LIG), ALLOW_XY_MPA, req)
row("spec §8: tab screws driven snug", f"notch strip {LIG:.2f}: splitting at {PRELOAD_SNUG_N:.0f} N", "XY",
    splitting(PRELOAD_SNUG_N, D_THREAD, D_MEAN, L_ENG, LIG), ALLOW_XY_MPA, SF_SUSTAINED)

# --- ring path: the support ring takes the whole overturning moment (servo ignored) ------------------------------------------
cases = [(lbl, req, probes["ring"].get(mode, "Mh")[0]) for mode, (lbl, req) in MODES.items()]
cases += [("20 N on the turntable rim (spec)", SF_STATIC, None)]
for lbl, req, Mh in cases:
    R = Mh / R_RING if Mh is not None else 20.0 * TT.DISK_R / R_RING
    row(lbl, f"ring path, R {R:.1f} N: top plate strip a {A_STRIP:g}, b {B_STRIP:.0f}", "XY",
        6 * R * A_STRIP / (B_STRIP * P.PLATE_T ** 2), ALLOW_XY_MPA, req)
    F_scr = MU_WORN * R * RG.R_OUT / RG.TAB_R
    row(lbl, f"ring path: friction {MU_WORN} x R on one ring screw, bearing in the plate pilot (L {RING_SCREW_L:g})", "bearing",
        F_scr / (D_PIL_PRINT * RING_SCREW_L), BEARING_MPA, req)

# --- cradle bosses (unchanged since round 3) -------------------------------------------------------------------------------
F_USB = 20.0
I_boss = math.pi * (P.CRADLE_BOSS_D ** 4 - (P.PILOT + HOLE_COMP) ** 4) / 64
row(f"USB insertion {F_USB:g} N / 3 bosses", "cradle-boss root bending (Kt 2.5)", "Z",
    2.5 * F_USB / 3 * P.CRADLE_BOSS_L * (P.CRADLE_BOSS_D / 2) / I_boss, allow(True), SF_STATIC)
CR_CLAMP = (CR.TOP - CR.BOT) - CR.CBORE_DEPTH
eng = min(P.CRADLE_BOSS_L, 10.0 - CR_CLAMP)
row("10 N jumper pull / 2 screws", f"cradle screw pull-out, {eng:g} mm engaged", "Z shear",
    5.0 / (math.pi * P.PILOT * eng), allow(True, True), SF_STATIC)

# --- advisory: the ring sharing the moment once the 0.3-0.4 mm gap closes ----------------------------------------------------
D_PL = E_MPA * P.PLATE_T ** 3 / (12 * (1 - NU ** 2))
k_s = 18.43 * D_PL                          # rigid boss b 9.85 in a clamped plate a 49 (derived for this review), N.mm/rad
I_strip = B_STRIP * P.PLATE_T ** 3 / 12
k_r = RG.R_OUT ** 2 * 3 * E_MPA * I_strip / A_STRIP ** 3     # ring force at r 44 on the plate strip
for gap in (0.4, 0.3):
    phi = gap / RG.R_OUT
    for mode in ("weight", "yaw"):
        lbl, req = MODES[mode]
        M = probes["tabs"].get(mode, "Mh")[0]
        Ms = M if M <= k_s * phi else k_s * phi + (M - k_s * phi) * k_s / (k_s + k_r)
        S = TOR_SHARE * Ms / TAB_LEVER_W
        row(lbl, f"servo path with the ring sharing past a {gap:g} mm gap (play-free servo): M_servo {Ms:.0f} of {M:.0f}",
            "XY", plate_at_tab(S), ALLOW_XY_MPA, req, info=True)
for mode in ("weight", "yaw"):
    lbl, req = MODES[mode]
    M = probes["tabs"].get(mode, "Mh")[0]
    Ms = M * k_s / (k_s + k_r)
    row(lbl, f"FIX: ring at zero gap (disk resting on the taped ring): servo path takes {k_s / (k_s + k_r):.2f}, "
        f"M_servo {Ms:.0f}", "XY", plate_at_tab(TOR_SHARE * Ms / TAB_LEVER_W), ALLOW_XY_MPA, req, info=True)
M_yaw = probes["tabs"].get("yaw", "Mh")[0]
for t in (6.0, 6.5, 7.0):
    row(MODES["yaw"][0], f"FIX: top plate {t:g} mm round the servo (servo path, ring ignored)", "XY",
        plate_at_tab(TOR_SHARE * M_yaw / TAB_LEVER_W, t), ALLOW_XY_MPA, SF_STATIC, info=True)
for t in (7.0, 7.5):
    row(MODES["yaw"][0], f"top plate {t:g} mm, corners left fully sharp (Kt 2.5 instead of {KT_PLATE})", "XY",
        plate_at_tab(TOR_SHARE * M_yaw / TAB_LEVER_W, t) * 2.5 / KT_PLATE, ALLOW_XY_MPA, SF_STATIC, info=True)
row(MODES["weight"][0], "FIX: top plate 7 mm round the servo (servo path, ring ignored)", "XY",
    plate_at_tab(TOR_SHARE * probes["tabs"].get("weight", "Mh")[0] / TAB_LEVER_W, 7.0), ALLOW_XY_MPA, SF_SUSTAINED, info=True)
row(MODES["weight"][0], "top plate 7.5 mm round the far tab, Kt 2.5", "XY",
    plate_at_tab(TOR_SHARE * probes["tabs"].get("weight", "Mh")[0] / TAB_LEVER_W, 7.5) * 2.5 / KT_PLATE, ALLOW_XY_MPA,
    SF_SUSTAINED, info=True)
for mode in ("yaw", "weight"):                # the near tab takes the other 35 %; the ESP32 cradle limits a pad there
    lbl, req = MODES[mode]
    row(lbl, f"top plate 5.5 mm round the near tab ({1 - TOR_SHARE:.2f} of M), Kt 2.5", "XY",
        plate_at_tab((1 - TOR_SHARE) * probes["tabs"].get(mode, "Mh")[0] / TAB_LEVER_W, 5.5) * 2.5 / KT_PLATE, ALLOW_XY_MPA,
        req, info=True)
row(f"yaw-stall sweep, tab screws over-tightened to {PRELOAD_TIGHT_N:.0f} N", f"notch strip {LIG:.2f}: splitting", "XY",
    splitting(PRELOAD_TIGHT_N + TOR_SHARE * M_yaw / TAB_LEVER_W, D_THREAD, D_MEAN, L_ENG, LIG), ALLOW_XY_MPA, SF_STATIC,
    info=True)

worst, fails = report(JOB)

# --- stability (spec §4, SYS-12) ------------------------------------------------------------------------------------------
st = TB["stability_arm_straight_out"]
print("\nSTABILITY (torque_budget.json, sliced masses): free-standing SF " +
      ", ".join(f"{k} {v['sf_free_standing']}" for k, v in st.items() if k.startswith("camera")) +
      " -> the desk screws (or the 200 x 200 board / ballast) stay required")
W_robot = (sum(i[1] for i in ITEMS) + mass_g(JOB) + mass_g("20261025-arm-turntable-ring") + mass_g("20261025-arm-esp32-cradle")
           + BS.mass_g + 35.0) * GN
for mode in ("yaw", "hand"):
    Md = probes["desk"].get(mode, "Mh")[0]
    edge = P.BY / 2
    up = max(Md - W_robot * edge, 0.0) / (2 * edge)
    print(f"  {MODES[mode][0]}: {Md:.0f} N.mm about the desk against {W_robot * edge:.0f} restoring -> uplift {up:.1f} N per desk "
          f"screw (2 screws, {edge:g} mm lever)")

# --- proof tests (spec §8 as this review would write it) --------------------------------------------------------------------
print("\nPROOF TEST (spec §8 as this review would write it). Ratio = test value / yaw-stall service value.")


def servo_share(M, gap=0.4):
    """Moment through the servo path when the ring shares past a running gap (play-free servo)."""
    phi = gap / RG.R_OUT
    return M if M <= k_s * phi else k_s * phi + (M - k_s * phi) * k_s / (k_s + k_r)


Mt_yaw, Mr_yaw = probes["tabs"].get("yaw", "Mh")[0], probes["ring"].get("yaw", "Mh")[0]
for name, (pose, F_N) in ARM_TESTS.items():
    Mt = probes["tabs"].checks["Mh"](*test_loads(probes["tabs"], pose, F_N))
    Mr = probes["ring"].checks["Mh"](*test_loads(probes["ring"], pose, F_N))
    F15 = force_for(lambda F: probes["tabs"].checks["Mh"](*test_loads(probes["tabs"], pose, F)) / Mt_yaw, PROOF_RATIO)
    print(f"  {name}, {F_N:g} N, base screwed down: servo path (ring ignored) {Mt:.0f} N.mm = {Mt / Mt_yaw:.2f} x; with the "
          f"ring sharing past 0.4 mm {servo_share(Mt):.0f} = {servo_share(Mt) / servo_share(Mt_yaw):.2f} x; ring path "
          f"{Mr / Mr_yaw:.2f} x; {PROOF_RATIO:g} x on the servo path at {F15:.1f} N")
F_rim = PROOF_RATIO * Mr_yaw / TT.DISK_R
M_rim = F_rim * TT.DISK_R + probes["tabs"].get("weight", "Mh")[0] / DYN
print(f"  rim test: {PROOF_RATIO:g} x the yaw-stall ring load = {F_rim:.0f} N straight down on the turntable rim (r {TT.DISK_R:g}); "
      f"the servo path then takes at most {servo_share(M_rim):.0f} N.mm ({servo_share(M_rim) / servo_share(Mt_yaw):.2f} x its "
      f"yaw-stall share), because the ring sits right under the load")
print(f"  spec §8 rim test as written: 50 N = {50.0 * TT.DISK_R / R_RING / (Mr_yaw / R_RING):.2f} x the yaw-stall ring load")

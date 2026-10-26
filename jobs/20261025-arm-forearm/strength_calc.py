"""Strength check for jobs/20261025-arm-forearm: Forearm (elbow -> wrist) (round 5, independent re-check, 2026-10-26).

Run from the project root:  python3 jobs/20261025-arm-forearm/strength_calc.py
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

# ============================================== 20261025-arm-forearm (round 5) ==============================================
JOB = "20261025-arm-forearm"
P = FA
HS, WS = MG996R, MG90S                      # elbow horn servo, wrist servo
FLOOR = P.T - HORN_DEPTH                    # 8: material over the elbow horn, under the clamp washer
D_WASHER = 9.0                              # Ø9 x 0.8 (ISO 7093) under the M3 x 14 clamp (BUILD_GUIDE §1)
LEV_TILT_ARMS = HS.horn_arm_len             # 17.5: tilting about the link's y axis pivots on a horn-arm tip
LEV_TILT_HUB = HS.horn_d / 2                # 5.5: tilting about the link's x axis pivots on the hub edge
WM = servo_mount(WS, P.CLR, P.END_CLR, lead="notch_shift_pilot", pilot_shift=1.3)
X_SERVO = P.L + WM.xm                       # 84.5: wrist-servo body centre
PIL_FAR, PIL_NEAR = P.L + WM.pilots[0][0], P.L + WM.pilots[1][0]          # 70.6, 99.7 (moved 1.3 out)
WIN_X0, WIN_X1 = P.L + WM.win_x[0], P.L + WM.win_x[1]                     # 72.9, 96.1
D_PIL_PRINT = WS.screw_pilot_d              # 1.5 printed (1.7 CAD)
D_THREAD = 2.0                              # M2 self-tapper, major diameter
D_MEAN = (D_THREAD + D_PIL_PRINT) / 2       # thread flank contact
L_ENG = 12.0 - WS.tab_t                     # M2 x 12 through the 2.5 mm tab: 9.5 mm in the 10 mm plate
L_BEAR = 2 * D_THREAD                       # side load on a screw bears over its first two diameters (assumption)
# the MG90S screw strips. CAD widths from the cutter's geometry; DFM round 4 measured 1.340 / 1.450 on sections of build()
# (the cutter's 0.01 notch overlap), so the smaller one is used. The M2 thread cuts (2.0 - 1.7) / 2 beyond the CAD hole:
# the strip that is left behind the thread crests is 0.15 mm narrower (DFM: "≈ 1.3 / 1.4 mm intact" printed).
LIG_LEAD_CAD = min(WM.ligaments[1], 1.340)  # notch end wall -> moved (lead-end) pilot
LIG_FAR_CAD = min(WM.ligaments[0], 1.450)   # window end -> far pilot
LIG_LEAD = LIG_LEAD_CAD - (D_THREAD - WM.d_pilot) / 2
LIG_FAR = LIG_FAR_CAD - (D_THREAD - WM.d_pilot) / 2
LIG_LEAD_OTHER = P.X1 - (PIL_NEAR + 0.4 + WM.d_pilot / 2) - (D_THREAD - WM.d_pilot) / 2   # slot end -> plate end
TAB_HALF_W = WS.width / 2                   # 6.1: twisting about the forearm axis pries a tab about its long edge
TAB_LEVER_L = min(PIL_NEAR - (X_SERVO - WS.tab_span / 2), (X_SERVO + WS.tab_span / 2) - PIL_FAR)   # 30.0
R_FAR, R_NEAR = P.L - PIL_FAR, PIL_NEAR - P.L                             # 19.4, 9.7 from the wrist shaft
SCREW_SPACING = PIL_NEAR - PIL_FAR                                        # 29.1
# twisting split between the two tabs (each held by ONE screw on the centre line): the near tab's path runs through the
# window rails, so it takes less. Stiffness estimate: rails as a frame 2.1e5 N.mm/rad, one tab prying 0.4-2.2e5 ->
# far tab 54-67 %, near tab 33-46 %. Used: 70 % on the far screw, 50 % on the near one and through the rails.
TOR_FAR, TOR_NEAR = 0.70, 0.50
# window rails between the tab rows: a single screw per tab can't pass a moment about the link's y axis, so (statics)
# the rails carry P2 x (x_near - x): at the window's far end that is PIN of the moment at the far pilot row.
RAIL_W = P.HALF_W - WM.win_hw               # 6.6
I_RAILS = 2 * RAIL_W * P.T ** 3 / 12        # out of plane, both rails
I_RAIL1 = RAIL_W * P.T ** 3 / 12
I_RAILS_IP = 2 * (P.T * RAIL_W ** 3 / 12 + P.T * RAIL_W * (WM.win_hw + RAIL_W / 2) ** 2)
L_WIN, D_RAILS = WIN_X1 - WIN_X0, 2 * (WM.win_hw + RAIL_W / 2)
PIN = (PIL_NEAR - WIN_X0) / (PIL_NEAR - PIL_FAR)
KT_CORNER, KT_HOLE = 2.5, 2.0
# plate sections (out of plane I; CAD values from build123d sections, printed for comparison)
POCKET_W = 6.9                              # horn pocket width at x 15 (arm 6.3 + 0.5 clearance + HOLE_COMP)
B, T = 2 * P.HALF_W, P.T


def sec_pocket():
    A = B * T - POCKET_W * HORN_DEPTH
    zc = (B * T * T / 2 - POCKET_W * HORN_DEPTH * HORN_DEPTH / 2) / A
    I = B * T ** 3 / 12 + B * T * (T / 2 - zc) ** 2 - (POCKET_W * HORN_DEPTH ** 3 / 12 + POCKET_W * HORN_DEPTH * (HORN_DEPTH / 2 - zc) ** 2)
    return I, max(zc, T - zc)


I_X15, C_X15 = sec_pocket()
I_FULL = B * T ** 3 / 12
I_ROW = (B - WM.d_pilot) * T ** 3 / 12
I_IP_FULL = T * B ** 3 / 12
CAD_I = {"x15": 1926.9, "x30": 2162.9, "row": 2021.2, "rails": 1096.2}    # build123d sections, 2026-10-26
ALPHA = 0.267 + (0.282 - 0.267) * (B / T - 2.5) / 1.5     # torsion coefficient, b/t 2.5 -> 4 (Roark)


def s_far(F, M):
    return TOR_FAR * abs(M[0]) / TAB_HALF_W + abs(M[1]) / TAB_LEVER_L + abs(F[2]) / 2


def s_near(F, M):
    return TOR_NEAR * abs(M[0]) / TAB_HALF_W + abs(M[1]) / TAB_LEVER_L + abs(F[2]) / 2


def side_load(F, M):
    """Worst in-plane force on one tab screw: the in-plane force on the servo (all on one screw) plus the couple of the
    moment about the plate normal over the screw spacing."""
    return math.hypot(F[0], F[1]) + abs(M[2]) / SCREW_SPACING


def rails(F, M, t=None):
    """Window rails between the tab rows, depth t (T as drawn; T + h with back-face ribs as wide as the rails)."""
    t = T if t is None else t
    i_r, i_1 = 2 * RAIL_W * t ** 3 / 12, RAIL_W * t ** 3 / 12
    i_ip = 2 * (t * RAIL_W ** 3 / 12 + t * RAIL_W * (WM.win_hw + RAIL_W / 2) ** 2)
    oop = PIN * abs(M[1]) * (t / 2) / i_r + TOR_NEAR * abs(M[0]) * L_WIN / (2 * D_RAILS) * (t / 2) / i_1
    ip = PIN * abs(M[2]) * P.HALF_W / i_ip
    return max(KT_CORNER * (oop + ip * WM.win_hw / P.HALF_W), oop + ip)


RIBS = (4.0, 6.0, 8.0)                      # what-if: back-face ribs on both rails (the forearm prints front face down)


def hoop(S, lig):
    return splitting(S, D_THREAD, D_MEAN, L_ENG, lig)


def tearout(F, lig):
    return F / (2 * lig * L_BEAR)


def pullout(S):
    return S / (math.pi * D_PIL_PRINT * L_ENG)


absM = lambda k: (lambda F, M: abs(M[k]))
F_items = [i for i in ITEMS if i[2] == "F"]
probes = {
    "horn": Probe("elbow-horn joint", "F", (0.0, 0.0, HORN_DEPTH),
                  own_items=[i for i in F_items if i[0] != "elbow horn + clamp"],
                  checks={"S": lambda F, M: abs(M[1]) / LEV_TILT_ARMS + abs(M[0]) / LEV_TILT_HUB + abs(F[2])}),
    "x15": Probe("x 15 over the pocket", "F", (15.0, 0.0, T / 2),
                 own_items=link_beyond("F", JOB, 15.0, P.X0, P.X1, exclude=("forearm",)),
                 checks={"My": absM(1), "Mx": absM(0), "Mz": absM(2)}),
    "x30": Probe("x 30 full section", "F", (30.0, 0.0, T / 2),
                 own_items=link_beyond("F", JOB, 30.0, P.X0, P.X1, exclude=("forearm",)),
                 checks={"My": absM(1), "Mx": absM(0)}),
    "row": Probe("far pilot row", "F", (PIL_FAR, 0.0, T / 2),
                 own_items=link_beyond("F", JOB, PIL_FAR, P.X0, P.X1, exclude=("forearm",)),
                 checks=dict({"My": absM(1), "rails": rails},
                             **{f"rails_h{h:g}": (lambda F, M, t=T + h: rails(F, M, t)) for h in RIBS})),
    "tabs": Probe("wrist tab plane", "F", (X_SERVO, 0.0, P.T),
                  own_items=[i for i in F_items if i[0] == "wrist MG90S"],
                  checks={"S_far": s_far, "S_near": s_near, "side": side_load, "Mx": absM(0), "My": absM(1)}),
}
model_check()
print(f"forearm: wrist MG90S window x {WIN_X0:.2f}-{WIN_X1:.2f}, pilots x {PIL_FAR:.2f} / {PIL_NEAR:.2f}; strips CAD "
      f"{LIG_LEAD_CAD:.2f} (lead end) / {LIG_FAR_CAD:.2f} (far end), intact behind the M2 thread {LIG_LEAD:.2f} / "
      f"{LIG_FAR:.2f}; rails {RAIL_W:.2f} x {T:g}, pin share at the window's far end {PIN:.3f}")
print(f"sections (out of plane): x15 I {I_X15:.0f} (CAD {CAD_I['x15']}), full {I_FULL:.0f} (CAD {CAD_I['x30']}), "
      f"pilot row {I_ROW:.0f} (CAD {CAD_I['row']}), rails {I_RAILS:.0f} (CAD {CAD_I['rails']})")
n = sweep(list(probes.values()))
print(f"{n} poses swept (shoulder {TRAVEL['shoulder']}, elbow {TRAVEL['elbow']}, wrist {TRAVEL['wrist']}, {STEP_DEG} deg)")
for k, pr in probes.items():
    shown = [c for c in pr.checks if not c.startswith("rails_h")]
    print(f"  {pr.name}: " + "; ".join(f"{m} " + ", ".join(f"{c} {pr.get(m, c)[0]:.0f}" for c in shown)
                                     for m in ("weight", "yaw", "hand")))

# --- local cases (not swept) --------------------------------------------------------------------------------------------
W_EE_N = (EE_G + PAYLOAD_G) * GN            # claw + camera + payload beyond the wrist horn
p_horn = 3 * STALL_MG996R_NMM / (2 * HORN_DEPTH * (HS.horn_arm_len + HS.horn_tip_d / 2) ** 2)
row("elbow stall 1079 N.mm", "horn-pocket wall bearing (arm flanks, triangular, 2 mm deep)", "bearing", p_horn,
    BEARING_MPA, SF_STATIC)
row("elbow stall 1079 N.mm", "in-plane bending, full section (M <= stall)", "XY",
    STALL_MG996R_NMM * (B / 2) / I_IP_FULL, ALLOW_XY_MPA, SF_STATIC)
F_stall_far = STALL_MG90S_NMM * R_FAR / (R_FAR ** 2 + R_NEAR ** 2) + W_EE_N
F_stall_near = STALL_MG90S_NMM * R_NEAR / (R_FAR ** 2 + R_NEAR ** 2) + W_EE_N
row("wrist stall 216 N.mm + static claw weight", f"far pilot bearing, F {F_stall_far:.1f} N", "bearing",
    F_stall_far / (D_PIL_PRINT * L_BEAR), BEARING_MPA, SF_STATIC)

# --- swept cases ----------------------------------------------------------------------------------------------------------
for mode, (lbl, req) in MODES.items():
    pr = probes["horn"]
    row(lbl, f"clamped elbow-horn joint: Ø{D_WASHER:g} washer pull-through, floor {FLOOR:g} (S {pr.get(mode, 'S')[0]:.0f} N; "
        f"{where(pr, mode, 'S')})", "Z shear", pr.get(mode, "S")[0] / (math.pi * D_WASHER * FLOOR), allow(True, True), req)
for mode, (lbl, req) in MODES.items():
    pr = probes["x15"]
    row(lbl, f"x 15 over the pocket, out of plane (Kt 2 arm-screw hole; M {pr.get(mode, 'My')[0]:.0f})", "XY",
        KT_HOLE * pr.get(mode, "My")[0] * C_X15 / I_X15, ALLOW_XY_MPA, req)
pr = probes["x30"]
row(MODES["yaw"][0], f"x 30 full section, out of plane (M {pr.get('yaw', 'My')[0]:.0f})", "XY",
    pr.get("yaw", "My")[0] * (T / 2) / I_FULL, ALLOW_XY_MPA, SF_STATIC)
for mode, (lbl, req) in MODES.items():
    pr = probes["row"]
    row(lbl, f"far MG90S pilot row x {PIL_FAR:.1f}, out of plane (Kt 2; M {pr.get(mode, 'My')[0]:.0f}; {where(pr, mode, 'My')})",
        "XY", KT_HOLE * pr.get(mode, "My")[0] * (T / 2) / I_ROW, ALLOW_XY_MPA, req)
for mode, (lbl, req) in MODES.items():
    pr = probes["row"]
    row(lbl, f"window rails 2 x {RAIL_W:.1f} at the far window end, tab screws as pins (Kt {KT_CORNER}; {where(pr, mode, 'rails')})",
        "XY", pr.get(mode, "rails")[0], ALLOW_XY_MPA, req)
for mode, (lbl, req) in MODES.items():
    pr = probes["x15"]
    row(lbl, f"plate torsion, full width (T {pr.get(mode, 'Mx')[0]:.0f})", "Z shear",
        pr.get(mode, "Mx")[0] / (ALPHA * B * T ** 2), allow(True, True), req)
for mode, (lbl, req) in MODES.items():
    pr = probes["tabs"]
    S = pr.get(mode, "S_far")[0]
    row(lbl, f"MG90S tab screw pull-out, far screw S {S:.0f} N (L {L_ENG:g}, Ø{D_PIL_PRINT:g}; {where(pr, mode, 'S_far')})",
        "Z shear", pullout(S), allow(True, True), req)

# --- the two MG90S screw strips: every spec §4 case that runs through the tab screws, and the §8 tests ---------------------
STRIPS = (("lead-end strip (notch -> moved pilot)", LIG_LEAD, "S_near"), ("far-end strip (window -> far pilot)", LIG_FAR, "S_far"))
for name, lig, skey in STRIPS:
    for mode, (lbl, req) in MODES.items():
        pr = probes["tabs"]
        Fs = pr.get(mode, "side")[0]
        row(lbl, f"{name} {lig:.2f} intact: tear-out toward the strip, side load {Fs:.1f} N", "XY shear",
            tearout(Fs, lig), allow(False, True), req)
        S = pr.get(mode, skey)[0]
        row(lbl, f"{name} {lig:.2f}: splitting, snug preload {PRELOAD_SNUG_N:.0f} N + screw tension {S:.0f} N", "XY",
            hoop(PRELOAD_SNUG_N + S, lig), ALLOW_XY_MPA, req)
    F_w = F_stall_near if skey == "S_near" else F_stall_far
    row("wrist stall 216 N.mm + static claw weight", f"{name} {lig:.2f}: tear-out, side load {F_w:.1f} N", "XY shear",
        tearout(F_w, lig), allow(False, True), SF_STATIC)
Fs_yaw = probes["tabs"].get("yaw", "side")[0]
row(MODES["yaw"][0], f"lead-end pilot, side load along the strips: net section {LIG_LEAD:.2f} + {LIG_LEAD_OTHER:.2f} (Kt 2)",
    "XY", KT_HOLE * Fs_yaw / ((LIG_LEAD + LIG_LEAD_OTHER) * L_BEAR), ALLOW_XY_MPA, SF_STATIC)
# spec §8 (proof and first-print checks) through the strips; required SF at a proof load: 3 / 1.5 = 2
S_8_2a = 15.0 / 2 + 15.0 * (P.L - X_SERVO) / TAB_LEVER_L          # 15 N along the wrist shaft, at the wrist axis
S_8_2b = TOR_FAR * 7.5 * 95.0 / TAB_HALF_W                          # 7.5 N on a 95 mm lever: 712 N.mm about the forearm axis
for name, lig, skey in STRIPS:
    row("spec §8 screw-strip check: M2 x 12 driven snug", f"{name} {lig:.2f}: splitting at {PRELOAD_SNUG_N:.0f} N",
        "XY", hoop(PRELOAD_SNUG_N, lig), ALLOW_XY_MPA, SF_SUSTAINED)
    row("spec §8 proof (1): 1 kg at the wrist axis, in plane", f"{name} {lig:.2f}: tear-out, 9.8 N on one screw", "XY shear",
        tearout(9.81, lig), allow(False, True), SF_PROOF)
    row("spec §8 proof (2): 15 N along the wrist shaft", f"{name} {lig:.2f}: splitting, preload + {S_8_2a:.1f} N", "XY",
        hoop(PRELOAD_SNUG_N + S_8_2a, lig), ALLOW_XY_MPA, SF_PROOF)
    row("spec §8 proof (2): 7.5 N on a 95 mm lever", f"{name} {lig:.2f}: splitting, preload + {S_8_2b:.0f} N", "XY",
        hoop(PRELOAD_SNUG_N + S_8_2b, lig), ALLOW_XY_MPA, SF_PROOF)
row("spec §8 proof (2): 7.5 N on a 95 mm lever", f"MG90S tab screw pull-out, S {S_8_2b:.0f} N", "Z shear", pullout(S_8_2b),
    allow(True, True), SF_PROOF)

# --- advisory ---------------------------------------------------------------------------------------------------------------
k_tab = 4.0e4                                # one MG90S tab prying about y (soft end of the estimate), N.mm/rad
phi_r = E_MPA * I_RAILS / (PIL_NEAR - PIL_FAR)
kk = k_tab / phi_r                           # tab springs instead of pins: share of the far-row moment in the rails
m2 = -(kk / 6) / (1 + kk / 2)
Q = 1 / (1 + kk * (1 / 3 + m2 / 2) + m2)
share_spring = Q * PIN + m2 * Q
pr = probes["row"]
row(MODES["yaw"][0], f"window rails with tab springs ({share_spring:.2f} of the row moment instead of {PIN:.2f})", "XY",
    pr.get("yaw", "rails")[0] * share_spring / PIN, ALLOW_XY_MPA, SF_STATIC, info=True)
M_crash = 4.8 * STALL_MG90S_NMM              # SYS-11: a desk crash back-drives the wrist at 3-5 x its stall
F_crash = M_crash * R_FAR / (R_FAR ** 2 + R_NEAR ** 2)
row("desk crash (SYS-11), wrist back-driven at 1040 N.mm", f"far-end strip {LIG_FAR:.2f}: tear-out, {F_crash:.0f} N", "XY shear",
    tearout(F_crash, LIG_FAR), allow(False, True), SF_STATIC, info=True)
row("desk crash (SYS-11)", f"far pilot bearing, {F_crash:.0f} N", "bearing", F_crash / (D_PIL_PRINT * L_BEAR), BEARING_MPA,
    SF_STATIC, info=True)
S_yaw = probes["tabs"].get("yaw", "S_far")[0]
for name, lig, skey in STRIPS:
    row(f"yaw-stall sweep, tab screws over-tightened to {PRELOAD_TIGHT_N:.0f} N", f"{name} {lig:.2f}: splitting", "XY",
        hoop(PRELOAD_TIGHT_N + probes["tabs"].get("yaw", skey)[0], lig), ALLOW_XY_MPA, SF_STATIC, info=True)
row("yaw-stall sweep, stock bag screws (≈5 mm engaged)", "MG90S tab screw pull-out", "Z shear",
    S_yaw / (math.pi * D_PIL_PRINT * 5.0), allow(True, True), SF_STATIC, info=True)
row(f"yaw-stall sweep with a {CLONE_FACTOR * 11:.0f} kgf.cm clone MG996R", "MG90S tab screw pull-out", "Z shear",
    pullout(S_yaw) * CLONE_FACTOR, allow(True, True), SF_STATIC, info=True)

worst, fails = report(JOB)

# --- what would pass (FAIL rows) ----------------------------------------------------------------------------------------------
print("\nWHAT-IF (the yaw stall governs; every line pose by pose, SF 3 required, 4 for weight x2):")
for h in RIBS:
    pr = probes["row"]
    print(f"  rails with {h:g} mm back-face ribs (rails {RAIL_W:.1f} x {T + h:g}): yaw SF "
          f"{ALLOW_XY_MPA / pr.get('yaw', f'rails_h{h:g}')[0]:.2f}, hand SF {ALLOW_XY_MPA / pr.get('hand', f'rails_h{h:g}')[0]:.2f}, "
          f"weight x2 SF {ALLOW_XY_MPA / pr.get('weight', f'rails_h{h:g}')[0]:.2f}")
S_near_yaw = probes["tabs"].get("yaw", "S_near")[0]
print(f"  near (lead-end) tab screw as drawn, M2 x 12, {L_ENG:g} mm engaged: yaw SF {allow(True, True) / pullout(S_near_yaw):.2f} "
      f"(S {S_near_yaw:.0f} N)")
for screw, L in (("M2 x 14", 14.0 - WS.tab_t), ("M2 x 16", 16.0 - WS.tab_t)):
    print(f"  far tab screw {screw} into a back-face boss under the far pilot, {L:g} mm engaged: yaw SF "
          f"{allow(True, True) / (S_yaw / (math.pi * D_PIL_PRINT * L)):.2f}, weight x2 SF "
          f"{allow(True, True) / (probes['tabs'].get('weight', 'S_far')[0] / (math.pi * D_PIL_PRINT * L)):.2f}")

# --- proof tests (spec §8 as this review would write it) ------------------------------------------------------------------
print("\nPROOF TEST (spec §8 as this review would write it). Ratio = test value / yaw-stall service value at the same check.")
PT = [("row", "rails", "window rails"), ("tabs", "S_far", "far tab screw"), ("tabs", "S_near", "near tab screw"),
      ("row", "My", "far pilot row"), ("x15", "My", "x 15 bending"), ("x15", "Mx", "plate torsion"),
      ("horn", "S", "elbow-horn joint")]
print(f"  bench: elbow horn in a vice, plate vertical; a bar on the wrist horn in place of the claw, pushed along the wrist "
      f"shaft {CF.X_TIP:.0f} mm from the wrist axis (where the fingertips are)")
for w in (0, 45, 90):
    pose = (0, 0, w)
    F_r = force_for(lambda F: test_ratio(probes["row"], "rails", pose, F, weight=False), PROOF_RATIO)
    F_s = force_for(lambda F: test_ratio(probes["tabs"], "S_far", pose, F, weight=False), PROOF_RATIO)
    F_x = force_for(lambda F: test_ratio(probes["x15"], "My", pose, F, weight=False), 2.0)
    print(f"    bar at {w} deg: {PROOF_RATIO:g} x at the rails with {F_r:.1f} N, at the far tab screw with {F_s:.1f} N; x 15 "
          f"reaches 2 x at {F_x:.1f} N")
BENCH_POSE, F_BENCH = (0, 0, 45), 19.0
print(f"  chosen: bar at {BENCH_POSE[2]} deg, {F_BENCH:g} N: " + ", ".join(
    f"{lbl} {test_ratio(probes[k], c, BENCH_POSE, F_BENCH, weight=False):.2f}" for k, c, lbl in PT))
F_t, M_t = test_loads(probes["tabs"], BENCH_POSE, F_BENCH, weight=False)
for sname, lig, skey in STRIPS:
    S_t = probes["tabs"].checks[skey](F_t, M_t)
    print(f"    {sname} {lig:.2f}: screw tension {S_t:.0f} N, splitting SF {ALLOW_XY_MPA / hoop(PRELOAD_SNUG_N + S_t, lig):.2f} "
          f"(required {SF_PROOF:g} at a proof load); side load on the screw {probes['tabs'].checks['side'](F_t, M_t):.1f} N")
for name, (pose, F_N) in ARM_TESTS.items():
    print(f"  turntable/base test ({name}, {F_N:g} N, servos powered): " + ", ".join(
        f"{lbl} {test_ratio(probes[k], c, pose, F_N):.2f}" for k, c, lbl in PT))
r15 = [test_ratio(probes[k], c, (0, 0, 0), 15.0, body="F", point=(P.L, 0.0, 0.0), weight=False) for k, c in
       (("row", "rails"), ("tabs", "S_far"))]
print(f"  spec §8 (2) as written: 15 N at the wrist axis: window rails {r15[0]:.2f}, far tab screw {r15[1]:.2f}; 7.5 N on a "
      f"95 mm lever on the tab holes = {7.5 * 95:.0f} N.mm of torsion, {7.5 * 95 / probes['tabs'].get('yaw', 'Mx')[0]:.2f} x the "
      f"yaw-stall torsion at the tab plane ({probes['tabs'].get('yaw', 'Mx')[0]:.0f}), and it bypasses the servo case")

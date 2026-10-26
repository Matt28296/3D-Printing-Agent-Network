"""Strength check for jobs/20261025-arm-upper-link: Upper link (shoulder -> elbow, 100 mm) (links round 6, independent re-check of
the round-6 solid: RIB_TAPER 6 -> 12, the ribs' run-out now 27 degrees to x 52.2; 2026-10-26).

Run from the project root:  python3 jobs/20261025-arm-upper-link/strength_calc.py
Plain Python (no build123d). It reads the jobs' model.py, tools/hobby_parts.py, the shared claw_frame.py, each
geometry.json and the assembly's torque_budget.json, sweeps the arm's poses for the yaw-stall, hand-push and weight
cases, prints every check as a markdown table and ends with the verdict. strength.md explains every assumption.
"""
# ===== shared arm model (links round 5): the same block in the five arm strength_calc.py files (base, turntable,  =====
# ===== ring, upper link, forearm). Plain Python, no build123d: parameters from each job's model.py and the shared  =====
# ===== claw_frame.py (top-level constants evaluated with ast), servo and camera data from tools/hobby_parts.py,     =====
# ===== masses from each job's geometry.json volume. Checked against torque_budget.json (see model_check below).    =====
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

# --- masses: geometry.json volume x 1.27 g/cm^3; centres of mass from build123d (design() of each job, re-measured
# on the round-6 / claw round-4 solids by this review, in each part's design frame). A volume change over 0.5 % prints a
# warning.
CAD = {"20261025-arm-turntable": (90736.5, (0.0, -4.089, 33.724)),          # round 5: 90 mm gussets
       "20261025-arm-upper-link": (44312.3, (44.808, 0.0, 4.199)),          # round 6: RIB_TAPER 12 (re-measured)
       "20261025-arm-forearm": (32851.0, (40.592, 0.0, 4.215)),             # round 6: round MG90S pilots (re-measured)
       "20261026-arm-claw-frame": (46397.2, (9.761, 0.290, 15.013)),        # claw round 4: anchor pilot (re-measured)
       "20261026-arm-claw-cover": (32943.6, (26.646, 1.364, 32.199)),       # claw round 4: 8 mm anchored post (pillars in
                                                                            # the volume, not in the CoG: design())
       "20261026-arm-claw-pinion": (3335.6, (0.0, 0.0, 6.089)),        # pinion frame: its z = claw +x (FACE_W 12)
       "20261026-arm-claw-jaw": (17118.3, (44.071, -2.286, 38.423)),     # jaw A at gap 0; jaw B is it turned
       "20261026-arm-camera-mount": (10479.9, (-8.231, -3.094, 66.085)),
       "20261025-arm-base": (94469.6, (-0.731, 0.262, -12.251)),           # round 5: tab pads
       "20261025-arm-turntable-ring": (13284.1, (0.0, 0.0, 7.806)),         # round 5: washer reliefs (build() volume)
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


def rect_section(rects):
    """Composite section from rectangles (b, z0, z1): area, centroid z, I about the centroidal axis, z range."""
    A = sum(b * (z1 - z0) for b, z0, z1 in rects)
    zc = sum(b * (z1 - z0) * (z0 + z1) / 2 for b, z0, z1 in rects) / A
    I = sum(b * (z1 - z0) ** 3 / 12 + b * (z1 - z0) * ((z0 + z1) / 2 - zc) ** 2 for b, z0, z1 in rects)
    return SimpleNamespace(A=A, zc=zc, I=I, zmin=min(r[1] for r in rects), zmax=max(r[2] for r in rects))


def first_moment(rects, zc, za, zb):
    """First moment about zc of the parts of the rectangles between za and zb (za < zb)."""
    q = 0.0
    for b, z0, z1 in rects:
        lo, hi = max(z0, za), min(z1, zb)
        if hi > lo:
            q += b * (hi - lo) * ((lo + hi) / 2 - zc)
    return q


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


# ========================================= 20261025-arm-upper-link (links round 6) =========================================
JOB = "20261025-arm-upper-link"
P = UL
HS = ES = MG996R                            # shoulder horn servo, elbow servo
FLOOR = P.T - HORN_DEPTH                    # 8: material over the shoulder horn, under the clamp washer
D_WASHER = 9.0                              # Ø9 x 0.8 (ISO 7093) under the M3 x 14 clamp (BUILD_GUIDE §1)
LEV_TILT_ARMS = HS.horn_arm_len             # 17.5: tilting about the link's y axis pivots on a horn-arm tip
LEV_TILT_HUB = HS.horn_d / 2                # 5.5: tilting about the link's x axis pivots on the hub edge
EM = servo_mount(ES, P.CLR, lead="notch")   # notches at both case ends (the MG996R's lead end is unverified)
X_SERVO = P.L + EM.xm                       # 89.85: elbow-servo body centre
PIL_FAR, PIL_NEAR = P.L + EM.pilots[0][0], P.L + EM.pilots[2][0]          # 65.6, 114.1 (rows of two, y +-5)
WIN_X0, WIN_X1 = P.L + EM.win_x[0], P.L + EM.win_x[1]                     # 69.2, 110.5
NOTCH_FAR = (P.L + EM.notches[1][0], P.L + EM.notches[1][1])             # 67.4 .. 69.5
D_PIL_PRINT = ES.screw_pilot_d              # 2.6 printed (2.8 CAD)
D_THREAD = 2.9                              # M3 (ST2.9) self-tapper, major diameter
D_MEAN = (D_THREAD + D_PIL_PRINT) / 2
L_ENG = 12.0 - 0.5 - ES.tab_t               # M3 x 12 + Ø7 x 0.5 washer through the 2.5 mm tab: 9 mm (the pilot is 16 deep now)
L_BEAR = 2 * D_THREAD
LIG_CAD = min(EM.ligaments)                 # notch -> nearest pilot, 1.84 CAD (2.05 printed)
LIG = LIG_CAD - max(D_THREAD - EM.d_pilot, 0.0) / 2
TAB_EDGE = ES.width / 2                     # 9.85
TAB_LEVER_W = ES.hole_dy / 2 + TAB_EDGE     # 14.85: twisting about the link axis pries a tab about its long edge
TAB_LEVER_L = ES.hole_dx / 2 + ES.tab_span / 2   # 51.25: prying about the far tab's tip
R_FAR = math.hypot(P.L - PIL_FAR, ES.hole_dy / 2)
R_NEAR = math.hypot(PIL_NEAR - P.L, ES.hole_dy / 2)
SUM_R2 = 2 * (R_FAR ** 2 + R_NEAR ** 2)
B, T = 2 * P.HALF_W, P.T
RAIL_W = P.HALF_W - EM.win_hw               # 6.85
TR = T + P.RIB_H                            # round 5: rails 6.85 x 16 (plate 10 + back-face rib 6) from x 64.2 to 117
X_TOE = P.RIB_X0 - P.RIB_TAPER              # 52.2 (round 6; 58.2 in round 5): the ribs' run-out meets the back face
TAPER_DEG = math.degrees(math.atan(P.RIB_H / P.RIB_TAPER))    # 27 (round 5: 45)
X_MID = P.RIB_X0 - P.RIB_TAPER / 2          # 58.2: half way down the run-out, ribs 3 deep
KT_TAPER = 1.5                              # the sloped rib top over a smooth section (no step): Kt 1.5, conservative
# twisting split between the two MG996R tabs: each tab has two screws across its width, so a tab joint is stiff in twist
# (est. 0.5-2.4e6 N.mm/rad); the near tab's path runs in series through the window rails as a frame (round 4 est. 0.85e5
# with 10 mm rails; x (16 / 10)^3 = 3.5e5 with the ribs). The far tab's outer screw is checked with all of it (lever 14.85);
# the rails now take 11-29 % instead of 3-13 %: 0.30 is used (round 4 used 0.15).
TOR_FAR, TOR_RAILS = 1.0, 0.30
I_RAILS = 2 * RAIL_W * TR ** 3 / 12
I_RAIL1 = RAIL_W * TR ** 3 / 12
I_RAILS_IP = 2 * (TR * RAIL_W ** 3 / 12 + TR * RAIL_W * (EM.win_hw + RAIL_W / 2) ** 2)
L_WIN, D_RAILS = WIN_X1 - WIN_X0, 2 * (EM.win_hw + RAIL_W / 2)
PIN = (PIL_NEAR - WIN_X0) / (PIL_NEAR - PIL_FAR)               # rails' share of the far-row moment (tab rows as pins)
X_NOTCH = (NOTCH_FAR[0] + NOTCH_FAR[1]) / 2
PIN_NOTCH = (PIL_NEAR - X_NOTCH) / (PIL_NEAR - PIL_FAR)
KT_CORNER, KT_HOLE, KT_TOE = 2.5, 2.0, 2.0  # window / notch corner; pilot hole; the run-out's foot (a 153° corner since
                                            # round 6; 2.0 kept, conservative)
POCKET_W = 6.9                              # horn pocket width at x 15 (arm 6.3 + 0.5 clearance + HOLE_COMP)


def sec_pocket():
    A = B * T - POCKET_W * HORN_DEPTH
    zc = (B * T * T / 2 - POCKET_W * HORN_DEPTH * HORN_DEPTH / 2) / A
    I = B * T ** 3 / 12 + B * T * (T / 2 - zc) ** 2 - (POCKET_W * HORN_DEPTH ** 3 / 12 + POCKET_W * HORN_DEPTH * (HORN_DEPTH / 2 - zc) ** 2)
    return I, max(zc, T - zc)


I_X15, C_X15 = sec_pocket()
I_FULL = B * T ** 3 / 12
RIBS = [(2 * RAIL_W, -P.RIB_H, 0.0)]                                  # both ribs, back face z -6 .. 0 (frame U)
SEC_ROW = rect_section([(B - 2 * EM.d_pilot, 0.0, T)] + RIBS)       # far pilot row x 65.6: plate less 2 pilots + ribs
SEC_NOTCH = rect_section([(B - 2 * EM.notches[1][2], 0.0, T)] + RIBS)   # far lead notch (between the ribs) + ribs
SEC_RIB0 = rect_section([(B, 0.0, T)] + RIBS)                         # full depth starts, x 64.2
SEC_MID = rect_section([(B, 0.0, T), (2 * RAIL_W, -P.RIB_H / 2, 0.0)])  # x 58.2, half way down the run-out (round 6)
SEC_RAIL1 = rect_section([(RAIL_W, -P.RIB_H, T)])                     # one rail in the window
Q_RIBS = abs(first_moment([(B, 0.0, T)] + RIBS, SEC_RIB0.zc, -P.RIB_H, 0.0))
Q_RAIL_ROOT = abs(first_moment([(RAIL_W, -P.RIB_H, T)], SEC_RAIL1.zc, -P.RIB_H, 0.0))
I_IP_FULL = T * B ** 3 / 12
CAD_I = {"x15": 2596.5, "x30": 2829.5, "toe": 2853.0, "mid": 4414.0, "rib0": 7095.0, "row": 6686.1, "notch": 6800.9,
         "rails": 4666.4}           # build123d sections at x 15, 30, 52.3, 58.2, 64.3 (round 6), 65.6, 68.45, 70 (round 5)
ALPHA = 0.267 + (0.282 - 0.267) * (B / T - 3.0) / 1.0     # torsion coefficient, b/t 3 -> 4 (Roark)


def c_max(sec):
    return max(sec.zmax - sec.zc, sec.zc - sec.zmin)


def s_tab(F, M):
    return TOR_FAR * abs(M[0]) / TAB_LEVER_W + abs(M[1]) / (2 * TAB_LEVER_L) + abs(F[2]) / 4


def rail_moment(F, M):
    """Out-of-plane moment in the busier rail at the window's far end: half the pinned-row share of M_y plus the
    differential bending that carries the rails' share of the twist."""
    return PIN * abs(M[1]) / 2 + TOR_RAILS * abs(M[0]) * L_WIN / (2 * D_RAILS)


def hoop(S, lig):
    return splitting(S, D_THREAD, D_MEAN, L_ENG, lig)


def pullout(S):
    return S / (math.pi * D_PIL_PRINT * L_ENG)


# stress functions (MPa) of a section's force F and moment M, in the link's axes; the sweep keeps the worst of each
STRESS = {
    "horn": lambda F, M: (abs(M[1]) / LEV_TILT_ARMS + abs(M[0]) / LEV_TILT_HUB + abs(F[2])) / (math.pi * D_WASHER * FLOOR),
    "x15": lambda F, M: KT_HOLE * abs(M[1]) * C_X15 / I_X15,
    "tors": lambda F, M: abs(M[0]) / (ALPHA * B * T ** 2),
    "x30": lambda F, M: abs(M[1]) * (T / 2) / I_FULL,
    "toe": lambda F, M: KT_TOE * abs(M[1]) * (T / 2) / I_FULL,
    "mid": lambda F, M: KT_TAPER * abs(M[1]) * c_max(SEC_MID) / SEC_MID.I,
    "ribroot": lambda F, M: KT_TOE * (abs(M[1]) * Q_RIBS / SEC_RIB0.I / 2
                                      + TOR_RAILS * abs(M[0]) * L_WIN / (2 * D_RAILS) * Q_RAIL_ROOT / SEC_RAIL1.I)
    / (RAIL_W * P.RIB_TAPER),
    "row": lambda F, M: KT_HOLE * abs(M[1]) * c_max(SEC_ROW) / SEC_ROW.I,
    "notch": lambda F, M: KT_CORNER * PIN_NOTCH * abs(M[1]) * c_max(SEC_NOTCH) / SEC_NOTCH.I,
    "rails": lambda F, M: KT_CORNER * rail_moment(F, M) * c_max(SEC_RAIL1) / SEC_RAIL1.I,
    "railshear": lambda F, M: (abs(M[1]) / (PIL_NEAR - PIL_FAR) / 2 + TOR_RAILS * abs(M[0]) / D_RAILS) * Q_RAIL_ROOT
    / (SEC_RAIL1.I * RAIL_W),
    "pull": lambda F, M: pullout(s_tab(F, M)),
    "split": lambda F, M: hoop(PRELOAD_SNUG_N + s_tab(F, M), LIG),
}
U_items = [i for i in ITEMS if i[2] == "U"]
beyond = lambda x: link_beyond("U", JOB, x, P.X0, P.X1, exclude=("upper link",))
pick = lambda *ks: {k: STRESS[k] for k in ks}
probes = {
    "horn": Probe("shoulder-horn joint", "U", (0.0, 0.0, HORN_DEPTH),
                  own_items=[i for i in U_items if i[0] != "shoulder horn + clamp"], checks=pick("horn")),
    "x15": Probe("x 15 over the pocket", "U", (15.0, 0.0, T / 2), own_items=beyond(15.0), checks=pick("x15", "tors")),
    "x30": Probe("x 30 full section", "U", (30.0, 0.0, T / 2), own_items=beyond(30.0), checks=pick("x30")),
    "toe": Probe(f"x {X_TOE:.1f}, foot of the ribs' run-out", "U", (X_TOE, 0.0, T / 2), own_items=beyond(X_TOE),
                 checks=pick("toe")),
    "mid": Probe(f"x {X_MID:.1f}, half way down the run-out", "U", (X_MID, 0.0, T / 2), own_items=beyond(X_MID),
                 checks=pick("mid")),
    "rib0": Probe(f"x {P.RIB_X0:.1f}, ribs at full depth", "U", (P.RIB_X0, 0.0, T / 2), own_items=beyond(P.RIB_X0),
                  checks=pick("ribroot")),
    "row": Probe("far elbow-pilot row", "U", (PIL_FAR, 0.0, T / 2), own_items=beyond(PIL_FAR),
                 checks=pick("row", "notch", "rails", "railshear")),
    "tabs": Probe("elbow tab plane", "U", (X_SERVO, 0.0, P.T), own_items=[i for i in U_items if i[0] == "elbow MG996R"],
                  checks=pick("pull", "split")),
}
TAPERS = (6.0, 10.0)                         # what-if: round 5's 45-degree run-out and a 10 mm one (full depth still at x 64.2)
for L_ in TAPERS:
    probes[f"toe{L_:g}"] = Probe(f"x {P.RIB_X0 - L_:.1f}", "U", (P.RIB_X0 - L_, 0.0, T / 2), own_items=beyond(P.RIB_X0 - L_),
                                 checks=pick("toe"))
model_check()
print(f"upper link: elbow MG996R window x {WIN_X0:.2f}-{WIN_X1:.2f}, pilot rows x {PIL_FAR:.2f} / {PIL_NEAR:.2f}, far notch "
      f"x {NOTCH_FAR[0]:.2f}-{NOTCH_FAR[1]:.2f}; notch -> pilot strip {LIG_CAD:.2f} CAD ({LIG:.2f} behind the thread); "
      f"rails {RAIL_W:.2f} x {TR:g} (ribs {P.RIB_H:g} deep, x {P.RIB_X0:.1f}-{P.RIB_X1:g}, run-out to x {X_TOE:.1f}); pin share "
      f"at the window's far end {PIN:.3f}, at the notch {PIN_NOTCH:.3f}")
print(f"sections (out of plane, I mm4): x15 {I_X15:.0f} (CAD {CAD_I['x15']}), full {I_FULL:.0f} (CAD x30 {CAD_I['x30']}, "
      f"x52.3 {CAD_I['toe']}), run-out half way {SEC_MID.I:.0f} (CAD x58.2 {CAD_I['mid']}), ribs at full depth {SEC_RIB0.I:.0f} (CAD {CAD_I['rib0']}), pilot row {SEC_ROW.I:.0f} (CAD "
      f"{CAD_I['row']}), notch {SEC_NOTCH.I:.0f} (CAD {CAD_I['notch']}), rails {2 * SEC_RAIL1.I:.0f} (CAD {CAD_I['rails']})")
n = sweep(list(probes.values()))
print(f"{n} poses swept (shoulder {TRAVEL['shoulder']}, elbow {TRAVEL['elbow']}, wrist {TRAVEL['wrist']}, {STEP_DEG} deg)")


def swept(k, c, lbl, dirn, allow_mpa, modes=MODES):
    for mode, (mlbl, req) in modes.items():
        row(mlbl, f"{lbl} ({where(probes[k], mode, c)})", dirn, probes[k].get(mode, c)[0], allow_mpa, req)


# --- local cases -----------------------------------------------------------------------------------------------------
p_horn = 3 * STALL_MG996R_NMM / (2 * HORN_DEPTH * (HS.horn_arm_len + HS.horn_tip_d / 2) ** 2)
row("shoulder stall 1079 N.mm", "horn-pocket wall bearing (arm flanks, triangular, 2 mm deep)", "bearing", p_horn,
    BEARING_MPA, SF_STATIC)
row("shoulder stall 1079 N.mm", "in-plane bending, full section (M <= stall)", "XY",
    STALL_MG996R_NMM * (B / 2) / I_IP_FULL, ALLOW_XY_MPA, SF_STATIC)
row("shoulder stall 1079 N.mm", f"in-plane bending of the window rails, {RAIL_W:.2f} x {TR:g} (Kt {KT_CORNER})", "XY",
    KT_CORNER * STALL_MG996R_NMM * P.HALF_W / I_RAILS_IP, ALLOW_XY_MPA, SF_STATIC)
F_stall = STALL_MG996R_NMM * R_FAR / SUM_R2
row("elbow stall 1079 N.mm", f"far tab pilot bearing, F {F_stall:.1f} N", "bearing", F_stall / (D_PIL_PRINT * L_BEAR),
    BEARING_MPA, SF_STATIC)
row("elbow stall 1079 N.mm", f"notch -> pilot strip {LIG:.2f}: tear-out, F {F_stall:.1f} N", "XY shear",
    F_stall / (2 * LIG * L_BEAR), allow(False, True), SF_STATIC)

# --- swept cases -----------------------------------------------------------------------------------------------------
swept("horn", "horn", f"clamped shoulder-horn joint: Ø{D_WASHER:g} washer pull-through, floor {FLOOR:g}", "Z shear",
      allow(True, True))
swept("x15", "x15", "x 15 over the pocket, out of plane (Kt 2 arm-screw hole)", "XY", ALLOW_XY_MPA)
swept("x15", "tors", "plate torsion, full width at x 15", "Z shear", allow(True, True))
swept("x30", "x30", "x 30 full section, out of plane", "XY", ALLOW_XY_MPA, modes={"yaw": MODES["yaw"]})
swept("toe", "toe", f"x {X_TOE:.1f}, plain plate at the foot of the ribs' {TAPER_DEG:.0f}° run-out (Kt {KT_TOE})", "XY", ALLOW_XY_MPA)
swept("mid", "mid", f"x {X_MID:.1f}, the run-out half way (ribs {P.RIB_H / 2:g} deep), out of plane (Kt {KT_TAPER})", "XY",
      ALLOW_XY_MPA)
swept("rib0", "ribroot", f"rib taper root: the ribs' force fed into the plate across the layers over the {P.RIB_TAPER:g} mm, "
      f"{TAPER_DEG:.0f}° run-out (Kt {KT_TOE})", "Z shear", allow(True, True))
swept("row", "row", f"far elbow-pilot row x {PIL_FAR:.1f}, plate + ribs, out of plane (Kt {KT_HOLE})", "XY", ALLOW_XY_MPA)
swept("row", "notch", f"far lead notch x {NOTCH_FAR[0]:.1f}-{NOTCH_FAR[1]:.1f}, plate + ribs (Kt {KT_CORNER}; "
      f"{PIN_NOTCH:.2f} M)", "XY", ALLOW_XY_MPA)
swept("row", "rails", f"window rails {RAIL_W:.2f} x {TR:g} at the far window end, tab rows as pins, {TOR_RAILS:.2f} of the "
      f"twist (Kt {KT_CORNER})", "XY", ALLOW_XY_MPA)
swept("row", "railshear", "window rails: interlayer shear at the rib's root (z 0)", "Z shear", allow(True, True))
swept("tabs", "pull", f"elbow MG996R tab screw pull-out (L {L_ENG:g}, Ø{D_PIL_PRINT:g})", "Z shear", allow(True, True))
swept("tabs", "split", f"notch -> pilot strip {LIG:.2f}: splitting, snug preload {PRELOAD_SNUG_N:.0f} N + screw tension", "XY",
      ALLOW_XY_MPA)
row("spec §8: tab screws driven snug", f"notch -> pilot strip {LIG:.2f}: splitting at {PRELOAD_SNUG_N:.0f} N", "XY",
    hoop(PRELOAD_SNUG_N, LIG), ALLOW_XY_MPA, SF_SUSTAINED)

# --- spec §8 proof tests (as written since round 5), as rows at the proof SF --------------------------------------------------------
L_BAR = 175.0                                # bar on the elbow horn in place of the forearm
BENCH_POSE, F_BENCH = (0, -60, 0), 16.0
bar = dict(body="F", point=(L_BAR, 0.0, 0.0), weight=False)
PT = [("row", "rails", "window rails"), ("row", "row", "far pilot row"), ("row", "notch", "far lead notch"),
      ("rib0", "ribroot", "rib taper root"), ("toe", "toe", "run-out foot"), ("mid", "mid", "run-out half way"),
      ("x15", "x15", "x 15 bending"),
      ("x15", "tors", "plate torsion"), ("horn", "horn", "shoulder-horn joint"), ("tabs", "pull", "elbow tab screw pull-out"),
      ("tabs", "split", "notch strip splitting")]
lbl_b = f"spec §8 proof (2): {F_BENCH:g} N at {L_BAR:g} mm, bar at {-BENCH_POSE[1]}°"
for k, c, lbl_ in PT:
    row(lbl_b, lbl_, "Z shear" if c in ("tors", "horn", "pull", "ribroot") else "XY",
        probes[k].checks[c](*test_loads(probes[k], BENCH_POSE, F_BENCH, **bar)),
        allow(True, True) if c in ("tors", "horn", "pull", "ribroot") else ALLOW_XY_MPA, SF_PROOF)
F1 = 9.81
row("spec §8 proof (1): 1 kg at the elbow axis, in plane", "in-plane bending at x 15 (Kt 2)", "XY",
    KT_HOLE * F1 * (P.L - 15.0) * (B / 2) / I_IP_FULL, ALLOW_XY_MPA, SF_PROOF)

# --- advisory ----------------------------------------------------------------------------------------------------------
pr = probes["row"]
row(MODES["yaw"][0], f"window rails with round 4's twist share (0.15 instead of {TOR_RAILS:.2f})", "XY",
    KT_CORNER * (pr.get("yaw", "rails")[4][1] and
                 (PIN * abs(pr.get("yaw", "rails")[4][1]) / 2 + 0.15 * abs(pr.get("yaw", "rails")[4][0]) * L_WIN / (2 * D_RAILS)))
    * c_max(SEC_RAIL1) / SEC_RAIL1.I, ALLOW_XY_MPA, SF_STATIC, info=True)
row(f"yaw-stall sweep with a {CLONE_FACTOR * 11:.0f} kgf.cm clone MG996R", "window rails", "XY",
    pr.get("yaw", "rails")[0] * CLONE_FACTOR, ALLOW_XY_MPA, SF_STATIC, info=True)
row(f"yaw-stall sweep with a {CLONE_FACTOR * 11:.0f} kgf.cm clone MG996R", "x 15 over the pocket", "XY",
    probes["x15"].get("yaw", "x15")[0] * CLONE_FACTOR, ALLOW_XY_MPA, SF_STATIC, info=True)
S_yaw = probes["tabs"].get("yaw", "pull")[0] * math.pi * D_PIL_PRINT * L_ENG
row(f"yaw-stall sweep, tab screws over-tightened to {PRELOAD_TIGHT_N:.0f} N", f"notch -> pilot strip {LIG:.2f}: splitting",
    "XY", hoop(PRELOAD_TIGHT_N + S_yaw, LIG), ALLOW_XY_MPA, SF_STATIC, info=True)

worst, fails = report(JOB)

# --- what would pass ---------------------------------------------------------------------------------------------------------
print(f"\nWHAT-IF: the run-out's length (RIB_TAPER), the ribs still at full depth from x {P.RIB_X0:.1f}. The rib-root stress scales with "
      f"{P.RIB_TAPER:g} / RIB_TAPER; SF 3 required (4 weight x2), 2 at the §8 bench test and at the turntable's arm-up test:")
rr = {m: probes["rib0"].get(m, "ribroot")[0] for m in MODES}
rr_b = probes["rib0"].checks["ribroot"](*test_loads(probes["rib0"], BENCH_POSE, F_BENCH, **bar))
rr_a = {nm: probes["rib0"].checks["ribroot"](*test_loads(probes["rib0"], pose, F_N)) for nm, (pose, F_N) in ARM_TESTS.items()}
for L_ in (P.RIB_TAPER,) + TAPERS:
    k = P.RIB_TAPER / L_
    toe = probes["toe"] if L_ == P.RIB_TAPER else probes[f"toe{L_:g}"]
    print(f"  RIB_TAPER {L_:g} (foot at x {P.RIB_X0 - L_:.1f}, {math.degrees(math.atan(P.RIB_H / L_)):.0f}°): rib root yaw SF "
          f"{allow(True, True) / (rr['yaw'] * k):.2f}, hand {allow(True, True) / (rr['hand'] * k):.2f}, weight x2 "
          f"{allow(True, True) / (rr['weight'] * k):.2f}; §8 bench test {allow(True, True) / (rr_b * k):.2f}; arm-up test "
          + ", ".join(f"{allow(True, True) / (v * k):.2f}" for v in rr_a.values())
          + f"; plain plate at the foot (Kt {KT_TOE}) yaw SF {ALLOW_XY_MPA / toe.get('yaw', 'toe')[0]:.2f}")

# --- proof-test summary ------------------------------------------------------------------------------------------------------
print("\nPROOF TEST (spec §8 as written since round 5). Ratio = test value / yaw-stall service value at the same check.")
print(f"  (1) shoulder horn in a vice, 1 kg at the elbow axis in plane: elbow deflection "
      f"{F1 * P.L ** 3 / (3 * E_MPA * I_IP_FULL):.2f} mm (spec: < 2 mm)")
print(f"  (2) {lbl_b}: " + ", ".join(f"{lbl} {test_ratio(probes[k], c, BENCH_POSE, F_BENCH, **bar):.2f}" for k, c, lbl in PT))
for e in (0, -60, -90):
    pose = (0, e, 0)
    F_r = force_for(lambda F: test_ratio(probes["row"], "rails", pose, F, **bar), PROOF_RATIO)
    F_x = force_for(lambda F: test_ratio(probes["x15"], "x15", pose, F, **bar), PROOF_RATIO)
    F_s = force_for(lambda F: test_ratio(probes["tabs"], "pull", pose, F, **bar), PROOF_RATIO)
    print(f"      bar at {-e} deg: {PROOF_RATIO:g} x at the rails with {F_r:.1f} N, at x 15 with {F_x:.1f} N, at the tab screw "
          f"with {F_s:.1f} N")
SF_YAW = {(k, c): (allow(True, True) if c in ("tors", "horn", "pull", "ribroot") else ALLOW_XY_MPA) / probes[k].get("yaw", c)[0]
          for k, c, _ in PT}
for name, (pose, F_N) in ARM_TESTS.items():
    for F_ in (F_N, 11.0):
        rat = {(k, c): test_ratio(probes[k], c, pose, F_) for k, c, _ in PT}
        print(f"  turntable/base test ({name}, {F_:g} N, servos powered): " + ", ".join(
            f"{lbl} {rat[(k, c)]:.2f}" + (f" (SF {SF_YAW[(k, c)] / rat[(k, c)]:.2f})" if rat[(k, c)] > 0.01 else "")
            for k, c, lbl in PT))

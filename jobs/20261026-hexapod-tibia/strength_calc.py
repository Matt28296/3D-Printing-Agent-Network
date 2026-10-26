"""Strength check for jobs/20261026-hexapod-tibia. Run: python3 jobs/20261026-hexapod-tibia/strength_calc.py

strength-analyst, 2026-10-26. Hand calculations (strength-checks skill) on placeholder PETG allowables. The block
between the ==== lines at the top is identical in all five hexapod strength_calc.py files: it re-derives the robot
mass, the leg frames (as assembly_check.py), the tripod load shares of the coded gait (hexapod_test.ino), the drop
loads and the servo caps, from hex_frame.py, tools/hobby_parts.py, the model.py files and the geometry.json files.
"""
# ==== shared hexapod load model (identical block in all five hexapod strength_calc.py) ====================
# Plain Python: reads hex_frame.py, tools/hobby_parts.py, tools/cadlib.py, each hexapod model.py (top-level
# constants, evaluated with ast) and each geometry.json. No build123d needed.
import ast
import json
import math
import os
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
JOBS = os.path.join(ROOT, "jobs")
ASM = os.path.join(JOBS, "20261026-hexapod-assembly")

# --- allowables (library/materials.csv has no rows, no datasheet in inputs/) -> placeholders, best verdict NEEDS_TEST
ALLOW_XY_MPA = 25.0        # strength-checks placeholder, PETG, along the layers
Z_RATIO = 0.5              # across layers / along layers (placeholder)
SHEAR_RATIO = 0.5          # shear = 0.5 x normal (Tresca), as in the arm and rover reviews
E_MPA = 1800.0             # placeholder PETG modulus
SF_STATIC, SF_CYCLIC = 3.0, 4.0     # short-term static; cyclic or sustained (creep)
T_SERVICE_C, T_SOFTEN_C = 40.0, 70.0
RHO_G_MM3 = 1.27e-3        # PETG density
INFILL_FACTOR = 1.0        # printed mass / solid mass: 1.0 = solid volume (upper bound, so loads are conservative);
                           # with 3-4 perimeters and 5 top/bottom layers on 3-7 mm plates the slicer gives ~0.75-0.9
G = 9.81e-3                # N per gram
DYN = 2.0                  # spec: walking dynamics x2
MU = 0.5                   # foot friction (PETG tip on a hard floor; a TPU sock can reach ~1): assumption
DROP_H_MM = 200.0          # spec: 20 cm drop onto the feet
DROP_DELTA_MM = 10.0       # stated stopping distance if the legs held: servo backlash + position band ~4 mm at the
                           # foot, horn/link/floor flex ~3 mm, carpet ~3 mm (assumption)
BACKDRIVE = 2.0            # powered MG90S back-drives at ~2 x stall (gear losses both ways): assumption
SHOVE_N = 3.0              # spec: sideways shove at a foot

cases, advisory = [], []


def allow(across, shear=False):
    a = ALLOW_XY_MPA * (Z_RATIO if across else 1.0)
    return a * (SHEAR_RATIO if shear else 1.0)


def check(name, stress, across, sf_req, shear=False, Kt=1.0, info=False):
    s = Kt * abs(stress)
    a = allow(across, shear)
    sf = a / s if s > 1e-9 else float("inf")
    tag = ("Z" if across else "XY") + (" shear" if shear else "")
    (advisory if info else cases).append((name, tag, s, a, sf, sf_req))
    return sf


def check_util(name, u, sf_req, info=False):
    """Utilisation-type check (demand / capacity at the interlayer shear allowable), shown as an equivalent stress."""
    return check(name, allow(True, True) * u, True, sf_req, shear=True, info=info)


def report(title):
    print(f"\n== {title} ==")
    print("| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |")
    print("|---|---|---|---|---|---|---|---|")
    for i, (n, d, s, a, sf, req) in enumerate(cases, 1):
        print(f"| {i} | {n} | {d} | {s:.2f} | {a:.2f} | {sf:.2f} | {req:.0f} | {'OK' if sf >= req else '**FAIL**'} |")
    if advisory:
        print("\nAdvisory (not in the verdict):")
        print("| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |")
        print("|---|---|---|---|---|---|")
        for n, d, s, a, sf, req in advisory:
            print(f"| {n} | {d} | {s:.2f} | {a:.2f} | {sf:.2f} | {req:.0f} |")
    worst = min(cases, key=lambda r: r[4] / r[5])
    fails = [r for r in cases if r[4] < r[5]]
    print(f"\nlowest SF {worst[4]:.2f} (required {worst[5]:.0f}) at: {worst[0]}")
    print("VERDICT:", "FAIL" if fails else "NEEDS_TEST (placeholder allowables: PASS needs measured data)")
    return worst, fails


# --- read the shared parameters ---------------------------------------------------------------------------
def _lit(n):
    return ast.literal_eval(n)


_FIELDS = {"ServoSpec": ["name", "length", "width", "case_top", "total_h", "tab_height", "tab_t", "tab_span", "hole_dx",
                         "hole_dy", "tab_hole_d", "screw_pilot_d", "shaft_from_end", "horn_kind", "horn_d", "horn_t",
                         "horn_arm_len", "horn_tip_d", "horn_arms", "horn_screw_clear_d", "stall_torque_nmm", "mass_g"],
           "BoardSpec": ["name", "length", "width", "pcb_t", "pins_below", "parts_above", "usb_w", "usb_h"],
           "BoxSpec": ["name", "length", "width", "height", "mass_g", "note"]}
_DEFAULTS = {"ServoSpec": dict(horn_arm_len=0.0, horn_tip_d=0.0, horn_arms=1, horn_screw_clear_d=3.4,
                               stall_torque_nmm=0.0, mass_g=0.0), "BoardSpec": {}, "BoxSpec": dict(mass_g=0.0, note="")}


def read_hobby():
    ns = {}
    for node in ast.parse(open(os.path.join(ROOT, "tools", "hobby_parts.py")).read()).body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)):
            continue
        name, v = node.targets[0].id, node.value
        fn = getattr(getattr(v, "func", None), "id", "")
        try:
            if fn in _FIELDS:
                d = dict(_DEFAULTS[fn])
                d.update(zip(_FIELDS[fn], [_lit(a) for a in v.args]))
                d.update({kw.arg: _lit(kw.value) for kw in v.keywords})
                ns[name] = SimpleNamespace(**d)
            elif fn == "replace":
                d = dict(vars(ns[v.args[0].id]))
                d.update({kw.arg: _lit(kw.value) for kw in v.keywords})
                ns[name] = SimpleNamespace(**d)
            else:
                ns[name] = _lit(v)
        except Exception:
            pass
    for node in ast.parse(open(os.path.join(ROOT, "tools", "cadlib.py")).read()).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "HOLE_COMP_DEFAULT":
            ns["HOLE_COMP_DEFAULT"] = _lit(node.value)
    return ns


HOBBY = read_hobby()
HORN_DEPTH = HOBBY.get("HORN_DEPTH", 2.0)
HOLE_COMP = HOBBY["HOLE_COMP_DEFAULT"]


def horn_face_z(s):
    return (s.total_h - s.tab_height) + 0.6          # same formula as tools/hobby_parts.py


def link_back_z(s, depth=HORN_DEPTH):
    return horn_face_z(s) - depth


def consts(path, base):
    """Top-level constants of a Python file, evaluated in order against `base` (failures skipped)."""
    ns = dict(base, math=math, max=max, min=min, abs=abs, horn_face_z=horn_face_z, link_back_z=link_back_z)
    start = set(ns)
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
            for e, v in zip(t.elts, val):
                ns[e.id] = v
    return {k: v for k, v in ns.items() if k not in start}


H = SimpleNamespace(**consts(os.path.join(ASM, "hex_frame.py"), HOBBY))
SERVO = H.SERVO
STALL = SERVO.stall_torque_nmm          # 216 N.mm at 6 V
T_BD = BACKDRIVE * STALL                 # torque at which a powered servo is driven backwards (assumed)
JOB = {k: "20261026-hexapod-" + k for k in ("coxa", "femur", "tibia", "body-bottom", "body-top")}


def model(part):
    return SimpleNamespace(**consts(os.path.join(JOBS, JOB[part], "model.py"), dict(HOBBY, **vars(H))))


def volume(part):
    return json.load(open(os.path.join(JOBS, JOB[part], "geometry.json")))["volume_mm3"]


# --- robot mass (geometry.json volumes) -------------------------------------------------------------------------
QTY = {"coxa": 6, "femur": 6, "tibia": 6, "body-bottom": 1, "body-top": 1}
M_PART = {k: volume(k) * RHO_G_MM3 * INFILL_FACTOR for k in QTY}
BOUGHT = [("18 x MG90S", 18 * SERVO.mass_g), ("2S 1000 mAh LiPo", HOBBY["LIPO_2S_1000"].mass_g),
          ("2 x PCA9685", 2 * HOBBY["PCA9685_BOARD"].mass_g), ("ESP32 DevKit", 10.0),
          ("6 V UBEC", HOBBY["UBEC_6V_5A"].mass_g), ("wiring, screws, buck", 30.0)]
M_PRINTED = sum(QTY[k] * M_PART[k] for k in QTY)
M_TOTAL = M_PRINTED + sum(m for _, m in BOUGHT)
W_N = M_TOTAL * G
# mass carried by the top deck (deck, both PCA9685, ESP32, UBEC, half the wiring)
M_DECK = M_PART["body-top"] + 2 * HOBBY["PCA9685_BOARD"].mass_g + 10.0 + HOBBY["UBEC_6V_5A"].mass_g + 15.0


# --- leg kinematics (same frames as leg_frames in assembly_check.py) --------------------------------------------
def mmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def mpt(A, p):
    return [A[i][0] * p[0] + A[i][1] * p[1] + A[i][2] * p[2] + A[i][3] for i in range(3)]


def mdir(A, v):
    return [A[i][0] * v[0] + A[i][1] * v[1] + A[i][2] * v[2] for i in range(3)]


def tdir(A, v):
    """Transpose rotation: world direction -> frame axes."""
    return [A[0][i] * v[0] + A[1][i] * v[1] + A[2][i] * v[2] for i in range(3)]


def trans(x=0.0, y=0.0, z=0.0):
    return [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]]


def rotz(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def sub(a, b):
    return [a[i] - b[i] for i in range(3)]


def frame(origin, xd, zd):
    nx = math.sqrt(sum(c * c for c in xd)); nz = math.sqrt(sum(c * c for c in zd))
    x = [c / nx for c in xd]; z = [c / nz for c in zd]; y = cross(z, x)
    return [[x[0], y[0], z[0], origin[0]], [x[1], y[1], z[1], origin[1]], [x[2], y[2], z[2], origin[2]], [0, 0, 0, 1]]


def leg_frames(mx, my, a, coxa=0.0, femur=0.0, tibia=-90.0, z_tab=H.STANCE_Z_TAB):
    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
    S0 = frame((mx, my, z_tab), (ca, sa, 0), (0, 0, -1))
    C = mmul(mmul(S0, trans(0, 0, H.LB)), rotz(coxa))
    S1 = mmul(C, frame((H.L_C, H.Y_F, H.Z_F), (1, 0, 0), (0, 1, 0)))
    F = mmul(mmul(S1, trans(0, 0, H.LB)), rotz(femur))
    S2 = mmul(F, trans(H.L_F, 0, H.T_F))
    T = mmul(mmul(S2, trans(0, 0, H.LB)), rotz(tibia))
    return {"S0": S0, "C": C, "S1": S1, "F": F, "S2": S2, "T": T}, mpt(T, (H.L_T, 0, H.T_T / 2))


# Everything leg-internal is computed in leg 0's coxa frame C at coxa 0 with the world frame shifted so that
# C is the identity: a leg turns rigidly with its coxa, so its internal loads depend only on the foot force
# expressed in C. Foot force components used below: radial (C +x, outward), tangential (C +y), up (C -z).
LEGC = {k: v for k, v in leg_frames(0.0, 0.0, 0.0, z_tab=0.0)[0].items()}
_Cinv_origin = [LEGC["C"][i][3] for i in range(3)]
FR = {}
for _k, _A in LEGC.items():     # every frame re-expressed in C (C is a pure translation of S0 here, plus axes)
    _R = [[sum(LEGC["C"][r][i] * _A[r][j] for r in range(3)) for j in range(3)] for i in range(3)]
    _o = tdir(LEGC["C"], sub([_A[i][3] for i in range(3)], _Cinv_origin))
    FR[_k] = [[_R[0][0], _R[0][1], _R[0][2], _o[0]], [_R[1][0], _R[1][1], _R[1][2], _o[1]],
              [_R[2][0], _R[2][1], _R[2][2], _o[2]], [0, 0, 0, 1]]
FOOT_C = mpt(FR["T"], (H.L_T, 0, H.T_T / 2))


def foot_force_C(radial, tangential, up):
    return [radial, tangential, -up]


def at(frame_name, local_pt, f_C, pt_C=None):
    """Force and moment of the foot force f_C (in C) about the point local_pt of frame `frame_name`,
    both expressed in that frame's axes."""
    A = FR[frame_name]
    q = mpt(A, local_pt)
    p = FOOT_C if pt_C is None else pt_C
    m = cross(sub(p, q), f_C)
    return tdir(A, f_C), tdir(A, m)


def joint_torques(f_C):
    """Servo torques (N.mm) for a foot force in C: coxa (about C z), femur and knee (about their shaft axes)."""
    tc = at("S0", (0, 0, 0), f_C)[1][2]
    tf = at("S1", (0, 0, 0), f_C)[1][2]
    tk = at("S2", (0, 0, 0), f_C)[1][2]
    return tc, tf, tk


# --- load shares in the coded tripod gait (hexapod_test.ino: stance coxae sweep +sw..-sw, femur 0, tibia 0) -----
LEFT = [i for i, (_, my, _) in enumerate(H.LEG_MOUNTS) if my > 0]


def feet_world(phi):
    """Foot positions with every coxa turned 'foot forward' by phi degrees (left legs clockwise from above)."""
    out = []
    for i, (mx, my, a) in enumerate(H.LEG_MOUNTS):
        out.append(leg_frames(mx, my, a, coxa=phi if i in LEFT else -phi)[1])
    return out


def tripod_shares(legs, phi, cg=(0.0, 0.0)):
    p = [feet_world(phi)[i] for i in legs]
    # solve w1+w2+w3 = 1, sum w x = cgx, sum w y = cgy
    A = [[1.0, 1.0, 1.0], [p[0][0], p[1][0], p[2][0]], [p[0][1], p[1][1], p[2][1]]]
    b = [1.0, cg[0], cg[1]]
    det = lambda M: (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
                     + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
    D = det(A)
    w = []
    for j in range(3):
        Mj = [row[:] for row in A]
        for r in range(3):
            Mj[r][j] = b[r]
        w.append(det(Mj) / D)
    return dict(zip(legs, w))


TRIPODS = ((0, 2, 4), (1, 3, 5))          # hexapod_test.ino TRIPOD_A / TRIPOD_B
SW_GAIT, SW_MAX = 15, 30                  # step(..., 15) and MAX_COXA


def max_share(sw):
    best = (0.0, None)
    for tri in TRIPODS:
        for phi in range(-sw, sw + 1):
            for leg, w in tripod_shares(tri, phi).items():
                if w > best[0]:
                    best = (w, (tri, phi, leg))
    return best


SHARE0 = max(tripod_shares(TRIPODS[0], 0).values())
SHARE_GAIT, WHERE_GAIT = max_share(SW_GAIT)
SHARE_MAX, WHERE_MAX = max_share(SW_MAX)
F_STAND6 = W_N / 6.0
F_SUST = SHARE_GAIT * W_N                 # sustained: robot stopped on a tripod (or a foot 2 mm high)
F_WALK = DYN * F_SUST                     # cyclic, replaces the spec's 4 N (2 N x 2)

# --- drop (energy method) and the servo cap -----------------------------------------------------------------------
E_DROP = M_TOTAL * 1e-3 * 9.81 * DROP_H_MM          # N.mm (= mJ)
F_DROP_TOTAL = 2.0 * W_N * (DROP_H_MM + DROP_DELTA_MM) / DROP_DELTA_MM   # linear stop over delta
F_DROP6, F_DROP3 = F_DROP_TOTAL / 6.0, F_DROP_TOTAL / 3.0
# A leg cannot push harder than its servos allow: femur 45*Fup + 70*Fr <= T_BD and knee |70*Fr| <= T_BD give
# Fup <= 2*T_BD/L_F when the floor pushes the splaying foot inward (needs mu >= L_F/(2 L_T)).
F_CAP = 2.0 * T_BD / H.L_F
DELTA6 = E_DROP / (6 * F_CAP - W_N)       # body travel while 6 legs back-drive at the cap
DELTA3 = E_DROP / (3 * F_CAP - W_N)
CLEAR_MM = 49.2                            # assembly_check.json: lowest non-tibia point above the floor


def feasible(f_C, t_cap=T_BD):
    return all(abs(t) <= t_cap * 1.0001 for t in joint_torques(f_C))


def envelope(fup_max, mu=MU, fup_min=None, horizontal="any", n_up=13, n_dir=36, n_mag=6, t_cap=T_BD, extra=None):
    """Foot forces (in C) in a case: 0..fup_max up (or fup_min..fup_max), horizontal force up to mu*up in the
    allowed directions ('any', 'radial', 'none'), every servo torque within t_cap. extra: list of fixed forces."""
    out = []
    lo = fup_max if fup_min is None else fup_min
    ups = [lo + (fup_max - lo) * i / max(n_up - 1, 1) for i in range(n_up)] if fup_min is not None else \
        [fup_max * i / (n_up - 1) for i in range(n_up)]
    for up in ups:
        if horizontal == "none" or mu == 0:
            dirs = [(0.0, 0.0)]
        elif horizontal == "radial":
            dirs = [(1.0, 0.0), (-1.0, 0.0)]
        else:
            dirs = [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in range(0, 360, 360 // n_dir)]
        for (cx, cy) in dirs:
            for k in range(n_mag + 1 if (cx, cy) != (0.0, 0.0) else 1):
                h = mu * abs(up) * k / n_mag
                f = foot_force_C(cx * h, cy * h, up)
                if feasible(f, t_cap):
                    out.append(f)
    return out + (extra or [])


print(f"robot mass {M_TOTAL:.0f} g ({W_N:.2f} N): printed {M_PRINTED:.0f} g at infill factor {INFILL_FACTOR} "
      + ", ".join(f"{k} {QTY[k]}x{M_PART[k]:.1f}" for k in QTY) + "; bought " + ", ".join(f"{n} {m:.0f}" for n, m in BOUGHT))
print(f"foot in C (neutral): x {FOOT_C[0]:.1f} radial, y {FOOT_C[1]:.1f} tangential, z {FOOT_C[2]:.1f} below the coxa"
      f" back face; stance tab plane {H.STANCE_Z_TAB:.1f} mm")
print(f"tripod shares: stance {SHARE0:.3f}, gait sweep +-{SW_GAIT} deg {SHARE_GAIT:.3f} (leg {WHERE_GAIT[2]}, phi"
      f" {WHERE_GAIT[1]}), MAX_COXA +-{SW_MAX} {SHARE_MAX:.3f}")
print(f"per-foot vertical: 6-leg stand {F_STAND6:.2f} N, sustained tripod {F_SUST:.2f} N, walking x{DYN:.0f} "
      f"{F_WALK:.2f} N (spec 4 N)")
print(f"drop {DROP_H_MM:.0f} mm: E {E_DROP:.0f} N.mm; legs rigid, delta {DROP_DELTA_MM:.0f} mm -> {F_DROP6:.1f} N/foot on 6,"
      f" {F_DROP3:.1f} N/foot on 3; servo cap (T_BD {T_BD:.0f}) {F_CAP:.1f} N/foot; body travel at the cap"
      f" {DELTA6:.0f} mm (6 feet) / {DELTA3:.0f} mm (3 feet) vs {CLEAR_MM} mm clearance")
# --- per-foot load cases (foot force in C: radial, tangential, up) -----------------------------------------------
def shove_set(up_max=None):
    up_max = F_SUST if up_max is None else up_max
    return [foot_force_C(SHOVE_N * math.cos(math.radians(a)), SHOVE_N * math.sin(math.radians(a)), u)
            for a in range(0, 360, 10) for u in (0.0, up_max / 2, up_max)]


STALL_SET = ([foot_force_C(0, 0, STALL / H.L_F), foot_force_C(0, 0, -STALL / H.L_F)]
             + [foot_force_C(0, sg * STALL / FOOT_C[0], F_SUST) for sg in (1, -1)]
             + [foot_force_C(sg * STALL / H.L_T, 0, F_SUST) for sg in (1, -1)])
LOAD_CASES = [   # (key, label, foot forces, required SF)
    ("sust", f"sustained: stopped on a tripod, {F_SUST:.2f} N up", [foot_force_C(0, 0, F_SUST)], SF_CYCLIC),
    ("walk", f"walking x{DYN:.0f}: {F_WALK:.2f} N up", [foot_force_C(0, 0, F_WALK)], SF_CYCLIC),
    ("scrub", f"walking foot scrub: {F_SUST:.2f} N up + mu {MU} any direction", envelope(F_SUST, t_cap=STALL), SF_CYCLIC),
    ("shove", f"shove {SHOVE_N:.0f} N any direction, 0..{F_SUST:.2f} N up", shove_set(), SF_STATIC),
    ("stall", "servo stalls at the foot (femur +-4.8 up, coxa 2.8 tang., knee 3.1 rad.)", STALL_SET, SF_STATIC),
    ("drop", f"drop: up to {F_CAP:.1f} N up (servo cap) + radial friction", envelope(F_CAP, horizontal="radial", n_mag=12,
                                                                     extra=[foot_force_C(-T_BD / H.L_T, 0, F_CAP),
                                                                            foot_force_C(0, 0, T_BD / H.L_F)]),
     SF_STATIC),
]
CASE_LABEL = {k: lab for k, lab, _, _ in LOAD_CASES}


def worst_over(forces, fn):
    """Max of fn(f) over a list of foot forces (fn returns a stress or a utilisation)."""
    return max(fn(f) for f in forces)


# ==== end of shared block ========================================================================================

# ==== helpers shared by the leg parts (coxa, femur, tibia) =======================================================
HUB_R = SERVO.horn_d / 2                  # horn hub radius: pivot of a clamped horn joint
WASHER_D = 6.0                            # spec 2: O6 washer under the clamp-screw head
ARM_SCREW_D, ARM_SCREW_L, ARM_SCREW_R = 1.2, 3.0, 13.0   # BUILD_GUIDE: 1.2 mm pilot through the outer horn-arm
                                          # hole (r ~13), small screw ~3 mm engaged: assumption
PRELOAD_SNUG, PRELOAD_FIRM = 125.0, 250.0  # M2 clamp screw at 0.05 / 0.1 N.m (F = T / (0.2 d)): assumption
CLAMP_HOLE = SERVO.horn_screw_clear_d + HOLE_COMP
BEARING = allow(False)                    # compression on a layer face or a vertical wall: in-plane value


def clamp_caps(t_floor, washer_d=WASHER_D):
    a = allow(True, True)
    wash = math.pi * washer_d * t_floor
    arm = math.pi * ARM_SCREW_D * min(t_floor, ARM_SCREW_L)
    cap_far = a * wash * HUB_R                                   # far side lifts: pivot on the arm side of the hub
    cap_arm = a * (wash * HUB_R + arm * (ARM_SCREW_R + HUB_R))   # arm side lifts: pivot on the far hub edge
    cap_T = a * (wash + arm) * HUB_R                             # tilt about the arm axis: pivot on a hub side edge
    return cap_far, cap_arm, cap_T, a * wash


def clamp_util(f_loc, m_loc, t_floor, washer_d=WASHER_D):
    """Clamped horn joint (washer pull-through + arm screw, interlayer shear). f_loc, m_loc: load on the link at the
    pocket floor on the shaft axis, link axes (x along the horn arm, z away from the servo). m_y > 0 lifts the far
    side of the hub (pivot on the arm side, conservatively at the hub edge: the thin horn arm cannot carry it)."""
    cap_far, cap_arm, cap_T, cap_pull = clamp_caps(t_floor, washer_d)
    mt = m_loc[1]
    return abs(mt) / (cap_far if mt > 0 else cap_arm) + abs(m_loc[0]) / cap_T + max(f_loc[2], 0.0) / cap_pull


def horn_bearing_mpa(torque=STALL):
    """Stall torque through the single horn arm onto the pocket wall (5 x pocket depth patch), as on the arm."""
    s = SERVO
    return torque / (s.horn_arm_len + s.horn_tip_d / 2 - 2.5) / (5.0 * HORN_DEPTH)


def preload_rows(t_floor, label):
    for P_n, lab, info in ((PRELOAD_SNUG, "snug 0.05 N.m", False), (PRELOAD_FIRM, "'firmly' 0.1 N.m", True)):
        check(f"assembly: clamp screw {lab} ({P_n:.0f} N): washer pull-through, {t_floor:.1f} mm {label} floor",
              P_n / (math.pi * WASHER_D * t_floor), True, SF_STATIC, shear=True, info=info)
    check(f"assembly: clamp screw snug ({PRELOAD_SNUG:.0f} N): washer bearing on the floor",
          PRELOAD_SNUG / (math.pi / 4 * (WASHER_D ** 2 - CLAMP_HOLE ** 2)), False, SF_STATIC)


def pocket_half_w(x):
    """Half width of the single-arm horn pocket at distance x along the arm (hobby_parts.horn_pocket_cutter)."""
    s = SERVO
    c = 0.5 + HOLE_COMP
    rh, rt = (s.horn_d + c) / 2, (s.horn_tip_d + c) / 2
    if x < 0:
        return math.sqrt(max(rh * rh - x * x, 0.0))
    if x <= s.horn_arm_len:
        return rh - (rh - rt) * x / s.horn_arm_len
    return math.sqrt(max(rt * rt - (x - s.horn_arm_len) ** 2, 0.0))


def section(rects):
    """rects: (u0, u1, v0, v1) rectangles (negative area allowed as (u0, u1, v0, v1, -1)). Returns A, uc, vc,
    Iu (= integral (u-uc)^2, stress varying along u), Iv (= integral (v-vc)^2)."""
    A = Su = Sv = Iu0 = Iv0 = 0.0
    for r in rects:
        u0, u1, v0, v1 = r[:4]; sg = r[4] if len(r) > 4 else 1.0
        b, h = u1 - u0, v1 - v0; a = sg * b * h; uc, vc = (u0 + u1) / 2, (v0 + v1) / 2
        A += a; Su += a * uc; Sv += a * vc
        Iu0 += sg * (h * b ** 3 / 12) + a * uc * uc; Iv0 += sg * (b * h ** 3 / 12) + a * vc * vc
    uc, vc = Su / A, Sv / A
    return A, uc, vc, Iu0 - A * uc * uc, Iv0 - A * vc * vc


def alpha_rect(b_over_t):
    """tau_max = T / (alpha b t^2) for a solid rectangle (Roark)."""
    tab = [(1, 0.208), (1.5, 0.231), (2, 0.246), (2.5, 0.258), (3, 0.267), (4, 0.282), (5, 0.291), (6, 0.299),
           (10, 0.312), (1e9, 0.333)]
    r = max(b_over_t, 1.0)
    for (r0, a0), (r1, a1) in zip(tab, tab[1:]):
        if r <= r1:
            return a0 + (a1 - a0) * (r - r0) / (r1 - r0)
    return 0.333


def pullout(F, d, L):
    return F / (math.pi * d * L)


def servo_torque_table():
    """Static servo torques (N.mm) per foot load, and what the gait and the pose do to them."""
    rows = []
    for lab, f in ((f"neutral stance, 6 feet ({F_STAND6:.2f} N)", foot_force_C(0, 0, F_STAND6)),
                   (f"neutral stance, tripod ({SHARE0 * W_N:.2f} N)", foot_force_C(0, 0, SHARE0 * W_N)),
                   (f"walking pose, gait +-{SW_GAIT} deg ({F_SUST:.2f} N)", foot_force_C(0, 0, F_SUST)),
                   (f"walking pose, MAX_COXA +-{SW_MAX} deg ({SHARE_MAX * W_N:.2f} N)", foot_force_C(0, 0, SHARE_MAX * W_N)),
                   (f"walking pose + foot scrub mu {MU} outward ({F_SUST:.2f} N)", foot_force_C(MU * F_SUST, 0, F_SUST)),
                   (f"walking pose x{DYN:.0f} dynamics ({F_WALK:.2f} N)", foot_force_C(0, 0, F_WALK))):
        rows.append((lab,) + tuple(abs(t) for t in joint_torques(f)))
    # same tripod load with the tibia turned inward so the foot is midway between the femur axis and the knee
    beta = math.degrees(math.asin(H.L_F / (2 * H.L_T)))
    f_mid = F_SUST * H.L_F / 2
    rows.append((f"tibia {beta:.1f} deg inward, foot midway ({F_SUST:.2f} N)", 0.0, f_mid, f_mid))
    return rows, beta, H.L_T * (1 - math.cos(math.radians(beta)))


def print_servo_table():
    rows, beta, drop_mm = servo_torque_table()
    print(f"\nservo torques (N.mm) against the MG90S stall {STALL:.0f} N.mm (6 V):")
    print("| pose / load | coxa | femur | knee | femur / stall |")
    print("|---|---|---|---|---|")
    for lab, tc, tf, tk in rows:
        print(f"| {lab} | {tc:.0f} | {tf:.0f} | {tk:.0f} | {tf / STALL:.0%} |")
    print(f"(tibia {beta:.1f} deg inward lowers the body {drop_mm:.1f} mm unless the femur is raised to match)")

# ==== 20261026-hexapod-tibia =====================================================================================
P = model("tibia")
s = SERVO
T = H.T_T
T_FLOOR = T - HORN_DEPTH
XF = H.L_T - P.FOOT_R
print(f"\ntibia: hub R{P.HUB_R} tapering to the R{P.FOOT_R} foot at x {H.L_T}; {T} thick; horn floor {T_FLOOR}")


def half_w(x):
    return P.HUB_R - (P.HUB_R - P.FOOT_R) * x / XF if x <= XF else math.sqrt(max(P.FOOT_R ** 2 - (x - XF) ** 2, 0.0))


def tib_stress(f, x, Kt=1.0):
    hw = half_w(x)
    rects = [(-hw, hw, 0.0, T)]
    if 0 <= x <= s.horn_arm_len + (s.horn_tip_d + 0.7) / 2:
        ph = pocket_half_w(x)
        rects.append((-ph, ph, 0.0, HORN_DEPTH, -1.0))
    A, uc, vc, Iu, Iv = section(rects)
    fl, m = at("T", (x, uc, vc), f)
    return Kt * (abs(fl[0]) / A + abs(m[2]) * hw / Iu + abs(m[1]) * max(vc, T - vc) / Iv)


def axial(f):
    return at("T", (0, 0, T / 2), f)[0][0]          # + = pulled toward the foot, - = compression


SECTIONS = [(4.0, 1.5, "x 4 over the horn hub (Kt 1.5 pocket edge)"), (13.0, 2.0, "x 13 over the pocket, arm-screw hole (Kt 2)"),
            (16.5, 1.0, "x 16.5 full section"), (35.0, 1.0, "x 35 mid-length"), (55.0, 1.0, "x 55 near the foot")]
check("knee stall 216 N.mm: horn-arm bearing on the pocket wall", horn_bearing_mpa(), False, SF_STATIC)
for key, lab, fs, req in LOAD_CASES:
    check_util(f"{lab}: knee horn clamp (O6 washer, {T_FLOOR:.0f} mm floor + arm screw)",
               worst_over(fs, lambda f: clamp_util(*at("T", (0, 0, HORN_DEPTH), f), T_FLOOR)), req)
for key, lab, fs, req in LOAD_CASES:
    best = max(((worst_over(fs, lambda f, x=x, k=k: tib_stress(f, x, k)), name) for x, k, name in SECTIONS))
    check(f"{lab}: tibia bending + axial, worst section ({best[1]})", best[0], False, req)
I_MIN = 2 * P.FOOT_R * T ** 3 / 12
P_CR = math.pi ** 2 * E_MPA * I_MIN / (2.0 * H.L_T) ** 2
for key, lab, fs, req in LOAD_CASES:
    if key in ("walk", "drop"):
        Fc = worst_over(fs, lambda f: -axial(f))
        check(f"{lab}: buckling, fixed-free (K 2) on the foot-end I {I_MIN:.0f} mm4: P_cr {P_CR:.0f} N vs {Fc:.1f} N",
              ALLOW_XY_MPA * Fc / P_CR, False, req)
preload_rows(T_FLOOR, "tibia")
# foot tip on a hard floor (Hertz line contact, R = FOOT_R, length = T less the bed chamfers): local flattening only
L_C = T - 2 * 0.4
E_STAR = E_MPA / (1 - 0.4 ** 2)
for key, lab, fs, req in LOAD_CASES:
    if key in ("walk", "drop"):
        Fn = worst_over(fs, lambda f: f[2] * -1)
        p = math.sqrt(Fn / L_C * E_STAR / (math.pi * P.FOOT_R))
        check(f"{lab}: foot-tip contact pressure on a hard floor (Hertz, R{P.FOOT_R} x {L_C:.1f})", p, False, req,
              info=True)

worst, fails = report(JOB["tibia"])
print_servo_table()


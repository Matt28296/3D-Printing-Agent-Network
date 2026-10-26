"""Strength check, round 2: jobs/20261026-arm-camera-mount (Brio 4K seat, lip and pad on the claw's top wall).

Run from the project root:  python3 jobs/20261026-arm-camera-mount/strength_calc.py
Plain python3: parameters come from claw_frame.py, this job's model.py and tools/hobby_parts.py (ast module).

The mount prints standing on its -y end (print Z = claw y): the side profile (pad, 34-degree seat, lip, root fillet) lies
in the bed plane, so seat and lip bending run along the layers (25 MPa); the mount as a beam along claw y bends across
them (12.5 MPa). Placeholder PETG allowables (no library row): NEEDS_TEST at best.
Camera frame (hobby_parts BRIO_4K): origin at the thread on the bottom face, +x lens, +y long axis, +z up; the body
spans x +-13.5, y +-51, z 0..27; tilted CAM_TILT nose-down about +y at (CAM_XC, CAM_ZC) in claw frame G.
"""
import ast
import math
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSY = ROOT / "jobs" / "20261025-robot-arm-assembly"
TOOLS = ROOT / "tools"

SAFE = {"__builtins__": {}, "math": math, "min": min, "max": max, "abs": abs, "round": round}


def _ev(node, env, src):
    return eval(compile(ast.Expression(node), src, "eval"), SAFE, env)


def hobby_specs():
    env, box = {}, ["name", "length", "width", "height", "mass_g", "note"]
    for node in ast.parse((TOOLS / "hobby_parts.py").read_text()).body:
        if not (isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)):
            continue
        name, v = node.targets[0].id, node.value
        try:
            fn = getattr(getattr(v, "func", None), "id", "")
            if fn in ("ServoSpec", "BoxSpec"):
                kw = {k.arg: _ev(k.value, env, "hobby_parts") for k in v.keywords}
                kw.update({f: _ev(a, env, "hobby_parts") for f, a in zip(box, v.args)})
                env[name] = SimpleNamespace(**kw)
            elif fn == "replace":
                d = dict(vars(env[v.args[0].id]))
                d.update({k.arg: _ev(k.value, env, "hobby_parts") for k in v.keywords})
                env[name] = SimpleNamespace(**d)
            else:
                env[name] = _ev(v, env, "hobby_parts")
        except Exception:
            pass
    return env


def consts(path, env):
    env = dict(env)
    for node in ast.parse(Path(path).read_text()).body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1):
            continue
        tgt = node.targets[0]
        try:
            val = _ev(node.value, env, str(path))
        except Exception:
            continue
        if isinstance(tgt, ast.Name):
            env[tgt.id] = val
        elif isinstance(tgt, ast.Tuple) and all(isinstance(e, ast.Name) for e in tgt.elts):
            env.update({e.id: v for e, v in zip(tgt.elts, val)})
    return env


HOBBY = hobby_specs()


def link_back_z(s, depth=HOBBY["HORN_DEPTH"]):
    return (s.total_h - s.tab_height) + 0.6 - depth


HOLE_COMP_DEFAULT = consts(TOOLS / "cadlib.py", {})["HOLE_COMP_DEFAULT"]
CF_ENV = consts(ASSY / "claw_frame.py", {**HOBBY, "link_back_z": link_back_z})
C = SimpleNamespace(**{k: v for k, v in CF_ENV.items() if k.isupper()})
P = SimpleNamespace(**{k: v for k, v in consts(HERE / "model.py", {**CF_ENV, "HOLE_COMP_DEFAULT": HOLE_COMP_DEFAULT}).items()
                       if k.isupper()})
BRIO = HOBBY["BRIO_4K"]
EDGE_R = HOBBY["BRIO_EDGE_R"]
D_SCREW = HOBBY["TRIPOD_SCREW_D"]

ALLOW_XY, ALLOW_Z = 25.0, 12.5
SHEAR_Z = 6.25
BEARING = 25.0
SF_SHORT, SF_CYCLIC = 3.0, 4.0
KT_FILLET, KT_SLOT = 1.5, 2.0
G = 9.81e-3

# ---------------------------------------------------------------- loads
F_TUG = 10.0                  # N, USB cable tug at the right-angle plug, any direction (spec)
Y_PORT = 45.0                 # port position on the camera's back: unmeasured (01 S5) -> anywhere within +-45
PLUG_BACK = 8.0               # cable exit of the right-angle plug, behind the camera's back face
F_CRASH = 13.0                # added: the Brio's end hits the desk (SYS-11: first contact in 37 % of crash poses)
CAM_G = BRIO.mass_g + 5.0     # camera + thumb screw
MOUNT_G = 13.3                # this part, solid PETG (CAD volume x 1.27)
HALF_D = BRIO.width / 2       # 13.5 (camera depth along its x)
XL = -HALF_D - C.LIP_CLR      # lip inner face, camera frame
Y0, Y1 = C.MOUNT_Y            # mount's y extent: -28 .. 22


def cam_to_g(cx, cz):
    a = math.radians(C.CAM_TILT)
    return C.CAM_XC + cx * math.cos(a) + cz * math.sin(a), C.CAM_ZC - cx * math.sin(a) + cz * math.cos(a)


ROWS, INFO = [], []


def row(case, sec, d, stress, allow, req, rows=ROWS):
    sf = allow / stress if stress > 1e-12 else float("inf")
    rows.append((case, sec, d, stress, allow, sf, req))
    return sf


# ================================================================ 1. lip: the tug twists the camera about the thumb screw
h_c = C.LIP_H                                   # the rounded (r 6) back edge meets the lip at its top: lever = lip height
PATCH = 2.0
for name, M_t in ((f"USB tug {F_TUG:.0f} N along the lens axis at a port {Y_PORT:.0f} mm off the centre", F_TUG * Y_PORT),
                  (f"USB tug {F_TUG:.0f} N along the camera at the plug ({HALF_D + PLUG_BACK:.1f} behind the screw)",
                   F_TUG * (HALF_D + PLUG_BACK))):
    for end, lever in (("+y end (22 from the screw)", Y1), ("-y end (28)", -Y0)):
        R = M_t / lever
        b = PATCH + h_c
        s = KT_FILLET * 6 * R * h_c / (b * C.LIP_T ** 2)
        row(f"{name}: twist {M_t:.0f} N.mm, the camera's back bears on the lip's {end} with {R:.1f} N",
            f"lip root, {C.LIP_T:.0f} thick, r {C.LIP_FILLET:.0f} fillet (Kt {KT_FILLET}), b_eff {b:.0f}, lever {h_c:.0f}",
            "XY", s, ALLOW_XY, SF_SHORT)

# ================================================================ 2. seat and thumb screw: the tug lifts one end of the camera
# camera pivots on the seat's far end (y Y0 or Y1); the thumb screw at y 0 holds it down
seat_len = (HALF_D - XL)                         # along the camera's x, from the lip face to the seat's front
for name, y_load in (("port at +45", Y_PORT), ("port at -45", -Y_PORT)):
    pivot = Y0 if y_load > 0 else Y1
    T = F_TUG * (y_load - pivot) / (0 - pivot)
    T = abs(T)
    head_d = 12.0                                  # knurled thumb-screw head, minimum assumed
    slot_w = D_SCREW + P.SCREW_CLR
    A_head = math.pi / 4 * head_d ** 2 - slot_w * head_d   # the slot under the head
    row(f"USB tug {F_TUG:.0f} N lifting the camera's end ({name}): thumb screw {T:.0f} N, head on the seat's underside",
        f"Ø{head_d:.0f} head over the Ø{slot_w:.2f} slot", "XY", T / A_head, BEARING, SF_SHORT)
    # seat as a plate across the slot: the head's ring load bends the seat between the slot's sides
    arm = (head_d - slot_w) / 2 / 2
    b = 2 * head_d
    s = KT_SLOT * 6 * (T / 2) * arm / (b * C.SEAT_T ** 2)
    row(f"same: the seat bends across the slot under the head ({name})", f"{C.SEAT_T:.0f} thick, Kt {KT_SLOT} (slot)",
        "XY", s, ALLOW_XY, SF_SHORT)
    # the seat cantilevers from the pad: the screw load at the camera thread, 13.5 from the seat front at the pad
    s_root = 6 * T * HALF_D / ((Y1 - Y0) * C.SEAT_T ** 2)
    row(f"same: seat root at the pad, the screw's {T:.0f} N at the thread ({name})", f"{Y1 - Y0:.0f} x {C.SEAT_T:.0f}, "
        f"lever {HALF_D:.1f}", "XY", s_root, ALLOW_XY, SF_SHORT)

# tug along the camera: the screw slides in its slot and bears on the slot's end
row(f"USB tug {F_TUG:.0f} N along the camera: thumb screw bears on the slot's end", f"Ø{D_SCREW} x {C.SEAT_T:.0f} seat",
    "XY", F_TUG / (D_SCREW * C.SEAT_T), BEARING, SF_SHORT)
lig = min(-Y0, Y1) - P.SLOT_HALF - (D_SCREW + P.SCREW_CLR + P.HOLE_COMP) / 2
row(f"same: slot-end tear-out towards the seat's end (ligament {lig:.1f}, planes y = const)", "interlayer shear",
    "Z shear", F_TUG / (2 * lig * C.SEAT_T), SHEAR_Z, SF_SHORT)

# ================================================================ 3. pad and screws: the tug tips the mount back over the cover's rear edge
cx_p, cz_p = -HALF_D - PLUG_BACK, BRIO.height / 2
xg, zg = cam_to_g(cx_p, cz_p)
M_tip = F_TUG * (zg - C.Z_TOP1)
x_screw = C.TOP_SCREWS[0][0]
T_screws = M_tip / (x_screw - C.PAD_X[0])
head_d = 5.7                                    # ISO 7380 M3 button head
A_pull = math.pi * head_d * (C.PAD_TOP - C.Z_TOP1)
row(f"USB tug {F_TUG:.0f} N along x at the plug (z {zg:.1f}): the mount tips on the cover's rear edge, M3 x 18 "
    f"screws {T_screws:.0f} N", f"button-head pull-through of the {C.PAD_TOP - C.Z_TOP1:.1f} pad (2 screws)", "Z shear",
    T_screws / 2 / A_pull, SHEAR_Z, SF_SHORT)
d_hole = C.M3_CLEAR + P.HOLE_COMP
row("USB tug along y: pad-hole bearing, both M3 shanks", f"Ø3 x {C.PAD_TOP - C.Z_TOP1:.1f} pad", "XY",
    F_TUG / 2 / (3.0 * (C.PAD_TOP - C.Z_TOP1)), BEARING, SF_SHORT)
# mount as a beam along y, across the layers: a tug along z at the camera's end, the mount held at its two pad screws
def profile():
    """Side profile (claw x, z) exactly as model.profile() draws it."""
    r = C.LIP_FILLET
    fil = [(XL + r - r * math.cos(t), r - r * math.sin(t)) for t in [k * (math.pi / 2) / 8 for k in range(9)]]
    sft = cam_to_g(HALF_D, 0.0)
    pts = [(C.PAD_X[1], C.Z_TOP1), (C.PAD_X[1], C.PAD_TOP), (sft[0] + 0.3, C.PAD_TOP), sft]
    pts += [cam_to_g(cx, cz) for cx, cz in reversed(fil)]
    pts += [cam_to_g(XL, C.LIP_H), cam_to_g(XL - C.LIP_T, C.LIP_H), cam_to_g(XL - C.LIP_T, -C.SEAT_T),
            cam_to_g(HALF_D, -C.SEAT_T), (C.PAD_X[0], C.Z_TOP1)]
    return pts


def poly_props(pts):
    """Area, centroid and centroidal second moments (int (z - zc)^2, int (x - xc)^2) of a simple polygon in (x, z)."""
    A = Sx = Sz = Ixx = Izz = 0.0
    for (x0, z0), (x1, z1) in zip(pts, pts[1:] + pts[:1]):
        c = x0 * z1 - x1 * z0
        A += c / 2
        Sx += (x0 + x1) * c / 6
        Sz += (z0 + z1) * c / 6
        Izz += (x0 * x0 + x0 * x1 + x1 * x1) * c / 12      # int x^2 (signed with A)
        Ixx += (z0 * z0 + z0 * z1 + z1 * z1) * c / 12      # int z^2
    xc, zc = Sx / A, Sz / A                                 # signs cancel for either winding
    s = 1.0 if A > 0 else -1.0
    A = abs(A)
    return A, xc, zc, s * Ixx - A * zc * zc, s * Izz - A * xc * xc


PRO = profile()
A_pro, xc_pro, zc_pro, Ixx_pro, Izz_pro = poly_props(PRO)
z_ext = max(abs(z - zc_pro) for _, z in PRO)
x_ext = max(abs(x - xc_pro) for x, _ in PRO)
# through the 1/4" slot: the seat loses the slot's width (7.05) over its 4 mm thickness at the thread
slot_w = D_SCREW + P.SCREW_CLR + P.HOLE_COMP
sx, sz = cam_to_g(0.0, -C.SEAT_T / 2)
A_s = slot_w * C.SEAT_T
Ixx_slot = Ixx_pro + A_pro * zc_pro ** 2 - (A_s * sz ** 2 + slot_w * C.SEAT_T ** 3 / 12)
zc_s = (A_pro * zc_pro - A_s * sz) / (A_pro - A_s)
Ixx_slot -= (A_pro - A_s) * zc_s ** 2
z_ext_s = max(abs(z - zc_s) for _, z in PRO)
ys1, ys2 = C.TOP_SCREWS[0][1], C.TOP_SCREWS[1][1]
M_scr = F_TUG * (Y_PORT - ys2)                              # at the +y screw: the camera's end load 31 beyond it
R1 = F_TUG * (Y_PORT - ys2) / (ys2 - ys1)                   # the -y screw's reaction
M_slot = R1 * (0 - ys1)                                     # at the thread (y 0), between the screws
row(f"USB tug {F_TUG:.0f} N along z at the port ({Y_PORT - ys2:.0f} beyond the +y screw): the mount bends along y, at the "
    f"+y screw", f"profile A {A_pro:.0f}, I {Ixx_pro:.0f} mm4, c {z_ext:.1f} (no slot there)", "Z",
    M_scr * z_ext / Ixx_pro, ALLOW_Z, SF_SHORT)
row(f"same, through the 1/4\" slot at the thread (y 0, M {M_slot:.0f} N.mm)", f"I {Ixx_slot:.0f} mm4, c {z_ext_s:.1f}, "
    f"slot Kt {KT_SLOT}", "Z", KT_SLOT * M_slot * z_ext_s / Ixx_slot, ALLOW_Z, SF_SHORT)

# ================================================================ 4. camera mass and inertia (cyclic), and the ramp check
alpha = math.radians(250.0)                      # firmware ACCEL, rad/s2 at every joint
omega = math.radians(66.7)                       # cruise
r_yaw, r_sh, r_el = 0.31, 0.27, 0.175            # m, camera from the yaw / shoulder / elbow axes, arm straight out
a_t = math.hypot(alpha * r_yaw, alpha * (r_sh + r_el))
a_c = omega ** 2 * r_yaw + omega ** 2 * r_sh + (2 * omega) ** 2 * r_el
dyn_g = 2.0 * (a_t + a_c) / 9.81                 # x2 for servo tracking overshoot at the ramp ends
INFO.append((f"info: 250 deg/s2 ramp: tangential {a_t:.2f} + centripetal {a_c:.2f} m/s2, x2 overshoot = {dyn_g:.2f} g "
             f"dynamic; the spec's x3 (1 g + 2 g) covers it", "-", "-", 0, 0, float("inf"), 0))
W3 = 3 * CAM_G * G
row(f"camera {CAM_G:.0f} g x3 along the lens axis into the lip (cyclic)", f"lip root, spread over {Y1 - Y0:.0f}", "XY",
    KT_FILLET * 6 * W3 * h_c / ((Y1 - Y0) * C.LIP_T ** 2), ALLOW_XY, SF_CYCLIC)
row(f"camera x3 across the seat (cyclic): seat root at the pad", f"{Y1 - Y0:.0f} x {C.SEAT_T:.0f}", "XY",
    6 * W3 * (HALF_D + 2.0) / ((Y1 - Y0) * C.SEAT_T ** 2), ALLOW_XY, SF_CYCLIC)

# ================================================================ 5. added: the Brio's end hits the desk (13 N along its long axis)
row(f"added: Brio's end hits the desk, {F_CRASH:.0f} N along y: screw slides {P.SLOT_HALF:.0f} mm, bears on the slot end",
    f"Ø{D_SCREW} x {C.SEAT_T:.0f}", "XY", F_CRASH / (D_SCREW * C.SEAT_T), BEARING, SF_SHORT)
row(f"same: slot-end tear-out (ligament {lig:.1f})", "interlayer shear", "Z shear", F_CRASH / (2 * lig * C.SEAT_T),
    SHEAR_Z, SF_SHORT)
M_x = F_CRASH * (cam_to_g(0.0, BRIO.height / 2)[1] - C.Z_TOP1)
dT = M_x / (C.TOP_SCREWS[1][1] - C.TOP_SCREWS[0][1])
row(f"same: the mount tips about x on its pad, {dT:.0f} N more on one M3", "button-head pull-through", "Z shear",
    dT / A_pull, SHEAR_Z, SF_SHORT)
# camera end lifted by the crash's moment about the lens axis: the thumb screw holds the other end down
T_c = F_CRASH * (BRIO.height / 2) / (BRIO.length / 2 + min(-Y0, Y1))
row(f"same: thumb screw tension {T_c:.1f} N (crash force {BRIO.height / 2:.1f} above the seat)", "head bearing", "XY",
    T_c / (math.pi / 4 * 12.0 ** 2 - (D_SCREW + P.SCREW_CLR) * 12.0), BEARING, SF_SHORT)


# ---------------------------------------------------------------- report
def table(rows, start=1):
    for i, (case, sec, d, s, a, sf, req) in enumerate(rows, start):
        ok = "" if not req else ("OK" if sf >= req else "**FAIL**")
        sf_s = "-" if sf == float("inf") else f"{sf:.2f}"
        print(f"| {i} | {case} | {sec} | {d} | {s:.2f} | {a:.2f} | {sf_s} | {req or '-'} | {ok} |")


print(f"mount: seat {C.SEAT_T}, lip {C.LIP_T} x {C.LIP_H} (r {C.LIP_FILLET}), pad x {C.PAD_X} z {C.Z_TOP1}..{C.PAD_TOP}, "
      f"y {C.MOUNT_Y}; camera {CAM_G:.0f} g at tilt {C.CAM_TILT}; plug exit G (x {xg:.1f}, z {zg:.1f})")
print("\n| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |")
print("|---|---|---|---|---|---|---|---|---|")
table(ROWS)
print("\nInformation rows:")
table(INFO, start=len(ROWS) + 1)
worst = min(ROWS, key=lambda r: r[5] / r[6])
print(f"\nlowest SF {worst[5]:.2f} (required {worst[6]:.0f}): {worst[0]} / {worst[1]}")
print("VERDICT (calculation):", "FAIL" if any(r[5] < r[6] for r in ROWS) else "NEEDS_TEST (placeholder allowables)")

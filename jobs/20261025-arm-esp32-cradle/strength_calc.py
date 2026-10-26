import math

# --- allowables -------------------------------------------------------------------
ALLOW_INPLANE_MPA = 25.0   # source: placeholder PETG (library/materials.csv has no measured row) -> verdict at best NEEDS_TEST
Z_RATIO = 0.5              # across-layer / in-plane; placeholder (skill: half the in-plane value)
SHEAR_RATIO = 0.5          # shear allowable = 0.5 x normal allowable (Tresca); assumption, stated in strength.md
SF_STATIC = 3.0            # short-term static
SF_SUSTAINED = 4.0         # sustained (creep) or cyclic
DYN = 2.0                  # dynamic factor on self-weight while the arm moves (as the spec uses)
G_N_PER_G = 9.81e-3        # N per gram
RHO_G_PER_MM3 = 1.27e-3    # PETG density

cases = []      # rows that set the verdict
advisory = []   # rows printed for information only (reason given in strength.md)


def allow_mpa(across, shear=False):
    a = ALLOW_INPLANE_MPA * (Z_RATIO if across else 1.0)
    return a * (SHEAR_RATIO if shear else 1.0)


def check(name, stress_mpa, across, sf_req, shear=False, Kt=1.0, info=False):
    """Record one check. across=True: the stress pulls layers apart (or shears them)."""
    s = Kt * stress_mpa
    a = allow_mpa(across, shear)
    sf = a / s if s > 1e-9 else float("inf")
    tag = ("Z" if across else "XY") + (" shear" if shear else "")
    (advisory if info else cases).append((name, tag, s, a, sf, sf_req))
    return sf


def bend(M_nmm, I_mm4, c_mm):
    return M_nmm * c_mm / I_mm4


def bearing(F_n, d_mm, t_mm):
    return F_n / (d_mm * t_mm)


def tearout(F_n, ligament_mm, t_mm):
    """Shear-out on two planes; ligament = edge distance minus hole radius."""
    return F_n / (2.0 * ligament_mm * t_mm)


def pullout(F_n, d_mm, L_mm):
    """Thread strip / pull-out of a self-tapping screw: shear on the pilot cylinder."""
    return F_n / (math.pi * d_mm * L_mm)


def torsion_thin(T_nmm, rects):
    """Open thin-walled section: J = sum b t^3/3 (1 - 0.63 t/b); tau_max = T t_max / J."""
    J = sum(b * t ** 3 / 3.0 * (1 - 0.63 * t / b) for b, t in rects)
    return T_nmm * max(t for _, t in rects) / J


def comp_section(rects):
    """rects: (width b along the neutral axis, depth d, centroid position y). Returns (A, ybar, I)."""
    A = sum(b * d for b, d, _ in rects)
    ybar = sum(b * d * y for b, d, y in rects) / A
    I = sum(b * d ** 3 / 12.0 + b * d * (y - ybar) ** 2 for b, d, y in rects)
    return A, ybar, I


def servo_screw_forces(T_nmm, holes):
    """Torque reacted by screws only (servo body bearing on the window ignored): F_i = T r_i / sum r^2."""
    r = [math.hypot(x, y) for x, y in holes]
    s = sum(ri ** 2 for ri in r)
    return [T_nmm * ri / s for ri in r]


def report(title):
    print(f"== {title} ==")
    print("| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |")
    print("|---|---|---|---|---|---|---|---|")
    for i, (n, d, s, a, sf, req) in enumerate(cases, 1):
        print(f"| {i} | {n} | {d} | {s:.2f} | {a:.2f} | {sf:.2f} | {req:.0f} | {'OK' if sf >= req else '**FAIL**'} |")
    if advisory:
        print("\nAdvisory (not in the verdict; see strength.md):")
        print("| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |")
        print("|---|---|---|---|---|---|")
        for n, d, s, a, sf, req in advisory:
            print(f"| {n} | {d} | {s:.2f} | {a:.2f} | {sf:.2f} | {req:.0f} |")
    worst = min(cases, key=lambda r: r[4] / r[5])
    fails = [r for r in cases if r[4] < r[5]]
    print(f"\nlowest SF {worst[4]:.2f} (required {worst[5]:.0f}) at: {worst[0]}")
    print("VERDICT:", "FAIL" if fails else "NEEDS_TEST (placeholder allowables; PASS not possible without measured data)")
    return worst, fails

# --- read the real parameters (model.py / tools/hobby_parts.py / geometry.json) ---------------------------
# model.py imports build123d, which plain python3 doesn't have, so its top-level constants are evaluated with
# ast against stand-ins for the hobby_parts names. Anything that can't be evaluated that way is skipped.
import ast
import json
import os
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
JOBS = os.path.join(ROOT, "jobs")
_SERVO_FIELDS = ["name", "length", "width", "case_top", "total_h", "tab_height", "tab_t", "tab_span", "hole_dx",
                 "hole_dy", "tab_hole_d", "screw_pilot_d", "shaft_from_end", "horn_kind", "horn_d", "horn_t"]
_SERVO_DEFAULTS = dict(horn_arm_len=0.0, horn_tip_d=0.0, horn_arms=1, horn_screw_clear_d=3.4, stall_torque_nmm=0.0,
                       mass_g=0.0)
_BOARD_FIELDS = ["name", "length", "width", "pcb_t", "pins_below", "parts_above", "usb_w", "usb_h"]


def _lit(node):
    return ast.literal_eval(node)


def _read_hobby():
    tree = ast.parse(open(os.path.join(ROOT, "tools", "hobby_parts.py")).read())
    ns = {}
    for node in tree.body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)):
            continue
        name, v = node.targets[0].id, node.value
        fn = getattr(getattr(v, "func", None), "id", "")
        if fn == "ServoSpec":
            d = dict(_SERVO_DEFAULTS)
            d.update(zip(_SERVO_FIELDS, [_lit(a) for a in v.args]))
            d.update({kw.arg: _lit(kw.value) for kw in v.keywords})
            ns[name] = SimpleNamespace(**d)
        elif fn == "BoardSpec":
            ns[name] = SimpleNamespace(**dict(zip(_BOARD_FIELDS, [_lit(a) for a in v.args])))
        elif fn == "replace":
            d = dict(vars(ns[v.args[0].id]))
            d.update({kw.arg: _lit(kw.value) for kw in v.keywords})
            ns[name] = SimpleNamespace(**d)
        else:
            try:
                ns[name] = _lit(v)
            except Exception:
                pass
    cad = ast.parse(open(os.path.join(ROOT, "tools", "cadlib.py")).read())
    for node in cad.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "HOLE_COMP_DEFAULT":
            ns["HOLE_COMP_DEFAULT"] = _lit(node.value)
    return ns


HOBBY = _read_hobby()
MG996R, SG90 = HOBBY["MG996R"], HOBBY["SG90"]
HORN_DEPTH = HOBBY.get("HORN_DEPTH", 2.0)


def horn_face_z(s):
    return (s.total_h - s.tab_height) + 0.6          # same formula as tools/hobby_parts.py


def link_back_z(s, depth=HORN_DEPTH):
    return horn_face_z(s) - depth


def model_params(job):
    """Top-level constants of jobs/<job>/model.py, evaluated in order."""
    ns = dict(HOBBY, math=math, horn_face_z=horn_face_z, link_back_z=link_back_z, max=max, min=min, abs=abs)
    base = set(ns)
    tree = ast.parse(open(os.path.join(JOBS, job, "model.py")).read())
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        try:
            val = eval(compile(ast.Expression(node.value), "model.py", "eval"), ns)
        except Exception:
            continue
        t = node.targets[0]
        if isinstance(t, ast.Name):
            ns[t.id] = val
        elif isinstance(t, ast.Tuple) and all(isinstance(e, ast.Name) for e in t.elts):
            for e, v in zip(t.elts, val):
                ns[e.id] = v
    return SimpleNamespace(**{k: v for k, v in ns.items() if k not in base and not k.startswith("__")})


def volume_mm3(job):
    return json.load(open(os.path.join(JOBS, job, "geometry.json")))["volume_mm3"]


HOLE_COMP = HOBBY["HOLE_COMP_DEFAULT"]

# --- 20261025-arm-esp32-cradle (round 2) -----------------------------------------------------------------
P = model_params("20261025-arm-esp32-cradle")
H_FRAME = P.TOP - P.BOT
LEDGE_H = P.PCB_BOT - P.BOT
CBORE = P.CBORE_D + HOLE_COMP
CLAMP_T = H_FRAME - P.CBORE_DEPTH
F_USB, F_JUMPER, BOARD_G = 20.0, 10.0, 10.0
F_end = F_JUMPER / 2
Y_IN0 = P.YC - P.HALF
STRIP_L = P.USB_LEDGE_Y1 - Y_IN0
PCB_Y0, PCB_Y1 = P.YC - max(b.width for b in P.BOARDS) / 2, min(P.YC + max(b.width for b in P.BOARDS) / 2, P.USB_LEDGE_Y1)
STRIP_ARM = (PCB_Y0 + PCB_Y1) / 2 - Y_IN0
FAR_FACE = P.FAR_X - P.CLR
print(f"frame {H_FRAME:.0f} tall, ledges {LEDGE_H:.1f} tall; USB-end strip {P.USB_LEDGE_W} x {LEDGE_H:.1f}, {STRIP_L:.2f} long,"
      f" load arm {STRIP_ARM:.2f}; screw clamp {CLAMP_T:.0f} mm under the head")

check(f"USB insertion {F_USB:.0f} N: PCB edge bearing on the far block (1.6 x 28)", F_USB / (1.6 * 28.0), False, SF_STATIC)
check("USB insertion: M3 shank bearing in the far-block holes (2 of 3, clamp length only)",
      bearing(F_USB / 2, 3.0, CLAMP_T), False, SF_STATIC)
lig = (FAR_FACE - P.SCREWS[0][0]) - CBORE / 2
check(f"USB insertion: far-block tear-out toward the pocket past the counterbore (ligament {lig:.2f})",
      tearout(F_USB / 2, lig, H_FRAME), False, SF_STATIC, shear=True)
check(f"USB insertion: counterbore wall to the far-block end (ligament {(P.SCREWS[0][0] - P.FAR_BLOCK_X0) - CBORE / 2:.2f})",
      tearout(F_USB / 2, (P.SCREWS[0][0] - P.FAR_BLOCK_X0) - CBORE / 2, P.CBORE_DEPTH), False, SF_STATIC, shear=True)
check(f"jumper pull: screw head through the {CLAMP_T:.0f} mm counterbore floor (head D5.5)",
      F_end / (math.pi * 5.5 * CLAMP_T), True, SF_STATIC, shear=True)
for lbl, F in (("spec 5 N pull", 2.5), (f"jumper pull {F_JUMPER:.0f} N", F_end), ("15 N proof (spec 8)", 7.5)):
    check(f"{lbl}, {F:.1f} N on the USB end: USB-end ledge strip, cantilever from the -Y wall (Kt 2.5)",
          F * STRIP_ARM / (P.USB_LEDGE_W * LEDGE_H ** 2 / 6), False, 1.5 if "proof" in lbl else SF_STATIC, Kt=2.5,
          info="proof" in lbl)
pad_edge = P.SCREWS[2][0] + P.PAD_R
lever = (P.USB_END_X - P.USB_LEDGE_W / 2) - pad_edge
check(f"jumper pull: -Y wall cantilever from the x40 pad (lever {lever:.1f}, Kt 2.5)",
      6 * F_end * lever / (P.WALL * H_FRAME ** 2), False, SF_STATIC, Kt=2.5)
check("jumper pull: far-ledge root on the far block (Kt 2.5)", 6 * F_end * 1.4 / (29.5 * LEDGE_H ** 2), False, SF_STATIC,
      Kt=2.5)
check("board weight x2 (sustained): USB-end ledge strip",
      DYN * BOARD_G * G_N_PER_G / 2 * STRIP_ARM / (P.USB_LEDGE_W * LEDGE_H ** 2 / 6), False, SF_SUSTAINED, Kt=2.5)
worst, fails = report("20261025-arm-esp32-cradle")
CR_SCREW = 10.0             # spec 2 / BUILD_GUIDE: 3 x M3x10 from below
BOSS_PILOT = 6.0            # base: blind cradle pilot, boss end Z -10 to the plate underside Z -4
print(f"FIT: M3x{CR_SCREW:.0f} from the counterbore floor leaves {CR_SCREW - CLAMP_T:.0f} mm beyond the cradle vs a {BOSS_PILOT:.0f} mm"
      f" pilot -> {'ok, fully engaged without bottoming' if CR_SCREW - CLAMP_T <= BOSS_PILOT else 'OVERRUN'}")

"""Strength check for jobs/20261026-rover-wheel (tracked rover, PETG), round 2. Run: python3 jobs/20261026-rover-wheel/strength_calc.py

Self-contained. model.py files import build123d, which plain python3 doesn't have, so this script reads the
top-level constants of rover_frame.py, tools/hobby_parts.py, tools/cadlib.py and the rover model.py files with
`ast`, and the part volumes from every rover geometry.json. Units: N, mm, MPa, g.

Round 2 = the round-1 method applied to the round-2 design: 5 cm design drop (spec §4; E = m g h, 5 mm stopping
distance, flat and corner landings), 2 mm steel track pins, sprocket hub running in a 6 mm wall journal, N20 in a
cradle (no face screws), M3 x 45 axle bolts, 4.5 mm walls. Rows tagged `drop` scale linearly with the drop height;
report() prints the height at which the first of them reaches its required SF.
"""
import ast
import json
import math
import os
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
JOBS = os.path.join(ROOT, "jobs")
ASM = os.path.join(JOBS, "20261026-rover-assembly")

# --- allowables (library/materials.csv has no measured rows) --------------------------------------------------
ALLOW_INPLANE_MPA = 25.0   # placeholder PETG, already knocked down (strength-checks skill) -> best verdict NEEDS_TEST
Z_RATIO = 0.5              # across-layer / in-plane (skill placeholder)
SHEAR_RATIO = 0.5          # shear allowable = 0.5 x normal allowable (Tresca); same convention as round 1
E_PETG_MPA = 1800.0        # skill placeholder
SF_STATIC = 3.0            # short-term static
SF_CYCLIC = 4.0            # cyclic or sustained (creep)
SF_METAL = 1.5             # bought steel, on yield, short-term (round-1 assumption)
SY_A2_70_MPA = 450.0       # A2-70 stainless M3: the spec names no grade, so the commonest hobby grade is assumed
SY_88_MPA = 640.0          # class 8.8 steel
SY_129_MPA = 1080.0        # class 12.9 steel
SY_STEEL_MPA = 350.0       # conservative yield for unspecified steel rod/shaft: the 2 mm track pins (annealed silver
                           # steel / drill rod ~400+, piano wire ~1500) and the N20 output shaft (round 1 used 450)
E_STEEL_MPA = 200000.0
RHO_G_PER_MM3 = 1.27e-3    # PETG; solid volume x density over-estimates infilled parts -> conservative mass
RHO_STEEL_G_PER_MM3 = 7.85e-3
G = 9.81                   # m/s^2

# --- read the real parameters ------------------------------------------------------------------------------------
_GM_FIELDS = ["name", "gb_w", "gb_h", "gb_len", "can_d", "can_flat", "can_len", "term_len", "shaft_d", "shaft_flat",
              "shaft_len", "boss_d", "boss_h", "face_hole_dx", "face_screw_d", "stall_torque_nmm", "mass_g"]
_BOX_FIELDS = ["name", "length", "width", "height", "mass_g", "note"]
_BOARD_FIELDS = ["name", "length", "width", "pcb_t", "pins_below", "parts_above", "usb_w", "usb_h"]


def _lit(node):
    return ast.literal_eval(node)


def _read_hobby():
    ns = {}
    for node in ast.parse(open(os.path.join(ROOT, "tools", "hobby_parts.py")).read()).body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)):
            continue
        name, v = node.targets[0].id, node.value
        fn = getattr(getattr(v, "func", None), "id", "")
        fields = {"GearMotorSpec": _GM_FIELDS, "BoxSpec": _BOX_FIELDS, "BoardSpec": _BOARD_FIELDS}.get(fn)
        try:
            if fields:
                d = dict(zip(fields, [_lit(a) for a in v.args]))
                d.update({kw.arg: _lit(kw.value) for kw in v.keywords})
                ns[name] = SimpleNamespace(**d)
            elif fn == "":
                ns[name] = _lit(v)
        except Exception:
            pass
    for node in ast.parse(open(os.path.join(ROOT, "tools", "cadlib.py")).read()).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "HOLE_COMP_DEFAULT":
            ns["HOLE_COMP_DEFAULT"] = _lit(node.value)
    return ns


def _eval_assigns(path, ns):
    """Evaluate every top-level `NAME = expr` / `A, B = expr` that only needs names already in ns."""
    for node in ast.parse(open(path).read()).body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1):
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
    return ns


HOBBY = _read_hobby()
FRAME = _eval_assigns(os.path.join(ASM, "rover_frame.py"), {"math": math, **HOBBY})


def model_params(job):
    ns = {"math": math, **HOBBY, **FRAME}
    return SimpleNamespace(**{k: v for k, v in _eval_assigns(os.path.join(JOBS, job, "model.py"), ns).items()
                              if not k.startswith("__")})


def geometry(job):
    return json.load(open(os.path.join(JOBS, job, "geometry.json")))


def print_req(job):
    return json.load(open(os.path.join(JOBS, job, "print_requirements.json")))


F = SimpleNamespace(**{k: v for k, v in FRAME.items() if not k.startswith("__") and k != "math"})
N20 = HOBBY["N20_100RPM"]
BATT = HOBBY["BATT_2X18650"]

# --- checks -------------------------------------------------------------------------------------------------------
cases = []      # rows that set the verdict: (name, dir, stress, allowable, SF, SF required, drop?)
advisory = []   # rows printed for information (what-ifs, bounds, fixes, bought parts); not in the verdict


def allow_mpa(across, shear=False):
    return ALLOW_INPLANE_MPA * (Z_RATIO if across else 1.0) * (SHEAR_RATIO if shear else 1.0)


def check(name, stress_mpa, across, sf_req, shear=False, Kt=1.0, info=False, drop=False):
    """Printed-PETG check. across=True when the stress pulls layers apart or shears along a layer interface."""
    s = Kt * stress_mpa
    a = allow_mpa(across, shear)
    sf = a / s if s > 1e-9 else float("inf")
    tag = ("Z" if across else "XY") + (" shear" if shear else "")
    (advisory if info else cases).append((name, tag, s, a, sf, sf_req, drop))
    return sf


def check_metal(name, stress_mpa, sy_mpa, sf_req=SF_METAL, info=False, drop=False):
    sf = sy_mpa / stress_mpa if stress_mpa > 1e-9 else float("inf")
    (advisory if info else cases).append((name, f"steel σy {sy_mpa:.0f}", stress_mpa, sy_mpa, sf, sf_req, drop))
    return sf


def check_custom(name, stress_mpa, allow, tag, sf_req, info=False, drop=False):
    sf = allow / stress_mpa if stress_mpa > 1e-9 else float("inf")
    (advisory if info else cases).append((name, tag, stress_mpa, allow, sf, sf_req, drop))
    return sf


def bend_rect(M, b, h):
    return 6.0 * M / (b * h * h)


def bend_round(M, d):
    return 32.0 * M / (math.pi * d ** 3)


def bearing(Fn, d, t):
    return Fn / (d * t)


def tearout(Fn, ligament, t):
    return Fn / (2.0 * ligament * t)


def plate_boss_moment_stress(M, a, t, Kt=1.0):
    """Wall/plate bending round a rigid boss of radius a carrying a moment M (Kirchhoff, rigid inclusion in a
    large plate): m_r,max = M / (2 pi a)  ->  sigma = Kt * 6 m / t^2."""
    m = M / (2.0 * math.pi * a)
    return Kt * 6.0 * m / (t * t)


def bef_beta(k, E, I):
    """Beam on elastic foundation: beta = (k / 4EI)^(1/4), k in N/mm per mm of length (N/mm^2)."""
    return (k / (4.0 * E * I)) ** 0.25


def section_modulus(D, removed, n=360):
    """Ø D disc minus the cells where removed(x, y) is True (grid integration). Bending stress along x (neutral
    axis parallel to y), worst fibre on either side: returns (Z = I / c_max, area, centroid x)."""
    h = D / n
    xs = []
    r2 = (D / 2) ** 2
    for i in range(n):
        x = -D / 2 + (i + 0.5) * h
        for j in range(n):
            y = -D / 2 + (j + 0.5) * h
            if x * x + y * y <= r2 and not removed(x, y):
                xs.append(x)
    xc = sum(xs) / len(xs)
    I = sum((x - xc) ** 2 for x in xs) * h * h
    c = max(max(xs) - xc, xc - min(xs)) + h / 2
    return I / c, len(xs) * h * h, xc


def report(title):
    print(f"\n== {title} ==")
    print("| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |")
    print("|---|---|---|---|---|---|---|---|")
    for i, (n, d, s, a, sf, req, _) in enumerate(cases, 1):
        print(f"| {i} | {n} | {d} | {s:.2f} | {a:.1f} | {sf:.2f} | {req:.1f} | {'OK' if sf >= req else '**FAIL**'} |")
    if advisory:
        print("\nAdvisory (not in the verdict: bounds, what-ifs, fixes, bought parts):")
        print("| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |")
        print("|---|---|---|---|---|---|---|")
        for n, d, s, a, sf, req, _ in advisory:
            print(f"| {n} | {d} | {s:.2f} | {a:.1f} | {sf:.2f} | {req:.1f} | {'OK' if sf >= req else 'no'} |")
    worst = min(cases, key=lambda r: r[4] / r[5])
    fails = [r for r in cases if r[4] < r[5]]
    print(f"\nlowest SF {worst[4]:.2f} (required {worst[5]:.1f}) at: {worst[0]}")
    drops = [r for r in cases if r[6]]
    if drops:
        lim = min(drops, key=lambda r: r[4] / r[5])
        print(f"drop rows scale with the height: all of them meet their SF up to a {H_DROP_MM * lim[4] / lim[5] / 10:.1f} cm"
              f" drop (design {H_DROP_MM / 10:.0f} cm), limited by: {lim[0]}")
    print(f"{len(fails)} of {len(cases)} verdict rows below their required SF")
    print("VERDICT:", "FAIL" if fails else "NEEDS_TEST (placeholder allowables; PASS not possible without measured data)")
    return worst, fails


# --- shared rover loads (round 2, re-derived; identical block in every rover strength_calc.py) ----------------------
ROVER_JOBS = {"chassis": ("20261026-rover-chassis", 1), "lid": ("20261026-rover-lid", 1),
              "sprocket": ("20261026-rover-sprocket", 2), "idler": ("20261026-rover-idler", 2),
              "wheel": ("20261026-rover-wheel", 4), "link": ("20261026-rover-track-link", F.N_LINKS * 2)}
ELECTRONICS_G = 40.0   # ESP32 + breadboard + TB6612 + buck + HC-SR04 + toggle switch + wiring (brief)
HARDWARE_G = 20.0      # assumption: 6 x M3x45 + nuts, nylocs, washers; 4 lid screws; 2 M2 set screws; zip ties
                       # (round 1's 25 g less its 68 filament pins). The steel pins are added from PIN_D below.
PIN_LEN_MM = 23.5      # spec §2: 2 mm steel rod cut 23.5 mm, one per link
T_STALL_PACK_NMM = 160.0          # N20 at the 7.4 V pack (design); 6 V datasheet value read from hobby_parts
V_FRESH, V_NOM = 8.4, 6.0         # fresh 2S pack vs rated voltage; stall torque ~ proportional to voltage
PWM_CAP = 0.8                     # test sketch caps PWM at 80 % (assembly plan)
T0_N = 5.0             # track pretension per run (round-1 assumption, now in spec §4); sustained
MU_LONG = 1.0          # longitudinal traction, grousers on carpet (conservative); caps the everyday track pull
MU_SIDE = 0.6          # skid-steer side friction (spec)
SPEC_SIDE_N = 3.0      # spec: 3 N per track on a flange (kept: larger than re-derived)
SPEC_DROP_FLAT_N, SPEC_DROP_CORNER_N = 14.0, 29.0   # spec §4 round 2 (from 0.58 kg), for comparison
H_DROP_MM = float(F.DROP_MM)      # 50: design drop onto a hard floor (spec §4; rover_frame.DROP_MM)
DELTA_STOP_MM = 5.0    # stopping distance (round-1 method). The computed elastic axle deflection is ~1 mm, so 5 mm
                       # is generous (non-conservative); DELTA_STIFF_MM shows the sensitivity
DELTA_STIFF_MM = 2.5   # advisory only: a stiffer landing doubles every drop load
N_AXLES = 8            # 2 sprockets + 2 idlers + 4 road wheels all sit on the bottom run (same axle height)


def rover_loads(verbose=True):
    parts_g = {}
    for k, (job, n) in ROVER_JOBS.items():
        parts_g[k] = geometry(job)["volume_mm3"] * RHO_G_PER_MM3 * n
    printed = sum(parts_g.values())
    pins_g = 2 * F.N_LINKS * math.pi / 4 * F.PIN_D ** 2 * PIN_LEN_MM * RHO_STEEL_G_PER_MM3
    m_g = printed + 2 * N20.mass_g + BATT.mass_g + ELECTRONICS_G + HARDWARE_G + pins_g
    W = m_g * 1e-3 * G
    T_stall_6v = N20.stall_torque_nmm
    T_fresh = T_stall_6v * V_FRESH / V_NOM
    T_cap = T_fresh * PWM_CAP
    F_stall = T_STALL_PACK_NMM / F.RP             # sprocket pull at stall
    F_trac = MU_LONG * W / 2.0                    # everyday pull, traction-limited
    T_tight_stall = T0_N + F_stall                # conservative (ignores slack-side relief)
    R_stall = T_tight_stall + T0_N                # sprocket radial: tight run + slack run (forward or reverse)
    R_idler_stall = 2 * T_tight_stall             # idler in reverse: both of its runs carry the tight tension (spec §4)
    T_tight_cyc = T0_N + F_trac
    R_cyc = T_tight_cyc + T0_N
    R_idler_cyc = 2 * T_tight_cyc
    R_sus = 2 * T0_N
    side_derived = MU_SIDE * W / 2.0
    # skid-steer spot-turn thrust per track (uniform pressure, contact length = axle span, track gauge 2*Y_T)
    F_turn = MU_SIDE * W * F.AXLE_DX / (4.0 * 2 * F.Y_T)

    def drop(H, delta):
        E = m_g * 1e-3 * G * H                    # N*mm
        Ftot = 2.0 * E / delta                    # linear-spring peak
        return SimpleNamespace(E=E, Ftot=Ftot, flat=Ftot / N_AXLES, corner=E / (2.0 * delta),  # m_eff = m/2 on 2 axles
                               a_g=2.0 * H / delta)
    dd, dst = drop(H_DROP_MM, DELTA_STOP_MM), drop(H_DROP_MM, DELTA_STIFF_MM)
    L = SimpleNamespace(parts_g=parts_g, printed_g=printed, pins_g=pins_g, m_g=m_g, W=W, T_stall_6v=T_stall_6v,
                        T_fresh=T_fresh, T_cap=T_cap, F_stall=F_stall, F_trac=F_trac, T_tight_stall=T_tight_stall,
                        R_stall=R_stall, R_idler_stall=R_idler_stall, T_tight_cyc=T_tight_cyc, R_cyc=R_cyc,
                        R_idler_cyc=R_idler_cyc, R_sus=R_sus, side_derived=side_derived,
                        side=max(SPEC_SIDE_N, side_derived), F_turn=F_turn, dd=dd, dst=dst)
    if verbose:
        print("== Shared rover loads (round 2, re-derived) ==")
        print("mass: " + ", ".join(f"{k} {v:.1f} g" for k, v in parts_g.items())
              + f"; printed {printed:.0f} g + 2 N20 {2 * N20.mass_g:.0f} g + battery {BATT.mass_g:.0f} g"
              f" + electronics {ELECTRONICS_G:.0f} g + hardware {HARDWARE_G:.0f} g + {2 * F.N_LINKS} steel pins"
              f" {pins_g:.0f} g = {m_g:.0f} g, W = {W:.2f} N (spec 0.58 kg / 5.7 N)")
        print(f"stall: {T_stall_6v:.0f} N*mm at 6 V, {T_STALL_PACK_NMM:.0f} at 7.4 V (design), {T_fresh:.0f} fresh pack"
              f" 100 % PWM, {T_cap:.0f} fresh pack at the 80 % cap -> sprocket pull {F_stall:.2f} N at RP {F.RP:.2f}")
        print(f"pretension T0 {T0_N:.1f} N (sustained); tight run at stall {T_tight_stall:.1f} N, everyday"
              f" {T_tight_cyc:.1f} N; radial on the sprocket: stall {R_stall:.1f}, cyclic {R_cyc:.1f}, sustained"
              f" {R_sus:.1f} N; on the idler (reverse: both runs tight): stall {R_idler_stall:.1f}, cyclic"
              f" {R_idler_cyc:.1f}, sustained {R_sus:.1f} N")
        print(f"everyday pull (traction-limited, mu {MU_LONG}) {F_trac:.2f} N/track; spot-turn thrust {F_turn:.2f} N/track;"
              f" side drag {side_derived:.2f} N/track derived, {SPEC_SIDE_N:.1f} N used")
        for tag, d in ((f"{H_DROP_MM / 10:.0f} cm, delta {DELTA_STOP_MM:.0f} (design)", dd),
                       (f"{H_DROP_MM / 10:.0f} cm, delta {DELTA_STIFF_MM} (sensitivity)", dst)):
            print(f"drop {tag}: E {d.E / 1000:.3f} J, peak {d.a_g:.0f} g, total {d.Ftot:.0f} N, per axle flat"
                  f" {d.flat:.1f} N, corner {d.corner:.1f} N (spec {SPEC_DROP_FLAT_N:.0f} / {SPEC_DROP_CORNER_N:.0f} N)")
    return L


# ==================================================================================================================
JOB = "20261026-rover-wheel"
L = rover_loads()
p = model_params(JOB)
ch = model_params("20261026-rover-chassis")
pr = print_req(JOB)["min"]
dd = L.dd

bore_cad = p.BORE + p.HOLE_COMP                     # 3.7 CAD, ~3.5 printed (0.5 mm running clearance), on M3 threads
d_bolt = 3.0
THREAD_F = 0.5
rim_w = 2 * p.RIM_HALF                              # 24.6 rim width = load length
h_half = p.RIM_HALF + p.CONE_RISE + p.FLANGE_FLAT   # 16.0
L_eff = THREAD_F * rim_w
perims, fill = pr["perimeters"], pr["fill_density"] / 100.0
shell_t = perims * 0.45


def infill_props(rho):
    """Gyroid infill as a cellular solid (Gibson-Ashby, bending-dominated): E ~ E_s rho^2, strength ~ s rho^1.5."""
    return E_PETG_MPA * rho ** 2, ALLOW_INPLANE_MPA * rho ** 1.5


E_inf, allow_inf = infill_props(fill)
depth_inf = p.RIM_R - bore_cad / 2 - 2 * shell_t    # infill between rim shell and bore shell
print(f"\nwheel: rim r {p.RIM_R:.2f} x {rim_w:.1f} wide; bore {bore_cad:.2f} CAD on M3 threads; {perims} perimeters"
      f" ({shell_t:.2f} mm), {fill * 100:.0f} % gyroid: E_inf {E_inf:.0f} MPa, crush allowable {allow_inf:.2f} MPa"
      f" (cellular-solid scaling, assumption), infill depth {depth_inf:.2f}")


def rim_shell(Fn, t_shell, rho):
    """Rim shell (perimeters, hoop-wise continuous) on an infill foundation, line load q = F / rim width.
    Infinite beam on elastic foundation, point load: M_max = q / (4 beta), p_max = q beta / 2."""
    Ei, ai = infill_props(rho)
    k = Ei / depth_inf                               # N/mm^3 per unit rim width
    I = t_shell ** 3 / 12
    b = bef_beta(k, E_PETG_MPA, I)
    q = Fn / rim_w
    return bend_rect(q / (4 * b), 1.0, t_shell), q * b / 2, ai


def checks(label, Fn, sf, info=False, t_shell=shell_t, rho=fill, drop=False):
    s_b, p_inf, ai = rim_shell(Fn, t_shell, rho)
    check(f"rim shell hoop bending (perimeters), {label} {Fn:.1f} N", s_b, False, sf, info=info, drop=drop)
    check_custom(f"rim shell -> infill crush, {label}", p_inf, ai, f"infill {rho * 100:.0f}%", sf, info=info, drop=drop)
    ring_od = bore_cad + 2 * t_shell
    check_custom(f"bore shell -> infill crush, {label}", Fn / (ring_od * rim_w), ai, f"infill {rho * 100:.0f}%", sf,
                 info=info, drop=drop)
    check(f"bore bearing on M3 threads, {label}", bearing(Fn, d_bolt, L_eff), False, sf, info=info, drop=drop)


checks("5 cm flat", dd.flat, SF_STATIC, drop=True)
checks("5 cm corner", dd.corner, SF_STATIC, drop=True)
checks("weight share (sustained)", L.W / N_AXLES * 2, SF_CYCLIC)     # x2: uneven sharing
# skid-steer side drag: track edge on the 45 deg cone; flange root ring section (axial thickness CONE_RISE+FLANGE_FLAT)
t_fl = p.CONE_RISE + p.FLANGE_FLAT
arc = 10.0                                          # contact arc on the flange (assumption)
check(f"V-flange root bending, side {L.side:.0f} N on the cone (radial stress, XY)",
      bend_rect(L.side * p.CONE_RISE / 2, arc, t_fl), False, SF_CYCLIC)
A_end = math.pi / 4 * ((2 * p.HUB_R) ** 2 - bore_cad ** 2)
check(f"hub end-face bearing on the wall nut, side {L.side:.0f} N", L.side / A_end, False, SF_CYCLIC)

# advisory
checks(f"5 cm corner, stiff landing delta {DELTA_STIFF_MM}", L.dst.corner, SF_STATIC, info=True)
checks("spec §8 proof (wheel on the bolt, 3 kg)", 3.0 * G, 1.0, info=True)
# the bolt (chassis-owned)
d3 = 2.387
arm = F.Y_T - F.HALF_W_OUT
for lab, Fb, sy in (("5 cm flat", dd.flat, SY_A2_70_MPA), ("5 cm corner", dd.corner, SY_A2_70_MPA),
                    ("5 cm corner", dd.corner, SY_88_MPA)):
    check_metal(f"M3 bolt bending at wall face, {lab} {Fb:.1f} N x {arm:.0f}", bend_round(Fb * arm, d3), sy, info=True)
# bolt length: head on the boss's inner face, nut flush in the outer face; washer + nyloc outboard of the wheel
y_head = F.HALF_W_OUT - F.WALL - ch.BOSS_IN
y_wheel_out = F.Y_T + h_half
need = y_wheel_out + 0.5 + 4.0 + 0.5 - y_head        # washer 0.5, nyloc 4.0, 1 thread out
print(f"bolt length: head at Y {y_head:.1f}, wheel outer face Y {y_wheel_out:.1f} -> needs >= {need:.1f} mm;"
      f" M3x45 ends at Y {y_head + 45:.1f} ({'OK' if 45 >= need else 'TOO SHORT'})")

report(f"{JOB} strength checks")

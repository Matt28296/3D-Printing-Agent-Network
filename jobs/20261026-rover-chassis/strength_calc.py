"""Strength check for jobs/20261026-rover-chassis (tracked rover, PETG), round 2. Run: python3 jobs/20261026-rover-chassis/strength_calc.py

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
JOB = "20261026-rover-chassis"
L = rover_loads()
p = model_params(JOB)
wh = model_params("20261026-rover-wheel")
M = N20

# --- geometry from model.py / rover_frame.py ------------------------------------------------------------------------
t_w = F.WALL                                           # 4.5
y_mid = F.HALF_W_OUT - t_w / 2                         # wall mid-plane 35.75
arm_w = F.Y_T - y_mid                                  # wheel load line (track centre) to the wall mid-plane 19.25
arm_bolt = F.Y_T - F.HALF_W_OUT                        # bolt leaves the nut at the outer face: 17
d3 = 2.387                                             # M3 minor diameter (fully threaded: the nut sits at the wall)
a_road = p.ROAD_BOSS_R                                 # Ø20 road-wheel boss (round top, block down to the floor)
xi1 = F.X_FRONT_OUT - t_w                              # front wall inner face 130.5
bl = min(F.AXLE_DX + p.IDLER_BLOCK[0] / 2, xi1) - (F.AXLE_DX - p.IDLER_BLOCK[0] / 2)   # 25.5: block runs into the front wall
bh = p.IDLER_BLOCK[1]
a_idler = math.sqrt(bl * bh / math.pi)                 # equivalent radius; front-wall junction ignored (conservative)
y_nut = F.HALF_W_OUT - p.NUT_DEPTH / 2                 # nut centre 36.7
y_in = F.HALF_W_OUT - t_w - p.BOSS_IN + 0.75           # bolt bears on the inner hole edge 32.75
nut_m = 2.4                                            # M3 nut thickness
inner_span = 2 * (F.HALF_W_OUT - t_w)                  # floor span between the side walls 67
# sprocket journal + N20 cradle (round 2)
L_j = t_w + F.JOURNAL_BOSS                             # 6 mm journal
d_j = F.HUB_D + p.JOURNAL_CLR                          # 10.5 printed
y_j_out = F.HALF_W_OUT                                 # 38: journal outer end, where the tilting hub bears
y_j_mid = F.HALF_W_OUT - L_j / 2                       # 35
y_face = F.MOTOR_FACE_Y                                # 31.5
y_can_end = y_face - M.gb_len - M.can_len              # 7.0
k_lev = (F.Y_T - y_j_out) / (y_j_out - y_can_end)      # 0.548: can-end reaction per N of sprocket load
cz = F.Z_A - M.gb_h / 2                                # cradle top = gearbox/can underside
cheek_root = p.CRADLE_HALF_X - (M.gb_w / 2 + 0.3)      # 0.7: part of the 2 mm cheek that sits on the cradle
L_cheek = (F.HALF_W_OUT - t_w - p.BOSS_IN) - y_can_end # 25: cheek length, journal boss -> can end
h_cheek = F.Z_A + p.CHEEK_TOP - cz                     # 8: cheek height above the cradle top
h_load = F.Z_A - cz                                    # 5: the can's widest point above the cradle top
flat_w = 2 * math.sqrt((M.can_d / 2) ** 2 - (M.can_flat / 2) ** 2)   # can's bottom flat width 6.6
print(f"\nchassis: wall {t_w}, boss Ø{2 * a_road:.0f} x {p.BOSS_IN} (to the floor), wheel load {arm_w:.2f} from the wall"
      f" mid-plane, idler block {bl:.1f} x {bh:.0f} (a_eq {a_idler:.1f}), nut lever {y_nut - y_in:.2f} mm; journal Ø{d_j}"
      f" x {L_j:.0f}; N20 can end at Y {y_can_end:.1f} -> lever k {k_lev:.3f}; cheeks {p.CHEEK_T} thick, {h_cheek:.0f} tall,"
      f" {L_cheek:.0f} long, only {cheek_root:.1f} mm on the cradle (CRADLE_HALF_X {p.CRADLE_HALF_X} vs cheek"
      f" x {M.gb_w / 2 + 0.3:.1f}..{M.gb_w / 2 + 0.3 + p.CHEEK_T:.1f}); floor {F.FLOOR_T} over {inner_span:.0f}")
print("wall stresses: plate bending round a rigid boss, m = M/(2 pi a), sigma = Kt 6m/t^2; a vertical load gives a moment"
      " about X -> vertical stress in the wall = ACROSS layers (Z); a horizontal (track) load gives a moment about Z ->"
      " horizontal stress = in-plane (XY)")
print(f"journal lever: hub load R at Y {F.Y_T:.0f}, fulcrum at the journal outer end Y {y_j_out:.0f}, the N20 body the"
      f" other arm: journal {1 + k_lev:.3f} R, can end {k_lev:.3f} R (cradle floor for a drop, cheek for track pull)")


def boss_Z(Fv, a=a_road, t=t_w, Kt=2.0, arm=arm_w):
    return plate_boss_moment_stress(Fv * arm, a, t, Kt)


def nut_bearing(Fv, yin=y_in):
    """No preload (creeps out of PETG): bolt couple between the trapped nut and the inner hole edge."""
    return Fv * (F.Y_T - yin) / (y_nut - yin) / (nut_m * p.NUT_AF)


def journal_bearing(R):
    """Hub load R on the track plane; the hub tilts about the cradle-supported N20 and bears at the journal's outer
    end: R_j = (1 + k) R, triangular over the journal length -> peak = 2 x mean (in-plane compression)."""
    Rj = (1 + k_lev) * R
    return 2 * Rj / (F.HUB_D * L_j), Rj


def cheek_as_built(Rc):
    """Cheek as modelled: its bottom sits on the cradle over only 0.7 mm, so its real support is the front end on the
    journal boss: a cantilever L_cheek long, h_cheek tall, CHEEK_T thick, loaded by the can end. Stress along Y = XY."""
    return bend_rect(Rc * L_cheek, h_cheek, p.CHEEK_T)


def cheek_on_cradle(Rc, t, Kt=2.0):
    """Cheek standing fully on the cradle: cantilever up from its root, load at the can's widest point (h_load),
    spread over b_eff = 2 h_load; vertical stress = across layers; sharp root Kt 2."""
    return Kt * bend_rect(Rc * h_load, 2 * h_load, t)


def floor(F_batt, slot_y=p.STRAP_Y, t=F.FLOOR_T):
    """Battery inertia on the floor: one-way strip across the span, simply supported on the side walls, load spread
    over the holder width; strip width = holder length. At the strap slot the strip loses STRAP_L."""
    c = BATT.width
    M_c = F_batt / 2 * (inner_span / 2 - c / 4)
    s_c = bend_rect(M_c / BATT.length, 1.0, t)
    M_s = F_batt / 2 * (inner_span / 2 - slot_y)
    s_s = bend_rect(M_s / (BATT.length - p.STRAP_L), 1.0, t)
    return s_c, s_s


mb = BATT.mass_g * 1e-3 * G
dd = L.dd
# --- A. road-wheel bolt: Ø20 boss on the 4.5 mm wall, nut trap, M3 bolt ------------------------------------------------
check(f"road-wheel boss rim, wall bending, 5 cm flat {dd.flat:.1f} N (Kt 2 sharp step)", boss_Z(dd.flat), True, SF_STATIC,
      drop=True)
check(f"road-wheel boss rim, wall bending, 5 cm corner {dd.corner:.1f} N (Kt 2)", boss_Z(dd.corner), True, SF_STATIC,
      drop=True)
check(f"road-wheel boss rim, weight share x2 sustained {L.W / 4:.1f} N", boss_Z(L.W / 4), True, SF_CYCLIC)
check(f"road-wheel boss rim, side drag {L.side:.0f} N at flange r{wh.RIM_R + wh.CONE_RISE:.1f} (moment about X)",
      plate_boss_moment_stress(L.side * (wh.RIM_R + wh.CONE_RISE), a_road, t_w, 2.0), True, SF_CYCLIC)
check("nut / hole-edge bearing (wheel traps and idler slot), no preload, 5 cm flat", nut_bearing(dd.flat), False,
      SF_STATIC, drop=True)
check("nut / hole-edge bearing, 5 cm corner", nut_bearing(dd.corner), False, SF_STATIC, drop=True)
check_metal(f"M3 bolt (A2-70; no grade in the spec) bending at the wall, 5 cm flat x {arm_bolt:.0f}",
            bend_round(dd.flat * arm_bolt, d3), SY_A2_70_MPA, drop=True)
check_metal("M3 bolt (A2-70) bending at the wall, 5 cm corner (road wheel or idler)", bend_round(dd.corner * arm_bolt, d3),
            SY_A2_70_MPA, drop=True)
# --- B. idler block, bolt and slot clamp --------------------------------------------------------------------------------
check(f"idler block, reverse stall R {L.R_idler_stall:.1f} N (in-plane, Kt 2)",
      plate_boss_moment_stress(L.R_idler_stall * arm_w, a_idler, t_w, 2.0), False, SF_STATIC)
check(f"idler block, cyclic R {L.R_idler_cyc:.1f} N", plate_boss_moment_stress(L.R_idler_cyc * arm_w, a_idler, t_w, 2.0),
      False, SF_CYCLIC)
check(f"idler block, pretension sustained R {L.R_sus:.0f} N", plate_boss_moment_stress(L.R_sus * arm_w, a_idler, t_w, 2.0),
      False, SF_CYCLIC)
check(f"idler block, 5 cm front corner {dd.corner:.1f} N (Z, Kt 2)", boss_Z(dd.corner, a=a_idler), True, SF_STATIC,
      drop=True)
check_metal(f"idler M3 bolt (A2-70) bending, reverse stall R {L.R_idler_stall:.1f} N x {arm_bolt:.0f}",
            bend_round(L.R_idler_stall * arm_bolt, d3), SY_A2_70_MPA)
P_after, mu_cl = 100.0, 0.2                            # clamp left after PETG creep (assumption), PETG on steel
cap = 2 * mu_cl * P_after                              # head face + nut face
check_custom(f"idler slot clamp friction (P {P_after:.0f} N after creep, mu {mu_cl}, 2 faces) vs reverse stall R",
             L.R_idler_stall, cap, "friction N", SF_STATIC)
check_custom("idler slot clamp friction vs pretension 2 T0 (sustained)", L.R_sus, cap, "friction N", SF_CYCLIC)
# --- C. sprocket journal and N20 cradle (round 2) -----------------------------------------------------------------------
for lab, R, sf in (("stall", L.R_stall, SF_STATIC), ("pretension sustained", L.R_sus, SF_CYCLIC)):
    s, Rj = journal_bearing(R)
    check(f"journal bearing, {lab} (hub {R:.1f} N -> journal {Rj:.1f} N at its outer end)", s, False, sf)
s, Rj_dr = journal_bearing(dd.corner)
check(f"journal bearing, 5 cm rear corner on the sprocket (journal {Rj_dr:.0f} N)", s, False, SF_STATIC, drop=True)
a_jb = math.sqrt(2 * p.JOURNAL_BOSS_HALF * (F.Z_A + 10 - (F.FLOOR_Z + F.FLOOR_T)) / math.pi)   # 20 x 19.5 boss block
check(f"wall round the journal, bearing {y_j_out - y_j_mid:.0f} mm off its mid-plane, 5 cm corner (Z, Kt 2)",
      plate_boss_moment_stress(Rj_dr * (y_j_out - y_j_mid), a_jb, t_w, 2.0), True, SF_STATIC, drop=True)
Rc_st, Rc_sus, Rc_dr = k_lev * L.R_stall, k_lev * L.R_sus, k_lev * dd.corner
check(f"N20 cradle cheek as built (front end only), stall: can end {Rc_st:.1f} N", cheek_as_built(Rc_st), False, SF_STATIC)
check(f"N20 cradle cheek as built, pretension sustained: can end {Rc_sus:.1f} N", cheek_as_built(Rc_sus), False, SF_CYCLIC)
check(f"cradle top under the N20 can end, 5 cm rear corner ({Rc_dr:.1f} N, can flat {flat_w:.1f} x 3)",
      Rc_dr / (flat_w * 3.0), False, SF_STATIC, drop=True)
# --- D. floor under the battery -----------------------------------------------------------------------------------------
s_c, s_s = floor(mb * dd.a_g)
check(f"floor mid-span under battery, 5 cm ({dd.a_g:.0f} g x {BATT.mass_g:.0f} g)", s_c, False, SF_STATIC, drop=True)
check(f"floor at strap slot Y ±{p.STRAP_Y} (Kt 2.5 square ends), 5 cm", s_s, False, SF_STATIC, Kt=2.5, drop=True)
# --- E. handling: lifted by the lid, 2 x weight on 4 lid screws ---------------------------------------------------------
F_scr = 2 * L.W / 4
L_thr = 10.0 - 3.0
check(f"lid-screw pull-out of column pilot, handling {F_scr:.1f} N", F_scr / (math.pi * p.LID_PILOT * L_thr), False,
      SF_STATIC, shear=True)
A_col = math.pi / 4 * (p.COLUMN_D ** 2 - (p.LID_PILOT + p.HOLE_COMP) ** 2)
check("lid column tension (Z), handling", F_scr / A_col, True, SF_STATIC)

# --- advisory: bounds and sensitivity -------------------------------------------------------------------------------------
check(f"BOUND: strip model, boss block to the floor ({t_w + p.BOSS_IN:.0f} x {2 * a_road:.0f}, no Kt), 5 cm corner",
      bend_rect(dd.corner * arm_w, 2 * a_road, t_w + p.BOSS_IN), True, SF_STATIC, info=True)
check(f"road-wheel boss rim, 5 cm corner, stiff landing delta {DELTA_STIFF_MM} ({L.dst.corner:.0f} N)", boss_Z(L.dst.corner),
      True, SF_STATIC, info=True)
check(f"nut / hole-edge bearing at the spec's 29 N corner", nut_bearing(SPEC_DROP_CORNER_N), False, SF_STATIC, info=True)
check(f"cheek bottom edge as built ({cheek_root:.1f} mm on the cradle, Z, no Kt), stall", cheek_on_cradle(Rc_st, cheek_root, Kt=1.0),
      True, SF_STATIC, info=True)
P_need = SF_STATIC * L.R_idler_stall / (2 * mu_cl)
print(f"idler clamp: SF {SF_STATIC:.0f} on slip at the reverse stall needs {P_need:.0f} N of clamp left after creep"
      f" (head/nut bearing {P_need / (math.pi / 4 * (7.0 ** 2 - 3.6 ** 2)):.0f} MPa on a Ø7 washer: creeps away)")
# --- FIX rows: the smallest changes that pass (all advisory) ---------------------------------------------------------------
for a_f, kt_f, lab in ((10.0, 1.5, "Ø20 + r1.5 fillet only (DFM round-2 fix 3 alone)"),
                       (13.0, 1.5, "Ø26 + r1.5 fillet (or 2 x 45° chamfer) round the rim"), (15.0, 2.0, "Ø30, sharp rim")):
    check(f"FIX road-wheel boss {lab}: 5 cm corner", boss_Z(dd.corner, a=a_f, Kt=kt_f), True, SF_STATIC, info=True)
boss_fix = 5.5                                         # boss face at |y| 28.0; head moves in -> M3 x 50
y_in_fix = F.HALF_W_OUT - t_w - boss_fix + 0.75
check(f"FIX BOSS_IN {p.BOSS_IN} -> {boss_fix} at the wheel bosses and idler block: nut bearing, 5 cm corner",
      nut_bearing(dd.corner, yin=y_in_fix), False, SF_STATIC, info=True)
s_c26, s_s26 = floor(mb * dd.a_g, slot_y=26.0)
check("FIX strap slots Y ±27.5 -> ±26 (clear the thicker bosses): floor at slot, 5 cm", s_s26, False, SF_STATIC, Kt=2.5,
      info=True)
for sy, lab in ((SY_88_MPA, "8.8"), (SY_129_MPA, "12.9")):
    check_metal(f"FIX M3 class {lab} bolt, 5 cm corner {dd.corner:.1f} N x {arm_bolt:.0f}", bend_round(dd.corner * arm_bolt, d3),
                sy, info=True)
check_metal(f"FIX M3 class 8.8 idler bolt, reverse stall {L.R_idler_stall:.1f} N", bend_round(L.R_idler_stall * arm_bolt, d3),
            SY_88_MPA, info=True)
L_tens = (F.AXLE_DX - F.IDLER_SLOT) - (F.AXLE_DX - p.IDLER_BLOCK[0] / 2)   # 11: idler block behind the slot
check(f"FIX M3 tensioner screw along X through the idler block ({L_tens:.0f} mm thread, Ø2.6 pilot), reverse stall"
      " (thread shear, Z)", L.R_idler_stall / (math.pi * 3.0 * L_tens * 0.5), True, SF_STATIC, shear=True, info=True)
for t_f in (2.0, 3.0, 4.0):   # 2.0 = DFM round-2 fix 2 alone (CRADLE_HALF_X 8.3, cheek unchanged)
    check(f"FIX cheek {t_f:.0f} mm standing fully on the cradle (CRADLE_HALF_X >= {M.gb_w / 2 + 0.3 + t_f:.1f}), stall"
          " (Z, Kt 2)", cheek_on_cradle(Rc_st, t_f), True, SF_STATIC, info=True)
check("FIX cheek 4 mm on the cradle, pretension sustained", cheek_on_cradle(Rc_sus, 4.0), True, SF_CYCLIC, info=True)
# proof loads on the fixed geometry (should not break a good part: SF >= 1 on the knocked-down allowable)
F_proof = 5.0 * G
check(f"proof 5 kg ({F_proof:.0f} N) on the wheel rim: boss Ø26 r1.5", boss_Z(F_proof, a=13.0, Kt=1.5), True, 1.0, info=True)
check(f"proof 5 kg on the wheel rim: nut bearing, BOSS_IN {boss_fix}", nut_bearing(F_proof, yin=y_in_fix), False, 1.0,
      info=True)

report(f"{JOB} strength checks")

"""Strength check for jobs/20261026-rover-chassis (tracked rover, PETG). Run: python3 jobs/__JOB__/strength_calc.py

Self-contained. model.py files import build123d, which plain python3 doesn't have, so this script reads the
top-level constants of rover_frame.py, tools/hobby_parts.py, tools/cadlib.py and the rover model.py files with
`ast`, and the part volumes from every rover geometry.json. Units: N, mm, MPa, g.
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
SHEAR_RATIO = 0.5          # shear allowable = 0.5 x normal allowable (Tresca); same convention as earlier jobs
E_PETG_MPA = 1800.0        # skill placeholder
SF_STATIC = 3.0            # short-term static
SF_CYCLIC = 4.0            # cyclic or sustained (creep)
SF_METAL = 1.5             # bought steel hardware, on yield, short-term (assumption)
SY_A2_70_MPA = 450.0       # A2-70 stainless M3 screws (most common hobby grade; worst common case)
SY_88_MPA = 640.0          # class 8.8 steel (12.9 black screws: ~1100)
E_STEEL_MPA = 200000.0
RHO_G_PER_MM3 = 1.27e-3    # PETG
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
cases = []      # rows that set the verdict
advisory = []   # rows printed for information (what-ifs, bounds, bought parts); not in the verdict


def allow_mpa(across, shear=False):
    return ALLOW_INPLANE_MPA * (Z_RATIO if across else 1.0) * (SHEAR_RATIO if shear else 1.0)


def check(name, stress_mpa, across, sf_req, shear=False, Kt=1.0, info=False):
    """Printed-PETG check. across=True when the stress pulls layers apart or shears along a layer interface."""
    s = Kt * stress_mpa
    a = allow_mpa(across, shear)
    sf = a / s if s > 1e-9 else float("inf")
    tag = ("Z" if across else "XY") + (" shear" if shear else "")
    (advisory if info else cases).append((name, tag, s, a, sf, sf_req))
    return sf


def check_metal(name, stress_mpa, sy_mpa, sf_req=SF_METAL, info=False):
    sf = sy_mpa / stress_mpa if stress_mpa > 1e-9 else float("inf")
    (advisory if info else cases).append((name, f"steel σy {sy_mpa:.0f}", stress_mpa, sy_mpa, sf, sf_req))
    return sf


def check_custom(name, stress_mpa, allow, tag, sf_req, info=False):
    sf = allow / stress_mpa if stress_mpa > 1e-9 else float("inf")
    (advisory if info else cases).append((name, tag, stress_mpa, allow, sf, sf_req))
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


def report(title):
    print(f"\n== {title} ==")
    print("| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |")
    print("|---|---|---|---|---|---|---|---|")
    for i, (n, d, s, a, sf, req) in enumerate(cases, 1):
        print(f"| {i} | {n} | {d} | {s:.2f} | {a:.1f} | {sf:.2f} | {req:.1f} | {'OK' if sf >= req else '**FAIL**'} |")
    if advisory:
        print("\nAdvisory (not in the verdict: bounds, what-ifs, bought parts):")
        print("| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |")
        print("|---|---|---|---|---|---|---|")
        for n, d, s, a, sf, req in advisory:
            print(f"| {n} | {d} | {s:.2f} | {a:.1f} | {sf:.2f} | {req:.1f} | {'OK' if sf >= req else 'no'} |")
    worst = min(cases, key=lambda r: r[4] / r[5])
    fails = [r for r in cases if r[4] < r[5]]
    print(f"\nlowest SF {worst[4]:.2f} (required {worst[5]:.1f}) at: {worst[0]}")
    print("VERDICT:", "FAIL" if fails else "NEEDS_TEST (placeholder allowables; PASS not possible without measured data)")
    return worst, fails


# --- shared rover loads (re-derived; identical block in every rover strength_calc.py) ------------------------------
ROVER_JOBS = {"chassis": ("20261026-rover-chassis", 1), "lid": ("20261026-rover-lid", 1),
              "sprocket": ("20261026-rover-sprocket", 2), "idler": ("20261026-rover-idler", 2),
              "wheel": ("20261026-rover-wheel", 4), "link": ("20261026-rover-track-link", F.N_LINKS * 2)}
ELECTRONICS_G = 40.0   # ESP32 + breadboard + TB6612 + buck + HC-SR04 + switch + wiring (brief)
HARDWARE_G = 25.0      # assumption: 6 x M3x45 + nuts/nylocs/washers (~20 g), 4 lid screws, 68 filament pins
T_STALL_PACK_NMM = 160.0          # N20 at the 7.4 V pack (brief); 6 V datasheet value read from hobby_parts
V_FRESH, V_NOM = 8.4, 6.0         # fresh 2S pack vs rated voltage; stall torque ~ proportional to voltage
PWM_CAP = 0.8                     # test sketch caps PWM at 80 % (assembly plan)
T0_N = 5.0             # MISSED BY SPEC: track pretension per run, assumed ("firm hand" on the idler); sustained
MU_LONG = 1.0          # longitudinal traction, grousers on carpet (conservative); caps the everyday track pull
MU_SIDE = 0.6          # skid-steer side friction (spec)
SPEC_SIDE_N = 3.0      # spec: 3 N per track on a flange (kept: larger than re-derived)
SPEC_DROP_AXLE_N = 25.0
H_DROP_MM = 300.0      # spec: 30 cm drop onto a hard floor
DELTA_STOP_MM = 5.0    # assumed total stopping distance (tracks, clearances, bolts, walls). Computed elastic
                       # deflection of a road-wheel axle at these loads is ~1 mm, so 5 mm is generous (non-conservative)
DELTA_LB_MM = 10.0     # implausibly soft bound, to show the conclusion doesn't hinge on DELTA_STOP_MM
N_AXLES = 8            # 2 sprockets + 2 idlers + 4 road wheels all sit on the bottom run (same axle height)
H_RELAX_MM = 80.0      # recommended relaxed drop height (keeps the flat per-axle load at about the spec's 25 N)


def rover_loads(verbose=True):
    parts_g = {}
    for k, (job, n) in ROVER_JOBS.items():
        parts_g[k] = geometry(job)["volume_mm3"] * RHO_G_PER_MM3 * n
    printed = sum(parts_g.values())
    m_g = printed + 2 * N20.mass_g + BATT.mass_g + ELECTRONICS_G + HARDWARE_G
    W = m_g * 1e-3 * G
    T_stall_6v = N20.stall_torque_nmm
    T_fresh = T_stall_6v * V_FRESH / V_NOM
    T_cap = T_fresh * PWM_CAP
    F_stall = T_STALL_PACK_NMM / F.RP             # sprocket pull at stall
    F_trac = MU_LONG * W / 2.0                    # everyday pull, traction-limited
    T_tight_stall = T0_N + F_stall                # conservative (ignores slack-side relief)
    R_stall = T_tight_stall + T0_N                # radial on sprocket / idler (both runs leave forward/back)
    T_tight_cyc = T0_N + F_trac
    R_cyc = T_tight_cyc + T0_N
    R_sus = 2 * T0_N
    side_derived = MU_SIDE * W / 2.0
    # skid-steer spot-turn thrust per track (uniform pressure, contact length = axle span, track gauge 2*Y_T)
    F_turn = MU_SIDE * W * F.AXLE_DX / (4.0 * 2 * F.Y_T)

    def drop(H, delta):
        E = m_g * 1e-3 * G * H                    # N*mm
        Ftot = 2.0 * E / delta                    # linear-spring peak
        return SimpleNamespace(E=E, Ftot=Ftot, flat=Ftot / N_AXLES, corner=E / (2.0 * delta),  # m_eff = m/2 on 2 axles
                               a_g=2.0 * H / delta)
    d30, dlb, drel = drop(H_DROP_MM, DELTA_STOP_MM), drop(H_DROP_MM, DELTA_LB_MM), drop(H_RELAX_MM, DELTA_STOP_MM)
    L = SimpleNamespace(parts_g=parts_g, printed_g=printed, m_g=m_g, W=W, T_stall_6v=T_stall_6v, T_fresh=T_fresh,
                        T_cap=T_cap, F_stall=F_stall, F_trac=F_trac, T_tight_stall=T_tight_stall, R_stall=R_stall,
                        T_tight_cyc=T_tight_cyc, R_cyc=R_cyc, R_sus=R_sus, side_derived=side_derived,
                        side=max(SPEC_SIDE_N, side_derived), F_turn=F_turn, d30=d30, dlb=dlb, drel=drel)
    if verbose:
        print("== Shared rover loads (re-derived) ==")
        print("mass: " + ", ".join(f"{k} {v:.1f} g" for k, v in parts_g.items())
              + f"; printed {printed:.0f} g + 2 N20 {2 * N20.mass_g:.0f} g + battery {BATT.mass_g:.0f} g"
              f" + electronics {ELECTRONICS_G:.0f} g + hardware {HARDWARE_G:.0f} g = {m_g:.0f} g, W = {W:.2f} N"
              f" (spec 0.5 kg / 4.9 N)")
        print(f"stall: {T_stall_6v:.0f} N*mm at 6 V, {T_STALL_PACK_NMM:.0f} at 7.4 V (design), {T_fresh:.0f} fresh pack"
              f" 100 % PWM, {T_cap:.0f} fresh pack at the 80 % cap -> sprocket pull {F_stall:.2f} N at RP {F.RP:.2f}")
        print(f"pretension T0 {T0_N:.1f} N (assumed, sustained); tight run at stall {T_tight_stall:.1f} N;"
              f" sprocket/idler radial: stall {R_stall:.1f}, cyclic {R_cyc:.1f}, sustained {R_sus:.1f} N")
        print(f"everyday pull (traction-limited, mu {MU_LONG}) {F_trac:.2f} N/track; spot-turn thrust {F_turn:.2f} N/track;"
              f" side drag {side_derived:.2f} N/track derived, {SPEC_SIDE_N:.1f} N used")
        for tag, d, H, dl in (("30 cm, delta 5", d30, H_DROP_MM, DELTA_STOP_MM), ("30 cm, delta 10", dlb, H_DROP_MM, DELTA_LB_MM),
                              (f"{H_RELAX_MM / 10:.0f} cm, delta 5", drel, H_RELAX_MM, DELTA_STOP_MM)):
            print(f"drop {tag}: E {d.E / 1000:.2f} J, peak {d.a_g:.0f} g, total {d.Ftot:.0f} N, per axle flat"
                  f" {d.flat:.0f} N, corner {d.corner:.0f} N (spec {SPEC_DROP_AXLE_N:.0f} N)")
    return L


# ==================================================================================================================
JOB = "20261026-rover-chassis"
L = rover_loads()
p = model_params(JOB)
wh = model_params("20261026-rover-wheel")
M = N20

# --- geometry from model.py / rover_frame.py ------------------------------------------------------------------------
t_w = F.WALL
y_mid = F.HALF_W_OUT - t_w / 2                         # wall mid-plane 36.5
arm_w = F.Y_T - y_mid                                  # wheel load line (track centre) to the wall mid-plane 18.5
arm_bolt = F.Y_T - F.HALF_W_OUT                        # bolt exits the nut at the outer face: 17
d3 = 2.387                                             # M3 minor diameter (fully threaded: the nut sits at the wall)
bl, bh = p.IDLER_BOSS
a_idler = math.sqrt(bl * bh / math.pi)                 # equivalent radius of the 22 x 15 idler block
a_motor = math.sqrt(M.gb_w * M.gb_h / math.pi)         # gearbox face clamped on the wall
y_nut = F.HALF_W_OUT - p.NUT_DEPTH / 2                 # nut centre 36.7
y_in = F.HALF_W_OUT - t_w - p.BOSS_T + 0.75            # bolt bears on the inner hole edge
nut_m = 2.4                                            # M3 nut thickness
inner_span = 2 * (F.HALF_W_OUT - t_w)                  # floor span between side walls 70
y_strap = BATT.width / 2 + 0.5 + p.STRAP_W / 2         # strap slot centre 22.5
y_cradle = F.MOTOR_FACE_Y - M.gb_len - M.can_len / 2   # can centre on the cradle 18.25
print(f"\nchassis: wall {t_w}, boss R{p.BOSS_R} x {p.BOSS_T}, wheel load {arm_w:.1f} from the wall mid-plane,"
      f" idler block {bl}x{bh} (a_eq {a_idler:.1f}), gearbox patch a_eq {a_motor:.2f}, floor {F.FLOOR_T} over {inner_span:.0f}")
print("wall stresses: plate bending round a rigid boss, m = M/(2 pi a), sigma = Kt 6m/t^2; a vertical load gives a moment"
      " about X -> vertical stress in the wall = ACROSS layers (Z); a horizontal (track) load gives a moment about Z ->"
      " horizontal stress = in-plane (XY)")


def boss_Z(Fv, a=p.BOSS_R, t=t_w, Kt=2.0, arm=arm_w):
    return plate_boss_moment_stress(Fv * arm, a, t, Kt)


def nut_bearing(Fv, yin=y_in):
    """No preload (creeps out of PETG): bolt couple between the trapped nut and the inner hole edge."""
    return Fv * (F.Y_T - yin) / (y_nut - yin) / (nut_m * p.NUT_AF)


def motor_moment(R):
    return R * arm_w


def face_screw_T(R):
    """Prying about the gearbox's far edge: far screw at gb_w/2 + face_hole_dx/2."""
    return R * (F.Y_T - F.MOTOR_FACE_Y) / (M.gb_w / 2 + M.face_hole_dx / 2)


A_s16 = 1.27                                           # M1.6 stress area
d_scr_hole = M.face_screw_d + 0.4                      # printed clearance 2.0 (CAD 2.2)
A_head = math.pi / 4 * (3.0 ** 2 - d_scr_hole ** 2)    # M1.6 pan/cheese head Ø3.0


def face_screw_vertical(Fv):
    """Drop on the sprocket: motor pivots on the cradle under the can; the wall holds the gearbox end down
    through 2 x M1.6 bearing in their 3 mm-long holes (compression on the teardrop flanks)."""
    R_face = Fv * (F.Y_T - y_cradle) / (F.MOTOR_FACE_Y - y_cradle)
    return R_face / (2 * M.face_screw_d * t_w), R_face


def floor(F_batt, slot_y=y_strap, t=F.FLOOR_T):
    """Battery inertia on the floor: one-way strip across the 70 mm span, simply supported on the side walls,
    load spread over the holder width; strip width = holder length. At the strap slot the strip loses STRAP_L."""
    c = BATT.width
    M_c = F_batt / 2 * (inner_span / 2 - c / 4)
    s_c = bend_rect(M_c / BATT.length, 1.0, t)
    M_s = F_batt / 2 * (inner_span / 2 - slot_y)
    s_s = bend_rect(M_s / (BATT.length - p.STRAP_L), 1.0, t)
    return s_c, s_s


mb = BATT.mass_g * 1e-3 * G
# --- A. road-wheel bolt boss -------------------------------------------------------------------------------------------
check(f"road-wheel boss rim, wall bending, spec {SPEC_DROP_AXLE_N:.0f} N (Kt 2 sharp step)", boss_Z(SPEC_DROP_AXLE_N), True, SF_STATIC)
check(f"road-wheel boss rim, 30 cm flat {L.d30.flat:.0f} N", boss_Z(L.d30.flat), True, SF_STATIC)
check(f"road-wheel boss rim, weight share x2 sustained {L.W / 4:.1f} N", boss_Z(L.W / 4), True, SF_CYCLIC)
check(f"road-wheel boss rim, side drag {L.side:.0f} N at flange r16 (moment about X)",
      plate_boss_moment_stress(L.side * (wh.RIM_R + wh.CONE_RISE), p.BOSS_R, t_w, 2.0), True, SF_CYCLIC)
check(f"nut / hole-edge bearing, no preload, spec {SPEC_DROP_AXLE_N:.0f} N (compression)", nut_bearing(SPEC_DROP_AXLE_N), False, SF_STATIC)
check(f"nut / hole-edge bearing, 30 cm flat", nut_bearing(L.d30.flat), False, SF_STATIC)
check_metal(f"M3 bolt (A2-70, grade not in BOM) bending at wall, spec {SPEC_DROP_AXLE_N:.0f} N x {arm_bolt:.0f}",
            bend_round(SPEC_DROP_AXLE_N * arm_bolt, d3), SY_A2_70_MPA)
check_metal(f"M3 bolt bending at wall, 30 cm flat", bend_round(L.d30.flat * arm_bolt, d3), SY_A2_70_MPA)
# --- B. idler block ---------------------------------------------------------------------------------------------------------
check(f"idler block, track tension stall R {L.R_stall:.1f} N (in-plane, Kt 2)", plate_boss_moment_stress(motor_moment(L.R_stall), a_idler, t_w, 2.0), False, SF_STATIC)
check(f"idler block, cyclic R {L.R_cyc:.1f} N", plate_boss_moment_stress(motor_moment(L.R_cyc), a_idler, t_w, 2.0), False, SF_CYCLIC)
check(f"idler block, pretension sustained R {L.R_sus:.0f} N", plate_boss_moment_stress(motor_moment(L.R_sus), a_idler, t_w, 2.0), False, SF_CYCLIC)
check(f"idler block, 30 cm front corner {L.d30.corner:.0f} N (Z)", boss_Z(L.d30.corner, a=a_idler), True, SF_STATIC)
check_metal(f"idler M3 bolt bending, 30 cm corner", bend_round(L.d30.corner * arm_bolt, d3), SY_A2_70_MPA)
# --- C. N20 mount -------------------------------------------------------------------------------------------------------------
check_metal(f"M1.6 face screw tension (prying), stall R {L.R_stall:.1f} N", face_screw_T(L.R_stall) / A_s16, SY_A2_70_MPA)
check(f"M1.6 head bearing on wall, stall", face_screw_T(L.R_stall) / A_head, False, SF_STATIC)
check(f"M1.6 head bearing on wall, cyclic", face_screw_T(L.R_cyc) / A_head, False, SF_CYCLIC)
check(f"wall round gearbox face, stall (in-plane, Kt 2 screw holes)", plate_boss_moment_stress(motor_moment(L.R_stall), a_motor, t_w, 2.0), False, SF_STATIC)
check(f"wall round gearbox face, cyclic", plate_boss_moment_stress(motor_moment(L.R_cyc), a_motor, t_w, 2.0), False, SF_CYCLIC)
check(f"wall round gearbox face, pretension sustained", plate_boss_moment_stress(motor_moment(L.R_sus), a_motor, t_w, 2.0), False, SF_CYCLIC)
s_fv, Rf = face_screw_vertical(L.d30.corner)
check(f"M1.6 screws bearing in wall, 30 cm rear corner on sprocket ({Rf:.0f} N)", s_fv, False, SF_STATIC)
# --- D. floor under the battery -----------------------------------------------------------------------------------------------
s_c, s_s = floor(mb * L.d30.a_g)
check(f"floor mid-span under battery, 30 cm ({L.d30.a_g:.0f} g x {BATT.mass_g:.0f} g)", s_c, False, SF_STATIC)
check(f"floor at strap slot (Kt 2.5 square ends), 30 cm", s_s, False, SF_STATIC, Kt=2.5)
# --- E. handling: lifted by the lid, 2 x weight on 4 lid screws -----------------------------------------------------------------
F_scr = 2 * L.W / 4
L_thr = 10.0 - 3.0
check(f"lid-screw pull-out of column pilot, handling {F_scr:.1f} N", F_scr / (math.pi * p.LID_PILOT * L_thr), False, SF_STATIC, shear=True)
A_col = math.pi / 4 * (p.COLUMN_D ** 2 - (p.LID_PILOT + p.HOLE_COMP) ** 2)
check("lid column tension (Z), handling", F_scr / A_col, True, SF_STATIC)

# --- advisory -----------------------------------------------------------------------------------------------------------------------
check("BOUND: strip model, boss rim, spec 25 N (lower stub only, no Kt)", bend_rect(SPEC_DROP_AXLE_N * arm_w, 2 * p.BOSS_R, t_w), True, SF_STATIC, info=True)
check(f"road-wheel boss rim, 30 cm flat, delta 10 ({L.dlb.flat:.0f} N)", boss_Z(L.dlb.flat), True, SF_STATIC, info=True)
check(f"road-wheel boss rim, {H_RELAX_MM / 10:.0f} cm flat {L.drel.flat:.0f} N", boss_Z(L.drel.flat), True, SF_STATIC, info=True)
check("spec proof test: 2 kg hung 17 mm out (19.6 N), boss rim", boss_Z(19.6), True, 1.0, info=True)
# idler clamp (sustained): friction on head + nut faces must hold 2 T0; preload after PETG creep assumed 100 N
P_after = 100.0
check_custom(f"idler slot clamp friction (P {P_after:.0f} N after creep, mu 0.2, 2 faces) vs stall R", L.R_stall,
             2 * 0.2 * P_after, "friction N", SF_STATIC, info=True)
check_custom("idler slot clamp friction vs pretension (sustained)", L.R_sus, 2 * 0.2 * P_after, "friction N", SF_CYCLIC, info=True)
s_c8, s_s8 = floor(mb * L.drel.a_g)
check(f"floor mid-span, {H_RELAX_MM / 10:.0f} cm ({L.drel.a_g:.0f} g)", s_c8, False, SF_STATIC, info=True)
check(f"floor at strap slot (Kt 2.5), {H_RELAX_MM / 10:.0f} cm", s_s8, False, SF_STATIC, Kt=2.5, info=True)
s_fv8, Rf8 = face_screw_vertical(L.drel.corner)
check(f"M1.6 screws bearing in wall, {H_RELAX_MM / 10:.0f} cm rear corner ({Rf8:.0f} N)", s_fv8, False, SF_STATIC, info=True)
check_metal(f"idler M3 bolt 8.8, {H_RELAX_MM / 10:.0f} cm corner {L.drel.corner:.0f} N", bend_round(L.drel.corner * arm_bolt, d3), SY_88_MPA, info=True)

# FIX set (with the drop limited to H_RELAX): side walls 4.5 from X~25 forward (inner side), Ø20 bosses + r2 fillets,
# 12.9 M3x45 bolts, N20 clamp cap + 4 mm cradle cheeks, strap slots moved out
t_fix, a_fix, Kt_fix = 4.5, 10.0, 1.5
arm_fix = F.Y_T - (F.HALF_W_OUT - t_fix / 2)
for lab, Fv in ((f"spec {SPEC_DROP_AXLE_N:.0f} N", SPEC_DROP_AXLE_N), (f"{H_RELAX_MM / 10:.0f} cm flat {L.drel.flat:.0f} N", L.drel.flat),
                ("30 cm flat", L.d30.flat)):
    check(f"FIX wall {t_fix}/boss Ø{2 * a_fix:.0f} r2: boss rim, {lab}", boss_Z(Fv, a=a_fix, t=t_fix, Kt=Kt_fix, arm=arm_fix),
          True, SF_STATIC, info=True)
check(f"FIX wall {t_fix}: idler block, {H_RELAX_MM / 10:.0f} cm corner {L.drel.corner:.0f} N",
      boss_Z(L.drel.corner, a=a_idler, t=t_fix, Kt=Kt_fix, arm=arm_fix), True, SF_STATIC, info=True)
a_id_fix = math.sqrt(30.0 * 24.0 / math.pi)
check(f"FIX wall {t_fix} + idler block 30x24 to the floor: {H_RELAX_MM / 10:.0f} cm corner",
      boss_Z(L.drel.corner, a=a_id_fix, t=t_fix, Kt=Kt_fix, arm=arm_fix), True, SF_STATIC, info=True)
check("FIX Ø4 washer under each M1.6 head: head bearing, stall", face_screw_T(L.R_stall) / (math.pi / 4 * (16 - d_scr_hole ** 2)),
      False, SF_STATIC, info=True)
check(f"FIX wall {t_fix}: nut bearing, spec 25 N", nut_bearing(SPEC_DROP_AXLE_N, yin=F.HALF_W_OUT - t_fix - p.BOSS_T + 0.75),
      False, SF_STATIC, info=True)
check_metal(f"FIX M3 12.9 bolt, {H_RELAX_MM / 10:.0f} cm corner {L.drel.corner:.0f} N", bend_round(L.drel.corner * arm_bolt, d3), 1080.0, info=True)
# motor: cradle cheeks 4 mm beside the can take the in-plane moment; a cap over the gearbox takes the vertical load
F_cheek = motor_moment(L.R_stall) / (F.MOTOR_FACE_Y - y_cradle)
h_cheek = F.Z_A - (F.Z_A - M.gb_h / 2)                 # contact at the can axis, above the cradle top
check(f"FIX cradle cheek 4 mm (Z), stall, {F_cheek:.0f} N", bend_rect(F_cheek * h_cheek, M.can_len, 4.0), True, SF_STATIC, Kt=1.5, info=True)
R8 = face_screw_vertical(L.drel.corner)[1]
check(f"FIX gearbox cap: 2 x M2 pull-out of cradle, {H_RELAX_MM / 10:.0f} cm corner", R8 / 2 / (math.pi * 1.6 * 8.0), False,
      SF_STATIC, shear=True, info=True)
s_c8b, s_s8b = floor(mb * L.drel.a_g, slot_y=27.5)
check(f"FIX strap slots at |y| 27.5: floor at slot, {H_RELAX_MM / 10:.0f} cm", s_s8b, False, SF_STATIC, Kt=2.5, info=True)

report(f"{JOB} strength checks")

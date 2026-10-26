"""Strength check for jobs/20261026-rover-sprocket (tracked rover, PETG), round 2. Run: python3 jobs/20261026-rover-sprocket/strength_calc.py

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
JOB = "20261026-rover-sprocket"
L = rover_loads()
p = model_params(JOB)
chp = model_params("20261026-rover-chassis")
M = N20
dd = L.dd

# --- teeth (round 2: 0.5 x 45° root chamfers) -------------------------------------------------------------------------
b_tooth = 2 * p.DISC_HALF                             # 7.0 axial
r_root = p.DISC_R + p.ROOT_CHAMFER                    # 12.39: chamfer top, where the 2.7 mm flank starts
h_root = p.TOOTH_BASE_W                               # 2.7 tangential
arm = F.RP - r_root                                   # 3.79: knuckle contact taken on the pitch circle (round-1 convention)
arm_tip = p.TOOTH_TIP_R - r_root                      # 5.5
KT_CH = 1.8                                           # 0.5 x 45° chamfer, c/h 0.19: between the skill's sharp 2.5 and
                                                      # r >= 0.25 h 1.5; a chamfer is a little worse than a fillet
# --- D-bore on the N20 shaft ----------------------------------------------------------------------------------------------
d_bore = M.shaft_d + p.D_CLEARANCE + p.HOLE_COMP      # 3.2 CAD -> ~3.0 printed: press fit
L_eng = p.SHAFT_END_Z - p.HUB_Z0_D                    # 9.5 shaft engagement
e_flat = M.shaft_flat - M.shaft_d / 2                 # 1.0: shaft flat from the axis
b_flat = math.sqrt((M.shaft_d / 2) ** 2 - e_flat ** 2)  # 1.118: half-width of the flat
# --- hub, journal and the N20 lever (sprocket frame: z = world Y - Y_T; track load on z = 0) -------------------------------
D = F.HUB_D
z_jo = F.HALF_W_OUT - F.Y_T                           # -17: journal outer end (the hub bears here when it tilts)
z_se = p.SHAFT_END_Z                                  # -13.5: shaft end; outboard of it the PETG hub alone carries R
z_g = p.GRUB_Y - F.Y_T                                # -14.5: M2 set-screw hole
z_face = F.MOTOR_FACE_Y - F.Y_T                       # -23.5: N20 gearbox face
z_can = F.MOTOR_FACE_Y - M.gb_len - M.can_len - F.Y_T # -48: N20 can end on the cradle
k_lev = -z_jo / (z_jo - z_can)                        # 0.548: can-end reaction per N of hub load
L_j = F.WALL + F.JOURNAL_BOSS                         # 6
d_grub = p.GRUB_PILOT + p.HOLE_COMP                   # 1.8 CAD
r_b = d_bore / 2


def bore(x, y):
    return x * x + y * y < r_b * r_b


Z_tube, _, _ = section_modulus(D, bore)
Z_grub, _, _ = section_modulus(D, lambda x, y: bore(x, y) or (x > 0 and abs(y) < d_grub / 2))   # hole at the hot fibre
Z_d = min(section_modulus(M.shaft_d, lambda x, y: y > e_flat)[0], section_modulus(M.shaft_d, lambda x, y: x > e_flat)[0])
print(f"\nsprocket: tooth root (chamfer top) {h_root} x {b_tooth:.0f} at r {r_root:.2f}, arm to RP {arm:.2f} (tip {arm_tip:.2f}),"
      f" Kt {KT_CH}; D-bore {d_bore:.1f} CAD (~{d_bore - 0.2:.1f} printed) on the Ø{M.shaft_d} shaft, flat half-width"
      f" {b_flat:.3f}, engaged {L_eng:.1f}; hub Ø{D:.0f}: Z tube {Z_tube:.1f}, at the grub hole {Z_grub:.1f} mm^3;"
      f" N20 D-shaft Z {Z_d:.2f} mm^3")
print(f"journal lever: hub load R on z 0, fulcrum at the journal outer end z {z_jo:.0f}, N20 body to the can end z {z_can:.0f}:"
      f" journal {1 + k_lev:.3f} R, can end {k_lev:.3f} R, N20 shaft moment at the face {k_lev * (z_face - z_can):.1f} R"
      f" (round 1, no journal: {-z_face:.1f} R)")
print(f"note: the M2 set-screw hole points along +X, the D-flat faces +Y (CAD probe): the screw lands 90° from the flat, on"
      f" the round of the shaft, so it is friction only. The hub end (z {p.HUB_Z0_D:.1f}) sits {p.HUB_Z0_D - z_face:.1f} mm"
      f" from the gearbox face but the N20 bearing boss stands {M.boss_h} mm proud (Ø{M.boss_d}): they overlap"
      f" {M.boss_h - (p.HUB_Z0_D - z_face):.1f} mm (assembly_check skips the motor/sprocket pair)")


def tooth_root(F_n, L_arm, Kt=KT_CH):
    return Kt * bend_rect(F_n * L_arm, b_tooth, h_root)


def dflat_bearing(T):
    """Rigid rotation of the shaft flat against the bore flat: pressure 0 at the flat centre -> p_max at its edge on
    one side; T = p_max L b^2 / 3. Returned: mean pressure on the loaded half (= p_max / 2), the bolt-bearing analogue.
    Press fit: no clearance to close, but friction is not credited (round-1 method)."""
    return 1.5 * T / (L_eng * b_flat ** 2)


def journal_bearing(R):
    Rj = (1 + k_lev) * R
    return 2 * Rj / (D * L_j), Rj              # triangular over the journal, peak = 2 x mean; hub surface = layer edges


def hub_end(R, Z=None):
    """Hub just outboard of the shaft end: only PETG between the track plane and the shaft. Axial stress = Z."""
    return R * (-z_se) / (Z or Z_tube)


def hub_grub(R, Kt=2.0):
    """Hub at the set-screw hole, full moment on the PETG (the shaft ends 1 mm further out), Kt 2 on the net section
    (skill: hole, tough material). The hub turns under a fixed load: rotating bending, every fibre sees it."""
    return Kt * R * (-z_g) / Z_grub


T_cyc = L.F_trac * F.RP
# --- teeth ---------------------------------------------------------------------------------------------------------------
check(f"tooth root (chamfer top), stall pull {L.F_stall:.1f} N on 1 tooth at RP (Kt {KT_CH})", tooth_root(L.F_stall, arm),
      False, SF_STATIC)
check(f"tooth root, everyday pull {L.F_trac:.1f} N (Kt {KT_CH})", tooth_root(L.F_trac, arm), False, SF_CYCLIC)
check("tooth root shear, stall", 1.5 * L.F_stall / (b_tooth * h_root), False, SF_STATIC, shear=True)
# --- torque into the shaft ------------------------------------------------------------------------------------------------
check(f"D-flat bearing, stall {T_STALL_PACK_NMM:.0f} N*mm, {L_eng:.1f} mm engaged (mean, loaded half)",
      dflat_bearing(T_STALL_PACK_NMM), False, SF_STATIC)
check(f"D-flat bearing, everyday {T_cyc:.0f} N*mm", dflat_bearing(T_cyc), False, SF_CYCLIC)
# --- hub: journal bearing and bending -------------------------------------------------------------------------------------
for lab, R, sf in (("stall", L.R_stall, SF_STATIC), ("pretension sustained", L.R_sus, SF_CYCLIC)):
    s, Rj = journal_bearing(R)
    check(f"hub on the journal, {lab} (journal {Rj:.1f} N at its outer end)", s, False, sf)
for lab, R, sf in (("stall", L.R_stall, SF_STATIC), ("cyclic (rotating bending)", L.R_cyc, SF_CYCLIC),
                   ("pretension sustained", L.R_sus, SF_CYCLIC)):
    check(f"hub bending at the shaft end (axial = Z), {lab} R {R:.1f} N x {-z_se:.1f}", hub_end(R), True, sf)
for lab, R, sf in (("stall", L.R_stall, SF_STATIC), ("cyclic (rotating bending)", L.R_cyc, SF_CYCLIC),
                   ("pretension sustained", L.R_sus, SF_CYCLIC)):
    check(f"hub at the M2 set-screw hole (Z, Kt 2 net), {lab} R {R:.1f} N x {-z_g:.1f}", hub_grub(R), True, sf)
# --- drop: the sprocket sits on the bottom run like a road wheel ------------------------------------------------------------
check(f"hub bending at the shaft end, 5 cm rear corner {dd.corner:.1f} N", hub_end(dd.corner), True, SF_STATIC, drop=True)
check(f"hub at the set-screw hole, 5 cm rear corner", hub_grub(dd.corner), True, SF_STATIC, drop=True)
s, Rj = journal_bearing(dd.corner)
check(f"hub on the journal, 5 cm rear corner (journal {Rj:.0f} N)", s, False, SF_STATIC, drop=True)
rim_area = b_tooth * 2 * (4 * 0.45)                  # 4 perimeters spread the link's line load
check("disc rim bearing under a link, 5 cm rear corner", dd.corner / rim_area, False, SF_STATIC, drop=True)
# --- skid-steer side load: 3 N axial pulls the sprocket along the shaft; set-screw friction + press fit ----------------------
mu, N_grub_min = 0.2, 30.0                            # assumption: set-screw clamp after creep >= 30 N
check_custom(f"axial retention (set-screw friction 2 x mu N >= side {L.side:.0f} N)", L.side, 2 * mu * N_grub_min,
             "friction N", SF_CYCLIC)

# --- advisory --------------------------------------------------------------------------------------------------------------
check("spec §4 tooth case: 14.9 N on one tooth TIP (not reachable: the teeth share T_tight - T_slack = 9.9 N)",
      tooth_root(L.T_tight_stall, arm_tip), False, SF_STATIC, info=True)
check(f"tooth root, stall pull {L.F_stall:.1f} N at the TIP (link riding over a tooth on a slack track)",
      tooth_root(L.F_stall, arm_tip), False, SF_STATIC, info=True)
check(f"tooth root, fresh pack 100 % PWM {L.T_fresh:.0f} N*mm", tooth_root(L.T_fresh / F.RP, arm), False, SF_STATIC, info=True)
check("tooth root, stall, if the chamfer behaves like a sharp corner (Kt 2.0)", tooth_root(L.F_stall, arm, 2.0), False,
      SF_STATIC, info=True)
check(f"D-flat bearing, fresh pack 100 % PWM {L.T_fresh:.0f} N*mm", dflat_bearing(L.T_fresh), False, SF_STATIC, info=True)
check(f"D-flat bearing, fresh pack at the 80 % PWM cap {L.T_cap:.0f} N*mm", dflat_bearing(L.T_cap), False, SF_STATIC, info=True)
L_cb = L_eng - 1.3                              # DFM round-2 fix 1: Ø4.7 x 1.3 counterbore in the hub end
check(f"D-flat bearing, stall, with the DFM hub-end counterbore ({L_cb:.1f} mm engaged)",
      1.5 * T_STALL_PACK_NMM / (L_cb * b_flat ** 2), False, SF_STATIC, info=True)
L_need = SF_STATIC * 1.5 * T_STALL_PACK_NMM / (ALLOW_INPLANE_MPA * b_flat ** 2)
print(f"D-flat: SF {SF_STATIC:.0f} at {T_STALL_PACK_NMM:.0f} N*mm needs {L_need:.0f} mm of flat in PETG; the N20 shaft is"
      f" {M.shaft_len:.0f} mm long -> no printed bore can pass")
check(f"hub bending at the shaft end, 5 cm corner, stiff landing delta {DELTA_STIFF_MM} ({L.dst.corner:.0f} N)",
      hub_end(L.dst.corner), True, SF_STATIC, info=True)
for lab, R in (("stall", L.R_stall), (f"5 cm corner", dd.corner)):
    check_metal(f"N20 shaft (D) at the gearbox face, lever model (journal + cradle), {lab} {R:.1f} N",
                k_lev * R * (z_face - z_can) / Z_d, SY_STEEL_MPA, info=True)
    check_metal(f"N20 shaft (D) at the gearbox face, bound: motor clamped, journal not reached, {lab}",
                R * (-z_face) / Z_d, SY_STEEL_MPA, info=True)
mu_j = 0.3
for lab, R in (("pretension", L.R_sus), ("everyday", L.R_cyc)):
    Tf = mu_j * (1 + k_lev) * R * D / 2
    print(f"journal friction ({lab}, PETG on PETG mu {mu_j}): {Tf:.0f} N*mm per side = {Tf / T_cyc * 100:.0f} % of the"
          f" everyday drive torque {T_cyc:.0f} N*mm (performance, not strength)")
# FIX: metal N20 hub (3 mm D bore, its own set screw on the flat); printed disc bolted to it with 4 x M3 on r 6
n_b, r_bc, d_b = 4, 6.0, 3.0
check(f"FIX metal N20 hub: M3 bolt bearing in the 7 mm disc (4 on r{r_bc:.0f}), stall", bearing(T_STALL_PACK_NMM / (n_b * r_bc),
      d_b, b_tooth), False, SF_STATIC, info=True)
check("FIX metal N20 hub: bolt bearing, 5 cm corner (radial shared by 4)", bearing(dd.corner / n_b, d_b, b_tooth), False,
      SF_STATIC, info=True)
y_fl = e_flat + (p.D_CLEARANCE + p.HOLE_COMP) / 2   # CAD flat 1.1 from the axis; hole turned onto it (DFM fix 2)
Z_onflat = section_modulus(D, lambda x, y: (bore(x, y) and x < y_fl) or (x > 0 and abs(y) < d_grub / 2))[0]
check(f"set screw turned onto the flat (DFM round-2 fix 2): hub at the hole (Kt 2 net), stall",
      2.0 * L.R_stall * (-z_g) / Z_onflat, True, SF_STATIC, info=True)
for D_f in (10.5, 11.0):
    Z_f = section_modulus(D_f, bore)[0]
    check(f"FIX HUB_D {D:.0f} -> {D_f} (journal follows), no set-screw hole: hub at the shaft end, 5 cm corner",
          hub_end(dd.corner, Z_f), True, SF_STATIC, info=True)

report(f"{JOB} strength checks")

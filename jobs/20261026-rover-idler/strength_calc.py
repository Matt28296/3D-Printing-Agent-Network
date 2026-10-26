"""Strength check for jobs/20261026-rover-idler (tracked rover, PETG). Run: python3 jobs/__JOB__/strength_calc.py

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
JOB = "20261026-rover-idler"
L = rover_loads()
sp = model_params("20261026-rover-sprocket")      # the idler model runs the sprocket model with BORE = "round"
ip = model_params(JOB)
pr = print_req(JOB)["min"]

bore_cad = ip.ROUND_BORE + sp.HOLE_COMP           # 3.4 CAD, ~3.2 printed
d_bolt = 3.0                                      # M3 major; idler runs on the bolt threads (fully threaded M3)
THREAD_F = 0.5                                    # contact on thread crests ~ half the projected area (assumption)
L_bore = sp.DISC_HALF - sp.HUB_Z0                 # 20
L_disc = 2 * sp.DISC_HALF + (sp.HUB_D - bore_cad) / 2   # disc width + 45 deg spread into the hub
L_eff = THREAD_F * min(L_disc, L_bore)
perim_t = pr["perimeters"] * 0.45
print(f"\nidler: bore {bore_cad:.2f} CAD on M3 threads, bore length {L_bore:.1f}, effective bearing length"
      f" {L_eff:.1f} (disc {L_disc:.1f} x thread factor {THREAD_F}); {pr['perimeters']} perimeters = {perim_t:.2f} mm")


def bore(R):
    return bearing(R, d_bolt, L_eff)


r0 = sp.DISC_R - 0.5
h_root = sp.TOOTH_BASE_W + (sp.TOOTH_TIP_W - sp.TOOTH_BASE_W) * (sp.DISC_R - r0) / (sp.TOOTH_TIP_R - r0)
b_tooth = 2 * sp.DISC_HALF
arm = F.RP - sp.DISC_R
# A free idler's teeth carry only its bearing drag: mu * R * r_bolt / RP (mu 0.3 plastic on steel threads)
F_tooth_drag = 0.3 * L.R_stall * (d_bolt / 2) / F.RP

check(f"bore bearing on M3 threads, stall R {L.R_stall:.1f} N", bore(L.R_stall), False, SF_STATIC)
check(f"bore bearing, cyclic R {L.R_cyc:.1f} N", bore(L.R_cyc), False, SF_CYCLIC)
check(f"bore bearing, pretension sustained R {L.R_sus:.0f} N (creep)", bore(L.R_sus), False, SF_CYCLIC)
check(f"bore bearing, 30 cm drop, front corner {L.d30.corner:.0f} N", bore(L.d30.corner), False, SF_STATIC)
check(f"disc rim bearing under a link, 30 cm corner", L.d30.corner / (b_tooth * 2 * perim_t), False, SF_STATIC)
check(f"tooth root, bearing drag {F_tooth_drag:.2f} N (Kt 2.5)", 2.5 * bend_rect(F_tooth_drag * arm, b_tooth, h_root), False, SF_CYCLIC)
# skid-steer side drag: track pushes the idler along the bolt onto the wall nut / washer; hub end face bearing
A_end = math.pi / 4 * (sp.HUB_D ** 2 - bore_cad ** 2)
check(f"hub end-face bearing, side {L.side:.0f} N", L.side / A_end, False, SF_CYCLIC)

# advisory
check(f"tooth root if a jam loads one idler tooth with stall pull {L.F_stall:.1f} N", 2.5 * bend_rect(L.F_stall * arm, b_tooth, h_root),
      False, SF_STATIC, info=True)
check(f"bore bearing, 30 cm flat {L.d30.flat:.0f} N", bore(L.d30.flat), False, SF_STATIC, info=True)
check(f"bore bearing, 30 cm corner, delta 10 ({L.dlb.corner:.0f} N)", bore(L.dlb.corner), False, SF_STATIC, info=True)
check(f"bore bearing, {H_RELAX_MM / 10:.0f} cm corner {L.drel.corner:.0f} N", bore(L.drel.corner), False, SF_STATIC, info=True)
# FIX: 4/3 mm brass tube sleeve on the bolt (bore 4.0 printed -> 4.2 CAD), smooth contact, factor 1
check(f"FIX Ø4 brass sleeve: bore bearing, 30 cm corner", bearing(L.d30.corner, 4.0, min(L_disc, L_bore)), False,
      SF_STATIC, info=True)
# bolt (owned by the chassis check): M3 cantilever, track centre plane 17 mm from the wall face
d3 = 2.387
arm_bolt = F.Y_T - F.HALF_W_OUT
for lab, Fb, sy in (("stall R", L.R_stall, SY_A2_70_MPA), ("30 cm corner", L.d30.corner, SY_88_MPA),
                    (f"{H_RELAX_MM / 10:.0f} cm corner", L.drel.corner, SY_88_MPA)):
    check_metal(f"M3 bolt bending at wall face ({lab} {Fb:.0f} N x {arm_bolt:.0f})", bend_round(Fb * arm_bolt, d3), sy, info=True)

report(f"{JOB} strength checks")

"""Strength check for jobs/20261026-rover-track-link (tracked rover, PETG). Run: python3 jobs/__JOB__/strength_calc.py

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
JOB = "20261026-rover-track-link"
L = rover_loads()
p = model_params(JOB)

# --- geometry from model.py / rover_frame.py ----------------------------------------------------------------------
d_pin = p.PIN_D                                   # 1.75 filament
d_hole = p.PIN_D + p.PIN_CLR + p.HOLE_COMP        # 2.10 CAD (prints ~1.9); CAD value used: smaller ligament
A_pin = math.pi / 4 * d_pin ** 2
I_pin = math.pi * d_pin ** 4 / 64
Lc = 2 * p.CENTRE_HALF                            # centre knuckle length 13.5
Lo = p.HALF_W - p.OUTER_IN                        # each outer knuckle 4.75
gap = p.OUTER_IN - p.CENTRE_HALF                  # axial gap at each shear plane 0.5
e_edge = p.KN_R                                   # pin axis to knuckle edge, along the pull (x)
lig = e_edge - d_hole / 2                         # 1.95 tear-out ligament
clr = p.KN_R + p.KN_GAP
print(f"\nlink: pin Ø{d_pin} in Ø{d_hole:.2f} CAD holes; centre knuckle {Lc} + 2 x outer {Lo}, gaps {gap};"
      f" ligament {lig:.2f}; 2 shear planes per hinge (spec says 3)")

# Pin = 1.75 mm PETG/PLA filament (extruded, not printed): placeholder in-plane allowable used, E = E_PETG.
# Pin bending: the pin is as soft as the knuckles (E_pin ~ E_knuckle) and the knuckles are long compared with
# 1/beta, so it is a beam on an elastic foundation (Hetenyi), not the stiff-pin clevis of Shigley.
# Foundation modulus k = 0.5 * E_PETG (soft end of the 0.5-1 E range -> larger moment, conservative).
k_found = 0.5 * E_PETG_MPA
beta = bef_beta(k_found, E_PETG_MPA, I_pin)
print(f"BEF: beta {beta:.3f} /mm, 1/beta {1 / beta:.2f} mm; beta*Lo {beta * Lo:.1f}, beta*Lc/2 {beta * Lc / 2:.1f}"
      f" (> ~2.5: semi-infinite assumption OK)")


def pin_moment_bef(V):
    """Max moment in a semi-infinite BEF pin segment loaded at the shear plane by shear V and the gap moment V*g/2."""
    M0 = V * gap / 2
    best = 0.0
    for i in range(1, 400):
        u = i * 0.01
        m = math.exp(-u) * (M0 * (math.cos(u) + math.sin(u)) + V / beta * math.sin(u))
        best = max(best, abs(m))
    return max(best, M0)


def pin_bearing_bef(V):
    """Peak line pressure at the knuckle face: q0 = 2 V beta + 2 M0 beta^2 (N/mm) -> bearing q0 / d."""
    M0 = V * gap / 2
    return (2 * V * beta + 2 * M0 * beta ** 2) / d_pin


def pin_moment_clevis(Fp):
    """Stiff-pin clevis, uniform pressure (Shigley): M = F/2 (a/2 + g + b/4)."""
    return Fp / 2 * (Lo / 2 + gap + Lc / 4)


L_load = min(2.0 / beta, Lo)   # length over which one knuckle end picks up the pin load (BEF), per end


def tension_checks(label, T, sf, info=False):
    V = T / 2
    check(f"pin shear (2 planes), {label} {T:.1f} N", T / (2 * A_pin), False, sf, shear=True, info=info)
    check(f"pin bending (BEF), {label}", bend_round(pin_moment_bef(V), d_pin), False, sf, info=info)
    check(f"pin bearing in knuckle (BEF peak), {label}", pin_bearing_bef(V), False, sf, info=info)
    # tear-out: the strip behind the hole (|z| < r_hole) is cut off from its own layer by the hole, so it can only
    # shed load into the layers above/below: shear along layer interfaces -> across-layer shear allowable.
    check(f"centre-knuckle tear-out to x=-{e_edge:.0f}, {label}", tearout(T, lig, 2 * L_load), True, sf, shear=True, info=info)
    check(f"outer-knuckle tear-out (each T/2), {label}", tearout(T / 2, lig, L_load), True, sf, shear=True, info=info)


# --- 1. track tension -----------------------------------------------------------------------------------------------
tension_checks("stall", L.T_tight_stall, SF_STATIC)
tension_checks("cyclic", L.T_tight_cyc, SF_CYCLIC)
check(f"pin bending (BEF), pretension sustained {T0_N:.0f} N", bend_round(pin_moment_bef(T0_N / 2), d_pin), False, SF_CYCLIC)
# body net section where the notch starts: two lands |y| NOTCH_HALF..CENTRE_HALF, full thickness, sharp corners
A_net = 2 * (p.CENTRE_HALF - p.NOTCH_HALF) * p.LINK_T
check("body net section at notch root (Kt 2.5), stall", L.T_tight_stall / A_net, False, SF_STATIC, Kt=2.5)
# bridge (x clr..P-clr) shears the load from the centre lands out to the outer knuckles
A_br = (p.P - 2 * clr) * p.LINK_T
check("bridge shear centre -> outer lands, stall", 1.5 * (L.T_tight_stall / 2) / A_br, False, SF_STATIC, shear=True)

# --- 2. drop: road-wheel rim lands on a hinge -----------------------------------------------------------------------
# The rim presses the centre knuckle of link n+1 and the outer knuckles of link n. The centre knuckle's share
# (Lc / TRACK_W) reaches the ground fastest through the pin into link n's outer knuckles, which sit 1 mm from
# link n's grousers: the pin carries it in double shear. (Rim on the bridge instead: load sits over the grousers.)
share = Lc / p.TRACK_W


def drop_checks(label, Fax, info=False):
    Fp = share * Fax
    V = Fp / 2
    check(f"drop on hinge, pin shear, {label} {Fax:.0f} N/axle", Fp / (2 * A_pin), False, SF_STATIC, shear=True, info=info)
    check(f"drop on hinge, pin bending (BEF), {label}", bend_round(pin_moment_bef(V), d_pin), False, SF_STATIC, info=info)
    check(f"drop on hinge, knuckle bearing (BEF), {label}", pin_bearing_bef(V), False, SF_STATIC, info=info)
    g_area = 2 * (p.GROUSER_X[1] - p.GROUSER_X[0]) * ((p.HALF_W - 0.5) - (p.OUTER_IN + 0.25))
    check(f"grouser compression, {label}", Fax / g_area, False, SF_STATIC, info=info)


drop_checks("30 cm flat", L.d30.flat)

# --- 3. skid-steer side drag: track edge on a V-flange -----------------------------------------------------------------
# 3 N on the outer knuckle end face (|y| 12, Lo x LINK_T contact), compression in-plane
check(f"side drag on knuckle end face, {L.side:.1f} N", L.side / (0.5 * (p.P - clr) * p.LINK_T), False, SF_CYCLIC)

# --- advisory --------------------------------------------------------------------------------------------------------
check("BOUND: stiff-pin clevis (uniform) pin bending, stall", bend_round(pin_moment_clevis(L.T_tight_stall), d_pin),
      False, SF_STATIC, info=True)
drop_checks("spec", SPEC_DROP_AXLE_N, info=True)
drop_checks("30 cm, delta 10", L.dlb.flat, info=True)
drop_checks(f"{H_RELAX_MM / 10:.0f} cm drop", L.drel.flat, info=True)
check("proof test 3 kg on 5-link chain: pin bending (BEF)", bend_round(pin_moment_bef(29.4 / 2), d_pin), False, 1.0, info=True)
# fix: Ø2.0 spring-steel (music) wire pins, hole 2.0 + 0.15 + 0.2 = 2.35 CAD -> stiff pin: uniform clevis
d_s = 2.0
hole_s = d_s + p.PIN_CLR + p.HOLE_COMP
Fp30 = share * L.d30.flat
check_custom(f"FIX Ø{d_s} music-wire pin bending (clevis), 30 cm flat", bend_round(pin_moment_clevis(Fp30), d_s),
             1500.0, "steel σy 1500", SF_METAL, info=True)
check(f"FIX Ø{d_s} steel pin: centre-knuckle bearing (uniform), 30 cm flat", bearing(Fp30, d_s, Lc), False, SF_STATIC, info=True)
check(f"FIX Ø{d_s} steel pin: tear-out (hole {hole_s:.2f}), stall", tearout(L.T_tight_stall, e_edge - hole_s / 2, Lc),
      True, SF_STATIC, shear=True, info=True)
check(f"FIX Ø{d_s} steel pin: tear-out, 30 cm drop on hinge", tearout(Fp30, e_edge - hole_s / 2, Lc), True, SF_STATIC,
      shear=True, info=True)

report(f"{JOB} strength checks")

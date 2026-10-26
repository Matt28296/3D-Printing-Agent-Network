"""Strength check, round 4: jobs/20261026-arm-claw-cover (front plate in two pieces + two ties, top wall, 8 mm lip, the
second tie's 8 mm post seated on the frame's rail block and anchored there by one vertical M3 x 45).

Run from the project root:  python3 jobs/20261026-arm-claw-cover/strength_calc.py
Plain python3: parameters come from claw_frame.py, this job's model.py, the jaw's model.py and tools/hobby_parts.py
(ast module). No build123d needed. Section widths quoted as "probed" were measured on the round 3 solid (design())
with thin slabs, and the second post's on the round 4 solid; the script states them as numbers so it runs without the
CAD venv.

Round 4 (independent re-check of the as-built anchor):
- the anchor is in the model as built (ANCHOR2 = ANCHOR_AS_BUILT, from ANCHOR_XY in claw_frame.py);
- the anchor's x hold is checked two ways: (a) the snug preload's friction holds the post's foot at once (round 3's
  what-if), (b) the preload has crept away (fdm-design-rules §4: do not count on preload in PETG), so the foot slides
  through the hole's radial clearance before the shank bears: the cover takes the push the unanchored way (z still held:
  seat in compression, screw in tension) until the foot has moved the gap, and the anchored way after that;
- new rows: the M3 x 45 (pull-out from the frame's pilot, head bearing on the top wall, shank bearing after a slip),
  the post's root under the lip and its foot over the rail block, the post round its hole, spec §8's proof push.

The cover prints standing on its -y end: print Z = claw y. Bending of the front plate, the top wall, the lip, the posts
and the webs in the side profile (stresses along claw x or z) runs along the layers (25 MPa); beams along claw y (the
strip under slot B) bend across them (12.5 MPa). Placeholder PETG allowables (no library row): NEEDS_TEST at best.

The pinion pass-through and the two open-ended slots cut the front plate into two pieces:
  upper piece  y > ~7 (and over slot A's closed end): hangs from the top wall and, since round 3, is tied to the lip by
               the second tie (post + web, full at y 24..32, 45-degree undersides growing from the lip and from the
               plate down to y ~8); since round 4 the post is 8 thick and stands on the frame's rail block, anchored
               there by one vertical M3 x 45;
  lower piece  the strip under slot B plus the -y region up to slot A: screwed to the wrist plate's front edge
               (2 x M2.5 x 16 at y +-24, z 3) and tied to the lip by the first tie (post 8 x 8 + web, y -32..-24).
Each rack reacts its finger's moment as a couple of x-forces at its two ends. A grip puts rack A's forward contact on
the upper piece near the top wall and rack B's on the lower piece; anything that pushes a finger TOWARDS closing (a desk
crash on the lower finger, a hand, the claw opening against an obstacle) reverses the couple: rack A then pushes the
lower piece's top strip (z 36.4..38.25, above the first tie's web) and rack B the upper piece's bottom strip
(z 16.25..18.1, below the second tie's web).
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
JAW_BED_CHAMFER = consts(ROOT / "jobs" / "20261026-arm-claw-jaw" / "model.py",
                         {**CF_ENV, "HOLE_COMP_DEFAULT": HOLE_COMP_DEFAULT})["BED_CHAMFER"]
FRAME_P = consts(ROOT / "jobs" / "20261026-arm-claw-frame" / "model.py",
                 {**CF_ENV, "HOLE_COMP_DEFAULT": HOLE_COMP_DEFAULT})

ALLOW_XY, ALLOW_Z = 25.0, 12.5
SHEAR_Z = 6.25
BEARING = 25.0
SF_SHORT, SF_CYCLIC = 3.0, 4.0
KT_SHARP, KT_FILLET = 2.5, 1.5
E_MPA = 1800.0                         # placeholder PETG modulus (strength-checks); only stiffness RATIOS use it

# ---------------------------------------------------------------- loads
T_STALL = HOBBY["MG90S"].stall_torque_nmm
F1 = T_STALL / C.R_P                  # 21.6 N
X_MESH = (C.X_P0 + C.X_P1) / 2
X_GRIP = C.X_TIP - 3.0
F_CRASH = 13.0
F_YAW_Z = 1079.0 / (2 * 76.0)
F_HAND = 5.0
SPAN_CLOSED = C.RACK_Y[1] - C.RACK_Y[0]                  # 56.5
SPAN_OPEN = (C.RACK_Y[1] - C.STROKE) - (-C.HALF_Y)       # 41.4 (rack end beyond the cover's edge)


def thrust(F, x_load, span):
    return F * (x_load - X_MESH) / span


ROWS, INFO = [], []


def row(case, sec, d, stress, allow, req, rows=ROWS):
    sf = allow / stress if stress > 1e-12 else float("inf")
    rows.append((case, sec, d, stress, allow, sf, req))
    return sf


R_go = thrust(F1, X_GRIP, SPAN_OPEN)        # one jaw blocked (or opening against an obstacle), jaws open
R_gc = thrust(F1, X_GRIP, SPAN_CLOSED)
R_cc = thrust(F_CRASH, C.X_TIP, SPAN_CLOSED)
R_co = thrust(F_CRASH, C.X_TIP, SPAN_OPEN)
R_hand = thrust(F_HAND, C.X_TIP, SPAN_OPEN)
PATCH = 2.0                                 # the cocked rack's end bears within ~2 mm of its end

# ================================================================ 1. lip wall behind rack A (cantilever from the top wall)
LIP_H = C.Z_TOP0 - (C.ZS + C.RAIL_IN)                    # 11.75
H_R = LIP_H / 2


def wall(case, R, e_edge, req, t=C.GUIDE_T, kt=KT_SHARP, rows=ROWS, lever=H_R, label="lip root at the top wall, "
         "rack side"):
    b = PATCH + lever + min(lever, e_edge)
    s = kt * 6 * R * lever / (b * t * t)
    return row(case, f"{label} (Kt {kt}): b_eff {b:.1f}, t {t:.1f}, lever {lever:.1f}", "XY", s, ALLOW_XY, req, rows)


wall(f"stall, one jaw blocked, jaws 44 open: rack A's -y end at the lip's end, R {R_go:.1f} N (the first tie's prop "
     f"ignored)", R_go, 0.0, SF_SHORT)
wall(f"stall, one jaw blocked, jaws closed: rack A's -y end at y {C.RACK_Y[0]:.1f}, R {R_gc:.1f} N", R_gc,
     C.HALF_Y + C.RACK_Y[0], SF_SHORT)
wall(f"stall, both jaws (cyclic), jaws 44 open: R {R_go / 2:.1f} N at the lip's end", R_go / 2, 0.0, SF_CYCLIC)
e_plus_closed = C.HALF_Y - C.RACK_Y[1]                    # rack A's +y end at 31.4: 0.6 from the lip's end
wall(f"crash {F_CRASH:.0f} N pushes jaw A shut, jaws closed: rack A's +y end on the lip at y {C.RACK_Y[1]:.1f}, R "
     f"{R_cc:.1f} N (the second tie's prop ignored)", R_cc, e_plus_closed, SF_SHORT)
wall(f"added: opening against an obstacle, jaw A, jaws nearly closed: rack A's +y end at y {C.RACK_Y[1]:.1f}, R "
     f"{R_gc:.1f} N (the second tie's prop ignored)", R_gc, e_plus_closed, SF_SHORT)

# ================================================================ 2. upper piece
ZA0 = C.ZS + C.NECK_Z[0] - C.SLOT_CLR                    # 38.25
ZB1 = C.ZS - C.NECK_Z[0] + C.SLOT_CLR                    # 16.25
h_a = C.Z_TOP0 - ZA0
y_apex, z_apex = C.SLOT_A_END + h_a / 2, (ZA0 + C.Z_TOP0) / 2
z_rb = (ZB1 + (C.ZS - C.RACK_TIP)) / 2                   # rack B's teeth on the plate's bottom strip: z 16.25..18.1
T5 = C.FRONT_T
X_PL = (C.X_F0 + C.X_F1) / 2                              # plate centreline 37.35

# 2a. grip: rack A's +y end presses the upper piece near the top wall (cantilever from the top wall, lever ~5)
lev = C.Z_TOP0 - (ZA0 + C.Z_TOP0) / 2
wall(f"stall, one jaw blocked: rack A's +y end on the upper piece near slot A's end, R {R_go:.1f} N", R_go, 0.0,
     SF_SHORT, t=T5, kt=KT_FILLET, lever=lev, label="front plate at the top wall")

# 2b / 3. Reversed couples: rack B pushes the upper piece's bottom strip forward (z 17.2, at y 24..32), or rack A pushes
# the lower piece's top strip forward (z 37.3, at y -32..-24). The push has to leave the cover for the frame, and the
# cover meets the frame at two places only: the top wall on the bulkhead top (2 x M3, x 3.5..10, z 48.5, full width) and
# the lower piece on the wrist plate's front edge (2 x M2.5 x 16 at z 3; pushed forward, only the screw holds it). So
# the cover is solved as a frame in the x-z plane (stresses along x/z: along the layers) in two y-zones:
#   zone + (y 0..32): the upper piece's plate leg (z 35.25..48.5), the second tie (web rigid, 4 mm post, 8 mm lip) and
#            the top wall in front of the lip;
#   zone - (y -32..0): the first tie (web rigid, 8 x 8 post, 8 mm lip) and the lower piece's plate z 19.25 -> 3 down to
#            the M2.5;
#   each zone has its own half of the top wall behind the lip (x 10..14.35, 32 wide) and of the top joint.
# The two zones' lip/top-wall corners are tied rigidly in x and z (the top wall is very stiff in its own plane) and in
# rotation through the torsion of the open lip + top-wall L-section between the ties: G J / L = 692 x 2365 / 56 =
# 2.9e4 N.mm/rad (K_T_LO), with 3.5 x that as the stiff variant (K_T_HI, 1e5). A fully rigid coupling (one 2-D frame for
# the whole cover) is reported as an information bound: it ignores that the bulkhead top holds each corner along its
# whole width.
# Rigid links: the ties' webs and the lower part of each piece (the web makes a 16 x 12.5 block of it).
# Widths along y (probed on the solid): upper-piece plate 24.1 at the web top, 21.0 beside slot A's V apex, 25.5 at the
# top wall; second post 24.3 (A 97 mm2 at z 35.5); first post 8 x 8; lower-piece plate 25 (y -32..-7); webs 8 x 16
# (their 45-degree parts ignored); top wall in front of the lip 25.5.
# The joints to the frame are uncertain, so every row is the worst of 64 variants:
#   - the top wall on the bulkhead top: clamped, or a rotational spring. Screwed flat on a 6.5 x 64 bearing patch by
#     2 x M3: about E I_patch / t = 1800 x 1465 / 6 = 4.4e5 N.mm/rad; the soft variant is a quarter of that, split
#     between the zones (a perfectly pinned top is not credible for a flat, screwed joint);
#   - the M2.5 joint along x 3 or 30 kN/mm, and along z held (preload friction, 100 N x 0.3 = 30 N available) or free;
#   - the upper plate leg 21 or 25.5 wide; the second lip 25.5 or 37.25 wide (45-degree spread);
#   - the corner coupling K_T_LO or K_T_HI.
K_TOP_SOFT = 1.1e5
K_T_LO, K_T_HI = 2.9e4, 1.0e5
B_PLATE_WEBTOP, B_PLATE_APEX, B_PLATE_TOP = 24.1, 21.0, 25.5
B_POST2 = 24.4               # round 4, probed at z 35.5: 195.1 mm2 net of the anchor hole / 8 (I_y 1090: b_eq 25.55)
B_TW_FRONT = 25.5
T_POST2 = P.TIE2_POST_T                                   # 8 (round 4; round 3: 4)
ANCHOR_AS_BUILT = hasattr(C, "ANCHOR_XY") and P.TIE2_FOOT_Z <= C.ZS - C.RAIL_IN + 1e-6
ANCHOR2 = ANCHOR_AS_BUILT                                 # the second post seated + screwed on the rail block (round 4)
K_ANCHOR_X = 3000.0                                       # N/mm: the foot held in x (friction, or the shank once it bears)
ANCHOR_KX = K_ANCHOR_X                                    # set to 0 for the slip phase (preload gone, gap still open)
P_M3 = 150.0                                              # N, the anchor driven "snug only" (<= 0.09 N.m), assumption
GAP_NOM = (C.M3_CLEAR - 3.0) / 2                          # 0.2: printed Ø3.4 hole round the Ø3 shank, centred
GAP_MAX = (C.M3_CLEAR + P.HOLE_COMP - 3.0) / 2 + 0.1      # 0.4: CAD Ø3.6 + 0.1 position error (bound)
Z_FOOT = C.ZS - C.RAIL_IN                                 # 17.75: the post's foot on the rail block
D_HOLE = C.M3_CLEAR + P.HOLE_COMP                         # 3.6 CAD
POST_FOOT_A, POST_FOOT_I = 63.1, 386.0                    # probed on the round 4 solid at z 19 (net of the hole)
POST_WALL = 2.2                                           # probed: hole to either x face of the post (z 25, 40, 50)
STACK = C.Z_TOP1 - Z_FOOT                                 # 33.75: top wall + lip + post under the head
L_ANCHOR = 45.0 - STACK                                   # 11.25 engaged in the frame's 14 mm pilot
HEAD_DK = 5.5                                             # ISO 4762 M3 socket head
WASHER_M3 = (7.0, 0.5)                                    # ISO 7089 M3 washer, as on the MG996R tab screws
TIE_W = C.TIE_Y[1] - C.TIE_Y[0]                          # 8
WEB_H = 2 * C.TIE_Z                                       # 16
Z_WEB0, Z_WEB1 = C.ZS - C.TIE_Z, C.ZS + C.TIE_Z          # 19.25, 35.25
Z_POST1 = C.ZS + C.RAIL_IN                                # 36.75: posts meet the lip
Z_TOP_C = (C.Z_TOP0 + C.Z_TOP1) / 2                       # 50: top wall centreline
B_LOWER = C.HALF_Y - C.CRESCENT_Y                         # 25: lower piece's plate, y -32..-7
B_LIP1 = TIE_W + (C.Z_TOP0 - Z_POST1)                     # 19.75: one-sided 45-degree spread above the first post
B_TW_BACK = C.HALF_Y                                      # 32 per zone: the top wall behind the lip is full width
T_TW_BACK = C.TOP_T                                       # top wall behind the lip, x 0..14.35 (what-if parameter)
B_POST1 = TIE_W                                           # first post's width along y (what-if parameter)
KT_LIP_BACK = KT_SHARP                                    # lip back face / top wall underside corner (what-if)
B_NET_SCREW = B_TW_BACK - (C.M3_CLEAR + P.HOLE_COMP)      # 28.4 per zone: the top wall through an M3 hole
z_ra = ((C.ZS + C.RACK_TIP) + ZA0) / 2                   # rack A's teeth on the lower piece's top strip, ~37.3
Z_SCREW = C.FRONT_SCREWS[0][1]                            # 3
L_M25 = FRAME_P["FRONT_PILOT_DEPTH"] - 3.0                 # M2.5 x 16 through the 5 mm plate: 11 engaged
HEAD_D = 5.0                                               # M2.5 pan head (spec: head <= Ø5)
HOLE_PR = C.M25_CLEAR                                      # 2.8 printed (3.0 CAD teardrop)
A_HEAD = math.pi / 4 * (HEAD_D ** 2 - HOLE_PR ** 2) - (HOLE_PR / 2) ** 2 * (1 - math.pi / 4)   # minus the teardrop


def frame2d(nodes, members, supports, loads, ties=()):
    """Tiny linear 2-D frame solver. nodes {name: (x, z)}; members [(i, j, EA, EI, tag)]; supports {name: dof indices
    restrained (0 x, 1 z, 2 rotation)}; loads {name: (Fx, Fz, M)}; ties [(node_a, node_b, dof, k)]: a spring k between
    the same dof of two nodes. Returns {tag: (N, M_i, M_j, L)}: N > 0 tension, M_i / M_j the internal bending moments
    at the two ends (same sign convention, so M varies linearly between them)."""
    names = list(nodes)
    idx = {n: k for k, n in enumerate(names)}
    nd = 3 * len(names)
    K = [[0.0] * nd for _ in range(nd)]
    F = [0.0] * nd
    cache = []
    for (i, j, EA, EI, tag) in members:
        (xi, zi), (xj, zj) = nodes[i], nodes[j]
        L = math.hypot(xj - xi, zj - zi)
        c, s = (xj - xi) / L, (zj - zi) / L
        k = [[EA / L, 0, 0, -EA / L, 0, 0],
             [0, 12 * EI / L ** 3, 6 * EI / L ** 2, 0, -12 * EI / L ** 3, 6 * EI / L ** 2],
             [0, 6 * EI / L ** 2, 4 * EI / L, 0, -6 * EI / L ** 2, 2 * EI / L],
             [-EA / L, 0, 0, EA / L, 0, 0],
             [0, -12 * EI / L ** 3, -6 * EI / L ** 2, 0, 12 * EI / L ** 3, -6 * EI / L ** 2],
             [0, 6 * EI / L ** 2, 2 * EI / L, 0, -6 * EI / L ** 2, 4 * EI / L]]
        T = [[c, s, 0, 0, 0, 0], [-s, c, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0],
             [0, 0, 0, c, s, 0], [0, 0, 0, -s, c, 0], [0, 0, 0, 0, 0, 1]]
        kT = [[sum(k[a][b] * T[b][q] for b in range(6)) for q in range(6)] for a in range(6)]
        kg = [[sum(T[a][p] * kT[a][q] for a in range(6)) for q in range(6)] for p in range(6)]
        dofs = [3 * idx[i], 3 * idx[i] + 1, 3 * idx[i] + 2, 3 * idx[j], 3 * idx[j] + 1, 3 * idx[j] + 2]
        for p in range(6):
            for q in range(6):
                K[dofs[p]][dofs[q]] += kg[p][q]
        cache.append((k, T, dofs, tag, L))
    for (a, b, d, kk) in ties:
        da, db = 3 * idx[a] + d, 3 * idx[b] + d
        K[da][da] += kk
        K[db][db] += kk
        K[da][db] -= kk
        K[db][da] -= kk
    for n, (fx, fz, m) in loads.items():
        F[3 * idx[n]] += fx
        F[3 * idx[n] + 1] += fz
        F[3 * idx[n] + 2] += m
    fixed = {3 * idx[n] + d for n, ds in supports.items() for d in ds}
    free = [d for d in range(nd) if d not in fixed]
    A = [[K[p][q] for q in free] + [F[p]] for p in free]
    n = len(free)
    for col in range(n):                                   # Gauss-Jordan with partial pivoting
        piv = max(range(col, n), key=lambda r: abs(A[r][col]))
        A[col], A[piv] = A[piv], A[col]
        pr = A[col]
        for r in range(n):
            if r != col and A[r][col] != 0.0:
                f = A[r][col] / pr[col]
                A[r] = [a - f * b for a, b in zip(A[r], pr)]
    u = [0.0] * nd
    for r, d in enumerate(free):
        u[d] = A[r][n] / A[r][r]
    out = {}
    for k, T, dofs, tag, L in cache:
        ue = [u[d] for d in dofs]
        ul = [sum(T[p][q] * ue[q] for q in range(6)) for p in range(6)]
        f = [sum(k[p][q] * ul[q] for q in range(6)) for p in range(6)]
        out[tag] = (f[3], -f[2], f[5], L)
    out["_u"] = {n: (u[3 * idx[n]], u[3 * idx[n] + 1], u[3 * idx[n] + 2]) for n in names}   # node displacements (mm, rad)
    return out


RIGID = 1e5
PENALTY = 1e9


def cover_frame(load_node, R, b_front, b_lip2, top_clamped, k_screw, screw_z, k_t):
    """The cover as a two-zone frame; R (+x) at load_node ('LD2' upper piece, 'LD1' lower piece). k_t None = the two
    corners joined rigidly (one 2-D frame)."""
    xl = (C.LIP_X0 + C.RAIL_X1) / 2                       # 18.35: lip (and first post) centreline
    xp2 = C.RAIL_X1 - T_POST2 / 2                         # 18.35: second post centreline (8 thick; 20.35 when 4)
    nodes = {"BKa": (C.X_B, Z_TOP_C), "TWRa": (C.LIP_X0, Z_TOP_C), "LTa": (xl, C.Z_TOP0), "TWB": (C.RAIL_X1, Z_TOP_C),
             "TWF": (C.X_F0, Z_TOP_C), "PLT": (X_PL, C.Z_TOP0),
             "L2B": (xl, Z_POST1), "P2T": (xp2 + 1e-3, Z_POST1), "P2B": (xp2, Z_WEB1), "FF2": (X_PL, Z_WEB1), "LD2": (X_PL, z_rb),
             "BKb": (C.X_B, Z_TOP_C + 1e-3), "TWRb": (C.LIP_X0, Z_TOP_C + 1e-3), "LTb": (xl, C.Z_TOP0 + 1e-3),
             "L1B": (xl, Z_POST1 + 1e-3), "P1B": (xl, Z_WEB1), "LPF": (X_PL, Z_WEB1 + 1e-3), "LD1": (X_PL, z_ra),
             "LPW": (X_PL, Z_WEB0), "LPS": (X_PL, Z_SCREW), "GS": (X_PL + 10.0, Z_SCREW),
             "GBa": (C.X_B - 10.0, Z_TOP_C), "GBb": (C.X_B - 10.0, Z_TOP_C + 1e-3)}
    Ep = E_MPA

    def mem(i, j, t, b, tag, rigid=False):
        k = RIGID if rigid else 1.0
        return (i, j, Ep * b * t * k, Ep * b * t ** 3 / 12 * k, tag)
    members = [mem("BKa", "TWRa", T_TW_BACK, B_TW_BACK, "top wall behind the lip, zone +"),
               mem("TWRa", "LTa", C.GUIDE_T, 32, "r1", True), mem("LTa", "TWB", C.GUIDE_T, 32, "r2", True),
               mem("TWF", "TWB", C.TOP_T, B_TW_FRONT, "top wall in front of the lip"),
               mem("PLT", "TWF", T5, b_front, "r3", True),
               mem("FF2", "PLT", T5, b_front, "plate leg"),
               mem("LTa", "L2B", C.GUIDE_T, b_lip2, "lip 2")]
    if abs(xp2 - xl) < 0.01:                              # round 4: the 8 mm post is on the lip's centreline (x 18.35)
        del nodes["P2T"]                                  # (a 0.001 mm link would make the stiffness matrix ill-posed)
        members += [mem("L2B", "P2B", T_POST2, B_POST2, "post 2")]
    else:
        members += [mem("L2B", "P2T", T_POST2, B_POST2, "r4", True), mem("P2T", "P2B", T_POST2, B_POST2, "post 2")]
    members += [mem("P2B", "FF2", WEB_H, TIE_W, "r5", True),
               mem("FF2", "LD2", T5, B_PLATE_WEBTOP, "r6", True),
               mem("BKb", "TWRb", T_TW_BACK, B_TW_BACK, "top wall behind the lip, zone -"),
               mem("TWRb", "LTb", C.GUIDE_T, 32, "r7", True),
               mem("LTb", "L1B", C.GUIDE_T, B_LIP1, "lip 1"), mem("L1B", "P1B", C.GUIDE_T, B_POST1, "post 1"),
               mem("P1B", "LPF", WEB_H, TIE_W, "r8", True), mem("LPF", "LD1", T5, B_LOWER, "r9", True),
               mem("LPF", "LPW", T5, B_LOWER, "r10", True),
               mem("LPW", "LPS", T5, B_LOWER, "lower plate"),
               ("LPS", "GS", k_screw * 10.0, 1e-6, "screw"),   # axial spring k_screw (EA / L, L 10)
               ("BKa", "GBa", 1e-6, K_TOP_SOFT / 2 * 10.0 / 4, "top joint +"),   # rotational springs 4 EI / L
               ("BKb", "GBb", 1e-6, K_TOP_SOFT / 2 * 10.0 / 4, "top joint -")]
    rot = (0, 1, 2) if top_clamped else (0, 1)
    sup = {"BKa": rot, "BKb": rot, "GS": (0, 1, 2), "GBa": (0, 1, 2), "GBb": (0, 1, 2),
           "LPS": (1,) if screw_z else ()}
    if ANCHOR2:
        # as built (round 4): the second post seated on the frame's rail block top (z 17.75) and clamped by the vertical
        # M3 x 45: the foot is held there in x (preload friction, or the shank once the gap has closed: a 3 kN/mm spring;
        # ANCHOR_KX 0 = sliding freely) and z (seat in compression, screw in tension: stiff)
        nodes.update({"AN": (xp2, C.ZS - C.RAIL_IN), "GA": (xp2 - 10.0, C.ZS - C.RAIL_IN),
                      "GZ": (xp2, C.ZS - C.RAIL_IN - 10.0)})
        members += [mem("P2B", "AN", WEB_H, TIE_W, "r11", True), ("AN", "GA", max(ANCHOR_KX, 1e-6) * 10.0, 1e-6, "anchor"),
                    ("AN", "GZ", 1e6 * 10.0, 1e-6, "anchor z")]   # seat (compression) / screw (tension), stiff
        sup.update({"GA": (0, 1, 2), "GZ": (0, 1, 2)})
    ties = [("LTa", "LTb", 0, PENALTY), ("LTa", "LTb", 1, PENALTY), ("LTa", "LTb", 2, PENALTY if k_t is None else k_t)]
    return frame2d(nodes, members, sup, {load_node: (R, 0.0, 0.0)}, ties)


VARIANTS = [(bf, bl, tc, ks, sz, kt) for bf in (B_PLATE_APEX, B_PLATE_TOP) for bl in (25.5, 37.25) for tc in (True, False)
            for ks in (3000.0, 30000.0) for sz in (True, False) for kt in (K_T_LO, K_T_HI)]


def vlabel(v):
    bf, bl, tc, ks, sz, kt = v
    return (f"plate b {bf}, lip b {bl}, top {'clamped' if tc else 'on 1.1e5 N.mm/rad'}, M2.5 {ks / 1000:.0f} kN/mm "
            f"{'held' if sz else 'free'} along z, corners {'rigid' if kt is None else f'{kt:.1e} N.mm/rad'}")


def sig(N, M, b, t, kt):
    return abs(N) / (b * t) + kt * 6 * abs(M) / (b * t * t)


def cover_sections(res, v, upper):
    """Stress at every checked section for one solved variant: {label: (stress, allow, dir, section text)}."""
    bf, bl, tc, ks, sz, kt = v
    bt = B_TW_FRONT
    out = {}
    s_tw = s_scr = 0.0
    for z_ in ("+", "-"):
        N, Mi, Mj, L = res[f"top wall behind the lip, zone {z_}"]   # BK (x 10) -> TWR (x 14.35, the lip's back face)
        s_tw = max(s_tw, sig(N, Mj, B_TW_BACK, T_TW_BACK, KT_LIP_BACK))
        # the moment at x 10 runs on, unchanged, over the bulkhead to the M3 screw line (x 6.75): the screws hold the top
        # wall down there and the bulkhead's rear edge (x 3.5) bears; net section through the Ø3.6 hole, Kt 2
        s_scr = max(s_scr, sig(N, Mi, B_NET_SCREW, T_TW_BACK, 2.0))
    out["top wall behind the lip, at the lip's back face (x 14.35)"] = (
        s_tw, ALLOW_XY, "XY", f"{B_TW_BACK:.0f} per zone x {T_TW_BACK:.1f}, Kt {KT_LIP_BACK}")
    out["top wall over the bulkhead, through the M3 holes (x 6.75)"] = (
        s_scr, ALLOW_XY, "XY", f"{B_NET_SCREW:.1f} net per zone x {T_TW_BACK:.1f}, Kt 2 (hole)")
    if upper:
        N, Mi, Mj, L = res["plate leg"]                      # FF2 (z 35.25) -> PLT (z 48.5)
        M_apex = Mi + (Mj - Mi) * (z_apex - Z_WEB1) / L
        out["upper piece's plate at the web top (z 35.25, sharp inner corner)"] = (
            sig(N, Mi, B_PLATE_WEBTOP, T5, KT_SHARP), ALLOW_XY, "XY", f"b {B_PLATE_WEBTOP} x {T5:.0f}, Kt {KT_SHARP}")
        out[f"upper piece's plate beside slot A's V apex (z {z_apex:.1f}, r {P.APEX_R})"] = (
            sig(N, M_apex, B_PLATE_APEX, T5, KT_FILLET), ALLOW_XY, "XY", f"b {B_PLATE_APEX} x {T5:.0f}, Kt {KT_FILLET}")
        out["upper piece's plate at the top wall (z 48.5, r 2 fillet)"] = (
            sig(N, Mj, B_PLATE_TOP, T5, KT_FILLET), ALLOW_XY, "XY", f"b {B_PLATE_TOP} x {T5:.0f}, Kt {KT_FILLET}")
        N, Mi, Mj, L = res["top wall in front of the lip"]
        out["top wall in front of the lip (r 2 at the plate, sharp at the lip)"] = (
            max(sig(N, Mi, bt, C.TOP_T, KT_FILLET), sig(N, Mj, bt, C.TOP_T, KT_SHARP)), ALLOW_XY, "XY",
            f"b {bt} x {C.TOP_T:.0f}")
        N, Mi, Mj, L = res["post 2"]
        out["second tie's post under the lip (z 35.25..36.75)"] = (
            sig(N, max(abs(Mi), abs(Mj)), B_POST2, T_POST2, KT_SHARP), ALLOW_XY, "XY",
            f"{T_POST2:.0f} x {B_POST2}, Kt {KT_SHARP}")
        V = (Mj - Mi) / L                                    # shear in the post = horizontal force into the web
        M_web = abs(Mj) + abs(V) * (Z_WEB1 - C.ZS) + abs(N) * T_POST2 / 2
        out["second tie's web at the post (tension + bending)"] = (
            abs(V) / (TIE_W * WEB_H) + KT_SHARP * 6 * M_web / (TIE_W * WEB_H ** 2), ALLOW_XY, "XY",
            f"{TIE_W:.0f} x {WEB_H:.0f} (45-degree parts ignored), Kt {KT_SHARP}")
        N, Mi, Mj, L = res["lip 2"]
        out["lip root at the top wall above the second tie"] = (sig(N, Mi, bl, C.GUIDE_T, KT_SHARP), ALLOW_XY, "XY",
                                                                f"b {bl} x {C.GUIDE_T:.0f}, Kt {KT_SHARP}")
    if upper and "anchor" in res:
        # round 4: the anchor's reaction at the post's foot. Fx (x hold) and Fz (+ = the post lifts: screw tension)
        Fx, Fz = abs(res["anchor"][0]), res["anchor z"][0]
        # the post alone below the web (z 17.75..19.25): 8 thick along x, 9.26 wide at z 19, net of the Ø3.6 hole on its
        # centreline (probed: A 63.1 mm2, I_y 386 mm4); bending in the x-z plane over the 1.5 mm stub, Kt 2.5 at the web's
        # bottom corner; in print these stresses run along the layers
        M_f = Fx * (Z_WEB0 - Z_FOOT)
        out["second post's foot below the web (z 17.75..19.25), the anchor's reaction (round 4)"] = (
            max(Fz, 0.0) / POST_FOOT_A + KT_SHARP * M_f * (T_POST2 / 2) / POST_FOOT_I, ALLOW_XY, "XY",
            f"8 x 9.26 net of the Ø{D_HOLE:.1f} hole (A {POST_FOOT_A}, I {POST_FOOT_I}), Fx {Fx:.1f} N, lift {Fz:+.1f} N, "
            f"Kt {KT_SHARP}")
        out["second post's foot: shear across it (z 19.25)"] = (
            1.5 * Fx / POST_FOOT_A, ALLOW_XY * 0.5, "XY shear", f"A {POST_FOOT_A}, Fx {Fx:.1f} N")
        # M3 x 45 pull-out from the frame's Ø2.7 x 14 pilot: preload + the lift (the joint opens only past the preload)
        T_scr = (P_M3 if CUR_MODE == "held" else 0.0) + max(Fz, 0.0)    # slip modes: the preload has gone
        out[f"M3 x 45 anchor: pull-out from the frame's rail block ({L_ANCHOR:.2f} engaged), preload (if any) + lift"] = (
            T_scr / (math.pi * 3.0 * L_ANCHOR), SHEAR_Z, "Z shear (frame)",
            f"screw {T_scr:.0f} N, thread cylinder Ø3 x {L_ANCHOR:.2f}")
        # once the preload has gone, the shank bears on the post's hole (its -x wall, 2.2 to the post's face)
        out["anchor shank bearing on the post's hole after a slip (Ø3 x 2d)"] = (
            Fx / (3.0 * 6.0), BEARING, "bearing", f"Fx {Fx:.1f} N on Ø3 x 6")
        out["post's 2.2 mm wall behind the hole: tear-out on the layer planes (y = const in print)"] = (
            Fx / (2 * POST_WALL * 6.0), SHEAR_Z, "Z shear", f"Fx {Fx:.1f} N, 2 x {POST_WALL} x 6")
    N, Mi, Mj, L = res["lip 1"]
    out["lip root at the top wall above the first tie"] = (sig(N, Mi, B_LIP1, C.GUIDE_T, KT_SHARP), ALLOW_XY, "XY",
                                                           f"b {B_LIP1} x {C.GUIDE_T:.0f}, Kt {KT_SHARP}")
    N, Mi, Mj, L = res["post 1"]
    out["first tie's post under the lip (flush with the lip; sharp web-top corner below)"] = (
        sig(N, max(abs(Mi), abs(Mj)), B_POST1, C.GUIDE_T, KT_SHARP), ALLOW_XY, "XY",
        f"{C.GUIDE_T:.0f} x {B_POST1:.0f}, Kt {KT_SHARP}")
    V = (Mj - Mi) / L
    M_web = abs(Mj) + abs(V) * (Z_WEB1 - C.ZS)
    out["first tie's web at the post (tension + bending)"] = (
        abs(V) / (TIE_W * WEB_H) + KT_SHARP * 6 * M_web / (TIE_W * WEB_H ** 2), ALLOW_XY, "XY",
        f"{TIE_W:.0f} x {WEB_H:.0f}, Kt {KT_SHARP}")
    N, Mi, Mj, L = res["lower plate"]                        # LPW (z 19.25) -> LPS (z 3)
    out["lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2)"] = (
        max(sig(N, Mi, B_LOWER, T5, KT_SHARP), 2.0 * sig(N, Mj, B_LOWER - (HOLE_PR + 0.2), T5, 1.0)), ALLOW_XY, "XY",
        f"b {B_LOWER:.0f} x {T5:.0f}")
    S = abs(res["screw"][0])
    out[f"M2.5 x 16 at z 3: pull-out from the frame ({L_M25:.0f} engaged)"] = (
        S / (math.pi * 2.5 * L_M25), SHEAR_Z, "Z shear", f"screw force {S:.0f} N")
    out["same M2.5: pan head on the cover's front plate"] = (S / A_HEAD, BEARING, "XY comp",
                                                             f"Ø{HEAD_D:.0f} head on the Ø{HOLE_PR} teardrop, "
                                                             f"{A_HEAD:.1f} mm2; screw force {S:.0f} N")
    return out


def _combine(r1, f1, r2, f2):
    """Member results r1 x f1 + r2 x f2 (linear superposition of two solves; L from r1)."""
    out = {}
    for k, v in r1.items():
        if k == "_u":
            out[k] = {n: tuple(f1 * a + f2 * b for a, b in zip(v[n], r2["_u"][n])) for n in v}
        else:
            w = r2[k]
            out[k] = (f1 * v[0] + f2 * w[0], f1 * v[1] + f2 * w[1], f1 * v[2] + f2 * w[2], v[3])
    return out


def anchored(load_node, R, v, mode):
    """Solve the as-built cover under R for one variant and one anchor mode:
    'held'   the preload's friction holds the post's foot in x from the start (round 3's what-if);
    'slip g' the preload has crept away: the foot slides freely (z still held) until it has moved g mm, then the shank
             bears (3 kN/mm). Linear in each phase, so the two solves superpose. Returns (res, R carried before bearing)."""
    global ANCHOR_KX, CUR_MODE
    CUR_MODE = mode
    if not ANCHOR2 or mode == "held":
        ANCHOR_KX = K_ANCHOR_X
        return cover_frame(load_node, R, *v), 0.0
    g = float(mode.split()[1])
    ANCHOR_KX = 0.0
    free1 = cover_frame(load_node, 1.0, *v)               # per newton, foot sliding
    ANCHOR_KX = K_ANCHOR_X
    dx1 = abs(free1["_u"]["AN"][0])
    R_g = R if dx1 * R <= g else g / dx1
    if R_g >= R:
        return _combine(free1, R, free1, 0.0), R
    held1 = cover_frame(load_node, 1.0, *v)
    return _combine(free1, R_g, held1, R - R_g), R_g


CUR_MODE = "held"
ANCHOR_MODES = ("held", f"slip {GAP_NOM:.2f}", f"slip {GAP_MAX:.2f}") if ANCHOR2 else ("held",)


def cover_rows(case, load_node, R, req, rows=ROWS, variants=None, modes=None):
    worst = {}
    for mode in (ANCHOR_MODES if modes is None else modes):
        for v in (VARIANTS if variants is None else variants):
            res, _ = anchored(load_node, R, v, mode)
            for k, (s, a, d, sec) in cover_sections(res, v, load_node == "LD2").items():
                if k not in worst or s / a > worst[k][0] / worst[k][1]:
                    am = "" if not ANCHOR2 else ("; anchor held by its preload" if mode == "held" else
                                                 f"; anchor preload gone, {mode.split()[1]} mm slip")
                    worst[k] = (s, a, d, f"{sec} [{vlabel(v)}{am}]")
    for k, (s, a, d, sec) in worst.items():
        row(f"{case}: {k}", sec, d, s, a, req, rows)


def strip_rows(case, R, lever, e_edge, label, req, rows=ROWS):
    """Plate strip loaded by the cocked rack's end, cantilevered from its tie's web (45-degree spread from the patch).
    lever/depth ~0.4: beam theory with Kt 2.5 on top is conservative for so short a stub."""
    b = PATCH + lever + min(lever, e_edge)
    return row(f"{case}: {label}", f"cantilever {lever:.2f} from the web, b_eff {b:.2f} x {T5:.0f}, Kt {KT_SHARP} (shear "
               f"{1.5 * R / (b * T5):.2f} MPa)", "XY", KT_SHARP * 6 * R * lever / (b * T5 ** 2), ALLOW_XY, req, rows)


lev_s2 = Z_WEB0 - z_rb                                    # 2.07: rack B's teeth resultant to the second tie's web
lev_s1 = z_ra - Z_WEB1                                    # 2.08: rack A's teeth resultant to the first tie's web
e_closed_b = C.HALF_Y - (-C.RACK_Y[0])                    # rack B's +y end at 25.1 closed: 6.9 from the plate's edge
e_closed_a = C.HALF_Y + C.RACK_Y[0]                       # rack A's -y end at -25.1 closed: 6.9 from the edge
for jaw, node, lab, lev_s, e_cl in (("B", "LD2", "plate strip under the second tie's web", lev_s2, e_closed_b),
                                    ("A", "LD1", "plate strip above the first tie's web", lev_s1, e_closed_a)):
    piece = "upper piece's bottom strip" if jaw == "B" else "lower piece's top strip"
    for case, R in ((f"crash {F_CRASH:.0f} N pushes jaw {jaw} shut, jaws 44 open: rack {jaw} pushes the {piece} at the "
                     f"cover's edge, R {R_co:.1f} N", R_co),
                    (f"added: opening against an obstacle, jaw {jaw}, jaws 44 open: R {R_go:.1f} N on the {piece}", R_go),
                    (f"handling: {F_HAND:.0f} N pushes jaw {jaw} shut, jaws 44 open: R {R_hand:.1f} N", R_hand)):
        strip_rows(case, R, lev_s, 0.0, lab, SF_SHORT)
        cover_rows(case, node, R, SF_SHORT)
    strip_rows(f"added: opening against an obstacle, jaw {jaw}, jaws closed: rack {jaw}'s end 6.9 from the edge, R "
               f"{R_gc:.1f} N", R_gc, lev_s, e_cl, lab, SF_SHORT)


# without the second tie (round 2's model, the upper piece hanging from the top wall only): information
for sec, z, b in ((f"beside slot A's V apex (z {z_apex:.1f})", z_apex, B_PLATE_APEX),
                  (f"top-wall junction (z {C.Z_TOP0})", C.Z_TOP0, B_PLATE_TOP)):
    row("info: opening stall on jaw B, upper piece WITHOUT the second tie (round 2's model)",
        f"{sec}: b {b} x {T5:.0f}, lever {z - z_rb:.1f}, Kt {KT_FILLET}", "XY",
        KT_FILLET * 6 * R_go * (z - z_rb) / (b * T5 ** 2), ALLOW_XY, SF_SHORT, INFO)
# bound: the two zones' corners joined rigidly in rotation (one 2-D frame for the whole cover): information only
_rigid = [v[:5] + (None,) for v in VARIANTS if v[5] == K_T_LO]
_bound = []
cover_rows("info, bound: opening stall on jaw B with the corners rigidly coupled", "LD2", R_go, SF_SHORT, rows=_bound,
           variants=_rigid)
INFO.extend(r for r in _bound if "first tie's post" in r[0] or "lip root at the top wall above the first" in r[0])

# grip: rack B's -y end pushes the lower piece forward at z 6..18.1 (rack B's whole front face): all of it on ONE M2.5
# (the lower piece pivots on the wrist plate's bottom edge, the screw 3 mm above it; the tie and the second screw ignored)
z_rbg = (C.T_W + (C.ZS - C.RACK_TIP)) / 2                 # 12.05: mid-height of rack B's front face
T_g = R_go * z_rbg / C.FRONT_SCREWS[0][1]
row(f"stall, one jaw blocked, jaws 44 open: rack B's -y end pushes the lower piece forward ({R_go:.1f} N at z "
    f"{z_rbg:.1f}): one M2.5 holds it, {T_g:.0f} N", f"pan head Ø{HEAD_D:.0f} on the Ø{HOLE_PR} teardrop, {A_HEAD:.1f} mm2",
    "XY comp", T_g / A_HEAD, BEARING, SF_SHORT)
# the plate between that screw (z 3) and the first tie's web (z 19.25), loaded at z 12 at the cover's -y edge
a_, b_ = z_rbg - C.FRONT_SCREWS[0][1], Z_WEB0 - z_rbg
M_pl = R_go * a_ * b_ / (a_ + b_)
b_pl = PATCH + min(a_, b_)
row(f"stall, one jaw blocked: the same push on the lower piece's plate between the screw (z 3) and the web (z 19.25)",
    f"simply supported, b_eff {b_pl:.1f} x {T5:.0f} (one-sided spread at the edge)", "XY", 6 * M_pl / (b_pl * T5 ** 2),
    ALLOW_XY, SF_SHORT)

# ================================================================ 4. strip under slot B (beam along y, across the layers)
ZB0 = C.ZS - C.NECK_Z[1] - C.SLOT_CLR                    # 5.75
STRIP_D = ZB0 - C.FRONT_Z0                               # 11.75 (FRONT_Z0 -6)


def strip_moments(Fs, y0, y1, n=40):
    """Propped cantilever: fixed at slot B's closed end (y -SLOT_B_END), pinned at the M2.5 at y +24, overhang to +32.
    Uniform load Fs over the neck's y range [y0, y1] (clipped to the plate). Returns (M at the fixed end, M at the screw)."""
    yA, yB = -C.SLOT_B_END, C.FRONT_SCREWS[1][0]
    L = yB - yA
    MA = MB = 0.0
    y0, y1 = max(y0, yA), min(y1, C.HALF_Y)
    for k in range(n):
        y = y0 + (y1 - y0) * (k + 0.5) / n
        p = Fs / n
        if y <= yB:
            a, b = y - yA, yB - y
            MA += p * a * b * (L + b) / (2 * L * L)
        else:
            c = y - yB
            MB += p * c
            MA += p * c / 2
    return MA, MB


# A -z push on jaw B's tip pitches the jaw nose-down; the strip carries the most when the rack has lifted off the wrist
# plate and the jaw pivots on the strip's front edge (x X_F1) while the pinion holds the rack's rear end (past its bed
# chamfer): S = F (X_TIP - x_r) / (X_F1 - x_r). With the rack on the plate and a rigid pinion the strip carries nothing.
X_REAR = C.X_P0 + JAW_BED_CHAMFER
lever_strip = (C.X_TIP - X_REAR) / (C.X_F1 - X_REAR)


def strip_sf(depth, F, y0, y1):
    Zs = T5 * depth ** 2 / 6
    MA, MB = strip_moments(lever_strip * F, y0, y1)
    dn = depth - (C.M25_CLEAR + P.HOLE_COMP)
    return max(1.7 * MA / Zs, 2.0 * 6 * MB / (T5 * dn ** 2))


for name, F in ((f"yaw stall {F_YAW_Z:.1f} N", F_YAW_Z), (f"hand push {F_HAND:.0f} N", F_HAND)):
    for pos, (y0, y1) in (("jaws closed", (0.0, C.NECK_Y)), ("jaws 44 open", (C.STROKE, C.STROKE + C.NECK_Y))):
        row(f"{name} on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to "
            f"{lever_strip * F:.0f} N (x{lever_strip:.2f}: the rack lifted off the plate, the pinion holding its rear), "
            f"{pos}", f"strip {STRIP_D:.2f} x {T5:.0f}: slot end (Kt 1.7) / through the screw hole (Kt 2)", "Z",
            strip_sf(STRIP_D, F, y0, y1), ALLOW_Z, SF_SHORT)

# ================================================================ 5. top wall
F_sep = F1 * math.tan(math.radians(20))
M_twist = F1 * ((C.ZS + C.R_P) - (C.ZS - 9.0))
R_lift = F_sep / 2 + M_twist / SPAN_OPEN
span_tw = C.X_F0 - C.RAIL_X1
M_tw = R_lift * span_tw / 8
b_tw = 2 * span_tw
row(f"rack A lift: separating {F_sep:.1f} N + grip twist {M_twist:.0f} N.mm -> {R_lift:.1f} N at the rack end",
    f"top wall between the lip and the front plate, span {span_tw:.1f}, b {b_tw:.0f} x {C.TOP_T:.0f}", "XY",
    KT_SHARP * 6 * M_tw / (b_tw * C.TOP_T ** 2), ALLOW_XY, SF_SHORT)
M_tip = 10.0 * (C.CAM_ZC + 13.5 * math.cos(math.radians(C.CAM_TILT)) + 13.5 * math.sin(math.radians(C.CAM_TILT))
                - C.Z_TOP1)
F_edge = M_tip / (C.TOP_SCREWS[0][0] - C.PAD_X[0])
row(f"USB tug 10 N tips the camera mount back: {F_edge:.0f} N on the top wall's rear edge", "50 x 1 mm contact",
    "XY", F_edge / (C.MOUNT_Y[1] - C.MOUNT_Y[0]), BEARING, SF_SHORT)

# ================================================================ 6. the anchor (round 4), local rows
HOLE_TD = C.M3_CLEAR                                       # 3.4 printed (3.6 CAD teardrop)
A_TD_TIP = (HOLE_TD / 2) ** 2 * (1 - math.pi / 4)          # the teardrop's point, outside the circle


def head_area(od):
    return math.pi / 4 * (od ** 2 - HOLE_TD ** 2) - A_TD_TIP


if ANCHOR2:
    row(f"anchor M3 x 45 driven snug: socket head (dk {HEAD_DK}) on the top wall, preload {P_M3:.0f} N (sustained)",
        f"{head_area(HEAD_DK):.1f} mm2 round the Ø{HOLE_TD} teardrop, no washer (BUILD_GUIDE lists none)", "XY comp",
        P_M3 / head_area(HEAD_DK), BEARING, SF_CYCLIC)
    a_post = C.GUIDE_T * TIE_W - math.pi / 4 * D_HOLE ** 2
    row(f"anchor preload {P_M3:.0f} N through the stack (sustained): the 8 x 8 post round its Ø{D_HOLE:.1f} hole",
        f"{a_post:.0f} mm2 (the full-depth part only; the 45-degree part ignored)", "XY comp", P_M3 / a_post, ALLOW_XY,
        SF_CYCLIC)
    row(f"anchor preload {P_M3:.0f} N (sustained): M3 x 45 pull-out from the frame's rail block",
        f"thread cylinder Ø3 x {L_ANCHOR:.2f} (Ø2.7 x 14 pilot)", "Z shear (frame)",
        P_M3 / (math.pi * 3.0 * L_ANCHOR), SHEAR_Z, SF_CYCLIC)

# ================================================================ 7. spec §8 proof push (round 4: the anchored cover)
SF_PROOF = SF_SHORT / 1.5                                  # 2 at 1.5 x the service load (as every arm script)
F_PROOF, GAP_PROOF = 32.0, 30.0
SPAN_30 = (C.RACK_Y[1] - GAP_PROOF / 2) - (-C.HALF_Y)      # 48.4: rack end beyond the cover's edge at 30 mm open
R_proof = thrust(F_PROOF, X_GRIP, SPAN_30)
PROOF = []
for jaw, node in (("B", "LD2"), ("A", "LD1")):
    cover_rows(f"spec §8 proof 1: {F_PROOF:.0f} N pushes jaw {jaw} towards the other, jaws 30 open, R {R_proof:.1f} N",
               node, R_proof, SF_PROOF, rows=PROOF)
    strip_rows(f"spec §8 proof 1: jaw {jaw} pushed towards the other, R {R_proof:.1f} N",
               R_proof, lev_s2 if jaw == "B" else lev_s1, 0.0, "plate strip at the tie's web", SF_PROOF, rows=PROOF)
wall(f"spec §8 proof 1: {F_PROOF:.0f} N pulls a jaw away, jaws 30 open: rack A's -y end at the lip's end, R {R_proof:.1f} N",
     R_proof, 0.0, SF_PROOF, rows=PROOF)
wall(f"spec §8 proof 1: the same, rack A's +y end on the upper piece near slot A's end", R_proof, 0.0, SF_PROOF, t=T5,
     kt=KT_FILLET, lever=lev, label="front plate at the top wall", rows=PROOF)
for pos, (y0, y1) in (("jaws closed", (0.0, C.NECK_Y)), ("jaws 44 open", (C.STROKE, C.STROKE + C.NECK_Y))):
    row(f"spec §8 proof 2: 10.7 N on jaw B's tip towards the wrist, {pos}", f"strip {STRIP_D:.2f} x {T5:.0f}", "Z",
        strip_sf(STRIP_D, 10.7, y0, y1), ALLOW_Z, SF_PROOF, PROOF)
ROWS.extend(PROOF)


# ---------------------------------------------------------------- report
def table(rows, start=1):
    for i, (case, sec, d, s, a, sf, req) in enumerate(rows, start):
        ok = "OK" if sf >= req else "**FAIL**"
        print(f"| {i} | {case} | {sec} | {d} | {s:.2f} | {a:.2f} | {sf:.2f} | {req:.0f} | {ok} |")


print(f"cover: front plate {C.FRONT_T} (z {C.FRONT_Z0}..{C.Z_TOP0}), top wall {C.TOP_T}, lip {C.GUIDE_T} x {LIP_H} "
      f"(x {C.LIP_X0}..{C.RAIL_X1}); slot A z {ZA0}..{C.Z_TOP0} (V apex y {y_apex:.2f}), slot B z {ZB0}..{ZB1}; tie 1 "
      f"y {C.TIE_Y}, post {C.GUIDE_T} x {TIE_W}; tie 2 y {C.TIE2_Y}, post {T_POST2} x {B_POST2} (probed)")
print(f"rack thrust: grip one jaw {R_gc:.1f} (closed) / {R_go:.1f} N (open); crash {R_cc:.1f} / {R_co:.1f}; hand "
      f"{R_hand:.1f} (open)")
print(f"two-zone cover frame, opening stall R {R_go:.1f} N, over the {len(VARIANTS)} variants"
      + (", anchor held by its preload:" if ANCHOR2 else ":"))
for node, name in (("LD2", "rack B on the upper piece"), ("LD1", "rack A on the lower piece")):
    rs = [anchored(node, R_go, v, "held")[0] for v in VARIANTS]
    S = [abs(r["screw"][0]) for r in rs]
    P1 = [max(abs(r["post 1"][1]), abs(r["post 1"][2])) for r in rs]
    P2 = [max(abs(r["post 2"][1]), abs(r["post 2"][2])) for r in rs]
    print(f"  {name}: M2.5 force {min(S):.0f}..{max(S):.0f} N; first post moment {min(P1):.0f}..{max(P1):.0f} N.mm; "
          f"second post moment {min(P2):.0f}..{max(P2):.0f} N.mm")
if ANCHOR2:
    print(f"anchor (as built): M3 x 45 at {tuple(C.ANCHOR_XY)}, stack {STACK:.2f}, {L_ANCHOR:.2f} engaged; post foot z {Z_FOOT}")
    for node, name in (("LD2", "rack B on the upper piece"), ("LD1", "rack A on the lower piece")):
        for R, lab in ((R_go, "opening stall"), (R_co, "crash")):
            for mode in ANCHOR_MODES:
                out = [anchored(node, R, v, mode) for v in VARIANTS]
                A = [abs(r["anchor"][0]) for r, _ in out]
                Z = [r["anchor z"][0] for r, _ in out]
                Rg = [rg for _, rg in out]
                print(f"  {name}, {lab} {R:.1f} N, {mode:9s}: anchor x {min(A):5.1f}..{max(A):5.1f} N, z "
                      f"{min(Z):+5.1f}..{max(Z):+5.1f} N (+ = lift); push carried before the shank bears "
                      f"{min(Rg):.1f}..{max(Rg):.1f} N")
    fr = []
    for v in VARIANTS:
        ANCHOR_KX = 0.0
        fr.append(abs(cover_frame("LD2", 1.0, *v)["_u"]["AN"][0]))
    ANCHOR_KX = K_ANCHOR_X
    print(f"  foot sliding freely (preload gone): {min(fr) * 1000:.1f}..{max(fr) * 1000:.1f} um per N of rack-B push, so "
          f"{GAP_NOM:.2f} mm closes at {GAP_NOM / max(fr):.1f}..{GAP_NOM / min(fr):.1f} N and {GAP_MAX:.2f} mm at "
          f"{GAP_MAX / max(fr):.1f}..{GAP_MAX / min(fr):.1f} N (opening stall {R_go:.1f}, crash {R_co:.1f}, hand {R_hand:.1f})")
print("\n| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |")
print("|---|---|---|---|---|---|---|---|---|")
table(ROWS)
print("\nInformation rows (not in the verdict):")
table(INFO, start=len(ROWS) + 1)
worst = min(ROWS, key=lambda r: r[5] / r[6])
print(f"\nlowest SF {worst[5]:.2f} (required {worst[6]:.0f}): {worst[0]} / {worst[1]}")
print("VERDICT (calculation):", "FAIL" if any(r[5] < r[6] for r in ROWS) else "NEEDS_TEST (placeholder allowables)")

# ---------------------------------------------------------------- what-if lines
print("\nWhat-if, M2.5 screw force -> pan-head bearing / frame pull-out (and with a Ø6 washer under the head):")
for T_s in (50.0, 80.0, 108.0, 134.0):
    print(f"  {T_s:.0f} N: head SF {BEARING / (T_s / A_HEAD):.2f}, washer SF "
          f"{BEARING / (T_s / (math.pi / 4 * (6.0 ** 2 - HOLE_PR ** 2))):.2f}, pull-out SF "
          f"{SHEAR_Z / (T_s / (math.pi * 2.5 * L_M25)):.2f}")


def reversed_worst(variants=None, modes=("held",)):
    """Worst SF over every frame-model section, both reversed pushes (opening stall and crash), all variants and anchor
    modes; and the best variant's own worst SF (how the most favourable joint assumptions do)."""
    worst, per_v = (9e9, ""), {}
    for node in ("LD2", "LD1"):
        for R in (R_go, R_co):
            for mode in modes:
                for v in (VARIANTS if variants is None else variants):
                    res, _ = anchored(node, R, v, mode)
                    for k, (s, a, d, sec) in cover_sections(res, v, node == "LD2").items():
                        sf = a / s
                        per_v[v] = min(per_v.get(v, 9e9), sf)
                        if sf < worst[0]:
                            worst = (sf, f"{k}, {mode}")
    return worst, max(per_v.values())


print("\nWhat-if, the cover's moment path to the frame (reversed pushes, worst of all frame-model sections and variants):")
_saveA = ANCHOR2
ANCHOR2 = False
(sf, k), best = reversed_worst()
print(f"  {'round 3 for reference: no anchor (post 2 as built, 8 thick, not seated)':78s}: lowest SF {sf:.2f} ({k}); "
      f"most favourable variant {best:.2f}")
ANCHOR2 = _saveA
if ANCHOR2:
    for modes in (("held",), (f"slip {GAP_NOM:.2f}",), (f"slip {GAP_MAX:.2f}",)):
        (sf, k), best = reversed_worst(modes=modes)
        print(f"  {'as built, anchor ' + modes[0]:78s}: lowest SF {sf:.2f} ({k}); most favourable variant {best:.2f}")
    print(f"What-if, the anchor's head on the top wall at the {P_M3:.0f} N preload (sustained, req 4):")
    for lab, od in ((f"bare socket head dk {HEAD_DK}", HEAD_DK), (f"+ M3 washer Ø{WASHER_M3[0]:g} x {WASHER_M3[1]:g}",
                                                                     WASHER_M3[0])):
        L_w = L_ANCHOR - (WASHER_M3[1] if od == WASHER_M3[0] else 0.0)
        print(f"  {lab:32s}: bearing SF {BEARING / (P_M3 / head_area(od)):.2f}; pull-out on the preload SF "
              f"{SHEAR_Z / (P_M3 / (math.pi * 3.0 * L_w)):.2f} ({L_w:.2f} engaged)")
    print(f"  preload that a bare head carries at SF 4: {BEARING / 4 * head_area(HEAD_DK):.0f} N")
    # what the 'held' mode asks of the preload: clamp left at the seat = preload - lift, friction mu x that >= Fx
    print("What-if, the clamp the seat's friction needs to hold the foot (preload - lift >= Fx / mu), worst variant:")
    for R, lab in ((R_go, "opening stall"), (R_co, "crash"), (R_proof, "spec §8 proof push")):
        out = [anchored("LD2", R, v, "held")[0] for v in VARIANTS]
        need = max(abs(r["anchor"][0]) / 0.3 + max(r["anchor z"][0], 0.0) for r in out)
        need2 = max(abs(r["anchor"][0]) / 0.2 + max(r["anchor z"][0], 0.0) for r in out)
        print(f"  {lab:20s} R {R:5.1f} N: preload >= {need:.0f} N at mu 0.3, {need2:.0f} N at mu 0.2 (snug assumed {P_M3:.0f} N)")
    print("What-if, residual radial gap at the foot once the preload has gone (both reversed pushes, all variants):")
    for gap in (0.0, 0.025, 0.04, 0.05, 0.075, 0.1):
        (sf, k), best = reversed_worst(modes=(f"slip {gap}",))
        print(f"  gap {gap:5.3f} mm: lowest SF {sf:.2f} ({k})")
    # the FIX: a 90-degree V-seat beside the anchor, so the foot is held in x by geometry and the screw's tension, not by
    # friction. The frame's rail block gets a V-groove along y in its top: centre x 15.25, 0.8 deep (x 14.45..16.05 at the
    # block top z 17.75, bottom z 16.95), y 23.5..32 (open at +y), 0.95 of block between its edge and the anchor pilot at
    # the top. The post's foot gets the matching V-ridge (the same flanks; tip truncated 0.15 at z 17.10, so it never
    # bottoms; x 14.35..16.15 where it meets the foot's flats), y 24..32 with a 45-degree lead-in over its first 0.8 (the
    # post's underside); the foot's flats rise 0.1 (TIE2_FOOT_Z 17.85) so the flanks seat, not the flats. A +x push on the
    # foot rides up a 45-degree flank: the screw holds it in tension (positive: no friction or preload needed); Fz added =
    # Fx (frictionless, the worst case). The anchor pilot and the M3 x 45 do not change.
    V_D, V_TRUNC, V_X0 = 0.8, 0.15, C.LIP_X0 + 0.1          # groove x 14.45..16.05 at the block top
    L_V = (C.TIE2_Y[1] - C.TIE2_Y[0]) - V_D                 # 7.2: full-depth ridge, y 24.8..32
    print(f"What-if, the FIX: 90-degree V-seat beside the anchor (x {V_X0:.2f}..{V_X0 + 2 * V_D:.2f}, {V_D} deep, along y "
          f"over the post's foot): x held positively (gap 0); M3 x 45 + Ø7 x 0.5 washer:")
    (sf, k), best = reversed_worst(modes=("slip 0.0",))
    print(f"  cover frame model, both reversed pushes, all variants: lowest SF {sf:.2f} ({k}); most favourable {best:.2f}")
    outs = [anchored(n, R, v, "slip 0.0")[0] for n in ("LD2",) for R in (R_go, R_proof) for v in VARIANTS]
    Fx_max = max(abs(r["anchor"][0]) for r in outs[:len(VARIANTS)])
    Fz_max = max(max(r["anchor z"][0], 0.0) for r in outs[:len(VARIANTS)])
    Fx_pr = max(abs(r["anchor"][0]) for r in outs[len(VARIANTS):])
    flank = (V_D - V_TRUNC) * math.sqrt(2)                  # 0.92 of flank on each side
    N_fl = Fx_max * math.sqrt(2)                            # all on one 45-degree flank, frictionless
    s_fl = N_fl / (flank * L_V)
    s_root = 1.5 * Fx_max / (2 * V_D * L_V)                 # ridge root on the post's foot: in print a vertical plane
    plug = (C.RAIL_X1 - (V_X0 + 2 * V_D)) * L_V - math.pi / 4 * (C.M3_PILOT + P.HOLE_COMP) ** 2
    s_plug = 1.5 * Fx_max / plug                            # the frame's block in front of the groove, sheared off its
    L45 = L_ANCHOR - WASHER_M3[1]                           # layers at the groove's bottom (interlayer, 6.25)
    T45 = P_M3 + Fx_max + Fz_max
    print(f"  anchor Fx {Fx_max:.1f} N, lift {Fz_max:.1f} N (opening stall); Fx {Fx_pr:.1f} N at the spec §8 proof push")
    print(f"  flank bearing {s_fl:.2f} MPa on {flank:.2f} x {L_V:.1f}: SF {BEARING / s_fl:.1f} (req 3); ridge root 1.5 V / A "
          f"{s_root:.2f} MPa along the layers: SF {ALLOW_XY / 2 / s_root:.1f}; the frame's block in front of the groove, "
          f"{plug:.0f} mm2 at the groove's bottom, interlayer: SF {SHEAR_Z / s_plug:.1f}")
    print(f"  M3 x 45 + washer: {L45:.2f} engaged; pull-out on the preload SF {SHEAR_Z / (P_M3 / (math.pi * 3.0 * L45)):.2f} "
          f"(req 4); preload + wedge lift + lift {T45:.0f} N: SF {SHEAR_Z / (T45 / (math.pi * 3.0 * L45)):.2f} (req 3); head "
          f"on the washer SF {BEARING / (P_M3 / head_area(WASHER_M3[0])):.2f} (req 4); the ridge's x play after seating = the "
          f"stack's creep under the head (gap <= 0.025 keeps every row >= 4.5)")
print("What-if, strip under slot B (yaw stall, the worse of closed / open):")
for d in (STRIP_D - 2.0, STRIP_D - 1.0, STRIP_D, STRIP_D + 2.0):
    w = max(strip_sf(d, F_YAW_Z, 0.0, C.NECK_Y), strip_sf(d, F_YAW_Z, C.STROKE, C.STROKE + C.NECK_Y))
    print(f"  strip {d:.2f} deep (FRONT_Z0 {ZB0 - d:+.0f}): SF {ALLOW_Z / w:.2f}")

"""Strength check, round 3: jobs/20261026-arm-claw-cover (front plate in two pieces + two ties, top wall, 8 mm lip).

Run from the project root:  python3 jobs/20261026-arm-claw-cover/strength_calc.py
Plain python3: parameters come from claw_frame.py, this job's model.py, the jaw's model.py and tools/hobby_parts.py
(ast module). No build123d needed. Section widths quoted as "probed" were measured on the round 3 solid (design())
with thin slabs; the script states them as numbers so it runs without the CAD venv.

The cover prints standing on its -y end: print Z = claw y. Bending of the front plate, the top wall, the lip, the posts
and the webs in the side profile (stresses along claw x or z) runs along the layers (25 MPa); beams along claw y (the
strip under slot B) bend across them (12.5 MPa). Placeholder PETG allowables (no library row): NEEDS_TEST at best.

The pinion pass-through and the two open-ended slots cut the front plate into two pieces:
  upper piece  y > ~7 (and over slot A's closed end): hangs from the top wall and, since round 3, is tied to the lip by
               the second tie (post 4 thick + web, full at y 24..32, 45-degree undersides growing from the lip and from
               the plate down to y ~8);
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
B_POST2 = 24.3
B_TW_FRONT = 25.5
T_POST2 = P.TIE2_POST_T                                   # 4
ANCHOR2 = False                                           # what-if: second post seated + screwed on the rail block
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
    return out


RIGID = 1e5
PENALTY = 1e9


def cover_frame(load_node, R, b_front, b_lip2, top_clamped, k_screw, screw_z, k_t):
    """The cover as a two-zone frame; R (+x) at load_node ('LD2' upper piece, 'LD1' lower piece). k_t None = the two
    corners joined rigidly (one 2-D frame)."""
    xl = (C.LIP_X0 + C.RAIL_X1) / 2                       # 18.35: lip (and first post) centreline
    xp2 = C.RAIL_X1 - T_POST2 / 2                         # 20.35: second post centreline
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
               mem("LTa", "L2B", C.GUIDE_T, b_lip2, "lip 2"), mem("L2B", "P2T", T_POST2, B_POST2, "r4", True),
               mem("P2T", "P2B", T_POST2, B_POST2, "post 2"), mem("P2B", "FF2", WEB_H, TIE_W, "r5", True),
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
        # what-if fix: the second post seated on the frame's rail block top (z 17.75) and clamped by a vertical M3: the
        # foot is held there in x (preload friction + shank, through a 3 kN/mm spring) and z
        nodes.update({"AN": (xp2, C.ZS - C.RAIL_IN), "GA": (xp2 - 10.0, C.ZS - C.RAIL_IN),
                      "GZ": (xp2, C.ZS - C.RAIL_IN - 10.0)})
        members += [mem("P2B", "AN", WEB_H, TIE_W, "r11", True), ("AN", "GA", 3000.0 * 10.0, 1e-6, "anchor"),
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


def cover_rows(case, load_node, R, req, rows=ROWS, variants=None):
    worst = {}
    for v in (VARIANTS if variants is None else variants):
        res = cover_frame(load_node, R, *v)
        for k, (s, a, d, sec) in cover_sections(res, v, load_node == "LD2").items():
            if k not in worst or s / a > worst[k][0] / worst[k][1]:
                worst[k] = (s, a, d, f"{sec} [{vlabel(v)}]")
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
print(f"two-zone cover frame, opening stall R {R_go:.1f} N, over the {len(VARIANTS)} variants:")
for node, name in (("LD2", "rack B on the upper piece"), ("LD1", "rack A on the lower piece")):
    rs = [cover_frame(node, R_go, *v) for v in VARIANTS]
    S = [abs(r["screw"][0]) for r in rs]
    P1 = [max(abs(r["post 1"][1]), abs(r["post 1"][2])) for r in rs]
    P2 = [max(abs(r["post 2"][1]), abs(r["post 2"][2])) for r in rs]
    print(f"  {name}: M2.5 force {min(S):.0f}..{max(S):.0f} N; first post moment {min(P1):.0f}..{max(P1):.0f} N.mm; "
          f"second post moment {min(P2):.0f}..{max(P2):.0f} N.mm")
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


def reversed_worst(variants=None):
    """Worst SF over every frame-model section, both reversed pushes (opening stall and crash), all variants; and the
    best variant's own worst SF (how the most favourable joint assumptions do)."""
    worst, per_v = (9e9, ""), {}
    for node in ("LD2", "LD1"):
        for R in (R_go, R_co):
            for v in (VARIANTS if variants is None else variants):
                res = cover_frame(node, R, *v)
                for k, (s, a, d, sec) in cover_sections(res, v, node == "LD2").items():
                    sf = a / s
                    per_v[v] = min(per_v.get(v, 9e9), sf)
                    if sf < worst[0]:
                        worst = (sf, k)
    return worst, max(per_v.values())


print("\nWhat-if, the cover's moment path to the frame (reversed pushes, worst of all frame-model sections and variants):")
_save = (T_TW_BACK, B_POST1, KT_LIP_BACK)
for name, t, bp, kl in (("as built: top wall 3 behind the lip, first post 8 x 8, sharp lip corner", 3.0, 8.0, KT_SHARP),
                        ("top wall 5 behind the lip", 5.0, 8.0, KT_SHARP),
                        ("top wall 6 behind the lip", 6.0, 8.0, KT_SHARP),
                        ("top wall 6 behind the lip, first post 8 x 14 (y -32..-18)", 6.0, 14.0, KT_SHARP),
                        ("top wall 6 behind the lip + r 2 at the lip's back corner, first post 8 x 14", 6.0, 14.0,
                         KT_FILLET),
                        ("top wall 7 behind the lip, first post 8 x 14", 7.0, 14.0, KT_SHARP)):
    T_TW_BACK, B_POST1, KT_LIP_BACK = t, bp, kl
    (sf, k), best = reversed_worst()
    print(f"  {name:78s}: lowest SF {sf:.2f} ({k}); most favourable variant {best:.2f}")
T_TW_BACK, B_POST1, KT_LIP_BACK = _save
# the anchored second post: TIE2_POST_T 4 -> 8 (x 14.35..22.35, like the first), down to the rail block's top (z 17.75)
_save2 = T_POST2
for name, t2 in (("second post 8 thick, seated on the rail block + vertical M3 (anchored)", 8.0),):
    T_POST2, ANCHOR2 = t2, True
    (sf, k), best = reversed_worst()
    rs = [cover_frame("LD2", R_go, *v) for v in VARIANTS]
    A = [abs(r["anchor"][0]) for r in rs]
    Z = [r["anchor z"][0] for r in rs]                   # + tension: the post pulls up on the screw
    print(f"  {name:78s}: lowest SF {sf:.2f} ({k}); most favourable variant {best:.2f}")
    print(f"    anchor under the opening stall ({R_go:.1f} N): x {min(A):.1f}..{max(A):.1f} N, z {min(Z):+.1f}..{max(Z):+.1f} N "
          f"(+ = lift, taken by the screw)")
    # the anchor's own checks: M3 snug preload 150 N (assumption, 'snug only' as every M3 here); friction 0.3 holds x
    P_M3 = 150.0
    lift = max(0.0, max(Z))
    stack = C.Z_TOP1 - (C.ZS - C.RAIL_IN)                # 33.75: top wall + lip + post, top to the rail block
    L_eng = 45.0 - stack                                  # M3 x 45 socket head: 11.25 in a 14 mm pilot
    A_th = math.pi * 3.0 * L_eng
    print(f"    friction {0.3 * P_M3:.0f} N >= x {max(A):.1f} N: {'yes' if 0.3 * P_M3 >= max(A) else 'NO (shank bearing)'}; "
          f"M3 x 45 through the {stack:.2f} mm stack, {L_eng:.2f} engaged in a Ø2.7 x 14 pilot in the rail block: "
          f"pull-out SF {SHEAR_Z / (P_M3 / A_th):.2f} on the preload (req 4, sustained), "
          f"{SHEAR_Z / ((P_M3 + lift) / A_th):.2f} with the lift (req 3)")
    a_post = C.GUIDE_T * TIE_W - math.pi / 4 * (C.M3_CLEAR + P.HOLE_COMP) ** 2
    print(f"    the 8 x 8 post round its Ø{C.M3_CLEAR + P.HOLE_COMP:.1f} hole under the clamp ({a_post:.0f} mm2): "
          f"{P_M3 / a_post:.2f} MPa, SF {ALLOW_XY / (P_M3 / a_post):.1f} (req 4, sustained, along the layers)")
T_POST2, ANCHOR2 = _save2, False
print("What-if, strip under slot B (yaw stall, the worse of closed / open):")
for d in (STRIP_D - 2.0, STRIP_D - 1.0, STRIP_D, STRIP_D + 2.0):
    w = max(strip_sf(d, F_YAW_Z, 0.0, C.NECK_Y), strip_sf(d, F_YAW_Z, C.STROKE, C.STROKE + C.NECK_Y))
    print(f"  strip {d:.2f} deep (FRONT_Z0 {ZB0 - d:+.0f}): SF {ALLOW_Z / w:.2f}")

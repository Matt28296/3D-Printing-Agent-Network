"""Strength check, round 7 CAD ENGINEER'S SELF-CHECK on the round 6 INDEPENDENT REVIEW's script: jobs/20261026-arm-claw-cover

Round 7 (cad-engineer's self-check, not an independent review): the round 6 review's fix, user-approved. Every cover screw
now has a washer under its head: top (no camera) M3 x 14 pan head + ISO 7089 Ø7 x 0.5 (claw_frame.TOP_WASHER; it was a
bare M3 x 10), front M2.5 x 16 pan head + DIN 125 Ø6 x 0.5 (claw_frame.FRONT_WASHER) with FRONT_SCREWS z 3 -> 2.5 so the
washer clears jaw B's neck, and a 0.3 x 45° chamfer on each slot's front edge nearer the axis (no strength effect). In
this script: the top-screw head rows bear on the Ø7 washer (A_M3_TOP), the M2.5 head rows on the Ø6 washer (A_BRG), the
M2.5 engagement is 16 - 5 - 0.5 = 10.5 (L_M25), the stall's screw force follows z 2.5 (130 N), the forced-closure info rows
take the washer's OD into b_eff; the round 6 bare-head rows and the camera case (M3 x 18 bare button heads on the camera
mount's pad) are kept as information rows. Everything else is the reviewer's script, unchanged.

Round 6, INDEPENDENT REVIEW (strength-analyst; did not design the part): jobs/20261026-arm-claw-cover
(front plate in two pieces + two ties, top wall, 8 mm lip, the second tie's 8 mm post located on the frame's rail block by
a 90° V-ridge in a V-groove and anchored there by one vertical M3 x 45 with a Ø7 x 0.5 washer under its head).

Round 6 design (ridge-first contact): VSEAT_CLR 0 (virtual apex 16.95), the foot's flats at 18.05 (FOOT_CLR 0.30), the
ridge's flanks carried up to them, its tip at 17.35, the frame's bulkhead top at 48.45. The CAD engineer's round-6 update
of this file was a self-check; this version recomputes it.

What this review changes or adds (every number below is recomputed here; slice facts from the reviewer's own slice):
- SLICE FACTS, read back from the reviewer's own scratch slice of both committed part.stl files with the arm's command
  (PrusaSlicer 2.7.2, Arachne, 0.20mm QUALITY @MK3, Prusament PETG, each job's slice_overrides.ini):
  frame: bulkhead and both ribs end at ;Z:48.4, rail block top 17.8 (both sides of the groove, and at -y), groove walls
  at half-widths 0.15 / 0.35 / 0.55 / 0.75 in the layers ending 17.2 / 17.4 / 17.6 / 17.8 (external perimeters
  14.875/15.625, 14.675/15.825, 14.475/16.025, 14.275/16.225, w 0.45), the layer below 17.0 solid; the 17.0..17.2 layer
  is an OPEN 0.3 mm slot between two external perimeters, so the groove's floor is 17.0 at |x - 15.25| < 0.15 and 17.2 at
  0.15..0.35 (the tip faces the latter).
  cover: ridge flanks, tip (17.35) and flats (18.05) print to CAD (external perimeter 0.225 inside each face); the
  0.2 x 0.2 bump behind the post's back face does NOT print (the outline runs from the flank straight onto the post's
  face), so the ridge's root is 2.0 wide (x 14.35..16.35), not 2.2; the top wall's underside is at 48.5.
- THE SEAT STACK. The round-6 self-check put no tolerance on the bulkhead's printed top or on the tip / slot surfaces.
  With +-0.05 on EVERY printed surface (the brief), plus the ridge flank +-0.05 normal (+-0.0707 vertical) and corner
  radius 0.05..0.10, the ridge lands first at nominal and RSS (play 0); the worst case is 0.079 by the top wall (which
  BUILD_GUIDE §4 step 9's 0.03 feeler rejects) and 0.029 by the tip on the groove's 17.2 layer (which no feeler can
  see). Verdict rows: 'locked' (play 0) and the worst ACCEPTED play 0.029, the worse of the two.
- WHICH CORNERS CARRY. Seated 0.056 above its CAD seat, the ridge's tip is at 17.406: the groove's 17.4 corner (its
  tangent point at z 17.378) lies beyond the tip, so only the 17.6 and 17.8 corners carry at first contact (the self-check
  counted 3 and took the band from the CAD tip). The anchor's 150 N then crushes them until the 17.4 corner joins; the
  band and the resultant are taken after that seating, with a flow stress of 80 MPa (2 x the self-check's 40: the
  SMALLEST crush, so the narrowest band). The resultant stays at the two upper corners (z 17.7): arm 0.5 Fx about
  the printed root's centroid (x 15.35; the root is 2.0 wide).
- THE TOP JOINT. Reactions are now read from the frame model (frame2d returns them), so the top M3s' real tension under
  every reversed push is computed; the frame's 'all of the moment on the top screws' row is reduced to information.
- SNUG PRELOADS, SUSTAINED (the project's rule: the anchor here, the ring, the links): new rows for the top M3 pan heads
  on the top wall (no washer) and the front M2.5 pan heads on the front plate, at the snug preloads the arm uses (M3
  150 N, M2 / M2.5 100 N).
- THE FORCED CLOSURE. The top wall stands 0.06..0.10 proud of the printed bulkhead after the anchor seats it (more at
  RSS); the top M3s pull it down by bending the top wall behind the lip. Information rows (displacement-controlled, it
  relaxes), with numbers.

Run from the project root:  python3 jobs/20261026-arm-claw-cover/strength_calc.py
Plain python3: parameters come from claw_frame.py, this job's model.py, the jaw's model.py and tools/hobby_parts.py
(ast module). No build123d needed. Section widths quoted as "probed" were measured on the round 3 solid (design())
with thin slabs, and the second post's on the round 4 / round 6 solid; the script states them as numbers so it runs
without the CAD venv.

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
               (2 x M2.5 x 16 + Ø6 washers at y +-24, z 2.5) and tied to the lip by the first tie (post 8 x 8 + web, y -32..-24).
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
# the lower piece on the wrist plate's front edge (2 x M2.5 x 16 at z 2.5 since round 7; pushed forward, only the screw holds it). So
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
B_POST2 = 24.3               # round 5, probed at z 35.5: 194.3 mm2 net of the anchor hole / 8 (I_y 1086: b_eq 25.45)
B_TW_FRONT = 25.5
T_POST2 = P.TIE2_POST_T                                   # 8 (round 4; round 3: 4)
Z_BLOCK = C.ZS - C.RAIL_IN                                # 17.75: the frame's rail block top
VSEAT = hasattr(C, "VSEAT_D") and hasattr(P, "RIDGE_TIP_Z")   # round 5: the foot's ridge in the block's V-groove
FOOT_CLR = getattr(P, "FOOT_CLR", C.VSEAT_CLR if VSEAT else 0.0)   # round 6: 0.30, decoupled from VSEAT_CLR
ANCHOR_AS_BUILT = (hasattr(C, "ANCHOR_XY")
                   and P.TIE2_FOOT_Z <= Z_BLOCK + FOOT_CLR + 1e-6)
ANCHOR2 = ANCHOR_AS_BUILT                                 # the second post seated + screwed on the rail block (round 4)
K_ANCHOR_X = 3000.0                                       # N/mm: the foot held in x (the ridge's flank; round 4: friction
                                                          # or the shank once it bears)
ANCHOR_KX = K_ANCHOR_X                                    # set to 0 for the slip phase (preload gone, gap still open)
P_M3 = 150.0                                              # N, the anchor driven "snug only" (<= 0.09 N.m), assumption
GAP_NOM = (C.M3_CLEAR - 3.0) / 2                          # 0.2: printed Ø3.4 hole round the Ø3 shank, centred
GAP_MAX = (C.M3_CLEAR + P.HOLE_COMP - 3.0) / 2 + 0.1      # 0.4: CAD Ø3.6 + 0.1 position error (bound)
Z_FOOT = P.TIE2_FOOT_Z if ANCHOR2 else Z_BLOCK            # 18.05: the post's foot flats (round 5 17.85, round 4 17.75)
D_HOLE = C.M3_CLEAR + P.HOLE_COMP                         # 3.6 CAD
POST_FOOT_A, POST_FOOT_I = 60.7, 373.5                    # probed on the round 6 solid at z 19 (net of the hole; y 23.04..32)
POST_WALL = 2.2                                           # probed: hole to either x face of the post (z 25, 40, 50)
STACK = C.Z_TOP1 - Z_BLOCK                                # 33.75: the head's seat (top wall top) to the block top, CAD
HEAD_DK = 5.5                                             # ISO 4762 M3 socket head
WASHER_M3 = getattr(C, "ANCHOR_WASHER", (7.0, 0.5))      # ISO 7089 M3 washer, as on the MG996R tab screws
WASHER_T = WASHER_M3[1] if VSEAT else 0.0                 # round 5: the washer is fitted (BUILD_GUIDE)
L_ANCHOR = 45.0 - STACK - WASHER_T                        # 10.75 engaged in the frame's 14 mm pilot (11.25 without washer)
LAYER = 0.2
# ---------------------------------------------------------------- the V-seat AS PRINTED (independent review, round 6)
# Reviewer's own scratch slice (not a job file) of both committed part.stl files with the arm's command, G-code read back
# (header). Printed: frame bulkhead + ribs top 48.4; rail block top 17.8; the groove's layer walls at half-widths 0.15 /
# 0.35 / 0.55 / 0.75 in the layers ending 17.2 / 17.4 / 17.6 / 17.8, so each layer's top corner stands 0.1 (horizontal)
# inside the CAD flank (corner half-width z_top - 17.05); the 17.0..17.2 layer an OPEN 0.3 slot between two external
# perimeters (floor 17.0 inside |dx| < 0.15, the layer's top 17.2 at 0.15..0.35, which the ridge's flat tip faces). The
# cover: ridge flanks, tip and flats to CAD; the 0.2 x 0.2 bump behind the post's back face does not print.
Z_BULK_PR = 48.4                 # printed bulkhead top
Z_BLOCK_PR = 17.8                # printed rail block top
Z_SLOT_TOP = 17.2                # the groove's 17.0..17.2 layer top beside its open slot (what the tip faces)
Z_GROOVE_APEX = Z_BLOCK - C.VSEAT_D if VSEAT else Z_BLOCK    # 16.95
K_ROUND = 2 - math.sqrt(2)       # a corner radius r drops a 45° flank's contact by (2 - sqrt2) r, vertically
R_BEAD = (0.05, 0.075, 0.10)     # bead corner radius: low / nominal / high (the brief)
# Tolerances, each a 3-sigma bound: +-0.05 on EVERY printed surface (the brief). As a vertical seat height:
TOL = {"ridge": 0.05 * math.sqrt(2),   # the ridge's 45° flank, +-0.05 normal -> +-0.0707 vertical
       "groove": 0.05,                 # the groove's vertical layer walls (horizontal error = vertical seat error at 45°)
       "cover": 0.05,                  # the cover's top-wall underside (relative to its ridge, same print plane)
       "bulk": 0.05,                   # the frame's bulkhead top (top-layer surface; the self-check had none)
       "tip": 0.05, "slot": 0.05,      # the ridge's flat tip; the groove's 17.2 layer top (the self-check had none)
       "flats": 0.05, "block": 0.05}   # the foot's flats; the rail block's top
FEELER_IN = 0.03                 # BUILD_GUIDE §4 step 9: this feeler MUST enter at the top wall before any screw
STOPS = ("top wall on the bulkhead", "ridge tip on the groove's 17.2 layer", "foot flats on the rail block")
GAPKEY = dict(zip(STOPS, ("top_gap", "tip_gap", "flat_gap")))
INVOLVE = dict(zip(STOPS, (("ridge", "groove", "bulk", "cover"), ("ridge", "groove", "tip", "slot"),
                           ("ridge", "groove", "flats", "block"))))


def seat(e=None, r=R_BEAD[1]):
    """Where the cover stops on the PRINTED frame. Every stop is a height h (vertical shift of the rigid cover from its
    CAD seat) at which it touches; the cover rests at the highest. e: signed errors (+ = more material on that surface).
    Returns the governing stop, the ridge's play (h over the ridge's own h = horizontal clearance per flank, 45°) and the
    gap each stop is left with (what a feeler would read)."""
    e = e or {}
    h = {"ridge on both flanks": LAYER / 2 - K_ROUND * r + e.get("ridge", 0) + e.get("groove", 0),
         STOPS[0]: (Z_BULK_PR - C.Z_TOP0) + e.get("bulk", 0) + e.get("cover", 0),
         STOPS[1]: (Z_SLOT_TOP - P.RIDGE_TIP_Z) + e.get("tip", 0) + e.get("slot", 0),
         STOPS[2]: (Z_BLOCK_PR - P.TIE2_FOOT_Z) + e.get("flats", 0) + e.get("block", 0)}
    gov = max(h, key=h.get)
    H = h[gov]
    out = {"by": gov, "h": H, "play": H - h["ridge on both flanks"], "ridge_h": h["ridge on both flanks"]}
    out.update({GAPKEY[k]: H - h[k] for k in STOPS})
    return out


def seat_cases():
    """Nominal; RSS (per competing stop: its nominal gap less the RSS of the tolerances it involves, the corner radius
    nominal -> high as one more term); worst case (every tolerance at a limit: 256 sign vertices x 3 radii), with and
    without BUILD_GUIDE step 9's 0.03 feeler (which rejects a build whose top wall carries the cover)."""
    nom = seat()
    rr = K_ROUND * (R_BEAD[2] - R_BEAD[1])
    rss = {k: nom[GAPKEY[k]] - math.sqrt(sum(TOL[t] ** 2 for t in INVOLVE[k]) + rr ** 2) for k in STOPS}
    keys = list(TOL)
    worst, worst_acc = (0.0, nom), (0.0, nom)
    top_hi, top_lo = (nom["top_gap"], nom), (nom["top_gap"], nom)
    for bits in range(1 << len(keys)):
        e = {k: (TOL[k] if bits >> i & 1 else -TOL[k]) for i, k in enumerate(keys)}
        for r in R_BEAD:
            s_ = seat(e, r)
            if s_["play"] > worst[0] + 1e-12:
                worst = (s_["play"], s_)
            if s_["top_gap"] >= FEELER_IN - 1e-12 and s_["play"] > worst_acc[0] + 1e-12:
                worst_acc = (s_["play"], s_)
            if s_["top_gap"] > top_hi[0]:
                top_hi = (s_["top_gap"], s_)
            if s_["top_gap"] < top_lo[0]:
                top_lo = (s_["top_gap"], s_)
    rss_top_hi = nom["top_gap"] + math.sqrt(sum(TOL[t] ** 2 for t in INVOLVE[STOPS[0]]) + rr ** 2)
    return {"nominal": nom, "rss_margin": rss, "worst": worst, "worst_accepted": worst_acc,
            "top_gap_range": (top_lo[0], top_hi[0]), "top_gap_rss_hi": rss_top_hi}


def corners_on_flank(lift, r=R_BEAD[1]):
    """The groove's printed layer corners that the seated ridge's flank actually touches: a rounded corner's tangent
    point (on the 45° flank) is at z_top - (1 - 1/sqrt2) r; it carries if that lies between the ridge's tip and flats."""
    tip, top = P.RIDGE_TIP_Z + lift, P.TIE2_FOOT_Z + lift
    return [round(LAYER * k, 3) for k in range(1, 200) if Z_SLOT_TOP < LAYER * k <= Z_BLOCK_PR + 1e-9
            and tip <= LAYER * k - (1 - 1 / math.sqrt(2)) * r <= top]


def seating(P_clamp, flow, lift=None, r=R_BEAD[1]):
    """Descent of the ridge (vertical, mm) when P_clamp (N) presses it into the groove's printed corners, each crushed
    flat at `flow` MPa (contact width sqrt2 x its own descent, both flanks): F = sum over carrying corners of
    2 flow L_V (d - d_k); a lower corner joins once the tip has come down to its tangent point. Returns
    (descent, number of corners carrying per flank)."""
    lift = LIFT_NOM if lift is None else lift
    tip0 = P.RIDGE_TIP_Z + lift
    starts = sorted(max(0.0, tip0 - (z - (1 - 1 / math.sqrt(2)) * r)) for z in (17.4, 17.6, 17.8))
    k1 = 2 * flow * L_V
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        F = sum(k1 * (mid - s0) for s0 in starts if mid > s0)
        lo, hi = (mid, hi) if F < P_clamp else (lo, mid)
    d = (lo + hi) / 2
    return d, sum(1 for s0 in starts if d > s0)


if VSEAT:
    LIFT_NOM = LAYER / 2 - K_ROUND * R_BEAD[1]            # 0.056: the ridge's printed seat above its CAD seat
    # the ridge's root as printed: x 14.35..16.35 (the bump behind the post's back face does not print), 2.0 wide
    X_RIDGE1 = C.VSEAT_XC + (P.TIE2_FOOT_Z - P.RIDGE_APEX_Z)          # 16.35
    RIDGE_B = X_RIDGE1 - C.LIP_X0                                     # 2.0 (the self-check: 2.2)
    RIDGE_X0 = (X_RIDGE1 + C.LIP_X0) / 2                              # 15.35: its centroid
    L_V = C.TIE2_Y[1] - (C.TIE2_Y[0] + (P.TIE2_FOOT_Z - P.RIDGE_TIP_Z))   # 7.3: full-depth ridge y 24.7..32 (lead-in ignored)
    SEAT = seat_cases()
    PLAY_NOM = round(SEAT["nominal"]["play"], 3)            # 0
    PLAY_RSS = 0.0 if min(SEAT["rss_margin"].values()) > 0 else round(-min(SEAT["rss_margin"].values()), 3)
    PLAY_WORST = round(SEAT["worst"][0], 3)                 # every tolerance at a limit (any build)
    PLAY_ACC = round(SEAT["worst_accepted"][0], 3)          # the worst a build that passes step 9's 0.03 feeler can have
    CORNERS0 = corners_on_flank(LIFT_NOM)                   # first contact: 17.6 and 17.8 only
    # seating by the anchor's 150 N (BUILD_GUIDE: anchor first, snug): the corners crush; 80 MPa = the least crush
    SEAT_D = {fl: seating(P_M3, fl) for fl in (40.0, 80.0)}
    D_MIN = SEAT_D[80.0][0]
    TIP_SEATED = P.RIDGE_TIP_Z + LIFT_NOM - D_MIN           # the tip after seating (least crush)
    FLANK_H = Z_BLOCK_PR - TIP_SEATED                       # contact band height: the tip to the groove's top corner
    FLANK_L = FLANK_H * math.sqrt(2)
    FLANK_H0 = Z_BLOCK_PR - (P.RIDGE_TIP_Z + LIFT_NOM)      # the same at first contact, before any crush (information)
    # where the flank force acts: the two upper corners carry from first contact, the 17.4 one only after crushing, so
    # the resultant is taken at their middle, z 17.7 (the self-check: 17.6 with three)
    Z_XR = sum(CORNERS0) / len(CORNERS0)
    # its moment about the printed root's centroid (x 15.35, the flats): Fx (2 z_c - flats - apex) on the +x flank,
    # plus (15.35 - 15.25) on the -x flank: the worse is used
    RIDGE_ARM = abs(2 * Z_XR - P.TIE2_FOOT_Z - P.RIDGE_APEX_Z) + abs(RIDGE_X0 - C.VSEAT_XC)
    # the top wall's standing over the printed bulkhead at the ridge: before the screws, and after the anchor's seating
    G_TOP = SEAT["nominal"]["top_gap"]                      # 0.156
    G_TOP_RSS = SEAT["top_gap_rss_hi"]                      # RSS-high
    G_TOP_W = SEAT["top_gap_range"][1]                      # worst-case high
    G_AFTER = {lab: tuple(max(0.0, g - d) for g in (G_TOP, G_TOP_RSS, G_TOP_W)) for lab, d in
               (("least crush, 80 MPa", D_MIN), ("40 MPa", SEAT_D[40.0][0]))}
    FLOAT_W = G_AFTER["least crush, 80 MPa"][2]            # worst top-wall standing after the anchor alone
    # M3 x 45 engagement, measured from the PRINTED block top (17.8): the head's seat is at 51.5 + (the cover's height
    # above its CAD seat) = 51.5 + (standing - 0.1); the tip 45 - 0.5 (washer) below that
    L_ANCHOR_EFF = Z_BLOCK_PR - (C.Z_TOP1 + (FLOAT_W - (C.Z_TOP0 - Z_BULK_PR)) + WASHER_T - 45.0)
else:
    Z_XR = Z_FOOT
    PLAY_NOM = PLAY_RSS = PLAY_WORST = PLAY_ACC = FLOAT_W = 0.0
    L_ANCHOR_EFF = L_ANCHOR
KT_RIDGE = 1.7      # the ridge's root corners: 135° re-entrant corners filled by the printed bead (strength-checks 1.7)
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
Z_SCREW = C.FRONT_SCREWS[0][1]                            # 2.5 (round 7: 3 -> 2.5)
M25_WASHER = getattr(C, "FRONT_WASHER", (0.0, 0.0))       # round 7: DIN 125 Ø6 x 0.5 under each front M2.5 head
L_M25 = min(FRAME_P["FRONT_PILOT_DEPTH"], 16.0 - C.FRONT_T - M25_WASHER[1])   # M2.5 x 16 through the 5 mm plate and the
                                                           # 0.5 washer: 10.5 engaged (11 without the washer)
HEAD_D = 5.0                                               # M2.5 pan head (spec: head <= Ø5)
HOLE_PR = C.M25_CLEAR                                      # 2.8 printed (3.0 CAD teardrop)
A_HEAD = math.pi / 4 * (HEAD_D ** 2 - HOLE_PR ** 2) - (HOLE_PR / 2) ** 2 * (1 - math.pi / 4)   # minus the teardrop
# what bears on the front plate (round 7): the washer's OD, or the bare head's if there is no washer
BRG_D = max(HEAD_D, M25_WASHER[0])
A_BRG = math.pi / 4 * (BRG_D ** 2 - HOLE_PR ** 2) - (HOLE_PR / 2) ** 2 * (1 - math.pi / 4)   # 21.7 mm2 on the Ø6 washer
BRG_TXT = (f"Ø{M25_WASHER[0]:g} x {M25_WASHER[1]:g} washer under the Ø{HEAD_D:.0f} pan head" if M25_WASHER[0] else
           f"Ø{HEAD_D:.0f} pan head")


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
    # review: support reactions (K u - F at every restrained dof; 0 at free ones), the force the support puts ON the node
    out["_r"] = {n: tuple((sum(K[3 * idx[n] + d][q] * u[q] for q in range(nd)) - F[3 * idx[n] + d])
                          if 3 * idx[n] + d in fixed else 0.0 for d in range(3)) for n in names}
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
        # as built: the second post on the frame's rail block, clamped by the vertical M3 x 45. Round 5: the foot is held
        # in x by its ridge's flank in the block's V-groove (a 3 kN/mm spring at the flank band's middle, z 17.5) and in z
        # by the flanks (compression) and the screw (tension): stiff. Round 4: preload friction or the shank at z 17.75;
        # ANCHOR_KX 0 = sliding freely
        nodes.update({"AN": (xp2, Z_XR), "GA": (xp2 - 10.0, Z_XR), "GZ": (xp2, Z_XR - 10.0)})
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


# review: the top joint's own reactions -> the top M3s' tension. Per zone, the joint at BK (x 10, z 50) puts (Rx, Rz, M)
# on the cover: the bulkhead top (x 3.5..10) can only push up, the M3 (x 6.75) can only pull down. The least tension that
# balances it: T = max(0, -Rz, M / 3.25, (-M - 6.5 Rz) / 3.25) (M about x 10, counter-clockwise with x right, z up).
X_SCREW_TOP = C.TOP_SCREWS[0][0]                            # 6.75
LEV_F, LEV_R = C.X_B - X_SCREW_TOP, X_SCREW_TOP - (C.X_B - C.BULK_T)   # 3.25 to the front edge, 3.25 to the rear edge
M3_PAN_DK = 5.6                                             # ISO 7049 ST2.9 / ISO 7045 M3 pan head
A_M3_PAN = math.pi / 4 * (M3_PAN_DK ** 2 - C.M3_CLEAR ** 2) - (C.M3_CLEAR / 2) ** 2 * (1 - math.pi / 4)
# round 7: the top screws are M3 x 14 pan heads on an ISO 7089 Ø7 x 0.5 washer (no camera); what bears on the top wall
TOP_WASHER = getattr(C, "TOP_WASHER", (0.0, 0.0))
TOP_BRG_D = max(M3_PAN_DK, TOP_WASHER[0])
A_M3_TOP = math.pi / 4 * (TOP_BRG_D ** 2 - C.M3_CLEAR ** 2) - (C.M3_CLEAR / 2) ** 2 * (1 - math.pi / 4)   # 28.8 mm2
TOP_TXT = (f"M3 x 14 pan head on the Ø{TOP_WASHER[0]:g} x {TOP_WASHER[1]:g} washer" if TOP_WASHER[0] else
           f"Ø{M3_PAN_DK} pan head")


def top_screw_T(res):
    out = []
    for z_, bk in (("+", "BKa"), ("-", "BKb")):
        Rx, Rz, Mr = res["_r"][bk]
        M = Mr + res[f"top joint {z_}"][1]
        out.append(max(0.0, -Rz, M / LEV_F, (-M - (LEV_F + LEV_R) * Rz) / LEV_R))
    return tuple(out)                                       # (zone + screw at y 14, zone - screw at y -23)


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
    # review: the top M3s' tension from the joint (service load only; the snug preload is its own sustained row)
    Tp, Tm = top_screw_T(res)
    out["top M3 head on the top wall, the joint's own tension (no preload)"] = (
        max(Tp, Tm) / A_M3_TOP, BEARING, "XY comp", f"T {max(Tp, Tm):.0f} N (y 14: {Tp:.0f}, y -23: {Tm:.0f}) on the "
        f"{TOP_TXT}, {A_M3_TOP:.1f} mm2")
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
        # the post alone below the web (round 6: flats z 18.05..19.25): 8 thick along x, 8.96 wide at z 19 (y 23.04..32),
        # net of the Ø3.6 hole on its centreline (probed: A 60.7 mm2, I_y 373.5 mm4); bending in the x-z plane from the x
        # reaction (at z 17.6, the ridge's flank) to the web, Kt 2.5 at the web's bottom corner; in print these run along
        # the layers
        # the wedge (round 5): the +x push rides up the groove's 45° flank, frictionless (worst): the ridge is pushed up by
        # Fx as well, and the screw holds both in tension
        lift_w = Fx if VSEAT else 0.0
        M_f = Fx * (Z_WEB0 - Z_XR)
        out[f"second post's foot below the web (z {Z_FOOT:.2f}..19.25), the anchor's reaction"] = (
            (max(Fz, 0.0) + lift_w) / POST_FOOT_A + KT_SHARP * M_f * (T_POST2 / 2) / POST_FOOT_I, ALLOW_XY, "XY",
            f"8 x 8.96 net of the Ø{D_HOLE:.1f} hole (A {POST_FOOT_A}, I {POST_FOOT_I}), Fx {Fx:.1f} N at z {Z_XR:.2f}, "
            f"lift {Fz:+.1f} N + wedge {lift_w:.1f} N, Kt {KT_SHARP}")
        out["second post's foot: shear across it (z 19.25)"] = (
            1.5 * Fx / POST_FOOT_A, ALLOW_XY * 0.5, "XY shear", f"A {POST_FOOT_A}, Fx {Fx:.1f} N")
        # M3 x 45 pull-out from the frame's Ø2.7 x 14 pilot: (preload) + the wedge's lift + the lift; round 5 adds the
        # preload on top, conservatively, although nothing relies on it
        # review: in a 'slip' mode the play only matters once the preload has crept away (with it, friction at the seat
        # holds the foot, round 4's 'held'), so the screw then carries the lifts alone; 'locked' adds the preload on top.
        # Round 6: engaged length with the top wall's worst-case float after seating (L_ANCHOR_EFF)
        T_scr = (P_M3 if CUR_MODE in ("held", "locked") else 0.0) + lift_w + max(Fz, 0.0)
        out[f"M3 x 45 anchor: pull-out from the frame's rail block ({L_ANCHOR_EFF:.2f} engaged), preload (if any) + "
            + ("wedge lift + lift" if VSEAT else "lift")] = (
            T_scr / (math.pi * 3.0 * L_ANCHOR_EFF), SHEAR_Z, "Z shear (frame)",
            f"screw {T_scr:.0f} N, thread cylinder Ø3 x {L_ANCHOR_EFF:.2f}")
        if VSEAT:
            # the ridge (round 5). In print the ridge is a vertical prism (G y = print Z): its cross-section is in the
            # layer plane, so its root (the plane of the flats) is sheared and bent along the layers (in-plane allowables)
            N_fl = Fx * math.sqrt(2)                                     # all on one 45° flank, frictionless
            out[f"V-ridge: flank bearing on the groove's 45° flank (contact band z {TIP_SEATED:.2f}..{Z_BLOCK_PR:.2f}: "
                f"the seated tip, after the anchor's least crush, to the printed top corner)"] = (
                N_fl / (FLANK_L * L_V), BEARING, "bearing",
                f"normal {N_fl:.1f} N on {FLANK_L:.2f} x {L_V:.1f} (the {P.TIE2_FOOT_Z - P.RIDGE_TIP_Z:.1f} lead-in ignored)")
            out[f"V-ridge root at the foot's flats (z {P.TIE2_FOOT_Z:.2f}): shear"] = (
                1.5 * Fx / (RIDGE_B * L_V), ALLOW_XY * 0.5, "XY shear", f"{RIDGE_B:.1f} x {L_V:.1f}, Fx {Fx:.1f} N")
            out[f"V-ridge root at the foot's flats (printed, x 14.35..16.35): the flank force's moment ({RIDGE_ARM:.2f} Fx, "
                f"resultant at the two upper corners, z {Z_XR:.1f}) + the wedge's compression, Kt {KT_RIDGE}"] = (
                lift_w / (RIDGE_B * L_V) + KT_RIDGE * 6 * Fx * RIDGE_ARM / (RIDGE_B ** 2 * L_V), ALLOW_XY, "XY",
                f"{RIDGE_B:.1f} x {L_V:.1f}, M {Fx * RIDGE_ARM:.1f} N.mm, Kt {KT_RIDGE} (bead-filled 135° root corners); "
                f"compression and bending added in magnitude")
        else:
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
    out[f"M2.5 x 16 at z {Z_SCREW:g}: pull-out from the frame ({L_M25:.1f} engaged)"] = (
        S / (math.pi * 2.5 * L_M25), SHEAR_Z, "Z shear", f"screw force {S:.0f} N")
    out["same M2.5: its head on the cover's front plate"] = (S / A_BRG, BEARING, "XY comp",
                                                             f"{BRG_TXT} on the Ø{HOLE_PR} teardrop, "
                                                             f"{A_BRG:.1f} mm2; screw force {S:.0f} N")
    return out


def _combine(r1, f1, r2, f2):
    """Member results r1 x f1 + r2 x f2 (linear superposition of two solves; L from r1)."""
    out = {}
    for k, v in r1.items():
        if k in ("_u", "_r"):
            out[k] = {n: tuple(f1 * a + f2 * b for a, b in zip(v[n], r2[k][n])) for n in v}
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
    if not ANCHOR2 or mode in ("held", "locked"):          # 'locked' (round 5): the ridge holds x, no preload needed
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
# review: the verdict rows run with the ridge's play AS PRINTED. Ridge-first contact gives zero play at nominal and RSS
# ('locked': the ridge holds x, the preload added to the screw where that is worse). The worst case with every tolerance
# at a limit is the top wall landing first (PLAY_WORST), which BUILD_GUIDE §4 step 9's 0.03 feeler rejects; the worst a
# build that PASSES step 9 can have is the tip bottoming on the groove's 17.2 layer (PLAY_ACC), which no feeler sees: the
# foot slides that far before the flank bears (preload gone). Every row takes the worse of 'locked' and PLAY_ACC.
ANCHOR_MODES = (("locked", f"slip {PLAY_ACC:.3f}") if VSEAT else ("held", f"slip {GAP_NOM:.2f}", f"slip {GAP_MAX:.2f}")) \
    if ANCHOR2 else ("held",)


def cover_rows(case, load_node, R, req, rows=ROWS, variants=None, modes=None):
    worst = {}
    for mode in (ANCHOR_MODES if modes is None else modes):
        for v in (VARIANTS if variants is None else variants):
            res, _ = anchored(load_node, R, v, mode)
            for k, (s, a, d, sec) in cover_sections(res, v, load_node == "LD2").items():
                if k not in worst or s / a > worst[k][0] / worst[k][1]:
                    am = "" if not ANCHOR2 else ("; ridge on both flanks, play 0 (nominal, RSS)" if mode == "locked"
                                                 else "; anchor held by its preload" if mode == "held" else
                                                 f"; ridge play {mode.split()[1]} mm (worst build step 9 accepts: "
                                                 f"tip bottomed; preload gone)"
                                                 if VSEAT else f"; anchor preload gone, {mode.split()[1]} mm slip")
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
    f"{z_rbg:.1f}): one M2.5 at z {Z_SCREW:g} holds it, {T_g:.0f} N", f"{BRG_TXT} on the Ø{HOLE_PR} teardrop, "
    f"{A_BRG:.1f} mm2", "XY comp", T_g / A_BRG, BEARING, SF_SHORT)
# the plate between that screw (z 2.5) and the first tie's web (z 19.25), loaded at z 12 at the cover's -y edge
a_, b_ = z_rbg - C.FRONT_SCREWS[0][1], Z_WEB0 - z_rbg
M_pl = R_go * a_ * b_ / (a_ + b_)
b_pl = PATCH + min(a_, b_)
row(f"stall, one jaw blocked: the same push on the lower piece's plate between the screw (z {Z_SCREW:g}) and the web "
    f"(z 19.25)",
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


if ANCHOR2 and VSEAT:
    row(f"anchor M3 x 45 driven snug: Ø{WASHER_M3[0]:g} x {WASHER_M3[1]:g} washer under the socket head on the top wall, "
        f"preload {P_M3:.0f} N (sustained)", f"{head_area(WASHER_M3[0]):.1f} mm2 round the Ø{HOLE_TD} teardrop (washer "
        f"OD; BUILD_GUIDE §1)", "XY comp", P_M3 / head_area(WASHER_M3[0]), BEARING, SF_CYCLIC)
elif ANCHOR2:
    row(f"anchor M3 x 45 driven snug: socket head (dk {HEAD_DK}) on the top wall, preload {P_M3:.0f} N (sustained)",
        f"{head_area(HEAD_DK):.1f} mm2 round the Ø{HOLE_TD} teardrop, no washer (BUILD_GUIDE lists none)", "XY comp",
        P_M3 / head_area(HEAD_DK), BEARING, SF_CYCLIC)
if ANCHOR2:
    a_post = C.GUIDE_T * TIE_W - math.pi / 4 * D_HOLE ** 2
    row(f"anchor preload {P_M3:.0f} N through the stack (sustained): the 8 x 8 post round its Ø{D_HOLE:.1f} hole",
        f"{a_post:.0f} mm2 (the full-depth part only; the 45-degree part ignored)", "XY comp", P_M3 / a_post, ALLOW_XY,
        SF_CYCLIC)
    row(f"anchor preload {P_M3:.0f} N (sustained): M3 x 45 pull-out from the frame's rail block"
        + (f", the top wall left {FLOAT_W:.3f} proud after seating (worst-case stack)" if VSEAT else ""),
        f"thread cylinder Ø3 x {L_ANCHOR_EFF:.2f} (Ø2.7 x 14 pilot; {L_ANCHOR:.2f} in CAD)", "Z shear (frame)",
        P_M3 / (math.pi * 3.0 * L_ANCHOR_EFF), SHEAR_Z, SF_CYCLIC)
if ANCHOR2 and VSEAT:
    # information (not in the verdict), review ruling: when the ridge reaches its flanks first, the snug preload presses
    # it there; bound: all 150 N on the two flanks. The bearing stress is local crushing of the frame's 0.2 mm layer
    # corners, and that crushing IS the seating: it stops by itself once the crushed area carries the clamp, it moves the
    # ridge deeper (closing play, never opening it), and its creep only relaxes a preload that nothing relies on. The
    # sustained-load SF 4 is for members whose creep deflection matters; here the creep is harmless, so not a verdict row.
    # Round 6: with ridge-first contact the flanks always take the preload; the seating it gives is printed below.
    row("info: anchor preload seats the ridge, bound: all 150 N on the two 45° flanks (sustained; seating, self-limiting)",
        f"normal {P_M3 / math.sqrt(2):.0f} N per flank on {FLANK_L:.2f} x {L_V:.1f}", "bearing",
        P_M3 / math.sqrt(2) / (FLANK_L * L_V), BEARING, SF_CYCLIC, INFO)
    # review: where the flank force acts. With zero play the three printed corners (17.4, 17.6, 17.8) share it and the
    # resultant is ~17.6 (the verdict row). Bound: a ridge seated on the top corner alone (the corners' own print scatter)
    # puts it at 17.8, arm |2 x 17.8 - flats - apex|.
    FX_LOCK = max(abs(anchored("LD2", R_go, v, "locked")[0]["anchor"][0]) for v in VARIANTS)
    ARM_TOP = abs(2 * Z_BLOCK_PR - P.TIE2_FOOT_Z - P.RIDGE_APEX_Z) + abs(RIDGE_X0 - C.VSEAT_XC)
    row(f"info, bound: opening stall with zero play, Fx {FX_LOCK:.1f} N all on the groove's top layer corner (z "
        f"{Z_BLOCK_PR}): V-ridge root at the flats, Kt {KT_RIDGE}",
        f"{RIDGE_B:.1f} x {L_V:.1f}, M {FX_LOCK * ARM_TOP:.1f} N.mm (arm {ARM_TOP:.2f})", "XY",
        FX_LOCK / (RIDGE_B * L_V) + KT_RIDGE * 6 * FX_LOCK * ARM_TOP / (RIDGE_B ** 2 * L_V), ALLOW_XY, SF_SHORT, INFO)
    # review: the flank bearing with NO seating credit (the band from the tip at first contact, two corners): the
    # verdict row above takes the band after the anchor's least crush (80 MPa), which BUILD_GUIDE's anchor-first order
    # guarantees before any service load
    row(f"info: opening stall, Fx {FX_LOCK:.1f} N: V-ridge flank bearing at FIRST contact, no seating credit (band z "
        f"{P.RIDGE_TIP_Z + LIFT_NOM:.3f}..{Z_BLOCK_PR}, corners {CORNERS0})",
        f"normal {FX_LOCK * math.sqrt(2):.1f} N on {FLANK_H0 * math.sqrt(2):.2f} x {L_V:.1f}", "bearing",
        FX_LOCK / (FLANK_H0 * L_V), BEARING, SF_SHORT, INFO)

# ================================================================ 6b. snug preloads of the cover's other screws (review)
# The project's rule (anchor here, turntable ring, links): a snug self-tapper's preload on a printed seat is a sustained
# load, SF 4. M3 snug 150 N (the anchor's figure), M2 / M2.5 snug 100 N (the frame's tab screws' figure).
P_M25 = 100.0
A_M25_W6 = math.pi / 4 * (6.0 ** 2 - HOLE_PR ** 2) - (HOLE_PR / 2) ** 2 * (1 - math.pi / 4)
# round 7 (the round 6 review's fix): M3 x 14 pan heads + Ø7 x 0.5 washers on top, Ø6 x 0.5 washers under the M2.5s
row(f"top screws (no camera), {TOP_TXT}, driven snug, {P_M3:.0f} N preload (sustained): bearing on the top wall",
    f"{A_M3_TOP:.1f} mm2 round the Ø{C.M3_CLEAR} teardrop (washer OD; BUILD_GUIDE §1)", "XY comp", P_M3 / A_M3_TOP,
    BEARING, SF_CYCLIC)
row(f"front M2.5 x 16 pan heads, {BRG_TXT}, driven snug, {P_M25:.0f} N preload (sustained): bearing on the front plate",
    f"{A_BRG:.1f} mm2 round the Ø{HOLE_PR} teardrop", "XY comp", P_M25 / A_BRG, BEARING, SF_CYCLIC)
# information: the round-6 BOM (bare heads), and the camera case (M3 x 18 button heads on the camera mount's 3.5 pad,
# Ø3.6 CAD teardrop holes, Ø3.4 printed: the same seat as here; BUILD_GUIDE lists no washer there)
row(f"info: round 6 BOM, top M3 x 10 bare pan heads driven snug, {P_M3:.0f} N (sustained): bearing on the top wall",
    f"Ø{M3_PAN_DK} pan head on the Ø{C.M3_CLEAR} teardrop, {A_M3_PAN:.1f} mm2", "XY comp", P_M3 / A_M3_PAN, BEARING,
    SF_CYCLIC, INFO)
row(f"info: round 6 BOM, front M2.5 bare pan heads driven snug, {P_M25:.0f} N (sustained): bearing on the front plate",
    f"Ø{HEAD_D:.0f} pan head on the Ø{HOLE_PR} teardrop, {A_HEAD:.1f} mm2", "XY comp", P_M25 / A_HEAD, BEARING, SF_CYCLIC,
    INFO)
BTN_DK = 5.7                                               # ISO 7380 M3 button head
A_BTN = math.pi / 4 * (BTN_DK ** 2 - C.M3_CLEAR ** 2) - (C.M3_CLEAR / 2) ** 2 * (1 - math.pi / 4)
row(f"info: camera case, M3 x 18 bare button heads (BOM) driven snug, {P_M3:.0f} N (sustained): bearing on the camera "
    f"mount's pad (not this part; the same Ø3.4 printed teardrop)", f"Ø{BTN_DK} button head, {A_BTN:.1f} mm2", "XY comp",
    P_M3 / A_BTN, BEARING, SF_CYCLIC, INFO)
row(f"info: camera case with the proposed fix, M3 x 18 button heads on Ø7 x 0.5 washers, {P_M3:.0f} N (sustained): "
    f"bearing on the camera mount's pad", f"{A_M3_TOP:.1f} mm2 (washer OD)", "XY comp", P_M3 / A_M3_TOP, BEARING,
    SF_CYCLIC, INFO)

# ================================================================ 6c. the proud top wall pulled down by the top M3s (review)
# After the anchor seats the ridge (least crush, 80 MPa) the top wall still stands G_AFTER over the printed bulkhead at
# the ridge. The cover rests on the ridge (y 24.7..32, centre 28.35) and on the bulkhead at its -y end, so the gap at a
# top screw is that x (y_s + 32) / (28.35 + 32): 0.76 at y 14, 0.15 at y -23. Driving the M3 closes it two ways in series:
# bending the top wall behind the lip (cantilever from the lip's back face, x 14.35, to the screw, L 7.6, b_eff 2L + dk)
# and tilting the whole cover (crushing the ridge's corners further, 3 corners at 80 MPa, through the lever ratio). The
# bending takes k_tilt / (k_bend + k_tilt) of it. Displacement-controlled: it relaxes with creep. Information rows.
L_TW = C.LIP_X0 - X_SCREW_TOP                              # 7.6
B_TW_EFF = 2 * L_TW + TOP_BRG_D                            # 22.2 on the Ø7 washer (round 7; 20.8 on the bare pan head)
K_BEND = 3 * E_MPA * (B_TW_EFF * C.TOP_T ** 3 / 12) / L_TW ** 3
Y_RIDGE_C = (C.TIE2_Y[0] + (P.TIE2_FOOT_Z - P.RIDGE_TIP_Z) + C.TIE2_Y[1]) / 2   # 28.35
K_TILT = 2 * 80.0 * 3 * L_V * ((Y_RIDGE_C + C.HALF_Y) / (C.TOP_SCREWS[1][1] + C.HALF_Y)) ** 2
SHARE = K_TILT / (K_BEND + K_TILT)
FORCED = {}
if VSEAT:
    for (y_s, lab) in ((C.TOP_SCREWS[1][1], "+y screw (y 14)"), (C.TOP_SCREWS[0][1], "-y screw (y -23)")):
        f_t = (y_s + C.HALF_Y) / (Y_RIDGE_C + C.HALF_Y)
        for case, g in zip(("nominal", "RSS-high", "worst"), G_AFTER["least crush, 80 MPa"]):
            d_b = SHARE * f_t * g
            FORCED[(lab, case)] = (f_t * g, d_b, K_BEND * d_b, 3 * E_MPA * C.TOP_T * d_b / (2 * L_TW ** 2))
    for case in ("nominal", "RSS-high"):
        gap, d_b, F_, s_ = FORCED[("+y screw (y 14)", case)]
        row(f"info: the +y top M3 pulls the proud top wall down ({case}: {gap:.3f} at the screw after the anchor's "
            f"seating; {SHARE:.2f} of it bends the wall, {F_:.0f} N): top face at the lip's back face, tension "
            f"(displacement-controlled, relaxes)", f"cantilever L {L_TW:.1f}, b_eff {B_TW_EFF:.1f} x {C.TOP_T:.0f}, "
            f"E {E_MPA:.0f}, Kt 1 (smooth face)", "XY", s_, ALLOW_XY, SF_CYCLIC, INFO)
        row(f"info: the same, {case}: the re-entrant corner under it (lip back face / top wall underside), compression",
            f"Kt {KT_SHARP}", "XY comp", KT_SHARP * s_, BEARING, SF_SHORT, INFO)

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
      + ((", foot held by the ridge in the groove:" if VSEAT else ", anchor held by its preload:") if ANCHOR2 else ":"))
for node, name in (("LD2", "rack B on the upper piece"), ("LD1", "rack A on the lower piece")):
    rs = [anchored(node, R_go, v, ANCHOR_MODES[0])[0] for v in VARIANTS]
    S = [abs(r["screw"][0]) for r in rs]
    P1 = [max(abs(r["post 1"][1]), abs(r["post 1"][2])) for r in rs]
    P2 = [max(abs(r["post 2"][1]), abs(r["post 2"][2])) for r in rs]
    print(f"  {name}: M2.5 force {min(S):.0f}..{max(S):.0f} N; first post moment {min(P1):.0f}..{max(P1):.0f} N.mm; "
          f"second post moment {min(P2):.0f}..{max(P2):.0f} N.mm")
if ANCHOR2:
    print(f"anchor (as built): M3 x 45 at {tuple(C.ANCHOR_XY)}, stack {STACK:.2f}"
          + (f" + Ø{WASHER_M3[0]:g} x {WASHER_M3[1]:g} washer" if VSEAT else "") + f", {L_ANCHOR:.2f} engaged in CAD "
          f"({L_ANCHOR_EFF:.2f} with the worst-case float); post foot "
          f"z {Z_FOOT:.2f}" + (f"; V-ridge flank band z {TIP_SEATED:.3f}..{Z_BLOCK_PR:.2f} ({FLANK_L:.2f} of flank) over "
                               f"{L_V:.1f}, root {RIDGE_B:.1f} wide; x held at z {Z_XR:.2f}" if VSEAT else ""))
    for node, name in (("LD2", "rack B on the upper piece"), ("LD1", "rack A on the lower piece")):
        for R, lab in ((R_go, "opening stall"), (R_co, "crash"), (R_proof, "spec §8 proof push")):
            for mode in ANCHOR_MODES:
                out = [anchored(node, R, v, mode) for v in VARIANTS]
                A = [abs(r["anchor"][0]) for r, _ in out]
                Z = [r["anchor z"][0] for r, _ in out]
                Rg = [rg for _, rg in out]
                print(f"  {name}, {lab} {R:.1f} N, {mode:9s}: anchor x {min(A):5.1f}..{max(A):5.1f} N, z "
                      f"{min(Z):+5.1f}..{max(Z):+5.1f} N (+ = lift)"
                      + (f"; screw (wedge + lift) {max(a + max(z, 0.0) for a, z in zip(A, Z)):.1f} N, + preload "
                         f"{max(a + max(z, 0.0) for a, z in zip(A, Z)) + P_M3:.1f} N" if VSEAT else
                         f"; push carried before the shank bears {min(Rg):.1f}..{max(Rg):.1f} N"))
    fr = []
    for v in VARIANTS:
        ANCHOR_KX = 0.0
        fr.append(abs(cover_frame("LD2", 1.0, *v)["_u"]["AN"][0]))
    ANCHOR_KX = K_ANCHOR_X
    print(f"  foot sliding freely (no x hold at all): {min(fr) * 1000:.1f}..{max(fr) * 1000:.1f} um per N of rack-B push"
          + ("" if VSEAT else f", so {GAP_NOM:.2f} mm closes at {GAP_NOM / max(fr):.1f}..{GAP_NOM / min(fr):.1f} N and "
             f"{GAP_MAX:.2f} mm at {GAP_MAX / max(fr):.1f}..{GAP_MAX / min(fr):.1f} N (opening stall {R_go:.1f}, crash "
             f"{R_co:.1f}, hand {R_hand:.1f})"))


def seat_line(lab, s_):
    print(f"    {lab:34s}: stops on the {s_['by']}; play {s_['play']:.3f}; top-wall gap {s_['top_gap']:.3f}, tip over "
          f"the 17.2 layer {s_['tip_gap']:.3f}, flats over the block {s_['flat_gap']:.3f}")


if ANCHOR2 and VSEAT:
    print("\nThe V-seat AS PRINTED (reviewer's slice: bulkhead 48.4, rail block 17.8, groove corners 0.1 inside the CAD "
          "flank, open 0.3 slot in the 17.0..17.2 layer; cover to CAD). Tolerances (3 sigma): " +
          ", ".join(f"{k} +-{v:.3f}" for k, v in TOL.items()) + f"; corner radius {R_BEAD[0]}..{R_BEAD[2]}:")
    seat_line("nominal (r 0.075)", SEAT["nominal"])
    print("    RSS margin of the ridge over each other stop (> 0: the ridge lands first): "
          + "; ".join(f"{k} {v:+.3f}" for k, v in SEAT["rss_margin"].items()))
    seat_line("worst case, any build", SEAT["worst"][1])
    seat_line("worst case step 9 accepts (0.03 in)", SEAT["worst_accepted"][1])
    print(f"    play: nominal {PLAY_NOM:.3f}, RSS {PLAY_RSS:.3f}, worst {PLAY_WORST:.3f} (top wall first: step 9 rejects "
          f"it), worst accepted {PLAY_ACC:.3f} (tip first: no feeler sees it)")
    print(f"    top-wall gap before the screws: nominal {G_TOP:.3f}, RSS-high {G_TOP_RSS:.3f}, range "
          f"{SEAT['top_gap_range'][0]:.3f}..{SEAT['top_gap_range'][1]:.3f}")
    print(f"    corners on the flank at first contact (lift {LIFT_NOM:.3f}, tip {P.RIDGE_TIP_Z + LIFT_NOM:.3f}): {CORNERS0}")
    for fl, (d, n) in SEAT_D.items():
        print(f"    anchor's {P_M3:.0f} N seating at {fl:.0f} MPa flow: descent {d:.3f}, {n} corners per flank carrying; "
              f"tip at {P.RIDGE_TIP_Z + LIFT_NOM - d:.3f}")
    for lab, (gn, gr, gw) in G_AFTER.items():
        print(f"    top wall over the printed bulkhead after the anchor ({lab}): nominal {gn:.3f}, RSS-high {gr:.3f}, "
              f"worst {gw:.3f}")
    print(f"    flank band for the bearing rows: {FLANK_H:.3f} tall ({FLANK_L:.3f} of flank) after the least crush; "
          f"{FLANK_H0:.3f} at first contact (information); ridge root {RIDGE_B:.2f} wide, resultant z {Z_XR:.2f}, "
          f"arm {RIDGE_ARM:.2f} Fx")
    print(f"    M3 x 45 engaged from the printed block top: {L_ANCHOR_EFF:.2f} with the worst standing after the anchor "
          f"({FLOAT_W:.3f}); {L_ANCHOR:.2f} in CAD")
    print("    the proud top wall pulled down by the top M3s (gap at the screw after seating; bend share "
          f"{SHARE:.2f}, k_bend {K_BEND:.0f} N/mm, k_tilt {K_TILT:.0f} N/mm):")
    for (lab, case), (g, d_b, F_, s_) in FORCED.items():
        print(f"      {lab:16s} {case:8s}: gap {g:.3f}, wall bent {d_b:.3f}, screw force to close {F_:.0f} N, top-face "
              f"stress {s_:.1f} MPa (corner {KT_SHARP * s_:.1f} MPa compression)")
    print(f"  verdict rows below: the worse of 'locked' (play 0: nominal, RSS, every build step 9 accepts but the tip "
          f"case) and the worst accepted play {PLAY_ACC:.3f} mm (preload gone)")
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
    (sf, k), best = reversed_worst(modes=ANCHOR_MODES)
    print(f"  {'as built (round 6): ridge-first, locked + worst accepted play ' + f'{PLAY_ACC:.3f}':78s}: lowest SF {sf:.2f} "
          f"({k}); most favourable variant {best:.2f}")
    for modes in ((f"slip {GAP_NOM:.2f}",), (f"slip {GAP_MAX:.2f}",)):
        (sf, k), best = reversed_worst(modes=modes)
        print(f"  {'round 4 for reference: no ridge, preload gone, ' + modes[0]:78s}: lowest SF {sf:.2f} ({k}); most "
              f"favourable variant {best:.2f}")
    print(f"What-if, the anchor's head on the top wall at the {P_M3:.0f} N preload (sustained, req 4):")
    for lab, od in ((f"bare socket head dk {HEAD_DK}", HEAD_DK), (f"+ M3 washer Ø{WASHER_M3[0]:g} x {WASHER_M3[1]:g}",
                                                                     WASHER_M3[0])):
        print(f"  {lab:32s}: bearing SF {BEARING / (P_M3 / head_area(od)):.2f}")
    # the ridge's play: any play left between the ridge and the groove's printed layer corners is free slide before the
    # flank bears (preload gone):
    print("What-if, play left between the ridge and the groove's flank in x (preload gone; both reversed pushes, all "
          "variants):")
    for gap in (0.0, 0.025, 0.04, 0.05, 0.075, 0.1):
        (sf, k), best = reversed_worst(modes=(f"slip {gap}",))
        print(f"  play {gap:5.3f} mm: lowest SF {sf:.2f} ({k})")
    if VSEAT:
        print("The as-built seat's play cases (as printed) -> lowest SF over the frame model (both reversed pushes, all "
              "variants):")
        for lab, pl in (("nominal", PLAY_NOM), ("RSS", PLAY_RSS), ("worst accepted by step 9", PLAY_ACC),
                        ("worst, any build (step 9 rejects)", PLAY_WORST)):
            (sf, k), best = reversed_worst(modes=(f"slip {pl:.3f}",))
            print(f"  {lab:34s} play {pl:.3f} mm: lowest SF {sf:.2f} ({k})")
        (sf, k), best = reversed_worst(modes=("locked",))
        print(f"  zero play, 'locked': lowest SF {sf:.2f} ({k})")
        # the ridge's rows at the opening stall and the proof push (Fx from the zero-play frame model), with the bound of
        # all the flank force on the groove's top layer corner
        FXP = max(abs(anchored("LD2", R_proof, v, "locked")[0]["anchor"][0]) for v in VARIANTS)
        armT = ARM_TOP
        print(f"The ridge (apex {P.RIDGE_APEX_Z:.2f}, flats {P.TIE2_FOOT_Z:.2f}: printed root {RIDGE_B:.1f} wide; "
              f"seated tip {TIP_SEATED:.3f}; flank band {FLANK_L:.2f} x {L_V:.1f}):")
        for Fx_, lab, req in ((FX_LOCK, "opening stall", SF_SHORT), (FXP, "spec §8 proof push", SF_SHORT / 1.5)):
            brg = Fx_ * math.sqrt(2) / (FLANK_L * L_V)
            sh = 1.5 * Fx_ / (RIDGE_B * L_V)
            rt = Fx_ / (RIDGE_B * L_V) + KT_RIDGE * 6 * Fx_ * RIDGE_ARM / (RIDGE_B ** 2 * L_V)
            rtT = Fx_ / (RIDGE_B * L_V) + KT_RIDGE * 6 * Fx_ * armT / (RIDGE_B ** 2 * L_V)
            print(f"  {lab}, Fx {Fx_:.1f} N: flank bearing {brg:.2f} MPa SF {BEARING / brg:.2f}; root shear SF "
                  f"{ALLOW_XY / 2 / sh:.2f}; root (resultant z {Z_XR:.1f}, arm {RIDGE_ARM:.2f}) SF {ALLOW_XY / rt:.2f}; "
                  f"root, all on the top corner (arm {armT:.2f}) SF {ALLOW_XY / rtT:.2f} (req {req:.0f})")
        # the frame's side of the seat, for the frame's strength_calc.py (its section 6 states these numbers)
        print("For the frame (worst of the variants): anchor Fx, lift, screw tension without / with the preload:")
        for R, lab in ((R_go, "opening stall"), (R_co, "crash"), (R_proof, "proof push")):
            for mode in ANCHOR_MODES:
                rs = [anchored("LD2", R, v, mode)[0] for v in VARIANTS]
                Fx_ = max(abs(r["anchor"][0]) for r in rs)
                T_ = max(abs(r["anchor"][0]) + max(r["anchor z"][0], 0.0) for r in rs)
                Fz_ = max(max(r["anchor z"][0], 0.0) for r in rs)
                print(f"  {lab:14s} {mode:11s}: Fx {Fx_:.1f} N, lift {Fz_:.1f} N, wedge + lift {T_:.1f} N, + preload "
                      f"{T_ + P_M3:.1f} N")
# review: the top M3s' tension from the frame model's own top-joint reactions (replaces the frame's 'all of the moment on
# the top screws' bound), worst over the variants and the two play modes, per case
if ANCHOR2:
    print("For the frame: the top M3s' tension from the top joint (worst of the variants and modes; y 14 / y -23):")
    TOPT = {}
    for node, nm in (("LD2", "upper piece (rack B pushed)"), ("LD1", "lower piece (rack A pushed)")):
        for R, lab in ((R_go, "opening stall"), (R_co, "crash"), (R_proof, "proof push")):
            Ts = [top_screw_T(anchored(node, R, v, m)[0]) for m in ANCHOR_MODES for v in VARIANTS]
            TOPT[(nm, lab)] = (max(t[0] for t in Ts), max(t[1] for t in Ts))
            print(f"  {nm:28s} {lab:14s}: {TOPT[(nm, lab)][0]:6.1f} / {TOPT[(nm, lab)][1]:6.1f} N")
    _a2 = ANCHOR2
    ANCHOR2 = False
    Ts = [top_screw_T(cover_frame("LD2", R_go, *v)) for v in VARIANTS]
    ANCHOR2 = _a2
    print(f"  for reference, no anchor at all (round 3): upper piece, opening stall: {max(t[0] for t in Ts):.1f} / "
          f"{max(t[1] for t in Ts):.1f} N")
print("What-if, the snug preloads (sustained, req 4): heads and fixes")
print(f"  top M3 pan head Ø{M3_PAN_DK} bare, {P_M3:.0f} N: SF {BEARING / (P_M3 / A_M3_PAN):.2f}; on a Ø7 x 0.5 washer: SF "
      f"{BEARING / (P_M3 / head_area(7.0)):.2f}")
print(f"  front M2.5 pan head Ø5, {P_M25:.0f} N: SF {BEARING / (P_M25 / A_HEAD):.2f}; on a Ø6 x 0.5 washer: SF "
      f"{BEARING / (P_M25 / A_M25_W6):.2f} (the washer needs the screws at z 2.5: at z 3 it touches jaw B's neck, "
      f"exact solids); preload for SF 4 on the bare head: {BEARING / 4 * A_HEAD:.0f} N")
for z_s in (3.0, 2.5):
    T_s = R_go * z_rbg / z_s
    print(f"  M2.5 at z {z_s}: the stall's {T_s:.0f} N on one screw: bare head SF {BEARING / (T_s / A_HEAD):.2f}, on the "
          f"Ø6 washer {BEARING / (T_s / A_M25_W6):.2f}, pull-out ({L_M25:.1f} engaged) "
          f"{SHEAR_Z / (T_s / (math.pi * 2.5 * L_M25)):.2f}")
print("What-if, strip under slot B (yaw stall, the worse of closed / open):")
for d in (STRIP_D - 2.0, STRIP_D - 1.0, STRIP_D, STRIP_D + 2.0):
    w = max(strip_sf(d, F_YAW_Z, 0.0, C.NECK_Y), strip_sf(d, F_YAW_Z, C.STROKE, C.STROKE + C.NECK_Y))
    print(f"  strip {d:.2f} deep (FRONT_Z0 {ZB0 - d:+.0f}): SF {ALLOW_Z / w:.2f}")

# review: rack A rides under the top wall, so the cover's height sets rack A's mesh with the frame-held pinion. The cover
# rests on the ridge at +y (height = standing - 0.1 over CAD) and on the printed bulkhead at -y (48.4: -0.1, down to -0.2
# with the bulkhead and underside errors). Backlash change 2 da tan20 per mesh; tip clearance 0.40 + da; contact ratio
# with the rack's addendum 0.85 - da (both members topped 0.15 m).
if VSEAT:
    al = math.radians(20.0)
    r_b, r_a = C.R_P * math.cos(al), C.R_TIP
    rec = math.sqrt(r_a ** 2 - r_b ** 2) - C.R_P * math.sin(al)
    p_b = math.pi * C.M * math.cos(al)
    print("Rack A's mesh against the cover's height (da = rack A's guide over its CAD height):")
    for lab, da in (("-y end, top wall on the printed bulkhead, worst low", -0.2),
                    ("-y end, top wall on the printed bulkhead (48.4)", Z_BULK_PR - C.Z_TOP0),
                    ("+y end, after the anchor, nominal", G_AFTER["least crush, 80 MPa"][0] - 0.1),
                    ("+y end, after the anchor, RSS-high", G_AFTER["least crush, 80 MPa"][1] - 0.1),
                    ("+y end, after the anchor, worst", G_AFTER["least crush, 80 MPa"][2] - 0.1),
                    ("+y end, before any screw, worst", G_TOP_W - 0.1)):
        eps = ((C.M - C.TIP_RELIEF - da) / math.sin(al) + rec) / p_b
        print(f"  {lab:52s} da {da:+.3f}: backlash {C.BACKLASH + 2 * da * math.tan(al):.3f}, tip clearance "
              f"{0.40 + da:.3f}, contact ratio {eps:.2f}")

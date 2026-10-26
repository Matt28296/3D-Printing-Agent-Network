"""Strength check, round 6, CAD ENGINEER'S SELF-CHECK (an independent review follows): jobs/20261026-arm-claw-cover
(front plate in two pieces + two ties, top wall, 8 mm lip, the second tie's 8 mm post located on the frame's rail block by
a 90° V-ridge in a V-groove and anchored there by one vertical M3 x 45 with a Ø7 x 0.5 washer under its head).

Round 6 design (the round 5 review's required fix, user-approved: ridge-first contact): VSEAT_CLR 0, so the ridge is the
groove's own V (virtual apex 16.95, flanks line to line in CAD); the foot's flats decoupled and raised, TIE2_FOOT_Z =
ZS - RAIL_IN + FOOT_CLR 0.30 = 18.05, with the ridge's 45° flanks carried on up to them (root 2.2 wide); the tip at 17.35
(absolute); the frame's bulkhead top at 48.45 (prints 48.4, off the slice plane). As printed (round 6 scratch slice, read
back: frame bulkhead 48.4, block 17.8, groove corners 0.1 inside the CAD flank; the cover's ridge, tip and flats to CAD)
the ridge reaches both flanks first: play 0 at nominal and RSS, 0.029 at the worst-case stack (which BUILD_GUIDE §4 step
9's 0.03 feeler rejects). The verdict rows therefore run 'locked' (zero play, the preload added to the screw where it
makes a row worse) AND at the worst-case play with the preload gone; the worse of the two is reported. The M3 x 45's
engagement is taken with the worst-case float of the top wall after seating (10.49 instead of 10.75).

Round 5 design (user-approved fix of round 4's FAIL): the post's foot carries a 90° ridge (0.1 clear per flank in CAD,
horizontal; tip cut flat at z 17.25) in a matching 0.8 mm groove in the rail block's top; the foot's flats stand 0.1 over
the block in CAD (TIE2_FOOT_Z 17.85). A +x push on the foot is held by the ridge's flank once it bears; the 45° flank
turns it into a lift equal to it (frictionless, the worst case), and the M3 x 45 holds that in tension.

What this review adds (strength-analyst, independent of the CAD engineer's round-5 self-check):
- THE SEAT AS PRINTED (section "the V-seat AS PRINTED" below). The frame was sliced with the arm's own command and the G-code
  read back: its bulkhead top (CAD 48.5, on a slice plane) prints at 48.4 and its rail block top (CAD 17.75) at 17.8.
  So the cover stops on the foot's flats or on the ridge, not on the top wall, and the ridge's x play is
  -0.05 + the groove's layer-corner rounding + the two flanks' print errors: about zero nominal, but up to ~0.08 mm
  (RSS) / ~0.13 mm (worst case) with realistic MK3 tolerances. Play over 0.04 mm takes every frame-model row's lowest
  SF under 3 (the slip what-if). The verdict rows are therefore run at the realistic (RSS-adverse) play, not at zero.
- The ridge's root: Kt 1.7 (a bead-filled 135° re-entrant corner, r/h 0.15..0.25) instead of 2.5, with the flank force
  at the printed corners' resultant (z 17.6); the bound with all of it on the top corner (z 17.8) is an info row.
- A fix (what-if, computed): VSEAT_CLR 0 (ridge flanks on the CAD groove flanks), the foot's flats decoupled and raised
  to 0.3 over the CAD block (TIE2_FOOT_Z 18.05, flanks carried on to them), the tip at 17.35, and the frame's bulkhead
  top off the slice plane (48.45, still prints 48.4). The ridge then always reaches both flanks first (zero play even at
  the worst-case stack, ~0.03), and BUILD_GUIDE's top-wall feeler can prove it.

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
# ---------------------------------------------------------------- the V-seat AS PRINTED (round 5 review; round 6 re-read)
# Round 6 scratch slice (CAD engineer) of BOTH round-6 part.stl files with the arm's own command (slice_settings.json:
# PrusaSlicer 2.7.2, 0.20mm QUALITY @MK3, Prusament PETG, each job's slice_overrides.ini; first layer 0.2, every layer
# sliced at its mid-height, Arachne perimeters), G-code read back; not a job file:
#   frame: last layer ;Z:48.4: the bulkhead top (CAD 48.45 since round 6, 0.05 under the slice plane 48.5) prints at 48.4,
#          and so do both ribs. The rail block top (CAD 17.75) prints at 17.8. The groove's external perimeters (frame
#          y 26, centre x 15.25, w 0.45) put its walls at half-widths 0.15 / 0.35 / 0.55 / 0.75 in the layers ending
#          17.2 / 17.4 / 17.6 / 17.8 (the round 5 review's numbers); the 0.3 mm first layer is a slot that closes up.
#   cover: external perimeters 0.225 (w 0.45) inside the CAD faces at layers G y 25.9 / 27.9 / 30.1: the ridge's flanks,
#          its tip (17.35) and the foot's flats (18.05) print to CAD.
Z_BULK_PR = 48.4                 # printed bulkhead top
Z_BLOCK_PR = 17.8                # printed rail block top
Z_SLOT_TOP = 17.2                # top of the groove's closed first layer
Z_GROOVE_APEX = Z_BLOCK - C.VSEAT_D if VSEAT else Z_BLOCK    # 16.95
if VSEAT:
    # the V-seat (claw_frame.py VSEAT_*, this model's RIDGE_*): the ridge's flanks bear on the groove's printed layer
    # corners from its flat tip (z 17.35) up to the printed block top (17.8): 0.45 tall, 0.64 of flank on each side. The
    # ridge's root is 2.2 wide at the flats (18.05).
    # Where the flank force acts: the frame prints in 0.2 mm layers sliced at mid-height, so the groove's flank is a
    # staircase whose layer-top corners stand 0.1 (horizontal) inside the CAD flank: z 17.4, 17.6 and 17.8 (the block's
    # top layer, sliced at 17.7, prints to 17.8). The ridge meets exactly those corners, so the flank's resultant is taken
    # at their middle, z 17.6.
    FLANK_H = Z_BLOCK_PR - P.RIDGE_TIP_Z                  # 0.45
    FLANK_L = FLANK_H * math.sqrt(2)                      # 0.64 of flank on each side
    RIDGE_B = 2 * (P.TIE2_FOOT_Z - P.RIDGE_APEX_Z)        # 2.2
    L_V = C.TIE2_Y[1] - (C.TIE2_Y[0] + (P.TIE2_FOOT_Z - P.RIDGE_TIP_Z))   # 7.3: full-depth ridge y 24.7..32 (lead-in ignored)
    _corners = [LAYER * k for k in range(1, 200) if P.RIDGE_TIP_Z < LAYER * k <= Z_BLOCK + LAYER / 2 + 1e-9]
    Z_XR = sum(_corners) / len(_corners)                  # 17.6 (corners 17.4, 17.6, 17.8)
    # the flank's normal force (-1, +1)/sqrt2 per unit, at (VSEAT_XC + z_c - apex, z_c): its moment about the root's
    # centroid (VSEAT_XC, the flats) is Fx (2 z_c - flats - apex): 0.2 Fx at z_c 17.6 (round 6; round 5 0.3 Fx)
    RIDGE_ARM = abs(2 * Z_XR - P.TIE2_FOOT_Z - P.RIDGE_APEX_Z)
else:
    Z_XR = Z_FOOT
KT_RIDGE = 1.7      # review: the ridge's root corners are 135° re-entrant corners, filled by the printed bead (r ~0.1..0.15
                    # against a 0.7 tall ridge -> 1.7 in the strength-checks table), not sharp 90° ones
# Each groove layer's top corner stands LAYER/2 = 0.1 inside the CAD flank (horizontal): corner half-width z - 17.05.
# Its bead is rounded (stadium edge, radius up to h/2 = 0.1): a radius r moves the 45° ridge's contact (2 - sqrt2) r
# further out, horizontally.
K_ROUND = 2 - math.sqrt(2)       # 0.586
R_BEAD = (0.05, 0.075, 0.10)     # corner radius: low / nominal / high (round 5 reviewer's assumption)
# Realistic MK3 / PETG tolerances (round 5 reviewer's assumption, no library data yet), each a 3-sigma bound:
TOL_RIDGE_N = 0.05               # the ridge's flank, normal to its 45° face (cover, in the print plane) -> x sqrt2
TOL_GROOVE = 0.05                # the groove's layer walls (frame, vertical perimeter walls), horizontal
TOL_COVER = 0.05                 # the cover's top-wall underside to its foot, 31 mm in the print plane (contour + scale)


def seat(apex_cad, z_flat, z_tip, e_c=0.0, e_rh=0.0, e_g=0.0, r=R_BEAD[1], z_bulk=Z_BULK_PR):
    """The cover lowered onto the PRINTED frame. U = its top wall underside (48.5 in CAD). Returns where it stops and
    the ridge's x play there (horizontal, per flank). apex_cad: the ridge's virtual apex with U = 48.5.
    e_c > 0: the foot printed lower against the top wall; e_rh > 0: the ridge fatter (per flank, horizontal);
    e_g > 0: the groove's walls stand further in (per wall); r: the groove corners' rounding."""
    u0 = C.Z_TOP0
    corner = Z_GROOVE_APEX + LAYER / 2                     # 17.05: corner half-width = z - 17.05
    stops = {"ridge on both flanks": u0 + corner + e_rh + e_g - K_ROUND * r - apex_cad + e_c,
             "top wall on the bulkhead": z_bulk,
             "foot flats on the block": u0 + (Z_BLOCK_PR - z_flat) + e_c,
             "ridge tip on the closed first layer": u0 + (Z_SLOT_TOP - z_tip) + e_c}
    gov = max(stops, key=stops.get)
    U = stops[gov]
    u_r = stops["ridge on both flanks"]
    return {"U": U, "by": gov, "play": max(0.0, U - u_r), "interf": u_r - z_bulk, "top_gap": U - z_bulk,
            "flat_gap": U - stops["foot flats on the block"], "tip_gap": U - stops["ridge tip on the closed first layer"]}


def seat_cases(apex_cad, z_flat, z_tip, z_bulk=Z_BULK_PR):
    """Nominal; RSS-adverse (the 3-sigma ellipsoid point that maximises the play, for each stop that can govern);
    worst case (every tolerance at its limit, adverse). Each: (play, the seat dict)."""
    tol = {"e_c": TOL_COVER, "e_rh": TOL_RIDGE_N * math.sqrt(2), "e_g": TOL_GROOVE}
    nom = seat(apex_cad, z_flat, z_tip, z_bulk=z_bulk)
    # the play a stop leaves, (stop height) - (ridge contact height), is linear in the errors:
    #   top wall:  z_bulk - 48.5 - 17.05 + apex - e_rh - e_g - e_c + K r
    #   flats:     17.8 - z_flat - 17.05 + apex - e_rh - e_g + K r          (e_c cancels)
    #   tip:       17.2 - z_tip - 17.05 + apex - e_rh - e_g + K r           (e_c cancels)
    # RSS-adverse = nominal + sqrt(sum of (tolerance x sensitivity)^2), the corner radius nominal -> high as one term
    corner = Z_GROOVE_APEX + LAYER / 2
    rr = K_ROUND * (R_BEAD[2] - R_BEAD[1])
    base = {"top wall on the bulkhead": (z_bulk - C.Z_TOP0 - corner + apex_cad, ("e_c", "e_rh", "e_g")),
            "foot flats on the block": (Z_BLOCK_PR - z_flat - corner + apex_cad, ("e_rh", "e_g")),
            "ridge tip on the closed first layer": (Z_SLOT_TOP - z_tip - corner + apex_cad, ("e_rh", "e_g"))}
    best_rss = (0.0, nom, "none")
    for stop, (g0, ks) in base.items():
        g = g0 + K_ROUND * R_BEAD[1] + math.sqrt(sum(tol[k] ** 2 for k in ks) + rr ** 2)
        if g > best_rss[0]:
            best_rss = (g, nom, stop)
    worst = (0.0, nom)
    for sc in (-1, 1):
        for sr in (-1, 1):
            for sg in (-1, 1):
                for r in R_BEAD:
                    s = seat(apex_cad, z_flat, z_tip, z_bulk=z_bulk, r=r, e_c=sc * tol["e_c"], e_rh=sr * tol["e_rh"],
                             e_g=sg * tol["e_g"])
                    if s["play"] >= worst[0]:
                        worst = (s["play"], s)
    hi = max((seat(apex_cad, z_flat, z_tip, z_bulk=z_bulk, r=r, e_c=sc * tol["e_c"], e_rh=sr * tol["e_rh"],
                   e_g=sg * tol["e_g"])["interf"] for sc in (-1, 1) for sr in (-1, 1) for sg in (-1, 1) for r in R_BEAD))
    rss_hi = nom["interf"] + math.sqrt(sum(tol[k] ** 2 for k in tol) + (K_ROUND * 0.025) ** 2)
    return {"nominal": (nom["play"], nom), "RSS": best_rss, "worst": worst, "interf_hi_rss": rss_hi, "interf_hi": hi}


if VSEAT:
    SEAT_NOW = seat_cases(P.RIDGE_APEX_Z, P.TIE2_FOOT_Z, P.RIDGE_TIP_Z)     # round 6 as built
    PLAY_RSS = round(SEAT_NOW["RSS"][0], 3)               # 0 with ridge-first contact
    PLAY_WORST = round(SEAT_NOW["worst"][0], 3)           # 0.029: the worst-case stack (step 9's 0.03 feeler rejects it)
    # round 5 for reference: apex 17.05 (VSEAT_CLR 0.1), flats 17.85 (tied to it), tip 17.25 (apex + 0.2)
    R5 = {"apex": Z_GROOVE_APEX + 0.1, "flat": Z_BLOCK + 0.1, "tip": Z_GROOVE_APEX + 0.3}
    SEAT_R5 = seat_cases(R5["apex"], R5["flat"], R5["tip"])
    # Seating: the ridge holds the top wall up until the screws crush the groove's layer corners: 3 corners a flank
    # crushed flat at ~40 MPa (PETG compressive flow, assumption), contact width sqrt2 x the interference
    K_CRUSH = 2 * 40.0 * len(_corners) * L_V              # N per mm of vertical interference (~1750)
    SEATING = {}
    for lab, Fc in (("anchor alone, 150 N", P_M3), ("anchor + the +y top screw's share (0.77 x 150 N)", P_M3 * 1.77)):
        ic = Fc / K_CRUSH
        SEATING[lab] = (ic, max(0.0, SEAT_NOW["nominal"][1]["interf"] - ic), max(0.0, SEAT_NOW["interf_hi"] - ic))
    FLOAT_W = SEATING["anchor alone, 150 N"][2]          # worst-case float of the top wall after the anchor alone (0.256)
    L_ANCHOR_EFF = L_ANCHOR - FLOAT_W                     # 10.49: the M3 x 45's engagement with that float
else:
    PLAY_RSS = PLAY_WORST = FLOAT_W = 0.0
    L_ANCHOR_EFF = L_ANCHOR
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
            out[f"V-ridge: flank bearing on the groove's 45° flank (contact band z {P.RIDGE_TIP_Z:.2f}..{Z_BLOCK_PR:.2f}, "
                f"the printed layer corners)"] = (
                N_fl / (FLANK_L * L_V), BEARING, "bearing",
                f"normal {N_fl:.1f} N on {FLANK_L:.2f} x {L_V:.1f} (the {P.TIE2_FOOT_Z - P.RIDGE_TIP_Z:.1f} lead-in ignored)")
            out[f"V-ridge root at the foot's flats (z {P.TIE2_FOOT_Z:.2f}): shear"] = (
                1.5 * Fx / (RIDGE_B * L_V), ALLOW_XY * 0.5, "XY shear", f"{RIDGE_B:.1f} x {L_V:.1f}, Fx {Fx:.1f} N")
            out[f"V-ridge root at the foot's flats: the flank force's moment ({RIDGE_ARM:.2f} Fx, resultant at the printed "
                f"layer corners, z {Z_XR:.1f}) + the wedge's compression, Kt {KT_RIDGE}"] = (
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
# round 6: the verdict rows run with the ridge's play AS PRINTED. Ridge-first contact gives zero play at nominal and RSS
# ('locked': the ridge holds x, the preload added to the screw), and PLAY_WORST at the worst-case stack (the foot slides
# that far before the flank bears, the preload gone); every row takes the worse of the two
ANCHOR_MODES = (("locked", f"slip {PLAY_WORST:.3f}") if VSEAT else ("held", f"slip {GAP_NOM:.2f}", f"slip {GAP_MAX:.2f}")) \
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
                                                 f"; ridge play {mode.split()[1]} mm (worst-case stack, preload gone)"
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
    ARM_TOP = abs(2 * Z_BLOCK_PR - P.TIE2_FOOT_Z - P.RIDGE_APEX_Z)
    row(f"info, bound: opening stall with zero play, Fx {FX_LOCK:.1f} N all on the groove's top layer corner (z "
        f"{Z_BLOCK_PR}): V-ridge root at the flats, Kt {KT_RIDGE}",
        f"{RIDGE_B:.1f} x {L_V:.1f}, M {FX_LOCK * ARM_TOP:.1f} N.mm (arm {ARM_TOP:.2f})", "XY",
        FX_LOCK / (RIDGE_B * L_V) + KT_RIDGE * 6 * FX_LOCK * ARM_TOP / (RIDGE_B ** 2 * L_V), ALLOW_XY, SF_SHORT, INFO)

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
          f"z {Z_FOOT:.2f}" + (f"; V-ridge flank band z {P.RIDGE_TIP_Z:.2f}..{Z_BLOCK_PR:.2f} ({FLANK_L:.2f} of flank) over "
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


def seat_report(lab, apex, z_flat, z_tip, S):
    n, w = S["nominal"][1], S["worst"][1]
    print(f"  {lab}: ridge apex {apex:.2f}, flats {z_flat:.2f}, tip {z_tip:.2f} (CAD, top wall at 48.5)")
    print(f"    nominal (corner r {R_BEAD[1]}): stops on the {n['by']}, U {n['U']:.3f}: play {n['play']:.3f}; top-wall gap "
          f"{n['top_gap']:.3f}, gap under the flats {n['flat_gap']:.3f}, tip over the closed first layer "
          f"{n['tip_gap']:.3f}; ridge contact height above the bulkhead {n['interf']:+.3f}")
    print(f"    RSS-adverse: play {S['RSS'][0]:.3f} (left by the {S['RSS'][2]})")
    print(f"    worst case (every tolerance at its limit): play {S['worst'][0]:.3f}, stops on the {w['by']}; the "
          f"BUILD_GUIDE feelers would then read: top wall {w['top_gap']:.3f}, under the flats {w['flat_gap']:.3f}")
    lo = n["interf"] - math.sqrt(TOL_COVER ** 2 + 2 * TOL_RIDGE_N ** 2 + TOL_GROOVE ** 2
                                 + (K_ROUND * (R_BEAD[2] - R_BEAD[1])) ** 2)
    print(f"    ridge contact above the bulkhead (+ = the ridge holds the top wall up before the screws): nominal "
          f"{n['interf']:+.3f}, RSS {lo:+.3f}..{S['interf_hi_rss']:+.3f}, worst ..{S['interf_hi']:+.3f}")


if ANCHOR2 and VSEAT:
    print("\nThe V-seat AS PRINTED (round 6 slice: frame bulkhead top 48.4, rail block top 17.8, groove corners at the "
          "layer tops; the cover to CAD; tolerances: ridge flank +-%.2f normal, groove walls +-%.2f, cover top wall to "
          "foot +-%.2f, corner radius %.3f..%.2f):" % (TOL_RIDGE_N, TOL_GROOVE, TOL_COVER, R_BEAD[0], R_BEAD[2]))
    seat_report("as built (round 6, ridge-first)", P.RIDGE_APEX_Z, P.TIE2_FOOT_Z, P.RIDGE_TIP_Z, SEAT_NOW)
    for lab, (ic, fl_n, fl_w) in SEATING.items():
        print(f"    seating by the {lab}: crushes ~{ic:.3f} mm (K {K_CRUSH:.0f} N/mm) -> top wall left proud of the "
              f"bulkhead: nominal {fl_n:.3f}, worst {fl_w:.3f}")
    print(f"    M3 x 45 engaged {L_ANCHOR:.2f} in CAD, {L_ANCHOR_EFF:.2f} with the worst float after the anchor alone")
    seat_report("round 5 for reference", R5["apex"], R5["flat"], R5["tip"], SEAT_R5)
    print(f"  verdict rows below: the worse of 'locked' (play 0, nominal and RSS; preload on the screw) and the "
          f"worst-case play {PLAY_WORST:.3f} mm (preload gone)")
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
    print(f"  {'as built (round 6): ridge-first, locked + worst-case play ' + f'{PLAY_WORST:.3f}':78s}: lowest SF {sf:.2f} "
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
        for lab, (pl, *_rest) in (("nominal", SEAT_NOW["nominal"]), ("RSS-adverse", SEAT_NOW["RSS"]),
                                  ("worst case", SEAT_NOW["worst"])):
            (sf, k), best = reversed_worst(modes=(f"slip {pl:.3f}",))
            print(f"  {lab:12s} play {pl:.3f} mm: lowest SF {sf:.2f} ({k})")
        (sf, k), best = reversed_worst(modes=("locked",))
        print(f"  zero play, 'locked': lowest SF {sf:.2f} ({k})")
        # the ridge's rows at the opening stall and the proof push (Fx from the zero-play frame model), with the bound of
        # all the flank force on the groove's top layer corner
        FXP = max(abs(anchored("LD2", R_proof, v, "locked")[0]["anchor"][0]) for v in VARIANTS)
        armT = abs(2 * Z_BLOCK_PR - P.TIE2_FOOT_Z - P.RIDGE_APEX_Z)
        print(f"The ridge (apex {P.RIDGE_APEX_Z:.2f}, flats {P.TIE2_FOOT_Z:.2f}: root {RIDGE_B:.1f} wide; tip "
              f"{P.RIDGE_TIP_Z:.2f}; flank band {FLANK_L:.2f} x {L_V:.1f}):")
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
print("What-if, strip under slot B (yaw stall, the worse of closed / open):")
for d in (STRIP_D - 2.0, STRIP_D - 1.0, STRIP_D, STRIP_D + 2.0):
    w = max(strip_sf(d, F_YAW_Z, 0.0, C.NECK_Y), strip_sf(d, F_YAW_Z, C.STROKE, C.STROKE + C.NECK_Y))
    print(f"  strip {d:.2f} deep (FRONT_Z0 {ZB0 - d:+.0f}): SF {ALLOW_Z / w:.2f}")

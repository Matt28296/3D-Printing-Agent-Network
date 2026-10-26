"""Shared geometry of the parallel claw (rack-and-pinion) and its Brio 4K camera mount.

Every claw model.py, assembly_check.py, claw_sequence_check.py and viz_export.py import this
file, so the parts always agree. Round 2 (2026-10-26): deep review 01 B1/B2 and 03 SYS-01/SYS-08,
plus every required fix of the claw DFM and strength round 1 (see each claw job's log.md).

CLAW frame G (same as the old gripper-base frame, so the forearm and wrist do not change):
  origin = the wrist axis, on the claw frame's back face (the face on the wrist horn)
  +x     = towards the fingertips
  +z     = away from the wrist servo (outboard; world +Y when the arm is in its plane)
  y      = completes the frame, in the arm plane; the jaws close along y

Layout along x: wrist horn (x 0) | claw MG90S body behind the bulkhead | bulkhead (x 3.5..10)
| claw servo's upper case, rail block below it (x 10..22.35) and lip wall above it (x 14.35..22.35) | pinion and both
racks (x 22.6..34.6) | cover front plate (x 34.85..39.85, with the pinion pass-through) | finger blades (x 40.35..83.35).
Round 3 (2026-10-26): every required fix of the claw DFM and strength round 2 (see each claw job's design_brief.md).
Layout along z (pinion axis at ZS 27.25): wrist plate (z 0..6, rack B rides on its top face)
| rack B (teeth up) | pinion | rack A (teeth down, rides under the top wall) | cover top wall
(z 48.5..51.5) | camera mount.
Jaw A (upper rack) carries the finger on the -y side; jaw B is the SAME part turned 180° about
the pinion axis (x), carrying the finger on the +y side. Turning the pinion positive about +x
moves rack A to -y and rack B to +y: the claw opens.

Assembly (SYS-01 fix A): frame on the wrist horn -> claw servo from the front -> cover -> both
jaws slid in from the open ends of their slots to fully open -> pinion pushed in last, axially,
through the front plate's pass-through hole. claw_sequence_check.py proves each step.
"""
from __future__ import annotations

import math

from hobby_parts import MG90S, MG90S_DOUBLE, link_back_z

# --- servos and horns -------------------------------------------------------------------
SERVO = MG90S                  # claw servo (B2: its own spec, spline top 14.0 above the tabs)
WRIST_HORN = MG90S             # single-arm horn in the frame's back-face pocket
PINION_HORN = MG90S_DOUBLE     # double-arm horn, both arms CUT to HORN_TRIM_R, inside the pinion
HORN_TRIM_R = 5.5              # cut each horn arm 5.5 mm from the centre and file the ends round (fits a Ø11 circle)

# --- gearing (pinion strength round 1: tool root fillet + face 10; SYS-08: 0.35 total backlash) ---
M = 1.0                        # module
Z_TEETH = 20                   # even: the pinion looks the same to both racks (symmetric jaws)
R_P = M * Z_TEETH / 2          # 10.0 pitch radius: 21.6 N per rack at the MG90S stall (24 N with 18 teeth)
TIP_RELIEF = 0.15 * M          # pinion and rack tips topped 0.15 m: tip clearance 0.25 -> 0.40 (SYS-08 stack-up)
R_TIP = R_P + M - TIP_RELIEF   # 10.85: pinion outside radius as made
FACE_W = 12.0                  # pinion and rack face width (along x); 10 -> 12 (claw round 3, pinion strength round 2:
                               # tooth fillet SF 2.85 -> 3.60, racks 3.93)
BACKLASH = 0.40                # total per mesh (SYS-08: 0.3-0.4; claw_sequence_check measures it), split unevenly.
PINION_BACKLASH = 0.1          # gears.py thins a member's teeth by ITS backlash/2 at the pitch line: the pinion's by
RACK_BACKLASH = 0.7            # 0.05 (its radial-flank root is the weaker one), the racks' by 0.35 (their 2.2 mm roots);
                               # (0.1 + 0.7) / 2 = 0.40 (claw round 3: pry margin 0.08 -> 0.15 mm, pinion strength round 2)
PINION_ROOT_FILLET = 0.38 * M  # tools/gears.py root fillets (pinion DFM fix 3 / strength)
RACK_ROOT_FILLET = 0.30 * M
P_CIRC = math.pi * M           # rack pitch 3.14
DEG_PER_MM_GAP = math.degrees(1.0 / (2.0 * R_P))   # 2.865° of servo per mm of jaw gap: 0-44 mm in 126°

# --- clearances ------------------------------------------------------------------------
CLR = 0.25                     # sliding clearance at the racks' x faces (lip / rail behind, front plate in front)
RACK_SEAT = 0.0                # rack backs ride ON their guides (B on the wrist plate, A under the top wall): the
                               # separating force seats them there, so both meshes run at the nominal centre
                               # distance (SYS-08: the old 0.25 here made rack B tight and rack A loose)
SLOT_CLR = 0.25                # around the necks in the cover slots, on the faces nearer the axis. Slot A's outer
                               # edge IS the top wall's underside (the neck top rides there with the rack back);
                               # slot B keeps SLOT_CLR over the cover's strip (a different part from the wrist plate)

# --- racks (distances from the pinion axis) -------------------------------------------
RACK_BACK = 10.0               # solid behind the tooth roots: the neck sits on it (jaw strength round 1, candidate C)
RACK_TIP = R_P - M + TIP_RELIEF    # 9.15 (topped)
RACK_ROOT = R_P + 1.25 * M     # 11.25
RACK_OUT = RACK_ROOT + RACK_BACK   # 21.25: rack back face
RACK_Y = (-8 * math.pi * M, 10 * math.pi * M)   # jaw A's rack along y, CLOSED (-25.1..31.4): both ends in a
                               # tooth gap (no slivers); covers the neck + its root fillet and the mesh at full open
STROKE = 22.0                  # per jaw: opening 0..44 mm
RACK_EDGE_CHAMFER = 2.0        # 45° on the rack's back/front edge, y >= 4.5 only: clears the cover's r 2 corner
                               # fillet, whose tangent line on the top wall is 1.75 behind the rack's front face
RACK_EDGE_Y0 = 4.5             # chamfer starts beyond the neck's root fillet

# --- frame ----------------------------------------------------------------------------
T_W = 6.0                      # wrist plate (z 0..6); rack B rides on its top face
PAD_T = 2.3                    # raised pad on the wrist plate behind the bulkhead (strength fix 1): the wrist-clamp
                               # floor is T_W + PAD_T - HORN_DEPTH = 6.3 mm (clamp screw reaches 4.6 into the spline)
ZS = T_W + RACK_SEAT + RACK_OUT    # 27.25: pinion / claw-servo axis height
X_B = 10.0                     # bulkhead front face = claw servo's tab underside
BULK_T = 6.5                   # bulkhead x 3.5..10 (DFM R2: 1.9 mm walls beside the top pilots; washer at x <= 3)
X_REAR = -8.0                  # wrist plate rear edge
REAR_HALF = 32.0               # full width behind the bulkhead (strength fix 1: no 20 mm tail)
HALF_Y = 32.0                  # frame / cover half width
X_P0 = X_B + link_back_z(SERVO)    # 22.6: pinion back face (horn 2 mm deep in it) = racks' back
X_P1 = X_P0 + FACE_W           # 34.6
RAIL_IN = 9.5                  # rails / lip start 9.5 from the axis (trimmed horn stubs reach 5.65)
RAIL_X1 = X_P0 - CLR           # 22.35: rails' / lip's front face
GUIDE_T = 8.0                  # cover's lip wall behind rack A: 4 -> 8 (claw round 3, cover strength round 2: lip root
LIP_X0 = RAIL_X1 - GUIDE_T     # 14.35   SF 1.30 -> 5.20, lip above the tie post 6.52); its back face, and the ties' posts
RAIL_X0 = X_B                  # 10.0: the frame's rail behind rack B is a BLOCK back to the bulkhead's front face (claw
                               # round 3, frame strength round 2: the 4 mm wall's root gave SF 0.65; the block 6.19). It
                               # stays below the claw servo's case (z <= ZS - RAIL_IN = 17.75 against 21.15)
WINDOW_ROOF = 7.0              # 45° shoulders above the servo window: bridge 23.2 - 14 = 9.2 mm (DFM fix 1)

# --- cover ----------------------------------------------------------------------------
FRONT_T = 5.0                  # front plate 3 -> 5 (cover strength fix 1)
X_F0 = X_P1 + CLR              # 34.85: front plate inner face (= wrist plate front edge)
X_F1 = X_F0 + FRONT_T          # 39.85
FRONT_Z0 = -6.0                # front plate reaches 6 mm below the claw's back face: the strip under slot B is
                               # 11.75 deep (z -6..5.75); -4 -> -6 in claw round 3 (cover strength round 2: SF 2.58 -> 4.34)
TOP_T = 3.0
TOP_X0 = 0.0                   # top wall's rear edge: x 0 (DFM R2; carries the whole camera pad)
Z_TOP0 = ZS + RACK_OUT + RACK_SEAT   # 48.5: top wall underside (= bulkhead top)
Z_TOP1 = Z_TOP0 + TOP_T        # 51.5: top of the claw
TOP_CHAMFER = 1.5              # 45° on the top-front outer edge: the camera sees the fingertips over it
                               # (1.5 keeps a 1.5 mm front face on the top wall over slot A: no knife edge)
CORNER_FILLET = 2.0            # inner corner front plate / top wall (Kt 2.5 -> 1.5), from CORNER_FILLET_Y0 to +y
CORNER_FILLET_Y0 = 9.0         # beyond slot A's roof (which reaches z Z_TOP0 - 2 at y 8.5); rack A's 45° edge
                               # chamfer (rack y >= 4.5) faces it over the whole stroke
ACCESS_D = 2 * (R_P + M) + 0.6     # 22.6 printed: the pinion's pass-through in the front plate (SYS-01 fix A)
SLOT_A_END = 6.5               # slot A (open at -y) closes at y +6.5 with a 45° roof (it is a ceiling in print)
SLOT_B_END = 5.0               # slot B (open at +y) closes at y -5.0 with r 2 corners (a floor in print)
SLOT_FILLET = 2.0              # slot B's closed-end corner fillet (cover strength fix 2)
CRESCENT_Y = 7.0               # plate slivers between the pass-through and the slots are cut back to |y| 7
# Slot A (open at -y), the pass-through and slot B (open at +y) cut the front plate in two: the half below
# slot A (+ the strip under slot B) and the half under the top wall. A tie inside the claw joins them again:
# a web between the racks (|z - ZS| <= TIE_Z, clear of both racks' tips by 1.15) from the front plate back to
# a post behind the racks that meets the lip, over y -32..-24 (outside the pinion and every jaw path).
TIE_Y = (-HALF_Y, -HALF_Y + 8.0)
TIE_Z = 8.0
TIE_X0 = LIP_X0                # 14.35: post's rear face, in line with the lip's (clear of the claw servo: its case
                               # ends at y -16.9, its tabs at y -21.6, and the posts are at |y| >= 24)
# Second tie (claw round 3, cover strength round 2, change 2): the same post + web at y 24..32 joins the UPPER piece
# (the plate beside slot B's open end, which rack B pushes when a finger is forced towards closing) to the lip. It sits
# at the top of the print (the cover stands on its -y end), so its undersides are 45° slopes: the post grows from
# the lip (full depth from y TIE2_Y[0]), the web from the post and from the front plate beside the pass-through.
TIE2_Y = (HALF_Y - 8.0, HALF_Y)
# Anchor (claw round 4, cover strength round 3: the reversed rack-B push left the cover through the 3 mm top wall,
# SF 1.23): the second tie's post is 8 thick (x 14.35..22.35) and stands on the frame's rail block (z ZS - RAIL_IN
# = 17.75), held by ONE vertical M3 x 45 socket head through the top wall, lip and post into a 14 mm pilot in the block.
ANCHOR_XY = (RAIL_X1 - GUIDE_T / 2, HALF_Y - 4.0)   # (18.35, 28): mid-post; 2.65 to the block's front face and +y end
ANCHOR_PILOT_DEPTH = 14.0      # M3 x 45 + Ø7 x 0.5 washer: 33.75 + 0.5 over the block top, 10.75 engaged in the block
# V-seat (claw round 5, cover strength round 4: the anchor held the post's foot in x only by the preload's friction,
# against fdm-design-rules §4): a 90° V-groove along y in the rail block's top and a matching ridge under the post's foot
# hold the foot in x by geometry; the M3 x 45 holds the 45° flank's lift in tension, so no preload is relied on.
# Groove: x 14.45..16.05 at the block top (z 17.75), VSEAT_D deep (bottom z 16.95), y 23.5..32 (open at +y).
# Ridge: the same 90° V raised VSEAT_CLR (0.1 per flank, horizontal), so the foot's flats stand VSEAT_CLR over the block.
VSEAT_D = 0.8                  # groove depth / the ridge's virtual height (90° V: half-width = depth)
VSEAT_XC = LIP_X0 + 0.1 + VSEAT_D   # 15.25: groove / ridge centre line (ridge base 0.1 inside the post's back face)
VSEAT_Y0 = TIE2_Y[0] - 0.5     # 23.5: the groove's closed -y end (the ridge starts at y 24 with a 45° lead-in)
VSEAT_CLR = 0.1                # per flank, horizontal; also the foot's flats over the block top
ANCHOR_WASHER = (7.0, 0.5)     # ISO 7089 M3 washer under the M3 x 45's head (as on the MG996R tab screws)
# cover screws: two M3 down into the bulkhead top, two M2.5 back into the wrist plate's front edge
TOP_SCREWS = [(X_B - BULK_T / 2, -23.0), (X_B - BULK_T / 2, 14.0)]   # (x, y), clear of the servo window
FRONT_SCREWS = [(-24.0, T_W / 2), (24.0, T_W / 2)]                  # (y, z)
M3_PILOT = 2.5                 # printed pilot for M3 self-tapping (+ HOLE_COMP in the models)
M3_CLEAR = 3.4
M25_PILOT = 2.0                # front screws: M2.5 x 16 pan head self-tapping (head Ø5 x 1.5 stands 0.5 under
M25_CLEAR = 2.8                # jaw B's finger, which sweeps over it; an M3 head would hit it). Pilot skin 1.9
                               # (DFM fix 2's M2.5 alternative)

# --- jaws -----------------------------------------------------------------------------
NECK_Z = (RACK_ROOT, RACK_OUT)     # neck band above the axis (jaw A): 11.25..21.25, on the rack's solid back
NECK_Y = 20.0                  # neck length along y (jaw A: y -20..0)
NECK_FILLET = 4.0              # neck root fillets at its two y edges (Kt 2.5 -> 1.5)
NECK_X1 = X_F1 + 0.5           # 40.35: blades start 0.5 in front of the cover
BLADE_T = 6.0                  # finger thickness (y) at the tip
BLADE_T_ROOT = 12.0            # finger thickness from the neck to TAPER_X0 (jaw strength candidate C)
TAPER_X0, TAPER_X1 = NECK_X1 + 20.0, NECK_X1 + 35.0   # 12 -> 6 taper
GRIP_HALF = 10.0               # blades overlap on z = ZS ± 10 (20 mm tall grip faces)
X_TIP = 83.35                  # fingertip: kept where round 2 put it when FACE_W grew 2 mm (claw round 3), so the
BLADE_L = X_TIP - NECK_X1      # arm's reach, payload and the guard's tip stay as they were; the blade is 45 -> 43
GRIP_X0 = NECK_X1 + NECK_Z[0] + GRIP_HALF   # 61.6: full-height grip face starts
TOP_KINK_X = NECK_X1 + 15.0    # finger top: flat at the neck top to here, then 45° down to ZS + GRIP_HALF
KINK_FILLET = 3.0              # fillets at the finger's re-entrant kinks (Kt 2 -> 1.5)

# --- Brio 4K mount ----------------------------------------------------------------------
CAM_TILT = 34.0               # nose-down tilt: fingertips just above the image centre (v +0.05 at the 90° preset),
                               # the cover's chamfered front edge 0.6° below the ray to the bottom of the grip zone
CAM_XC = -8.5                  # camera thread (bottom-face centre) in G. The seat's front face (x 3.0) stays behind
CAM_ZC = Z_TOP1 + 16.9         # 68.4   the cover screws' button heads (x 3.9..9.6) with room for the hex key; the
                               # thumb screw's head sits ~8 mm behind the pad, reachable from below and behind
SEAT_T = 4.0
LIP_T, LIP_H, LIP_CLR = 5.0, 6.0, 0.3      # lip 3 -> 5 with an r 2 root fillet (camera-mount strength)
LIP_FILLET = 2.0
MOUNT_Y = (-28.0, 22.0)        # bracket width along y; it shares the cover's TOP_SCREWS
PAD_X = (0.0, 14.0)
PAD_TOP = Z_TOP1 + 3.5         # 55.0: button-head screws clear the camera's front face

# --- fasteners whose length follows from the geometry (S2: every horn clamp screw 4.6 mm into its spline) ---
HORN_FACE_ABOVE_SPLINE = 0.6   # hobby_parts.horn_face_z assumption
CLAMP_ENGAGE = 4.6             # target engagement of every horn clamp screw in its spline thread
PINION_CB_D = 6.2              # Ø6 M2 washer under the pinion clamp screw (pinion strength fix)
PINION_FLOOR = 6.3             # pinion: counterbore floor to the horn face; M2 x 12 - 0.5 washer - 6.3 - 0.6 = 4.6
WRIST_WASHER_OD = 8.0          # wrist clamp: Ø8 x 0.8 washer (DIN 9021 M2.5 size, hole 2.7) on the frame's pad, Ø6 -> 8
WRIST_WASHER_T = 0.8           # (claw round 3, frame strength round 2: bearing SF 2.12 -> 4.08); M2 x 12 - 0.8 - 6.3 - 0.6
                               # = 4.3 mm into the spline (thread depth >= 5.1, BUILD_GUIDE §2)

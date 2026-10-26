"""Shared geometry of the parallel claw (rack-and-pinion) and its Brio 4K camera mount.

Every claw model.py imports this file, so the parts always agree.

CLAW frame G (same as the old gripper-base frame, so the forearm and wrist do not change):
  origin = the wrist axis, on the claw frame's back face (the face on the wrist horn)
  +x     = towards the fingertips
  +z     = away from the wrist servo (outboard; world +Y when the arm is in its plane)
  y      = completes the frame, in the arm plane; the jaws close along y

Layout along x: wrist horn (x 0) | claw MG90S body behind the bulkhead | bulkhead (x 4..10)
| rails + lip (x 10..19.15) | pinion and both racks (x 19.4..27.4) | cover front plate
(x 27.65..30.65) | finger blades (x 31.15..76.15).
Layout along z (pinion axis at ZS): wrist plate (z 0..6) | rack B (lower, teeth up) |
pinion | rack A (upper, teeth down) | cover top wall (z 39..42) | camera mount.
Jaw A (upper rack) carries the finger on the -y side; jaw B is the SAME part turned 180°
about the pinion axis (x), carrying the finger on the +y side. Turning the pinion
positive about +x moves rack A to -y and rack B to +y: the claw opens.
"""
from __future__ import annotations

import math

from hobby_parts import MG90S, MG90S_DOUBLE, link_back_z

# --- servos and horns -------------------------------------------------------------------
SERVO = MG90S                  # claw servo; the wrist servo is an MG90S too (same size as the SG90)
WRIST_HORN = MG90S             # single-arm horn in the frame's back-face pocket
PINION_HORN = MG90S_DOUBLE     # double-arm horn, both arms CUT to HORN_TRIM_R, inside the pinion
HORN_TRIM_R = 5.5              # cut each horn arm 5.5 mm from the centre

# --- gearing ------------------------------------------------------------------------------
M = 1.0                        # module (tooth 1.57 mm thick on the pitch line: 4 extrusion widths)
Z_TEETH = 18                   # even: the pinion looks the same to both racks (symmetric jaws)
R_P = M * Z_TEETH / 2          # 9.0 pitch radius
FACE_W = 8.0                   # pinion and rack face width (along x)
BACKLASH = 0.1                 # each member gives up 0.1 (0.2 total at the nominal centre distance)
P_CIRC = math.pi * M           # rack pitch 3.14

# --- clearances ------------------------------------------------------------------------
CLR = 0.25                     # sliding clearance around the racks (x and z)
SLOT_CLR = 0.25                # around the necks in the cover slots

# --- racks (distances from the pinion axis) -------------------------------------------
RACK_BACK = 6.0                # solid behind the tooth roots (the neck and the bearing strip)
RACK_TIP = R_P - M             # 8.0
RACK_ROOT = R_P + 1.25 * M     # 10.25
RACK_OUT = RACK_ROOT + RACK_BACK   # 16.25: rack back face
RACK_Y = (-5 * math.pi * M, 9 * math.pi * M)   # jaw A's rack along y, CLOSED (-15.7..28.3): both ends
                               # in a tooth gap, no slivers (open: shifted by -STROKE)
STROKE = 22.0                  # per jaw: opening 0..44 mm
DEG_PER_MM_GAP = math.degrees(1.0 / (2.0 * R_P))   # 3.18° of servo per mm of jaw gap

# --- frame ----------------------------------------------------------------------------
T_W = 6.0                      # wrist plate (z 0..6); rack B slides on its top face
ZS = T_W + CLR + RACK_OUT      # 22.5: pinion / claw-servo axis height
X_B = 10.0                     # bulkhead front face = claw servo's tab underside
BULK_T = 6.0                   # bulkhead x 4..10 (the wrist clamp washer at x <= 3 stays clear)
X_REAR = -8.0                  # wrist plate rear edge
REAR_HALF = 10.0               # wrist plate half width behind the bulkhead
HALF_Y = 32.0                  # frame / cover half width
X_P0 = X_B + link_back_z(SERVO)    # 19.4: pinion back face (horn 2 mm deep in it) = racks' back
X_P1 = X_P0 + FACE_W           # 27.4
RAIL_IN = 9.5                  # rails / lip start 9.5 from the axis (horn stubs reach 5.85)
RAIL_X1 = X_P0 - CLR           # 19.15: rails' / lip's front face
WINDOW_ROOF = 5.0              # 45° shoulders above the servo window (bridge 12.9 instead of 22.9)

# --- cover ----------------------------------------------------------------------------
FRONT_T = 3.0
X_F0 = X_P1 + CLR              # 27.65: front plate inner face (= wrist plate front edge)
X_F1 = X_F0 + FRONT_T          # 30.65
TOP_T = 3.0
Z_TOP0 = ZS + RACK_OUT + CLR   # 39.0: top wall underside (= bulkhead top)
Z_TOP1 = Z_TOP0 + TOP_T        # 42.0: top of the claw
ACCESS_D = 5.0                 # hole in the front plate for the pinion's clamp screw
# cover screws (M3 self-tapping): two down into the bulkhead top, two back into the wrist plate
TOP_SCREWS = [(X_B - BULK_T / 2, -23.0), (X_B - BULK_T / 2, 14.0)]   # (x, y), clear of the servo window
FRONT_SCREWS = [(-24.0, T_W / 2), (24.0, T_W / 2)]                  # (y, z)
M3_PILOT = 2.5                 # printed pilot for M3 self-tapping (+ HOLE_COMP in the models)
M3_CLEAR = 3.4

# --- jaws -----------------------------------------------------------------------------
NECK_Z = (RACK_TIP, RACK_TIP + 5.0)   # neck band above the axis (jaw A): 8..13
NECK_Y = 14.0                  # neck length along y (jaw A: y -14..0)
NECK_X1 = X_F1 + 0.5           # 31.15: blades start 0.5 in front of the cover
BLADE_T = 6.0                  # finger thickness (y)
GRIP_HALF = 10.0               # blades overlap on z = ZS ± 10 (20 mm tall grip faces)
BLADE_L = 45.0
X_TIP = NECK_X1 + BLADE_L      # 76.15: fingertip
GRIP_X0 = NECK_X1 + NECK_Z[0] + GRIP_HALF   # 49.15: full-height grip face starts

# --- Brio 4K mount ----------------------------------------------------------------------
CAM_TILT = 30.0                # nose-down tilt: the jaws sit near the middle of the image
CAM_XC, CAM_ZC = -10.0, 52.5   # camera thread (bottom-face centre) in G
SEAT_T = 4.0
LIP_T, LIP_H, LIP_CLR = 3.0, 6.0, 0.3
MOUNT_Y = (-28.0, 22.0)        # bracket width along y; it shares the cover's TOP_SCREWS
PAD_X = (0.0, 14.0)
PAD_TOP = Z_TOP1 + 3.5         # 45.5: button-head screws clear the camera's front face

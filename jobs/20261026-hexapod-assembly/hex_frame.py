"""Shared frame and numbers for the hexapod. Every hexapod model.py imports this.

World frame: X forward, Y left, Z up, ground at Z = 0, origin under the body centre. Six identical
legs (rotated copies, not mirrored). Each leg has 3 MG90S servos: coxa (vertical axis, hung under the
bottom body plate, shaft down), femur and tibia (horizontal axes).

Round 3 (deep review 2026-10-26):
  - B2: the MG90S has its own spec (tools/hobby_parts.py): spline top 14.0 mm above the tab underside,
    so LB = link_back_z = 12.6 (was 9.4).
  - B1: no servo lead could pass its closed window. Each window now says how the lead gets through
    (*_MOUNT below): "reversed" = tabs on the plate's FAR face, upper case and spline through the window,
    so the lead root never crosses the plate (option 2, lead='none'); "normal" = tabs on the link-side
    face, case through the window, lead through a notch beside a pilot moved 1.3 mm outward
    (option 1, lead='notch_shift_pilot', the builder files that tab's slit to 2.1 mm).
  - Strength round 1: T_C 8 (6 mm floor under the coxa horn), T_V 10 (coxa vertical plate), T_BODY 6.

Leg frames (all right-handed; leg_frames() below builds them):
  S0 coxa servo frame: on the coxa axis at the coxa servo's tab underside, x = u (radial outward),
      z = world -Z (shaft down). With COXA_MOUNT "reversed" the tabs sit on the bottom plate's TOP face:
      S0 is S0_Z (= T_BODY + TAB_T) above the plate's underside.
  C  coxa bracket: origin on the coxa axis at the bracket's back face (top face of its horizontal plate),
      LB below S0, x = radial (turned by the coxa angle), z = world -Z (down), y = z × x.
      Horizontal plate z in [0, T_C]; vertical plate y in [Y_F - T_V, Y_F] carries the femur servo.
  S1 femur servo frame (in C): origin (L_C, Y_F, Z_F), x = C x, z = C y (shaft along +C y); tabs on the
      vertical plate's +y face (FEMUR_MOUNT "normal").
  F  femur: origin on the femur axis at the femur's back face (LB along S1 z), x along the femur.
  S2 tibia servo frame (in F): origin (L_F, 0, S2_Z), x = F x, z = F z. TIBIA_MOUNT "reversed": the tabs sit
      on the femur's BACK face (F z = 0), so the tab underside is at F z = -TAB_T.
  T  tibia: origin on the knee axis at the tibia's back face (LB along S2 z), x along the tibia to the foot.

Angles: leg_frames(coxa, femur, tibia) in degrees: coxa about world -Z (+ = clockwise seen from above),
femur + = up, tibia relative to the femur, -90 = perpendicular to it (straight down with the femur level).
The firmware's ("sketch") angles: femur the same, tibia_sketch = tibia + 90 (+ = foot outward).
"""
from __future__ import annotations

import math

import numpy as np
from hobby_parts import MG90S, link_back_z

SERVO = MG90S
LB = link_back_z(SERVO)          # 12.6: servo tab underside -> next link's back face (horn 2 mm deep). B2: was 9.4
TAB_T = SERVO.tab_t              # 2.5
GEAR_BOSS_TOP = 28.4 - SERVO.tab_height   # 9.9: TowerPro C 28.4 (case bottom -> top of the round gear boss) - F 18.5
GEAR_BOSS_D = 11.8               # gear boss round the output shaft (MCAD SG90 model; MG90S the same width class)

# --- B1: how each window passes its servo's lead (deep review 01) ------------------------------
COXA_MOUNT = "reversed"          # body-bottom: option 2 (tabs on the plate top; case inside the body)
FEMUR_MOUNT = "normal"           # coxa vertical plate: option 1 (T_V 10 leaves 0.1 mm to the femur if reversed)
TIBIA_MOUNT = "reversed"         # femur: option 2 (tabs on the femur's back face)

# --- leg ----------------------------------------------------------------------------------
L_C = 32.0        # coxa axis -> femur axis (radial)
L_F = 45.0        # femur axis -> knee axis
L_T = 70.0        # knee axis -> foot tip
T_C = 8.0         # coxa bracket horizontal plate (strength round 1: 6 mm floor under the 2 mm horn pocket; was 5)
T_V = 10.0        # coxa bracket vertical plate, grown towards -y (strength round 1; was 4.5)
T_F = 7.0         # femur plate
T_T = 7.0         # tibia plate
Y_F = -13.5       # femur servo tab plane (C y) = the vertical plate's +y face (strength: the tab face stays here)
Z_F = T_C + 12.0  # 20: femur axis below the bracket's back face (C z, downwards). Z_F grew by 4 mm in DFM round 1
                  # (room for a 45° root gusset under the femur servo's tabs) and by 3 mm with T_C 8 in round 3

S1_Y = Y_F if FEMUR_MOUNT == "normal" else Y_F - T_V - TAB_T     # femur servo tab underside (C y)
S2_Z = T_F if TIBIA_MOUNT == "normal" else -TAB_T                # tibia servo tab underside (F z): -2.5

# --- body -----------------------------------------------------------------------------------
# Middle legs at y ±56 (round 3, was ±52): with the coxa tabs on the plate top, the middle servos' inner tabs
# and nuts would otherwise sit where the UBEC goes, beside the LiPo (y 22-32).
LEG_MOUNTS = [(60.0, 42.0, 40.0), (0.0, 56.0, 90.0), (-60.0, 42.0, 140.0),        # left: x, y, angle deg
              (60.0, -42.0, -40.0), (0.0, -56.0, -90.0), (-60.0, -42.0, -140.0)]  # right
LEG_NAMES = ["LF", "LM", "LR", "RF", "RM", "RR"]
T_BODY = 6.0      # bottom plate (strength round 1; was 4)
COLUMN_H = 40.0   # bottom-plate top -> top-plate underside (DFM round 1: room for the ESP32 jumper leads over the LiPo)
COLUMNS = [(36.0, 25.0), (36.0, -25.0), (-36.0, 25.0), (-36.0, -25.0)]   # both plates. Round 3: x ±40 -> ±36, clear
                  # of the corner coxa servos' inner tabs and nuts, which now sit on the plate top
T_TOP = 3.0

S0_Z = T_BODY + TAB_T if COXA_MOUNT == "reversed" else 0.0   # 8.5: S0 (coxa tab underside) above the plate underside
PLATE_GAP = LB - S0_Z            # 4.1: bottom-plate underside -> coxa bracket's back face

# --- neutral stance (SYS-1, round 3) -----------------------------------------------------------
# Servo centre (fit the horns here): femur level, tibia perpendicular to it. The walking stance tucks the
# tibias in at the same body height; the angles are in the firmware's convention (femur + = up,
# tibia + = foot outward). Chosen in stance_torques.py (assembly_plan.md, "Stance").
NEUTRAL_FEMUR = -4.7
NEUTRAL_TIBIA = -14.0


def _T(x=0.0, y=0.0, z=0.0):
    m = np.eye(4); m[:3, 3] = (x, y, z); return m


def _Rz(deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    m = np.eye(4); m[:2, :2] = [[c, -s], [s, c]]; return m


def _frame(origin, x_dir, z_dir):
    x = np.asarray(x_dir, float); x /= np.linalg.norm(x)
    z = np.asarray(z_dir, float); z /= np.linalg.norm(z)
    y = np.cross(z, x)
    m = np.eye(4); m[:3, 0], m[:3, 1], m[:3, 2], m[:3, 3] = x, y, z, origin
    return m


def leg_frames(mx, my, a, coxa=0.0, femur=0.0, tibia=-90.0, z_pu=None):
    """World frames of one leg and its foot tip (on the tibia's mid-plane). z_pu = height of the bottom
    plate's underside (default: the neutral stance)."""
    z_pu = STANCE_Z_PU if z_pu is None else z_pu
    S0 = _frame((mx, my, z_pu + S0_Z), (math.cos(math.radians(a)), math.sin(math.radians(a)), 0), (0, 0, -1))
    C = S0 @ _T(0, 0, LB) @ _Rz(coxa)
    S1 = C @ _frame((L_C, S1_Y, Z_F), (1, 0, 0), (0, 1, 0))
    F = S1 @ _T(0, 0, LB) @ _Rz(femur)
    S2 = F @ _T(L_F, 0, S2_Z)
    Tt = S2 @ _T(0, 0, LB) @ _Rz(tibia)
    foot = Tt @ np.array([L_T, 0, T_T / 2, 1.0])
    return {"S0": S0, "C": C, "S1": S1, "F": F, "S2": S2, "T": Tt}, foot[:3]


def _foot_in_C(femur, tibia):
    fr, foot = leg_frames(0.0, 0.0, 0.0, 0.0, femur, tibia, z_pu=0.0)
    return (np.linalg.inv(fr["C"]) @ np.append(foot, 1.0))[:3]


def sketch_to_frames(femur_s, tibia_s):
    return femur_s, tibia_s - 90.0


def stance_z_pu(femur_s=NEUTRAL_FEMUR, tibia_s=NEUTRAL_TIBIA):
    """Plate-underside height that puts the feet on the ground in the given stance."""
    f, t = sketch_to_frames(femur_s, tibia_s)
    return PLATE_GAP + float(_foot_in_C(f, t)[2])      # foot depth below the bracket's back face + the plate gap


# Closed forms (kept as plain expressions so scripts that read this file's constants with `ast` get them too);
# checked against the frames below.
FOOT_SIDE = S1_Y + 2 * LB + S2_Z + T_T / 2         # 12.7: foot tip sideways from the coxa line (C +y), every pose
CENTRE_Z_PU = PLATE_GAP + Z_F + L_T                # 94.1: bottom-plate underside above the ground, servos centred
STANCE_Z_PU = (PLATE_GAP + Z_F - L_F * math.sin(math.radians(NEUTRAL_FEMUR))
               - L_T * math.sin(math.radians(NEUTRAL_FEMUR + NEUTRAL_TIBIA - 90.0)))   # 94.1 in the walking stance
STANCE_Z_TAB = STANCE_Z_PU + S0_Z                  # S0 (coxa tab underside) above the ground (name kept for old scripts)
assert abs(FOOT_SIDE - float(_foot_in_C(0.0, -90.0)[1])) < 1e-9
assert abs(CENTRE_Z_PU - stance_z_pu(0.0, 0.0)) < 1e-9 and abs(STANCE_Z_PU - stance_z_pu()) < 1e-9


def ik(i, target, z_pu=None):
    """Joint angles (coxa, femur, tibia in leg_frames' convention) that put leg i's foot tip on `target`
    (world xyz). Closed form on the frames above; checked against leg_frames in assembly_check.py."""
    z_pu = STANCE_Z_PU if z_pu is None else z_pu
    mx, my, a = LEG_MOUNTS[i]
    ar = math.radians(a)
    xa, ya = np.array([math.cos(ar), math.sin(ar)]), np.array([math.sin(ar), -math.cos(ar)])   # S0 x, S0 y
    p = np.asarray(target[:2], float) - (mx, my)
    u, v = float(p @ xa), float(p @ ya)
    r = math.sqrt(max(u * u + v * v - FOOT_SIDE ** 2, 1e-9))
    coxa = math.degrees(math.atan2(v, u) - math.atan2(FOOT_SIDE, r))
    zc = z_pu + S0_Z - LB                          # C origin height
    X, Y = r - L_C, -((zc - target[2]) - Z_F)      # foot from the femur axis: out, up
    k = (X * X + Y * Y - L_F ** 2 - L_T ** 2) / (2 * L_F * L_T)
    t = -math.acos(max(-1.0, min(1.0, k)))         # knee bends the foot down
    f = math.atan2(Y, X) - math.atan2(L_T * math.sin(t), L_F + L_T * math.cos(t))
    return coxa, math.degrees(f), math.degrees(t)


def neutral_feet(z_pu=None, femur_s=NEUTRAL_FEMUR, tibia_s=NEUTRAL_TIBIA):
    f, t = sketch_to_frames(femur_s, tibia_s)
    return [leg_frames(mx, my, a, 0.0, f, t, z_pu=z_pu)[1] for (mx, my, a) in LEG_MOUNTS]


# Tripod gait (round 3, matches the firmware): feet move in straight lines along X, stride 30-40 mm, sine lift
# 20 mm; each tripod swings for 40 % of the cycle, so all six feet are down for 10 % at each hand-over.
TRIPOD_A, TRIPOD_B = (0, 2, 4), (1, 3, 5)          # {LF, LR, RM}, {LM, RF, RR}
CYCLE_FRAMES, SWING_FRAMES = 20, 8


def foot_offset(tau, stride, lift=20.0):
    """Foot offset (dx along X, dz up) from neutral at frame tau of its tripod's cycle (tau 0 = lift-off)."""
    if tau <= SWING_FRAMES:
        p = tau / SWING_FRAMES
        return -stride / 2 + stride * p, lift * max(0.0, math.sin(p * math.pi))
    q = (tau - SWING_FRAMES) / (CYCLE_FRAMES - SWING_FRAMES)
    return stride / 2 - stride * q, 0.0


def gait_pose(frame, stride, lift=20.0, femur_s=NEUTRAL_FEMUR, tibia_s=NEUTRAL_TIBIA):
    """(angles per leg, feet, down flags) at gait frame `frame` (0 .. CYCLE_FRAMES-1), walking from the
    stance (femur_s, tibia_s) at its own body height."""
    z_pu = stance_z_pu(femur_s, tibia_s)
    feet0 = neutral_feet(z_pu, femur_s, tibia_s)
    angles, feet, down = [], [], []
    for i in range(6):
        tau = (frame + (0 if i in TRIPOD_A else CYCLE_FRAMES // 2)) % CYCLE_FRAMES
        dx, dz = foot_offset(tau, stride, lift)
        tgt = feet0[i] + (dx, 0.0, dz)
        angles.append(ik(i, tgt, z_pu))
        feet.append(tgt)
        down.append(dz == 0.0)
    return angles, feet, down

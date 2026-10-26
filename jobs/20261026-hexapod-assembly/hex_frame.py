"""Shared frame and numbers for the hexapod. Every hexapod model.py imports this.

World frame: X forward, Y left, Z up, ground at Z = 0, origin under the body centre.
Six identical legs (rotated copies). Each leg has 3 MG90S servos: coxa (vertical axis, hung
under the bottom body plate, shaft down), femur and tibia (horizontal axes).

Leg frames (all right-handed, built by `leg_frames` in assembly_check.py):
  coxa servo frame S0: origin at the mount point on the tab plane (= body-plate underside),
      x = u (radial outward), z = world -Z (shaft down)
  C (coxa bracket): origin on the coxa axis at the bracket's back face (top face of its
      horizontal plate), x = radial (turned by the coxa angle), z = world -Z (down), y = z × x
      Horizontal plate z in [0, T_C]; vertical plate (normal C +y) carries the femur servo.
  femur servo frame S1 (in C): origin (L_C, Y_F, Z_F), x = C x, z = C y  (shaft along +C y)
  F (femur): origin on the femur axis at the femur's back face, z = C y, x = along the femur
  tibia servo frame S2 (in F): origin (L_F, 0, T_F), x = F x, z = F z
  T (tibia): origin on the knee axis at the tibia's back face, x = along the tibia to the foot
"""
from hobby_parts import MG90S, link_back_z

SERVO = MG90S
LB = link_back_z(SERVO)          # 9.7: servo tab plane -> next link's back face (horn 2 mm deep)

# --- leg ----------------------------------------------------------------------------------
L_C = 32.0        # coxa axis -> femur axis (radial)
L_F = 45.0        # femur axis -> knee axis
L_T = 70.0        # knee axis -> foot tip
T_C = 5.0         # coxa bracket horizontal plate
T_V = 4.5         # coxa bracket vertical plate (femur servo tab face at its +y face)
T_F = 7.0         # femur plate
T_T = 7.0         # tibia plate
Y_F = -13.5       # femur servo tab plane (C y): puts the femur plate's mid-plane near the coxa line
Z_F = T_C + 8.0   # femur axis below the bracket's back face (C z, i.e. downwards): window clear of the plate

# --- body -----------------------------------------------------------------------------------
LEG_MOUNTS = [(60.0, 42.0, 40.0), (0.0, 52.0, 90.0), (-60.0, 42.0, 140.0),        # left: x, y, angle deg
              (60.0, -42.0, -40.0), (0.0, -52.0, -90.0), (-60.0, -42.0, -140.0)]  # right
T_BODY = 4.0      # bottom plate (coxa servos hang below it)
COLUMN_H = 30.0   # bottom-plate top -> top-plate underside
T_TOP = 3.0

# Neutral stance: femur horizontal, tibia vertical -> foot tip on the ground.
STANCE_Z_TAB = LB + Z_F + L_T    # 92.7: height of the body-plate underside (coxa tab plane)

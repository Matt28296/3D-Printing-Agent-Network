"""Shared frame and numbers for the tracked rover. Every rover model.py imports this
(sys.path gets this folder), so the chassis, sprockets, wheels and links agree.

World frame: X forward, Y left, Z up. Origin on the ground, midway between the two tracks,
under the drive-sprocket axis (rear). Left side shown; the right side mirrors in Y.
"""
import math

from hobby_parts import N20_100RPM

# --- track ------------------------------------------------------------------------------
P = 10.0                      # link pitch (pin to pin)
N_TEETH = 10                  # sprocket and idler
RP = P / (2 * math.sin(math.pi / N_TEETH))   # 16.18: pitch radius (pin axes on the wrap)
LINK_T = 6.0                  # link thickness; pins on its mid-plane
GROUSER = 1.5                 # tread bars below the outer face
TRACK_W = 24.0                # link width (Y)
N_LINKS = 34                  # per side
PIN_D = 1.75                  # 1.75 mm filament pins
AXLE_DX = (N_LINKS - N_TEETH) * P / 2      # 120: sprocket to idler, nominal
IDLER_SLOT = 4.0              # ± travel of the idler bolt for track tension

Z_A = RP + LINK_T / 2 + GROUSER            # 20.68: all axle heights (ground = grouser bottoms)
CHORD_IN = RP * math.cos(math.pi / N_TEETH) - LINK_T / 2   # 12.39: link inner face at mid-chord on a wrap
STRAIGHT_IN = RP - LINK_T / 2                             # 13.18: inner face to axle line on a straight run

# --- chassis ------------------------------------------------------------------------------
WALL = 3.0
FLOOR_T = 2.5
HALF_W_OUT = 38.0             # chassis outer half width (Y)
X_REAR_OUT, X_FRONT_OUT = -19.0, 135.0
FLOOR_Z = Z_A - 12.0          # 8.68: chassis underside (ground clearance)
TOP_Z = FLOOR_Z + 40.0        # 48.68: wall top = lid underside
Y_T = 55.0                    # track centre plane (left); inner edge at 43
ROAD_X = (40.0, 80.0)         # road-wheel axles
HUB_GAP = 0.5                 # rotating hub to wall / nut

MOTOR = N20_100RPM
MOTOR_FACE_Y = HALF_W_OUT - WALL      # 35: gearbox face against the wall's inner face


def mirror_y(y: float, side: int) -> float:
    return y * side

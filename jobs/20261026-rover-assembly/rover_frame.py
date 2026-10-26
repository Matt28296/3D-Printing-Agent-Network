"""Shared frame and numbers for the tracked rover. Every rover model.py imports this
(sys.path gets this folder), so the chassis, sprockets, wheels and links agree.

World frame: X forward, Y left, Z up. Origin on the ground, midway between the two tracks,
under the drive-sprocket axis (rear). Left side shown; the right side mirrors in Y.

Round 3 drivetrain (see 20261026-rover-sprocket/design_brief.md): each N20 is rolled 45° about
its shaft, so its 12 × 10 gearbox section becomes a diamond whose faces are all at 45°. It slides
from inside the tub along a V-trough into a diamond pocket that runs through the side wall, a
housing on the wall's outer face and a nacelle that reaches into the track's wrap (inside the
links, r <= 10.9 against the links' inner faces at r >= 12.39). Its face stops on a 2 mm skin at
the nacelle's end (round 4: strength round 3, change 2, SKIN 1.0 -> 2.0; the skin grows inward, so the
gearbox face moves from |y| 45 to 44 while the nacelle, thrust washer, hub and track plane stay put).
A Pololu #1996 aluminium hub on the shaft, outside the skin, carries the sprocket disc on 4 × M3.
The torque path is metal from the shaft to the sprocket, and the shaft overhang (gearbox face to
the track plane) is 11 mm with the track plane unchanged.
Round 5 (chassis strength round 4's fix, approved by the user): the idler's steel nut plate left the
wall for its outer face, with a Ø9 washer under the wall nut, so the idler's hub starts 5.2 mm further
out (IDLER_HUB_Y0, |y| 43.7); the track plane and the idler's teeth don't move.
"""
import math

from hobby_parts import N20_100RPM, POLOLU_HUB_1996

# --- track ------------------------------------------------------------------------------
P = 10.0                      # link pitch (pin to pin)
N_TEETH = 10                  # sprocket and idler
RP = P / (2 * math.sin(math.pi / N_TEETH))   # 16.18: pitch radius (pin axes on the wrap)
LINK_T = 6.0                  # link thickness; pins on its mid-plane
GROUSER = 1.5                 # tread bars below the outer face
TRACK_W = 24.0                # link width (Y)
N_LINKS = 34                  # per side
PIN_D = 2.0                   # 2 mm steel pins (strength round 1: filament pins bend when a wheel lands on a hinge)
AXLE_DX = (N_LINKS - N_TEETH) * P / 2      # 120: sprocket to idler, nominal
IDLER_SLOT = 4.0              # ± travel of the idler bolt for track tension

Z_A = RP + LINK_T / 2 + GROUSER            # 20.68: all axle heights (ground = grouser bottoms)
CHORD_IN = RP * math.cos(math.pi / N_TEETH) - LINK_T / 2   # 12.39: link inner face at mid-chord on a wrap
STRAIGHT_IN = RP - LINK_T / 2                             # 13.18: inner face to axle line on a straight run

# --- chassis ------------------------------------------------------------------------------
WALL = 4.5                    # strength round 1: 3 -> 4.5
FLOOR_T = 2.5
HALF_W_OUT = 38.0             # chassis outer half width (Y)
X_REAR_OUT, X_FRONT_OUT = -19.0, 135.0
FLOOR_Z = Z_A - 12.0          # 8.68: chassis underside (ground clearance)
TOP_Z = FLOOR_Z + 40.0        # 48.68: wall top = lid underside
Y_T = 55.0                    # track centre plane (left); inner edge at 43
ROAD_X = (40.0, 80.0)         # road-wheel axles
HUB_GAP = 0.5                 # rotating wheel hub to the wall, or idler hub to its wall nut (a washer)
BOSS_IN = 5.5                 # inward boss at the road-wheel bolts and the idler block: wall + boss = 10
                              # (strength round 2, change 3: nut / hole-edge bearing at the 5 cm corner)
HUB_D = 10.0                  # idler hub diameter (round bore on its M3 bolt)
DROP_MM = 50                  # design drop height onto a hard floor (spec §4)
LID_SCREWS = [(-13.0, 32.5), (-13.0, -32.5), (102.0, 32.5), (102.0, -32.5)]   # chassis columns = lid holes
#   (round 3: M3 heat-set inserts in Ø10 columns; |y| 32.5 keeps the idler jack screw's line at |y| 25.4 clear,
#    and the front pair at x 102 overlaps the idler block instead of touching it tangentially)

# --- drivetrain ------------------------------------------------------------------------------
MOTOR = N20_100RPM
MOTOR_ROLL = 45.0             # motor rolled about its shaft: gearbox x-axis at 45° in the XZ plane
HUB = POLOLU_HUB_1996         # aluminium hub on the N20 shaft: the sprocket disc bolts to it
DISC_HALF = 3.5               # sprocket/idler disc and teeth: Y_T ± 3.5 (the link notch is ± 4)
LINK_WALL_GAP = 1.0           # links to the chassis (>= 1 mm, Architect round 3)
SKIN = 2.0                    # printed skin in front of the gearbox face: the motor's outward stop
#                               (round 4, strength round 3 change 2: 1.0 -> 2.0 for the drop's diaphragm shear)
THRUST_WASHER_T = 0.5         # M3 washer (ISO 7089, 0.5 mm) on the shaft between the skin and the hub
HUB_Y1 = Y_T - DISC_HALF                                      # 51.5: hub outer face = sprocket disc's inner face
HUB_Y0 = HUB_Y1 - HUB.t                                       # 46.5: hub inner face
MOTOR_FACE_Y = HUB_Y0 - THRUST_WASHER_T - SKIN                # 44.0: gearbox face (skin inner face; skin 44-46)
SHAFT_ARM = Y_T - MOTOR_FACE_Y                                # 11.0: shaft overhang, gearbox face to track plane
HOUSING_OUT = Y_T - TRACK_W / 2 - LINK_WALL_GAP - HALF_W_OUT   # 4.0: housing on the wall's outer face (y 38-42),
#                                                               beside the links: 1 mm from their inner edge (43)
NACELLE_WALL = 2.0            # nacelle walls round the diamond pocket, beyond the housing (y 42-46, inside the wrap)

# --- axle and hub fasteners (all M3; axle bolts are socket head cap screws, class 12.9, FULLY threaded,
# because each one must engage the nut trapped in the wall's outer face) -------------------------------
SCREW_HEAD = (5.5, 3.0)       # DIN 912 / ISO 4762 M3 head: diameter, height
WASHER = (7.0, 0.5)           # ISO 7089 M3 washer: outside diameter, thickness
WASHER_WIDE = (9.0, 0.8)      # DIN 9021 M3 washer: under each idler-bolt head on its head plate and, since round 5,
#                               under each idler wall nut on its nut plate
NUT = (5.5, 2.4)              # DIN 934 M3 nut: across flats, height (road-wheel wall traps; the idler nuts sit outside the
#                               wall on their nut plates since round 5)
NYLOC = (5.5, 4.0)            # DIN 985 M3 nyloc nut
THREAD_PAST_NYLOC = 1.5       # minimum bolt thread standing out of each nyloc
ROAD_BOLT_L = 50.0            # road wheels: head on a washer on the boss face (y 27.5) .. tip y 77.5
IDLER_BOLT_L = 40.0           # idlers: head on a DIN 9021 washer on the head plate (y 27.2) .. tip y 67.2
HUB_SCREW_L = 12.0            # sprocket to hub: through the 7 mm disc under a washer, 4.5 mm into the hub

# --- idler clamp plates (round 4, strength round 3 change 1; round 5, chassis strength round 4's fix): made from 2 mm
# steel (14-gauge 1.9 mm, or metric 2 mm, flat bar or strip), so the yaw moment on each idler bolt bears on steel
# footprints instead of a Ø9 washer edge. Round 5: the nut plate left the wall (its 9 × 15 × 4.6 slot is gone), so the
# PETG between the plates is the full 8.0 mm from the head-plate recess (|y| 30) to the wall's outer face (|y| 38) ----
PLATE_T = 2.0                 # plate thickness = depth of the head-plate recess
IDLER_PLATE = (20.6, 10.0)    # head plate (x, z), let into the idler-block face under the DIN 9021 washer: strength's
#                               21 × 10 fills x 108-129 between the jack buttress and the front 45° strip, so it is cut
#                               0.4 short to drop into its recess (21.0 CAD between them, about 20.8 printed)
NUT_PLATE = (20.6, 10.0)      # nut plate (x, z), round 5: the head plate's twin (was 14 × 8 in the nut slot). It lies flat
#                               on the wall's outer face (|y| 38-40) at the head plate's x and z, on a printed lip between two
#                               printed end stops (chassis NUT_PLATE_X), under a DIN 9021 washer and the idler's wall nut
PLATE_SLOT = (3.4, 12.0)      # slot in both plates: width (z) × overall length (x); the bolt travels ±4.5 in it
PLATE_SLOT_FROM = 6.0         # the slot runs from 6 to 18 mm along each plate; the 6 mm end goes to the rear (jack side)
IDLER_HUB_Y0 = HALF_W_OUT + PLATE_T + WASHER_WIDE[1] + NUT[1] + HUB_GAP   # 43.7: idler hub's inner end (round 5; 38.5 before):
#                               nut plate 38-40, Ø9 washer 40-40.8, wall nut 40.8-43.2, running washer 43.2-43.7


def mirror_y(y: float, side: int) -> float:
    return y * side


def motor_diamond(half_x: float, half_y: float) -> list[tuple[float, float]]:
    """(x, z - Z_A) corners of a motor-frame rectangle (half sizes along the motor's x and y axes)
    rolled MOTOR_ROLL about the shaft: the same corners on both sides of the rover."""
    c, s = math.cos(math.radians(MOTOR_ROLL)), math.sin(math.radians(MOTOR_ROLL))
    return [(u * c + v * s, u * s - v * c) for (u, v) in ((half_x, half_y), (half_x, -half_y), (-half_x, -half_y),
                                                          (-half_x, half_y))]


def motor_x_dir(side: int):
    """World direction of the motor's x-axis (the gearbox's 12 mm side) for the motor frame used by the
    assembly check: z = (0, side, 0) out of the gearbox."""
    return (math.cos(math.radians(MOTOR_ROLL)), 0.0, math.sin(math.radians(MOTOR_ROLL)))

# Design brief: Rover chassis (tub)

Job: 20261026-rover-chassis · design-lead (round 3) · 2026-10-26

## Material
PETG for every rover part: tough against knocks, wears acceptably on steel pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Floor on the bed, walls vertical. Every hole in a wall is horizontal, so each is a teardrop or has a 45° roof; every inward boss runs down to the floor. The motor pocket is a diamond (the N20 is rolled 45°), so all four of its faces are at 45° and it needs no roof. The nacelle beyond the housing has 45° underside faces. The wall roots carry the wheel-bolt and drop moments across the layers: 4.5 mm walls, Ø26 bosses with r1.5 rims, BOSS_IN 5.5, 3 mm floor fillets and 1.5 × 45° join strips.

## Concept
Open-top tub, 154 × 76 × 40 mm, 4.5 mm walls (154 × 92 overall with the nacelles).
- **Drivetrain** (chosen and justified in 20261026-rover-sprocket/design_brief.md): no journal. Each N20 slides from inside the tub along an open V-trough into a diamond pocket through the wall, a housing on the wall's outer face and a nacelle inside the track's wrap. Its gearbox face stops on a 1 mm skin at |y| 45. A Pololu #1996 aluminium hub on the shaft outside the skin carries the sprocket, which puts the track plane 10 mm from the gearbox face.
  - The pocket sets the shaft's height and takes the reaction torque.
  - The trough (walls ≥ 4 mm standing on the floor; they are the round-3 "cheeks") steadies the can, and a zip tie through the tunnel under the can holds it down.
  - No rear stop: the motor is located by its face (outward by the skin; inward by the shaft hub and its thrust washer on the skin), so 9 and 11 mm gearboxes and 9 or 10 mm shafts all fit.
- **Road-wheel bolts and idler block:** Ø26 road-wheel bosses with r1.5 rims, and the 30 × 24 idler block, both with faces at |y| 28 (BOSS_IN 5.5).
- **Idler stop:** the idler bolt slides in a ±4 mm slot. An M3 × 20 set screw along +X, threaded into a buttress behind the idler block, bears on the bolt head. It holds the 29.8 N reverse-stall pull with no friction; the head clamp only keeps the bolt square.
- **Lid columns:** Ø10, with M3 heat-set inserts.
- **Battery and sensor:** battery holder on the floor (velcro through slots at |y| 26); HC-SR04 behind the front wall.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Sprocket-to-idler axle distance | 120.0 (slot ±4) | ±0.3 | track length 34 × 10 | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Axle height | Z 20.68 | ±0.3 | track meets the ground | — | rover_frame.Z_A |
| Gearbox pocket | 12.2 × 10.2 printed, rolled 45° | +0.15/−0 | gearbox slides in, 0.1 a side | GB_CLR 0.2 + HOLE_COMP 0.2 on each dimension | default |
| Gearbox face (skin inner face) | \|y\| 45.0 | ±0.2 | datum for hub and sprocket | — | rover_frame.MOTOR_FACE_Y |
| Skin | 1.0 thick; Ø4.5 printed boss hole | ±0.1 | clears the Ø4 × 0.8 bearing boss by 0.25 a side | HOLE_COMP | N20_100RPM boss_d, boss_h |
| Nacelle | r ≤ 10.91 (2.0 walls) | max | 1.5 inside the links (r ≥ 12.39); assert in model.py | — | rover_frame.NACELLE_WALL, CHORD_IN |
| Housing outer face | \|y\| 42.0 | ±0.2 | 1.0 from the links' inner edge | — | rover_frame.HOUSING_OUT, LINK_WALL_GAP |
| Bolt holes | Ø3.4 printed | +0.15/−0 | M3 clearance | HOLE_COMP | default |
| Nut traps | 5.8 AF × 2.6 deep | +0.2/−0 | M3 nut push fit | HOLE_COMP | default |
| Boss and idler-block faces | \|y\| 28.0 | ±0.2 | bolt-head stack | — | strength round 2, change 3 |
| Jack-screw pilot | Ø2.6 printed, axis (\|y\| 25.4, Z_A) | ±0.1 | M3 set screw taps its thread | HOLE_COMP | default |
| Insert holes | Ø4.0 × 6.5 | ±0.1 | M3 × 5.7 heat-set insert | none (maker's hole size) | fdm-design-rules §4 |

Printed targets for the whole rover: M3 bolt clearance Ø3.4; wheel and idler running bores Ø3.5 on M3 bolts (0.5 mm running clearance); sprocket M3 slots 3.4 wide and the Ø3.4 shaft-clearance hole; lid screw holes Ø3.4; M3 nut traps 5.8 across flats; track pin holes Ø2.3 in the centre knuckle (pin runs, 0.3 sliding fit) and Ø2.0 in the outer knuckles (pin gripped), teardrops. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row), except insert holes, which use the maker's size.

## Parameters exposed by model.py
HOLE_COMP, CORNER_R, BED_CHAMFER, BOLT_D, NUT_AF, NUT_CLR, NUT_DEPTH, ROAD_BOSS_R, BOSS_RIM_R, JOIN, IDLER_BLOCK, GB_CLR, POCKET_HX, POCKET_HY, HOUSING_HALF_X, HOUSING_TOP, BOSS_HOLE_D, CHEEK_T, CRADLE_HALF_X, TROUGH_TOP, CRADLE_Y0, TIE_W, TIE_Y, COLUMN_D, INSERT_D, INSERT_DEPTH, COLUMNS, JACK_Y, JACK_PILOT, JACK_X, JACK_Y_IN, BATT_X0, BATT_LEN, STRAP_W, STRAP_L, STRAP_Y, FLOOR_FILLET, SENSOR_Z, SENSOR_CLR (+ rover_frame.py: WALL, BOSS_IN, MOTOR_FACE_Y, SKIN, HOUSING_OUT, NACELLE_WALL, MOTOR_ROLL, LID_SCREWS, ...). `cad_checks.py` proves each critical dimension on the geometry.

## Round-3 changes (DFM and strength round 2, Architect's decisions, deep reviews 01 and 04)
- Idler slot hull up to the teardrop tips (Z_A + 2.55): one 8 mm bridge on both 45° flanks (DFM fix 1).
- Cradle "cheeks": the trough walls, ≥ 4 mm at their thinnest, standing on the floor. CRADLE_HALF_X is 12.1 rather than 10.3 because the rolled gearbox is 16.1 wide across its corners; that keeps the Architect's 4 mm cheek. No rear-stop posts: the motor is now located by its face, which also removes the 0.8 mm length window that an end cap or an 11 mm gearbox could not meet (deep review 04 S-07).
- ROAD_BOSS_R 13 with an r1.5 rim fillet, and BOSS_IN 5.5 at the road-wheel bosses and the idler block (strength changes 2 and 3).
- STRAP_Y 26.
- 1.5 × 45° strips where the bosses, idler block, trough and housing meet a wall (DFM fix 3).
- Axle bolts: class 12.9, fully threaded, M3 × 50 and M3 × 40, chosen so the thread stands ≥ 1.5 mm out of each nyloc. assembly_check.json: 2.0 and 4.2 mm, and the wall nut engaged.
- Idler positive stop: an M3 jack screw (DFM fix 4a, strength change 4), a Ø9 DIN 9021 washer under each idler-bolt head (DFM fix 4b), and the BUILD_GUIDE now tensions with the jack screw and calls the inside part the head.
- Lid columns Ø10 with heat-set inserts (DFM R1, deep review 04 S-09), moved to |y| 32.5 so the jack screw's line is clear. The front pair moved to x 102 so they overlap the idler block instead of touching its rear face tangentially.
- Toggle switch moved to the lid (deep review 04 S-06); HC-SR04 leads soldered to its bent pins (deep review 01 S13, 04 S-05).

## Risks
- **N20 shaft overload:** metal hub and a 10 mm overhang. Shaft SF 3.40 at stall and 2.13 at the 5 cm corner (sprocket brief).
- **Pocket printed tight on its 45° faces:** test-fit the motor before final assembly; scrape the faces lightly if needed.
- **Idler creeping back:** the jack screw holds it with no friction, and the pen mark in proof test 1 confirms it.
- **Self-tapped jack-screw thread:** adjusted a few times only; 6.5 mm of thread in the buttress.

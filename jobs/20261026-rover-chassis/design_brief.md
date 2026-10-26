# Design brief: Rover chassis (tub)

Job: 20261026-rover-chassis · design-lead (round 3; round 4: strength round 3's changes 1 and 2, approved by the user) · 2026-10-26

## Material
PETG for every rover part: tough against knocks, wears acceptably on steel pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Floor on the bed, walls vertical. Every hole in a wall is horizontal, so each is a teardrop or has a 45° roof; every inward boss runs down to the floor. The motor pocket is a diamond (the N20 is rolled 45°), so all four of its faces are at 45° and it needs no roof. The nacelle beyond the housing has 45° underside faces. The wall roots carry the wheel-bolt and drop moments across the layers: 4.5 mm walls, Ø26 bosses with r1.5 rims, BOSS_IN 5.5, 3 mm floor fillets and 1.5 × 45° join strips.

## Concept
Open-top tub, 154 × 76 × 40 mm, 4.5 mm walls (154 × 92 overall with the nacelles).
- **Drivetrain** (chosen and justified in 20261026-rover-sprocket/design_brief.md): no journal. Each N20 slides from inside the tub along an open V-trough into a diamond pocket through the wall, a housing on the wall's outer face and a nacelle inside the track's wrap. Its gearbox face stops on a 2 mm skin at |y| 44 (round 4; it was 1 mm at |y| 45). A Pololu #1996 aluminium hub on the shaft outside the skin carries the sprocket, which puts the track plane 11 mm from the gearbox face.
  - The pocket sets the shaft's height and takes the reaction torque.
  - The trough (walls ≥ 4 mm standing on the floor; they are the round-3 "cheeks") steadies the can, and a zip tie through the tunnel under the can holds it down.
  - No rear stop: the motor is located by its face (outward by the skin; inward by the shaft hub and its thrust washer on the skin), so 9 and 11 mm gearboxes and 9 or 10 mm shafts all fit.
- **Road-wheel bolts and idler block:** Ø26 road-wheel bosses with r1.5 rims, and the 30 × 24 idler block, both with faces at |y| 28 (BOSS_IN 5.5).
- **Idler stop:** the idler bolt slides in a ±4 mm slot. An M3 × 20 set screw along +X, threaded into a buttress behind the idler block, bears on the bolt head. It holds the 29.8 N reverse-stall pull with no friction.
- **Idler clamp (round 4):** the slot has no edges along X, so the bolt's yaw moment (29.6 R with the jack screw at the head) goes through the clamp faces. Both faces now bear on 2 mm steel plates: a 20.6 × 10 head plate let flush into a 2 mm recess in the block face, under the Ø9 washer, and a 14 × 8 nut plate on the bottom of a nut slot opened to 9 mm tall and 2 mm deeper, under the wall nut. The recess keeps the head, its washer, `JACK_Y` and the buttress where they were.
- **Lid columns:** Ø10, with M3 heat-set inserts.
- **Battery and sensor:** battery holder on the floor (velcro through slots at |y| 26); HC-SR04 behind the front wall.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Sprocket-to-idler axle distance | 120.0 (slot ±4) | ±0.3 | track length 34 × 10 | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Axle height | Z 20.68 | ±0.3 | track meets the ground | — | rover_frame.Z_A |
| Gearbox pocket | 12.2 × 10.2 printed, rolled 45° | +0.15/−0 | gearbox slides in, 0.1 a side | GB_CLR 0.2 + HOLE_COMP 0.2 on each dimension | default |
| Gearbox face (skin inner face) | \|y\| 44.0 | ±0.2 | the motor's datum (hub and sprocket sit on the skin's outer face, \|y\| 46) | — | rover_frame.MOTOR_FACE_Y |
| Skin | 2.0 thick (\|y\| 44–46); Ø4.5 printed boss hole | ±0.1 | clears the Ø4 × 0.8 bearing boss by 0.25 a side | HOLE_COMP | rover_frame.SKIN (strength round 3, change 2) |
| Nacelle | r ≤ 10.91 (2.0 walls) | max | 1.5 inside the links (r ≥ 12.39); assert in model.py | — | rover_frame.NACELLE_WALL, CHORD_IN |
| Housing outer face | \|y\| 42.0 | ±0.2 | 1.0 from the links' inner edge | — | rover_frame.HOUSING_OUT, LINK_WALL_GAP |
| Bolt holes | Ø3.4 printed | +0.15/−0 | M3 clearance | HOLE_COMP | default |
| Nut traps | 5.8 AF × 2.6 deep | +0.2/−0 | M3 nut push fit | HOLE_COMP | default |
| Boss and idler-block faces | \|y\| 28.0 | ±0.2 | bolt-head stack | — | strength round 2, change 3 |
| Jack-screw pilot | Ø2.6 printed, axis (\|y\| 25.4, Z_A) | ±0.1 | M3 set screw taps its thread | HOLE_COMP | default |
| Head-plate recess | 2.0 deep (\|y\| 28–30), x 108–129, Z_A ± 5.2, 45° roof to Z_A + 7.2 at the face | ±0.1 | 20.6 × 10 × 2 plate flush with the block face; 0.2 a side in Z, about 0.1 a side in X as printed | none in X (the recess fills the gap between the buttress and the strip; the plate is cut to fit), +0.2 a side in Z | rover_frame.PLATE_T, IDLER_PLATE (strength round 3, change 1a) |
| Idler nut slot | 9.0 tall (Z_A ± 4.5) × 4.6 deep (\|y\| 33.4–38) × 15.0 (x 112.5–127.5) | +0.2/−0 | 14 × 8 × 2 nut plate on the bottom, 0.5 below the flat roof; M3 nut on the plate | +0.5 a side on the plate (covers HOLE_COMP) | rover_frame.PLATE_T, NUT_PLATE (strength round 3, change 1b) |
| Insert holes | Ø4.0 × 6.5 | ±0.1 | M3 × 5.7 heat-set insert | none (maker's hole size) | fdm-design-rules §4 |

Printed targets for the whole rover: M3 bolt clearance Ø3.4; wheel and idler running bores Ø3.5 on M3 bolts (0.5 mm running clearance); sprocket M3 slots 3.4 wide and the Ø3.4 shaft-clearance hole; lid screw holes Ø3.4; M3 nut traps 5.8 across flats; track pin holes Ø2.3 in the centre knuckle (pin runs, 0.3 sliding fit) and Ø2.0 in the outer knuckles (pin gripped), teardrops. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row), except insert holes, which use the maker's size.

## Parameters exposed by model.py
HOLE_COMP, CORNER_R, BED_CHAMFER, BOLT_D, NUT_AF, NUT_CLR, NUT_DEPTH, ROAD_BOSS_R, BOSS_RIM_R, JOIN, IDLER_BLOCK, GB_CLR, POCKET_HX, POCKET_HY, HOUSING_HALF_X, HOUSING_TOP, BOSS_HOLE_D, CHEEK_T, CRADLE_HALF_X, TROUGH_TOP, CRADLE_Y0, TIE_W, TIE_Y, COLUMN_D, INSERT_D, INSERT_DEPTH, COLUMNS, JACK_Y, JACK_PILOT, JACK_X, JACK_Y_IN, PLATE_RECESS_X, PLATE_RECESS_Z, PLATE_RECESS_D, NUT_SLOT_H, NUT_SLOT_L, NUT_SLOT_D, BATT_X0, BATT_LEN, STRAP_W, STRAP_L, STRAP_Y, FLOOR_FILLET, SENSOR_Z, SENSOR_CLR (+ rover_frame.py: WALL, BOSS_IN, MOTOR_FACE_Y, SKIN, HOUSING_OUT, NACELLE_WALL, MOTOR_ROLL, LID_SCREWS, PLATE_T, IDLER_PLATE, NUT_PLATE, PLATE_SLOT, ...). `cad_checks.py` proves each critical dimension on the geometry.

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

## Round-4 changes (strength round 3, changes 1 and 2; nothing else changed)
- **Skin 1.0 → 2.0** (`rover_frame.SKIN`). The skin grows inward: the gearbox face moves from |y| 45 to 44, and the pocket's end, the trough's rear end (`CRADLE_Y0` 17.5 → 16.5) and the motor move with it. The nacelle (|y| 42–46, r ≤ 10.91), thrust washer (46–46.5), hub (46.5–51.5), sprocket and track plane don't move, so the sprocket, idler and wheel need no change: the assembly check finds the same 7 teeth engaged and 1.0 / 1.5 mm to the links. The shaft arm becomes 11.0 mm. Both shafts keep 5 mm in the hub; the shaft end now reaches |y| 54 (10 mm shaft) or 53 (9 mm), i.e. 2.5 or 1.5 mm into the sprocket's Ø3.4 centre hole instead of 3.5 or 2.5.
- **Head plate** (change 1a): 20.6 × 10 × 2 steel, slotted 3.4 × 12, flush in a 2 mm recess (`PLATE_RECESS_D` = `PLATE_T`) in each idler-block face, x 108–129. The recess runs exactly from the buttress's front face to the start of the front 45° strip, so it cuts neither, and that leaves no room for fitting clearance round a 21 mm plate: the plate is strength's 21 × 10 cut 0.4 short (I/x about 4 % lower than the 21 mm plate's). The DIN 9021 washer stays under the head, now on the plate, so the head (27.2), `JACK_Y` (25.4) and the buttress are unchanged. The recess's top is a 45° roof from its back up to the block face, so nothing over it needs bridging (a flat 21 mm ceiling would).
- **Nut plate** (change 1b): 14 × 8 × 2 steel, slotted 3.4 × 12, on the bottom of the idler nut slot, opened from 6.0 to 9 mm tall (Z_A ± 4.5) and 2 mm deeper (|y| 33.4–38), x 112.5–127.5. The nut sits on the plate where it sat before (|y| 35.4–37.8), so the bolt stack is unchanged (4.2 mm past the nyloc). The roof is flat over the plate (|y| 33.4–35.4, 0.5 above it) so its top edge bears there in a drop, then rises at 45° to the outer face: the only flat roof is a 15.0 × 2.0 strip anchored on three sides (mesh_check), and the idler-slot hull's bridge shrinks from 8.0 × 7.4 to 8.0 × 3.4.
- **The idler nut is no longer held by flats.** A slot tall enough for the 8 mm plate lets an M3 nut (6.35 mm across corners) turn. So the BUILD_GUIDE snugs each idler bolt at step 3, with the nut held, before the idler goes on, and the jack screw then slides the snug bolt (as the service section already did); nobody turns an idler head once the idler is on.
- **Web.** 3.4 mm of PETG (|y| 30–33.4) is left between the recess and the nut slot, clamped between the plates.
- Volume 131 834 → 130 848 mm³. cad_checks: 47 checks (probes for the 2 mm skin, the recess and its clearance to the buttress and strip, the nut slot and its roof, and the web).

## Risks
- **N20 shaft overload:** metal hub and an 11 mm overhang (round 4). Shaft SF 3.06 at stall and 1.91 at the 5 cm corner (strength round 3's FIX SKIN 2.0 rows), inside the Architect's limits of 2 and 1.5.
- **Sprocket centre hole (round 4):** the shaft end now sits 1 mm less deep in the sprocket's centre hole (2.5 mm with a 10 mm shaft, 1.5 mm with a 9 mm shaft). The sprocket's strength report sized its shaft-end rows H4 and H5 at 2.5 mm, which a 10 mm shaft still gives; with a 9 mm shaft its own formulas give about H4 3.5 and H5 2.2 (against 3). The sprocket job is unchanged: the Architect decides between a 10 mm shaft only and a re-check of H5.
- **Pocket printed tight on its 45° faces:** test-fit the motor before final assembly; scrape the faces lightly if needed.
- **Idler creeping back:** the jack screw holds it with no friction; proof tests 1 and 2 measure the idler disc (≤ 0.3 mm).
- **Idler nut turning with the bolt:** see round 4; hold the nut at step 3.
- **Hand-made plates:** cut from 2 mm steel (14-gauge 1.9 mm, or metric 2 mm). 1/8 in stock is 3.2 mm: it would stand 1.2 mm proud, put the jack screw on the washer and push the nut out of its slot.
- **Self-tapped jack-screw thread:** adjusted a few times only; 6.5 mm of thread in the buttress.

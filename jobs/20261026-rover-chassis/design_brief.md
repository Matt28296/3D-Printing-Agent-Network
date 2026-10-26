# Design brief: Rover chassis (tub)

Job: 20261026-rover-chassis · design-lead (round 3; round 4: strength round 3's changes 1 and 2; round 5: strength round 4's fix to the idler clamp; both approved by the user) · 2026-10-26

## Material
PETG for every rover part: tough against knocks, wears acceptably on steel pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Floor on the bed, walls vertical. Every hole in a wall is horizontal, so each is a teardrop or has a 45° roof; every inward boss runs down to the floor. The motor pocket is a diamond (the N20 is rolled 45°), so all four of its faces are at 45° and it needs no roof. The nacelle beyond the housing has 45° underside faces. The wall roots carry the wheel-bolt and drop moments across the layers: 4.5 mm walls, Ø26 bosses with r1.5 rims, BOSS_IN 5.5, 3 mm floor fillets and 1.5 × 45° join strips.

## Concept
Open-top tub, 154 × 76 × 40 mm, 4.5 mm walls (154 × 92 overall with the nacelles).
- **Drivetrain** (chosen and justified in 20261026-rover-sprocket/design_brief.md): no journal. Each N20 slides from inside the tub along an open V-trough into a diamond pocket through the wall, a housing on the wall's outer face and a nacelle inside the track's wrap. Its gearbox face stops on a 2 mm skin at |y| 44 (round 4; it was 1 mm at |y| 45). A Pololu #1996 aluminium hub on the shaft outside the skin carries the sprocket, which puts the track plane 11 mm from the gearbox face.
  - The pocket sets the shaft's height and takes the reaction torque.
  - The trough (walls ≥ 4 mm standing on the floor; they are the round-3 "cheeks") steadies the can, and a zip tie through the tunnel under the can holds it down.
  - No rear stop: the motor is located by its face (outward by the skin; inward by the shaft hub and its thrust washer on the skin), so 9 and 11 mm gearboxes both fit. The shaft must be 10 mm from the gearbox face (at least 9.6 mm: a 9 mm shaft is too short for the sprocket's centre hole, sprocket strength round 4).
- **Road-wheel bolts and idler block:** Ø26 road-wheel bosses with r1.5 rims, and the 30 × 24 idler block, both with faces at |y| 28 (BOSS_IN 5.5).
- **Idler stop:** the idler bolt slides in a ±4 mm slot. An M3 × 20 set screw along +X, threaded into a buttress behind the idler block, bears on the bolt head. It holds the 29.8 N reverse-stall pull with no friction.
- **Idler clamp (rounds 4 and 5):** the slot has no edges along X, so the bolt's yaw moment (29.6 R with the jack screw at the head) and its tilt in a drop go through the clamp faces. Both faces bear on identical 20.6 × 10 × 2 steel plates:
  - the head plate is let flush into a 2 mm recess in the block face (round 4), under the Ø9 head washer, which keeps the head, `JACK_Y` and the buttress where they were;
  - the nut plate (round 5) lies flat on the wall's outer face at the same x and height, on a printed lip between two printed end stops, under a second Ø9 washer and the wall nut.
  - Nothing is cut into the wall behind either plate, so the PETG between them is the full 8.0 mm (|y| 30–38) round the bolt slot.
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
| Nut-plate seat on the outer face (round 5) | end stops' inner faces x 108 and 129 (21.0 CAD, about 20.8 printed); lip top Z_A − 5.2 (print z 6.8, a layer line); lip and stops 1.0 proud (\|y\| 38–39); lip 1.0 face + 45° underside; stops up to Z_A + 5.2 | ±0.1 | 20.6 × 10 × 2 nut plate flat on the wall (\|y\| 38–40) between the stops, on the lip: 0.2 a side in X as printed, like the head plate in its recess | none in X (same gap as the recess; the plate is cut to fit), none in Z (it rests on the lip) | rover_frame.NUT_PLATE, PLATE_T; strength round 4 FIX (plate at x 108.2–128.8, lip under its bottom edge, no recess) |
| PETG between the plates (round 5) | 8.0 (\|y\| 30–38), only the bolt slot through it | min | no nut slot | — | strength round 4 FIX |
| Insert holes | Ø4.0 × 6.5 | ±0.1 | M3 × 5.7 heat-set insert | none (maker's hole size) | fdm-design-rules §4 |

Printed targets for the whole rover: M3 bolt clearance Ø3.4; wheel and idler running bores Ø3.5 on M3 bolts (0.5 mm running clearance); sprocket M3 slots 3.4 wide and the Ø3.4 shaft-clearance hole; lid screw holes Ø3.4; M3 nut traps 5.8 across flats; track pin holes Ø2.3 in the centre knuckle (pin runs, 0.3 sliding fit) and Ø2.0 in the outer knuckles (pin gripped), teardrops. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row), except insert holes, which use the maker's size.

## Parameters exposed by model.py
HOLE_COMP, CORNER_R, BED_CHAMFER, BOLT_D, NUT_AF, NUT_CLR, NUT_DEPTH, ROAD_BOSS_R, BOSS_RIM_R, JOIN, IDLER_BLOCK, GB_CLR, POCKET_HX, POCKET_HY, HOUSING_HALF_X, HOUSING_TOP, BOSS_HOLE_D, CHEEK_T, CRADLE_HALF_X, TROUGH_TOP, CRADLE_Y0, TIE_W, TIE_Y, COLUMN_D, INSERT_D, INSERT_DEPTH, COLUMNS, JACK_Y, JACK_PILOT, JACK_X, JACK_Y_IN, PLATE_RECESS_X, PLATE_RECESS_Z, PLATE_RECESS_D, NUT_PLATE_X, LIP_DZ, LIP_OUT, LIP_FACE, STOP_W, BATT_X0, BATT_LEN, STRAP_W, STRAP_L, STRAP_Y, FLOOR_FILLET, SENSOR_Z, SENSOR_CLR (+ rover_frame.py: WALL, BOSS_IN, MOTOR_FACE_Y, SKIN, HOUSING_OUT, NACELLE_WALL, MOTOR_ROLL, LID_SCREWS, PLATE_T, IDLER_PLATE, NUT_PLATE, PLATE_SLOT, PLATE_SLOT_FROM, IDLER_HUB_Y0, ...). `cad_checks.py` proves each critical dimension on the geometry (50 checks).

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
- (The nut slot, the 14 × 8 nut plate and the web are superseded by round 5.)

## Round-5 changes (strength round 4's fix, approved by the user; nothing else changed)
**Why.** Round 4 passed DFM but failed strength at SF 0.61. The 9 × 15 × 4.6 nut slot left a 3.4 mm PETG web between the head-plate recess and the slot, and the nut plate sat wholly inside the slot. So its share of the yaw and tilt couples landed on the web, whose strips bend across the layers from the slot's sharp corners. This is the chassis's fourth DESIGN failure; the user approved this fifth round with the reviewer's fix, and a further failure goes back to the user.

**What changed:**
- **Nut slot deleted** (`_idler_nut_slot`, `NUT_SLOT_H/L/D`). The bolt slot (teardrop ends and hull) still runs through the block and the wall. The PETG between the head plate (|y| 30) and the outer face (|y| 38) is now 8.0 mm, with nothing behind either plate.
- **Nut plate = the head plate's twin** (`rover_frame.NUT_PLATE` (14, 8) → (20.6, 10); slot 3.4 × 12 from 6 to 18 mm along, `PLATE_SLOT_FROM`, 6 mm end to the rear). It lies flat on the wall's outer face (|y| 38–40) at the head plate's x 108.2–128.8 and height.
- **Seat on the outer face** (`_nut_plate_seat`). The reviewer asked for a lip, not a recess: a 0.5 mm locating recess would thin the PETG (2.94).
  - A lip under the plate's bottom edge: top face at Z_A − 5.2 (`LIP_DZ` = `PLATE_RECESS_Z`), 1.0 proud (`LIP_OUT`), a 1.0 vertical face, then a 45° underside back into the wall (no support).
  - The reviewer said Z_A − 5.1. I used − 5.2 for two reasons. It is level with the head-plate recess floor, so both plates rest at the same height and their slots line up on the bolt (both clear it by 0.2 below and 0.3 above). It also falls on a layer line (print z 6.8) instead of mid-layer.
  - **End stops**, my addition (`STOP_W` 1.5, inner faces at `NUT_PLATE_X` = x 108 and 129, up to Z_A + 5.2). A lip alone locates the plate only in Z. In X it would be held only by friction, which the clamp check (S2) may not count on, and by the bolt in its slot, which lets it wander up to about 8.6 mm forward (past the corner fillet that starts at x 129). The strength FIX assumes the plate at x 108.2–128.8. The stops are the recess's ends on the outside: the same 21.0 CAD gap, the same 0.2 printed fit. They are beyond the plate's ends, so they add no notch to the strips the FIX rows check.
  - The lip and stops are 1.0 proud, under half the plate's thickness. The Ø9 washer (|y| 40–40.8) clears them, and they stay 4.0 mm inboard of the links (|y| 43). They join the wall 1 mm inside its face, so the front stop also merges with the r6 corner fillet that starts at x 129.
- **Ø9 × 0.8 DIN 9021 washer under each idler wall nut**, as under the head. Strength: it cuts the drop's prying tension from 157 to 139 N and spreads the nut's push; without it the drop shear row is 2.49.
- **Idler hub 5.2 mm shorter** (idler job): it now starts at |y| 43.7 = 38 + 2.0 plate + 0.8 washer + 2.4 nut + 0.5 running washer (`rover_frame.IDLER_HUB_Y0`). The M3 × 40, the nyloc (4.2 mm of thread past it), the jack screw, the head plate and the head stack (27.2, `JACK_Y` 25.4) don't change.

**Travel, fit and access** (assembly_check.json, round 5):
- **Travel.** Both plates' slots cover the PETG slot's ±4 travel with either plate anywhere in its 0.4 mm of play: bolt centre x 115.9–124.5 against 116–124 needed. Both Ø9 washers stay on their plates: 0.3 mm to spare at the front end, 0.1 with a plate pushed to the rear of its play.
- **Jack screw.** It still bears on 2.7 mm of the head and clears the head washer by 0.3.
- **Assembly.** 160 bodies, 0 collisions; the idler and jack screw are clear at both slot ends; 7 teeth in mesh on every sprocket and idler; links 1.0 / 1.5 mm from the housing / nacelle.
- **Holding the nut.** It is outside now, so a 5.5 mm spanner holds it at step 3 (nothing else is fitted on the outside then).

**Snug and oil (strength S1/S2).** Each idler bolt is snugged to at most 0.04 N·m on oiled plates: the 2.5 mm key's long arm in the head, its short arm twisted with two fingertips. That gives 46 N of jack thrust, so the self-tapped jack thread is at SF 3.15; dry, the same snug gives 1.60. The clamp is checked with no clamp force left, so nothing relies on friction. The BUILD_GUIDE (§1, §3 steps 3, 7 and 8, Service) carries the figure, the oil, the spanner, holding the head while the nyloc turns, tensioning with the jack screw only, and the witness mark on the head washer and head plate.

**Predicted** (strength round 4's FIX rows, for this geometry):
- reverse stall 6.45 (head plate on PETG);
- everyday reverse 11.7; sustained 19.2;
- 5 cm front corner **3.02** (strip root at the recess-floor edge, Kt 2.5) and 3.05 (shear along the layer);
- steel plates 3.50 against 1.5;
- proofs 6.95 / 5.12 / 1.96 against 1.0.

**Printability.** The bolt-slot hull ceiling is again 8.0 × 8.0 at print z 14.55 (round 3 had 8.0 × 7.4); the nut-slot roof strip is gone. The lip's underside is 45° and the stops are vertical. Overhang 0.53 % (327.9 mm²), no thin walls. Volume 130 848 → 131 908 mm³. cad_checks: 50 checks (the nut-slot and web probes replaced by the 8.0 mm PETG, the lip, the stops, the plate's clear space and the twin plates).

## Risks
- **N20 shaft overload:** metal hub and an 11 mm overhang (round 4). Shaft SF 3.06 at stall and 1.91 at the 5 cm corner (strength round 3's FIX SKIN 2.0 rows), inside the Architect's limits of 2 and 1.5.
- **Sprocket centre hole (resolved):** the Architect specified a 10 mm shaft only (at least 9.6 mm from the gearbox face). The assembly check now runs the 9.6 mm minimum: 2.1 mm into the centre hole (sprocket H4 4.95, H5 3.13).
- **Pocket printed tight on its 45° faces:** test-fit the motor before final assembly; scrape the faces lightly if needed.
- **Idler creeping back:** the jack screw holds it with no friction; proof tests 1 and 2 measure the idler disc (≤ 0.3 mm).
- **Thin drop margin at the head plate (round 5):** the FIX's lowest row is 3.02, the strip root at the head-plate recess floor's sharp edge in the 5 cm corner drop (2.77 for the drop shear with rigid roots, advisory). The reviewer offered a cheap extra margin: a 1 × 45° chamfer on that floor edge, with the plate's bottom-back edge filed to match (about 4.7, Kt 1.6). It is **not** taken in this round, because the user's instruction was to keep the recess as it passed. If the round-5 review asks for it, it is a one-line cut.
- **Idler snug lost or too tight:** too tight (a normal 0.3 N·m snug) strips the jack screw's thread at the first tensioning; turned by the nyloc, the snug is lost. The guide gives 0.04 N·m (about 230 g at the tip of the key's short arm, felt on the kitchen scale first), oiled plates, the nut held with a spanner at step 3, and the head held with the key at step 7.
- **Nut plate fitted backwards:** its slot is off-centre (6 mm and 2.6 mm ends), so a plate fitted 6 mm end forward loses 3 mm of tensioning travel. The guide has the 6 mm end marked with a pen and fitted to the rear.
- **Hand-made plates:** four identical plates, cut from 2 mm steel (14-gauge 1.9 mm, or metric 2 mm). 1/8 in stock is 3.2 mm: a head plate would stand 1.2 mm proud and put the jack screw on the washer. The closed slots are chain-drilled and filed (BUILD_GUIDE §1).
- **Self-tapped jack-screw thread:** adjusted a few times only; 6.5 mm of thread in the buttress.

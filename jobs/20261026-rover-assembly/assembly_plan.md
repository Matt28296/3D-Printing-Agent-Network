# Assembly plan: tracked rover (ESP32, 2 × N20, printed tracks)

Robot 2 of 3 (after the desktop arm, before the hexapod). Architect: Claude, 2026-10-26; rounds 3, 4 and 5 the same day (round 4: strength round 3's fixes to the chassis and lid; round 5: chassis strength round 4's fix to the idler clamp, which shortens the idler's hub; both approved by the user).
The user chose the ESP32 and left motors, power and material to the designer. System spec and acceptance tests: [spec.md](spec.md).

## Decisions

| Item | Choice | Why |
|---|---|---|
| Layout | Skid-steer tank: one drive sprocket per side at the rear, a toothed idler at the front, two road wheels per side | Simple, turns on the spot, every part prints flat or axis-vertical |
| Drive | 2 × N20 gear motors, 6 V 100 rpm (150:1, LP or MP, 9 mm gearbox, 3 mm D-shaft 10 mm, at least 9.6 mm from the gearbox face), each rolled 45°. The diamond gearbox slides along a V-trough into a pocket through the wall, a housing and a nacelle inside the track's wrap. The face stops on a 2 mm skin (round 4; 1 mm before). A Pololu #1996 aluminium hub on the shaft carries the sprocket disc on 4 × M3 (concept C, sprocket design_brief.md) | Metal torque path. The shaft overhang is 11 mm, so the shaft SF is 3.06 at stall and 1.91 at a 5 cm corner drop (chassis strength round 3). No journal friction. The motor is located by its face, so 9 and 11 mm gearboxes fit; the shaft must be 10 mm (at least 9.6 mm) from the gearbox face, because a 9 mm shaft reaches only 1.5 mm into the sprocket's centre hole (see Status) |
| Driver | TB6612FNG carrier on a 170-point mini breadboard on the lid | 1.2 A per channel (N20 stall 0.36–0.7 A for the pinned class); 3.3 V logic matches the ESP32 |
| Controller | ESP32 DevKit (38- or 30-pin), pins down, in a seat on the lid | User's choice; female jumpers reach every pin through the window |
| Power | 2 × 18650 in series (7.4 V) on the floor under a velcro strap: protected ≈70 mm cells in a holder up to 80 mm long, or unprotected cells + a 2S BMS. MTS-102 toggle on the lid, lever up. MP1584 buck at 5.0 V under the lid. Cells charged outside the rover in a two-bay charger | Estimated 5–11 h (deep review 04 S-14). Motors are rated 6 V, so the test sketch limits PWM |
| Sensor | HC-SR04 behind the front wall, transducers through two holes, pins bent back with the leads soldered on | Obstacle distance for a first autonomous program; no room for a Dupont housing below the board |
| Tracks | 34 printed links per side, 10 mm pitch, on Ø2 × 24 steel dowel pins. The outer knuckles grip each pin and it runs in the centre knuckle with 0.3 mm clearance. 10-tooth sprocket and idler (pitch radius 16.18); road wheels with 45° V-flanges | Steel pins survive a wheel landing on a hinge (strength round 1) |
| Tension | Idler bolt in a ±4 mm slot. An M3 × 20 jack screw in a buttress behind the idler block bears on the bolt head: a positive stop with no friction. The bolt is snug between two identical 20.6 × 10 × 2 steel plates (round 5): a head plate flush in a recess in the block face, under a Ø9 DIN 9021 washer, and a nut plate flat on the wall's outer face, on a printed lip between two printed end stops, under a second Ø9 washer and the wall nut. No nut slot: 8 mm of solid PETG between the plates | Holds the 29.8 N reverse-stall pull; the plates carry the bolt's yaw and tilt couples on steel footprints into 8 mm of PETG (chassis strength round 4's fix: lowest predicted SF 3.02; round 4's nut slot left a 3.4 mm web at SF 0.61). The bolt is snugged to 0.04 N·m on oiled plates before the idler goes on, and only the jack screw moves it after that (46 N of thrust, thread SF 3.15). Re-tension with the lid off, the sensor stays |
| Axles | M3 socket-head screws, class 12.9, fully threaded: × 50 for road wheels, × 40 for idlers. Road wheel: head inside on a washer, nut trapped in the wall, washer, wheel, washer, DIN 985 nyloc. Idler (round 5): head on a Ø9 washer on the head plate, wall, nut plate, Ø9 washer, wall nut outside, washer, idler (hub from \|y\| 43.7), washer, nyloc | Fully threaded, so the wall nut engages; ≥ 1.5 mm of thread past each nyloc (2.0 / 4.2) |
| Lid fixing | 4 × M3 heat-set inserts in Ø10 columns, M3 × 8 screws | The lid comes off for every charge |
| Material | PETG throughout | Tough, wears acceptably at the pins |
| Mass | ≈ 0.65 kg (649 g, strength round 2) | |

## Shared frame (`rover_frame.py`; every model.py imports it)

X forward, Y left, Z up; ground at Z = 0 (grouser bottoms on the straight run); drive-sprocket axis at X = 0.

| Item | Value |
|---|---|
| Axle height (all wheels) | Z 20.68 = pitch radius 16.18 + half link 3 + grouser 1.5 |
| Sprocket → idler | 120 mm nominal (idler slot ±4) = (34 − 10) links × 10 / 2 |
| Road wheels | X 40 and 80 |
| Track centre planes | Y ±55; links 24 wide, inner edge 43 |
| Chassis | X −19 … 135, Y ±38 (±46 at the nacelles), Z 8.68 … 48.68 (ground clearance 8.7) |
| N20 (rolled 45°) | gearbox face \|y\| 44.0 on the 2 mm skin (44–46); thrust washer 46.0–46.5; hub 46.5–51.5; sprocket disc 51.5–58.5; shaft end 54 (10 mm shaft; at least 53.6 for the 9.6 mm minimum): 5 mm in the hub, 2.5 (at least 2.1) mm in the disc's centre hole |
| Housing / nacelle | housing \|y\| 38–42, 1.0 mm from the links; nacelle \|y\| 42–46, r ≤ 10.91 (links' inner faces r ≥ 12.39 on the wrap) |
| Axle-bolt heads | road wheels \|y\| 27.5 on an ISO 7089 washer; idlers \|y\| 27.2 on a DIN 9021 washer on the head plate |
| Idler clamp plates (round 5) | Two identical 20.6 × 10 × 2 steel plates per idler (`IDLER_PLATE` = `NUT_PLATE`, `PLATE_T`), slotted 3.4 × 12 from 6 to 18 mm along, 6 mm end to the rear, both at x 108.2–128.8 resting at Z_A − 5.2 … + 4.8. Head plate \|y\| 28–30 in a recess x 108–129 (buttress face to front strip). Nut plate \|y\| 38–40 on the wall's outer face, on a lip (top Z_A − 5.2, 1 mm proud, 45° underside) between end stops at x 108 and 129. 8.0 mm of PETG between them (\|y\| 30–38). With either plate anywhere in its 0.4 mm of play, the bolt can travel x 115.9–124.5 (the slot needs 116–124) |
| Idler stack outside the wall (round 5) | nut plate 38–40, Ø9 washer 40–40.8, wall nut 40.8–43.2, washer 43.2–43.7, idler hub 43.7–51.5 (`IDLER_HUB_Y0`; 5.2 mm shorter), disc 51.5–58.5, washer, nyloc 59.0–63.0, bolt tip 67.2 |
| Jack screws | along X at (\|y\| 25.4, Z 20.68), threaded in buttresses x 101.5–108 |
| Lid | Z 48.68 … 51.68; screws at (−13, ±32.5), (102, ±32.5); toggle at (0, −23) |
| Overall | 159.8 × 155.0 × 72.7 (assembly_check.json) |

## Printed pieces

| # | Job | Piece | Qty | Orientation |
|---|---|---|---|---|
| 1 | 20261026-rover-chassis | Tub with motor troughs, pockets, housings and nacelles; wheel bosses; idler slots and jack-screw buttresses; insert columns; strap slots; sensor holes | 1 | floor down |
| 2 | 20261026-rover-lid | Deck with ESP32 seat, breadboard area, toggle hole, cable slots and tie bar | 1 | flat |
| 3 | 20261026-rover-sprocket | 10-tooth disc bolted to the hub through 4 radial slots | 2 | outer face down |
| 4 | 20261026-rover-idler | Toothed idler, Ø10 hub (7.8 long since round 5), round Ø3.5 bore, 14.8 tall | 2 | outer face down, hub up |
| 5 | 20261026-rover-wheel | Road wheel, V-flanges, 0.4 mm bed chamfer | 4 | outer flange down |
| 6 | 20261026-rover-track-link | Track link | 68 + 2 spare (2 plates) | inner face down |

## Assembly check (`assembly_check.py` → `assembly_check.json`, `assembly_rover.png`)

Both 34-link loops are placed pin by pin (13 on the bottom run, 5 round the idler, 12 on the top run, 4 round the sprocket), with every printed part and these bought parts:
- **Drivetrain:** the detailed N20 (end cap, tabs, Ø4 × 0.8 bearing boss, D-shaft), rolled 45°; hubs, thrust washers, hub screws and their washers.
- **Axles:** axle bolts at their real lengths, head washers, wall nuts, running washers and nylocs; the jack screws; the idler head and nut plates resting on their recess floor and lip (round 5), fixed while the idler hardware (with the Ø9 washer under each idler wall nut) moves to both slot ends.
- **Electronics and power:** the 80 mm battery holder and its strap; the HC-SR04 with bent pins and soldered leads; the ESP32 with jumper housings; the breadboard, TB6612 and buck; the toggle with its nuts and lever.
- **Lid fixing:** inserts and lid screws.

Results:
- **Collisions.** 160 bodies (round 5 adds a Ø9 washer under each idler wall nut), no exemptions: **0 collisions** (tolerance 0.5 mm³). A plate pushed 0.5 mm into the PETG would show 33–80 mm³, so the check sees them.
- **Idler and jack screws.**
  - The idler, its hardware and the jack screw are clear at both slot ends, with the plates in place.
  - Both plates' slots cover the bolt's whole travel with either plate anywhere in its 0.4 mm of play (bolt centre x 115.9–124.5 against 116–124 needed).
  - Both Ø9 washers stay on their plates at every slot position: 0.3 mm to spare at the front end (0.1 with a plate pushed to the rear of its play).
  - The jack screw still bears on 2.7 mm of the head and clears the head washer by 0.3. It keeps 6.5 mm of thread in the buttress, with its socket outside it.
  - A 1.5 mm key reaches it at 25° with the lid off and the sensor in place.
  - The nut plate and its lip and stops stay 3.0 mm inboard of the links' inner edge (\|y\| 43).
- **Motor variants.** An 11 mm gearbox is clear. The specified 10 mm shaft and the 9.6 mm minimum both sit 5 mm deep in the hub; their ends reach 2.5 and 2.1 mm into the sprocket disc's centre hole.
- **Fastener stacks.**
  - Thread past the nyloc: 2.0 mm (road wheels) and 4.2 mm (idlers, unchanged by round 5: only the parts inside the stack moved).
  - The idler's hub (from \|y\| 43.7, in its own model) seats on the running washer on the wall nut.
  - The wall nuts engage. A partly threaded ISO 4762 screw would not.
  - Hub screws go 4.5 mm into the hub, and their tips stop 1.0 mm from the skin.
- **Tracks.**
  - 7 teeth sit in link notches on every sprocket and idler.
  - Measured link clearance: 1.0 mm to the housing, 1.5 mm to the nacelle.
- **Size.** The track bottom is at Z 0. Overall 159.8 × 155.0 × 72.7 mm.

## Status

| # | Piece | Status |
|---|---|---|
| 1–6 | all | Round 3: modelled, built, mesh-checked, `cad_checks.py` passing, assembly-checked, reviewed |
| 1 | Chassis | Round 5 (user-approved after the fourth DESIGN failure): idler nut slot deleted (8.0 mm of PETG between the plates), nut plate as the head plate's twin on the wall's outer face on a printed lip between end stops, Ø9 washer under the wall nut; built, mesh-checked, `cad_checks.py` passing (50), assembly-checked. Fresh DFM and strength reviews next |
| 2 | Lid | Round 4: rails 4.5 mm wide; DFM PASS, strength NEEDS_TEST; sliced at 5 perimeters, and `print_requirements.json` now asks for at least 5 (round 5) |
| 3 | Sprocket | Unchanged geometry. Architect's decision after its round 4 strength re-check: a **10 mm shaft only** (at least 9.6 mm from the gearbox face). A 9 mm shaft reaches 1.5 mm into the centre hole and fails H5 (SF 2.24); at 9.6 mm H4 is 4.95 and H5 3.13. Build guide §1 and §3 step 6 check it; the assembly check now runs the 9.6 mm minimum |
| 4 | Idler | Round 5: hub starts at \|y\| 43.7 (5.2 mm shorter, 14.8 tall) to make room for the nut plate, washer and nut outside the wall; disc, teeth and bolt stack beyond the disc unchanged; built, mesh-checked, `cad_checks.py` passing (5). Fresh DFM and strength reviews next; its round 4 slice is stale |
| 5–6 | Wheel, link | Unchanged |

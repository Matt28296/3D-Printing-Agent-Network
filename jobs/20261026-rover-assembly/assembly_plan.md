# Assembly plan: tracked rover (ESP32, 2 × N20, printed tracks)

Robot 2 of 3 (after the desktop arm, before the hexapod). Architect: Claude, 2026-10-26; rounds 3 and 4 the same day (round 4: strength round 3's fixes to the chassis and lid, approved by the user).
The user chose the ESP32 and left motors, power and material to the designer. System spec and acceptance tests: [spec.md](spec.md).

## Decisions

| Item | Choice | Why |
|---|---|---|
| Layout | Skid-steer tank: one drive sprocket per side at the rear, a toothed idler at the front, two road wheels per side | Simple, turns on the spot, every part prints flat or axis-vertical |
| Drive | 2 × N20 gear motors, 6 V 100 rpm (150:1, LP or MP, 9 mm gearbox, 3 mm D-shaft 9–10 mm), each rolled 45°. The diamond gearbox slides along a V-trough into a pocket through the wall, a housing and a nacelle inside the track's wrap. The face stops on a 2 mm skin (round 4; 1 mm before). A Pololu #1996 aluminium hub on the shaft carries the sprocket disc on 4 × M3 (concept C, sprocket design_brief.md) | Metal torque path. The shaft overhang is 11 mm, so the shaft SF is 3.06 at stall and 1.91 at a 5 cm corner drop (chassis strength round 3). No journal friction. The motor is located by its face, so 9/11 mm gearboxes and 9/10 mm shafts fit (a 9 mm shaft now reaches only 1.5 mm into the sprocket's centre hole: see Status) |
| Driver | TB6612FNG carrier on a 170-point mini breadboard on the lid | 1.2 A per channel (N20 stall 0.36–0.7 A for the pinned class); 3.3 V logic matches the ESP32 |
| Controller | ESP32 DevKit (38- or 30-pin), pins down, in a seat on the lid | User's choice; female jumpers reach every pin through the window |
| Power | 2 × 18650 in series (7.4 V) on the floor under a velcro strap: protected ≈70 mm cells in a holder up to 80 mm long, or unprotected cells + a 2S BMS. MTS-102 toggle on the lid, lever up. MP1584 buck at 5.0 V under the lid. Cells charged outside the rover in a two-bay charger | Estimated 5–11 h (deep review 04 S-14). Motors are rated 6 V, so the test sketch limits PWM |
| Sensor | HC-SR04 behind the front wall, transducers through two holes, pins bent back with the leads soldered on | Obstacle distance for a first autonomous program; no room for a Dupont housing below the board |
| Tracks | 34 printed links per side, 10 mm pitch, on Ø2 × 24 steel dowel pins. The outer knuckles grip each pin and it runs in the centre knuckle with 0.3 mm clearance. 10-tooth sprocket and idler (pitch radius 16.18); road wheels with 45° V-flanges | Steel pins survive a wheel landing on a hinge (strength round 1) |
| Tension | Idler bolt in a ±4 mm slot. An M3 × 20 jack screw in a buttress behind the idler block bears on the bolt head: a positive stop with no friction. The bolt is snug between two 2 mm steel plates (round 4): a 20.6 × 10 head plate flush in a recess in the block face, under the Ø9 DIN 9021 washer, and a 14 × 8 nut plate on the bottom of a 9 mm tall nut slot, under the wall nut | Holds the 29.8 N reverse-stall pull; the plates carry the bolt's yaw moment on steel footprints (strength round 3). Re-tension with the lid off, the sensor stays. The nut isn't held by flats in the tall slot, so the bolt is snugged before the idler goes on and never turned again |
| Axles | M3 socket-head screws, class 12.9, fully threaded: × 50 for road wheels, × 40 for idlers. Head inside on a washer, nut trapped in the wall, washer, part, washer, DIN 985 nyloc | Fully threaded, so the wall nut engages; ≥ 1.5 mm of thread past each nyloc (2.0 / 4.2) |
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
| N20 (rolled 45°) | gearbox face \|y\| 44.0 on the 2 mm skin (44–46); thrust washer 46.0–46.5; hub 46.5–51.5; sprocket disc 51.5–58.5; shaft end 54 (10 mm shaft) or 53 (9 mm): 5 mm in the hub, 2.5 or 1.5 mm in the disc's centre hole |
| Housing / nacelle | housing \|y\| 38–42, 1.0 mm from the links; nacelle \|y\| 42–46, r ≤ 10.91 (links' inner faces r ≥ 12.39 on the wrap) |
| Axle-bolt heads | road wheels \|y\| 27.5 on an ISO 7089 washer; idlers \|y\| 27.2 on a DIN 9021 washer on the head plate |
| Idler clamp plates (round 4) | 2 mm steel (`PLATE_T`). Head plate 20.6 × 10 at x 108.2–128.8, \|y\| 28–30, in a recess x 108–129 (buttress face to front strip); nut plate 14 × 8 at x 113–127, \|y\| 33.4–35.4, in a nut slot 9 tall × 15 long, \|y\| 33.4–38. Both slotted 3.4 × 12, so the bolt travels x 115.5–124.5 (the slot needs 116–124) |
| Jack screws | along X at (\|y\| 25.4, Z 20.68), threaded in buttresses x 101.5–108 |
| Lid | Z 48.68 … 51.68; screws at (−13, ±32.5), (102, ±32.5); toggle at (0, −23) |
| Overall | 159.8 × 155.0 × 72.7 (assembly_check.json) |

## Printed pieces

| # | Job | Piece | Qty | Orientation |
|---|---|---|---|---|
| 1 | 20261026-rover-chassis | Tub with motor troughs, pockets, housings and nacelles; wheel bosses; idler slots and jack-screw buttresses; insert columns; strap slots; sensor holes | 1 | floor down |
| 2 | 20261026-rover-lid | Deck with ESP32 seat, breadboard area, toggle hole, cable slots and tie bar | 1 | flat |
| 3 | 20261026-rover-sprocket | 10-tooth disc bolted to the hub through 4 radial slots | 2 | outer face down |
| 4 | 20261026-rover-idler | Toothed idler, Ø10 hub, round Ø3.5 bore | 2 | outer face down, hub up |
| 5 | 20261026-rover-wheel | Road wheel, V-flanges, 0.4 mm bed chamfer | 4 | outer flange down |
| 6 | 20261026-rover-track-link | Track link | 68 + 2 spare (2 plates) | inner face down |

## Assembly check (`assembly_check.py` → `assembly_check.json`, `assembly_rover.png`)

Both 34-link loops are placed pin by pin (13 on the bottom run, 5 round the idler, 12 on the top run, 4 round the sprocket), with every printed part and these bought parts:
- **Drivetrain:** the detailed N20 (end cap, tabs, Ø4 × 0.8 bearing boss, D-shaft), rolled 45°; hubs, thrust washers, hub screws and their washers.
- **Axles:** axle bolts at their real lengths, head washers, wall nuts, running washers and nylocs; the jack screws; the idler head and nut plates (round 4), fixed while the idler hardware moves to both slot ends.
- **Electronics and power:** the 80 mm battery holder and its strap; the HC-SR04 with bent pins and soldered leads; the ESP32 with jumper housings; the breadboard, TB6612 and buck; the toggle with its nuts and lever.
- **Lid fixing:** inserts and lid screws.

Results:
- **Collisions.** 158 bodies (round 4 adds the four plates), no exemptions: **0 collisions** (tolerance 0.5 mm³). A plate pushed 0.5 mm into the PETG would show 33–80 mm³, so the check sees them.
- **Idler and jack screws.**
  - The idler, its hardware and the jack screw are clear at both slot ends, with the plates in place.
  - The Ø9 washer stays on the head plate at every slot position (0.3 mm to spare at the front end), and the nut's flats stay on the nut plate (0.25 mm).
  - The jack screw keeps 6.5 mm of thread in the buttress, with its socket outside it.
  - A 1.5 mm key reaches it at 25° with the lid off and the sensor in place.
- **Motor variants.** An 11 mm gearbox is clear. 9 and 10 mm shafts both sit 5 mm deep in the hub; their ends reach 1.5 and 2.5 mm into the sprocket disc's centre hole (round 4: 1 mm less than before).
- **Fastener stacks.**
  - Thread past the nyloc: 2.0 mm (road wheels) and 4.2 mm (idlers).
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
| 1 | Chassis | Round 4: 2 mm skin, idler head-plate recesses and 9 mm nut slots for the steel plates; built, mesh-checked, `cad_checks.py` passing (47), assembly-checked. Fresh DFM and strength reviews next |
| 2 | Lid | Round 4: rails 4.5 mm wide; built, mesh-checked, `cad_checks.py` passing (14), assembly-checked. Fresh DFM and strength reviews next |
| 3–6 | Sprocket, idler, wheel, link | Unchanged in round 4 (no geometry change follows from the skin). Open for the Architect: the sprocket's strength rows H4/H5 assumed a 9 mm shaft 2.5 mm deep in the centre hole; now a 9 mm shaft reaches 1.5 mm (H5 about 2.2 by the sprocket report's own formula) and a 10 mm shaft 2.5 mm. Either specify a 10 mm shaft only, or have the sprocket's H5 re-checked |

# Part spec: Rover chassis (tub)

Job: 20261026-rover-chassis · Written by: Architect · Date: 2026-10-26 (round 3) · Assembly: [20261026-rover-assembly](../20261026-rover-assembly/assembly_plan.md)

## 1. Function
Open-top tub, 154 × 76 × 40 mm with 4.5 mm walls, plus a motor housing and nacelle on each side wall at the rear (154 × 92 overall). It holds both N20 drive motors. Each motor is rolled 45° about its shaft and slides from inside the tub along a V-trough into a diamond pocket. The pocket runs through the wall, the housing (beside the track) and a nacelle that reaches inside the track's wrap. The gearbox face stops on a 1 mm skin, and an aluminium hub on the shaft outside the skin carries the sprocket, so the torque path is metal and the shaft overhang is 10 mm. The tub also carries the axle bolts for 4 road wheels and 2 idlers (heads inside on washers, nuts trapped in the outer face; idler bolts in a ±4 mm slot, held against the track tension by an M3 jack screw), the battery holder (velcro strap through floor slots), the HC-SR04 (front wall) and four lid columns with M3 heat-set inserts.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions:
  - 154 × 92 × 40 mm. Axles at Z 20.68: X 0 sprocket (N20 shaft), 40 and 80 road wheels, 120 ± 4 idler. Track centre planes Y ±55, links' inner edges at |y| 43.
  - Drivetrain: diamond gearbox pocket (12.4 × 10.4 CAD, rolled 45°) from the trough's rear end (|y| 16.5) to the gearbox face at |y| 45.0; housing |y| 38–42 (x ±11.2, floor to Z_A + 12.5); nacelle |y| 42–46 (2 mm walls, r ≤ 10.9 from the axle); skin |y| 45–46 with a Ø4.7 CAD teardrop round the N20's Ø4 × 0.8 bearing boss. V-trough cradle under the can (x ±12.1, walls ≥ 4 mm, top at Z_A − 0.71, rear end |y| 17.5) with a 4 × 1.9 zip-tie tunnel under the can at |y| 22–26.
  - Road-wheel bosses Ø26 with an r1.5 rim fillet, idler block 30 × 24; both faces at |y| 28 (BOSS_IN 5.5); 1.5 × 45° strips where bosses, idler block, trough and housing meet a wall. 4 × Ø3.6 teardrop bolt holes + 6.0 AF CAD nut traps (2.6 deep); idler slot ±4 (teardrop ends, hull up to Z_A + 2.55) with a sliding nut slot.
  - Idler jack screws: Ø2.8 CAD teardrop pilots along X at (|y| 25.4, Z_A) through buttresses x 101.5–108 (inner face |y| 22).
  - Lid columns Ø10 at (−13, ±32.5) and (102, ±32.5) with Ø4.0 × 6.5 holes for M3 heat-set inserts. Strap slots 22 × 3 at |y| 26, centred on x 62. HC-SR04: 2 × Ø16.6 CAD teardrops in the front wall at y ±13, z 30. No switch hole (the toggle moved to the lid).
- Fasteners used (all bought, see the BUILD_GUIDE BOM):
  - Road wheels: 4 × M3 × 50 and idlers: 2 × M3 × 40 socket head cap screws, **class 12.9, fully threaded** (each must engage the nut trapped in the wall; a partly threaded ISO 4762 screw's 18 mm of thread never reaches it). Under each head: an M3 washer (ISO 7089, 7 × 0.5) for the road wheels, an M3 DIN 9021 washer (9 × 0.8) for the idlers. Then: M3 nut (DIN 934) in each wall trap, washer, wheel or idler, washer, M3 nyloc (DIN 985).
  - 2 × M3 × 20 set screws (DIN 913, flat point) as idler jack screws.
  - Per motor: 1 zip tie (≤ 3.6 mm wide). Battery: 1 velcro strap (20 mm).
  - Lid: 4 × M3 heat-set inserts (M3 × 5.7, Ø4.0 hole) + 4 × M3 × 8 screws.
  - HC-SR04: hot glue.

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Sprocket-to-idler axle distance | 120.0 (slot ±4) | ±0.3 | track length 34 × 10 |
| Axle height | Z 20.68 | ±0.3 | track meets the ground |
| Gearbox pocket (diamond, 45°) | 12.2 × 10.2 printed (12.4 × 10.4 CAD) | +0.15/−0 | gearbox 12 × 10 slides in, 0.1 a side |
| Gearbox face (skin inner face) | \|y\| 45.0 | ±0.2 | sets the hub and sprocket position |
| Skin | 1.0 thick, Ø4.5 printed boss hole | ±0.1 | clears the Ø4 × 0.8 bearing boss |
| Nacelle | r ≤ 10.9 from the axle | max | 1.5 mm inside the wrapping links (r ≥ 12.39) |
| Housing outer face | \|y\| 42.0 | ±0.2 | 1.0 mm from the links' inner edge |
| Bolt holes | Ø3.4 printed (Ø3.6 CAD) | +0.15/−0 | M3 clearance |
| Nut traps | 5.8 AF × 2.6 deep printed | +0.2/−0 | M3 nut push fit |
| Boss / idler-block faces | \|y\| 28.0 | ±0.2 | sets the bolt-head stack |
| Jack-screw pilot | Ø2.6 printed (Ø2.8 CAD), axis \|y\| 25.4 | ±0.1 | M3 set screw taps its own thread |
| Insert holes | Ø4.0 × 6.5 (maker's size, no compensation) | ±0.1 | M3 × 5.7 heat-set insert |

Motor, battery-holder and sensor sizes are nominal (tools/hobby_parts.py: N20_100RPM, BATT_2X18650_LONG, HCSR04). The motor is an N20 (GA12) 6 V, 100 rpm (≈150:1), low- or medium-power winding (stall ≤ 0.7 A at 6 V), 9 mm gearbox, 3 mm D-shaft 10 mm long. A 9 mm shaft and an 11 mm gearbox also fit, because the gearbox face is the datum. Measure your N20 (gearbox section 12 × 10, can Ø12 with 10 mm flats, shaft Ø3 with a 2.5 mm D-flat) and your 2 × 18650 holder (up to 80 × 41 × 21) before printing, and give Claude any difference over 0.3 mm. Track pins: Ø2 × 24 mm steel dowel pins (ISO 8734 / ISO 2338, m6), or 2 mm steel rod cut to 23.5 mm and deburred.

## 4. Loads
Design loads, as re-derived by strength round 2 (see the strength.md files):
- **Rover mass:** 649 g (6.36 N; a heavy-side estimate with 68 steel pins).
- **Motor stall:** 160 N·mm design value at the 7.4 V pack. A fresh 8.4 V pack gives 182 N·mm at 100 % PWM and 146 at the sketch's 80 % cap. That is 9.9 N of sprocket pull per side at the 16.18 mm pitch radius.
- **Track:** pretension 5 N per run (sustained); tight run 14.9 N at stall, 8.2 N everyday.
- **Sprocket radial:** 19.9 N stall / 13.2 N cyclic / 10 N sustained.
- **Idler radial:** 29.8 N at a reverse stall (both runs tight) / 16.4 N cyclic / 10 N sustained.
- **Skid-steer side drag:** 3 N per track.
- **Drop: 5 cm onto a hard floor** (the design limit). E = m·g·h = 0.318 J over a 5 mm stopping distance gives a 20 g peak and 127 N in total: 15.9 N per axle on a flat landing (8 axles) and 31.8 N per axle on a corner (half the mass on 2 axles), short-term.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Sprocket radial through the N20 shaft into the pocket | 19.9 stall, 13.2 cyclic, 10 sustained; 31.8 at a 5 cm corner | track plane Y 55, 10 mm outboard of the gearbox face; pocket edges carry 1.87 R and 0.87 R | as stated | hours / seconds |
| Motor reaction torque | 160 N·mm (182 fresh pack) | gearbox in the diamond pocket | short-term | seconds |
| Road-wheel bolt, drop | 15.9 flat / 31.8 corner per axle | track plane, 17 mm from the wall face: boss bending, nut and hole-edge bearing | short-term | seconds |
| Idler bolt against the jack screw | 29.8 reverse stall, 10 sustained | rearward along the slot; jack screw thread in the buttress, bolt head bearing | short-term / sustained | seconds / hours |
| Skid-steer side load | 3 per track | flanges and teeth → bolts and shaft → walls | cyclic | hours |

## 5. Environment
- Max temperature (°C): 40 (indoor floor; N20 motors run warm, the 18650 cells must stay below 45 °C)
- Outdoor / UV: occasional indoor/outdoor use on dry ground; no UV-critical parts
- Chemicals, oils, moisture: dust and grit on the tracks

## 6. Material
- Preferred or required: PETG (designer's choice; the user left material to the designer)
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA for the chassis and tracks (creep and impact); TPU optional later for grip pads, not used now

## 7. Quantity and time
- Quantity: 1
- Max acceptable print time per batch (h): 12

## 8. Acceptance criteria (measurable)
- [ ] Each N20 slides along its trough into its pocket until the gearbox face stops on the skin; the hub turns freely 0.5 mm clear of the skin on its thrust washer
- [ ] Battery holder (up to 80 mm) fits between the strap slots
- [ ] HC-SR04 transducers fit through the front wall
- [ ] Idler bolts slide the full ±4 mm slot, and the jack screw pushes them through it
- [ ] **Proof tests** (strength round 2; measure the motors first):
  1. **Axle bolt and boss.** With a road wheel on its M3 × 50 bolt, hang **5 kg (49 N, 1.5 × the 31.8 N corner load)** for 1 min from a strap round the **middle of the wheel rim** (on the track centre plane, 17 mm from the wall). Repeat on an idler bolt at mid-slot, with the jack screw set. Pass: no crack or whitening at the boss, nut trap or floor fillet; the bolt still square (≤ 0.5 mm runout at its tip); the idler bolt not moved (pen mark at the slot).
  2. **Stall.** First measure each motor's stall torque at 100 % PWM on a freshly charged pack: a 50 mm arm screwed to the hub, pressing on a kitchen scale. It must read ≤ 371 g (182 N·mm); if it reads more, the motor is not the specified type, so stop and don't run this test. Then, with the track tensioned, stall each motor at **100 % PWM on the fresh pack for 1 s, 5 times, forward and in reverse** (reverse loads the idler with both runs tight). Pass: no motor movement in its pocket (pen marks on can and trough); no crack at the nacelle, housing, skin or trough; the idler bolt not slid (pen mark); no slip of the hub on the shaft or of the sprocket on the hub (pen marks).
  3. **Drop.** Drop the assembled rover (battery fitted, lid on) from 5 cm onto a hard floor, flat and on each of the four corners. Pass: no cracks, bolts square, tracks on, the sprockets run true with no visible wobble, motors not shifted, every wheel spins freely.

## 9. Notes and open questions
None open. Shared frames, clearances and the fastener stacks: see the assembly plan and `assembly_check.json`.

# Part spec: Rover chassis (tub)

Job: 20261026-rover-chassis · Written by: Architect · Date: 2026-10-26 (round 3; round 4 by design-lead: strength round 3's changes 1 and 2) · Assembly: [20261026-rover-assembly](../20261026-rover-assembly/assembly_plan.md)

## 1. Function
Open-top tub, 154 × 76 × 40 mm with 4.5 mm walls, plus a motor housing and nacelle on each side wall at the rear (154 × 92 overall). It holds both N20 drive motors. Each motor is rolled 45° about its shaft and slides from inside the tub along a V-trough into a diamond pocket. The pocket runs through the wall, the housing (beside the track) and a nacelle that reaches inside the track's wrap. The gearbox face stops on a 2 mm skin, and an aluminium hub on the shaft outside the skin carries the sprocket, so the torque path is metal and the shaft overhang is 11 mm. The tub also carries the axle bolts for 4 road wheels and 2 idlers (heads inside on washers, nuts trapped in the outer face; idler bolts in a ±4 mm slot, clamped between two 2 mm steel plates and held against the track tension by an M3 jack screw), the battery holder (velcro strap through floor slots), the HC-SR04 (front wall) and four lid columns with M3 heat-set inserts.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions:
  - 154 × 92 × 40 mm. Axles at Z 20.68: X 0 sprocket (N20 shaft), 40 and 80 road wheels, 120 ± 4 idler. Track centre planes Y ±55, links' inner edges at |y| 43.
  - Drivetrain: diamond gearbox pocket (12.4 × 10.4 CAD, rolled 45°) from |y| 15.5 (behind the trough's rear end) to the gearbox face at |y| 44.0; housing |y| 38–42 (x ±11.2, floor to Z_A + 12.5); nacelle |y| 42–46 (2 mm walls, r ≤ 10.9 from the axle); skin |y| 44–46 (2 mm, round 4) with a Ø4.7 CAD teardrop round the N20's Ø4 × 0.8 bearing boss. V-trough cradle under the can (x ±12.1, walls ≥ 4 mm, top at Z_A − 0.71, rear end |y| 16.5) with a 4 × 1.9 zip-tie tunnel under the can at |y| 22–26.
  - Road-wheel bosses Ø26 with an r1.5 rim fillet, idler block 30 × 24; both faces at |y| 28 (BOSS_IN 5.5); 1.5 × 45° strips where bosses, idler block, trough and housing meet a wall. 4 × Ø3.6 teardrop bolt holes + 6.0 AF CAD nut traps (2.6 deep); idler slot ±4 (teardrop ends, hull up to Z_A + 2.55).
  - Idler clamp (round 4, strength round 3 change 1): a 2 mm recess in each idler-block face for the steel head plate, x 108–129 (from the buttress's front face to the front 45° strip, cutting neither), |y| 28–30, Z_A ± 5.2 with a 45° roof up to Z_A + 7.2 at the face; and an idler nut slot opened to 9 mm tall (Z_A ± 4.5) and 2 mm deeper (|y| 33.4–38), x 112.5–127.5, for the steel nut plate on its bottom and the sliding nut on the plate. The slot's roof is flat over the plate (|y| 33.4–35.4), then rises at 45° to the outer face. The plate depths are one parameter, `PLATE_T` = 2.0 (rover_frame.py).
  - Idler jack screws: Ø2.8 CAD teardrop pilots along X at (|y| 25.4, Z_A) through buttresses x 101.5–108 (inner face |y| 22).
  - Lid columns Ø10 at (−13, ±32.5) and (102, ±32.5) with Ø4.0 × 6.5 holes for M3 heat-set inserts. Strap slots 22 × 3 at |y| 26, centred on x 62. HC-SR04: 2 × Ø16.6 CAD teardrops in the front wall at y ±13, z 30. No switch hole (the toggle moved to the lid).
- Fasteners used (all bought, see the BUILD_GUIDE BOM):
  - Road wheels: 4 × M3 × 50 and idlers: 2 × M3 × 40 socket head cap screws, **class 12.9, fully threaded** (each must engage the nut trapped in the wall; a partly threaded ISO 4762 screw's 18 mm of thread never reaches it). Under each head: an M3 washer (ISO 7089, 7 × 0.5) for the road wheels, an M3 DIN 9021 washer (9 × 0.8) for the idlers. Then: M3 nut (DIN 934) in each wall trap, washer, wheel or idler, washer, M3 nyloc (DIN 985).
  - 2 × M3 × 20 set screws (DIN 913, flat point) as idler jack screws.
  - Idler clamp plates (round 4), made from 2 mm steel (14-gauge 1.9 mm, or metric 2 mm, flat bar or strip; not 1/8 in, which is 3.2 mm and doesn't fit the 2 mm recess): 2 head plates 20.6 × 10 × 2, slotted 3.4 × 12 from 6 to 18 mm along, each in its block-face recess under the DIN 9021 washer; 2 nut plates 14 × 8 × 2, slotted 3.4 × 12 in the middle, each on the bottom of its nut slot under the wall nut. The head plate is strength round 3's 21 × 10 cut 0.4 mm short so it drops into its recess (the recess fills the 21 mm between the buttress and the corner strip and prints about 20.8). In the 9 mm slot the idler nut is no longer held by its flats: hold it while the bolt is snugged (BUILD_GUIDE step 3), and don't turn the idler heads after that; the jack screw slides the snug bolt.
  - Per motor: 1 zip tie (≤ 3.6 mm wide). Battery: 1 velcro strap (20 mm).
  - Lid: 4 × M3 heat-set inserts (M3 × 5.7, Ø4.0 hole) + 4 × M3 × 8 screws.
  - HC-SR04: hot glue.

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Sprocket-to-idler axle distance | 120.0 (slot ±4) | ±0.3 | track length 34 × 10 |
| Axle height | Z 20.68 | ±0.3 | track meets the ground |
| Gearbox pocket (diamond, 45°) | 12.2 × 10.2 printed (12.4 × 10.4 CAD) | +0.15/−0 | gearbox 12 × 10 slides in, 0.1 a side |
| Gearbox face (skin inner face) | \|y\| 44.0 | ±0.2 | the motor's datum; the hub and sprocket sit on the fixed skin outer face (\|y\| 46) |
| Skin | 2.0 thick (\|y\| 44–46), Ø4.5 printed boss hole | ±0.1 | clears the Ø4 × 0.8 bearing boss |
| Nacelle | r ≤ 10.9 from the axle | max | 1.5 mm inside the wrapping links (r ≥ 12.39) |
| Housing outer face | \|y\| 42.0 | ±0.2 | 1.0 mm from the links' inner edge |
| Bolt holes | Ø3.4 printed (Ø3.6 CAD) | +0.15/−0 | M3 clearance |
| Nut traps | 5.8 AF × 2.6 deep printed | +0.2/−0 | M3 nut push fit |
| Boss / idler-block faces | \|y\| 28.0 | ±0.2 | sets the bolt-head stack |
| Jack-screw pilot | Ø2.6 printed (Ø2.8 CAD), axis \|y\| 25.4 | ±0.1 | M3 set screw taps its own thread |
| Head-plate recess | 2.0 deep (= `PLATE_T`), x 108–129 (21.0 CAD), Z_A ± 5.2 + 45° roof | ±0.1 | 20.6 × 10 × 2 steel plate sits flush with the block face (\|y\| 28) |
| Idler nut slot | 9.0 tall × 4.6 deep (\|y\| 33.4–38) × 15.0 long | +0.2/−0 | 14 × 8 × 2 nut plate (0.5 under the flat roof) + M3 nut on it |
| Insert holes | Ø4.0 × 6.5 (maker's size, no compensation) | ±0.1 | M3 × 5.7 heat-set insert |

Motor, battery-holder and sensor sizes are nominal (tools/hobby_parts.py: N20_100RPM, BATT_2X18650_LONG, HCSR04). The motor is an N20 (GA12) 6 V, 100 rpm (≈150:1), low- or medium-power winding (stall ≤ 0.7 A at 6 V), 9 mm gearbox, 3 mm D-shaft 10 mm long from the gearbox face (at least 9.6 mm: a 9 mm shaft is too short for the sprocket's centre hole, sprocket strength round 4). An 11 mm gearbox also fits, because the gearbox face is the datum. Measure your N20 (gearbox section 12 × 10, can Ø12 with 10 mm flats, shaft Ø3 with a 2.5 mm D-flat) and your 2 × 18650 holder (up to 80 × 41 × 21) before printing, and give Claude any difference over 0.3 mm. Track pins: Ø2 × 24 mm steel dowel pins (ISO 8734 / ISO 2338, m6), or 2 mm steel rod cut to 23.5 mm and deburred.

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
| Sprocket radial through the N20 shaft into the pocket | 19.9 stall, 13.2 cyclic, 10 sustained; 31.8 at a 5 cm corner | track plane Y 55, 11 mm outboard of the gearbox face (round 4); pocket edges carry 1.87 R and 0.87 R | as stated | hours / seconds |
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
- [ ] Each steel plate drops into its place: the head plates flush in their block-face recesses, the nut plates on the bottoms of their nut slots
- [ ] Idler bolts slide the full ±4 mm slot through both plates, and the jack screw pushes them through it
- [ ] **Proof tests** (strength rounds 2 and 3; measure the motors first; run them only with both idler plates fitted):
  1. **Axle bolt and boss.** With a road wheel on its M3 × 50 bolt, hang **5 kg (49 N, 1.5 × the 31.8 N corner load)** for 1 min from a strap round the **middle of the wheel rim** (on the track centre plane, 17 mm from the wall). Repeat on an idler bolt at mid-slot, with the jack screw set. On the idler, also pull **4.5 kg (44 N) rearward along the track line for 1 min** (idler `spec.md` §8 test 1). Before and after, measure the idler disc's rear face against a fixed mark on the chassis. Pass: no crack or whitening at the boss, nut trap, plates or floor fillet; the bolts still square (≤ 0.5 mm runout at the tip); **the idler disc moved ≤ 0.3 mm**.
  2. **Stall.** First measure each motor's stall torque at 100 % PWM on a freshly charged pack, **with the hub on and before the sprocket disc is fitted** (BUILD_GUIDE step 6): a 50 mm arm screwed to the hub, pressing on a kitchen scale. It must read ≤ 371 g (182 N·mm); if it reads more, the motor is not the specified type, so stop: don't fit the sprocket disc to it and don't run this test. Then, with the track tensioned, stall each motor at **100 % PWM on the fresh pack for 1 s, 5 times, forward and in reverse** (reverse loads the idler with both runs tight). The sketch caps the average motor voltage at 6.0 V (`MOTOR_V`), so lift the cap for this test only (`MOTOR_V` 8.4, then back to 6.0). Pass: no motor movement in its pocket (pen marks on can and trough); no crack at the nacelle, housing, skin or trough; no slip of the hub on the shaft or of the sprocket on the hub (pen marks); **after the reverse stalls, the idler disc has moved ≤ 0.3 mm** (measured as in test 1); **with the hubs off, the skins and nacelles show no crack or whitening**.
  3. **Drop.** Drop the assembled rover (battery fitted, lid on) from 5 cm onto a hard floor, flat and on each of the four corners. Pass: no cracks, bolts square, tracks on, the sprockets run true with no visible wobble, motors not shifted, every wheel spins freely. Then **take each hub off and inspect the skin and nacelle** (no crack or whitening), and **check the idler bolts are still square** (≤ 0.5 mm runout at the tip).

## 9. Notes and open questions
None open. Shared frames, clearances and the fastener stacks: see the assembly plan and `assembly_check.json`.

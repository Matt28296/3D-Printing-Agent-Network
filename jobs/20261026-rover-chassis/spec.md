# Part spec: Rover chassis (tub)

Job: 20261026-rover-chassis · Written by: Architect · Date: 2026-10-26 · Assembly: [20261026-rover-assembly](../20261026-rover-assembly/assembly_plan.md)

## 1. Function
Open-top tub, 154 × 76 × 40 mm, 4.5 mm walls. Holds both N20 drive motors in cradles (cheeks, a rear stop and a zip-tie tunnel; no face screws), with each sprocket hub running in a 6 mm journal in the side wall so the track loads go into the wall, not the N20 shaft. Carries the axle bolts for 4 road wheels (M3 × 45) and 2 idlers (M3 × 35) (heads inside, nuts in traps in the outer faces; idler bolts in an 8 mm tension slot with a sliding nut), the 2 × 18650 holder (velcro strap through floor slots), a mini toggle switch (rear wall) and an HC-SR04 (front wall).

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 154 × 76 × 40 mm. Axles at Z 20.68 (X 0 sprocket journal, 40 and 80 road wheels, 120 ± 4 idler), track centre planes Y ±55. Interfaces: journal Ø10.7 CAD through wall + 1.5 mm boss (6 mm long); N20 cradle with cheeks at x ±6.3–8.3, rear stop posts, zip-tie tunnel; Ø20 road-wheel bosses and a 30 × 24 idler block down to the floor; 6 × Ø3.6 teardrop bolt holes + 5.8 AF nut traps; idler slot ±4 with teardrop ends and a nut slot; 4 lid columns (−13, ±30), (100, ±30) with Ø2.8 pilots; toggle hole Ø6.4; 2 × Ø16.6 teardrop sensor holes; strap slots at |y| 27.5; 3 mm 45° floor fillets.
- Fasteners used: 4 × M3 × 45 (road wheels) and 2 × M3 × 35 (idlers) bolts, class 12.9, head inside the tub, + M3 nut in each wall trap + washer and nyloc on the outer end (wheels and idlers run free between); 2 zip ties for the motors; 4 × M3 × 10 self-tapping for the lid; 1 velcro strap for the battery holder; MTS-102 mini toggle switch (6 mm bushing nut)

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Sprocket-to-idler axle distance | 120.0 (slot ±4) | ±0.3 | track length 34 × 10 |
| Axle height | Z 20.68 | ±0.3 | track meets the ground |
| Journal | Ø10.5 printed, 6 long | +0.15/−0 | running fit on the Ø10 sprocket hub |
| Nut traps | 5.8 AF × 2.6 deep | +0.2/−0 | M3 nut push fit |

Motor, battery-holder and sensor sizes are nominal (tools/hobby_parts.py: N20_100RPM, BATT_2X18650, HCSR04). Measure your N20 (gearbox 12 × 10 × 9, can Ø12 with 10 mm flats, shaft Ø3 with a 2.5 mm D-flat, 10 mm long from the gearbox face) and your 2 × 18650 holder (77 × 41 × 21) before printing, and give Claude any difference over 0.3 mm. Track pins are **2 mm steel rod** (silver steel, drill rod or piano wire), cut 23.5 mm and deburred.

## 4. Loads
Design loads (strength round 1 re-derived them; see the strength.md files): N20 stall ≈160 N·mm at the 7.4 V pack → ≈10 N of sprocket pull per side at the 16.18 mm pitch radius, 14.9 N in the tight run with a 5 N pretension (sustained); rover ≈0.58 kg (5.7 N); skid-steer drag 3 N per track. **Drop: 5 cm onto a hard floor** (the design limit; strength round 1 showed the printed pins and hubs can't survive a 30 cm desk fall): 5 mm stopping distance → 20 g peak → ≈14 N per axle flat, ≈29 N per axle on a corner, short-term.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Sprocket radial load through the journal | 19.9 N stall, 12.9 N cyclic, 10 N sustained (pretension) | journal bearing, wall bending | as stated | hours |
| Road-wheel bolt, drop | ≈14 N flat / 29 N corner per axle (5 cm drop), 17 mm from the wall | boss bending, nut trap | short-term | seconds |
| Idler clamp in the slot | 2 × track tension, ≤ 30 N | nut slot bearing, friction | sustained | hours |
| Skid-steer side load | 3 N per wheel axially | flanges → bolts → walls | cyclic | hours |

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
- [ ] Both N20 motors seat in their cradles and the sprocket hubs turn freely in the journals
- [ ] Battery holder fits between the strap slots
- [ ] HC-SR04 transducers fit through the front wall
- [ ] Idler bolts slide the full ±4 mm slot
- [ ] **Proof test:** (1) With a road wheel fitted on its M3 × 45 bolt, hang 3 kg (≈30 N) from the bolt end next to the wheel for 1 min. Pass: no cracking at the boss or nut trap; the bolt stays square to the wall. (2) Track tensioned, stall both motors at 80 % PWM for 3 s, 5 times: no cracks at the journals, no motor movement in the cradles. (3) Drop the assembled rover (battery fitted, lid on) from 5 cm onto a hard floor, flat and on each corner: no cracks, tracks stay on.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

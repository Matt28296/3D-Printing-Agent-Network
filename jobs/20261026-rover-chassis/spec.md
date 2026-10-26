# Part spec: Rover chassis (tub)

Job: 20261026-rover-chassis · Written by: Architect · Date: 2026-10-26 · Assembly: [20261026-rover-assembly](../20261026-rover-assembly/assembly_plan.md)

## 1. Function
Open-top tub, 154 × 76 × 40 mm, that holds both N20 drive motors (gearbox face screwed to the side walls, can on a cradle with a zip tie), the M3 axle bolts for 4 road wheels and 2 idlers (nuts in traps in the walls' outer faces; idler bolts in an 8 mm tension slot), the 2 × 18650 holder (velcro strap through floor slots), a mini rocker switch (rear wall) and an HC-SR04 (front wall).

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 154 × 76 × 40 mm. Wheel axles at Z 20.68 (X 0 sprocket, 40 and 80 road wheels, 120 ± 4 idler), track centre planes Y ±55. Interfaces: N20 shaft-boss hole Ø4.8 + 2 × Ø2.2 face-screw holes (teardrops); 4 × Ø3.6 bolt holes + nut traps; 2 idler slots; 4 lid columns with Ø2.8 pilots; switch cut-out 15 × 10 with 45° roof; 2 × Ø16.6 teardrop sensor holes; 2 × 3 × 22 strap slots.
- Fasteners used: 4 × M1.6×5 (or M1.6×4) screws through the wall into each N20 gearbox face (2 per motor); 6 × M3×40 bolts + M3 nuts in the traps (+ washer and nyloc on the outer end, wheel/idler free between); 4 × M3×10 self-tapping for the lid; 2 zip ties for the motors; 1 velcro strap for the battery holder

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Sprocket-to-idler axle distance | 120.0 (slot ±4) | ±0.3 | track length 34 × 10 |
| Axle height | Z 20.68 | ±0.3 | track meets the ground |
| N20 face holes | 2 × Ø1.6 + 0.4 clearance, 9 apart | ±0.15 | clearance |
| Nut traps | 5.8 AF × 2.6 deep | +0.2/−0 | M3 nut push fit |

Motor, battery-holder and sensor sizes are nominal (tools/hobby_parts.py: N20_100RPM, BATT_2X18650, HCSR04). Measure your N20 (gearbox 12 × 10, face screw spacing 9, shaft Ø3 with D-flat 2.5, shaft length 10 from the face) and your 2 × 18650 holder (77 × 41 × 21) before printing; give Claude any difference over 0.3 mm. Track pins are 1.75 mm filament (PLA or PETG), cut 25 mm long.

## 4. Loads
Design loads: N20 stall ≈130 N·mm at 6 V (≈160 N·mm at the 7.4 V pack) → up to **10 N of track pull per side** at the 16.2 mm sprocket pitch radius; rover mass ≈0.5 kg (4.9 N); skid-steer turning drags the tracks sideways (μ ≈ 0.6 → ≈3 N per track); a **30 cm drop** off a desk is taken as 5 × weight on one track (≈25 N), short-term.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Track pull at the drive motor | 10 N at the sprocket (≈16 mm out from the wall) | N20 face screws + wall at the motor | cyclic | hours |
| Wheel load, drop case | 25 N on one road-wheel bolt, 17 mm from the wall | bolt boss bending, nut trap | short-term | seconds |
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
- Max acceptable print time per batch (h): 10

## 8. Acceptance criteria (measurable)
- [ ] Both N20 motors fit with their face screws; shafts turn freely
- [ ] Battery holder fits between the strap slots
- [ ] HC-SR04 transducers fit through the front wall
- [ ] **Proof test:** With a road wheel fitted on its M3×40 bolt, hang 2 kg from the bolt end next to the wheel for 1 min (≈20 N, 17 mm out). Pass: no cracking at the boss or nut trap, the bolt stays square to the wall. Then drop the assembled rover (battery fitted, lid on) from 30 cm onto a hard floor, flat and on one corner: no cracks, tracks stay on.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

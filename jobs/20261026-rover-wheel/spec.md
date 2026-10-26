# Part spec: Road wheel (×4)

Job: 20261026-rover-wheel · Written by: Architect · Date: 2026-10-26 · Assembly: [20261026-rover-assembly](../20261026-rover-assembly/assembly_plan.md)

## 1. Function
Carries the rover on the bottom track run (rim r 13.1 meets the links' inner faces) with 45° V-flanges that keep the track centred.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: Ø32.2 × 32.5 mm, running bore Ø3.5 printed.
- Fasteners used: Rides on an M3 × 45 bolt between the wall nut (with a washer) and a washer + nyloc nut

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Rim radius | 13.10 | ±0.15 | meets the link inner face 13.18 below the axle |
| Running bore | Ø3.5 printed | +0.15/−0 | running fit on M3, 0.5 clearance |

Motor, battery-holder and sensor sizes are nominal (tools/hobby_parts.py: N20_100RPM, BATT_2X18650, HCSR04). Measure your N20 (gearbox 12 × 10 × 9, can Ø12 with 10 mm flats, shaft Ø3 with a 2.5 mm D-flat, 10 mm long from the gearbox face) and your 2 × 18650 holder (77 × 41 × 21) before printing, and give Claude any difference over 0.3 mm. Track pins are **2 mm steel rod** (silver steel, drill rod or piano wire), cut 23.5 mm and deburred.

## 4. Loads
Design loads (strength round 1 re-derived them; see the strength.md files): N20 stall ≈160 N·mm at the 7.4 V pack → ≈10 N of sprocket pull per side at the 16.18 mm pitch radius, 14.9 N in the tight run with a 5 N pretension (sustained); rover ≈0.58 kg (5.7 N); skid-steer drag 3 N per track. **Drop: 5 cm onto a hard floor** (the design limit; strength round 1 showed the printed pins and hubs can't survive a 30 cm desk fall): 5 mm stopping distance → 20 g peak → ≈14 N per axle flat, ≈29 N per axle on a corner, short-term.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Drop (5 cm) | ≈14 N flat / 29 N corner, radial | rim → bore bearing | short-term | seconds |
| Skid-steer | 3 N axial on a flange | flange root | cyclic | hours |

## 5. Environment
- Max temperature (°C): 40 (indoor floor; N20 motors run warm, the 18650 cells must stay below 45 °C)
- Outdoor / UV: occasional indoor/outdoor use on dry ground; no UV-critical parts
- Chemicals, oils, moisture: dust and grit on the tracks

## 6. Material
- Preferred or required: PETG (designer's choice; the user left material to the designer)
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA for the chassis and tracks (creep and impact); TPU optional later for grip pads, not used now

## 7. Quantity and time
- Quantity: 4
- Max acceptable print time per batch (h): 3

## 8. Acceptance criteria (measurable)
- [ ] Spins freely; the track runs centred between the flanges
- [ ] **Proof test:** Covered by the chassis drop test; wheels must still spin freely.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

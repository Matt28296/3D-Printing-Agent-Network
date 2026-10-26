# Part spec: Idler (×2)

Job: 20261026-rover-idler · Written by: Architect · Date: 2026-10-26 · Assembly: [20261026-rover-assembly](../20261026-rover-assembly/assembly_plan.md)

## 1. Function
The sprocket's toothed geometry with a round Ø3.5 running bore and a shorter hub, free on the M3 × 35 bolt in the chassis's tension slot, so the track wraps it exactly like the sprocket.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: Ø35.8 × 20 mm, round bore through.
- Fasteners used: Rides on the M3 × 35 idler bolt between the wall nut (with a washer) and a washer + nyloc nut

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Running bore | Ø3.5 printed (Ø3.7 CAD) | +0.15/−0 | running fit on M3, 0.5 clearance |

Motor, battery-holder and sensor sizes are nominal (tools/hobby_parts.py: N20_100RPM, BATT_2X18650, HCSR04). Measure your N20 (gearbox 12 × 10 × 9, can Ø12 with 10 mm flats, shaft Ø3 with a 2.5 mm D-flat, 10 mm long from the gearbox face) and your 2 × 18650 holder (77 × 41 × 21) before printing, and give Claude any difference over 0.3 mm. Track pins are **2 mm steel rod** (silver steel, drill rod or piano wire), cut 23.5 mm and deburred.

## 4. Loads
Design loads (strength round 1 re-derived them; see the strength.md files): N20 stall ≈160 N·mm at the 7.4 V pack → ≈10 N of sprocket pull per side at the 16.18 mm pitch radius, 14.9 N in the tight run with a 5 N pretension (sustained); rover ≈0.58 kg (5.7 N); skid-steer drag 3 N per track. **Drop: 5 cm onto a hard floor** (the design limit; strength round 1 showed the printed pins and hubs can't survive a 30 cm desk fall): 5 mm stopping distance → 20 g peak → ≈14 N per axle flat, ≈29 N per axle on a corner, short-term.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Track tension at the idler | 2 × 14.9 N stall, 2 × 5 N sustained | bore bearing on the bolt, teeth | as stated | hours |

## 5. Environment
- Max temperature (°C): 40 (indoor floor; N20 motors run warm, the 18650 cells must stay below 45 °C)
- Outdoor / UV: occasional indoor/outdoor use on dry ground; no UV-critical parts
- Chemicals, oils, moisture: dust and grit on the tracks

## 6. Material
- Preferred or required: PETG (designer's choice; the user left material to the designer)
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA for the chassis and tracks (creep and impact); TPU optional later for grip pads, not used now

## 7. Quantity and time
- Quantity: 2
- Max acceptable print time per batch (h): 2

## 8. Acceptance criteria (measurable)
- [ ] Spins freely on the bolt with < 0.5 mm axial play
- [ ] **Proof test:** Covered by the chassis stall and drop tests; the idler must still spin freely afterwards.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

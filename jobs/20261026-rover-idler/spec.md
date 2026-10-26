# Part spec: Idler (×2)

Job: 20261026-rover-idler · Written by: Architect · Date: 2026-10-26 · Assembly: [20261026-rover-assembly](../20261026-rover-assembly/assembly_plan.md)

## 1. Function
The sprocket's toothed geometry with a round Ø3.4 running bore, free on the M3 bolt in the chassis's tension slot, so the track wraps it exactly like the sprocket.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: Ø35.8 × 20 mm, round bore through.
- Fasteners used: Rides on the M3×40 idler bolt between the wall nut and a washer + nyloc nut

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Running bore | Ø3.2 printed (Ø3.4 CAD) | +0.15/−0 | running fit on M3 |

Motor, battery-holder and sensor sizes are nominal (tools/hobby_parts.py: N20_100RPM, BATT_2X18650, HCSR04). Measure your N20 (gearbox 12 × 10, face screw spacing 9, shaft Ø3 with D-flat 2.5, shaft length 10 from the face) and your 2 × 18650 holder (77 × 41 × 21) before printing; give Claude any difference over 0.3 mm. Track pins are 1.75 mm filament (PLA or PETG), cut 25 mm long.

## 4. Loads
Design loads: N20 stall ≈130 N·mm at 6 V (≈160 N·mm at the 7.4 V pack) → up to **10 N of track pull per side** at the 16.2 mm sprocket pitch radius; rover mass ≈0.5 kg (4.9 N); skid-steer turning drags the tracks sideways (μ ≈ 0.6 → ≈3 N per track); a **30 cm drop** off a desk is taken as 5 × weight on one track (≈25 N), short-term.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Track tension at the idler | 2 × 10 N (both runs) | bore bearing on the bolt, teeth | cyclic | hours |

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
- [ ] **Proof test:** Covered by the sprocket stall test and the chassis drop test; the idler must spin freely afterwards.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

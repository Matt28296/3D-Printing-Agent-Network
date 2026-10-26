# Part spec: Track link (×68, 34 per side)

Job: 20261026-rover-track-link · Written by: Architect · Date: 2026-10-26 · Assembly: [20261026-rover-assembly](../20261026-rover-assembly/assembly_plan.md)

## 1. Function
10 mm-pitch link with a centre knuckle at the rear hinge and two outer knuckles at the front, pinned with 1.75 mm filament; the centre notch takes a sprocket tooth; grousers on the outer face.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 16 × 24 × 7.5 mm. Pin holes Ø2.1 CAD (Ø1.9 printed) at x 0 and 10.
- Fasteners used: 1 × 25 mm piece of 1.75 mm filament per link; melt or flatten both ends slightly with a soldering iron (or a drop of CA) so the pins can't walk out

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Pitch | 10.00 | ±0.1 | matches the sprocket |
| Pin hole | Ø1.9 printed | +0.1/−0 | free running on 1.75 filament |
| Knuckle gaps | 0.5 axial, 0.4 radial | min | free hinge |

Motor, battery-holder and sensor sizes are nominal (tools/hobby_parts.py: N20_100RPM, BATT_2X18650, HCSR04). Measure your N20 (gearbox 12 × 10, face screw spacing 9, shaft Ø3 with D-flat 2.5, shaft length 10 from the face) and your 2 × 18650 holder (77 × 41 × 21) before printing; give Claude any difference over 0.3 mm. Track pins are 1.75 mm filament (PLA or PETG), cut 25 mm long.

## 4. Loads
Design loads: N20 stall ≈130 N·mm at 6 V (≈160 N·mm at the 7.4 V pack) → up to **10 N of track pull per side** at the 16.2 mm sprocket pitch radius; rover mass ≈0.5 kg (4.9 N); skid-steer turning drags the tracks sideways (μ ≈ 0.6 → ≈3 N per track); a **30 cm drop** off a desk is taken as 5 × weight on one track (≈25 N), short-term.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Track pull | 10 N | pin shear (3 shear planes), knuckle tear-out across the pin | cyclic | hours |
| Drop / obstacle | 25 N on one link | link bending, grousers | short-term | seconds |

## 5. Environment
- Max temperature (°C): 40 (indoor floor; N20 motors run warm, the 18650 cells must stay below 45 °C)
- Outdoor / UV: occasional indoor/outdoor use on dry ground; no UV-critical parts
- Chemicals, oils, moisture: dust and grit on the tracks

## 6. Material
- Preferred or required: PETG (designer's choice; the user left material to the designer)
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA for the chassis and tracks (creep and impact); TPU optional later for grip pads, not used now

## 7. Quantity and time
- Quantity: 68
- Max acceptable print time per batch (h): 6

## 8. Acceptance criteria (measurable)
- [ ] Pinned links flex freely to 40° both ways
- [ ] 34 links close into a loop round sprocket and idler with the idler mid-slot
- [ ] **Proof test:** Pin 5 links into a chain and hang 3 kg from it for 1 min (≈30 N, 3 × the stall pull). Pass: no cracked knuckle, the pins don't pull through, the chain still flexes freely.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

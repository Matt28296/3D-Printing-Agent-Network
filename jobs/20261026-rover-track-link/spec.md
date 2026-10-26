# Part spec: Track link (×68, 34 per side)

Job: 20261026-rover-track-link · Written by: Architect · Date: 2026-10-26 · Assembly: [20261026-rover-assembly](../20261026-rover-assembly/assembly_plan.md)

## 1. Function
10 mm-pitch link with a centre knuckle at the rear hinge and two outer knuckles at the front, pinned with 2 mm steel rod: the pin runs free in the centre knuckle (Ø2.2) and is gripped by the outer knuckles (Ø2.0), so it can't walk out. The centre notch takes a sprocket tooth; grousers on the outer face.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 16 × 24 × 7.5 mm. Pin holes at x 0 (Ø2.4 CAD) and x 10 (Ø2.2 CAD), teardrops pointing at the grouser face.
- Fasteners used: 1 × 23.5 mm piece of 2 mm steel rod per link, pressed into the outer knuckles (flush, deburred)

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Pitch | 10.00 | ±0.1 | matches the sprocket |
| Centre-knuckle hole | Ø2.2 printed | +0.1/−0 | running fit on Ø2 rod |
| Outer-knuckle holes | Ø2.0 printed | +0.05/−0.05 | grip fit on Ø2 rod |
| Knuckle gaps | 0.5 axial, 0.4 radial | min | free hinge |

Motor, battery-holder and sensor sizes are nominal (tools/hobby_parts.py: N20_100RPM, BATT_2X18650, HCSR04). Measure your N20 (gearbox 12 × 10 × 9, can Ø12 with 10 mm flats, shaft Ø3 with a 2.5 mm D-flat, 10 mm long from the gearbox face) and your 2 × 18650 holder (77 × 41 × 21) before printing, and give Claude any difference over 0.3 mm. Track pins are **2 mm steel rod** (silver steel, drill rod or piano wire), cut 23.5 mm and deburred.

## 4. Loads
Design loads (strength round 1 re-derived them; see the strength.md files): N20 stall ≈160 N·mm at the 7.4 V pack → ≈10 N of sprocket pull per side at the 16.18 mm pitch radius, 14.9 N in the tight run with a 5 N pretension (sustained); rover ≈0.58 kg (5.7 N); skid-steer drag 3 N per track. **Drop: 5 cm onto a hard floor** (the design limit; strength round 1 showed the printed pins and hubs can't survive a 30 cm desk fall): 5 mm stopping distance → 20 g peak → ≈14 N per axle flat, ≈29 N per axle on a corner, short-term.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Track pull | 14.9 N stall, 7.9 N everyday | pin bending/shear, knuckle bearing and tear-out | as stated | hours |
| Drop (5 cm) | ≈14 N per axle with a road wheel landing on a hinge | pin bending, knuckle bearing | short-term | seconds |

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
- Max acceptable print time per batch (h): 7

## 8. Acceptance criteria (measurable)
- [ ] Pinned links flex freely to 40° both ways
- [ ] 34 links close into a loop round sprocket and idler with the idler near mid-slot
- [ ] **Proof test:** Pin 5 links into a chain with steel pins and hang 4.5 kg from it for 1 min (≈45 N, 3 × the stall pull). Pass: no cracked knuckle, the pins don't move, the chain still flexes freely to 40° both ways.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

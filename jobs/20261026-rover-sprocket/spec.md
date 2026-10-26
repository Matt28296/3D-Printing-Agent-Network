# Part spec: Drive sprocket (×2)

Job: 20261026-rover-sprocket · Written by: Architect · Date: 2026-10-26 · Assembly: [20261026-rover-assembly](../20261026-rover-assembly/assembly_plan.md)

## 1. Function
10-tooth sprocket (pitch radius 16.18, 45° tooth-root chamfers) on the N20's D-shaft. Its Ø10 hub runs back through the 6 mm journal in the chassis wall to 0.5 mm from the gearbox face, so the wall carries the track loads and the shaft only the torque; the D-bore takes 9.5 mm of the shaft.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: Ø35.8 × 26.5 mm. D-bore Ø3.2 / flat CAD (press fit) 10 deep; M2 set-screw teardrop pilot 2.5 mm outside the wall.
- Fasteners used: 1 × M2 × 4 set screw (or M2 × 6 self-tapper) per sprocket onto the shaft flat; a drop of thread-locker or CA on the bore

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| D-bore | Ø3.0 / flat 2.5 printed | +0.1/−0 | press fit on the N20 shaft |
| Hub | Ø10.0 | −0.1/+0 | runs in the Ø10.5 journal |
| Pitch radius | 16.18 | ±0.15 | matches the 10 mm link pitch |

Motor, battery-holder and sensor sizes are nominal (tools/hobby_parts.py: N20_100RPM, BATT_2X18650, HCSR04). Measure your N20 (gearbox 12 × 10 × 9, can Ø12 with 10 mm flats, shaft Ø3 with a 2.5 mm D-flat, 10 mm long from the gearbox face) and your 2 × 18650 holder (77 × 41 × 21) before printing, and give Claude any difference over 0.3 mm. Track pins are **2 mm steel rod** (silver steel, drill rod or piano wire), cut 23.5 mm and deburred.

## 4. Loads
Design loads (strength round 1 re-derived them; see the strength.md files): N20 stall ≈160 N·mm at the 7.4 V pack → ≈10 N of sprocket pull per side at the 16.18 mm pitch radius, 14.9 N in the tight run with a 5 N pretension (sustained); rover ≈0.58 kg (5.7 N); skid-steer drag 3 N per track. **Drop: 5 cm onto a hard floor** (the design limit; strength round 1 showed the printed pins and hubs can't survive a 30 cm desk fall): 5 mm stopping distance → 20 g peak → ≈14 N per axle flat, ≈29 N per axle on a corner, short-term.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Motor stall torque | 160 N·mm (182 fresh pack at 100 % PWM) | D-flat bearing, set screw | short-term | seconds |
| Tooth load | 14.9 N on one tooth tip (tight run at stall) | tooth root bending (in-plane) | short-term | seconds |
| Radial load | 19.9 N stall / 10 N sustained | hub bearing in the journal | as stated | hours |

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
- [ ] Presses onto the N20 shaft firmly; set screw bites the flat
- [ ] Hub turns freely in the journal
- [ ] **Proof test:** Hold the track still and stall the motor at 80 % PWM for 3 s, 5 times. Pass: the sprocket doesn't slip on the shaft, no tooth cracks or shears, the hub still turns freely in the journal.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

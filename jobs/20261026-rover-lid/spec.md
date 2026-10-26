# Part spec: Rover lid / electronics deck

Job: 20261026-rover-lid · Written by: Architect · Date: 2026-10-26 · Assembly: [20261026-rover-assembly](../20261026-rover-assembly/assembly_plan.md)

## 1. Function
3 mm deck screwed onto the chassis columns, carrying the ESP32 DevKit (pins down through a window, PCB on end ledges, held by zip ties over its pin-free ends), a 170-point mini breadboard with the TB6612FNG driver and the 5 V buck, and a Ø10 cable hole.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 154 × 76 × 7.1 mm. Interfaces: 4 × Ø3.6 screw holes on the chassis columns (−13, ±30), (100, ±30); ESP32 seat 55.6 × 29.7 with ledges 2 mm above the deck; 6 tie slots 3.2 × 1.8 at the board ends; breadboard area 47 × 35; cable hole Ø10 at (76, 0).
- Fasteners used: 4 × M3 × 10 self-tapping into the chassis columns; 2 small zip ties for the ESP32 (across its USB end and its far end)

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| ESP32 pocket width | 29.7 | +0.3/−0 | 0.6 clearance |
| Screw holes | Ø3.4 | +0.2/−0 | M3 clearance |

Motor, battery-holder and sensor sizes are nominal (tools/hobby_parts.py: N20_100RPM, BATT_2X18650, HCSR04). Measure your N20 (gearbox 12 × 10 × 9, can Ø12 with 10 mm flats, shaft Ø3 with a 2.5 mm D-flat, 10 mm long from the gearbox face) and your 2 × 18650 holder (77 × 41 × 21) before printing, and give Claude any difference over 0.3 mm. Track pins are **2 mm steel rod** (silver steel, drill rod or piano wire), cut 23.5 mm and deburred.

## 4. Loads
Design loads (strength round 1 re-derived them; see the strength.md files): N20 stall ≈160 N·mm at the 7.4 V pack → ≈10 N of sprocket pull per side at the 16.18 mm pitch radius, 14.9 N in the tight run with a 5 N pretension (sustained); rover ≈0.58 kg (5.7 N); skid-steer drag 3 N per track. **Drop: 5 cm onto a hard floor** (the design limit; strength round 1 showed the printed pins and hubs can't survive a 30 cm desk fall): 5 mm stopping distance → 20 g peak → ≈14 N per axle flat, ≈29 N per axle on a corner, short-term.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Hand pressure on the deck | 20 N at mid-span | plate bending | short-term | seconds |
| USB plug / jumper pull | 10 N at the ESP32 seat | ledges, rails, ties | short-term | seconds |
| Drop (5 cm) | electronics ≈40 g × 20 g | seat ledges, screw holes | short-term | seconds |

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
- Max acceptable print time per batch (h): 5

## 8. Acceptance criteria (measurable)
- [ ] ESP32 (38- or 30-pin) seats on both ledges with jumpers on every pin
- [ ] Lid screws line up with the chassis columns
- [ ] **Proof test:** Lid screwed on: press 20 N (2 kg) at the deck centre for 1 min, and plug/unplug USB 5 times. Pass: no cracks at the seat, rails, tie slots or screw holes; the board stays on both ledges.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

# Part spec: Rover lid / electronics deck

Job: 20261026-rover-lid · Written by: Architect · Date: 2026-10-26 · Assembly: [20261026-rover-assembly](../20261026-rover-assembly/assembly_plan.md)

## 1. Function
3 mm deck screwed onto the chassis columns, carrying the ESP32 DevKit (pins down through a window, PCB on end ledges, zip tie), a 170-point mini breadboard with the TB6612FNG driver and the 5 V buck, and a Ø10 cable hole.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 154 × 76 × 7.1 mm. Interfaces: 4 × Ø3.6 screw holes on the chassis columns; ESP32 seat 55.6 × 29.7 with ledges 2 mm above the deck; breadboard area 47 × 35 at x 84–131.
- Fasteners used: 4 × M3×10 self-tapping into the chassis columns; 1 zip tie for the ESP32

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| ESP32 pocket width | 29.7 | +0.3/−0 | 0.6 clearance |
| Screw holes | Ø3.4 | +0.2/−0 | M3 clearance |

Motor, battery-holder and sensor sizes are nominal (tools/hobby_parts.py: N20_100RPM, BATT_2X18650, HCSR04). Measure your N20 (gearbox 12 × 10, face screw spacing 9, shaft Ø3 with D-flat 2.5, shaft length 10 from the face) and your 2 × 18650 holder (77 × 41 × 21) before printing; give Claude any difference over 0.3 mm. Track pins are 1.75 mm filament (PLA or PETG), cut 25 mm long.

## 4. Loads
Design loads: N20 stall ≈130 N·mm at 6 V (≈160 N·mm at the 7.4 V pack) → up to **10 N of track pull per side** at the 16.2 mm sprocket pitch radius; rover mass ≈0.5 kg (4.9 N); skid-steer turning drags the tracks sideways (μ ≈ 0.6 → ≈3 N per track); a **30 cm drop** off a desk is taken as 5 × weight on one track (≈25 N), short-term.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Hand pressure on the deck | 20 N at mid-span | plate bending | short-term | seconds |
| USB plug / jumper pull | 10 N at the ESP32 seat | ledges, rails | short-term | seconds |

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
- [ ] **Proof test:** Lid screwed on: press 20 N (2 kg) at the deck centre for 1 min, and plug/unplug USB 5 times. Pass: no cracks at the seat, rails or screw holes; the board stays on both ledges.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

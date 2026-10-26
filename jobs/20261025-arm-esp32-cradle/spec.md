# Part spec: ESP32 cradle

Job: 20261025-arm-esp32-cradle · Written by: Architect · Date: 2026-10-25 · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Open frame that hangs under the base top plate on 3 bosses and holds an ESP32 DevKit (38-pin or 30-pin) pins-down, USB at the base's +X slot, so female jumpers fit every pin.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 64 × 42 × 6 mm. Interfaces: 3 × Ø3.4 holes matching the base cradle pilots; PCB pocket 55.6 × 29.5 with end ledges at PCB-bottom height (Z −11.6).
- Fasteners used: 3 × M3×8 self-tapping into the base bosses

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| PCB pocket width | 29.5 | +0.3/−0 | 0.6 clearance around a 28.3 board |
| Ledge height | Z −11.6 | ±0.2 | lines the USB up with the slot |

Servo dimensions are nominal (tools/hobby_parts.py). Measure your servos and horns first (body length/width, tab-hole spacing, shaft-to-end distance, double-arm horn hub Ø, arm length and tip width) and put any differences into `replace(MG996R, ...)` / `replace(SG90, ...)` in model.py. An optional fit coupon can be printed first.

## 4. Loads
Design loads come from the servos' datasheet stall torques (MG996R 1000 N·mm, SG90 160 N·mm at 6 V), because a stalled servo is the worst case the part sees, plus the arm's own weight with a 50 g payload.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| USB/jumper pull | 5 N | side wall / ledges | short-term | seconds |

## 5. Environment
- Max temperature the part will see (°C): 40 (indoor desk; servo cases reach ~45 °C under sustained stall, so do not stall the servos for minutes)
- Outdoor / UV: no
- Chemicals, oils, moisture: none

## 6. Material
- Preferred or required: PETG (Prusament PETG or equivalent), user left the choice to the designer
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA for the load-path parts (creeps under sustained servo-holding load); ABS/ASA (no enclosure needed for this job)

## 7. Quantity and time
- Quantity: 1
- Max acceptable print time per batch (h): 2

## 8. Acceptance criteria (measurable)
- [ ] Board drops in and sits on both ledges
- [ ] USB cable plugs in through the base slot
- [ ] **Proof test:** none needed (non-structural); check the board seats and the USB plug reaches it.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

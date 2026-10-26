# Part spec: Upper link (shoulder → elbow, 100 mm)

Job: 20261025-arm-upper-link · Written by: Architect · Date: 2026-10-25 · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Flat 6 mm plate on the shoulder servo's double-arm horn, carrying the elbow MG996R at 100 mm.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 146 × 34 × 6 mm. Interfaces: horn slot (back face) at x 0; elbow MG996R window at x 100 with 4 × Ø2.6 pilots; lightening slot.
- Fasteners used: Shoulder horn centre screw + 2 screws through the horn arms; elbow servo: 4 tab screws

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Shoulder–elbow axis distance | 100.0 | ±0.3 | kinematics |
| Horn slot | as turntable | +0.2/−0 | locating |
| Elbow window | 41.1 × 20.1 | +0.3/−0 | clearance |

Servo dimensions are nominal (tools/hobby_parts.py). Measure your servos and horns first (body length/width, tab-hole spacing, shaft-to-end distance, double-arm horn hub Ø, arm length and tip width) and put any differences into `replace(MG996R, ...)` / `replace(SG90, ...)` in model.py. An optional fit coupon can be printed first.

## 4. Loads
Design loads come from the servos' datasheet stall torques (MG996R 1000 N·mm, SG90 160 N·mm at 6 V), because a stalled servo is the worst case the part sees, plus the arm's own weight with a 50 g payload.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Shoulder stall through the horn slot | 1000 N·mm | slot walls in bearing; in-plane bending of the link | short-term | seconds |
| Distal weight + 50 g payload | ≈310 N·mm at the shoulder static, 620 N·mm dynamic | in-plane bending (34 mm deep section) | sustained | hours |
| Elbow stall reaction | 1000 N·mm | 4 tab screws into the plate | short-term | seconds |

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
- Max acceptable print time per batch (h): 5

## 8. Acceptance criteria (measurable)
- [ ] Elbow MG996R fits the window; tab screws bite
- [ ] Horn seats flat
- [ ] **Proof test:** Lock the shoulder horn in a vice (horn screwed in its slot), hang 1 kg at the elbow axis for 1 min: no cracking around the slot or lightening hole, deflection at the elbow < 2 mm, no permanent set.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

# Part spec: Gripper base with fixed jaw

Job: 20261025-arm-gripper-base · Written by: Architect · Date: 2026-10-25 · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
5 mm plate on the wrist SG90's single-arm horn; carries the gripper SG90 at x 40 and the fixed jaw (x 55–95, face at y −6).

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 104 × 25 × 19.4 mm. Interfaces: SG90 arm-horn pocket at x 0; SG90 window at x 40; fixed jaw block 40 × 8 × 14.4.
- Fasteners used: Wrist horn centre screw + 1 screw through the horn arm; gripper SG90: 2 tab screws

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Wrist–gripper axis distance | 40.0 | ±0.3 | jaw geometry |
| Fixed jaw face | y = −6.0 | ±0.3 | meets moving jaw |

Servo dimensions are nominal (tools/hobby_parts.py). Measure your servos and horns first (body length/width, tab-hole spacing, shaft-to-end distance, double-arm horn hub Ø, arm length and tip width) and put any differences into `replace(MG996R, ...)` / `replace(SG90, ...)` in model.py. An optional fit coupon can be printed first.

## 4. Loads
Design loads come from the servos' datasheet stall torques (MG996R 1000 N·mm, SG90 160 N·mm at 6 V), because a stalled servo is the worst case the part sees, plus the arm's own weight with a 50 g payload.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Wrist stall | 160 N·mm | horn pocket bearing | short-term | seconds |
| Grip reaction | 2.9 N at the fingertip, 55 mm from the gripper axis | fixed jaw block bending | short-term | seconds |

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
- Max acceptable print time per batch (h): 3

## 8. Acceptance criteria (measurable)
- [ ] Gripper SG90 fits; jaws close flat against each other
- [ ] **Proof test:** Squeeze the closed jaws with 10 N by hand for 1 min: no cracking at the jaw root.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

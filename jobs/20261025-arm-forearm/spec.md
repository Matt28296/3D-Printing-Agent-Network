# Part spec: Forearm (elbow → wrist, 90 mm)

Job: 20261025-arm-forearm · Written by: Architect · Date: 2026-10-25 · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Flat 5 mm plate on the elbow servo's double-arm horn, carrying the wrist SG90 at 90 mm.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 129 × 26 × 5 mm. Interfaces: MG996R horn slot at x 0; SG90 window 22.9 × 12.4 at x 90 with 2 Ø1.8 slotted pilots; lightening slot.
- Fasteners used: Elbow horn centre screw + 2 arm screws; wrist SG90: its 2 tab screws

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Elbow–wrist axis distance | 90.0 | ±0.3 | kinematics |
| SG90 window | 22.9 × 12.4 | +0.3/−0 | clearance |

Servo dimensions are nominal (tools/hobby_parts.py). Measure your servos and horns first (body length/width, tab-hole spacing, shaft-to-end distance, double-arm horn hub Ø, arm length and tip width) and put any differences into `replace(MG996R, ...)` / `replace(SG90, ...)` in model.py. An optional fit coupon can be printed first.

## 4. Loads
Design loads come from the servos' datasheet stall torques (MG996R 1000 N·mm, SG90 160 N·mm at 6 V), because a stalled servo is the worst case the part sees, plus the arm's own weight with a 50 g payload.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Elbow stall through the horn slot | 1000 N·mm | slot bearing + in-plane bending | short-term | seconds |
| Distal weight + payload | ≈140 N·mm static, 280 dynamic | in-plane bending | sustained | hours |

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
- Max acceptable print time per batch (h): 4

## 8. Acceptance criteria (measurable)
- [ ] SG90 fits the window; tab screws bite
- [ ] **Proof test:** Clamp at the elbow horn, hang 1 kg at the wrist axis (≈880 N·mm) for 1 min: no cracking, no permanent set.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

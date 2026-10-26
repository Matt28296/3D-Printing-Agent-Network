# Part spec: Forearm (elbow → wrist, 90 mm)

Job: 20261025-arm-forearm · Written by: Architect · Date: 2026-10-25 · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Flat 10 mm plate on the elbow servo's double-arm horn, carrying the wrist SG90 at 90 mm.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 129 × 26 × 10 mm. Interfaces: MG996R horn slot with Ø3.4 clamp hole at x 0; SG90 window 22.7 × 12.4 (printed) at x 90 with 2 Ø1.5 slotted pilots.
- Fasteners used: Elbow horn: M3×16 centre screw + Ø9 washer from the front face + 2 arm screws; wrist SG90: its 2 tab screws

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Elbow–wrist axis distance | 90.0 | ±0.3 | kinematics |
| SG90 window | 22.7 × 12.4 | +0.3/−0 | clearance 0.1/side at the ends |
| SG90 pilot-to-window wall | 1.8 printed | min | 4 perimeters |

Servo dimensions are nominal (tools/hobby_parts.py). Measure your servos and horns first (body length/width, tab-hole spacing, shaft-to-end distance, double-arm horn hub Ø, arm length and tip width) and put any differences into `replace(MG996R, ...)` / `replace(SG90, ...)` in model.py. An optional fit coupon can be printed first.

## 4. Loads
Design loads come from the servos' datasheet stall torques (MG996R 1000 N·mm, SG90 160 N·mm at 6 V), because a stalled servo is the worst case the part sees, plus the arm's own weight with a 50 g payload. Round 2 adds the out-of-plane cases found by the strength review: the pitch servos give no resistance sideways, so a **base-yaw stall into a side obstacle** (swept over the joint ranges, up to 12 N at the fingertip) and a **5 N sideways hand push at the fingertip** load the printed plates and horn joints directly.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Elbow stall through the horn slot | 1000 N·mm | slot bearing + in-plane bending | short-term | seconds |
| Distal weight + payload | ≈160 N·mm static, 320 dynamic | in-plane bending | sustained | hours |
| Base-yaw stall / 5 N sideways hand push | at the horn ≈1480 N·mm out of plane + ≈960 N·mm torsion | plate out-of-plane bending, torsion, horn clamp, wrist tab screws | short-term | seconds |

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
- [ ] SG90 fits the window (measure it first: ends have only 0.1 mm clearance each); tab screws bite
- [ ] **Proof test:** (1) Clamp at the elbow horn, 1 kg at the wrist axis for 1 min: no cracks, no set. (2) Same clamping, 15 N sideways (out of plane) at the wrist axis for 1 min each way, then 7.5 N sideways at the end of a 95 mm lever on the wrist tab holes. Pass: no cracks at the pocket or the SG90 pilots, no lift off the horn, no permanent set.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

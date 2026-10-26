# Part spec: Turntable support ring

Job: 20261025-arm-turntable-ring · Written by: Architect · Date: 2026-10-25 · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Ring (r 41–44, 15 mm tall) screwed to the base top plate under the turntable. A 1.5 mm running gap means it only touches when the arm tips, so the base servo's output bearing is not the only thing resisting a knock.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: Ø88 ring + 3 tabs at r47.5, 15 mm tall. Interfaces: 3 × Ø3.4 tab holes matching the base's ring pilots; top face 1.5 mm below the turntable underside (Z 16.5).
- Fasteners used: 3 × M3×6 self-tapping into the base (3 mm tab + 3 mm into the 4 mm plate; a longer screw would reach the ESP32 under the plate)

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Ring height | 15.0 | ±0.2 | 1.5 mm running gap to turntable |
| Tab holes | Ø3.4 at r47.5 | ±0.2 | M3 clearance |

Servo dimensions are nominal (tools/hobby_parts.py). Measure your servos and horns first (body length/width, tab-hole spacing, shaft-to-end distance, double-arm horn hub Ø, arm length and tip width) and put any differences into `replace(MG996R, ...)` / `replace(SG90, ...)` in model.py. An optional fit coupon can be printed first.

## 4. Loads
Design loads come from the servos' datasheet stall torques (MG996R 1000 N·mm, SG90 160 N·mm at 6 V), because a stalled servo is the worst case the part sees, plus the arm's own weight with a 50 g payload. Round 2 adds the out-of-plane cases found by the strength review: the pitch servos give no resistance sideways, so a **base-yaw stall into a side obstacle** (swept over the joint ranges, up to 12 N at the fingertip) and a **5 N sideways hand push at the fingertip** load the printed plates and horn joints directly.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Knock on the arm | 20 N at the turntable rim | compression in the ring wall, shear in tab screws | short-term | seconds |
| Yaw-stall ring catch | ≈52 N | ring wall and tab screw heads | short-term | seconds |

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
- [ ] Turntable turns freely through ±90° with no rubbing (sand the ring top if it rubs)
- [ ] **Proof test:** Covered by the base proof test (50 N on the turntable rim, 1 min at each of 4 positions 90° apart). Pass: no cracks in the tabs or the ring wall, no crushing of the ring top (the 1.5 mm running gap still clears), and the turntable then turns freely through ±90° with no rubbing.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

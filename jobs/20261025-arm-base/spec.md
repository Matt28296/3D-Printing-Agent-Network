# Part spec: Robot arm base

Job: 20261025-arm-base · Written by: Architect · Date: 2026-10-25 · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Open-bottom box (110 × 104 × 40 mm) that holds the base-yaw MG996R (hanging through its top plate), the turntable support ring, the ESP32 cradle, the 5.5 × 2.1 mm DC panel jack and the USB access slot. Screws to the desk or sits on rubber feet.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 110 × 104 × 40 mm. Interfaces: MG996R window 41.1 × 20.1 mm with 4 × Ø2.6 pilots (48.5 × 10 mm pattern) through 4 mm plate + 6 mm bosses; 3 × Ø2.6 ring pilots at r47.5 (30°, 150°, 270°); 3 × Ø2.6 cradle pilots on Ø7 bosses; DC jack Ø11.4 teardrop; USB slot 13 × 7; cable slot 14 × 8 at (−40, −36); 4 × Ø3.4 desk holes in corner pillars.
- Fasteners used: 4 × MG996R tab screws (from the servo bag) self-tapping into Ø2.6 pilots; 3 × M3×6 self-tapping for the ring; 3 × M3×12 for the cradle (from below, heads in counterbores); 4 × M3×50 (or #4 × 2") wood screws to the desk or a board: REQUIRED, the arm tips the base over with the arm out (strength round 1)

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Servo window | 41.1 × 20.1 | +0.3/−0 | clearance 0.2/side |
| Servo pilot holes | Ø2.6 | ±0.1 | self-tap M3/servo screw |
| Servo pilot pattern | 48.5 × 10.0 | ±0.2 | matches MG996R tabs |
| DC jack hole | Ø11.4 | +0.3/−0 | panel jack Ø11 thread |
| Overall | 110 × 104 × 40 | ±0.5 | free |

Servo dimensions are nominal (tools/hobby_parts.py). Measure your servos and horns first (body length/width, tab-hole spacing, shaft-to-end distance, double-arm horn hub Ø, arm length and tip width) and put any differences into `replace(MG996R, ...)` / `replace(SG90, ...)` in model.py. An optional fit coupon can be printed first.

## 4. Loads
Design loads come from the servos' datasheet stall torques (MG996R 1000 N·mm, SG90 160 N·mm at 6 V), because a stalled servo is the worst case the part sees, plus the arm's own weight with a 50 g payload. Round 2 adds the out-of-plane cases found by the strength review: the pitch servos give no resistance sideways, so a **base-yaw stall into a side obstacle** (swept over the joint ranges, up to 12 N at the fingertip) and a **5 N sideways hand push at the fingertip** load the printed plates and horn joints directly.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Base-servo stall reaction | 1000 N·mm about Z | 4 tab screws into the top plate | short-term | seconds |
| Arm tipping moment | 600 N·mm (2 × static 300) | servo tabs and ring tabs into top plate | sustained while powered | hours |
| Hand push on the arm | 20 N at the turntable rim | ring → 3 ring screws → top plate | short-term | seconds |
| Yaw-stall ring catch | ≈52 N at the ring | ring → 3 ring screws → top plate | short-term | seconds |
| Tipping with the arm out (static) | 358 N·mm about the base edge vs 147 N·mm restoring | desk screws in tension | sustained | hours |

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
- Max acceptable print time per batch (h): 10

## 8. Acceptance criteria (measurable)
- [ ] MG996R drops into the window without force and its tab screws bite in all 4 pilots
- [ ] DC jack nut tightens on the panel jack through the wall
- [ ] ESP32 USB plug reaches the board through the slot with the cradle fitted
- [ ] **Proof test:** With the base screwed to a board (desk screws fitted), the base servo, horn, turntable and ring assembled and the servo unpowered, press 50 N (≈5 kg on a bathroom or luggage scale) straight down on the turntable rim, 1 min at each of 4 positions 90° apart. Pass: no cracking or whitening at the 4 servo pilots and bosses, the 3 ring pilots or the top plate around the ring; after unloading, the rim returns to within 0.3 mm of its height. Also plug and unplug the USB cable 5 times with the cradle fitted: no cracks at the cradle bosses.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

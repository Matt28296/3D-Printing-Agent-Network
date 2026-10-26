# Part spec: Robot arm base

Job: 20261025-arm-base · Written by: Architect · Date: 2026-10-25 (round 3: 2026-10-26, deep reviews 01 B1/S3/S8 and 03 SYS-05/SYS-09/SYS-12) · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Open-bottom box (110 × 104 × 40 mm) that holds the base-yaw MG996R (hanging through its top plate), the turntable support ring, the ESP32 cradle, the power bus, the 5.5 × 2.1 mm DC panel jack and the USB access slot. It is built and wired upside down on the bench, then screwed to the desk or to a board last (deep review 03 SYS-09).

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 110 × 104 × 40 mm. Interfaces: MG996R window 41.1 × 20.1 mm (printed) with a lead notch 4.4 × 2.0 mm (printed) at each case end through the 4 mm top plate only (deep review 01 B1: below the plate the ribbon passes between the bosses, ≥ 3 mm off the centreline at the case end) and 4 × Ø2.6 pilots (48.5 × 10 mm pattern) through the 4 mm plate + 6 mm bosses; 3 × Ø2.6 ring pilots at r47.5 (30°, 150°, 270°); 3 × Ø2.6 cradle pilots on Ø7 bosses; DC jack Ø11.4 teardrop; USB slot 13 × 7; cable slot 14 × 8 at (−40, −36); 4 × Ø3.4 desk holes in corner pillars.
- Fasteners used: base servo: 4 × M3 × 12 pan-head self-tapping + Ø7 washers, the grommets and eyelets left out (01 S3: 9 mm engaged in plate + boss); 3 × M3 × 6 self-tapping for the ring; 3 × M3 × 10 for the cradle (from below, heads in counterbores: 4 mm clamp + 6 mm into the boss pilots); 4 × M3 × 50 (or #4 × 2") wood screws to the desk or a board: REQUIRED, the arm tips the base over with the arm out (strength round 1; SYS-12: or a 200 × 200 mm, 0.4 kg board, or 1.2 kg of ballast inside)

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Servo window | 41.1 × 20.1 | +0.3/−0 | clearance 0.2/side |
| Lead notches | 4.4 wide, 2.0 beyond each case end (printed), through the 4 mm plate | +0.2/−0 | 4 × 1.3 mm lead ribbon; 2.0 mm printed ligament to the nearest pilot |
| Servo pilot holes | Ø2.6 | ±0.1 | M3 × 12 self-tapping (ST2.9) |
| Servo pilot pattern | 48.5 × 10.0 | ±0.2 | matches MG996R tabs |
| DC jack hole | Ø11.4 | +0.3/−0 | panel jack Ø11 thread |
| Overall | 110 × 104 × 40 | ±0.5 | free |

Servo dimensions are nominal (tools/hobby_parts.py). Measure your servos and horns first (body length/width, tab-hole spacing, shaft-to-end distance, the lead exit, the disc horn) and put any differences into `replace(MG996R, ...)` in model.py.

## 4. Loads
Design loads come from the servos' datasheet stall torques (MG996R 1000 N·mm, MG90S 216 N·mm at 6 V), because a stalled servo is the worst case the part sees, plus the arm's own weight with a 50 g payload. The out-of-plane cases: a **base-yaw stall into a side obstacle** (up to 12 N at the fingertip) and a **5 N sideways hand push at the fingertip**. Round 3: the round-3 claw and camera (`../20261025-robot-arm-assembly/torque_budget.json`, solid parts); the turntable now sits on a Ø25 disc horn and the support ring runs 0.4 mm under it (PTFE tape), so the ring shares the arm's overturning moment after 0.5° of tilt (deep review 03 SYS-05).

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Base-servo stall reaction | 1000 N·mm about Z | 4 tab screws into the top plate | short-term | seconds |
| Moment of everything on the turntable (SYS-05) | 692 N·mm, arm straight out with the camera (832 with 50 g), ×2 dynamic; 245–286 N·mm of it in every pose | servo tabs → plate and bosses; ring → 3 ring screws → top plate | sustained while powered | hours |
| Hand push on the arm | 20 N at the turntable rim | ring → 3 ring screws → top plate | short-term | seconds |
| Yaw-stall ring catch | ≈52 N at the ring | ring → 3 ring screws → top plate | short-term | seconds |
| Tipping with the arm out (SYS-12) | robot 0.70–0.75 kg, centre of mass 85–98 mm out against the 55 mm edge: 400–510 N·mm overturning vs 190 N·mm restoring | desk screws in tension (≈3 N per pair, static) | sustained | hours |

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
- [ ] MG996R goes into the window from above, case bottom first, with its lead ribbon through an end notch, without force; its tab screws bite in all 4 pilots
- [ ] DC jack nut tightens on the panel jack through the wall
- [ ] ESP32 USB plug reaches the board through the slot with the cradle fitted
- [ ] **Proof test (links strength round 4, at the 1079 N·mm datasheet stall):** (1) Run the turntable's arm-up test with this base screwed down and the ring fitted (servos powered, arm pointing straight up, 11.5 N ≈1.2 kg sideways at the fingertips, 1 min each way). Pass: no cracking or whitening in the top plate round the four servo tab bosses, the lead notches or the window corners, and the servo doesn't shift in its window. (2) Servo unpowered, press 77 N (≈8 kg on a bathroom or luggage scale) straight down on the turntable rim, 1 min at each of 4 positions 90° apart. Pass: no cracking or whitening at the 4 servo pilots and bosses, the 3 ring pilots or the top plate round the ring; after unloading, the rim returns to within 0.3 mm of its height and the running gap still clears. (3) Plug and unplug the USB cable 5 times with the cradle fitted: no cracks at the cradle bosses.
## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

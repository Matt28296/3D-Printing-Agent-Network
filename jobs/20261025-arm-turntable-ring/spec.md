# Part spec: Turntable support ring

Job: 20261025-arm-turntable-ring · Written by: Architect · Date: 2026-10-25 (round 3: 2026-10-26, deep review 03 SYS-05) · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Ring (r 41–44, 16.1 mm tall) screwed to the base top plate under the turntable. Round 3 (deep review 03 SYS-05): the running gap is 0.4 mm (was 1.5) with a layer of PTFE tape on the top face, so the ring works as a bearing: it catches the disk after 0.5° of tilt (was 1.95°, a 9.3 mm drop at full reach) and shares the arm's overturning moment with the base servo's output bearings, the disc horn and the clamp screw.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: Ø88 ring + 3 tabs at r47.5, 16.1 mm tall. Interfaces: 3 × Ø3.4 tab holes matching the base's ring pilots; top face 0.4 mm below the turntable underside (Z 16.5), ≈0.3 mm with the PTFE tape.
- Fasteners used: 3 × M3 × 6 self-tapping into the base (3 mm tab + 3 mm into the 4 mm plate; a longer screw would reach the ESP32 under the plate)

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Ring height | 16.1 | ±0.15 | 0.4 mm running gap to the turntable (0.3 with tape); sand the top to an even gap |
| Tab holes | Ø3.4 at r47.5 | ±0.2 | M3 clearance |

Servo dimensions are nominal (tools/hobby_parts.py): the turntable underside sits at the MG996R horn face, 16.5 mm above the top plate. Measure your servo with its disc horn pressed home (top plate to horn face) before printing, and give Claude any difference over 0.1 mm: it sets this gap.

## 4. Loads
Design loads come from the servos' datasheet stall torques (MG996R 1000 N·mm, MG90S 216 N·mm at 6 V), plus the arm's own weight with a 50 g payload, the base-yaw stall into a side obstacle (up to 12 N at the fingertip) and a 5 N sideways hand push. Round 3: the ring now carries part of the arm's overturning moment in normal use (`../20261025-robot-arm-assembly/torque_budget.json`, round-3 claw, solid parts).

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Overturning moment on the turntable (SYS-05) | up to 832 N·mm (arm straight out, camera, 50 g) → ≈19 N on the ring's top at r 44 if the ring takes all of it, ×2 dynamic | ring wall in compression, PTFE sliding contact, 3 tab screws | sustained while the arm is out | hours |
| Knock on the arm | 20 N at the turntable rim | compression in the ring wall, shear in tab screws | short-term | seconds |
| Yaw-stall ring catch | ≈52 N | ring wall and tab screw heads | short-term | seconds |
| Friction torque while yawing | μ 0.1 (PTFE) × ≈19 N × 44 mm ≈ 85 N·mm | against the yaw servo's 1000 N·mm, which carries no gravity load | cyclic | hours |

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
- [ ] With the PTFE tape on, the turntable runs 0.3–0.4 mm above the ring all round (feeler gauge at 8 points) and turns freely through ±90° (sand the ring top where it rubs)
- [ ] With the arm straight out, the disk rests on the ring at the far side and the arm still yaws smoothly at `b` commands
- [ ] **Proof test (links strength round 4, at the 1079 N·mm datasheet stall):** Covered by the base proof test (77 N, ≈8 kg, straight down on the turntable rim, 1 min at each of 4 positions 90° apart, servo unpowered). Pass: no cracks in the tabs or the ring wall, no crushing of the ring top (the running gap still clears), the washers still tight under the screw heads, and the turntable then turns freely through ±90° with no rubbing.
## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

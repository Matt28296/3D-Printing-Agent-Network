# Part spec: Upper link (shoulder → elbow, 100 mm)

Job: 20261025-arm-upper-link · Written by: Architect · Date: 2026-10-25 (round 3: 2026-10-26, deep reviews 01 B1/S2/S3/S4 and 03 SYS-04) · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Flat 10 mm plate on the shoulder servo's double-arm horn, carrying the elbow MG996R at 100 mm.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 146 × 34 × 10 mm. Interfaces: horn slot (back face, 2 deep) with Ø3.6 CAD clamp hole at x 0 (8 mm floor); elbow MG996R window at x 100 (41.1 × 20.1 printed) with a lead notch 4.4 × 2.0 (printed) at each case end (deep review 01 B1) and 4 × Ø2.6 pilots.
- Fasteners used: Shoulder horn: M3 × 14 + Ø9 × 0.8 washer from the front face (clamps link + horn onto the spline: 14 − 0.8 − 8 − 0.6 = 4.6 mm into it, 01 S2) + 2 × M2 × 6 self-tappers through the horn's arm holes (01 S4); elbow servo: 4 × M3 × 12 pan-head self-tapping + Ø7 washers, 9 mm engaged (01 S3), the servo going in from the front face, case bottom first, its lead through a notch

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Shoulder–elbow axis distance | 100.0 | ±0.3 | kinematics |
| Horn slot | as turntable | +0.2/−0 | locating |
| Elbow window | 41.1 × 20.1 printed | +0.3/−0 | clearance |
| Lead notches | 4.4 wide, 2.0 beyond each case end (printed) | +0.2/−0 | 4 × 1.3 mm lead ribbon; 2.0 mm printed ligament to the nearest pilot |

Servo dimensions are nominal (tools/hobby_parts.py). Measure your servos and horns first (body length/width, tab-hole spacing, shaft-to-end distance, the lead exit, double-arm horn hub Ø, arm length and tip width) and put any differences into `replace(MG996R, ...)` in model.py.

## 4. Loads
Design loads come from the servos' datasheet stall torques (MG996R 1000 N·mm, MG90S 216 N·mm at 6 V), because a stalled servo is the worst case the part sees, plus the arm's own weight with a 50 g payload. The out-of-plane cases: the pitch servos give no resistance sideways, so a **base-yaw stall into a side obstacle** (swept over the joint ranges, up to 12 N at the fingertip) and a **5 N sideways hand push at the fingertip** load the printed plates and horn joints directly. Round 3: masses of the round-3 claw (heavier, ≈224 g beyond the wrist horn with the camera, solid parts) from `../20261025-robot-arm-assembly/torque_budget.json`; and the camera's sideways weight (deep review 03 SYS-04), which bends every pitch joint across its shaft in every pose.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Shoulder stall through the horn slot | 1000 N·mm | slot walls in bearing; in-plane bending of the link | short-term | seconds |
| Distal weight + 50 g payload | ≈740 N·mm at the shoulder static (arm straight out, camera, solid parts; the 1000 N·mm stall caps it) | in-plane bending (34 mm deep section) | sustained | hours |
| Camera + distal weight across the shoulder shaft (SYS-04) | 239 N·mm (278 with 50 g) about the shoulder servo's case-top plane | horn clamp preload, plate round the pocket | sustained (every pose) | hours |
| Elbow servo's sideways moment (SYS-04) | 161 N·mm (188 with 50 g) about the elbow servo's case-top plane | 4 tab screws, plate round the window | sustained (every pose) | hours |
| Elbow stall reaction | 1000 N·mm | 4 tab screws into the plate | short-term | seconds |
| Base-yaw stall / 5 N sideways hand push | at the horn ≈1400 N·mm out of plane + ≈930 N·mm torsion | plate out-of-plane bending, torsion, horn clamp | short-term | seconds |

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
- [ ] Elbow MG996R goes into the window from the front face, case bottom first, with its lead through an end notch; tab screws bite
- [ ] Horn seats flat
- [ ] **Proof test:** (1) Shoulder horn in a vice (horn clamped in its slot), 1 kg at the elbow axis for 1 min: deflection at the elbow < 2 mm, no permanent set. (2) Same clamping, 21 N (≈2.1 kg) sideways (out of the link plane) at the elbow axis for 1 min each way, then 7.5 N sideways at the end of a 185 mm lever bolted to the elbow tab holes. Pass: no cracks at the pocket, no lift of the link off the horn, no permanent set.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

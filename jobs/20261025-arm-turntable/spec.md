# Part spec: Turntable with shoulder upright

Job: 20261025-arm-turntable · Written by: Architect · Date: 2026-10-25 (round 3: 2026-10-26, deep reviews 01 B1/S2/S3 and 03 SYS-04/SYS-05/SYS-09/SYS-16) · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Ø96 × 8 mm disk whose flat underside sits on the base servo's round Ø25 disc horn (no pocket, so no bridge; deep review 03 SYS-05: the disc supports the disk ±12.5 mm in every direction, where the double-arm horn supported it only on its Ø11 hub across the arms), with a 66 × 7 mm upright, root wedges and two 70 mm gussets that hold the shoulder MG996R horizontally (shaft +Y, axis at X 10.15, Z 60.5). The support ring (0.4 mm below the disk, PTFE tape) catches the disk after 0.5° of tilt.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 96 × 96 × 80.8 mm. Interfaces: Ø3.6 CAD (3.4 printed) clamp-screw hole on the yaw axis; shoulder MG996R window 41.1 × 20.1 (printed) with a 45° roof, lead notches 4.4 × 2.0 (printed) at both case ends with 45° tops (deep review 01 B1: the notch is a hole in a standing wall), 4 × Ø2.6 horizontal teardrop pilots. The upright's front face (+Y) is where the shoulder shaft comes out: it faces +Y when the base servo is centred.
- Fasteners used: Base horn: M3 × 14 socket head (ISO 4762, re-tightened with an L-key past the upright: SYS-16) + Ø9 × 0.8 washer from the top through the 8 mm disk into the spline: 14 − 0.8 − 8 − 0.6 = 4.6 mm engaged (01 S2), plus 2 × M2 × 6 self-tappers through two of the disc horn's holes into the disk; shoulder servo: 4 × M3 × 12 pan-head self-tapping + Ø7 washers (01 S3; 7 mm engaged, the tips stand 2 mm out of the back face at X ±24.25, clear of the gussets at |X| ≥ 28.5). Drive the centre screw BEFORE fitting the shoulder servo (the servo body covers the hole).

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Clamp hole | Ø3.4 printed | +0.2/−0 | M3 clearance |
| Shoulder window | 41.1 × 20.1 printed | +0.3/−0 | clearance 0.2/side |
| Lead notches | 4.4 wide, 2.0 beyond each case end (printed), 45° top | +0.2/−0 | 4 × 1.3 mm lead ribbon; 2.0 mm printed ligament to the nearest pilot |
| Shoulder axis | X 10.15, Z 60.5 (assembly frame) | ±0.3 | position |
| Disk underside | Z 16.5 | ±0.2 | 0.4 mm over the support ring |

Servo dimensions are nominal (tools/hobby_parts.py). Measure your servos and horns first (body length/width, tab-hole spacing, shaft-to-end distance, the lead exit, the disc horn's Ø and hole circle) and put any differences into `replace(MG996R, ...)` in model.py.

## 4. Loads
Design loads come from the servos' datasheet stall torques (MG996R 1000 N·mm, MG90S 216 N·mm at 6 V), because a stalled servo is the worst case the part sees, plus the arm's own weight with a 50 g payload. The out-of-plane cases: the pitch servos give no resistance sideways, so a **base-yaw stall into a side obstacle** (swept over the joint ranges, up to 12 N at the fingertip) and a **5 N sideways hand push at the fingertip** load the printed plates and horn joints directly. Round 3 (deep review 03 SYS-04): every link mounts on the front of the previous servo, so the arm and the camera hang outboard of the upright, and their weight bends it about X **in every pose**. Masses from `../20261025-robot-arm-assembly/torque_budget.json` (round-3 claw, solid parts: the upper bound).

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Shoulder servo stall reaction | 1000 N·mm about Y | 4 tab screws → upright (in its plane) | short-term | seconds |
| Base servo stall | 1000 N·mm about Z | disc horn → 2 M2 screws and the clamp's friction | short-term | seconds |
| Arm + camera weight out of the upright's plane (SYS-04) | 290 N·mm about X with the camera (335 with 50 g); 172 / 217 without it; about the upright's mid-plane (Y −8.5), ×2 dynamic | upright root + gussets | sustained (every pose) | hours |
| Everything on the turntable, on the base horn (SYS-05) | arm straight out with the camera: 692 N·mm (832 with 50 g), 245–286 of it about X from the sideways offset in every pose; axial 5.6–6.1 N | disk on the Ø25 disc horn, clamp screw; the ring takes over after 0.5° of tilt | sustained | hours |
| Base-yaw stall / 5 N sideways hand push at the fingertip | up to 12 N at the fingertip, ≈300 mm lever | upright out of plane, base-horn joint | short-term | seconds |

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
- Max acceptable print time per batch (h): 8

## 8. Acceptance criteria (measurable)
- [ ] Shoulder MG996R goes into the window from the front, case bottom first, with its lead through an end notch, and all 4 tab screws bite
- [ ] The disc horn sits flat on the disk's underside; the disk turns 0.3–0.4 mm above the taped support ring all round
- [ ] **Proof test (links strength round 4, at the 1079 N·mm datasheet stall):** (1) Base screwed down, ring fitted, arm assembled, servos powered, base servo centred, arm pointing straight up (upper link, forearm and claw in one vertical line). Push 11.5 N (≈1.2 kg on a luggage scale) sideways at the fingertips, square to the arm's plane (±Y), 1 min each way. Pass: no cracks or whitening at the upright's window corners, the tab pilots and lead notches, the gusset toes or the upright–disk corner; the disk doesn't lift off the disc horn; the fingertips come back to within 1 mm. (2) Disc-horn check: servos powered, base centred; mark the disk rim against the base. Push tangentially on the rim with the luggage scale up to 34 N (≈3.5 kg), or until the base servo gives way, 5 times each way. Pass: back at the same command the marks line up again within 1 mm (nothing slipped at the disc horn); when the turntable is next off, no cracks or elongated holes at the anti-rotation screws.
## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

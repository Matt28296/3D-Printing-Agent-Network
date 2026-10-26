# System spec: Desktop robot arm (4 joints + parallel claw, optional wrist camera)

Job: 20261025-robot-arm-assembly · Written by: Architect · Date: 2026-10-25 (system spec written 2026-10-26, round 3, deep review 03 SYS-18) · Parts: [assembly_plan.md](assembly_plan.md) · Build: [BUILD_GUIDE.md](BUILD_GUIDE.md)

## 1. Function
A desktop pick-and-place arm for small objects: base yaw, shoulder, elbow and wrist pitch, and a rack-and-pinion parallel claw, on hobby servos (3 × MG996R, 2 × MG90S) driven by an ESP32 that takes serial commands from a PC. An optional Logitech Brio 4K on the claw gives the PC an eye-in-hand view for vision. Printed in PETG on the MK3S; every printed part is its own job (assembly_plan.md, "Printed pieces").

## 2. Envelope and interfaces
- Footprint: the 110 × 104 × 40 mm base, screwed to the desk (4 × M3 × 50 wood screws) or to a board ≥ 200 × 200 mm, ≥ 0.4 kg. Keep-out: the claw and camera sweep a circle of ≈300 mm radius round the yaw axis; behind the base (−X, jack and cable slot) the arm reaches the desk with the shoulder past 90°.
- Power: 6 V 5 A adapter, 5.5 × 2.1 mm centre-positive, through an inline switch (the e-stop) and a 5 A fuse to a stripboard bus in the base. The ESP32 runs from its USB port only.
- Data: ESP32 USB (serial commands, `arm_test/arm_test.ino`); Brio USB-C → PC.
- Frames, joint conventions and every link's interface: assembly_plan.md ("Shared frame") and `claw_frame.py`.

## 3. Critical dimensions and tolerances
| Feature | Nominal | Tolerance | Why |
|---|---|---|---|
| Shoulder axis above the desk | 100.5 mm | ±1 | kinematics, guard |
| Link lengths shoulder→elbow / elbow→wrist / wrist→fingertip | 100 / 90 / 83 mm | ±0.5 | kinematics |
| Arm plane offset (fingertips) | Y ≈ 84 mm at yaw 0 | ±1 | yaw targets, PC kinematics |
| Joint windows (joint angles, sketch commands) | shoulder 0…180°, elbow −150…+30°, wrist −90…+90°, claw 0…44 mm | trims ±7° (MG996R) / ±9° (MG90S) | servo 0–180° each; elbow horn fitted at servo 90 = −60° |
| Claw stroke | 0–44 mm in 126° of servo (2.865°/mm) | ±1 mm at 40 mm (claw scale, §5) | 20-tooth, module-1 pinion |
| Claw backlash | 0.35 mm per mesh (pitch-circle arc) | 0.3–0.4 | 03 SYS-08 |

## 4. Loads
Servo stall torques at 6 V: MG996R 1079 N·mm (11 kgf·cm; the part specs use 1000 as their design value), MG90S 216 N·mm. Masses: `torque_budget.json` (round-3 claw). End effector beyond the wrist horn: ≈209 g with the camera, ≈124 g without (sliced estimate; 224 / 140 g solid). Payload sits 10 mm behind the fingertips. Rating criteria (TowerPro gives no continuous rating): ≤ 50 % of stall for short holds, ×1.3 while moving, ≤ ⅓ of stall for continuous holding.

| Case | Value | Where it acts |
|---|---|---|
| Shoulder, arm straight out, camera, 0 / 50 g | 615 / 744 N·mm (57 / 69 % of stall; claw round 3 + links round 5, sliced masses; 63 % solid) | shoulder servo; why the arm parks upright |
| Shoulder, arm straight out, no camera, 0 / 50 g | 391 / 520 N·mm (36 / 48 %) | |
| Elbow / wrist, worst in the travel, camera, 50 g | 314 N·mm (29 %) / 63 N·mm (29 %) | |
| Camera's sideways moment across the pitch shafts (03 SYS-04), solid parts, camera 0 / 50 g | shoulder 239 / 278, elbow 161 / 188, wrist 108 / 124 N·mm; upright mid-plane 290 / 335 N·mm | horn clamps, link specs §4 |
| Everything on the turntable, arm straight out, camera, 0 / 50 g (03 SYS-05) | 692 / 832 N·mm on the base servo's output (245–286 of it in every pose) | disc horn, clamp screw; the support ring after 0.5° of tilt |
| Free-standing tipping, arm straight out, camera (03 SYS-12) | safety factor 0.34–0.48 | why the base is screwed down |

## 5. Environment
Indoor desk, 15–40 °C, no UV, no chemicals. Servo cases warm under sustained holding: don't hold a stall for minutes (the sketch eases a squeezing claw off after 2 s and parks the arm after 60 s idle).

## 6. Material
PETG (Prusament PETG or equivalent) for every printed part. PLA excluded (creeps under the servos' holding load).

## 7. Quantity and time
One arm: 12 printed pieces (the two jaws are one job), ≈35 h of printing (round 3's estimate from volumes); each job's `slice_stats.json` after re-slicing is the reference.

## 8. Acceptance criteria (measurable)
Checked in CAD (`assembly_check.py`, which also runs `claw_sequence_check.py`; `torque_budget.py`), then on the built arm.

**In CAD (re-run after any geometry change):**
- [ ] Every named pose and every viewer demo pose (`viz_export.DEMO`) is collision-free (meshes, > 1 mm³ = collision) and inside the servo travel.
- [ ] Joint windows: the shoulder 0…180° (elbow 0), the elbow's self-collision-free window covers −150…+30° (`elbow_window_deg`), the wrist −90…+90° with the camera fitted.
- [ ] Reach ≥ 280 mm from the yaw axis at full horizontal extension; collision-free desk reach (fingertips 0–8 mm up) from ≤ 100 mm to ≥ 250 mm out (any claw angle) and from ≤ 100 mm to ≥ 200 mm with the claw straight down.
- [ ] Claw assembly sequence (03 SYS-01): servo in from the front with its lead, cover and camera mount lowered on, each jaw slid in to fully open, the pinion pushed in axially at 44 mm open: 0 mm³ against everything already fitted (exact solids, 0.001 mm³ tolerance); service is the same paths in reverse.
- [ ] Claw stroke 0–44 mm every 1 mm, and one tooth pitch in 0.1 mm steps: 0 mm³ between any two claw parts (exact solids); backlash 0.3–0.4 mm per mesh, measured.
- [ ] Payload by reach as in the BUILD_GUIDE table (`torque_budget.json`), with the camera ≥ 150 g short lift at 140–160 mm out.

**On the built arm:**
- [ ] Every servo goes into its window case bottom first with its lead through the notch, without force; all tab screws bite.
- [ ] The forearm's and the claw frame's screw-strip checks pass (their spec §8; user decision 26 Oct 2026: the MG90S strips stay under 1.8 mm, checked on the first print).
- [ ] `c` puts the arm in the fitting pose: upright upper link, forearm 30° above horizontal towards +X, claw in line (§4 of the BUILD_GUIDE); after the trims (§5), the parked arm is vertical within 1°.
- [ ] Joint windows reached without buzzing at either end of each servo's travel (end-stop test, §4 step 2).
- [ ] Claw: `g 40` measures 40 ± 1 mm between the grip faces; `g 0` ↔ `g 44` runs with no tight spot; the pinion comes out through the front plate at `g 44` and goes back in.
- [ ] Desk reach: with the claw straight down (within 5°, as the mechanical check measures it), the guard lets the fingertips reach the desk (8 mm up) from ≤ 100 mm to ≥ 200 mm from the yaw axis. Firmware round 3 gives 99–223 mm within 5°; with the claw exactly vertical it is 103–217 mm, where the elbow's −150° stop sets the near end (§5 gives the guard's figures).
- [ ] Payload: holds 50 g for 10 s with the camera at 160 mm out and the claw down, shoulder servo case below 50 °C afterwards.
- [ ] Each part's own proof tests (its `spec.md` §8).

## 9. Notes and open questions
None open. Round history and every number: assembly_plan.md, `assembly_check.json`, `claw_sequence_check.json`, `torque_budget.json`.

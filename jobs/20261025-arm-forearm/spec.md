# Part spec: Forearm (elbow → wrist, 90 mm)

Job: 20261025-arm-forearm · Written by: Architect · Date: 2026-10-25 (round 3: 2026-10-26, deep reviews 01 B1/B2/S1/S2/S4 and 03 SYS-03/SYS-04/SYS-18) · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Flat 10 mm plate on the elbow servo's double-arm horn, carrying the wrist **MG90S** at 90 mm (deep review 03 SYS-18: the wrist servo is an MG90S, 216 N·mm, not an SG90). It goes onto the elbow spline at the elbow servo's centre with the forearm 60° below the upper link's line, towards +X (SYS-03), so the elbow's window is −150 … +30°.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 129 × 26 × 10 mm. Interfaces: MG996R horn slot with Ø3.6 CAD clamp hole at x 0 (8 mm floor); MG90S window 23.0 × 12.6 (printed; 23.2 × 12.8 CAD) at x 90 (deep review 01 S1: the MG90S body is 22.8 × 12.2), lead notch at the shaft end (+x) 4.2 × 1.5 printed beyond the case end, 2 × Ø1.5 printed slotted pilots, the lead-end one moved 1.3 mm out (x 99.7; 01 B1, `lead="notch_shift_pilot"`).
- Round 5 (links strength round 4): a 6 mm rib on the back face along each MG90S-window rail, and a cross-rib boss under the far pilot for the M2 × 16.
- Fasteners used: Elbow horn: M3 × 14 + Ø9 × 0.8 washer from the front face (14 − 0.8 − 8 − 0.6 = 4.6 mm into the spline, 01 S2) + 2 × M2 × 6 self-tappers through the horn's arm holes (01 S4); wrist MG90S: M2 × 12 self-tapping at the lead end and M2 × 16 at the far end, into a boss on the back face (round 5: 13.5 mm engaged; the M2 × 12 9.5 mm; NOT the short bag screws: they engage only ~5 mm and pull out under the yaw-stall case, strength round 2), the lead-end tab's slit filed to 2.1 mm so its screw reaches the moved pilot

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Elbow–wrist axis distance | 90.0 | ±0.3 | kinematics |
| MG90S window | 23.0 × 12.6 printed | +0.3/−0 | 0.4 side / 0.2 end clearance on the 22.8 × 12.2 body |
| Lead notch | 4.2 wide, 1.5 beyond the case end (printed) | +0.2/−0 | 3.6 × 1.2 mm lead ribbon |
| Printed ligaments | notch → moved pilot 1.55, far pilot → window 1.65, moved pilot → window 2.95 | min | kept under the 1.8 mm rule by the user's decision of 26 Oct 2026, with the §8 screw-strip check; strength round 4: 4.75 / 5.19 |

Servo dimensions are nominal (tools/hobby_parts.py). The MG90S has its own spec since deep review 01: body 22.8 × 12.2 mm, case bottom 18.5 mm below the tab underside, spline top 14.0 mm above it, lead leaving the shaft end 5.1 mm above the case bottom. Measure your servos and horns first and give Claude any body-size difference over 0.1 mm, any other over 0.3 mm.

## 4. Loads
Design loads come from the servos' datasheet stall torques (MG996R 1000 N·mm, MG90S 216 N·mm at 6 V), because a stalled servo is the worst case the part sees, plus the arm's own weight with a 50 g payload. The out-of-plane cases: the pitch servos give no resistance sideways, so a **base-yaw stall into a side obstacle** (swept over the joint ranges, up to 12 N at the fingertip) and a **5 N sideways hand push at the fingertip** load the printed plates and horn joints directly. Round 3: the MG90S wrist (216 N·mm: its tab-screw loads are 35 % above the SG90's), the round-3 claw (≈224 g beyond the wrist horn with the camera, solid parts) and the camera's sideways weight (deep review 03 SYS-04), from `../20261025-robot-arm-assembly/torque_budget.json`.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Elbow stall through the horn slot | 1000 N·mm | slot bearing + in-plane bending | short-term | seconds |
| Distal weight + 50 g payload | ≈335 N·mm at the elbow static (camera, solid parts), ×2 dynamic | in-plane bending | sustained | hours |
| Wrist stall reaction | 216 N·mm | 2 tab screws (MG90S) into the plate | short-term | seconds |
| Camera + claw weight across the elbow shaft (SYS-04) | 161 N·mm (188 with 50 g) about the elbow servo's case-top plane | horn clamp preload, plate round the pocket | sustained (every pose) | hours |
| Wrist servo's sideways moment (SYS-04) | 108 N·mm (124 with 50 g) about the wrist servo's case-top plane | 2 tab screws, plate round the window | sustained (every pose) | hours |
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
- [ ] The MG90S goes into the window from the front face, case bottom first, with its lead ribbon in the notch, without force (measure it first: 22.8 × 12.2 nominal); both tab screws bite, the lead-end one through the filed slit
- [ ] **Screw-strip check (user decision 26 Oct 2026).** The strips between the window and the two tab pilots are 1.34 mm (lead end) and 1.45 mm (far end) in CAD, about 1.55 / 1.65 printed, under fdm-design-rules' 1.8 mm. The user kept them and asked for this check instead: drive both tab screws (M2 × 12 lead end, M2 × 16 far end) snug on the printed forearm, then look at both strips. Pass: no whitening, no crack. If either fails, stop: the pilots move out (lead end 1.6 mm, far end 0.2 mm, with the tab slits filed to match) and the forearm is reprinted
- [ ] At the elbow servo's centre the forearm sits 60° below the upper link's line, towards +X (within one spline step, ±7°)
- [ ] **Proof test (links strength round 4, at the 1079 N·mm datasheet stall):** (1) Clamp the elbow horn in a vice, 1 kg at the wrist axis for 1 min (in the forearm's plane): no cracks, no set. (2) Same clamping, with the forearm plate vertical and the wrist MG90S fitted with its tab screws as built. Screw a flat bar (≥ 100 mm, wood or aluminium) to the wrist horn in place of the claw, and set it at 45° to the forearm in the forearm's plane. Push 19 N (≈1.9 kg on a luggage scale) along the wrist shaft, square to the plate, at 83 mm from the wrist axis, 1 min each way. Pass: no cracks or whitening at the window corners and rails, the horn pocket, the MG90S pilots or either screw strip; the MG90S tabs don't lift; the forearm doesn't lift off the horn; the bar end comes back to within 1 mm of where it started.
## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

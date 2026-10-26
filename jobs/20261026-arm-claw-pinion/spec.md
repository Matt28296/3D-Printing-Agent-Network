# Part spec: Claw pinion (18 teeth, module 1)

Job: 20261026-arm-claw-pinion · Written by: Architect · Date: 2026-10-26 · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Spur gear on the claw MG90S: module 1, 18 teeth, 20°, pitch Ø18, 8 mm wide. Turns both racks in opposite directions, so the jaws open and close symmetrically: 3.18° of servo per mm of jaw gap, 0–44 mm in 140°. The servo's double-arm horn, both arms cut 5.5 mm from the centre, sits 2 mm deep in its back face.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: Ø20 × 8 mm. Interfaces: trimmed-horn pocket (hub Ø7.6 + two stubs to r 5.75, 2 deep) on the back face; Ø2.6 clamp hole; Ø4.4 × 1.6 counterbore for the M2 head on the front face.
- Fasteners used: M2×10 pan/cheese head from the front (through the pinion and the horn into the spline); optional drop of CA glue on the horn stubs

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Teeth | m 1, z 18, 20°, 0.1 thinned | profile in the bed plane | 0.2 backlash with the racks |
| Horn pocket | hub + stubs to r 5.75 | +0.3 clearance | snug on the trimmed horn |
| Counterbore | Ø4.4 × 1.6 | +0.2/−0 | M2 head below the face |

Servo and camera dimensions are nominal (tools/hobby_parts.py, claw_frame.py). The MG90S is kept at the SG90 body size the arm was reviewed with; makers list 22.5–22.8 × 12–12.2 mm, so measure your MG90S (body length and width, tab-hole spacing, shaft to near end) and the double-arm horn (hub Ø, arm width near the hub), and give Claude any difference over 0.3 mm. Brio 4K: 27 × 102 × 27 mm, 63 g with its clip removed, 1/4"-20 thread centred on the bottom (Logitech quick-start guide); check the thread depth before choosing the screw.

## 4. Loads
Design loads come from the MG90S datasheet stall torque (≈216 N·mm at 6 V), the stalled servo being the worst case the claw sees: the pinion (pitch radius 9 mm) then pushes **24 N** into the racks, **12 N per jaw** when both jaws touch the object, or the full **24 N on one jaw** when an off-centre object stops one jaw first. Plus the arm cases kept from the arm's strength review: a **5 N sideways push** and a base-yaw stall of up to **12 N** at the fingertip. The end effector now weighs ≈148 g with the camera (claw ≈53 g printed + 2 × MG90S + Brio 63 g + screws), ×3 for arm accelerations; the Brio's USB cable can tug the camera with ≈10 N.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Claw stall, one jaw blocked | 216 N·mm → 24 N on one rack | tooth bending (Lewis), horn-stub bearing | short-term | seconds |
| Normal gripping | ≈50 % of stall, both jaws | tooth bending | cyclic | thousands of cycles |

## 5. Environment
- Max temperature the part will see (°C): 40 (indoor desk; MG90S cases warm under sustained grip)
- Outdoor / UV: no
- Chemicals, oils, moisture: none

## 6. Material
- Preferred or required: PETG (Prusament PETG or equivalent), user left the choice to the designer
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA for the load-path parts (creeps under sustained servo-holding load); ABS/ASA (no enclosure needed for this job)

## 7. Quantity and time
- Quantity: 1
- Max acceptable print time per batch (h): 1

## 8. Acceptance criteria (measurable)
- [ ] Pinion presses onto the trimmed horn snugly
- [ ] Turning the servo by hand (unpowered) runs both jaws smoothly with a little backlash
- [ ] **Proof test:** With the claw assembled, grip a 20 mm wooden block clamped in a vice, first centred, then 8 mm off-centre (one jaw touches first), and command full close for 10 s, 5 times each. Pass: no tooth damage or whitening on the pinion or racks, the horn stubs do not slip in the pocket (mark a line across pinion and servo case with a pen), and the jaws open again smoothly.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

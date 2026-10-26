# Part spec: Claw frame (wrist plate + servo bulkhead)

Job: 20261026-arm-claw-frame · Written by: Architect · Date: 2026-10-26 · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
6 mm wrist plate on the wrist MG90S's single-arm horn, a 6 mm bulkhead that holds the claw MG90S with its shaft pointing at the fingertips, and the lower rail that backs rack B. Rack B slides on the wrist plate's top face. Replaces the old gripper base (20261025-arm-gripper-base).

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 35.7 × 64 × 39 mm. Interfaces: MG90S arm-horn pocket (back face, 2 deep) with Ø2.6 clamp hole at (0, 0); MG90S window 22.9 × 12.6 (printed) through the bulkhead at x 4–10, shaft on (y 0, z 22.5), 45° shoulders above it, 2 × Ø1.7 teardrop tab pilots; lower rail x 10–19.15, z 6–13; 2 × Ø2.7 M3 pilots 14 deep in the bulkhead top at (7, −23) and (7, 14); 2 × Ø2.7 teardrop M3 pilots 10 deep in the wrist plate's front edge at (y ±24, z 3).
- Fasteners used: Wrist horn: M2×12 centre screw + Ø6 washer from the front face at (0, 0), BEFORE the claw servo goes in (its body covers the screw), + 1 small screw through the horn arm; claw MG90S: 2 tab screws (M2×8 self-tapping if the bag screws are short); cover: 2 × M3×10 (or M3×18 button heads with the camera mount) into the top pilots, 2 × M3×12 into the front pilots

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Claw-servo axis | y 0, z 22.5 | ±0.2 | sets the gear mesh |
| Bulkhead front face (tab seat) | x 10.0 | ±0.2 | sets the pinion's x |
| Wrist plate top (rack B track) | z 6.0 | ±0.15 | 0.25 sliding gap |
| Lower rail front face | x 19.15 | ±0.15 | 0.25 sliding gap |
| MG90S window | 22.9 × 12.6 printed | +0.3/−0 | clearance |

Servo and camera dimensions are nominal (tools/hobby_parts.py, claw_frame.py). The MG90S is kept at the SG90 body size the arm was reviewed with; makers list 22.5–22.8 × 12–12.2 mm, so measure your MG90S (body length and width, tab-hole spacing, shaft to near end) and the double-arm horn (hub Ø, arm width near the hub), and give Claude any difference over 0.3 mm. Brio 4K: 27 × 102 × 27 mm, 63 g with its clip removed, 1/4"-20 thread centred on the bottom (Logitech quick-start guide); check the thread depth before choosing the screw.

## 4. Loads
Design loads come from the MG90S datasheet stall torque (≈216 N·mm at 6 V), the stalled servo being the worst case the claw sees: the pinion (pitch radius 9 mm) then pushes **24 N** into the racks, **12 N per jaw** when both jaws touch the object, or the full **24 N on one jaw** when an off-centre object stops one jaw first. Plus the arm cases kept from the arm's strength review: a **5 N sideways push** and a base-yaw stall of up to **12 N** at the fingertip. The end effector now weighs ≈148 g with the camera (claw ≈53 g printed + 2 × MG90S + Brio 63 g + screws), ×3 for arm accelerations; the Brio's USB cable can tug the camera with ≈10 N.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Wrist stall through the horn pocket | 216 N·mm | pocket walls in bearing | short-term | seconds |
| Claw-servo stall reaction | 216 N·mm about x | 2 tab screws into the bulkhead | short-term | seconds |
| Rack B back thrust (one jaw blocked) | ≈24 N grip × lever → ±20 N | lower rail, in its plane | short-term | seconds |
| Claw + camera weight | ≈148 g × 3 g | wrist plate bending, bulkhead root | cyclic | hours |
| Sideways push / yaw stall at the fingertip | 5 N / 12 N | wrist plate out of plane, horn clamp | short-term | seconds |

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
- Max acceptable print time per batch (h): 4

## 8. Acceptance criteria (measurable)
- [ ] MG90S slides into the window from behind without force; both tab screws bite
- [ ] Wrist horn seats flat in its pocket
- [ ] Rack B slides along the wrist plate with no binding
- [ ] **Proof test:** Claw fully assembled with the camera, wrist horn clamped in a vice: push 7.5 N (≈0.75 kg on a luggage scale) at the fingertips, sideways (±z) then up and down (±y), 1 min each. Pass: no cracks or whitening at the horn pocket, the bulkhead root, the servo window corners or any screw pilot; the frame doesn't lift off the horn; the fingertips return to within 0.5 mm.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

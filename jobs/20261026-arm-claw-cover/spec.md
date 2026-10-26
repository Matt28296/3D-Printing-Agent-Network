# Part spec: Claw cover (front plate, top wall, upper lip)

Job: 20261026-arm-claw-cover · Written by: Architect · Date: 2026-10-26 · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Closes both rack channels: the front plate holds both racks forward and carries the two neck slots (A open at −y, B open at +y, so the jaws slide in from the ends), the top wall holds rack A down against the pinion's separating force, and the upper lip backs rack A. A Ø5 hole reaches the pinion's clamp screw. The camera mount sits on its top wall.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 26.7 × 64 × 42 mm (print: 26.7 × 42 × 64). Interfaces: top wall x 4–30.65, z 39–42; front plate x 27.65–30.65, z 0–39; lip x 10–19.15, z 32–39; slot A z 30.25–35.75, y −33…+0.25; slot B z 9.25–14.75, y −0.25…+33; 2 × Ø3.6 top holes, 2 × Ø3.6 front holes, Ø5.2 access hole on the pinion axis.
- Fasteners used: 2 × M3×10 down into the frame's bulkhead (M3×18 button heads when the camera mount is fitted), 2 × M3×12 back into the wrist plate's front edge

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Front plate inner face | x 27.65 | ±0.15 | 0.25 sliding gap to the racks |
| Top wall underside | z 39.0 | ±0.15 | 0.25 gap over rack A |
| Lip front face | x 19.15 | ±0.15 | 0.25 gap behind rack A |
| Neck slots | 5.5 wide | +0.2/−0 | 0.25 around the 5 mm necks |

Servo and camera dimensions are nominal (tools/hobby_parts.py, claw_frame.py). The MG90S is kept at the SG90 body size the arm was reviewed with; makers list 22.5–22.8 × 12–12.2 mm, so measure your MG90S (body length and width, tab-hole spacing, shaft to near end) and the double-arm horn (hub Ø, arm width near the hub), and give Claude any difference over 0.3 mm. Brio 4K: 27 × 102 × 27 mm, 63 g with its clip removed, 1/4"-20 thread centred on the bottom (Logitech quick-start guide); check the thread depth before choosing the screw.

## 4. Loads
Design loads come from the MG90S datasheet stall torque (≈216 N·mm at 6 V), the stalled servo being the worst case the claw sees: the pinion (pitch radius 9 mm) then pushes **24 N** into the racks, **12 N per jaw** when both jaws touch the object, or the full **24 N on one jaw** when an off-centre object stops one jaw first. Plus the arm cases kept from the arm's strength review: a **5 N sideways push** and a base-yaw stall of up to **12 N** at the fingertip. The end effector now weighs ≈148 g with the camera (claw ≈53 g printed + 2 × MG90S + Brio 63 g + screws), ×3 for arm accelerations; the Brio's USB cable can tug the camera with ≈10 N.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Rack A lift (gear separating force) | 24 N × tan 20° ≈ 9 N | top wall bending between screws | short-term | seconds |
| Rack thrust from the finger moment (one jaw blocked) | ±20 N | front plate strips and lip, in their planes | short-term | seconds |
| Camera mount on the top wall | ≈1.5 N × 3, cable tug 10 N | top wall, 2 screws through it | short-term | seconds |

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
- Max acceptable print time per batch (h): 3

## 8. Acceptance criteria (measurable)
- [ ] Both jaws slide in from the ends and run 0–44 mm without binding
- [ ] Pinion clamp screw reachable through the Ø5 hole
- [ ] **Proof test:** Covered by the claw proof tests (frame and jaw): after them, both jaws still slide the full 0–44 mm with no binding, the slot edges show no cracks, and the cover screws are still tight.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

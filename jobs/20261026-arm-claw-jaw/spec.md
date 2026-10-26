# Part spec: Claw jaw (rack + finger), ×2

Job: 20261026-arm-claw-jaw · Written by: Architect · Date: 2026-10-26 · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
One-piece rack (module 1, 44 mm, teeth along y), neck (14 × 5 mm, passes through the cover slot) and finger blade (6 mm thick, 45 mm long, 20 mm-tall grip face). The grip face has 0.6 mm cross-grooves and a 1.5 mm V-notch along the centre line for pens, rods and wires. Two identical copies: jaw B is jaw A turned 180° about the pinion axis.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 57 × 44 × 26 mm (claw x × y × z). Interfaces: rack teeth meshing with the pinion (pitch line 9 from its axis), rack back face against the lip/rail, rack front face against the cover front plate, neck through the cover slot, grip face on y 0 when closed.
- Fasteners used: None

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Rack pitch line to back face | 7.25 | ±0.15 | sets the mesh |
| Rack face width | 8.0 | −0.15/+0 | 0.25 sliding gaps |
| Neck | 14 × 5 | ±0.15 | 0.25 in the slot |
| Grip face | y 0 closed | ±0.2 | jaws meet |

Servo and camera dimensions are nominal (tools/hobby_parts.py, claw_frame.py). The MG90S is kept at the SG90 body size the arm was reviewed with; makers list 22.5–22.8 × 12–12.2 mm, so measure your MG90S (body length and width, tab-hole spacing, shaft to near end) and the double-arm horn (hub Ø, arm width near the hub), and give Claude any difference over 0.3 mm. Brio 4K: 27 × 102 × 27 mm, 63 g with its clip removed, 1/4"-20 thread centred on the bottom (Logitech quick-start guide); check the thread depth before choosing the screw.

## 4. Loads
Design loads come from the MG90S datasheet stall torque (≈216 N·mm at 6 V), the stalled servo being the worst case the claw sees: the pinion (pitch radius 9 mm) then pushes **24 N** into the racks, **12 N per jaw** when both jaws touch the object, or the full **24 N on one jaw** when an off-centre object stops one jaw first. Plus the arm cases kept from the arm's strength review: a **5 N sideways push** and a base-yaw stall of up to **12 N** at the fingertip. The end effector now weighs ≈148 g with the camera (claw ≈53 g printed + 2 × MG90S + Brio 63 g + screws), ×3 for arm accelerations; the Brio's USB cable can tug the camera with ≈10 N.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Grip at stall, one jaw blocked | 24 N on the grip face, up to 45 mm in front of the rack | neck and blade root bending across layers, rack teeth | short-term | seconds |
| Grip, both jaws | 12 N each | as above | cyclic | thousands of cycles |
| Sideways push at the fingertip | 5 N along z | blade bending about y (along the layers) | short-term | seconds |

## 5. Environment
- Max temperature the part will see (°C): 40 (indoor desk; MG90S cases warm under sustained grip)
- Outdoor / UV: no
- Chemicals, oils, moisture: none

## 6. Material
- Preferred or required: PETG (Prusament PETG or equivalent), user left the choice to the designer
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA for the load-path parts (creeps under sustained servo-holding load); ABS/ASA (no enclosure needed for this job)

## 7. Quantity and time
- Quantity: 2
- Max acceptable print time per batch (h): 4

## 8. Acceptance criteria (measurable)
- [ ] Both jaws slide in from the ends and mesh at the closed position
- [ ] Grip faces meet flat when closed (feeler 0.2 mm max gap)
- [ ] **Proof test:** Grip test as for the pinion (centred and 8 mm off-centre, full close 10 s, 5 times each), then grip a 10 mm wooden dowel at the fingertips and hang 200 g from it for 1 min. Pass: no cracks or whitening at the neck, the flares or the blade root; the dowel does not slip; jaws still slide freely.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

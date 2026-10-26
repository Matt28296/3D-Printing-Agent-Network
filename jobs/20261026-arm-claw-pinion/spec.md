# Part spec: Claw pinion (20 teeth, module 1)

Job: 20261026-arm-claw-pinion · Written by: Architect · Date: 2026-10-26 (round 3: 2026-10-26, deep reviews 01 B2 and 03 SYS-01 / SYS-08, pinion DFM and strength round 1) · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Spur gear on the claw MG90S: module 1, 20 teeth, 20°, pitch Ø20, 10 mm wide, tips topped 0.15 (outside Ø21.7), root fillets r 0.38. Turns both racks in opposite directions, so the jaws open and close symmetrically: 2.865° of servo per mm of jaw gap, 0–44 mm in 126°. The servo's double-arm horn, both arms cut 5.5 mm from the centre, sits 2 mm deep in its back face with a light 0.1 mm fit that centres the pinion on the spline (SYS-08). It goes on last, pushed axially through the cover's Ø22.6 pass-through with both jaws parked fully open, and comes off first for service (SYS-01).

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: Ø21.7 × 10 mm. Interfaces: trimmed-horn pocket on the back face (hub Ø7.2 + two stubs to r 5.5, + 0.1 fit and HOLE_COMP, 2 deep); Ø2.6 clamp hole; Ø6.4 CAD × 1.7 counterbore on the front face for the Ø6 washer, leaving a 6.3 mm floor above the horn; 0.25 mm 45° chamfer on the bed face, tooth outline included.
- Fasteners used: M2 × 12 + Ø6 × 0.5 washer from the front (through the pinion and the horn into the spline): 12 − 0.5 − 6.3 − 0.6 = 4.6 mm into the spline, like every other horn clamp on the arm; a drop of CA glue on the horn stubs after the dry run

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Teeth | m 1, z 20, 20°, each tooth 0.10 thinner at the pitch line (the racks' 0.25) | profile in the bed plane | 0.35 backlash per mesh with the racks (measured in `claw_sequence_check.json`) |
| Outside diameter | 21.7 (tips topped 0.15) | ±0.1 | 0.40 tip clearance to the rack roots; 0.45 radial in the pass-through |
| Horn pocket | hub + stubs to r 5.5 | +0.1 fit | centres the pinion on the horn |
| Counterbore | Ø6.4 CAD × 1.7 | +0.2/−0 | seats the Ø6 washer; the M2 head stands ≤ 0.8 proud of the face, inside the pass-through |

Servo dimensions are nominal (`tools/hobby_parts.py`, `claw_frame.py`). The MG90S has its own spec since deep review 01: spline top 14.0 mm above the tab underside, so the pinion's back face sits at claw x 22.6. Measure yours, and the double-arm horn (hub Ø, arm width near the hub), and give Claude any difference over 0.3 mm.

## 4. Loads
Design loads come from the MG90S's 6 V stall torque (≈216 N·mm), the stalled servo being the worst case the claw sees: the pinion (pitch radius 10 mm) then pushes **21.6 N** into the racks, **10.8 N per jaw** when both jaws touch the object, or the full **21.6 N on one jaw** when an off-centre object stops one jaw first. (A real stall grip is 6–8.5 N per finger: deep review 03 SYS-15.)

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Claw stall, one jaw blocked | 216 N·mm → 21.6 N on one rack | tooth bending at the filleted root, horn-stub bearing in the pocket | short-term | seconds |
| Normal gripping | ≈50 % of stall, both jaws | tooth bending | cyclic | thousands of cycles |
| Clamp preload | M2 × 12 snug | 6.3 mm floor under the washer | sustained | months |

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
- [ ] Pinion presses onto the trimmed horn with a light fit and sits centred
- [ ] At `g 44`, with both jaws parked fully open, it slides axially through the cover's hole into both racks (nudging a jaw by at most half a tooth)
- [ ] `g 0` ↔ `g 44` runs both jaws smoothly, with no tight spot, and a little backlash (≈0.35 mm per mesh)
- [ ] **Proof test (claw strength round 2, 1.5 × the design loads; the claw opening against an obstacle stays a design case):** Claw assembled, wrist horn in a vice, servo powered and holding, jaws at 30 mm.
  1. Each fingertip in turn, 3 mm from the tip: pull it along the jaw travel, away from the other jaw, with **32 N** (3.3 kg on a luggage scale, 1.5 × the one-jaw stall force), 10 s. If the servo slips before 32 N, note the force: the teeth have then been proven only to that force.
  2. Push jaw B's fingertip sideways towards the wrist (−z) with **10.7 N** (1.5 × the yaw stall), 10 s, with the jaws closed and again at 44 mm.
  3. Then the grip test already in §8: a 20 mm wooden block in a vice, centred and then 8 mm off-centre, 5 full closes each.

  Pass:
  - no tooth damage or whitening on the pinion or the racks (look at the tooth roots with a loupe);
  - the horn stubs haven't slipped in the pocket (pen line across the pinion and the servo case);
  - the jaws run 0–44 mm smoothly afterwards, with no tight spot and no new play.
## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`; claw assembly order and fit: `claw_sequence_check.json`.

# Part spec: Claw jaw (rack + finger), ×2

Job: 20261026-arm-claw-jaw · Written by: Architect · Date: 2026-10-26 (round 3: 2026-10-26, deep review 03 SYS-01 / SYS-08, jaw DFM and strength round 1) · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
One piece: a module-1 rack (56.5 mm along y, 10 mm face, 10 mm of solid behind the tooth roots), a 20 × 10 mm neck on that solid back (r 4 root fillets; it passes through the cover's slot), and a finger: 12 mm thick for 20 mm from the neck, tapering to 6 mm over the next 15, 45 mm long, with a full-height 45° gusset from the neck and r 3 fillets at its re-entrant kinks. The 20 mm-tall grip face has 0.6 mm cross-grooves and a 1.5 mm V-notch along the centre line for pens, rods and wires. Two identical copies: jaw B is jaw A turned 180° about the pinion axis. Each rack's back face rides on its guide (rack A under the cover's top wall, rack B on the frame's wrist plate), where the gear's separating force presses it, so both meshes run at the nominal centre distance (deep review 03 SYS-08). The jaws slide in from the open ends of their slots to fully open before the pinion goes in (SYS-01).

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 60.75 × 56.5 × 31.25 mm (claw x × y × z; print 31.25 × 56.5 × 60.75, standing on the rack's back end). Interfaces (jaw A, closed, claw frame G): rack teeth meshing with the pinion, pitch line on z 37.25 (10 from the axis); rack back face on z 48.5 (the top wall); rack x faces at 22.6 and 32.6 (0.25 to the lip wall and to the front plate); neck z 38.5–48.5, y −20…0, through slot A; grip face on y 0. The rack's back/front edge has a 2 mm 45° chamfer for y ≥ 4.5 (clears the cover's r 2 corner fillet over the whole stroke); the bed face a 0.3 mm chamfer, tooth outline included.
- Fasteners used: None

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Rack pitch line to back face | 11.25 | ±0.15 | sets the mesh (the back rides on its guide) |
| Rack face width (x) | 10.0 | −0.15/+0 | 0.25 sliding gaps |
| Teeth | m 1, 20°, each 0.25 thinner at the pitch line, tips topped 0.15 | in the bed plane | 0.35 backlash per mesh with the pinion's 0.10 |
| Neck | 20 × 10 | ±0.15 | 0.25 in its slot |
| Grip face | y 0 closed | ±0.2 | jaws meet |

Servo and camera dimensions are nominal (`tools/hobby_parts.py`, `claw_frame.py`). The MG90S has its own spec since deep review 01 (spline top 14.0 mm above the tab underside), which sets the racks' x position. Measure yours and give Claude any difference over 0.3 mm.

## 4. Loads
Design loads come from the MG90S's 6 V stall torque (≈216 N·mm), the stalled servo being the worst case the claw sees: the 20-tooth pinion (pitch radius 10 mm) then pushes **21.6 N** into the racks, **10.8 N per jaw** when both jaws touch the object, or the full **21.6 N on one jaw** when an off-centre object stops one jaw first. (A real stall grip is 6–8.5 N per finger, because the finger's moment presses the rack onto its guides: deep review 03 SYS-15. The stall figures stay the design loads.) Plus the arm cases: a **5 N sideways push** and the base-yaw stall sweep at the fingertip. The jaw prints standing, finger up (claw x = print Z), so **every bending of the neck and the finger, in either direction, puts its stress across the layers** (DFM round 1, item 4).

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Grip at stall, one jaw blocked | 21.6 N on the grip face, 3 mm from the tip (up to 45 mm in front of the rack) | neck and finger root bending and twist, across the layers; rack teeth | short-term | seconds |
| Grip, both jaws | 10.8 N each | as above | cyclic | thousands of cycles |
| Sideways push at the fingertip | 5 N along ±z | neck and finger bending, across the layers | short-term | seconds |
| Yaw-stall sweep at the fingertip | ≤ 6.6 N along z, ≤ 2.8 N along y, ≤ 13 N along x | as above | short-term | seconds |
| Rack ends on the guides | ≈28 N (the couple of the one-jaw stall) | lip / rail wall and front plate | short-term | seconds |

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
- Max acceptable print time per batch (h): 6 (both on one plate; round 3's jaw is 2.3 times the round-1 volume)

## 8. Acceptance criteria (measurable)
- [ ] Without the pinion, both jaws slide in from the open slot ends to fully open with no binding
- [ ] With the pinion in, the jaws run 0–44 mm with no tight spot; the grip faces meet flat when closed (feeler 0.2 mm max gap)
- [ ] `claw_sequence_check.py`: 0 mm³ on both slide-in paths and over the stroke
- [ ] **Proof test (claw strength round 2, 1.5 × the design loads; the claw opening against an obstacle stays a design case):** Claw assembled, wrist horn in a vice, servo powered and holding, jaws at 30 mm. For each jaw in turn:
  1. Loop a cord round the finger 3 mm from the tip, at the edge of the grip face farthest from the jaw's own rack. Pull away from the other jaw with **32 N** (3.3 kg on a luggage scale, 1.5 × the one-jaw stall), 10 s.
  2. At the same place, push towards the other jaw on the outer face with **32 N** (1.5 × the opening stall), 10 s.
  3. Push the fingertip sideways (±z) with **10.7 N** (1.5 × the yaw stall), 10 s each way.
  4. Then the checks §8 already has: the grip test as for the pinion (centred and 8 mm off-centre, 5 full closes each), and a 10 mm wooden dowel gripped at the fingertips with 200 g hanging from it for 1 min.

  If the servo slips before a pull reaches 32 N, note the force: the jaw has then been proven only to that force.

  Pass:
  - no crack or whitening at the grooves nearest the tip, the taper's end, the neck's root fillets, the gusset or the kinks (use a loupe; whitening runs along a layer line);
  - the dowel doesn't slip;
  - the jaws still slide freely and meet flat (0.2 mm feeler at most).
## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`; claw assembly order and fit: `claw_sequence_check.json`.

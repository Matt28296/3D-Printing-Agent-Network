# Part spec: Claw cover (front plate, top wall, upper lip)

Job: 20261026-arm-claw-cover · Written by: Architect · Date: 2026-10-26 (round 3: 2026-10-26, deep review 03 SYS-01, claw DFM and strength round 1) · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Closes both rack channels. The front plate holds both racks forward and carries the two neck slots (A open at −y, B open at +y, so the jaws slide in from the ends) and the pinion's pass-through: the pinion goes in last, axially, with both jaws parked fully open, and comes out first for service (deep review 03 SYS-01, fix A). The top wall is rack A's guide (the gear's separating force presses rack A's back against it); the lip wall backs rack A. A tie (post + web, between the racks) joins the two halves of the front plate that the slots and the pass-through separate. The camera mount sits on its top wall.


**Round 3 (claw DFM and strength round 2): lip wall GUIDE_T 8 (lip at x 14.35); a second tie at y 24–32 with 45° undersides; FRONT_Z0 −6 (front plate down to 6 below the claw's back face); X_F0 / X_F1 34.85 / 39.85; two breakaway support pillars under the pieces beside the pinion pass-through (slicer supports off; BUILD_GUIDE step 9 snaps them off; justified in the brief); front screws M2.5 × 16. Where a row in §2–§4 below gives an older value, these govern.**


**Round 4 (user-approved, claw round 3 DFM and strength): support pillar B SUP_B = (−8.0, CRESCENT_Y, ZB1 + 0.2, ZB1 + 1.8); the second tie's post 8 mm thick (x 14.35–22.35), down onto the frame's rail block at z 17.75, held by one M3 × 45 socket head through a Ø3.6 hole at (18.35, 28) into the frame's Ø2.7 × 14 pilot.**

**Round 5 (user-approved, cover strength round 4): the second tie's post foot flats at z 17.85 (0.1 over the frame's rail block), with a 90° V-ridge under them (0.1 clear per flank, tip flat at z 17.25) in the frame's V-groove; an M3 washer Ø7 × 0.5 under the M3 × 45's head.**

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 37.85 × 64 × 55.5 mm (print: 37.85 × 55.5 × 64; claw frame G: x 0…37.85, y ±32, z −4…51.5). Interfaces:
  - top wall x 0–37.85, z 48.5–51.5, 1.5 mm 45° chamfer on its top-front edge (the camera looks over it);
  - front plate x 32.85–37.85, z −4–48.5; r 2 fillet in its inner corner with the top wall over y 9–32;
  - lip wall x 18.35–22.35, z 36.75–48.5;
  - tie: post x 18.35–22.35 (z 19.25–36.75) and web x 22.35–32.85 (z 19.25–35.25), both at y −32…−24, clear of both racks' tips by 1.15;
  - slot A z 38.25–48.5 (its outer edge is the top wall's underside), open at −y, closing at y +6.5 with a 45° roof;
  - slot B z 5.75–16.25, open at +y, closing at y −5 with r 2 corners;
  - pinion pass-through Ø22.8 CAD (≈22.6 printed) on the pinion axis (y 0, z 27.25) with a 45° teardrop top; the slivers it would leave beside the slots are cut back to |y| 7;
  - 2 × Ø3.6 teardrop top holes at (6.75, −23) and (6.75, 14); 2 × Ø3.0 teardrop front holes at (y ±24, z 3).
- Fasteners used: 2 × M3 × 10 down into the frame's bulkhead (2 × M3 × 18 button heads through the camera mount when it is fitted); 2 × M2.5 × 12 pan head (head ≤ Ø5) back into the wrist plate's front edge

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Front plate inner face | x 32.85 | ±0.15 | 0.25 sliding gap in front of the racks |
| Top wall underside | z 48.5 | ±0.15 | rack A's back rides on it |
| Lip wall front face | x 22.35 | ±0.15 | 0.25 sliding gap behind rack A |
| Slot A (neck A, 10 tall) | z 38.25–48.5 | +0.2/−0 | 0.25 on the side nearer the axis |
| Slot B (neck B, 10 tall) | z 5.75–16.25 | +0.2/−0 | 0.25 each side |
| Pinion pass-through | Ø22.6 printed | +0.3/−0 | pinion tips Ø21.7: 0.45 radial |

Servo and camera dimensions are nominal (`tools/hobby_parts.py`, `claw_frame.py`). The MG90S has its own spec since deep review 01: body 22.8 × 12.2 mm, case bottom 18.5 mm below the tab underside, spline top 14.0 mm above it. Measure yours and give Claude any body-size difference over 0.1 mm or any other over 0.3 mm. Brio 4K: 27 × 102 × 27 mm, 63 g with its clip removed, 1/4"-20 thread centred on the bottom, USB-C on its back.

## 4. Loads
Design loads come from the MG90S's 6 V stall torque (≈216 N·mm), the stalled servo being the worst case the claw sees: the 20-tooth pinion (pitch radius 10 mm) then pushes **21.6 N** into the racks, **10.8 N per jaw** when both jaws touch the object, or the full **21.6 N on one jaw** when an off-centre object stops one jaw first. (A real stall grip is 6–8.5 N per finger, because the finger's moment presses the rack onto its guides: deep review 03 SYS-15. The stall figures stay the design loads.) Plus the arm cases: a **5 N sideways push** and a base-yaw stall of up to **12 N** at the fingertip. The end effector beyond the wrist horn weighs ≈209 g with the camera (≈224 g with solid parts; `../20261025-robot-arm-assembly/torque_budget.json`), ×3 for arm accelerations. The Brio's USB cable can tug the camera with ≈10 N.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Rack A lift (gear separating force) | 21.6 N × tan 20° ≈ 7.9 N | top wall, bending between the screws | short-term | seconds |
| Rack thrust from the finger moment (one jaw blocked) | ≈28 N | front plate strips and lip wall, in their planes; the tie web | short-term | seconds |
| Neck in its slot (one jaw blocked, side push) | 21.6 N / 5 N / 12 N | slot edges, slot A's roof, slot B's corners | short-term | seconds |
| Camera mount on the top wall | ≈0.8 N × 3, cable tug 10 N | top wall, 2 screws through it | short-term | seconds |

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
- [ ] The cover lowers onto the frame with the claw servo fitted, without force
- [ ] Both jaws slide in from the open slot ends to fully open without binding; the pinion then passes the front plate's hole and meshes with both racks; the jaws run 0–44 mm without binding
- [ ] The pinion's clamp screw is reachable through the pass-through
- [ ] `claw_sequence_check.py`: 0 mm³ on every insertion path and over the stroke
- [ ] **Proof test (claw strength round 2, 1.5 × the design loads; the claw opening against an obstacle stays a design case):** Claw assembled on the frame, wrist horn in a vice, servo powered and holding, jaws at 30 mm.
  1. Each fingertip in turn, 3 mm from the tip: pull it away from the other jaw with **32 N** (3.3 kg on a luggage scale, 1.5 × the one-jaw stall), 10 s. Then push it towards the other jaw with **32 N** (1.5 × the opening stall), 10 s.
  2. Push jaw B's fingertip sideways towards the wrist (−z) with **10.7 N** (1.5 × the yaw stall), 10 s, jaws closed and again at 44 mm.

  Pass:
  - no crack or whitening at the lip's roots, the top wall behind the lip, both ties' posts, webs and their corners, the second post's ridge still seated in the frame's groove (a 0.15 mm feeler does not enter under the post's foot), and its M3 × 45 and washer still tight, the upper piece's top corner and slot A's V apex, the strip under slot B, or the slot ends;
  - both jaws still slide the full 0–44 mm without binding;
  - the cover screws are still tight.
## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`; claw assembly order and fit: `claw_sequence_check.json`.

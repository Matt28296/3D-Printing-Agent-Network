# Part spec: Claw frame (wrist plate + servo bulkhead)

Job: 20261026-arm-claw-frame · Written by: Architect · Date: 2026-10-26 (round 3: 2026-10-26, deep reviews 01 and 03, claw DFM and strength round 1) · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
A 6 mm wrist plate, full width, with a 2.3 mm raised pad behind the bulkhead, clamped on the wrist MG90S's single-arm horn; a 6.5 mm bulkhead that holds the claw MG90S with its shaft pointing at the fingertips; and a 4 mm rail wall that backs rack B. Rack B rides on the wrist plate's top face. The cover screws onto it. Replaces the old gripper base (20261025-arm-gripper-base).


**Round 3 (claw DFM and strength round 2): rail block from the bulkhead (x 10–22.35) instead of a 4 mm rail wall; two 6 × 10 ribs behind the bulkhead and an r 1.5 fillet at its root; lead notch with a 45° top; wrist clamp washer Ø8 × 0.8 (DIN 9021, 4.3 mm into the spline) with a 1 mm relief in the bulkhead; front screws M2.5 × 16 in 14 mm pilots. Where a row in §2–§4 below gives an older value, these govern.**


**Round 4 (user-approved with the cover anchor): one Ø2.7 × 14 M3 pilot in the rail block at (18.35, 28) for the cover's M3 × 45 anchor; 2.65 mm wall round it.**

**Round 5 (user-approved with the cover's V-seat): a 90° V-groove, 0.8 deep, along y in the rail block's top (x 14.45–16.05 at z 17.75, y 23.5–32, open at +y), 0.95 mm from the anchor pilot; the cover's M3 × 45 has a Ø7 × 0.5 washer, 10.75 mm engaged.**

**Round 6 (user-approved, frame round 5 review): the bulkhead and rib tops at z 48.45 (off the slice plane; prints at 48.4); the top M3 pilots 14 deep below it.**

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 40.85 × 64 × 48.5 mm (claw frame G: x −8…32.85, y ±32, z 0…48.45). Interfaces:
  - MG90S arm-horn pocket on the back face (2 deep), Ø2.6 clamp hole at (0, 0) through plate and pad: 6.3 mm floor;
  - MG90S window through the bulkhead (x 3.5–10): 23.2 × 12.8 CAD (23.0 × 12.6 printed), shaft on (y 0, z 27.25); 7 mm 45° roof above it, Ø3 teardrop reliefs at its two lower corners;
  - lead notch at the shaft end (G +y): 4.4 wide CAD, reaching 1.6 beyond the case end; the tab pilots are Ø1.7 CAD teardrop slots (0.4 longer outwards) at G y −19.4 and +9.7: the lead-end one moved 1.3 mm out (`lead="notch_shift_pilot"`, deep review 01 B1);
  - rail wall x 18.35–22.35, z 6–17.75 (r 2 root fillet behind it);
  - 2 × Ø2.7 M3 pilots 14 deep in the bulkhead top at (6.75, −23) and (6.75, 14);
  - 2 × Ø2.2 flat-topped teardrop M2.5 pilots 10 deep in the wrist plate's front edge at (y ±24, z 3).
- Fasteners used: wrist horn: M2 × 12 + Ø6 × 0.5 washer from the pad's front face at (0, 0), 12 − 0.5 − 6.3 − 0.6 = 4.6 mm into the spline, fitted BEFORE the claw servo (its body covers the screw), + 1 × M2 × 6 self-tapper through the horn arm; claw MG90S: 2 × M2 × 8 self-tapping (5.5 mm engaged), the lead-end tab's slit filed to 2.1 mm; cover: 2 × M3 × 10 (or 2 × M3 × 18 button heads through the camera mount) into the top pilots, 2 × M2.5 × 12 pan head (head ≤ Ø5) into the front pilots.

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Claw-servo axis | y 0, z 27.25 | ±0.2 | sets the gear mesh |
| Bulkhead front face (tab seat) | x 10.0 | ±0.2 | sets the pinion's back face, x 22.6 |
| Wrist plate top (rack B's guide) | z 6.0 | ±0.15 | rack B rides on it (the gear's separating force seats it) |
| Rail wall front face | x 22.35 | ±0.15 | 0.25 sliding gap behind rack B |
| Wrist plate front edge | x 32.85 | ±0.15 | the cover's front plate slides down it |
| MG90S window | 23.0 × 12.6 printed | +0.3/−0 | clearance |
| Wrist clamp floor | 6.3 | ±0.2 | M2 × 12 reaches 4.6 into the spline |
| Bulkhead top (the cover's top-wall datum) | z 48.45 (prints 48.4) | ±0.1 | the cover's top wall stands 0.05 over it in CAD; must stay off a 0.2 mm slice plane |

Servo and camera dimensions are nominal (`tools/hobby_parts.py`, `claw_frame.py`). The MG90S has its own spec since deep review 01: body 22.8 × 12.2 mm, case bottom 18.5 mm below the tab underside, spline top 14.0 mm above it, lead leaving the shaft end 5.1 mm above the case bottom. Measure yours (body length and width, tab-hole spacing, shaft to near end, those heights, the lead exit, the tab slits) and give Claude any body-size difference over 0.1 mm or any other over 0.3 mm. Brio 4K: 27 × 102 × 27 mm, 63 g with its clip removed, 1/4"-20 thread centred on the bottom, USB-C on its back.

## 4. Loads
Design loads come from the MG90S's 6 V stall torque (≈216 N·mm), the stalled servo being the worst case the claw sees: the 20-tooth pinion (pitch radius 10 mm) then pushes **21.6 N** into the racks, **10.8 N per jaw** when both jaws touch the object, or the full **21.6 N on one jaw** when an off-centre object stops one jaw first. (A real stall grip is 6–8.5 N per finger, because the finger's moment presses the rack onto its guides: deep review 03 SYS-15. The stall figures stay the design loads.) Plus the arm cases: a **5 N sideways push** and a base-yaw stall of up to **12 N** at the fingertip. The end effector beyond the wrist horn weighs ≈209 g with the camera (≈224 g with solid parts; `../20261025-robot-arm-assembly/torque_budget.json`): claw printed parts and camera mount ≈115 g, claw MG90S 13.4 g, Brio 63 g, screws, horns, thumb screw and cable; ×3 for arm accelerations. The camera package hangs ≈80 mm outboard of the claw's back face (deep review 03 SYS-04), so its weight bends the wrist joint across its shaft in every pose. The Brio's USB cable can tug the camera with ≈10 N.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Wrist stall through the horn pocket | 216 N·mm | pocket walls in bearing | short-term | seconds |
| Claw-servo stall reaction | 216 N·mm about x | 2 tab screws into the bulkhead | short-term | seconds |
| Rack B back thrust (one jaw blocked) | ≈28 N (the couple of the 21.6 N grip) | rail wall and wrist plate, in their planes | short-term | seconds |
| End effector weight | 224 g × 3 g (solid parts) | wrist plate bending, bulkhead root | cyclic | hours |
| Camera's sideways moment on the wrist joint (SYS-04) | 108 N·mm, 124 N·mm with 50 g (solid parts), about the wrist servo's case-top plane | horn clamp preload, wrist plate round the pocket | sustained (every pose) | hours |
| Sideways push / yaw stall at the fingertip | 5 N / 12 N | wrist plate out of plane, horn clamp | short-term | seconds |
| USB cable tug | 10 N at the camera | camera mount → 2 top screws into the bulkhead | short-term | seconds |

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
- [ ] The MG90S goes into the window from the front, case bottom first, with its lead ribbon in the notch, without force; both tab screws bite (the lead-end one through the filed slit)
- [ ] **Screw-strip check (user decision 26 Oct 2026).** The strips between the MG90S window and its tab pilots are under fdm-design-rules' 1.8 mm, like every closed MG90S window in the three robots. The user kept them and asked for this check instead: drive both M2 × 8 tab screws snug on the first printed frame and look at both strips. Pass: no whitening, no crack. If either fails, stop before printing again: the pilots move out with the tab slits filed to match
- [ ] Wrist horn seats flat in its pocket; the M2 × 12 clamps the frame without the screw bottoming in the spline
- [ ] Rack B slides along the wrist plate with no binding
- [ ] `claw_sequence_check.py` (run by `assembly_check.py`): 0 mm³ on every insertion path and over the 0–44 mm stroke
- [ ] **Proof test (claw strength round 2, 1.5 × the design loads; the claw opening against an obstacle stays a design case):** Claw fully assembled with the camera, wrist horn clamped in a vice, servo powered and holding.
  1. Jaws at 30 mm: pull jaw B's fingertip (3 mm from the tip) away from jaw A with **32 N** (3.3 kg on a luggage scale, 1.5 × the one-jaw stall force), 10 s. Then push it towards jaw A with **32 N** (1.5 × the opening stall), 10 s. Repeat with the jaws closed, pulling only. At 30 mm a slipping servo can't run the rack out of mesh.
  2. **15 N** (1.5 kg) on the Brio's USB plug, 10 s each along +x (towards the fingers), ±y and ±z.
  3. **20 N** (1.5 × the 13 N desk hit) on the end face of the Brio, along its length, 10 s each way.
  4. 7.5 N at the fingertips, sideways (±z) then ±y, 1 min each.

  Pass:
  - no crack or whitening at the rail block's rack-side root (along it and at its +y end), the V-groove's flanks and the anchor pilot's mouth on the block top, the horn pocket, the clamp washer's seat (washer flat on the pad), the bulkhead root, the rib roots on the pad and the washer relief's foot, the window's corners and strips, or any screw pilot (the tab-pilot strips included);
  - the frame doesn't lift off the horn;
  - the fingertips return to within 0.5 mm.
## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`; claw assembly order and fit: `claw_sequence_check.json`.

# Part spec: Femur (×6)

Job: 20261026-hexapod-femur · Written by: Architect · Date: 2026-10-26 (round 3: §1–4 and §8 updated by design-lead after strength round 1 and the deep review) · Assembly: [20261026-hexapod-assembly](../20261026-hexapod-assembly/assembly_plan.md)

## 1. Function
7 mm flat plate from the femur MG90S horn to the knee (45 mm), carrying the tibia MG90S. The tibia servo is mounted **reversed** (deep review B1, option 2): its tabs sit on the femur's back face and its case and lead stay behind the femur, so the lead never crosses the plate.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 64.9 × 19 × 7 mm.
  - Femur horn: SG90/MG90S arm-horn pocket (2 deep, 5 mm floor) and a Ø2.6 CAD clamp hole.
  - Tibia servo: MG90S window **23.2 × 12.8 CAD** at x 27.9–51.1 (knee at x 45), with 2 × Ø1.7 CAD pilots slotted 0.4 mm outward at x 25.6 and 53.4. Its tabs rest on the back face (the bed face); its spline comes out of the front face.
  - Tibia lead: a 3.2 × 1.8 tie slot at (20, −6) (SYS-5).
  - The tibia's back face is 3.1 mm off the femur's front face.
- Fasteners used:
  - Femur horn: **M2 × 12** centre screw (M2 × 10 if the shaft thread bottoms before 6.5 mm) + Ø6 washer, driven **snug, ≈ 0.05 N·m** (strength round 1), plus 1 anti-rotation screw through the horn arm.
  - Tibia servo: 2 × **M2 × 8** self-tapping tab screws from the back, 5.5 mm into the plate.

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Femur axis → knee | 45.0 | ±0.3 | leg geometry |
| Tibia-servo window | 23.0 × 12.6 printed (23.2 × 12.8 CAD) | +0.3/−0 | 0.1 end / 0.2 side clearance |
| Side walls beside the window | 3.1 | ±0.2 | strength (rails) |
| Floor under the horn pocket | 5.0 | ±0.2 | clamp pull-through |

Servo dimensions are nominal. Since the deep review (B2, S1) the MG90S has its own spec in `tools/hobby_parts.py`:
- body 22.8 × 12.2 mm;
- spline top 14.0 mm above the tab underside;
- case bottom 18.5 mm below it;
- tab holes 27.8 mm apart.

Measure your MG90S (`BUILD_GUIDE.md` §3 step 1). Give Claude any difference over **0.1 mm** in body length or width, or over 0.3 mm elsewhere: the window ends have only 0.1 mm clearance each.

## 4. Loads
Load cases as strength round 1 re-derived them (`strength.md`, "Load cases"); the earlier 0.6 kg and 4 N per foot were 40 % low (deep review SYS-2).

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Robot on a tripod (683 g, lone leg 41.5–43.3 %) | **2.90** up at the foot | in-plane bending (19 mm deep section), torsion from the tibia's offset | sustained (SF 4) | minutes |
| Walking (× 2) | **5.80** per foot | as above | cyclic (SF 4) | hours |
| Foot scrub | µ 0.5 × 2.90, capped by each servo's stall | foot | cyclic (SF 4) | hours |
| Femur and knee stalls | 216 N·mm each: pocket bearing; the knee stall into the tibia-servo tab pilots | pocket, pilots | short-term (SF 3) | seconds |
| Sideways shove | 3 at the foot, with 0–2.90 up | out-of-plane bending, horn clamp | short-term (SF 3) | seconds |
| 20 cm drop | **19.2** up per foot (servo back-drive cap) + ≤ 6.2 inward | foot | short-term (SF 3) | impact |
| Assembly | M2 clamp screw snug 0.05 N·m ≈ 125 N preload | Ø6 washer on the 5 mm floor | short-term (SF 3) | — |

Round 3 changes two things for the femur:
- **The tibia sits closer.** Its mid-plane is now **10.1 mm** in front of the femur's (the strength check had 16.4), which lowers the torsion that governed the service rows.
- **Tab screw direction.** The tibia servo's tab screws go in from the back, so a sideways push towards the coxa loads them in pull-out instead of bearing; the magnitudes are those already checked.

Round-3 mass (812–877 g) raises the walking and servo loads by 19–28 %; the drop is capped by the servos.

## 5. Environment
- Max temperature (°C): 40 (indoor floor; MG90S cases warm under load)
- Outdoor / UV: no
- Chemicals, oils, moisture: none

## 6. Material
- Preferred or required: PETG (designer's choice; the user left material to the designer)
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA (creep under constant servo-holding load); TPU only as optional foot socks

## 7. Quantity and time
- Quantity: 6
- Max acceptable print time per batch (h): 3

## 8. Acceptance criteria (measurable)
- [ ] The tibia MG90S goes into the window from the back, spline first; its tab screws bite from the back
- [ ] **Proof test (strength round 3):**
  1. **Set-up.** Fit the femur on its horn on an MG90S clamped in a vice, with the M2 × 12 clamp screw **snug (0.05 N·m)**. Fit the tibia servo and the tibia, with the femur level and the tibia hanging straight down. Put a stop **above the femur's rear end** (behind the horn), so the femur servo's gears do not carry the moment.
  2. **Load.** Hang **1.5 kg** from the foot tip for **1 min** (2 × the walking foot load at 906 g). With the tibia vertical, this loads the femur root like the foot does, torsion included. Then turn the servo over in the vice, move the stop to the other side, and repeat: a hanging weight pulls the foot opposite to the ground's push, and the horn clamp tips on a different side each way.
  3. **Shove.** Push **6 N** sideways at the foot tip, each way, for 10 s (1.5 × the 4.0 N a coxa stall puts there).

  Pass:
  - no cracks or whitening at the pocket, the window corners or the pilots;
  - no gap over 0.2 mm (feeler gauge) between the femur and the horn;
  - after unloading, the knee returns to within 0.3 mm of where it started.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

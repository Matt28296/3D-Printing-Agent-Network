# Part spec: Coxa bracket (×6)

Job: 20261026-hexapod-coxa · Written by: Architect · Date: 2026-10-26 (round 3: §1–4 and §8 updated by design-lead after strength round 1 and the deep review) · Assembly: [20261026-hexapod-assembly](../20261026-hexapod-assembly/assembly_plan.md)

## 1. Function
L-shaped bracket under the coxa MG90S horn: a hub plate round the horn and an arm (outside the femur's swing plane) out to a 10 mm vertical plate that carries the femur MG90S with its axis horizontal and tangential, 32 mm out from the coxa axis. Each leg hangs on its coxa servo's output shaft through this bracket.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 60.1 × 30.5 × 41.0 mm.
  - Coxa horn: SG90/MG90S arm-horn pocket, 2 deep, with a **6 mm floor**, and a Ø2.6 CAD clamp hole on the bed face.
  - Femur servo: MG90S window **23.2 × 12.8 CAD** with a 45° roof in the **10 mm** vertical plate (femur axis 32 out and 20 below the back face). It has a **lead notch 4.4 × 1.6** at its outboard end and 2 teardrop pilots; the outboard pilot sits **1.3 mm further out** than the tab hole (deep review B1, option 1).
  - Vertical plate: **13 mm posts** beside the window, R1 T-bone reliefs at the window floor's corners, a 45° × 4.9 mm root gusset along the whole plate on the tab side, a **45° × 8 mm ramp** where the plate's inner end meets the hub, and a 6 mm 45° cut on the plate's outer top corner (print).
  - Hub and arm widened to y −23.5; r2.5 fillet where the arm leaves the hub.
  - A 1.8 × 3.2 tie slot through the outer post for the femur and tibia leads (deep review SYS-5).
- Fasteners used:
  - Coxa horn: **M2 × 12** centre screw (M2 × 14 if the shaft thread is 7.5 mm deep or more), with an **M3 penny washer Ø10 × 1** under its head, from below. Stack: washer 1 + floor 6 + the measured spline thread. Drive it **snug, ≈ 0.05 N·m**. Plus 1 anti-rotation screw through the horn arm.
  - Femur servo: 2 × **M2 × 10** self-tapping tab screws, 7.5 mm into the plate. The outboard one goes through that tab's slit, filed open to 2.1 mm.

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Coxa axis → femur axis | 32.0 radial | ±0.3 | leg geometry |
| Femur axis depth | 20.0 below the back face (Z_F = T_C + 12) | ±0.3 | leg geometry (stance: bottom-plate underside 94.1 above the ground) |
| Vertical plate | 10.0 thick, posts 13.0 wide | +0.3/−0 | strength (posts ≥ 12.5) |
| Floor under the horn pocket | 6.0 | ±0.2 | strength (clamp pull-through) |
| Femur-servo window | 23.2 × 12.8 CAD (≈ 23.0 × 12.6 printed) | +0.3/−0 | 0.1 end / 0.2 side clearance |
| Lead notch | 4.4 wide CAD, 1.6 beyond the case end | +0.3/−0 | lead root passes |
| Outboard pilot | 9.7 from the femur axis (tab hole + 1.3) | ±0.2 | screw through the filed slit; ligament to the notch 1.35 CAD |

Servo dimensions are nominal. Since the deep review (B2, S1) the MG90S has its own spec in `tools/hobby_parts.py`:
- body 22.8 × 12.2 mm;
- spline top 14.0 mm above the tab underside;
- case bottom 18.5 mm below it;
- tab holes 27.8 mm apart.

Measure your MG90S (`BUILD_GUIDE.md` §3 step 1). Give Claude any difference over **0.1 mm** in body length or width, or over 0.3 mm elsewhere: the window ends have only 0.1 mm clearance each.

## 4. Loads
Load cases as strength round 1 re-derived them (`strength.md`, "Load cases"; the same block in all five hexapod checks). The spec's earlier 0.6 kg and 4 N per foot were 40 % low (deep review SYS-2).

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Robot on a tripod (683 g, lone leg 41.5–43.3 %) | **2.90** up at the foot: hub moment ≈ 2.90 × 78.6 = 228 N·mm | foot: 77 out, 15.8 to the side, 87 below the back face | sustained (SF 4) | minutes |
| Walking (× 2) | **5.80** up at the foot: hub moment ≈ **440–456 N·mm**; vertical plate out of plane ≈ 177 N·mm | as above | cyclic (SF 4) | hours |
| Foot scrub | µ 0.5 × 2.90 in the worst horizontal direction, capped by each servo's stall | foot | cyclic (SF 4) | hours |
| Servo stalls | 216 N·mm per joint: femur ±4.8 N vertical at the foot, coxa 2.8 N tangential, knee 3.1 N radial, with 2.90 N up; each stall straight into its horn pocket and tab screws | foot, horn pocket, femur-servo tab screws | short-term (SF 3) | seconds |
| Sideways shove | 3 in any horizontal direction, with 0–2.90 up | foot | short-term (SF 3) | seconds |
| 20 cm drop | **19.2** up per foot (femur and knee servos back-drive at ≈ 2 × stall), plus ≤ 6.2 inward | foot | short-term (SF 3) | impact |
| Assembly | M2 clamp screw snug 0.05 N·m ≈ 125 N preload | Ø10 washer on the 6 mm floor | short-term (SF 3) | — |

Round-3 mass: the strength set and the 6 mm bottom plate make the robot 812 g (877 g with solid parts). Every walking and servo load above rises by 19–28 %; the drop is capped by the servos and does not change. Each leg hangs on its coxa servo's shaft alone: 194 N·mm of bending at 812 g in the walking stance (deep review SYS-6).

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
- Max acceptable print time per batch (h): 6

## 8. Acceptance criteria (measurable)
- [ ] The femur servo's lead root passes the notch as the case goes in; the outboard tab screw reaches its pilot through the filed slit; both tab screws bite
- [ ] The femur swings −70 … +90° without touching the bracket (assembly check)
- [ ] **Proof test (strength round 1, for the redesigned bracket):**
  1. Assemble one leg (coxa servo, bracket, femur, tibia) with the clamp screws snug (0.05 N·m).
  2. Power the servos at 6 V in the neutral pose and clamp the coxa servo body in a vice.
  3. Hang **0.45 kg** (4.4 N, 1.5 × the static tripod share) from the foot tip for **10 min**. The femur servo then holds about 200 N·mm, still under its stall torque.
  4. Push **3 N** sideways at the foot tip, each way, for 10 s.
  5. Finally run the body-bottom spec §8 drop test: 3 × 20 cm landing flat on 6 feet, then 3 × 20 cm tilted so it lands on 3.

  Pass:
  - no whitening or cracks at the post roots, reliefs, gusset tip, pilots or hub ramp;
  - no gap over 0.2 mm (feeler gauge) between the bracket and the coxa horn;
  - after unloading, the foot returns to within 0.5 mm of where it started.
- [ ] **Coxa shaft (deep review SYS-6):** run the leg proof test in the assembly `spec.md` §8 on the same leg: 680 g at the foot for 10 min, foot play under ±1 N before and after 30 min of walking. Pass: the play grows by under 1 mm, with no clicking or skipped teeth.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

VERDICT: FAIL

# Strength check: 20261026-rover-chassis (round 3)

strength-analyst (independent) · 2026-10-26 · run with the CAD venv: `source /home/claude/.venv-cad/bin/activate`, then `python3 jobs/20261026-rover-chassis/strength_calc.py` (13 s; it builds the round-3 chassis with build123d and recomputes the rover mass from every rover `part.stl`)

**Result: FAIL.** 5 of 35 verdict rows are below their required SF. Every failure is in the idler mount or the motor nacelle's 1 mm skin, both new or changed in round 3. The concept-C pocket, housing and trough, the road-wheel axles, the jack screw's thread, the floor and the insert columns all pass.

| Row | What fails | SF | Required |
|---|---|---|---|
| B6 | Idler clamp yaw at a reverse stall: the Ø9 washer edge crushes the PETG | **0.60** (lowest) | 3 |
| B5 | Idler clamp yaw under the 5 N pretension: creep | 1.50 | 4 |
| B4 | Idler sliding nut on its slot roof, 5 cm front-corner drop | 2.14 | 3 |
| C1 | 1 mm skin, in-plane (diaphragm) shear across layers, 5 cm rear corner | 2.91 | 3 |
| C2 | Nacelle wall root, 5 cm rear corner, at the walls' upper load share | 2.55 | 3 |

- **The idler failures are mechanism problems, not marginal numbers.** The jack screw holds the idler bolt's force, but not its moment. The bolt sits in a slot, so the moment about Z from the track pull can only go through the clamp faces, and both faces bear on PETG with the slot cut through their middle. Round 2's friction check didn't cover this moment.
- **Consequence.** The idler leans back and the track slowly loses tension. Nothing breaks.
- **Fixes.** All three changes below are geometry or hardware changes with checked SFs.

## Round-2 required changes: what round 3 did

| Round 2 change | Round 3 | Result |
|---|---|---|
| 1. Fully threaded axle bolts, class 8.8 or better (12.9 recommended), grade named | Class 12.9, fully threaded, M3 × 50 (wheels) and M3 × 40 (idlers), named in spec §2 and the BOM | ✓ A6 SF 2.66, B11 2.66, B10 1.79 (required 1.5). The grade matters: fully threaded **A2-70** gives 1.11 at the 5 cm drop, and the 5 kg proof test would bend it (0.72). Class 8.8 is the minimum. |
| 2. Ø26 road-wheel bosses with an r ≥ 1.5 fillet or a 2 × 45° chamfer at the boss-to-wall junction | Ø26 done. `BOSS_RIM_R` 1.5 went on the boss's *free face* edge, which has no structural effect. The 1.5 × 45° collar (`JOIN`) at the wall junction is what does the work. | ✓ A1 SF 3.51, at Kt 1.6 for the 1.5 mm chamfer (round 2 predicted 3.75 at Kt 1.5) |
| 3. `BOSS_IN` 5.5 at the wheel bosses and idler block; M3 × 50; `STRAP_Y` 26 | Done | ✓ Wheel nut traps: A4 SF 3.22 (3.14 by round 2's lever model). Floor at the strap slots: D2 6.08. **Not fixed for the idler** (B4): round 2 gave the idler slot the wheel trap's 13.2 mm² of nut bearing, but the sliding nut bears on its slot roof with its 3.18 mm flat only (7.6 mm²). |
| 4. Idler positive stop (M3 tensioner screw) | M3 × 20 jack screw on the bolt head, 6.5 mm of thread in a buttress | ✓ Thread strip-out B7 4.82 and B8 14.4 (coordinator item 2). ✗ The stop takes the force, not the moment, and sits at the head, which raises the clamp's moment from 22 R to 29.6 R: B5, B6. |
| 5. Cradle cheeks 4 mm, standing on the cradle | Made redundant by concept C. The journal lever is gone, and the V-trough walls now only carry the can's rear reaction. | ✓ C12 71 |

## Load cases

The shared block (identical in all six rover scripts) reads `rover_frame.py` and `tools/hobby_parts.py`.

| Load | Value used | Source, and how it differs from deep review 04 | Duration |
|---|---|---|---|
| Mass | **649 g** (W 6.37 N) | Spec §4. Checked in this script: **618 g** = printed parts at their `print_requirements` minima (voxel shell + infill, review S-18 method) 315 g + the round-3 BOM 304 g. All-solid prints would give 713 g. 649 g covers the estimate by 5 %. Review S-18 gave 577–599 g for the round-2 parts. | n/a |
| Stall torque | **160 N·mm** design → 9.89 N pull. 182 N·mm proof → 11.25 N. | Spec §4, against S-08's 6.6–13.6 N per side "at the 80 % cap". Round 3 changed two things: the sketch now caps the *average motor voltage* at 6.0 V (`rover_test.ino`: `MOTOR_V` 6.0, `pwmCap = 255 × 6.0 / V_pack`), and chassis §8 now **gates** the motor (≤ 371 g at 50 mm, 100 % PWM, fresh pack = 182 N·mm). At the 6 V cap the S-08 motors give 6.7–12.1 N, and a motor that passes the gate gives ≤ 130 N·mm = 8.0 N. 160 N·mm covers service with margin. An ungated 2 kg·cm motor (S-08 Phipps: 196 N·mm, 12.1 N) is shown as advisory rows. | short-term |
| Pretension | 5 N per run, sustained | Spec §4. S-16: the guide's 3–5 mm sag over a 40 mm span is about 0.1 N, so 5 N is an over-tension bound. Only B5 depends on it (see below). | sustained |
| Track | Tight run at stall 14.9 N (proof 16.2). Sprocket radial 19.9 stall / 13.2 cyclic / 10 sustained. Idler at a reverse stall 29.8 N, both runs tight (proof 32.5). | T0 + pull, with no slack-side relief (upper bound) | as stated |
| 5 cm drop | **31.8 N per axle, every axle** | E = m·g·h = 0.318 J with rounds 1–2's 5 mm stopping distance (spec §4), giving 127 N in total. S-15 shows the sprocket and idler sit 1.29 mm above a straight run, so a flat landing loads only the 4 road wheels: 31.8 N each, not 15.9 N on 8 axles. That equals the corner value (half the mass on 2 axles). Sensitivity: 2.5 mm doubles it (63.7 N). An elastic estimate with a rigid floor and the M3 axles as the only spring gives about 176 N per axle, so the convention relies on floor, track and body compliance. **The drop test is the evidence for the 5 cm rating.** | short-term |
| Side | 3 N per track | Spec. S-15's pivot turn on carpet needs at most 1.43 N per track half. | cyclic |
| Motor reaction | 160 N·mm (182 proof) on the gearbox in its pocket | Spec §4 | short-term |
| Handling | Rover lifted by the lid: 2 × W on 4 inserts, 3.2 N each | Added | short-term |
| Assembly | Axle-bolt tightening; jack screw self-tapping; inserts | Added (advisory rows and notes) | once |

## Assumptions (this part)

**Geometry**
- From `model.py`, `rover_frame.py` and the build123d solid in the rover frame.
- Nacelle ring at |y| 43.5: A 107.2 mm², I 3280 mm⁴, c 10.89 (OCP section).
- Trough cheeks from the |y| 24 section.
- The printed pocket is 12.2 × 10.2 (CAD minus `HOLE_COMP`). The skin hole prints Ø4.5.

**Axle bolts and the wall**
- No preload is credited, because PETG creep removes it (rounds 1–2).
- The bolt is treated as a rigid pin on a Winkler foundation. Checks use the mean bearing over each contact zone: the nut in its trap (5.5 wide; the idler's sliding nut 3.18) and the shank at the inner hole edge. Peaks are advisory.
- Wall bending round a boss or block uses the rigid-inclusion plate model of rounds 1–2, m = M/(2πa).
- Stress concentration:
  - Kt 1.6 at the 1.5 × 45° collars and strips (`JOIN`). A 1.5 mm chamfer leg is roughly an r 1.1 fillet, which is 0.25 t, so Kt 1.5 by the skill; +0.1 because a chamfer is a little worse than a fillet (round 2).
  - Kt 2.5 at sharp corners (skill; coordinator ≥ 2).

**Idler clamp (B5, B6)**
- The slot has no edges along X, so the bolt's moment about Z from the rearward track pull R (applied at |y| 55) goes through the clamp faces.
- The jack screw pushes at the head (|y| 25.4), so the clamp must carry M = 29.6 R. A friction-held bolt would see 22 R.
- The head side takes 95 % of it, in proportion to the footprints' I:
  - Ø9 washer on the block face minus the 4.35 mm slot band: A 26.3 mm², I 90.3 mm⁴, x 4.12, so I/x = 22 mm³;
  - sliding nut beside the slot: 4.3 mm², I 4.8.
- Clamp left after creep: 100 N (round 2). Pressure P/A + M·x/I. That is a lower bound once the joint opens, which happens above 83 N·mm.

**Motor in its pocket (concept C)**
- The motor is a rigid body.
- **Vertical loads (drop):** the can rests on the open V-trough back to its end at |y| 20.5. A triangular reaction centres at |y| 28.7, so the nacelle carries **1.61 R**.
- **Horizontal (track) loads:** the open trough can't push the can sideways without lifting it off the V, against only the zip tie. The rear reaction is therefore at the pocket's inner end, so **1.87 R** (spec §4's figure) applies.
- The gearbox front edge bears 0.3 mm inside its face, allowing for its edge radius.

**Nacelle and skin split (C1, C2)**
- The reaction reaches the housing in one of two ways:
  - through the two upper 2 mm nacelle walls bending as 2.7 mm cantilevers: 1671 N/mm, bending and shear;
  - through the 1 mm skin acting as a diaphragm that spreads it to all four walls: 2075 N/mm, as a shear panel of two 4.96 mm ligaments beside the hole, 6.38 mm tall.
- Each row takes the end of the stiffness range that is worse for it:
  - skin share 55 % (walls × 1, skin × 1);
  - wall share 67 % (walls × 1.5 for fold-line restraint, skin × 0.6 for its bending and the hole).
- Peak skin shear is 1.5 × the mean over the net cut. The hole's 4τ hoop stress at 45° gives the same SF within 3 %.
- The skin is a vertical 1 mm wall, so its in-plane shear acts on layer interfaces: across-layer shear allowable.
- **Nacelle root Kt (coordinator item 1).**
  - The gearbox can only push the walls outward. The tension side of their bending at the housing face is the pocket face, which runs straight through with no notch, so Kt 1.
  - The sharp outer corner is in compression for that load. It is in tension only under tube bending (C3), where Kt 2.5 is applied.

**Skin out of plane (C9, C10)**
- Modelled as an annular plate, clamped at the area-equivalent circle of the printed pocket (r 6.29) and free at the Ø4.5 hole.
- The solver reproduces the classical clamped-plate results: P/(4π) for a central load and P/(8π) for a uniform load.

**Jack screw (B7–B9)**
- Self-tapped into the Ø2.6 printed pilot, with 6.5 mm in the buttress.
- Thread fill 0.5 (rounds 1–2), and 270° of thread (teardrop).
- The shear cylinder crosses layer interfaces, so the across-layer shear allowable applies.

**Mass**
- Bought-part masses come from `hobby_parts` where it gives one (N20 10 g, hub 2.8 g, battery 135 g), otherwise catalogue values. The list is printed by the script.

## Allowables and sources (all six rover jobs)

- **No measured data.** `library/materials.csv` has only its header row, and no job has a datasheet in `inputs/`. The skill's placeholders apply: PETG 25 MPa in-plane, 12.5 MPa across layers, E 1.8 GPa, ν 0.35. Shear allowable is 0.5 × normal (Tresca, as in rounds 1–2). **PASS is not possible; NEEDS_TEST is the best verdict.**
- **Direction.** Compressive bearing on layer faces and on 45° flanks uses the in-plane value. Anything that pulls layers apart or shears along a layer interface uses the across-layer value. Infill crush uses the cellular-solid scaling of 25·ρ^1.5.
- **Required SF.** 3 for short-term static loads, 4 for cyclic or sustained loads, 1.5 on yield for bought steel, and 1.0 on the knocked-down allowable for proof loads.
- **Steel.** Class 12.9: 1080 MPa; 8.8: 640; A2-70: 450. Unspecified rod and the N20 shaft: 350 MPa (conservative).
- **Temperature.** 40 °C service against a PETG softening point of about 70 °C, so more than 20 °C apart.

## Results (`strength_calc.py` output)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | A1 road-wheel boss: wall bending at the collar, 5 cm drop 31.8 N (Kt 1.6) | Z | 3.56 | 12.5 | 3.51 | 3.0 | OK |
| 2 | A2 road-wheel boss: weight share 1.9 N sustained (Kt 1.6) | Z | 0.21 | 12.5 | 58.58 | 4.0 | OK |
| 3 | A3 road-wheel boss: side drag 3 N at the flange r16.1 (Kt 1.6) | Z | 0.28 | 12.5 | 44.59 | 4.0 | OK |
| 4 | A4 road-wheel nut-trap bearing (rigid bolt on PETG, mean over the nut), 5 cm drop | XY | 7.75 | 25.0 | 3.22 | 3.0 | OK |
| 5 | A5 road-wheel inner hole-edge bearing (mean over the loaded 5.1 mm), 5 cm drop | XY | 5.72 | 25.0 | 4.37 | 3.0 | OK |
| 6 | A6 M3 x 50 class 12.9 bending at the outer face, 5 cm drop x 17 | steel σy 1080 | 405.30 | 1080.0 | 2.66 | 1.5 | OK |
| 7 | B1 idler block: wall bending, 5 cm front corner 31.8 N (Kt 1.6 top strip) | Z | 3.31 | 12.5 | 3.77 | 3.0 | OK |
| 8 | B2 idler block: wall bending, reverse stall 29.8 N (Kt 2.5: sharp rear corner) | XY | 4.84 | 25.0 | 5.16 | 3.0 | OK |
| 9 | B3 idler block: wall bending, pretension 10 N sustained (Kt 2.5) | XY | 1.63 | 25.0 | 15.38 | 4.0 | OK |
| 10 | B4 idler sliding nut on its slot roof (flat 3.18 x 2.4), 5 cm front corner | XY | 11.68 | 25.0 | 2.14 | 3.0 | **FAIL** |
| 11 | B5 idler clamp yaw: Ø9.0 washer edge on PETG, pretension 10 N sustained (P 100 N) | XY | 16.62 | 25.0 | 1.50 | 4.0 | **FAIL** |
| 12 | B6 idler clamp yaw: washer edge, reverse stall 29.8 N | XY | 41.97 | 25.0 | 0.60 | 3.0 | **FAIL** |
| 13 | B7 jack-screw thread strip-out (6.5 mm, Ø2.6 pilot), reverse stall 29.8 N | Z shear | 1.30 | 6.2 | 4.82 | 3.0 | OK |
| 14 | B8 jack-screw thread, pretension 10 N sustained | Z shear | 0.44 | 6.2 | 14.36 | 4.0 | OK |
| 15 | B9 buttress lug at the block face (y 28): bending, reverse stall (Kt 2.5) | XY | 1.96 | 25.0 | 12.73 | 3.0 | OK |
| 16 | B10 idler M3 x 40 class 12.9: bending at the head face (y 28), reverse stall x 27 | steel σy 1080 | 602.13 | 1080.0 | 1.79 | 1.5 | OK |
| 17 | B11 idler M3 x 40 class 12.9: bending at the outer face, 5 cm front corner x 17 | steel σy 1080 | 405.30 | 1080.0 | 2.66 | 1.5 | OK |
| 18 | C1 skin (1 mm) diaphragm shear across layers, 5 cm rear corner: nacelle reaction 51.3 N, skin share 55 % | Z shear | 2.15 | 6.2 | 2.91 | 3.0 | **FAIL** |
| 19 | C2 nacelle wall root bending (pocket face in tension, no notch), 5 cm rear corner, wall share 67 % | XY | 9.82 | 25.0 | 2.55 | 3.0 | **FAIL** |
| 20 | C3 nacelle root, tube bending (sharp outer corner in tension, Kt 2.5), 5 cm rear corner | XY | 1.15 | 25.0 | 21.73 | 3.0 | OK |
| 21 | C4 nacelle root, tube shear (2 V/A), 5 cm rear corner | Z shear | 0.96 | 6.2 | 6.53 | 3.0 | OK |
| 22 | C5 gearbox front edge bearing on the pocket faces (1 mm x face width), 5 cm rear corner | XY | 3.63 | 25.0 | 6.89 | 3.0 | OK |
| 23 | C6 skin diaphragm shear, track stall 19.9 N (horizontal, 1.87 R) | Z shear | 1.56 | 6.2 | 4.02 | 3.0 | OK |
| 24 | C7 nacelle wall root bending, track stall 19.9 N | XY | 7.11 | 25.0 | 3.51 | 3.0 | OK |
| 25 | C6 skin diaphragm shear, track pretension 10 N sustained (horizontal, 1.87 R) | Z shear | 0.78 | 6.2 | 7.99 | 4.0 | OK |
| 26 | C7 nacelle wall root bending, track pretension 10 N sustained | XY | 3.58 | 25.0 | 6.99 | 4.0 | OK |
| 27 | C8 reaction torque 160 N*mm: gearbox corner bearing (13.3 N over 9 x 1 mm) | XY | 1.48 | 25.0 | 16.88 | 3.0 | OK |
| 28 | C9 skin out of plane: side 3 N inward on the thrust washer (annular plate a 6.29, hole r 2.25) | Z | 1.64 | 12.5 | 7.62 | 4.0 | OK |
| 29 | C10 skin out of plane: side 3 N outward on the gearbox face (Kt 2.5 at the pocket corner) | Z | 1.76 | 12.5 | 7.11 | 4.0 | OK |
| 30 | C11 wall bending round the motor housing (Ø22.4 equivalent, Kt 1.6), 5 cm rear corner | Z | 3.09 | 12.5 | 4.04 | 3.0 | OK |
| 31 | C12 trough cheek bridge over the tie tunnel: tie 47 N (can rear reaction 17.3 N + 30 N preload) | XY | 0.35 | 25.0 | 71.23 | 3.0 | OK |
| 32 | D1 floor mid-span under the battery, 5 cm (20 g x 135 g) | XY | 3.69 | 25.0 | 6.77 | 3.0 | OK |
| 33 | D2 floor at the strap slots \|y\| 26.0 (Kt 2.5, square ends), 5 cm | XY | 4.11 | 25.0 | 6.08 | 3.0 | OK |
| 34 | E1 insert knurl shear-out of the column, lifted by the lid 3.2 N per insert | Z shear | 0.04 | 6.2 | 140.63 | 3.0 | OK |
| 35 | E2 column tension (Z) round the insert, lifted by the lid | Z | 0.05 | 12.5 | 259.06 | 3.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, fixes, proof loads, bought parts):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| A4/A5 Winkler peaks: nut edge 10.4, inner hole edge (peak), 5 cm drop | XY | 11.43 | 25.0 | 2.19 | 3.0 | no |
| A4 round-2 lever model (inner contact 1.5 mm at the boss face), nut bearing, 5 cm drop | XY | 7.96 | 25.0 | 3.14 | 3.0 | OK |
| proof 5 kg (49 N) at the wheel rim centre: boss collar | Z | 5.48 | 12.5 | 2.28 | 1.0 | OK |
| proof 5 kg at the wheel rim centre: nut-trap bearing | XY | 11.95 | 25.0 | 2.09 | 1.0 | OK |
| proof 5 kg at the rim centre: M3 class 12.9 at the outer face | steel σy 1080 | 624.50 | 1080.0 | 1.73 | 1.0 | OK |
| if A2-70 (fully threaded stainless) bolts are fitted instead: 5 cm drop | steel σy 450 | 405.30 | 450.0 | 1.11 | 1.5 | no |
| if A2-70 bolts are fitted: proof 5 kg at the rim centre | steel σy 450 | 624.50 | 450.0 | 0.72 | 1.0 | no |
| proof 5 kg on the idler bolt (chassis §8 test 1): sliding nut on its slot roof | XY | 18.00 | 25.0 | 1.39 | 1.0 | OK |
| idler clamp yaw at the reverse-stall proof (32.5 N, 100 % PWM fresh pack) | XY | 45.45 | 25.0 | 0.55 | 1.0 | no |
| idler clamp yaw if the preload held 350 N (joint just closed at T0): washer edge, pretension sustained | XY | 26.13 | 25.0 | 0.96 | 4.0 | no |
| idler sliding nut on its slot bottom under 100 N clamp (4.3 mm² beside the slot): creeps | XY | 23.51 | 25.0 | 1.06 | 4.0 | no |
| jack-screw thread, reverse-stall proof 32.5 N | Z shear | 1.41 | 6.2 | 4.42 | 1.0 | OK |
| BOUND buttress as a column off the floor only (6.5 x 11.5, Kt 2.5), reverse stall | Z | 8.73 | 12.5 | 1.43 | 3.0 | no |
| C1 BOUND skin carries all (rigid diaphragm), 5 cm rear corner | Z shear | 3.88 | 6.2 | 1.61 | 3.0 | no |
| C2 central split (walls x1, skin x1), 5 cm rear corner | XY | 6.56 | 25.0 | 3.81 | 3.0 | OK |
| C2 BOUND walls carry all (no skin), 5 cm rear corner | XY | 14.70 | 25.0 | 1.70 | 3.0 | no |
| C1 at the spec's lever 1.87 R (rear reaction at the pocket's inner end), 5 cm rear corner | Z shear | 2.49 | 6.2 | 2.51 | 3.0 | no |
| C2 at the spec's lever 1.87 R, 5 cm rear corner | XY | 11.39 | 25.0 | 2.20 | 3.0 | no |
| C9 skin, sideways friction in a corner drop (mu 0.3 x 31.8 N) on the thrust washer | Z | 5.22 | 12.5 | 2.39 | 3.0 | no |
| C8 reaction torque at the proof 182 N*mm | XY | 1.69 | 25.0 | 14.84 | 1.0 | OK |
| S-08 ungated 196 N*mm motor: jack-screw thread, reverse stall 34.2 N | Z shear | 1.49 | 6.2 | 4.19 | 3.0 | OK |
| S-08 ungated 196 N*mm motor: idler clamp yaw, reverse stall | XY | 47.67 | 25.0 | 0.52 | 3.0 | no |
| S-08 ungated 196 N*mm motor: skin shear, track stall (1.87 x 22.1 N) | Z shear | 1.73 | 6.2 | 3.61 | 3.0 | OK |
| N20 shaft (bought), arm 10, Z_min 1.911 mm³: stall 19.9 N | steel σy 350 | 104.07 | 350.0 | 3.36 | 1.5 | OK |
| N20 shaft (bought), arm 10, Z_min 1.911 mm³: 5 cm corner 31.8 N | steel σy 350 | 166.58 | 350.0 | 2.10 | 1.5 | OK |
| FIX SKIN 1 -> 1.5 (gearbox face \|y\| 44.5, shaft arm 10.5): skin shear, 5 cm corner | Z shear | 1.39 | 6.2 | 4.49 | 3.0 | OK |
| FIX SKIN 1 -> 1.5: rigid-diaphragm bound | Z shear | 2.59 | 6.2 | 2.42 | 3.0 | no |
| FIX SKIN 1 -> 1.5: nacelle wall root, 5 cm corner (L 2.2) | XY | 8.17 | 25.0 | 3.06 | 3.0 | OK |
| FIX SKIN 1 -> 1.5: N20 shaft at the 5 cm corner (arm 10.5) | steel σy 350 | 174.91 | 350.0 | 2.00 | 1.5 | OK |
| FIX SKIN 1 -> 1.5: N20 shaft at stall (arm 10.5; Architect's criterion SF >= 2) | steel σy 350 | 109.28 | 350.0 | 3.20 | 2.0 | OK |
| FIX SKIN 1 -> 2.0 (gearbox face \|y\| 44.0, shaft arm 11.0): skin shear, 5 cm corner | Z shear | 0.92 | 6.2 | 6.76 | 3.0 | OK |
| FIX SKIN 1 -> 2.0: rigid-diaphragm bound | Z shear | 1.94 | 6.2 | 3.22 | 3.0 | OK |
| FIX SKIN 1 -> 2.0: nacelle wall root, 5 cm corner (L 1.7) | XY | 6.78 | 25.0 | 3.69 | 3.0 | OK |
| FIX SKIN 1 -> 2.0: N20 shaft at the 5 cm corner (arm 11.0) | steel σy 350 | 183.23 | 350.0 | 1.91 | 1.5 | OK |
| FIX SKIN 1 -> 2.0: N20 shaft at stall (arm 11.0; Architect's criterion SF >= 2) | steel σy 350 | 114.48 | 350.0 | 3.06 | 2.0 | OK |
| FIX idler clamp, inner steel plate 21 x 10 x 2: PETG edge pressure, reverse stall | XY | 2.62 | 25.0 | 9.53 | 3.0 | OK |
| FIX idler clamp, outer nut plate 14 x 8 x 2 (nut slot 9 tall): PETG edge pressure, reverse stall (bolt 137 N) | XY | 3.87 | 25.0 | 6.47 | 3.0 | OK |
| FIX idler clamp, inner steel plate 21 x 10 x 2: PETG edge pressure, pretension sustained | XY | 1.44 | 25.0 | 17.36 | 4.0 | OK |
| FIX idler clamp, outer nut plate 14 x 8 x 2 (nut slot 9 tall): PETG edge pressure, pretension sustained (bolt 100 N) | XY | 2.35 | 25.0 | 10.62 | 4.0 | OK |
| FIX idler nut plate's top edge (14 x 2) on the slot roof, 5 cm front corner | XY | 2.68 | 25.0 | 9.33 | 3.0 | OK |
| FIX idler sliding nut alone: DIN 557 square nut 5.5 x 2.4 (full 5.5 top face), 5 cm front corner | XY | 7.75 | 25.0 | 3.22 | 3.0 | OK |
| NOT ENOUGH: DIN 9021 M4 Ø12 washer under the head, reverse stall | XY | 13.72 | 25.0 | 1.82 | 3.0 | no |
| assembly: road-wheel bolt tightened to 0.15 N*m (P 250 N): nut on the trap bottom (17.1 mm²) | XY | 14.60 | 25.0 | 1.71 | 3.0 | no |
| assembly: road-wheel bolt tightened to 0.5 N*m (P 833 N): nut on the trap bottom (17.1 mm²) | XY | 48.68 | 25.0 | 0.51 | 3.0 | no |

- Lowest SF: **0.60** (required 3.0), at B6, the idler clamp's yaw at a reverse stall.
- Drop rows meet their SF up to a **3.6 cm** drop, limited by B4. After changes 1 and 2 the limit is about **5.4 cm**, limited by A4 at SF 3.22.
- 5 of 35 verdict rows are below their required SF.

## Required changes

### 1. Idler bolt clamp (B4, B5, B6): a yaw restraint that doesn't creep, on both faces

**The requirement:**
- **Head side.** The yaw moment 29.6 R needs a bearing footprint on the block face of section I/x ≥ **112 mm³**. That gives SF 3 at the 29.8 N reverse stall. The Ø9 washer on the slotted face gives 22 mm³, and a Ø12 DIN 9021 M4 washer still only reaches SF 1.82.
- **Nut side.** It has to carry the clamp plus the prying tension: about 140 N at the reverse stall. Today it bears on 4.3 mm² beside the slot.

**One package that passes:**
- **(a) Inner plate.** A steel plate 21 × 10 × 2 mm, slotted 3.4 × 12, fixed on each idler-block face between x 108 and x 129 (clear of the buttress and the front 45° strip), with the bolt head on it:
  - B6 0.60 → **9.5**;
  - B5 1.50 → **17**.
  - Let it into a 2 mm recess in the block face, so the head, `JACK_Y` and the buttress stay where they are. Otherwise move them with the head (the buttress is 1.5 mm from the battery holder), then re-run `assembly_check.py`.
- **(b) Nut plate.** A steel nut plate 14 × 8 × 2 mm, slotted, under the nut, in a nut slot opened from 6.0 to 9 mm tall and 2 mm deeper:
  - nut-side pressure SF **6.5** at the reverse stall and **10.6** sustained;
  - its top edge on the slot roof fixes B4: 2.14 → **9.3**.
  - On its own, a DIN 557 square nut (5.5 × 5.5 × 2.4) fixes only B4 (3.22).

**Alternative.** A tensioner whose pivot bolt sits in a round hole: for example, the idler on a printed swing arm that the jack screw pushes. The nut and hole-edge couple then carries the moment, as at the road wheels (A4–A6 pass).

**Do not run the reverse stall proof test on the current clamp.** At 32.5 N it would crush the PETG under the washer (advisory, SF 0.55).

### 2. Skin, `rover_frame.SKIN` 1.0 → 2.0 mm (C1, C2)

- The gearbox face moves to |y| 44.0. The nacelle, thrust washer, hub and track plane don't move.
- Results:
  - skin shear 2.91 → **6.76**; 3.22 even if the skin carries the whole reaction;
  - nacelle wall root 2.55 → **3.69**.
- **Cost.** The shaft arm becomes 11.0 mm. The N20 shaft goes from SF 3.36 to **3.06** at stall and from 2.10 to **1.91** at the 5 cm corner, still inside the Architect's limits of 2 and 1.5.
- Both shafts keep 5 mm in the hub: a 10 mm shaft ends at |y| 54, a 9 mm one at 53.
- **1.5 mm is not enough.** It gives 2.42 on the rigid-diaphragm bound and 3.06 at the wall root.
- The skin is the coordinator's item 3. Under the motor reaction (C6 to C10) it passes; it fails only in the drop (C1).

## Proof tests (after the changes; spec §8 tests 1 to 3 stay, with these additions)

1. **Axle bolt and boss (as spec).**
   - Hang **5 kg (49 N)** from the middle of a road-wheel rim for 1 min. With class 12.9 bolts this reaches SF 1.73 on yield.
   - On the idler, also pull **4.5 kg (44 N) rearward along the track line for 1 min** (idler §8 test 1). Before and after, measure the idler disc's rear face against a fixed mark on the chassis.
   - Pass: no crack or whitening at the boss, nut trap, plates or floor fillet; bolts square (≤ 0.5 mm runout at the tip); **the idler disc moved ≤ 0.3 mm**.
2. **Stall (as spec).**
   - Measure each motor's stall torque first, **with the hub on and before the sprocket disc is fitted**, so that a motor stronger than 371 g at 50 mm never drives the printed teeth.
   - Then stall at 100 % PWM on a fresh pack for 1 s, 5 times, forward and reverse. The round-3 sketch caps the motors at 6.0 V average, so this test needs the cap lifted for the test only.
   - Additional passes:
     - after the reverse stalls, the idler disc has moved ≤ 0.3 mm;
     - with the hubs off, the skins and nacelles show no crack or whitening.
3. **Drop (as spec).**
   - Drop from 5 cm, flat and on each corner.
   - Additional checks: take each hub off and inspect the skin and nacelle (no crack or whitening), and check the idler bolts are square.

## Notes

**Coordinator's DFM items**
1. **Sharp roots.** The buttress lug has Kt 2.5 (B9, SF 12.7). The floor-only bound is 1.43, but the lug's outer side merges into the block and column 2.6 mm from the jack line, so that bound doesn't govern. The nacelle root has Kt 2.5 under tube bending (C3, SF 21.7); see the assumptions for why the wall-bending row uses Kt 1.
2. **Jack screw.** 6.5 mm of thread is enough. The screw pushes on the bolt head, so the load is the idler's rearward force, and thread strip-out and pull-out are the same failure: the thread shearing out along its 6.5 mm cylinder. That gives SF 4.82 at the reverse stall (B7), 4.42 at the proof and 14.4 under sustained pretension (B8). Self-tapping it strains the **2.0 mm ligament** between the pilot and the buttress's inner face (|y| 22–24) across the layers. Run it in slowly and back it out to clear the chips. If the ligament cracks, open the pilot to Ø2.7.
3. **Skin.** See change 2.
4. **Inserts.** The Ø4.0 holes print about Ø3.8. An M3 × 5.7 insert then displaces about 30 mm³ instead of 23. More melt rises round the insert, so scrape it flush. Retention isn't reduced, the column keeps a 2.7 mm wall, and the loads are tiny (E1 SF 141). Lid §8 test 5 (refit × 5) checks for spin-out.

**Documentation**
- **Spec §4 is stale in two places.** "146 N·mm at the sketch's 80 % cap": the sketch now caps at 6.0 V, so a gated motor gives at most 130. "Pocket edges carry 1.87 R and 0.87 R" holds for horizontal loads only (1.61 R for the drop).
- **BUILD_GUIDE step 3.** It says "tighten the road-wheel bolts (2.5 mm key)". A firm hand gives about 0.5 N·m: 830 N on the nut trap, 49 MPa (advisory SF 0.51). The design takes no credit for preload. Say "snug: head seated plus a quarter turn, about 0.15 N·m".
- **The δ 5 mm drop convention isn't conservative** (see the load table). The drop test, not this calculation, establishes the 5 cm rating.

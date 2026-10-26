VERDICT: FAIL

# Strength check: 20261026-rover-chassis (round 4)

strength-analyst (independent) · 2026-10-26 · run with the CAD venv: `source /home/claude/.venv-cad/bin/activate`, then `python3 jobs/20261026-rover-chassis/strength_calc.py` from the project root (about 1 min). The script builds the round-4 chassis with build123d, probes the idler clamp on the solid, solves the clamp as a contact problem and recomputes the rover mass from every rover `part.stl`.

**Result: FAIL.** Round 4 fixed all five round-3 failures, but its idler clamp has a new weak link. 10 of 58 verdict rows are below their required SF, all in one place: the **3.4 mm PETG web** left between the head-plate recess (|y| 28–30) and the deepened nut slot (|y| 33.4–38).

| Row | What fails | SF | Required |
|---|---|---|---|
| B15 | Web's top strip root, across the layers, 5 cm front-corner drop (Kt 2.5 at the nut slot's sharp corner) | **0.61** (lowest; 1.52 without the Kt) | 3 |
| B15 | The same root, shear along the layer, drop | 1.10 | 3 |
| B15 | Web's bottom strip under the head plate, drop | 1.92 | 3 |
| B12 | Web strip root across the layers: reverse stall / everyday reverse / sustained pretension | 1.20 / 2.19 / 3.56 | 3 / 4 / 4 |
| B13 | Web strip root, shear along the layer: reverse stall / everyday reverse | 2.17 / 3.95 | 3 / 4 |
| B14 | Web end piece at the nut slot's end corner, reverse stall | 2.31 | 3 |
| B6 | Nut plate's bearing on the web (zone mean), reverse stall | 2.26 | 3 |

- **What happens.**
  - The slot has no edges along X. So the idler bolt's yaw moment (29.6 R, with the jack screw at the head) can only be carried by the bolt's tension times the lever between the washer's and the nut's bearing resultants. The same is true of its tilt about X in a drop.
  - With no preload credited (DFM note S2), that tension is the prying force the moment itself creates:
    - 189 N at the reverse stall (lever 4.66 mm);
    - 157 N in the 5 cm drop.
  - The head plate pushes the tension into the PETG at one end of the clamp, and the nut plate pushes back at the other. The two pushes are on opposite faces of the web and in different places, so they don't cancel through its thickness.
  - The nut plate lies wholly inside the 9 × 15 nut slot, so all of its push lands on the web.
  - The bolt slot splits the web into two strips, 1.95 and 2.70 mm tall. Loaded across their 3.4 mm, they bend as short cantilevers from the nut slot's flat roof and floor.
  - The tension face is the web's outer face. It ends at the slot's sharp 90° corners, and the stress there pulls the layers apart (σz).
- **Two earlier readings this corrects.**
  - DFM round 4 (checklist item 10) read these corners as compression only. That holds for the clamp preload, not for the yaw and tilt couples.
  - Round 3's plate rows (FIX 9.5 and 6.5) assumed each plate bears on solid PETG with 100 N of clamp left. As built, both plates press on the same 3.4 mm web, and the preload is gone after about 0.003 mm of creep.
- **Consequence.**
  - The web would crack along a layer line at the nut slot's roof corner, in a drop of about 1 cm or more, or in reverse stalls.
  - The idler bolt would then lean and the track lose tension.
  - The idler parts of the §8 proof tests would crack a correctly made web.
- **What passes:**
  - the skin, nacelle and N20 shaft (round-3 changes 1 and 2 as predicted, within 4 %);
  - the steel plates themselves;
  - the head plate's bearing on PETG, the nut plate's top edge on the slot roof, and the washer on steel;
  - the jack screw, both axle bolts, and all road-wheel, floor and lid rows.
- **Fix:** take the nut plate out of the wall (one package: [Required change](#required-change-take-the-idler-nut-plate-out-of-the-wall)). Lowest SF then 3.02.

## Round 4 as built: the designer's numbers, checked

| Item | Designer's value | Checked on the round-4 geometry |
|---|---|---|
| Gearbox face | \|y\| 44 | rover_frame `MOTOR_FACE_Y` 44.0; skin solid at \|y\| 43.98–46.03 (probe at x 0, Z_A − 3) ✓ |
| Shaft overhang (gearbox face to track plane) | 11.0 | `SHAFT_ARM` = 55 − 44 = 11.0; assembly_check 11.0. Both shafts keep 5.0 mm in the hub (9 and 10 mm shafts) ✓ |
| Head-plate recess | x 108–129, Z_A ± 5.2, 45° roof | Probes at \|y\| 29: void x 108.03–128.98 and Z_A − 5.18 to Z_A + 6.18. The roof runs from Z_A + 7.15 at \|y\| 28.05 to Z_A + 5.25 at 29.95, so 45° ✓ |
| Steel plates | 20.6 × 10 × 2 and 14 × 8 × 2 (14 gauge), both slotted 3.4 × 12 | `IDLER_PLATE`, `NUT_PLATE`, `PLATE_SLOT`, `PLATE_T` 2.0; BUILD_GUIDE §1; assembly_check. The head-plate slot is 114.2–126.2 at x 108.2–128.8; the nut plate is at x 113–127 ✓ |
| Idler nut slot | 9 tall × 15 × 4.6 deep, flat roof over the nut plate | Probes: void x 112.53–127.48 and Z_A ± 4.48 at \|y\| 34.4. The roof is flat at Z_A + 4.49 for \|y\| 33.45–35.35, then rises at 45° ✓ |
| Web (not stated as a strength item) | 3.4 mm in the brief | \|y\| 30.0–33.4, cut by the bolt slot Z_A − 1.8..+2.55 at x 114.2–125.8. Its end pieces (x 112.5–114.2, 125.8–127.5) are full height. Asserted by probes in the script; sections in the scratchpad |
| Stall gate | BUILD_GUIDE step 6 | Hub on, disc off, motor straight to a fresh pack for 1 s, ≤ 371 g at 50 mm. Matches spec §8 test 2 ✓ |
| Stall test cap | spec §8 test 2 | Lifts `MOTOR_V` to 8.4 for the stall test only ✓ |

**Round 3's FIX predictions against round 4**

| Round-3 FIX row | Predicted | Round 4 | Why it differs |
|---|---|---|---|
| Skin shear, 5 cm corner | 6.76 | C1 **6.52** | The motor moved 1 mm inward, so the vertical lever went from 1.61 to 1.67 R |
| Skin, rigid-diaphragm bound | 3.22 | **3.11** | Same |
| Nacelle wall root, 5 cm corner | 3.69 | C2 **3.55** | Same, plus a 73 % wall share |
| N20 shaft, stall / 5 cm corner | 3.06 / 1.91 | **3.06 / 1.91** | As predicted |
| Head plate on PETG, reverse stall | 9.53 | B6 **3.28** (zone mean) | With no preload the tension is all prying (189 N). At the slot's front end the Ø9 washer sits 0.3 mm from the plate's end, so the plate can't spread the yaw forward |
| Nut plate on PETG, reverse stall | 6.47 | B6 **2.26**, and the web **1.20** | The plate bears on the 3.4 mm web, not on solid PETG |
| Nut plate's top edge on the roof, drop | 9.33 | B4 **5.03** | Round-4 zones: the nut no longer bears on PETG; the plate's zone is 2.6–4.6 mm in from the outer face |
| Round-3 failures | B6 0.60, B5 1.50, B4 2.14, C1 2.91, C2 2.55 | B17 42 (washer on steel), B6 3.28 / 9.78 (head plate), B4 5.03, C1 6.52, C2 3.55 | All five fixed |

## DFM round 4 notes S1 and S2

**S2: the clamp with no clamp force left.**
- Every clamp row runs with zero preload. The sustained rows also run with 80 N, and the worse result is kept.
- No friction is credited in any verdict row.
- The reverse-stall yaw then goes through prying alone.
- **Holds:**
  - the jack screw takes the 29.8 N alone (B7 4.82);
  - the bolt's bending (B10 1.79);
  - the steel plates (B16: 2.54 and 1.82 against 200 MPa);
  - the nut and the washer on steel (B17: 9.9 and 42);
  - the head plate on PETG (B6 3.28).
- **Doesn't hold:**
  - the nut plate's bearing on the web (2.26);
  - the web strips (1.20, and 2.17 in shear);
  - the web's end pieces (2.31).
- **With the fix,** all of these hold with no preload. At the reverse stall the lowest PETG row is then 6.45; the steel plates are at 3.50 against 1.5.

**S1: snug torque for BUILD_GUIDE step 3.**
- Tensioning slides the bolt on two steel faces: the washer on the head plate, and the nut on the nut plate. The jack's thrust is therefore 2µP + 2T0.
- The thread's capacity at the allowable is 143.6 N (22.97 mm² × 6.25 MPa). SF 3 therefore needs a thrust of **47.9 N or less**.
- **Set the snug at 0.04 N·m and no more, with the plates oiled.**
  - P is then 89 N. Oil on the faces lowers K, so K 0.15 is used, which raises P for a given torque.
  - With µ 0.2 the thrust is 46 N, so B7t is SF 3.15.
- **Words for the guide:** "Put a drop of light machine oil on each plate where the washer and the nut slide. With the 2.5 mm key's long arm in the head, twist its short arm with two fingertips until the head stops, and stop there (about 0.04 N·m)."
- **Oil is required.**
  - The same snug dry (static µ 0.6) gives SF 1.60.
  - The DFM's 0.05 N·m gives 2.64 even oiled.
  - A normal L-key snug of 0.3 N·m gives 0.24 dry and 0.52 oiled.
- **Friction appears only as a demand:** it is what the jack screw must overcome. It is never credited as holding anything.

## Load cases

The shared block is unchanged from round 3 and identical in all six rover scripts.

| Load | Value used | Source | Duration |
|---|---|---|---|
| Mass | **649 g** (W 6.37 N) | Spec §4. This script's estimate is 626 g at the print_requirements minima, including the four steel plates (7.6 g). 721 g if every printed part were solid | n/a |
| Stall torque | 160 N·mm design → 9.89 N pull; 182 N·mm proof → 11.25 N | Spec §4; the chassis §8 gate | short-term |
| Pretension | 5 N per run | Spec §4 (an over-tension bound) | sustained |
| Idler radial | Reverse stall 29.8 N (both runs tight), proof 32.5, everyday reverse 16.4, sustained 10 | Round 3 | short-term / proof / cyclic / sustained |
| Idler yaw moment | R × 29.6 (track plane 55 − jack line 25.4): 882 / 962 / 485 / 296 N·mm | Geometry | as above |
| 5 cm drop | **31.8 N per axle**, any axle. At the idler it acts upward at the track plane: tilt moment 31.8 × (55 − 30) = 795 N·mm about the head plate's bearing face | Round-3 convention, 5 mm stopping distance. 30 is the innermost place the shear can react, so it gives the largest moment | short-term |
| Tensioning slide (S1) | Jack thrust 2µP + 10 N | DFM S1 | short-term, a few times |
| Proof loads | 5 kg (49 N) hung from the idler; 4.5 kg (44 N) rearward pull; 32.5 N reverse stall | Spec §8 tests 1 and 2 | 1 min / 1 s × 5 |
| Side, motor reaction, lid lift, assembly | 3 N per track; 160 N·mm; 2 × W on 4 inserts | Round 3 | as round 3 |

## Assumptions

**Idler clamp, yaw (B5/B6, B12–B14, B16–B17)**
- **Geometry.** Taken from `model.py` and `rover_frame.py`, and asserted on the solid by `is_inside` probes in the script (the table above).
- **1-D contact model along X,** at 0.1 mm stations:
  - **Plates:** both steel plates are Hermite beams, with slotted sections where they are slotted.
  - **Web:** two face nodes and a mid node per station:
    - through-thickness springs, 2E·b/t per half;
    - an out-of-plane ground spring: the two strips as Timoshenko cantilevers from their roots, loaded at the nut plate's resultant, with 30 % extra root compliance;
    - end pieces at 11 000 N/mm per mm.
  - **Head plate support:** solid PETG wherever no web is behind it (200 N/mm³ × width), and on the 0.5 mm margins above and below the nut slot.
  - **Washer:** the Ø9 washer is a rigid disc with the head; its contact excludes the plate-slot band.
  - **Nut:** flats on top and bottom, which gives the smaller lever.
  - **Bolt:** 70 kN/mm axially.
  - **Contacts:** compression-only, solved by active-set iteration.
  - **Slot positions:** x 116–124 every 2 mm; the worst case is kept.
- **No friction and no preload** (DFM S2).
- **Strip roots.**
  - Bending: σz = Kt·6·q·a/t², where q is the strip's line load and a is the arm from the root to the nut plate's resultant (1.225 mm top, 1.6 mm bottom).
  - Kt 2.5 at the nut slot's sharp roof and floor corners on the outer face. That face is in tension when the nut plate pushes.
  - The inner face has no corner at the root (Kt 1). The recess floor's corner, 0.7 mm lower, is checked on the 8 mm section with Kt 2.5.
  - Shear: 1.5 q/t on the root plane, which is a layer plane, so the across-layer shear allowable applies.
- **End pieces:** cantilevers in X from the nut slot's ends, σx = Kt·6·M/(9·t²) (in-plane), with Kt 2.5 when the nut plate pushes.
- **Bearing rows:** the mean over the contiguous zone above half the peak (round 3's mean over the contact zone). Peaks are advisory, because the 1-D model spikes where a width steps.
- **Hand check.** The classical infinite-beam BEF peak line load, Tβ/2, gives:
  - yaw: 15.4 N/mm by hand, 11.1 N/mm in the model (the model shares the load with the head plate and the end pieces);
  - drop: 13.3 by hand, 12.9 in the model.
- **Sensitivity** (advisory rows):
  - every stiffness assumption leaves the governing reverse-stall row between 0.90 and 1.42;
  - the drop row is 1.52 with no Kt at all.
  - The verdict doesn't hinge on the model.

**Idler clamp, drop and the 5 kg hang (B15)**
- Prying T = M/(z_h + z_n), where z_h and z_n are the uniform-pressure centroids of the washer's and the nut's contacts beyond the plate-slot band (2.86 + 2.20 mm). An edge-loaded contact gives a longer lever and a smaller T.
- **Nut side:** the nut plate's loaded strip is a beam on its web strip and end pieces; tension on the outer face (Kt 2.5).
- **Head side:** the head plate's loaded strip is a beam on the opposite web strip, the end pieces and solid PETG; tension on the inner face.
- The z-gaps (the nut plate 0.5 mm under its roof, the head plate 0.4 under its 45° roof) are far larger than what the clamp couple's rotation moves. The yaw model gives θ = 0.0026–0.0051 rad at the reverse stall, which is about 0.015 mm at 3 mm from the axis. So the clamp couple carries the moment. (At the idler disc that rotation is about 0.13 mm, elastic; §8 measures the permanent movement.)
- B4 bounds the other path (round 3's rigid pin in z), which is worse for the roof.

**Steel plates:** hand-cut 14 gauge or 2 mm mild steel, σy 200 MPa (conservative; A36 is 250), required SF 1.5.

**Everything else** uses round 3's models unchanged (git `7fa597b`, strength.md: axle bolts, motor pocket, skin/nacelle split, floor, inserts). The C rows pick up `SKIN` 2.0 and the face at \|y\| 44 from rover_frame. The skin's out-of-plane rows (C9, C10) are the 2 mm skin as the motor's outward and inward stop.

## Allowables and sources

- **No measured data.** `library/materials.csv` has only its header row, and no job has a datasheet in `inputs/`. The skill's placeholders apply:
  - PETG 25 MPa in-plane, 12.5 MPa across the layers;
  - E 1.8 GPa, ν 0.35;
  - shear allowable 0.5 × normal.
  - **PASS is not possible; NEEDS_TEST is the best verdict.**
- **Direction.**
  - In-plane: compressive bearing on layer faces and on 45° flanks, and in-plane bending (the end pieces).
  - Across-layer: the web strips' σz and their shear on the root plane.
- **Required SF:**
  - 3 for short-term static loads;
  - 4 for cyclic or sustained loads;
  - 1.5 on yield for steel (class 12.9: 1080 MPa; plates: 200; N20 shaft and rod: 350);
  - 1.0 on the knocked-down allowable for proof loads.
- **Temperature.** 40 °C service against a PETG softening point of about 70 °C: more than 20 °C apart.

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
| 10 | B4 idler nut plate's top edge (14 x 2) on the flat slot roof (rigid pin, round-4 zones; the nut no longer touches PETG), 5 cm front corner | XY | 4.97 | 25.0 | 5.03 | 3.0 | OK |
| 11 | B5/B6 idler head plate on PETG (zone mean, peak 3.3 at x 126.2), pretension 10 N sustained (P 0 or 80 N) | XY | 2.56 | 25.0 | 9.78 | 4.0 | OK |
| 12 | B5/B6 idler nut plate on the 3.4 mm web (zone mean, peak 5.4 at x 114.0), pretension 10 N sustained (P 0 or 80 N) | XY | 3.71 | 25.0 | 6.74 | 4.0 | OK |
| 13 | B12 web strip root, bending across layers at the nut slot's sharp corner (Kt 2.5), pretension 10 N sustained (P 0 or 80 N) | Z | 3.52 | 12.5 | 3.56 | 4.0 | **FAIL** |
| 14 | B13 web strip root, shear along the layer at the strip root, pretension 10 N sustained (P 0 or 80 N) | Z shear | 0.97 | 6.2 | 6.42 | 4.0 | OK |
| 15 | B14 web end piece, bending at the nut slot's end corner (Kt 2.5 when the nut plate pushes), pretension 10 N sustained (P 0 or 80 N) | XY | 3.64 | 25.0 | 6.87 | 4.0 | OK |
| 16 | B5/B6 idler head plate on PETG (zone mean, peak 5.2 at x 126.2), everyday reverse 16.4 N cyclic | XY | 4.18 | 25.0 | 5.98 | 4.0 | OK |
| 17 | B5/B6 idler nut plate on the 3.4 mm web (zone mean, peak 8.8 at x 114.0), everyday reverse 16.4 N cyclic | XY | 6.07 | 25.0 | 4.12 | 4.0 | OK |
| 18 | B12 web strip root, bending across layers at the nut slot's sharp corner (Kt 2.5), everyday reverse 16.4 N cyclic | Z | 5.71 | 12.5 | 2.19 | 4.0 | **FAIL** |
| 19 | B13 web strip root, shear along the layer at the strip root, everyday reverse 16.4 N cyclic | Z shear | 1.58 | 6.2 | 3.95 | 4.0 | **FAIL** |
| 20 | B14 web end piece, bending at the nut slot's end corner (Kt 2.5 when the nut plate pushes), everyday reverse 16.4 N cyclic | XY | 5.96 | 25.0 | 4.20 | 4.0 | OK |
| 21 | B5/B6 idler head plate on PETG (zone mean, peak 9.4 at x 126.2), reverse stall 29.8 N | XY | 7.61 | 25.0 | 3.28 | 3.0 | OK |
| 22 | B5/B6 idler nut plate on the 3.4 mm web (zone mean, peak 16.0 at x 114.0), reverse stall 29.8 N | XY | 11.05 | 25.0 | 2.26 | 3.0 | **FAIL** |
| 23 | B12 web strip root, bending across layers at the nut slot's sharp corner (Kt 2.5), reverse stall 29.8 N | Z | 10.39 | 12.5 | 1.20 | 3.0 | **FAIL** |
| 24 | B13 web strip root, shear along the layer at the strip root, reverse stall 29.8 N | Z shear | 2.88 | 6.2 | 2.17 | 3.0 | **FAIL** |
| 25 | B14 web end piece, bending at the nut slot's end corner (Kt 2.5 when the nut plate pushes), reverse stall 29.8 N | XY | 10.84 | 25.0 | 2.31 | 3.0 | **FAIL** |
| 26 | B15 web top strip root under the nut plate's top strip, across layers (Kt 2.5), 5 cm front corner | Z | 20.52 | 12.5 | 0.61 | 3.0 | **FAIL** |
| 27 | B15 web top strip root, shear along the layer, 5 cm front corner | Z shear | 5.69 | 6.2 | 1.10 | 3.0 | **FAIL** |
| 28 | B15 web bottom strip under the head plate (inner face; recess-floor corner), 5 cm front corner | Z | 6.51 | 12.5 | 1.92 | 3.0 | **FAIL** |
| 29 | B16 steel head plate bending (slotted section), reverse stall | steel σy 200 | 78.73 | 200.0 | 2.54 | 1.5 | OK |
| 30 | B16 steel nut plate bending (slotted section), reverse stall | steel σy 200 | 109.96 | 200.0 | 1.82 | 1.5 | OK |
| 31 | B17 nut on the nut plate's two strips: mean steel bearing at T 189 N, reverse stall | steel σy 200 | 20.18 | 200.0 | 9.91 | 1.5 | OK |
| 32 | B17 Ø9 washer on the head plate: mean steel bearing at T 189 N | steel σy 200 | 4.74 | 200.0 | 42.22 | 1.5 | OK |
| 33 | B7 jack-screw thread strip-out (6.5 mm, Ø2.6 pilot), reverse stall 29.8 N | Z shear | 1.30 | 6.2 | 4.82 | 3.0 | OK |
| 34 | B8 jack-screw thread, pretension 10 N sustained | Z shear | 0.44 | 6.2 | 14.36 | 4.0 | OK |
| 35 | B7t jack-screw thread while tensioning: snug 0.04 N*m (K 0.15: P 89 N), oiled plates (mu 0.2): thrust 46 N | Z shear | 1.98 | 6.2 | 3.15 | 3.0 | OK |
| 36 | B9 buttress lug at the block face (y 28): bending, reverse stall (Kt 2.5) | XY | 1.96 | 25.0 | 12.73 | 3.0 | OK |
| 37 | B10 idler M3 x 40 class 12.9: bending at the head face (y 28), reverse stall x 27 | steel σy 1080 | 602.13 | 1080.0 | 1.79 | 1.5 | OK |
| 38 | B11 idler M3 x 40 class 12.9: bending at the outer face, 5 cm front corner x 17 | steel σy 1080 | 405.30 | 1080.0 | 2.66 | 1.5 | OK |
| 39 | C1 skin (2 mm) diaphragm shear across layers, 5 cm rear corner: nacelle reaction 53.3 N, skin share 48 % | Z shear | 0.96 | 6.2 | 6.52 | 3.0 | OK |
| 40 | C2 nacelle wall root bending (pocket face in tension, no notch), 5 cm rear corner, wall share 73 % | XY | 7.04 | 25.0 | 3.55 | 3.0 | OK |
| 41 | C3 nacelle root, tube bending (sharp outer corner in tension, Kt 2.5), 5 cm rear corner | XY | 0.75 | 25.0 | 33.26 | 3.0 | OK |
| 42 | C4 nacelle root, tube shear (2 V/A), 5 cm rear corner | Z shear | 0.99 | 6.2 | 6.29 | 3.0 | OK |
| 43 | C5 gearbox front edge bearing on the pocket faces (1 mm x face width), 5 cm rear corner | XY | 3.77 | 25.0 | 6.64 | 3.0 | OK |
| 44 | C6 skin diaphragm shear, track stall 19.9 N (horizontal, 2.05 R) | Z shear | 0.73 | 6.2 | 8.52 | 3.0 | OK |
| 45 | C7 nacelle wall root bending, track stall 19.9 N | XY | 5.38 | 25.0 | 4.64 | 3.0 | OK |
| 46 | C6 skin diaphragm shear, track pretension 10 N sustained (horizontal, 2.05 R) | Z shear | 0.37 | 6.2 | 16.95 | 4.0 | OK |
| 47 | C7 nacelle wall root bending, track pretension 10 N sustained | XY | 2.71 | 25.0 | 9.24 | 4.0 | OK |
| 48 | C8 reaction torque 160 N*mm: gearbox corner bearing (13.3 N over 9 x 1 mm) | XY | 1.48 | 25.0 | 16.88 | 3.0 | OK |
| 49 | C9 skin out of plane: side 3 N inward on the thrust washer (annular plate a 6.29, hole r 2.25) | Z | 0.41 | 12.5 | 30.48 | 4.0 | OK |
| 50 | C10 skin out of plane: side 3 N outward on the gearbox face, the motor's outward stop (Kt 2.5 at the pocket corner) | Z | 0.44 | 12.5 | 28.43 | 4.0 | OK |
| 51 | C11 wall bending round the motor housing (Ø22.4 equivalent, Kt 1.6), 5 cm rear corner | Z | 2.85 | 12.5 | 4.38 | 3.0 | OK |
| 52 | C12 trough cheek bridge over the tie tunnel: tie 51 N (can rear reaction 20.8 N + 30 N preload) | XY | 0.38 | 25.0 | 66.27 | 3.0 | OK |
| 53 | C13 N20 shaft (bought steel), arm 11.0, Z_min 1.911 mm³: stall 19.9 N (target 1.5 on yield; the Architect's 2 also met) | steel σy 350 | 114.48 | 350.0 | 3.06 | 1.5 | OK |
| 54 | C13 N20 shaft, arm 11.0: 5 cm corner 31.8 N | steel σy 350 | 183.23 | 350.0 | 1.91 | 1.5 | OK |
| 55 | D1 floor mid-span under the battery, 5 cm (20 g x 135 g) | XY | 3.69 | 25.0 | 6.77 | 3.0 | OK |
| 56 | D2 floor at the strap slots |y| 26.0 (Kt 2.5, square ends), 5 cm | XY | 4.11 | 25.0 | 6.08 | 3.0 | OK |
| 57 | E1 insert knurl shear-out of the column, lifted by the lid 3.2 N per insert | Z shear | 0.04 | 6.2 | 140.63 | 3.0 | OK |
| 58 | E2 column tension (Z) round the insert, lifted by the lid | Z | 0.05 | 12.5 | 259.06 | 3.0 | OK |

Advisory (not in the verdict: peaks, bounds, sensitivities, proof loads, S1 table, bought parts, the FIX and what is not enough):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| A4/A5 Winkler peaks: nut edge 10.4, inner hole edge (peak), 5 cm drop | XY | 11.43 | 25.0 | 2.19 | 3.0 | no |
| proof 5 kg (49 N) at the wheel rim centre: boss collar | Z | 5.48 | 12.5 | 2.28 | 1.0 | OK |
| proof 5 kg at the wheel rim centre: nut-trap bearing | XY | 11.95 | 25.0 | 2.09 | 1.0 | OK |
| proof 5 kg at the rim centre: M3 class 12.9 at the outer face | steel σy 1080 | 624.50 | 1080.0 | 1.73 | 1.0 | OK |
| if A2-70 (fully threaded stainless) bolts are fitted instead: 5 cm drop | steel σy 450 | 405.30 | 450.0 | 1.11 | 1.5 | no |
| B6 head plate on PETG, reverse stall: PEAK (at a width step of the 1-D model) 9.4 at x 126.2 | XY | 9.43 | 25.0 | 2.65 | 3.0 | no |
| B6n nut plate on the web, reverse stall: PEAK 16.0 at x 114.0 | XY | 16.04 | 25.0 | 1.56 | 3.0 | no |
| B12 web strip root, reverse stall, WITHOUT the corner Kt (nominal) | Z | 4.16 | 12.5 | 3.01 | 3.0 | OK |
| B15 web top strip root, 5 cm front corner, WITHOUT the corner Kt (nominal) | Z | 8.21 | 12.5 | 1.52 | 3.0 | no |
| B12 sensitivity, washer bearing only to r 3.55 (head edge + 45° through the washer): web strip root (Kt 2.5), reverse stall | Z | 10.53 | 12.5 | 1.19 | 3.0 | no |
| B12 sensitivity, PETG foundation 500 N/mm³: web strip root (Kt 2.5), reverse stall | Z | 10.34 | 12.5 | 1.21 | 3.0 | no |
| B12 sensitivity, root fully rigid (root_soft 1.0): web strip root (Kt 2.5), reverse stall | Z | 12.20 | 12.5 | 1.02 | 3.0 | no |
| B12 sensitivity, roots twice as soft (2.0): web strip root (Kt 2.5), reverse stall | Z | 8.78 | 12.5 | 1.42 | 3.0 | no |
| B12 sensitivity, end pieces 3x stiffer: web strip root (Kt 2.5), reverse stall | Z | 10.73 | 12.5 | 1.17 | 3.0 | no |
| B12 sensitivity, end pieces half as stiff: web strip root (Kt 2.5), reverse stall | Z | 13.95 | 12.5 | 0.90 | 3.0 | no |
| proof: reverse stall at 100 % PWM fresh pack (32.5 N, §8 test 2): web strip root (Kt 2.5) | Z | 11.34 | 12.5 | 1.10 | 1.0 | OK |
| proof: 4.5 kg (44 N) rearward pull on the idler (§8 test 1): web strip root (Kt 2.5) | Z | 15.41 | 12.5 | 0.81 | 1.0 | no |
| proof: 4.5 kg rearward pull: web end piece (Kt 2.5) | XY | 16.07 | 25.0 | 1.56 | 1.0 | OK |
| proof: 5 kg (49 N) hung from the idler (§8 test 1, pulls down): web bottom strip root (Kt 2.5) | Z | 35.26 | 12.5 | 0.35 | 1.0 | no |
| proof 5 kg on the idler bolt: M3 class 12.9 at the outer face | steel σy 1080 | 624.50 | 1080.0 | 1.73 | 1.0 | OK |
| S1 tensioning: snug 0.02 N*m, oiled plates (K 0.15, mu 0.2): P 44 N, jack thrust 28 N vs thread capacity 144 N | jack N | 27.78 | 143.6 | 5.17 | 3.0 | OK |
| S1 tensioning: snug 0.02 N*m, dry plates (K 0.2, mu 0.6): P 33 N, jack thrust 50 N vs thread capacity 144 N | jack N | 50.00 | 143.6 | 2.87 | 3.0 | no |
| S1 tensioning: snug 0.04 N*m, oiled plates (K 0.15, mu 0.2): P 89 N, jack thrust 46 N vs thread capacity 144 N | jack N | 45.56 | 143.6 | 3.15 | 3.0 | OK |
| S1 tensioning: snug 0.04 N*m, dry plates (K 0.2, mu 0.6): P 67 N, jack thrust 90 N vs thread capacity 144 N | jack N | 90.00 | 143.6 | 1.60 | 3.0 | no |
| S1 tensioning: snug 0.05 N*m, oiled plates (K 0.15, mu 0.2): P 111 N, jack thrust 54 N vs thread capacity 144 N | jack N | 54.44 | 143.6 | 2.64 | 3.0 | no |
| S1 tensioning: snug 0.05 N*m, dry plates (K 0.2, mu 0.6): P 83 N, jack thrust 110 N vs thread capacity 144 N | jack N | 110.00 | 143.6 | 1.31 | 3.0 | no |
| S1 tensioning: snug 0.10 N*m, oiled plates (K 0.15, mu 0.2): P 222 N, jack thrust 99 N vs thread capacity 144 N | jack N | 98.89 | 143.6 | 1.45 | 3.0 | no |
| S1 tensioning: snug 0.10 N*m, dry plates (K 0.2, mu 0.6): P 167 N, jack thrust 210 N vs thread capacity 144 N | jack N | 210.00 | 143.6 | 0.68 | 3.0 | no |
| S1 tensioning: snug 0.30 N*m, oiled plates (K 0.15, mu 0.2): P 667 N, jack thrust 277 N vs thread capacity 144 N | jack N | 276.67 | 143.6 | 0.52 | 3.0 | no |
| S1 tensioning: snug 0.30 N*m, dry plates (K 0.2, mu 0.6): P 500 N, jack thrust 610 N vs thread capacity 144 N | jack N | 610.00 | 143.6 | 0.24 | 3.0 | no |
| N20 shaft fatigue, rotating bending at everyday pull 13.2 N, arm 11, Kf 1.5 (endurance limit estimated for an unknown steel) | steel Se 190 | 113.83 | 189.7 | 1.67 | 1.5 | OK |
| N20 shaft fatigue, rotating bending at pretension 10 N, arm 11, Kf 1.5 (endurance limit estimated for an unknown steel) | steel Se 190 | 86.34 | 189.7 | 2.20 | 1.5 | OK |
| C1 BOUND skin carries all (rigid diaphragm), 5 cm rear corner | Z shear | 2.01 | 6.2 | 3.11 | 3.0 | OK |
| C2 BOUND walls carry all (no skin), 5 cm rear corner | XY | 9.61 | 25.0 | 2.60 | 3.0 | no |
| C2 at the spec's horizontal lever 2.05 R applied to the drop, 5 cm rear corner | XY | 8.62 | 25.0 | 2.90 | 3.0 | no |
| C9 skin, sideways friction in a corner drop (mu 0.3 x 31.8 N) on the thrust washer | Z | 1.31 | 12.5 | 9.57 | 3.0 | OK |
| S-08 ungated 196 N*mm motor: skin shear, track stall (2.05 x 22.1 N) | Z shear | 0.82 | 6.2 | 7.67 | 3.0 | OK |
| head plate's top edge on the recess's 45° roof (all the drop shear on a 0.3 mm wide line, 20.6 long), 5 cm front corner | XY | 5.15 | 25.0 | 4.85 | 3.0 | OK |
| FIX head plate on PETG (zone mean), pretension sustained (P 0 or 80 N) | XY | 1.30 | 25.0 | 19.21 | 4.0 | OK |
| FIX nut plate on the wall's outer face (zone mean), pretension sustained (P 0 or 80 N) | XY | 0.51 | 25.0 | 48.63 | 4.0 | OK |
| FIX 8.0 mm PETG between the plates: strip root across layers (Kt 2.5 at both faces), pretension sustained (P 0 or 80 N) | Z | 0.57 | 12.5 | 21.98 | 4.0 | OK |
| FIX strip root, shear along the layer, pretension sustained (P 0 or 80 N) | Z shear | 0.32 | 6.2 | 19.61 | 4.0 | OK |
| FIX head plate on PETG (zone mean), everyday reverse cyclic | XY | 2.13 | 25.0 | 11.74 | 4.0 | OK |
| FIX nut plate on the wall's outer face (zone mean), everyday reverse cyclic | XY | 0.84 | 25.0 | 29.72 | 4.0 | OK |
| FIX 8.0 mm PETG between the plates: strip root across layers (Kt 2.5 at both faces), everyday reverse cyclic | Z | 0.91 | 12.5 | 13.81 | 4.0 | OK |
| FIX strip root, shear along the layer, everyday reverse cyclic | Z shear | 0.51 | 6.2 | 12.31 | 4.0 | OK |
| FIX head plate on PETG (zone mean), reverse stall | XY | 3.88 | 25.0 | 6.45 | 3.0 | OK |
| FIX nut plate on the wall's outer face (zone mean), reverse stall | XY | 1.53 | 25.0 | 16.33 | 3.0 | OK |
| FIX 8.0 mm PETG between the plates: strip root across layers (Kt 2.5 at both faces), reverse stall | Z | 1.65 | 12.5 | 7.59 | 3.0 | OK |
| FIX strip root, shear along the layer, reverse stall | Z shear | 0.92 | 6.2 | 6.77 | 3.0 | OK |
| FIX top strip root under the nut plate (Kt 2.5), 5 cm front corner | Z | 3.66 | 12.5 | 3.42 | 3.0 | OK |
| FIX bottom strip root under the head plate, recess floor edge (Kt 2.5), 5 cm front corner | Z | 4.15 | 12.5 | 3.02 | 3.0 | OK |
| FIX strip root, shear along the layer, 5 cm front corner | Z shear | 2.05 | 6.2 | 3.05 | 3.0 | OK |
| FIX steel plates bending, reverse stall (both 20.6 x 10 x 2) | steel σy 200 | 57.20 | 200.0 | 3.50 | 1.5 | OK |
| FIX jack screw unchanged; idler M3 x 40 at the outer face, 5 cm front corner x 17 | steel σy 1080 | 405.30 | 1080.0 | 2.66 | 1.5 | OK |
| FIX proof 32.5 N reverse stall (§8 test 2): strip root | Z | 1.80 | 12.5 | 6.95 | 1.0 | OK |
| FIX proof 44 N rearward pull (§8 test 1): strip root | Z | 2.44 | 12.5 | 5.12 | 1.0 | OK |
| FIX proof 44 N rearward pull: head plate on PETG (zone mean) | XY | 5.75 | 25.0 | 4.35 | 1.0 | OK |
| FIX proof 49 N hung from the idler (§8 test 1): strip root under the nut plate | Z | 6.39 | 12.5 | 1.96 | 1.0 | OK |
| FIX proof 49 N hung from the idler: shear along the layer | Z shear | 3.16 | 6.2 | 1.98 | 1.0 | OK |
| FIX nut plate's bottom edge on its lip (20.6 x 2.0), 49 N hang | XY | 1.19 | 25.0 | 21.00 | 3.0 | OK |
| FIX sensitivity (wall beyond the bolt slot 3x softer, rigid roots): strip root, reverse stall | Z | 1.70 | 12.5 | 7.36 | 3.0 | OK |
| FIX sensitivity (rigid roots): strip root shear, 5 cm front corner | Z shear | 2.26 | 6.2 | 2.77 | 3.0 | no |
| NOT ENOUGH: the same move without the washer under the nut: shear along the layer, 5 cm front corner | Z shear | 2.51 | 6.2 | 2.49 | 3.0 | no |
| NOT ENOUGH: the nut plate in a 0.5 mm locating recess instead of on a lip: shear along the layer, 5 cm front corner | Z shear | 2.13 | 6.2 | 2.94 | 3.0 | no |
| NOT ENOUGH: web 5.4: idler-block face 2 mm inward (needs JACK_Y 23.4, JACK_Y_IN 20, JACK_X from 102.5): web strip root (Kt 2.5), reverse stall | Z | 6.23 | 12.5 | 2.01 | 3.0 | no |
| NOT ENOUGH: web 5.4: idler-block face 2 mm inward (needs JACK_Y 23.4, JACK_Y_IN 20, JACK_X from 102.5): web top strip root (Kt 2.5), 5 cm front corner | Z | 10.16 | 12.5 | 1.23 | 3.0 | no |
| NOT ENOUGH: web 4.0: DIN 439 thin nut (1.8), nut slot 0.6 shallower: web strip root (Kt 2.5), reverse stall | Z | 8.64 | 12.5 | 1.45 | 3.0 | no |
| NOT ENOUGH: web 4.0: DIN 439 thin nut (1.8), nut slot 0.6 shallower: web top strip root (Kt 2.5), 5 cm front corner | Z | 16.01 | 12.5 | 0.78 | 3.0 | no |

- Lowest SF: **0.61** (required 3.0), at B15: the web's top strip root in the 5 cm front-corner drop.
- **Drop rows** scale with the height:
  - as built they meet their SF up to a **1.0 cm** drop, limited by B15;
  - with the fix, about **5.0 cm** (lowest fixed drop row 3.02); without the clamp rows, A4 limits at 5.4 cm.
- 10 of 58 verdict rows are below their required SF.

## Required change: take the idler nut plate out of the wall

**Why the web can't simply be thickened.** The web is what is left of the 10 mm of block and wall after 6.6 mm of steel stack (head plate, nut plate, nut) has been let into it. Inside the wall:
- moving the idler-block face 2 mm inward (web 5.4; this also needs `JACK_Y` 23.4, `JACK_Y_IN` 20 and `JACK_X` from 102.5) still gives **1.23** in the drop and **2.01** at the reverse stall;
- a thin DIN 439 nut (web 4.0) gives **0.78** and **1.45**;
- the sharp root corners and the across-layer tension stay, so neither is enough.

**The change.** The smallest change that passes every row:
1. **`model.py`:** delete the idler nut slot (`_idler_nut_slot`: 9 × 15 × 4.6; keep the bolt slot).
   - The PETG between the head plate and the wall's outer face is then **8.0 mm** (\|y\| 30–38).
   - Neither plate has a slot behind it.
2. **`rover_frame.NUT_PLATE` (14, 8) → (20.6, 10).** The nut plate becomes the head plate's twin:
   - the same 3.4 × 12 slot, from 6 to 18 mm along;
   - fitted **flat on the wall's outer face** at x 108.2–128.8, Z_A ± 5, with the 6 mm end toward the rear.
3. **Locate it with a printed lip under its bottom edge,** not a recess:
   - along x 108–129, top face at Z_A − 5.1, about 1 mm proud, with a 45° underside;
   - a 0.5 mm locating recess thins the PETG and gives 2.94.
4. **Add a Ø9 × 0.8 DIN 9021 washer under each idler wall nut,** as under the head (2 more in the BOM).
   - It cuts the drop's prying tension from 157 to 139 N and spreads the nut's push.
   - Without it the drop gives 2.49.
5. **Idler job: its hub starts at \|y\| 43.7 instead of 38.5,** 5.2 mm shorter (plate 2.0 + washer 0.8 + nut 2.4).
   - The M3 × 40 bolt, the nyloc (4.2 mm of thread past it), the jack screw and the head plate don't change.
   - The nut and washers stay within r 4.5 of the idler axis, inside the links' wrap (r ≥ 12.39).
   - The plate and lip stay inboard of the links' inner edge (\|y\| 43).

**Predicted with the change** (same model and assumptions; FIX rows in the advisory table):

| Case | Lowest row | SF | Required |
|---|---|---|---|
| Sustained pretension (P 0 or 80 N) | head plate on PETG | 19.2 | 4 |
| Everyday reverse 16.4 N | head plate on PETG | 11.7 | 4 |
| Reverse stall 29.8 N | head plate on PETG (zone mean) | 6.45 | 3 |
| 5 cm front corner | bottom strip under the head plate, recess-floor edge (Kt 2.5) | **3.02** | 3 |
| 5 cm front corner | shear along the layer | 3.05 | 3 |
| Steel plates, reverse stall | both 20.6 × 10 × 2 | 3.50 | 1.5 |
| Proof: 32.5 N reverse stall / 44 N pull / 49 N hang | strip roots | 6.95 / 5.12 / 1.96 | 1.0 |

**Margins.**
- The drop rows sit just above 3. Treating the strip roots as rigid gives 2.77 for the drop shear.
- The 5 mm stopping-distance convention isn't conservative (round 3), so the drop test (§8 test 3) remains the evidence for the 5 cm rating.
- **Cheap extra margin:** a 1 × 45° chamfer on the head-plate recess's floor edge, with the plate's bottom-back edge filed to match, takes the head-side drop row from 3.02 to about 4.7 (Kt 1.6).

**Mass:** +3.6 g (larger nut plates and two washers), 630 g in all, inside the 649 g design mass.

## N20 shaft: which target, and is it met

- **Target.**
  - The shaft is bought steel, so the printed-part targets (3 and 4) don't apply.
  - The project's metal convention does: **SF ≥ 1.5 on yield for short-term static loads**, using 350 MPa for the unknown shaft steel (rounds 1–3).
- **Stall and drop.**
  - Stall (19.9 N radial at the 11.0 mm arm): 114 MPa, **SF 3.06**. That is ≥ 1.5, and also above the Architect's own limit of 2.
  - 5 cm corner (31.8 N): 183 MPa, **SF 1.91** (≥ 1.5).
  - Both match round 3's prediction exactly: **met.**
- **Fatigue (advisory).**
  - Driving puts the shaft in rotating bending, which is a fatigue case: the target is SF ≥ 1.5 on the endurance limit.
  - Estimated Se is 190 MPa (σy 350 → UTS ≥ 450; ground surface; 90 % reliability), with Kf 1.5 at the D-flat run-out.
  - **1.67** at the everyday 13.2 N, **2.20** at the 10 N pretension. Met, but advisory, because the steel grade is unknown.
  - Under 10–20 N of overhung load, the N20's sintered output bushing is the likelier life limit. That isn't a printed-part check.

## Spec §8 proof tests against the round-4 design

**What matches.**
- §8 runs the proof tests only with both idler plates fitted, and test 1's pass criterion names the plates.
- **The stall wording matches the round-4 design.** Test 2 measures the motor first, with the hub on, before the sprocket disc goes on (BUILD_GUIDE step 6: straight to a fresh pack for 1 s, ≤ 371 g at 50 mm). It then lifts `MOTOR_V` to 8.4 for the stall test only.

**What doesn't match.**
1. **On the round-4 clamp, the idler parts of tests 1 and 2 would crack a correctly made web.**
   - Hanging 5 kg from the idler gives proof SF 0.35.
   - The 44 N rearward pull gives 0.81.
   - The reverse-stall proof only just passes (1.10).
   - Don't run them on this design.
2. **No test names the web, or the PETG round the plates,** which is the clamp's weak point.
3. **The idler's 44 N pull is done at mid-slot,** but the head plate is worst at the slot's front end.

**Exact changes, with the fix above:**
1. Checklist: "Each steel plate drops into its place: the head plates flush in their block-face recesses, the nut plates on the bottoms of their nut slots" → "Each steel plate sits in its place: the head plates flush in their block-face recesses; the nut plates (20.6 × 10, the head plates' twins) flat on the walls' outer faces, resting on their lips, with a Ø9 × 0.8 DIN 9021 washer under each idler nut".
2. Proof-test heading: "(strength rounds 2 and 3; …)" → "(strength rounds 2–4; …)".
3. Test 1:
   - "Repeat on an idler bolt at mid-slot, with the jack screw set." → "Repeat on an idler bolt at the front end of its slot, held there by the jack screw."
   - In its pass criterion, "no crack or whitening at the boss, nut trap, plates or floor fillet" → "no crack or whitening at the boss, nut trap, floor fillet, or the PETG round each idler plate (the recess edges inside the tub, the wall face under the nut plate outside)".
4. Test 2's pass criterion: "with the hubs off, the skins and nacelles show no crack or whitening" → "with the hubs off, the skins, nacelles and the PETG round the idler plates show no crack or whitening".
5. Test 3: after "check the idler bolts are still square (≤ 0.5 mm runout at the tip)", add "and look for cracks or whitening in the PETG round each idler plate".

**Predicted with the fix:**
- test 1 idler: 44 N pull **5.12** (strip roots) and **4.35** (head plate); 5 kg hang **1.96** and 1.98 (shear);
- test 2 reverse-stall proof: **6.95**;
- all against a required 1.0.

## Notes

**Spec §4 is stale in two places** (not §8, but the reviewers read it):
- "146 at the sketch's 80 % cap": the sketch caps at 6.0 V, so a gated motor gives at most 130 N·mm.
- "pocket edges carry 1.87 R and 0.87 R": since the face moved to \|y\| 44 these are 2.05 R and 1.05 R for horizontal loads, and 1.67 R for the drop.

**§2 and §3** describe the round-4 nut slot. They change with the fix.

**BUILD_GUIDE step 3** (assembly job; DFM note A1):
- Replace "just enough to keep the bolt square" with the S1 wording above: oil the plates, and snug to 0.04 N·m.
- With the fix, the idler nut sits on its washer outside the wall. A 5.5 mm spanner can hold it, instead of a fingertip in the slot.

**Unchanged from round 3:** the jack-screw thread (B7 4.82, B8 14.4), the buttress lug, both axle bolts (class 12.9: B10 1.79, B11 2.66, A6 2.66), and the road-wheel, floor and lid rows. The round-3 advisories still apply:
- fully threaded A2-70 bolts are not enough (1.11);
- don't tighten the road-wheel bolts beyond a snug.

**Not checked here:** the sprocket's shaft-end rows (another reviewer) and the idler part itself. The fix changes the idler's hub length, so the idler job needs a re-check of its hub.

VERDICT: NEEDS_TEST

# Strength check: 20261026-rover-chassis (round 6)

strength-analyst (independent) · 2026-10-26.

Run from the project root with the CAD venv's interpreter: `/home/claude/.venv-cad/bin/python3 jobs/20261026-rover-chassis/strength_calc.py` (about 1.5 min). The script builds the round-6 chassis with build123d, probes the clamp, the lip and the stops on the solid, solves the clamp as a contact problem, and recomputes the rover mass from every rover `part.stl`.

**Result: every verdict row passes: 0 of 70 below its required SF.** The lowest is **3.01**, at B15: the strip shear in the 5 cm front-corner drop, unchanged from round 5.

The verdict is NEEDS_TEST, not PASS, only because there is no measured data. `library/materials.csv` has only its header row, so the PETG allowables are the skill's placeholders, and the method caps the verdict at NEEDS_TEST. The proof tests that settle it are already in spec §8 (tests 1–3; see below).

| | Round 5 (STOP_W 1.5) | Round 5's FIX prediction | **Round 6 as built** | Required |
|---|---|---|---|---|
| Rear stop root bending, reverse stall 29.8 N (B18) | 2.75 FAIL | 4.88 | **4.88** | 3 |
| … everyday 16.4 N cyclic / sustained 10 N | 4.99 / 8.17 | 8.88 / 14.53 | **8.88 / 14.53** | 4 |
| … 44 N proof pull (advisory) | 1.85 | 3.29 | **3.29** | 1 |
| … plate bearing on the stop's tip only (advisory) | 1.37 | 2.44 | **2.44** | 3 (advisory) |
| Lowest verdict row | 2.75 (B18) | 3.01 (B15) | **3.01 (B15)** | 3 |

## What round 6 changed, and what the script does with it

- **The change.** `model.py` `STOP_W` went from 1.5 to 2.0, and nothing else changed (git cc1b341). The inner faces stay at x 108 and 129, so the stops now span x 106–108 and 129–131 and the lip runs x 106–131.
- **The script, updated without changing any load case or method:**
  - **The round-5 probe** that stopped it (l.425–428, "void at (106.4, 38.5, Z_A)") now checks the round-6 stops:
    - `STOP_W` 2.0 in model.py;
    - rear stop solid at x 106.1 and 107, void at 105.9 and 108.1;
    - front stop solid at x 130 and 130.9, void at 128.9 and 131.1;
    - the rear stop's root solid to the wall over its full 2.0 (x 106.1 and 107.9, \|y\| 37.5–38.95, Z_A − 5.6 / 0 / + 5.1).
    
    All the probes pass. The script prints "between stops x 106.0–108.0 and 129.0–131.0".
  - **The B18 verdict rows** already read `p.STOP_W` from model.py, so they are now the round-6 stops. Their load cases are unchanged: friction drag min(R, µ(T + P)), µ 0.2 oiled, the 89 N snug, Kt 2.5, arm 0.5, a 10.9 mm root, and no credit for the jack screw or the PETG face friction.
  - **Round 5's "FIX STOP_W 2.0" advisory rows** would now duplicate the verdict rows, so they are replaced by two advisory rows:
    - a **round 5 as built (1.5)** reference row, which gives back round 5's 2.75 exactly, so the functions are unchanged;
    - the optional `STOP_W` 2.5 tip-only row (3.81).
  - **The labels** "round-5 chassis" and "mass check (round 5)" now say round 6. The clamp itself (`CLAMP_R5`) is round 5's design, unchanged, and keeps its name.
- **Every row was re-run.** Apart from the B18 stop rows (and the stop's advisory rows), every row is identical to round 5 to two decimals, including all 7 sensitivities, the proof rows and the round-4 FIX cross-check. Mass: chassis 130.9 g, rover 631 g at the print minima, the same as round 5 (the stops add 0.03 g). The design mass of 649 g still covers it by 2.8 %.

## Load cases

The shared block is unchanged from round 3. Every case is round 5's.

| Load | Value used | Source | Duration |
|---|---|---|---|
| Mass | **649 g** (W 6.37 N) | Spec §4. Estimate 631 g at the print minima, 725 g if every printed part were solid | n/a |
| Stall torque | 160 N·mm design → 9.89 N pull; 182 N·mm proof → 11.25 N | Spec §4; the §8 gate | short-term |
| Idler radial | Reverse stall 29.8 N (both runs tight), proof 32.5, everyday 16.4, sustained 10 | Spec §4 | short-term / proof / cyclic / sustained |
| Idler yaw moment | R × 29.6 (track plane 55 − jack line 25.4): 882 / 962 / 485 / 296 N·mm | Geometry | as above |
| 5 cm drop | **31.8 N per axle**, upward at the idler's track plane; tilt moment 795 N·mm about the head plate's bearing face | Round-3 convention, 5 mm stopping distance | short-term |
| Friction drag on the nut plate (a demand on the stops, never a credit) | min(R, µ(T + P)): µ 0.2 oiled, T from the clamp model, P 89 N (0.04 N·m snug, K 0.15) → 10 / 16.4 / 29.8 N into the rear stop; while tensioning, µP = 17.8 N into the front stop | BUILD_GUIDE step 3 (oil, snug); S1 | as the idler load; tensioning a few times |
| Tensioning slide (S1) | Jack thrust 2µP + 10 N = 46 N | DFM S1 | short-term |
| Proof loads | 49 N hung from the idler at mid-slot; 44 N rearward pull at the slot's front end; 32.5 N reverse stall | Spec §8 tests 1 and 2 | 1 min / 1 s × 5 |
| Side, motor reaction, lid lift, assembly | 3 N per track; 160 N·mm; 2 × W on 4 inserts; the snug | Rounds 3–4 | as round 4 |

## Assumptions

All of round 5's assumptions are unchanged; see the round-5 report in git 44880d0 for the full list. The ones that matter here:

- **End stops (B18).**
  - **Friction is a demand, not a credit.** At a reverse stall the bolt body yaws (≤ 2.43 mrad) about the jack screw's tip. The nut-side Ø9 washer, 14.6 mm from the jack line, then drags the nut plate rearward into its stop with µ(T + P), capped at R.
  - **Section and loading.**
    - Bearing is on 1.0 mm of the plate's thickness (the stop is 1.0 proud) × 10 mm.
    - Root bending is at arm 0.5 with Kt 2.5 (a sharp corner on the loaded face). Shear is 1.5 V/A.
    - The root section is now **2.0 × 10.9** (Z_A − 5.7 to + 5.2).
    - All of this is in-plane: the root is a vertical plane, and the stress runs along the layers.
  - **No credit taken for:**
    - the lip merged under the stop (counting it gives 5.55, advisory);
    - the jack screw's share;
    - the PETG face's friction behind the plate.
  - **The rear stop governs.** It stands on the flat outer face. The front stop also merges into the r6 corner fillet and, from x 130.5, the front wall, so it is stiffer. It is checked with the same section anyway.
- **Idler clamp (B5, B6, B12, B13, B15, B16, B17).** This is round 4's 1-D contact model as round 5 generalised it. It takes the as-built z-bands, puts the bolt on the printed slot floor (Z_A − 0.2), and checks the plates at 1.9 mm (14 ga). No friction or preload is credited. The stops are outside the plates' footprint, so they don't touch it.
- **Drop shear (B4).** All 31.8 N goes through the head plate's top back edge on the 45° roof. The nut plate has nothing over it, and the stops only locate it in X.

## Allowables and sources

- **No measured data.** `library/materials.csv` has only its header row, and no job has a datasheet in `inputs/`. The skill's placeholders apply:
  - PETG 25 MPa in-plane, 12.5 MPa across the layers;
  - E 1.8 GPa, ν 0.35;
  - shear allowable 0.5 × normal.
  - **So PASS isn't possible; NEEDS_TEST is the best verdict.**
- **Direction.**
  - In-plane: bearing on layer faces and 45° flanks; the stops' and the lip's root bending and shear (vertical root planes).
  - Across the layers: the strips' σz and their shear on the root plane.
- **Required SF:**
  - 3 for short-term static loads;
  - 4 for cyclic or sustained loads;
  - 1.5 on yield for steel (class 12.9: 1080 MPa; plates and washers: 200; N20 shaft: 350);
  - 1.0 on the knocked-down allowable for proof loads.
- **Temperature.** 40 °C service against a PETG softening point of about 70 °C: more than 20 °C apart.

## Proof test required (NEEDS_TEST): spec §8 tests 1–3, already in the acceptance criteria

The spec already has the proof tests the verdict needs. Nothing has to be added. Predicted SFs (proof SF required 1.0; all met):

| §8 test | Load, duration | Governing rows (round 6) | Pass criterion (spec §8) |
|---|---|---|---|
| 1, hang | 5 kg (49 N, 1.5 × 31.8 N) for 1 min from the wheel rim's middle, at a road wheel and at an idler bolt **at mid-slot** | idler: strip shear and bottom strip root **1.96** (worst at x 120 = mid-slot; 2.54 at the front end); lip root 5.60; bolt on the slot floor 12.2. Road wheel: nut trap 2.09, boss 2.28 | no crack or whitening (the PETG round each plate, the lip and both stops included); bolts square (≤ 0.5 mm runout); idler disc moved ≤ 0.3 mm |
| 1, pull | 4.5 kg (44 N, 1.5 × 29.8 N) rearward along the track line for 1 min, bolt **at the slot's front end** | head plate on PETG 4.35 and strip root 4.90 (both worst at x 124 = the front end); **rear stop root 3.29**, shear 4.12, bearing 5.66 | as above |
| 2, stall | 100 % PWM, 1 s × 5, forward and reverse (32.5 N on the idler) | strip root 6.65; head plate on PETG 5.90 | no crack (the PETG round each plate included); disc moved ≤ 0.3 mm |
| 3, drop | 5 cm, flat and on each of the four corners | B15 strip shear 3.01 (verdict row), B15 roots 3.02 / 3.16 | no cracks (round each plate included); bolts square |

## Spec §8 against the round-6 design: it matches

I checked all four of round 5's requested changes in spec.md §8 (git 4b91608) and the idler's spec:

1. **Hang at mid-slot, pull at the front end.** Test 1: "Repeat on an idler bolt at mid-slot, with the jack screw set. Then turn the jack screw in until the bolt is at the slot's front end and … pull 4.5 kg (44 N) rearward". ✓
   - The script confirms each is at its worst position: "49 N hang worst at x 120 (nut side) / 120 (head side)" and "44 N pull worst at x 124 (strip) / 124 (head plate)".
2. **The stops are named in the pass criteria.** "the PETG round each idler plate (the recess edges inside the tub; the lip, both end stops and the wall face round the nut plate outside)". ✓
3. **The disc is measured with the idler pulled rearward.** "with the idler pulled rearward by hand along the track line (about 0.5 kg on the strap) for both readings". ✓ Test 2 reads "measured as in test 1". ✓
4. **The idler's spec, test 1.** "Fit the idler on its bolt at the front end of the chassis slot", with the same disc-measurement wording. ✓

The round-6 change doesn't affect §8. The stops' width isn't stated there, and the predicted proof SFs went up (rear stop at the 44 N pull: 1.85 → 3.29). One optional cosmetic edit: the heading says "strength rounds 2–5" and could say 2–6. No wording change is needed.

## Results (`strength_calc.py` output)

Verdict rows:

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
| 10 | B5 idler head plate on the recess floor (zone mean, peak 1.7 at x 128.8, bolt at x 124), pretension 10 N sustained (P 0 or 80 N) | XY | 1.30 | 25.0 | 19.18 | 4.0 | OK |
| 11 | B6 idler nut plate on the wall's outer face (zone mean, peak 0.7 at x 108.2, bolt at x 116), pretension 10 N sustained (P 0 or 80 N) | XY | 0.51 | 25.0 | 48.92 | 4.0 | OK |
| 12 | B12 8.0 mm PETG between the plates: strip root beside the bolt slot, bending across layers (Kt 2.5 at every root), pretension 10 N sustained (P 0 or 80 N) | Z | 0.59 | 12.5 | 21.04 | 4.0 | OK |
| 13 | B13 strip root, shear along the layer, pretension 10 N sustained (P 0 or 80 N) | Z shear | 0.31 | 6.2 | 20.08 | 4.0 | OK |
| 14 | B5 idler head plate on the recess floor (zone mean, peak 2.8 at x 128.8, bolt at x 124), everyday reverse 16.4 N cyclic | XY | 2.13 | 25.0 | 11.72 | 4.0 | OK |
| 15 | B6 idler nut plate on the wall's outer face (zone mean, peak 1.1 at x 108.2, bolt at x 116), everyday reverse 16.4 N cyclic | XY | 0.84 | 25.0 | 29.89 | 4.0 | OK |
| 16 | B12 8.0 mm PETG between the plates: strip root beside the bolt slot, bending across layers (Kt 2.5 at every root), everyday reverse 16.4 N cyclic | Z | 0.95 | 12.5 | 13.20 | 4.0 | OK |
| 17 | B13 strip root, shear along the layer, everyday reverse 16.4 N cyclic | Z shear | 0.50 | 6.2 | 12.60 | 4.0 | OK |
| 18 | B5 idler head plate on the recess floor (zone mean, peak 5.1 at x 128.8, bolt at x 124), reverse stall 29.8 N | XY | 3.88 | 25.0 | 6.44 | 3.0 | OK |
| 19 | B6 idler nut plate on the wall's outer face (zone mean, peak 2.0 at x 108.2, bolt at x 116), reverse stall 29.8 N | XY | 1.52 | 25.0 | 16.43 | 3.0 | OK |
| 20 | B12 8.0 mm PETG between the plates: strip root beside the bolt slot, bending across layers (Kt 2.5 at every root), reverse stall 29.8 N | Z | 1.72 | 12.5 | 7.26 | 3.0 | OK |
| 21 | B13 strip root, shear along the layer, reverse stall 29.8 N | Z shear | 0.90 | 6.2 | 6.93 | 3.0 | OK |
| 22 | B15 top strip root under the nut plate (outer face; Kt 2.5), across layers, 5 cm front corner | Z | 3.96 | 12.5 | 3.16 | 3.0 | OK |
| 23 | B15 bottom strip root under the head plate (inner face: the recess floor's sharp edge, Kt 2.5), 5 cm front corner | Z | 4.14 | 12.5 | 3.02 | 3.0 | OK |
| 24 | B15 strip root, shear along the layer, 5 cm front corner | Z shear | 2.07 | 6.2 | 3.01 | 3.0 | OK |
| 25 | B4 head plate's top back edge on the recess's 45° roof (all of the drop shear on a 0.3 mm wide line, 20.6 long), 5 cm front corner | XY | 5.15 | 25.0 | 4.85 | 3.0 | OK |
| 26 | B16 steel head plate bending (slotted section, 1.9 thick), reverse stall | steel σy 200 | 50.67 | 200.0 | 3.95 | 1.5 | OK |
| 27 | B16 steel nut plate bending (slotted section, 1.9 thick), reverse stall | steel σy 200 | 60.71 | 200.0 | 3.29 | 1.5 | OK |
| 28 | B17 Ø9 washer on the nut plate: mean steel bearing at T 127 N, reverse stall | steel σy 200 | 3.48 | 200.0 | 57.51 | 1.5 | OK |
| 29 | B17 Ø9 washer on the head plate: mean steel bearing at T 127 N, reverse stall | steel σy 200 | 3.48 | 200.0 | 57.51 | 1.5 | OK |
| 30 | B17 M3 nut's face on its Ø9 washer (Ø5.5 - Ø3.2) at T 127 N, reverse stall | steel σy 200 | 8.07 | 200.0 | 24.78 | 1.5 | OK |
| 31 | B18 nut plate's end on its end stop: bearing (1.0 x 10), rear stop, friction drag min(R, mu (T + P)) = min(10.0, 0.2 x (43 + 89)) = 10.0 N, pretension 10 N sustained | XY | 1.00 | 25.0 | 25.00 | 4.0 | OK |
| 32 | B18 end stop root (2.0 x 10.9 at the wall face, plate at arm 0.5): bending (Kt 2.5, sharp corner on the loaded face), rear stop, friction drag min(R, mu (T + P)) = min(10.0, 0.2 x (43 + 89)) = 10.0 N, pretension 10 N sustained | XY | 1.72 | 25.0 | 14.53 | 4.0 | OK |
| 33 | B18 end stop root: shear, rear stop, friction drag min(R, mu (T + P)) = min(10.0, 0.2 x (43 + 89)) = 10.0 N, pretension 10 N sustained | XY shear | 0.69 | 12.5 | 18.17 | 4.0 | OK |
| 34 | B18 nut plate's end on its end stop: bearing (1.0 x 10), rear stop, friction drag min(R, mu (T + P)) = min(16.4, 0.2 x (70 + 89)) = 16.4 N, everyday reverse 16.4 N cyclic | XY | 1.64 | 25.0 | 15.27 | 4.0 | OK |
| 35 | B18 end stop root (2.0 x 10.9 at the wall face, plate at arm 0.5): bending (Kt 2.5, sharp corner on the loaded face), rear stop, friction drag min(R, mu (T + P)) = min(16.4, 0.2 x (70 + 89)) = 16.4 N, everyday reverse 16.4 N cyclic | XY | 2.82 | 25.0 | 8.88 | 4.0 | OK |
| 36 | B18 end stop root: shear, rear stop, friction drag min(R, mu (T + P)) = min(16.4, 0.2 x (70 + 89)) = 16.4 N, everyday reverse 16.4 N cyclic | XY shear | 1.13 | 12.5 | 11.10 | 4.0 | OK |
| 37 | B18 nut plate's end on its end stop: bearing (1.0 x 10), rear stop, friction drag min(R, mu (T + P)) = min(29.8, 0.2 x (127 + 89)) = 29.8 N, reverse stall 29.8 N | XY | 2.98 | 25.0 | 8.40 | 3.0 | OK |
| 38 | B18 end stop root (2.0 x 10.9 at the wall face, plate at arm 0.5): bending (Kt 2.5, sharp corner on the loaded face), rear stop, friction drag min(R, mu (T + P)) = min(29.8, 0.2 x (127 + 89)) = 29.8 N, reverse stall 29.8 N | XY | 5.12 | 25.0 | 4.88 | 3.0 | OK |
| 39 | B18 end stop root: shear, rear stop, friction drag min(R, mu (T + P)) = min(29.8, 0.2 x (127 + 89)) = 29.8 N, reverse stall 29.8 N | XY shear | 2.05 | 12.5 | 6.10 | 3.0 | OK |
| 40 | B18 nut plate's end on its end stop: bearing (1.0 x 10), front stop, tensioning (the jack slides the snug bolt forward; the washer drags the plate, mu P 17.8 N) | XY | 1.78 | 25.0 | 14.06 | 3.0 | OK |
| 41 | B18 end stop root (2.0 x 10.9 at the wall face, plate at arm 0.5): bending (Kt 2.5, sharp corner on the loaded face), front stop, tensioning (the jack slides the snug bolt forward; the washer drags the plate, mu P 17.8 N) | XY | 3.06 | 25.0 | 8.17 | 3.0 | OK |
| 42 | B18 end stop root: shear, front stop, tensioning (the jack slides the snug bolt forward; the washer drags the plate, mu P 17.8 N) | XY shear | 1.22 | 12.5 | 10.22 | 3.0 | OK |
| 43 | B18h head plate's end on the recess end (x 108, solid buttress; 1.9 x 10), reverse stall 29.8 N | XY | 1.57 | 25.0 | 15.95 | 3.0 | OK |
| 44 | B19 lip under the nut plate, root bending (Kt 2.5): the plate's own mass at the drop's 20 g (0.52 N) | XY | 0.05 | 25.0 | 531.77 | 3.0 | OK |
| 45 | B7 jack-screw thread strip-out (6.5 mm, Ø2.6 pilot), reverse stall 29.8 N | Z shear | 1.30 | 6.2 | 4.82 | 3.0 | OK |
| 46 | B8 jack-screw thread, pretension 10 N sustained | Z shear | 0.44 | 6.2 | 14.36 | 4.0 | OK |
| 47 | B7t jack-screw thread while tensioning: snug 0.04 N*m (K 0.15: P 89 N), oiled plates (mu 0.2): thrust 46 N | Z shear | 1.98 | 6.2 | 3.15 | 3.0 | OK |
| 48 | B9 buttress lug at the block face (y 28): bending, reverse stall (Kt 2.5) | XY | 1.96 | 25.0 | 12.73 | 3.0 | OK |
| 49 | B10 idler M3 x 40 class 12.9: bending at the head face (y 28), reverse stall x 27 | steel σy 1080 | 602.13 | 1080.0 | 1.79 | 1.5 | OK |
| 50 | B11 idler M3 x 40 class 12.9: bending at the outer face, 5 cm front corner x 17 | steel σy 1080 | 405.30 | 1080.0 | 2.66 | 1.5 | OK |
| 51 | C1 skin (2 mm) diaphragm shear across layers, 5 cm rear corner: nacelle reaction 53.3 N, skin share 48 % | Z shear | 0.96 | 6.2 | 6.52 | 3.0 | OK |
| 52 | C2 nacelle wall root bending (pocket face in tension, no notch), 5 cm rear corner, wall share 73 % | XY | 7.04 | 25.0 | 3.55 | 3.0 | OK |
| 53 | C3 nacelle root, tube bending (sharp outer corner in tension, Kt 2.5), 5 cm rear corner | XY | 0.75 | 25.0 | 33.26 | 3.0 | OK |
| 54 | C4 nacelle root, tube shear (2 V/A), 5 cm rear corner | Z shear | 0.99 | 6.2 | 6.29 | 3.0 | OK |
| 55 | C5 gearbox front edge bearing on the pocket faces (1 mm x face width), 5 cm rear corner | XY | 3.77 | 25.0 | 6.64 | 3.0 | OK |
| 56 | C6 skin diaphragm shear, track stall 19.9 N (horizontal, 2.05 R) | Z shear | 0.73 | 6.2 | 8.52 | 3.0 | OK |
| 57 | C7 nacelle wall root bending, track stall 19.9 N | XY | 5.38 | 25.0 | 4.64 | 3.0 | OK |
| 58 | C6 skin diaphragm shear, track pretension 10 N sustained (horizontal, 2.05 R) | Z shear | 0.37 | 6.2 | 16.95 | 4.0 | OK |
| 59 | C7 nacelle wall root bending, track pretension 10 N sustained | XY | 2.71 | 25.0 | 9.24 | 4.0 | OK |
| 60 | C8 reaction torque 160 N*mm: gearbox corner bearing (13.3 N over 9 x 1 mm) | XY | 1.48 | 25.0 | 16.88 | 3.0 | OK |
| 61 | C9 skin out of plane: side 3 N inward on the thrust washer (annular plate a 6.29, hole r 2.25) | Z | 0.41 | 12.5 | 30.48 | 4.0 | OK |
| 62 | C10 skin out of plane: side 3 N outward on the gearbox face, the motor's outward stop (Kt 2.5 at the pocket corner) | Z | 0.44 | 12.5 | 28.43 | 4.0 | OK |
| 63 | C11 wall bending round the motor housing (Ø22.4 equivalent, Kt 1.6), 5 cm rear corner | Z | 2.85 | 12.5 | 4.38 | 3.0 | OK |
| 64 | C12 trough cheek bridge over the tie tunnel: tie 51 N (can rear reaction 20.8 N + 30 N preload) | XY | 0.38 | 25.0 | 66.27 | 3.0 | OK |
| 65 | C13 N20 shaft (bought steel), arm 11.0, Z_min 1.911 mm³: stall 19.9 N (target 1.5 on yield; the Architect's 2 also met) | steel σy 350 | 114.48 | 350.0 | 3.06 | 1.5 | OK |
| 66 | C13 N20 shaft, arm 11.0: 5 cm corner 31.8 N | steel σy 350 | 183.23 | 350.0 | 1.91 | 1.5 | OK |
| 67 | D1 floor mid-span under the battery, 5 cm (20 g x 135 g) | XY | 3.69 | 25.0 | 6.77 | 3.0 | OK |
| 68 | D2 floor at the strap slots |y| 26.0 (Kt 2.5, square ends), 5 cm | XY | 4.11 | 25.0 | 6.08 | 3.0 | OK |
| 69 | E1 insert knurl shear-out of the column, lifted by the lid 3.2 N per insert | Z shear | 0.04 | 6.2 | 140.63 | 3.0 | OK |
| 70 | E2 column tension (Z) round the insert, lifted by the lid | Z | 0.05 | 12.5 | 259.06 | 3.0 | OK |

Advisory (not in the verdict: peaks, bounds, sensitivities, proof loads, the round-5 reference row, the 2.5 option, the S1 table, bought parts):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| A4/A5 Winkler peaks: nut edge 10.4, inner hole edge (peak), 5 cm drop | XY | 11.43 | 25.0 | 2.19 | 3.0 | no |
| proof 5 kg (49 N) at the wheel rim centre: boss collar | Z | 5.48 | 12.5 | 2.28 | 1.0 | OK |
| proof 5 kg at the wheel rim centre: nut-trap bearing | XY | 11.95 | 25.0 | 2.09 | 1.0 | OK |
| proof 5 kg at the rim centre: M3 class 12.9 at the outer face | steel σy 1080 | 624.50 | 1080.0 | 1.73 | 1.0 | OK |
| if A2-70 (fully threaded stainless) bolts are fitted instead: 5 cm drop | steel σy 450 | 405.30 | 450.0 | 1.11 | 1.5 | no |
| B5 head plate on PETG, reverse stall: PEAK (at a width step of the 1-D model) 5.1 at x 128.8 | XY | 5.07 | 25.0 | 4.93 | 3.0 | OK |
| B6 nut plate on PETG, reverse stall: PEAK 2.0 at x 108.2 | XY | 1.99 | 25.0 | 12.55 | 3.0 | OK |
| B15 bottom strip root under the head plate, 5 cm front corner, WITHOUT the corner Kt (nominal) | Z | 1.65 | 12.5 | 7.55 | 3.0 | OK |
| B15 top strip root under the nut plate with Kt 1.0 (the outer face is flat at that root), 5 cm front corner | Z | 1.58 | 12.5 | 7.89 | 3.0 | OK |
| sensitivity, roots rigid (root_soft 1.0): strip root (Kt 2.5), reverse stall | Z | 1.80 | 12.5 | 6.94 | 3.0 | OK |
| sensitivity, roots rigid (root_soft 1.0): strip roots (Kt 2.5), 5 cm front corner | Z | 4.57 | 12.5 | 2.74 | 3.0 | no |
| sensitivity, roots rigid (root_soft 1.0): strip shear, 5 cm front corner | Z shear | 2.28 | 6.2 | 2.74 | 3.0 | no |
| sensitivity, roots twice as soft (2.0): strip root (Kt 2.5), reverse stall | Z | 1.57 | 12.5 | 7.98 | 3.0 | OK |
| sensitivity, roots twice as soft (2.0): strip roots (Kt 2.5), 5 cm front corner | Z | 3.39 | 12.5 | 3.68 | 3.0 | OK |
| sensitivity, roots twice as soft (2.0): strip shear, 5 cm front corner | Z shear | 1.72 | 6.2 | 3.64 | 3.0 | OK |
| sensitivity, uncut band 3x softer (k_end 10000): strip root (Kt 2.5), reverse stall | Z | 1.70 | 12.5 | 7.36 | 3.0 | OK |
| sensitivity, uncut band 3x softer (k_end 10000): strip roots (Kt 2.5), 5 cm front corner | Z | 4.67 | 12.5 | 2.67 | 3.0 | no |
| sensitivity, uncut band 3x softer (k_end 10000): strip shear, 5 cm front corner | Z shear | 2.32 | 6.2 | 2.69 | 3.0 | no |
| sensitivity, uncut band 3x stiffer (k_end 90000): strip root (Kt 2.5), reverse stall | Z | 1.73 | 12.5 | 7.21 | 3.0 | OK |
| sensitivity, uncut band 3x stiffer (k_end 90000): strip roots (Kt 2.5), 5 cm front corner | Z | 3.49 | 12.5 | 3.58 | 3.0 | OK |
| sensitivity, uncut band 3x stiffer (k_end 90000): strip shear, 5 cm front corner | Z shear | 1.77 | 6.2 | 3.53 | 3.0 | OK |
| sensitivity, metric 2.0 mm plates: strip root (Kt 2.5), reverse stall | Z | 1.63 | 12.5 | 7.66 | 3.0 | OK |
| sensitivity, metric 2.0 mm plates: strip roots (Kt 2.5), 5 cm front corner | Z | 3.96 | 12.5 | 3.15 | 3.0 | OK |
| sensitivity, metric 2.0 mm plates: strip shear, 5 cm front corner | Z shear | 1.99 | 6.2 | 3.14 | 3.0 | OK |
| sensitivity, bolt on the CAD slot floor (Z_A - 0.3): strip root (Kt 2.5), reverse stall | Z | 1.72 | 12.5 | 7.26 | 3.0 | OK |
| sensitivity, bolt on the CAD slot floor (Z_A - 0.3): strip roots (Kt 2.5), 5 cm front corner | Z | 4.12 | 12.5 | 3.03 | 3.0 | OK |
| sensitivity, bolt on the CAD slot floor (Z_A - 0.3): strip shear, 5 cm front corner | Z shear | 2.08 | 6.2 | 3.00 | 3.0 | OK |
| sensitivity, bolt up against the plates' slot tops (Z_A + 0.0): strip root (Kt 2.5), reverse stall | Z | 1.72 | 12.5 | 7.28 | 3.0 | OK |
| sensitivity, bolt up against the plates' slot tops (Z_A + 0.0): strip roots (Kt 2.5), 5 cm front corner | Z | 4.16 | 12.5 | 3.00 | 3.0 | OK |
| sensitivity, bolt up against the plates' slot tops (Z_A + 0.0): strip shear, 5 cm front corner | Z shear | 2.06 | 6.2 | 3.03 | 3.0 | OK |
| sensitivity, washers bearing only to r 3.55 (head/nut edge + 45° through the washer): head plate on PETG (zone mean), reverse stall | XY | 4.58 | 25.0 | 5.46 | 3.0 | OK |
| sensitivity, washers bearing only to r 3.55: strip root, reverse stall | Z | 1.98 | 12.5 | 6.32 | 3.0 | OK |
| proof 32.5 N reverse stall (§8 test 2), bolt at the slot's front end (x 124): strip root (Kt 2.5) | Z | 1.88 | 12.5 | 6.65 | 1.0 | OK |
| proof 32.5 N reverse stall, bolt at the slot's front end (x 124): head plate on PETG (zone mean) | XY | 4.24 | 25.0 | 5.90 | 1.0 | OK |
| proof 44 N rearward pull (§8 test 1), bolt at the slot's front end (x 124): strip root (Kt 2.5) | Z | 2.55 | 12.5 | 4.90 | 1.0 | OK |
| proof 44 N rearward pull, bolt at the slot's front end (x 124): strip shear | Z shear | 1.34 | 6.2 | 4.67 | 1.0 | OK |
| proof 44 N rearward pull, bolt at the slot's front end (x 124): head plate on PETG (zone mean) | XY | 5.75 | 25.0 | 4.35 | 1.0 | OK |
| proof 44 N rearward pull, bolt at the slot's front end (x 124): nut plate on PETG (zone mean) | XY | 2.04 | 25.0 | 12.23 | 1.0 | OK |
| proof 49 N hung from the idler (§8 test 1, pulls down), bolt at the slot's front end (x 124): bottom strip root under the nut plate (the lip's corner, Kt 2.5) | Z | 4.88 | 12.5 | 2.56 | 1.0 | OK |
| proof 49 N hang, bolt at the slot's front end (x 124): top strip root under the head plate (Kt 2.5) | Z | 4.70 | 12.5 | 2.66 | 1.0 | OK |
| proof 49 N hang, bolt at the slot's front end (x 124): strip shear | Z shear | 2.46 | 6.2 | 2.54 | 1.0 | OK |
| proof 32.5 N reverse stall (§8 test 2), worst slot position: strip root (Kt 2.5) | Z | 1.88 | 12.5 | 6.65 | 1.0 | OK |
| proof 32.5 N reverse stall, worst slot position: head plate on PETG (zone mean) | XY | 4.24 | 25.0 | 5.90 | 1.0 | OK |
| proof 44 N rearward pull (§8 test 1), worst slot position: strip root (Kt 2.5) | Z | 2.55 | 12.5 | 4.90 | 1.0 | OK |
| proof 44 N rearward pull, worst slot position: strip shear | Z shear | 1.34 | 6.2 | 4.67 | 1.0 | OK |
| proof 44 N rearward pull, worst slot position: head plate on PETG (zone mean) | XY | 5.75 | 25.0 | 4.35 | 1.0 | OK |
| proof 44 N rearward pull, worst slot position: nut plate on PETG (zone mean) | XY | 2.26 | 25.0 | 11.08 | 1.0 | OK |
| proof 49 N hung from the idler (§8 test 1, pulls down), worst slot position: bottom strip root under the nut plate (the lip's corner, Kt 2.5) | Z | 6.37 | 12.5 | 1.96 | 1.0 | OK |
| proof 49 N hang, worst slot position: top strip root under the head plate (Kt 2.5) | Z | 6.10 | 12.5 | 2.05 | 1.0 | OK |
| proof 49 N hang, worst slot position: strip shear | Z shear | 3.20 | 6.2 | 1.96 | 1.0 | OK |
| B18 nut plate's end on its end stop: bearing (1.0 x 10), proof 44 N rearward pull (§8 test 1), rear stop, min(R, mu (T + P)) 44.1 N | XY | 4.41 | 25.0 | 5.66 | 1.0 | OK |
| B18 end stop root (2.0 x 10.9 at the wall face, plate at arm 0.5): bending (Kt 2.5, sharp corner on the loaded face), proof 44 N rearward pull (§8 test 1), rear stop, min(R, mu (T + P)) 44.1 N | XY | 7.59 | 25.0 | 3.29 | 1.0 | OK |
| B18 end stop root: shear, proof 44 N rearward pull (§8 test 1), rear stop, min(R, mu (T + P)) 44.1 N | XY shear | 3.04 | 12.5 | 4.12 | 1.0 | OK |
| proof 49 N hang: the nut plate's bottom edge on its lip (bound: all of it, 20.6 mm²) | XY | 2.38 | 25.0 | 10.50 | 1.0 | OK |
| proof 49 N hang: lip root bending (bound: all of it, Kt 2.5) | XY | 4.46 | 25.0 | 5.60 | 1.0 | OK |
| proof 49 N hang: the bolt on the PETG slot floor (Ø3 x 8) | XY | 2.04 | 25.0 | 12.23 | 1.0 | OK |
| proof 5 kg on the idler bolt: M3 class 12.9 at the outer face | steel σy 1080 | 624.50 | 1080.0 | 1.73 | 1.0 | OK |
| B18 nut plate's end on its end stop: bearing (1.0 x 10), if the plates are dry (mu 0.6): rear stop, reverse stall, min(R, mu (T + P)) 29.8 N | XY | 2.98 | 25.0 | 8.40 | 3.0 | OK |
| B18 end stop root (2.0 x 10.9 at the wall face, plate at arm 0.5): bending (Kt 2.5, sharp corner on the loaded face), if the plates are dry (mu 0.6): rear stop, reverse stall, min(R, mu (T + P)) 29.8 N | XY | 5.12 | 25.0 | 4.88 | 3.0 | OK |
| B18 end stop root: shear, if the plates are dry (mu 0.6): rear stop, reverse stall, min(R, mu (T + P)) 29.8 N | XY shear | 2.05 | 12.5 | 6.10 | 3.0 | OK |
| end stop root bending with the plate bearing on the stop's outer edge only (arm 1.0), reverse stall 29.8 N (Kt 2.5) | XY | 10.24 | 25.0 | 2.44 | 3.0 | no |
| end stop root bending if the merged lip under it is counted (section 2.0 x 12.4), reverse stall (Kt 2.5) | XY | 4.50 | 25.0 | 5.55 | 3.0 | OK |
| B18 nut plate's end on its end stop: bearing (1.0 x 10), if the snug has crept away (P 0, prying T up to 127 N only): rear stop, reverse stall 25.4 N | XY | 2.54 | 25.0 | 9.85 | 3.0 | OK |
| B18 end stop root (2.0 x 10.9 at the wall face, plate at arm 0.5): bending (Kt 2.5, sharp corner on the loaded face), if the snug has crept away (P 0, prying T up to 127 N only): rear stop, reverse stall 25.4 N | XY | 4.36 | 25.0 | 5.73 | 3.0 | OK |
| B18 end stop root: shear, if the snug has crept away (P 0, prying T up to 127 N only): rear stop, reverse stall 25.4 N | XY shear | 1.75 | 12.5 | 7.16 | 3.0 | OK |
| assembly, if the nut is turned instead of the head (oiled, mu 0.2, P 89 N): plate corner on the lip (7.5 N on 2 x 1.0) | XY | 3.74 | 25.0 | 6.69 | 3.0 | OK |
| assembly, if the nut is turned instead of the head (oiled): lip root bending over 4 mm (Kt 2.5) | XY | 3.50 | 25.0 | 7.13 | 3.0 | OK |
| assembly, if the nut is turned instead of the head (dry, mu 0.6, P 67 N): plate corner on the lip (16.8 N on 2 x 1.0) | XY | 8.41 | 25.0 | 2.97 | 3.0 | no |
| assembly, if the nut is turned instead of the head (dry): lip root bending over 4 mm (Kt 2.5) | XY | 7.88 | 25.0 | 3.17 | 3.0 | OK |
| round 5 as built, STOP_W 1.5 (for reference; round 5: 2.75): end stop root bending (Kt 2.5), reverse stall (29.8 N) | XY | 9.11 | 25.0 | 2.75 | 3.0 | no |
| option STOP_W 2.5 (more margin, not required): end stop root bending, the plate on the stop's outer edge only (arm 1.0), reverse stall | XY | 6.56 | 25.0 | 3.81 | 3.0 | OK |
| option (not required): 1 x 45° chamfer on the recess floor's edge (Kt 1.6): bottom strip root, 5 cm front corner | Z | 2.65 | 12.5 | 4.72 | 3.0 | OK |
| round 4 FIX model, recomputed: head plate on PETG (zone mean), reverse stall (round 4: 6.45) | XY | 3.88 | 25.0 | 6.45 | 3.0 | OK |
| round 4 FIX model, recomputed: bottom strip under the head plate, 5 cm front corner (round 4: 3.02) | Z | 4.15 | 12.5 | 3.02 | 3.0 | OK |
| round 4 FIX model, recomputed: strip shear, 5 cm front corner (round 4: 3.05) | Z shear | 2.05 | 6.2 | 3.05 | 3.0 | OK |
| round 4 FIX model, recomputed: top strip under the nut plate, 5 cm front corner (round 4: 3.42) | Z | 3.65 | 12.5 | 3.42 | 3.0 | OK |
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

- **Lowest SF: 3.01** (required 3.0), at B15: the strip shear in the 5 cm front-corner drop, unchanged from round 5. The stop rows have left the bottom of the table: the lowest is 4.88 (the rear stop, reverse stall).
- **Drop rows** meet their SF up to a **5.0 cm** drop, limited by B15's strip shear (3.01).
  - That is a thin margin, unchanged from round 5: rigid roots give 2.74, and a 3× softer uncut band 2.67 (advisory).
  - The 5 mm stopping-distance convention isn't conservative (round 3), so §8 test 3 stays the evidence for the 5 cm rating.
- 0 of 70 verdict rows are below their required SF.

## Notes

- **The stop's tip-only reading (advisory, 2.44 against 3).**
  - It assumes an out-of-square plate end that bears only on the stop's outer edge, at arm 1.0 instead of 0.5. It was advisory in round 5 too, where it was 1.37.
  - BUILD_GUIDE §1 step 3 already says to deburr every edge, so the plate's end bears across the stop's face.
  - If the user wants that case covered as well, `STOP_W` 2.5 gives 3.81 (option, not required). The front stop would then end at x 131.5, where the r6 fillet's face is at \|y\| 37.45, so it would still join the corner from \|y\| 37.
- **Snug and oil (S1)** are unchanged: B7t 3.15 at the 0.04 N·m snug on oiled plates, and 1.60 dry, so oil is required. The stop rows use the same oiled µ. With dry plates (µ 0.6) the drag reaches the 29.8 N cap and the rear stop is still 4.88.
- **Spec §4 is still stale in two places** (round 4 note, unchanged):
  - "146 at the sketch's 80 % cap": the cap is 6.0 V, at most 130 N·mm;
  - "pocket edges carry 1.87 R and 0.87 R": 2.05 R and 1.05 R horizontally, 1.67 R in the drop.
- **Unchanged from round 5:**
  - the jack-screw thread (B7 4.82, B8 14.4) and the buttress lug (B9 12.7);
  - both axle bolts (B10 1.79, B11 2.66, A6 2.66, against 1.5 for steel);
  - the skin, nacelle and N20 shaft (C1 6.52, C2 3.55, C13 3.06 / 1.91);
  - the road-wheel, floor and lid rows.

  The round-3 advisories still apply: fully threaded A2-70 bolts aren't enough (1.11), and the road-wheel bolts should be no more than snug.
- **Not checked here:** the sprocket's own rows and the idler part (their own jobs' reports).

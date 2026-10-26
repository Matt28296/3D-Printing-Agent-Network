VERDICT: FAIL

# Strength check: 20261026-rover-chassis (round 5)

strength-analyst (independent) · 2026-10-26 · run from the project root with the CAD venv's interpreter: `/home/claude/.venv-cad/bin/python3 jobs/20261026-rover-chassis/strength_calc.py` (about 1.5 min). The script builds the round-5 chassis with build123d, probes the clamp, the lip and the stops on the solid, solves the clamp as a contact problem, and recomputes the rover mass from every rover `part.stl`.

**Result: FAIL, on one row.** Round 4's fix works as predicted. One row fails: the end stop the designer added. 1 of 70 verdict rows is below its required SF.

| Row | What fails | SF | Required |
|---|---|---|---|
| B18 | Root of the nut plate's **rear end stop** (1.5 × 10.9 × 1.0 proud), bending at its sharp corner (Kt 2.5) at a reverse stall. The washer under the nut drags the plate into the stop with up to the bolt's whole 29.8 N | **2.75** (lowest) | 3 |

- **Round 4's fix, as built.**
  - The clamp rows land on round 4's FIX predictions (table below). The lowest is the 5 cm drop: 3.02 at the recess floor's edge, and 3.01 for the strip shear.
  - With the nut slot gone, the yaw and tilt rows that failed in round 4 (0.61–2.31) are now at least 6.4 at the reverse stall and 11.7 everyday. In the drop they are 3.0–3.2.
- **What happens at the stop.**
  - Nothing in the clamp is credited to friction, but friction is still a *demand* on the stops.
  - At a reverse stall the bolt body yaws about the jack screw's tip (up to 2.43 mrad in the model). That moves the nut's Ø9 washer, 14.6 mm out from the jack line, about 0.035 mm rearward on the nut plate. A 1 mm PETG stop needs far less movement than that to build up the full friction force.
  - So the washer drags the plate into its rear stop with µ(T + P): 0.2 × (127 + 89) = 43 N on oiled plates with the step-3 snug, capped at the bolt's 29.8 N.
  - The stop is a 1.5 mm thick nub, loaded 0.5 mm from its root, with a sharp corner on the loaded face.
  - Counting no credit for the jack screw's share or for friction on the PETG face behind the plate:
    - root bending is 9.1 MPa with Kt 2.5, SF **2.75**;
    - shear is 4.58 and bearing 8.40.
- **Fix: `STOP_W` 1.5 → 2.0** in `model.py` (one parameter). The inner faces stay at x 108 and 129, so the stops become x 106.0–108 and 129–131. Stop rows then:
  - reverse stall **4.88**;
  - everyday 8.88, sustained 14.5;
  - 44 N proof 3.29.
  - Lowest SF in the whole check: **3.01**, the drop's strip shear, unchanged by the fix.
  - Both stops still fit:
    - the front one still joins the r6 corner fillet (its face is at |y| 37.66 at x 131; the stop starts at |y| 37);
    - the rear one stands on the flat face;
    - both stay 4 mm inboard of the links.
- **How close it is.** Three other honest readings give 3.1–3.2:
  - the lip under the stop counted in the stop's root section: 3.12;
  - the snug crept away, so the drag is 0.2 × 127 = 25.4 N: 3.22;
  - the jack screw's share credited.

  But the snug is there at the first reverse stalls (and in the §8 stall test), and with dry plates (µ 0.6) the cap is reached with or without it. The conservative row is the one the method asks for. The fix costs one parameter and no other change.
- **Everything else passes:**
  - the head plate on PETG, both strips, the steel plates, both Ø9 washers and the nut on its washer;
  - the head plate's edge on the 45° roof, which now carries all of the drop's shear (4.85);
  - the head plate on its recess end, the lip, the front stop while tensioning (4.60);
  - the jack screw at the snug (3.15), and every road-wheel, drivetrain, floor and lid row from round 4.

## Round 5 as built: the designer's items, checked

| Item | Designer / spec | Checked on the round-5 geometry |
|---|---|---|
| Nut slot deleted | 8.0 mm of solid PETG between the plates, only the bolt slot through it | `model.py`: no `_idler_nut_slot`. Probes are solid at \|y\| 30.1, 34.0, 36.0 and 37.9 (between Z_A − 4.4 and + 4.4) and void at 38.1. The bolt slot is the only cut (x 114.2–125.8, Z_A −1.80..+2.55), with uncut PETG beside it at x 113.5 and 126.5. assembly_check: `nut_slot_in_wall` false, `petg_between_the_plates_mm` 8.0 ✓ |
| Nut plate | 20.6 × 10 × 2, the head plate's twin, flat on the outer face | `rover_frame.NUT_PLATE` (20.6, 10) = `IDLER_PLATE`; slot 3.4 × 12 from 6 to 18 mm along. assembly_check: \|y\| 38–40, x 108.2–128.8, z Z_A −5.2..+4.8 ✓ |
| Lip | top Z_A − 5.2, 1.0 proud, 45° underside | Probes: solid under Z_A − 5.2 and void above; void at \|y\| 39.05; the 1.0 face ends at Z_A − 6.2; the underside passes Z_A − 7.15 at \|y\| 38.05, so 45° ✓. The lip top is level with the recess floor, so both plates rest at Z_A − 5.2 and their slots (Z_A −1.9..+1.5) line up ✓ |
| End stops | x 108 and 129, up to Z_A + 5.2 (`STOP_W` 1.5, 1.0 proud) | Probes: solid at x 107 and 130, void at 108.1 and 128.9 and at 106.4; top between Z_A + 5.1 and + 5.3 ✓. They hold the plate at x 108.2–128.8 (±0.2 CAD play), which is what the round-4 FIX assumed ✓. **They carry load** (B18): see above |
| Ø9 washer under the nut | DIN 9021 9 × 0.8 | `rover_frame.WASHER_WIDE` note; BUILD_GUIDE BOM 4 × DIN 9021; assembly_check stack 40.0–40.8 ✓ |
| Idler hub | 5.2 shorter; the part is 14.8 tall | `IDLER_HUB_Y0` 43.7 = 38 + 2 + 0.8 + 2.4 + 0.5; idler solid 14.8 tall (idler report) ✓ |
| Idler cock | about 1.9° (1.4° before) | 0.5 / 14.8 = 1.94° (0.5 / 20 = 1.43°) ✓. Checked in the idler report (lowest 4.19) |
| Snug | ≤ 0.04 N·m, plates oiled | Spec §2; BUILD_GUIDE step 3: oil on each plate where its Ø9 washer slides; 230 g at the 18 mm short arm = 0.041 N·m ✓ |
| Mass | design 649 g | 631 g at the print minima (+5 g on round 4: bigger nut plates and two washers); covered by 2.8 % ✓ |

**Round 4's FIX predictions against round 5.**
- Recomputed with this script's generalised functions on round 4's idealised FIX geometry, every FIX number comes back exactly (advisory rows "round 4 FIX model, recomputed").
- The differences below are therefore due to the as-built geometry. Both plates sit 0.2 mm low (Z_A − 5.2..+4.8 on the recess floor and lip), the bolt rests on the slot floor (Z_A − 0.2), and the plates were checked at 1.9 mm (14 ga).

| Case | Round 4 FIX | Round 5 as built |
|---|---|---|
| Head plate on PETG, reverse stall (zone mean) | 6.45 | B5 **6.44** |
| Nut plate on PETG, reverse stall | 16.33 | B6 **16.43** |
| Strip root, reverse stall / everyday / sustained | 7.59 / 13.81 / 21.98 | B12 **7.26 / 13.20 / 21.04** |
| Strip shear, reverse stall | 6.77 | B13 **6.93** |
| Bottom strip under the head plate (recess floor edge), 5 cm drop | 3.02 | B15 **3.02** (the plate now reaches the root: arm 1.65 instead of 1.80) |
| Strip shear, 5 cm drop | 3.05 | B15 **3.01** |
| Top strip under the nut plate, 5 cm drop | 3.42 | B15 **3.16** (the top strip's band is 0.2 higher: arm 1.53 instead of 1.43) |
| Steel plates, reverse stall | 3.50 (2.0 thick) | B16 **3.95 / 3.29** (1.9 thick) |
| Proof 32.5 / 44 / 49 N | 6.95 / 5.12 / 1.96 | **6.65 / 4.90 / 1.96** |

## Load cases

The shared block is unchanged from round 3 and identical in all six rover scripts.

| Load | Value used | Source | Duration |
|---|---|---|---|
| Mass | **649 g** (W 6.37 N) | Spec §4. Estimate 631 g at the print minima (round 5), 725 g if every printed part were solid | n/a |
| Stall torque | 160 N·mm design → 9.89 N pull; 182 N·mm proof → 11.25 N | Spec §4; the §8 gate | short-term |
| Idler radial | Reverse stall 29.8 N (both runs tight), proof 32.5, everyday 16.4, sustained 10 | Spec §4 | short-term / proof / cyclic / sustained |
| Idler yaw moment | R × 29.6 (track plane 55 − jack line 25.4): 882 / 962 / 485 / 296 N·mm | Geometry | as above |
| 5 cm drop | **31.8 N per axle**, upward at the idler's track plane: tilt moment 31.8 × (55 − 30) = 795 N·mm about the head plate's bearing face | Round-3 convention, 5 mm stopping distance | short-term |
| Friction drag on the nut plate (new) | min(R, µ(T + P)): µ 0.2 oiled, T from the clamp model, P 89 N (the 0.04 N·m snug, K 0.15) → 10 / 16.4 / 29.8 N; while tensioning µP = 17.8 N into the front stop | BUILD_GUIDE step 3 (oil, snug); S1 | as the idler load; tensioning a few times |
| Tensioning slide (S1) | Jack thrust 2µP + 10 N = 46 N | DFM S1 | short-term |
| Proof loads | 49 N hung from the idler; 44 N rearward pull; 32.5 N reverse stall | Spec §8 tests 1 and 2 | 1 min / 1 s × 5 |
| Side, motor reaction, lid lift, assembly | 3 N per track; 160 N·mm; 2 × W on 4 inserts; the snug | Round 3 / 4 | as round 4 |

## Assumptions

**Idler clamp (B5, B6, B12, B13, B15, B16, B17)**
- **Model.** Round 4's model, unchanged in method: a 1-D contact model along X at 0.1 mm stations.
  - Both plates are steel Hermite beams.
  - The 8.0 mm of PETG is modelled as through-thickness springs, with an out-of-plane ground spring at its mid node. Beside the bolt slot that spring is the PETG strips, as Timoshenko cantilevers with 30 % extra root compliance; elsewhere it is the uncut band, 30 000 N/mm per mm.
  - The bolt body is rigid, with the two Ø9 washers as rigid discs.
  - Contacts are compression-only. Bolt slot positions x 116–124, every 2 mm; the worst is kept.
- **Geometry, now taken as built in the bolt's frame.** The bolt rests on the printed slot floor at Z_A − 0.2. In that frame the steel is exactly symmetric: plates ±5.0, slot bands ±1.7, washers r 4.5. The PETG is not:
  - the 8 mm band runs from the lip / recess floor (−5.0) to the recess roof's start (+5.4);
  - the bolt slot runs −1.6..+2.75;
  - so the strips are 2.65 (top) and 3.4 (bottom) tall, and the plates bear at 1.53 and 1.65 mm from their roots.
  - Sensitivity rows put the bolt at Z_A − 0.3 (on the CAD slot floor) and at Z_A + 0.0.
- **Kt 2.5 at all four strip roots.**
  - Two are real sharp corners: the recess floor's edge (inside) and the lip's top (outside).
  - The other two are conservative: the 135° turn into the recess roof, and the flat outer face (Kt 1.0 there gives 7.89).
- **No friction and no preload credited** (DFM round 4 S2). The sustained rows also run with 80 N of preload, and the worse result is kept.
- **Plates are checked at 1.9 mm**, the BOM's 14 gauge. Metric 2.0 is in the sensitivity rows.

**Drop shear (B4).**
- The nut plate has nothing over it: no roof, and the stops only locate it in X. The bolt is 1.05 mm below the PETG slot's top.
- So the shear goes through the head plate's slot edge to its top back edge, which meets the 45° roof after 0.4 mm. All 31.8 N is taken on a 0.3 mm line along the plate's 20.6 mm.
- The nut plate is lifted with the bolt by at most 0.4 mm, to Z_A + 5.2, and stays between the stops.

**End stops and lip (B18, B19).**
- **Friction is a demand here, never a credit.**
  - Neither the PETG face's friction behind the plate nor the jack screw's share is credited.
  - Bearing is on 1.0 mm of the plate's thickness (the stop is 1.0 proud) × 10 mm; root bending at arm 0.5, Kt 2.5; shear 1.5 V/A. All are in-plane: the root is a vertical plane and the stress runs along the layers.
  - The rear stop's section is 1.5 × 10.9 (Z_A − 5.7..+5.2). Advisory rows count the merged lip under it (3.12) and the plate bearing on the stop's tip only (1.37 as built; 2.44 with `STOP_W` 2.0, 3.81 with 2.5).
- **The lip** carries only the plate's own weight in service.
  - The bolt rests on the PETG slot floor 0.2 mm above the plates' slot bottoms, so downward bolt loads go to the PETG. The proof hang row puts all 49 N on the lip anyway, as a bound.
  - Upward loads lift the plate off the lip.
  - The BUILD_GUIDE has the head turned and the nut held, so the nut's washer doesn't twist the plate. If the nut were turned instead, the lip rows give 6.7 oiled and 2.97 dry (advisory).

**Everything else** uses round 4's models unchanged: axle bolts, motor pocket, skin and nacelle, floor, inserts, the jack thread and the S1 snug.

## Allowables and sources

- **No measured data.** `library/materials.csv` has only its header row, and no job has a datasheet in `inputs/`. The skill's placeholders apply:
  - PETG 25 MPa in-plane, 12.5 MPa across the layers;
  - E 1.8 GPa, ν 0.35;
  - shear allowable 0.5 × normal.
  - **PASS is not possible; NEEDS_TEST is the best verdict.**
- **Direction.**
  - In-plane: bearing on layer faces and 45° flanks; the stops' and the lip's root bending and shear (vertical root planes).
  - Across the layers: the strips' σz, and their shear on the root plane.
- **Required SF:**
  - 3 for short-term static loads;
  - 4 for cyclic or sustained loads;
  - 1.5 on yield for steel (class 12.9: 1080 MPa; plates and washers: 200; N20 shaft: 350);
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
| 32 | B18 end stop root (1.5 x 10.9 at the wall face, plate at arm 0.5): bending (Kt 2.5, sharp corner on the loaded face), rear stop, friction drag min(R, mu (T + P)) = min(10.0, 0.2 x (43 + 89)) = 10.0 N, pretension 10 N sustained | XY | 3.06 | 25.0 | 8.17 | 4.0 | OK |
| 33 | B18 end stop root: shear, rear stop, friction drag min(R, mu (T + P)) = min(10.0, 0.2 x (43 + 89)) = 10.0 N, pretension 10 N sustained | XY shear | 0.92 | 12.5 | 13.62 | 4.0 | OK |
| 34 | B18 nut plate's end on its end stop: bearing (1.0 x 10), rear stop, friction drag min(R, mu (T + P)) = min(16.4, 0.2 x (70 + 89)) = 16.4 N, everyday reverse 16.4 N cyclic | XY | 1.64 | 25.0 | 15.27 | 4.0 | OK |
| 35 | B18 end stop root (1.5 x 10.9 at the wall face, plate at arm 0.5): bending (Kt 2.5, sharp corner on the loaded face), rear stop, friction drag min(R, mu (T + P)) = min(16.4, 0.2 x (70 + 89)) = 16.4 N, everyday reverse 16.4 N cyclic | XY | 5.01 | 25.0 | 4.99 | 4.0 | OK |
| 36 | B18 end stop root: shear, rear stop, friction drag min(R, mu (T + P)) = min(16.4, 0.2 x (70 + 89)) = 16.4 N, everyday reverse 16.4 N cyclic | XY shear | 1.50 | 12.5 | 8.32 | 4.0 | OK |
| 37 | B18 nut plate's end on its end stop: bearing (1.0 x 10), rear stop, friction drag min(R, mu (T + P)) = min(29.8, 0.2 x (127 + 89)) = 29.8 N, reverse stall 29.8 N | XY | 2.98 | 25.0 | 8.40 | 3.0 | OK |
| 38 | B18 end stop root (1.5 x 10.9 at the wall face, plate at arm 0.5): bending (Kt 2.5, sharp corner on the loaded face), rear stop, friction drag min(R, mu (T + P)) = min(29.8, 0.2 x (127 + 89)) = 29.8 N, reverse stall 29.8 N | XY | 9.11 | 25.0 | 2.75 | 3.0 | **FAIL** |
| 39 | B18 end stop root: shear, rear stop, friction drag min(R, mu (T + P)) = min(29.8, 0.2 x (127 + 89)) = 29.8 N, reverse stall 29.8 N | XY shear | 2.73 | 12.5 | 4.58 | 3.0 | OK |
| 40 | B18 nut plate's end on its end stop: bearing (1.0 x 10), front stop, tensioning (the jack slides the snug bolt forward; the washer drags the plate, mu P 17.8 N) | XY | 1.78 | 25.0 | 14.06 | 3.0 | OK |
| 41 | B18 end stop root (1.5 x 10.9 at the wall face, plate at arm 0.5): bending (Kt 2.5, sharp corner on the loaded face), front stop, tensioning (the jack slides the snug bolt forward; the washer drags the plate, mu P 17.8 N) | XY | 5.44 | 25.0 | 4.60 | 3.0 | OK |
| 42 | B18 end stop root: shear, front stop, tensioning (the jack slides the snug bolt forward; the washer drags the plate, mu P 17.8 N) | XY shear | 1.63 | 12.5 | 7.66 | 3.0 | OK |
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

Advisory (not in the verdict: peaks, bounds, sensitivities, proof loads, the fix, the S1 table, bought parts):

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
| B18 end stop root (1.5 x 10.9 at the wall face, plate at arm 0.5): bending (Kt 2.5, sharp corner on the loaded face), proof 44 N rearward pull (§8 test 1), rear stop, min(R, mu (T + P)) 44.1 N | XY | 13.50 | 25.0 | 1.85 | 1.0 | OK |
| B18 end stop root: shear, proof 44 N rearward pull (§8 test 1), rear stop, min(R, mu (T + P)) 44.1 N | XY shear | 4.05 | 12.5 | 3.09 | 1.0 | OK |
| proof 49 N hang: the nut plate's bottom edge on its lip (bound: all of it, 20.6 mm²) | XY | 2.38 | 25.0 | 10.50 | 1.0 | OK |
| proof 49 N hang: lip root bending (bound: all of it, Kt 2.5) | XY | 4.46 | 25.0 | 5.60 | 1.0 | OK |
| proof 49 N hang: the bolt on the PETG slot floor (Ø3 x 8) | XY | 2.04 | 25.0 | 12.23 | 1.0 | OK |
| proof 5 kg on the idler bolt: M3 class 12.9 at the outer face | steel σy 1080 | 624.50 | 1080.0 | 1.73 | 1.0 | OK |
| B18 nut plate's end on its end stop: bearing (1.0 x 10), if the plates are dry (mu 0.6): rear stop, reverse stall, min(R, mu (T + P)) 29.8 N | XY | 2.98 | 25.0 | 8.40 | 3.0 | OK |
| B18 end stop root (1.5 x 10.9 at the wall face, plate at arm 0.5): bending (Kt 2.5, sharp corner on the loaded face), if the plates are dry (mu 0.6): rear stop, reverse stall, min(R, mu (T + P)) 29.8 N | XY | 9.11 | 25.0 | 2.75 | 3.0 | no |
| B18 end stop root: shear, if the plates are dry (mu 0.6): rear stop, reverse stall, min(R, mu (T + P)) 29.8 N | XY shear | 2.73 | 12.5 | 4.58 | 3.0 | OK |
| end stop root bending with the plate bearing on the stop's outer edge only (arm 1.0), reverse stall 29.8 N (Kt 2.5) | XY | 18.21 | 25.0 | 1.37 | 3.0 | no |
| end stop root bending if the merged lip under it is counted (section 1.5 x 12.4), reverse stall (Kt 2.5) | XY | 8.00 | 25.0 | 3.12 | 3.0 | OK |
| B18 nut plate's end on its end stop: bearing (1.0 x 10), if the snug has crept away (P 0, prying T up to 127 N only): rear stop, reverse stall 25.4 N | XY | 2.54 | 25.0 | 9.85 | 3.0 | OK |
| B18 end stop root (1.5 x 10.9 at the wall face, plate at arm 0.5): bending (Kt 2.5, sharp corner on the loaded face), if the snug has crept away (P 0, prying T up to 127 N only): rear stop, reverse stall 25.4 N | XY | 7.76 | 25.0 | 3.22 | 3.0 | OK |
| B18 end stop root: shear, if the snug has crept away (P 0, prying T up to 127 N only): rear stop, reverse stall 25.4 N | XY shear | 2.33 | 12.5 | 5.37 | 3.0 | OK |
| assembly, if the nut is turned instead of the head (oiled, mu 0.2, P 89 N): plate corner on the lip (7.5 N on 2 x 1.0) | XY | 3.74 | 25.0 | 6.69 | 3.0 | OK |
| assembly, if the nut is turned instead of the head (oiled): lip root bending over 4 mm (Kt 2.5) | XY | 3.50 | 25.0 | 7.13 | 3.0 | OK |
| assembly, if the nut is turned instead of the head (dry, mu 0.6, P 67 N): plate corner on the lip (16.8 N on 2 x 1.0) | XY | 8.41 | 25.0 | 2.97 | 3.0 | no |
| assembly, if the nut is turned instead of the head (dry): lip root bending over 4 mm (Kt 2.5) | XY | 7.88 | 25.0 | 3.17 | 3.0 | OK |
| FIX STOP_W 2.0: end stop root bending (Kt 2.5), pretension 10 N sustained (10.0 N) | XY | 1.72 | 25.0 | 14.53 | 4.0 | OK |
| FIX STOP_W 2.0: end stop root bending (Kt 2.5), everyday reverse 16.4 N cyclic (16.4 N) | XY | 2.82 | 25.0 | 8.88 | 4.0 | OK |
| FIX STOP_W 2.0: end stop root bending (Kt 2.5), reverse stall 29.8 N (29.8 N) | XY | 5.12 | 25.0 | 4.88 | 3.0 | OK |
| FIX STOP_W 2.0: end stop root bending, the plate on the stop's outer edge only (arm 1.0), reverse stall | XY | 10.24 | 25.0 | 2.44 | 3.0 | no |
| FIX+ STOP_W 2.5 (more margin): end stop root bending, the plate on the stop's outer edge only (arm 1.0), reverse stall | XY | 6.56 | 25.0 | 3.81 | 3.0 | OK |
| FIX STOP_W 2.0: end stop root bending, proof 44 N pull | XY | 7.59 | 25.0 | 3.29 | 1.0 | OK |
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

- Lowest SF: **2.75** (required 3.0), at B18: the rear end stop's root, reverse stall.
- **Drop rows** meet their SF up to a **5.0 cm** drop, limited by B15's strip shear (3.01).
  - That is a thin margin: rigid roots give 2.74, and a 3× softer uncut band 2.67 (advisory, as in round 4).
  - The 5 mm stopping-distance convention isn't conservative (round 3), so §8 test 3 stays the evidence for the 5 cm rating.
  - The recess floor chamfer that round 4 offered (1 × 45°, plate edge filed to match) lifts that edge's row from 3.02 to 4.72. It doesn't help the shear row, so it isn't required.
- 1 of 70 verdict rows is below its required SF.

## Required change: widen the end stops

**`model.py`: `STOP_W` = 1.5 → 2.0.** Nothing else changes:
- `NUT_PLATE_X` stays (108, 129), so the plate's fit, position and play are the same;
- the lip lengthens with the stops (x 106.0–131.0).

| Row | As built (1.5) | With 2.0 | Required |
|---|---|---|---|
| Rear stop root bending, reverse stall 29.8 N | 2.75 | **4.88** | 3 |
| … everyday 16.4 N / sustained 10 N | 4.99 / 8.17 | 8.88 / 14.53 | 4 |
| … 44 N proof pull | 1.85 | 3.29 | 1 |
| … plate bearing on the stop's tip only (advisory) | 1.37 | 2.44 (3.81 with `STOP_W` 2.5) | 3 |

- **Fit.** The front stop ends at x 131.0, where the corner fillet's face is at |y| 37.66, so the stop (from |y| 37) still joins it. The rear stop ends at x 106.0 on the flat outer face, far from the road wheel at x 80. Both stay 1.0 proud, inside the links' |y| 43.
- **Plate ends.** Deburr them square to the face (BUILD_GUIDE §1 step 3 already says to deburr every edge), so the plate bears across the stop's face and not only on its tip. If more margin is wanted against an out-of-square end, use `STOP_W` 2.5 (tip-only 3.81).
- **Lowest SF with the change:** 3.01 (B15, the drop's strip shear).

## Spec §8 proof tests against the round-5 design

**What matches (the round-4 review's changes are in):**
- the checklist (plates on their seats between the stops);
- the heading "strength rounds 2–5";
- the PETG round each idler plate named in tests 1, 2 and 3;
- test 1's idler pull at the slot's front end. That is right for the pull: the head plate is worst there (proof 4.35; strip root 4.90).

**Predicted proof SFs (all ≥ 1.0):**
- test 2's 32.5 N reverse stall: 6.65 (strip root), 5.90 (head plate);
- test 1's 44 N pull: 4.35 (head plate), 4.90 (strip); the rear stop 1.85, or 3.29 with the fix;
- test 1's 49 N hang: 1.96 (strip shear and root, at mid-slot); lip 5.60; bolt on the slot floor 12.2.

**What doesn't match, and the exact changes:**
1. **The 5 kg hang should be at mid-slot, not at the front end.**
   - The vertical cases are worst with the bolt at mid-slot. There the Ø9 washers sit in the middle of the PETG strips' span; at the ends they sit near the uncut band.
   - So the 5 cm drop rows (B15) govern at x 120, and the hang's proof SF is 1.96 at mid-slot against 2.56 at the front end. At the front end the hang doesn't test the drop's weak spot.
   - Test 1: "Repeat on an idler bolt at the slot's front end, with the jack screw set. On the idler, also pull 4.5 kg (44 N) rearward along the track line for 1 min (idler `spec.md` §8 test 1)." → "Repeat on an idler bolt at mid-slot, with the jack screw set. Then turn the jack screw in until the bolt is at the slot's front end and, on the idler, also pull 4.5 kg (44 N) rearward along the track line for 1 min (idler `spec.md` §8 test 1)."
2. **Name the stops in the pass criteria.** They now carry the pull's friction drag.
   - Test 1's pass: "the PETG round each idler plate" → "the PETG round each idler plate (the recess edges inside the tub; the lip, both end stops and the wall face round the nut plate outside)".
   - Tests 2 and 3 can keep the short form.
3. **Take up the idler's bore clearance when measuring the disc.**
   - The idler's own 0.5 mm running clearance can move its disc 0.5 mm on the bolt, and its 1.94° cock up to 0.38 mm, with nothing damaged. Either exceeds the 0.3 mm limit.
   - Test 1: "Before and after, measure the idler disc's rear face against a fixed mark on the chassis." → "Before and after, measure the idler disc's rear face against a fixed mark on the chassis, with the idler pulled rearward by hand along the track line (about 0.5 kg on the strap) for both readings."
   - Test 2's "(measured as in test 1)" then follows.
4. **The idler spec's test 1 still says mid-slot.** The chassis test 1 points to it. Idler `spec.md` §8 test 1: "Fit the idler on its bolt at mid-slot in the chassis" → "Fit the idler on its bolt at the front end of the chassis slot". The idler report has the same change, and the same disc-measurement wording.

## Notes

- **If the fix is taken:**
  - spec §2 and §3 and the design brief describe the stops as `STOP_W` 1.5 (x 106.5–108, 129–130.5); with 2.0 they are x 106.0–108 and 129–131;
  - cad_checks' stop probes at x 106.4 (void) move to 105.9.
- **Spec §4 is still stale in two places** (round 4 note, unchanged):
  - "146 at the sketch's 80 % cap" (the cap is 6.0 V, at most 130 N·mm);
  - "pocket edges carry 1.87 R and 0.87 R" (2.05 R and 1.05 R horizontally, 1.67 R in the drop).
- **Snug and oil (S1)** are unchanged (B7t 3.15): the 0.04 N·m snug on oiled plates. Oil is required: dry gives 1.60. The stop rows use the same oiled µ.
- **Unchanged from round 4:**
  - the jack-screw thread (B7 4.82, B8 14.4) and the buttress lug (B9 12.7);
  - both axle bolts (B10 1.79, B11 2.66, A6 2.66);
  - the skin, nacelle and N20 shaft (C1 6.52, C2 3.55, C13 3.06 / 1.91);
  - the road-wheel, floor and lid rows.
  - The round-3 advisories still apply: fully threaded A2-70 bolts aren't enough (1.11), and the road-wheel bolts should be no more than snug.
- **Not checked here:** the sprocket's own rows (another reviewer). The idler part is in the idler job's report (NEEDS_TEST, lowest 4.19).

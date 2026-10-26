VERDICT: NEEDS_TEST

# Strength check: 20261026-rover-idler (round 5)

strength-analyst (independent) · 2026-10-26 · run from the project root with the CAD venv's interpreter: `/home/claude/.venv-cad/bin/python3 jobs/20261026-rover-idler/strength_calc.py` (a few seconds). The script builds the round-5 idler with build123d and takes the tooth section, the part's height and the bore from the solid.

**Result: NEEDS_TEST.** The allowables are placeholders, so PASS is not possible. The shorter part is sound.

- **Lowest SF: 4.19** (required 3), at I8: the bore's outer end edge with the idler cocked by the 3 N side drag, plus the radial peak, at a reverse stall. The 20 mm bore gave 4.63 for the same row.
- **Every one of the 16 verdict rows passes.** That includes the rows new in this round: the peak bearing on a rigid bore, the cocked bore's edges, the hub root (across the layers) and a tooth pushed sideways by a link.
- **Drop rows:** they hold up to a 10.3 cm drop, limited by the bore's peak bearing. Round 3's mean-bearing rows alone gave 19.9 cm; the peak rows are new in this round.
- **Spec §8 needs two changes and a label fix** (below): test 1 at the slot's front end, as in the chassis spec; and a light rearward pull while the disc is measured, so the bore's own clearance isn't read as movement.

## What round 5 changed, checked

| Item | Brief / spec | Checked |
|---|---|---|
| Part height | 14.8 (hub 7.8) | Solid: 14.80 tall, bore through (`geometry.json` 14.8; assembly_check `idler_bore_length_mm` 14.8) ✓ |
| Hub inner end | \|y\| 43.7 = nut plate 38–40 + Ø9 washer –40.8 + wall nut –43.2 + running washer –43.7 | `rover_frame.IDLER_HUB_Y0` 43.7; the sprocket model's `HUB_Z0_ROUND` −11.3 = 43.7 − 55 ✓ |
| Disc, teeth, track plane | unchanged | Same tooth section from the solid (Z 8.40 mm³); disc ±3.5 about \|y\| 55 ✓ |
| Bore | Ø3.5 printed (Ø3.7 CAD), 0.5 clearance on the Ø3 bolt | ✓ |
| Cock on the bolt | about 1.9° (1.4° before) | 0.5 / 14.8 = 33.8 mrad = **1.94°** (0.5 / 20 = 1.43°) ✓. Tooth tips (r 17.9) 0.60 mm sideways, against the link notch's 0.5 mm a side |
| Bearing length | the hub is still longer than the bearing spread, so I1–I4 shouldn't change | ✓: I1–I4 are unchanged. The 10.5 mm contact triangle (next section) also still fits in the 14.8 mm bore |

## Load cases

These come from the shared rover block; the chassis report has the full table.

| Load | Value | Note | Duration |
|---|---|---|---|
| Idler radial, reverse stall | **29.8 N** (both runs tight: 2 × (5 + 9.89)) | Spec §4. Proof stall 32.5 N. An ungated S-08 motor gives 34.2 N | short-term |
| Everyday | 16.4 N | | cyclic |
| Pretension | 10 N | an upper bound | sustained |
| 5 cm drop | 31.8 N, front corner | Mass 649 g (round-5 estimate 631 g), 5 mm stopping distance | short-term |
| Side drag | 3 N at the pitch circle (r 16.18) | Taken on one tooth, and as the couple that cocks the idler | cyclic |
| Proof | 44 N rearward (§8 test 1); 49 N hang (chassis §8 test 1) | | 1 min |

## Assumptions

- **Bore.**
  - The Ø3.7 CAD bore prints at about Ø3.5 and runs on the threads of the fully threaded M3, with 0.5 mm clearance.
  - Crest contact: half the projected area (round 3).
- **Mean bearing (I1–I4, unchanged).** The 7 mm disc plus a 45° spread into the Ø10 hub gives an effective 5.08 mm.
- **Peak bearing (I1p–I4p, new).** The idler is treated as a rigid bore on the bolt (round 3's rigid-pin model).
  - The radial load acts at the track plane, 3.5 mm from the bore's outer end.
  - The contact is therefore a triangle 10.5 mm long, with its peak at the outer end. Its length doesn't depend on the bore's length, as long as the bore is at least 10.5 mm long; it is 14.8.
- **Cock (I8, new).**
  - The 3 N side drag at the pitch circle is a 48.5 N·mm couple. It cocks the idler the full 1.94° until the bore's end edges touch the bolt on opposite sides.
  - Each edge then carries 48.5 / 14.8 = 3.28 N (2.43 N with the 20 mm bore), taken over 1 mm of bore at the thread factor.
  - At the outer edge this is added to the radial peak, although the two act at right angles to each other.
  - Closing the 0.3 mm end play would take more tilt than the bore allows, so the running washers don't share the couple.
- **Hub root (I10, new).**
  - The Ø10 hub meets the disc's inner face at a sharp corner (Kt 2.5). The hub's axis is the print Z, so its bending stress runs **across the layers**.
  - Its loads are:
    - the cock couple's inner edge force at the hub's free end (arm 7.8);
    - the part of the radial triangle that lies beyond the 7 mm disc.
- **Teeth.**
  - I6, unchanged: a free idler's teeth carry only the bearing drag (0.83 N).
  - I9, new: a link pushes one tooth tip sideways with the whole 3 N side drag. The tooth bends about its 2.7 × 7 root (in-plane, Kt 1.8). The cock's 0.1 mm of excess against the notch is free play, so it adds no force of its own.
- **Hub end face (I7).**
  - The inner running washer (ISO 7089, Ø7) now sits on the wall nut.
  - The hub bears on it over r 1.85–3.5, 27.7 mm². Round 3 took the whole hub annulus.
- **The chassis clamp's yaw** at the reverse stall is at most 2.43 mrad (chassis round 5). The idler's own free cock is 33.8 mrad, so the hub face never becomes the backstop that round 3 checked; that advisory row is retired.

## Allowables and sources

- **No measured data.** `library/materials.csv` has only its header row, so the skill's placeholders apply:
  - PETG 25 MPa in-plane, 12.5 MPa across the layers;
  - shear allowable 0.5 × normal.
- **NEEDS_TEST is the best verdict possible.**
- **Required SF:**
  - 3 for short-term loads;
  - 4 for cyclic or sustained loads;
  - 1.5 on yield for steel;
  - 1.0 for proof loads.
- **Temperature:** 40 °C service against a softening point of about 70 °C, so it doesn't limit the part.

## Results (`strength_calc.py` output)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | I1 bore bearing on the M3 threads (mean, effective 5.08 mm), reverse stall 29.8 N | XY | 1.96 | 25.0 | 12.78 | 3.0 | OK |
| 2 | I2 bore bearing (mean), cyclic 16.4 N | XY | 1.07 | 25.0 | 23.26 | 4.0 | OK |
| 3 | I3 bore bearing (mean), pretension 10 N sustained (creep) | XY | 0.66 | 25.0 | 38.06 | 4.0 | OK |
| 4 | I4 bore bearing (mean), 5 cm front corner 31.8 N | XY | 2.09 | 25.0 | 11.96 | 3.0 | OK |
| 5 | I1p bore bearing PEAK at the outer end (rigid bore, triangular over 10.5 of the 14.8 mm bore), reverse stall | XY | 3.78 | 25.0 | 6.61 | 3.0 | OK |
| 6 | I3p bore bearing PEAK, pretension 10 N sustained (creep) | XY | 1.27 | 25.0 | 19.69 | 4.0 | OK |
| 7 | I4p bore bearing PEAK, 5 cm front corner | XY | 4.04 | 25.0 | 6.18 | 3.0 | OK |
| 8 | I8 bore's outer end edge, idler cocked 1.94° by the side drag 3 N at r 16.18 (edge force 3.28 N on 1 mm) + the radial PEAK, everyday 16.4 N cyclic | XY | 4.26 | 25.0 | 5.86 | 4.0 | OK |
| 9 | I8 the same, reverse stall 29.8 N | XY | 5.97 | 25.0 | **4.19** | 3.0 | OK |
| 10 | I5 disc rim bearing under a link, 5 cm front corner | XY | 1.26 | 25.0 | 19.79 | 3.0 | OK |
| 11 | I6 tooth root (chamfer top), bearing drag 0.83 N (Kt 1.8) | XY | 0.67 | 25.0 | 37.15 | 4.0 | OK |
| 12 | I9 tooth pushed sideways by a link at its tip (side drag 3 N on one tooth): root bending, Kt 1.8 | XY | 1.35 | 25.0 | 18.56 | 4.0 | OK |
| 13 | I7 hub end face on its running washer (Ø7 on the wall nut: r 1.85–3.5, 27.7 mm²), side 3 N | XY | 0.11 | 25.0 | 231.10 | 4.0 | OK |
| 14 | I10 hub root (Ø10 / Ø3.7, 7.8 long) bending across layers, sharp corner (Kt 2.5), everyday 16.4 N + side 3 N cyclic | Z | 0.72 | 12.5 | 17.39 | 4.0 | OK |
| 15 | I10 the same, reverse stall 29.8 N + side 3 N | Z | 0.76 | 12.5 | 16.36 | 3.0 | OK |
| 16 | I10 the same, 5 cm front corner 31.8 N + side 3 N | Z | 0.77 | 12.5 | 16.21 | 3.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, proof loads, bought parts):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| proof (§8 test 1): 4.5 kg (44 N) rearward, bore bearing (mean) | XY | 2.90 | 25.0 | 8.62 | 1.0 | OK |
| proof (§8 test 1): 4.5 kg rearward, bore bearing PEAK | XY | 5.61 | 25.0 | 4.46 | 1.0 | OK |
| proof: reverse stall at 100 % PWM on a fresh pack 32.5 N, bore bearing (mean) | XY | 2.13 | 25.0 | 11.71 | 1.0 | OK |
| proof: 5 kg (49 N) hung from the idler (chassis §8 test 1), bore bearing PEAK | XY | 6.23 | 25.0 | 4.01 | 1.0 | OK |
| jam: stall pull 9.89 N on one idler tooth (Kt 1.8) | XY | 8.03 | 25.0 | 3.11 | 3.0 | OK |
| bore bearing (mean), 5 cm corner, stiff landing (64 N) | XY | 4.18 | 25.0 | 5.98 | 3.0 | OK |
| bore bearing PEAK, 5 cm corner, stiff landing (64 N) | XY | 8.08 | 25.0 | 3.09 | 3.0 | OK |
| S-08 ungated 196 N*mm motor at the 6.0 V cap: reverse stall 34.2 N, bore bearing (mean) | XY | 2.25 | 25.0 | 11.12 | 3.0 | OK |
| round 4's 20 mm bore for comparison: I8 at the reverse stall (edge force 2.43 N) | XY | 5.40 | 25.0 | 4.63 | 3.0 | OK |
| chassis clamp yaw at the reverse stall (2.43 mrad) against the idler's free cock (33.8 mrad): the hub face doesn't become a backstop | mrad | 2.43 | 33.8 | 13.90 | 3.0 | OK |
| M3 x 40 class 12.9 bending at the wall face (chassis-owned): reverse stall 29.8 N x 17 | steel σy 1080 | 379.12 | 1080.0 | 2.85 | 1.5 | OK |
| M3 x 40 class 12.9 bending at the wall face (chassis-owned): 5 cm corner 31.8 N x 17 | steel σy 1080 | 405.30 | 1080.0 | 2.66 | 1.5 | OK |

- **Lowest SF:** 4.19 (required 3.0), at I8.
- **Drop rows:** they meet their SF up to 10.3 cm (I4p).
- **Verdict rows:** 0 of 16 are below their required SF.

## The shorter bore: what it changes

- **Bearing.** Nothing changes. The rigid bore's contact needs 10.5 mm, from the outer end inward, and the bore is 14.8 mm long. The mean rows I1–I4 are unchanged.
- **Cock: 1.94° instead of 1.43°.**
  - **Edge loads.** The side couple puts 35 % more force on the bore's end edges: I8 drops from 4.63 to 4.19.
  - **Teeth.** The tooth tips can stand 0.60 mm off the track plane against the notch's 0.5. The links take that out as the teeth enter, as before (0.45 mm with the 20 mm bore). This is free play, so the teeth see only the side drag (I9, 18.6).
  - **Measurement.** The bore's clearance also moves the disc when nothing is broken. The disc can shift 0.5 mm rearward on the bolt, and the cock can move the disc centre up to 0.38 mm in X (0.0338 × 11.3 mm). Both exceed §8's 0.3 mm limit, so the measurement must take the clearance up the same way both times (change 2 below).
- **Hub.** Shortening it lowers its root moment, and the root stays far from limiting (I10, 16 or more across the layers).

## Spec §8 against the round-5 design

**Matches:**
- Test 1's load (4.5 kg rearward for 1 min) and its criteria (spins freely, axial play, ovalisation, pen mark, disc ≤ 0.3 mm, runout) suit the round-5 part.
- "Run this test on the round 5 clamp" is right.
- Test 2 (the chassis stall run in reverse, and the drop) matches.

**Doesn't match, and the exact changes:**
1. **Test position.**
   - The chassis spec now runs the idler pull with the bolt **at the slot's front end**, where the head plate is worst (chassis proof row 4.35), but this spec still says mid-slot.
   - Test 1: "Fit the idler on its bolt at mid-slot in the chassis, the jack screw set against the bolt head" → "Fit the idler on its bolt at the front end of the chassis slot, held there by the jack screw".
2. **Take up the bore's clearance when measuring the disc.**
   - The 0.5 mm running clearance alone can move the disc 0.5 mm, and the 1.94° cock up to 0.38 mm, with nothing damaged. The ≤ 0.3 mm criterion could then fail a good part, or hide a real movement.
   - Test 1, after "measured against a fixed mark on the chassis": add ", with the idler pulled rearward by hand along the track line (about 0.5 kg on the strap) for both readings, so the bore's clearance is taken up the same way each time".
   - Make the same change wherever the chassis spec says "measure the idler disc's rear face against a fixed mark on the chassis" (chassis §8 tests 1 and 2).
3. **Heading.** "**Proof tests** (strength round 3)" → "(strength rounds 3–5)". This is a label only.

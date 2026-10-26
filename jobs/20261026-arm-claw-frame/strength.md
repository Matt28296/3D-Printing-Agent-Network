VERDICT: FAIL

# Strength check (round 6, independent review): 20261026-arm-claw-frame

strength-analyst (independent; did not design the part) · 2026-10-26 · round 6, merged at 105aafe ·
`python3 jobs/20261026-arm-claw-frame/strength_calc.py` (plain python3, from the project root). The CAD engineer's
round-6 self-check of this file is replaced; every number below is recomputed. The cover's forces come from the cover's
reviewed strength_calc.py.

## Verdict

**FAIL, on one row: the top M3 × 10's pull-out at its snug preload. The fix is hardware only (no geometry change).**

- **Lowest SF 2.73 (row 42, FAIL, sustained, req 4).** The cover's two top M3 × 10 (no camera) driven snug.
  - 150 N preload, the anchor's own figure, on the 6.95 engaged in CAD (7.00 as printed with the wall pulled down).
  - This frame already holds the anchor's M3 × 45 to exactly this rule: row 46, pull-out on the same preload, req 4,
    4.15.
  - **Fix:** M3 × 14 pan head + Ø7 × 0.5 washer (the cover's review): 10.50 engaged, **SF 4.12** (4.02 with the worst
    standing left at the screw). The tip ends at z 38.0, 3.55 above the pilot's floor. **No change to this part.**
  - The camera option (M3 × 18 through the pad) passes: 4.41 (row 43).
- **Every other verdict row passes.**
  - Lowest: **3.17** (row 54), the V-groove's flank bearing under the opening stall (band 0.446 × 7.3, after the
    anchor's least crush). Then 3.36 (row 47, the anchor under the stall with its preload).
  - The frame's own load cases: lowest 3.53 (row 4, floor punching under the Ø8 washer when the camera hits the desk),
    unchanged.
  - Sustained rows: the anchor pull-out on its preload 4.15 (row 46); the front M2.5 pull-out on its 100 N preload 5.40
    (row 45, new); the anchor preload hoop 23.6 (row 53). The clamp rows are ≥ 8.8.
  - Proof rows: lowest 2.50 (row 56, the groove's bearing).
- **Placeholder PETG allowables.** NEEDS_TEST at best once fixed.

## The rows the brief asked about

### The 3.004 bound row and the 2.94 info row (item 2)

**Ruling: the bound is too conservative. It is information, not a verdict row.** The same holds for 2.94.
- The bound puts all 886 N·mm of the opening stall on the top screws, as if the post held nothing: 136 N each. That is
  the load path of a cover with **no anchor**. The cover's frame model (round 3, unanchored) gives 284 N on one screw.
- As built, the ridge in the groove takes the push. The cover's frame model now returns its support reactions. Worst of
  64 variants and both play modes, the real top-screw tension is **23.0 N** at the opening stall and **24.5 N** at the
  proof push (the +y screw).
- Pull-out on the worst engaged length (6.74, the worst standing left at the screw) is **SF 17.3 / 16.2** (rows 39–41).
- The old rows are kept as information: rows 67–69, at 3.00 / 4.95 / 2.91. Row 69 is the 2.94 row recomputed at the
  worst standing after seating (0.259, not 0.19).
- What governs the top screws is their own **preload** (row 42), not the joint's service load.

### The top wall's standing (item 3), on this part

- **M3 engagement.** The bulkhead prints at 48.4 (G-code). An M3 × 10 under the 3 mm top wall has 7.00 below it with
  the wall pulled down, and 6.74 if the worst standing (0.259) is left at the screw. An M3 × 18 through the camera pad
  has 11.50 / 11.24. The pilots are 14.0 deep as printed (the last pilot layer is ;Z:34.6; ;Z:34.4 is solid).
- **Rack A's guide** is the cover's, not this part's. The cover's review has the backlash table: 0.33–0.40 nominal, no
  binding.
- **Camera mount:** the M3 × 18 rows above. The USB-tug row 38 is 10.16.

### Printability on this part (item 4)

**The 0.95 mm ligament between the V-groove and the anchor pilot (row 70, info, 2.54).**
- **What is printed.** My G-code at y 28 shows the top layer as the groove's external perimeter (w 0.52, edge 15.99)
  next to the pilot's (w 0.48, edge 17.03): two bonded beads, 1.04 mm of material. CAD has 0.95 at the block top; with
  the hole printing at Ø2.5 it is 1.10. It widens 1 mm per mm downward (1.5 at 17.4).
- **Ruling: it stays information, not a verdict row.**
  - It is loaded only while the M3 × 45 forms its thread, once.
  - Lame on the thinnest ring is a lower bound: the top 0.8 mm of a 10.6 mm engagement, on the groove side's quarter of
    the circumference.
  - A split there does not open any load path. The flank push crosses it in compression, backed by the screw's shank.
  - Losing that thread costs ~0.2 mm-equivalent: pull-out on the preload 4.15 → 4.07 (row 71, still ≥ 4).
- **Make it checkable.** The cover hides it once fitted. Add "before fitting the cover, drive the M3 × 45 into the
  rail-block pilot once and back it out (it forms the thread); look at the groove beside the pilot: no split or bulge"
  to BUILD_GUIDE §4 step 9 and to spec §8 (design_review.md has the text).

**The groove's first layer.** The 17.0–17.2 layer is an open 0.3 slot (not closed), floor 17.0. The cover's tip faces
that layer's top (17.2), 0.206 above it nominal and +0.093 at RSS. In the worst stack the tip bottoms, with play
0.029: the anchor rows 50–51 take it (10.32 / 8.93).

### Everything else (item 6)

All verdict rows ≥ 3 (≥ 2 for proof) except row 42. The sustained screw rows:

| Row | What | SF | Note |
|---|---|---|---|
| 46 | anchor pull-out | 4.15 | |
| 42 | top M3 × 10 | **2.73** | |
| 43 | M3 × 18 | 4.41 | |
| 45 | M2.5 pull-out | 5.40 | |
| 53 | anchor hoop | 23.62 | |
| 9–10 | wrist clamp | 11.1 / 9.9 | |

The MG90S tab-pilot strips (rows 72–79) are the user-accepted deviation (26 Oct 2026), with the screw-strip check in
spec §8. Unchanged.

## Slice facts (my scratch slice of this job's committed part.stl, arm's command, G-code read back)

| Feature | CAD | Printed |
|---|---|---|
| Bulkhead top and both ribs | 48.45 | **48.4**; last layer `;Z:48.4`, 0.05 from the slice planes 48.3 / 48.5 |
| Rail block top | 17.75 | **17.8** (both sides of the groove, and at −y) |
| Groove walls (layers ending 17.2 / 17.4 / 17.6 / 17.8) | 45° | half-widths 0.15 / 0.35 / 0.55 / 0.75, centred on x 15.25 |
| Groove's 17.0–17.2 layer | — | open 0.3 slot; 17.0 solid |
| Anchor pilot, top M3 pilots | Ø2.7 | external perimeter at r 1.57 (Ø2.69 to the bead edge; Ø2.5 assumed with the default hole compensation) |
| Top pilot floor | 34.45 | 34.4 (the pilot layers end at ;Z:34.6) |

## Method, sections and allowables

As round 4: placeholder PETG (no library row), stresses mapped to the layers.
- **The frame prints back face down.**
  - Wrist-plate bending runs along the layers: 25 MPa.
  - Bulkhead, rib and rail-block root bending runs across them: 12.5 MPa.
  - Pull-out and punching are interlayer shear: 6.25 MPa.
  - Hoop round a vertical pilot runs along the layers: 25 MPa.
- **Kt:** 2.5 sharp, 2 at holes, 1.5 / 1.7 at fillets.
- **Required SF:** 3 short-term, 4 sustained or cyclic, 2 at the proof load.
- **Snug preloads** (the project's rule): M3 150 N (≤ 0.09 N·m, the anchor), M2 / M2.5 100 N (the tab screws).
- **The cover's forces** come from its reviewed script:
  - 'locked': Fx 25.7 / 16.4 / 32.6 N, lift 10.0 / 6.4 / 12.7 N;
  - the worst build step 9 accepts (play 0.029, preload gone): wedge + lift 60.3 / 69.7 N;
  - the top joint's tension: 23.0 / 24.5 N.
- **The anchor's engagement** is measured from the printed block top with the worst standing after seating: 10.56. The
  self-check had 10.49.
- **Temperature:** 40 °C against PETG at ~70 °C, OK.

## Proof test (spec §8)

With the fix, the frame's proof rows pass: V-groove 2.50 / 5.15, anchor pull-out 3.20 (preload + wedge + lift), 8.93
at the worst accepted play.

## Results (from `strength_calc.py`, verbatim)

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | USB tug 10 N at the plug (z 91.6), across the shaft: washer bearing (M_t 896 N.mm -> screw 249 N) | Ø8 x 0.8 washer on the pad, 44.5 mm2 (its Ø2.7 bore) | Z comp | 5.59 | 25.00 | 4.47 | 3 | OK |
| 2 | USB tug 10 N at the plug (z 91.6), across the shaft: floor punching under the washer | Ø8 x 6.3 floor | Z shear | 1.57 | 6.25 | 3.98 | 3 | OK |
| 3 | added: camera hits the desk, 13 N at its end (z 79.6): washer bearing (M_t 1009 N.mm -> screw 280 N) | Ø8 x 0.8 washer on the pad, 44.5 mm2 (its Ø2.7 bore) | Z comp | 6.29 | 25.00 | 3.97 | 3 | OK |
| 4 | added: camera hits the desk, 13 N at its end (z 79.6): floor punching under the washer | Ø8 x 6.3 floor | Z shear | 1.77 | 6.25 | 3.53 | 3 | OK |
| 5 | crash: 13 N in the arm plane at the fingertip (z <= 33.2): washer bearing (M_t 406 N.mm -> screw 113 N) | Ø8 x 0.8 washer on the pad, 44.5 mm2 (its Ø2.7 bore) | Z comp | 2.53 | 25.00 | 9.87 | 3 | OK |
| 6 | crash: 13 N in the arm plane at the fingertip (z <= 33.2): floor punching under the washer | Ø8 x 6.3 floor | Z shear | 0.71 | 6.25 | 8.77 | 3 | OK |
| 7 | weight x3 incl. the 250 deg/s2 ramp (cyclic): 3 x the 50 g overhung moment (134 N.mm, torque_budget round 3): washer bearing (M_t 401 N.mm -> screw 111 N) | Ø8 x 0.8 washer on the pad, 44.5 mm2 (its Ø2.7 bore) | Z comp | 2.50 | 25.00 | 10.00 | 4 | OK |
| 8 | weight x3 incl. the 250 deg/s2 ramp (cyclic): 3 x the 50 g overhung moment (134 N.mm, torque_budget round 3): floor punching under the washer | Ø8 x 6.3 floor | Z shear | 0.70 | 6.25 | 8.88 | 4 | OK |
| 9 | SYS-04 overhung moment, 50 g, x1.3 moving (sustained): washer bearing (M_t 174 N.mm -> screw 100 N) | Ø8 x 0.8 washer on the pad, 44.5 mm2 (its Ø2.7 bore) | Z comp | 2.25 | 25.00 | 11.13 | 4 | OK |
| 10 | SYS-04 overhung moment, 50 g, x1.3 moving (sustained): floor punching under the washer | Ø8 x 6.3 floor | Z shear | 0.63 | 6.25 | 9.90 | 4 | OK |
| 11 | added: yaw stall 7.1 N along the wrist axis at the fingertip (x 83.3), pulling the claw off the horn: washer bearing (M_t 592 N.mm -> screw 171 N) | Ø8 x 0.8 washer on the pad, 44.5 mm2 (its Ø2.7 bore) | Z comp | 3.85 | 25.00 | 6.49 | 3 | OK |
| 12 | added: yaw stall 7.1 N along the wrist axis at the fingertip (x 83.3), pulling the claw off the horn: floor punching under the washer | Ø8 x 6.3 floor | Z shear | 1.08 | 6.25 | 5.77 | 3 | OK |
| 13 | wrist stall 216 N.mm (cyclic): horn arm on the pocket wall | arm flank r 3.6..16.1 x 1.6 (mean, resultant at r 11.9) | XY | 0.91 | 25.00 | 27.62 | 4 | OK |
| 14 | crash: 13 N at the fingertip x 83.3 back-drives the wrist (1084 N.mm, 5 x stall: the top of SYS-11's 3-5 x): horn arm on the pocket wall | arm flank r 3.6..16.1 x 1.6 (mean, resultant at r 11.9) | XY | 4.54 | 25.00 | 5.51 | 3 | OK |
| 15 | stall, one jaw blocked, jaws 44 open: rack B's +y end at the block's end, R 27.0 N | rail block root, rack side with the anchor's Ø2.7 pilot in it (round 4): b_eff 7.9, depth 12.35, lever 5.9; I 1194; face Kt 2.5 2.11 / pilot edge Kt 2 0.98 MPa | Z | 2.11 | 12.50 | 5.93 | 3 | OK |
| 16 | stall, one jaw blocked, jaws closed: rack B's +y end at y 25.1, R 19.8 N | rail block root, rack side with the anchor's Ø2.7 pilot in it (round 4): b_eff 13.8, depth 12.35, lever 5.9; I 2118; face Kt 2.5 0.86 / pilot edge Kt 2 0.40 MPa | Z | 0.86 | 12.50 | 14.54 | 3 | OK |
| 17 | stall, both jaws (cyclic), jaws 44 open: R 13.5 N at the block's end | rail block root, rack side with the anchor's Ø2.7 pilot in it (round 4): b_eff 7.9, depth 12.35, lever 5.9; I 1194; face Kt 2.5 1.05 / pilot edge Kt 2 0.49 MPa | Z | 1.05 | 12.50 | 11.86 | 4 | OK |
| 18 | crash 13 N pushes jaw B shut: rack B's -y end on the block at y -31.4, R 12.6 N | rail block root, rack side (sharp, Kt 2.5): b_eff 8.5, depth 12.35, lever 5.9 | Z | 0.86 | 12.50 | 14.54 | 3 | OK |
| 19 | added: opening against an obstacle, jaw B: rack B's -y end at y -31.4, R 19.8 N | rail block root, rack side (sharp, Kt 2.5): b_eff 8.5, depth 12.35, lever 5.9 | Z | 1.35 | 12.50 | 9.26 | 3 | OK |
| 20 | added: opening against an obstacle, jaw B, jaws 44 open: rack B's -y end at y -9.4, R 27.0 N | rail block root, rack side (sharp, Kt 2.5): b_eff 13.8, depth 12.35, lever 5.9 | Z | 1.13 | 12.50 | 11.02 | 3 | OK |
| 21 | new path: the same (jaws 44 open, R 27.0 N) where the 14 mm front pilot passes 1.9 under the root (x 20.85..22.35, y 24) | rail block root less the pilot's 1.0 mm overlap with the anchor's Ø2.7 pilot in it (round 4): b_eff 6.9, depth 12.35, lever 5.9; I 1041; face Kt 2.5 2.43 / pilot edge Kt 2 1.14 MPa | Z | 2.43 | 12.50 | 5.15 | 3 | OK |
| 22 | new path: rack B pressed down on the plate over a front pilot (separating 7.9 N + pitch 8.5 N, all on the skin) | skin 1.9 over Ø2.2, b 12 (rack face), simply supported | XY | 1.24 | 25.00 | 20.09 | 3 | OK |
| 23 | USB tug 10 N along x at the plug (+x): rib roots on the pad (z 8.3), rail block ignored | bulkhead + 2 ribs 6 x 10: A 532, I 8804, centroid x 4.90; rib back x -6.5, sharp Kt 2.5 | Z | 2.70 | 12.50 | 4.63 | 3 | OK |
| 24 | USB tug 10 N along x at the plug (+x): rib roots on the pad (z 8.3), as built (the rail block is in the section) | + block 64 x 12.35: A 1326 (probed 1373), I 59432, centroid x 11.62; Kt 2.5 | Z | 0.64 | 12.50 | 19.68 | 3 | OK |
| 25 | USB tug 10 N along x at the plug (+x): pad / bulkhead r 1.5 fillet (z 8.3, x 3.5), rail block ignored | bulkhead + ribs, Kt 1.7 (r/h 0.23) | Z | 0.23 | 12.50 | 55.38 | 3 | OK |
| 26 | USB tug 10 N along x at the plug (+x): washer relief's foot (z 8.3, x 4.5), sharp, rail block ignored | bulkhead + ribs, Kt 2.5 | Z | 0.10 | 12.50 | 131.11 | 3 | OK |
| 27 | USB tug 10 N along x at the plug (-x): rail block's top meets the bulkhead's front face (z 17.75, sharp) | bulkhead + ribs above the block, front face x 10.0, Kt 2.5 | Z | 1.07 | 12.50 | 11.69 | 3 | OK |
| 28 | USB tug 10 N along x at the plug (+x), port at y +-45: rib back above the block (z 17.75), bending + the twist's warping | global 739 N.mm on bulkhead + ribs, + rib flange 184 N.mm (L_c 32), Kt 1 (smooth) | Z | 1.63 | 12.50 | 7.66 | 3 | OK |
| 29 | camera package 86 g x3 along x (cyclic): rib roots, rail block ignored | as above | Z | 0.59 | 12.50 | 21.32 | 4 | OK |
| 30 | new path: USB tug 10 N along x at the plug: the ribs' moment carried to the horn as torsion of plate + bulkhead + block (half each side) | J 9585 mm4, plate 6 thick | Z shear | 0.26 | 6.25 | 23.97 | 3 | OK |
| 31 | USB tug 10 N along x, port at y -45 (twist 450 N.mm): -y strip + its rib | 13.3 x 6.5 + rib 6 x 10 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +15.9 N | Z | 2.73 | 12.50 | 4.58 | 3 | OK |
| 32 | USB tug 10 N along x, port at y -45 (twist 450 N.mm): +y strip + its rib | 24.3 x 6.5 + rib 6 x 10 at the window's lower corner (Ø3 relief, Kt 1.5), screw force -5.9 N | Z | 1.82 | 12.50 | 6.88 | 3 | OK |
| 33 | USB tug 10 N along x, port at y +45 (twist 450 N.mm): -y strip + its rib | 13.3 x 6.5 + rib 6 x 10 at the window's lower corner (Ø3 relief, Kt 1.5), screw force -8.4 N | Z | 1.77 | 12.50 | 7.07 | 3 | OK |
| 34 | USB tug 10 N along x, port at y +45 (twist 450 N.mm): +y strip + its rib | 24.3 x 6.5 + rib 6 x 10 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +18.4 N | Z | 3.22 | 12.50 | 3.88 | 3 | OK |
| 35 | camera x3 along x (cyclic): -y strip + its rib | 13.3 x 6.5 + rib 6 x 10 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +1.0 N | Z | 0.25 | 12.50 | 49.81 | 4 | OK |
| 36 | camera x3 along x (cyclic): +y strip + its rib | 24.3 x 6.5 + rib 6 x 10 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +1.6 N | Z | 0.39 | 12.50 | 32.19 | 4 | OK |
| 37 | one jaw blocked: tab screw pull-out 14 N (M2, 5.5 engaged) | thread shear cylinder | Z shear | 0.40 | 6.25 | 15.64 | 3 | OK |
| 38 | USB tug 10 N along x at the plug: M3 x 18 pull-out from the bulkhead top, 66 N per screw | M3, 11.5 engaged | Z shear | 0.62 | 6.25 | 10.16 | 3 | OK |
| 39 | opening stall on jaw B, jaws open (27.0 N on the cover's upper piece): the top joint's tension 23.0 N on the +y top screw (cover frame model, anchored; M3 x 10, no camera) | M3, 6.74 engaged (the worst standing at the screw) | Z shear | 0.36 | 6.25 | 17.26 | 3 | OK |
| 40 | opening stall on jaw B, jaws open (27.0 N on the cover's upper piece): the top joint's tension 23.0 N on the +y top screw (cover frame model, anchored; M3 x 18 with the camera mount) | M3, 11.24 engaged (the worst standing at the screw) | Z shear | 0.22 | 6.25 | 28.79 | 3 | OK |
| 41 | spec §8 proof push: the top joint's tension 24.5 N on the +y top screw (M3 x 10) | M3, 6.74 engaged | Z shear | 0.39 | 6.25 | 16.21 | 2 | OK |
| 42 | top M3 x 10 (no camera) driven snug, 150 N preload (sustained): pull-out from the bulkhead top | thread cylinder Ø3 x 6.95 | Z shear | 2.29 | 6.25 | 2.73 | 4 | **FAIL** |
| 43 | top M3 x 18 through the camera mount driven snug, 150 N preload (sustained): pull-out | thread cylinder Ø3 x 11.24 | Z shear | 1.42 | 6.25 | 4.41 | 4 | OK |
| 44 | stall, one jaw blocked: rack B pushes the cover's lower piece forward (27.0 N at z 12.1): M2.5 pull-out 108 N (one screw) | M2.5 x 16, 11 engaged (14 mm pilot), 1.9 mm skins | Z shear | 1.25 | 6.25 | 4.98 | 3 | OK |
| 45 | front M2.5 x 16 driven snug, 100 N preload (sustained): pull-out from the wrist plate's front edge | thread cylinder Ø2.5 x 11 | Z shear | 1.16 | 6.25 | 5.40 | 4 | OK |
| 46 | cover anchor M3 x 45 driven snug, 150 N preload (sustained): pull-out from the block | thread cylinder Ø3 x 10.56 (from the printed block top, the cover 0.339 proud of the printed bulkhead; 10.75 in CAD) | Z shear | 1.51 | 6.25 | 4.15 | 4 | OK |
| 47 | cover anchor under the opening stall: preload + the wedge's lift + the cover's lift (35.2 N; foot held by the ridge) | thread cylinder Ø3 x 10.56 | Z shear | 1.86 | 6.25 | 3.36 | 3 | OK |
| 48 | cover anchor, preload crept away: the wedge's lift + the cover's lift 35.2 N under the opening stall | thread cylinder Ø3 x 10.56 | Z shear | 0.35 | 6.25 | 17.67 | 3 | OK |
| 49 | cover anchor, spec §8 proof push 34.2 N: preload + wedge + lift 44.6 N | thread cylinder Ø3 x 10.56 | Z shear | 1.96 | 6.25 | 3.20 | 2 | OK |
| 50 | cover anchor, the worst accepted ridge play 0.029 mm (preload gone): wedge + lift 60.3 N under the opening stall | thread cylinder Ø3 x 10.56 | Z shear | 0.61 | 6.25 | 10.32 | 3 | OK |
| 51 | cover anchor, the worst accepted ridge play 0.029 mm (preload gone): wedge + lift 69.7 N under the spec §8 proof push 34.2 N | thread cylinder Ø3 x 10.56 | Z shear | 0.70 | 6.25 | 8.93 | 2 | OK |
| 52 | cover anchor driven: thread forming (4.6 MPa, as the M2 rows) + preload (0.87 MPa), short-term | 2.65 CAD / 2.75 printed walls to the front face and the +y end; Lame peak x1.22, along the layers | XY | 6.69 | 25.00 | 3.74 | 3 | OK |
| 53 | cover anchor: preload alone (sustained; the forming pressure relaxes) | as above | XY | 1.06 | 25.00 | 23.62 | 4 | OK |
| 54 | V-groove (opening stall, Fx 25.7 N): the cover's ridge on the groove's +x flank (frictionless, all on one flank) | normal 36.3 N on 0.63 x 7.3 (the frame's layer edges) | bearing | 7.89 | 25.00 | 3.17 | 3 | OK |
| 55 | V-groove (opening stall, Fx 25.7 N): the block in front of the groove sheared off along the groove's bottom (z 16.95) | 40 mm2 ((22.35 - 16.05) x 7.3 less the pilot), interlayer | Z shear | 0.96 | 6.25 | 6.53 | 3 | OK |
| 56 | V-groove (spec §8 proof push, Fx 32.6 N): the cover's ridge on the groove's +x flank (frictionless, all on one flank) | normal 46.1 N on 0.63 x 7.3 (the frame's layer edges) | bearing | 10.01 | 25.00 | 2.50 | 2 | OK |
| 57 | V-groove (spec §8 proof push, Fx 32.6 N): the block in front of the groove sheared off along the groove's bottom (z 16.95) | 40 mm2 ((22.35 - 16.05) x 7.3 less the pilot), interlayer | Z shear | 1.21 | 6.25 | 5.15 | 2 | OK |
| 58 | cover push into the block, bound: all of it on the screw (opening stall, whole push 27.0 N): shank bearing in the pilot | Ø3 x 6 | bearing | 1.50 | 25.00 | 16.67 | 3 | OK |
| 59 | cover push into the block, bound: all of it on the screw (opening stall, whole push 27.0 N): tear-out of the 2.65 wall to the block's front face | 2 x 2.65 x 6, vertical planes (along the layers) | XY shear | 0.85 | 12.50 | 14.73 | 3 | OK |
| 60 | cover push into the block (opening stall, whole push 27.0 N): rail block root bent the other way (pull at the top, lever 11.75) | b_eff 14.6 (less the pilot), depth 12.35, Kt 2.5 | Z | 2.14 | 12.50 | 5.83 | 3 | OK |
| 61 | cover push into the block, bound: all of it on the screw (spec §8 proof push, 34.2 N): shank bearing in the pilot | Ø3 x 6 | bearing | 1.90 | 25.00 | 13.16 | 2 | OK |
| 62 | cover push into the block, bound: all of it on the screw (spec §8 proof push, 34.2 N): tear-out of the 2.65 wall to the block's front face | 2 x 2.65 x 6, vertical planes (along the layers) | XY shear | 1.08 | 12.50 | 11.62 | 2 | OK |
| 63 | cover push into the block (spec §8 proof push, 34.2 N): rail block root bent the other way (pull at the top, lever 11.75) | b_eff 14.6 (less the pilot), depth 12.35, Kt 2.5 | Z | 2.72 | 12.50 | 4.60 | 2 | OK |

Information rows (not in the verdict):
| 64 | info: proof test, horn in a vice, one jaw blocked: 1736 N.mm through the pocket | as above | XY | 7.27 | 25.00 | 3.44 | 3 | OK |
| 65 | info: same tug with the port at the centre: -y strip + its rib | 13.3 x 6.5 + rib 6 x 10 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +3.8 N | Z | 1.18 | 12.50 | 10.56 | 3 | OK |
| 66 | info: same tug with the port at the centre: +y strip + its rib | 24.3 x 6.5 + rib 6 x 10 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +6.2 N | Z | 1.85 | 12.50 | 6.77 | 3 | OK |
| 67 | info, bound, kept since round 4: all of the cover's moment on its top screws, as if the post held nothing (M3 x 10, CAD): opening stall on jaw B, the cover's overturning moment 886 N.mm, 136 N each | M3, 6.95 engaged | Z shear | 2.08 | 6.25 | 3.00 | 3 | OK |
| 68 | info, the same bound, M3 x 18 with the camera (CAD): opening stall on jaw B, the cover's overturning moment 886 N.mm, 136 N each | M3, 11.45 engaged | Z shear | 1.26 | 6.25 | 4.95 | 3 | OK |
| 69 | info, the same bound on the worst standing at the screw (0.259), M3 x 10: opening stall on jaw B, the cover's overturning moment 886 N.mm, 136 N each | M3, 6.74 engaged | Z shear | 2.15 | 6.25 | 2.91 | 3 | **FAIL** |
| 70 | info: cover anchor driven: thread forming (4.6 MPa) + preload (0.87 MPa) in the ligament between the pilot and the V-groove (installation) | 1.10 printed (0.95 CAD) at the block top, Lame peak x1.79, along the layers | XY | 9.84 | 25.00 | 2.54 | 3 | **FAIL** |
| 71 | info: the same, if the ligament splits: M3 x 45 pull-out on the preload with that thread lost (sustained) | thread cylinder Ø3 x 10.36 | Z shear | 1.54 | 6.25 | 4.07 | 4 | OK |

MG90S tab-pilot strips (user decision 26 Oct: strips kept, first-print screw-strip check, spec §8):
| 72 | screw driving, M2 x 8 snug (100 N) + thread forming (0.04 N.m), sustained: lead-end pilot to the lead notch | strip 1.35 CAD / 1.55 printed; hoop stress at the pilot edge (Lame peak), p 6.3 MPa | Z | 7.80 | 12.50 | 1.60 | 4 | **FAIL** |
| 73 | same, mean hoop stress across the strip (p r / w): lead-end pilot to the lead notch | 1.55 printed | Z | 3.05 | 12.50 | 4.10 | 4 | OK |
| 74 | one jaw blocked: tab screw pulled with 14 N, its flank pressure added (short-term): lead-end pilot to the lead notch | Lame peak, p 6.5 MPa | Z | 8.09 | 12.50 | 1.55 | 3 | **FAIL** |
| 75 | screw driving, M2 x 8 snug (100 N) + thread forming (0.04 N.m), sustained: far-end pilot to the window | strip 1.45 CAD / 1.65 printed; hoop stress at the pilot edge (Lame peak), p 6.3 MPa | Z | 7.66 | 12.50 | 1.63 | 4 | **FAIL** |
| 76 | same, mean hoop stress across the strip (p r / w): far-end pilot to the window | 1.65 printed | Z | 2.86 | 12.50 | 4.36 | 4 | OK |
| 77 | one jaw blocked: tab screw pulled with 14 N, its flank pressure added (short-term): far-end pilot to the window | Lame peak, p 6.5 MPa | Z | 7.95 | 12.50 | 1.57 | 3 | **FAIL** |
| 78 | one jaw blocked: the case's end bears on the window's end (21.6 N): far-end pilot to the window | bridge over the pilot, span 1.7, depth 1.65 | Z | 0.14 | 12.50 | 90.72 | 3 | OK |
| 79 | claw stall reaction 216 N.mm: 7.4 N per tab screw along z (the strips lie beside this path) | pilot wall bearing Ø1.5 x 5.5 | XY | 0.90 | 25.00 | 27.79 | 3 | OK |
(drop: this load set has no drop case)

lowest SF 2.73 (required 4): top M3 x 10 (no camera) driven snug, 150 N preload (sustained): pull-out from the bulkhead top / thread cylinder Ø3 x 6.95
VERDICT (calculation): FAIL

The script also prints the what-ifs: wrist clamp, rail depth, ribs, and the top M3 options at the snug preload. The
last is quoted above.

---

# History

- **Round 6 self-check** (cad-engineer; git 8527ef6 / 105aafe): it reported NEEDS_TEST, lowest SF 3.00 (the bound row),
  with 2.94 as information. This review replaces it. The bound is now information, and the top M3s' snug-preload
  pull-out (missing before) governs.
- **Round 5 independent review** (git be24872, 60d5e8f has its full table): NEEDS_TEST, 3.03. The bulkhead top on a
  slice plane was a DFM fail, fixed in round 6.
- **Round 4** (git a701995): PASS. The anchor pilot was added.

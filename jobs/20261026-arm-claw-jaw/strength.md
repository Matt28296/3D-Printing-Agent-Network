VERDICT: NEEDS_TEST

# Strength check: 20261026-arm-claw-jaw (round 3)

strength-analyst (independent review of the round-3 geometry) · 2026-10-26 ·
`python3 jobs/20261026-arm-claw-jaw/strength_calc.py` (plain python3, run from the project root: reads `claw_frame.py`,
this job's `model.py` and `tools/hobby_parts.py` with `ast`, and runs `rack_outline` from `tools/gears.py` on its own;
`--cad` in the CAD venv compares the hand sections with the build123d solid)

Round 2's failure is fixed. The grooves now stop at x 70.6, so the thin tip has none: the last groove gives 3.57 and the
ungrooved tip 4.26. **The neck root governs at 3.52** (grip with one jaw blocked, and the same for the claw opening
against an obstacle), exactly as the designer predicted.

The rack teeth at face 12 with 0.35 thinning give 3.95. Every row passes; the verdict is NEEDS_TEST only because the
allowables are placeholders.

## Round-2 fixes: made?

| Round-2 required change | Round 3 as built | Made? |
|---|---|---|
| 1. Fingertip: grooves stop at x 66, or BLADE_T 7 | GROOVE_X (62.6, 71): grooves at 62.6…70.6. Not x 66, but the last groove sits where the finger is still 7.9 thick | Yes: the last groove gives 3.57 (row 10), the ungrooved tip 4.26 (row 11). The neck root governs |
| 2. Rack teeth with the pinion's change (FACE_W 12, RACK_BACKLASH 0.7) | FACE_W 12 (x 22.6–34.6), RACK_BACKLASH 0.7, BED_CHAMFER 0.25 | Yes: 3.95 on an effective face of 12 − 0.25 − 0.25 = 11.5 (row 12) |
| Blade 45 → 43, fingertip kept at x 83.35 | NECK_X1 40.35, taper x 60.35–75.35 | The levers from the rack face to the grip are 2 mm shorter; the neck root's moments drop by ~2 % (3.44 → 3.52) |

The `--cad` cross-check matches the hand sections to 0.1 mm² from x 42 to the tip. At the neck root the solid is larger
(268 mm² at x 34.65 against 200 mm²) because of the r 4 fillets the hand section leaves out, which is conservative.

## Load cases

| # | Case | Load | Point and direction | Type, SF req |
|---|---|---|---|---|
| 1 | Stall, one jaw blocked (spec) | 21.6 N | Grip face at x 50, 60, 70 and 80.35 (3 mm from the tip), bottom / middle / top, along y away from the other jaw | Short-term, 3 |
| 2 | Stall, both jaws, every full-close grip | 10.8 N per jaw | As 1 | Cyclic, 4 |
| 3 | The claw opens against an obstacle (Architect: a design case) | 21.6 N on the outer face | As 1, reversed | Short-term, 3 |
| 4 | Crash (required) | 13 N at the tip in the arm plane, every 15° | Tip, z −6 / 0 / +6 | Short-term, 3 |
| 5 | Yaw stall | 7.1 N along ±z | Tip | Short-term, 3 |
| 6 | Handling | 5 N any direction (30° steps, five elevations) | Tip | Short-term, 3 |
| 7 | Rack teeth | 21.6 N / 10.8 N / the crash's 13 N | Teeth | Short-term 3 / cyclic 4 |
| 8 | Rack ends on the guides | The couple of case 1: 27.0 N (open), 19.8 N (closed) | Lip / rail block and front plate | Short-term, 3 |

The cover's round-3 fix doesn't change any load on the jaw.

## Build direction and method

The jaw prints standing on the rack's back end (claw x = print Z). Every normal stress along x in the neck and the
finger, and every shear on a plane x = const, acts across the layers: 12.5 MPa normal, 6.25 MPa shear. The rack teeth
lie in the bed plane: 25 MPa.

- **Sections.** Every 0.1 mm from the rack's front face (x 34.6) to 3 mm short of each load point. Each section is the
  plan outline's y range times the side outline's z range, minus the V-notch and the 0.6 mm groove at each groove
  centre. That polygon gives exact A, centroid and I_yy, I_zz, I_yz.
- **Stress.** Normal stress at every vertex from N, M_y and M_z (unsymmetric bending), times the Kt of that vertex's
  face. Shear is torsion (Roark rectangle) + 1.5 V/A. Combined across the layers as
  (σ/12.5)² + (τ/6.25)² = 1/SF². σ_max and τ_max are combined even when they sit at different points, which is
  conservative.
- **Kt:**
  - neck root: 1.7 on the y faces (r 4, r/h 0.2); 2.5 on the bottom face, where the rack's teeth leave a 2.1 mm step;
    1.0 on top, flush with the rack's back;
  - r 3 kinks: 1.5 / 1.7;
  - V-grooves: 2.5.
- **The neck root, as built.** The neck (20 × 10) sits on the rack's 10 mm solid back from the rack's front face
  (x 34.6) to the blades (x 40.35).
  - Under the grip, the governing combination is M_z (Kt 1.7 at the fillets) with the torsion of the grip's 24.75 mm
    offset below the neck.
  - The torsional shear peaks at the long faces' mid-points. The bottom face is the one with the toothed step.
  - The teeth are thin ribs (1.6–2.1 mm along y) whose faces are normal to y, so they cannot carry that face's τ_xy. The
    step therefore doesn't concentrate the torsional shear (Kts ≈ 1), while it does concentrate bending (Kt 2.5, kept).
  - Information row 17 bounds it: Kts 1.5 there gives 3.48.
- **Rack teeth.** The pinion report's method: load at the rack's highest point of single-tooth contact, the
  Dolan–Broghamer fillet factor in the root, effective face 11.5.

## Assumptions

- The stall force is the same anywhere along the grip face, so the tip and the face's corners are the worst points.
  At the corner farthest from the jaw's own rack (z −8.5), the grip also twists the finger.
- When the jaw is pushed sideways, the cover's strip and the pinion can prop the neck. That is ignored, which is
  conservative for the neck.
- The crash force is SYS-11's arm push, 13 N. The wrist's back-drive torque is unmeasured.
- Service temperature is 40 °C against PETG softening at about 70 °C: OK.

## Allowables and sources

`library/materials.csv` has no measured row, so these are the strength-checks **placeholder** PETG values and
NEEDS_TEST is the best possible verdict.

| Quantity | Value | Source |
|---|---|---|
| Along the layers (rack teeth, bearing) | 25 MPa | Skill placeholder, PETG |
| Across the layers (all neck and finger bending) | 12.5 MPa | 0.5 × in-plane |
| Interlayer shear | 6.25 MPa | 0.5 × 12.5 (Tresca) |
| Kt | 2.5 sharp; 1.5 for r ≥ 0.25 h; 1.7 for r/h 0.15–0.25 | Skill; the 1.7 is a Peterson-based interpolation |

## Results (copied from `python3 strength_calc.py`)

"Z comb" rows combine across-layer normal stress and interlayer shear; their stress column is 12.5 / SF.

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | grip at stall, one jaw blocked, 21.6 N on the grip face [x 80.35 z -8.5] | x 34.6: sigma 2.52, tau 1.25 | Z comb | 3.55 | 12.50 | 3.52 | 3 | OK |
| 2 | grip at stall, both jaws, 10.8 N each (every full-close grip, cyclic) [x 80.35 z -8.5] | x 34.6: sigma 1.26, tau 0.63 | Z comb | 1.78 | 12.50 | 7.04 | 4 | OK |
| 3 | added: claw opening against an obstacle, 21.6 N on the outer face [x 80.35 z -8.5] | x 34.6: sigma 2.52, tau 1.25 | Z comb | 3.55 | 12.50 | 3.52 | 3 | OK |
| 4 | crash: 13 N at the fingertip in the arm plane, any direction (wrist back-driven) [tip z -6, 315 deg] | x 34.6: sigma 2.93, tau 0.49 | Z comb | 3.08 | 12.50 | 4.05 | 3 | OK |
| 5 | yaw stall: 7.1 N out of the arm plane at the fingertip, either way [tip z -6, along +z] | x 34.6: sigma 2.60, tau 0.18 | Z comb | 2.62 | 12.50 | 4.77 | 3 | OK |
| 6 | handling: 5 N at the fingertip, any direction [tip z -6, 330 deg in plan, 45 deg elevation] | x 34.6: sigma 2.11, tau 0.05 | Z comb | 2.11 | 12.50 | 5.93 | 3 | OK |
| 7 | neck root (x 34.6..35.1, r 4 fillets, toothed bottom edge): one jaw blocked, 21.6 N on the grip face [x 80.35 z -8.5] | x 34.6: sigma 2.52, tau 1.25 | Z comb | 3.55 | 12.50 | 3.52 | 3 | OK |
| 8 | neck root: opening against an obstacle, 21.6 N on the outer face [x 80.35 z -8.5] | x 34.6: sigma 2.52, tau 1.25 | Z comb | 3.55 | 12.50 | 3.52 | 3 | OK |
| 9 | neck root: yaw stall 7.1 N along z at the tip (bottom face, Kt 2.5) [tip z -6, along +z] | x 34.6: sigma 2.60, tau 0.18 | Z comb | 2.62 | 12.50 | 4.77 | 3 | OK |
| 10 | last groove (x 70.6, Kt 2.5): one jaw blocked, 21.6 N on the grip face [x 80.35 z -8.5] | x 70.6: sigma 3.02, tau 0.89 | Z comb | 3.50 | 12.50 | 3.57 | 3 | OK |
| 11 | ungrooved tip beyond the last groove (x 71.6..77.3): one jaw blocked [x 80.35 z +8.5] | x 77.3: sigma 0.69, tau 1.43 | Z comb | 2.93 | 12.50 | 4.26 | 3 | OK |
| 12 | rack teeth, one jaw blocked (21.6 N), HPSTC + Kf, face 11.50 | root width 1.88, Kf 1.89 | XY | 6.34 | 25.00 | 3.95 | 3 | OK |
| 13 | rack teeth, both jaws (10.8 N, cyclic), HPSTC + Kf | root width 1.88, Kf 1.89 | XY | 3.17 | 25.00 | 7.89 | 4 | OK |
| 14 | rack teeth, crash 13 N along y on one finger (held by the claw servo) | root width 1.88, Kf 1.89 | XY | 3.81 | 25.00 | 6.56 | 3 | OK |
| 15 | rack bar bending between its end contacts, one jaw blocked (couple 1118 N.mm, stress along y: in the bed plane) | solid back 12 x 10 | XY | 5.59 | 25.00 | 4.47 | 3 | OK |
| 16 | rack end on the lip / front plate, thrust 27.0 N (jaws open; 19.8 closed), compression across the layers | 3 mm x 10.0 of the end face | Z comp | 0.90 | 25.00 | 27.79 | 3 | OK |

**Lowest SF: 3.52 (required 3), the neck root** (x 34.6). It comes from the one-jaw grip at the grip face's bottom
corner 3 mm from the tip, and from the opening push at the same point. For reference: every Kt = 1 gives 4.30.

Information rows (not in the verdict):

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 17 | info: neck root's bottom face mid-point, grip torsion with a torsional Kts 1.5 bound (see strength.md) | tau 1.80 (sigma 0 there) | Z shear | 1.80 | 6.25 | 3.48 | 3 | OK |
| 18 | info: rack teeth, one jaw blocked, Lewis tip load, no Kf, full face 12 | width 1.36 | XY | 5.44 | 25.00 | 4.60 | 3 | OK |

## What-if lines (in the script)

- Grooves stopping at x 70 or 66, r 0.3 groove roots, or a 7 mm tip: all 3.52. The neck root governs, and the
  finger's options no longer change the result.
- Rack teeth at face 12: rack backlash 0.5 → 4.29, **0.7 (as built) → 3.95**, 0.8 → 3.77.

## Required changes

None. If more margin at the neck root is wanted later, the cheapest lever is the fillet: its r 4 at the y faces (Kt 1.7)
carries the governing bending. The neck can't grow without changing the cover's slots.

## Proof test (spec §8)

It still matches:
- 32 N pull and 32 N opening push at the far edge of the grip face, 3 mm from the tip (1.5 × the one-jaw stall and the
  opening stall);
- 10.7 N sideways (1.5 × the yaw stall);
- the grip and dowel tests.

At 1.5 × the neck root sits at SF 2.35 on the placeholder allowables. A real PETG part should hold; this is the test that
replaces the placeholder.

Update one wording: "the grooves nearest the tip" → **"the last groove (x 70.6) and the ungrooved tip beyond it"**. Keep
"the neck's root fillets", and add **"the neck's bottom edge where it meets the rack's teeth"**.

Run step 2 (the 32 N push towards the other jaw) on jaw B only once the cover's round-3 fix is in. On the as-built cover
that push cracks the cover's top wall first (cover report).

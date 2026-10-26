VERDICT: FAIL

# Strength check: 20261026-arm-claw-jaw (round 1)

strength-analyst · 2026-10-26 · `python3 strength_calc.py` (plain python3; reads `claw_frame.py`, this job's `model.py`,
`tools/hobby_parts.py` and `geometry.json`)

The jaw prints standing (claw +x = print Z). Every stress the finger loads put on the neck and the finger root acts
across the layers: grip bending, sideways bending, axial, torsion and shear. The 14 × 5 neck and the 6 mm-thick,
5–8 mm-tall finger root are 3 to 8 times too weak for that. At the 24 N stall with one jaw blocked:

- the finger root at the flare end (x 38) reaches 33 MPa against the 12.5 MPa across-layer allowable: **SF 0.37**;
- the neck root reaches **0.69**;
- the normal both-jaw grip (12 N, cyclic) gives **0.74**;
- a 5 N hand push on the fingertip gives **0.68**.

Even with no stress concentration at all, the finger root is at SF 0.75. The rack teeth pass.

This cannot be fixed with one dimension. A verified redesign is given under **Required changes**.

## Load cases

| # | Case | Load | Point and direction | Type, SF req |
|---|---|---|---|---|
| 1 | Grip at stall, one jaw blocked | 24 N (216 N·mm / 9 mm) | grip face, 3 mm from the tip (x 73.15), on the V-notch line (z = ZS), along −y | short-term, 3 |
| 2 | Grip at stall, both jaws (every full-close grip) | 12 N per jaw | as 1 | cyclic, 4 |
| 3 | Hand push (arm review) | 5 N along ±z | fingertip (x 76.15), one finger | short-term, 3 |
| 4 | Yaw-stall sweep (arm review), added for the jaw | every pose's fingertip force (≤ 6.6 N along z, ≤ 2.8 N along y, ≤ 13 N along x), both signs | fingertip, one finger | short-term, 3 |
| 5 | Rack teeth | 24 N / 12 N tangential | pitch line, tip load | short-term / cyclic |
| 6 | Rack ends on the guides | thrust couple of case 1, 31 N | lip and front plate | short-term, 3 |

The grip force sits 10.5 mm below the neck (z = ZS against the neck centroid at ZS + 10.5), so case 1 also twists the
neck by 252 N·mm. The spec calls the sideways push "along the layers". It is not: when the finger grows along print
Z, bending in either direction puts normal stress along Z.

## Critical sections and method

Sections are built from the parameters as rectangles: the neck, then the blade with its 45° lower edge, the 3 mm 45°
step on its top edge, the 45° flare in plan, the grooves and the V-notch. They match the build123d sections of
`design()` (x 27.5: A 70.0, I_grip 1143, I_side 146; x 34.15: 40.0 / 338 / 83; x 37: 51.4 / 208 / 277; x 49.15: 117.8 /
348 / 4000; CAD 70.0 / 1143 / 146, 40.0 / 337 / 83, 51.5 / 208 / 278, 117.8 / 346 / 3999).

Every section from the rack face to 6 mm short of the tip is checked:

- **Bending**: unsymmetric bending (I_yz included), each direction with its own Kt.
- **Kt values**:
  - 2.5 at the neck root, where it meets the rack face square;
  - 2.0 at the 225° re-entrant corners: the neck bottom turning into the 45° lower edge and the top-edge step for
    sideways bending, and the flare end on the outer face for grip bending;
  - 2.0 at the 0.6 mm V-grooves on the grip face.
- **Combination**: torsion (thin-strip J) plus transverse shear as interlayer shear, combined with
  (σ/12.5)² + (τ/6.25)² = 1/SF².

## Assumptions

- The stall force is the same at any grip position, so the worst load point is the fingertip.
- The yaw-stall and hand-push forces are the arm jobs' sweep forces, applied to one finger.
- Rack teeth are drawn in the bed plane, so tooth bending runs along the layers (25 MPa). Lewis with Y = 0.485 for the
  rack, and a direct root check of the gears.py trapezoid (root 2.43 wide, tip load 2.25 above it).

## Allowables and sources

`library/materials.csv` has no measured row: these are the strength-checks **placeholder** PETG values. NEEDS_TEST is the
best verdict possible.

| Quantity | Value | Source |
|---|---|---|
| Along the layers (rack teeth, bearing) | 25 MPa | skill placeholder, PETG |
| Across the layers (all finger and neck bending) | 12.5 MPa | placeholder × 0.5 |
| Interlayer shear | 6.25 MPa | 0.5 × 12.5 (Tresca) |
| Kt | 2.5 sharp corner, 2.0 for 225° corners and V-grooves, 1.5 with r ≥ 0.25 × section | skill / arm-job convention |

Required SF is 3 for short-term loads and 4 for cyclic loads. Service temperature 40 °C: OK.

## Results (copied from `python3 strength_calc.py`)

"Z comb" rows combine normal stress across the layers with interlayer shear. The stress column is 12.5 / SF.

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | grip at stall, one jaw blocked, 24 N: neck root at the rack face (Kt 2.5) x 27.4, sigma 16.8 tau 3.3 | Z comb | 18.05 | 12.50 | 0.69 | 3 | **FAIL** |
| 2 | grip at stall, one jaw blocked, 24 N: neck + finger root (worst section) x 38.2, sigma 33.4 tau 2.7 | Z comb | 33.85 | 12.50 | 0.37 | 3 | **FAIL** |
| 3 | grip at stall, both jaws, 12 N each (cyclic): neck root at the rack face (Kt 2.5) x 27.4, sigma 8.4 tau 1.7 | Z comb | 9.03 | 12.50 | 1.38 | 4 | **FAIL** |
| 4 | grip at stall, both jaws, 12 N each (cyclic): neck + finger root (worst section) x 38.2, sigma 16.7 tau 1.4 | Z comb | 16.92 | 12.50 | 0.74 | 4 | **FAIL** |
| 5 | hand push 5 N at the fingertip: neck root (Kt 2.5) x 27.4, sigma 10.4 tau 0.3 | Z comb | 10.46 | 12.50 | 1.19 | 3 | **FAIL** |
| 6 | yaw-stall sweep at the fingertip: neck root (Kt 2.5) x 27.4, sigma 19.6 tau 0.2 | Z comb | 19.57 | 12.50 | 0.64 | 3 | **FAIL** |
| 7 | hand push 5 N at the fingertip: neck + finger root (worst section) x 34.0, sigma 18.4 tau 0.5 | Z comb | 18.47 | 12.50 | 0.68 | 3 | **FAIL** |
| 8 | yaw-stall sweep at the fingertip: neck + finger root (worst section) x 34.0, sigma 32.0 tau 0.7 | Z comb | 32.07 | 12.50 | 0.39 | 3 | **FAIL** |
| 9 | rack teeth, one jaw blocked 24 N: Lewis (rack Y 0.485), face 8 | XY | 6.19 | 25.00 | 4.04 | 3 | OK |
| 10 | rack teeth, one jaw blocked: tooth root 2.43 wide, tip load 2.25 m above it | XY | 6.85 | 25.00 | 3.65 | 3 | OK |
| 11 | rack teeth, both jaws (cyclic) 12 N: Lewis (rack Y 0.485), face 8 | XY | 3.09 | 25.00 | 8.08 | 4 | OK |
| 12 | rack teeth, both jaws (cyclic): tooth root 2.43 wide, tip load 2.25 m above it | XY | 3.43 | 25.00 | 7.29 | 4 | OK |
| 13 | rack end bearing on the lip / front plate, thrust couple 31 N (3 mm x rack height) | XY | 1.26 | 25.00 | 19.83 | 3 | OK |

**Lowest SF 0.37 (required 3): one jaw blocked, finger root at the flare end, x 38.**

## Required changes (rows 1–8; candidates computed in the script's what-if lines)

The neck can only be as tall as the solid part of the rack it grows from, which is 6 mm. A 6 mm neck fails the sideways
cases whatever its length (candidate A: lowest SF 2.10). So the rack must get taller.

**Recommended, candidate C: lowest SF 3.71, every jaw row passing.** With the cover's front plate at 5 mm, as the cover
report asks, it is still 3.71.

1. **Taller rack.** In `claw_frame.py`, RACK_BACK 6 → 10. Each rack is 4 mm taller, so ZS, the cover, the frame
   bulkhead and the camera height all re-flow: the claw grows 8 mm in z, and CAM_ZC should go +8.
2. **Taller, longer neck.** NECK_Z (8, 13) → (RACK_ROOT, RACK_OUT), i.e. 10 tall, on the rack's solid back strip with no
   tooth gaps under it. NECK_Y 14 → 20.
3. **Longer rack.** RACK_Y[0] −5π → −7π (two more teeth at the −y end), so the 20 mm neck sits fully on the rack.
4. **Thicker finger.** 12 thick instead of 6 from the neck to x ≈ 51, tapering to 6 by x ≈ 66. The grip face stays at
   y = 0; the extra thickness goes outboard.
5. **Full-height gusset, flat top.** Make the 45° gusset from the 20 mm neck into the 12 mm finger span the finger's full
   height, not just the neck band. Keep the finger's top edge at the neck top (no 3 mm step down).
6. **Fillets.** r ≥ 4 where the neck meets the rack face (drawn in the bed plane, so it prints). r ≥ 3 at the 45° kinks
   and the gusset end.

**Minimum that passes, candidate D**: RACK_BACK 6 → 8 and a 20 × 8 neck, everything else as C. Lowest SF 3.06, or 3.02
with the 5 mm front plate. No margin.

Consequences for the other claw parts: slot A becomes neck height + 0.5. With C it reaches the top wall. Keep a strip of
front plate above slot A on the −y half (C with an 8 mm neck, or a 1 mm lip on the rack's back face), so rack A still
bears forward at its −y end when a jaw is pushed open. The cover and frame then have to be re-checked.

**Alternative the design-lead may prefer:** split the jaw. Print the rack standing as now, and print the finger with its
neck flat, with claw y vertical: all finger bending then runs along the layers, which doubles the allowable. Bolt the
finger to the rack's front face with 2 × M3, in vertical pilots in the rack. This needs its own check, mainly screw
pull-out under the ≈1.1 N·m grip moment.

## Proof test (for the redesigned jaw; adjusts spec §8)

1. Grip a 20 mm wooden block clamped in a vice, centred and then 8 mm off-centre. Full close for 10 s, 5 times each.
2. Grip a 10 mm dowel at the fingertips and hang 200 g from it for 1 min.
3. With the claw closed, push 7.5 N (1.5 × the hand push) sideways (±z) on one fingertip, 1 min each way.

Pass: no cracks or whitening at the neck, the gusset or the finger root; no layer lines opening; the jaws still slide
freely.

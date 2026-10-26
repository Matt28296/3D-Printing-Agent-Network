VERDICT: NEEDS_TEST

# Strength check: 20261025-arm-base (round 3)

strength-analyst · 2026-10-26 · `python3 strength_calc.py` reads model.py, tools/hobby_parts.py and geometry.json

Round 3: the cradle screws are now M3×10, so they engage the full 6 mm boss pilot without bottoming out (script FIT
line: ok). Every check is at SF 4.10 or above. Still required, as before: the base **must be screwed down**, because
it tips over with the arm out.

## Round 1 → round 2 → round 3

| | Round 1 | Round 2 |
|---|---|---|
| Lowest SF | 4.00, servo tab screws under a yaw stall | 4.10, cradle-boss root under USB insertion |
| Servo tab screws, yaw stall | 4.00 | 4.35 (M 2440 vs 2655 N·mm) |
| Ring pilots | r 48 | r 47.5: tear-out ligament 3.1 mm. The ring now uses M3×6 screws, 3 mm engaged |
| Stability | tips (223 vs 147 N·mm) | still tips (274 vs 170 N·mm); desk screws required (the build guide says so) |

**Round 2 → round 3:** cradle screws M3×12 → M3×10: 6 mm engaged in the 6 mm pilot with no overrun; pull-out SF 61
(unchanged, the engagement was already capped at 6 mm). Turntable volume −53 mm³: no SF changed.

## Load cases

**Inputs, re-derived (round 2).** Each script now reads its parameters from the jobs' `model.py` (top-level constants
evaluated with `ast`), servo data from `tools/hobby_parts.py`, and masses from each `geometry.json` volume x 1.27 g/cm³:
upper link 50.4 g, forearm 37.3 g, gripper base 30.8 g, jaw 8.5 g, turntable 113.5 g. MG996R 55 g and SG90 9 g; horn
+ clamp screw 5 g (MG996R) / 2 g (SG90); 10 g cable allowance; 50 g payload. CGs come from the parameters (within
4 mm of the build123d centres of mass). The world-Y stack is rebuilt from the new thicknesses: horn faces at Y 11.5 /
36.0 / 55.4 / 72.8 and the fingertip at Y 74.8 (assembly plan: ≈75). Static moments with the arm straight and
horizontal: about the yaw axis 442 N·mm, shoulder 415 (plan ≈410, 41 % of stall), elbow 186 (plan ≈180), wrist 71,
gripper 29. Pose-independent out-of-plane weight moments: shoulder horn 74, elbow 34, wrist 13, upright root 137 N·mm.
Dynamic factor x2.

**Load cases** (spec §4 now lists them all): every servo stall (MG996R 1000 N·mm, SG90 160 N·mm); weight x2 (sustained,
SF 4); a **base-yaw stall into a side obstacle**, swept over shoulder 0–180°, elbow ±90° and wrist ±90° in 5° steps
(F = 1000/R, tangential, scaled down wherever a pitch servo backdrives first; up to 12 N at the fingertip); a **5 N
sideways hand push** at the fingertip; and the shoulder stall with the fingertip pressing on the desk (1158 N·mm about
the base horn). Short-term cases need SF 3.

Base-specific: the overturning moment from each case goes through the base servo's 4 tab screws (ring ignored on that
path); the ring catch force when the turntable rocks onto the ring is R = M/(42.5 − 5.5); the spec's 20 N and 50 N rim
loads; USB insertion 20 N shared by the 3 cradle bosses; a 10 N jumper pull. The part prints upside down: top-plate
bending and pilot bearing run along the layers; screw pull-out and the boss roots are across them.

## Assumptions

- The servo tab screws engage about 7 mm in plate + boss. The weak axis has a 14.85 lever (screws at y ±5, pivot on
  the tab edge), and because the turntable yaws, every moment is taken on that axis.
- Top plate: a strip cantilevered 20.3 mm from the nearest wall, b_eff = 2a + 2 x ring height.
- Cradle bosses Ø7/Ø2.8 × 6 mm, sharp root Kt 2.5. Ring screws M3×6 (build guide) through the 3 mm tab, 3 mm engaged.
- Pull-out: τ = F/(π·d_pilot·L), against the interlayer shear allowable.

## Allowables and sources
`library/materials.csv` still has no measured row, and no printed-specimen datasheet is in `inputs/`, so these are the
strength-checks **placeholder** values for PETG. **NEEDS_TEST is the best verdict possible.**

| Quantity | Value | Source |
|---|---|---|
| Tension/bending along the layers (XY) | 25 MPa | skill placeholder, PETG |
| Tension/bending across the layers (Z) | 12.5 MPa | placeholder x 0.5 |
| Shear in-plane / interlayer (screw pull-out, washer pull-through, tear-out in vertical walls) | 12.5 / 6.25 MPa | 0.5 x the normal value (Tresca), assumption |
| Bearing, compression (any direction) | 25 MPa | in-plane value: compression does not separate layers |
| Kt | 2.5 sharp internal corner or window corner; 2.0 the 45° root wedge (two 135° corners); 2 hole; 1.5 rounded pocket tip | skill (2.0 for the wedge is my interpolation) |

Required SF: 3 short-term, 4 sustained or cyclic. Service temperature 40 °C (servo cases up to 45 °C) against PETG
softening at about 70 °C: margin of 25 °C or more, OK.

## Results (copied from `python3 strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | base stall 1000 N.mm: tab-pilot bearing (plate 4 only) | XY | 1.17 | 25.00 | 21.42 | 3 | OK |
| 2 | base stall: pilot-to-window ligament 2.20 tear-out | XY shear | 0.69 | 12.50 | 18.13 | 3 | OK |
| 3 | weight x2 (sustained): servo tab screws pull-out, M 903 on the 14.85 lever | Z shear | 0.53 | 6.25 | 11.75 | 4 | OK |
| 4 | shoulder stall on desk: servo tab screws pull-out, M 1158 on the 14.85 lever | Z shear | 0.68 | 6.25 | 9.16 | 3 | OK |
| 5 | 20 N on the turntable rim (spec): servo tab screws pull-out, M 960 on the 14.85 lever | Z shear | 0.57 | 6.25 | 11.06 | 3 | OK |
| 6 | yaw-stall sweep: servo tab screws pull-out, M 2440 on the 14.85 lever | Z shear | 1.44 | 6.25 | 4.35 | 3 | OK |
| 7 | hand push 5 N: servo tab screws pull-out, M 1728 on the 14.85 lever | Z shear | 1.02 | 6.25 | 6.14 | 3 | OK |
| 8 | 20 N on the rim (spec), R 20.0 N: top plate strip bending | XY | 2.16 | 25.00 | 11.59 | 3 | OK |
| 9 | 20 N on the rim (spec): ring-screw pilot tear-out at 270 deg (friction 0.3) | XY shear | 0.24 | 12.50 | 51.67 | 3 | OK |
| 10 | 20 N on the rim (spec): ring screw M3x6 pull-out (3 mm engaged), friction lift ignored, uplift 0.3R | Z shear | 0.24 | 6.25 | 25.53 | 3 | OK |
| 11 | yaw-stall ring catch, R 45.2 N: top plate strip bending | XY | 4.88 | 25.00 | 5.13 | 3 | OK |
| 12 | yaw-stall ring catch: ring-screw pilot tear-out at 270 deg (friction 0.3) | XY shear | 0.55 | 12.50 | 22.85 | 3 | OK |
| 13 | yaw-stall ring catch: ring screw M3x6 pull-out (3 mm engaged), friction lift ignored, uplift 0.3R | Z shear | 0.55 | 6.25 | 11.29 | 3 | OK |
| 14 | hand-push ring catch, R 44.5 N: top plate strip bending | XY | 4.79 | 25.00 | 5.21 | 3 | OK |
| 15 | hand-push ring catch: ring-screw pilot tear-out at 270 deg (friction 0.3) | XY shear | 0.54 | 12.50 | 23.24 | 3 | OK |
| 16 | hand-push ring catch: ring screw M3x6 pull-out (3 mm engaged), friction lift ignored, uplift 0.3R | Z shear | 0.54 | 6.25 | 11.48 | 3 | OK |
| 17 | USB insertion 20 N / 3 bosses: cradle-boss root bending (Kt 2.5) | Z | 3.05 | 12.50 | 4.10 | 3 | OK |
| 18 | cradle screw pull-out, 6 mm engaged, 10 N jumper pull / 2 | Z shear | 0.10 | 6.25 | 61.26 | 3 | OK |

Advisory rows (not in the verdict, reason under Assumptions):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| proof 50 N on the rim (spec 8): servo tab screws pull-out | Z shear | 1.41 | 6.25 | 4.42 | 2 |
| proof 50 N on the rim: top plate strip bending (R 50 N) | XY | 5.39 | 25.00 | 4.64 | 2 |

**lowest SF 4.10 (required 3) at: USB insertion 20 N / 3 bosses: cradle-boss root bending (Kt 2.5)**

Script notes:

```
arm model: Y horn faces shoulder 11.5, elbow 36.0, wrist 55.4, gripper 72.8; fingertip Y 74.8; masses UL 50.4 FA 37.3 GB 30.8 JW 8.5 TT 113.5 g; CG x UL 39.9 FA 35.5 GB 52.6 (z 6.8) JW 20.5
yaw  sweep: tab Mx=1777 My=1672 Mz=1000; disk Mx=1673 My=1489 Mz=1000; desk Mx=2030 My=2117 Mz=1000
hand sweep: tab Mx=1728 My=0 Mz=1000; disk Mx=1645 My=0 Mz=1000; desk Mx=1928 My=0 Mz=1000
FIT: cradle M3x10 from the counterbore floor (4 mm of cradle) reaches 6 mm into the base boss, whose blind pilot is 6 deep -> ok
STABILITY: base-side weight 3.26 N, arm 3.23 N
  arm straight out over the 52 mm edge: tipping 274 vs restoring 170 N.mm -> TIPS
  yaw case: overturning 2117 vs restoring 338 N.mm -> TIPS (desk-screw uplift when screwed down: 9.0 N per screw)
  hand case: overturning 1928 vs restoring 338 N.mm -> TIPS (desk-screw uplift when screwed down: 8.0 N per screw)
```

## Proof test (spec §8 confirmed)
The §8 test (base screwed down, 50 N on the turntable rim, 1 min at each of 4 positions, plus 5 USB plug cycles) is
right. At 50 N the servo tab screws are at SF 4.4 and the plate at SF 4.6 on the placeholder allowables (advisory
rows). The M3×10 cradle screws should seat without bottoming out.

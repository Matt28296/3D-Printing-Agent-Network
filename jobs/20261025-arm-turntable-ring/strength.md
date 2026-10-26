VERDICT: NEEDS_TEST

# Strength check: 20261025-arm-turntable-ring (round 2)

strength-analyst · 2026-10-26 · `python3 strength_calc.py` reads model.py, tools/hobby_parts.py and geometry.json

## Round 4 (claw v2 + Brio, 2026-10-26)

The end effector is now the claw v2 with a Logitech Brio (jobs `20261026-arm-claw-frame`, `-cover`, `-pinion`, `-jaw`
×2 and `20261026-arm-camera-mount`). `strength_calc.py` reads it from those jobs: the layout from `claw_frame.py`, the
masses from their `geometry.json`, and their measured CoGs (it warns if a claw part's volume changes). Everything else
is as in round 2.

- 172 g beyond the wrist horn, CoG 8.3 mm in front of the wrist axis and 39.5 mm outboard of the claw's back face. The
  Brio's CoG is at world Y 117.6.
- Fingertip 76.15 mm from the wrist axis (was ≈95), at world Y 75.9 (was 74.8). Wrist servo MG90S, 216 N·mm stall (was
  SG90, 160). 50 g payload at the fingertip, as before.
- Arm straight and horizontal: shoulder 625 N·mm (was 415), elbow 275 (was 186), about the yaw axis 665 (was 442).

For the ring, only the catch forces change: the yaw-stall catch goes 45.2 → 46.3 N and the hand-push catch 44.5 → 41.9 N.

| Rows | Round 2 SF | Round 4 SF |
|---|---|---|
| 6–10 yaw-stall catch: wall bearing / edgewise bending / interlayer shear / tab bearing / tab tear-out | 16.59 / 11.06 / 27.65 / 16.59 / 14.93 | 16.20 / 10.80 / 27.00 / 16.20 / 14.58 |
| 11–15 hand-push catch: same order | 16.87 / 11.25 / 28.12 / 16.87 / 15.18 | 17.89 / 11.93 / 29.82 / 17.89 / 16.11 |

**Verdict unchanged: NEEDS_TEST.** The lowest SF is still 3.39 (screw-head clamp at assembly), and the §8 proof test
still applies.

**Advisory, not in this job's load cases.** The claw and camera-mount specs add a 10 N tug on the Brio's USB cable at
the camera. Servo-capped as in the yaw sweep, it would make the turntable catch on the ring with 82.9 N. The lowest ring
row is then 6.03 (wall edgewise bending), so the ring covers it.

## Round 2 summary

The ring only takes load when the turntable rocks 1.5 mm onto it, and the clamped base horn makes that less likely
than in round 1. Every check is at SF 3.39 or above. The governing row is the assembly case: the tab crushed under a
pan head with no washer.

## Round 1 → round 2

| | Round 1 | Round 2 |
|---|---|---|
| Lowest SF | 3.67, screw-head clamp | 3.39, screw-head clamp (the tab hole is now Ø3.6 in CAD, so the head's bearing ring is smaller) |
| Wall | 3.5 thick, 13 tall | 3.0 thick (R_OUT 44), 15 tall: friction checks SF ≥ 8.6 |
| Worst ring catch | 52.5 N | 45.2 N |

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

Ring force R = M_x/(ring mid radius 42.5 − hub radius 5.5) from the turntable sweep: spec 20 N on the rim, the 50 N
§8 proof (advisory rows), a yaw-stall catch of 45.2 N and a hand-push catch of 44.5 N. Friction 0.3R acts tangentially,
which puts edgewise bending (across the layers) and interlayer shear in the wall. Screw clamp: 100 N under an M3 pan
head (assembly, sustained).

## Assumptions

- Contact patch: 10 mm of arc × the 3 mm wall. The bending wall segment is 2 x the 15 mm height.
- Friction is taken by a single tab. The tab hole is Ø3.6 (CAD), edge distance 4.5.
- A snug hand-tightened M3×6 is taken as 100 N. Tighten until snug, or fit an M3 washer (which doubles the bearing area).

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

Round-2 values. The script now prints the round-4 values; the rows that changed are listed under Round 4 at the top.

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | 20 N on the rim (spec): ring wall bearing, R 20.0 N (compression) | XY | 0.67 | 25.00 | 37.50 | 3 | OK |
| 2 | 20 N on the rim (spec): wall edgewise bending from friction 0.3R, 30 mm segment (Z, Kt 2.5) | Z | 0.50 | 12.50 | 25.00 | 3 | OK |
| 3 | 20 N on the rim (spec): interlayer shear in the wall from friction | Z shear | 0.10 | 6.25 | 62.50 | 3 | OK |
| 4 | 20 N on the rim (spec): tab bearing on the M3 shank from friction (one tab) | XY | 0.67 | 25.00 | 37.50 | 3 | OK |
| 5 | 20 N on the rim (spec): tab tear-out to its edge (e 4.5) | XY shear | 0.37 | 12.50 | 33.75 | 3 | OK |
| 6 | yaw-stall ring catch: ring wall bearing, R 45.2 N (compression) | XY | 1.51 | 25.00 | 16.59 | 3 | OK |
| 7 | yaw-stall ring catch: wall edgewise bending from friction 0.3R, 30 mm segment (Z, Kt 2.5) | Z | 1.13 | 12.50 | 11.06 | 3 | OK |
| 8 | yaw-stall ring catch: interlayer shear in the wall from friction | Z shear | 0.23 | 6.25 | 27.65 | 3 | OK |
| 9 | yaw-stall ring catch: tab bearing on the M3 shank from friction (one tab) | XY | 1.51 | 25.00 | 16.59 | 3 | OK |
| 10 | yaw-stall ring catch: tab tear-out to its edge (e 4.5) | XY shear | 0.84 | 12.50 | 14.93 | 3 | OK |
| 11 | hand-push 5 N ring catch: ring wall bearing, R 44.5 N (compression) | XY | 1.48 | 25.00 | 16.87 | 3 | OK |
| 12 | hand-push 5 N ring catch: wall edgewise bending from friction 0.3R, 30 mm segment (Z, Kt 2.5) | Z | 1.11 | 12.50 | 11.25 | 3 | OK |
| 13 | hand-push 5 N ring catch: interlayer shear in the wall from friction | Z shear | 0.22 | 6.25 | 28.12 | 3 | OK |
| 14 | hand-push 5 N ring catch: tab bearing on the M3 shank from friction (one tab) | XY | 1.48 | 25.00 | 16.87 | 3 | OK |
| 15 | hand-push 5 N ring catch: tab tear-out to its edge (e 4.5) | XY shear | 0.82 | 12.50 | 15.18 | 3 | OK |
| 16 | assembly: screw-head clamp 100 N on the tab, no washer (compression) | XY | 7.36 | 25.00 | 3.39 | 3 | OK |

Advisory rows (not in the verdict, reason under Assumptions):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| 50 N proof on the rim (spec 8): ring wall bearing, R 50.0 N (compression) | XY | 1.67 | 25.00 | 15.00 | 2 |
| 50 N proof on the rim (spec 8): wall edgewise bending from friction 0.3R, 30 mm segment (Z, Kt 2.5) | Z | 1.25 | 12.50 | 10.00 | 2 |
| 50 N proof on the rim (spec 8): interlayer shear in the wall from friction | Z shear | 0.25 | 6.25 | 25.00 | 2 |
| 50 N proof on the rim (spec 8): tab bearing on the M3 shank from friction (one tab) | XY | 1.67 | 25.00 | 15.00 | 2 |
| 50 N proof on the rim (spec 8): tab tear-out to its edge (e 4.5) | XY shear | 0.93 | 12.50 | 13.50 | 2 |

**lowest SF 3.39 (required 3) at: assembly: screw-head clamp 100 N on the tab, no washer (compression)**

Script notes:

```
arm model: Y horn faces shoulder 11.5, elbow 36.0, wrist 55.4, gripper 72.8; fingertip Y 74.8; masses UL 50.4 FA 37.3 GB 30.8 JW 8.5 TT 113.5 g; CG x UL 39.9 FA 35.5 GB 52.6 (z 6.8) JW 20.5
```

## Proof test (spec §8 confirmed)
Covered by the base test: 50 N on the rim at 4 positions. At 50 N every ring check is at SF 10 or above (advisory rows).
Pass criteria as in §8: no cracks in the tabs or the wall, the 1.5 mm running gap still clears, and the turntable turns
freely through ±90°.

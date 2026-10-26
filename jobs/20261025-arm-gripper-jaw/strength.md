VERDICT: NEEDS_TEST

# Strength check: 20261025-arm-gripper-jaw (round 2)

strength-analyst · 2026-10-26 · `python3 strength_calc.py` reads model.py, tools/hobby_parts.py and geometry.json

Every check is at SF 4.08 or above. The lowest is out-of-plane bending over the horn pocket at x 8 under the
yaw-stall sweep.

## Round 1 → round 2

| | Round 1 | Round 2 |
|---|---|---|
| Verdict / lowest SF | FAIL / 0.91 | NEEDS_TEST / 4.08 |
| Gripper-horn joint, yaw stall | 1.45 | 10.95 (clamped) |
| Out-of-plane bending x8 | 0.91 | 4.08 (T 8, bar 14 wide) |

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

The jaw's out-of-plane load is the fingertip force at its tip, 55 mm from the gripper axis: up to 381 N·mm (yaw stall)
or 275 N·mm (hand push) at the horn. Grip in plane: 2.9 N at the tip or 10.7 N at r 15.

## Assumptions

- Sections at x 8 and x 16.5 are computed from the parameters and match the CAD (468/469 and 597/596 mm⁴).
- **Clamped horn joints (new).** The centre screw (M3×16 + DIN 9021 Ø9 washer on the MG996R joints, M2×12 + Ø6 washer
  on the SG90 joints) clamps link and horn onto the spline. Capacity = washer pull-through (π·D_washer·floor) plus the
  anti-rotation arm screws (M2, Ø1.6 pilot, about 5 mm engaged), both against the interlayer shear allowable. Levers:
  MG996R transverse 17.5 (washer) / 32.5 (arm screw at r 15), torsion 5.5 (hub radius); SG90 weak direction 3.6
  (washer) / 10.6 (arm screw at r 7), torsion 3.6. Utilisation per pose = M_t/cap_t + T/cap_T, worst over the sweep.
  The clamp screw's thread in the spline (metal on the MG996R, plastic on the SG90) is bought hardware and is left to
  the proof test.
- Pull-out: τ = F/(π·d_pilot·L), with the printed pilot sizes (MG996R 2.6, SG90 1.5) and the real screw engagement
  (MG996R tab screws about 7 mm, SG90 bag tab screws about 5 mm; screws can't engage more than their own length).
- Bearing and tear-out at vertical pilots in flat plates are in-plane. Tear-out from horizontal holes in vertical walls
  shears the layers. Combined moments are added (conservative).
- Advisory "rails alone" rows: the servo case (bolted across its window at both tab rows, about 40 x stiffer than the
  rails) carries the out-of-plane moment between the tab rows. The verdict rows check the tab screws that make that
  path work.

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
| 1 | gripper stall 160 N.mm: horn-pocket wall bearing | XY | 1.42 | 25.00 | 17.63 | 3 | OK |
| 2 | gripper stall: bar in-plane bending x8 over the pocket (Kt 2.5) | XY | 1.34 | 25.00 | 18.70 | 3 | OK |
| 3 | gripper stall: bar in-plane bending x16.5 pocket tip (Kt 1.5) | XY | 0.64 | 25.00 | 38.89 | 3 | OK |
| 4 | yaw-stall sweep: clamped gripper-horn joint (D6 washer + arm screw, floor 6) | Z shear | 0.57 | 6.25 | 10.95 | 3 | OK |
| 5 | yaw-stall sweep: out-of-plane bending x8 over the pocket (Kt 2 arm-screw hole) | XY | 6.13 | 25.00 | 4.08 | 3 | OK |
| 6 | yaw-stall sweep: out-of-plane bending x16.5 at the pocket tip (Kt 1.5) | XY | 2.72 | 25.00 | 9.18 | 3 | OK |
| 7 | hand push 5 N: clamped gripper-horn joint (D6 washer + arm screw, floor 6) | Z shear | 0.41 | 6.25 | 15.31 | 3 | OK |
| 8 | hand push 5 N: out-of-plane bending x8 over the pocket (Kt 2 arm-screw hole) | XY | 4.39 | 25.00 | 5.69 | 3 | OK |
| 9 | hand push 5 N: out-of-plane bending x16.5 at the pocket tip (Kt 1.5) | XY | 1.93 | 25.00 | 12.93 | 3 | OK |

Advisory rows (not in the verdict, reason under Assumptions):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| proof 5 N at the tip: bar in-plane bending x8 (Kt 2.5) | XY | 2.30 | 25.00 | 10.88 | 2 |

**lowest SF 4.08 (required 3) at: yaw-stall sweep: out-of-plane bending x8 over the pocket (Kt 2 arm-screw hole)**

Script notes:

```
arm model: Y horn faces shoulder 11.5, elbow 36.0, wrist 55.4, gripper 72.8; fingertip Y 74.8; masses UL 50.4 FA 37.3 GB 30.8 JW 8.5 TT 113.5 g; CG x UL 39.9 FA 35.5 GB 52.6 (z 6.8) JW 20.5
jaw_oop x8 468 (CAD 469), x16.5 597 (CAD 596)
yaw  sweep: horn T=3 Mt=381; x8 T=3 Mt=328; x16 T=3 Mt=271
hand sweep: horn T=0 Mt=275; x8 T=0 Mt=235; x16 T=0 Mt=193
```

## Proof test (spec §8 confirmed)
The gripper-base squeeze test plus 7.5 N sideways at the jaw tip (1.5 x the hand push). Keep it.

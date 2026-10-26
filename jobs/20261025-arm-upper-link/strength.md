VERDICT: NEEDS_TEST

# Strength check: 20261025-arm-upper-link (round 2)

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
- Weight beyond the shoulder horn, arm straight and horizontal: 625 N·mm in-plane (was 415, now 63 % of stall),
  186 out-of-plane (was 74).

Changes:

- **Lowest SF 3.94 → 3.90**, now out-of-plane bending at x 15 over the pocket under the yaw-stall sweep (transverse
  moment 1551 → 1610 N·mm). Plate torsion, the round-2 lowest, goes 3.94 → 4.11 (torsion 1465 → 1403).
- Other yaw-stall rows: elbow pilot row 4.73 → 4.56, x 30 9.70 → 9.34, shoulder-horn joint 5.80 → 5.95, elbow tab
  screws 6.57 → 6.95.
- Hand-push rows rise 7–11 % (x 15 4.65 → 5.00, torsion 6.24 → 6.95, joint 8.42 → 9.22).
- Weight ×2 rows (SF 4 required): the lowest is now 15.93 (elbow pilot row, was 40.23).
- Advisory "rails alone" rows: 1.83 → 1.76 (yaw), 2.08 → 2.28 (hand).
- Proof test (2) still loads at least 1.5 × the hand push: 21 N at the elbow axis is 1.6 × the new transverse moment at
  the horn, and 7.5 N on 185 mm is 1.67 × the new torsion.

**Verdict unchanged: NEEDS_TEST.**

**Advisory, not in this job's load cases.** The claw and camera-mount specs add a 10 N tug on the Brio's USB cable at
the camera. Applied at either end of the camera in any direction, and scaled down wherever a servo would backdrive (as
in the yaw sweep), it gives a transverse moment of 2489 N·mm at x 15 and a torsion of 1764 N·mm. The SFs are then: x 15
2.52, elbow pilot row 2.89, plate torsion 3.27, shoulder-horn joint 4.49. That is below 3, so this verdict holds only if
a snag cannot pull on the camera: tie the cable along each link with a slack loop at each joint, and anchor it at the
base. To design the arm for the tug instead, this part needs another round.

## Round 2 summary

Every check is at SF 3.94 or above. The lowest is plate torsion under the yaw-stall sweep (1465 N·mm), conservatively
taken as interlayer shear.

## Round 1 → round 2

| | Round 1 | Round 2 |
|---|---|---|
| Verdict / lowest SF | FAIL / 0.58 (slot torsion, yaw stall) | NEEDS_TEST / 3.94 (full-width torsion, yaw stall) |
| Shoulder-horn joint, yaw stall | 0.76 (2 M2 screws, 4 mm floor) | 5.80 (clamped, 8 mm floor) |
| Out-of-plane bending over the pocket | 1.27 | 4.05 |
| Lightening slot | 0.91 bending / 0.58 torsion | removed |
| Mass | 27 g | 50 g (shoulder static 415 N·mm, 41 % of stall) |

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

At the shoulder horn the yaw sweep gives up to 1641 N·mm transverse and 1465 N·mm torsion; the hand push gives 1425
and 925. Build direction: printed flat (front face down), so bending in either plane runs along the layers. Screw and
washer pull-out shear the layers, and plate torsion is conservatively taken as interlayer shear.

## Assumptions

- Plate sections (over the pocket at x 15, full section, elbow pilot row at x 65.6, window) are computed from the
  parameters and match the CAD (out-of-plane I 2597 / 2830 / 2363 / 1138 mm⁴).
- Elbow pilots: the ligament from pilot to window is 2.2 mm in CAD (the pilot prints at Ø2.6).
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

Round-2 values. The script now prints the round-4 values; the rows that changed are listed under Round 4 at the top.

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | shoulder stall 1000 N.mm: horn-pocket wall bearing | XY | 2.82 | 25.00 | 8.88 | 3 | OK |
| 2 | stall 1000 N.mm: in-plane bending, full section x30 | XY | 0.52 | 25.00 | 48.17 | 3 | OK |
| 3 | stall: in-plane bending at the elbow MG996R window, M 1000 (Kt 2.5) | XY | 1.65 | 25.00 | 15.17 | 3 | OK |
| 4 | weight x2 (sustained): in-plane bending, full section | XY | 0.43 | 25.00 | 58.10 | 4 | OK |
| 5 | elbow MG996R stall: tab-pilot bearing | XY | 0.47 | 25.00 | 53.56 | 3 | OK |
| 6 | elbow MG996R stall: pilot-to-window ligament 2.20 tear-out (full F toward the window) | XY shear | 0.28 | 12.50 | 45.32 | 3 | OK |
| 7 | weight x2 (sustained): clamped shoulder-horn joint (torsion) | Z shear | 0.10 | 6.25 | 64.62 | 4 | OK |
| 8 | yaw-stall sweep: clamped shoulder-horn joint (D9 washer + arm screws, floor 8) | Z shear | 1.08 | 6.25 | 5.80 | 3 | OK |
| 9 | hand push 5 N: clamped shoulder-horn joint (D9 washer + arm screws, floor 8) | Z shear | 0.74 | 6.25 | 8.42 | 3 | OK |
| 10 | weight x2 (sustained): out-of-plane bending x15 over the pocket (Kt 2 arm-screw hole) | XY | 0.59 | 25.00 | 42.66 | 4 | OK |
| 11 | weight x2 (sustained): out-of-plane bending x30, full section | XY | 0.26 | 25.00 | 96.33 | 4 | OK |
| 12 | weight x2 (sustained): out-of-plane bending at the elbow MG996R pilot row x65.6 (Kt 2) | XY | 0.62 | 25.00 | 40.23 | 4 | OK |
| 13 | yaw-stall sweep: out-of-plane bending x15 over the pocket (Kt 2 arm-screw hole) | XY | 6.18 | 25.00 | 4.05 | 3 | OK |
| 14 | yaw-stall sweep: out-of-plane bending x30, full section | XY | 2.58 | 25.00 | 9.70 | 3 | OK |
| 15 | yaw-stall sweep: out-of-plane bending at the elbow MG996R pilot row x65.6 (Kt 2) | XY | 5.29 | 25.00 | 4.73 | 3 | OK |
| 16 | yaw-stall sweep: plate torsion, full width (Z shear) | Z shear | 1.59 | 6.25 | 3.94 | 3 | OK |
| 17 | yaw-stall sweep: elbow MG996R tab screws pull-out (L 7) | Z shear | 0.95 | 6.25 | 6.57 | 3 | OK |
| 18 | hand push 5 N: out-of-plane bending x15 over the pocket (Kt 2 arm-screw hole) | XY | 5.38 | 25.00 | 4.65 | 3 | OK |
| 19 | hand push 5 N: out-of-plane bending x30, full section | XY | 2.25 | 25.00 | 11.11 | 3 | OK |
| 20 | hand push 5 N: out-of-plane bending at the elbow MG996R pilot row x65.6 (Kt 2) | XY | 4.64 | 25.00 | 5.39 | 3 | OK |
| 21 | hand push 5 N: plate torsion, full width (Z shear) | Z shear | 1.00 | 6.25 | 6.24 | 3 | OK |
| 22 | hand push 5 N: elbow MG996R tab screws pull-out (L 7) | Z shear | 0.57 | 6.25 | 10.98 | 3 | OK |

Advisory rows (not in the verdict, reason under Assumptions):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| yaw-stall sweep: elbow MG996R window rails alone, servo case ignored (Kt 2.5) | XY | 13.70 | 25.00 | 1.83 | 3 |
| hand push 5 N: elbow MG996R window rails alone, servo case ignored (Kt 2.5) | XY | 12.01 | 25.00 | 2.08 | 3 |

**lowest SF 3.94 (required 3) at: yaw-stall sweep: plate torsion, full width (Z shear)**

Script notes:

```
arm model: Y horn faces shoulder 11.5, elbow 36.0, wrist 55.4, gripper 72.8; fingertip Y 74.8; masses UL 50.4 FA 37.3 GB 30.8 JW 8.5 TT 113.5 g; CG x UL 39.9 FA 35.5 GB 52.6 (z 6.8) JW 20.5
yaw  sweep: horn T=1465 Mt=1641; x15 T=1465 Mt=1551; x30 T=1465 Mt=1460; row T=1465 Mt=1251; far T=1465 Mt=1094
hand sweep: horn T=925 Mt=1425; x15 T=925 Mt=1350; x30 T=925 Mt=1275; row T=925 Mt=1097; far T=925 Mt=925
weight beyond the shoulder horn: in-plane 415 N.mm (arm straight, horizontal), out-of-plane 74
sections: oop I x15 2596, full 2833, pilot row 2367, window 1142 (CAD x15 2597, x30 2830, x65.6 2363, window 1138)
```

## Proof test (spec §8 confirmed)
(1) Horn in a vice, 1 kg at the elbow axis, deflection < 2 mm. (2) 21 N sideways at the elbow axis, 1.5 x the
hand-push moment at the horn, then 7.5 N on a 185 mm lever, 1.5 x the hand-push torsion. Both are right for the
clamped joint. Clamp with the M3×16 screw and washer as built.

VERDICT: NEEDS_TEST

# Strength check: 20261025-arm-forearm (round 3)

strength-analyst · 2026-10-26 · `python3 strength_calc.py` reads model.py, tools/hobby_parts.py and geometry.json

## Round 4 (claw v2 + Brio, 2026-10-26)

The end effector is now the claw v2 with a Logitech Brio (jobs `20261026-arm-claw-frame`, `-cover`, `-pinion`, `-jaw`
×2 and `20261026-arm-camera-mount`). `strength_calc.py` reads it from those jobs: the layout from `claw_frame.py`, the
masses from their `geometry.json`, and their measured CoGs (it warns if a claw part's volume changes). Everything else
is as in round 3.

- 172 g beyond the wrist horn, CoG 8.3 mm in front of the wrist axis and 39.5 mm outboard of the claw's back face. The
  Brio's CoG is at world Y 117.6.
- Fingertip 76.15 mm from the wrist axis (was ≈95), at world Y 75.9 (was 74.8). 50 g payload at the fingertip, as
  before.
- Weight beyond the elbow horn, arm straight and horizontal: 275 N·mm in-plane (was 186), 117 out-of-plane (was 34).
- **Wrist servo SG90 → MG90S** (216 N·mm stall, was 160). `tools/hobby_parts.py` gives the MG90S the SG90 body, so the
  window and pilots are as reviewed. This job's `model.py` and spec still say SG90: rename them, and read the proof
  test's pass criterion as "the MG90S tabs don't lift".

Changes:

- **Lowest SF 3.28 → 3.78**, still the wrist tab screws under the yaw-stall sweep. The shorter claw lowers the moments at
  the wrist end (torsion 892 → 749 N·mm).
- Other yaw-stall rows: x 15 3.72 → 3.90, plate torsion 4.60 → 5.48, wrist pilot row 5.84 → 6.19, elbow-horn joint
  8.13 → 9.27.
- Wrist-stall rows with the MG90S's 216 N·mm: pilot bearing 54.02 → 40.01, ligament tear-out 64.82 → 48.02. Window
  bending (M 603 → 558) goes 16.55 → 17.89.
- Weight ×2 rows (SF 4 required): the lowest is now 19.76 (x 15, was 67.41). The claw + camera ligament row goes
  149.61 → 84.02.
- Hand-push rows rise 12–25 %. Advisory "rails alone" rows: 2.57 → 2.73 (yaw), 3.91 → 4.68 (hand). The stock bag
  screws (≈5 mm engaged) would now give 1.99, still below 3, so keep the M2×12.
- Proof test (2): 7.5 N on the 95 mm lever (≈710 N·mm) is now 0.95 × the yaw-stall torsion (was 0.8 ×).

**Verdict unchanged: NEEDS_TEST.**

**Advisory, not in this job's load cases.** The claw and camera-mount specs add a 10 N tug on the Brio's USB cable at
the camera. Applied at either end of the camera in any direction, and scaled down wherever a servo would backdrive (as
in the yaw sweep), it gives a lowest SF of 3.07 here (x 15), with the wrist tab screws at 3.20. The forearm covers it.
The base, turntable and upper link do not (their lowest SFs are 2.27 to 2.80), so tie the cable along each link with a slack loop at each
joint, and anchor it at the base.

## Round 3 summary

Round 3: the wrist SG90 is now fixed with 2 × M2×12 self-tapping screws (spec §2, BUILD_GUIDE), engaging 9.5 mm in
the 10 mm forearm. The last failing check, tab-screw pull-out under the yaw-stall sweep, moves from SF 1.73 to
**3.28**, which is now the lowest SF. Everything else is at SF 3.72 or above. With the stock bag screws (~5 mm
engaged) it would still be 1.73; the script prints that for reference.

## Round 1 → round 2 → round 3

| | Round 1 | Round 2 |
|---|---|---|
| Verdict / lowest SF | FAIL / 0.42 (slot torsion) | FAIL / 1.73 (wrist SG90 tab screws, yaw stall) |
| Elbow-horn joint, yaw stall | 0.79 | 8.13 (clamped, 8 mm floor) |
| Out-of-plane bending over the pocket | 0.80 | 3.72 |
| Lightening slot | 0.56 / 0.42 | removed |
| Wrist SG90 tab screws, yaw stall | 1.93 (Ø1.8, L 5) | 1.73 (printed pilot now Ø1.5, L 5 — the bag screw's limit) |
| Pilot-to-window ligament | 1.55 | 1.80 printed (end clearance 0.2), SF 46 |

**Round 2 → round 3:** wrist tab screws are now M2×12 (engaged 9.5 mm): yaw-stall pull-out 1.73 → 3.28, hand push
3.42 → 6.49. Verdict FAIL → NEEDS_TEST.

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

At the elbow horn the yaw sweep gives up to 1336 N·mm transverse and 892 N·mm torsion; the hand push gives 925 and
475. At the wrist servo, the tab screws take the transverse moment over the 27.8 mm row spacing plus the forearm
torsion over the 6 mm tab half-width (both screws in tension).

## Assumptions

- Plate sections (x 15, full section, wrist pilot row at x 70.75, window) are computed from the parameters and match
  the CAD (out-of-plane I 1927 / 2163 / 2021 / 1113 mm⁴).
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

Round-3 values. The script now prints the round-4 values; the rows that changed are listed under Round 4 at the top.

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | elbow stall 1000 N.mm: horn-pocket wall bearing | XY | 2.82 | 25.00 | 8.88 | 3 | OK |
| 2 | stall 1000 N.mm: in-plane bending, full section x30 | XY | 0.89 | 25.00 | 28.17 | 3 | OK |
| 3 | stall: in-plane bending at the wrist SG90 window, M 603 (Kt 2.5) | XY | 1.51 | 25.00 | 16.55 | 3 | OK |
| 4 | weight x2 (sustained): in-plane bending, full section | XY | 0.33 | 25.00 | 75.81 | 4 | OK |
| 5 | wrist SG90 stall: tab-pilot bearing | XY | 0.46 | 25.00 | 54.02 | 3 | OK |
| 6 | wrist SG90 stall: pilot-to-window ligament 1.80 tear-out (full F toward the window) | XY shear | 0.19 | 12.50 | 64.82 | 3 | OK |
| 7 | weight x2 (sustained): clamped elbow-horn joint (torsion) | Z shear | 0.04 | 6.25 | 139.10 | 4 | OK |
| 8 | yaw-stall sweep: clamped elbow-horn joint (D9 washer + arm screws, floor 8) | Z shear | 0.77 | 6.25 | 8.13 | 3 | OK |
| 9 | hand push 5 N: clamped elbow-horn joint (D9 washer + arm screws, floor 8) | Z shear | 0.42 | 6.25 | 14.82 | 3 | OK |
| 10 | weight x2 (sustained): out-of-plane bending x15 over the pocket (Kt 2 arm-screw hole) | XY | 0.37 | 25.00 | 67.41 | 4 | OK |
| 11 | weight x2 (sustained): out-of-plane bending x30, full section | XY | 0.16 | 25.00 | 158.57 | 4 | OK |
| 12 | weight x2 (sustained): out-of-plane bending at the wrist SG90 pilot row x70.8 (Kt 2) | XY | 0.34 | 25.00 | 74.10 | 4 | OK |
| 13 | yaw-stall sweep: out-of-plane bending x15 over the pocket (Kt 2 arm-screw hole) | XY | 6.71 | 25.00 | 3.72 | 3 | OK |
| 14 | yaw-stall sweep: out-of-plane bending x30, full section | XY | 2.62 | 25.00 | 9.53 | 3 | OK |
| 15 | yaw-stall sweep: out-of-plane bending at the wrist SG90 pilot row x70.8 (Kt 2) | XY | 4.28 | 25.00 | 5.84 | 3 | OK |
| 16 | yaw-stall sweep: plate torsion, full width (Z shear) | Z shear | 1.36 | 6.25 | 4.60 | 3 | OK |
| 17 | yaw-stall sweep: wrist SG90 tab screws pull-out (L 9.5) | Z shear | 1.90 | 6.25 | 3.28 | 3 | OK |
| 18 | hand push 5 N: out-of-plane bending x15 over the pocket (Kt 2 arm-screw hole) | XY | 4.61 | 25.00 | 5.42 | 3 | OK |
| 19 | hand push 5 N: out-of-plane bending x30, full section | XY | 1.79 | 25.00 | 13.98 | 3 | OK |
| 20 | hand push 5 N: out-of-plane bending at the wrist SG90 pilot row x70.8 (Kt 2) | XY | 2.82 | 25.00 | 8.86 | 3 | OK |
| 21 | hand push 5 N: plate torsion, full width (Z shear) | Z shear | 0.72 | 6.25 | 8.64 | 3 | OK |
| 22 | hand push 5 N: wrist SG90 tab screws pull-out (L 9.5) | Z shear | 0.96 | 6.25 | 6.49 | 3 | OK |
| 23 | gripper weight x2 + 1 N along x: SG90 pilot ligament tear-out | XY shear | 0.08 | 12.50 | 149.61 | 3 | OK |

Advisory rows (not in the verdict, reason under Assumptions):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| yaw-stall sweep: wrist SG90 window rails alone, servo case ignored (Kt 2.5) | XY | 9.71 | 25.00 | 2.57 | 3 |
| hand push 5 N: wrist SG90 window rails alone, servo case ignored (Kt 2.5) | XY | 6.39 | 25.00 | 3.91 | 3 |

**lowest SF 3.28 (required 3) at: yaw-stall sweep: wrist SG90 tab screws pull-out (L 9.5)**

Script notes:

```
arm model: Y horn faces shoulder 11.5, elbow 36.0, wrist 55.4, gripper 72.8; fingertip Y 74.8; masses UL 50.4 FA 37.3 GB 30.8 JW 8.5 TT 113.5 g; CG x UL 39.9 FA 35.5 GB 52.6 (z 6.8) JW 20.5
yaw  sweep: horn T=892 Mt=1336; x15 T=892 Mt=1236; x30 T=892 Mt=1137; row T=892 Mt=868; far T=892 Mt=740
hand sweep: horn T=475 Mt=925; x15 T=475 Mt=850; x30 T=475 Mt=775; row T=475 Mt=571; far T=475 Mt=475
weight beyond the elbow horn: in-plane 186 N.mm (arm straight, horizontal), out-of-plane 34
sections: oop I x15 1926, full 2167, pilot row 2025, window 1117 (CAD x15 1927, x30 2163, x70.75 2021, window 1113)
```

## Proof test (spec §8 confirmed)
(1) 1 kg at the wrist axis with the elbow horn clamped. (2) 15 N sideways at the wrist axis, then 7.5 N on a 95 mm
lever on the wrist tab holes (≈710 N·mm of torsion, about 0.8 x the yaw-stall torsion), **run with the M2×12 screws
fitted**; pass includes "SG90 tabs don't lift". That is the test this fix needs. Keep it as written.

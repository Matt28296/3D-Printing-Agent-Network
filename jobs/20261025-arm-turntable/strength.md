VERDICT: NEEDS_TEST

# Strength check: 20261025-arm-turntable (round 3)

strength-analyst · 2026-10-26 · `python3 strength_calc.py` reads model.py, tools/hobby_parts.py and geometry.json

## Round 4 (claw v2 + Brio, 2026-10-26)

The end effector is now the claw v2 with a Logitech Brio (jobs `20261026-arm-claw-frame`, `-cover`, `-pinion`, `-jaw`
×2 and `20261026-arm-camera-mount`). `strength_calc.py` reads it from those jobs: the layout from `claw_frame.py`, the
masses from their `geometry.json`, and their measured CoGs (it warns if a claw part's volume changes). Everything else
is as in round 3.

- 172 g beyond the wrist horn, CoG 8.3 mm in front of the wrist axis and 39.5 mm outboard of the claw's back face. The
  Brio's CoG is at world Y 117.6.
- Fingertip 76.15 mm from the wrist axis (was ≈95), at world Y 75.9 (was 74.8). Wrist servo MG90S, 216 N·mm stall (was
  SG90, 160). 50 g payload at the fingertip, as before.
- Arm straight and horizontal: shoulder 625 N·mm (was 415), elbow 275 (was 186), about the yaw axis 665 (was 442).

Changes:

- **Lowest SF 4.36 → 4.29**, now the lower tab-pilot row (front face) under the yaw-stall sweep. In round 3 it was the
  same section under the hand push.
- Yaw-stall rows drop 2–3 % (upright-root M_x 1603 → 1645 N·mm): lower tab-pilot row 4.43 → 4.29, gusset toe
  4.55 → 4.45, window bottom 4.66 → 4.52, disk 5.26 → 5.14, base-horn joint 4.43 → 4.34.
- Hand-push rows rise 6–7 % (root M_x 1590 → 1496): lower tab-pilot row 4.36 → 4.66, window bottom 4.61 → 4.92.
- Weight ×2 rows (SF 4 required) about halve and stay at 10.9 or more: lower tab-pilot row 22.91 → 11.30, base-horn
  joint 19.99 → 10.92, gusset toe 30.31 → 14.94, disk 45.35 → 19.71.
- Shoulder stall on the desk, M_y 1158 → 1171: rows 4–5 drop 1 %. The proof advisory row (1 kg at the elbow, base-horn
  joint) goes 19.60 → 17.10.

**Verdict unchanged: NEEDS_TEST.** The §8 proof test still applies.

**Advisory, not in this job's load cases.** The claw and camera-mount specs add a 10 N tug on the Brio's USB cable at
the camera. Applied at either end of the camera in any direction, and scaled down wherever a servo would backdrive (as
in the yaw sweep), it gives M_x 3020 N·mm at the upright root (yaw sweep: 1645). The SFs are then: lower tab-pilot row
2.27, window bottom 2.41, gusset toe 2.57, base-horn joint 2.69, disk 2.87. That is below 3, so this verdict holds only
if a snag cannot pull on the camera: tie the cable along each link with a slack loop at each joint, and anchor it at the
base. To design the arm for the tug instead, this part needs another round.

## Round 3 summary

Round 3: the front root wedge now stops at |X| ≥ 6 (WASHER_CLEAR_X), so the Ø9 clamp washer seats flat and the
clamped base-horn joint gets its full capacity. Every check is at SF 4.36 or above; the lowest is the lower tab-pilot
row of the upright under the 5 N hand push. No open fit or strength items.

## Round 1 → round 2 → round 3

| | Round 1 | Round 2 |
|---|---|---|
| Verdict / lowest SF | FAIL / 0.42 (base-horn arm screws, yaw stall) | NEEDS_TEST / 4.36 (lower tab-pilot row, hand push) |
| Base-horn joint, yaw stall | 0.42 (2 M2 screws in a 3 mm floor) | 4.43 (clamped, 8 mm floor, no pocket) |
| Disk at the upright front | 1.41 | 5.26 (t 8, root wedge) |
| Lower tab-pilot row, front face | 1.74 | 4.43 yaw / 4.36 hand (UP_T 7, 70 mm gussets with a 23 mm run) |
| Window corner | 2.29 | 4.66 |
| Base-yaw torque into the disk | slot walls | no pocket: 2 arm screws in bearing, SF 6.0 with friction ignored |

**Round 2 → round 3:** the front wedge is split at |X| < 6. The washer clash is gone (script FIT line: clear). The
12 mm gap leaves a sharp root corner, already checked with Kt 2.5 (rows "at the washer gap", SF ≥ 10.6). Volume
89389 → 89336 mm³; no SF changed.

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

Build direction: the disk prints on the bed and the upright stands vertical. All upright bending puts stress along Z,
across the layers; upright torsion shears the layers; disk bending runs along them.

## Assumptions

- Upright sections (above the wedge at Z 28, window bottom Z 51, lower tab-pilot row Z 56) are computed from the
  parameters and match the CAD sections (I_xx 35227 / 10448 / 7507 mm⁴).
- Root wedges (3 mm, 45°): checked just above the wedge with Kt 2.0. The front wedge stops at |X| < 6 around the
  clamp washer; that stretch has a sharp corner (rows "at the washer gap", Kt 2.5).
- Shoulder-servo M_x enters the upright as a couple between the tab screws and the opposite tab edge (lever 14.85).
- Disk: the full M_x crosses the disk at the upright's front face, b_eff 66, Kt 2.0.
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
| 1 | base stall 1000 N.mm: arm-screw bearing in the disk (no pocket, friction ignored, L 5) | XY | 4.17 | 25.00 | 6.00 | 3 | OK |
| 2 | yaw stall: upright torsion above the wedges (open section) | Z shear | 0.88 | 6.25 | 7.07 | 3 | OK |
| 3 | yaw stall: window ligament pair, toe | Z | 0.46 | 12.50 | 26.92 | 3 | OK |
| 4 | shoulder stall on desk: upright in-plane bending, root (Kt 2.0) | Z | 0.23 | 12.50 | 54.25 | 3 | OK |
| 5 | shoulder stall on desk: upright in-plane bending, window (Kt 2.5) | Z | 0.46 | 12.50 | 27.45 | 3 | OK |
| 6 | yaw sweep: upright in-plane bending, root (Kt 2.0) | Z | 0.27 | 12.50 | 45.98 | 3 | OK |
| 7 | yaw sweep: upright in-plane bending, window (Kt 2.5) | Z | 0.54 | 12.50 | 23.27 | 3 | OK |
| 8 | weight x2 (sustained): upright root above the wedge, front (Kt 2.0) | Z | 0.12 | 12.50 | 108.62 | 4 | OK |
| 9 | weight x2 (sustained): upright root, front, at the washer gap |X|<6 (no wedge, Kt 2.5) | Z | 0.14 | 12.50 | 86.90 | 4 | OK |
| 10 | weight x2 (sustained): upright root, gusset toe (Kt 2.5) | Z | 0.41 | 12.50 | 30.31 | 4 | OK |
| 11 | weight x2 (sustained): window bottom, front face (Kt 2.5) | Z | 0.51 | 12.50 | 24.55 | 4 | OK |
| 12 | weight x2 (sustained): window bottom, gusset toe | Z | 0.36 | 12.50 | 35.04 | 4 | OK |
| 13 | weight x2 (sustained): lower tab-pilot row, front face (Kt 2 hole) | Z | 0.55 | 12.50 | 22.91 | 4 | OK |
| 14 | weight x2 (sustained): lower tab-pilot row, gusset toe | Z | 0.28 | 12.50 | 44.39 | 4 | OK |
| 15 | weight x2 (sustained): shoulder tab screws pull-out (2 screws, L 7) | Z shear | 0.16 | 6.25 | 38.40 | 4 | OK |
| 16 | weight x2 (sustained): disk at the upright front, b 66 t 8 (Kt 2.0) | XY | 0.55 | 25.00 | 45.35 | 4 | OK |
| 17 | yaw-stall sweep: upright root above the wedge, front (Kt 2.0) | Z | 0.94 | 12.50 | 13.25 | 3 | OK |
| 18 | yaw-stall sweep: upright root, front, at the washer gap |X|<6 (no wedge, Kt 2.5) | Z | 1.18 | 12.50 | 10.60 | 3 | OK |
| 19 | yaw-stall sweep: upright root, gusset toe (Kt 2.5) | Z | 2.75 | 12.50 | 4.55 | 3 | OK |
| 20 | yaw-stall sweep: window bottom, front face (Kt 2.5) | Z | 2.68 | 12.50 | 4.66 | 3 | OK |
| 21 | yaw-stall sweep: window bottom, gusset toe | Z | 1.88 | 12.50 | 6.65 | 3 | OK |
| 22 | yaw-stall sweep: lower tab-pilot row, front face (Kt 2 hole) | Z | 2.82 | 12.50 | 4.43 | 3 | OK |
| 23 | yaw-stall sweep: lower tab-pilot row, gusset toe | Z | 1.48 | 12.50 | 8.43 | 3 | OK |
| 24 | yaw-stall sweep: shoulder tab screws pull-out (2 screws, L 7) | Z shear | 0.86 | 6.25 | 7.29 | 3 | OK |
| 25 | yaw-stall sweep: disk at the upright front, b 66 t 8 (Kt 2.0) | XY | 4.75 | 25.00 | 5.26 | 3 | OK |
| 26 | hand push 5 N: upright root above the wedge, front (Kt 2.0) | Z | 0.67 | 12.50 | 18.77 | 3 | OK |
| 27 | hand push 5 N: upright root, front, at the washer gap |X|<6 (no wedge, Kt 2.5) | Z | 0.83 | 12.50 | 15.02 | 3 | OK |
| 28 | hand push 5 N: upright root, gusset toe (Kt 2.5) | Z | 2.39 | 12.50 | 5.24 | 3 | OK |
| 29 | hand push 5 N: window bottom, front face (Kt 2.5) | Z | 2.71 | 12.50 | 4.61 | 3 | OK |
| 30 | hand push 5 N: window bottom, gusset toe | Z | 1.90 | 12.50 | 6.57 | 3 | OK |
| 31 | hand push 5 N: lower tab-pilot row, front face (Kt 2 hole) | Z | 2.87 | 12.50 | 4.36 | 3 | OK |
| 32 | hand push 5 N: lower tab-pilot row, gusset toe | Z | 1.50 | 12.50 | 8.33 | 3 | OK |
| 33 | hand push 5 N: shoulder tab screws pull-out (2 screws, L 7) | Z shear | 0.87 | 6.25 | 7.20 | 3 | OK |
| 34 | hand push 5 N: disk at the upright front, b 66 t 8 (Kt 2.0) | XY | 4.67 | 25.00 | 5.35 | 3 | OK |
| 35 | shoulder stall: tab-pilot bearing (compression) | XY | 0.67 | 25.00 | 37.49 | 3 | OK |
| 36 | shoulder stall: pilot-to-window ligament 2.20 tear-out | Z shear | 0.39 | 6.25 | 15.86 | 3 | OK |
| 37 | weight x2 (sustained): clamped base-horn joint (washer D9 + 2 arm screws, floor 8) | Z shear | 0.31 | 6.25 | 19.99 | 4 | OK |
| 38 | shoulder stall on desk: clamped base-horn joint (washer D9 + 2 arm screws, floor 8) | Z shear | 0.24 | 6.25 | 25.77 | 3 | OK |
| 39 | yaw-stall sweep: clamped base-horn joint (washer D9 + 2 arm screws, floor 8) | Z shear | 1.41 | 6.25 | 4.43 | 3 | OK |
| 40 | hand push 5 N: clamped base-horn joint (washer D9 + 2 arm screws, floor 8) | Z shear | 1.08 | 6.25 | 5.78 | 3 | OK |

Advisory rows (not in the verdict, reason under Assumptions):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| proof test (1 kg at the elbow): clamped base-horn joint | Z shear | 0.32 | 6.25 | 19.60 | 1 |

**lowest SF 4.36 (required 3) at: hand push 5 N: lower tab-pilot row, front face (Kt 2 hole)**

Script notes:

```
arm model: Y horn faces shoulder 11.5, elbow 36.0, wrist 55.4, gripper 72.8; fingertip Y 74.8; masses UL 50.4 FA 37.3 GB 30.8 JW 8.5 TT 113.5 g; CG x UL 39.9 FA 35.5 GB 52.6 (z 6.8) JW 20.5
section Z=28.0: A=636.8 Ixx=35229 (CAD 35227) ybar=-12.46 c_front=7.46 c_toe=21.39
section Z=51.0: A=287.2 Ixx=10454 (CAD 10448) ybar=-12.74 c_front=7.74 c_toe=13.55
section Z=56.0: A=237.5 Ixx=7512 (CAD 7507) ybar=-12.69 c_front=7.69 c_toe=11.96
M_y shoulder stall on desk 1158; arm weight about the yaw axis 442 static; proof 1 kg at elbow 1522 N.mm
yaw  sweep: root Mx=1603 My=1367 Mz=1114; wb Mx=1456 My=1107 Mz=1116; pr Mx=1426 My=1056 Mz=1116; disk Mx=1673 My=1489 Mz=1000
hand sweep: root Mx=1590 My=0 Mz=1000; wb Mx=1473 My=0 Mz=1000; pr Mx=1450 My=0 Mz=1000; disk Mx=1645 My=0 Mz=1000
ring catch force if the disk rocks onto the ring: 45.2 N
FIT: clamp washer D9 (r 4.5) vs front-wedge gap |X| < 6.0 -> clear, seats flat
```

## Proof test (spec §8 confirmed)
(1) 1 kg at the elbow axis: base-horn joint SF 19.6 at that load (advisory). (2) 10 N sideways at the fingertip, arm
up, then with the elbow at 90°: 2 x the hand push and 1.2 x the largest out-of-plane yaw-stall force. Keep both.

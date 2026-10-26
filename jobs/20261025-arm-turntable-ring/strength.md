VERDICT: NEEDS_TEST

# Strength check: 20261025-arm-turntable-ring (links round 5, independent re-check of the round-5 solid)

strength-analyst (independent review: I did not design this part) · 2026-10-26 ·
`python3 jobs/20261025-arm-turntable-ring/strength_calc.py` from the project root (about 10 s). It reads every link's
`model.py`, `tools/hobby_parts.py`, the claw's `claw_frame.py`, each part's `geometry.json` and the assembly's
`torque_budget.json`, sweeps 47 170 arm poses and prints every row below.

## Summary

- **NEEDS_TEST.** Every row reaches its required SF.
- **Lowest SF 4.72** (4 required, sustained): the Ø7 × 0.5 washer bearing on the 3 mm tab at the 150 N snug preload.
  This is round 4's failure (the bare Ø5.5 pan head, 2.26), fixed as built.
- **The Ø8 washer reliefs (new failure path) pass.** They leave the wall 2.5 mm thick over 3.9 mm of its length beside
  each tab screw. Every wall row is now taken at 2.5 mm all along the contact patch and the segment, which is
  conservative:
  - bearing under the disk: 10.73;
  - edgewise bending: 9.21 (governed by the 3 mm root, Z 0, not by the relief's floor at Z 3);
  - interlayer shear: 19.19.
- **The washer seats flat.** Its inner edge reaches r 44.0, the wall's outer face line, and the relief clears it by
  0.5 mm all round.
- **The washer leaves 2.5 mm of thread in the base plate (advisory).**
  - That holds about 130 N on the placeholder interlayer shear, against the 150 N assumed snug preload (0.85).
  - The ring screws carry no tension in service: the disk only presses down on the ring, and its friction acts in the
    ring's plane. So this is about assembly torque, not strength.
  - Keep BUILD_GUIDE's "snug, no harder".
- **Spec §8:** the proof test still matches the design. At the base's 77 N on the rim (1.49 × the yaw-stall ring load)
  the ring stays at SF ≥ 6.17.

## What changed since round 4

**Design (round 5)**

- A Ø7 × 0.5 washer under each of the three M3 × 6 pan heads.
- A vertical Ø8 relief round each screw, from the tab's top (Z 3) up through the wall, so the washer sits flat. The wall
  is 2.5 mm (r 41 … 43.5) beside each relief.
- Volume 13.28 cm³.

**Method (this review)**

- The washer's bearing row is now the verdict row.
- The wall rows use the relief's 2.5 mm.
- The masses are re-measured on the round-5 solids: 706 N·mm with the arm straight out, as in `torque_budget.json`.

## Load cases

Spec §4 cases, all at 40 °C. The ring takes the whole overturning moment of each pose, the servo ignored:
R = M / 42.5.

| Case | Load | Duration | How it is applied here |
|---|---|---|---|
| Overturning moment (SYS-05) | weight ×2: 1702 N·mm → R 40.1 N | sustained | Wall bearing, edgewise bending, shear; tab bearing and tear-out |
| Yaw-stall ring catch | 2476 N·mm → R 58.3 N | short-term | as above |
| Hand push 5 N | 1875 N·mm → R 44.1 N | short-term | as above |
| Knock on the arm | 20 N at the rim (r 48) → R 22.6 N | short-term | as above |
| Friction while yawing | μ 0.1 (PTFE) to 0.3 (worn) | cyclic | Printed against the servo's stall |
| Assembly | M3 × 6 snug, 150 N | sustained | Washer on the tab; thread in the base (advisory) |

## Assumptions

**Wall**
- **Contact patch:** 10 mm of arc. An elastic estimate gives about 20.
- **Friction:** 0.3 R (PTFE worn through). It bends the wall edgewise over a 32 mm segment, twice the height.
- **Edgewise section:** the larger of two stresses, both with Kt 2.5 (sharp corners):
  - the root (Z 0, 3 mm);
  - the relief's floor (Z 3, 2.5 mm).
- **Wall thickness:** 2.5 mm everywhere in the bearing and shear rows. The relief thins only 3.9 mm of the 32 mm
  segment, so this is conservative.

**Tabs and screws**
- One tab carries the whole friction torque: bearing on the M3 shank, and tear-out to the tab's edge (2.7 mm). The relief
  starts above the tab, so the tab is unchanged.
- **Washer bearing:** 150 N snug preload over the Ø7 − Ø3.6 annulus. A 0.5 mm steel washer under a Ø5.5 head overhangs
  0.75 mm, which is stiff next to PETG, so the full annulus is counted.

**Temperature.** 40 °C against PETG softening at about 70 °C: margin 30 °C, OK.

## Allowables and sources

`library/materials.csv` has only its header, and no job has a datasheet in `inputs/`, so these are the strength-checks
**placeholder** PETG values and **NEEDS_TEST is the best verdict possible**.

| Quantity | Value | Source |
|---|---|---|
| Tension / bending along the layers (XY) | 25 MPa | strength-checks placeholder, PETG |
| Tension / bending across the layers (Z) | 12.5 MPa | placeholder × 0.5 |
| Shear in-plane / interlayer | 12.5 / 6.25 MPa | 0.5 × the normal value (Tresca), assumption |
| Bearing | 25 MPa | in-plane value |
| Kt | 2.5 wall root and relief floor (sharp) | skill; agent rule Kt ≥ 2 |

Required SF: 3 short-term, 4 sustained, 2 at a proof load.

## Results (copied from `strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | weight x2 (sustained): ring wall bearing under the disk, R 40.1 N on a 10 mm arc of the 2.5 mm wall at a relief | bearing | 1.60 | 25.00 | 15.60 | 4 | OK |
| 2 | weight x2 (sustained): wall edgewise bending from friction 0.3 R, 32 mm segment, at the root (Z 0, 3 thick) (Kt 2.5) | Z | 0.93 | 12.50 | 13.40 | 4 | OK |
| 3 | weight x2 (sustained): interlayer shear in the 2.5 mm wall from that friction | Z shear | 0.22 | 6.25 | 27.91 | 4 | OK |
| 4 | weight x2 (sustained): one tab carries the friction torque: bearing on the M3 shank, F 11.1 N | bearing | 1.24 | 25.00 | 20.21 | 4 | OK |
| 5 | weight x2 (sustained): tab tear-out to its edge (2.7 mm) | XY shear | 0.69 | 12.50 | 18.19 | 4 | OK |
| 6 | yaw-stall sweep: ring wall bearing under the disk, R 58.3 N on a 10 mm arc of the 2.5 mm wall at a relief | bearing | 2.33 | 25.00 | 10.73 | 3 | OK |
| 7 | yaw-stall sweep: wall edgewise bending from friction 0.3 R, 32 mm segment, at the root (Z 0, 3 thick) (Kt 2.5) | Z | 1.36 | 12.50 | 9.21 | 3 | OK |
| 8 | yaw-stall sweep: interlayer shear in the 2.5 mm wall from that friction | Z shear | 0.33 | 6.25 | 19.19 | 3 | OK |
| 9 | yaw-stall sweep: one tab carries the friction torque: bearing on the M3 shank, F 16.2 N | bearing | 1.80 | 25.00 | 13.90 | 3 | OK |
| 10 | yaw-stall sweep: tab tear-out to its edge (2.7 mm) | XY shear | 1.00 | 12.50 | 12.51 | 3 | OK |
| 11 | hand push 5 N: ring wall bearing under the disk, R 44.1 N on a 10 mm arc of the 2.5 mm wall at a relief | bearing | 1.77 | 25.00 | 14.16 | 3 | OK |
| 12 | hand push 5 N: wall edgewise bending from friction 0.3 R, 32 mm segment, at the root (Z 0, 3 thick) (Kt 2.5) | Z | 1.03 | 12.50 | 12.16 | 3 | OK |
| 13 | hand push 5 N: interlayer shear in the 2.5 mm wall from that friction | Z shear | 0.25 | 6.25 | 25.34 | 3 | OK |
| 14 | hand push 5 N: one tab carries the friction torque: bearing on the M3 shank, F 12.3 N | bearing | 1.36 | 25.00 | 18.35 | 3 | OK |
| 15 | hand push 5 N: tab tear-out to its edge (2.7 mm) | XY shear | 0.76 | 12.50 | 16.51 | 3 | OK |
| 16 | 20 N knock on the turntable rim (spec): ring wall bearing under the disk, R 22.6 N on a 10 mm arc of the 2.5 mm wall at a relief | bearing | 0.90 | 25.00 | 27.67 | 3 | OK |
| 17 | 20 N knock on the turntable rim (spec): wall edgewise bending from friction 0.3 R, 32 mm segment, at the root (Z 0, 3 thick) (Kt 2.5) | Z | 0.53 | 12.50 | 23.76 | 3 | OK |
| 18 | 20 N knock on the turntable rim (spec): interlayer shear in the 2.5 mm wall from that friction | Z shear | 0.13 | 6.25 | 49.50 | 3 | OK |
| 19 | 20 N knock on the turntable rim (spec): one tab carries the friction torque: bearing on the M3 shank, F 6.3 N | bearing | 0.70 | 25.00 | 35.84 | 3 | OK |
| 20 | 20 N knock on the turntable rim (spec): tab tear-out to its edge (2.7 mm) | XY shear | 0.39 | 12.50 | 32.26 | 3 | OK |
| 21 | assembly: M3 x 6 driven snug, Ø7 x 0.5 washer (round 5): washer on the tab at 150 N (sustained) | bearing | 5.30 | 25.00 | 4.72 | 4 | OK |
| 22 | spec §8 proof: 77 N on the rim (1.49 x the yaw-stall ring load): ring wall bearing under the disk, R 87.0 N on a 10 mm arc of the 2.5 mm wall at a relief | bearing | 3.48 | 25.00 | 7.19 | 2 | OK |
| 23 | spec §8 proof: 77 N on the rim (1.49 x the yaw-stall ring load): wall edgewise bending from friction 0.3 R, 32 mm segment, at the root (Z 0, 3 thick) (Kt 2.5) | Z | 2.03 | 12.50 | 6.17 | 2 | OK |
| 24 | spec §8 proof: 77 N on the rim (1.49 x the yaw-stall ring load): interlayer shear in the 2.5 mm wall from that friction | Z shear | 0.49 | 6.25 | 12.86 | 2 | OK |
| 25 | spec §8 proof: 77 N on the rim (1.49 x the yaw-stall ring load): tab tear-out from the friction torque | XY shear | 1.49 | 12.50 | 8.38 | 2 | OK |

**Lowest SF 4.72 (required 4): the Ø7 washer on the tab at the snug preload (row 21).**

### Advisory rows (not in the verdict)

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| assembly: M3 x 6 driven snug, no washer (round 4): pan head Ø5.5 on the tab at 150 N | bearing | 11.05 | 25.00 | 2.26 | 4 |
| yaw-stall sweep: ring wall bearing on the full 3 mm wall (away from the reliefs) | bearing | 1.94 | 25.00 | 12.87 | 3 |
| assembly: M3 x 6 driven snug, no washer (round 4): thread in the base plate, 3 mm engaged, at 150 N | Z shear | 6.12 | 6.25 | 1.02 | 1 |
| assembly: M3 x 6 driven snug, Ø7 x 0.5 washer (round 5): thread in the base plate, 2.5 mm engaged, at 150 N | Z shear | 7.35 | 6.25 | 0.85 | 1 |

Why each one is advisory:
- **Bare pan head (2.26).** Round 4's failure; the washer replaces it.
- **Full 3 mm wall (12.87).** For comparison with the 2.5 mm verdict row.
- **Thread in the base plate (0.85 with the washer, 1.02 without).**
  - These carry only the assembly preload: the ring screws carry no tension in service.
  - A thread that strips does so on the bench, where it is seen.
  - If one spins, an M3 × 6 wafer-head screw (head ≥ Ø7) without the washer gets the 3 mm back and the same bearing
    area.

**Friction while yawing** with the arm straight out: 88 N·mm with PTFE, 264 N·mm worn, against the yaw servo's
1079 N·mm. Acceptable.

## Proof test (spec §8): still matches the design

The base's rim test covers the ring: 77 N straight down on the turntable rim, 1 min at each of 4 positions, servo
unpowered.
- R = 87.0 N, **1.49 ×** the yaw-stall ring load.
- Rows 22–25 at the proof SF of 2: wall bearing 7.19, edgewise bending 6.17, interlayer shear 12.86, tab tear-out 8.38.
- §8's pass criteria (no cracks in the tabs or wall, no crushing of the top, washers still tight, free turning) fit the
  round-5 ring as built.

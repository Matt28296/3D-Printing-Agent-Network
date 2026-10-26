VERDICT: NEEDS_TEST

# Strength check: 20261025-arm-upper-link (links round 6, independent re-check of the round-6 solid)

strength-analyst (independent review: I did not design this part) · 2026-10-26 ·
`python3 jobs/20261025-arm-upper-link/strength_calc.py` from the project root (about 10 s). It reads every link's
`model.py`, `tools/hobby_parts.py`, the claw's `claw_frame.py`, each part's `geometry.json` and the assembly's
`torque_budget.json`, sweeps 47 170 arm poses and prints every row below.

## Summary

- **Every row passes. The verdict is NEEDS_TEST only because the allowables are placeholders** (no library row).
- **Lowest SF 3.39** (3 required): x 15 over the horn pocket under the yaw-stall sweep (row 10). It is unchanged from
  round 5. Next come the window rails at 3.42 and plate torsion at 3.69.
- **The fix works.**
  - **Rib taper root** (row 23), the ribs' force fed into the plate across the layers over the 12 mm, 27° run-out:
    yaw **3.74**, hand 4.86, weight ×2 12.2.
  - **§8 bench test:** 2.14.
  - These match the analyst's prediction of 3.78 / 4.94 / 13.2 / 2.14. The 1 % gap is the re-measured masses (below).
- **New sections pass.**
  - Half way down the run-out (x 58.2, ribs 3 deep): 6.34.
  - The plain plate at the new foot (x 52.2): 4.36 (round 5 at 58.2: 4.51).
- **Spec §8 still matches.**
  - (1): deflection 0.06 mm.
  - (2), 16 N at 175 mm with the bar at 60°: every row ≥ 2. The lowest are the rails at 2.01 and the rib taper root at 2.14.

## What changed since round 5

**Design (round 6, user-approved fourth attempt)**
- `RIB_TAPER` 6 → 12 (model.py:42). The ribs reach full depth at x 64.2 and run out at 27° to x 52.2.
- Volume +246 mm³ (44 312 mm³).

**Method (this review)**
- **The rib-root row is now the "rib taper root".** Same mechanism: F = M_y·Q/I at x 64.2 plus the rails' twist share,
  fed over 6.85 × `RIB_TAPER` per rib, Kt 2.0 at the foot. It is read from model.py, so it scales with the as-built
  12 mm.
- **New row: the run-out half way, x 58.2.** Plate 34 × 10 plus two 6.85 × 3 ribs: I 4413 mm⁴ (CAD 4414). Kt 1.5 for
  the sloped top, conservative.
- **The run-out's foot row moves to x 52.2.** I 2833 mm⁴ (CAD 2853). Kt 2.0 kept at the 153° corner.
- **Masses and centres of mass re-measured** on the round-6 / claw round-4 solids with build123d:
  - upper link (44.808, 0, 4.199);
  - forearm (40.592, 0, 4.215);
  - claw frame (9.761, 0.290, 15.013);
  - cover (26.646, 1.364, 32.199);
  - pinion z 6.089;
  - jaw (44.071, −2.286, 38.423).

  Round 5's table carried the round-2 claw (34.8 / 22.5 cm³ frame / cover). The volumes were already current through
  geometry.json, but the centres were not. The model check now reproduces torque_budget.json within 1.5 g and 4 N·mm:
  end effector 255.4 g (torque_budget 253.9: the cover's anchored post, +1.5 g, came after it). No STALE warning.

## Load cases

Spec §4 cases, all at 40 °C.

| Case | Load | Duration | How it is applied here |
|---|---|---|---|
| Shoulder stall through the horn slot | 1079 N·mm (datasheet, 01 N1) | short-term | Pocket-wall bearing; in-plane bending of the plate and the rails |
| Elbow stall | 1079 N·mm | short-term | Far tab pilot bearing; notch strip tear-out |
| Distal weight + 50 g, camera across the shafts (SYS-04) | weight ×2 over the sweep | sustained | Every section, SF 4 |
| Base-yaw stall into a side obstacle | sweep, F = 1079 / R at a fingertip or a camera end | short-term | Every section, SF 3 |
| Hand push 5 N | sweep, ±Y | short-term | Every section, SF 3 |
| Assembly | M3 × 12 tab screws snug, 150 N | sustained | Notch strip splitting |
| Spec §8 tests | as written | proof | Rows at SF 2 |

## Assumptions

- **Frame U:** back face at z 0, front face at z 10, ribs z −6…0. The link prints front face down, so the ribs are
  the last layers. Every run-out stress that passes the rib's force into the plate runs along a layer interface.
- **Rib taper root.** Each rib's axial force at x 64.2 is ½ M_y·Q_ribs/I (Q 530 mm³, I 7316 mm⁴), plus its twist
  share. That force goes into the plate through 6.85 × 12 mm of interface.
  - Kt 2.0 covers the linear run-out's peak near the foot, which is 1.8 × the average.
  - With the 27° ramp, this peak sits under a rib less than 1 mm tall, so 2.0 stays conservative.
- **Rails** carry 0.926 of the far-row moment and 0.30 of the twist (round 5's frame argument).
- **Temperature:** 40 °C, servo cases up to 45 °C, against PETG softening at about 70 °C. That is ≥ 25 °C of margin: OK.

## Allowables and sources

`library/materials.csv` has only its header, and no job has a datasheet in `inputs/`. These are the strength-checks
**placeholder** PETG values, so **NEEDS_TEST is the best verdict possible.**

| Quantity | Value | Source |
|---|---|---|
| Along the layers (XY): the link prints flat | 25 MPa | strength-checks placeholder, PETG |
| Shear, in-plane / interlayer | 12.5 / 6.25 MPa | 0.5 × the normal value (Tresca), assumption |
| Bearing | 25 MPa | in-plane value |
| E, ν | 1800 MPa, 0.35 | skill table; ν assumed |
| Kt | 2.5 at window and notch corners; 2.0 at holes and the run-out's foot; 1.5 on the sloped run-out | skill; agent rule Kt ≥ 2 at sharp transitions |

Required SF: 3 short-term, 4 sustained, 2 at a proof load (1.5 × service).

## Results (from `strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | shoulder stall: horn-pocket wall bearing | bearing | 1.97 | 25.00 | 12.67 | 3 | OK |
| 2 | shoulder stall: in-plane bending, full section | XY | 0.56 | 25.00 | 44.64 | 3 | OK |
| 3 | shoulder stall: in-plane bending of the window rails 6.85 × 16 (Kt 2.5) | XY | 1.11 | 25.00 | 22.49 | 3 | OK |
| 4 | elbow stall: far tab pilot bearing, 13.1 N | bearing | 0.87 | 25.00 | 28.79 | 3 | OK |
| 5 | elbow stall: notch → pilot strip 1.79 tear-out | XY shear | 0.63 | 12.50 | 19.88 | 3 | OK |
| 6 | weight ×2: shoulder-horn joint, Ø9 washer pull-through | Z shear | 0.45 | 6.25 | 13.80 | 4 | OK |
| 7 | yaw stall: shoulder-horn joint | Z shear | 1.48 | 6.25 | 4.23 | 3 | OK |
| 8 | hand push: shoulder-horn joint | Z shear | 1.10 | 6.25 | 5.66 | 3 | OK |
| 9 | weight ×2: x 15 over the pocket (Kt 2) | XY | 2.03 | 25.00 | 12.32 | 4 | OK |
| 10 | **yaw stall: x 15 over the pocket (Kt 2)** (s120 e−25 w50, fingertip) | XY | 7.37 | 25.00 | **3.39** | 3 | OK |
| 11 | hand push: x 15 over the pocket | XY | 6.15 | 25.00 | 4.06 | 3 | OK |
| 12 | weight ×2: plate torsion at x 15 | Z shear | 0.55 | 6.25 | 11.37 | 4 | OK |
| 13 | yaw stall: plate torsion at x 15 | Z shear | 1.70 | 6.25 | 3.69 | 3 | OK |
| 14 | hand push: plate torsion | Z shear | 1.21 | 6.25 | 5.17 | 3 | OK |
| 15 | yaw stall: x 30 full section | XY | 3.11 | 25.00 | 8.04 | 3 | OK |
| 16 | weight ×2: x 52.2, plain plate at the foot of the 27° run-out (Kt 2.0) | XY | 1.80 | 25.00 | 13.89 | 4 | OK |
| 17 | yaw stall: x 52.2, plain plate at the foot of the run-out | XY | 5.74 | 25.00 | 4.36 | 3 | OK |
| 18 | hand push: x 52.2 | XY | 4.80 | 25.00 | 5.21 | 3 | OK |
| 19 | weight ×2: **new** x 58.2, the run-out half way (ribs 3 deep, Kt 1.5) | XY | 1.27 | 25.00 | 19.76 | 4 | OK |
| 20 | yaw stall: **new** x 58.2, the run-out half way | XY | 3.94 | 25.00 | 6.34 | 3 | OK |
| 21 | hand push: **new** x 58.2 | XY | 3.30 | 25.00 | 7.57 | 3 | OK |
| 22 | weight ×2: **rib taper root**, 12 mm 27° run-out (Kt 2.0) | Z shear | 0.51 | 6.25 | 12.17 | 4 | OK |
| 23 | **yaw stall: rib taper root** (s105 e5 w35, fingertip) | Z shear | 1.67 | 6.25 | **3.74** | 3 | OK |
| 24 | hand push: rib taper root | Z shear | 1.29 | 6.25 | 4.86 | 3 | OK |
| 25 | weight ×2: far elbow-pilot row x 65.6, plate + ribs (Kt 2.0) | XY | 1.40 | 25.00 | 17.82 | 4 | OK |
| 26 | yaw stall: far pilot row | XY | 4.25 | 25.00 | 5.89 | 3 | OK |
| 27 | hand push: far pilot row | XY | 3.56 | 25.00 | 7.03 | 3 | OK |
| 28 | weight ×2: far lead notch, plate + ribs (Kt 2.5) | XY | 1.63 | 25.00 | 15.33 | 4 | OK |
| 29 | yaw stall: far lead notch | XY | 4.94 | 25.00 | 5.06 | 3 | OK |
| 30 | hand push: far lead notch | XY | 4.14 | 25.00 | 6.04 | 3 | OK |
| 31 | weight ×2: window rails 6.85 × 16 (Kt 2.5, 0.30 of the twist) | XY | 2.25 | 25.00 | 11.11 | 4 | OK |
| 32 | **yaw stall: window rails** (s105 e5 w35, fingertip) | XY | 7.30 | 25.00 | **3.42** | 3 | OK |
| 33 | hand push: window rails | XY | 5.63 | 25.00 | 4.44 | 3 | OK |
| 34 | weight ×2: rails, interlayer shear at the rib's root | Z shear | 0.10 | 6.25 | 63.23 | 4 | OK |
| 35 | yaw stall: rails, interlayer shear | Z shear | 0.32 | 6.25 | 19.43 | 3 | OK |
| 36 | hand push: rails, interlayer shear | Z shear | 0.24 | 6.25 | 26.03 | 3 | OK |
| 37 | weight ×2: elbow tab screw pull-out (9, Ø2.6) | Z shear | 0.43 | 6.25 | 14.43 | 4 | OK |
| 38 | yaw stall: elbow tab screw pull-out | Z shear | 1.51 | 6.25 | 4.14 | 3 | OK |
| 39 | hand push: elbow tab screw pull-out | Z shear | 1.04 | 6.25 | 6.00 | 3 | OK |
| 40 | weight ×2: notch strip splitting, 150 N + tension | XY | 2.02 | 25.00 | 12.35 | 4 | OK |
| 41 | yaw stall: notch strip splitting | XY | 2.90 | 25.00 | 8.61 | 3 | OK |
| 42 | hand push: notch strip splitting | XY | 2.52 | 25.00 | 9.91 | 3 | OK |
| 43 | spec §8: tab screws snug, notch strip splitting at 150 N | XY | 1.67 | 25.00 | 14.97 | 4 | OK |
| 44 | §8 proof (2), 16 N at 175 mm, bar at 60°: window rails | XY | 12.46 | 25.00 | 2.01 | 2 | OK |
| 45 | §8 proof (2): far pilot row | XY | 5.36 | 25.00 | 4.66 | 2 | OK |
| 46 | §8 proof (2): far lead notch | XY | 6.24 | 25.00 | 4.01 | 2 | OK |
| 47 | §8 proof (2): **rib taper root** | Z shear | 2.92 | 6.25 | **2.14** | 2 | OK |
| 48 | §8 proof (2): run-out foot | XY | 7.64 | 25.00 | 3.27 | 2 | OK |
| 49 | §8 proof (2): **new** run-out half way | XY | 5.13 | 25.00 | 4.87 | 2 | OK |
| 50 | §8 proof (2): x 15 bending | XY | 10.98 | 25.00 | 2.28 | 2 | OK |
| 51 | §8 proof (2): plate torsion | Z shear | 2.61 | 6.25 | 2.39 | 2 | OK |
| 52 | §8 proof (2): shoulder-horn joint | Z shear | 2.78 | 6.25 | 2.25 | 2 | OK |
| 53 | §8 proof (2): elbow tab screw pull-out | Z shear | 2.48 | 6.25 | 2.52 | 2 | OK |
| 54 | §8 proof (2): notch strip splitting | XY | 3.70 | 25.00 | 6.75 | 2 | OK |
| 55 | §8 proof (1), 1 kg at the elbow axis in plane: x 15 (Kt 2) | XY | 0.87 | 25.00 | 28.88 | 2 | OK |

The script prints each row's full label, with the governing pose.

**Lowest SF 3.39 (required 3): x 15 over the pocket, yaw stall (row 10).** Every row passes.

### Advisory rows (not in the verdict)

| Case / section | SF | SF req | Why advisory |
|---|---|---|---|
| Yaw stall, rails with round 4's twist share 0.15 | 3.80 | 3 | Comparison only |
| Yaw stall with a 15 kgf·cm clone MG996R: rails / x 15 | 2.51 / 2.49 | 3 | A clone is not a spec case (01 N1) |
| Yaw stall, tab screws over-tightened to 300 N: notch strip | 5.47 | 3 | Misuse bound |

### What-if (run-out length; full depth stays at x 64.2)

| RIB_TAPER | Foot | Yaw | Hand | Weight ×2 | §8 bench | Arm-up test | Plate at the foot |
|---|---|---|---|---|---|---|---|
| 6 (round 5) | x 58.2, 45° | 1.87 | 2.43 | 6.09 | 1.07 | 1.33 | 4.46 |
| 10 | x 54.2, 31° | 3.12 | 4.05 | 10.14 | 1.78 | 2.22 | 4.39 |
| **12 (as built)** | **x 52.2, 27°** | **3.74** | **4.86** | **12.17** | **2.14** | **2.67** | **4.36** |

## Proof test (spec §8)

- **(1) Horn in a vice, 1 kg at the elbow axis, in plane: still matches.** Deflection 0.06 mm (< 2 mm). In-plane SF 28.9.
- **(2) Bar at 60°, 16 N at 175 mm along the elbow shaft: still matches; no change is needed.**
  - The governing rows reach these multiples of their yaw-stall service value: rails 1.71 ×, rib taper root 1.75 ×,
    x 15 1.49 ×, tab screw 1.65 ×, horn joint 1.88 ×.
  - Every row is at SF ≥ 2: rails 2.01, rib taper root 2.14, x 15 2.28.
- **The turntable/base arm-up test (11.5 N at the fingertips, arm straight up)** loads this link too:
  - rib taper root 2.67;
  - rails 2.39;
  - x 15 1.95, 2 % under the proof margin, as reported in round 5 and noted in those jobs.

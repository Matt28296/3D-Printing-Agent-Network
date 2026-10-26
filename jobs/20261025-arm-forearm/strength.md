VERDICT: FAIL

# Strength check: 20261025-arm-forearm (links round 5, independent re-check of the round-5 solid)

strength-analyst (independent review: I did not design this part) · 2026-10-26 ·
`python3 jobs/20261025-arm-forearm/strength_calc.py` from the project root (about 20 s). It reads every link's
`model.py`, `tools/hobby_parts.py`, the claw's `claw_frame.py`, each part's `geometry.json` and the assembly's
`torque_budget.json`, sweeps 47 170 arm poses and prints every row below.

## Summary

- **FAIL.** Both MG90S tab screws pull out below SF 3 under the yaw-stall sweep:
  - lead-end M2 × 12: **2.42** (row 35);
  - far M2 × 16 in the new cross-rib: **2.62** (row 32).
- **Why: the pilots are slots.**
  - `servo_mount_cutter` stretches every micro-servo pilot 0.4 mm outward to take the tabs' spacing error, so the
    printed pilot reaches 0.75 + 0.4 = 1.15 mm from the screw's axis.
  - The M2 thread reaches only 1.0. Over ±42° of its circle it has no plastic to cut, so 0.77 of the thread is engaged.
  - Round 4's FIX rows, and the round-5 brief's 3.41 / 3.15, took a round pilot.
  - This applies to the M2 × 16 boss as built. It also applies to the lead-end screw, which round 4 passed at 3.15.
- **Spec §8 (2) as written over-tests the forearm.** At 19 N, bar at 45°:
  - x 15 over the horn pocket: SF 1.82 (1.85 ×);
  - lead-end screw: 1.52;
  - far screw: 1.72 (2 required at a proof load).
- **What the round-5 ribs fixed.**
  - Window rails 6.6 × 16: **4.29** (round 4: 1.71).
  - New failure paths, all passing:
    - cross-rib root (its force fed into the plate across the layers over the 6 mm run-out): 4.14;
    - plain plate at the run-out's foot: 5.00;
    - far pilot row in the cross-rib: 12.7;
    - interlayer shear at the rails' rib root: 13.7;
    - the cross-rib wall beyond the far slot: 10.0.
  - The user-accepted MG90S strips keep their rows: tear-out 4.75 / 5.19, splitting ≥ 6.20, first-print check 9.87 /
    14.61.
- **Smallest exact fix:**
  1. Cut both MG90S pilots **round**, Ø1.7 CAD (1.5 printed), at the tab holes' measured positions, without the 0.4 mm
     outward slot. Yaw stall: far M2 × 16 **3.41**, lead-end M2 × 12 **3.15**. The strips don't move, because the slots
     ran away from them.
  2. Change §8 (2) to **17 N at 83 mm with the bar at 60°**. Every row is then ≥ 2.07, and the governing rows reach
     1.44–1.52 ×.

## What changed since round 4

**Design (round 5)**

- **Rail ribs:** 6 mm back-face ribs on both rails, x 72.9 … 101.1, 6.6 wide, so the rails are 6.6 × 16.
- **Cross-rib:** x 66.9 … 72.9, full width, 6 deep, with a 45° run-out to x 60.9.
- **Far pilot:** now 16 deep, for an M2 × 16 with 13.5 mm engaged. The lead-end screw stays M2 × 12 (9.5): the lead
  leaves the case there.
- **Mass:** 32.8 cm³ (+3.6).

**Method (this review)**

- **Slotted pilots:** the engaged fraction of the M2 thread's circle is computed from the cutter's slot.
- **New rows:** the cross-rib root, the plain plate at the run-out's foot, interlayer shear at the rails' rib root, and
  the cross-rib wall beyond the slot.
- **Composite sections** with the ribs: far pilot row 8294, cross-rib at full depth 8875, rails 4506 mm⁴. They match the
  round-5 CAD within 0.2 %.
- **Spec §8 rows** are taken at the round-5 tests: (1) 1 kg at the wrist axis; (2) 19 N at 83 mm, bar at 45°. Round 4
  had stale 15 N and 7.5 N rows.
- **Masses and centres of mass** re-measured on the round-5 solids. The model reproduces `torque_budget.json`.

## Load cases

Spec §4 cases, all at 40 °C.

| Case | Load | Duration | How it is applied here |
|---|---|---|---|
| Elbow stall through the horn slot | 1079 N·mm | short-term | Pocket-wall bearing; in-plane bending |
| Wrist stall + static claw weight | 216 N·mm + 2.7 N | short-term | Far pilot bearing; strip tear-out |
| Distal weight + 50 g, camera across the shafts (SYS-04) | weight ×2 sweep | sustained | Every section and screw, SF 4 |
| Base-yaw stall into a side obstacle | sweep, F = 1079 / R | short-term | SF 3 |
| Hand push 5 N | sweep, ±Y | short-term | SF 3 |
| Assembly | M2 tab screws snug, 150 N | sustained | Strip splitting (the §8 screw-strip check) |
| Spec §8 tests | as written | proof | Rows at SF 2 |

## Assumptions

**MG90S tab screws**
- One screw per tab, on the centre line. Screw tension S = share × M_x / 6.1 + |M_y| / 30 + |F_z| / 2.
- Share: 0.70 on the far screw, 0.50 on the lead-end one. The ribs make the rails stiffer, which only moves the split
  towards 50 / 50, so both are kept.
- **Pull-out:** τ = S / (π × 1.5 × L × 0.77), against the interlayer shear allowable.
  - L 13.5 (far) and 9.5 (lead end).
  - 0.77 is the slot factor. The screw sits at the slot's inner end (its nominal place), and the slot's far end lies
    1.15 mm away, beyond the thread's 1.0 mm.
- **Strips:** the user's decision of 26 Oct 2026.
  - Widths 1.34 / 1.445 CAD, 1.19 / 1.30 intact behind the M2 thread.
  - Tear-out over 2 × d; Lamé splitting at 150 N + S, over L 9.5 / 13.5.

**Sections and rails** (frame F: back face z 0, front z 10, ribs z −6 … 0)
- **Rails:** pinned tab rows, 0.921 of the far-row moment. The twist frame takes 0.50 × M_x as differential bending, plus
  in-plane M_z; Kt 2.5.
- **Cross-rib root (new).** At x 66.9 the cross-rib's force is F = M_y × Q / I (Q about the 26 × 16 section's centroid).
  - The rails' twist couple is added on half the width.
  - Both are fed into the plate over the 6 mm × 26 mm run-out, Kt 2.0, as interlayer shear (the ribs are the last
    layers printed).
- **x 15, x 30, torsion:** unchanged.

**Temperature.** 40 °C, servo cases up to 45 °C, against PETG softening at about 70 °C: margin ≥ 25 °C, OK.

## Allowables and sources

`library/materials.csv` has only its header, and no job has a datasheet in `inputs/`, so these are the strength-checks
**placeholder** PETG values. With the fix, **NEEDS_TEST is the best verdict possible**.

| Quantity | Value | Source |
|---|---|---|
| Tension / bending along the layers (XY): the forearm prints flat | 25 MPa | strength-checks placeholder, PETG |
| Shear in-plane / interlayer | 12.5 / 6.25 MPa | 0.5 × the normal value (Tresca), assumption |
| Bearing | 25 MPa | in-plane value |
| E, ν | 1800 MPa, 0.35 | skill table; ν assumed |
| Kt | 2.5 window corners; 2.0 holes and the run-out's foot | skill; agent rule Kt ≥ 2 |

Required SF: 3 short-term, 4 sustained, 2 at a proof load (1.5 × service).

## Results (copied from `strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | elbow stall 1079 N.mm: horn-pocket wall bearing (arm flanks, triangular, 2 mm deep) | bearing | 1.97 | 25.00 | 12.67 | 3 | OK |
| 2 | elbow stall 1079 N.mm: in-plane bending, full section (M <= stall) | XY | 0.96 | 25.00 | 26.10 | 3 | OK |
| 3 | wrist stall 216 N.mm + static claw weight: far pilot bearing, F 11.6 N | bearing | 1.93 | 25.00 | 12.93 | 3 | OK |
| 4 | wrist stall 216 N.mm + static claw weight: lead-end strip 1.19: tear-out, side load 7.1 N | XY shear | 0.75 | 12.50 | 16.66 | 3 | OK |
| 5 | wrist stall 216 N.mm + static claw weight: far-end strip 1.30: tear-out, side load 11.6 N | XY shear | 1.12 | 12.50 | 11.21 | 3 | OK |
| 6 | weight x2 (sustained): clamped elbow-horn joint: Ø9 washer pull-through, floor 8 (s0 e-15 w-50) | Z shear | 0.28 | 6.25 | 22.50 | 4 | OK |
| 7 | yaw-stall sweep: clamped elbow-horn joint: Ø9 washer pull-through, floor 8 (s150 e-95 w-70, fingertip) | Z shear | 1.03 | 6.25 | 6.06 | 3 | OK |
| 8 | hand push 5 N: clamped elbow-horn joint: Ø9 washer pull-through, floor 8 (s65 e-50 w75, fingertip) | Z shear | 0.63 | 6.25 | 9.99 | 3 | OK |
| 9 | weight x2 (sustained): x 15 over the pocket, out of plane (Kt 2 arm-screw hole) (s0 e-90 w-90) | XY | 1.68 | 25.00 | 14.85 | 4 | OK |
| 10 | yaw-stall sweep: x 15 over the pocket, out of plane (Kt 2 arm-screw hole) (s175 e-150 w-5, fingertip) | XY | 7.44 | 25.00 | 3.36 | 3 | OK |
| 11 | hand push 5 N: x 15 over the pocket, out of plane (Kt 2 arm-screw hole) (s65 e25 w0, fingertip) | XY | 5.13 | 25.00 | 4.87 | 3 | OK |
| 12 | weight x2 (sustained): plate torsion, full width at x 15 (s0 e0 w-90) | Z shear | 0.45 | 6.25 | 14.01 | 4 | OK |
| 13 | yaw-stall sweep: plate torsion, full width at x 15 (s145 e-85 w-75, fingertip) | Z shear | 1.30 | 6.25 | 4.82 | 3 | OK |
| 14 | hand push 5 N: plate torsion, full width at x 15 (s0 e0 w-90, fingertip) | Z shear | 0.82 | 6.25 | 7.61 | 3 | OK |
| 15 | yaw-stall sweep: x 30 full section, out of plane (s175 e-150 w-5, fingertip) | XY | 2.95 | 25.00 | 8.47 | 3 | OK |
| 16 | weight x2 (sustained): x 60.9, plain plate at the foot of the cross-rib's 45° run-out (Kt 2.0) (s0 e-90 w-90) | XY | 1.43 | 25.00 | 17.42 | 4 | OK |
| 17 | yaw-stall sweep: x 60.9, plain plate at the foot of the cross-rib's 45° run-out (Kt 2.0) (s175 e-150 w-5, fingertip) | XY | 5.00 | 25.00 | 5.00 | 3 | OK |
| 18 | hand push 5 N: x 60.9, plain plate at the foot of the cross-rib's 45° run-out (Kt 2.0) (s65 e25 w0, fingertip) | XY | 3.31 | 25.00 | 7.55 | 3 | OK |
| 19 | weight x2 (sustained): cross-rib root: its force (and the rails' twist couple) fed into the plate across the layers over the 6 mm run-out, 26 wide (Kt 2.0) (s165 e-105 w-90) | Z shear | 0.41 | 6.25 | 15.31 | 4 | OK |
| 20 | yaw-stall sweep: cross-rib root: its force (and the rails' twist couple) fed into the plate across the layers over the 6 mm run-out, 26 wide (Kt 2.0) (s170 e-125 w-30, fingertip) | Z shear | 1.51 | 6.25 | 4.14 | 3 | OK |
| 21 | hand push 5 N: cross-rib root: its force (and the rails' twist couple) fed into the plate across the layers over the 6 mm run-out, 26 wide (Kt 2.0) (s140 e-80 w30, fingertip) | Z shear | 0.88 | 6.25 | 7.09 | 3 | OK |
| 22 | weight x2 (sustained): far MG90S pilot row x 70.6, plate + cross-rib 16 deep, out of plane (Kt 2.0) (s0 e-90 w-90) | XY | 0.60 | 25.00 | 41.69 | 4 | OK |
| 23 | yaw-stall sweep: far MG90S pilot row x 70.6, plate + cross-rib 16 deep, out of plane (Kt 2.0) (s175 e-150 w-5, fingertip) | XY | 1.97 | 25.00 | 12.69 | 3 | OK |
| 24 | hand push 5 N: far MG90S pilot row x 70.6, plate + cross-rib 16 deep, out of plane (Kt 2.0) (s140 e-50 w0, fingertip) | XY | 1.29 | 25.00 | 19.37 | 3 | OK |
| 25 | weight x2 (sustained): window rails 6.6 x 16 at the far window end, tab screws as pins (Kt 2.5) (s0 e-55 w55) | XY | 1.66 | 25.00 | 15.05 | 4 | OK |
| 26 | yaw-stall sweep: window rails 6.6 x 16 at the far window end, tab screws as pins (Kt 2.5) (s180 e-135 w-30, fingertip) | XY | 5.83 | 25.00 | 4.29 | 3 | OK |
| 27 | hand push 5 N: window rails 6.6 x 16 at the far window end, tab screws as pins (Kt 2.5) (s100 e25 w35, fingertip) | XY | 3.25 | 25.00 | 7.68 | 3 | OK |
| 28 | weight x2 (sustained): window rails: interlayer shear at the ribs' root (z 0) (s30 e-65 w-90) | Z shear | 0.13 | 6.25 | 48.75 | 4 | OK |
| 29 | yaw-stall sweep: window rails: interlayer shear at the ribs' root (z 0) (s170 e-120 w-55, fingertip) | Z shear | 0.46 | 6.25 | 13.70 | 3 | OK |
| 30 | hand push 5 N: window rails: interlayer shear at the ribs' root (z 0) (s65 e-30 w-55, fingertip) | Z shear | 0.26 | 6.25 | 24.21 | 3 | OK |
| 31 | weight x2 (sustained): far MG90S tab screw M2 x 16 pull-out (L 13.5 x 0.77 slotted, Ø1.5) (s0 e-15 w-50) | Z shear | 0.69 | 6.25 | 9.05 | 4 | OK |
| 32 | yaw-stall sweep: far MG90S tab screw M2 x 16 pull-out (L 13.5 x 0.77 slotted, Ø1.5) (s145 e-85 w-75, fingertip) | Z shear | 2.38 | 6.25 | 2.62 | 3 | **FAIL** |
| 33 | hand push 5 N: far MG90S tab screw M2 x 16 pull-out (L 13.5 x 0.77 slotted, Ø1.5) (s65 e-50 w75, fingertip) | Z shear | 1.43 | 6.25 | 4.36 | 3 | OK |
| 34 | weight x2 (sustained): lead-end MG90S tab screw M2 x 12 pull-out (L 9.5 x 0.77 slotted, Ø1.5) (s0 e-20 w-35) | Z shear | 0.73 | 6.25 | 8.60 | 4 | OK |
| 35 | yaw-stall sweep: lead-end MG90S tab screw M2 x 12 pull-out (L 9.5 x 0.77 slotted, Ø1.5) (s150 e-95 w-70, fingertip) | Z shear | 2.59 | 6.25 | 2.42 | 3 | **FAIL** |
| 36 | hand push 5 N: lead-end MG90S tab screw M2 x 12 pull-out (L 9.5 x 0.77 slotted, Ø1.5) (s70 e-50 w70, fingertip) | Z shear | 1.53 | 6.25 | 4.07 | 3 | OK |
| 37 | weight x2 (sustained): lead-end strip (notch -> moved pilot) 1.19 intact: tear-out toward the strip (s0 e0 w0) | XY shear | 1.21 | 12.50 | 10.35 | 4 | OK |
| 38 | yaw-stall sweep: lead-end strip (notch -> moved pilot) 1.19 intact: tear-out toward the strip (s0 e-125 w-45, fingertip) | XY shear | 2.63 | 12.50 | 4.75 | 3 | OK |
| 39 | hand push 5 N: lead-end strip (notch -> moved pilot) 1.19 intact: tear-out toward the strip (s0 e0 w0, fingertip) | XY shear | 0.60 | 12.50 | 20.69 | 3 | OK |
| 40 | weight x2 (sustained): lead-end strip 1.19: splitting, snug preload 150 N + screw tension (L 9.5) (s0 e-20 w-35) | XY | 2.95 | 25.00 | 8.46 | 4 | OK |
| 41 | yaw-stall sweep: lead-end strip 1.19: splitting, snug preload 150 N + screw tension (L 9.5) (s150 e-95 w-70, fingertip) | XY | 4.03 | 25.00 | 6.20 | 3 | OK |
| 42 | hand push 5 N: lead-end strip 1.19: splitting, snug preload 150 N + screw tension (L 9.5) (s0 e20 w70, fingertip) | XY | 3.42 | 25.00 | 7.31 | 3 | OK |
| 43 | weight x2 (sustained): far-end strip (window -> far pilot) 1.30 intact: tear-out toward the strip (s0 e0 w0) | XY shear | 1.11 | 12.50 | 11.30 | 4 | OK |
| 44 | yaw-stall sweep: far-end strip (window -> far pilot) 1.30 intact: tear-out toward the strip (s0 e-125 w-45, fingertip) | XY shear | 2.41 | 12.50 | 5.19 | 3 | OK |
| 45 | hand push 5 N: far-end strip (window -> far pilot) 1.30 intact: tear-out toward the strip (s0 e0 w0, fingertip) | XY shear | 0.55 | 12.50 | 22.60 | 3 | OK |
| 46 | weight x2 (sustained): far-end strip 1.30: splitting, snug preload 150 N + screw tension (L 13.5) (s0 e-15 w-50) | XY | 2.10 | 25.00 | 11.93 | 4 | OK |
| 47 | yaw-stall sweep: far-end strip 1.30: splitting, snug preload 150 N + screw tension (L 13.5) (s145 e-85 w-75, fingertip) | XY | 3.04 | 25.00 | 8.22 | 3 | OK |
| 48 | hand push 5 N: far-end strip 1.30: splitting, snug preload 150 N + screw tension (L 13.5) (s65 e-50 w75, fingertip) | XY | 2.51 | 25.00 | 9.96 | 3 | OK |
| 49 | yaw-stall sweep: cross-rib wall beyond the far slot, 2.30 at the rib's bottom: splitting (s145 e-85 w-75, fingertip) | XY | 2.49 | 25.00 | 10.03 | 3 | OK |
| 50 | yaw-stall sweep: lead-end pilot, side load along the strips: net section 1.19 + 2.90 (Kt 2) (s0 e-125 w-45, fingertip) | XY | 3.06 | 25.00 | 8.16 | 3 | OK |
| 51 | spec §8 screw-strip check: tab screws driven snug: lead-end strip 1.19: splitting at 150 N | XY | 2.53 | 25.00 | 9.87 | 4 | OK |
| 52 | spec §8 screw-strip check: tab screws driven snug: far-end strip 1.30: splitting at 150 N | XY | 1.71 | 25.00 | 14.61 | 4 | OK |
| 53 | spec §8 proof (2): 19 N at 83 mm, bar at 45°: window rails | XY | 9.03 | 25.00 | 2.77 | 2 | OK |
| 54 | spec §8 proof (2): 19 N at 83 mm, bar at 45°: far pilot row | XY | 2.86 | 25.00 | 8.73 | 2 | OK |
| 55 | spec §8 proof (2): 19 N at 83 mm, bar at 45°: cross-rib root | Z shear | 2.50 | 6.25 | 2.50 | 2 | OK |
| 56 | spec §8 proof (2): 19 N at 83 mm, bar at 45°: run-out foot | XY | 7.70 | 25.00 | 3.25 | 2 | OK |
| 57 | spec §8 proof (2): 19 N at 83 mm, bar at 45°: x 15 bending | XY | 13.76 | 25.00 | 1.82 | 2 | **FAIL** |
| 58 | spec §8 proof (2): 19 N at 83 mm, bar at 45°: plate torsion | Z shear | 1.60 | 6.25 | 3.91 | 2 | OK |
| 59 | spec §8 proof (2): 19 N at 83 mm, bar at 45°: elbow-horn joint | Z shear | 1.69 | 6.25 | 3.69 | 2 | OK |
| 60 | spec §8 proof (2): 19 N at 83 mm, bar at 45°: far tab screw pull-out | Z shear | 3.64 | 6.25 | 1.72 | 2 | **FAIL** |
| 61 | spec §8 proof (2): 19 N at 83 mm, bar at 45°: lead-end tab screw pull-out | Z shear | 4.11 | 6.25 | 1.52 | 2 | **FAIL** |
| 62 | spec §8 proof (2): 19 N at 83 mm, bar at 45°: far strip splitting | XY | 3.74 | 25.00 | 6.68 | 2 | OK |
| 63 | spec §8 proof (2): 19 N at 83 mm, bar at 45°: lead-end strip splitting | XY | 4.92 | 25.00 | 5.08 | 2 | OK |
| 64 | spec §8 proof (2): 19 N at 83 mm, bar at 45°: far strip tear-out | XY shear | 0.00 | 12.50 | inf | 2 | OK |
| 65 | spec §8 proof (2): 19 N at 83 mm, bar at 45°: lead-end strip tear-out | XY shear | 0.00 | 12.50 | inf | 2 | OK |
| 66 | spec §8 proof (1): 1 kg at the wrist axis, in plane: lead-end strip 1.19: tear-out, 9.8 N on one screw | XY shear | 1.03 | 12.50 | 12.13 | 2 | OK |
| 67 | spec §8 proof (1): 1 kg at the wrist axis, in plane: far-end strip 1.30: tear-out, 9.8 N on one screw | XY shear | 0.94 | 12.50 | 13.25 | 2 | OK |

**Lowest SF 1.52 (required 2): §8 bench test, lead-end screw pull-out (row 61).**
- Also failing: rows 35 (2.42) and 32 (2.62) under the yaw stall; rows 57 (x 15, 1.82) and 60 (far screw, 1.72) in the
  §8 test.
- Every other row passes. Next lowest: x 15 3.36 (row 10), run-out foot 5.00 (row 17), cross-rib root 4.14 (row 20),
  rails 4.29 (row 26).

### Advisory rows (not in the verdict)

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| yaw-stall sweep: far M2 x 16 pull-out as round 4 and the round-5 brief count it (round pilot, slot ignored) | Z shear | 1.83 | 6.25 | 3.41 | 3 |
| yaw-stall sweep: lead-end M2 x 12 pull-out as round 4 and the round-5 brief count it (round pilot, slot ignored) | Z shear | 1.99 | 6.25 | 3.15 | 3 |
| desk crash (SYS-11), wrist back-driven at 1040 N.mm: far-end strip 1.30: tear-out, 43 N | XY shear | 4.11 | 12.50 | 3.04 | 3 |
| desk crash (SYS-11): far pilot bearing, 43 N | bearing | 7.13 | 25.00 | 3.51 | 3 |
| yaw-stall sweep, tab screws over-tightened to 300 N: lead-end strip 1.19: splitting | XY | 6.56 | 25.00 | 3.81 | 3 |
| yaw-stall sweep, tab screws over-tightened to 300 N: far-end strip 1.30: splitting | XY | 4.75 | 25.00 | 5.26 | 3 |
| yaw-stall sweep with a 15 kgf.cm clone MG996R: far tab screw pull-out | Z shear | 3.25 | 6.25 | 1.92 | 3 |
| yaw-stall sweep with a 15 kgf.cm clone MG996R: window rails | XY | 7.95 | 25.00 | 3.14 | 3 |

Why each one is advisory:
- **Pull-out with a round pilot (3.41 / 3.15).** The pass the fix gives.
- **Desk crash (SYS-11).** Not a spec case.
- **Over-tightened screws.** A sensitivity.
- **Clone MG996R.** Not a spec case (01 N1).

## Required changes (FAIL)

1. **Both MG90S pilots round: Ø1.7 CAD, no 0.4 mm outward slot.**
   - Place them at the tab holes as measured; spec §3 already asks for the servo to be measured.
   - `servo_mount_cutter` always slots micro-servo pilots, so either it gets an option to leave the slot out, or
     `model.py` cuts these two pilots itself.
   - Yaw stall: far M2 × 16 **3.41**, lead-end M2 × 12 **3.15**.
   - Nothing gets thinner: the strips (the slots ran away from them), the 2.45 cross-rib wall (it grows to 2.85), the plate end
     past the lead-end pilot (3.05 CAD, 3.45 without the slot).
   - Longer screws can't do it alone. The far screw would need 15.5 mm engaged in a 16 mm pilot, and the lead end
     11.8 mm in a 10 mm plate that can't take a boss.
2. **Spec §8 (2): 17 N at 83 mm with the bar at 60°.** Was 19 N at 45°. See below.

With both changes every row reaches its required SF, and the verdict becomes NEEDS_TEST.

## Proof test (spec §8)

- **(1) Elbow horn in a vice, 1 kg at the wrist axis, in plane.** Strip tear-out SF 12.1 / 13.3. Still matches.
- **Screw-strip check (first print).** Splitting at the snug preload: 9.87 / 14.61. Still matches.
- **(2) Bar on the wrist horn, 19 N along the wrist shaft at 83 mm, bar at 45°: does not match.**
  - With the ribs, the rails are no longer what governs (ratio 1.55, SF 2.77). The test's 1.85 × on x 15 takes that
    section to SF 1.82.
  - The tab screws reach 1.53–1.59 ×: SF 1.72 / 1.52 as drawn, 2.23 / 1.98 even with round pilots.
  - Replace it with:

    > (2) Same clamping, with the forearm plate vertical and the wrist MG90S fitted with its tab screws as built. Screw a
    > flat bar (≥ 100 mm) to the wrist horn in place of the claw, set at **60°** to the forearm in its plane. Push
    > **17 N (≈1.7 kg)** along the wrist shaft, square to the plate, at 83 mm from the wrist axis, 1 min each way. Pass:
    > as now.

  - With round pilots it gives the governing rows: x 15 1.44 ×, far screw 1.50 ×, lead-end screw 1.52 ×, horn joint
    1.57 ×, rails 1.28 ×.
  - Every row then stays at SF ≥ 2.07, the lowest being the lead-end screw.
- **The turntable/base arm-up test (11.5 N)** loads this forearm to at most 1.44 × at x 15: SF ≥ 2.34. Still fine.

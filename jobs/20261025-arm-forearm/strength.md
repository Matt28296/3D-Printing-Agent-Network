VERDICT: NEEDS_TEST

# Strength check: 20261025-arm-forearm (links round 6, independent re-check of the round-6 solid)

strength-analyst (independent review: I did not design this part) · 2026-10-26 ·
`python3 jobs/20261025-arm-forearm/strength_calc.py` from the project root (about 10 s). It reads every link's
`model.py`, `tools/hobby_parts.py`, the claw's `claw_frame.py`, each part's `geometry.json` and the assembly's
`torque_budget.json`, sweeps 47 170 arm poses and prints every row below.

## Summary

- **Every row passes. The verdict is NEEDS_TEST only because the allowables are placeholders.**
- **Lowest service SF 3.12** (3 required): the lead-end M2 × 12 pulling out under the yaw-stall sweep (row 35).
  - The far M2 × 16 gives **3.38** (row 32).
  - Round 5, with slotted pilots, gave 2.39 / 2.60 on today's masses (2.42 / 2.62 as reported then).
  - The analyst's prediction was 3.15 / 3.41. The 1 % gap is the re-measured claw masses and centres (below).
- **The round pilots are as built.** model.py's `PILOT_D` 1.7 and `LEAD_PILOT_X` 99.7 are read by the script, and an
  assert ties them to the cutter's pilot positions. The whole M2 thread circle is in plastic (0.77 in round 5).
- **New rows for the round pilots all pass:**
  - plate end beyond the lead pilot (3.30 behind the thread): splitting 8.46, tear-out 12.9;
  - cross-rib wall beyond the far pilot (2.70): splitting 10.4, tear-out 10.6.
- **The user-accepted MG90S strips keep their margins:**
  - tear-out 4.65 / 5.08, splitting ≥ 6.18;
  - first-print screw-strip check 9.87 / 14.61.
- **Spec §8 matches as now written.**
  - (2), 17 N at 83 mm with the bar at 60°: every row ≥ 2. The lowest is the lead-end screw at **2.07**.
  - (1) and the screw-strip check still match.

## What changed since round 5

**Design (round 6, user-approved fourth attempt)**
- Both MG90S tab pilots are cut round, Ø1.7 CAD (Ø1.5 printed), at x 70.6 and 99.7. Round 5 had them slotted 0.4
  outward.
- The walls beyond them grow: cross-rib wall 2.45 → 2.85 CAD, plate end 3.05 → 3.45 CAD. The strips don't move.
- Spec §8 (2) is now 17 N at 83 mm with the bar at 60° (was 19 N at 45°).

**Method (this review)**
- `SLOT` is 0 when model.py defines `PILOT_D` and `LEAD_PILOT_X`, so `SLOT_ENG` is 1.0. The far-wall and plate-end
  ligaments drop the 0.4 mm slot.
- **New rows:**
  - plate end beyond the round lead-end pilot: splitting (Lamé, 150 N snug + tension) and tear-out;
  - tear-out into the cross-rib wall beyond the far pilot.
- **Spec §8 (2) rows** are taken at 17 N, bar at 60°.
- **Masses and centres of mass re-measured** on the round-6 / claw round-4 solids, as in the upper-link report. The model
  reproduces torque_budget.json; the end effector is 255.4 g against 253.9, because the cover's anchored post came after
  torque_budget was run. No STALE warning.
- **Advisory:** the same pull-out rows had the pilots stayed slotted, for comparison.

## Load cases

Spec §4 cases, all at 40 °C.

| Case | Load | Duration | How it is applied here |
|---|---|---|---|
| Elbow stall through the horn slot | 1079 N·mm | short-term | Pocket-wall bearing; in-plane bending |
| Wrist stall + static claw weight | 216 N·mm + 3.0 N (claw, camera, 50 g) | short-term | Pilot bearing; strip tear-out |
| Distal weight + 50 g (SYS-04) | weight ×2 over the sweep | sustained | Every section, SF 4 |
| Base-yaw stall into a side obstacle | sweep, F = 1079 / R | short-term | Every section, SF 3 |
| Hand push 5 N | sweep, ±Y | short-term | Every section, SF 3 |
| Assembly | M2 tab screws snug, 150 N | sustained | Strip splitting |
| Spec §8 tests | as written (round 6) | proof | Rows at SF 2 |

## Assumptions

- **Tab screws.** Far: M2 × 16 with 13.5 mm engaged in plate + cross-rib. Lead end: M2 × 12 with 9.5 mm engaged.
  - Pull-out is a thread-shear cylinder Ø1.5 (printed pilot) × L, now with the whole circle engaged.
  - Twist split: 70 % on the far screw, 50 % on the near screw (round 5).
- **Ligaments behind the M2 thread** (0.15 off the CAD hole on each side):
  - lead-end strip 1.19, far strip 1.30 (user-accepted);
  - plate end beyond the lead pilot 3.30;
  - cross-rib wall beyond the far pilot 2.70.
- **The far tab has no slot any more** (DFM note 1). A tab-hole spacing error then goes into the far strip. BUILD_GUIDE
  §2's measurement and the first-print strip check cover it.
- **Temperature:** 40 °C against PETG softening at about 70 °C: OK.

## Allowables and sources

`library/materials.csv` has only its header, and no job has a datasheet in `inputs/`. These are the **placeholder** PETG
values: NEEDS_TEST at best.

| Quantity | Value | Source |
|---|---|---|
| Along the layers (XY) | 25 MPa | strength-checks placeholder, PETG |
| Shear, in-plane / interlayer | 12.5 / 6.25 MPa | 0.5 × the normal value, assumption |
| Bearing | 25 MPa | in-plane value |
| Kt | 2.5 window corners; 2.0 holes and the run-out's foot | skill; agent rule |

Required SF: 3 short-term, 4 sustained, 2 at a proof load.

## Results (from `strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | elbow stall: horn-pocket wall bearing | bearing | 1.97 | 25.00 | 12.67 | 3 | OK |
| 2 | elbow stall: in-plane bending, full section | XY | 0.96 | 25.00 | 26.10 | 3 | OK |
| 3 | wrist stall + weight: far pilot bearing, 11.9 N | bearing | 1.98 | 25.00 | 12.60 | 3 | OK |
| 4 | wrist stall + weight: lead-end strip 1.19 tear-out | XY shear | 0.78 | 12.50 | 15.97 | 3 | OK |
| 5 | wrist stall + weight: far strip 1.30 tear-out | XY shear | 1.14 | 12.50 | 10.92 | 3 | OK |
| 6 | weight ×2: elbow-horn joint | Z shear | 0.30 | 6.25 | 20.76 | 4 | OK |
| 7 | yaw stall: elbow-horn joint | Z shear | 1.04 | 6.25 | 6.01 | 3 | OK |
| 8 | hand push: elbow-horn joint | Z shear | 0.64 | 6.25 | 9.81 | 3 | OK |
| 9 | weight ×2: x 15 over the pocket | XY | 1.82 | 25.00 | 13.71 | 4 | OK |
| 10 | yaw stall: x 15 over the pocket (Kt 2) | XY | 7.47 | 25.00 | 3.35 | 3 | OK |
| 11 | hand push: x 15 | XY | 5.20 | 25.00 | 4.81 | 3 | OK |
| 12 | weight ×2: plate torsion | Z shear | 0.48 | 6.25 | 12.94 | 4 | OK |
| 13 | yaw stall: plate torsion | Z shear | 1.30 | 6.25 | 4.79 | 3 | OK |
| 14 | hand push: plate torsion | Z shear | 0.84 | 6.25 | 7.44 | 3 | OK |
| 15 | yaw stall: x 30 full section | XY | 2.96 | 25.00 | 8.44 | 3 | OK |
| 16 | weight ×2: x 60.9, plate at the run-out's foot (Kt 2) | XY | 1.55 | 25.00 | 16.09 | 4 | OK |
| 17 | yaw stall: x 60.9 | XY | 5.02 | 25.00 | 4.98 | 3 | OK |
| 18 | hand push: x 60.9 | XY | 3.37 | 25.00 | 7.41 | 3 | OK |
| 19 | weight ×2: cross-rib root over the 6 mm run-out | Z shear | 0.44 | 6.25 | 14.14 | 4 | OK |
| 20 | yaw stall: cross-rib root | Z shear | 1.53 | 6.25 | 4.09 | 3 | OK |
| 21 | hand push: cross-rib root | Z shear | 0.90 | 6.25 | 6.96 | 3 | OK |
| 22 | weight ×2: far pilot row x 70.6, 16 deep (Kt 2) | XY | 0.65 | 25.00 | 38.49 | 4 | OK |
| 23 | yaw stall: far pilot row | XY | 1.98 | 25.00 | 12.62 | 3 | OK |
| 24 | hand push: far pilot row | XY | 1.32 | 25.00 | 19.00 | 3 | OK |
| 25 | weight ×2: window rails 6.6 × 16 (Kt 2.5) | XY | 1.80 | 25.00 | 13.89 | 4 | OK |
| 26 | yaw stall: window rails | XY | 5.90 | 25.00 | 4.24 | 3 | OK |
| 27 | hand push: window rails | XY | 3.32 | 25.00 | 7.52 | 3 | OK |
| 28 | weight ×2: rails, interlayer shear at the rib root | Z shear | 0.14 | 6.25 | 45.02 | 4 | OK |
| 29 | yaw stall: rails, interlayer shear | Z shear | 0.46 | 6.25 | 13.55 | 3 | OK |
| 30 | hand push: rails, interlayer shear | Z shear | 0.26 | 6.25 | 23.72 | 3 | OK |
| 31 | weight ×2: far M2 × 16 pull-out (13.5, round pilot) | Z shear | 0.57 | 6.25 | 10.90 | 4 | OK |
| 32 | **yaw stall: far M2 × 16 pull-out, round pilot** (s145 e−85 w−75, fingertip) | Z shear | 1.85 | 6.25 | **3.38** | 3 | OK |
| 33 | hand push: far M2 × 16 pull-out | Z shear | 1.12 | 6.25 | 5.56 | 3 | OK |
| 34 | weight ×2: lead-end M2 × 12 pull-out (9.5, round pilot) | Z shear | 0.60 | 6.25 | 10.36 | 4 | OK |
| 35 | **yaw stall: lead-end M2 × 12 pull-out, round pilot** (s150 e−95 w−70, fingertip) | Z shear | 2.01 | 6.25 | **3.12** | 3 | OK |
| 36 | hand push: lead-end M2 × 12 pull-out | Z shear | 1.20 | 6.25 | 5.20 | 3 | OK |
| 37 | weight ×2: lead-end strip 1.19 tear-out | XY shear | 1.33 | 12.50 | 9.42 | 4 | OK |
| 38 | yaw stall: lead-end strip tear-out | XY shear | 2.69 | 12.50 | 4.65 | 3 | OK |
| 39 | hand push: lead-end strip tear-out | XY shear | 0.66 | 12.50 | 18.84 | 3 | OK |
| 40 | weight ×2: lead-end strip splitting, 150 N + tension | XY | 2.99 | 25.00 | 8.37 | 4 | OK |
| 41 | yaw stall: lead-end strip splitting | XY | 4.05 | 25.00 | 6.18 | 3 | OK |
| 42 | hand push: lead-end strip splitting | XY | 3.44 | 25.00 | 7.27 | 3 | OK |
| 43 | weight ×2: far strip 1.30 tear-out | XY shear | 1.21 | 12.50 | 10.29 | 4 | OK |
| 44 | yaw stall: far strip tear-out | XY shear | 2.46 | 12.50 | 5.08 | 3 | OK |
| 45 | hand push: far strip tear-out | XY shear | 0.61 | 12.50 | 20.58 | 3 | OK |
| 46 | weight ×2: far strip splitting | XY | 2.13 | 25.00 | 11.75 | 4 | OK |
| 47 | yaw stall: far strip splitting | XY | 3.05 | 25.00 | 8.19 | 3 | OK |
| 48 | hand push: far strip splitting | XY | 2.53 | 25.00 | 9.90 | 3 | OK |
| 49 | yaw stall: cross-rib wall beyond the far pilot, 2.70: splitting | XY | 2.41 | 25.00 | 10.38 | 3 | OK |
| 50 | yaw stall: **new** plate end beyond the round lead pilot, 3.30: splitting | XY | 2.95 | 25.00 | 8.46 | 3 | OK |
| 51 | yaw stall: **new** round lead pilot, tear-out to the plate end | XY shear | 0.97 | 12.50 | 12.90 | 3 | OK |
| 52 | yaw stall: **new** round far pilot, tear-out into the cross-rib wall | XY shear | 1.18 | 12.50 | 10.55 | 3 | OK |
| 53 | yaw stall: lead pilot net section 1.19 + 3.30 (Kt 2) | XY | 2.85 | 25.00 | 8.77 | 3 | OK |
| 54 | §8 screw-strip check: lead-end strip splitting at 150 N | XY | 2.53 | 25.00 | 9.87 | 4 | OK |
| 55 | §8 screw-strip check: far strip splitting at 150 N | XY | 1.71 | 25.00 | 14.61 | 4 | OK |
| 56 | §8 proof (2), 17 N at 83 mm, bar at 60°: window rails | XY | 7.48 | 25.00 | 3.34 | 2 | OK |
| 57 | §8 proof (2): far pilot row | XY | 2.00 | 25.00 | 12.52 | 2 | OK |
| 58 | §8 proof (2): cross-rib root | Z shear | 2.06 | 6.25 | 3.03 | 2 | OK |
| 59 | §8 proof (2): run-out foot | XY | 5.54 | 25.00 | 4.51 | 2 | OK |
| 60 | §8 proof (2): x 15 bending | XY | 10.73 | 25.00 | 2.33 | 2 | OK |
| 61 | §8 proof (2): plate torsion | Z shear | 1.75 | 6.25 | 3.56 | 2 | OK |
| 62 | §8 proof (2): elbow-horn joint | Z shear | 1.62 | 6.25 | 3.85 | 2 | OK |
| 63 | §8 proof (2): far tab screw pull-out | Z shear | 2.76 | 6.25 | 2.27 | 2 | OK |
| 64 | **§8 proof (2): lead-end tab screw pull-out** | Z shear | 3.02 | 6.25 | **2.07** | 2 | OK |
| 65 | §8 proof (2): far strip splitting | XY | 3.71 | 25.00 | 6.74 | 2 | OK |
| 66 | §8 proof (2): lead-end strip splitting | XY | 4.82 | 25.00 | 5.19 | 2 | OK |
| 67 | §8 proof (2): far strip tear-out (no in-plane force in this test) | XY shear | 0.00 | 12.50 | ∞ | 2 | OK |
| 68 | §8 proof (2): lead-end strip tear-out | XY shear | 0.00 | 12.50 | ∞ | 2 | OK |
| 69 | §8 proof (1), 1 kg at the wrist axis: lead-end strip tear-out | XY shear | 1.03 | 12.50 | 12.13 | 2 | OK |
| 70 | §8 proof (1): far strip tear-out | XY shear | 0.94 | 12.50 | 13.25 | 2 | OK |

**Lowest SF 3.12 (required 3): the lead-end M2 × 12 pull-out under the yaw stall (row 35).** Next come x 15 at 3.35 and
the far M2 × 16 at 3.38. Every row passes.

### Advisory rows (not in the verdict)

| Case / section | SF | SF req | Why advisory |
|---|---|---|---|
| Yaw stall: far / lead-end pull-out had the pilots stayed slotted (0.77 of the thread) | 2.60 / 2.39 | 3 | Round 5 for comparison |
| Desk crash (SYS-11), wrist back-driven at 1040 N·mm: far strip tear-out / pilot bearing | 3.04 / 3.51 | 3 | 01 SYS-11 bound, not a spec case |
| Tab screws over-tightened to 300 N: lead / far strip splitting | 3.80 / 5.25 | 3 | Misuse bound |
| 15 kgf·cm clone MG996R: far screw pull-out / rails | 2.48 / 3.11 | 3 | A clone is not a spec case (01 N1) |

**Engagement margin.** The yaw stall needs 9.1 mm engaged at the lead end (9.5 fitted) and 12.0 at the far end (13.5).
Don't shorten either screw.

## Proof test (spec §8)

- **(1) Elbow horn in a vice, 1 kg at the wrist axis: still matches.** Strip tear-out 12.1 / 13.3.
- **Screw-strip check (first print): still matches.** Splitting at the snug preload is 9.87 / 14.61. It now also covers
  the far tab's lost spacing play (DFM note 1).
- **(2) Bar at 60°, 17 N along the wrist shaft at 83 mm: matches as written.**
  - Every row is at SF ≥ 2. The lowest is the lead-end screw pull-out at 2.07; then the far screw 2.27 and x 15 2.33.
  - The governing yaw-stall rows reach 1.44–1.56 × their service values: x 15 1.44, far screw 1.49, lead-end screw 1.51,
    horn joint 1.56.
  - For reference, the largest push that keeps every row ≥ 2 with the bar at 60° is 17.6 N. So 17 N is the right test.
- **The turntable/base arm-up test (11.5 N)** loads this forearm to at most 1.44 × (x 15): SF ≥ 2.32. Still fine.

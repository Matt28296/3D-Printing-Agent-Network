VERDICT: FAIL

# Strength check: 20261025-arm-upper-link (links round 5, independent re-check of the round-5 solid)

strength-analyst (independent review: I did not design this part) · 2026-10-26 ·
`python3 jobs/20261025-arm-upper-link/strength_calc.py` from the project root (about 20 s). It reads every link's
`model.py`, `tools/hobby_parts.py`, the claw's `claw_frame.py`, each part's `geometry.json` and the assembly's
`torque_budget.json`, sweeps 47 170 arm poses and prints every row below.

## Summary

- **FAIL.** Lowest SF **1.89** (3 required) under the yaw-stall sweep (s105 e5 w35, fingertip), at the **root of the new
  rail ribs where they run out** (row 20). The hand push gives 2.47 (row 21) and spec §8's bench test 1.07 (row 44,
  2 required).
- **What fails.**
  - The ribs reach full depth at x 64.2 and run out at 45° to the back face at x 58.2.
  - At x 64.2 the two ribs carry 106 N of the out-of-plane bending force (M_y 1467 N·mm).
  - All of it has to pass into the plate through the 6 mm run-out, across the layer interface (z 0, the back face).
  - Interlayer shear: 3.30 MPa against 6.25.
  - This is a new failure path, a "cover plate" ending too abruptly. Round 4's FIX rows checked only the rails' bending.
- **The ribs do their main job.** The window rails (6.85 × 16) are at **3.47** under the yaw stall (round 4: 1.49).
  - This is below the designer's 3.82, because the stiffer rails now draw 30 % of the twist instead of 15 %.
  - With round 4's 15 % the rails would be at 3.85.
  - The other new sections pass: the far pilot row 5.95, the far notch 5.12, the plain plate at the run-out's foot 4.51.
- **Smallest exact fix: `RIB_TAPER` 6 → 12.**
  - The ribs still reach full depth at x 64.2; their run-out becomes 27° and meets the back face at x 52.2.
  - Rib root: yaw **3.78**, hand 4.94, weight ×2 13.2.
  - §8 bench test 2.14, and the turntable's arm-up test 2.69.
  - The plate at the new foot: 4.40.
  - 10 mm is not enough: 3.15 yaw, but 1.78 in the §8 test.
  - Re-run `assembly_check.py` for the shoulder sweep: the ribs then start 52 mm from the shoulder axis, not 58. They are
    under 1 mm tall for their first 2 mm.
- **Spec §8:**
  - (1) still matches: 0.06 mm deflection.
  - (2), 16 N at 175 mm with the bar at 60°, matches once the fix is in. Rails 2.01, rib root 2.14, x 15 2.28: every row
    ≥ 2.
  - The turntable/base arm-up test (11.5 N) takes x 15 here to SF 1.96, 2 % under the proof margin. Noted in those jobs.

## What changed since round 4

**Design (round 5)**

- **Rail ribs:** a 6 mm rib on each window rail, on the back face (`rail_ribs()`).
  - Full depth from x 64.2 to 117, 6.85 wide (the inner face continues the window wall).
  - A 45° run-out to x 58.2.
- **What passes through:** the window, both notches and the four pilots go through 16 mm. The M3 × 12 tab screws still
  engage 9 mm.
- **Mass:** 44.1 cm³ (+4.6).

**Method (this review)**

- **New rows.**
  - **Rib root.** The ribs' force fed into the plate over the run-out (the failure above).
  - **Plain plate at the run-out's foot.**
  - **Interlayer shear at the ribs' root inside the window.** 19.7.
  - **Spec §8 proof rows** at the proof SF.
- **Sections with the ribs.** Composite sections: far pilot row, far notch, rails, and full depth at x 64.2. They match
  the round-5 CAD within 0.5 % (3 % at x 64.2, where the CAD cut grazes the pilot holes).
- **Twist share in the rails: 0.30** (round 4: 0.15).
  - The near tab's path runs in series through the rails as a frame. The ribs raise that frame's stiffness by
    (16 / 10)³ = 4.1 ×.
  - The rails' share of the twist goes from 3–13 % to 11–29 %.
- **Masses and centres of mass** re-measured on the round-5 solids. The model reproduces `torque_budget.json`.

## Load cases

Spec §4 cases, all at 40 °C.

| Case | Load | Duration | How it is applied here |
|---|---|---|---|
| Shoulder stall through the horn slot | 1079 N·mm | short-term | Pocket-wall bearing; in-plane bending of the plate and the rails |
| Elbow stall | 1079 N·mm | short-term | Far tab pilot bearing; notch strip tear-out |
| Distal weight + 50 g, camera across the shafts (SYS-04) | weight ×2 sweep | sustained | Every section, SF 4 |
| Base-yaw stall into a side obstacle | sweep, F = 1079 / R | short-term | Every section, SF 3 |
| Hand push 5 N | sweep, ±Y | short-term | Every section, SF 3 |
| Assembly | M3 × 12 tab screws snug, 150 N | sustained | Notch strip splitting |
| Spec §8 tests | as written | proof | Rows at SF 2 |

The sweep is the same as the base's: 47 170 poses, contact cases plus static weight with the worse sign of each component.

## Assumptions

**Sections** (frame U: back face z 0, front face z 10, ribs z −6 … 0)
- **x 15** over the 2 mm horn pocket, Kt 2 for the arm-screw hole: I 2599.
- **x 30**, full: 2833.
- **Foot of the run-out (x 58.2)**, plain plate, Kt 2.0 at the 135° corner: 2833.
- **Full depth (x 64.2)**: plate 34 × 10 + ribs 2 × 6.85 × 6, centroid z 3.44: I 7316.
- **Far pilot row (x 65.6)**: plate less 2 × Ø2.8 + ribs, Kt 2: 6693.
- **Far notch**: plate less 4.6 + ribs, Kt 2.5, 0.94 of the row moment: 6808.
- **Rails**: 2 × 6.85 × 16: 4676.

**Rail moment.** Each tab row of two screws acts as a pin about the plate's y axis.
- The rails carry 0.926 of the far-row moment at the window's far end.
- Each rail also carries its share of the twist (0.30 × M_x) as differential bending: M_x × 41.3 / (2 × 27.15).
- Kt 2.5 at the sharp window corner.

**Rib root (new).**
- At x 64.2 the ribs' axial force is F = M_y × Q / I, with Q = 530 mm³, the ribs' first moment about the centroid. Each
  rib carries half of it, plus its twist force (rail moment × 205.5 / 2338).
- The force goes into the plate through the run-out's interface: 6.85 × 6 mm per rib.
- Kt 2.0 at the foot. For a linear run-out the force falls steeply near d = 0: F/M is 0.032 at 1.5 mm of rib depth,
  0.054 at 3 and 0.072 at 6. So the shear at the foot is about 1.8 × the average.
- **Direction:** the link prints front face down, so the ribs are the last layers and this shear runs along a layer
  interface: 6.25 MPa allowable.
- **Without the twist term** the yaw stall still gives 2.42. With Kt 1.5, 2.52. Either way the row fails.

**Other rows.**
- **Horn joint:** washer pull-through, S = |M_y| / 17.5 + |M_x| / 5.5 + |F_z|.
- **Plate torsion:** τ = T / (α b t²).
- **Tab screws:** S = |M_x| / 14.85 (all on the far tab's outer screw) + |M_y| / (2 × 51.25) + |F_z| / 4.
  - Pull-out over 9 mm, Ø2.6.
  - Notch strip splitting with Lamé, at 150 N + S.

**Temperature.** 40 °C, servo cases up to 45 °C, against PETG softening at about 70 °C: margin ≥ 25 °C, OK.

## Allowables and sources

`library/materials.csv` has only its header, and no job has a datasheet in `inputs/`, so these are the strength-checks
**placeholder** PETG values. With the fix, **NEEDS_TEST is the best verdict possible**.

| Quantity | Value | Source |
|---|---|---|
| Tension / bending along the layers (XY): the link prints flat | 25 MPa | strength-checks placeholder, PETG |
| Shear in-plane / interlayer | 12.5 / 6.25 MPa | 0.5 × the normal value (Tresca), assumption |
| Bearing | 25 MPa | in-plane value |
| E, ν | 1800 MPa, 0.35 | skill table; ν assumed |
| Kt | 2.5 window and notch corners; 2.0 holes and the run-out's foot | skill; agent rule Kt ≥ 2 |

Required SF: 3 short-term, 4 sustained, 2 at a proof load (1.5 × service).

## Results (copied from `strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | shoulder stall 1079 N.mm: horn-pocket wall bearing (arm flanks, triangular, 2 mm deep) | bearing | 1.97 | 25.00 | 12.67 | 3 | OK |
| 2 | shoulder stall 1079 N.mm: in-plane bending, full section (M <= stall) | XY | 0.56 | 25.00 | 44.64 | 3 | OK |
| 3 | shoulder stall 1079 N.mm: in-plane bending of the window rails, 6.85 x 16 (Kt 2.5) | XY | 1.11 | 25.00 | 22.49 | 3 | OK |
| 4 | elbow stall 1079 N.mm: far tab pilot bearing, F 13.1 N | bearing | 0.87 | 25.00 | 28.79 | 3 | OK |
| 5 | elbow stall 1079 N.mm: notch -> pilot strip 1.79: tear-out, F 13.1 N | XY shear | 0.63 | 12.50 | 19.88 | 3 | OK |
| 6 | weight x2 (sustained): clamped shoulder-horn joint: Ø9 washer pull-through, floor 8 (s15 e-150 w-90) | Z shear | 0.42 | 6.25 | 14.98 | 4 | OK |
| 7 | yaw-stall sweep: clamped shoulder-horn joint: Ø9 washer pull-through, floor 8 (s115 e-70 w-15, fingertip) | Z shear | 1.46 | 6.25 | 4.27 | 3 | OK |
| 8 | hand push 5 N: clamped shoulder-horn joint: Ø9 washer pull-through, floor 8 (s165 e-75 w0, fingertip) | Z shear | 1.09 | 6.25 | 5.75 | 3 | OK |
| 9 | weight x2 (sustained): x 15 over the pocket, out of plane (Kt 2 arm-screw hole) (s90 e-150 w-90) | XY | 1.87 | 25.00 | 13.39 | 4 | OK |
| 10 | yaw-stall sweep: x 15 over the pocket, out of plane (Kt 2 arm-screw hole) (s120 e-25 w50, fingertip) | XY | 7.30 | 25.00 | 3.42 | 3 | OK |
| 11 | hand push 5 N: x 15 over the pocket, out of plane (Kt 2 arm-screw hole) (s90 e0 w0, fingertip) | XY | 6.07 | 25.00 | 4.12 | 3 | OK |
| 12 | weight x2 (sustained): plate torsion, full width at x 15 (s0 e-150 w-90) | Z shear | 0.51 | 6.25 | 12.36 | 4 | OK |
| 13 | yaw-stall sweep: plate torsion, full width at x 15 (s130 e-90 w-15, fingertip) | Z shear | 1.68 | 6.25 | 3.72 | 3 | OK |
| 14 | hand push 5 N: plate torsion, full width at x 15 (s180 e-90 w0, fingertip) | Z shear | 1.19 | 6.25 | 5.27 | 3 | OK |
| 15 | yaw-stall sweep: x 30 full section, out of plane (s120 e-25 w50, fingertip) | XY | 3.08 | 25.00 | 8.12 | 3 | OK |
| 16 | weight x2 (sustained): x 58.2, plain plate at the foot of the ribs' 45° run-out (Kt 2.0) (s90 e-150 w-90) | XY | 1.66 | 25.00 | 15.09 | 4 | OK |
| 17 | yaw-stall sweep: x 58.2, plain plate at the foot of the ribs' 45° run-out (Kt 2.0) (s120 e-25 w50, fingertip) | XY | 5.55 | 25.00 | 4.51 | 3 | OK |
| 18 | hand push 5 N: x 58.2, plain plate at the foot of the ribs' 45° run-out (Kt 2.0) (s90 e0 w0, fingertip) | XY | 4.62 | 25.00 | 5.41 | 3 | OK |
| 19 | weight x2 (sustained): rib root: the ribs' force fed into the plate across the layers over the 6 mm run-out (Kt 2.0) (s60 e-150 w-90) | Z shear | 0.94 | 6.25 | 6.62 | 4 | OK |
| 20 | yaw-stall sweep: rib root: the ribs' force fed into the plate across the layers over the 6 mm run-out (Kt 2.0) (s105 e5 w35, fingertip) | Z shear | 3.30 | 6.25 | 1.89 | 3 | **FAIL** |
| 21 | hand push 5 N: rib root: the ribs' force fed into the plate across the layers over the 6 mm run-out (Kt 2.0) (s60 e-30 w0, fingertip) | Z shear | 2.53 | 6.25 | 2.47 | 3 | **FAIL** |
| 22 | weight x2 (sustained): far elbow-pilot row x 65.6, plate + ribs, out of plane (Kt 2.0) (s90 e-150 w-90) | XY | 1.29 | 25.00 | 19.37 | 4 | OK |
| 23 | yaw-stall sweep: far elbow-pilot row x 65.6, plate + ribs, out of plane (Kt 2.0) (s120 e-25 w50, fingertip) | XY | 4.20 | 25.00 | 5.95 | 3 | OK |
| 24 | hand push 5 N: far elbow-pilot row x 65.6, plate + ribs, out of plane (Kt 2.0) (s90 e0 w0, fingertip) | XY | 3.50 | 25.00 | 7.14 | 3 | OK |
| 25 | weight x2 (sustained): far lead notch x 67.4-69.5, plate + ribs (Kt 2.5; 0.94 M) (s90 e-150 w-90) | XY | 1.50 | 25.00 | 16.66 | 4 | OK |
| 26 | yaw-stall sweep: far lead notch x 67.4-69.5, plate + ribs (Kt 2.5; 0.94 M) (s120 e-25 w50, fingertip) | XY | 4.88 | 25.00 | 5.12 | 3 | OK |
| 27 | hand push 5 N: far lead notch x 67.4-69.5, plate + ribs (Kt 2.5; 0.94 M) (s90 e0 w0, fingertip) | XY | 4.07 | 25.00 | 6.14 | 3 | OK |
| 28 | weight x2 (sustained): window rails 6.85 x 16 at the far window end, tab rows as pins, 0.30 of the twist (Kt 2.5) (s65 e-150 w-90) | XY | 2.07 | 25.00 | 12.07 | 4 | OK |
| 29 | yaw-stall sweep: window rails 6.85 x 16 at the far window end, tab rows as pins, 0.30 of the twist (Kt 2.5) (s105 e5 w35, fingertip) | XY | 7.21 | 25.00 | 3.47 | 3 | OK |
| 30 | hand push 5 N: window rails 6.85 x 16 at the far window end, tab rows as pins, 0.30 of the twist (Kt 2.5) (s65 e25 w0, fingertip) | XY | 5.54 | 25.00 | 4.51 | 3 | OK |
| 31 | weight x2 (sustained): window rails: interlayer shear at the rib's root (z 0) (s135 e-150 w-90) | Z shear | 0.09 | 6.25 | 68.73 | 4 | OK |
| 32 | yaw-stall sweep: window rails: interlayer shear at the rib's root (z 0) (s155 e-120 w-15, fingertip) | Z shear | 0.32 | 6.25 | 19.66 | 3 | OK |
| 33 | hand push 5 N: window rails: interlayer shear at the rib's root (z 0) (s135 e-45 w0, fingertip) | Z shear | 0.24 | 6.25 | 26.46 | 3 | OK |
| 34 | weight x2 (sustained): elbow MG996R tab screw pull-out (L 9, Ø2.6) (s10 e-150 w-90) | Z shear | 0.40 | 6.25 | 15.69 | 4 | OK |
| 35 | yaw-stall sweep: elbow MG996R tab screw pull-out (L 9, Ø2.6) (s135 e-90 w-25, fingertip) | Z shear | 1.49 | 6.25 | 4.18 | 3 | OK |
| 36 | hand push 5 N: elbow MG996R tab screw pull-out (L 9, Ø2.6) (s170 e-80 w0, fingertip) | Z shear | 1.02 | 6.25 | 6.10 | 3 | OK |
| 37 | weight x2 (sustained): notch -> pilot strip 1.79: splitting, snug preload 150 N + screw tension (s10 e-150 w-90) | XY | 2.00 | 25.00 | 12.53 | 4 | OK |
| 38 | yaw-stall sweep: notch -> pilot strip 1.79: splitting, snug preload 150 N + screw tension (s135 e-90 w-25, fingertip) | XY | 2.89 | 25.00 | 8.64 | 3 | OK |
| 39 | hand push 5 N: notch -> pilot strip 1.79: splitting, snug preload 150 N + screw tension (s170 e-80 w0, fingertip) | XY | 2.51 | 25.00 | 9.97 | 3 | OK |
| 40 | spec §8: tab screws driven snug: notch -> pilot strip 1.79: splitting at 150 N | XY | 1.67 | 25.00 | 14.97 | 4 | OK |
| 41 | spec §8 proof (2): 16 N at 175 mm, bar at 60°: window rails | XY | 12.46 | 25.00 | 2.01 | 2 | OK |
| 42 | spec §8 proof (2): 16 N at 175 mm, bar at 60°: far pilot row | XY | 5.36 | 25.00 | 4.66 | 2 | OK |
| 43 | spec §8 proof (2): 16 N at 175 mm, bar at 60°: far lead notch | XY | 6.24 | 25.00 | 4.01 | 2 | OK |
| 44 | spec §8 proof (2): 16 N at 175 mm, bar at 60°: rib root | Z shear | 5.84 | 6.25 | 1.07 | 2 | **FAIL** |
| 45 | spec §8 proof (2): 16 N at 175 mm, bar at 60°: run-out foot | XY | 7.30 | 25.00 | 3.42 | 2 | OK |
| 46 | spec §8 proof (2): 16 N at 175 mm, bar at 60°: x 15 bending | XY | 10.98 | 25.00 | 2.28 | 2 | OK |
| 47 | spec §8 proof (2): 16 N at 175 mm, bar at 60°: plate torsion | Z shear | 2.61 | 6.25 | 2.39 | 2 | OK |
| 48 | spec §8 proof (2): 16 N at 175 mm, bar at 60°: shoulder-horn joint | Z shear | 2.78 | 6.25 | 2.25 | 2 | OK |
| 49 | spec §8 proof (2): 16 N at 175 mm, bar at 60°: elbow tab screw pull-out | Z shear | 2.48 | 6.25 | 2.52 | 2 | OK |
| 50 | spec §8 proof (2): 16 N at 175 mm, bar at 60°: notch strip splitting | XY | 3.70 | 25.00 | 6.75 | 2 | OK |
| 51 | spec §8 proof (1): 1 kg at the elbow axis, in plane: in-plane bending at x 15 (Kt 2) | XY | 0.87 | 25.00 | 28.88 | 2 | OK |

**Lowest SF 1.89 (required 3): rib root, yaw stall (row 20).** Rows 21 (2.47) and 44 (1.07 at the §8 bench test) fail
too. Every other row passes. Next lowest: x 15 3.42 (row 10), rails 3.47 (row 29), plate torsion 3.72 (row 13).

### Advisory rows (not in the verdict)

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| yaw-stall sweep: window rails with round 4's twist share (0.15 instead of 0.30) | XY | 6.50 | 25.00 | 3.85 | 3 |
| yaw-stall sweep with a 15 kgf.cm clone MG996R: window rails | XY | 9.84 | 25.00 | 2.54 | 3 |
| yaw-stall sweep with a 15 kgf.cm clone MG996R: x 15 over the pocket | XY | 9.96 | 25.00 | 2.51 | 3 |
| yaw-stall sweep, tab screws over-tightened to 300 N: notch -> pilot strip 1.79: splitting | XY | 4.56 | 25.00 | 5.48 | 3 |

Why each one is advisory:
- **Rails at round 4's twist share (3.85).** For comparison.
- **Clone MG996R (2.54 rails, 2.51 x 15).** A 15 kgf·cm clone is not a spec case (01 N1).
- **Over-tightened tab screws (5.48).**

## Required change (FAIL)

**`RIB_TAPER` 6 → 12.** Nothing else moves:
- `RIB_X0` stays at 64.2; the run-out meets the back face at x 52.2, sloping at 27°.
- The rib root's stress scales with 6 / RIB_TAPER, from the script's what-if:

  | RIB_TAPER | Run-out foot | Yaw | Hand | Weight ×2 | §8 bench | Arm-up test | Plate at the foot |
  |---|---|---|---|---|---|---|---|
  | 6 (as drawn) | x 58.2 | **1.89** | 2.47 | 6.62 | **1.07** | **1.34** | 4.51 |
  | 10 | x 54.2 | 3.15 | 4.11 | 11.03 | **1.78** | 2.24 | 4.44 |
  | **12** | x 52.2 | **3.78** | 4.94 | 13.23 | **2.14** | 2.69 | 4.40 |

- **Printing.** It is a ramp rising in print, so it prints without support.
- **Clearance.** Check it with `assembly_check.py` over the shoulder's 0–180°. The ribs gain only 0–3 mm of height
  between x 52.2 and 58.2.
- **Result.** Every row then reaches its required SF, and the verdict becomes NEEDS_TEST.

## Proof test (spec §8)

- **(1) Horn in a vice, 1 kg at the elbow axis, in plane.** Deflection 0.06 mm (< 2 mm); in-plane stress SF 28.9.
  Still matches.
- **(2) Horn in a vice, elbow MG996R fitted, bar at 60°, 16 N at 175 mm along the elbow shaft.**
  - Ratios to the yaw-stall service value: rails 1.73, rib root 1.77, x 15 1.50, plate torsion 1.55, tab screw 1.66,
    horn joint 1.90.
  - **As drawn, the test would overload the rib root** (SF 1.07).
  - **With `RIB_TAPER` 12 it matches the design.** Every row is then ≥ 2: rails 2.01, rib root 2.14, x 15 2.28. No
    change to §8 is needed.
- **The turntable/base arm-up test (11.5 N at the fingertips, arm straight up)** loads this link too:
  - x 15 at 1.75 ×, SF 1.96;
  - rails 2.41;
  - rib root 1.34 as drawn, 2.69 with the fix.

  The x 15 figure is 2 % under the proof margin, which is acceptable: 11 N would leave the turntable's window bottom at
  only 1.43 ×.

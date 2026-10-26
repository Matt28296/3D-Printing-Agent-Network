VERDICT: NEEDS_TEST

# Strength check: 20261025-arm-turntable (links round 5, independent re-check of the round-5 solid)

strength-analyst (independent review: I did not design this part) · 2026-10-26 ·
`python3 jobs/20261025-arm-turntable/strength_calc.py` from the project root (about 15 s). It reads every link's
`model.py`, `tools/hobby_parts.py`, the claw's `claw_frame.py`, each part's `geometry.json` and the assembly's
`torque_budget.json`, sweeps 47 170 arm poses and prints every row below.

## Summary

- **NEEDS_TEST.** Every row reaches its required SF. The lowest is **3.26** (3 required): the upright's front face at the
  window bottom (Z 50.6) under the yaw-stall sweep (s75 e10 w−50, fingertip).
- **Round 4's two failures are fixed.**
  - **Disc-horn anti-rotation:** 4 × M2 × 8 with 5.2 mm in the disk.
    - **5.06** at r 7, the smallest hole circle BUILD_GUIDE allows (6.51 at the assumed r 9).
    - BUILD_GUIDE's fallbacks also pass: 4 at r 5 gives **3.61**, 3 at r 7 gives **3.80**.
  - **Upright with the 90 mm gussets:** window bottom **3.26**, lower pilot row **3.45**, notch level 4.34.
- **The section model matches the round-5 CAD exactly** (I_xx 36 173 / 13 735 / 10 558 / 9185 mm⁴ at Z 28 / 50.6 / 55.5
  / 60.5). Round 4's script compared it with the 70 mm-gusset CAD.
- **New failure paths, checked:**
  - the M2 × 8 bite in the 30-layer solid bottom (bearing rows 1–3);
  - the 90 mm gussets' sloping free edge in compression (buckling, SF 18.5);
  - the gussets' cut-off top, which is free and unloaded.
- **One condition is outside this part's CAD: the solid bottom is a slicer setting.**
  - `print_requirements.json` asks for ≥ 30 bottom layers and ≥ 6 mm, which is right.
  - This job's slice files are still round 4's, with 5 bottom layers. If it were sliced that way, the screws would bite
    1 mm of skin and 40 % gyroid: SF 2.61 (advisory).
  - Re-slice before the gcode-auditor.
- **Spec §8:** both tests still match the design.
  - (1) arm-up push, 11.5 N: window bottom 1.49 ×, every row SF ≥ 2.10.
  - (2) disc-horn test, 34 N: anti-rotation SF ≥ 2.39 with any hole circle BUILD_GUIDE allows.

## What changed since round 4

**Design (round 5)**

- **Anti-rotation:** 4 × M2 × 8 replace 2 × M2 × 6, in opposite pairs on one circle at r ≥ 7. Pilots Ø1.5, drilled 6 mm
  into the disk at assembly.
- **Disk bottom:** 30 solid layers, 6 mm solid.
- **Gussets:** GUSSET_H 70 → 90, cut off at the upright's top (Z 97.3), 4.4 mm deep there. The toe is unchanged at
  r 47.76.
- **Mass:** 90.7 cm³ (+1.5). The upper link and forearm are heavier (ribs); every centre of mass is re-measured here.

**Method (this review)**

- **Anti-rotation verdict row.** Taken at r 7, the BUILD_GUIDE minimum, not at the assumed r 9, because the disc's
  holes aren't measured. BUILD_GUIDE's fallbacks are rows too.
- **CAD sections** re-measured on the round-5 solid. Round 4's what-if machinery is removed.

## Load cases

Spec §4 cases, all at 40 °C.

| Case | Load | Duration | How it is applied here |
|---|---|---|---|
| Base servo stall | 1079 N·mm about Z (datasheet) | short-term | Anti-rotation screws in bearing, friction ignored |
| Shoulder servo stall | 1079 N·mm about Y | short-term | Far tab pilot bearing; notch strip tear-out |
| Arm + camera weight (SYS-04, SYS-05) | weight ×2 sweep | sustained | Upright, disk, clamped disc-horn joint, SF 4 |
| Base-yaw stall into a side obstacle | sweep, F = 1079 / R | short-term | SF 3 |
| Hand push 5 N | sweep, ±Y | short-term | SF 3 |
| Assembly | M3 × 12 tab screws snug, 150 N | sustained | Notch strip splitting |

The sweep is the same as the base's: 47 170 poses, the ring ignored (conservative for the disc-horn joint, no effect on
the upright).

## Assumptions

**Masses and loads**
- Solid parts × 1.27 g/cm³ with build123d centres of mass re-measured on the round-5 solids; servos, horns and cable
  allowances; 50 g at the fingertips.
- ×2 dynamic on the weight.
- The model reproduces `torque_budget.json`: 706 N·mm with the arm straight out; overhung 240 / 161 / 108 N·mm.

**Upright sections** (Z 28 root, 50.6 window bottom, 55.5 lower pilot row, 60.5 notch level)
- Built from the parameters with the 90 mm gussets (depth at height z: 23 × (1 − (z − 24.5) / 90)). They match the CAD
  sections within 0.1 %.
- **Front face:** σ = Kt × [f·M_x·c / I_xx + M_z couple through the window columns + f·M_y·x_corner / I_yy].
  - All three moments come from the same pose.
  - f is the share of M_x that passes between the tab edges.
- **Kt:** 2.5 at the window corners, the notch and the root's washer gap; 2.0 at the pilot row; 2.5 at the gusset toe.
- The upright prints standing, so all of this is across the layers: 12.5 MPa, and 6.25 MPa in shear.

**Gusset free edge (new).** Plate buckling with one free edge:

σ_cr = 0.425 π² E / (12 (1 − ν²)) × (t / b)² = 21.7 MPa

- b is the root depth, 23 mm (the deepest point, conservative); t is 4 mm.
- It is set against the toe's stress without Kt.

**Disc-horn joint**
- **Clamp:** washer pull-through for S = M_h / 12.5 (the disk tips on the disc's edge).
- **Disk at the disc's edge:** rigid boss in a plate, K 0.876.
- **Disk strip under the upright:** Kt 2.0.
- **Anti-rotation:** the whole base stall goes into the screws, friction ignored.
  - Bearing on the Ø1.5 pilot over the 5.2 mm engaged (M2 × 8 through the 2.8 mm horn).
  - The bite is in solid plastic: the pilot reaches Z 22.5 and the solid bottom ends at Z 22.5.
  - The screw's force is tangential, so no free edge lies in its way. The 2.45 mm between an r 5 pilot and the clamp
    hole is radial, so it does not tear out.

**Shoulder tab screws.**
- M3 × 12 + Ø7 washer: 7 mm in the 7 mm upright.
- Screw tension S = 0.6·M_x / 14.85 + M_z / (2 × 51.25) + F_y / 4.
- Splitting uses Lamé with 150 N + S, across the layers.

**Temperature.** 40 °C, servo cases up to 45 °C, against PETG softening at about 70 °C: margin ≥ 25 °C, OK.

## Allowables and sources

`library/materials.csv` has only its header, and no job has a datasheet in `inputs/`, so these are the strength-checks
**placeholder** PETG values and **NEEDS_TEST is the best verdict possible**.

| Quantity | Value | Source |
|---|---|---|
| Tension / bending along the layers (XY): disk | 25 MPa | strength-checks placeholder, PETG |
| Tension / bending across the layers (Z): upright, gussets | 12.5 MPa | placeholder × 0.5 |
| Shear in-plane / interlayer | 12.5 / 6.25 MPa | 0.5 × the normal value (Tresca), assumption |
| Bearing | 25 MPa | in-plane value |
| E, ν | 1800 MPa, 0.35 | skill table; ν assumed |
| Kt | 2.5 sharp corner, window corner, notch; 2.0 hole or 45° wedge | skill; agent rule Kt ≥ 2 |

Required SF: 3 short-term, 4 sustained, 2 at a proof load (1.5 × service).

## Results (copied from `strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | base stall 1079 N.mm (yaw stall): disc-horn anti-rotation 4 x M2 x 8 at r 7 (the BUILD_GUIDE minimum; r 9 assumed), bearing in the disk's solid bottom, L 5.2, friction ignored | bearing | 4.94 | 25.00 | 5.06 | 3 | OK |
| 2 | base stall 1079 N.mm (yaw stall): disc-horn anti-rotation, 4 in opposite pairs at r 5 (BUILD_GUIDE fallback for r 5-7): bearing, L 5.2 | bearing | 6.92 | 25.00 | 3.61 | 3 | OK |
| 3 | base stall 1079 N.mm (yaw stall): disc-horn anti-rotation, 3 on one circle at r 7 (BUILD_GUIDE fallback): bearing, L 5.2 | bearing | 6.59 | 25.00 | 3.80 | 3 | OK |
| 4 | weight x2 (sustained): clamped base-horn joint: disk tips on the Ø25 disc's edge, clamp S 136 N, Ø9 washer pull-through, floor 8 (s0 e0 w0) | Z shear | 0.60 | 6.25 | 10.38 | 4 | OK |
| 5 | yaw-stall sweep: clamped base-horn joint: disk tips on the Ø25 disc's edge, clamp S 198 N, Ø9 washer pull-through, floor 8 (s70 e25 w-65, fingertip) | Z shear | 0.88 | 6.25 | 7.14 | 3 | OK |
| 6 | hand push 5 N: clamped base-horn joint: disk tips on the Ø25 disc's edge, clamp S 150 N, Ø9 washer pull-through, floor 8 (s90 e0 w0, fingertip) | Z shear | 0.66 | 6.25 | 9.42 | 3 | OK |
| 7 | weight x2 (sustained): disk at the disc horn's edge (rigid boss r 12.5, t 8; M 1702) | XY | 1.86 | 25.00 | 13.41 | 4 | OK |
| 8 | weight x2 (sustained): disk strip under the upright, b 66 t 8 (Kt 2.0; M_x 576) | XY | 1.64 | 25.00 | 15.27 | 4 | OK |
| 9 | yaw-stall sweep: disk at the disc horn's edge (rigid boss r 12.5, t 8; M 2476) | XY | 2.71 | 25.00 | 9.22 | 3 | OK |
| 10 | yaw-stall sweep: disk strip under the upright, b 66 t 8 (Kt 2.0; M_x 1968) | XY | 5.59 | 25.00 | 4.47 | 3 | OK |
| 11 | hand push 5 N: disk at the disc horn's edge (rigid boss r 12.5, t 8; M 1875) | XY | 2.05 | 25.00 | 12.17 | 3 | OK |
| 12 | hand push 5 N: disk strip under the upright, b 66 t 8 (Kt 2.0; M_x 1875) | XY | 5.33 | 25.00 | 4.69 | 3 | OK |
| 13 | weight x2 (sustained): upright Z 28.0, front face at the washer gap \|X\| < 6, no wedge (Kt 2.5; M_x 715, M_y 1602, M_z 0; s0 e0 w0) | Z | 0.77 | 12.50 | 16.24 | 4 | OK |
| 14 | weight x2 (sustained): upright Z 28.0, gusset toe (Kt 2.5; s0 e-150 w-90) | Z | 1.07 | 12.50 | 11.72 | 4 | OK |
| 15 | yaw-stall sweep: upright Z 28.0, front face at the washer gap \|X\| < 6, no wedge (Kt 2.5; M_x 1968, M_y 1438, M_z 1113; s75 e10 w-50, fingertip) | Z | 1.38 | 12.50 | 9.05 | 3 | OK |
| 16 | yaw-stall sweep: upright Z 28.0, gusset toe (Kt 2.5; s75 e10 w-50, fingertip) | Z | 2.94 | 12.50 | 4.26 | 3 | OK |
| 17 | hand push 5 N: upright Z 28.0, front face at the washer gap \|X\| < 6, no wedge (Kt 2.5; M_x 1840, M_y 262, M_z 375; s70 e5 w10, fingertip) | Z | 1.02 | 12.50 | 12.23 | 3 | OK |
| 18 | hand push 5 N: upright Z 28.0, gusset toe (Kt 2.5; s90 e0 w0, fingertip) | Z | 2.81 | 12.50 | 4.44 | 3 | OK |
| 19 | weight x2 (sustained): upright Z 50.6, front face (Kt 2.5; M_x 725, M_y 1602, M_z 0; s0 e0 w0) | Z | 1.46 | 12.50 | 8.58 | 4 | OK |
| 20 | yaw-stall sweep: upright Z 50.6, front face (Kt 2.5; M_x 1837, M_y 1336, M_z 1118; s75 e10 w-50, fingertip) | Z | 3.83 | 12.50 | 3.26 | 3 | OK |
| 21 | hand push 5 N: upright Z 50.6, front face (Kt 2.5; M_x 1651, M_y 364, M_z 628; s65 e0 w0, fingertip) | Z | 3.03 | 12.50 | 4.12 | 3 | OK |
| 22 | weight x2 (sustained): upright Z 55.5, front face (Kt 2.0; M_x 727, 1.00 of it between the tab screws, M_y 1602, M_z 0; s0 e0 w0) | Z | 1.51 | 12.50 | 8.28 | 4 | OK |
| 23 | yaw-stall sweep: upright Z 55.5, front face (Kt 2.0; M_x 1808, 1.00 of it between the tab screws, M_y 1313, M_z 1119; s75 e10 w-50, fingertip) | Z | 3.63 | 12.50 | 3.45 | 3 | OK |
| 24 | hand push 5 N: upright Z 55.5, front face (Kt 2.0; M_x 1709, 1.00 of it between the tab screws, M_y 240, M_z 404; s75 e0 w0, fingertip) | Z | 3.01 | 12.50 | 4.15 | 3 | OK |
| 25 | weight x2 (sustained): upright Z 60.5, front face (Kt 2.5; M_x 719, 0.70 of it between the tab screws, M_y 1602, M_z 0; s0 e0 w0) | Z | 1.35 | 12.50 | 9.29 | 4 | OK |
| 26 | yaw-stall sweep: upright Z 60.5, front face (Kt 2.5; M_x 1774, 0.70 of it between the tab screws, M_y 1291, M_z 1115; s75 e10 w-50, fingertip) | Z | 2.88 | 12.50 | 4.34 | 3 | OK |
| 27 | hand push 5 N: upright Z 60.5, front face (Kt 2.5; M_x 1723, 0.70 of it between the tab screws, M_y 104, M_z 134; s85 e0 w5, fingertip) | Z | 2.61 | 12.50 | 4.79 | 3 | OK |
| 28 | weight x2 (sustained): upright torsion at the root, open section (T 0) | Z shear | 0.00 | 6.25 | inf | 4 | OK |
| 29 | yaw-stall sweep: upright torsion at the root, open section (T 1240) | Z shear | 1.02 | 6.25 | 6.11 | 3 | OK |
| 30 | hand push 5 N: upright torsion at the root, open section (T 1079) | Z shear | 0.89 | 6.25 | 7.02 | 3 | OK |
| 31 | weight x2 (sustained): gusset's free edge in compression: buckling, t 4 / depth 23 (sigma_cr 21.7 MPa taken as the allowable) | Z | 0.43 | 21.69 | 50.83 | 4 | OK |
| 32 | yaw-stall sweep: gusset's free edge in compression: buckling, t 4 / depth 23 (sigma_cr 21.7 MPa taken as the allowable) | Z | 1.17 | 21.69 | 18.47 | 3 | OK |
| 33 | hand push 5 N: gusset's free edge in compression: buckling, t 4 / depth 23 (sigma_cr 21.7 MPa taken as the allowable) | Z | 1.13 | 21.69 | 19.27 | 3 | OK |
| 34 | shoulder stall 1079 N.mm: far tab pilot bearing, F 13.1 N | bearing | 0.87 | 25.00 | 28.79 | 3 | OK |
| 35 | shoulder stall 1079 N.mm: notch -> pilot strip 1.74: tear-out (planes across the layers), F 13.1 N | Z shear | 0.65 | 6.25 | 9.63 | 3 | OK |
| 36 | weight x2 (sustained): shoulder MG996R tab screw pull-out, S 26 N (L 7, Ø2.6; s0 e-150 w-90) | Z shear | 0.45 | 6.25 | 13.90 | 4 | OK |
| 37 | weight x2 (sustained): notch strip 1.74: splitting, snug preload 150 N + 26 N (horizontal pilot in a standing wall: taken across the layers) | Z | 2.55 | 12.50 | 4.90 | 4 | OK |
| 38 | yaw-stall sweep: shoulder MG996R tab screw pull-out, S 82 N (L 7, Ø2.6; s80 e-5 w-40, fingertip) | Z shear | 1.44 | 6.25 | 4.35 | 3 | OK |
| 39 | yaw-stall sweep: notch strip 1.74: splitting, snug preload 150 N + 82 N (horizontal pilot in a standing wall: taken across the layers) | Z | 3.37 | 12.50 | 3.71 | 3 | OK |
| 40 | hand push 5 N: shoulder MG996R tab screw pull-out, S 71 N (L 7, Ø2.6; s75 e0 w0, fingertip) | Z shear | 1.25 | 6.25 | 5.01 | 3 | OK |
| 41 | hand push 5 N: notch strip 1.74: splitting, snug preload 150 N + 71 N (horizontal pilot in a standing wall: taken across the layers) | Z | 3.21 | 12.50 | 3.89 | 3 | OK |
| 42 | spec §8: tab screws driven snug: notch strip 1.74: splitting at 150 N (across the layers) | Z | 2.18 | 12.50 | 5.74 | 4 | OK |

**Lowest SF 3.26 (required 3): upright window bottom, front face, yaw stall (row 20).** Next: lower pilot row 3.45
(row 23), anti-rotation at r 5 3.61 (row 2), notch strip splitting 3.71 (row 39).

### Advisory rows (not in the verdict)

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| base stall 1079 N.mm: anti-rotation 4 x M2 x 8 at the assumed r 9 | bearing | 3.84 | 25.00 | 6.51 | 3 |
| base stall 1079 N.mm: if the slice kept round 4's 5 bottom layers: 4 x M2 x 8 at r 7, 1 mm of skin + 40 % gyroid (x 0.4) over the rest | bearing | 9.59 | 25.00 | 2.61 | 3 |
| yaw-stall sweep with a 15 kgf.cm clone MG996R: upright window bottom, front | Z | 5.23 | 12.50 | 2.39 | 3 |
| yaw-stall sweep, tab screws over-tightened to 300 N: notch strip 1.74: splitting | Z | 5.55 | 12.50 | 2.25 | 3 |

Why each one is advisory:
- **Anti-rotation at the assumed r 9 (6.51).** For comparison.
- **The slice ignoring the 30 solid layers (2.61).** Not the design: `print_requirements.json` asks for 30 layers and
  6 mm. The current slice files (round 4's, 5 layers) must be redone.
- **Clone MG996R at the window bottom (2.39).** A 15 kgf·cm clone is not a spec case (01 N1).
- **Over-tightened tab screws (2.25).** Drive them snug, no harder.

## Proof test (spec §8): still matches the design

- **(1) Arm-up push: 11.5 N sideways at the fingertips, 1 min each way.**
  - Ratios to the yaw-stall service value:

    | Check | Ratio | SF at the test |
    |---|---|---|
    | Window bottom | 1.49 | 2.19 |
    | Lower pilot row | 1.64 | 2.10 |
    | Notch level | 1.83 | 2.37 |
    | Root front | 1.47 | 6.16 |
    | Gusset toe | 1.97 | 2.16 |
    | Base-horn joint and disk | 1.59 | 4.49 |
    | Disk strip | 2.00 | 2.24 |
    | Shoulder tab screw | 1.75 | 2.49 |

  - Every row stays at SF ≥ 2.10.
  - The upright's torsion is not tested (0.09 ×; SF 6.1).
  - 11 N would bring the window bottom down to 1.43 ×. Keep 11.5 N.
  - The same push takes the upper link's x 15 to SF 1.96; see that job.
- **(2) Disc-horn test: 34 N tangential at the rim.** That is 1632 N·mm, 1.51 × the base stall.
  - Anti-rotation bearing SF 3.35 at r 7, 2.39 with 4 at r 5, 2.51 with 3 at r 7: all ≥ 2.
  - A datasheet servo gives way first at 22.5 N, a 15 kgf·cm clone at 30.7 N. Either way, the screws then carry the
    most the servo can apply.

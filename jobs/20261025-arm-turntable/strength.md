VERDICT: FAIL

# Strength check: 20261025-arm-turntable (round 5, independent re-check)

strength-analyst (independent review: I did not design this part) · 2026-10-26 ·
`python3 jobs/20261025-arm-turntable/strength_calc.py` (plain Python, no build123d, about 15 s). It reads every link's
`model.py`, `tools/hobby_parts.py`, the claw's `claw_frame.py`, each part's `geometry.json` and the assembly's
`torque_budget.json`, sweeps 47 170 arm poses and prints the tables below.

## Summary

- **FAIL.** Lowest SF **2.00** (3 required): the disc horn's two M2 × 6 anti-rotation screws, bearing in the disk under
  the base servo's stall. This assumes they sit at r 9 and ignores friction; with the clamp's friction credited it is
  2.92.
- The upright's front face also fails under the yaw-stall sweep, at the same pose (s75 e10 w-50, fingertip):
  - window bottom (Z 50.6): SF **2.80**;
  - lower tab-pilot row (Z 55.5): SF **2.83**.
- Everything else is at SF 3.38 or above. The hand-push rows pass (3.39 or above).
- **Changes that pass:**
  1. **4 × M2 × 8** through four of the disc horn's holes on one circle: SF 6.51 at r 9, 5.06 at r 7;
  2. **GUSSET_H 70 → 90**: window bottom 3.27, pilot row 3.46.
- With both changes every row reaches its required SF. The best verdict is then NEEDS_TEST, because the allowables are
  placeholders.
- **Proof test:** two parts of §8 cannot be run as written:
  - §8 (1): the shoulder servo cannot hold 1 kg at the elbow axis (1335–1589 N·mm against its 1079 N·mm stall);
  - the elbow-at-90° repeat: the base servo slips at 5.9 N.

  The replacement is under "Proof test".

## What changed since round 4

**Design changes this round**

- **Turntable mounting.**
  - The disk's flat underside sits on the base servo's Ø25 disc horn, with no pocket.
  - It is clamped by an M3 × 14 + Ø9 × 0.8 washer, 4.6 mm into the spline (01 S2).
  - Two M2 × 6 anti-rotation screws go through the disc's holes.
- **Support ring.** It runs 0.4 mm under the disk with PTFE tape, so it catches the disk after 0.52° of tilt (SYS-05).
- **Lead notches** with 45° tops at both ends of the shoulder MG996R window: notch-to-pilot strip 1.84 CAD, 1.74 behind
  the thread.
- **Claw and camera.** 224.1 g beyond the wrist horn with solid parts ("camera, solid"; 208.6 g sliced).
- **The camera's sideways weight** (SYS-04) bends the upright about X in every pose. At the upright sections, weight ×2
  gives M_x 702–711 N·mm.

**Method changes in this review**

- **New pose model.** The pose model is my own, but it reproduces `torque_budget.json` exactly:
  - end effector 224.1 g;
  - overhung moments 239 / 161 / 108 N·mm;
  - 692 N·mm on the base horn with the arm straight out.
- **Stall torque.** MG996R stall 1079 N·mm (11 kgf·cm datasheet, 01 N1); the specs say 1000.
- **Contact points.** Yaw-stall and hand-push forces act at the fingertips and at either end of the camera.

**Why the lowest SF fell from 4.29 (round 4) to 2.00**

1. **Anti-rotation screws.**
   - The disc horn's screws sit at about r 9 mm, much closer to the axis than the double-arm horn's at r 15. Round 4
     gave those SF 6.00.
   - They engage only 3.2 mm (M2 × 6 through the 2.8 mm horn).
   - So the base stall bears 60 N on each.
2. **The upright window region now combines three moments of the same pose.** Round 4 checked each of these in its own
   row:
   - **M_x:** bending across the upright;
   - **M_y:** in-plane bending at the window corner;
   - **M_z:** the servo's twist, which reaches the two columns beside the window as a couple.

   Combining them, with this round's heavier loads, takes the window bottom from round 4's 4.52 to 2.80. About 75 % of
   that stress is M_x, 19 % the M_z couple and 6 % M_y.

## Load cases

Spec §4 cases, all at 40 °C:

| Case | Load | Duration | How it is applied here |
|---|---|---|---|
| Shoulder servo stall reaction | 1079 N·mm about Y | short-term | Far tab pilot bearing; notch strip tear-out |
| Base servo stall | 1079 N·mm about Z | short-term | Anti-rotation screws in bearing, friction ignored |
| Arm + camera weight out of the upright's plane (SYS-04), and everything on the base horn (SYS-05) | ×2 dynamic | sustained | "Weight ×2" sweep, SF 4: upright, disk and the clamped disc-horn joint |
| Base-yaw stall into a side obstacle | F = 1079 / R, tangential, at the fingertips or a camera end | short-term | "Yaw-stall" sweep, SF 3 |
| Sideways hand push | 5 N along ±Y at the same points | short-term | "Hand push" sweep, SF 3 |
| Assembly | M3 × 12 tab screws driven snug | sustained | Notch strip splitting at 150 N |

**How the sweep is set up**

- **Poses.** Shoulder 0–180, elbow -150 … +30, wrist ±90, in 5° steps. That gives 47 170 poses with the elbow, wrist
  and fingertips above the desk.
- **Yaw stall.** The force is scaled down wherever a pitch servo would back-drive first.
- **Hand push.** The force is capped where the yaw servo would back-drive.
- **Combining with weight.** Both contact cases add the static weight, component by component, taking the worse sign of
  each.
- **Ring ignored.** Every overturning moment is taken through the disc-horn joint. This is conservative for the joint
  and has no effect on the upright.

## Assumptions

**Masses and loads**

- **Masses:**
  - each `geometry.json` volume × 1.27 g/cm³, as solid parts;
  - build123d centres of mass;
  - servos and horns from `hobby_parts.py`, plus cable allowances;
  - 50 g payload at the fingertips.
- **Dynamic factor:** ×2 on the weight.

**Upright sections**

- Taken at:
  - Z 28: the root, just above the 45° wedges;
  - Z 50.6: the window bottom;
  - Z 55.5: the lower tab-pilot row;
  - Z 60.5: the notch level.
- Built from the parameters. I_xx is within 0.1 % of the CAD sections: 35 229 / 10 648 / 7644 / 6129 mm⁴.
- **Front-face stress:**

  σ = Kt × [f·M_x·c / I_xx + (M_z couple through the window columns) + f·M_y·x_corner / I_yy]

  - The M_z couple acts as ±M_z / (2 × 24.25) at the tab pilots, over (60.5 − z).
  - f is the share of M_x that passes a section between the tab edges. Each tab pries about one long edge with its two
    screws in tension, so f is 1.0 below the tabs and 0.70 at the axis height.
- **Gusset toe:** Kt 2.5, at the sharp corner with the disk.
- **Kt:** 2.5 at the window corners, the notch and the root's washer gap (where there is no wedge); 2.0 at the pilot
  row (hole).
- **All three moments come from the same pose**, worst pose kept.
- The upright prints standing, so every upright stress runs across the layers: 12.5 MPa, and 6.25 MPa in shear.

**Disc-horn joint**

- **Clamp.** The overturning moment tips the disk about the disc's edge (r 12.5). The clamp must therefore hold
  S = M_h / 12.5, and its capacity is Ø9 washer pull-through on the 8 mm disk (interlayer shear).
- **Disk bending at the disc's edge.** Treated as a rigid central boss in a circular plate:
  - σ = K·M / (b·t²);
  - K = 0.876 (b 12.5, a 40, simply supported; derived for this review; a clamped edge gives 0.785).
- **Disk strip under the upright:** b 66, t 8, Kt 2.0.
- **The clamp screw's thread in the metal spline** is bought hardware. At most 198 N holds there, provided the screw
  does not bottom out (01 S2).

**Anti-rotation screws**

- The whole base stall (1079 N·mm) goes into the two screws, with friction ignored.
- The hole circle is **assumed r 9**:
  - neither `hobby_parts.py` nor a measurement gives the stock Ø25 disc's hole circle;
  - a web search found only aftermarket metal 25T horns, which were not used.
- Bearing is taken on the Ø1.5 pilot over the 3.2 mm in the disk.
- Sensitivity rows cover r 7 and r 10.5, and the clamp's friction (μ 0.2 on the 150 N left of the preload: 340 N·mm).

**Shoulder MG996R tab screws**

- M3 × 12 + Ø7 washer: 7 mm engaged in the 7 mm upright.
- Screw tension S = 0.6·M_x / 14.85 + M_z / (2 × 51.25) + F_y / 4. 60 % of the twist goes to the busier tab.
- The pilots are horizontal in a standing wall, so pull-out and the strip's splitting are taken across the layers.
- Splitting uses Lamé with 150 N preload plus the screw tension; 300 N is a sensitivity row.

**Upright torsion.** Open thin-walled section: τ = T·t / J.

**Temperature.** 40 °C, and servo cases up to 45 °C, against PETG softening at about 70 °C. The margin is 25 °C or more,
which is OK.

## Allowables and sources

`library/materials.csv` has only its header, and no job has a datasheet in `inputs/`. These are the strength-checks
**placeholder** values for PETG, so **NEEDS_TEST is the best verdict possible**.

| Quantity | Value | Source |
|---|---|---|
| Tension / bending along the layers (XY): disk | 25 MPa | strength-checks placeholder, PETG |
| Tension / bending across the layers (Z): upright | 12.5 MPa | placeholder × 0.5 |
| Shear in-plane / interlayer | 12.5 / 6.25 MPa | 0.5 × the normal value (Tresca), my assumption |
| Bearing (compression, any direction) | 25 MPa | in-plane value |
| E, ν | 1800 MPa, 0.35 | skill table; ν assumed |
| Kt | 2.5 sharp corner, window corner or notch; 2.0 hole or 45° wedge | skill; agent rule Kt ≥ 2 |

Required SF: 3 short-term, 4 sustained or cyclic, and 2 at a 1.5 × proof load.

## Results (copied from `python3 strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | base stall 1079 N.mm (yaw stall): disc-horn anti-rotation screws 2 x M2 x 6 at r 9 (assumed), bearing in the disk, L 3.2, friction ignored | bearing | 12.49 | 25.00 | 2.00 | 3 | **FAIL** |
| 2 | weight x2 (sustained): clamped base-horn joint: disk tips on the Ø25 disc's edge, clamp S 134 N, Ø9 washer pull-through, floor 8 (s0 e0 w0) | Z shear | 0.59 | 6.25 | 10.55 | 4 | OK |
| 3 | yaw-stall sweep: clamped base-horn joint: disk tips on the Ø25 disc's edge, clamp S 198 N, Ø9 washer pull-through, floor 8 (s70 e25 w-65, fingertip) | Z shear | 0.87 | 6.25 | 7.15 | 3 | OK |
| 4 | hand push 5 N: clamped base-horn joint: disk tips on the Ø25 disc's edge, clamp S 150 N, Ø9 washer pull-through, floor 8 (s90 e0 w0, fingertip) | Z shear | 0.66 | 6.25 | 9.43 | 3 | OK |
| 5 | weight x2 (sustained): disk at the disc horn's edge (rigid boss r 12.5, t 8; M 1675) | XY | 1.83 | 25.00 | 13.63 | 4 | OK |
| 6 | weight x2 (sustained): disk strip under the upright, b 66 t 8 (Kt 2.0; M_x 573) | XY | 1.63 | 25.00 | 15.35 | 4 | OK |
| 7 | yaw-stall sweep: disk at the disc horn's edge (rigid boss r 12.5, t 8; M 2473) | XY | 2.71 | 25.00 | 9.23 | 3 | OK |
| 8 | yaw-stall sweep: disk strip under the upright, b 66 t 8 (Kt 2.0; M_x 1967) | XY | 5.59 | 25.00 | 4.47 | 3 | OK |
| 9 | hand push 5 N: disk at the disc horn's edge (rigid boss r 12.5, t 8; M 1874) | XY | 2.05 | 25.00 | 12.18 | 3 | OK |
| 10 | hand push 5 N: disk strip under the upright, b 66 t 8 (Kt 2.0; M_x 1873) | XY | 5.32 | 25.00 | 4.70 | 3 | OK |
| 11 | weight x2 (sustained): upright Z 28.0, front face at the washer gap \|X\| < 6, no wedge (Kt 2.5; M_x 708, M_y 1574, M_z 0; s0 e0 w0) | Z | 0.77 | 12.50 | 16.28 | 4 | OK |
| 12 | weight x2 (sustained): upright Z 28.0, gusset toe (Kt 2.5; s0 e-150 w-90) | Z | 1.08 | 12.50 | 11.62 | 4 | OK |
| 13 | yaw-stall sweep: upright Z 28.0, front face at the washer gap \|X\| < 6, no wedge (Kt 2.5; M_x 1965, M_y 1434, M_z 1113; s75 e10 w-50, fingertip) | Z | 1.40 | 12.50 | 8.94 | 3 | OK |
| 14 | yaw-stall sweep: upright Z 28.0, gusset toe (Kt 2.5; s75 e10 w-50, fingertip) | Z | 2.98 | 12.50 | 4.19 | 3 | OK |
| 15 | hand push 5 N: upright Z 28.0, front face at the washer gap \|X\| < 6, no wedge (Kt 2.5; M_x 1836, M_y 257, M_z 375; s70 e5 w10, fingertip) | Z | 1.04 | 12.50 | 12.06 | 3 | OK |
| 16 | hand push 5 N: upright Z 28.0, gusset toe (Kt 2.5; s90 e0 w0, fingertip) | Z | 2.86 | 12.50 | 4.37 | 3 | OK |
| 17 | weight x2 (sustained): upright Z 50.6, front face (Kt 2.5; M_x 711, M_y 1574, M_z 0; s0 e0 w0) | Z | 1.65 | 12.50 | 7.59 | 4 | OK |
| 18 | yaw-stall sweep: upright Z 50.6, front face (Kt 2.5; M_x 1830, M_y 1332, M_z 1114; s75 e10 w-50, fingertip) | Z | 4.47 | 12.50 | 2.80 | 3 | **FAIL** |
| 19 | hand push 5 N: upright Z 50.6, front face (Kt 2.5; M_x 1644, M_y 357, M_z 628; s65 e0 w0, fingertip) | Z | 3.55 | 12.50 | 3.52 | 3 | OK |
| 20 | weight x2 (sustained): upright Z 55.5, front face (Kt 2.0; M_x 711, 1.00 of it between the tab screws, M_y 1574, M_z 0; s0 e0 w0) | Z | 1.78 | 12.50 | 7.03 | 4 | OK |
| 21 | yaw-stall sweep: upright Z 55.5, front face (Kt 2.0; M_x 1800, 1.00 of it between the tab screws, M_y 1310, M_z 1114; s75 e10 w-50, fingertip) | Z | 4.41 | 12.50 | 2.83 | 3 | **FAIL** |
| 22 | hand push 5 N: upright Z 55.5, front face (Kt 2.0; M_x 1701, 1.00 of it between the tab screws, M_y 236, M_z 404; s75 e0 w0, fingertip) | Z | 3.69 | 12.50 | 3.39 | 3 | OK |
| 23 | weight x2 (sustained): upright Z 60.5, front face (Kt 2.5; M_x 702, 0.70 of it between the tab screws, M_y 1574, M_z 0; s0 e0 w0) | Z | 1.67 | 12.50 | 7.51 | 4 | OK |
| 24 | yaw-stall sweep: upright Z 60.5, front face (Kt 2.5; M_x 1766, 0.70 of it between the tab screws, M_y 1287, M_z 1110; s75 e10 w-50, fingertip) | Z | 3.70 | 12.50 | 3.38 | 3 | OK |
| 25 | hand push 5 N: upright Z 60.5, front face (Kt 2.5; M_x 1714, 0.70 of it between the tab screws, M_y 102, M_z 134; s85 e0 w5, fingertip) | Z | 3.39 | 12.50 | 3.69 | 3 | OK |
| 26 | weight x2 (sustained): upright torsion at the root, open section (T 0) | Z shear | 0.00 | 6.25 | inf | 4 | OK |
| 27 | yaw-stall sweep: upright torsion at the root, open section (T 1239) | Z shear | 1.02 | 6.25 | 6.11 | 3 | OK |
| 28 | hand push 5 N: upright torsion at the root, open section (T 1079) | Z shear | 0.89 | 6.25 | 7.02 | 3 | OK |
| 29 | shoulder stall 1079 N.mm: far tab pilot bearing, F 13.1 N | bearing | 0.87 | 25.00 | 28.79 | 3 | OK |
| 30 | shoulder stall 1079 N.mm: notch -> pilot strip 1.74: tear-out (planes across the layers), F 13.1 N | Z shear | 0.65 | 6.25 | 9.63 | 3 | OK |
| 31 | weight x2 (sustained): shoulder MG996R tab screw pull-out, S 26 N (L 7, Ø2.6; s0 e-150 w-90) | Z shear | 0.45 | 6.25 | 14.00 | 4 | OK |
| 32 | weight x2 (sustained): notch strip 1.74: splitting, snug preload 150 N + 26 N (horizontal pilot in a standing wall: taken across the layers) | Z | 2.55 | 12.50 | 4.90 | 4 | OK |
| 33 | yaw-stall sweep: shoulder MG996R tab screw pull-out, S 82 N (L 7, Ø2.6; s80 e-5 w-40, fingertip) | Z shear | 1.44 | 6.25 | 4.35 | 3 | OK |
| 34 | yaw-stall sweep: notch strip 1.74: splitting, snug preload 150 N + 82 N (horizontal pilot in a standing wall: taken across the layers) | Z | 3.37 | 12.50 | 3.71 | 3 | OK |
| 35 | hand push 5 N: shoulder MG996R tab screw pull-out, S 71 N (L 7, Ø2.6; s75 e0 w0, fingertip) | Z shear | 1.25 | 6.25 | 5.01 | 3 | OK |
| 36 | hand push 5 N: notch strip 1.74: splitting, snug preload 150 N + 71 N (horizontal pilot in a standing wall: taken across the layers) | Z | 3.21 | 12.50 | 3.89 | 3 | OK |
| 37 | spec §8: tab screws driven snug: notch strip 1.74: splitting at 150 N (across the layers) | Z | 2.18 | 12.50 | 5.74 | 4 | OK |

**Lowest SF 2.00 (required 3) at: base stall: disc-horn anti-rotation screws (row 1).** Rows 18 (2.80) and 21 (2.83)
fail too.

### Advisory rows (not in the verdict)

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | Why it is advisory |
|---|---|---|---|---|---|---|
| base stall 1079 N.mm: anti-rotation screws 2 x M2 x 6 at r 7 (hole-circle sensitivity) | bearing | 16.06 | 25.00 | 1.56 | 3 | The disc's hole circle is not measured |
| base stall 1079 N.mm: anti-rotation screws 2 x M2 x 6 at r 10.5 (hole-circle sensitivity) | bearing | 10.70 | 25.00 | 2.34 | 3 | as above |
| base stall 1079 N.mm: FIX: 2 x M2 x 8 at r 7, L 5.2 | bearing | 9.88 | 25.00 | 2.53 | 3 | Candidate fix |
| base stall 1079 N.mm: FIX: 2 x M2 x 8 at r 9, L 5.2 | bearing | 7.69 | 25.00 | 3.25 | 3 | Candidate fix |
| base stall 1079 N.mm: FIX: 4 x M2 x 8 at r 7, L 5.2 | bearing | 4.94 | 25.00 | 5.06 | 3 | Recommended fix, worst hole circle |
| base stall 1079 N.mm: FIX: 4 x M2 x 8 at r 9, L 5.2 | bearing | 3.84 | 25.00 | 6.51 | 3 | Recommended fix |
| base stall 1079 N.mm: 2 x M2 x 6 at r 9 with clamp friction credited (μ 0.2, 150 N left of the preload: 340 N.mm) | bearing | 8.55 | 25.00 | 2.92 | 3 | Friction depends on a preload nobody sets; still fails |
| yaw-stall sweep with a 15 kgf.cm clone MG996R: upright window bottom, front | Z | 6.10 | 12.50 | 2.05 | 3 | Sensitivity (01 N1) |
| yaw-stall sweep, tab screws over-tightened to 300 N: notch strip 1.74: splitting | Z | 5.55 | 12.50 | 2.25 | 3 | Sensitivity: twice the assumed preload. Drive them snug, no harder |

## Required changes (FAIL)

**1. Anti-rotation screws: use 4 × M2 × 8 through four of the disc horn's holes on one circle.**

- **Drilling.** Drill the Ø1.5 pilots 5.5–6 mm deep into the disk's underside. Do not break through the 8 mm disk. Each
  screw then engages 5.2 mm.
- **Result.** SF **6.51** at r 9, and still 5.06 if the circle is only r 7. No CAD change is needed: BUILD_GUIDE §4 step
  3 drills the pilots through the horn.
- **Alternative.** If the hole circle is measured at r ≥ 9 mm, 2 × M2 × 8 is enough (3.25 at r 9).

**2. Upright window region: GUSSET_H 70 → 90.**

- **Results.** Window bottom **3.27**, lower pilot row **3.46**, notch level 4.36 (yaw stall). The hand push gives
  4.14 / 4.17.
- **Footprint unchanged.** The gusset toe stays at r 47.8, inside the disk.
- **The gussets would now end above the upright's top** (Z 97.3), so cut them off there. They are then 4.4 mm deep at
  the top.
- **Printing.** The outer face leans 14° from vertical, so it prints without support.

Other ways I checked (window bottom / pilot row under the yaw stall):

| Change | Window bottom | Pilot row | Note |
|---|---|---|---|
| GUSSET_H 70 → 100 | 3.44 | 3.69 | More margin |
| GUSSET_T 4 → 6 with GUSSET_X 30.5 → 29.5 | 3.16 | 3.19 | Keeps the toe at r 47.8; leaves 0.8 mm to the tab screw tips |
| UP_T 7 → 8 with GUSSET_LEN 23 → 22 | 2.90 | 2.97 | **Not enough.** The thicker upright alone would push the gusset toe off the disk |

**After both changes**

- Every row reaches its required SF, so the verdict becomes NEEDS_TEST.
- **Sensitivity.** With 15 kgf·cm clone servos, GUSSET_H 90 drops to about 2.4.

## Proof test (spec §8)

**Why §8 as written does not work**

- **§8 (1) cannot be run.** With the upper link horizontal, 1 kg at the elbow axis plus the arm's own weight is
  1335 N·mm (forearm hanging down) to 1589 N·mm (forearm straight out) about the shoulder. That is more than the shoulder
  servo's 1079 N·mm stall, so the servo would be back-driven.
- **The elbow-at-90° repeat in §8 (2) cannot reach a proof load.**
  - With servos unpowered, the elbow may not hold the forearm level.
  - With servos powered, the fingertips are 184 mm out along X. A ±Y push of 5.9 N there already reaches the base
    servo's 1079 N·mm stall, so the base slips.
  - The upright torsion it was meant to test has SF 6.1 anyway.
- **The anti-rotation screws** are not tested at all.

Replace the §8 "Proof test" item with:

> **Proof test:** (1) Base screwed down, ring fitted, arm assembled, servos powered, base servo centred, arm pointing
> straight up (upper link, forearm and claw in one vertical line). Push 11.5 N (≈1.2 kg on a luggage scale) sideways at
> the fingertips, square to the arm's plane (±Y), 1 min each way. Pass: no cracks or whitening at the upright's window
> corners, the tab pilots and lead notches, the gusset toes or the upright–disk corner; the disk doesn't lift off the
> disc horn; the fingertips come back to within 1 mm. (2) Disc-horn check: servos powered, base centred; mark the disk
> rim against the base. Push tangentially on the rim with the luggage scale up to 34 N (≈3.5 kg), or until the base
> servo gives way, 5 times each way. Pass: back at the same command the marks line up again within 1 mm (nothing slipped
> at the disc horn); when the turntable is next off, no cracks or elongated holes at the anti-rotation screws.

**What the replacement tests do**

- **Test (1), ratios at 11.5 N.** The script prints each check's test value over its yaw-stall value:

  | Check | Ratio |
  |---|---|
  | Window bottom | 1.50 |
  | Lower pilot row | 1.66 |
  | Notch level | 1.86 |
  | Root front | 1.47 |
  | Gusset toe | 1.97 |
  | Base-horn joint and disk | 1.59 |
  | Disk strip | 2.00 |
  | Shoulder tab screw | 1.75 |

  - The upright's torsion is not tested (0.09 ×; SF 6.1).
  - The same test is the base's proof test.
  - It loads the upper link to 1.75 × at x 15 and the forearm to 1.44 ×.
  - Run it only after all three parts have their fixes. On the links as drawn, the upper link's rails would see SF 0.94.
- **Test (2).** 34 N at r 48 is 1.5 × the base stall.
  - If the servo gives way first, the screws have seen the most the servo can ever apply to them.
  - The marks show slip at the disc horn, whether it comes from the screws or from the spline.

VERDICT: FAIL

# Strength check: 20261025-arm-upper-link (round 5, independent re-check)

strength-analyst (independent review: I did not design this part) · 2026-10-26 ·
`python3 jobs/20261025-arm-upper-link/strength_calc.py` (plain Python, no build123d, about 10 s). It reads every link's
`model.py`, `tools/hobby_parts.py`, the claw's `claw_frame.py`, each part's `geometry.json` and the assembly's
`torque_budget.json`, sweeps 47 170 arm poses and prints the tables below.

## Summary

- **FAIL.** Lowest SF **1.49** (3 required): the two window rails beside the elbow MG996R window, at the window's far
  end, under the yaw-stall sweep (s110 e-5 w40, contact at the fingertips).
- The 5 N hand push fails the same rails: SF **1.89**.
- Every other check is at SF 3.41 or above:

  | Check | SF |
  |---|---|
  | Far lead notch section | 3.41 |
  | x 15 over the horn pocket | 3.42 |
  | Plate torsion | 3.72 |
  | Far pilot row | 3.88 |
  | Elbow tab screws | 4.18 |
  | Shoulder-horn joint | 4.27 |

- **Change that passes:** ribs 6 mm deep on the back face along both rails, giving yaw 3.82 and hand 4.84. 4 mm ribs are
  not enough (2.93).
- With that change every row reaches its required SF. The best verdict is then NEEDS_TEST, because the allowables are
  placeholders.
- **Proof test:** §8 (2) as written loads the rails to only 0.44 × their yaw-stall value. The replacement is under
  "Proof test".

## What changed since round 4

**Design changes this round**

- **Lead notches** at both ends of the elbow MG996R's case, 4.4 × 2.0 printed. They cut two things:
  - the notch-to-pilot strip, now 1.84 CAD and 1.79 behind the ST2.9 thread;
  - the plate section at the far notch (x 67.4–69.5): net width 29.4, Kt 2.5.
- **Forearm fitting.** The forearm is fitted 60° below this link (SYS-03), so the elbow window is -150 … +30.
- **Claw and camera.** 224.1 g beyond the wrist horn with solid parts ("camera, solid"; 208.6 g sliced).
- **The camera's sideways weight** (SYS-04) acts in every pose: 239 N·mm about the shoulder servo's case top and
  161 N·mm about the elbow servo's.
- **Shoulder clamp:** M3 × 14 + Ø9 × 0.8 washer, 4.6 mm into the spline (01 S2).

**Method changes in this review**

- **New pose model.** The pose model is my own, but it reproduces `torque_budget.json` exactly:
  - end effector 224.1 g;
  - overhung moments 239 / 161 / 108 N·mm;
  - 692 N·mm on the base horn with the arm straight out.
- **Stall torque.** MG996R stall 1079 N·mm (11 kgf·cm datasheet, deep review 01 N1); the specs say 1000.
- **Contact points.** Yaw-stall and hand-push forces act at the fingertips and at either end of the camera. The
  fingertips governed.

**Why the lowest SF fell from 3.90 (round 4) to 1.49**

- **Round 4 treated the rails as advisory.** Its "rails alone" rows gave 1.76 (yaw) and 2.28 (hand). It assumed the
  servo case, bolted at both tab rows, carries the out-of-plane moment across the window.
- **It cannot.** Each MG996R tab has two screws, but both sit at the same x (y ±5). So each tab row is a pin about the
  plate's y axis.
- **By statics,** the near tab's force must travel back through the rails. The rails carry:
  - **0.926** of the far-row moment at the window's far end;
  - 0.941 of it at the far notch.
- **A tab-spring estimate** (each tab stiff in its own bending) still leaves 0.67 of the moment: SF 2.06, advisory.

## Load cases

Spec §4 cases, all at 40 °C:

| Case | Load | Duration | How it is applied here |
|---|---|---|---|
| Shoulder stall through the horn slot | 1079 N·mm | short-term | Horn-pocket wall bearing; in-plane bending (full section and rails) |
| Distal weight + 50 g payload | ×2 dynamic | sustained | "Weight ×2" sweep, SF 4 |
| Camera + distal weight across the shoulder shaft (SYS-04) | 239 N·mm static, every pose | sustained | Part of the weight ×2 sweep: horn clamp, plate round the pocket |
| Elbow servo's sideways moment (SYS-04) | 161 N·mm static, every pose | sustained | Part of the weight ×2 sweep: tab screws, rails |
| Elbow stall reaction | 1079 N·mm | short-term | Far tab pilot bearing; notch strip tear-out |
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

## Assumptions

**Allowables, masses and loads**

- **Allowables:** placeholders, listed below.
- **Masses:**
  - each `geometry.json` volume × 1.27 g/cm³, as solid parts;
  - build123d centres of mass;
  - servos and horns from `hobby_parts.py`, plus cable allowances;
  - 50 g payload at the fingertips.
- **Dynamic factor:** ×2 on the weight (the specs; SYS-06's 250 °/s² ramps need about ×1.1).

**Shoulder-horn joint**

- The clamp tension needed is S = |M_y| / 17.5 + |M_x| / 5.5 + |F_z|. The link tilts on a horn-arm tip (17.5 mm) or on
  the hub edge (5.5 mm).
- The capacity is Ø9 washer pull-through on the 8 mm floor, against the interlayer shear allowable.
- The M2 × 6 arm screws are not credited.
- The thread in the metal spline is bought hardware. At most 331 N of clamp tension holds there, provided the screw
  does not bottom out (01 S2).

**Plate sections**

- The sections are computed from the parameters and match the CAD within 0.4 %. Out-of-plane I:
  - x 15 over the 2 mm horn pocket, Kt 2 for the arm-screw hole: 2599;
  - x 30: 2833;
  - far pilot row, Kt 2: 2367;
  - far notch, Kt 2.5: 2450;
  - rails: 1142 mm⁴.
- Plate torsion: τ = T / (α b t²), taken against the interlayer shear allowable.

**Window rails** (6.85 × 10 each, Kt 2.5 at the sharp window corners)

- 0.926 of the far-row moment in out-of-plane bending.
- 15 % of the torsion crosses the window as a frame couple in the two rails.
- Evaluated pose by pose.

**Elbow MG996R tab screws**

- M3 × 12 + Ø7 × 0.5 washer through the 2.5 mm tab: 9 mm engaged in the 10 mm plate, Ø2.6 printed pilot.
- Torsion split:
  - Each tab has two screws across its width, so a tab joint is stiff in twist: 0.5–2.4e6 N·mm/rad.
  - The rails as a frame give only 0.85e5 N·mm/rad.
  - So the far tab takes 87–97 % of the torsion. I put all of it on the far tab's outer screw (lever 14.85 mm; the
    inner screw is ignored).
- Screw tension S = |M_x| / 14.85 + |M_y| / (2 × 51.25) + |F_z| / 4.
- Pull-out is taken against the interlayer shear allowable.

**Notch strip**

- 1.84 CAD, minus the 0.05 mm the ST2.9 thread cuts beyond the Ø2.8 CAD hole: 1.79 intact.
- Tear-out and Lamé splitting as in the forearm review: 150 N snug preload plus the screw tension, with 300 N as a
  sensitivity.

**Temperature.** 40 °C, and servo cases up to 45 °C, against PETG softening at about 70 °C. The margin is 25 °C or more,
which is OK.

## Allowables and sources

`library/materials.csv` has only its header, and no job has a datasheet in `inputs/`. These are the strength-checks
**placeholder** values for PETG, so **NEEDS_TEST is the best verdict possible**.

| Quantity | Value | Source |
|---|---|---|
| Tension / bending along the layers (XY) | 25 MPa | strength-checks placeholder, PETG |
| Tension / bending across the layers (Z) | 12.5 MPa | placeholder × 0.5 |
| Shear in-plane / interlayer | 12.5 / 6.25 MPa | 0.5 × the normal value (Tresca), my assumption |
| Bearing (compression, any direction) | 25 MPa | in-plane value |
| E, ν | 1800 MPa, 0.35 | skill table; ν assumed |
| Kt | 2.5 sharp window corner or notch; 2.0 hole | skill; agent rule Kt ≥ 2 |

Required SF: 3 short-term, 4 sustained or cyclic, and 2 at a 1.5 × proof load. The link prints flat, front face down, so
all its bending runs along the layers. Screw and washer pull-out and plate torsion are taken against the interlayer
shear allowable.

## Results (copied from `python3 strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | shoulder stall 1079 N.mm: horn-pocket wall bearing (arm flanks, triangular, 2 mm deep) | bearing | 1.97 | 25.00 | 12.67 | 3 | OK |
| 2 | shoulder stall 1079 N.mm: in-plane bending, full section (M <= stall) | XY | 0.56 | 25.00 | 44.64 | 3 | OK |
| 3 | shoulder stall 1079 N.mm: in-plane bending of the window rails (Kt 2.5) | XY | 1.78 | 25.00 | 14.06 | 3 | OK |
| 4 | elbow stall 1079 N.mm: far tab pilot bearing, F 13.1 N | bearing | 0.87 | 25.00 | 28.79 | 3 | OK |
| 5 | elbow stall 1079 N.mm: notch -> pilot strip 1.79: tear-out, F 13.1 N | XY shear | 0.63 | 12.50 | 19.88 | 3 | OK |
| 6 | weight x2 (sustained): clamped shoulder-horn joint: Ø9 washer pull-through, floor 8 (S 94 N; s15 e-150 w-90) | Z shear | 0.42 | 6.25 | 15.02 | 4 | OK |
| 7 | yaw-stall sweep: clamped shoulder-horn joint: Ø9 washer pull-through, floor 8 (S 331 N; s115 e-70 w-15, fingertip) | Z shear | 1.46 | 6.25 | 4.27 | 3 | OK |
| 8 | hand push 5 N: clamped shoulder-horn joint: Ø9 washer pull-through, floor 8 (S 246 N; s165 e-75 w0, fingertip) | Z shear | 1.09 | 6.25 | 5.75 | 3 | OK |
| 9 | weight x2 (sustained): x 15 over the pocket, out of plane (Kt 2 arm-screw hole; M 468) | XY | 1.86 | 25.00 | 13.43 | 4 | OK |
| 10 | yaw-stall sweep: x 15 over the pocket, out of plane (Kt 2 arm-screw hole; M 1835) | XY | 7.30 | 25.00 | 3.42 | 3 | OK |
| 11 | hand push 5 N: x 15 over the pocket, out of plane (Kt 2 arm-screw hole; M 1526) | XY | 6.07 | 25.00 | 4.12 | 3 | OK |
| 12 | yaw-stall sweep: x 30 full section, out of plane (M 1743) | XY | 3.08 | 25.00 | 8.13 | 3 | OK |
| 13 | weight x2 (sustained): far elbow-pilot row x 65.6, out of plane (Kt 2; M 468; s90 e-150 w-90) | XY | 1.98 | 25.00 | 12.65 | 4 | OK |
| 14 | weight x2 (sustained): far lead notch x 67.4-69.5, net 29.4 (Kt 2.5; 0.94 M) | XY | 2.25 | 25.00 | 11.13 | 4 | OK |
| 15 | weight x2 (sustained): window rails 2 x 6.85 at the far window end, tab rows as pins (Kt 2.5; s75 e-150 w-90) | XY | 4.88 | 25.00 | 5.12 | 4 | OK |
| 16 | yaw-stall sweep: far elbow-pilot row x 65.6, out of plane (Kt 2; M 1526; s120 e-25 w50, fingertip) | XY | 6.45 | 25.00 | 3.88 | 3 | OK |
| 17 | yaw-stall sweep: far lead notch x 67.4-69.5, net 29.4 (Kt 2.5; 0.94 M) | XY | 7.33 | 25.00 | 3.41 | 3 | OK |
| 18 | yaw-stall sweep: window rails 2 x 6.85 at the far window end, tab rows as pins (Kt 2.5; s110 e-5 w40, fingertip) | XY | 16.75 | 25.00 | 1.49 | 3 | **FAIL** |
| 19 | hand push 5 N: far elbow-pilot row x 65.6, out of plane (Kt 2; M 1273; s90 e0 w0, fingertip) | XY | 5.38 | 25.00 | 4.65 | 3 | OK |
| 20 | hand push 5 N: far lead notch x 67.4-69.5, net 29.4 (Kt 2.5; 0.94 M) | XY | 6.11 | 25.00 | 4.09 | 3 | OK |
| 21 | hand push 5 N: window rails 2 x 6.85 at the far window end, tab rows as pins (Kt 2.5; s75 e15 w0, fingertip) | XY | 13.23 | 25.00 | 1.89 | 3 | **FAIL** |
| 22 | weight x2 (sustained): plate torsion, full width (T 468) | Z shear | 0.50 | 6.25 | 12.40 | 4 | OK |
| 23 | yaw-stall sweep: plate torsion, full width (T 1561) | Z shear | 1.68 | 6.25 | 3.72 | 3 | OK |
| 24 | hand push 5 N: plate torsion, full width (T 1101) | Z shear | 1.19 | 6.25 | 5.27 | 3 | OK |
| 25 | weight x2 (sustained): elbow MG996R tab screw pull-out, S 29 N (L 9, Ø2.6; s10 e-150 w-90) | Z shear | 0.40 | 6.25 | 15.73 | 4 | OK |
| 26 | weight x2 (sustained): notch -> pilot strip 1.79: splitting, snug preload 150 N + 29 N | XY | 1.99 | 25.00 | 12.53 | 4 | OK |
| 27 | yaw-stall sweep: elbow MG996R tab screw pull-out, S 110 N (L 9, Ø2.6; s135 e-90 w-25, fingertip) | Z shear | 1.49 | 6.25 | 4.18 | 3 | OK |
| 28 | yaw-stall sweep: notch -> pilot strip 1.79: splitting, snug preload 150 N + 110 N | XY | 2.89 | 25.00 | 8.64 | 3 | OK |
| 29 | hand push 5 N: elbow MG996R tab screw pull-out, S 75 N (L 9, Ø2.6; s170 e-80 w0, fingertip) | Z shear | 1.02 | 6.25 | 6.10 | 3 | OK |
| 30 | hand push 5 N: notch -> pilot strip 1.79: splitting, snug preload 150 N + 75 N | XY | 2.51 | 25.00 | 9.97 | 3 | OK |
| 31 | spec §8: tab screws driven snug: notch -> pilot strip 1.79: splitting at 150 N | XY | 1.67 | 25.00 | 14.97 | 4 | OK |

**Lowest SF 1.49 (required 3) at: yaw-stall sweep: window rails 2 × 6.85 at the far window end (row 18).** Row 21
(hand push, 1.89) fails too.

### Advisory rows (not in the verdict)

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | Why it is advisory |
|---|---|---|---|---|---|---|
| yaw-stall sweep: window rails with tab springs (0.67 of the row moment instead of 0.93) | XY | 12.13 | 25.00 | 2.06 | 3 | The most the tabs' own stiffness might help; not relied on. It still fails |
| yaw-stall sweep with a 15 kgf.cm clone MG996R: window rails | XY | 22.84 | 25.00 | 1.09 | 3 | Sensitivity (01 N1): every yaw-stall load scales by 15 / 11 |
| yaw-stall sweep, tab screws over-tightened to 300 N: notch -> pilot strip 1.79: splitting | XY | 4.56 | 25.00 | 5.48 | 3 | Sensitivity: twice the assumed snug preload |

## Required changes (FAIL)

Add **ribs on the back face along both window rails**:

- **Shape.** As wide as the rails (6.85 mm), along the whole window (x 69.2–110.5) and at least 5 mm past each window
  end onto the full plate. They deepen the window's side walls.
- **Results.** Every term of the rail stress scales with (10 / (10 + rib))², so these are exact:

  | Rib depth | Yaw stall | Hand push | Weight ×2 |
  |---|---|---|---|
  | 4 mm (rails 6.85 × 14) | 2.93, not enough | 3.70 | 10.04 |
  | **6 mm (rails 6.85 × 16), recommended** | **3.82** | **4.84** | 13.11 |
  | 8 mm (rails 6.85 × 18) | 4.84 | 6.12 | 16.59 |

- **15 kgf·cm clones.** If the base servo is a clone, the 6 mm ribs drop to 2.80. Use 8 mm then (3.55).
- **Why the ribs fit:**
  - The elbow servo's case already stands 17 mm out of the back face here, 69–110 mm from the shoulder axis. The ribs
    sit 64–116 mm out, at less depth.
  - Nothing else passes behind the link at that distance. The upright lies within about 45 mm of the shoulder axis. The
    link never drops below Z 43.5, while the disk lies below Z 24.5.
  - The servo's lead leaves its case end on the centre line, between the ribs.
  - The link prints front face down, so the ribs print upward without supports.

With 6 mm ribs every row reaches its required SF, so the verdict becomes NEEDS_TEST.

## Proof test (spec §8)

**Why §8 (2) as written does not prove the rails**

- **The 21 N push at the elbow axis** loads the rails to 0.44 × their yaw-stall value. It enters between the tab rows,
  so most of it bypasses them.
- **The 7.5 N push on a 185 mm lever** gives 1388 N·mm, which is 0.89 × the yaw-stall torsion (1561 N·mm).
- **Test (1)** (1 kg at the elbow axis, deflection < 2 mm) is fine. Keep it.

Replace the §8 "Proof test" item with:

> **Proof test:** (1) Shoulder horn in a vice (horn clamped in its slot), 1 kg at the elbow axis for 1 min: deflection at
> the elbow < 2 mm, no permanent set. (2) Same clamping, with the link plate vertical and the elbow MG996R fitted with its
> 4 tab screws as built. Screw a flat bar to the elbow horn in place of the forearm, and set it at 60° to the link in the
> link's plane. Push 16 N (≈1.6 kg on a luggage scale) along the elbow shaft, square to the plate, at 175 mm from the
> elbow axis, 1 min each way. Pass: no cracks or whitening at the window corners and rails, the lead notches, the tab
> pilots or the horn pocket; the MG996R tabs don't lift; the link doesn't lift off the horn; the bar end comes back to
> within 1 mm of where it started.

**What the replacement test does**

- **Where the load goes.** 175 mm is the forearm and claw's reach (173.4 mm).
- **Ratios at 16 N.** The script prints each check's test value over its yaw-stall value:

  | Check | Ratio |
  |---|---|
  | Rails | 1.54 |
  | Tab screw | 1.66 |
  | Far pilot row | 1.28 |
  | x 15 | 1.50 |
  | Torsion | 1.55 |
  | Shoulder-horn joint | 1.90 |

- **The notch strip** reaches splitting SF 6.75, against 2 required.
- **Why 60°.** Each critical check reaches 1.5 × at a different force and bar angle:

  | Bar angle | Rails at 1.5 × | Tab screw at 1.5 × |
  |---|---|---|
  | 0° (in line) | 11.8 N | 80 N |
  | 90° | 32 N | 13.6 N |

  60° loads both together.
- **The turntable and base test** (arm straight up, 11.5 N sideways at the fingertips) loads this link to 1.59 × at the
  rails and 1.75 × at x 15.
- **Run either test only after the ribs are added.** On the link as drawn, the rails would see SF 0.94 in the
  turntable test and 0.97 in this one.

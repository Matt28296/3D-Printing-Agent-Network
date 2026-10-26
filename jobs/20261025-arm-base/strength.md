VERDICT: FAIL

# Strength check: 20261025-arm-base (round 5, independent re-check)

strength-analyst (independent review: I did not design this part) · 2026-10-26 ·
`python3 jobs/20261025-arm-base/strength_calc.py` (plain Python, no build123d, about 10 s). It reads every link's
`model.py`, `tools/hobby_parts.py`, the claw's `claw_frame.py`, each part's `geometry.json` and the assembly's
`torque_budget.json`, sweeps 47 170 arm poses and prints the tables below.

## Summary

- **FAIL.** Lowest SF **1.21** (3 required): the 4 mm top plate round the base servo's tension-side tab-screw boss, under
  the yaw-stall sweep. The servo path carries M 2602 N·mm there, with the ring ignored.
- The same section fails in every other case:

  | Case | SF | Required |
  |---|---|---|
  | Weight ×2 | 1.87 | 4 |
  | Hand push | 1.60 | 3 |
  | Shoulder stall on the desk | 1.49 | 3 |
  | 20 N on the turntable rim | 1.74 | 3 |

- Even if the ring shares the moment past its 0.4 mm gap (play-free servo), the plate stays at 1.51 (yaw) and 1.87
  (weight ×2).
- Everything else passes: servo tab screws 4.03 or above, ring path 3.64 or above, USB bosses 4.10.
- **Change that passes:** a local pad under the top plate, **7.5 mm** thick round the far tab and 5.5 mm round the near
  tab (where the ESP32 cradle leaves less room). Both give SF 3.39 even with fully sharp corners (Kt 2.5). 7 mm round
  the far tab is enough (3.69) if the notch and window corners get a fillet.
- With that change every row reaches its required SF. The best verdict is then NEEDS_TEST, because the allowables are
  placeholders.
- **Proof test:**
  - §8 needs the turntable's arm-up test, which loads the servo path.
  - The rim load rises 50 → 77 N: 50 N is only 0.97 × the yaw-stall ring load.

## What changed since round 4

**Design changes this round**

- **Lead notches** at both case ends through the 4 mm plate. The notch-to-pilot strip is 1.84 CAD, 1.79 behind the
  ST2.9 thread.
- **The turntable now sits on the base servo's Ø25 disc horn**, clamped by an M3 × 14. Until the ring catches it, the
  whole overturning moment goes through the servo's shaft and case into its four tab screws, and so into this plate.
- **The ring runs 0.4 mm under the disk** with PTFE tape (SYS-05). It shares the moment only after 0.52° of tilt.
- **Claw and camera.** 224.1 g with solid parts.
- **The arm's sideways offset** gives 245–286 N·mm about X in every pose. With the arm straight out the moment is
  692 N·mm, or 832 N·mm with 50 g (torque_budget).

**Method changes in this review**

- **New pose model.** The pose model is my own, but it reproduces `torque_budget.json` exactly. MG996R stall
  1079 N·mm (datasheet).

**Why the lowest SF fell from 4.10 (round 4) to 1.21**

- **New check.** Round 4 checked the servo tab screws' pull-out (4.30), but not the 4 mm plate the tension screw pulls
  on.
- **Why the plate is weak there.** The base's top plate is a 4 mm sheet spanning 98 × 104 mm between the walls. The
  window, the lead notch and the pilot are all cut within 2–4 mm of the tension screw's boss.
- **What the screw does.** When the turntable is pushed over, the far tab pries about its long edge and its outer screw
  pulls up on the plate with S = 0.65 × M / 14.85. That is 114 N under the yaw stall.

## Load cases

Spec §4 cases, all at 40 °C:

| Case | Load | Duration | How it is applied here |
|---|---|---|---|
| Base-servo stall reaction | 1079 N·mm about Z | short-term | Far tab pilot bearing; notch strip tear-out |
| Moment of everything on the turntable (SYS-05) | ×2 dynamic | sustained | "Weight ×2" sweep, SF 4; servo path and ring path |
| Base-yaw stall / hand push on the arm, including the spec's ≈52 N ring catch | swept (below); the ring catch comes out at 58.2 N | short-term | Servo path and ring path, SF 3 |
| Shoulder stall with the fingertips on the desk | 1079 × (60 + 10.15) / 60 + static = 2099 N·mm | short-term | Servo path |
| Hand push on the turntable | 20 N at the rim | short-term | Servo path; ring path |
| Tipping with the arm out (SYS-12) | stability | sustained | Desk-screw uplift, printed |
| USB insertion / jumper pull | 20 N / 10 N | short-term | Cradle bosses, as in round 3 |
| Assembly | M3 × 12 tab screws driven snug | sustained | Notch strip splitting at 150 N |

**How the sweep is set up**

- **Poses.** Shoulder 0–180, elbow -150 … +30, wrist ±90, in 5° steps. That gives 47 170 poses with the elbow, wrist
  and fingertips above the desk.
- **Yaw stall.** F = 1079 / R, tangential, at the fingertips or a camera end. It is scaled down wherever a pitch servo
  would back-drive first.
- **Hand push.** 5 N along ±Y, capped where the yaw servo would back-drive.
- **Combining with weight.** Both contact cases add the static weight, component by component, taking the worse sign of
  each.
- **Moments taken:**
  - at the tab plane (Z 0) for the servo path: weight ×2 1675, yaw 2602, hand 1956 N·mm;
  - at the disk underside for the ring path: 1675 / 2473 / 1874 N·mm.

## Assumptions

**Servo path (verdict rows): the ring ignored**

- The whole overturning moment passes through the base servo's four tab screws.
- Every direction is taken on the servo's weak axis, because the turntable yaws.
- 65 % goes to the far tab, which sits 15 mm from the -X wall, on its outer screw (lever 14.85; the inner screw is
  ignored). The screw tension is S = 0.65 M / 14.85.
- **Pull-out:** M3 × 12 + Ø7 washer gives 9 mm in plate + boss, Ø2.6 pilot, against the interlayer shear allowable.

**Plate round the tension screw's boss**

- Roark: a circular plate, simply supported at a = 14.85 (the tab's pivot edge), loaded over the Ø6.5 boss
  (r0 = 3.25):

  σ = Kt × 3S / (2π t²) × [(1 + ν) ln(a / r0) + 1]

- **Kt 2.0** for the notch and window corner beside the boss. I used 2.0 rather than 2.5 because the Roark value is
  already the peak at the boss edge. 2.5 is shown as a sensitivity, and the recommended change passes with it.
- The plate prints on the bed, so this bending runs along the layers (25 MPa).

**Ring sharing (advisory only)**

- **Stiffnesses:**
  - servo path: a rigid boss of b 9.85 in a clamped plate of a 49, which gives 18.43·D = 2.0e5 N·mm/rad (derived for
    this review);
  - ring path: the ring force at r 44 on the plate strip (a 20.6): 4.2e5 N·mm/rad.
- **Sharing.** Until the 0.4 mm gap closes, the servo takes everything: 0.4 / 44 rad × 2.0e5 = 1833 N·mm. Beyond that
  it takes 0.33 of the rest.
- **Not credited:** play in the servo's output bearing, which would close the gap sooner.

**Ring path (verdict rows)**

- The ring takes the whole overturning moment at r 42.5.
- The plate under it is a strip from the nearest wall: a 20.6, b = 2a + 2 × ring height − the cable slot.
- One ring screw takes 0.3 R of friction, as bearing in the plate pilot (L 3).

**Other rows**

- **Notch strip:** tear-out, and Lamé splitting at 150 N snug preload plus the screw tension. 300 N is a sensitivity
  row.
- **Cradle bosses:** as in round 3.
- **Masses:** solid parts × 1.27 g/cm³, ×2 dynamic for weight.

**Temperature.** 40 °C, and servo cases up to 45 °C, against PETG softening at about 70 °C. The margin is 25 °C or more,
which is OK.

## Allowables and sources

`library/materials.csv` has only its header, and no job has a datasheet in `inputs/`. These are the strength-checks
**placeholder** values for PETG, so **NEEDS_TEST is the best verdict possible**.

| Quantity | Value | Source |
|---|---|---|
| Tension / bending along the layers (XY): top plate | 25 MPa | strength-checks placeholder, PETG |
| Tension / bending across the layers (Z): boss roots | 12.5 MPa | placeholder × 0.5 |
| Shear in-plane / interlayer | 12.5 / 6.25 MPa | 0.5 × the normal value (Tresca), my assumption |
| Bearing (compression, any direction) | 25 MPa | in-plane value |
| E, ν | 1800 MPa, 0.35 | skill table; ν assumed |
| Kt | 2.0 plate at the notch and window corner, with 2.5 as a sensitivity; 2.5 boss roots | skill; agent rule Kt ≥ 2 |

Required SF: 3 short-term, 4 sustained or cyclic, and 2 at a 1.5 × proof load.

## Results (copied from `python3 strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | base stall 1079 N.mm: far tab pilot bearing, F 13.1 N | bearing | 0.87 | 25.00 | 28.79 | 3 | OK |
| 2 | base stall 1079 N.mm: notch -> pilot strip 1.79 in the 4 mm plate: tear-out, F 13.1 N | XY shear | 0.91 | 12.50 | 13.71 | 3 | OK |
| 3 | weight x2 (sustained): servo path: tab screw pull-out, M 1675 N.mm on the weak axis, S 73 N (L 9); s0 e0 w0 | Z shear | 1.00 | 6.25 | 6.27 | 4 | OK |
| 4 | weight x2 (sustained): servo path: top plate 4 mm round the tension screw's boss (Kt 2.0: notch and window corner) | XY | 13.35 | 25.00 | 1.87 | 4 | **FAIL** |
| 5 | weight x2 (sustained): notch strip 1.79: splitting, snug preload 150 N + 73 N | XY | 2.49 | 25.00 | 10.06 | 4 | OK |
| 6 | yaw-stall sweep: servo path: tab screw pull-out, M 2602 N.mm on the weak axis, S 114 N (L 9); s70 e25 w-65, fingertip | Z shear | 1.55 | 6.25 | 4.03 | 3 | OK |
| 7 | yaw-stall sweep: servo path: top plate 4 mm round the tension screw's boss (Kt 2.0: notch and window corner) | XY | 20.74 | 25.00 | 1.21 | 3 | **FAIL** |
| 8 | yaw-stall sweep: notch strip 1.79: splitting, snug preload 150 N + 114 N | XY | 2.94 | 25.00 | 8.51 | 3 | OK |
| 9 | hand push 5 N: servo path: tab screw pull-out, M 1956 N.mm on the weak axis, S 86 N (L 9); s90 e0 w0, fingertip | Z shear | 1.16 | 6.25 | 5.37 | 3 | OK |
| 10 | hand push 5 N: servo path: top plate 4 mm round the tension screw's boss (Kt 2.0: notch and window corner) | XY | 15.59 | 25.00 | 1.60 | 3 | **FAIL** |
| 11 | hand push 5 N: notch strip 1.79: splitting, snug preload 150 N + 86 N | XY | 2.62 | 25.00 | 9.53 | 3 | OK |
| 12 | shoulder stall on the desk: servo path: tab screw pull-out, M 2099 N.mm on the weak axis, S 92 N (L 9) | Z shear | 1.25 | 6.25 | 5.00 | 3 | OK |
| 13 | shoulder stall on the desk: servo path: top plate 4 mm round the tension screw's boss (Kt 2.0: notch and window corner) | XY | 16.73 | 25.00 | 1.49 | 3 | **FAIL** |
| 14 | shoulder stall on the desk: notch strip 1.79: splitting, snug preload 150 N + 92 N | XY | 2.69 | 25.00 | 9.29 | 3 | OK |
| 15 | 20 N on the turntable rim (spec): servo path: tab screw pull-out, M 1797 N.mm on the weak axis, S 79 N (L 9) | Z shear | 1.07 | 6.25 | 5.84 | 3 | OK |
| 16 | 20 N on the turntable rim (spec): servo path: top plate 4 mm round the tension screw's boss (Kt 2.0: notch and window corner) | XY | 14.33 | 25.00 | 1.74 | 3 | **FAIL** |
| 17 | 20 N on the turntable rim (spec): notch strip 1.79: splitting, snug preload 150 N + 79 N | XY | 2.55 | 25.00 | 9.82 | 3 | OK |
| 18 | spec §8: tab screws driven snug: notch strip 1.79: splitting at 150 N | XY | 1.67 | 25.00 | 14.97 | 4 | OK |
| 19 | weight x2 (sustained): ring path, R 39.4 N: top plate strip a 20.6, b 65 | XY | 4.66 | 25.00 | 5.37 | 4 | OK |
| 20 | weight x2 (sustained): ring path: friction 0.3 x R on one ring screw, bearing in the plate pilot (L 3) | bearing | 1.40 | 25.00 | 17.81 | 4 | OK |
| 21 | yaw-stall sweep: ring path, R 58.2 N: top plate strip a 20.6, b 65 | XY | 6.87 | 25.00 | 3.64 | 3 | OK |
| 22 | yaw-stall sweep: ring path: friction 0.3 x R on one ring screw, bearing in the plate pilot (L 3) | bearing | 2.07 | 25.00 | 12.06 | 3 | OK |
| 23 | hand push 5 N: ring path, R 44.1 N: top plate strip a 20.6, b 65 | XY | 5.21 | 25.00 | 4.80 | 3 | OK |
| 24 | hand push 5 N: ring path: friction 0.3 x R on one ring screw, bearing in the plate pilot (L 3) | bearing | 1.57 | 25.00 | 15.91 | 3 | OK |
| 25 | 20 N on the turntable rim (spec): ring path, R 22.6 N: top plate strip a 20.6, b 65 | XY | 2.67 | 25.00 | 9.37 | 3 | OK |
| 26 | 20 N on the turntable rim (spec): ring path: friction 0.3 x R on one ring screw, bearing in the plate pilot (L 3) | bearing | 0.80 | 25.00 | 31.07 | 3 | OK |
| 27 | USB insertion 20 N / 3 bosses: cradle-boss root bending (Kt 2.5) | Z | 3.05 | 12.50 | 4.10 | 3 | OK |
| 28 | 10 N jumper pull / 2 screws: cradle screw pull-out, 6 mm engaged | Z shear | 0.10 | 6.25 | 61.26 | 3 | OK |

**Lowest SF 1.21 (required 3) at: yaw-stall sweep: servo path: top plate 4 mm round the tension screw's boss (row 7).**
Rows 4, 10, 13 and 16 fail too.

### Advisory rows (not in the verdict)

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | Why it is advisory |
|---|---|---|---|---|---|---|
| weight x2 (sustained): servo path with the ring sharing past a 0.4 mm gap (play-free servo): M_servo 1675 of 1675 | XY | 13.35 | 25.00 | 1.87 | 4 | Credits the ring: still fails |
| yaw-stall sweep: servo path with the ring sharing past a 0.4 mm gap (play-free servo): M_servo 2084 of 2602 | XY | 16.61 | 25.00 | 1.51 | 3 | as above |
| weight x2 (sustained): servo path with the ring sharing past a 0.3 mm gap (play-free servo): M_servo 1473 of 1675 | XY | 11.74 | 25.00 | 2.13 | 4 | The gap with the PTFE tape on |
| yaw-stall sweep: servo path with the ring sharing past a 0.3 mm gap (play-free servo): M_servo 1775 of 2602 | XY | 14.14 | 25.00 | 1.77 | 3 | as above |
| weight x2 (sustained): FIX: ring at zero gap (disk resting on the taped ring): servo path takes 0.33, M_servo 546 | XY | 4.35 | 25.00 | 5.75 | 4 | Alternative fix; depends on assembly (below) |
| yaw-stall sweep: FIX: ring at zero gap (disk resting on the taped ring): servo path takes 0.33, M_servo 848 | XY | 6.76 | 25.00 | 3.70 | 3 | as above |
| yaw-stall sweep: FIX: top plate 6 mm round the servo (servo path, ring ignored) | XY | 9.22 | 25.00 | 2.71 | 3 | Not enough |
| yaw-stall sweep: FIX: top plate 6.5 mm round the servo (servo path, ring ignored) | XY | 7.85 | 25.00 | 3.18 | 3 | Passes at Kt 2.0 only |
| yaw-stall sweep: FIX: top plate 7 mm round the servo (servo path, ring ignored) | XY | 6.77 | 25.00 | 3.69 | 3 | Passes at Kt 2.0 |
| yaw-stall sweep: top plate 7 mm, corners left fully sharp (Kt 2.5 instead of 2.0) | XY | 8.46 | 25.00 | 2.95 | 3 | Kt sensitivity |
| yaw-stall sweep: top plate 7.5 mm, corners left fully sharp (Kt 2.5 instead of 2.0) | XY | 7.37 | 25.00 | 3.39 | 3 | **Recommended fix** |
| weight x2 (sustained): FIX: top plate 7 mm round the servo (servo path, ring ignored) | XY | 4.36 | 25.00 | 5.73 | 4 | The sustained case after the fix |
| weight x2 (sustained): top plate 7.5 mm round the far tab, Kt 2.5 | XY | 4.75 | 25.00 | 5.27 | 4 | as above, for the recommended fix |
| yaw-stall sweep: top plate 5.5 mm round the near tab (0.35 of M), Kt 2.5 | XY | 7.38 | 25.00 | 3.39 | 3 | Where the ESP32 cradle limits the pad |
| weight x2 (sustained): top plate 5.5 mm round the near tab (0.35 of M), Kt 2.5 | XY | 4.75 | 25.00 | 5.26 | 4 | as above |
| yaw-stall sweep, tab screws over-tightened to 300 N: notch strip 1.79: splitting | XY | 4.61 | 25.00 | 5.43 | 3 | Sensitivity: twice the assumed preload |

**Stability (SYS-12).**

- Free-standing, the robot tips with the arm out: SF 0.34–0.48 (torque_budget, sliced masses). The desk screws, or
  the 200 × 200 board, or ballast, stay **required**.
- Screwed down, the uplift per desk screw is 24.0 N under the yaw stall and 16.7 N under the hand push (two screws on
  the 52 mm lever).
- The M3 × 50 or #4 wood screws in the spec carry that easily.

## Required changes (FAIL)

**PLATE_T 4 → 7.5 mm round the base servo's tabs.** A local pad under the top plate is enough.

- **Far tab** (x -34.4, which takes 65 % in my model). Pad 7.5 mm thick, reaching at least 15 mm round both of its
  bosses: about x -52 (the wall) … -20, |y| ≤ 25.
  - Result: SF **3.39** under the yaw stall even with fully sharp corners (Kt 2.5); 4.2 with my Kt 2.0.
  - Weight ×2: 5.27.
- **Near tab** (x 14.1, which takes 35 %). The ESP32 cradle starts at y ≈ 10.7, under the plate, with its PCB top at
  Z -10 and the module above it. So the pad there must stop short of the cradle and the board on it.
  - A 5.5 mm pad is enough on this side: SF **3.39** at Kt 2.5; weight ×2 5.26.
  - Check that the pad's underside (Z -5.5) clears the ESP32 module.
- **Cut through the pad:** the lead notches, the window and the pilots, as now.
- **Keep clear of the pad:** the cable slot and the three cradle bosses.
- **7 mm round the far tab** is enough (SF 3.69) if the notch and window corners get a fillet. 6.5 mm (3.18) passes
  only at Kt 2.0.
- **What stays the same.** The tab screws still engage 9 mm, in the thicker plate plus the existing bosses. The servo
  still hangs at the same height, because its tabs sit on the top face.

**Alternative or addition: the ring at zero gap.**

- **How.** The disk rests on the PTFE-taped ring; shim or sand the ring to touch.
- **Result.** The plate's share of the moment falls to 0.33: SF 3.70 at Kt 2.0, but only 2.96 at Kt 2.5.
- **Cost.** Friction while yawing becomes 87–260 N·mm against the servo's 1079 N·mm.
- **Why it is not enough alone.** It works only as well as the gap is set at assembly, so it should not replace the
  thicker plate.

After the plate change every row reaches its required SF, so the verdict becomes NEEDS_TEST.

## Proof test (spec §8)

**Why §8 as written does not prove the plate**

- **The rim test barely loads the servo path.** 50 N on the turntable rim is 0.97 × the yaw-stall ring load, and the
  ring under the load takes it straight down.
- **The arm-up push is missing.** Without it, the plate round the servo tabs is never tested.

Replace the §8 "Proof test" item with:

> **Proof test:** (1) Run the turntable's arm-up test with this base screwed down and the ring fitted (servos powered,
> arm pointing straight up, 11.5 N ≈1.2 kg sideways at the fingertips, 1 min each way). Pass: no cracking or whitening
> in the top plate round the four servo tab bosses, the lead notches or the window corners, and the servo doesn't shift
> in its window. (2) Servo unpowered, press 77 N (≈8 kg on a bathroom or luggage scale) straight down on the turntable
> rim, 1 min at each of 4 positions 90° apart. Pass: no cracking or whitening at the 4 servo pilots and bosses, the 3
> ring pilots or the top plate round the ring; after unloading, the rim returns to within 0.3 mm of its height and the
> running gap still clears. (3) Plug and unplug the USB cable 5 times with the cradle fitted: no cracks at the cradle
> bosses.

**What the replacement tests do**

- **Test (1)** applies 4126 N·mm to the base: **1.59 ×** the design overturning moment that the verdict uses (servo
  path, ring ignored).
  - Because the ring shares more at higher loads, the plate itself sees about 1.24 × its own yaw-stall share
    (play-free servo, 0.4 mm gap).
  - The test proves the base as built, ring included, at 1.59 × its design load.
  - It loads the upper link to 1.75 × at x 15, so run it only after the links' fixes.
- **Test (2).** 77 N is 1.5 × the yaw-stall ring load.
  - The ring checks then stay at SF 6.15 or above.
  - The servo path takes at most 2717 N·mm (1.30 × its yaw-stall share).

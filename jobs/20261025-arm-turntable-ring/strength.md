VERDICT: FAIL

# Strength check: 20261025-arm-turntable-ring (round 5, independent re-check)

strength-analyst (independent review: I did not design this part) · 2026-10-26 ·
`python3 jobs/20261025-arm-turntable-ring/strength_calc.py` (plain Python, no build123d, about 10 s). It reads every
link's `model.py`, `tools/hobby_parts.py`, the claw's `claw_frame.py`, each part's `geometry.json` and the assembly's
`torque_budget.json`, sweeps 47 170 arm poses and prints the tables below.

## Summary

- **FAIL.** Lowest SF **2.26** (4 required): the M3 × 6 pan head (Ø5.5) bearing on the 3 mm tab, at the 150 N snug
  preload. This is a sustained load. The tab creeps under the small head, the clamp relaxes and the screw works loose.
- **Every load row passes.** The lowest is 9.22 (yaw stall, edgewise bending of the wall), with the ring taking the
  whole overturning moment.
- **Change that passes** (hardware, no CAD change): a **Ø7 × 0.5 washer** under each pan head, giving SF 4.72.
  - An M3 × 6 wafer-head screw with a head of Ø7 or more does the same, and keeps the full 3 mm of thread in the base.
- With the washer every row reaches its required SF. The best verdict is then NEEDS_TEST, because the allowables are
  placeholders.
- **Proof test:** the base's rim test must rise from 50 N to **77 N**: 50 N is 0.97 × the yaw-stall ring load.

## What changed since round 4

**Design changes this round**

- **Running gap 1.5 → 0.4 mm**, with PTFE tape on the ring's top (SYS-05). The disk now rests on the ring after 0.52°
  of tilt (0.39° with the tape), so the ring carries part of the overturning moment in normal use.
- **Turntable mounting.** The turntable sits on a Ø25 disc horn (M3 × 14 clamp). Until the ring catches it, the servo
  shaft carries the moment.
- **Claw and camera.** 224.1 g with solid parts.

**How the ring is checked now**

- **The ring takes the whole overturning moment** of every pose, with the servo ignored. The reaction is
  R = M / 42.5, where 42.5 mm is the ring's mid radius. Under the yaw stall that gives R 58.2 N, more than the spec's
  ≈52 N catch.

**Why the lowest SF fell from 3.39 (round 4) to 2.26**

- **The screw-head row is now a sustained case at 150 N.** Round 4 took 100 N and treated it as an assembly case,
  needing SF 3.
- **150 N is the snug preload I assume for every self-tapper in this review.** A preload stays on, so it needs SF 4.
- **At 100 N it would still fail:** 3.39 against 4.

## Load cases

Spec §4 cases, all at 40 °C:

| Case | Load | Duration | How it is applied here |
|---|---|---|---|
| Overturning moment on the turntable (SYS-05) | ×2 dynamic; the ring takes all of it | sustained | "Weight ×2" sweep at the disk underside: 1675 N·mm → R 39.4 N |
| Knock on the arm | 20 N at the turntable rim (r 48) | short-term | R 22.6 N |
| Yaw-stall ring catch | the whole yaw-stall moment, 2473 N·mm | short-term | R 58.2 N |
| Hand push 5 N | 1874 N·mm | short-term | R 44.1 N |
| Friction while yawing | μ 0.1 (PTFE) to 0.3 (worn) | cyclic | Printed against the servo's stall |
| Assembly | M3 × 6 pan heads driven snug | sustained | Head bearing on the tab at 150 N |

**How the sweep is set up**

- **Poses.** Shoulder 0–180, elbow -150 … +30, wrist ±90, in 5° steps. That gives 47 170 poses.
- **Yaw stall.** F = 1079 / R, tangential, at the fingertips or a camera end. It is scaled down wherever a pitch servo
  would back-drive first.
- **Hand push.** 5 N along ±Y, capped where the yaw servo would back-drive.
- **Combining with weight.** Both contact cases add the static weight, component by component, taking the worse sign of
  each.

**Friction while yawing.**

- With the arm straight out and the ring taking the whole static moment, the friction torque is 87 N·mm with PTFE and
  260 N·mm worn.
- The yaw servo's stall is 1079 N·mm, and the 250 °/s² ramp needs another 60–85 N·mm. That is acceptable.

## Assumptions

**Ring wall**

- **Contact patch:** 10 mm of arc × the 3 mm wall. An elastic estimate gives about 20 mm, so this is conservative.
- **Friction:** 0.3 R (PTFE worn through). It bends the wall edgewise over a segment twice the ring's height (32 mm),
  with Kt 2.5 at the wall's root on the tab layer.
- **Shear:** interlayer shear from the same friction.

**Tabs and screws**

- One tab carries the whole friction torque: bearing on the M3 shank, and tear-out to the tab's edge (2.7 mm).
- **Screw head:** 150 N snug preload (assumed; no torque is specified) on the pan head's annulus, Ø5.5 over the Ø3.6
  CAD hole.

**Masses and loads**

- Solid parts × 1.27 g/cm³, ×2 dynamic for weight.
- MG996R stall 1079 N·mm (datasheet).

**Temperature.** 40 °C against PETG softening at about 70 °C. The margin is 30 °C, which is OK.

## Allowables and sources

`library/materials.csv` has only its header, and no job has a datasheet in `inputs/`. These are the strength-checks
**placeholder** values for PETG, so **NEEDS_TEST is the best verdict possible**.

| Quantity | Value | Source |
|---|---|---|
| Tension / bending along the layers (XY) | 25 MPa | strength-checks placeholder, PETG |
| Tension / bending across the layers (Z) | 12.5 MPa | placeholder × 0.5 |
| Shear in-plane / interlayer | 12.5 / 6.25 MPa | 0.5 × the normal value (Tresca), my assumption |
| Bearing (compression, any direction) | 25 MPa | in-plane value |
| Kt | 2.5 wall root (sharp corner) | skill; agent rule Kt ≥ 2 |

Required SF: 3 short-term, 4 sustained or cyclic, and 2 at a 1.5 × proof load.

## Results (copied from `python3 strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | weight x2 (sustained): ring wall bearing under the disk, R 39.4 N on a 10 mm arc (compression) | bearing | 1.31 | 25.00 | 19.03 | 4 | OK |
| 2 | weight x2 (sustained): wall edgewise bending from friction 0.3 R, 32 mm segment (Kt 2.5) | Z | 0.92 | 12.50 | 13.62 | 4 | OK |
| 3 | weight x2 (sustained): interlayer shear in the wall from that friction | Z shear | 0.18 | 6.25 | 34.04 | 4 | OK |
| 4 | weight x2 (sustained): one tab carries the friction torque: bearing on the M3 shank, F 11.0 N | bearing | 1.22 | 25.00 | 20.54 | 4 | OK |
| 5 | weight x2 (sustained): tab tear-out to its edge (2.7 mm) | XY shear | 0.68 | 12.50 | 18.49 | 4 | OK |
| 6 | yaw-stall sweep: ring wall bearing under the disk, R 58.2 N on a 10 mm arc (compression) | bearing | 1.94 | 25.00 | 12.89 | 3 | OK |
| 7 | yaw-stall sweep: wall edgewise bending from friction 0.3 R, 32 mm segment (Kt 2.5) | Z | 1.36 | 12.50 | 9.22 | 3 | OK |
| 8 | yaw-stall sweep: interlayer shear in the wall from that friction | Z shear | 0.27 | 6.25 | 23.06 | 3 | OK |
| 9 | yaw-stall sweep: one tab carries the friction torque: bearing on the M3 shank, F 16.2 N | bearing | 1.80 | 25.00 | 13.92 | 3 | OK |
| 10 | yaw-stall sweep: tab tear-out to its edge (2.7 mm) | XY shear | 1.00 | 12.50 | 12.53 | 3 | OK |
| 11 | hand push 5 N: ring wall bearing under the disk, R 44.1 N on a 10 mm arc (compression) | bearing | 1.47 | 25.00 | 17.01 | 3 | OK |
| 12 | hand push 5 N: wall edgewise bending from friction 0.3 R, 32 mm segment (Kt 2.5) | Z | 1.03 | 12.50 | 12.17 | 3 | OK |
| 13 | hand push 5 N: interlayer shear in the wall from that friction | Z shear | 0.21 | 6.25 | 30.43 | 3 | OK |
| 14 | hand push 5 N: one tab carries the friction torque: bearing on the M3 shank, F 12.3 N | bearing | 1.36 | 25.00 | 18.36 | 3 | OK |
| 15 | hand push 5 N: tab tear-out to its edge (2.7 mm) | XY shear | 0.76 | 12.50 | 16.53 | 3 | OK |
| 16 | 20 N knock on the turntable rim (spec): ring wall bearing under the disk, R 22.6 N on a 10 mm arc (compression) | bearing | 0.75 | 25.00 | 33.20 | 3 | OK |
| 17 | 20 N knock on the turntable rim (spec): wall edgewise bending from friction 0.3 R, 32 mm segment (Kt 2.5) | Z | 0.53 | 12.50 | 23.76 | 3 | OK |
| 18 | 20 N knock on the turntable rim (spec): interlayer shear in the wall from that friction | Z shear | 0.11 | 6.25 | 59.40 | 3 | OK |
| 19 | 20 N knock on the turntable rim (spec): one tab carries the friction torque: bearing on the M3 shank, F 6.3 N | bearing | 0.70 | 25.00 | 35.84 | 3 | OK |
| 20 | 20 N knock on the turntable rim (spec): tab tear-out to its edge (2.7 mm) | XY shear | 0.39 | 12.50 | 32.26 | 3 | OK |
| 21 | assembly: M3 x 6 driven snug, no washer: pan head Ø5.5 on the tab at 150 N (sustained) | bearing | 11.05 | 25.00 | 2.26 | 4 | **FAIL** |

**Lowest SF 2.26 (required 4) at: assembly: M3 × 6 driven snug, no washer: pan head Ø5.5 on the tab (row 21).**

### Advisory rows (not in the verdict)

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | Why it is advisory |
|---|---|---|---|---|---|---|
| proof test (corrected): 77 N on the rim: ring wall bearing, R 87.3 N | bearing | 2.91 | 25.00 | 8.59 | 2 | The corrected proof load |
| proof test (corrected): 77 N on the rim: wall edgewise bending from friction | Z | 2.03 | 12.50 | 6.15 | 2 | as above |
| proof test (corrected): 77 N on the rim: tab tear-out from the friction torque | XY shear | 1.50 | 12.50 | 8.35 | 2 | as above |
| assembly: M3 x 6 driven snug, FIX: Ø7 washer: washer on the tab at 150 N | bearing | 5.30 | 25.00 | 4.72 | 4 | **The fix** |
| assembly: M3 x 6 just snug (100 N), no washer: pan head on the tab | bearing | 7.36 | 25.00 | 3.39 | 4 | Round 4's case: still short of 4 |
| assembly: M3 x 6 driven snug, no washer: thread in the base plate, 3 mm engaged, at 150 N | Z shear | 6.12 | 6.25 | 1.02 | 1 | The thread is in the base (below) |
| assembly: M3 x 6 driven snug, with the Ø7 x 0.5 washer: thread in the base plate, 2.5 mm engaged, at 150 N | Z shear | 7.35 | 6.25 | 0.85 | 1 | as above |

**The thread in the base.** The M3 × 6 can't be longer: the spec says a longer screw would reach the ESP32 under the
plate. Its thread in the base's 4 mm plate is short:

| Engagement | Holds on the placeholder interlayer shear |
|---|---|
| 3 mm (no washer) | about 150 N |
| 2.5 mm (with the washer) | about 130 N |

- Real PETG threads hold several times more, and a thread that strips does so on the bench, where it is seen. So this
  is not a verdict row.
- It does mean: **drive these three screws snug and no harder**. With the washer, 100 N already gives the tab SF 7.

## Required changes (FAIL)

**A Ø7 × 0.5 washer under each of the three M3 × 6 pan heads** (hardware, no CAD change): SF 2.26 → **4.72**.

- These are the same washers as on the servo tab screws.
- **Or** use M3 × 6 wafer-head (flange) self-tappers with a head of Ø7 or more, which keep the full 3 mm of thread.
- Update the spec §2 fastener line and the BUILD_GUIDE to match.
- With this change every row reaches its required SF, so the verdict becomes NEEDS_TEST.

## Proof test (spec §8)

**The spec covers the ring with the base's rim test, at 50 N.** That is 0.97 × the yaw-stall ring load, so it is not a
proof load.

Replace the §8 "Proof test" item with:

> **Proof test:** Covered by the base proof test (77 N, ≈8 kg, straight down on the turntable rim, 1 min at each of 4
> positions 90° apart, servo unpowered). Pass: no cracks in the tabs or the ring wall, no crushing of the ring top (the
> running gap still clears), the washers still tight under the screw heads, and the turntable then turns freely through
> ±90° with no rubbing.

**At 77 N** (1.5 × the yaw-stall ring load) the ring stays at SF 6.15 or above: the wall's edgewise bending is the
lowest.

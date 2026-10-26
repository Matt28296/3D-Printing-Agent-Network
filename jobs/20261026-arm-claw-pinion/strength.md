VERDICT: FAIL

# Strength check: 20261026-arm-claw-pinion (round 1)

strength-analyst · 2026-10-26 · `python3 strength_calc.py` (plain python3; reads `claw_frame.py`, this job's `model.py`,
`tools/hobby_parts.py`, and `gear_outline` from `tools/gears.py` executed without build123d)

The teeth fail at the stall with one jaw blocked, which puts all 24 N on one mesh:

- Standard Lewis, as the spec asks (Y = 0.309 for 18 teeth), gives SF **2.58** against the required 3.
- The tooth `tools/gears.py` actually draws is weaker. With 18 teeth the base circle (r 8.46) lies above the root circle
  (r 7.75), and the tool draws **radial flanks with no fillet** below it. The tooth is only 1.54 mm thick at the root,
  where a generated 18-tooth gear is about 2 mm. Lewis on that tooth gives Y = 0.205: SF **1.71**, and **3.41** for the
  cyclic both-jaw grip (required 4).
- The M2 clamp-screw head bears straight on the counterbore floor with no washer: SF **1.51** (sustained).

The horn stubs and the pocket walls pass.

## Load cases

| # | Case | Load | Where | Type, SF req |
|---|---|---|---|---|
| 1 | Claw stall, one jaw blocked | 216 N·mm → 24 N on one mesh | tooth tip, along the line of action | short-term, 3 |
| 2 | Claw stall, both jaws: every full-close grip | 12 N per mesh | as 1 | cyclic, 4 |
| 3 | Horn torque | 216 N·mm on every full-close grip | trimmed double-arm horn stubs on the pocket walls | cyclic, 4 |
| 4 | Clamp screw (added) | M2 snug, 100 N (same assumption as the ring's M3) | head on the counterbore floor | sustained, 4 |
| 5 | Sideways push on a finger (added) | 5 N hand push / 6.6 N yaw stall | the jaw pitches; its rack's rear end is pried onto the pinion with 24 / 32 N radial | short-term, 3 |

The pinion spec calls normal gripping "≈50 % of stall". The jaw spec, and any servo that is told to close fully on an
object, gives the full stall torque every time. So case 2 uses the full stall as the cyclic load.

## Build direction and sections

The pinion prints horn pocket down with its axis vertical. Tooth bending and pocket-wall bearing run along the layers.

- **Teeth**: Lewis tip load along the line of action. The critical chord is the 1.54 mm root of the radial flank, at r
  7.75.
- **Horn stubs**: arms cut 5.5 from the centre. Each side flat runs from x 1.10 to 4.54 along the arm and the horn is
  1.6 thick. Contact is taken as triangular (peak at the cut end), giving a lever of 3.39 and 31.8 N per stub.
- **Pocket wall ahead of each flat**: the ring from the hub pocket (r 3.85) to the root circle (r 7.75), 3.9 mm thick,
  over the 2 mm pocket depth.
- **Wall between the stub ends and the tooth roots**: 2.00 mm (r 5.75 → 7.75). Its backup ratio is 0.89, below the 1.2
  gear-design limit, so the AGMA rim factor 1.48 is shown as an advisory row. Over the other 6 mm of face width the rim
  is backed by solid gear.

## Assumptions

- Lewis with a tip load and no extra Kf. The tip-load assumption roughly compensates for the root fillet concentration,
  as AGMA's J does at the highest point of single-tooth contact. The printed root corner gets about a 0.2 mm radius from
  the 0.4 mm extrusion.
- Bearing uses the mean pressure on the flat. The triangular peak (11.6 MPa) is noted, not used.
- Prying (case 5): the jaw pitches about the slot edge (x 29.15) and its rack's rear end (x 19.4) presses on the pinion.
  At nominal geometry the tooth tips bottom on the root lands after 0.250 mm of radial approach, before the flanks wedge
  at 0.275 mm. The verdict row uses tip-land bearing. If the flanks wedge instead (printing tolerance), see the advisory
  rows.

## Allowables and sources

`library/materials.csv` has no measured row: these are the strength-checks **placeholder** PETG values. NEEDS_TEST is the
best verdict possible.

| Quantity | Value | Source |
|---|---|---|
| Along the layers (teeth, pocket walls) | 25 MPa | skill placeholder, PETG |
| Shear in-plane | 12.5 MPa | 0.5 × 25 |
| Bearing, compression | 25 MPa | in-plane value |

Required SF is 3 for short-term loads and 4 for cyclic or sustained loads. Service temperature 40 °C: OK.

## Results (copied from `python3 strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | teeth, one jaw blocked, all 24 N on one mesh: Lewis, standard Y 0.309 (spec method) | XY | 9.71 | 25.00 | 2.58 | 3 | **FAIL** |
| 2 | teeth, one jaw blocked, all 24 N on one mesh: Lewis on the actual gears.py tooth (Y 0.205, root 1.54) | XY | 14.65 | 25.00 | 1.71 | 3 | **FAIL** |
| 3 | teeth, both jaws at stall (every full-close grip), 12 N per mesh (cyclic): Lewis, standard Y 0.309 (spec method) | XY | 4.85 | 25.00 | 5.15 | 4 | OK |
| 4 | teeth, both jaws at stall (every full-close grip), 12 N per mesh (cyclic): Lewis on the actual gears.py tooth (Y 0.205, root 1.54) | XY | 7.33 | 25.00 | 3.41 | 4 | **FAIL** |
| 5 | horn stub bearing on the pocket wall, stall torque at every full-close grip (cyclic), flat 3.4 x 1.6 | XY | 5.78 | 25.00 | 4.32 | 4 | OK |
| 6 | pocket wall ahead of a stub flat: ring 3.90 (hub pocket r 3.85 to root r 7.75) x 2 deep, 2 shear planes (cyclic) | XY shear | 2.04 | 12.50 | 6.13 | 4 | OK |
| 7 | assembly: M2 head clamp 100 N on the counterbore floor, no washer (head D3.8) (sustained) | XY | 16.58 | 25.00 | 1.51 | 4 | **FAIL** |
| 8 | hand push 5 N on one finger pries its rack onto the pinion: 24 N radial on 2 tooth tip lands (0.63 wide) (compression) | XY | 2.41 | 25.00 | 10.39 | 3 | OK |
| 9 | yaw-stall sweep on one finger pries its rack onto the pinion: 32 N radial on 2 tooth tip lands (0.63 wide) (compression) | XY | 3.17 | 25.00 | 7.88 | 3 | OK |

Advisory rows (not in the verdict, for the reasons under Assumptions):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| teeth over the pocket depth, one jaw blocked: actual tooth x AGMA rim factor K_B 1.48 (rim 2.00; conservative: the solid face behind restrains the rim) | XY | 21.69 | 25.00 | 1.15 | 3 |
| hand push 5 N: same load if the flanks wedge instead (backlash closes before the tips bottom): tooth bending | XY | 20.22 | 25.00 | 1.24 | 3 |
| yaw-stall sweep: same load if the flanks wedge instead (backlash closes before the tips bottom): tooth bending | XY | 26.65 | 25.00 | 0.94 | 3 |

**Lowest SF: teeth 1.71 (required 3); clamp head 1.51 (required 4).**

## Required changes (computed in the script's what-if lines)

**Teeth** (rows 1, 2, 4). Either of these passes on the actual tooth.

1. **No tool change:** Z_TEETH 18 → 24 and FACE_W 8 → 10 in `claw_frame.py`.
   - Actual-tooth SF goes to 3.33 short-term and 6.65 cyclic.
   - R_P becomes 12, so the stall rack force drops from 24 to 18 N. That relieves the jaws, cover and frame by 25 %.
   - Each rack moves 3 mm further from the axis, so the claw grows 6 mm in z. The full 44 mm opening takes 105° of servo
     travel.
   - m 1.25 with z 18 and face 10 also passes (3.37 / 6.75).
2. **Fix the tool:** give `tools/gears.py` a generated (trochoidal) or r ≥ 0.38 m root fillet, so the tooth root is as
   thick as a standard 18-tooth gear (Lewis Y 0.309), and set FACE_W 8 → 10. That gives 3.22 / 6.44 and keeps the claw's
   height. This is a toolsmith job: the same radial-flank root affects every gear the tool makes with fewer than about
   42 teeth.

FACE_W 10 alone, with the current tool, is not enough (2.13). The rack teeth pass either way, and get wider with
FACE_W.

**Clamp screw** (row 7). Put a Ø6 M2 washer (DIN 9021, the one the wrist joint uses) under the head: counterbore HEAD_D
4.2 → 6.2 and HEAD_H 1.6 → 2.0. SF goes to 5.74. A Ø5 washer gives only 3.58. Tighten snug only.

**Prying margin** (advisory rows). Set BACKLASH 0.1 → 0.15 per member in `claw_frame.py`. A pried rack then bottoms on
the tooth tips 0.16 mm before the flanks can wedge; today the margin is only 0.025 mm. The claw gets 0.1 mm more play
per jaw.

## Proof test (for the redesigned pinion; spec §8 test kept)

Grip a 20 mm wooden block clamped in a vice, first centred, then 8 mm off-centre so one jaw touches first. Command full
close for 10 s, 5 times each. Then push 7.5 N sideways (±z) on one fingertip for 1 min each way.

Pass:

- no tooth damage or whitening on the pinion or racks;
- the horn stubs don't slip in the pocket (pen line across the pinion and the servo case);
- the jaws open again smoothly with no new play.

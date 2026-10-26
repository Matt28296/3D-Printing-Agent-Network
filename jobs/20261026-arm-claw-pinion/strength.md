VERDICT: NEEDS_TEST

# Strength check: 20261026-arm-claw-pinion (round 3)

strength-analyst (independent review of the round-3 geometry) · 2026-10-26 ·
`python3 jobs/20261026-arm-claw-pinion/strength_calc.py` (plain python3, run from the project root: reads `claw_frame.py`,
this job's and the jaw job's `model.py` and `tools/hobby_parts.py` with `ast`, and runs `gear_outline` / `rack_outline`
from `tools/gears.py` on their own)

Round 2's tooth failure is fixed. At FACE_W 12 with the backlash split 0.1 / 0.7, the tooth fillet gives **3.61** with
one jaw blocked; it was 2.85. The racks give 3.95. The pry margin (rack tips bottom before the flanks can wedge) widens
from +0.08 to +0.15 mm.

The 3.7 mm counterbore keeps the 6.3 floor. The torque path beside it gives 60, and the washer row is unchanged at 5.94.
The 0.2 mm mouth chamfer on the horn pocket sits below the horn plate (z 0–0.2 against the plate's 0.4–2.0), so the
stubs' bearing is unchanged. Every verdict row passes; the verdict is NEEDS_TEST only because the allowables are
placeholders.

## Round-2 fixes: made?

| Round-2 required change | Round 3 as built | Made? |
|---|---|---|
| 1. FACE_W 10 → 12, PINION_BACKLASH 0.2 → 0.1, RACK_BACKLASH 0.5 → 0.7 | All three, in `claw_frame.py`; the pinion's teeth 0.05 thinner, the racks' 0.35 (0.40 per mesh) | Yes: 3.61 (row 1), racks 3.95 (row 15), pry margin +0.15 mm |
| 2. Build guide: never force the jaws by hand with the servo powered; clamp screw snug only (≤ 0.06 N·m) | Architect's | Still advisory (rows 17–18); keep it in BUILD_GUIDE |
| Counterbore for the washer with a 6.3 floor at the new face | CB_H = 12 − 2 − 6.3 = 3.7 | Yes: floor 6.3 (row 6), the ring beside it 60 (row 7) |

## Load cases

| # | Case | Load | Where | Type, SF req |
|---|---|---|---|---|
| 1 | Stall, one jaw blocked; the same torque reversed covers the claw opening against an obstacle | 216 N·mm: 21.6 N tangential on one mesh, 22.99 N along the line of action | Tooth fillet | Short-term, 3 |
| 2 | Stall, both jaws: every full-close grip | 10.8 N per mesh | As 1 | Cyclic, 4 |
| 3 | Crash (required) | 13 N along the jaw travel at one fingertip; 130 N·mm < stall, so the servo holds it on one mesh | As 1 | Short-term, 3 |
| 4 | Horn torque | 216 N·mm at every full-close grip | Trimmed horn stubs on the pocket walls; the ring beside the counterbore | Cyclic, 4 |
| 5 | Clamp preload | M2 × 12 snug, 100 N | Ø6 washer on the 6.3 floor | Sustained, 4 |
| 6 | Sideways push on jaw B's tip (advisory) | Yaw stall 7.1 N; hand 5 N. The jaw pries its rack's rear onto the pinion: × 4.15 (round 2: × 5.23; the front plate moved 2 mm forward) | Root lands, or the flanks if they wedge | Short-term, 3 |
| 7 | Jaws forced by hand, servo powered (advisory) | Back-drive at an unmeasured 2–4 × stall | Tooth fillet | Short-term, 3 |

## Build direction and sections

The pinion prints with the horn pocket down and its axis vertical. The tooth profile lies in the bed plane, so tooth
bending and pocket bearing run along the layers (25 MPa).

- **Tooth:**
  - m 1, z 20, 20°, each tooth 0.05 thinner at the pitch line, r 0.38 root fillet, tips topped 0.15 (r_a 10.85);
  - contact ratio 1.52, highest point of single-tooth contact at r 10.169;
  - critical section in the fillet, chord 1.69, Kf 1.78.
- **Effective face:** 12 − 0.25 (the rack's float between its guides) − 0.25 (both parts' bed chamfers, at the same end)
  = 11.5.
- **Horn stubs, pocket wall and clamp:** as round 2. The 6.3 floor is unchanged, under a 3.7 deep Ø6.4 counterbore.

## Assumptions

- The whole normal load is on one tooth at its highest point of single-tooth contact. Kf (Dolan–Broghamer) applies in
  the fillet zone. The radial compression is ignored, which is conservative.
- **Pry.** The jaw pitches on its rack's front-bottom edge, and the rack's rear rises onto the pinion. The rack's tips
  bottom on the pinion's root lands after 0.40 mm of radial approach, and the flanks would wedge after 0.55 mm.
  - ±0.05 mm of print error on each tooth's thickness moves the wedge point by ±0.14 mm. The +0.15 margin therefore just
    covers it.
  - The tip-contact rows are compressive bearing, a dent at worst: advisory, as in round 2.
- The MG90S back-drive torque is unmeasured.
- Service temperature is 40 °C against PETG softening at about 70 °C: OK.

## Allowables and sources

`library/materials.csv` has no measured row, so these are the strength-checks **placeholder** PETG values and
NEEDS_TEST is the best possible verdict.

| Quantity | Value | Source |
|---|---|---|
| Along the layers (teeth, pocket walls) | 25 MPa | Skill placeholder, PETG |
| In-plane shear | 12.5 MPa | 0.5 × 25 (Tresca) |
| Bearing | 25 MPa | In-plane value |
| Fillet factor | Dolan–Broghamer Kf, 20° | The stress-correction factor in AGMA 908's geometry factor |

## Results (copied from `python3 strength_calc.py`)

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | stall, one jaw blocked (or opening against an obstacle): 21.6 N on one mesh | tooth fillet: HPSTC r 10.17, chord 1.69, Kf 1.78, face 11.50 | XY | 6.92 | 25.00 | 3.61 | 3.0 | OK |
| 2 | stall, both jaws (every full-close grip, cyclic): 10.8 N per mesh | tooth fillet (as above) | XY | 3.46 | 25.00 | 7.23 | 4.0 | OK |
| 3 | crash: 13 N along the jaw travel at one fingertip, held by the claw servo | tooth fillet (as above) | XY | 4.16 | 25.00 | 6.00 | 3.0 | OK |
| 4 | horn stubs, stall torque 216 N.mm at every full-close grip (cyclic) | stub flat x 0.77..5.50 x horn 1.6 (mean bearing) | XY | 4.55 | 25.00 | 5.49 | 4.0 | OK |
| 5 | pocket wall ahead of a stub flat (cyclic): shear-out on 2 planes, wall to the root circle x pocket depth | wall 4.75 x 2.0 (backed by the solid face behind) | XY shear | 1.81 | 12.50 | 6.90 | 4.0 | OK |
| 6 | assembly: M2 x 12 snug, 100 N, on the Ø6 washer (sustained) | washer annulus 23.8 mm2 on the 6.3 floor | XY | 4.21 | 25.00 | 5.94 | 4.0 | OK |

**Lowest SF: 3.61 (required 3), the tooth fillet, one jaw blocked at stall.** It is the same for the claw opening
against an obstacle. The clamp screw's preload must stay ≤ 148 N for SF 4 on the washer (about 0.06 N·m: snug only).

Information and advisory rows (not in the verdict):

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 8 | info: one jaw blocked, Lewis tip load, no Kf, full face 12 | tooth root chord 1.68 | XY | 6.04 | 25.00 | 4.14 | 3.0 | OK |
| 9 | info: one jaw blocked, HPSTC + Kf, full face 12 | fillet chord 1.69, Kf 1.78 | XY | 6.63 | 25.00 | 3.77 | 3.0 | OK |
| 10 | info: rim under the 2 mm pocket, backup ratio (r_root - r_pocket) / tooth height | 1.38 >= 1.2: no rim factor | - | 0.00 | 0.00 | - | - |  |
| 11 | advisory: yaw stall 7.1 N sideways on jaw B's fingertip pries its rack onto the pinion: 29 N (lever x4.15); compressive contact, a dent at worst | 1 rack tip land 0.60 x 4.0 on the root land (1-2 teeth, contact length assumed) | XY | 12.23 | 25.00 | 2.04 | 3.0 | **FAIL** |
| 12 | advisory: hand push 5.0 N sideways on jaw B's fingertip pries its rack onto the pinion: 21 N (lever x4.15); compressive contact, a dent at worst | 1 rack tip land 0.60 x 4.0 on the root land (1-2 teeth, contact length assumed) | XY | 8.61 | 25.00 | 2.90 | 3.0 | **FAIL** |
| 13 | advisory: yaw stall, if the flanks wedge instead (tip clearance 0.40 vs wedge at 0.55 radial; tolerance can swap them): 43 N on one pinion flank | tooth fillet, contact length 4.0 | XY | 37.26 | 25.00 | 0.67 | 3.0 | **FAIL** |
| 14 | advisory: hand push, if the flanks wedge instead (tip clearance 0.40 vs wedge at 0.55 radial; tolerance can swap them): 30 N on one pinion flank | tooth fillet, contact length 4.0 | XY | 26.25 | 25.00 | 0.95 | 3.0 | **FAIL** |
| 15 | info (jaw job): rack tooth, one jaw blocked, HPSTC + Kf, face 11.50 | root width 1.88, Kf 1.89 | XY | 6.34 | 25.00 | 3.95 | 3.0 | OK |
| 16 | info (jaw job): rack tooth, one jaw blocked, Lewis tip, no Kf, face 12 | width 1.36 | XY | 5.44 | 25.00 | 4.60 | 3.0 | OK |
| 17 | advisory: jaws forced by hand, servo powered, back-drives at 2 x stall: 43 N on one mesh | tooth fillet | XY | 13.84 | 25.00 | 1.81 | 3.0 | **FAIL** |
| 18 | advisory: jaws forced by hand, servo powered, back-drives at 4 x stall: 86 N on one mesh | tooth fillet | XY | 27.68 | 25.00 | 0.90 | 3.0 | **FAIL** |

About the advisory rows:
- **Rows 11–12 (tip lands, a dent at worst):** 2.04 and 2.90. They were 1.58 and 2.24 in round 2: the lever fell from
  5.23 to 4.15, and the contact length grew to a third of 12.
- **Rows 13–14 (the flanks wedge instead):** they still fail. They apply only if print error eats the 0.15 mm margin;
  the proof test's 10.7 N sideways push checks it.
- **Rows 17–18 (jaws forced by hand with the servo powered):** they still fail. That is a build-guide rule, not a design
  case.

## What-if lines (in the script)

| Option (one jaw blocked) | Pinion | Racks | Pry margin |
|---|---|---|---|
| **As built: face 12, 0.10 / 0.70** | **3.61** | **3.95** | **+0.15** |
| Round 2 for reference: face 10, 0.20 / 0.50 | 2.86 | 3.54 | +0.08 |
| Face 12, 0.10 / 0.80 (0.45 per mesh) | 3.61 | 3.77 | +0.22 |
| Face 12, z 24 (r_p 12) | 4.69 | 4.79 | +0.15 |

## Required changes

None. Keep the two build-guide rules from round 2:
- never force the jaws by hand with the servo powered;
- drive the pinion's clamp screw snug only (≤ 0.06 N·m).

## Proof test (spec §8)

It still matches the round-3 pinion:
- 32 N along the jaw travel at each fingertip (1.5 × the one-jaw stall). At 1.5 × the tooth fillet is at SF 2.4 on the
  placeholder allowables.
- 10.7 N sideways on jaw B, closed and at 44 mm (the pry).
- The 20 mm block grip test.

The pass criteria (no tooth damage or whitening at the roots, no horn slip, smooth 0–44 mm with no new play) still cover
every row here. §2–§3 still quote face 10 and 0.35 backlash, but §1's round-3 note governs. Measure the backlash on the
first print: it should be about 0.40 per mesh.

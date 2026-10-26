VERDICT: FAIL

# Strength check: 20261026-arm-claw-pinion (round 2)

strength-analyst (independent review of the round-2 geometry) · 2026-10-26 ·
`python3 jobs/20261026-arm-claw-pinion/strength_calc.py` (plain python3: reads `claw_frame.py`, this job's and the jaw
job's `model.py` and `tools/hobby_parts.py` with `ast`, and runs `gear_outline` / `rack_outline` from `tools/gears.py`
on their own, so no build123d is needed)

Round 1's fixes are in: 20 teeth, a 10 mm face, r 0.38 root fillets from `tools/gears.py`, topped tips and a Ø6 washer
under the clamp screw. The washer, the horn stubs and the pocket walls now pass with SF 5.49 or more. **The teeth still
fall short at the one-jaw stall: SF 2.85 against 3.**

- The designer's SF 3.25 is arithmetically right. It puts the load at the tooth tip with no fillet factor, which
  usually balances out. It doesn't here: below the base circle (r 9.40) `gears.py` still draws the flank radial down to
  the r 0.38 fillet, so the critical section sits in the fillet, where the stress is concentrated.
- The same tooth by an AGMA-type method gives 3.01 on the full 10 mm face: the load at the highest point of single-tooth
  contact, with the Dolan–Broghamer fillet factor (Kf 1.75). Only 9.45 mm of the face can carry load, because the rack
  floats 0.25 in its guides and both parts have a bed chamfer at the same end. That gives **2.85**.
- A sideways push on jaw B pries its rack onto the pinion. As drawn, the rack's tips bottom on the pinion's root lands
  only 0.08 mm before the flanks would wedge. That margin is within print tolerance. If the flanks wedge, a yaw stall
  breaks a tooth (advisory SF 0.43).

## Round-1 fixes: made?

| Round-1 required change | Round 2 | Made? |
|---|---|---|
| Teeth: z 18 → 24 with face 10, **or** a filleted root in `gears.py` with face 10 | z 20, face 10, r 0.38 root fillets in `gears.py`, tips topped 0.15 | Yes (the tool fix, plus 2 teeth). It isn't enough by the conservative method: row 1 |
| Ø6 washer under the clamp head: counterbore Ø6.2 | Ø6.2 × 1.7 counterbore, 6.3 mm floor, M2 × 12 | Yes: row 6, SF 5.94 |
| Pry margin: thinner teeth, so a pried rack bottoms on the tips before the flanks wedge (+0.16 mm) | 0.35 total backlash, but the topped tips raised the tip clearance from 0.25 to 0.40 | Only partly: the margin is +0.08 mm (round 1: +0.025) |
| Proof test: a sideways push on a fingertip after the grip test | Spec §8 has the grip test only | Not made: see the proof test below |

## The designer's numbers

| Number | Check | Result |
|---|---|---|
| Lewis SF 3.25, one jaw blocked at stall | Row 7 reproduces it: tip load, no Kf, full face, chord 1.63 | Arithmetic right; the method isn't conservative for this radial-flank tooth (rows 8 and 1: 3.01 and 2.85) |
| 10.8 N per jaw at stall | 216 N·mm / r 10 = 21.6 N, half per jaw on a free object | Right as the free-object share. An off-centre object stops one jaw first and puts the full 21.6 N on one mesh: that is the design case (spec §4) |
| 0.35 mm backlash per mesh | `gears.py` thins the pinion's teeth by 0.10 and the racks' by 0.25 at the pitch line; `claw_sequence_check.json` measures 0.327–0.35 | Right in CAD. Printing can move it by about ±0.1 |

## Load cases

| # | Case | Load | Where | Type, SF req |
|---|---|---|---|---|
| 1 | Stall, one jaw blocked (spec). The same torque reversed covers the claw opening against an obstacle (added) | 216 N·mm: 21.6 N tangential on one mesh, 22.99 N along the line of action | Tooth fillet | Short-term, 3 |
| 2 | Stall, both jaws: every full-close grip | 10.8 N per mesh. The spec's "≈50 % of stall" holds only if the sketch never closes fully on an object; a servo told to close on one stalls, so the full stall is the cyclic load | As 1 | Cyclic, 4 |
| 3 | **Crash** (required): the fingertips hit the desk and back-drive the wrist | 13 N at a fingertip, taken all along the jaw travel. 130 N·mm is below the servo's stall, so the servo holds and one mesh carries it | As 1 | Short-term, 3 |
| 4 | Horn torque | 216 N·mm at every full-close grip | Trimmed horn stubs on the pocket walls | Cyclic, 4 |
| 5 | Clamp preload | M2 × 12 snug, 100 N (assumed, as the arm jobs) | Ø6 washer on the 6.3 mm floor | Sustained, 4 |
| 6 | Sideways push on jaw B's tip towards the wrist (advisory) | Yaw stall 7.1 N (the largest out-of-plane part, 1079 / (2 × 76)); hand 5 N. The jaw pitches on its rack's front-bottom edge and pries the rack's rear onto the pinion: × 5.23 | Root lands, or the flanks if they wedge | Short-term, 3 |
| 7 | Jaws forced open or shut by hand with the servo powered (advisory) | The MG90S back-drives at an unmeasured 2–4 × stall | Tooth fillet | Short-term, 3 |

Camera mass and inertia, the camera crash and the cover tie don't load the pinion.

## Build direction and sections

The pinion prints horn pocket down, axis vertical. The tooth profile lies in the bed plane, so tooth bending and pocket
bearing run along the layers (25 MPa).

- **Tooth:** m 1, z 20, 20°, each tooth 0.10 thinner at the pitch line, r 0.38 root fillet, tips topped 0.15 (r_a
  10.85). Base circle r 9.397, root circle r 8.75: between them the flank is radial. Contact ratio 1.52, so the
  highest point of single-tooth contact is at r 10.169. The critical section is the fillet chord, 1.65 mm, with Kf 1.75.
- **Effective face:** 10 − 0.25 (the rack's float between its guides) − 0.3 (the rack's bed chamfer, at the same end as
  the pinion's 0.25 chamfer) = 9.45.
- **Horn stubs:** each flat runs x 0.77–5.50 along the cut arm, 1.6 thick (mean bearing).
- **Pocket wall:** 4.75 from the stub flat to the root circle, 2 deep, sheared on 2 planes and backed by the solid
  face behind. The rim's backup ratio is 1.38 (≥ 1.2), so no rim factor applies (row 9).
- **Clamp:** the Ø6 washer's annulus (23.8 mm²) on the 6.3 mm floor.

## Assumptions

- The whole normal load is on one tooth at its highest point of single-tooth contact. Kf (Dolan–Broghamer, H 0.18,
  L 0.15, M 0.45) applies only in the fillet zone. The direct radial compression is ignored, which is conservative on the
  tension side.
- A pried rack: the jaw pitches on the front-bottom edge of its rack. With the pinion rigid, the rack's rear rises
  0.40 mm onto the pinion before the neck closes its 0.25 mm gap to the cover's strip, so the pinion carries 5.23 × the
  push. If the servo's output gives radially, the cover's strip takes part of it, but the pinion always keeps at least
  3.04 × (the cover report). The contact is taken over a third of the face (3.3 mm) on one tooth.
- **Tips or flanks?** At nominal sizes the rack's tips bottom on the pinion's root lands after 0.40 mm of radial approach,
  and the flanks would wedge after 0.48 mm. Tip contact is compressive bearing: a dent at worst, so those rows are
  advisory. ±0.05 mm of print error on each tooth's thickness moves the wedge point by ±0.14 mm, which can swap the order,
  so the required changes widen the margin.
- The MG90S's back-drive torque is unmeasured; 2 and 4 × stall are shown.
- Service temperature 40 °C against PETG softening at about 70 °C: OK.

## Allowables and sources

`library/materials.csv` has no measured row, so these are the strength-checks **placeholder** PETG values and
NEEDS_TEST is the best possible verdict.

| Quantity | Value | Source |
|---|---|---|
| Along the layers (teeth, pocket walls) | 25 MPa | Skill placeholder, PETG |
| In-plane shear | 12.5 MPa | 0.5 × 25 (Tresca) |
| Bearing | 25 MPa | In-plane value |
| Fillet factor | Dolan–Broghamer Kf, 20° | The stress-correction factor of AGMA 908's geometry factor |

## Results (copied from `python3 strength_calc.py`)

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | Stall, one jaw blocked (or opening against an obstacle): 21.6 N on one mesh | Tooth fillet: HPSTC r 10.17, chord 1.65, Kf 1.75, face 9.45 | XY | 8.78 | 25.00 | **2.85** | 3 | **FAIL** |
| 2 | Stall, both jaws (every full-close grip, cyclic): 10.8 N per mesh | Tooth fillet (as above) | XY | 4.39 | 25.00 | 5.69 | 4 | OK |
| 3 | Crash: 13 N along the jaw travel at one fingertip, held by the claw servo | Tooth fillet (as above) | XY | 5.28 | 25.00 | 4.73 | 3 | OK |
| 4 | Horn stubs, stall torque 216 N·mm at every full-close grip (cyclic) | Stub flat x 0.77–5.50 × horn 1.6 (mean bearing) | XY | 4.55 | 25.00 | 5.49 | 4 | OK |
| 5 | Pocket wall ahead of a stub flat (cyclic): shear-out on 2 planes, wall to the root circle × pocket depth | Wall 4.75 × 2.0 (backed by the solid face behind) | XY shear | 1.81 | 12.50 | 6.90 | 4 | OK |
| 6 | Assembly: M2 × 12 snug, 100 N, on the Ø6 washer (sustained) | Washer annulus 23.8 mm² on the 6.3 floor | XY | 4.21 | 25.00 | 5.94 | 4 | OK |

Information and advisory rows (not in the verdict):

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 7 | Designer's method (info): one jaw blocked, Lewis tip load, no Kf, full face 10 | Tooth root chord 1.63 | XY | 7.70 | 25.00 | 3.25 | 3 | OK |
| 8 | Info: one jaw blocked, HPSTC + Kf, full face 10 | Fillet chord 1.65, Kf 1.75 | XY | 8.30 | 25.00 | 3.01 | 3 | OK |
| 9 | Info: rim under the 2 mm pocket, backup ratio (r_root - r_pocket) / tooth height | 1.38 ≥ 1.2: no rim factor | – | – | – | – | – |  |
| 10 | Advisory: yaw stall 7.1 N sideways on jaw B's fingertip pries its rack onto the pinion: 37 N (lever ×5.23); compressive contact, a dent at worst | 1 rack tip land 0.70 × 3.3 on the root land (1-2 teeth, contact length assumed) | XY | 15.87 | 25.00 | 1.58 | 3 | **FAIL** |
| 11 | Advisory: hand push 5.0 N sideways on jaw B's fingertip pries its rack onto the pinion: 26 N (lever ×5.23); compressive contact, a dent at worst | 1 rack tip land 0.70 × 3.3 on the root land (1-2 teeth, contact length assumed) | XY | 11.18 | 25.00 | 2.24 | 3 | **FAIL** |
| 12 | Advisory: yaw stall, if the flanks wedge instead (tip clearance 0.40 vs wedge at 0.48 radial; tolerance can swap them): 54 N on one pinion flank | Tooth fillet, contact length 3.3 | XY | 58.80 | 25.00 | 0.43 | 3 | **FAIL** |
| 13 | Advisory: hand push, if the flanks wedge instead (tip clearance 0.40 vs wedge at 0.48 radial; tolerance can swap them): 38 N on one pinion flank | Tooth fillet, contact length 3.3 | XY | 41.42 | 25.00 | 0.60 | 3 | **FAIL** |
| 14 | Info (jaw job): rack tooth, one jaw blocked, HPSTC + Kf, face 9.45 | Root width 2.07, Kf 1.92 | XY | 7.09 | 25.00 | 3.53 | 3 | OK |
| 15 | Info (jaw job): rack tooth, one jaw blocked, Lewis tip, no Kf, face 10 (the designer's method) | Width 1.59 | XY | 5.60 | 25.00 | 4.47 | 3 | OK |
| 16 | Advisory: jaws forced by hand, servo powered, back-drives at 2 × stall: 43 N on one mesh | Tooth fillet | XY | 17.56 | 25.00 | 1.42 | 3 | **FAIL** |
| 17 | Advisory: jaws forced by hand, servo powered, back-drives at 4 × stall: 86 N on one mesh | Tooth fillet | XY | 35.12 | 25.00 | 0.71 | 3 | **FAIL** |

**Lowest SF: 2.85 (required 3), the tooth fillet. One jaw blocked at stall.** The clamp screw's preload must stay at or
below 148 N for SF 4 on the washer: about 0.06 N·m, so snug only.

## Required changes (computed in the script's what-if lines)

1. **Teeth:** in `claw_frame.py`, either of these.
   - **FACE_W 10 → 12, PINION_BACKLASH 0.2 → 0.1, RACK_BACKLASH 0.5 → 0.7.** The pinion's teeth then thin by 0.05 and the
     racks' by 0.35: 0.40 per mesh, the top of SYS-08's 0.3–0.4. Pinion **3.60** (cyclic 7.19), racks 3.93, pry margin
     +0.15 mm. The fingers move 2 mm forward, so re-run the cover and frame scripts.
   - **Z_TEETH 20 → 24**, with the same backlash split: pinion 3.85, racks 3.94, margin +0.15 mm. The rack force drops to
     18 N, which relieves the jaws, cover and frame by 17 %. But R_P becomes 12: the claw grows 4 mm in z, the cover's
     pass-through must grow to Ø ≥ 26.6, and 0–44 mm takes 105° of servo.
   - If the Architect accepts 0.45 per mesh, RACK_BACKLASH 0.8 widens the pry margin to +0.22 mm (pinion 3.60, racks
     3.76).
   - Moving the backlash alone (0.0 / 0.7 at face 10) only just passes, 3.09 with the racks at 3.24, and leaves the pry
     margin at +0.08 mm. Z 22 at face 10 gives 3.26, with the same margin.
2. **Build guide** (Architect): never force the jaws open or shut by hand while the servo is powered (rows 16–17). Drive
   the clamp screw snug only: at most 0.06 N·m.

## Proof test

The spec's §8 grip test runs at the servo's own stall, 1.0 × the design load. **Replace it with this**, valid for the
redesigned pinion:

> **Proof test.** Claw assembled, wrist horn in a vice, servo powered and holding, jaws at 30 mm.
> 1. Each fingertip in turn, 3 mm from the tip: pull it along the jaw travel, away from the other jaw, with **32 N**
>    (3.3 kg on a luggage scale, 1.5 × the one-jaw stall force), 10 s. If the servo slips before 32 N, note the force: the
>    teeth have then been proven only to that force.
> 2. Push jaw B's fingertip sideways towards the wrist (−z) with **10.7 N** (1.5 × the yaw stall), 10 s, with the jaws
>    closed and again at 44 mm.
> 3. Then the grip test already in §8: a 20 mm wooden block in a vice, centred and then 8 mm off-centre, 5 full closes
>    each.
>
> Pass:
> - no tooth damage or whitening on the pinion or the racks (look at the tooth roots with a loupe);
> - the horn stubs haven't slipped in the pocket (pen line across the pinion and the servo case);
> - the jaws run 0–44 mm smoothly afterwards, with no tight spot and no new play.

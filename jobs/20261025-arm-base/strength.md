VERDICT: NEEDS_TEST

# Strength check: 20261025-arm-base (links round 5, independent re-check of the round-5 solid)

strength-analyst (independent review: I did not design this part) · 2026-10-26 ·
`python3 jobs/20261025-arm-base/strength_calc.py` from the project root (about 1 min). It reads every link's `model.py`,
`tools/hobby_parts.py`, the claw's `claw_frame.py`, each part's `geometry.json` and the assembly's `torque_budget.json`,
sweeps 47 170 arm poses, runs a plate FE of the top plate (numpy and scipy; recorded values if they are missing) and prints
every row below.

## Summary

- **NEEDS_TEST.** Every row reaches its required SF. The lowest is **3.41** (3 required): the 4 mm plate at the edge of
  the far pad, at its corner (x −19.4, y ±20.5), under the yaw-stall sweep (plate FE, Kt 2.0 for the 7.5 → 4 mm step).
- **Round 4's failure is fixed.** The plate round the tension-side tab boss was SF 1.20 at 4 mm. With the pads it is now:
  - far pad (7.5 mm): **3.67**;
  - near pad (5.5 mm): **4.23**;
  - window corner beside a tab's pivot (plate FE): **3.64**.
- **The designer's re-run of round 4's script passed nothing.** Its plate rows were still hard-coded to the 4 mm plate
  (SF 1.20 FAIL). This script takes the pads' thickness and extent from `model.py`.
- **New failure paths, all checked:**
  - the pad-edge steps (3.41 at the far pad's corner);
  - the near pad's ESP32-side edge (5.30). Under the yaw stall its underside moves 0.13 mm towards the board, against a
    0.5 mm gap;
  - the rest of the 4 mm plate, cable-slot corners included (6.45);
  - the ring screws' 2.5 mm of thread under the round-5 washer (advisory: no service tension).
- **One assumption is now worse than round 4 had it.** The far tab takes **75 %** of the overturning moment, not 65 %
  (plate FE with the servo as a rigid body). The far-tab rows use 0.75.
- **Spec §8:** all three tests still match the design. Test (1) takes the plate to SF 2.15, test (2) the ring path to
  2.43 and the servo path to 2.35 (≥ 2 required at a proof load). Test (1) takes the upper link's x 15 section to SF
  1.96. That is 2 % under the proof margin: acceptable (see "Proof test").

## What changed since round 4

**Design (round 5)**

- Pads under the top plate round the base servo's tabs:
  - far tab, `PAD_FAR`: x −52.5 … −19.4, |y| ≤ 20.5, 7.5 mm;
  - near tab, `PAD_NEAR`: x −0.9 … 29.1, y −20 … 18, 5.5 mm.
- The window, both lead notches and the four tab pilots run through plate + pad + boss.
- Cradle pilots are 7 mm deep.
- The ring screws now have Ø7 × 0.5 washers (ring job). Each one keeps 2.5 mm of thread in this plate, not 3.
- Mass 94.5 cm³ (+4.8). The turntable, upper link and forearm are heavier too, and their centres of mass are
  re-measured here.

**Method (this review)**

- **Moments.** The pose sweep and the masses reproduce `torque_budget.json` (round 5): 706 N·mm with the arm straight
  out, overhung 240 / 161 / 108 N·mm. Servo path under the yaw stall: 2605 N·mm.
- **Plate round the bosses.** Roark's circular plate is kept, now at each pad's thickness.
- **Plate FE (new).** A Mindlin plate of the top plate inside the walls, built for this review:
  - 0.5 mm elements, the walls simply supported (the softer choice);
  - the window, both notches and the cable slot as holes, the pads at their thickness;
  - the servo as a rigid body: tension bosses bonded, pivot bands push only (unilateral contact, iterated);
  - the moment applied on the servo's weak axis, both ways.

  It gives the moment split between the tabs and the stress at the window corners and the pad edges. The hand
  calculation can't bound those, because the pads end inside the Roark plate's 14.85 mm radius.

  Checks against the hand calculation:
  - round the far boss, the FE gives 5.89 MPa under the yaw stall against Roark's 6.82 (Kt 2), so the Roark rows are
    the conservative ones;
  - the FE reproduces round 4's 4 mm failure (34 MPa at the far window corner with no pads, where Roark with Kt 2 gave
    20.7).

## Load cases

Spec §4 cases, all at 40 °C.

| Case | Load | Duration | How it is applied here |
|---|---|---|---|
| Base-servo stall reaction | 1079 N·mm about Z (datasheet; spec 1000) | short-term | Far tab pilot bearing; notch strip tear-out, 5.5 deep |
| Everything on the turntable (SYS-05) | weight ×2 sweep: 1702 N·mm | sustained | Servo path and ring path, SF 4 |
| Base-yaw stall into a side obstacle | sweep: 2605 N·mm at the tabs (2476 at the ring) | short-term | Servo path and ring path, SF 3 |
| Hand push 5 N | sweep: 1958 / 1875 N·mm | short-term | as above |
| Shoulder stall, fingertips on the desk | 2113 N·mm | short-term | Servo path |
| 20 N on the turntable rim | 1811 N·mm | short-term | Servo path; ring path |
| USB insertion / jumper pull | 20 N / 10 N | short-term | Cradle bosses |
| Assembly | tab screws snug, 150 N | sustained | Notch strip splitting; ring screws' thread (advisory) |
| Tipping (SYS-12) | stability | sustained | Desk-screw uplift, printed |

Poses: shoulder 0–180, elbow −150 … +30, wrist ±90, 5° steps; 47 170 poses with the elbow, wrist and fingertips above
the desk. Yaw stall F = 1079 / R tangential at the fingertips or a camera end, scaled down where a pitch servo back-drives
first. Hand push 5 N along ±Y, capped where the yaw servo back-drives. Contact cases add the static weight, the worse sign
of each component.

## Assumptions

**Servo path (verdict): the ring ignored.**

- The whole overturning moment passes through the four tab screws, on the servo's weak axis (the turntable yaws).
- This is also what happens in service. The plate FE gives the servo path 3.45e5 N·mm/rad with the pads, so the disk
  tilts only 0.4 / 44 rad by 3138 N·mm. Before that the ring takes nothing, and the yaw stall is 2605.

**Tension screw and plate round its boss (hand rows)**

- Tension S = share × M / 14.85: the tab pries about its edge, outer screw in tension, inner screw ignored.
- Share: 0.75 at the far tab (FE 0.75; round 4 assumed 0.65), 0.35 at the near tab (FE 0.25; the hand value kept).
- Roark circular plate, supported at 14.85, load over the Ø6.5 boss:

  σ = Kt × 3S / (2π t²) × [(1 + ν) ln(14.85 / 3.25) + 1]

  - t = 7.5 at the far tab and 5.5 at the near tab. Each pad reaches 15.0 / 13.0 mm from its bosses, so it covers the
    Roark plate's radius (the near pad's ESP32 side 1.85 mm short).
  - Kt 2.0 for the notch and window corner beside the boss; 2.5 (fully sharp) as a sensitivity.
  - The FE's peak round the boss lies under Roark's Kt 2 value.

**Plate FE rows (verdict).** Per 1000 N·mm, scaled to each case's moment (linear: no preload, so the same contact set).

- **Window corner beside a tab's pivot.** Peak element, 0.25 mm from the sharp CAD corner, no extra Kt. It is the
  highest stress in either pad.
- **Pad-edge steps.** The highest element of the 4 mm plate within 1 mm of either pad, corners included, × Kt 2.0 for the
  thickness step (sharp in CAD; a printed r ≈ 0.2 on 4 mm gives Kt ≈ 2 for D/d 1.9).
- **4 mm plate elsewhere.** Peak element; it sits at a cable-slot corner.

**Ring path (verdict).** The ring takes the whole moment at r 42.5. The plate under it is taken as a 4 mm strip (a 20.6,
b 65); the far pad under the 180° side is ignored. One ring screw takes 0.3 R of friction, in bearing over the 2.5 mm of
thread left under the round-5 washer.

**Other rows.**
- Notch strip: 1.79 mm behind the thread.
  - Tear-out over 5.5 mm, now that the notches run through plate + pad.
  - Lamé splitting at the 150 N snug preload + S.
- Cradle bosses: unchanged. The pilots are now 7 deep, so the screw still has 6 mm engaged.
- Masses: solid parts × 1.27 g/cm³, ×2 dynamic for the weight case.

**Temperature.** 40 °C, servo cases up to 45 °C, against PETG softening at about 70 °C: margin ≥ 25 °C, OK.

## Allowables and sources

`library/materials.csv` has only its header, and no job has a datasheet in `inputs/`, so these are the strength-checks
**placeholder** PETG values and **NEEDS_TEST is the best verdict possible**.

| Quantity | Value | Source |
|---|---|---|
| Tension / bending along the layers (XY): top plate, pads | 25 MPa | strength-checks placeholder, PETG |
| Tension / bending across the layers (Z): boss roots | 12.5 MPa | placeholder × 0.5 |
| Shear in-plane / interlayer | 12.5 / 6.25 MPa | 0.5 × the normal value (Tresca), assumption |
| Bearing | 25 MPa | in-plane value |
| E, ν | 1800 MPa, 0.35 | skill table; ν assumed |
| Kt | 2.0 notch / window corner and pad step; 2.5 boss roots and as a sensitivity | skill; agent rule Kt ≥ 2 |

Required SF: 3 short-term, 4 sustained, 2 at a proof load (1.5 × service).

## Results (copied from `strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | base stall 1079 N.mm: far tab pilot bearing, F 13.1 N | bearing | 0.87 | 25.00 | 28.79 | 3 | OK |
| 2 | base stall 1079 N.mm: notch -> pilot strip 1.79, 5.5 deep (plate + pad): tear-out, F 13.1 N | XY shear | 0.66 | 12.50 | 18.85 | 3 | OK |
| 3 | weight x2 (sustained): servo path: far tab screw pull-out, M 1702 N.mm on the weak axis, S 86 N (L 9); s0 e0 w0 | Z shear | 1.17 | 6.25 | 5.34 | 4 | OK |
| 4 | weight x2 (sustained): servo path: far pad 7.5 mm round the tension screw's boss (0.75 of M; Kt 2.0) | XY | 4.45 | 25.00 | 5.61 | 4 | OK |
| 5 | weight x2 (sustained): servo path: near pad 5.5 mm round the tension screw's boss (0.35 of M; Kt 2.0) | XY | 3.86 | 25.00 | 6.47 | 4 | OK |
| 6 | weight x2 (sustained): plate FE: window corner beside a tab's pivot (peak element, sharp corner, no extra Kt) | XY | 4.48 | 25.00 | 5.57 | 4 | OK |
| 7 | weight x2 (sustained): plate FE: 4 mm plate at the pad-edge steps (Kt 2.0 for the step) | XY | 4.80 | 25.00 | 5.21 | 4 | OK |
| 8 | weight x2 (sustained): plate FE: 4 mm plate elsewhere, cable-slot corners included (peak element, no extra Kt) | XY | 2.53 | 25.00 | 9.87 | 4 | OK |
| 9 | weight x2 (sustained): notch strip 1.79: splitting, snug preload 150 N + 86 N | XY | 2.63 | 25.00 | 9.52 | 4 | OK |
| 10 | yaw-stall sweep: servo path: far tab screw pull-out, M 2605 N.mm on the weak axis, S 132 N (L 9); s70 e25 w-65, fingertip | Z shear | 1.79 | 6.25 | 3.49 | 3 | OK |
| 11 | yaw-stall sweep: servo path: far pad 7.5 mm round the tension screw's boss (0.75 of M; Kt 2.0) | XY | 6.82 | 25.00 | 3.67 | 3 | OK |
| 12 | yaw-stall sweep: servo path: near pad 5.5 mm round the tension screw's boss (0.35 of M; Kt 2.0) | XY | 5.91 | 25.00 | 4.23 | 3 | OK |
| 13 | yaw-stall sweep: plate FE: window corner beside a tab's pivot (peak element, sharp corner, no extra Kt) | XY | 6.86 | 25.00 | 3.64 | 3 | OK |
| 14 | yaw-stall sweep: plate FE: 4 mm plate at the pad-edge steps (Kt 2.0 for the step) | XY | 7.34 | 25.00 | 3.41 | 3 | OK |
| 15 | yaw-stall sweep: plate FE: 4 mm plate elsewhere, cable-slot corners included (peak element, no extra Kt) | XY | 3.88 | 25.00 | 6.45 | 3 | OK |
| 16 | yaw-stall sweep: notch strip 1.79: splitting, snug preload 150 N + 132 N | XY | 3.13 | 25.00 | 7.98 | 3 | OK |
| 17 | hand push 5 N: servo path: far tab screw pull-out, M 1958 N.mm on the weak axis, S 99 N (L 9); s90 e0 w0, fingertip | Z shear | 1.35 | 6.25 | 4.65 | 3 | OK |
| 18 | hand push 5 N: servo path: far pad 7.5 mm round the tension screw's boss (0.75 of M; Kt 2.0) | XY | 5.12 | 25.00 | 4.88 | 3 | OK |
| 19 | hand push 5 N: servo path: near pad 5.5 mm round the tension screw's boss (0.35 of M; Kt 2.0) | XY | 4.44 | 25.00 | 5.62 | 3 | OK |
| 20 | hand push 5 N: plate FE: window corner beside a tab's pivot (peak element, sharp corner, no extra Kt) | XY | 5.16 | 25.00 | 4.85 | 3 | OK |
| 21 | hand push 5 N: plate FE: 4 mm plate at the pad-edge steps (Kt 2.0 for the step) | XY | 5.52 | 25.00 | 4.53 | 3 | OK |
| 22 | hand push 5 N: plate FE: 4 mm plate elsewhere, cable-slot corners included (peak element, no extra Kt) | XY | 2.91 | 25.00 | 8.58 | 3 | OK |
| 23 | hand push 5 N: notch strip 1.79: splitting, snug preload 150 N + 99 N | XY | 2.77 | 25.00 | 9.02 | 3 | OK |
| 24 | shoulder stall on the desk: servo path: far tab screw pull-out, M 2113 N.mm on the weak axis, S 107 N (L 9) | Z shear | 1.45 | 6.25 | 4.31 | 3 | OK |
| 25 | shoulder stall on the desk: servo path: far pad 7.5 mm round the tension screw's boss (0.75 of M; Kt 2.0) | XY | 5.53 | 25.00 | 4.52 | 3 | OK |
| 26 | shoulder stall on the desk: servo path: near pad 5.5 mm round the tension screw's boss (0.35 of M; Kt 2.0) | XY | 4.80 | 25.00 | 5.21 | 3 | OK |
| 27 | shoulder stall on the desk: plate FE: window corner beside a tab's pivot (peak element, sharp corner, no extra Kt) | XY | 5.57 | 25.00 | 4.49 | 3 | OK |
| 28 | shoulder stall on the desk: plate FE: 4 mm plate at the pad-edge steps (Kt 2.0 for the step) | XY | 5.95 | 25.00 | 4.20 | 3 | OK |
| 29 | shoulder stall on the desk: plate FE: 4 mm plate elsewhere, cable-slot corners included (peak element, no extra Kt) | XY | 3.14 | 25.00 | 7.95 | 3 | OK |
| 30 | shoulder stall on the desk: notch strip 1.79: splitting, snug preload 150 N + 107 N | XY | 2.86 | 25.00 | 8.75 | 3 | OK |
| 31 | 20 N on the turntable rim (spec): servo path: far tab screw pull-out, M 1811 N.mm on the weak axis, S 91 N (L 9) | Z shear | 1.24 | 6.25 | 5.02 | 3 | OK |
| 32 | 20 N on the turntable rim (spec): servo path: far pad 7.5 mm round the tension screw's boss (0.75 of M; Kt 2.0) | XY | 4.74 | 25.00 | 5.28 | 3 | OK |
| 33 | 20 N on the turntable rim (spec): servo path: near pad 5.5 mm round the tension screw's boss (0.35 of M; Kt 2.0) | XY | 4.11 | 25.00 | 6.08 | 3 | OK |
| 34 | 20 N on the turntable rim (spec): plate FE: window corner beside a tab's pivot (peak element, sharp corner, no extra Kt) | XY | 4.77 | 25.00 | 5.24 | 3 | OK |
| 35 | 20 N on the turntable rim (spec): plate FE: 4 mm plate at the pad-edge steps (Kt 2.0 for the step) | XY | 5.10 | 25.00 | 4.90 | 3 | OK |
| 36 | 20 N on the turntable rim (spec): plate FE: 4 mm plate elsewhere, cable-slot corners included (peak element, no extra Kt) | XY | 2.70 | 25.00 | 9.27 | 3 | OK |
| 37 | 20 N on the turntable rim (spec): notch strip 1.79: splitting, snug preload 150 N + 91 N | XY | 2.69 | 25.00 | 9.30 | 3 | OK |
| 38 | spec §8: tab screws driven snug: notch strip 1.79: splitting at 150 N | XY | 1.67 | 25.00 | 14.97 | 4 | OK |
| 39 | weight x2 (sustained): ring path, R 40.1 N: top plate strip a 20.6, b 65, 4 thick | XY | 4.73 | 25.00 | 5.28 | 4 | OK |
| 40 | weight x2 (sustained): ring path: friction 0.3 x R on one ring screw, bearing in the plate pilot (L 2.5: M3 x 6 under a Ø7 x 0.5 washer) | bearing | 1.71 | 25.00 | 14.60 | 4 | OK |
| 41 | yaw-stall sweep: ring path, R 58.3 N: top plate strip a 20.6, b 65, 4 thick | XY | 6.88 | 25.00 | 3.63 | 3 | OK |
| 42 | yaw-stall sweep: ring path: friction 0.3 x R on one ring screw, bearing in the plate pilot (L 2.5: M3 x 6 under a Ø7 x 0.5 washer) | bearing | 2.49 | 25.00 | 10.04 | 3 | OK |
| 43 | hand push 5 N: ring path, R 44.1 N: top plate strip a 20.6, b 65, 4 thick | XY | 5.21 | 25.00 | 4.80 | 3 | OK |
| 44 | hand push 5 N: ring path: friction 0.3 x R on one ring screw, bearing in the plate pilot (L 2.5: M3 x 6 under a Ø7 x 0.5 washer) | bearing | 1.89 | 25.00 | 13.25 | 3 | OK |
| 45 | 20 N on the turntable rim (spec): ring path, R 22.6 N: top plate strip a 20.6, b 65, 4 thick | XY | 2.67 | 25.00 | 9.37 | 3 | OK |
| 46 | 20 N on the turntable rim (spec): ring path: friction 0.3 x R on one ring screw, bearing in the plate pilot (L 2.5: M3 x 6 under a Ø7 x 0.5 washer) | bearing | 0.97 | 25.00 | 25.89 | 3 | OK |
| 47 | USB insertion 20 N / 3 bosses: cradle-boss root bending (Kt 2.5) | Z | 3.05 | 12.50 | 4.10 | 3 | OK |
| 48 | 10 N jumper pull / 2 screws: cradle screw pull-out, 6 mm engaged | Z shear | 0.10 | 6.25 | 61.26 | 3 | OK |

**Lowest SF 3.41 (required 3): the 4 mm plate at the far pad's corner step, yaw stall (row 14).** Next: far pad round the
boss 3.67 (row 11), window corner 3.64 (row 13), far tab screw pull-out 3.49 (row 10), ring path 3.63 (row 41).

### Advisory rows (not in the verdict)

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| yaw-stall sweep: far pad 7.5 mm round the boss, corners fully sharp (Kt 2.5 instead of 2.0) | XY | 8.52 | 25.00 | 2.93 | 3 |
| yaw-stall sweep: near pad 5.5 mm round the boss, corners fully sharp (Kt 2.5 instead of 2.0) | XY | 7.39 | 25.00 | 3.38 | 3 |
| yaw-stall sweep: far pad at round 4's 0.65 share (Kt 2.0) | XY | 5.91 | 25.00 | 4.23 | 3 |
| yaw-stall sweep: plate FE: far / near tension boss (FE peak, compare the Roark rows) | XY | 5.89 | 25.00 | 4.25 | 3 |
| yaw-stall sweep: plate FE: 4 mm plate at the near pad's ESP32-side edge (y 18; Kt 2.0) | XY | 4.72 | 25.00 | 5.30 | 3 |
| yaw-stall sweep with a 15 kgf.cm clone MG996R: plate FE: window corner beside a tab's pivot | XY | 9.36 | 25.00 | 2.67 | 3 |
| yaw-stall sweep, tab screws over-tightened to 300 N: notch strip 1.79: splitting | XY | 4.80 | 25.00 | 5.20 | 3 |
| assembly: ring M3 x 6 driven snug, no washer (round 4): thread in the 4 mm plate, 3 mm engaged, at 150 N | Z shear | 6.12 | 6.25 | 1.02 | 1 |
| assembly: ring M3 x 6 driven snug, Ø7 x 0.5 washer (round 5): thread in the 4 mm plate, 2.5 mm engaged, at 150 N | Z shear | 7.35 | 6.25 | 0.85 | 1 |

Why each one is advisory:
- **Kt 2.5 rows (2.93 far, 3.38 near).** Fully sharp corners, a sensitivity. The FE (which models the corners) peaks
  under the Kt 2.0 Roark value. The far pad was sized at 0.65 of M; at 0.75 its Kt 2.5 margin has gone.
- **0.65 share (4.23).** Round 4's split, for comparison.
- **FE at the bosses (4.25)** and **the ESP32-side pad edge (5.30).** Cross-checks of verdict rows.
- **Clone MG996R (2.67).** A 15 kgf·cm clone is not a spec case (01 N1).
- **Over-tightened tab screws (5.20).**
- **Ring screws' thread in this plate.**
  - 150 N of snug preload on 2.5 mm of thread gives 0.85 on the placeholder interlayer shear (1.02 with round 4's
    3 mm).
  - The ring screws carry no service tension: the disk only presses down on the ring, and the friction acts in its
    plane. So this is about assembly torque, not strength.
  - Real PETG threads hold several times the placeholder, and a stripped thread shows on the bench.
  - Keep BUILD_GUIDE's "snug, no harder". If one spins, an M3 × 6 wafer-head screw without the washer gets the 3 mm
    back.

**Clearance.** The near pad's underside (Z −5.5) is 0.5 mm above the ESP32's 4 mm parts envelope. The FE moves it at most
0.13 mm under the yaw stall: about 4 × margin.

**Stability (SYS-12).** Free-standing SF 0.34–0.48 (torque_budget), so the desk screws, the 200 × 200 board or the
ballast stay **required**. Screwed down, the uplift is 24.0 N per desk screw under the yaw stall.

## Proof test (spec §8): still matches the design

- **(1) Arm-up push, 11.5 N at the fingertips.**
  - The servo path sees 4128 N·mm, **1.58 ×** the yaw stall (ring ignored).
  - The lowest servo-path or plate row is then SF 2.15, the ring path 2.28 (≥ 2 required).
  - It loads the round-5 pads and the window corners where they are weakest, so it proves the fix.
  - Across the arm, it takes the upper link's x 15 section to 1.75 ×, SF 1.96. That is 2 % under the proof margin.
  - 11 N would give the upper link 2.04, but the turntable's window bottom would then see only 1.43 ×. I would keep
    11.5 N.
- **(2) 77 N straight down on the rim at 4 positions.**
  - 1.49 × the yaw-stall ring load; ring rows SF ≥ 2.43.
  - With the ring sharing past the 0.4 mm gap, the servo path takes 3776 N·mm (1.45 ×), lowest row 2.35.
- **(3) USB plug and unplug 5 times.** The cradle-boss row (SF 4.10 at 20 N) covers it.

VERDICT: FAIL

# Strength check: 20261026-arm-claw-jaw (round 2)

strength-analyst (independent review of the round-2 geometry) · 2026-10-26 ·
`python3 jobs/20261026-arm-claw-jaw/strength_calc.py` (plain python3: reads `claw_frame.py`, this job's `model.py` and
`tools/hobby_parts.py` with `ast`, and runs `rack_outline` from `tools/gears.py` on its own. Add `--cad` in the CAD venv
to compare the hand sections with the build123d solid)

Round 1's candidate C is in: the 10 mm rack back, the 20 × 10 neck with r 4 fillets, the 12 mm finger root, the
full-height gusset and r 3 at every kink. The neck and the finger root now pass every case; the lowest there is 3.44, at
the neck root.

**The jaw now fails at the fingertip: SF 2.62**, with one jaw blocked. The critical section is the V-groove at x 72.6,
where the finger has tapered to 6.3 mm.

- The spec puts the 21.6 N grip 3 mm from the tip. At the grip face's bottom corner it bends the thin tip across the
  layers and twists it.
- The grooves' sharp roots (Kt 2.5) sit on the face in tension.
- With no grooves past x 66, or with a 7 mm tip, the jaw gives 3.44.

The rack teeth pass by the conservative method (3.53).

## Round-1 fixes: made?

| Round-1 required change (candidate C) | Round 2 | Made? |
|---|---|---|
| RACK_BACK 6 → 10 | RACK_BACK 10 | Yes |
| A 10 mm-tall neck on the rack's solid back; NECK_Y 14 → 20 | NECK_Z (11.25, 21.25), NECK_Y 20 | Yes |
| Rack two teeth longer at −y (RACK_Y[0] −5π → −7π) | −8π: the rack ends in tooth gaps at both ends | Yes |
| Finger 12 thick to x ≈ 51, tapering to 6 by x ≈ 66 | 12 thick to x 58.35, 6 by x 73.35. The claw grew, so the finger starts at x 38.35 | Yes, moved out with the finger |
| Full-height 45° gusset; flat top at the neck's top | Full-height gusset. The top runs flat to x 53.35, then drops at 45° to the grip zone (r 3 at the kink) | Yes. The 45° drop is new (lighter, and the camera sees the tips over it); its kink is checked (Kt 1.7) and doesn't govern |
| r ≥ 4 at the neck root; r ≥ 3 at the kinks and the gusset end | r 4 at both y edges of the neck; r 3 at the side kink, the top kink, the gusset end and the taper end | Yes |
| Cover: keep a strip of front plate above slot A | Not made. The tie backs the strip below slot A instead | Checked in the cover report |

## Load cases

| # | Case | Load | Point and direction | Type, SF req |
|---|---|---|---|---|
| 1 | Stall, one jaw blocked (spec) | 216 N·mm / r 10 = 21.6 N | Grip face, 3 mm from the tip (x 80.35), at its bottom, middle and top; also at x 50, 60 and 70. Along y, away from the other jaw | Short-term, 3 |
| 2 | Stall, both jaws: every full-close grip | 10.8 N per jaw. The designer's 10.8 N is right as the free-object share | As 1 | Cyclic, 4 |
| 3 | Added: the claw opens against an obstacle | 21.6 N on the outer face | As 1, reversed | Short-term, 3 |
| 4 | **Crash** (required): fingertips on the desk, wrist back-driven | 13 N at the tip in the arm plane (claw x-y), every 15°; SYS-11's arm push | Tip, at z −6, 0 and +6 from the axis | Short-term, 3 |
| 5 | Yaw stall (arm review) | 7.1 N along ±z, the largest out-of-plane part of a base-yaw stall (1079 / (2 × 76)) | Tip | Short-term, 3 |
| 6 | Handling | 5 N in any direction (every 30° in plan, five elevations) | Tip | Short-term, 3 |
| 7 | Rack teeth | 21.6 N one jaw, 10.8 N both. The crash's 13 N along y: 130 N·mm is below the stall, so the servo holds it on one mesh | Teeth | Short-term 3 / cyclic 4 |
| 8 | Rack ends on the guides | The couple of case 1 at the rack's ends: 27.5 N with the jaws open, 20.1 N closed | Lip or rail and the front plate | Short-term, 3 |

Camera inertia and the cover tie don't load the jaw.

## Build direction and method

The jaw prints standing on the rack's back end (claw x = print Z). Every normal stress along x in the neck and the
finger, and every shear on a plane x = const, acts across the layers: 12.5 MPa normal, 6.25 MPa shear. The rack teeth
are drawn in the bed plane: 25 MPa.

- **Sections:** at every 0.1 mm from the rack face to 3 mm short of the load, the section is the plan outline's y range
  times the side outline's z range, minus the grip face's V-notch and, at each groove centre, the 0.6 mm groove. That
  polygon gives the exact A, centroid and I_yy, I_zz and I_yz. Examples: x 32.6 (neck root) A 200, I_yy 1667, I_zz 6667;
  x 46.35 (gusset end) A 216; x 58.35 (taper start) A 298; x 73.35 (taper end) A 118, I_zz 345; x 80 A 76, I_zz 107.
- **Stress:** normal stress at every vertex from N, M_y and M_z (unsymmetric bending), each term times the Kt of the face
  the vertex sits on. Shear: torsion (Roark rectangle) plus 1.5 V/A. Combined across the layers:
  (σ/12.5)² + (τ/6.25)² = 1/SF². The "Z comb" rows show 12.5/SF as the stress.
- **Kt:**
  - neck root: 1.7 on the y faces (r 4, r/h 0.2); 2.5 on its bottom face, where the rack's teeth leave a sharp 2.1 mm
    step; 1.0 on top, flush with the rack's back;
  - r 3 kinks: 1.5 (side kink, gusset end, taper end), 1.7 (top kink, 20 tall);
  - V-grooves: **2.5**. They are 0.6 deep and 90°, with a sharp root that prints at about r 0.2. That is the skill's
    sharp-corner value; Peterson's V-notch charts give 2.5–2.8 at r/d 0.04. Round 1 used 2.0.
- **Rack teeth:** the pinion report's method. The load is at the rack's own highest point of single-tooth contact, with
  the Dolan–Broghamer fillet factor in the root, on an effective face of 10 − 0.25 (float) − 0.3 (bed chamfer) = 9.45.

## Assumptions

- The stall force is the same anywhere along the grip face, so the tip and the face's corners are the worst points. At
  the corner farthest from the jaw's own rack (z −8.5 from the axis), the grip also twists the finger.
- When the jaw is pushed sideways, the cover's strip and the pinion can prop the neck. That is ignored here, which is
  conservative for the neck.
- The crash force is SYS-11's arm push, 13 N. The wrist's back-drive torque is unmeasured.
- Service temperature 40 °C against PETG softening at about 70 °C: OK.

## Allowables and sources

`library/materials.csv` has no measured row, so these are the strength-checks **placeholder** PETG values and
NEEDS_TEST is the best possible verdict.

| Quantity | Value | Source |
|---|---|---|
| Along the layers (rack teeth, bearing) | 25 MPa | Skill placeholder, PETG |
| Across the layers (all neck and finger bending) | 12.5 MPa | 0.5 × in-plane |
| Interlayer shear | 6.25 MPa | 0.5 × 12.5 (Tresca) |
| Kt | 2.5 sharp; 1.5 for r ≥ 0.25 h; 1.7 for r/h 0.15–0.25 | Skill; the 1.7 is a Peterson-based interpolation |

## Results (copied from `python3 strength_calc.py`)

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | Grip at stall, one jaw blocked, 21.6 N on the grip face [x 80.35 z −8.5] | x 72.6: σ 3.96, τ 1.33 | Z comb | 4.76 | 12.50 | **2.62** | 3 | **FAIL** |
| 2 | Grip at stall, both jaws, 10.8 N each (every full-close grip, cyclic) [x 80.35 z −8.5] | x 72.6: σ 1.98, τ 0.66 | Z comb | 2.38 | 12.50 | 5.25 | 4 | OK |
| 3 | Added: claw opening against an obstacle, 21.6 N on the outer face [x 80.35 z −8.5] | x 32.6: σ 2.63, τ 1.25 | Z comb | 3.63 | 12.50 | 3.44 | 3 | OK |
| 4 | Crash: 13 N at the fingertip in the arm plane, any direction (wrist back-driven) [tip z −6, 285°] | x 72.6: σ 3.45, τ 0.59 | Z comb | 3.65 | 12.50 | 3.43 | 3 | OK |
| 5 | Yaw stall: 7.1 N out of the arm plane at the fingertip, either way [tip z −6, along +z] | x 32.6: σ 2.70, τ 0.18 | Z comb | 2.73 | 12.50 | 4.59 | 3 | OK |
| 6 | Handling: 5 N at the fingertip, any direction [tip z −6, 330° in plan, 45° elevation] | x 32.6: σ 2.17, τ 0.05 | Z comb | 2.17 | 12.50 | 5.76 | 3 | OK |
| 7 | Rack teeth, one jaw blocked (21.6 N), HPSTC + Kf, face 9.45 | Root width 2.07, Kf 1.92 | XY | 7.09 | 25.00 | 3.53 | 3 | OK |
| 8 | Rack teeth, both jaws (10.8 N, cyclic), HPSTC + Kf | Root width 2.07, Kf 1.92 | XY | 3.55 | 25.00 | 7.05 | 4 | OK |
| 9 | Rack teeth, crash 13 N along y on one finger (held by the claw servo) | Root width 2.07, Kf 1.92 | XY | 4.27 | 25.00 | 5.86 | 3 | OK |
| 10 | Rack bar bending between its end contacts, one jaw blocked (couple 1139 N·mm, stress along y: in the bed plane) | Solid back 10 × 10 | XY | 6.84 | 25.00 | 3.66 | 3 | OK |
| 11 | Rack end on the lip / front plate, thrust 27.5 N (jaws open; 20.1 closed), compression across the layers | 3 mm × 10.0 of the end face | Z comp | 0.92 | 25.00 | 27.26 | 3 | OK |

Information rows (not in the verdict):

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 12 | Info: rack teeth, one jaw blocked, Lewis tip load, no Kf, face 10 (the designer's method) | Width 1.59 | XY | 5.60 | 25.00 | 4.47 | 3 | OK |

**Lowest SF: 2.62 (required 3), the groove at x 72.6 near the tip. One jaw blocked, grip at the bottom corner.**

For reference, the same grip with every Kt set to 1 gives 3.93, and the neck root alone gives 3.44.

## Required changes (computed in the script's what-if lines)

1. **The fingertip:** either of these.
   - **BLADE_T 6 → 7** in `claw_frame.py` (the tip 7 mm thick, every groove kept): **3.44**. The neck root then
     governs. The grip face stays on y = 0, so the extra millimetre goes on the outer face, and the tip bevel keeps the
     tip thin for small parts.
   - **Stop the grooves at x 66** (GROOVE_X ends at 66, so only 60.6, 62.6 and 64.6 remain): **3.44**. Stopping at x 70
     gives 3.09, with no margin.
   - Rounding the groove roots to r 0.3 (Kt 2.0) gives 3.03, but a 0.4 mm nozzle can't print an r 0.3 root reliably.
     Not recommended.
2. **Rack teeth with the pinion report's change** (FACE_W 12, RACK_BACKLASH 0.7): 3.93; with 0.8: 3.76. FACE_W 12 moves
   the rack face and the whole finger 2 mm forward together, so the jaw's own lever arms don't change.

## Proof test

The spec's §8 test runs at the servo's own stall (1.0 ×) and hangs 2 N from a dowel. It doesn't reach 1.5 × at the
fingertip, the neck root or the sideways cases. **Replace it with this**, valid once the changes above pass:

> **Proof test.** Claw assembled, wrist horn in a vice, servo powered and holding, jaws at 30 mm. For each jaw in turn:
> 1. Loop a cord round the finger 3 mm from the tip, at the edge of the grip face farthest from the jaw's own rack. Pull
>    away from the other jaw with **32 N** (3.3 kg on a luggage scale, 1.5 × the one-jaw stall), 10 s.
> 2. At the same place, push towards the other jaw on the outer face with **32 N** (1.5 × the opening stall; 20 N,
>    1.5 × the 13 N crash, if the Architect drops that case), 10 s.
> 3. Push the fingertip sideways (±z) with **10.7 N** (1.5 × the yaw stall), 10 s each way.
> 4. Then the checks §8 already has: the grip test as for the pinion (centred and 8 mm off-centre, 5 full closes each),
>    and a 10 mm wooden dowel gripped at the fingertips with 200 g hanging from it for 1 min.
>
> If the servo slips before a pull reaches 32 N, note the force: the jaw has then been proven only to that force.
>
> Pass:
> - no crack or whitening at the grooves nearest the tip, the taper's end, the neck's root fillets, the gusset or the
>   kinks (use a loupe; whitening runs along a layer line);
> - the dowel doesn't slip;
> - the jaws still slide freely and meet flat (0.2 mm feeler at most).

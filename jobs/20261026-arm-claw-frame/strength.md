VERDICT: NEEDS_TEST

# Strength check: 20261026-arm-claw-frame (round 5, independent review)

strength-analyst (independent; did not design the part) · 2026-10-26 · `python3 jobs/20261026-arm-claw-frame/strength_calc.py`
(plain python3, from the project root). The CAD engineer's round-5 strength.md was a self-check; this file replaces it.
The script's method is round 4's (strength-analyst). This review re-ran it, checked the round-5 rows against the
geometry and against the cover's independent model, and added the rows below.

## Verdict

**Every verdict row passes. NEEDS_TEST only because the allowables are placeholders** (no library row for PETG).

- **Lowest SF 3.03** (row 39): the cover's top M3 × 10 screws pulling out of the bulkhead top, opening stall on jaw B,
  no camera mount. This bound, kept since round 4, puts all of the cover's moment on its top screws, as if the second
  post held nothing. It therefore also covers the cover's as-printed ridge play.
- **Lowest of the frame's own load cases: 3.53** (row 4): floor punching under the Ø8 washer when the camera hits the
  desk. Unchanged.
- **The V-groove rows:**
  - flank bearing 3.61 (row 50; proof 2.85, row 52);
  - the block in front of the groove sheared along the groove's bottom (interlayer) 6.66 (row 51; proof 5.24, row 53).
- **The M3 × 45 anchor, 10.75 engaged:**
  - pull-out on the preload 4.22 (row 42, sustained, req 4);
  - preload + wedge + lift 3.42 (row 43);
  - proof 3.26 (row 45);
  - thread forming in the 2.65 walls 3.75 (row 48).
- **New rows 46–47: the cover's as-printed play.** With the ridge's realistic play (0.082 mm RSS, cover strength.md)
  and the preload crept away, the foot slides before the flank bears, and the cover's model sends up to 106 N (115 N
  at the proof push) of lift to the screw. Pull-out is then 5.97 / 5.49.
- **The frame is not where the claw's round-5 problem is.** It is the cover's seat, and its fix needs one change on this
  part: the bulkhead top at 48.45 (design_review.md). That change does not alter any row here; the printed height stays
  48.4. With the fix the cover's ridge bears on a 0.64 mm band instead of 0.71 (its tip at 17.35), so row 50 becomes
  3.20 and row 52 2.53. The fix's other numbers are in the cover's strength.md.

## Review items

### 1. The ligament between the V-groove and the anchor pilot (new info row 63)

**What the self-check missed.** The round-5 self-check said this 0.95 mm wall "carries no hoop load of its own". It
does. It is the pilot's wall on the groove side, so the M3's thread forming presses on it.

**Lame on the thinnest ring it leaves:**
- printed: pilot Ø2.5, groove edge 16.0 at the top layer, so 1.10 thick (CAD 0.95);
- peak ×1.79 on 4.6 + 0.85 MPa → **SF 2.55** at installation.

**Why it is information and not a verdict row:**
- **It is conservative.** Lame with the top layer's thickness is a lower bound. The ligament thickens 1 mm per mm down
  (1.3, 1.5, 1.7) and its layers are bonded. Averaged over the top 0.8 mm (w ≈ 1.5) it is ≈ 3.0.
- **It acts once.** The stress exists only while the screw forms its thread.
- **A split loses no load path.** The split would sit on the groove's +x flank beside the pilot, and that face is
  backed by the screw itself for the cover's push.
- **The thread lost is small.** The top ~0.8 mm × a quarter of the circumference: pull-out on the preload 4.22 → 4.14
  (info row 64, req 4).
- **It is checked.** The first assembly shows it. Suggested spec §8 line in the report.

### 2. The groove's x span (cover item 5)

- Model: x 14.45–16.05 at the block top, centre 15.25 (`VSEAT_XC = LIP_X0 + 0.1 + VSEAT_D`).
- The cover's ridge uses the same constant. Sections at y 26 and 30 match: 0 mm³, 0.0707 normal gap per flank in CAD.
- Round 4's review text said 14.35–15.95, but round 4's own what-if code used `LIP_X0 + 0.1` = 14.45, as built.
- The 0.1 shift costs 0.1 of ligament (1.05 → 0.95 CAD). Moving it back would raise item 1 only from 2.55 to about 2.7,
  so it is not required.

### 3. Forces taken from the cover

From the cover's independent script (worst of 64 variants):

| Mode | Opening stall | Proof push |
|---|---|---|
| Zero play ('locked', as the fix gives) | Fx 25.6 N, lift 10.0 N; screw carries Fx + lift = 35.1 N, plus the snug preload where that makes a row worse | Fx 32.5 N, lift 12.7 N; 44.5 N |
| As printed today, play 0.082 mm, preload gone | Fx ≤ 10 N reaches the groove; wedge + lift up to 106 N on the screw | wedge + lift 115 N |

Both sets are in the table.

## Slice facts (the arm's own command on this job's committed part.stl, G-code read back; a scratch slice)

| Feature | CAD | Printed | Note |
|---|---|---|---|
| Bulkhead top | 48.5 | 48.4 | Exactly the slice plane of layer 48.4–48.6; the slicer dropped that layer |
| Rail block top | 17.75 | 17.8 | |
| Groove walls | 45° flank | vertical steps, half-widths 0.15 / 0.35 / 0.55 / 0.75 in the layers ending 17.2 / 17.4 / 17.6 / 17.8 | Centred on x 15.25 |
| Groove's first layer | 0.3 slot | a slot between two external perimeters | Closes up in print |
| Ligament to the pilot (top layer) | 0.95 | two external perimeters, 0.52 wide each | Prints solid |

## Method, sections and allowables

As round 4: placeholder PETG (no library row); stresses mapped to the layers.
- **The frame prints back face down.**
  - wrist-plate bending runs along the layers: 25 MPa;
  - bending of the bulkhead, ribs and rail block about their roots runs across them: 12.5 MPa;
  - pull-out and punching shear are interlayer: 6.25 MPa;
  - hoop round a vertical pilot runs along the layers: 25 MPa.
- **Kt:** 2.5 sharp, 2 at holes, 1.5 / 1.7 at fillets.
- **Required SF:** 3 short-term, 4 sustained or cyclic, 2 at the proof load.
- **The cover's forces** come from its own strength_calc.py output, quoted in the rows.
- **Temperature:** 40 °C against PETG at ~70 °C, OK.
- **Tab-pilot strips** (rows 65–72): a user-accepted deviation (26 Oct 2026), with the first-print screw-strip check in
  spec §8. Unchanged.

## Results (from `strength_calc.py`, verbatim)

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | USB tug 10 N at the plug (z 91.6), across the shaft: washer bearing (M_t 896 N.mm -> screw 249 N) | Ø8 x 0.8 washer on the pad, 44.5 mm2 (its Ø2.7 bore) | Z comp | 5.59 | 25.00 | 4.47 | 3 | OK |
| 2 | USB tug 10 N at the plug (z 91.6), across the shaft: floor punching under the washer | Ø8 x 6.3 floor | Z shear | 1.57 | 6.25 | 3.98 | 3 | OK |
| 3 | added: camera hits the desk, 13 N at its end (z 79.6): washer bearing (M_t 1009 N.mm -> screw 280 N) | Ø8 x 0.8 washer on the pad, 44.5 mm2 (its Ø2.7 bore) | Z comp | 6.29 | 25.00 | 3.97 | 3 | OK |
| 4 | added: camera hits the desk, 13 N at its end (z 79.6): floor punching under the washer | Ø8 x 6.3 floor | Z shear | 1.77 | 6.25 | 3.53 | 3 | OK |
| 5 | crash: 13 N in the arm plane at the fingertip (z <= 33.2): washer bearing (M_t 406 N.mm -> screw 113 N) | Ø8 x 0.8 washer on the pad, 44.5 mm2 (its Ø2.7 bore) | Z comp | 2.53 | 25.00 | 9.87 | 3 | OK |
| 6 | crash: 13 N in the arm plane at the fingertip (z <= 33.2): floor punching under the washer | Ø8 x 6.3 floor | Z shear | 0.71 | 6.25 | 8.77 | 3 | OK |
| 7 | weight x3 incl. the 250 deg/s2 ramp (cyclic): 3 x the 50 g overhung moment (134 N.mm, torque_budget round 3): washer bearing (M_t 401 N.mm -> screw 111 N) | Ø8 x 0.8 washer on the pad, 44.5 mm2 (its Ø2.7 bore) | Z comp | 2.50 | 25.00 | 9.99 | 4 | OK |
| 8 | weight x3 incl. the 250 deg/s2 ramp (cyclic): 3 x the 50 g overhung moment (134 N.mm, torque_budget round 3): floor punching under the washer | Ø8 x 6.3 floor | Z shear | 0.70 | 6.25 | 8.88 | 4 | OK |
| 9 | SYS-04 overhung moment, 50 g, x1.3 moving (sustained): washer bearing (M_t 174 N.mm -> screw 100 N) | Ø8 x 0.8 washer on the pad, 44.5 mm2 (its Ø2.7 bore) | Z comp | 2.25 | 25.00 | 11.13 | 4 | OK |
| 10 | SYS-04 overhung moment, 50 g, x1.3 moving (sustained): floor punching under the washer | Ø8 x 6.3 floor | Z shear | 0.63 | 6.25 | 9.90 | 4 | OK |
| 11 | added: yaw stall 7.1 N along the wrist axis at the fingertip (x 83.3), pulling the claw off the horn: washer bearing (M_t 592 N.mm -> screw 171 N) | Ø8 x 0.8 washer on the pad, 44.5 mm2 (its Ø2.7 bore) | Z comp | 3.85 | 25.00 | 6.49 | 3 | OK |
| 12 | added: yaw stall 7.1 N along the wrist axis at the fingertip (x 83.3), pulling the claw off the horn: floor punching under the washer | Ø8 x 6.3 floor | Z shear | 1.08 | 6.25 | 5.77 | 3 | OK |
| 13 | wrist stall 216 N.mm (cyclic): horn arm on the pocket wall | arm flank r 3.6..16.1 x 1.6 (mean, resultant at r 11.9) | XY | 0.91 | 25.00 | 27.62 | 4 | OK |
| 14 | crash: 13 N at the fingertip x 83.3 back-drives the wrist (1084 N.mm, 5 x stall: the top of SYS-11's 3-5 x): horn arm on the pocket wall | arm flank r 3.6..16.1 x 1.6 (mean, resultant at r 11.9) | XY | 4.54 | 25.00 | 5.51 | 3 | OK |
| 15 | stall, one jaw blocked, jaws 44 open: rack B's +y end at the block's end, R 27.0 N | rail block root, rack side with the anchor's Ø2.7 pilot in it (round 4): b_eff 7.9, depth 12.35, lever 5.9; I 1194; face Kt 2.5 2.11 / pilot edge Kt 2 0.98 MPa | Z | 2.11 | 12.50 | 5.93 | 3 | OK |
| 16 | stall, one jaw blocked, jaws closed: rack B's +y end at y 25.1, R 19.8 N | rail block root, rack side with the anchor's Ø2.7 pilot in it (round 4): b_eff 13.8, depth 12.35, lever 5.9; I 2118; face Kt 2.5 0.86 / pilot edge Kt 2 0.40 MPa | Z | 0.86 | 12.50 | 14.54 | 3 | OK |
| 17 | stall, both jaws (cyclic), jaws 44 open: R 13.5 N at the block's end | rail block root, rack side with the anchor's Ø2.7 pilot in it (round 4): b_eff 7.9, depth 12.35, lever 5.9; I 1194; face Kt 2.5 1.05 / pilot edge Kt 2 0.49 MPa | Z | 1.05 | 12.50 | 11.86 | 4 | OK |
| 18 | crash 13 N pushes jaw B shut: rack B's -y end on the block at y -31.4, R 12.6 N | rail block root, rack side (sharp, Kt 2.5): b_eff 8.5, depth 12.35, lever 5.9 | Z | 0.86 | 12.50 | 14.54 | 3 | OK |
| 19 | added: opening against an obstacle, jaw B: rack B's -y end at y -31.4, R 19.8 N | rail block root, rack side (sharp, Kt 2.5): b_eff 8.5, depth 12.35, lever 5.9 | Z | 1.35 | 12.50 | 9.26 | 3 | OK |
| 20 | added: opening against an obstacle, jaw B, jaws 44 open: rack B's -y end at y -9.4, R 27.0 N | rail block root, rack side (sharp, Kt 2.5): b_eff 13.8, depth 12.35, lever 5.9 | Z | 1.13 | 12.50 | 11.02 | 3 | OK |
| 21 | new path: the same (jaws 44 open, R 27.0 N) where the 14 mm front pilot passes 1.9 under the root (x 20.85..22.35, y 24) | rail block root less the pilot's 1.0 mm overlap with the anchor's Ø2.7 pilot in it (round 4): b_eff 6.9, depth 12.35, lever 5.9; I 1041; face Kt 2.5 2.43 / pilot edge Kt 2 1.14 MPa | Z | 2.43 | 12.50 | 5.15 | 3 | OK |
| 22 | new path: rack B pressed down on the plate over a front pilot (separating 7.9 N + pitch 8.5 N, all on the skin) | skin 1.9 over Ø2.2, b 12 (rack face), simply supported | XY | 1.24 | 25.00 | 20.09 | 3 | OK |
| 23 | USB tug 10 N along x at the plug (+x): rib roots on the pad (z 8.3), rail block ignored | bulkhead + 2 ribs 6 x 10: A 532, I 8804, centroid x 4.90; rib back x -6.5, sharp Kt 2.5 | Z | 2.70 | 12.50 | 4.63 | 3 | OK |
| 24 | USB tug 10 N along x at the plug (+x): rib roots on the pad (z 8.3), as built (the rail block is in the section) | + block 64 x 12.35: A 1326 (probed 1373), I 59432, centroid x 11.62; Kt 2.5 | Z | 0.64 | 12.50 | 19.68 | 3 | OK |
| 25 | USB tug 10 N along x at the plug (+x): pad / bulkhead r 1.5 fillet (z 8.3, x 3.5), rail block ignored | bulkhead + ribs, Kt 1.7 (r/h 0.23) | Z | 0.23 | 12.50 | 55.38 | 3 | OK |
| 26 | USB tug 10 N along x at the plug (+x): washer relief's foot (z 8.3, x 4.5), sharp, rail block ignored | bulkhead + ribs, Kt 2.5 | Z | 0.10 | 12.50 | 131.11 | 3 | OK |
| 27 | USB tug 10 N along x at the plug (-x): rail block's top meets the bulkhead's front face (z 17.75, sharp) | bulkhead + ribs above the block, front face x 10.0, Kt 2.5 | Z | 1.07 | 12.50 | 11.69 | 3 | OK |
| 28 | USB tug 10 N along x at the plug (+x), port at y +-45: rib back above the block (z 17.75), bending + the twist's warping | global 739 N.mm on bulkhead + ribs, + rib flange 184 N.mm (L_c 32), Kt 1 (smooth) | Z | 1.63 | 12.50 | 7.66 | 3 | OK |
| 29 | camera package 86 g x3 along x (cyclic): rib roots, rail block ignored | as above | Z | 0.59 | 12.50 | 21.32 | 4 | OK |
| 30 | new path: USB tug 10 N along x at the plug: the ribs' moment carried to the horn as torsion of plate + bulkhead + block (half each side) | J 9590 mm4, plate 6 thick | Z shear | 0.26 | 6.25 | 23.98 | 3 | OK |
| 31 | USB tug 10 N along x, port at y -45 (twist 450 N.mm): -y strip + its rib | 13.3 x 6.5 + rib 6 x 10 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +15.9 N | Z | 2.73 | 12.50 | 4.57 | 3 | OK |
| 32 | USB tug 10 N along x, port at y -45 (twist 450 N.mm): +y strip + its rib | 24.3 x 6.5 + rib 6 x 10 at the window's lower corner (Ø3 relief, Kt 1.5), screw force -5.9 N | Z | 1.82 | 12.50 | 6.88 | 3 | OK |
| 33 | USB tug 10 N along x, port at y +45 (twist 450 N.mm): -y strip + its rib | 13.3 x 6.5 + rib 6 x 10 at the window's lower corner (Ø3 relief, Kt 1.5), screw force -8.4 N | Z | 1.77 | 12.50 | 7.07 | 3 | OK |
| 34 | USB tug 10 N along x, port at y +45 (twist 450 N.mm): +y strip + its rib | 24.3 x 6.5 + rib 6 x 10 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +18.4 N | Z | 3.23 | 12.50 | 3.87 | 3 | OK |
| 35 | camera x3 along x (cyclic): -y strip + its rib | 13.3 x 6.5 + rib 6 x 10 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +1.0 N | Z | 0.25 | 12.50 | 49.80 | 4 | OK |
| 36 | camera x3 along x (cyclic): +y strip + its rib | 24.3 x 6.5 + rib 6 x 10 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +1.6 N | Z | 0.39 | 12.50 | 32.19 | 4 | OK |
| 37 | one jaw blocked: tab screw pull-out 14 N (M2, 5.5 engaged) | thread shear cylinder | Z shear | 0.40 | 6.25 | 15.64 | 3 | OK |
| 38 | USB tug 10 N along x at the plug: M3 x 18 pull-out from the bulkhead top, 66 N per screw | M3, 11.5 engaged | Z shear | 0.61 | 6.25 | 10.21 | 3 | OK |
| 39 | new path: opening stall on jaw B, jaws open (27.0 N on the cover's upper piece): the cover's overturning moment 886 N.mm on its top screws, 136 N each (M3 x 10, no camera; bound: as if the post held nothing, kept since round 4) | M3, 7.0 engaged | Z shear | 2.07 | 6.25 | 3.03 | 3 | OK |
| 40 | new path: opening stall on jaw B, jaws open (27.0 N on the cover's upper piece): the cover's overturning moment 886 N.mm on its top screws, 136 N each (M3 x 18 with the camera mount; bound: as if the post held nothing, kept since round 4) | M3, 11.5 engaged | Z shear | 1.26 | 6.25 | 4.97 | 3 | OK |
| 41 | stall, one jaw blocked: rack B pushes the cover's lower piece forward (27.0 N at z 12.1): M2.5 pull-out 108 N (one screw) | M2.5 x 16, 11 engaged (14 mm pilot), 1.9 mm skins | Z shear | 1.25 | 6.25 | 4.98 | 3 | OK |
| 42 | cover anchor M3 x 45 driven snug, 150 N preload (sustained): pull-out from the block | thread cylinder Ø3 x 10.75 | Z shear | 1.48 | 6.25 | 4.22 | 4 | OK |
| 43 | cover anchor under the opening stall: preload + the wedge's lift + the cover's lift (35.1 N; foot held by the ridge) | thread cylinder Ø3 x 10.75 | Z shear | 1.83 | 6.25 | 3.42 | 3 | OK |
| 44 | cover anchor, preload crept away: the wedge's lift + the cover's lift 35.1 N under the opening stall | thread cylinder Ø3 x 10.75 | Z shear | 0.35 | 6.25 | 18.04 | 3 | OK |
| 45 | cover anchor, spec §8 proof push 34.2 N: preload + wedge + lift 44.5 N | thread cylinder Ø3 x 10.75 | Z shear | 1.92 | 6.25 | 3.26 | 2 | OK |
| 46 | cover anchor, ridge play as printed (0.082 mm, preload gone): wedge + lift 106.0 N under the opening stall | thread cylinder Ø3 x 10.75 | Z shear | 1.05 | 6.25 | 5.97 | 3 | OK |
| 47 | cover anchor, ridge play as printed (0.082 mm, preload gone): wedge + lift 115.4 N under the spec §8 proof push 34.2 N | thread cylinder Ø3 x 10.75 | Z shear | 1.14 | 6.25 | 5.49 | 2 | OK |
| 48 | cover anchor driven: thread forming (4.6 MPa, as the M2 rows) + preload (0.85 MPa), short-term | 2.65 CAD / 2.75 printed walls to the front face and the +y end; Lame peak x1.22, along the layers | XY | 6.67 | 25.00 | 3.75 | 3 | OK |
| 49 | cover anchor: preload alone (sustained; the forming pressure relaxes) | as above | XY | 1.04 | 25.00 | 24.04 | 4 | OK |
| 50 | V-groove (opening stall, Fx 25.6 N): the cover's ridge on the groove's +x flank (frictionless, all on one flank) | normal 36.2 N on 0.71 x 7.4 (the frame's layer edges) | bearing | 6.92 | 25.00 | 3.61 | 3 | OK |
| 51 | V-groove (opening stall, Fx 25.6 N): the block in front of the groove sheared off along the groove's bottom (z 16.95) | 41 mm2 ((22.35 - 16.05) x 7.4 less the pilot), interlayer | Z shear | 0.94 | 6.25 | 6.66 | 3 | OK |
| 52 | V-groove (spec §8 proof push, Fx 32.5 N): the cover's ridge on the groove's +x flank (frictionless, all on one flank) | normal 46.0 N on 0.71 x 7.4 (the frame's layer edges) | bearing | 8.78 | 25.00 | 2.85 | 2 | OK |
| 53 | V-groove (spec §8 proof push, Fx 32.5 N): the block in front of the groove sheared off along the groove's bottom (z 16.95) | 41 mm2 ((22.35 - 16.05) x 7.4 less the pilot), interlayer | Z shear | 1.19 | 6.25 | 5.24 | 2 | OK |
| 54 | cover push into the block, bound: all of it on the screw (opening stall, whole push 27.0 N): shank bearing in the pilot | Ø3 x 6 | bearing | 1.50 | 25.00 | 16.67 | 3 | OK |
| 55 | cover push into the block, bound: all of it on the screw (opening stall, whole push 27.0 N): tear-out of the 2.65 wall to the block's front face | 2 x 2.65 x 6, vertical planes (along the layers) | XY shear | 0.85 | 12.50 | 14.73 | 3 | OK |
| 56 | cover push into the block (opening stall, whole push 27.0 N): rail block root bent the other way (pull at the top, lever 11.75) | b_eff 14.6 (less the pilot), depth 12.35, Kt 2.5 | Z | 2.14 | 12.50 | 5.83 | 3 | OK |
| 57 | cover push into the block, bound: all of it on the screw (spec §8 proof push, 34.2 N): shank bearing in the pilot | Ø3 x 6 | bearing | 1.90 | 25.00 | 13.16 | 2 | OK |
| 58 | cover push into the block, bound: all of it on the screw (spec §8 proof push, 34.2 N): tear-out of the 2.65 wall to the block's front face | 2 x 2.65 x 6, vertical planes (along the layers) | XY shear | 1.08 | 12.50 | 11.62 | 2 | OK |
| 59 | cover push into the block (spec §8 proof push, 34.2 N): rail block root bent the other way (pull at the top, lever 11.75) | b_eff 14.6 (less the pilot), depth 12.35, Kt 2.5 | Z | 2.72 | 12.50 | 4.60 | 2 | OK |

Information rows (not in the verdict):

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 60 | info: proof test, horn in a vice, one jaw blocked: 1736 N.mm through the pocket | as above | XY | 7.27 | 25.00 | 3.44 | 3 | OK |
| 61 | info: same tug with the port at the centre: -y strip + its rib | 13.3 x 6.5 + rib 6 x 10 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +3.8 N | Z | 1.18 | 12.50 | 10.56 | 3 | OK |
| 62 | info: same tug with the port at the centre: +y strip + its rib | 24.3 x 6.5 + rib 6 x 10 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +6.2 N | Z | 1.85 | 12.50 | 6.77 | 3 | OK |
| 63 | info: cover anchor driven: thread forming (4.6 MPa) + preload (0.85 MPa) in the ligament between the pilot and the V-groove (installation) | 1.10 printed (0.95 CAD) at the block top, Lame peak x1.79, along the layers | XY | 9.81 | 25.00 | 2.55 | 3 | **FAIL** |
| 64 | info: the same, if the ligament splits: M3 x 45 pull-out on the preload with that thread lost (sustained) | thread cylinder Ø3 x 10.55 | Z shear | 1.51 | 6.25 | 4.14 | 4 | OK |

MG90S tab-pilot strips (user decision 26 Oct: strips kept, first-print screw-strip check, spec §8):

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 65 | screw driving, M2 x 8 snug (100 N) + thread forming (0.04 N.m), sustained: lead-end pilot to the lead notch | strip 1.35 CAD / 1.55 printed; hoop stress at the pilot edge (Lame peak), p 6.3 MPa | Z | 7.80 | 12.50 | 1.60 | 4 | **FAIL** |
| 66 | same, mean hoop stress across the strip (p r / w): lead-end pilot to the lead notch | 1.55 printed | Z | 3.05 | 12.50 | 4.10 | 4 | OK |
| 67 | one jaw blocked: tab screw pulled with 14 N, its flank pressure added (short-term): lead-end pilot to the lead notch | Lame peak, p 6.5 MPa | Z | 8.09 | 12.50 | 1.55 | 3 | **FAIL** |
| 68 | screw driving, M2 x 8 snug (100 N) + thread forming (0.04 N.m), sustained: far-end pilot to the window | strip 1.45 CAD / 1.65 printed; hoop stress at the pilot edge (Lame peak), p 6.3 MPa | Z | 7.66 | 12.50 | 1.63 | 4 | **FAIL** |
| 69 | same, mean hoop stress across the strip (p r / w): far-end pilot to the window | 1.65 printed | Z | 2.86 | 12.50 | 4.36 | 4 | OK |
| 70 | one jaw blocked: tab screw pulled with 14 N, its flank pressure added (short-term): far-end pilot to the window | Lame peak, p 6.5 MPa | Z | 7.95 | 12.50 | 1.57 | 3 | **FAIL** |
| 71 | one jaw blocked: the case's end bears on the window's end (21.6 N): far-end pilot to the window | bridge over the pilot, span 1.7, depth 1.65 | Z | 0.14 | 12.50 | 90.72 | 3 | OK |
| 72 | claw stall reaction 216 N.mm: 7.4 N per tab screw along z (the strips lie beside this path) | pilot wall bearing Ø1.5 x 5.5 | XY | 0.90 | 25.00 | 27.79 | 3 | OK |

(drop: this load set has no drop case)


Script: lowest SF 3.03 (required 3): new path: opening stall on jaw B, jaws open (27.0 N on the cover's upper piece): the cover's overturning moment 886 N.mm on its top screws, 136 N each (M3 x 10, no camera; bound: as if the post held nothing, kept since round 4) / M3, 7.0 engaged

## Proof test (spec §8)

- **The frame's proof rows pass:** V-groove 2.85 / 5.24, anchor pull-out 3.26, with play 5.49.
- **On the round-5 build as printed, the cover itself is not safe for step 1's push on jaw B** (cover strength.md,
  1.79 against 2). Run the proof test only after the cover's fix.
- **Suggested addition** to the pass list, exact text in the report: no split or bulge at the anchor pilot's mouth on
  the groove side, checked when the M3 × 45 is first driven.

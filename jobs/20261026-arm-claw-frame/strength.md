VERDICT: NEEDS_TEST

# Strength check: 20261026-arm-claw-frame (round 3)

strength-analyst (independent review of the round-3 geometry) · 2026-10-26 ·
`python3 jobs/20261026-arm-claw-frame/strength_calc.py` (plain python3, run from the project root: reads `claw_frame.py`,
this job's `model.py`, `tools/cadlib.py`, `tools/hobby_parts.py` and the assembly's `torque_budget.json`; no build123d)

Every round-2 failure is fixed as built, and every row passes. The verdict is NEEDS_TEST only because the allowables
are placeholders.

**Lowest SF: 3.03.** It is a new row: the cover's top M3 screws pulling out of the bulkhead top (M3 × 10, no camera
mount) when the claw opens against an obstacle on jaw B. The cover analysis (round 3, FAIL) found that push leaving the
cover through its top joint. The cover's required fix, an anchored second-tie post, removes this row. It adds one M3
pilot to this frame's rail block, which leaves the block's root at 5.93.

**Lowest SF of the frame's own load cases: 3.53.** Floor punching under the Ø8 washer when the camera hits the desk,
exactly as the designer predicted.

The MG90S tab-pilot strips are unchanged and stay a user-accepted deviation, with the first-print check in spec §8.
Their rows are in their own table.

## Round-2 fixes: made?

| Round-2 required change | Round 3 as built | Made? |
|---|---|---|
| 1. Rail wall → GUIDE_T 10, 8 + r 2 fillet, or a block back to the bulkhead | Block x 10–22.35, z 6–17.75, merged into the bulkhead's front face (RAIL_X0 = X_B) | Yes: 6.31 at its end, sharp root (row 15). Opening against an obstacle 9.26 / 11.02 |
| 2. Wrist clamp: Ø8 washer, bulkhead relieved to let it down | Ø8 × 0.8 (DIN 9021 M2.5, bore 2.7); Ø9 relief 1.0 into the bulkhead from the pad's top; floor 6.3 kept | Yes: bearing 3.97, punching **3.53** (rows 3–4). See the fit note on the relief below |
| 3. r 1.5 fillet at the pad / bulkhead back | r 1.5 full width, interrupted by the relief over \|y\| ≤ 4 | Yes. With the ribs it is no longer near the governing fibre: 55 (row 25). The relief's sharp foot gives 131 (row 26) |
| 4. Window strips: 6 × 10 ribs behind the strips' outer edges | Ribs y ±(26…32), x −6.5…3.5, pad to bulkhead top | Yes: 3.87 (row 34) |
| Front M2.5 pull-out (row 28) | M2.5 × 16 in 14 mm pilots, 11 engaged | Yes: 4.98 (row 41) |

## Load cases

| # | Case | Load | Point, direction | Type, SF req |
|---|---|---|---|---|
| 1 | Stall, one jaw blocked | 21.6 N, 3 mm from the tip. Rack-end couple R = 21.6 × 51.75 / span: 19.8 N (closed) to 27.0 N (open) | Rack B back on the rail block at one end | Short-term, 3 |
| 2 | Stall, both jaws, every full-close grip | Half of 1 | As 1 | Cyclic, 4 |
| 3 | Crash (required) | 13 N at a fingertip in the arm plane, finger pushed shut (reversed couple) | Rail block at rack B's −y end; wrist joint | Short-term, 3 |
| 4 | Opening against an obstacle (Architect: stays a design case) | 21.6 N on a finger's outer face, reversed | As 3; and on the cover (new rows 39–40) | Short-term, 3 |
| 5 | USB cable tug (spec) | 10 N, any direction, at the right-angle plug, G (−18.8, y_port, 91.6). y_port anywhere within ±45 | 2 top M3 → bulkhead → wrist joint | Short-term, 3 |
| 6 | Camera hits the desk (SYS-11) | 13 N along claw y at the Brio's end face (z 79.6) | Wrist joint | Short-term, 3 |
| 7 | Weight ×3 incl. the ramp | 3 × the 50 g overhung moment, **133 N·mm** (torque_budget round 3; was 124). Camera package 86 g | Wrist joint, bulkhead | Cyclic, 4 |
| 8 | SYS-04 overhung moment | 133 × 1.3 = 173 N·mm | Clamp preload | Sustained, 4 |
| 9 | Yaw stall at a fingertip | 7.1 N along the wrist axis at x 83.35 | Wrist joint (+ 7.1 N pull) | Short-term, 3 |
| 10 | Claw-servo reaction, handling | 216 N·mm about the shaft; tab screws snug; 5 N handling (covered by 3) | Tab pilots | Short-term 3 / sustained 4 |

The end effector is now 253.9 g solid / 233.6 g sliced (torque_budget.json). The wrist rows read the overhung moments
from that file. There is no drop case in this load set.

## Build direction and critical sections (as built)

The frame prints back face down: its layers are z = const. Wrist-plate bending runs along the layers. The bulkhead, the
ribs and the rail block bend about horizontal roots, with their stress along z, across the layers. Pull-out and punching
are interlayer shear.

- **Rail block** (x 10–22.35 × z 6–17.75, full width).
  - Checked as a cantilever off the wrist plate, 12.35 deep, with a sharp rack-side root (Kt 2.5) and a 45° spread from
    a 2 mm patch at the cocked rack's end.
  - Its merge with the bulkhead's front face is ignored, which is conservative.
  - The 14 mm front M2.5 pilots now run 1.5 mm under the root at y ±24 (x 20.85–22.35, top z 4.1). At the block's +y
    end the root's spread reaches the pilot's edge, so 1.0 mm comes off b_eff (row 21: 5.53).
- **Bulkhead root** (probed sections).
  - At z 8.3–17.7 the plate-top section includes the rail block (A ≈ 1320–1373 mm²). Above z 17.75 it is bulkhead +
    ribs (A 532).
  - With the block counted, the rib roots at z 8.3 give 19.7 (row 24). With it ignored, as the designer did, 4.63
    (row 23).
  - The re-entrant corner moves to the block's top at the bulkhead's front face (z 17.75, sharp): 11.69 for a tug
    along −x (row 27).
  - Above the block the ribs run on smooth. A port off-centre twists the bulkhead; the ribs take it as opposed bending
    (open-section warping, L_c 32 mm): 7.66 (row 28).
  - The ribs' moment reaches the horn by torsion of plate + bulkhead + block: 24 (row 30).
- **Window strips:** each strip plus its 6 × 10 rib at the window's lower corner (Ø3 relief, Kt 1.5).
- **Wrist clamp.** The washer (Ø8, bore 2.7: 44.5 mm²) bears on the pad. The 6.3 floor punches on π × 8 × 6.3. The Ø9
  relief starts on the pad's top face, so the seat and the floor are whole.
- **Tab-pilot strips:** from the CAD (1.35 / 1.45; printed 1.55 / 1.65), unchanged.

## Assumptions

- The camera loads reach the frame through the 2 top M3 screws, and the bulkhead + ribs take their moment. The cover's
  portal is ignored.
- Rack ends land within 2 mm of their ends (they cock in 0.25 gaps).
- New rows 39–40 bound the cover's top joint under its reversed rack-B push: all of the overturning moment
  R × (50 − 17.2) = 886 N·mm as M3 tension against the bulkhead's rear edge (lever 3.25). The cover's global model
  gives 1.46–1.23 for its own top wall in the same event (cover report).
- The pad / bulkhead fillet r 1.5 at h 6.5: Kt 1.7. The relief's foot, the rib roots and the block-top corner are sharp
  (2.5).
- **Fit, not strength.** The relief's printed radius is 4.40. The washer is radius 4.0 plus 0.35 radial play on the M2
  in its 2.7 bore, so the margin is 0.05 mm. A washer pushed hard against the bulkhead side can ride on the relief's
  edge. Seat it centred (BUILD_GUIDE §4) and check it lies flat before tightening.
- Service temperature is 40 °C against PETG softening at about 70 °C: OK while stalls stay short (the sketch eases off
  after closing squeezes, not after an opening stall: SYS-11).

## Allowables and sources

`library/materials.csv` has no measured row and there is no datasheet in `inputs/`. These are the strength-checks
**placeholder** PETG values, so NEEDS_TEST is the best possible verdict.

| Quantity | Value | Source |
|---|---|---|
| Along the layers | 25 MPa | Skill placeholder, PETG |
| Across the layers | 12.5 MPa | 0.5 × in-plane |
| Interlayer shear | 6.25 MPa | 0.5 × 12.5 |
| Bearing | 25 MPa | In-plane value |
| Kt | 2.5 sharp; 1.5 for r ≥ 0.25 h; 1.7 for r/h 0.15–0.25 | Skill; the 1.7 is a Peterson-based interpolation |

## Results (copied from `python3 strength_calc.py`)

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | USB tug 10 N at the plug (z 91.6), across the shaft: washer bearing (M_t 896 N.mm -> screw 249 N) | Ø8 x 0.8 washer on the pad, 44.5 mm2 (its Ø2.7 bore) | Z comp | 5.59 | 25.00 | 4.47 | 3 | OK |
| 2 | USB tug 10 N at the plug (z 91.6), across the shaft: floor punching under the washer | Ø8 x 6.3 floor | Z shear | 1.57 | 6.25 | 3.98 | 3 | OK |
| 3 | added: camera hits the desk, 13 N at its end (z 79.6): washer bearing (M_t 1009 N.mm -> screw 280 N) | Ø8 x 0.8 washer on the pad, 44.5 mm2 (its Ø2.7 bore) | Z comp | 6.29 | 25.00 | 3.97 | 3 | OK |
| 4 | added: camera hits the desk, 13 N at its end (z 79.6): floor punching under the washer | Ø8 x 6.3 floor | Z shear | 1.77 | 6.25 | 3.53 | 3 | OK |
| 5 | crash: 13 N in the arm plane at the fingertip (z <= 33.2): washer bearing (M_t 406 N.mm -> screw 113 N) | Ø8 x 0.8 washer on the pad, 44.5 mm2 (its Ø2.7 bore) | Z comp | 2.53 | 25.00 | 9.87 | 3 | OK |
| 6 | crash: 13 N in the arm plane at the fingertip (z <= 33.2): floor punching under the washer | Ø8 x 6.3 floor | Z shear | 0.71 | 6.25 | 8.77 | 3 | OK |
| 7 | weight x3 incl. the 250 deg/s2 ramp (cyclic): 3 x the 50 g overhung moment (133 N.mm, torque_budget round 3): washer bearing (M_t 399 N.mm -> screw 111 N) | Ø8 x 0.8 washer on the pad, 44.5 mm2 (its Ø2.7 bore) | Z comp | 2.49 | 25.00 | 10.05 | 4 | OK |
| 8 | weight x3 incl. the 250 deg/s2 ramp (cyclic): 3 x the 50 g overhung moment (133 N.mm, torque_budget round 3): floor punching under the washer | Ø8 x 6.3 floor | Z shear | 0.70 | 6.25 | 8.93 | 4 | OK |
| 9 | SYS-04 overhung moment, 50 g, x1.3 moving (sustained): washer bearing (M_t 173 N.mm -> screw 100 N) | Ø8 x 0.8 washer on the pad, 44.5 mm2 (its Ø2.7 bore) | Z comp | 2.25 | 25.00 | 11.13 | 4 | OK |
| 10 | SYS-04 overhung moment, 50 g, x1.3 moving (sustained): floor punching under the washer | Ø8 x 6.3 floor | Z shear | 0.63 | 6.25 | 9.90 | 4 | OK |
| 11 | added: yaw stall 7.1 N along the wrist axis at the fingertip (x 83.3), pulling the claw off the horn: washer bearing (M_t 592 N.mm -> screw 171 N) | Ø8 x 0.8 washer on the pad, 44.5 mm2 (its Ø2.7 bore) | Z comp | 3.85 | 25.00 | 6.49 | 3 | OK |
| 12 | added: yaw stall 7.1 N along the wrist axis at the fingertip (x 83.3), pulling the claw off the horn: floor punching under the washer | Ø8 x 6.3 floor | Z shear | 1.08 | 6.25 | 5.77 | 3 | OK |
| 13 | wrist stall 216 N.mm (cyclic): horn arm on the pocket wall | arm flank r 3.6..16.1 x 1.6 (mean, resultant at r 11.9) | XY | 0.91 | 25.00 | 27.62 | 4 | OK |
| 14 | crash: 13 N at the fingertip x 83.3 back-drives the wrist (1084 N.mm, 5 x stall: the top of SYS-11's 3-5 x): horn arm on the pocket wall | arm flank r 3.6..16.1 x 1.6 (mean, resultant at r 11.9) | XY | 4.54 | 25.00 | 5.51 | 3 | OK |
| 15 | stall, one jaw blocked, jaws 44 open: rack B's +y end at the block's end, R 27.0 N | rail block root, rack side (sharp, Kt 2.5): b_eff 7.9, depth 12.35, lever 5.9 | Z | 1.98 | 12.50 | 6.31 | 3 | OK |
| 16 | stall, one jaw blocked, jaws closed: rack B's +y end at y 25.1, R 19.8 N | rail block root, rack side (sharp, Kt 2.5): b_eff 13.8, depth 12.35, lever 5.9 | Z | 0.83 | 12.50 | 15.05 | 3 | OK |
| 17 | stall, both jaws (cyclic), jaws 44 open: R 13.5 N at the block's end | rail block root, rack side (sharp, Kt 2.5): b_eff 7.9, depth 12.35, lever 5.9 | Z | 0.99 | 12.50 | 12.62 | 4 | OK |
| 18 | crash 13 N pushes jaw B shut: rack B's -y end on the block at y -31.4, R 12.6 N | rail block root, rack side (sharp, Kt 2.5): b_eff 8.5, depth 12.35, lever 5.9 | Z | 0.86 | 12.50 | 14.54 | 3 | OK |
| 19 | added: opening against an obstacle, jaw B: rack B's -y end at y -31.4, R 19.8 N | rail block root, rack side (sharp, Kt 2.5): b_eff 8.5, depth 12.35, lever 5.9 | Z | 1.35 | 12.50 | 9.26 | 3 | OK |
| 20 | added: opening against an obstacle, jaw B, jaws 44 open: rack B's -y end at y -9.4, R 27.0 N | rail block root, rack side (sharp, Kt 2.5): b_eff 13.8, depth 12.35, lever 5.9 | Z | 1.13 | 12.50 | 11.02 | 3 | OK |
| 21 | new path: the same (jaws 44 open, R 27.0 N) where the 14 mm front pilot passes 1.9 under the root (x 20.85..22.35, y 24) | rail block root less the pilot's 1.0 mm overlap (sharp, Kt 2.5): b_eff 6.9, depth 12.35, lever 5.9 | Z | 2.26 | 12.50 | 5.53 | 3 | OK |
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
| 39 | new path: opening stall on jaw B, jaws open (27.0 N on the cover's upper piece): the cover's overturning moment 886 N.mm on its top screws, 136 N each (M3 x 10, no camera; the cover's anchored-post fix removes it) | M3, 7.0 engaged | Z shear | 2.07 | 6.25 | 3.03 | 3 | OK |
| 40 | new path: opening stall on jaw B, jaws open (27.0 N on the cover's upper piece): the cover's overturning moment 886 N.mm on its top screws, 136 N each (M3 x 18 with the camera mount; the cover's anchored-post fix removes it) | M3, 11.5 engaged | Z shear | 1.26 | 6.25 | 4.97 | 3 | OK |
| 41 | stall, one jaw blocked: rack B pushes the cover's lower piece forward (27.0 N at z 12.1): M2.5 pull-out 108 N (one screw) | M2.5 x 16, 11 engaged (14 mm pilot), 1.9 mm skins | Z shear | 1.25 | 6.25 | 4.98 | 3 | OK |

**Lowest SF: 3.03 (required 3), row 39.** That is the cover's top screws (M3 × 10, 7 engaged) under the cover's
reversed rack-B push; 4.97 with the camera mount's M3 × 18. The cover's required fix removes the row.

Of the frame's own cases, the lowest is **3.53**: floor punching under the Ø8 washer, camera hits the desk (row 4).

Information rows (not in the verdict):

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 42 | info: proof test, horn in a vice, one jaw blocked: 1736 N.mm through the pocket | as above | XY | 7.27 | 25.00 | 3.44 | 3 | OK |
| 43 | info: same tug with the port at the centre: -y strip + its rib | 13.3 x 6.5 + rib 6 x 10 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +3.8 N | Z | 1.18 | 12.50 | 10.56 | 3 | OK |
| 44 | info: same tug with the port at the centre: +y strip + its rib | 24.3 x 6.5 + rib 6 x 10 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +6.2 N | Z | 1.85 | 12.50 | 6.77 | 3 | OK |

### MG90S tab-pilot strips (user decision, 26 Oct: strips kept, first-print check in spec §8)

These are unchanged from round 2 and are not in the verdict: the user accepted the deviation. At the pilot's edge (Lamé
peak) the hand calculation can't show the sustained SF of 4. On the mean hoop stress it can (4.10 / 4.36). The
first-print screw-strip check is the acceptance.

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 45 | screw driving, M2 x 8 snug (100 N) + thread forming (0.04 N.m), sustained: lead-end pilot to the lead notch | strip 1.35 CAD / 1.55 printed; hoop stress at the pilot edge (Lame peak), p 6.3 MPa | Z | 7.80 | 12.50 | 1.60 | 4 | **FAIL** |
| 46 | same, mean hoop stress across the strip (p r / w): lead-end pilot to the lead notch | 1.55 printed | Z | 3.05 | 12.50 | 4.10 | 4 | OK |
| 47 | one jaw blocked: tab screw pulled with 14 N, its flank pressure added (short-term): lead-end pilot to the lead notch | Lame peak, p 6.5 MPa | Z | 8.09 | 12.50 | 1.55 | 3 | **FAIL** |
| 48 | screw driving, M2 x 8 snug (100 N) + thread forming (0.04 N.m), sustained: far-end pilot to the window | strip 1.45 CAD / 1.65 printed; hoop stress at the pilot edge (Lame peak), p 6.3 MPa | Z | 7.66 | 12.50 | 1.63 | 4 | **FAIL** |
| 49 | same, mean hoop stress across the strip (p r / w): far-end pilot to the window | 1.65 printed | Z | 2.86 | 12.50 | 4.36 | 4 | OK |
| 50 | one jaw blocked: tab screw pulled with 14 N, its flank pressure added (short-term): far-end pilot to the window | Lame peak, p 6.5 MPa | Z | 7.95 | 12.50 | 1.57 | 3 | **FAIL** |
| 51 | one jaw blocked: the case's end bears on the window's end (21.6 N): far-end pilot to the window | bridge over the pilot, span 1.7, depth 1.65 | Z | 0.14 | 12.50 | 90.72 | 3 | OK |
| 52 | claw stall reaction 216 N.mm: 7.4 N per tab screw along z (the strips lie beside this path) | pilot wall bearing Ø1.5 x 5.5 | XY | 0.90 | 25.00 | 27.79 | 3 | OK |

Drive the tab screws with dry threads and stop at the first firm resistance (≈ 0.06 N·m), as in round 2.

## What-if lines (in the script)

| Item | Result |
|---|---|
| Wrist clamp, camera desk hit | Ø6 2.01 · **Ø8 3.53 (as built)** · Ø8 on a 7.0 floor 3.92 · Ø10 on 7.0 4.91 |
| Rail block depth, one jaw blocked, jaws open | 4 → 0.66 · 8 → 2.65 · **12.35 → 6.31 (as built)** |
| The cover fix's M3 pilot (Ø2.7 at x 18.35, y 28) in the rail block | Block root 5.93 |
| Window strips | no ribs 1.32 · 6 × 8 3.04 · **6 × 10 3.87 (as built)** · 8 × 10 4.89 |

## Required changes

None for the frame's own load cases.

The cover's required fix adds one feature here: a **Ø2.7 CAD × 14** M3 pilot in the rail block's top at
**(x 18.35, y 28)**, for the anchor M3 × 45 through the cover's second-tie post. It is 2.65 mm from the block's front
face and from its +y end, and clear of the 14 mm front M2.5 pilot (x ≥ 20.85, y 22.9–25.1). With it:
- the block's rack-side root gives 5.93;
- rows 39–40 fall away;
- the frame's lowest becomes 3.53.

## Proof test (spec §8)

It still matches. The loads are 1.5 × the design loads:
- 32 N one-jaw pull and opening push;
- 15 N on the USB plug;
- 20 N on the Brio's end;
- 7.5 N at the fingertips.

They load every governing item here: the washer and floor (camera end push 20 N: 1.5 × the 13 N), the rail block, the
ribs and the window strips (USB plug 15 N along x).

Update the pass criteria's wording to the round-3 geometry:
- "the rail wall's root (along it and at its ends)" → **"the rail block's rack-side root (along it and at its +y
  end)"**;
- add **"the rib roots on the pad and the washer relief's foot"**;
- add **"the washer lies flat on the pad, not on the relief's edge"**.

Run the 32 N opening push (step 1) only after the cover's fix: on the as-built cover it would crack the cover's top wall
(cover report). Keep the screw-strip check that §8 already has.

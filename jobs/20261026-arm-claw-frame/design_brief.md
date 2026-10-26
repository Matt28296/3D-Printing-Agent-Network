# Design brief: Claw frame (wrist plate + servo bulkhead)

Job: 20261026-arm-claw-frame · design-lead · 2026-10-26, claw round 3: every required fix of the claw DFM and strength round 2 (this job's design_review.md and strength.md); earlier rounds: deep reviews 01 B1/B2/S1, 03 SYS-01/SYS-08, claw round 1.

## Material
PETG, as for the rest of the arm: tough, low creep under the servo's holding load, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables: 25 MPa along the layers, 12.5 MPa across them, 6.25 MPa interlayer shear.

## Orientation
Flat, back face (wrist horn pocket) on the bed, 0.4 mm bed chamfer. The layers are z = const planes in claw frame G.
- **Bridges and overhangs:**
  - The pocket ceiling bridges 7.9 mm, anchored all round.
  - The servo window has a 7 mm 45° roof; its 9.2 mm flat is anchored on both shoulders.
  - The tab pilots are teardrops pointing up, and the window's lower corners have Ø3 teardrop reliefs.
  - The lead notch has a 45° top (round 3, DFM fix 1), as the turntable's `_notch_tops()`. It runs from the notch end (y 7.5, z 29.45) up to the window wall (y 6.1, z 30.85), so the notch has no flat ceiling.
  - The front M2.5 pilots are flat-topped teardrops, with 1.9 mm of skin under rack B's track.
  - The rail block, the ribs, the Ø9 washer relief and the cover's anchor pilot (round 4) are all vertical-walled.
- **Layer check** of part.stl (0.2 mm layers on a 0.04 mm raster, each compared with the layer below grown 0.3 mm): the only unsupported patches are the pocket ceiling (z 2.1), the front pilots' flats (z 4.1, 0.91 mm between 45° flanks), the 0.17 mm flats where the pilot slots pass their teardrops (z 28.1), and the window roof's two-sided flat (z 40.7). There is nothing at the lead notch any more: round 2 had a 1.4 mm one-sided ledge at z 29.45.

### Load paths and the layers (DFM fix 2: the rail is named here)
| Path | Load (spec §4) | Section | Along or across the layers |
|---|---|---|---|
| Wrist-plate bending | claw weight, side pushes, yaw stall | 6 mm plate | along |
| **Rail block behind rack B** | rack B's back thrust (one jaw blocked: 27 N at one rack end, jaws open; the couple of the grip) | cantilever off the wrist plate, 12.35 deep (x 10…22.35, merged into the bulkhead's front face) × 11.75 tall (z 6…17.75); thrust at mid-height | **across**: the root bends with its stress along z |
| — its rack-side root (x 22.35, z 6) | as above | sharp (Kt 2.5): rack B's square edge runs 0.25 from it | across |
| — its free end (y +32) | at wide openings rack B's back end bears there (it reaches y 47 at 44 mm open) | 45° spread from the end only (b_eff 7.9) | across |
| Bulkhead root above the pad (z 8.3) | camera package weight ×3, USB tug along x, via the 2 top M3 screws | 64 × 6.5 bulkhead + two 6 × 10 ribs | across |
| Window-side strips (window's lower corners) | USB tug with the port off-centre: the twist reaches one top screw | strip + rib behind its outer edge | across |
| Wrist clamp | camera desk hit / USB tug across the wrist shaft: the M2 clamp screw | Ø8 washer on the pad; 6.3 mm floor in punching | bearing / interlayer shear |
| Horn pocket | wrist stall, crash back-drive | pocket wall bearing | along |
| MG90S tab pilots | screw driving, one jaw blocked | 1.34 / 1.45 mm strips (user decision, spec §8 screw-strip check) | across |

The rail is a block, not round 2's 4 mm wall (strength fix 1). Its front root is sharp, its bending stress runs across the layers, and the worst case is rack B's end at the rail's free end with the jaws open. The strength numbers are below.

## Concept
- **Wrist plate:** full width, 6 mm, on the wrist MG90S's single-arm horn. A 2.3 mm raised pad sits behind the bulkhead, so the clamp floor is 6.3 mm. The plate now reaches x 34.85, under the cover's front plate (FACE_W 12).
- **Bulkhead:** 6.5 mm, holding the claw MG90S. The servo goes in from the front, case bottom first, with its lead through the notch at the shaft end; that end's tab pilot is moved 1.3 mm out (`lead="notch_shift_pilot"`).
- **Rail block** behind rack B, x 10…22.35, z 6…17.75: it fills the space between the bulkhead and rack B, below the claw servo's case (z ≥ 21.15). Rack B rides on the plate's top face.
- **r 1.5 fillet** where the pad meets the bulkhead's back face, full width (round 3, strength fix 3).
- **Two ribs** 6 × 10 mm behind the bulkhead's outer edges: y −32…−26 and 26…32, x −6.5…3.5, from the pad (z 8.3) to the bulkhead top (z 48.5) (round 3, strength fix 4). They clear the claw servo (y −16.9…5.9), the top screws (y −23, 14) and the clamp.
- **Ø8 clamp washer:** a Ø9 vertical relief round the clamp axis cuts 1.0 mm into the bulkhead's back face (|y| ≤ 2.9), from the pad's top to the bulkhead top, so the washer goes down past the bulkhead and lies flat on the pad (round 3, strength fix 2). The relief starts on the pad's top face, so the washer seat and the 6.3 mm floor stay whole; it interrupts the r 1.5 fillet over |y| ≤ 4.0.
- **Cover screws:** the cover screws on from above (2 × M3) and from the front (2 × M2.5 × 16 into 14 mm pilots; was × 12 into 10 mm).
- **MG90S tab-pilot strips:** unchanged. The user decided on 26 Oct 2026 to keep them, and spec §8's screw-strip check covers them.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Claw-servo axis | y 0, z 27.25 | ±0.2 | sets the gear mesh | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Bulkhead front face (tab seat) | x 10.0 | ±0.2 | sets the pinion's back face (x 22.6 = 10 + MG90S link_back_z 12.6) | — | claw_frame.py |
| Wrist plate top (rack B's guide) | z 6.0 | ±0.15 | rack back rides on it | — | claw_frame.py (RACK_SEAT 0) |
| Rail block front face | x 22.35 | ±0.15 | 0.25 sliding gap behind rack B | — | claw_frame.py RAIL_X1 |
| **Rail block back face** | **x 10.0 (on the bulkhead)** | — | was a 4 mm wall at x 18.35 | — | claw_frame.py RAIL_X0 = X_B (strength fix 1) |
| **Wrist plate front edge** | **x 34.85** | ±0.15 | the cover's front plate slides down it | — | claw_frame.py X_F0 (FACE_W 10 → 12) |
| MG90S window | 23.2 × 12.8 CAD, 23.0 × 12.6 printed | +0.3/−0 | 0.4 side / 0.2 end clearance on the 22.8 × 12.2 MG90S | HOLE_COMP +0.2 | deep review 01 S1 |
| Lead notch | 4.4 × 1.6 CAD beyond the case end, **45° top** | +0.2 | 3.6 × 1.2 ribbon + bend | HOLE_COMP | deep review 01 B1; DFM round 2 fix 1 |
| Wrist clamp floor | 6.3 | ±0.2 | M2 × 12 + **Ø8 × 0.8 washer**: 12 − 0.8 − 6.3 − 0.6 = 4.3 mm into the spline | — | deep review 01 S2; strength round 2 fix 2 |
| **Washer relief** | Ø9.0 CAD (Ø8 washer + 0.4 a side + HOLE_COMP), 1.0 into the bulkhead | +0.3 | the washer passes the bulkhead | HOLE_COMP | strength round 2 fix 2 |
| **Front M2.5 pilots** | Ø2.2 CAD, **14 deep** | +0.2 | M2.5 × 16 through the 5 mm front plate: 11 engaged | HOLE_COMP | cover strength round 2 (row 22) |
| **Cover anchor M3 pilot (round 4)** | Ø2.7 CAD (Ø2.5 printed), **14 deep**, vertical, in the rail block's top at **(x 18.35, y 28)**, z 3.75…17.75 | +0.2 | M3 × 45 socket head through the cover's second-tie post: 11.25 engaged | HOLE_COMP | cover strength round 3 required change; frame strength round 3 |

Printed targets:
- MG90S window +0.4 side / +0.2 end; wrist horn pocket +0.5.
- Pilots: M2 clamp hole Ø2.4, M3 self-tap Ø2.5, M2.5 self-tap Ø2.0, MG90S tab pilots Ø1.5 (slots 0.4 longer outwards).
- Every hole gets HOLE_COMP = +0.2 mm in CAD.
- measure_holes (geometry.json): Ø2.6 clamp, 2 × Ø2.7 top pilots, Ø2.7 anchor pilot (round 4), 2 × Ø2.2 front pilots. The tab pilots are slots, and the washer relief is a partial arc.

`cad_checks.py` proves on the solid:
- overall size and holes;
- plate top, plate front edge, the rail block's extent;
- bulkhead, clamp floor and washer seat, the relief, the fillet, the ribs;
- the window, the notch's 45° top, the tab pilots, the roof;
- the anchor pilot (round 4): Ø2.7 at (18.35, 28), 14 deep, the block's 2.65 walls round it, and its clearance to the front M2.5 pilot.

## Strength, predicted
The strength-analyst's `strength_calc.py` what-if lines, re-run on the round-3 parameters (FACE_W 12 changes the rack-end thrust slightly). The rib-and-relief section is a hand calculation by the analyst's method: one section at z 8.3, Kt per corner.

| Required change (strength.md) | Round 2 | Round 3 |
|---|---|---|
| 1. Rail root, one jaw blocked, jaws open | 0.65 | **6.31** (block, sharp root); opening against an obstacle 9.26; both jaws, cyclic, ≥ 12 |
| 2. Wrist clamp, camera desk hit | bearing 2.12, punching 2.65 | **Ø8 washer: 4.08 / 3.53**; USB tug 4.59 / 3.98 |
| 3. Bulkhead root, USB tug along +x | 2.70 (sharp) | r 1.5 fillet alone 3.98 (3.86 with the relief); **with the ribs:** rib root (sharp, Kt 2.5) **4.63**, fillet 55, relief corner 129 (A 532 mm², I 8800 mm⁴, centroid x 4.91) |
| 4. Window strips, USB tug with the port at ±45 | 1.32 | **3.87** (6 × 10 ribs) |
| Front M2.5 pull-out (row 28) | 3.41 | **5.4** (11 engaged) |

The frame's lowest predicted SF is **3.53**: floor punching under the Ø8 washer when the camera hits the desk (13 N at its end). The tab-pilot rows are unchanged: user decision, spec §8 screw-strip check.

## Parameters exposed by model.py
- model.py: HOLE_COMP, CLR, END_CLR, TOP_PILOT_DEPTH, FRONT_PILOT_DEPTH, BED_CHAMFER, RELIEF_D, BACK_FILLET, WASHER_RELIEF_D, RIB_W, RIB_D, SERVO_LOC.
- shared, in claw_frame.py: ANCHOR_XY, ANCHOR_PILOT_DEPTH (round 4), T_W, PAD_T, ZS, X_B, BULK_T, X_REAR, HALF_Y, RAIL_IN, RAIL_X0, RAIL_X1, X_F0, WINDOW_ROOF, TOP_SCREWS, FRONT_SCREWS, M3_PILOT, M25_PILOT, WRIST_WASHER_OD, WRIST_WASHER_T.

## Risks
- **The wrist clamp screw sits under the claw servo:** BUILD_GUIDE §4 fits it first.
- **The claw servo goes in from the front with its lead root crossing the bulkhead:** notch at the shaft end, moved pilot, slit filed to 2.1 mm (BUILD_GUIDE §4 step 8).
- **The 1.34 / 1.45 mm pilot strips:** kept by the user's decision (26 Oct 2026); spec §8's screw-strip check on the first print.
- **The frame is heavier:** 46.5 cm³ against 34.8. The rail block and the ribs add 11.6 cm³, about 15 g at the end of the arm; `torque_budget.py` and the BUILD_GUIDE payload table use it.
- **The washer must go down past the bulkhead:** the Ø9 relief runs to the bulkhead top. Fit the clamp before the claw servo, as before.
- **Spec §3 values that changed:**
  - wrist washer Ø6 × 0.5 → Ø8 × 0.8 (4.3 mm into the spline);
  - wrist plate front edge x 32.85 → 34.85;
  - rail: a block from x 10 instead of the x 18.35…22.35 wall;
  - front pilots 10 → 14 deep with M2.5 × 16;
  - the envelope is 42.85 × 64 × 48.5.

## Round 4 (2026-10-26: the cover's claw strength round 3 required change). User-approved
- **Why.** The cover failed at SF 1.23: the reversed rack-B push (opening stall on jaw B, 27 N, or the 13 N crash) could leave the cover only through its 3 mm top wall behind the lip. The fix anchors the cover's second-tie post on this frame's rail block with one vertical M3 × 45, which takes about 25 of the 27 N straight into the block.
- **Change: one M3 pilot in the rail block's top**, Ø2.7 CAD (`M3_PILOT` 2.5 + HOLE_COMP), **14 deep** (z 17.75 → 3.75, `ANCHOR_PILOT_DEPTH`), at **`ANCHOR_XY` (18.35, 28)** in `claw_frame.py`, shared with the cover. The frame prints wrist plate down, so the pilot is vertical in print: a plain round hole, no teardrop.
- **What it leaves.** 2.65 mm of block to its front face (x 22.35) and to its +y end (y 32); 3.75 mm floor under it; clear of the +y front M2.5 pilot (x ≥ 20.85, y 22.9–25.1). The analyst's figure for the block's rack-side root with the hole is **SF 5.93** (as built 6.31), and the frame's top-screw rows 39–40 fall away, so the frame's lowest stays 3.53.
- **Fit.** The cover's post foot and its top wall's underside are 30.75 apart, the same as the block top (z 17.75) and the bulkhead top (z 48.5) here: zero nominal gap. BUILD_GUIDE §4 step 9 has the dry-fit check (0.1 mm feeler) before the M3 is driven.
- **Checks.** `cad_checks.py` (19 checks, exit 0) adds the anchor pilot (`measure_holes`: Ø2.7, vertical, at (18.35, 28)), its depth and floor, the block's walls round it, and its clearance to the front pilot. mesh_check: overhang 1.4 %, bed contact 2534.7 mm², widest bridge 7.9 mm, thin walls 0, as before.
- **Mass.** −0.08 cm³: 46.4 cm³.

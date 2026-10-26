VERDICT: FAIL

# DFM review: 20261026-arm-claw-frame (round 2)

Reviewer: dfm-reviewer (independent) · 2026-10-26 · DESIGN gate, round 2 (round 1: FAIL).
Inputs: spec.md (including the 459ee45 screw-strip check), design_brief.md, model.py, geometry.json, mesh_check.json, print_requirements.json, renders/*.png (regenerated; all 5 viewed), round-1 design_review.md and strength.md, ../20261025-robot-arm-assembly/claw_frame.py, claw_sequence_check.py/.json, assembly_plan.md, BUILD_GUIDE §4, deep reviews 01 (B1, B2) and 03 (SYS-01, SYS-08), tools/hobby_parts.py (`servo_mount_cutter`, `MG90S`), tools/cadlib.py, library/ (no lessons, no material rows, so skill defaults apply).

The outputs are current. `build()` rebuilt in memory gives 34 759.99 mm³ and 14 333.26 mm², the same as geometry.json, and mesh_check re-run in memory reproduces mesh_check.json. Extra evidence:
- a layer-by-layer slice of part.stl: 0.2 mm layers on a 0.04 mm raster, each layer compared with the one below, flagging anything more than 0.3 mm from it;
- a per-layer 0.9 mm thin-feature test;
- ray probes.

The frame prints in G: back face on the bed, z up.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits the bed with a 5 mm margin | PASS | 40.85 × 64.0 × 48.5 mm, `fits_bed: true` |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, `min_z_mm: 0.0` |
| 3 | Orientation matches the brief | PASS | Back face on the bed with the horn pocket in it (bottom.png). The bulkhead, the window with its 45° roof and the rail wall rise from the plate (iso.png, front.png, right.png) |
| 4 | Load paths vs layers | **FAIL** | **The rail wall is new this round:** a 4 mm wall at x 18.35–22.35, z 6–17.75, standing upright in print (front.png). Rack B's back thrust (spec §4: ≈28 N at one rack end, along x) bends it as a cantilever off the plate, so its root stress runs along z, across the layers. Spec §4 says "in their planes" and the brief says "bending along its 64 mm length (≈0.9 MPa)". That figure is 168 N·mm over the whole 64 mm wall (Z = 64 × 4²/6). But a rack end loads only a strip about twice its ≈6 mm lever wide. And when the claw is wide open, rack B's back end (it reaches y 47 at 44 mm open) bears on the rail's free end at y 32. Reviewer's estimate: ≈5 MPa nominal mid-rail and ≈10 MPa at the end, before Kt 2.5 at the sharp front root (item 10). The across-layer placeholder is 12.5 MPa, and SF 3 needs ≤ 4.2. The brief neither names this across-layer path nor justifies it, and round-1 strength checked only bearing, on the old solid rail (row 14). Other paths are fine: plate bending runs along the layers, and the bulkhead root is named in the brief as across the layers and covered by strength |
| 5 | Bed contact | PASS | 2408.3 mm², PETG |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | **FAIL** | **The lead notch has a flat top.** The notch is at the window's +y end (y 6.1–7.5, z 25.05–29.45). Its top at z 29.45 opens into the window, so it is a 1.4 mm ledge anchored on its +y side only. The layer check at z 29.5 finds 7.6 mm² up to 1.16 mm beyond the 0.3 mm support allowance. mesh_check lists it as a 1.41 mm "bridge", but its −y side is the open window. It is neither supported nor justified in the brief. Deep review 01 B1 gives a notch in a standing wall "a 45° top", and the turntable's notches have exactly that (its model.py `_notch_tops()`, its round-4 review item 6). **Everything else passes:** window-roof flat 9.2 mm, anchored on both shoulders (layer check at z 40.7: at most 4.48 from support, so two-sided); horn-pocket ceiling 7.9 mm, anchored all round (z 2.1); front-pilot flats 0.91 mm between 45° flanks (z 4.1); pilot teardrops and the Ø3 corner reliefs point up (right.png). Where each pilot's 0.4 mm outward slot passes its teardrop, a 0.17 mm flat is left: negligible. overhang_pct 1.49 |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (user-accepted deviation) | **MG90S tab-pilot strips,** measured on part.stl at the pilots' centre line (z 27.25) through the whole bulkhead (x 3.6, 6.75 and 9.9, the same at all three). **Lead end:** notch end wall y 7.51 → moved pilot slot y 8.85 = **1.34 mm CAD** (≈1.54 printed). **Far end:** pilot slot y −18.55 → window end y −17.1 = **1.45 mm CAD** (≈1.65 printed). Both are under rule §2's 1.8 mm. The user kept them on 26 Oct 2026, and spec §8 (459ee45) now has the screw-strip check: drive both M2 × 8 snug, no whitening, no crack. So they are a user-accepted deviation covered by that check, not a fail. What still holds: no strip is under 0.9 mm; neither pilot breaks into the window or the notch; the pilots are the right size (Ø1.7 CAD = MG90S `screw_pilot_d` 1.5 + HOLE_COMP, slotted 0.4 mm outward). **Other walls:** bulkhead 6.5 mm, with 1.9 mm each side of the Ø2.7 top pilots; front pilots 1.9 mm of skin above (flat at z 4.1, rack B's track at z 6) and 1.9 below; rail 4.0; the top pilots stay 4.55 and 6.55 mm from the window and roof. `thin_wall_warnings` is empty, and the per-layer 0.9 mm test finds no thin region |
| 8 | HOLE_COMP; horizontal holes teardrop or flat-top | PASS | `HOLE_COMP = HOLE_COMP_DEFAULT` goes into the window (23.2 × 12.8 CAD, 23.0 × 12.6 printed), the notch (4.4 × 1.6 CAD), the tab pilots (Ø1.7), the pocket (hub Ø7.9), the clamp hole (Ø2.6), the top pilots (Ø2.7) and the front pilots (Ø2.2); measure_holes agrees. Horizontal openings: the window has its 45° roof, the pilots and the corner reliefs are teardrops, the front pilots are flat-topped teardrops. The notch's flat top is item 6 |
| 9 | Bottom edges chamfered | PASS (note) | 0.4 mm `chamfer_plane_edges` on the plate blank (model.py l.94; bottom.png). The pocket and clamp-hole mouths are cut after it. They are loose fits (pocket +0.5) and rely on EFC 0.2, as in round 1 |
| 10 | Internal corners on load paths filleted | PASS (advisory) | **Filleted:** the rail's back root, r 2 (front.png); the window's lower corners, Ø3 reliefs (strength fix 2). **Rail front root (x 22.35, z 6), sharp:** a channel corner, because rack B's square edge runs 0.25 mm from it (model.py l.79–80), so it is accepted as round 1 accepted channel corners. It is the tension side of item 4's path, though, so fix 2's check must use Kt 2.5 there. If that fails, it needs the relief and fillet in fix 2. **Bulkhead roots (x 10 / z 6 and x 3.5 / z 8.3), sharp:** round-1 R1 was not adopted. Strength checked them at Kt 2.5, SF ≥ 5.6 (round-1 rows 13, 17) |
| 11 | Fasteners per §4 | PASS | **Wrist:** M2 × 12 + Ø6 washer over the 6.3 mm floor, 12 − 0.5 − 6.3 − 0.6 = 4.6 mm into the spline; washer edge at x 3.0, bulkhead at x 3.5. **Claw servo tabs:** M2 × 8, 5.5 mm engaged in 6.5, so no breakout; the lead-end slit is filed to 2.1 mm (BUILD_GUIDE §4 step 8). **Cover:** M3 × 10 or M3 × 18 engage 7 or 11.5 mm of the 14 mm pilots; M2.5 × 12 engage 7 mm of 10. Self-tapping is acceptable here: these come apart only for service |
| 12 | Spec §3 dims are named parameters | PASS | ZS 27.25, X_B 10, T_W 6 (RACK_SEAT 0), RAIL_X1 22.35, X_F0 32.85, and the clamp floor T_W + PAD_T − HORN_DEPTH = 6.3. The window is CLR 0.4 and END_CLR 0.2 + HOLE_COMP, so 23.0 × 12.6 printed, and the spec now says printed (round-1 fix 3). All are named, with comments, in model.py or claw_frame.py |
| 13 | Service temperature | PASS | 40 °C against PETG at ≈70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ |

## Required fixes

1. **Give the lead notch a 45° top (item 6).**
   - **Change:** add a right triangle on the notch's upper side (servo +y, which is up here), as the turntable's `_notch_tops()` does (20261025-arm-turntable/model.py l.44–59). Its legs are the notch reach, 1.6 mm. The notch top then runs from (y 7.5, z 29.45) up to the window wall at (y 6.1, z 30.85).
   - **What stays the same:** the notch's end wall at y 7.51, the 1.34 mm strip to the moved pilot, and the 4.4 mm the ribbon passes through.
   - **Rule:** §2 (overhangs ≤ 45°); deep review 01 B1 (a notch in a standing wall gets a 45° top).
   - **Evidence:** item 6. right.png shows the square notch at the window's +y end.
2. **Name the rail wall's across-layer bending, and have it checked (items 4 and 10).**
   - **Brief:** in design_brief.md's orientation section, replace "bending along its 64 mm length (≈0.9 MPa)" with the real path:
     - the rail is a 4 × 11.75 mm cantilever off the plate, so its root stress runs across the layers;
     - its tension-side root (x 22.35, z 6) is sharp;
     - at wide openings rack B's back end bears on the rail's free end at y 32.
   - **Spec:** spec §4's row ("rail wall and wrist plate, in their planes") needs the same correction. That is the Architect's file.
   - **Strength:** strength-analyst then checks the rail root under rack B's back thrust at the across-layer allowable with Kt 2.5, both mid-rail and at the y 32 end.
   - **If it fails,** the options include:
     - the rail back to a block to the bulkhead, as in round 1;
     - a 45° gusset on its back face;
     - a 45° relief of 1 mm or more on rack B's rear-bottom edge, so the front root can take an r ≥ 1 fillet. On the jaw this is the same edge that runs at the cover's lip.
   - **Rule:** §1 (trace every load path; justify loads across the layers).
   - **Evidence:** item 4. front.png shows the rail with a fillet only behind it.

## Round-1 required fixes

| Round-1 fix | Status | Evidence |
|---|---|---|
| 1. Window-roof bridge ≤ 10 mm | Done | WINDOW_ROOF 7.0. Flat 23.2 − 14 = 9.2 mm, anchored on both shoulders (item 6) |
| 2. Thicker skin over the front pilots | Done | Flat-topped Ø2.2 M2.5 pilots, round 1's alternative. 1.9 mm skin under rack B's track |
| 3. Window size stated as printed in the spec | Done | Spec §2/§3: 23.2 × 12.8 CAD, 23.0 × 12.6 printed, for the 22.8 × 12.2 MG90S (01 S1) |
| R1. Bulkhead-root fillets | Not adopted | Advisory again (item 10) |
| R2. BULK_T 6.5 | Done | 1.9 mm walls beside the top pilots |
| R3. geometry.json holes | Done | All 5 holes listed |
| Strength 1–2: full-width plate + pad, corner reliefs | Done | REAR_HALF 32, PAD_T 2.3 (floor 6.3), Ø3 teardrop reliefs |

Other round-2 changes checked:
- **Lead notch and moved pilot (01 B1, option 1):** notch 4.4 × 1.6 CAD, ≈4.2 × 1.5 printed, passes the 3.6 × 1.2 ribbon. claw_sequence_check sweeps the servo and its lead in from 20 mm out: 0 mm³.
- **MG90S window for 22.8 × 12.2 (01 S1, B2):** done.

## Recommendations (not blocking)

- R1. Fillet the bulkhead's front root r 2 (x 10, z 6). The nearest feature, the rail's back fillet, starts 6.35 mm away, and the claw servo's tabs start at z 21.15. Fillet its back root r 0.5: the clamp washer reaches x 3.0.
- R2. Process: slice_plan.json, slice_settings.json, slice_stats.json and validation.json in this folder date from before round 1. Re-slice after the DESIGN gate passes.

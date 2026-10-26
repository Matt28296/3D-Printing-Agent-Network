VERDICT: FAIL

# DFM review: 20261026-arm-claw-cover

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, print_requirements.json, renders/*.png (all 5 viewed), ../20261025-robot-arm-assembly/claw_frame.py, the jaw and frame models, slice_plan.json (read only), library/ (empty, so skill defaults apply).
Outputs are current: `build()` gives 15434.92 mm³, the same as geometry.json. Ray casts below run through `design()` in the claw frame G; in print, G +y is up.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 26.65 × 42.0 × 64.0 mm, `fits_bed: true` |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | Standing on the −y end with the C profile on the bed (iso.png, bottom.png). Slot A opens at the bed and slot B at the top (right.png) |
| 4 | Load paths vs layers | **FAIL** | The brief says "Bending of the front plate and top wall runs along the layers". In this orientation G y is print Z. Spec §4 row 1 sends the 9 N rack-A lift into "top wall bending **between screws**", and the two top screws are 37 mm apart along y. Row 2's ±20 N rack thrust pushes the front plate normal to its plane. There, slot A (y −33 to +0.25) and slot B (y −0.25 to +33) leave strips that span along y to the slot ends and to the y ±24 screws. Both cases put the bending stress along print Z, across the layers. The brief neither identifies nor justifies that |
| 5 | Bed contact | PASS (note) | 202.8 mm² under a 64 mm part, PETG. The brief asks for a brim and slice_plan.json uses a 5 mm outer brim, but print_requirements.json does not require one (R1) |
| 6 | Overhangs / bridges | PASS | The only bridge is slot A's closed end at print z 32.25: 5.5 mm (mesh_check: span 3.0 = plate thickness, length 5.5). Overhang 0.17 %. Slot B's closed end is a floor |
| 7 | Walls | PASS (note) | Front plate and top wall 3.0, top strip above slot A 3.25, lip 9.15 × 7, fin below slot B 9.25 × 3. The M3 clearance holes leave **1.2 mm** to the top wall's rear edge (x 4–5.2) and to the plate's bottom edge (z 0–1.2). Both lie under the screw heads and see little tear-out (R2). `thin_wall_warnings` is empty |
| 8 | HOLE_COMP / horizontal holes | PASS | Ø3.6 holes = 3.4 + HOLE_COMP and Ø5.2 access hole = 5.0 + HOLE_COMP, all teardrops pointing print +Z (front.png, right.png). The neck slots are open-ended gaps between islands in every layer, so they print close to the nominal 5.5 without compensation |
| 9 | Bottom edges chamfered | **FAIL** | `chamfer_plane_edges(..., −HALF_Y, 0.3)` runs at l.47, **before** slot A is cut at l.49, so slot A's mouth on the bed is square. Rays at z 30.20 and 35.80 are solid from y −32.00, while every other bed edge, the rack bearing faces included, starts at −31.75. Jaw A's neck passes through this mouth with 0.25 mm per side on every full opening (it reaches y −36 at 44 mm). The 5 mm outer brim in slice_plan.json will also fill the 5.5 mm mouth, and its flash on square edges stays in the slot |
| 10 | Internal corners on load paths | PASS (advisory) | The channel corners have to stay square because the racks' square corners run in them. The slot ends are square too. Stresses are low |
| 11 | Fasteners (§4) | PASS | M3 clearance holes through 3 mm walls into the frame's pilots (engagement in the frame review, item 11). M3×18 button heads go through here when the camera mount is fitted |
| 12 | Spec §3 dims named and matching | PASS | X_F0 27.65, Z_TOP0 39.0, RAIL_X1 19.15, slots NECK_Z ± SLOT_CLR = 5.5, all named in claw_frame.py with comments |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

1. **Correct the load-path rationale (item 4).** In design_brief.md's orientation section, name the across-layer cases: top-wall bending between the two top screws under the 9 N lift, and the front-plate strips spanning y to the slot ends and screws under the ±20 N thrust. Then have strength-analyst check them with the ×0.5 across-layer allowable. No geometry change is expected unless strength fails. Keep the orientation: lying flat would turn the slots into 32 mm bridges. Rule §1 (trace every load path; record the trade-off in the brief).
2. **Chamfer slot A's mouth (item 9).** Cut both slots **before** the bed chamfer by moving model.py l.48–50 above l.47. Slot A's mouth then gets the same 0.3 mm chamfer as the rest of the −y end. Rule §2 (bottom edges) and §6 (chamfer plus slicer compensation). Evidence: the rays above. The neck runs through this mouth with 0.25 mm clearance.

## Recommendations (not blocking)

- R1. Add `"brim_width": 5` under `min` in print_requirements.json so the validator enforces the brim that the brief and slice plan rely on. After printing, clear the brim out of slot A's mouth.
- R2. Extend the top wall rearward from x 4 to x 0, matching the camera pad's PAD_X[0]. The top-hole ligament grows from 1.2 to 5.2 mm, and the camera pad (x 0–14), which now overhangs the cover's rear edge by 4 mm, gets full support. Nothing in the claw sits at z 39–42 behind the bulkhead. Re-run assembly_check.py to confirm.
- R3. If the jaw review's neck-root fillet (jaw fix 2) is adopted, each slot's closed end moves out 1 mm: slot A to y +1.25 and slot B to y −1.25. Use a new slot-end parameter, because SLOT_CLR also sets the slot width.
- Process note: part.gcode and the other slice files were written here at about 05:24–05:25 UTC, before this review. Re-slice after the fixes.

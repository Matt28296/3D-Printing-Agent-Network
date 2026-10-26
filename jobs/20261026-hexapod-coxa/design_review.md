VERDICT: PASS

# DFM review (round 4): 20261026-hexapod-coxa

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26

**Inputs**
- This job: spec.md, design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json, print_requirements.json, slice_plan.json, status.json, log.md, and the round-3 design_review.md and strength.md.
- Renders: all 5, regenerated with `tools/render.py` and viewed. front.png was also enlarged at the lead notch.
- Assembly job: assembly_plan.md, hex_frame.py, assembly_check.json, stance_torques.json, BUILD_GUIDE.md §1 and §3.
- Deep review 05-hexapod-system.md. Also `tools/hobby_parts.py` (`servo_mount_cutter`), config/printer.json.
- Skills: fdm-design-rules, material-selection, and prusaslicer-settings for the fill settings. library/lessons.md: no entries.

**Probes:** build123d `is_inside` on the built solid. Frame C, z up in print. The vertical plate's mid-plane is y −18.5; the notch probes were also run at y −23.4 and −13.6, near both faces.

**Outputs are current.**
- `build()` gives 23312.97 mm³ and a 60.1 × 30.5 × 41.0 bbox from (−9, −23.5, 0), the same as geometry.json.
- part.stl is one watertight body (23313.04 mm³).
- `tools/mesh_check.py`, re-run in memory, gives exactly the committed mesh_check.json.
- cad_checks.py: 17/17 PASS, exit 0.

**What round 4 changed, and nothing else:**
- the 45° roof on the lead notch (DFM round 3, fix 1);
- `print_requirements.json`: `fill_density` 100 and `fill_pattern` rectilinear (strength round 3);
- spec §7 (2 per plate) and §8 (round 3's proof test).

The volume fell by 9.94 mm³ (23322.91 → 23312.97). That is exactly the roof's prism: ½ × 1.41 × 1.41 mm × the 10 mm plate. The bbox and the other 16 cad_checks are unchanged, so no other geometry moved.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits the bed with a 5 mm margin | PASS | 60.1 × 30.5 × 41.0 mm, `fits_bed: true`. Two per plate (spec §7) need about 60 × 66 mm |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, `watertight: true`, `min_z_mm: 0.0`. part.stl is 1 body |
| 3 | Orientation matches the brief | PASS | The horizontal plate is on the bed with the horn pocket on the bed face (bottom.png). The vertical plate stands. The window roof, the new lead-notch roof, the pilot teardrops, the tie-slot roof and the corner cut all point up (front.png, enlarged at the notch; iso.png) |
| 4 | Load paths | PASS (justified) | Unchanged from round 3. Hub bending runs along the layers. The plate's out-of-plane bending crosses the layers at the posts and the band under the window. The brief justifies it: the horn pocket must be on the bed. The section is strength round 1's (T_V 10, 13 mm posts, R1 reliefs, full gusset), and round 4 prints it solid |
| 5 | Bed contact | PASS | 1205.1 mm² of PETG, which warps little |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | `overhang_pct` 1.6 (131.4 mm²; round 3: 1.77). **Round 3's z 22.2 "bridge" (span 1.41, length 10.0), the one-sided ledge, is gone.** The notch ceiling now follows z = 22.2 + (39.51 − x) to within 0.01 mm at x 38.15, 38.4, 38.7, 39.0, 39.3 and 39.45, through the whole plate (y −23.4, −18.5, −13.6). Rows: z 22.3 is solid from x 39.41, z 23.0 from 38.71, z 23.55 from 38.16, and z 23.7 from 38.10, the window face. Every ceiling over the lead's path is 45°. What mesh_check still lists: the horn-pocket ceiling at z 2.0 (span 7.9, closed all round), 0.1 mm² at z 7.99, and the pilot slots' far-end arcs at z 20.85 (span 0.17, 1.8 mm² each), which bridge themselves (round 3) |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (note) | T_V 10, posts 13.5 / 13.0 at the window floor (cad_checks), 6.0 mm floor under the horn. The roof leaves the outer post 11.66 wide at z 22.25 (solid x 39.46–51.12), more than the pilot row's net 9.50 (1.35 + 8.15), which stays the smallest section. The roof's nearest point, (39.51, 22.2), is 2.25 mm from the moved pilot's hole, teardrop included. The ligaments are unchanged on the z 20 row: inboard pilot to window 1.46 (solid 13.45–14.91), notch end wall to moved pilot 1.35 (solid 39.51–40.86), about 1.65 / 1.55 printed. Both are solid, above 0.9 and above hobby_parts' 1.5 mm printed minimum. `thin_wall_warnings: []` |
| 8 | HOLE_COMP; horizontal holes teardrop or flat-top | PASS | `HOLE_COMP = HOLE_COMP_DEFAULT` (0.2) goes into both cutters: window 23.2 × 12.8 CAD, notch 4.2 + 0.2 wide reaching 1.5 + 0.1 past the case end, pilots Ø1.7, clamp Ø2.6 (geometry.json). Every horizontal opening has a 45° top: the window roof, the **notch roof (fixed this round)**, the pilot teardrops, the tie-slot roof, and the relief teardrops, whose points lie inside the window |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(br, 0.0, BED_CHAMFER)` with 0.4 (model.py:97) on the hub and arm, which are the whole bed outline (bottom.png). The horn-pocket rim relies on `elefant_foot_compensation` 0.2, as in rounds 2–3 |
| 10 | Internal corners on load paths filleted | PASS | Unchanged from round 3: R1 T-bone reliefs at the window floor, the 45° × 4.9 gusset along the whole plate, the 45° × 8 ramp at the hub step, and the r2.5 hub-to-arm fillet (cad_checks; top.png). The roof turns the notch's top corner at the end wall from 90° to an obtuse 135° |
| 11 | Fasteners per §4 | PASS | Unchanged. Femur servo: 2 × M2 × 10 self-tapping, 7.5 mm into the 10 mm plate through Ø1.7 CAD pilots. The outboard one goes through the tab's slit filed to 2.1 mm (spec §2, BUILD_GUIDE). Horn: M2 × 12 (× 14 for a deep shaft thread) with a Ø10 × 1 penny washer on the flat hub, driven snug (rule §4: a washer against creep). At 100 % infill the floor under that washer is solid (strength) |
| 12 | Spec §3 dimensions are named parameters | PASS | The roof adds `NOTCH_END_X` (39.51), `NOTCH_TOP` (22.2) and `NOTCH_ROOF`, each with a source comment (model.py:51–56). Spec §3 and the brief's notch rows say "4.4 at the end wall, opening at 45° to 5.8 at the window face". Probed: 4.4 at x 39.45 (z 17.8–22.2) and 5.81 at the window face (z 17.8–23.61). The other §3 rows are as round 3: L_C 32, Z_F 20, T_V 10, POST_W 13, T_C 8, the window and the pilots |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG ≈ 70 °C. At the assembly spec's 50 °C servo-case limit the margin is exactly 20 °C. `materials_on_hand` in config/printer.json is still empty (spec §6 says to check before slicing) |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

## Required fixes

None.

## Round-3 fix checked

1. **45° roof on the lead notch: done.**
   - The triangle (38.1, 22.2), (39.51, 22.2), (38.1, 23.61) is cut through the plate (y −24.5 … −12.5) with `_prism_y` (model.py:114). See the probes in #6.
   - mesh_check's z 22.2 entry is gone.
   - The follow-ups round 3 listed:
     - cad_checks.py moved the notch's solid probe to (39.6, z 22.4) and added the void probe (38.4, 23.2) and the solid probe (39.3, 22.5) (cad_checks.py:61–65);
     - spec §3 and the brief's notch rows say "4.4 at the end wall, opening at 45° to 5.8 at the window face";
     - the brief's Orientation section no longer calls the notch top a bridge;
     - the part was rebuilt, mesh-checked, rendered and cad-checked (17/17).

Round 3's recommendations:
- Strength round 3 re-checked the pilot ligaments, the filed slit and the plate's rows.
- `slice_plan.json` still disagrees with the brief; see "For slicing".

## Print settings (round 4): `print_requirements.json` against the brief

| Key | Value | Brief / spec |
|---|---|---|
| perimeters, top / bottom solid layers | ≥ 4, ≥ 5 / 5 | as rounds 2–3 |
| `fill_density` | ≥ 100 | spec §6 "Print solid: 100 % infill"; brief round-4 table #2 |
| `fill_pattern` | rectilinear | spec §6, brief #2 |
| layer height | ≤ 0.2 | 0.20 mm QUALITY |
| nozzle / bed | 230–250 / 80–90 °C | PETG (material-selection) |
| `max_print_hours` | 6 | spec §7: one plate of 2 brackets |

- **They match.**
- **Rectilinear is the right pattern at 100 %.** PrusaSlicer treats gyroid as unsuitable at 100 % density and offers to switch to rectilinear. The prusaslicer-settings skill allows 100 % for small, highly loaded parts. The arm-claw-pinion job uses the same pair (100, rectilinear).
- **No DFM objection to solid printing.** The window, notch and pilots are each bounded by 4 perimeters, so their printed size does not depend on the infill.

## For slicing (not DFM failures)

- **`slice_plan.json` is stale.** It still says `fill_density` 50 %, `fill_pattern` gyroid and 6 copies. It must become 100 %, rectilinear and 2 copies per plate (3 plates). The validator enforces the first two from `print_requirements.json`. Strength's script shows why it matters: at 50 % gyroid the horn clamp is back at SF 2.91 in the drop.
- **Print time is at risk.** Two per plate at 100 % is about 4.9–6.3 h (the brief's estimate, scaled by filament mass) against `max_print_hours` 6, which the validator checks against the slice estimate. If it runs over, relaxing spec §7 (or printing 1 per plate) is the user's call.
- **Short layer times.** The posts' upper layers (two 13 × 10 mm islands per bracket) print quickly. The PETG profile's minimum layer time will slow them; that is expected.
- **Bed release.** The only sheet is smooth PEI (config/printer.json). PETG bonds hard to it, so use glue stick as a release layer (material-selection). Put it in preflight.md.

## Recommendations (not blocking)

- **Check the first plate before printing the other two.** Fit a MG90S through the window and notch and through its filed slit, and fit a horn in the pocket. A solid PETG part shows any over-extrusion more than a 50 % one, and the window ends have 0.1 mm clearance. The brief already says to fit one servo before filing six slits.
- **Tie slot.** It still has no HOLE_COMP: 1.8 × 3.2 CAD prints about 1.6 × 3.0. BUILD_GUIDE's ties (≤ 2.5 wide, about 1 thick) still pass.

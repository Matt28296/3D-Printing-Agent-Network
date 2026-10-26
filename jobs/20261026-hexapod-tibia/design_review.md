VERDICT: PASS

# DFM review (round 3): 20261026-hexapod-tibia

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26

**Inputs**
- This job: spec.md (round 3), design_brief.md, model.py, geometry.json, mesh_check.json, print_requirements.json, slice_plan.json, strength.md (round 1).
- The previous review: round 1, PASS. The tibia had no round-2 DFM review. There is no cad_checks.py in this job.
- Renders: all 5, regenerated with `tools/render.py` and viewed.
- Assembly job: assembly_plan.md, hex_frame.py, BUILD_GUIDE.md, assembly_check.json (`clean: true`).
- Deep review: 01-bought-parts.md (B1, B2) and 05-hexapod-system.md. Also tools/hobby_parts.py.
- library/lessons.md: no entries.

**Probes:** trimesh `contains` on part.stl. Frame T, z up in print; the back face (z 0) is on the bed.

**The geometry is unchanged since round 1.**
- `build()` gives 7016.92 mm³ and a 79.0 × 18.0 × 7.0 bbox from (−9, −9, 0). That matches geometry.json and the round-1 review.
- part.stl is one watertight body.
- `tools/mesh_check.py`, re-run in memory, gives exactly the committed mesh_check.json: overhang 3.47 %, one bridge of 7.9 mm, contact 851.4 mm², the same as round 1.
- The MG90S's own spec (B2) keeps the horn sizes, so the pocket is the same.

This review checks the part against the round-3 spec.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits the bed with a 5 mm margin | PASS | 79.0 × 18.0 × 7.0 mm |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, `watertight: true`, `min_z_mm: 0.0`. part.stl is 1 body |
| 3 | Orientation matches the brief | PASS | Flat, with the horn pocket on the bed face (bottom.png) |
| 4 | Load paths | PASS | Round 3's tucked stance (spec §4) adds bending in the plate's own plane, and the stance load runs along the tibia. Both run along the layers. A sideways shove puts face tension along x, also along the layers |
| 5 | Bed contact | PASS | 851.4 mm² |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | `overhang_pct` 3.47. The only bridge is the horn-pocket ceiling, 7.9 mm at z 2.0 |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | Hub wall round the pocket 9.0 − 3.95 = 5.05 (y 0 row at z 1: solid −9.0…−3.95). Beside the horn-arm tip (x 14), 8.04 − 2.45 = 5.59. Floor 5.0 (solid z 2–7). Foot Ø9 (x 65.5: solid ±4.5). `thin_wall_warnings: []` |
| 8 | HOLE_COMP; horizontal holes | PASS | `horn_pocket_cutter(..., hole_comp=HOLE_COMP)`: pocket +0.7, clamp Ø2.6. No horizontal holes |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(t, 0.0, 0.4)` (model.py:36) |
| 10 | Internal corners on load paths filleted | PASS | The outline is convex except a ≈ 4° kink where the flank meets the Ø9 foot circle. No re-entrant corners |
| 11 | Fasteners per §4 | PASS | M2 × 12 clamp screw with a Ø6 washer on the flat front face, driven snug (≈ 0.05 N·m, spec §2). M2 × 10 if the shaft thread bottoms before 6.5 mm, which settles the round-1 note. The horn's anti-rotation screw is pilot-drilled through the horn |
| 12 | Spec §3 dimensions are named parameters | PASS | `L_T` 70.0 (hex_frame.py:56) is the foot tip (`xf = L_T − FOOT_R`; the probe is solid to x 70.0). Floor 5.0 = `T_T` 7 − the 2 mm pocket |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG ≈ 70 °C. Before slicing: `materials_on_hand` in config/printer.json is empty |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

**Against the round-3 spec:**
- **§2 asks that nothing stand proud of the back face**, which now runs 3.1 mm off the femur's front face. The back face is the bed face: flat, with only the recessed horn pocket and the 0.4 mm edge chamfer. The front face is flat too: the z 6.95 row is solid except at the clamp hole.
- **The femur's clamp head and washer** stand 2.1 mm proud of the femur. They leave 1.0 mm, and the tibia only reaches them folded back past the femur axis (assembly plan, interfaces). The assembly check is clean over the femur's −70…+90° and the tibia's −80…+90°.

## Required fixes

None.

## Round 1 checked

- No required fixes in round 1.
- Its note on the clamp-screw length is now in spec §2: M2 × 12, or × 10 if the thread bottoms before 6.5 mm.

## Recommendations (not blocking)

- **geometry.json `holes`** still holds an error (`"type NoneType doesn't define __round__ method"`), as in round 1. The other four hexapod jobs now get a valid list. This is for the toolsmith.
- **Print layout:** slice_plan.json prints 6 per plate. Round 2's slice of six took 3.9 h against spec §7's 3 h. The brief proposes 4 + 2, which is the slicing stage's call. There is no DFM objection.
- **Strength:** re-check the tucked-stance bending at the round-3 mass. The spec gives knee torques of 86–98 N·mm, capped by the 216 N·mm stall that strength checked.

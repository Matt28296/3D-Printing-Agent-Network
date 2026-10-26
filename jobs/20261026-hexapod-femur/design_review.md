VERDICT: PASS

# DFM review (round 1): 20261026-hexapod-femur

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), ../20261026-hexapod-assembly/{hex_frame.py, assembly_plan.md, assembly_check.json}, tools/hobby_parts.py, library/lessons.md (no entries). Section probe run on part.stl.
Outputs are current: `build()` gives 6069.39 mm³, the same as geometry.json. model.py (21:44:39) is older than part.stl (21:44:48). The geometry.json `holes` field still holds an error (toolsmith, advisory).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 64.9 × 19.0 × 7.0 mm |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | Flat, horn pocket on the bed face (bottom.png). Servo tab face up (top.png) |
| 4 | Load paths | PASS | Foot load and femur stall bend the plate in its own plane (19 mm deep), along the layers. Sideways shove is out-of-plane bending, with face tension along the layers too |
| 5 | Bed contact | PASS | 722.3 mm² |
| 6 | Overhangs / bridges | PASS | `overhang_pct` 3.27. Only bridge: the horn-pocket ceiling, span 7.9 mm at z 2.0. The window and pilots are vertical through-cuts |
| 7 | Walls | PASS | Rails beside the window: 9.5 − 6.3 = 3.2 mm. Pilot-to-window ligaments 1.62 / 1.62 mm CAD (section y 0, z 3.5: solid 26.60–28.22 and 51.10–52.72), ≈ 1.8 mm printed, as accepted on the arm. Outer pilot edge 54.80 → plate end 56.92 = 2.12 mm. Horn-pocket floor 5.0 mm, pocket-to-X0 wall 4.05 mm. `thin_wall_warnings: []` |
| 8 | HOLE_COMP / teardrops | PASS | HOLE_COMP 0.2 in both cutters: window 22.9 × 12.6 CAD (x 28.2…51.1), pilots Ø1.7 slotted 0.4 outward, pocket +0.7, clamp Ø2.6. No horizontal holes |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(f, 0.0, 0.4)` |
| 10 | Internal corners | PASS (advisory) | The window's corners are sharp, as the servo needs, but the window is in the low-moment zone. The moment there is at most 4 N × (45 − 28.2) ≈ 67 N·mm plus the tibia's share, on a two-rail section with Z ≈ 298 mm³ |
| 11 | Fasteners | PASS (see cross-part note) | Tibia tab screws go into Ø1.7 vertical pilots through 7 mm: an M2×8 engages ≈ 5.5 mm after the 2.5 mm tab. The tab tips (x 23.55…55.75) land on solid plate: at y ±6 the r 6 end reaches x 56.37. The clamp washer Ø6 seats on the flat front face at x 0 |
| 12 | Critical dims named | PASS | `L_F = 45.0` (hex_frame.py), as in spec §3 |
| 13 | Service temperature | PASS | 40 °C against PETG ≈ 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

None.

Notes for the next stages (not blocking this part):
- Centre-screw stack: 5.0 mm floor + 0.5 washer means an M2×12 runs 6.5 mm past the horn face. The coxa (3.0 mm floor) needs a different length (see the coxa review). Confirm that the MG90S spline bore takes 6.5 mm, or use M2×10.
- Tab-screw engagement is ≈ 5.5 mm. On the arm, about 5 mm of engagement was found to pull out under the SG90 stall case (20261025-arm-forearm strength round 2). Strength-analyst should check the tibia-stall pull-out here.
- The window has no lead notch and its printed end clearance is ≈ 0.1 mm. Check on one real MG90S that the lead exit passes.

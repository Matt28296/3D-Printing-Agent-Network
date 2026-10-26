VERDICT: PASS

# DFM review (round 1): 20261026-hexapod-body-bottom

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), ../20261026-hexapod-assembly/{hex_frame.py, assembly_plan.md, assembly_check.py, assembly_check.json}, ../20261026-hexapod-body-top/model.py (the interface), tools/hobby_parts.py, library/lessons.md (no entries).
Outputs are current: `build()` gives 73338.66 mm³, the same as geometry.json. The geometry.json `holes` field still holds an error (toolsmith, advisory).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 154.9 × 131.1 × 34.0 mm on 250 × 210 |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | The tab face (underside) is on the bed and the columns rise up (iso.png). The servo frame `z_dir=(0,0,-1)` puts the cutter's plate band at Z 0…4, so the tabs bear on the flat bed face |
| 4 | Load paths | PASS | Robot weight comes up through the shafts. It pushes the tabs **into** the plate's underside (bearing), not out through the screws. Plate bending runs along the layers. The brief records that tab-screw pull-out runs across the layers |
| 5 | Bed contact | PASS | 16694 mm² of PETG |
| 6 | Overhangs / bridges | PASS | `overhang_pct` 0.0, `bridges: []` |
| 7 | Walls | PASS | Plate 4 mm. Pilot-to-window ligament 1.6 mm CAD (same cutter as the femur: 1.62 measured there), ≈ 1.8 mm printed. Pilot to plate edge: 5.0 − 0.4 − 0.85 = 3.75 mm. Window side to edge: 11.0 − 6.3 = 4.7 mm. Column wall (8 − 2.8)/2 = 2.6 mm |
| 8 | HOLE_COMP / teardrops | PASS | Windows 22.9 × 12.6 CAD, pilots Ø1.7 (servo cutter with `hole_comp=HOLE_COMP`), column pilots Ø2.6 + 0.2. All vertical |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(bp.part, 0.0, 0.4)` on the blank |
| 10 | Internal corners | PASS (advisory) | The column roots are sharp (iso.png). Handling lift (6 N over 4 columns) gives about 0.03 MPa across the layers, so the risk is low. Add an r 1.5 root fillet anyway if COLUMN_H grows (see body-top review) |
| 11 | Fasteners | PASS | The coxa tab screws (M2×8) go through the 2.5 mm tab into 4 mm of plate and stick out 1.5 mm on top, clear of the servo body. The 4 × M3×8 self-tapping screws from the 3 mm top plate engage 5 mm of a 10 mm Ø2.8 pilot |
| 12 | Critical dims named | PASS | LEG_MOUNTS, T_BODY and COLUMN_H come from hex_frame.py. COLUMNS, COLUMN_D, CLR, END_CLR and HOLE_COMP are named. **But** spec §3 / brief "22.7 × 12.6 printed" is wrong. The CAD window is 22.9 × 12.6, so it prints at ≈ 22.7 × **12.4** |
| 13 | Service temperature | PASS | 40 °C against PETG ≈ 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

The LiPo fits: its strap slots are at y ±(18.5…21.5), outside the 35 mm LiPo, and it slides along x between the columns (gap y ±21). The coxa servo bodies rise 11.9 mm above the plate (Z 15.9 < 34). The assembly check finds no stance collisions.

## Required fixes

None for this part on its own.

Conditional: this part sets the column pattern (±30, ±25) and COLUMN_H 30 that the top plate depends on. The body-top review **fails** on both: its PCA9685 posts sit on the column screws, and its ESP32 jumper housings end 0.5 mm above the LiPo. If that fix moves COLUMNS or changes COLUMN_H, rebuild and re-review this part. Also correct spec §3's printed window width (12.4, not 12.6).

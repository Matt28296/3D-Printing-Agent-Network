VERDICT: FAIL

# DFM review (round 2): 20261026-hexapod-body-bottom

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), the round-1 review, ../20261026-hexapod-assembly/{hex_frame.py, assembly_check.py, assembly_check.json, assembly_plan.md, BUILD_GUIDE.md}, ../20261026-hexapod-body-top/model.py, tools/hobby_parts.py, library/lessons.md (no entries). Section probes: `mesh.contains` on part.stl.

Outputs are current: `build()` gives 75401.89 mm³ and a 154.902 × 131.1 × 44.0 bbox, identical to geometry.json, and model.py (05:18:57 UTC) is older than part.stl (05:19:07).

The geometry is sound. The FAIL is documentation only (#12): the spec and the brief state a window size the model does not make.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 154.9 × 131.1 × 44.0 mm on 250 × 210 |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | The tab face (underside) is on the bed and the columns rise up (iso.png, front.png, right.png) |
| 4 | Load paths | PASS | As in round 1: the robot's weight pushes the coxa tabs into the plate (bearing), plate bending runs along the layers, and the brief records tab-screw pull-out across the layers. The taller columns take the top-plate handling lift across the layers: about 1.4 N per Ø8 column, ≈ 0.03 MPa |
| 5 | Bed contact | PASS | 16694.3 mm² of PETG |
| 6 | Overhangs / bridges | PASS | `overhang_pct` 0.0, `bridges: []`. The root fillets shrink as they rise, so they are not overhangs |
| 7 | Walls | PASS | Plate 4 mm. Pilot-to-window ligament 1.6 mm CAD (middle-left window probe: pilot at y 31.5–33.6, window from y 35.2), ≈ 1.8 mm printed. Pilot to plate edge 3.75 mm. Column wall (8 − 2.8)/2 = 2.6 mm. `thin_wall_warnings: []` |
| 8 | HOLE_COMP / teardrops | PASS | Windows are 22.9 × 12.6 CAD (probe: void y 35.2–58.1 and x ±6.32). Pilots Ø1.7. Column pilots Ø2.6 + 0.2. All holes are vertical |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(bp.part, 0.0, 0.4)` on the blank |
| 10 | Internal corners | PASS | The column roots now have r1.5 fillets (`COLUMN_FILLET`). Probe at (40, 25): radius 4.96 at z 4.1, 4.38 at z 4.5, 4.0 from z 5.4 (front.png, right.png). The window corners are in a flat plate that bends along the layers |
| 11 | Fasteners | PASS | Coxa tab screws: M2×8 through the 2.5 mm tab and the 4 mm plate, 1.5 mm proud. Top plate: 4 × M3×8 self-tapping into Ø2.8 CAD pilots 10 mm deep (probe: bore z 34–44), 5 mm engaged below the 3 mm deck. Each column now sits 1.75 mm from the nearest corner servo's inner pilot slot (column centre at servo x −26.25, y 0.17; slot out to x −20.5). The r1.5 fillet foot ends 0.25 mm short of the slot (probe along the servo axis at z 4.05: solid to x −21.14), so the pilot does not cut the fillet and the screw tip clears it |
| 12 | Critical dims named | **FAIL** | Spec §3 and the brief give the coxa windows as "22.7 × 12.6 printed, +0.3/−0". The model cuts 22.9 × 12.6 CAD (`SERVO` + `CLR` 0.4 / `END_CLR` 0.2 + `HOLE_COMP` 0.2; probe in #8), which prints at about 22.7 × **12.4**. That is 0.2 mm below the spec's own tolerance. The same row's "0.1 end / 0.2 side clearance" and the brief's "+0.4 side / +0.2 end" agree with the model, so the nominal is what is wrong. Spec §2 now says "22.9 × 12.8"; the CAD width is 12.6. Round 1 asked for this correction and it was not made. Spec §1 and the brief's concept still say "four 30 mm columns", but `COLUMN_H` is 40, as §2 and §3 say. Mount positions (`LEG_MOUNTS`) and column height 40.0 (`COLUMN_H`, hex_frame.py:39, with a comment) match |
| 13 | Service temperature | PASS | 40 °C against PETG ≈ 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

1. **Make spec.md and design_brief.md state the windows the model makes** (checklist #12; evidence above).
   - Spec §3 and the brief's table: "22.7 × 12.4 printed". Keep +0.3/−0 and "0.1 end / 0.2 side clearance".
   - Spec §2: "22.9 × 12.6 CAD".
   - Spec §1 and the brief's concept: "four 40 mm columns".

   This is documentation only, with no model change or rebuild. If 12.6 printed was really intended, raise `CLR` to 0.6 instead and re-run everything, including the assembly check.

## Round 1 fixes checked

- Rebuild after the column change: **done.**
  - The columns come from `hex_frame.COLUMNS` (±40, ±25) and `COLUMN_H` 40 (model.py:18). The top plate shares them (`SCREWS = COLUMNS`).
  - The part was rebuilt at 05:19 UTC and assembly_check.py was re-run at 05:20 UTC with a clear stance.
  - The LiPo (x ±35, y ±17.5) still slides between the columns: the gap is y ±19.5 at the fillet foot.
- r1.5 root fillets on the taller columns: **done** (probe in #10).
- Correct spec §3's printed window width: **not done** (fix 1).

## Recommendations

- MG90S lead exit, as on the coxa and femur: the coxa servos go in from below, case first. Each lead leaves its case at the inner end, where the printed end clearance is ≈ 0.1 mm. On the corner servos the lead then has only 5.6 mm to bend before it reaches the column. Fit one real servo before printing.
- BUILD_GUIDE.md now puts the UBEC on its side beside the LiPo. There is room for it (y ≈ 22–31, between the strap slot and the middle servo window), but the assembly check has no UBEC dummy. Add one.
- The geometry.json `holes` field still holds an error (toolsmith).

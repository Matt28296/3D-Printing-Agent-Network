VERDICT: PASS

# DFM review: 20261025-arm-turntable-ring

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), assembly_plan.md, base model.py, library/lessons.md (no entries).
Outputs are current: `build()` gives 12667.0 mm³, matching geometry.json (12667.02 mm³).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 92.1 × 97.0 × 13.0 mm; `fits_bed: true` |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, `min_z_mm: 0.0` |
| 3 | Orientation matches brief | PASS | Printed flat with the tabs on the bed (iso.png, front.png) |
| 4 | Load paths | PASS | The knock load puts the 13 mm wall in pure compression across the layers (brief), and the tab screws in shear in the XY plane |
| 5 | Bed contact | PASS | 860.4 mm² of PETG on a thin ring is enough |
| 6 | Overhangs / bridges | PASS | The only overhang faces are the 45° bottom chamfer, tessellated at n_z −0.718 (all at z 0.13, 26 mm², which is the 0.28% in mesh_check). No bridges |
| 7 | Walls | PASS | Ring wall R_OUT − R_IN = 3.5 mm. Tabs 3.0 thick. Tab disc Ø9 around Ø3.4 leaves a 2.8 mm wall |
| 8 | Fit holes / HOLE_COMP | PASS (note) | Only the Ø3.4 M3 clearance holes. Spec §3 allows ±0.2, so the default 0.2 mm undersize (about Ø3.2) stays inside tolerance and still clears M3. There is still no `HOLE_COMP` parameter: add one for consistency with the other parts |
| 9 | Bottom edges chamfered | PASS | `chamfer_bottom(design(), 0.4)` |
| 10 | Internal corners on load paths | PASS (advisory) | The web-to-ring corners at the tabs are sharp (top.png), but the load is small: 20 N short-term, shared by 3 tabs |
| 11 | Fasteners | PASS | M3×8 self-tapping through the 3 mm tab into the 4 mm base plate gives 4 mm of engagement, and the tip comes out 1 mm below the plate |
| 12 | Critical dims named | PASS | `H = TURNTABLE_Z − RUN_GAP` = 14.5 − 1.5 = 13.0 (spec 13.0), `TAB_R = 48`, `TAB_HOLE = 3.4`, `TAB_ANG` matches the base `RING_PILOT_ANG` (30°, 150°, 270°) |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C. The brief's "~80 °C" should read about 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

None.

## Notes (not blocking)

1. Cross-part: the 270° tab reaches y −52.5 (geometry.json `bbox_min` y −52.5), but the base's outer face is at y −52.0, so the tab hangs 0.5 mm past the base edge. Its pilot also breaks 0.3 mm into the base's inner wall. Move `TAB_R` and the base's `RING_PILOT_R` to 47 together.
2. The 1.5 mm running gap assumes the turntable's horn-slot ceiling prints flat. That ceiling is a bridge (longest strand 10.6 mm, see the turntable review), and any sag lowers the turntable towards the ring. The acceptance step "sand the ring top if it rubs" covers this.
3. Add `HOLE_COMP` as a named parameter, even though no fix is needed here.

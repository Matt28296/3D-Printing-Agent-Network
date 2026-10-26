VERDICT: PASS

# DFM review (round 2): 20261025-arm-turntable-ring

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), base and turntable model.py, library/lessons.md (no entries).
Outputs are current: `build()` gives 12452.3 mm³, matching geometry.json (12452.3 mm³).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 91.3 × 96.0 × 15.0 mm |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | Tabs on the bed (iso.png, front.png) |
| 4 | Load paths | PASS | The wall takes compression across the layers and the tabs take in-plane shear |
| 5 | Bed contact | PASS | 718.7 mm² |
| 6 | Overhangs / bridges | PASS | The only overhang faces are the tessellated 45° bottom chamfer (23.3 mm², 0.23%). No bridges |
| 7 | Walls | PASS | R_OUT − R_IN = 44 − 41 = 3.0. Tab Ø9 around Ø3.6 leaves 2.7. Tabs 3.0 thick. No thin regions in sections at z 1 and z 8 |
| 8 | HOLE_COMP | PASS | `HOLE_COMP` (0.2, sourced). Tab holes Ø3.6 in CAD (geometry.json) print at about Ø3.4 |
| 9 | Bottom edges chamfered | PASS | `chamfer_bottom(design(), 0.4)` |
| 10 | Internal corners | PASS (advisory) | The web-to-ring corners are sharp, but the load is low (compression only) |
| 11 | Fasteners | PASS | M3×6 through the 3 mm tab gives 3 mm in the 4 mm plate pilot. The tip stays inside the plate, clear of the ESP32 under it |
| 12 | Critical dims named | PASS | `H = horn_face_z(MG996R) − RUN_GAP` = 16.5 − 1.5 = 15.0, matching the turntable underside at Z 16.5. `TAB_R = 47.5` matches the base's `RING_PILOT_R`, and `TAB_ANG` matches too |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

None.

## Round 1 → round 2

| Round-1 finding | Status | How I checked |
|---|---|---|
| 270° tab overhung the base edge by 0.5 mm | Closed | The tab reaches r 47.5 + 4.5 = 52.0. geometry.json `bbox_min` y is −52.0, equal to the base outer face ±52.0 (flush) |
| No HOLE_COMP parameter | Closed | `HOLE_COMP` is applied to the tab holes |
| Ring gap depends on slot-ceiling sag | Closed | The turntable no longer has a horn pocket, so its underside is the flat bed face at Z 16.5 |

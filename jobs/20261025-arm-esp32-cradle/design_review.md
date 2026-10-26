VERDICT: PASS

# DFM review (round 3): 20261025-arm-esp32-cradle

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), base model.py and spec.md, tools/hobby_parts.py, assembly_plan.md, library/lessons.md (no entries).
Outputs are current: `build()` gives 11498.6 mm³, matching geometry.json (11498.57 mm³).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 66.5 × 43.25 × 10 mm |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | The Z −20 face is on the bed. Counterbores open from the bed side (bottom.png) |
| 4 | Load paths | PASS | Non-structural |
| 5 | Bed contact | PASS | 1055.6 mm² |
| 6 | Overhangs / bridges | PASS (note) | The three counterbore ceilings at print z 6 are annular bridges (25.1 mm² each, bounding-box span 6.7). Each runs 1.55 mm from Ø6.7 in to the Ø3.6 hole, well under 10 |
| 7 | Walls | PASS | WALL 2.5. Counterbore walls: pad 5.8 − 3.35 = 2.45, far block x 12.75 − 15.5 → 2.75, towards the pocket 2.05, y sides 4.0. The USB ledge is 2.8 wide. No region under 1.8 mm at z 1, 5, 7 and 9 |
| 8 | HOLE_COMP | PASS | Holes Ø3.6 and counterbores Ø6.7 in CAD (geometry.json). `HALF = 14.15 + 0.6 + 0.1` = 14.85, so the pocket is 29.7 in CAD and prints at about 29.5 (spec §3) |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(c, BOT, 0.4)` |
| 10 | Internal corners | PASS | Non-structural |
| 11 | Fasteners | PASS | Spec §2 now says "3 × M3×10 … (4 mm clamp + 6 mm thread)". The head sits on the counterbore floor at Z −14 and the tip reaches Z −4, the end of the base's 6 mm Ø2.8 boss pilot (Z −10 to −4). That gives 6 mm of engagement with no overshoot |
| 12 | Critical dims named | PASS | `HALF`, `PCB_BOT`, `CBORE_D`, `CBORE_DEPTH`, and `SCREWS` matching the base `CRADLE_PILOTS` |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

None.

## Round 1 → round 2

| Round-1 finding | Status | How I checked |
|---|---|---|
| 2 mm screw engagement | Replaced by an overshoot | The counterbores are in, but M3×12 overshoots the pilot (item 11) |
| No bottom chamfer | Closed | `chamfer_plane_edges` on the blank |
| Pocket width without HOLE_COMP | Closed | `HALF` includes `HOLE_COMP/2` |
| USB ledge tangent to the base corner pillar | Closed | Ledge y1 is 41.5, so the corner (49.5, 41.5) is 5.0 mm from the pillar centre (49.5, 46.5): **1.0 mm** clear of r 4. The +Y wall still stops at x 44 against the pillar edge at x 45.5 |
| −Y wall beside the base servo | Open (note) | y_out0 = 28 − 14.85 − 2.5 = 10.65 against the servo body at y 9.85 nominal: 0.8 mm gap, or 0.6 with the window float. Check it against your measured servo |

## Notes

1. The USB ledge (x 48.2–51) relies on the last header pins sitting at x ≤ 47.9 (model.py comment), which leaves 0.3 mm to the jumper housings. That figure isn't in `BoardSpec`, so check it on your board.
2. The assembly plan's fastener row is now current (M3×6 ring, M3×10 cradle).

## Round 2 → round 3

| Round-2 finding | Status | How I checked |
|---|---|---|
| M3×12 overshoots the base pilots by 2 mm | Closed | This spec §2, the base spec §2, assembly_plan.md line 16 and BUILD_GUIDE.md line 34 ("not longer: the boss pilots are 6 mm deep") all say M3×10. The geometry is unchanged: rebuilt 11498.6 mm³ = geometry.json |

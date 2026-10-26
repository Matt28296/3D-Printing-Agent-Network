VERDICT: FAIL

# DFM review (round 2): 20261025-arm-esp32-cradle

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
| 11 | Fasteners | **FAIL** | Spec §2 calls for "3 × M3×12 … (4 mm clamp + ~8 mm thread)", but the base's cradle pilots are only **6 mm** deep: Ø2.8 from Z −10 to −4, blind (base model.py `CRADLE_BOSS_L + 1` cylinder starting at Z −11). With the head on the counterbore floor at Z −14 (BOT −20 + `CBORE_DEPTH` 6), an M3×12 tip reaches Z −2, 2 mm into unpiloted plate with only 2 mm of plate left under the base's bed face. The screw bottoms out before it clamps, or cracks or raises the plate top |
| 12 | Critical dims named | PASS | `HALF`, `PCB_BOT`, `CBORE_D`, `CBORE_DEPTH`, and `SCREWS` matching the base `CRADLE_PILOTS` |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

1. **Use M3×10, not M3×12** (rule §4, checklist 11). The head seats at Z −14 and the tip reaches Z −4, which is exactly the end of the 6 mm pilot: 6 mm of engagement plus the 4 mm clamp. Update this spec, the base spec §2 and the assembly plan's fastener row. The alternative is deepening the base pilots (see the base review).

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
2. The assembly plan's "Decisions" row still lists M3×8 for the ring and the cradle, which is stale against the specs (M3×6 ring, and M3×12, to become M3×10, for the cradle).

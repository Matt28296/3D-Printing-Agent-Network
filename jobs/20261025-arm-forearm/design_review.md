VERDICT: PASS

# DFM review (round 2): 20261025-arm-forearm

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), tools/hobby_parts.py (round 2), assembly_plan.md, library/lessons.md (no entries).
Outputs are current: `build()` gives 29381.4 mm³, matching geometry.json (29381.42 mm³). The geometry.json `holes` field still holds an error (toolsmith, advisory).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 129 × 26 × 10 mm |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | Front face down: the slot opens upward (iso.png, top.png) |
| 4 | Load paths | PASS | Bending runs along the layers |
| 5 | Bed contact | PASS | 2888.6 mm² |
| 6 | Overhangs / bridges | PASS | `overhang_pct` 0.0 and `bridges` is empty |
| 7 | Walls | PASS | The SG90 pilot-to-window ligament is 1.60 / 1.65 mm in CAD (section z 5, y 0: solid 71.60–73.20 and 96.10–97.75). Printed it is about 2.65 − 0.1 (end clearance per end) − 0.75 (printed pilot radius) = **1.80 mm**, which meets the round-1 criterion. The rails beside the window are (26 − 12.6)/2 = 6.7 mm |
| 8 | HOLE_COMP | PASS | `HOLE_COMP` on the slot (clearance 0.7 CAD, clamp hole Ø3.6) and the SG90 window: CAD 22.9 × 12.6, which prints at 22.7 × 12.4 (spec). Pilots CAD Ø1.7 print at Ø1.5 |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(arm, T, 0.4)` on the bed (front) face |
| 10 | Internal corners | PASS (advisory) | Window corners are sharp, but the section is now 10 mm thick |
| 11 | Fasteners | PASS | The M3×16 clamp screw and Ø9 washer seat on the flat front face. The SG90 tab screws go into Ø1.5 printed pilots, 10 mm deep |
| 12 | Critical dims named | PASS | `L = 90.0`, `CLR`, `END_CLR = 0.2`, `HOLE_COMP` |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

None.

## Round 1 → round 2

| Round-1 finding | Status | How I checked |
|---|---|---|
| Slot-ceiling bridge 10.6 mm | Closed | Front face on the bed. `bridges` is empty |
| SG90 pilot ligament 1.55 mm | Closed | `END_CLR` 0.2 plus printed pilot Ø1.5 gives about 1.80 mm printed (2.65 − 0.1 − 0.75). Measured 1.60–1.65 in CAD before shrinkage |
| No HOLE_COMP | Closed | `hole_comp=HOLE_COMP` on both cutters |
| 1.55 mm partition at the lightening slot | Closed | The lightening slot was removed |

## Notes

1. The SG90 window ends now have about 0.1 mm of clearance each, and the spec's acceptance step already says to measure the servo first. A body over 22.6 mm long won't go in, so sand the window ends rather than enlarging the pilots' side.
2. The 1.80 mm printed ligament assumes the default 0.2 mm hole shrinkage. Once `hole_comp_mm` is measured, re-check it.

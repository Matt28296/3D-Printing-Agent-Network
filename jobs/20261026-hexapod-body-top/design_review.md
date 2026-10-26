VERDICT: FAIL

# DFM review (round 1): 20261026-hexapod-body-top

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), ../20261026-hexapod-assembly/{hex_frame.py, assembly_plan.md, assembly_check.py, assembly_check.json}, ../20261026-hexapod-body-bottom/model.py, tools/hobby_parts.py, library/lessons.md (no entries). Section probes run on part.stl.
Outputs are current: `build()` gives 36637.67 mm³, the same as geometry.json.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 130 × 104 × 8 mm |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | Underside on the bed. The seat and posts rise from the top (iso.png) |
| 4 | Load paths | PASS | The handling lift through 4 M3 heads bears on the 3 mm deck along the layers. A USB pull goes into the end ledge and rails |
| 5 | Bed contact | PASS | 11270.9 mm² |
| 6 | Overhangs / bridges | **FAIL** (symptom of #11) | mesh_check lists 4 bridges at z 4.0 (span 2.2, length 3.6). These are the PCA9685 posts overhanging the top of the M3 screw holes (the hole cutter ends at z 4, the posts start at z 3) |
| 7 | Walls | PASS (advisory) | Deck 3 mm. Rails 2.5 × 4.1 mm. Posts Ø5.5 with a Ø2.4 pilot = 1.55 mm wall, non-structural (brief) |
| 8 | HOLE_COMP / teardrops | PASS | SCREW_D + HOLE_COMP = Ø3.6 and POST_PILOT + HOLE_COMP = Ø2.4 (geometry.json holes). Seat HALF = 14.85 includes HOLE_COMP/2. No horizontal holes |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(top, 0.0, 0.4)` |
| 10 | Internal corners | PASS (advisory) | The post and rail roots are sharp, under low loads |
| 11 | Fasteners / fits | **FAIL** | **The PCA9685 posts sit on the column screws.** Post centres are at x ±hx/2 = ±28, y ±(PCA_Y ∓ 9.5) = ±25 / ±44. The column screw holes are at SCREWS (±30, ±25), only **2.0 mm** from four of the posts. geometry.json lists both the Ø2.4 hole at (±28, ±25) and the Ø3.6 hole at (±30, ±25). At those four places the post pilot and the screw hole merge. Section y 25: at z 3.5 the only solid is x 25.3–26.8, a crescent of post. At z 6.0 the solid is 25.3–26.8 and 29.25–30.75. top.png shows the eye-shaped merged holes. An M3 head (Ø5.5) at (30, 25) covers x 27.25–32.75 and the post covers 25.25–30.75, so **the top plate cannot be screwed to the columns**, and those posts lose their pilot wall. Also, the PCA9685 board (x ±31.25, y 21.8…47.2) covers all four screws, so even with the posts moved the plate cannot come off with the boards fitted |
| 12 | Critical dims named | PASS | PCA9685_HOLES (56, 19), PCA_Y, POST_*, HALF, LEDGE_H, SCREWS. But SCREWS duplicates the bottom plate's COLUMNS by hand instead of sharing it through hex_frame.py, and that duplication is how this clash got past |
| 13 | Service temperature | PASS | 40 °C against PETG ≈ 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

**Assembly stack, ESP32 jumpers against the LiPo (spec §8 "ESP32 seats with jumpers on every pin"): FAIL.** These heights are in the body frame, tab plane = 0, using assembly_check.py's own dummies:
- Deck underside: T_BODY + COLUMN_H = 34.0.
- PCB underside: 34 + T_TOP 3 + LEDGE_H 2 = 39.0.
- Bottom of the female jumper housings: 39 − 16.5 = **22.5**.
- LiPo top: T_BODY 4 + 18 = **22.0**, and the velcro strap goes over it.

That leaves **0.5 mm**. The LiPo (x ±35, y ±17.5) sits directly under the pin rows (x ±24.1, y ±12.65). Dupont leads leave the housings straight down and need roughly 8–10 mm to bend. The assembly check passes only because it models the housings without leads, with a 1 mm³ tolerance.

Checked and fine:
- ESP32 window: x ±24.8 against 38-pin housings at ±24.13; y ±14.85 against ±13.92 (38-pin) and ±14.12 (30-pin).
- Middle ledge (|y| ≤ 9) clears the inner housing edge at ±11.4.
- Tie slots at y ±18.85…20.65 clear the rails and the boards.
- Cable slots at x ±(46…54) are outside the boards.
- USB end is open to −x.

## Required fixes

1. **Separate the PCA9685 posts from the column screws** (rule §4 fasteners, assembly; evidence: geometry.json holes at (±28, ±25) and (±30, ±25), the 2.0 mm offset, the y 25 section, top.png). Every M3 head (Ø5.5 + 0.5 clearance) must clear every post by ≥ 1 mm and stay outside the board footprints (x ±31.25, |y| 21.8…47.2). One way: move the column pattern to (±40, ±25). From the numbers:
   - The head clears the cable slot by 3.25 mm and the board by 6 mm.
   - On the bottom plate, the column is 1.75 mm from the front coxa servo's inner pilot and 5.6 mm from that servo's body.
   - The LiPo still slides between the columns.

   Move the pattern into hex_frame.py so both plates import it, then rebuild both plates and re-run assembly_check.py.
2. **Leave room for the ESP32 jumper leads** (spec §8; evidence: the 0.5 mm stack above). Either raise COLUMN_H (hex_frame.py) from 30 to ≥ 40 mm, giving ≥ 10 mm for lead bends with the strap in place, or move the LiPo or the ESP32 so they no longer overlap in plan. Add the leads' bend zone (e.g. +10 mm under the housings) to the electronics dummy in assembly_check.py so the check can see this. If the columns get longer, give their roots an r ≥ 1.5 fillet (body-bottom review, item 10).

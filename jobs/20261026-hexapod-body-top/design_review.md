VERDICT: PASS

# DFM review (round 3): 20261026-hexapod-body-top

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26

**Inputs**
- This job: spec.md, design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json, print_requirements.json, slice_plan.json, strength.md (round 1), the round-2 review.
- Renders: all 5, regenerated with `tools/render.py` and viewed.
- Assembly job: assembly_plan.md, hex_frame.py, assembly_check.py (switch dummy 18 × 13 × 24 under the deck), assembly_check.json (`clean: true`), BUILD_GUIDE.md.
- Deep review: 05-hexapod-system.md (SYS-4, SYS-10, SYS-14) and 01-bought-parts.md. Also tools/hobby_parts.py.
- library/lessons.md: no entries.

**Probes:** trimesh `contains` on part.stl, in the body frame with the deck's underside at z 0, at mid-deck height z 1.5.

**Outputs are current.**
- `build()` gives 35302.88 mm³ and a 130 × 104 × 8 bbox from (−65, −52, 0), the same as geometry.json.
- part.stl is one watertight body.
- `tools/mesh_check.py`, re-run in memory, gives exactly the committed mesh_check.json.
- cad_checks.py: 8/8 PASS, exit 0.

**What is new in round 3:**
- screw holes moved with the columns to (±36, ±25);
- 6 lead notches 10 × 5 with r1.5 inner corners, each with a tie slot (SYS-4);
- a Ø12.2 CAD switch hole at (−50, 0) (SYS-10);
- the cable slots now driven by `CABLE_SLOTS`.

All are vertical through-cuts in the 3 mm deck.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits the bed with a 5 mm margin | PASS | 130 × 104 × 8 mm |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, `watertight: true`, `min_z_mm: 0.0`. part.stl is 1 body |
| 3 | Orientation matches the brief | PASS | The underside is on the bed. The ESP32 seat, rails and PCA9685 posts rise from the top (iso.png, right.png) |
| 4 | Load paths | PASS | Deck bending runs along the layers. The posts and rails stand across the layers under low loads, as in round 2 |
| 5 | Bed contact | PASS | 10843.0 mm² |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | `overhang_pct` 0.0, `bridges: []`. The notches, tie slots, switch hole and screw holes are vertical through-cuts (top.png, bottom.png) |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (advisory) | Deck 3, rails 2.5. Post wall 1.55 (Ø5.5 post, Ø2.4 pilot: z 5 row 25.25–26.8), non-structural as in round 2. Switch hole to the rear edge 8.9 (y 0 row: void −56.1…−43.9) and to the cable slots 7.9 (x −50 column: void −6.1…6.1, slots from ±14). Screw hole to the nearest post 3.45 (y 25 row: hole −37.8…−34.2, post to −30.75). Tie slot to its notch 1.8 (y 49.5 row, e.g. −35.0…−33.2). **Tie slot to the deck edge: 1.5 mm CAD** (columns at x −31.5, 8.5, 31.5: void 48.5–50.5, edge 52.0). That is under 1.8 but above 0.9, on a lead-tie anchor with no load case in spec §4 |
| 8 | HOLE_COMP; horizontal holes | PASS | Screw holes Ø3.6 = `SCREW_D` 3.4 + 0.2. Post pilots Ø2.4 = 2.2 + 0.2. Switch Ø12.2 = `SWITCH_D` 12.0 + 0.2 (geometry.json holes, cad_checks). Tie slots 3.4 × 2.0. ESP32 pocket 29.7 = 2 × `HALF`. No horizontal holes |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(top, 0.0, 0.4)` (model.py:78), on the blank before the cuts |
| 10 | Internal corners on load paths filleted | PASS (advisory) | The new notches have r1.5 inner corners (y 47.2 row: void −44.25…−35.75, opening to the full 10 mm from y 48.5). The cable slots, tie slots and post and rail roots are square, as in round 2. Loads there are low, and strength carries the slots at Kt 2.5 |
| 11 | Fasteners per §4 | PASS | 4 × M3 × 8 self-tapping through Ø3.6 into the column pilots, 5 mm engaged. The heads (Ø6) are 1.75 mm clear of the PCA9685 boards (x ±31.25; cad_checks, spec §8 ≥ 1.75), so the deck comes off with the boards fitted. 8 × M2.5 × 6 self-tapping into the Ø2.4 post pilots. The switch's 12 mm bushing goes through Ø12.0 printed in a 3 mm deck |
| 12 | Spec §3 dimensions are named parameters | PASS (advisory) | `SCREWS = COLUMNS` (model.py:32 → hex_frame.py:76, commented). `PCA9685_HOLES` 56 × 19 (hobby_parts). ESP32 pocket 2 × `HALF` (:39). `SWITCH_D` 12.0 (:49, commented). `SCREW_D` 3.4 (:33) has no comment; the brief's table gives its source ("M3 clearance", default), as accepted in rounds 1 and 2 |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG ≈ 70 °C. Before slicing: `materials_on_hand` in config/printer.json is empty |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

## Required fixes

None.

## Round 2 recommendations checked

There were no required fixes in round 2.
- **`CABLE_SLOTS` unused:** done. `CABLE_SLOTS` / `CABLE_SLOT_SIZE` (model.py:43–44) drive the cuts (slots at x ±46…±54, y ±14…±30).
- **UBEC text:** done. Spec §1, the brief and the model docstring say it stands on the bottom plate.
- **ESP32 pocket label:** done. Spec §3 says "29.5 printed (29.7 CAD)".
- **Velcro strap:** still not modelled in assembly_check.py, and `COLUMN_H` is still 40. The jumper bend room over the LiPo is still 10.5 mm: housings at 34.5, LiPo top at 24, above the plate underside. A ≈ 1.5 mm strap leaves ≈ 9 mm. Advisory, as before.

## Recommendations (not blocking)

1. **USB plug against the switch (design-lead or the electronics owner, before printing).**
   - The switch hole (x −56.1…−43.9) sits on the ESP32's USB axis (y 0), 16.1 mm behind the board's USB end (x −27.2).
   - The toggle's bushing, nut and lever stand on the deck top there.
   - A straight micro-USB plug with its overmould is typically 18–25 mm long at about 2–9 mm above the deck top, so it is likely to hit them.
   - Spec §8 step 3 plugs USB 5 times.
   - Check with the real cable and switch. If they clash, move the switch off the y 0 line, or use a right-angle cable.
   - This is not a printability item, so it doesn't affect the verdict.
2. **Strength re-check of two sections round 3 narrowed.**
   - **x −50:** the switch hole sits in the rear cable slots' section. Net width there is 59.8 mm (22 + 7.9 + 7.9 + 22), against 72 at x ±46, which the brief calls the lowest handling section.
   - **x 0:** the middle notches take this section from 70.7 mm (round 2) to 60.7 mm. It also loses the ESP32 window and the two zip-tie slots. The brief's "the notch at x 0 leaves 94 mm" leaves out the window.
3. **Tie slots:** move them 0.5 mm inward (`yt` ±49.0) for a 2.0 mm edge ligament. This is optional.
4. **Switch fit:** Ø12.0 printed is line-to-line for an M12 bushing. Consider `SWITCH_D` 12.3, or plan to ream. If the chosen toggle has an anti-rotation tab, add its key slot.
5. **`SCREW_D`:** add a one-line source comment.

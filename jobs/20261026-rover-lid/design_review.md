VERDICT: PASS

# DFM review, round 3: 20261026-rover-lid

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, cad_checks.py, renders/{iso,front,right,top,bottom}.png (regenerated with tools/render.py), print_requirements.json, slice_plan.json, round-2 design_review.md and strength.md, rover_frame.py (LID_SCREWS), chassis model.py (insert columns), tools/hobby_parts.py (ESP32 boards, breadboard), assembly_check.json, BUILD_GUIDE.md (steps 2 and 11, Service). The library is empty, so the defaults apply (HOLE_COMP +0.2).

Outputs are current: a fresh in-memory `build()` gives 31 376.89 mm³ and 154 × 76 × 7.1, identical to geometry.json. `mesh_check.check()` re-run in memory is identical to mesh_check.json. `cad_checks.py`: all 9 checks pass. Extra evidence: a layer-by-layer support analysis of part.stl (0.1 mm grid, 0.2 mm layers).

Round 3 changed three things on the lid:
- the screw holes moved onto the chassis's new heat-set-insert columns (the inserts are in the chassis job);
- the MTS-102 toggle hole is new;
- two cable slots with a tie bar replace the Ø10 cable hole.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 154.0 × 76.0 × 7.1, fits_bed true |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight true, min_z 0.0 |
| 3 | Orientation | PASS | Flat, underside down, the seat rising from the top (iso.png, front.png, right.png) |
| 4 | Load paths vs layers | PASS | Deck bending is in the layer plane. The rail roots bend across the layers under a sideways jumper pull (strength round 2: lowest SF 3.27). The toggle's bushing nuts clamp the deck through its thickness |
| 5 | Bed contact | PASS | 9 756.8 mm². A 3 mm PETG plate has a low warp risk; use a glue release layer on smooth PEI (preflight) |
| 6 | Overhangs, bridges | PASS | overhang_pct 0, no bridges. Layer analysis: no unsupported cell in any layer. The window, slots and holes are all vertical through-cuts |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | T 3.0, RAIL_W 2.5, END_LEDGE 2.4. The tie bar is 2.8 wide in CAD (\|y\| ≤ 1.4; cad_checks) and 3.0 thick. Each screw hole is 3.7 from the side edge and the corner arc (centre at \|y\| 32.5, r 1.8; it was 2.2 in round 2). The toggle hole is ≥ 11.8 from any edge. thin_wall_warnings empty |
| 8 | HOLE_COMP, teardrops | PASS | Screw holes 3.4 + 0.2 = Ø3.6 (l.80); toggle 6.2 + 0.2 = Ø6.4 (l.82; geometry.json). Cable slots get +0.1 per edge (l.85). The ESP32 pocket's HALF includes HOLE_COMP/2 (l.38). No horizontal holes |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(lid, z0, 0.4)` (l.60); bottom.png shows the bevel. The through-cuts are clearance features |
| 10 | Internal corners on load paths | PASS (note) | The cable-slot corners are r2 (l.87). The ESP32 window's corners are still sharp, but the deck rests on the whole wall rim, so stress there is low (round-2 R2, still open: R2 below) |
| 11 | Fasteners (§4) | PASS (note) | 4 × M3 × 8 go through Ø3.6 holes into M3 × 5.7 heat-set inserts in the chassis's Ø10 columns: metal threads, fine for the lid coming off at every charge (§4; this was round-2 R3). Engagement is 8 − 3 = 5 mm of the 5.7 mm insert, and the tip stops 1.5 mm above the bottom of the 6.5 mm hole. No washers are listed under the heads (R3) |
| 12 | Spec §3 dims are named parameters | PASS | Each spec §3 dimension is a named, commented parameter, and cad_checks proves each: 2·HALF = 2·(28.3/2 + 0.6 + 0.1) = 29.7 (pocket width); SCREW_D 3.4; SWITCH_D 6.2; CABLE_X (71, 81) and CABLE_Y (1.5, 12) give the 10 × 10.5 slots |
| 13 | Service temp | PASS | 40 °C against ≈ 70 °C for PETG |
| 14 | Lessons | N/A | None recorded |
| 15 | FreeCAD reference | N/A | None |
| 16 | Fits and assembly (cross-part) | PASS | SCREWS = rover_frame.LID_SCREWS = the chassis COLUMNS, (−13, ±32.5) and (102, ±32.5), so the holes can't drift from the inserts (cad_checks). The toggle at (0, −23) hangs over the right-hand motor with 0 collisions; its tie head goes beside the can (BUILD_GUIDE step 5). The slots clear the ESP32 seat (ends at x 14 + 54.4 + 0.6 = 69.0) and the breadboard (from x 84). The ESP32 ties still cross the board 1.2 mm from its pin-free ends |

## Required fixes

None.

## Round 2 fixes checked

Round 2 passed with no required fixes. Its recommendations:
- **R1 (USB-end tie on EN/BOOT): still applies** (R1 below).
- **R2 (round the window corners r ≥ 2): not done** (R2 below).
- **R3 (heat-set inserts): done.** They are in the chassis columns, Ø4.0 × 6.5 holes in Ø10 columns, and the lid takes M3 × 8 machine screws.

## Printing notes vs print_requirements.json

The brief's only printing note is "flat, underside on the bed". print_requirements.json asks for 3 perimeters, 5 top and 5 bottom layers, 20 % gyroid, and PETG at 230–250 °C nozzle and 80–90 °C bed, within 5 h. These are consistent with the brief, and slice_plan.json matches them.

## Recommendations (not blocking)

- **R1.** On your actual board, check that the USB-end tie (1.2 mm from the end, over the micro-USB socket) doesn't press EN or BOOT. A tie pressing EN holds the ESP32 in reset; if it does, use a small printed clip at that end instead.
- **R2.** Round the window's internal corners to r ≥ 2 mm. It costs nothing, and the cable slots already have r2.
- **R3.** The lid comes off at every charge, and the screw heads bear straight on PETG. Add an M3 washer (ISO 7089) under each lid-screw head, as §4 asks for plastic under clamping load. That means 4 more washers in the BOM, and an M3 × 8 still engages 4.5 mm of the insert.

VERDICT: PASS

# DFM review, round 2: 20261026-rover-lid

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/{iso,top,front,right,bottom}.png, print_requirements.json, rover_frame.py, tools/hobby_parts.py (ESP32 boards, breadboard), assembly_check.py (ESP32 header and jumper dummy), chassis model.py (COLUMNS), round-1 design_review.md and strength.md. The library is empty, so the defaults apply.
Outputs are current: a fresh in-memory `build()` gives 31 862.50 mm³ and 154 × 76 × 7.1, identical to geometry.json. Also read: assembly BUILD_GUIDE.md; its step 8 (two small ties through the end slots, never across the pin rows) matches the model.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 154.0 × 76.0 × 7.1, fits_bed true |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight true, min_z 0 |
| 3 | Orientation | PASS | Flat, underside down, seat rising from the top (iso.png, front.png, right.png) |
| 4 | Load paths vs layers | PASS | Deck bending is in the layer plane. The rail roots bend across the layers under a sideways jumper pull; strength round 1 gave SF 3.27 there (OK) |
| 5 | Bed contact | PASS | 9 919 mm². A 3 mm PETG plate has a low warp risk. Use a glue release layer on smooth PEI (preflight) |
| 6 | Overhangs, bridges | PASS | overhang_pct 0, no bridges. The window, tie slots and holes are vertical through-cuts |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | T 3.0, RAIL_W 2.5, END_LEDGE 2.4. From the screw hole at (−13, ±30) to the corner fillet arc: 6 − 2.0 − 1.8 = 2.2 mm |
| 8 | HOLE_COMP, teardrops | PASS | Screws 3.4 + 0.2 = Ø3.6, cable hole Ø10.2 (geometry.json). The ESP32 pocket HALF includes HOLE_COMP/2. There are no horizontal holes |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(lid, z0, 0.4)` l.51; the bevel shows in bottom.png |
| 10 | Internal corners on load paths | PASS (note) | The window corners are sharp, but the deck sits on the whole 4.5 mm wall rim, so stress there is low (R2) |
| 11 | Fasteners | PASS (note) | 4 × M3 × 10 self-tappers go through Ø3.6 holes into the chassis Ø2.6 pilots, about 7 mm of engagement. SCREWS = chassis COLUMNS: (−13, ±30) and (100, ±30). Repeated removal: see chassis R1 |
| 12 | Spec §3 dims are named parameters | PASS | 2·HALF = 2·(28.3/2 + 0.6 + 0.1) = 29.7 (spec 29.7); SCREW_D 3.4 |
| 13 | Service temp | PASS | 40 °C against about 70 °C for PETG |
| 14 | Lessons | N/A | None recorded |
| 15 | FreeCAD reference | N/A | None |
| 16 | Fits and assembly (cross-part) | PASS | The ties now cross the board 1.2 mm from its pin-free ends (TIE_FROM_END), at x 15.2 (USB end), 67.2 (38-pin far end) and 64.3 (30-pin far end), through 3.2 × 1.8 slots at \|y\| 18.85–20.65 (top.png, bottom.png). For the 38-pin board, a 2.5 mm tie runs under the deck at x 13.95–16.45 and 65.95–68.45: solid deck beside the window (x 16.4–66.0), at least 0.6 mm from the header and jumper housings (x 17.07–65.33 in the assembly_check dummy). The 30-pin far tie passes under the tongue. Jumpers stay changeable without cutting a tie, and the screw holes match the round-2 chassis columns |

## Required fixes

None.

## Round 1 fixes checked

1. Hold the ESP32 without enclosing the window: **done.** The ties moved to the board ends (TIE_FROM_END 1.2), so the tie loops no longer wrap the jumper housings (item 16).
2. Round-1 R2, keep SCREWS on the chassis columns: **done.** SCREWS equals the round-2 COLUMNS list.

## Recommendations (not blocking)

- R1. On your actual board, check that the USB-end tie (1.2 mm from the end, over the micro-USB socket) doesn't press EN or BOOT. On DevKitC and DOIT boards those buttons sit beside the socket at that end, and a tie pressing EN holds the ESP32 in reset. If it does press them, use a small printed clip at that end instead of the tie.
- R2. Round the window's internal corners to r ≥ 2 mm (round-1 R1; it costs nothing).
- R3. If the lid will come off often (for battery charging and idler re-tensioning), put heat-set inserts in the chassis columns (chassis R1).

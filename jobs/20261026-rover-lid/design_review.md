VERDICT: FAIL

# DFM review: 20261026-rover-lid

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png, rover_frame.py, hobby_parts.py (ESP32 boards, breadboard), assembly_check.py (ESP32 header and jumper dummy), chassis model.py (COLUMNS). The library is empty, so the defaults apply.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit | PASS | 154.0 × 76.0 × 7.1 |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight, min_z 0 |
| 3 | Orientation | PASS | Flat, underside down, seat rising from the top (iso.png) |
| 4 | Load paths vs layers | PASS | Deck bending is in the layer plane |
| 5 | Bed contact | PASS | 9 941 mm². A PETG plate 3 mm thick on PEI is a low warp risk |
| 6 | Overhangs, bridges | PASS | overhang_pct 0, no bridges. The window and tie slots are vertical through-cuts |
| 7 | Walls | PASS | T 3.0, RAIL_W 2.5, END_LEDGE 2.4. Screw hole to the corner fillet is 6 − 2.12 − 1.8 = 2.08 mm |
| 8 | HOLE_COMP, teardrops | PASS | Screws 3.4 + 0.2 = 3.6 and cable hole 10.2 (geometry.json). The ESP32 pocket HALF includes HOLE_COMP/2. No horizontal holes |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(lid, z0, 0.4)` l.50 |
| 10 | Internal corners | PASS (note) | The 49.6 × 29.7 window has sharp corners. The deck rests on the whole chassis wall rim, so bending stress under the 20 N press is low. See R1 |
| 11 | Fasteners | PASS (note) | M3×10 self-tappers through Ø3.6 into the chassis Ø2.6 pilots (12 deep), about 7 mm of engagement. SCREWS = chassis COLUMNS. See chassis R3 on repeated opening |
| 12 | Spec §3 dims | PASS | 2·HALF = 2·(28.3/2 + 0.6 + 0.1) = 29.7 (spec 29.7); SCREW_D 3.4 |
| 13 | Temperature | PASS | 40 vs about 70 °C |
| 14 | Lessons | N/A | None |
| 15 | FreeCAD reference | N/A | None |
| 16 | Assembles (cross-part) | **FAIL** | The ESP32 zip tie cannot close without crossing the jumper zone, as detailed below |

Detail for 16: the TIE_SLOTs sit at x = 39.75 (xm), |y| 18.85 to 20.65. A tie loop over the board and down through both slots must pass under the deck from one slot to the other. At that x the deck has the window (|y| ≤ 14.85, x 16.4 to 66.0), and the pin-header rows with female jumper housings hang through it at |y| 11.4 to 13.9, down to Z 37.2 (the dummy in assembly_check.py: 16.5 mm below the PCB). The loop would therefore wrap under and around the jumper housings and wires. Spec §8 asks for "jumpers on every pin", and those jumpers could no longer be changed without cutting the tie.

## Required fixes

1. **Retain the ESP32 without enclosing the window.** Options:
   - (a) Snap lips: add about 0.6 mm inward lips on the side rails (the rail top is already ztop + 1.6 + 0.5, so 0.5 mm above the PCB top), with the rails as the flex members.
   - (b) Move the tie to an x where the deck is solid across the full board width. The only band that covers both boards is the USB-end ledge (x 13.4 to 16.4), and it also crosses the USB connector, so (a) is preferred.
   Keep the 30-pin and 38-pin support as it is now (USB ledge, far ledge, tongue).

## Recommendations (not blocking)

- R1. Round the window's internal corners r ≥ 2 mm (rule §2). This costs nothing: the header rows end 0.67 mm from the ledges along x but sit well inside the corners.
- R2. If the chassis front columns are shortened to clear the idler bolt (chassis fix 2), keep the column axes at (127.5, ±30.5) so SCREWS stays valid.

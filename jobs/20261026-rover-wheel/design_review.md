VERDICT: FAIL

# DFM review, round 2: 20261026-rover-wheel

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/{iso,top,front,right,bottom}.png, print_requirements.json, chassis model.py (boss, nut trap), rover_frame.py, assembly_check.json, round-1 design_review.md and strength.md. The library is empty, so the defaults apply.
Outputs are current: a fresh in-memory `build()` gives 18 125.49 mm³ and 32.201 × 32.201 × 32.5, identical to geometry.json. Also read: assembly BUILD_GUIDE.md (step 4: washer, wheel, washer, nyloc). The fix below was tried in a scratch copy: `chamfer_bottom(build(), 0.4)` gives one valid solid.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 32.2 × 32.2 × 32.5 |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight true, min_z 0 |
| 3 | Orientation | PASS | Outer flange down, hub up, as the brief says (iso.png, front.png) |
| 4 | Load paths vs layers | PASS (note) | The radial rim load goes to the bore in the layer plane. The 3 N skid-steer load bends the upper flange's root across the layers, but the load is tiny (strength round 1: SF 127) |
| 5 | Bed contact | PASS | 803 mm² |
| 6 | Overhangs, bridges | PASS | The upper V-cone is exactly 45° (CONE_RISE 3 over 3). overhang_pct 0, no bridges |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | A solid body, with 5 perimeters required (print_requirements.json). The flange band is 0.7 mm tall at r 16.1, backed by solid material |
| 8 | HOLE_COMP, teardrops | PASS | BORE 3.5 + 0.2 = Ø3.7 CAD, vertical (geometry.json: hole 3.7, axis Z) |
| 9 | Bottom edges chamfered | **FAIL** | `build()` (l.44–45) only flips and beds the part; it adds no chamfer. bottom.png shows a plain disc and bore with no bevel, unlike the sprocket's and idler's bottom.png; front.png shows a square bed edge on the flange. Round-1 fix 3 was not done |
| 10 | Internal corners on load paths | PASS | The rim-to-cone corners are 135°; there is no sharp re-entrant corner on the load path |
| 11 | Fasteners | PASS | M3 × 45 from the boss face (y 32) ends at y 77. The wheel ends at y 71.0, and a washer + nyloc need 75.5, leaving 1.5 mm of thread past the nyloc |
| 12 | Spec §3 dims are named parameters | PASS | RIM_R = STRAIGHT_IN − 0.08 = 13.10. BORE 3.5 printed (Ø3.7 CAD) matches spec §3. RIM_HALF 12.3 leaves 0.3 mm side clearance to the 24 mm track |
| 13 | Service temp | PASS | 40 °C against about 70 °C for PETG |
| 14 | Lessons | N/A | None recorded |
| 15 | FreeCAD reference | N/A | None |
| 16 | Fits and assembly (cross-part) | PASS | The bore has 0.5 mm diametral clearance on M3, the §3 free-running fit. The hub end (y 38.5) sits on the washer over the flush wall nut |

## Required fixes

1. **Chamfer the bed face (rule §2 bottom edges, §6 elephant's foot).** Put a 0.4 mm 45° chamfer on every bed-plane edge, i.e. the outer flange edge at r 16.1 and the bore edge: for example, `chamfer_bottom(part, 0.4)` from cadlib after the flip in `build()`. Also add `elefant_foot_compensation` ≥ 0.2 to the "min" block of print_requirements.json, as the links have. Without it, the first layer flares the flange and narrows the running bore at that end. Evidence: item 9.

## Round 1 fixes checked

1. Running bore: **done.** BORE went from 3.2 to 3.5 printed (Ø3.7 CAD in geometry.json), and spec §3 was updated.
2. Bolt length: **done.** M3 × 45 is in spec §2; it ends 1.5 mm past the nyloc (item 11).
3. Bed-face chamfer: **not done** (fix 1).

## Recommendations (not blocking)

- R1. The wheel is fully solid (18.1 cm³ × 4). A hub, web and rim design would save material and print time (round-1 R1).
- R2. The bore runs on bolt threads over 32.5 mm. A plain-shank bolt or a brass sleeve would wear better.
- R3. slice_plan.json still overrides perimeters to 3, below the print_requirements minimum of 5 set in round 2. The slicing-lead should update it before SLICE.

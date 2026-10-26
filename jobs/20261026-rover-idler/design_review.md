VERDICT: PASS

# DFM review, round 3: 20261026-rover-idler

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py (it runs the sprocket's model.py with BORE = "round"), the sprocket's model.py, geometry.json, mesh_check.json, cad_checks.py, renders/{iso,front,right,top,bottom}.png (regenerated with tools/render.py), print_requirements.json, slice_plan.json, round-2 design_review.md and strength.md, chassis model.py (slot, nut slot, jack screw), rover_frame.py, assembly_check.json, BUILD_GUIDE.md (steps 3, 4, 7, 8). The library is empty, so the defaults apply (HOLE_COMP +0.2).

Outputs are current: a fresh in-memory `build()` gives 4 853.17 mm³ and 35.777 × 34.52 × 20.0, identical to geometry.json. `mesh_check.check()` re-run in memory is identical to mesh_check.json. `cad_checks.py`: all 5 checks pass. The only geometric change since round 2 is the shared tooth-root chamfer (4 858.19 → 4 853.17 mm³). Extra evidence: a layer-by-layer support analysis of part.stl (0.1 mm grid, 0.2 mm layers).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 35.8 × 34.5 × 20.0; two per plate |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight true, min_z 0.0 |
| 3 | Orientation | PASS | Disc down, hub up, as the brief says (iso.png, front.png); `Rot(180, 0, 0)` in `build()` (l.34) |
| 4 | Load paths vs layers | PASS | Bore bearing and tooth bending lie in the layer plane. The bore runs the full 20 mm on the bolt, so the hub doesn't act as a cantilever |
| 5 | Bed contact | PASS | 514.9 mm² |
| 6 | Overhangs, bridges | PASS | overhang_pct 0, no bridges. Layer analysis: no unsupported cell in any layer |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | Hub: (10 − 3.7)/2 = 3.15. Teeth as on the sprocket: 2.7 at the root plus the chamfers, an unloaded 1.6 tip. thin_wall_warnings empty |
| 8 | HOLE_COMP, teardrops | PASS | ROUND_BORE 3.5 + HOLE_COMP 0.2 = Ø3.7 CAD, a vertical through-bore (sprocket model.py l.92; geometry.json: hole 3.7, axis Z). No horizontal holes |
| 9 | Bottom edges chamfered | PASS | The 0.3 mm bed chamfer comes from the sprocket model (l.84 there); bottom.png shows the bevel round the disc and teeth. The bore is cut afterwards; `elefant_foot_compensation` 0.2 is now in "min" (round-2 R1) |
| 10 | Internal corners on load paths | PASS (note) | The tooth-root chamfers now start on the disc circle (sprocket l.56). The hub-to-disc corner is sharp, but the bore carries the load along its full length, so that corner is not on a bending path |
| 11 | Fasteners | PASS | The idler runs on an M3 × 40, class 12.9, fully threaded. Its stack: head on a DIN 9021 washer (\|y\| 27.2–28.0), sliding slot nut, washer, idler (38.5–58.5), washer, nyloc (59.0–63.0). The tip is at 67.2, 4.2 mm past the nyloc (assembly_check.json). The chassis jack screw stops the bolt positively, so no preload is relied on (§4) |
| 12 | Spec §3 dims are named parameters | PASS | ROUND_BORE 3.5 (l.18, commented) with HOLE_COMP gives the spec's Ø3.5 printed / Ø3.7 CAD. Pitch radius RP 16.18 comes from rover_frame. cad_checks proves both |
| 13 | Service temp | PASS | 40 °C against ≈ 70 °C for PETG |
| 14 | Lessons | N/A | None recorded |
| 15 | FreeCAD reference | N/A | None |
| 16 | Fits and assembly (cross-part) | PASS | The bore has 0.5 mm of diametral clearance on M3, a §3 free-running fit; the nyloc sets the end play (spec §8: < 0.5 mm). assembly_check.json: idler and jack screw clear at both slot ends; 7 teeth in link notches on each idler; 0 collisions with no exemptions |

## Required fixes

None.

## Round 2 fixes checked

Round 2 passed with no required fixes. Its recommendations:
- **R1 (EFC): done.** `elefant_foot_compensation` 0.2 is in the "min" block of print_requirements.json.
- **R2 (keep sprocket changes out of the idler): done.** `design()` sets BORE "round" and restores the sprocket model's setting afterwards (l.21–27). The round-3 hub, slots and centre hole stay in the sprocket's own branch: cad_checks finds no slot and the hub solid at r 6.35.
- **R3 (bore runs on threads): unchanged.** The brief keeps it as a risk; the bolt is now fully threaded.

## Printing notes vs print_requirements.json

The brief's printing notes:
- outer disc face on the bed, hub up;
- `elefant_foot_compensation` 0.2 is now required.

print_requirements.json matches: 4 perimeters, 5 top and 5 bottom layers, 50 % gyroid, EFC 0.2 in "min", PETG at 230–250 °C nozzle and 80–90 °C bed, ≤ 2 h. slice_plan.json matches the requirements, with 2 copies.

## Recommendations (not blocking)

- **R1.** This job builds from the sprocket's model.py. Rebuild and re-render it after any sprocket change, and re-run its cad_checks.py.

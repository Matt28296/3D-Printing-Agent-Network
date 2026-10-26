VERDICT: PASS

# DFM review, round 3: 20261026-rover-track-link

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, cad_checks.py, renders/{iso,front,right,top,bottom}.png (regenerated with tools/render.py), print_requirements.json, slice_plan.json, round-2 design_review.md and strength.md, rover_frame.py, wheel and sprocket model.py, assembly_check.json, BUILD_GUIDE.md (BOM, "Before you start", step 1). The library is empty, so the defaults apply (HOLE_COMP +0.2).

Outputs are current: a fresh in-memory `build()` gives 1 029.73 mm³ and 16 × 24 × 7.5, identical to geometry.json. `mesh_check.check()` re-run in memory is identical to mesh_check.json. `cad_checks.py`: all 7 checks pass. Extra evidence: a layer-by-layer support analysis of part.stl (0.05 mm grid, 0.2 mm layers).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 16.0 × 24.0 × 7.5. 36 per plate fit (6 × 6 at a 19 × 27 pitch = 114 × 162 mm) |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight true, min_z 0.0 |
| 3 | Orientation | PASS | Inner face down, grousers up, as the brief says (front.png, right.png, iso.png) |
| 4 | Load paths vs layers | PASS (justified) | Track tension loads the knuckles in the layer plane. The brief notes that the tear-out shear planes cross the layers (strength round 1) |
| 5 | Bed contact | PASS (note) | 122.8 mm² per link, one connected footprint (bottom.png). PETG on smooth PEI needs a release layer (preflight) |
| 6 | Overhangs, bridges | PASS (justified) | overhang_pct 2.34 (25.6 mm²): the knuckle undersides within 0.8 mm of their tangent line on the bed. The layer analysis shows them ≤ 0.35 mm past the 45° allowance at z 0.3–0.7, every one attached; the brief notes the tangent knuckles. The only "bridges" are 0.04 mm slivers at z 5.99. Unchanged since round 2 |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (note) | The running-hole wall is 3.0 − 1.25 = 1.75, 0.05 under the nominal 1.8. It still takes the four perimeters §2 asks for: 0.45 + 3 × 0.41 = 1.68 at PrusaSlicer's spacing (cad_checks). Spec §3 lists 1.75 as the minimum, and this is the value round-2 fix 1 prescribed. Above the teardrop tip: 3.0 − 1.77 = 1.23, which is ≥ 0.9. Round the grip holes: 3.0 − 1.1 = 1.9. Notch side strips: 2.75. thin_wall_warnings empty |
| 8 | HOLE_COMP, teardrops | PASS | Running hole 2.0 + 0.3 + 0.2 = Ø2.5 CAD; grip holes 2.0 + 0 + 0.2 = Ø2.2 (l.67–68; geometry.json). Both are teardrops pointing up in print (arc 270°, front.png) |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(link, t, 0.3)` (l.62) bevels the box edges, including the faces bounding the 0.5 mm knuckle gaps (bottom.png). The tangent knuckle lines are skipped. `elefant_foot_compensation` 0.2 is in "min" |
| 10 | Internal corners on load paths | PASS (note) | The box steps at the notch and bridge are sharp; strength round 1 found low stress in the 2.75 × 6 strips. Unchanged |
| 11 | Fasteners | PASS | The outer knuckles grip the Ø2 pin at Ø2.0 printed (§3 press fit 0–0.1); it runs in the centre knuckle at about Ø2.3. ISO 2338 / 8734 m6 dowels (Ø2.002–2.008) leave 0.29 mm. The pin ends sit 2.4 mm from the wheel flange cones (deep review 04, S-23) |
| 12 | Spec §3 dims are named parameters | PASS | P 10 (rover_frame); PIN_RUN_CLR 0.3 (l.25), PIN_GRIP_CLR 0, HOLE_COMP; KN_GAP 0.4 and the 0.5 axial gap. Spec §3 now reads "Ø2.3 printed (Ø2.5 CAD), sliding fit", with a 1.75 mm wall minimum, matching the model |
| 13 | Service temp | PASS | 40 °C against ≈ 70 °C for PETG |
| 14 | Lessons | N/A | None recorded |
| 15 | FreeCAD reference | N/A | None |
| 16 | Fits and assembly (cross-part) | PASS | The centre knuckle now has 0.3 mm of diametral clearance on the Ø2 pin, the §3 sliding-fit range (0.3–0.4) that round 2 required. Flexing to 40° both ways: the next link's body starts 3.4 mm from the hinge axis (corners at r 4.53), so it doesn't reach this link's outer box until 48.6°. assembly_check.json: 7 teeth seated in link notches on every sprocket and idler |

## Required fixes

None.

## Round 2 fixes checked

1. **Open the running hole to a sliding fit: done.**
   - PIN_RUN_CLR went from 0.2 to 0.3 (l.25): Ø2.5 CAD, about Ø2.3 printed, 0.3 mm of clearance on the Ø2 pin.
   - Spec §3 and the brief were updated, wall cost included (1.75 and 1.23).
   - Strength round 3 should still re-check knuckle bearing and tear-out at the larger hole, as round 2 asked.

Round-2 recommendations:
- R1 (5-link test chain): now in spec §8 and BUILD_GUIDE "Before you start".
- R2 (notch bed edges): unchanged; EFC 0.2 covers it.
- R3 (34 islands per plate): left to the slicer-engineer.

## Printing notes vs print_requirements.json

The brief's printing notes:
- inner face on the bed;
- 34 per plate;
- 0.3 bed chamfer plus slicer EFC 0.2.

print_requirements.json asks for:
- 4 perimeters;
- 5 top and 5 bottom layers;
- 40 % gyroid;
- `elefant_foot_compensation` 0.2;
- PETG at 230–250 °C nozzle, 80–90 °C bed;
- ≤ 7 h.

These are consistent with the brief: 4 perimeters is the four lines the 1.75 mm wall is sized for. slice_plan.json matches the requirements.

## Note for slicing (not a DFM item)

Spec §7 asks for 68 links + 2 spares, "two plates of 34, plus 2 on either plate". slice_plan.json has `copies` 34, so one of the two plates needs 36. That still fits the bed (item 1).

## Recommendations (not blocking)

- **R1.** Print the spec §8 five-link chain from the first plate and run its pressing, tension and hinge-crush tests before printing the second plate. That is the only check of the 0.3 mm running fit and of the outer-knuckle grip on your pins.

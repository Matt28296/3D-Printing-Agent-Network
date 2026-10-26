VERDICT: PASS

# DFM review, round 3: 20261026-rover-wheel

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, cad_checks.py, renders/{iso,front,right,top,bottom}.png (regenerated with tools/render.py), print_requirements.json, slice_plan.json, round-2 design_review.md and strength.md, chassis model.py (boss, nut trap), rover_frame.py, assembly_check.json, BUILD_GUIDE.md (step 7). The library is empty, so the defaults apply (HOLE_COMP +0.2).

Outputs are current: a fresh in-memory `build()` gives 18 116.47 mm³ and 32.201 × 32.201 × 32.5, identical to geometry.json. `mesh_check.check()` re-run in memory is identical to mesh_check.json. `cad_checks.py`: all 6 checks pass. Extra evidence: a layer-by-layer support analysis of part.stl (0.1 mm grid, 0.2 mm layers).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 32.2 × 32.2 × 32.5; four per plate (slice_plan copies 4) |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight true, min_z 0.0 |
| 3 | Orientation | PASS | Outer flange on the bed, hub up, as the brief says (front.png, iso.png) |
| 4 | Load paths vs layers | PASS (note) | The radial rim load reaches the bore in the layer plane. The 3 N skid-steer load bends the upper flange's root across the layers, but that load is tiny (strength round 1: SF 127) |
| 5 | Bed contact | PASS | 758.2 mm² (mesh_check; 803 before the chamfer) |
| 6 | Overhangs, bridges | PASS | The upper V-cone is exactly 45° (CONE_RISE 3 over 3). overhang_pct 0, no bridges. Layer analysis: no unsupported cell in any layer |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | A solid body printed with 5 perimeters (print_requirements). The 0.7 mm flange band at r 16.1 is backed by solid material. thin_wall_warnings empty |
| 8 | HOLE_COMP, teardrops | PASS | BORE 3.5 + 0.2 = Ø3.7 CAD, vertical (l.44; geometry.json: hole 3.7, axis Z) |
| 9 | Bottom edges chamfered | PASS | `chamfer_bottom(..., 0.4)` after the flip (l.49) chamfers the outer flange edge and the bore mouth (cad_checks: both 0.4 × 45° chamfers). bottom.png shows the bevel ring at the rim and round the bore; front.png shows the chamfered bed edge. `elefant_foot_compensation` 0.2 is in "min" |
| 10 | Internal corners on load paths | PASS | The rim-to-cone corners are 135°; there is no sharp re-entrant corner on the load path |
| 11 | Fasteners | PASS | The wheel runs on an M3 × 50, class 12.9, fully threaded. The head sits on an ISO 7089 washer at \|y\| 27.5 and the wall nut is engaged. Then the wheel (38.5–71.0), a washer and a nyloc (71.5–75.5). The tip is at 77.5, 2.0 mm past the nyloc (assembly_check.json) |
| 12 | Spec §3 dims are named parameters | PASS | RIM_R = STRAIGHT_IN − 0.08 = 13.10; BORE 3.5 printed (Ø3.7 CAD); BED_CHAMFER 0.4 (l.33). All match spec §3, are commented, and are proved by cad_checks |
| 13 | Service temp | PASS | 40 °C against ≈ 70 °C for PETG |
| 14 | Lessons | N/A | None recorded |
| 15 | FreeCAD reference | N/A | None |
| 16 | Fits and assembly (cross-part) | PASS | The bore has 0.5 mm of diametral clearance on M3, a §3 free-running fit. RIM_HALF 12.3 gives 0.3 mm side clearance to the 24 mm track. The hub end (y 38.5) runs on the washer over the flush wall nut; 0 collisions in assembly_check |

## Required fixes

None.

## Round 2 fixes checked

1. **Chamfer the bed face and require EFC: done.**
   - `build()` now ends with `chamfer_bottom(to_bed(...), 0.4)` (l.49). That bevels the outer flange edge at r 16.1 and the bore mouth; cad_checks and bottom.png confirm both.
   - `elefant_foot_compensation` 0.2 is in the "min" block of print_requirements.json.

Round-2 recommendations:
- R1 (fully solid geometry): unchanged. It prints as 5 perimeters plus 20 % gyroid.
- R2 (bore running on bolt threads): unchanged. The bolt is now fully threaded.
- R3 (slice plan perimeters): still open; see the note below.

## Printing notes vs print_requirements.json

The brief asks for:
- outer flange on the bed;
- 5 perimeters, "so the bore and rim are solid walls";
- `elefant_foot_compensation` 0.2 in "min" and in slice_plan.json.

print_requirements.json matches: 5 perimeters, 4 top and 4 bottom layers, 20 % gyroid, EFC 0.2, PETG at 230–250 °C nozzle and 80–90 °C bed, ≤ 3 h. Strength round 2's rim-shell rows also use 5 perimeters, so the requirements are right.

## Note for slicing (not a DFM item)

slice_plan.json still overrides `perimeters` to 3, below the required 5. The validator will fail it at SLICE, so the slicing-lead must set 5 before slicing. The EFC 0.2 in the plan is correct.

## Recommendations (not blocking)

- **R1.** The bore runs on the threads of a fully threaded bolt, over 32.5 mm. If wear shows up in use, a 3.2 ID × 5 OD brass or steel sleeve would wear better (deep review 04, S-01 option 2). It needs a larger bore in the wheel.

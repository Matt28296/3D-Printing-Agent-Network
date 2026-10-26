VERDICT: FAIL

# DFM review, round 2: 20261026-rover-track-link

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/{iso,top,front,right,bottom}.png, print_requirements.json, slice_plan.json, rover_frame.py, assembly_check.py/json, wheel and sprocket model.py, round-1 design_review.md and strength.md. The library is empty, so the defaults apply (HOLE_COMP +0.2, measured for vertical holes).
Outputs are current: a fresh in-memory `build()` gives 1 035.28 mm³ and 16 × 24 × 7.5, identical to geometry.json. Also read: assembly BUILD_GUIDE.md (BOM, step 1).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 16.0 × 24.0 × 7.5. 34 per plate fit, for example 6 × 6 at a 19 × 27 pitch = 114 × 162 mm |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight true, min_z 0 |
| 3 | Orientation | PASS | Inner face down, grousers up, as the brief says (front.png, right.png) |
| 4 | Load paths vs layers | PASS (justified) | Track tension loads the knuckles in the layer plane. The brief notes that the tear-out shear planes lie along layer interfaces (strength round 1) |
| 5 | Bed contact | PASS (note) | 122.8 mm² per link, one connected footprint (bottom.png). PETG on smooth PEI needs a release layer (preflight) |
| 6 | Overhangs, bridges | PASS (justified) | overhang_pct 2.35 (25.6 mm², down from 5.93): the knuckle undersides within about 0.9 mm of their tangent line on the bed, which the brief acknowledges. The only "bridges" are 0.04 mm slivers at z 5.99 |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | Knuckle wall 3.0 − 1.2 = 1.80 round the running hole and 3.0 − 1.1 = 1.90 round the grip holes. Above the teardrop tips: 1.30 and 1.44. Notch side strips 6.75 − 4.0 = 2.75. thin_wall_warnings is empty |
| 8 | HOLE_COMP, teardrops | PASS | Running hole 2.0 + 0.2 + 0.2 = Ø2.4 CAD; grip holes 2.0 + 0 + 0.2 = Ø2.2 CAD. Both are teardrops pointing up in print (geometry.json arc 270° for both; front.png) |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(link, t, 0.3)` l.61 bevels the box edges, including the faces bounding the 0.5 mm axial gaps (bottom.png). The tangent knuckle lines are skipped. print_requirements.json "min" has `elefant_foot_compensation` 0.2 |
| 10 | Internal corners on load paths | PASS (note) | The box steps at the notch and bridge are sharp; strength round 1 found low stress in the 2.75 × 6 strips |
| 11 | Fasteners | PASS | A 23.5 mm, 2 mm steel rod is gripped by the outer knuckles (Ø2.0 printed, the §3 press-fit range of 0 to 0.1) and sits 0.25 mm inside each face, so no pin heads rub the wheel flanges |
| 12 | Spec §3 dims are named parameters | PASS | P 10 (rover_frame). PIN_RUN_CLR, PIN_GRIP_CLR and HOLE_COMP give the spec §2 CAD sizes, 2.4 and 2.2. KN_GAP 0.4 and the 0.5 axial gap match. The spec's "running fit" label is wrong: see item 16 |
| 13 | Service temp | PASS | 40 °C against about 70 °C for PETG |
| 14 | Lessons | N/A | None recorded |
| 15 | FreeCAD reference | N/A | None |
| 16 | Fits and assembly (cross-part) | **FAIL** | The centre-knuckle hole (Ø2.4 CAD, Ø2.2 printed) on the Ø2.0 rod leaves 0.2 mm of diametral clearance. fdm-design-rules §3 classes that as a snug or locating fit (0.15–0.2), not sliding (0.3–0.4) or free running (≥ 0.5). Spec §3 calls it a "running fit", and round-1 fix 1 asked for 0.4. Each of the 68 hinges swings 36° on every sprocket and idler wrap, under up to 14.9 N, and spec §8 needs free flex to 40° both ways. Small horizontal holes also tend to print a little under size, so the real clearance may be below 0.2. The build guide's BOM also allows ISO 2338/8734 m6 dowels (Ø2.002–2.008), which leave even less. assembly_check doesn't model the pins |

## Required fixes

1. **Open the running hole to at least a sliding fit (rule §3).** Raise PIN_RUN_CLR from 0.2 to at least 0.3: Ø2.5 CAD, about Ø2.3 printed. 0.4 (Ø2.6 CAD), as round 1 asked, is better.
   - Wall cost: the knuckle wall drops from 1.80 to 1.75 mm (1.70 at 0.4). That still holds four 0.45 mm lines at PrusaSlicer's 0.41 mm spacing (0.45 + 3 × 0.41 ≈ 1.67 mm). The wall above the teardrop tip becomes 1.23 mm (1.16 at 0.4), still ≥ 0.9.
   - Update spec §3 and the briefs' "Printed targets" line, and have the strength-analyst re-check knuckle bearing and tear-out.
   - Alternative: keep 0.2, but only after a printed 3-link coupon with your rod flexes freely to 40° both ways, and the measured fit is recorded in library/. Rule §3 lets measured fits replace the defaults.

## Round 1 fixes checked

1. Make the hinge a real running fit: **partly done.** The pins are now 2 mm steel, gripped by the outer knuckles (PIN_GRIP_CLR 0, Ø2.2 CAD), with no melted heads. But the clearance in the centre knuckle is 0.2, below the 0.3–0.4 asked for (fix 1).
2. Teardrop the pin holes: **done** (arc 270°, front.png).
3. Protect the knuckle gaps from elephant's foot: **done.** 0.3 bed chamfer (l.61, bottom.png) and `elefant_foot_compensation` 0.2 in print_requirements.json.

## Recommendations (not blocking)

- R1. Print the spec §8 five-link chain, or the 3-link coupon, from the first plate before committing all 68 links.
- R2. The notch's bed edges are cut after the chamfer, so they are sharp. With elephant-foot compensation 0.2 required, the 0.5 mm side clearance for the sprocket tooth is still safe.
- R3. One plate of 34 has 34 islands per layer. Stringing and first-layer adhesion are for the slicer-engineer.

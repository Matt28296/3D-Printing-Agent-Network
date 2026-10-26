VERDICT: FAIL

# DFM review: 20261025-arm-gripper-jaw

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), tools/hobby_parts.py, gripper-base model.py, library/lessons.md (no entries).
Outputs are current: `build()` gives 3390.0 mm³, matching geometry.json (3390.04 mm³). The geometry.json `holes` field holds an error, so I measured the pocket from model parameters and part.stl sections.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 63 × 16 × 5 mm |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | Flat with the pocket side on the bed (bottom.png) |
| 4 | Load paths | PASS | Bar bending is in-plane, along the layers |
| 5 | Bed contact | PASS | 585.0 mm². A small PETG part, so no warping concern |
| 6 | Overhangs / bridges | PASS | The only overhang is the SG90 pocket ceiling at z 2.0 (84.9 mm²). The longest strand anchored at both ends is 6.95 mm (mesh_check bounding-box span 7.7) |
| 7 | Walls | PASS | An opening test with a 1.8 mm disk on sections at z 1 and z 4 finds no thinner region. The minimum wall beside the arm pocket is above 1.8 mm, so the "≥1.6 mm" in the model.py comment is conservative |
| 8 | Fit holes / HOLE_COMP | **FAIL** | No `HOLE_COMP`. The horn pocket is modelled at hub Ø7.7 and tip 4.7 (SG90 horn 7.2 / 4.2 + 0.5) and prints at about 7.5 / 4.5. That leaves 0.3 mm of clearance, not 0.5 |
| 9 | Bottom edges chamfered | PASS (note) | The outline has `chamfer_bottom(jaw, 0.3)`. The pocket mouth on the bed is deliberately left unchamfered (model.py comment), so the first layer gets an elephant's-foot lip right where the horn enters. Rely on `elefant_foot_compensation` 0.2 (prusaslicer-settings) and list it in print_requirements.json |
| 10 | Internal corners on load paths | PASS (advisory) | The hub-to-bar corners are sharp (top.png). The bar-root stress is about 160 N·mm / (5 × 11.5²/6) ≈ 1.5 MPa nominal, so this is negligible |
| 11 | Fasteners | PASS | Horn centre screw through the Ø6.5 access hole, plus 1 arm screw drilled through 3 mm |
| 12 | Critical dims named | PASS | `BAR_Y0 = −6.0` (spec jaw face −6.0 ±0.3), `BAR_X1 = 55` |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C. Correct the brief's "~80 °C" |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

1. **Apply `HOLE_COMP` (0.2 default, replace once measured)** to the horn pocket: pass `clearance=0.5 + HOLE_COMP` to `horn_pocket_cutter` (rule §3, checklist 8).

## Notes

1. The jaws are drawn closed and line-to-line at y = −6, so the servo stalls on closing unless the gripper's "closed" angle is set a few degrees open in firmware. Calibrate that in software, not in CAD.

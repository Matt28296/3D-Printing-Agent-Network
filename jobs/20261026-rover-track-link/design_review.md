VERDICT: FAIL

# DFM review: 20261026-rover-track-link

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png, rover_frame.py, assembly_check.py/json, wheel and sprocket model.py. The library is empty, so the defaults apply (HOLE_COMP +0.2, measured for **vertical** holes).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit | PASS | 16.0 × 24.0 × 7.5. 34 per plate fits, for example 7 × 5 at a 19 × 27 pitch = 133 × 135 mm |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight, min_z 0 |
| 3 | Orientation | PASS | Inner face down, grousers up (front.png, right.png) |
| 4 | Load paths vs layers | PASS | The pin axis lies along the bed, and the track tension (X) loads the knuckles in the layer plane |
| 5 | Bed contact | PASS (note) | 137 mm² per link, one connected footprint (bottom.png). Fine for PETG; PETG on smooth PEI needs a release agent (preflight) |
| 6 | Overhangs, bridges | PASS (justified) | overhang_pct 5.93. The knuckle cylinders (r 3.0) touch the bed tangentially, so their undersides exceed 45° only in the lowest 0.88 mm. Half-chord per layer is 0.77, 1.31, 1.66, 1.93, 2.14 mm at z 0.1 to 0.9: steps of up to 0.54 mm per layer, ending on the bed. The brief acknowledges this. The only bridges are the pin-hole tops (span 0.26) |
| 7 | Walls | PASS | Knuckle wall around the pin is 3.0 − 1.05 = 1.95 (≥ 1.8). Centre side strips 6.75 − 4.0 = 2.75. thin_wall_warnings empty |
| 8 | HOLE_COMP, teardrops | **FAIL** | HOLE_COMP is applied (1.75 + 0.15 + 0.2 = Ø2.1 CAD). But both pin holes are **horizontal and round**: l.53 is a plain Cylinder, and geometry.json shows arc_deg 355 for both Ø2.1 holes, where a teardrop would read about 270. The +0.2 comp is the vertical-hole default; a round horizontal hole also sags at its top, about 1 layer at Z 4.05 (mesh_check bridge) |
| 9 | Bottom edges chamfered | **FAIL** | No chamfer (`to_bed` only). The 0.5 mm axial knuckle gaps (CENTRE_HALF 6.75 vs OUTER_IN 7.25, which pass between neighbouring links) have their side-face edges on the first layer. Elephant's foot of 0.1 to 0.2 per edge can close them to 0.1 to 0.3 mm, and the 40° flex test (spec §8) needs them free |
| 10 | Internal corners | PASS (note) | Box-cut steps at the notch and bridge are sharp, but the 10 N pull gives < 1 MPa in the 2.75 × 6 strips |
| 11 | Fasteners | PASS (note) | 25 mm filament pins in a 24 mm link, ends melted. Clearance to the road-wheel flange: the pin's inner surface is at r 15.31 from the wheel axle, where the flange is at |y| 14.5, 2.0 mm past the pin end (|y| 12.5). A melted head must stay ≤ 1 mm and the pin must be centred |
| 12 | Spec §3 dims | PASS | P from rover_frame. Pin hole Ø1.9 printed, KN_GAP 0.4 and the 0.5 axial gap match spec §3. The spec's fit value itself fails rule §3 (item 16) |
| 13 | Temperature | PASS | 40 vs about 70 °C |
| 14 | Lessons | N/A | None |
| 15 | FreeCAD reference | N/A | None |
| 16 | Fits and assembly | **FAIL** | Every knuckle is a running joint, and the pin turns in all three knuckles. The printed target Ø1.9 on 1.75 filament (±0.02 to 0.05) is 0.15 mm diametral clearance, which is a snug or locating fit; rule §3 wants 0.3 to 0.4 for sliding and ≥ 0.5 for free running. Top sag and Z stair-stepping in a round horizontal hole take most of that 0.15 away. With 68 joints × 3 knuckles, binding is likely, and the spec §8 "flex freely to 40°" would fail. assembly_check does not model the pins |

## Required fixes

1. **Make the hinge a real running fit (rule §3).** Recommended: the centre knuckle runs, Ø2.15 printed / Ø2.35 CAD (0.4 mm), and the outer knuckles grip the pin, Ø1.8 printed / Ø2.0 CAD. The pin is then held by the link that carries it, with no melted heads to rub the wheel flanges. The minimum alternative is all holes at Ø2.35 CAD, keeping the melted heads. Update spec §3 ("Ø1.9 printed, free running") to match whichever is chosen.
2. **Teardrop or flat-top the pin holes (rule §2).** Point the teardrop at the grouser face (−z in the design frame, +Z in print). For Ø2.35 the tip is r·√2 = 1.66 above the axis, leaving 1.34 mm (≥ 0.9) on the unloaded side. A flat top at r + 0.15 (about a 2.3 mm bridge) also works. Then print a fit coupon: 3 links and 2 pins.
3. **Protect the knuckle gaps from elephant's foot (rule §2 and §6).** Add a 0.3 mm 45° chamfer on the bed-face edges (`chamfer_bottom` after the flip), at least on the side faces that bound the 0.5 mm axial gaps. Also require `elefant_foot_compensation` ≥ 0.2 in print_requirements.json.

## Recommendations (not blocking)

- R1. Knuckle undersides: truncating each exposed knuckle 0.3 mm above the bed (a flat on the inner side) removes the 70° first step. The wall under the pin is then 1.65 mm. If that is too thin, keep the cylinder; the overhang only reaches 0.88 mm.
- R2. Print the spec §8 five-link proof chain from the first plate before committing all 68 links.
- R3. One plate of 34 is about 36 cm³ of PETG with 34 islands per layer. Check the 6 h batch limit in slicing, and expect stringing: retraction and avoid-crossing-perimeters are for the slicer-engineer. A single detached link can wreck the plate, so the first layer matters.

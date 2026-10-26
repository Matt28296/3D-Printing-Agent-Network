VERDICT: FAIL

# DFM review: 20261026-rover-wheel

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png, chassis model.py (boss and nut trap), rover_frame.py, assembly_check.json. The library is empty, so the defaults apply.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit | PASS | 32.2 × 32.2 × 32.5 |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight, min_z 0 |
| 3 | Orientation | PASS | Outer flange down, hub boss up (iso.png, front.png) |
| 4 | Load paths vs layers | PASS (note) | Radial rim load goes to the bore in the layer plane. The 3 N skid-steer axial load on the upper flange bends its root across the layers, but the load is tiny |
| 5 | Bed contact | PASS | 805 mm² |
| 6 | Overhangs, bridges | PASS | The upper V-cone is exactly 45° (CONE_RISE 3 over 3 mm). overhang_pct 0, no bridges. The brief's round-1 32 mm bridge has been removed |
| 7 | Walls | PASS | Solid body. Flange edge band 0.7 mm tall at r 16.1, backed by solid material |
| 8 | HOLE_COMP, teardrops | PASS | Bore BORE 3.2 + 0.2 = Ø3.4 CAD, vertical (geometry.json hole 3.4, axis Z) |
| 9 | Bottom edges chamfered | **FAIL** | No chamfer in `build()`. The bed-side flange edge (r 16.1) gets elephant's foot (front.png, sharp bottom edge) |
| 10 | Internal corners | PASS | The rim-to-cone corners are 135°, with no sharp re-entrant corner on the load path |
| 11 | Fasteners | **FAIL** | See 16b: the listed bolt is too short |
| 12 | Spec §3 dims | PASS | RIM_R = STRAIGHT_IN − 0.08 = 13.10 and BORE 3.2 match spec §3. RIM_HALF 12.3 gives 0.3 mm side clearance to the 24 mm track |
| 13 | Temperature | PASS | 40 vs about 70 °C |
| 14 | Lessons | N/A | None |
| 15 | FreeCAD reference | N/A | None |
| 16 | Fits and assembly | **FAIL** | (a) The running bore prints Ø3.2 on M3: 0.2 mm diametral clearance, but rule §3 free running is ≥ 0.5. (b) The wheel spans world Y 38.5 to 71.0 (INNER_FACE_Z −16.5, h 16.0). The M3×40 from spec §2, with its head on the chassis boss face at Y 32, ends at Y 72.0. A washer (0.5) and nyloc (4.0) beyond the wheel face need Y 75.5, so the nyloc cannot be fitted |

## Required fixes

1. **Running bore.** Raise BORE from 3.2 to 3.5 printed (3.7 CAD): rule §3, free running ≥ 0.5 mm. Update spec §3 to match.
2. **Bolt length (spec §2 / chassis spec §2 fastener list).** Specify M3×45 for the four road-wheel bolts (tip at Y 77, giving about 1.5 mm of thread past the nyloc). Or narrow the wheel by at least 4 mm, but RIM_HALF is set by the 24 mm track, so the bolt is the right change.
3. **Chamfer the bed face.** Add a 0.4 mm 45° chamfer on the bed-face flange edge (`chamfer_bottom` after the flip): rule §2 and §6.

## Recommendations (not blocking)

- R1. The wheel is fully solid (18.2 cm³ × 4). A hub, web and rim design (for example a 2.4 mm rim shell and a 3 mm web) would cut mass and print time without affecting the bore or flanges.
- R2. The bore runs on bolt threads over 32.5 mm. A plain-shank bolt or a brass sleeve would reduce wear.

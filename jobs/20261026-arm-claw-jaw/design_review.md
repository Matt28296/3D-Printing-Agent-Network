VERDICT: FAIL

# DFM review: 20261026-arm-claw-jaw (×2) (round 2)

Reviewer: dfm-reviewer (independent) · 2026-10-26 · DESIGN gate, round 2 (round 1: FAIL).
Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, print_requirements.json, slice_plan.json (read only), renders/*.png (regenerated; all 5 viewed), round-1 design_review.md and strength.md, ../20261025-robot-arm-assembly/claw_frame.py, claw_sequence_check.py/.json, BUILD_GUIDE §4 step 10, deep review 03 (SYS-01, SYS-08), tools/gears.py, library/ (no lessons, no material rows, so skill defaults apply).

The outputs are current. `build()` rebuilt in memory gives 16 126.67 mm³ and 6281.38 mm², the same as geometry.json, and mesh_check re-run in memory reproduces mesh_check.json. Extra evidence:
- a layer-by-layer slice of part.stl: 0.2 mm layers on a 0.02–0.04 mm raster, with even-odd, nonzero and positive fill (they agree);
- an uncapped version of mesh_check's thin-wall test;
- sections of the teeth near the bed;
- `gears._chamfer_band` rebuilt both ways, as a loft and as 0.1 mm steps;
- a scratch copy of model.py with only `BED_CHAMFER = 0.25`, built and checked the same way.

Print frame: (X, Y, Z) = claw G (−z, y, x − 22.6). The rack's teeth point to +X, and the tooth band is print X −38.5…−36.4 (G z 36.4 tip line to 38.5 root).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits the bed with a 5 mm margin | PASS | 31.25 × 56.55 × 60.75 mm, `fits_bed: true`; two copies fit one plate |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, `min_z_mm: 0.0`, OCC valid |
| 3 | Orientation matches the brief | PASS | Standing on the rack's x 22.6 face, finger up, teeth in the bed plane (iso.png, front.png, right.png) |
| 4 | Load paths vs layers | PASS (justified) | The brief and spec §4 now say every bending of the neck and finger runs across the layers (round-1 fix 3). The sections are strength candidate C, sized for the 12.5 MPa across-layer placeholder |
| 5 | Bed contact | PASS (note) | 566.7 mm², PETG, no brim (`max.brim_width` 0, because a brim would fill the tooth gaps). **Note:** the part is 60.75 mm tall and its centre of mass (print −37.9, −2.7, 21.5) sits over the tooth edge of the footprint: solid back X −48.5…−38.5, teeth to −36.4. The finger reaches 19 mm past the footprint at the top (front.png). Round-1 R2 (small ears at the rack ends if it rocks) still applies |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | **FAIL** | The bed chamfer is defective (item 9), and as a result layer 2 overhangs layer 1 by up to **1.04 mm** at the teeth, under all three fill rules. A true 45° chamfer gives 0.20 mm. The layer check flags 14 teeth at z 0.3, each 0.65–0.91 mm² with nothing under it for up to 0.77 mm beyond the 0.3 mm allowance. Everything else passes: the finger's lower edge is exactly 45° with an r 3 kink fillet (front.png); the gusset and the taper recede upwards; the grooves are 45°; no bridges outside the bed band. overhang_pct 0.47 |
| 7 | Walls ≥ 1.8, none < 0.9 | **FAIL** | `thin_wall_warnings`: 20, the list cap, at 0.02–0.17 mm and print z ≤ 0.2. **The designer says these are "only the chamfered tooth tips at the bed". Not confirmed:** (a) they sit at print X −38.2…−37.1, i.e. G z 37.1–38.2, which is 0.7–1.8 mm in from the tip line (36.4), in the middle and root of each tooth, not at the tips; (b) the cap hides the count: an uncapped scan finds 1,120 hits among 6,000 sampled faces, all at print z < 0.3; (c) they come from the twisted chamfer (item 9): the scratch build with a true 0.25 chamfer has no hits in the bed band. The only other hits, 2, are at acute (≈72°) convex edges (the neck/gusset corner at G (38.4, −19.9, 38.2) and a groove end at the finger top); those are corners, not walls. **Real walls:** rack back 10, neck 20 × 10, finger 12 → 6. The fingertip is 1.0 mm behind the 1.5 mm V-notch at the very tip (x 83.35) and ≥ 1.8 for x ≤ 81.75: a thin tip by design (round-1 R3), and the spec §8 dowel test loads it |
| 8 | HOLE_COMP; horizontal holes | N/A | No holes |
| 9 | Bottom edges chamfered | **FAIL** | **The 0.3 mm bed chamfer on the tooth outline is not a 45° chamfer.** `gears._chamfer_band` makes it as a ruled loft from the rack outline (256 edges) to its 0.3 mm inset. That inset has only 254 edges, so the loft pairs the wrong edges and the band twists. Its volume is 175.196 mm³, against 178.149 for a true 45° band; the 0.1 mm stepped band gives 178.147. OCC still calls the solid valid, so gears.py's fallback to steps never runs. **Effect at print z 0.1:** each tooth's tip is cut back to G z ≈37.15, 0.75 mm in from the tip line (a true chamfer gives 0.15), and a notch runs into one flank to within ≈0.25 mm of the root. The first layer keeps 38.2 of the 72.7 mm² tooth band (a true chamfer keeps 56.8). The mesh balloons to 182 706 faces (3580 with a true chamfer). gears.py's docstring itself limits true gear chamfers to 0.25 m. Away from the teeth the chamfer is true: the back edge and both rack ends are inset exactly 0.20 mm at print z 0.1 (bottom.png) |
| 10 | Internal corners on load paths filleted | PASS | Neck roots r 4 at both y edges (round-1 fix 2; right.png); kink fillets r 3 (front.png); gusset end r 3 and taper r 3 (top.png); rack tooth roots r 0.30 (`RACK_ROOT_FILLET`) |
| 11 | Fasteners per §4 | N/A | No fasteners |
| 12 | Spec §3 dims are named parameters | PASS | RACK_OUT − R_P = 11.25, FACE_W 10, RACK_BACKLASH 0.5 (each tooth 0.25 thinner), TIP_RELIEF 0.15, NECK_Y 20 × NECK_Z 10, grip face y 0. All named, with comments, in claw_frame.py, matching spec §3 |
| 13 | Service temperature | PASS | 40 °C against PETG at ≈70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ |

## Required fixes

1. **Make the bed chamfer a true 45° chamfer (items 6, 7 and 9).**
   - **Change:** set `BED_CHAMFER` 0.3 → 0.25 (model.py l.39). The 0.25 inset keeps all 256 edges, so the loft is true. That is gears.py's documented limit for module 1, and the pinion's value.
   - **Verified on a scratch copy with only that change:**
     - layer 1 keeps 56.8 mm² of the tooth band;
     - layer 2 overhangs it by 0.20 mm, which is 45°;
     - no unsupported region in the first 2 mm;
     - no thin-wall hits in the bed band;
     - 3580 mesh faces;
     - tooth tip at the bed 0.35 mm wide.
   - **Alternative:** keep 0.3 and have toolsmith make `_extrude_chamfered` use the stepped band whenever the inset's edge count, or its volume, differs from the loft's. That also stops a twisted loft passing silently in other gear jobs.
   - **Then:** rebuild, re-run mesh_check (`thin_wall_warnings` should be down to the 2 corner hits) and claw_sequence_check.
   - **Rule:** §2 and §6 (the bed edge gets a 45° chamfer); `tools/gears.py` docstring (≤ 0.25 m for a true face).
   - **Evidence:** items 6, 7 and 9.

## Round-1 required fixes

| Round-1 fix | Status | Evidence |
|---|---|---|
| 1. Chamfer the bed face 0.3 mm, tooth outline included | Done, but defective | Fix 1 above |
| 2. Fillet the neck root; move the slot ends | Done | NECK_FILLET 4 at both y edges. SLOT_A_END 6.5 and SLOT_B_END 5.0 in the cover. claw_sequence_check: both slide-in paths and the stroke 0 mm³ |
| 3. Correct the load-path rationale | Done | Brief (orientation) and spec §4 say every bending is across the layers |
| R1. Neck vs pinion front face (item 16) | Closed | The neck now sits on the rack's solid back, at r ≥ 11.25 from the axis, outside the pinion's 10.85 tip circle: 0 mm³ over the stroke |
| R2. Ears if the print rocks | Still advisory | Item 5 |
| R3. Thin fingertip | Unchanged by design | 1.0 mm at the very tip (item 7) |
| Strength: candidate C | Done | RACK_BACK 10, neck 20 × 10 with r 4, finger 12 → 6, full-height gusset, r 3 kinks. The rack runs RACK_Y −8π…10π, with both ends in a tooth gap, so the neck sits wholly on the rack |

Other round-2 changes checked:
- **Teeth at a 0.4 mm nozzle:** 1.32 mm at the pitch line (0.25 thinner), tip land 0.70 after the 0.15 topping, root fillets r 0.30. All are in the bed plane. The tip land is 0.1 mm under the 0.8 mm smallest feature, at the tip of a tapered tooth, as for the pinion.
- **Rack edge chamfer:** 2 mm, for y ≥ 4.5. It faces up in print.
- **Grip grooves:** the two nearest the neck (x 60.6 and 62.6) end below the finger's top edge. That leaves a 0.5–0.6 mm step of grip face above each, which is surface relief, not a wall.

## Recommendations (not blocking)

- R1. **Bed adhesion (item 5):** if the first print rocks, add two small sacrificial ears at the rack's y ends, away from the teeth and the back face.
- R2. **gears.py:** see fix 1's alternative. The same twist can come back in any job with module 1 and a chamfer over 0.25.
- R3. **Process:** the slice files in this folder date from before round 1. Re-slice after the DESIGN gate passes.

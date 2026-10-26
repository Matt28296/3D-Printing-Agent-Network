VERDICT: FAIL

# DFM review: 20261026-arm-claw-pinion

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, print_requirements.json, renders/*.png (all 5 viewed), ../20261025-robot-arm-assembly/claw_frame.py, assembly_check.py/json, BUILD_GUIDE.md (step 9), tools/gears.py, tools/hobby_parts.py (`horn_pocket_cutter`, MG90S_DOUBLE), the jaw model, library/ (empty, so skill defaults apply).
Outputs are current: `build()` gives 1765.53 mm³, the same as geometry.json. Numbers below come from ray casts through `design()` and, for item 16, from mesh booleans with the pinion placed in G as assembly_check.py places it.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 20.0 × 19.8 × 8.0 mm |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | Back face (horn pocket) on the bed, axis vertical, so the involute lies in the bed plane (iso.png, top.png, bottom.png) |
| 4 | Load paths vs layers | PASS | Tooth bending and horn-stub bearing both lie in the layer plane |
| 5 | Bed contact | PASS | 138.7 mm² |
| 6 | Overhangs / bridges | PASS | Only the pocket ceiling at z 2.0: span 7.7 (hub), length 11.5. The 4.67 % overhang is that ceiling |
| 7 | Walls | PASS (note) | Pocket arc (r 5.75) to root circle (r 7.75): **2.0 mm** (rays at 10°, 30° and 170°). Hub to root: 3.9. Teeth (module 1, 0.45 mm extrusion): 1.52 at the pitch line, which is **3.4** extrusion widths, not the 4 in claw_frame.py's comment; 1.54–1.68 at the root; 0.94 at r 9.72, 0.80 at r 9.85 and **0.63** at the tip. Only the outer 0.15 mm of each tooth is under the 0.8 mm minimum feature, so the tips may print slightly rounded. The contact ratio is 1.76 nominal and about 1.66 even if that 0.15 mm is lost |
| 8 | HOLE_COMP / horizontal holes | PASS | Pocket clearance 0.3 + HOLE_COMP 0.2, clamp hole Ø2.6, counterbore Ø4.4. There are no horizontal holes |
| 9 | Bottom edges chamfered | PASS (note) | The 0.25 bed chamfer is present despite the try/except at l.31–34: a ray at r 9.9 starts at z 0.15, and bottom.png shows the bevel on every tooth. The pocket mouth is unchamfered (snug static fit; the slice uses EFC 0.2). See R1 |
| 10 | Internal corners on load paths | **FAIL** | Tooth roots are sharp. `gear_outline` (tools/gears.py) joins the radial flank to the root circle at a corner with no fillet (top.png, bottom.png). Lewis at stall: 24 N on one rack, Y 0.309 (18 teeth), b 8, m 1 → **9.7 MPa**. With Kt 2–3 at a sharp root that is 19–29 MPa, against the 25 MPa in-plane placeholder, and normal gripping cycles at about half that. rover-sprocket round 1 failed the same point |
| 11 | Fasteners (§4) | PASS | M2×10 from the Ø4.4 × 1.6 counterbore: 6.4 mm through the pinion, then about 5 mm into the spline past the horn face. The wrist joint's M2×12 was accepted at about 7 mm |
| 12 | Spec §3 dims named and matching | PASS (note) | M, Z_TEETH, BACKLASH, POCKET_CLR 0.3, HORN_TRIM_R 5.5 and HEAD_D/HEAD_H are named with comments. Spec §2 gives the hub as Ø7.6, but the CAD hub is Ø7.7. The Ø4.4 counterbore is the CAD size; it prints at about 4.2 (R3) |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |
| 16 | Cross-part fit with real hardware (added, as in rover-sprocket) | **FAIL** | (a) **The trimmed horn does not fit the pocket.** BUILD_GUIDE step 9 says to cut the arms 5.5 mm from the centre and "file the cut ends flat". The pocket's stub ends are r 5.75 arcs (bottom.png; pocket half-width 2.84 at x 5.0 and 1.68 at x 5.5). A flat end 5.5 out on an arm about 6.0 wide (hobby_parts MG90S taper, half-width 3.01) puts the corners at **r 6.27**, 0.5 mm into the wall. (b) **No axial clearance to the jaw necks.** The front face (G x 27.40) overlaps both necks, whose back faces are at x 27.39: 0.033 mm³ per jaw over y −3.8 to 0, z 30.5–32.5 at closed. They still touch at a 10 mm gap and are clear by 16 mm. assembly_check.py counts anything under 1 mm³ as touching, so it could not flag this. In print, the neck bridges over the rack's tooth gaps (jaw mesh_check, z 7.99) and sags into the space these teeth run through |

## Required fixes

1. **Make the horn preparation and the pocket agree without thinning the 2.0 mm root wall (item 16a).** Keep the pocket. Change spec §1 and BUILD_GUIDE step 9 (the Architect's files) from "cut 5.5 mm from the centre, file the ends flat" to "cut 5.5 mm from the centre, then file each stub end round so the horn fits inside a Ø11 circle". The alternative is to cut flat at 4.6 mm from the centre. Do **not** square the pocket ends instead: at x 5.75 the corners reach r 6.61, which leaves only 1.14 mm to the tooth roots. Rule §2 (structural walls ≥ 1.8) and §3 (fits).
2. **Give the pinion 0.5 mm of axial clearance from the necks (item 16b).** Relieve the front face 0.5 mm over r ≥ 7.5, the teeth only, keeping the hub and the Ø4.4 × 1.6 counterbore as they are. Alternatively, make the pinion 7.5 wide instead of 8.0 and re-check the M2×10 length. The teeth then use 7.5 of the racks' 8 mm, so strength-analyst should add about 7 % to the Lewis stress. Also make assembly_check.py report pinion/jaw overlaps above about 0.001 mm³ instead of 1 mm³. Rule §3 (free-running clearance ≥ 0.5 mm). Evidence: item 16b.
3. **Fillet the tooth roots (item 10).** In tools/gears.py (toolsmith), add the standard 0.38 m = **0.38 mm** root fillet to `gear_outline`, and about 0.3 mm to `rack_outline`, whose root land is 0.71 mm wide. Rebuild the pinion and the jaw and re-check the mesh over 0–44 mm. At r 8.0, the depth the rack tips reach, the 0.38 fillet stands only 0.02 mm off the flank, while the rack tip passes about 0.2 mm from it. The rule's r ≥ 1–2 mm cannot fit a 1.17 mm root land. Rule §2 (internal corners on load paths).

## Recommendations (not blocking)

- R1. Drop the try/except around `chamfer_plane_edges` (l.31–34). A future failure should stop the build instead of silently dropping the chamfer.
- R2. Slicing: the outer 0.3 mm of each tooth is 0.63–0.94 mm wide. The profile leaves `perimeter_generator` unset, so confirm in the slice preview that Arachne or gap fill fills the tips. print_requirements.json now asks for 100 % rectilinear, which suits PrusaSlicer at 100 %.
- R3. In spec §2/§3, write "Ø4.4 CAD (≈4.2 printed)" for the counterbore and "hub Ø7.7 CAD" for the pocket.
- Process note: part.gcode and the other slice files were written here at about 05:24–05:25 UTC, before this review. Re-slice after the fixes.

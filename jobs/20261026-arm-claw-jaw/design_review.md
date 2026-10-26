VERDICT: FAIL

# DFM review: 20261026-arm-claw-jaw (×2)

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, print_requirements.json, renders/*.png (all 5 viewed), ../20261025-robot-arm-assembly/claw_frame.py, assembly_check.py/json, tools/gears.py, the pinion and cover models, slice_plan.json (read only), library/ (empty, so skill defaults apply).
Outputs are current: `build()` gives 6898.26 mm³, the same as geometry.json. Numbers below come from ray casts through `design()` (claw frame G; print Z = G x − 19.4) and from mesh booleans with the pinion placed as in assembly_check.py.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 26.25 × 43.98 × 56.75 mm |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | Standing on the rack's x 19.4 face (the face that runs against the lip or lower rail) with the finger up and the teeth in the bed plane (iso.png, right.png, bottom.png) |
| 4 | Load paths vs layers | **FAIL** | The grip case across the layers is acknowledged. But the brief says "Sideways pushes bend the blade along its layers", and spec §4 row 3 says "(along the layers)". The finger grows along print Z, so **any** bending of the neck or blade puts its stress along Z, across the layers. At the neck root about y (14 wide, 5 deep, S 58 mm³): 5 N at x 74 gives **4.0 MPa**. The 12 N base-yaw stall in the spec §4 text gives **9.6 MPa** nominal, and about **16 MPa** on the area actually bonded, because the neck's lower 2.25 mm stands on rack teeth with gaps between them (ray at x 27.35, z 31.6). The across-layer placeholder is 12.5 MPa |
| 5 | Bed contact | PASS (note) | 314.7 mm². But the part is 56.75 mm tall on a footprint only 8.25 mm wide in print X, and the blade overhangs that footprint by up to 18 mm (front.png). See R2 |
| 6 | Overhangs / bridges | PASS | Overhang 0.37 %. The neck's underside bridges the rack's tooth gaps at print z 7.99 (spans ≤ 2.35 mm, mesh_check); item 16 covers what their sag does. The blade underside is exactly 45°, the V-groove flanks are 45° and the flare recedes upward (right.png) |
| 7 | Walls | PASS (note) | Neck 14 × 5, blade 6, rack body 6 behind the roots. Rack teeth are 1.52 at the pitch line and 0.79 at the tip. The fingertip wall behind the 1.5 mm V-notch is 1.08 mm at x 76.0 and reaches 1.8 mm only 1.5 mm back from the tip (x 74.6). That thin tip is by design. `thin_wall_warnings` is empty |
| 8 | HOLE_COMP / horizontal holes | N/A | No holes (geometry.json `holes: []`) |
| 9 | Bottom edges chamfered | **FAIL** | There is no chamfer anywhere: `build()` is `to_bed(Rot(0, -90, 0) * design())` (l.101–102). Rays 0.05 mm inside the rack's back face (z 38.70) and at the tooth tips (z 30.55) both start at x 19.40, and bottom.png shows square edges. This bed face carries the rack's back edge, which runs 0.25 mm from the cover's top wall (jaw A) or the wrist plate (jaw B), and the tooth flanks, which have 0.1 mm backlash per member. The slice's EFC 0.2 is only half of rule §6 |
| 10 | Internal corners on load paths | **FAIL** | The neck meets the rack's front face (x 27.4) with sharp 90° corners along z at y 0 and y −14 (top.png, right.png). For jaw A's grip, the y 0 side is in tension across the layers. At the neck root, 24 N at x ≈ 72 gives 1070 N·mm; with S_z 163 mm³ that is **6.6 MPa** nominal, and about **8.5 MPa** on the area bonded over the teeth. A tooth gap sits right at y 0: the ray at x 27.35, z 31.6 is empty from y −0.77 to 0.77. With Kt ≈ 2 at the sharp corner that becomes 13–17 MPa, against 12.5 MPa across the layers. The rack's tooth roots are sharp too (gears.py, see pinion fix 3), but their 110° corners at 6.2 MPa nominal (Lewis, rack Y 0.485) matter less |
| 11 | Fasteners (§4) | N/A | No fasteners |
| 12 | Spec §3 dims named and matching | PASS | Pitch line to back face = RACK_BACK 6 + 1.25 m = 7.25; face width FACE_W 8.0; neck NECK_Y 14 × NECK_Z 5; grip face at y 0 (RACK_Y with phase P_CIRC/2). All are named in claw_frame.py with comments |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |
| 16 | Cross-part fit, moving joint (added, as in rover-sprocket) | **FAIL** | The neck's back face (x 27.39) overlaps the pinion's front face (x 27.40): 0.033 mm³ per jaw over y −3.8 to 0, z 30.5–32.5 at closed. The parts still touch at a 10 mm gap and are clear by 16 mm. assembly_check.py's 1 mm³ tolerance hides this. The neck bridges in item 6 sag into exactly that space. **The fix belongs in the pinion (pinion fix 2); this part needs no change for item 16** |

## Required fixes

1. **Chamfer the bed face (item 9).** Chamfer every edge of the rack's x 19.4 face 0.3 mm, tooth outline included. That face is `rack_bar`'s z = FACE_W end, so do it before placing the rack: `rack = RACK_LOC * chamfer_plane_edges(rack_bar(...), FACE_W, 0.3)`, as the pinion does with 0.25. Rule §2 and §6.
2. **Fillet the neck root (item 10).** Fillet r ≥ 1 mm (2 mm if the slots allow) along the neck's two root edges at y 0 and y −14 (x 27.4, z 30.5–35.5). So that the jaws still close, move each cover slot's closed end out by the fillet size, slot A to y +1.25 and slot B to y −1.25. Use a new parameter, because SLOT_CLR also sets the slot width (cover R3). Then re-run assembly_check.py. The rack roots get their fillet from pinion fix 3 (tools/gears.py). Rule §2 (internal corners on load paths).
3. **Correct the load-path rationale (item 4).** In design_brief.md and spec §4 row 3, state that the 5 N sideways push and the 12 N base-yaw stall (spec §4 text) bend the neck and blade across the layers. Add both as across-layer cases for strength-analyst; the critical one is expected to be 12 N on the neck root's bonded area, about 16 MPa against 12.5. If strength fails, options include a taller neck in z, or a fillet on the z 35.5 root edge with slot A widened to match. Rule §1 (trace every load path; justify loads across layers).

## Recommendations (not blocking)

- R1. Item 16 is closed by pinion fix 2, the 0.5 mm front-face relief. If you would rather change this part, the neck's back face must stay at least 0.5 mm clear of the pinion's teeth (r ≤ 10) over z 30.5–32.5.
- R2. Tall, narrow print: don't use a brim, because it would fill the tooth gaps. If the first print rocks, add two small sacrificial ears (about Ø8 × 0.4) at the rack's y ends, away from the teeth and the back face. Print the two copies side by side as slice_plan.json plans.
- R3. The fingertip is 1.08 mm thick behind the V-notch. If it chips in the dowel test, end the notch 2 mm short of the tip.
- Process note: part.gcode and the other slice files were written here at about 05:24–05:25 UTC, before this review. Re-slice after the fixes.

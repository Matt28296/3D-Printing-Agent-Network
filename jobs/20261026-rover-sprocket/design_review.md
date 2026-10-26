VERDICT: PASS

# DFM review, round 3: 20261026-rover-sprocket

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26 · Inputs: spec.md, design_brief.md (concepts A/B/C), model.py, geometry.json, mesh_check.json, cad_checks.py, renders/{iso,front,right,top,bottom}.png (regenerated with tools/render.py), print_requirements.json, slice_plan.json, round-2 design_review.md and strength.md, rover_frame.py, tools/hobby_parts.py (POLOLU_HUB_1996, N20_100RPM), chassis model.py (skin, nacelle), assembly_check.json, BUILD_GUIDE.md (step 6), deep reviews 04 (S-03, S-04) and 01 (S9, S10). The library is empty, so the defaults apply (HOLE_COMP +0.2).

Outputs are current: a fresh in-memory `build()` gives 3 554.86 mm³ and 35.777 × 34.52 × 7.0, identical to geometry.json. `mesh_check.check()` re-run in memory is identical to mesh_check.json. `cad_checks.py`: all 14 checks pass. Extra evidence: a layer-by-layer support analysis of part.stl (0.1 mm grid, 0.2 mm layers).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 35.8 × 34.5 × 7.0; two per plate (slice_plan copies 2) |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight true, min_z 0.0 |
| 3 | Orientation | PASS | Outer face on the bed (`Rot(180, 0, 0)`, l.97), as the brief says. bottom.png shows the bevel on the bed face; iso.png shows the hub face up |
| 4 | Load paths vs layers | PASS | All in the layer plane: tooth bending, screw shanks bearing on the slot sides (tangential), the hub-face contact. The screw clamp is compression through the 7 mm disc. No printed hub, bore or radial hole is left (brief, concept C) |
| 5 | Bed contact | PASS | 455.3 mm² (mesh_check), PETG |
| 6 | Overhangs, bridges | PASS | overhang_pct 0, no bridges. Layer analysis: no unsupported cell in any layer. Every cut is vertical |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | Tooth 2.7 at the root, plus the root chamfers; the tip is 1.6, an unloaded tip, above the 0.8 minimum feature. Slot inner end (r 5.5 − 1.8 = 3.7) to the centre hole (r 1.8): 1.9. Slot to slot at r 5.5: 7.78 − 3.6 = 4.2. Slot outer end (r 8.65) to the disc rim (r 11.9): 3.25. thin_wall_warnings empty |
| 8 | HOLE_COMP, teardrops | PASS | Slots 3.4 + 0.2 = 3.6 wide in CAD (l.87); centre hole 3.4 + 0.2 = Ø3.6 (l.88; geometry.json). All holes are vertical, so no teardrops are needed |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(s, DISC_HALF, 0.3)` on the outer face, which goes on the bed (l.84); bottom.png shows it round the disc and every tooth. The slots and centre hole are cut afterwards. They are clearance features, and `elefant_foot_compensation` 0.2 is now in the requirements' "min" |
| 10 | Internal corners on load paths | PASS | The root chamfers now start on the disc circle: `xr = √(DISC_R² − (b + f)²)` (l.56, round-2 R1), so the 0.144 mm ledge is gone. The slot ends are full r 1.8 radii |
| 11 | Fasteners (§4) | PASS | 4 × M3 × 12 go into the hub's metal threads, so repeated assembly is fine. There is an ISO 7089 washer under each head, on the disc (§4: washers on plastic). Torque is carried by the shanks bearing on the slot sides, not by preload (brief: bearing SF 66–79). The hub's own set screw goes on the D-flat (BUILD_GUIDE step 6) |
| 12 | Spec §3 dims are named parameters | PASS | Each §3 dimension is a named, commented parameter: pitch radius RP 16.18 (rover_frame); disc DISC_HALF 3.5; slots `SLOT_R` = HUB.bolt_circle_r_range (5.5, 6.85) and HUB_SCREW_D + HOLE_COMP; centre hole SHAFT_CLEAR_D + HOLE_COMP; tooth tip TOOTH_TIP_R 17.9. cad_checks proves each. The SHAFT_CLEAR_D comment is stale (R1) |
| 13 | Service temp | PASS | 40 °C against ≈ 70 °C for PETG |
| 14 | Lessons | N/A | None recorded |
| 15 | FreeCAD reference | N/A | None |
| 16 | Fits and assembly (cross-part) | PASS | The Ø17.5 hub face lies inside the Ø23.8 disc. The slots end at r 8.65, inside the hub's r 8.75, so the hub face backs the disc round every slot. The slots take M3 screws on any hole circle from r 5.5 to 6.85, covering the unconfirmed 6.35. The centre hole clears the shaft end (Y 54/55) by 0.2 a side. assembly_check.json: screw tips 0.5 mm inside the hub and 1.0 mm from the skin; 7 teeth in link notches; 0 collisions with no exemptions |

## Required fixes

None.

## Round 2 fixes checked

1. **Clear the N20 output bushing: superseded, and the problem is gone.**
   - The print has no hub any more.
   - The Ø4 × 0.8 bushing now sits inside the chassis skin's Ø4.5 printed hole (y 45.0–45.8).
   - The aluminium hub starts at y 46.5, behind a 0.5 mm thrust washer at 46.0–46.5.
   - assembly_check runs with no exemptions and finds 0 collisions.
2. **Put the set screw on the flat: superseded.** There is no printed set-screw hole. The Pololu hub's own screw goes on the flat: BUILD_GUIDE step 6 says to turn the shaft so its flat faces the set screw, with threadlocker.

Round-2 recommendations:
- R1 (start the chamfer on the disc circle): done.
- R2 (hub-to-disc fillet) and R3 (GRUB_Y): superseded.
- R4 (try the first sprocket on the real parts): still applies; see R3 below.
- R5 (geometry.json `holes` error): fixed; geometry.json now lists the Ø3.6 hole.

## Printing notes vs print_requirements.json

The brief's only printing note is "outer disc face on the bed". print_requirements.json asks for:
- 4 perimeters;
- 5 top and 5 bottom layers;
- 50 % gyroid;
- `elefant_foot_compensation` 0.2;
- PETG at 230–250 °C nozzle, 80–90 °C bed;
- ≤ 2 h.

These are consistent with the brief, and with the 0.3 bed chamfer. slice_plan.json matches the requirements, with 2 copies.

## Recommendations (not blocking)

- **R1.** The comment on `SHAFT_CLEAR_D` (l.46) says the shaft end is at "Y 51.0". The docstring and assembly_check.json put it at Y 54 or 55, for a 9 or 10 mm shaft. Correct the comment.
- **R2.** The disc is centred only within its clearances: the Ø3.4 printed centre hole on the Ø3.0 shaft, and the 3.4 mm slots on M3. That allows up to about 0.2 mm of eccentricity, although BUILD_GUIDE step 6 says the shaft end "centres the disc". Before the final tightening, spin the sprocket and nudge it true (spec §8: "it runs true").
- **R3.** The hub's hole circle is unconfirmed, so print one sprocket first and fit it to your hub before printing the second.

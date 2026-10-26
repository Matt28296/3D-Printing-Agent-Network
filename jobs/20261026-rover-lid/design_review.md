VERDICT: PASS

# DFM review, round 4: 20261026-rover-lid

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26

**Inputs:**
- this job: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, cad_checks.py, print_requirements.json, slice_plan.json, log.md;
- renders/{iso,front,right,top,bottom}.png, regenerated with tools/render.py;
- the round-3 design_review.md and strength.md;
- rover_frame.py (LID_SCREWS) and tools/hobby_parts.py (ESP32 boards);
- assembly_check.json and BUILD_GUIDE.md (step 11, BOM).

The library is empty, so the defaults apply (HOLE_COMP +0.2).

**Outputs are current.**
- A fresh `build()` gives 32 288.73 mm³ and 154 × 76 × 7.1, identical to geometry.json.
- part.stl is watertight (32 288.72 mm³).
- `tools/mesh_check.py` re-run: mesh_check.json is unchanged.
- `cad_checks.py`: all 14 checks pass.

**Extra evidence** (my scripts, in the scratchpad):
- a layer-by-layer support analysis of part.stl (0.05 mm raster, 0.2 mm layers, 0.2 mm allowance);
- ray-cast wall thickness from every face (4 rays per face);
- edge-to-edge distances from each tie slot and rail to every other feature, from the model's parameters;
- `is_inside` probes on `design()`.

**What changed in round 4: one parameter.** RAIL_W went from 2.5 to 4.5 (l.38), and the rails widened outward to \|y\| 14.85–19.35. That moved the zip-tie slots out by 2.0, to \|y\| 20.85–22.65 (l.79). The window, the pocket (29.7) and the ledges did not move.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 154.0 × 76.0 × 7.1, fits_bed true |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight true, min_z 0.0 |
| 3 | Orientation | PASS | Flat, underside down. front.png and right.png show the rails standing 4.1 above the deck; top.png shows the four tie slots just outside the rails |
| 4 | Load paths vs layers | PASS | Deck bending is in the layer plane. Only the rail roots cross the layers, under a sideways push: strength round 3 gives SF 10.6 with 4.5 mm rails |
| 5 | Bed contact | PASS | 9 756.8 mm², unchanged. A 3 mm PETG plate has a low warp risk; use a glue release layer on smooth PEI |
| 6 | Overhangs, bridges | PASS | overhang_pct 0, no bridges. Layer analysis: no unsupported region in any of the 35 layers. Rails, ledges, slots and holes are all vertical walls or through-cuts |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | Rails 4.5 (10 lines), deck 3.0, ledges 2.4. Around the moved tie slots: 6.00 of deck to the window edge (the rail sits on 4.5 of it), 15.35 to the deck edge. Ray-cast: thinnest 3.0 around the tie slots, and 2.6 overall (at the 0.4 bed chamfer). thin_wall_warnings empty |
| 8 | HOLE_COMP, teardrops | PASS | Unchanged: screw holes Ø3.6 (l.83), toggle Ø6.4 (l.85), cable slots +0.1 per edge (l.88). The tie slots are clearance slots. No horizontal holes |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(lid, z0, 0.4)`; bottom.png |
| 10 | Internal corners on load paths | PASS (note) | Cable slots r2. The window corners are still sharp (round-3 R2). The wider rails stiffen the window edges that meet them |
| 11 | Fasteners (§4) | PASS (note) | Unchanged: 4 × M3 × 8 into the chassis's heat-set inserts. Still no washers under the heads (round-3 R3) |
| 12 | Spec §3 dimensions are named parameters | PASS | RAIL_W 4.5 (l.38), with its source (strength round 3; 4.0 minimum); spec §3 "4.5 wide (`RAIL_W`) ±0.2". cad_checks proves the rail width, height and extent, the tie-slot positions, and the clearances to the walls, toggle, cable slots and screws |
| 13 | Service temp | PASS | 40 °C against ≈ 70 °C for PETG |
| 14 | Lessons | N/A | None recorded |
| 15 | FreeCAD reference | N/A | None |
| 16 | Fits and assembly (cross-part) | PASS | SCREWS = rover_frame.LID_SCREWS = the chassis columns. assembly_check.json: 158 bodies, 0 collisions. The tie slots stay 10.85 inside the chassis walls' inner faces (\|y\| 33.5), so the ties under the deck run over the tub |

Rails and tie slots against the other features (edge to edge, from the model's parameters):

| From | To | Distance (mm) |
|---|---|---|
| Rails (\|y\| 14.85–19.35, x 13.4–69.0, 4.1 tall) | toggle hole Ø6.4 at (0, −23) | 10.69 |
| | cable slots (x 70.9–81.1, \|y\| 1.4–12.1) | 1.90 in X, 3.3 diagonal |
| | screw holes at \|y\| 32.5 | 11.35 |
| USB-end tie slots (x 13.6–16.8) | toggle hole | 10.40 (right side), 42.7 (left side) |
| Far tie slots (x 62.7–65.9 and 65.6–68.8) | cable slots | 9.00 or more |
| All tie slots | screw holes; rail outer face; window edge; deck edge | 26.57 or more; 1.50; 6.00; 15.35 |

The two far-end slots (for the 38- and 30-pin boards) overlap by 0.3. They print as one 6.1 × 1.8 slot, as in round 3, and the deck around it is 6.0 or more on every side.

## Required fixes

None.

## Round-3 findings

Round 3 had no required fixes. Its recommendations:
- **R1 (USB-end tie on EN/BOOT):** still applies. The ties are still 1.2 mm from the board ends.
- **R2 (window corners r ≥ 2):** not done.
- **R3 (M3 washers under the lid-screw heads):** not done, and not in the BOM.

The round-3 checklist items all still pass on the round-4 geometry.

## Recommendations (not blocking)

- **R1 (new; a BOM line in the assembly job): give the ESP32 zip ties a length.**
  - The wider rails and the moved slots make each tie's loop about 98 mm, up from about 90:
    - 28.3 over the board;
    - twice 13.9 for the rail top, the rail face, the deck and the slot;
    - 41.7 under the deck between the slots.
  - A common 2.5 × 100 mm tie can't close that.
  - BUILD_GUIDE §1 only says "2 at most 2.5 mm wide (ESP32)". Make it "at most 2.5 mm wide and at least 150 mm long".
- **R2 to R4:** round-3 R1, R2 and R3, as above.

## Printing notes against print_requirements.json

- The brief's only printing note is "flat, underside on the bed".
- print_requirements.json asks for 3 perimeters, 5 top and 5 bottom layers, 20 % gyroid, and PETG at 230–250 °C nozzle and 80–90 °C bed, within 5 h.
- These are consistent with the brief, and slice_plan.json matches them.

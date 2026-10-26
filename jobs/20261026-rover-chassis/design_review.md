VERDICT: PASS

# DFM review, round 3: 20261026-rover-chassis

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, cad_checks.py, renders/{iso,front,right,top,bottom}.png (regenerated with tools/render.py), print_requirements.json, slice_plan.json, round-2 design_review.md and strength.md, rover_frame.py, tools/hobby_parts.py (N20_100RPM, POLOLU_HUB_1996), assembly_plan.md, assembly_check.json, BUILD_GUIDE.md, deep reviews 04 and 01 (S9–S13), sprocket design_brief.md (concept C). library/lessons.md and materials.csv have no rows, so the fdm-design-rules defaults apply (HOLE_COMP +0.2).

Outputs are current: a fresh in-memory `build()` gives 131 834.40 mm³ and 154 × 92 × 40, identical to geometry.json. `mesh_check.check()` re-run in memory is identical to mesh_check.json (file not rewritten). `cad_checks.py`: all 39 checks pass.

Extra evidence:
- `is_inside` probes on `design()` (world frame; print z = world z − 8.68).
- A layer-by-layer support analysis of part.stl. It ray-casts a 0.1 mm grid at 0.2 mm layers and flags cells with no solid within 0.275 mm in the layer below.
- Close-up renders of the nacelle, trough and buttress (scratchpad).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 154.0 × 92.0 × 40.0 (nacelles to \|y\| 46); fits_bed true, margin 5. With the margin, 164 × 102 on 250 × 210 |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight true, min_z 0.0 (geometry.json and the fresh build) |
| 3 | Orientation | PASS | Floor down, open top up, as the brief says. iso.png and front.png show the tub; top.png and bottom.png show the housings and nacelles at the rear of each side wall |
| 4 | Load paths vs layers | PASS (justified) | The brief justifies the wall-root moments across the layers: 4.5 walls, Ø26 bosses with r1.5 rims, BOSS_IN 5.5, 3 mm floor fillets, 1.5 strips. The round-3 paths run in the layer plane: the housing and nacelle are cantilevers along Y; the gearbox torque bears on 45° pocket faces; the jack-screw thrust is horizontal. Insert pull-out runs along Z, but each Ø10 column is merged full height into the walls: the rear pair into the corners, the front pair into the side wall, idler block and buttress (§1 "wide base"). Each sees 3.2 N per screw (lid spec §4) |
| 5 | Bed contact | PASS | 11 540.5 mm² (mesh_check). PETG is not a warping material. Use a glue release layer on smooth PEI (preflight) |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS (note) | overhang_pct 0.62 (377.9 mm²), all flat ceilings: tie-tunnel roofs (z 5.8, 4.0 span), idler-slot hull roofs (z 14.55, 8.0 between the 45° teardrop flanks), nut-trap roofs (z 15.0, 3.46, and the 11.46 × 2.6 idler nut slot). Largest bridge 8.0 mm. All other down-facing faces are exactly 45° (1 389.6 mm² at 45 ± 1°): pocket roofs, nacelle undersides, teardrops, strips. Layer analysis: no floating island anywhere. The only new unsupported start is the nacelle's bottom edge: at print z ≈ 1.2, a 0.3 × 3.7 mm strand hangs from the housing face, reaching 3.8 mm; every later layer stays inside the 45° allowance (R2) |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (note) | WALL 4.5, FLOOR_T 2.5. Nacelle 2.0 normal to its faces (2.83 per layer; cad_checks). Housing round the pocket: 11.2 − 8.06 = 3.14 at the side vertices, 3.94 under, 4.44 over. Trough cheeks 4.06 and 5.46 (probes at y 20, 28, 32). Jack pilot: 2.0 to the buttress inner face, 2.52 above its tip. Insert columns: ≥ 3.0 round each Ø4.0 hole (probe at 5° steps). The skin is the one wall under 1.8: 1.00 mm (probe y 45.0–46.0), two lines. It is above 0.9, its thickness is fixed by the stack-up (gearbox face 45.0, thrust washer 46.0–46.5, hub 46.5), and it carries only axial thrust (R3). thin_wall_warnings empty |
| 8 | HOLE_COMP, teardrops | PASS | HOLE_COMP (l.44) on every fit (geometry.json, cad_checks): bolts Ø3.6, skin hole Ø4.7, jack pilots Ø2.8, sensors Ø16.6, nut AF 6.0 (l.135), pocket 12.4 × 10.4 (GB_CLR + HOLE_COMP, l.54–56). Insert holes Ø4.0 have no compensation on purpose: §4 maker's size, stated in spec §3 (R4). Horizontal holes point up (arc 270° in geometry.json; right.png; close-ups): bolt holes, slot ends, skin hole, jack pilots and sensor holes are teardrops (l.252, 259, 264, 269, 278). The pocket is a 45° diamond; the tunnel and nut traps are flat-top |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(outer, FLOOR_Z, 0.4)` (l.203) runs on the tub, both housings and their strips before any cut. bottom.png shows the bevel round the outline and the housings. The strap slots, cut after it, are clearance slots |
| 10 | Internal corners on load paths | PASS (note) | Filleted or stripped: floor 3 mm 45° strips (l.207–211); road-wheel bosses with r1.5 rims (l.183), a 1.5 × 45° collar over the top half (l.184–186) and strips below (l.187–188); idler block (l.229–233); cradle (l.218–221); housing (l.155–158). Two new roots are sharp, both lightly loaded (R1): the jack-screw buttress (probes empty at (108.15, 27.85, Z_A) and at its front, rear and inner base edges) and the nacelle-to-housing joint. My estimate for the buttress at the 29.8 N reverse stall: ≈ 0.8 MPa nominal, in the layer plane, ≤ 2.7 MPa if only the 4 mm band at the thread carries it; × Kt 3 ≤ 8.2 against 25 MPa. Its base takes almost none: it is a 9.5 mm cantilever against a 2.6 mm path to the idler block. The nacelle root sees ≈ 0.6 MPa at the 5 cm corner (59.5 N × 3 mm on the diamond ring, Z ≈ 300 mm³) |
| 11 | Fasteners (§4) | PASS | Nut traps: 5.8 AF printed (nominal + 0.3) × 2.6 for a 2.4 nut, flats up. Washers under every axle-bolt head: ISO 7089 on the road wheels, DIN 9021 on the idlers (spec §2). The idler is held by a positive stop (jack screw), not by PETG preload. Inserts: Ø4.0 hole (§4: 4.0–4.2); Ø10 boss ≥ 2 × the ≈ 4.6 mm OD of a typical M3 × 5.7 insert (spec §2 gives no OD); 6.5 deep for 5.7 (0.8 mm melt sump). The jack screw self-taps a Ø2.6 pilot with 6.5 mm of thread and is only turned to re-tension (brief risk) |
| 12 | Spec §3 dims are named parameters | PASS | AXLE_DX, IDLER_SLOT, Z_A, MOTOR_FACE_Y 45.0, SKIN 1.0, HOUSING_OUT 4.0, BOSS_IN 5.5 come from rover_frame.py, commented. Also commented in model.py: POCKET_HX/HY 6.2/5.2 (l.55–56), NACELLE_R with its assert (l.59–61), BOSS_HOLE_D (l.65), BOLT_D, NUT_AF/CLR/DEPTH (l.47–48), JACK_PILOT 2.6 and JACK_Y 25.4 (l.81–82), INSERT_D/INSERT_DEPTH 4.0/6.5 (l.76). Every value matches spec §3, and cad_checks.py proves each one |
| 13 | Service temp ≥ 20 °C below softening | PASS | 40 °C against ≈ 70 °C for PETG. config/printer.json `materials_on_hand` is empty; confirm PETG at slicing (spec §6) |
| 14 | Lessons | N/A | library/lessons.md has no entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |
| 16 | Fits and assembly (cross-part) | PASS | Pocket 12.2 × 10.2 printed on a 12 × 10 gearbox, 0.1 a side, a §3 locating fit. Skin hole Ø4.5 printed over the Ø4 × 0.8 boss. The can and the gearbox sit 0.1 off the same V planes, so the zip tie lowers the motor ≤ 0.14 mm without tilting it. assembly_check.json: 154 bodies, 0 collisions, no exemptions; nacelle 1.5 mm and housing 1.0 mm from the links; 11 mm gearbox and 9/10 mm shafts fit; jack screw has 6.5 mm in the buttress at every slot position, socket outside, key path clear; 2.0 / 4.2 mm of thread past the nylocs, wall nuts engaged |

## Required fixes

None.

## Round 2 fixes checked

1. **Idler slot hull up to the teardrop tips: done.**
   - The box top is now Z_A + r·√2 = Z_A + 2.55 (l.265–266), so the bolt has 1.05 mm of headroom.
   - mesh_check now shows one 8.0 × 7.4 bridge per side at z 14.55, anchored on both 45° flanks. The layer analysis reaches 3.9 mm, half the span.
   - The floating 22–26 mm² patch is gone.
2. **Cheeks standing on the cradle: done, by a different route.**
   - The trough walls are the cradle block itself: CRADLE_HALF_X 12.1 from the floor (l.217), 4.06 / 5.46 thick.
   - The rear-stop posts are gone; the motor is located by its face.
   - mesh_check has no z 6.99 ledges, and the layer analysis finds nothing unsupported in the cradle.
3. **Fillets where the bosses meet the wall: done.**
   - The Ø26 bosses have 1.5 × 45° collars and strips (cad_checks "45° collar at the wall").
   - The idler block has strips along its top and at the front wall.
   - The journal boss is gone.
4. **Idler positive stop: done.**
   - (a) An M3 × 20 jack screw in a buttress bears on the bolt head. assembly_check finds it clear at both slot ends, with 6.5 mm of thread.
   - (b) The DIN 9021 washer is in spec §2 and the BOM.
   - (c) Pen marks are in spec §8, tests 1 and 2.
   - The BUILD_GUIDE now says the inside part is the head (step 3), and tensions with the jack screw, snugging the head only "to keep the bolt square" (step 8).

Round-2 recommendations:
- R1 (inserts): done.
- R2 (11.46 mm idler nut-slot roof): unchanged, and still prints. It is anchored along its inner edge and both ends; the layer analysis reaches 2.4 mm.
- R3 (toggle): moved to the lid; cad_checks finds no switch hole.
- R4 (assembly_check): rewritten with heads, shanks and no exemptions.
- R5 (slice plan): still open; see the note below.

## Printing notes vs print_requirements.json

The brief's printing notes:
- floor on the bed;
- a 0.4 bed chamfer.

print_requirements.json asks for:
- PETG;
- 5 perimeters;
- 5 top and 5 bottom layers;
- 30 % gyroid;
- layers ≤ 0.2;
- 230–250 °C nozzle, 80–90 °C bed;
- ≤ 12 h.

Nothing in the brief contradicts these. elefant_foot_compensation is not required here; the profile and the plan both set 0.2, and no fit sits at the first layer. The requirements are consistent with the brief and the strength basis.

## Note for slicing (not a DFM item)

slice_plan.json overrides `perimeters` 4 and `fill_density` 25 %, against the required minimums of 5 and 30 %. The validator will fail it at SLICE, so the slicing-lead must raise both before slicing. The requirements themselves are right.

## Recommendations (not blocking)

- **R1. Buttress and nacelle roots.**
  - For consistency with the rest of the tub, add 1.5 × 45° strips at the buttress's vertical corner with the idler-block face (x 108, |y| 28) and along its front-face base (x 108, |y| 22–28).
  - Tell strength round 3 that both roots are sharp (use Kt ≈ 3).
  - Also tell it that the jack screw has 6.5 mm of thread in the buttress at |y| 25.4, not the 11 mm through the idler block that strength round 2 sized (SF 10.9).
- **R2. Nacelle underside.** The nacelle's V bottom starts in mid-air at print z 1.11. Its first layer is a 0.3 × 3.7 mm strand hung from the housing face. It will print, but may droop a little. Look at the nacelle underside on the first print: any droop comes out of the 1.5 mm link clearance (assembly_check `nacelle_to_links_min_mm`).
- **R3. Skin.** Ask strength round 3 to check the 1.0 mm skin in plate bending under an inward push on the Ø7 thrust-washer ring. That is the 3 N skid-steer side load of spec §4; my rough estimate is 1–2 MPa. Build step 6 already backs the skin with the gearbox face while the hub is set.
- **R4. Insert holes.** Ø4.0 in CAD with no compensation prints at about Ø3.8, by the project's own +0.2 default. That is fine for heat-setting, but spec §3 gives "Ø4.0 ±0.1". Either model Ø4.2 so it prints about 4.0, inside §4's 4.0–4.2, or state the expected printed size in the spec so inspection doesn't reject it.

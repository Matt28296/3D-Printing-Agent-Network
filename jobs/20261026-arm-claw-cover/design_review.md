VERDICT: FAIL

# DFM review: 20261026-arm-claw-cover (round 2)

Reviewer: dfm-reviewer (independent) · 2026-10-26 · DESIGN gate, round 2 (round 1: FAIL).
Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, print_requirements.json, renders/*.png (regenerated; all 5 viewed), round-1 design_review.md and strength.md, ../20261025-robot-arm-assembly/claw_frame.py, claw_sequence_check.py/.json, assembly_plan.md, BUILD_GUIDE §4, deep review 03 SYS-01 (fix A), tools/hobby_parts.py, library/ (no lessons, no material rows, so skill defaults apply).

The outputs are current. `build()` rebuilt in memory gives 22 526.38 mm³ and 13 366.77 mm², the same as geometry.json, and mesh_check re-run in memory reproduces mesh_check.json. Extra evidence:
- a layer-by-layer slice of part.stl: 0.2 mm layers on a 0.04 mm raster, each layer compared with the one below;
- per-layer connectivity: which regions of a layer are joined to the rest;
- a per-layer 0.9 mm thin-feature test;
- probes along print Y.

Print frame: (X, Y, Z) = claw G (x, −z, y + 32), so G +y is up.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits the bed with a 5 mm margin | PASS | 37.85 × 55.5 × 64.0 mm, `fits_bed: true` |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, `min_z_mm: 0.0` |
| 3 | Orientation matches the brief | PASS | Standing on its −y end (`TO_PRINT = Rot(90, 0, 0)`): bottom.png shows the C profile and the tie on the bed. right.png shows slot A rising from the bed to its 45° roof, the pass-through with its 45° top, and slot B open at the top |
| 4 | Load paths vs layers | **FAIL** | The brief still says "bending of the front plate and the top wall runs along the layers (their planes are vertical in print)". With G y up, these paths bend across the layers: (a) the strip under slot B (z −4…5.75) spans y between slot B's closed end (y −5) and the +y front screw (y 24), and carries neck B's bearing; (b) the top wall spans y between the two top screws (y −23, 14) under rack A's lift (spec §4 row 1); (c) the lower half of the front plate carries rack B's forward thrust and the neck loads along y to the tie (y −32…−24, print z 0–8) and to the −y front screw. Round-1 fix 1 asked the brief to name these, and that wasn't done. The tie post and web themselves are loaded in the bed plane, along the layers, as the brief says |
| 5 | Bed contact | PASS | 542.2 mm² on a 64 mm-tall part, with `brim_width` ≥ 5 now required in print_requirements.json (round-1 R1) |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | **FAIL** | **Two regions of the front plate start in mid-air.** Slot A (open at −y), the Ø22.8 pass-through and slot B (open at +y) cut through the plate between z 5.75 and 48.5 for y −5…6.5. The cut-backs then end two regions of the upper half with flat ends that are ceilings in print. (a) **Beside slot A's roof, above the pass-through:** first layer at print z 38.5 (G y 6.5, cres_a's end), 1.64 × 5.0 mm, 8.2 mm², at G z 36.62–38.26. It isn't joined to the rest until print z 43.1, at slot A's apex. (b) **Beside slot B, below the pass-through:** first layer at print z 39.1 (G y 7.0, cres_b's end), 2.08 × 5.0 mm, 10.4 mm², at G z 16.26–18.34. It isn't joined until print z 47.7, at the pass-through's apex. In their first layers nothing is under them or beside them. The layer check flags both as islands, with the nearest supported material 11.7 and 12.6 mm away, and the connectivity check shows them separate from the rest for 4.6 and 8.6 mm of height. mesh_check lists their first faces as "bridges" of 1.63 and 2.0 mm, but neither has an anchor. Unsupported, the slicer extrudes them in mid-air. Sagging or dragged PETG then ends up in slot B, where neck B runs with 0.25 mm, or in the pass-through, where the pinion has 0.45 mm. **Everything else passes:** slot A's roof and the pass-through top are 45°, with r 1.5 apexes leaving flats of 0.6 mm or less; slot B's closed end is a floor; the end of the corner fillet (print z 41) is a 2 × 2 mm triangle anchored on two sides; the tie prints up from the bed. overhang_pct 0.32 |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (note) | Front plate 5, top wall 3, lip 4; tie post 4 × 8; web 10.5 × 8 × 16. Strip under slot B 9.75 deep. The slivers beside the pass-through start 1.63–2.0 wide and widen. Top hole to the top wall's rear edge 4.95. `thin_wall_warnings` is empty, and the per-layer 0.9 mm test finds nothing. **Note:** the +y front-screw clearance hole (Ø3.0 at y 24, z 3) leaves **1.25 mm CAD** (1.26 measured on part.stl) to slot B's lower edge at z 5.75, which guides neck B. It sits under the screw head and takes only neck B's share over the 3 mm hole: ≈1.6 MPa across the layers by reviewer estimate. Accepted like round 1's 1.2 mm clearance-hole walls (R1) |
| 8 | HOLE_COMP; horizontal holes teardrop or flat-top | PASS | Pass-through Ø22.8 (ACCESS_D 22.6 + HOLE_COMP) with a 45° teardrop top; top holes Ø3.6 (M3); front holes Ø3.0 (M2.5). All are teardrops pointing up in print (front.png, right.png), and measure_holes gives 270° arcs |
| 9 | Bottom edges chamfered | PASS | The openings are cut before the 0.3 mm bed chamfer (model.py l.126–139). At print z 0.05, slot A spans print Y −48.75…−38.01; at z 0.5 and above, −48.51…−38.25. So the mouth is chamfered (round-1 fix 2) |
| 10 | Internal corners on load paths filleted | PASS (advisory) | **Filleted:** slot B's closed end, r 2; the junction of slot A's roof and the top wall, r 2 (apex r 1.5); the front plate / top wall corner over y 9–32, r 2 (strength fixes). **Lip front root, sharp:** a channel corner where rack A's square edge runs, accepted as in round 1. The lip is now a 4 mm cantilever wall, though, so strength should check that root at Kt 2.5 (R2). **Web-to-front-plate corners (x 32.85, z 19.25 and 35.25), sharp:** low stress, ≈0.2 MPa nominal if the whole thrust went through the 8 × 16 web. They can't take more than ≈0.8 mm of fillet before reaching the racks' tips (1.15 mm away) |
| 11 | Fasteners per §4 | PASS | M3 × 10 (or M3 × 18 with the camera mount) through Ø3.6 into the frame's 14 mm pilots. M2.5 × 12 pan heads through Ø3.0 into the frame's 10 mm pilots. The heads clear jaw B's finger: claw_sequence_check gives `front_screws` 0 mm³ on every path and over the stroke |
| 12 | Spec §3 dims are named parameters | PASS | X_F0 32.85, Z_TOP0 48.5, RAIL_X1 22.35, ZA0/ZA1 38.25/48.5, ZB0/ZB1 5.75/16.25, R_PASS 11.4 (22.6 printed). All are named, with comments, in model.py or claw_frame.py |
| 13 | Service temperature | PASS | 40 °C against PETG at ≈70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ |

## Required fixes

1. **Give both hanging regions a supported start (item 6).**
   - **Requirement:** the first layer of each region must sit on material, either support or the part:
     - region (a): print z 38.5, 1.64 × 5 mm;
     - region (b): print z 39.1, 2.08 × 5 mm.
   - **Route (a), support, justified in the brief.** Two ways:
     - a breakaway rib modelled in each cut-back channel. Each rib stands on the lower half below it: the slot-A-side channel ends on solid at print z 25, the slot-B-side one at print z ≈25–27. Each stops one 0.2 mm layer under its region;
     - or slicer support enforcers at the two spots, declared in print_requirements.json and slice_plan.json.

     Either way, BUILD_GUIDE §4 step 9 must say to remove them before the jaws go in.
   - **Route (b), change the openings,** so that each region is joined to material in the layer below its first layer. A 45° end or a different cut-back length won't do it: the two regions join the rest only at slot A's apex (print z 43.1) and the pass-through's apex (print z 47.7). The connection has to come from the lower half, or the slots, pass-through and cut-backs have to be laid out differently.
   - **Then:** re-run a layer-by-layer island check (no region may start without material under it) and claw_sequence_check.
   - **Rule:** §2 (overhangs ≤ 45° without support; a bridge needs an anchor at each end and ≤ 10 mm); checklist item 6 ("supported and justified").
   - **Evidence:** item 6. In right.png, the two regions are the pieces either side of the pass-through's 45° top: one between it and slot B, one between it and slot A's roof. Each ends in a short flat edge at print z ≈38.5–39.
2. **Name the across-layer load paths in the brief (item 4; round-1 fix 1, not done).**
   - **Change:** in design_brief.md's orientation section, replace "bending of the front plate and the top wall runs along the layers" with item 4's paths (a)–(c).
   - **Strength:** strength-analyst checks them with the ×0.5 across-layer allowable. Round 1 already did this for the slot-B strip, so this records what the strength check relies on.
   - **Geometry:** no change is expected from this fix.
   - **Rule:** §1 (trace every load path; record the trade-off in the brief).
   - **Evidence:** item 4.

## Round-1 required fixes

| Round-1 fix | Status | Evidence |
|---|---|---|
| 1. Name the across-layer cases in the brief | **Not done** | The brief repeats the round-1 wording (item 4, fix 2) |
| 2. Chamfer slot A's mouth | Done | Openings cut before the bed chamfer; the mouth is 0.24 mm wider per side at print z 0.05 (item 9) |
| R1. `brim_width` 5 in print_requirements.json | Done | `min.brim_width: 5` |
| R2. Top wall back to x 0 | Done | TOP_X0 0; top-hole ligament 4.95 |
| R3. Slot-end parameter | Done | SLOT_A_END 6.5, SLOT_B_END 5.0 |
| Strength 1–3: FRONT_T 5, r ≥ 2 at the slot ends, deeper strip under slot B | Done | FRONT_T 5; slot B r 2, slot A 45° roof with r 2; FRONT_Z0 −4 (strip 9.75 deep); r 2 corner fillet |

Other round-2 changes checked: the SYS-01 fix A pass-through (Ø22.6 printed, 0.45 mm radial to the pinion; claw_sequence_check's swept pinion gives 0 mm³), the tie post and web (they print from the bed; top at print z 8), and the lip as a 4 mm wall. The two islands in item 6 are what this layout costs in this print orientation.

## Recommendations (not blocking)

- R1. The 1.25 mm ligament between the +y front-screw hole and slot B (item 7) is the thinnest part of the slot-B strip. Strength-analyst should include it in that strip's check.
- R2. For strength-analyst: the lip is now a 4 mm cantilever wall off the top wall, with a sharp front root, loaded by rack A's back thrust. At wide openings rack A's back end bears near the lip's −y end, where the tie post joins it. The bending stays in the layer plane, but the root needs the Kt 2.5 check. The frame's rail carries the same thrust, but across the layers and with a free end (frame review, fix 2).
- R3. Process: slice_plan.json and the other slice files in this folder date from before round 1; its rationale still says a 203 mm² end face. Re-slice after the DESIGN gate passes.

VERDICT: PASS

# DFM review, round 6: 20261026-rover-chassis

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26

**Inputs:**
- this job: spec.md, design_brief.md (round-6 section), model.py, geometry.json, mesh_check.json, cad_checks.py, log.md, round-5 design_review.md and strength.md;
- renders/{iso,front,right,top,bottom}.png, rebuilt with `tools/render.py` and looked at;
- git cc1b341 (the round-6 change) and its parent (the round-5 part.stl, for a before/after layer comparison);
- from the assembly job: assembly_check.json and assembly_plan.md (round 6).

library/lessons.md has no entries, and there is no materials row, so the fdm-design-rules defaults apply.

**What round 6 changed, checked against the diff (cc1b341):**
- model.py: one parameter, `STOP_W` 1.5 → 2.0 (l.123), plus comments. `_nut_plate_seat` (l.191–203) is unchanged. It builds the stops from `NUT_PLATE_X[0] − STOP_W` to `NUT_PLATE_X[1] + STOP_W`, so the inner faces stay at x 108 and 129 and the lip lengthens with the stops to x 106–131.
- The drop-in assert (l.125) is unchanged and still holds: 20.6 ≤ 21.0 − 0.4.
- cad_checks.py: three round-6 probes added. Two round-5 void probes, at x 106.4 and 130.6, were removed because the stops now fill those points.
- The brief has a round-6 section, and assembly_plan.md gives the new width. No other geometry changed.

**Outputs are current.**
- A fresh in-memory `build()` gives 131 935.52 mm³, 154.0 × 92.0 × 40.0, one solid, min Z 0. That is identical to geometry.json, and +27.1 mm³ on round 5 (2 sides × 2 stops × 0.5 × 1–2 × 10.9, plus the longer lip).
- part.stl is 131 929.8 mm³, watertight, one body.
- `tools/mesh_check.py` re-run: mesh_check.json is unchanged (git shows no diff): overhang 0.53 % (327.9 mm²), bed contact 11 540.5 mm², widest bridge 8.0, no thin walls, fits the bed.
- `cad_checks.py`: 53/53 PASS, exit 0.
- assembly_check.json: 160 bodies, 0 collisions. Chassis to links is still at least 1.0, at (−8.5, 42, 9.6) by the housing, not at the stops.

**Extra evidence** (my scripts, in the scratchpad):
- **Layer-by-layer support analysis** of part.stl round both seats: x 100–135.5, |y| 35–41, 0.05 mm raster, mid-layer planes every 0.2 mm. It flags any cell more than 0.2 mm from the layer below. I ran it on the round-6 STL and on round 5's.
- **Ray probes** along X and Y through both stops, the lip and the fillet join, on both sides.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 154.0 × 92.0 × 40.0, the same as before: the stops are inside the envelope. fits_bed true |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight true, min_z 0.0 (geometry.json and the fresh build); the STL is one body |
| 3 | Orientation | PASS | Floor down, open top up (iso.png, front.png). front.png shows the seat at the front of each side wall: the lip under it and a stop at each end, the front stop running into the corner's curve. right.png shows the front stops at the corner, 1 mm proud, with the lip's 45° underside below them |
| 4 | Load paths vs layers | PASS (justified) | Unchanged from round 5. The nut plate bears flat on the outer face (\|y\| 38), in compression along Y in the layer plane. The stops take the plate's X drag on a vertical root plane, so the stress runs along the layers (strength B18). Widening them adds no across-layer load |
| 5 | Bed contact | PASS | 11 540.5 mm², unchanged; the seat's lowest point is print z 3.8, clear of the bed. PETG is not a warping material: glue release layer on smooth PEI |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | overhang_pct 0.53 (327.9 mm²), unchanged. The lip's longer 45° underside adds nothing over 45°. The stops are vertical prisms standing on the lip, from Z_A − 5.7, inside the lip's 1.0 face (seat l.200–202). **Layer analysis: nothing new floats** (see "Round-6 checks"). Largest bridge 8.0, the bolt-slot hull ceiling at print z 14.7, unchanged |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | Stops are now **2.0 along X** × 1.0 proud × 10.9 tall: 4+ extrusion widths along X, and ≥ 0.8 proud like the lip. The lip is 1.0 proud on a 2.0 root. thin_wall_warnings empty. The 8.0 mm of PETG between the plates is unchanged (cad_checks; round-5 probes) |
| 8 | HOLE_COMP on fits; horizontal holes teardrop or flat-top | PASS | No new holes. The seat's X fit is unchanged: 21.0 CAD between the stops' inner faces (X-probes: faces at 108.0 and 129.0 on both sides) for the 20.6 plate. The bolt slot is unchanged |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges` unchanged; the seat doesn't reach the bed (bottom.png) |
| 10 | Internal corners on load paths | PASS (note) | Unchanged from round 5. The stops' roots are sharp. Strength checks them with Kt 2.5 (B18), and they pass at 4.88 in round 6. The recess floor edge is still sharp: strength's drop row at 3.02 is there, and the brief declines the optional chamfer. That is a strength call |
| 11 | Fasteners (§4) | PASS | Unchanged. The wall nut sits on a Ø9 washer on the steel plate. No preload is counted on. The nut is held with a spanner at step 3, and the stops (\|y\| ≤ 39) don't reach the nut's band (\|y\| 40.8–43.2) |
| 12 | Spec §3 dimensions are named parameters | PASS (note) | `STOP_W` 2.0 (l.123) has its source comment (strength round 5 FIX). `NUT_PLATE_X`, `LIP_*` are unchanged. The spec §2/§3 seat rows give the stops' inner faces (x 108 / 129; "stop gap ≥ 20.7 printed"), which are unchanged; they don't state the width, so nothing there is stale. The brief's seat row says 2.0 |
| 13 | Service temp ≥ 20 °C below softening | PASS | 40 °C against ≈ 70 °C for PETG |
| 14 | Lessons | N/A | library/lessons.md has no entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |
| 16 | Fits and assembly (cross-part) | PASS | Inner faces unchanged, so the plate fit, the plate slots against the bolt's travel, and the washer and nut clearances are all exactly as in round 5. The stops stay 4.0 inboard of the links (cad_checks round-6 probe; assembly check 0 collisions). The round-5 G1 (ball-end key) is now in BUILD_GUIDE (Tools l.66, step 3 l.136) |

## Required fixes

None.

## Round-6 checks in detail

### The wider stops print without support

| Probe (world, both sides identical) | Result |
|---|---|
| X at \|y\| 38.5 and 38.95, Z_A − 3.0 / 0 / + 3.0 / + 5.1 | solid **106.0–108.0** and **129.0–131.0** only |
| X at \|y\| 38.5 and 38.95, Z_A − 5.6 and − 5.3 (the lip) | solid 106.0–131.0 |
| X at \|y\| 38.5, Z_A + 5.3 | void (the stops end at Z_A + 5.2) |
| Y at x 106.05, 107.0, 107.95, Z_A | solid from the wall to 39.0, so the rear stop is fused to the wall over its whole 2.0 |

- **Layer analysis.** Each stop's first cells at \|y\| 38–39 are the lip's, at print z 4.9. Each stop is fully solid over its 2.0 × 1.0 footprint from print z 5.9 to 17.1 (Z_A − 6.1 to + 5.1). It grows straight up out of the lip, with no start of its own.
- **The only flags round the seat** are single raster cells at the lip's exact-45° underside edge: print z 4.9–5.5, x 129.75–130.95, \|y\| 38.1–38.7, 1 to 7 cells per layer.
  - Each is at most 0.25 mm from the layer below, which is one 0.05 raster step over 0.2.
  - **The round-5 STL gives the same flags at the same edge** (x 129.5–130.3, 0.25 mm). They are raster quantisation on a true 45° face, not a new overhang.
  - mesh_check, which counts only faces over 45°, is unchanged at 327.9 mm². So the 45° underside under the extra 0.5 mm at each end added nothing over 45°.
- The other starts in the window are unchanged from round 5:
  - the bed chamfer's corner diagonal at z 0.3 (≤ 0.21 mm);
  - the bolt-slot hull ceiling at z 14.7 (the 8.0 mm bridge, anchored on the teardrop flanks).

### The front stop joins the r6 fillet

- At x 131.0 the corner fillet's face is at \|y\| 37.66. The probe at x 131.05 finds solid only to ±37.64, the fillet's face just past the stop's end.
- The stop starts at \|y\| 37 (seat l.197), so it is buried 0.66 mm into the fillet there. Its outer face is 1.34 proud of the curved surface.
- Y-probes at x 129.05, 130.0, 130.5 and 130.95 are solid from inside the wall continuously out to 39.0 (cad_checks round-6 probe: \|y\| 37.0–38.95 solid at x 130.95, three heights).
- From x 130.5 the stop also overlaps the front wall's own x-range (x 130.5–135), so at x 130.95 the section is solid straight across the front wall (−39 to 39).
- No gap and no floating sliver anywhere along the front stop.

### Clear of the links

- Nothing is solid past \|y\| 39 between x 105 and 132 (cad_checks round-6 probe; my X-probes start the seat at 106.0 and stop it at 131.0). The links' inner edge is at \|y\| 43, so the clearance is **4.0 mm**, as claimed.
- Ends: the rear stop ends at x 106 on the flat outer face. The road wheel axle at x 80 and the housing (x ±11.2) are far from it.
- The front stop ends at x 131, 4 mm short of the front face (x 135). It sits inside the outline of the corner's r6 when seen from above (top.png).
- assembly_check.json: 160 bodies, 0 collisions. The chassis-to-links minimum is still 1.0, at the housing.

### The plates still drop in

- The inner faces are unchanged: X-probes find the stops' faces at exactly x 108.0 and 129.0, both sides. That is 21.0 CAD for the 20.6 plate (assert l.125), printing about 20.8–20.9.
- Spec §3 asks for a printed gap of at least 20.7, and filing is in BUILD_GUIDE §1 step 5. This is the round-5 table, unchanged: 0.0–0.5 printed clearance for 20.4–20.8 hand-cut plates.
- The plate goes in from outside (−Y), over the lip, between the stops. The stops are still 1.0 proud, half the plate's 2.0, so the stack is unchanged too:
  - the Ø9 washer clears the stops by 0.72–1.17 for 1.72–2.17 sheet;
  - the idler hub start is 43.42–43.87.
- The plate's clear space x 108.05–128.95, \|y\| 38.05–40, Z_A ± 5.15 is still empty (cad_checks).

## Round-5 evidence carried over (unchanged by round 6)

These items don't depend on `STOP_W`, and the probes above show the geometry they rest on is the same.

- **Lip.** Top at Z_A − 5.2, a layer boundary (print z 6.8), so the plate's seat height is exact. A 1.0 face, then a 45° underside: from (39, Z_A − 6.2) to (37, Z_A − 8.2).
- **Bolt slot and wall.** The slot is x 114.2–125.8, Z_A − 1.8 to + 2.55. It has at least 5.6 mm of PETG to any free surface, and 8.0 mm between the plates elsewhere.
- **Plates and slots line up.**
  - In Z: both plates rest at Z_A − 5.2, and the bolt clears both plate slots by 0.15 below and 0.2–0.25 above.
  - In X: the bolt's travel of 115.75–124.25 is covered by the plate slots in every plate position (assembly_check `covers_slot_travel`).
- **Hand access.**
  - Step 3: a spanner on the nut outside, at \|y\| 40.8–43.2. The stops reach only to \|y\| 39, so a spanner on the nut still clears them.
  - Step 3 snug: ball-end key, now in BUILD_GUIDE.
  - Step 7: the nyloc outside, the head held from inside with a plain key.
- **Whole-part unsupported starts.** Round 5's whole-part analysis is carried, not re-run. I re-ran it only in the window round both seats, where it matches round 5. The 16 starts:
  - 4 bed-chamfer corner diagonals;
  - the 2 nacelle V-bottoms at z 1.3;
  - 4 zip-tie tunnel roofs at z 5.9 (4 mm bridges);
  - 2 bolt-slot hull ceilings at z 14.7 (8.0 mm bridges);
  - 4 road-wheel nut-trap roofs at z 15.1.

  Round 6 changed nothing outside x 106–131, \|y\| 37–39. mesh_check is identical.

## Round-5 recommendations: status

| Item | Status | Evidence |
|---|---|---|
| G1: step 3 ball-end key | Resolved | BUILD_GUIDE Tools l.66, step 3 l.136 |
| R1: printed targets in spec §3 | Resolved for the seat row ("stop gap ≥ 20.7 printed … file the stops if it doesn't", l.40). The head-plate recess row is not yet written the same way (minor) | spec.md l.40 |
| R2: insert holes' printed size; slice-plan overrides | **Still open, not DFM-blocking.** spec §3 still says "Ø4.0 ±0.1" (l.41), against about Ø3.8 printed. slice_plan.json still has perimeters 4 and fill 25 %, against print_requirements' 5 and 30 %. The validator will fail it at SLICE unless it is raised first | slice_plan.json l.6, l.9 |
| R3: process | Partly open. log.md now has the round-5 change line (13:58), but **has no line for the round-6 model change** (cc1b341 didn't touch log.md; the last line is the 14:22 approval). spec.md's header still says "round 4 by design-lead" | log.md; spec.md l.3 |

## Notes

- The round-5 notes for the strength review still apply and are unchanged by round 6:
  - the idler's axial position depends on the nut-plate thickness and the hardware stack (−0.68 to +0.32 mm);
  - the running washer drags on the snug wall nut.
- Spec §8 says "strength rounds 2–5" in the proof-test heading. It could say 2–6, but the tests themselves already match round 6 (see strength.md).
- Printing: PETG, 5 perimeters, 5 top and 5 bottom layers, 30 % gyroid, layers ≤ 0.2, 230–250 °C nozzle, 80–90 °C bed. That matches the brief (floor on the bed, 0.4 bed chamfer). slice_plan.json has to be raised to meet it (R2).

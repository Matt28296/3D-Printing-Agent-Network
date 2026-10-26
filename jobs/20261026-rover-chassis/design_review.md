VERDICT: PASS

# DFM review, round 5: 20261026-rover-chassis

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26

**Inputs:**
- this job: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, cad_checks.py, print_requirements.json, slice_plan.json, log.md, round-4 design_review.md;
- renders/{iso,front,right,top,bottom}.png, rebuilt with tools/render.py and looked at;
- rover_frame.py (PLATE_T, IDLER_PLATE, NUT_PLATE, PLATE_SLOT, PLATE_SLOT_FROM, WASHER_WIDE, NUT, IDLER_HUB_Y0);
- from the assembly job: assembly_check.json (round 5), BUILD_GUIDE.md (§1 plates, tools; §3 steps 3, 4, 7, 8; Service);
- git b7eb995 (the round-5 model change) and 55c2196 (round-5 spec).

library/lessons.md has no entries, and there is no materials row, so the fdm-design-rules defaults apply (HOLE_COMP +0.2, walls print 0.1 inward a face).

**The round-5 claims, checked against model.py:**
- Nut slot deleted: no `_idler_nut_slot` or `NUT_SLOT_*` remain. The only cuts through the idler block and wall are the bolt slot's teardrops and hull (l.320–324) and the head-plate recess (l.326).
- Nut plate (rover_frame `NUT_PLATE` (20.6, 10.0)) on a seat, `_nut_plate_seat` (l.187–199), with these parameters:
  - `LIP_DZ` 5.2: lip top at Z_A − 5.2;
  - `LIP_OUT` 1.0 proud, `LIP_FACE` 1.0, then a 45° underside back into the wall;
  - `STOP_W` 1.5: end stops at x 106.5–108 and 129–130.5, up to Z_A + 5.2;
  - `NUT_PLATE_X` = (108, 129), with an assert that the plate drops in (l.121).
- Ø9 washer under the wall nut: rover_frame `WASHER_WIDE`, and `IDLER_HUB_Y0` = 38 + 2.0 + 0.8 + 2.4 + 0.5 = 43.7.
- Head-plate recess and jack screw unchanged. `_plate_recess`, `JACK_*` and `PLATE_RECESS_*` match round 4 byte for byte in the diff.

**Outputs are current.**
- A fresh in-memory `build()` gives 131 908.43 mm³, 154.0 × 92.0 × 40.0, one solid, min Z 0. That is identical to geometry.json.
- part.stl is 131 902.7 mm³ and watertight.
- `tools/mesh_check.py` re-run: mesh_check.json is unchanged (git shows no diff).
- `cad_checks.py`: 50/50 PASS, exit 0.

**Extra evidence** (my scripts, in the scratchpad):
- **Layer-by-layer support analysis of part.stl.** Mid-layer planes at 0.2 mm, raster 0.05 mm round both idler blocks and 0.1 mm over the whole part. It flags any cell more than 0.2 mm from the layer below. It is validated by finding the known road-wheel nut-trap roofs.
- **Ray probes along X, Y and Z** through the seat, stops, lip, slot and recess, on both sides.
- **Stack and fit arithmetic** from the model's own parameters, with real hardware tolerances.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 154.0 × 92.0 × 40.0; fits_bed true (164 × 102 with the margin, on 250 × 210) |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight true, min_z 0.0 (geometry.json and the fresh build) |
| 3 | Orientation | PASS | Floor down, open top up (iso.png, front.png). front.png shows the new seat round the idler slot on the outer face: the lip under it and a stop at each end, with no nut-slot mouth any more. bottom.png shows the lip's 45° undersides just proud of each side wall at the front |
| 4 | Load paths vs layers | PASS (justified) | The nut plate now bears flat on the wall's outer face (\|y\| 38), in compression along Y, in the layer plane, like the head plate on the recess's back face (\|y\| 30). The 8.0 mm of PETG between them is compressed along Y. The lip and stops only locate the plate; the bolt carries it in service. Nothing new loads across the layers |
| 5 | Bed contact | PASS | 11 540.5 mm², unchanged. PETG is not a warping material; use a glue release layer on smooth PEI |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | overhang_pct 0.53 (327.9 mm²). Lip underside exactly 45° (l.196: from (39, Z_A − 6.2) to (37, Z_A − 8.2)). Stops are vertical prisms standing on the lip (their base, Z_A − 5.7, is inside the lip's 1.0 face). **Layer analysis: no unsupported cell at the lip or stops on either side.** In x 98–136 the only unsupported start is the bolt-slot hull ceiling, 8.0 × 7.9 at print z 14.7, anchored on the teardrop flanks at both ends: largest bridge 8.0 (mesh_check: two 8.0 bridges at 14.55). The whole part has 16 starts: round 4's 18 less the two nut-slot roof strips (table below). Nothing floats on its first layer |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | PETG between the plates: Y-probes at x 110, 112, 118, 120, 126 and 128.5, from Z_A − 5.1 to + 5.3, both sides, find solid \|y\| 30.0–38.0 (8.0) wherever the slot isn't. Round the slot: front end (x 125.8) to the outer skin 8.9 at \|y\| 34 and 5.6 at \|y\| 37.5 (the r6 corner); below it 10.2 to the bed (z 8.68–18.88); above it 12.0 to the block top. The lip is 1.0 proud on a 2.0 root, and the stops are 1.5 × 1.0 proud: both are locators, ≥ 2 extrusion widths and ≥ 0.8. thin_wall_warnings empty. The round-4 feather edge at the trough is unchanged (round 4, note 1) |
| 8 | HOLE_COMP on fits; horizontal holes teardrop or flat-top | PASS | No new holes. The seat's X fit is explicit (l.113–114): 21.0 CAD between the stops for a 20.6 plate, the same as the recess. The bolt slot is unchanged (Ø3.6 CAD teardrops plus the hull to the tips, l.320–324) |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges` (l.259) is unchanged. The seat's lowest point is print z 3.8, clear of the bed (bottom.png) |
| 10 | Internal corners on load paths | PASS (note) | The seat's corners carry no load. The head-plate recess floor edge is still sharp. Strength's 3.02 drop row sits there, and its optional 1 × 45° chamfer is declined in the brief (Risks). That is a strength call; DFM has no objection to either |
| 11 | Fasteners (§4) | PASS | The wall nut sits on a Ø9 washer on a steel plate (§4 "washers or wide heads"), the head on a Ø9 washer on the head plate. No preload is counted on: the jack screw holds the tension, and strength checks the clamp with no clamp force left. The nut is not captive: a spanner holds it at step 3 (access below). Road-wheel nut traps unchanged |
| 12 | Spec §3 dimensions are named parameters | PASS (note) | NUT_PLATE_X, LIP_DZ, LIP_OUT, LIP_FACE and STOP_W (l.113–120) all have source comments; NUT_PLATE comes from rover_frame l.98. cad_checks proves the lip, the stops, the plate's clear space and the 8.0 mm of PETG. The spec §3 seat row's tolerance doesn't match what prints (R1) |
| 13 | Service temp ≥ 20 °C below softening | PASS | 40 °C against ≈ 70 °C for PETG |
| 14 | Lessons | N/A | library/lessons.md has no entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |
| 16 | Fits and assembly (cross-part) | PASS (one guide correction, G1) | The plates fit the seat for 1.72–2.17 mm stock, and both plate slots cover the bolt's whole travel (tables below). assembly_check.json (round 5): 160 bodies, 0 collisions; idler and jack screw clear at both slot ends; 7 teeth engaged. The nut is easy to reach at step 3. **But step 3's "long arm of the 2.5 mm key into the bolt head" cannot be done with a plain key: see G1** |

Whole-part layer analysis, every unsupported start (print z):

| z | Where | Size | Furthest from support | Verdict |
|---|---|---|---|---|
| 0.3 | 4 housing corners at the bed chamfer | 0.01 mm² | 0.28 | diagonal of a 45° chamfer; fine |
| 1.3 | nacelle V-bottom, both sides | 0.3 × 3.7 | 4.0 | unchanged since round 3 |
| 5.9 | zip-tie tunnel roofs, 4 | 9.3–10.7 × 3.5 | 2.0 | 4 mm bridges |
| 14.7 | idler bolt-slot hull ceiling, both sides | 7.5 × 7.9 | 4.0 | 8.0 mm bridge along X between the teardrop flanks; same as round 3 |
| 15.1 | road-wheel nut-trap roofs, 4 | 3.1 × 2.3 | 1.8 | unchanged |

## Required fixes

None to the part.

**Required before assembly (BUILD_GUIDE, not this part).**

**G1. Step 3 key method.**
- Step 3 says "put the **long** arm of the 2.5 mm key into the bolt head, and twist the key by its **short** arm". Service says the same.
- A 2.5 mm L-key (ISO 2936) has a 56 mm long arm, as the guide's 18 mm short arm implies.
- Coaxial with the idler bolt, it has 49.7 mm to the other idler bolt's head. Socket bottom at \|y\| 25.5 (head top 24.2 + 1.3 socket depth); opposite head at −24.2, at the same x 115.75 because step 3 snugs both at the rear of their slots.
- Even with the other bolt out, it has only 53.5 mm to the opposite block face at \|y\| 28.
- A plain key tilts only a few degrees in a hex socket, and the opposite block stands to Z_A + 14.5. **So the instruction, which carries the 0.04 N·m snug that strength S1 depends on, can't be followed as written.**

**Fix.** In step 3, the Tools list and Service, replace that sentence with:

> "Put the ball end of a 2.5 mm ball-end L-key into the bolt head, with the key tilted 18–25° up from the bolt's axis so its long arm passes over the opposite idler block. Twist the key by its short arm with two fingertips until the head stops turning (about 230 g at the short arm's tip)."

Add "2.5 mm hex key, ball end (long arm ≥ 56 mm): idler bolt heads" to the Tools list. The geometry:
- At 18° the key clears the opposite head by 11.8 mm and the opposite block top by 1.4 mm (key radius included).
- Its bend lands inside the tub at \|y\| 27.8, Z_A + 17.3, below the rim at Z_A + 28.
- The short arm swings freely through its upper half, about 190°: pointed down and outward it meets the opposite block. Re-index the key in the head if the snug needs more turn.

The 230 g calibration is unchanged, and the part needs no change. Step 7 ("hold its bolt head still with the 2.5 mm key") works with a plain key, short arm in the head, long arm pointing up out of the tub.

## Round-4 findings: still resolved?

| Round-4 item | Status in round 5 | Evidence |
|---|---|---|
| Checklist items 1–16 | PASS | Above |
| A1: how light the snug is; oil; how to hold the nut; grease | Resolved, but the key method is wrong (G1) | BUILD_GUIDE l.130 (oil "required"), l.127 (grease), l.132–136 (0.04 N·m, the 230 g scale check), l.134 (spanner on the nut, now outside) |
| A2: hold the head while turning the nyloc | Resolved | BUILD_GUIDE l.156 |
| A3: witness mark on the head washer and head plate | Resolved | BUILD_GUIDE l.162. At the slot's rear end, 2.95–3.15 mm of head plate shows behind the Ø9 washer: the guide says "at least 3 mm", close enough |
| A4: chain-drill the closed slots | Resolved | BUILD_GUIDE §1 step 2 (four 2.5 mm holes, ends opened to 3.4) |
| R1: printed targets in spec §3 | Still open (now also the seat row) | See R1 below |
| R2: insert holes' printed size; slice-plan overrides | Still open | spec §3 still says "Ø4.0 ±0.1". slice_plan.json still has perimeters 4 and fill 25 % against the required 5 and 30 %; the validator will fail it at SLICE |
| S1: snug P and lubrication for the jack thread | Resolved by strength | 0.04 N·m on oiled plates, jack thread SF 3.15 (brief "Snug and oil") |
| S2: check the plates with the joint open | Resolved by strength | Brief: "the clamp is checked with no clamp force left" |
| Note 2: nut-slot roof strip | Gone with the slot | Layer analysis: no start at z 16.5 |

## Round-5 checks in detail

### Lip and stops print without support

- **Lip** (section at x 118, \|y\| 38.5: solid z 13.98–15.48, i.e. Z_A − 6.7 to − 5.2).
  - From the bed up, it grows out of the wall on its 45° underside, 0.2 mm per 0.2 mm layer, then rises 1.0 vertically to its top at print z 6.8.
  - Print z 6.8 is a layer boundary, so the plate's seat height is exact.
  - Layer analysis: no cell more than 0.2 from the layer below.
- **Stops** (X-probe at \|y\| 38.5: solid 106.5–108.0 and 129.0–130.5 at every Z from Z_A − 5 to + 4.9).
  - They are vertical, from Z_A − 5.7, which is inside the lip's 1.0 face, up to Z_A + 5.2.
  - At the front corner the outer skin curves in on the r6 fillet (\|y\| 37.96 at x 129.7, 37.86 at 130.3). The front stop joins it, because the seat starts at \|y\| 37, 1 mm inside the face (l.193). So the stop is 1.04–1.14 proud there, and still solid to the wall.
- **Nothing floats**: the seat is fused to the wall over \|y\| 37–38 along its whole length.

### Wall round the seat and the bolt slot

The PETG between the plates is 8.0 everywhere in the plate footprint except the slot (cad_checks and the probes above). The slot (x 114.2–125.8, Z_A − 1.8 to + 2.55) has at least 5.6 mm of PETG to any free surface.

### Real 14-gauge or 2 mm plate in the seat

The seat is open outward, so plate thickness only moves the stack. The X and Z fits are those of the head plate.

| | Seat, CAD → printed | Plate | Clearance printed |
|---|---|---|---|
| X between the stops | 21.0 → about 20.8–20.9 (each stop's inner face prints 0.05–0.1 proud) | 20.6 (hand-cut 20.4–20.8) | 0.0–0.5. Filing is already in §1 step 5. A seam blob on a stop face can take 0.1 |
| Z | lip top at print z 6.8 (layer boundary); no top constraint; stops reach Z_A + 5.2 | 10.0 (9.8–10.2): top at Z_A + 4.6 to + 5.0 | free |

| Sheet | Lip and stops engage | Ø9 washer clears lip and stops (Y) | Idler hub start (nominal hardware) | Thread past the nyloc (0.3 end play) |
|---|---|---|---|---|
| 1.72 | 1.0 of 1.72 | 0.72 | 43.42 (−0.28) | 4.46 |
| 1.90 (14 ga) | 1.0 of 1.90 | 0.90 | 43.60 (−0.10) | 4.29 |
| 2.00 | 1.0 of 2.00 | 1.00 | 43.70 | 4.20 |
| 2.17 | 1.0 of 2.17 | 1.17 | 43.87 (+0.17) | 3.56 |

- The washer never reaches the lip in Z either: its edge is at Z_A − 4.75 against the lip top at Z_A − 5.2.
- At the stops in X, the washer's front edge (128.75 at the printed slot end) clears the front stop's face (≈ 128.9) by 0.15. It is outboard of the stop in Y anyway.
- **The idler moves with the stack.** With the nut's (2.15–2.4) and washers' tolerances as well, the idler's disc sits −0.68 to +0.32 off the track plane, against the link notch's 0.5 a side.
  - With the 0.3 end play the disc can float into the notch in every case: −0.38 at worst.
  - The 1/8 in (3.2 mm) exclusion still stands.

### Bolt and slots line up through both plates over the full travel

- **In Z.** Both plates rest at Z_A − 5.2: the recess floor and the lip top are the same layer line. So both slot bands are Z_A − 1.9 to + 1.5.
  - The bolt resting in the Ø3.4 printed PETG slot sits at Z_A − 0.25.
  - It clears both plate slots by 0.15 below and 0.2–0.25 above.
- **In X.** The bolt's centre (thread major 2.9–3.0) can travel 115.75–124.25 in the printed PETG slot. Each plate's slot allows rear end + 7.45 to + 16.55:

| Plate position between its stops (or recess ends) | Bolt-centre range its slot allows |
|---|---|
| At the rear (rear end 108.1) | 115.55–124.65 |
| At the front (20.6 plate: 108.3; 20.4: 108.5) | 115.75–124.85 / 115.95–125.05 |

- Every case covers the front end.
- At the rear end, a short plate pushed forward stops the bolt at most 0.2 short. The bolt's push carries it back, which is how step 3 snugs it (bolt pushed to the rear first).
- This agrees with assembly_check.json's `covers_slot_travel: true` (115.5/115.9–124.5/124.9).
- A plate fitted 6 mm end forward loses 3 mm of travel. Guide §1 step 4 and step 3 cover it with the pen mark.

### Hand access

- **Step 3, holding the nut: easy.**
  - The nut is outside now, on the Ø9 washer at \|y\| 40.8–43.2. Nothing on the outer face stands beyond \|y\| 39 near it: lip and stops at 39, housing at x ±11.2, no idler or track yet.
  - So a 5.5 mm open-end spanner (or pliers) goes on from any direction in the XZ plane, at either end of the slot.
  - The bolt's tip stands 24 mm beyond the nut (tip 67.2), so the spanner can't slip off the end.
- **Step 3, turning the head: see G1.** The long arm can't go in coaxially. A ball-end key, or the short arm in the socket, does reach it.
- **Step 7, the nyloc.**
  - Outside, with no track: a spanner on the nyloc at \|y\| 59–63, beyond the disc.
  - Inside, the head is held with a plain 2.5 mm key: short arm in the socket, long arm up out of the open tub. The motors are at x ±12; the battery and sensor go in later.
  - The arm can swing about 28° forward before it meets the front wall rim, and freely to the rear.

## Recommendations (not blocking)

- **R1 (carried from round 4, now wider). Spec §3: give printed targets.**
  - The new "Nut-plate seat … +0.2/−0" row would reject the stops' expected 20.8–20.9 printed gap (−0.1 to −0.2 against 21.0).
  - Write it as "stops 21.0 CAD apart, about 20.8 printed; the 20.6 plate drops in", and the head-plate recess row the same way.
- **R2 (carried).** State the insert holes' printed size (about Ø3.8). Raise slice_plan.json to perimeters 5 and fill 30 % before SLICE.
- **R3. Process.**
  - log.md has no line for the round-5 model.py, brief and cad_checks change (git b7eb995). The 13:41 Architect line only records the merge.
  - spec.md's header still says "round 4 by design-lead".

## Notes for the strength review (not DFM items)

- The idler's axial position now depends on the nut-plate thickness and the hardware stack (−0.68 to +0.32 mm; table above). The disc stays within the link notch only with the end play kept near 0.3 mm (spec < 0.5).
- The running washer bears on the wall nut, which is held only by its 0.04 N·m snug. A side load (skid-steer drag) on the spinning idler drags that washer. Rough figure: 3 N × µ 0.3 × r 2.7 ≈ 0.0024 N·m, about a tenth of the nut's breakaway torque. That is the same arrangement as round 4. Worth a line if strength re-checks the snug.

## Printing notes against print_requirements.json

PETG, 5 perimeters, 5 top and 5 bottom layers, 30 % gyroid, layers ≤ 0.2, 230–250 °C nozzle, 80–90 °C bed, 12 h or less. They are consistent with the brief: floor on the bed, 0.4 bed chamfer. slice_plan.json still has to be raised to meet them (R2).

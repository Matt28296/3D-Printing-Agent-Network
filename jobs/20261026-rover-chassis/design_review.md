VERDICT: PASS

# DFM review, round 4: 20261026-rover-chassis

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26

**Inputs:**
- this job: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, cad_checks.py, print_requirements.json, slice_plan.json, log.md;
- renders/{iso,front,right,top,bottom}.png, regenerated with tools/render.py;
- round-3 design_review.md and strength.md;
- rover_frame.py (SKIN, MOTOR_FACE_Y, PLATE_T, IDLER_PLATE, NUT_PLATE, PLATE_SLOT);
- from the assembly job: assembly_check.json, assembly_plan.md, and BUILD_GUIDE.md (§1 plates and how-to; §3 steps 3, 7 and 8; Service).

library/lessons.md and materials.csv have no rows, so the fdm-design-rules defaults apply (HOLE_COMP +0.2).

**Outputs are current.**
- A fresh `build()` gives 130 848.15 mm³ and 154 × 92 × 40, identical to geometry.json.
- part.stl is 130 842.3 mm³ and watertight.
- `tools/mesh_check.py` re-run: mesh_check.json is unchanged.
- `cad_checks.py`: all 47 checks pass.

**Extra evidence** (my scripts, run in the scratchpad):
- **Layer-by-layer support analysis of part.stl.** 0.05 mm raster at PrusaSlicer's mid-layer planes. It flags anything more than 0.2 mm (45° at 0.2 mm layers) from the layer below.
- **Ray-cast wall thickness.** Four rays from every face around the round-4 features.
- **Probes and sections.** `is_inside` probes, plus YZ and XZ sections through the recess, the web and the nut slot, on both sides.
- **Plate, nut and tool-gap calculation** from the model's own parameters.
- **Comparison with round 3:** the round-3 part.stl (git 87cd918~1).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 154.0 × 92.0 × 40.0; fits_bed true (164 × 102 with the margin, on 250 × 210) |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight true, min_z 0.0 (geometry.json and the fresh build) |
| 3 | Orientation | PASS | Floor down, open top up (iso.png, front.png). front.png shows each idler nut slot in the outer face: 15 × 9 with the dark band of its 45° roof. My close-ups show the head-plate recess in the idler-block face, with its 45° roof band |
| 4 | Load paths vs layers | PASS (justified) | Round-3 paths unchanged. The round-4 plates bear horizontally, in the layer plane: the head plate on the recess's back face (\|y\| 30), the nut plate on the slot's bottom (\|y\| 33.4), and the web compressed along Y. Only one load crosses the layers: in a drop, the nut plate's top edge pushes up on the slot roof, and that is compression |
| 5 | Bed contact | PASS | 11 540.5 mm², unchanged. PETG is not a warping material; use a glue release layer on smooth PEI |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS (note) | overhang_pct 0.51 (314.3 mm², down from 377.9). The layer analysis finds 18 unsupported starts, all expected, and no floating island (table below). Largest bridge: 8.0 mm, the idler-slot hull ceiling, which now lies only in the 3.4 mm web (z 14.7). The new nut-slot roof strip (z 16.5, 14.55 × 1.75) is anchored along the web for its whole length and at both ends: at most 2.0 mm from support. The recess roofs are 45° from (\|y\| 30, z 17.2) to (28, 19.2) in print z, and leave nothing unsupported |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (note) | Skin 2.0 (ray-cast 1.999 at \|y\| 44–46; cad_checks): round 3's one wall under 1.8 is gone. Nacelle walls 2.0. Web between the recess and the nut slot 3.4 (\|y\| 30–33.4; probes and sections). Ray-cast over x 104–134, \|y\| 26–39 (recess, nut slot, web, buttress), both sides: thinnest 2.50 (the floor), no ray under 1.8. Recess roof to block top 7.3; nut-slot floor 7.5 above the bed. Jack-pilot ligament 2.0, unchanged. thin_wall_warnings empty. One feather edge under 0.9 (see note 1) |
| 8 | HOLE_COMP on fits; horizontal holes teardrop or flat-top | PASS | No new holes. Neither new horizontal cavity has a ceiling to bridge: the recess roof is 45°, and the nut-slot roof is flat only over the plate (2.0) before rising at 45°. Fits are explicit (l.98–106): the recess is 21.0 CAD in X between the buttress (108) and the strip (129), and the plate is cut 0.4 short instead of compensating the recess (rover_frame l.88; spec §2/§3); Z is ±5.2 (+0.2 a side; a Z size needs no XY compensation); the nut slot is 15.0 × 9.0 (+0.5 a side, which covers HOLE_COMP). Skin hole: still a Ø4.7 teardrop (l.290) |
| 9 | Bottom edges chamfered | PASS | Unchanged: `chamfer_plane_edges` (l.241) runs before any cut; bottom.png |
| 10 | Internal corners on load paths | PASS (note) | Round-3 roots unchanged. The corners of the recess and nut slot carry plate bearing (compression), not tension |
| 11 | Fasteners (§4) | PASS (note) | The steel plates put the head and nut clamp on wide steel faces (§4 "washers or wide heads"). The idler wall nut is no longer captive: it sits in a 9 mm tall slot, and an M3 nut is 6.0–6.35 across its corners. So it must be held while it is snugged, and in service it stays put only by preload, which §4 says not to count on in PETG. The worst case is mild: the bolt turns with the idler as its axle, and the jack screw still holds the tension. See the assembly notes. Road-wheel traps unchanged |
| 12 | Spec §3 dimensions are named parameters | PASS | All named and commented, and cad_checks proves each one: PLATE_T 2.0, IDLER_PLATE, NUT_PLATE, PLATE_SLOT (rover_frame l.87–92); PLATE_RECESS_X/Z/D (l.98–102); NUT_SLOT_H/L/D (l.104–106); SKIN 2.0 and MOTOR_FACE_Y 44.0 (rover_frame l.62, 67); CRADLE_Y0 16.5 (l.81). Printed-value wording: R1 |
| 13 | Service temp ≥ 20 °C below softening | PASS | 40 °C against ≈ 70 °C for PETG. `materials_on_hand` is empty: confirm PETG at slicing |
| 14 | Lessons | N/A | library/lessons.md has no entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |
| 16 | Fits and assembly (cross-part) | PASS (notes) | Plates fit; both plate slots cover the bolt's whole travel; the 1.72–2.17 mm sheet range is absorbed (tables below). assembly_check.json: 158 bodies, 0 collisions; jack screw 6.5 mm in the buttress at every slot position, socket outside it, key path clear. Hand access works, on the conditions in the assembly notes |

Layer analysis, every unsupported start (print z):

| z | Where | Size | Furthest from support | Verdict |
|---|---|---|---|---|
| 0.3 | 4 housing corners at the bed chamfer | 0.02 mm² | 0.28 | the diagonal of a 45° chamfer; fine |
| 1.3 | nacelle V-bottom, both sides | 0.35 × 3.75 | 4.0 | unchanged since round 3 (its R2) |
| 5.9 | zip-tie tunnel roofs, 4 | 9.4–10.8 × 3.55 | 2.0 | 4 mm bridge across the tunnel |
| 14.7 | idler-slot hull ceiling in the web, both sides | 7.65 × 3.35 | 4.05 | 8.0 mm bridge along X between the teardrop flanks |
| 15.1 | road-wheel nut-trap roofs, 4 | 3.15 × 2.35 | 1.8 | unchanged |
| 16.5 | idler nut-slot flat roof, both sides | 14.55 × 1.75 | 2.0 | 2 mm ledge off the web; see note 2 |

The round-3 starts that are gone: the 11.46 × 2.6 idler nut-slot roof (reached 2.4) and the 8.0 × 7.4 hull bridge.

## Required fixes

None.

## Round-3 findings: still resolved

- **Round-3 checklist.** Every item is still PASS on the round-4 geometry (above).
- **Round-2 fixes that round 3 confirmed:** all still in place.
  - Hull up to the teardrop tips: hull top at Z_A + 2.55 (sections).
  - V-trough cheeks: CRADLE_HALF_X 12.1. The trough end moved 1 mm inward with the gearbox face; cad_checks covers it.
  - Strips and collars: unchanged.
  - Jack-screw stop: unchanged; assembly_check.
- **Round-3 recommendations:**
  - **R1 (strips at the buttress roots):** not done. Now moot at the block face, because the recess starts exactly at the buttress face (x 108). Strength round 3 rated the sharp root (B9, Kt 2.5, SF 12.7).
  - **R2 (nacelle strand):** unchanged; still prints.
  - **R3 (skin bending):** superseded by SKIN 2.0.
  - **R4 (insert holes print at about Ø3.8 against spec §3's "Ø4.0 ±0.1"):** still open (R2 below).
  - **Slicing note:** still open. slice_plan.json overrides `perimeters` 4 and `fill_density` 25 %, against the required 5 and 30 %. The validator will fail it at SLICE.

## Round-4 checks in detail

### Steel plates in their pockets

Printed sizes assume the fdm-design-rules default: each pocket wall prints 0.1 inward. Hand-cut plates are taken as ±0.2.

| | Pocket CAD → printed | Plate | Clearance printed |
|---|---|---|---|
| Head plate, X | 21.0 → about 20.8 (x 108–129) | 20.6 (hand-cut 20.4–20.8) | 0.2 (0.0–0.4) |
| Head plate, Z | 10.4: both edges fall on 0.2 mm layer boundaries (print z 6.8, 17.2) | 10.0 (9.8–10.2) | 0.4 (0.2–0.6) |
| Nut plate, X | 15.0 → about 14.8 (x 112.5–127.5) | 14.0 | 0.8 |
| Nut plate, Z | 9.0 → 8.8–9.2: floor and roof fall mid-layer (print z 7.5, 16.5) | 8.0 (7.8–8.2) | 0.6–1.4 |

**Is 0.4 mm of length clearance on the head plate enough?** Yes, as specified.
- It prints to a 0.2 mm locating fit (§3 snug/locating 0.15–0.2). That suits a plate whose slot must stay on the bolt.
- With a hand-cut plate, about half will need a few file strokes. BUILD_GUIDE §1 step 4 already says "file its ends if it's tight".
- More length is not available: the recess fills the space between the buttress face and the corner strip.
- Nothing is gained by cutting the plate shorter:
  - the Ø9 washer reaches x 128.75 at the slot's front end, and the plate ends at 128.7–128.9;
  - the plate's slot is positioned from the rear end, so filing the front end changes nothing.

**Real sheet thickness.**
- 14 ga plain steel is 1.90 mm nominal, and galvanized 14 ga is about 2.0 mm.
- Mill thickness tolerances at this size are about ±0.15 mm, so plates will measure roughly 1.75–2.15. I checked 1.72–2.17. PLATE_T = 2.0 takes all of it:

| Sheet | Head plate vs block face | Jack screw to the Ø9 washer | Jack screw bears on (of the 3.0 head) | Wall nut below the outer face |
|---|---|---|---|---|
| 1.72 | 0.28 below | 0.58 | 2.42 | 0.48 |
| 1.90 (14 ga) | 0.10 below | 0.40 | 2.60 | 0.30 |
| 2.00 | flush | 0.30 | 2.70 | 0.20 |
| 2.17 | 0.17 proud | 0.13 (0.03 with a 0.9 washer) | 2.87 | 0.03 |

- **Thin plate:** the Ø9 washer can follow it down. The washer is smaller than the recess, which is 10.4 tall and covers the washer's whole x travel of 111.25–128.75.
- **Thick plate:** its top edge still bears on the flat roof for 2.0 of its thickness.
- **1/8 in (3.2 mm) is correctly excluded.** At 1.2 mm proud it would put the jack screw on the washer.

### Plate slots against the bolt travel

The PETG slot's teardrop ends are Ø3.4 printed and the bolt is Ø2.9 (thread major diameter), so the bolt's centre can travel x 115.75–124.25. The plate slots never cut that short:

| Plate position in its pocket | Bolt-centre range the plate slot allows |
|---|---|
| Head plate at the rear of its recess / at the front | 115.55–124.65 / 115.75–124.85 |
| Nut plate at the rear of its slot / at the front | 115.05–124.15 / 115.85–124.95 (it floats 0.8, so the bolt carries it along) |

- **In Z:** with the bolt resting in its PETG slot (axis Z_A − 0.25), the head plate's slot (resting on its floor) clears it by 0.1 below and 0.3 above. The nut plate hangs on the bolt or rests on its floor; either works.
- **A head plate fitted backwards** (6 mm end at the front) allows only 112.15–121.25, losing 3 mm of tensioning travel. Step 3 states the orientation, and the 6 / 2.6 mm ends are easy to tell apart.

### Hand access, BUILD_GUIDE step 3: snug each idler bolt while holding its nut

**Yes: a person can do it with ordinary tools, using a fingertip on the nut.** Flat-nose pliers can't do it where the guide snugs the bolt.

**Inside the tub.**
- The tub is empty at step 3: the motors go in at step 5, the sensor at 9 and the battery at 10.
- The M3 × 40 (43 mm with the head) fits between the two idler-block faces, which are 56 mm apart.
- The 2.5 mm key reaches the head along Y. The bolt axis is 9.5 mm above the floor and 28 mm below the rim, so the long arm swings freely.

**Outside.**
- No idler is fitted yet, so the nut slot's 15 × 11.6 mouth is open.
- Push the bolt through until its tip stands out of the slot. Spin the nut on, and down to the plate, by finger.
- Then press a fingertip on the nut's face, 0.2 mm below the wall face, while the key snugs the head.
- Once the steel nut bears on the steel plate, its face friction roughly equals the thread torque: 0.33 P against 0.31 P N·mm at µ 0.15. The fingertip only adds the margin.

**Pliers and spanner.** At the slot's rear end, where step 3 puts the bolt (x 115.75):
- there is 0.40 mm between the nut's rear flat and the slot end, and 1.50 mm under its lower flat;
- no plier jaw or spanner fits there;
- a 5.5 mm spanner only fits near mid-slot (4.65 mm).

A large nut (6.35 across its corners) can just touch the slot's rear end (−0.02) when a corner points back, and that only helps.

### Hand access, step 8: tension with the jack screw only

**Physically yes, but only with a light, stated snug.**

**Access.** assembly_check shows the 1.5 mm ball-end key reaches the jack screw at every slot position, with the socket outside the buttress (x 93.2–101.2). The torque is small: under 0.1 N·m for a 110 N push.

**What changed in round 4.**
- Round 3 tensioned with the bolt finger-tight and snugged it afterwards.
- Round 4 snugs it at step 3. The jack screw then slides a pre-clamped bolt across two steel-on-steel faces: the washer on the head plate and the nut on the nut plate. Both plates are captive in X.
- So the jack screw's thrust is about 2µP + 10 N (P is the snug clamp, 10 N the track pretension).
- The guide doesn't bound P: "just enough to keep the bolt square".
- The jack screw is self-tapped in PETG. Its design strip-out is 142 N (strength round 3, B7: 1.30 MPa at 29.8 N against the 6.2 MPa allowable).

| Snug torque | Clamp P (K 0.2) | Jack-screw thrust (µ 0.15 / 0.3) | Thread SF against 142 N |
|---|---|---|---|
| 0.05 N·m (two fingers on the key's short arm) | 83 N | 35 / 60 N | 4.1 / 2.4 |
| 0.1 N·m | 167 N | 60 / 110 N | 2.4 / 1.3 |
| 0.2 N·m | 333 N | 110 / 210 N | 1.3 / 0.68 |
| 0.3 N·m (a normal L-key "snug") | 500 N | 160 / 310 N | 0.89 / 0.46 |

A firm snug at step 3 can strip the jack screw's thread at its first tensioning. The fix is in the guide (A1), not the part: strength should set the number (S1).

### Note 1: the feather edge at the trough

Where the gearbox pocket's upper-left 45° face cuts the trough's 1.5 × 45° join strip at the wall, a 60° sliver is left:
- location: x −7.9 to −6.9, \|y\| 32.2–33.5, print z 11.5–12.8;
- thickness: 0.03–0.9 mm by ray cast;
- it is identical in the round-3 mesh;
- it carries nothing, is a 45° overhang underneath, and will print as a small nub or be dropped by the slicer.

### Note 2: the nut-slot roof strip

- With 5 perimeters the 2.0 mm strip is filled entirely by perimeter lines running along X. They span the 15 mm between the slot's end walls, and the innermost lies on the web.
- This is the same class as round 3's 11.46 × 2.6 roof, which printed by that review's analysis, and its overhang is shorter (2.0 against 2.4).
- Expect a little droop at the free edge. It eats into the 0.5–1.0 mm gap above the nut plate, and the plate still goes in through 8.3 mm or more.
- The strip is a drop stop backed by solid PETG, not a fit face.

## Recommendations (not blocking)

**Assembly notes for the assembly job's BUILD_GUIDE.** They change no part, but make them before anyone assembles the rover.

- **A1. Step 3: say how light "snug" is, and how to hold the nut.**
  - Replace "snug it there, still holding its nut: just enough to keep the bolt square" with: "turn the 2.5 mm key by its short arm, with two fingers, until the head stops (about 0.05 N·m); don't lever on the long arm".
  - Add: "a drop of light oil on each plate where the washer and the nut slide".
  - Replace "hold it with a fingertip or flat-nose pliers" with: "spin the nut down to the plate by finger, then hold it with a fingertip while you snug; pliers don't fit beside the nut at the rear of the slot".
  - Add: "a dab of grease holds each plate in place while you fit the bolt".
  - Evidence: step 8 table above.
- **A2. Step 7: hold the idler bolt's head.** Add: "On each idler, hold the bolt head with the 2.5 mm key from inside the tub while you turn the nyloc."
  - A nyloc's prevailing torque (a few tenths of a N·m) drags the bolt in its loosening direction against a light snug (about 0.05 N·m of head and thread friction).
  - Once the idler covers the nut, the step-3 snug can't be redone.
- **A3. Step 8 and the assembly spec §8 test 6: move the witness mark.**
  - The guide says to draw a pen line across the slot nut, but with the idler fitted the nut is behind its Ø7 washer and Ø10 hub.
  - That washer fits inside the 15 × 11.6 slot mouth, so it seats on the nut, 0.2 below the wall face.
  - Draw the line across the Ø9 washer's edge and the head plate inside the tub instead: it shows any slide, with the lid off.
- **A4. §1 "Making the idler plates", step 2.** A hacksaw can't enter a closed 3.4 mm slot. Say: "drill a third hole, or a row of 3 mm holes, between the two ends, then file to the line".

**Spec and carried-over items.**

- **R1. Spec §3: give printed targets for the new pockets.**
  - Give the recess as about 20.8 printed and the nut slot as about 14.8 long and 8.8–9.2 tall (its floor and roof fall mid-layer), so that inspection doesn't reject them against "21.0 CAD ±0.1" and "15.0 +0.2/−0".
  - Optionally, NUT_SLOT_H 9.0 → 9.2 puts the floor and roof on layer boundaries (print z 7.4 and 16.6), for a predictable height.
- **R2. Round-3 items still open:**
  - R4: state the insert holes' printed size (about Ø3.8) in spec §3;
  - the slice-plan overrides (perimeters 5, fill 30 %) before SLICE.

## Notes for the strength review (not DFM items)

- **S1. The jack-screw thread now carries the slide force of a pre-clamped bolt,** at step 8 and at every re-tension: about 2µP + 10 N, over two steel-on-steel faces. B7 was sized at 29.8 N.
  - Please set the snug P and the lubrication that keep B7 at SF 3 or more.
  - The guide should then carry that number (A1).
- **S2. The clamp's preload is fragile.**
  - The joint is about 27 kN/mm. That is dominated by the 3.4 mm PETG web, about 73 mm² under the nut plate.
  - An 80 N snug is therefore gone after about 0.003 mm of web creep, or about 2° of relative nut rotation.
  - The round-3 plate rows assumed 100 N of clamp left after creep. Please check the plates with the joint open (P ≈ 0).

## Printing notes against print_requirements.json

- The brief asks for the floor on the bed and a 0.4 bed chamfer.
- The requirements: PETG, 5 perimeters, 5 top and 5 bottom layers, 30 % gyroid, layers ≤ 0.2, 230–250 °C nozzle, 80–90 °C bed, 12 h or less.
- They are consistent with each other.
- slice_plan.json still has to be raised to meet them (round-3 note).

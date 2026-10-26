# Design brief: Claw cover (front plate, top wall, upper lip)

Job: 20261026-arm-claw-cover · design-lead · 2026-10-26, claw round 3: every required fix of the cover DFM and strength round 2 (this job's design_review.md and strength.md); earlier: deep review 03 SYS-01 fix A, cover round 1.

## Material
PETG, as for the rest of the arm: tough, low creep under the servo's holding load, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables: 25 MPa along the layers, 12.5 MPa across them.

## Orientation
Standing on its −y end (`TO_PRINT = Rot(90, 0, 0)`): print Z = claw y + 32, so the layers are y = const planes. The whole side profile lies in the bed plane, so every rack bearing face is a vertical wall and comes out straight and smooth: the front plate's inner face, the top wall's underside, the lip's face.

### Openings, bridges and overhangs
- **Slot A** runs along print Z from the bed and closes with a 45° roof: a ceiling in print, apex rounded r 1.5.
- **Slot B**'s closed end is a floor in print (r 2 corners).
- **The pinion pass-through** is a teardrop with its 45° point up (+y).
- **The screw holes** are teardrops pointing up.
- **Bed chamfer:** the openings are cut before the 0.3 mm bed chamfer, so slot A's mouth on the bed is chamfered too.
- **Brim:** the part is 64 mm tall on a 704 mm² footprint, so it needs a 5 mm outer brim (`print_requirements.json` min `brim_width` 5).

### Two breakaway supports (DFM fix 1), and why they are needed
The two pieces of the front plate beside the pass-through start in mid-air at print z 38.5 and 39.1: (a) between the pass-through and slot A's roof, and (b) between the pass-through and slot B. They cannot be laid out to grow from material below them:
- **The pass-through must break into both slots.** It is r 11.4 in CAD: the pinion's r 10.85 tips plus 0.55 radial. The necks' inner faces are r 11.25 from the axis, and the slots' inner edges r 11.0, so no plate can stay between the pass-through and either slot.
- **Both slots must cross y 0.** At the closed position neck A spans y −20…0 and neck B y 0…20, plus their r 4 root fillets.
- **The slots open at opposite ends.** Slot A opens at −y (the bed) and slot B at +y (the top), so the jaws can slide in from the ends (SYS-01).
- **So the plate is cut in two.** The cut runs slot A → pass-through → slot B, from the bed to the top. The plate beside the pass-through above the two breaks (|y| ≈ 3) belongs to the upper piece, and it has no material under it in print.
- **Standing on the +y end** moves the islands to the lower piece. Other orientations turn the 32 mm slots into bridges.
- **Neither moving the cut-backs nor sloping them helps.** The reviewer showed this: the pieces join the rest only at slot A's apex and the pass-through's apex.

So `build()` adds two **breakaway pillars** (`supports()`; `design()` is the cover as fitted, without them). Each pillar:
- is 4 mm along x, 0.5 mm in from both plate faces;
- stands on the lower half's material below its piece;
- stops 0.25 mm (one 0.2 mm layer) under the piece, as a support's top gap.

| Pillar | y (from → top) | z (claw G) | Under |
|---|---|---|---|
| A | −8 → 6.25 (emerges at the cut-back's floor, y −7) | 36.8…38.1 (1.3 thick) | piece (a), first layer at y 6.5: z 36.62…38.26 |
| B | −8 → 6.75 (its foot inside the plate, solid to z 19.13 at y −8; emerges between y −6.7 and −5 as the pass-through's surface crosses it) | 16.45…18.05 (1.6 thick; was 16.35…17.35) | piece (b), whole first layer (print z 39.0–39.2, y 7.1): z 16.25…18.33, 0.20 / 0.28 beyond the pillar |

**Removal and checks:**
- Both pillars stand inside the pass-through, clear of both slots: z ≤ 38.1 against slot A's 38.25, and z ≥ 16.45 against slot B's 16.25.
- They block only the pinion. BUILD_GUIDE §4 step 9 snaps them off, and trims any nub flush, before the cover goes on.
- They are the part's only supports: `print_requirements.json` now requires `support_material` 0, so the slicer adds none of its own.
- The layer check of part.stl (0.2 mm layers, 0.04 mm raster, each layer compared with the one below grown 0.3 mm) finds, besides the two pieces over their pillars' one-layer gap:
  - the end of the corner fillet (print z 41.1, 0.15 mm²);
  - the r 1.5 apexes of slot A's roof (z 42.9–43.1, at most 0.56 mm);
  - the pass-through's teardrop apex (z 47.5, 0.76 mm).
- All three are the same as in round 2.
- The second tie, at the top of the print, adds no unsupported patch.

### Load paths and the layers (DFM fix 2; round 1's fix 1)
The round-2 brief said "all bending runs along the layers". That was wrong.

| Path | Load | Direction of the bending stress | Along or across |
|---|---|---|---|
| **(a) Strip under slot B** (z −6…5.75, 5 thick) | neck B's bearing (yaw stall or hand push on jaw B), spanning y from slot B's closed end (y −5, r 2 corners) to the +y M2.5 at y 24 | along y | **across** |
| **(b) Top wall between the two top screws** (y −23, 14) | rack A's lift (gear separating force + the grip's twist) | along y | **across** |
| **(c) Lower half of the front plate** | rack B's forward thrust and the necks' loads, carried along y to the first tie (y −32…−24) and to the −y M2.5 | along y | **across** |
| Upper half of the plate, hanging from the top wall | rack A's grip thrust near the top wall; rack B's reversed push on its bottom strip (z 16.25…18.1) | along z, in the side profile | along |
| Lip wall (cantilever off the top wall) | rack A's back thrust at the rack's end | along z / x, in the side profile | along (sharp rack-side root, Kt 2.5) |
| Ties: posts and webs (both) | the reversed rack pushes into the lip | in the side profile | along |

The strength analyst checks (a)–(c) at the 12.5 MPa across-layer allowable, as in round 2's rows 28–33.

## Concept
- **Pass-through and pinion order (SYS-01 fix A):** the pinion goes in last, axially, through the Ø22.6 (printed) pass-through on its axis, with both jaws parked fully open, and comes out first for service.
- **The split plate and the first tie:** the pass-through merges with both neck slots and cuts the front plate in two. The first tie (y −32…−24) joins the lower piece to the lip: a post behind the racks and a web between them, |z − ZS| ≤ 8, 1.15 mm clear of both racks' tips.
- **Round 3 changes:**
  - **Lip 4 → 8 mm** (GUIDE_T 8, x 14.35…22.35; cover strength change 1). The first tie's post grows with it (x 14.35…22.35). The lip stays above the claw servo's case (z ≥ 36.75 against 33.35).
  - **Second tie at y 24…32** (strength change 2): the same post and web, joining the upper piece's lower half to the lip, between the racks and outside every jaw path and the pinion. It is at the top of the print, so its undersides are 45° slopes:
    - the post (4 × 8 mm, x 18.35…22.35) grows from the lip, full depth from y 24 down to its foot at the lip at y 6.5;
    - the web grows from the post at its back and from the front plate at its front, just above the pass-through's 45° teardrop flanks;
    - it is full height (z 19.25…35.25) for y ≥ 24;
    - it stays outside the pinion's r 11.4 (`cad_checks.py`).
  - **Front plate down to z −6** (FRONT_Z0 −6, strength change 3): the strip under slot B is 11.75 deep.
  - **FACE_W 12** (pinion strength): the front plate is at x 34.85…39.85, 2 mm further forward. The fingertips stay where they were (the jaw's blade is 2 mm shorter).
  - **Front screws M2.5 × 16** into the frame's 14 mm pilots, 11 mm engaged (was × 12, 7 engaged).

**Camera.** The cover's top-front edge is 2 mm nearer the fingers, so it fills more of the Brio's image: 44 % at the 65° preset and 46 % at 90°, against 38 / 43 %. The fingertips stay at v +0.14. The PC code's crop (`CLAW_ROWS`) goes from 0.40 to 0.46, and BUILD_GUIDE §6 says so.

## Critical dimensions
| Feature | Nominal | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| **Front plate inner face** | **x 34.85** | ±0.15 | 0.25 sliding gap in front of the racks | — | claw_frame.py X_F0 (FACE_W 10 → 12) |
| **Front plate outer face** | **x 39.85**, z **−6**…48.5 | ±0.15 | — | — | claw_frame.py X_F1, FRONT_Z0 −4 → −6 |
| Top wall underside | z 48.5 | ±0.15 | rack A's back rides on it | — | claw_frame.py (RACK_SEAT 0) |
| Lip wall front face | x 22.35 | ±0.15 | 0.25 gap behind rack A | — | claw_frame.py |
| **Lip wall back face** | **x 14.35** (GUIDE_T 8) | ±0.2 | — | — | strength round 2 change 1 |
| Slot A / slot B | z 38.25–48.5 / 5.75–16.25 | +0.2/−0 | 0.25 around the 10 mm necks | — | claw_frame.py |
| Pinion pass-through | Ø22.8 CAD, ≈22.6 printed | +0.3/−0 | pinion Ø21.7: 0.55 CAD / 0.45 printed radial | HOLE_COMP +0.2 | deep review 03 SYS-01 (≥ 20.6) |
| Top / front screw holes | Ø3.6 / Ø3.0 | +0.2 | M3 / M2.5 clearance | HOLE_COMP +0.2 | fdm-design-rules default |
| **Second tie** | y 24…32; post **x 14.35…22.35 (8 thick), foot flats z 17.85…36.75** (round 5; round 4 z 17.75, round 3 x 18.35…, z 19.25); web x 22.35…34.85, z 19.25…35.25 | ±0.2 | 1.15 from both racks' tips; 0.25 behind both racks (x 22.35 against 22.6); **flats 0.1 over the frame's rail block** | — | strength round 2 change 2; claw strength round 3; cover strength round 4 |
| **V-ridge under the post's foot (round 5)** | 90° V on x 15.25: base x 14.45…16.05 at the flats (z 17.85), virtual apex z 17.05, **tip cut flat at z 17.25** (0.4 wide); y 24.6…32 full, 45° lead-in from y 24 | ±0.1 | the frame's groove (x 14.45…16.05 at z 17.75, bottom 16.95) **0.1 clear per flank, horizontal** (0.071 normal); in print the groove's 0.2 mm layer corners take that 0.1 up, so the ridge bears on them at the nominal seat. Dry fit: 0.1 / 0.15 feelers (BUILD_GUIDE §4 step 9) | — | cover strength round 4 required change; `VSEAT_*` in claw_frame.py |
| **Anchor hole (round 4)** | Ø3.6 CAD at **(x 18.35, y 28)**, vertical through the top wall, lip and post (z 17.85…51.5), teardrop pointing +y in print; its edge 0.5 from the ridge's base | +0.2 | M3 × 45 socket head + **Ø7 × 0.5 washer** (round 5) | HOLE_COMP +0.2 | claw strength round 3 required change; cover strength round 4 |
| **Support pillars** | see the table above | — | removed before assembly | — | DFM round 2 fix 1; pillar B: DFM round 3 fix 1 |

measure_holes (geometry.json): Ø22.8 pass-through, 3 × Ø3.6 (2 top + the anchor, round 4), 2 × Ø3.0, all teardrops (270°). `cad_checks.py` proves the plate, top wall, lip, slots, pass-through, both ties with their 45° undersides, the tie's clearance to the pinion, and the pillars, which exist only as printed.

## Strength, predicted
From the strength-analyst's `strength_calc.py` and its what-if lines, on the round-3 parameters. The analyst's script does not model the second tie or the longer M2.5 engagement yet; those lines are its own what-if formulas.

| Required change | Round 2 | Round 3 |
|---|---|---|
| 1. Lip root at its end, one jaw blocked, jaws open (GUIDE_T 8) | 1.30 | **5.30**; both jaws (cyclic) 10.6; the lip above the first tie's post under the opening stall **6.64** (was 1.63) |
| 2. Upper piece under the opening stall (second tie) | 1.96 | plate strip under the second tie's web **5.95**; lip above its post **6.64**; its 4 × 8 post (the first tie's formula, t 4) 4.47 |
| 3. Strip under slot B, yaw stall (FRONT_Z0 −6) | 2.58 | **7.45** |
| Row 22: M2.5 pull-out under the opening stall (40 % share) | 2.51 | **4.0** with 11 mm engaged (2.56 at 7) |

The cover's lowest predicted SF is **3.58**: row 12, rack A's +y end on the upper piece near slot A's end (one jaw blocked). Without the second tie, the upper piece's own rows 8–9 would be 2.00 / 2.09; the tie carries that push.

## Parameters exposed by model.py
- model.py: HOLE_COMP, BED_CHAMFER, TO_PRINT, APEX_R, R_PASS, ZA0/ZA1, ZB0/ZB1, Z_CRES, SUP_X, SUP_A, SUP_B, SUP_GAP, TIE2_POST_T, TIE2_FOOT_Z, RIDGE_APEX_Z, RIDGE_TIP_Z (round 5).
- shared, in claw_frame.py: ANCHOR_XY (round 4), VSEAT_D, VSEAT_XC, VSEAT_CLR, ANCHOR_WASHER (round 5), X_F0, X_F1, FRONT_Z0, Z_TOP0, Z_TOP1, TOP_X0, RAIL_IN, LIP_X0, RAIL_X1, GUIDE_T, NECK_Z, SLOT_CLR, SLOT_A_END, SLOT_B_END, SLOT_FILLET, ACCESS_D, CRESCENT_Y, TIE_X0, TIE_Y, TIE2_Y, TIE_Z, CORNER_FILLET, CORNER_FILLET_Y0, TOP_CHAMFER, TOP_SCREWS, FRONT_SCREWS, M3_CLEAR, M25_CLEAR.

## Risks
- **The front plate is two pieces**, joined only through the ties and the top wall: both ties are in the strength check, and the claw proof test checks them. Since round 4 the second tie's post is also anchored on the frame's rail block by an M3 × 45.
- **The ridge must bear in the groove** (round 5): the cover's x hold now comes from the ridge's flank, so play there is what matters. Free slide before the flank bears costs strength fast (strength.md: play 0.025 → 3.72, 0.04 → 3.41, 0.05 → 2.83, 0.1 → 1.54). The CAD's 0.1 per flank is what the frame's 0.2 mm layer corners take up, so the nominal printed play is zero, but the frame's bulkhead top (z 48.5) lies exactly on a slice plane (layer 48.4–48.6 is sliced at 48.5) and can print 0.1 high or low, which moves the cover against the groove by as much. BUILD_GUIDE §4 step 9 checks both ways before any screw: a 0.1 feeler must not enter at the top wall (ridge holding the cover up), and a 0.15 feeler must not enter under the post's foot flats (ridge short of the flanks; that bounds the play to about 0.05). The anchor is driven snug only, over a Ø7 × 0.5 washer.
- **The two support pillars must come off before the pinion goes in.** BUILD_GUIDE §4 step 9 says so, and they sit inside the pass-through where they are easy to reach with pliers. A nub left on the pass-through's surface must be trimmed flush: the pinion clears it by 0.45 mm.
- **Long slots in a vertical wall would bridge 32 mm:** printed standing on its end, so the slots are vertical.
- **Tall thin print:** 5 mm brim, PETG first layer.
- **Assembly order is fixed** (cover before the jaws, pinion last): `claw_sequence_check.py` sweeps every step with exact solids, 0 mm³.
- **The cover is heavier:** 32.8 cm³ as fitted since round 4 (32.9 as printed, with the pillars) against 22.5 (lip +3.0, second tie +4.3, plate +1.3). The payload table uses it.
- **Spec §3 values that changed:**
  - front plate inner face x 32.85 → 34.85, plate x 34.85…39.85, z −6…48.5;
  - lip x 14.35…22.35 (was 18.35);
  - a second tie at y 24…32;
  - front screws M2.5 × 16;
  - envelope 39.85 × 64 × 57.5 (print 39.85 × 57.5 × 64).

## Claw DFM round 3 fix 1 (2026-10-26): pillar B carries all of piece (b). User-approved fix
- **What failed (design_review.md item 6).** Pillar B (1.0 thick, z 16.35…17.35, from y −6) carried only the lower half of piece (b)'s first layer (print z 39.0–39.2, z 16.25…18.33). At print z 39.1, 4.24 mm² of the 10.4 mm² layer started in mid-air, up to 1.13 mm from the pillar: a strip along the pass-through edge over the full plate thickness.
- **Change (model.py):** `SUP_B = (-6.0, CRESCENT_Y, ZB1 + 0.1, ZB1 + 1.1)` → `SUP_B = (-8.0, CRESCENT_Y, ZB1 + 0.2, ZB1 + 1.8)`, exactly as the reviewer's fix 1.
  - The pillar is now G y −8 → 6.75, z 16.45…18.05 (1.6 thick), x 35.35…39.35 as before.
  - It starts at y −8, where the plate is solid up to the pass-through at z 19.13, so the whole 1.6 mm foot grows out of the lower piece.
  - Unchanged: SUP_GAP 0.25 (one 0.2 mm layer under the piece), the clearance to slot B, the 1.6 × 4 mm section that snaps with pliers, BUILD_GUIDE §4 step 9, and `design()`, so `claw_sequence_check.py` stays valid.
- **Layer check, re-run on the new part.stl** (0.2 mm layers on a 0.04 mm raster; support = the union of the 3 layers below, so each pillar's top counts across its gap; allowance 0.3 mm). Every patch beyond 0.3 mm:

  | Print z | Where | Area | Max distance | Status |
  |---|---|---|---|---|
  | 38.5 | piece (a)'s first layer, the 0.5 mm x-inset strips at both plate faces | 0.40 + 0.33 mm² | 0.54 | as round 3, the reviewer's allowed x-inset |
  | 39.1 | piece (b)'s first layer, the 0.5 mm x-inset strips at both plate faces only | 0.52 + 0.44 mm² | 0.59 (the strips' corners) | **was 4.24 mm², up to 1.13 mm, across the full width** |
  | 41.1 | end of the corner fillet | 0.20 mm² | 0.60 | as round 3 |
  | 42.9–43.1 | slot A's r 1.5 roof apex | ≤ 2.6 mm² | 0.56 | as round 3 |
  | 47.5 | pass-through's teardrop apex | 4.6 mm² | 0.76 | as round 3 |

  No first layer of either piece now lies more than 0.3 mm beyond its pillar except at the 0.5 mm x-inset at the plate faces. Piece (b) overhangs pillar B by 0.20 mm (below) and 0.28 mm (above).
- **mesh_check:** overhang 0.27 %, bed contact 703.6 mm², thin walls 0, as before.
- **Checks.** `cad_checks.py` (exit 0): the pillar probe now tests z 16.45…18.05 from y −8, and two new checks prove pillar B's extent and its foot in the plate, and that piece (b)'s first layer stays within 0.3 mm of it in z.
- **Mass as printed:** 31.82 cm³ (+0.03, the pillar only; snapped off before assembly).

## Round 4 (2026-10-26: claw strength round 3, cover SF 1.23). User-approved
- **What failed (strength.md).** The reversed rack-B push lands on the upper piece's bottom strip at z 17.2: 27 N under an opening stall on jaw B (17.2 N in the 13 N desk crash). Its reaction is on the frame, and the cover could pass it there only through the 3 mm top wall behind the lip (SF **1.23**), the M3 holes over the bulkhead (1.53) and the first tie's post (1.56).
- **Change: the second tie's post is anchored on the frame's rail block**, exactly as the analyst's smallest fix.
  - `TIE2_POST_T` 4 → **8**: the post is x 14.35…22.35, like the first tie's.
  - `TIE2_FOOT_Z` = ZS − RAIL_IN = **17.75**: its full-depth part (y 24…32) reaches down to the rail block's top (was 19.25). Its 45° underside moves down 1.5 with it and now meets the lip at y 5; at y 5.9 it is 2.5 mm over the claw servo's case. The web is unchanged.
  - A vertical **Ø3.6 CAD** hole (M3_CLEAR + HOLE_COMP) at **`ANCHOR_XY` (18.35, 28)** (`claw_frame.py`, shared with the frame's pilot) through the top wall, the lip and the post, z 17.75…51.5, a teardrop pointing +y in print like the top holes. Walls: 2.2 to both post faces; 1.45 from the teardrop's tip to the cover's +y end. It is clear of the camera mount (y ≤ 22) and of rack A (x ≥ 22.6).
  - **Hardware:** one M3 × 45 socket head, driven snug (≤ 150 N, about 0.09 N·m) after the cover's other screws, into the frame's new Ø2.7 × 14 pilot: 33.75 through the cover, 11.25 engaged. BUILD_GUIDE §1 and §4 step 9 (with the 0.1 mm seat check and how to reach it: from above with a 2.5 mm L-key, before the camera goes on).
- **Predicted (analyst's what-if, 64 variants):** every cover row **≥ 4.64** (the first tie's post); M3 pull-out from the rail block **4.42** on the preload (4.11 with the lift); the 8 × 8 post round its hole 9.0; the frame's block root with the pilot 5.93.
- **Printing.** The post grows from the lip at 45° (G +y is up), so it needs no support. mesh_check: overhang 0.26 % (same 42.6 mm² area), bed contact 703.6 mm², widest bridge 2.0 mm, thin walls 0. The layer check (above) finds exactly the same 9 patches as before this round: the post and the anchor hole add none.
- **Assembly.** `claw_sequence_check.py` (exact solids): cover lowered 57 positions, both jaw slide-ins 91 positions each, the swept pinion, the stroke 0–44 every 1 mm and one tooth pitch in 0.1 mm steps: **0 mm³ everywhere**, `ok`. The post stays 0.25 behind both racks (x 22.35 against 22.6), like the lip. `assembly_check.py`: every named pose and sweep collision-free, `claw: clear`.
- **Checks.** `cad_checks.py` (20 checks, exit 0) adds: the 8 mm post, its foot at z 17.75 over y 24…32, its 45° underside (y 5 → 24), the anchor hole (Ø3.6 by `measure_holes`, open from z 17.75 to 51.5, teardrop +y) and the walls round it.
- **Mass.** +1.12 cm³: 32.8 cm³ as fitted (was 31.7), 32.9 as printed with the pillars. About 1.4 g more at the end of the arm; `torque_budget.json` has not been re-run for it.

## Round 5 (2026-10-26: cover strength round 4, the anchor held the foot only by friction). User-approved
- **What failed (strength.md and design_review.md, round 4).** The M3 × 45 held the post's foot in x only by its preload's friction (fdm-design-rules §4). With the preload crept away the foot slides through the screw's hole clearance and the push goes back through the top wall: SF **1.37** (spec §8 proof push 1.08). The bare socket head on the PETG top wall was SF 2.34 sustained (req 4).
- **Change (model.py), the reviewer's fix with the clearance the user set:**
  - `TIE2_FOOT_Z` 17.75 → **17.85** (`ZS − RAIL_IN + VSEAT_CLR`): the foot's flats stand 0.1 over the rail block. The post's 45° underside rises 0.1 with it (it meets the lip at y 5.1; 2.6 over the claw servo's case at y 5.9).
  - **V-ridge** along y under the foot (`ridge()`): the frame groove's 90° V raised `VSEAT_CLR` 0.1, so **0.1 clear per flank horizontally** (0.071 normal), virtual apex z 17.05 (0.8 under the flats), base x 14.45…16.05, from y 24 to the +y end. Its −y end is the post's 45° underside carried on down, a 45° lead-in over y 24…24.6.
  - **Tip cut flat at `RIDGE_TIP_Z` 17.25** (0.4 wide; the ridge stands 0.6 under the flats). Why: in the frame the groove's bottom layer (z 17.0–17.2, sliced at 17.1) is a 0.3 mm slot that will not print open, so its printed floor is about z 17.2. A full 0.8 ridge (sharp tip 17.05, about 17.14 once the nozzle rounds it) would land there and hold the cover up. The 90° flanks and the groove's 0.8 depth are kept.
  - The anchor hole now runs z 17.85…51.5. Its edge is 0.5 from the ridge's base.
  - Shared constants (`claw_frame.py`): `VSEAT_D` 0.8, `VSEAT_XC` 15.25, `VSEAT_Y0` 23.5, `VSEAT_CLR` 0.1, `ANCHOR_WASHER` (7.0, 0.5).
- **Why 0.1 per flank seats in print.** The frame prints the groove in 0.2 mm layers sliced at mid-height, so each layer's top corner stands 0.1 (horizontal) inside the CAD flank: corners at z 17.4, 17.6 and 17.8 (the block's top layer, sliced at 17.7, prints to 17.8). The ridge meets exactly those corners with the top wall on the bulkhead. The strength check takes the flank's resultant there (z 17.6).
- **Hardware:** an M3 washer Ø7 × 0.5 under the M3 × 45's head: 10.75 mm engaged (was 11.25). Washer + head clear the jaws by 3.16 over the stroke (3.47 before), the camera mount by 3.91 (4.66) and the Brio by 13.97 (14.25), exact solids.
- **Printing (G +y up).** The ridge is a vertical prism; its lead-in grows 0.2 per 0.2 mm layer (45°). Layer check of part.stl (0.2 mm layers, 0.02 mm raster, print z 50…64, x 13…39.9, G z 16.5…40; new material beyond the layer below grown 0.5 mm): **no new island**. mesh_check: overhang 0.26 %, bed contact 703.6 mm², widest bridge 2.0 mm, thin walls 0, as round 4.
- **Fit (exact solids).** Ridge in the frame's groove as fitted: 0 mm³ overlap, 0.0707 mm normal gap on each flank, flats 0.1 over the block, tip 0.3 over the groove's bottom. The post (x ≤ 22.35) against both jaws and the pinion, gaps 0…44 every 1 mm: **0.25 mm**, as round 4. `claw_sequence_check.py`: 0 mm³ on every path, the stroke and one tooth pitch in 0.1 mm steps.
- **Checks.** `cad_checks.py` (22 checks, exit 0) adds the ridge (flanks probed ±0.05 at three heights and three y, tip, lead-in), its fit in the frame's groove (overlap 0, gap 0.0707), the raised flats and underside, and the anchor hole's distance to the ridge.
- **Strength (strength.md, round 5).** Foot held in x by the ridge, no preload relied on: every verdict row ≥ 3.01 (the unchanged M2.5 pan head; the ridge's root 3.03, its flank bearing 3.61), the washer on the top wall 4.80 and the M3 pull-out on the preload 4.22 (req 4).
- **Mass.** −0.016 cm³: **32.78 cm³ as fitted, 32.93 as printed** with the pillars (round 4: 32.80 / 32.94).
- **Risk: play at the ridge.** See Risks: the frame's bulkhead top (z 48.5) sits exactly on a slice plane, so it can print 0.1 high or low; BUILD_GUIDE §4 step 9's two feeler checks catch either.

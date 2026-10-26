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
| B | −6 → 6.75 (emerges between y −5.8 and −5 as the pass-through's surface crosses it) | 16.35…17.35 (1.0 thick) | piece (b), first layer at y 7.0: z 16.26…18.25 |

**Removal and checks:**
- Both pillars stand inside the pass-through, clear of both slots: z ≤ 38.1 against slot A's 38.25, and z ≥ 16.35 against slot B's 16.25.
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
| **Second tie** | y 24…32; post x 18.35…22.35, z 19.25…36.75; web x 22.35…34.85, z 19.25…35.25 | ±0.2 | 1.15 from both racks' tips | — | strength round 2 change 2 |
| **Support pillars** | see the table above | — | removed before assembly | — | DFM round 2 fix 1 |

measure_holes (geometry.json): Ø22.8 pass-through, 2 × Ø3.6, 2 × Ø3.0, all teardrops (270°). `cad_checks.py` proves the plate, top wall, lip, slots, pass-through, both ties with their 45° undersides, the tie's clearance to the pinion, and the pillars, which exist only as printed.

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
- model.py: HOLE_COMP, BED_CHAMFER, TO_PRINT, APEX_R, R_PASS, ZA0/ZA1, ZB0/ZB1, Z_CRES, SUP_X, SUP_A, SUP_B, SUP_GAP, TIE2_POST_T.
- shared, in claw_frame.py: X_F0, X_F1, FRONT_Z0, Z_TOP0, Z_TOP1, TOP_X0, RAIL_IN, LIP_X0, RAIL_X1, GUIDE_T, NECK_Z, SLOT_CLR, SLOT_A_END, SLOT_B_END, SLOT_FILLET, ACCESS_D, CRESCENT_Y, TIE_X0, TIE_Y, TIE2_Y, TIE_Z, CORNER_FILLET, CORNER_FILLET_Y0, TOP_CHAMFER, TOP_SCREWS, FRONT_SCREWS, M3_CLEAR, M25_CLEAR.

## Risks
- **The front plate is two pieces**, joined only through the ties and the top wall: both ties are in the strength check, and the claw proof test checks them.
- **The two support pillars must come off before the pinion goes in.** BUILD_GUIDE §4 step 9 says so, and they sit inside the pass-through where they are easy to reach with pliers. A nub left on the pass-through's surface must be trimmed flush: the pinion clears it by 0.45 mm.
- **Long slots in a vertical wall would bridge 32 mm:** printed standing on its end, so the slots are vertical.
- **Tall thin print:** 5 mm brim, PETG first layer.
- **Assembly order is fixed** (cover before the jaws, pinion last): `claw_sequence_check.py` sweeps every step with exact solids, 0 mm³.
- **The cover is heavier:** 31.7 cm³ against 22.5 (lip +3.0, second tie +4.3, plate +1.3). The payload table uses it.
- **Spec §3 values that changed:**
  - front plate inner face x 32.85 → 34.85, plate x 34.85…39.85, z −6…48.5;
  - lip x 14.35…22.35 (was 18.35);
  - a second tie at y 24…32;
  - front screws M2.5 × 16;
  - envelope 39.85 × 64 × 57.5 (print 39.85 × 57.5 × 64).

VERDICT: FAIL

# DFM review, round 2: 20261026-rover-chassis

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/{iso,top,front,right,bottom}.png, print_requirements.json, rover_frame.py, tools/hobby_parts.py (N20_100RPM), tools/cadlib.py, assembly_check.py/json, round-1 design_review.md and strength.md. library/lessons.md and materials.csv are empty, so the fdm-design-rules defaults apply (HOLE_COMP +0.2).
Outputs are current: a fresh in-memory `build()` gives 115 008.31 mm³ and 154 × 76 × 40, identical to geometry.json. That still holds after the architect's 05:46Z update (idler bolts M3 × 35, class 12.9; in model.py only the docstring changed). Also read: assembly BUILD_GUIDE.md.
Extra evidence: probe scripts using build123d slab sections and `is_inside` point tests on `design()`. They work in the world frame; print z = world z − 8.68.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 154.0 × 76.0 × 40.0, fits_bed true, margin 5 |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight true, min_z 0 |
| 3 | Orientation | PASS | Floor down, open top up, as the brief says (iso.png, front.png) |
| 4 | Load paths vs layers | PASS (justified) | The wheel-bolt, journal and drop moments load the wall roots across the layers. The brief says so and answers with 4.5 mm walls, Ø20 bosses, the 30 × 24 idler block and 3 mm floor fillets |
| 5 | Bed contact | PASS | 11 362 mm² (mesh_check). PETG on the smooth PEI sheet needs a glue release layer in preflight (material-selection) |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | **FAIL** | (a) **The idler-slot roof floats.** The flat roof at Z_A + 1.8 (x 116.7–123.3, \|y\| 32–35.4) is bounded by the two teardrop tips (0.75 mm each side), the tub interior and the nut slot. Slab sections at +0.05, +0.2, +0.4 and +0.6 mm above it each show a separate solid of 22.5 to 26.2 mm², with the empty slot below (point tests empty from z 18.98 to 22.38). It joins the wall only at +0.74 mm, the tip height. mesh_check calls it a bridge (z 13.8, span 3.4, length 6.51), but no side of it is anchored for about 4 layers. (b) **The cradle cheeks overhang.** The cheeks (x ±6.3–8.3) and rear-stop posts start on a cradle only ±7.0 wide (CRADLE_HALF_X), leaving flat 1.3 mm ledges 25.0 and 1.7 mm long (mesh_check z 6.99, span 1.3, 4 of each). Point tests are empty under x 7.2–8.2. The rest of the 390.7 mm² overhang area is anchored flat roofs: tie tunnels (4.0 × 14.0) and nut traps (3.46, plus the idler's 11.46; see R2) |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | WALL 4.5, FLOOR_T 2.5, column wall (8 − 2.8)/2 = 2.6, CHEEK_T 2.0. The tie-tunnel roof is 1.0 mm and not structural. thin_wall_warnings is empty |
| 8 | HOLE_COMP, teardrops | PASS | HOLE_COMP is applied everywhere: journal 10.7, bolts 3.6, pilots 2.8, switch 6.4 and sensors 16.6 (geometry.json), nut AF 6.0. Every wall hole is a teardrop pointing up, including the slot ends at l.148–149 (right.png, front.png) |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(outer, FLOOR_Z, 0.4)` l.98; bottom.png shows the bevel |
| 10 | Internal corners on load paths | **FAIL** | The floor fillets are done (3 mm 45° strips, l.103–106). But the Ø20 road-wheel bosses, the idler block and the journal boss meet the wall's inner face at sharp 90° corners (l.111, l.127–131). That 6 → 4.5 mm step is on the wheel-bolt, idler and journal load paths. Round-1 fix 8 and the strength round-1 boss fix (r 2, Kt 1.5) both asked for fillets there |
| 11 | Fasteners (§4) | **FAIL** | The nut traps pass: 5.5 + 0.3 = 5.8 AF printed (6.0 CAD), 2.6 deep for a 2.4 mm nut, flats up so the roof bridges 3.46. But **the idler is held in its slot only by bolt preload in PETG**, which §4 says not to rely on. The bare Ø5.5 head bears on about 5.5 mm² beside the Ø3.6 slot, and the nut on about 7 mm² of the nut-slot floor, because the slot band removes the rest. Strength round 1 (advisory) gave friction SF 2.0 at stall with 100 N of residual preload. Lid self-tappers: see R1 |
| 12 | Spec §3 dims are named parameters | PASS | AXLE_DX 120, IDLER_SLOT 4 and Z_A 20.68 (rover_frame). Journal HUB_D 10 + JOURNAL_CLR 0.5 + HOLE_COMP = Ø10.7 CAD (Ø10.5 printed), WALL 4.5 + JOURNAL_BOSS 1.5 = 6 long. NUT_AF 5.5 + NUT_CLR 0.3 = 5.8, NUT_DEPTH 2.6. All commented |
| 13 | Service temp ≥ 20 °C below softening | PASS | 40 °C against about 70 °C for PETG. Note: config/printer.json `materials_on_hand` is empty, and spec §6 defers the PETG check to slicing |
| 14 | Lessons | N/A | library/lessons.md has no entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |
| 16 | Fits and assembly (cross-part, carried from round 1) | PASS (notes) | The round-1 cross-part items are closed: the idler head clears the moved columns at both slot ends (head edge at x 113.25 against the column at x ≤ 104, and x 126.75 against the front wall at 130.5); the face screws are gone; the tie has a tunnel; the columns are joined. Bolt lengths: M3 × 45 reaches y 77, where the wheel stack needs 75.5; M3 × 35 reaches y 67, where the idler stack needs 63. The sprocket-hub vs N20-bushing clash is fixed in the sprocket job. assembly_check.py places its axle bolt at y 12.9–57.9 with no head; the real bolts have the head at y 29–32 and the shank from y 32, so the reported "clear" doesn't cover them. I checked them by hand above (R4) |

## Required fixes

1. **Make the idler slot a true hull of its two teardrops (rule §2, overhangs and bridges).** At l.150, raise the slot box's top from Z_A + r (1.8 above the axle) to the tip height Z_A + r·√2 (2.55). The roof then becomes one 8 mm bridge, anchored on both 45° flanks, instead of a floating 22.5 to 26.2 mm² patch (slab sections in item 6). The bolt also gains 1.05 mm of headroom, so roof sag can't bind the slide (spec §8: "idler bolts slide the full ±4 mm"). The nut slot (top at +3.0) is unaffected.
2. **Stand the cradle cheeks and rear-stop posts on the cradle (rule §2, overhangs).** Raise CRADLE_HALF_X from 7.0 to 8.3 (= MOTOR.gb_w/2 + 0.3 + CHEEK_T), or run the cheeks and posts down to the floor. Today 1.3 mm of each cheek's 2.0 mm base hangs in the air (mesh_check z 6.99, span 1.3 × 25.0 and × 1.7, four of each), so the cheek that holds the motor against its reaction torque joins the cradle along only 0.7 mm. The tie tunnel, at ±(CRADLE_HALF_X + CHEEK_T + 2), still exits both sides.
3. **Fillet the boss-to-wall joins (rule §2, internal corners on load paths and abrupt thickness changes).** Add r 1.5 fillets, or 1.5 × 45° strips like the floor ones, where the Ø20 road-wheel bosses, the 30 × 24 idler block and the journal boss meet the wall's inner face (l.111, l.127–131). This finishes round-1 fix 8. The strength round-1 boss check assumed these fillets (Kt 1.5 instead of 2).
4. **Stop relying on preload to hold the idler (rule §4).**
   - (a) Add a positive stop that holds the idler bolt against at least 2 × 14.9 ≈ 30 N rearward without friction: for example, a jack screw bearing on the bolt from behind, or ratchet steps in the slot.
   - (b) Add an M3 DIN 9021 washer (Ø9) under each idler-bolt head to the spec §2 fastener list. A bare Ø5.5 head bears on about 5.5 mm² beside the slot today, and on about 3 mm² once fix 1 raises the roof; a Ø9 washer gives about 26 mm². The nut side (about 7 mm² today, about 4 mm² after fix 1) can't take a washer, which is why (a) is needed.
   - (c) Add "idler bolt not slid in its slot (pen mark)" to spec §8 proof test (2), as strength round 1 proposed.
   - BUILD_GUIDE step 6 currently locks the slot by friction ("tighten the idler bolt's nut (inside) to lock the slot"), which is exactly what §4 rules out. That step also calls the inside part the nut; it is the head.

## Round 1 fixes checked

1. Join the lid columns to the walls: **done.** The columns overlap the side walls by 0.5 mm (a 4.2 mm neck at x 97.9–102.1) and the rear wall by 2.5 mm, and the probe finds solid all the way from column to wall at z 20 and z 40 for all four. The joins aren't filleted, which is acceptable at the column SF of 190 or more found in strength round 1.
2. Idler travel ±4: **done.** The front columns moved to x 100.
3. Flat cantilevers under the bosses: **done.** The bosses and the idler block run to the floor, and the z 4.5 / 5.52 shelves are gone from mesh_check.
4. Teardrop idler slot: **partly done.** The ends are teardrops, but the flat roof sits below the tips (fix 1).
5. Zip tie: **done.** A 4.0 × 2.0 tunnel with a 1.0 mm roof (bridge 4.0 × 14.0). It is smaller than suggested but takes ties up to 3.6 × 1.2 mm; name that width in the spec.
6. Motor screw heads vs the sprocket hub: **superseded.** There are no face screws now.
7. M3 × 45 road-wheel bolts: **done** (spec §2).
8. Load-path fillets: **partly done.** The floor fillets are in, but the boss joins are still sharp (fix 3).

## Recommendations (not blocking)

- R1. Lid fastening (§4). The lid comes off for every battery charge (the cells come out of the holder to charge) and every idler re-tension. That is more than the "few times" §4 allows for self-tappers in PETG. Heat-set M3 inserts need Ø4.0–4.2 holes, and COLUMN_D should go from 8 to 10 so the boss is at least 2 × the insert OD (this was round-1 R3).
- R2. The idler nut slot's roof bridges 11.46 mm (x 114.27–125.73) at its opening in the outer face. It is anchored along its inner edge, so it will print, but check on the first print that the nut still slides the full slot.
- R3. Mini toggle: check that your switch's bushing still leaves room for its nut through the 4.5 mm wall. If it doesn't, counterbore the wall from the inside to about 2.5 mm thick around the hole.
- R4. In assembly_check.py, model the axle bolts as a head at y 29–32 plus a shank from y 32 to 77 (wheels) or 67 (idlers). For the motor, accept only the shaft-in-bore overlap instead of skipping the whole motor/sprocket pair (see the sprocket review).
- R5. slice_plan.json still overrides perimeters to 4, below the print_requirements minimum of 5. The slicing-lead should update it before SLICE.

VERDICT: FAIL

# DFM review: 20261026-rover-chassis

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/{iso,top,front,right,bottom}.png, rover_frame.py, assembly_check.py/json, tools/hobby_parts.py, tools/cadlib.py, library/ (lessons.md has no entries and materials.csv has no rows, so the fdm-design-rules defaults apply, including HOLE_COMP +0.2).
Extra evidence: a probe script (build123d `is_inside` and boolean overlap on `design()`), run from the scratchpad. Its numbers are quoted below.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit with a 5 mm margin | PASS | geometry.json bbox 154.0 × 76.0 × 40.0, fits_bed true, margin 5 |
| 2 | One watertight solid, min Z = 0 | PASS | solids 1, watertight true, min_z 0.0 |
| 3 | Orientation matches the brief | PASS | Floor down, open top up (iso.png, front.png) |
| 4 | Load paths vs layers | PASS (justified) | The wheel-bolt drop moment loads the wall roots across the layers. The brief says so, and spec §8 has a 2 kg proof test on a bolt |
| 5 | Bed contact | PASS | 11 362 mm² (mesh_check). PETG, little warping |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | **FAIL** | The idler boss (model.py l.95-96) is a flat 22 × 3 mm shelf cantilevered off the wall at print Z 4.5. mesh_check shows it as a "bridge" (z 4.5, span 3.0, length 22.0), but it has only one anchored edge: the probe point under it is empty. The Ø13 road-wheel bosses are 3 mm cantilevers too (bridges at z 5.52). The idler-slot ceiling bridges 8 mm flat plus the round ends, about 10.5 mm (see 8) |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | WALL 3.0, FLOOR_T 2.5, column wall (8 − 2.8)/2 = 2.6, thin_wall_warnings empty |
| 8 | HOLE_COMP and teardrops | **FAIL** | HOLE_COMP is applied everywhere (bolts 3.6, motor 4.8/2.2, sensors 16.6, pilots 2.8, nut AF 6.0). Wheel bolts, motor holes and sensor holes are teardrops and the switch has a 45° roof (right.png, front.png). But the idler slot ends are plain round cylinders (l.114-115), not teardrops |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(outer, FLOOR_Z, 0.4)` l.80 |
| 10 | Internal corners on load paths filleted | **FAIL** | The wall-floor edges (inner box, l.81) and the boss-to-wall joins (l.94-96) are sharp, on the wheel-bolt drop path. The 3 mm to 6 mm step at each boss is an abrupt thickness change (§2) |
| 11 | Fasteners per §4 | PASS (note) | Nut trap 5.5 + 0.3 = 5.8 printed AF (+0.2 comp = 6.0 CAD), 2.6 deep for a 2.4 mm nut, flats top and bottom so the ceiling is a 3.46 mm bridge. Lid self-tappers go into Ø2.6 pilots: see recommendation R3 |
| 12 | Spec §3 dims are named parameters | PASS | AXLE_DX/IDLER_SLOT/Z_A (rover_frame), face holes 1.6 + 0.4 (+0.2) in `gearmotor_wall_cutter`, NUT_AF + NUT_CLR = 5.8, NUT_DEPTH 2.6 |
| 13 | Service temp ≥ 20 °C below softening | PASS | 40 °C vs PETG about 70 °C |
| 14 | Lessons | N/A | library/lessons.md has no entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |
| 16 | Assembles with the listed hardware (cross-part) | **FAIL** | (a) The front lid columns block the idler tension slot. (b) The M1.6 motor screw heads hit the sprocket hub. (c) The motor zip tie has nothing to wrap around. (d) M3×40 is too short for the road wheels. (e) The columns are not joined to the walls. Details in the fixes below |

## Required fixes

1. **Join the lid columns to the walls.** All four Ø8 columns stand 0.5 mm clear of both walls: x −15.5 vs the inner wall at −16 (rear), 131.5 vs 132 (front), and |y| 34.5 vs 35. The probe found the 0.25 mm mid-gap points empty at all 8 locations. A 0.5 mm slit is below the smallest reliable feature (0.8 mm, rule §2), so the slicer will half-fuse it. The result is a free-standing 37.5 mm column with an uncontrolled join that takes the self-tapper torque. Fix: union a fill or web from each column to both adjacent walls, filleted r ≥ 1.5. Keep the column axes so the lid SCREWS still line up.
2. **Let the idler bolt travel its full ±4 mm.** The idler bolt head sits on the boss face at Y ±32, extending to |Y| 29. The front columns at (127.5, ±30.5), r 4, sit in its path. Overlap with a Ø5.5 × 3 head is 0 mm³ at +0, 0.5 at +1, 7.65 at +2 and 35.9 at +4. That leaves about +0.9 mm of forward (tensioning) travel instead of the +4 in IDLER_SLOT, and a washer makes it worse. Fix: end the two front columns above the head (start them at Z ≥ Z_A + 4.5 ≈ 25.2 world) as corner bosses merged into the walls, with a 45° underside. The pilot and lid holes stay where they are. Re-run assembly_check with the bolt head modelled at dx = −4 and +4.
3. **Remove the flat cantilevers under the bosses.** Give the idler boss (IDLER_BOSS 22 × 15 × 3) a 45° wedge underneath, sloping from the wall face down 3 mm, so its underside is ≤ 45° (rule §2; mesh_check bridge z 4.5, span 3.0, length 22.0). Do the same for the four Ø13 road-wheel bosses: a 45° point or wedge below, like a teardrop boss (bridges at z 5.52).
4. **Teardrop the idler bolt slot.** Make the slot outline a hull of two teardrops (45° roof, point +Z) instead of two round ends plus a flat top (l.114-116). Today the ceiling bridges about 10.5 mm (8 mm flat plus about 1.27 mm of >45° arc at each end). The bolt has only 0.3 mm radial clearance in the Ø3.6 slot, so ceiling sag can bind the slide (rule §2).
5. **Give the motor zip tie something to hold.** The cradle is solid from the floor to its top (probe: solid at Z 9.68, 12.18 and 12.68 under the groove at y ±18.25), and the tie groove is open on top (l.91). A tie around the can therefore only wraps the can and holds nothing. Fix: add a tunnel along X through the cradle under the groove, at least 4.5 wide (Y) × 2.5 tall, with its roof at least 2 mm below the cradle top. The roof then bridges 4.5 mm. Floor slots are an alternative.
6. **Clear the motor screw heads from the sprocket hub (cross-part).** The M1.6 face screws go in from outside. Their heads (ISO 7045 pan: dk 3.2, k 1.3) sit on the outer face at r 4.5 from the shaft and reach Y ±39.3, covering r 2.9 to 6.1. The sprocket hub (Ø11) ends at Y ±38.5, so they interfere by 0.8 mm. Fix it in one job: either Ø3.8 (CAD) × 1.5 deep counterbores here, which leaves 1.5 mm (< 1.8) under the heads, or the sprocket-side change in that job's review (hub end at ≥ 1.0 mm clear of the heads). The sprocket-side change is preferred.
7. **Road-wheel bolt length (spec §2 fastener list).** With the head on the boss face (Y ±32), an M3×40 ends at Y 72. The road wheel's outer face is at Y 71, and a washer plus nyloc needs Y 75.5. Use M3×45 for the 4 road-wheel bolts. M3×40 (or ×35) is fine for the idlers, which need Y 63.
8. **Add fillets on the load path.** Add r ≥ 1.5 to 2 on the inner wall-floor edges of both side walls and at the boss-to-wall joins (rule §2, internal corners and abrupt thickness change). If a kernel fillet fails, a 45° fillet strip (chamfer) works too.

## Recommendations (not blocking)

- R1. The HC-SR04 has no retention. The board rests only on its transducers in Ø16.6 holes, and the lid underside (Z 48.68) is 8.7 mm above the board's top edge, so it can slide back into the tub. Add two tie slots or a printed clip behind the board.
- R2. The switch cut-out's 45° roof removes the top edge. Check which edges carry the KCD11 snap latches and the panel thickness they accept (the wall is 3.0 mm). If needed, turn the switch 90° or thin the wall locally to about 2 mm.
- R3. The idler bolt heads are inside the tub, so every re-tension and battery swap means removing the lid. Self-tappers in PETG pilots wear out after a few cycles (§4), so consider M3 heat-set inserts (Ø4.0 to 4.2 hole, boss ≥ Ø9).
- R4. geometry.json `holes` failed ("type NoneType doesn't define __round__"). The hole sizes above come from model.py instead. Report this to toolsmith.

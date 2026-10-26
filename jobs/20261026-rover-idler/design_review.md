VERDICT: PASS

# DFM review, round 5: 20261026-rover-idler

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26

**Inputs:**
- this job: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, cad_checks.py, print_requirements.json, status.json, log.md, round-3 design_review.md;
- the sprocket's model.py (round-bore branch; `HUB_Z0_ROUND`, l.50);
- renders/{iso,front,right,top,bottom}.png, rebuilt with tools/render.py and looked at;
- rover_frame.py (`IDLER_HUB_Y0`, the stack constants);
- assembly_check.json (round 5), BUILD_GUIDE.md step 7;
- the chassis round-5 model and review.

The library is empty, so the defaults apply (HOLE_COMP +0.2).

**The round-5 change, checked against the model.**
- The idler's model.py only adds the round-5 docstring (git b7eb995).
- The shorter hub comes from the sprocket model's `HUB_Z0_ROUND = IDLER_HUB_Y0 − Y_T` = 43.7 − 55 = −11.3. The hub is cut from there to the disc (sprocket model.py l.93), and the Ø3.7 CAD bore runs through it (l.95).
- So the part is 14.8 tall: a 7.0 disc plus a 7.8 hub, where round 3 had 7.0 + 13.0.
- `IDLER_HUB_Y0` = 38 + 2.0 (nut plate) + 0.8 (Ø9 washer) + 2.4 (nut) + 0.5 (running washer) = 43.7, matching the chassis stack.

**Outputs are current.**
- A fresh in-memory `build()` gives 4 500.68 mm³ and 35.777 × 34.52 × 14.8, one solid, min Z 0. That is identical to geometry.json.
- part.stl is 4 500.0 mm³ and watertight.
- `tools/mesh_check.py` re-run: mesh_check.json is unchanged.
- `cad_checks.py`: 5/5 PASS.

**Extra evidence:** a layer-by-layer support analysis of part.stl (0.05 mm raster, mid-layer planes at 0.2 mm).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 35.8 × 34.5 × 14.8 |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight true, min_z 0.0 |
| 3 | Orientation | PASS | Outer disc face on the bed, hub up, as the brief says. `Rot(180, 0, 0)` in `build()` (l.37). front.png and right.png show the 7.0 disc on the bed and the Ø10 hub above it; bottom.png shows the full disc face with the bore |
| 4 | Load paths vs layers | PASS | Bore bearing and tooth bending lie in the layer plane. The bore still runs the whole part (14.8), so the hub isn't a cantilever. The hub is still longer than the 45° bearing spread from the disc that strength round 3 used (brief) |
| 5 | Bed contact | PASS | 514.9 mm² (the whole disc face), unchanged |
| 6 | Overhangs, bridges | PASS | overhang_pct 0, no bridges. Layer analysis: the only flagged cells are four 0.01 mm² specks at z 0.3, the diagonals of the 0.3 × 45° bed chamfer at tooth corners. Nothing else is unsupported, and nothing floats. The hub's top (z 14.8) is a plain top surface |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | Hub wall (10 − 3.7)/2 = 3.15 for its whole 7.8 length. Disc 7.0 thick. Teeth unchanged (2.7 at the root plus the chamfers, an unloaded 1.6 tip). thin_wall_warnings empty |
| 8 | HOLE_COMP; teardrops | PASS | ROUND_BORE 3.5 + HOLE_COMP 0.2 = Ø3.7 CAD, a vertical through-bore. geometry.json: hole 3.7, axis Z, 355° (the 5° gap is the bed chamfer's facet); cad_checks: through the whole 14.8. No horizontal holes |
| 9 | Bottom edges chamfered | PASS | 0.3 × 45° bed chamfer (sprocket model.py l.87; bevel visible in bottom.png). `elefant_foot_compensation` 0.2 is in print_requirements "min" |
| 10 | Internal corners on load paths | PASS (note) | Tooth roots are chamfered as before. The hub-to-disc corner is sharp but not on a bending path: the bore carries the bolt load along its whole length |
| 11 | Fasteners | PASS | It runs on the M3 × 40, class 12.9, fully threaded. Stack (assembly_check.json): running washer 43.2–43.7 on the wall nut; idler 43.7–58.5; washer; nyloc 59.0–63.0; tip 67.2, i.e. **4.2 past the nyloc** (≥ 1.5). With real 1.72–2.17 plate it is 3.56–4.46 (chassis review table). The jack screw holds the bolt, so no preload is relied on |
| 12 | Spec §3 dimensions are named parameters | PASS | ROUND_BORE (l.21) with HOLE_COMP gives the spec's Ø3.5 printed. Pitch radius RP 16.18 is from rover_frame. The hub's inner end, `IDLER_HUB_Y0` 43.7, is in rover_frame with its stack comment and is proved by cad_checks (z −11.3) |
| 13 | Service temp | PASS | 40 °C against ≈ 70 °C for PETG |
| 14 | Lessons | N/A | None recorded |
| 15 | FreeCAD reference | N/A | None |
| 16 | Fits and assembly (cross-part) | PASS (notes) | Details below. Clearances are those of a free-running fit; assembly_check: 160 bodies, 0 collisions, 7 teeth engaged, idler and jack screw clear at both slot ends |

On item 16:
- **Hub against the running washer.** The Ø10 hub end bears on the Ø7 running washer over r 1.85–3.5. That washer sits on the nut's face, whose corners reach r 3.18. So the hub's outer annulus faces only the washer, never the nut.
- **Clear of the chassis seat.** The hub (r 5, from \|y\| 43.7) clears the chassis's lip and stops (\|y\| ≤ 39) and the Ø9 washer (40–40.8).
- **Bore.** The 0.5 diametral clearance on M3 is a §3 free-running fit.

## Required fixes

None.

## Round-3 findings: still resolved

- **Checklist.** All round-3 items are still PASS on the 14.8 mm part (above).
- **R1 (rebuild after any sprocket change): done for round 5.** The sprocket's model.py changed (`HUB_Z0_ROUND` from rover_frame). This part was rebuilt, re-rendered and re-checked (cad_checks 5/5), and my fresh build matches.
- **Round-2 items:** still in place.
  - EFC 0.2 is in print_requirements.
  - BORE "round" is set and restored around the shared model (l.24–31).
  - The bolt is fully threaded.

## Round-5 checks in detail

- **Printability.** The part is now shorter and simpler, with nothing over 45° and no bridges (layer analysis). The bed face is unchanged.
- **Bore and hub.**
  - The bore is Ø3.7 CAD (3.5 printed) through 14.8, L/D 4.9 on the Ø3 bolt (6.7 before).
  - The 0.5 clearance lets it cock atan(0.5/14.8) = 1.93°, which is 0.60 mm at the tooth tips (r 17.9).
  - That is against the link notch's 0.5 a side (round 3: 1.43°, 0.45 mm). With 0.3 mm end play the Ø7 washers would allow 2.45°, so the bore sets the limit.
  - At full cock a tooth tip can touch a notch side; the links centre it as the teeth enter (brief). This is the cost of the user-approved shorter hub, not a printability defect.
  - If proof test 1 shows the idler rubbing, the remedy is a tighter bore (ROUND_BORE 3.3, 0.3 clearance: 1.16°, 0.36 mm). Don't make it pre-emptively: it trades away the round-1 running clearance.
- **Axial position.** The hub start now follows the chassis's outside stack: nut plate, washer and nut tolerances give −0.68 to +0.32 mm (chassis review). With the end play near 0.3 mm the disc can always settle in the link notch. Keep the spec's end play below 0.5, as BUILD_GUIDE step 7 says (0.3).

## Recommendations (not blocking)

- **R1. Stale text in design_brief.md.** The Orientation section still says "The bore runs the full 20 mm on the bolt". It is 14.8 now.
- **R2. Re-slice.** status.json correctly marks the round-4 slice (20 mm part) stale. Re-slice before approval: 2 per plate should now be under 1.16 h.

## Printing notes against print_requirements.json

PETG, 4 perimeters, 5 top and 5 bottom layers, 50 % gyroid, EFC 0.2, layers ≤ 0.2, 230–250 °C nozzle, 80–90 °C bed, ≤ 2 h. Outer disc face on the bed, hub up, as in the brief.

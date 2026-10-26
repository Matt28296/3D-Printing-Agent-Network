VERDICT: PASS

# DFM review, round 2: 20261026-rover-idler

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py (it runs the sprocket model with BORE = "round"), the sprocket's model.py, geometry.json, mesh_check.json, renders/{iso,top,front,right,bottom}.png, print_requirements.json, chassis model.py (slot, nut slot), rover_frame.py, assembly_check.json, round-1 design_review.md and strength.md. The library is empty, so the defaults apply.
Outputs are current: a fresh in-memory `build()` gives 4 858.19 mm³ and 35.777 × 34.52 × 20.0, identical to geometry.json. Spec and brief were re-read after the architect's 05:46Z update (idler bolt M3 × 35). Also read: assembly BUILD_GUIDE.md.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 35.8 × 34.5 × 20.0 |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight true, min_z 0 |
| 3 | Orientation | PASS | Disc down, hub up, as the brief says (iso.png, front.png) |
| 4 | Load paths vs layers | PASS | Bore bearing and tooth bending lie in the layer plane. The bore runs the full 20 mm on the bolt, so the hub doesn't act as a cantilever |
| 5 | Bed contact | PASS | 515 mm² |
| 6 | Overhangs, bridges | PASS | overhang_pct 0, no bridges |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | Hub (10 − 3.7)/2 = 3.15. The teeth are the same as the sprocket's (2.7 at the root, about 1.9 at RP) |
| 8 | HOLE_COMP, teardrops | PASS | ROUND_BORE 3.5 + HOLE_COMP 0.2 = Ø3.7 CAD, a vertical through-bore (geometry.json: hole 3.7, axis Z). No horizontal holes |
| 9 | Bottom edges chamfered | PASS (note) | 0.3 mm bed chamfer from the sprocket model (l.58 there); bottom.png shows the bevel round the disc and teeth. The bore's bed edge is cut after the chamfer, so it has none (R1) |
| 10 | Internal corners on load paths | PASS (note) | Same 0.5 × 45° tooth-root chamfers as the sprocket (see that review's R1) |
| 11 | Fasteners | PASS | Runs on the M3 × 35 idler bolt between the wall washer (hub end at y 38.5, against the 38.0 wall face + a 0.5 washer) and a washer + nyloc. From the block face (y 32) the bolt ends at y 67; the stack needs 63, so 4 mm of thread passes the nyloc |
| 12 | Spec §3 dims are named parameters | PASS | Running bore Ø3.5 printed / Ø3.7 CAD (ROUND_BORE + HOLE_COMP), matching spec §3 |
| 13 | Service temp | PASS | 40 °C against about 70 °C for PETG |
| 14 | Lessons | N/A | None recorded |
| 15 | FreeCAD reference | N/A | None |
| 16 | Fits and assembly (cross-part) | PASS | The bore has 0.5 mm diametral clearance on M3, the §3 free-running fit. The nyloc sets the axial play (spec §8: < 0.5 mm). assembly_check.json: 7 teeth sit in link notches on each idler. How the idler is held in its slot is a chassis issue (chassis fixes 1 and 4) |

## Required fixes

None.

## Round 1 fixes checked

1. Running bore: **done.** ROUND_BORE went from 3.2 to 3.5 printed (Ø3.7 CAD in geometry.json), and spec §3 was updated to match.
2. Bed-face chamfer: **done**, through the sprocket model (bottom.png).
3. Tooth-root fillets: **done as 0.5 × 45° chamfers**, through the sprocket model.

## Recommendations (not blocking)

- R1. Elephant's foot will narrow the first layer of the Ø3.7 bore, because `chamfer_plane_edges` runs before the bore is cut. Add `elefant_foot_compensation` ≥ 0.2 to the "min" block of print_requirements.json (as the links have), or chamfer the bore edge.
- R2. This job runs the sprocket's model.py, so re-build it after every sprocket change. Keep sprocket fixes 1 and 2 inside the `BORE == "D"` branch so this part doesn't change.
- R3. The bore still runs on bolt threads (the brief's own risk). A plain-shank bolt or a brass sleeve would wear better.

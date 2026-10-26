VERDICT: FAIL

# DFM review: 20261026-rover-idler

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py (it runs the sprocket model with BORE = "round"), the sprocket's model.py, geometry.json, mesh_check.json, renders/*.png, chassis model.py (slot and nut), rover_frame.py. The library is empty, so the defaults apply.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit | PASS | 35.8 × 34.5 × 20.0 |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight, min_z 0 |
| 3 | Orientation | PASS | Disc down, hub up (iso.png) |
| 4 | Load paths vs layers | PASS | Bore bearing and tooth bending are in the layer plane |
| 5 | Bed contact | PASS | 562 mm² |
| 6 | Overhangs, bridges | PASS | overhang_pct 0, no bridges |
| 7 | Walls | PASS | Hub (11 − 3.4)/2 = 3.8 mm. Teeth as on the sprocket (root 2.7, about 1.9 at the pitch radius) |
| 8 | HOLE_COMP, teardrops | PASS | ROUND_BORE 3.2 + HOLE_COMP 0.2 = Ø3.4 vertical through-bore (geometry.json hole 3.4, axis Z). No horizontal holes |
| 9 | Bottom edges chamfered | **FAIL** | No chamfer (inherited from the sprocket `build()`). Same 0.5 mm tooth-to-notch side clearance |
| 10 | Internal corners on load paths | **FAIL** | Sharp tooth roots, inherited from the sprocket (see the sprocket review) |
| 11 | Fasteners | PASS | Runs on the M3 idler bolt between the flush wall nut and a washer plus nyloc. Hub r 5.5 covers the 6.0 mm-tall nut slot |
| 12 | Spec §3 dims | PASS | Running bore 3.2 printed (ROUND_BORE) matches spec §3. Its value fails §3 of the rules: see 16 |
| 13 | Temperature | PASS | 40 vs about 70 °C |
| 14 | Lessons | N/A | None |
| 15 | FreeCAD reference | N/A | None |
| 16 | Fits and assembly | **FAIL** | The running bore prints Ø3.2 on an M3 (Ø3.0) bolt: 0.2 mm diametral clearance. That is a snug or locating fit; fdm-design-rules §3 wants ≥ 0.5 mm for free running. Separately, the idler can only move about +0.9 mm forward in its ±4 slot because the bolt head hits the chassis front lid column (chassis fix 2). That is a cross-part issue, not this model's |

## Required fixes

1. **Running bore.** Raise ROUND_BORE from 3.2 to 3.5 printed (3.7 CAD with HOLE_COMP): rule §3, free running ≥ 0.5 mm. Update spec §3 ("Ø3.2 printed, +0.15/−0") and the shared "Printed targets" line in the briefs to match.
2. **Chamfer the bed face** (0.3 to 0.4 mm). This comes through the sprocket model; fix it there (sprocket fix 3) and re-build both jobs.
3. **Tooth-root fillets** r 0.5, through the sprocket model (sprocket fix 4).

## Notes

- Any change to the sprocket's HUB_Z0 (sprocket fix 1a) also moves this idler's hub end. That is harmless here, because the nyloc sets the axial position. Just re-build this job after the sprocket changes, since model.py loads the sprocket file when it runs.
- The brief's own risk applies: the bore runs on bolt threads. A plain-shank bolt or a Ø3/Ø4 brass tube sleeve (bore re-sized to suit) would wear far better.

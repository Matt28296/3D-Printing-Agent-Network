VERDICT: FAIL

# DFM review: 20261025-arm-forearm

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), tools/hobby_parts.py, assembly_plan.md, library/lessons.md (no entries).
Outputs are current: `build()` gives 12046.2 mm³, matching geometry.json (12046.19 mm³). The geometry.json `holes` field holds an error, so I measured the holes from model parameters and part.stl sections.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 129 × 26 × 5 mm |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | Flat with the slot side on the bed (bottom.png) |
| 4 | Load paths | PASS | In-plane bending, along the layers |
| 5 | Bed contact | PASS | 2008.7 mm² |
| 6 | Overhangs ≤45°, bridges ≤10 mm | **FAIL** | This is the same MG996R double-arm slot as the upper link, with a ceiling at z 2.0 (301.9 mm²). The longest strand anchored at both ends is **10.6 mm**, at x = ±3.25 just outside the Ø6.5 access hole, where the first taper disc (r 5.41 at x 2.19) is wider than the hub. That is over the 10 mm rule |
| 7 | Walls ≥1.8 mm structural | **FAIL** | The ligament between each SG90 tab-screw pilot slot and the window is **1.55 mm** (section z 2.5, y 0: solid 71.65–73.20 and 96.10–97.70). It equals (hole_dx − length)/2 − CLR/2 − pilot/2 = 2.65 − 0.2 − 0.9. That is the modelled width. Uncompensated print shrinkage of the window and pilot would widen it to about 1.75 mm, and with HOLE_COMP (fix 3) it prints at about 1.55 mm. The self-tapping tab screw spreads into this wall, so it is structural and under 1.8. The partition between the horn-slot tip and the lightening slot is also 1.55 mm (z 0–2, solid 20.50–22.05; visible in bottom.png). It is backed by the 3 mm ceiling and carries no load, but it is needlessly thin |
| 8 | Fit holes / HOLE_COMP | **FAIL** | No `HOLE_COMP`. Spec §3 sets the SG90 window 22.9 × 12.4 at **+0.3/−0**, and it prints about 0.2 mm under. The MG996R horn slot has no compensation either |
| 9 | Bottom edges chamfered | PASS | `chamfer_bottom(design(), 0.4)` |
| 10 | Internal corners on load paths | PASS (advisory) | Window corners are sharp. Distal moment is small: 280 N·mm dynamic |
| 11 | Fasteners | PASS (see item 7) | SG90 tab screws go into Ø1.8 slotted pilots through 5 mm |
| 12 | Critical dims named | PASS | `L = 90.0` (spec 90 ±0.3), `CLR` |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C. Correct the brief's "~80 °C" |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

1. **Remove the 10.6 mm slot-ceiling bridge** (rule §2, checklist 6). Preferred: print front face (z = 5) down, so the slot opens upward with no bridge and everything else is a through-cut. Otherwise, cap the arm-taper half-width of the slot cutter at ≤5.0 mm.
2. **Raise the SG90 pilot-to-window ligament to ≥1.8 mm as printed** (rule §2 structural walls, checklist 7). The servo's tab-hole position fixes 2.65 mm, so the ligament only reaches 1.8 mm with a window end clearance ≤0.1 mm and a printed pilot ≤Ø1.5 mm (2.65 − 0.1 − 0.75 = 1.8). The other route is to justify 1.55 mm in design_brief.md and prove it on the arm-fit-test coupon: drive and remove an SG90 tab screw 3 times with no crack into the window. Applies to the gripper-base too.
3. **Apply `HOLE_COMP` (0.2 default)** to the SG90 window and the MG996R slot (rule §3, checklist 8; spec §3 −0 tolerance).
4. Change `LIGHT` x0 from 22 to 25 to thicken the 1.55 mm partition at the slot tip to 4.5 mm (rule §2).

VERDICT: FAIL

# DFM review: 20261025-arm-gripper-base

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), tools/hobby_parts.py, assembly_plan.md, gripper-jaw model.py, library/lessons.md (no entries).
Outputs are current: `build()` gives 15634.5 mm³, matching geometry.json (15634.5 mm³). The geometry.json `holes` field holds an error, so I measured the holes from model parameters and part.stl sections.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 104 × 25 × 19.4 mm |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | Flat with the wrist-horn pocket on the bed and the fixed jaw block rising from the front face (iso.png, right.png) |
| 4 | Load paths | PASS (justified) | The jaw-block root bends across the layers, and the brief justifies this with a 2.9 N grip force. Plate loads are in-plane |
| 5 | Bed contact | PASS | 2006.9 mm² |
| 6 | Overhangs / bridges | PASS (note) | SG90 single-arm pocket ceiling: the longest strand anchored at both ends is 6.95 mm, computed exactly (mesh_check gives the bounding-box span as 7.7 mm). Minor: the jaw block's fingertip corner overhangs the R6 plate corner by ≤1 mm. This is the downward face at z 4.99, x 94.0–95.0, y −13.9 to −11.4, 1.9 mm² (mesh_check bridge 2), and the small tab is visible at the right end of bottom.png |
| 7 | Walls ≥1.8 mm structural | **FAIL** | The ligament between each gripper-SG90 tab-screw pilot slot and the window is **1.60 mm** (section z 2.5, y 0: solid 21.65–23.25 and 46.10–47.70). Modelled, that is 2.65 − 0.2 − 0.9 = 1.55 (the slot extension points outward); the raster gives 1.60. With HOLE_COMP applied it prints at about that width. The self-tapping tab screw spreads into this ligament, so it is structural and under 1.8. The +y rail beside the window is Y1 − 6.2 = 2.8 mm, which is fine |
| 8 | Fit holes / HOLE_COMP | **FAIL** | No `HOLE_COMP`. The SG90 window (CLR 0.4) and the SG90 horn pocket (clearance 0.5) both print about 0.2 mm under. Acceptance requires "Gripper SG90 fits" |
| 9 | Bottom edges chamfered | PASS | `chamfer_bottom(design(), 0.4)` |
| 10 | Internal corners on load paths | PASS (advisory) | The jaw-block root is a sharp corner (right.png). The brief accepts it for a 2.9 N load; a 1 mm fillet would cost nothing |
| 11 | Fasteners | PASS (see item 7) | Wrist horn: centre screw plus 1 arm screw. Gripper SG90: 2 tab screws in Ø1.8 slotted pilots |
| 12 | Critical dims named | PASS | `GRIP_X = 40.0` (spec 40 ±0.3), `JAW_Y1 = −6.0` (spec −6.0 ±0.3), `JAW_TOP` = 5 + 9.4 + 5 = 19.4, which matches the jaw band of 14.4–19.4 |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C. Correct the brief's "~80 °C" |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

1. **Raise the SG90 pilot-to-window ligament to ≥1.8 mm as printed** (rule §2 structural walls, checklist 7). This needs a window end clearance ≤0.1 mm and a printed pilot ≤Ø1.5 mm (2.65 − 0.1 − 0.75 = 1.8). The other route is to justify 1.6 mm in design_brief.md and prove it on the arm-fit-test coupon: drive and remove a tab screw 3 times with no crack. This is the same fix as the forearm.
2. **Apply `HOLE_COMP` (0.2 default)** to the SG90 window (`CLR + HOLE_COMP`) and the wrist-horn pocket (0.5 + HOLE_COMP) (rule §3, checklist 8).

## Notes

1. Optional: set `JAW_X1` to 94 or round the block's end corner, so the fixed jaw stays inside the plate's R6 corner and loses the ≤1 mm overhang.
2. The jaw block is fused through a 0.01 mm overlap (`T − 0.01`). This is harmless, but you can drop it by starting the block at z = T.

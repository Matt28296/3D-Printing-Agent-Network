VERDICT: FAIL

# DFM review: 20261025-arm-upper-link

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), tools/hobby_parts.py, assembly_plan.md, library/lessons.md (no entries).
Outputs are current: `build()` gives 21245.9 mm³, matching geometry.json (21245.89 mm³). The `holes` field in geometry.json is `{"error": "type NoneType doesn't define __round__ method"}`, so the hole measurement failed in cad_build. I checked the holes from the model parameters and from sections of part.stl instead.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 146 × 34 × 6 mm; `fits_bed: true` |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | Flat with the back face (horn slot) on the bed. bottom.png shows the slot and the Ø6.5 access hole |
| 4 | Load paths | PASS | All bending is in the plate's plane, about the 34 mm-deep section, along the layers |
| 5 | Bed contact | PASS | 3078.5 mm² |
| 6 | Overhangs ≤45°, bridges ≤10 mm | **FAIL** | The horn-slot ceiling at z 2.0 is the only overhang (301.9 mm²). The longest strand anchored at both ends is **10.6 mm**, just outside the Ø6.5 access hole: the first taper disc of `horn_pocket_cutter` (r 5.41 at x 2.19) is wider than the hub circle. A section of part.stl at z 1 gives 10.55 mm at x −3.45. That is over the 10 mm rule, and the brief's "9.5 mm strand" is wrong. mesh_check reports the bounding-box span as 11.5 mm |
| 7 | Walls | PASS | T 6. Rails beside the window are (34 − 20.1)/2 = 6.95 mm. Pilot-to-window ligament is 2.40 mm (section z 3, y 5: solid 66.95–69.35 and 110.45–112.85). Web between the slot tip and the lightening slot is 5.5 mm. An opening test with a 1.8 mm disk at z 1 and z 4 finds no thinner region |
| 8 | Fit holes / HOLE_COMP | **FAIL** | No `HOLE_COMP`. Spec §3 sets the horn slot at **+0.2/−0** and the elbow window at **+0.3/−0**. Both print about 0.2 mm under, so the window clearance becomes 0.2 total, not 0.4 |
| 9 | Bottom edges chamfered | PASS | `chamfer_bottom(design(), 0.4)` is applied after the slot cut, so the slot mouth gets a lead-in too |
| 10 | Internal corners on load paths | PASS (advisory) | The window corners are sharp, but the lightening slot is a stadium. The window sits at the low-moment end, near the elbow |
| 11 | Fasteners | PASS | Elbow tab pilots run through the full 6 mm. Self-tapping is fine for a few assemblies |
| 12 | Critical dims named | PASS | `L = 100.0` (spec 100 ±0.3), `CLR`, `SERVO` |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C. Correct the brief's "~80 °C" |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

1. **Remove the 10.6 mm slot-ceiling bridge** (rule §2 bridges ≤10 mm, checklist 6). Preferred: print the link **front face (z = 6) down**. Every other feature is a through-cut, so the slot then opens upward with no bridge and no new overhang, and the elbow-servo tab face gets the flat bed finish. Keep `chamfer_bottom` on the new bed face. Otherwise, cap the arm-taper half-width of the slot cutter at ≤5.0 mm, as in the turntable fix.
2. **Apply `HOLE_COMP` (0.2 default, replace once measured)** to the elbow window (`CLR + HOLE_COMP`) and the horn slot (0.5 + HOLE_COMP) (rule §3, checklist 8; spec §3 −0 tolerances).

## Notes

1. Toolsmith: the hole measurement in `tools/cad_build.py` fails on this part (geometry.json `holes.error`). It does the same for turntable, forearm, gripper-base and gripper-jaw.
2. The MG996R tab-screw pilot (Ø2.6) is unverified against the actual servo-bag screw (see the base review, note 4).

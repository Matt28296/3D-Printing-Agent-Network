VERDICT: FAIL

# DFM review: 20261026-arm-claw-frame

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, print_requirements.json, renders/*.png (all 5 viewed), ../20261025-robot-arm-assembly/claw_frame.py, assembly_check.py/json, BUILD_GUIDE.md, tools/hobby_parts.py, tools/cadlib.py, library/ (empty, so skill defaults apply).
Outputs are current: `build()` gives 24422.2 mm³ and 9702.4 mm², the same as geometry.json. Wall and bridge numbers below come from ray casts through `design()` (G frame = print frame).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 35.65 × 64.0 × 39.0 mm, `fits_bed: true` |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, `min_z_mm: 0.0` |
| 3 | Orientation matches brief | PASS | Back face (wrist-horn pocket) on the bed, bulkhead and rail rising from it (iso.png, front.png; the pocket shows in bottom.png) |
| 4 | Load paths vs layers | PASS (justified) | Wrist-plate bending runs in the layers. The brief accepts the bulkhead root across the layers. Note for strength.md: the Brio's 10 N cable tug (about 50 mm above the bulkhead root, about 500 N·mm) and the cover/camera screws pulling out of the vertical top pilots also act across the layers |
| 5 | Bed contact | PASS | 1551.6 mm², PETG |
| 6 | Overhangs / bridges | **FAIL** | The flat top of the servo-window roof at z 33.8 spans y −11.8 to 1.1 = **12.9 mm** (the brief and claw_frame.py l.66 say so too). It is anchored only at its y ends: just above it the only solid along x is the bulkhead, x 4–10, open on both sides. mesh_check lists it as span 6.0 / length 12.9 because it takes the bounding-box short side, but here the short side is the unsupported one. The pocket ceiling (z 2.0, 7.9 mm) is fine |
| 7 | Walls | **FAIL** | Front pilots (y ±24, z 3): only **1.09 mm** of skin above the teardrop tip (solid z 4.91–6.00 by ray at x 22). That skin is the floor of rack B's track (x 19.4–27.4, 0.25 mm gap under the rack), and a self-tapping M3 goes in under it. Walls beside and below the pilot are 1.65. Other walls: top pilots 1.65 each side in the 6 mm bulkhead (x 4–5.65 and 8.35–10, about 1.75 printed); tab-pilot-to-window ligament 1.60 in CAD (about 1.80 printed, the same as the forearm and old gripper base accepted in round 2); `thin_wall_warnings` empty |
| 8 | HOLE_COMP / horizontal holes | PASS | `HOLE_COMP = HOLE_COMP_DEFAULT` (0.2, sourced) on the window (22.9 × 12.6 CAD), pocket (hub Ø7.9), clamp hole Ø2.6 and pilots Ø2.7 / Ø1.7. Front and tab pilots are teardrops pointing +Z (right.png). The window has 45° shoulders |
| 9 | Bottom edges chamfered | PASS (note) | `chamfer_plane_edges(plate, 0.0, 0.4)` on the plate blank (l.59, bottom.png). The pocket and clamp-hole mouths are cut afterwards. They are a static fit, so they can rely on `elefant_foot_compensation` 0.2, which the slice uses. Rack B's track (z 6) and the rail face (x 19.15) are not bed faces |
| 10 | Internal corners on load paths | PASS (advisory) | Sharp at the bulkhead roots (rail top to bulkhead at x 10 / z 13; tail to bulkhead at x 4 / z 6), at the tail corners (x 4, y ±10) and at the window's lower corners. Nominal stresses are low (the bulkhead root is 64 × 6), but the proof test inspects these spots. See R1 |
| 11 | Fasteners (§4) | PASS | Engagement: M3×10 cover screws 7 mm and M3×18 with the camera 11.5 mm, both in the 14 mm top pilots. M3×12 front screws engage 9 of 10 mm. MG90S tab screws reach 5.5 mm into the 6 mm bulkhead. The M2×12 + Ø6 washer on the tail reaches x 3, clear of the bulkhead at x 4. Self-tapping is acceptable because the jaws slide in from the ends, so the cover is seldom removed |
| 12 | Spec §3 dims named and matching | **FAIL** | Spec §2 and §3 say "MG90S window 22.9 × 12.6 **printed** (+0.3/−0)". model.py makes 22.9 × 12.6 **in CAD** (`CLR, END_CLR = 0.4, 0.2  # ... (printed)` l.26, plus HOLE_COMP via l.63), which prints at about **22.7 × 12.4**, the brief's printed target. The other rows match named shared parameters with comments: ZS 22.5, X_B 10, T_W 6, RAIL_X1 19.15 |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

1. **Shorten the window-roof bridge to 10 mm or less.** Raise `WINDOW_ROOF` (claw_frame.py l.66; only this frame uses it) from 5.0 to at least 6.5 mm. At 7.0 the bridge is 8.9 mm and the roof top sits at z 35.8. That leaves 3.2 mm of solid under the bulkhead top and keeps clear of the top pilots at y −23 / 14 (they are 4.85 and 6.55 mm from the window). Rule §2 (bridges ≤ 10 mm). Evidence: item 6; right.png shows the shoulders.
2. **Thicken the skin over the front pilots.** Truncate each front pilot's teardrop flat at the top of its Ø2.7 circle, z 4.35, which leaves a 1.1 mm flat (model.py l.71–72, `teardrop_cutter`). The skin under rack B's track goes from 1.09 to 1.65 mm in CAD (about 1.75 printed), the same as every other pilot wall here. Rule §2 lists flat-top as an accepted profile for horizontal holes. Alternative: M2.5 self-tapping screws in a Ø2.2 CAD pilot (skin 1.9). Rule §2 (walls) and §4 (screws into plastic). Evidence: item 7. A thread bulge in 1.1 mm of skin rises straight into the 0.25 mm gap under rack B.
3. **Correct the window size in the spec.** In spec §2 and §3, change "22.9 × 12.6 printed" to "22.7 × 12.4 printed (22.9 × 12.6 in CAD)". Otherwise inspection will reject a correct print against "−0". This is the Architect's file. The model needs no change. Checklist item 12; fdm-design-rules §3.

## Recommendations (not blocking)

- R1. Fillet the bulkhead roots: r 2 at x 10 / z 13 (the servo tabs start at z 16.5) and r 1 at x 4 / z 6 (the Ø6 clamp washer reaches x 3). These are corners the proof test checks for whitening.
- R2. Pilot walls in the bulkhead are 1.65 mm (CAD). For margin, `BULK_T` 6.0 → 6.5 (bulkhead x 3.5–10, still 0.5 mm clear of the washer) moves the top screws to x 6.75 and gives 1.9 mm walls. The cover's top wall would then start at x 3.5.
- R3. geometry.json `holes` holds an error ("type NoneType doesn't define __round__"), so hole sizes had to be measured separately (toolsmith).
- Process note: part.gcode, slice_plan.json, slice_settings.json, slice_stats.json and validation.json appeared in this folder at about 05:24–05:25 UTC, before this DESIGN review existed. They were sliced from the current part.stl and must be redone after the fixes.

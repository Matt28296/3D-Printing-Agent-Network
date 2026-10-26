VERDICT: PASS

# DFM review (round 4): 20261025-arm-base

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26

**Why it reopened.** Deep review 01 B1 (status.json; log.md 06:39:59): the MG996R's lead can't cross a closed window. Design round 3 (log.md 10:25) did three things:
- cut a lead notch at each case end, through the 4 mm top plate only;
- set the tab screws to M3 × 12 + Ø7 washers (01 S3);
- updated the loads for the disc horn and the 0.4 mm ring gap (03 SYS-05) and for tipping (SYS-12).

**Inputs**
- This job: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, print_requirements.json, slice_plan.json, status.json, log.md and the round-3 review.
- Renders: all 5, regenerated with `tools/render.py` and viewed.
- Tools and assembly: `tools/hobby_parts.py` (`servo_mount_cutter`, `lead="notch"`), and the assembly job's assembly_plan.md and BUILD_GUIDE §4.
- Deep reviews: 01 (B1, S3, N7) and 03 (SYS-05, SYS-09, SYS-12).
- library/lessons.md: no entries.

**Outputs are current.**
- `build()` gives 89630.57 mm³ and a 110 × 104 × 40 bbox from (−55, −52, 0), the same as geometry.json.
- part.stl is watertight (89627.75 mm³).
- `tools/mesh_check.py`, re-run in memory, gives exactly the committed mesh_check.json.
- The volume fell by 66.6 mm³ from round 3 (89697.2). That is exactly the two notches: 2 × 4.6 × 1.81 × 4.0 mm (the window already covers the first 0.3 mm past each case end). Nothing else changed.

**Method.** Exact OCC distances between the hole outlines on horizontal sections of `build()`, in the print frame: top plate z 0–4 on the bed, bosses z 4–10.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 110 × 104 × 40 mm, inside 240 × 200 × 210; `fits_bed: true` |
| 2 | One watertight solid, min Z 0 | PASS | `solids: 1`, `watertight: true`, `min_z_mm: 0.0` |
| 3 | Orientation matches the brief | PASS | Upside down, top plate on the bed. bottom.png shows the bed face: window, a notch at each end between the pilot pairs, cable slot, pilots. iso.png shows the open box upward |
| 4 | Load paths | PASS | The plate takes the tab-screw loads, and now also the ring's share of the overturning moment through the 3 ring screws (spec §4). Those are in-plane or plate bending, along the layers. Tab-screw pull-out puts the boss-to-plate layers in compression. The notches don't change this |
| 5 | Bed contact | PASS | 10191.7 mm² of PETG (was 10208.3; the notch mouths take the difference) |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | `overhang_pct` 0.0. The notches are vertical cuts through the bed layers, with nothing printed over them (bottom.png, top.png). The four mesh_check "bridges" (z 4.01, span 0.01, length 0.02, area 0.0) are slivers, not bridges. The notch cutter is clipped 0.01 mm below the plate (model.py:71), and its corners (12.31, ±2.30) touch the Ø6.5 bosses: at z 4.005 the boss outline runs through that corner, and at z 4.02 the bosses are whole. Below print resolution. USB slot: 45° roof (right.png). Jack: teardrop |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | **Notch → nearest pilot: 1.839 mm CAD at all four pilots.** Sections at z 2.0 and 3.99 give (12.31, ±2.30) → (13.33, ±3.83), mirrored at x −32.61. That is ≈ 2.04 printed (both edges print 0.1 mm inward) and holds 4 extrusion lines. Other walls: window end → pilot 2.2 CAD; boss wall 1.85 (z 7.0); pillar hole to cavity 2.2; ring pilot to edge 3.1. `thin_wall_warnings: []`. Below the plate the 4 × 1.3 ribbon clears the bosses: at y ±2 they start 2.65 mm past the case end, and at the ribbon's outer face (1.3 out) they are 3.05 mm off the centreline, as the brief says |
| 8 | HOLE_COMP; horizontal holes | PASS | `HOLE_COMP = HOLE_COMP_DEFAULT` (model.py:18) goes into both `servo_mount_cutter` calls (model.py:67, 70). In CAD the notch is 4.6 wide (y ±2.30) and reaches 2.1 past the case end, ≈ 4.4 × 2.0 printed (spec §3). Window 41.3 × 20.3 CAD; pilots Ø2.8 (geometry.json). Horizontal holes: the jack is a teardrop pointing up in print; the USB slot has a 45° roof |
| 9 | Bottom edges chamfered | PASS (note) | `chamfer_plane_edges(outer, 0.0, 0.4)` (model.py:46) chamfers the bed outline. The new notch mouths on the bed face aren't chamfered, nor are the window and pilot mouths (as in round 3). slice_plan.json's `elefant_foot_compensation` 0.2 covers them |
| 10 | Internal corners on load paths | PASS (advisory) | The notches' far corners are sharp and sit 1.84 mm from the tab pilots, like the window corners accepted in rounds 1–3. Loads here are low (strength.md lowest SF 4.10). Note 2 gives an optional relief |
| 11 | Fasteners per §4 | PASS (note) | **Tab screws:** M3 × 12 + Ø7 washers (spec §2, 01 S3) engage 9 mm of the 10 mm through-pilot (plate + boss), so they can't bottom out. The washers spread the head load (§4, creep). **Ring:** M3 × 6, 3 mm into the 4 mm plate. **Cradle:** see note 1 |
| 12 | Spec §3 dims are named parameters | PASS | `SERVO_CLR` 0.4 (model.py:20) and `HOLE_COMP`. The notch is `MG996R.lead_notch_w` 4.4 / `lead_notch_reach` 2.0 (hobby_parts.py:74, sourced to deep review B1 at :55–63) via `lead="notch"` (model.py:70). The CAD matches spec §3: window 41.1 × 20.1 printed, notches 4.4 × 2.0 printed, pilots Ø2.6, pattern 48.5 × 10 (pilots at x 14.1 / −34.4, y ±5), ligament "2.0 printed" (2.04) |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG at ≈ 70 °C: a 30 °C margin. `materials_on_hand` in config/printer.json is empty, so check the spool before slicing (spec §6) |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

## Required fixes

None.

## Notes (not blocking)

1. **Cradle screws: no depth margin** (deep review 01 N7, still open).
   - The M3 × 10 with its 4 mm clamp reaches exactly the end of the 6 mm blind boss pilots (model.py:64).
   - A shallow-printed cradle counterbore puts the tip into the solid plate.
   - Running the cradle pilots 1 mm into the plate (to design Z −3) gives 1 mm of margin and still leaves 3 mm of plate above.
2. **Notch corners.** A 0.5 mm radius on each notch's two far corners would add ≈ 0.2 mm to the corner ligament (1.84 → ≈ 2.03 CAD). It stays 0.8 mm clear of a 1.3 mm ribbon lying against the case end.
3. **Brief.** design_brief.md gives the notch only in prose (4.4 × 2.0 mm printed), without spec §3's +0.2/−0 tolerance. Add it as a row in the critical-dimension table (rule §3).

## Round 3 → round 4

| Reason it reopened | Status | How I checked |
|---|---|---|
| 01 B1: the lead can't cross the closed window | Closed (DFM side) | Notches at both case ends, through the plate only (model.py:68–71). 1.839 mm CAD to the pilots. Vertical cuts, no overhang. The ribbon clears the bosses below the plate (#7) |
| 01 S3: tab screws | Closed | M3 × 12 + Ø7 washers in spec §2 and assembly_plan.md; 9 mm engaged of 10 (#11) |
| Round 3's passing items | Still pass | The volume change is exactly the two notches, so nothing else in the geometry moved |

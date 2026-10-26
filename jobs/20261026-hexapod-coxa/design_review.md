VERDICT: FAIL

# DFM review (round 2): 20261026-hexapod-coxa

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), the round-1 review, ../20261026-hexapod-assembly/{hex_frame.py, assembly_check.py, assembly_check.json, assembly_hexapod.png, assembly_plan.md, BUILD_GUIDE.md}, tools/hobby_parts.py, library/lessons.md (no entries). Section probes: `mesh.contains` on part.stl, at the points quoted below.

Outputs are current. model.py (05:19:31 UTC) is newer than part.stl (05:19:00), but `build()` gives 8144.95 mm³ and a 53.05 × 25.0 × 37.75 bbox from (−9, −18, 0), identical to geometry.json, so nothing was re-run. assembly_check.json (05:20:21) is newer than hex_frame.py and every hexapod model.py.

Numbers below are in frame C (z up in print), from the parameters and from `assembly_check.leg_frames`:
- Femur axis at (32, ·, 17).
- Femur-servo tabs at x 10.55–42.75, y −13.5…−11.0, z 11–23.
- Window at x 15.2–38.1, from z 10.7 up (roof apex 34.75).
- Vertical plate at x 9.25–44.05, y −18…−13.5.
- Femur back face at y −4.1.
- Stance foot at (77, 15.8, 87).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 53.05 × 25.0 × 37.75 mm, `fits_bed: true`. Six copies fit the plate |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, `min_z_mm: 0.0` |
| 3 | Orientation matches brief | PASS | The horizontal plate is on the bed and the vertical plate stands. The window roof and the pilot teardrops point +Z (front.png, iso.png) |
| 4 | Load paths | PASS | The brief accepts cross-layer bending of the vertical plate, because the horn pocket has to be on the bed. Its mitigation now exists in the model. The window floor is at z 10.7, leaving a 5.7 mm solid band (mid-plane probe at x 27: solid z 0–10.65). The 5 mm 45° gusset is real (YZ probe at x 27: solid to y −8.75 at z 5.2, −11.05 at z 7.5 and −13.35 at z 9.8; right.png). It does not run the "whole length" the brief claims (see #10b). The two posts above the window floor still carry the femur servo's out-of-plane moment across the layers: see #10a and the strength note under Recommendations |
| 5 | Bed contact | PASS | 788.6 mm² of PETG |
| 6 | Overhangs / bridges | PASS | `overhang_pct` 2.66. Horn-pocket bridge 7.9 mm at z 2.0 (≤ 10 mm). Roof 45°, teardrops 45°, and the gusset slope faces up. A 1.9 mm² patch at z 4.99 is the plate end overhanging the arm's r3 corner (probe (43.8, −17.8): void at z 4.9, solid at z 5.2). It is cosmetic, and fix 2 removes it. Two 0.8 mm² slivers at z 17.85 (span 0.17 mm) are the tops of the pilot slots' outer circles, 0.05 mm above the teardrop flank. They are negligible |
| 7 | Walls | PASS | Plate 4.5 mm. z 17 section: pilot-to-window ligaments are 1.55 and 1.6 mm CAD (≈ 1.8 printed), pilot to plate end 2.25 mm. Horn-pocket floor 3.0 mm. Hub wall at the horn tip 2.55 mm. `thin_wall_warnings: []` |
| 8 | HOLE_COMP / teardrops | PASS | `HOLE_COMP = HOLE_COMP_DEFAULT` (0.2) goes into both cutters. Pilots have `pilot_teardrop="-y"` (C +z, up). The window roof is `"-y"` (up) |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(br, 0.0, 0.4)` runs after the hub fillet and before the pockets. The bed outline is chamfered (bottom.png). The horn-pocket rim is not chamfered and relies on `elefant_foot_compensation` 0.2 (slice_plan.json) |
| 10 | Internal corners on load paths | **FAIL** | **(a)** The window's bottom corners at (15.2, 10.7) and (38.1, 10.7) are square. A 0.15 mm probe grid around each corner is solid on the post side and void on the window side right into the corner (front.png). Above z 10.7 the plate is only two posts, 5.95 × 4.5 mm each (z 11 section: solid x 9.28–15.18 and 38.10–44.03). Together they carry the femur servo's whole moment about C x into the band, across the layers. Nominal stress at that layer (estimate): the 4 N stance load with the foot 31.6 mm off the plate mid-plane gives 126 N·mm → 3.1 MPa, cyclic. The spec's 3 N shove, 76.3 mm below the window floor, adds 229 N·mm → 8.8 MPa together, against the brief's placeholder 12.5 MPa across layers. That is before any sharp-corner concentration. **(b)** The gusset runs only x 12.3–41.0 (probe at y −12, z 6.5). That is 3 mm short of each plate end and 1.7 mm inside the tab span (10.55–42.75). At x 10.5 and x 42.5 the z 5.3 section ends at the plate face (y −13.55), so the root corner is still sharp under the outer half of each post. **(c)** Hub-to-arm corner: fixed. The r2.5 fillet is present (probe (19.3, −6.2) is solid; points within 2.5 mm of the fillet centre (21.5, −4.0) are void; top.png, bottom.png) |
| 11 | Fasteners | PASS | Spec §2 and BUILD_GUIDE.md (BOM, step 4) now give an M2×10 centre screw. It passes the horn face by 10 − 0.5 washer − 3.0 floor = 6.5 mm, the same as the femur and tibia M2×12 (12 − 0.5 − 5.0). Tab screws: M2×8 self-tapping into Ø1.7 CAD teardrop pilots through the 2.5 mm tab and the 4.5 mm plate. The brief still says M2×12 for horn joints (fix 3) |
| 12 | Critical dims named | PASS | Spec §3: L_C 32.0 = `L_C` (hex_frame.py:24); the femur axis 17.0 below the back face = `Z_F = T_C + 12.0` (hex_frame.py:32). Both have source comments. Several model.py comments are still wrong (fix 3) |
| 13 | Service temperature | PASS | 40 °C against PETG ≈ 70 °C (30 °C margin) |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

1. **Give the window's two bottom corners a radius of at least 1 mm** (rule §2, internal corners on load paths; rule §1, cross-layer load; evidence #10a).
   - A fillet inside the window cannot reach 1 mm. With 0.1 mm printed end clearance and 0.2 mm side clearance, any radius over 0.5 mm hits a square servo-case corner.
   - Cut relief (T-bone) holes instead: Ø2–3 mm through the plate, centred on the post's inner face r above the floor, at (15.2, 10.7 + r) and (38.1, 10.7 + r). Each arc is then tangent to the window floor, and the post runs into the band through a radius.
   - Give each relief a 45° point upwards (teardrop) so it prints without support.
   - The reliefs only remove material. They stay above the gusset (top z 10.0) and below the pilots (which start at z 16.15).
   - Each relief narrows its post by r at that height, so the strength-analyst must size the post there (see Recommendations). If a post needs more section, lengthen VPLATE_X outward rather than thinning anything.
2. **Run the gusset the full plate length, x 9.25 → 44.05** (rule §2; round-1 fix 1 asked for "full-length" and "on the tab span"; the brief says "along its whole length"; evidence #10b).
   - At the hub end nothing is in the way: the hub is solid under x 9.25–12.25.
   - At the outer end, either square the arm's far-end corners (r3 → ≤ 0.5) or run the arm 3 mm past the plate. Either one also removes the z 4.99 overhang patch (#6).
   - The extended gusset stays within 25.7 mm of the femur axis (the tibia servo sweeps ≥ 28.4 mm) and 1.0 mm under the tabs.
   - Then rebuild and re-run mesh_check, render and assembly_check.py.
3. **Correct the documentation** (round-1 fix 4 was not done in model.py; rule §7; evidence: the parameter values from `build()`).
   - model.py:31, PILOT_X comment: "−19.4, 8.4" → −19.25, 8.55.
   - model.py:32, VPLATE_X: "9.1 … 43.9" → 9.25 … 44.05.
   - model.py:33, WIN_HALF: "6.4" → 6.3.
   - model.py:35, VPLATE_H: "37.85" → 37.75.
   - model.py:28 (ARM_Y) and the docstring: the femur plane is −4.1 … 2.9 and the arm clears it by 2.4 mm (not −3.8 … 3.2 and 2.7 mm).
   - design_brief.md: make the horn-joint line give M2×10 for the coxa (it still says M2×12, against spec §2 and BUILD_GUIDE.md), and describe the posts' cross-layer bending and the corner reliefs.

## Round 1 fixes checked

1. Vertical-plate root support: **partly done.**
   - `Z_F = T_C + 12` (hex_frame.py:32) gives the 5.7 mm band (window floor z 10.7, probe).
   - A 5 mm 45° gusset exists, 1.0 mm under the tabs (probe; right.png).
   - But the gusset stops 3 mm short of both plate ends, and the window corners above the band are still sharp (fixes 1–2).
   - assembly_check.py was re-run after the change (05:20 UTC): stance clear, femur −70…+90, tibia −170…0, coxae ±45, neighbours converge to 35.
2. Hub-to-arm fillet: **done**, r2.5 (`HUB_ARM_FILLET`; probe; top.png).
3. Coxa centre screw: **done** in spec §2 (M2×10) and BUILD_GUIDE.md. The brief still says M2×12 (fix 3).
4. Stale numbers: **partly done.** Spec §2 now says "22.9 × 12.6 CAD", but the model.py comments are unchanged (fix 3).

Round-1 advisories: the plate-end overhang over the arm's r3 corner is unchanged (fix 2 removes it). The lead-exit advisory is still open (below).

## Recommendations

- strength-analyst: check the posts in cross-layer bending about C x.
  - Window floor, z 10.7: two posts of 5.95 × 4.5 mm (less r after fix 1).
  - Pilots, z 17: widths 2.25 + 1.55 and 1.6 + 2.25 mm.
  - Loads: the stance load (≈ 126 N·mm) and the 3 N shove (≈ 229 N·mm).
- MG90S lead exit (round-1 advisory, still open): the lead leaves the case at the hub-side end (C x ≈ 15.4), where the printed end clearance is ≈ 0.1 mm. A lead notch there would cut the left post, which is the critical section. Fit one real servo before printing six.
- The geometry.json `holes` field still holds an error (toolsmith).

VERDICT: PASS

# DFM review (round 5): 20261025-arm-turntable

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26 · third design attempt

**Why it reopened.** Links strength round 4 failed two things (log.md 13:06): the disc horn's 2 × M2 × 6 anti-rotation screws (SF 2.00) and the upright's window region under the yaw-stall sweep (2.80). Design round 5 (design_brief.md "Round 5") changed three things:
- `GUSSET_H` 70 → 90, cut off at the upright's top (model.py:37, 101–106);
- 4 × M2 × 8 anti-rotation screws through the disc horn's own holes, with pilots drilled at assembly (model.py:40–46);
- `print_requirements.json`: `bottom_solid_layers` 30 and `bottom_solid_min_thickness` 6.0.

**Inputs**
- This job: spec.md, design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json, print_requirements.json, slice_plan.json, log.md and the round-4 review.
- Renders: all 5, regenerated with `tools/render.py` and viewed.
- Assembly: BUILD_GUIDE §1 and §4 step 3, and `hobby_parts.py` (MG996R lead exit).
- Skills: fdm-design-rules, material-selection, build123d-cad. library/lessons.md has no entries.

**Outputs are current.**
- `build()` run in memory gives 90736.48 mm³, a 96 × 96 × 80.8 bbox from (−48, −48, 0) and 1 solid. That matches geometry.json.
- part.stl is watertight.
- `tools/mesh_check.py` re-run gives the committed mesh_check.json.
- The volume is +1540.0 mm³ on round 4 (89196.50). That is the gusset growth: 2 × 4 × [½(23 + 4.42) × 72.8 − ½ × 23 × 70] = 1545. Nothing else moved.
- `cad_checks.py` re-run: 14/14 PASS.

**Print frame:** the disk is at z 0–8 with the upright on it. The gussets sit at |x| 28.5–32.5 behind the upright (y < −12) and reach z 80.8.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 96 × 96 × 80.8 mm; `fits_bed: true` |
| 2 | One watertight solid, min Z 0 | PASS | `solids: 1`, `watertight: true`, bbox min z 0.0 |
| 3 | Orientation matches the brief | PASS | Disk down, upright vertical. right.png shows each gusset as a trapezoid, 23 mm deep at the disk and 4.4 mm at the top, flush with the upright's top (z 80.8). front.png: window, 45° roof, notches with 45° tops, teardrop pilots, all unchanged. bottom.png: the plain underside with only the Ø3.6 clamp hole |
| 4 | Load paths | PASS (justified) | The brief accepts upright bending across the layers and sizes for it with the across-layer allowable. The taller gussets carry more of it into the disk. The disk carries the anti-rotation screws in bearing, along the layers |
| 5 | Bed contact | PASS | **The disk's underside prints down.** 7105.0 mm², unchanged. The 30 solid bottom layers make the first 6 mm of the Ø96 disk solid: more shrink stress than 40 % gyroid, but PETG on a heated sheet with the 0.4 mm chamfer handles it |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | `overhang_pct` 0.0, `bridges: []`. The gusset's outer face leans 14.3° **inward** as it rises (23 → 4.42 deep over 72.8 mm), so each layer sits inside the one below. Its top is a flat 4.4 × 4 face, level with the upright. Round 4 note 2 is closed: the notch tops now reach the notch ends, and the two 0.02 × 7 mm flats are gone (0.28 mm² → 0.0) |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | GUSSET_T 4.0 (about 9 lines), DISK_T 8, UP_T 7. Window, notch and pilot walls are unchanged from round 4: ≥ 2.2 in every layer, with a 3D minimum of 1.775 CAD, as the brief now says. **Anti-rotation pilots** (drilled Ø1.5, 6 deep): at r ≥ 7, a pilot leaves ≥ 4.45 mm to the Ø3.6 clamp hole and 2.0 mm of disk above its end. The zone r 4–13 is plain solid down to 6.5 mm (cad_checks: 648 probes, 0 void). `thin_wall_warnings: []` |
| 8 | HOLE_COMP; horizontal holes | PASS | `HOLE_COMP` goes into the clamp hole and the shoulder cutter (model.py:108–113). The horizontal pilots are teardrops pointing up; the window and notch tops are 45°. The anti-rotation pilots aren't modelled: they are drilled through the horn at assembly (BUILD_GUIDE §4 step 3, model.py:40–41) |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(disk, Z0, 0.4)` (model.py:90) |
| 10 | Internal corners on load paths | PASS (advisory) | The gusset-to-upright and gusset-to-disk junctions are sharp, as in rounds 1–4. The root wedges (3 mm, 45°) are unchanged |
| 11 | Fasteners per §4 | PASS (note) | **Anti-rotation:** 4 × M2 × 8 self-tappers, 8 − 2.8 (disc) = 5.2 mm engaged in 6 mm pilots. All 5.2 mm sit inside the 6 mm of solid bottom layers (print_requirements.json `bottom_solid_layers` 30 at 0.2 mm, `bottom_solid_min_thickness` 6.0). That closes round 4 note 4. They are assembled once, so self-tappers are acceptable (§4). **Shoulder tab screws:** M3 × 12 + Ø7 washers; the tips stand 2 mm out of the back at x ±24.25, about 2.8 mm clear of the gussets' inner faces (x ±28.5), as before. **Clamp:** M3 × 14 + Ø9 washer, unchanged |
| 12 | Spec §3 dims are named parameters | PASS (note) | `GUSSET_H` 90 (model.py:37) and `ANTI_ROT_N`, `ANTI_ROT_L`, `DISC_HOLE_R_MIN`, `ANTI_ROT_PILOT_D`, `ANTI_ROT_PILOT_DEPTH`, `ANTI_ROT_ZONE` (:42–46) are sourced and match the brief's new rows. `XS`, `ZS`, `Z0` and `CLR` are unchanged. Spec §3's notch row still says "2.0 mm printed ligament" (note 2) |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG at ≈ 70 °C. `materials_on_hand` is empty: check the spool |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

**The gussets against the parts around them**
- **Shoulder servo body.** It is centred on x 0 and spans ±20.35, so it sits 8.15 mm inside the gussets' inner faces at every height. Its tab-screw tips are ≈ 2.8 mm clear.
- **Upper link.** It is on the upright's front (+Y) side, away from the gussets. Its ribs sweep ≥ 11.89 mm from the turntable over shoulder 0–180° (my sweep, upper-link review).
- **Disk edge.** The toe is at r 47.76, inside the disk's r 48.

## Required fixes

None.

## Notes (not blocking)

1. **Shoulder servo lead.** In the servo frame the MG996R lead leaves the case end 6 mm above the case bottom. On this part that is world y ≈ −26, at x ±20.35 (the lead end is unverified, so both ends are notched).
   - At the shoulder axis's height the 90 mm gusset's back edge is now at y −25.8 (it was −23.2 at 70 mm).
   - A 4 × 1.3 ribbon running straight out along x would meet the gusset's inner face 8.15 mm from the case end.
   - It is flexible, and it has to turn towards −Y and down to the base anyway.
   - Add one line to BUILD_GUIDE §4: route the shoulder lead back behind the gusset (−Y), not out sideways.
2. **Spec §3** (Architect). The notch row still says "2.0 mm printed ligament". The brief already carries round 4 note 1's corrected 1.775 CAD (≈ 1.97 printed); the spec should match it.
3. **Slicing.** slice_plan.json and slice_overrides.ini still give `bottom_solid_layers` 5. The new minimum is 30, with `bottom_solid_min_thickness` 6.0. The validator will hold the slice until slicing-lead updates the plan. Expect about +0.5 h (brief: 6.8 → ≈ 7.3 h of the 8 h limit).

## Round 4 → round 5

| Item | Status | How I checked |
|---|---|---|
| Strength round 4: window region (2.80) | Gussets 90 tall, printable | #3, #6: inward lean, no overhang; top flush with the upright |
| Strength round 4: anti-rotation (2.00) | 4 × M2 × 8 in solid plastic | #7, #11; zone probes; print_requirements.json |
| Round 4 note 1: brief overstated the ligament | Closed in the brief; spec open | Brief rows give 1.775 CAD (note 2) |
| Round 4 note 2: 0.02 mm flats | Closed | `overhang_pct` 0.0, `bridges: []` |
| Round 4 note 4: screws in sparse infill | Closed | 30 bottom layers / 6.0 mm |
| Round 4's passing items | Still pass | The volume change is the gussets |

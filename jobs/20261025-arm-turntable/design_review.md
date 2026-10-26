VERDICT: PASS

# DFM review (round 4): 20261025-arm-turntable

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26

**Why it reopened.** Deep review 01 B1 (status.json; log.md 06:39:59): the shoulder MG996R's lead can't pass its window in the upright. Design round 3 (log.md 10:25) changed four things:
- lead notches at both case ends, with 45° tops;
- the base servo's Ø25 disc horn under the disk (03 SYS-05), with no CAD change;
- an M3 × 14 ISO 4762 clamp (01 S2, 03 SYS-16);
- the SYS-04 moment in spec §4.

**Inputs**
- This job: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, print_requirements.json, slice_plan.json, status.json, log.md and the round-3 review.
- Renders: all 5, regenerated with `tools/render.py` and viewed.
- Tools and assembly: `tools/hobby_parts.py` (`servo_mount_cutter`, `lead="notch"`), and the assembly job's assembly_plan.md and BUILD_GUIDE §4.
- Deep reviews: 01 (B1, S2, S3, S4) and 03 (SYS-04, SYS-05, SYS-16).
- library/lessons.md: no entries.

**Outputs are current.**
- `build()` gives 89196.50 mm³ and a 96 × 96 × 80.8 bbox from (−48, −48, 0), the same as geometry.json.
- part.stl is watertight.
- `tools/mesh_check.py`, re-run in memory, gives exactly the committed mesh_check.json.
- The volume fell by 139.1 mm³ from round 3 (89335.6). That is the two notches plus their 45° tops: 2 × (4.6 × 1.81 + ½ × 1.8²) × 7 ≈ 139.3 mm³. Nothing else changed.

**Method**
- Print frame: disk z 0–8; upright y −12…−5; window x ±20.65; shoulder axis z 44.0; pilots at x ±24.25, z 39.0 and 49.0.
- Exact OCC distances between the hole outlines on vertical sections through the upright, at y −5.2, −8.5 and −11.8.
- Point-in-solid probes along x at fixed z, giving the wall each layer actually prints.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 96 × 96 × 80.8 mm, inside 240 × 200 × 210; `fits_bed: true` |
| 2 | One watertight solid, min Z 0 | PASS | `solids: 1`, `watertight: true`, `min_z_mm: −0.0` |
| 3 | Orientation matches the brief | PASS | Disk on the bed, upright vertical (iso.png, right.png). front.png shows the window's 45° roof, both notches with 45° tops, and the four teardrop pilots pointing up. bottom.png shows the flat underside for the disc horn, with only the Ø3.6 clamp hole |
| 4 | Load paths | PASS (justified) | The brief accepts upright bending across the layers and sizes for it with UP_T 7, 3 mm root wedges and 70 mm gussets. The notches narrow each side post beside the window from 12.35 to 10.54 mm over print z 41.7–48.1 (x 22.46 → 33). That is for strength's round-4 check against spec §4's 290–335 N·mm (note 3) |
| 5 | Bed contact | PASS | 7105.0 mm² (unchanged) |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | The notch outline in the mid-plane section is floor z 41.70 (x 20.65 → 22.46), end wall x 22.46 up to z 46.30, then a 45° top from (22.44, 46.30) to the window wall at (20.65, 48.10). So there is no flat ceiling. mesh_check's 0.28 mm² of overhang and two "bridges" (z 46.3, span 0.02, length 7.0) are one 0.02 mm × 7 mm flat per notch, x ±22.44…±22.46. That is where the triangle starts 0.01 mm inside the notch box (model.py:53) and the box runs 0.01 mm past the notch end (hobby_parts.py:181). It is 1/20 of a line width: cosmetic. Teardrops and the window roof are at 45° |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | **In every layer the wall is ≥ 2.2 mm.** Probes at y −8.5: z 39.0 solid x 20.65–22.855 (window to lower pilot); z 41.0–41.6 solid from 20.65 (pilot tip at z 40.98, notch floor at 41.7); z 47.7 21.05–23.735; z 48.0 20.75–23.275 (45° top to upper pilot). **3D minimum:** 1.775 mm CAD from each lower pilot's teardrop flank to the notch's lower-outer corner, (±23.72, 40.45) → (±22.46, 41.70); and 1.788 mm from the 45° top to the upper pilots. Those are diagonals across about 4 layers, not walls a layer prints. Perimeter count is set per layer, and the layers there are fully solid. They are ≈ 1.97 / 1.99 printed. The notch also stays off the pilots' own layer planes (z 39.0, 49.0), where a self-tapper would split a standing wall; the in-layer wall there stays 2.2 mm. DISK_T 8, UP_T 7, GUSSET_T 4. `thin_wall_warnings: []` |
| 8 | HOLE_COMP; horizontal holes | PASS | `HOLE_COMP` goes into the window, pilots and notch (`servo_mount_cutter(..., hole_comp=HOLE_COMP, lead="notch")`, model.py:92–93), and into `_notch_tops()` with the same `nw` and `reach` (model.py:49–50). Notch CAD: 4.6 tall (z 41.7–46.3), 2.1 past the case end (x 20.35 → 22.46), ≈ 4.4 × 2.0 printed. Pilots: Ø2.8 CAD teardrops pointing up in print (geometry.json `arc_deg` 270). Clamp hole Ø3.6. Every horizontal opening has a 45° top |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(disk, Z0, 0.4)` (model.py:74) |
| 10 | Internal corners on load paths | PASS (advisory) | Root wedges unchanged (3 mm, 45°). The notches' far corners are sharp, like the window corners accepted in rounds 1–3 |
| 11 | Fasteners per §4 | PASS (note) | **Clamp:** M3 × 14 ISO 4762 + Ø9 washer goes 4.6 mm into the metal spline (spec §2). The washer seats flat: the front wedge stops at \|x\| ≥ 6 (model.py:34), and the washer rim is 0.5 mm from the upright. The washer is there for creep (§4), and spec §2 allows re-tightening with an L-key past the upright (SYS-16). **Shoulder tab screws:** M3 × 12 + Ø7 washers in the teardrop pilots. Their tips stand 2 mm out of the back face at x ±24.25, 4.25 mm clear of the gussets. **Anti-rotation:** see note 4 |
| 12 | Spec §3 dims are named parameters | PASS | `XS` 10.15, `ZS` 60.5, `Z0 = horn_face_z(SERVO)` 16.5, `CLR`, `HOLE_COMP` (model.py:20–27). The notch comes from `MG996R.lead_notch_w` / `lead_notch_reach` (hobby_parts.py:74), and the 45° top from `_notch_tops()` (model.py:44–59). The CAD matches spec §3: clamp Ø3.4 printed, window 41.1 × 20.1 printed, notches 4.4 × 2.0 printed with 45° tops, axis (10.15, 60.5), disk underside Z 16.5 |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG at ≈ 70 °C. Check the spool: `materials_on_hand` is empty |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

## Required fixes

None.

## Notes (not blocking)

1. **The brief overstates the ligament.**
   - design_brief.md says "notch → nearest pilot 2.05 mm". That is the cutter's own check (hobby_parts.py:173–175), which treats the pilot as a plain circle.
   - The lower pilots' teardrop points aim at the notch, so the true minimum is 1.775 mm CAD, ≈ 1.97 printed (#7). It still passes.
   - Correct the brief, and spec §3's "2.0 mm printed ligament", to ≈ 1.97.
2. **0.02 mm flats.** Starting the triangle at the notch's top edge (`−nw / 2 − 0.01` at model.py:53) instead of 0.01 mm inside it would remove the two z 46.3 slivers from mesh_check. Cosmetic.
3. **For strength (round 4).** Two things to re-check:
   - the side posts beside the window are now 10.54 mm wide over the notch height (#4);
   - the 1.78 mm diagonal from the lower pilots to the notch corners now sits in the tab screws' tear-out path.
4. **Anti-rotation screws under the disc horn** (01 S4, BUILD_GUIDE §4 step 3).
   - The 2 × M2 × 6 are drilled through the horn into the bed face at assembly. They bite 1.0 mm of bottom skin (5 layers), then 40 % gyroid.
   - Spec §4 routes the base-servo stall through them and the clamp's friction.
   - If strength counts on them, a solid-infill modifier under the horn (r ≤ 13 mm, first 4 mm) gives them solid plastic. That is the slicing-lead's call.

## Round 3 → round 4

| Reason it reopened | Status | How I checked |
|---|---|---|
| 01 B1: the lead can't cross the closed window | Closed (DFM side) | Notches at both case ends with true 45° tops (outline in #6). No flat ceiling. In-layer walls ≥ 2.2 mm (#7) |
| 03 SYS-05: disc horn | Closed | Flat underside, no pocket (bottom.png). The disc horn needs no CAD change |
| 01 S2 / 03 SYS-16: M3 × 14 ISO 4762 clamp | Closed | Spec §2, assembly_plan.md and BUILD_GUIDE §4 step 4. The washer seat is unchanged (#11) |
| Round 3's passing items | Still pass | The volume change is exactly the notches and their tops |

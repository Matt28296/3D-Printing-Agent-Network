VERDICT: PASS

# DFM review (round 4): 20261025-arm-upper-link

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26

**Why it reopened.** Deep review 01 B1 (status.json; log.md 06:39:59): the elbow MG996R's lead can't pass its window. Design round 3 (log.md 10:25) changed:
- a lead notch at both case ends of the elbow window, through the 10 mm plate;
- the shoulder clamp to M3 × 14 (01 S2), plus 2 × M2 × 6 anti-rotation screws (S4);
- the tab screws to M3 × 12 + Ø7 washers (S3);
- the SYS-04 moments in spec §4.

**Inputs**
- This job: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, print_requirements.json, slice_plan.json, status.json, log.md and the round-2 review.
- Renders: all 5, regenerated with `tools/render.py` and viewed.
- Tools and assembly: `tools/hobby_parts.py` (`servo_mount_cutter`, `lead="notch"`), and the assembly job's assembly_plan.md and BUILD_GUIDE §4.
- Deep reviews: 01 (B1, S2, S3, S4) and 03 (SYS-04).
- library/lessons.md: no entries.

**Outputs are current.**
- `build()` gives 39496.47 mm³ and a 146 × 34 × 10 bbox from (−25, −17, 0), the same as geometry.json.
- part.stl is watertight.
- `tools/mesh_check.py`, re-run in memory, gives exactly the committed mesh_check.json.
- The volume fell by 166.5 mm³ from round 2 (39663.0). That is exactly the two notches: 2 × 4.6 × 1.81 × 10. Nothing else changed.

**Method.** Exact OCC distances between the hole outlines on horizontal sections of `build()` at print z 0.2, 5.0 and 9.8. Print frame: front face on the bed; elbow axis at x 100; pilots at x 65.6 / 114.1, y ±5.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 146 × 34 × 10 mm; `fits_bed: true` |
| 2 | One watertight solid, min Z 0 | PASS | `solids: 1`, `watertight: true`, `min_z_mm: −0.0` |
| 3 | Orientation matches the brief | PASS | Front face on the bed (`Rot(180, 0, 0)`, model.py:40). top.png shows the horn pocket opening upward. bottom.png shows the bed face: clamp hole, window with a notch at each end between the pilot pairs, 4 pilots |
| 4 | Load paths | PASS | In-plane and out-of-plane bending run along the layers. The brief's centre-screw clamp carries horn pull-out. The notches don't change this |
| 5 | Bed contact | PASS | 3881.1 mm² (was 3897.8; the notch mouths take the difference) |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | `overhang_pct` 0.0, `bridges: []`. The notches are vertical cuts through a flat plate: no ceiling. The pocket is an open top recess |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | **Notch → nearest pilot: 1.839 mm CAD at all four pilots**, the same at z 0.2, 5.0 and 9.8: (112.31, ±2.30) → (113.33, ±3.83), mirrored at x 67.39 → 66.37. That is ≈ 2.04 printed and holds 4 extrusion lines. Other walls: rails beside the window (34 − 20.3) / 2 = 6.85; outer pilots to the plate end 5.5 (5.3 at the bed chamfer); horn pocket to the plate end 4.4. `thin_wall_warnings: []` |
| 8 | HOLE_COMP; horizontal holes | PASS | `HOLE_COMP` goes into `horn_pocket_cutter` and `servo_mount_cutter(..., hole_comp=HOLE_COMP, lead="notch")` (model.py:33–35). Notch CAD: 4.6 wide, 2.1 past each case end (x 110.2 → 112.31 and 69.5 → 67.39), ≈ 4.4 × 2.0 printed. Window 41.3 × 20.3 CAD; pilots Ø2.8 (geometry.json). No horizontal holes |
| 9 | Bottom edges chamfered | PASS (note) | `chamfer_plane_edges(link, T, 0.4)` (model.py:32) on the bed (front) face. The notch, window and pilot mouths on the bed face rely on `elefant_foot_compensation` 0.2 (slice_plan.json) |
| 10 | Internal corners on load paths | PASS (advisory) | The notches' far corners are sharp, 1.84 mm from the pilots, like the window corners accepted in rounds 1–2 in this 10 mm plate (strength.md lowest SF 3.90) |
| 11 | Fasteners per §4 | PASS (note) | **Elbow tab screws:** M3 × 12 + Ø7 washers, 9 mm into the 10 mm through-pilots, so they can't bottom out. **Shoulder clamp:** M3 × 14 + Ø9 washer through the 8 mm floor, 4.6 mm into the metal spline. The washer seats on the flat front face. **Anti-rotation:** see note 2 |
| 12 | Spec §3 dims are named parameters | PASS | `L` 100.0, `T` 10, `CLR` 0.4, `HOLE_COMP` (model.py:19–26). The notch is `MG996R.lead_notch_w` / `lead_notch_reach` (hobby_parts.py:74). The CAD matches spec §3: axis distance 100 (servo frame at x 100), window 41.1 × 20.1 printed, notches 4.4 × 2.0 printed with "2.0 mm printed ligament" (2.04) |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG at ≈ 70 °C. Check the spool: `materials_on_hand` is empty |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

## Required fixes

None.

## Notes (not blocking)

1. **Notch corners.** A 0.5 mm radius on each notch's far corners adds ≈ 0.2 mm to the corner ligament. It stays clear of a 1.3 mm ribbon lying against the case end.
2. **Anti-rotation screws** (01 S4, BUILD_GUIDE §4 step 3). The 2 × M2 × 6 are drilled through the horn's arms into the pocket floor at assembly. They bite the floor's 1.0 mm of top skin (5 layers), then 40 % gyroid. If strength counts on them, a solid-infill modifier under the pocket gives them solid plastic. That is the slicing-lead's call.
3. **Brief.** design_brief.md gives the notch only in prose, without spec §3's +0.2/−0. Add it as a row in the critical-dimension table (rule §3).

## Round 2 → round 4

| Reason it reopened | Status | How I checked |
|---|---|---|
| 01 B1: the lead can't cross the closed window | Closed (DFM side) | Notches at both case ends: vertical cuts, 1.839 mm CAD to the pilots (#6, #7) |
| 01 S2 / S3 / S4: fasteners | Closed | Spec §2: M3 × 14 + washer, M3 × 12 + washers, 2 × M2 × 6 (#11) |
| Round 2's passing items | Still pass | The volume change is exactly the two notches |

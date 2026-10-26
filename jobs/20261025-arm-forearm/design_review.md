VERDICT: FAIL

# DFM review (round 4): 20261025-arm-forearm

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26

**Why it reopened.** Deep review 01 B1 and B2 (status.json; log.md 06:39:59): the wrist servo's lead can't pass its window, and the MG90S isn't the SG90 the model used. Design round 3 (log.md 10:25) changed:
- the wrist servo SG90 → MG90S, a 22.8 × 12.2 body (B2, S1, SYS-18);
- `lead="notch_shift_pilot"`: a notch at the shaft end, and that end's pilot moved 1.3 mm out (B1, option 1);
- the fitting pose: forearm 60° below the upper link (SYS-03);
- spec §4 loads for the MG90S and SYS-04.

**Inputs**
- This job: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, print_requirements.json, slice_plan.json, strength.md, status.json, log.md and the round-2 review (with its round-3 note).
- Renders: all 5, regenerated with `tools/render.py` and viewed.
- Tools and assembly: `tools/hobby_parts.py` (`MG90S`, `servo_mount_cutter`, `_pilot_xy`); the assembly job's assembly_plan.md, BUILD_GUIDE §4 and assembly_check.json.
- Deep reviews: 01 (B1, B2, S1, S2, S4) and 03 (SYS-03, SYS-04, SYS-18). For comparison: the hexapod coxa and femur reviews.
- library/lessons.md: no entries.

**Outputs are current.**
- `build()` gives 29235.18 mm³ and a 129 × 26 × 10 bbox from (−25, −13, 0), the same as geometry.json.
- part.stl is watertight.
- `tools/mesh_check.py`, re-run in memory, gives exactly the committed mesh_check.json.
- The volume fell by 146.2 mm³ from round 2 (29381.42). That is exactly the larger window plus the notch: (23.2 × 12.8 − 22.9 × 12.6) × 10 + 4.4 × 1.41 × 10. Nothing else changed.

**Method.** Exact OCC distances between the hole outlines on horizontal sections of `build()` at print z 0.2, 5.0 and 9.8. Print frame: front face on the bed; wrist axis at x 90; window x 72.90–96.10, with the notch to 97.51; far pilot slot x 69.35–71.45; moved pilot slot x 98.85–100.95.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 129 × 26 × 10 mm; `fits_bed: true` |
| 2 | One watertight solid, min Z 0 | PASS | `solids: 1`, `watertight: true`, `min_z_mm: −0.0` |
| 3 | Orientation matches the brief | PASS | Front face on the bed. top.png shows the horn pocket opening upward. bottom.png shows the bed face: clamp hole, MG90S window with its notch at the +x end, the two slotted pilots |
| 4 | Load paths | PASS | Bending runs along the layers (brief) |
| 5 | Bed contact | PASS | 2874.0 mm² |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | `overhang_pct` 0.0, `bridges: []`. The notch is a vertical cut through a flat plate: no ceiling. The pocket is an open top recess |
| 7 | Walls ≥ 1.8, none < 0.9 | **FAIL** | **Two structural walls are under 1.8 mm, at the same values on all three sections.** **Lead end** (notch end wall → moved pilot): **1.340 mm CAD**, x 97.51 → 98.85, ≈ 1.54 printed. **Far end** (window end → far pilot): **1.450 mm CAD**, x 71.45 → 72.90, ≈ 1.65 printed. These are vertical holes in a flat plate, so the widths are in-layer: room for 3 extrusion lines, not the rule's 4. The M2 × 12 thread (Ø2.0 into a Ø1.5 printed pilot) cuts 0.25 mm into each, leaving ≈ 1.3 / 1.4 mm intact. **They are structural:** spec §4 routes three loads through these two tab screws: the wrist stall (216 N·mm), the SYS-04 sideways moment (108–124 N·mm, every pose) and the yaw-stall case. Spec §8's proof test checks for cracks at these pilots. Other walls pass: moved pilot slot → plate end 3.05 (2.85 at the bed chamfer); rails (26 − 12.8) / 2 = 6.6; pocket → plate end 4.4. `thin_wall_warnings: []` (the tool only flags < 0.9) |
| 8 | HOLE_COMP; horizontal holes | PASS | `HOLE_COMP` goes into both cutters (model.py:36–38). **Window:** 23.2 × 12.8 CAD (x 72.90–96.10, y ±6.4), ≈ 23.0 × 12.6 printed for the 22.8 × 12.2 body (spec §3). **Notch:** 4.4 wide (y ±2.2), reaching 1.6 past the case end (95.9 → 97.51), ≈ 4.2 × 1.5 printed. **Pilots:** Ø1.7 CAD, ≈ 1.5 printed, each slotted 0.4 mm outward. **Clamp hole:** Ø3.6. No horizontal holes |
| 9 | Bottom edges chamfered | PASS (note) | `chamfer_plane_edges(arm, T, 0.4)` (model.py:35) on the bed face. The window, notch and pilot mouths rely on `elefant_foot_compensation` 0.2 (slice_plan.json) |
| 10 | Internal corners on load paths | PASS (advisory) | Window and notch corners are sharp, as accepted in rounds 1–2. The thin walls are #7's finding, not a corner issue |
| 11 | Fasteners per §4 | PASS (note) | **Wrist tabs:** M2 × 12 self-tappers go 9.5 mm into the 10 mm through-pilots, so they can't bottom out. The lead-end one goes through the slit filed to 2.1 mm (BUILD_GUIDE §4 step 6). **Elbow clamp:** M3 × 14 + Ø9 washer through the 8 mm floor, 4.6 mm into the metal spline. **Anti-rotation:** see note 3 |
| 12 | Spec §3 dims are named parameters | PASS (note) | `L` 90, `CLR` 0.4, `END_CLR` 0.2, `HOLE_COMP`, `WRIST = MG90S` (model.py:20–29). The notch comes from `MG90S.lead_notch_w` / `lead_notch_reach` (hobby_parts.py:550). The values match spec §3, including its ligament row (1.55 / 1.65 printed). But the pilot shift (1.3) is only the cutter's default (hobby_parts.py:126), not a named parameter here. Fix 1 names it |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG at ≈ 70 °C. Check the spool: `materials_on_hand` is empty |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

## The sub-1.8 mm MG90S ligaments: judged against the rules and the brief

**They do not pass.**

- **What the brief says.** design_brief.md line 33 rests the two walls on two claims. They are "above hobby_parts' 1.5 mm minimum for a self-tapper", and "M2 × 12 self-tappers [are] driven snug".
- **The 1.5 mm figure isn't a rule.** It is the cutter's refusal threshold, `min_ligament=1.5` (hobby_parts.py:125, 176), a tool default. fdm-design-rules §2 sets 1.8 mm (4 perimeters) for structural walls. Neither the skill nor library/ lowers that for screw pilots, and checklist #7 has no exception clause.
- **"Driven snug" doesn't change the wall.** It is an assembly instruction.
- **The walls are structural.** See #7: three spec §4 load cases, and the §8 proof test, run through them.
- **This job has already decided this.**
  - DFM round 1 failed a 1.55 mm wall at this pilot.
  - Round 2 closed it only at 1.80 printed.
  - The brief's own table (line 19) still lists "SG90 pilot-to-window wall | 1.8 printed | min | 4 perimeters".
  - The new walls are thinner than the one round 1 failed.
- **No calculation backs them.** strength.md still checks the SG90-era "pilot-to-window ligament 1.80 printed" (lines 61, 133).
- **Other reviews.** The hexapod coxa and femur reviews passed 1.34–1.45 mm CAD walls of the same MG90S geometry as "PASS (note)", on the same cutter default. I don't follow them, for the reasons above. Every MG90S closed window has these walls: forearm, claw bulkhead, hexapod. One decision should cover them all (fix 2).

## Required fixes

1. **Lead end: raise the notch-to-pilot wall from 1.340 to ≥ 1.60 mm CAD (≈ 1.80 printed).**
   - **Rule:** fdm-design-rules §2 (structural walls ≥ 1.8 mm, 4 perimeters); checklist #7.
   - **Evidence:** #7. Sections at z 0.2 / 5.0 / 9.8: notch end wall at x 97.51, moved pilot slot from x 98.85.
   - **Change:** in model.py, add `PILOT_SHIFT = 1.6` with its source (deep review 01 B1, option 1). Pass `pilot_shift=PILOT_SHIFT, min_ligament=1.8` to `servo_mount_cutter` (model.py:37–38), so the cutter enforces the rule. The wall becomes 1.64 CAD, ≈ 1.84 printed.
   - **Why 1.6 and not 1.55:** the cutter's check ignores the notch box's 0.01 mm extension (hobby_parts.py:181). At 1.3 it reports 1.35 CAD where the part measures 1.340, so 1.55 would give only 1.59 CAD.
   - **X1:** it can stay 104 (2.75 mm left past the slot), or go to 104.3 to keep the brief's 3.0.
   - **Check:** the screw then sits 0.6 mm inside the MG90S tab end (x 100.6), in the filed slit.
     - Try it on one servo first.
     - Put a Ø5 washer under the M2 head, which then bears on the slit's two prongs only.
     - Update spec §2/§3, the brief and BUILD_GUIDE §4 step 6 ("moved 1.6 mm out").
2. **Far end: raise the window-to-pilot wall from 1.450 to ≥ 1.60 mm CAD (≈ 1.80 printed).**
   - **Rule:** fdm-design-rules §2; checklist #7.
   - **Evidence:** #7. Far pilot slot ends at x 71.45, window end at x 72.90.
   - **Why the current layout can't get there:** the servo fixes the tab hole 2.5 mm past the case end (27.8 mm spacing on a 22.8 mm body). With the window's 0.1 mm printed end clearance and a Ø1.5 printed pilot, the wall can't exceed 1.65 printed.
   - **Change:** move the far pilot ≥ 0.2 mm outward (x 70.6 → ≤ 70.4), giving 1.65 CAD, ≈ 1.85 printed.
     - File that tab's slit to 2.1 mm as at the lead end, so the screw follows the pilot. Otherwise the tab hole holds the screw where it is, its thread cuts deeper on the window side, and the intact wall doesn't change.
     - `_pilot_xy` shifts only the +x pilot (hobby_parts.py:218–222). Either the toolsmith adds a far-end shift to `servo_mount_cutter`, or model.py cuts this pilot itself: Ø1.7 CAD, with its 0.4 mm outward slot.
     - Add the second slit to BUILD_GUIDE §4 step 6.
   - **The only alternative** for either wall is a user-accepted deviation from rule §2, because the rule lives in `.claude/skills/` and agents can't change it. It would need evidence in place of the cutter default:
     - a strength check of these exact walls;
     - a printed coupon of this window, notch and pilots (assembly_plan row 0, arm-fit-test) with the M2 × 12 screws driven home and loaded.

## Notes (not blocking)

1. **Strength** must re-check the wrist tab-screw rows against the post-fix walls. strength.md still describes the SG90 window.
2. **Brief.** design_brief.md's critical-dimension table holds only the SG90 rows (marked as the round-2 record). Add the MG90S rows with spec §3's tolerances: window 23.0 × 12.6 printed +0.3/−0, notch 4.2 × 1.5 +0.2/−0, and the ligaments.
3. **Anti-rotation screws** (01 S4, BUILD_GUIDE §4 step 3). The 2 × M2 × 6 are drilled into the pocket floor at assembly. They bite 1.0 mm of top skin, then 40 % gyroid. A solid-infill modifier under the pocket would give them solid plastic. That is the slicing-lead's call.
4. **60° fitting pose (SYS-03).** No CAD change: the double-arm pocket runs along the forearm's x axis, and BUILD_GUIDE §4 step 6 sets the pose at assembly. assembly_check.json (MG90S dummy) gives the elbow window [−150, 30] free of self-collision.

## Round 2 → round 4

| Change | Status | How I checked |
|---|---|---|
| 01 B1: lead notch + moved pilot (option 1) | Notch PASS; walls **FAIL** | The notch is a vertical cut, ≈ 4.2 × 1.5 printed, which passes a 3.6 × 1.2 ribbon (#6, #8). The moved pilot leaves 1.340 mm CAD (#7, fix 1) |
| 01 B2 / S1: MG90S body 22.8 × 12.2 | Window PASS; far wall **FAIL** | Window 23.2 × 12.8 CAD (#8). The 0.3 mm longer body cut round 2's 1.80 mm printed far wall to 1.65 (#7, fix 2) |
| 03 SYS-03: fitting pose | PASS | No geometry change (note 4) |
| Round 2's passing items | Still pass | The volume change is exactly the window growth plus the notch |

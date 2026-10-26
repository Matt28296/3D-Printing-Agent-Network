VERDICT: PASS

# DFM review (round 6): 20261025-arm-forearm

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26 · fourth design attempt, user-approved

**Why it reopened.**
- Links strength round 5 failed MG90S tab-screw pull-out: lead end 2.42, far end 2.62. The cause was that
  `servo_mount_cutter` slots every micro-servo pilot 0.4 mm outward (log.md 15:43).
- The user approved round pilots and a new spec §8 test (2): 17 N with the bar at 60° (log.md 15:44).
- Round 6 adds `wrist_cutter()` (model.py:79–90). It keeps the cutter's window and lead notch, masks out the two
  slotted pilots and cuts **round Ø1.7 CAD (Ø1.5 printed) pilots at the same centres**, x 70.6 and 99.7.
- `PILOT_SHIFT = 1.3` and `LEAD_PILOT_X = 99.7` are now named parameters (model.py:50–51), which closes round 5 note 2.

**Inputs**
- This job: spec.md, design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json, log.md, and the round-5
  design_review.md.
- Renders: all 5, regenerated with `tools/render.py` and viewed.
- Skills: fdm-design-rules, material-selection. library/lessons.md has no entries.

**Outputs are current.**
- `design()` in memory gives 32851.0 mm³. geometry.json has 32850.97 mm³, a 129 × 26 × 16 bbox and 1 solid.
- measure_holes gives Ø3.6 (the clamp) and **2 × Ø1.7 full-circle holes**. The slotted pilots were not reported as
  circles in round 5.
- `tools/mesh_check.py` re-run gives exactly the committed mesh_check.json.
- `cad_checks.py` re-run: 17/17 PASS. It checks:
  - both pilots round Ø1.7 at x 70.6 / 99.7, y 0;
  - solid 0.80 beyond each pilot's outer edge (no slot);
  - the far pilot open through 16 mm;
  - the cross-rib wall beyond the far pilot, 2.86;
  - the lead pilot to the plate end, 3.45;
  - the strips, 1.340 / 1.445.
- The volume is +17.7 mm³ on round 5 (32833.3): the two filled slots. Bed contact is +1.3 mm² (2875.3), the same slots
  on the bed face.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 129 × 26 × 16 mm; `fits_bed: true` |
| 2 | One watertight solid, min Z 0 | PASS | `solids: 1`, `watertight: true`, bbox min z 0.0 |
| 3 | Orientation matches the brief | PASS | Front face down, ribs on top (`Rot(180, 0, 0)`, model.py:103). top.png shows two round pilots on the centre line: one in the cross-rib, before the window, and one past the lead notch. There is no slot. iso / front / bottom are unchanged |
| 4 | Load paths | PASS | Tab-screw pull-out shears the pilot wall across many layers, as before. It now has the whole thread circle in plastic, against 0.77 of it in round 5 |
| 5 | Bed contact | PASS | 2875.3 mm² |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | `overhang_pct` 0.0, `bridges: []`. The pilots are vertical holes in print |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (accepted deviation) | **Walls the change touches grew.** Cross-rib wall beyond the far pilot 2.86 (round 5: 2.45). Lead pilot to the plate end 3.45 (was 3.05). **MG90S screw strips, unchanged:** 1.340 (lead end) and 1.445 (far end) CAD. They are under §2's 1.8, as the user accepted on 26 Oct 2026, with the first-print screw-strip check in spec §8, which now names the M2 × 12 and the M2 × 16 (closes round 5 note 1). Strength rows: tear-out 4.65 / 5.08, splitting ≥ 6.18. `thin_wall_warnings: []` |
| 8 | HOLE_COMP; horizontal holes | PASS | `PILOT_D = WRIST.screw_pilot_d + HOLE_COMP` = 1.7 (model.py:52). The window and notch still come from the cutter with `hole_comp=HOLE_COMP`. The mask (model.py:85–87) is 0.2 larger than each slotted pilot and stays clear of the window (x 72.9) and the notch (x 97.51): it leaves no sliver, which cad_checks' window and notch probes confirm. No horizontal holes |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(arm, T, 0.4)` (model.py:95) |
| 10 | Internal corners on load paths | PASS | Unchanged: the 45° run-out of the cross-rib and ribs, and the square end at x 101.1 past the last tab row |
| 11 | Fasteners per §4 | PASS (note 1) | Far tab: M2 × 16, 13.5 mm into the 16 mm round pilot. Lead-end tab: M2 × 12, 9.5 mm into the 10 mm plate, through the slit filed to 2.1. Elbow clamp: M3 × 14 + Ø9 washer. Self-tappers in a joint assembled a few times are acceptable |
| 12 | Spec §3 dims are named parameters | PASS | `PILOT_D` 1.7, `PILOT_SHIFT` 1.3, `LEAD_PILOT_X` 99.7, `FAR_PILOT_X` 70.6, each with its source comment (model.py:49–52). The brief's pilot row says "round Ø1.5 printed (Ø1.7 CAD), no outward slot" |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG at about 70 °C |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

**Clearances:** nothing outside the two pilots moved, so round 5's sweep still holds. The ribs are ≥ 10.17 mm from the
upper link and ≥ 26.7 mm from the elbow MG996R and its horn. `assembly_check.json` (round 6) has no collisions.

## Required fixes

None.

## Notes (not blocking)

1. **The far tab now has no spacing play.** The 0.4 mm slot was there to take the MG90S's tab-hole spacing error.
   - At the lead end the screw still passes through the filed 2.1 mm slit, so that end keeps its play.
   - At the far end the screw goes through the tab hole into a round pilot. If the real far hole sits nearer the
     window than the CAD's, the screw cuts towards the 1.45 strip. A 0.3 mm error leaves about 1.0 mm behind the thread.
   - The BUILD_GUIDE §2 measurement covers this: a hole spacing off by more than 0.3 mm goes back to Claude. The
     first-print screw-strip check (spec §8) catches the rest.
   - Measure the spacing before printing, not after.
2. **Elbow horn anti-rotation** (open since round 4): a solid-infill modifier under the pocket is the slicing-lead's call.
3. **Re-slice.** The slice files in this folder are older than round 5.

## Round 5 → round 6

| Item | Status | How I checked |
|---|---|---|
| Strength round 5: pull-out 2.42 / 2.62 (slotted pilots) | Pilots round, Ø1.7 CAD, same centres | measure_holes 2 × Ø1.7 at full arc; cad_checks; top.png |
| Spec §8 (2) → 17 N at 60° | In spec.md | strength.md checks it |
| Round 5 notes 1 (§8 screws) and 2 (`PILOT_SHIFT`) | Closed | spec §8; model.py:50 |
| Round 5's passing items | Still pass | The volume change is the two slots alone |

VERDICT: PASS

# DFM review (round 6): 20261025-arm-upper-link

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26 · fourth design attempt, user-approved

**Why it reopened.** Links strength round 5 failed the ribs' run-out: SF 1.89 under the yaw stall, 1.07 at spec §8's
bench test (log.md 15:43). The user approved the analyst's fix (log.md 15:44), and the cad-engineer made it (16:34,
merged fa56765):
- `RIB_TAPER` goes 6 → 12 (model.py:42). Nothing else moves.
- The ribs still reach full depth at x 64.2. Their run-out now slopes at 27° and meets the back face at x 52.2 (was 58.2, 45°).

**Inputs**
- This job: spec.md, design_brief.md (round 6 section), model.py, cad_checks.py, geometry.json, mesh_check.json, log.md,
  and the round-5 design_review.md.
- Renders: all 5, regenerated with `tools/render.py` and viewed.
- Clearance: an independent sweep of mine. The rib solid goes in the shoulder frame of `assembly_check.chain()`, and
  `distance_to` is measured to the turntable and to `servo_dummy(MG996R, with_horn=True)`, shoulder 0–180° in 5° steps.
- Skills: fdm-design-rules, material-selection. library/lessons.md has no entries.

**Outputs are current.**
- `design()` in memory gives 44312.4 mm³. geometry.json has 44312.35 mm³, a 146 × 34 × 16 bbox and 1 solid.
- `tools/mesh_check.py` re-run gives exactly the committed mesh_check.json.
- `cad_checks.py` re-run: 14/14 PASS. The new probe gives rib depth 3 at x 58.2, 1 at x 54.2 and 0 at x 52.2.
- The volume is +246 mm³ on round 5 (44066.2), which is the run-out's extra wedge (2 × 6.85 × ½ × 6 × 6 = 247). Nothing
  else moved.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 146 × 34 × 16 mm; `fits_bed: true` |
| 2 | One watertight solid, min Z 0 | PASS | `solids: 1`, `watertight: true`, bbox min z 0.0 |
| 3 | Orientation matches the brief | PASS | The front face prints down and the ribs print on top (`Rot(180, 0, 0)`, model.py:71). **front.png** shows the longer, shallower ramp rising from about x 52 to full height at 64, then flat to the square end at 117. **iso.png** shows both rails' ramps. bottom.png (the bed face) is unchanged |
| 4 | Load paths | PASS | The ramp feeds the ribs' force into the plate over 12 mm instead of 6. The ribs' bending fibres still run along x, in the layers. The across-layer shear at the run-out is strength's rib-root row (3.74, strength.md) |
| 5 | Bed contact | PASS | 3881.1 mm², unchanged. The ribs are at print z 10–16 |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | `overhang_pct` 0.0, `bridges: []`. The run-out is a 27° ramp facing up, so each 0.2 mm layer steps 0.39 mm along x onto the layer below. The rib sides are vertical, flush with the window wall and the plate edge |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | **Rib width:** 6.85, the same over the run-out (it is the same prism, cut by the ramp). The first 2 mm of ramp is under 1 mm tall, about 1–4 layers on a 6.85 mm-wide strip, so it is not a thin wall. **Unchanged:** notch → pilot strip 1.835 CAD; window rails 6.85. `thin_wall_warnings: []` |
| 8 | HOLE_COMP; horizontal holes | PASS | Unchanged: `HOLE_COMP` in both cutters (model.py:63–66). measure_holes gives Ø3.6 clamp and 4 × Ø2.8 pilots. No horizontal holes |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(link, T, 0.4)` on the bed face (model.py:61) |
| 10 | Internal corners on load paths | PASS | The rib meets the back face at x 52.2 at a 153° corner (was 135°), with no step. Strength keeps Kt 2.0 there. The plate at the foot gives 4.36 |
| 11 | Fasteners per §4 | PASS | Unchanged: M3 × 12 + Ø7 washer tab screws with 9 mm engaged; the shoulder clamp is an M3 × 14 + Ø9 washer |
| 12 | Spec §3 dims are named parameters | PASS | `RIB_TAPER = 12.0` (model.py:42), with its source: links strength round 5, 6 → 12. The brief's "Rail ribs" row says "27° run-out (`RIB_TAPER` 12) to x 52.2". Spec §2 asks for ≥ 10 mm rib clearance; see below |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG at about 70 °C. `materials_on_hand` is empty, so check the spool |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

**The ribs against the parts round them** (my sweep, shoulder 0–180°, the whole rib solid including the run-out):
- **Turntable:** ≥ **11.33 mm**, closest at shoulder 130° (round 5: 11.89). It is the run-out that comes nearest.
- **Shoulder MG996R with its double-arm horn:** ≥ **19.04 mm**, at 155° (round 5: 23.9).
- Both clear spec §2's 10 mm. `assembly_check.json` (round 6) has no collisions in any pose or sweep.
- The elbow end is unchanged.

## Required fixes

None.

## Notes (not blocking)

1. **Shoulder horn anti-rotation** (open since round 4). The 2 × M2 × 6 bite 1.0 mm of pocket-floor skin, then infill. A
   solid-infill modifier under the pocket is the slicing-lead's call.
2. **Notch corners** (optional, open since round 4): an r 0.5 on each notch's far corners.
3. **Re-slice.** The slice files in this folder are older than round 5. Re-slice once the DESIGN gate passes.

## Round 5 → round 6

| Item | Status | How I checked |
|---|---|---|
| Strength round 5: rib run-out SF 1.89 | `RIB_TAPER` 12 as asked | cad_checks probes; front.png; strength.md re-runs it at 3.74 |
| Printability of the longer ramp | PASS | #6, #7 |
| Clearance of the ribs, now from x 52.2 | ≥ 11.33 / ≥ 19.04 mm | My sweep (above) |
| Round 5's passing items | Still pass | The volume change is the ramp alone |

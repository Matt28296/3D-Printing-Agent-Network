VERDICT: PASS

# DFM review (round 5): 20261025-arm-turntable-ring

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26

**Why it reopened.**
- **Round 4 DFM failed** on the brief: it still described the 15.0 mm ring with a 1.5 mm gap.
- **Links strength round 4 failed** the bare M3 × 6 pan head creeping into the 3 mm tab: SF 2.26 against 4 (log.md 11:38, 13:06).
- **Design round 5** (design_brief.md "Round 5"):
  - adds a Ø7 × 0.5 washer under each tab screw head;
  - cuts a Ø8 relief through the wall round each screw, from the tab's top up (model.py:31, 48–49);
  - corrects the brief.

**Inputs**
- This job: spec.md, design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json, slice_plan.json, log.md and the round-4 review.
- Renders: all 5, regenerated with `tools/render.py` and viewed.
- Related: the base's ring pilots (base model.py:96–99) and BUILD_GUIDE §1 and §4 step 1.
- Skills: fdm-design-rules, material-selection, build123d-cad. library/lessons.md has no entries.

**Outputs are current.**
- `build()` run in memory gives 13284.15 mm³, a 91.27 × 96 × 16.1 bbox from (−45.64, −52, 0) and 1 solid. That matches geometry.json.
- part.stl is watertight.
- `tools/mesh_check.py` re-run gives the committed mesh_check.json.
- The volume is −49.4 mm³ on round 4 (13333.52). That is three lens-shaped cuts, each ≈ 1.3 mm² × 13.1 mm tall: the Ø8 relief takes only the wall's outer 0.5 mm. Nothing else moved.
- `cad_checks.py` re-run: 6/6 PASS.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 91.3 × 96.0 × 16.1 mm; `fits_bed: true` |
| 2 | One watertight solid, min Z 0 | PASS | `solids: 1`, `watertight: true`, bbox min z 0.0 |
| 3 | Orientation matches the brief | PASS | Flat, with the ring and tabs on the bed. iso.png, front.png and right.png show each relief as a vertical groove in the wall's outer face, rising from the tab's top face (z 3) to the top |
| 4 | Load paths | PASS | The turntable presses the top face down, so the wall is in compression across the layers, as in round 4. Over each relief's 3.7 mm length the wall is 2.5 mm instead of 3.0. The brief carries the analyst's worst ring row with that: ≥ 7.7 |
| 5 | Bed contact | PASS | **The ring's and tabs' bottom face prints down.** 718.7 mm², unchanged: the relief starts at the tab's top (z 3) and never reaches the bed |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | `bridges: []`. Each relief is a vertical cylinder cut with solid below it: its floor at z 3 faces up, and its walls are vertical. I listed every facet behind mesh_check's 34.9 mm² (0.33 %): all of them sit at z 0.03–0.33, in the 0.4 mm bottom chamfer, at 44.1–45.0°. Round 4 had 23.3 mm² of the same facets; the extra is re-tessellation. None is at the reliefs |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | **Wall at each relief: 2.50** (r 41–43.5, cad_checks at 30°, 150° and 270°). That is 5 lines and above the 1.8 rule. Elsewhere the wall is 3.0. Tab ligament round the Ø3.6 hole: 2.7 (Ø9 tab), unchanged, because the relief stops at the tab's top. `thin_wall_warnings: []` |
| 8 | HOLE_COMP; horizontal holes | PASS | `HOLE_COMP` on the tab holes (model.py:46): Ø3.6 CAD, ≈ 3.4 printed. The relief is a clearance with 0.5 mm all round the Ø7 washer (`WASHER_CLR`), not a fit, so it gets no compensation. No horizontal holes |
| 9 | Bottom edges chamfered | PASS | `chamfer_bottom(design(), 0.4)` (model.py:54) |
| 10 | Internal corners on load paths | PASS (advisory) | The relief's floor-to-wall edge is a 90° internal corner at z 3, on a wall in compression. The web and tab corners are as accepted in round 4 |
| 11 | Fasteners per §4 | PASS (note) | §4 asks for washers or wide heads against creep, and this round adds them. cad_checks shows each Ø7 washer sits flat on the tab and clears the wall by ≥ 0.5 mm. **Engagement:** 6 − 0.5 (washer) − 3 (tab) = 2.5 mm into the base's 4 mm through-pilot. That is short, but the parts are assembled once and BUILD_GUIDE §4 step 1 says "snug, no harder". The ring loads press it onto the plate, not off it (note 1) |
| 12 | Spec §3 dims are named parameters | PASS | `H = TURNTABLE_Z − RUN_GAP` = 16.1, `TAB_HOLE` 3.4, `WASHER_D` 7.0, `WASHER_CLR` 0.5 (model.py:22–32), all sourced. **Round 4 fix 1 is closed:** the brief's table now reads "Ring height \| 16.1 \| ±0.15 \| 0.4 mm running gap … (≈ 0.3 with … PTFE tape)", and its Risks line gives the 0.4 mm gap, measuring the horn face and sanding to fit. The new washer-relief row (Ø8, wall 2.5) matches the model |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG at ≈ 70 °C. `materials_on_hand` is empty: check the spool |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

## Required fixes

None.

## Notes (not blocking)

1. **Spec §2 is stale** (Architect). It still reads "3 mm tab + 3 mm into the 4 mm plate". With the washer it is 2.5 mm, as the brief, BUILD_GUIDE §1 and the base spec say. Change "3 mm into" to "2.5 mm into".
2. **H 16.1** is still half a layer (round 4 note 1): at 0.2 mm layers PrusaSlicer ends the ring at 16.0 or 16.2. Both are inside ±0.15, and assembly sands or tapes to the gap.
3. **Top edges** (round 4 note 2, optional): a 0.3 mm chamfer on the two top edges would keep them from cutting the PTFE tape.

## Round 4 → round 5

| Item | Status | How I checked |
|---|---|---|
| DFM round 4 fix 1: the brief gave the round-2 ring | Closed | #12: brief table and Risks line |
| Strength round 4: pan head creep in the tab | Washer + Ø8 relief, printable | #6, #7, #11: vertical cut, wall 2.50, washer seat flat |
| Round 4 notes 1–3 (half-layer height, top chamfer, horn-face measurement) | Notes 1–2 carried here as notes 2–3; the measurement is still asked for in spec §3 | — |
| Round 4's passing items | Still pass | The volume change is the three reliefs |

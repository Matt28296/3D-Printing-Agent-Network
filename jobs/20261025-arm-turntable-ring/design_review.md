VERDICT: FAIL

# DFM review (round 3, reopened): 20261025-arm-turntable-ring

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26

**Why it reopened.** Deep review 03 SYS-05 (status.json; log.md 10:25). The job was at AWAITING_APPROVAL with the round-2 PASS. Then:
- the running gap went from 1.5 to 0.4 mm (`RUN_GAP`), so `H` went from 15.0 to 16.1;
- one layer of PTFE tape now goes on the top face;
- the ring now shares the arm's overturning moment in normal use, as a bearing.

**Inputs**
- This job: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, print_requirements.json, slice_plan.json, status.json, log.md and the round-2 review.
- Renders: all 5, regenerated with `tools/render.py` and viewed.
- Related parts: the base and turntable model.py, and `horn_face_z` in tools/hobby_parts.py.
- Assembly: assembly_plan.md, and BUILD_GUIDE §1 (PTFE tape) and §4 steps 1 and 4.
- Deep review 03 (SYS-05). library/lessons.md: no entries.

**Outputs are current.**
- `build()` gives 13333.52 mm³ and a 91.272 × 96 × 16.1 bbox from (−45.636, −52, 0), the same as geometry.json.
- part.stl is watertight.
- `tools/mesh_check.py`, re-run in memory, gives exactly the committed mesh_check.json.
- The volume grew by 881.2 mm³ from round 2 (12452.3). That is exactly the taller wall: π(44² − 41²) × 1.1. Nothing else changed.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 91.3 × 96.0 × 16.1 mm; `fits_bed: true` |
| 2 | One watertight solid, min Z 0 | PASS | `solids: 1`, `watertight: true`, `min_z_mm: 0.0` |
| 3 | Orientation matches the brief | PASS | Flat, tabs on the bed (iso.png, front.png, right.png) |
| 4 | Load paths | PASS | The new bearing load (≈ 19 N at r 44, ×2 dynamic; the 52 N yaw-stall catch, spec §4) presses the top face down. That puts the wall in compression across the layers, and the base plate carries it directly under the ring's bed face. Tilting the disk the other way lifts it off the ring, so the layers are never in tension. Friction (μ ≈ 0.1 on PTFE) is a small shear into the tab screws |
| 5 | Bed contact | PASS | 718.7 mm² of PETG (unchanged) |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | `bridges: []`. The 23.3 mm² (0.22 %) of overhang is all the 0.4 mm bottom chamfer's tessellated facets at z 0–0.4, 44.1° from straight down. The taller wall is vertical |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | Sections: ring wall 3.0 at z 1.5, 8.0 and 16.0 (r 41–44); tab ligament 2.7 (Ø9 around Ø3.6) at z 1.5; tabs 3.0 thick. `thin_wall_warnings: []` |
| 8 | HOLE_COMP; horizontal holes | PASS | `HOLE_COMP` (model.py:16) on the tab holes: Ø3.6 CAD (geometry.json), ≈ 3.4 printed (spec §3). No horizontal holes |
| 9 | Bottom edges chamfered | PASS | `chamfer_bottom(design(), 0.4)` (model.py:44); the chamfer shows in bottom.png. slice_plan.json's `elefant_foot_compensation` 0.2 is paired with it |
| 10 | Internal corners on load paths | PASS (advisory) | The web-to-ring and tab corners are sharp, as in round 2. They are loaded in compression and light shear only |
| 11 | Fasteners per §4 | PASS | 3 × M3 × 6 self-tapping through the 3 mm tabs: 3 mm into the base's 4 mm plate (spec §2). The new downward load goes ring → base plate, not through the screws |
| 12 | Critical dims: spec §3 = model.py = brief | **FAIL** | model.py matches spec §3: `RUN_GAP = 0.4` (model.py:19–21, sourced to 03 SYS-05) and `H = TURNTABLE_Z − RUN_GAP` = 16.5 − 0.4 = 16.1 (model.py:22; bbox top 16.1). **design_brief.md contradicts both.** Its critical-dimension table (line 17) still reads "Ring height \| 15.0 \| ±0.2 \| 1.5 mm running gap to turntable". Its Risks line (26) still reads "→ 1.5 mm gap, sand to fit". Spec §3 (line 16) says 16.1 ±0.15 with a 0.4 mm gap. This is the one dimension this round changed. Rule §3 requires the brief to carry it with its tolerance |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG at ≈ 70 °C; PTFE sliding at these loads adds no meaningful heat. `materials_on_hand` is empty: check the spool |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

## Required fixes

1. **Update design_brief.md to the round-3 ring.** This is a documentation change only; no CAD change.
   - **Rule:** fdm-design-rules §3: every critical dimension in the spec appears in design_brief.md with its tolerance. Checklist #12.
   - **Evidence:** brief line 17 says 15.0 ±0.2 with a 1.5 mm gap. Spec §3 line 16 and model.py lines 19–22 say 16.1 ±0.15 with a 0.4 mm gap.
   - **Change the table row** to: "Ring height | 16.1 | ±0.15 | 0.4 mm running gap to the turntable (≈ 0.3 with one layer of PTFE tape); sand the top to an even gap | source: deep review 03 SYS-05".
   - **Change the Risks line** to say three things:
     - 0.4 mm gap with PTFE tape;
     - the gap depends on the disc horn's face height, so measure it first (spec §3);
     - sand where it rubs, add tape where it's loose (BUILD_GUIDE §4 step 4).

## Notes (not blocking)

1. **H 16.1 is half a layer.** slice_plan.json prints 0.2 mm layers, so PrusaSlicer ends the ring at 16.0 or 16.2. That is a 0.1 mm step either way, inside spec §3's ±0.15. BUILD_GUIDE §4 step 4 sands or tapes to the gap anyway, so no change is needed. For a predictable height, either use H 16.0 (0.5 mm bare, ≈ 0.4 taped) or keep 16.1 and expect up to 0.1 mm of sanding.
2. **Top edges.** BUILD_GUIDE §1 lists plumber's PTFE tape, which isn't adhesive, so it will be wrapped over the 3 mm top face. A 0.3 mm chamfer on the two top edges would keep them from cutting the tape. Optional; the rule asks only for bottom chamfers.
3. **The gap's real value** rests on `horn_face_z(MG996R)` = 16.5. That is the spline top (15.9, which TowerPro confirms) plus 0.6 mm assumed for the disc horn, unverified per 01 S2. Spec §3 already asks for the measurement before printing. Keep that step.
4. **Strength.** strength.md (06:55) predates this change (10:25); the ring now carries load in normal use. The re-check is due, as status.json says.

## Round 2 → round 3

| Change | Status | How I checked |
|---|---|---|
| Running gap 1.5 → 0.4, H 15.0 → 16.1 (03 SYS-05) | Printable | Still a plain vertical wall: no overhang beyond the bottom chamfer, walls 3.0 / 2.7 (#6, #7). Height within tolerance (note 1) |
| PTFE tape on the top face | OK | BOM line in BUILD_GUIDE §1. Step 1 fits it, step 4 sets the gap by sanding or taping, and spec §8 checks it with a feeler gauge at 8 points |
| Documentation | **Open** | design_brief.md still describes the round-2 ring (fix 1) |

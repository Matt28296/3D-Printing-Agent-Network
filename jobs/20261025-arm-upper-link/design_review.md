VERDICT: PASS

# DFM review (round 5): 20261025-arm-upper-link

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26 · third design attempt

**Why it reopened.** Links strength round 4 failed the two 6.85 × 10 elbow-window rails in out-of-plane bending: yaw stall 1.49 (log.md 13:06). Design round 5 adds a 6 mm rib on the back face along each rail (`rail_ribs()`, model.py:36–53, 59) and cuts the window, notches and pilots 16 deep (:61).

**Inputs**
- This job: spec.md, design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json, slice_plan.json, log.md and the round-4 review.
- Renders: all 5, regenerated with `tools/render.py` and viewed.
- Clearance: an independent mesh sweep of mine (method below), using the turntable model and `hobby_parts.servo_dummy` / `link_back_z`.
- Skills: fdm-design-rules, material-selection, build123d-cad. library/lessons.md has no entries.

**Outputs are current.**
- `build()` run in memory gives 44066.16 mm³, a 146 × 34 × 16 bbox from (−25, −17, 0) and 1 solid. That matches geometry.json.
- part.stl is watertight.
- `tools/mesh_check.py` re-run gives the committed mesh_check.json.
- The volume is +4569.7 mm³ on round 4 (39496.47). That is the two ribs: 2 × 6.85 × 6 × 52.8 plus the 45° run-outs, minus the r 8 corner at the elbow end. Nothing else moved.
- `cad_checks.py` re-run: 14/14 PASS.

**Method**
- **Print frame:** front face on the bed, so the plate is at z 0–10 and the ribs at z 10–16. Point-in-solid line scans of part.stl at 0.005 mm steps.
- **Clearance sweep:**
  - The rib solid goes in the shoulder frame (`frame((XS, UP_Y + link_back_z, ZS))`, as in assembly_check.py), swept over shoulder 0–180° in 5° steps.
  - The other bodies are the turntable, the shoulder MG996R with its double-arm horn, and the four upright tab-screw heads (M3 pan head Ø5.5 × 2.4 on a Ø7 × 0.5 washer, on top of the 2.5 mm tab).
  - Distance is mesh-to-mesh closest points, sampled both ways.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 146 × 34 × 16 mm; `fits_bed: true` |
| 2 | One watertight solid, min Z 0 | PASS | `solids: 1`, `watertight: true`, bbox min z 0.0 |
| 3 | Orientation matches the brief | PASS | **The front face prints down; the ribs, on the back face, print on top** (`Rot(180, 0, 0)`, model.py:68). iso.png and front.png show the ribs rising 6 mm off the top face, with a 45° run-out towards the shoulder and a square end at x 117. bottom.png (bed face) is unchanged |
| 4 | Load paths | PASS | The ribs deepen the rails to 16 mm for out-of-plane bending. Their fibres run along x in the layers, so the bending stays along the layers |
| 5 | Bed contact | PASS | 3881.1 mm², the same as round 4. The ribs are at print z 10–16 |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | `overhang_pct` 0.0, `bridges: []`. Each rib stands on the plate. Its run-out rises at exactly 45° from x 58.2 to 64.2 and faces up. Its sides are vertical and flush with the window wall and the plate edge, and its top is flat at z 16 |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | **Rib width** at z 13: 6.84 at x 90 (y 10.155–16.995) and 6.26 at x 116 (in the r 8 corner); cad_checks gives 5.8 at the x 117 end. **Pilots:** the four sit at y ±5, between the ribs (rib inner face y ±10.15). The x scan at y 13, z 13 is solid 61.2–117 with no hole, so the ribs touch no hole. Notch → pilot strip 1.835 CAD (round 4: 1.839). Window rails 6.85. `thin_wall_warnings: []` |
| 8 | HOLE_COMP; horizontal holes | PASS | `HOLE_COMP` goes into `horn_pocket_cutter` and `servo_mount_cutter` (model.py:60–63). Window 41.3 × 20.3 CAD, now through 16 mm, so its side walls continue up the ribs' inner faces. Notches 4.6 × 2.1; pilots Ø2.8. No horizontal holes |
| 9 | Bottom edges chamfered | PASS (note) | `chamfer_plane_edges(link, T, 0.4)` (model.py:58) on the bed face. The hole mouths rely on `elefant_foot_compensation` 0.2 |
| 10 | Internal corners on load paths | PASS (advisory) | Towards the shoulder the rib meets the plate through a 45° run-out, with no step (cad_checks: depth 3 at x 61.2, 0 at x 58.2). At x 117 it ends in a square 6 mm step. That is 2.9 mm past the near pilot row, where the rail moment has fallen to the cantilever end. The notch corners are as in round 4 |
| 11 | Fasteners per §4 | PASS | **Elbow tab screws:** M3 × 12 + Ø7 washer, 9 mm into the 10 mm plate. The pilots are through-holes (16 mm cut), so the screws can't bottom out. **Shoulder clamp:** M3 × 14 + Ø9 washer through the 8 mm floor, unchanged. **Horn anti-rotation:** note 1 |
| 12 | Spec §3 dims are named parameters | PASS | `RIB_H` 6, `RIB_PAST` 5, `RIB_X0` 64.2, `RIB_TAPER` 6, `RIB_X1` 117 (model.py:37–42), sourced to strength round 4. They match the brief's new "Rail ribs" row. `L` 100, `T` 10, `CLR` and `HOLE_COMP` are unchanged. The brief now carries the notch row with +0.2/−0, which closes round 4 note 3 |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG at ≈ 70 °C. `materials_on_hand` is empty: check the spool |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

**The ribs against the parts around them** (my sweep, shoulder 0–180°):
- **Turntable:** ≥ **11.89 mm**, closest at shoulder 130°. The brief says ≥ 11.9.
- **Shoulder MG996R with its horn:** ≥ 23.9 mm.
- **Upright tab-screw heads:** ≥ 23.5 mm.
- **Elbow servo:** its case already stands 17 mm out of the back face, between the ribs. The ribs continue the window's side walls, so the case slides along a 16 mm-deep window.
- **Elbow servo lead:** it leaves the case end 11 mm below the back face, on the centre line. That is below the ribs (6 mm) and between them.
- **Elbow horn and forearm:** on the link's front side. The forearm's ribs come no nearer than 10.17 mm to this link (forearm review).

## Required fixes

None.

## Notes (not blocking)

1. **Shoulder horn anti-rotation** (round 4 note 2, still open). The 2 × M2 × 6 are drilled into the pocket floor at assembly. They bite the floor's 1.0 mm of top skin, then 40 % gyroid. A local solid-infill modifier under the pocket would give them solid plastic, as the turntable's 30 bottom layers do for the disc horn. That is the slicing-lead's call.
2. **Notch corners** (round 4 note 1, optional): an r 0.5 on each notch's far corners.

## Round 4 → round 5

| Item | Status | How I checked |
|---|---|---|
| Strength round 4: window rails (1.49) | Ribs added, printable | #3, #6, #7: on the top face, 45° run-out, ≥ 5.8 wide; clearance ≥ 11.89 |
| Round 4 note 3: notch tolerance in the brief | Closed | Brief table row |
| Round 4 notes 1–2 | Open, optional / slicing | Notes 1–2 |
| Round 4's passing items | Still pass | The volume change is the ribs |

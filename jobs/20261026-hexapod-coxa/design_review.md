VERDICT: FAIL

# DFM review (round 3): 20261026-hexapod-coxa

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26

**Inputs**
- This job: spec.md, design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json, print_requirements.json, slice_plan.json, strength.md (round 1), the round-2 review.
- Renders: all 5, regenerated with `tools/render.py` and viewed. front.png was also enlarged at the window.
- Assembly job: assembly_plan.md, hex_frame.py, spec.md, BUILD_GUIDE.md, assembly_check.json.
- Deep review: 01-bought-parts.md (B1, B2, S1) and 05-hexapod-system.md. Also tools/hobby_parts.py.
- library/lessons.md: no entries.

**Probes:** trimesh `contains` on part.stl. Frame C, z up in print; the vertical plate's mid-plane is y −18.5.

**Outputs are current.**
- `build()` gives 23322.91 mm³ and a 60.1 × 30.5 × 41.0 bbox from (−9, −23.5, 0), the same as geometry.json.
- part.stl is one watertight body.
- `tools/mesh_check.py`, re-run in memory, gives exactly the committed mesh_check.json.
- cad_checks.py: 16/16 PASS, exit 0.

**One item fails: #6, the flat top of the new lead notch.** Everything else passes, including all three round-2 fixes. The fix is a cutter change only and touches no section strength relies on.

Layout in frame C, from the parameters and probes:
- femur axis at (32, ·, 20);
- window x 14.9–38.1, floor z 13.6, full width up to z 26.4, roof apex z 38.0;
- plate x 1.9–51.1, y −23.5…−13.5, top z 41;
- lead notch x 38.1–39.51, z 17.8–22.2;
- moved outboard pilot at x 41.7.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits the bed with a 5 mm margin | PASS | 60.1 × 30.5 × 41.0 mm, `fits_bed: true`. Two per plate need about 60 × 66 mm, six (3 × 2) about 190 × 71 mm. Both fit inside 240 × 200 |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, `watertight: true`, `min_z_mm: 0.0`. part.stl splits into 1 body |
| 3 | Orientation matches the brief | PASS | The horizontal plate is on the bed, with the horn pocket on the bed face (bottom.png). The vertical plate stands, and the window roof, pilot teardrop points, tie-slot roof and corner cut point up (front.png, iso.png) |
| 4 | Load paths | PASS (justified) | Hub bending runs along the layers. The plate's out-of-plane bending crosses the layers at the posts and the floor band. The brief accepts this because the horn pocket must sit on the bed, and the model has strength round 1's section for it: T_V 10, posts 13 (cad_checks), R1 reliefs and a full gusset. Strength round 1 checked that set (lowest SF 3.19) |
| 5 | Bed contact | PASS | 1205.1 mm² of PETG, which warps little |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | **FAIL** | `overhang_pct` 1.77. **The lead notch's top is a one-sided ledge.** Its ceiling is flat at z 22.2 over x 38.10–39.51, through the whole plate (flat overhang face, 14.1 mm²). The window is open beside it, on the x 38.1 side, up to z 26.4. Probes: (38.5, −18.5, 22.1) void, (38.5, −18.5, 22.3) solid, (37.9, −18.5, 22.3) void. The z 22.1 row is solid from x 39.51, the z 22.3 row from 38.10. So the ceiling is anchored on one 10 mm edge only: a 1.41 mm cantilever printed over air. mesh_check lists it as a "bridge" (z 22.2, span 1.41, length 10.0) because the tool doesn't check anchoring. It is neither ≤ 45° nor supported. Everything else here passes (see the note below the table) |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (note) | T_V 10, posts 13, 6.0 mm floor under the horn (cad_checks). 3.0 above the roof apex (x 26.5: solid z 38.0–41.0). 2.7 from the tie slot to the plate end, 8.15 from the moved pilot to the plate end (z 20 row: void 40.85–42.95, solid to 51.1). `thin_wall_warnings: []`. The two pilot ligaments are under 1.8: inboard pilot to window 1.45 CAD (z 20 row: solid 13.45–14.9), notch to the moved pilot 1.34 CAD (solid 39.51–40.85), ≈ 1.65 / 1.55 printed. Both are solid, above 0.9, and above hobby_parts' 1.5 mm printed minimum for a self-tapper. The MG90S fixes them: its tab hole is 2.5 mm from the case end. Strength must re-check them (round 1 used 1.60) |
| 8 | HOLE_COMP; horizontal holes teardrop or flat-top | PASS | `HOLE_COMP = HOLE_COMP_DEFAULT` (0.2) goes into both cutters: window 23.2 × 12.8 CAD; notch 4.2 + 0.2 wide, reaching 1.5 + 0.1 past the case end; pilots Ø1.7; clamp Ø2.6 (geometry.json). Pilots are teardrops pointing up (`pilot_teardrop="-y"` = C +z; enlarged front.png). The reliefs are teardrops whose points lie inside the window. The tie slot has a 45° roof (x 47.5: void to the apex at z 32.5), the window a 45° roof. The notch's flat top is #6 |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(br, 0.0, 0.4)` (model.py:89) runs on the hub and arm after the r2.5 fillet and before the cuts. The plate, ramp and gusset start at z 7.99, so the hub and arm are the whole bed outline (bottom.png). The horn-pocket rim relies on `elefant_foot_compensation` 0.2 (slice_plan.json), as in round 2 |
| 10 | Internal corners on load paths filleted | PASS | **Window floor:** R1 T-bone reliefs, Ø2, tangent to the post faces at (15.9, 13.6) and (37.1, 13.6). z 13.5 row: void 14.91–16.89 and 36.11–38.09, down to z 12.6. **Gusset:** 45° × 4.9 along the whole plate, x 1.9–51.1 (YZ probes at x 1.95, 10.5, 26.5, 42.5, 51.0: solid to y −8.91 at z 8.3 and to −13.41 at z 12.8). **Hub step:** 45° ramp from x −6.1 at z 8, on the hub's straight edge (the r2 corner ends at x −7), to x 1.9 at z 16. **Hub to arm:** r2.5 (top.png). See the notes below the table |
| 11 | Fasteners per §4 | PASS | **Femur servo:** 2 × M2 × 10 self-tapping, 7.5 mm into the 10 mm plate through Ø1.7 CAD pilots. The outboard one goes through the slit filed to 2.1 mm (spec §2, BUILD_GUIDE step 4). **Horn:** M2 × 12 (× 14 for a thread 7.5 mm deep or more) with a Ø10 × 1 washer on the hub's top face, driven snug. The washer seats on the flat hub: the nearest raised feature, the plate at y −13.5, is 8.5 mm beyond its rim, and the hub's edges are ≥ 2 mm outside it. The washer limits creep (rule §4) |
| 12 | Spec §3 dimensions are named parameters | PASS | L_C 32.0 (hex_frame.py:54), Z_F = T_C + 12 = 20 (:62), T_V 10 (:58), T_C 8 → 6 mm floor (:57), POST_W 13 (model.py:40). Window: SERVO + CLR/END_CLR (:35) + HOLE_COMP (:34). LEAD (:36), PILOT_X 9.7 (:37–39). All have source comments, and the comment values match `build()` (round-2 fix 3) |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG ≈ 70 °C. The femur-servo case sits in the window with 0.1–0.2 mm clearance: at the assembly spec's 50 °C case limit the margin is exactly 20 °C. Before slicing: `materials_on_hand` in config/printer.json is empty (spec §6 says to check) |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

**#6, what passes:**
- Horn-pocket bridge: 7.9 mm at z 2.0.
- Facing up at 45°: window roof, teardrops, tie-slot roof, ramp, gusset and corner cut.
- The pilot slots' far ends leave two arcs 0.63 mm wide at z 20.62–20.85 (x 11.62–12.25 and 42.05–42.68). They bridge themselves.
- 0.05 mm² at z 7.99, where the plate's square corner sits on the arm's r0.5 corner. Negligible.

**#10, notes:**
- Along the ramp (x −6.1 … 1.9) the plate's +y root is square. Strength's band section is the 48.9 mm under the plate proper, which the gusset covers.
- The reliefs are cut 1 mm past the tab face and nick the gusset tip by 0.3 mm or less (z 12.75 row: void 15.38–16.42 and 36.58–37.62). That is below print resolution.

## Required fixes

1. **Give the lead notch a 45° top instead of its flat ledge.**
   - **Rule:** fdm-design-rules §2: overhangs 45° or less, horizontal holes teardrop or flat-top. A flat top is fine only as a bridge anchored at both ends; this one is anchored at one. Checklist #6.
   - **Direct instruction:** deep review 01-B1 asks for this where a servo window sits in a standing wall, for the arm's turntable upright: "the notch is a horizontal hole in a standing wall: give it a 45° top". This window is in a standing wall too.
   - **Precedent:** rover-chassis DFM round 1, #6 (commit 70993cb) failed a flat shelf that mesh_check also reported as a "bridge" but that had one anchored edge. That shelf was 3 mm wide; this one is 1.41 mm.
   - **Evidence:** the probes and the overhang face in #6.
   - **Why it matters here:** the 3.6 × 1.2 mm lead ribbon slides right under this ledge (C x 37.9–39.1, z 18.2–21.8). The gap above it is 0.4 mm in CAD, ≈ 0.3 mm printed. Sag at the ledge's free edge, which is the window face, eats into that gap along the whole 10 mm the root travels. Spec §8's first criterion is that the lead root passes.
   - **Change:** add a right triangle to the cutter, in the x–z plane, with corners (38.1, 22.2), (39.51, 22.2) and (38.1, 23.61). Cut it through the plate (y −24.5 … −12.5). The ceiling then rises at 45° from the notch's end wall to the window face. Use `_prism_y` in model.py, or add a notch-roof option to `servo_mount_cutter`.
   - **No new problems:**
     - The triangle's nearest point, (39.51, 22.2), is ≥ 2.2 mm from the moved pilot's hole, including its teardrop.
     - The 1.34 mm ligament at the notch's end wall is unchanged.
     - The post keeps ≈ 11.6 mm at z 22.2, so its pilot row (net 9.49 mm: 1.34 + 8.15) stays the smallest section.
     - No strength section changes.
   - **Then:**
     - cad_checks.py: the notch check's solid probe at (38.9, −18.5, 22.4) falls inside the new roof, so move it to x 39.6. Add a void probe at (38.4, −18.5, 23.2) and a solid probe at (39.3, −18.5, 22.5).
     - Spec §3 and the brief's notch rows: write "4.4 at the end wall, opening at 45° to 5.8 at the window face".
     - The brief's Orientation line: it calls the notch top a "≤ 1.6 mm bridge"; correct it.
     - Rebuild, re-run mesh_check (the z 22.2 "bridge" must be gone), render and cad_checks.

## Round 2 fixes checked

1. **R1 reliefs at the window floor's corners: done.** `RELIEF_D` 2, teardrop, tangent to the post faces (probes in #10). Strength round 1 carried them at Kt 2.0.
2. **Gusset along the whole plate: done.**
   - It runs over `VPLATE_X`, x 1.9–51.1.
   - The arm's far corners are r0.5, so the old 1.9 mm² patch at z 4.99 over the r3 corner is gone. 0.05 mm² is left at z 7.99.
3. **Documentation: done.**
   - The model.py comments match `build()`: WIN_X 14.9…38.1, VPLATE_X 1.9…51.1, WIN_HALF 6.4, ROOF 11.6, VPLATE_H 41.0, GUSSET 4.9, TIE_XZ (47.5, 30).
   - The docstring gives the femur plane as −0.9…6.1 (Y_F + LB = −13.5 + 12.6) and the arm's clearance as 5.6 mm.
   - The brief's horn screw matches spec §2 and BUILD_GUIDE: M2 × 12 or × 14 with a Ø10 washer. Round 2's "M2 × 10" was for the 3 mm floor, which strength's 6 mm floor replaced.

Round-2 recommendations:
- The post check was done by strength round 1, which set T_V 10 and 13 mm posts.
- The lead exit is now B1 option 1 (fix 1 concerns its top).
- geometry.json `holes` is a valid list now.

## Print layout: the designer's 2 brackets per plate

- **No DFM objection.** Both layouts fit (#1).
- **Short layer times:** with only two parts, the posts' upper layers (two 13 × 10 mm islands per part) print quickly. The PETG profile's minimum-layer-time slowdown will slow them. That is expected, not a defect.
- **slice_plan.json disagrees:** it still says `"copies": 6` ("6 copies per plate"), against the brief's 2 per plate. Six brackets take ≈ 15 h, against spec §7's 6 h per batch. The slicing stage must change it, or the user relaxes §7.

## Recommendations (not blocking)

- **Strength re-check:**
  - the pilot ligaments at 1.45 / 1.34 mm CAD (round 1 used 1.60);
  - the outboard screw through the filed slit;
  - the plate's out-of-plane rows at the round-3 mass.
- **Builder:** fit one MG90S through the notch and its filed slit before filing all six (the brief already says so).
- **Tie slot:** it has no HOLE_COMP: 1.8 × 3.2 CAD prints ≈ 1.6 × 3.0. The BUILD_GUIDE's ties (≤ 2.5 wide, ≈ 1 thick) still pass, so no change is needed.

VERDICT: PASS

# DFM review: 20261026-arm-claw-frame (round 3)

Reviewer: dfm-reviewer (independent) · 2026-10-26 · DESIGN gate, round 3 (rounds 1 and 2: FAIL). This is the third design attempt.

**Inputs:**
- this job: spec.md (§1 holds the round-3 values), design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json, print_requirements.json, log.md (the 15:16Z lines), and the round-2 design_review.md and strength.md;
- renders/*.png, regenerated with `tools/render.py`; all 5 viewed;
- `../20261025-robot-arm-assembly/`: claw_frame.py, claw_sequence_check.py (re-run), assembly_check.json, BUILD_GUIDE §4 steps 7–9;
- tools/hobby_parts.py;
- library/: no lessons and no material rows, so the skill defaults apply.

**The outputs are current.** Each check below was run on the round-3 files:
- `build()` rebuilt in memory gives 46 477.38 mm³ and 14 986.02 mm², the same as geometry.json. part.stl gives 46 477.7 mm³.
- `tools/mesh_check.py` re-run: overhang 1.41 %, bed contact 2534.7 mm², widest bridge 7.9 mm, thin walls 0.
- `cad_checks.py` exits 0, with 15/15 PASS.

**Extra evidence:**
- **Layer check** of part.stl: 0.2 mm layers on a 0.04 mm raster. Each layer is compared with the one below grown 0.3 mm, and every patch is reported with its distance from material below.
- **Thin-feature test:** a per-layer 0.9 mm morphological opening.
- **Bridge columns:** a per-column look at the window-roof bridge next to the washer relief.

Print frame = claw frame G: the back face is on the bed, and z is up.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits the bed with a 5 mm margin | PASS | 42.85 × 64.0 × 48.5 mm, `fits_bed: true` |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, `min_z_mm: 0.0` |
| 3 | Orientation matches the brief | PASS | Back face on the bed with the horn pocket in it (bottom.png). Rising from the plate (iso.png, front.png, top.png): the bulkhead with its window, the rail block from the bulkhead's front face to x 22.35, the pad behind the bulkhead, and the two ribs at the y ends |
| 4 | Load paths vs layers | PASS (justified) | **Round-2 fix 2 is done.** The brief's table names the rail block as a cantilever off the plate with its root stress along z, across the layers. It also names the sharp rack-side root (x 22.35, z 6, Kt 2.5) and the worst case: rack B's end at the free end y +32, jaws open, b_eff 7.9. **The rail is a block back to the bulkhead now** (RAIL_X0 = X_B = 10; cad_checks "rail block … x 10 to x 22.35"). The brief predicts SF 6.31 for it (round 2: 0.65); the number is strength's to confirm. **Other across-layer paths in the table:** the bulkhead root (with the ribs), the window strips, the clamp floor punching and the tab-pilot strips |
| 5 | Bed contact | PASS | 2534.7 mm² of PETG on a 42.85 × 64 plate |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | **Round-2 fix 1 is done: the lead notch has a 45° top.** `_notch_top()` (model.py l.95–108) adds the triangle (y 7.5, z 29.45) → (y 6.1, z 30.85). The layer check finds nothing between z 29.3 and 31.0; round 2 had a 7.6 mm² one-sided ledge at z 29.5. mesh_check's z 29.45 entry is the 0.01 mm overlap sliver (0.1 mm²). **The layer check finds only these patches:**<br>• the pocket ceiling, z 2.1: 7.9 mm bridge, anchored all round, 3.74 mm from support at most;<br>• the front pilots' flats, z 4.1: 0.91 mm between 45° flanks;<br>• the pilot slots' 0.17 mm flats, z 28.1;<br>• the window-roof flat, z 40.7: 9.2 mm, two-sided.<br>**New this round:** the Ø9 washer relief removes the roof flat's +y anchor over x 3.5–4.45, the 1 mm of bulkhead next to the back face (columns end at y −2.78 to −0.86 against the relief). Those lines sit inside the 4 perimeters (1.8 mm), which follow the relief's arc onto the shoulder at (x 4.45, y −0.8), so they stay anchored at both ends: about 9.5 mm along the path. Every point is within 4.80 mm of material below (round 2: 4.48), so it is still a two-sided bridge under 10 mm. overhang_pct 1.41 |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (user-accepted deviation) | **MG90S tab-pilot strips: 1.34 mm CAD at the lead end, 1.45 at the far end.** These are a deviation the user accepted on 26 Oct 2026, covered by the spec §8 screw-strip check on the first printed frame (both M2 × 8 snug, no whitening, no crack; BUILD_GUIDE §4 step 8 repeats it). They are not a fail. No strip is under 0.9 mm. **Other walls:**<br>• bulkhead 6.5 (5.5 where the relief cuts it, \|y\| ≤ 2.83);<br>• ribs 6 × 10;<br>• rail block 12.35 deep;<br>• 1.9 mm skin over the front pilots;<br>• the top pilots stay 4.55 / 6.55 mm from the window and roof.<br>`thin_wall_warnings` is empty, and the 0.9 mm opening finds nothing in any layer |
| 8 | HOLE_COMP; horizontal holes teardrop or flat-top | PASS | `HOLE_COMP = HOLE_COMP_DEFAULT` on:<br>• the window: 23.2 × 12.8 CAD;<br>• the notch, 4.4 × 1.6, now with its 45° top;<br>• the tab pilots, Ø1.7 teardrop slots;<br>• the clamp hole (Ø2.6), the top pilots (Ø2.7) and the front pilots (Ø2.2);<br>• the washer relief: Ø8 + 2 × 0.4 + 0.2 = Ø9.0.<br>geometry.json's measure_holes agrees: 2.6, 2.7, 2.7, 2.2, 2.2. The front pilots are flat-topped teardrops, 14 deep. The point_on_axis x 27.85 is the middle of x 20.85–34.85 |
| 9 | Bottom edges chamfered | PASS (note) | 0.4 mm `chamfer_plane_edges` on the plate blank (model.py l.132; bottom.png). The pocket and clamp-hole mouths are loose fits cut after it, as in rounds 1–2 |
| 10 | Internal corners on load paths filleted | PASS | **Filleted:**<br>• the pad / bulkhead back root, r 1.5, full width except where the relief interrupts it (strength fix 3; cad_checks);<br>• the window's lower corners, Ø3 reliefs.<br>**Sharp, named in the brief with Kt 2.5 for strength:**<br>• the rail block's rack-side root (x 22.35, z 6), a channel corner where rack B's square edge runs 0.25 away;<br>• the rib roots on the pad.<br>The old sharp bulkhead front root (x 10, z 6) is gone: the rail block fills it. The new re-entrant corner at the block top (x 10, z 17.75) is R1 |
| 11 | Fasteners per §4 | PASS | **Wrist clamp:** M2 × 12 + Ø8 × 0.8 washer on the pad. 12 − 0.8 − 6.3 − 0.6 = 4.3 mm into the spline, within BUILD_GUIDE §2's ≥ 5.1 mm thread check. The washer (r 4.0) lies inside the r 4.5 relief, clear of the fillet. **Claw servo:** M2 × 8 in 6.5 mm, the lead-end slit filed to 2.1 (BUILD_GUIDE §4 step 8). **Cover:** M3 × 10 or × 18 into the 14 mm top pilots, and M2.5 × 16 through the 5 mm front plate into the 14 mm front pilots: 11 engaged, 3 mm spare. Self-tapping is fine for service-only joints |
| 12 | Spec §3 dims are named parameters | PASS (note) | ZS 27.25, X_B 10, T_W 6, RAIL_X0 10 / RAIL_X1 22.35, the clamp floor T_W + PAD_T − HORN_DEPTH = 6.3, WASHER_RELIEF_D, RIB_W/RIB_D and FRONT_PILOT_DEPTH 14 are all named with source comments (model.py l.50–62, claw_frame.py). **Note:** spec §3 still gives the wrist plate front edge as x 32.85, and the §1 round-3 line doesn't override it. The model has X_F0 = 34.85, following FACE_W 12 (recorded in the cover's and pinion's spec §1 and in claw_frame.py). That is a spec wording gap for the Architect (R2), not a design error |
| 13 | Service temperature | PASS | 40 °C against PETG at ≈70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ |

**Assembly:** `claw_sequence_check.py` re-run on the round-3 parts:
- every insertion path is 0 mm³ (servo, cover, camera mount, jaw A, jaw B);
- the swept pinion is 0 mm³;
- the stroke 0–44 every 1 mm is 0 mm³, and so is one tooth pitch in 0.1 mm steps;
- backlash is 0.40 per mesh;
- `ok: true`.

assembly_check.json (89b2f2a) has no collisions in any pose or sweep. Its `claw_internal` matches.

## Required fixes

None.

## Round-2 required fixes

| Round-2 fix | Status | Evidence |
|---|---|---|
| 1. 45° top on the lead notch | Done | `_notch_top()`; the layer check is clean at z 29.3–31.0; cad_checks "lead notch … 45° top" |
| 2. Name the rail's across-layer bending; strength to check it | Done (brief), and redesigned | The brief's load-path table names it (item 4). The rail is a block from the bulkhead (x 10–22.35), and spec §1 records it |

**Round-2 strength fixes, as built:**
- the rail block;
- the Ø8 washer with its 1 mm relief (cad_checks: r 4.5, pad top whole);
- the r 1.5 back fillet;
- the two 6 × 10 ribs at y ±(26…32), x −6.5…3.5, from the pad to the top;
- the M2.5 × 16 front screws in 14 mm pilots.

The ribs clear the claw servo (y −16.9…5.9) and the top screws (y −23, 14), and they carry the cover's top wall at z 48.5 (a declared contact plane).

## Recommendations (not blocking)

- **R1. Block-top corner.** An r 1.5 fillet at the rail block's top / bulkhead front corner (x 10, z 17.75) would take Kt off the bulkhead's front face under a −x USB tug. It fits: it reaches z 19.25, below the claw servo's tabs at z 21.15. Strength can tell whether it is needed.
- **R2. For the Architect, spec §1.**
  - Add "wrist plate front edge x 34.85 (FACE_W 12); envelope 42.85 × 64 × 48.5". §2 and §3 still say x 32.85 and 40.85.
  - §2 still describes the "rail wall x 18.35–22.35" and the "M2.5 × 12". §1 overrides both, but rewriting §2–§3 would remove the ambiguity.
- **R3. Process.** slice_plan.json, slice_settings.json, slice_stats.json and validation.json in this folder are from before round 1. Re-slice after the DESIGN gate passes.

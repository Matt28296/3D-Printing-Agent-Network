VERDICT: PASS

# DFM review: 20261026-arm-claw-pinion (round 3)

Reviewer: dfm-reviewer (independent) · 2026-10-26 · DESIGN gate, round 3. The pinion's round 2 DFM was PASS; it was rebuilt this round for the pinion strength round 2 change.

**Inputs:**
- this job: spec.md (§1 holds the round-3 values), design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json, print_requirements.json, log.md (the 15:16Z lines), and the round-2 design_review.md and strength.md;
- renders/*.png, regenerated with `tools/render.py`; all 5 viewed;
- `../20261025-robot-arm-assembly/`: claw_frame.py, claw_sequence_check.py (re-run), assembly_check.json;
- tools/gears.py and tools/hobby_parts.py (`horn_pocket_cutter`);
- library/: no lessons and no material rows, so the skill defaults apply.

**The outputs are current.**
- `build()` rebuilt in memory gives 3335.64 mm³ and 2223.12 mm², the same as geometry.json.
- `tools/mesh_check.py` re-run: overhang 3.07 %, bed contact 193.4 mm², one bridge of 7.5 mm, thin walls 0.
- `cad_checks.py` exits 0, with 10/10 PASS.

**Extra evidence:**
- **Layer check** of part.stl: 0.2 mm layers on a 0.02 mm raster, each layer compared with the one below grown 0.3 mm.
- **Thin-feature test:** a per-layer 0.9 mm morphological opening.
- **Chamfer band:** `gears._chamfer_band` rebuilt on this outline (PINION_BACKLASH 0.1, r 0.38 root fillets, 0.15 tip relief) at 0.25, as a ruled loft and as 0.1 mm steps.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits the bed with a 5 mm margin | PASS | 21.7 × 21.7 × 12.0 mm, `fits_bed: true` |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, `min_z_mm: 0.0` |
| 3 | Orientation matches the brief | PASS | Horn-pocket face on the bed, axis vertical. bottom.png shows the clipped horn pocket with its mouth chamfer and the bed chamfer on every tooth. top.png and iso.png show the 20 teeth, the deeper counterbore and the clamp hole |
| 4 | Load paths vs layers | PASS | Tooth bending and horn-stub bearing lie in the layer plane. The clamp preload squeezes the 6.3 mm floor |
| 5 | Bed contact | PASS | 193.4 mm², PETG; the mouth chamfer takes 4.3 mm² off round 2's 197.7 |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | **The layer check finds only the pocket ceiling:** z 2.1, 7.5 mm, anchored all round, every point within 3.56 mm of support. **The 0.2 mm pocket-mouth chamfer** is a 45° inward step of one layer; nothing is flagged at z 0.3. **The counterbore** opens upward. overhang_pct 3.07 is the ceiling |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (note) | `thin_wall_warnings` is empty, and the 0.9 mm opening finds nothing.<br>• **Counterbore Ø6.4 to the root circle (r 8.75):** 5.55 mm.<br>• **Pocket stubs (r 5.65 CAD) to the root circle:** 3.1 mm.<br>• **Floor:** 6.3 mm, from z 2.0 to the counterbore bottom at z 8.3 (cad_checks).<br>• **Teeth:** the teeth are now only 0.05 thinner, 1.52 mm at the pitch line. The tip land is ≈0.79 after the 0.15 topping: the tapering tip of a tooth, as accepted before |
| 8 | HOLE_COMP; horizontal holes | PASS | Pocket: POCKET_CLR 0.1 + HOLE_COMP (hub Ø7.5 CAD, stubs to r 5.65). Clamp hole Ø2.6 = 2.4 + 0.2. Counterbore Ø6.4 = PINION_CB_D 6.2 + 0.2. measure_holes: 2.6 and 6.4. No horizontal holes |
| 9 | Bottom edges chamfered | PASS | **Teeth:** 0.25 × 45° on the whole tooth outline. The inset keeps 780 of 780 edges. Rebuilt here, the loft's band is 72.0579 mm³ against 72.0571 for the stepped band (0.001 %), so it is a true face. The value is under the rule's 0.3, but it is gears.py's true-45° limit for module 1, as accepted in rounds 1–2. **Pocket mouth:** now chamfered 0.2 × 45° (`_pocket_mouth()`, round-2 R1). cad_checks measures 0.15 wider at z 0.05, so no first-layer lip forms on the 0.1 mm fit. The horn plate sits at z 0.4–2.0, above it |
| 10 | Internal corners on load paths filleted | PASS | Tooth roots r 0.38 (`PINION_ROOT_FILLET`). The rule's r ≥ 1 can't fit a module-1 root |
| 11 | Fasteners per §4 | PASS | M2 × 12 + Ø6 × 0.5 washer in the Ø6.4 × 3.7 counterbore: 12 − 0.5 − 6.3 − 0.6 = 4.6 mm into the spline, as for every horn clamp. The head sits below the front face, inside the cover's pass-through. CB_H is derived as FACE_W − HORN_DEPTH − PINION_FLOOR, so the floor follows FACE_W |
| 12 | Spec §3 dims are named parameters | PASS | M 1, Z_TEETH 20, FACE_W 12, PINION_BACKLASH 0.1 / RACK_BACKLASH 0.7 (cad_checks: tooth 0.05 thinner), TIP_RELIEF 0.15 (Ø21.70), PINION_ROOT_FILLET 0.38, POCKET_CLR 0.1, POCKET_CHAMFER 0.2, CB_D 6.2, CB_H 3.7. All are named with comments. Spec §1 records FACE_W 12, the backlash split, the 3.7 counterbore and the 0.2 mouth chamfer, and it overrides the older §3 rows |
| 13 | Service temperature | PASS | 40 °C against PETG at ≈70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ |

**Mesh and assembly:** `claw_sequence_check.py` re-run:
- the pinion swept in axially through the pass-through is 0 mm³ against the frame, servo, cover, camera mount, screws and both jaws;
- it comes out once the claw is ≥ 22 mm open;
- the stroke 0–44 is 0 mm³, and so is one tooth pitch in 0.1 mm steps;
- the measured backlash is 0.40 per mesh, against the design's 0.40 = (0.1 + 0.7) / 2;
- `ok: true`.

assembly_check.json has no collisions.

## Required fixes

None.

## Round-2 recommendations

| Round-2 item | Status | Evidence |
|---|---|---|
| R1. Chamfer the horn-pocket mouth | Done | POCKET_CHAMFER 0.2 (item 9) |
| R2. Check the tip lands fill in the preview | Open | For slicing (R1 below) |
| R3. Re-slice after DESIGN | Open | R2 below |

**Round-2 strength change, as built:** FACE_W 12; PINION_BACKLASH 0.1 with the racks' 0.7; the counterbore 3.7 deep, floor 6.3.

## Recommendations (not blocking)

- **R1. Slicing.** Check in the preview that the ≈0.79 mm tip lands fill.
- **R2. Process.** The slice files in this folder are from before round 1. Re-slice after the DESIGN gate passes.

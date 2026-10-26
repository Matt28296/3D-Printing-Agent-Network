VERDICT: PASS

# DFM review: 20261026-arm-claw-jaw (×2) (round 3)

Reviewer: dfm-reviewer (independent) · 2026-10-26 · DESIGN gate, round 3 (rounds 1 and 2: FAIL). This is the third design attempt.

**Inputs:**
- this job: spec.md (§1 holds the round-3 values), design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json, print_requirements.json, log.md (the 15:16Z lines), and the round-2 design_review.md and strength.md;
- renders/*.png, regenerated with `tools/render.py`; all 5 viewed;
- `../20261025-robot-arm-assembly/`: claw_frame.py, claw_sequence_check.py (re-run), assembly_check.json;
- tools/gears.py (`_chamfer_band`, `_extrude_chamfered`);
- library/: no lessons and no material rows, so the skill defaults apply.

**The outputs are current.**
- `build()` rebuilt in memory gives 17 118.35 mm³ and 6463.10 mm², the same as geometry.json. part.stl is the same volume and has 3470 faces.
- `tools/mesh_check.py` re-run: overhang 0.0 %, bed contact 571.9 mm², no bridges, thin walls 0.
- `cad_checks.py` exits 0, with 12/12 PASS.

**Extra evidence:**
- **Layer check** of part.stl: 0.2 mm layers on a 0.04 mm raster, each layer compared with the one below grown 0.3 mm. It covers all 304 layers.
- **Thin-feature test:** a per-layer 0.9 mm morphological opening.
- **Chamfer band:** `gears._chamfer_band` rebuilt on the jaw's rack outline at 0.25, as a ruled loft and as 0.1 mm steps.

Print frame: (X, Y, Z) = claw G (−z, y, x − 22.6). The rack stands on its x 22.6 face, finger up.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits the bed with a 5 mm margin | PASS | 31.25 × 56.55 × 60.75 mm, `fits_bed: true`; two copies fit one plate |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, `min_z_mm: 0.0` |
| 3 | Orientation matches the brief | PASS | Standing on the rack's x 22.6 face, finger up, teeth in the bed plane (iso.png, front.png, right.png) |
| 4 | Load paths vs layers | PASS (justified) | The brief says every bending of the neck and finger runs across the layers, and sizes them for 12.5 MPa (candidate C). Tooth bending is in the bed plane |
| 5 | Bed contact | PASS (note) | 571.9 mm², PETG, no brim (`max.brim_width` 0: a brim would fill the tooth gaps). The note from round 2 stands: the part is tall (60.75 mm), and the finger overhangs its footprint. The brief keeps the sacrificial-ears fallback (R1) |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | **Round-2 fix 1 is done.** BED_CHAMFER 0.25 (model.py l.39). The layer check finds **no unsupported patch in any layer**; round 2 had 14 teeth hanging up to 1.04 mm at z 0.3. Also:<br>• the finger's 45° edges, the gusset and the grooves all recede;<br>• there are no bridges;<br>• overhang_pct 0.0 |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (note) | `thin_wall_warnings` is empty (round 2: 20, capped, from the twisted chamfer), and the 0.9 mm opening finds nothing in any layer. Rack back 10, neck 20 × 10, finger 12 → 6. **Notes:**<br>• the tooth tip land is 0.60 mm after the 0.35 thinning and 0.15 topping, the tapering tip of a tooth, as accepted for the pinion;<br>• the fingertip is thin by design behind the V-notch (round-1 R3) |
| 8 | HOLE_COMP; horizontal holes | N/A | No holes (measure_holes: none) |
| 9 | Bottom edges chamfered | PASS | **The bed chamfer outline is clean:**<br>• the 0.25 inset keeps all 256 outline edges (cad_checks: (256, 256));<br>• rebuilt here, the ruled loft's band is 148.6462 mm³ and the 0.1 mm stepped band's is 148.6451 mm³, a 0.0007 % difference, so it is a true 45° face, not a twisted one;<br>• the mesh is 3470 faces (round 2: 182 706);<br>• cad_checks shows the back edge is inset 0.2 at x 22.65.<br>`tools/gears.py` now refuses a loft whose inset loses edges (l.167–170), so the round-2 twist can't pass silently. The value is under the rule's 0.3, but it is gears.py's true-45° limit for module 1, as accepted for the pinion |
| 10 | Internal corners on load paths filleted | PASS | Neck roots r 4 at both y edges; kink fillets r 3; gusset end and taper r 3; rack tooth roots r 0.30 |
| 11 | Fasteners per §4 | N/A | No fasteners |
| 12 | Spec §3 dims are named parameters | PASS (note) | RACK_OUT − R_P 11.25, FACE_W 12, RACK_BACKLASH 0.7 (cad_checks: half width 0.6104 at the pitch line), TIP_RELIEF 0.15, NECK_Y × NECK_Z 20 × 10, X_TIP 83.35, GROOVE_X (62.6, 71.0). All are named with comments. Spec §1 records FACE_W 12, the grooves and BED_CHAMFER 0.25. **Note:** the teeth row in spec §3 still says "0.25 thinner, 0.35 per mesh". Only the pinion's spec §1 records RACK_BACKLASH 0.7 / 0.40 per mesh (R2) |
| 13 | Service temperature | PASS | 40 °C against PETG at ≈70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ |

**Grooves:** GROOVE_X = (GRIP_X0 + 1, 71.0) cuts V-grooves at x 62.6, 64.6, 66.6, 68.6 and 70.6, each ±0.6 wide, so x 62.0–71.2. cad_checks confirms none beyond, leaving 12.15 mm of plain finger to the tip at 83.35. right.png and iso.png show five grooves only.

**Assembly:** `claw_sequence_check.py` re-run:
- jaw A's and jaw B's slide-ins are 0 mm³ (91 positions each);
- the stroke 0–44 is 0 mm³, and so is one tooth pitch in 0.1 mm steps;
- the swept pinion against both jaws is 0 mm³;
- backlash is 0.40 per mesh;
- `ok: true`.

assembly_check.json has no collisions.

## Required fixes

None.

## Round-2 required fixes

| Round-2 fix | Status | Evidence |
|---|---|---|
| 1. True 45° bed chamfer (BED_CHAMFER 0.25, or a gears.py fallback) | Done, both | BED_CHAMFER 0.25, and gears.py refuses a twisted loft. Items 6, 7 and 9 |

**Round-2 strength change, as built:** the grooves stop at x 70.6, with none in the last 12.7 mm (cad_checks). FACE_W 12 and RACK_BACKLASH 0.7 follow the pinion's change.

## Recommendations (not blocking)

- **R1. Bed adhesion (item 5).** If the first print rocks, add two small sacrificial ears at the rack's y ends, away from the teeth and the back face.
- **R2. For the Architect.** Bring spec §3's teeth row up to date: each tooth 0.35 thinner, 0.40 backlash per mesh with the pinion's 0.05. Today only the pinion's spec §1 carries it.
- **R3. Slicing.** Check in the preview that the 0.60 mm tooth tip lands fill.
- **R4. Process.** The slice files in this folder are from before round 1. Re-slice after the DESIGN gate passes.

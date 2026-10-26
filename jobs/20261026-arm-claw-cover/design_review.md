VERDICT: FAIL

# DFM review: 20261026-arm-claw-cover (round 3)

Reviewer: dfm-reviewer (independent) · 2026-10-26 · DESIGN gate, round 3 (rounds 1 and 2: FAIL). This is the third design attempt.

**Inputs:**
- this job: spec.md (§1 holds the round-3 values), design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json, print_requirements.json, log.md (the 15:16Z lines), and the round-2 design_review.md and strength.md;
- renders/*.png, regenerated with `tools/render.py`; all 5 viewed;
- `../20261025-robot-arm-assembly/`: claw_frame.py, claw_sequence_check.py (re-run), assembly_check.json, BUILD_GUIDE §4 step 9;
- library/: no lessons and no material rows, so the skill defaults apply.

**The outputs are current.**
- `build()` (the cover plus its pillars) rebuilt in memory gives 31 791.09 mm³ and 15 639.02 mm², the same as geometry.json.
- `tools/mesh_check.py` re-run: overhang 0.27 %, bed contact 703.6 mm², thin walls 0.
- `cad_checks.py` exits 0, with 14/14 PASS.

**Extra evidence:**
- **Layer check** of part.stl: 0.2 mm layers on a 0.04 mm raster, each layer compared with the one below grown 0.3 mm.
- **Pillar coverage:** the same check run a second way, with support taken as the union of the 3 layers below. This counts each pillar's top across its gap and measures how much of each piece's first layer it carries.
- **Thin-feature test:** a per-layer 0.9 mm morphological opening.

Print frame: (X, Y, Z) = claw G (x, −z, y + 32), so G +y is up.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits the bed with a 5 mm margin | PASS | 39.85 × 57.5 × 64.0 mm, `fits_bed: true` |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1` as printed and as fitted (cad_checks), watertight, `min_z_mm: 0.0` |
| 3 | Orientation matches the brief | PASS | Standing on its −y end, `TO_PRINT = Rot(90, 0, 0)`. bottom.png shows the side profile with both ties' feet on the bed. right.png shows:<br>• slot A rising from the bed to its 45° roof;<br>• the pass-through with its 45° top;<br>• slot B open at the top;<br>• the two pillars as thin posts inside the pass-through. |
| 4 | Load paths vs layers | PASS | **Round-2 fix 2 is done.** The brief now says "The round-2 brief said 'all bending runs along the layers'. That was wrong." Its table names paths (a), (b) and (c) as bending along y, across the layers:<br>• (a) the strip under slot B, z −6…5.75, from slot B's closed end to the +y M2.5;<br>• (b) the top wall between the two top screws;<br>• (c) the lower half of the plate, out to the first tie and the −y M2.5.<br>The upper piece hanging from the top wall, the 8 mm lip and both ties are loaded in the side profile, along the layers. The text matches the geometry, and strength checks (a)–(c) at 12.5 MPa |
| 5 | Bed contact | PASS | 703.6 mm² on a 64 mm-tall part, with `min.brim_width` 5 in print_requirements.json |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | **FAIL** | **The brief's justification holds.** The pass-through is r 11.4 CAD, so its top (z 38.65) passes slot A's edge (38.25) and its bottom (15.85) passes slot B's (16.25). The slots open at opposite ends. So the two pieces beside the pass-through can't be re-laid to grow from material below them. Modelled supports, with `support_material` 0 required, are the right answer, and BUILD_GUIDE §4 step 9 lists their removal.<br><br>**Pillar A (piece (a), slot-A side) carries its piece:**<br>• 1.3 thick, z 36.8…38.1, from y −8;<br>• the piece's first slice (print z 38.5, G y 6.5) spans z 36.62…38.25, so 0.18 / 0.15 mm overhangs the pillar;<br>• pillar coverage check: only the 0.5 mm x-inset strips at the two plate faces, 0.73 mm² in all, ≤ 0.54 mm from the pillar.<br><br>**Pillar B (piece (b), slot-B side) does not:**<br>• 1.0 thick, z 16.35…17.35, from y −6;<br>• the piece's first printed layer (print z 39.0–39.2, G y 7.1) spans **z 16.25…18.33**;<br>• the pillar carries only the lower half;<br>• pillar coverage check at z 39.1: **4.24 mm² of the 10.4 mm² first layer is more than 0.3 mm from the pillar, up to 1.13 mm away**: a 0.9–1.0 mm strip along the pass-through edge (G z 17.35…18.33) over the full 5 mm plate thickness.<br>That strip starts in mid-air over a 0.2 mm gap. It is neither supported nor justified: the brief's pillar table says "under piece (b)" without noting the uncovered half.<br><br>**Everything else passes:**<br>• slot A's apex (z 42.9–43.1, ≤ 0.56 mm);<br>• the pass-through apex (z 47.5, 0.76 mm);<br>• the end of the corner fillet (z 41.1, 0.2 mm²): all three are r 1.5 / r 2 roundings, accepted in round 2;<br>• the second tie: its post underside is exactly 45° and its web undersides ≈35° from vertical. The layer check finds no patch.<br>overhang_pct 0.27 |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (note) | Front plate 5, top wall 3, lip 8; posts 8 × 8 (first tie) and 4 × 8 (second tie); strip under slot B 11.75 deep. `thin_wall_warnings` is empty. The 0.9 mm opening flags only 0.33–0.45 mm² at print z 46.5–46.7, G (x 28–29.4, y 14.6, z 34.6–35.2). There the second tie's two 45° growth fronts (from the post and from the plate) meet at the web's top edge. It is the meeting tip of two supported wedges in one layer, not a wall, and has material under it. Note as in round 2: 1.25 mm between the +y front-screw hole and slot B's lower edge, under the screw head |
| 8 | HOLE_COMP; horizontal holes teardrop or flat-top | PASS | Pass-through Ø22.8 = ACCESS_D 22.6 + HOLE_COMP, teardrop top. Top holes Ø3.6 and front holes Ø3.0, all teardrops pointing up in print. measure_holes: 3.0, 3.0, 3.6, 3.6, 22.8 (270° arcs) |
| 9 | Bottom edges chamfered | PASS | 0.3 mm bed chamfer (model.py l.192), with the openings cut before it, so slot A's mouth is chamfered (bottom.png). The pillars don't reach the bed |
| 10 | Internal corners on load paths filleted | PASS | **Filleted (cad_checks):**<br>• slot B's closed end, r 2;<br>• slot A's roof into the top wall, r 2;<br>• the front plate / top wall corner over y 9–32, r 2.<br>**Sharp, in strength's Kt 2.5 rows:**<br>• the lip's rack-side root (a channel corner; SF 5.30 predicted);<br>• the webs' corners on the front plate (low stress) |
| 11 | Fasteners per §4 | PASS | M3 × 10 (or × 18 through the camera mount) through Ø3.6 into the frame's 14 mm pilots. M2.5 × 16 pan heads (≤ Ø5) through Ø3.0 into the frame's 14 mm front pilots: 11 engaged. `front_screws` is 0 mm³ on every path and over the stroke |
| 12 | Spec §3 dims are named parameters | PASS | X_F0 / X_F1 34.85 / 39.85, FRONT_Z0 −6, Z_TOP0 48.5, LIP_X0 / RAIL_X1 14.35 / 22.35, ZA0/ZA1 38.25/48.5, ZB0/ZB1 5.75/16.25, R_PASS 11.4, TIE2_Y, SUP_A / SUP_B / SUP_GAP. All are named with comments, and spec §1 records the round-3 values |
| 13 | Service temperature | PASS | 40 °C against PETG at ≈70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ |

**Can the pillars come off without damage?** Yes for both, as BUILD_GUIDE §4 step 9 describes: pliers at the foot, then trim the nub flush.
- **Pillar A's foot** is on the cut-back's end face (y −7). That face lies at r ≥ 11.84 from the axis, outside the r 11.4 pass-through, so a nub there can't reach the pinion.
- **Pillar B's foot** is partly on the pass-through surface (z 17.0…17.35 at y −5…−5.65). The trim-flush instruction matters there: 0.45 mm printed radial clearance to the pinion. The fix keeps this, over z 17.0…18.05.

**Assembly:** `claw_sequence_check.py` re-run (it uses `design()`, without the pillars):
- the cover's descent is 0 mm³ (57 positions), and so are both jaw slide-ins and the swept pinion;
- the stroke 0–44 is 0 mm³;
- `ok: true`.

assembly_check.json has no collisions.

## Required fixes

1. **Make pillar B carry the whole first layer of piece (b) (item 6).**
   - **Change:** in model.py l.66, `SUP_B = (-6.0, CRESCENT_Y, ZB1 + 0.1, ZB1 + 1.1)` → `SUP_B = (-8.0, CRESCENT_Y, ZB1 + 0.2, ZB1 + 1.8)`. The pillar is then G y −8 → 6.75, z 16.45…18.05 (1.6 thick), x 35.35…39.35 as before.
   - **Why the start moves to y −8:** there the plate is solid up to the pass-through at z 19.13, so the whole 1.6 mm foot grows out of the lower piece. At y −6 it is solid only to z 17.56, and that is why the pillar was held to 1.0 mm.
   - **Result:** piece (b)'s first layer (print z 39.0–39.2, z 16.25…18.33) overhangs the pillar by only 0.20 mm and 0.28 mm, within the 0.3 mm allowance. Piece (a) is already within it at 0.18 / 0.15.
   - **What stays the same:**
     - SUP_GAP 0.25: the realised gap is exactly one 0.2 mm layer, 38.8–39.0;
     - the clearance to slot B (the void below z 16.25);
     - the 1.6 × 4 mm section, which still snaps with pliers;
     - BUILD_GUIDE §4 step 9 as written.
   - **Then:**
     - update the brief's pillar table and cad_checks.py's pillar probe (z 16.45…18.05, from y −8);
     - rebuild, re-run mesh_check, and re-render;
     - re-run the layer check with the pillar tops counted as support (union of the 3 layers below). No patch of either piece's first layer may lie more than 0.3 mm beyond its pillar, apart from the 0.5 mm x-inset at the two plate faces.
     - `design()` doesn't change, so claw_sequence_check stays valid.
   - **Rule:** fdm-design-rules §2 (overhangs ≤ 45° unless supported); checklist item 6 ("supported and justified").
   - **Evidence:** item 6, the pillar coverage check at print z 39.1: 4.24 mm², up to 1.13 mm from the pillar. In right.png, the right-hand pillar is a 1 mm post against slot B's edge, under only part of the piece above it.

## Round-2 required fixes

| Round-2 fix | Status | Evidence |
|---|---|---|
| 1. Give both hanging regions a supported start | **Partly done** | Route (a), modelled breakaway pillars, justified in the brief; slicer supports off; removal in BUILD_GUIDE step 9. Pillar A is adequate; pillar B covers only half its piece (fix 1) |
| 2. Name the across-layer load paths | Done | Brief table (a)–(c) (item 4) |

**Round-2 strength changes, as built (cad_checks):**
- the 8 mm lip (x 14.35…22.35), with the first tie's post grown to match;
- the second tie at y 24…32: post x 18.35…22.35 from the lip at y 6.5, web with 45° and steeper undersides, clear of the pinion's r 11.4;
- FRONT_Z0 −6 (strip 11.75 deep);
- FACE_W 12 (plate x 34.85…39.85);
- M2.5 × 16.

## Recommendations (not blocking)

- **R1. Pillar A's gap.** Piece (a)'s underside (G y 6.5, print z 38.5) lies exactly on the mid-plane of the 38.4–38.6 layer, so the slicer may start the piece there or one layer later. If it starts at 38.6–38.8, the piece spans z 36.47…38.45, 0.33 / 0.35 mm beyond the pillar, over a 0.4 mm gap. Setting SUP_A's z to `ZA0 - 1.6, ZA0 - 0.1` (z 36.65…38.15) covers both cases within 0.3. The base at y −8 stays inside the plate, which is solid there from z 35.37. This is cheap to do with fix 1. Either way, look at the slicer preview at print z 38.2–39.2 when slicing.
- **R2. The 1.25 mm ligament** between the +y front-screw hole and slot B (item 7): keep it in strength's slot-B strip check, as in round 2.
- **R3. Process.** The slice files in this folder are from before round 1. Re-slice after the DESIGN gate passes.

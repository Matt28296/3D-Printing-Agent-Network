VERDICT: PASS

# DFM recheck (round 5): 20261026-arm-claw-cover

cad-engineer, 2026-10-26: the checks run on the round-5 geometry (round 4's required fix 1, user-approved). **This is the
designer's own recheck, not an independent review**; the round-4 independent review follows unchanged below.

**Change (model.py):**
- `TIE2_FOOT_Z` 17.75 → **17.85**: the post's foot flats stand 0.1 over the frame's rail block.
- **V-ridge** under the foot (`ridge()`): the frame groove's 90° V raised 0.1, so it is 0.1 clear per flank horizontally
  (0.071 normal). Virtual apex z 17.05 (0.8 under the flats), base x 14.45–16.05, y 24–32, a 45° lead-in over y 24–24.6.
- **The ridge's tip is cut flat at z 17.25** (0.4 wide, 0.6 under the flats). The groove's first layer in the frame is a
  0.3 mm slot that will not print open (frame recheck item 3), so a full ridge would bottom there.
- **Washer:** Ø7 × 0.5 under the M3 × 45's head (BUILD_GUIDE §1 and §4 step 9).

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, one watertight solid, min Z 0 | PASS | 39.85 × 57.5 × 64.0 mm, 1 solid as printed and as fitted, watertight (geometry.json, cad_checks) |
| 2 | Orientation, load paths vs layers | PASS | Unchanged (standing on its −y end, G +y up). The ridge is a vertical prism in print: its cross-section lies in the layer plane, so its flank bearing and root shear and bending are in-plane (strength.md rows 41–44) |
| 3 | Overhangs ≤ 45°, bridges | PASS | The ridge's lead-in continues the post's 45° underside (y + z ≥ 41.85). **Layer check of part.stl** (0.2 mm layers at mid-height, 0.02 mm raster, print z 50–64 over x 13–39.9 and G z 16.5–40; new material beyond the layer below grown 0.5 mm): **no new island**. The ridge grows 0.20–0.22 mm per 0.2 mm layer over print z 56.1–56.7, then stops. mesh_check: overhang 0.26 %, bed contact 703.6 mm², widest bridge 2.0 mm, as round 4. The round-4 whole-part findings (pillars A/B, slot A apex, pass-through apex) are unchanged: the rest of the part is untouched |
| 4 | Walls and features | PASS | The ridge: 1.6 at its base, 0.6 tall, 0.4 flat tip; its tip is rounded by the nozzle, which only adds clearance. Anchor hole edge to the ridge's base 0.5 (cad_checks). The post's 2.2 mm walls round the hole are unchanged. `thin_wall_warnings: []` |
| 5 | HOLE_COMP; horizontal holes | PASS | Unchanged: 3 × Ø3.6 (2 top + the anchor, now z 17.85–51.5), 2 × Ø3.0, Ø22.8, all teardrops (measure_holes, 270°) |
| 6 | Fasteners per §4 | PASS | **Round 4's item 11 is fixed.** The post's foot is held in x by the ridge in the frame's groove; the M3 × 45 holds the flank's 45° lift in tension. No preload or friction is relied on, and a Ø7 × 0.5 washer spreads the head's clamp on the PETG top wall (strength: 4.80 sustained, was 2.34) |
| 7 | Spec §3 dims are named parameters | PASS | `TIE2_FOOT_Z`, `RIDGE_APEX_Z`, `RIDGE_TIP_Z` (model.py) and `VSEAT_*`, `ANCHOR_WASHER` (claw_frame.py); the brief's critical-dimensions table has the row "V-ridge under the post's foot" |
| 8 | cad_checks | PASS | 22/22 (exit 0), with new checks for the ridge (flanks ±0.05 at z 17.3 / 17.55 / 17.8, y 24.8 / 28 / 31.9; tip; lead-in), its fit in the frame's groove (0 mm³ overlap, 0.0707 mm normal gap per flank), the raised flats and underside, and the anchor hole's distance to the ridge |
| 9 | Post against the racks over the stroke | PASS | The post (x ≤ 22.35, with the ridge) against jaw A, jaw B and the pinion, gaps 0–44 every 1 mm, exact solids: **0.25 mm**, as round 4 (≥ 0.2 required). The post's underside is 2.6 over the claw servo's case at y 5.9 (2.5 before) |
| 10 | Anchor hardware clearance | PASS | Washer + head (Ø7 × 0.5 + Ø5.5 × 3, 0.5 higher than round 4's bare head): jaws over the stroke 3.16 (3.47 before), camera mount 3.91 (4.66), Brio 13.97 (14.25) |
| 11 | Assembly sequence | PASS | `claw_sequence_check.py` re-run with the round-5 cover and frame: `ok`, 0 mm³ on every insertion path (the cover lowered 57 positions, its ridge entering the groove), the swept pinion, the stroke 0–44 every 1 mm and one tooth pitch in 0.1 mm steps |

**Required fixes:** none.

**Notes (not blocking)**
1. **Play at the ridge** is the design's one sensitive point (strength.md: play 0.04 mm → 3.41, 0.05 → 2.83). The frame's
   bulkhead top (z 48.5) lies exactly on a slice plane, so it can print 0.1 high or low and move the cover against the
   groove by as much. BUILD_GUIDE §4 step 9's two feeler checks (0.1 at the top wall, 0.15 under the foot's flats) catch
   either before any screw goes in. If the second fails, set `VSEAT_CLR` to 0 in claw_frame.py.
2. **Re-slice.** The slice files in this folder are older than round 2.

---

# DFM review (round 4, history): 20261026-arm-claw-cover

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26 · fourth design attempt, user-approved

**Why it reopened.**
- Round 3 failed twice:
  - **DFM:** support pillar B carried only half of piece (b)'s first layer. 4.24 mm² lay up to 1.13 mm from it.
  - **Strength:** 1.23, from the reversed rack-B push leaving through the 3 mm top wall.
- The user approved both fixes (log.md 16:09). Round 4 (fa56765, model.py) makes three changes:
  - `SUP_B = (-8.0, CRESCENT_Y, ZB1 + 0.2, ZB1 + 1.8)` (model.py:71). The pillar is 1.6 thick, z 16.45–18.05, from y −8.
  - The second tie's post is 8 thick (`TIE2_POST_T` 8, x 14.35–22.35) and stands on the frame's rail block
    (`TIE2_FOOT_Z` 17.75) (model.py:75–76, 148–151).
  - A Ø3.6 teardrop hole at `ANCHOR_XY` (18.35, 28) runs through the top wall, the lip and the post for one M3 × 45 into
    the frame's pilot (model.py:210–212).

**Inputs**
- This job: spec.md (§1 round-4 line, §8), design_brief.md (round 4), model.py, cad_checks.py, geometry.json,
  mesh_check.json, log.md, and the round-3 design_review.md and strength.md.
- Shared: claw_frame.py; claw_sequence_check.json (round 4); BUILD_GUIDE §1 and §4 step 9.
- Renders: all 5, regenerated and viewed.
- Skills: fdm-design-rules (§2 and §4), material-selection. library/ has no lessons and no material rows.

**Extra evidence (mine)**
- **Layer check of part.stl.** 0.2 mm layers on a 0.04 mm raster, in both slicing phases (layer tops at 0.2k, and offset
  0.1).
  - Each layer is compared with the layer below **grown by 0.5 mm**. New islands are counted.
  - A second pass takes support as the union of the 3 layers below. That counts each pillar's top across its 0.25 gap.
- **Clearances on exact solids** with `claw_sequence_check`'s placements: the post, the M3 × 45 (Ø3 shank, Ø5.5 × 3 head)
  and a 2.5 mm hex key against the jaws at gaps 0–44 (every 2 mm), the pinion, the claw servo with its lead, the camera
  mount and the Brio (`assembly_check.brio_with_plug`, as placed).
- **Sections of `design()`** at the post and round the anchor hole.

**Outputs are current.**
- `design()` gives 32 795.6 mm³; as printed with the pillars, 32 943.56 mm³ (geometry.json): 1 solid, 39.85 × 57.5 × 64.
- measure_holes: 3 × Ø3.6 (2 top + the anchor), 2 × Ø3.0, Ø22.8.
- `tools/mesh_check.py` re-run gives exactly the committed mesh_check.json.
- `cad_checks.py` re-run: 20/20 PASS, including pillar B's extent and its coverage of piece (b) within 0.3 in z.

Print frame: (X, Y, Z) = claw G (x, −z, y + 32), so G +y is up.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits the bed with a 5 mm margin | PASS | 39.85 × 57.5 × 64.0 mm, `fits_bed: true` |
| 2 | Single watertight solid, min Z = 0 | PASS | 1 solid as printed and as fitted (cad_checks), watertight, `min_z_mm: 0.0` |
| 3 | Orientation matches the brief | PASS | Standing on its −y end (`TO_PRINT`). **front.png** looks at the top wall's outer face: two top holes and the new anchor hole near the top, each a teardrop pointing up. **right.png** shows the two pillars inside the pass-through. **iso.png** shows the post as the thick column at the top-right end |
| 4 | Load paths vs layers | PASS | The post, lip and webs are loaded in the side profile, along the layers. The anchor's seat and clamp run along G z, which is horizontal in print: compression of the post (2.79 MPa round the hole) and of the top wall under the head. The anchor's x hold is item 11 |
| 5 | Bed contact | PASS | 703.6 mm² on a 64 mm-tall part, with `min.brim_width` 5 (print_requirements.json) |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | **Round-3 fix 1 is done: no piece's first layer starts unsupported beyond 0.5 mm.** The 0.5 mm layer check over the whole part finds only two new islands, pieces (a) and (b) on their pillars. Nothing else starts in mid-air: the 8 mm post grows from the lip at exactly 45°, and the anchor teardrop and the post's foot add no patch.<br>**Piece (b) on pillar B** (z 39.0–39.2, G y 7.0–7.2): its first layer spans G z 16.28…18.32 over the pillar's 16.45…18.05, so the edges are 0.17 below and 0.27 above. Along x the pillar is 0.5 in from each plate face (x 35.35–39.35 under 34.85–39.85). Every edge is ≤ 0.5 from the pillar. Only the four outer corners reach 0.54–0.57 diagonally: ≤ 0.14 mm² per layer, which is a raster artefact plus the corner of two in-limit edges. Round 3 had 4.24 mm² up to 1.13 mm. The offset slicing phase (39.0) gives the same: ≤ 0.56.<br>**Piece (a) on pillar A**, unchanged: 0.18 / 0.15 in z, 0.5 in x, corners ≤ 0.54 (0.57 in the offset phase, round 3's R1).<br>**Other patches** are r 1.5 / r 2 roundings closing over two-sided spans: slot A's apex at z 43.1 (0.60 mm², ≤ 0.56), the pass-through apex at z 47.5 (2.6 mm², ≤ 0.76, a 1.5 mm two-sided bridge), and the end of the corner fillet at z 41.1 (0.02 mm²). mesh_check: 0.26 % overhang, widest bridge 2.0 mm |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | **Post:** 8 thick; 2.20 from the anchor hole to either x face (probed at z 25, 40 and 50). The teardrop's point is 1.50 from the +y end (probed; the brief says 1.45). That side carries no load (it faces the cover's free end, and the shank bears towards −x), and it is ≥ 0.9. **Post below the web:** 8 × 9.26 at z 19, 63.1 mm² net of the hole. **Pillar B:** 1.6 × 4, breakaway by design. Front plate 5, top wall 3, lip 8, strip under slot B 11.75. `thin_wall_warnings: []` |
| 8 | HOLE_COMP; horizontal holes teardrop or flat-top | PASS | Anchor: `M3_CLEAR + HOLE_COMP` = Ø3.6 (model.py:211), a teardrop pointing +y (up in print), like the top holes. measure_holes lists it at a 270° arc |
| 9 | Bottom edges chamfered | PASS | 0.3 mm bed chamfer on the −y end, the openings cut before it. The pillars don't reach the bed |
| 10 | Internal corners on load paths | PASS | The post meets the web and the lip in sharp corners. Strength takes Kt 2.5 at the post's root under the lip and at its foot under the web |
| 11 | Fasteners follow fdm-design-rules §4 | **FAIL** | §4: *"Plastic creeps under clamping load. Use washers or wide heads, and do not count on bolt preload lasting in PLA or PETG."* The anchor breaks both parts of this:<br>• **It holds the post's foot in x only by the preload's friction.** The shank sits in a Ø3.4 printed hole (Ø3.6 CAD), with 0.2 mm radial clearance (up to 0.4 with position error). Without friction the foot slides 3.6–5.0 µm per N of push (strength.md), so the shank would only bear at 40–56 N. That is beyond the 27 N opening stall and the 34 N proof push. To hold the stall, the seat needs ≥ 94 N of clamp left at μ 0.3, or ≥ 136 N at μ 0.2, out of a "snug only" 150 N. Once the preload creeps, the cover is back on round 3's load path: SF 1.37 (strength.md).<br>• **The socket head (dk 5.5) bears straight on the PETG top wall:** 10.7 MPa at 150 N, sustained SF 2.34. BUILD_GUIDE §1 lists no washer for it, though it puts one under every other clamped M3 head in the arm (the tab screws, the ring tabs) for exactly this creep |
| 12 | Spec §3 dims are named parameters | PASS | `SUP_B`, `TIE2_POST_T` 8, `TIE2_FOOT_Z` 17.75 (model.py:71, 75–76), and `ANCHOR_XY` from claw_frame.py:135, each with its source. Spec §1 records round 4 |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ |

**The post against the racks over the stroke** (exact solids, gaps 0–44 every 2 mm):
- **Post to jaw A and jaw B:** ≥ **0.24 mm**. My post solid includes the 0.01 overlap into the web at x 22.36, so the
  real gap is 0.25: the x gap between the post's front face (22.35) and both racks' backs (22.6). The claim of 0.25 holds.
- **Post to the pinion:** 0.25 likewise.
- **Post to the claw servo and its lead:** ≥ 1.77 mm. Its 45° underside is 2.5 over the case at y 5.9.
- **The anchor:**
  - shank to the jaws: ≥ 2.75;
  - head to jaw A: ≥ 3.47;
  - head to the camera mount: 4.66;
  - shank to the claw servo: 16.9.
- **Overlaps:** the shank overlaps the cover by 0.000 mm³, the post overlaps the frame by 0.000 mm³, and the shank
  overlaps the frame by 15.11 mm³, which is exactly the thread annulus over 11.25 mm.
- claw_sequence_check.json (round 4) is `ok`, with 0 mm³ on every path and over the stroke.

**The anchor screw can be reached.**
- A straight 2.5 mm key stays clear of the camera mount (5.96 mm) at any height. It clears the Brio for the first 20 mm
  above the head (4.15 mm), but meets it higher up.
- An L-key works with the Brio fitted: short leg in the socket, long leg turned towards +x or +y at z 69.5. It clears
  the Brio by 6.5 / 5.3 mm and the mount by 15.8.
- BUILD_GUIDE §4 step 9 (drive it before the camera, from directly above) is right, and servicing it with the camera on
  is possible with an L-key.

## Required fixes

1. **Hold the post's foot in x by geometry, not by preload friction, and put a washer under the anchor's head (item 11).**
   - **Change (cover, model.py):**
     - Add a 90° V-ridge along y under the post's foot: centre x 15.25, flanks at 45°, the virtual apex at z 16.95, the
       tip truncated 0.15 (tip at z 17.10).
     - It runs y 24 → 32, with a 45° lead-in over y 24–24.8 that continues the post's underside.
     - Raise the foot's flats 0.1: `TIE2_FOOT_Z` 17.75 → 17.85. The flanks then seat and the flats don't.
     - The ridge is a prism standing vertically in print, so it needs no support. Its base is x 14.35–16.15, within the
       post. The anchor hole (Ø3.6, edge at x 16.55) is unchanged.
   - **Change (frame, model.py):**
     - Add a matching 90° V-groove along y in the rail block's top: x 14.45–16.05 at z 17.75, 0.8 deep (bottom z 16.95),
       y 23.5 → 32, open at the +y end.
     - It opens upward in print. It leaves 0.95 mm of block to the anchor pilot at the top, widening downward.
     - The pilot and the M3 × 45 don't change.
   - **Change (hardware, BUILD_GUIDE §1 and §4 step 9):** an M3 washer Ø7 × 0.5 (ISO 7089, as on the tab screws) under
     the anchor's head. The seat check becomes "the ridge sits in the groove with the top wall on the bulkhead: a 0.1
     feeler must not enter at the top wall".
   - **What it gives** (strength.md what-if):
     - The +x push rides up a 45° flank, and the screw holds that in tension. That hold is positive, with no friction or
       preload needed.
     - Every cover row ≥ 4.64. Flank bearing 4.5. Ridge root 3.7. The frame's block in front of the groove 6.4.
     - M3 pull-out: 4.22 on the preload (10.75 engaged), 3.41 with the wedge's lift.
     - Head on the washer: 4.80.
   - **Why not a smaller change:**
     - A tighter hole at the foot needs ≤ 0.04 mm radial clearance (0.05 gives 2.82), which a printed hole can't promise.
     - A thread formed in the post's foot would take the hoop stress across the layers: about 2.2 at installation.
     - A washer alone leaves the hold on friction.
   - **Rule:** fdm-design-rules §4.
   - **Evidence:** item 11; strength.md rows 29, 8 and 107; spec §8 proof row 110 (1.08).
   - **Then:**
     - update cad_checks (the ridge, the groove, the raised flats);
     - re-run claw_sequence_check (the post now drops 0.8 lower in its last 0.8 of travel, inside the groove);
     - re-run my 0.5 mm layer check (the ridge's lead-in);
     - re-review both parts.

## Notes (not blocking)

1. **The 1.25 mm ligament** between the +y front-screw hole and slot B (round 3 R2) is unchanged. It stays in strength's
   slot-B strip check.
2. **Re-slice.** The slice files in this folder are older than round 2.

## Round 3 → round 4

| Round-3 item | Status | Evidence |
|---|---|---|
| DFM fix 1: pillar B under piece (b)'s whole first layer | **Done** | Item 6: 0.17 / 0.27 in z, 0.5 in x; corners ≤ 0.57 (round 3: up to 1.13 mm, 4.24 mm²) |
| R1: pillar A's gap | Unchanged; still within 0.5 (corners 0.57) | Item 6, both slicing phases |
| Strength round 3: 1.23 (top wall behind the lip) | Anchor built as asked, **but held only by preload friction** | Item 11; strength.md |
| Post clear of the racks over the stroke | 0.25 mm | Above |
| Anchor reachable | Yes | Above |

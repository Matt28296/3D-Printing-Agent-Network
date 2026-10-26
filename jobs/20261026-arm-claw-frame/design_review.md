VERDICT: PASS

# DFM recheck (round 5): 20261026-arm-claw-frame

cad-engineer, 2026-10-26: the checks run on the round-5 geometry (the cover's V-seat fix, user-approved). **This is the
designer's own recheck, not an independent review**; the round-4 independent review follows unchanged below.

**Change.** A 90° V-groove, 0.8 deep, along y in the rail block's top, for the cover's ridge (model.py `_groove()`):
- x 14.45–16.05 at z 17.75, bottom z 16.95 on x 15.25, y 23.5–32, open through the block's +y end;
- numbers shared through `VSEAT_*` in claw_frame.py;
- the anchor pilot (Ø2.7 × 14 at (18.35, 28)) unchanged; 0.95 mm of block between it and the groove at the top.

The round-4 review's note 1 gave the groove as x 14.35–15.95 (1.05 to the pilot). The approved fix (cover review and
strength.md) is x 14.45–16.05, which keeps the cover's ridge 0.1 inside its post's back face; that is what was built.

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, one watertight solid, min Z 0 | PASS | 42.85 × 64.0 × 48.5 mm, 1 solid, watertight, `fits_bed: true` (geometry.json); 46391.78 mm³ (−5.4) |
| 2 | Orientation, load paths vs layers | PASS | Unchanged (back face on the bed). The groove's flank takes the cover's +x push: bearing on the layer edges, and the block in front of it shears along the layer plane of the groove's bottom (interlayer). Both are rows in strength.md: 3.61 and 6.66 |
| 3 | Overhangs, bridges | PASS | The groove opens upward in print: both flanks face up at 45°, so no overhang and no bridge. mesh_check: overhang 1.4 %, widest bridge 7.9 mm, the same as round 4. Sections of part.stl at the layers' mid-heights: the groove is 0.3 / 0.7 / 1.1 / 1.5 mm wide at z 17.1 / 17.3 / 17.5 / 17.7. **The 0.3 mm slot of its first layer will not print open,** so the printed bottom is about z 17.2. Kept as designed: a flat floor wide enough to print would push the mouth past the cover post's back face or under the 0.9 mm minimum wall to the pilot. The cover's ridge is cut flat at z 17.25 to stay above it (cover brief, round 5) |
| 4 | Walls ≥ 1.8, none < 0.9 | PASS | Groove to anchor pilot: 0.95 at the block top (x 16.05–17.0), +1 mm per mm downward (cad_checks). It carries no hoop load of its own (the pilot's 2.65 walls are on its other sides); strength takes the push on the screw as a bound (shank bearing 16.7). `thin_wall_warnings: []` |
| 5 | HOLE_COMP; holes | PASS | Unchanged: clamp Ø2.6, 3 × Ø2.7 pilots, 2 × Ø2.2 flat-topped front pilots (measure_holes) |
| 6 | Bottom edges chamfered | PASS | Unchanged, 0.4 mm |
| 7 | Fasteners per §4 | PASS | The cover's x hold is now geometric (ridge in groove); the M3 × 45 holds the flank's lift in tension, with a Ø7 × 0.5 washer under its head. 10.75 engaged in the 14 mm pilot. No preload is relied on |
| 8 | Spec §3 dims are named parameters | PASS | `VSEAT_D`, `VSEAT_XC`, `VSEAT_Y0`, `VSEAT_CLR` (claw_frame.py), `GROOVE_Y` (model.py); the brief's critical-dimensions table has the row "V-groove (round 5)" |
| 9 | cad_checks | PASS | 21/21 (exit 0), with two new checks: the groove (flanks ±0.05 at z 17.1 / 17.4 / 17.7, y 23.6 / 28 / 31.9; bottom; closed −y end; open +y end) and the 0.95 mm wall to the pilot |
| 10 | Assembly | PASS | `claw_sequence_check.py` re-run: `ok`, 0 mm³ on every path, the stroke and the fine pitch. Cover ridge in this groove: 0 mm³ overlap, 0.0707 mm normal gap per flank (cover cad_checks) |

**Required fixes:** none.

---

# DFM review (round 4, history): 20261026-arm-claw-frame

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26 · fourth design attempt, user-approved

**Why it reopened.** The cover's strength round 3 failed at 1.23, and the user approved its anchor fix (log.md 16:09).
For this frame the fix is one change: a **Ø2.7 CAD (Ø2.5 printed) × 14 M3 pilot**.
- It sits in the rail block's top at `ANCHOR_XY` (18.35, 28), from claw_frame.py:135.
- It runs vertically from z 17.75 to 3.75 (model.py:154–157).
- It takes the cover's M3 × 45 anchor: 11.25 mm engaged.

**Inputs**
- This job: spec.md, design_brief.md (round 4), model.py, cad_checks.py, geometry.json, mesh_check.json, log.md, and the
  round-3 design_review.md.
- Shared: claw_frame.py; BUILD_GUIDE §1 and §4 step 9.
- Renders: all 5, regenerated with `tools/render.py` and viewed.
- **Layer check of part.stl.** 0.2 mm layers on a 0.04 mm raster. Each layer is compared with the layer below grown
  by **0.5 mm**, and any island that touches nothing below is reported.
- Skills: fdm-design-rules, material-selection. library/lessons.md has no entries.

**Outputs are current.**
- `design()` in memory gives 46397.2 mm³, matching geometry.json (46397.22 mm³, 42.85 × 64 × 48.5, 1 solid).
- measure_holes now lists a third Ø2.7: the anchor pilot at (18.35, 28), arc 355°, vertical.
- `tools/mesh_check.py` re-run gives exactly the committed mesh_check.json.
- `cad_checks.py` re-run: 19/19 PASS. Among them:
  - the pilot's Ø2.7 at (18.35, 28), z 3.75–17.75;
  - 2.65 mm of block to the front face (x 22.35) and to the +y end (y 32);
  - solid between it and the +y front M2.5 pilot.
- The volume is −80 mm³ on round 3: the pilot.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 42.85 × 64.0 × 48.5 mm, `fits_bed: true` |
| 2 | One watertight solid, min Z 0 | PASS | `solids: 1`, watertight, `min_z_mm: 0.0` |
| 3 | Orientation matches the brief | PASS | Back face on the bed (bottom.png). top.png shows the new pilot as a round hole in the rail block's top, near its +y end, between the block's front face and the bulkhead; iso.png shows its mouth on the block top. Everything else is as in round 3 |
| 4 | Load paths vs layers | PASS | **The pilot's walls:** hoop stress round a vertical hole in a flat print runs along the layers. **Pull-out** shears the thread cylinder across the layers. **The block's root** loses the pilot from its section. All three are rows in strength.md: block root with the pilot 5.93; pull-out 4.42 on the preload; forming hoop 3.77 |
| 5 | Bed contact | PASS | 2534.7 mm², unchanged; the pilot stops 3.75 above the bed |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | `overhang_pct` 1.4, the same 210.9 mm² as round 3. The pilot is vertical in print and opens upward: no overhang, no bridge. **Layer check, 0.5 mm, whole part:** no new island. Only round 3's four accepted patches remain: the pocket ceiling at z 2.1 (7.9 mm bridge, ≤ 3.74 from support); the front pilots' flats at z 4.1 (0.91 between 45° flanks, ≤ 0.64); the pilot slots' flats at z 28.1 (≤ 0.56); the window-roof flat at z 40.7 (two-sided, ≤ 4.80). Nothing appears near z 3.75 or 17.75 at (18.35, 28) |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (user-accepted deviation unchanged) | **Round the anchor pilot,** probed at z 6, 12 and 17 on `design()`: 2.65 to the block's front face (2.78 at z 6, where the plate is under it), 2.65 to the +y end, 7.5 behind it (towards the bulkhead), 6.65 towards −y. The floor under it is 3.75. **To the +y front M2.5 pilot** (x 20.85–34.85, y 22.9–25.1, z ≤ 4.1): 2.48 mm centre-line distance minus radii, solid between (cad_checks). **The MG90S tab-pilot strips** (1.34 / 1.45) are unchanged: the user accepted them on 26 Oct 2026, with the spec §8 first-print check. `thin_wall_warnings: []` |
| 8 | HOLE_COMP; horizontal holes | PASS | `d = M3_PILOT + HOLE_COMP` = 2.7 (model.py:154), the same as the two top pilots. Vertical, so it is a plain round hole. The other holes are unchanged: clamp Ø2.6, 2 × top Ø2.7, front pilots Ø2.2 as flat-topped teardrops |
| 9 | Bottom edges chamfered | PASS | 0.4 mm `chamfer_plane_edges` on the plate (bottom.png), unchanged |
| 10 | Internal corners on load paths | PASS | Unchanged from round 3: the r 1.5 pad / bulkhead fillet, the Ø3 window reliefs, and the sharp rack-side block root (Kt 2.5 in strength). The pilot crosses the root plane (z 6) 2.65 from the rack-side face; strength takes it out of that section (5.93) |
| 11 | Fasteners per §4 | PASS (see the cover's report) | **On this part:** an M3 self-tapper into a Ø2.5 printed pilot, 11.25 engaged in a 14 mm pilot. The tip stops at z 6.5, 2.75 above the floor. This follows §4 for a joint assembled a few times. **The joint as a whole** relies on the screw's preload friction, which the cover's review fails under §4. The frame's own rows pass either way (strength.md) |
| 12 | Spec §3 dims are named parameters | PASS | `ANCHOR_XY` and `ANCHOR_PILOT_DEPTH` (claw_frame.py:135–136), with source comments, are shared with the cover. The brief's critical-dimensions table has the row "Cover anchor M3 pilot". Spec §1 records round 4 |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ |

**Assembly.**
- `claw_sequence_check.json` (round 4, run_s 1009) is `ok`. Every insertion path, the swept pinion and the stroke give
  0 mm³.
- My own measurement on the exact solids: the M3 × 45 shank (Ø3, z 6.5–51.5) overlaps the frame by 15.11 mm³. That is
  exactly the thread annulus (Ø3 against Ø2.7) over 11.25 mm. It does not touch the cover (Ø3 in Ø3.6) or the claw servo
  (16.9 mm away).

## Required fixes

None for this part as built.

## Notes (not blocking)

1. **The cover's required fix touches this part.** The cover's review fails its anchor because it holds the post only by
   preload friction (fdm-design-rules §4). The fix it gives adds to this frame's rail block:
   - a 90° V-groove, 0.8 deep, along y, at x 14.35–15.95, y 23.5–32, open at the +y end;
   - the anchor pilot does not change;
   - 1.05 mm of block stays between the groove's edge and the pilot at the top, widening downward.

   Re-review this part with that change.
2. **Spec §8 wording** (Architect; round 3's strength R-note is still open): "the rail wall's root (along it and at its
   ends)" should read "the rail block's rack-side root (along it and at its +y end)". Add "the anchor pilot".
3. **Re-slice.** The slice files in this folder are older than round 3.

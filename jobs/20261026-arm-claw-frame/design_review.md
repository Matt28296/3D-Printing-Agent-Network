VERDICT: PASS

# DFM recheck (round 7, CAD engineer's self-check): 20261026-arm-claw-frame

cad-engineer · 2026-10-26 · round 7: the round 6 independent reviews' fix (the cover's screws), user-approved. **This is
the designer's own recheck, not an independent review; an independent review follows.** The round 6 independent review
is kept below as history.

**Strength (self-check): NEEDS_TEST** (strength.md). Every verdict row passes. The lowest against its requirement is row
42: the cover's top M3 × 14 + washer pulling out of the bulkhead at its snug preload, **4.02** with the worst standing
left at the screw (4.12 with the wall pulled down; round 6's bare M3 × 10: 2.73).

**Change.**
- claw_frame.py: `FRONT_SCREWS` z 3 → **2.5** (`FRONT_SCREW_Z`), so the cover's new Ø6 × 0.5 washers under the M2.5
  heads clear jaw B's neck. `TOP_WASHER` and `FRONT_WASHER` are new (hardware only).
- model.py: no edit to the geometry code. The two flat-topped Ø2.2 front pilots follow `FRONT_SCREWS` to z 2.5. Their
  flat top is now at z 3.6: **2.4** to rack B's track (z 6; it was 1.9) and **1.4** to the back face (z 0). They are still
  14 deep (x 20.85–34.85). The top M3 pilots are unchanged: Ø2.7 CAD, 14 deep, floor 34.45. Comments updated.
- Hardware: the cover's top screws are M3 × 14 pan head + Ø7 × 0.5 washer (was a bare M3 × 10). The front screws are
  M2.5 × 16 + Ø6 × 0.5 washer, 10.5 engaged (was 11).

**Run here:**
- `tools/cad_build.py`: 46 365.18 mm³, the same as round 6 (the pilots only moved).
- `render.py`, `mesh_check.py`: overhang 1.4 %, widest bridge 7.9 mm, the front pilots' flat tops now bridge 0.91 at z
  3.6, no thin walls.
- `cad_checks.py`: 24/24, exit 0. New: the front pilots at z 2.5 with their skins and depth. The anchor-pilot probe now
  also covers the space between it and the +y front pilot.
- A scratch probe of the bulkhead round each top pilot (x 3.5–10, y ±3.25), over the screw's path (z 38.0–48.45) and the
  whole pilot (34.45–48.45): the frame volume equals the box less the Ø2.7 pilot exactly, so nothing else is in the
  screw's path. Under the floor (z 33.45–34.4) it is solid.
- `claw_sequence_check.py`: `ok`. Exact-solid clearances, gaps 0–44 every 1 mm. `strength_calc.py`.

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, one watertight solid, min Z 0 | PASS | 42.85 × 64.0 × 48.45, 1 solid, `fits_bed` |
| 2 | Orientation | PASS | Back face on the bed, unchanged |
| 3 | Overhangs, bridges | PASS | mesh_check: 1.4 %, widest bridge 7.9 mm (the window roof); the front pilots' flat tops 0.91 wide at z 3.6 (were at 4.1) |
| 4 | Mating datum off the slice planes | PASS | Bulkhead top 48.45, unchanged (cad_checks: 0.05 to the nearest plane) |
| 5 | Front M2.5 pilots: walls and edges | PASS | z 2.5, Ø2.2 flat-topped at 3.6: 2.4 skin under rack B's track (frame strength row 22, SF 32), 1.4 to the back face, which is clear of the 0.4 bed chamfer. Clear of the anchor pilot: the front pilot reaches z 3.6 and x ≥ 20.85, the anchor pilot starts at z 3.75 and reaches x ≤ 19.7 |
| 6 | Top M3 pilots for the M3 × 14 | PASS | 14.0 deep below BULK_TOP (floor 34.45; printed 14.0 deep, floor 34.4, per the round 6 slice). The M3 × 14 + 0.5 washer under a 3 mm top wall ends at z 38.0: 3.55 above the floor. 10.45 engaged in CAD, 10.5 below the printed bulkhead. Nothing but the pilot in the screw's path (probe above) |
| 7 | Fasteners per §4 | PASS | The pilots take the screws they are sized for. Snug-preload pull-out: M3 × 14 4.02 (worst standing) / 4.12 (pulled down), M2.5 5.15; under the stall the M2.5 at z 2.5 takes 130 N: 3.96 (req 3). Camera case (M3 × 18): 4.41 bare; 4.22 if the proposed Ø7 washer goes under its button heads (see the cover's review, item 7b) |
| 8 | Named parameters | PASS | `FRONT_SCREW_Z`, `FRONT_SCREWS`, `TOP_WASHER`, `FRONT_WASHER` (claw_frame.py); `TOP_PILOT_DEPTH`, `FRONT_PILOT_DEPTH` (model.py) |
| 9 | Rack clearance (rail block) | PASS | Exact solids, gaps 0–44: the rail block is 0.250 from jaw B (unchanged) |
| 10 | Assembly sequence | PASS | `claw_sequence_check.py`: `ok` |

## Spec text that needs to change (Architect)

**§2, interfaces:** "2 × Ø2.2 flat-topped teardrop M2.5 pilots 10 deep in the wrist plate's front edge at (y ±24, z 3)"
becomes:

> 2 × Ø2.2 flat-topped teardrop M2.5 pilots 14 deep in the wrist plate's front edge at (y ±24, z 2.5) (flat top z 3.6:
> 2.4 below rack B's track)

**§2, "Fasteners used":** replace "cover: 2 × M3 × 10 (or 2 × M3 × 18 button heads through the camera mount) into the top
pilots, 2 × M2.5 × 12 pan head (head ≤ Ø5) into the front pilots." with:

> cover: 2 × M3 × 14 pan head + Ø7 × 0.5 washers, snug only (or 2 × M3 × 18 button heads through the camera mount) into
> the top pilots, 2 × M2.5 × 16 pan head (head ≤ Ø5) + DIN 125 Ø6 × 0.5 washers, snug only, into the front pilots
> (10.5 mm engaged).

**§8, the first Pass bullet (the anchor ligament, from the round 6 review):** after "the V-groove's flanks and the anchor
pilot's mouth on the block top", add:

> (checked once before the cover is fitted, after the M3 × 45 has been driven into the pilot and backed out to form its
> thread: no split or bulge between the pilot and the groove)

---

# Round 6 independent review (kept as history; its verdict: PASS)

# DFM review (round 6, independent): 20261026-arm-claw-frame

dfm-reviewer + strength-analyst (independent; did not design the part) · 2026-10-26 · round 6 (bulkhead top off the
slice plane), merged at 105aafe. The CAD engineer's round-6 recheck (designer's own) is replaced by this review.

**Strength verdict: FAIL** (strength.md). Lowest SF 2.73: the cover's top M3 × 10 pulling out of this part's bulkhead at
its snug preload. The fix is hardware only (M3 × 14 + Ø7 × 0.5 washer) and changes nothing on this part's geometry, so
DFM passes.

## Inputs and what I re-ran

- **This job:** spec.md, design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json; the git history of
  this file and strength.md.
- **Shared:** claw_frame.py (`BULK_TOP`, `VSEAT_*`, `ANCHOR_*`). The cover's model and review. BUILD_GUIDE §4 step 9.
- **Skills:** fdm-design-rules, prusaslicer-settings, build123d-cad, strength-checks.

**Re-run here:**
- model.py rebuilt: 46 365.18 mm³. The committed part.stl matches it (46 365.53).
- cad_checks.py: exit 0, no FAIL (23 PASS).
- **My own scratch slice** of the committed part.stl with the arm's command (PrusaSlicer 2.7.2, 0.20mm QUALITY @MK3,
  Prusament PETG, slice_overrides.ini; output in the scratchpad). G-code read back with my own parser.
- Exact-solid sections and distances (build123d), and strength_calc.py rewritten for this review.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, one watertight solid, min Z 0 | PASS | 42.85 × 64.0 × 48.45, 1 solid, watertight, `fits_bed` |
| 2 | Orientation, load paths vs layers | PASS | Back face on the bed, unchanged |
| 3 | Overhangs, bridges | PASS | mesh_check: overhang 1.4 %, widest bridge 7.9 mm (the window roof), no thin walls |
| 4 | **Mating datum off the slice planes** | PASS | Bulkhead and rib tops at 48.45, 0.05 from the planes 48.3 / 48.5. G-code: the last layer is `;Z:48.4`, and extrusion over the bulkhead (x 3.6–9.9) at every y and over both ribs ends there. **Printed height 48.4**, now set by design |
| 5 | Rail block top; the groove | PASS | Block top **17.8** (front of the groove, behind it, and at −y). Groove walls at half-widths 0.15 / 0.35 / 0.55 / 0.75 in the layers ending 17.2–17.8, centred on x 15.25 (external perimeters 14.875/15.625 … 14.275/16.225). The flanks face up at 45°: no overhang, no bridge |
| 6 | The groove's 17.0–17.2 layer | PASS (note) | It prints as an **open** 0.3 slot between two external perimeters (bead edges 15.10 / 15.40), not a closed layer. The layer below (17.0) is solid. The cover's tip faces this layer's top (17.2), 0.206 above it nominal, +0.093 at RSS. At the absolute worst stack it bottoms with 0.029 of play, and the strength rows carry that (SF ≥ 4.04 in the cover's frame model) |
| 7 | Walls ≥ 0.9; the ligament to the anchor pilot | PASS (note) | 0.95 CAD at the block top. G-code at y 28: two bonded external perimeters (w 0.52 + 0.48), 1.04 between the groove's edge (15.99) and the pilot's (17.03); 1.10 with the hole at Ø2.5. It widens 1 mm per mm down. Thread forming acts on it once: info row 70, 2.54, with the ruling in strength.md. Make it inspectable (spec text below) |
| 8 | HOLE_COMP; holes | PASS | The anchor pilot and both top pilots print with their external perimeter at r 1.57 (Ø2.7 CAD). The top pilots are 14.0 deep as printed (the last pilot layer is ;Z:34.6). Clamp Ø2.6, 2 × Ø2.2 front pilots, as before |
| 9 | Bottom chamfer | PASS | 0.4 mm, unchanged |
| 10 | Fasteners per §4 | PASS on this part | The pilots take the screws they are sized for. The cover's top screws' engaged length at the snug preload is a strength FAIL (row 42: M3 × 10 has 6.95–7.0 engaged). The fix, an M3 × 14 + washer with 10.5 engaged, fits the 14 mm pilots (tip z 38.0, floor 34.45). The front M2.5 pilots: pull-out on the preload 5.40 |
| 11 | Everything that references the bulkhead top | PASS | The cover's top wall stands 0.156 over the printed bulkhead before the screws (0.06–0.10 after the anchor seats): ridge-first by design (cover review). The top M3s have 7.0 engaged with the wall pulled down, 6.74 if not. `claw_sequence_check` declares `BULK_TOP` as the plane |
| 12 | Named parameters | PASS | `BULK_TOP` (claw_frame.py), `VSEAT_*`, `GROOVE_Y`, `TOP_PILOT_DEPTH` |
| 13 | cad_checks | PASS | Exit 0: the size check (48.45), the bulkhead and rib tops, their distance to the nearest slice plane, the pilots' depth |
| 14 | Rack clearance (rail block) | PASS | Exact solids, gap 0–44: the rail block is 0.250 from jaw B |

**Required fixes on this part:** none. The strength FAIL is fixed in the cover's BOM: 2 × M3 × 14 pan head + 2 × Ø7 ×
0.5 washers for the no-camera build (see the cover's review).

## Notes

1. **If the cover's M2.5 fix (b) is taken**, this part's front pilots move with `FRONT_SCREWS` to z 2.5. The flat-topped
   pilot then keeps 2.4 to rack B's track and 1.4 to the back face. Re-run cad_checks.
2. **Re-slice** for the job: the committed G-code predates rounds 3–6.
3. **The tab-pilot strips** (user-accepted 26 Oct 2026) are unchanged; spec §8 has the screw-strip check.

## Spec text that needs to change

**Frame spec §8**, first Pass bullet. After "the V-groove's flanks and the anchor pilot's mouth on the block top", add:

> (checked once before the cover is fitted, after the M3 × 45 has been driven into the pilot and backed out to form its
> thread: no split or bulge between the pilot and the groove)

**Frame spec §2**, "Fasteners used". Replace "cover: 2 × M3 × 10 (or 2 × M3 × 18 button heads through the camera mount)
into the top pilots" with:

> cover: 2 × M3 × 14 pan head + Ø7 × 0.5 washers, snug only (or 2 × M3 × 18 button heads through the camera mount) into
> the top pilots

Correct the stale "M2.5 × 12" in the same line to M2.5 × 16 (as the BOM).

---

# History

- **Round 6 self-check** (cad-engineer; git 8527ef6 / 105aafe): PASS. It is replaced by this review, which agrees on the
  geometry.
- **Round 5 independent review** (git be24872): FAIL. The bulkhead top lay on the slice plane of layer 48.4–48.6. It
  was fixed in round 6 and is verified above.
- **Round 4** (independent; git a701995): PASS. The anchor pilot was added.

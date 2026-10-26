VERDICT: PASS

# DFM review (round 7, independent): 20261026-arm-claw-frame

dfm-reviewer + strength-analyst (independent; did not design the part) · 2026-10-26 · round 7 (front M2.5 pilots at
z 2.5; the cover's screws on washers), merged at a8ae29c. The CAD engineer's round-7 recheck (designer's own, PASS) is
replaced by this review. The round 6 independent review is kept below as history.

**DFM: PASS. Strength: NEEDS_TEST** (strength.md): every verdict row passes; NEEDS_TEST only because the PETG
allowables are placeholders. Lowest against its requirement: row 42, the cover's top M3 × 14 + washer pulling out of
the bulkhead at its 150 N snug preload with the worst standing left at the screw, **4.02** (req 4). Lowest absolute
verdict SF: 3.17 (row 58, the V-groove's flank under the opening stall, req 3). **No required fix.**

## Inputs and what I re-ran

- **This job:** spec.md, design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json, the self-check's
  files, and the round 6 review (below).
- **Shared:** claw_frame.py (`FRONT_SCREW_Z`, `FRONT_SCREWS`, `TOP_WASHER`, `FRONT_WASHER`), BUILD_GUIDE §1 and §4
  steps 9 and 13, the cover's model and review.
- **Skills:** fdm-design-rules, strength-checks, build123d-cad, prusaslicer-settings.

**Re-run here** (`/home/claude/.venv-cad/bin/python3`):
- model.py rebuilt: 46 365.18 mm³ = geometry.json. The committed part.stl matches it (46 365.53, watertight).
- `cad_checks.py`: 24 PASS, exit 0.
- `tools/mesh_check.py`: overhang 1.4 %, bed contact 2534.7 mm², widest bridge 7.9 (the window roof), no thin walls,
  fits bed. mesh_check.json is unchanged.
- **My own scratch slice** of the committed part.stl with the arm's command (output in the scratchpad as a text file),
  read back with my own parser.
- Exact-solid clearances (with the cover's review) and `strength_calc.py`, rewritten for this review.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, one watertight solid, min Z 0 | PASS | 42.85 × 64.0 × 48.45, 1 solid, `fits_bed` |
| 2 | Orientation | PASS | Back face on the bed, unchanged |
| 3 | Overhangs, bridges | PASS | mesh_check as above |
| 4 | **Moved front M2.5 pilots** (Ø2.2 CAD, flat-topped, y ±24, **z 2.5**, x 20.85–34.85) | PASS | G-code, both pilots, at x 32: layers up to ;Z:1.4 solid (the **1.4 floor skin**, 7 layers), the void opening from the 1.4–1.6 layer, 2.2 wide at mid-height (the CAD circle), and closing at the 3.4–3.6 layer (1.1 wide). The 3.6–3.8 layer is solid across it: the **flat top at 3.6** is a 0.9–1.1 bridge. Above it, 12 solid layers to rack B's track at z 6: the **2.4 skin**. The pilots' mouths are at x 34.85, clear of the 0.4 bed chamfer, which reaches z 0.4 only. Clear of the anchor pilot (≥ 2.4 apart in 3-D; cad_checks probes) |
| 5 | **The two skins under load** | PASS | New strength rows. Thread forming + preload, short-term: floor skin **3.40**, top skin 3.98. Preload alone, sustained: 25.9 / 30.3. The top skin under rack B's separating force: SF 32 (row 22). See strength.md |
| 6 | Top M3 pilots for the M3 × 14 + Ø7 washer | PASS | Unchanged: Ø2.7 CAD, 14 deep, floor 34.45 (printed 34.4). Tip z 37.9–38.0: **3.5** above the floor. With the camera, M3 × 18 + washer: tip 37.4–37.5, 3.0 above it. A js15-long screw (+0.35) keeps ≥ 2.6 |
| 7 | Front M2.5 engagement | PASS | 16 − 0.5 − 5.0 = **10.5** engaged; tip x 24.35, **3.5** inside the floor at x 20.85 |
| 8 | Fasteners per §4 | PASS | The pilots take the screws they are sized for; every screw has a washer on the cover |
| 9 | Named parameters | PASS | `FRONT_SCREW_Z`, `FRONT_SCREWS`, `TOP_WASHER`, `FRONT_WASHER` (claw_frame.py); `TOP_PILOT_DEPTH`, `FRONT_PILOT_DEPTH`, `BED_CHAMFER` (model.py) |
| 10 | Rack clearance (rail block) | PASS | Exact solids, gap 0–44: 0.250 to jaw B. Jaw B to the front washers 0.500, to the heads 1.000. The washer is located by this part's pilot, as jaw B is by this part's plate, so the cover's standing does not reduce it |
| 11 | Mating datum off the slice planes | PASS | Bulkhead top 48.45, unchanged. The last layer is ;Z:48.4 in my slice |

## Rulings on the two rows the brief asked about (strength.md has the detail)

- **Row 42, 4.02: computed correctly; net conservative; passes.**
  - Hand check: 150 / (π × 3 × 10.24) = 1.554 MPa; 6.25 / 1.554 = 4.02.
  - Conservative: it holds the worst standing (0.259) at the screw while the screw carries 150 N. Closing that gap
    takes only 144 N, so at 150 N the wall is down: 10.5 engaged, 4.12. It also takes the interlayer shear allowable
    (6.25) for a thread cylinder that, in this vertical pilot, runs through the layers. With the in-plane 12.5 the row
    is about 7.
  - Lenient, not modelled before:
    - the screw's js15 length tolerance (−0.35): 3.88;
    - about 1 mm of partial thread in a pointed self-tapper's lead: 3.63;
    - both: 3.49 on the interlayer allowable, 6.98 on the in-plane.
  - These are information rows 72–75. The conservative terms outweigh them.
  - Optional margin, hardware only: **M3 × 16 + Ø7 washer**. Engaged 12.24–12.5, SF 4.81–4.91; tip z 35.9–36.0, 1.5
    above the floor (1.15 with a long screw).
- **The M2.5 under the stall: 3.44, not 3.96** (row 44, req 3). It still passes.
  - The bound pivots the cover's lower piece on this part's front face at its lowest point. That point is the top of
    the 0.4 bed chamfer (z 0.4), not z 0.
  - So the screw takes 27.0 × 11.65 / 2.1 = 150 N, not 130 N; pull-out 150 / (π × 2.5 × 10.5) = 1.82 MPa.
  - The bound stays conservative overall: the first tie (y −32…−24) and the other M2.5 are ignored.
  - The self-check's 130 N is info row 81.
- **Camera build:** with the Ø7 washers now in the BOM, the M3 × 18 engagement is 10.95 in CAD and 10.74 with the worst
  standing. The verdict row (43) is **4.22**; the self-check had it on the bare 11.24 (4.41).

## Required fix

None.

## Notes (not blocking)

1. **Spec text (Architect), pre-existing:** §2 still gives the envelope as "40.85 × 64 × 48.5 (… x −8…32.85 …)" and §3
   "Wrist plate front edge x 32.85". The model, cad_checks and claw_frame.py have had x 34.85 (FACE_W 12) since round 3,
   with the bulkhead top at 48.45: 42.85 × 64 × 48.45, x −8…34.85, and the front edge at x 34.85.
2. **BUILD_GUIDE §1** (cover's review): the top-screw row's "(10.5 / 11.5 mm engaged)" should read "(10.5 / 11.0 mm
   engaged)", now that the M3 × 18 has a washer.
3. **Re-slice** for the job: the committed G-code predates rounds 3–7.
4. **The tab-pilot strips** (user-accepted 26 Oct 2026) are unchanged; spec §8 has the screw-strip check.

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

- **Round 7 self-check** (cad-engineer; git 327fd36 / a8ae29c): PASS. It is replaced by this review, which agrees on the geometry (the pilots at z 2.5, the 1.4 / 2.4 skins, read back from a slice here). Its strength rows had the M2.5 stall bound's pivot at z 0 (3.96; 3.44 here) and the camera rows on the bare-head engagement (4.41; 4.22 with the washer now in the BOM), and did not check the 1.4 floor skin under thread forming (3.40 here).

- **Round 6 self-check** (cad-engineer; git 8527ef6 / 105aafe): PASS. It is replaced by this review, which agrees on the
  geometry.
- **Round 5 independent review** (git be24872): FAIL. The bulkhead top lay on the slice plane of layer 48.4–48.6. It
  was fixed in round 6 and is verified above.
- **Round 4** (independent; git a701995): PASS. The anchor pilot was added.

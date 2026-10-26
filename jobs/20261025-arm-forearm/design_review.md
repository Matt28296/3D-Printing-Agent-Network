VERDICT: PASS

# DFM review (round 5): 20261025-arm-forearm

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26 · third design attempt

**Why it reopened.**
- **Round 4 DFM failed** on the MG90S tab-pilot strips: 1.340 / 1.445 mm CAD, under rule §2's 1.8.
- **The user's decision (26 Oct 2026; log.md 11:51):** keep the strips and check them on the first print (spec §8).
- **Links strength round 4 failed** two things (log.md 13:06):
  - the 6.6 × 10 window rails, SF 1.71;
  - the far tab screw's pull-out, SF 2.40.
- **Design round 5:**
  - a 6 mm rib on the back face along each rail;
  - a cross-rib at the window's far end that carries the far pilot 16 deep for an M2 × 16;
  - a 45° run-out towards the elbow (`back_ribs()`, model.py:45–66, 72).

**Inputs**
- This job: spec.md, design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json, slice_plan.json, log.md and the round-4 review.
- Renders: all 5, regenerated with `tools/render.py` and viewed.
- Assembly: BUILD_GUIDE §1 and §4 step 6.
- Clearance: an independent mesh sweep of mine (method below), using the upper link model and `hobby_parts.servo_dummy` / `link_back_z`.
- Skills: fdm-design-rules, material-selection, build123d-cad. library/lessons.md has no entries.

**Outputs are current.**
- `build()` run in memory gives 32833.29 mm³, a 129 × 26 × 16 bbox from (−25, −13, 0) and 1 solid. That matches geometry.json.
- part.stl is watertight.
- `tools/mesh_check.py` re-run gives the committed mesh_check.json.
- The volume is +3598.1 mm³ on round 4 (29235.18), which is the ribs, cross-rib and run-out minus the far pilot's extra 6 mm and the r 7 corner. Nothing else moved.
- `cad_checks.py` re-run: 16/16 PASS.

**Method**
- **Print frame:** front face on the bed, so the plate is at z 0–10 and the ribs at z 10–16. Point-in-solid line scans of part.stl at 0.005 mm steps.
- **Clearance sweep:**
  - The rib solid goes in the elbow frame (`U @ T(L, 0, T + link_back_z) @ Rz(−el)`, as in assembly_check.py), swept over elbow −150…+30° in 5° steps, then in 1° steps round the closest angle.
  - The other bodies are the upper link (with its ribs), the elbow MG996R with its double-arm horn, and the screw heads on the upper link's front face. Those heads are four M3 pan heads Ø5.5 × 2.4 on Ø7 × 0.5 washers, on the 2.5 mm tabs, plus the shoulder clamp's socket head on its Ø9 × 0.8 washer.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 129 × 26 × 16 mm; `fits_bed: true` |
| 2 | One watertight solid, min Z 0 | PASS | `solids: 1`, `watertight: true`, bbox min z 0.0 |
| 3 | Orientation matches the brief | PASS | **The front face prints down; the ribs and cross-rib, on the back face, print on top** (`Rot(180, 0, 0)`, model.py:81). iso.png shows a U of ribs round the window, closed at the far end by the cross-rib and open at the lead end. front.png shows the 45° run-out and the square end at x 101.1. top.png shows the far pilot in the cross-rib's top. bottom.png (bed face) is unchanged |
| 4 | Load paths | PASS | The ribs deepen the rails to 16 mm for out-of-plane bending, along the layers. The far screw's pull-out shears 13.5 mm of pilot wall, across many layers |
| 5 | Bed contact | PASS | 2874.0 mm², the same as round 4. The ribs are at print z 10–16 |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | `overhang_pct` 0.0, `bridges: []`. Everything new stands on the plate: run-outs at 45° facing up (back face at x 60.9, full depth at x 66.9), vertical sides and a flat top at z 16. The far pilot is a vertical hole through the cross-rib, open at the top |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (accepted deviation) | **Holes the change touches.** The scan at y 0, z 13 runs solid 63.9–69.35, then the far pilot's slot, then solid 71.45–72.90, then the window. **Cross-rib wall beyond the slot:** 2.45 at the full-depth top (66.9 → 69.35), more lower down (cad_checks: 2.55). **Rib width:** 6.59 at x 85 (y ±6.405…±12.995); 5.3 at the x 101.1 end. **Cross-rib** at x 69.9: solid full width except the pilot slot. **MG90S screw strips:** 1.45 (far, plate and cross-rib, now 16 deep) and 1.335 (lead end, plate only; z 5 scan x 97.515–98.85). Both are under §2's 1.8, as **the user accepted on 26 Oct 2026** (log.md 11:51), with a first-print screw-strip check (spec §8, BUILD_GUIDE §4 step 6) and strength round 4's strip rows (SF 4.75 / 5.19). Recorded as that deviation, not failed on width. Other walls: lead-end slot to plate end 3.05; rails 6.6; pocket to plate end 4.4. `thin_wall_warnings: []` |
| 8 | HOLE_COMP; horizontal holes | PASS | `HOLE_COMP` goes into both cutters (model.py:73–76). Window 23.2 × 12.8 CAD, now through 16 mm; its far-end wall continues up the cross-rib and its side walls up the ribs. Notch 4.4 × 1.6 CAD. Pilots Ø1.7 CAD (1.5 printed), each slotted 0.4 outward. The far pilot is open through z −7…11 on its axis (cad_checks). No horizontal holes |
| 9 | Bottom edges chamfered | PASS (note) | `chamfer_plane_edges(arm, T, 0.4)` (model.py:71) on the bed face. The hole mouths rely on `elefant_foot_compensation` 0.2 |
| 10 | Internal corners on load paths | PASS (advisory) | Towards the elbow the ribs and cross-rib meet the plate through a 45° run-out, with no step (the brief: SF > 4 even with Kt 2.5 at its foot). At x 101.1 the ribs end in a square 6 mm step, past the last tab row. Window and notch corners are as accepted |
| 11 | Fasteners per §4 | PASS (note) | **Far tab:** M2 × 16, 16 − 2.5 (tab) = 13.5 mm engaged in a 16 mm through-pilot, so it can't bottom out (the strength FIX asked for ≥ 14 of pilot). **Lead-end tab:** M2 × 12, 9.5 into the 10 mm plate, through the filed slit. BUILD_GUIDE §1 lines 69–70 and §4 step 6 give exactly these screws. **Elbow clamp:** M3 × 14 + Ø9 washer, unchanged. Self-tappers in a part assembled once are acceptable (§4). See note 1 for spec §8's wording |
| 12 | Spec §3 dims are named parameters | PASS (note) | `RIB_H` 6, `RIB_PAST` 5, `RIB_X1` 101.1, `BOSS_X0` 66.9, `FAR_SCREW_L` 16, `TAPER` 6 (model.py:46–54), sourced to strength round 4, matching the brief's new "Far tab pilot" and "Rail ribs + cross-rib" rows. Spec §3's MG90S rows (window, notch, strips "kept … by the user's decision") are in the brief with their tolerances, closing round 4 note 2. The 1.3 mm pilot shift is still only the cutter's default (note 2) |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG at ≈ 70 °C. `materials_on_hand` is empty: check the spool |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

**The ribs against the parts around them** (my sweep, elbow −150…+30°). The forearm's back face, which carries the ribs, faces the upper link's front face:
- **Upper link:** ≥ **10.17 mm**, closest at −150° (the folded limit; the 1° steps confirm it). The brief says ≥ 10.2, which is the same to my sampling.
- **Elbow MG996R with its horn:** ≥ 26.7 mm.
- **Screw heads on the upper link's front face:** ≥ 33.4 mm. They sit at r ≤ 34.4 or r = 100 from the elbow axis, and the ribs start at r 60.9.
- **Wrist servo:** the MG90S case stands 8.5 mm out of the back face, 2.5 mm beyond the ribs, so the ribs don't widen the envelope in depth.
- **Wrist servo lead:** it leaves the shaft end 3.4 mm below the back face, on the centre line, between the ribs (open: cad_checks probes x 96.5–101).

## Required fixes

None.

## Notes (not blocking)

1. **Spec §8's screw-strip check names the wrong far screw** (Architect). It says "drive both M2 × 12 tab screws snug". Since round 5 the far tab takes an M2 × 16, 13.5 mm into the 1.45 mm strip, and BUILD_GUIDE §4 step 6 already says so. The check the user's acceptance rests on must use the screws actually fitted. Change it to "drive the M2 × 12 (lead end) and the M2 × 16 (far end) snug".
2. **Pilot shift** (round 4 #12). The lead-end pilot's 1.3 mm move is still the cutter's default `pilot_shift` (hobby_parts.py), not a named parameter here. Spec §2 and the brief do state it. A `PILOT_SHIFT = 1.3` line with its source would make the 26 Oct fallback (move it 1.6) a one-number change.
3. **Elbow horn anti-rotation** (round 4 note 3, still open). The 2 × M2 × 6 bite 1.0 mm of pocket-floor skin, then infill. A solid-infill modifier under the pocket is the slicing-lead's call.

## Round 4 → round 5

| Item | Status | How I checked |
|---|---|---|
| DFM round 4 fixes 1–2: strips 1.340 / 1.445 < 1.8 | Accepted deviation (user, 26 Oct 2026) | #7; spec §8 and BUILD_GUIDE §4 step 6 carry the check (note 1: name the M2 × 16) |
| Round 4 note 1: strength on the real strips | Closed | Strength round 4: 4.75 / 5.19 |
| Round 4 note 2: MG90S rows in the brief | Closed | Brief table |
| Strength round 4: rails (1.71) and far screw (2.40) | Ribs, cross-rib, M2 × 16; printable | #3, #6, #7, #11; clearance ≥ 10.17 |
| Round 4's passing items | Still pass | The volume change is the ribs and cross-rib |

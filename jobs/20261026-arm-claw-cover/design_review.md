VERDICT: PASS

# DFM recheck (round 6, CAD engineer's self-check): 20261026-arm-claw-cover

cad-engineer · 2026-10-26 · round 6 (ridge-first contact), the round 5 review's required fix, user-approved. **This is
the designer's own recheck, not an independent review; an independent review follows.** The round 5 independent review
is kept below as history.

**Change.**
- claw_frame.py: `VSEAT_CLR` 0.1 → **0.0** (ridge apex 16.95); new `BULK_TOP` 48.45 (frame only).
- model.py:
  - `FOOT_CLR` **0.30**, `TIE2_FOOT_Z` = ZS − RAIL_IN + FOOT_CLR = **18.05**, independent of `VSEAT_CLR`;
  - the ridge's 45° flanks run up to the flats: base **x 14.15–16.35**, 2.2 wide, 0.2 behind the post's back face
    and 0.2 to the anchor hole;
  - `RIDGE_TIP_Z` **17.35**, absolute.
- Kept: the groove x 14.45–16.05 (`VSEAT_XC` 15.25), its 90° flanks and 0.8 depth; the Ø7 × 0.5 washer under the
  M3 × 45; the top wall at 48.5.

**Run here:**
- `tools/cad_build.py`, `render.py` and `mesh_check.py`; `cad_checks.py` (26/26, exit 0).
- Exact-solid clearances (scratch script, `claw_sequence_check` placements), gaps 0–44 every 1 mm.
- `claw_sequence_check.py`: `ok`.
- A scratch slice of both round-6 part.stl files with the arm's own command (PrusaSlicer 2.7.2, 0.20mm QUALITY @MK3,
  Prusament PETG, each job's slice_overrides.ini), output to the scratchpad, G-code read back.

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, one watertight solid, min Z 0 | PASS | 39.85 × 57.5 × 64.0, 1 solid as printed and as fitted, watertight, `fits_bed`; 32 890.4 mm³ (round 5: 32 927.7) |
| 2 | Orientation, load paths vs layers | PASS | Unchanged: standing on its −y end (G +y up). The ridge is a vertical prism in print, so its root and flank stresses are in the layer plane |
| 3 | Overhangs ≤ 45°, bridges | PASS | The ridge's lead-in continues the post's 45° underside (y + z ≥ 42.05). mesh_check: overhang 0.26 %, bed contact 703.6 mm², widest bridge 2.0 mm (unchanged) |
| 4 | Ridge printable as drawn | PASS | Read back from the G-code (layers at G y 25.9 / 27.9 / 30.1): the external perimeter runs 0.225 inside both 45° flanks, the tip (17.35, from x 14.94 to 15.56 at the centreline) and the flats (18.05). The ridge, its tip and the flats print to CAD |
| 5 | Walls and thin features | PASS (note) | mesh_check reports **one thin-wall hit, 0.14 mm** at G (14.3, 29.3, 18.1): the 0.2 × 0.2 triangle of ridge the fix asks for behind the post's back face (x 14.15–14.35, z 17.85–18.05). It is not a wall and carries nothing (the groove's −x flank ends at 14.45 at the block top, so this part of the ridge is above the frame). In the G-code the slicer merges it into the post's perimeter (the outline turns from the flank at x 14.53 to the post's face). Anchor hole 0.2 from the ridge's base, 2.2 to the post's faces (cad_checks) |
| 6 | **Fits and tolerances (§3): the V-seat, as printed** | PASS | **Ridge-first by design.** CAD: flanks line to line (0 mm³, distance 0), flats 0.30 over the block, tip 0.15 over the groove's closed first layer, top wall 0.05 over the bulkhead. As printed (slice above + corner rounding r 0.075): the ridge lands on the groove's layer corners 0.056 above its CAD seat, so the top wall stands **0.156** over the printed bulkhead (48.4), the flats 0.306 over the printed block (17.8), the tip 0.206 over the closed first layer. Stack-up (strength.md, reviewer's tolerances): play **0** nominal and RSS, **0.029** worst case, where the top wall lands on the bulkhead and BUILD_GUIDE step 9's 0.03 feeler stops the build |
| 7 | Fasteners per §4 | PASS | The ridge, not friction, holds the foot in x and always takes the anchor's preload on its flanks (seating). Ø7 × 0.5 washer: head bearing 4.80 sustained. M3 × 45 pull-out on the preload 4.12 with the worst-case float (10.49 engaged). Anchor first, snug, then the M2.5 and M3 screws (BUILD_GUIDE §4 step 9) |
| 8 | Spec §3 dims are named parameters | PASS | `FOOT_CLR`, `TIE2_FOOT_Z`, `RIDGE_APEX_Z`, `RIDGE_TIP_Z` (model.py); `VSEAT_*`, `BULK_TOP`, `ANCHOR_WASHER` (claw_frame.py). The flats no longer depend on `VSEAT_CLR`. Spec text changes needed: in the report to the Architect (top wall underside tolerance as assembled; the §8 ridge line) |
| 9 | Rack clearance over the stroke (≥ 0.2) | PASS | Exact solids, gaps 0–44 every 1 mm: second post + ridge against jaw A **0.240** (gap 0) and jaw B 0.312 (gap 1); lip against jaw A 0.250; first tie 0.240 / 1.150; second web 1.150 / 1.150; post + ridge to the pinion 0.240, to the claw servo (with its lead) 1.85 |
| 10 | Washer and head clearance | PASS | Ø7 × 0.5 washer + Ø5.5 × 3 socket head at (18.35, 28) on z 51.5: jaws 3.162 (jaw A, gap 0; jaw B 33.4), camera mount 3.911, Brio with its plug and thumb screw 13.973. Unchanged (the top wall did not move) |
| 11 | Ridge and groove line up | PASS | cad_checks: flanks probed ±0.05 at z 17.4 / 17.7 / 18.0 and y 24.9 / 28 / 31.9, both on x 15.25; the CAD fit 0 mm³, distance 0 |
| 12 | Assembly sequence | PASS | `claw_sequence_check.py` (round 6 cover and frame): `ok`, 0 mm³ on every insertion path (the cover lowered 57 positions, its ridge landing line to line in the groove), the swept pinion, the stroke 0–44 every 1 mm, one tooth pitch in 0.1 mm steps; backlash 0.4 per mesh. The declared contact "top wall on the bulkhead top" now names `BULK_TOP` (0.05 clear in CAD) |

**Required fixes:** none.

**Notes (not blocking)**
1. **Re-slice for the job.** The committed slice files in this folder are older than round 2; the scratch slice above is
   not a job file.
2. **Spec text.** §3's "top wall underside z 48.5 ±0.15" holds on the part, but assembled the top wall stands 0–0.26
   over the printed bulkhead at the +y end (rack A's 0.7 backlash absorbs it); §8's "0.15 mm feeler under the post's
   foot" now checks nothing. The exact replacement text is in the report to the Architect.

---

# History

## DFM review (round 5, independent): 20261026-arm-claw-cover

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26 · round 5 (V-seat), merged at 022af2e. The CAD
engineer's round-5 recheck (designer's own) is replaced by this review.

### Inputs

- **This job:** spec.md, design_brief.md (round 5), model.py, cad_checks.py, geometry.json, mesh_check.json, and git
  history of this file and strength.md (rounds 3–5).
- **Frame:** model.py, design_review.md and strength.md.
- **Shared:** jobs/20261025-robot-arm-assembly/claw_frame.py (`VSEAT_*`, `ANCHOR_*`), BUILD_GUIDE §1 and §4 step 9,
  claw_sequence_check.py helpers.
- **Skills:** fdm-design-rules, prusaslicer-settings, build123d-cad, strength-checks. library/ has no PETG fit data.

**Re-run here:**
- `cad_checks.py` (22/22, exit 0).
- **Exact-solid sections and distances** (build123d, CAD venv):
  - ridge and groove profiles at y 26 and y 30;
  - ridge-to-groove fit;
  - post, lip and ties against both jaws, every 1 mm of gap from 0 to 44;
  - washer + head against the jaws, the camera mount and the Brio (with its USB plug and thumb screw).
- **A scratch slice of this part.stl and the frame's part.stl** with the arm's own command (PrusaSlicer 2.7.2, 0.20mm
  QUALITY @MK3, Prusament PETG, each job's slice_overrides.ini). The G-code was read back at the ridge and the groove.
  (The slice files committed in this folder are older than round 2.)

### Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, one watertight solid, min Z 0 | PASS | 39.85 × 57.5 × 64.0, 1 solid, watertight, `fits_bed` (geometry.json, mesh_check.json); 32 927.7 mm³ |
| 2 | Orientation, load paths vs layers | PASS | Standing on its −y end (G +y up), unchanged. The ridge is a vertical prism in print, so its root and flank stresses are in the layer plane |
| 3 | Overhangs ≤ 45°, bridges | PASS | The ridge's 45° lead-in continues the post's underside. In the G-code the ridge's outline grows about 0.2 mm per layer over print z 56.2–56.8, then holds (path at G z 17.25). mesh_check: overhang 0.26 %, bed contact 703.6 mm², unchanged |
| 4 | Ridge printable as drawn | PASS | Layer z 58 (G y 25.9): the external perimeter follows both 45° flanks 0.225 (±0.01) inside the contour, and turns the 0.4 mm tip on a 0.21 mm segment. The second perimeter fills the root. The ridge prints to CAD; its tip corners round a little, which only adds clearance |
| 5 | Walls and holes | PASS | Anchor hole Ø3.6 teardrop (+y, up in print) at (18.35, 28), its edge 0.5 from the ridge's base; 2.2 to the post's faces. Other holes unchanged (measure_holes) |
| 6 | **Fits and tolerances (§3): the V-seat** | **FAIL** | See "Finding". The x hold needs ≤ 0.04 mm play (strength). As printed, the seat's play is set by ±0.05 mm print errors and can reach 0.08 (RSS) to 0.13 mm (worst). The stack-up was closed against CAD, not against the printed frame, and BUILD_GUIDE's two feeler checks cannot detect the play |
| 7 | Fasteners per §4 | **FAIL** (follows from 6) | **The washer is right:** Ø7 × 0.5, head bearing 4.80 sustained. **The x hold is not:** when the foot's flats land on the block first, as they do at the RSS-adverse play and worse, they take the preload. The x hold is then friction until the preload creeps (round 4's finding again), then the play |
| 8 | Spec §3 dims are named parameters | PASS, with a coupling to undo | `TIE2_FOOT_Z`, `RIDGE_APEX_Z`, `RIDGE_TIP_Z`, `VSEAT_*`, `ANCHOR_WASHER` are named. But `TIE2_FOOT_Z` = … + `VSEAT_CLR` ties the flats to the flank clearance, which is why changing `VSEAT_CLR` alone cannot fix item 6 |
| 9 | Rack clearance over the stroke (≥ 0.2) | PASS | Exact solids, gaps 0–44 every 1 mm: second post + ridge against jaw A 0.240 (gap 0) and jaw B 0.240 (gap 1); lip against jaw A 0.240; first tie 0.240 / 0.934; second web 1.128 / 0.934 |
| 10 | Washer and head clearance | PASS | Ø7 × 0.5 washer + Ø5.5 × 3 socket head at (18.35, 28) on z 51.5: jaws 3.162 (jaw A, gap 0; jaw B ≥ 33), camera mount 3.911, Brio with its plug and thumb screw 13.973 |
| 11 | Ridge and groove line up (x span) | PASS | Sections at y 26 and 30: groove x 14.45–16.05 at z 17.75, apex (15.25, 16.95). Ridge base 14.45–16.05 at z 17.85, tip 15.05–15.45 at z 17.25. Both on x 15.25. Fit: 0 mm³, min distance 0.0707 (both flanks). The frame's round-4 note (x 14.35–15.95) was text only; round 4's own what-if used `LIP_X0 + 0.1` = 14.45, as built |
| 12 | Assembly sequence | PASS (CAD) | Committed `claw_sequence_check.json` (round 5): 0 mm³ on every path. Not re-run here: the exact distances above cover the round-5 change |

### Finding (items 6–8): the V-seat is over-constrained, and its play is set by print tolerances

**The sliced frame.** I sliced the frame's committed part.stl with the arm's command and read the G-code back:
- **The bulkhead top**, on which the cover's top wall sits (CAD 48.5, exactly the slice plane of layer 48.4–48.6),
  prints at **48.4**. The last layer is `;Z:48.4`.
- **The rail block top**, on which the foot's flats land (CAD 17.75), prints at **17.8**.
- **The groove** prints as 0.2 mm steps whose top corners stand 0.1 inside the CAD flank: half-widths
  0.15 / 0.35 / 0.55 / 0.75 at the layers ending 17.2 / 17.4 / 17.6 / 17.8.
- **The cover's ridge** prints to CAD.

**So, as printed:**
- **The foot's flats stand 0.05 over the block, not 0.1.** Three stops coincide within 0.006 mm at the nominal seat:
  the ridge on its flanks, the flats on the block, and the ridge tip on the groove's closed first layer.
- **The layer corners are rounded** (stadium bead, r ≤ 0.1), which moves the ridge's contact out by 0.586 r.
- **Once the flats govern, the play is −0.05 + 0.586 r − (ridge error) − (groove error).** It does not depend on
  `VSEAT_CLR`.
- **With ±0.05 per printed surface** it is 0 (nominal), **0.082** (RSS-adverse) and **0.129** (worst case). Strength
  needs ≤ 0.04.

**Why the BUILD_GUIDE §4 step 9 checks do not detect it.**
- **The 0.15 feeler under the flats.** Whenever the ridge has play, the flats sit on the block (gap 0).
- **The 0.1 feeler at the top wall.** The top-wall gap stays 0.05–0.10 either way.

The numbers are in the cover's strength.md and strength_calc.py, section "round 5 review".

### Required fix (one change set; the strength report computes it)

1. **`VSEAT_CLR` 0.1 → 0.0** (claw_frame.py): the ridge's flanks on the CAD groove's, virtual apex 16.95.
2. **Decouple and raise the foot's flats** (cover model.py): `TIE2_FOOT_Z` = ZS − RAIL_IN + `FOOT_CLR`, with `FOOT_CLR`
   **0.30** (z 18.05). Carry the ridge's 45° flanks up to the flats: base x 14.15–16.35, 2.2 wide. That puts 0.2 of
   ridge behind the post's back face (it prints as a bump on the post's face) and 0.2 between the base and the anchor
   hole's edge on the flats plane.
3. **`RIDGE_TIP_Z` 17.35** (cover model.py), absolute: 0.15 over the closed first layer (17.2) and 0.8 wide.
4. **The frame's bulkhead top 48.45**, frame only (see the frame's review). It prints at 48.4 as today, but off the
   slice plane. The cover's `Z_TOP0` stays 48.5.
5. **BUILD_GUIDE §4 step 9:**
   - Before any screw, with the cover pressed down by hand, a 0.03 mm feeler **must** go in between the top wall and
     the bulkhead at the +y end. That proves the ridge carries the cover. The flats are now clear by design, so only
     the ridge can.
   - Then drive the M3 × 45 + washer snug **first** (it seats and centres the ridge), then the M2.5 and M3 screws.
   - Afterwards a 0.3 mm feeler must not go in at the top wall.
6. **cad_checks.py:**
   - the ridge flanks on the groove (line-to-line, 0 mm³);
   - the flats 0.30 over the block;
   - the tip at 17.35;
   - the ridge's −x base 0.2 behind the post's face;
   - the 0.2 to the anchor hole.

   Then re-run `claw_sequence_check.py`: the ridge touches the groove's flanks in CAD, so declare that contact (or keep
   the 0.001 mm³ tolerance).

**With the fix:**
- the ridge always reaches both flanks first (play 0 at nominal and RSS; 0.029 at the worst-case stack, which the
  step-9 check then rejects);
- the top wall is held up 0.06–0.26 before the screws, and stands 0–0.26 proud after them;
- spec §3's "top wall underside z 48.5 ±0.15" needs that noted (a fit matter; rack A's 0.7 backlash absorbs it).

### Notes (not blocking)

1. **Re-slice** after the fix. The committed slice files predate round 2.
2. **Spec §8's ridge line** ("a 0.15 mm feeler does not enter under the post's foot") checks nothing. The replacement
   wording is in the report.

---

### History

- **Round 4** (independent; git a701995): FAIL on §4. The anchor held the post's foot in x only by preload friction.
  Fix: the V-seat and the washer.
- **Round 3:** FAIL. Pillar B covered only half its piece; fixed in round 4.
- **Round 5 self-check** (cad-engineer): PASS. Superseded by this review.

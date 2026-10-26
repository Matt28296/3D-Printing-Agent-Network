VERDICT: FAIL

# DFM review (round 6, independent): 20261026-arm-claw-cover

dfm-reviewer + strength-analyst (independent; did not design the part) · 2026-10-26 · round 6 (ridge-first contact),
merged at 105aafe. The CAD engineer's round-6 recheck (designer's own, PASS) is replaced by this review.

**Strength verdict: FAIL** (strength.md). Lowest SF 2.49: the top M3 pan heads on the top wall at the snug preload.

## Inputs and what I re-ran

- **This job:** spec.md, design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json; the git history of
  this file and strength.md (rounds 4–6).
- **Frame:** model.py, its review and strength.
- **Shared:** claw_frame.py; BUILD_GUIDE §1 and §4 step 9; claw_sequence_check.py's placements.
- **Skills:** fdm-design-rules, prusaslicer-settings, build123d-cad, strength-checks. library/ has no PETG fit data.

**Re-run here:**
- model.py rebuilt: 32 890.41 mm³. The committed part.stl matches it (32 890.83).
- cad_checks.py: exit 0, no FAIL.
- **My own scratch slice** of both committed part.stl files with the arm's command (PrusaSlicer 2.7.2, 0.20mm QUALITY
  @MK3, Prusament PETG, each job's slice_overrides.ini). The output went to the scratchpad, not the job folders, and I
  read the G-code back with my own parser.
- **Exact-solid distances** (build123d), with jaws A and B at every 1 mm of gap from 0 to 44.
- strength_calc.py, rewritten for this review.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, one watertight solid, min Z 0 | PASS | 39.85 × 57.5 × 64.0, 1 solid, watertight, `fits_bed` |
| 2 | Orientation, load paths vs layers | PASS | Standing on its −y end (G +y up). The ridge is a vertical prism in print, so its root and flanks are in the layer plane |
| 3 | Overhangs ≤ 45°, bridges | PASS | mesh_check: overhang 0.26 %, bridges ≤ 2.0 mm. The ridge's 45° lead-in continues the post's underside (G-code: the tip path is at z 17.775 at G y 24.5, the full tip from y 24.9 on) |
| 4 | **Printed heights** | PASS | Read back: flats at **18.05** (perimeter 18.275), tip at **17.35** (17.575), flanks to CAD (0.225 inside), top wall underside 48.5. Frame: bulkhead and ribs **48.4**, block **17.8** (frame review) |
| 5 | **The 0.2 × 0.2 bump** (mesh_check thin wall 0.14 at G (14.3, 29.3, 18.1)) | PASS | **It does not print.** The external perimeter runs from the −x flank (14.527, 17.991) straight onto the post's back face (14.575, 18.039). No sliver, no gap fill, nothing to snag. The printed ridge root is x 14.35–16.35 (**2.0**, not 2.2), and strength uses 2.0 |
| 6 | **Fits (§3): the V-seat as printed** | PASS | **The ridge lands first** at nominal and RSS (margins: top wall +0.043, tip +0.093, flats +0.193). Play is **0 / 0** there; 0.079 at the absolute worst stack, which step 9 rejects; 0.029 for the worst build step 9 accepts (the tip on the groove's 17.2 layer), where the lowest frame-model SF is 4.04. Tolerances are ±0.05 on every printed surface, the bulkhead top and the tip/slot included, plus r 0.05–0.10 (strength.md §1) |
| 7 | **Fasteners per fdm-design-rules §4** ("use washers or wide heads") | **FAIL** | The two top M3 × 10 pan heads (no camera) and the two front M2.5 × 16 pan heads clamp the PETG cover **with no washer**. At the arm's snug preloads, head bearing is **2.49** and **3.26** (sustained, req 4; strength rows 119–120). The anchor got its washer for the same reason in round 5, as did every MG996R and ring screw. Round 6 adds to it: the top M3s now also pull the proud top wall down. The anchor itself is right: Ø7 × 0.5 washer, 4.80 |
| 8 | Named parameters (§3) | PASS | `FOOT_CLR`, `TIE2_FOOT_Z`, `RIDGE_APEX_Z`, `RIDGE_TIP_Z`; `VSEAT_*`, `BULK_TOP`, `ANCHOR_WASHER`. The flats no longer depend on `VSEAT_CLR` |
| 9 | **Rack clearance over the stroke (≥ 0.2)** | PASS | Exact solids, gaps 0–44: second post + ridge + foot **0.240** (jaw A, gap 0), lip 0.240, first tie 0.240, webs 1.128, frame rail block 0.250 |
| 10 | **Washer and head clearance** | PASS | Ø7 × 0.5 washer + Ø5.5 head at (18.35, 28): jaws **3.162**, camera mount **3.911**, Brio with its plug **14.301**. The front M2.5 heads are 0.500 from jaw B (0.26 with the worst standing) |
| 11 | Ridge and groove line up | PASS | Both on `VSEAT_XC` 15.25. The printed groove walls are centred on it (frame G-code). cad_checks' flank probes pass |
| 12 | **The standing of the top wall** (0.05 CAD, 0.156 printed) | PASS (notes) | Rack A: backlash 0.33–0.40 along the guide nominal (0.25–0.57 at the extremes), tip clearance ≥ 0.20, contact ratio ≥ 1.28: no binding. The M3s have 7.0 engaged with the wall pulled down, 6.74 if not. Camera mount ≤ 0.6° pitch, ≈ 1 % of the image. Slot B's lower clearance 0.246 nominal / 0.133 RSS / 0.011 worst (strength.md §3) |
| 13 | BUILD_GUIDE §4 step 9 seat check | PASS (with two wording fixes) | See "Step 9" below |

## Required fix

The fasteners (§4). The strength review computes these.

1. **Top screws without the camera:** replace the 2 × M3 × 10 pan heads with **2 × M3 × 14 pan head + 2 × Ø7 × 0.5
   washers (ISO 7089)**, driven snug only (≤ 0.09 N·m, as the anchor).
   - Head bearing: 4.80.
   - Pull-out on the preload: 4.12 (4.02 if the worst standing is left at the screw).
   - The tip ends at z 38.0; the 14 mm pilot's floor is 34.45.
   - No model change.
   - With the camera, the 2 × M3 × 18 button heads stay (pull-out 4.41).
2. **Front M2.5 screws.** At z 3 a DIN 125 Ø6 × 0.5 washer touches jaw B's neck (exact solids: 0.000).
   - **Recommended (b):** `FRONT_SCREWS` z 3 → **2.5** in claw_frame.py, plus **2 × DIN 125 Ø6 × 0.5 washers**.
     - Washer and head 0.50 under jaw B (0.26 with the worst standing).
     - Head bearing 5.42 on the preload, 4.17 under the stall (130 N at z 2.5).
     - Pull-out 4.15.
     - The frame's front pilots keep a 2.4 top skin and 1.4 underneath.
     - Re-run cad_checks and claw_sequence_check, with the washers added to its screw heads.
   - **Text-only (a):** "M2.5: drive each until the head seats, then stop (≤ 0.04 N·m)". The preload is then ≤ 82 N and
     head bearing ≥ 4.0. A torque that small cannot be measured by hand, so (b) is the robust fix.
   - z 2.75 is not enough: 0.25 in CAD, 0.01 with the worst standing.

## Step 9 (BUILD_GUIDE §4): can it tell a good seat from a bad one?

**Yes, for what matters.**
- **Before any screw, the 0.03 feeler must enter at the +y end.** If the ridge carries the cover, the top-wall gap is
  ≥ 0.043 at RSS (0.156 nominal), so the feeler enters. If the top wall carries it (play up to 0.079, frame-model SF
  1.89), the gap is 0: the feeler cannot enter, and the build stops.
- **The case it cannot see is the tip bottoming** on the groove's 17.2 layer. That is play ≤ 0.029, SF 4.04: harmless.
- **False rejects:** a good build reads under 0.03 only beyond the 3σ tail.
- **After the screws, the 0.3 feeler must not enter.** That catches a ridge riding out of the groove (≥ 0.8 high). It
  does not prove the anchor seated: a good build stands 0.06–0.10 after the anchor, under 0.3 either way. A worst-stack
  good build (0.34 after the anchor alone) could falsely reject before the top screws are in.

**Two wording fixes, so that the reading means what it should:**
- (i) **"Press the top wall straight down directly over the inner post (over the third hole)."** Pressing behind the lip
  (over the bulkhead) rolls the cover about the ridge against the front plate's contact and closes the gap. Pressing on
  the front plate tips it about the bulkhead's front edge.
- (ii) **"Use a feeler blade at least 10 mm wide, slid in flat from that side across the whole bulkhead top (and the
  rib beside it)."** A narrow blade can find the open end of a wedge-shaped gap.

## Notes (not blocking)

1. **The groove's 17.0–17.2 layer is an open 0.3 slot**, not "closed": two external perimeters with bead edges 15.10 /
   15.40 at every y. Harmless: the ridge's flat tip faces that layer's top (17.2) at 0.15–0.35 off the centre line,
   0.206 above it nominal.
2. **Slot A's front edge.** The front plate is 0.148 from jaw A at slot A's lower edge on its front face, for the whole
   stroke. This is the jaw's r 3 kink fillet. It predates round 6. A 0.3 × 45° chamfer on both slots' front edges would
   restore 0.25.
3. **Re-slice** for the job: the committed slice files are older than round 2.

## Spec text that needs to change

**Cover spec §8**, the Pass list's second bullet. Replace "the second post's ridge still seated (a 0.3 mm feeler does
not enter between the top wall and the bulkhead at the end where the lower slot is open)," with:

> the second post's ridge still seated (a 0.3 mm feeler, blade at least 10 mm wide, does not enter between the top wall
> and the bulkhead at the end where the lower slot is open), and no new whitening at the lip's back corner under the top
> wall (compare with its state after assembly),

**Cover spec §8**, add an acceptance line before the proof test:

> - [ ] **Seat check (BUILD_GUIDE §4 step 9).** Before any cover screw, with the top wall pressed straight down over the
>   inner post, a 0.03 mm feeler (blade ≥ 10 mm wide) enters between the top wall and the bulkhead at the end where the
>   lower slot is open. After the anchor and every cover screw, a 0.3 mm feeler does not. The strength verdict assumes a
>   build that passes the first check.

**Cover spec §2**, "Fasteners used". Replace it with:

> 2 × M3 × 14 pan head + Ø7 × 0.5 washers (ISO 7089) down into the frame's bulkhead, snug only (2 × M3 × 18 button heads
> through the camera mount when it is fitted); 2 × M2.5 × 16 pan head (head ≤ Ø5) + DIN 125 Ø6 × 0.5 washers back into
> the wrist plate's front edge at z 2.5; 1 × M3 × 45 socket head + Ø7 × 0.5 washer (the anchor)

With fix (a) instead of (b), the M2.5 part is unchanged, plus "≤ 0.04 N·m".

**Cover spec §3**, the top wall's row: "assembled, 0 to +0.3 over the printed bulkhead (48.4) at the +y end" becomes
"assembled, 0 to +0.35 (0.06–0.10 nominal after the anchor)". The fit-type note "rack A's 0.7 backlash absorbs it"
becomes "a higher guide only increases rack A's backlash (0.33–0.49 nominal to RSS)".

**BUILD_GUIDE** (Architect): §1's BOM rows for the top M3s and the front M2.5s, and §4 step 9 (i)–(ii) above.

---

# History

- **Round 6 self-check** (cad-engineer; git 8527ef6 / 105aafe): PASS. It is replaced by this review. Its ridge, flats
  and tip print as it said. Its stack left out the bulkhead and tip/slot tolerances. It counted three carrying corners
  and did not check the screw heads.
- **Round 5 independent review** (git be24872): FAIL on §3. Three stops coincided and the play came from print
  tolerances (0.082 RSS). The fix was ridge-first contact, now built and verified.
- **Round 4** (independent; git a701995): FAIL on §4. The anchor relied on preload friction.
- **Round 3:** FAIL. Pillar B covered only half its piece; fixed in round 4.

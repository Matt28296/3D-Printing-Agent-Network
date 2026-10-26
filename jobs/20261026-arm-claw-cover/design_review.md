VERDICT: PASS

# DFM review (round 7, independent): 20261026-arm-claw-cover

dfm-reviewer + strength-analyst (independent; did not design the part) · 2026-10-26 · round 7 (washers under every
cover screw, front M2.5 at z 2.5, 0.3 slot-edge chamfers), merged at a8ae29c. The CAD engineer's round-7 recheck
(designer's own, PASS) is replaced by this review. The round 6 independent review is kept below as history.

**DFM: PASS. Strength: NEEDS_TEST** (strength.md): every verdict row passes; NEEDS_TEST only because the PETG
allowables are placeholders. Lowest verdict SF **3.03** (rows 30 / 87, the plate strips at the ties' webs, opening
against an obstacle, req 3). Sustained rows: top washers **4.80**, front washers **5.42**, anchor washer 4.80, anchor
pull-out 4.15 (req 4). **No required fix.**

## Inputs and what I re-ran

- **This job:** spec.md, design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json, the self-check's
  design_review.md / strength.md / strength_calc.py, and the round 6 review (below).
- **Shared:** claw_frame.py (`TOP_WASHER`, `FRONT_WASHER`, `FRONT_SCREW_Z`), BUILD_GUIDE §1 and §4 steps 9 and 13, the
  frame's and the camera mount's model.py, the jaw's model.py, `claw_sequence_check.py`.
- **Skills:** fdm-design-rules, strength-checks, build123d-cad, prusaslicer-settings. library/ has no PETG fit or
  strength data.

**Re-run here** (`/home/claude/.venv-cad/bin/python3`):
- model.py rebuilt: 32 888.17 mm³ = geometry.json; the committed part.stl matches (32 888.59, watertight).
- `cad_checks.py`: 27 PASS, exit 0 (the self-check's "28/28" miscounts; 27 checks exist). `tools/mesh_check.py`: overhang 0.26 %, bed contact 703.6 mm², widest bridge 2.0,
  1 thin-wall hit (the ridge's 0.2 × 0.2 bump, which does not print: round 6), fits bed; mesh_check.json unchanged.
- **My own scratch slice** of the committed part.stl with the arm's command (PrusaSlicer, 0.20mm QUALITY @MK3,
  Prusament PETG, this job's slice_overrides.ini; output in the scratchpad as a text file, never a job file), read back
  with my own parser (the changed features below).
- **Exact-solid clearances** with my own scripts (OCC `BRepExtrema`, face by face so that the designed contact planes
  are skipped and nothing else), jaws at every 2 mm of gap from 0 to 44 and the prismatic features re-checked at 0, 11,
  22, 33, 44; washer and head solids for both builds; washer-seat probe rings.
- `claw_sequence_check.run()` into the scratchpad (not the committed JSON): see item 12.
- `strength_calc.py`, rewritten for this review (strength.md).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, one watertight solid, min Z 0 | PASS | 39.85 × 57.5 × 64.0, 1 solid as printed and as fitted, `fits_bed` |
| 2 | Orientation, load paths vs layers | PASS | Unchanged: standing on its −y end (G +y up) |
| 3 | Overhangs ≤ 45°, bridges | PASS | mesh_check as above. The new chamfers are prisms along G y: vertical in print |
| 4 | **Moved front holes** (Ø3.0 teardrops at y ±24, **z 2.5**) | PASS | Teardrop point +y = up in print (correct for a hole horizontal in print). G-code at the layers through both hole centres (Z 8.0, 56.0), at x 37.35: void z 1.1–3.9 (the Ø3.0 CAD circle), then solid perimeters z 4.0–5.75 at y +24 up to slot B's lower edge: the **1.75 ligament** prints solid (it was 1.25 at z 3). 7.0 to the plate's bottom |
| 5 | **Slot-edge chamfers** (0.3 × 45°, slot A's lower side y −33…−6.5, slot B's upper side y 6.5…33) | PASS | G-code at G y −25, −10, +10, +25: the outline's front corner steps in to x 39.65 / 39.75 / 39.85 at 0.1 / 0.2 / 0.3 from the slot side, as CAD; the external perimeter's centreline is 0.437 from the CAD corner. No strength effect: the chamfers sit at the free ends of the two plate strips, and the racks bear on the plate's inner face |
| 6 | **Washer seats** | PASS | Probe rings at r 2.5 and 3.45 (Ø7) round both top holes on the top wall (z 51.5), and at r 2.5 and 2.95 (Ø6) round both front holes on the front face (x 39.85, z 2.5): every probe on the flat face, except where the ring crosses the hole's own teardrop point (r 2.5, +y), which the washer bridges. The Ø6 washers' top edge is at z 5.5, 0.25 under slot B's lower edge. Stacked against it: the washer's 0.1 float on its bore, the frame pilot's ±0.05, and the cover at the +y screw at most 0.07 low in a build step 9 accepts. Even then the washer stays on the face to within 0.02, and a 0.5 steel washer overhanging an edge by 0.02 still bears flat. Both seats are vertical walls in print, so perimeter-flat |
| 7 | **Fasteners per fdm-design-rules §4** | PASS | Every cover screw has a washer. Engagement and tips: **M3 × 14** + 0.5 washer under the 3.0 top wall: 10.45 below the bulkhead in CAD, **10.5** below the printed bulkhead (48.4) with the wall pulled down, 10.24 with the worst standing left; tip z 37.9–38.0, **3.5** above the pilot floor (34.45 CAD / 34.4 printed). **M2.5 × 16** + 0.5 washer through the 5.0 plate: **10.5** engaged; tip x 24.35, **3.5** inside the 14 mm pilot's floor (x 20.85). **M3 × 18** + 0.5 washer through the 3.5 pad and the 3.0 top wall: **11.0** engaged with the wall pulled down (10.95 CAD, 10.74 worst standing), **not 11.5** (that is the bare-head figure); tip z 37.4–37.5, 3.0 above the floor. Even a +0.35 (js15) long screw keeps ≥ 2.6 to every floor. Strength rows: strength.md |
| 8 | Named parameters (§3) | PASS | `TOP_WASHER`, `FRONT_SCREW_Z`, `FRONT_SCREWS`, `FRONT_WASHER` (claw_frame.py), `SLOT_EDGE_CHAMFER` (model.py) |
| 9 | **Rack, jaw and slot-edge clearances, gap 0–44 (≥ 0.2)** | PASS (one ruling) | Exact solids, the contact planes (top-wall underside z 48.5 for jaw A, wrist-plate top z 6 for jaw B) skipped, nothing else: **slot A's front edge 0.211** to jaw A's r 3 kink fillet and **slot B's 0.211** to jaw B's, constant over the whole stroke (were 0.148); frame rail block 0.250 (jaw B); jaw A–jaw B ≥ 2.0 for gap ≥ 2. **The r 2 corner fillet to rack A's 2 mm edge chamfer: 0.177**, not 0.187 (analytic (CLR + chamfer − r)/√2 = 0.25/√2 = 0.1768; the solids give 0.1768 at every gap, at the fillet's tangent line on the guide plane). **Ruling: acceptable, not an interference risk** (see below). The jaws' kink fillets print as a 0.2 staircase in the jaw (its x is print Z): at the slot edge the fillet's slope is 0.16, so ±0.016 |
| 10 | **Washer and head clearance** | PASS | Front Ø6 washers: **0.500** under jaw B's neck (gap ≥ 8; 2.3 at gap 0), heads 1.000. The washer is located by the screw, which the **frame's** pilot locates, and jaw B rides on the **frame's** wrist plate, so the cover's standing does not close it (the self-check's "0.26 with the worst standing" is wrong); its own float on the bore (0.1) and the pilot's print position (±0.05) leave ≥ 0.35. Top Ø7 washers + M3 pan heads (no camera): 12.77 to the jaws over the stroke |
| 11 | Ridge, groove, seat | PASS | Unchanged since round 6 (cad_checks: flanks 0 mm³ / distance 0, flats 0.30, tip 0.15, top wall 0.05; as printed 0.156 / 0.306 / 0.206) |
| 12 | Assembly sequence | PASS | `claw_sequence_check.run()`, re-run into the scratchpad (the committed JSON untouched) with the Ø6 washers under the M2.5 heads: **ok** (873 s). 0 mm³ on every insertion path, the swept pinion and the 0–44 stroke; backlash 0.40 per mesh at gaps 2 / 22 / 42 |
| 13 | **Camera build with washers** (M3 × 18 button heads on Ø7 × 0.5 washers on the mount's pad) | PASS | The Ø7 washers lie whole on the pad (probe ring r 3.45 at z 55.0). Washer **0.258** from the seat's front face (x 2.99 at the pad, leaning back 0.3 over its 5.85 height), the button head 0.9, the Brio (with its plug and thumb screw) 3.89. With the washer's 0.1 bore float and the screw's 0.2 float in the mount's Ø3.4 printed hole, the washer's edge can come to touch that face: harmless, because the face meets the pad at a sharp corner (no fillet to ride up) and leans away, so the washer still lies flat. Rows: head on the washer 4.80 (the camera mount's own row; information here), pull-out 4.22 (frame, verdict row) |
| 14 | BUILD_GUIDE §4 step 9 | PASS (one text correction) | See "Step 9" below |

### Ruling: the 0.177 between the cover's r 2 corner fillet and rack A's 2 mm edge chamfer

**Acceptable; not an interference risk. No fix required.** It is not round 7: `RACK_EDGE_CHAMFER` 2.0 and
`CORNER_FILLET` 2.0 have stood since round 3.

- The clearance is (CLR + c − r)/√2 with c = r = 2: only the 0.25 x gap between rack A's front face (x 34.6) and the front
  plate (x 34.85), seen across the two 45° faces. The fillet's material lies wholly in x + z ≥ X_F0 + Z_TOP0 − r
  (81.35); rack A's lies in x + z ≤ (rack front) + (rack top) − c. The rack's top can never rise above the guide
  (z 48.5, the top wall it rides on) and its front can never pass the front plate (x 34.85). So the closest the
  chamfer can come is line-to-line **at the fillet's two tangent lines**, and only when the rack is already bearing on
  both the guide and the front plate. The arc curves away from the chamfer everywhere else. In every admissible
  position the gap is ≥ 0.
- As printed: the fillet prints in the cover's layer plane (perimeter-accurate), and the rack's chamfer prints as a
  0.2 staircase in the jaw. A step corner standing up to 0.1 proud of the chamfer can reach the fillet only within
  ~0.1 of its tangent line. There the fillet has left the guide plane by s²/(2r) ≤ 0.0025: microns, below the
  surface's own roughness. Any print error that makes the fillet fat near its tangent line is a bump on the top
  wall's underside, which the rack's top face meets anyway.
- So the ≥ 0.2 rule, which protects sliding gaps between faces that are not themselves bounded by the designed
  contacts, does not bind here.
- The literal fix, if wanted: `CORNER_FILLET` 2.0 → 1.9 gives 0.247 in CAD (1.95 gives 0.212). The fillet's Kt 1.5 row
  needs r ≥ 0.25 h = 1.25, so either keeps it; the cover only. Not required.

### Step 9 (BUILD_GUIDE §4): can it be followed, and does it tell a good seat from a bad one?

**Yes.** The round-7 hardware changes nothing in the seat. The round 6 review's two wording fixes are in, and its
reasoning still holds:
- the 0.03 feeler before any screw (blade ≥ 10 mm, pressed over the inner post) separates a ridge-carried cover (gap
  ≥ 0.043 at RSS, 0.156 nominal) from a top-wall-carried one (gap 0);
- the 0.3 feeler after the screws catches a ridge out of its groove (≥ 0.8 high);
- the case no feeler sees is the tip bottoming (play ≤ 0.029; frame-model SF 4.04);
- a false reject on the 0.3 check is possible only in the worst-stack tail beyond RSS.

New in round 7, checked here:
- **Order and hardware.** Anchor + Ø7 first, then 2 × M2.5 × 16 + Ø6, then 2 × M3 × 14 + Ø7 (or the camera mount with
  2 × M3 × 18 + Ø7), each snug. This order matches the strength model. Every washer seat is whole (item 6).
- **"Snug only: stop when the washer seats"** is the best hand instruction available for the pan heads. On the top
  M3s a worst-stack cover needs up to 144 N (RSS-high 92 N) to pull the proud wall down. A user who stops at the first
  touch leaves it proud at the screw. No verdict row relies on the wall being pulled down: the pull-out row takes the
  worst standing, and the joint's own service tension is ≤ 24.5 N. The after-check reads the +y end, which the ridge
  sets. So no change is needed.
- **Text correction (Architect), BUILD_GUIDE §1**, the top-screw row: "(10.5 / 11.5 mm engaged)" → "(10.5 / 11.0 mm
  engaged)". With the Ø7 washer under the M3 × 18 button head, 0.5 less is engaged; the strength rows use 11.0 / 10.74.

## Required fix

None.

## Notes (not blocking)

1. **The frame's lowest row, 4.02** (top M3 × 14 pull-out at the snug preload, worst standing), is thin but computed
   correctly. The frame's strength.md weighs its bounds. If the Architect wants margin that does not lean on the
   project's interlayer-shear convention, the no-camera top screws can be **M3 × 16 + Ø7 × 0.5**: 12.24–12.5 engaged,
   SF 4.81–4.91, tip z 35.9–36.0, 1.5 above the pilot floor (1.15 with a js15-long screw). Hardware only, no model
   change.
2. **The camera mount job** still lists bare M3 × 18 button heads in its own spec and strength rows (bare head on its
   pad: 2.64, sustained). BUILD_GUIDE now puts a Ø7 × 0.5 washer under each (4.80). That job's spec §2 and strength row
   should be brought in line by its owner. It is not this part.
3. **Re-slice for the job.** The committed slice files predate rounds 2–7. My scratch slice was for read-back only.
4. **Slot B's upper chamfer with the cover low.** The 0.211 to jaw B is CAD. Slot B's upper side belongs to the upper
   piece, which the ridge holds at or above its CAD height (nominal +0.004 after the anchor). So the cover's float
   does not erode this clearance materially. Slot B's lower side (0.25 CAD) is the one the float erodes: 0.133 RSS,
   0.011 worst, as round 6 found. Unchanged by round 7.

## Spec text

None needed beyond the BUILD_GUIDE §1 figure above. Spec §2 and §3 already carry the round-7 values; the slot rows'
"(0.21)" matches the solids (0.211).

---

# Round 6 independent review (kept as history; its verdict: FAIL)

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

- **Round 7 self-check** (cad-engineer; git 327fd36 / a8ae29c): PASS. It is replaced by this review. Its geometry and hardware check out. Its errors: the fillet-to-chamfer clearance (0.187; it is 0.177, ruled acceptable here), the front washers' clearance with the cover's standing (the washer moves with the frame-located screw, not the cover), the camera build's engagement (11.5; 11.0 with the washer), and the M2.5 stall bound's pivot (z 0; the frame's 0.4 bed chamfer puts it at z 0.4, 150 N, SF 3.62 instead of 4.17).

- **Round 6 self-check** (cad-engineer; git 8527ef6 / 105aafe): PASS. It is replaced by this review. Its ridge, flats
  and tip print as it said. Its stack left out the bulkhead and tip/slot tolerances. It counted three carrying corners
  and did not check the screw heads.
- **Round 5 independent review** (git be24872): FAIL on §3. Three stops coincided and the play came from print
  tolerances (0.082 RSS). The fix was ridge-first contact, now built and verified.
- **Round 4** (independent; git a701995): FAIL on §4. The anchor relied on preload friction.
- **Round 3:** FAIL. Pillar B covered only half its piece; fixed in round 4.

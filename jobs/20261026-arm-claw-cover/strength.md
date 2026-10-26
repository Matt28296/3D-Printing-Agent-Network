VERDICT: NEEDS_TEST

# Strength check: 20261026-arm-claw-cover (round 5)

cad-engineer (round 5 design change, by the user-approved fix; the strength method and the 64-variant frame model are
the strength-analyst's from round 4, extended for the V-seat) · 2026-10-26 ·
`python3 jobs/20261026-arm-claw-cover/strength_calc.py`. It is plain python3, run from the project root (about 30 s). It
reads `claw_frame.py`, this job's, the jaw's and the frame's `model.py`, `tools/cadlib.py` and `tools/hobby_parts.py`
with `ast`. Section widths marked "probed" were measured on the solids and are written into the script as numbers.

## Summary

**Every verdict row passes. The verdict is NEEDS_TEST only because the allowables are placeholders.**

- **The post's foot is now held in x by geometry.** A 90° ridge under it sits in a V-groove in the frame's rail block.
  A +x push rides up the groove's 45° flank; the M3 × 45 holds that lift in tension. No friction and no preload are
  relied on (fdm-design-rules §4). The script's anchor mode is `locked`: x held at the flank, preload not counted.
- **Lowest SF 3.01** (required 3): row 102, rack B's −y end pushing the lower piece forward on one M2.5 pan head.
  It is unchanged since round 3.
- **The rows that failed in round 4 are now well clear:**

  | Round-4 row | Round 4 (preload gone) | Round 5 |
  |---|---|---|
  | Top wall behind the lip, opening stall on jaw B | 1.37 | **18.58** (row 30) |
  | Top wall behind the lip, desk crash on jaw B | 2.15 | **29.17** (row 8) |
  | Top wall through the M3 holes, opening stall | 2.44 | **29.53** (row 31) |
  | Anchor head on the top wall, 150 N sustained (req 4) | 2.34, bare head | **4.80**, on the Ø7 × 0.5 washer (row 110) |
  | Spec §8 proof push on jaw B (req 2): top wall behind the lip / through the M3 holes | 1.08 / 1.93 | **14.66 / 23.30** (rows 113–114) |

- **The new rows (the ridge and the anchor), opening stall on jaw B, Fx 25.6 N:**
  - the ridge's root, the flank force's moment + the wedge's compression, Kt 2.5: **3.03** (row 44);
  - flank bearing on the groove: **3.61** (row 42);
  - the ridge's root in shear: **3.85** (row 43);
  - M3 × 45 pull-out with the preload + the wedge's lift + the lift, 185 N on 10.75 mm: **3.42** (row 41);
  - M3 × 45 pull-out on the preload alone, sustained: **4.22** (row 112, req 4).
- **The reviewer's estimate** was about 4.6 (cover), 4.22 (pull-out on the preload) and 4.80 (head on the washer).
  The last two match exactly. The cover's lowest is 3.01, not 4.6, for two reasons:
  - Row 102 (3.01) and the plate strips at the ties' webs (3.03, rows 29 and 83) never depended on the anchor. They were
    already in round 4's table at the same values; the reviewer's 4.64 was the frame-model sections only.
  - The ridge's own rows (3.03 to 3.85) are new. They are lower than the reviewer's what-if (flank 4.5, root 3.7) because
    the ridge's tip is cut flat at z 17.25 (see "Design" below), which leaves 0.71 mm of flank in contact instead of
    0.92, and because the root now also carries the flank force's moment.
- **One sensitivity matters: play at the ridge.** Free slide before the flank bears costs strength fast (table below:
  0.04 mm → 3.41, 0.05 → 2.83, 0.1 → 1.54). BUILD_GUIDE §4 step 9's feeler checks bound it; see "Play".

## Design (round 5)

- **Frame:** a 90° V-groove, 0.8 deep, along y in the rail block's top: x 14.45–16.05 at z 17.75, bottom z 16.95, y
  23.5–32, open at +y. The anchor pilot is unchanged.
- **Cover:** the matching ridge under the post's foot, 0.1 clear per flank (horizontal; 0.071 normal). Virtual apex
  z 17.05, base x 14.45–16.05 at the foot's flats. The flats rise 0.1 (`TIE2_FOOT_Z` 17.85). The ridge runs y 24–32,
  full depth from y 24.6, with a 45° lead-in.
- **The ridge's tip is cut flat at z 17.25** (0.4 wide). The groove's first layer in the frame (z 17.0–17.2) is a 0.3 mm
  slot at its mid-height and will not print open, so a full ridge would bottom there.
- **Where the flank bears.** The frame prints the groove in 0.2 mm layers sliced at mid-height. Each layer's top corner
  stands 0.1 (horizontal) inside the CAD flank: z 17.4, 17.6 and 17.8. The CAD's 0.1 per flank is exactly that, so the
  printed ridge meets those corners at the nominal seat. The x reaction is taken at their middle, z 17.6.
- **Hardware:** an M3 washer Ø7 × 0.5 (ISO 7089) under the M3 × 45's head: 10.75 mm engaged (11.25 without it).

## Round-4 required change: made?

| Round-4 required change | Round 5 as built | Made? |
|---|---|---|
| Frame: 90° V-groove, 0.8 deep, x 14.45–16.05 at z 17.75, y 23.5–32, open at +y | Exactly (frame cad_checks) | Yes |
| Cover: matching ridge, 45° lead-in, flats raised 0.1 (`TIE2_FOOT_Z` 17.85) | Yes, 0.1 clear per flank as the user set; tip cut at 17.25 (the reviewer had 17.10) for the groove's unprintable bottom | Yes |
| M3 washer Ø7 × 0.5 under the head; BUILD_GUIDE §1 and §4 step 9 | Yes | Yes |

## Load cases

As round 4. The stall is 216 N·mm through the 20-tooth pinion: 21.6 N on one rack, or 10.8 N per jaw. Each rack cocks in
its 0.25 mm gaps and reacts its finger's moment with end forces R = F × (x_load − 28.6) / span. The span is 56.5 with the
jaws closed, 48.4 at 30 mm open, and 41.4 at 44 mm open.

| # | Case | Load | Where it lands | Type, SF req |
|---|---|---|---|---|
| 1 | Stall, one jaw blocked (spec) | 21.6 N, 3 mm from the tip: R 19.8–27.0 N | Rack A forward on the upper piece near the top wall, and back on the lip; rack B on the lower piece | Short-term, 3 |
| 2 | Stall, both jaws | half of 1 | As 1 | Cyclic, 4 |
| 3 | Crash | 13 N at the tip, finger pushed shut: R 12.6–17.2 N, reversed | Rack B on the upper piece's bottom strip (z 17.2), whose reaction is on the frame; rack A on the lower piece's top strip | Short-term, 3 |
| 4 | Opening against an obstacle (Architect: a design case) | 21.6 N, reversed: R up to 27.0 N | As 3 | Short-term, 3 |
| 5 | Handling | 5 N pushing a finger shut: R 6.6 N | As 3 | Short-term, 3 |
| 6 | Sideways push on jaw B | Yaw stall 7.1 N; hand 5 N | Strip under slot B | Short-term, 3 |
| 7 | Rack A lift | 13.8 N at the rack's end | Top wall between the lip and the plate | Short-term, 3 |
| 8 | Camera tug | 10 N USB tug tips the mount back | Top wall's rear edge | Short-term, 3 |
| 9 | Anchor | M3 × 45 snug, 150 N, on a Ø7 washer | Washer on the top wall, the post round its hole, pull-out from the frame | Sustained, 4 |
| 10 | Spec §8 proof | 32 N at 3 mm from the tip, jaws 30: R 34.2 N; 10.7 N sideways | As 3/4 and 6 | Proof, 2 |

## Build direction and sections

- **Print direction.** The cover prints standing on its −y end (print Z = claw y), so bending in the side profile runs
  along the layers. The strip under slot B is a beam along y and bends across them.
- **Global model:** round 4's two-zone 2-D frame in the x–z plane, 64 joint variants. The second post (8 thick on the
  lip's centre line) is probed at z 35.5: 194.3 mm² net of the anchor hole, I_y 1086 mm⁴, so b 24.3.
- **The post's foot (round 5):** a rigid link from the web to the anchor node at z 17.6 (the flank's resultant). The node
  is held in x by the ridge (3 kN/mm) and in z by the flanks (compression) and the screw (tension).
- **The post below the web** (z 17.85–19.25): probed at z 19, 8 × 9.15 net of the hole: A 62.4 mm², I_y 383.5 mm⁴.
  Kt 2.5 at the web's bottom corner. It carries the lift plus the wedge's lift.
- **The ridge (round 5).** It prints as a vertical prism, so its cross-section lies in the layer plane and its root (the
  plane z 17.85, 1.6 wide over the full-depth 7.4 mm) is in-plane: 25 MPa, 12.5 in shear.
  - **Flank bearing:** all of Fx on one 45° flank, frictionless: normal Fx √2 on 0.71 × 7.4 mm (the contact band from the
    ridge's flat tip, z 17.25, to the block top, z 17.75; the 0.6 mm lead-in ignored).
  - **Root, shear:** 1.5 Fx / (1.6 × 7.4).
  - **Root, moment and compression:** the flank's normal force acts along (−1, +1)/√2 through (15.25 + z_c − 17.05, z_c).
    Its moment about the root's centroid (15.25, 17.85) is Fx (2 z_c − 17.85 − 17.05): 0.3 Fx at z_c 17.6 (0.1 Fx at the
    CAD band's middle, 17.5). Its vertical part (= Fx) compresses the root. Stress = Fx / A + Kt 6 M / (b² L), with
    Kt 2.5 (the root corners are 135°; they are taken as sharp 90° ones) and the two added in magnitude.
- **Anchor screw:** Ø3 thread cylinder over 10.75 mm in the frame. Tension = the preload (150 N, added only where it makes
  a row worse) + the wedge's lift (= Fx) + the frame model's lift. The washer (Ø7) bears on 28.8 mm² round the Ø3.4
  printed teardrop.

## Assumptions

- **Preload.** "Snug only", about 150 N (0.09 N·m). It is not relied on for any load path. It is added to the screw's
  tension for pull-out, which can only make that row worse.
- **Friction on the flank: none** (worst case for the lift and the flank's normal force).
- **Play at the ridge: zero** in the verdict rows (the printed corners meet the ridge at the nominal seat). The table
  below gives the strength with play. BUILD_GUIDE §4 step 9 checks it.
- **Joint variants** as round 4: top wall clamped or on 1.1 × 10⁵ N·mm/rad; M2.5 3 or 30 kN/mm, held or free along z;
  plate leg 21 / 25.5; second lip 25.5 / 37.25; corner coupling 2.9 × 10⁴ / 10⁵ N·mm/rad.
- **PETG** E 1.8 GPa (placeholder); only stiffness ratios use it.
- **Temperature:** 40 °C against PETG at about 70 °C: OK.

## Allowables and sources

`library/materials.csv` has no measured row: these are the strength-checks **placeholder** PETG values, so NEEDS_TEST is
the best possible verdict.

| Quantity | Value | Source |
|---|---|---|
| Along the layers | 25 MPa | Skill placeholder |
| Across the layers | 12.5 MPa | 0.5 × in-plane |
| Interlayer shear | 6.25 MPa | 0.5 × 12.5 |
| Bearing | 25 MPa | In-plane value |
| Kt | 2.5 sharp; 1.5 for r ≥ 0.25 h; 1.7 for r/h 0.15–0.25; 2 at a hole | Skill |

Required SF: 3 short-term, 4 cyclic or sustained, 2 at a proof load (1.5 × service).

## Anchor forces (worst of 64 variants, foot held by the ridge)

| Case | Fx at the ridge | Lift | Screw: wedge + lift | + preload |
|---|---|---|---|---|
| Opening stall on jaw B, 27.0 N | 25.6 N | 10.0 N | 35.1 N | 185.1 N |
| Desk crash on jaw B, 17.2 N | 16.3 N | 6.4 N | 22.3 N | 172.3 N |
| Spec §8 proof push on jaw B, 34.2 N | 32.5 N | 12.7 N | 44.5 N | 194.5 N |

## Results (from `strength_calc.py`, verbatim)

The bracket gives the joint variant that governs a frame-model row; "foot held by the ridge in the groove" is the anchor
mode.

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | stall, one jaw blocked, jaws 44 open: rack A's -y end at the lip's end, R 27.0 N (the first tie's prop ignored) | lip root at the top wall, rack side (Kt 2.5): b_eff 7.9, t 8.0, lever 5.9 | XY | 4.72 | 25.00 | 5.30 | 3 | OK |
| 2 | stall, one jaw blocked, jaws closed: rack A's -y end at y -25.1, R 19.8 N | lip root at the top wall, rack side (Kt 2.5): b_eff 13.8, t 8.0, lever 5.9 | XY | 1.98 | 25.00 | 12.63 | 3 | OK |
| 3 | stall, both jaws (cyclic), jaws 44 open: R 13.5 N at the lip's end | lip root at the top wall, rack side (Kt 2.5): b_eff 7.9, t 8.0, lever 5.9 | XY | 2.36 | 25.00 | 10.60 | 4 | OK |
| 4 | crash 13 N pushes jaw A shut, jaws closed: rack A's +y end on the lip at y 31.4, R 12.6 N (the second tie's prop ignored) | lip root at the top wall, rack side (Kt 2.5): b_eff 8.5, t 8.0, lever 5.9 | XY | 2.05 | 25.00 | 12.20 | 3 | OK |
| 5 | added: opening against an obstacle, jaw A, jaws nearly closed: rack A's +y end at y 31.4, R 19.8 N (the second tie's prop ignored) | lip root at the top wall, rack side (Kt 2.5): b_eff 8.5, t 8.0, lever 5.9 | XY | 3.22 | 25.00 | 7.77 | 3 | OK |
| 6 | stall, one jaw blocked: rack A's +y end on the upper piece near slot A's end, R 27.0 N | front plate at the top wall (Kt 1.5): b_eff 7.1, t 5.0, lever 5.1 | XY | 6.99 | 25.00 | 3.58 | 3 | OK |
| 7 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 1.27 MPa) | XY | 5.25 | 25.00 | 4.76 | 3 | OK |
| 8 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 0.86 | 25.00 | 29.17 | 3 | OK |
| 9 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 0.54 | 25.00 | 46.38 | 3 | OK |
| 10 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.18 | 25.00 | 136.41 | 3 | OK |
| 11 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.01 | 25.00 | 1988.82 | 3 | OK |
| 12 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.07 | 25.00 | 350.84 | 3 | OK |
| 13 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.36 | 25.00 | 69.26 | 3 | OK |
| 14 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: second tie's post under the lip (z 35.25..36.75) | 8 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.15 | 25.00 | 166.29 | 3 | OK |
| 15 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.41 | 25.00 | 61.35 | 3 | OK |
| 16 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.29 | 25.00 | 84.81 | 3 | OK |
| 17 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: second post's foot below the web (z 17.85..19.25), the anchor's reaction | 8 x 9.15 net of the Ø3.6 hole (A 62.4, I 383.5), Fx 16.0 N at z 17.60, lift +6.3 N + wedge 16.0 N, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 1.04 | 25.00 | 23.93 | 3 | OK |
| 18 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: second post's foot: shear across it (z 19.25) | A 62.4, Fx 16.3 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY shear | 0.39 | 12.50 | 31.84 | 3 | OK |
| 19 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: M3 x 45 anchor: pull-out from the frame's rail block (10.75 engaged), preload (if any) + wedge lift + lift | screw 172 N, thread cylinder Ø3 x 10.75 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | Z shear (frame) | 1.70 | 6.25 | 3.67 | 3 | OK |
| 20 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: V-ridge: flank bearing on the groove's 45° flank (contact band z 17.25..17.75) | normal 23.1 N on 0.71 x 7.4 (the 0.6 lead-in ignored) [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | bearing | 4.41 | 25.00 | 5.66 | 3 | OK |
| 21 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: V-ridge root at the foot's flats (z 17.85): shear | 1.6 x 7.4, Fx 16.3 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY shear | 2.07 | 12.50 | 6.04 | 3 | OK |
| 22 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: V-ridge root at the foot's flats: the flank force's moment (0.30 Fx, resultant at the printed layer corners, z 17.6) + the wedge's compression, Kt 2.5 | 1.6 x 7.4, M 4.9 N.mm, Kt 2.5 (the 135° root corners taken as sharp 90° ones); compression and bending added in magnitude [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 5.26 | 25.00 | 4.75 | 3 | OK |
| 23 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.05 | 25.00 | 454.59 | 3 | OK |
| 24 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.14 | 25.00 | 184.28 | 3 | OK |
| 25 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.03 | 25.00 | 757.38 | 3 | OK |
| 26 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.04 | 25.00 | 647.41 | 3 | OK |
| 27 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 0 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | Z shear | 0.00 | 6.25 | 5453.36 | 3 | OK |
| 28 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 0 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY comp | 0.01 | 25.00 | 3296.70 | 3 | OK |
| 29 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 1.99 MPa) | XY | 8.25 | 25.00 | 3.03 | 3 | OK |
| 30 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 1.35 | 25.00 | 18.58 | 3 | OK |
| 31 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 0.85 | 25.00 | 29.53 | 3 | OK |
| 32 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.29 | 25.00 | 86.86 | 3 | OK |
| 33 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.02 | 25.00 | 1266.36 | 3 | OK |
| 34 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.11 | 25.00 | 223.40 | 3 | OK |
| 35 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.57 | 25.00 | 44.10 | 3 | OK |
| 36 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: second tie's post under the lip (z 35.25..36.75) | 8 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.24 | 25.00 | 105.89 | 3 | OK |
| 37 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.64 | 25.00 | 39.06 | 3 | OK |
| 38 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.46 | 25.00 | 54.00 | 3 | OK |
| 39 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: second post's foot below the web (z 17.85..19.25), the anchor's reaction | 8 x 9.15 net of the Ø3.6 hole (A 62.4, I 383.5), Fx 25.1 N at z 17.60, lift +9.9 N + wedge 25.1 N, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 1.64 | 25.00 | 15.24 | 3 | OK |
| 40 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: second post's foot: shear across it (z 19.25) | A 62.4, Fx 25.6 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY shear | 0.62 | 12.50 | 20.28 | 3 | OK |
| 41 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: M3 x 45 anchor: pull-out from the frame's rail block (10.75 engaged), preload (if any) + wedge lift + lift | screw 185 N, thread cylinder Ø3 x 10.75 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | Z shear (frame) | 1.83 | 6.25 | 3.42 | 3 | OK |
| 42 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: V-ridge: flank bearing on the groove's 45° flank (contact band z 17.25..17.75) | normal 36.3 N on 0.71 x 7.4 (the 0.6 lead-in ignored) [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | bearing | 6.93 | 25.00 | 3.61 | 3 | OK |
| 43 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: V-ridge root at the foot's flats (z 17.85): shear | 1.6 x 7.4, Fx 25.6 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY shear | 3.25 | 12.50 | 3.85 | 3 | OK |
| 44 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: V-ridge root at the foot's flats: the flank force's moment (0.30 Fx, resultant at the printed layer corners, z 17.6) + the wedge's compression, Kt 2.5 | 1.6 x 7.4, M 7.7 N.mm, Kt 2.5 (the 135° root corners taken as sharp 90° ones); compression and bending added in magnitude [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 8.26 | 25.00 | 3.03 | 3 | OK |
| 45 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.09 | 25.00 | 289.46 | 3 | OK |
| 46 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.21 | 25.00 | 117.34 | 3 | OK |
| 47 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.05 | 25.00 | 482.26 | 3 | OK |
| 48 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.06 | 25.00 | 412.23 | 3 | OK |
| 49 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 0 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | Z shear | 0.00 | 6.25 | 3472.38 | 3 | OK |
| 50 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 0 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY comp | 0.01 | 25.00 | 2099.14 | 3 | OK |
| 51 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 0.49 MPa) | XY | 2.02 | 25.00 | 12.38 | 3 | OK |
| 52 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 0.33 | 25.00 | 75.85 | 3 | OK |
| 53 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 0.21 | 25.00 | 120.59 | 3 | OK |
| 54 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.07 | 25.00 | 354.68 | 3 | OK |
| 55 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.00 | 25.00 | 5170.93 | 3 | OK |
| 56 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.03 | 25.00 | 912.19 | 3 | OK |
| 57 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.14 | 25.00 | 180.07 | 3 | OK |
| 58 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: second tie's post under the lip (z 35.25..36.75) | 8 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.06 | 25.00 | 432.36 | 3 | OK |
| 59 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.16 | 25.00 | 159.50 | 3 | OK |
| 60 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.11 | 25.00 | 220.49 | 3 | OK |
| 61 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: second post's foot below the web (z 17.85..19.25), the anchor's reaction | 8 x 9.15 net of the Ø3.6 hole (A 62.4, I 383.5), Fx 6.1 N at z 17.60, lift +2.4 N + wedge 6.1 N, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 0.40 | 25.00 | 62.21 | 3 | OK |
| 62 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: second post's foot: shear across it (z 19.25) | A 62.4, Fx 6.3 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY shear | 0.15 | 12.50 | 82.80 | 3 | OK |
| 63 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: M3 x 45 anchor: pull-out from the frame's rail block (10.75 engaged), preload (if any) + wedge lift + lift | screw 159 N, thread cylinder Ø3 x 10.75 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | Z shear (frame) | 1.57 | 6.25 | 3.99 | 3 | OK |
| 64 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: V-ridge: flank bearing on the groove's 45° flank (contact band z 17.25..17.75) | normal 8.9 N on 0.71 x 7.4 (the 0.6 lead-in ignored) [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | bearing | 1.70 | 25.00 | 14.73 | 3 | OK |
| 65 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: V-ridge root at the foot's flats (z 17.85): shear | 1.6 x 7.4, Fx 6.3 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY shear | 0.80 | 12.50 | 15.71 | 3 | OK |
| 66 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: V-ridge root at the foot's flats: the flank force's moment (0.30 Fx, resultant at the printed layer corners, z 17.6) + the wedge's compression, Kt 2.5 | 1.6 x 7.4, M 1.9 N.mm, Kt 2.5 (the 135° root corners taken as sharp 90° ones); compression and bending added in magnitude [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 2.02 | 25.00 | 12.36 | 3 | OK |
| 67 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.02 | 25.00 | 1181.93 | 3 | OK |
| 68 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.05 | 25.00 | 479.14 | 3 | OK |
| 69 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.01 | 25.00 | 1969.20 | 3 | OK |
| 70 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.01 | 25.00 | 1683.26 | 3 | OK |
| 71 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 0 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | Z shear | 0.00 | 6.25 | 14178.74 | 3 | OK |
| 72 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 0 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY comp | 0.00 | 25.00 | 8571.41 | 3 | OK |
| 73 | added: opening against an obstacle, jaw B, jaws closed: rack B's end 6.9 from the edge, R 19.8 N: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 6.15 x 5, Kt 2.5 (shear 0.96 MPa) | XY | 4.00 | 25.00 | 6.25 | 3 | OK |
| 74 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 1.27 MPa) | XY | 5.25 | 25.00 | 4.76 | 3 | OK |
| 75 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 2.16 | 25.00 | 11.55 | 3 | OK |
| 76 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 1.36 | 25.00 | 18.41 | 3 | OK |
| 77 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 1.21 | 25.00 | 20.59 | 3 | OK |
| 78 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 3.43 | 25.00 | 7.29 | 3 | OK |
| 79 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 1.90 | 25.00 | 13.16 | 3 | OK |
| 80 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 0.85 | 25.00 | 29.31 | 3 | OK |
| 81 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 2 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | Z shear | 0.03 | 6.25 | 246.88 | 3 | OK |
| 82 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 2 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY comp | 0.17 | 25.00 | 149.24 | 3 | OK |
| 83 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 1.99 MPa) | XY | 8.25 | 25.00 | 3.03 | 3 | OK |
| 84 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 3.40 | 25.00 | 7.36 | 3 | OK |
| 85 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 2.13 | 25.00 | 11.72 | 3 | OK |
| 86 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 1.91 | 25.00 | 13.11 | 3 | OK |
| 87 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 5.39 | 25.00 | 4.64 | 3 | OK |
| 88 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 2.98 | 25.00 | 8.38 | 3 | OK |
| 89 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 1.34 | 25.00 | 18.66 | 3 | OK |
| 90 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 3 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | Z shear | 0.04 | 6.25 | 157.20 | 3 | OK |
| 91 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 3 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY comp | 0.26 | 25.00 | 95.03 | 3 | OK |
| 92 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 0.49 MPa) | XY | 2.02 | 25.00 | 12.38 | 3 | OK |
| 93 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 0.83 | 25.00 | 30.04 | 3 | OK |
| 94 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 0.52 | 25.00 | 47.88 | 3 | OK |
| 95 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.47 | 25.00 | 53.54 | 3 | OK |
| 96 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 1.32 | 25.00 | 18.95 | 3 | OK |
| 97 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 0.73 | 25.00 | 34.23 | 3 | OK |
| 98 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 0.33 | 25.00 | 76.20 | 3 | OK |
| 99 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 1 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | Z shear | 0.01 | 6.25 | 641.89 | 3 | OK |
| 100 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 1 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY comp | 0.06 | 25.00 | 388.04 | 3 | OK |
| 101 | added: opening against an obstacle, jaw A, jaws closed: rack A's end 6.9 from the edge, R 19.8 N: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 6.15 x 5, Kt 2.5 (shear 0.96 MPa) | XY | 4.00 | 25.00 | 6.25 | 3 | OK |
| 102 | stall, one jaw blocked, jaws 44 open: rack B's -y end pushes the lower piece forward (27.0 N at z 12.1): one M2.5 holds it, 108 N | pan head Ø5 on the Ø2.8 teardrop, 13.1 mm2 | XY comp | 8.30 | 25.00 | 3.01 | 3 | OK |
| 103 | stall, one jaw blocked: the same push on the lower piece's plate between the screw (z 3) and the web (z 19.25) | simply supported, b_eff 9.2 x 5 (one-sided spread at the edge) | XY | 2.82 | 25.00 | 8.86 | 3 | OK |
| 104 | yaw stall 7.1 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 25 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws closed | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 1.69 | 12.50 | 7.38 | 3 | OK |
| 105 | yaw stall 7.1 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 25 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws 44 open | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 2.53 | 12.50 | 4.93 | 3 | OK |
| 106 | hand push 5 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 18 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws closed | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 1.19 | 12.50 | 10.48 | 3 | OK |
| 107 | hand push 5 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 18 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws 44 open | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 1.78 | 12.50 | 7.00 | 3 | OK |
| 108 | rack A lift: separating 7.9 N + grip twist 410 N.mm -> 13.8 N at the rack end | top wall between the lip and the front plate, span 12.5, b 25 x 3 | XY | 1.44 | 25.00 | 17.34 | 3 | OK |
| 109 | USB tug 10 N tips the camera mount back: 53 N on the top wall's rear edge | 50 x 1 mm contact | XY | 1.06 | 25.00 | 23.67 | 3 | OK |
| 110 | anchor M3 x 45 driven snug: Ø7 x 0.5 washer under the socket head on the top wall, preload 150 N (sustained) | 28.8 mm2 round the Ø3.4 teardrop (washer OD; BUILD_GUIDE §1) | XY comp | 5.21 | 25.00 | 4.80 | 4 | OK |
| 111 | anchor preload 150 N through the stack (sustained): the 8 x 8 post round its Ø3.6 hole | 54 mm2 (the full-depth part only; the 45-degree part ignored) | XY comp | 2.79 | 25.00 | 8.97 | 4 | OK |
| 112 | anchor preload 150 N (sustained): M3 x 45 pull-out from the frame's rail block | thread cylinder Ø3 x 10.75 (Ø2.7 x 14 pilot) | Z shear (frame) | 1.48 | 6.25 | 4.22 | 4 | OK |
| 113 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 1.71 | 25.00 | 14.66 | 2 | OK |
| 114 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 1.07 | 25.00 | 23.30 | 2 | OK |
| 115 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.36 | 25.00 | 68.54 | 2 | OK |
| 116 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.03 | 25.00 | 999.27 | 2 | OK |
| 117 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.14 | 25.00 | 176.28 | 2 | OK |
| 118 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.72 | 25.00 | 34.80 | 2 | OK |
| 119 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: second tie's post under the lip (z 35.25..36.75) | 8 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.30 | 25.00 | 83.55 | 2 | OK |
| 120 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.81 | 25.00 | 30.82 | 2 | OK |
| 121 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.59 | 25.00 | 42.61 | 2 | OK |
| 122 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: second post's foot below the web (z 17.85..19.25), the anchor's reaction | 8 x 9.15 net of the Ø3.6 hole (A 62.4, I 383.5), Fx 31.8 N at z 17.60, lift +12.5 N + wedge 31.8 N, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 2.08 | 25.00 | 12.02 | 2 | OK |
| 123 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: second post's foot: shear across it (z 19.25) | A 62.4, Fx 32.5 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY shear | 0.78 | 12.50 | 16.00 | 2 | OK |
| 124 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: M3 x 45 anchor: pull-out from the frame's rail block (10.75 engaged), preload (if any) + wedge lift + lift | screw 194 N, thread cylinder Ø3 x 10.75 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | Z shear (frame) | 1.92 | 6.25 | 3.26 | 2 | OK |
| 125 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: V-ridge: flank bearing on the groove's 45° flank (contact band z 17.25..17.75) | normal 46.0 N on 0.71 x 7.4 (the 0.6 lead-in ignored) [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | bearing | 8.78 | 25.00 | 2.85 | 2 | OK |
| 126 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: V-ridge root at the foot's flats (z 17.85): shear | 1.6 x 7.4, Fx 32.5 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY shear | 4.12 | 12.50 | 3.04 | 2 | OK |
| 127 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: V-ridge root at the foot's flats: the flank force's moment (0.30 Fx, resultant at the printed layer corners, z 17.6) + the wedge's compression, Kt 2.5 | 1.6 x 7.4, M 9.7 N.mm, Kt 2.5 (the 135° root corners taken as sharp 90° ones); compression and bending added in magnitude [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 10.47 | 25.00 | 2.39 | 2 | OK |
| 128 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.11 | 25.00 | 228.41 | 2 | OK |
| 129 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.27 | 25.00 | 92.59 | 2 | OK |
| 130 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.07 | 25.00 | 380.54 | 2 | OK |
| 131 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 0.08 | 25.00 | 325.29 | 2 | OK |
| 132 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 0 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | Z shear | 0.00 | 6.25 | 2740.01 | 2 | OK |
| 133 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 0 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY comp | 0.02 | 25.00 | 1656.41 | 2 | OK |
| 134 | spec §8 proof 1: jaw B pushed towards the other, R 34.2 N: plate strip at the tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 2.52 MPa) | XY | 10.45 | 25.00 | 2.39 | 2 | OK |
| 135 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 4.31 | 25.00 | 5.80 | 2 | OK |
| 136 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 2.70 | 25.00 | 9.25 | 2 | OK |
| 137 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; foot held by the ridge in the groove] | XY | 2.42 | 25.00 | 10.35 | 2 | OK |
| 138 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 6.83 | 25.00 | 3.66 | 2 | OK |
| 139 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 3.78 | 25.00 | 6.61 | 2 | OK |
| 140 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY | 1.70 | 25.00 | 14.73 | 2 | OK |
| 141 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 4 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | Z shear | 0.05 | 6.25 | 124.04 | 2 | OK |
| 142 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 4 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; foot held by the ridge in the groove] | XY comp | 0.33 | 25.00 | 74.99 | 2 | OK |
| 143 | spec §8 proof 1: jaw A pushed towards the other, R 34.2 N: plate strip at the tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 2.52 MPa) | XY | 10.45 | 25.00 | 2.39 | 2 | OK |
| 144 | spec §8 proof 1: 32 N pulls a jaw away, jaws 30 open: rack A's -y end at the lip's end, R 34.2 N | lip root at the top wall, rack side (Kt 2.5): b_eff 7.9, t 8.0, lever 5.9 | XY | 5.98 | 25.00 | 4.18 | 2 | OK |
| 145 | spec §8 proof 1: the same, rack A's +y end on the upper piece near slot A's end | front plate at the top wall (Kt 1.5): b_eff 7.1, t 5.0, lever 5.1 | XY | 8.86 | 25.00 | 2.82 | 2 | OK |
| 146 | spec §8 proof 2: 10.7 N on jaw B's tip towards the wrist, jaws closed | strip 11.75 x 5 | Z | 2.55 | 12.50 | 4.90 | 2 | OK |
| 147 | spec §8 proof 2: 10.7 N on jaw B's tip towards the wrist, jaws 44 open | strip 11.75 x 5 | Z | 3.82 | 12.50 | 3.27 | 2 | OK |

Information rows (not in the verdict):

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 148 | info: opening stall on jaw B, upper piece WITHOUT the second tie (round 2's model) | beside slot A's V apex (z 43.4): b 21.0 x 5, lever 26.2, Kt 1.5 | XY | 12.12 | 25.00 | 2.06 | 3 | **FAIL** |
| 149 | info: opening stall on jaw B, upper piece WITHOUT the second tie (round 2's model) | top-wall junction (z 48.5): b 25.5 x 5, lever 31.3, Kt 1.5 | XY | 11.94 | 25.00 | 2.09 | 3 | **FAIL** |
| 150 | info, bound: opening stall on jaw B with the corners rigidly coupled: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm held along z, corners rigid; foot held by the ridge in the groove] | XY | 0.16 | 25.00 | 153.91 | 3 | OK |
| 151 | info, bound: opening stall on jaw B with the corners rigidly coupled: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners rigid; foot held by the ridge in the groove] | XY | 0.34 | 25.00 | 72.69 | 3 | OK |
| 152 | info: anchor preload seats the ridge, bound: all 150 N on the two 45° flanks (sustained; seating, self-limiting) | normal 106 N per flank on 0.71 x 7.4 | bearing | 20.27 | 25.00 | 1.23 | 4 | **FAIL** |

**Lowest SF 3.01 (required 3), row 102:** one M2.5 pan head under rack B's push on the lower piece (unchanged since
round 3). Next: the plate strips at the ties' webs 3.03 (rows 29, 83) and the ridge's root 3.03 (row 44).

**Information rows** (not in the verdict):
- 148–149: the upper piece without the second tie (round 2's model), 2.06 / 2.09.
- 150–151: the bound with the zone corners rigidly coupled.
- **152: the anchor's preload on the two flanks, 1.23 against 4 sustained.** If the ridge reaches the flanks before the
  top wall lands, the snug preload seats it there. That bound puts all 150 N on the two 0.71 mm flank bands. It is
  information, not a load path: local crushing of the frame's layer corners under the clamp *is* the seating. It is
  self-limiting (the top wall lands on the bulkhead within the 0.1 the flats stand clear), it can only close the
  ridge's play, never open it, and it only lowers a preload that nothing relies on.

## Play at the ridge

Free slide before the flank bears (the preload gone), both reversed pushes, all variants:

| Play (mm) | 0 | 0.025 | 0.04 | 0.05 | 0.075 | 0.1 |
|---|---|---|---|---|---|---|
| Lowest SF | 3.03 | 3.72 | 3.41 | 2.83 | 1.99 | 1.54 |

(At 0.025 the ridge row eases because less of the push reaches it; from 0.04 the top wall behind the lip governs again.)

- **Nominal print: zero play.** The CAD's 0.1 per flank equals the 0.1 that the frame's mid-layer slicing puts the layer
  corners inside the flank.
- **What can move it: the frame's bulkhead top, z 48.5, lies exactly on a slice plane** (layer 48.4–48.6 is sliced at
  48.5). It can print 0.1 high or low, and the cover's top wall sits on it.
  - **0.1 high:** the cover rides 0.1 up, the ridge has 0.1 of play → 1.54.
  - **0.1 low:** the ridge holds the cover's top wall 0.1 off the bulkhead; the top screws then pull it down onto the
    ridge (no play).
- **BUILD_GUIDE §4 step 9** checks both before any screw goes in:
  - a 0.1 feeler must not enter between the top wall and the bulkhead (the ridge holding the cover up);
  - a 0.15 feeler must not enter under the post's foot flats, whose design gap is 0.1 (play ≤ about 0.05, SF ≥ 2.83).
- **If the second check fails,** the fix is in CAD: `VSEAT_CLR` 0.1 → 0 in `claw_frame.py` (the reviewer's original
  line-to-line flanks) lowers the ridge 0.1 against the cover, and both models follow it.

## Proof test (spec §8)

- **The loads still match the design cases.**
  - Step 1's 32 N push towards the other jaw is 1.5 × the opening stall; at 30 mm open, R is 34.2 N.
  - The 32 N pull is 1.5 × the one-jaw stall: lip root 4.18, front plate at the top wall 2.82.
  - Step 2's 10.7 N sideways: strip under slot B 4.90 / 3.27.
- **Step 1's push on jaw B is now safe to run.** Every proof row ≥ 2.39 (req 2): the plate strips at the ties' webs and
  the ridge's root (2.39), the flank bearing 2.85, the M3 pull-out 3.26. The top wall behind the lip is 14.66.
- **Wording:** "the anchored second post and its M3 × 45 (still tight)" should read "the second post's ridge still seated
  in the frame's groove, and the M3 × 45 (with its washer) still tight".

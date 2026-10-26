VERDICT: NEEDS_TEST

# Strength check (round 7, CAD engineer's self-check): 20261026-arm-claw-cover

cad-engineer · 2026-10-26 · `python3 jobs/20261026-arm-claw-cover/strength_calc.py` (plain python3, from the project
root, about 60 s). **This is the designer's own check of the round-7 change, not an independent review; an independent
review follows.** The script is the round 6 reviewer's. This round changes only the hardware it reads (see its header)
and re-runs it. The round 6 independent review is kept below as history.

## Verdict

**Every verdict row passes. NEEDS_TEST only because the allowables are placeholders** (no library row for PETG).

- **The two round-6 failures pass now:**

  | Row | What (sustained, req 4) | Round 6 | Round 7 |
  |---|---|---|---|
  | 119 | top screws (no camera): M3 × 14 pan head on the Ø7 × 0.5 washer, 150 N snug preload, on the top wall (28.8 mm²) | 2.49 (bare M3 × 10, 14.9 mm²) | **4.80** |
  | 120 | front M2.5 × 16 pan heads on the Ø6 × 0.5 washer, 100 N snug preload, on the front plate (21.7 mm²) | 3.26 (bare head, 13.1 mm²) | **5.42** |

  The other sustained rows: the anchor's washer 4.80 (row 116), the post round its hole 8.97 (row 117), the anchor's
  pull-out 4.15 (row 118). The cyclic row is 10.60.
- **Lowest verdict row: 3.03** (rows 30 and 87, req 3): the plate strips at the ties' webs under the opening stall.
  Unchanged since round 6.
- **The M2.5 under the one-jaw stall (row 108).** At z 2.5 the screw takes 130 N (108 N at z 3). On the Ø6 washer that is
  **4.17** (req 3). It was 3.01 on the bare head at z 3, so the move and the washer together raise it.
- **Proof rows (req 2):** lowest 2.39, the plate strips (rows 143 / 153). The ridge's bearing is 2.50 (row 134).
- **Information rows (not the verdict):**
  - the round-6 bare heads, kept for reference: 2.49 (row 165) and 3.26 (row 166);
  - **the camera case:** the bare M3 × 18 button heads on the camera mount's pad give **2.64** (row 167, req 4). With a
    Ø7 × 0.5 washer under each it is 4.80 (row 168). That is the camera mount's row, not this part's; the design
    review's item 7b proposes the washer;
  - the forced closure of the proud top wall: with the washer's Ø7 in b_eff, the same displacement-controlled numbers
    (rows 169–172), relaxing.

## What changed in the calculation

| Item | Round 6 | Round 7 |
|---|---|---|
| Top screws (no camera) | M3 × 10 pan head, bare: Ø5.6 on the Ø3.4 teardrop, 14.9 mm² | M3 × 14 pan head + ISO 7089 Ø7 × 0.5 washer: 28.8 mm² (`A_M3_TOP`) |
| Front screws | M2.5 × 16 pan head at z 3, bare: 13.1 mm² | at **z 2.5**, + DIN 125 Ø6 × 0.5 washer: 21.7 mm² (`A_BRG`) |
| M2.5 engaged in the frame | 11 | **10.5** (16 − 5 plate − 0.5 washer) |
| One-jaw stall on one M2.5 | 27.0 N × 12.05 / 3 = 108 N | 27.0 N × 12.05 / 2.5 = **130 N** |
| Top joint's service tension rows (10, 33, 56, 80, 90, 100, 123, 146) | on the bare pan head | on the Ø7 washer |
| Forced-closure info rows | b_eff 2 L + 5.6 = 20.8 | 2 L + 7 = 22.2 |

The cover's frame model, the seat stack, the play modes, the load cases and the allowables are unchanged. The front
screws' frame-model node follows `FRONT_SCREWS` to z 2.5, which moves nothing over 0.1 MPa.

## Clearances (exact solids, `claw_sequence_check` placements, gaps 0–44 every 1 mm)

| Item | Clearance | Where |
|---|---|---|
| Slot A's front edge (0.3 chamfer) to jaw A | **0.211** | gap 0, at the chamfer's back edge (x 39.55, z 38.25); was 0.148 |
| Slot B's front edge (0.3 chamfer) to jaw B | **0.211** | the same, mirrored; was 0.148 |
| Second post + ridge + foot | 0.240 / 0.312 | jaw A / jaw B |
| Lip | 0.240 / 0.312 | |
| First tie | 0.240 / 1.150 | |
| Frame rail block | 0.250 | jaw B |
| Front Ø6 washers under jaw B's neck | **0.500** | 0.26 with the worst standing (0.239) |
| Front M2.5 heads (Ø5 × 1.75, on the washer) | 1.000 | jaw B |
| Top Ø7 washers / M3 × 14 heads | 12.77 / 13.58 | jaw A |

**A 0.3 chamfer gives 0.21, not the review's ≥ 0.25.** The slot's side is only 0.25 from the neck's flat face, and the
kink fillet starts 1.24 behind NECK_X1. So no chamfer shorter than about 0.75 can reach 0.25. The task's ≥ 0.2 is met.

**A pre-existing note, not part of round 7.** The r 2 corner fillet (front plate / top wall, y ≥ 9) is 0.187 from rack A's
2 mm 45° edge chamfer. The closest point is the fillet's tangent line on rack A's guide plane, z 48.5. Analytically it is
(2.0 − 1.75)/√2 = 0.177: the 0.25 gap along the guide, measured across the two 45° faces. It has been unchanged since
round 3, and the round 6 review's table does not list it.

## Results (from `strength_calc.py`, verbatim; each frame-model row is the worse of 'locked' and the worst accepted play 0.029 mm)

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | stall, one jaw blocked, jaws 44 open: rack A's -y end at the lip's end, R 27.0 N (the first tie's prop ignored) | lip root at the top wall, rack side (Kt 2.5): b_eff 7.9, t 8.0, lever 5.9 | XY | 4.72 | 25.00 | 5.30 | 3 | OK |
| 2 | stall, one jaw blocked, jaws closed: rack A's -y end at y -25.1, R 19.8 N | lip root at the top wall, rack side (Kt 2.5): b_eff 13.8, t 8.0, lever 5.9 | XY | 1.98 | 25.00 | 12.63 | 3 | OK |
| 3 | stall, both jaws (cyclic), jaws 44 open: R 13.5 N at the lip's end | lip root at the top wall, rack side (Kt 2.5): b_eff 7.9, t 8.0, lever 5.9 | XY | 2.36 | 25.00 | 10.60 | 4 | OK |
| 4 | crash 13 N pushes jaw A shut, jaws closed: rack A's +y end on the lip at y 31.4, R 12.6 N (the second tie's prop ignored) | lip root at the top wall, rack side (Kt 2.5): b_eff 8.5, t 8.0, lever 5.9 | XY | 2.05 | 25.00 | 12.20 | 3 | OK |
| 5 | added: opening against an obstacle, jaw A, jaws nearly closed: rack A's +y end at y 31.4, R 19.8 N (the second tie's prop ignored) | lip root at the top wall, rack side (Kt 2.5): b_eff 8.5, t 8.0, lever 5.9 | XY | 3.22 | 25.00 | 7.77 | 3 | OK |
| 6 | stall, one jaw blocked: rack A's +y end on the upper piece near slot A's end, R 27.0 N | front plate at the top wall (Kt 1.5): b_eff 7.1, t 5.0, lever 5.1 | XY | 6.99 | 25.00 | 3.58 | 3 | OK |
| 7 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 1.27 MPa) | XY | 5.25 | 25.00 | 4.76 | 3 | OK |
| 8 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 5.21 | 25.00 | 4.79 | 3 | OK |
| 9 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 3.28 | 25.00 | 7.63 | 3 | OK |
| 10 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: top M3 head on the top wall, the joint's own tension (no preload) | T 21 N (y 14: 21, y -23: 1) on the M3 x 14 pan head on the Ø7 x 0.5 washer, 28.8 mm2 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.73 | 25.00 | 34.17 | 3 | OK |
| 11 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.06 | 25.00 | 23.66 | 3 | OK |
| 12 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.07 | 25.00 | 335.50 | 3 | OK |
| 13 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.41 | 25.00 | 60.69 | 3 | OK |
| 14 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.10 | 25.00 | 11.91 | 3 | OK |
| 15 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: second tie's post under the lip (z 35.25..36.75) | 8 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.83 | 25.00 | 30.07 | 3 | OK |
| 16 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.47 | 25.00 | 10.14 | 3 | OK |
| 17 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.82 | 25.00 | 13.76 | 3 | OK |
| 18 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: second post's foot below the web (z 18.05..19.25), the anchor's reaction | 8 x 8.96 net of the Ø3.6 hole (A 60.7, I 373.5), Fx 8.7 N at z 17.70, lift +38.5 N + wedge 8.7 N, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.14 | 25.00 | 21.92 | 3 | OK |
| 19 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: second post's foot: shear across it (z 19.25) | A 60.7, Fx 16.4 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY shear | 0.40 | 12.50 | 30.88 | 3 | OK |
| 20 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: M3 x 45 anchor: pull-out from the frame's rail block (10.56 engaged), preload (if any) + wedge lift + lift | screw 172 N, thread cylinder Ø3 x 10.56 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | Z shear (frame) | 1.73 | 6.25 | 3.61 | 3 | OK |
| 21 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: V-ridge: flank bearing on the groove's 45° flank (contact band z 17.35..17.80: the seated tip, after the anchor's least crush, to the printed top corner) | normal 23.2 N on 0.63 x 7.3 (the 0.7 lead-in ignored) [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | bearing | 5.03 | 25.00 | 4.97 | 3 | OK |
| 22 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: V-ridge root at the foot's flats (z 18.05): shear | 2.0 x 7.3, Fx 16.4 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY shear | 1.68 | 12.50 | 7.43 | 3 | OK |
| 23 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: V-ridge root at the foot's flats (printed, x 14.35..16.35): the flank force's moment (0.50 Fx, resultant at the two upper corners, z 17.7) + the wedge's compression, Kt 1.7 | 2.0 x 7.3, M 8.2 N.mm, Kt 1.7 (bead-filled 135° root corners); compression and bending added in magnitude [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 3.98 | 25.00 | 6.28 | 3 | OK |
| 24 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.34 | 25.00 | 74.47 | 3 | OK |
| 25 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.83 | 25.00 | 30.19 | 3 | OK |
| 26 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.20 | 25.00 | 124.08 | 3 | OK |
| 27 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.24 | 25.00 | 105.16 | 3 | OK |
| 28 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: M2.5 x 16 at z 2.5: pull-out from the frame (10.5 engaged) | screw force 1 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | Z shear | 0.01 | 6.25 | 871.52 | 3 | OK |
| 29 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: same M2.5: its head on the cover's front plate | Ø6 x 0.5 washer under the Ø5 pan head on the Ø2.8 teardrop, 21.7 mm2; screw force 1 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.03 | 25.00 | 917.16 | 3 | OK |
| 30 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 1.99 MPa) | XY | 8.25 | 25.00 | 3.03 | 3 | OK |
| 31 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 5.70 | 25.00 | 4.38 | 3 | OK |
| 32 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 3.59 | 25.00 | 6.97 | 3 | OK |
| 33 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: top M3 head on the top wall, the joint's own tension (no preload) | T 23 N (y 14: 23, y -23: 1) on the M3 x 14 pan head on the Ø7 x 0.5 washer, 28.8 mm2 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.80 | 25.00 | 31.24 | 3 | OK |
| 34 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.16 | 25.00 | 21.50 | 3 | OK |
| 35 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.08 | 25.00 | 305.78 | 3 | OK |
| 36 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.45 | 25.00 | 55.16 | 3 | OK |
| 37 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.31 | 25.00 | 10.83 | 3 | OK |
| 38 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: second tie's post under the lip (z 35.25..36.75) | 8 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.92 | 25.00 | 27.19 | 3 | OK |
| 39 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.70 | 25.00 | 9.26 | 3 | OK |
| 40 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.99 | 25.00 | 12.59 | 3 | OK |
| 41 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: second post's foot below the web (z 18.05..19.25), the anchor's reaction | 8 x 8.96 net of the Ø3.6 hole (A 60.7, I 373.5), Fx 17.9 N at z 17.70, lift +42.1 N + wedge 17.9 N, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.73 | 25.00 | 14.45 | 3 | OK |
| 42 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: second post's foot: shear across it (z 19.25) | A 60.7, Fx 25.7 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY shear | 0.64 | 12.50 | 19.66 | 3 | OK |
| 43 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: M3 x 45 anchor: pull-out from the frame's rail block (10.56 engaged), preload (if any) + wedge lift + lift | screw 185 N, thread cylinder Ø3 x 10.56 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | Z shear (frame) | 1.86 | 6.25 | 3.36 | 3 | OK |
| 44 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: V-ridge: flank bearing on the groove's 45° flank (contact band z 17.35..17.80: the seated tip, after the anchor's least crush, to the printed top corner) | normal 36.4 N on 0.63 x 7.3 (the 0.7 lead-in ignored) [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | bearing | 7.90 | 25.00 | 3.16 | 3 | OK |
| 45 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: V-ridge root at the foot's flats (z 18.05): shear | 2.0 x 7.3, Fx 25.7 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY shear | 2.64 | 12.50 | 4.73 | 3 | OK |
| 46 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: V-ridge root at the foot's flats (printed, x 14.35..16.35): the flank force's moment (0.50 Fx, resultant at the two upper corners, z 17.7) + the wedge's compression, Kt 1.7 | 2.0 x 7.3, M 12.9 N.mm, Kt 1.7 (bead-filled 135° root corners); compression and bending added in magnitude [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 6.25 | 25.00 | 4.00 | 3 | OK |
| 47 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.37 | 25.00 | 68.10 | 3 | OK |
| 48 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.91 | 25.00 | 27.60 | 3 | OK |
| 49 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.22 | 25.00 | 113.46 | 3 | OK |
| 50 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.26 | 25.00 | 96.17 | 3 | OK |
| 51 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: M2.5 x 16 at z 2.5: pull-out from the frame (10.5 engaged) | screw force 1 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | Z shear | 0.01 | 6.25 | 797.07 | 3 | OK |
| 52 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: same M2.5: its head on the cover's front plate | Ø6 x 0.5 washer under the Ø5 pan head on the Ø2.8 teardrop, 21.7 mm2; screw force 1 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.03 | 25.00 | 838.81 | 3 | OK |
| 53 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 0.49 MPa) | XY | 2.02 | 25.00 | 12.38 | 3 | OK |
| 54 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 4.45 | 25.00 | 5.61 | 3 | OK |
| 55 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.51 | 25.00 | 9.97 | 3 | OK |
| 56 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: top M3 head on the top wall, the joint's own tension (no preload) | T 16 N (y 14: 16, y -23: 1) on the M3 x 14 pan head on the Ø7 x 0.5 washer, 28.8 mm2 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.56 | 25.00 | 44.67 | 3 | OK |
| 57 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.92 | 25.00 | 27.29 | 3 | OK |
| 58 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.07 | 25.00 | 378.96 | 3 | OK |
| 59 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.36 | 25.00 | 69.46 | 3 | OK |
| 60 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.84 | 25.00 | 13.60 | 3 | OK |
| 61 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: second tie's post under the lip (z 35.25..36.75) | 8 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.62 | 25.00 | 40.08 | 3 | OK |
| 62 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.87 | 25.00 | 13.38 | 3 | OK |
| 63 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.61 | 25.00 | 15.51 | 3 | OK |
| 64 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: second post's foot below the web (z 18.05..19.25), the anchor's reaction | 8 x 8.96 net of the Ø3.6 hole (A 60.7, I 373.5), Fx 0.0 N at z 17.70, lift +29.6 N + wedge 0.0 N, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.49 | 25.00 | 51.24 | 3 | OK |
| 65 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: second post's foot: shear across it (z 19.25) | A 60.7, Fx 6.3 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY shear | 0.16 | 12.50 | 80.30 | 3 | OK |
| 66 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: M3 x 45 anchor: pull-out from the frame's rail block (10.56 engaged), preload (if any) + wedge lift + lift | screw 159 N, thread cylinder Ø3 x 10.56 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | Z shear (frame) | 1.59 | 6.25 | 3.92 | 3 | OK |
| 67 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: V-ridge: flank bearing on the groove's 45° flank (contact band z 17.35..17.80: the seated tip, after the anchor's least crush, to the printed top corner) | normal 8.9 N on 0.63 x 7.3 (the 0.7 lead-in ignored) [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | bearing | 1.93 | 25.00 | 12.92 | 3 | OK |
| 68 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: V-ridge root at the foot's flats (z 18.05): shear | 2.0 x 7.3, Fx 6.3 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY shear | 0.65 | 12.50 | 19.31 | 3 | OK |
| 69 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: V-ridge root at the foot's flats (printed, x 14.35..16.35): the flank force's moment (0.50 Fx, resultant at the two upper corners, z 17.7) + the wedge's compression, Kt 1.7 | 2.0 x 7.3, M 3.1 N.mm, Kt 1.7 (bead-filled 135° root corners); compression and bending added in magnitude [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 1.53 | 25.00 | 16.32 | 3 | OK |
| 70 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.30 | 25.00 | 84.53 | 3 | OK |
| 71 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.73 | 25.00 | 34.28 | 3 | OK |
| 72 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.18 | 25.00 | 140.86 | 3 | OK |
| 73 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.21 | 25.00 | 118.56 | 3 | OK |
| 74 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: M2.5 x 16 at z 2.5: pull-out from the frame (10.5 engaged) | screw force 1 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | Z shear | 0.01 | 6.25 | 982.62 | 3 | OK |
| 75 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: same M2.5: its head on the cover's front plate | Ø6 x 0.5 washer under the Ø5 pan head on the Ø2.8 teardrop, 21.7 mm2; screw force 1 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.02 | 25.00 | 1034.07 | 3 | OK |
| 76 | added: opening against an obstacle, jaw B, jaws closed: rack B's end 6.9 from the edge, R 19.8 N: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 6.15 x 5, Kt 2.5 (shear 0.96 MPa) | XY | 4.00 | 25.00 | 6.25 | 3 | OK |
| 77 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 1.27 MPa) | XY | 5.25 | 25.00 | 4.76 | 3 | OK |
| 78 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.25 | 25.00 | 11.10 | 3 | OK |
| 79 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 1.37 | 25.00 | 18.29 | 3 | OK |
| 80 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: top M3 head on the top wall, the joint's own tension (no preload) | T 9 N (y 14: 4, y -23: 9) on the M3 x 14 pan head on the Ø7 x 0.5 washer, 28.8 mm2 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY comp | 0.30 | 25.00 | 82.64 | 3 | OK |
| 81 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 1.22 | 25.00 | 20.44 | 3 | OK |
| 82 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 3.53 | 25.00 | 7.08 | 3 | OK |
| 83 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.93 | 25.00 | 12.96 | 3 | OK |
| 84 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.88 | 25.00 | 28.25 | 3 | OK |
| 85 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: M2.5 x 16 at z 2.5: pull-out from the frame (10.5 engaged) | screw force 2 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | Z shear | 0.03 | 6.25 | 234.16 | 3 | OK |
| 86 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: same M2.5: its head on the cover's front plate | Ø6 x 0.5 washer under the Ø5 pan head on the Ø2.8 teardrop, 21.7 mm2; screw force 2 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.10 | 25.00 | 246.42 | 3 | OK |
| 87 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 1.99 MPa) | XY | 8.25 | 25.00 | 3.03 | 3 | OK |
| 88 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 3.54 | 25.00 | 7.07 | 3 | OK |
| 89 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 2.15 | 25.00 | 11.64 | 3 | OK |
| 90 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: top M3 head on the top wall, the joint's own tension (no preload) | T 14 N (y 14: 6, y -23: 14) on the M3 x 14 pan head on the Ø7 x 0.5 washer, 28.8 mm2 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY comp | 0.48 | 25.00 | 52.62 | 3 | OK |
| 91 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 1.92 | 25.00 | 13.02 | 3 | OK |
| 92 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 5.54 | 25.00 | 4.51 | 3 | OK |
| 93 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 3.03 | 25.00 | 8.25 | 3 | OK |
| 94 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.39 | 25.00 | 17.99 | 3 | OK |
| 95 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: M2.5 x 16 at z 2.5: pull-out from the frame (10.5 engaged) | screw force 3 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | Z shear | 0.04 | 6.25 | 149.10 | 3 | OK |
| 96 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: same M2.5: its head on the cover's front plate | Ø6 x 0.5 washer under the Ø5 pan head on the Ø2.8 teardrop, 21.7 mm2; screw force 3 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.16 | 25.00 | 156.90 | 3 | OK |
| 97 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 0.49 MPa) | XY | 2.02 | 25.00 | 12.38 | 3 | OK |
| 98 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.87 | 25.00 | 28.86 | 3 | OK |
| 99 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 0.53 | 25.00 | 47.54 | 3 | OK |
| 100 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: top M3 head on the top wall, the joint's own tension (no preload) | T 3 N (y 14: 1, y -23: 3) on the M3 x 14 pan head on the Ø7 x 0.5 washer, 28.8 mm2 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY comp | 0.12 | 25.00 | 214.86 | 3 | OK |
| 101 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 0.47 | 25.00 | 53.15 | 3 | OK |
| 102 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.36 | 25.00 | 18.42 | 3 | OK |
| 103 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.74 | 25.00 | 33.70 | 3 | OK |
| 104 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.34 | 25.00 | 73.46 | 3 | OK |
| 105 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: M2.5 x 16 at z 2.5: pull-out from the frame (10.5 engaged) | screw force 1 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | Z shear | 0.01 | 6.25 | 608.81 | 3 | OK |
| 106 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: same M2.5: its head on the cover's front plate | Ø6 x 0.5 washer under the Ø5 pan head on the Ø2.8 teardrop, 21.7 mm2; screw force 1 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.04 | 25.00 | 640.69 | 3 | OK |
| 107 | added: opening against an obstacle, jaw A, jaws closed: rack A's end 6.9 from the edge, R 19.8 N: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 6.15 x 5, Kt 2.5 (shear 0.96 MPa) | XY | 4.00 | 25.00 | 6.25 | 3 | OK |
| 108 | stall, one jaw blocked, jaws 44 open: rack B's -y end pushes the lower piece forward (27.0 N at z 12.1): one M2.5 at z 2.5 holds it, 130 N | Ø6 x 0.5 washer under the Ø5 pan head on the Ø2.8 teardrop, 21.7 mm2 | XY comp | 6.00 | 25.00 | 4.17 | 3 | OK |
| 109 | stall, one jaw blocked: the same push on the lower piece's plate between the screw (z 2.5) and the web (z 19.25) | simply supported, b_eff 9.2 x 5 (one-sided spread at the edge) | XY | 2.89 | 25.00 | 8.65 | 3 | OK |
| 110 | yaw stall 7.1 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 25 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws closed | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 1.69 | 12.50 | 7.38 | 3 | OK |
| 111 | yaw stall 7.1 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 25 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws 44 open | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 2.53 | 12.50 | 4.93 | 3 | OK |
| 112 | hand push 5 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 18 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws closed | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 1.19 | 12.50 | 10.48 | 3 | OK |
| 113 | hand push 5 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 18 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws 44 open | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 1.78 | 12.50 | 7.00 | 3 | OK |
| 114 | rack A lift: separating 7.9 N + grip twist 410 N.mm -> 13.8 N at the rack end | top wall between the lip and the front plate, span 12.5, b 25 x 3 | XY | 1.44 | 25.00 | 17.34 | 3 | OK |
| 115 | USB tug 10 N tips the camera mount back: 53 N on the top wall's rear edge | 50 x 1 mm contact | XY | 1.06 | 25.00 | 23.67 | 3 | OK |
| 116 | anchor M3 x 45 driven snug: Ø7 x 0.5 washer under the socket head on the top wall, preload 150 N (sustained) | 28.8 mm2 round the Ø3.4 teardrop (washer OD; BUILD_GUIDE §1) | XY comp | 5.21 | 25.00 | 4.80 | 4 | OK |
| 117 | anchor preload 150 N through the stack (sustained): the 8 x 8 post round its Ø3.6 hole | 54 mm2 (the full-depth part only; the 45-degree part ignored) | XY comp | 2.79 | 25.00 | 8.97 | 4 | OK |
| 118 | anchor preload 150 N (sustained): M3 x 45 pull-out from the frame's rail block, the top wall left 0.339 proud after seating (worst-case stack) | thread cylinder Ø3 x 10.56 (Ø2.7 x 14 pilot; 10.75 in CAD) | Z shear (frame) | 1.51 | 6.25 | 4.15 | 4 | OK |
| 119 | top screws (no camera), M3 x 14 pan head on the Ø7 x 0.5 washer, driven snug, 150 N preload (sustained): bearing on the top wall | 28.8 mm2 round the Ø3.4 teardrop (washer OD; BUILD_GUIDE §1) | XY comp | 5.21 | 25.00 | 4.80 | 4 | OK |
| 120 | front M2.5 x 16 pan heads, Ø6 x 0.5 washer under the Ø5 pan head, driven snug, 100 N preload (sustained): bearing on the front plate | 21.7 mm2 round the Ø2.8 teardrop | XY comp | 4.61 | 25.00 | 5.42 | 4 | OK |
| 121 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 6.07 | 25.00 | 4.12 | 2 | OK |
| 122 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 3.81 | 25.00 | 6.56 | 2 | OK |
| 123 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: top M3 head on the top wall, the joint's own tension (no preload) | T 24 N (y 14: 24, y -23: 1) on the M3 x 14 pan head on the Ø7 x 0.5 washer, 28.8 mm2 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.85 | 25.00 | 29.39 | 2 | OK |
| 124 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.24 | 25.00 | 20.14 | 2 | OK |
| 125 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.09 | 25.00 | 287.06 | 2 | OK |
| 126 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.48 | 25.00 | 51.69 | 2 | OK |
| 127 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.46 | 25.00 | 10.15 | 2 | OK |
| 128 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: second tie's post under the lip (z 35.25..36.75) | 8 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.98 | 25.00 | 25.40 | 2 | OK |
| 129 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.87 | 25.00 | 8.70 | 2 | OK |
| 130 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.11 | 25.00 | 11.85 | 2 | OK |
| 131 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: second post's foot below the web (z 18.05..19.25), the anchor's reaction | 8 x 8.96 net of the Ø3.6 hole (A 60.7, I 373.5), Fx 24.6 N at z 17.70, lift +44.8 N + wedge 24.6 N, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.16 | 25.00 | 11.55 | 2 | OK |
| 132 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: second post's foot: shear across it (z 19.25) | A 60.7, Fx 32.6 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY shear | 0.81 | 12.50 | 15.52 | 2 | OK |
| 133 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: M3 x 45 anchor: pull-out from the frame's rail block (10.56 engaged), preload (if any) + wedge lift + lift | screw 195 N, thread cylinder Ø3 x 10.56 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | Z shear (frame) | 1.96 | 6.25 | 3.20 | 2 | OK |
| 134 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: V-ridge: flank bearing on the groove's 45° flank (contact band z 17.35..17.80: the seated tip, after the anchor's least crush, to the printed top corner) | normal 46.1 N on 0.63 x 7.3 (the 0.7 lead-in ignored) [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | bearing | 10.01 | 25.00 | 2.50 | 2 | OK |
| 135 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: V-ridge root at the foot's flats (z 18.05): shear | 2.0 x 7.3, Fx 32.6 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY shear | 3.35 | 12.50 | 3.73 | 2 | OK |
| 136 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: V-ridge root at the foot's flats (printed, x 14.35..16.35): the flank force's moment (0.50 Fx, resultant at the two upper corners, z 17.7) + the wedge's compression, Kt 1.7 | 2.0 x 7.3, M 16.3 N.mm, Kt 1.7 (bead-filled 135° root corners); compression and bending added in magnitude [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 7.93 | 25.00 | 3.15 | 2 | OK |
| 137 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.39 | 25.00 | 64.08 | 2 | OK |
| 138 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.96 | 25.00 | 25.97 | 2 | OK |
| 139 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.23 | 25.00 | 106.75 | 2 | OK |
| 140 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.28 | 25.00 | 90.49 | 2 | OK |
| 141 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: M2.5 x 16 at z 2.5: pull-out from the frame (10.5 engaged) | screw force 1 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | Z shear | 0.01 | 6.25 | 749.94 | 2 | OK |
| 142 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: same M2.5: its head on the cover's front plate | Ø6 x 0.5 washer under the Ø5 pan head on the Ø2.8 teardrop, 21.7 mm2; screw force 1 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.03 | 25.00 | 789.20 | 2 | OK |
| 143 | spec §8 proof 1: jaw B pushed towards the other, R 34.2 N: plate strip at the tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 2.52 MPa) | XY | 10.45 | 25.00 | 2.39 | 2 | OK |
| 144 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 4.48 | 25.00 | 5.58 | 2 | OK |
| 145 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 2.72 | 25.00 | 9.19 | 2 | OK |
| 146 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: top M3 head on the top wall, the joint's own tension (no preload) | T 17 N (y 14: 7, y -23: 17) on the M3 x 14 pan head on the Ø7 x 0.5 washer, 28.8 mm2 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY comp | 0.60 | 25.00 | 41.52 | 2 | OK |
| 147 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 2.43 | 25.00 | 10.27 | 2 | OK |
| 148 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 7.02 | 25.00 | 3.56 | 2 | OK |
| 149 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 3.84 | 25.00 | 6.51 | 2 | OK |
| 150 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.76 | 25.00 | 14.20 | 2 | OK |
| 151 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: M2.5 x 16 at z 2.5: pull-out from the frame (10.5 engaged) | screw force 4 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | Z shear | 0.05 | 6.25 | 117.65 | 2 | OK |
| 152 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: same M2.5: its head on the cover's front plate | Ø6 x 0.5 washer under the Ø5 pan head on the Ø2.8 teardrop, 21.7 mm2; screw force 4 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.20 | 25.00 | 123.81 | 2 | OK |
| 153 | spec §8 proof 1: jaw A pushed towards the other, R 34.2 N: plate strip at the tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 2.52 MPa) | XY | 10.45 | 25.00 | 2.39 | 2 | OK |
| 154 | spec §8 proof 1: 32 N pulls a jaw away, jaws 30 open: rack A's -y end at the lip's end, R 34.2 N | lip root at the top wall, rack side (Kt 2.5): b_eff 7.9, t 8.0, lever 5.9 | XY | 5.98 | 25.00 | 4.18 | 2 | OK |
| 155 | spec §8 proof 1: the same, rack A's +y end on the upper piece near slot A's end | front plate at the top wall (Kt 1.5): b_eff 7.1, t 5.0, lever 5.1 | XY | 8.86 | 25.00 | 2.82 | 2 | OK |
| 156 | spec §8 proof 2: 10.7 N on jaw B's tip towards the wrist, jaws closed | strip 11.75 x 5 | Z | 2.55 | 12.50 | 4.90 | 2 | OK |
| 157 | spec §8 proof 2: 10.7 N on jaw B's tip towards the wrist, jaws 44 open | strip 11.75 x 5 | Z | 3.82 | 12.50 | 3.27 | 2 | OK |

Information rows (not in the verdict):
| 158 | info: opening stall on jaw B, upper piece WITHOUT the second tie (round 2's model) | beside slot A's V apex (z 43.4): b 21.0 x 5, lever 26.2, Kt 1.5 | XY | 12.12 | 25.00 | 2.06 | 3 | **FAIL** |
| 159 | info: opening stall on jaw B, upper piece WITHOUT the second tie (round 2's model) | top-wall junction (z 48.5): b 25.5 x 5, lever 31.3, Kt 1.5 | XY | 11.94 | 25.00 | 2.09 | 3 | **FAIL** |
| 160 | info, bound: opening stall on jaw B with the corners rigidly coupled: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm held along z, corners rigid; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.68 | 25.00 | 36.51 | 3 | OK |
| 161 | info, bound: opening stall on jaw B with the corners rigidly coupled: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners rigid; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.46 | 25.00 | 17.07 | 3 | OK |
| 162 | info: anchor preload seats the ridge, bound: all 150 N on the two 45° flanks (sustained; seating, self-limiting) | normal 106 N per flank on 0.63 x 7.3 | bearing | 23.03 | 25.00 | 1.09 | 4 | **FAIL** |
| 163 | info, bound: opening stall with zero play, Fx 25.7 N all on the groove's top layer corner (z 17.8): V-ridge root at the flats, Kt 1.7 | 2.0 x 7.3, M 18.0 N.mm (arm 0.70) | XY | 8.05 | 25.00 | 3.10 | 3 | OK |
| 164 | info: opening stall, Fx 25.7 N: V-ridge flank bearing at FIRST contact, no seating credit (band z 17.406..17.8, corners [17.6, 17.8]) | normal 36.4 N on 0.56 x 7.3 | bearing | 8.94 | 25.00 | 2.79 | 3 | **FAIL** |
| 165 | info: round 6 BOM, top M3 x 10 bare pan heads driven snug, 150 N (sustained): bearing on the top wall | Ø5.6 pan head on the Ø3.4 teardrop, 14.9 mm2 | XY comp | 10.05 | 25.00 | 2.49 | 4 | **FAIL** |
| 166 | info: round 6 BOM, front M2.5 bare pan heads driven snug, 100 N (sustained): bearing on the front plate | Ø5 pan head on the Ø2.8 teardrop, 13.1 mm2 | XY comp | 7.66 | 25.00 | 3.26 | 4 | **FAIL** |
| 167 | info: camera case, M3 x 18 bare button heads (BOM) driven snug, 150 N (sustained): bearing on the camera mount's pad (not this part; the same Ø3.4 printed teardrop) | Ø5.7 button head, 15.8 mm2 | XY comp | 9.48 | 25.00 | 2.64 | 4 | **FAIL** |
| 168 | info: camera case with the proposed fix, M3 x 18 button heads on Ø7 x 0.5 washers, 150 N (sustained): bearing on the camera mount's pad | 28.8 mm2 (washer OD) | XY comp | 5.21 | 25.00 | 4.80 | 4 | OK |
| 169 | info: the +y top M3 pulls the proud top wall down (nominal: 0.079 at the screw after the anchor's seating; 0.91 of it bends the wall, 44 N): top face at the lip's back face, tension (displacement-controlled, relaxes) | cantilever L 7.6, b_eff 22.2 x 3, E 1800, Kt 1 (smooth face) | XY | 10.08 | 25.00 | 2.48 | 4 | **FAIL** |
| 170 | info: the same, nominal: the re-entrant corner under it (lip back face / top wall underside), compression | Kt 2.5 | XY comp | 25.20 | 25.00 | 0.99 | 3 | **FAIL** |
| 171 | info: the +y top M3 pulls the proud top wall down (RSS-high: 0.165 at the screw after the anchor's seating; 0.91 of it bends the wall, 92 N): top face at the lip's back face, tension (displacement-controlled, relaxes) | cantilever L 7.6, b_eff 22.2 x 3, E 1800, Kt 1 (smooth face) | XY | 21.02 | 25.00 | 1.19 | 4 | **FAIL** |
| 172 | info: the same, RSS-high: the re-entrant corner under it (lip back face / top wall underside), compression | Kt 2.5 | XY comp | 52.55 | 25.00 | 0.48 | 3 | **FAIL** |

lowest SF 3.03 (required 3): added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: plate strip above the first tie's web / cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 1.99 MPa)
VERDICT (calculation): NEEDS_TEST (placeholder allowables)

The script also prints the seat stack, the what-ifs and the tables quoted above.

---

# Round 6 independent review (kept as history; its verdict: FAIL)

# Strength check (round 6, independent review): 20261026-arm-claw-cover

strength-analyst (independent; did not design the part) · 2026-10-26 · round 6 (ridge-first contact), merged at
105aafe · `python3 jobs/20261026-arm-claw-cover/strength_calc.py` (plain python3, from the project root, about 60 s).
The CAD engineer's round-6 self-check of this file is replaced. Every number here is recomputed: the slice facts from my
own scratch slice (scratchpad, not a job file), the geometry from the models, the rest from the script.

## Verdict

**FAIL, on two snug-preload rows (sustained, req 4). The round-6 seat itself works.**

- **Lowest SF 2.49 (row 119, FAIL):** the two top M3 × 10 **bare pan heads** on the 3 mm top wall at the snug preload
  (150 N, the anchor's own figure). That is 10.1 MPa on 14.9 mm². The project rule (the anchor in round 5, the turntable
  ring, the links) is a Ø7 × 0.5 washer under every snug M3 head on PETG. The frame fails the same screw's pull-out
  (6.95 engaged, SF 2.73; frame strength.md).
- **Row 120, FAIL: 3.26.** The two front M2.5 × 16 bare pan heads on the front plate at their snug preload (100 N, the
  frame's tab-screw figure), on 13.1 mm².
- **Every other verdict row passes.** The lowest are:
  - 3.01, row 108: the M2.5 pan head under the one-jaw stall (short-term);
  - 3.03, rows 30 and 87: the plate strips at the ties' webs;
  - 3.16, row 44: the ridge's flank bearing under the opening stall.

  The sustained rows are the anchor's washer 4.80 (row 116), the post round its hole 8.97 (row 117) and the M3 × 45
  pull-out on the preload 4.15 (row 118). The cyclic row is 10.60. The lowest proof rows (req 2) are 2.39 (the plate
  strips) and 2.50 (the ridge bearing).
- **Placeholder allowables.** With the fix below, the verdict would be NEEDS_TEST, not PASS: there is no library row
  for PETG.

## Required fix (smallest, with numbers)

1. **Top screws without the camera:** **M3 × 14 pan head + Ø7 × 0.5 washer (ISO 7089)**, snug only (≤ 0.09 N·m, as the
   anchor). This replaces the M3 × 10.
   - Head on the washer: 28.8 mm², **SF 4.80**.
   - Engaged 10.50 below the printed bulkhead (10.24 if the worst standing, 0.259, is left at the screw): pull-out
     **4.12 / 4.02**.
   - The tip ends at z 38.0, 3.55 above the 14 mm pilot's floor (34.45).
   - The head is 12.8 from the jaws (exact solids).
   - With the camera, the M3 × 18 button heads stay. Their head is on the camera mount's pad, and their pull-out on
     the preload is 4.41 (frame).
   - An M3 × 10 or × 12 with the washer does not pass: pull-out 2.55 / 3.34.
2. **Front M2.5 screws.** A standard washer does not fit at z 3: a DIN 125 Ø6 × 0.5 washer touches jaw B's neck
   (0.000, exact solids). There are two ways to fix it:
   - (a) **The smallest:** BUILD_GUIDE §4 step 9 and the BOM say "drive each M2.5 until the head seats, then stop
     (≤ 0.04 N·m)". That gives a preload ≤ 82 N and head bearing SF ≥ 4.0. This is no harder to follow than the
     anchor's "≤ 0.09 N·m".
   - (b) **The robust one:** `FRONT_SCREWS` z 3 → **2.5** in claw_frame.py, plus DIN 125 **Ø6 × 0.5** washers. This
     changes both models.
     - Clearance to jaw B: 0.50 in CAD, 0.26 with the worst standing.
     - Head bearing 21.7 mm²: SF 5.42 on the preload; 4.17 under the stall, whose screw force rises to 130 N at
       z 2.5.
     - Pull-out 4.15.
     - The frame's front pilots keep a 2.4 skin on top and 1.4 underneath.

   **I recommend (b).** z 2.75 is not enough: 0.25 in CAD, 0.01 with the worst standing.

## 1. The seat as printed: is the ridge really the first contact?

**My slice** (PrusaSlicer 2.7.2, Arachne, 0.20mm QUALITY @MK3, Prusament PETG, each job's slice_overrides.ini; the
committed part.stl files, which match a rebuild of model.py to 0.4 mm³). Read back from the G-code:

| Feature | CAD | Printed | Evidence |
|---|---|---|---|
| Frame bulkhead top and both ribs | 48.45 | **48.4** | last layer `;Z:48.4`; extrusion over x 3.6–9.9 at every y, and on both ribs, ends there |
| Frame rail block top | 17.75 | **17.8** | front of the groove, behind it, and at −y |
| Groove walls, layers ending 17.2 / 17.4 / 17.6 / 17.8 | 45° | half-widths **0.15 / 0.35 / 0.55 / 0.75** | external perimeters 14.875/15.625, 14.675/15.825, 14.475/16.025, 14.275/16.225 (w 0.45) at y 25, 26, 30, 31.5 |
| Groove's 17.0–17.2 layer | — | **an open 0.3 slot** | two external perimeters, bead edges 15.10 / 15.40; the layer below (17.0) is solid. It is not "closed": the tip faces this layer's top (17.2) at 0.15–0.35 off the centre line |
| Cover ridge flanks, tip, flats | 45°, 17.35, 18.05 | **to CAD** | external perimeter 0.225 inside each (tip path z 17.575, flats 18.275) |
| Cover 0.2 × 0.2 bump behind the post's face | x 14.15–14.35 | **not printed** | the outline runs from the flank (14.527, 17.991) straight onto the post's face (14.575, 18.039): the printed root is **2.0** wide, not 2.2 |
| Cover top wall underside | 48.5 | 48.5 | perimeter at 48.725 |

**Stack model.** Each stop is a height at which the rigid cover touches; it rests on the highest. Tolerances are 3σ,
±0.05 on **every** printed surface as the brief says:
- the ridge flank ±0.05 normal (±0.0707 vertical);
- the groove's walls ±0.05;
- the cover's underside ±0.05;
- the bulkhead top ±0.05;
- the tip ±0.05 and the 17.2 layer ±0.05;
- the flats ±0.05 and the block ±0.05;
- the bead corner radius 0.05–0.10.

The self-check had no tolerance on the bulkhead top, the tip or the slot.

| Case | Stops on | Play (per flank, mm) | Top wall over the printed bulkhead | Tip over the 17.2 layer | Lowest frame-model SF |
|---|---|---|---|---|---|
| Nominal (r 0.075) | ridge, both flanks | **0** | 0.156 | 0.206 | 3.16 (ridge bearing, 'locked') |
| RSS | ridge, both flanks (margins: top wall +0.043, tip +0.093, flats +0.193) | **0** | ≥ 0.043 | ≥ 0.093 | 3.16 |
| Worst, any build | the top wall | **0.079** | 0.000 | 0.250 | **1.89** (top wall behind the lip). **BUILD_GUIDE step 9 rejects this build** (0.03 feeler cannot enter) |
| Worst a build passing step 9 can have | the ridge's tip on the 17.2 layer | **0.029** | 0.150 | 0.000 | 4.04 (less push reaches the ridge) |

**Ruling on the play:**
- Ridge-first holds at nominal and RSS.
- Play 0.079 is possible only when every tolerance is at its limit, and that build fails step 9.
- What step 9 cannot see is the tip bottoming: 0.029 at the absolute worst. At that play the frame model's lowest SF
  is 4.04.
- The verdict rows therefore run at 'locked' (play 0) and at 0.029, and take the worse. The self-check's 0.029 was the
  right number by coincidence: it came from the top-wall case with the bulkhead held at exactly 48.4.

**Which corners carry.**
- The groove's printed corners stand 0.1 inside the CAD flank. Rounded r 0.075, they let the ridge land **0.056** above
  its CAD seat, so its tip is at 17.406.
- A rounded corner touches the flank at z_top − 0.29 r. The 17.4 corner (17.378) is beyond the tip, so **only the 17.6
  and 17.8 corners carry at first contact**. The self-check counted three and took the band from the CAD tip.
- The anchor's 150 N then crushes them. At 80 MPa, which gives the least crush, the ridge sinks 0.052, the 17.4 corner
  joins, and the tip settles at 17.354 (0.095 / 17.311 at 40 MPa).
- The anchor goes in first and snug (BUILD_GUIDE), before any service load. So the verdict bearing rows use the band
  after the least crush: 0.446 tall, 0.63 of flank, **SF 3.16** (stall) and 2.50 (proof).
- At first contact, with no crush credit, it would be 2.79 (info row 164).
- The flank force's resultant is taken at the two upper corners (z 17.7). On the printed 2.0-wide root that gives an
  arm of 0.50 Fx: root bending **4.00**, shear 4.73. With all of it on the top corner (arm 0.70), 3.10 (info row 163).

**Seating and the top wall's standing** (over the printed bulkhead, at the ridge):

| | Nominal | RSS-high | Worst |
|---|---|---|---|
| Before any screw | 0.156 | 0.269 | 0.391 |
| After the anchor, least crush (80 MPa) | 0.104 | 0.217 | 0.339 |
| After the anchor, 40 MPa | 0.061 | 0.174 | 0.296 |

The M3 × 45's engagement is counted from the **printed** block top: **10.56** with the worst standing. The self-check
had 10.49, taken from the CAD block top less the whole float.

## 2. The frame's 3.004 bound row and the 2.94 info row

I added the support reactions to the frame solver and read the top joint off the model directly. Per zone, the least M3
tension that balances it is `T = max(0, −Rz, M/3.25, (−M − 6.5 Rz)/3.25)`. Worst of the 64 variants and both play modes:

| Push | Case | +y screw (y 14) | −y screw (y −23) |
|---|---|---|---|
| Rack B on the upper piece | opening stall / crash / proof | **23.0** / 21.1 / 24.5 N | 4.7 / 4.3 / 5.0 N |
| Rack A on the lower piece | opening stall / crash / proof | 8.7 / 5.5 / 11.0 N | 13.6 / 8.6 / 17.2 N |
| The same cover with no anchor at all (round 3) | opening stall | 20.2 N | **283.8 N** |

**Ruling: the bound is too conservative and belongs in neither verdict.** Its 136 N per screw (all 886 N·mm on the top
screws, "as if the post held nothing") is the unanchored cover's load path. With the ridge in the groove, the push leaves
through the post. The real top-screw tension is ≤ 24.5 N, so pull-out is SF ≥ 16 even at the worst standing.

The 2.94 info row compounds that bound with a standing left at the screw, so it is a bound on a bound. I recompute it at
the worst standing after seating (6.74 engaged, 2.91) and keep it as information only.

What does govern the top screws is their own snug preload (the required fix).

## 3. The top wall's standing: what it does

**Rack A's guide and backlash.** Rack A rides under the top wall, so the cover's height sets its mesh with the
frame-held pinion. The cover rests on the ridge at +y and on the printed bulkhead at −y. Backlash per mesh is 0.40 +
2 da tan 20°:

| Where | da (mm) | Backlash | Tip clearance | Contact ratio |
|---|---|---|---|---|
| −y end, worst low | −0.200 | 0.254 | 0.200 | 1.72 |
| −y end, on 48.4 | −0.100 | 0.327 | 0.300 | 1.62 |
| +y end after the anchor, nominal | +0.004 | 0.403 | 0.404 | 1.52 |
| +y end after the anchor, RSS-high | +0.117 | 0.485 | 0.517 | 1.41 |
| +y end after the anchor, worst | +0.239 | 0.574 | 0.639 | 1.28 |

- No binding anywhere: the clearances stay positive.
- The contact ratio stays ≥ 1.28.
- Backlash runs 0.33–0.40 nominal along the guide. That is the SYS-08 target (round 5's printed seat gave 0.33
  everywhere). At RSS-high it exceeds 0.40 at the +y end. That costs jaw-position slop, not strength. Rack A's 0.25
  gaps to the lip and front plate do not change: both move with the cover.
- The spec's note "rack A's 0.7 backlash absorbs it" is the wrong reason. A higher guide *increases* backlash; it needs
  no absorbing.

**Slot B (a fit item the self-check did not look at).**
- Jaw B rides on the frame's wrist plate, but slot B moves with the cover. Its lower clearance is 0.25 − (the cover's
  height): **0.246 nominal, 0.133 RSS-high, 0.011 worst** after seating.
- The strip's top stays below the rack's running surface (z 6) as long as the height is under 0.25, so this rubs in
  the worst case at most and never lifts the jaw. It is a note, not a fail.
- The M2.5 heads (on the cover) sit 0.50 under jaw B's neck in CAD, 0.26 with the worst standing.

**M3 × 10 and × 18 engagement.**
- The bulkhead prints at 48.4. With the wall pulled down, an M3 × 10 has 7.00 engaged (6.95 in CAD). With the worst
  standing left at the screw (0.259) it has 6.74. An M3 × 18 through the camera pad has 11.50 / 11.24.
- Service tension is ≤ 24.5 N, so service pull-out is SF ≥ 16.
- The preload is what fails: the frame row at 2.73.

**Camera mount.**
- It sits on the top wall and rises with it. The cover's tilt along y (0.10–0.34 over 60 mm) is ≤ 0.3° about x.
- When the M3 × 18s pull the proud wall down behind the lip, the pad (x 0–14) can pitch by up to about 0.6° (nominal).
  That shifts the image by about 1 % of its height. No clearance changes: the anchor head is 3.91 from the mount and
  14.3 from the Brio with its plug.

**The proud wall pulled down (info rows 165–168).** After seating, the gap at the +y screw is 0.079 nominal (0.165
RSS-high, 0.259 worst). Driving the M3 closes it in two ways in series:
- bending the top wall behind the lip (cantilever, L 7.6, b_eff 20.8: 576 N/mm);
- tilting the cover, which crushes the ridge more (6030 N/mm).

Bending takes 91 % of it.

| Case at the +y screw | Gap | Screw force to close | Top face, tension | Re-entrant corner, compression |
|---|---|---|---|---|
| Nominal | 0.079 | 42 N | 10.1 MPa | 25.3 MPa |
| RSS-high | 0.165 | 87 N | 21.1 MPa | 52.9 MPa |

**Ruling: information, not a verdict row.**
- It is displacement-controlled, like the seating crush the round 5 review also ruled information.
- Creep only lets the wall settle onto the bulkhead.
- The tensile side is a smooth face, below the in-plane strength even at RSS-high. The sharp corner is in compression.
- It is an upper bound: a rigid root, the narrow b_eff.

It is another reason for "snug only" on the top screws. It is also why the proof test must not count whitening at the
lip's back corner seen right after assembly (inspect before the first screw and after the proof).

## 4. Printability (the strength side)

- **The ridge bump does not print.** The root is 2.0 wide (rows 26, 49 etc. use 2.0).
- **The groove's 17.2 layer.** The tip's 0.206 over it holds at RSS (+0.093). In the worst case the tip bottoms (play
  0.029, SF 4.04).
- **The anchor pilot's 0.95 mm ligament** is the frame's (frame strength.md).

## 5. Clearances (exact solids, claw_sequence_check placements, gap 0–44 every 1 mm)

- **Racks:**

  | Feature | Clearance | Where it is least |
  |---|---|---|
  | Second post + ridge + foot | 0.240 | jaw A, gap 0 |
  | Lip | 0.240 | |
  | First tie's post | 0.240 | |
  | Webs | 1.128 | |
  | Frame rail block | 0.250 | jaw B |

  All are ≥ 0.2.
- **Washer and head:**

  | Item | Clearance |
  |---|---|
  | Anchor Ø7 × 0.5 washer + Ø5.5 head, to the jaws | 3.162 |
  | the same, to the camera mount | 3.911 |
  | the same, to the Brio with its plug | 14.301 |
  | M2.5 heads to jaw B | 0.500 (0.26 with the worst standing) |
  | Fix: M3 × 14 head on a Ø7 washer, to the jaws | 12.77 |

- **Note (not the round-6 change, not a rack).** At gap 0–44 the front plate is 0.148 from jaw A, at slot A's lower
  edge on the plate's front face. The jaw's r 3 kink fillet (neck → finger) starts 1.24 behind NECK_X1, inside the slot.
  A 0.3 × 45° chamfer on slot A's (and slot B's) front edges would restore ≥ 0.25. This is a jaw / cover detail for the
  next round.

## 6. Every other row

Every verdict row ≥ 3 passes except the two preload rows above.

**Sustained rows (req 4):**

| Row | What | SF |
|---|---|---|
| 116 | anchor washer | 4.80 |
| 117 | post round its hole | 8.97 |
| 118 | anchor pull-out | 4.15 |
| 119 | top M3 heads | **2.49** |
| 120 | M2.5 heads | **3.26** |

Rows 119 and 120 are new: the self-check had no row for these preloads. The cyclic row (both jaws stalled) is 10.60.

## Load cases (unchanged since round 4)

The stall is 216 N·mm through the 20-tooth pinion: 21.6 N on one rack, 10.8 N per jaw. Each rack cocks in its 0.25 gaps
and reacts its finger's moment with end forces R = F (x_load − 28.6) / span. The cases:
- one jaw blocked (R 19.8–27.0 N, short-term);
- both jaws (cyclic);
- crash, 13 N at the tip (R 12.6–17.2 N, reversed);
- opening against an obstacle (R up to 27.0 N, reversed);
- handling, 5 N;
- yaw stall 7.1 N and hand 5 N sideways on jaw B;
- rack A lift 13.8 N;
- camera tug 10 N;
- the anchor's snug preload (150 N, sustained);
- **the cover screws' snug preloads (new: M3 150 N, M2.5 100 N, sustained);**
- spec §8 proof (32 N, R 34.2 N; 10.7 N sideways).

## Method, allowables

- **Two-zone x–z frame of the cover, 64 joint variants** (round 4), with the post's foot held by the ridge (3 kN/mm in
  x at z 17.7, stiff in z).
- **Play modes:** 'locked' (play 0, the preload added to the screw where that is worse) and 'slip 0.029' (the worst
  build that step 9 accepts, preload gone). Each row is the worse of the two.
- **Support reactions** are now returned by the solver, for the top joint.
- **Allowables are placeholders, PETG** (no library row):
  - 25 MPa along the layers, 12.5 across, 6.25 interlayer shear;
  - bearing 25;
  - Kt 2.5 sharp, 1.7 at the ridge's root, 1.5 at r ≥ 0.25 h, 2 at a hole;
  - E 1.8 GPa (stiffness ratios and the forced-closure rows only).
- **Corner crush** is taken at 40 or 80 MPa (an assumption, bracketed).
- **Temperature:** 40 °C against PETG at ~70 °C, OK.
- **Required SF:** 3 short-term, 4 sustained or cyclic, 2 at the proof load.

## Proof test (spec §8)

With the fix, the cover's proof rows pass (lowest 2.39, the plate strips). See design_review.md for the §8 text changes:
- the step-9 seat check as an acceptance line;
- the M2.5 and M3 hardware;
- "inspect the lip's back corner before loading".

## Results (from `strength_calc.py`, verbatim; each frame-model row is the worse of 'locked' and the worst accepted play 0.029 mm)

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | stall, one jaw blocked, jaws 44 open: rack A's -y end at the lip's end, R 27.0 N (the first tie's prop ignored) | lip root at the top wall, rack side (Kt 2.5): b_eff 7.9, t 8.0, lever 5.9 | XY | 4.72 | 25.00 | 5.30 | 3 | OK |
| 2 | stall, one jaw blocked, jaws closed: rack A's -y end at y -25.1, R 19.8 N | lip root at the top wall, rack side (Kt 2.5): b_eff 13.8, t 8.0, lever 5.9 | XY | 1.98 | 25.00 | 12.63 | 3 | OK |
| 3 | stall, both jaws (cyclic), jaws 44 open: R 13.5 N at the lip's end | lip root at the top wall, rack side (Kt 2.5): b_eff 7.9, t 8.0, lever 5.9 | XY | 2.36 | 25.00 | 10.60 | 4 | OK |
| 4 | crash 13 N pushes jaw A shut, jaws closed: rack A's +y end on the lip at y 31.4, R 12.6 N (the second tie's prop ignored) | lip root at the top wall, rack side (Kt 2.5): b_eff 8.5, t 8.0, lever 5.9 | XY | 2.05 | 25.00 | 12.20 | 3 | OK |
| 5 | added: opening against an obstacle, jaw A, jaws nearly closed: rack A's +y end at y 31.4, R 19.8 N (the second tie's prop ignored) | lip root at the top wall, rack side (Kt 2.5): b_eff 8.5, t 8.0, lever 5.9 | XY | 3.22 | 25.00 | 7.77 | 3 | OK |
| 6 | stall, one jaw blocked: rack A's +y end on the upper piece near slot A's end, R 27.0 N | front plate at the top wall (Kt 1.5): b_eff 7.1, t 5.0, lever 5.1 | XY | 6.99 | 25.00 | 3.58 | 3 | OK |
| 7 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 1.27 MPa) | XY | 5.25 | 25.00 | 4.76 | 3 | OK |
| 8 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 5.21 | 25.00 | 4.79 | 3 | OK |
| 9 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 3.28 | 25.00 | 7.63 | 3 | OK |
| 10 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: top M3 pan head on the top wall, the joint's own tension (no preload) | T 21 N (y 14: 21, y -23: 1) on the Ø5.6 pan head, 14.9 mm2 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 1.41 | 25.00 | 17.73 | 3 | OK |
| 11 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.06 | 25.00 | 23.66 | 3 | OK |
| 12 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.07 | 25.00 | 335.50 | 3 | OK |
| 13 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.41 | 25.00 | 60.69 | 3 | OK |
| 14 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.10 | 25.00 | 11.91 | 3 | OK |
| 15 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: second tie's post under the lip (z 35.25..36.75) | 8 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.83 | 25.00 | 30.07 | 3 | OK |
| 16 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.47 | 25.00 | 10.14 | 3 | OK |
| 17 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.82 | 25.00 | 13.76 | 3 | OK |
| 18 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: second post's foot below the web (z 18.05..19.25), the anchor's reaction | 8 x 8.96 net of the Ø3.6 hole (A 60.7, I 373.5), Fx 8.7 N at z 17.70, lift +38.5 N + wedge 8.7 N, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.14 | 25.00 | 21.93 | 3 | OK |
| 19 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: second post's foot: shear across it (z 19.25) | A 60.7, Fx 16.4 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY shear | 0.40 | 12.50 | 30.88 | 3 | OK |
| 20 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: M3 x 45 anchor: pull-out from the frame's rail block (10.56 engaged), preload (if any) + wedge lift + lift | screw 172 N, thread cylinder Ø3 x 10.56 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | Z shear (frame) | 1.73 | 6.25 | 3.61 | 3 | OK |
| 21 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: V-ridge: flank bearing on the groove's 45° flank (contact band z 17.35..17.80: the seated tip, after the anchor's least crush, to the printed top corner) | normal 23.2 N on 0.63 x 7.3 (the 0.7 lead-in ignored) [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | bearing | 5.03 | 25.00 | 4.97 | 3 | OK |
| 22 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: V-ridge root at the foot's flats (z 18.05): shear | 2.0 x 7.3, Fx 16.4 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY shear | 1.68 | 12.50 | 7.43 | 3 | OK |
| 23 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: V-ridge root at the foot's flats (printed, x 14.35..16.35): the flank force's moment (0.50 Fx, resultant at the two upper corners, z 17.7) + the wedge's compression, Kt 1.7 | 2.0 x 7.3, M 8.2 N.mm, Kt 1.7 (bead-filled 135° root corners); compression and bending added in magnitude [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 3.98 | 25.00 | 6.28 | 3 | OK |
| 24 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.34 | 25.00 | 74.32 | 3 | OK |
| 25 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.83 | 25.00 | 30.21 | 3 | OK |
| 26 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.20 | 25.00 | 123.91 | 3 | OK |
| 27 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.24 | 25.00 | 105.81 | 3 | OK |
| 28 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 1 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | Z shear | 0.01 | 6.25 | 891.30 | 3 | OK |
| 29 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 1 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.05 | 25.00 | 538.81 | 3 | OK |
| 30 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 1.99 MPa) | XY | 8.25 | 25.00 | 3.03 | 3 | OK |
| 31 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 5.70 | 25.00 | 4.38 | 3 | OK |
| 32 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 3.59 | 25.00 | 6.97 | 3 | OK |
| 33 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: top M3 pan head on the top wall, the joint's own tension (no preload) | T 23 N (y 14: 23, y -23: 1) on the Ø5.6 pan head, 14.9 mm2 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 1.54 | 25.00 | 16.21 | 3 | OK |
| 34 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.16 | 25.00 | 21.49 | 3 | OK |
| 35 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.08 | 25.00 | 305.77 | 3 | OK |
| 36 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.45 | 25.00 | 55.16 | 3 | OK |
| 37 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.31 | 25.00 | 10.83 | 3 | OK |
| 38 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: second tie's post under the lip (z 35.25..36.75) | 8 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.92 | 25.00 | 27.19 | 3 | OK |
| 39 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.70 | 25.00 | 9.26 | 3 | OK |
| 40 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.99 | 25.00 | 12.59 | 3 | OK |
| 41 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: second post's foot below the web (z 18.05..19.25), the anchor's reaction | 8 x 8.96 net of the Ø3.6 hole (A 60.7, I 373.5), Fx 17.9 N at z 17.70, lift +42.1 N + wedge 17.9 N, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.73 | 25.00 | 14.46 | 3 | OK |
| 42 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: second post's foot: shear across it (z 19.25) | A 60.7, Fx 25.7 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY shear | 0.64 | 12.50 | 19.66 | 3 | OK |
| 43 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: M3 x 45 anchor: pull-out from the frame's rail block (10.56 engaged), preload (if any) + wedge lift + lift | screw 185 N, thread cylinder Ø3 x 10.56 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | Z shear (frame) | 1.86 | 6.25 | 3.36 | 3 | OK |
| 44 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: V-ridge: flank bearing on the groove's 45° flank (contact band z 17.35..17.80: the seated tip, after the anchor's least crush, to the printed top corner) | normal 36.4 N on 0.63 x 7.3 (the 0.7 lead-in ignored) [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | bearing | 7.90 | 25.00 | 3.16 | 3 | OK |
| 45 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: V-ridge root at the foot's flats (z 18.05): shear | 2.0 x 7.3, Fx 25.7 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY shear | 2.64 | 12.50 | 4.73 | 3 | OK |
| 46 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: V-ridge root at the foot's flats (printed, x 14.35..16.35): the flank force's moment (0.50 Fx, resultant at the two upper corners, z 17.7) + the wedge's compression, Kt 1.7 | 2.0 x 7.3, M 12.9 N.mm, Kt 1.7 (bead-filled 135° root corners); compression and bending added in magnitude [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 6.25 | 25.00 | 4.00 | 3 | OK |
| 47 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.37 | 25.00 | 67.97 | 3 | OK |
| 48 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.91 | 25.00 | 27.62 | 3 | OK |
| 49 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.22 | 25.00 | 113.31 | 3 | OK |
| 50 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.26 | 25.00 | 96.77 | 3 | OK |
| 51 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 1 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | Z shear | 0.01 | 6.25 | 815.16 | 3 | OK |
| 52 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 1 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.05 | 25.00 | 492.79 | 3 | OK |
| 53 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 0.49 MPa) | XY | 2.02 | 25.00 | 12.38 | 3 | OK |
| 54 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 4.45 | 25.00 | 5.62 | 3 | OK |
| 55 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.51 | 25.00 | 9.97 | 3 | OK |
| 56 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: top M3 pan head on the top wall, the joint's own tension (no preload) | T 16 N (y 14: 16, y -23: 1) on the Ø5.6 pan head, 14.9 mm2 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 1.08 | 25.00 | 23.17 | 3 | OK |
| 57 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.92 | 25.00 | 27.29 | 3 | OK |
| 58 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.07 | 25.00 | 378.96 | 3 | OK |
| 59 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.36 | 25.00 | 69.46 | 3 | OK |
| 60 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.84 | 25.00 | 13.60 | 3 | OK |
| 61 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: second tie's post under the lip (z 35.25..36.75) | 8 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.62 | 25.00 | 40.10 | 3 | OK |
| 62 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.87 | 25.00 | 13.38 | 3 | OK |
| 63 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.61 | 25.00 | 15.51 | 3 | OK |
| 64 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: second post's foot below the web (z 18.05..19.25), the anchor's reaction | 8 x 8.96 net of the Ø3.6 hole (A 60.7, I 373.5), Fx 0.0 N at z 17.70, lift +29.6 N + wedge 0.0 N, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.49 | 25.00 | 51.31 | 3 | OK |
| 65 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: second post's foot: shear across it (z 19.25) | A 60.7, Fx 6.3 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY shear | 0.16 | 12.50 | 80.30 | 3 | OK |
| 66 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: M3 x 45 anchor: pull-out from the frame's rail block (10.56 engaged), preload (if any) + wedge lift + lift | screw 159 N, thread cylinder Ø3 x 10.56 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | Z shear (frame) | 1.59 | 6.25 | 3.92 | 3 | OK |
| 67 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: V-ridge: flank bearing on the groove's 45° flank (contact band z 17.35..17.80: the seated tip, after the anchor's least crush, to the printed top corner) | normal 8.9 N on 0.63 x 7.3 (the 0.7 lead-in ignored) [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | bearing | 1.93 | 25.00 | 12.92 | 3 | OK |
| 68 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: V-ridge root at the foot's flats (z 18.05): shear | 2.0 x 7.3, Fx 6.3 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY shear | 0.65 | 12.50 | 19.31 | 3 | OK |
| 69 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: V-ridge root at the foot's flats (printed, x 14.35..16.35): the flank force's moment (0.50 Fx, resultant at the two upper corners, z 17.7) + the wedge's compression, Kt 1.7 | 2.0 x 7.3, M 3.1 N.mm, Kt 1.7 (bead-filled 135° root corners); compression and bending added in magnitude [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 1.53 | 25.00 | 16.32 | 3 | OK |
| 70 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.30 | 25.00 | 84.37 | 3 | OK |
| 71 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.73 | 25.00 | 34.30 | 3 | OK |
| 72 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.18 | 25.00 | 140.67 | 3 | OK |
| 73 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.21 | 25.00 | 119.35 | 3 | OK |
| 74 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 1 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | Z shear | 0.01 | 6.25 | 1005.33 | 3 | OK |
| 75 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 1 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.04 | 25.00 | 607.75 | 3 | OK |
| 76 | added: opening against an obstacle, jaw B, jaws closed: rack B's end 6.9 from the edge, R 19.8 N: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 6.15 x 5, Kt 2.5 (shear 0.96 MPa) | XY | 4.00 | 25.00 | 6.25 | 3 | OK |
| 77 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 1.27 MPa) | XY | 5.25 | 25.00 | 4.76 | 3 | OK |
| 78 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.23 | 25.00 | 11.20 | 3 | OK |
| 79 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 1.36 | 25.00 | 18.41 | 3 | OK |
| 80 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: top M3 pan head on the top wall, the joint's own tension (no preload) | T 9 N (y 14: 4, y -23: 9) on the Ø5.6 pan head, 14.9 mm2 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY comp | 0.58 | 25.00 | 43.17 | 3 | OK |
| 81 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 1.21 | 25.00 | 20.59 | 3 | OK |
| 82 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 3.51 | 25.00 | 7.12 | 3 | OK |
| 83 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.92 | 25.00 | 13.03 | 3 | OK |
| 84 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.88 | 25.00 | 28.48 | 3 | OK |
| 85 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 2 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | Z shear | 0.03 | 6.25 | 239.92 | 3 | OK |
| 86 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 2 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.17 | 25.00 | 145.04 | 3 | OK |
| 87 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 1.99 MPa) | XY | 8.25 | 25.00 | 3.03 | 3 | OK |
| 88 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 3.50 | 25.00 | 7.13 | 3 | OK |
| 89 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 2.13 | 25.00 | 11.73 | 3 | OK |
| 90 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: top M3 pan head on the top wall, the joint's own tension (no preload) | T 14 N (y 14: 6, y -23: 14) on the Ø5.6 pan head, 14.9 mm2 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY comp | 0.91 | 25.00 | 27.49 | 3 | OK |
| 91 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 1.91 | 25.00 | 13.11 | 3 | OK |
| 92 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 5.51 | 25.00 | 4.53 | 3 | OK |
| 93 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 3.01 | 25.00 | 8.30 | 3 | OK |
| 94 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.38 | 25.00 | 18.14 | 3 | OK |
| 95 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 4 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | Z shear | 0.04 | 6.25 | 152.76 | 3 | OK |
| 96 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 4 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.27 | 25.00 | 92.35 | 3 | OK |
| 97 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 0.49 MPa) | XY | 2.02 | 25.00 | 12.38 | 3 | OK |
| 98 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.86 | 25.00 | 29.13 | 3 | OK |
| 99 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 0.52 | 25.00 | 47.88 | 3 | OK |
| 100 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: top M3 pan head on the top wall, the joint's own tension (no preload) | T 3 N (y 14: 1, y -23: 3) on the Ø5.6 pan head, 14.9 mm2 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY comp | 0.22 | 25.00 | 112.23 | 3 | OK |
| 101 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 0.47 | 25.00 | 53.54 | 3 | OK |
| 102 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.35 | 25.00 | 18.51 | 3 | OK |
| 103 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.74 | 25.00 | 33.87 | 3 | OK |
| 104 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.34 | 25.00 | 74.05 | 3 | OK |
| 105 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 1 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | Z shear | 0.01 | 6.25 | 623.78 | 3 | OK |
| 106 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 1 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.07 | 25.00 | 377.09 | 3 | OK |
| 107 | added: opening against an obstacle, jaw A, jaws closed: rack A's end 6.9 from the edge, R 19.8 N: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 6.15 x 5, Kt 2.5 (shear 0.96 MPa) | XY | 4.00 | 25.00 | 6.25 | 3 | OK |
| 108 | stall, one jaw blocked, jaws 44 open: rack B's -y end pushes the lower piece forward (27.0 N at z 12.1): one M2.5 holds it, 108 N | pan head Ø5 on the Ø2.8 teardrop, 13.1 mm2 | XY comp | 8.30 | 25.00 | 3.01 | 3 | OK |
| 109 | stall, one jaw blocked: the same push on the lower piece's plate between the screw (z 3) and the web (z 19.25) | simply supported, b_eff 9.2 x 5 (one-sided spread at the edge) | XY | 2.82 | 25.00 | 8.86 | 3 | OK |
| 110 | yaw stall 7.1 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 25 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws closed | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 1.69 | 12.50 | 7.38 | 3 | OK |
| 111 | yaw stall 7.1 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 25 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws 44 open | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 2.53 | 12.50 | 4.93 | 3 | OK |
| 112 | hand push 5 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 18 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws closed | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 1.19 | 12.50 | 10.48 | 3 | OK |
| 113 | hand push 5 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 18 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws 44 open | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 1.78 | 12.50 | 7.00 | 3 | OK |
| 114 | rack A lift: separating 7.9 N + grip twist 410 N.mm -> 13.8 N at the rack end | top wall between the lip and the front plate, span 12.5, b 25 x 3 | XY | 1.44 | 25.00 | 17.34 | 3 | OK |
| 115 | USB tug 10 N tips the camera mount back: 53 N on the top wall's rear edge | 50 x 1 mm contact | XY | 1.06 | 25.00 | 23.67 | 3 | OK |
| 116 | anchor M3 x 45 driven snug: Ø7 x 0.5 washer under the socket head on the top wall, preload 150 N (sustained) | 28.8 mm2 round the Ø3.4 teardrop (washer OD; BUILD_GUIDE §1) | XY comp | 5.21 | 25.00 | 4.80 | 4 | OK |
| 117 | anchor preload 150 N through the stack (sustained): the 8 x 8 post round its Ø3.6 hole | 54 mm2 (the full-depth part only; the 45-degree part ignored) | XY comp | 2.79 | 25.00 | 8.97 | 4 | OK |
| 118 | anchor preload 150 N (sustained): M3 x 45 pull-out from the frame's rail block, the top wall left 0.339 proud after seating (worst-case stack) | thread cylinder Ø3 x 10.56 (Ø2.7 x 14 pilot; 10.75 in CAD) | Z shear (frame) | 1.51 | 6.25 | 4.15 | 4 | OK |
| 119 | top M3 x 10 pan heads (BOM: no washer) driven snug, 150 N preload (sustained): bearing on the top wall | Ø5.6 pan head on the Ø3.4 teardrop, 14.9 mm2 | XY comp | 10.05 | 25.00 | 2.49 | 4 | **FAIL** |
| 120 | front M2.5 x 16 pan heads driven snug, 100 N preload (sustained): bearing on the front plate | Ø5 pan head on the Ø2.8 teardrop, 13.1 mm2 | XY comp | 7.66 | 25.00 | 3.26 | 4 | **FAIL** |
| 121 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 6.07 | 25.00 | 4.12 | 2 | OK |
| 122 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 3.81 | 25.00 | 6.56 | 2 | OK |
| 123 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: top M3 pan head on the top wall, the joint's own tension (no preload) | T 24 N (y 14: 24, y -23: 1) on the Ø5.6 pan head, 14.9 mm2 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 1.64 | 25.00 | 15.24 | 2 | OK |
| 124 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.24 | 25.00 | 20.14 | 2 | OK |
| 125 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.09 | 25.00 | 287.05 | 2 | OK |
| 126 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.48 | 25.00 | 51.69 | 2 | OK |
| 127 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.46 | 25.00 | 10.15 | 2 | OK |
| 128 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: second tie's post under the lip (z 35.25..36.75) | 8 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.98 | 25.00 | 25.40 | 2 | OK |
| 129 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.87 | 25.00 | 8.71 | 2 | OK |
| 130 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.11 | 25.00 | 11.85 | 2 | OK |
| 131 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: second post's foot below the web (z 18.05..19.25), the anchor's reaction | 8 x 8.96 net of the Ø3.6 hole (A 60.7, I 373.5), Fx 24.6 N at z 17.70, lift +44.7 N + wedge 24.6 N, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 2.16 | 25.00 | 11.56 | 2 | OK |
| 132 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: second post's foot: shear across it (z 19.25) | A 60.7, Fx 32.6 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY shear | 0.81 | 12.50 | 15.52 | 2 | OK |
| 133 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: M3 x 45 anchor: pull-out from the frame's rail block (10.56 engaged), preload (if any) + wedge lift + lift | screw 195 N, thread cylinder Ø3 x 10.56 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | Z shear (frame) | 1.95 | 6.25 | 3.20 | 2 | OK |
| 134 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: V-ridge: flank bearing on the groove's 45° flank (contact band z 17.35..17.80: the seated tip, after the anchor's least crush, to the printed top corner) | normal 46.1 N on 0.63 x 7.3 (the 0.7 lead-in ignored) [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | bearing | 10.01 | 25.00 | 2.50 | 2 | OK |
| 135 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: V-ridge root at the foot's flats (z 18.05): shear | 2.0 x 7.3, Fx 32.6 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY shear | 3.35 | 12.50 | 3.73 | 2 | OK |
| 136 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: V-ridge root at the foot's flats (printed, x 14.35..16.35): the flank force's moment (0.50 Fx, resultant at the two upper corners, z 17.7) + the wedge's compression, Kt 1.7 | 2.0 x 7.3, M 16.3 N.mm, Kt 1.7 (bead-filled 135° root corners); compression and bending added in magnitude [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 7.93 | 25.00 | 3.15 | 2 | OK |
| 137 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.39 | 25.00 | 63.95 | 2 | OK |
| 138 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.96 | 25.00 | 25.98 | 2 | OK |
| 139 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.23 | 25.00 | 106.60 | 2 | OK |
| 140 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.27 | 25.00 | 91.05 | 2 | OK |
| 141 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 1 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | Z shear | 0.01 | 6.25 | 766.96 | 2 | OK |
| 142 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 1 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.05 | 25.00 | 463.64 | 2 | OK |
| 143 | spec §8 proof 1: jaw B pushed towards the other, R 34.2 N: plate strip at the tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 2.52 MPa) | XY | 10.45 | 25.00 | 2.39 | 2 | OK |
| 144 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 4.44 | 25.00 | 5.63 | 2 | OK |
| 145 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 2.70 | 25.00 | 9.25 | 2 | OK |
| 146 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: top M3 pan head on the top wall, the joint's own tension (no preload) | T 17 N (y 14: 7, y -23: 17) on the Ø5.6 pan head, 14.9 mm2 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY comp | 1.15 | 25.00 | 21.69 | 2 | OK |
| 147 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge on both flanks, play 0 (nominal, RSS)] | XY | 2.42 | 25.00 | 10.35 | 2 | OK |
| 148 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 6.99 | 25.00 | 3.58 | 2 | OK |
| 149 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 3.82 | 25.00 | 6.55 | 2 | OK |
| 150 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.75 | 25.00 | 14.31 | 2 | OK |
| 151 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 4 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | Z shear | 0.05 | 6.25 | 120.54 | 2 | OK |
| 152 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 4 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY comp | 0.34 | 25.00 | 72.87 | 2 | OK |
| 153 | spec §8 proof 1: jaw A pushed towards the other, R 34.2 N: plate strip at the tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 2.52 MPa) | XY | 10.45 | 25.00 | 2.39 | 2 | OK |
| 154 | spec §8 proof 1: 32 N pulls a jaw away, jaws 30 open: rack A's -y end at the lip's end, R 34.2 N | lip root at the top wall, rack side (Kt 2.5): b_eff 7.9, t 8.0, lever 5.9 | XY | 5.98 | 25.00 | 4.18 | 2 | OK |
| 155 | spec §8 proof 1: the same, rack A's +y end on the upper piece near slot A's end | front plate at the top wall (Kt 1.5): b_eff 7.1, t 5.0, lever 5.1 | XY | 8.86 | 25.00 | 2.82 | 2 | OK |
| 156 | spec §8 proof 2: 10.7 N on jaw B's tip towards the wrist, jaws closed | strip 11.75 x 5 | Z | 2.55 | 12.50 | 4.90 | 2 | OK |
| 157 | spec §8 proof 2: 10.7 N on jaw B's tip towards the wrist, jaws 44 open | strip 11.75 x 5 | Z | 3.82 | 12.50 | 3.27 | 2 | OK |

Information rows (not in the verdict):
| 158 | info: opening stall on jaw B, upper piece WITHOUT the second tie (round 2's model) | beside slot A's V apex (z 43.4): b 21.0 x 5, lever 26.2, Kt 1.5 | XY | 12.12 | 25.00 | 2.06 | 3 | **FAIL** |
| 159 | info: opening stall on jaw B, upper piece WITHOUT the second tie (round 2's model) | top-wall junction (z 48.5): b 25.5 x 5, lever 31.3, Kt 1.5 | XY | 11.94 | 25.00 | 2.09 | 3 | **FAIL** |
| 160 | info, bound: opening stall on jaw B with the corners rigidly coupled: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm held along z, corners rigid; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 0.69 | 25.00 | 36.24 | 3 | OK |
| 161 | info, bound: opening stall on jaw B with the corners rigidly coupled: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners rigid; ridge play 0.029 mm (worst build step 9 accepts: tip bottomed; preload gone)] | XY | 1.46 | 25.00 | 17.14 | 3 | OK |
| 162 | info: anchor preload seats the ridge, bound: all 150 N on the two 45° flanks (sustained; seating, self-limiting) | normal 106 N per flank on 0.63 x 7.3 | bearing | 23.03 | 25.00 | 1.09 | 4 | **FAIL** |
| 163 | info, bound: opening stall with zero play, Fx 25.7 N all on the groove's top layer corner (z 17.8): V-ridge root at the flats, Kt 1.7 | 2.0 x 7.3, M 18.0 N.mm (arm 0.70) | XY | 8.05 | 25.00 | 3.10 | 3 | OK |
| 164 | info: opening stall, Fx 25.7 N: V-ridge flank bearing at FIRST contact, no seating credit (band z 17.406..17.8, corners [17.6, 17.8]) | normal 36.4 N on 0.56 x 7.3 | bearing | 8.94 | 25.00 | 2.79 | 3 | **FAIL** |
| 165 | info: the +y top M3 pulls the proud top wall down (nominal: 0.079 at the screw after the anchor's seating; 0.91 of it bends the wall, 42 N): top face at the lip's back face, tension (displacement-controlled, relaxes) | cantilever L 7.6, b_eff 20.8 x 3, E 1800, Kt 1 (smooth face) | XY | 10.14 | 25.00 | 2.47 | 4 | **FAIL** |
| 166 | info: the same, nominal: the re-entrant corner under it (lip back face / top wall underside), compression | Kt 2.5 | XY comp | 25.35 | 25.00 | 0.99 | 3 | **FAIL** |
| 167 | info: the +y top M3 pulls the proud top wall down (RSS-high: 0.165 at the screw after the anchor's seating; 0.91 of it bends the wall, 87 N): top face at the lip's back face, tension (displacement-controlled, relaxes) | cantilever L 7.6, b_eff 20.8 x 3, E 1800, Kt 1 (smooth face) | XY | 21.14 | 25.00 | 1.18 | 4 | **FAIL** |
| 168 | info: the same, RSS-high: the re-entrant corner under it (lip back face / top wall underside), compression | Kt 2.5 | XY comp | 52.86 | 25.00 | 0.47 | 3 | **FAIL** |

lowest SF 2.49 (required 4): top M3 x 10 pan heads (BOM: no washer) driven snug, 150 N preload (sustained): bearing on the top wall / Ø5.6 pan head on the Ø3.4 teardrop, 14.9 mm2
VERDICT (calculation): FAIL

The script also prints the seat stack, the seating, the forced-closure numbers, the top joint's tensions, the rack A mesh
table and the what-ifs quoted above.

---

# History

- **Round 6 self-check** (cad-engineer; git 8527ef6 / 105aafe): it reported NEEDS_TEST, with lowest SF 3.01 and play
  0 / 0 / 0.029. This review replaces it. The self-check:
  - had no tolerance on the bulkhead top, the tip or the slot;
  - counted three carrying corners and took the band from the CAD tip;
  - used a 2.2 root, where the printed root is 2.0;
  - took the anchor's engagement from the CAD block top;
  - had no preload rows for the top M3 and front M2.5 heads.
- **Round 5 independent review** (git be24872): FAIL (1.84). Three stops coincided and the play was 0.082 RSS. The fix
  was ridge-first contact, which is now built and verified above.
- **Round 4** (git a701995): FAIL (the anchor's x hold relied on preload friction). Fix: the V-seat and the washer.

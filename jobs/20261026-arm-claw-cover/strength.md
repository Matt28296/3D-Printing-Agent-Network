VERDICT: FAIL

# Strength check: 20261026-arm-claw-cover (round 4)

strength-analyst (independent review of the round-4 geometry) · 2026-10-26 ·
`python3 jobs/20261026-arm-claw-cover/strength_calc.py`. It is plain python3, run from the project root (about 50 s). It
reads `claw_frame.py`, this job's, the jaw's and the frame's `model.py`, `tools/cadlib.py` and `tools/hobby_parts.py`
with `ast`. Section widths marked "probed" were measured on the solids and are written into the script as numbers.

## Summary

**The anchor is built as asked, but it holds the post's foot in x only by the preload's friction. Once that preload
creeps, the cover goes back to round 3's load path. Lowest SF 1.37** (required 3), against 1.23 in round 3: the top
wall behind the lip under an opening stall on jaw B with the jaws open (row 29).

**Why.**
- The M3 × 45 passes the cover through a Ø3.6 CAD hole (Ø3.4 printed) round a Ø3 shank, so there is 0.2 mm of radial
  clearance (0.4 with position error).
- Without friction the post's foot slides **3.6–5.0 µm per newton** of push, worst of 64 joint variants. So the shank
  only bears at **40–56 N**.
- The design pushes are below that: the opening stall is 27.0 N, the desk crash 17.2 N, and spec §8's proof push 34.2 N.
  Up to those, the push leaves the cover the round-3 way.
- The anchor still holds z (seat in compression, screw in tension), which lifts round 3's 1.23 only to 1.37.

**What the round-3 what-if assumed.** Friction 0.3 × 150 N = 45 N ≥ 25.8 N. As my "held" mode confirms:
- with that friction the cover reaches **4.14** (anchor pull-out with the lift) and every section ≥ 4.64;
- but the seat needs **≥ 94 N of clamp left at μ 0.3 (136 N at μ 0.2)** for the stall, and 119 / 172 N for the proof
  push, out of a "snug only" 150 N;
- fdm-design-rules §4 says not to count on preload lasting in PETG;
- the socket head bears straight on the top wall at 10.7 MPa, which creeps: **SF 2.34 sustained** (row 107).

**Rows under the required SF** (preload gone; 0.2 and 0.4 mm give the same):

| Row | Case | Section | SF | Req |
|---|---|---|---|---|
| 29 | Opening stall on jaw B, jaws open, 27.0 N | Top wall behind the lip, at the lip's back face | **1.37** | 3 |
| 8 | Desk crash on jaw B, 17.2 N | Same | 2.15 | 3 |
| 30 | Opening stall on jaw B | Top wall through the M3 holes over the bulkhead | 2.44 | 3 |
| 107 | Anchor snug, 150 N (sustained) | Socket head (dk 5.5) on the top wall, no washer | 2.34 | 4 |
| 110 / 111 | Spec §8 proof push on jaw B, 34.2 N | Top wall behind the lip / through the M3 holes | 1.08 / 1.93 | 2 |

**Everything round 4 adds passes in either mode:**
- the 8 mm post under the lip ≥ 9.86;
- its foot below the web ≥ 13.1;
- the anchor's pull-out from the frame 4.14 (preload + lift) / 4.42 (preload, sustained);
- the post round its hole under the clamp 9.0;
- the shank bearing 17.5 and the post's 2.2 wall 6.40, if it ever bears.

**Smallest exact fix** (computed in the script's what-if):
- a **90° V-seat** at the post's foot, beside the anchor;
- a **Ø7 × 0.5 washer** under the anchor's head.

Every cover row is then ≥ **4.64**, pull-out 4.22 on the preload and 3.41 with the wedge's lift, and the head 4.80. Details
under "Required change".

## Round-3 required change: made?

| Round-3 required change | Round 4 as built | Made? |
|---|---|---|
| TIE2_POST_T 4 → 8 | Post x 14.35–22.35 (cad_checks) | Yes |
| Post down to the rail block, z 17.75 | `TIE2_FOOT_Z` 17.75; post on the block, 0 mm³ overlap, zero nominal gap | Yes |
| Ø3.6 teardrop hole at (18.35, 28) | Yes (measure_holes, 270° arc) | Yes |
| Frame: Ø2.7 × 14 pilot | Yes (frame report: block root 5.93) | Yes |
| M3 × 45, snug ≤ 150 N | BUILD_GUIDE §1 and §4 step 9 | Yes, **but** the x hold rests on that preload (above) |

## Load cases

The stall is 216 N·mm through the 20-tooth pinion: 21.6 N on one rack, or 10.8 N per jaw. Each rack cocks in its 0.25 mm
gaps and reacts its finger's moment with end forces R = F × (x_load − 28.6) / span. The span is 56.5 with the jaws
closed, 48.4 at 30 mm open, and 41.4 at 44 mm open.

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
| 9 | **Anchor (new)** | M3 × 45 snug, 150 N | Head on the top wall, the post round its hole, pull-out from the frame | Sustained, 4 |
| 10 | **Spec §8 proof (new rows)** | 32 N at 3 mm from the tip, jaws 30: R 34.2 N; 10.7 N sideways | As 3/4 and 6 | Proof, 2 |

## Build direction and sections

- **Print direction.** The cover prints standing on its −y end (print Z = claw y), so bending in the side profile runs
  along the layers. The strip under slot B is a beam along y and bends across them.
- **Global model:** round 3's two-zone 2-D frame in the x–z plane, 64 joint variants. Two round-4 changes:
  - **The second post is 8 thick on the lip's centre line** (x 18.35). It runs straight from the lip to the web, and
    the 0.001 mm link round 3 used for a 4 mm post is dropped.
  - **Its section is probed:** 195.1 mm² net of the anchor hole at z 35.5, I_y 1090 mm⁴, so b 24.4 for area and stress.
- **Post below the web to its foot:** a rigid link to the anchor node at z 17.75. The anchor is a z support (seat in
  compression, screw in tension), plus an x spring of 3 kN/mm for friction or shank bearing.
- **Anchor modes.** Every frame-model row is the worst of three modes × 64 variants:
  - **held:** the preload's friction holds the foot from the start (round 3's what-if);
  - **slip 0.20 / slip 0.40:** the preload has gone. The foot slides freely, z still held, until it has moved 0.2 (or
    0.4) mm; after that the shank bears. Each phase is linear, so the two solves superpose. Neither gap closes below
    40 N, so these modes are the unanchored-in-x cover.
- **The post's foot below the web** (z 17.75–19.25): 8 × 9.26, net of the hole: A 63.1 mm², I_y 386 mm⁴, both probed.
  Kt 2.5 at the web's bottom corner.
- **Anchor screw:** Ø3 thread cylinder over 11.25 mm in the frame. The head is ISO 4762 dk 5.5 on a Ø3.4 printed teardrop:
  14.1 mm². The 8 × 8 post round its Ø3.6 hole: 54 mm².

## Assumptions

- **Preload.** The M3 × 45 is "snug only" at about 150 N (0.09 N·m), as in round 3. Friction μ 0.3 (0.2 as a variant).
  The preload is **not** relied on for a load path, following fdm-design-rules §4. Its friction is reported as the
  "held" mode, for comparison only.
- **Hole clearance.** Ø3.4 printed against a Ø3 shank (the thread's major diameter at the foot is 2.87–2.98) gives
  0.2 mm radial nominal and 0.4 as a bound. Below 0.04 mm every row would pass (what-if); a printed hole can't promise that.
- **Joint variants** as round 3: top wall clamped or on 1.1 × 10⁵ N·mm/rad; M2.5 3 or 30 kN/mm, held or free along z;
  plate leg 21 / 25.5; second lip 25.5 / 37.25; corner coupling 2.9 × 10⁴ / 10⁵ N·mm/rad.
- **PETG** E 1.8 GPa (placeholder); only stiffness ratios and the slip use it.
- **Temperature:** 40 °C against PETG at about 70 °C: OK.

## Allowables and sources

`library/materials.csv` has no measured row: these are the strength-checks **placeholder** PETG values. Without the
failures, NEEDS_TEST would be the best possible verdict.

| Quantity | Value | Source |
|---|---|---|
| Along the layers | 25 MPa | Skill placeholder |
| Across the layers | 12.5 MPa | 0.5 × in-plane |
| Interlayer shear | 6.25 MPa | 0.5 × 12.5 |
| Bearing | 25 MPa | In-plane value |
| Kt | 2.5 sharp; 1.5 for r ≥ 0.25 h; 1.7 for r/h 0.15–0.25; 2 at a hole | Skill |

Required SF: 3 short-term, 4 cyclic or sustained, 2 at a proof load (1.5 × service).

## Results (from `strength_calc.py`; labels shortened, the script prints them in full with the joint variant)

The bracket gives the anchor mode that governs a frame-model row: [held] means the preload's friction holds the foot;
[preload gone] means it slides. Rows without a bracket don't depend on it.

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | stall, one jaw blocked, jaws 44 open: rack A's -y end at the lip's end, R 27.0 N (the first tie's prop ignored) | lip root at the top wall, rack side (Kt 2.5): b_eff 7.9, t 8.0, lev... | XY | 4.72 | 25.00 | 5.30 | 3 | OK |
| 2 | stall, one jaw blocked, jaws closed: rack A's -y end at y -25.1, R 19.8 N | lip root at the top wall, rack side (Kt 2.5): b_eff 13.8, t 8.0, le... | XY | 1.98 | 25.00 | 12.63 | 3 | OK |
| 3 | stall, both jaws (cyclic), jaws 44 open: R 13.5 N at the lip's end | lip root at the top wall, rack side (Kt 2.5): b_eff 7.9, t 8.0, lev... | XY | 2.36 | 25.00 | 10.60 | 4 | OK |
| 4 | crash 13 N pushes jaw A shut, jaws closed: rack A's +y end on the lip at y 31.4, R 12.6 N (the second tie's prop ignored) | lip root at the top wall, rack side (Kt 2.5): b_eff 8.5, t 8.0, lev... | XY | 2.05 | 25.00 | 12.20 | 3 | OK |
| 5 | opening stall, jaw A, jaws nearly closed: rack A's +y end at y 31.4, R 19.8 N (the second tie's prop ignored) | lip root at the top wall, rack side (Kt 2.5): b_eff 8.5, t 8.0, lev... | XY | 3.22 | 25.00 | 7.77 | 3 | OK |
| 6 | stall, one jaw blocked: rack A's +y end on the upper piece near slot A's end, R 27.0 N | front plate at the top wall (Kt 1.5): b_eff 7.1, t 5.0, lever 5.1 | XY | 6.99 | 25.00 | 3.58 | 3 | OK |
| 7 | crash on jaw B, R 17.2: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 1.27 MPa) | XY | 5.25 | 25.00 | 4.76 | 3 | OK |
| 8 | crash on jaw B, R 17.2: top wall behind the lip, at the lip's back face (x 14.35) [preload gone] | 32 per zone x 3.0, Kt 2.5 | XY | 11.61 | 25.00 | **2.15** | 3 | **FAIL** |
| 9 | crash on jaw B, R 17.2: top wall over the bulkhead, through the M3 holes (x 6.75) [preload gone] | 28.4 net per zone x 3.0, Kt 2 (hole) | XY | 6.52 | 25.00 | 3.84 | 3 | OK |
| 10 | crash on jaw B, R 17.2: upper piece's plate at the web top (z 35.25, sharp inner corner) [preload gone] | b 24.1 x 5, Kt 2.5 | XY | 2.38 | 25.00 | 10.50 | 3 | OK |
| 11 | crash on jaw B, R 17.2: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) [preload gone] | b 21.0 x 5, Kt 1.5 | XY | 0.18 | 25.00 | 141.22 | 3 | OK |
| 12 | crash on jaw B, R 17.2: upper piece's plate at the top wall (z 48.5, r 2 fillet) [preload gone] | b 25.5 x 5, Kt 1.5 | XY | 0.94 | 25.00 | 26.52 | 3 | OK |
| 13 | crash on jaw B, R 17.2: top wall in front of the lip (r 2 at the plate, sharp at the lip) [preload gone] | b 25.5 x 3 | XY | 4.80 | 25.00 | 5.20 | 3 | OK |
| 14 | crash on jaw B, R 17.2: second tie's post under the lip (z 35.25..36.75) [preload gone] | 8 x 24.4, Kt 2.5 | XY | 1.61 | 25.00 | 15.48 | 3 | OK |
| 15 | crash on jaw B, R 17.2: second tie's web at the post (tension + bending) [preload gone] | 8 x 16 (45-degree parts ignored), Kt 2.5 | XY | 4.86 | 25.00 | 5.15 | 3 | OK |
| 16 | crash on jaw B, R 17.2: lip root at the top wall above the second tie [preload gone] | b 25.5 x 8, Kt 2.5 | XY | 4.20 | 25.00 | 5.96 | 3 | OK |
| 17 | crash on jaw B, R 17.2: second post's foot below the web (z 17.75..19.25), the anchor's reaction (round 4) [preload gone] | 8 x 9.26 net of the Ø3.6 hole (A 63.1, I 386.0), Fx 0.0 N, lift +76... | XY | 1.22 | 25.00 | 20.51 | 3 | OK |
| 18 | crash on jaw B, R 17.2: second post's foot: shear across it (z 19.25) [held] | A 63.1, Fx 16.4 N | XY shear | 0.39 | 12.50 | 32.06 | 3 | OK |
| 19 | crash on jaw B, R 17.2: M3 x 45 anchor: pull-out from the frame's rail block (11.25 engaged), preload (if any) + lift [held] | screw 156 N, thread cylinder Ø3 x 11.25 | Z shear (frame) | 1.48 | 6.25 | 4.24 | 3 | OK |
| 20 | crash on jaw B, R 17.2: anchor shank bearing on the post's hole after a slip (Ø3 x 2d) [held] | Fx 16.4 N on Ø3 x 6 | bearing | 0.91 | 25.00 | 27.43 | 3 | OK |
| 21 | crash on jaw B, R 17.2: post's 2.2 mm wall behind the hole: tear-out on the layer planes (y = const in print) [held] | Fx 16.4 N, 2 x 2.2 x 6 | Z shear | 0.62 | 6.25 | 10.06 | 3 | OK |
| 22 | crash on jaw B, R 17.2: lip root at the top wall above the first tie [preload gone] | b 19.75 x 8, Kt 2.5 | XY | 0.79 | 25.00 | 31.81 | 3 | OK |
| 23 | crash on jaw B, R 17.2: first tie's post under the lip [preload gone] | 8 x 8, Kt 2.5 | XY | 1.89 | 25.00 | 13.20 | 3 | OK |
| 24 | crash on jaw B, R 17.2: first tie's web at the post (tension + bending) [preload gone] | 8 x 16, Kt 2.5 | XY | 0.47 | 25.00 | 53.51 | 3 | OK |
| 25 | crash on jaw B, R 17.2: lower piece's plate between the first tie's web and the M2.5 [preload gone] | b 25 x 5 | XY | 0.56 | 25.00 | 45.00 | 3 | OK |
| 26 | crash on jaw B, R 17.2: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) [preload gone] | screw force 1 N | Z shear | 0.02 | 6.25 | 379.07 | 3 | OK |
| 27 | crash on jaw B, R 17.2: same M2.5: pan head on the cover's front plate [preload gone] | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 1 N | XY comp | 0.11 | 25.00 | 229.16 | 3 | OK |
| 28 | opening stall, jaw B, R 27.0: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 1.99 MPa) | XY | 8.25 | 25.00 | 3.03 | 3 | OK |
| 29 | opening stall, jaw B, R 27.0: top wall behind the lip, at the lip's back face (x 14.35) [preload gone] | 32 per zone x 3.0, Kt 2.5 | XY | 18.24 | 25.00 | **1.37** | 3 | **FAIL** |
| 30 | opening stall, jaw B, R 27.0: top wall over the bulkhead, through the M3 holes (x 6.75) [preload gone] | 28.4 net per zone x 3.0, Kt 2 (hole) | XY | 10.24 | 25.00 | **2.44** | 3 | **FAIL** |
| 31 | opening stall, jaw B, R 27.0: upper piece's plate at the web top (z 35.25, sharp inner corner) [preload gone] | b 24.1 x 5, Kt 2.5 | XY | 3.74 | 25.00 | 6.68 | 3 | OK |
| 32 | opening stall, jaw B, R 27.0: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) [preload gone] | b 21.0 x 5, Kt 1.5 | XY | 0.28 | 25.00 | 89.92 | 3 | OK |
| 33 | opening stall, jaw B, R 27.0: upper piece's plate at the top wall (z 48.5, r 2 fillet) [preload gone] | b 25.5 x 5, Kt 1.5 | XY | 1.48 | 25.00 | 16.89 | 3 | OK |
| 34 | opening stall, jaw B, R 27.0: top wall in front of the lip (r 2 at the plate, sharp at the lip) [preload gone] | b 25.5 x 3 | XY | 7.55 | 25.00 | 3.31 | 3 | OK |
| 35 | opening stall, jaw B, R 27.0: second tie's post under the lip (z 35.25..36.75) [preload gone] | 8 x 24.4, Kt 2.5 | XY | 2.54 | 25.00 | 9.86 | 3 | OK |
| 36 | opening stall, jaw B, R 27.0: second tie's web at the post (tension + bending) [preload gone] | 8 x 16 (45-degree parts ignored), Kt 2.5 | XY | 7.63 | 25.00 | 3.28 | 3 | OK |
| 37 | opening stall, jaw B, R 27.0: lip root at the top wall above the second tie [preload gone] | b 25.5 x 8, Kt 2.5 | XY | 6.59 | 25.00 | 3.79 | 3 | OK |
| 38 | opening stall, jaw B, R 27.0: second post's foot below the web (z 17.75..19.25), the anchor's reaction (round 4) [preload gone] | 8 x 9.26 net of the Ø3.6 hole (A 63.1, I 386.0), Fx 0.0 N, lift +12... | XY | 1.91 | 25.00 | 13.06 | 3 | OK |
| 39 | opening stall, jaw B, R 27.0: second post's foot: shear across it (z 19.25) [held] | A 63.1, Fx 25.8 N | XY shear | 0.61 | 12.50 | 20.41 | 3 | OK |
| 40 | opening stall, jaw B, R 27.0: M3 x 45 anchor: pull-out from the frame's rail block (11.25 engaged), preload (if any) + lift [held] | screw 160 N, thread cylinder Ø3 x 11.25 | Z shear (frame) | 1.51 | 6.25 | 4.14 | 3 | OK |
| 41 | opening stall, jaw B, R 27.0: anchor shank bearing on the post's hole after a slip (Ø3 x 2d) [held] | Fx 25.8 N on Ø3 x 6 | bearing | 1.43 | 25.00 | 17.47 | 3 | OK |
| 42 | opening stall, jaw B, R 27.0: post's 2.2 mm wall behind the hole: tear-out on the layer planes (y = const in print) [held] | Fx 25.8 N, 2 x 2.2 x 6 | Z shear | 0.98 | 6.25 | 6.40 | 3 | OK |
| 43 | opening stall, jaw B, R 27.0: lip root at the top wall above the first tie [preload gone] | b 19.75 x 8, Kt 2.5 | XY | 1.23 | 25.00 | 20.26 | 3 | OK |
| 44 | opening stall, jaw B, R 27.0: first tie's post under the lip [preload gone] | 8 x 8, Kt 2.5 | XY | 2.97 | 25.00 | 8.40 | 3 | OK |
| 45 | opening stall, jaw B, R 27.0: first tie's web at the post (tension + bending) [preload gone] | 8 x 16, Kt 2.5 | XY | 0.73 | 25.00 | 34.07 | 3 | OK |
| 46 | opening stall, jaw B, R 27.0: lower piece's plate between the first tie's web and the M2.5 [preload gone] | b 25 x 5 | XY | 0.87 | 25.00 | 28.65 | 3 | OK |
| 47 | opening stall, jaw B, R 27.0: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) [preload gone] | screw force 2 N | Z shear | 0.03 | 6.25 | 241.37 | 3 | OK |
| 48 | opening stall, jaw B, R 27.0: same M2.5: pan head on the cover's front plate [preload gone] | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 2 N | XY comp | 0.17 | 25.00 | 145.91 | 3 | OK |
| 49 | hand 5 N on jaw B, R 6.6: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 0.49 MPa) | XY | 2.02 | 25.00 | 12.38 | 3 | OK |
| 50 | hand 5 N on jaw B, R 6.6: top wall behind the lip, at the lip's back face (x 14.35) [preload gone] | 32 per zone x 3.0, Kt 2.5 | XY | 4.47 | 25.00 | 5.60 | 3 | OK |
| 51 | hand 5 N on jaw B, R 6.6: top wall over the bulkhead, through the M3 holes (x 6.75) [preload gone] | 28.4 net per zone x 3.0, Kt 2 (hole) | XY | 2.51 | 25.00 | 9.97 | 3 | OK |
| 52 | hand 5 N on jaw B, R 6.6: upper piece's plate at the web top (z 35.25, sharp inner corner) [preload gone] | b 24.1 x 5, Kt 2.5 | XY | 0.92 | 25.00 | 27.29 | 3 | OK |
| 53 | hand 5 N on jaw B, R 6.6: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) [preload gone] | b 21.0 x 5, Kt 1.5 | XY | 0.07 | 25.00 | 367.16 | 3 | OK |
| 54 | hand 5 N on jaw B, R 6.6: upper piece's plate at the top wall (z 48.5, r 2 fillet) [preload gone] | b 25.5 x 5, Kt 1.5 | XY | 0.36 | 25.00 | 68.95 | 3 | OK |
| 55 | hand 5 N on jaw B, R 6.6: top wall in front of the lip (r 2 at the plate, sharp at the lip) [preload gone] | b 25.5 x 3 | XY | 1.85 | 25.00 | 13.53 | 3 | OK |
| 56 | hand 5 N on jaw B, R 6.6: second tie's post under the lip (z 35.25..36.75) [preload gone] | 8 x 24.4, Kt 2.5 | XY | 0.62 | 25.00 | 40.25 | 3 | OK |
| 57 | hand 5 N on jaw B, R 6.6: second tie's web at the post (tension + bending) [preload gone] | 8 x 16 (45-degree parts ignored), Kt 2.5 | XY | 1.87 | 25.00 | 13.38 | 3 | OK |
| 58 | hand 5 N on jaw B, R 6.6: lip root at the top wall above the second tie [preload gone] | b 25.5 x 8, Kt 2.5 | XY | 1.61 | 25.00 | 15.49 | 3 | OK |
| 59 | hand 5 N on jaw B, R 6.6: second post's foot below the web (z 17.75..19.25), the anchor's reaction (round 4) [preload gone] | 8 x 9.26 net of the Ø3.6 hole (A 63.1, I 386.0), Fx 0.0 N, lift +29... | XY | 0.47 | 25.00 | 53.33 | 3 | OK |
| 60 | hand 5 N on jaw B, R 6.6: second post's foot: shear across it (z 19.25) [held] | A 63.1, Fx 6.3 N | XY shear | 0.15 | 12.50 | 83.35 | 3 | OK |
| 61 | hand 5 N on jaw B, R 6.6: M3 x 45 anchor: pull-out from the frame's rail block (11.25 engaged), preload (if any) + lift [held] | screw 152 N, thread cylinder Ø3 x 11.25 | Z shear (frame) | 1.44 | 6.25 | 4.35 | 3 | OK |
| 62 | hand 5 N on jaw B, R 6.6: anchor shank bearing on the post's hole after a slip (Ø3 x 2d) [held] | Fx 6.3 N on Ø3 x 6 | bearing | 0.35 | 25.00 | 71.33 | 3 | OK |
| 63 | hand 5 N on jaw B, R 6.6: post's 2.2 mm wall behind the hole: tear-out on the layer planes (y = const in print) [held] | Fx 6.3 N, 2 x 2.2 x 6 | Z shear | 0.24 | 6.25 | 26.15 | 3 | OK |
| 64 | hand 5 N on jaw B, R 6.6: lip root at the top wall above the first tie [preload gone] | b 19.75 x 8, Kt 2.5 | XY | 0.30 | 25.00 | 82.71 | 3 | OK |
| 65 | hand 5 N on jaw B, R 6.6: first tie's post under the lip [preload gone] | 8 x 8, Kt 2.5 | XY | 0.73 | 25.00 | 34.31 | 3 | OK |
| 66 | hand 5 N on jaw B, R 6.6: first tie's web at the post (tension + bending) [preload gone] | 8 x 16, Kt 2.5 | XY | 0.18 | 25.00 | 139.14 | 3 | OK |
| 67 | hand 5 N on jaw B, R 6.6: lower piece's plate between the first tie's web and the M2.5 [preload gone] | b 25 x 5 | XY | 0.21 | 25.00 | 117.01 | 3 | OK |
| 68 | hand 5 N on jaw B, R 6.6: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) [preload gone] | screw force 1 N | Z shear | 0.01 | 6.25 | 985.58 | 3 | OK |
| 69 | hand 5 N on jaw B, R 6.6: same M2.5: pan head on the cover's front plate [preload gone] | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 1 N | XY comp | 0.04 | 25.00 | 595.81 | 3 | OK |
| 70 | opening stall, jaw B, jaws closed: rack B's end 6.9 from the edge, R 19.8 N: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 6.15 x 5, Kt 2.5 (shear 0.96 MPa) | XY | 4.00 | 25.00 | 6.25 | 3 | OK |
| 71 | crash on jaw A, R 17.2: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 1.27 MPa) | XY | 5.25 | 25.00 | 4.76 | 3 | OK |
| 72 | crash on jaw A, R 17.2: top wall behind the lip, at the lip's back face (x 14.35) [preload gone] | 32 per zone x 3.0, Kt 2.5 | XY | 2.23 | 25.00 | 11.20 | 3 | OK |
| 73 | crash on jaw A, R 17.2: top wall over the bulkhead, through the M3 holes (x 6.75) [held] | 28.4 net per zone x 3.0, Kt 2 (hole) | XY | 1.36 | 25.00 | 18.41 | 3 | OK |
| 74 | crash on jaw A, R 17.2: lip root at the top wall above the first tie [held] | b 19.75 x 8, Kt 2.5 | XY | 1.21 | 25.00 | 20.59 | 3 | OK |
| 75 | crash on jaw A, R 17.2: first tie's post under the lip [preload gone] | 8 x 8, Kt 2.5 | XY | 3.51 | 25.00 | 7.12 | 3 | OK |
| 76 | crash on jaw A, R 17.2: first tie's web at the post (tension + bending) [preload gone] | 8 x 16, Kt 2.5 | XY | 1.92 | 25.00 | 13.03 | 3 | OK |
| 77 | crash on jaw A, R 17.2: lower piece's plate between the first tie's web and the M2.5 [preload gone] | b 25 x 5 | XY | 0.88 | 25.00 | 28.48 | 3 | OK |
| 78 | crash on jaw A, R 17.2: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) [preload gone] | screw force 2 N | Z shear | 0.03 | 6.25 | 239.92 | 3 | OK |
| 79 | crash on jaw A, R 17.2: same M2.5: pan head on the cover's front plate [preload gone] | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 2 N | XY comp | 0.17 | 25.00 | 145.04 | 3 | OK |
| 80 | opening stall, jaw A, R 27.0: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 1.99 MPa) | XY | 8.25 | 25.00 | 3.03 | 3 | OK |
| 81 | opening stall, jaw A, R 27.0: top wall behind the lip, at the lip's back face (x 14.35) [preload gone] | 32 per zone x 3.0, Kt 2.5 | XY | 3.50 | 25.00 | 7.13 | 3 | OK |
| 82 | opening stall, jaw A, R 27.0: top wall over the bulkhead, through the M3 holes (x 6.75) [held] | 28.4 net per zone x 3.0, Kt 2 (hole) | XY | 2.13 | 25.00 | 11.72 | 3 | OK |
| 83 | opening stall, jaw A, R 27.0: lip root at the top wall above the first tie [held] | b 19.75 x 8, Kt 2.5 | XY | 1.91 | 25.00 | 13.11 | 3 | OK |
| 84 | opening stall, jaw A, R 27.0: first tie's post under the lip [preload gone] | 8 x 8, Kt 2.5 | XY | 5.51 | 25.00 | 4.53 | 3 | OK |
| 85 | opening stall, jaw A, R 27.0: first tie's web at the post (tension + bending) [preload gone] | 8 x 16, Kt 2.5 | XY | 3.01 | 25.00 | 8.30 | 3 | OK |
| 86 | opening stall, jaw A, R 27.0: lower piece's plate between the first tie's web and the M2.5 [preload gone] | b 25 x 5 | XY | 1.38 | 25.00 | 18.14 | 3 | OK |
| 87 | opening stall, jaw A, R 27.0: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) [preload gone] | screw force 4 N | Z shear | 0.04 | 6.25 | 152.77 | 3 | OK |
| 88 | opening stall, jaw A, R 27.0: same M2.5: pan head on the cover's front plate [preload gone] | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 4 N | XY comp | 0.27 | 25.00 | 92.35 | 3 | OK |
| 89 | hand 5 N on jaw A, R 6.6: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 0.49 MPa) | XY | 2.02 | 25.00 | 12.38 | 3 | OK |
| 90 | hand 5 N on jaw A, R 6.6: top wall behind the lip, at the lip's back face (x 14.35) [preload gone] | 32 per zone x 3.0, Kt 2.5 | XY | 0.86 | 25.00 | 29.13 | 3 | OK |
| 91 | hand 5 N on jaw A, R 6.6: top wall over the bulkhead, through the M3 holes (x 6.75) [held] | 28.4 net per zone x 3.0, Kt 2 (hole) | XY | 0.52 | 25.00 | 47.87 | 3 | OK |
| 92 | hand 5 N on jaw A, R 6.6: lip root at the top wall above the first tie [held] | b 19.75 x 8, Kt 2.5 | XY | 0.47 | 25.00 | 53.54 | 3 | OK |
| 93 | hand 5 N on jaw A, R 6.6: first tie's post under the lip [preload gone] | 8 x 8, Kt 2.5 | XY | 1.35 | 25.00 | 18.51 | 3 | OK |
| 94 | hand 5 N on jaw A, R 6.6: first tie's web at the post (tension + bending) [preload gone] | 8 x 16, Kt 2.5 | XY | 0.74 | 25.00 | 33.87 | 3 | OK |
| 95 | hand 5 N on jaw A, R 6.6: lower piece's plate between the first tie's web and the M2.5 [preload gone] | b 25 x 5 | XY | 0.34 | 25.00 | 74.06 | 3 | OK |
| 96 | hand 5 N on jaw A, R 6.6: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) [preload gone] | screw force 1 N | Z shear | 0.01 | 6.25 | 623.80 | 3 | OK |
| 97 | hand 5 N on jaw A, R 6.6: same M2.5: pan head on the cover's front plate [preload gone] | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 1 N | XY comp | 0.07 | 25.00 | 377.10 | 3 | OK |
| 98 | opening stall, jaw A, jaws closed: rack A's end 6.9 from the edge, R 19.8 N: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 6.15 x 5, Kt 2.5 (shear 0.96 MPa) | XY | 4.00 | 25.00 | 6.25 | 3 | OK |
| 99 | stall, one jaw blocked, jaws 44 open: rack B's -y end pushes the lower piece forward (27.0 N at z 12.1): one M2.5 holds it, 108 N | pan head Ø5 on the Ø2.8 teardrop, 13.1 mm2 | XY comp | 8.30 | 25.00 | 3.01 | 3 | OK |
| 100 | stall, one jaw blocked: the same push on the lower piece's plate between the screw (z 3) and the web (z 19.25) | simply supported, b_eff 9.2 x 5 (one-sided spread at the edge) | XY | 2.82 | 25.00 | 8.86 | 3 | OK |
| 101 | yaw stall 7.1 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 25 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws closed | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 1.69 | 12.50 | 7.38 | 3 | OK |
| 102 | yaw stall 7.1 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 25 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws 44 open | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 2.53 | 12.50 | 4.93 | 3 | OK |
| 103 | hand push 5 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 18 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws closed | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 1.19 | 12.50 | 10.48 | 3 | OK |
| 104 | hand push 5 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 18 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws 44 open | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 1.78 | 12.50 | 7.00 | 3 | OK |
| 105 | rack A lift: separating 7.9 N + grip twist 410 N.mm -> 13.8 N at the rack end | top wall between the lip and the front plate, span 12.5, b 25 x 3 | XY | 1.44 | 25.00 | 17.34 | 3 | OK |
| 106 | USB tug 10 N tips the camera mount back: 53 N on the top wall's rear edge | 50 x 1 mm contact | XY | 1.06 | 25.00 | 23.67 | 3 | OK |
| 107 | anchor M3 x 45 driven snug: socket head (dk 5.5) on the top wall, preload 150 N (sustained) | 14.1 mm2 round the Ø3.4 teardrop, no washer (BUILD_GUIDE lists none) | XY comp | 10.67 | 25.00 | **2.34** | 4 | **FAIL** |
| 108 | anchor preload 150 N through the stack (sustained): the 8 x 8 post round its Ø3.6 hole | 54 mm2 (the full-depth part only; the 45-degree part ignored) | XY comp | 2.79 | 25.00 | 8.97 | 4 | OK |
| 109 | anchor preload 150 N (sustained): M3 x 45 pull-out from the frame's rail block | thread cylinder Ø3 x 11.25 (Ø2.7 x 14 pilot) | Z shear (frame) | 1.41 | 6.25 | 4.42 | 4 | OK |
| 110 | §8 proof 1, jaw B pushed in, R 34.2: top wall behind the lip, at the lip's back face (x 14.35) [preload gone] | 32 per zone x 3.0, Kt 2.5 | XY | 23.11 | 25.00 | **1.08** | 2 | **FAIL** |
| 111 | §8 proof 1, jaw B pushed in, R 34.2: top wall over the bulkhead, through the M3 holes (x 6.75) [preload gone] | 28.4 net per zone x 3.0, Kt 2 (hole) | XY | 12.97 | 25.00 | **1.93** | 2 | **FAIL** |
| 112 | §8 proof 1, jaw B pushed in, R 34.2: upper piece's plate at the web top (z 35.25, sharp inner corner) [preload gone] | b 24.1 x 5, Kt 2.5 | XY | 4.74 | 25.00 | 5.27 | 2 | OK |
| 113 | §8 proof 1, jaw B pushed in, R 34.2: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) [preload gone] | b 21.0 x 5, Kt 1.5 | XY | 0.35 | 25.00 | 70.95 | 2 | OK |
| 114 | §8 proof 1, jaw B pushed in, R 34.2: upper piece's plate at the top wall (z 48.5, r 2 fillet) [preload gone] | b 25.5 x 5, Kt 1.5 | XY | 1.88 | 25.00 | 13.32 | 2 | OK |
| 115 | §8 proof 1, jaw B pushed in, R 34.2: top wall in front of the lip (r 2 at the plate, sharp at the lip) [preload gone] | b 25.5 x 3 | XY | 9.56 | 25.00 | 2.61 | 2 | OK |
| 116 | §8 proof 1, jaw B pushed in, R 34.2: second tie's post under the lip (z 35.25..36.75) [preload gone] | 8 x 24.4, Kt 2.5 | XY | 3.21 | 25.00 | 7.78 | 2 | OK |
| 117 | §8 proof 1, jaw B pushed in, R 34.2: second tie's web at the post (tension + bending) [preload gone] | 8 x 16 (45-degree parts ignored), Kt 2.5 | XY | 9.67 | 25.00 | 2.59 | 2 | OK |
| 118 | §8 proof 1, jaw B pushed in, R 34.2: lip root at the top wall above the second tie [preload gone] | b 25.5 x 8, Kt 2.5 | XY | 8.35 | 25.00 | 2.99 | 2 | OK |
| 119 | §8 proof 1, jaw B pushed in, R 34.2: second post's foot below the web (z 17.75..19.25), the anchor's reaction (round 4) [preload gone] | 8 x 9.26 net of the Ø3.6 hole (A 63.1, I 386.0), Fx 0.0 N, lift +15... | XY | 2.43 | 25.00 | 10.31 | 2 | OK |
| 120 | §8 proof 1, jaw B pushed in, R 34.2: second post's foot: shear across it (z 19.25) [held] | A 63.1, Fx 32.6 N | XY shear | 0.78 | 12.50 | 16.11 | 2 | OK |
| 121 | §8 proof 1, jaw B pushed in, R 34.2: M3 x 45 anchor: pull-out from the frame's rail block (11.25 engaged), preload (if any) + lift [held] | screw 163 N, thread cylinder Ø3 x 11.25 | Z shear (frame) | 1.53 | 6.25 | 4.07 | 2 | OK |
| 122 | §8 proof 1, jaw B pushed in, R 34.2: anchor shank bearing on the post's hole after a slip (Ø3 x 2d) [held] | Fx 32.6 N on Ø3 x 6 | bearing | 1.81 | 25.00 | 13.78 | 2 | OK |
| 123 | §8 proof 1, jaw B pushed in, R 34.2: post's 2.2 mm wall behind the hole: tear-out on the layer planes (y = const in print) [held] | Fx 32.6 N, 2 x 2.2 x 6 | Z shear | 1.24 | 6.25 | 5.05 | 2 | OK |
| 124 | §8 proof 1, jaw B pushed in, R 34.2: lip root at the top wall above the first tie [preload gone] | b 19.75 x 8, Kt 2.5 | XY | 1.56 | 25.00 | 15.98 | 2 | OK |
| 125 | §8 proof 1, jaw B pushed in, R 34.2: first tie's post under the lip [preload gone] | 8 x 8, Kt 2.5 | XY | 3.77 | 25.00 | 6.63 | 2 | OK |
| 126 | §8 proof 1, jaw B pushed in, R 34.2: first tie's web at the post (tension + bending) [preload gone] | 8 x 16, Kt 2.5 | XY | 0.93 | 25.00 | 26.89 | 2 | OK |
| 127 | §8 proof 1, jaw B pushed in, R 34.2: lower piece's plate between the first tie's web and the M2.5 [preload gone] | b 25 x 5 | XY | 1.11 | 25.00 | 22.61 | 2 | OK |
| 128 | §8 proof 1, jaw B pushed in, R 34.2: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) [preload gone] | screw force 3 N | Z shear | 0.03 | 6.25 | 190.46 | 2 | OK |
| 129 | §8 proof 1, jaw B pushed in, R 34.2: same M2.5: pan head on the cover's front plate [preload gone] | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 3 N | XY comp | 0.22 | 25.00 | 115.14 | 2 | OK |
| 130 | spec §8 proof 1: jaw B pushed towards the other, R 34.2 N: plate strip at the tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 2.52 MPa) | XY | 10.45 | 25.00 | 2.39 | 2 | OK |
| 131 | §8 proof 1, jaw A pushed in, R 34.2: top wall behind the lip, at the lip's back face (x 14.35) [preload gone] | 32 per zone x 3.0, Kt 2.5 | XY | 4.44 | 25.00 | 5.63 | 2 | OK |
| 132 | §8 proof 1, jaw A pushed in, R 34.2: top wall over the bulkhead, through the M3 holes (x 6.75) [held] | 28.4 net per zone x 3.0, Kt 2 (hole) | XY | 2.70 | 25.00 | 9.25 | 2 | OK |
| 133 | §8 proof 1, jaw A pushed in, R 34.2: lip root at the top wall above the first tie [held] | b 19.75 x 8, Kt 2.5 | XY | 2.42 | 25.00 | 10.35 | 2 | OK |
| 134 | §8 proof 1, jaw A pushed in, R 34.2: first tie's post under the lip [preload gone] | 8 x 8, Kt 2.5 | XY | 6.99 | 25.00 | 3.58 | 2 | OK |
| 135 | §8 proof 1, jaw A pushed in, R 34.2: first tie's web at the post (tension + bending) [preload gone] | 8 x 16, Kt 2.5 | XY | 3.82 | 25.00 | 6.55 | 2 | OK |
| 136 | §8 proof 1, jaw A pushed in, R 34.2: lower piece's plate between the first tie's web and the M2.5 [preload gone] | b 25 x 5 | XY | 1.75 | 25.00 | 14.31 | 2 | OK |
| 137 | §8 proof 1, jaw A pushed in, R 34.2: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) [preload gone] | screw force 4 N | Z shear | 0.05 | 6.25 | 120.55 | 2 | OK |
| 138 | §8 proof 1, jaw A pushed in, R 34.2: same M2.5: pan head on the cover's front plate [preload gone] | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 4 N | XY comp | 0.34 | 25.00 | 72.87 | 2 | OK |
| 139 | spec §8 proof 1: jaw A pushed towards the other, R 34.2 N: plate strip at the tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 2.52 MPa) | XY | 10.45 | 25.00 | 2.39 | 2 | OK |
| 140 | spec §8 proof 1: 32 N pulls a jaw away, jaws 30 open: rack A's -y end at the lip's end, R 34.2 N | lip root at the top wall, rack side (Kt 2.5): b_eff 7.9, t 8.0, lev... | XY | 5.98 | 25.00 | 4.18 | 2 | OK |
| 141 | spec §8 proof 1: the same, rack A's +y end on the upper piece near slot A's end | front plate at the top wall (Kt 1.5): b_eff 7.1, t 5.0, lever 5.1 | XY | 8.86 | 25.00 | 2.82 | 2 | OK |
| 142 | spec §8 proof 2: 10.7 N on jaw B's tip towards the wrist, jaws closed | strip 11.75 x 5 | Z | 2.55 | 12.50 | 4.90 | 2 | OK |
| 143 | spec §8 proof 2: 10.7 N on jaw B's tip towards the wrist, jaws 44 open | strip 11.75 x 5 | Z | 3.82 | 12.50 | 3.27 | 2 | OK |
| 144 | info: opening stall on jaw B, upper piece WITHOUT the second tie (round 2's model) | beside slot A's V apex (z 43.4): b 21.0 x 5, lever 26.2, Kt 1.5 | XY | 12.12 | 25.00 | **2.06** | 3 | **FAIL** |
| 145 | info: opening stall on jaw B, upper piece WITHOUT the second tie (round 2's model) | top-wall junction (z 48.5): b 25.5 x 5, lever 31.3, Kt 1.5 | XY | 11.94 | 25.00 | **2.09** | 3 | **FAIL** |
| 146 | info, bound: opening stall on jaw B with the corners rigidly coupled: lip root at the top wall above the first tie [preload gone] | b 19.75 x 8, Kt 2.5 | XY | 1.94 | 25.00 | 12.89 | 3 | OK |
| 147 | info, bound: opening stall on jaw B with the corners rigidly coupled: first tie's post under the lip [preload gone] | 8 x 8, Kt 2.5 | XY | 4.23 | 25.00 | 5.90 | 3 | OK |

Rows 144–147 are information rows (not in the verdict):
- the upper piece without the second tie (round 2's model): 2.06 / 2.09;
- the bound with the zone corners rigidly coupled: 12.9 / 5.90.

**Lowest SF 1.37 (required 3), row 29:** the top wall behind the lip, opening stall on jaw B, with the preload gone.

**Failing rows:**
- 8 (crash, 2.15);
- 30 (top wall through the M3 holes, 2.44);
- 107 (the anchor's bare head on the top wall at the snug preload, sustained, 2.34);
- 110 / 111 (spec §8 proof push on jaw B, 1.08 / 1.93, at 2 required).

The lowest passing rows are:
- the plate strip under the second web, 3.03;
- the second web at the post, 3.28;
- the top wall in front of the lip, 3.31;
- rack A's grip on the upper piece, 3.58.

### The two anchor modes side by side (worst of 64 variants)

| Case | Held by preload friction | Preload gone (0.2 or 0.4 mm) | FIX (V-seat: x held positively) |
|---|---|---|---|
| Opening stall, jaw B, 27.0 N | 4.14 (anchor pull-out, preload + lift) | **1.37** (top wall behind the lip) | 6.40 / every section ≥ 4.64 |
| Crash, jaw B, 17.2 N | 4.24 | **2.15** | 10.1 |
| Hand push, jaw B, 6.6 N | 4.35 | 5.60 | 26.2 |
| Opening stall, jaw A, 27.0 N | 4.64 (first tie's post) | 4.53 | 4.64 |
| Spec §8 proof push, jaw B, 34.2 N (req 2) | 4.07 | **1.08** | 5.05 |
| Spec §8 proof push, jaw A, 34.2 N (req 2) | 3.66 | 3.58 | 3.66 |

**What the foot does without friction.** It slides 3.6–5.0 µm per newton, so:
- 0.2 mm closes at 40.3–55.7 N;
- 0.4 mm closes at 80.7–111.4 N.

Residual gap against lowest SF:

| Gap (mm) | 0 | 0.025 | 0.04 | 0.05 | 0.075 | 0.1 |
|---|---|---|---|---|---|---|
| Lowest SF | 4.64 | 4.53 | 3.39 | 2.82 | 1.98 | 1.54 |

**Clamp the seat's friction needs (preload − lift ≥ Fx / μ):**

| Case | μ 0.3 | μ 0.2 |
|---|---|---|
| Opening stall | 94 N | 136 N |
| Crash | 60 N | 87 N |
| Spec §8 proof push | 119 N | 172 N |

"Snug only" is about 150 N on the day it is driven, under a bare socket head at 10.7 MPa.

## Required change (FAIL): the smallest exact fix

**Hold the post's foot in x by geometry, with the screw in tension, and put a washer under the anchor's head.** The
script's what-if computes it.

1. **Frame (`model.py`, rail block):** a 90° V-groove along y in the block's top.
   - Centre x 15.25; 0.8 deep (x 14.45–16.05 at z 17.75, bottom z 16.95); y 23.5 → 32, open at the +y end.
   - 0.95 mm of block stays between its edge and the anchor pilot at the top.
   - The pilot (Ø2.7 × 14) does not change.
2. **Cover (`model.py`, second tie's post):** the matching 90° V-ridge under the foot.
   - The same flanks. The tip is truncated 0.15 (z 17.10), so it never bottoms.
   - Base x 14.35–16.15, y 24 → 32, with a 45° lead-in over its first 0.8 continuing the post's underside.
   - `TIE2_FOOT_Z` 17.75 → **17.85**, so the flanks seat and the flats stand 0.1 clear.
   - The anchor hole is unchanged.
3. **Hardware (BUILD_GUIDE §1 and §4 step 9):** an M3 washer Ø7 × 0.5 (ISO 7089) under the M3 × 45's head. The dry-fit
   check becomes "ridge in the groove, top wall on the bulkhead, a 0.1 feeler won't enter at the top wall".

**What it gives:**
- A +x push on the foot rides up a 45° flank. The screw holds that in tension, which needs neither friction nor preload.
  The cover model with x held: **every section ≥ 4.64** (the first tie's post, under jaw A's stall, unchanged).
- Anchor forces: Fx 25.8 N and lift 10.1 N at the stall; Fx 32.6 N at the proof push.
- **Flank bearing** 5.50 MPa on 0.92 × 7.2 mm: SF 4.5. **Ridge root** (a vertical plane in print, along the layers):
  3.35 MPa against 12.5 in shear, SF 3.7. **The frame's block in front of the groove**, 40 mm² of interlayer shear at the
  groove's bottom: SF 6.4.
- **M3 × 45 + washer:** 10.75 engaged. Pull-out on the preload 4.22 (req 4). With the preload, the wedge's lift (= Fx,
  frictionless) and the lift, 186 N: 3.41 (req 3).
- **Head on the washer:** 4.80 (req 4).
- **Residual x play** after seating equals the stack's creep under the head. Every row stays ≥ 4.5 up to 0.025 mm.

**Why nothing smaller:**
- **A washer alone** leaves the hold on friction.
- **A close-fitting hole at the foot** must stay ≤ 0.04 mm radial; 0.05 gives 2.82, and a printed hole can't promise it.
- **Letting the M3 form its thread in the post's foot** puts the forming pressure's hoop across the post's layers: the
  Lamé peak gives about 2.2 at installation by the frame's own method. The head's preload would also then react in the
  cover's foot thread.
- **Stiffening the cover instead** gave ≤ 2.92 for any single change in round 3.

After the change:
- update cad_checks;
- re-run claw_sequence_check (the ridge enters the groove in the cover's last 0.8 mm of descent);
- run the DFM layer check for the ridge's lead-in;
- re-run this script with the V-seat in the model (`ANCHOR_KX` stays 3 kN/mm, as the "held" mode but without relying on
  preload).

## Proof test (spec §8)

- **The loads still match the design cases.**
  - Step 1's 32 N push towards the other jaw is 1.5 × the opening stall; at 30 mm open, R is 34.2 N.
  - The 32 N pull is 1.5 × the one-jaw stall: lip root 4.18, front plate at the top wall 2.82.
  - Step 2's 10.7 N sideways: strip under slot B 4.90 / 3.27.
- **Do not run step 1's push on jaw B on the as-built cover.**
  - It needs ≥ 119 N of clamp left at the seat (μ 0.3).
  - If the foot slips, the top wall behind the lip is at SF 1.08 at the proof load and would probably crack along the
    lip's back face.
  - A fresh, snugged anchor would probably pass the test, but that wouldn't show the design is safe: the preload it
    relies on relaxes afterwards.
- **With the fix, every proof row ≥ 2.39** (the plate strips at the ties' webs). The proof is then valid as written, with
  "the anchored second post and its M3 × 45 (still tight)" read as "the post's ridge still seated in the frame's groove,
  and the M3 × 45 still tight".

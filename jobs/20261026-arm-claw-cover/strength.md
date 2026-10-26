VERDICT: FAIL

# Strength check: 20261026-arm-claw-cover (round 3)

strength-analyst (independent review of the round-3 geometry) · 2026-10-26 ·
`python3 jobs/20261026-arm-claw-cover/strength_calc.py` (plain python3, run from the project root: reads `claw_frame.py`,
this job's, the jaw's and the frame's `model.py`, `tools/cadlib.py` and `tools/hobby_parts.py` with `ast`; section widths
marked "probed" were measured on the round-3 solid and are written into the script as numbers)

Round 2's fixes are in and they work where round 2 put its sections:
- the 8 mm lip: 5.30 against 1.30;
- the strip under slot B at FRONT_Z0 −6: 4.93 against 2.58. The brief's 7.45 read the what-if line one step too deep;
  the line labelled "9.75 deep" was already the 11.75 strip;
- the second tie: the upper piece's own sections now pass, at ≥ 5.87;
- the front M2.5 × 16 in 14 mm pilots.

**The cover still fails, one step further along the same load path. Lowest SF 1.23.** Round 2 checked the reversed
rack-B push only on the upper piece. Neither round followed it to the frame. The push is 27 N at z 17.2 on the upper
piece's bottom strip: the claw opening against an obstacle, or 17.2 N from the 13 N desk crash on jaw B.

It is a force on the cover whose reaction sits on the frame (rack B's other end bears on the frame's rail block), so it
has to leave the cover. The cover has only two anchors:
- the top wall on the bulkhead top (2 × M3, z 48.5–51.5);
- the lower piece's 2 × M2.5 at z 3.

The upper piece reaches the M2.5s only through the second tie, the lip, the first tie and the lower piece. That path is
soft, because the lower piece hangs 33 mm below the first post. So most of the overturning moment, about
27 × (50 − 17.2) = 890 N·mm, goes into the 3 mm top wall between the lip and the M3 screw line. It fails in three places:

| Where | Opening stall (jaw B) | Crash (jaw B) |
|---|---|---|
| At the lip's back face | **1.23** | 1.94 |
| Through the M3 holes over the bulkhead | 1.53 | 2.40 |
| First tie's 8 × 8 post, the part of the push that does go round through the lower piece | 1.56 | 2.45 |
| Top wall in front of the lip | 2.92 | — |

**Robustness.** The joints to the frame are uncertain, so each row is the worst of 64 variants:
- the top wall clamped, or on a rotational spring;
- the M2.5 stiff or soft, held along z or free;
- the plate leg, lip and top-wall widths;
- the coupling between the two lip corners.

The most favourable variant still gives 1.46. **The fix (below) is to anchor the second tie's post on the frame's rail
block with one vertical M3.** That takes about 25 of the 27 N straight into the frame, and every row then gives ≥ 4.64.

Without the second tie this load would fail the upper piece itself (2.06, information rows). The tie moved the
weakness; it didn't remove it.

## Round-2 fixes: made?

| Round-2 required change | Round 3 | Made? |
|---|---|---|
| 1. GUIDE_T 4 → 8 (lip and the first post) | GUIDE_T 8, lip x 14.35–22.35; first post 8 × 8 | Yes: lip 5.30 (row 1), lip above the first post ≥ 3.37 in the global model |
| 2. Upper piece: a second tie at y 24–32 (or FRONT_T 7) | Second tie: post 4 thick (x 18.35–22.35) growing from the lip (24.3 wide at the lip, probed), web full height for y ≥ 24, 45° undersides | Made. The upper piece's own sections pass (≥ 5.87). The load path beyond it fails: see above |
| 3. Strip under slot B: FRONT_Z0 −6 | FRONT_Z0 −6 (strip 11.75) | Yes: 4.93 (row 87) |
| Row 22: the M2.5 share | M2.5 × 16, 11 engaged | Yes. The global model gives the M2.5 3–14 N under the reversed pushes |

## Load cases

The stall is 216 N·mm through the 20-tooth pinion: 21.6 N on one rack (one jaw blocked) or 10.8 N per jaw. Each rack
cocks in its 0.25 gaps and reacts its finger's moment with end forces R = F × (x_load − 28.6) / span. The span is 56.5
with the jaws closed, or 41.4 with them 44 mm open (the rack's end past the cover's edge).

| # | Case | Load | Where it lands | Type, SF req |
|---|---|---|---|---|
| 1 | Stall, one jaw blocked (spec) | 21.6 N, 3 mm from the tip: R 19.8–27.0 N | Rack A forward on the upper piece near the top wall, back on the lip's −y end; rack B forward on the lower piece's −y end | Short-term, 3 |
| 2 | Stall, both jaws, every full-close grip | Half of 1 | As 1 | Cyclic, 4 |
| 3 | **Crash** (required): fingertip on the desk | 13 N at the tip, finger pushed shut: R 12.6–17.2 N, **reversed** | Rack A forward on the lower piece's top strip (z 37.3); rack B forward on the upper piece's bottom strip (z 17.2) | Short-term, 3 |
| 4 | Opening against an obstacle (Architect: a design case) | 21.6 N on a finger's outer face: R up to 27.0 N, reversed | As 3 | Short-term, 3 |
| 5 | Handling | 5 N pushing a finger shut: R 6.6 N | As 3 | Short-term, 3 |
| 6 | Sideways push on jaw B's tip towards the wrist | Yaw stall 7.1 N; hand 5 N | Neck B on the strip under slot B | Short-term, 3 |
| 7 | Rack A lift (spec) | Separating 7.9 N + the grip's twist: 13.8 N at the rack's end | Top wall between the lip and the plate | Short-term, 3 |
| 8 | Camera on the top wall (spec) | 10 N USB tug tips the mount back | Top wall's rear edge | Short-term, 3 |

The reversed rack-B push (cases 3 and 4 on jaw B) is the one whose reaction is on the frame. Rack A's couples (cases 1
and 3 on jaw A) and rack B's grip land on the cover at both ends, or on the lower piece and its own screws.

The rack-A load on the lower piece is modelled as leaving the cover too. That is conservative for the joints: rack A's
other end pushes the lip.

## Build direction and sections

The cover prints standing on its −y end (print Z = claw y), so bending in the side profile runs along the layers:
plate, top wall, lip, posts, webs (25 MPa). The strip under slot B is a beam along y and bends across the layers.

- **Global model.** A 2-D frame in the x–z plane in two y-zones:
  - zone + (y 0…32): the upper piece's plate leg, the second tie and the top wall in front of the lip;
  - zone − (y −32…0): the first tie, the lower piece's plate to the M2.5 at z 3;
  - each zone has half of the top wall behind the lip (x 10…14.35, 32 wide) and half of the top joint.

  The two lip/top-wall corners are tied rigidly in x and z (the top wall in its own plane). In rotation they are tied
  by the torsion of the open lip + top-wall L-section between the ties: G J / L = 2.9 × 10⁴ N·mm/rad, with 10⁵ as the
  stiff variant. A fully rigid coupling is shown as an information bound (rows 94–95).

  The ties' webs, and each piece's part beside its web, are rigid links. The solver is a plain stiffness solve; every
  member's N and M go into σ = N/A + Kt·6M/(b·t²).
- **Sections and Kt:**
  - top wall at the lip's back face: sharp, 2.5;
  - top wall through the Ø3.6 M3 holes: net 28.4 per zone, Kt 2;
  - top wall in front of the lip: r 2 at the plate (1.5), sharp at the lip (2.5);
  - upper plate at the web top: sharp, 2.5; beside slot A's V apex (b 21.0 probed): 1.5; at the top wall: r 2, 1.5;
  - second post 4 × 24.3 and first post 8 × 8: sharp, 2.5;
  - lips at the top wall: 2.5;
  - webs 8 × 16: 2.5;
  - lower plate: 2.5 at the web, 2 at the M2.5 hole.
- **Local strips.** The plate strip under the second web and above the first web is a cantilever 2.07 from its web,
  with a 45° spread from a 2 mm patch at the cover's edge (b_eff 4.07). Round 2 used the full 8 mm tie width there; this
  is the as-built value. The stub is short (lever / depth 0.4), so beam theory with Kt 2.5 on top is conservative.
- **Head bearing.** The M2.5 pan head (Ø5) on the Ø2.8 teardrop: 13.1 mm².

## Assumptions

- **Joint variants** (64; every global row is the worst of them):
  - the top wall on the bulkhead top: clamped, or a rotational spring of 1.1 × 10⁵ N·mm/rad. That is a quarter of
    E·I_patch/t for the screwed 6.5 × 64 bearing patch; a pinned top isn't credible for a flat, screwed joint;
  - the M2.5 joint 3 or 30 kN/mm along x, held along z (preload friction, 30 N available) or free;
  - the plate leg 21 or 25.5 wide; the second lip 25.5 or 37.25 wide (45° spread);
  - the corner coupling 2.9 × 10⁴ or 10⁵ N·mm/rad.
- PETG E 1.8 GPa (placeholder). Only stiffness ratios use it.
- Friction is ignored in the members. The 45° parts of the second tie are ignored, which is conservative for the tie.
- When the cover is screwed on with the camera mount, the mount's pad (x 0…14) sits on the top wall behind the lip.
  It is a separate, unbonded plate and is ignored. It doesn't cover the lip's back corner at x 14.35 either way.
- Service temperature is 40 °C against PETG softening at about 70 °C: OK.

## Allowables and sources

`library/materials.csv` has no measured row, so these are the strength-checks **placeholder** PETG values, and
NEEDS_TEST is the best possible verdict.

| Quantity | Value | Source |
|---|---|---|
| Along the layers | 25 MPa | Skill placeholder |
| Across the layers | 12.5 MPa | 0.5 × in-plane |
| Interlayer shear | 6.25 MPa | 0.5 × 12.5 |
| Bearing | 25 MPa | In-plane value |
| Kt | 2.5 sharp; 1.5 for r ≥ 0.25 h; 1.7 for r/h 0.15–0.25; 2 at a hole | Skill (the 1.7 is a Peterson-based interpolation) |

## Results (copied from `python3 strength_calc.py`)

The bracketed text in a Section cell names the variant that governs that row.

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | stall, one jaw blocked, jaws 44 open: rack A's -y end at the lip's end, R 27.0 N (the first tie's prop ignored) | lip root at the top wall, rack side (Kt 2.5): b_eff 7.9, t 8.0, lever 5.9 | XY | 4.72 | 25.00 | 5.30 | 3 | OK |
| 2 | stall, one jaw blocked, jaws closed: rack A's -y end at y -25.1, R 19.8 N | lip root at the top wall, rack side (Kt 2.5): b_eff 13.8, t 8.0, lever 5.9 | XY | 1.98 | 25.00 | 12.63 | 3 | OK |
| 3 | stall, both jaws (cyclic), jaws 44 open: R 13.5 N at the lip's end | lip root at the top wall, rack side (Kt 2.5): b_eff 7.9, t 8.0, lever 5.9 | XY | 2.36 | 25.00 | 10.60 | 4 | OK |
| 4 | crash 13 N pushes jaw A shut, jaws closed: rack A's +y end on the lip at y 31.4, R 12.6 N (the second tie's prop ignored) | lip root at the top wall, rack side (Kt 2.5): b_eff 8.5, t 8.0, lever 5.9 | XY | 2.05 | 25.00 | 12.20 | 3 | OK |
| 5 | added: opening against an obstacle, jaw A, jaws nearly closed: rack A's +y end at y 31.4, R 19.8 N (the second tie's prop ignored) | lip root at the top wall, rack side (Kt 2.5): b_eff 8.5, t 8.0, lever 5.9 | XY | 3.22 | 25.00 | 7.77 | 3 | OK |
| 6 | stall, one jaw blocked: rack A's +y end on the upper piece near slot A's end, R 27.0 N | front plate at the top wall (Kt 1.5): b_eff 7.1, t 5.0, lever 5.1 | XY | 6.99 | 25.00 | 3.58 | 3 | OK |
| 7 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 1.27 MPa) | XY | 5.25 | 25.00 | 4.76 | 3 | OK |
| 8 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad] | XY | 12.89 | 25.00 | 1.94 | 3 | **FAIL** |
| 9 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad] | XY | 10.41 | 25.00 | 2.40 | 3 | **FAIL** |
| 10 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 2.71 | 25.00 | 9.22 | 3 | OK |
| 11 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 2.9e+04 N.mm/rad] | XY | 0.21 | 25.00 | 117.51 | 3 | OK |
| 12 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad] | XY | 1.10 | 25.00 | 22.66 | 3 | OK |
| 13 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 5.45 | 25.00 | 4.59 | 3 | OK |
| 14 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: second tie's post under the lip (z 35.25..36.75) | 4 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 3.29 | 25.00 | 7.59 | 3 | OK |
| 15 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 2.38 | 25.00 | 10.49 | 3 | OK |
| 16 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 3.67 | 25.00 | 6.82 | 3 | OK |
| 17 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 4.73 | 25.00 | 5.29 | 3 | OK |
| 18 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad] | XY | 10.22 | 25.00 | 2.45 | 3 | **FAIL** |
| 19 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm held along z, corners 2.9e+04 N.mm/rad] | XY | 2.68 | 25.00 | 9.32 | 3 | OK |
| 20 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 3.41 | 25.00 | 7.32 | 3 | OK |
| 21 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 9 N [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad] | Z shear | 0.10 | 6.25 | 61.70 | 3 | OK |
| 22 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 9 N [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY comp | 0.67 | 25.00 | 37.30 | 3 | OK |
| 23 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 1.99 MPa) | XY | 8.25 | 25.00 | 3.03 | 3 | OK |
| 24 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad] | XY | 20.24 | 25.00 | 1.23 | 3 | **FAIL** |
| 25 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad] | XY | 16.35 | 25.00 | 1.53 | 3 | **FAIL** |
| 26 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 4.26 | 25.00 | 5.87 | 3 | OK |
| 27 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 2.9e+04 N.mm/rad] | XY | 0.33 | 25.00 | 74.82 | 3 | OK |
| 28 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad] | XY | 1.73 | 25.00 | 14.43 | 3 | OK |
| 29 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 8.55 | 25.00 | 2.92 | 3 | **FAIL** |
| 30 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: second tie's post under the lip (z 35.25..36.75) | 4 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 5.17 | 25.00 | 4.83 | 3 | OK |
| 31 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 3.74 | 25.00 | 6.68 | 3 | OK |
| 32 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 5.76 | 25.00 | 4.34 | 3 | OK |
| 33 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 7.42 | 25.00 | 3.37 | 3 | OK |
| 34 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad] | XY | 16.05 | 25.00 | 1.56 | 3 | **FAIL** |
| 35 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm held along z, corners 2.9e+04 N.mm/rad] | XY | 4.21 | 25.00 | 5.93 | 3 | OK |
| 36 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 5.36 | 25.00 | 4.66 | 3 | OK |
| 37 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 14 N [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad] | Z shear | 0.16 | 6.25 | 39.28 | 3 | OK |
| 38 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 14 N [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY comp | 1.05 | 25.00 | 23.75 | 3 | OK |
| 39 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 0.49 MPa) | XY | 2.02 | 25.00 | 12.38 | 3 | OK |
| 40 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad] | XY | 4.96 | 25.00 | 5.04 | 3 | OK |
| 41 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad] | XY | 4.00 | 25.00 | 6.24 | 3 | OK |
| 42 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 1.04 | 25.00 | 23.96 | 3 | OK |
| 43 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 2.9e+04 N.mm/rad] | XY | 0.08 | 25.00 | 305.51 | 3 | OK |
| 44 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad] | XY | 0.42 | 25.00 | 58.92 | 3 | OK |
| 45 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 2.09 | 25.00 | 11.93 | 3 | OK |
| 46 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: second tie's post under the lip (z 35.25..36.75) | 4 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 1.27 | 25.00 | 19.73 | 3 | OK |
| 47 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 0.92 | 25.00 | 27.27 | 3 | OK |
| 48 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 1.41 | 25.00 | 17.72 | 3 | OK |
| 49 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 1.82 | 25.00 | 13.75 | 3 | OK |
| 50 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad] | XY | 3.93 | 25.00 | 6.36 | 3 | OK |
| 51 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm held along z, corners 2.9e+04 N.mm/rad] | XY | 1.03 | 25.00 | 24.22 | 3 | OK |
| 52 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY | 1.31 | 25.00 | 19.04 | 3 | OK |
| 53 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 3 N [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad] | Z shear | 0.04 | 6.25 | 160.41 | 3 | OK |
| 54 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 3 N [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad] | XY comp | 0.26 | 25.00 | 96.97 | 3 | OK |
| 55 | added: opening against an obstacle, jaw B, jaws closed: rack B's end 6.9 from the edge, R 19.8 N: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 6.15 x 5, Kt 2.5 (shear 0.96 MPa) | XY | 4.00 | 25.00 | 6.25 | 3 | OK |
| 56 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 1.27 MPa) | XY | 5.25 | 25.00 | 4.76 | 3 | OK |
| 57 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad] | XY | 1.70 | 25.00 | 14.74 | 3 | OK |
| 58 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad] | XY | 1.37 | 25.00 | 18.22 | 3 | OK |
| 59 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad] | XY | 0.58 | 25.00 | 42.82 | 3 | OK |
| 60 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad] | XY | 5.25 | 25.00 | 4.76 | 3 | OK |
| 61 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad] | XY | 2.38 | 25.00 | 10.49 | 3 | OK |
| 62 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad] | XY | 1.52 | 25.00 | 16.43 | 3 | OK |
| 63 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 4 N [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad] | Z shear | 0.05 | 6.25 | 138.37 | 3 | OK |
| 64 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 4 N [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad] | XY comp | 0.30 | 25.00 | 83.65 | 3 | OK |
| 65 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 1.99 MPa) | XY | 8.25 | 25.00 | 3.03 | 3 | OK |
| 66 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad] | XY | 2.66 | 25.00 | 9.39 | 3 | OK |
| 67 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad] | XY | 2.16 | 25.00 | 11.60 | 3 | OK |
| 68 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad] | XY | 0.92 | 25.00 | 27.27 | 3 | OK |
| 69 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad] | XY | 8.25 | 25.00 | 3.03 | 3 | OK |
| 70 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad] | XY | 3.74 | 25.00 | 6.68 | 3 | OK |
| 71 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad] | XY | 2.39 | 25.00 | 10.46 | 3 | OK |
| 72 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 6 N [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad] | Z shear | 0.07 | 6.25 | 88.10 | 3 | OK |
| 73 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 6 N [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad] | XY comp | 0.47 | 25.00 | 53.26 | 3 | OK |
| 74 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 0.49 MPa) | XY | 2.02 | 25.00 | 12.38 | 3 | OK |
| 75 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad] | XY | 0.65 | 25.00 | 38.32 | 3 | OK |
| 76 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad] | XY | 0.53 | 25.00 | 47.37 | 3 | OK |
| 77 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad] | XY | 0.22 | 25.00 | 111.33 | 3 | OK |
| 78 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad] | XY | 2.02 | 25.00 | 12.37 | 3 | OK |
| 79 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad] | XY | 0.92 | 25.00 | 27.27 | 3 | OK |
| 80 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad] | XY | 0.59 | 25.00 | 42.71 | 3 | OK |
| 81 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 2 N [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad] | Z shear | 0.02 | 6.25 | 359.75 | 3 | OK |
| 82 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 2 N [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad] | XY comp | 0.11 | 25.00 | 217.48 | 3 | OK |
| 83 | added: opening against an obstacle, jaw A, jaws closed: rack A's end 6.9 from the edge, R 19.8 N: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 6.15 x 5, Kt 2.5 (shear 0.96 MPa) | XY | 4.00 | 25.00 | 6.25 | 3 | OK |
| 84 | stall, one jaw blocked, jaws 44 open: rack B's -y end pushes the lower piece forward (27.0 N at z 12.1): one M2.5 holds it, 108 N | pan head Ø5 on the Ø2.8 teardrop, 13.1 mm2 | XY comp | 8.30 | 25.00 | 3.01 | 3 | OK |
| 85 | stall, one jaw blocked: the same push on the lower piece's plate between the screw (z 3) and the web (z 19.25) | simply supported, b_eff 9.2 x 5 (one-sided spread at the edge) | XY | 2.82 | 25.00 | 8.86 | 3 | OK |
| 86 | yaw stall 7.1 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 25 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws closed | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 1.69 | 12.50 | 7.38 | 3 | OK |
| 87 | yaw stall 7.1 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 25 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws 44 open | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 2.53 | 12.50 | 4.93 | 3 | OK |
| 88 | hand push 5 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 18 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws closed | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 1.19 | 12.50 | 10.48 | 3 | OK |
| 89 | hand push 5 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 18 N (x3.56: the rack lifted off the plate, the pinion holding its rear), jaws 44 open | strip 11.75 x 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 1.78 | 12.50 | 7.00 | 3 | OK |
| 90 | rack A lift: separating 7.9 N + grip twist 410 N.mm -> 13.8 N at the rack end | top wall between the lip and the front plate, span 12.5, b 25 x 3 | XY | 1.44 | 25.00 | 17.34 | 3 | OK |
| 91 | USB tug 10 N tips the camera mount back: 53 N on the top wall's rear edge | 50 x 1 mm contact | XY | 1.06 | 25.00 | 23.67 | 3 | OK |

**Lowest SF: 1.23 (required 3).** The top wall behind the lip, at the lip's back face, under the opening stall on jaw B
with the jaws open. Next:
- the top wall through the M3 holes: 1.53;
- the first tie's post: 1.56;
- the crash on jaw B: 1.94, 2.40, 2.45;
- the top wall in front of the lip: 2.92.

Every other row passes. The lowest passing rows are:
- the M2.5 pan head under rack B's grip push: 3.01 (row 84; a Ø6 washer gives 5.12);
- the local plate strips at the cover's edges: 3.03;
- rack A's grip on the upper piece near the top wall: 3.58.

Information rows (not in the verdict):

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 92 | info: opening stall on jaw B, upper piece WITHOUT the second tie (round 2's model) | beside slot A's V apex (z 43.4): b 21.0 x 5, lever 26.2, Kt 1.5 | XY | 12.12 | 25.00 | 2.06 | 3 | **FAIL** |
| 93 | info: opening stall on jaw B, upper piece WITHOUT the second tie (round 2's model) | top-wall junction (z 48.5): b 25.5 x 5, lever 31.3, Kt 1.5 | XY | 11.94 | 25.00 | 2.09 | 3 | **FAIL** |
| 94 | info, bound: opening stall on jaw B with the corners rigidly coupled: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 21.0, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners rigid] | XY | 7.74 | 25.00 | 3.23 | 3 | OK |
| 95 | info, bound: opening stall on jaw B with the corners rigidly coupled: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm held along z, corners rigid] | XY | 16.26 | 25.00 | 1.54 | 3 | **FAIL** |

## Required change: the smallest fix (computed in the script's what-if lines)

**Anchor the second tie's post on the frame's rail block with one vertical M3.** This gives the upper piece an anchor
at the height of the push.

What changes:
- **Cover, `model.py`:**
  - TIE2_POST_T 4 → **8** (the post x 14.35…22.35, like the first tie's);
  - the post's full-depth part (y 24…32) reaches down to **z 17.75** (= ZS − RAIL_IN, the frame's rail-block top), not
    19.25. Its 45° underside moves down 1.5 with it, leaving 2.5 mm over the claw servo's case at y 5.9;
  - a vertical **Ø3.6 CAD** hole (M3_CLEAR + HOLE_COMP) at **(x 18.35, y 28)** through the top wall, the lip and the
    post. Make it a teardrop pointing +y in print, like the top holes. It is clear of the camera mount (y ≤ 22) and of
    rack A (x ≥ 22.6).
- **Frame, `model.py`:** a **Ø2.7 CAD × 14** M3 pilot (M3_PILOT + HOLE_COMP) in the rail block's top at (18.35, 28).
  The block's root with that hole gives 5.93 (as built 6.31; frame report).
- **Hardware:** 1 × **M3 × 45** socket head (ISO 4762). It passes 33.75 mm of cover and has 11.25 engaged. Drive it
  snug only (≤ 150 N, about 0.09 N·m), after the cover's other screws.
- **Fit:** the post's foot and the top wall's underside are both 30.75 apart on the cover and on the frame, at zero
  nominal gap. Check at the dry fit that the post seats within 0.1 mm before the M3 is driven. A larger gap means the
  screw bends the lip to close it. Re-run `claw_sequence_check.py`: the post is now 8 thick and 1.5 lower.

| With the anchor (64 variants, both reversed pushes) | Result |
|---|---|
| Lowest SF of every global-model section | **4.64** (the first tie's post); most favourable variant 5.46 |
| Anchor force, opening stall on jaw B | x 25.2–25.8 N (of 27.0), z +6.5…+11.1 N lift |
| x held by preload friction | 0.3 × 150 = 45 N ≥ 25.8 N |
| M3 pull-out from the rail block | **4.42** on the preload (sustained, req 4); 4.11 with the lift (req 3) |
| 8 × 8 post round its Ø3.6 hole under the clamp | 9.0 |
| The frame's top-screw rows under this push (frame report rows 39–40) | removed: the push no longer goes through the top joint |

Stiffening the existing path instead doesn't pass with a single change. Each of these was computed:

| Change | Lowest SF |
|---|---|
| Top wall behind the lip 6 mm (the frame's bulkhead and ribs lowered 3 mm under it) | 1.92 (the first post) |
| As above, + the first post 8 × 14 (y −32…−18) | 2.92 (the top wall in front of the lip) |
| As above, at 7 mm | 2.92 |

The top wall over the racks can't grow downward (rack A rides on it), and upward it changes the camera's mount and view.

## Proof test (spec §8)

The loads still match: step 1's 32 N push towards the other jaw is 1.5 × the opening stall, exactly the failing case.
**Do not run it on the as-built cover.** At 1.5 × the top wall behind the lip would be at SF 0.82 (1.23 / 1.5), and it
would probably crack along the lip's back face.

With the fix it is valid as written, with these additions to the pass criteria:
- no crack or whitening along the lip's back face (the top wall's underside behind the lip), round the M3 holes, or at
  the first tie's post;
- the anchor M3 is still tight, and the second post is still seated on the rail block (0.1 feeler won't enter);
- the jaws still slide 0–44 mm; the cover screws are still tight (as now).

Step 2 (10.7 N sideways on jaw B) is unchanged: the strip under slot B gives 4.93 at 1.0 ×.

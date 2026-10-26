VERDICT: FAIL

# Strength check: 20261026-arm-claw-cover (round 5, independent review)

strength-analyst (independent; did not design the part) · 2026-10-26 · `python3 jobs/20261026-arm-claw-cover/strength_calc.py`
(plain python3, from the project root, about 60 s). The CAD engineer's round-5 strength.md was a self-check; this file
replaces it. The 64-variant cover frame model is round 4's (strength-analyst); this review re-ran it, re-derived the
V-seat rows, and added what the self-check did not have: **the seat as it actually prints.**

## Verdict

**FAIL. As printed, the ridge does not reliably take the push: its x play is not controlled, and above 0.04 mm the
cover falls back below SF 3.**

- **Lowest SF 1.84** (required 3), row 30: the top wall behind the lip, at the lip's back face (x 14.35), under the
  opening stall on jaw B (27.0 N), with the ridge's realistic as-printed play of **0.082 mm** (RSS-adverse).
- Below 3 at that play as well:
  - row 8, the same section under the desk crash, 2.16;
  - row 31, the top wall through the M3 holes, 2.92;
  - row 113, spec §8's proof push, 1.79 against 2. **The proof test would be unsafe to run on this build.**
- With zero play (the CAD engineer's assumption) every verdict row passes: lowest 3.01, row 102, the M2.5 pan head,
  unchanged since round 3. The design is not wrong in principle. It needs a seat that stays at zero play as printed:
  see "Required change".

## Ruling on the ridge play (item 1)

### What the arm's own slicing does

I sliced both committed part.stl files with the exact command in their slice_settings.json and read the G-code back
(a scratch slice, not a job file):
- PrusaSlicer 2.7.2, 0.20mm QUALITY @MK3, Prusament PETG, each job's slice_overrides.ini;
- first layer 0.2; every layer sliced at its mid-height; Arachne perimeters.

| Feature | CAD | Printed | Evidence |
|---|---|---|---|
| Frame bulkhead top (the cover's top wall sits on it) | 48.5 | **48.4** | last layer `;Z:48.4`. 48.5 is exactly the slice plane of layer 48.4–48.6, and the slicer dropped that layer |
| Frame rail block top (the foot's flats land on it) | 17.75 | **17.8** | layer 17.6–17.8 is sliced at 17.7, inside the block; nothing at 18.0 |
| Groove walls, layers ending 17.2 / 17.4 / 17.6 / 17.8 | 45° flank | vertical steps at half-widths 0.15 / 0.35 / 0.55 / 0.75 | external-perimeter centrelines at frame y 26, centred on x 15.25 ± 0.001 |
| Groove's first layer (17.0–17.2) | 0.3 slot | a slot between two external perimeters | it will close up, as the engineer said |
| Cover ridge flanks | CAD | CAD ± 0.01 | external perimeter 0.225 inside both 45° flanks; the second perimeter fills the root |

So each groove layer's top corner stands 0.1 inside the CAD flank, as the engineer said. But:
1. **The bulkhead does not print "0.1 high or low": it prints 0.1 low, deterministically.**
2. **The block prints 0.05 high.** The foot's flats, 0.1 over the block in CAD, are therefore only 0.05 over it in print.
3. **The corners are not sharp.** A perimeter bead has a rounded edge, radius up to h/2 = 0.1. A corner radius r moves
   the 45° ridge's contact (2 − √2)·r = 0.586·r further out: 0.03–0.06 mm.

### Stack-up

I lowered the cover (as CAD) onto the printed frame and found the first stop. Tolerances, each taken as a 3σ bound
(my assumption, because library/ has no measured data):
- ridge flank ±0.05 normal to its face (±0.071 horizontal);
- groove walls ±0.05;
- cover top wall to foot ±0.05 (31 mm in its print plane);
- corner radius 0.05 / 0.075 / 0.10.

| Case | Stops on | Ridge play (x, per flank) | BUILD_GUIDE feelers would read: top wall / under the flats | Lowest frame-model SF |
|---|---|---|---|---|
| Nominal | the ridge, with the flats 0.006 above the block | **0.000** | 0.056 / 0.006 | 3.61 |
| RSS-adverse | the foot's flats on the block | **0.082** | ≈0.05 / 0 | **1.84** |
| Worst case | the foot's flats on the block | **0.129** | 0.100 / 0.000 | 1.38 |

- **The seat has no margin.** At nominal, three stops coincide within 0.006 mm: the ridge on its flanks, the flats on
  the block, and the tip on the closed first layer.
- **The play is set by the two flanks' print errors.** Once the flats govern, the play is −0.05 + 0.586·r − (ridge
  error) − (groove error). VSEAT_CLR cancels out of that line.
- **The bulkhead is not what matters here.** Its slice-plane position decides nothing at the moment, because the foot
  lands first.

### Play → SF (preload gone; both reversed pushes, all 64 variants)

| Play (mm) | 0 | 0.025 | 0.04 | 0.05 | 0.075 | 0.1 |
|---|---|---|---|---|---|---|
| Lowest SF (this review) | 3.61 | 4.43 | 3.41 | 2.83 | 1.99 | 1.54 |
| CAD engineer's table | 3.03 | 3.72 | 3.41 | 2.83 | 1.99 | 1.54 |

From 0.04 mm on, the two tables agree. Below that they differ only because I take the ridge's root with Kt 1.7 instead
of 2.5. The limit is **about 0.04 mm**, the same as round 4's analyst found for the shank. Hand check: with the foot
free, the top wall behind the lip carries 0.68 MPa per newton (1.37 at the full 27 N). The foot slides 3.6–5.0 µm/N. So
0.04 mm of play passes about 11 N through the top wall before the flank bears: about 7.5 MPa plus about 1 MPa
afterwards, SF ≈ 3.0.

### Are the realistic plays inside 0.04 mm?

**No.** With MK3 tolerances of ±0.05 mm per printed surface, the RSS-adverse play is 0.082 mm and the worst case
0.129 mm.

### The BUILD_GUIDE checks cannot see it

- **The 0.15 feeler under the flats.** Whenever the ridge has play, the flats rest on the block (gap 0), so the feeler
  never goes in.
- **The 0.1 feeler at the top wall.** The cover is held 0.05–0.10 off the bulkhead, so the feeler reads the same with
  or without play.
- The engineer's "bounds the play to about 0.05" assumed that the block prints at 17.75 and that the bulkhead sets the
  cover's height. Neither is true in this slice.

### Preload does not save it either

As printed, the foot's flats, not the flanks, usually take the anchor's preload. The x hold until that preload creeps is
friction again: round 4's fdm-design-rules §4 problem.

## Required change (smallest robust fix, computed in the script's "THE FIX" lines)

**Make the ridge the only stop, always reached first, and seat it with the screws.** The flats are then clear by
design, and the top-wall feeler can prove that the ridge bears.

| # | Change | Where | Value |
|---|---|---|---|
| 1 | Ridge flanks onto the CAD groove flanks | claw_frame.py | `VSEAT_CLR` 0.1 → **0.0** (ridge virtual apex 17.05 → **16.95**) |
| 2 | Decouple the foot's flats from VSEAT_CLR and raise them | cover model.py | `TIE2_FOOT_Z` = ZS − RAIL_IN + **FOOT_CLR 0.30** = **18.05**. Carry the ridge's 45° flanks on up to the flats: base x 14.15–16.35, 2.2 wide, 0.2 behind the post's back face; 0.2 from the anchor hole's edge on the flats plane |
| 3 | Ridge tip above the closed first layer with margin | cover model.py | `RIDGE_TIP_Z` **17.35** (absolute, not apex + 0.2): tip 0.8 wide |
| 4 | Bulkhead top off the slice plane | frame model.py | bulkhead top **48.45** (frame only; the cover's Z_TOP0 stays 48.5). It prints 48.4, as today, with 0.05 to either slice plane |
| 5 | Assembly order and check | BUILD_GUIDE §4 step 9 | see the report's exact text: anchor first, before the M2.5 and M3 screws; a 0.03 feeler **must** enter at the top wall before any screw |

**The fix's stack-up:**

| Case | Stops on | Play | Ridge contact above the bulkhead (before the screws) |
|---|---|---|---|
| Nominal | ridge on both flanks | 0 | +0.156 |
| RSS-adverse | ridge on both flanks | 0 | +0.055 … +0.257 |
| Worst case | the top wall (top-wall feeler reads 0.000, so the step-9 check stops the build) | 0.029 → frame-model SF 4.40 | … +0.341 |

The flats stay 0.20–0.31 clear. The tip stays ≥ 0.05 above the closed first layer.

**Seating.** The ridge then holds the top wall up until the screws crush the groove's layer corners:
- crush rate about 1750 N per mm (3 corners a flank × 7.3 mm, flattened at about 40 MPa, an assumption);
- the anchor alone (150 N) takes out about 0.086 mm, which leaves the top wall 0.070 proud nominal and 0.256 worst;
- with the +y top screw's share it takes out about 0.152 mm, which leaves 0.005 / 0.190.

Consequences of the float:
- **Pull-out:** with the worst float the M3 × 45 has 10.49 engaged; pull-out on the preload is 4.12 (req 4).
- **Fit:** a top wall standing up to about 0.2 proud at the +y end is a fit matter, not a strength one. Rack A gets
  that much more lift room, which is harmless against its 0.7 backlash. Spec §3's "top wall underside z 48.5 ±0.15"
  needs the wider tolerance noted.
- **Crushing:** the crushing only takes play out. Its creep only relaxes a preload that nothing relies on.

**The fix's ridge rows** (Fx from the zero-play frame model):

| Row | Opening stall, 25.6 N | Proof push, 32.5 N (req 2) |
|---|---|---|
| Flank bearing, 0.64 × 7.3 band | **3.20** | 2.53 |
| Root shear | 5.22 | 4.12 |
| Root bending at the corners' resultant, Kt 1.7 | 8.12 | 6.41 |
| Root bending, bound: all of the flank force on the top corner | 4.14 | 3.27 |

**Alternatives that do not work:**
- **`VSEAT_CLR` 0 alone.** The flats move down with it, so the play is unchanged (the flats term does not contain
  VSEAT_CLR). It also lifts the top wall 0.15 off the bulkhead.
- **Moving only the bulkhead off its slice plane.** The bulkhead is not today's governing stop.
- **VSEAT_CLR 0.05 instead of 0 in item 1.** It halves the float, but leaves 0.02 RSS / about 0.08 worst-case play, and
  the step-9 check would reject about 1 build in 10.

## Info row 152 (item 2): the preload on the two flanks, SF 1.23 against 4

**It should not count toward the verdict.** It is right to keep it as information.
- **The stress is crushing, and the crushing is the seating.** The bearing stress is local crushing of the frame's
  0.2 mm layer corners. It stops by itself once the crushed area carries the clamp.
- **It only closes play.** It moves the ridge deeper and never opens a gap.
- **Its creep is harmless.** Creep only relaxes a preload that nothing relies on. The sustained SF 4 exists to limit
  creep deflection of members that carry load; here that creep is harmless.
- **Today's build does not even reach it.** The flats, not the flanks, usually take the preload.

With the fix, this crushing is how the seat is made, and its size is computed above.

## Other rows (item 6)

- **At zero play** (the fix, or a lucky print):
  - nothing is under 3 except what is noted;
  - lowest 3.01, row 102, M2.5 pan head under rack B's push (unchanged since round 3, at the limit);
  - then the plate strips at the ties' webs, 3.03 (rows 29 and 83).
- **Sustained screw-head and pull-out rows (req 4):**
  - the washer on the top wall: 4.80;
  - the post round its hole: 8.97;
  - M3 × 45 pull-out on the preload: 4.22 (4.12 with the fix's worst float).
- **The ridge's root.**
  - Verdict row: Kt 1.7, a bead-filled 135° corner, with the flank force at the printed corners' resultant (z 17.6).
  - Bound, info row 153: all of it on the top corner, 2.11. In today's design nothing seats the ridge on all three
    corners, so the bound is possible. In the fix the preload seats it, and the bound is 4.14.
- **Rows 148–149** (2.06 / 2.09) are round 2's cover without the second tie, kept for reference only.

## Design (round 5) as reviewed

| Part | Geometry |
|---|---|
| Frame | 90° V-groove, 0.8 deep: x 14.45–16.05 at z 17.75, bottom 16.95, y 23.5–32, open at +y |
| Cover: ridge | Its flanks 0.1 clear per flank in CAD (0.0707 normal): virtual apex 17.05, tip cut flat at 17.25 (0.4 wide), base x 14.45–16.05 at the flats |
| Cover: foot | Flats at 17.85 |
| Hardware | M3 × 45 with a Ø7 × 0.5 washer, 10.75 engaged |

**Exact solids, checked:**
- groove and ridge both centred on x 15.25, at y 26 and y 30;
- 0 mm³ overlap, 0.0707 mm gap on each flank.

**Item 5:** the frame's round-4 review text said x 14.35–15.95. Both models use 14.45–16.05, which is round 4's own
what-if (`LIP_X0 + 0.1`), so they line up. The 0.1 shift costs 0.1 mm of the ligament to the anchor pilot (0.95 CAD
instead of 1.05); the frame's report covers it.

## Load cases

As round 4: the stall is 216 N·mm through the 20-tooth pinion, 21.6 N on one rack or 10.8 N per jaw. Each rack cocks in
its 0.25 mm gaps and reacts its finger's moment with end forces R = F × (x_load − 28.6) / span.

| # | Case | Load | Where it lands | Type, SF req |
|---|---|---|---|---|
| 1 | Stall, one jaw blocked (spec) | 21.6 N 3 mm from the tip: R 19.8–27.0 N | Rack A forward on the upper piece and back on the lip; rack B on the lower piece | Short-term, 3 |
| 2 | Stall, both jaws | half of 1 | As 1 | Cyclic, 4 |
| 3 | Crash | 13 N at the tip, finger pushed shut: R 12.6–17.2 N, reversed | Rack B on the upper piece's bottom strip (reaction on the frame through the post's foot); rack A on the lower piece's top strip | Short-term, 3 |
| 4 | Opening against an obstacle (Architect: a design case) | 21.6 N reversed: R up to 27.0 N | As 3 | Short-term, 3 |
| 5 | Handling | 5 N pushing a finger shut: R 6.6 N | As 3 | Short-term, 3 |
| 6 | Sideways push on jaw B | Yaw stall 7.1 N; hand 5 N | Strip under slot B | Short-term, 3 |
| 7 | Rack A lift | 13.8 N at the rack's end | Top wall between the lip and the plate | Short-term, 3 |
| 8 | Camera tug | 10 N | Top wall's rear edge | Short-term, 3 |
| 9 | Anchor | M3 × 45 snug, 150 N, on a Ø7 washer | Washer on the top wall, the post round its hole, pull-out | Sustained, 4 |
| 10 | Spec §8 proof | 32 N at 3 mm from the tip, jaws 30: R 34.2 N; 10.7 N sideways | As 3/4 and 6 | Proof, 2 |

## Method, sections and assumptions

- **Print direction.** The cover prints on its −y end (print Z = claw y). Side-profile bending runs along the layers
  (25 MPa). The strip under slot B bends across them (12.5).
- **Global model:** round 4's two-zone x–z frame, 64 joint variants: top wall clamped or on 1.1 × 10⁵ N·mm/rad; M2.5 3
  or 30 kN/mm, held or free in z; plate leg 21 / 25.5; second lip 25.5 / 37.25; corner coupling 2.9 × 10⁴ / 10⁵
  N·mm/rad.
- **The post's foot** is a node at z 17.6, the flank resultant: x held by the ridge (3 kN/mm), z by the flanks and the
  screw.
- **The play.** It is modelled as round 4's slip: the foot slides freely, z held, until it has moved the play, and is
  held after that. Linear in each phase, so the two superpose.
- **The ridge.** It is a vertical prism in the cover's print, so its root (the flats' plane) is in-plane (25 MPa, 12.5
  shear).
  - Flank bearing: all of Fx on one 45° flank, frictionless: normal Fx√2 on the 0.71 × 7.4 band.
  - Root: Fx/A + Kt·6M/(b²L), with M = Fx·(2z_c − flats − apex), the flank force's moment about the root's centroid.
- **Screw tension.** In a "slip" mode the play only matters once the preload has crept away; with the preload, friction
  at the seat holds the foot. So the screw then carries the lifts alone (lift up to ~105 N with play: pull-out ≥ 5.5).
  In "locked" (zero play) the preload is added on top.
- **The seat stack-up** uses the slice facts and tolerances above (script section "round 5 review").
- **PETG:** E 1.8 GPa (placeholder; only stiffness ratios use it).
- **Temperature:** 40 °C against PETG at ~70 °C, OK.

## Allowables and sources

`library/materials.csv` has no measured PETG row, so these are the strength-checks **placeholders**. NEEDS_TEST is the
best verdict possible even after the fix.

| Quantity | Value | Source |
|---|---|---|
| Along the layers | 25 MPa | Skill placeholder |
| Across the layers | 12.5 MPa | 0.5 × in-plane |
| Interlayer shear | 6.25 MPa | 0.5 × 12.5 |
| Bearing | 25 MPa | In-plane value |
| Kt | 2.5 sharp; 1.7 for r/h 0.15–0.25 (the ridge's root); 1.5 for r ≥ 0.25 h; 2 at a hole | Skill |
| Corner crush (seating estimate only) | ~40 MPa | Assumption, PETG compressive flow |

Required SF: 3 short-term, 4 cyclic or sustained, 2 at a proof load (1.5 × service).

## Results (from `strength_calc.py`, verbatim; frame-model rows at the as-printed RSS-adverse play, 0.082 mm)

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | stall, one jaw blocked, jaws 44 open: rack A's -y end at the lip's end, R 27.0 N (the first tie's prop ignored) | lip root at the top wall, rack side (Kt 2.5): b_eff 7.9, t 8.0, lever 5.9 | XY | 4.72 | 25.00 | 5.30 | 3 | OK |
| 2 | stall, one jaw blocked, jaws closed: rack A's -y end at y -25.1, R 19.8 N | lip root at the top wall, rack side (Kt 2.5): b_eff 13.8, t 8.0, lever 5.9 | XY | 1.98 | 25.00 | 12.63 | 3 | OK |
| 3 | stall, both jaws (cyclic), jaws 44 open: R 13.5 N at the lip's end | lip root at the top wall, rack side (Kt 2.5): b_eff 7.9, t 8.0, lever 5.9 | XY | 2.36 | 25.00 | 10.60 | 4 | OK |
| 4 | crash 13 N pushes jaw A shut, jaws closed: rack A's +y end on the lip at y 31.4, R 12.6 N (the second tie's prop ignored) | lip root at the top wall, rack side (Kt 2.5): b_eff 8.5, t 8.0, lever 5.9 | XY | 2.05 | 25.00 | 12.20 | 3 | OK |
| 5 | added: opening against an obstacle, jaw A, jaws nearly closed: rack A's +y end at y 31.4, R 19.8 N (the second tie's prop ignored) | lip root at the top wall, rack side (Kt 2.5): b_eff 8.5, t 8.0, lever 5.9 | XY | 3.22 | 25.00 | 7.77 | 3 | OK |
| 6 | stall, one jaw blocked: rack A's +y end on the upper piece near slot A's end, R 27.0 N | front plate at the top wall (Kt 1.5): b_eff 7.1, t 5.0, lever 5.1 | XY | 6.99 | 25.00 | 3.58 | 3 | OK |
| 7 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 1.27 MPa) | XY | 5.25 | 25.00 | 4.76 | 3 | OK |
| 8 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 11.58 | 25.00 | 2.16 | 3 | **FAIL** |
| 9 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 6.52 | 25.00 | 3.84 | 3 | OK |
| 10 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 2.38 | 25.00 | 10.49 | 3 | OK |
| 11 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.18 | 25.00 | 141.33 | 3 | OK |
| 12 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.94 | 25.00 | 26.52 | 3 | OK |
| 13 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 4.80 | 25.00 | 5.21 | 3 | OK |
| 14 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: second tie's post under the lip (z 35.25..36.75) | 8 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 1.62 | 25.00 | 15.42 | 3 | OK |
| 15 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 4.86 | 25.00 | 5.15 | 3 | OK |
| 16 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 4.20 | 25.00 | 5.96 | 3 | OK |
| 17 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: second post's foot below the web (z 17.85..19.25), the anchor's reaction | 8 x 9.15 net of the Ø3.6 hole (A 62.4, I 383.5), Fx 0.0 N at z 17.60, lift +76.9 N + wedge 0.0 N, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 1.23 | 25.00 | 20.29 | 3 | OK |
| 18 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: second post's foot: shear across it (z 19.25) | A 62.4, Fx 0.7 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY shear | 0.02 | 12.50 | 744.26 | 3 | OK |
| 19 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: M3 x 45 anchor: pull-out from the frame's rail block (10.75 engaged), preload (if any) + wedge lift + lift | screw 77 N, thread cylinder Ø3 x 10.75 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | Z shear (frame) | 0.76 | 6.25 | 8.23 | 3 | OK |
| 20 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: V-ridge: flank bearing on the groove's 45° flank (contact band z 17.25..17.75) | normal 1.0 N on 0.71 x 7.4 (the 0.6 lead-in ignored) [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | bearing | 0.19 | 25.00 | 132.39 | 3 | OK |
| 21 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: V-ridge root at the foot's flats (z 17.85): shear | 1.6 x 7.4, Fx 0.7 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY shear | 0.09 | 12.50 | 141.22 | 3 | OK |
| 22 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: V-ridge root at the foot's flats: the flank force's moment (0.30 Fx, resultant at the printed layer corners, z 17.6) + the wedge's compression, Kt 1.7 | 1.6 x 7.4, M 0.2 N.mm, Kt 1.7 (bead-filled 135° root corners); compression and bending added in magnitude [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.17 | 25.00 | 145.46 | 3 | OK |
| 23 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.79 | 25.00 | 31.80 | 3 | OK |
| 24 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 1.89 | 25.00 | 13.19 | 3 | OK |
| 25 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.47 | 25.00 | 53.50 | 3 | OK |
| 26 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.56 | 25.00 | 44.99 | 3 | OK |
| 27 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 1 N [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | Z shear | 0.02 | 6.25 | 378.97 | 3 | OK |
| 28 | crash 13 N pushes jaw B shut, jaws 44 open: rack B pushes the upper piece's bottom strip at the cover's edge, R 17.2 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 1 N [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY comp | 0.11 | 25.00 | 229.10 | 3 | OK |
| 29 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 1.99 MPa) | XY | 8.25 | 25.00 | 3.03 | 3 | OK |
| 30 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 13.62 | 25.00 | 1.84 | 3 | **FAIL** |
| 31 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 8.56 | 25.00 | 2.92 | 3 | **FAIL** |
| 32 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 2.74 | 25.00 | 9.11 | 3 | OK |
| 33 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.19 | 25.00 | 128.82 | 3 | OK |
| 34 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 1.07 | 25.00 | 23.37 | 3 | OK |
| 35 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 5.46 | 25.00 | 4.58 | 3 | OK |
| 36 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: second tie's post under the lip (z 35.25..36.75) | 8 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 2.15 | 25.00 | 11.64 | 3 | OK |
| 37 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 6.44 | 25.00 | 3.88 | 3 | OK |
| 38 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 4.75 | 25.00 | 5.26 | 3 | OK |
| 39 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: second post's foot below the web (z 17.85..19.25), the anchor's reaction | 8 x 9.15 net of the Ø3.6 hole (A 62.4, I 383.5), Fx 4.6 N at z 17.60, lift +100.6 N + wedge 4.6 N, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 1.88 | 25.00 | 13.29 | 3 | OK |
| 40 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: second post's foot: shear across it (z 19.25) | A 62.4, Fx 10.0 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY shear | 0.24 | 12.50 | 51.92 | 3 | OK |
| 41 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: M3 x 45 anchor: pull-out from the frame's rail block (10.75 engaged), preload (if any) + wedge lift + lift | screw 106 N, thread cylinder Ø3 x 10.75 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | Z shear (frame) | 1.05 | 6.25 | 5.97 | 3 | OK |
| 42 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: V-ridge: flank bearing on the groove's 45° flank (contact band z 17.25..17.75) | normal 14.2 N on 0.71 x 7.4 (the 0.6 lead-in ignored) [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | bearing | 2.71 | 25.00 | 9.24 | 3 | OK |
| 43 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: V-ridge root at the foot's flats (z 17.85): shear | 1.6 x 7.4, Fx 10.0 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY shear | 1.27 | 12.50 | 9.85 | 3 | OK |
| 44 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: V-ridge root at the foot's flats: the flank force's moment (0.30 Fx, resultant at the printed layer corners, z 17.6) + the wedge's compression, Kt 1.7 | 1.6 x 7.4, M 3.0 N.mm, Kt 1.7 (bead-filled 135° root corners); compression and bending added in magnitude [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 2.46 | 25.00 | 10.15 | 3 | OK |
| 45 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.88 | 25.00 | 28.44 | 3 | OK |
| 46 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 2.16 | 25.00 | 11.56 | 3 | OK |
| 47 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.53 | 25.00 | 47.42 | 3 | OK |
| 48 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.62 | 25.00 | 40.49 | 3 | OK |
| 49 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 2 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | Z shear | 0.02 | 6.25 | 341.05 | 3 | OK |
| 50 | added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 2 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY comp | 0.12 | 25.00 | 206.17 | 3 | OK |
| 51 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 0.49 MPa) | XY | 2.02 | 25.00 | 12.38 | 3 | OK |
| 52 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 4.47 | 25.00 | 5.60 | 3 | OK |
| 53 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 2.51 | 25.00 | 9.97 | 3 | OK |
| 54 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.92 | 25.00 | 27.29 | 3 | OK |
| 55 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.07 | 25.00 | 367.23 | 3 | OK |
| 56 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.36 | 25.00 | 68.94 | 3 | OK |
| 57 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 1.85 | 25.00 | 13.53 | 3 | OK |
| 58 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: second tie's post under the lip (z 35.25..36.75) | 8 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.62 | 25.00 | 40.10 | 3 | OK |
| 59 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 1.87 | 25.00 | 13.38 | 3 | OK |
| 60 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 1.61 | 25.00 | 15.49 | 3 | OK |
| 61 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: second post's foot below the web (z 17.85..19.25), the anchor's reaction | 8 x 9.15 net of the Ø3.6 hole (A 62.4, I 383.5), Fx 0.0 N at z 17.60, lift +29.6 N + wedge 0.0 N, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.47 | 25.00 | 52.74 | 3 | OK |
| 62 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: second post's foot: shear across it (z 19.25) | A 62.4, Fx 0.0 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY shear | 0.00 | 12.50 | 15782345390.53 | 3 | OK |
| 63 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: M3 x 45 anchor: pull-out from the frame's rail block (10.75 engaged), preload (if any) + wedge lift + lift | screw 30 N, thread cylinder Ø3 x 10.75 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | Z shear (frame) | 0.29 | 6.25 | 21.41 | 3 | OK |
| 64 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: V-ridge: flank bearing on the groove's 45° flank (contact band z 17.25..17.75) | normal 0.0 N on 0.71 x 7.4 (the 0.6 lead-in ignored) [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | bearing | 0.00 | 25.00 | 2807436439.66 | 3 | OK |
| 65 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: V-ridge root at the foot's flats (z 17.85): shear | 1.6 x 7.4, Fx 0.0 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY shear | 0.00 | 12.50 | 2994598868.97 | 3 | OK |
| 66 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: V-ridge root at the foot's flats: the flank force's moment (0.30 Fx, resultant at the printed layer corners, z 17.6) + the wedge's compression, Kt 1.7 | 1.6 x 7.4, M 0.0 N.mm, Kt 1.7 (bead-filled 135° root corners); compression and bending added in magnitude [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.00 | 25.00 | 3084565358.60 | 3 | OK |
| 67 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.30 | 25.00 | 82.69 | 3 | OK |
| 68 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.73 | 25.00 | 34.30 | 3 | OK |
| 69 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.18 | 25.00 | 139.10 | 3 | OK |
| 70 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.21 | 25.00 | 116.97 | 3 | OK |
| 71 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 1 N [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | Z shear | 0.01 | 6.25 | 985.33 | 3 | OK |
| 72 | handling: 5 N pushes jaw B shut, jaws 44 open: R 6.6 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 1 N [plate b 25.5, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY comp | 0.04 | 25.00 | 595.65 | 3 | OK |
| 73 | added: opening against an obstacle, jaw B, jaws closed: rack B's end 6.9 from the edge, R 19.8 N: plate strip under the second tie's web | cantilever 2.07 from the web, b_eff 6.15 x 5, Kt 2.5 (shear 0.96 MPa) | XY | 4.00 | 25.00 | 6.25 | 3 | OK |
| 74 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 1.27 MPa) | XY | 5.25 | 25.00 | 4.76 | 3 | OK |
| 75 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 2.23 | 25.00 | 11.20 | 3 | OK |
| 76 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 1.35 | 25.00 | 18.50 | 3 | OK |
| 77 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 1.18 | 25.00 | 21.17 | 3 | OK |
| 78 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 3.51 | 25.00 | 7.12 | 3 | OK |
| 79 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 1.92 | 25.00 | 13.03 | 3 | OK |
| 80 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.88 | 25.00 | 28.48 | 3 | OK |
| 81 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 2 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | Z shear | 0.03 | 6.25 | 239.92 | 3 | OK |
| 82 | crash 13 N pushes jaw A shut, jaws 44 open: rack A pushes the lower piece's top strip at the cover's edge, R 17.2 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 2 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY comp | 0.17 | 25.00 | 145.04 | 3 | OK |
| 83 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 1.99 MPa) | XY | 8.25 | 25.00 | 3.03 | 3 | OK |
| 84 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 3.50 | 25.00 | 7.13 | 3 | OK |
| 85 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 2.12 | 25.00 | 11.78 | 3 | OK |
| 86 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 1.85 | 25.00 | 13.48 | 3 | OK |
| 87 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 5.51 | 25.00 | 4.53 | 3 | OK |
| 88 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 3.01 | 25.00 | 8.30 | 3 | OK |
| 89 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 1.38 | 25.00 | 18.14 | 3 | OK |
| 90 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 4 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | Z shear | 0.04 | 6.25 | 152.76 | 3 | OK |
| 91 | added: opening against an obstacle, jaw A, jaws 44 open: R 27.0 N on the lower piece's top strip: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 4 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY comp | 0.27 | 25.00 | 92.35 | 3 | OK |
| 92 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: plate strip above the first tie's web | cantilever 2.08 from the web, b_eff 4.08 x 5, Kt 2.5 (shear 0.49 MPa) | XY | 2.02 | 25.00 | 12.38 | 3 | OK |
| 93 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.86 | 25.00 | 29.13 | 3 | OK |
| 94 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.52 | 25.00 | 48.11 | 3 | OK |
| 95 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.45 | 25.00 | 55.04 | 3 | OK |
| 96 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 1.35 | 25.00 | 18.51 | 3 | OK |
| 97 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.74 | 25.00 | 33.87 | 3 | OK |
| 98 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.34 | 25.00 | 74.05 | 3 | OK |
| 99 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 1 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | Z shear | 0.01 | 6.25 | 623.78 | 3 | OK |
| 100 | handling: 5 N pushes jaw A shut, jaws 44 open: R 6.6 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 1 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY comp | 0.07 | 25.00 | 377.09 | 3 | OK |
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
| 113 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 13.98 | 25.00 | 1.79 | 2 | **FAIL** |
| 114 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 8.79 | 25.00 | 2.85 | 2 | OK |
| 115 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: upper piece's plate at the web top (z 35.25, sharp inner corner) | b 24.1 x 5, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 2.82 | 25.00 | 8.86 | 2 | OK |
| 116 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: upper piece's plate beside slot A's V apex (z 43.4, r 1.5) | b 21.0 x 5, Kt 1.5 [plate b 21.0, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.20 | 25.00 | 125.41 | 2 | OK |
| 117 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: upper piece's plate at the top wall (z 48.5, r 2 fillet) | b 25.5 x 5, Kt 1.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 1.10 | 25.00 | 22.73 | 2 | OK |
| 118 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: top wall in front of the lip (r 2 at the plate, sharp at the lip) | b 25.5 x 3 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 5.61 | 25.00 | 4.46 | 2 | OK |
| 119 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: second tie's post under the lip (z 35.25..36.75) | 8 x 24.3, Kt 2.5 [plate b 21.0, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 2.21 | 25.00 | 11.30 | 2 | OK |
| 120 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: second tie's web at the post (tension + bending) | 8 x 16 (45-degree parts ignored), Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 6.61 | 25.00 | 3.78 | 2 | OK |
| 121 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: lip root at the top wall above the second tie | b 25.5 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 4.88 | 25.00 | 5.13 | 2 | OK |
| 122 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: second post's foot below the web (z 17.85..19.25), the anchor's reaction | 8 x 9.15 net of the Ø3.6 hole (A 62.4, I 383.5), Fx 11.3 N at z 17.60, lift +103.2 N + wedge 11.3 N, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 2.32 | 25.00 | 10.77 | 2 | OK |
| 123 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: second post's foot: shear across it (z 19.25) | A 62.4, Fx 16.9 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY shear | 0.41 | 12.50 | 30.83 | 2 | OK |
| 124 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: M3 x 45 anchor: pull-out from the frame's rail block (10.75 engaged), preload (if any) + wedge lift + lift | screw 115 N, thread cylinder Ø3 x 10.75 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | Z shear (frame) | 1.14 | 6.25 | 5.49 | 2 | OK |
| 125 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: V-ridge: flank bearing on the groove's 45° flank (contact band z 17.25..17.75) | normal 23.9 N on 0.71 x 7.4 (the 0.6 lead-in ignored) [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | bearing | 4.56 | 25.00 | 5.48 | 2 | OK |
| 126 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: V-ridge root at the foot's flats (z 17.85): shear | 1.6 x 7.4, Fx 16.9 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY shear | 2.14 | 12.50 | 5.85 | 2 | OK |
| 127 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: V-ridge root at the foot's flats: the flank force's moment (0.30 Fx, resultant at the printed layer corners, z 17.6) + the wedge's compression, Kt 1.7 | 1.6 x 7.4, M 5.1 N.mm, Kt 1.7 (bead-filled 135° root corners); compression and bending added in magnitude [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 4.15 | 25.00 | 6.02 | 2 | OK |
| 128 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.90 | 25.00 | 27.71 | 2 | OK |
| 129 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 2.22 | 25.00 | 11.27 | 2 | OK |
| 130 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.54 | 25.00 | 46.20 | 2 | OK |
| 131 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 0.63 | 25.00 | 39.45 | 2 | OK |
| 132 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 2 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | Z shear | 0.02 | 6.25 | 332.32 | 2 | OK |
| 133 | spec §8 proof 1: 32 N pushes jaw B towards the other, jaws 30 open, R 34.2 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 2 N [plate b 25.5, lip b 25.5, top clamped, M2.5 30 kN/mm free along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY comp | 0.12 | 25.00 | 200.90 | 2 | OK |
| 134 | spec §8 proof 1: jaw B pushed towards the other, R 34.2 N: plate strip at the tie's web | cantilever 2.07 from the web, b_eff 4.07 x 5, Kt 2.5 (shear 2.52 MPa) | XY | 10.45 | 25.00 | 2.39 | 2 | OK |
| 135 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: top wall behind the lip, at the lip's back face (x 14.35) | 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 4.44 | 25.00 | 5.63 | 2 | OK |
| 136 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: top wall over the bulkhead, through the M3 holes (x 6.75) | 28.4 net per zone x 3.0, Kt 2 (hole) [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 2.69 | 25.00 | 9.30 | 2 | OK |
| 137 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 1.0e+05 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 2.35 | 25.00 | 10.64 | 2 | OK |
| 138 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 6.99 | 25.00 | 3.58 | 2 | OK |
| 139 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: first tie's web at the post (tension + bending) | 8 x 16, Kt 2.5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 3.82 | 25.00 | 6.55 | 2 | OK |
| 140 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: lower piece's plate between the first tie's web and the M2.5 (web corner Kt 2.5; hole Kt 2) | b 25 x 5 [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY | 1.75 | 25.00 | 14.31 | 2 | OK |
| 141 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: M2.5 x 16 at z 3: pull-out from the frame (11 engaged) | screw force 4 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | Z shear | 0.05 | 6.25 | 120.54 | 2 | OK |
| 142 | spec §8 proof 1: 32 N pushes jaw A towards the other, jaws 30 open, R 34.2 N: same M2.5: pan head on the cover's front plate | Ø5 head on the Ø2.8 teardrop, 13.1 mm2; screw force 4 N [plate b 21.0, lip b 25.5, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm free along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)] | XY comp | 0.34 | 25.00 | 72.87 | 2 | OK |
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
| 150 | info, bound: opening stall on jaw B with the corners rigidly coupled: lip root at the top wall above the first tie | b 19.75 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 30 kN/mm held along z, corners rigid; ridge play as printed 0.082 mm (RSS)] | XY | 1.65 | 25.00 | 15.17 | 3 | OK |
| 151 | info, bound: opening stall on jaw B with the corners rigidly coupled: first tie's post under the lip (flush with the lip; sharp web-top corner below) | 8 x 8, Kt 2.5 [plate b 25.5, lip b 37.25, top on 1.1e5 N.mm/rad, M2.5 3 kN/mm held along z, corners rigid; ridge play as printed 0.082 mm (RSS)] | XY | 3.48 | 25.00 | 7.18 | 3 | OK |
| 152 | info: anchor preload seats the ridge, bound: all 150 N on the two 45° flanks (sustained; seating, self-limiting) | normal 106 N per flank on 0.71 x 7.4 | bearing | 20.27 | 25.00 | 1.23 | 4 | **FAIL** |
| 153 | info, bound: opening stall with zero play, Fx 25.6 N all on the groove's top layer corner (z 17.8): V-ridge root at the flats, Kt 1.7 | 1.6 x 7.4, M 18.0 N.mm (arm 0.70) | XY | 11.83 | 25.00 | 2.11 | 3 | **FAIL** |

Script: lowest SF 1.84 (required 3): added: opening against an obstacle, jaw B, jaws 44 open: R 27.0 N on the upper piece's bottom strip: top wall behind the lip, at the lip's back face (x 14.35) / 32 per zone x 3.0, Kt 2.5 [plate b 25.5, lip b 37.25, top clamped, M2.5 3 kN/mm held along z, corners 2.9e+04 N.mm/rad; ridge play as printed 0.082 mm (RSS)]

## Proof test (spec §8)

- **The loads still match the design cases.**
  - Step 1's 32 N push towards the other jaw is 1.5 × the opening stall (R 34.2 N at 30 mm open).
  - Its 32 N pull is 1.5 × the one-jaw stall: lip root 4.18, front plate at the top wall 2.82.
  - Step 2's 10.7 N sideways: strip under slot B 4.90 / 3.27.
- **On the round-5 build as printed, step 1's push on jaw B is not safe.** The top wall behind the lip is at 1.79 against
  2 (row 113) at the realistic play.
- **After the fix**, every proof row is ≥ 2.39 (req 2). The fix's ridge rows are flank bearing 2.53, root 3.27 bound and
  pull-out 3.26 (the preload added).
- **Wording.** The pass line's ridge check ("a 0.15 mm feeler does not enter under the post's foot") cannot detect
  anything. With the fix the flats stand 0.2–0.3 clear by design, so it would never pass meaningfully. The report to
  the Architect gives the exact replacement text.

VERDICT: FAIL

# Strength check: 20261026-arm-claw-cover (round 2)

strength-analyst (independent review of the round-2 geometry) · 2026-10-26 ·
`python3 jobs/20261026-arm-claw-cover/strength_calc.py` (plain python3: reads `claw_frame.py`, this job's `model.py`,
`tools/cadlib.py` and `tools/hobby_parts.py` with `ast`)

Round 2's 5 mm front plate and its fillets and corners fix round 1's front-plate failure. But two round-2 changes made
new weak points.

**The 4 mm lip.** It is now a wall instead of a block back to the bulkhead. Rack A pushes it backwards at the rack's end,
which with the jaws open is the lip's free corner, and its rack-side root is sharp. **SF 1.30** with one jaw blocked;
2.60 for every full-close grip (cyclic).

**The split front plate.** The pass-through and the two slots cut it into an *upper piece*, which hangs from the top wall
only, and a *lower piece*, joined to the lip by the tie. A grip loads each piece near its support. Anything that pushes a
finger **towards closing** reverses the rack's couple. That includes the required desk crash (the lower finger is always
pushed shut), a hand, or the claw opening against an obstacle. The reversed couple pushes each piece at its far edge:

- rack A pushes the lower piece's 2 mm top strip, and the tie carries that load into the lip above the post;
- rack B pushes the upper piece's bottom edge, 31 mm below the top wall.

The tie's post and web themselves are strong (SF ≥ 4.4). The lip above the post is not: **2.56** under the crash and
1.63 under the opening stall. The upper piece passes the crash (3.09) but not the opening stall (1.96).

**The strip under slot B** gives **SF 2.58** when the yaw stall pushes jaw B towards the wrist with the jaws open. That is
the most the strip can be asked to carry: the rack lifted off the wrist plate, with the pinion holding its rear.

## Round-1 fixes: made?

| Round-1 required change | Round 2 | Made? |
|---|---|---|
| FRONT_T 3 → 5 | FRONT_T 5 | Yes: the plate at the top-wall corner now gives 3.51 (row 12) |
| r ≥ 2 at both slots' closed ends | Slot B: r 2 corners. Slot A: a 45° V roof (it is a ceiling in print), apex r 1.5, r 2 where it meets the top wall | Yes in substance (r 1.5 / 5 ≥ 0.25: Kt 1.5) |
| After the jaw redesign, keep a strip under slot B and thicken it | FRONT_Z0 −4: a 9.75 mm strip | Made, but see rows 28–31 |
| Keep a strip of plate *above* slot A on the −y half, so rack A bears forward there when a jaw is pushed open | Not made: slot A's outer edge is the top wall's underside. Instead rack A bears on the 2 mm strip *below* slot A, which the new tie backs | Replaced by the tie (rows 13–27) |

## Load cases

Stall: 216 N·mm through the 20-tooth pinion, so 21.6 N on one rack (one jaw blocked) or 10.8 N per jaw (both jaws, free
object). Each rack cocks in its 0.25 mm gaps and reacts its finger's moment with end forces:
R = F × (x_grip − 27.6) / span. The span is 56.5 with the jaws closed, or 41.4 with them 44 mm open, when the rack's end
is past the cover's edge.

| # | Case | Load | Where it lands on the cover | Type, SF req |
|---|---|---|---|---|
| 1 | Stall, one jaw blocked (spec) | 21.6 N, 3 mm from the tip: R 20.1–27.5 N | Rack A: forward on the upper piece near the top wall, backward on the lip at its −y end | Short-term, 3 |
| 2 | Stall, both jaws (every full-close grip) | Half of case 1 | As 1 | Cyclic, 4 |
| 3 | **Crash** (required): fingertip on the desk, wrist back-driven | 13 N at the tip, in the arm plane: R 12.8–17.5 N, **reversed** | Rack A: forward on the lower piece's top strip, so through the tie; back on the lip's +y end. Rack B: forward on the upper piece's bottom edge | Short-term, 3 |
| 4 | Added: the claw opens against an obstacle | 21.6 N on a finger's outer face, reversed, R up to 27.5 N | As 3 | Short-term, 3 |
| 5 | Sideways push on jaw B's tip towards the wrist | Yaw stall 7.1 N (its out-of-plane part, 1079 / (2 × 76)); hand 5 N | Neck B on the strip under slot B | Short-term, 3 |
| 6 | Rack A lift (spec) | Separating 7.9 N + the grip's twist 410 N·mm, giving 13.8 N at the rack's end | Top wall between the lip and the front plate | Short-term, 3 |
| 7 | Camera on the top wall (spec) | 10 N USB tug tips the mount back | Top wall's rear edge | Short-term, 3 |
| 8 | Handling | 5 N at a fingertip pushing a finger shut: R 6.7 N | As 3 | Short-term, 3 |

Camera inertia under the 250 °/s² ramp (≤ 0.84 g dynamic) and the weight ×3 reach the cover only through its top
screws. Those are checked in the frame and camera-mount reports. The cover has no case of its own there.

## Build direction and sections

The cover prints standing on its −y end (print Z = claw y). Bending in the side profile is along the layers: the
plate, the top wall, the lip, the post and the web (stress along claw x or z). Beams along claw y (the strip under slot B)
bend across the layers.

- **Lip:** x 18.35–22.35 (4 thick), z 36.75–48.5, a cantilever from the top wall. Its rack-side root is sharp, Kt 2.5.
  The push acts at mid-height (lever 5.9). Width: b = 2 + 5.9 + min(5.9, distance to the lip's end).
- **Upper piece:** its narrowest section is beside slot A's V apex (z 43.4, b 20.4 to the +y edge, apex r 1.5,
  Kt 1.5), and its top-wall junction is b 25.5 (r 2, Kt 1.5). Rack B's teeth press its bottom strip at z 17.2.
- **Tie:** web x 22.35–32.85, z 19.25–35.25; post x 18.35–22.35, z 19.25–36.75; both at y −32…−24. All corners are
  sharp (Kt 2.5). Rack A's teeth press the plate strip 2 mm above the web's top.
- **Strip under slot B:** z −4…5.75 (9.75 deep, 5 thick). It is fixed at slot B's closed end (r 2 corners, r/h 0.21,
  Kt 1.7) and pinned by the M2.5 at y 24, with a free end at 32. Through the screw hole: Kt 2.

## Assumptions

- **Tie path:** all of rack A's reversed push goes through the tie into the lip (conservative for the tie). The lower
  piece pivots on the wrist plate's bottom edge with its M2.5 3 mm above the pivot. Its stiffness gives the screw 20–35 %
  of the push; 40 % is used for the screw row.
- **Lip at its −y end:** the post below it props it in a grip. The prop is ignored, which is conservative. Taking it into
  account cuts the root moment by about 30 %: row 1 would be 1.9, still failing.
- **Strip under slot B:** a −z push on jaw B's tip pitches the jaw nose-down. The wrist plate and the strip can only push
  the jaw up; only the pinion, on the rack's teeth, can hold its rear down.
  - As drawn, the jaw first pivots on the rack's front-bottom edge. Its rear rises 0.40 mm onto the pinion at 0.040 rad,
    before the neck closes its 0.25 mm gap to the strip at 0.048 rad. With a rigid pinion the strip carries nothing, and
    the pinion takes 5.2 × the push (pinion report).
  - If the servo's output gives radially, the neck reaches the strip and the two share the load. The strip carries the
    most when the rack has lifted off the plate and the jaw pivots on the strip's front edge: 4.04 × the push, with the
    pinion still holding the rear (3.04 ×). Rows 28–31 use that bound.
- Friction is ignored. Service temperature is 40 °C against PETG softening at about 70 °C: OK.

## Allowables and sources

`library/materials.csv` has no measured row, so these are the strength-checks **placeholder** PETG values and
NEEDS_TEST is the best possible verdict.

| Quantity | Value | Source |
|---|---|---|
| Along the layers | 25 MPa | Skill placeholder |
| Across the layers | 12.5 MPa | 0.5 × in-plane |
| Interlayer shear | 6.25 MPa | 0.5 × 12.5 |
| Bearing | 25 MPa | In-plane value |
| Kt | 2.5 sharp; 1.5 for r ≥ 0.25 h; 1.7 for r/h 0.15–0.25; 2 at a hole | Skill (the 1.7 is a Peterson-based interpolation) |

## Results (copied from `python3 strength_calc.py`)

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | Stall, one jaw blocked, jaws 44 open: rack A's −y end at the lip's end, R 27.5 N (the tie's prop ignored) | Lip root at the top wall, rack side (Kt 2.5): b_eff 7.9, t 4.0, lever 5.9 | XY | 19.24 | 25.00 | **1.30** | 3 | **FAIL** |
| 2 | Stall, one jaw blocked, jaws closed: rack A's −y end at y −25.1, R 20.1 N | Lip root at the top wall, rack side (Kt 2.5): b_eff 13.8, t 4.0, lever 5.9 | XY | 8.07 | 25.00 | 3.10 | 3 | OK |
| 3 | Stall, both jaws (cyclic), jaws 44 open: R 13.8 N at the lip's end | Lip root at the top wall, rack side (Kt 2.5): b_eff 7.9, t 4.0, lever 5.9 | XY | 9.62 | 25.00 | 2.60 | 4 | **FAIL** |
| 4 | Crash 13 N pushes jaw A shut, jaws closed: rack A's +y end on the lip at y 31.4, R 12.8 N | Lip root at the top wall, rack side (Kt 2.5): b_eff 8.5, t 4.0, lever 5.9 | XY | 8.34 | 25.00 | 3.00 | 3 | **FAIL** |
| 5 | Added: opening against an obstacle, jaw A, jaws nearly closed: rack A's +y end at y 31.4, R 20.1 N | Lip root at the top wall, rack side (Kt 2.5): b_eff 8.5, t 4.0, lever 5.9 | XY | 13.12 | 25.00 | 1.91 | 3 | **FAIL** |
| 6 | Crash 13 N pushes jaw B shut, jaws 44 open: rack B's +y end at the plate's edge, R 17.5 N on the bottom edge (z 17.2) | Beside slot A's V apex (z 43.4, r 1.5 apex): b 20.4 × 5, lever 26.2 | XY | 8.10 | 25.00 | 3.09 | 3 | OK |
| 7 | Crash 13 N pushes jaw B shut, jaws 44 open: rack B's +y end at the plate's edge, R 17.5 N on the bottom edge (z 17.2) | Top-wall junction (z 48.5, r 2.0 fillet): b 25.5 × 5, lever 31.3 | XY | 7.74 | 25.00 | 3.23 | 3 | OK |
| 8 | Added: opening against an obstacle, jaw B, jaws 44 open: R 27.5 N on the bottom edge | Beside slot A's V apex (z 43.4, r 1.5 apex): b 20.4 × 5, lever 26.2 | XY | 12.74 | 25.00 | 1.96 | 3 | **FAIL** |
| 9 | Added: opening against an obstacle, jaw B, jaws 44 open: R 27.5 N on the bottom edge | Top-wall junction (z 48.5, r 2.0 fillet): b 25.5 × 5, lever 31.3 | XY | 12.17 | 25.00 | 2.05 | 3 | **FAIL** |
| 10 | Handling: 5 N pushes jaw B shut, jaws 44 open: R 6.7 N | Beside slot A's V apex (z 43.4, r 1.5 apex): b 20.4 × 5, lever 26.2 | XY | 3.12 | 25.00 | 8.02 | 3 | OK |
| 11 | Handling: 5 N pushes jaw B shut, jaws 44 open: R 6.7 N | Top-wall junction (z 48.5, r 2.0 fillet): b 25.5 × 5, lever 31.3 | XY | 2.98 | 25.00 | 8.40 | 3 | OK |
| 12 | Stall, one jaw blocked: rack A's +y end on the upper piece near slot A's end, R 27.5 N | Front plate at the top wall (Kt 1.5): b_eff 7.1, t 5.0, lever 5.1 | XY | 7.12 | 25.00 | 3.51 | 3 | OK |
| 13 | Crash 13 N pushes jaw A shut, jaws 44 open: rack A's −y end at the cover's edge, R 17.5 N: plate strip above the web | Cantilever 2.1 from the web top, b 8 × 5, Kt 2.5 | XY | 2.72 | 25.00 | 9.18 | 3 | OK |
| 14 | Crash 13 N pushes jaw A shut, jaws 44 open: rack A's −y end at the cover's edge, R 17.5 N: web, tension + bending at its junctions | 8 × 16, offset 10.1, Kt 2.5 | XY | 1.63 | 25.00 | 15.31 | 3 | OK |
| 15 | Crash 13 N pushes jaw A shut, jaws 44 open: rack A's −y end at the cover's edge, R 17.5 N: lip root above the post (the tie takes all of R) | b_eff 19.8 × 4, lever 11.8, sharp roots Kt 2.5 | XY | 9.76 | 25.00 | 2.56 | 3 | **FAIL** |
| 16 | Crash 13 N pushes jaw A shut, jaws 44 open: rack A's −y end at the cover's edge, R 17.5 N: post between the web and the lip | 4 × 8, lever 1.5, Kt 2.5 | XY | 3.62 | 25.00 | 6.90 | 3 | OK |
| 17 | Crash 13 N pushes jaw A shut, jaws 44 open: rack A's −y end at the cover's edge, R 17.5 N: M2.5 at y −24 (40% of R reaches it: 87 N), pull-out from the frame | M2.5, 7 engaged | Z shear | 1.58 | 6.25 | 3.95 | 3 | OK |
| 18 | Added: opening against an obstacle, jaw A, jaws 44 open: R 27.5 N: plate strip above the web | Cantilever 2.1 from the web top, b 8 × 5, Kt 2.5 | XY | 4.28 | 25.00 | 5.84 | 3 | OK |
| 19 | Added: opening against an obstacle, jaw A, jaws 44 open: R 27.5 N: web, tension + bending at its junctions | 8 × 16, offset 10.1, Kt 2.5 | XY | 2.57 | 25.00 | 9.74 | 3 | OK |
| 20 | Added: opening against an obstacle, jaw A, jaws 44 open: R 27.5 N: lip root above the post (the tie takes all of R) | b_eff 19.8 × 4, lever 11.8, sharp roots Kt 2.5 | XY | 15.34 | 25.00 | 1.63 | 3 | **FAIL** |
| 21 | Added: opening against an obstacle, jaw A, jaws 44 open: R 27.5 N: post between the web and the lip | 4 × 8, lever 1.5, Kt 2.5 | XY | 5.70 | 25.00 | 4.39 | 3 | OK |
| 22 | Added: opening against an obstacle, jaw A, jaws 44 open: R 27.5 N: M2.5 at y −24 (40% of R reaches it: 137 N), pull-out from the frame | M2.5, 7 engaged | Z shear | 2.49 | 6.25 | 2.51 | 3 | **FAIL** |
| 23 | Handling: 5 N pushes jaw A shut: R 6.7 N: plate strip above the web | Cantilever 2.1 from the web top, b 8 × 5, Kt 2.5 | XY | 1.05 | 25.00 | 23.87 | 3 | OK |
| 24 | Handling: 5 N pushes jaw A shut: R 6.7 N: web, tension + bending at its junctions | 8 × 16, offset 10.1, Kt 2.5 | XY | 0.63 | 25.00 | 39.80 | 3 | OK |
| 25 | Handling: 5 N pushes jaw A shut: R 6.7 N: lip root above the post (the tie takes all of R) | b_eff 19.8 × 4, lever 11.8, sharp roots Kt 2.5 | XY | 3.75 | 25.00 | 6.66 | 3 | OK |
| 26 | Handling: 5 N pushes jaw A shut: R 6.7 N: post between the web and the lip | 4 × 8, lever 1.5, Kt 2.5 | XY | 1.39 | 25.00 | 17.94 | 3 | OK |
| 27 | Handling: 5 N pushes jaw A shut: R 6.7 N: M2.5 at y −24 (40% of R reaches it: 33 N), pull-out from the frame | M2.5, 7 engaged | Z shear | 0.61 | 6.25 | 10.26 | 3 | OK |
| 28 | Yaw stall 7.1 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 29 N (×4.04: the rack lifted off the plate, the pinion holding its rear), jaws closed | Strip 9.75 × 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 2.79 | 12.50 | 4.47 | 3 | OK |
| 29 | Yaw stall 7.1 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 29 N (×4.04: the rack lifted off the plate, the pinion holding its rear), jaws 44 open | Strip 9.75 × 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 4.84 | 12.50 | 2.58 | 3 | **FAIL** |
| 30 | Hand push 5 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 20 N (×4.04: the rack lifted off the plate, the pinion holding its rear), jaws closed | Strip 9.75 × 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 1.97 | 12.50 | 6.35 | 3 | OK |
| 31 | Hand push 5 N on jaw B's tip, towards the wrist: its neck presses the strip under slot B with up to 20 N (×4.04: the rack lifted off the plate, the pinion holding its rear), jaws 44 open | Strip 9.75 × 5: slot end (Kt 1.7) / through the screw hole (Kt 2) | Z | 3.41 | 12.50 | 3.67 | 3 | OK |
| 32 | Rack A lift: separating 7.9 N + grip twist 410 N·mm → 13.8 N at the rack end | Top wall between the lip and the front plate, span 10.5, b 21 × 3 | XY | 1.44 | 25.00 | 17.34 | 3 | OK |
| 33 | USB tug 10 N tips the camera mount back: 53 N on the top wall's rear edge | 50 × 1 mm contact | XY | 1.06 | 25.00 | 23.67 | 3 | OK |

**Lowest SF: 1.30 (required 3), the lip root at the lip's end. One jaw blocked, jaws open.** Row 4 prints as 3.00
but is 2.996 before rounding, so it fails.

## Required changes (computed in the script's what-if lines)

1. **GUIDE_T 4 → 8.** This is `claw_frame.py`'s shared lip and rail thickness; the post's x range follows TIE_X0.
   - Lip: 5.20.
   - Lip above the post: 6.52, which fixes rows 15 and 20.
   - Post: 15.25.
   - GUIDE_T 10 gives 8.12 / 10.18. GUIDE_T 8 with r 2 fillets at the lip's roots gives 8.66.
   - The frame's rail wall needs GUIDE_T 10, or 8 with a fillet (frame report). Pick one value for both parts.
   - The thicker lip stiffens the tie path, so the M2.5's share falls below today's 20–35 % estimate. Row 22 needs it at
     33 % or less; confirm it in the proof test (the cover screws stay tight).
   - The lip stays above the claw servo's case (z ≥ 36.75 against 33.35), so it fits back to x 14.35, or to 12.35 at 10.
2. **Upper piece under the opening stall:** either change works.
   - **A second tie at y 24…32**: the same post and web, between the racks, outside every jaw path, joining the upper
     piece's lower half to the lip. With GUIDE_T 8: the strip under its web 5.84, the lip above its post 6.52.
   - **FRONT_T 5 → 7**: 3.85. This moves the fingers 2 mm forward.
3. **Strip under slot B:** either works.
   - **FRONT_Z0 −4 → −6**: an 11.75 mm strip, 4.34 (−5 gives 3.41). Re-run `assembly_check.py`; the plate then reaches
     6 mm below the claw's back face.
   - **Slot B's bottom clearance 0.25 → 0.6**: the neck then never reaches the strip, and the strip carries nothing. All
     of the pry (5.2 × the push) goes into the pinion's root lands, so this needs the pinion report's backlash change.
4. Re-run this script with the jaw and pinion changes. FACE_W 12 moves the fingers 2 mm forward, which raises every
   rack-end force R by about 2 %; FRONT_T 7 would add another 2 %.

The opening-stall case (case 4) drives change 2 and part of change 1. If the Architect rules it out of the spec, the
crash alone still fails rows 4 and 15, so change 1 is needed either way.

## Proof test

The spec's §8 says this part is "covered by the claw proof tests (frame and jaw)". Those tests don't load the lip, the
tie or the upper piece at the governing levels, and their pushes go only one way. **Replace it with this**, valid once
the changes above pass:

> **Proof test.** Claw assembled on the frame, wrist horn in a vice, servo powered and holding, jaws at 30 mm.
> 1. Each fingertip in turn, 3 mm from the tip: pull it away from the other jaw with **32 N** (3.3 kg on a luggage scale,
>    1.5 × the one-jaw stall), 10 s. Then push it towards the other jaw with **32 N** (1.5 × the opening stall; 20 N if
>    the Architect drops that case), 10 s.
> 2. Push jaw B's fingertip sideways towards the wrist (−z) with **10.7 N** (1.5 × the yaw stall), 10 s, jaws closed and
>    again at 44 mm.
>
> Pass:
> - no crack or whitening at the lip's roots, the tie's post, web and their corners, the upper piece's top corner and
>   slot A's V apex, the strip under slot B, or the slot ends;
> - both jaws still slide the full 0–44 mm without binding;
> - the cover screws are still tight.

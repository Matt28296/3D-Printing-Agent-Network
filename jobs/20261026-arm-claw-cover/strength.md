VERDICT: FAIL

# Strength check: 20261026-arm-claw-cover (round 1)

strength-analyst · 2026-10-26 · `python3 strength_calc.py` (plain python3; reads `claw_frame.py`, this job's `model.py`,
`tools/hobby_parts.py`, and the arm model for the fingertip forces)

The cover fails in two places.

1. **The 3 mm front plate.** When one jaw is blocked, the finger's grip moment (24 N × 50 mm about z) has to be held by
   the rack's two ends. One end pushes back on the lip, the other pushes the front plate forward with 27–31 N. That
   forward push lands at the rack's front end, 0.25–8.5 mm below the plate's sharp corner with the top wall. SF **1.28**
   short-term and **2.55** cyclic (required 3 / 4). Next to the front screw (rack B) the same push gives **2.17**.
2. **The strip under slot B.** A sideways push on jaw B's fingertip pitches the jaw, and its neck presses the strip under
   slot B downwards with 5.8 × the fingertip force. That strip is a beam along claw y, which runs across the layers in
   this print orientation. SF **1.36** (yaw stall) and **1.80** (hand push).

Every other check passes. The lowest of them is 3.19, on the same strip through the front-screw hole under the hand
push.

## Load cases

| # | Case | Load | Point and direction | Type, SF req |
|---|---|---|---|---|
| 1 | Thrust couple, one jaw blocked (added) | finger moment 1194 N·mm about z → R = 27.1 N (jaws closed) to 31.2 N (44 mm apart) at each rack end | rack A: lip (back) and front plate under the top wall (front, +y end); rack B: rail (back) and front plate above the wrist plate (front, −y end) | short-term, 3 |
| 2 | Same with both jaws, 12 N each | R 13.6–15.6 N | as 1 | cyclic, 4 |
| 3 | Rack A lift (spec) | 8.7 N separating + the grip twist 216 N·mm → 13.8 N at the rack end | top wall between the lip and the front plate | short-term, 3 |
| 4 | Sideways push on a finger (added) | hand push 5 N; yaw stall up to 6.6 N (arm sweep) | the neck bears on a slot edge (5.8 × F); the rack's rear on the pinion | short-term, 3 |
| 5 | Camera on the top wall (spec) | 10 N USB tug tips the mount: 74 N on the pad screws, pad edge on the cover's rear edge | top wall over the bulkhead | short-term, 3 |

## Build direction and sections

The cover prints standing on its −y end: print (X, Y, Z) = claw (x, −z, y + 32).

- **Along the layers**: front-plate, top-wall and lip bending in the side profile.
- **Across the layers**: the strips above and below the open-ended slots, which bend as beams along claw y, and shear on
  planes y = const.
- **Front plate under rack A**: a cantilever plate from the top wall. The rack's end load is spread over its height at
  0.25–8.5 mm from the corner, each slice spreading at 45° to the root. The plate's free end limits the spread on one
  side when the jaws are closed. Sharp inner corner, Kt 2.5.
- **Front plate above the wrist plate** (rack B, jaws closed): clamped by the front screw at y −24, 4.3 mm from the load.
  Cantilever from the wrist plate's top edge, Kt 1.5 (contact edge). Jaws 44 apart: the open panel, Roark point load.
- **Strip under slot B** (+y half, z 0…9.25, 3 thick): fixed at the slot's closed end (y −0.25), pinned by the front
  screw at y 24, free to the end. Loaded by the neck over its 14 mm length, at every jaw opening. Sharp root, Kt 2.5.
  Through the screw hole, Kt 2.

## Assumptions

- Contacts and clearances: 0.25 mm sliding gaps. Under the finger moment the rack cocks until opposite corners touch.
- The cover is screwed down with 2 × M3 (top) and 2 × M3 (front), snug. Friction is ignored.
- Sideways push: the jaw pitches about the slot edge (x 29.15) and its rack's rear end (x 19.4). For jaw B pushed
  towards the wrist plate, the neck loads slot B's bottom strip. Every other slot edge is backed by solid plate or by the
  top wall.

## Allowables and sources

`library/materials.csv` has no measured row: these are the strength-checks **placeholder** PETG values. NEEDS_TEST is the
best verdict possible.

| Quantity | Value | Source |
|---|---|---|
| Along the layers (XY) | 25 MPa | skill placeholder, PETG |
| Across the layers (Z) | 12.5 MPa | placeholder × 0.5 |
| Interlayer shear | 6.25 MPa | 0.5 × 12.5 |
| Kt | 2.5 sharp inner corner, 2 hole, 1.5 contact edge / r ≥ 0.25 h fillet | skill |

Required SF is 3 for short-term loads and 4 for cyclic loads. Service temperature 40 °C: OK.

## Results (copied from `python3 strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | one jaw blocked 24 N, jaws 0 apart: rack A front end (27.1 N at y 28.3) bends the front plate at the top-wall corner (sharp, Kt 2.5) | XY | 19.23 | 25.00 | 1.30 | 3 | **FAIL** |
| 2 | one jaw blocked 24 N, jaws 44 apart: rack A front end (31.2 N at y 6.3) bends the front plate at the top-wall corner (sharp, Kt 2.5) | XY | 19.61 | 25.00 | 1.28 | 3 | **FAIL** |
| 3 | one jaw blocked 24 N, jaws closed: rack B front end (27.1 N at y -28.3, next to the front screw) bends the plate above the clamped edge on the wrist plate (contact edge, Kt 1.5) | XY | 11.54 | 25.00 | 2.17 | 3 | **FAIL** |
| 4 | one jaw blocked 24 N, jaws 44 apart: rack B front end (31.2 N at y -6.3) on the open plate panel (Roark, simply supported r 15) | XY | 6.95 | 25.00 | 3.60 | 3 | OK |
| 5 | both jaws 12 N (cyclic), jaws 0 apart: rack A front end (13.6 N at y 28.3) bends the front plate at the top-wall corner (sharp, Kt 2.5) | XY | 9.61 | 25.00 | 2.60 | 4 | **FAIL** |
| 6 | both jaws 12 N (cyclic), jaws 44 apart: rack A front end (15.6 N at y 6.3) bends the front plate at the top-wall corner (sharp, Kt 2.5) | XY | 9.80 | 25.00 | 2.55 | 4 | **FAIL** |
| 7 | both jaws 12 N (cyclic), jaws closed: rack B front end (13.6 N at y -28.3, next to the front screw) bends the plate above the clamped edge on the wrist plate (contact edge, Kt 1.5) | XY | 5.77 | 25.00 | 4.33 | 4 | OK |
| 8 | both jaws 12 N (cyclic), jaws 44 apart: rack B front end (15.6 N at y -6.3) on the open plate panel (Roark, simply supported r 15) | XY | 3.48 | 25.00 | 7.19 | 4 | OK |
| 9 | rack A back end 31.2 N on the lip face (3 mm x lip height, compression) | XY | 1.49 | 25.00 | 16.83 | 3 | OK |
| 10 | rack A lift (8.7 N separating + twist 216 N.mm -> 13.8 N at the rack end) on the top wall span 8.5 between lip and front plate (fixed ends) | XY | 1.57 | 25.00 | 15.94 | 3 | OK |
| 11 | hand push 5 N: strip under slot B, root at the slot's closed end (Z, sharp, Kt 2.5) | Z | 6.96 | 12.50 | 1.80 | 3 | **FAIL** |
| 12 | hand push 5 N: strip under slot B through the front-screw hole (Z, Kt 2) | Z | 3.92 | 12.50 | 3.19 | 3 | OK |
| 13 | hand push 5 N: neck bearing on the slot edge (29 N over 14 x 3) | XY | 0.69 | 25.00 | 36.08 | 3 | OK |
| 14 | hand push 5 N: front-screw hole tear-out up to the slot edge (ligament 4.45, Z shear) | Z shear | 1.09 | 6.25 | 5.73 | 3 | OK |
| 15 | yaw-stall sweep: strip under slot B, root at the slot's closed end (Z, sharp, Kt 2.5) | Z | 9.17 | 12.50 | 1.36 | 3 | **FAIL** |
| 16 | yaw-stall sweep: strip under slot B through the front-screw hole (Z, Kt 2) | Z | 5.17 | 12.50 | 2.42 | 3 | **FAIL** |
| 17 | yaw-stall sweep: neck bearing on the slot edge (38 N over 14 x 3) | XY | 0.91 | 25.00 | 27.37 | 3 | OK |
| 18 | yaw-stall sweep: front-screw hole tear-out up to the slot edge (ligament 4.45, Z shear) | Z shear | 1.44 | 6.25 | 4.35 | 3 | OK |
| 19 | USB tug 10 N tips the camera mount back: pad edge on the top wall's rear edge (84 N over 50 x 1 mm) | XY | 1.68 | 25.00 | 14.89 | 3 | OK |

**Lowest SF 1.28 (required 3): front plate at the top-wall corner, one jaw blocked, jaws 44 mm apart.**

## Required changes (computed in the script's what-if lines)

1. **FRONT_T 3 → 5** (`claw_frame.py`).
   - Corner: 1.28 → 3.54 short-term, about 7.1 cyclic.
   - Above the clamped edge: 2.17 → 6.02.
   - Slot-B strip through the screw hole: 2.42 → about 4.0.
   - FRONT_T 4 is not enough (2.27).
   - Knock-on: the front screws become M3×14, and the fingers start 2 mm further forward (the fingertip moves to
     x 78.15). The jaw's recommended redesign is checked with this.
2. **r ≥ 2 fillets at the closed ends of both slots** (Kt 2.5 → 1.5). With FRONT_T 5, the slot-B strip goes to 3.79
   under the yaw stall and about 5 under the hand push. Slot B's closed end is at the bottom of the slot as printed, so
   its fillets print as plain concave corners. Slot A's are at its bridged top and print as short 45° overhangs.
3. **After the jaw redesign, re-check this part.** The jaw report asks for taller necks on taller racks, which makes the
   slots taller. With RACK_BACK 10, slot B reaches down to the wrist-plate level and leaves only a 6 mm strip under it
   (z 0…6, with the front screw in it). That strip would fail again unless it is thickened outboard, for example 8 mm in
   x over z 0…6, in front of the plate where the fingers don't reach. The jaw report also asks to keep a strip of plate
   above slot A on the −y half, so rack A still bears forward at that end when a jaw is pushed open.

## Proof test (after the changes; replaces the spec §8 test)

Run it after the frame and jaw proof tests.

1. Grip the vice-clamped block 8 mm off-centre at full close for 10 s, 5 times. This puts the full thrust couple on the
   front plate.
2. Push 7.5 N sideways towards the wrist (−z) on jaw B's fingertip for 1 min.

Pass:

- no cracks or whitening at the front plate's top corner, around the front screws or at the slot ends;
- both jaws still slide the full 0–44 mm without binding;
- the cover screws are still tight.

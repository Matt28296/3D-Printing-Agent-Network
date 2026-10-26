VERDICT: FAIL

# Strength check: 20261026-arm-camera-mount (round 1)

strength-analyst · 2026-10-26 · `python3 strength_calc.py` (plain python3; reads `claw_frame.py`, this job's `model.py`,
`tools/hobby_parts.py` and `geometry.json`)

The Brio sits on one 1/4"-20 thumb screw. A 10 N tug on its USB cable at the camera's end twists the camera about that
screw with 510 N·mm. With friction ignored, the camera's back face then bears on **one end of the 3 mm lip** with 23 N,
6 mm above the seat, against a sharp root corner: **SF 0.86**. Everything else passes with SF 4.5 or more: the seat, the
pad, the slot, the screws and the mount bending as a beam across the layers.

## Load cases

| # | Case | Load | Point and direction | Type, SF req |
|---|---|---|---|---|
| 1 | USB-cable tug (spec) | 10 N, any direction | the Brio's end (y ±51), mid height: (−3.3, ±51, 64.2) | short-term, 3 |
| 2 | Camera weight with arm accelerations (spec) | (63 + 4) g × 3 | camera CoG (−3.25, 0, 64.2), any direction | cyclic, 4 |
| 3 | Yaw stall with the camera against an obstacle (added) | ≤ 1000 N·mm / R ≈ 7.7 N at the camera (R ≥ 130) | camera body | short-term, 3 |

Case 3 is smaller than the 10 N tug at a similar lever, so case 1 covers it.

The tug produces four effects, each checked:

- twist about the screw: lip end;
- lift of the camera's end: thumb-screw tension of 33 N with a pivot on the seat's end, giving head bearing,
  pull-through and seat bending;
- slide along the slot: the screw bears on the slot end;
- the mount tipping on the cover: pad screws and pad edge.

## Build direction and sections

The mount prints standing on its −y end: print (X, Y, Z) = claw (x, −z, y + 28). The side profile (pad, 30° seat, lip) is
in the bed plane, so seat and lip bending run along the layers (25 MPa). Bending of the whole mount as a beam along claw
y, and shear on planes y = const, run across them.

Sections from the build123d sections of `design()`:

- seat cut at x −2…−0.5: A 230.9, Z 177.6 mm³;
- pad at x 3: Z 102.1 mm³;
- whole profile for bending along y: Z 489 mm³.

The lip is 3 × 6 × 50, with a sharp 90° root on the seat (Kt 2.5). The camera's back edge is rounded (BRIO_EDGE_R ≈ 6),
so it touches the lip near its top: lever 6.

## Assumptions

- Friction between the camera and the seat is ignored. A tightened thumb screw would help, but its preload is unknown.
  The spec's proof test requires that "the camera has not turned on the screw".
- The lip end load spreads at 45° on one side only: b_eff = 6 + 2 mm.
- Thumb-screw head: Ø12 knurled head (minimum assumed).

## Allowables and sources

`library/materials.csv` has no measured row: these are the strength-checks **placeholder** PETG values. NEEDS_TEST is the
best verdict possible.

| Quantity | Value | Source |
|---|---|---|
| Along the layers | 25 MPa | skill placeholder, PETG |
| Across the layers | 12.5 MPa | × 0.5 |
| Interlayer shear | 6.25 MPa | 0.5 × 12.5 |
| Kt | 2.5 sharp inner corner, 2 slot or hole, 1.5 with r ≥ 0.25 t | skill |

Required SF is 3 for short-term loads and 4 for cyclic loads. Service temperature 40 °C: OK.

## Results (copied from `python3 strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | USB tug twists the camera on its screw: lip root at the lip end (sharp corner with the seat, Kt 2.5) | XY | 28.98 | 25.00 | 0.86 | 3 | **FAIL** |
| 2 | camera inertia x3 along the lens axis into the lip (spread over 50) (cyclic, Kt 2.5) | XY | 0.39 | 25.00 | 63.39 | 4 | OK |
| 3 | tug lifts the camera end: thumb-screw head bearing on the seat under the slot (33 N, head D12) | XY | 1.16 | 25.00 | 21.47 | 3 | OK |
| 4 | tug lifts the camera end: head pull-through of the 4 mm seat (Z shear, conservative) | Z shear | 0.22 | 6.25 | 28.40 | 3 | OK |
| 5 | tug lifts the camera end: seat root at the pad (33 N on the screw 13.5 away, b_eff 34; the slot is 10 mm from the root, no Kt there) | XY | 4.93 | 25.00 | 5.07 | 3 | OK |
| 6 | tug lifts the camera end: seat through the slot at the thumb-screw head edge (arm 6, net width 27, slot Kt 2) | XY | 5.53 | 25.00 | 4.52 | 3 | OK |
| 7 | tug along the camera: thumb screw bearing on the slot end (10 N, D6.35 x seat 4) | XY | 0.39 | 25.00 | 63.50 | 3 | OK |
| 8 | tug along the camera: slot-end tear-out to the seat end (ligament 14.5, plane y = const: Z shear) | Z shear | 0.09 | 6.25 | 72.38 | 3 | OK |
| 9 | USB tug, worst direction: seat root bending in the profile (206 N.mm, Z 178 from CAD) | XY | 1.16 | 25.00 | 21.58 | 3 | OK |
| 10 | USB tug, worst direction: pad between the seat and the screws (206 N.mm, Z 102 from CAD) | XY | 2.01 | 25.00 | 12.41 | 3 | OK |
| 11 | USB tug: mount as a beam along y between the pad screws (540 N.mm, Z 489, slot Kt 2, across the layers) | Z | 2.21 | 12.50 | 5.66 | 3 | OK |
| 12 | camera weight x3 (cyclic): seat root bending in the profile | XY | 0.23 | 25.00 | 109.45 | 4 | OK |
| 13 | USB tug tips the mount back over the cover's rear edge: button head pull-through of the 3.5 pad (37 N per screw, head D5.7, conservative Z shear) | Z shear | 0.59 | 6.25 | 10.59 | 3 | OK |
| 14 | USB tug along y: pad-hole tear-out towards the pad end (e 5.0, plane y = const: Z shear) | Z shear | 0.22 | 6.25 | 28.00 | 3 | OK |

**Lowest SF 0.86 (required 3): the lip root at the lip's end under the USB-tug twist.**

## Required changes (computed in the script's what-if lines)

**LIP_T 3 → 5 with an r ≥ 2 fillet at the lip root** (in the profile, so it prints in the bed plane). SF 0.86 → 3.99.

- The fillet clears the Brio's rounded back edge (≈ r 6, but measure yours).
- LIP_T 5 with a sharp root gives only 2.40. A 3 mm lip with a fillet gives 1.44.
- LIP_T 6 with a fillet gives 5.75.

Also strain-relieve the USB cable. Run it down the arm with ties and a slack loop at each joint, and anchor it at the
base, so a snag pulls on the base, not the camera's end. That protects this lip, the frame's wrist joint and the arm
links. See the frame report and the arm jobs' round 4 notes.

## Proof test (spec §8, kept, with the cable pull at 1.5 × service)

1. Camera fitted, arm powered: run the arm through its fastest full-range sweep 10 times.
2. Pull the camera's USB cable with 15 N (≈1.5 kg on a luggage scale) for 10 s along each axis, at the plug end.

Pass:

- no crack or whitening at the lip root or the seat root;
- the camera has not turned on the screw;
- the screws are still tight.

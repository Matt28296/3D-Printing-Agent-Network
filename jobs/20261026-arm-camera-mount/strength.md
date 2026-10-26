VERDICT: NEEDS_TEST

# Strength check: 20261026-arm-camera-mount (round 2)

strength-analyst (independent review of the round-2 geometry) · 2026-10-26 ·
`python3 jobs/20261026-arm-camera-mount/strength_calc.py` (plain python3: reads `claw_frame.py`, this job's `model.py`
and `tools/hobby_parts.py` with `ast`)

Round 1's fix works. The 5 mm lip with its r 2 root fillet holds the USB tug's twist with **SF 4.53**, against 0.86 in
round 1. That is the lowest row, with the USB port assumed 45 mm off the camera's centre; every other row gives 5.76 or
more. Every row passes, but the allowables are placeholders, so the verdict is NEEDS_TEST. The spec's §8 proof test pulls
the cable at 1.0 × the service load and has to be raised (below).

## Round-1 fixes: made?

| Round-1 required change | Round 2 | Made? |
|---|---|---|
| LIP_T 3 → 5 with an r ≥ 2 fillet at the lip root | LIP_T 5, LIP_FILLET 2, in the side profile (it prints in the bed plane) | Yes: rows 1–4, lowest 4.53 |
| Strain-relieve the USB cable along the arm (advice) | The spec still puts the tug at the camera | A system decision; this report keeps the tug at the plug |
| Proof test: cable pull 15 N (1.5 ×) | Spec §8 still pulls 10 N | No: see the proof test below |

## Load cases

| # | Case | Load | Point and direction | Type, SF req |
|---|---|---|---|---|
| 1 | USB cable tug (spec) | 10 N in any direction | The right-angle plug's cable exit, 8 mm behind the camera's back, at mid-height: G (−18.8, y_port, 91.6). The port's position is unmeasured (deep review 01 S5), so y_port is anywhere within ±45 of the centre | Short-term, 3 |
| 2 | Camera mass and inertia in a moving start or stop (spec) | Camera + thumb screw 68 g × 3. The firmware ramps at 250 °/s² to 66.7 °/s. At the camera that is 2.37 m/s² tangential plus 1.73 m/s² centripetal, and with × 2 for servo tracking at most 0.84 g dynamic. The spec's × 3 (1 g + 2 g) covers it (info row 23) | Camera's centre of mass | Cyclic, 4 |
| 3 | Added: the camera hits the desk (SYS-11: the first contact in 37 % of crash poses) | 13 N along the camera's length at its end face | Slot end, pad screws, thumb screw | Short-term, 3 |
| 4 | SYS-04 sideways moment (spec) | ≈0.8 N, ≈30 mm over the top wall: ≈24 N·mm | Pad and its 2 screws | Sustained, 4. Covered: the tug's moment on the pad (row 13) is 17 × larger and gives SF 13 |
| 5 | Handling; base-yaw stall with the camera against an obstacle | 5 N; ≤ 1079 N·mm / R ≥ 130 mm = 8.3 N on the camera body | As case 1 | Covered by case 1 (10 N at a similar or longer lever) |

The tug has four effects, each checked:

- it twists the camera about the thumb screw, and the camera's back bears on one end of the lip;
- it lifts one end of the camera, so the thumb screw pulls on the seat;
- it slides the camera along its slot, so the screw bears on the slot's end;
- it tips the whole mount on the cover, so the pad screws pull.

## Build direction and sections

The mount prints standing on its −y end (print Z = claw y). The side profile (pad, 34° seat, lip and root fillet) lies in
the bed plane, so seat and lip bending run along the layers (25 MPa). The mount bending as a beam along y runs across
them (12.5 MPa), and shear on planes y = const is interlayer shear (6.25 MPa).

- **Lip:** 5 thick, 6 tall, 50 long (y −28…22), r 2 root fillet (Kt 1.5). The Brio's rounded back edge (r ≈ 6,
  `BRIO_EDGE_R`) meets the lip at its top: lever 6. A load at the lip's end spreads at 45° to one side only:
  b_eff = 2 + 6 = 8.
- **Seat:** 4 thick, 50 wide. The 1/4" slot is Ø6.85 printed and runs ±4 along y (Kt 2).
- **Thumb screw:** 1/4"-20 × 5/16", knurled head assumed Ø12 at least.
- **Pad:** 3.5 thick on the cover's top wall. 2 × M3 × 18 button heads (Ø5.7) at (6.75, −23) and (6.75, 14), 11.5 mm
  engaged in the bulkhead.
- **Whole profile** as a beam along y: A 219, I 19,114 mm⁴, c 17.9; through the slot, I 19,059.

## Assumptions

- Friction between the camera and the seat is ignored. The thumb screw's preload is unknown, so it isn't relied on.
- The USB port can be anywhere within ±45 mm of the camera's centre. Measuring it (BUILD_GUIDE §2) would tighten the
  twist rows: with the port at the centre, the twist on the lip comes only from a tug along the camera (rows 3–4).
- The mount tips about its pad's rear edge (x 0) when the tug pulls back along x.
- Service temperature 40 °C against PETG softening at about 70 °C: OK.

## Allowables and sources

`library/materials.csv` has no measured row, so these are the strength-checks **placeholder** PETG values and
NEEDS_TEST is the best possible verdict.

| Quantity | Value | Source |
|---|---|---|
| Along the layers (seat, lip, pad) | 25 MPa | Skill placeholder, PETG |
| Across the layers (beam along y) | 12.5 MPa | 0.5 × in-plane |
| Interlayer shear | 6.25 MPa | 0.5 × 12.5 (Tresca) |
| Bearing | 25 MPa | In-plane value |
| Kt | 1.5 for r ≥ 0.25 t (lip fillet); 2 at the slot | Skill |

## Results (copied from `python3 strength_calc.py`)

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | USB tug 10 N along the lens axis at a port 45 mm off the centre: twist 450 N·mm, the camera's back bears on the lip's +y end (22 from the screw) with 20.5 N | Lip root, 5 thick, r 2 fillet (Kt 1.5), b_eff 8, lever 6 | XY | 5.52 | 25.00 | **4.53** | 3 | OK |
| 2 | USB tug 10 N along the lens axis at a port 45 mm off the centre: twist 450 N·mm, the camera's back bears on the lip's −y end (28) with 16.1 N | Lip root, 5 thick, r 2 fillet (Kt 1.5), b_eff 8, lever 6 | XY | 4.34 | 25.00 | 5.76 | 3 | OK |
| 3 | USB tug 10 N along the camera at the plug (21.5 behind the screw): twist 215 N·mm, the camera's back bears on the lip's +y end (22 from the screw) with 9.8 N | Lip root, 5 thick, r 2 fillet (Kt 1.5), b_eff 8, lever 6 | XY | 2.64 | 25.00 | 9.47 | 3 | OK |
| 4 | USB tug 10 N along the camera at the plug (21.5 behind the screw): twist 215 N·mm, the camera's back bears on the lip's −y end (28) with 7.7 N | Lip root, 5 thick, r 2 fillet (Kt 1.5), b_eff 8, lever 6 | XY | 2.07 | 25.00 | 12.06 | 3 | OK |
| 5 | USB tug 10 N lifting the camera's end (port at +45): thumb screw 26 N, head on the seat's underside | Ø12 head over the Ø6.85 slot | XY | 0.84 | 25.00 | 29.63 | 3 | OK |
| 6 | Same: the seat bends across the slot under the head (port at +45) | 4 thick, Kt 2.0 (slot) | XY | 0.52 | 25.00 | 47.67 | 3 | OK |
| 7 | Same: seat root at the pad, the screw's 26 N at the thread (port at +45) | 50 × 4, lever 13.5 | XY | 2.64 | 25.00 | 9.47 | 3 | OK |
| 8 | USB tug 10 N lifting the camera's end (port at −45): thumb screw 30 N, head on the seat's underside | Ø12 head over the Ø6.85 slot | XY | 0.99 | 25.00 | 25.36 | 3 | OK |
| 9 | Same: the seat bends across the slot under the head (port at −45) | 4 thick, Kt 2.0 (slot) | XY | 0.61 | 25.00 | 40.81 | 3 | OK |
| 10 | Same: seat root at the pad, the screw's 30 N at the thread (port at −45) | 50 × 4, lever 13.5 | XY | 3.08 | 25.00 | 8.11 | 3 | OK |
| 11 | USB tug 10 N along the camera: thumb screw bears on the slot's end | Ø6.35 × 4 seat | XY | 0.39 | 25.00 | 63.50 | 3 | OK |
| 12 | Same: slot-end tear-out towards the seat's end (ligament 14.5, planes y = const) | Interlayer shear | Z shear | 0.09 | 6.25 | 72.38 | 3 | OK |
| 13 | USB tug 10 N along x at the plug (z 91.6): the mount tips on the cover's rear edge, M3 × 18 screws 59 N | Button-head pull-through of the 3.5 pad (2 screws) | Z shear | 0.47 | 6.25 | 13.18 | 3 | OK |
| 14 | USB tug along y: pad-hole bearing, both M3 shanks | Ø3 × 3.5 pad | XY | 0.48 | 25.00 | 52.50 | 3 | OK |
| 15 | USB tug 10 N along z at the port (31 beyond the +y screw): the mount bends along y, at the +y screw | Profile A 219, I 19114 mm⁴, c 17.9 (no slot there) | Z | 0.29 | 12.50 | 43.14 | 3 | OK |
| 16 | Same, through the 1/4" slot at the thread (y 0, M 193 N·mm) | I 19059 mm⁴, c 18.0, slot Kt 2.0 | Z | 0.36 | 12.50 | 34.39 | 3 | OK |
| 17 | Camera 68 g ×3 along the lens axis into the lip (cyclic) | Lip root, spread over 50 | XY | 0.09 | 25.00 | 289.17 | 4 | OK |
| 18 | Camera ×3 across the seat (cyclic): seat root at the pad | 50 × 4 | XY | 0.23 | 25.00 | 107.46 | 4 | OK |
| 19 | Added: Brio's end hits the desk, 13 N along y: screw slides 4 mm, bears on the slot end | Ø6.35 × 4 | XY | 0.51 | 25.00 | 48.85 | 3 | OK |
| 20 | Same: slot-end tear-out (ligament 14.5) | Interlayer shear | Z shear | 0.11 | 6.25 | 55.67 | 3 | OK |
| 21 | Same: the mount tips about x on its pad, 10 N more on one M3 | Button-head pull-through | Z shear | 0.16 | 6.25 | 39.69 | 3 | OK |
| 22 | Same: thumb screw tension 2.4 N (crash force 13.5 above the seat) | Head bearing | XY | 0.08 | 25.00 | 321.30 | 3 | OK |

Information rows (not in the verdict):

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 23 | Info: 250 °/s² ramp: tangential 2.37 + centripetal 1.73 m/s², ×2 overshoot = 0.84 g dynamic; the spec's ×3 (1 g + 2 g) covers it | – | – | – | – | – | – |  |

**Lowest SF: 4.53 (required 3), the lip root at its +y end under the USB tug's twist, with the port 45 mm off-centre.**

No geometry change is needed. The claw frame's report fails the wrist clamp under this same tug and under the camera's
desk hit (2.39 and 2.12). Tying the cable to the frame near the wrist axis, with a slack loop to the plug (SYS-10), would
take the tug off both parts.

## Proof test

The spec's §8 pulls the cable with 10 N, 1.0 × the service tug. **Replace it with this:**

> **Proof test.**
> 1. Camera fitted, arm powered: run the arm through its fastest full-range sweep 10 times.
> 2. Claw off the arm, wrist horn in a vice. Pull the USB cable at the plug with **15 N** (1.5 kg on a luggage scale,
>    1.5 × the 10 N tug), 10 s each: both ways along the lens axis, both ways along the camera's length, and both ways
>    across them (up and down).
> 3. Loop a cord round the camera 45 mm from its centre (6 mm in from one end). Pull **15 N** along the lens axis,
>    forwards then backwards, 10 s each. Repeat at the other end. This is the twist from a port 45 mm off-centre.
> 4. Push the camera's end face along its length with **20 N** (1.5 × the 13 N desk hit), 10 s each way.
>
> Pass:
> - no crack or whitening at the lip's root fillet, the seat's root or the slot's ends;
> - the camera hasn't turned on the thumb screw (pen line across the camera and the seat);
> - the screws are still tight.

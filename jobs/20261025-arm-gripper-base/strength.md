VERDICT: FAIL

# Strength check: 20261025-arm-gripper-base

strength-analyst · 2026-10-26 · calculations in `strength_calc.py` (plain python3; section properties cross-checked against build123d sections of `design()`)

The spec's cases pass: wrist-stall bearing SF 17.6, and the jaw-block root under the real worst grip (10.7 N with
the object at the jaw root, not 2.9 N at the tip) at SF 5.0 across the layers. The part fails at the **wrist-horn
joint**, which is one M2 screw in a 3 mm floor, and in **out-of-plane bending** of the 5 mm plate over the pocket and
at the SG90 pilot row. Lowest SF 0.71. **The 5 N hand push alone also fails** (SF 1.39 at the horn screw, 2.56 over
the pocket).

## Load cases

**Mass model (re-derived, not taken from the spec).** Printed parts = geometry.json volume x 1.27 g/cm³ (upper
link 27.0 g, forearm 15.3 g, gripper base 19.9 g, jaw 4.3 g, turntable 77.0 g), CG from the build123d centre of mass of
`design()`; MG996R 55 g, SG90 9 g (hobby_parts.py); horn + screws 4 g (MG996R) / 1.5 g (SG90); 10 g cable allowance;
50 g payload at the fingertip. Arm straight and horizontal, static moments: about the yaw axis 358 N·mm, shoulder
337 (spec 310), elbow 156 (spec 140), wrist 63, gripper 28. Because the arm steps forward in +Y, the weight also
puts a pose-independent **out-of-plane** moment on every joint: 43 N·mm at the shoulder horn, 21 at the elbow, 8.6
at the wrist, 98 at the upright root (the spec assumed 120). The dynamic factor is x2, as the spec uses.

**Loads the spec misses (added here).** The spec treats every arm load as acting in the plane of its link. The
pitch servos only resist moments about their own axes, so a sideways load on the arm is carried by nothing but the
printed plates and the horn joints:
1. **Base-yaw stall into a side obstacle** (the yaw servo, or a hand stopping a yaw move): F = 1000 N·mm / R at the
   contact, horizontal and tangential. Swept over shoulder 0–180°, elbow ±90° and wrist ±90° in 5° steps, with the
   joints kept above the desk, and scaled down wherever a pitch servo would backdrive first (shoulder and elbow
   1000 N·mm, wrist 160 N·mm). Up to 12 N at the fingertip, of which up to 8.2 N is out of plane. This is the spec's
   own "a stalled servo is the worst case" basis. Short-term, SF 3.
2. **Hand push 5 N sideways (±Y) at the fingertip**, any pose (with the arm pointing up, no servo backdrives under it).
   Short-term, SF 3.
3. **Horn joints.** Each link is held on its horn only by the small screws through the horn arms: the centre screw
   passes through the Ø6.5 access hole and its head bears on the horn, not on the link. Out-of-plane moments pull those
   screws out of the floor left above the 2 mm pocket (3 or 4 mm), shearing the layers. For torsion about the link axis
   the screws sit on the axis, so the only lever is the hub radius (5.5 mm on the MG996R, 3.6 mm on the SG90).
   Assumed: M2 self-tapping screws, Ø1.6 drilled pilot, engagement = floor thickness, MG996R outermost arm hole r 15
   (transverse lever 15 + 17.5 = 32.5, one screw), SG90 inner arm hole r 7 (weak-direction lever 14 − 7 = 7).

| Case | Load | Applied at, direction | Duration | Source |
|---|---|---|---|---|
| Wrist stall | 160 N·mm | single-arm pocket walls | short-term | spec |
| Gripper stall reaction | 160 N·mm | 2 slotted SG90 pilots | short-term | spec |
| Grip with the object at the jaw root | 160/15 = 10.7 N, 11.9 mm above the root | fixed-jaw block, across the layers | short-term | **added** (spec: 2.9 N at the tip) |
| Weight beyond the wrist x2 | 127 in plane / 17 out of plane N·mm | horn, plate | sustained | re-derived |
| Base-yaw stall sweep | transverse up to 893 N·mm at the wrist horn | horn screw, plate, SG90 screws | short-term | **added** |
| Hand push 5 N sideways at the fingertip | 475 N·mm at the wrist horn | same | short-term | **added** |
| Spec proof squeeze, 10 N at the tip | 119 N·mm at the jaw root | fixed jaw | test | spec §8 (advisory row) |

Build direction: printed flat, horn pocket on the bed, fixed jaw growing up. Jaw-root bending is across the layers.
Plate bending runs along them. Screw pull-out shears them.

## Assumptions

- The SG90 single-arm horn has one arm screw. In the weak direction the plate pivots on the arm tip, leaving a 7 mm
  lever. Torsion pivots on the hub edge (3.6 mm).
- Jaw root: an end load spreads at 45° on one side only, b_eff = 12 mm, sharp root Kt 2.5.
- Plate sections at x 10 and x 20.75 are computed from the parameters and match the CAD (229/230 and 242 mm⁴).
- Advisory: the gripper-window rails alone, with the servo case ignored (as for the links).
- Pull-out and thread stripping: τ = F/(π·d_pilot·L), checked against the interlayer shear allowable.
- Bearing and tear-out at vertical pilots in flat plates are in-plane. Tear-out from horizontal holes in vertical
  walls shears the layers.
- Combined moments are added rather than combined vectorially, except where the script says otherwise (conservative).
- Pilot holes are taken at their nominal size. Hoop stress from driving the self-tapping screws into thin ligaments is
  not computable by hand, so it is left to the proof test and the fit coupon.

## Allowables and sources
`library/materials.csv` has no measured row and no printed-specimen datasheet is in `inputs/`, so these are the
strength-checks **placeholder** values for PETG. **NEEDS_TEST is the best verdict possible.**

| Quantity | Value | Source |
|---|---|---|
| Tension/bending along the layers (XY) | 25 MPa | skill placeholder, PETG |
| Tension/bending across the layers (Z) | 12.5 MPa | placeholder x 0.5 |
| Shear in-plane / interlayer (incl. screw pull-out, tear-out in vertical walls) | 12.5 / 6.25 MPa | 0.5 x the normal value (Tresca), assumption |
| Bearing, compression (any direction) | 25 MPa | in-plane value: compression does not separate layers |
| Kt | 2.5 sharp internal corner or window corner; 2 hole (PETG); 1.5 rounded pocket tip | skill |

Required SF: 3 short-term, 4 sustained or cyclic. Service temperature 40 °C (servo cases up to 45 °C) against PETG
softening at about 70 °C: margin of 25 °C or more, OK.

## Results (copied from `python3 strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | wrist stall 160 N.mm: horn-pocket wall bearing | XY | 1.42 | 25.00 | 17.63 | 3 | OK |
| 2 | gripper stall: SG90 tab-pilot bearing | XY | 0.77 | 25.00 | 32.41 | 3 | OK |
| 3 | gripper stall: pilot tear-out to the +y edge (e 9) | XY shear | 0.09 | 12.50 | 145.85 | 3 | OK |
| 4 | weight x2 + 1 N along x: pilot-to-window ligament 1.55 | XY shear | 0.14 | 12.50 | 92.49 | 3 | OK |
| 5 | grip at the jaw root, 10.7 N: jaw-block root (Kt 2.5) | Z | 2.48 | 12.50 | 5.04 | 3 | OK |
| 6 | weight x2 (sustained): wrist horn arm-screw pull-out (floor 3) | Z shear | 0.32 | 6.25 | 19.61 | 4 | OK |
| 7 | yaw-stall sweep: wrist horn arm-screw pull-out (floor 3, lever 7) | Z shear | 8.84 | 6.25 | 0.71 | 3 | **FAIL** |
| 8 | yaw-stall sweep: out-of-plane bending x10 over the pocket (Kt 2 arm-screw hole) | XY | 18.73 | 25.00 | 1.33 | 3 | **FAIL** |
| 9 | yaw-stall sweep: out-of-plane bending at the SG90 pilot row x20.75 (Kt 2) | XY | 14.97 | 25.00 | 1.67 | 3 | **FAIL** |
| 10 | yaw-stall sweep: gripper SG90 tab screw pull-out (1 screw, L 5) | Z shear | 0.92 | 6.25 | 6.79 | 3 | OK |
| 11 | hand push 5 N: wrist horn arm-screw pull-out (floor 3, lever 7) | Z shear | 4.50 | 6.25 | 1.39 | 3 | **FAIL** |
| 12 | hand push 5 N: out-of-plane bending x10 over the pocket (Kt 2 arm-screw hole) | XY | 9.81 | 25.00 | 2.55 | 3 | **FAIL** |
| 13 | hand push 5 N: out-of-plane bending at the SG90 pilot row x20.75 (Kt 2) | XY | 7.68 | 25.00 | 3.25 | 3 | OK |
| 14 | hand push 5 N: gripper SG90 tab screw pull-out (1 screw, L 5) | Z shear | 0.47 | 6.25 | 13.23 | 3 | OK |

Advisory rows (not in the verdict, reason under Assumptions):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| proof squeeze 10 N at the tip: jaw-block root (Kt 2.5) | Z | 2.32 | 12.50 | 5.38 | 2 |
| yaw-stall sweep: gripper window rails alone, servo case ignored (Kt 2.5) | XY | 34.53 | 25.00 | 0.72 | 3 |
| hand push 5 N: gripper window rails alone, servo case ignored (Kt 2.5) | XY | 17.71 | 25.00 | 1.41 | 3 |

**lowest SF 0.71 (required 3) at: yaw-stall sweep: wrist horn arm-screw pull-out (floor 3, lever 7)**

## Geometry changes that pass (what-if below, lowest SF 3.53)
1. **T 5 → 8** (floor 3 → 6). The gripper SG90 plane, and with it the jaw, moves 3 mm in +Y. JAW_TOP follows T
   automatically; re-run the assembly check.
2. **Clamp the plate to the wrist horn with the horn's centre screw:** pass `screw_access_d=2.4` to
   `horn_pocket_cutter` and fit an M2×12 screw with a DIN 9021 Ø6 washer on the front face, keeping the arm screw.
   Joint SF 0.71 → 4.9.

## Proof test to put in §8 once changed (the best verdict will still be NEEDS_TEST)
The spec's 10 N tip squeeze loads the jaw root about the same as the worst service grip (10.7 N at the root), so it
proves nothing extra. Replace it with: **squeeze 16 N (1.5 x) between the jaws at their root end (x 55–60), and 5 N at
the tips, 1 min each; then, with the wrist horn clamped in a vice, push 7.5 N sideways (out of plane) at the fixed-jaw
tip for 1 min each way. Pass: no cracks at the jaw root, the pocket or the SG90 pilots, no lift off the horn, no
permanent set.**

### Script output: what-if / stability

```
WHAT-IF  T 5->8 (floor 3->6) and the wrist horn clamped by its centre screw (access hole 6.5 -> 2.4, M2x12 + DIN 9021 OD6 washer):
  yaw: clamped wrist horn joint            SF  4.93 OK
  yaw: out-of-plane bending x10 (Kt 2)     SF  3.53 OK
  yaw: out-of-plane bending row1 (Kt 2)    SF  4.27 OK
  yaw: gripper SG90 tab screw pull-out     SF 10.86 OK
  hand: clamped wrist horn joint           SF  9.56 OK
  hand: out-of-plane bending x10 (Kt 2)    SF  6.74 OK
  hand: out-of-plane bending row1 (Kt 2)   SF  8.33 OK
  hand: gripper SG90 tab screw pull-out    SF 21.17 OK
  what-if lowest SF 3.53
```

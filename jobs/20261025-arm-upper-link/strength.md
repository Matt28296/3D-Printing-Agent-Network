VERDICT: FAIL

# Strength check: 20261025-arm-upper-link

strength-analyst · 2026-10-26 · calculations in `strength_calc.py` (plain python3; section properties cross-checked against build123d sections of `design()`)

The spec's in-plane cases all pass: SF ≥ 8.9 on slot bearing, 9.2 at the elbow window, 13 at the lightening slot,
and 29.7 or more on the elbow pilots. The 6 mm plate fails under **out-of-plane** loads, which the spec omits. So do the
lightening slot (out-of-plane bending and torsion) and the **shoulder-horn joint** (two M2 screws in a 4 mm floor).
Lowest SF 0.58. **The 5 N hand push alone also fails** (SF 1.01 at the slot), so the verdict doesn't depend on the
yaw-stall case.

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
| Shoulder stall through the horn slot | 1000 N·mm | slot walls (bearing); in-plane bending | short-term | spec |
| Elbow MG996R stall reaction | 1000 N·mm | tab screws into the plate | short-term | spec |
| Weight beyond the horn x2, in plane | 674 N·mm (static 337) | in-plane bending | sustained | spec: 310 static / 620 |
| Weight beyond the horn x2, out of plane | 86 N·mm (static 43) | horn screws, plate | sustained | **added** |
| Base-yaw stall sweep | at the horn: torsion 1607, transverse 1834 N·mm | horn screws, plate, Elbow MG996R screws | short-term | **added** |
| Hand push 5 N sideways at the fingertip | at the horn: torsion 925, transverse 1425 N·mm | same | short-term | **added** |

Build direction: printed flat, back face (horn pocket) on the bed. In-plane and out-of-plane bending of the plate run
along the layers. Horn-screw and tab-screw pull-out, and plate torsion (conservatively), shear the layers.

## Assumptions

- Plate sections (over the pocket at x 15, lightening slot, screw rows, window) are computed from the parameters and
  match the CAD sections (out-of-plane I 549 / 360 / 523 / 250 mm⁴).
- In-plane bending is bounded by the stall of the horn servo: 1000 N·mm at any section beyond the horn, or the
  proportional share at the far window.
- Slot torsion: the two rails are treated as separate open sections (St Venant). Rails tied at both ends act partly
  as a frame, so this is conservative. A frame model gives SF of about 1.5, which still fails.
- **Advisory rows**: the window rails carrying the out-of-plane moment alone, with the servo case ignored. The servo
  case is about 40 x stiffer than the rails and is bolted across the window at both tab rows, so the load enters and
  leaves through the tab screws (checked in the verdict rows). The rails-alone stress shows why those screws must stay
  tight. It is not used for the verdict.
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
| 1 | shoulder stall 1000 N.mm: horn-slot wall bearing | XY | 2.82 | 25.00 | 8.88 | 3 | OK |
| 2 | stall 1000 N.mm: in-plane bending at lightening slot (Kt 2) | XY | 1.86 | 25.00 | 13.44 | 3 | OK |
| 3 | stall: in-plane bending at the elbow MG996R window, M 1000 (Kt 2.5) | XY | 2.73 | 25.00 | 9.17 | 3 | OK |
| 4 | weight x2 (sustained): in-plane bending at slot (Kt 2) | XY | 1.25 | 25.00 | 19.92 | 4 | OK |
| 5 | elbow MG996R stall: tab-pilot bearing | XY | 0.78 | 25.00 | 32.14 | 3 | OK |
| 6 | elbow MG996R stall: pilot-to-window ligament 2.40 tear-out (full F toward window) | XY shear | 0.42 | 12.50 | 29.66 | 3 | OK |
| 7 | weight x2 (sustained): horn arm-screw pull-out (floor 4, torsion lever 5.5) | Z shear | 0.39 | 6.25 | 16.14 | 4 | OK |
| 8 | yaw-stall sweep: horn arm-screw pull-out (floor 4) | Z shear | 8.23 | 6.25 | 0.76 | 3 | **FAIL** |
| 9 | hand push 5 N: horn arm-screw pull-out (floor 4) | Z shear | 5.18 | 6.25 | 1.21 | 3 | **FAIL** |
| 10 | weight x2 (sustained): out-of-plane bending x15 over the pocket (Kt 2 arm-screw hole) | XY | 0.98 | 25.00 | 25.52 | 4 | OK |
| 11 | weight x2 (sustained): out-of-plane bending at the lightening slot x26 (Kt 2) | XY | 1.43 | 25.00 | 17.52 | 4 | OK |
| 12 | weight x2 (sustained): out-of-plane bending at the elbow MG996R screw row x65.6 (Kt 2) | XY | 0.98 | 25.00 | 25.45 | 4 | OK |
| 13 | yaw-stall sweep: out-of-plane bending x15 over the pocket (Kt 2 arm-screw hole) | XY | 19.72 | 25.00 | 1.27 | 3 | **FAIL** |
| 14 | yaw-stall sweep: out-of-plane bending at the lightening slot x26 (Kt 2) | XY | 27.38 | 25.00 | 0.91 | 3 | **FAIL** |
| 15 | yaw-stall sweep: out-of-plane bending at the elbow MG996R screw row x65.6 (Kt 2) | XY | 15.63 | 25.00 | 1.60 | 3 | **FAIL** |
| 16 | yaw-stall sweep: plate torsion at the slot (2 rails, Z shear) | Z shear | 10.76 | 6.25 | 0.58 | 3 | **FAIL** |
| 17 | yaw-stall sweep: elbow MG996R tab screws pull-out | Z shear | 1.21 | 6.25 | 5.16 | 3 | OK |
| 18 | hand push 5 N: out-of-plane bending x15 over the pocket (Kt 2 arm-screw hole) | XY | 15.45 | 25.00 | 1.62 | 3 | **FAIL** |
| 19 | hand push 5 N: out-of-plane bending at the lightening slot x26 (Kt 2) | XY | 21.58 | 25.00 | 1.16 | 3 | **FAIL** |
| 20 | hand push 5 N: out-of-plane bending at the elbow MG996R screw row x65.6 (Kt 2) | XY | 12.59 | 25.00 | 1.99 | 3 | **FAIL** |
| 21 | hand push 5 N: plate torsion at the slot (2 rails, Z shear) | Z shear | 6.20 | 6.25 | 1.01 | 3 | **FAIL** |
| 22 | hand push 5 N: elbow MG996R tab screws pull-out | Z shear | 0.66 | 6.25 | 9.41 | 3 | OK |

Advisory rows (not in the verdict, reason under Assumptions):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| yaw-stall sweep: elbow MG996R window rails alone, servo case ignored (Kt 2.5) | XY | 40.85 | 25.00 | 0.61 | 3 |
| hand push 5 N: elbow MG996R window rails alone, servo case ignored (Kt 2.5) | XY | 32.88 | 25.00 | 0.76 | 3 |

**lowest SF 0.58 (required 3) at: yaw-stall sweep: plate torsion at the slot (2 rails, Z shear)**

## Geometry changes that pass (what-if B below, lowest SF 3.59)
1. **T 6 → 10.** This moves the elbow servo plane 4 mm in +Y, so the assembly frames and the assembly check must be
   re-run. Option A (T 9) reaches only SF 2.94.
2. **Remove the lightening slot** (LIGHT): it halves the out-of-plane stiffness and the torsion constant.
3. **Clamp the link to the shoulder horn with the horn's centre screw:** pass `screw_access_d=3.4` to
   `horn_pocket_cutter` and fit an M3×12–14 screw with a DIN 9021 Ø9 washer on the front face, keeping the arm screws.
   Horn joint SF 0.76 → 5.8.
The link grows from about 27 g to about 50 g. With the forearm and gripper changes the static shoulder moment rises
from 337 to about 410 N·mm (x2 dynamic ≈ 820, still under the 1000 N·mm stall). Front-face edge ribs could replace the
extra thickness, but they need re-checking for torsion.

## Proof test to put in §8 once changed (the best verdict will still be NEEDS_TEST)
Keep the spec's test (shoulder horn in a vice, 1 kg at the elbow axis, 1 min, deflection < 2 mm, no set). Add:
**same clamping, 21 N (≈2.1 kg) sideways (out of the link plane) at the elbow axis for 1 min each way (2100 N·mm,
1.5 x the hand-push moment at the horn), then 7.5 N sideways at the end of a 185 mm lever bolted to the elbow tab
holes (torsion ≈1390 N·mm, 1.5 x the hand-push torsion). Pass: no cracks at the pocket, no lift of the link off the
horn, no permanent set.**

### Script output: what-if / stability

```
WHAT-IF A: T 6->9, no lightening slot, centre-screw clamp:
  yaw: horn joint (clamped)                SF  5.11 OK
  yaw: x15 over pocket (Kt2)               SF  2.94 FAIL
  yaw: x26 no slot (Kt1)                   SF  6.98 OK
  yaw: torsion full width                  SF  2.98 FAIL
  yaw: elbow MG996R screw row (Kt2)        SF  3.60 OK
  yaw: elbow MG996R tab screws pull-out    SF  7.74 OK
  hand: horn joint (clamped)               SF  8.16 OK
  hand: x15 over pocket (Kt2)              SF  3.75 OK
  hand: x26 no slot (Kt1)                  SF  8.86 OK
  hand: torsion full width                 SF  5.17 OK
  hand: elbow MG996R screw row (Kt2)       SF  4.47 OK
  hand: elbow MG996R tab screws pull-out   SF 14.11 OK
  what-if lowest SF 2.94

WHAT-IF B: T 6->10, no lightening slot, centre-screw clamp:
  yaw: horn joint (clamped)                SF  5.84 OK
  yaw: x15 over pocket (Kt2)               SF  3.65 OK
  yaw: x26 no slot (Kt1)                   SF  8.62 OK
  yaw: torsion full width                  SF  3.59 OK
  yaw: elbow MG996R screw row (Kt2)        SF  4.44 OK
  yaw: elbow MG996R tab screws pull-out    SF  8.60 OK
  hand: horn joint (clamped)               SF  9.32 OK
  hand: x15 over pocket (Kt2)              SF  4.66 OK
  hand: x26 no slot (Kt1)                  SF 10.94 OK
  hand: torsion full width                 SF  6.24 OK
  hand: elbow MG996R screw row (Kt2)       SF  5.52 OK
  hand: elbow MG996R tab screws pull-out   SF 15.68 OK
  what-if lowest SF 3.59
```

VERDICT: FAIL

# Strength check: 20261025-arm-forearm

strength-analyst · 2026-10-26 · calculations in `strength_calc.py` (plain python3; section properties cross-checked against build123d sections of `design()`)

The spec's in-plane cases pass: SF ≥ 6.3. The 5 mm plate fails under **out-of-plane** loads, which the spec omits.
So do the lightening slot, the **elbow-horn joint** (two M2 screws in a 3 mm floor) and the wrist SG90 tab screws in
the yaw-stall case. Lowest SF 0.42. **The 5 N hand push alone also fails** (SF 0.84 in torsion at the slot, 0.89 in
bending there).

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
| Elbow stall through the horn slot | 1000 N·mm | slot walls (bearing); in-plane bending | short-term | spec |
| Wrist SG90 stall reaction | 160 N·mm | tab screws into the plate | short-term | spec |
| Weight beyond the horn x2, in plane | 312 N·mm (static 156) | in-plane bending | sustained | spec: 140 static / 280 |
| Weight beyond the horn x2, out of plane | 42 N·mm (static 21) | horn screws, plate | sustained | **added** |
| Base-yaw stall sweep | at the horn: torsion 960, transverse 1479 N·mm | horn screws, plate, Wrist SG90 screws | short-term | **added** |
| Hand push 5 N sideways at the fingertip | at the horn: torsion 475, transverse 925 N·mm | same | short-term | **added** |

Build direction: printed flat, back face (horn pocket) on the bed. In-plane and out-of-plane bending of the plate run
along the layers. Horn-screw and tab-screw pull-out, and plate torsion (conservatively), shear the layers.

## Assumptions

- Plate sections (over the pocket at x 15, lightening slot, screw rows, window) are computed from the parameters and
  match the CAD sections (out-of-plane I 232 / 146 / 252 / 142 mm⁴).
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
- Wrist SG90 pilots are slotted Ø1.8. The pilot-to-window ligament is 1.55 mm (not the ~1.2 mm a first estimate
  gives). An axial push of 2 x the gripper weight plus 1 N is checked on it.

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
| 1 | elbow stall 1000 N.mm: horn-slot wall bearing | XY | 2.82 | 25.00 | 8.88 | 3 | OK |
| 2 | stall 1000 N.mm: in-plane bending at lightening slot (Kt 2) | XY | 3.94 | 25.00 | 6.35 | 3 | OK |
| 3 | stall: in-plane bending at the wrist SG90 window, M 604 (Kt 2.5) | XY | 3.01 | 25.00 | 8.31 | 3 | OK |
| 4 | weight x2 (sustained): in-plane bending at slot (Kt 2) | XY | 1.23 | 25.00 | 20.35 | 4 | OK |
| 5 | wrist SG90 stall: tab-pilot bearing | XY | 0.77 | 25.00 | 32.41 | 3 | OK |
| 6 | wrist SG90 stall: pilot-to-window ligament 1.55 tear-out (full F toward window) | XY shear | 0.45 | 12.50 | 27.91 | 3 | OK |
| 7 | weight x2 (sustained): horn arm-screw pull-out (floor 3, torsion lever 5.5) | Z shear | 0.25 | 6.25 | 24.88 | 4 | OK |
| 8 | yaw-stall sweep: horn arm-screw pull-out (floor 3) | Z shear | 7.90 | 6.25 | 0.79 | 3 | **FAIL** |
| 9 | hand push 5 N: horn arm-screw pull-out (floor 3) | Z shear | 3.94 | 6.25 | 1.59 | 3 | **FAIL** |
| 10 | weight x2 (sustained): out-of-plane bending x15 over the pocket (Kt 2 arm-screw hole) | XY | 0.96 | 25.00 | 26.05 | 4 | OK |
| 11 | weight x2 (sustained): out-of-plane bending at the lightening slot x22 (Kt 2) | XY | 1.43 | 25.00 | 17.50 | 4 | OK |
| 12 | weight x2 (sustained): out-of-plane bending at the wrist SG90 screw row x70.8 (Kt 2) | XY | 0.83 | 25.00 | 30.22 | 4 | OK |
| 13 | yaw-stall sweep: out-of-plane bending x15 over the pocket (Kt 2 arm-screw hole) | XY | 31.42 | 25.00 | 0.80 | 3 | **FAIL** |
| 14 | yaw-stall sweep: out-of-plane bending at the lightening slot x22 (Kt 2) | XY | 44.91 | 25.00 | 0.56 | 3 | **FAIL** |
| 15 | yaw-stall sweep: out-of-plane bending at the wrist SG90 screw row x70.8 (Kt 2) | XY | 18.61 | 25.00 | 1.34 | 3 | **FAIL** |
| 16 | yaw-stall sweep: plate torsion at the slot (2 rails, Z shear) | Z shear | 14.96 | 6.25 | 0.42 | 3 | **FAIL** |
| 17 | yaw-stall sweep: wrist SG90 tab screws pull-out | Z shear | 3.24 | 6.25 | 1.93 | 3 | **FAIL** |
| 18 | hand push 5 N: out-of-plane bending x15 over the pocket (Kt 2 arm-screw hole) | XY | 19.58 | 25.00 | 1.28 | 3 | **FAIL** |
| 19 | hand push 5 N: out-of-plane bending at the lightening slot x22 (Kt 2) | XY | 27.94 | 25.00 | 0.89 | 3 | **FAIL** |
| 20 | hand push 5 N: out-of-plane bending at the wrist SG90 screw row x70.8 (Kt 2) | XY | 11.34 | 25.00 | 2.20 | 3 | **FAIL** |
| 21 | hand push 5 N: plate torsion at the slot (2 rails, Z shear) | Z shear | 7.40 | 6.25 | 0.84 | 3 | **FAIL** |
| 22 | hand push 5 N: wrist SG90 tab screws pull-out | Z shear | 1.52 | 6.25 | 4.10 | 3 | OK |
| 23 | gripper weight x2 + 1 N handling along x: SG90 pilot ligament 1.55 tear-out | XY shear | 0.17 | 12.50 | 72.01 | 3 | OK |

Advisory rows (not in the verdict, reason under Assumptions):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| yaw-stall sweep: wrist SG90 window rails alone, servo case ignored (Kt 2.5) | XY | 41.36 | 25.00 | 0.60 | 3 |
| hand push 5 N: wrist SG90 window rails alone, servo case ignored (Kt 2.5) | XY | 25.20 | 25.00 | 0.99 | 3 |

**lowest SF 0.42 (required 3) at: yaw-stall sweep: plate torsion at the slot (2 rails, Z shear)**

## Geometry changes that pass (what-if B below, lowest SF 3.39)
1. **T 5 → 10.** This moves the wrist SG90 plane 5 mm in +Y; re-run the assembly check. Option A (T 8) reaches only
   SF 2.12.
2. **Remove the lightening slot** (LIGHT).
3. **Clamp the forearm to the elbow horn with the horn's centre screw:** pass `screw_access_d=3.4` and fit an M3×12–14
   screw with a Ø9 washer. Horn joint SF 0.79 → 8.2.
The forearm grows from about 15 g to about 38 g (already included in the upper-link note).

## Proof test to put in §8 once changed (the best verdict will still be NEEDS_TEST)
Keep the spec's test (clamp at the elbow horn, 1 kg at the wrist axis, 1 min, no cracks, no set). Add: **same
clamping, 15 N sideways (out of plane) at the wrist axis for 1 min each way (≈1390 N·mm, 1.5 x the hand-push moment),
then 7.5 N sideways at the end of a 95 mm lever on the wrist tab holes (torsion ≈710 N·mm). Pass: no cracks at the
pocket or the SG90 pilots, no lift off the horn, no permanent set.**

### Script output: what-if / stability

```
WHAT-IF A: T 5->8, no lightening slot, centre-screw clamp:
  yaw: horn joint (clamped)                SF  6.13 OK
  yaw: x15 over pocket (Kt2)               SF  2.12 FAIL
  yaw: x22 no slot (Kt1)                   SF  5.29 OK
  yaw: torsion full width                  SF  2.91 FAIL
  yaw: wrist SG90 screw row (Kt2)          SF  3.44 OK
  yaw: wrist SG90 tab screws pull-out      SF  3.09 OK
  hand: horn joint (clamped)               SF 12.30 OK
  hand: x15 over pocket (Kt2)              SF  3.40 OK
  hand: x22 no slot (Kt1)                  SF  8.51 OK
  hand: torsion full width                 SF  5.88 OK
  hand: wrist SG90 screw row (Kt2)         SF  5.64 OK
  hand: wrist SG90 tab screws pull-out     SF  6.56 OK
  what-if lowest SF 2.12

WHAT-IF B: T 5->10, no lightening slot, centre-screw clamp:
  yaw: horn joint (clamped)                SF  8.17 OK
  yaw: x15 over pocket (Kt2)               SF  3.39 OK
  yaw: x22 no slot (Kt1)                   SF  8.27 OK
  yaw: torsion full width                  SF  4.27 OK
  yaw: wrist SG90 screw row (Kt2)          SF  5.37 OK
  yaw: wrist SG90 tab screws pull-out      SF  3.86 OK
  hand: horn joint (clamped)               SF 16.40 OK
  hand: x15 over pocket (Kt2)              SF  5.45 OK
  hand: x22 no slot (Kt1)                  SF 13.29 OK
  hand: torsion full width                 SF  8.64 OK
  hand: wrist SG90 screw row (Kt2)         SF  8.82 OK
  hand: wrist SG90 tab screws pull-out     SF  8.20 OK
  what-if lowest SF 3.39
```

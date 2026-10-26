VERDICT: FAIL

# Strength check: 20261025-arm-turntable

strength-analyst · 2026-10-26 · calculations in `strength_calc.py` (plain python3; section properties cross-checked against build123d sections of `design()`)

The spec's in-plane stall cases all pass with large margins. The part fails on two kinds of load that aren't in
the spec. The **base-horn joint** (the disk is held on the horn by two M2 screws in a 3 mm floor) fails even under
the spec's own shoulder stall when the fingertip presses on the desk (SF 2.66). The **out-of-plane loads** overload
the upright at its lower tab-pilot row and window corner, and the disk in front of the upright. Lowest SF 0.42.
The design brief also needs correcting: shoulder torque bends the upright in its own plane, but the resulting stress
runs along Z, which is **across** the layers, not along them as the brief says (SF ≥ 13 there, so harmless).

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
| Base-servo stall | 1000 N·mm about Z | horn-slot walls (bearing); upright torsion | short-term | spec |
| Shoulder-servo stall | 1000 N·mm about Y | 4 horizontal tab pilots; upright in-plane bending | short-term | spec |
| Shoulder stall with the fingertip on the desk (91 mm) | 1152 N·mm about Y | through the base-horn arm screws and the upright | short-term | **added** |
| Arm weight out of the upright plane x2 | 196 N·mm at the root (98 static) | upright, disk, base horn | sustained | spec: 120 assumed |
| Arm weight about the yaw axis x2 | 716 N·mm | base-horn arm screws | sustained | **added** |
| Base-yaw stall sweep | M_x up to 1920 (root) / 1957 (disk), M_y up to 1511, M_z 1000 N·mm | upright, disk, base horn | short-term | **added** |
| Hand push 5 N sideways, arm vertical | M_x up to 1630 (root) / 1655 (disk) N·mm | upright, disk, base horn | short-term | **added** |
| Spec proof test (1 kg at the elbow) | 1439 N·mm about Y at the base horn | base horn | test | spec §8 (advisory row) |

Build direction: the disk prints on the bed and the upright stands vertical. All upright bending, in-plane and out of
plane, puts stress along Z, across the layers. Upright torsion shears the layers. Disk bending runs along them.

## Assumptions

- Upright sections (root Z 19.6, window bottom Z 51, lower tab-pilot row Z 56) are computed from the parameters and
  match the CAD sections exactly (I_xx 60937 / 4530 / 2254 mm⁴).
- The shoulder servo passes M_x to the upright as a couple between the tab screws and the opposite tab edge
  (lever 14.85). At Z 56 that leaves 0.97 of the moment for front-face tension and 0.64 for gusset-toe tension.
- Disk: everything that supports the upright under forward tipping (hub, screws, ring) lies in front of its front
  face, so the full M_x crosses the disk there. b_eff = 66 (the upright width), sharp corner, Kt 2.5.
- Base-horn screws: transverse moment on one screw at lever 32.5, plus torsion on two screws at the hub radius 5.5.
  The ring (1.5 mm gap) is not counted: the screws would have to lift about 0.2 mm (across the arms) or about 1.8 mm
  (along the arms) before the ring takes load.
- Advisory row: the spec's proof test loads the base-horn screws to SF 2.1 on the placeholder allowable. The test may
  strip them before it proves anything about the upright.
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
| 1 | base stall 1000 N.mm: horn-slot wall bearing | XY | 2.82 | 25.00 | 8.88 | 3 | OK |
| 2 | yaw stall: upright torsion at root (open section) | Z shear | 1.32 | 6.25 | 4.74 | 3 | OK |
| 3 | yaw stall: window ligament pair, Z51 toe | Z | 0.80 | 12.50 | 15.57 | 3 | OK |
| 4 | shoulder stall on desk: upright in-plane bending, root (Kt 2.5) | Z | 0.28 | 12.50 | 45.10 | 3 | OK |
| 5 | shoulder stall on desk: upright in-plane bending, window Z60.5 (Kt 2.5) | Z | 0.72 | 12.50 | 17.24 | 3 | OK |
| 6 | yaw sweep: upright in-plane bending, root (Kt 2.5) | Z | 0.35 | 12.50 | 35.72 | 3 | OK |
| 7 | yaw sweep: upright in-plane bending, window Z60.5 (Kt 2.5) | Z | 0.92 | 12.50 | 13.66 | 3 | OK |
| 8 | weight x2 (sustained): upright root, front face (Kt 2.5) | Z | 0.08 | 12.50 | 158.19 | 4 | OK |
| 9 | weight x2 (sustained): upright root, gusset toe (Kt 2.5) | Z | 0.20 | 12.50 | 62.08 | 4 | OK |
| 10 | weight x2 (sustained): Z51 window bottom, front face (Kt 2.5) | Z | 0.56 | 12.50 | 22.15 | 4 | OK |
| 11 | weight x2 (sustained): Z51 window bottom, gusset toe | Z | 0.40 | 12.50 | 31.61 | 4 | OK |
| 12 | weight x2 (sustained): Z56 lower tab-pilot row, front face (Kt 2 hole) | Z | 0.74 | 12.50 | 16.85 | 4 | OK |
| 13 | weight x2 (sustained): Z56 lower tab-pilot row, gusset toe | Z | 0.40 | 12.50 | 31.37 | 4 | OK |
| 14 | weight x2 (sustained): shoulder tab screws pull-out (2 screws, L 5) | Z shear | 0.14 | 6.25 | 43.37 | 4 | OK |
| 15 | weight x2 (sustained): disk at upright front face, b 66 (Kt 2.5) | XY | 1.08 | 25.00 | 23.25 | 4 | OK |
| 16 | yaw-stall sweep: upright root, front face (Kt 2.5) | Z | 1.13 | 12.50 | 11.11 | 3 | OK |
| 17 | yaw-stall sweep: upright root, gusset toe (Kt 2.5) | Z | 2.33 | 12.50 | 5.37 | 3 | OK |
| 18 | yaw-stall sweep: Z51 window bottom, front face (Kt 2.5) | Z | 5.46 | 12.50 | 2.29 | 3 | **FAIL** |
| 19 | yaw-stall sweep: Z51 window bottom, gusset toe | Z | 3.83 | 12.50 | 3.27 | 3 | OK |
| 20 | yaw-stall sweep: Z56 lower tab-pilot row, front face (Kt 2 hole) | Z | 7.20 | 12.50 | 1.74 | 3 | **FAIL** |
| 21 | yaw-stall sweep: Z56 lower tab-pilot row, gusset toe | Z | 3.85 | 12.50 | 3.24 | 3 | OK |
| 22 | yaw-stall sweep: shoulder tab screws pull-out (2 screws, L 5) | Z shear | 1.39 | 6.25 | 4.48 | 3 | OK |
| 23 | yaw-stall sweep: disk at upright front face, b 66 (Kt 2.5) | XY | 17.79 | 25.00 | 1.41 | 3 | **FAIL** |
| 24 | hand push 5 N: upright root, front face (Kt 2.5) | Z | 0.66 | 12.50 | 18.99 | 3 | OK |
| 25 | hand push 5 N: upright root, gusset toe (Kt 2.5) | Z | 1.68 | 12.50 | 7.45 | 3 | OK |
| 26 | hand push 5 N: Z51 window bottom, front face (Kt 2.5) | Z | 4.76 | 12.50 | 2.63 | 3 | **FAIL** |
| 27 | hand push 5 N: Z51 window bottom, gusset toe | Z | 3.33 | 12.50 | 3.75 | 3 | OK |
| 28 | hand push 5 N: Z56 lower tab-pilot row, front face (Kt 2 hole) | Z | 6.30 | 12.50 | 1.98 | 3 | **FAIL** |
| 29 | hand push 5 N: Z56 lower tab-pilot row, gusset toe | Z | 3.36 | 12.50 | 3.72 | 3 | OK |
| 30 | hand push 5 N: shoulder tab screws pull-out (2 screws, L 5) | Z shear | 1.21 | 6.25 | 5.15 | 3 | OK |
| 31 | hand push 5 N: disk at upright front face, b 66 (Kt 2.5) | XY | 15.05 | 25.00 | 1.66 | 3 | **FAIL** |
| 32 | shoulder stall: tab-pilot bearing (compression) | XY | 0.93 | 25.00 | 26.78 | 3 | OK |
| 33 | shoulder stall: pilot-to-window ligament tear-out | Z shear | 0.51 | 6.25 | 12.36 | 3 | OK |
| 34 | weight x2 (sustained): base-horn arm screw pull-out (floor 3) | Z shear | 2.18 | 6.25 | 2.87 | 4 | **FAIL** |
| 35 | shoulder stall on desk: base-horn arm screw pull-out (floor 3) | Z shear | 2.35 | 6.25 | 2.66 | 3 | **FAIL** |
| 36 | yaw-stall sweep: base-horn arm screw pull-out (floor 3) | Z shear | 14.88 | 6.25 | 0.42 | 3 | **FAIL** |
| 37 | hand push 5 N: base-horn arm screw pull-out (floor 3) | Z shear | 9.98 | 6.25 | 0.63 | 3 | **FAIL** |

Advisory rows (not in the verdict, reason under Assumptions):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| proof test (1 kg at elbow): base-horn arm screw | Z shear | 2.94 | 6.25 | 2.13 | 1 |

**lowest SF 0.42 (required 3) at: yaw-stall sweep: base-horn arm screw pull-out (floor 3)**

## Geometry changes that pass (what-if below, lowest SF 3.24)
1. **DISK_T 5 → 8** (floor over the base horn 3 → 6 mm; disk bending SF 1.41 → 3.60). The shoulder axis stays at Z 60.5.
2. **UP_T 5 → 7** (grows toward −Y; the tab plane UP_Y = −5 is unchanged) and **GUSSET_H 50 → 70**: lower tab-pilot row
   SF 1.74 → 5.13, window corner 2.29 → 5.38. The gussets stay at |X| ≥ 28.5, clear of the servo body (|X| ≤ 20.4).
3. **Clamp the disk to the base horn with the horn's own centre screw:** pass `screw_access_d=3.4` to
   `horn_pocket_cutter` and fit an M3×12 screw with a DIN 9021 Ø9 washer on the disk top, keeping the two arm screws.
   Base-horn joint SF 0.42 → 3.24. Fit this screw before the shoulder servo, which sits over it.
   DISK_T must be 8: at 7 the 5 mm floor brings the clamped joint down to about SF 2.7.

## Proof test to put in §8 once changed (the best verdict will still be NEEDS_TEST)
Keep the 1 kg-at-the-elbow test (in-plane), and add: **arm assembled and pointing straight up, servos unpowered.
Push 10 N (≈1 kg on a luggage scale) sideways (±Y) at the fingertip, 1 min each way, then repeat with the elbow at
90°. Pass: no cracks or whitening at the upright window corners, the tab pilots, the gusset toes or the upright–disk
corner; the base horn doesn't lift off; the fingertip returns to within 1 mm (no permanent lean).** 10 N is 2 x the
hand push and 1.2 x the largest out-of-plane yaw-stall force.

### Script output: what-if / stability

```
WHAT-IF  DISK_T 5->8, UP_T 5->7, GUSSET_H 50->70, base horn clamped by its centre screw (access hole 6.5 -> 3.4, M3x12 + OD9 washer):
  yaw: root front (Kt2.5)                            SF 13.42 (req 3) OK
  yaw: root toe (Kt2.5)                              SF  6.11 (req 3) OK
  yaw: Z51 front (Kt2.5)                             SF  5.38 (req 3) OK
  yaw: Z51 toe                                       SF  7.76 (req 3) OK
  yaw: Z56 front (Kt2)                               SF  5.13 (req 3) OK
  yaw: disk at upright (Kt2.5)                       SF  3.60 (req 3) OK
  yaw: clamped base-horn joint                       SF  3.24 (req 3) OK
  hand: root front (Kt2.5)                           SF 23.26 (req 3) OK
  hand: root toe (Kt2.5)                             SF  8.41 (req 3) OK
  hand: Z51 front (Kt2.5)                            SF  6.17 (req 3) OK
  hand: Z51 toe                                      SF  8.91 (req 3) OK
  hand: Z56 front (Kt2)                              SF  5.87 (req 3) OK
  hand: disk at upright (Kt2.5)                      SF  4.25 (req 3) OK
  hand: clamped base-horn joint                      SF  4.78 (req 3) OK
  shoulder stall on desk: clamped base-horn joint    SF 21.43 (req 3) OK
  weight x2 (sustained): clamped base-horn joint     SF 22.73 (req 4) OK
  what-if lowest SF 3.24
```

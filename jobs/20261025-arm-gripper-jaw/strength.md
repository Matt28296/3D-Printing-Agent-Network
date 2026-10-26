VERDICT: FAIL

# Strength check: 20261025-arm-gripper-jaw

strength-analyst · 2026-10-26 · calculations in `strength_calc.py` (plain python3; section properties cross-checked against build123d sections of `design()`)

In-plane grip bending of the bar passes (SF ≥ 7.5). The 5 mm × 11.5 mm bar fails in **out-of-plane bending over the
horn pocket** at x 8, and the **gripper-horn joint** (one M2 screw in a 3 mm floor) fails as well. Lowest SF 0.91.
**The 5 N hand push alone also fails** (SF 1.50 / 2.40).

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
| Gripper stall | 160 N·mm | pocket walls; bar in-plane bending (2.9 N at the tip or 10.7 N at r 15) | short-term | spec (+ grip at the root) |
| Base-yaw stall sweep, fingertip on the jaw | transverse up to 453 N·mm at the gripper horn | horn screw, bar | short-term | **added** |
| Hand push 5 N sideways at the jaw tip | 275 N·mm at the gripper horn | horn screw, bar | short-term | **added** |
| Spec proof squeeze, 10 N at the tip | 470 N·mm in plane at x 8 | bar | test | spec §8 (advisory row) |

Build direction: printed flat, pocket side on the bed. Bar bending in either plane runs along the layers. Horn-screw
pull-out shears them.

## Assumptions

- The jaw's out-of-plane load is the fingertip force applied at its tip (55 mm). Its in-plane component is taken by
  the pocket walls, and the gripper servo backdrives above 160 N·mm.
- Sections at x 8 (82 mm⁴, pocket + bar) and x 16.5 (120 mm⁴) match the CAD. Kt 2 at x 8 for the drilled arm-screw
  hole, 1.5 at the rounded pocket tip.
- Advisory: the spec's 10 N tip squeeze is 3.4 x the stall grip at the tip, and gives SF 2.2 on the allowable in the
  bar. It is acceptable as a test, but more than a proof test needs.
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
| 1 | gripper stall 160 N.mm: horn-pocket wall bearing | XY | 1.42 | 25.00 | 17.63 | 3 | OK |
| 2 | gripper stall: bar in-plane bending x8 over the pocket (Kt 2.5) | XY | 3.33 | 25.00 | 7.50 | 3 | OK |
| 3 | gripper stall: bar in-plane bending x16.5 pocket tip (Kt 1.5) | XY | 1.53 | 25.00 | 16.33 | 3 | OK |
| 4 | grip reaction 2.9 N at the tip (in-plane, carried by the pocket walls) | XY | 1.42 | 25.00 | 17.63 | 3 | OK |
| 5 | yaw-stall sweep: gripper horn arm-screw pull-out (floor 3, lever 7) | Z shear | 4.30 | 6.25 | 1.45 | 3 | **FAIL** |
| 6 | yaw-stall sweep: out-of-plane bending x8 over the pocket (Kt 2 arm-screw hole) | XY | 27.41 | 25.00 | 0.91 | 3 | **FAIL** |
| 7 | yaw-stall sweep: out-of-plane bending x16.5 at the pocket tip (Kt 1.5) | XY | 9.95 | 25.00 | 2.51 | 3 | **FAIL** |
| 8 | hand push 5 N: gripper horn arm-screw pull-out (floor 3, lever 7) | Z shear | 2.61 | 6.25 | 2.40 | 3 | **FAIL** |
| 9 | hand push 5 N: out-of-plane bending x8 over the pocket (Kt 2 arm-screw hole) | XY | 16.63 | 25.00 | 1.50 | 3 | **FAIL** |
| 10 | hand push 5 N: out-of-plane bending x16.5 at the pocket tip (Kt 1.5) | XY | 6.03 | 25.00 | 4.15 | 3 | OK |

Advisory rows (not in the verdict, reason under Assumptions):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| 10 N proof squeeze at the tip: bar in-plane bending x8 (Kt 2.5) | XY | 11.45 | 25.00 | 2.18 | 2 |

**lowest SF 0.91 (required 3) at: yaw-stall sweep: out-of-plane bending x8 over the pocket (Kt 2 arm-screw hole)**

## Geometry changes that pass (what-if below, lowest SF 3.50)
1. **T 5 → 8** (floor 3 → 6). The jaw's band moves to z 14.4–22.4 in the gripper frame, so the gripper base's
   JAW_TOP must follow (it currently hard-codes the 5 mm jaw). Re-run the assembly check.
2. **BAR_Y1 5.5 → 8.0** (bar 11.5 → 14 wide, matching the hub radius; it opens toward +y, away from the fixed jaw).
3. **Clamp the jaw to the gripper horn with the horn's centre screw:** pass `screw_access_d=2.4` and fit an M2×12 screw
   with a Ø6 washer, keeping the arm screw. Joint SF 1.45 → 10.

## Proof test to put in §8 once changed (the best verdict will still be NEEDS_TEST)
Covered by the gripper-base test (16 N at the jaw root, 5 N at the tips), plus: **with the gripper horn held, push 7.5 N
sideways (out of plane) at the jaw tip for 1 min each way. Pass: no crack over the pocket, no lift off the horn, no
permanent set; the jaw then opens 0–60° without rubbing.**

### Script output: what-if / stability

```
WHAT-IF  T 5->8 (floor 3->6), BAR_Y1 5.5->8.0 (bar 11.5->14 wide, matches the hub r 8) and the horn clamped by its centre screw (access hole 6.5 -> 2.4, M2x12 + OD6 washer):
  yaw: clamped gripper horn joint          SF 10.02 OK
  yaw: out-of-plane bending x8             SF  3.50 OK
  yaw: out-of-plane bending x16            SF  7.83 OK
  hand: clamped gripper horn joint         SF 16.52 OK
  hand: out-of-plane bending x8            SF  5.77 OK
  hand: out-of-plane bending x16           SF 12.93 OK
  what-if lowest SF 3.50
```

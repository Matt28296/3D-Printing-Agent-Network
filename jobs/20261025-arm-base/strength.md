VERDICT: NEEDS_TEST

# Strength check: 20261025-arm-base

strength-analyst · 2026-10-26 · calculations in `strength_calc.py` (plain python3; section properties cross-checked against build123d sections of `design()`)

Every check is at SF 4.0 or above. Because the allowables are placeholders, NEEDS_TEST is the best verdict possible.
Two findings are outside the stress checks: **the robot tips over unless the base is screwed down** (see Stability),
and the cradle screws as specified (M3×8) only engage 2 mm.

## Load cases

**Mass model (re-derived, not taken from the spec).** Printed parts = geometry.json volume x 1.27 g/cm³ (upper
link 27.0 g, forearm 15.3 g, gripper base 19.9 g, jaw 4.3 g, turntable 77.0 g), CG from the build123d centre of mass of
`design()`; MG996R 55 g, SG90 9 g (hobby_parts.py); horn + screws 4 g (MG996R) / 1.5 g (SG90); 10 g cable allowance;
50 g payload at the fingertip. Arm straight and horizontal, static moments: about the yaw axis 358 N·mm, shoulder
337 (spec 310), elbow 156 (spec 140), wrist 63, gripper 28. Because the arm steps forward in +Y, the weight also
puts a pose-independent **out-of-plane** moment on every joint: 43 N·mm at the shoulder horn, 21 at the elbow, 8.6
at the wrist, 98 at the upright root (the spec assumed 120). The dynamic factor is x2, as the spec uses.

| Case | Load | Applied at, direction | Duration | Source |
|---|---|---|---|---|
| Base-servo stall | 1000 N·mm about Z | 4 tab screws, in the plate's plane | short-term | spec |
| Arm weight x2 | 725 N·mm overturning (358 x2 in plane + out-of-plane) | servo tabs into the top plate | sustained/cyclic | re-derived (spec: 600) |
| 20 N on the turntable rim | 960 N·mm + 20 N down | servo, or ring onto the plate | short-term | spec |
| Shoulder stall pressing the fingertip on the desk | 1152 N·mm about a horizontal axis | servo tabs | short-term | **added** |
| Base-yaw stall into an obstacle (sweep) | up to 2655 N·mm overturning at the tab plane; ring catch 52.5 N | servo tabs / ring onto the plate | short-term | **added** |
| Hand push 5 N sideways at the fingertip (arm up) | 1728 N·mm; ring catch 44.4 N | servo tabs / ring | short-term | **added** |
| USB plug insertion | 20 N, shared by the 3 cradle bosses | boss ends, sideways | short-term | **added** (spec cradle: 5 N) |
| Jumper pull-off | 10 N down on the board | cradle screws in the bosses | short-term | **added** |

Build direction: the part prints upside down (top plate on the bed). Top-plate bending, pilot bearing and tear-out
run along the layers. Screw pull-out from the plate and bosses, and bending at the boss roots, run across them.

## Assumptions

- The overturning moment goes through the base servo to its 4 tab screws, which are pulled out of plate + boss
  (engagement taken as 7 mm: about a 10 mm tab screw minus the 2.5 mm tab). Weak axis: screws at y ±5, pivot on the
  tab edge at 9.85, so the lever is 14.85. The turntable yaws, so any moment direction can land on that axis. The ring
  is ignored on this path (conservative).
- Ring path checked separately: when the turntable rocks 1.5 mm onto the ring, R = M/(42.75 − 5.5). The plate is a
  strip cantilevered from the nearest wall (20.3 mm at the worst angle), b_eff = 2a + 2 x 13 (the ring wall spreads
  the load).
- Base-servo stall into the pilots: all torque on the screws (servo body bearing on the window ignored); plate 4 mm
  only (boss ignored). Pilot-to-window ligament 2.40 mm.
- Cradle bosses Ø7/Ø2.6 × 6 mm, sharp root (Kt 2.5). The 3 bosses share the USB insertion force.
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
| 1 | base stall 1000 N.mm: tab-pilot bearing (plate 4 only) | XY | 1.17 | 25.00 | 21.42 | 3 | OK |
| 2 | base stall: pilot-to-window ligament 2.40 tear-out | XY shear | 0.63 | 12.50 | 19.78 | 3 | OK |
| 3 | weight x2 (sustained): servo tab screws pull-out, M 725 on the 14.85 lever | Z shear | 0.43 | 6.25 | 14.64 | 4 | OK |
| 4 | shoulder stall on desk: servo tab screws pull-out, M 1152 on the 14.85 lever | Z shear | 0.68 | 6.25 | 9.21 | 3 | OK |
| 5 | 20 N on the turntable rim (spec): servo tab screws pull-out, M 960 on the 14.85 lever | Z shear | 0.57 | 6.25 | 11.06 | 3 | OK |
| 6 | yaw-stall sweep: servo tab screws pull-out, M 2655 on the 14.85 lever | Z shear | 1.56 | 6.25 | 4.00 | 3 | OK |
| 7 | hand push 5 N: servo tab screws pull-out, M 1728 on the 14.85 lever | Z shear | 1.02 | 6.25 | 6.14 | 3 | OK |
| 8 | 20 N on the rim (spec), R 20.0 N: top plate strip bending | XY | 2.29 | 25.00 | 10.94 | 3 | OK |
| 9 | 20 N on the rim (spec): ring-screw pilot tear-out at 270 deg (friction 0.3) | XY shear | 0.28 | 12.50 | 45.00 | 3 | OK |
| 10 | yaw-stall ring catch, R 52.5 N: top plate strip bending | XY | 6.00 | 25.00 | 4.16 | 3 | OK |
| 11 | yaw-stall ring catch: ring-screw pilot tear-out at 270 deg (friction 0.3) | XY shear | 0.73 | 12.50 | 17.13 | 3 | OK |
| 12 | hand-push ring catch, R 44.4 N: top plate strip bending | XY | 5.08 | 25.00 | 4.92 | 3 | OK |
| 13 | hand-push ring catch: ring-screw pilot tear-out at 270 deg (friction 0.3) | XY shear | 0.62 | 12.50 | 20.26 | 3 | OK |
| 14 | USB insertion 20 N / 3 bosses: cradle-boss root bending (Kt 2.5) | Z | 3.03 | 12.50 | 4.13 | 3 | OK |
| 15 | cradle screw M3x8 pull-out with 2 mm engagement, 10 N jumper pull / 2 | Z shear | 0.31 | 6.25 | 20.42 | 3 | OK |

**lowest SF 4.00 (required 3) at: yaw-stall sweep: servo tab screws pull-out, M 2655 on the 14.85 lever**

## Stability (not a stress check, but it matters)
With the arm straight out and the 50 g payload the robot tips over the base edge: 223 N·mm tipping against
147 N·mm restoring. The yaw-stall, hand-push and shoulder-on-desk cases all tip it as well. **The 4 desk screws are
required, not optional** (spec §1 says "or sits on rubber feet"). The uplift per screw is then only about 10 N. The
Ø3.4 holes run the full 40 mm pillar, so "M3 wood screws" must be about 50 mm long. Weighting the base is the
alternative to screwing it down.

## Notes
- Cradle screws: M3×8 through the 6 mm cradle leaves about 2 mm of thread in the 6 mm-deep boss pilot. Use **M3×12**.
- The thin ligaments (2.40 mm pilot-to-window, 1.95 mm boss wall) are fine for the loads above. Splitting while the
  servo tab screws are driven in can't be calculated, so the fit coupon or the first assembly checks it.

## Proof test (improves spec §8)
The spec's 20 N on the rim is the service load, not a proof load. Replace it with:
**With the base screwed to a board (desk screws fitted), the base servo, horn, turntable and ring assembled and the
servo unpowered, press 50 N (≈5 kg on a bathroom or luggage scale) straight down on the turntable rim, 1 min at each
of 4 positions 90° apart (over each end and each side of the base servo). Pass: no cracking or whitening at the 4
servo pilots and bosses, the 3 ring pilots or the top plate around the ring; after unloading, the rim returns to
within 0.3 mm of its height.** 50 N is 2.5 x the spec case and about 1 x the governing yaw-stall ring catch (52.5 N).
Going higher would overload the servo's output bearing, which is not the part under test. Also plug and unplug the USB
cable 5 times with the cradle fitted: no cracks at the cradle bosses.

### Script output: what-if / stability

```
STABILITY: base-side weight 2.83 N, arm 2.60 N
  arm straight out over the 52 mm edge: tipping 223 vs restoring 147 N.mm -> TIPS
  yaw case: overturning 2354 vs restoring 283 N.mm -> TIPS (desk-screw uplift if screwed down: 10.5 N per screw)
  hand case: overturning 1928 vs restoring 283 N.mm -> TIPS (desk-screw uplift if screwed down: 8.3 N per screw)
  shoulder stall pressing on the desk at 91 mm: lifts the back edge unless screwed down (1152 vs 283 N.mm)
```

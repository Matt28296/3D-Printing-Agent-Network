VERDICT: NEEDS_TEST

# Strength check: 20261025-arm-turntable-ring

strength-analyst · 2026-10-26 · calculations in `strength_calc.py` (plain python3; section properties cross-checked against build123d sections of `design()`)

The ring is only loaded when the turntable rocks 1.5 mm onto it. Every check is at SF 3.67 or above. Because the
allowables are placeholders, NEEDS_TEST is the best verdict possible.

## Load cases

The ring force comes from the turntable cases (see ../20261025-arm-turntable/strength_calc.py), re-derived from
servo stall torques and masses: R = M_x / (ring mid radius 42.75 − hub radius 5.5).

| Case | Load | Applied at, direction | Duration | Source |
|---|---|---|---|---|
| 20 N on the turntable rim | R = 20 N | ring top, down | short-term | spec |
| Base-yaw stall into an obstacle (sweep) | R = 52.5 N, friction 0.3R tangential | ring top | short-term | **added** |
| Hand push 5 N sideways at the fingertip (arm up) | R = 44.4 N | ring top | short-term | **added** |
| Tab screw clamp (assembly) | 100 N under an M3 pan head, no washer | tab | sustained | **added** |

Build direction: the ring prints as modelled (tabs on the bed). Ring-wall compression is across the layers but does
not separate them. Edgewise bending of the wall from friction puts stress across the layers. Tab bearing and
tear-out run along the layers.

## Assumptions

- Contact patch: 10 mm of arc × the 3.5 mm wall. The friction coefficient is 0.3 and acts tangentially (the turntable
  yaws), i.e. in the plane of the wall. A 26 mm wall segment (45° spread over the 13 mm height) bends edgewise.
- Friction is taken by a single tab (conservative). The tab hole is 3.4 mm with an M3 shank, edge distance 4.5 mm.
- Screw clamp: a snug hand-tightened self-tapper is taken as 100 N. A PETG ring creeps under a cranked screw, so tighten
  until snug, or fit an M3 washer (which doubles the bearing area).
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
| 1 | 20 N on the rim (spec): ring wall bearing (compression across layers), R 20.0 N | XY | 0.57 | 25.00 | 43.75 | 3 | OK |
| 2 | 20 N on the rim (spec): wall edgewise bending from friction 0.3R, 26 mm segment (Z, Kt 2.5) | Z | 0.49 | 12.50 | 25.28 | 3 | OK |
| 3 | 20 N on the rim (spec): interlayer shear in the wall from friction (Z shear) | Z shear | 0.10 | 6.25 | 63.19 | 3 | OK |
| 4 | 20 N on the rim (spec): tab bearing on the M3 shank from friction (one tab) | XY | 0.67 | 25.00 | 37.50 | 3 | OK |
| 5 | 20 N on the rim (spec): tab tear-out to its edge (e 4.5) | XY shear | 0.36 | 12.50 | 35.00 | 3 | OK |
| 6 | yaw-stall ring catch: ring wall bearing (compression across layers), R 52.5 N | XY | 1.50 | 25.00 | 16.66 | 3 | OK |
| 7 | yaw-stall ring catch: wall edgewise bending from friction 0.3R, 26 mm segment (Z, Kt 2.5) | Z | 1.30 | 12.50 | 9.62 | 3 | OK |
| 8 | yaw-stall ring catch: interlayer shear in the wall from friction (Z shear) | Z shear | 0.26 | 6.25 | 24.06 | 3 | OK |
| 9 | yaw-stall ring catch: tab bearing on the M3 shank from friction (one tab) | XY | 1.75 | 25.00 | 14.28 | 3 | OK |
| 10 | yaw-stall ring catch: tab tear-out to its edge (e 4.5) | XY shear | 0.94 | 12.50 | 13.33 | 3 | OK |
| 11 | hand-push 5 N ring catch: ring wall bearing (compression across layers), R 44.4 N | XY | 1.27 | 25.00 | 19.69 | 3 | OK |
| 12 | hand-push 5 N ring catch: wall edgewise bending from friction 0.3R, 26 mm segment (Z, Kt 2.5) | Z | 1.10 | 12.50 | 11.38 | 3 | OK |
| 13 | hand-push 5 N ring catch: interlayer shear in the wall from friction (Z shear) | Z shear | 0.22 | 6.25 | 28.45 | 3 | OK |
| 14 | hand-push 5 N ring catch: tab bearing on the M3 shank from friction (one tab) | XY | 1.48 | 25.00 | 16.88 | 3 | OK |
| 15 | hand-push 5 N ring catch: tab tear-out to its edge (e 4.5) | XY shear | 0.79 | 12.50 | 15.76 | 3 | OK |
| 16 | assembly: screw-head clamp 100 N on the tab, no washer (compression) | XY | 6.81 | 25.00 | 3.67 | 3 | OK |

**lowest SF 3.67 (required 3) at: assembly: screw-head clamp 100 N on the tab, no washer (compression)**

## Proof test (spec §8 confirmed, with the base test raised)
The ring is covered by the base proof test, which should be raised from 20 N to **50 N on the turntable rim, 1 min at
each of 4 positions 90° apart**. Pass: no cracks in the tabs or the ring wall, no crushing of the ring top (the
1.5 mm running gap still clears), and the turntable then turns freely through ±90° with no rubbing.

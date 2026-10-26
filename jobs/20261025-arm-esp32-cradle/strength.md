VERDICT: NEEDS_TEST

# Strength check: 20261025-arm-esp32-cradle (round 3)

strength-analyst · 2026-10-26 · `python3 strength_calc.py` reads model.py, tools/hobby_parts.py and geometry.json

Round 3: the screws are now M3×10. That leaves a 4 mm clamp and 6 mm of thread, exactly the depth of the base boss
pilot, so there is no overrun (script FIT line). Every check is at SF 4.53 or above. The lowest is the USB-end ledge
under a 10 N jumper pull.

## Round 1 → round 2 → round 3

| | Round 1 | Round 2 |
|---|---|---|
| Verdict / lowest SF | FAIL / 0.71 (USB-end ledge, 1.6 × 4.4) | NEEDS_TEST / 4.53 (ledge now 2.8 × 8.4) |
| Spec 5 N pull on the ledge | 1.42 | 9.07 |
| Screws | M3×8, 2 mm engaged | M3×12 from counterbores: 4 mm clamp, 8 mm protrudes, 6 mm pilot → overrun |

**Round 2 → round 3:** M3×12 → M3×10: 6 mm engaged, fully seated, no overrun. No SF changed.

## Load cases

| Case | Load | Applied at, direction | Duration | Source |
|---|---|---|---|---|
| USB/jumper pull | 5 N, half on each end ledge (15 N proof) | ledges, down | short-term | spec |
| Jumper bundle pulled off | 10 N | ledges, down | short-term | added (round 1) |
| Micro-USB insertion | 20 N along −X | PCB edge on the far block, screws | short-term | added (round 1) |
| Board weight x2 | 0.2 N | ledges | sustained | added |

Build direction: printed upright with Z −20 on the bed; the ledges and walls bend in their own vertical planes, along
the layers.

## Assumptions

- Parameters come from `model.py`: frame 10 tall, ledges 8.4 tall, USB-end strip 2.8 wide running from y 13.15 to
  41.5 (28.35 long). It is still treated as a cantilever from the −Y wall, ignoring the soft centre spine.
- Counterbores Ø6.7 × 6 from below leave a 4 mm clamp. The far-block ligament past the counterbore is checked, as is
  head pull-through on the 4 mm floor.
- Pull-out and shear: τ = F/(π·d·L), against the interlayer shear allowable.

## Allowables and sources
`library/materials.csv` still has no measured row, and no printed-specimen datasheet is in `inputs/`, so these are the
strength-checks **placeholder** values for PETG. **NEEDS_TEST is the best verdict possible.**

| Quantity | Value | Source |
|---|---|---|
| Tension/bending along the layers (XY) | 25 MPa | skill placeholder, PETG |
| Tension/bending across the layers (Z) | 12.5 MPa | placeholder x 0.5 |
| Shear in-plane / interlayer (screw pull-out, washer pull-through, tear-out in vertical walls) | 12.5 / 6.25 MPa | 0.5 x the normal value (Tresca), assumption |
| Bearing, compression (any direction) | 25 MPa | in-plane value: compression does not separate layers |
| Kt | 2.5 sharp internal corner or window corner; 2.0 the 45° root wedge (two 135° corners); 2 hole; 1.5 rounded pocket tip | skill (2.0 for the wedge is my interpolation) |

Required SF: 3 short-term, 4 sustained or cyclic. Service temperature 40 °C (servo cases up to 45 °C) against PETG
softening at about 70 °C: margin of 25 °C or more, OK.

## Results (copied from `python3 strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | USB insertion 20 N: PCB edge bearing on the far block (1.6 x 28) | XY | 0.45 | 25.00 | 56.00 | 3 | OK |
| 2 | USB insertion: M3 shank bearing in the far-block holes (2 of 3, clamp length only) | XY | 0.83 | 25.00 | 30.00 | 3 | OK |
| 3 | USB insertion: far-block tear-out toward the pocket past the counterbore (ligament 2.05) | XY shear | 0.24 | 12.50 | 51.25 | 3 | OK |
| 4 | USB insertion: counterbore wall to the far-block end (ligament 2.75) | XY shear | 0.30 | 12.50 | 41.25 | 3 | OK |
| 5 | jumper pull: screw head through the 4 mm counterbore floor (head D5.5) | Z shear | 0.07 | 6.25 | 86.39 | 3 | OK |
| 6 | spec 5 N pull, 2.5 N on the USB end: USB-end ledge strip, cantilever from the -Y wall (Kt 2.5) | XY | 2.76 | 25.00 | 9.07 | 3 | OK |
| 7 | jumper pull 10 N, 5.0 N on the USB end: USB-end ledge strip, cantilever from the -Y wall (Kt 2.5) | XY | 5.51 | 25.00 | 4.53 | 3 | OK |
| 8 | jumper pull: -Y wall cantilever from the x40 pad (lever 3.8, Kt 2.5) | XY | 1.14 | 25.00 | 21.93 | 3 | OK |
| 9 | jumper pull: far-ledge root on the far block (Kt 2.5) | XY | 0.05 | 25.00 | 495.60 | 3 | OK |
| 10 | board weight x2 (sustained): USB-end ledge strip | XY | 0.11 | 25.00 | 231.09 | 4 | OK |

Advisory rows (not in the verdict, reason under Assumptions):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| 15 N proof (spec 8), 7.5 N on the USB end: USB-end ledge strip, cantilever from the -Y wall (Kt 2.5) | XY | 8.27 | 25.00 | 3.02 | 2 |

**lowest SF 4.53 (required 3) at: jumper pull 10 N, 5.0 N on the USB end: USB-end ledge strip, cantilever from the -Y wall (Kt 2.5)**

Script notes:

```
frame 10 tall, ledges 8.4 tall; USB-end strip 2.8 x 8.4, 28.35 long, load arm 14.53; screw clamp 4 mm under the head
FIT: M3x10 from the counterbore floor leaves 6 mm beyond the cradle vs a 6 mm pilot -> ok, fully engaged without bottoming
```

## Proof test (spec §8 confirmed)
15 N down on the USB end (SF 3.0 on the allowable at that load, advisory), then 5 USB plug cycles. Keep it; the cradle
is fitted with M3×10 screws.

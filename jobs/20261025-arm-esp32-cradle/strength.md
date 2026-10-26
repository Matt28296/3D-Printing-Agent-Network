VERDICT: FAIL

# Strength check: 20261025-arm-esp32-cradle

strength-analyst · 2026-10-26 · calculations in `strength_calc.py` (plain python3; section properties cross-checked against build123d sections of `design()`)

The **USB-end ledge** fails. It is a 1.6 × 4.4 mm strip that is only attached at the −Y wall: the +Y wall stops at
x 44 for the base pillar, and the centre spine is about 13 x softer than the strip, so it gives little support. The
strip is therefore a 29 mm cantilever. It fails even under the spec's own 5 N pull (SF 1.42 with 2.5 N on the USB end)
and at SF 0.71 under a 10 N jumper pull. Everything else is at SF 5 or above. The spec calls the part non-structural,
but a cracked ledge drops the board onto its pins.

## Load cases

| Case | Load | Applied at, direction | Duration | Source |
|---|---|---|---|---|
| USB/jumper pull | 5 N, half on each end ledge | ledges, down | short-term | spec |
| Jumper bundle pulled off | 10 N, half on each end ledge | ledges, down | short-term | **added** |
| Micro-USB insertion | 20 N along −X (connector spec allows up to 35 N) | PCB edge on the far block, screws | short-term | **added** |
| Board weight x2 | 0.2 N | ledges | sustained | added |

Build direction: printed upright (Z −16 on the bed). The ledges and walls bend in their own vertical planes, with
stress along X or Y, i.e. along the layers.

## Assumptions

- Board mass about 10 g. USB insertion is taken by 2 of the 3 screws. Hole edge distances are from the parameters
  (far-block hole at x −9.4, block face at −4.0).
- USB-end strip: cantilever from the −Y wall (y 13.25) to y 42.5. The PCB rests on it from y 13.85 to 41.75, and the
  load resultant sits at mid-contact. The spine is ignored (its stiffness is about 1.4 N/mm against about 18 N/mm for
  the strip). The junction is sharp, Kt 2.5.
- The −Y wall is a cantilever from the screw pad at x 40 (pad edge x 44.5) out to the USB ledge.
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
| 1 | USB insertion 20 N: PCB edge bearing on the far block (1.6 x 28) | XY | 0.45 | 25.00 | 56.00 | 3 | OK |
| 2 | USB insertion: M3 shank bearing in the far-block holes (2 of 3 share) | XY | 0.56 | 25.00 | 45.00 | 3 | OK |
| 3 | USB insertion: far-block hole tear-out toward the pocket (e-r 3.7) | XY shear | 0.23 | 12.50 | 55.50 | 3 | OK |
| 4 | spec 5 N pull, 2.5 N on the USB end: USB-end ledge strip, cantilever from the -Y wall (Kt 2.5) | XY | 17.61 | 25.00 | 1.42 | 3 | **FAIL** |
| 5 | jumper pull 10 N, 5.0 N on the USB end: USB-end ledge strip, cantilever from the -Y wall (Kt 2.5) | XY | 35.23 | 25.00 | 0.71 | 3 | **FAIL** |
| 6 | jumper pull: -Y wall cantilever from the x40 pad (Kt 2.5) | XY | 4.75 | 25.00 | 5.26 | 3 | OK |
| 7 | jumper pull: far-ledge root on the far block (cantilever 2.8, b 29.5, Kt 2.5) | XY | 0.18 | 25.00 | 135.98 | 3 | OK |
| 8 | board weight x2 (sustained): USB-end ledge strip | XY | 0.69 | 25.00 | 36.17 | 4 | OK |

**lowest SF 0.71 (required 3) at: jumper pull 10 N, 5.0 N on the USB end: USB-end ledge strip, cantilever from the -Y wall (Kt 2.5)**

## Geometry changes that pass (what-if below)
1. **USB-end ledge 1.6 → 2.8 mm wide** (x 48.2–51). It stays beyond the end-pin jumper housings, which reach x ≤ 48.0,
   but check this against the 30-pin board.
2. **BOT −16 → −20** (frame 6 → 10 mm, ledges 4.4 → 8.4 mm tall; PCB_BOT and the USB alignment are unchanged). The side
   walls stay outside the pin-row keep-out. Strip SF 0.71 → 4.53 at 10 N, 9.05 at the spec's 5 N.
Also: use **M3×12** cradle screws. M3×8 through the 6 mm frame (10 mm after change 2) leaves 2 mm of thread or less in
the base boss.

## Proof test to put in §8 once changed (the best verdict will still be NEEDS_TEST)
Replace "none needed" with: **board seated and the cradle screwed in, pull 15 N (≈1.5 kg on a luggage scale) straight
down on the board's USB end for 1 min, then plug and unplug the USB cable 5 times. Pass: no crack at the USB-end
ledge, the −Y wall or the screw pads; the board still sits on both ledges.**

### Script output: what-if / stability

```
WHAT-IF  USB-end ledge x 51-1.6 -> 51-2.8 (2.8 wide, still clear of the end-pin housings at x <= 48.0) and BOT -16 -> -20 (ledges 4.4 -> 8.4 tall; PCB_BOT unchanged):
  spec 5 N pull: USB-end ledge strip SF 9.05 OK
  jumper pull 10 N: USB-end ledge strip SF 4.53 OK
note: M3x8 through the 6 mm frame leaves ~2 mm of thread in the base boss -> use M3x12 (boss pilot is 6 deep)
```

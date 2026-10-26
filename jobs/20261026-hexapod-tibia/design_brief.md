# Design brief: Tibia (×6)

Job: 20261026-hexapod-tibia · design-lead · 2026-10-26 · round 3: strength round 1 (NEEDS_TEST, snug clamp) and the deep review

## Material
PETG for every hexapod part: tough, low creep under the servos' constant holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, horn pocket on the bed (bridge 7.9 mm). Bending in both directions runs along the layers.

## Concept
7 mm flat plate from the tibia MG90S horn to a rounded foot tip 70 mm away; tapers from a Ø18 hub to a Ø9 foot.

**Geometry unchanged in round 3.** The MG90S's own spec (B2) keeps the horn sizes, so the pocket is the same: a rebuild gives the same volume (7016.92 mm³) and bbox. Strength round 1 needs no change (lowest SF 4.59, assembly case), on condition that the clamp screw is driven **snug (≈ 0.05 N·m)**; spec §2 and BUILD_GUIDE now say so.

What round 3 changes around the tibia:
- **Closer to the femur.** The tibia servo is mounted reversed on the femur (deep review B1, option 2), so the tibia runs 3.1 mm off the femur's front face instead of 12.6 mm. Its back face must stay flat. The femur's clamp head is the nearest thing proud of the femur (2.1 mm), only reached with the tibia folded back past the femur axis.
- **Tucked stance.** The firmware tucks the tibia 18.7° in (femur −4.7°, tibia −14.0°), which splits the foot moment between the femur and knee servos (assembly plan, "Stance"). The foot load now bends the tibia; the knee servo's stall still caps it at the checked 216 N·mm.

## Critical dimensions
| Feature | Nominal | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Knee → foot tip | 70.0 | ±0.3 | stance height | — | hex_frame `L_T` |
| Clamp hole / horn pocket | Ø2.4 + HOLE_COMP / horn + 0.5 + HOLE_COMP, 2 deep | +0.2 | M2 clearance / horn locating | HOLE_COMP +0.2 | default from fdm-design-rules (no library row) |

## Parameters exposed by model.py
HOLE_COMP, HUB_R, FOOT_R, BED_CHAMFER (+ hex_frame.py)

## Risks
- **Thin foot (Ø9) under sideways load:** checked by strength (SF ≥ 7).
- **Foot tip on hard floors:** ≈ 12 MPa line contact walking (advisory); a TPU sock spreads it.
- **Print time:** round 2's slice of 6 tibias took 3.9 h against spec §7's 3 h: print 4 + 2, or the user relaxes §7.

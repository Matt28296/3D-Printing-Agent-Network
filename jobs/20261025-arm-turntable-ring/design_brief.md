# Design brief: Turntable support ring

Job: 20261025-arm-turntable-ring · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~70 °C (material-selection skill) still 30 °C above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, tabs on the bed. Compression in the wall runs across layers but in pure compression (layer bonding not loaded in tension).

## Concept
Ring (r 41–44, 15 mm tall) screwed to the base top plate under the turntable. A 1.5 mm running gap means it only touches when the arm tips, so the base servo's output bearing is not the only thing resisting a knock.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Ring height | 15.0 | ±0.2 | 1.5 mm running gap to turntable | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Tab holes | Ø3.4 at r47.5 | ±0.2 | M3 clearance | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: servo windows +0.4 total (SG90 window ends +0.2), horn pockets +0.5 total, M3 clearance Ø3.4, M2 clearance Ø2.4, self-tap pilots Ø2.6 (MG996R tab screws) and Ø1.5 (SG90 tab screws). Every hole and pocket also gets **HOLE_COMP = +0.2 mm** in CAD (fdm-design-rules default; no library row yet), applied in tools/hobby_parts.py cutters and each model.py. Horn joints: the horn's centre screw is replaced by a longer one + washer through the link, clamping link and horn onto the spline (strength round 1).

## Parameters exposed by model.py
HOLE_COMP, R_IN, R_OUT, TURNTABLE_Z, RUN_GAP, H, TAB_R, TAB_ANG, TAB_D, TAB_T, TAB_HOLE

## Risks
- Ring rubs the turntable if the base servo sits low → 1.5 mm gap, sand to fit

# Design brief: Turntable support ring

Job: 20261025-arm-turntable-ring · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~80 °C far above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, tabs on the bed. Compression in the wall runs across layers but in pure compression (layer bonding not loaded in tension).

## Concept
Ring (r 41–44.5, 13 mm tall) screwed to the base top plate under the turntable. A 1.5 mm running gap means it only touches when the arm tips, so the base servo's output bearing is not the only thing resisting a knock.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Ring height | 13.0 | ±0.2 | 1.5 mm running gap to turntable | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |
| Tab holes | Ø3.4 at r48 | ±0.2 | M3 clearance | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |

Clearances: servo windows +0.4 total (0.2/side), horn pockets +0.5 total, M3 clearance Ø3.4, self-tap pilots Ø2.6 (M3/MG996R screws) and Ø1.8 (SG90 screws). Source: fdm-design-rules defaults, recorded in tools/hobby_parts.py.

## Parameters exposed by model.py
R_IN, R_OUT, TURNTABLE_Z, RUN_GAP, H, TAB_R, TAB_ANG, TAB_D, TAB_T, TAB_HOLE

## Risks
- Ring rubs the turntable if the base servo sits low → 1.5 mm gap, sand to fit

# Design brief: Upper link (shoulder → elbow, 100 mm)

Job: 20261025-arm-upper-link · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~80 °C far above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, back face (horn slot) on the bed. All bending loads are in the plate's plane, along the layers.

## Concept
Flat 6 mm plate on the shoulder servo's double-arm horn, carrying the elbow MG996R at 100 mm.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Shoulder–elbow axis distance | 100.0 | ±0.3 | kinematics | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |
| Horn slot | as turntable | +0.2/−0 | locating | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |
| Elbow window | 41.1 × 20.1 | +0.3/−0 | clearance | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |

Clearances: servo windows +0.4 total (0.2/side), horn pockets +0.5 total, M3 clearance Ø3.4, self-tap pilots Ø2.6 (M3/MG996R screws) and Ø1.8 (SG90 screws). Source: fdm-design-rules defaults, recorded in tools/hobby_parts.py.

## Parameters exposed by model.py
SERVO, L, T, HALF_W, X0, X1, CORNER_R, LIGHT, CLR

## Risks
- Horn slot ceiling bridge (9.5 mm strand) on the bed side → acceptable, bridging settings

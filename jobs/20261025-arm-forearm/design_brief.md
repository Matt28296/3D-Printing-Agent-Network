# Design brief: Forearm (elbow → wrist, 90 mm)

Job: 20261025-arm-forearm · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~80 °C far above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, horn slot side on the bed. Loads in-plane, along layers.

## Concept
Flat 5 mm plate on the elbow servo's double-arm horn, carrying the wrist SG90 at 90 mm.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Elbow–wrist axis distance | 90.0 | ±0.3 | kinematics | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |
| SG90 window | 22.9 × 12.4 | +0.3/−0 | clearance | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |

Clearances: servo windows +0.4 total (0.2/side), horn pockets +0.5 total, M3 clearance Ø3.4, self-tap pilots Ø2.6 (M3/MG996R screws) and Ø1.8 (SG90 screws). Source: fdm-design-rules defaults, recorded in tools/hobby_parts.py.

## Parameters exposed by model.py
HORN_SERVO, WRIST, L, T, HALF_W, X0, X1, CORNER_R, LIGHT, CLR

## Risks
- Thin 5 mm plate around the 2 mm pocket: 3 mm ceiling → checked by strength analysis

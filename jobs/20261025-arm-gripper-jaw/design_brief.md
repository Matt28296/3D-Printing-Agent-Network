# Design brief: Moving jaw

Job: 20261025-arm-gripper-jaw · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~80 °C far above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, pocket side on the bed. Bending in-plane, along layers.

## Concept
Lever (hub r8 + 55 mm bar) on the gripper SG90's single-arm horn; closes against the fixed jaw.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Jaw face | y = −6.0 (closed) | ±0.3 | meets fixed jaw | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |

Clearances: servo windows +0.4 total (0.2/side), horn pockets +0.5 total, M3 clearance Ø3.4, self-tap pilots Ø2.6 (M3/MG996R screws) and Ø1.8 (SG90 screws). Source: fdm-design-rules defaults, recorded in tools/hobby_parts.py.

## Parameters exposed by model.py
SERVO, T, HUB_R, BAR_X1, BAR_Y0, BAR_Y1

## Risks
- Thin wall beside the arm pocket (found by mesh check, fixed by widening the bar to +5.5)

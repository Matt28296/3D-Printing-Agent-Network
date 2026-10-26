# Design brief: Gripper base with fixed jaw

Job: 20261025-arm-gripper-base · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~80 °C far above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, horn pocket on the bed; fixed jaw block grows up from the plate. Jaw-block bending puts its root across layers (low load: 2.9 N).

## Concept
5 mm plate on the wrist SG90's single-arm horn; carries the gripper SG90 at x 40 and the fixed jaw (x 55–95, face at y −6).

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Wrist–gripper axis distance | 40.0 | ±0.3 | jaw geometry | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |
| Fixed jaw face | y = −6.0 | ±0.3 | meets moving jaw | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |

Clearances: servo windows +0.4 total (0.2/side), horn pockets +0.5 total, M3 clearance Ø3.4, self-tap pilots Ø2.6 (M3/MG996R screws) and Ø1.8 (SG90 screws). Source: fdm-design-rules defaults, recorded in tools/hobby_parts.py.

## Parameters exposed by model.py
SERVO, T, GRIP_X, X0, X1, Y0, Y1, CORNER_R, JAW_X0, JAW_X1, JAW_Y0, JAW_Y1, JAW_TOP, CLR

## Risks
- Jaw root across layers → load is tiny (SG90 max 2.9 N)

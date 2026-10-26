# Design brief: Gripper base with fixed jaw

Job: 20261025-arm-gripper-base · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~70 °C (material-selection skill) still 30 °C above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, horn pocket on the bed (SG90 pocket bridges 7.9 mm); fixed jaw block grows up from the plate. Jaw-block bending puts its root across layers.

## Concept
8 mm plate on the wrist SG90's single-arm horn; carries the gripper SG90 at x 40 and the fixed jaw (x 55–95, face at y −6).

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Wrist–gripper axis distance | 40.0 | ±0.3 | jaw geometry | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Fixed jaw face | y = −6.0 | ±0.3 | meets moving jaw | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: servo windows +0.4 total (SG90 window ends +0.2), horn pockets +0.5 total, M3 clearance Ø3.4, M2 clearance Ø2.4, self-tap pilots Ø2.6 (MG996R tab screws) and Ø1.5 (SG90 tab screws). Every hole and pocket also gets **HOLE_COMP = +0.2 mm** in CAD (fdm-design-rules default; no library row yet), applied in tools/hobby_parts.py cutters and each model.py. Horn joints: the horn's centre screw is replaced by a longer one + washer through the link, clamping link and horn onto the spline (strength round 1).

## Parameters exposed by model.py
SERVO, HOLE_COMP, T, GRIP_X, X0, X1, Y0, Y1, CORNER_R, JAW_X0, JAW_X1, JAW_Y0, JAW_Y1, JAW_T, JAW_TOP, CLR, END_CLR, BED_CHAMFER

## Risks
- Jaw root across layers → 17.4 mm-tall block, low SG90 forces
- SG90 pilot wall → Ø1.5 pilot + 0.2 end clearance
- Plate 5→8 and centre-screw clamp (strength round 1)

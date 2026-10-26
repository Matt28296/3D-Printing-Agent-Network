# Design brief: Moving jaw

Job: 20261025-arm-gripper-jaw · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~70 °C (material-selection skill) still 30 °C above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, pocket side on the bed (bridge 7.9 mm). Bending along the layers.

## Concept
Lever (hub r8 + 55 mm × 14 mm bar, 8 thick) on the gripper SG90's single-arm horn; closes against the fixed jaw.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Jaw face | y = −6.0 (closed) | ±0.3 | meets fixed jaw | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: servo windows +0.4 total (SG90 window ends +0.2), horn pockets +0.5 total, M3 clearance Ø3.4, M2 clearance Ø2.4, self-tap pilots Ø2.6 (MG996R tab screws) and Ø1.5 (SG90 tab screws). Every hole and pocket also gets **HOLE_COMP = +0.2 mm** in CAD (fdm-design-rules default; no library row yet), applied in tools/hobby_parts.py cutters and each model.py. Horn joints: the horn's centre screw is replaced by a longer one + washer through the link, clamping link and horn onto the spline (strength round 1).

## Parameters exposed by model.py
SERVO, HOLE_COMP, T, HUB_R, BAR_X1, BAR_Y0, BAR_Y1, BED_CHAMFER

## Risks
- Thin wall beside the arm pocket (found by mesh check, fixed by widening the bar to +5.5)

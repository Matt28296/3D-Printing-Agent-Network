# Design brief: Coxa bracket (×6)

Job: 20261026-hexapod-coxa · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG for every hexapod part: tough, low creep under the servos' constant holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Horizontal plate on the bed (horn pocket bridge 7.9 mm), vertical plate standing with its window roof up. The vertical plate's root bends across the layers: 4.5 mm plate + 6 mm 45° gussets.

## Concept
L-shaped bracket under the coxa MG90S horn: a hub plate round the horn and an arm (outside the femur's swing plane) out to a vertical plate that carries the femur MG90S with its axis horizontal and tangential, 32 mm out from the coxa axis.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Coxa axis → femur axis | 32.0 radial | ±0.3 | leg geometry | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Femur axis height | 13.0 below the back face | ±0.3 | leg geometry | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: servo windows +0.4 side / +0.2 end clearance, horn pockets +0.5, M2 clamp-screw holes Ø2.4, SG90/MG90S tab-screw pilots Ø1.5, M3 clearance Ø3.4, column pilots Ø2.6, PCA9685 post pilots Ø2.2. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row). Horn joints: an M2×12 centre screw + washer goes through the link into the spline, as on the arm (strength review of the arm).

## Parameters exposed by model.py
HOLE_COMP, CLR, END_CLR, HUB, ARM_Y, VPLATE_X, WIN_HALF, ROOF, VPLATE_H, GUSSET, BED_CHAMFER (+ hex_frame.py)

## Risks
- Window roof would cut the pilots on a short side → roof on the long side (hobby_parts refuses the other)
- Arm in the femur's plane → arm kept at y ≤ −6.5

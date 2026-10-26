# Design brief: Femur (×6)

Job: 20261026-hexapod-femur · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG for every hexapod part: tough, low creep under the servos' constant holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, horn pocket on the bed (bridge 7.9 mm). Bending along the layers.

## Concept
7 mm flat plate from the femur MG90S horn to the knee (45 mm), carrying the tibia MG90S.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Femur axis → knee | 45.0 | ±0.3 | leg geometry | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: servo windows +0.4 side / +0.2 end clearance, horn pockets +0.5, M2 clamp-screw holes Ø2.4, SG90/MG90S tab-screw pilots Ø1.5, M3 clearance Ø3.4, column pilots Ø2.6, PCA9685 post pilots Ø2.2. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row). Horn joints: an M2×12 centre screw + washer goes through the link into the spline, as on the arm (strength review of the arm).

## Parameters exposed by model.py
HOLE_COMP, HALF_W, X0, X1, CLR, END_CLR, BED_CHAMFER (+ hex_frame.py)

## Risks
- SG90-size pilot wall 1.8 mm printed, as reviewed on the arm

# Design brief: Hexapod bottom body plate

Job: 20261026-hexapod-body-bottom · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG for every hexapod part: tough, low creep under the servos' constant holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, the tab face (underside) on the bed. Plate bending along the layers; the tab screws pull out across the layers.

## Concept
4 mm plate (hull of the six coxa-servo windows, 155 × 131 mm) that the six coxa MG90S hang under (tabs on its underside, shafts down), with four 30 mm columns for the top plate and two strap slots for the 2S LiPo that sits on it.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Coxa servo windows | 22.7 × 12.6 printed | +0.3/−0 | 0.1 end / 0.2 side clearance | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Mount positions | per hex_frame.LEG_MOUNTS | ±0.3 | leg spacing | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Column height | 30.0 | ±0.3 | top-plate seat | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: servo windows +0.4 side / +0.2 end clearance, horn pockets +0.5, M2 clamp-screw holes Ø2.4, SG90/MG90S tab-screw pilots Ø1.5, M3 clearance Ø3.4, column pilots Ø2.6, PCA9685 post pilots Ø2.2. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row). Horn joints: an M2×12 centre screw + washer goes through the link into the spline, as on the arm (strength review of the arm).

## Parameters exposed by model.py
HOLE_COMP, CLR, END_CLR, MARGIN, COLUMNS, COLUMN_D, COLUMN_PILOT, PILOT_DEPTH, STRAP, BED_CHAMFER (+ hex_frame.py)

## Risks
- Many small pilots: 1.8 mm printed wall to each window end, as reviewed on the arm

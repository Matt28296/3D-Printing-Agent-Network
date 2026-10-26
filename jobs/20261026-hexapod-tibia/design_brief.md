# Design brief: Tibia (×6)

Job: 20261026-hexapod-tibia · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG for every hexapod part: tough, low creep under the servos' constant holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, horn pocket on the bed (bridge 7.9 mm). Bending along the layers.

## Concept
7 mm flat plate from the tibia MG90S horn to a rounded foot tip 70 mm away; tapers from a Ø18 hub to a Ø9 foot.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Knee → foot tip | 70.0 | ±0.3 | stance height | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: servo windows +0.4 side / +0.2 end clearance, horn pockets +0.5, M2 clamp-screw holes Ø2.4, SG90/MG90S tab-screw pilots Ø1.5, M3 clearance Ø3.4, column pilots Ø2.6, PCA9685 post pilots Ø2.2. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row). Horn joints: an M2×12 centre screw + washer goes through the link into the spline, as on the arm (strength review of the arm).

## Parameters exposed by model.py
HOLE_COMP, HUB_R, FOOT_R, BED_CHAMFER (+ hex_frame.py)

## Risks
- Thin foot (Ø9) under sideways load → checked by strength analysis

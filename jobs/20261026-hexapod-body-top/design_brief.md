# Design brief: Hexapod top plate / electronics deck

Job: 20261026-hexapod-body-top · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG for every hexapod part: tough, low creep under the servos' constant holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, underside on the bed; seat and posts rise from the top.

## Concept
3 mm deck (130 × 104 mm) on the four columns, carrying the ESP32 seat (pins down through a window), two PCA9685 servo drivers on M2.5 posts, the UBEC, and four cable slots for the 18 servo leads.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| PCA9685 post pattern | 56 × 19 | ±0.2 | board holes | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| ESP32 pocket width | 29.7 | +0.3/−0 | 0.6 clearance | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: servo windows +0.4 side / +0.2 end clearance, horn pockets +0.5, M2 clamp-screw holes Ø2.4, SG90/MG90S tab-screw pilots Ø1.5, M3 clearance Ø3.4, column pilots Ø2.6, PCA9685 post pilots Ø2.2. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row). Horn joints: an M2×12 centre screw + washer goes through the link into the spline, as on the arm (strength review of the arm).

## Parameters exposed by model.py
HOLE_COMP, SIZE, CORNER_R, SCREWS, SCREW_D, BOARDS, USB_END_X, LEDGE_H, CLR, RAIL_W, HALF, ROW_KEEP, END_LEDGE, PCA_Y, POST_D, POST_H, POST_PILOT, TIE_SLOT, BED_CHAMFER

## Risks
- Posts 5 mm tall Ø5.5 with a Ø2.4 pilot: 1.55 mm wall, but non-structural
- Column screw heads on the PCA9685 posts (DFM round 1) → column pattern (±40, ±25) from hex_frame.py; heads clear the posts, boards and cable slots

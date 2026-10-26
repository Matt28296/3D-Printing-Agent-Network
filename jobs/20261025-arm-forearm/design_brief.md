# Design brief: Forearm (elbow → wrist, 90 mm)

Job: 20261025-arm-forearm · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~70 °C (material-selection skill) still 30 °C above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, FRONT face on the bed (horn pocket opens upward, no bridge). Bending along the layers.

## Concept
Flat 10 mm plate on the elbow servo's double-arm horn, carrying the wrist SG90 at 90 mm.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Elbow–wrist axis distance | 90.0 | ±0.3 | kinematics | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| SG90 window | 22.7 × 12.4 | +0.3/−0 | clearance 0.1/side at the ends | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| SG90 pilot-to-window wall | 1.8 printed | min | 4 perimeters | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: servo windows +0.4 total (SG90 window ends +0.2), horn pockets +0.5 total, M3 clearance Ø3.4, M2 clearance Ø2.4, self-tap pilots Ø2.6 (MG996R tab screws) and Ø1.5 (SG90 tab screws). Every hole and pocket also gets **HOLE_COMP = +0.2 mm** in CAD (fdm-design-rules default; no library row yet), applied in tools/hobby_parts.py cutters and each model.py. Horn joints: the horn's centre screw is replaced by a longer one + washer through the link, clamping link and horn onto the spline (strength round 1).

## Parameters exposed by model.py
HORN_SERVO, WRIST, HOLE_COMP, L, T, HALF_W, X0, X1, CORNER_R, CLR, END_CLR, BED_CHAMFER

## Risks
- SG90 pilot-to-window wall 1.55 mm (DFM round 1) → Ø1.5 printed pilot + 0.2 end clearance → 1.8 mm printed
- Sideways loads (strength round 1) → T 5→10, slot removed, centre-screw clamp
- Wrist SG90 tab screws pull out (strength round 2) → M2×12 self-tapping, 9.5 mm engaged

# Design brief: Upper link (shoulder → elbow, 100 mm)

Job: 20261025-arm-upper-link · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~70 °C (material-selection skill) still 30 °C above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, FRONT face on the bed (the horn pocket opens upward, so no bridge). In-plane and out-of-plane bending run along the layers; horn-joint pull-out shears the layers, which the centre-screw clamp now carries.

## Concept
Flat 10 mm plate on the shoulder servo's double-arm horn, carrying the elbow MG996R at 100 mm.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Shoulder–elbow axis distance | 100.0 | ±0.3 | kinematics | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Horn slot | as turntable | +0.2/−0 | locating | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Elbow window | 41.1 × 20.1 | +0.3/−0 | clearance | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: servo windows +0.4 total (SG90 window ends +0.2), horn pockets +0.5 total, M3 clearance Ø3.4, M2 clearance Ø2.4, self-tap pilots Ø2.6 (MG996R tab screws) and Ø1.5 (SG90 tab screws). Every hole and pocket also gets **HOLE_COMP = +0.2 mm** in CAD (fdm-design-rules default; no library row yet), applied in tools/hobby_parts.py cutters and each model.py. Horn joints: the horn's centre screw is replaced by a longer one + washer through the link, clamping link and horn onto the spline (strength round 1).

## Parameters exposed by model.py
SERVO, HOLE_COMP, L, T, HALF_W, X0, X1, CORNER_R, CLR, BED_CHAMFER

## Risks
- Horn-slot bridge 10.6 mm (DFM round 1) → printed front-face down, pocket opens upward
- Sideways loads (strength round 1) → T 6→10, lightening slot removed, centre-screw clamp

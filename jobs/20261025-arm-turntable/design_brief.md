# Design brief: Turntable with shoulder upright

Job: 20261025-arm-turntable · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~80 °C far above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Disk on the bed, upright vertical. Shoulder torque is in the upright's plane (along layers). The out-of-plane moment bends the upright across its layers at the root, which is why the gussets are there.

## Concept
Ø96 × 5 mm disk that sits on the base servo's double-arm horn (2 mm slot pocket underneath), with a 66 × 5 mm upright and two gussets that hold the shoulder MG996R horizontally (shaft +Y, axis at X 10.15, Z 60.5).

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Horn slot | hub Ø11.5, width 6.0 at tips, depth 2.0 | +0.2/−0 | horn locating, clearance 0.25/side | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |
| Shoulder window | 41.1 × 20.1 | +0.3/−0 | clearance 0.2/side | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |
| Shoulder axis | X 10.15, Z 60.5 (assembly frame) | ±0.3 | position | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |

Clearances: servo windows +0.4 total (0.2/side), horn pockets +0.5 total, M3 clearance Ø3.4, self-tap pilots Ø2.6 (M3/MG996R screws) and Ø1.8 (SG90 screws). Source: fdm-design-rules defaults, recorded in tools/hobby_parts.py.

## Parameters exposed by model.py
SERVO, Z0, DISK_R, DISK_T, CLR, UP_T, UP_W, UP_Y, XS, ZS, WIN_HALF_H, ROOF_H, UP_TOP, GUSSET_T, GUSSET_X, GUSSET_LEN, GUSSET_H

## Risks
- Window roof cutting tab pilots (found in review, fixed by turning the servo horizontal)
- Horn slot ceiling bridge 11.5 mm with a Ø6.5 hole in the middle → longest strand 9.5 mm
- Upright root across layers → gussets 50 × 30 mm

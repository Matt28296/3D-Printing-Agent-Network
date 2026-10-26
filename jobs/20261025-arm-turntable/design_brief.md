# Design brief: Turntable with shoulder upright

Job: 20261025-arm-turntable · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~70 °C (material-selection skill) still 30 °C above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Disk on the bed, upright vertical. All upright bending, in-plane and out of plane, puts stress across the layers (Z); the 7 mm upright, the 3 mm root wedges and the 70 mm gussets size for that with the across-layer allowable. Disk bending runs along the layers.

## Concept
Ø96 × 8 mm disk whose flat underside sits on the base servo's double-arm horn (no pocket, so no bridge), with a 66 × 7 mm upright, root wedges and two 70 mm gussets that hold the shoulder MG996R horizontally (shaft +Y, axis at X 10.15, Z 60.5).

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Clamp hole | Ø3.4 | +0.2/−0 | M3 clearance | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Shoulder window | 41.1 × 20.1 | +0.3/−0 | clearance 0.2/side | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Shoulder axis | X 10.15, Z 60.5 (assembly frame) | ±0.3 | position | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: servo windows +0.4 total (SG90 window ends +0.2), horn pockets +0.5 total, M3 clearance Ø3.4, M2 clearance Ø2.4, self-tap pilots Ø2.6 (MG996R tab screws) and Ø1.5 (SG90 tab screws). Every hole and pocket also gets **HOLE_COMP = +0.2 mm** in CAD (fdm-design-rules default; no library row yet), applied in tools/hobby_parts.py cutters and each model.py. Horn joints: the horn's centre screw is replaced by a longer one + washer through the link, clamping link and horn onto the spline (strength round 1).

## Parameters exposed by model.py
SERVO, HOLE_COMP, Z0, DISK_R, DISK_T, CLR, UP_T, UP_W, UP_Y, XS, ZS, WIN_HALF_H, ROOF_H, UP_TOP, GUSSET_T, GUSSET_X, GUSSET_LEN, GUSSET_H, ROOT_FILLET, BED_CHAMFER

## Risks
- Window roof cutting tab pilots (found in design, fixed by turning the servo horizontal; hobby_parts now refuses such roofs)
- Horn-slot ceiling bridge 10.6 mm (DFM round 1) → no pocket: horn flat on the bed face, clamped by the centre screw
- Upright root across layers → UP_T 7, root wedges, 70 mm gussets with toes inside the disk
- Horizontal pilots → teardrops pointing up

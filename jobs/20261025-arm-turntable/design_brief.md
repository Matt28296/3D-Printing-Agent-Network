# Design brief: Turntable with shoulder upright

Job: 20261025-arm-turntable · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~70 °C (material-selection skill) still 30 °C above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Disk on the bed, upright vertical. All upright bending, in-plane and out of plane, puts stress across the layers (Z); the 7 mm upright, the 3 mm root wedges and the 70 mm gussets size for that with the across-layer allowable. Disk bending runs along the layers.

## Concept
Ø96 × 8 mm disk whose flat underside sits on the base servo's Ø25 disc horn (round 3; no pocket, so no bridge), with a 66 × 7 mm upright, root wedges and two 70 mm gussets that hold the shoulder MG996R horizontally (shaft +Y, axis at X 10.15, Z 60.5).

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Clamp hole | Ø3.4 | +0.2/−0 | M3 clearance | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Shoulder window | 41.1 × 20.1 | +0.3/−0 | clearance 0.2/side | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Shoulder axis | X 10.15, Z 60.5 (assembly frame) | ±0.3 | position | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: servo windows +0.4 total (SG90 window ends +0.2), horn pockets +0.5 total, M3 clearance Ø3.4, M2 clearance Ø2.4, self-tap pilots Ø2.6 (MG996R tab screws) and Ø1.5 (SG90 tab screws). Every hole and pocket also gets **HOLE_COMP = +0.2 mm** in CAD (fdm-design-rules default; no library row yet), applied in tools/hobby_parts.py cutters and each model.py. Horn joints: the horn's centre screw is replaced by a longer one + washer through the link, clamping link and horn onto the spline (strength round 1).

## Parameters exposed by model.py
SERVO, HOLE_COMP, Z0, DISK_R, DISK_T, CLR, UP_T, UP_W, UP_Y, XS, ZS, WIN_HALF_H, ROOF_H, UP_TOP, GUSSET_T, GUSSET_X, GUSSET_LEN, GUSSET_H, ROOT_FILLET, WASHER_CLEAR_X, BED_CHAMFER

## Risks
- Window roof cutting tab pilots (found in design, fixed by turning the servo horizontal; hobby_parts now refuses such roofs)
- Horn-slot ceiling bridge 10.6 mm (DFM round 1) → no pocket: horn flat on the bed face, clamped by the centre screw
- Upright root across layers → UP_T 7, root wedges, 70 mm gussets with toes inside the disk
- Horizontal pilots → teardrops pointing up
- Clamp washer on the root wedge (round 2) → front wedge stops at |X| ≥ 6

## Round 3 (2026-10-26: deep reviews 01 B1/S2/S3/S4, 03 SYS-04/SYS-05/SYS-09/SYS-16)
- **Disc horn (SYS-05).** The base servo's round Ø25 disc horn replaces the double-arm horn under the disk: it supports the disk ±12.5 mm in every direction instead of on the Ø11 hub across the arms. The disk's underside is flat, so the CAD doesn't change; the 2 anti-rotation screws (M2 × 6, S4) go through two of the disc's holes. Clamp: M3 × 14 socket head (ISO 4762, SYS-16: re-tightened with an L-key past the upright) + Ø9 × 0.8 washer, 4.6 mm into the spline (S2).
- **Lead notches (B1).** The shoulder MG996R goes in from the front (+Y) face, case bottom first; `lead="notch"` cuts a 4.4 × 2.0 mm (printed) notch at both case ends. The notch is a hole in a standing wall, so `_notch_tops()` adds a right triangle over each one: its ceiling rises at 45° from the notch's end wall to the window (the hexapod coxa's DFM round 3 failed a flat notch top). Printed ligaments: notch → nearest pilot 2.05 mm, 45° top → pilot ≈2.0 mm. Pilots stay teardrops pointing up.
- **Tab screws (S3):** 4 × M3 × 12 pan-head self-tapping + Ø7 washers; 7 mm engaged, the tips stand 2 mm out of the back face at X ±24.25, clear of the gussets (|X| ≥ 28.5).
- **Orientation (SYS-09):** the upright's front face (+Y) is where the shoulder shaft comes out; at the base servo's centre it faces +Y, so the arm reaches out over the +X (USB) wall at yaw 0.
- **Loads (SYS-04):** the arm and camera hang outboard of the upright: 290 N·mm (335 with 50 g) about X at the upright's mid-plane in every pose, with the round-3 claw (spec §4; was ≈100 N·mm with the old gripper).
- measure_holes: 4 × Ø2.8 shoulder tab pilots (teardrops), Ø3.6 clamp hole.

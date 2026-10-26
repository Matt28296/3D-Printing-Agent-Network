# Design brief: Brio 4K camera mount (optional)

Job: 20261026-arm-camera-mount · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG, as for the rest of the arm: tough, low creep under the servo's holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Standing on its −y end: the side profile lies in the bed plane, so the tilted seat and lip are vertical walls and need no support. The seat cantilever bends along the layers. The 1/4" slot and the M3 holes are teardrops pointing up. 50 mm tall on a 186 mm² footprint: use a brim.

## Concept
Holds a Logitech Brio 4K (clip removed) on top of the claw, lens pointing along the fingers and tilted 30° down so the jaws sit near the middle of the picture. The camera's own 1/4"-20 thread takes a knurled thumb screw from under the seat; a rear lip stops it turning. Shares the cover's two top screws, so the claw works without it.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Seat angle | 30° nose-down | ±1° | aims the camera | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| 1/4" slot | Ø6.85 printed, ±4 along y | +0.3/−0 | clearance | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Lip to camera back | 0.3 | ±0.2 | anti-rotation | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: MG90S window +0.4 side / +0.2 end, wrist horn pocket +0.5, pinion horn pocket +0.3 (gear backlash adds up), M2 clamp holes Ø2.4, M3 clearance Ø3.4, M3 self-tap pilots Ø2.5, MG90S tab pilots Ø1.5, 1/4"-20 clearance Ø6.85. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row). Sliding clearance around the racks 0.25 mm; gears module 1, 20°, each member 0.1 mm thinner (0.2 mm backlash). Gears and racks are drawn in the bed plane (axis vertical) so the involute is as accurate as XY.

## Parameters exposed by model.py
HOLE_COMP, SCREW_CLR, SLOT_HALF, TO_PRINT, CAM_LOC; shared: claw_frame.py (CAM_TILT, CAM_XC, CAM_ZC, SEAT_T, LIP_T, LIP_H, LIP_CLR, MOUNT_Y, PAD_X, PAD_TOP, TOP_SCREWS)

## Risks
- Tilted seat would need support lying down → printed standing, profile on the bed
- Camera front corner over the pad → pad top 0.25 under the corner, button-head screws
- The Brio is 102 mm wide: it overhangs the claw by 19 mm each side (clear of every arm part in the assembly check)

# Design brief: ESP32 cradle

Job: 20261025-arm-esp32-cradle · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~70 °C (material-selection skill) still 30 °C above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Upright, frame bottom (Z −20) on the bed; all ledges rise from the bed; counterbore ceilings bridge 6.7 mm.

## Concept
Open frame that hangs under the base top plate on 3 bosses and holds an ESP32 DevKit (38-pin or 30-pin) pins-down, USB at the base's +X slot, so female jumpers fit every pin.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| PCB pocket width | 29.5 | +0.3/−0 | 0.6 clearance around a 28.3 board | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Ledge height | Z −11.6 | ±0.2 | lines the USB up with the slot | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: servo windows +0.4 total (SG90 window ends +0.2), horn pockets +0.5 total, M3 clearance Ø3.4, M2 clearance Ø2.4, self-tap pilots Ø2.6 (MG996R tab screws) and Ø1.5 (SG90 tab screws). Every hole and pocket also gets **HOLE_COMP = +0.2 mm** in CAD (fdm-design-rules default; no library row yet), applied in tools/hobby_parts.py cutters and each model.py. Horn joints: the horn's centre screw is replaced by a longer one + washer through the link, clamping link and horn onto the spline (strength round 1).

## Parameters exposed by model.py
BOARDS, HOLE_COMP, USB_END_X, YC, PCB_BOT, TOP, BOT, CLR, WALL, HALF, ROW_KEEP, USB_LEDGE_W, USB_LEDGE_Y1, PILLAR_CLEAR_X, SCREWS, HOLE, CBORE_D, CBORE_DEPTH, PAD_R, FAR_BLOCK_X0, BED_CHAMFER

## Risks
- Jumper housings blocked by the frame → nothing passes under the pin rows (|y − 28| between 11 and 15)
- Base corner pillar → +Y wall stops at x 44, USB ledge at y 41.5
- USB-end ledge cantilever (strength round 1) → 2.8 wide, frame 10 tall
- 2 mm screw engagement (both reviews) → counterbores + M3×10 (6 mm thread, matches the 6 mm boss pilot)

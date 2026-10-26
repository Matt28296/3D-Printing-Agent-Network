# Design brief: ESP32 cradle

Job: 20261025-arm-esp32-cradle · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~80 °C far above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Upright, frame bottom (Z −16) on the bed; all ledges rise from the bed.

## Concept
Open frame that hangs under the base top plate on 3 bosses and holds an ESP32 DevKit (38-pin or 30-pin) pins-down, USB at the base's +X slot, so female jumpers fit every pin.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| PCB pocket width | 29.5 | +0.3/−0 | 0.6 clearance around a 28.3 board | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |
| Ledge height | Z −11.6 | ±0.2 | lines the USB up with the slot | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |

Clearances: servo windows +0.4 total (0.2/side), horn pockets +0.5 total, M3 clearance Ø3.4, self-tap pilots Ø2.6 (M3/MG996R screws) and Ø1.8 (SG90 screws). Source: fdm-design-rules defaults, recorded in tools/hobby_parts.py.

## Parameters exposed by model.py
BOARDS, USB_END_X, YC, PCB_BOT, TOP, BOT, CLR, WALL, HALF, ROW_KEEP, PILLAR_CLEAR_X, SCREWS, HOLE

## Risks
- Jumper housings blocked by the frame → nothing passes under the pin rows (|y − 28| between 11 and 15)
- Base corner pillar → +Y wall stops at x 44

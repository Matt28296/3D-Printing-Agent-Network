# Design brief: Robot arm base

Job: 20261025-arm-base · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~80 °C far above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Upside down: top plate on the bed. All wall openings have 45° roofs pointing at the desk side (up in print). Top plate in-plane loads run along the layers.

## Concept
Open-bottom box (110 × 104 × 40 mm) that holds the base-yaw MG996R (hanging through its top plate), the turntable support ring, the ESP32 cradle, the 5.5 × 2.1 mm DC panel jack and the USB access slot. Screws to the desk or sits on rubber feet.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Servo window | 41.1 × 20.1 | +0.3/−0 | clearance 0.2/side | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |
| Servo pilot holes | Ø2.6 | ±0.1 | self-tap M3/servo screw | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |
| Servo pilot pattern | 48.5 × 10.0 | ±0.2 | matches MG996R tabs | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |
| DC jack hole | Ø11.4 | +0.3/−0 | panel jack Ø11 thread | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |
| Overall | 110 × 104 × 40 | ±0.5 | free | none (clearance built into the model) | default from fdm-design-rules / hobby_parts.py |

Clearances: servo windows +0.4 total (0.2/side), horn pockets +0.5 total, M3 clearance Ø3.4, self-tap pilots Ø2.6 (M3/MG996R screws) and Ø1.8 (SG90 screws). Source: fdm-design-rules defaults, recorded in tools/hobby_parts.py.

## Parameters exposed by model.py
BX, BY, H, WALL, PLATE_T, CORNER_R, PILLAR_D, PILLAR_HOLE, SERVO_BOSS_D, SERVO_BOSS_L, RING_PILOT_R, RING_PILOT_ANG, CRADLE_PILOTS, CRADLE_BOSS_D, CRADLE_BOSS_L, PILOT, USB_SLOT, USB_Y, USB_Z, JACK_D, JACK_Y, JACK_Z, CABLE_SLOT

## Risks
- Wall openings printed as overhangs → 45° roofs / teardrop pointing up in print
- Self-tapping pilots crack the plate → servo screw bosses lengthen the grip to 10 mm; PETG is tough

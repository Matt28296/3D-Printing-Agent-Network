# Design brief: Rover lid / electronics deck

Job: 20261026-rover-lid · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG for every rover part: tough against knocks, wears acceptably on steel pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, underside on the bed; seat ledges and rails rise from the top face. Deck bending along the layers.

## Concept
3 mm deck screwed onto the chassis columns, carrying the ESP32 DevKit (pins down through a window, PCB on end ledges, held by zip ties over its pin-free ends), a 170-point mini breadboard with the TB6612FNG driver and the 5 V buck, and a Ø10 cable hole.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| ESP32 pocket width | 29.7 | +0.3/−0 | 0.6 clearance | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Screw holes | Ø3.4 | +0.2/−0 | M3 clearance | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: M3 bolt clearance Ø3.4; wheel and idler running bores Ø3.5 on M3 bolts (0.5 mm running clearance); sprocket hub Ø10 in a Ø10.5 journal; lid-screw pilots Ø2.6; M3 nut traps 5.8 across flats; N20 D-bore Ø3.0 / flat 2.5 (press fit, + M2 set screw); track pin holes Ø2.2 in the centre knuckle (pin runs) and Ø2.0 in the outer knuckles (pin gripped), teardrops. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row).

## Parameters exposed by model.py
HOLE_COMP, T, CORNER_R, SCREWS, SCREW_D, BOARDS, USB_END_X, LEDGE_H, CLR, RAIL_W, HALF, ROW_KEEP, END_LEDGE, TIE_SLOT, TIE_FROM_END, CABLE_HOLE, BED_CHAMFER

## Risks
- Zip ties across the pin rows would short or bend pins (DFM round 1) → ties cross the board 1.2 mm from its ends
- Jumper housings under the ESP32 → window spans both pin rows; housings end ≥ 4 mm above the battery

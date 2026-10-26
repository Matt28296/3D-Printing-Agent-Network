# Design brief: Rover lid / electronics deck

Job: 20261026-rover-lid · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG for every rover part: tough against knocks and drops, wears acceptably at the track pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, underside on the bed; seat ledges and rails rise from the top face. Deck bending along the layers.

## Concept
3 mm deck screwed onto the chassis columns, carrying the ESP32 DevKit (pins down through a window, PCB on end ledges, zip tie), a 170-point mini breadboard with the TB6612FNG driver and the 5 V buck, and a Ø10 cable hole.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| ESP32 pocket width | 29.7 | +0.3/−0 | 0.6 clearance | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Screw holes | Ø3.4 | +0.2/−0 | M3 clearance | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: M3 bolt clearance Ø3.4, wheel/idler running bores Ø3.2 on M3 bolts, lid-screw pilots Ø2.6, M3 nut traps 5.8 across flats, N20 D-bore Ø3.1 with a 2.6 flat (press fit + M2 grub screw), pin holes Ø1.9 for 1.75 mm filament. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row).

## Parameters exposed by model.py
HOLE_COMP, T, CORNER_R, SCREWS, SCREW_D, BOARDS, USB_END_X, LEDGE_H, CLR, RAIL_W, HALF, ROW_KEEP, END_LEDGE, TIE_SLOT, BB_X0, CABLE_HOLE, BED_CHAMFER

## Risks
- Jumper housings under the ESP32 → window spans both pin rows; housings end ≥ 4 mm above the battery

# Design brief: Rover chassis (tub)

Job: 20261026-rover-chassis · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG for every rover part: tough against knocks and drops, wears acceptably at the track pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Floor on the bed, walls vertical. Wheel-bolt bending and wall bending under drops put the wall roots across the layers; walls are 3 mm + 3 mm bosses at every bolt.

## Concept
Open-top tub, 154 × 76 × 40 mm, that holds both N20 drive motors (gearbox face screwed to the side walls, can on a cradle with a zip tie), the M3 axle bolts for 4 road wheels and 2 idlers (nuts in traps in the walls' outer faces; idler bolts in an 8 mm tension slot), the 2 × 18650 holder (velcro strap through floor slots), a mini rocker switch (rear wall) and an HC-SR04 (front wall).

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Sprocket-to-idler axle distance | 120.0 (slot ±4) | ±0.3 | track length 34 × 10 | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Axle height | Z 20.68 | ±0.3 | track meets the ground | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| N20 face holes | 2 × Ø1.6 + 0.4 clearance, 9 apart | ±0.15 | clearance | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Nut traps | 5.8 AF × 2.6 deep | +0.2/−0 | M3 nut push fit | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: M3 bolt clearance Ø3.4, wheel/idler running bores Ø3.2 on M3 bolts, lid-screw pilots Ø2.6, M3 nut traps 5.8 across flats, N20 D-bore Ø3.1 with a 2.6 flat (press fit + M2 grub screw), pin holes Ø1.9 for 1.75 mm filament. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row).

## Parameters exposed by model.py
HOLE_COMP, CORNER_R, BED_CHAMFER, BOLT_D, NUT_AF, NUT_CLR, NUT_DEPTH, BOSS_T, BOSS_R, IDLER_BOSS, CRADLE_HALF_X, TIE_W, TIE_D, COLUMN_D, LID_PILOT, PILOT_DEPTH, COLUMNS, BATT_X0, STRAP_W, STRAP_L, SWITCH_Z, SENSOR_Z, SENSOR_CLR (+ rover_frame.py)

## Risks
- Horizontal wall holes → teardrops (motor, bolts, sensors) and a 45° roof (switch)
- Nut traps in vertical walls → flats top and bottom, 3.2 mm flat ceiling

# Design brief: Rover chassis (tub)

Job: 20261026-rover-chassis · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG for every rover part: tough against knocks, wears acceptably on steel pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Floor on the bed, walls vertical. Every hole in a wall is horizontal, so each is a teardrop or has a 45° roof; every inward boss runs down to the floor. Wheel-bolt bending and wall bending in a drop put the wall roots across the layers: 4.5 mm walls, Ø20 bosses, 3 mm floor fillets.

## Concept
Open-top tub, 154 × 76 × 40 mm, 4.5 mm walls. Holds both N20 drive motors in cradles (cheeks, a rear stop and a zip-tie tunnel; no face screws), with each sprocket hub running in a 6 mm journal in the side wall so the track loads go into the wall, not the N20 shaft. Carries the axle bolts for 4 road wheels (M3 × 45) and 2 idlers (M3 × 35) (heads inside, nuts in traps in the outer faces; idler bolts in an 8 mm tension slot with a sliding nut), the 2 × 18650 holder (velcro strap through floor slots), a mini toggle switch (rear wall) and an HC-SR04 (front wall).

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Sprocket-to-idler axle distance | 120.0 (slot ±4) | ±0.3 | track length 34 × 10 | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Axle height | Z 20.68 | ±0.3 | track meets the ground | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Journal | Ø10.5 printed, 6 long | +0.15/−0 | running fit on the Ø10 sprocket hub | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Nut traps | 5.8 AF × 2.6 deep | +0.2/−0 | M3 nut push fit | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: M3 bolt clearance Ø3.4; wheel and idler running bores Ø3.5 on M3 bolts (0.5 mm running clearance); sprocket hub Ø10 in a Ø10.5 journal; lid-screw pilots Ø2.6; M3 nut traps 5.8 across flats; N20 D-bore Ø3.0 / flat 2.5 (press fit, + M2 set screw); track pin holes Ø2.2 in the centre knuckle (pin runs) and Ø2.0 in the outer knuckles (pin gripped), teardrops. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row).

## Parameters exposed by model.py
HOLE_COMP, CORNER_R, BED_CHAMFER, BOLT_D, NUT_AF, NUT_CLR, NUT_DEPTH, BOSS_IN, ROAD_BOSS_R, IDLER_BLOCK, JOURNAL_CLR, JOURNAL_BOSS_HALF, CRADLE_HALF_X, REAR_STOP, COLUMNS, STRAP_W, STRAP_L, STRAP_Y, FLOOR_FILLET, SENSOR_Z, SENSOR_CLR (+ rover_frame.py: WALL, JOURNAL_BOSS, MOTOR_FACE_Y, HUB_D, ...)

## Risks
- N20 shaft overload in a drop (strength round 1) → Ø10 sprocket hub in a 6 mm wall journal; the shaft carries torque only
- Face screws into the N20 gearbox (M1.6) → replaced by a cradle with cheeks, a rear stop and a zip tie
- Thin walls (strength round 1) → 4.5 mm walls, Ø20 bosses, idler block, floor fillets
- Snap-in rocker needs a 1.5 mm wall → threaded mini toggle (Ø6.4 hole)

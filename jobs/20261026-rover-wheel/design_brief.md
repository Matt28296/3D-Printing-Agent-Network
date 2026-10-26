# Design brief: Road wheel (×4)

Job: 20261026-rover-wheel · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG for every rover part: tough against knocks and drops, wears acceptably at the track pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Outer flange face on the bed, hub up: one 45° cone faces up, the other is a 45° overhang.

## Concept
Carries the rover on the bottom track run (rim r 13.1 meets the links' inner faces) with 45° V-flanges that keep the track centred.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Rim radius | 13.10 | ±0.15 | meets the link inner face 13.18 below the axle | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Running bore | Ø3.2 printed | +0.15/−0 | running fit on M3 | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: M3 bolt clearance Ø3.4, wheel/idler running bores Ø3.2 on M3 bolts, lid-screw pilots Ø2.6, M3 nut traps 5.8 across flats, N20 D-bore Ø3.1 with a 2.6 flat (press fit + M2 grub screw), pin holes Ø1.9 for 1.75 mm filament. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row).

## Parameters exposed by model.py
HOLE_COMP, RIM_R, RIM_HALF, CONE_RISE, FLANGE_FLAT, BORE, HUB_R, INNER_FACE_Z

## Risks
- 32 mm bridge with the hub down (mesh check round 1) → printed flange face down

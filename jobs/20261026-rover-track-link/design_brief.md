# Design brief: Track link (×68, 34 per side)

Job: 20261026-rover-track-link · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG for every rover part: tough against knocks and drops, wears acceptably at the track pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Inner face on the bed, grousers up, 34 per plate. Pin-hole tear-out acts in the layer plane; the pin axis is along the bed.

## Concept
10 mm-pitch link with a centre knuckle at the rear hinge and two outer knuckles at the front, pinned with 1.75 mm filament; the centre notch takes a sprocket tooth; grousers on the outer face.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Pitch | 10.00 | ±0.1 | matches the sprocket | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Pin hole | Ø1.9 printed | +0.1/−0 | free running on 1.75 filament | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Knuckle gaps | 0.5 axial, 0.4 radial | min | free hinge | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: M3 bolt clearance Ø3.4, wheel/idler running bores Ø3.2 on M3 bolts, lid-screw pilots Ø2.6, M3 nut traps 5.8 across flats, N20 D-bore Ø3.1 with a 2.6 flat (press fit + M2 grub screw), pin holes Ø1.9 for 1.75 mm filament. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row).

## Parameters exposed by model.py
HOLE_COMP, PIN_CLR, KN_R, KN_GAP, CENTRE_HALF, OUTER_IN, HALF_W, NOTCH_HALF, NOTCH_X0, GROUSER_H, GROUSER_X (+ rover_frame.py)

## Risks
- Small horizontal pin holes (Ø2.1) → round, small enough to print
- Knuckle undersides near the bed: 6 % overhang area, curved, within 45° above 0.9 mm

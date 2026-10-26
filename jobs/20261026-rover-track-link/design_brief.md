# Design brief: Track link (×68, 34 per side)

Job: 20261026-rover-track-link · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG for every rover part: tough against knocks, wears acceptably on steel pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Inner face on the bed (0.3 mm chamfer on its edges; the knuckles touch the bed tangentially), grousers up, 34 per plate. Pin-hole tear-out runs along the layers in load direction but its shear planes cross the layers (strength round 1); teardrop pin holes.

## Concept
10 mm-pitch link with a centre knuckle at the rear hinge and two outer knuckles at the front, pinned with 2 mm steel rod: the pin runs free in the centre knuckle (Ø2.2) and is gripped by the outer knuckles (Ø2.0), so it can't walk out. The centre notch takes a sprocket tooth; grousers on the outer face.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Pitch | 10.00 | ±0.1 | matches the sprocket | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Centre-knuckle hole | Ø2.2 printed | +0.1/−0 | running fit on Ø2 rod | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Outer-knuckle holes | Ø2.0 printed | +0.05/−0.05 | grip fit on Ø2 rod | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Knuckle gaps | 0.5 axial, 0.4 radial | min | free hinge | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: M3 bolt clearance Ø3.4; wheel and idler running bores Ø3.5 on M3 bolts (0.5 mm running clearance); sprocket hub Ø10 in a Ø10.5 journal; lid-screw pilots Ø2.6; M3 nut traps 5.8 across flats; N20 D-bore Ø3.0 / flat 2.5 (press fit, + M2 set screw); track pin holes Ø2.2 in the centre knuckle (pin runs) and Ø2.0 in the outer knuckles (pin gripped), teardrops. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row).

## Parameters exposed by model.py
HOLE_COMP, PIN_RUN_CLR, PIN_GRIP_CLR, KN_R, KN_GAP, CENTRE_HALF, OUTER_IN, HALF_W, NOTCH_HALF, NOTCH_X0, GROUSER_H, GROUSER_X, BED_CHAMFER (+ rover_frame.py: PIN_D, P, LINK_T, TRACK_W)

## Risks
- Filament pins bent in a drop (strength round 1) → 2 mm steel rod
- Tight running fit (DFM round 1) → Ø2.2 running / Ø2.0 grip, teardrops
- Elephant's foot closing the 0.5 mm knuckle gaps → 0.3 bed chamfer + slicer EFC 0.2

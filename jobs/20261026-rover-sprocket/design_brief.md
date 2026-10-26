# Design brief: Drive sprocket (×2)

Job: 20261026-rover-sprocket · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG for every rover part: tough against knocks and drops, wears acceptably at the track pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Outer disc face on the bed, hub up. Tooth bending and bore bearing act in the layer plane.

## Concept
10-tooth sprocket (pitch radius 16.18) on the N20's D-shaft, driving the track through notches in the links; hub reaches back to 0.5 mm from the chassis wall.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| D-bore | Ø3.1 / flat 2.6 | +0.1/−0 | press fit on the N20 shaft | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Pitch radius | 16.18 | ±0.15 | matches 10 mm link pitch | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: M3 bolt clearance Ø3.4, wheel/idler running bores Ø3.2 on M3 bolts, lid-screw pilots Ø2.6, M3 nut traps 5.8 across flats, N20 D-bore Ø3.1 with a 2.6 flat (press fit + M2 grub screw), pin holes Ø1.9 for 1.75 mm filament. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row).

## Parameters exposed by model.py
HOLE_COMP, DISC_HALF, DISC_R, TOOTH_TIP_R, TOOTH_BASE_W, TOOTH_TIP_W, PHASE_DEG, HUB_D, HUB_Z0, SHAFT_END_Z, BORE_DEPTH, GRUB_PILOT, BORE, ROUND_BORE

## Risks
- Tooth flank at the run-out (assembly check round 1) → tooth slimmed, notch lengthened

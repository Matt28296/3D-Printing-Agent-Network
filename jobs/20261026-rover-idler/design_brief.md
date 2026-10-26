# Design brief: Idler (×2)

Job: 20261026-rover-idler · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG for every rover part: tough against knocks and drops, wears acceptably at the track pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Outer disc face on the bed, hub up. Bearing on the bore is in the layer plane.

## Concept
The sprocket's toothed geometry with a round Ø3.4 running bore, free on the M3 bolt in the chassis's tension slot, so the track wraps it exactly like the sprocket.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Running bore | Ø3.2 printed (Ø3.4 CAD) | +0.15/−0 | running fit on M3 | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: M3 bolt clearance Ø3.4, wheel/idler running bores Ø3.2 on M3 bolts, lid-screw pilots Ø2.6, M3 nut traps 5.8 across flats, N20 D-bore Ø3.1 with a 2.6 flat (press fit + M2 grub screw), pin holes Ø1.9 for 1.75 mm filament. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row).

## Parameters exposed by model.py
ROUND_BORE (+ the sprocket model's parameters)

## Risks
- Bore wear on bolt threads → use bolts with a plain shank where the idler runs, or a short Ø3 brass tube

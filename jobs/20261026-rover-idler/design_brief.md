# Design brief: Idler (×2)

Job: 20261026-rover-idler · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG for every rover part: tough against knocks, wears acceptably on steel pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Outer disc face on the bed, hub up. Bearing on the bore is in the layer plane.

## Concept
The sprocket's toothed geometry with a round Ø3.5 running bore and a shorter hub, free on the M3 × 45 bolt in the chassis's tension slot, so the track wraps it exactly like the sprocket.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Running bore | Ø3.5 printed (Ø3.7 CAD) | +0.15/−0 | running fit on M3, 0.5 clearance | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: M3 bolt clearance Ø3.4; wheel and idler running bores Ø3.5 on M3 bolts (0.5 mm running clearance); sprocket hub Ø10 in a Ø10.5 journal; lid-screw pilots Ø2.6; M3 nut traps 5.8 across flats; N20 D-bore Ø3.0 / flat 2.5 (press fit, + M2 set screw); track pin holes Ø2.2 in the centre knuckle (pin runs) and Ø2.0 in the outer knuckles (pin gripped), teardrops. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row).

## Parameters exposed by model.py
ROUND_BORE (+ the sprocket model's parameters)

## Risks
- Bore wear on bolt threads → bolts with a plain shank where the idler runs, or a short Ø3 brass tube

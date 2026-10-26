# Design brief: Track link (×68 + 2 spares, 34 per side)

Job: 20261026-rover-track-link · design-lead (round 3) · 2026-10-26

## Material
PETG for every rover part: tough against knocks, wears acceptably on steel pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Inner face on the bed (0.3 mm chamfer on its edges; the knuckles touch the bed tangentially), grousers up, 34 per plate. Pin-hole tear-out runs along the layers in the load direction, but its shear planes cross the layers (strength round 1). Teardrop pin holes.

## Concept
10 mm-pitch link with a centre knuckle at the rear hinge and two outer knuckles at the front, pinned with Ø2 steel pins.
- **Running hole (centre knuckle):** Ø2.3 printed, a 0.3 sliding fit.
- **Grip holes (outer knuckles):** Ø2.0 printed. The pins can't walk out.
- **Tooth notch:** the centre notch takes a sprocket tooth.
- **Grousers:** on the outer face.

**Round 3:** PIN_RUN_CLR 0.2 → 0.3 (DFM round 2 fix 1). That opens the running hole to Ø2.5 CAD, about Ø2.3 printed, a sliding fit by fdm-design-rules §3.
- **Wall round the running hole:** 3.0 − 1.25 = 1.75 mm, which still holds four 0.45 mm lines at PrusaSlicer's 0.41 mm spacing (1.68).
- **Wall above the teardrop tip (up in print):** 3.0 − 1.77 = 1.23 mm, still ≥ 0.9.
- **Proof test:** the strength round-2 pin-pressing check stays in spec §8.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Pitch | 10.00 | ±0.1 | matches the sprocket | — | rover_frame.P |
| Centre-knuckle hole | Ø2.3 printed (Ø2.5 CAD) | +0.1/−0 | sliding fit on the Ø2 pin | PIN_RUN_CLR 0.3 + HOLE_COMP +0.2 | DFM round 2 fix 1; HOLE_COMP default (no library row) |
| Outer-knuckle holes | Ø2.0 printed (Ø2.2 CAD) | +0.05/−0.05 | grip fit on the Ø2 pin | PIN_GRIP_CLR 0 + HOLE_COMP +0.2 | default |
| Knuckle wall | 1.75 | min | 4 extrusion lines | — | DFM round 2 |
| Knuckle gaps | 0.5 axial, 0.4 radial | min | free hinge | — | — |

Printed targets for the whole rover: see the chassis brief.

## Parameters exposed by model.py
HOLE_COMP, PIN_RUN_CLR, PIN_GRIP_CLR, KN_R, KN_GAP, CENTRE_HALF, OUTER_IN, HALF_W, NOTCH_HALF, NOTCH_X0, GROUSER_H, GROUSER_X, BED_CHAMFER (+ rover_frame.py: PIN_D, P, LINK_T, TRACK_W). `cad_checks.py` proves them on the geometry.

## Risks
- **Filament pins bent in a drop** (strength round 1): Ø2 steel pins.
- **Tight running fit** (DFM rounds 1–2): Ø2.3 printed running hole, Ø2.0 grip, teardrops.
- **Outer knuckle split while pressing a pin:** proof test 1 on a 5-link chain from the first plate; fallback PIN_GRIP_CLR +0.05 with CA.
- **Elephant's foot closing the 0.5 mm knuckle gaps:** 0.3 bed chamfer + slicer EFC 0.2.

# Design brief: Drive sprocket (×2)

Job: 20261026-rover-sprocket · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG for every rover part: tough against knocks, wears acceptably on steel pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Outer disc face on the bed, hub up. Tooth bending, bore bearing and hub bearing act in the layer plane.

## Concept
10-tooth sprocket (pitch radius 16.18, 45° tooth-root chamfers) on the N20's D-shaft. Its Ø10 hub runs back through the 6 mm journal in the chassis wall to 0.5 mm from the gearbox face, so the wall carries the track loads and the shaft only the torque; the D-bore takes 9.5 mm of the shaft.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| D-bore | Ø3.0 / flat 2.5 printed | +0.1/−0 | press fit on the N20 shaft | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Hub | Ø10.0 | −0.1/+0 | runs in the Ø10.5 journal | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Pitch radius | 16.18 | ±0.15 | matches the 10 mm link pitch | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: M3 bolt clearance Ø3.4; wheel and idler running bores Ø3.5 on M3 bolts (0.5 mm running clearance); sprocket hub Ø10 in a Ø10.5 journal; lid-screw pilots Ø2.6; M3 nut traps 5.8 across flats; N20 D-bore Ø3.0 / flat 2.5 (press fit, + M2 set screw); track pin holes Ø2.2 in the centre knuckle (pin runs) and Ø2.0 in the outer knuckles (pin gripped), teardrops. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row).

## Parameters exposed by model.py
HOLE_COMP, DISC_HALF, DISC_R, TOOTH_TIP_R, TOOTH_BASE_W, TOOTH_TIP_W, ROOT_CHAMFER, PHASE_DEG, HUB_Z0_D, HUB_Z0_ROUND, SHAFT_END_Z, D_CLEARANCE, GRUB_PILOT, GRUB_Y, BORE, ROUND_BORE, BED_CHAMFER

## Risks
- N20 shaft bending in a drop (strength round 1) → hub journal in the wall
- Tooth flank at the run-out (assembly check round 1) → tooth slimmed, notch lengthened
- Set-screw pilot horizontal → teardrop pointing up in print

# Design brief: Road wheel (×4)

Job: 20261026-rover-wheel · design-lead (round 3) · 2026-10-26

## Material
PETG for every rover part: tough against knocks, wears acceptably on steel pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Outer flange face on the bed, hub up: one 45° cone faces up, the other is a 45° overhang. 5 perimeters, so the bore and rim are solid walls. Round 3:
- **Bed chamfer:** `chamfer_bottom(part, 0.4)` after the flip puts a 0.4 × 45° chamfer on every bed edge, the outer flange edge and the bore mouth (DFM round 2 fix 1).
- **Elephant's foot:** `elefant_foot_compensation` 0.2 is in print_requirements.json "min" and in slice_plan.json.

## Concept
Carries the rover on the bottom track run (rim r 13.1 meets the links' inner faces) with 45° V-flanges that keep the track centred. Runs on its M3 × 50 bolt (class 12.9, fully threaded). The track plane stays at Y 55: the round-3 drivetrain kept it there, so the wheels keep both flanges.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Rim radius | 13.10 | ±0.15 | meets the link inner face 13.18 below the axle | — | rover_frame.STRAIGHT_IN − 0.08 |
| Running bore | Ø3.5 printed (Ø3.7 CAD) | +0.15/−0 | running fit on M3, 0.5 clearance | HOLE_COMP +0.2 | default from fdm-design-rules (no library row) |
| Bed chamfer | 0.4 × 45° | ±0.1 | elephant's-foot relief | + slicer EFC 0.2 | DFM round 2 fix 1 |

Printed targets for the whole rover: see the chassis brief.

## Parameters exposed by model.py
HOLE_COMP, RIM_R, RIM_HALF, CONE_RISE, FLANGE_FLAT, BORE, HUB_R, INNER_FACE_Z, BED_CHAMFER. `cad_checks.py` proves them on the geometry.

## Risks
- **32 mm bridge with the hub down** (mesh check round 1): printed flange face down instead.
- **Bore bearing** (strength round 1): 5 perimeters, 0.5 mm running clearance.
- **Flared first layer:** bed chamfer + EFC 0.2.

# Design brief: Claw cover (front plate, top wall, upper lip)

Job: 20261026-arm-claw-cover · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG, as for the rest of the arm: tough, low creep under the servo's holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Standing on its −y end: the whole side profile lies in the bed plane, so every rack bearing face (front plate inner face, top wall underside, lip face) is a vertical wall and comes out straight and smooth. Slot A's closed end bridges 5.5 mm; the screw holes are teardrops pointing up. Bending of the front plate and top wall runs along the layers. 64 mm tall on a 203 mm² footprint: use a brim.

## Concept
Closes both rack channels: the front plate holds both racks forward and carries the two neck slots (A open at −y, B open at +y, so the jaws slide in from the ends), the top wall holds rack A down against the pinion's separating force, and the upper lip backs rack A. A Ø5 hole reaches the pinion's clamp screw. The camera mount sits on its top wall.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Front plate inner face | x 27.65 | ±0.15 | 0.25 sliding gap to the racks | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Top wall underside | z 39.0 | ±0.15 | 0.25 gap over rack A | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Lip front face | x 19.15 | ±0.15 | 0.25 gap behind rack A | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Neck slots | 5.5 wide | +0.2/−0 | 0.25 around the 5 mm necks | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: MG90S window +0.4 side / +0.2 end, wrist horn pocket +0.5, pinion horn pocket +0.3 (gear backlash adds up), M2 clamp holes Ø2.4, M3 clearance Ø3.4, M3 self-tap pilots Ø2.5, MG90S tab pilots Ø1.5, 1/4"-20 clearance Ø6.85. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row). Sliding clearance around the racks 0.25 mm; gears module 1, 20°, each member 0.1 mm thinner (0.2 mm backlash). Gears and racks are drawn in the bed plane (axis vertical) so the involute is as accurate as XY.

## Parameters exposed by model.py
HOLE_COMP, BED_CHAMFER, TO_PRINT; shared: claw_frame.py (X_F0, X_F1, Z_TOP0, Z_TOP1, RAIL_IN, RAIL_X1, NECK_Z, SLOT_CLR, ACCESS_D, TOP_SCREWS, FRONT_SCREWS, M3_CLEAR)

## Risks
- Long slots in a vertical wall would bridge 32 mm → printed standing on its end, slots vertical
- Tall thin print → brim, PETG first layer

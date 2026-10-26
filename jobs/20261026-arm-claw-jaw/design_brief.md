# Design brief: Claw jaw (rack + finger), ×2

Job: 20261026-arm-claw-jaw · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG, as for the rest of the arm: tough, low creep under the servo's holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Standing on the rack's back face, finger up: the rack teeth are drawn in the bed plane. The grip force bends the neck and the blade root ACROSS the layers (the finger grows in Z); the 14 × 5 neck and the 45° flares are sized for the across-layer allowable. Sideways pushes bend the blade along its layers. The grooves and the 45° flares print without support.

## Concept
One-piece rack (module 1, 44 mm, teeth along y), neck (14 × 5 mm, passes through the cover slot) and finger blade (6 mm thick, 45 mm long, 20 mm-tall grip face). The grip face has 0.6 mm cross-grooves and a 1.5 mm V-notch along the centre line for pens, rods and wires. Two identical copies: jaw B is jaw A turned 180° about the pinion axis.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Rack pitch line to back face | 7.25 | ±0.15 | sets the mesh | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Rack face width | 8.0 | −0.15/+0 | 0.25 sliding gaps | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Neck | 14 × 5 | ±0.15 | 0.25 in the slot | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Grip face | y 0 closed | ±0.2 | jaws meet | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: MG90S window +0.4 side / +0.2 end, wrist horn pocket +0.5, pinion horn pocket +0.3 (gear backlash adds up), M2 clamp holes Ø2.4, M3 clearance Ø3.4, M3 self-tap pilots Ø2.5, MG90S tab pilots Ø1.5, 1/4"-20 clearance Ø6.85. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row). Sliding clearance around the racks 0.25 mm; gears module 1, 20°, each member 0.1 mm thinner (0.2 mm backlash). Gears and racks are drawn in the bed plane (axis vertical) so the involute is as accurate as XY.

## Parameters exposed by model.py
TIP_CHAMFER, TIP_BEVEL, GROOVE_D, GROOVE_PITCH, GROOVE_X, NOTCH_D, GUSSET, RACK_LOC; shared: claw_frame.py (M, FACE_W, BACKLASH, RACK_BACK, RACK_Y, NECK_Z, NECK_Y, NECK_X1, BLADE_T, GRIP_HALF, BLADE_L, X_TIP)

## Risks
- Grip loads the neck across layers → 14 mm-long neck, 45° flares into a 6 mm blade
- Partial teeth at the rack ends make slivers → rack ends in tooth gaps (RACK_Y = −5π…9π)
- Rack and finger in one part → no screws to loosen; jaws are identical (one job, 2 copies)

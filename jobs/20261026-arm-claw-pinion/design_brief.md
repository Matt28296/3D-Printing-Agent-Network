# Design brief: Claw pinion (18 teeth, module 1)

Job: 20261026-arm-claw-pinion · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG, as for the rest of the arm: tough, low creep under the servo's holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Back face (horn pocket) on the bed, axis vertical: the involute profile is drawn in the bed plane and tooth bending runs along the layers. The pocket ceiling bridges ≤ 7.7 mm. Print solid (100 % infill): the part is small and the teeth carry the grip.

## Concept
Spur gear on the claw MG90S: module 1, 18 teeth, 20°, pitch Ø18, 8 mm wide. Turns both racks in opposite directions, so the jaws open and close symmetrically: 3.18° of servo per mm of jaw gap, 0–44 mm in 140°. The servo's double-arm horn, both arms cut 5.5 mm from the centre, sits 2 mm deep in its back face.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Teeth | m 1, z 18, 20°, 0.1 thinned | profile in the bed plane | 0.2 backlash with the racks | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Horn pocket | hub + stubs to r 5.75 | +0.3 clearance | snug on the trimmed horn | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Counterbore | Ø4.4 × 1.6 | +0.2/−0 | M2 head below the face | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: MG90S window +0.4 side / +0.2 end, wrist horn pocket +0.5, pinion horn pocket +0.3 (gear backlash adds up), M2 clamp holes Ø2.4, M3 clearance Ø3.4, M3 self-tap pilots Ø2.5, MG90S tab pilots Ø1.5, 1/4"-20 clearance Ø6.85. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row). Sliding clearance around the racks 0.25 mm; gears module 1, 20°, each member 0.1 mm thinner (0.2 mm backlash). Gears and racks are drawn in the bed plane (axis vertical) so the involute is as accurate as XY.

## Parameters exposed by model.py
HOLE_COMP, HEAD_D, HEAD_H, POCKET_CLR, BED_CHAMFER; shared: claw_frame.py (M, Z_TEETH, FACE_W, BACKLASH, PINION_HORN, HORN_TRIM_R)

## Risks
- The full horn is wider than the gear → horn arms cut to 5.5 mm (BUILD_GUIDE step with a photo-free description); 2 mm wall to the tooth roots
- Small teeth → module 1 (4 extrusion widths per tooth), solid print, 0.25 bed chamfer

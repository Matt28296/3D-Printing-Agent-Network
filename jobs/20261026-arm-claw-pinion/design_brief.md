# Design brief: Claw pinion (20 teeth, module 1)

Job: 20261026-arm-claw-pinion · design-lead · 2026-10-26 (round 3: deep reviews 01 B2 and 03 SYS-01 / SYS-08, pinion DFM and strength round 1)

## Material
PETG, as for the rest of the arm: tough, low creep under the servo's holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, 12.5 MPa across layers).

## Orientation
Back face (horn pocket) on the bed, axis vertical: the involute profile is drawn in the bed plane and tooth bending runs along the layers. The pocket ceiling bridges ≤ 7.5 mm (mesh_check). Print solid (100 % infill): the part is small and the teeth carry the grip. 0.25 mm 45° chamfer on the bed face with the tooth outline included (`tools/gears.py` chamfer: a true 45° band, no fallback). It narrows each tooth tip on the first layers by design.

## Concept
Spur gear on the claw MG90S: module 1, 20 teeth (was 18), 20°, pitch Ø20, 10 mm wide (was 8), r 0.38 root fillets, tips topped 0.15 m (outside Ø21.7, tip clearance 0.40 to the rack roots), each tooth 0.10 thinner at the pitch line, the racks' 0.25: 0.35 backlash per mesh (SYS-08 asks 0.3–0.4; `claw_sequence_check.py` measures it). The pinion keeps the thicker teeth because gears.py draws its flanks radial below the base circle (r 9.40 > root 8.75), so its critical chord (1.63 mm at r 9.0) is the weak one: Lewis on the actual filleted, topped tooth, 21.6 N at the tip, gives SF 3.25 at the one-jaw stall (3.0 required) and 6.5 for the both-jaw grip; the even 0.175/0.175 split gave 2.96. 21.6 N per rack at the MG90S stall; 2.865° of servo per mm of jaw gap, 0–44 mm in 126°. The servo's double-arm horn, both arms cut 5.5 mm from the centre and filed round, sits 2 mm deep in the back face with a light 0.1 mm fit that centres the pinion (SYS-08; was 0.3). An M2 × 12 + Ø6 washer in a 1.7 mm counterbore clamps it with a 6.3 mm floor: 4.6 mm into the spline like every other horn clamp (01 S2). With the MG90S's real height (01 B2) its back face sits at claw x 22.6.
SYS-01: the pinion goes on LAST, pushed axially through the cover's Ø22.6 pass-through with both jaws parked fully open (`g 44`), and comes off first. `claw_sequence_check.py` sweeps it in as one exact solid (its outline swept 70 mm along the axis): 0 mm³ against both jaws, the cover, the frame, the servo and the screws. It can come out once the claw is ≥ 22 mm open.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Teeth | m 1, z 20, 20°, each 0.10 thinner, root fillet r 0.38, tips topped 0.15 | profile in the bed plane | 0.35 backlash per mesh | — | tools/gears.py, claw_frame.py PINION_BACKLASH |
| Outside diameter | 21.7 | ±0.1 | 0.45 radial in the pass-through (printed) | — | claw_frame.py |
| Horn pocket | hub Ø7.2 + stubs to r 5.5, 2 deep | +0.1 fit | centres the pinion | HOLE_COMP +0.2 | deep review 03 SYS-08 |
| Counterbore | Ø6.2 printed × 1.7 | +0.2/−0 | Ø6 washer, 6.3 mm floor | HOLE_COMP +0.2 | deep review 01 S2 |

measure_holes (geometry.json): Ø2.6 clamp hole, Ø6.4 counterbore.

## Parameters exposed by model.py
HOLE_COMP, POCKET_CLR, BED_CHAMFER, CB_D, CB_H; shared: claw_frame.py (M, Z_TEETH, FACE_W, BACKLASH, TIP_RELIEF, PINION_ROOT_FILLET, PINION_HORN, HORN_TRIM_R, PINION_CB_D, PINION_FLOOR)

## Risks
- The full horn is wider than the gear → horn arms cut to 5.5 mm (BUILD_GUIDE §4 step 11); ≈3.1 mm of ring between the pocket and the tooth roots (r 8.75).
- Small teeth → module 1 (4 extrusion widths per tooth), solid print, bed chamfer.
- The light pocket fit may need a drop of CA once the run is smooth (BUILD_GUIDE step 12).

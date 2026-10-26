# Design brief: Claw jaw (rack + finger), ×2

Job: 20261026-arm-claw-jaw · design-lead · 2026-10-26 (round 3: deep review 03 SYS-01 / SYS-08, jaw DFM and strength round 1)

## Material
PETG, as for the rest of the arm: tough, low creep under the servo's holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, 12.5 MPa across layers).

## Orientation
Standing on the rack's back end (claw x = print Z, the x 22.6 face on the bed), finger up: the rack teeth are drawn in the bed plane, so tooth bending runs along the layers. **Every bending of the neck and the finger, in either direction, puts its stress across the layers** (DFM round 1, item 4): the grip force, the sideways push and the yaw-stall sweep all do. The neck and finger are sized for the 12.5 MPa across-layer allowable (strength round 1's candidate C). The grooves, the gusset and the finger's 45° edges print without support. No brim (it would fill the tooth gaps: `print_requirements.json` max `brim_width` 0); 0.3 mm bed chamfer, tooth outline included (`tools/gears.py`), which narrows the tooth tips to ≈0.2 mm over the first 0.3 mm: mesh_check's 20 thin-wall hits are those tips, all at print z ≤ 0.2.

## Concept
One piece: a module-1 rack (56.5 mm along y, ends in tooth gaps, 10 mm face, 10 mm solid behind the roots), a 20 × 10 mm neck on that solid back with r 4 root fillets at both y edges, and a finger 12 mm thick for 20 mm, tapering to 6 mm over 15 mm, 45 mm long, joined to the neck by a full-height 45° gusset in plan, with r 3 fillets at its re-entrant kinks. The finger's top runs flat at the neck's top for 15 mm, then 45° down to the grip zone (lighter, and the camera sees the fingertips over it). Grip face: 0.6 mm V-grooves across, 1.5 mm V-notch along the centre line, a 3.5 mm bevel on the tip's outer face. Two identical copies: jaw B is jaw A turned 180° about the pinion axis.
SYS-08: each rack's back rides on its guide (RACK_SEAT 0), where the gear's separating force presses it, so both meshes run at the nominal centre distance. Teeth 0.25 thinner at the pitch line (0.35 backlash per mesh with the pinion's 0.10: the rack's 2.2 mm tooth roots take the bigger share, the pinion's weaker radial-flank roots the smaller one), tips topped 0.15 (0.70 mm tip land), root fillets r 0.30. A 2 mm 45° chamfer on the rack's back/front edge for y ≥ 4.5 clears the cover's r 2 corner fillet over the whole stroke (`claw_sequence_check.py`: 0 mm³ against the cover on the slide-in path and every 1 mm of stroke).
SYS-01: the jaws slide in from the open ends of their slots to fully open before the pinion goes in; nothing else has to pass the mesh.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Rack pitch line to back face | 11.25 | ±0.15 | sets the mesh (back on its guide) | — | claw_frame.py |
| Rack face width (x) | 10.0 | −0.15/+0 | 0.25 sliding gaps | — | claw_frame.py |
| Teeth | m 1, 20°, 0.25 thin, tips topped 0.15, root r 0.30 | in the bed plane | 0.35 backlash per mesh | — | tools/gears.py, claw_frame.py RACK_BACKLASH |
| Neck | 20 × 10 | ±0.15 | 0.25 in its slot | — | claw_frame.py |
| Grip face | y 0 closed | ±0.2 | jaws meet | — | claw_frame.py |

No holes (measure_holes: none).

## Parameters exposed by model.py
BED_CHAMFER, TIP_CHAMFER, TIP_BEVEL, GROOVE_D, GROOVE_PITCH, GROOVE_X, NOTCH_D, GUSSET, TAPER_FILLET, RACK_LOC; shared: claw_frame.py (M, FACE_W, BACKLASH, TIP_RELIEF, RACK_ROOT_FILLET, RACK_BACK, RACK_Y, RACK_EDGE_CHAMFER, RACK_EDGE_Y0, NECK_Z, NECK_Y, NECK_FILLET, NECK_X1, BLADE_T, BLADE_T_ROOT, TAPER_X0, TAPER_X1, GRIP_HALF, BLADE_L, X_TIP, GRIP_X0, TOP_KINK_X, KINK_FILLET)

## Risks
- Grip and side loads bend the neck and finger across the layers → candidate C's sections and fillets (strength round 1's model gives a lowest SF of ≈3.8 at the 21.6 N stall).
- Each jaw is 16.2 cm³ (round 1: 6.9) → 2.3 times the print time and ≈39 g for the pair at the end of the arm: the payload table includes it.
- Partial teeth at the rack ends make slivers → rack ends in tooth gaps (RACK_Y = −8π…10π).

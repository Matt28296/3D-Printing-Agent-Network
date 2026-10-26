# Design brief: Brio 4K camera mount (optional)

Job: 20261026-arm-camera-mount · design-lead · 2026-10-26 (round 3: deep reviews 01 S5/S6 and 03 SYS-13, camera-mount DFM and strength round 1)

## Material
PETG, as for the rest of the arm: tough, low creep under the servo's holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, 12.5 MPa across layers).

## Orientation
Standing on its −y end (`TO_PRINT = Rot(90, 0, 0)`): the side profile lies in the bed plane, so the tilted seat, the lip and its r 2 root fillet are vertical walls and need no support (mesh_check: 0 % overhang, no bridges, no thin walls). The seat cantilever and the lip bend along the layers. The 1/4" slot and the M3 holes are teardrops pointing up. 0.3 mm chamfer on the bed end, cut before the holes (DFM fix 1). 50 mm tall on a 184 mm² footprint: 5 mm outer brim (`print_requirements.json` min `brim_width` 5).

## Concept
Holds a Logitech Brio 4K (clip removed) on top of the claw, tilted 34° nose-down. The claw grew in round 2 (Z_TOP1 42 → 51.5, fingertips 7 mm further out), so the camera moved up and the placement was re-found with a 2D sight-line study in the claw's mid-plane (lens at the camera's (13.5, 0, 13.5), Logitech's vertical fields of view 52.2 / 43.3 / 34.7° for the 90 / 78 / 65° presets), with three constraints:
- the ray from the lens to the bottom of the grip zone at the tips (x 80.35, z ZS − 10) passes over the cover's chamfered front edge with ≥ 0.5° to spare (0.6°; round 1 had 0.03°);
- the fingertips sit just above the image centre: v +0.05 / +0.06 / +0.08 of the half-height (round 1: +0.06 … +0.09);
- the seat's front face stays at x ≤ 3.0, behind the cover screws' M3 button heads (x 3.9–9.6, 1.65 tall on the pad top), with room for a 2 mm hex key with the camera off. This set CAM_XC −8.5 (the sight-line optimum alone, −6, put the seat over the heads).
Result: CAM_XC −8.5, CAM_ZC = Z_TOP1 + 16.9 (68.4), tilt 34°; fingertips ≈83 mm from the lens; the cover fills the bottom 37–42 % of the frame. Lip 3 → 5 mm with an r 2 root fillet (strength: USB-tug twist). The thumb screw is 1/4"-20 × 5/16" (deep review 01 S6). The Brio's USB-C port is on its back (S5): a right-angle plug sits above the 6 mm lip.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Seat angle | 34° nose-down | ±1° | aims the camera | — | claw_frame.py CAM_TILT |
| Thread position | G (−8.5, 0, 68.4) | ±0.3 | sight line | — | claw_frame.py CAM_XC, CAM_ZC |
| 1/4" slot | Ø7.05 CAD (6.85 printed), ±4 along y | +0.3/−0 | clearance | HOLE_COMP +0.2 | fdm-design-rules default |
| Lip to camera back | 0.3 | ±0.2 | anti-rotation | — | claw_frame.py LIP_CLR |
| Seat front face | x 3.0 | ±0.3 | 0.9 clear of the button heads | — | sight-line study |
| M3 holes | Ø3.6 CAD | +0.2 | M3 × 18 clearance | HOLE_COMP +0.2 | fdm-design-rules default |

measure_holes (geometry.json): 2 × Ø3.6 (teardrops); the 1/4" slot is a slot. Checked with build123d solids: a rounded (r 6) Brio box sits on the seat and lip with 0 mm³ overlap; the thumb screw's Ø16 × 5 head clears the mount and the cover; button heads (+0.5 all round) and the hex-key columns: 0 mm³.

## Parameters exposed by model.py
HOLE_COMP, SCREW_CLR, SLOT_HALF, BED_CHAMFER, TO_PRINT, HALF_D, CAM_LOC; shared: claw_frame.py (CAM_TILT, CAM_XC, CAM_ZC, SEAT_T, LIP_T, LIP_H, LIP_CLR, LIP_FILLET, MOUNT_Y, PAD_X, PAD_TOP, TOP_SCREWS, Z_TOP1, M3_CLEAR)

## Risks
- The camera sits higher than in round 1 (its centre of mass ≈80 mm outboard of the claw's back face, 15 mm more) → bigger sideways moments on the pitch joints (SYS-04: the link specs carry them) and more shoulder torque (the payload table includes it).
- The USB port's height on the back is unmeasured → BUILD_GUIDE §2 asks for it; the lip is 6 mm tall.
- The Brio is 102 mm long: it overhangs the claw by 19 mm each side (clear of every arm part in `assembly_check.py`, which carries it with the plug and the thumb screw).

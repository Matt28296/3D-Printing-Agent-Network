# Design brief: Claw frame (wrist plate + servo bulkhead)

Job: 20261026-arm-claw-frame · design-lead · 2026-10-26 (round 3: deep reviews 01 B1/B2/S1, 03 SYS-01/SYS-08, claw DFM and strength round 1)

## Material
PETG, as for the rest of the arm: tough, low creep under the servo's holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, 12.5 MPa across layers).

## Orientation
Flat, back face (wrist horn pocket) on the bed, 0.4 mm bed chamfer. The pocket ceiling bridges 7.9 mm. The bulkhead and the rail wall grow straight up. The servo window has a 7 mm 45° roof, so its top bridges 9.2 mm; its tab pilots are teardrops pointing up and its lower corners have Ø3 teardrop reliefs. The front M2.5 pilots are flat-topped teardrops (1.9 mm skin under rack B's track).

Load paths: wrist-plate bending (claw weight, side pushes) runs along the layers. The bulkhead root takes the claw's weight moment and the camera package's sideways moment across the layers; the full-width plate and the 6.5 mm × 64 mm bulkhead carry it (strength fix 1). The rail wall stands on the plate and takes rack B's back thrust in bending along its 64 mm length (≈0.9 MPa).

## Concept
A full-width 6 mm wrist plate on the wrist MG90S's single-arm horn, with a 2.3 mm raised pad behind the bulkhead so the clamp floor is 6.3 mm; a 6.5 mm bulkhead holding the claw MG90S, which goes in from the front, case bottom first, its lead through a notch at the shaft end (that end's tab pilot moved 1.3 mm out: `lead="notch_shift_pilot"`); a 4 mm rail wall behind rack B (round 3: a wall, not a block back to the bulkhead, 8 g less at the end of the arm). Rack B rides on the plate's top face. The cover screws on from above (2 × M3) and the front (2 × M2.5).

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Claw-servo axis | y 0, z 27.25 | ±0.2 | sets the gear mesh | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Bulkhead front face (tab seat) | x 10.0 | ±0.2 | sets the pinion's back face (x 22.6 = 10 + MG90S link_back_z 12.6) | — | claw_frame.py |
| Wrist plate top (rack B's guide) | z 6.0 | ±0.15 | rack back rides on it | — | claw_frame.py (RACK_SEAT 0) |
| Rail wall front face | x 22.35 | ±0.15 | 0.25 sliding gap | — | claw_frame.py |
| MG90S window | 23.2 × 12.8 CAD, 23.0 × 12.6 printed | +0.3/−0 | 0.4 side / 0.2 end clearance on the 22.8 × 12.2 MG90S | HOLE_COMP +0.2 | deep review 01 S1 |
| Lead notch | 4.4 × 1.6 CAD beyond the case end | +0.2 | 3.6 × 1.2 ribbon + bend | HOLE_COMP | deep review 01 B1 |
| Wrist clamp floor | 6.3 | ±0.2 | M2 × 12 + Ø6 × 0.5 washer: 4.6 into the spline | — | deep review 01 S2 |

Printed targets: MG90S window +0.4 side / +0.2 end, wrist horn pocket +0.5, M2 clamp hole Ø2.4, M3 self-tap pilots Ø2.5, M2.5 self-tap pilots Ø2.0, MG90S tab pilots Ø1.5 (slots 0.4 longer outwards). Every hole gets HOLE_COMP = +0.2 mm in CAD. measure_holes (geometry.json): Ø2.6 clamp, 2 × Ø2.7 top pilots, 2 × Ø2.2 front pilots; the tab pilots are slots, not round holes.

Printed ligaments (servo_mount_cutter's check, holes printing HOLE_COMP/2 small): lead notch to the moved pilot 1.55 mm, far-end pilot to the window 1.65 mm (set by the MG90S's 27.8 mm hole spacing on a 22.8 mm body: every MG90S window in the repo has it), moved pilot to the window 2.95 mm. Both small ones are above hobby_parts' 1.5 mm minimum for a self-tapper and below the 1.8 mm "4 perimeters" rule of thumb: the screws are M2 × 8 self-tappers in a 6.5 mm wall, driven snug, not tight.

## Parameters exposed by model.py
HOLE_COMP, CLR, END_CLR, TOP_PILOT_DEPTH, FRONT_PILOT_DEPTH, BED_CHAMFER, RELIEF_D, RAIL_FILLET, SERVO_LOC; shared: claw_frame.py (T_W, PAD_T, ZS, X_B, BULK_T, X_REAR, HALF_Y, RAIL_IN, RAIL_X0, RAIL_X1, GUIDE_T, WINDOW_ROOF, TOP_SCREWS, FRONT_SCREWS, M3_PILOT, M25_PILOT)

## Risks
- The wrist clamp screw sits under the claw servo → BUILD_GUIDE §4 fits it first.
- The claw servo goes in from the front with its lead root crossing the bulkhead → notch at the shaft end, moved pilot, slit filed to 2.1 mm (BUILD_GUIDE §4 step 8). `claw_sequence_check.py` sweeps the servo + lead in from 20 mm out: 0 mm³.
- The 1.55 / 1.65 mm pilot ligaments → self-tappers driven snug, not tight.
- The claw is heavier than round 1 (frame 34.8 cm³ against 24.4): the arm's payload table (torque_budget.py) uses it.

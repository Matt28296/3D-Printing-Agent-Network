# Design brief: Claw frame (wrist plate + servo bulkhead)

Job: 20261026-arm-claw-frame · design-lead (Architect acting in this test run) · 2026-10-26

## Material
PETG, as for the rest of the arm: tough, low creep under the servo's holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, back face (wrist horn pocket) on the bed: the pocket ceiling bridges 7.9 mm as on the old gripper base. The bulkhead and rail grow straight up; the servo window has 45° shoulders so its top bridges 12.9 mm, and its tab pilots are teardrops pointing up. Wrist-plate bending runs along the layers; the bulkhead root takes the claw's weight moment across the layers (5 N lever about 40 mm).

## Concept
6 mm wrist plate on the wrist MG90S's single-arm horn, a 6 mm bulkhead that holds the claw MG90S with its shaft pointing at the fingertips, and the lower rail that backs rack B. Rack B slides on the wrist plate's top face. Replaces the old gripper base (20261025-arm-gripper-base).

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Claw-servo axis | y 0, z 22.5 | ±0.2 | sets the gear mesh | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Bulkhead front face (tab seat) | x 10.0 | ±0.2 | sets the pinion's x | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Wrist plate top (rack B track) | z 6.0 | ±0.15 | 0.25 sliding gap | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Lower rail front face | x 19.15 | ±0.15 | 0.25 sliding gap | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| MG90S window | 22.9 × 12.6 printed | +0.3/−0 | clearance | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: MG90S window +0.4 side / +0.2 end, wrist horn pocket +0.5, pinion horn pocket +0.3 (gear backlash adds up), M2 clamp holes Ø2.4, M3 clearance Ø3.4, M3 self-tap pilots Ø2.5, MG90S tab pilots Ø1.5, 1/4"-20 clearance Ø6.85. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row). Sliding clearance around the racks 0.25 mm; gears module 1, 20°, each member 0.1 mm thinner (0.2 mm backlash). Gears and racks are drawn in the bed plane (axis vertical) so the involute is as accurate as XY.

## Parameters exposed by model.py
HOLE_COMP, CLR, END_CLR, TOP_PILOT_DEPTH, FRONT_PILOT_DEPTH, BED_CHAMFER, SERVO_LOC; shared: claw_frame.py (T_W, ZS, X_B, BULK_T, X_REAR, REAR_HALF, HALF_Y, RAIL_IN, RAIL_X1, WINDOW_ROOF, TOP_SCREWS, FRONT_SCREWS, M3_PILOT)

## Risks
- The wrist clamp screw sits under the claw servo → assembly order in BUILD_GUIDE (screw first); bulkhead starts at x 4 so the Ø6 washer clears
- Servo window in a vertical wall → 45° shoulders (bridge 12.9 mm) and teardrop tab pilots
- Bulkhead root across layers → 6 mm bulkhead, 64 mm wide, merged with the rail

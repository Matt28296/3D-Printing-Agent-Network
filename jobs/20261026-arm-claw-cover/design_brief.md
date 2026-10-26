# Design brief: Claw cover (front plate, top wall, upper lip)

Job: 20261026-arm-claw-cover · design-lead · 2026-10-26 (round 3: deep review 03 SYS-01 fix A, cover DFM and strength round 1)

## Material
PETG, as for the rest of the arm: tough, low creep under the servo's holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, 12.5 MPa across layers).

## Orientation
Standing on its −y end (`TO_PRINT = Rot(90, 0, 0)`): the whole side profile lies in the bed plane, so every rack bearing face (front plate inner face, top wall underside, lip wall face) is a vertical wall and comes out straight and smooth. Slot A runs along print Z and closes with a 45° roof (a ceiling in print, apex rounded r 1.5); slot B's closed end is a floor in print (r 2 corners). The pinion pass-through is a teardrop with its 45° point up (+y). The screw holes are teardrops pointing up. The openings are cut before the 0.3 mm bed chamfer, so slot A's mouth on the bed is chamfered too. 64 mm tall on a 542 mm² footprint: 5 mm outer brim (`print_requirements.json` min `brim_width` 5).

Load paths: bending of the front plate and the top wall runs along the layers (their planes are vertical in print). The tie post and web, which join the two halves of the front plate, are loaded in their planes along the layers.

## Concept
SYS-01 fix A: the pinion goes in last, axially, through a Ø22.6 (printed) hole on its axis, with both jaws parked fully open, and comes out first for service. The hole merges with both neck slots and cuts the front plate in two: the half below slot A (with the strip under slot B) and the half under the top wall. A tie inside the claw joins them again: a web between the two racks (|z − ZS| ≤ 8, 1.15 mm clear of both racks' tips) from the front plate back to a post that meets the lip, at y −32…−24, outside the pinion and every jaw path. The slivers the hole would leave beside the slots are cut back to |y| 7.
Strength and DFM round 1: front plate 3 → 5 mm and down to z −4 (9.75 mm strip under slot B), top wall back to x 0 (carries the whole camera pad), r 2 fillet in the inner corner front plate / top wall (y 9–32, beyond slot A's roof), 1.5 mm 45° chamfer on the top-front edge (the camera sees the fingertips over it; 1.5 keeps a 1.5 mm face over slot A, no knife edge). Round 3: the lip is a 4 mm wall, not a block back to the bulkhead (8 g less at the end of the arm).

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Front plate inner face | x 32.85 | ±0.15 | 0.25 sliding gap in front of the racks | — | claw_frame.py |
| Top wall underside | z 48.5 | ±0.15 | rack A's back rides on it | — | claw_frame.py (RACK_SEAT 0) |
| Lip wall front face | x 22.35 | ±0.15 | 0.25 gap behind rack A | — | claw_frame.py |
| Slot A / slot B | z 38.25–48.5 / 5.75–16.25 | +0.2/−0 | 0.25 around the 10 mm necks | — | claw_frame.py |
| Pinion pass-through | Ø22.8 CAD, ≈22.6 printed | +0.3/−0 | pinion Ø21.7: 0.55 CAD / 0.45 printed radial | HOLE_COMP +0.2 | deep review 03 SYS-01 (≥ 20.6) |
| Top / front screw holes | Ø3.6 / Ø3.0 | +0.2 | M3 / M2.5 clearance | HOLE_COMP +0.2 | fdm-design-rules default |

measure_holes (geometry.json): Ø22.8 pass-through, 2 × Ø3.6, 2 × Ø3.0, all teardrops (270°).

## Parameters exposed by model.py
HOLE_COMP, BED_CHAMFER, TO_PRINT, APEX_R, R_PASS, ZA0/ZA1, ZB0/ZB1, Z_CRES; shared: claw_frame.py (X_F0, X_F1, FRONT_Z0, Z_TOP0, Z_TOP1, TOP_X0, RAIL_IN, RAIL_X0, RAIL_X1, NECK_Z, SLOT_CLR, SLOT_A_END, SLOT_B_END, SLOT_FILLET, ACCESS_D, CRESCENT_Y, TIE_X0, TIE_Y, TIE_Z, CORNER_FILLET, CORNER_FILLET_Y0, TOP_CHAMFER, TOP_SCREWS, FRONT_SCREWS, M3_CLEAR, M25_CLEAR)

## Risks
- The front plate is two pieces joined only through the tie and the top wall → the tie is in the strength check; the claw proof test checks it.
- Long slots in a vertical wall would bridge 32 mm → printed standing on its end, slots vertical.
- Tall thin print → 5 mm brim, PETG first layer.
- Assembly order is fixed (cover before jaws, pinion last) → `claw_sequence_check.py` sweeps every step with exact solids: 0 mm³.

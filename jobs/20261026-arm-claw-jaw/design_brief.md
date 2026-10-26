# Design brief: Claw jaw (rack + finger), ×2

Job: 20261026-arm-claw-jaw · design-lead · 2026-10-26, claw round 3: every required fix of the jaw DFM and strength round 2 (this job's design_review.md and strength.md) and the pinion's strength change (FACE_W 12, backlash 0.1 / 0.7); earlier: deep review 03 SYS-01 / SYS-08, jaw round 1.

## Material
PETG, as for the rest of the arm: tough, low creep under the servo's holding load, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables: 25 MPa along the layers, 12.5 MPa across them.

## Orientation
Standing on the rack's back end (claw x = print Z, the x 22.6 face on the bed), finger up.
- **Load paths:** the rack teeth are drawn in the bed plane, so tooth bending runs along the layers. **Every bending of the neck and the finger, in either direction, puts its stress across the layers** (DFM round 1, item 4): the grip force, the opening stall, the sideways push and the yaw-stall sweep all do. The neck and finger are sized for the 12.5 MPa across-layer allowable.
- **Printing:** the grooves, the gusset and the finger's 45° edges print without support. No brim: it would fill the tooth gaps (`print_requirements.json` max `brim_width` 0).
- **Bed chamfer 0.25 mm, tooth outline included** (round 3, DFM fix 1; it was 0.3). At 0.3 the inset of the rack outline lost 2 of its 256 edges, so `tools/gears.py`'s ruled loft twisted: the first layer lost half the tooth area and the mesh had 182 706 faces. At 0.25 the result is clean:
  - the inset keeps all 256 edges (`cad_checks.py`);
  - the loft's volume equals the 0.1 mm stepped band's to 0.001 % (148.646 / 148.645 mm³), so it is a true 45° face;
  - mesh_check finds 0 thin-wall hits (round 2: 20, capped) and 0 % overhang, with 3470 mesh faces;
  - the layer check (0.2 mm layers, 0.04 mm raster, each layer against the one below grown 0.3 mm) finds no unsupported patch anywhere in the part.
  - `tools/gears.py` now refuses a loft whose inset lost edges and falls back to the stepped band, so this can't pass silently again (`tests/test_gears.py`).

## Concept
- **One piece:** a module-1 rack, 56.5 mm along y and **12 mm along x** (FACE_W 10 → 12, x 22.6…34.6, pinion strength round 2), ending in tooth gaps, with 10 mm of solid behind the roots.
- **Neck:** 20 × 10 mm on the rack's solid back, with r 4 root fillets at both y edges.
- **Finger:** 12 mm thick for 20 mm, tapering to 6 mm over 15 mm, joined to the neck by a full-height 45° gusset in plan, with r 3 fillets at its re-entrant kinks.
- **The fingertip stays at x 83.35:** the rack grew 2 mm forward, so the blade is 43 mm long instead of 45. The taper keeps its place relative to the neck (x 60.35…75.35), so the finger is a little thicker near its tip than in round 2. The arm's reach, payload, guard tip and the camera's view of the fingertips don't change.
- **Finger top:** flat at the neck's top for 15 mm, then 45° down to the grip zone.
- **Grip face:** 0.6 mm V-grooves across it at x 62.6…70.6 only. Round 3 stops them 12.7 mm short of the tip (strength fix: the groove at x 72.6 governed with SF 2.62). It keeps the 1.5 mm V-notch along the centre line and the 3.5 mm bevel on the tip's outer face.
- **Two identical copies:** jaw B is jaw A turned 180° about the pinion axis.
- **SYS-08 mesh:**
  - each rack's back rides on its guide (RACK_SEAT 0);
  - the teeth are **0.35 thinner at the pitch line** (RACK_BACKLASH 0.7; the pinion's 0.05 makes 0.40 per mesh, the top of SYS-08's 0.3–0.4);
  - tips topped 0.15 (0.60 mm tip land), root fillets r 0.30;
  - a 2 mm 45° chamfer on the rack's back/front edge for y ≥ 4.5 clears the cover's r 2 corner fillet.
- **SYS-01:** the jaws slide in from the open ends of their slots to fully open before the pinion goes in.

## Critical dimensions
| Feature | Nominal | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Rack pitch line to back face | 11.25 | ±0.15 | sets the mesh (back on its guide) | — | claw_frame.py |
| **Rack face width (x)** | **12.0** | −0.15/+0 | 0.25 sliding gaps | — | claw_frame.py FACE_W (pinion strength round 2) |
| **Teeth** | m 1, 20°, **0.35 thin** at the pitch line, tips topped 0.15, root r 0.30 | in the bed plane | **0.40 backlash per mesh** | — | tools/gears.py, claw_frame.py RACK_BACKLASH 0.7 |
| Neck | 20 × 10 | ±0.15 | 0.25 in its slot | — | claw_frame.py |
| Grip face | y 0 closed | ±0.2 | jaws meet | — | claw_frame.py |
| **Fingertip** | **x 83.35** (blade 43) | ±0.3 | — | — | claw_frame.py X_TIP (kept) |
| **Grooves** | x 62.6…70.6, 0.6 deep, pitch 2 | — | — | — | GROOVE_X (strength round 2) |
| **Bed chamfer** | **0.25 × 45°**, tooth outline included | — | elephant's foot | — | DFM round 2 fix 1; gears.py ≤ 0.25 m |

No holes (measure_holes: none). `cad_checks.py` proves:
- the size, the rack face and back, the tooth tips and their 0.35 thinning, the neck and its fillet;
- the grip face, the groove range, the fingertip;
- the bed chamfer, both on the solid and as the inset's edge count.

## Strength, predicted
From the strength-analyst's `strength_calc.py`, re-run on the round-3 parameters (it reads claw_frame.py and this model.py):

| Case | Round 2 | Round 3 |
|---|---|---|
| Grip at stall, one jaw blocked (governing) | 2.62 (groove at x 72.6) | **3.52**: the neck root governs. With the grooves stopping at x 71 no groove is critical; a groove at 72.6 would give 3.37 |
| Opening against an obstacle | 3.44 | 3.52 |
| Crash 13 N, yaw stall, handling | 3.43 / 4.59 / 5.76 | 4.05 / 4.77 / 5.93 |
| Rack teeth, one jaw blocked (HPSTC + Kf, face 11.5) | 3.53 | **3.95** |
| Rack bar bending | 3.66 | 4.47 |

The jaw's lowest predicted SF is **3.52**.

## Parameters exposed by model.py
- model.py: BED_CHAMFER, TIP_CHAMFER, TIP_BEVEL, GROOVE_D, GROOVE_PITCH, GROOVE_X, NOTCH_D, GUSSET, TAPER_FILLET, RACK_LOC.
- shared, in claw_frame.py: M, FACE_W, BACKLASH, RACK_BACKLASH, TIP_RELIEF, RACK_ROOT_FILLET, RACK_BACK, RACK_Y, RACK_EDGE_CHAMFER, RACK_EDGE_Y0, NECK_Z, NECK_Y, NECK_FILLET, NECK_X1, BLADE_T, BLADE_T_ROOT, TAPER_X0, TAPER_X1, GRIP_HALF, BLADE_L, X_TIP, GRIP_X0, TOP_KINK_X, KINK_FILLET.

## Risks
- **Grip and side loads bend the neck and finger across the layers:** candidate C's sections and fillets; lowest predicted SF 3.52.
- **Each jaw is 17.1 cm³** (round 2: 16.1), about 43 g for the pair at the end of the arm: the payload table includes it.
- **Partial teeth at the rack ends would make slivers:** the rack ends in tooth gaps (RACK_Y = −8π…10π).
- **Bed adhesion:** 572 mm² on a 60.75 mm-tall part. If the first print rocks, add two small sacrificial ears at the rack's y ends (DFM R1).
- **Spec §3 values that changed:**
  - rack face width 10 → 12;
  - each rack tooth 0.25 → 0.35 thinner (0.40 backlash per mesh);
  - blade 45 → 43 mm (tip unchanged at x 83.35);
  - grooves only at x 62.6…70.6;
  - bed chamfer 0.25.

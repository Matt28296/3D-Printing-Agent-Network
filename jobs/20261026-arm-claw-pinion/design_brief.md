# Design brief: Claw pinion (20 teeth, module 1)

Job: 20261026-arm-claw-pinion · design-lead · 2026-10-26, claw round 3: the pinion strength round 2 change (strength.md) and the DFM round 2 advisory R1 (design_review.md); earlier: deep reviews 01 B2 and 03 SYS-01 / SYS-08, pinion round 1.

## Material
PETG, as for the rest of the arm: tough, low creep under the servo's holding load, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables: 25 MPa along the layers, 12.5 MPa across them.

## Orientation
Back face (horn pocket) on the bed, axis vertical.
- **Load paths:** the involute profile is drawn in the bed plane, so tooth bending and the horn stubs' bearing run along the layers. The clamp preload squeezes the 6.3 mm floor.
- **Bridges:** the pocket ceiling bridges ≤ 7.5 mm, anchored all round. The layer check (0.2 mm layers, 0.04 mm raster, each layer against the one below grown 0.3 mm) finds that ceiling (z 2.1) and nothing else.
- **Infill:** print solid (100 %): the part is small and the teeth carry the grip.
- **Bed chamfer:** 0.25 mm 45°, tooth outline included. It is a true 45° band: the inset keeps all 780 edges, and the loft's volume equals the stepped band's to 0.001 % (72.058 / 72.057 mm³).
- **Pocket mouth (round 3, DFM R1):** a 0.2 mm 45° chamfer at the bed face, so no first-layer lip forms on the 0.1 mm fit. The horn plate sits at z 0.4…2.0, above it.

## Concept
**Gear:** module 1, 20 teeth, 20°, pitch Ø20, r 0.38 root fillets, tips topped 0.15 m (outside Ø21.7, tip clearance 0.40 to the rack roots).

**Round 3 (pinion strength round 2, required change 1):**
- **Face 10 → 12** (x 22.6…34.6).
- **Teeth 0.05 thinner at the pitch line** (PINION_BACKLASH 0.2 → 0.1), the racks' 0.35 (0.5 → 0.7): **0.40 backlash per mesh**, the top of SYS-08's 0.3–0.4.
- **The pry margin widens.** A jaw pushed sideways pries its rack onto the pinion; the rack's tips now bottom on the pinion's root lands 0.15 mm before the flanks could wedge (wedge at 0.55 radial, against the 0.40 tip clearance). Round 2's margin was 0.08 mm.
- **The counterbore deepens** from 1.7 to 3.7 mm, so the floor stays 6.3 mm. The M2 × 12 + Ø6 × 0.5 washer still reaches 4.6 mm into the spline, and its head sits 1.2 mm below the front face, inside the pass-through.

**Unchanged:**
- The servo's double-arm horn, both arms cut 5.5 mm from the centre and filed round, sits 2 mm deep in the back face with a light 0.1 mm fit that centres the pinion (SYS-08). With the MG90S's real height (01 B2) the back face sits at claw x 22.6.
- **SYS-01:** the pinion goes on last, pushed axially through the cover's Ø22.6 pass-through with both jaws parked fully open (`g 44`), and comes off first. `claw_sequence_check.py` sweeps it in as one exact solid: 0 mm³ against both jaws, the cover, the frame, the servo and the screws. It can come out once the claw is ≥ 22 mm open.

## Critical dimensions
| Feature | Nominal | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Teeth | m 1, z 20, 20°, each **0.05 thinner**, root fillet r 0.38, tips topped 0.15 | profile in the bed plane | **0.40 backlash per mesh** | — | tools/gears.py, claw_frame.py PINION_BACKLASH 0.1 |
| **Face width** | **12.0** | −0.15/+0 | racks 12, 0.25 to the cover's front plate | — | claw_frame.py FACE_W (strength round 2) |
| Outside diameter | 21.7 | ±0.1 | 0.45 radial in the pass-through (printed) | — | claw_frame.py |
| Horn pocket | hub Ø7.2 + stubs to r 5.5, 2 deep, **0.2 × 45° mouth chamfer** | +0.1 fit | centres the pinion | HOLE_COMP +0.2 | deep review 03 SYS-08; DFM round 2 R1 |
| Counterbore | Ø6.2 printed × **3.7** | +0.2/−0 | Ø6 washer, 6.3 mm floor | HOLE_COMP +0.2 | deep review 01 S2 |

measure_holes (geometry.json): Ø2.6 clamp hole, Ø6.4 counterbore. `cad_checks.py` proves:
- the size (Ø21.70 × 12), the holes, a tooth's tip and root radius, the 0.05 thinning;
- the counterbore depth and floor, the pocket and its mouth chamfer;
- the bed chamfer, both on the solid and as the inset's edge count.

## Strength, predicted
From the strength-analyst's `strength_calc.py`, re-run on the round-3 parameters:

| Case | Round 2 | Round 3 |
|---|---|---|
| Tooth fillet, one jaw blocked (HPSTC + Kf, face 11.5) | **2.85** | **3.61** |
| Both jaws, every full-close grip (cyclic) | 5.69 | 7.23 |
| Crash 13 N along the jaw travel | 4.73 | 6.00 |
| Rack teeth (jaw job) | 3.53 | 3.95 |
| Horn stubs / pocket wall / washer | 5.49 / 6.90 / 5.94 | unchanged |
| Pry margin (tips bottom before the flanks wedge) | +0.08 mm | **+0.15 mm** |

The pinion's lowest predicted SF is **3.61**.

## Parameters exposed by model.py
- model.py: HOLE_COMP, POCKET_CLR, BED_CHAMFER, CB_D, CB_H, POCKET_CHAMFER.
- shared, in claw_frame.py: M, Z_TEETH, FACE_W, BACKLASH, PINION_BACKLASH, TIP_RELIEF, PINION_ROOT_FILLET, PINION_HORN, HORN_TRIM_R, PINION_CB_D, PINION_FLOOR.

## Risks
- **The full horn is wider than the gear:** horn arms cut to 5.5 mm (BUILD_GUIDE §4 step 11); about 3.1 mm of ring between the pocket and the tooth roots (r 8.75).
- **Small teeth:** module 1 (4 extrusion widths per tooth), solid print, bed chamfer.
- **The light pocket fit** may need a drop of CA once the run is smooth (BUILD_GUIDE step 12).
- **Spec §3 values that changed:**
  - face 10 → 12;
  - each tooth 0.10 → 0.05 thinner (0.40 backlash per mesh);
  - counterbore 1.7 → 3.7 deep;
  - pocket mouth chamfer 0.2;
  - envelope Ø21.7 × 12.

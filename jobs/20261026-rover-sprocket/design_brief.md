# Design brief: Drive sprocket (×2)

Job: 20261026-rover-sprocket · design-lead (round 3) · 2026-10-26

## Material
PETG for every rover part: tough against knocks, wears acceptably on steel pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Outer disc face on the bed. Tooth bending, slot bearing and the hub-face contact all act in the layer plane. The part is now only the 7 mm disc: no printed hub, no bore, no radial hole, so nothing bends across the layers.

## Drivetrain decision (round 3)
**Problem (strength round 2).** In round 2 the N20's torque went through a printed D-bore with a radial M2 set screw, in a Ø10 printed hub running in a wall journal. No printed bore can carry the 160 N·mm stall torque: SF 3 would need 23 mm of D-flat, and the shaft is 10 mm long. No printed hub section may have a radial hole: SF 1.06–3.37 at the set-screw hole. The stock N20 shaft (10 mm, or 9 mm on Pololu motors) only just reached past the wall, so the layout had to change.

**Criteria (Architect):**
- N20 shaft bending SF at the gearbox bushing ≥ 2 at stall and ≥ 1.5 in the 5 cm corner drop, on σy 350 MPa;
- journal or hub friction torque against the 160 N·mm stall;
- assembly with ordinary tools;
- part availability.

**Shaft section.** D-shaft Ø3 with its flat 2.5 from the far side: area 6.29 mm², Ix 2.704 and Iy 3.773 mm⁴. The minimum effective section modulus over every bending direction is **1.931 mm³**, at the corner of the flat. Strength round 2 used 1.9955, about the principal axis only. A rotating shaft sees every direction, so the minimum is used below, with the principal-axis value in brackets.

**Loads.** Shaft radial load R = sprocket pull + 2 × 5 N pretension:
- stall 19.9 N;
- fresh pack at 100 % PWM 21.2 N;
- 5 cm corner drop 31.8 N;
- 5 cm flat drop 15.9 N.

The moment is R × the arm, the arm being the gearbox face to the track plane (Y 55).

| Concept | Arm (mm) | SF stall | SF fresh pack | SF 5 cm corner | Friction torque | Notes |
|---|---|---|---|---|---|---|
| **A** as specified: gearbox in a wall pocket, face 1 mm inside the skin (Y 37), track plane moved to Y 51 | 14.0 | 2.43 (2.51) | 2.27 | **1.52** (1.57) | 0 (no journal) | The road wheels' 3.7 mm inner V-flanges can't fit in the 1 mm left between the wall and the links: wheels would lose their inner flange, the wall would guide the track. 1.52 is 1 % over the limit, and falls below 1.5 if the critical section is taken just inside the face. |
| A with the track left at Y 55 | 18.0 | 1.89 | 1.77 | 1.18 | 0 | fails |
| A′: housing outside the wall beside the links (face Y 41), track at 55 | 14.0 | 2.43 | 2.27 | 1.52 | 0 | wheels unchanged, same thin drop margin (built first, then superseded) |
| **B**: journal kept, 3 × 20 mm-shaft N20 | 23.5 (journal not reached) | 1.45 | 1.35 | 0.90 | journal: 20 N·mm at 5 N pretension (12 % of stall), 62 N·mm at stall (39 %) | The lever model (journal engaged, strength round 2: 13.4 R) gives 2.54 / 1.59. It is statically indeterminate and needs a printed tube in the journal (Ø ≥ 10.5, no hole). Long-shaft N20s are sold, but less commonly than the 10 mm standard. |
| **C, chosen:** the N20 rolled 45° in a diamond nacelle that reaches inside the track's wrap; gearbox face at Y 45; hub on the shaft just outside the 1 mm skin; disc bolted straight to the hub | **10.0** | **3.40** (3.52) | **3.18** | **2.13** (2.20) | 0 driving straight; 2.3 N·mm (1.4 %) only under a 3 N inward side load on the thrust washer | Wheels, idler and track plane unchanged. Section at the bushing exit (face + 0.8): 2.31 at the corner; even 1 mm inside the face: 1.93. |

**Why C works.**
- **The section.** Rolling the N20 45° turns its 12 × 10 gearbox section into a diamond whose four faces are all at 45°. The pocket needs no roof or gable, and the outside of the nacelle prints without support.
- **The fit inside the wrap.** With 2 mm walls the nacelle reaches r 10.9 from the axle, while the links' inner faces on the wrap never come closer than 12.39 (CHORD_IN). That lets the gearbox face sit at Y 45, inside the track's width, with 1.5 mm measured clearance to the links (assembly_check.json).
- **Clearances beside the track.** The housing between the wall and the track keeps 1.0 mm to the links' inner edge.

**Torque path.** N20 D-shaft → Pololu #1996 aluminium hub (its M3 set screw on the D-flat, threadlocker) → 4 × M3 × 12 screws in shear (7.2 N each at 182 N·mm; strength round 2's FIX row gave bolt bearing SF 66–79) → the disc.

**Motor location.**
- **Outward:** the gearbox face stops on the skin.
- **Inward:** the shaft hub's thrust washer bears on the skin.
- **Torque and height:** the diamond pocket.

This removes the rear stop and makes 9 or 11 mm gearboxes and 9 or 10 mm shafts all work (assembly_check.json: an 11 mm gearbox is collision-free; both shafts sit 5 mm deep in the hub with ≥ 3.5 mm past the set screw).

**Assembly with ordinary tools:**
1. Solder the leads.
2. Slide the motor along its trough into the pocket.
3. Zip-tie the can.
4. Put the thrust washer and the hub on the shaft (1.5 mm key, set screw on the flat).
5. Fit 4 × M3 × 12 (2.5 mm key).

**Availability:** Pololu #1996 is a stocked 2-pack (Pololu and its distributors); standard N20s and M3 screws.

**Gearbox reaction (for the strength check).** The pocket is 11.5 mm long (|y| 33.5–45). At the 5 cm corner its edges carry 59.5 N (outer, in the nacelle) and 27.7 N (inner). The 2 mm nacelle walls form a closed box with the skin and the housing.

## Concept (this part)
The 10-tooth disc (pitch radius 16.18, 45° root chamfers that start on the disc circle) with 4 radial M3 slots and a centre clearance hole. The idler job runs this model with BORE = "round" (Ø10 hub, Ø3.5 bore on its M3 bolt).

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Pitch radius | 16.18 | ±0.15 | matches the 10 mm link pitch | — | rover_frame.RP |
| Disc | 7.0 thick, r 11.9 | ±0.1 | 8 mm link notch, under the links' inner faces | — | rover_frame.DISC_HALF, CHORD_IN |
| Hub slots | 3.4 wide printed, r 5.5–6.85 | +0.15/−0 | M3 clearance | HOLE_COMP +0.2 | POLOLU_HUB_1996.bolt_circle_r_range |
| Centre hole | Ø3.4 printed | +0.15/−0 | shaft end runs free | HOLE_COMP +0.2 | default |
| Hub face | world \|y\| 51.5 | — | disc seats on the hub | — | rover_frame.HUB_Y1 |

Printed targets for the whole rover: see the chassis brief. Every hole gets HOLE_COMP = +0.2 mm in CAD (fdm-design-rules default; no library row).

## Parameters exposed by model.py
HOLE_COMP, DISC_R, TOOTH_TIP_R, TOOTH_BASE_W, TOOTH_TIP_W, ROOT_CHAMFER, PHASE_DEG, BORE, HUB_FACE_Z, HUB_SCREW_D, SLOT_R, SLOT_ANGLE0, SHAFT_CLEAR_D, HUB_Z0_ROUND, ROUND_BORE, BED_CHAMFER (+ rover_frame.py: DISC_HALF, HUB, HUB_Y1, ...). `cad_checks.py` proves them on the geometry.

## Risks
- **Hub hole circle unconfirmed:** the radial slots cover r 5.5–6.85.
- **Set screw on the wrong side of the shaft:** turn the shaft so the flat faces the set screw before tightening; use threadlocker.
- **Gearbox radial load at the bushing:** no published N20 rating. The 10 mm overhang is the smallest the layout allows; the stall and drop proof tests cover it.

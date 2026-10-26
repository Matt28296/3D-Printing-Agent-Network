# Part spec: Road wheel (×4)

Job: 20261026-rover-wheel · Written by: Architect · Date: 2026-10-26 (round 3) · Assembly: [20261026-rover-assembly](../20261026-rover-assembly/assembly_plan.md)

## 1. Function
Carries the rover on the bottom track run (rim r 13.1 meets the links' inner faces) with 45° V-flanges that keep the track centred.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: Ø32.2 × 32.5 mm, running bore Ø3.5 printed, 0.4 × 45° chamfer on every bed edge (outer flange and bore mouth). Hub face at world |y| 38.5 on a washer against the wall; outer face at |y| 71.0.
- Fasteners used: rides on an M3 × 50 socket head cap screw (class 12.9, fully threaded). Stack from inside the tub: head on an M3 washer (ISO 7089) on the boss face (|y| 27.5–28.0), M3 nut in the wall trap, washer, wheel, washer, M3 nyloc (DIN 985). The bolt stands 2.0 mm out of the nyloc.

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Rim radius | 13.10 | ±0.15 | meets the link inner face 13.18 below the axle |
| Running bore | Ø3.5 printed (Ø3.7 CAD) | +0.15/−0 | running fit on M3, 0.5 clearance |
| Bed chamfer | 0.4 × 45° | ±0.1 | elephant's-foot relief |

Track pins: Ø2 × 24 mm steel dowel pins (ISO 8734 / ISO 2338, m6), or 2 mm steel rod cut to 23.5 mm and deburred.

## 4. Loads
Design loads, as re-derived by strength round 2 (see the strength.md files):
- **Rover mass:** 649 g (weight share 1.6 N per wheel, sustained).
- **Drop:** 5 cm onto a hard floor gives 15.9 N per axle on a flat landing and 31.8 N per axle on a corner (short-term).
- **Skid-steer side drag:** 3 N per track.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Drop (5 cm) | 15.9 flat / 31.8 corner, radial | rim → bore bearing | short-term | seconds |
| Weight share | 1.6 | rim | sustained | hours |
| Skid-steer | 3 axial on a flange | flange root | cyclic | hours |

## 5. Environment
- Max temperature (°C): 40 (indoor floor; N20 motors run warm, the 18650 cells must stay below 45 °C)
- Outdoor / UV: occasional indoor/outdoor use on dry ground; no UV-critical parts
- Chemicals, oils, moisture: dust and grit on the tracks

## 6. Material
- Preferred or required: PETG (designer's choice; the user left material to the designer)
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA for the chassis and tracks (creep and impact); TPU optional later for grip pads, not used now

## 7. Quantity and time
- Quantity: 4
- Max acceptable print time per batch (h): 3

## 8. Acceptance criteria (measurable)
- [ ] Spins freely; the track runs centred between the flanges
- [ ] **Proof test** (strength round 2): covered by the chassis tests. Chassis test 1 hangs 5 kg (49 N, 1.5 × the corner load) from the middle of this wheel's rim; chassis test 3 is the 5 cm drop, flat and on each corner. Pass after both: the wheel still spins freely with axial play under 0.5 mm; no dent or crack in the rim and no ring of crushed infill; bore ovalisation under 0.1 mm.

## 9. Notes and open questions
None open. Shared frames and clearances: see the assembly plan and `assembly_check.json`.

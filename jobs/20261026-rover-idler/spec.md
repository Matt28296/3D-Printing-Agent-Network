# Part spec: Idler (×2)

Job: 20261026-rover-idler · Written by: Architect · Date: 2026-10-26 (round 3) · Assembly: [20261026-rover-assembly](../20261026-rover-assembly/assembly_plan.md)

## 1. Function
The sprocket's toothed geometry (10 teeth, pitch radius 16.18) with a round Ø3.5 running bore and a Ø10 hub, free on its M3 × 40 bolt in the chassis's ±4 mm tension slot, so the track wraps it exactly like the sprocket. An M3 jack screw in the chassis bears on the bolt's head and holds the idler forward against the track tension.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: Ø35.8 × 20 mm, round bore through. Hub end at world |y| 38.5 on a washer against the wall; disc ±3.5 about the track plane (|y| 51.5–58.5).
- Fasteners used: rides on an M3 × 40 socket head cap screw (class 12.9, fully threaded). Stack from inside the tub: head on an M3 DIN 9021 washer (Ø9 × 0.8) on the idler block's face (|y| 27.2–28.0), sliding M3 nut in the wall's outer slot, washer (ISO 7089), idler, washer, M3 nyloc (DIN 985). The bolt stands 4.2 mm out of the nyloc. The jack screw is an M3 × 20 set screw (chassis job).

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Running bore | Ø3.5 printed (Ø3.7 CAD) | +0.15/−0 | running fit on M3, 0.5 clearance |
| Pitch radius | 16.18 | ±0.15 | matches the 10 mm link pitch |

Motor, battery-holder and sensor sizes are nominal (tools/hobby_parts.py). Track pins: Ø2 × 24 mm steel dowel pins (ISO 8734 / ISO 2338, m6), or 2 mm steel rod cut to 23.5 mm and deburred.

## 4. Loads
Design loads, as re-derived by strength round 2 (see the strength.md files):
- **Rover mass:** 649 g.
- **Motor stall:** 160 N·mm (182 at 100 % PWM on a fresh pack).
- **Track:** tight run 14.9 N at stall, pretension 5 N per run.
- **Drop:** 5 cm onto a hard floor gives 15.9 N per axle flat and 31.8 N per axle on a corner (the idler is a corner axle).

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Track tension at the idler | 29.8 at a reverse stall (both runs tight), 16.4 cyclic, 10 sustained | bore bearing on the bolt; held by the jack screw, not by friction | as stated | hours |
| Drop (5 cm) | 15.9 flat / 31.8 corner | rim → bore bearing | short-term | seconds |
| Debris jam | 9.9 on one tooth | tooth root | short-term | seconds |

## 5. Environment
- Max temperature (°C): 40 (indoor floor; N20 motors run warm, the 18650 cells must stay below 45 °C)
- Outdoor / UV: occasional indoor/outdoor use on dry ground; no UV-critical parts
- Chemicals, oils, moisture: dust and grit on the tracks

## 6. Material
- Preferred or required: PETG (designer's choice; the user left material to the designer)
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA for the chassis and tracks (creep and impact); TPU optional later for grip pads, not used now

## 7. Quantity and time
- Quantity: 2
- Max acceptable print time per batch (h): 2

## 8. Acceptance criteria (measurable)
- [ ] Spins freely on the bolt with < 0.5 mm axial play
- [ ] **Proof tests** (strength round 3):
  1. **Rearward pull.** Fit the idler on its bolt at mid-slot in the chassis, the jack screw set against the bolt head and a pen mark across the slot and the washer. Pull it **rearward, horizontally along the track line, with 4.5 kg (44 N, 1.5 × the 29.8 N reverse-stall load)** for 1 min, using a strap round the idler. Pass: the idler still spins freely; axial play < 0.5 mm; bore ovalisation < 0.1 mm; the bolt hasn't moved (pen mark); measured against a fixed mark on the chassis, the idler disc's rear face has moved ≤ 0.3 mm; the bolt stays square (≤ 0.5 mm runout at its tip). Run this test after the chassis's idler-clamp change (chassis strength round 3, change 1).
  2. **Chassis tests.** The chassis stall test, run **in reverse as well**, and the 5 cm drop also cover the idler. Afterwards it must still spin freely.

## 9. Notes and open questions
None open. Shared frames and clearances: see the assembly plan and `assembly_check.json` (idler and jack screw clear at both slot ends).

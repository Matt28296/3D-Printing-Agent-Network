# System spec: Tracked rover (assembly of 6 printed jobs)

Job: 20261026-rover-assembly · Written by: Architect · Date: 2026-10-26 (round 3; round 4 by design-lead: 2 mm motor skin and idler clamp plates in the chassis, wider lid rails) · Plan: [assembly_plan.md](assembly_plan.md) · Build: [BUILD_GUIDE.md](BUILD_GUIDE.md)

## 1. Function
A small skid-steer tracked rover, robot 2 of 3, for driving and simple autonomy tests indoors (tile, wood, carpet).
- **Electronics:** an ESP32 DevKit (the user's choice) drives 2 × N20 gear motors through a TB6612FNG. It reads an HC-SR04 distance sensor.
- **Power:** 2 × 18650 cells (7.4 V) through a toggle, and an MP1584 buck for the 5 V rail.
- **Tracks:** each side has 34 printed PETG links on Ø2 steel pins, a 10-tooth drive sprocket at the rear, a toothed idler at the front and two V-flanged road wheels. An M3 jack screw tensions the track and holds it.
- **Drop rating: 5 cm onto a hard floor.** It is not built to survive a fall off a desk.

## 2. Envelope and interfaces
- **Overall:** 160 × 155 × 73 mm (assembly_check.json: 159.8 × 155.0 × 72.7). This includes the axle-bolt tips at |y| 77.5 and the toggle lever on the lid.
- **Ground clearance:** 8.7 mm.
- **Mass:** about 0.65 kg (649 g, strength round 2).
- **Shared frame:** `rover_frame.py`, which every model.py imports. X forward, Y left, Z up, ground at Z 0, sprocket axle at X 0.
- **Pieces:** the printed pieces are in assembly_plan.md; the bought parts are in BUILD_GUIDE.md §1.

## 3. Critical dimensions and tolerances (system)
| Feature | Nominal (mm) | Tolerance | Check |
|---|---|---|---|
| Sprocket to idler | 120 (idler slot ±4) | — | 34 links × 10 mm close exactly at 120. One link removed puts the idler back to 119 |
| Track planes | Y ±55 | ±0.3 | sprocket, idler and wheel flanges coplanar |
| Links to chassis | ≥ 1.0 | min | measured 1.0 beside the housing, 1.5 to the nacelle |
| N20 shaft overhang | 11.0 | max | gearbox face (\|y\| 44, on the 2 mm skin) to the track plane |
| Bolt thread past each nyloc | ≥ 1.5 | min | 2.0 (road wheels), 4.2 (idlers) |
| Teeth in link notches | 7 per sprocket and idler | — | assembly check |

## 4. Loads (system)
| Case | Value | Where it goes |
|---|---|---|
| Motor stall | 160 N·mm design per motor; 182 N·mm at 100 % PWM on a fresh pack. **Measure each motor first** (chassis spec §8) | sprocket pull 9.9 N; tight run 14.9 N with 5 N pretension; idler 29.8 N at a reverse stall, on the jack screw |
| Everyday driving | tight run 8.2 N; skid-steer drag 3 N per track | tracks, wheels, bolts |
| Drop, 5 cm onto a hard floor | 20 g peak: 15.9 N per axle flat, 31.8 N per axle on a corner | every axle; the N20 shaft (SF 1.91 at the 11 mm arm) |
| Lifted by the lid | 2 × weight on 4 screws: 3.2 N each | inserts |

Part-level load cases and proof tests are in each part's `spec.md` §4 and §8.

## 5. Environment
- Max temperature (°C): 40 (indoor floor; N20 motors run warm, the 18650 cells must stay below 45 °C)
- Outdoor / UV: occasional indoor/outdoor use on dry ground; no UV-critical parts
- Chemicals, oils, moisture: dust and grit on the tracks

## 6. Material
- **Printed:** PETG for every printed part (the designer's choice; the user left material to the designer).
- **Excluded:** PLA, because of creep and impact.
- **Bought:** steel pins and fasteners. M3 axle bolts are class 12.9 and fully threaded.

## 7. Quantity and time
- Quantity: 1 rover. Printed: 1 chassis, 1 lid, 2 sprockets, 2 idlers, 4 road wheels, 68 + 2 track links
- Print time: per job (see each `print_requirements.json`); the chassis is the longest, up to 12 h

## 8. Acceptance criteria (measurable)
Do these after every part's §8 proof tests have passed (deep review 04 S-11):
- [ ] **1. Free-running.** With the rover propped up so the tracks are off the ground, both tracks start and run at `speedPct` 30 (about 24 % PWM). If one stalls, its track is too tight or a wheel binds.
- [ ] **2. Straight run.** 2 m on tile at the sketch's PWM cap: at least 120 mm/s, drifting less than 10 % of the distance (200 mm).
- [ ] **3. Pivot.** A 360° pivot turn (one track forward, one back) on the household's thickest carpet without stalling.
- [ ] **4. Step.** Drives forward over a 12 mm step, both tracks.
- [ ] **5. Ramp.** Drives up and down a 20° carpet ramp.
- [ ] **6. Tension holds.** Pen-mark each idler slot nut against its slot edge. After 30 min of driving, the idler hasn't moved.
- [ ] **7. Run time.** At least 2 h of mixed driving on one charge (estimated 5–11 h, deep review 04 S-14).
- [ ] **8. Drops.** The 5 cm drops in the chassis spec §8 (test 3): flat and on each corner. Afterwards, tests 1 and 2 still pass.

## 9. Notes and open questions
- **Motor class.** N20 (GA12) 6 V, 100 rpm (≈150:1), LP or MP winding (stall ≤ 0.7 A at 6 V), 9 mm gearbox, 3 mm D-shaft 10 mm long from the flat gearbox face (at least 9.6 mm; a 9 mm shaft is too short for the sprocket, strength round 4). An 11 mm gearbox also fits.
- **Reverse steps.** They are limited to about 8.7 mm, because the chassis's rear-bottom corner meets a step before the track does (deep review 04 S-18). Forward steps are limited by grip: expect 12–15 mm.
- **Status file.** `status.json` still says `"kind": "part"`. It is the head-orchestrator's file, so it is not changed here.

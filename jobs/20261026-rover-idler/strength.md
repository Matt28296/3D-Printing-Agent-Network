VERDICT: NEEDS_TEST

# Strength check: 20261026-rover-idler (round 2)

strength-analyst · 2026-10-26 · `python3 jobs/20261026-rover-idler/strength_calc.py` · reads the sprocket model.py the idler runs, plus ROUND_BORE

**Result: NEEDS_TEST.** The allowables are placeholders, so PASS is not possible. Lowest SF **11.96**: the bore bearing on the M3 threads under the 5 cm front-corner drop (31.8 N). Every row passes with SF 12 or more, including the reverse stall, where the idler sees both runs tight (29.8 N). The drop rows stay above their SF up to a 19.9 cm drop. The idler's M3 bolt and its slot clamp belong to the chassis and fail there. **Fit class 8.8+ bolts and the tensioner screw** (chassis changes 1 and 4).

## Round 1 findings addressed

| Round 1 finding | Round 2 response | Round 2 result |
|---|---|---|
| Bore bearing at the 30 cm corner: SF 2.36 | 5 cm drop; Ø3.5 printed running bore (Ø3.7 CAD) | 5 cm corner: SF 11.96 ✓ |
| Jammed idler tooth (sharp root): SF 1.88 | 0.5 × 45° root chamfers in the shared sprocket model | Jam case: SF 3.15 ✓ (advisory) |
| Bolt bending (chassis-owned) | M3 × 45, still no grade | A2-70: SF 1.19 at reverse stall and 1.11 at the 5 cm corner ✗. Class 8.8: 1.69 / 1.58 ✓ (chassis change 1) |
| Spec missed the sustained pretension | Spec §4 now lists 2 × 5 N sustained and 2 × 14.9 N at stall | SF 38.1 sustained and 12.78 at reverse stall ✓ |

## Load cases: round 2, re-derived and shared by all six rover jobs

The same block runs at the top of every rover `strength_calc.py`. It reads `rover_frame.py` (`DROP_MM` 50, `PIN_D` 2.0, `HUB_D` 10, `WALL` 4.5), `tools/hobby_parts.py` and the six current `geometry.json` files.

| Load | Spec §4 (round 2) | Re-derived | Duration |
|---|---|---|---|
| Rover mass | ≈ 0.58 kg (5.7 N) | **649 g (6.36 N)**, from solid volumes × 1.27 g/cm³: chassis 146, lid 41, 2 sprockets 14, 2 idlers 12, 4 wheels 92, 68 links 89 (394 g printed). Add 2 × N20 (20 g), the battery (135 g), electronics (40 g), hardware (20 g, assumed) and **68 steel pins (39 g)**. Counting the wheels as solid overstates their 20 % infill by about 40 g, so the mass errs on the heavy side. | — |
| N20 stall torque | ≈ 160 N·mm | 160 N·mm design value (7.4 V). A fresh 8.4 V pack gives 182 at 100 % PWM and 146 at the sketch's 80 % cap. | short-term |
| Sprocket pull at stall | ≈ 10 N | 9.89 N (160 / RP 16.18) | short-term |
| Track pretension T0 | 5 N, sustained | 5 N per run (round-1 assumption) | sustained (creep) |
| Tight run | 14.9 N stall, 7.9 N everyday | 14.9 N at stall (T0 + stall pull, no slack-side relief). 8.2 N everyday: T0 plus the 3.18 N traction-limited pull (μ 1.0 × W/2). | short-term / cyclic |
| Sprocket radial | 19.9 / 12.9 / 10 N | 19.9 N stall, 13.2 N cyclic, 10 N sustained (tight run + slack run) | as stated |
| Idler radial | 2 × 14.9 N | **29.8 N at a reverse stall**: driving in reverse makes both idler runs the tight run. 16.4 N cyclic, 10 N sustained. | as stated |
| Skid-steer side drag | 3 N per track | 1.9 N derived (0.6 × W/2); the spec's 3 N is kept | cyclic |
| **5 cm drop onto a hard floor** | ≈ 14 N per axle flat, ≈ 29 N corner | Round-1 method: E = m·g·h = 0.318 J, stopping distance δ = 5 mm. That gives a 20 g peak and 127 N in total: **15.9 N per axle on a flat landing** (8 axles on the bottom run) and **31.8 N per axle on a corner** (half the mass on 2 axles). The spec's figures come from 0.58 kg. Sensitivity: δ = 2.5 mm doubles every drop load (31.8 / 63.6 N). | short-term |

Every drop row scales linearly with the height, so the script also prints the drop height at which the first drop row reaches its required SF.

**Loads the spec still misses:**
- **The journal turns the sprocket and N20 into a lever.** The track or ground load acts 17 mm outboard of the journal, so the hub tilts about the cradle-supported motor:
  - the journal outer end carries 1.55 × the hub load;
  - the N20 can end carries 0.55 × that load: on the cradle floor in a drop, on a cradle cheek under track pull;
  - the N20 shaft still carries 13.4 × R N·mm at the gearbox face (it was 23.5 × R in round 1).
- **The idler clamp holds the reverse-stall load (29.8 N) along its slot by friction alone.**
- **Pressing the steel pins into the Ø2.0 outer knuckles** puts an assembly hoop stress across the layers.

## Part-specific load path and assumptions

- **Bore.** The Ø3.7 CAD bore prints at about Ø3.5 and runs with 0.5 mm clearance on the threads of the fully threaded M3 bolt.
- **Bearing on the threads.** Taken as 0.5 × the projected area (crest contact). The bearing length is the 7 mm disc plus a 45° spread into the Ø10 hub: 10.15 mm, of which 5.1 mm counts after the thread factor. Bearing on the bore wall is in-plane: the bore is vertical in print.
- **Radial load (spec §4: 2 × the track tension).** Driving in reverse makes both idler runs the tight run: 29.8 N at stall, 16.4 N cyclic, 10 N sustained.
- **Teeth.** A free idler's teeth carry only the bearing drag, 0.83 N. If debris jams the idler, one tooth sees the stall pull: SF 3.15 with the chamfer.
- **Drop.** The idler sits on the bottom run like a road wheel, so it takes the corner share: 31.8 N.

## Allowables and sources (all jobs)

- **No measured data:** `library/materials.csv` has only its header row, so the skill's placeholders apply. PETG in-plane 25 MPa, across layers 12.5 MPa, E 1.8 GPa. Shear is 0.5 × normal (Tresca), as in round 1. **The best verdict possible is NEEDS_TEST.**
- **Direction:** compressive bearing on layer faces and on 45° teardrop flanks uses the in-plane value. Anything that pulls layers apart, or shears along a layer interface, uses the across-layer value.
- **Required SF:** 3 for short-term static loads; 4 for cyclic or sustained loads. Bought steel needs 1.5 on yield.
- **Steel yields:**
  - M3 bolts: A2-70 (450 MPa) is assumed, because the spec gives no grade. 8.8 is 640 MPa and 12.9 is 1080 MPa.
  - Track pins and the N20 shaft: **350 MPa**. This is a conservative yield for unspecified rod. Annealed silver steel or drill rod is about 400 MPa or more, and piano wire about 1500 MPa. Round 1 used 450 for the N20 shaft.
- **Temperature:** service is 40 °C against a PETG softening point of about 70 °C, so it is more than 20 °C away.

## Results (`strength_calc.py` output)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | bore bearing on M3 threads, reverse stall R 29.8 N | XY | 1.96 | 25.0 | 12.78 | 3.0 | OK |
| 2 | bore bearing, cyclic R 16.4 N | XY | 1.07 | 25.0 | 23.26 | 4.0 | OK |
| 3 | bore bearing, pretension sustained R 10 N (creep) | XY | 0.66 | 25.0 | 38.06 | 4.0 | OK |
| 4 | bore bearing, 5 cm front corner 31.8 N | XY | 2.09 | 25.0 | 11.96 | 3.0 | OK |
| 5 | disc rim bearing under a link, 5 cm front corner | XY | 1.26 | 25.0 | 19.80 | 3.0 | OK |
| 6 | tooth root (chamfer top), bearing drag 0.83 N (Kt 1.8) | XY | 0.66 | 25.0 | 37.62 | 4.0 | OK |
| 7 | hub end-face bearing, side 3 N | XY | 0.04 | 25.0 | 564.90 | 4.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, fixes, bought parts):
| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| tooth root if a jam loads one idler tooth with the stall pull 9.9 N (Kt 1.8) | XY | 7.94 | 25.0 | 3.15 | 3.0 | OK |
| bore bearing, 5 cm flat 15.9 N | XY | 1.05 | 25.0 | 23.92 | 3.0 | OK |
| bore bearing, 5 cm corner, stiff landing delta 2.5 (64 N) | XY | 4.18 | 25.0 | 5.98 | 3.0 | OK |
| M3 bolt bending at the wall face (reverse stall 29.8 N x 17) | steel σy 450 | 379.12 | 450.0 | 1.19 | 1.5 | no |
| M3 bolt bending at the wall face (reverse stall 29.8 N x 17) | steel σy 640 | 379.12 | 640.0 | 1.69 | 1.5 | OK |
| M3 bolt bending at the wall face (5 cm corner 31.8 N x 17) | steel σy 450 | 405.13 | 450.0 | 1.11 | 1.5 | no |
| M3 bolt bending at the wall face (5 cm corner 31.8 N x 17) | steel σy 640 | 405.13 | 640.0 | 1.58 | 1.5 | OK |

- lowest SF 11.96 (required 3.0) at: bore bearing, 5 cm front corner 31.8 N
- drop rows scale with the height: all of them meet their SF up to a 19.9 cm drop (design 5 cm), limited by: bore bearing, 5 cm front corner 31.8 N
- 0 of 7 verdict rows below their required SF

## Proof test (add to spec §8, which relies only on the chassis tests)

1. **Rearward pull.** Fit the idler on its bolt at mid-slot in the chassis, with the tensioner screw fitted (chassis change 4). Pull it **rearward and horizontally along the track line with 4.5 kg (44 N, 1.5 × the 29.8 N reverse-stall load)** for 1 min, using a strap round the idler. Pass:
   - the idler still spins freely;
   - axial play is under 0.5 mm;
   - bore ovalisation is under 0.1 mm;
   - the bolt hasn't moved (pen mark at the slot).
2. **Chassis tests.** The chassis stall test, run **in reverse as well**, and the 5 cm drop test also cover the idler. Afterwards the idler must still spin freely.

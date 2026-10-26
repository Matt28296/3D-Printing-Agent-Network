VERDICT: NEEDS_TEST

# Strength check: 20261026-rover-wheel (round 2)

strength-analyst · 2026-10-26 · `python3 jobs/20261026-rover-wheel/strength_calc.py` · also reads print_requirements.json, for perimeters and infill

**Result: NEEDS_TEST.** The allowables are placeholders, so PASS is not possible. Lowest SF **12.96**: hoop bending of the rim shell under the 5 cm corner drop (31.8 N per axle). Every row is at SF 13 or more, and the drop rows hold their SF up to a 21.6 cm drop. The wheel's M3 bolt belongs to the chassis and fails there with A2-70 at the corner load (SF 1.11). **Class 8.8 or better is required** (chassis change 1). The bolt length is fine: M3 × 45 needs 44 mm. It grows to M3 × 50 if the chassis bosses thicken (chassis change 3).

## Round 1 findings addressed

| Round 1 finding | Round 2 response | Round 2 result |
|---|---|---|
| Rim shell, 3 perimeters, at the 30 cm drop: SF 2.38 | 5 perimeters; 5 cm drop | 5 cm corner: SF 12.96 ✓ (6.48 even with δ 2.5) |
| M3 × 40 too short for the nyloc | M3 × 45 | Needs ≥ 44.0 mm, ends at Y 77.0 ✓ |
| Bolt grade (chassis-owned) | Still no grade | A2-70 at the 5 cm corner: SF 1.11 ✗. 8.8: 1.58 ✓ (chassis change 1) |
| Bore on threads, Ø3.2 printed | Ø3.5 running bore (0.5 mm clearance) | Bearing SF 29 at the corner ✓ |

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

- **Construction.** The wheel is not solid. print_requirements gives 5 perimeters (2.25 mm) and 20 % gyroid. The rim (r 13.1) carries the link's line load across its 24.6 mm width.
- **Rim model.** The perimeters form a rim shell, continuous in the hoop direction (in-plane), resting on the infill as an elastic foundation.
  - The infill is treated as a cellular solid (Gibson–Ashby, an assumption): E ≈ E_s·ρ² = 72 MPa, crush allowable ≈ 25·ρ^1.5 = 2.24 MPa.
  - An infinite beam on an elastic foundation then gives M = q/(4β) and p = qβ/2.
- **Bore.** The Ø3.7 CAD bore prints at about Ø3.5 and bears on the M3 threads at 0.5 × the projected area over the rim width.
- **Load cases.** The spec now lists both the flat (≈ 14 N) and corner (≈ 29 N) per-axle drop loads for the road wheels. The re-derived 15.9 and 31.8 N are used.
- **V-flange root under the 3 N skid-steer load:** in-plane, SF 127.

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
| 1 | rim shell hoop bending (perimeters), 5 cm flat 15.9 N | XY | 0.96 | 25.0 | 25.93 | 3.0 | OK |
| 2 | rim shell -> infill crush, 5 cm flat | infill 20% | 0.06 | 2.2 | 34.79 | 3.0 | OK |
| 3 | bore shell -> infill crush, 5 cm flat | infill 20% | 0.08 | 2.2 | 28.35 | 3.0 | OK |
| 4 | bore bearing on M3 threads, 5 cm flat | XY | 0.43 | 25.0 | 57.98 | 3.0 | OK |
| 5 | rim shell hoop bending (perimeters), 5 cm corner 31.8 N | XY | 1.93 | 25.0 | 12.96 | 3.0 | OK |
| 6 | rim shell -> infill crush, 5 cm corner | infill 20% | 0.13 | 2.2 | 17.39 | 3.0 | OK |
| 7 | bore shell -> infill crush, 5 cm corner | infill 20% | 0.16 | 2.2 | 14.18 | 3.0 | OK |
| 8 | bore bearing on M3 threads, 5 cm corner | XY | 0.86 | 25.0 | 28.99 | 3.0 | OK |
| 9 | rim shell hoop bending (perimeters), weight share (sustained) 1.6 N | XY | 0.10 | 25.0 | 259.30 | 4.0 | OK |
| 10 | rim shell -> infill crush, weight share (sustained) | infill 20% | 0.01 | 2.2 | 347.89 | 4.0 | OK |
| 11 | bore shell -> infill crush, weight share (sustained) | infill 20% | 0.01 | 2.2 | 283.50 | 4.0 | OK |
| 12 | bore bearing on M3 threads, weight share (sustained) | XY | 0.04 | 25.0 | 579.82 | 4.0 | OK |
| 13 | V-flange root bending, side 3 N on the cone (radial stress, XY) | XY | 0.20 | 25.0 | 126.76 | 4.0 | OK |
| 14 | hub end-face bearing on the wall nut, side 3 N | XY | 0.04 | 25.0 | 564.90 | 4.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, fixes, bought parts):
| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| rim shell hoop bending (perimeters), 5 cm corner, stiff landing delta 2.5 63.6 N | XY | 3.86 | 25.0 | 6.48 | 3.0 | OK |
| rim shell -> infill crush, 5 cm corner, stiff landing delta 2.5 | infill 20% | 0.26 | 2.2 | 8.70 | 3.0 | OK |
| bore shell -> infill crush, 5 cm corner, stiff landing delta 2.5 | infill 20% | 0.32 | 2.2 | 7.09 | 3.0 | OK |
| bore bearing on M3 threads, 5 cm corner, stiff landing delta 2.5 | XY | 1.72 | 25.0 | 14.50 | 3.0 | OK |
| rim shell hoop bending (perimeters), spec §8 proof (wheel on the bolt, 3 kg) 29.4 N | XY | 1.78 | 25.0 | 14.02 | 1.0 | OK |
| rim shell -> infill crush, spec §8 proof (wheel on the bolt, 3 kg) | infill 20% | 0.12 | 2.2 | 18.81 | 1.0 | OK |
| bore shell -> infill crush, spec §8 proof (wheel on the bolt, 3 kg) | infill 20% | 0.15 | 2.2 | 15.33 | 1.0 | OK |
| bore bearing on M3 threads, spec §8 proof (wheel on the bolt, 3 kg) | XY | 0.80 | 25.0 | 31.35 | 1.0 | OK |
| M3 bolt bending at wall face, 5 cm flat 15.9 N x 17 | steel σy 450 | 202.57 | 450.0 | 2.22 | 1.5 | OK |
| M3 bolt bending at wall face, 5 cm corner 31.8 N x 17 | steel σy 450 | 405.13 | 450.0 | 1.11 | 1.5 | no |
| M3 bolt bending at wall face, 5 cm corner 31.8 N x 17 | steel σy 640 | 405.13 | 640.0 | 1.58 | 1.5 | OK |

- lowest SF 12.96 (required 3.0) at: rim shell hoop bending (perimeters), 5 cm corner 31.8 N
- drop rows scale with the height: all of them meet their SF up to a 21.6 cm drop (design 5 cm), limited by: rim shell hoop bending (perimeters), 5 cm corner 31.8 N
- 0 of 14 verdict rows below their required SF

## Proof test (spec §8 says the chassis drop test covers the wheel; confirmed)

The wheel's margins (SF 13 or more) make the chassis tests sufficient:
- **Chassis test 1:** 5 kg hung from the middle of the wheel rim. That puts 49 N, 1.5 × the corner load, through this rim and bore. The spec §8 proof (3 kg) gives SF 14.
- **Chassis test 3:** the 5 cm drop, flat and on each corner.

After both, pass if:
- the wheel still spins freely, with axial play under 0.5 mm;
- there is no dent or crack in the rim and no ring of crushed infill;
- bore ovalisation is under 0.1 mm.

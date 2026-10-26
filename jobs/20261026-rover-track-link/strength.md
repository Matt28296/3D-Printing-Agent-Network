VERDICT: NEEDS_TEST

# Strength check: 20261026-rover-track-link (round 2)

strength-analyst · 2026-10-26 · `python3 jobs/20261026-rover-track-link/strength_calc.py` · reads model.py, rover_frame.py, hobby_parts.py and all rover geometry.json

**Result: NEEDS_TEST.** The allowables are placeholders, so PASS is not possible.
- The lowest ratio is the **steel pin in bending** when a road wheel lands on a hinge in the 5 cm corner drop: SF **4.91** against the 1.5 required on a conservative 350 MPa yield.
- The lowest PETG row is the outer-knuckle tear-out at stall: SF 15.2.
- The drop rows hold their SF up to a 16.4 cm drop.
- One assembly risk is outside the verdict: pressing the Ø2 rod into the Ø2.0 printed outer knuckles strains them 1 to 2.5 % across the layers. The proof test must cover the pressing (item 1 below).

## Round 1 findings addressed

| Round 1 finding | Round 2 response | Round 2 result |
|---|---|---|
| Filament pin bending: 0.88 at the 30 cm drop, 2.85 at stall | 2 mm steel rod (`PIN_D` 2.0) | Stall: SF 5.91. 5 cm corner: 4.91. Both on σy 350 with 1.5 required ✓ |
| Pin shear 1.25, knuckle bearing 1.06 (30 cm) | Steel rod, stiff in bearing on PETG | Shear SF 61 or more; knuckle bearing SF 26 or more ✓ |
| Tight running fit | Ø2.2 printed running (Ø2.4 CAD), Ø2.0 grip (Ø2.2 CAD), teardrops | Tear-out with the smaller ligaments (1.8 / 1.9): SF 15 or more ✓ |
| Spec said "3 shear planes" | Spec now says pin bending / shear | 2 planes used ✓ |

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

- **Hinge.** A 13.5 mm centre knuckle sits between two 4.75 mm outer knuckles, with 0.5 mm gaps, so the pin is in double shear.
- **Stiff pin.** The 2 mm steel pin is 111 × stiffer than PETG. Its beam-on-elastic-foundation length (1/β = 5.1 mm at k = 0.5 E) is about one outer knuckle (β·L 0.92) and half the centre knuckle (1.31). So the pin is near-rigid, and bearing is taken as uniform.
  - Pin bending uses the stiff-pin clevis formula: M = F/2 · (a/2 + g + b/4) = 3.125 F.
  - Pin shear is checked against 0.5 × σy.
  - Bearing is uniform: T/(d·Lc) on the centre knuckle, (T/2)/(d·Lo) on each outer knuckle.
- **Tear-out runs along the layers.** The link prints inner face down, so the pin holes are horizontal.
  - The strip ahead of the hole can only shed load into the layers above and below it, so tear-out uses the across-layer shear allowable (6.25 MPa).
  - With a stiff pin, the whole knuckle length carries load. Round 1 used 2/β for the soft filament pin.
  - The ligaments use the CAD holes: 1.8 mm (centre) and 1.9 mm (outer).
- **Drop.** The road-wheel rim lands on a hinge, and the centre knuckle's share (13.5/24 of the axle load) passes through the pin into the outer knuckles above the grousers. Spec §4 lists the flat load only; the corner load per axle (31.8 N) is checked too, because a road wheel is one of the two corner axles.
- **Press fit (advisory, secondary stress).** The outer knuckles grip the rod: Ø2.0 printed, tolerance ±0.05. Treating each knuckle as a thick ring (r 1 → 3) on a rigid pin:
  - 0.02 mm interference gives 1 % hoop strain and 13.8 MPa;
  - 0.05 mm interference gives 2.5 % and 34.5 MPa.

  That stress runs across the layers at the knuckle's front ligament. It is displacement-controlled: it yields or creeps the hole wall rather than growing, so it is not in the verdict. The risk is a knuckle **splitting along its layer line while the pin is pressed in**, or the grip creeping loose so the pin walks out.

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
| 1 | steel pin bending (stiff-pin clevis), stall 14.9 N | steel σy 350 | 59.24 | 350.0 | 5.91 | 1.5 | OK |
| 2 | steel pin shear (2 planes), stall | steel τy 175 | 2.37 | 175.0 | 73.85 | 1.5 | OK |
| 3 | centre-knuckle bearing (uniform), stall | XY | 0.55 | 25.0 | 45.34 | 3.0 | OK |
| 4 | outer-knuckle bearing (uniform, each T/2), stall | XY | 0.78 | 25.0 | 31.90 | 3.0 | OK |
| 5 | centre-knuckle tear-out to x=-3, stall | Z shear | 0.31 | 6.2 | 20.40 | 3.0 | OK |
| 6 | outer-knuckle tear-out (each T/2), stall | Z shear | 0.41 | 6.2 | 15.15 | 3.0 | OK |
| 7 | steel pin bending (stiff-pin clevis), cyclic 8.2 N | steel σy 350 | 32.56 | 350.0 | 10.75 | 1.5 | OK |
| 8 | steel pin shear (2 planes), cyclic | steel τy 175 | 1.30 | 175.0 | 134.39 | 1.5 | OK |
| 9 | centre-knuckle bearing (uniform), cyclic | XY | 0.30 | 25.0 | 82.50 | 4.0 | OK |
| 10 | outer-knuckle bearing (uniform, each T/2), cyclic | XY | 0.43 | 25.0 | 58.05 | 4.0 | OK |
| 11 | centre-knuckle tear-out to x=-3, cyclic | Z shear | 0.17 | 6.2 | 37.12 | 4.0 | OK |
| 12 | outer-knuckle tear-out (each T/2), cyclic | Z shear | 0.23 | 6.2 | 27.58 | 4.0 | OK |
| 13 | outer-knuckle bearing, pretension sustained 5 N (creep) | XY | 0.26 | 25.0 | 95.00 | 4.0 | OK |
| 14 | outer-knuckle tear-out, pretension sustained (creep) | Z shear | 0.14 | 6.2 | 45.13 | 4.0 | OK |
| 15 | body net section at notch root (Kt 2.5), stall | XY | 1.13 | 25.0 | 22.16 | 3.0 | OK |
| 16 | bridge shear centre -> outer lands, stall | XY shear | 0.58 | 12.5 | 21.49 | 3.0 | OK |
| 17 | drop on hinge, steel pin bending (clevis), 5 cm flat 15.9 N/axle | steel σy 350 | 35.61 | 350.0 | 9.83 | 1.5 | OK |
| 18 | drop on hinge, steel pin shear, 5 cm flat | steel τy 175 | 1.42 | 175.0 | 122.86 | 1.5 | OK |
| 19 | drop on hinge, centre-knuckle bearing, 5 cm flat | XY | 0.33 | 25.0 | 75.42 | 3.0 | OK |
| 20 | drop on hinge, outer-knuckle bearing (each Fp/2), 5 cm flat | XY | 0.47 | 25.0 | 53.08 | 3.0 | OK |
| 21 | grouser compression, 5 cm flat | XY | 0.40 | 25.0 | 62.85 | 3.0 | OK |
| 22 | drop on hinge, steel pin bending (clevis), 5 cm corner 31.8 N/axle | steel σy 350 | 71.22 | 350.0 | 4.91 | 1.5 | OK |
| 23 | drop on hinge, steel pin shear, 5 cm corner | steel τy 175 | 2.85 | 175.0 | 61.43 | 1.5 | OK |
| 24 | drop on hinge, centre-knuckle bearing, 5 cm corner | XY | 0.66 | 25.0 | 37.71 | 3.0 | OK |
| 25 | drop on hinge, outer-knuckle bearing (each Fp/2), 5 cm corner | XY | 0.94 | 25.0 | 26.54 | 3.0 | OK |
| 26 | grouser compression, 5 cm corner | XY | 0.80 | 25.0 | 31.43 | 3.0 | OK |
| 27 | side drag on knuckle end face, 3.0 N | XY | 0.15 | 25.0 | 165.00 | 4.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, fixes, bought parts):
| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| drop on hinge, steel pin bending (clevis), 5 cm corner, stiff landing delta 2.5 63.6 N/axle | steel σy 350 | 142.44 | 350.0 | 2.46 | 1.5 | OK |
| drop on hinge, steel pin shear, 5 cm corner, stiff landing delta 2.5 | steel τy 175 | 5.70 | 175.0 | 30.72 | 1.5 | OK |
| drop on hinge, centre-knuckle bearing, 5 cm corner, stiff landing delta 2.5 | XY | 1.33 | 25.0 | 18.86 | 3.0 | OK |
| drop on hinge, outer-knuckle bearing (each Fp/2), 5 cm corner, stiff landing delta 2.5 | XY | 1.88 | 25.0 | 13.27 | 3.0 | OK |
| grouser compression, 5 cm corner, stiff landing delta 2.5 | XY | 1.59 | 25.0 | 15.71 | 3.0 | OK |
| steel pin bending (stiff-pin clevis), spec §8 proof 4.5 kg on a 5-link chain 44.1 N | steel σy 350 | 175.65 | 350.0 | 1.99 | 1.5 | OK |
| steel pin shear (2 planes), spec §8 proof 4.5 kg on a 5-link chain | steel τy 175 | 7.03 | 175.0 | 24.91 | 1.5 | OK |
| centre-knuckle bearing (uniform), spec §8 proof 4.5 kg on a 5-link chain | XY | 1.64 | 25.0 | 15.29 | 1.0 | OK |
| outer-knuckle bearing (uniform, each T/2), spec §8 proof 4.5 kg on a 5-link chain | XY | 2.32 | 25.0 | 10.76 | 1.0 | OK |
| centre-knuckle tear-out to x=-3, spec §8 proof 4.5 kg on a 5-link chain | Z shear | 0.91 | 6.2 | 6.88 | 1.0 | OK |
| outer-knuckle tear-out (each T/2), spec §8 proof 4.5 kg on a 5-link chain | Z shear | 1.22 | 6.2 | 5.11 | 1.0 | OK |
| drop on hinge, steel pin bending (clevis), proof: 5 kg wheel pressed on a hinge 49.1 N/axle | steel σy 350 | 109.78 | 350.0 | 3.19 | 1.5 | OK |
| drop on hinge, steel pin shear, proof: 5 kg wheel pressed on a hinge | steel τy 175 | 4.39 | 175.0 | 39.85 | 1.5 | OK |
| drop on hinge, centre-knuckle bearing, proof: 5 kg wheel pressed on a hinge | XY | 1.02 | 25.0 | 24.46 | 1.0 | OK |
| drop on hinge, outer-knuckle bearing (each Fp/2), proof: 5 kg wheel pressed on a hinge | XY | 1.45 | 25.0 | 17.22 | 1.0 | OK |
| grouser compression, proof: 5 kg wheel pressed on a hinge | XY | 1.23 | 25.0 | 20.39 | 1.0 | OK |
| pin press fit 0.02 mm (spec grip tolerance -0.05): hoop at the outer knuckle's front ligament, strain 1.0 % | Z | 13.80 | 12.5 | 0.91 | 1.0 | no |
| pin press fit 0.05 mm (spec grip tolerance -0.05): hoop at the outer knuckle's front ligament, strain 2.5 % | Z | 34.51 | 12.5 | 0.36 | 1.0 | no |

- lowest SF 4.91 (required 1.5) at: drop on hinge, steel pin bending (clevis), 5 cm corner 31.8 N/axle
- drop rows scale with the height: all of them meet their SF up to a 16.4 cm drop (design 5 cm), limited by: drop on hinge, steel pin bending (clevis), 5 cm corner 31.8 N/axle
- 0 of 27 verdict rows below their required SF

## Proof test (spec §8 test kept; two items added)

1. **Pressing (new).** Press all 10 pins of a 5-link test chain: 2 mm rod, 23.5 mm long, deburred. Pass: no crack or white line at any outer knuckle, especially along the layer line through the pin, and each pin flush and firm. If knuckles crack, set `PIN_GRIP_CLR` 0 → +0.05 and retain each pin with a drop of CA at both ends instead.
2. **Tension (spec §8, kept).** Hang **4.5 kg (44 N, 3 × the 14.9 N stall tension)** from the same chain for 1 min. The pins reach SF 2.0 on 350 MPa and tear-out SF 5.1, so the test won't damage a sound chain. Pass:
   - no cracked knuckle;
   - the pins haven't moved;
   - the chain flexes freely to 40° both ways.
3. **Hinge crush (new).** Lay the chain grousers-down on a hard surface. Press a road wheel on its bolt across a pinned joint with **5 kg (49 N, 1.5 × the 31.8 N corner load per axle)** for 1 min. Pass: no cracking, pin straight, the joint still flexes freely.

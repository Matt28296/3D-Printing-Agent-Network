VERDICT: FAIL

# Strength check: 20261026-rover-track-link

strength-analyst · 2026-10-26 · `python3 jobs/20261026-rover-track-link/strength_calc.py` (reads model.py, rover_frame.py, hobby_parts.py and all rover geometry.json)

**Result: FAIL.** Lowest SF **0.88**: pin bending when a road-wheel rim lands on a hinge in the re-derived 30 cm drop (86 N per axle). Even without a drop, pin bending at stall is SF **2.85** (3 required). Tear-out, body and grousers are SF 9 or more.

## Part-specific load path and assumptions

- **Track tension:** 14.9 N at stall (short-term), 7.9 N everyday (cyclic), 5 N pretension (sustained). The pins are 1.75 mm filament in Ø2.10 CAD holes (Ø1.9 printed). Each hinge is double shear: a 13.5 mm centre knuckle between two 4.75 mm outer knuckles, with 0.5 mm gaps.
- **Pin bending:** the filament pin is as soft as the PETG knuckles, and both knuckles are much longer than 1/β = 1.39 mm, so the pin acts as a beam on an elastic foundation (Hetényi, semi-infinite: β·L ≥ 3.4). The foundation modulus is k = 0.5·E, the soft end of the plausible range, which gives the larger moment. The stiff-pin clevis formula (uniform pressure) is printed as an upper bound: SF 0.28. It does not apply to a pin this flexible, but it shows how sensitive this joint is.
- **Tear-out runs along the layers.** The part prints inner face down, so the pin hole is horizontal. The strip behind the hole (|z| < r) is cut off from its own layer and can only pass load to the layers above and below it. Tear-out is therefore checked against the across-layer shear allowable (6.25 MPa). The loaded length is 2/β per knuckle end. The design brief's "tear-out acts in the layer plane" is true only of the load direction, not of the shear planes.
- **Drop:** the road-wheel rim lands on a hinge. The centre knuckle's share (13.5/24 of the rim load) reaches the ground fastest through the pin, into the outer knuckles of the link in front, which sit 1 mm from that link's grousers. The pin therefore carries it in double shear. A rim landing on the bridge sits directly over the grousers and does not load the pin.
- **Pin material:** extruded filament (PLA or PETG) is not a printed part. The in-plane placeholder (25 MPa) is used for it, which is conservative for drawn filament.

## Load cases: re-derived, shared by all six rover jobs

The same block is computed at the top of every rover `strength_calc.py`, from `rover_frame.py`, `tools/hobby_parts.py` and the six `geometry.json` files.

| Load | Spec §4 | Re-derived | Duration |
|---|---|---|---|
| Rover mass | 0.5 kg (4.9 N) | **583 g (5.72 N)**: solid volumes × 1.27 g/cm³: chassis 112, lid 41, 2 sprockets 13, 2 idlers 13, 4 wheels 92, 68 links 92 (printed 363 g). Plus 2 × N20 (20 g), 2 × 18650 holder (135 g), electronics (40 g) and hardware (25 g, assumed). | — |
| N20 stall torque | 130 / 160 N·mm | 160 N·mm design (7.4 V). A fresh 8.4 V pack at 100 % PWM gives ≈182; at the sketch's 80 % cap, 146. | short-term. Only a jam or a hand-held track stalls the motor; on the floor the track slips first. |
| Sprocket pull at stall | 10 N | 9.89 N (160 / RP 16.18) | short-term |
| **Track pretension T0** | **missing** | 5 N per run (assumed: a firm push on the idler) | **sustained (creep)** |
| Tight run at stall | — | 14.9 N (T0 + stall pull; ignores slack-side relief) | short-term |
| Sprocket / idler radial load | 2 × 10 N (idler only) | 19.9 N stall, 12.9 N cyclic, 10 N sustained | as stated |
| Everyday track pull | 10 N cyclic | 2.9 N per track. Traction limits it to μ 1.0 (grousers in carpet) × W/2. A spot turn needs only 0.94 N per track. | cyclic |
| Skid-steer side drag | 3 N per track | 1.7 N per track derived (0.6 × W/2); the spec's 3 N is kept | cyclic |
| **30 cm drop onto a hard floor** | 25 N on one road-wheel bolt ("5 × weight") | E = m·g·h = 1.71 J. Assumed stopping distance δ = 5 mm; the computed elastic deflection of an axle is ≈ 1 mm, so this is generous. That gives a peak of 120 g and 686 N in total: **86 N per axle on a flat landing** (all 8 axles, sprockets included, sit on the bottom run) and **171 N on a corner** (half the mass on 2 axles). With δ = 10 mm: 43 / 86 N. The spec's 25 N per axle implies δ ≈ 17 mm, and nothing in the rover deflects that much. | short-term |
| 8 cm drop (recommended limit) | — | 32 g peak: 23 N per axle flat, 46 N corner | short-term |

**Loads the spec misses:**
- Track pretension, which is sustained and creeps the bores, the idler clamp and the motor wall.
- The drop share on the sprocket and the N20 shaft. The spec puts a drop load only on a road-wheel bolt.
- The battery's inertia on the 2.5 mm floor in a drop.
- The lid electronics' inertia.
- The idler clamp slipping in its slot under stall.
- The fresh-pack stall torque during a "full PWM" test.
- An upside-down landing, which hits the ESP32: its module and USB stand 3.5 mm proud of the seat rails.

The spec's link case says "3 shear planes". A hinge has 2: one centre knuckle between two outer knuckles.

## Allowables and assumptions (all jobs)

- **No measured data** (`library/materials.csv` is empty). The skill's placeholders are used: PETG in-plane 25 MPa, across layers 12.5 MPa, E 1.8 GPa. Shear = 0.5 × normal (Tresca), as in earlier jobs. **NEEDS_TEST is the best possible verdict.**
- Required SF: 3 for short-term static loads; 4 for cyclic or sustained loads. Bought steel needs 1.5 on yield (A2-70 = 450 MPa, 8.8 = 640, 12.9 ≈ 1080). The service temperature is 40 °C, against a softening point of about 70 °C for PETG: more than 20 °C away.
- Compressive bearing on layer faces and on 45° teardrop flanks uses the in-plane allowable. Anything that pulls layers apart or shears along a layer interface uses the across-layer value.
- Every value that is not stated above is printed by the script next to the case that uses it.

## Results (`strength_calc.py` output)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | pin shear (2 planes), stall 14.9 N | XY shear | 3.09 | 12.5 | 4.04 | 3.0 | OK |
| 2 | pin bending (BEF), stall | XY | 8.78 | 25.0 | 2.85 | 3.0 | **FAIL** |
| 3 | pin bearing in knuckle (BEF peak), stall | XY | 7.25 | 25.0 | 3.45 | 3.0 | OK |
| 4 | centre-knuckle tear-out to x=-3, stall | Z shear | 0.69 | 6.2 | 9.07 | 3.0 | OK |
| 5 | outer-knuckle tear-out (each T/2), stall | Z shear | 0.69 | 6.2 | 9.07 | 3.0 | OK |
| 6 | pin shear (2 planes), cyclic 7.9 N | XY shear | 1.63 | 12.5 | 7.65 | 4.0 | OK |
| 7 | pin bending (BEF), cyclic | XY | 4.63 | 25.0 | 5.39 | 4.0 | OK |
| 8 | pin bearing in knuckle (BEF peak), cyclic | XY | 3.83 | 25.0 | 6.53 | 4.0 | OK |
| 9 | centre-knuckle tear-out to x=-3, cyclic | Z shear | 0.36 | 6.2 | 17.19 | 4.0 | OK |
| 10 | outer-knuckle tear-out (each T/2), cyclic | Z shear | 0.36 | 6.2 | 17.19 | 4.0 | OK |
| 11 | pin bending (BEF), pretension sustained 5 N | XY | 2.95 | 25.0 | 8.48 | 4.0 | OK |
| 12 | body net section at notch root (Kt 2.5), stall | XY | 1.13 | 25.0 | 22.16 | 3.0 | OK |
| 13 | bridge shear centre -> outer lands, stall | XY shear | 0.58 | 12.5 | 21.49 | 3.0 | OK |
| 14 | drop on hinge, pin shear, 30 cm flat 86 N/axle | XY shear | 10.02 | 12.5 | 1.25 | 3.0 | **FAIL** |
| 15 | drop on hinge, pin bending (BEF), 30 cm flat | XY | 28.44 | 25.0 | 0.88 | 3.0 | **FAIL** |
| 16 | drop on hinge, knuckle bearing (BEF), 30 cm flat | XY | 23.48 | 25.0 | 1.06 | 3.0 | **FAIL** |
| 17 | grouser compression, 30 cm flat | XY | 2.14 | 25.0 | 11.66 | 3.0 | OK |
| 18 | side drag on knuckle end face, 3.0 N | XY | 0.15 | 25.0 | 165.00 | 4.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, bought parts):
| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| BOUND: stiff-pin clevis (uniform) pin bending, stall | XY | 88.43 | 25.0 | 0.28 | 3.0 | no |
| drop on hinge, pin shear, spec 25 N/axle | XY shear | 2.92 | 12.5 | 4.28 | 3.0 | OK |
| drop on hinge, pin bending (BEF), spec | XY | 8.29 | 25.0 | 3.01 | 3.0 | OK |
| drop on hinge, knuckle bearing (BEF), spec | XY | 6.85 | 25.0 | 3.65 | 3.0 | OK |
| grouser compression, spec | XY | 0.62 | 25.0 | 40.00 | 3.0 | OK |
| drop on hinge, pin shear, 30 cm, delta 10 43 N/axle | XY shear | 5.01 | 12.5 | 2.49 | 3.0 | no |
| drop on hinge, pin bending (BEF), 30 cm, delta 10 | XY | 14.22 | 25.0 | 1.76 | 3.0 | no |
| drop on hinge, knuckle bearing (BEF), 30 cm, delta 10 | XY | 11.74 | 25.0 | 2.13 | 3.0 | no |
| grouser compression, 30 cm, delta 10 | XY | 1.07 | 25.0 | 23.33 | 3.0 | OK |
| drop on hinge, pin shear, 8 cm drop 23 N/axle | XY shear | 2.67 | 12.5 | 4.68 | 3.0 | OK |
| drop on hinge, pin bending (BEF), 8 cm drop | XY | 7.59 | 25.0 | 3.30 | 3.0 | OK |
| drop on hinge, knuckle bearing (BEF), 8 cm drop | XY | 6.26 | 25.0 | 3.99 | 3.0 | OK |
| grouser compression, 8 cm drop | XY | 0.57 | 25.0 | 43.74 | 3.0 | OK |
| proof test 3 kg on 5-link chain: pin bending (BEF) | XY | 17.34 | 25.0 | 1.44 | 1.0 | OK |
| FIX Ø2.0 music-wire pin bending (clevis), 30 cm flat | steel σy 1500 | 191.87 | 1500.0 | 7.82 | 1.5 | OK |
| FIX Ø2.0 steel pin: centre-knuckle bearing (uniform), 30 cm flat | XY | 1.79 | 25.0 | 14.00 | 3.0 | OK |
| FIX Ø2.0 steel pin: tear-out (hole 2.35), stall | Z shear | 0.30 | 6.2 | 20.68 | 3.0 | OK |
| FIX Ø2.0 steel pin: tear-out, 30 cm drop on hinge | Z shear | 0.98 | 6.2 | 6.39 | 3.0 | OK |

**lowest SF 0.88 (required 3.0) at: drop on hinge, pin bending (BEF), 30 cm flat**

## Verdict and changes

FAIL. The drop-on-hinge pin checks fail at the re-derived 30 cm drop (pin shear 1.25, pin bending 0.88, knuckle bearing 1.06), and pin bending at stall fails narrowly (2.85).

- **Smallest change (BOM + one parameter): Ø2.0 mm spring-steel (music) wire pins** in place of the filament. Each needs 25 mm, so 1.7 m in total. Set `PIN_D` 1.75 → 2.0 in rover_frame.py; the hole becomes 2.35 CAD. Results at the 30 cm drop on a hinge: pin bending SF 7.8 on steel yield, centre-knuckle bearing SF 14, tear-out SF 6.4 (20.7 at stall). The ligament shrinks from 1.95 to 1.83 mm, which still passes. Both pins and holes must be cut to length and retained as before.
- **Alternative that keeps the filament pins:** limit the drop requirement to 8 cm (pin bending SF 3.30, shear 4.68) **and** set the pretension at 3 N or less. With T0 = 3 N the stall tension is 12.9 N and pin bending SF ≈ 3.3. The script's T0 is 5 N.

## Proof test (after the change; add to spec §8)

1. **Tension (keep the spec's test; it is 2.0 × the stall tight run):** pin 5 links into a chain, hang 3 kg (29.4 N) for 1 min. Pass: no cracked knuckle, no pin bent visibly, and the chain still flexes freely to 40°.
2. **Hinge crush (new):** lay the 5-link chain grousers down on a hard surface. Press a road wheel on its bolt (or any Ø26 rod) across a pinned joint with 5 kg (≈ 49 N) for 1 min. That is 2 × the 8 cm per-axle load, or 0.6 × the 30 cm load. Pass: no cracking and the joint still flexes freely. With steel pins, also repeat at 9 kg (≈ 88 N, the 30 cm flat-drop load).

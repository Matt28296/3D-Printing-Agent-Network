VERDICT: NEEDS_TEST

# Strength check: 20261026-rover-lid

strength-analyst · 2026-10-26 · `python3 jobs/20261026-rover-lid/strength_calc.py`

**Result: NEEDS_TEST** (placeholder allowables only). Lowest SF **3.27**: the side rail's root, across layers, under a 10 N sideways jumper pull. Every other case is at SF 3.75 or more, including the re-derived 30 cm drop inertia (SF 8.7).

## Part-specific load path and assumptions

- **Support:** the deck (3 mm, printed flat, so deck bending is in-plane) rests on the wall tops all round and is screwed down at the 4 corner columns.
- **Hand press (spec 20 N):**
  - Beside the ESP32 window: the 20.1 mm strip between the side wall and the window edge acts as a cantilever, 45° spread (width = 2 × length), ignoring the rail that stiffens its edge.
  - On the breadboard area: a one-way strip across the 73 mm span, simply supported, with b_eff = span/2.
  - On the seated ESP32: bearing on the two 2.4 mm end ledges.
- **USB plugging (10 N along X):** the header strips bear on the end face of the window.
- **Sideways jumper pull (10 N):** the PCB edge bears on one rail over at least half the board length. The rail root bends vertically, which is across layers, with Kt 2.5 at the sharp root.
- **Pushing jumpers on from below** lifts the board against its zip tie: 20 N on the slot ligament.
- **Handling:** a rover lifted by the lid is held by 4 screw heads, at 2 × weight.
- **Drop (missed by the spec):** the lid, ESP32, breadboard, driver and buck (65 g) at 120 g. Load on the deck and on the end ledges, and on the screws if the rover lands on its side or back.
- **Not a lid-strength issue, but a design risk:** the ESP32 module and USB stand 7.6 mm above the deck, against 4.1 mm for the rails. An upside-down landing therefore hits the ESP32 first, with its PCB spanning 50 mm over the window. Raising the rails to 8 mm, or adding two corner posts, would protect it.

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
| 1 | deck beside the ESP32 window, hand 20 N at the window edge | XY | 6.67 | 25.0 | 3.75 | 3.0 | OK |
| 2 | deck at breadboard centre, hand 20 N (one-way, b_eff span/2) | XY | 6.67 | 25.0 | 3.75 | 3.0 | OK |
| 3 | end ledge bearing, 20 N on the ESP32 | XY | 0.14 | 25.0 | 178.20 | 3.0 | OK |
| 4 | window end face bearing, USB 10 N (2 header strips 2.5 x 2.5) | XY | 0.80 | 25.0 | 31.25 | 3.0 | OK |
| 5 | side rail root, sideways jumper pull 10 N over 26 mm (Z) | Z | 3.82 | 12.5 | 3.27 | 3.0 | OK |
| 6 | zip-tie slot ligament shear, 20 N tie load | XY shear | 0.83 | 12.5 | 15.00 | 3.0 | OK |
| 7 | screw-head bearing, rover lifted by the lid (2.9 N per screw) | XY | 0.21 | 25.0 | 118.80 | 3.0 | OK |
| 8 | screw-hole push-through (plug shear, Z), lifted by the lid | Z shear | 0.06 | 6.2 | 113.37 | 3.0 | OK |
| 9 | deck under its own + electronics inertia, 30 cm (65 g x 120 g) | XY | 2.88 | 25.0 | 8.67 | 3.0 | OK |
| 10 | end ledge to deck, ESP32 inertia 12 N, 30 cm (Z shear) | Z shear | 0.08 | 6.2 | 75.69 | 3.0 | OK |
| 11 | screw-head bearing, deck inertia 30 cm (19 N/screw) | XY | 1.40 | 25.0 | 17.87 | 3.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, bought parts):
| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| proof 40 N beside the window | XY | 13.33 | 25.0 | 1.88 | 1.0 | OK |
| proof 40 N at breadboard centre | XY | 13.33 | 25.0 | 1.88 | 1.0 | OK |

**lowest SF 3.27 (required 3.0) at: side rail root, sideways jumper pull 10 N over 26 mm (Z)**

## Verdict and proof test

NEEDS_TEST. Every check meets its required SF on the placeholder allowables. No geometry change is required.

**Proof test (strengthens spec §8; the spec's 20 N is only 1 × service):** with the lid screwed on:
1. Press 4 kg (≈ 40 N, 2 × service) for 1 min at (a) the deck beside the ESP32 window at mid-length, and (b) the centre of the breadboard area.
2. Push the seated ESP32 sideways with 2 kg (≈ 20 N) at mid-length for 10 s each way.
3. Plug and unplug USB 10 times.

Pass: no crack or whitening at the window corners, rails, ledges or screw holes; no permanent set over 0.2 mm (straight-edge across the deck); the board stays on both ledges.

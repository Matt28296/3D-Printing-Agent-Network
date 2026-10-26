VERDICT: NEEDS_TEST

# Strength check: 20261026-rover-lid (round 2)

strength-analyst · 2026-10-26 · `python3 jobs/20261026-rover-lid/strength_calc.py`

**Result: NEEDS_TEST.** The allowables are placeholders, so PASS is not possible.
- Lowest SF **3.27**: the side rail's root, across layers, under a 10 N sideways jumper pull. This is unchanged from round 1.
- Every other row is at SF 3.75 or more.
- The 5 cm drop is trivial for the lid (20 g peak): its drop rows hold up to about 90 cm.
- No geometry change is required.

## Round 1 findings addressed

| Round 1 finding | Round 2 response | Round 2 result |
|---|---|---|
| NEEDS_TEST, rail root SF 3.27 | Lid geometry unchanged | SF 3.27 ✓ |
| Screw positions | Moved to (−13, ±30) and (100, ±30), matching the moved chassis columns (both geometry.json files agree) | Handling rows SF 100 or more ✓ |
| Deck on the walls | Walls are now 4.5 mm (inner face \|y\| 33.5) | The strip beside the window is 18.6 wide (was 20.1). Its 45°-spread cantilever stress doesn't depend on the width: SF 3.75 ✓ |
| ESP32 stands 3.5 mm proud of the rails (upside-down landing) | Not changed | Advisory only; the 5 cm design drop is the right way up. Raising the rails to 8 mm, or adding two corner posts, would still protect the board. |

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

- **Support.** The deck is 3 mm thick and printed flat, so deck bending is in-plane. It rests on the 4.5 mm wall tops all round and is screwed down at the 4 columns.
- **Hand press (spec, 20 N).**
  - Beside the ESP32 window: the strip between the side wall and the window edge is taken as a cantilever with a 45° spread (width = 2 × length), ignoring the rail that stiffens its edge.
  - On the breadboard area: a one-way strip across the 71.5 mm span, simply supported, with b_eff = span/2.
  - On the seated ESP32: bearing on the two 2.4 mm end ledges.
- **USB plugging (10 N along X):** the header strips bear on the end face of the window.
- **Sideways jumper pull (10 N):** the PCB edge bears on one rail over at least half the board length. The rail root bends vertically, which is across layers, with Kt 2.5 at the sharp root.
- **Pushing jumpers on from below** lifts the board against its zip tie: 20 N on the slot ligament.
- **Handling:** the rover is lifted by the lid, so the 4 screw heads carry 2 × its weight (re-derived 649 g).
- **Drop (5 cm, 20 g peak):** the lid, ESP32, breadboard, driver and buck (64 g) decelerate through the deck and the end ledges, and through the screws if the rover lands on its side or back.

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
| 1 | deck beside the ESP32 window, hand 20 N at the window edge | XY | 6.67 | 25.0 | 3.75 | 3.0 | OK |
| 2 | deck at breadboard centre, hand 20 N (one-way, b_eff span/2) | XY | 6.67 | 25.0 | 3.75 | 3.0 | OK |
| 3 | end ledge bearing, 20 N on the ESP32 | XY | 0.14 | 25.0 | 178.20 | 3.0 | OK |
| 4 | window end face bearing, USB 10 N (2 header strips 2.5 x 2.5) | XY | 0.80 | 25.0 | 31.25 | 3.0 | OK |
| 5 | side rail root, sideways jumper pull 10 N over 26 mm (Z) | Z | 3.82 | 12.5 | 3.27 | 3.0 | OK |
| 6 | zip-tie slot ligament shear, 20 N tie load | XY shear | 0.83 | 12.5 | 15.00 | 3.0 | OK |
| 7 | screw-head bearing, rover lifted by the lid (3.2 N per screw) | XY | 0.23 | 25.0 | 106.69 | 3.0 | OK |
| 8 | screw-hole push-through (plug shear, Z), lifted by the lid | Z shear | 0.06 | 6.2 | 101.81 | 3.0 | OK |
| 9 | deck under its own + electronics inertia, 5 cm (64 g x 20 g) | XY | 0.46 | 25.0 | 54.30 | 3.0 | OK |
| 10 | end ledge to deck, ESP32 inertia 2.0 N, 5 cm (Z shear) | Z shear | 0.01 | 6.2 | 454.13 | 3.0 | OK |
| 11 | screw-head bearing, deck inertia 5 cm (3.2 N/screw) | XY | 0.23 | 25.0 | 107.36 | 3.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, fixes, bought parts):
| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| proof 40 N beside the window | XY | 13.33 | 25.0 | 1.88 | 1.0 | OK |
| proof 40 N at breadboard centre | XY | 13.33 | 25.0 | 1.88 | 1.0 | OK |
| proof 20 N sideways on the seated ESP32: rail root | Z | 7.64 | 12.5 | 1.64 | 1.0 | OK |

- lowest SF 3.27 (required 3.0) at: side rail root, sideways jumper pull 10 N over 26 mm (Z)
- drop rows scale with the height: all of them meet their SF up to a 90.5 cm drop (design 5 cm), limited by: deck under its own + electronics inertia, 5 cm (64 g x 20 g)
- 0 of 11 verdict rows below their required SF

## Proof test (strengthens spec §8, whose 20 N is only 1 × service)

With the lid screwed on:
1. Press **4 kg (≈ 40 N, 2 × service)** for 1 min at (a) the deck beside the ESP32 window at mid-length, and (b) the centre of the breadboard area.
2. Push the seated ESP32 sideways with **2 kg (≈ 20 N)** at mid-length for 10 s each way (rail root SF 1.6 at that load).
3. Plug and unplug USB 10 times.

Pass:
- no crack or whitening at the window corners, rails, ledges or screw holes;
- no permanent set over 0.2 mm (straight-edge across the deck);
- the board stays on both ledges.

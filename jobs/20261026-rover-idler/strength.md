VERDICT: FAIL

# Strength check: 20261026-rover-idler

strength-analyst · 2026-10-26 · `python3 jobs/20261026-rover-idler/strength_calc.py` (reads the sprocket model.py the idler runs, plus ROUND_BORE)

**Result: FAIL, on the re-derived 30 cm corner drop only.** Lowest SF **2.36**: the bore bearing on the M3 threads when the front corner lands on the idler (171 N). Every operating case passes with SF ≥ 20. At an 8 cm drop the bore is at SF 8.9.

## Part-specific load path and assumptions

- **Bore:** Ø3.4 CAD (≈ 3.2 printed) running on the threads of a fully threaded M3 bolt. The bolt has to be fully threaded because its nut sits in the wall trap.
- **Bearing on threads:** taken as 0.5 × the projected area (crest contact; assumption). The bearing length is the 7 mm disc plus a 45° spread into the Ø11 hub, 10.8 mm in all.
- **Teeth:** a free idler's teeth carry only bearing drag, 0.55 N. If debris jams the idler, one tooth sees the stall pull: SF 1.88 (advisory), the same as the sprocket.
- **Advisory, owned by the chassis:** the idler's M3 bolt cantilevered 17 mm from the wall. Its bending is SF 1.78 at stall (A2-70). It yields at the 30 cm corner drop (SF 0.29) and is still under SF 1.5 at 8 cm with 8.8 steel (SF 1.10); 12.9 steel is needed.
- **Spec §4:** "2 × 10 N" on the idler. Re-derived: 19.9 N at stall, 12.9 N cyclic, plus **10 N of pretension, sustained, which the spec misses** (creep, SF 4 required; it is at SF 40).

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
| 1 | bore bearing on M3 threads, stall R 19.9 N | XY | 1.23 | 25.0 | 20.36 | 3.0 | OK |
| 2 | bore bearing, cyclic R 12.9 N | XY | 0.79 | 25.0 | 31.50 | 4.0 | OK |
| 3 | bore bearing, pretension sustained R 10 N (creep) | XY | 0.62 | 25.0 | 40.50 | 4.0 | OK |
| 4 | bore bearing, 30 cm drop, front corner 171 N | XY | 10.58 | 25.0 | 2.36 | 3.0 | **FAIL** |
| 5 | disc rim bearing under a link, 30 cm corner | XY | 6.80 | 25.0 | 3.67 | 3.0 | OK |
| 6 | tooth root, bearing drag 0.55 N (Kt 2.5) | XY | 0.74 | 25.0 | 33.62 | 4.0 | OK |
| 7 | hub end-face bearing, side 3 N | XY | 0.03 | 25.0 | 716.28 | 4.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, bought parts):
| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| tooth root if a jam loads one idler tooth with stall pull 9.9 N | XY | 13.30 | 25.0 | 1.88 | 3.0 | no |
| bore bearing, 30 cm flat 86 N | XY | 5.29 | 25.0 | 4.72 | 3.0 | OK |
| bore bearing, 30 cm corner, delta 10 (86 N) | XY | 5.29 | 25.0 | 4.72 | 3.0 | OK |
| bore bearing, 8 cm corner 46 N | XY | 2.82 | 25.0 | 8.86 | 3.0 | OK |
| FIX Ø4 brass sleeve: bore bearing, 30 cm corner | XY | 3.97 | 25.0 | 6.30 | 3.0 | OK |
| M3 bolt bending at wall face (stall R 20 N x 17) | steel σy 450 | 253.22 | 450.0 | 1.78 | 1.5 | OK |
| M3 bolt bending at wall face (30 cm corner 171 N x 17) | steel σy 640 | 2182.97 | 640.0 | 0.29 | 1.5 | no |
| M3 bolt bending at wall face (8 cm corner 46 N x 17) | steel σy 640 | 582.13 | 640.0 | 1.10 | 1.5 | no |

**lowest SF 2.36 (required 3.0) at: bore bearing, 30 cm drop, front corner 171 N**

## Verdict and changes

FAIL only because of the 30 cm corner drop.

- **Smallest change (BOM + one parameter): a Ø4/3 mm brass tube sleeve, 20 mm long, on the bolt.** ROUND_BORE 3.2 → 4.0 printed, which is 4.2 CAD. The bore bears on a smooth tube instead of thread crests: SF **6.3** at the 30 cm corner drop. It also ends the thread wear the design brief lists as a risk.
- **Or** limit the drop to 8 cm, which the chassis needs anyway: bore SF 8.9 with no change.
- Also fix the tooth-root fillet (r ≥ 0.7) in the sprocket model the idler shares, so a jammed idler survives too.

## Proof test (add to spec §8; the spec's "covered by the sprocket and drop tests" doesn't load the idler bore)

With the idler on its bolt in the chassis slot, pass a strap round the idler and pull it **rearward, horizontally**, along the track line, with 4 kg (≈ 39 N, 2 × the stall radial load) for 1 min. Pass: the idler still spins freely, its axial play is under 0.5 mm, there is no bore ovalisation over 0.1 mm, and **the idler bolt has not slid in its slot** (pen mark at the slot).

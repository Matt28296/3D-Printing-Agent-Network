VERDICT: FAIL

# Strength check: 20261026-rover-wheel

strength-analyst · 2026-10-26 · `python3 jobs/20261026-rover-wheel/strength_calc.py` (also reads print_requirements.json, for perimeters and infill)

**Result: FAIL, on the re-derived 30 cm drop only.** Lowest SF **2.38**: hoop bending of the rim shell. The rim is only 3 perimeters (1.35 mm) over 20 % gyroid, under the 86 N flat-drop line load. Everything else passes. At the spec's 25 N the rim shell is at SF 8.2, and at an 8 cm drop SF 8.9.

## Part-specific load path and assumptions

- **Construction:** the wheel is not solid. print_requirements gives 3 perimeters and 20 % gyroid. The rim (r 13.1) carries the link's line load across its 24.6 mm width.
- **Rim model:** the perimeters form the rim shell, continuous in the hoop direction (in-plane), resting on the infill as an elastic foundation. The infill is treated as a cellular solid (Gibson–Ashby, assumption): E ≈ E_s·ρ² = 72 MPa, crush allowable ≈ 25·ρ^1.5 = 2.24 MPa. With an infinite beam on an elastic foundation: M = q/(4β) and p = qβ/2.
- **Bore:** bears on M3 threads at 0.5 × projected area over the rim width (SF 10.8 at the 30 cm drop).
- **V-flange root under 3 N of skid-steer side load:** in-plane, SF 127.
- **Bolt (chassis-owned, advisory):** at the spec's 25 N an A2-70 bolt is at SF 1.41 and an 8.8 bolt at SF 2.01. At 86 N the bolt yields (8.8: SF 0.59).
- **BOM error:** the head sits on the boss at Y 32.0 and the wheel's outer face at Y 71.0. A washer plus nyloc then needs a bolt of at least 44 mm, but **an M3×40 ends at Y 72.0, too short for the nyloc. Use M3×45** (or ×50 if the chassis wall is thickened).

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
| 1 | rim shell hoop bending (perimeters), 30 cm flat 86 N | XY | 10.48 | 25.0 | 2.38 | 3.0 | **FAIL** |
| 2 | rim shell -> infill crush, 30 cm flat | infill 20% | 0.48 | 2.2 | 4.69 | 3.0 | OK |
| 3 | bore shell -> infill crush, 30 cm flat | infill 20% | 0.57 | 2.2 | 3.91 | 3.0 | OK |
| 4 | bore bearing on M3 threads, 30 cm flat | XY | 2.32 | 25.0 | 10.76 | 3.0 | OK |
| 5 | rim shell hoop bending (perimeters), weight share (sustained) 1 N | XY | 0.17 | 25.0 | 143.10 | 4.0 | OK |
| 6 | rim shell -> infill crush, weight share (sustained) | infill 20% | 0.01 | 2.2 | 281.39 | 4.0 | OK |
| 7 | bore shell -> infill crush, weight share (sustained) | infill 20% | 0.01 | 2.2 | 234.84 | 4.0 | OK |
| 8 | bore bearing on M3 threads, weight share (sustained) | XY | 0.04 | 25.0 | 645.64 | 4.0 | OK |
| 9 | V-flange root bending, side 3 N on the cone (radial stress, XY) | XY | 0.20 | 25.0 | 126.76 | 4.0 | OK |
| 10 | hub end-face bearing on the wall nut, side 3 N | XY | 0.04 | 25.0 | 578.84 | 4.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, bought parts):
| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| rim shell hoop bending (perimeters), spec 25 N | XY | 3.06 | 25.0 | 8.18 | 3.0 | OK |
| rim shell -> infill crush, spec | infill 20% | 0.14 | 2.2 | 16.08 | 3.0 | OK |
| bore shell -> infill crush, spec | infill 20% | 0.17 | 2.2 | 13.42 | 3.0 | OK |
| bore bearing on M3 threads, spec | XY | 0.68 | 25.0 | 36.90 | 3.0 | OK |
| rim shell hoop bending (perimeters), 30 cm flat, delta 10 43 N | XY | 5.24 | 25.0 | 4.77 | 3.0 | OK |
| rim shell -> infill crush, 30 cm flat, delta 10 | infill 20% | 0.24 | 2.2 | 9.38 | 3.0 | OK |
| bore shell -> infill crush, 30 cm flat, delta 10 | infill 20% | 0.29 | 2.2 | 7.83 | 3.0 | OK |
| bore bearing on M3 threads, 30 cm flat, delta 10 | XY | 1.16 | 25.0 | 21.52 | 3.0 | OK |
| rim shell hoop bending (perimeters), 8 cm flat 23 N | XY | 2.80 | 25.0 | 8.94 | 3.0 | OK |
| rim shell -> infill crush, 8 cm flat | infill 20% | 0.13 | 2.2 | 17.59 | 3.0 | OK |
| bore shell -> infill crush, 8 cm flat | infill 20% | 0.15 | 2.2 | 14.68 | 3.0 | OK |
| bore bearing on M3 threads, 8 cm flat | XY | 0.62 | 25.0 | 40.35 | 3.0 | OK |
| rim shell hoop bending (perimeters), FIX 5 perimeters, 30 cm flat 86 N | XY | 5.54 | 25.0 | 4.52 | 3.0 | OK |
| rim shell -> infill crush, FIX 5 perimeters, 30 cm flat | infill 20% | 0.33 | 2.2 | 6.88 | 3.0 | OK |
| bore shell -> infill crush, FIX 5 perimeters, 30 cm flat | infill 20% | 0.44 | 2.2 | 5.07 | 3.0 | OK |
| bore bearing on M3 threads, FIX 5 perimeters, 30 cm flat | XY | 2.32 | 25.0 | 10.76 | 3.0 | OK |
| rim shell hoop bending (perimeters), FIX 40 % infill, 30 cm flat 86 N | XY | 7.41 | 25.0 | 3.37 | 3.0 | OK |
| rim shell -> infill crush, FIX 40 % infill, 30 cm flat | infill 40% | 0.67 | 6.3 | 9.38 | 3.0 | OK |
| bore shell -> infill crush, FIX 40 % infill, 30 cm flat | infill 40% | 0.57 | 6.3 | 11.07 | 3.0 | OK |
| bore bearing on M3 threads, FIX 40 % infill, 30 cm flat | XY | 2.32 | 25.0 | 10.76 | 3.0 | OK |
| M3 bolt bending at wall face, spec 25 N x 17 | steel σy 450 | 318.30 | 450.0 | 1.41 | 1.5 | no |
| M3 bolt bending at wall face, spec 25 N x 17 | steel σy 640 | 318.30 | 640.0 | 2.01 | 1.5 | OK |
| M3 bolt bending at wall face, 30 cm flat x 17 | steel σy 640 | 1091.49 | 640.0 | 0.59 | 1.5 | no |

**lowest SF 2.38 (required 3.0) at: rim shell hoop bending (perimeters), 30 cm flat 86 N**

## Verdict and changes

FAIL only because of the 30 cm drop.

- **Smallest change (print setting, no geometry change): `perimeters` 3 → 5** in print_requirements.json. Rim shell: SF 2.38 → **4.52** at the 30 cm drop, and every other row is at SF 5 or more. Raising `fill_density` from 20 % to 40 % also works but less well (SF 3.37).
- **BOM:** M3×45 bolts, class 12.9 (black alloy steel), not A2 stainless. See the chassis report.
- With the drop limited to 8 cm, the current settings pass (lowest SF 8.9).

## Proof test (add to spec §8; it isolates the wheel from the chassis)

Put the wheel on an M3×45 bolt supported at **both** ends, so that the bolt does not bend: for example through a scrap block on each side, or between vise jaws. Hang 13 kg (≈ 128 N, 1.5 × the 30 cm flat-drop load) from a strap over the rim, centred on the rim width, for 1 min. Pass: no crack or dent in the rim (no ring of crushed infill), bore ovalisation under 0.1 mm, and the wheel spins freely afterwards. If the drop is limited to 8 cm, use 5 kg (2 × 23 N).

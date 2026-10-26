VERDICT: FAIL

# Strength check: 20261026-rover-chassis

strength-analyst · 2026-10-26 · `python3 jobs/20261026-rover-chassis/strength_calc.py`

**Result: FAIL.** Lowest SF **0.19**: wall bending across layers round the idler block in the 30 cm front-corner drop. **The road-wheel bosses fail even at the spec's own 25 N (SF 0.83)**, and the spec's proof test (2 kg hung 17 mm out) loads them to SF 1.06 on the knocked-down allowable. Apart from the drop, the motor wall fails at stall (SF 1.98) and everyday (3.06; 4 required), and the M1.6 head bearing fails at stall (2.59).

## Part-specific load path and assumptions

- **Cantilevered axles:** every wheel and idler hangs on an M3 bolt cantilevered 17 mm from the wall face; the load line is the track centre, Y 55. The bolt clamps a 3 mm wall plus a 3 mm boss, with the nut in a trap in the outer face. The PETG preload creeps away, so the moment M = F × 18.5 mm (to the wall mid-plane) enters the wall as a moment on a rigid boss.
- **Wall bending model (Kirchhoff, rigid inclusion in a large plate):** m_max = M/(2πa) and σ = Kt·6m/t². Kt is 2 at the unfilleted step from the 6 mm boss to the 3 mm wall.
  - A **vertical** load (weight, drop) gives a moment about X, so the wall stress is vertical: **across layers** (12.5 MPa). The walls print standing on the floor.
  - A **horizontal** track load gives a moment about Z, so the stress is horizontal: in-plane (25 MPa).
  - A strip model with no Kt (advisory) gives SF 0.53 at 25 N, so the FAIL does not depend on the plate model.
- **Nut and hole edge:** with no preload, the bolt is held by a couple between the trapped nut (Y 36.7) and the inner hole edge (Y 32.75). That is compressive bearing on the 2.4 × 5.5 mm nut flats.
- **N20:** the gearbox face is screwed to the wall with 2 × M1.6, and the sprocket radial load acts 20 mm outboard.
  - Track load: the far screw takes the prying, and the wall round the 12 × 10 face bends in-plane. Kt 2: the screw holes are 1.5 mm from the edge of the gearbox face.
  - Drop on the sprocket: the motor pivots on the cradle under the can, so the screws carry 2.2 × F in bearing in the 3 mm wall.
  - Advisory: the cradle's zip tie could take some of the moment; no credit is taken for it.
- **Floor:** the battery (135 g) at the drop deceleration loads a one-way strip across the 70 mm span, simply supported, with its width set by the holder length. The strap slot (22 mm, square ends, Kt 2.5) cuts the section where the moment is still high.
- **Idler slot clamp (advisory):** it must hold 2·T0 sustained and the 19.9 N stall load by friction alone. With an assumed 100 N of preload left after creep, the stall load is at SF 2.0, so the idler can slide back and slacken the track. Consider a small jack screw or ratchet teeth in the slot.
- **Bolts:** the spec gives no grade. A2-70 stainless is assumed in the verdict rows, because it is the commonest hobby M3.

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
| 1 | road-wheel boss rim, wall bending, spec 25 N (Kt 2 sharp step) | Z | 15.10 | 12.5 | 0.83 | 3.0 | **FAIL** |
| 2 | road-wheel boss rim, 30 cm flat 86 N | Z | 51.78 | 12.5 | 0.24 | 3.0 | **FAIL** |
| 3 | road-wheel boss rim, weight share x2 sustained 1.4 N | Z | 0.86 | 12.5 | 14.48 | 4.0 | OK |
| 4 | road-wheel boss rim, side drag 3 N at flange r16 (moment about X) | Z | 1.58 | 12.5 | 7.93 | 4.0 | OK |
| 5 | nut / hole-edge bearing, no preload, spec 25 N (compression) | XY | 10.67 | 25.0 | 2.34 | 3.0 | **FAIL** |
| 6 | nut / hole-edge bearing, 30 cm flat | XY | 36.58 | 25.0 | 0.68 | 3.0 | **FAIL** |
| 7 | M3 bolt (A2-70, grade not in BOM) bending at wall, spec 25 N x 17 | steel σy 450 | 318.30 | 450.0 | 1.41 | 1.5 | **FAIL** |
| 8 | M3 bolt bending at wall, 30 cm flat | steel σy 450 | 1091.49 | 450.0 | 0.41 | 1.5 | **FAIL** |
| 9 | idler block, track tension stall R 19.9 N (in-plane, Kt 2) | XY | 7.62 | 25.0 | 3.28 | 3.0 | OK |
| 10 | idler block, cyclic R 12.9 N | XY | 4.93 | 25.0 | 5.08 | 4.0 | OK |
| 11 | idler block, pretension sustained R 10 N | XY | 3.83 | 25.0 | 6.53 | 4.0 | OK |
| 12 | idler block, 30 cm front corner 171 N (Z) | Z | 65.68 | 12.5 | 0.19 | 3.0 | **FAIL** |
| 13 | idler M3 bolt bending, 30 cm corner | steel σy 450 | 2182.97 | 450.0 | 0.21 | 1.5 | **FAIL** |
| 14 | M1.6 face screw tension (prying), stall R 19.9 N | steel σy 450 | 29.83 | 450.0 | 15.09 | 1.5 | OK |
| 15 | M1.6 head bearing on wall, stall | XY | 9.65 | 25.0 | 2.59 | 3.0 | **FAIL** |
| 16 | M1.6 head bearing on wall, cyclic | XY | 6.24 | 25.0 | 4.01 | 4.0 | OK |
| 17 | wall round gearbox face, stall (in-plane, Kt 2 screw holes) | XY | 12.63 | 25.0 | 1.98 | 3.0 | **FAIL** |
| 18 | wall round gearbox face, cyclic | XY | 8.17 | 25.0 | 3.06 | 4.0 | **FAIL** |
| 19 | wall round gearbox face, pretension sustained | XY | 6.35 | 25.0 | 3.94 | 4.0 | **FAIL** |
| 20 | M1.6 screws bearing in wall, 30 cm rear corner on sprocket (376 N) | XY | 39.19 | 25.0 | 0.64 | 3.0 | **FAIL** |
| 21 | floor mid-span under battery, 30 cm (120 g x 135 g) | XY | 24.52 | 25.0 | 1.02 | 3.0 | **FAIL** |
| 22 | floor at strap slot (Kt 2.5 square ends), 30 cm | XY | 43.34 | 25.0 | 0.58 | 3.0 | **FAIL** |
| 23 | lid-screw pull-out of column pilot, handling 2.9 N | XY shear | 0.05 | 12.5 | 250.11 | 3.0 | OK |
| 24 | lid column tension (Z), handling | Z | 0.06 | 12.5 | 192.94 | 3.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, bought parts):
| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| BOUND: strip model, boss rim, spec 25 N (lower stub only, no Kt) | Z | 23.72 | 12.5 | 0.53 | 3.0 | no |
| road-wheel boss rim, 30 cm flat, delta 10 (43 N) | Z | 25.89 | 12.5 | 0.48 | 3.0 | no |
| road-wheel boss rim, 8 cm flat 23 N | Z | 13.81 | 12.5 | 0.91 | 3.0 | no |
| spec proof test: 2 kg hung 17 mm out (19.6 N), boss rim | Z | 11.84 | 12.5 | 1.06 | 1.0 | OK |
| idler slot clamp friction (P 100 N after creep, mu 0.2, 2 faces) vs stall R | friction N | 19.89 | 40.0 | 2.01 | 3.0 | no |
| idler slot clamp friction vs pretension (sustained) | friction N | 10.00 | 40.0 | 4.00 | 4.0 | OK |
| floor mid-span, 8 cm (32 g) | XY | 6.54 | 25.0 | 3.82 | 3.0 | OK |
| floor at strap slot (Kt 2.5), 8 cm | XY | 11.56 | 25.0 | 2.16 | 3.0 | no |
| M1.6 screws bearing in wall, 8 cm rear corner (100 N) | XY | 10.45 | 25.0 | 2.39 | 3.0 | no |
| idler M3 bolt 8.8, 8 cm corner 46 N | steel σy 640 | 582.13 | 640.0 | 1.10 | 1.5 | no |
| FIX wall 4.5/boss Ø20 r2: boss rim, spec 25 N | Z | 3.40 | 12.5 | 3.67 | 3.0 | OK |
| FIX wall 4.5/boss Ø20 r2: boss rim, 8 cm flat 23 N | Z | 3.11 | 12.5 | 4.02 | 3.0 | OK |
| FIX wall 4.5/boss Ø20 r2: boss rim, 30 cm flat | Z | 11.67 | 12.5 | 1.07 | 3.0 | no |
| FIX wall 4.5: idler block, 8 cm corner 46 N | Z | 6.07 | 12.5 | 2.06 | 3.0 | no |
| FIX wall 4.5 + idler block 30x24 to the floor: 8 cm corner | Z | 4.11 | 12.5 | 3.04 | 3.0 | OK |
| FIX Ø4 washer under each M1.6 head: head bearing, stall | XY | 4.02 | 25.0 | 6.22 | 3.0 | OK |
| FIX wall 4.5: nut bearing, spec 25 N | XY | 8.25 | 25.0 | 3.03 | 3.0 | OK |
| FIX M3 12.9 bolt, 8 cm corner 46 N | steel σy 1080 | 582.13 | 1080.0 | 1.86 | 1.5 | OK |
| FIX cradle cheek 4 mm (Z), stall, 22 N | Z | 3.99 | 12.5 | 3.14 | 3.0 | OK |
| FIX gearbox cap: 2 x M2 pull-out of cradle, 8 cm corner | XY shear | 1.25 | 12.5 | 10.02 | 3.0 | OK |
| FIX strap slots at |y| 27.5: floor at slot, 8 cm | XY | 6.93 | 25.0 | 3.61 | 3.0 | OK |

**lowest SF 0.19 (required 3.0) at: idler block, 30 cm front corner 171 N (Z)**

## Verdict and changes

FAIL. **The 30 cm hard-floor drop cannot be met by this architecture.** A 3 mm wall printed standing carries every axle moment across its layers, and the battery leaves no room for cross-ribs or through-axles. Even with the geometry fixes below, the road-wheel boss is at SF 1.07 at 30 cm. Smallest set that reaches NEEDS_TEST:

1. **Requirement: limit the drop acceptance to 8 cm onto a hard floor** (≈ 25 N per axle, the spec's own design value), or 30 cm onto something that gives at least 17 mm.
2. **Geometry, side walls:** WALL 3 → 4.5 mm on the side walls from X ≈ 25 forward, thickened inward so the wheel gap is unchanged. The motor zone stays 3 mm, keeping the N20 face at Y 35. Road-wheel bosses Ø13 → Ø20 (merging into the floor), with r 2 fillets (Kt 1.5). Boss rim SF: 0.83 → **3.67** at 25 N, **4.02** at an 8 cm drop.
3. **Geometry, idler:** idler block 22 × 15 → 30 × 24, running down to the floor. 8 cm corner: SF **3.04**.
4. **Geometry, motor:** **4 mm side cheeks on the motor cradle** beside the can (SF 3.14 for the in-plane moment), plus a **screwed cap over the gearbox** (2 × M2 into the cradle, SF 10). The gearbox body then carries the loads, not the M1.6 screws or the wall. **Ø4 washers under the M1.6 heads** (SF 2.59 → 6.2).
5. **Geometry, floor:** move the strap slots out from |y| 22.5 to 27.5. Floor at the slot, 8 cm drop: SF 2.16 → **3.61**. Mid-span: SF 3.82.
6. **BOM:** **M3×45, class 12.9** (σy ≈ 1080). At the 8 cm corner: SF 1.86. A2-70 is at SF 1.41 even at 25 N, and 8.8 is at SF 1.10 at the 8 cm corner. With the 4.5 mm wall, use M3×50.

The N20 output shaft (20 mm overhang, bought part) is at SF 1.30 on an 8 cm corner drop (advisory, sprocket report). To protect it, raise the sprocket axle about 3 mm so that it doesn't ride on the ground run (the assembly check must then be re-run), or accept the risk.

## Proof test (after the changes; replaces spec §8's)

1. **Wheel bolt and boss:** with a road wheel on its bolt, hang 5 kg (49 N, 2 × 25 N) from the bolt end next to the wheel, 17 mm out, for 1 min. Repeat on the idler bolt at mid-slot. Pass: no crack or whitening at the boss, nut trap or floor junction; the bolt still square to the wall (≤ 0.5 mm runout at its tip); the idler not slid in its slot.
2. **Motor:** hold the track and stall at 100 % PWM on a fresh pack for 3 s, 5 times. Pass: no movement of the gearbox on the wall, no cracking round the face screws.
3. **Drop:** from **8 cm** onto a hard floor, assembled with battery and lid, once flat and once on each front and rear corner. Pass: no cracks, bolts square, tracks stay on, all wheels spin.

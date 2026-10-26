VERDICT: FAIL

# Strength check: 20261026-rover-chassis (round 2)

strength-analyst · 2026-10-26 · `python3 jobs/20261026-rover-chassis/strength_calc.py` · round-1 method, round-2 design and loads

**Result: FAIL**, with 7 of 26 rows below their required SF.

The lowest SF is **0.49**, in the **N20 cradle cheeks**. The new journal now loads them:
- they are 2 mm thick;
- they rest on the cradle over only 0.7 mm;
- they are held at their front end only.

The other five failures are the **5 cm corner drop** (31.8 N per axle) and the **reverse stall on the idler** (29.8 N):
- road-wheel boss rim: SF 2.16;
- nut and hole-edge bearing: SF 1.84;
- A2-70 bolts: SF 1.11 at the corner drop and 1.19 at the reverse stall;
- the idler's friction-only slot clamp: SF 1.34.

The nut row limits the whole drop to **3.1 cm** on this method.

These all pass: the flat 5 cm drop (SF 3.7 or more), the journal, the floor, the idler block, the handling cases, and the cradle floor under a drop.

## Round 1 findings addressed

| Round 1 finding | Round 2 response | Round 2 result |
|---|---|---|
| Road-wheel boss, 25 N: SF 0.83 | Wall 4.5, Ø20 bosses down to the floor | Flat landing: SF 4.33 ✓. Corner landing (now in spec §4): **2.16 ✗**. Round 1's fix assumed r 2 rim fillets (Kt 1.5); the model's rim step is sharp. |
| Idler block, 30 cm corner: SF 0.19 | 30 × 24 block down to the floor (25.5 × 24 up to the front wall) | 5 cm corner: SF 3.02 ✓ |
| N20 face screws: prying, head bearing 2.59, wall 1.98, drop 0.64 | Screws removed; cradle plus journal | Those rows are gone ✓. The cradle cheeks now carry the lever reaction: **0.49 ✗** |
| Floor at the strap slot: SF 0.58 | Slots moved to \|y\| 27.5; 5 cm drop | SF 7.21 ✓ |
| Nut / hole-edge bearing: SF 2.34 | None (round 1's fix assumed 4.5 + 3 mm; the model has 4.5 + 1.5) | 5 cm corner: **1.84 ✗** |
| A2-70 bolts | M3 × 45, still no grade in the spec | 5 cm corner: **1.11 ✗**; idler at reverse stall: **1.19 ✗** |
| Idler clamp friction (advisory, 2.01) | No change; spec §4 now loads it with 2 × 14.9 N | **1.34 ✗** |
| 30 cm drop impossible | Requirement cut to 5 cm | Drop loads ÷ 5.4: height ÷ 6, mass up 11 % (583 → 649 g). Corner load 171 → 31.8 N |

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

- **Cantilevered axles.** Each road wheel and idler hangs on an M3 bolt. The head sits inside on the 1.5 mm boss (Y 32.0) and the nut in a trap in the outer face (Y 35.4 to 38). The load line is the track centre at Y 55: 17 mm from the outer face and 19.25 mm from the wall mid-plane.
- **Wall bending.** The model treats the boss as a rigid inclusion in a large plate (Kirchhoff): m_max = M/(2πa), σ = Kt·6m/t², with a = 10 for the Ø20 boss and Kt 2 for the sharp 1.5 mm step.
  - A vertical load (drop) gives stress up the wall, **across the layers** (12.5 MPa): the chassis prints floor-down.
  - The bound row treats the boss block as a strip down to the floor (6 × 20, no Kt) and gives SF 2.45. So the failure doesn't depend on the plate model.
- **Nut and hole edge.** PETG creep removes the preload, as in round 1. The bolt is then held by a couple between the trapped nut (Y 36.7) and the inner hole edge (Y 32.75). That lever is only 3.95 mm, so the nut flat (2.4 × 5.5) carries 5.6 × the axle load.
- **Journal lever (new).** The hub (Ø10, 0.25 mm radial clearance) can't carry the overhung load as a cantilever in a 6 mm journal: it would have to tilt 4.8°. Instead the hub, shaft and N20 tilt as one body:
  - it pivots on the motor's can end (Y 7) and bears on the journal's outer end (Y 38);
  - journal load = 1.55 R, can-end load = 0.55 R;
  - in a drop the can end presses on the cradle floor (solid to the floor, SF 28);
  - under track pull (horizontal) it presses on a cheek.
- **Cradle cheeks.** The cheeks are 2 mm thick at x 6.3 to 8.3. The cradle block is only ±7.0, so each cheek sits on it over **0.7 mm** and overhangs the rest. There is also a 0.3 mm gap to the rear-stop posts. That leaves the cheek's front end on the journal boss as its only real support: a 25 mm cantilever, 8 mm tall and 2 mm thick, loaded by the can end.
  - At the stall (10.9 N) the cheek reaches 51 MPa, SF 0.49.
  - Under the sustained pretension alone (5.5 N) it reaches SF 0.97.
  - What happens: the motor yaws until its gearbox face edge hits the journal boss (about 2.5°). That bends the cheek and runs the sprocket about 0.8 mm out of plane at the tooth tips, against 0.5 mm of notch clearance.
  - Zip-tie friction may hold the motor at first; it is not credited.
- **Idler clamp.** In reverse both idler runs are tight, so 29.8 N pulls the bolt rearward along its slot, held only by head and nut friction. The model assumes 100 N of clamp is left after creep, with μ 0.2, giving SF 1.34. SF 3 would need 223 N of clamp left after creep, which PETG won't keep. If the clamp slips, the track goes slack by up to 8 mm and can jump teeth (sprocket report: a tooth tip loaded on a slack track is SF 2.17).
- **Bolts.** No grade is given, so A2-70 is assumed (the commonest hobby M3). The bolts are fully threaded at the wall (the nut sits there), so bending uses the minor diameter, 2.387 mm.

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
| 1 | road-wheel boss rim, wall bending, 5 cm flat 15.9 N (Kt 2 sharp step) | Z | 2.89 | 12.5 | 4.33 | 3.0 | OK |
| 2 | road-wheel boss rim, wall bending, 5 cm corner 31.8 N (Kt 2) | Z | 5.78 | 12.5 | 2.16 | 3.0 | **FAIL** |
| 3 | road-wheel boss rim, weight share x2 sustained 1.6 N | Z | 0.29 | 12.5 | 43.27 | 4.0 | OK |
| 4 | road-wheel boss rim, side drag 3 N at flange r16.1 (moment about X) | Z | 0.46 | 12.5 | 27.44 | 4.0 | OK |
| 5 | nut / hole-edge bearing (wheel traps and idler slot), no preload, 5 cm flat | XY | 6.79 | 25.0 | 3.68 | 3.0 | OK |
| 6 | nut / hole-edge bearing, 5 cm corner | XY | 13.58 | 25.0 | 1.84 | 3.0 | **FAIL** |
| 7 | M3 bolt (A2-70; no grade in the spec) bending at the wall, 5 cm flat x 17 | steel σy 450 | 202.57 | 450.0 | 2.22 | 1.5 | OK |
| 8 | M3 bolt (A2-70) bending at the wall, 5 cm corner (road wheel or idler) | steel σy 450 | 405.13 | 450.0 | 1.11 | 1.5 | **FAIL** |
| 9 | idler block, reverse stall R 29.8 N (in-plane, Kt 2) | XY | 3.87 | 25.0 | 6.45 | 3.0 | OK |
| 10 | idler block, cyclic R 16.4 N | XY | 2.13 | 25.0 | 11.74 | 4.0 | OK |
| 11 | idler block, pretension sustained R 10 N | XY | 1.30 | 25.0 | 19.22 | 4.0 | OK |
| 12 | idler block, 5 cm front corner 31.8 N (Z, Kt 2) | Z | 4.14 | 12.5 | 3.02 | 3.0 | OK |
| 13 | idler M3 bolt (A2-70) bending, reverse stall R 29.8 N x 17 | steel σy 450 | 379.12 | 450.0 | 1.19 | 1.5 | **FAIL** |
| 14 | idler slot clamp friction (P 100 N after creep, mu 0.2, 2 faces) vs reverse stall R | friction N | 29.78 | 40.0 | 1.34 | 3.0 | **FAIL** |
| 15 | idler slot clamp friction vs pretension 2 T0 (sustained) | friction N | 10.00 | 40.0 | 4.00 | 4.0 | OK |
| 16 | journal bearing, stall (hub 19.9 N -> journal 30.8 N at its outer end) | XY | 1.03 | 25.0 | 24.35 | 3.0 | OK |
| 17 | journal bearing, pretension sustained (hub 10.0 N -> journal 15.5 N at its outer end) | XY | 0.52 | 25.0 | 48.44 | 4.0 | OK |
| 18 | journal bearing, 5 cm rear corner on the sprocket (journal 49 N) | XY | 1.64 | 25.0 | 15.22 | 3.0 | OK |
| 19 | wall round the journal, bearing 3 mm off its mid-plane, 5 cm corner (Z, Kt 2) | Z | 1.25 | 12.5 | 9.99 | 3.0 | OK |
| 20 | N20 cradle cheek as built (front end only), stall: can end 10.9 N | XY | 51.12 | 25.0 | 0.49 | 3.0 | **FAIL** |
| 21 | N20 cradle cheek as built, pretension sustained: can end 5.5 N | XY | 25.71 | 25.0 | 0.97 | 4.0 | **FAIL** |
| 22 | cradle top under the N20 can end, 5 cm rear corner (17.4 N, can flat 6.6 x 3) | XY | 0.88 | 25.0 | 28.51 | 3.0 | OK |
| 23 | floor mid-span under battery, 5 cm (20 g x 135 g) | XY | 3.84 | 25.0 | 6.51 | 3.0 | OK |
| 24 | floor at strap slot Y ±27.5 (Kt 2.5 square ends), 5 cm | XY | 3.47 | 25.0 | 7.21 | 3.0 | OK |
| 25 | lid-screw pull-out of column pilot, handling 3.2 N | XY shear | 0.06 | 12.5 | 224.61 | 3.0 | OK |
| 26 | lid column tension (Z), handling | Z | 0.07 | 12.5 | 173.27 | 3.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, fixes, bought parts):
| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| BOUND: strip model, boss block to the floor (6 x 20, no Kt), 5 cm corner | Z | 5.10 | 12.5 | 2.45 | 3.0 | no |
| road-wheel boss rim, 5 cm corner, stiff landing delta 2.5 (64 N) | Z | 11.55 | 12.5 | 1.08 | 3.0 | no |
| nut / hole-edge bearing at the spec's 29 N corner | XY | 12.38 | 25.0 | 2.02 | 3.0 | no |
| cheek bottom edge as built (0.7 mm on the cradle, Z, no Kt), stall | Z | 66.78 | 12.5 | 0.19 | 3.0 | no |
| FIX road-wheel boss Ø20 + r1.5 fillet only (DFM round-2 fix 3 alone): 5 cm corner | Z | 4.33 | 12.5 | 2.88 | 3.0 | no |
| FIX road-wheel boss Ø26 + r1.5 fillet (or 2 x 45° chamfer) round the rim: 5 cm corner | Z | 3.33 | 12.5 | 3.75 | 3.0 | OK |
| FIX road-wheel boss Ø30, sharp rim: 5 cm corner | Z | 3.85 | 12.5 | 3.25 | 3.0 | OK |
| FIX BOSS_IN 1.5 -> 5.5 at the wheel bosses and idler block: nut bearing, 5 cm corner | XY | 7.96 | 25.0 | 3.14 | 3.0 | OK |
| FIX strap slots Y ±27.5 -> ±26 (clear the thicker bosses): floor at slot, 5 cm | XY | 4.33 | 25.0 | 5.77 | 3.0 | OK |
| FIX M3 class 8.8 bolt, 5 cm corner 31.8 N x 17 | steel σy 640 | 405.13 | 640.0 | 1.58 | 1.5 | OK |
| FIX M3 class 12.9 bolt, 5 cm corner 31.8 N x 17 | steel σy 1080 | 405.13 | 1080.0 | 2.67 | 1.5 | OK |
| FIX M3 class 8.8 idler bolt, reverse stall 29.8 N | steel σy 640 | 379.12 | 640.0 | 1.69 | 1.5 | OK |
| FIX M3 tensioner screw along X through the idler block (11 mm thread, Ø2.6 pilot), reverse stall (thread shear, Z) | Z shear | 0.57 | 6.2 | 10.88 | 3.0 | OK |
| FIX cheek 2 mm standing fully on the cradle (CRADLE_HALF_X >= 8.3), stall (Z, Kt 2) | Z | 16.36 | 12.5 | 0.76 | 3.0 | no |
| FIX cheek 3 mm standing fully on the cradle (CRADLE_HALF_X >= 9.3), stall (Z, Kt 2) | Z | 7.27 | 12.5 | 1.72 | 3.0 | no |
| FIX cheek 4 mm standing fully on the cradle (CRADLE_HALF_X >= 10.3), stall (Z, Kt 2) | Z | 4.09 | 12.5 | 3.06 | 3.0 | OK |
| FIX cheek 4 mm on the cradle, pretension sustained | Z | 2.06 | 12.5 | 6.08 | 4.0 | OK |
| proof 5 kg (49 N) on the wheel rim: boss Ø26 r1.5 | Z | 5.14 | 12.5 | 2.43 | 1.0 | OK |
| proof 5 kg on the wheel rim: nut bearing, BOSS_IN 5.5 | XY | 12.27 | 25.0 | 2.04 | 1.0 | OK |

- lowest SF 0.49 (required 3.0) at: N20 cradle cheek as built (front end only), stall: can end 10.9 N
- drop rows scale with the height: all of them meet their SF up to a 3.1 cm drop (design 5 cm), limited by: nut / hole-edge bearing, 5 cm corner
- 7 of 26 verdict rows below their required SF

## Required changes (each one is a FIX row above)

1. **BOM: M3 × 45, fully threaded, class 8.8 or better; 12.9 recommended.** The 5 cm corner goes from SF 1.11 to 1.58 with 8.8, or 2.67 with 12.9. The idler at reverse stall goes from SF 1.19 to 1.69. The spec must name the grade.
2. **Road-wheel bosses: `ROAD_BOSS_R` 10 → 13 (Ø26), with an r ≥ 1.5 fillet or a 2 × 45° chamfer round the boss rim (Kt 1.5).** Boss rim at the 5 cm corner: SF 2.16 → **3.75**. Without the rim fillet it needs Ø30 (`ROAD_BOSS_R` 15): SF 3.25. The idler block already passes (3.02). The DFM round-2 fix 3 alone (r 1.5 fillets on the Ø20 bosses) gives SF 2.88, so the boss must grow as well.
3. **Nut traps: `BOSS_IN` 1.5 → 5.5 at the four road-wheel bosses and the idler block only.** The journal boss stays 1.5. Nut and hole-edge bearing at the 5 cm corner: SF 1.84 → **3.14**.
   - The bolt heads move to Y 28.0, so the bolts become **M3 × 50**.
   - Move the strap slots (`STRAP_Y`) from 27.5 to 26 so they clear the thicker bosses: floor at the slot SF 5.77.
4. **Idler: add a positive stop.** Fit an M3 tensioner screw along X from the idler block's rear face at X 105 into the slot, with its tip on the idler bolt (Ø2.6 pilot, 11 mm of thread). Thread shear across the layers: SF 10.9 at 29.8 N. It also sets the track tension. The friction clamp then only has to locate the bolt.
5. **N20 cradle: `CHEEK_T` 2 → 4 and `CRADLE_HALF_X` 7 → 10.3**, so each cheek stands fully on the cradle. Close the 0.3 mm gap to the rear-stop posts.
   - Stall: SF 0.49 → **3.06**. Sustained: SF 6.08.
   - 4 mm is the minimum: 3 mm gives SF 1.72, and 5 mm would give about 4.8.
   - The DFM round-2 fix 2 alone (`CRADLE_HALF_X` 8.3 under the unchanged 2 mm cheek) stands the cheek on the cradle but gives only SF 0.76.
   - The zip-tie tunnel (±11) still exits outside the cheeks.

Re-run `assembly_check.py` after items 2, 3 and 5. By hand, the thicker bosses and cheeks clear the bolt heads, the battery (\|y\| ≤ 20.5), the HC-SR04 and the lid columns (X 96 to 104), but the assembly check must confirm it.

## Proof test (after the changes; replaces spec §8 item (1) and the load in (2))

1. **Axle bolt and boss.** With a road wheel on its bolt, hang **5 kg (49 N, 1.5 × the 31.8 N corner load)** for 1 min from a strap round the **middle of the wheel rim**, on the track centre plane 17 mm from the wall. The spec's "from the bolt end" would double the moment. Repeat on an idler bolt at mid-slot. Pass:
   - no crack or whitening at the boss, nut trap or floor fillet;
   - the bolt still square, with 0.5 mm or less runout at its tip;
   - the idler bolt not moved (pen mark).
2. **Stall.** Tension the track and stall each motor for 3 s, 5 times, **at 100 % PWM on a freshly charged pack** (about 182 N·mm, 1.14 × the design value and the most the N20 can give). The spec's 80 % gives only 146 N·mm, below the 160 design value. Do it **forward and in reverse**: reverse loads the idler with both runs tight. Pass:
   - no motor movement in the cradle (pen marks on can and cheek);
   - no crack at the journal or cheeks;
   - the idler bolt not slid;
   - the sprocket not slipped on its shaft.
3. **Drop (as spec §8).** Drop the assembled rover from 5 cm onto a hard floor, flat and on each of the four corners. Pass: no cracks, bolts square, tracks on, the sprockets run true with no visible wobble, motors not shifted, every wheel spins freely.

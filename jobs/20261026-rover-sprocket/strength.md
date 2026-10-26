VERDICT: FAIL

# Strength check: 20261026-rover-sprocket (round 2)

strength-analyst · 2026-10-26 · `python3 jobs/20261026-rover-sprocket/strength_calc.py` · round-1 method, round-2 design and loads

**Result: FAIL**, with 7 of 18 rows below their required SF. The lowest SF is **1.06**: the M2 set-screw hole in the hub at the 5 cm corner drop. Two problems remain:
- **The torque still goes through a printed D-flat.** SF 1.24 at stall, 3.84 everyday (4 required). No printed bore can pass: SF 3 at 160 N·mm needs 23 mm of flat, and the N20 shaft is 10 mm long.
- **The journal turns the PETG hub into a lever that bends across its layers.**
  - At the set-screw hole: SF 1.69 at stall, 2.56 cyclic, 3.37 sustained, 1.06 at the 5 cm corner.
  - Just outboard of the shaft end: SF 2.83 at the 5 cm corner.

What passes:
- the chamfered teeth: SF 3.15 at stall;
- the hub bearing in the journal: SF 15 or more;
- the disc rim: SF 19.8.

## Round 1 findings addressed

| Round 1 finding | Round 2 response | Round 2 result |
|---|---|---|
| D-flat torque at stall, SF 0.85 | 9.5 mm engagement (was 6.5), press fit, M2 set screw | **1.24 ✗**. A metal hub is still required. |
| Bore rocking under the overhung load (1.85; 0.21 at 30 cm) | The Ø10 hub runs in a 6 mm wall journal | The rocking is gone: the hub bears on the journal at SF 15 or more ✓. The hub itself is now the lever arm: **2.83 ✗ at the shaft end, 1.06 ✗ at the set-screw hole**. |
| Sharp tooth root, SF 1.88 | 0.5 × 45° root chamfers | **3.15 ✓** (Kt 1.8). It would be 2.84 if the chamfer behaved like a sharp corner. |
| N20 shaft at the drop (advisory, 1.30 at 8 cm) | Journal | The shaft moment falls from 23.5 R to 13.4 R: SF 1.64 at the 5 cm corner on σy 350. That holds only if the motor can pivot in its cradle. A zip tie pulled tight enough to clamp the motor stops the journal engaging: SF 0.94. |
| M1.6 heads against the hub (DFM) | Face screws removed | ✓. New interference: the hub end sits 0.5 mm from the gearbox face, but the N20 bearing boss (Ø4) stands 0.8 mm proud, an **overlap of 0.3 mm**. The assembly check skips the motor/sprocket pair, so it can't see this. |

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

- **Torque.** The press-fit D-bore is Ø3.2 in CAD and prints at about Ø3.0, with the flat line-to-line. Friction is not credited (round-1 method), so all the torque goes through the flat.
  - Model: rigid rotation against the flat, pressure rising from zero at its centre to p_max at one edge, T = p_max·L·b²/3. The table reports the mean over the loaded half.
  - The bore is vertical in print, so this bearing is in-plane.
- **The set screw cannot bite the flat.** A CAD probe shows the set-screw hole along +X and the D-flat facing +Y: the screw lands **90° from the flat**, on the round of the shaft. It holds by friction only, which is enough for the 3 N axial retention (SF 4.0). Spec §8's "set screw bites the flat" cannot be met.
- **Hub as a lever.** The track or ground load R acts on the track plane (Y 55). The hub bears on the journal's outer end (Y 38), and the N20 body reacts at its can end on the cradle. Journal load = 1.55 R; N20 shaft moment at the face = 13.4 R.
  - Outboard of the shaft end (Y 41.5) only PETG carries R: M = 13.5 R. The ring there is Ø10 with the Ø3.2 bore, Z = 97.1 mm³.
  - At the set-screw hole (Y 40.5): M = 14.5 R. The radial Ø1.8 hole leaves Z = 78.2 mm³ on the net section, with Kt 2 for a hole in a tough material. The shaft ends 1 mm further out, so it is given no share of the moment.
  - The hub is printed upright, so this bending stress is **across the layers**.
  - The hub turns under a fixed load, so every fibre sees **rotating bending, once per revolution**.
- **Teeth.** The critical section is the top of the 0.5 × 45° chamfer: 2.7 × 7 mm at r 12.39.
  - Load: the stall pull (9.89 N) on one tooth at the pitch radius, the round-1 convention.
  - Kt 1.8: c/h is 0.19, which lies between the skill's 2.5 for a sharp corner and 1.5 for r ≥ 0.25 h. A chamfer is a little worse than a fillet of the same size.
- **Spec §4's tooth case (14.9 N on one tooth tip) cannot occur.** The engaged teeth together carry the tight-run tension minus the slack-run tension, 9.9 N. The case is kept as advisory (SF 1.44).
  - Ask the Architect to change §4 to 9.9 N at the pitch radius.
  - The physical tip case is a link riding over a tooth on a slack track: 9.9 N at the tip, SF 2.17. A positive idler stop (chassis fix 4) prevents it.
- **Journal friction (performance, not strength).** With PETG on PETG at μ 0.3, the journal takes about 23 N·mm per side under the pretension alone. That is roughly the N20's rated torque, and 45 % of the everyday drive torque. Grease the journal (PTFE or silicone) and keep the pretension light.

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
| 1 | tooth root (chamfer top), stall pull 9.9 N on 1 tooth at RP (Kt 1.8) | XY | 7.94 | 25.0 | 3.15 | 3.0 | OK |
| 2 | tooth root, everyday pull 3.2 N (Kt 1.8) | XY | 2.55 | 25.0 | 9.79 | 4.0 | OK |
| 3 | tooth root shear, stall | XY shear | 0.78 | 12.5 | 15.93 | 3.0 | OK |
| 4 | D-flat bearing, stall 160 N*mm, 9.5 mm engaged (mean, loaded half) | XY | 20.21 | 25.0 | 1.24 | 3.0 | **FAIL** |
| 5 | D-flat bearing, everyday 51 N*mm | XY | 6.50 | 25.0 | 3.84 | 4.0 | **FAIL** |
| 6 | hub on the journal, stall (journal 30.8 N at its outer end) | XY | 1.03 | 25.0 | 24.35 | 3.0 | OK |
| 7 | hub on the journal, pretension sustained (journal 15.5 N at its outer end) | XY | 0.52 | 25.0 | 48.44 | 4.0 | OK |
| 8 | hub bending at the shaft end (axial = Z), stall R 19.9 N x 13.5 | Z | 2.76 | 12.5 | 4.52 | 3.0 | OK |
| 9 | hub bending at the shaft end (axial = Z), cyclic (rotating bending) R 13.2 N x 13.5 | Z | 1.83 | 12.5 | 6.82 | 4.0 | OK |
| 10 | hub bending at the shaft end (axial = Z), pretension sustained R 10.0 N x 13.5 | Z | 1.39 | 12.5 | 8.99 | 4.0 | OK |
| 11 | hub at the M2 set-screw hole (Z, Kt 2 net), stall R 19.9 N x 14.5 | Z | 7.38 | 12.5 | 1.69 | 3.0 | **FAIL** |
| 12 | hub at the M2 set-screw hole (Z, Kt 2 net), cyclic (rotating bending) R 13.2 N x 14.5 | Z | 4.89 | 12.5 | 2.56 | 4.0 | **FAIL** |
| 13 | hub at the M2 set-screw hole (Z, Kt 2 net), pretension sustained R 10.0 N x 14.5 | Z | 3.71 | 12.5 | 3.37 | 4.0 | **FAIL** |
| 14 | hub bending at the shaft end, 5 cm rear corner 31.8 N | Z | 4.42 | 12.5 | 2.83 | 3.0 | **FAIL** |
| 15 | hub at the set-screw hole, 5 cm rear corner | Z | 11.80 | 12.5 | 1.06 | 3.0 | **FAIL** |
| 16 | hub on the journal, 5 cm rear corner (journal 49 N) | XY | 1.64 | 25.0 | 15.22 | 3.0 | OK |
| 17 | disc rim bearing under a link, 5 cm rear corner | XY | 1.26 | 25.0 | 19.80 | 3.0 | OK |
| 18 | axial retention (set-screw friction 2 x mu N >= side 3 N) | friction N | 3.00 | 12.0 | 4.00 | 4.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, fixes, bought parts):
| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| spec §4 tooth case: 14.9 N on one tooth TIP (not reachable: the teeth share T_tight - T_slack = 9.9 N) | XY | 17.33 | 25.0 | 1.44 | 3.0 | no |
| tooth root, stall pull 9.9 N at the TIP (link riding over a tooth on a slack track) | XY | 11.51 | 25.0 | 2.17 | 3.0 | no |
| tooth root, fresh pack 100 % PWM 182 N*mm | XY | 9.03 | 25.0 | 2.77 | 3.0 | no |
| tooth root, stall, if the chamfer behaves like a sharp corner (Kt 2.0) | XY | 8.82 | 25.0 | 2.84 | 3.0 | no |
| D-flat bearing, fresh pack 100 % PWM 182 N*mm | XY | 22.99 | 25.0 | 1.09 | 3.0 | no |
| D-flat bearing, fresh pack at the 80 % PWM cap 146 N*mm | XY | 18.39 | 25.0 | 1.36 | 3.0 | no |
| D-flat bearing, stall, with the DFM hub-end counterbore (8.2 mm engaged) | XY | 23.41 | 25.0 | 1.07 | 3.0 | no |
| hub bending at the shaft end, 5 cm corner, stiff landing delta 2.5 (64 N) | Z | 8.85 | 12.5 | 1.41 | 3.0 | no |
| N20 shaft (D) at the gearbox face, lever model (journal + cradle), stall 19.9 N | steel σy 350 | 133.63 | 350.0 | 2.62 | 1.5 | OK |
| N20 shaft (D) at the gearbox face, bound: motor clamped, journal not reached, stall | steel σy 350 | 233.74 | 350.0 | 1.50 | 1.5 | no |
| N20 shaft (D) at the gearbox face, lever model (journal + cradle), 5 cm corner 31.8 N | steel σy 350 | 213.80 | 350.0 | 1.64 | 1.5 | OK |
| N20 shaft (D) at the gearbox face, bound: motor clamped, journal not reached, 5 cm corner | steel σy 350 | 373.97 | 350.0 | 0.94 | 1.5 | no |
| FIX metal N20 hub: M3 bolt bearing in the 7 mm disc (4 on r6), stall | XY | 0.32 | 25.0 | 78.75 | 3.0 | OK |
| FIX metal N20 hub: bolt bearing, 5 cm corner (radial shared by 4) | XY | 0.38 | 25.0 | 66.00 | 3.0 | OK |
| set screw turned onto the flat (DFM round-2 fix 2): hub at the hole (Kt 2 net), stall | Z | 7.37 | 12.5 | 1.70 | 3.0 | no |
| FIX HUB_D 10 -> 10.5 (journal follows), no set-screw hole: hub at the shaft end, 5 cm corner | Z | 3.81 | 12.5 | 3.28 | 3.0 | OK |
| FIX HUB_D 10 -> 11.0 (journal follows), no set-screw hole: hub at the shaft end, 5 cm corner | Z | 3.31 | 12.5 | 3.77 | 3.0 | OK |

- lowest SF 1.06 (required 3.0) at: hub at the set-screw hole, 5 cm rear corner
- drop rows scale with the height: all of them meet their SF up to a 1.8 cm drop (design 5 cm), limited by: hub at the set-screw hole, 5 cm rear corner
- 7 of 18 verdict rows below their required SF

## Required changes

1. **BOM: metal N20 hub.** No printed geometry can carry the torque, so the round-1 recommendation stands. Use a brass or aluminium hub with a 3 mm D bore and its own set screw on the flat.
   - Bolt the printed disc to it with 4 × M3 on r 6: bolt bearing SF 79 at stall and 66 at the 5 cm corner.
   - Its OD can run in the journal.
   - It must also clear the N20's Ø4 × 0.8 bearing boss. The current hub end overlaps that boss by 0.3 mm.
2. **No radial hole in any printed hub section.** Delete the M2 set-screw hole: SF 1.06 to 3.37 at all four load levels. The metal hub carries the set screw.
3. **Any printed tube between the metal hub and the disc must be Ø ≥ 10.5 with no hole: `HUB_D` 10 → 10.5.** It is shared in `rover_frame.py`, and the chassis journal follows it. Shaft-end section at the 5 cm corner: SF 2.83 → **3.28**. Ø11 gives 3.77.

Without the set-screw hole, the drop limit rises from 1.8 cm to 4.7 cm with Ø10, and to 5.5 cm with Ø10.5.

The DFM round-2 fixes don't change this verdict:
- The Ø4.7 × 1.3 hub-end counterbore clears the bushing but cuts the engagement to 8.2 mm: D-flat SF 1.07.
- Turning the set screw onto the flat leaves the hub at the hole at SF 1.70 at stall.

Both are moot once the metal hub carries the torque and the set screw. The metal hub must still clear the bushing.

## Proof test (after the changes; replaces spec §8)

1. **Torque.** Hold the track still and stall the motor for 3 s, 5 times, **at 100 % PWM on a freshly charged pack** (about 182 N·mm, 1.14 × design and the most the N20 gives; 80 % PWM gives only 146 N·mm). Pass:
   - no slip of the hub on the shaft or of the disc on the hub (pen marks);
   - no cracked or sheared tooth;
   - the hub still turns freely in the journal.
2. **Tooth.** Mount the sprocket on its hub on a spare N20, or on a 3 mm D shaft in a vise. Hang **2 kg (19.6 N, 2 × the 9.9 N stall pull)** for 1 min from one link seated on one horizontal tooth. Pass: no crack at the tooth root, no permanent set.

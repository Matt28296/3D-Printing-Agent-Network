VERDICT: FAIL

# Strength check: 20261026-rover-sprocket

strength-analyst · 2026-10-26 · `python3 jobs/20261026-rover-sprocket/strength_calc.py`

**Result: FAIL.** Lowest SF is **0.21**: the D-bore rocking on the shaft under the 30 cm corner-drop load. The sprocket fails even without any drop:
- **D-flat torque transfer at stall: SF 0.85.** It is 1.04 at the 6 V stall and 2.93 everyday, where 4 is required.
- **Bore rocking under the overhung track load: SF 1.85** at stall, 3.68 under pretension (4 required).
- **Tooth root at stall: SF 1.88** (sharp root, Kt 2.5).

## Part-specific load path and assumptions

- **Shaft and bore:** the N20 shaft is Ø3 with a flat 1.0 mm from the axis (flat half-width 1.12 mm) and is engaged 6.5 mm. The D-bore is 3.3 CAD and prints at about 3.1, a **0.1 mm slip fit, not the press fit the brief and spec claim**. All torque goes through the flat.
- **Flat torque model:** the shaft rotates rigidly against the bore flat. Pressure is zero at the centre of the flat and rises to its edge on one side, so T = p_max·L·b²/3. The table reports the mean over the loaded half (p_max/2), the analogue of bolt bearing. With the clearance, real contact is the corner line of the flat, at twice that pressure or more. The bore is vertical in print, so this bearing is in-plane.
- **Grub screw as the only torque path (advisory, SF 0.43):** an M2 set screw in a printed Ø1.6 radial hole would need about 200 N of axial force. Its threads cross the layers and would strip.
- **Overhung load:** the disc centre is 13.25 mm outboard of the middle of the shaft engagement. A radial load R there gives a bore edge bearing of R/(dL) + 6M/(dL²). The hub bending at the shaft end is axial stress, which is across the layers.
- **Teeth:** one tooth takes the whole stall pull (9.9 N) at the pitch radius, 4.29 mm from the 2.62 × 7 mm root, with Kt 2.5 at the unfilleted root. Loading the tip instead gives SF 1.35 (advisory). The everyday pull (2.9 N) passes at SF 6.5.
- **Drop:** the sprocket sits on the bottom run like a road wheel, so it takes a corner share of 171 N. The same load bends the N20 output shaft at the gearbox face (advisory, bought part): σ ≈ 1294 MPa at 30 cm and ≈ 345 MPa at 8 cm. **Nothing supports the shaft outboard; this is a motor risk at any drop height.**
- **Proof test:** the spec's proof test ("full PWM") on a fresh pack reaches about 182 N·mm, 1.14 × the design torque.

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
| 1 | tooth root bending, stall 9.9 N on 1 tooth at RP (Kt 2.5 sharp root) | XY | 13.30 | 25.0 | 1.88 | 3.0 | **FAIL** |
| 2 | tooth root bending, everyday pull 2.9 N (Kt 2.5) | XY | 3.84 | 25.0 | 6.51 | 4.0 | OK |
| 3 | tooth root shear, stall | XY shear | 0.81 | 12.5 | 15.43 | 3.0 | OK |
| 4 | D-flat bearing, stall 160 N*mm (mean, loaded half) | XY | 29.54 | 25.0 | 0.85 | 3.0 | **FAIL** |
| 5 | D-flat bearing, everyday 46 N*mm | XY | 8.54 | 25.0 | 2.93 | 4.0 | **FAIL** |
| 6 | bore rocking (overhung radial), stall R 19.9 N | XY | 13.49 | 25.0 | 1.85 | 3.0 | **FAIL** |
| 7 | bore rocking, cyclic R 12.9 N | XY | 8.72 | 25.0 | 2.87 | 4.0 | **FAIL** |
| 8 | bore rocking, pretension sustained R 10 N | XY | 6.79 | 25.0 | 3.68 | 4.0 | **FAIL** |
| 9 | hub bending at shaft end (axial = Z), stall | Z | 1.53 | 12.5 | 8.15 | 3.0 | OK |
| 10 | hub bending at shaft end, 30 cm corner 171 N | Z | 13.23 | 12.5 | 0.94 | 3.0 | **FAIL** |
| 11 | bore rocking, 30 cm corner | XY | 116.33 | 25.0 | 0.21 | 3.0 | **FAIL** |
| 12 | disc rim bearing under a link, 30 cm corner | XY | 6.80 | 25.0 | 3.67 | 3.0 | OK |
| 13 | axial retention (grub friction 2 x mu N >= side 3 N) | friction N | 3.00 | 12.0 | 4.00 | 4.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, bought parts):
| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| tooth root, stall, load at the tip | XY | 18.59 | 25.0 | 1.35 | 3.0 | no |
| tooth root, fresh pack 100 % PWM 182 N*mm | XY | 15.12 | 25.0 | 1.65 | 3.0 | no |
| D-flat bearing, fresh pack 100 % PWM 182 N*mm | XY | 33.60 | 25.0 | 0.74 | 3.0 | no |
| D-flat bearing, 6 V stall 130 N*mm | XY | 24.00 | 25.0 | 1.04 | 3.0 | no |
| grub alone carries stall: thread strip (radial hole, Z shear), 200 N | Z shear | 14.63 | 6.2 | 0.43 | 3.0 | no |
| hub bending, 30 cm flat 86 N | Z | 6.61 | 12.5 | 1.89 | 3.0 | no |
| hub bending, 8 cm corner 46 N | Z | 3.53 | 12.5 | 3.54 | 3.0 | OK |
| N20 shaft Ø3.0 bending at gearbox face, stall 20 N x 20 | steel σy 450 | 150.06 | 450.0 | 3.00 | 1.5 | OK |
| N20 shaft Ø3.0 bending at gearbox face, 30 cm corner 171 N x 20 | steel σy 450 | 1293.67 | 450.0 | 0.35 | 1.5 | no |
| N20 shaft Ø3.0 bending at gearbox face, 8 cm corner 46 N x 20 | steel σy 450 | 344.98 | 450.0 | 1.30 | 1.5 | no |
| FIX tooth root with r0.8 root fillets (Kt 1.5), stall | XY | 7.98 | 25.0 | 3.13 | 3.0 | OK |
| FIX coupler: M3 bolt bearing in the disc (4 on r6), stall | XY | 0.32 | 25.0 | 78.75 | 3.0 | OK |
| FIX coupler: bolt bearing, 30 cm corner (radial shared by 4) | XY | 2.04 | 25.0 | 12.25 | 3.0 | OK |

**lowest SF 0.21 (required 3.0) at: bore rocking, 30 cm corner**

## Verdict and changes

FAIL. The smallest change that passes every stall, cyclic and sustained case has two parts:

1. **BOM + geometry: drop the printed D-bore.** Fit a metal N20 flange coupler (3 mm D bore with its own M3 set screw, flange of about Ø16) and bolt the disc to it with 4 × M3 on a Ø12 circle. The printed hub then goes, or becomes just a spacer. Bolt bearing in the 7 mm disc: SF 79 at stall and 12 at the 30 cm corner drop. The coupler also takes the overhung-moment rocking (SF 0.21 → metal). Check that the coupler fits within the 6.5 mm of shaft that is available.
2. **Geometry: r ≥ 0.7 mm fillets at the tooth roots** (r ≥ 0.25 × the 2.62 mm root, so Kt 1.5). Tooth root at stall: SF 1.88 → **3.13**. The fillet sits at the disc rim (r 11.9), below the link knuckles (r ≥ 13.2), so it does not affect the assembly check.

The N20 shaft overhang (20 mm from the gearbox face) is not fixed by either change. See the chassis report: raise the sprocket off the ground run, or limit the drop height.

## Proof test (after the changes; replaces the spec §8 test)

1. **Torque:** hold the track still and stall the motor for 3 s, 5 times, on a **fresh pack at 100 % PWM** (≈ 182 N·mm, 1.14 × design; the motor cannot go higher). Pass: no slip on the shaft (pen mark across shaft and hub), no tooth cracks.
2. **Tooth (static, 2 × stall):** mount the sprocket on its coupler on a spare Ø3 D-shaft (or a spare N20) clamped in a vise. Hang 2 kg (19.6 N) for 1 min from one link seated on one horizontal tooth, so the load is at the pitch radius. Pass: no crack at the tooth root, no permanent set.

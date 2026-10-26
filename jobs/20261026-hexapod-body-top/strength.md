VERDICT: NEEDS_TEST

# Strength check: 20261026-hexapod-body-top

strength-analyst · 2026-10-26 · `python3 jobs/20261026-hexapod-body-top/strength_calc.py`

**NEEDS_TEST** (placeholder allowables only). No geometry change is needed.

- **Lowest SF: 3.27**, at the root of the ESP32 seat's side rail. A jumper pulled sideways at 10 N pushes the board
  edge against one rail, bending its root across the layers. This matches the rover lid, which uses the same seat.
- **Next lowest: 4.77**, at the PCA9685 post root when a servo lead is pulled sideways.
- **Lifting the robot by one end of the deck: SF 5.01.** The section through the cable slots at x 46 carries the
  whole 579 g below the deck, at × 2.
- **Every other row: SF 6 or more.**

## Print orientation and critical sections

**Orientation.** The deck prints flat. Deck bending, header bearing on the window and tie-slot shear all run along the
layers (XY). The seat rails and PCA9685 posts stand up from the deck, so their root bending runs across the layers
(Z). Screw-head push-through shears the layers (Z shear).

**Sections checked:**
- Handling, robot lifted by both long edges: the deck at the column line, through the cable slots.
- Handling, robot lifted by one end: the deck through the cable slots at x 46.
- Deck-screw heads: plug shear and bearing.
- USB plug, 10 N: header strips bearing on the window end.
- Jumper pulled sideways, 10 N: the side rail, loaded over half the board length.
- Jumpers pushed on from below: the zip-tie slot ligament.
- PCA9685: post root under a 10 N sideways lead pull, and M2.5 screw pull-out when unplugging.
- Drop on 6 feet at 17.2 g: deck bending between the columns, through the ESP32 window.

## Load cases (re-derived; the same block runs at the top of all five hexapod `strength_calc.py`)

Inputs: `hex_frame.py`, `tools/hobby_parts.py`, the five `model.py` files (top-level constants read with `ast`) and the
five `geometry.json` volumes. The leg frames are rebuilt as in `leg_frames()` of `assembly_check.py`; the feet match
`assembly_check.json` to 0.1 mm. In the neutral stance the foot is 77.0 mm out from the coxa axis, **15.8 mm to the
side of it** (the tibia's mid-plane sits two link thicknesses in front of the coxa line), and 87.0 mm below the coxa
bracket's back face. The body underside is 96.4 mm up.

| Load | Spec §4 | Re-derived here | Duration, SF |
|---|---|---|---|
| Robot mass | ≈ 0.6 kg | **683 g (6.70 N)**. Printed parts at solid volume × 1.27 g/cm³, **infill factor 1.0** (an upper bound: with 3–4 perimeters and 5 top/bottom layers on 3–7 mm plates the slicer will report ≈ 75–90 %): bottom 95.8, top 46.6, coxa 6 × 10.3, femur 6 × 7.7, tibia 6 × 8.9 = 304 g. Bought: 18 × MG90S 241, LiPo 65, 2 × PCA9685 18, ESP32 10, UBEC 15, wiring, screws and buck 30 | — |
| Foot load on a tripod | 6 N / 3 = 2 N | CG at the body centre, shares from the real foot positions. The middle leg of a tripod carries 41.5 % in the stance and up to **43.3 %** over the coded ±15° coxa sweep (47.5 % at MAX_COXA 30°): **2.90 N** | sustained (robot stopped on a tripod, or one foot 2 mm high): SF 4 |
| Walking | 4 N (2 N × 2) | 2 × 2.90 = **5.80 N** up | cyclic: SF 4 |
| Foot scrub (missed by the spec) | — | `hexapod_test.ino` sweeps the stance coxae ±15° with femur and tibia fixed. The front and rear feet cannot follow those arcs while the body moves straight, so they slide every step. Friction μ 0.5 × 2.90 N in the worst horizontal direction, limited by each servo's stall | cyclic: SF 4 |
| Servo stalls | 216 N·mm per joint | Each stall applied at the foot (femur ±4.8 N vertical = 216/45; coxa 2.8 N tangential = 216/77; knee 3.1 N radial = 216/70; with 2.90 N up), and each stall torque straight into its horn pocket and tab screws | short-term: SF 3 |
| Sideways shove | 3 N at a foot | 3 N in any horizontal direction, with 0–2.90 N up | short-term: SF 3 |
| 20 cm drop | "3 × weight over 6 feet, ≈ 3 N per foot" | E = m·g·h = **1.34 J**. Stated stopping distance if the legs held: **δ = 10 mm** (servo backlash and position band ≈ 4 mm at the foot, horn/link/floor flex ≈ 3 mm, carpet ≈ 3 mm). A linear stop gives 281 N peak: **47 N per foot landing flat on 6 feet, 94 N on 3**. A leg cannot push that hard. Its femur and knee servos back-drive at T_bd ≈ 2 × stall = 432 N·mm (assumed: gear losses act in both directions). That caps the vertical foot force at 2·T_bd/L_F = **19.2 N**, with ≤ 6.2 N of inward friction, which a splaying landing supplies. Both landings therefore load each foot to 19.2 N plus up to 6.2 N radial. The rest of the energy goes into back-driving the servos over 12 mm of body travel (6 feet) or 26 mm (3 feet), inside the 49 mm ground clearance. The spec's 3 N per foot implies a 100–400 mm stop, so it is not used | short-term: SF 3 |
| Drop inertia of the body | — | Support load factor at the cap: 6 × 19.2 / 6.70 = **17.2 g** on 6 feet, 8.6 g on 3 | short-term: SF 3 |
| Handling | top plate only | Robot lifted by the top plate, × 2. Robot lifted by one leg: that leg's femur servo back-drives at the same 19.2 N, so the drop envelope covers it | short-term: SF 3 |
| Assembly (missed by the spec) | — | M2 horn clamp screw **snug, 0.05 N·m ≈ 125 N** preload (verdict rows; F = T / (0.2 d)). BUILD_GUIDE's "firmly", taken as 0.1 N·m ≈ 250 N, is advisory | short-term: SF 3 |
| Temperature | 40 °C | PETG softens at ≈ 70 °C: 30 °C margin, OK | — |

**How the drop result depends on the back-drive assumption.** At 1.5 × stall the cap is 14.4 N per foot; at 1 × stall
it is 9.6 N. At 1 × stall a 3-foot landing runs out of travel: the body reaches the floor after 49 mm with ≈ 0.25 J
left. The lowest points are the coxa brackets' vertical plates, which then take the rest of the impact edge-on. The
proof drop test settles which case applies.

## Assumptions

- **Envelope search.** Every case searches its whole foot-force envelope: the vertical load, the size and direction of
  the friction, and every servo torque within its cap. Each section takes its own worst point. A leg's internal loads
  depend only on the foot force expressed in the coxa frame, so one leg covers all six.
- **Section properties.** They come from the `model.py` parameters. They were cross-checked against sections cut from
  the CAD (trimesh) and agree within 1 %.
- **Clamped horn joints.** These follow the arm review, with one change.
  - Capacity is washer pull-through (π·D_w·t_floor) plus the anti-rotation arm screw (Ø1.2 drilled, 3 mm engaged at
    r 13; assumed), taken against the interlayer shear allowable.
  - The pivot is the horn hub's edge (r 3.6), not the arm tip. The 1.6 mm arm of a micro horn cannot carry the pivot
    force.
  - When the far side of the hub lifts, the arm screw is on the pressed side and adds nothing.
  - The M2 thread in the metal spline, and the horn itself, are bought parts. They are left to the proof test.
- **Tab screws.**
  - Pull-out is τ = F / (π · 1.5 · L), using the printed Ø1.5 pilot and the engaged length: an M2×8 through the 2.5 mm
    tab, limited by the plate thickness.
  - Rocking about the screw line pivots on the tab edge, 6 mm from the screws. Rocking along the servo uses the 27.8 mm
    screw spacing.
  - Servo bodies bearing on the window walls get no credit. A 0.2 mm clearance does not close before the screws carry
    the load.
- **Stress concentration factors (Kt):**
  - 2.5 at sharp internal or window corners;
  - 2.0 at holes in PETG and at the 45° gusset tip;
  - 1.5 at rounded pocket edges and 45° ramps;
  - 1.6 at the r2.5 hub–arm fillet.

## Allowables and sources

`library/materials.csv` has no rows and `inputs/` has no printed-specimen datasheet, so these are the strength-checks
**placeholders** for PETG. **NEEDS_TEST is the best verdict possible.**

| Quantity | Value | Source |
|---|---|---|
| Tension or bending along the layers (XY) | 25 MPa | skill placeholder, PETG |
| Tension or bending across the layers (Z) | 12.5 MPa | 0.5 × in-plane (placeholder) |
| Shear: in-plane / interlayer (pull-out, washer pull-through, tear-out in standing walls) | 12.5 / 6.25 MPa | 0.5 × normal (Tresca), as in the arm and rover reviews |
| Bearing (compression on a layer face or a wall) | 25 MPa | in-plane value: compression does not separate the layers |
| E | 1.8 GPa | skill placeholder |

Required SF: 3 for short-term loads, 4 for cyclic or sustained loads. Service temperature 40 °C against ≈ 70 °C
softening: OK.

## Results (copied from `python3 strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | handling: lifted by the long edges (11.4 N): deck at the column line y 25 (cable slots, Kt 2.5) | XY | 2.39 | 25.00 | 10.45 | 3 | OK |
| 2 | handling: lifted by one end (11.4 N): deck through the cable slots x 46 (Kt 2.5) | XY | 4.99 | 25.00 | 5.01 | 3 | OK |
| 3 | handling: screw-head plug shear through the 3 mm deck (2 screws carry it) | Z shear | 0.11 | 6.25 | 57.06 | 3 | OK |
| 4 | handling: screw-head bearing on the deck (2 screws) | XY | 0.42 | 25.00 | 59.80 | 3 | OK |
| 5 | USB plug 10 N along x: header strips on the window end face (2 x 2.5 x 2.5) | XY | 0.80 | 25.00 | 31.25 | 3 | OK |
| 6 | jumper pulled sideways 10 N: side rail root over half the board (25.8 mm, Kt 2.5) | Z | 3.82 | 12.50 | 3.27 | 3 | OK |
| 7 | jumpers pushed on from below: zip-tie slot ligament (20 N) | XY shear | 0.83 | 12.50 | 15.00 | 3 | OK |
| 8 | servo lead pulled sideways 10 N: PCA9685 post root (Ø5.5/Ø2.4, 4 posts, Kt 2.5) | Z | 2.62 | 12.50 | 4.77 | 3 | OK |
| 9 | PCA9685 unplugging 15 N at one end: M2.5 pull-out (2 screws, Ø2.2 pilot, 4.4 mm) | Z shear | 0.25 | 6.25 | 25.34 | 3 | OK |
| 10 | sustained: deck group at 1 g: deck between the columns through the ESP32 window (span 80, b 71, Kt 2.5) | XY | 0.24 | 25.00 | 103.40 | 4 | OK |
| 11 | drop on 6 feet: deck group at 17.2 g: deck between the columns through the ESP32 window (span 80, b 71, Kt 2.5) | XY | 4.16 | 25.00 | 6.02 | 3 | OK |
| 12 | drop: screw-head bearing, deck group at 17.2 g over 4 screws | XY | 0.32 | 25.00 | 77.04 | 3 | OK |

**lowest SF 3.27 (required 3) at: jumper pulled sideways 10 N: side rail root over half the board (25.8 mm, Kt 2.5)**

## Servo torques

**The femur servos do not have enough margin** (details and fixes in the femur report):

- Standing evenly on all six feet, each femur servo holds 50 N·mm (23 % of stall).
- Stopped on a tripod, it holds 125–143 N·mm (58–66 %) continuously.
- Walking pushes it past stall: × 2 dynamics give 121 %, and outward foot scrub gives 107 %.

The cheapest fix is in software: turn the tibia 18.7° inward so the foot sits midway between the femur axis and the
knee. That splits the moment, 30 % on the femur and 30 % on the knee.

## Proof test (spec §8, extended to the two lowest rows)

1. **Lift by both long edges.** Lift the assembled robot by the top plate 5 times, holding both long edges.
2. **Lift by one end.** Then lift it once by one end of the deck only, so the robot hangs from that edge.
3. **USB.** Plug and unplug USB 5 times.
4. **Side push on the ESP32.** Push the seated ESP32 sideways with **2 kg (≈ 20 N, 2 × the jumper-pull case)** at
   mid-length, for 10 s each way.

Pass:
- no cracks or whitening at the screw holes, the cable-slot corners, the PCA9685 post roots, or the seat rails and
  ledges;
- the board stays on both ledges.

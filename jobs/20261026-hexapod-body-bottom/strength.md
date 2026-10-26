VERDICT: FAIL

# Strength check: 20261026-hexapod-body-bottom

strength-analyst · 2026-10-26 · `python3 jobs/20261026-hexapod-body-bottom/strength_calc.py`

**FAIL. 3 of 23 rows fail, all at the six coxa-servo mounts. The lowest SF is 1.71.**

- **Plate strip outside each coxa window's outer end** (7.45 mm deep × 4 mm, between the window and the outline
  edge). The coxa servo's outer tab pushes this strip up while the inner tab screw pulls the plate down. That is the
  whole leg moment, 82 mm × F_up, over a 27.8 mm tab spacing. **Walking: SF 3.84 (needs 4). Drop: SF 1.71.**
- **Coxa-servo tab screws** (M2×8 self-tapping, 4 mm engaged): pull-out **SF 1.94** in the drop. The tangential foot
  offset of 15.8 mm also rocks the servo about its screw line.

Everything else passes with room to spare:
- plate mid-span through the LiPo strap slots: SF ≥ 4.6;
- columns: handling SF 3.69, drop SF 6.95;
- column screws: SF 45;
- pilots and ligaments: SF ≥ 19.

## Print orientation and critical sections

- **Orientation.** Printed flat with the tab face on the bed. Plate bending, pilot bearing and ligament tear-out
  around the vertical tab pilots run along the layers (XY). Tab-screw pull-out shears the layers (Z shear).
- **Columns.** Ø8 × 40, standing, with r1.5 root fillets (Kt 1.5). Bending and tension at the root act across the
  layers (Z).
- **Sections checked:**
  - for each coxa mount: tab-screw pull-out, pilot bearing (stall and drop), the 1.60 mm pilot-to-window ligament, and
    the plate strip outside the window, modelled as fixed-fixed over the window width plus one plate thickness each
    side (the plate carries on beside the window at every mount); a rigid-inclusion model (rover precedent) is
    advisory;
  - plate mid-span, on the hull chord through a strap slot (133 mm net, Kt 2.5): tripod span when walking and in a
    3-foot landing, left–right span in a 6-foot landing;
  - columns: handling with the robot lifted by the deck and tipped 90°, tension, drop inertia of the deck group
    (105 g at 17.2 g, landing tilted 20°), buckling;
  - pull-out of the M3 deck screws from the columns.

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
| 1 | sustained 2.90 N: coxa-servo tab screw pull-out (M2x8, 4 mm in the plate) | Z shear | 0.66 | 6.25 | 9.49 | 4 | OK |
| 2 | walking 5.80 N: coxa-servo tab screw pull-out (M2x8, 4 mm in the plate) | Z shear | 1.32 | 6.25 | 4.74 | 4 | OK |
| 3 | scrub: coxa-servo tab screw pull-out (M2x8, 4 mm in the plate) | Z shear | 1.33 | 6.25 | 4.70 | 4 | OK |
| 4 | shove 3 N: coxa-servo tab screw pull-out (M2x8, 4 mm in the plate) | Z shear | 2.05 | 6.25 | 3.05 | 3 | OK |
| 5 | stalls: coxa-servo tab screw pull-out (M2x8, 4 mm in the plate) | Z shear | 1.85 | 6.25 | 3.37 | 3 | OK |
| 6 | drop 19.2 N: coxa-servo tab screw pull-out (M2x8, 4 mm in the plate) | Z shear | 3.22 | 6.25 | 1.94 | 3 | **FAIL** |
| 7 | coxa stall 216 N·mm: tab pilot bearing | XY | 1.29 | 25.00 | 19.31 | 3 | OK |
| 8 | drop: tab pilot bearing | XY | 0.78 | 25.00 | 32.11 | 3 | OK |
| 9 | drop: pilot-to-window ligament 1.60 tear-out, whole radial force on one screw | XY shear | 0.48 | 12.50 | 25.93 | 3 | OK |
| 10 | walking x2, tripod: plate mid-span, 217 g at the centre, section through a strap slot (b 133, Kt 2.5) | XY | 0.70 | 25.00 | 35.76 | 4 | OK |
| 11 | drop on 3 feet (8.6 g), tripod span: plate mid-span, 217 g at the centre, section through a strap slot (b 133, Kt 2.5) | XY | 3.00 | 25.00 | 8.32 | 3 | OK |
| 12 | drop on 6 feet (17.2 g), left-right rows: plate mid-span, 217 g at the centre, section through a strap slot (b 133, Kt 2.5) | XY | 5.43 | 25.00 | 4.60 | 3 | OK |
| 13 | sustained 2.90 N: plate strip outside the coxa window (7.45 deep x 4.0, span 20.6, Kt 2.5) | XY | 3.25 | 25.00 | 7.68 | 4 | OK |
| 14 | walking 5.80 N: plate strip outside the coxa window (7.45 deep x 4.0, span 20.6, Kt 2.5) | XY | 6.51 | 25.00 | 3.84 | 4 | **FAIL** |
| 15 | scrub: plate strip outside the coxa window (7.45 deep x 4.0, span 20.6, Kt 2.5) | XY | 4.61 | 25.00 | 5.42 | 4 | OK |
| 16 | shove 3 N: plate strip outside the coxa window (7.45 deep x 4.0, span 20.6, Kt 2.5) | XY | 6.63 | 25.00 | 3.77 | 3 | OK |
| 17 | drop 19.2 N: plate strip outside the coxa window (7.45 deep x 4.0, span 20.6, Kt 2.5) | XY | 14.61 | 25.00 | 1.71 | 3 | **FAIL** |
| 18 | handling: lifted by the deck, tipped 90°: column root bending (2.84 N at 40 mm, Kt 1.5) | Z | 3.39 | 12.50 | 3.69 | 3 | OK |
| 19 | handling: lifted by the deck: column tension (2.84 N, Kt 1.5) | Z | 0.08 | 12.50 | 147.56 | 3 | OK |
| 20 | drop on 6 feet, landing tilted 20°: column root bending (deck 105 g at 17.2 g, Kt 1.5) | Z | 1.80 | 12.50 | 6.95 | 3 | OK |
| 21 | drop: column buckling, K 2: P_cr 558 N vs 4.4 N | XY | 0.20 | 25.00 | 126.65 | 3 | OK |
| 22 | handling: M3x8 self-tapping pull-out from a column (2 screws carry it, Ø2.6 pilot, 5 mm) | Z shear | 0.14 | 6.25 | 44.96 | 3 | OK |
| 23 | sustained: column under the deck group (compression) | XY | 0.01 | 25.00 | 4900.90 | 4 | OK |

**lowest SF 1.71 (required 3) at: drop 19.2 N: plate strip outside the coxa window (7.45 deep x 4.0, span 20.6, Kt 2.5)**

Advisory (not in the verdict):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| walking 5.80 N: plate round a coxa window, rigid-inclusion model (r 16.1, Kt 2.5) | XY | 4.51 | 25.00 | 5.54 | 4 |
| drop 19.2 N: plate round a coxa window, rigid-inclusion model (r 16.1, Kt 2.5) | XY | 9.56 | 25.00 | 2.61 | 3 |

## Required changes (the script checks them as one set; all rows pass)

1. **Plate thickness.** T_BODY 4 → **6 mm** (`hex_frame.py`). Results:
   - strip outside each coxa window: walking 3.84 → **7.24**, drop 1.71 → **3.23**;
   - plate mid-span: drop 4.60 → 10.4.

   Knock-on effects:
   - The columns start on the new top face, so the deck rises 2 mm. The LiPo rises 2 mm with it, so the gap for the
     ESP32 leads does not change.
   - Re-run `assembly_check.py`.

   An alternative is MARGIN 4 → 10, which deepens the strip to 13.45 mm (drop ≈ 3.1). It grows the plate to about
   167 × 143 mm and moves its edge closer to the raised femurs, so the assembly sweep would need re-checking.
2. **Coxa-servo tab screws.** Use **M2×12 machine screws through the 2.0 mm tab holes, with an M2 washer and nut on
   the plate top**, in Ø2.4 CAD clearance holes instead of the Ø1.7 self-tapping pilots. Drop results: pull-out 1.94
   becomes nut bearing **3.84**, and plug shear through the 6 mm plate becomes **7.76**.

   Self-tapping screws cannot reach SF 3 here: an M2×8 in a 6 mm plate (5.5 mm engaged) only gets to 2.67. The nuts
   are reachable from above before the LiPo and the top plate go on.

Required-change set as computed by the script (advisory rows):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| FIX T_BODY 6: walking 5.80 N: plate strip outside the coxa window | XY | 3.46 | 25.00 | 7.24 | 4 |
| FIX T_BODY 6: drop 19.2 N: plate strip outside the coxa window | XY | 7.75 | 25.00 | 3.23 | 3 |
| FIX T_BODY 6: drop on 6 feet (17.2 g): plate mid-span through a strap slot | XY | 2.41 | 25.00 | 10.36 | 3 |
| FIX through-bolt + nut: walking 5.80 N: nut bearing on the plate top (M2 nut 4 AF) | XY | 2.66 | 25.00 | 9.40 | 4 |
| FIX through-bolt + nut: walking 5.80 N: nut plug shear through T_BODY 6 | Z shear | 0.33 | 6.25 | 18.98 | 4 |
| FIX through-bolt + nut: shove 3 N: nut bearing on the plate top (M2 nut 4 AF) | XY | 4.14 | 25.00 | 6.04 | 3 |
| FIX through-bolt + nut: shove 3 N: nut plug shear through T_BODY 6 | Z shear | 0.51 | 6.25 | 12.20 | 3 |
| FIX through-bolt + nut: drop 19.2 N: nut bearing on the plate top (M2 nut 4 AF) | XY | 6.51 | 25.00 | 3.84 | 3 |
| FIX through-bolt + nut: drop 19.2 N: nut plug shear through T_BODY 6 | Z shear | 0.81 | 6.25 | 7.76 | 3 |

## Servo torques

**The femur servos do not have enough margin** (details and fixes in the femur report):

- Standing evenly on all six feet, each femur servo holds 50 N·mm (23 % of stall).
- Stopped on a tripod, it holds 125–143 N·mm (58–66 %) continuously.
- Walking pushes it past stall: × 2 dynamics give 121 %, and outward foot scrub gives 107 %.

The cheapest fix is in software: turn the tibia 18.7° inward so the foot sits midway between the femur axis and the
knee. That splits the moment, 30 % on the femur and 30 % on the knee.

## Proof test (for the revised plate; adjusts spec §8)

1. **Standing load.** Stand the assembled robot on **all six feet** (servos powered, neutral stance). Add **500 g** on
   the top plate for 1 min. Each femur then holds ≈ 87 N·mm.

   Do not do this on a tripod: the femur servos would stall.
2. **Drop test.**
   - Drop it from **20 cm** onto a carpeted floor 3 times, landing flat on 6 feet.
   - Then drop it 3 more times, tilted so it lands on one side's 3 feet.

Pass:
- no cracks or whitening at the coxa windows, especially at the strip outside each window's outer end;
- no cracks at the nut seats or the column roots;
- no servo tab lifting off the plate (0.2 mm feeler gauge);
- the nuts are still tight.

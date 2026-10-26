VERDICT: NEEDS_TEST

# Strength check: 20261026-hexapod-tibia (×6)

strength-analyst · 2026-10-26 · `python3 jobs/20261026-hexapod-tibia/strength_calc.py`

**NEEDS_TEST** (placeholder allowables only).

- **Lowest SF 4.59:** washer bearing on the 5 mm horn floor at a snug clamp preload (assembly case).
- **Lowest service-load SF 7.05:** the 3 N shove at the plate over the horn pocket (x 13, the arm-screw hole).
- **No geometry change is needed.**

The tibia is lightly loaded. In the neutral stance the foot force runs along it in compression and through the knee
axis. Bending comes only from foot friction (which the knee servo limits to its torque) and from sideways forces.

Conditions:
1. **Clamp screw torque.** Drive the M2×12 clamp screw **snug (≈ 0.05 N·m)**. At 0.1 N·m the washer pull-through on
   the 5 mm floor drops to SF 2.36.
2. **Foot tip on hard floors (advisory).** On a hard floor the Ø9 foot tip sees a line-contact pressure of ≈ 12 MPa
   walking and ≈ 22 MPa in the drop. That flattens the tip locally but does not break it. The optional TPU sock spreads
   the load.

## Print orientation and critical sections

- **Orientation.** The tibia is printed flat with the horn pocket on the bed, so bending in both directions and the
  axial load run along the layers (XY).
- **Sections checked:**
  - the horn clamp (5 mm floor) and the horn-pocket bearing at the knee stall;
  - x 4 over the horn hub (Kt 1.5);
  - x 13 over the pocket at the arm-screw hole (Kt 2), which governs;
  - x 16.5 (full section), x 35 and x 55;
  - buckling as a fixed-free column (K = 2) on the foot-end second moment, I = 257 mm⁴;
  - the clamp preload;
  - foot-tip contact (advisory).

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
| 1 | knee stall 216 N·mm: horn-arm bearing on the pocket wall | XY | 1.59 | 25.00 | 15.74 | 3 | OK |
| 2 | sustained 2.90 N: knee horn clamp (Ø6 washer, 5 mm floor + arm screw) | Z shear | 0.01 | 6.25 | 756.88 | 4 | OK |
| 3 | walking 5.80 N: knee horn clamp (Ø6 washer, 5 mm floor + arm screw) | Z shear | 0.02 | 6.25 | 378.44 | 4 | OK |
| 4 | scrub: knee horn clamp (Ø6 washer, 5 mm floor + arm screw) | Z shear | 0.29 | 6.25 | 21.82 | 4 | OK |
| 5 | shove 3 N: knee horn clamp (Ø6 washer, 5 mm floor + arm screw) | Z shear | 0.62 | 6.25 | 10.10 | 3 | OK |
| 6 | stalls: knee horn clamp (Ø6 washer, 5 mm floor + arm screw) | Z shear | 0.57 | 6.25 | 11.04 | 3 | OK |
| 7 | drop 19.2 N: knee horn clamp (Ø6 washer, 5 mm floor + arm screw) | Z shear | 0.08 | 6.25 | 79.11 | 3 | OK |
| 8 | sustained 2.90 N: tibia bending + axial, worst section (x 13 over the pocket, arm-screw hole (Kt 2)) | XY | 0.07 | 25.00 | 357.11 | 4 | OK |
| 9 | walking 5.80 N: tibia bending + axial, worst section (x 13 over the pocket, arm-screw hole (Kt 2)) | XY | 0.14 | 25.00 | 178.55 | 4 | OK |
| 10 | scrub: tibia bending + axial, worst section (x 13 over the pocket, arm-screw hole (Kt 2)) | XY | 1.75 | 25.00 | 14.28 | 4 | OK |
| 11 | shove 3 N: tibia bending + axial, worst section (x 13 over the pocket, arm-screw hole (Kt 2)) | XY | 3.54 | 25.00 | 7.05 | 3 | OK |
| 12 | stalls: tibia bending + axial, worst section (x 13 over the pocket, arm-screw hole (Kt 2)) | XY | 3.14 | 25.00 | 7.95 | 3 | OK |
| 13 | drop 19.2 N: tibia bending + axial, worst section (x 13 over the pocket, arm-screw hole (Kt 2)) | XY | 2.78 | 25.00 | 9.00 | 3 | OK |
| 14 | walking 5.80 N: buckling, fixed-free (K 2) on the foot-end I 257 mm⁴: P_cr 233 N vs 5.8 N | XY | 0.62 | 25.00 | 40.18 | 4 | OK |
| 15 | drop 19.2 N: buckling, fixed-free (K 2) on the foot-end I 257 mm⁴: P_cr 233 N vs 19.2 N | XY | 2.06 | 25.00 | 12.14 | 3 | OK |
| 16 | assembly: clamp screw snug 0.05 N·m (125 N): washer pull-through, 5.0 mm tibia floor | Z shear | 1.33 | 6.25 | 4.71 | 3 | OK |
| 17 | assembly: clamp screw snug (125 N): washer bearing on the floor | XY | 5.44 | 25.00 | 4.59 | 3 | OK |

**lowest SF 4.59 (required 3) at: assembly: clamp screw snug (125 N): washer bearing on the floor**

Advisory (not in the verdict):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| assembly: clamp screw 'firmly' 0.1 N·m (250 N): washer pull-through, 5.0 mm tibia floor | Z shear | 2.65 | 6.25 | 2.36 | 3 |
| walking 5.80 N: foot-tip contact pressure on a hard floor (Hertz, R4.5 x 6.2) | XY | 11.91 | 25.00 | 2.10 | 4 |
| drop 19.2 N: foot-tip contact pressure on a hard floor (Hertz, R4.5 x 6.2) | XY | 21.67 | 25.00 | 1.15 | 3 |

## Servo torques (static, N·mm; MG90S stall 216 N·mm at 6 V)

| pose / load | coxa | femur | knee | femur / stall |
|---|---|---|---|---|
| neutral stance, 6 feet (1.12 N) | 0 | 50 | 0 | 23% |
| neutral stance, tripod (2.78 N) | 0 | 125 | 0 | 58% |
| walking pose, gait ±15° (2.90 N) | 0 | 131 | 0 | 60% |
| walking pose, MAX_COXA ±30° (3.18 N) | 0 | 143 | 0 | 66% |
| walking pose + foot scrub mu 0.5 outward (2.90 N) | 23 | 232 | 102 | 107% |
| walking pose x2 dynamics (5.80 N) | 0 | 261 | 0 | 121% |
| tibia 18.7° inward, foot midway (2.90 N) | 0 | 65 | 65 | 30% |

**The femur servos do not have enough margin** (details and fixes in the femur report):

- Standing evenly on all six feet, each femur servo holds 50 N·mm (23 % of stall).
- Stopped on a tripod, it holds 125–143 N·mm (58–66 %) continuously.
- Walking pushes it past stall: × 2 dynamics give 121 %, and outward foot scrub gives 107 %.

The cheapest fix is in software: turn the tibia 18.7° inward so the foot sits midway between the femur axis and the
knee. That splits the moment, 30 % on the femur and 30 % on the knee.

## Proof test (spec §8 confirmed, with set-up details)

The spec's 1 kg at the foot tip gives ≈ 690 N·mm at the hub, about 1.6 × the most the knee servo can put through the
tibia. That is a good proof load.

1. **Set-up.**
   - Fit the tibia on its horn on an MG90S clamped in a vice, with the M2×12 clamp screw **snug (0.05 N·m)**.
   - Hold the tibia horizontal, with a stop on the far side of the hub so the servo gears do not carry the moment.
2. **Load.** Hang **1 kg** from the foot tip for **1 min**.
3. **Shove.** Push **3 N** sideways at the tip, each way, for 10 s.

Pass:
- no cracks or whitening around the pocket or the arm-screw hole;
- no gap over 0.2 mm (feeler gauge) between the tibia and the horn;
- after unloading, the tip returns to within 0.5 mm of where it started.

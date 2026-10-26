VERDICT: NEEDS_TEST

# Strength check: 20261026-hexapod-femur (×6)

strength-analyst · 2026-10-26 · `python3 jobs/20261026-hexapod-femur/strength_calc.py`

**NEEDS_TEST** (placeholder allowables only).

- **Lowest SF 4.59:** washer bearing on the 5 mm horn floor at a snug clamp preload (assembly case).
- **Lowest service-load SF 4.84:** plate torsion in the servo-capped drop. The torsion arises because the tibia's
  mid-plane sits 16.4 mm in front of the femur's.
- Every service-load row is at SF 4.84 or more, and the clamp pull-through at the snug preload is 4.71. **No geometry change is needed.**

Two conditions:
1. **Clamp screw torque.** Drive the M2×12 clamp screw **snug (≈ 0.05 N·m)**, not "firmly" as BUILD_GUIDE §3 says.
   At 0.1 N·m the washer pull-through on the 5 mm floor drops to SF 2.36.
2. **Femur servo margin.** The femur *servos* do not have enough torque margin (see "Servo torques" below). This is a
   system problem; the femur plate itself is fine.

## Print orientation and critical sections

- **Orientation.** The femur is printed flat with the horn pocket on the bed. In-plane bending (the 19 mm-deep
  section) and out-of-plane bending (7 mm) both run along the layers (XY). Torsion is counted as interlayer shear, to be
  conservative.
- **Tibia-servo tab pilots.** These are vertical, so pull-out shears the layers (Z shear), while pilot bearing and
  ligament tear-out stay in-plane.
- **Sections checked:**
  - the horn clamp (5 mm floor) and the horn-pocket bearing at the femur stall;
  - the plate over the pocket at x 13 (Kt 2, at the drilled hole for the horn-arm screw);
  - the full section at x 16.5;
  - the inner tibia-servo pilot row at x 25.75 (Kt 2);
  - plate torsion;
  - the tibia-servo tab screws (pull-out over 5.5 mm, bearing, and the 1.60 mm ligament to the window);
  - the knee stall into the pilots;
  - the clamp preload;
  - the window rails on their own (advisory: the servo case, bolted at both tab rows, carries the moment across the
    window).

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
| 1 | femur stall 216 N·mm: horn-arm bearing on the pocket wall | XY | 1.59 | 25.00 | 15.74 | 3 | OK |
| 2 | sustained 2.90 N: femur horn clamp (Ø6 washer, 5 mm floor + arm screw) | Z shear | 0.14 | 6.25 | 45.73 | 4 | OK |
| 3 | walking 5.80 N: femur horn clamp (Ø6 washer, 5 mm floor + arm screw) | Z shear | 0.27 | 6.25 | 22.87 | 4 | OK |
| 4 | scrub: femur horn clamp (Ø6 washer, 5 mm floor + arm screw) | Z shear | 0.55 | 6.25 | 11.46 | 4 | OK |
| 5 | shove 3 N: femur horn clamp (Ø6 washer, 5 mm floor + arm screw) | Z shear | 0.98 | 6.25 | 6.36 | 3 | OK |
| 6 | stalls: femur horn clamp (Ø6 washer, 5 mm floor + arm screw) | Z shear | 0.92 | 6.25 | 6.77 | 3 | OK |
| 7 | drop 19.2 N: femur horn clamp (Ø6 washer, 5 mm floor + arm screw) | Z shear | 1.11 | 6.25 | 5.61 | 3 | OK |
| 8 | sustained 2.90 N: plate over the horn pocket x 13, arm-screw hole (Kt 2) | XY | 0.44 | 25.00 | 56.39 | 4 | OK |
| 9 | walking 5.80 N: plate over the horn pocket x 13, arm-screw hole (Kt 2) | XY | 0.89 | 25.00 | 28.19 | 4 | OK |
| 10 | scrub: plate over the horn pocket x 13, arm-screw hole (Kt 2) | XY | 1.59 | 25.00 | 15.75 | 4 | OK |
| 11 | shove 3 N: plate over the horn pocket x 13, arm-screw hole (Kt 2) | XY | 2.81 | 25.00 | 8.90 | 3 | OK |
| 12 | stalls: plate over the horn pocket x 13, arm-screw hole (Kt 2) | XY | 2.31 | 25.00 | 10.81 | 3 | OK |
| 13 | drop 19.2 N: plate over the horn pocket x 13, arm-screw hole (Kt 2) | XY | 2.55 | 25.00 | 9.82 | 3 | OK |
| 14 | walking 5.80 N: full section x 16.5, 19.0 x 7.0 | XY | 0.39 | 25.00 | 63.67 | 4 | OK |
| 15 | walking 5.80 N: inner tibia-servo pilot row x 25.75 (Kt 2) | XY | 0.53 | 25.00 | 47.10 | 4 | OK |
| 16 | walking 5.80 N: plate torsion, full 19.0 x 7.0 section (Z shear) | Z shear | 0.39 | 6.25 | 16.01 | 4 | OK |
| 17 | shove 3 N: full section x 16.5, 19.0 x 7.0 | XY | 1.20 | 25.00 | 20.87 | 3 | OK |
| 18 | shove 3 N: inner tibia-servo pilot row x 25.75 (Kt 2) | XY | 2.18 | 25.00 | 11.44 | 3 | OK |
| 19 | shove 3 N: plate torsion, full 19.0 x 7.0 section (Z shear) | Z shear | 1.06 | 6.25 | 5.92 | 3 | OK |
| 20 | drop 19.2 N: full section x 16.5, 19.0 x 7.0 | XY | 1.00 | 25.00 | 25.12 | 3 | OK |
| 21 | drop 19.2 N: inner tibia-servo pilot row x 25.75 (Kt 2) | XY | 2.24 | 25.00 | 11.16 | 3 | OK |
| 22 | drop 19.2 N: plate torsion, full 19.0 x 7.0 section (Z shear) | Z shear | 1.29 | 6.25 | 4.84 | 3 | OK |
| 23 | sustained 2.90 N: tibia-servo tab screw pull-out (M2x8, 5.5 mm, vertical pilot) | Z shear | 0.12 | 6.25 | 51.94 | 4 | OK |
| 24 | scrub: tibia-servo tab screw pull-out (M2x8, 5.5 mm, vertical pilot) | Z shear | 0.49 | 6.25 | 12.87 | 4 | OK |
| 25 | shove 3 N: tibia-servo tab screw pull-out (M2x8, 5.5 mm, vertical pilot) | Z shear | 0.88 | 6.25 | 7.14 | 3 | OK |
| 26 | drop 19.2 N: tibia-servo tab screw pull-out (M2x8, 5.5 mm, vertical pilot) | Z shear | 0.91 | 6.25 | 6.89 | 3 | OK |
| 27 | drop: tibia-servo tab pilot bearing | XY | 2.06 | 25.00 | 12.12 | 3 | OK |
| 28 | drop: pilot-to-window ligament 1.60 tear-out, whole radial force on one screw | XY shear | 0.28 | 12.50 | 45.37 | 3 | OK |
| 29 | knee stall 216 N·mm: tab pilot bearing (2 screws, 27.8 apart) | XY | 0.74 | 25.00 | 33.78 | 3 | OK |
| 30 | assembly: clamp screw snug 0.05 N·m (125 N): washer pull-through, 5.0 mm femur floor | Z shear | 1.33 | 6.25 | 4.71 | 3 | OK |
| 31 | assembly: clamp screw snug (125 N): washer bearing on the floor | XY | 5.44 | 25.00 | 4.59 | 3 | OK |

**lowest SF 4.59 (required 3) at: assembly: clamp screw snug (125 N): washer bearing on the floor**

Advisory (not in the verdict):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| assembly: clamp screw 'firmly' 0.1 N·m (250 N): washer pull-through, 5.0 mm femur floor | Z shear | 2.65 | 6.25 | 2.36 | 3 |
| walking 5.80 N: window rails alone, servo case ignored (Kt 2.5) | XY | 0.81 | 25.00 | 30.69 | 4 |
| shove 3 N: window rails alone, servo case ignored (Kt 2.5) | XY | 5.32 | 25.00 | 4.70 | 3 |
| drop 19.2 N: window rails alone, servo case ignored (Kt 2.5) | XY | 6.57 | 25.00 | 3.80 | 3 |

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

**The femur servos do not have enough margin.**
- **Standing evenly on all six feet:** each femur holds 50 N·mm (23 % of stall). That is fine.
- **Stopped on a tripod:** the femur holds **125–143 N·mm (58–66 %)** continuously. That is the middle leg's 41.5–47.5 %
  share at the 45 mm femur lever. Micro servos held this close to stall run hot and drift; a common target for
  continuous holding is about ⅓ of stall.
- **Walking:** peaks go past stall. The × 2 dynamics give 261 N·mm (121 %). Foot scrub pushing the foot outward gives
  232 N·mm (107 %). Expect the body to sag at each tripod change.
- **Knee and coxa servos:** lightly loaded in the coded gait, ≤ 102 N·mm (47 %), and that only under scrub. In the
  neutral pose a vertical foot load passes through the knee axis and gives no coxa torque.
- **Mass:** the coxa's required changes add ≈ 14 % to the robot mass, and every number here rises with it.

Fixes, cheapest first:
1. **Change the gait pose (software).** Stand and walk with the tibia turned **18.7° inward**, so the foot sits midway
   between the femur axis and the knee. The moment then splits: femur 65 and knee 65 N·mm (30 % each) at the same
   2.90 N. The body drops 3.7 mm unless the femur is raised slightly to match.
2. **Use proper inverse kinematics (software).** Move the stance feet in straight lines so they stop scrubbing (this
   removes the 107 % case), and soften the tripod hand-over so the dynamic peak stays well under × 2.
3. **Change the hardware.** Fit femur servos with about twice the torque (a ≈ 4–5 kg·cm metal-gear micro servo), or
   shorten the femur. L_F 45 → 30 cuts femur torque by a third, but changes the leg geometry and the assembly check.

## Proof test (spec §8, made specific)

The spec's test is the right size: 1 kg at the knee is about 1 × the drop cap at the femur root. It needs a way to stop
the femur servo back-driving, a defined clamp torque, and a measurable pass criterion.

1. **Set-up.**
   - Fit the femur on its horn on an MG90S clamped in a vice, with the M2×12 clamp screw **snug (0.05 N·m)**.
   - Fit the tibia servo and the tibia, with the femur level and the tibia hanging straight down.
   - Put a stop **above the femur's rear end** (behind the horn), so the femur servo's gears do not carry the moment.
2. **Load.** Hang **1 kg** from the foot tip for **1 min**. With the tibia vertical, this loads the femur root like the
   foot does, torsion included.
3. **Shove.** Push **3 N** sideways at the foot tip, each way, for 10 s.

Pass:
- no cracks or whitening at the pocket, the window corners or the pilots;
- no gap over 0.2 mm (feeler gauge) between the femur and the horn;
- after unloading, the knee returns to within 0.3 mm of where it started.

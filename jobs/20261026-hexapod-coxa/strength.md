VERDICT: FAIL

# Strength check: 20261026-hexapod-coxa (×6)

strength-analyst · 2026-10-26 · `python3 jobs/20261026-hexapod-coxa/strength_calc.py` (≈ 10 s)

**FAIL. 24 of 35 verdict rows fail. The lowest SF is 0.27**, at the post roots beside the femur-servo window in the
drop. The bracket fails even without a drop. Ordinary walking puts the posts at SF 1.01, the hub at 2.17 and the horn
clamp at 2.43, against 4 required.

All three weaknesses come from the same layout. The foot sits 31.5 mm in front of the vertical plate and 77 mm out
from the coxa horn, and that whole moment passes through thin printed sections:

1. **Posts beside the femur-servo window.** They are 5.95 × 4.5 mm, printed standing, so they bend across the layers.
   The femur servo hangs on its two tab screws. Its rocking moment about the screw line, ≈ 31.5 × F_up + 70 ×
   F_tangential (N·mm), bends both posts out of plane.
2. **Hub plate at the vertical plate's square inner end** (x 9.25). The foot moment (≈ 68 mm × F_up) steps from the
   deep L-section into the 5 mm hub at a sharp corner (Kt 2.5).
3. **Horn clamp.** The floor under the horn is only 3 mm. An upward foot force lifts the far side of the hub, so the M2
   centre screw and its Ø6 washer carry the whole 77 mm × F moment about a 3.6 mm pivot.

The coordinator's planned DFM round 2 changes (below) do not change this. The required changes at the end are checked
as one set.

## Print orientation and critical sections

- **Horizontal plate (hub and arm).** Printed on the bed, pocket side down, so the hub's bending runs along the layers
  (XY). Hub torsion is counted as interlayer shear (conservative).
- **Vertical plate.** Printed standing, so its out-of-plane bending puts σ_zz across the layers (Z). This applies at
  the floor band under the window, at the two posts (root at the window floor, z 10.7) and at the net section through
  the M2 tab pilots (z 17).
- **Femur-servo tab pilots.** These are horizontal holes in a standing wall, so pull-out and the 1.60 mm
  pilot-to-window ligament shear the layers (Z shear).
- **Sections checked:**
  - horn clamp (3.0 mm floor) and horn-pocket bearing at the coxa stall;
  - hub at x 9.2 (bending and torsion);
  - floor band at z 10.35 (34.8 × 4.5);
  - posts, at the root and at the pilot row;
  - tab-screw pull-out, bearing and ligament;
  - arm-and-plate L-section beside the r2.5 fillet;
  - clamp preload.

## The coordinator's planned geometry (DFM round 2)

The plan:
- Ø2 T-bone reliefs through the plate at x 16.2 and 37.1 on the window-floor line, z 10.7. Each is tangent to a post's
  inner edge, so the post section at the floor stays 5.95 × 4.5.
- The 45° 5 mm gusset (y −13.5…−8.5) runs over the full length, x 9.25–44.05, with the arm's far corners squared.

**This does not pass.**
- **The reliefs only help the corner.** They bring the window-corner Kt from ≈ 2.5 down to ≈ 2.0 (r/w 0.17). Kt 2.0
  also covers the gusset tip at z 10, which sits just under the post roots.
- **The full-length gusset misses the critical section.** It ends at z 10, below the post roots. It does remove the
  sharp plate-to-arm corner at the plate ends.
- **The real shortfall is section, not corner quality.** With no stress raiser at all (Kt 1), walking still gives SF
  2.5 against 4. With the spec's own 4 N walking load and Kt 2.0, the post root is at SF 1.8.

| Case | Post root, planned (Kt 2.0) | Post net section at the M2 pilot, z 17 (Kt 2) | SF req |
|---|---|---|---|
| sustained 2.90 N | 2.52 | 20.6 | 4 |
| walking 5.80 N | 1.26 | 10.3 | 4 |
| scrub | 1.03 | 4.58 | 4 |
| shove 3 N | 0.63 | **0.66** | 3 |
| stalls | 0.66 | **0.97** | 3 |
| drop 19.2 N | 0.33 | 1.74 | 3 |

The pilot row takes the whole rocking couple only when the tab pivots on its far edge (z 23). That happens with a
tangential push toward the plate or a downward force on the foot. Otherwise it carries only the yaw and in-plane
share.

The ligaments beside the pilot are 1.60 mm (window side) and 2.25 mm (plate end) in CAD, about 0.1 mm more each when
printed. The ≈ 1.2 mm estimate is low.

**Minimum equal posts.** The posts grow outward in x and the plate thickens toward −y, so the tab face stays at Y_F.
Planned R1 corners:

| T_V (mm) | Service cases only | With the 20 cm drop |
|---|---|---|
| 4.5 (today) | 28.5 | > 40 |
| 6 | 16.2 | 30.5 |
| 7 | 12.2 | 23.0 |
| 8 | 9.5 | 18.2 |
| 9 | 7.5 | 14.7 |
| 10 | 6.2 | 12.5 |
| 12 | 6.0 | 9.2 |

At 4.5 mm no practical post width passes, so the plate has to get thicker. The drop also needs longer tab screws: M2×8
pull-out is SF 2.31 in any plate, and M2×10 (7.5 mm engaged) brings it to 3.53.

The DFM estimates (3.1 MPa standing, 8.8 MPa under the shove) are nominal stresses. This check gives 2.5 MPa nominal
for the 2.90 N tripod share and 10.0 MPa for the shove, because it also includes the servo's yaw and pull-off. The
table above then applies Kt.

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

## Results (copied from `python3 strength_calc.py`; the geometry as modelled today)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | coxa stall 216 N·mm: horn-arm bearing on the pocket wall | XY | 1.59 | 25.00 | 15.74 | 3 | OK |
| 2 | sustained 2.90 N: coxa horn clamp (Ø6 washer, 3 mm floor + arm screw) | Z shear | 1.29 | 6.25 | 4.86 | 4 | OK |
| 3 | walking 5.80 N: coxa horn clamp (Ø6 washer, 3 mm floor + arm screw) | Z shear | 2.57 | 6.25 | 2.43 | 4 | **FAIL** |
| 4 | scrub: coxa horn clamp (Ø6 washer, 3 mm floor + arm screw) | Z shear | 2.07 | 6.25 | 3.01 | 4 | **FAIL** |
| 5 | shove 3 N: coxa horn clamp (Ø6 washer, 3 mm floor + arm screw) | Z shear | 2.92 | 6.25 | 2.14 | 3 | **FAIL** |
| 6 | stalls: coxa horn clamp (Ø6 washer, 3 mm floor + arm screw) | Z shear | 2.57 | 6.25 | 2.43 | 3 | **FAIL** |
| 7 | drop 19.2 N: coxa horn clamp (Ø6 washer, 3 mm floor + arm screw) | Z shear | 5.93 | 6.25 | 1.05 | 3 | **FAIL** |
| 8 | sustained 2.90 N: hub at the vertical plate's sharp inner end x 9.2 (Kt 2.5) | XY | 5.76 | 25.00 | 4.34 | 4 | OK |
| 9 | walking 5.80 N: hub at the vertical plate's sharp inner end x 9.2 (Kt 2.5) | XY | 11.51 | 25.00 | 2.17 | 4 | **FAIL** |
| 10 | scrub: hub at the vertical plate's sharp inner end x 9.2 (Kt 2.5) | XY | 9.00 | 25.00 | 2.78 | 4 | **FAIL** |
| 11 | shove 3 N: hub at the vertical plate's sharp inner end x 9.2 (Kt 2.5) | XY | 13.65 | 25.00 | 1.83 | 3 | **FAIL** |
| 12 | stalls: hub at the vertical plate's sharp inner end x 9.2 (Kt 2.5) | XY | 13.80 | 25.00 | 1.81 | 3 | **FAIL** |
| 13 | drop 19.2 N: hub at the vertical plate's sharp inner end x 9.2 (Kt 2.5) | XY | 23.59 | 25.00 | 1.06 | 3 | **FAIL** |
| 14 | sustained 2.90 N: post root at the window floor, 2 x 5.95 x 4.5 (sharp corner, Kt 2.5) | Z | 6.19 | 12.50 | 2.02 | 4 | **FAIL** |
| 15 | walking 5.80 N: post root at the window floor, 2 x 5.95 x 4.5 (sharp corner, Kt 2.5) | Z | 12.38 | 12.50 | 1.01 | 4 | **FAIL** |
| 16 | scrub: post root at the window floor, 2 x 5.95 x 4.5 (sharp corner, Kt 2.5) | Z | 15.24 | 12.50 | 0.82 | 4 | **FAIL** |
| 17 | shove 3 N: post root at the window floor, 2 x 5.95 x 4.5 (sharp corner, Kt 2.5) | Z | 24.91 | 12.50 | 0.50 | 3 | **FAIL** |
| 18 | stalls: post root at the window floor, 2 x 5.95 x 4.5 (sharp corner, Kt 2.5) | Z | 23.50 | 12.50 | 0.53 | 3 | **FAIL** |
| 19 | drop 19.2 N: post root at the window floor, 2 x 5.95 x 4.5 (sharp corner, Kt 2.5) | Z | 46.83 | 12.50 | 0.27 | 3 | **FAIL** |
| 20 | shove 3 N: post net section at the tab pilot z 17 (Kt 2 hole) | Z | 18.96 | 12.50 | 0.66 | 3 | **FAIL** |
| 21 | stalls: post net section at the tab pilot z 17 (Kt 2 hole) | Z | 12.94 | 12.50 | 0.97 | 3 | **FAIL** |
| 22 | drop 19.2 N: post net section at the tab pilot z 17 (Kt 2 hole) | Z | 7.20 | 12.50 | 1.74 | 3 | **FAIL** |
| 23 | scrub: femur-servo tab screw pull-out (M2x8, 4.5 mm in a horizontal pilot) | Z shear | 0.92 | 6.25 | 6.78 | 4 | OK |
| 24 | shove 3 N: femur-servo tab screw pull-out (M2x8, 4.5 mm in a horizontal pilot) | Z shear | 1.52 | 6.25 | 4.11 | 3 | OK |
| 25 | drop 19.2 N: femur-servo tab screw pull-out (M2x8, 4.5 mm in a horizontal pilot) | Z shear | 2.71 | 6.25 | 2.31 | 3 | **FAIL** |
| 26 | drop: tab pilot bearing (femur torque + radial load) | XY | 4.30 | 25.00 | 5.82 | 3 | OK |
| 27 | drop: pilot-to-window ligament 1.60 tear-out, whole radial force on one screw (Z shear) | Z shear | 0.43 | 6.25 | 14.58 | 3 | OK |
| 28 | walking 5.80 N: hub torsion at x 9.2 (Z shear) | Z shear | 0.70 | 6.25 | 8.95 | 4 | OK |
| 29 | walking 5.80 N: floor band under the window z 10.35, 34.8 x 4.5 (Kt 2) | Z | 3.76 | 12.50 | 3.32 | 4 | **FAIL** |
| 30 | walking 5.80 N: arm + plate L-section at x 21 beside the r2.5 fillet (Kt 1.6) | XY | 2.58 | 25.00 | 9.68 | 4 | OK |
| 31 | drop 19.2 N: hub torsion at x 9.2 (Z shear) | Z shear | 2.31 | 6.25 | 2.71 | 3 | **FAIL** |
| 32 | drop 19.2 N: floor band under the window z 10.35, 34.8 x 4.5 (Kt 2) | Z | 11.40 | 12.50 | 1.10 | 3 | **FAIL** |
| 33 | drop 19.2 N: arm + plate L-section at x 21 beside the r2.5 fillet (Kt 1.6) | XY | 6.52 | 25.00 | 3.83 | 3 | OK |
| 34 | assembly: clamp screw snug 0.05 N·m (125 N): washer pull-through, 3.0 mm coxa floor | Z shear | 2.21 | 6.25 | 2.83 | 3 | **FAIL** |
| 35 | assembly: clamp screw snug (125 N): washer bearing on the floor | XY | 5.44 | 25.00 | 4.59 | 3 | OK |

**lowest SF 0.27 (required 3) at: drop 19.2 N: post root at the window floor, 2 x 5.95 x 4.5 (sharp corner, Kt 2.5)**

Advisory (not in the verdict):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| assembly: clamp screw 'firmly' 0.1 N·m (250 N): washer pull-through, 3.0 mm coxa floor | Z shear | 4.42 | 6.25 | 1.41 | 3 |

## Required changes (the script checks them as one set: every row passes, lowest SF 3.19)

1. **Vertical plate.**
   - T_V 4.5 → **10 mm**, grown toward −y. The plate becomes y −23.5…−13.5, so ARM_Y[0] and HUB[2] go to −23.5.
   - Both posts at least **12.5 mm** wide, grown outward in x. With 13 mm posts the plate spans x 2.2…51.1: the margin
     past the pilots, 3.5 in VPLATE_X, becomes 10.55.
   - Keep the planned R1 T-bone reliefs and the full-length gusset.
   - Results: post root SF 0.27 → **3.19** in the drop and 1.01 → 11.6 walking; pilot row 0.66 → 9.1 under the shove;
     floor band 1.10 → 6.7 in the drop.
2. **Femur-servo tab screws.** M2×8 → **M2×10**, engaging 7.5 mm in the 10 mm plate. Drop pull-out SF 2.31 → 3.53.
3. **Horn floor.**
   - T_C 5 → **8 mm**, which makes the floor under the horn 6 mm instead of 3.
   - An **M3 penny washer, Ø10 × 1 mm**, under the head of the M2 centre screw.
   - Results: clamp SF 1.05 → **3.42** in the drop and 2.43 → 7.95 walking; snug-preload pull-through 2.83 → 9.4.
   - Screw length = washer 1 mm + floor 6 mm + the measured spline thread depth, so about M2×12–14. Measure the thread,
     as the DFM asked.
   - T_C also sets Z_F = T_C + 12, which raises the stance by 3 mm, so re-run `assembly_check.py`.
   - Equivalent alternative: keep T_C 5 and add an Ø18 × 8 mm boss under the horn. The hub step (item 4) then needs
     checking again.
4. **Hub step.** Where the vertical plate's inner end meets the hub, replace the square end with a 45° ramp at least
   8 mm long. With item 3 this takes the hub from SF 1.06 → **4.76** in the drop and 2.17 → 10.6 walking, and hub
   torsion from 2.71 → 7.2.

**Mass penalty.** The set adds ≈ 16 g per bracket, ≈ 95 g per robot (+14 %), and every walking and servo load rises by
the same 14 %. The walking rows still keep SF ≥ 7.9, and the drop rows are set by the servo cap rather than by mass.
But the femur-servo margin, already short, gets worse.

**A lighter alternative to item 1** (it needs its own check). Carry the femur servo at both ends: add a second wall
behind its case bottom (C y ≈ −29.4) with a **zero-clearance** pocket, joined to a widened arm. The rocking moment then
becomes a pair of in-plane forces about 13 mm apart instead of bending the posts. The pocket must fit tight: one with
the usual 0.2 mm clearance takes no load until the posts have already bent about 1°.

Required-change set as computed by the script (advisory rows):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req |
|---|---|---|---|---|---|
| FIX sustained 2.90 N: post root | Z | 0.54 | 12.50 | 23.14 | 4 |
| FIX sustained 2.90 N: post net section at the pilot | Z | 0.10 | 12.50 | 129.64 | 4 |
| FIX sustained 2.90 N: tab screw pull-out (M2x10, 7.5 mm) | Z shear | 0.23 | 6.25 | 26.64 | 4 |
| FIX sustained 2.90 N: horn clamp (Ø10, 6 mm floor) | Z shear | 0.39 | 6.25 | 15.91 | 4 |
| FIX sustained 2.90 N: hub at the new plate end x 2.15, T_C 8.0 (ramp, Kt 1.5) | XY | 1.18 | 25.00 | 21.11 | 4 |
| FIX walking 5.80 N: post root | Z | 1.08 | 12.50 | 11.57 | 4 |
| FIX walking 5.80 N: post net section at the pilot | Z | 0.19 | 12.50 | 64.82 | 4 |
| FIX walking 5.80 N: tab screw pull-out (M2x10, 7.5 mm) | Z shear | 0.47 | 6.25 | 13.32 | 4 |
| FIX walking 5.80 N: horn clamp (Ø10, 6 mm floor) | Z shear | 0.79 | 6.25 | 7.95 | 4 |
| FIX walking 5.80 N: hub at the new plate end x 2.15, T_C 8.0 (ramp, Kt 1.5) | XY | 2.37 | 25.00 | 10.55 | 4 |
| FIX scrub: post root | Z | 1.21 | 12.50 | 10.35 | 4 |
| FIX scrub: post net section at the pilot | Z | 0.27 | 12.50 | 46.90 | 4 |
| FIX scrub: tab screw pull-out (M2x10, 7.5 mm) | Z shear | 0.57 | 6.25 | 10.91 | 4 |
| FIX scrub: horn clamp (Ø10, 6 mm floor) | Z shear | 0.64 | 6.25 | 9.73 | 4 |
| FIX scrub: hub at the new plate end x 2.15, T_C 8.0 (ramp, Kt 1.5) | XY | 1.82 | 25.00 | 13.71 | 4 |
| FIX shove 3 N: post root | Z | 1.92 | 12.50 | 6.51 | 3 |
| FIX shove 3 N: post net section at the pilot | Z | 1.37 | 12.50 | 9.13 | 3 |
| FIX shove 3 N: tab screw pull-out (M2x10, 7.5 mm) | Z shear | 0.93 | 6.25 | 6.69 | 3 |
| FIX shove 3 N: horn clamp (Ø10, 6 mm floor) | Z shear | 0.91 | 6.25 | 6.88 | 3 |
| FIX shove 3 N: hub at the new plate end x 2.15, T_C 8.0 (ramp, Kt 1.5) | XY | 2.69 | 25.00 | 9.31 | 3 |
| FIX stalls: post root | Z | 1.82 | 12.50 | 6.86 | 3 |
| FIX stalls: post net section at the pilot | Z | 1.11 | 12.50 | 11.26 | 3 |
| FIX stalls: tab screw pull-out (M2x10, 7.5 mm) | Z shear | 0.88 | 6.25 | 7.09 | 3 |
| FIX stalls: horn clamp (Ø10, 6 mm floor) | Z shear | 0.78 | 6.25 | 8.02 | 3 |
| FIX stalls: hub at the new plate end x 2.15, T_C 8.0 (ramp, Kt 1.5) | XY | 2.70 | 25.00 | 9.26 | 3 |
| FIX drop 19.2 N: post root | Z | 3.92 | 12.50 | 3.19 | 3 |
| FIX drop 19.2 N: post net section at the pilot | Z | 0.70 | 12.50 | 17.79 | 3 |
| FIX drop 19.2 N: tab screw pull-out (M2x10, 7.5 mm) | Z shear | 1.77 | 6.25 | 3.53 | 3 |
| FIX drop 19.2 N: horn clamp (Ø10, 6 mm floor) | Z shear | 1.83 | 6.25 | 3.42 | 3 |
| FIX drop 19.2 N: hub at the new plate end x 2.15, T_C 8.0 (ramp, Kt 1.5) | XY | 5.25 | 25.00 | 4.76 | 3 |
| FIX walking 5.80 N: floor band 48.9 x 10.0 (Kt 2) | Z | 0.64 | 12.50 | 19.68 | 4 |
| FIX walking 5.80 N: hub torsion, T_C 8.0 | Z shear | 0.26 | 6.25 | 23.87 | 4 |
| FIX drop 19.2 N: floor band 48.9 x 10.0 (Kt 2) | Z | 1.87 | 12.50 | 6.67 | 3 |
| FIX drop 19.2 N: hub torsion, T_C 8.0 | Z shear | 0.87 | 6.25 | 7.22 | 3 |
| FIX assembly: clamp screw snug (125 N), Ø10 washer pull-through, 6 mm floor | Z shear | 0.66 | 6.25 | 9.42 | 3 |

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

## Proof test (for the redesigned bracket; replaces spec §8)

The spec's test hangs 1 kg from the femur-servo horn, only ≈ 14 mm in front of the posts. That loads them to about
¼ of the walking case. Load the bracket through the leg instead:

1. Assemble one leg (coxa servo, bracket, femur, tibia) with the clamp screws snug (0.05 N·m).
2. Power the servos at 6 V in the neutral pose and clamp the coxa servo body in a vice.
3. Hang 0.45 kg (4.4 N, 1.5 × the static tripod share) from the foot tip for **10 min**. The femur servo then holds
   about 200 N·mm, which is still under its stall torque.
4. Push 3 N sideways at the foot tip, each way, for 10 s.
5. Finally run the body-bottom spec §8 drop test: 3 × 20 cm landing flat on 6 feet, then 3 × 20 cm tilted so it lands
   on 3.

Pass:
- no whitening or cracks at the post roots, reliefs, gusset tip, pilots or hub step;
- no gap over 0.2 mm (feeler gauge) between the bracket and the coxa horn;
- after unloading, the foot returns to within 0.5 mm of where it started.

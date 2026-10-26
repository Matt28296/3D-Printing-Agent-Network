VERDICT: FAIL

# Strength check: 20261026-hexapod-coxa (×6), round 3

Independent strength-analyst · 2026-10-26 · `python3 jobs/20261026-hexapod-coxa/strength_calc.py` (about 30 s; needs
build123d, trimesh and scipy, like `cad_checks.py`)

**FAIL by one row. The lowest SF is 2.91 against 3**, for the horn clamp in the 20 cm drop: the Ø10 washer pulled
through the floor, with the part printed as `print_requirements.json` specifies (4 perimeters, 50 % gyroid). Every
other row passes; the next lowest is 3.14.

- **The round-3 geometry is sound.** Every change strength round 1 asked for is in the model and works (table below).
- **What fails is the print setting.** Under the washer, the 6 mm floor is a 1 mm top skin over a 50 % gyroid core.
  That core carries the washer's plug shear at about 0.35 × solid, so the floor holds 868 N instead of 1470 N.
- **Required change (no geometry change): print the coxa solid.** Raise `print_requirements.json` min
  `fill_density` from 50 to 100. Every row then passes:
  - the lowest SF is 4.22 (post roots, drop);
  - the clamp is at 4.92.
  - The cost is 31.0 g per bracket instead of 22.1 g: +53 g on the robot (906 g with the body-bottom changes), and a
    longer slice.

**How firm the FAIL is.** The clamp is 3 % short, and that depends on the infill model. The row reaches 3.0 with
either of these:
- the core's shear strength at ρ^1.3 instead of ρ^1.5;
- a back-drive cap of 1.9 × stall instead of 2.

The row is short for a structural reason. The clamp is the only place in the leg where the whole leg moment
(F × 55.9 mm in the drop) acts on a 3.6 mm lever, the horn hub's edge. So the M2 clamp screw pulls 299 N on its
washer in the drop.

## What changed since strength round 1: every requested fix is in

| Round-1 required change | Round 3 | Checked |
|---|---|---|
| T_V 4.5 → 10, plate grown to −y (y −23.5 … −13.5); arm and hub to y −23.5 | `hex_frame.T_V` 10; `HUB`, `ARM_Y` to −23.5 | `cad_checks.py`; section z 13.7 is 283.0 mm², the same exact (build123d) and rastered |
| Posts ≥ 12.5 mm, grown outward | `POST_W` 13, plate x 1.9 … 51.1. The inner post measures 15.25 at its root because the ramp widens it | yes |
| Keep the R1 T-bone reliefs and the full-length gusset | `RELIEF_D` 2; gusset over x 1.9 … 51.1 | yes |
| Femur-servo tab screws M2 × 8 → M2 × 10, 7.5 mm engaged | spec §2, BUILD_GUIDE §1 | rows 19–24 |
| T_C 5 → 8 (6 mm floor) + Ø10 × 1 penny washer; M2 × 12–14 | `hex_frame.T_C` 8; spec §2, BUILD_GUIDE | rows 2–9, 32 |
| 45° ramp ≥ 8 mm at the plate's inner end | `RAMP` 8: the full-height plate now starts at x 1.9, inside the horn pivot (x 3.6) | rows 30–31; the hub is no longer critical (SF ≥ 25) |
| Proof test into spec §8 | in spec §8 | see "Proof test" |

Round 3 also added:
- the B1 lead notch with the outboard pilot moved 1.3 mm, which leaves a 1.35 mm ligament (row 26);
- the SYS-5 tie slot, at z 30 above the servo's tab zone (z 13.9–26.1), where the post carries almost nothing (not
  rowed);
- a 6 mm corner cut on an unloaded corner.

**Round 3 also loads the bracket differently.**
- The tucked stance moves the foot from 77 to 54.4 mm out of the coxa axis, which cuts the hub moments.
- The tangential offset that bends the posts barely changes: the foot sits 31.2 mm off the plate's mid-plane (31.55 in
  round 2).
- In the drop, the stance needs no inward friction to reach the servo cap, so nothing relieves the clamp.

## Load cases

The same block runs in all five round-3 hexapod checks. `strength_calc.py` rebuilds it from:
- `hex_frame.py`: round-3 frames, stance femur −4.7°, tibia −14.0°, IK gait;
- `tools/hobby_parts.py`: MG90S, 216 N·mm stall, 13.4 g;
- the five `model.py`, built with build123d;
- each `print_requirements.json`.

**Robot mass: 840 g (8.24 N). This is my number.**
- **Printed parts: 334 g.** Each part goes through a slicer-like layer model (below), × 1.045:
  - bottom plate 82.8 g;
  - deck 36.2 g;
  - 6 coxae × 22.1 g;
  - 6 femurs × 6.6 g;
  - 6 tibias × 7.1 g.

  Printed solid, they would be 463 g. Calibration: on the four round-2 slices (tibia, femur, deck, bottom plate) the
  model reads 1.4–4.3 % under the slicer's filament weight, so ×1.045 is the largest ratio.
- **Bought parts: 506 g, itemised from BUILD_GUIDE §1:**
  - 18 MG90S 241.2 g; horns 6.3 g;
  - 2 × PCA9685 18 g; ESP32 10 g;
  - LiPo 65 g; UBEC 25 g; buck 2 g;
  - switch 15 g; fuse and holder 6 g; XT30 pigtail 5 g; alarm 7 g; capacitors and divider 5.6 g;
  - 12 extensions 36 g;
  - screws, washers and nuts 33.4 g; ties and strap 10 g;
  - harness 20 g.
- **Against the designer's 812–877 g.** The 812 g figure uses the deep review's 0.76 printed fraction and a lighter
  bought list. The 877 g figure counts the printed parts as solid.
- **With every round-3 required change made, the robot is 906 g:** a solid coxa, plus the body-bottom's `MARGIN` 8
  and Ø10 columns. All change-set rows use 906 g.

| Case | Foot force | Poses | Duration, SF |
|---|---|---|---|
| Sustained | share × weight, up to **3.58 N** up | Every planted foot of every tripod-only frame of the 30 and 40 mm IK gaits (`hex_frame.gait_pose`), plus both neutral tripods (102 feet). Shares solved exactly, CG anywhere within ±3 mm of the centre: max **0.435** | sustained, 4 |
| Walking | ×2: up to **7.16 N** | same | cyclic, 4 |
| Foot friction | 3.58 N up + µ 0.5 in any horizontal direction, all servos within stall | the stance plus the 6 poses where a joint reaches its gait extreme | cyclic, 4 |
| Shove | 3 N in any horizontal direction, with 0 … 3.58 N up | same 7 poses | short-term, 3 |
| Servo stall (spec: one at a time) | Vertical, either way, until the first servo stalls. Or radial/tangential on top of 3.58 N up, until the first servo stalls. At the stance: 9.6 N vertical, 4.0 N tangential, 3.1 N radial. Plus 216 N·mm straight into the horn pocket | same 7 poses | short-term, 3 |
| 20 cm drop | Up to the back-drive cap, femur and knee at 2 × stall = 432 N·mm: **19.2 N** up at the stance, with radial friction up to µ 0.5 within the cap | same 7 poses (cap 18.9–19.3 N) | short-term, 3 |
| Assembly | M2 horn-clamp screw snug, 0.05 N·m ≈ 125 N | — | short-term, 3 |

Service temperature 40 °C against PETG's ≈ 70 °C: OK.

**Against deep review 05.** I use its load cases (tripod lone-leg share, ×2 walking, the servo-capped drop). My
numbers differ where round 3 or my margins move them:

| Quantity | DR05 | Here | Why |
|---|---|---|---|
| Mass | 662 g | 840 g (906 g with the fixes) | Round-3 strength set: the coxae weigh +81 g printed, the 6 mm plate +18 g. Bought parts +75 g: switch, fuse, alarm, 6 more extensions, nuts and washers, a bigger UBEC |
| Lone-leg share | 41 % | 41.1–41.7 % with the CG at the centre (the same as `stance_torques.py`); **43.5 %** with the CG anywhere within ±3 mm | the legs swing; DR05 found the CG 1 mm off |
| Static foot load | 2.8 N | 3.58 N | mass and CG margin |
| Drop per foot | 14.4–19.2 N | 19.2 N | The tucked stance puts the foot 22.4 mm from both the femur and the knee axis, so 432/22.4 = 19.2 N with no friction needed (round 2 needed 6.2 N inward) |
| Coxa-shaft bending, static tripod | 187–203 (round 2); 156–161 tucked at 662 g | **209 N·mm** (418 walking) | mass and CG margin |
| Coxa-shaft bending, drop | 1130–1510 N·mm | **1075 N·mm** | the foot is now 55.9 mm from the coxa axis, not 78.6 |

## Assumptions

- **One leg covers all six.** A leg's internal loads depend only on its joint angles and on the foot force in its own
  frames, so leg 0's frames are used for every pose.
- **The drop cap is an assumption.** A powered MG90S is back-driven at about 2 × stall (spec, DR05). At 1.5 × stall
  the cap would be 14.4 N and the failing row SF 3.9. The motor's reflected inertia may push the very first contact
  above the cap on a hard floor, so the drop test must be on carpet, as the body-bottom spec says.
- **Printed construction**, from `print_requirements.json` on the 0.20 mm QUALITY profile:
  - Perimeter band 0.45 + 3 × 0.407 = **1.67 mm**; top and bottom skins 5 × 0.2 = **1.0 mm**.
  - Each 0.2 mm layer is rasterised at 0.1 mm and classified as the slicer builds it: perimeter, top/bottom solid,
    or infill.
  - Perimeters and skins count as solid.
  - The 50 % gyroid core is a cellular solid (Gibson–Ashby, as in the rover-wheel review): stiffness ρ² = 0.25,
    strength ρ^1.5 = 0.35.
  - Bending is taken on the composite section at the outermost solid fibre; core points are checked as well.
  - Under the clamp washer the classes are verified: at r 5 the plug passes the pocket's perimeter ring (z 0–2),
    infill (z 2–7) and the top skin (z 7–8). The as-printed plug area is 139 mm², against 235 mm² solid.
- **Section properties from the build123d solid.** Every rastered section agrees with build123d's exact section area
  within 0.6 %.
- **Femur servo on its two tab screws** (strength round 1's model, round-3 numbers):
  - it is a rigid body on the two screws;
  - its rocking moment about the screw line splits between the posts by width;
  - yaw acts as opposite y-forces at the screws, 6.4 mm above the post roots;
  - the radial force bends each post in plane;
  - the in-plane moment and any pull loads them axially.
  - The pilot row takes the rocking moment only when the tab pivots on its far edge.
  - The case gets no credit in the window (0.1–0.2 mm clearance).
- **Horn clamp.**
  - The joint tips on the horn hub's edge (r 3.6); the 1.6 mm horn arm can't carry the pivot.
  - The screw holds the resultant horizontal moment over 3.6 mm, plus any pull-off.
  - Capacity is the washer's plug shear on the cylinder r 5 through the whole hub (z 0–8), against the interlayer
    shear allowable.
  - The washer's bearing pressure shares between the solid perimeter ring round the clamp hole (to r 3.0) and the
    skin over the core, by stiffness.
- **Kt:** 2.0 at the R1-relief post roots, holes and the band; 1.5 at the ramp.
- **Preload.** No bolt preload is counted for strength (fdm-design-rules: PETG creeps). Preload enters only the
  assembly row.

## Allowables and sources

`library/materials.csv` has no rows, and `inputs/` has no printed-specimen datasheet. So these are the strength-checks
**placeholders**, and NEEDS_TEST is the best verdict possible.

| Quantity | Value (MPa) | Source |
|---|---|---|
| Tension or bending along the layers (XY) | 25 | placeholder, PETG |
| Across the layers (Z) | 12.5 | 0.5 × in-plane (placeholder) |
| Shear, in-plane / interlayer | 12.5 / 6.25 | 0.5 × normal (as every earlier hexapod, arm and rover check) |
| Bearing (compression) | 25 | in-plane value |
| Infill core | ρ^1.5 × the above: 0.35 at 50 % (crush 8.84) | Gibson–Ashby, rover-wheel review |
| E | 1800 | placeholder |

## Results: the design as specified (as printed, 50 % gyroid)

| # | Case | Section | Dir | Stress | Allow. | SF | Req. | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | coxa stall 216 N·mm | horn arm on the pocket wall (perimeters) | XY | 1.59 | 25.0 | 15.74 | 3 | OK |
| 2 | sustained 3.58 N | horn clamp: Ø10 washer pulled through the floor | Z shear | 0.42 | 6.25 | 14.93 | 4 | OK |
| 3 | walking 7.16 N | horn clamp | Z shear | 0.84 | 6.25 | 7.47 | 4 | OK |
| 4 | foot friction | horn clamp | Z shear | 0.77 | 6.25 | 8.13 | 4 | OK |
| 5 | shove | horn clamp | Z shear | 1.02 | 6.25 | 6.16 | 3 | OK |
| 6 | stall | horn clamp | Z shear | 1.14 | 6.25 | 5.46 | 3 | OK |
| **7** | **drop 19.2 N** | **horn clamp (screw force 299 N; plug 868 N)** | **Z shear** | **2.15** | **6.25** | **2.91** | **3** | **FAIL** |
| 8 | drop | Ø10 washer on the floor's skin over the 50 % core | crush | 2.28 | 8.84 | 3.88 | 3 | OK |
| 9 | drop | Ø10 washer on the clamp hole's perimeter ring | bearing | 7.97 | 25.0 | 3.14 | 3 | OK |
| 10 | sustained | post roots z 13.7 (R1 reliefs, Kt 2.0) | Z | 0.64 | 12.5 | 19.62 | 4 | OK |
| 11 | walking | post roots | Z | 1.27 | 12.5 | 9.81 | 4 | OK |
| 12 | foot friction | post roots | Z | 1.54 | 12.5 | 8.14 | 4 | OK |
| 13 | shove | post roots | Z | 2.12 | 12.5 | 5.91 | 3 | OK |
| 14 | stall | post roots | Z | 2.74 | 12.5 | 4.56 | 3 | OK |
| 15 | drop | post roots | Z | 3.63 | 12.5 | 3.44 | 3 | OK |
| 16 | shove | post net section at the pilot row z 20 (Kt 2) | Z | 1.60 | 12.5 | 7.81 | 3 | OK |
| 17 | stall | pilot row | Z | 2.36 | 12.5 | 5.30 | 3 | OK |
| 18 | drop | pilot row | Z | 0.77 | 12.5 | 16.31 | 3 | OK |
| 19 | sustained | femur-servo tab screw pull-out (M2 × 10, 7.5 mm in the pilot's perimeters) | Z shear | 0.26 | 6.25 | 24.13 | 4 | OK |
| 20 | walking | tab screw pull-out | Z shear | 0.52 | 6.25 | 12.06 | 4 | OK |
| 21 | foot friction | tab screw pull-out | Z shear | 0.64 | 6.25 | 9.69 | 4 | OK |
| 22 | shove | tab screw pull-out | Z shear | 0.91 | 6.25 | 6.87 | 3 | OK |
| 23 | stall | tab screw pull-out | Z shear | 1.23 | 6.25 | 5.08 | 3 | OK |
| 24 | drop | tab screw pull-out | Z shear | 1.43 | 6.25 | 4.38 | 3 | OK |
| 25 | drop | tab pilot bearing | XY | 1.84 | 25.0 | 13.56 | 3 | OK |
| 26 | drop | moved outboard pilot → lead notch, 1.35 mm CAD ligament | Z shear | 0.18 | 6.25 | 35.10 | 3 | OK |
| 27 | walking | band under the window z 13.0, through the reliefs (Kt 2) | Z | 0.79 | 12.5 | 15.88 | 4 | OK |
| 28 | shove | band | Z | 1.07 | 12.5 | 11.66 | 3 | OK |
| 29 | drop | band | Z | 2.12 | 12.5 | 5.89 | 3 | OK |
| 30 | walking | hub + plate section x 6, outboard of the pivot (Kt 1.5) | XY | 0.38 | 25.0 | 66.48 | 4 | OK |
| 31 | drop | hub + plate section x 6 | XY | 0.98 | 25.0 | 25.45 | 3 | OK |
| 32 | assembly, snug 125 N | horn clamp: washer pull-through | Z shear | 0.90 | 6.25 | 6.94 | 3 | OK |

**Lowest SF 2.91 (required 3), at row 7.** Solid sections, the predecessor's basis, would give the same row 4.92.

## Required change, checked as a set (at 906 g)

**`print_requirements.json`: min `fill_density` 50 → 100 for the coxa.** Every row passes:

| Section | Sustained | Walking | Friction | Shove | Stall | Drop |
|---|---|---|---|---|---|---|
| Horn clamp (235 mm² plug, 1470 N) | 23.45 | 11.72 | 13.39 | 10.05 | 9.25 | **4.92** |
| Post roots (Kt 2.0) | 22.29 | 11.15 | 9.15 | 6.93 | 5.36 | **4.22** |
| Pilot row (Kt 2) | — | — | — | 8.78 | 6.10 | 19.89 |
| Tab screw pull-out | 22.37 | 11.18 | 8.98 | 6.72 | 4.99 | 4.38 |
| Band (Kt 2) | — | 17.33 | — | 13.01 | — | 6.90 |

Also: washer bearing in the drop 6.13; hub section 44.65; snug-preload pull-through 11.76. **Lowest 4.22**, required 3.

A possible alternative that I have **not** checked: keep 50 % infill and make only the hub floor solid, with a
modifier over the hub or `top_solid_layers` ≥ 30. Its rows would need re-running. The required change above is the
one I verified.

Sensitivity of the failing row, as specified:
- core shear strength ρ^1.3: SF 3.07; ρ^1.0: 3.36;
- back-drive cap 1.9 × stall: 3.06; 1.5 × stall: 3.87.

## Beyond the spec (advisory, not in the verdict)

| Case | As printed, 50 % | 100 % infill |
|---|---|---|
| Drop with friction in **any** direction (tangential up to the coxa servo's back-drive, 7.9 N at the foot): post roots | 1.85 | 2.23 |
| same: femur-servo tab screw pull-out | 2.16 | 2.16 |
| same: horn clamp | 2.31 | 3.90 |
| **Any combination** of stalled servos at once: pilot row | 2.65 | 3.00 |

The spec's drop case has radial friction only. A **tilted** landing can drive a corner leg's foot sideways, so this is
the residual risk that the tilted drop test settles.
- If it cracks the post roots or pulls the tab screws, the next step is the coxa brief's second support: the bump arc
  under the bottom plate, or a support opposite the horn.
- More plate wouldn't fix that load path.

**Assembly advisory.** A "firm" 0.1 N·m (250 N) on the clamp screw gives washer pull-through SF 3.47 as printed and
6.9 solid. Snug stays the instruction.

## Proof test

Once the change is made, the verdict becomes NEEDS_TEST (placeholder allowables). **Spec §8's test does not match it**
and should become the following.

1. **Leg test first:** as in the assembly spec §8 (deep review SYS-6), unchanged.
2. **Static, bracket.**
   - Take the femur off. Clamp the coxa servo body in a vice **shaft up**, so a hanging load acts on the bracket the
     way the ground does.
   - Hang **2.8 kg** from the femur servo's horn: a loop through its holes, on the shaft axis, so the femur servo
     carries no torque. Hold **1 min**.
   - This puts 2 × the walking load at the stance foot (15.4 N at 906 g) on the post roots, the femur-servo tab
     screws and the horn clamp. At the horn that takes 27.5 N, which the script derives. The 100 % bracket is then at
     SF 5.5 (posts) and 6.0 (clamp).
   - Use a spare femur servo if you don't want 27 N on the leg's own shaft.
3. **Side push.** Refit the femur and tibia, servos powered in the walking stance. Push **6 N** sideways at the foot
   tip, each way, for 10 s: 1.5 × the 4.0 N a coxa stall puts there.
4. **Drop:** the body-bottom spec §8 drop test, on carpet. Use spare coxa servos, or run it only after step 1 has
   passed (DR05 SYS-6).

Pass:
- no whitening or cracks at the post roots, R1 reliefs, pilots, lead notch, gusset tip, ramp, or the floor round the
  washer;
- no gap over 0.2 mm (feeler gauge) between the bracket and the horn while loaded;
- after unloading, the horn returns within 0.3 mm of where it started (step 2) and the foot within 0.5 mm (steps
  3–4).

Why spec §8 doesn't match as written:
- **Too light.** Its 0.45 kg at the foot is 4.4 N: 0.6 × the walking load, under the skill's 1.5–2 × service.
- **Wrong direction.** A weight hung from the foot of an upright leg pulls the foot **down**, the opposite of the
  ground's push. That reverses the clamp's lifting side and the posts' tension face.
- **Wrong pose.** Its "neutral pose", with the femur servo "holding about 200 N·mm", is the servo centre (femur
  level): 92 % of stall for 10 min. The walking stance is femur −4.7°, tibia −14.0°.
- **Drop on the robot's own servos.** Its step 5 does that before the leg test.

**The leg test (assembly §8).** 680 g = 6.7 N at the foot is 0.93 × my walking load. In the stance the coxa shaft then
sees 373 N·mm, 0.89 × walking. It is a good creep and play test of the servo, and none of these verdicts depends on it.

## Servo torques (system context; not a printed-part row)

At 840 g with the CG margin, static over the 30/40 mm gaits:
- femur 94 N·mm (43 % of stall);
- knee 107 N·mm (50 %).

With ×2 walking that is 187 / 214 N·mm: the knee reaches stall at a 40 mm stride. The `stance_torques.py` numbers at
812 g with a centred CG are 87 / 98. Walk at the 30 mm stride the plan chose, and watch the case temperatures
(assembly §8).

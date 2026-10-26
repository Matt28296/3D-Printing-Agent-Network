VERDICT: NEEDS_TEST

# Strength check: 20261026-hexapod-femur (×6), round 3

Independent strength-analyst · 2026-10-26 · `python3 jobs/20261026-hexapod-femur/strength_calc.py` (about 30 s; needs
build123d, trimesh and scipy, like `cad_checks.py`)

**NEEDS_TEST: placeholder allowables only. No change to the geometry is needed.**
- **Lowest SF 4.19:** the clamp washer pulled through the 5 mm horn floor at the snug preload (assembly), as printed.
- **Lowest service SF 4.50:** the horn clamp under a servo stall.
- **Drop rows:** 7.31 or more.

The round-3 changes help the femur:
- **Less torsion.** With the tibia servo reversed, the tibia's mid-plane is 10.1 mm in front of the femur's (16.4 mm
  in round 2).
- **Small in-plane moment in the tucked stance.** The vertical foot load's moment changes sign at x ≈ 22.5 along the
  femur, so it never exceeds the femur or knee servo torque (≤ 432 N·mm, the back-drive cap).

The spec §8 proof test needs three small changes (bottom).

## What changed since strength round 1

- **Clamp screw snug ≈ 0.05 N·m** (round 1's condition): in spec §2 and BUILD_GUIDE §3 step 6. Rows 27–28.
- **Femur servo margin** (round 1's system note): the tucked stance. Round-3 servo torques are below.
- **Tibia servo reversed** (B1 option 2): tabs on the back face, M2 × 8 from the back, 5.5 mm engaged. A push towards
  the coxa now pulls the screws out rather than bearing. Rows 18–23 cover both directions: the stall case and the
  shove push either way.
- **SYS-5 tie slot** at (20, −6): the section through it is in the table (x 20.0). It doesn't govern.

## Load cases

The same block as all five round-3 checks (details in the coxa's `strength.md`):
- **Robot mass 840 g:** 334 g printed (layer model calibrated on the round-2 slices) + 506 g bought (BUILD_GUIDE §1).
  906 g with every round-3 change.
- **Lone-leg share up to 0.435** (CG within ±3 mm).
- **Sustained 3.58 N**, walking ×2 = 7.16 N, over every planted foot of the 30 and 40 mm IK gaits.
- **Foot friction** µ 0.5, servos ≤ stall.
- **Shove** 3 N.
- **Servo stalls** one at a time (at the stance: 9.6 N vertical, 4.0 N tangential, 3.1 N radial).
- **20 cm drop:** 19.2 N up per foot (femur and knee back-driven at 2 × stall), with radial friction.
- **Assembly:** clamp screw snug, 125 N.
- Temperature 40 °C against ≈ 70 °C: OK.

In the femur's frame F (x along the femur, z out of the front face), the stance foot is at (28.1, −67.9, 13.6):
- the vertical foot force bends the femur in its own 19 mm plane;
- torsion is F × 10.1 mm.

## Assumptions

- **Printed:** 4 perimeters (1.67 mm band), 1.0 mm top and bottom skins, 50 % gyroid core. The core counts at
  stiffness ρ² = 0.25 and strength ρ^1.5 = 0.35 (rover-wheel review).
  - Sections are rastered from the built solid. Areas agree with build123d's exact sections within 0.6 %.
  - As printed, the in-plane second moment is 0.71–0.83 × solid (0.83 through the tie slot, whose perimeters fill
    the section); the out-of-plane one is 0.81–0.83 × solid.
- **Bending** is taken on the composite section (biaxial, unsymmetric). Kt:
  - 1.5 over the horn hub;
  - 2.0 at the arm-screw hole (x 13), the tie slot (x 20) and the inner pilot row (x 25.6).
- **Torsion,** as printed: the perimeter/skin tube alone carries it (Bredt; the core is ignored).
  - The side walls carry it across the layers.
  - The skins carry it along the layers.
  - Solid Roark values are advisory.
- **Horn clamp:** the predecessor's model.
  - The joint tips on the horn hub's edge, r 3.6.
  - Capacity is the Ø6 washer's plug shear through the whole link, z 0–7: 84 mm² as printed (94 solid), 524 N.
- **Tibia servo:** a rigid body on its two screws.
  - Pull-out = roll over the tab edges (6.1 mm) + pitch over the screw spacing + any pull off the back face.
  - The case gets no credit in the window. The window rails alone are advisory: the case, bolted at both tab rows,
    carries the window's torsion through the tab couples, which the screw rows check.

## Allowables and sources

Placeholders (no rows in `library/materials.csv`, no datasheet in `inputs/`):
- along / across the layers: 25 / 12.5 MPa;
- in-plane / interlayer shear: 12.5 / 6.25 MPa;
- bearing: 25 MPa;
- infill core: ρ^1.5 × these;
- E: 1.8 GPa.

So NEEDS_TEST is the best possible verdict.

## Results (as specified, as printed)

| # | Case | Section | Dir | Stress | Allow. | SF | Req. | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | femur stall 216 N·mm | horn arm on the pocket wall | XY | 1.59 | 25.0 | 15.74 | 3 | OK |
| 2 | sustained 3.58 N | horn clamp: Ø6 washer pull-through | Z shear | 0.14 | 6.25 | 45.40 | 4 | OK |
| 3 | walking 7.16 N | horn clamp | Z shear | 0.28 | 6.25 | 22.70 | 4 | OK |
| 4 | foot friction | horn clamp | Z shear | 0.61 | 6.25 | 10.22 | 4 | OK |
| 5 | shove | horn clamp | Z shear | 0.94 | 6.25 | 6.66 | 3 | OK |
| 6 | stall | horn clamp | Z shear | 1.39 | 6.25 | 4.50 | 3 | OK |
| 7 | drop 19.2 N | horn clamp | Z shear | 0.74 | 6.25 | 8.44 | 3 | OK |
| 8 | sustained | worst section: x 25.6, inner pilot row (Kt 2) | XY | 0.43 | 25.0 | 58.63 | 4 | OK |
| 9 | walking | x 25.6 | XY | 0.85 | 25.0 | 29.31 | 4 | OK |
| 10 | foot friction | x 13, arm-screw hole (Kt 2) | XY | 1.85 | 25.0 | 13.49 | 4 | OK |
| 11 | shove | x 13 | XY | 2.83 | 25.0 | 8.83 | 3 | OK |
| 12 | stall | x 4, over the horn hub (Kt 1.5) | XY | 2.08 | 25.0 | 12.02 | 3 | OK |
| 13 | drop | x 25.6 | XY | 2.80 | 25.0 | 8.94 | 3 | OK |
| 14 | walking | torsion x 16.5, skin tube | Z shear | 0.21 | 6.25 | 30.17 | 4 | OK |
| 15 | shove | torsion | Z shear | 0.70 | 6.25 | 8.89 | 3 | OK |
| 16 | stall | torsion | Z shear | 1.08 | 6.25 | 5.80 | 3 | OK |
| 17 | drop | torsion | Z shear | 0.56 | 6.25 | 11.21 | 3 | OK |
| 18 | sustained | tibia-servo tab screw pull-out (M2 × 8 from the back, 5.5 mm) | Z shear | 0.16 | 6.25 | 39.16 | 4 | OK |
| 19 | walking | tab screw pull-out | Z shear | 0.32 | 6.25 | 19.58 | 4 | OK |
| 20 | foot friction | tab screw pull-out | Z shear | 0.56 | 6.25 | 11.14 | 4 | OK |
| 21 | shove | tab screw pull-out | Z shear | 0.84 | 6.25 | 7.43 | 3 | OK |
| 22 | stall | tab screw pull-out | Z shear | 1.32 | 6.25 | 4.73 | 3 | OK |
| 23 | drop | tab screw pull-out | Z shear | 0.85 | 6.25 | 7.31 | 3 | OK |
| 24 | drop | tab pilot bearing | XY | 2.03 | 25.0 | 12.29 | 3 | OK |
| 25 | drop | pilot → window ligament 1.45 mm CAD | XY shear | 0.24 | 12.5 | 51.12 | 3 | OK |
| 26 | knee stall 216 N·mm | pilot bearing, 2 screws 27.8 apart | XY | 0.74 | 25.0 | 33.78 | 3 | OK |
| 27 | assembly, snug 125 N | Ø6 washer pull-through (as printed) | Z shear | 1.49 | 6.25 | 4.19 | 3 | OK |
| 28 | assembly, snug | Ø6 washer bearing on the clamp hole's perimeter ring | bearing | 5.44 | 25.0 | 4.59 | 3 | OK |

**Lowest SF 4.19 (required 3), at row 27.**

Advisory:

| Case | Section | SF |
|---|---|---|
| assembly, "firm" 0.1 N·m (250 N) | washer pull-through, as printed | 2.09: keep "snug" |
| shove / drop, window rails alone, servo case ignored (Kt 2.5, solid) | rails | 1.31 / 1.56 (see Assumptions) |
| drop with friction in any direction (beyond the spec) | tab screw pull-out / horn clamp / torsion | 2.45 / 2.36 / 3.07 |
| any combination of stalled servos (beyond the spec) | tab screws / clamp / torsion | 3.55 / 3.72 / 4.77 |
| walking at the change-set mass, 906 g | clamp / worst section / tab screws | 21.05 / 27.18 / 18.15 |

## Proof test

**Spec §8's test is the right kind; three changes bring it to the loads.**
1. **Set-up:** as written. The femur sits on its horn on an MG90S clamped in a vice, clamp screw snug (0.05 N·m),
   with the tibia servo (reversed) and the tibia fitted. The femur is level, the tibia hangs straight down, and a stop
   bears on the femur's rear end.
2. **Load: 1.5 kg** (was 1 kg) at the foot tip for **1 min**.
   - This is 2 × the walking foot load (7.7 N at 906 g), the top of the skill's 1.5–2 ×. The femur root then sees
     about 660 N·mm in plane.
   - Then **turn the servo over in the vice, move the stop to the other side, and repeat.** A hanging weight pulls the
     foot opposite to the ground's push, and the horn clamp tips on a different side each way.
3. **Side push: 6 N** (was 3 N) at the foot tip, each way, for 10 s: 1.5 × the 4.0 N a coxa stall puts there. This
   covers the stall rows (clamp 4.50, tab screws 4.73) and the tab screws' pull-out direction.

Pass, as written:
- no cracks or whitening at the pocket, the window corners or the pilots;
- no gap over 0.2 mm (feeler gauge) between the femur and the horn;
- after unloading, the knee returns to within 0.3 mm of where it started.

## Servo torques (system context)

At 840 g with the CG margin, static over the 30/40 mm gaits: femur 94 N·mm (43 % of stall), knee 107 N·mm (50 %).
×2 walking takes the knee to stall at a 40 mm stride. Walk at 30 mm, as the assembly plan chose, and watch the case
temperatures.

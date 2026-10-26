VERDICT: NEEDS_TEST

# Strength check: 20261026-hexapod-tibia (×6), round 3

Independent strength-analyst · 2026-10-26 · `python3 jobs/20261026-hexapod-tibia/strength_calc.py` (about 30 s; needs
build123d, trimesh and scipy, like `cad_checks.py`)

**NEEDS_TEST: placeholder allowables only. No change to the geometry is needed.**

- **Lowest SF 3.45: the plate over the horn-arm pocket at x 13**, where the arm-screw hole is (Kt 2), as printed.
  - The case is a coxa servo stall: 216 N·mm puts 4.0 N sideways at the foot.
  - That bends the tibia out of its plane over 57 mm.
- **Next lowest:** 4.12 (washer pull-through at the snug preload), 4.59 (washer bearing), 4.90 (horn clamp under a
  stall), 5.15 (the 3 N shove).
- **Drop rows:** 6.78 or more.

The geometry is unchanged in round 3, so the rebuild is identical. What changed around the tibia:

- **The tucked stance.** It turns the foot load 18.7° off the tibia's axis, so 0.32 of the vertical foot force now
  bends the tibia in its plane. The knee servo still caps that moment at the knee: 216 N·mm at stall, 432 N·mm
  back-driven.
- **The foot is now 54 mm from the coxa axis (77 before).** A coxa stall therefore pushes the foot sideways harder:
  216/54.4 = 4.0 N, where round 2 had 2.8 N. That is why the stall row is now the lowest.

## What changed since strength round 1

- **Clamp screw snug ≈ 0.05 N·m** (round 1's condition): in spec §2 and BUILD_GUIDE §3. Rows 16–17.
- **Proof test** (round 1's): in spec §8. One change needed (below).
- **Geometry:** unchanged. Its back face must stay flat: the femur's clamp head is the nearest thing proud, and only
  the tibia folded back past the femur axis reaches it (brief).

## Load cases

The same block as all five round-3 checks (details in the coxa's `strength.md`):
- **Robot mass 840 g:** 334 g printed + 506 g bought; 906 g with every round-3 change.
- **Lone-leg share up to 0.435.**
- **Sustained 3.58 N**, walking ×2 = 7.16 N, every planted foot of the 30/40 mm IK gaits.
- **Foot friction** µ 0.5, servos ≤ stall.
- **Shove** 3 N.
- **Servo stalls** one at a time (stance: 9.6 N vertical, 4.0 N tangential, 3.1 N radial, on top of 3.58 N up).
- **20 cm drop:** 19.2 N up at the 2 × stall back-drive cap, radial friction.
- **Assembly:** clamp screw snug, 125 N.
- Temperature: OK.

In the tibia's frame T the foot is at (70, 0, 3.5), on the tibia's mid-plane. World up in T is (−0.947, −0.321, 0).

## Assumptions

- **Printed:** 4 perimeters (1.67 mm), 1.0 mm skins, 50 % gyroid core. The core counts at stiffness ρ² = 0.25 and
  strength ρ^1.5 = 0.35.
  - Sections are rastered from the built solid; areas match build123d's within 0.6 %.
  - As printed, the second moments are 0.75–0.84 × solid.
- **Bending:** on the composite section. Kt 1.5 over the hub, 2 at the arm-screw hole (x 13).
- **Buckling:** fixed-free (K 2) on the as-printed foot-end second moment, 241 mm⁴.
- **Horn clamp:** pivot on the hub edge (r 3.6). The Ø6 washer's plug is 82 mm² as printed (515 N).
- **Foot-tip contact on a hard floor:** advisory local flattening (Hertz). A TPU sock spreads it.

## Allowables and sources

Placeholders (no rows in `library/materials.csv`, no datasheet):
- along / across the layers: 25 / 12.5 MPa;
- in-plane / interlayer shear: 12.5 / 6.25 MPa;
- bearing: 25 MPa;
- infill core: ρ^1.5 × these;
- E: 1.8 GPa.

NEEDS_TEST is the best possible verdict.

## Results (as specified, as printed)

| # | Case | Section | Dir | Stress | Allow. | SF | Req. | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | knee stall 216 N·mm | horn arm on the pocket wall | XY | 1.59 | 25.0 | 15.74 | 3 | OK |
| 2 | sustained 3.58 N | horn clamp: Ø6 washer pull-through | Z shear | 0.02 | 6.25 | 345 | 4 | OK |
| 3 | walking 7.16 N | horn clamp | Z shear | 0.04 | 6.25 | 173 | 4 | OK |
| 4 | foot friction | horn clamp | Z shear | 0.46 | 6.25 | 13.52 | 4 | OK |
| 5 | shove | horn clamp | Z shear | 0.76 | 6.25 | 8.20 | 3 | OK |
| 6 | stall | horn clamp | Z shear | 1.28 | 6.25 | 4.90 | 3 | OK |
| 7 | drop 19.2 N | horn clamp | Z shear | 0.10 | 6.25 | 64.19 | 3 | OK |
| 8 | sustained | worst section x 13 (arm pocket, arm-screw hole, Kt 2) | XY | 0.86 | 25.0 | 29.15 | 4 | OK |
| 9 | walking | x 13 | XY | 1.71 | 25.0 | 14.58 | 4 | OK |
| 10 | foot friction | x 13 | XY | 3.27 | 25.0 | 7.65 | 4 | OK |
| 11 | shove | x 13 | XY | 4.85 | 25.0 | 5.15 | 3 | OK |
| 12 | stall | x 13 | XY | 7.24 | 25.0 | **3.45** | 3 | OK |
| 13 | drop | x 13 | XY | 3.69 | 25.0 | 6.78 | 3 | OK |
| 14 | walking | buckling: P_cr 218 N against 6.7 N | XY | 0.77 | 25.0 | 32.41 | 4 | OK |
| 15 | drop | buckling: P_cr 218 N against 18.2 N | XY | 2.09 | 25.0 | 11.96 | 3 | OK |
| 16 | assembly, snug 125 N | Ø6 washer pull-through (as printed) | Z shear | 1.52 | 6.25 | 4.12 | 3 | OK |
| 17 | assembly, snug | Ø6 washer bearing on the clamp hole's perimeter ring | bearing | 5.44 | 25.0 | 4.59 | 3 | OK |

**Lowest SF 3.45 (required 3), at row 12.**

Advisory:

| Case | Section | SF |
|---|---|---|
| assembly, "firm" 0.1 N·m | washer pull-through | 2.06: keep "snug" |
| walking / drop, hard floor | foot-tip contact (Hertz, local flattening) | 1.89 / 1.15: the TPU sock |
| any combination of stalled servos (beyond the spec) | x 13 | 2.90 |
| drop with friction in any direction (beyond the spec) | x 13 | 1.87 |
| walking at the change-set mass, 906 g | x 13 / clamp | 13.52 / 160 |

**The tibia is weakest out of its own plane.** In a tilted landing, a sideways foot load near the coxa servo's
back-drive (7.9 N) would load x 13 to SF 1.9. The tilted drop test (body-bottom spec §8) settles it. If x 13 cracks
there, a thicker hub (7 → 9 mm over x 0–20) is the fix to check.

## Proof test

**Spec §8's test matches the verdict except for the side push.**

1. **Set-up:** as written. The tibia sits on its horn on an MG90S clamped in a vice, clamp screw snug (0.05 N·m),
   tibia horizontal, with a stop on the far side of the hub.
2. **Load:** **1 kg** at the foot tip for **1 min**, as written. That is 687 N·mm in plane at the hub: 1.6 × the most
   the knee servo can put through the tibia when back-driven.
3. **Side push: 6 N** (was 3 N) at the tip, each way, for 10 s.
   - That is 1.5 × the 4.0 N a coxa stall puts on the foot, the governing row 12.
   - At 6 N, x 13 sits at SF 3.35 against the placeholder allowable (7.46 MPa as printed). The 1 kg hang puts x 13
     at 5.10. A real proof, not a destructive one.

Pass, as written:
- no cracks or whitening round the pocket or the arm-screw hole;
- no gap over 0.2 mm (feeler gauge) between the tibia and the horn;
- after unloading, the tip returns within 0.5 mm.

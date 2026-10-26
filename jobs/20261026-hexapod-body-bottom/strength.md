VERDICT: FAIL

# Strength check: 20261026-hexapod-body-bottom, round 3

Independent strength-analyst · 2026-10-26 · `python3 jobs/20261026-hexapod-body-bottom/strength_calc.py` (about 2 min;
needs build123d, trimesh and scipy, like `cad_checks.py`)

**FAIL. 4 of 27 rows fail. The lowest SF is 2.03, at the strip outside each coxa window's outboard end, in the 20 cm
drop.** The spec (§4) asked for the reversed mount to be re-checked: its load path is new in round 3, and it doesn't
pass.

1. **The strip outside each coxa window's outboard end.**
   - The tabs now sit on the plate's top face, so the outboard M2 screw pulls the strip **up**, through its own
     clearance hole.
   - In the drop that is 51 N. The section through the hole is 4.5 mm net of the 7.3 mm strip.
   - **Drop: SF 2.03 at the hole, 2.27 at the window's corners.** Walking passes (5.58 / 6.24).
   - Two things made it worse than round 1's T_BODY 6 check (3.23):
     - Round 1 had the tab bearing on the strip, with no hole in the section.
     - The tucked stance reaches the drop cap with no inward friction, so the uplift rose from 45 to 51 N.
   - It fails under every reasonable model: 2.68 with a shorter span, 2.15 with solid sections. So the geometry has
     to change.
2. **Tab-screw washer bearing at assembly.** Each M2 head bears on the plate's underside through an M2 washer,
   14.2 mm² (the hole is slotted).
   - Snug, 0.05 N·m ≈ 125 N: 8.83 MPa, **SF 2.83**.
   - BUILD_GUIDE §3's "tighten to a firm stop", about 0.1 N·m: **SF 1.42**.
3. **Columns, robot lifted by the deck and tipped 90°.** **SF 2.29** as printed (2.85 solid).
   - The robot below the deck is now 748 g; round 2 had 578 g (+30 %).
   - Round 1's 3.69 used the same model at 578 g with solid sections.

**Everything else passes.** Washer pull-through 6.23 in the drop; screw bearing and ligament ≥ 34; plate mid-span
≥ 7.03; column tension 65; buckling 143; deck-screw pull-out 35.

## Required changes, checked as a set (at 906 g, with the coxa's change)

1. **Deepen the strip: `MARGIN` 4 → 8** (`model.py`). The strip outside each window goes from 7.25 to 11.25 mm deep.
   - Drop: **3.37** at the hole, **3.39** at the corners.
   - Walking: 8.60 / 8.65.
   - The plate gains 10.6 g printed.
   - `MARGIN` 7 gives only 3.04 / 3.10, too close. `MARGIN` 6 fails (2.68).
   - A local outboard extension that gives the same 11.25 mm strip at each window's outboard end is equivalent.
   - The plate's outline moves 4 mm out all round, so re-run `assembly_check.py`. By my estimate the femur at +90°
     (C x ≥ 22.5) still clears the new edge (u 17.4) by about 5 mm.
2. **Tab screws snug, ≤ 0.045 N·m** (≈ 110 N): washer bearing **3.22**.
   - Put this in BUILD_GUIDE §3 step 5 and spec §2, in place of "tighten to a firm stop".
   - Use **nylon-insert (Nyloc) M2 nuts**, so the nuts hold without preload. PETG creeps (fdm-design-rules), so
     preload is not counted on for strength anyway.
   - A larger washer doesn't fit the outboard screw. Its Ø5 washer already reaches the servo's gear boss (r 5.9) and
     the window's end.
3. **Columns Ø8 → Ø10** (`COLUMN_D`; r1.5 root fillets kept): **3.68**. Ø9 gives only 2.84.
   - Re-check the LiPo passage between the column fillet feet: 37 mm against the 35 mm pack, 1 mm each side.
   - Re-check the corner coxa servos' inner tab nuts. By my estimate they keep about 2.4 / 1.2 mm to the column and
     its fillet foot (the assembly plan has 3.4 / 2.2 at Ø8).
   - Sensitivity: if the deck's clamp on the column tops (one M3 each) is counted, the root moment is about 0.7 × the
     cantilever's and Ø8 gives 3.28. I don't count it, because the M3 joint's preload is not counted on in PETG.

With these three changes every row passes; the lowest is the strip in the drop, 3.37.

## What changed since strength round 1

| Round-1 required change | Round 3 | |
|---|---|---|
| T_BODY 4 → 6 | `hex_frame.T_BODY` 6 | made |
| M2 × 12 machine screws + nuts in Ø2.4 CAD clearance holes | made, but with the servo **reversed** (B1 option 2): head + Ø5 washer under the plate, nut on the tab inside the body | load path re-checked here (rows 1–19) |
| Proof test into spec §8 | in spec §8 | see "Proof test" |

Round 3 also moved the middle mounts to y ±56 and the columns to (±36, ±25), and added six tie slots.
- Every mount's outboard edge is still 7.25 mm past its window: probed at all six mounts.
- The tie slots sit beside the windows (S0 u 2.3–5.7, v −15…−17), about 9 mm from the strip's corner support. They
  are not in a checked section.

## Load cases

The same block as the coxa's `strength.md`, rebuilt by `strength_calc.py`:
- **Robot mass 840 g:** 334 g printed (layer model, calibrated on the four round-2 slices) + 506 g bought (itemised
  from BUILD_GUIDE §1). 906 g with every round-3 change.
- **Lone-leg share up to 0.435** (CG anywhere within ±3 mm).
- **Sustained 3.58 N up**, walking ×2 = 7.16 N, every planted foot of the 30/40 mm IK gaits.
- **Foot friction:** µ 0.5 × 3.58 N in any direction, servos ≤ stall.
- **Shove:** 3 N with 0 … 3.58 N up.
- **Servo stalls**, one at a time.
- **20 cm drop:** 19.2 N up per foot at the servo back-drive cap (2 × stall), with radial friction.
- **Plate mid-span drop:** body deceleration 6 × 19.2 / 8.24 N = **14.0 g** on 6 feet, 7.0 g on 3.
- **Handling:** robot lifted by the deck, ×2.
- **Assembly:** tab screws snug, 0.05 N·m ≈ 125 N (F = T / 0.2d).
- Service temperature 40 °C against PETG's ≈ 70 °C: OK.

**The mount (reversed).** In the coxa servo's frame S0 (fixed to the plate):
- **Pitch.** The foot force's moment about the inboard screw line lifts the outboard end. The outboard screw carries
  it in tension, pivoting conservatively on the other screw, 27.8 mm away. At the stance in the drop:
  19.2 N × 73.8 mm / 27.8 = **51 N**.
- **Roll** about the screw line goes to the tab edges, 6.1 mm off, and adds to the screw tension. It is a local couple
  on the strip, so it does not bend it.
- **Strip.** The strip outside the window is a fixed-fixed beam over the window width + one plate thickness each side
  (24.8 mm), the predecessor's model, loaded at mid-span by the uplift. Two sections are taken from the solid:
  - **at the hole:** 4.54 mm of material, I 76.6 mm⁴ as printed (81.1 solid), Kt 2;
  - **at the window's corners:** 7.29 mm, I 107.1 mm⁴ (130.5 solid), Kt 2.5, sharp corners.

## Assumptions

- **Printed construction:** 3 perimeters (band 1.26 mm), 1.0 mm top and bottom skins, 25 % gyroid core. The core is a
  cellular solid: stiffness ρ² = 0.06, strength ρ^1.5 = 0.13 (rover-wheel review).
  - Each layer is rasterised from the built solid.
  - Around each tab-screw hole, the hole's perimeter ring covers 85 % of the washer's radius, so the washer bears
    on solid material.
- **Section properties** come from the build123d solid. Rastered areas agree with build123d's exact sections within
  0.05 %, except the strip through the slotted hole: +1.08 %, because its 1.1 mm ligament is the hardest to raster.
  A 1 % excess can't move the `MARGIN` 8 result (3.37) below 3.
- **No bolt preload is counted for strength.** The servo case gets no credit in its window (0.1–0.2 mm clearance).
- **Columns:** cantilevers from the plate when the robot hangs from the deck on its side; deck joint taken as a pin.
- **Plate mid-span:** a point load at the centre on the strap-slot chord (132.8 mm net), Kt 2.5. The load is what
  rests on the plate: deck group, LiPo, UBEC and half the plate, 223 g.
- **Drop cap:** 2 × stall back-drive, an assumption (spec, DR05). The drop test on carpet settles it.

## Allowables and sources

`library/materials.csv` has no rows and `inputs/` has no datasheet, so these are **placeholders** and NEEDS_TEST is
the best possible verdict.

| Quantity | Value (MPa) | Source |
|---|---|---|
| Along layers / across layers | 25 / 12.5 | placeholder, PETG |
| Shear, in-plane / interlayer | 12.5 / 6.25 | 0.5 × normal |
| Bearing | 25 | in-plane value |
| Infill core | ρ^1.5 × the above (0.13 at 25 %) | Gibson–Ashby |

## Results: the design as specified (as printed)

| # | Case | Section | Dir | Stress | Allow. | SF | Req. | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | sustained 3.58 N | strip at the outboard screw hole (net 4.5 of 7.3 mm, Kt 2) | XY | 2.24 | 25.0 | 11.16 | 4 | OK |
| 2 | sustained | strip at the window's corners (7.3 mm, Kt 2.5) | XY | 2.00 | 25.0 | 12.49 | 4 | OK |
| 3 | walking 7.16 N | strip at the hole | XY | 4.48 | 25.0 | 5.58 | 4 | OK |
| 4 | walking | strip at the corners | XY | 4.00 | 25.0 | 6.24 | 4 | OK |
| 5 | foot friction | strip at the hole | XY | 3.80 | 25.0 | 6.59 | 4 | OK |
| 6 | foot friction | strip at the corners | XY | 3.39 | 25.0 | 7.37 | 4 | OK |
| 7 | shove | strip at the hole | XY | 5.16 | 25.0 | 4.85 | 3 | OK |
| 8 | shove | strip at the corners | XY | 4.61 | 25.0 | 5.43 | 3 | OK |
| 9 | stall | strip at the hole | XY | 6.02 | 25.0 | 4.15 | 3 | OK |
| 10 | stall | strip at the corners | XY | 5.38 | 25.0 | 4.65 | 3 | OK |
| **11** | **drop 19.2 N** | **strip at the hole (uplift 51 N)** | **XY** | **12.32** | **25.0** | **2.03** | **3** | **FAIL** |
| **12** | **drop** | **strip at the corners** | **XY** | **11.01** | **25.0** | **2.27** | **3** | **FAIL** |
| 13 | walking | Ø5 washer pulled through the plate by the outboard screw | Z shear | 0.44 | 6.25 | 14.34 | 4 | OK |
| 14 | shove | washer pull-through | Z shear | 0.59 | 6.25 | 10.67 | 3 | OK |
| 15 | drop | washer pull-through | Z shear | 1.00 | 6.25 | 6.23 | 3 | OK |
| 16 | drop | screw bearing in the clearance hole | XY | 0.30 | 25.0 | 82.63 | 3 | OK |
| 17 | drop | window → hole ligament 1.1 mm CAD, whole radial force on one screw | XY shear | 0.36 | 12.5 | 34.61 | 3 | OK |
| 18 | coxa stall 216 N·mm | screws bearing in their holes | XY | 0.65 | 25.0 | 38.61 | 3 | OK |
| **19** | **assembly, snug 125 N** | **Ø5 washer bearing on the plate underside (14.2 mm²)** | **bearing** | **8.83** | **25.0** | **2.83** | **3** | **FAIL** |
| 20 | walking ×2, tripod span | plate mid-span through a strap slot (Kt 2.5) | XY | 0.42 | 25.0 | 59.43 | 4 | OK |
| 21 | drop on 3 feet, 7.0 g | plate mid-span | XY | 1.47 | 25.0 | 16.95 | 3 | OK |
| 22 | drop on 6 feet, 14.0 g | plate mid-span | XY | 3.55 | 25.0 | 7.03 | 3 | OK |
| **23** | **handling, lifted by the deck and tipped 90°** | **column root above the r1.5 fillet (3.67 N at 40 mm, Kt 1.5)** | **Z** | **5.45** | **12.5** | **2.29** | **3** | **FAIL** |
| 24 | handling | column tension | Z | 0.19 | 12.5 | 65.28 | 3 | OK |
| 25 | drop, landing tilted 20° | column root (deck 91 g at 14.0 g) | Z | 1.59 | 12.5 | 7.85 | 3 | OK |
| 26 | drop | column buckling, K 2: P_cr 449 N against 3.1 N | XY | 0.17 | 25.0 | 143.07 | 3 | OK |
| 27 | handling | M3 × 8 deck screw pull-out from a column | Z shear | 0.18 | 6.25 | 34.77 | 3 | OK |

**Lowest SF 2.03 (required 3) at row 11.**

Advisory:

| Case | Section | SF |
|---|---|---|
| assembly at BUILD_GUIDE's "firm stop" (~0.1 N·m, 250 N) | washer bearing | 1.42 |
| drop, strip span window + one thickness (18.8 mm) | strip at the hole | 2.68 |
| drop, solid sections | strip at the hole | 2.15 |
| drop with friction in any direction (beyond the spec) | strip at the hole | 1.89 |
| any combination of stalled servos (beyond the spec) | strip at the hole | 3.53 |
| handling, deck restraining the column tops (0.7 × cantilever) | column root | 3.28 |

Change set at 906 g: the `MARGIN` sweep shows 6 → 2.68 / 2.82, 7 → 3.04 / 3.10, 8 → **3.37 / 3.39** (drop: hole /
corners). Tab screws at 0.045 N·m: **3.22**. Columns Ø9 → 2.84, Ø10 → **3.68**.

## Proof test

Once the changes are made, the verdict becomes NEEDS_TEST. **Spec §8's test covers the strip but not the columns.** It
should read:

1. **Standing load:** as written (six feet, +500 g on the deck, 1 min). It is harmless, but it loads the strip only to
   about 0.3 × walking, so it doesn't prove the strip.
2. **Handling (new):** lift the robot by the deck and turn it on its side (deck vertical). Hold **1 min** with
   **0.8 kg** hung from the bottom plate's lower edge: about 2 × the static load on the columns.
3. **Drop:** as written. 3 × 20 cm landing flat on 6 feet, then 3 × 20 cm tilted onto one side's 3 feet, onto carpet.
   This is the strip's governing case (51 N uplift per mount).
   - Run it on **spare coxa servos**, or only after the leg test in the assembly spec §8 has passed (DR05 SYS-6).
   - Mark each nut with paint first.

Pass:
- no cracks or whitening at the coxa windows, especially the strip at each outboard screw and the window corners;
- none at the column roots;
- no servo tab lifting off the plate (0.2 mm feeler gauge);
- no nut turned (paint marks).

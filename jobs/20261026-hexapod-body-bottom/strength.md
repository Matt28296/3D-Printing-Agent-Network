VERDICT: NEEDS_TEST

# Strength check: 20261026-hexapod-body-bottom, round 4

Independent strength-analyst · 2026-10-26 · `python3 jobs/20261026-hexapod-body-bottom/strength_calc.py` (about 2 min;
needs build123d, trimesh and scipy, like `cad_checks.py`: CAD venv `/home/claude/.venv-cad`)

**Every row passes. The lowest SF is 3.09 (required 3).** It is the Ø5 washer under a tab screw's head bearing on the
plate's underside, with the screw driven to the spec's 0.045 N·m cap.

Next lowest:
- **the strip outside each window's outboard end, in the drop: 3.37** at the screw hole, 3.39 at the corners (round 3,
  at `MARGIN` 4: 2.03 / 2.27);
- **the Ø10 columns, robot lifted by the deck and tipped 90°: 3.67** (round 3, Ø8: 2.29).

Two things to note:
- **The verdict is NEEDS_TEST, not PASS, only because the allowables are placeholders.** `library/materials.csv` has
  no PETG row.
- **Spec §8's proof test matches this check and stays as written.**

## Round 3's required changes: all made

| # | Round 3 required | Round 4 | Checked |
|---|---|---|---|
| 1 | `MARGIN` 4 → 8: the strip outside each window 7.25 → 11.25 mm deep | `MARGIN` 8. The plate is 166.1 × 146.8 mm. The strip, probed on the built plate at all six mounts in 0.05 mm steps, is 11.25–11.30 mm (CAD 11.3) | rows 1–12: drop 3.37 / 3.39, walking 8.58 / 8.63, as round 3 predicted |
| 2 | Tab screws snug, ≤ 0.045 N·m, with Nyloc nuts; spec §2 and BUILD_GUIDE §3 step 5 instead of "a firm stop" | Spec §2, BUILD_GUIDE §1 and §3 step 5: M2 × 14 with a Ø5 washer under the head, then a Ø5 washer and an M2 Nyloc (DIN 985) on the tab. Driven snug, at most 0.045 N·m above the Nyloc's running torque, never to a firm stop. The thread runs 1.9 mm past a 3.0 mm Nyloc | row 19: **3.09** (round 3 said 3.22; see below) |
| 3 | Columns Ø8 → Ø10, r1.5 root fillets kept | `COLUMN_D` 10, `COLUMN_FILLET` 1.5, at (±36, ±25) | row 23: 3.67 |
| — | Round 3's re-checks: the LiPo passage, the corner servos' inner nuts, `assembly_check.py` | 37.0 mm between the fillet feet for the 35 mm pack; tab hardware 2.7 mm from the column, the tab 1.2 mm from the fillet foot; assembly check clean | DFM round 4, assembly plan |
| 4 | Proof test: handling hold and the drop on spare servos with paint-marked nuts | spec §8 | see "Proof test" |

**Row 19 is 3.09, not round 3's 3.22.** Still ≥ 3. Two exact corrections, which compound:
- Round 3 took 110 N for 0.045 N·m. Its own formula, F = T / (0.2 d), gives **112.5 N**.
- At its tab hole the screw sits at the window end of its slot, because the slot runs 0.4 mm outward. So the Ø5
  washer's rim reaches **0.2 mm past the window's end** (DFM round 3 noted it). That 0.26 mm² segment bears on
  nothing: **13.89 mm²** instead of 14.15.

## Load cases

The same block as the coxa's round-4 `strength.md`. `strength_calc.py` rebuilds it from `hex_frame.py`, hobby_parts,
the five `model.py` and each `print_requirements.json`.

- **Robot mass: 907 g (8.90 N).**
  - 400 g printed, through the layer model. This plate is 96.2 g of it (167.7 g solid).
  - 507 g bought: round 3's itemised list, plus 1.3 g for the round-4 tab hardware (12 M2 × 14 and Nyloc nuts).
  - The plan's 906 g is round 3's estimate of the same robot.
- **Lone-leg share up to 0.435** (CG anywhere within ±3 mm).
- **Sustained 3.87 N up**; walking × 2 = 7.74 N. Every planted foot of the 30/40 mm IK gaits.
- **Foot friction:** µ 0.5 × 3.87 N in any direction, servos ≤ stall.
- **Shove:** 3 N with 0 … 3.87 N up.
- **Servo stalls:** one at a time.
- **20 cm drop:** 19.2 N up per foot at the servo back-drive cap (2 × stall), with radial friction.
- **Plate mid-span drop:** body deceleration 6 × 19.2 / 8.90 N = **13.0 g** on 6 feet, 6.5 g on 3.
- **Handling:** robot lifted by the deck, × 2, upright and tipped 90°.
- **Assembly:** tab screws snug at the 0.045 N·m cap: 112.5 N.
- Service temperature 40 °C against PETG's ≈ 70 °C: OK.

**The mount (reversed: tabs on the plate's top face).** In the coxa servo's frame S0, which is fixed to the plate:
- **Pitch.** The foot force's moment about the inboard screw lifts the outboard end. The outboard screw carries it in
  tension, pivoting conservatively on the other screw, 27.8 mm away. That is **51 N** at the stance in the drop.
- **Roll** about the screw line goes to the tab edges, 6.1 mm off, and adds to the screw tension. It is a local couple
  on the strip, so it does not bend the strip.
- **Strip.** A fixed-fixed beam over the window width + one plate thickness each side (24.8 mm), loaded at mid-span by
  the uplift. This is rounds 1–3's model. Two sections are taken from the built solid:
  - **at the hole:** 8.44 mm of material of the 11.25, I 127.1 mm⁴ as printed (151.3 solid), Kt 2;
  - **at the window's corners:** 11.33 mm, I 159.9 mm⁴ (203.3 solid), Kt 2.5, sharp corners.

## Assumptions

- **Printed construction:** 3 perimeters (band 1.26 mm), 1.0 mm top and bottom skins, 25 % gyroid core.
  - The core is a cellular solid: stiffness ρ² = 0.06, strength ρ^1.5 = 0.13 (rover-wheel review, round 3).
  - Each layer is rasterised from the built solid.
  - Around each tab-screw hole, the hole's perimeter ring covers 81 % of the washer's radius.
- **Where the uplift enters.** The outboard screw is 2.3 mm from the window's end and 9.0 mm from the outline, off
  the strip's centre. The beam model spreads the load over the whole strip. I accept that, for these reasons:
  - **At the window's corners** it holds. A 45° spread from the washer (u 5.9–10.9) over the 6.4 mm to the corner
    line reaches u 6.1–17.3, the whole strip.
  - **At the hole**, under the load, the bending is more concentrated near the screw than a beam assumes. Against
    that, the model's span (24.8 mm) gives a mid-span moment of 3.1 F·mm. That is what a strip only simply supported
    across the window's 12.8 mm would carry (3.2 F). The strip's ends are continuous 6 mm plate, so the true value is
    nearer the fixed-end 1.6 F. That factor of about 2 is what covers the concentration.
  - **Torsion** from the load's 3.33 mm offset doesn't govern. Combined with bending at the middle of the faces it
    gives SF 6.74, and it is zero at the section's corners, where Kt acts.
  - I can't bound the hole section more tightly by hand, and no FEA toolchain (CalculiX) is installed. The drop test
    in spec §8 loads this section at its full design value.
- **No bolt preload is counted for strength.** The Nyloc holds the nut without preload (fdm-design-rules: PETG creeps).
  - Preload enters only the assembly row, which is short-term.
  - The joint is displacement-controlled, so creep relaxes the preload rather than adding to it.
- **Nut factor K 0.2** (dry steel, the round-3 basis).
  - With an oiled thread (K 0.15) the same 0.045 N·m gives 150 N and SF 2.31 (advisory).
  - So drive the nuts the way BUILD_GUIDE §3 step 5 says: until both washers just clamp, then stop. Don't drive them
    to a torque setting.
- **Columns:** each is a cantilever from the plate when the robot hangs from the deck on its side. The deck joint is
  taken as a pin; if the deck clamps the column tops, SF 5.24 (advisory).
- **Plate mid-span:** a point load at the centre on the strap-slot chord (138.0 mm net), Kt 2.5. The load is what
  rests on the plate: the deck group, the LiPo, the UBEC and half the plate, 229 g.
- **Drop cap:** 2 × stall back-drive, an assumption (spec, DR05). The drop test on carpet settles it.
- **The servo case gets no credit** in its window (0.1–0.2 mm clearance).

## Allowables and sources

`library/materials.csv` has no rows and `inputs/` has no datasheet. So these are the strength-checks
**placeholders**, and NEEDS_TEST is the best verdict possible.

| Quantity | Value (MPa) | Source |
|---|---|---|
| Along layers / across layers | 25 / 12.5 | placeholder, PETG |
| Shear, in-plane / interlayer | 12.5 / 6.25 | 0.5 × normal |
| Bearing | 25 | in-plane value |
| Infill core (25 % gyroid) | ρ^1.5 × the above: 0.13 | Gibson–Ashby |
| E | 1800 | placeholder |

## Results: the round-4 design as specified (as printed)

| # | Case | Section | Dir | Stress | Allow. | SF | Req. | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | sustained 3.87 N | strip at the outboard screw hole (net 8.4 of 11.3 mm, Kt 2) | XY | 1.46 | 25.0 | 17.16 | 4 | OK |
| 2 | sustained | strip at the window's corners (11.3 mm, Kt 2.5) | XY | 1.45 | 25.0 | 17.27 | 4 | OK |
| 3 | walking 7.74 N | strip at the hole | XY | 2.91 | 25.0 | 8.58 | 4 | OK |
| 4 | walking | strip at the corners | XY | 2.90 | 25.0 | 8.63 | 4 | OK |
| 5 | foot friction | strip at the hole | XY | 2.47 | 25.0 | 10.13 | 4 | OK |
| 6 | foot friction | strip at the corners | XY | 2.45 | 25.0 | 10.19 | 4 | OK |
| 7 | shove | strip at the hole | XY | 3.23 | 25.0 | 7.75 | 3 | OK |
| 8 | shove | strip at the corners | XY | 3.21 | 25.0 | 7.79 | 3 | OK |
| 9 | stall | strip at the hole | XY | 3.62 | 25.0 | 6.90 | 3 | OK |
| 10 | stall | strip at the corners | XY | 3.60 | 25.0 | 6.94 | 3 | OK |
| 11 | drop 19.2 N | strip at the hole (uplift 51 N) | XY | 7.41 | 25.0 | 3.37 | 3 | OK |
| 12 | drop | strip at the corners | XY | 7.37 | 25.0 | 3.39 | 3 | OK |
| 13 | walking | Ø5 washer pulled through the plate by the outboard screw | Z shear | 0.47 | 6.25 | 13.34 | 4 | OK |
| 14 | shove | washer pull-through | Z shear | 0.60 | 6.25 | 10.40 | 3 | OK |
| 15 | drop | washer pull-through | Z shear | 1.00 | 6.25 | 6.26 | 3 | OK |
| 16 | drop | screw bearing in the clearance hole | XY | 0.30 | 25.0 | 82.63 | 3 | OK |
| 17 | drop | window → hole ligament 1.1 mm CAD, whole radial force on one screw | XY shear | 0.36 | 12.5 | 34.61 | 3 | OK |
| 18 | coxa stall 216 N·mm | screws bearing in their holes | XY | 0.65 | 25.0 | 38.61 | 3 | OK |
| **19** | **assembly, 0.045 N·m cap (112.5 N)** | **Ø5 washer bearing on the plate underside (13.89 mm²)** | **bearing** | **8.10** | **25.0** | **3.09** | **3** | **OK** |
| 20 | walking × 2, tripod span | plate mid-span through a strap slot (Kt 2.5) | XY | 0.44 | 25.0 | 56.64 | 4 | OK |
| 21 | drop on 3 feet, 6.5 g | plate mid-span | XY | 1.43 | 25.0 | 17.46 | 3 | OK |
| 22 | drop on 6 feet, 13.0 g | plate mid-span | XY | 3.45 | 25.0 | 7.24 | 3 | OK |
| 23 | handling, lifted by the deck and tipped 90° | Ø10 column root above the r1.5 fillet (4.00 N at 40 mm, Kt 1.5) | Z | 3.41 | 12.5 | 3.67 | 3 | OK |
| 24 | handling | column tension | Z | 0.16 | 12.5 | 79.51 | 3 | OK |
| 25 | drop, landing tilted 20° | column root (deck 91 g at 13.0 g) | Z | 0.85 | 12.5 | 14.79 | 3 | OK |
| 26 | drop | column buckling, K 2: P_cr 978 N against 2.9 N | XY | 0.07 | 25.0 | 337.01 | 3 | OK |
| 27 | handling | M3 × 8 deck screw pull-out from a column | Z shear | 0.20 | 6.25 | 31.89 | 3 | OK |

**Lowest SF 3.09 (required 3), at row 19.** The lowest structural row is the strip in the drop, 3.37 (row 11).

## Advisory (not in the verdict)

| Case | Section | SF |
|---|---|---|
| Tab screw driven to a "firm stop", about 0.1 N·m (250 N), which BUILD_GUIDE now forbids | washer bearing | 1.39 |
| 0.045 N·m with an oiled thread (K 0.15, 150 N) | washer bearing | 2.31 |
| Drop with friction in any direction (beyond the spec) | strip at the hole | 3.15 |
| Any combination of stalled servos (beyond the spec) | strip at the hole | 5.87 |
| Drop, strip span 18.8 mm (window + one thickness) | strip at the hole | 4.45 |
| Drop, solid sections | strip at the hole | 4.02 |
| Drop, bending + torsion from the uplift's 3.33 mm offset (Tresca, middle of the faces) | strip at the corners | 6.74 |
| Handling, deck restraining the column tops (0.7 × the cantilever moment) | column root | 5.24 |

**The first two rows say how to tighten.** The 0.045 N·m figure is a cap, not a target. Drive each nut by feel, as
BUILD_GUIDE §3 step 5 says: until both washers just clamp, then stop.

## Proof test

The verdict is NEEDS_TEST (placeholder allowables). **Spec §8's proof test matches this check and needs no change.**

1. **Standing load:** six feet, +500 g on the deck, 1 min. It is harmless, but it loads the strip only to about
   0.3 × walking, so it doesn't prove the strip.
2. **Handling:** lift the robot by the deck, turn it on its side, and hang **0.8 kg** from the bottom plate's lower
   edge for **1 min**.
   - With the 816 g below the deck, that is 1.98 × the static load on the columns, the handling row's × 2.
   - Column roots at the proof load: SF 3.71 (placeholder allowables).
3. **Drop:** 3 × 20 cm flat on 6 feet, then 3 × 20 cm tilted onto one side's 3 feet, onto carpet.
   - This is the strip's governing case: 51 N uplift per mount, 2.5 × the walking load there. It also loads each
     outboard screw's washer.
   - Run it on spare coxa servos, or only after the assembly spec §8 leg test has passed (DR05 SYS-6).
   - Mark each nut with paint first.

Pass, as spec §8 states:
- no cracks or whitening at the coxa windows, especially the strip at each outboard screw and the window corners;
- none at the column roots;
- no servo tab lifting off the plate (0.2 mm feeler gauge);
- no nut turned (paint marks).

When you inspect "the strip at each outboard screw", include the underside round its washer: a ring pressed into the
plate there means the screw was overtightened (row 19).

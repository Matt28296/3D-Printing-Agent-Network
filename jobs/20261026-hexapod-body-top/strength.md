VERDICT: NEEDS_TEST

# Strength check: 20261026-hexapod-body-top, round 3

Independent strength-analyst · 2026-10-26 · `python3 jobs/20261026-hexapod-body-top/strength_calc.py` (about 30 s;
needs build123d, trimesh and scipy, like `cad_checks.py`)

**NEEDS_TEST: placeholder allowables only. No change to the geometry is needed.**

- **Lowest SF 3.27: the ESP32 seat's side rail** when a jumper is pulled sideways (10 N). This is unchanged from
  round 2.
- **Round 3 lowered one row.** In the one-end lift, the worst section is now at the **rear**: through the cable slots
  at x −46.5, beside the new Ø12 switch hole. There, 61.9 mm of the deck's 104 mm width is left. The row went from
  5.01 (front, 579 g below the deck) to **3.54** (748 g below the deck), and **3.25** at the change-set mass (815 g
  below the deck).
- **The six lead notches** (10 × 5, r1.5) sit at the long edges, outside every critical section. A lead pulled 10 N
  at a notch gives SF 5.00.
- Every other row is 4.77 or more.

## What changed since strength round 1

- **No geometry change was required.** The proof test was extended to the two lowest rows; it is in spec §8.
- **Round-3 changes:**
  - screw holes moved with the columns to (±36, ±25): the drop span between them is now 72 mm;
  - six lead notches with tie slots;
  - a Ø12 switch hole at (−50, 0).
  - The designer's estimate of "≈ 3.8" for the heavier robot's handling was right in kind. The lift by one end lands
    at 3.54, and the rear section beside the switch governs.

## Load cases

The same block as all five round-3 checks (details in the coxa's `strength.md`):
- **Robot mass 840 g**, 906 g with every round-3 change.
- **The deck group is 91 g:** deck 36.2, two PCA9685 18, ESP32 10, buck 2, switch 15, half the harness 10. The UBEC
  stands on the bottom plate.
- **Below the deck: 748 g**, 815 g at the change-set mass.

| Case | Load | Duration, SF |
|---|---|---|
| Handling: lifted by the long edges | the robot below the deck × 2 = 14.7 N, half per edge, cantilevered from the column line (27 mm) | 3 |
| Handling: lifted by one end | 14.7 N; sections scanned every 0.5 mm through both ends' cable slots (x ±44 … ±57), lever to the deck's end | 3 |
| USB plug | 10 N along x | 3 |
| Jumper pulled sideways / pushed on from below | 10 N / 20 N | 3 |
| Servo lead pulled sideways / board unplugged | 10 N / 15 N | 3 |
| Drop on 6 feet | deck group at 6 × 19.2 / 8.24 N = **14.0 g** (round 2: 17.2 g) | 3 |
| Sustained | deck group at 1 g | 4 |
| Lead pulled at a notch | 10 N | 3 |

## Assumptions

- **Printed:** 3 perimeters (1.26 mm), 1.0 mm top and bottom skins over a 1 mm core of 20 % gyroid. The core counts at
  stiffness ρ² = 0.04 and strength ρ^1.5 = 0.09.
  - On a 3 mm deck the as-printed section modulus is 0.94–0.97 × solid.
  - Sections come from the built solid, within 0.05 % of build123d's exact section areas (checked at x −46.5 and
    x 0).
  - The seat rails (2.5 mm wide) and the PCA9685 post walls (1.55 mm) are all perimeter, so they count as solid.
- **Kt** 2.5 at the cable-slot corners and the rail and post roots, as in round 1.
- **Deck screw heads:** M3 pan, Ø5.5 (assumed).

## Allowables and sources

Placeholders (no rows in `library/materials.csv`, no datasheet):
- along / across the layers: 25 / 12.5 MPa;
- in-plane / interlayer shear: 12.5 / 6.25 MPa;
- bearing: 25 MPa.

NEEDS_TEST is the best possible verdict.

## Results (as specified, as printed)

| # | Case | Section | Dir | Stress | Allow. | SF | Req. | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | lifted by the long edges, 14.7 N | deck at the column line y 25 (cable slots, Kt 2.5) | XY | 3.12 | 25.0 | 8.01 | 3 | OK |
| 2 | lifted by one end, 14.7 N | deck at x −46.5, rear cable slots beside the switch hole (Kt 2.5) | XY | 7.07 | 25.0 | 3.54 | 3 | OK |
| 3 | handling | screw-head plug shear, 3 mm deck | Z shear | 0.14 | 6.25 | 44.13 | 3 | OK |
| 4 | handling | screw-head bearing | XY | 0.54 | 25.0 | 46.25 | 3 | OK |
| 5 | USB plug 10 N | header strips on the window end face | XY | 0.80 | 25.0 | 31.25 | 3 | OK |
| 6 | jumper pulled sideways 10 N | seat side-rail root over half the board (Kt 2.5) | Z | 3.82 | 12.5 | **3.27** | 3 | OK |
| 7 | jumpers pushed on from below 20 N | zip-tie slot ligament | XY shear | 0.83 | 12.5 | 15.00 | 3 | OK |
| 8 | servo lead pulled sideways 10 N | PCA9685 post root (4 posts, Kt 2.5) | Z | 2.62 | 12.5 | 4.77 | 3 | OK |
| 9 | board unplugged 15 N | M2.5 pull-out (2 screws, 4.4 mm) | Z shear | 0.25 | 6.25 | 25.34 | 3 | OK |
| 10 | sustained, deck group at 1 g | deck between the columns through the ESP32 window (span 72, Kt 2.5) | XY | 0.22 | 25.0 | 113.55 | 4 | OK |
| 11 | drop on 6 feet, 14.0 g | same section | XY | 3.09 | 25.0 | 8.10 | 3 | OK |
| 12 | drop | screw-head bearing, 4 screws | XY | 0.23 | 25.0 | 108.22 | 3 | OK |
| 13 | lead pulled 10 N at a notch | ligament beside the notch (r1.5, Kt 1.5) | XY | 5.00 | 25.0 | 5.00 | 3 | OK |

**Lowest SF 3.27 (required 3), at row 6.**

Advisory:
- the round-2 section (front, x 46, no switch hole): 4.01;
- solid sections at the rear section: 3.64;
- **at the change-set mass (906 g): lifted by one end 3.25, by the long edges 7.36.**

## Proof test

**Spec §8's test matches the verdict, with one change: lift by the rear end, with weight added.**

1. **Lift by both long edges,** 5 times: as written.
2. **Lift by one end, changed.** Lift by the **rear (switch) end** of the deck only, so the robot hangs from that
   edge. Hold **1 min** with **0.8 kg** added to the bottom plate, for example a bag hung from the strap slots.
   - That is 2 × the static load below the deck: the design case.
   - As written ("lift it once by one end"), the test reaches only half the design load and doesn't name the weaker
     end.
   - Do it after the body-bottom's Ø10 columns are in: the columns bend in this test too.
3. **USB,** 5 times: as written.
4. **Side push on the ESP32: 2 kg (≈ 20 N, 2 × the jumper case),** each way for 10 s: as written. This proves the
   lowest row, row 6, at 2 ×.

Pass, as written:
- no cracks or whitening at the screw holes, the cable-slot corners, the lead notches, the PCA9685 post roots, the
  seat rails or the ledges; the switch hole is added to this list;
- the board stays on both ledges.

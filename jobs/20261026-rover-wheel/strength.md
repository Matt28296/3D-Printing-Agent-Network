VERDICT: NEEDS_TEST

# Strength check: 20261026-rover-wheel (round 3)

strength-analyst (independent) · 2026-10-26 · run with the CAD venv: `source /home/claude/.venv-cad/bin/activate`, then `python3 jobs/20261026-rover-wheel/strength_calc.py`

**Result: NEEDS_TEST.** The allowables are placeholders, so PASS is not possible.

- **Lowest SF: 12.96.** It is the hoop bending of the rim shell in the 5 cm drop, at 31.8 N per wheel.
- **Margins.** Every row is at SF 13 or more, and the drop rows hold up to a 21.6 cm drop.
- **Round-3 geometry.** The bed chamfers and the M3 × 50 class-12.9 bolt don't change the wheel's load path.
- **The bolt belongs to the chassis check and passes there.** Its SF is 2.66 at the drop and 1.73 at the 5 kg proof. Fully threaded **A2-70** bolts would not pass: 1.11 at the drop, and the proof test would bend them (0.72). Class 8.8 is the minimum.

## Round-2 findings: what round 3 did

| Round 2 | Round 3 | Result |
|---|---|---|
| Bolt grade (chassis-owned): A2-70 fails at the 5 cm corner | Class 12.9, fully threaded | ✓ SF 2.66 (advisory here; chassis row A6) |
| Bolt length: M3 × 50 if the bosses thicken | `BOSS_IN` 5.5 and M3 × 50 | ✓ Needs ≥ 49.5 mm. The tip is at \|y\| 77.5, with 2.0 mm of thread past the nyloc (`assembly_check.json`). |
| Proof via the chassis tests | Spec §8: chassis test 1 (5 kg at the rim centre) and test 3 (drops) | ✓ Matches (below) |

## Load cases

Shared rover block; the chassis report has the full table.

| Load | Value | Note | Duration |
|---|---|---|---|
| 5 cm drop | **31.8 N per wheel** | Mass 649 g, 5 mm stopping distance (spec §4). Flat landing: deep review S-15 shows that only the 4 road wheels touch a straight run, so each takes 127/4 = 31.8 N (round 2 had 15.9 N on 8 axles). This equals the corner value. An elastic estimate gives several times more; the drop test is the evidence. | short-term |
| Weight share | 1.9 N (0.3 W; the rear wheels carry 0.27 W each, S-18) | | sustained |
| Side drag | 3 N on a flange (S-15 pivot turn ≤ 1.43 N per track half) | | cyclic |
| Proof (chassis §8 test 1) | 5 kg = 49 N at the rim centre | | 1 min |

## Assumptions

**Construction**
- The wheel is printed at the `print_requirements` minima: 5 perimeters (2.25 mm) and 20 % gyroid.
- The rim is a shell of perimeters, continuous round the hoop (in-plane), on an infill foundation.

**Rim and infill model**
- The infill is treated as a cellular solid (Gibson–Ashby, an assumption): E ≈ E_s·ρ² = 72 MPa, crush allowable ≈ 25·ρ^1.5 = 2.24 MPa.
- The rim is an infinite beam on an elastic foundation under the link's line load over the 24.6 mm rim: M = q/(4β), p = qβ/2.

**Bore and flange**
- Bore: Ø3.7 CAD, about Ø3.5 printed, on the M3 threads, with bearing on half the projected area over the rim width.
- V-flange root under the side load: in-plane, 10 mm contact arc.

## Allowables and sources

**Allowables**
- No measured data, so the skill's placeholders apply: PETG 25 MPa in-plane, 12.5 MPa across layers, shear 0.5 × normal.
- **NEEDS_TEST is the best verdict possible.**

**Required SF**

| Load type | SF |
|---|---|
| Short-term | 3 |
| Cyclic or sustained | 4 |
| Steel, on yield | 1.5 |
| Proof | 1.0 |

**Temperature:** service is 40 °C against a softening point of about 70 °C.

## Results (`strength_calc.py` output)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | W1 5 cm drop 31.8 N (flat on 4 wheels or a corner): rim shell hoop bending | XY | 1.93 | 25.0 | 12.96 | 3.0 | OK |
| 2 | W1 5 cm drop 31.8 N (flat on 4 wheels or a corner): rim shell -> infill crush | infill 20% | 0.13 | 2.2 | 17.39 | 3.0 | OK |
| 3 | W1 5 cm drop 31.8 N (flat on 4 wheels or a corner): bore shell -> infill crush | infill 20% | 0.16 | 2.2 | 14.17 | 3.0 | OK |
| 4 | W1 5 cm drop 31.8 N (flat on 4 wheels or a corner): bore bearing on the M3 threads | XY | 0.86 | 25.0 | 28.98 | 3.0 | OK |
| 5 | W2 weight share 1.9 N sustained: rim shell hoop bending | XY | 0.12 | 25.0 | 215.99 | 4.0 | OK |
| 6 | W2 weight share 1.9 N sustained: rim shell -> infill crush | infill 20% | 0.01 | 2.2 | 289.79 | 4.0 | OK |
| 7 | W2 weight share 1.9 N sustained: bore shell -> infill crush | infill 20% | 0.01 | 2.2 | 236.16 | 4.0 | OK |
| 8 | W2 weight share 1.9 N sustained: bore bearing on the M3 threads | XY | 0.05 | 25.0 | 482.98 | 4.0 | OK |
| 9 | W3 V-flange root bending, side 3 N on the cone (10 mm contact arc) | XY | 0.20 | 25.0 | 126.76 | 4.0 | OK |
| 10 | W4 hub end-face bearing on the wall washer, side 3 N | XY | 0.04 | 25.0 | 564.90 | 4.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, fixes, proof loads, bought parts):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| proof 5 kg (49 N) at the rim centre (chassis §8 test 1): rim shell hoop bending | XY | 2.97 | 25.0 | 8.41 | 1.0 | OK |
| proof 5 kg (49 N) at the rim centre (chassis §8 test 1): rim shell -> infill crush | infill 20% | 0.20 | 2.2 | 11.28 | 1.0 | OK |
| proof 5 kg (49 N) at the rim centre (chassis §8 test 1): bore shell -> infill crush | infill 20% | 0.24 | 2.2 | 9.20 | 1.0 | OK |
| proof 5 kg (49 N) at the rim centre (chassis §8 test 1): bore bearing on the M3 threads | XY | 1.33 | 25.0 | 18.81 | 1.0 | OK |
| 5 cm drop, stiff landing (64 N): rim shell hoop bending | XY | 3.86 | 25.0 | 6.48 | 3.0 | OK |
| 5 cm drop, stiff landing (64 N): rim shell -> infill crush | infill 20% | 0.26 | 2.2 | 8.69 | 3.0 | OK |
| 5 cm drop, stiff landing (64 N): bore shell -> infill crush | infill 20% | 0.32 | 2.2 | 7.08 | 3.0 | OK |
| 5 cm drop, stiff landing (64 N): bore bearing on the M3 threads | XY | 1.73 | 25.0 | 14.49 | 3.0 | OK |
| 5 cm drop at the slice plan's 3 perimeters: rim shell hoop bending | XY | 3.88 | 25.0 | 6.45 | 3.0 | OK |
| 5 cm drop at the slice plan's 3 perimeters: rim shell -> infill crush | infill 20% | 0.18 | 2.2 | 12.58 | 3.0 | OK |
| 5 cm drop at the slice plan's 3 perimeters: bore shell -> infill crush | infill 20% | 0.20 | 2.2 | 11.06 | 3.0 | OK |
| 5 cm drop at the slice plan's 3 perimeters: bore bearing on the M3 threads | XY | 0.86 | 25.0 | 28.98 | 3.0 | OK |
| M3 x 50 class 12.9 bending at the wall face (chassis-owned), 5 cm drop x 17 | steel σy 1080 | 405.30 | 1080.0 | 2.66 | 1.5 | OK |
| M3 x 50 class 12.9, proof 5 kg at the rim centre | steel σy 1080 | 624.50 | 1080.0 | 1.73 | 1.0 | OK |
| M3 x 50 A2-70 (if fitted instead) bending at the wall face (chassis-owned), 5 cm drop x 17 | steel σy 450 | 405.30 | 450.0 | 1.11 | 1.5 | no |
| M3 x 50 A2-70 (if fitted instead), proof 5 kg at the rim centre | steel σy 450 | 624.50 | 450.0 | 0.72 | 1.0 | no |

- **Lowest SF:** 12.96 (required 3.0), at the W1 rim shell.
- **Drop rows:** all meet their SF up to a 21.6 cm drop.
- **Verdict rows below their required SF:** 0 of 10.

## Proof tests

Spec §8 covers the wheel through the chassis tests and matches the NEEDS_TEST verdict. Keep it as written.

**Chassis test 1.** Hang 5 kg (49 N, 1.5 × the corner load) for 1 min from a strap round the middle of this wheel's rim.

**Chassis test 3.** Drop the rover from 5 cm, flat and on each corner.

**Pass after both:**
- the wheel still spins freely, with axial play under 0.5 mm;
- no dent or crack in the rim, and no ring of crushed infill;
- bore ovalisation under 0.1 mm.

The wheel's own margins are large (SF 8 or more at the proof). The proof test mainly checks the chassis boss and the bolt, so **fit class 12.9, or 8.8 at least, before running it.**

**Not strength, for the slicing stage:** `slice_plan.json` sets 3 perimeters against the 5 in `print_requirements.json` (deep review S-24). The validator will reject it. Even at 3 perimeters the rim's SF is 6.45.

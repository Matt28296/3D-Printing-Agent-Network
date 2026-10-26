VERDICT: NEEDS_TEST

# Strength check: 20261026-rover-track-link (round 3)

strength-analyst (independent) · 2026-10-26 · run with the CAD venv: `source /home/claude/.venv-cad/bin/activate`, then `python3 jobs/20261026-rover-track-link/strength_calc.py`

**Result: NEEDS_TEST.** The allowables are placeholders, so PASS is not possible.

- **Lowest ratio.** The Ø2 steel pin in bending when a road wheel lands on a hinge in the 5 cm drop: **SF 4.91**. It needs 1.5 on a conservative 350 MPa yield.
- **Lowest PETG row.** Outer-knuckle tear-out at stall: SF 15.2.
- **Round-3 change.** The running hole opened to Ø2.5 CAD (`PIN_RUN_CLR` 0.3), which thins the centre-knuckle ligament from 1.80 to 1.75 mm. Its tear-out goes from SF 20.4 to 19.8.
- **Drop.** The drop rows hold up to a 16.4 cm drop.
- **Assembly risk (outside the verdict).** Pressing the dowel into the Ø2.0 printed outer knuckles strains them 1–2.5 % across the layers. Spec §8 test 1 covers it.

## Round-2 findings: what round 3 did

| Round 2 | Round 3 | Result |
|---|---|---|
| Steel pins | Ø2 × 24 dowels (ISO 2338 / 8734) or 2 mm rod cut to 23.5 mm | ✓ |
| Proof tests in spec §8: pressing, 4.5 kg tension, 5 kg hinge crush | All three are in spec §8 | ✓ Matches (below) |
| Running fit (DFM) | `PIN_RUN_CLR` 0.2 → 0.3: Ø2.5 CAD, about Ø2.3 printed. Wall 1.75 mm = 4 lines. | Ligament 1.75 mm, confirmed on the solid. Tear-out SF 19.8 at stall, 6.69 at the proof. |

## Load cases

These come from the shared rover block; the chassis report has the full table.

| Load | Value | Note | Duration |
|---|---|---|---|
| Tight run at stall | **14.9 N** (5 + 9.89) | 160 N·mm design. With a gated motor at the sketch's 6 V cap it is ≤ 13.0 N; the stall proof gives 16.2 N, and an ungated S-08 motor 17.1 N (advisory). | short-term |
| Tight run, everyday | 8.2 N (5 + 3.18) | | cyclic |
| Pretension | 5 N | S-16: the guide's sag gives 0.1–1 N, so this is an upper bound | sustained |
| 5 cm drop | 31.8 N per axle, a road wheel landing on a hinge | Mass 649 g, 5 mm stopping distance | short-term |
| Side drag | 3 N | | cyclic |

## Assumptions

**Hinge geometry.** A 13.5 mm centre knuckle sits between two 4.75 mm outer knuckles with 0.5 mm gaps, so each pin works in double shear.

**Pin.** The steel pin is 111 times stiffer than PETG, and its foundation length (1/β = 5.1 mm) is about one knuckle. It is therefore treated as near-rigid:
- bending uses the stiff-pin clevis moment M = F/2 · (a/2 + g + b/4);
- bearing is uniform along each knuckle.

**Tear-out.** The links print inner face down, so the pin holes are horizontal. The strip behind each hole can only shed load into the layers above and below it, so tear-out is checked against the across-layer shear allowable. The ligaments use the CAD holes and were probed on the solid: 1.75 mm (centre knuckle) and 1.90 mm (outer knuckles).

**Drop.** The centre knuckle's share (13.5/24) of the axle load passes through the pin to the outer knuckles above the grousers.

**Press fit (advisory).** Each outer knuckle is treated as a thick ring on a rigid pin. The resulting hoop stress runs across the layers, but it is displacement-controlled: it yields or creeps rather than growing.

## Allowables and sources

**PETG (placeholder).** There is no measured data, so the skill's placeholders apply:
- 25 MPa in-plane, 12.5 MPa across layers;
- shear allowable 0.5 × normal.

**NEEDS_TEST is the best verdict possible.**

**Steel.** Unspecified rod or dowel is taken at 350 MPa yield, which is conservative. An ISO 8734 hardened dowel is far stronger.

**Required SF.**

| Load type | Required SF |
|---|---|
| Short-term | 3 |
| Cyclic or sustained | 4 |
| Steel, on yield | 1.5 |
| Proof loads | 1.0 |

**Temperature.** Service is 40 °C against a PETG softening point of about 70 °C, so it is not limiting.

## Results (`strength_calc.py` output)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | K1 stall tight run: pin bending (stiff-pin clevis), 14.9 N | steel σy 350 | 59.24 | 350.0 | 5.91 | 1.5 | OK |
| 2 | K1 stall tight run: pin shear (2 planes) | steel τy 175 | 2.37 | 175.0 | 73.85 | 1.5 | OK |
| 3 | K1 stall tight run: centre-knuckle bearing | XY | 0.55 | 25.0 | 45.34 | 3.0 | OK |
| 4 | K1 stall tight run: outer-knuckle bearing (each T/2) | XY | 0.78 | 25.0 | 31.90 | 3.0 | OK |
| 5 | K1 stall tight run: centre-knuckle tear-out (ligament 1.75) | Z shear | 0.32 | 6.2 | 19.83 | 3.0 | OK |
| 6 | K1 stall tight run: outer-knuckle tear-out (each T/2, ligament 1.90) | Z shear | 0.41 | 6.2 | 15.15 | 3.0 | OK |
| 7 | K2 everyday tight run: pin bending (stiff-pin clevis), 8.2 N | steel σy 350 | 32.56 | 350.0 | 10.75 | 1.5 | OK |
| 8 | K2 everyday tight run: pin shear (2 planes) | steel τy 175 | 1.30 | 175.0 | 134.37 | 1.5 | OK |
| 9 | K2 everyday tight run: centre-knuckle bearing | XY | 0.30 | 25.0 | 82.48 | 4.0 | OK |
| 10 | K2 everyday tight run: outer-knuckle bearing (each T/2) | XY | 0.43 | 25.0 | 58.04 | 4.0 | OK |
| 11 | K2 everyday tight run: centre-knuckle tear-out (ligament 1.75) | Z shear | 0.17 | 6.2 | 36.09 | 4.0 | OK |
| 12 | K2 everyday tight run: outer-knuckle tear-out (each T/2, ligament 1.90) | Z shear | 0.23 | 6.2 | 27.57 | 4.0 | OK |
| 13 | K3 outer-knuckle bearing, pretension 5 N sustained (creep) | XY | 0.26 | 25.0 | 95.00 | 4.0 | OK |
| 14 | K4 outer-knuckle tear-out, pretension sustained (creep) | Z shear | 0.14 | 6.2 | 45.13 | 4.0 | OK |
| 15 | K5 body net section at the notch root (Kt 2.5), stall | XY | 1.13 | 25.0 | 22.16 | 3.0 | OK |
| 16 | K6 bridge shear, centre lands to outer lands, stall | XY shear | 0.58 | 12.5 | 21.49 | 3.0 | OK |
| 17 | K7 5 cm drop, wheel on a hinge: pin bending on a hinge (clevis), 31.8 N/axle | steel σy 350 | 71.25 | 350.0 | 4.91 | 1.5 | OK |
| 18 | K7 5 cm drop, wheel on a hinge: centre-knuckle bearing | XY | 0.66 | 25.0 | 37.70 | 3.0 | OK |
| 19 | K7 5 cm drop, wheel on a hinge: outer-knuckle bearing (each Fp/2) | XY | 0.94 | 25.0 | 26.53 | 3.0 | OK |
| 20 | K7 5 cm drop, wheel on a hinge: grouser compression | XY | 0.80 | 25.0 | 31.41 | 3.0 | OK |
| 21 | K8 side drag 3.0 N on an outer-knuckle end face | XY | 0.15 | 25.0 | 165.00 | 4.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, fixes, proof loads, bought parts):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| proof (§8 test 2) 4.5 kg on a 5-link chain: pin bending (stiff-pin clevis), 44.1 N | steel σy 350 | 175.65 | 350.0 | 1.99 | 1.0 | OK |
| proof (§8 test 2) 4.5 kg on a 5-link chain: pin shear (2 planes) | steel τy 175 | 7.03 | 175.0 | 24.91 | 1.0 | OK |
| proof (§8 test 2) 4.5 kg on a 5-link chain: centre-knuckle bearing | XY | 1.64 | 25.0 | 15.29 | 1.0 | OK |
| proof (§8 test 2) 4.5 kg on a 5-link chain: outer-knuckle bearing (each T/2) | XY | 2.32 | 25.0 | 10.76 | 1.0 | OK |
| proof (§8 test 2) 4.5 kg on a 5-link chain: centre-knuckle tear-out (ligament 1.75) | Z shear | 0.93 | 6.2 | 6.69 | 1.0 | OK |
| proof (§8 test 2) 4.5 kg on a 5-link chain: outer-knuckle tear-out (each T/2, ligament 1.90) | Z shear | 1.22 | 6.2 | 5.11 | 1.0 | OK |
| proof (§8 test 3) 5 kg road wheel pressed on a hinge: pin bending on a hinge (clevis), 49.1 N/axle | steel σy 350 | 109.78 | 350.0 | 3.19 | 1.0 | OK |
| proof (§8 test 3) 5 kg road wheel pressed on a hinge: centre-knuckle bearing | XY | 1.02 | 25.0 | 24.46 | 1.0 | OK |
| proof (§8 test 3) 5 kg road wheel pressed on a hinge: outer-knuckle bearing (each Fp/2) | XY | 1.45 | 25.0 | 17.22 | 1.0 | OK |
| proof (§8 test 3) 5 kg road wheel pressed on a hinge: grouser compression | XY | 1.23 | 25.0 | 20.39 | 1.0 | OK |
| 5 cm drop, stiff landing (64 N): pin bending on a hinge (clevis), 63.7 N/axle | steel σy 350 | 142.49 | 350.0 | 2.46 | 1.5 | OK |
| 5 cm drop, stiff landing (64 N): centre-knuckle bearing | XY | 1.33 | 25.0 | 18.85 | 3.0 | OK |
| 5 cm drop, stiff landing (64 N): outer-knuckle bearing (each Fp/2) | XY | 1.88 | 25.0 | 13.26 | 3.0 | OK |
| 5 cm drop, stiff landing (64 N): grouser compression | XY | 1.59 | 25.0 | 15.71 | 3.0 | OK |
| stall proof (100 % PWM, fresh pack): pin bending (stiff-pin clevis), 16.2 N | steel σy 350 | 64.65 | 350.0 | 5.41 | 1.5 | OK |
| stall proof (100 % PWM, fresh pack): pin shear (2 planes) | steel τy 175 | 2.59 | 175.0 | 67.67 | 1.5 | OK |
| stall proof (100 % PWM, fresh pack): centre-knuckle bearing | XY | 0.60 | 25.0 | 41.54 | 3.0 | OK |
| stall proof (100 % PWM, fresh pack): outer-knuckle bearing (each T/2) | XY | 0.86 | 25.0 | 29.23 | 3.0 | OK |
| stall proof (100 % PWM, fresh pack): centre-knuckle tear-out (ligament 1.75) | Z shear | 0.34 | 6.2 | 18.18 | 3.0 | OK |
| stall proof (100 % PWM, fresh pack): outer-knuckle tear-out (each T/2, ligament 1.90) | Z shear | 0.45 | 6.2 | 13.89 | 3.0 | OK |
| S-08 ungated 196 N*mm motor: pin bending, tight run 17.1 N | steel σy 350 | 68.09 | 350.0 | 5.14 | 1.5 | OK |
| S-08 ungated motor: outer-knuckle tear-out | Z shear | 0.47 | 6.2 | 13.18 | 3.0 | OK |
| pin press fit 0.02 mm (grip tolerance -0.05): hoop at the outer knuckle's ligament, strain 1.0 % | Z | 14.06 | 12.5 | 0.89 | 1.0 | no |
| pin press fit 0.05 mm (grip tolerance -0.05): hoop at the outer knuckle's ligament, strain 2.5 % | Z | 35.16 | 12.5 | 0.36 | 1.0 | no |

- **Lowest SF:** 4.91 (required 1.5), at K7: pin bending when a wheel lands on a hinge in the 5 cm drop.
- **Drop rows:** all meet their SF up to 16.4 cm.
- **Verdict rows:** 0 of 21 below their required SF.

## Proof tests

Spec §8's three tests match the NEEDS_TEST verdict; keep them as written. Run all three on a 5-link test chain from the first plate.

| Test | Load | Duration | Pass | Placeholder SF at this load |
|---|---|---|---|---|
| 1. Pressing | Press all 10 pins | n/a | No crack or white line at any outer knuckle, especially along the layer line through the pin. Each pin flush and firm. | n/a |
| 2. Tension | Hang 4.5 kg (44 N, 3 × the 14.9 N stall tension) | 1 min | No cracked knuckle, pins not moved, the chain still flexes to 40° both ways | Pin 1.99; tear-out 5.1 or more |
| 3. Hinge crush | Press a road wheel on its bolt across a pinned joint with 5 kg (49 N, 1.5 × the corner load) | 1 min | No cracking, pin straight, joint flexes freely | Pin 3.19 |

**If knuckles crack in test 1:** set `PIN_GRIP_CLR` 0 → +0.05 and retain each pin with CA instead.

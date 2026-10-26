VERDICT: NEEDS_TEST

# Strength check: 20261026-rover-sprocket (round 3)

strength-analyst (independent) · 2026-10-26 · run with the CAD venv: `source /home/claude/.venv-cad/bin/activate`, then `python3 jobs/20261026-rover-sprocket/strength_calc.py`

**Result: NEEDS_TEST.** The allowables are placeholders, so PASS is not possible. All 10 verdict rows pass.

- **Lowest SF: 3.11**, at the tooth root (chamfer top) under the 160 N·mm design stall: 9.89 N on one tooth at the pitch circle, Kt 1.8.
- **Drop:** the rows hold their SF up to a 6.2 cm drop, limited by the 1.9 mm ligament between the centre hole and a slot.
- **Concept C works for this part.** The torque now reaches the disc through metal. Slot bearing is SF 36 or more, the shaft end in the centre hole 5.9, and the rim 19.8.
- **One condition.** The tooth margin depends on the chassis §8 motor gate. An ungated 2 kg·cm motor (S-08) puts the tooth at SF 2.54, so the gate has to happen before the disc is fitted (see proof tests).

## Round-2 required changes: what round 3 did

| Round 2 change | Round 3 | Result |
|---|---|---|
| 1. Metal N20 hub, clear of the bearing boss | Pololu #1996 aluminium hub, its own M3 set screw on the D-flat. The disc bolts to it with 4 × M3 × 12 through radial slots (r 5.5–6.85). The hub sits outside the 1 mm chassis skin, and the boss passes through the skin's Ø4.5 hole. | ✓ The D-flat rows are gone (round 2: SF 1.24). Slot bearing H1 is 36 at stall. |
| 2. No radial hole in any printed hub section | No printed hub; the part is a 7 mm disc | ✓ The set-screw-hole rows are gone (round 2: SF 1.06–3.37) |
| 3. Any printed tube Ø ≥ 10.5 | No tube | ✓ Redundant |
| DFM round 2 (hub-end counterbore, set screw onto the flat) | The metal hub carries the set screw and doesn't touch the boss | ✓ Moot |

## Load cases

Shared rover block; the chassis `strength.md` has the full table.

| Load | Value | Note | Duration |
|---|---|---|---|
| Stall pull at the pitch circle (RP 16.18) | **9.89 N** (160 N·mm design). Proof 11.25 N (182 N·mm). | Deep review S-08 brackets 6.6–13.6 N per side at the *old* 80 % cap. Round 3 changed two things: the sketch caps the motor at 6.0 V average, and chassis §8 gates the motor at ≤ 182 N·mm on a fresh pack at 100 % PWM. A gated motor therefore gives ≤ 130 N·mm (8.0 N) in service; 160 covers it. The ungated S-08 motor (196 N·mm: 12.1 N at the 6 V cap, 13.6 N at the old cap) is in the advisory rows. | short-term |
| Everyday pull | 3.18 N (μ 1.0 × W/2) | Rounds 1–2 | cyclic |
| Sprocket radial | 19.9 N stall / 13.2 cyclic / 10 sustained (pretension 5 N per run) | | as stated |
| 5 cm drop | 31.8 N on the rear axle, corner landing | Mass 649 g; 5 mm stopping distance (spec §4). An elastic estimate gives several times this; the drop test is the evidence. | short-term |
| Side drag | 3 N per track | Spec. S-15's pivot turn needs ≤ 1.43 N per track half. | cyclic |

**Tooth case.** The engaged teeth together carry the tight run minus the slack run, which is the stall pull. Rounds 1–2 put all of it on one tooth at the pitch circle, and that convention is kept. A tooth tip loaded on a slack track is advisory; the jack screw limits the slack.

## Assumptions

- **Tooth section.** Cut from the build123d solid at the top of the root chamfer (r 12.39): 2.70 × 7.00, A 18.81 mm², Z 8.40 mm³ (the hand formula gives 8.51).
- **Tooth Kt 1.8**, the rounds 1–2 value for a 0.5 × 45° chamfer on a small step (D/d 1.37). A sharp corner (Kt 2.0) gives 2.80 (advisory).
- **Screws.** No clamp friction is credited, because the PETG under the screw washers creeps. The torque goes into the slot sides in bearing.
- **Slot tolerance.** Only 2 of the 4 screws are assumed to bear at first, at the smallest slot radius (5.5).
- **Radial loads.** The slots sit at 45° to any vertical load. The disc can shift about 0.2 mm before the shaft end bears in the Ø3.4 centre hole. A 9 mm shaft engages 2.5 mm of the disc (a 10 mm shaft, 3.5 mm), so 2.5 is used.
- **Direction.** The disc prints flat, so tooth bending, slot bearing and ligament shear are all in the layer plane.
- **The N20 shaft is bought and checked as advisory.**
  - Minimum section modulus over every bending direction: 1.911 mm³ (designer: 1.931).
  - Arm 10 mm. SF 3.36 at stall, 3.15 on a fresh pack and 2.10 at the 5 cm corner, against the designer's 3.40, 3.18 and 2.13.
  - If the chassis skin grows to 2 mm (chassis change 2), the arm is 11 mm: 3.06 and 1.91, still inside the Architect's 2 and 1.5.

## Allowables and sources

**No measured data:**
- `library/materials.csv` has only its header row, so the skill's placeholders apply: PETG 25 MPa in-plane, 12.5 MPa across layers. Shear allowable is 0.5 × normal.
- **NEEDS_TEST is the best verdict possible.**

**Required SF:**

| Load type | Required SF |
|---|---|
| Short-term | 3 |
| Cyclic or sustained | 4 |
| Bought steel, on yield | 1.5 |
| Proof loads | 1.0 |

**Steel and temperature:**
- The N20 shaft is taken at 350 MPa.
- At 40 °C service against a PETG softening point of about 70 °C, temperature is not limiting.

## Results (`strength_calc.py` output)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | T1 tooth root (chamfer top), stall pull 9.89 N on one tooth at RP (Kt 1.8) | XY | 8.03 | 25.0 | 3.11 | 3.0 | OK |
| 2 | T2 tooth root, everyday pull 3.18 N (Kt 1.8) | XY | 2.59 | 25.0 | 9.67 | 4.0 | OK |
| 3 | T3 tooth root shear, stall | XY shear | 0.79 | 12.5 | 15.85 | 3.0 | OK |
| 4 | H1 hub-screw bearing on the slot side, stall 160 N*mm (2 of 4 screws at r 5.5) | XY | 0.69 | 25.0 | 36.09 | 3.0 | OK |
| 5 | H2 hub-screw bearing, everyday 52 N*mm | XY | 0.22 | 25.0 | 112.12 | 4.0 | OK |
| 6 | H3 hub-screw bearing, 5 cm rear corner 31.8 N (slots at 45° to the load, 2 bearing) | XY | 1.07 | 25.0 | 23.32 | 3.0 | OK |
| 7 | H4 shaft end bearing in the centre hole, 5 cm rear corner (9 mm shaft: 2.5 mm engaged) | XY | 4.24 | 25.0 | 5.89 | 3.0 | OK |
| 8 | H5 centre-hole-to-slot ligament (1.90 mm) shear-out, 5 cm rear corner toward a slot | XY shear | 3.35 | 12.5 | 3.73 | 3.0 | OK |
| 9 | R1 disc rim bearing under a link, 5 cm rear corner | XY | 1.26 | 25.0 | 19.79 | 3.0 | OK |
| 10 | S1 side drag 3 N on the screw washers (4 x 23.4 mm² beside the slots) | XY | 0.03 | 25.0 | 781.52 | 4.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, fixes, proof loads, bought parts):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| proof (§8 test 1): stall 182 N*mm, tooth root (11.25 N) | XY | 9.14 | 25.0 | 2.74 | 1.0 | OK |
| proof (§8 test 2): 2 kg (19.6 N) on one tooth at RP | XY | 15.94 | 25.0 | 1.57 | 1.0 | OK |
| proof: stall 182 N*mm, hub-screw bearing | XY | 0.79 | 25.0 | 31.73 | 1.0 | OK |
| S-08 ungated motor Phipps GA12-N20 6V 100 rpm: tooth root at the 6.0 V cap (12.1 N) | XY | 9.84 | 25.0 | 2.54 | 3.0 | no |
| S-08 Phipps GA12-N20 6V 100 rpm: tooth root at the old 80 % cap (13.6 N) | XY | 11.02 | 25.0 | 2.27 | 3.0 | no |
| tooth root, stall, if the chamfer acts like a sharp corner (Kt 2.0) | XY | 8.93 | 25.0 | 2.80 | 3.0 | no |
| tooth root, stall pull at the TIP (a link riding over a tooth on a slack track) | XY | 11.65 | 25.0 | 2.15 | 3.0 | no |
| H3/H4, 5 cm corner, stiff landing (stopping distance 2.5 mm, 64 N): shaft end bearing | XY | 8.49 | 25.0 | 2.95 | 3.0 | no |
| assembly: M3 x 12 into the hub at 0.3 N*m (P 500 N): washer on the disc (23.4 mm² beside the slot) | XY | 21.33 | 25.0 | 1.17 | 3.0 | no |
| assembly: M3 x 12 into the hub at 0.8 N*m (P 1333 N): washer on the disc (23.4 mm² beside the slot) | XY | 56.87 | 25.0 | 0.44 | 3.0 | no |
| N20 shaft (bought), arm 10, Z_min 1.911: stall 19.9 N | steel σy 350 | 104.07 | 350.0 | 3.36 | 1.5 | OK |
| N20 shaft (bought), arm 10, Z_min 1.911: fresh pack 100 % PWM 21.2 N | steel σy 350 | 111.19 | 350.0 | 3.15 | 1.5 | OK |
| N20 shaft (bought), arm 10, Z_min 1.911: 5 cm corner 31.8 N | steel σy 350 | 166.58 | 350.0 | 2.10 | 1.5 | OK |

- Lowest SF: 3.11 (required 3.0), at T1, the tooth root.
- Drop rows meet their SF up to 6.2 cm, limited by H5.
- 0 of 10 verdict rows are below their required SF.

## Proof tests

Spec §8 matches the NEEDS_TEST verdict; keep both tests.

1. **Torque.**
   - Hold the track still and stall the motor at 100 % PWM on a freshly charged pack, 1 s at a time, 5 times. That applies about 182 N·mm: 1.14 × the design value and 1.4 × a gated motor at the sketch's cap. Tooth SF at that torque: 2.74 on the placeholder.
   - Pass: no slip of the hub on the shaft or of the disc on the hub (pen marks); no cracked or sheared tooth; the sprocket still runs true.
   - The sketch caps the motors at 6.0 V average, so this test needs the cap lifted for the test only.
2. **Tooth.**
   - Hang **2 kg (19.6 N, 2 × the stall pull)** for 1 min from one link seated on one horizontal tooth.
   - Pass: no crack at the tooth root and no permanent set. SF 1.57 on the placeholder.

**Condition (from S-08):**
- Measure each motor's stall torque (chassis §8 test 2: ≤ 371 g on a 50 mm arm) **with only the hub fitted, before the disc goes on and before the first drive**.
- If a motor reads higher, it isn't the specified type and must not drive these teeth. At 196 N·mm the tooth is at SF 2.54.

## Notes

- **Hub screws.** BUILD_GUIDE step 6 says "tighten the screws evenly (2.5 mm key)". A firm 0.8 N·m into the aluminium hub puts about 1.3 kN on each washer, and the washer bridges the slot onto 23 mm² of PETG: 57 MPa. That crushes the disc and lets it wobble. The design takes no credit for the clamp (H1 is in bearing), so say "snug, about 0.3 N·m, and re-check after the first run".
- **Advisory below 3, all outside the verdict cases:**
  - the stiff-landing shaft-end bearing (2.95);
  - the tooth-tip case (2.15), which the jack screw prevents.

VERDICT: NEEDS_TEST

# Strength check: 20261026-rover-sprocket (round 3, with the round 4 shaft-end re-check)

strength-analyst (independent) · 2026-10-26 (round 4 re-check the same day) · run with the CAD venv: `source /home/claude/.venv-cad/bin/activate`, then `python3 jobs/20261026-rover-sprocket/strength_calc.py`

**Result: NEEDS_TEST, with one new condition.** The allowables are placeholders, so PASS is not possible.
- All 10 verdict rows pass **only if the motor's shaft sticks out at least 9.6 mm from the gearbox face**. The BUILD_GUIDE change is below.
- With a 9 mm shaft, H5 is at SF 2.24 and the verdict would be FAIL.

- **Round 4 re-check: the shaft end, after the chassis round-4 skin change.**
  - **What moved.** The 2 mm skin moved the gearbox face from |y| 45 to 44. Every shaft end now sits 1 mm less deep in the disc's centre hole: 1.5 mm for a 9 mm shaft, 2.5 mm for a 10 mm one.
  - **What H5 needs.** The centre-hole-to-slot ligament (H5) needs 2.01 mm of shaft in the disc for SF 3, which is a shaft at least 9.51 mm from the gearbox face.
  - **Results:**

    | Shaft from the gearbox face | H4 | H5 |
    |---|---|---|
    | 9 mm | 3.53 | **2.24 (fails)** |
    | 10 mm | 5.89 | 3.73 |
    | 9.6 mm, the shortest allowed | 4.95 | **3.13** |

  - **Decision: restrict the motor to a 10 mm shaft, 9.6 mm at least.** The load-path arguments don't clear a 9 mm shaft without relaxing the method (round 4 section).
  - **The example motor still qualifies.** The BUILD_GUIDE's Pololu 150:1 Micro Metal Gearmotor stays: Pololu's spec note says its output shaft "adds 10 mm" to the body length.
- **Lowest SF: 3.11, unchanged.** It is at the tooth root (chamfer top) under the 160 N·mm design stall: 9.89 N on one tooth at the pitch circle, Kt 1.8.
- **Drop rows meet their SF up to 5.2 cm** at the shortest allowed shaft, limited by H5 (round 3: 6.2 cm).
  - With a 10 mm shaft: 6.2 cm.
  - A 9 mm shaft would limit it to 3.7 cm.
- **Concept C still works for this part.** The torque reaches the disc through metal. Slot bearing is SF 36 or more and the rim 19.8.
- **Round 3's condition stands.** The tooth margin depends on the chassis §8 motor gate. An ungated 2 kg·cm motor (S-08) puts the tooth at SF 2.54, so the gate has to happen before the disc is fitted (see proof tests).

## Round 4 re-check: the shaft end in the centre hole

This section covers only the change from the chassis round 4. The sprocket's geometry is unchanged, and every other row is as in round 3.

### What moved

The chassis skin in front of the gearbox grew inward from 1 to 2 mm. The thrust washer, the hub and the track plane stayed where they were, so the gearbox face moved 1 mm inward. `strength_calc.py` now computes the shaft end from `rover_frame`: `MOTOR_FACE_Y` + the shaft length. Round 3 hard-coded the end at |y| 54.

| | Round 3 | Round 4 |
|---|---|---|
| Gearbox face (`MOTOR_FACE_Y`) | \|y\| 45.0 | **44.0** |
| Skin, thrust washer, hub | 45–46, 46.0–46.5, 46.5–51.5 | 44–46, 46.0–46.5, 46.5–51.5 |
| Sprocket disc | 51.5–58.5 | 51.5–58.5 |
| 9 mm shaft: end, depth in the disc | 54.0, 2.5 mm | 53.0, **1.5 mm** |
| 10 mm shaft (`MOTOR.shaft_len`): end, depth in the disc | 55.0, 3.5 mm | 54.0, **2.5 mm** |
| N20 shaft arm, gearbox face to track plane | 10 mm | 11 mm |

### H4 and H5 in the 5 cm rear-corner drop (31.8 N)

The method is round 3's, unchanged.
- **H4, bearing:** σ = F/(d·L), where L is the shaft length inside the disc.
- **H5, tear-out:** τ = F/(2·e·L), where e is the 1.90 mm CAD ligament from the centre hole to a slot's inner end.

| Shaft (from the gearbox face) | In the disc | H4 bearing SF | H5 ligament SF | |
|---|---|---|---|---|
| 9 mm, round 3 geometry | 2.5 mm | 5.89 | 3.73 | was the verdict row |
| 9 mm, round 4 | 1.5 mm | 3.53 | **2.24** | fails 3.0 |
| 9.6 mm (shortest allowed), round 4 | 2.1 mm | 4.95 | **3.13** | verdict rows |
| 10 mm, round 4 | 2.5 mm | 5.89 | 3.73 | the specified N20 |
| Needed for SF 3 | H4 1.27 mm, H5 **2.01 mm** | | | H5: a shaft ≥ 9.51 mm |

### Can a load-path analysis clear a 9 mm shaft? No.

**1. The hub screws can't be counted on to take the load first (the H3 argument).**
- Both radial paths have about 0.2 mm of nominal clearance:
  - the Ø3.0 shaft in the printed Ø3.4 hole;
  - an M3 in a printed 3.4 mm slot, on each side.
- But the slots are radial, so a screw only bears once the disc has moved 0.2 mm across its slot.
- **Load at 45° to the slots** (where the shaft bears between two slots, H4):
  - The screws need a disc shift of 0.28 mm to bear; the shaft end needs only 0.20.
  - At 1.5 mm of engagement, the shaft-end path gives only about 0.035 mm at the full 31.8 N (ligament bending and shear plus a contact allowance). That is less than the 0.083 mm the screws still need.
  - So the shaft end carries the whole drop load before any screw touches.
- **Load toward a slot** (H5's case):
  - The two screws across that slot and the shaft end have equal nominal gaps (0.20 = 0.20).
  - Which path bears first is then set by the printed sizes of the hole and the slots, ±0.1 mm. There is no library row for hole compensation.
- Clamp friction isn't credited, as in round 3: the PETG under the washers creeps.
- So H3 (SF 23) shows that the screws could carry the load. It does not take the load off the shaft end. Round 3's convention stays: each path is checked for the full load.

**2. Bearing can't be spread through the 7 mm disc either.**
- **What the method uses.** The skill's tear-out formula takes t as the length the pin bears on, and round 3 used the engaged length.
- **What spreading would need.** For H5 to pass with a 9 mm shaft, the layers below the engaged 1.5 mm would have to take about 8 N. That load would cross layer interfaces inside the 1.9 × 3.6 mm ligament.
- **Why it isn't credited:**
  - The disc prints outer face down, so the engaged 1.5 mm is the last layers printed, and the transfer would rely on their across-layer strength. That is exactly where placeholder data say least.
  - No formula in `strength-checks` covers that dispersion. Crediting it would relax the method.

**3. The cheap fix is the shaft length, not an analysis.** A 10 mm shaft, as specified (`N20_100RPM.shaft_len`) and as on the Pololu example motor, gives 2.5 mm in the disc: H5 3.73.
- **The 9.6 mm floor.** It catches shafts sold as "9 mm" and keeps a small margin over the 9.51 mm limit (H5 3.13).
- **The stack-up check.** The engagement also depends on the printed skin thickness and the washer (about ±0.2 mm). A direct check on the assembled hub is therefore proposed as a §8 acceptance item (below).

### The Pololu motor's shaft

The BUILD_GUIDE's example is the Pololu 150:1 Micro Metal Gearmotor LP/MP 6 V (the MP is #2368).
- **The product page reads two ways:**
  - its description says "a 9 mm long, 3 mm diameter D-shaped gearbox output shaft";
  - its dimensions table, note 1, says "Output shaft adds 10 mm to the 26 mm length. See dimension diagram for details."
- **The dimension diagram.** Its side view of the LP/MP/HP no-encoder version carries 10 / 0.7 / 4.0 / 3.0 / 2.5 mm (micro-metal-gearmotors-dimensions.pdf, read as extracted text).
- **My reading:** the shaft ends **10 mm from the gearbox face**, past a Ø4.0 × 0.7 bushing. Ø3.0 is the shaft and 2.5 the D-flat dimension. The "9 mm" in the description is the shaft beyond the bushing.
- **What that gives here:** about 2.5 mm in the disc, H5 3.73.
- **Caveat:** I read the drawing as extracted text, not as an image. The shaft-length check at the hub (below) catches any surprise.
- **Sources:**
  - [Pololu 150:1 Micro Metal Gearmotor MP 6V, specs](https://www.pololu.com/product/2368/specs)
  - [Pololu micro metal gearmotor resources](https://www.pololu.com/product/2382/resources)
  - [dimension diagram PDF](https://www.pololu.com/file/0J949/micro-metal-gearmotors-dimensions.pdf)

### BUILD_GUIDE §1, row 2 (the motor): how it should read

| Qty | Item | Notes |
|---|---|---|
| 2 | N20 (GA12) gear motor: 6 V, 100 rpm (≈150:1), **LP or MP winding** (stall ≤ 0.7 A at 6 V), 9 mm metal gearbox, 3 mm D-shaft **10 mm long, measured from the flat gearbox face (at least 9.6 mm)**. For example, Pololu 150:1 Micro Metal Gearmotor LP or MP 6 V: its output shaft adds 10 mm to the body length | An 11 mm gearbox also fits. **Don't use a 9 mm shaft**: its end reaches only 1.5 mm into the sprocket's centre hole, and a 5 cm drop can then shear the ring between that hole and a screw slot. Measure from the flat metal face of the gearbox, not from the round bushing. Don't use an HP winding: it overloads the driver and the printed parts. Measure each motor's stall torque before the proof tests (chassis `spec.md` §8) |

**Optional, BUILD_GUIDE §3 step 6.** After the line that tightens the hub's set screw, add:
> Check that the shaft end stands at least 2.1 mm proud of the hub's outer face (calipers' depth rod). If it is shorter, the motor's shaft is too short (§1).

### Spec changes for the Architect

Spec §8's proof tests 1 and 2 still match: they don't involve the shaft end. Other lines no longer match round 4:

- **§1.** "the shaft overhang from the gearbox face to the track plane is 10 mm" → "is 11 mm (chassis round 4: 2 mm skin)".
- **§2, centre hole.** "the shaft end (world |y| 55 for a 10 mm shaft, 54 for 9 mm) runs free in it" → "the shaft end (world |y| 54 for a 10 mm shaft; at least 53.6) runs free in it, at least 2.1 mm deep".
- **§3, motor note.** "3 mm D-shaft 10 mm long; a 9 mm shaft also fits (5 mm engaged in the hub either way)" → "3 mm D-shaft 10 mm long from the gearbox face (at least 9.6 mm). A 9 mm shaft is too short: its end reaches only 1.5 mm into the centre hole (strength round 4, H5)".
- **§4, the radial-load row.** "disc → hub → N20 shaft, 10 mm from the gearbox face" → "11 mm from the gearbox face".
- **§8, add an acceptance item** before the proof tests:
  > [ ] With the hub on its thrust washer against the skin, the shaft end stands at least 2.1 mm proud of the hub's outer face (calipers' depth rod), so it reaches at least 2.1 mm into the disc's centre hole (strength round 4, H5).

**Other files carrying the old wording** (not this review's to edit):
- `model.py`: its docstring says "Y 54 or 55 for a 9 or 10 mm shaft", and the comment on `SHAFT_CLEAR_D` says "Y 51.0";
- this job's `design_brief.md`: "9 or 10 mm shafts all work";
- the chassis `design_brief.md`: "9 or 10 mm shafts all fit";
- the assembly plan's motor-variants line.

### N20 shaft bending at the 11 mm arm (bought part, advisory)

The chassis round 4 made round 3's what-if real:
- stall: SF 3.06;
- fresh pack at 100 % PWM: 2.86;
- 5 cm corner: 1.91.

All three are inside the Architect's limits of 2 at stall and 1.5 in the drop.

## Round-2 required changes: what round 3 did

| Round 2 change | Round 3 | Result |
|---|---|---|
| 1. Metal N20 hub, clear of the bearing boss | Pololu #1996 aluminium hub, its own M3 set screw on the D-flat. The disc bolts to it with 4 × M3 × 12 through radial slots (r 5.5–6.85). The hub sits outside the chassis skin (1 mm in round 3, 2 mm since chassis round 4), and the boss passes through the skin's Ø4.5 hole. | ✓ The D-flat rows are gone (round 2: SF 1.24). Slot bearing H1 is 36 at stall. |
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
- **Radial loads (round 4).** The slots sit at 45° to any vertical load. The disc can shift about 0.2 mm before the shaft end bears in the Ø3.4 centre hole. Since chassis round 4, the shaft end reaches 2.1 mm into the disc at the shortest allowed shaft (9.6 mm) and 2.5 mm at the specified 10 mm, so 2.1 is used. Round 3 used 2.5, for a 9 mm shaft with the gearbox face at |y| 45.
- **Direction.** The disc prints flat, so tooth bending, slot bearing and ligament shear are all in the layer plane.
- **The N20 shaft is bought and checked as advisory.**
  - Minimum section modulus over every bending direction: 1.911 mm³ (designer: 1.931).
  - The arm is 11 mm since chassis round 4 (10 in round 3). SF 3.06 at stall, 2.86 on a fresh pack and 1.91 at the 5 cm corner. All are inside the Architect's 2 and 1.5.

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

Rows 1–6, 9 and 10 are round 3's rows, with unchanged values. Rows 7 and 8 (H4 and H5) are re-run for round 4, at the shortest allowed shaft.

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | T1 tooth root (chamfer top), stall pull 9.89 N on one tooth at RP (Kt 1.8) | XY | 8.03 | 25.0 | 3.11 | 3.0 | OK |
| 2 | T2 tooth root, everyday pull 3.18 N (Kt 1.8) | XY | 2.59 | 25.0 | 9.67 | 4.0 | OK |
| 3 | T3 tooth root shear, stall | XY shear | 0.79 | 12.5 | 15.85 | 3.0 | OK |
| 4 | H1 hub-screw bearing on the slot side, stall 160 N*mm (2 of 4 screws at r 5.5) | XY | 0.69 | 25.0 | 36.09 | 3.0 | OK |
| 5 | H2 hub-screw bearing, everyday 52 N*mm | XY | 0.22 | 25.0 | 112.12 | 4.0 | OK |
| 6 | H3 hub-screw bearing, 5 cm rear corner 31.8 N (slots at 45° to the load, 2 bearing) | XY | 1.07 | 25.0 | 23.32 | 3.0 | OK |
| 7 | H4 shaft end bearing in the centre hole, 5 cm rear corner (round 4: shortest allowed shaft, 9.6 mm from the gearbox face, 2.1 mm in the disc) | XY | 5.05 | 25.0 | 4.95 | 3.0 | OK |
| 8 | H5 centre-hole-to-slot ligament (1.90 mm) shear-out, 5 cm rear corner toward a slot (round 4: 2.1 mm engaged) | XY shear | 3.99 | 12.5 | 3.13 | 3.0 | OK |
| 9 | R1 disc rim bearing under a link, 5 cm rear corner | XY | 1.26 | 25.0 | 19.79 | 3.0 | OK |
| 10 | S1 side drag 3 N on the screw washers (4 x 23.4 mm² beside the slots) | XY | 0.03 | 25.0 | 781.52 | 4.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, proof loads, bought parts):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| proof (§8 test 1): stall 182 N*mm, tooth root (11.25 N) | XY | 9.14 | 25.0 | 2.74 | 1.0 | OK |
| proof (§8 test 2): 2 kg (19.6 N) on one tooth at RP | XY | 15.94 | 25.0 | 1.57 | 1.0 | OK |
| proof: stall 182 N*mm, hub-screw bearing | XY | 0.79 | 25.0 | 31.73 | 1.0 | OK |
| S-08 ungated motor Phipps GA12-N20 6V 100 rpm: tooth root at the 6.0 V cap (12.1 N) | XY | 9.84 | 25.0 | 2.54 | 3.0 | no |
| S-08 Phipps GA12-N20 6V 100 rpm: tooth root at the old 80 % cap (13.6 N) | XY | 11.02 | 25.0 | 2.27 | 3.0 | no |
| tooth root, stall, if the chamfer acts like a sharp corner (Kt 2.0) | XY | 8.93 | 25.0 | 2.80 | 3.0 | no |
| tooth root, stall pull at the TIP (a link riding over a tooth on a slack track) | XY | 11.65 | 25.0 | 2.15 | 3.0 | no |
| round 4 H4, 9 mm shaft (excluded by the round-4 BUILD_GUIDE row): 1.5 mm in the disc | XY | 7.07 | 25.0 | 3.53 | 3.0 | OK |
| round 4 H5, 9 mm shaft (excluded by the round-4 BUILD_GUIDE row): 1.5 mm in the disc | XY shear | 5.58 | 12.5 | 2.24 | 3.0 | no |
| round 4 H4, 10 mm shaft (the specified N20; Pololu micro metal gearmotors): 2.5 mm in the disc | XY | 4.24 | 25.0 | 5.89 | 3.0 | OK |
| round 4 H5, 10 mm shaft (the specified N20; Pololu micro metal gearmotors): 2.5 mm in the disc | XY shear | 3.35 | 12.5 | 3.73 | 3.0 | OK |
| H3/H4, 5 cm corner, stiff landing (stopping distance 2.5 mm, 64 N): shaft end bearing, 2.1 mm engaged | XY | 10.11 | 25.0 | 2.47 | 3.0 | no |
| assembly: M3 x 12 into the hub at 0.3 N*m (P 500 N): washer on the disc (23.4 mm² beside the slot) | XY | 21.33 | 25.0 | 1.17 | 3.0 | no |
| assembly: M3 x 12 into the hub at 0.8 N*m (P 1333 N): washer on the disc (23.4 mm² beside the slot) | XY | 56.87 | 25.0 | 0.44 | 3.0 | no |
| N20 shaft (bought), arm 11, Z_min 1.911: stall 19.9 N | steel σy 350 | 114.48 | 350.0 | 3.06 | 1.5 | OK |
| N20 shaft (bought), arm 11, Z_min 1.911: fresh pack 100 % PWM 21.2 N | steel σy 350 | 122.31 | 350.0 | 2.86 | 1.5 | OK |
| N20 shaft (bought), arm 11, Z_min 1.911: 5 cm corner 31.8 N | steel σy 350 | 183.24 | 350.0 | 1.91 | 1.5 | OK |

- **Lowest SF:** 3.11 (required 3.0), at T1, the tooth root.
- **Drop rows:** they meet their SF up to 5.2 cm, limited by H5 at the shortest allowed shaft (9.6 mm). With a 10 mm shaft it is 6.2 cm; a 9 mm shaft would give 3.7 cm. Round 3 had 6.2 cm.
- **Verdict rows:** 0 of 10 are below their required SF, with the shaft restricted as above.

## Proof tests

**Spec §8 matches the NEEDS_TEST verdict; keep both tests.** Round 4 adds only the shaft-length acceptance item above.

1. **Torque.**
   - **Test.** Hold the track still and stall the motor at 100 % PWM on a freshly charged pack, 1 s at a time, 5 times.
   - **Load.** About 182 N·mm: 1.14 × the design value and 1.4 × a gated motor at the sketch's cap. Tooth SF at that torque: 2.74 on the placeholder.
   - **Pass.** No slip of the hub on the shaft or of the disc on the hub (pen marks); no cracked or sheared tooth; the sprocket still runs true.
   - The sketch caps the motors at 6.0 V average, so this test needs the cap lifted for the test only.
2. **Tooth.**
   - **Test.** Hang **2 kg (19.6 N, 2 × the stall pull)** for 1 min from one link seated on one horizontal tooth.
   - **Pass.** No crack at the tooth root and no permanent set. SF 1.57 on the placeholder.

**Condition (from S-08):**
- Measure each motor's stall torque (chassis §8 test 2: ≤ 371 g on a 50 mm arm) **with only the hub fitted, before the disc goes on and before the first drive**.
- If a motor reads higher, it isn't the specified type and must not drive these teeth. At 196 N·mm the tooth is at SF 2.54.

**Condition (round 4):** the motor's shaft must stick out at least 9.6 mm from the gearbox face. Check it on the fitted hub: the shaft end must stand at least 2.1 mm proud of the hub's outer face.

## Notes

- **Hub screws.** BUILD_GUIDE step 6 says "tighten the screws evenly (2.5 mm key)".
  - **The problem.** A firm 0.8 N·m into the aluminium hub puts about 1.3 kN on each washer. The washer bridges the slot onto 23 mm² of PETG: 57 MPa. That crushes the disc and lets it wobble.
  - **The advice.** The design takes no credit for the clamp (H1 is in bearing), so the step should say "snug, about 0.3 N·m, and re-check after the first run".
- **Advisory below 3, all outside the verdict cases:**
  - the stiff-landing shaft-end bearing (2.47 at the shortest allowed shaft; 2.95 with a 10 mm shaft);
  - the tooth-tip case (2.15), which the jack screw prevents.
- **An alternative to restricting the shaft, needing a new design round.** A centre hole the shaft can never touch would remove H4 and H5 altogether: Ø4.4 printed instead of Ø3.4 gives 0.7 mm of radial clearance, more than the 0.28 mm the screws need plus tolerance. The hub screws (H3, SF 23) would then carry the drop. The ligament to each slot would shrink to about 1.5 mm, but it would carry no load. It would allow 9 mm shafts, but it changes `model.py`, so the shaft restriction is the change for now.

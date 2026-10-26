VERDICT: NEEDS_TEST

# Strength check: 20261026-rover-idler (round 3)

strength-analyst (independent) · 2026-10-26 · run with the CAD venv: `source /home/claude/.venv-cad/bin/activate`, then `python3 jobs/20261026-rover-idler/strength_calc.py`

**Result: NEEDS_TEST.** The allowables are placeholders, so PASS is not possible.

- **Lowest SF:** 11.96, for bore bearing on the M3 threads in the 5 cm front-corner drop (31.8 N).
- **Every row** is at SF 11 or more, including the reverse stall, where the idler carries both runs tight (29.8 N).
- **Drop rows:** they hold up to a 19.9 cm drop.

The idler itself is sound. Its mounting belongs to the chassis check (bolt, slot, sliding nut, clamp, jack screw), and that check **fails**:
- **Jack screw:** it holds the idler bolt's rearward *force* (thread SF 4.8).
- **Clamp:** the bolt's *yaw moment* still rests on PETG under the Ø9 head washer and the sliding nut, at SF 0.60 at a reverse stall and 1.50 under the sustained pretension.
- **Consequence:** the idler leans back and the track loses tension.
- **If the chassis is not fixed:** the idler's own hub face becomes the backstop and crushes at a reverse stall (advisory, SF 0.56).
- **Spec §8 proof test 1:** it needs a lean criterion to catch this (below).

## Round-2 findings: what round 3 did

| Round 2 | Round 3 | Result |
|---|---|---|
| Bolt grade (chassis-owned): A2-70 fails at the reverse stall and the 5 cm corner | Class 12.9, fully threaded, M3 × 40 | ✓ SF 2.85 at the reverse stall, 2.66 at the 5 cm corner (advisory; chassis rows B10/B11) |
| Positive stop instead of a friction clamp (chassis change 4) | An M3 × 20 jack screw bears on the bolt head | ✓ Force held (chassis B7, SF 4.82). ✗ The moment is not held (chassis B5/B6). See the chassis report, change 1. |
| Proof test added to spec §8 | §8 test 1: 4.5 kg rearward for 1 min | ✓ Kept, with a lean criterion added (below) |
| Root chamfer starts on the disc circle (DFM round 2, R1) | Done in the shared sprocket model | Tooth section 8.40 mm³ (from the solid); jam case SF 3.11 |

## Load cases

Shared rover block; the chassis report has the full table.

| Load | Value | Note | Duration |
|---|---|---|---|
| Idler radial, reverse stall | **29.8 N** (both runs tight: 2 × (5 + 9.89)) | Spec §4. Proof stall 32.5 N. An ungated S-08 motor at the 6 V cap gives 34.2 N. | short-term |
| Everyday | 16.4 N (2 × 8.2) | | cyclic |
| Pretension | 10 N (2 × 5 N) | S-16: the guide's sag gives about 0.1–1 N per run, so this is an upper bound | sustained |
| 5 cm drop | 31.8 N, front corner | Mass 649 g, 5 mm stopping distance | short-term |
| Side drag | 3 N | | cyclic |

## Assumptions

- **Bore.** The Ø3.7 CAD bore prints at about Ø3.5 and runs on the threads of the fully threaded M3 with 0.5 mm clearance.
- **Bearing area.** Taken as half the projected area (crest contact), over the 7 mm disc plus a 45° spread into the Ø10 hub. That gives an effective 5.08 mm. Bearing on the vertical bore is in-plane.
- **Teeth.** A free idler's teeth only carry the bearing drag (0.83 N). A jam that puts the stall pull on one tooth is advisory: SF 3.11, the same teeth as the sprocket.
- **Backstop (advisory).** If the chassis clamp yaws, the idler leans until its hub face presses the wall washer.
  - The edge contact is taken as a 30° arc × 1.5 mm at r 5.
  - The force is the yaw moment divided by 5 mm.

## Allowables and sources

**No measured data.** The skill's placeholders apply:
- PETG 25 MPa in-plane and 12.5 MPa across layers;
- shear allowable 0.5 × normal.

**NEEDS_TEST is the best verdict possible.**

**Required SF:**
- 3 for short-term loads;
- 4 for cyclic or sustained loads;
- 1.5 on yield for steel;
- 1.0 for proof loads.

**Temperature:** service is 40 °C against a softening point of about 70 °C, so it is not limiting.

## Results (`strength_calc.py` output)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | I1 bore bearing on the M3 threads, reverse stall 29.8 N | XY | 1.96 | 25.0 | 12.78 | 3.0 | OK |
| 2 | I2 bore bearing, cyclic 16.4 N | XY | 1.07 | 25.0 | 23.26 | 4.0 | OK |
| 3 | I3 bore bearing, pretension 10 N sustained (creep) | XY | 0.66 | 25.0 | 38.06 | 4.0 | OK |
| 4 | I4 bore bearing, 5 cm front corner 31.8 N | XY | 2.09 | 25.0 | 11.96 | 3.0 | OK |
| 5 | I5 disc rim bearing under a link, 5 cm front corner | XY | 1.26 | 25.0 | 19.79 | 3.0 | OK |
| 6 | I6 tooth root (chamfer top), bearing drag 0.83 N (Kt 1.8) | XY | 0.67 | 25.0 | 37.15 | 4.0 | OK |
| 7 | I7 hub end-face bearing on the wall washer, side 3 N | XY | 0.04 | 25.0 | 564.90 | 4.0 | OK |

Advisory (not in the verdict: bounds, what-ifs, fixes, proof loads, bought parts):

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| proof (§8 test 1): 4.5 kg (44 N) rearward, bore bearing | XY | 2.90 | 25.0 | 8.62 | 1.0 | OK |
| proof: reverse stall at 100 % PWM on a fresh pack 32.5 N, bore bearing | XY | 2.13 | 25.0 | 11.71 | 1.0 | OK |
| jam: stall pull 9.89 N on one idler tooth (Kt 1.8) | XY | 8.03 | 25.0 | 3.11 | 3.0 | OK |
| bore bearing, 5 cm corner, stiff landing (64 N) | XY | 4.18 | 25.0 | 5.98 | 3.0 | OK |
| S-08 ungated 196 N*mm motor at the 6.0 V cap: reverse stall 34.2 N, bore bearing | XY | 2.25 | 25.0 | 11.12 | 3.0 | OK |
| backstop if the chassis clamp yaws: hub-face edge on the wall washer, reverse stall (176 N) | XY | 44.89 | 25.0 | 0.56 | 3.0 | no |
| M3 x 40 class 12.9 bending at the wall face (chassis-owned): reverse stall 29.8 N x 17 | steel σy 1080 | 379.12 | 1080.0 | 2.85 | 1.5 | OK |
| M3 x 40 class 12.9 bending at the wall face (chassis-owned): 5 cm corner 31.8 N x 17 | steel σy 1080 | 405.30 | 1080.0 | 2.66 | 1.5 | OK |

- **Lowest SF:** 11.96 (required 3.0), at I4.
- **Drop rows:** they meet their SF up to 19.9 cm.
- **Verdict rows:** 0 of 7 are below their required SF.

## Proof tests

Spec §8 tests 1 and 2 match the NEEDS_TEST verdict. Add **one pass criterion** to test 1.

### 1. Rearward pull

**Setup:**
- Fit the idler on its bolt at mid-slot.
- Set the jack screw against the bolt head.
- Put a pen mark across the slot and the washer.
- **Before and after:** measure the distance from the idler disc's rear face to a fixed mark on the chassis (calliper or feeler).

**Load:** pull **4.5 kg (44 N, 1.5 × the 29.8 N reverse stall)** rearward along the track line for **1 min**, with a strap round the idler.

**Pass:**
- the idler still spins freely;
- axial play under 0.5 mm;
- bore ovalisation under 0.1 mm;
- the bolt hasn't moved (pen mark);
- **new:** the idler disc has moved **0.3 mm or less**, and the bolt is still square (0.5 mm runout or less at its tip).

The pen mark sits at the head and the jack screw holds the head, so the mark alone can't show the bolt yawing about the jack screw. The disc measurement can.

### 2. Chassis tests

The chassis stall test, run in reverse as well, and the 5 cm drops. Afterwards the idler must still spin freely, with the same 0.3 mm lean limit.

**Run these after the chassis clamp has been fixed** (chassis change 1). On the current clamp the reverse-stall proof (32.5 N) crushes the PETG under the head washer (chassis advisory SF 0.55).

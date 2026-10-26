# Hexapod: status

Robot 3 of 3. **Ready for your approval (26 Oct 2026).** All five printed parts have passed the printability (DFM) and strength reviews and have been sliced, validated and audited. Every strength verdict is NEEDS_TEST: the PETG strengths are placeholders until someone measures them, so each part's proof test in its `spec.md` §8 is the final check.

| Part | Job | Size (mm, as printed) | Per plate × plates | Time per plate | PETG per plate | Status |
|---|---|---|---|---|---|---|
| Bottom body plate (with columns) | `20261026-hexapod-body-bottom` | 166 × 147 × 46 | 1 × 1 | 7.8 h | 94 g | AWAITING_APPROVAL |
| Top plate / electronics deck | `20261026-hexapod-body-top` | 130 × 104 × 8 | 1 × 1 | 2.7 h | 36 g | AWAITING_APPROVAL |
| Coxa bracket (solid) | `20261026-hexapod-coxa` | 60 × 31 × 41 each | 2 × 3 | 4.4 h | 59 g | AWAITING_APPROVAL |
| Femur | `20261026-hexapod-femur` | 65 × 19 × 7 each | 3 × 2 | 2.1 h | 19.5 g | AWAITING_APPROVAL |
| Tibia | `20261026-hexapod-tibia` | 79 × 18 × 7 each | 3 × 2 | 1.9 h | 20.7 g | AWAITING_APPROVAL |

Nine plates in all: about **31.6 h and 388 g of PETG**, on the smooth PEI sheet with a thin layer of glue stick. Times and grams are from the slices made here on 26 Oct with the stock Prusa PETG profiles; your own slice may differ by a few minutes.

**Print order.** Print the first coxa plate and the first femur plate first, then do the screw-strip check (BUILD_GUIDE §1): fit a femur servo in one bracket and a tibia servo in one femur, drive both screws snug and look at the thin strips beside the screw holes. If one turns white or cracks, stop and tell Claude before printing the rest (you chose this check over moving the screw holes, 26 Oct 2026).

Read next: [BUILD_GUIDE.md](BUILD_GUIDE.md) (parts list, wiring, centring, assembly, first steps, safety), [spec.md](spec.md) (system spec and acceptance tests), [assembly_plan.md](assembly_plan.md) (frames, decisions), `assembly_check.json` and `stance_torques.json` (the checks behind them).

## To print a part

The G-code isn't stored in git, so you slice each job on your own PC first.

1. Pull this branch, then slice the job: ask Claude Code to slice it, or run `python3 tools/slice.py jobs/<job-id> --plan jobs/<job-id>/slice_plan.json`.
2. Read its `preflight.md`.
3. In your own terminal: `python3 tools/approve.py jobs/<job-id>` (agents never run this). It re-validates the G-code you just sliced.
4. Insert the SD card and ask Claude to export the job; `tools/export_sd.py` copies and verifies the file (for example `1026_hexapod_coxa.gcode`).
5. Eject the card, insert it in the printer, **Print from SD** → the file, and watch the first layer.

## Review history

- Round 2: the coxa bracket failed printability (window corners, gusset) and strength (lowest SF 0.27); the bottom plate failed strength (SF 1.71); the femur and tibia passed as NEEDS_TEST.
- Round 3 (deep reviews 01 and 05): every servo lead passes its plate (coxa and tibia servos fitted reversed, one lead notch with a moved pilot on the femur servo) and the parts use the real MG90S height. Femur, tibia and deck passed. The coxa bracket (a one-sided ledge on its notch; horn clamp SF 2.91) and the bottom plate (SF 2.03) failed for the third time, and you approved a fourth round.
- Round 4: the coxa bracket got a 45° roof over its notch and prints solid; the bottom plate got a wider strip outside each servo window, Ø10 columns and Nyloc nuts on the coxa tab screws. Both passed printability; strength NEEDS_TEST, lowest SF 4.22 (coxa) and 3.09 (bottom plate, the washer under each tab screw head: tighten by feel, dry threads).
- Slicing (26 Oct): all five pass the validator (0 errors, 0 warnings) and the audit. The femur and tibia print 3 per plate on two plates, because six on one plate takes about 3.9 h against their 3 h limit.

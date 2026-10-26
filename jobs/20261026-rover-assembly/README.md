# Tracked rover: status

Robot 2 of 3. **Ready for your approval (26 Oct 2026).** All six printed parts passed the printability (DFM) and strength reviews and are sliced, validated and audited. Every strength verdict is NEEDS_TEST: the PETG strengths are placeholders until measured, so each part's proof test (its `spec.md` §8) is the final check.

| Part | Job | Size (mm, as printed) | Per plate × plates | Time per plate | PETG per plate | Status |
|---|---|---|---|---|---|---|
| Chassis (tub) | `20261026-rover-chassis` | 154 × 92 × 40 | 1 × 1 | 11.5 h | 142 g | AWAITING_APPROVAL |
| Lid / electronics deck | `20261026-rover-lid` | 154 × 76 × 7 | 1 × 1 | 2.4 h | 34 g | AWAITING_APPROVAL |
| Drive sprocket | `20261026-rover-sprocket` | 36 × 35 × 7 each | 2 × 1 | 1.0 h | 8 g | AWAITING_APPROVAL |
| Idler | `20261026-rover-idler` | 36 × 35 × 15 each | 2 × 1 | 1.0 h | 10 g | AWAITING_APPROVAL |
| Road wheel | `20261026-rover-wheel` | 32 × 32 × 33 each | 2 × 2 | 2.3 h | 25 g | AWAITING_APPROVAL |
| Track link | `20261026-rover-track-link` | 16 × 24 × 8 each | 35 × 2 | 6.2 h | 45 g | AWAITING_APPROVAL |

Eight plates in all: about **34 h and 335 g of PETG**, on the smooth PEI sheet with a thin layer of glue stick. Build the 5-link test chain from the first track-link plate before printing the second.

**Buy before you build** (BUILD_GUIDE §1 has the full list):
- N20 gear motors with a **3 mm D-shaft 10 mm long** from the flat gearbox face (at least 9.6 mm); a 9 mm shaft is too short for the sprocket.
- **2 mm steel flat bar** (14-gauge) for the four idler clamp plates, 20.6 × 10 mm each, slotted.
- A **2.5 mm ball-end hex key** for the idler snug (0.04 N·m, plates oiled).

Read next: [BUILD_GUIDE.md](BUILD_GUIDE.md) (parts list, wiring, assembly, first drive, service), [spec.md](spec.md) (system spec and acceptance tests), [assembly_plan.md](assembly_plan.md), `assembly_check.json`.

## To print a part

The G-code isn't stored in git, so you slice each job on your own PC first.

1. Pull this branch, then slice the job: ask Claude Code to slice it, or run `python3 tools/slice.py jobs/<job-id> --plan jobs/<job-id>/slice_plan.json`.
2. Read its `preflight.md`.
3. In your own terminal: `python3 tools/approve.py jobs/<job-id>` (agents never run this). It re-validates the G-code you just sliced.
4. Insert the SD card and ask Claude to export the job; `tools/export_sd.py` copies and verifies the file (for example `1026_rover_chassis.gcode`).
5. Eject the card, insert it in the printer, **Print from SD** → the file, and watch the first layer.

## Review history

- Round 2: printability 2 of 6 pass; the chassis failed strength (SF 0.49, motor cradle lever) and the sprocket failed on its printed D-flat.
- Round 3 (deep reviews 01 and 04): the sprocket bolts to a Pololu aluminium hub (metal torque path), fully threaded class-12.9 axle bolts, a jack-screw idler tensioner. Four parts passed; the lid failed on its rails and the chassis failed a third time (idler clamp SF 0.60). You approved a fourth round.
- Round 4: a 2 mm skin in front of each motor, steel plates under the idler bolt head and nut, wider lid rails. The lid passed; the sprocket's re-check required a 10 mm motor shaft. The chassis failed again (SF 0.61, the PETG web between the plates), and you approved a fifth round.
- Round 5: the nut plate moved onto the wall's outer face and the idler's hub got 5.2 mm shorter. One row failed (the new end stop, SF 2.75), and you approved a sixth round.
- Round 6: the end stops 2 mm wide. Chassis DFM PASS, strength NEEDS_TEST (lowest SF 3.01). All six parts sliced on 26 Oct.

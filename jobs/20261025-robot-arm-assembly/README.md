# Desktop robot arm: status

Robot 1 of 3. **All 11 printed parts passed their DFM and strength reviews and are sliced, validated and audited: they await your approval (26 Oct 2026).** Strength is NEEDS_TEST for every part (the PETG allowables are placeholders until the calibration coupons are printed), so each part's spec §8 proof test is part of its acceptance. G-code isn't stored in git: slice a job on your PC (`python3 tools/slice.py jobs/<job-id>`) before approving it.

| Part | Job | Size (mm, as printed) | Print (latest slice) | Status |
|---|---|---|---|---|
| Base | `20261025-arm-base` | 110 × 104 × 40 | 8.66 h · 119.5 g | AWAITING_APPROVAL |
| Turntable support ring | `20261025-arm-turntable-ring` | 91 × 96 × 16 | 1.76 h · 16.9 g | AWAITING_APPROVAL |
| Turntable + shoulder upright | `20261025-arm-turntable` | 96 × 96 × 81 | 6.87 h · 105.3 g | AWAITING_APPROVAL |
| Upper link | `20261025-arm-upper-link` | 146 × 34 × 16 | 3.45 h · 38.6 g | AWAITING_APPROVAL |
| Forearm | `20261025-arm-forearm` | 129 × 26 × 16 | 2.55 h · 28.6 g | AWAITING_APPROVAL |
| Claw frame | `20261026-arm-claw-frame` | 43 × 64 × 48 | 3.93 h · 41.3 g | AWAITING_APPROVAL |
| Claw cover | `20261026-arm-claw-cover` | 40 × 58 × 64 | 3.57 h · 34.3 g | AWAITING_APPROVAL |
| Claw pinion (20 teeth) | `20261026-arm-claw-pinion` | 22 × 22 × 12 | 0.45 h · 4.3 g | AWAITING_APPROVAL |
| Claw jaw (× 2, one plate) | `20261026-arm-claw-jaw` | 31 × 57 × 61 each | 4.01 h · 39.5 g | AWAITING_APPROVAL |
| Brio 4K camera mount *(optional)* | `20261026-arm-camera-mount` | 40 × 32 × 50 | 1.42 h · 12.9 g | AWAITING_APPROVAL |
| ESP32 cradle | `20261025-arm-esp32-cradle` | 66 × 43 × 10 | 1.03 h · 10.8 g | AWAITING_APPROVAL |
| **Total** | | | **37.7 h · 452 g PETG** | |

Print first: the forearm and the claw frame, then do the screw-strip check (BUILD_GUIDE §1) before the rest; measure your MG996R's tab-hole spacing before the forearm. Hardware for the claw cover (round 7): M3 × 14 pan heads + Ø7 × 0.5 washers on top (or M3 × 18 button heads + Ø7 washers through the camera mount), M2.5 × 16 + DIN 125 Ø6 × 0.5 washers in front, the M3 × 45 anchor + Ø7 washer; do the seat check in BUILD_GUIDE §4 step 9.

The old gripper (`20261025-arm-gripper-base`, `-gripper-jaw`) is superseded: don't print it.

Read next: [BUILD_GUIDE.md](BUILD_GUIDE.md) (parts list, payload by reach, wiring, assembly, calibration), [spec.md](spec.md) (system spec and acceptance tests), [assembly_plan.md](assembly_plan.md) (frames, decisions, joint windows), `assembly_check.json` and `assembly_*.png` (collision and reach check, with the claw's assembly sequence in `claw_internal`), `torque_budget.json` (torques, payload, stability), `arm_test/arm_test.ino` (the sketch).

## To print a part
1. Read its `preflight.md`.
2. In your own terminal: `python3 tools/approve.py jobs/<job-id>` (agents never run this).
3. Insert the SD card and ask Claude to export the job; `tools/export_sd.py` copies and verifies the file.
4. Eject the card, insert it in the printer, **Print from SD** → the file, and watch the first layer.

## Review history
- Round 1: DFM 7/8 FAIL (no hole compensation, 10.6 mm horn-slot bridges, thin SG90 pilot walls, clearances); strength 6/8 FAIL (sideways loads not in the specs; links held on their horns by two small screws).
- Round 2: horn clamp screws, thicker plates, pocket-up printing, HOLE_COMP everywhere: DFM 5/8 PASS, strength 7/8 NEEDS_TEST.
- Round 3 of the arm parts: turntable washer clearance, M3×10 cradle screws, M2×12 wrist screws: all PASS / NEEDS_TEST.
- Claw v2, round 1 (2026-10-26): DFM and strength FAIL on all five claw jobs; deep reviews 01 (bought parts) and 03 (arm system) found the servo leads can't pass their windows, the MG90S output sits 3 mm higher than modelled, and the claw can't be assembled.
- Arm round 3 / claw round 2 (2026-10-26): the redesign above, verified by `assembly_check.py` and `claw_sequence_check.py`. Claw DFM and strength round 2: camera mount passed; frame, cover, jaw and pinion failed.
- Claw round 3 (2026-10-26): rail block and ribs on the frame, 8 mm lip, second tie and support pillars on the cover, 12 mm racks and pinion, true 0.25 mm gear chamfers, shorter grip grooves; reviews pending.
- Links rounds 4–6 and claw rounds 3–7 (2026-10-26): ribs, pads, gussets and washers on the links; on the claw a rail block, ribs, an 8 mm lip, support pillars, an M3 × 45 anchor for the cover's second post seated in a V-groove (ridge-first contact, bulkhead top moved off a slice plane), and washers with longer screws on the cover. Every part now passes DFM and strength (NEEDS_TEST).

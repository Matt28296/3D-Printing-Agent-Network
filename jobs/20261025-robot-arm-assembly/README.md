# Desktop robot arm: status

Robot 1 of 3. **Don't approve or print anything yet (26 Oct 2026).** Round 3 answers deep reviews 01 and 03 and the claw's first DFM and strength round: lead notches in every servo window, the real MG90S height, the claw's new assembly order (pinion last, through the cover's front plate), the re-centred elbow window, the disc horn under the turntable and a 0.4 mm ring gap. Every part except the cradle changed, so their DFM and strength reviews run again, and their G-code (sliced from the old geometry) is stale. The table is the round-3 CAD; print times and filament come back with the re-slice.

| Part | Job | Size (mm, as printed) | PETG, solid (g) | Status |
|---|---|---|---|---|
| Base | `20261025-arm-base` | 110 × 104 × 40 | 114 | DESIGN round 3 (lead notches) |
| Turntable support ring | `20261025-arm-turntable-ring` | 91 × 96 × 16 | 17 | DESIGN round 3 (0.4 mm gap) |
| Turntable + shoulder upright | `20261025-arm-turntable` | 96 × 96 × 81 | 113 | DESIGN round 3 (lead notches, disc horn) |
| Upper link | `20261025-arm-upper-link` | 146 × 34 × 10 | 50 | DESIGN round 3 (lead notches) |
| Forearm | `20261025-arm-forearm` | 129 × 26 × 10 | 37 | DESIGN round 3 (MG90S window, lead notch) |
| Claw frame | `20261026-arm-claw-frame` | 43 × 64 × 48 | 59 | DESIGN round 3 (claw) |
| Claw cover | `20261026-arm-claw-cover` | 40 × 58 × 64 | 40 | DESIGN round 3 (claw) |
| Claw pinion (20 teeth) | `20261026-arm-claw-pinion` | 22 × 22 × 12 | 4.2 | DESIGN round 3 (claw) |
| Claw jaw (× 2, one plate) | `20261026-arm-claw-jaw` | 31 × 57 × 61 each | 2 × 21.7 | DESIGN round 3 (claw) |
| Brio 4K camera mount *(optional)* | `20261026-arm-camera-mount` | 40 × 32 × 50 | 13 | DESIGN passed (round 2) |
| ESP32 cradle | `20261025-arm-esp32-cradle` | 66 × 43 × 10 | 15 | AWAITING_APPROVAL (unchanged) |

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

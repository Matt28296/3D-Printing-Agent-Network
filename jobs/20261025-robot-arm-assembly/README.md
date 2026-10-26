# Desktop robot arm: status

Robot 1 of 3. **Don't approve or print anything yet (26 Oct 2026).** The deep review found that no servo lead can pass its closed window, and that the MG90S output sits 3.2 mm higher than modelled. The base, turntable, upper link and forearm are back in DESIGN for lead notches. The gripper below was replaced by the parallel claw and Brio camera mount (`jobs/20261026-arm-claw-*`, `jobs/20261026-arm-camera-mount`), which are in their second design round. The table below is the state before the deep review; it is regenerated when the round passes.

| Part | Job | Size (mm, as printed) | Print time | PETG | DFM | Strength | G-code audit | SD-card file |
|---|---|---|---|---|---|---|---|---|
| Base | `20261025-arm-base` | 110 × 104 × 40 | 8.08 h | 97.6 g | PASS | NEEDS_TEST | PASS | `1025_arm_base.gcode` |
| Turntable support ring | `20261025-arm-turntable-ring` | 91 × 96 × 15 | 1.23 h | 14.1 g | PASS | NEEDS_TEST | PASS | `1025_arm_turntable_ring.gcode` |
| Turntable + shoulder upright | `20261025-arm-turntable` | 96 × 96 × 81 | 6.76 h | 77.0 g | PASS | NEEDS_TEST | PASS | `1025_arm_turntable.gcode` |
| Upper link | `20261025-arm-upper-link` | 146 × 34 × 10 | 2.98 h | 33.9 g | PASS | NEEDS_TEST | PASS | `1025_arm_upper_link.gcode` |
| Forearm | `20261025-arm-forearm` | 129 × 26 × 10 | 2.21 h | 25.1 g | PASS | NEEDS_TEST | PASS | `1025_arm_forearm.gcode` |
| Gripper base + fixed jaw | `20261025-arm-gripper-base` | 108 × 25 × 25 | 1.90 h | 20.9 g | PASS | NEEDS_TEST | PASS | `1025_arm_gripper_base.gcode` |
| Moving jaw | `20261025-arm-gripper-jaw` | 63 × 16 × 8 | 0.55 h | 6.2 g | PASS | NEEDS_TEST | PASS | `1025_arm_gripper_jaw.gcode` |
| ESP32 cradle | `20261025-arm-esp32-cradle` | 66 × 43 × 10 | 1.03 h | 10.8 g | PASS | NEEDS_TEST | PASS | `1025_arm_esp32_cradle.gcode` |
| **Total** | | | **24.7 h** | **285 g** | | | | |

Read next: [BUILD_GUIDE.md](BUILD_GUIDE.md) (parts list, wiring, assembly, proof tests), [assembly_plan.md](assembly_plan.md) (frames, decisions, joint ranges), `assembly_check.json` and `assembly_*.png` (collision and reach check), `arm_test/arm_test.ino` (servo centring sketch).

## To print a part
1. Read its `preflight.md`.
2. In your own terminal: `python3 tools/approve.py jobs/<job-id>` (agents never run this).
3. Insert the SD card and ask Claude to export the job; `tools/export_sd.py` copies and verifies the file.
4. Eject the card, insert it in the printer, **Print from SD** → the file, and watch the first layer.

## Review history
- Round 1: DFM 7/8 FAIL (no hole compensation, 10.6 mm horn-slot bridges, thin SG90 pilot walls, clearances); strength 6/8 FAIL (sideways loads not in the specs; links held on their horns by two small screws).
- Round 2: horn clamp screws, thicker plates, pocket-up printing, HOLE_COMP everywhere: DFM 5/8 PASS, strength 7/8 NEEDS_TEST.
- Round 3: turntable washer clearance, M3×10 cradle screws, M2×12 wrist screws: all PASS / NEEDS_TEST.

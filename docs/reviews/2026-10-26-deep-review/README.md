# Deep review, 26 October 2026

Five independent reviewers each took one slice of all three robot test builds: the desktop arm, the tracked rover and the hexapod. This was on top of each part's own printability (DFM) and strength reviews. No reviewer had worked on the designs. Each one read the CAD, the specs, the build guides and the firmware, and checked numbers with their own scripts.

## Reports

| Report | Slice | Blockers | Should fix | Notes | Headline |
|---|---|---|---|---|---|
| [01](01-bought-parts.md) | Bought parts and bills of materials | 2 | 15 | 8 | No servo lead can pass its closed window (all 23), and the MG90S output sits about 3 mm higher above its tabs than the parts library assumed |
| [02](02-electronics-firmware.md) | Wiring, power and firmware | 2 | 20 | 16 | The arm's stop command didn't cancel a move, and opening the PC port reset the arm to its boot pose at full speed |
| [03](03-arm-system.md) | The arm as a machine | 1 | 10 | 8 | The new claw can't be assembled as drawn. With the camera, the shoulder holds 42–54 % of stall at full reach |
| [04](04-rover-system.md) | The rover as a machine | 1 | 12 | 11 | Sound as a machine, but the class-12.9 axle bolts are threaded only on their last 18 mm and can't reach the trap nuts |
| [05](05-hexapod-system.md) | The hexapod as a machine | 0 | 6 | 8 | The geometry works. At 662 g each femur servo holds 51–59 % of stall; an IK gait with tucked tibias brings that to 36–42 % |
| | **Total** | **6** | **63** | **51** | |

## The blockers and where they stand

| ID | Robot | Finding | Fix | Status |
|---|---|---|---|---|
| 01-B1 | Arm, hexapod | No servo lead can pass its closed window | `servo_mount_cutter(lead=...)` in `tools/hobby_parts.py` cuts a lead notch; MG90S windows shift the pilot | Library done (merged). Applying to the arm links and claw (arm round) and the hexapod (round 3) |
| 01-B2 | Arm, hexapod | MG90S spline top is 14.0 mm above the tabs, not 10.8 | MG90S has its own spec in `hobby_parts.py` | Library done (merged). Wrist, claw and hexapod geometry being rebuilt |
| 02-A1 | Arm | `x` stopped a move, but the next command finished it | Cancel clears the target | Fixed and merged |
| 02-A2 | Arm | Opening the PC port reset the ESP32, which snapped every joint to boot | Pose kept in NVS; slow start from it; port opened without reset | Fixed and merged |
| 03-SYS-01 | Arm | The claw has no assembly or service sequence that works | Ø ≥ 20.6 mm pinion pass-through in the front plate; pinion fitted last with the jaws parked open | Arm round in progress |
| 04-S-01 | Rover | Partly threaded M3 × 45 and × 35 bolts can't engage the wall trap nuts | Fully threaded bolts, or a changed clamp | Rover round 3 in progress |

## How the fixes flow

- Each finding goes back into the job it affects, and that job reopens to DESIGN. The reopened arm links say so in their `status.json` and `log.md`.
- After a design round, fresh reviewers repeat the DFM and strength reviews. A part moves on to slicing only when both pass. The usual three-iteration limit still applies: a part that fails a gate three times goes to you.
- Should-fix items that are documentation (build guides, plans, specs) are fixed in the same round as the CAD.
- Notes are kept for reference. Some became build-guide tips, for example the camera focus distance or a spare track link.
- Nothing from the robots is ready to print until its parts pass again. The robot READMEs say so.

## Where the work is

| Robot | Round | Covers |
|---|---|---|
| Arm, mechanical | Links round 4, claw round 2 | 01-B1/B2/S2–S8, 03 (SYS-01 to SYS-05, SYS-08 to SYS-10, SYS-12, SYS-16 to SYS-18), claw DFM and strength round 1 |
| Arm, firmware | Firmware round 2 | 03 SYS-02/03 (elbow window), SYS-06 (motion profiles), SYS-07 (trims and calibration), SYS-11, SYS-13 |
| Rover | Round 3 | DFM and strength round 2, 01-S9 to S13, 04 |
| Hexapod | Round 3 | Coxa redesign, 01-B1/B2/S14/S15, 05 |
| All | Firmware round 1 | 02 (done and merged) |

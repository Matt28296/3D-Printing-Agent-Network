# Assembly plan: desktop robot arm (5 servos, ESP32)

Robot 1 of 3 (then tracked rover, then hexapod). Architect: Claude, 2026-10-25.
The user left motors, power and material to the designer.

## Decisions

| Item | Choice | Why |
|---|---|---|
| Layout | 4-DOF arm + gripper: base yaw, shoulder pitch, elbow pitch, wrist pitch, gripper | The classic desktop arm; every printed part is a flat plate, printed flat, so bending runs along the layers |
| Big joints | 3 × MG996R (base, shoulder, elbow) | Metal gears, ≈1000 N·mm stall at 6 V, standard size, cheap |
| Small joints | 2 × SG90 (wrist, gripper) | Light, which keeps the shoulder load low |
| Controller | ESP32 DevKit (30 or 38 pin) in a cradle inside the base | User's choice. The ESP32 drives all 5 servos directly with LEDC PWM |
| Power | 6 V 5 A DC adapter, 5.5 × 2.1 mm plug; panel jack (Ø11 mm hole) in the base; ESP32 fed from 5 V USB or a 5 V buck | Servos stall at up to ~2.5 A each, so they must not run from the ESP32's 5 V pin |
| Material | PETG (Prusament PETG profile) | Tough, low creep, no enclosure needed |
| Fasteners | Servo tab screws (supplied with the servos) into printed pilot holes; 3 × M3×8 self-tapping for the ring; 3 × M3×8 for the cradle; 4 × M3 wood screws for the desk (optional) | All screws self-tap into PETG |
| Horns | MG996R **double-arm** horn and SG90 single-arm horn (both in the servo bags), each seated 2 mm deep in a slot pocket on the link's back face (the turntable has none: the base horn sits flat on its underside) | The slot carries torque on its walls; a Ø25 disc pocket would need a 25 mm bridge. The pocketed links print pocket-up (upper link, forearm) or bridge ≤ 7.9 mm (SG90 parts). **A longer centre screw + washer goes through each link into the spline** (M3×16 + Ø9 washer on MG996R joints, M2×12 + Ø6 on SG90 joints), clamping link and horn together; small screws through the horn arm holes stop rotation (strength round 1: the stock screw clamps only the horn) |

## Shared frame (every model.py follows it)

Origin: the base-servo shaft axis on the **top surface of the base top plate**. Z up. The desk is at Z = −40.

Each link's frame has its origin on its joint axis at the link's **back face** (servo side). The back face sits at `link_back_z = horn face − 2 mm`, so the horn is 2 mm deep in its pocket (`tools/hobby_parts.py`).

| Joint | Servo | Servo-frame origin (tab underside, on the axis) | Axis | Horn face | Next link's back face |
|---|---|---|---|---|---|
| Base yaw | MG996R | (0, 0, 0) | +Z | Z = 16.5 | turntable underside Z = 16.5 (no pocket) |
| Shoulder | MG996R | (10.15, −5, 60.5); body **horizontal** along X, centred on the yaw axis | +Y | Y = 11.5 | upper link Y = 9.5 |
| Elbow | MG996R | upper link (100, 0, 10); body along link +x | link +z | link z = 26.5 | forearm at link z = 24.5 |
| Wrist | SG90 | forearm (90, 0, 10) | forearm +z | forearm z = 21.4 | gripper base at forearm z = 19.4 |
| Gripper | SG90 | gripper base (40, 0, 8) | +z | gripper z = 19.4 | jaw at gripper z = 17.4 |

Plate thicknesses (strength round 1): turntable disk 8, upright 7; upper link 10; forearm 10; gripper base 8; jaw 8.

Link lengths: shoulder→elbow 100 mm, elbow→wrist 90 mm, wrist→fingertip 95 mm. The shoulder axis is 100.5 mm above the desk. Each link mounts on the front of the previous servo, so the arm plane steps out in +Y (fingertip at Y ≈ 75). The yaw target must allow for that offset. Static moments with a 50 g payload, arm straight out: ≈410 N·mm at the shoulder (41 % of MG996R stall), ≈180 at the elbow. **The base must be screwed down**: with the arm out it tips over (358 vs 147 N·mm).

## Assembly check (`assembly_check.py` → `assembly_check.json`, `assembly_*.png`)

All 8 printed parts, 5 servo dummies, the ESP32 board and the desk, placed per pose; pairwise overlap volume by mesh boolean (> 1 mm³ = collision).

| Joint (0 = straight / horizontal, + = up / open) | Collision-free range found | Use (servo 180°) |
|---|---|---|
| Shoulder (elbow 0) | −10° … 180° (desk at −20°) | 0° … 180° |
| Elbow (shoulder 60) | −140° … +170° | −90° … +90° |
| Wrist (shoulder 45, elbow −45) | −150° … +150° | −90° … +90° |
| Gripper | 0° … 60° (below 0 the jaws overlap: 0 = closed) | 0° … 60° |

Reach (round 2 geometry): 304 mm from the yaw axis at full horizontal extension; collision-free poses put the fingertip on the desk from 75 mm to 236 mm out. Every named pose is collision-free except a deliberate 150° fold-down of the elbow, which is outside the servo's range.

## Printed pieces

| # | Job | Piece | Orientation | Mates with | Clearance |
|---|---|---|---|---|---|
| 0 | arm-fit-test | *(optional)* horn pocket + servo window coupon | flat | MG996R horn, SG90 horn, both servo bodies | 0.4 window, 0.5 horn pocket |
| 1 | 20261025-arm-base | Base: 110 × 104 × 40 box, open bottom | upside down (top plate on bed) | base servo, ring, cradle, DC jack | 0.4 servo window |
| 2 | 20261025-arm-turntable-ring | Support ring r 41–44.5, 13 tall + 3 tabs | flat | base top, turntable underside (1.5 mm running gap) | 1.5 axial |
| 3 | 20261025-arm-turntable | Disk Ø96 + 66 mm upright + gussets | disk on bed | base horn, shoulder servo | 0.5 horn, 0.4 window |
| 4 | 20261025-arm-upper-link | Link 100 mm, 6 thick | flat | shoulder horn, elbow servo | 0.5 / 0.4 |
| 5 | 20261025-arm-forearm | Link 90 mm, 5 thick | flat | elbow horn, wrist SG90 | 0.5 / 0.4 |
| 6 | 20261025-arm-gripper-base | Plate + fixed jaw | flat | wrist horn, gripper SG90 | 0.5 / 0.4 |
| 7 | 20261025-arm-gripper-jaw | Moving jaw | flat | gripper horn | 0.5 |
| 8 | 20261025-arm-esp32-cradle | Tray for the ESP32 | flat | base bosses, ESP32 board | 0.6 around the PCB |

**Before printing, measure your servos.** The servo dimensions are nominal datasheet values (`tools/hobby_parts.py`); brands differ by up to ~1 mm. Measure: body length and width, tab-hole spacing, shaft-to-body-end distance, and the horns (double-arm hub Ø, centre-to-tip length and tip width; SG90 arm the same). Put any differences into `replace(MG996R, ...)` in each model.py.

## Status

| # | Piece | Status |
|---|---|---|
| 1–8 | all | round 2: DFM (7 FAIL) and strength (6 FAIL, 2 NEEDS_TEST) round-1 findings applied, rebuilt, mesh-checked, assembly re-checked; round-2 reviews next |

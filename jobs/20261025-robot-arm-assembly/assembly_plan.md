# Assembly plan: desktop robot arm (5 servos, ESP32, parallel claw, optional Brio 4K)

Robot 1 of 3 (then tracked rover, then hexapod). Architect: Claude, 2026-10-25.
The user left motors, power and material to the designer.

## Decisions

| Item | Choice | Why |
|---|---|---|
| Layout | 4-DOF arm + claw: base yaw, shoulder pitch, elbow pitch, wrist pitch, parallel claw | The classic desktop arm; the links are flat plates printed flat, so bending runs along the layers |
| Big joints | 3 × MG996R (base, shoulder, elbow) | Metal gears, ≈1000 N·mm stall at 6 V, standard size, cheap |
| Small joints | 2 × MG90S (wrist, claw) | SG90 size and weight class but metal gears (≈216 N·mm at 6 V): they hold a grip and the camera without stripping (claw v2, 2026-10-26; the SG90s were replaced) |
| Claw (v2, user request 2026-10-26) | Rack-and-pinion parallel claw: an 18-tooth module-1 pinion on the claw MG90S drives two identical racks the opposite ways; each rack carries a finger | The old claw was one SG90 swinging a bar against a fixed block (≈3 N at the tip, V-shaped opening). Now both fingers move, stay parallel and self-centre: 0–44 mm, ≈12 N per finger at stall, force the same along the finger |
| Wrist camera (user request 2026-10-26) | Optional Logitech Brio 4K on a mount on the claw's top, 30° nose-down at the fingertips; USB to the PC | The user chose the wrist (eye-in-hand). The ESP32 has no USB host, so the PC runs vision and sends serial commands (`arm_test.ino` `m`/`?`/`x`, `pc/arm_pc_control.py`) |
| Controller | ESP32 DevKit (30 or 38 pin) in a cradle inside the base | User's choice. The ESP32 drives all 5 servos directly with LEDC PWM |
| Power | 6 V 5 A DC adapter, 5.5 × 2.1 mm plug; panel jack (Ø11 mm hole) in the base; ESP32 fed from 5 V USB or a 5 V buck | Servos stall at up to ~2.5 A each, so they must not run from the ESP32's 5 V pin |
| Material | PETG (Prusament PETG profile) | Tough, low creep, no enclosure needed |
| Fasteners | Servo tab screws (supplied with the servos) into printed pilots (Ø2.6 MG996R, Ø1.5 SG90; check against the actual screws); 3 × M3×6 self-tapping for the ring; 3 × M3×10 for the cradle (from below, counterbored); horn clamp screws M3×16 + Ø9 washer (×3) and M2×12 + Ø6 washer (×2); 4 × M3×50 wood screws through the corner pillars, **required** (the arm tips the base) | All screws self-tap into PETG |
| Horns | MG996R **double-arm** horn and SG90 single-arm horn (both in the servo bags), each seated 2 mm deep in a slot pocket on the link's back face (the turntable has none: the base horn sits flat on its underside) | The slot carries torque on its walls; a Ø25 disc pocket would need a 25 mm bridge. The pocketed links print pocket-up (upper link, forearm) or bridge ≤ 7.9 mm (SG90 parts). **A longer centre screw + washer goes through each link into the spline** (M3×16 + Ø9 washer on MG996R joints, M2×12 + Ø6 on SG90 joints), clamping link and horn together; small screws through the horn arm holes stop rotation (strength round 1: the stock screw clamps only the horn) |

## Shared frame (every model.py follows it)

Origin: the base-servo shaft axis on the **top surface of the base top plate**. Z up. The desk is at Z = −40.

Each link's frame has its origin on its joint axis at the link's **back face** (servo side). The back face sits at `link_back_z = horn face − 2 mm`, so the horn is 2 mm deep in its pocket (`tools/hobby_parts.py`).

| Joint | Servo | Servo-frame origin (tab underside, on the axis) | Axis | Horn face | Next link's back face |
|---|---|---|---|---|---|
| Base yaw | MG996R | (0, 0, 0) | +Z | Z = 16.5 | turntable underside Z = 16.5 (no pocket) |
| Shoulder | MG996R | (10.15, −5, 60.5); body **horizontal** along X, centred on the yaw axis | +Y | Y = 11.5 | upper link Y = 9.5 |
| Elbow | MG996R | upper link (100, 0, 10); body along link +x | link +z | link z = 26.5 | forearm at link z = 24.5 |
| Wrist | MG90S | forearm (90, 0, 10) | forearm +z | forearm z = 21.4 | claw frame at forearm z = 19.4 (claw frame G) |
| Claw | MG90S | claw frame G (10, 0, 22.5), body along y | G +x | G x = 21.4 | pinion back face at G x = 19.4; racks slide along y |

Plate thicknesses (strength round 1): turntable disk 8, upright 7; upper link 10; forearm 10. Claw (v2): wrist plate 6, bulkhead 6, cover walls 3, finger blades 6. Shared claw geometry: `claw_frame.py`.

Link lengths: shoulder→elbow 100 mm, elbow→wrist 90 mm, wrist→fingertip 76 mm (claw v2; was 95). The shoulder axis is 100.5 mm above the desk. Each link mounts on the front of the previous servo, so the arm plane steps out in +Y (fingertips at Y ≈ 76); the camera sits further out, at Y ≈ 95–140. The yaw target must allow for that offset.

Static servo torques, arm straight out (Architect's estimate from the parts' volumes; the strength re-check in `20261026-arm-claw-frame/strength.md` is the reference): without the camera, shoulder ≈410 N·mm (41 % of MG996R stall) with 50 g; with the Brio, ≈420 / 470 / 550 N·mm with 0 / 20 / 50 g (42–55 %), elbow ≈160–245, wrist ≤ 50 (≤ 22 % of MG90S). Payload rating: 50 g without the camera, 20 g at full reach with it. **The base must be screwed down**: with the arm out it tips over.

## Assembly check (`assembly_check.py` → `assembly_check.json`, `assembly_*.png`)

Every printed part (claw v2: frame, cover, pinion, both jaws, camera mount), 5 servo dummies, the ESP32 board, the Brio 4K and the desk, placed per pose; pairwise overlap volume by mesh boolean (> 1 mm³ = collision). The claw's own fit (pinion and racks in mesh over 0–44 mm, jaws clear of the cover, a 5° mis-phased pinion collides) was checked separately while designing it.

| Joint (0 = straight / horizontal, + = up / open) | Collision-free range found | Use (servo 180°) |
|---|---|---|
| Shoulder (elbow 0) | −10° … 180° (desk at −20°) | 0° … 180° |
| Elbow (shoulder 60) | −170° … +170° | −90° … +90° |
| Wrist (shoulder 45, elbow −45) | −150° … +150° (camera fitted) | −90° … +90° |
| Claw | 0 … 44 mm (0 = fingers touching) | 0 … 44 mm (140° of servo) |

Reach (claw v2): 284 mm from the yaw axis at full horizontal extension; collision-free poses put the fingertips on the desk from 76 mm to 260 mm out. Every named pose is collision-free, including the elbow folded ±150° and the wrist at −150° with the camera passing over the forearm (the camera sits outboard of every other part).

## Printed pieces

| # | Job | Piece | Orientation | Mates with | Clearance |
|---|---|---|---|---|---|
| 0 | arm-fit-test | *(optional)* horn pocket + servo window coupon | flat | MG996R horn, MG90S horn, both servo bodies | 0.4 window, 0.5 horn pocket |
| 1 | 20261025-arm-base | Base: 110 × 104 × 40 box, open bottom | upside down (top plate on bed) | base servo, ring, cradle, DC jack | 0.4 servo window |
| 2 | 20261025-arm-turntable-ring | Support ring r 41–44.5, 13 tall + 3 tabs | flat | base top, turntable underside (1.5 mm running gap) | 1.5 axial |
| 3 | 20261025-arm-turntable | Disk Ø96 + 66 mm upright + gussets | disk on bed | base horn, shoulder servo | 0.5 horn, 0.4 window |
| 4 | 20261025-arm-upper-link | Link 100 mm, 10 thick | flat, pocket up | shoulder horn, elbow servo | 0.5 / 0.4 |
| 5 | 20261025-arm-forearm | Link 90 mm, 10 thick | flat, pocket up | elbow horn, wrist MG90S | 0.5 / 0.4 |
| 6 | 20261026-arm-claw-frame | Wrist plate + bulkhead + lower rail | back face down | wrist horn, claw MG90S, rack B, cover | 0.5 / 0.4 / 0.25 sliding |
| 7 | 20261026-arm-claw-cover | Front plate + top wall + lip, 2 neck slots | standing on its end | frame, both racks, camera mount | 0.25 sliding |
| 8 | 20261026-arm-claw-pinion | 18 T module-1 gear, trimmed-horn pocket | flat | claw horn (arms cut to 5.5), both racks | 0.3 pocket, 0.2 backlash |
| 9–10 | 20261026-arm-claw-jaw ×2 | Rack + neck + finger, identical | standing, finger up | pinion, frame/cover channels | 0.25 sliding |
| 11 | 20261026-arm-camera-mount | *(optional)* Brio 4K seat, 30° | standing on its end | cover top, camera (1/4"-20) | 0.3 lip |
| — | ~~20261025-arm-gripper-base / -gripper-jaw~~ | superseded by claw v2 | | | |
| 12 | 20261025-arm-esp32-cradle | Tray for the ESP32 | flat | base bosses, ESP32 board | 0.6 around the PCB |

**Before printing, measure your servos.** The servo dimensions are nominal datasheet values (`tools/hobby_parts.py`); brands differ by up to ~1 mm. Measure: body length and width, tab-hole spacing, shaft-to-body-end distance, and the horns (double-arm hub Ø, centre-to-tip length and tip width; MG90S arms the same, plus the arm width near the hub). Put any differences into `replace(MG996R, ...)` in each model.py.

## Status

| # | Piece | Status |
|---|---|---|
| 1–5, 12 | base, ring, turntable, upper link, forearm, cradle | AWAITING_APPROVAL: DFM PASS, strength NEEDS_TEST (proof tests in §8), G-code audit PASS (round 3); strength re-check for the heavier claw v2 + camera in progress |
| 6–11 | claw v2 + camera mount | DESIGN: models built, assembly check clean; DFM and strength reviews in progress |
| — | old gripper base / jaw | SUPERSEDED (kept for the record; don't print) |

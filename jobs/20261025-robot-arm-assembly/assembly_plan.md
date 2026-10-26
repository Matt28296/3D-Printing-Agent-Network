# Assembly plan: desktop robot arm (5 servos, ESP32, parallel claw, optional Brio 4K)

Robot 1 of 3 (then tracked rover, then hexapod). Architect: Claude, 2026-10-25; round 3 (deep reviews 01 and 03, claw DFM and strength round 1): 2026-10-26.
The user left motors, power and material to the designer. The system spec, with its acceptance tests, is [spec.md](spec.md).

## Decisions

| Item | Choice | Why |
|---|---|---|
| Layout | 4-DOF arm + claw: base yaw, shoulder pitch, elbow pitch, wrist pitch, parallel claw | The classic desktop arm; the links are flat plates printed flat, so bending runs along the layers |
| Big joints | 3 × MG996R (base, shoulder, elbow) | Metal gears, ≈1000 N·mm stall at 6 V, standard size, cheap |
| Small joints | 2 × MG90S (wrist, claw) | Metal gears (216 N·mm at 6 V): they hold a grip and the camera without stripping. Own `ServoSpec` since deep review 01: body 22.8 × 12.2, spline top 14.0 above the tabs (B2, S1) |
| Claw (v2, user request 2026-10-26; round 3) | Rack-and-pinion parallel claw: a 20-tooth module-1 pinion on the claw MG90S drives two identical racks the opposite ways; each rack carries a finger | Both fingers move, stay parallel and self-centre: 0–44 mm in 126° of servo (2.865°/mm). At stall the pinion pushes 21.6 N into the racks, 10.8 N per jaw when both grip (the safety figure); rack friction leaves a real grip of about 5–7.5 N per finger (03 SYS-15's 6–8.5 N scaled from pitch radius 9 to 10) |
| Claw assembly (03 SYS-01, fix A) | Frame → claw servo from the front → cover → camera mount → both jaws slid in from the open slot ends to fully open → pinion pushed in last, axially, through a Ø22.6 hole in the cover's front plate | The jaws can't pass the mesh and the cover can't go over fitted jaws. Service is the reverse, pinion first. `claw_sequence_check.py` proves every step with exact solids |
| Wrist camera (user request 2026-10-26) | Optional Logitech Brio 4K on a mount on the claw's top, 34° nose-down at the fingertips; USB-C (right-angle plug on its back) to the PC | The user chose the wrist (eye-in-hand). The ESP32 has no USB host, so the PC runs vision and sends serial commands (`arm_test.ino`, `pc/arm_pc_control.py`) |
| Controller | ESP32 DevKit (30 or 38 pin) in a cradle inside the base | User's choice. The ESP32 drives all 5 servos directly with LEDC PWM |
| Power | 6 V 5 A DC adapter, 5.5 × 2.1 mm plug; panel jack (Ø11 mm hole) in the base; fuse, switch lead; stripboard power bus with 3-pin headers; ESP32 from its USB port | Servos stall at up to ~2.5 A each: their power never runs through the ESP32 or Dupont jumpers (01 S8) |
| Material | PETG (Prusament PETG profile) | Tough, low creep, no enclosure needed |
| Fasteners | MG996R tabs: 12 × M3 × 12 pan-head self-tapping + Ø7 washers, no grommets (01 S3). MG90S tabs: 2 × M2 × 12 (forearm), 2 × M2 × 8 (claw), the lead-end tab's slit filed to 2.1 mm. Horn clamps: 3 × M3 × 14 socket head + Ø9 × 0.8 washer (base, shoulder, elbow) and 2 × M2 × 12 + Ø6 washer (wrist, pinion): **each reaches 4.6 mm into its spline** (01 S2). 7 × M2 × 6 horn anti-rotation screws (01 S4). Ring 3 × M3 × 6; cradle 3 × M3 × 10; claw cover 2 × M3 × 10 top (M3 × 18 button heads through the camera mount) and 2 × M2.5 × 12 front; 4 × M3 × 50 wood screws through the corner pillars, **required** (the arm tips the base) | All screws self-tap into PETG. Full list: BUILD_GUIDE §1 |
| Horns | Base: MG996R **Ø25 disc** horn flat on the turntable's underside (03 SYS-05). Shoulder and elbow: MG996R **double-arm** horns in 2 mm slot pockets on the links' back faces. Wrist: MG90S single-arm horn in the claw frame's back-face pocket. Pinion: MG90S double-arm horn with both arms cut to 5.5 mm, in a light 0.1 mm fit pocket (03 SYS-08) | A longer centre screw + washer goes through each link into the spline and clamps link and horn together; small screws through the horn holes stop rotation |

## Shared frame (every model.py follows it)

Origin: the base-servo shaft axis on the **top surface of the base top plate**. Z up. The desk is at Z = −40.

Each link's frame has its origin on its joint axis at the link's **back face** (servo side). The back face sits at `link_back_z = horn face − 2 mm`, so the horn is 2 mm deep in its pocket (`tools/hobby_parts.py`).

| Joint | Servo | Servo-frame origin (tab underside, on the axis) | Axis | Horn face | Next link's back face |
|---|---|---|---|---|---|
| Base yaw | MG996R | (0, 0, 0) | +Z | Z = 16.5 | turntable underside Z = 16.5 (no pocket) |
| Shoulder | MG996R | (10.15, −5, 60.5); body **horizontal** along X, centred on the yaw axis | +Y | Y = 11.5 | upper link Y = 9.5 |
| Elbow | MG996R | upper link (100, 0, 10); body along link +x | link +z | link z = 26.5 | forearm at link z = 24.5 |
| Wrist | MG90S | forearm (90, 0, 10) | forearm +z | forearm z = 24.6 | claw frame at forearm z = 22.6 (claw frame G) |
| Claw | MG90S | claw frame G (10, 0, 27.25), body along y | G +x | G x = 24.6 | pinion back face at G x = 22.6; racks slide along y |

Plate thicknesses: turntable disk 8, upright 7; upper link 10; forearm 10. Claw: wrist plate 6 (+ 2.3 pad behind the bulkhead), bulkhead 6.5, rail and lip walls 4, cover front plate 5, top wall 3, fingers 12 → 6. Shared claw geometry: `claw_frame.py`.

Link lengths: shoulder→elbow 100 mm, elbow→wrist 90 mm, wrist→fingertip 83 mm (round 3; was 76). The shoulder axis is 100.5 mm above the desk. Each link mounts on the front of the previous servo, so the arm plane steps out in +Y: the claw's back face is at Y 56.6 and the fingertips at Y ≈ 84; the camera's centre of mass sits at Y ≈ 136, and the camera with its plug reaches Y ≈ 155. The yaw target must allow for that offset.

**Torque budget and payload** (`torque_budget.py` → `torque_budget.json`, deep review 03 SYS-02 method, round-3 claw): the end effector beyond the wrist horn weighs ≈209 g with the camera (sliced estimate; 224 g with solid parts), ≈124 g without it. Worst static shoulder torque, arm straight out: 553 N·mm with the camera and no payload (51 % of the MG996R's 1079 N·mm stall at 6 V), 683 N·mm with 50 g (63 %); without the camera 391 / 520 N·mm (36 / 48 %). Elbow ≤ 314 N·mm (29 %), wrist ≤ 63 N·mm (29 % of the MG90S). The payload-by-reach table in BUILD_GUIDE (header) replaces the old single ratings: with the camera, nothing is safe to hold straight out, ≈160 g can be lifted at 140–160 mm, ≈50 g at 180–200 mm. **Park upright** (`r`: shoulder 90, elbow 0, wrist 0), where the shoulder holds almost nothing; the sketch parks by itself after 60 s idle. **The base must be screwed down** (or on a 200 × 200 mm, 0.4 kg board): with the arm out it tips over.

## Assembly check (`assembly_check.py` → `assembly_check.json`, `assembly_*.png`)

Every printed part (claw: frame, cover, pinion, both jaws, camera mount), 5 servo dummies, the ESP32 board, the Brio 4K with a right-angle USB-C plug on its back and the thumb screw under its seat, and the desk, placed per pose; pairwise overlap volume by mesh boolean (> 1 mm³ = collision). The claw's own assembly sequence and running fit are checked with exact solids by `claw_sequence_check.py`, which `assembly_check.py` runs (`claw_internal` in the json): every insertion path (servo from the front with its lead, cover and camera mount lowered, each jaw slid in to fully open), the pinion's axial path as one swept solid, the stroke every 1 mm and one tooth pitch in 0.1 mm steps: 0 mm³ (strict tolerance 0.001 mm³), and the backlash measured per mesh.

| Joint (0 = straight / horizontal, + = up / open) | Collision-free range found | Use (servo 0–180°) |
|---|---|---|
| Shoulder (elbow 0) | 0° … 180° (every 10°) | 0° … 180° (90 = upright) |
| Elbow (shoulder 90; self-collision of the forearm, wrist and claw with the upper link) | −150° … +30° (every 5°) | −150° … +30° (servo 90 = −60, the fitting pose) |
| Wrist (shoulder 45, elbow −45) | −90° … +90° | −90° … +90° |
| Claw | 0 … 44 mm (0 = fingers touching) | 0 … 44 mm (126° of servo) |

The elbow window is free of self-collision over its whole travel, so it isn't narrowed: `elbow_window_deg` [−150, 30]. Collisions with the turntable, the base, the ring and the desk depend on the other joints; the firmware's guard keeps the arm out of them (BUILD_GUIDE §5).

Reach: 293 mm from the yaw axis at full horizontal extension. Collision-free poses inside the servos' travel put the fingertips on the desk (0–8 mm up) from 84 to 263 mm from the yaw axis with any claw angle, and from 98 to 220 mm with the claw within 5° of straight down. Every named pose is collision-free, including "pick from desk" (claw down, 20 mm open, fingertips 6.5 mm above the desk, 157 mm from the yaw axis) and the elbow folded to −150°, and so are the viewer's demo poses.

## Printed pieces

| # | Job | Piece | Orientation | Mates with | Clearance |
|---|---|---|---|---|---|
| 0 | arm-fit-test | *(optional)* horn pocket + servo window coupon | flat | MG996R horn, MG90S horn, both servo bodies | 0.4 window, 0.5 horn pocket |
| 1 | 20261025-arm-base | Base: 110 × 104 × 40 box, open bottom | upside down (top plate on bed) | base servo, ring, cradle, DC jack | 0.4 servo window, lead notches |
| 2 | 20261025-arm-turntable-ring | Support ring r 41–44, 16.1 tall + 3 tabs | flat | base top, turntable underside (0.4 mm running gap + PTFE tape) | 0.4 axial |
| 3 | 20261025-arm-turntable | Disk Ø96 + 66 mm upright + gussets | disk on bed | base disc horn, shoulder servo | 0.4 window, lead notches with 45° tops |
| 4 | 20261025-arm-upper-link | Link 100 mm, 10 thick | flat, pocket up | shoulder horn, elbow servo | 0.5 / 0.4, lead notches |
| 5 | 20261025-arm-forearm | Link 90 mm, 10 thick | flat, pocket up | elbow horn, wrist MG90S | 0.5 / 0.4 side, 0.2 end, lead notch + moved pilot |
| 6 | 20261026-arm-claw-frame | Wrist plate + bulkhead + rail wall | back face down | wrist horn, claw MG90S, rack B, cover | 0.5 / 0.4 / 0.25 sliding |
| 7 | 20261026-arm-claw-cover | Front plate (2 neck slots, Ø22.6 pinion pass-through) + top wall + lip wall + tie | standing on its −y end, 5 mm brim | frame, both racks, camera mount | 0.25 sliding |
| 8 | 20261026-arm-claw-pinion | 20 T module-1 gear, trimmed-horn pocket | flat | claw horn (arms cut to 5.5), both racks | 0.1 pocket fit, 0.35 backlash per mesh |
| 9–10 | 20261026-arm-claw-jaw ×2 | Rack + neck + finger, identical | standing, finger up, no brim | pinion, frame/cover channels | 0.25 sliding |
| 11 | 20261026-arm-camera-mount | *(optional)* Brio 4K seat, 34° | standing on its −y end, 5 mm brim | cover top, camera (1/4"-20) | 0.3 lip |
| — | ~~20261025-arm-gripper-base / -gripper-jaw~~ | superseded by claw v2 | | | |
| 12 | 20261025-arm-esp32-cradle | Tray for the ESP32 | flat | base bosses, ESP32 board | 0.6 around the PCB |

**Before printing, measure your servos.** The servo dimensions are nominal datasheet values (`tools/hobby_parts.py`); brands differ by up to ~1 mm. Measure: body length and width, tab-hole spacing, shaft-to-body-end distance, the MG90S's heights (case bottom → tabs → spline top), each lead's exit, the spline thread depth, and the horns. BUILD_GUIDE §2 lists them; put any differences into `replace(MG996R, ...)` / `replace(MG90S, ...)` in the models.

## Status

| # | Piece | Status |
|---|---|---|
| 1–5 | base, ring, turntable, upper link, forearm | DESIGN round 3: lead notches (01 B1), MG90S wrist (01 B2/S1), disc horn and 0.4 mm ring gap (03 SYS-05); DFM and strength to re-run. Their G-code is from round 2: don't print it |
| 6–11 | claw + camera mount | DESIGN round 2 (claw) / round 3 (arm): every required fix of the claw DFM and strength round 1, SYS-01 fix A, SYS-08; DFM and strength to re-run. Their G-code is from before round 1: don't print it |
| 12 | cradle | AWAITING_APPROVAL (unchanged) |
| — | old gripper base / jaw | SUPERSEDED (kept for the record; don't print) |

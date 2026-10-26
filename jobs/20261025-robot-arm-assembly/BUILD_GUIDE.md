# Desktop robot arm: build guide

Robot 1 of 3 (then the tracked rover, then the hexapod). Four joints plus a parallel claw, 5 hobby servos, an ESP32 DevKit, a 6 V supply and PETG, with an optional Logitech Brio 4K webcam on the claw.
Reach is 284 mm horizontally. Within the servos' travel the fingertips come down to the desk from about 125 to 245 mm out, and the sketch's desk guard stops them about 8 mm above it. The claw opens 0–44 mm with about 12 N per finger at stall.

**Payload:**
- 50 g without the camera.
- 20 g at full reach with the camera. Bend the elbow and it can carry more. The camera's 63 g sits at the arm's end, so the shoulder servo works harder.

## 1. Bill of materials

### Printed (PETG): 12 parts, 11 SD-card files

| # | Part | Job | Print orientation |
|---|---|---|---|
| 1 | Base | `20261025-arm-base` | upside down (top plate on bed) |
| 2 | Turntable support ring | `20261025-arm-turntable-ring` | flat, tabs down |
| 3 | Turntable + shoulder upright | `20261025-arm-turntable` | disk on bed |
| 4 | Upper link (100 mm) | `20261025-arm-upper-link` | flat, horn pocket up |
| 5 | Forearm (90 mm) | `20261025-arm-forearm` | flat, horn pocket up |
| 6 | Claw frame | `20261026-arm-claw-frame` | back face down (wrist-horn pocket on the bed) |
| 7 | Claw cover | `20261026-arm-claw-cover` | standing on its end (brim) |
| 8 | Claw pinion | `20261026-arm-claw-pinion` | flat, horn pocket down, solid |
| 9–10 | Claw jaw × 2 (identical) | `20261026-arm-claw-jaw` | standing on the rack, finger up (both on one plate) |
| 11 | Brio 4K camera mount *(optional)* | `20261026-arm-camera-mount` | standing on its end (brim) |
| 12 | ESP32 cradle | `20261025-arm-esp32-cradle` | as it hangs (frame bottom down) |

Each part's print time and filament are in its `slice_stats.json`, and `README.md` next to this file has a summary table.

The old gripper (`20261025-arm-gripper-base` and `-gripper-jaw`) is **superseded**. Don't print it.

### Bought
| Qty | Item | Notes |
|---|---|---|
| 3 | MG996R servo (metal gear, 180°) | Base, shoulder, elbow. Keep the bag: you need the **double-arm horn** and the screws |
| 2 | MG90S micro servo (metal gear, 180°) | Wrist and claw. Keep the **single-arm horn** (wrist) and the **double-arm horn** (claw pinion) |
| 1 | ESP32 DevKit (38-pin DevKitC or 30-pin DOIT) | Pins soldered down |
| 1 | 6 V 5 A DC adapter, 5.5 × 2.1 mm plug, **centre positive** | Servo power. 5 A covers two MG996R stalling at once. Unloaded it should read 6.2 V or less: the MG90S is rated 4.8–6.0 V |
| 1 | 5.5 × 2.1 mm panel-mount DC jack (Ø11 mm thread) | Goes in the base's −X wall. Label it "6 V, centre +" |
| 1 | 1000 µF 10 V (or higher) electrolytic capacitor | Across the servo supply, at the jack |
| 1 | Inline DC switch lead, 5.5 × 2.1 mm plug to socket, rated 5 A or more | Between the adapter and the jack, on the desk within reach: the arm's off switch and emergency stop |
| 1 | 5 A fuse: inline blade-fuse holder with a 5 A blade, or a 5 A (hold) polyfuse | In the + wire from the jack to the power bus |
| *opt.* | SMBJ6.5A TVS diode (6.5 V, unidirectional) | Across the bus after the fuse, stripe to +6 V: a 9–12 V or reversed adapter then blows the fuse instead of the servos |
| *opt.* | 5 × 10 kΩ resistor | Pull-down from each servo signal to GND: the pins float until the sketch starts |
| *opt.* | USB phone charger (5 V, 1 A) | Runs the ESP32 through its USB port when no PC is connected. The ESP32 always runs from USB: there is no buck |
| ~15 | Female–female and female–male jumper wires, servo extension leads (2 × 30 cm) | The shoulder, elbow, wrist and claw leads must reach the base |
| 3 | M3 × 6 self-tapping (pan head) | Ring tabs. A longer screw would reach the ESP32 under the plate |
| 3 | M3 × 10 self-tapping (pan head) | Cradle, from below into the counterbores. Not longer: the boss pilots are 6 mm deep |
| 3 | M3 × 16 screw + Ø9 (M3 large) washer | MG996R horn clamp screws for the base, shoulder and elbow. They replace the short horn screw from the bag |
| 1 | M2 × 12 screw + Ø6 washer | Wrist horn clamp screw, through the claw frame |
| 1 | M2 × 10 pan or cheese head | Pinion clamp screw |
| 2 | M2 × 12 self-tapping | Wrist MG90S tab screws in the 10 mm forearm |
| 2 | M2 × 8 self-tapping | Claw MG90S tab screws in the bulkhead, if the bag screws are shorter |
| 2 | M3 × 12 self-tapping (pan head) | Claw cover, front, into the claw frame |
| 2 | M3 × 10 self-tapping, **or** 2 × M3 × 18 button head (ISO 7380) with the camera mount | Claw cover, top, into the bulkhead |
| 4 | M3 × 50 (or #4 × 2") wood screws, or 2 desk clamps | **Required**: screw the base to the desk or to a board. With the arm out, it tips the base over |
| — | Spiral cable wrap or zip ties, 4 rubber feet, a drop of CA glue | Tidy the leads; the glue locks the trimmed horn in the pinion |
| *opt.* | Logitech Brio 4K webcam, with its clip removed | Plugs into your **PC**, not the ESP32 (the ESP32 has no USB host) |
| *opt.* | 1/4"-20 × 3/8" knurled thumb screw (camera screw) | Holds the Brio on the mount. It must not stand more than the camera's thread depth above the 4 mm seat |
| *opt.* | Flexible USB-C to USB-A cable, 2 m or more | A thin, soft cable loads the wrist less than the stiff stock cable |

## 2. Before you print

1. **Measure your servos and horns.** The CAD uses nominal datasheet sizes (`tools/hobby_parts.py`).
   - On the servos, measure body length and width, tab-hole spacing, and the distance from the shaft to the near body end.
   - On the horns, measure the MG996R double-arm horn (hub Ø, centre to tip, tip width) and the MG90S arm horns (the same three sizes, plus the arm's width near the hub).
   - If anything differs by more than 0.3 mm, give the numbers to Claude. Claude updates the specs in the models and re-runs the pipeline.
2. **Camera:** measure how deep the Brio's tripod thread is, so the thumb screw doesn't bottom out.
3. Load PETG. The G-code is sliced with Prusa's stock **Prusament PETG** and **0.20 mm QUALITY** presets. Print on a smooth PEI sheet with glue stick or a release agent: PETG can bond too hard to bare smooth PEI. The cover and the camera mount print standing up with a brim.

## 3. Wiring

```
6 V adapter ─► inline switch ─► DC jack + ─► 5 A fuse ─► bus +6 V ─┬─ 1000 µF (+ to +6 V)
(6 V, centre +)    (off / e-stop)                                    ├─ SMBJ6.5A (optional, stripe to +6 V)
                                                                     └─► servo V+ (red) × 5
                                DC jack − ─────────────► bus GND ───┬─ capacitor −, TVS anode
                                                                     ├─► servo GND (brown) × 5
                                                                     └─► ESP32 GND   ← common ground is required

ESP32 GPIO ─► servo signal (orange/yellow)          (optional: 10 kΩ from each signal to GND)
  GPIO13  base yaw (MG996R)
  GPIO32  shoulder (MG996R)
  GPIO27  elbow (MG996R)
  GPIO26  wrist (MG90S)
  GPIO25  claw (MG90S)

ESP32 USB ─► your PC (commands, and the ESP32's power), or a USB phone charger when no PC is used
Brio 4K ─► USB-C cable ─► your PC (vision)
```

- Never power the servos from the ESP32's 5V/3V3 pins: the arm can draw several amps.
- The ESP32 runs from its USB port only. Never connect the 6 V supply, or a buck converter, to its 5V or 3V3 pin: Espressif allows only one of USB, 5V and 3V3 at a time, and a buck would let the PC's USB port feed the servos when the adapter is unplugged.
- **Before the first connection**, check the adapter with a meter: 6.2 V or less unloaded, centre pin positive. A 9 V or 12 V adapter with the same plug destroys the MG90S servos, and a centre-negative one reverses the capacitor and the servos.
- The inline switch is the arm's off switch: keep it within reach while the arm moves.
- None of these GPIOs is a strapping pin (0, 2, 5, 12, 15) or input-only (34–39). The shoulder is on GPIO32, not GPIO14: GPIO14 puts out a PWM signal at boot, and the shoulder carries the whole arm.
- Make a 5-way power bus inside the base for V+ and GND: a small piece of stripboard, or Wago-style lever connectors. Run the 6 V from the jack through the fuse to the bus in 20–22 AWG wire, not jumper wire.
- GPIO13, 25, 26 and 27 are ADC2 pins. That's fine for servo signals, but any analog input added later must use ADC1 (GPIO32–39): ADC2 stops working once Wi-Fi is on.

## 4. Centre the servos, then assemble

The horns must go on with every servo at its centre position (90°) and the links in their neutral pose. Otherwise a joint's travel won't line up with its collision-free range.

1. **Flash, find the end stops, and centre.**
   - Wire everything (section 3).
   - Flash `arm_test/arm_test.ino`: Arduino IDE, board "ESP32 Dev Module" on the arduino-esp32 3.x core, library **ESP32Servo** 3.x.
   - Plug in the USB first, then switch on the 6 V. Open the Serial Monitor at 115200 and type `c`.
   - **End stops**, one servo at a time, with a horn pushed loosely onto the spline as a pointer. Hobby servos don't all turn 180° between 500 and 2500 µs; one that hits its end stop first stalls there at full current.
     - Type `u s 1500`, then step down 100 µs at a time (`u s 1400`, `u s 1300` …) to `u s 500`. If the horn stops turning or the servo buzzes before 500, come back in 20 µs steps until it is quiet, then 30 µs more, and note that pulse.
     - Do the same upwards to `u s 2500`. Type `c`.
     - Repeat for `b`, `e`, `w` and `g` (the claw).
     - If a servo stopped short, put its two pulses into `minUs` and `maxUs` on its line of the sketch's `joints[]` table and re-flash.
   - Type `c`. This centres the base, shoulder, elbow and wrist and closes the claw servo.
   - Leave the power on while you fit the horns.
2. **Base.**
   - Screw the base to the desk or to a board with 4 × M3×50 wood screws through the corner pillars.
   - Fit the cradle to the 3 bosses under the base top plate (M3×10 from below).
   - Drop the ESP32 in pins-down, with its USB end against the slot in the +X wall.
   - Fit the DC jack, the capacitor and the power bus.
   - Drop the base MG996R into the top-plate window, shaft up, and fix it with its 4 tab screws.
   - Screw the ring on with 3 × M3×6.
3. **Horns into the links.**
   - Press each horn into its pocket on the link's back face, with double-arm horns along the link's long axis.
   - Drill 1.5 mm pilots through two of the horn's arm holes into the plastic. Screw the horn down with the small horn screws so it can't turn.
   - The **centre clamp screw** goes in from the link's front face, through the link and the horn, into the spline: M3×16 + washer on the big servos, M2×12 + washer on the wrist. It holds the link on, so tighten it firmly.
4. **Turntable, before the shoulder servo.** The servo body covers the centre hole once it's fitted.
   - Lay the base horn flat on the turntable's underside, centred on the Ø3.4 hole and pointing along X. Drill and screw through two arm holes.
   - Push it onto the base servo's spline with the upright facing **+X**.
   - Drive the M3×16 + washer from the top. A screwdriver with a shaft of 75 mm or more clears the upright.
   - **Then** put the shoulder MG996R through the upright window from the front (+Y side), shaft facing forward and body horizontal. Fix it with 4 tab screws.
5. **Upper link.**
   - Fit the elbow MG996R in the link's far window: tabs on the front face, shaft forward.
   - Push the link's horn onto the shoulder spline with the link pointing **straight up** (servo at 90° = upright).
   - Fit the clamp screw.
6. **Forearm.**
   - Fit the wrist MG90S in the forearm's far window, shaft forward, with 2 × M2×12 self-tapping screws.
   - Push the forearm onto the elbow spline **in line with the upper link** (elbow at 90° = straight).
7. **Claw frame, before the claw servo.** The claw servo's body covers the wrist clamp screw.
   - Press the MG90S **single-arm** horn into the pocket on the frame's back face, pointing towards the bulkhead. Screw it down through one arm hole.
   - Push the frame onto the wrist spline **in line with the forearm**.
   - Fit the M2×12 + Ø6 washer from the front through the centre hole.
8. **Claw servo.** Slide the claw MG90S through the bulkhead window from behind, shaft pointing at the fingertips. Fix it with its 2 tab screws (M2×8 self-tapping if the bag screws are short).
9. **Pinion.**
   - Cut both arms of the MG90S **double-arm** horn **5.5 mm from the centre** with flush cutters, leaving two short stubs on the hub.
   - File the cut ends flat and press the horn into the pinion's back pocket. It should be snug. A drop of CA glue removes any play.
   - Type `f`: the claw servo goes to its closed angle.
   - Push the pinion and horn onto the claw spline (any tooth orientation is fine) and drive the M2×10 from the front.
10. **Cover.**
    - Lower the cover onto the frame. The lip goes behind the pinion's level, the top wall rests on the bulkhead, and the front plate covers the wrist plate's front edge.
    - Fix the front with 2 × M3×12 into the wrist plate's edge.
    - Fix the top with 2 × M3×10, or with the camera mount and 2 × M3×18 button heads (step 13).
11. **Jaws.** The front plate has two slots. The upper slot is open at one side and the lower slot at the other.
    - Slide one jaw into the **upper** channel from the side where the upper slot is open: rack teeth down, finger pointing forward, neck in the slot.
    - At the pinion, push gently and wiggle until the teeth mesh. Keep pushing until the finger reaches the claw's centre line.
    - Slide the second jaw, upside down, into the **lower** channel from the other side, in the same way.
    - The two grip faces should meet in the middle. If one is a tooth off (about 3 mm), pull it back out one tooth and slide it in again.
12. **Claw calibration.**
    - Type `g 10`: the claw should open 10 mm.
    - If it squeezes instead, set `GRIP_OPEN_DIR = -1` and `GRIP_CLOSED_DEG = 160` in the sketch, re-flash, and redo step 9 from `f`.
    - Then type `k 20`, `k 22`, … until `g 0` just brings the faces together without the servo buzzing.
    - Copy the printed `GRIP_CLOSED_DEG` value into the sketch.
13. **Camera (optional).**
    - Take the clip off the Brio (Logitech's quick-start guide shows how, in its tripod section).
    - Screw the camera mount onto the cover with the 2 × M3×18 button heads.
    - Hold the camera on the tilted seat against the rear lip, lens towards the fingers. Turn the knurled 1/4"-20 thumb screw up into it from below until snug. The thread is in the camera's plastic, so don't force it.
    - Plug the USB cable into the camera's end and zip-tie it to the claw frame.
    - Run it along the forearm and upper link with a slack loop at the wrist, elbow, shoulder and base, then on to your PC.
14. **Leads.**
    - Run the servo leads down each link with spiral wrap, leaving slack at every joint.
    - Take them through the base's cable slot to the bus and the ESP32.

## 5. First power-up and joint limits

**Power order:** plug in the ESP32's USB first, then switch on the 6 V. The servo signal pins float until the sketch starts, and a servo can twitch on a floating signal (the optional 10 kΩ pull-downs stop that). **Type `c` before you switch off:** the arm then rests upright, which is also the pose the sketch restores next time.

The sketch saves the pose and the claw trim on the ESP32 after every move. After a reset (power-up, or the PC opening the serial port) the servos start where they stopped instead of jumping to 90°. The `k` trim survives power-off and re-flashing, so copying it into the sketch is optional. A re-flash with a different `GRIP_OPEN_DIR` or `GRIP_CLOSED_DEG` starts the claw closed at the new value.

Use the Serial Monitor commands in `arm_test.ino` to move one joint at a time. For example, `s 100` sets the shoulder to 100° and `g 30` opens the claw 30 mm. Joints move 1° per 15 ms. `x` stops a move for good: no later command resumes it. `p` prints the angles and moves nothing. A command without a valid number (`s`, `s abc`) is refused with `err`.

| Joint | Command | Meaning |
|---|---|---|
| Base | `b 0–180` | yaw ±90° |
| Shoulder | `s 0–180` | 90 = upright. The link reaches horizontal at 0 or 180, depending on the mounting side: check the direction with small moves first |
| Elbow | `e 0–180` | 90 = straight. The arm can't hit itself anywhere in the servo range (clear to ±170°); the desk guard keeps it off the desk |
| Wrist | `w 0–180` | 90 = straight. Clear of the arm to ±150°; the camera clears the arm in every pose |
| Claw | `g 0–44` (mm) | 0 = closed. 3.18° of servo per mm; `k` trims the closed angle |
| Any | `u <joint> <µs>` | A raw pulse, moved slowly: the end-stop test of section 4, step 1. `u s 1500` = shoulder at 1500 µs |

**Desk guard.** Limiting each joint on its own doesn't keep the claw or the camera off the desk: with the shoulder low, the elbow and wrist can still drive the jaws into it. So the sketch checks every 1° step against a side view of the arm and stops the move with `blocked: desk` before the claw, the jaws or the camera reaches the desk; the fingertips stay about 8 mm above it. From a pose that is already too low, a move may only go up. It needs two signs, set once after assembly with the claw empty and the switch within reach:

1. Type `c`, then `s 60`: the arm leans towards the side that `s 0` points to.
2. Type `e 100`. If the forearm's end rises, keep `EL_SIGN = +1`; if it drops, set `EL_SIGN = -1`. Type `e 90`.
3. Type `w 100`. If the fingertips rise, keep `WR_SIGN = +1`; if they drop, set `WR_SIGN = -1`. Type `w 90`, then `c`.
4. Without the Brio, set `CAMERA_FITTED = false`: the wrist may then come closer to the desk.
5. Re-flash if you changed anything. Check: type `s 0`, then swing the forearm down (`e 0` with `EL_SIGN = +1`, `e 180` with `-1`). It should stop with `blocked: desk` when the forearm is about 25° below horizontal (30° without the camera). If it keeps going, type `x` and recheck the signs.

The guard takes the desk to be level with the underside of the base, which is screwed down on it.

**Claw scale:** type `g 40` and measure the gap between the grip faces with calipers. It should be 40 ± 1 mm. If not, the claw servo turns more or less than 180° between its `minUs` and `maxUs`: set `DEG_PER_MM` to 3.183 × 40 / (the measured gap) and re-flash.

**Holding something:** command the object's width minus 2 mm, not `g 0`. At `g 0` the claw servo stalls against the object and heats up.

Then do the **proof tests** in each part's `spec.md` §8, for example 1 kg hung at the elbow axis for 1 minute with the shoulder holding, and the claw's grip tests. The strength verdicts rely on them, because there's no measured PETG data in `library/` yet. Record the results in each job's `inspection.md`.

## 6. Driving it from a PC, with the camera

The Brio plugs into your PC, and the ESP32's USB port takes commands from the same PC. `pc/arm_pc_control.py` is a starting point. Install its dependencies with `pip install pyserial opencv-python`.

- `python pc/arm_pc_control.py --port COM5 preview` shows the camera with a crosshair. `o` and `c` open and close the claw, `[` and `]` move the wrist, `q` quits. It asks the camera for MJPG at 1920 × 1080 and 30 fps (uncompressed 1080p doesn't fit through USB 2.0, which many thin cables are) and prints the size it got. Camera 0 is often a laptop's own camera: if the picture isn't the Brio's, use `--camera 1`.
- `python pc/arm_pc_control.py --port COM5 move 90 60 80 100 20` moves every joint together (base, shoulder, elbow, wrist in degrees, claw in mm) and waits for `ok`. A move the desk guard stops ends with `arm: blocked: desk`.
- In your own code, `Arm(port).move(...)` and `.status()` use the same serial commands (`m`, `?`, `x`; see the top of `arm_test.ino`). `move()` returns True when every joint arrived and False after `stop()`. It raises `RuntimeError` when the sketch refuses the move (`err …`) or the desk guard stops it (`blocked: desk`), `TimeoutError` when the arm doesn't answer, and `ValueError` for a NaN target.
- **Keep one connection open** for a whole session, as the preview does, rather than running the script once per move. It opens the port with DTR and RTS off, which keeps most PCs from resetting the ESP32, but not all. After a reset the sketch restarts where the arm stopped, which takes about 2 s.
- The camera is mounted turned 90° to the arm. With the claw level, "up" is at the right of the raw image; the preview rotates it upright.
- The jaws sit near the middle of the picture, about 70–100 mm from the lens. Set the Brio's field of view to 78° or 65° in Logi Tune for a closer view.

## 7. Safety

- Keep your fingers out of the claw and the elbow while the arm is powered. The claw squeezes about 12 N per finger, and an MG996R stalls at about 1 N·m.
- Don't hold a servo stalled for minutes: it overheats, and so does the PETG near it. Use `k` so that `g 0` doesn't squeeze when the claw is empty.
- Unplug the 6 V supply before working on the wiring.

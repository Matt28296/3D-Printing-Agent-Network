# Desktop robot arm: build guide

Robot 1 of 3 (then the tracked rover, then the hexapod). Four joints plus a parallel claw, 5 hobby servos, an ESP32 DevKit, a 6 V supply and PETG, with an optional Logitech Brio 4K webcam on the claw.
Reach is 293 mm horizontally. Inside the servos' travel the fingertips reach the desk from 88 to 263 mm from the yaw axis (claw straight down: 98 to 220 mm), collision-free; the sketch's guard keeps them 8 mm above it (§5 gives the guard's own figures). The claw opens 0–44 mm. At stall the pinion pushes 21.6 N into the racks: 10.8 N per jaw when both grip (the safety figure), all 21.6 N into one jaw when the other is blocked. Rack friction leaves a real grip of about 5–7.5 N per finger (deep review 03, SYS-15, scaled to the 10 mm pitch radius).

**Payload.** The shoulder MG996R sets it, and the camera package (Brio, mount, thumb screw, cable: ≈95 g at the arm's end) costs most of it. Grams the arm can carry 10 mm behind the fingertips, claw pointing down, object 20–60 mm above the desk, at the best pose inside the servo travel. "Short lift" keeps every servo under 50 % of its 6 V stall torque, "moving" allows ×1.3 for starting and stopping, "holding" keeps it under ⅓ of stall, the running-current band, for as long as you like. Above about 200 g the claw's friction grip, not the servos, is the limit.

| Fingertips out along the arm | Camera: short lift | Camera: moving | Camera: holding | No camera: short lift | No camera: moving | No camera: holding |
|---|---|---|---|---|---|---|
| 60–100 mm | 200 g | 200 g | 200 g | 200 g | 200 g | 200 g |
| 100–120 mm | 200 g | 190 g | 130 g | 200 g | 200 g | 200 g |
| 120–140 mm | 200 g | 105 g | 50 g | 200 g | 185 g | 135 g |
| 140–160 mm | 130 g | 35 g | — | 200 g | 120 g | 75 g |
| 160–180 mm | 65 g | — | — | 150 g | 65 g | 30 g |
| 180–200 mm | 20 g | — | — | 105 g | 30 g | — |
| 200–220 mm | — | — | — | 70 g | 5 g | — |
| Arm straight out (≈280 mm) | — | — | — | 30 g | — | — |

"Out along the arm" is the fingertips' distance from the yaw axis in the arm's own plane; "—" means none. With the camera, holding the empty arm straight out already takes 57 % of the shoulder's stall torque, so don't park or wait there: `r` parks the arm upright (shoulder 90, elbow 0, wrist 0), where the shoulder holds almost nothing, and the sketch parks it by itself after 60 s without a command (§5). The figures use the parts' sliced masses; with solid parts each cell drops by about 30 g. Claw round 3 made the claw about 25 g heavier (the frame's rail block and ribs, the cover's thicker lip and second tie, the 12 mm racks and pinion), which costs every cell 20–30 g. Method and every number: `torque_budget.py` → `torque_budget.json` (deep review 03, SYS-02).

## 1. Bill of materials

### Printed (PETG): 12 parts, 11 SD-card files

| # | Part | Job | Print orientation |
|---|---|---|---|
| 1 | Base | `20261025-arm-base` | upside down (top plate on bed) |
| 2 | Turntable support ring | `20261025-arm-turntable-ring` | flat, tabs down |
| 3 | Turntable + shoulder upright | `20261025-arm-turntable` | disk on bed |
| 4 | Upper link (100 mm) | `20261025-arm-upper-link` | flat, horn pocket and back-face ribs up |
| 5 | Forearm (90 mm) | `20261025-arm-forearm` | flat, horn pocket and back-face ribs up |
| 6 | Claw frame | `20261026-arm-claw-frame` | back face down (wrist-horn pocket on the bed) |
| 7 | Claw cover | `20261026-arm-claw-cover` | standing on its −y end (5 mm brim; 2 support pillars inside the round hole, snapped off before assembly) |
| 8 | Claw pinion (20 teeth) | `20261026-arm-claw-pinion` | flat, horn pocket down, solid |
| 9–10 | Claw jaw × 2 (identical) | `20261026-arm-claw-jaw` | standing on the rack's back end, finger up (both on one plate, no brim) |
| 11 | Brio 4K camera mount *(optional)* | `20261026-arm-camera-mount` | standing on its −y end (5 mm brim) |
| 12 | ESP32 cradle | `20261025-arm-esp32-cradle` | as it hangs (frame bottom down) |

Each part's print time and filament are in its `slice_stats.json`, and `README.md` next to this file has a summary table. Round 3 (deep reviews 01 and 03) changed every part except the cradle: their G-code is from the old geometry and gets sliced again once the reviews pass.

The old gripper (`20261025-arm-gripper-base` and `-gripper-jaw`) is **superseded**. Don't print it.

### Bought
| Qty | Item | Notes |
|---|---|---|
| 3 | MG996R servo (metal gear, 180°) | Base, shoulder, elbow. Keep the bags: the base needs the **Ø25 round disc horn**, the shoulder and elbow the **double-arm horn**. Leave the rubber grommets and brass eyelets out: the tabs sit flat on the plastic |
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
| 1 | Power bus: stripboard ≈50 × 30 mm with 5 rows of 3-pin male headers (G-V-S), or a 5-way terminal strip | Inside the base. Each servo plugs straight onto it; only its signal wire goes on to the ESP32 |
| 1 m | Silicone wire 0.5–0.75 mm² (18–20 AWG), red and black, plus heat-shrink | Jack → fuse → bus, and bus GND → ESP32 GND. Servo power never runs through Dupont jumpers |
| 5 | Female–female jumper wires | Servo signals from the bus to the ESP32 only |
| 2 | Servo extension lead, 50 cm (40 cm at least) | Claw and wrist: their MG90S leads are 24–25 cm, the run to the base ≈560 and ≈520 mm |
| 1 | Servo extension lead, 30 cm | Elbow (run ≈430 mm, MG996R lead 30 cm). The shoulder and base leads reach without one |
| 12 + 12 | M3 × 12 pan-head self-tapping screw (ST2.9 or a thread-forming screw for plastics) + M3 washer Ø7 × 0.5 | MG996R tab screws: base, shoulder, elbow, 4 each. Through the 2.5 mm tab and the washer they reach 9 mm into the 10 mm base plate and boss and the 10 mm upper link; in the 7 mm upright the tip stands 2 mm out at the back, clear of the gussets |
| 3 + 3 | M3 × 6 self-tapping (pan head) + M3 washer Ø7 × 0.5 | Ring tabs. The washer spreads the head's clamp on the 3 mm tab, which creeps under a bare pan head (links strength round 4); a relief in the ring's wall lets it sit flat. A longer screw would reach the ESP32 under the plate, and with the washer 2.5 mm bites the plate: drive them snug, no harder |
| 3 | M3 × 10 self-tapping (pan head) | Cradle, from below into the counterbores. Not longer: the boss pilots are 7 mm deep, 1 mm more than an M3 × 10 reaches |
| 3 + 3 | M3 × 14 socket head (ISO 4762) + Ø9 × 0.8 washer (M3 large, ISO 7093) | Horn clamp screws: base (through the 8 mm turntable disk), shoulder and elbow (through the 10 mm links, 8 mm above the horn). Each reaches 4.6 mm into the spline (14 − 0.8 − 8 − 0.6, the horn face standing 0.6 above the spline). A socket head lets you re-tighten the base one with an L-key past the upright |
| 2 | M2 × 12 socket or pan head (head ≤ Ø5.5) | Horn clamp screws: wrist (through the claw frame's raised pad) and pinion (from its front counterbore). Both have a 6.3 mm floor above the horn |
| 1 | Ø8 × 0.8 washer, hole 2.7 (DIN 9021 / ISO 7093, M2.5 size) | Under the wrist clamp screw: 12 − 0.8 − 6.3 − 0.6 = 4.3 mm into the spline. The bigger washer spreads the camera's knocks over the pad (claw round 3) |
| 1 | Ø6 × 0.5 washer (M2) | Under the pinion clamp screw, in its counterbore: 12 − 0.5 − 6.3 − 0.6 = 4.6 mm into the spline, like the big ones |
| 5 | M2 × 6 self-tapping (pan head) | Horn anti-rotation screws: 2 each through the shoulder and elbow double-arm horns, 1 through the wrist horn. Drill the horn's hole to 2.0 mm first. The pinion's horn is glued instead |
| 4 | M2 × 8 self-tapping (pan head) | Base disc horn anti-rotation: through 4 of the disc's holes, in opposite pairs on one circle at r ≥ 7 mm, 5.2 mm into the turntable disk (§4 step 3). Two M2 × 6 weren't enough for the base servo's stall (links strength round 4) |
| 1 | M2 × 12 self-tapping (pan head) | Wrist MG90S, lead-end tab, in the 10 mm forearm (9.5 mm engaged) |
| 1 | M2 × 16 self-tapping (pan head) | Wrist MG90S, far tab, into the 16 mm pilot through the forearm's cross-rib (13.5 mm engaged; links strength round 4). Not shorter: an M2 × 12 there pulls out under a yaw stall |
| 2 | M2 × 8 self-tapping (pan head) | Claw MG90S tab screws in the 6.5 mm bulkhead (5.5 mm engaged) |
| 2 + 2 | M2.5 × 16 pan-head self-tapping, head Ø5.0 or less + M2.5 washer Ø6 × 0.5 (DIN 125) | Claw cover, front, into the wrist plate's front edge (10.5 mm engaged in the 14 mm pilots). The washer spreads the head's clamp on the front plate, which creeps under a bare pan head (claw round 7). Jaw B's finger passes 0.5 mm over the washers, so no bigger head or washer. Snug only |
| 2 + 2 | M3 × 14 pan-head self-tapping + M3 washer Ø7 × 0.5 (ISO 7089), **or** 2 × M3 × 18 button head (ISO 7380) through the camera mount, each also with a Ø7 × 0.5 washer | Claw cover, top, into the bulkhead's 14 mm pilots (10.5 / 11.0 mm engaged). The washer spreads the head's clamp on the top wall, which creeps under a bare pan head; not shorter: an M3 × 10 or × 12 pulls out under its own snug preload (claw round 7). Snug only |
| 1 + 1 | M3 × 45 socket head (ISO 4762) + M3 washer Ø7 × 0.5 (ISO 7089) | Claw cover **anchor**: straight down through the cover's top wall, lip and inner post into the frame's rail block (14 mm pilot, 10.75 mm engaged with the washer). A ridge under the post sits in a V-groove in the block, carries the cover and takes the push when a jaw is forced open or knocked shut; the screw only holds the ridge down in the groove, and goes in first (claw rounds 5–6). The washer spreads the head's clamp on the top wall, which creeps under a bare head. Not shorter. Snug only |
| 4 | M3 × 50 (or #4 × 2") wood screws, or 2 desk clamps | **Required**: screw the base to the desk or to a board. With the arm out, it tips the base over |
| *alt.* | Board ≥ 200 × 200 mm, 12–18 mm plywood or MDF, ≥ 0.4 kg, with 4 rubber feet; **or** 1.3 kg of ballast (0.95 kg without the camera) fixed inside the base | If you won't screw into the desk (deep review 03, SYS-12). Free-standing, the 0.7 kg robot tips over with the arm out (safety factor 0.31–0.44 with the camera). On the board it holds with a safety factor of 2.0 or more, camera and 50 g at full reach included; the ballast gives 1.5 (`torque_budget.json`) |
| — | PTFE (plumber's) tape | One layer on the support ring's top face: the turntable disk runs on it |
| — | Spiral cable wrap, zip ties (≤ 2.5 mm wide), 2 adhesive cable-tie mounts (≈10 × 10 mm), a drop of CA glue | Tidy the leads; one tie mount on the claw's bulkhead holds the camera cable (§4 step 14); the glue locks the trimmed horn in the pinion |
| 1 | Right-angle micro-USB (or USB-C, to suit your ESP32) cable | The ESP32's USB cable leaves the base's +X wall under the arm's main pick zone: a right-angle plug keeps it down on the desk |
| *opt.* | Logitech Brio 4K webcam, with its clip removed | Plugs into your **PC**, not the ESP32 (the ESP32 has no USB host) |
| *opt.* | 1/4"-20 × 5/16" knurled thumb screw (camera screw), **or** a 3/8" one with a 1.5 mm washer under its head | Holds the Brio on the mount: 7.9 mm under the head, so 3.9 mm into the camera after the 4 mm seat. Camera makers keep tripod screws under 5.5 mm |
| *opt.* | Thin USB-C **right-angle (90°)** to USB-A cable, 2 m or more | The Brio's port is on its **back**. A straight plug sticks out 50–75 mm towards the wrist; a right-angle plug stands ≈12 mm out and turns the cable along the camera. A thin, soft cable also loads the wrist less (1080p runs over USB 2.0) |

## 2. Before you print

1. **Measure your servos and horns.** The CAD uses nominal datasheet sizes (`tools/hobby_parts.py`).
   - On the servos: body length and width, tab-hole spacing, the distance from the shaft to the near body end.
   - On the MG90S also (deep review 01, B2): case bottom → tab underside (CAD 18.5), tab underside → spline top (CAD 14.0), and the width of the slit from each tab hole to the tab end.
   - Where each lead leaves its case (01, B1): which end, how high above the case bottom, how wide and thick the ribbon is. The windows' notches assume the shaft end, 5.1 mm (MG90S) or 6 mm (MG996R) up, a 3.6 × 1.2 mm (4 × 1.3 mm) ribbon.
   - On the horns: the MG996R double-arm horn (hub Ø, centre to tip, tip width), the MG996R disc horn, the MG90S arm horns (the same three sizes, plus the arm's width near the hub).
   - On the **MG996R disc horn** (links strength round 4): its diameter, its thickness at the holes, and its holes. For each circle of holes, count the holes and measure centre to centre across the circle: the radius is half that. The turntable needs **4 holes in opposite pairs on one circle at r ≥ 7 mm** for its 4 anti-rotation screws (§4 step 3). The design assumed r 9; anything from r 7 up is fine. If your disc has no such circle, tell Claude before printing.
   - **Spline thread depth** (01, S2): screw a long M3 (MG996R) or M2 (MG90S) into a bare output shaft until it stops and count the turns (0.5 or 0.4 mm each). Every horn clamp screw reaches 4.6 mm into it; if yours is shallower than 5.1 mm, use the next shorter screw.
   - If a body length or width differs by more than 0.1 mm, or anything else by more than 0.3 mm, give the numbers to Claude. Claude updates the specs in the models and re-runs the pipeline.
2. **Camera:** measure how deep the Brio's tripod thread is, so the thumb screw doesn't bottom out, and where the USB-C port sits on its back: the mount's rear lip stands 6 mm up the back, so the plug must sit above that.
3. Load PETG. The G-code is sliced with Prusa's stock **Prusament PETG** and **0.20 mm QUALITY** presets. Print on a smooth PEI sheet with glue stick or a release agent: PETG can bond too hard to bare smooth PEI. The cover and the camera mount print standing up with a 5 mm brim; the jaws print without one (it would fill the tooth gaps).

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
- Make the 5-way power bus inside the base (deep review 01, S8): stripboard with five rows of 3-pin male headers, G-V-S, the V strip and the G strip each joined along the board. Each servo's plug (or its extension's) goes straight onto a row; only the signal strip of each row goes on to the ESP32, on a jumper. Run the 6 V from the jack through the fuse to the bus in 18–20 AWG silicone wire, never in jumper wire: an MG996R stalls at 2.5 A.
- Put the extension-lead junctions just outside the base's cable slot or on the turntable side, never at a moving joint: the 2.54 mm housings are bulky, and the junctions stay reachable after the base is screwed down.
- GPIO13, 25, 26 and 27 are ADC2 pins. That's fine for servo signals, but any analog input added later must use ADC1 (GPIO32–39): ADC2 stops working once Wi-Fi is on.

## 4. Centre the servos, then assemble

Build the whole base on the bench first and screw it down last: once it is screwed to the desk, the cradle, the ESP32 and the bus inside it are out of reach (deep review 03, SYS-09). Every horn goes on with its servo at its centre (`c`: 90° on every servo) and its link in that joint's fitting pose. Otherwise a joint's travel won't line up with its collision-free range and the sketch's limits.

| Joint | Fitting pose at `c` (joint angle, §5) |
|---|---|
| Base | the upright's front face (where the shoulder shaft comes out) towards +Y, so the arm reaches out over the +X (USB) wall (0) |
| Shoulder | upper link straight up (90) |
| Elbow | forearm 60° below the upper link's line, bent towards +X: it points 30° above horizontal (−60). The elbow's window is then −150 … +30 |
| Wrist | claw in line with the forearm (0) |
| Claw | pinion fitted last, at `g 44` with both jaws fully open (steps 10–11) |

Every servo goes into its window **from the tab side, case bottom first**. Its lead comes out of the case end nearest the shaft, close to the case bottom, so its root crosses the plate: each window has a notch at that end (both ends on the MG996Rs, whose lead end isn't confirmed). Feed the plug through first, then keep the ribbon flat in the notch while the case follows.

1. **Base, upside down on the bench.**
   - Fit the DC jack in the −X wall (label it "6 V, centre +"), and the fuse, the capacitor and the power bus inside (§3).
   - Fit the cradle to the 3 bosses under the top plate (3 × M3 × 10 from below) and drop the ESP32 in pins-down, its USB end against the slot in the +X wall.
   - Turn the base over. Put the base MG996R into the top-plate window from above, shaft up, case bottom first, its lead through an end notch. Fix it with 4 × M3 × 12 + washers and plug it onto the bus.
   - Put one layer of PTFE tape on the support ring's top face, then screw the ring on with 3 × M3 × 6, each with a Ø7 washer under its head (the wall has a relief for it). Snug, no harder: they have 2.5 mm of thread in the plate.
   - Don't screw the base down yet (step 15).
2. **Flash, find the end stops, and centre.**
   - Plug the other four servos onto the bus loose, on the bench.
   - Flash `arm_test/arm_test.ino`: Arduino IDE, board "ESP32 Dev Module" on the arduino-esp32 3.x core, library **ESP32Servo** 3.x.
   - Plug in the USB first, then switch on the 6 V. Open the Serial Monitor at 115200, line ending "Newline".
   - Type `i 0` first. The sketch parks the arm by itself after 60 s without a command (§5), and nothing may move while you fit the horns and links; §5 switches parking back on with `i 60`. Then type `c`.
   - **End stops**, one servo at a time, with a horn pushed loosely onto the spline as a pointer. Hobby servos don't all turn 180° between 500 and 2500 µs; one that hits its end stop first stalls there at full current.
     - Type `u s 1500`, then step down 100 µs at a time (`u s 1400`, `u s 1300` …) to `u s 500`. If the horn stops turning or the servo buzzes before 500, come back in 20 µs steps until it is quiet, then 30 µs more, and note that pulse.
     - Do the same upwards to `u s 2500`. Type `c`.
     - Repeat for `b`, `e`, `w` and `g` (the claw).
     - If a servo stopped short, put its two pulses into `minUs` and `maxUs` on its line of the sketch's `joints[]` table and re-flash.
   - Type `c`: every servo goes to its centre and the claw servo to its closed angle. Leave the power on while you fit the horns, and unplug a servo from the bus only to thread its lead.
3. **Horns.** Drill each horn's screw hole to 2.0 mm, put a 1.5 mm pilot through it into the plastic, and fix the horn with M2 self-tappers so it can't turn: M2 × 6, or M2 × 8 on the base disc horn.
   - Shoulder and elbow: the MG996R **double-arm** horns into the pockets on the back faces of the upper link and the forearm, along the link's long axis, 2 screws each.
   - Base: the MG996R **Ø25 disc horn** flat on the turntable's underside, centred on the Ø3.6 hole (deep review 03, SYS-05: the disc carries the disk ±12.5 mm in every direction), with **4 × M2 × 8** through 4 of its holes (links strength round 4). Use 4 holes in opposite pairs on one circle at r ≥ 7 mm (§2). Drill each pilot 1.5 mm **6 mm deep** into the disk, with a tape flag on the drill, and no deeper: the disk is 8 mm, and its bottom 6 mm is printed solid for these screws. Opposite pairs let §5's half turn reuse the same pilots.
     - If your disc has no circle of 4 holes at r ≥ 7 mm: 4 holes in opposite pairs at r 5–7 mm still hold (safety factor ≥ 3.6). Or use 3 holes on one circle at r ≥ 7 mm (≥ 3.8), but then §5's half turn needs 3 fresh pilots. Anything less: tell Claude before drilling.
   - Wrist: the MG90S **single-arm** horn into the pocket on the claw frame's back face, arm towards the bulkhead, 1 screw.
4. **Turntable, before the shoulder servo** (the servo body covers the centre hole once it's in).
   - Push the turntable's disc horn onto the base servo's spline with the upright's **front face towards +Y**: the shoulder shaft will come out of that face, and the arm then reaches out over the +X (USB) wall at `b 0`.
   - Drive the M3 × 14 socket head + Ø9 washer from the top. An L-key or a screwdriver with a 75 mm shaft clears the upright.
   - The disk should now turn 0.3–0.4 mm above the taped ring all round. Where it rubs, sand the ring's top; where the gap is bigger, add a second layer of tape there.
   - **Then** put the shoulder MG996R through the upright's window from the front (+Y side), case bottom first, shaft facing forward, body horizontal, its lead through an end notch. Fix it with 4 × M3 × 12 + washers: their tips stand 2 mm out of the upright's back face.
5. **Upper link.**
   - Put the elbow MG996R into the link's far window from the front face, case bottom first, shaft forward, lead through a notch: 4 × M3 × 12 + washers.
   - Push the link's horn onto the shoulder spline with the link **straight up**, and fit the M3 × 14 + Ø9 washer.
6. **Forearm** (deep review 03, SYS-03).
   - File the slit that runs from the lead-end tab's hole to the tab's end to 2.1 mm wide with a needle file: that pilot is moved 1.3 mm out, beside the lead notch (deep review 01, B1). Check that an M2 passes, then fit the wrist MG90S into the forearm's far window from the front face, case bottom first, shaft forward, its lead in the notch at the shaft end, between the two ribs on the back face. Screws: **M2 × 12 in the lead-end tab, M2 × 16 in the far tab**, whose pilot runs 16 mm deep through the cross-rib on the back face (links strength round 4).
   - **Screw-strip check.** The plastic between the window and each screw hole is only about 1.5 mm wide, under the project's 1.8 mm rule; you chose to keep it and check it instead (26 Oct 2026). Drive both screws snug, no more, then look at the two strips. If either has turned white or cracked, stop and tell Claude: the screw holes move out and the forearm is reprinted.
   - With the elbow servo at its centre, push the forearm onto the elbow spline **60° below the upper link's line, bent towards +X**: with the upper link straight up, the forearm points 30° above horizontal, out over the USB wall. Check it with a protractor or a phone level, take the spline position nearest 30°, and fit the M3 × 14 + Ø9 washer. The trims in §5 take out the rest.
7. **Claw frame, before the claw servo** (its body covers the wrist clamp screw).
   - Push the frame, with its horn, onto the wrist spline **in line with the forearm**.
   - Put the Ø8 washer on the M2 × 12 and drive it from the front, through the centre hole in the raised pad. The washer slides down the shallow round groove in the bulkhead's back face and lies flat on the pad.
8. **Claw servo, from the front.**
   - File its lead-end tab's slit to 2.1 mm as in step 6.
   - Feed its plug through the bulkhead's window from the front, then push the MG90S in after it, **case bottom first**, shaft pointing at the fingertips, the ribbon flat in the notch at the shaft end, until the tabs sit on the bulkhead's front face. Fix it with 2 × M2 × 8 self-tappers.
   - **Screw-strip check,** as in step 6: drive both screws snug and look at the strips beside the screw holes. White or cracked: stop and tell Claude.
   - **Direction.** Push a horn loosely onto its spline as a pointer and type `g 20`. Seen from the front, the spline must turn **anticlockwise** to open the claw. If it turns clockwise, set `GRIP_OPEN_DIR = -1` and `GRIP_CLOSED_DEG` to about 160 in the sketch and re-flash. Type `f` and take the pointer off.
9. **Cover, then the camera mount.**
   - First snap off the cover's two **support pillars**: the thin posts inside the round hole in its front plate, one under each side piece. Grip each with pliers and break it off at its foot, then trim any nub flush with a knife: the pinion passes 0.45 mm from the hole's edge.
   - **Before the cover goes on, form the anchor's thread and look at the groove** (claw round 6 review): drive the M3 × 45 straight down into the pilot in the rail block's top, beside the V-groove, about 10 mm deep (20 turns), then back it out. Look at the groove beside the pilot: no split or bulge. If there is one, stop and tell Claude.
   - Lower the cover onto the frame: the front plate slides down past the wrist plate's front edge, the lip goes in front of the claw servo's case, and the ridge under the inner post drops into the V-groove in the rail block's top. The ridge, not the top wall, carries the cover: the top wall comes to rest a hair above the bulkhead (about 0.15 mm at the end where the lower slot is open) until the screws pull it down.
   - **Check the inner post's seat before any screw goes in.** Inside the cover, at the end where the lower slot is open, an 8 mm post runs down behind the racks' channel. A small ridge along its foot sits in a V-groove in the frame's rail block (the block behind the lower rack); the groove is open at that side of the claw. The post's outer face is flush with that side, so the joint shows there as a line, and by design there is a 0.3 mm gap between the post's foot and the block beside the ridge. Press the top wall straight down by hand **directly over the inner post** (over the third hole), not behind the lip and not on the front plate: either of those tips the cover and closes the gap. Use a feeler blade **at least 10 mm wide**, slid in flat from that side across the whole bulkhead top (and the rib beside it); a narrow blade can find the open end of a wedge-shaped gap. With the cover pressed down that way, a 0.03 mm feeler **must** go in between the top wall and the bulkhead at that end (the ridge, not the top wall, carries the cover). If it doesn't, stop and tell Claude. Then drive the M3 × 45 + washer snug **first**, then the M2.5 and M3 screws; afterwards a 0.3 mm feeler (the same wide blade) must not go in there.
   - **Anchor screw, first:** put the Ø7 × 0.5 washer on the M3 × 45 socket head. The screw goes into the third hole in the top wall, 4 mm in from the side where the lower slot is open and about 21 mm behind the front plate's face. It runs straight down through the post into the rail block. Drive it with a 2.5 mm L-key from directly above, **snug only** (≤ 0.09 N·m: stop when the washer seats and the key just stiffens). It seats the ridge in the groove and centres it. Do it before the camera goes on in step 13: the Brio sits over it. To reach it later, take the camera off its mount (thumb screw) first.
   - Then fix the front with 2 × M2.5 × 16, each with a Ø6 × 0.5 washer under its head, into the wrist plate's edge. **Snug only:** stop when the washer seats.
   - Then fix the top with 2 × M3 × 14, each with a Ø7 × 0.5 washer under its head, **snug only** (as the anchor), or put the camera mount on now and use 2 × M3 × 18 button heads through both, each with a Ø7 × 0.5 washer under its head, snug only (step 13).
   - **Check again:** the 0.3 mm feeler (blade at least 10 mm wide) must **not** go in between the top wall and the bulkhead at that end. If it does, stop and tell Claude.
10. **Jaws, slid in to fully open** (deep review 03, SYS-01). Without the pinion they slide freely. The front plate has two slots: the upper one is open on one side of the claw, the lower one on the other.
    - Jaw A: rack teeth facing the claw's middle, finger pointing forward. Slide its rack into the **upper** channel (under the top wall) from the side where the upper slot is open, neck in the slot, until its grip face is 22 mm from the claw's centre line.
    - Jaw B: the same part turned upside down. Slide it into the **lower** channel (on the wrist plate) from the other side, where the lower slot is open, until its grip face is 22 mm from the centre line too: the grip faces are now 44 mm apart.
11. **Pinion, last, pushed in axially through the front plate.**
    - Cut both arms of the MG90S **double-arm** horn **5.5 mm from the centre** with flush cutters and file the ends round, so the horn fits a Ø11 circle.
    - Press the horn into the pinion's back pocket. It's a light fit that centres the pinion on the horn (deep review 03, SYS-08); glue it only after the run in step 12.
    - Type `g 44`: the claw servo turns to its fully open angle.
    - Push the pinion, horn first, through the round hole in the front plate onto the spline. Its teeth slide into both racks at once. If they don't, nudge one or both jaws along their channels by up to half a tooth (1.6 mm), or turn the pinion by one spline tooth, until it slides home.
    - Drive the M2 × 12 + Ø6 washer through the pinion's front counterbore into the spline. The head sits about 1 mm below the pinion's face.
12. **Claw calibration.**
    - Type `g 10`, then `k 20`: `k` sets the claw's closed servo angle and closes the claw to it by itself. Listen during the first 2 s: a closing move squeezes for at most 2 s and then eases off, so a buzz only shows then. If it buzzed, type `g 10` again and try `k 22`, `k 24`, …; if a gap is left between the grip faces, try lower values. Stop at the value where the faces just touch without a buzz. With `GRIP_OPEN_DIR = -1`, start at `k 160` and step the other way. The ESP32 keeps the trim; copying the printed `GRIP_CLOSED_DEG` into the sketch is optional.
    - Run `g 44` and `g 0` a few times: the jaws must run without a tight spot or a click anywhere over the stroke. A tight spot means a rack isn't riding on its guide or the pinion isn't centred on its horn; then glue the horn with a drop of CA.
    - Then do §5's claw scale check (`g 40`).
    - **Service** is the same in reverse: `g 44`, the M2 screw out, the pinion out through the front hole, then the jaws out of the slots' open ends, the cover off (the M3 × 45 anchor first; take the camera off to reach it), and the claw servo out to the front. With a dead claw servo, pull the jaws open by hand first; that back-drives the servo you are replacing anyway.
13. **Camera (optional).**
    - Take the clip off the Brio (Logitech's quick-start guide shows how, in its tripod section).
    - If not done in step 9, screw the camera mount onto the cover with the 2 × M3 × 18 button heads, each with a Ø7 × 0.5 washer under its head, snug only.
    - Hold the camera on the tilted seat against the rear lip, lens towards the fingers. Turn the 1/4"-20 × 5/16" thumb screw up into it from below until snug. The thread is in the camera's plastic, so don't force it.
    - Plug the **right-angle** USB-C plug into the port on the camera's **back**, turned so the cable runs along the camera, and route it as in step 14.
14. **Leads and cables** (deep review 03, SYS-10).
    - Extensions: 50 cm on the claw and wrist leads, 30 cm on the elbow lead. Put the junctions outside the base's cable slot or on the turntable side, never at a joint.
    - Run each lead along its links in spiral wrap. Tie it with a zip tie around the link 6–14 mm from each joint axis on both sides of the joint, and leave a free loop over the joint. Run each joint slowly through its window (§5) and check the loops never pull tight.
    - Cross every joint **around the outside of the servo body**, never through the 2.6–5 mm gap between a link's back face and the servo case behind it: the horn turns there.
    - The upper link and the forearm have 6 mm ribs on their back faces along both sides of each servo window. Lay the bundle along a link's edge or over a rib, and put the zip ties round the whole link, ribs and servo included.
    - **Yaw loop:** tie the bundle to the upright's rear gusset and to a clip at the base's cable slot. About 60 mm of slack then hangs in a vertical loop outside r 52 mm, never under the disk's rim, where the ring's tab screws are.
    - **Racks:** at 44 mm open each rack sticks 15 mm out of the claw's sides (front half of the claw). Keep every tie and cable behind the bulkhead.
    - **Camera cable:** stick an adhesive cable-tie mount on the claw frame's bulkhead, on the side the cable leaves the camera, and tie the cable there with a short strain-relief loop between it and the plug, so a tug never reaches the plug. Tie it again on the forearm 10–15 mm behind the wrist axis, with a 60 mm loop between the two ties outside the wrist servo, then along the forearm and upper link with a loop at the elbow, shoulder and base, and on to your PC.
15. **Screw the base down, last.**
    - 4 × M3 × 50 wood screws through the corner pillars into the desk, or into a board of at least 200 × 200 mm and 0.4 kg (12–18 mm plywood or MDF) with the rubber feet under the board. Or fix 1.3 kg of ballast inside the base (0.95 kg without the camera). Free-standing, the arm tips over in every extended pose (deep review 03, SYS-12).
    - **Keep-out zones** (SYS-17): the claw and camera sweep a circle of about 300 mm radius round the yaw axis. With the shoulder past 90° the arm reaches the desk behind the base, over the jack and the cable slot, so run the 6 V lead and the cables away from there. The ESP32's USB cable leaves the +X wall under the main pick zone: use a right-angle plug and keep the cable flat on the desk. The camera and its plug stand 155 mm out sideways from the yaw axis.

## 5. First power-up, calibration and joint limits

**Power order:** plug in the ESP32's USB first, then switch on the 6 V. The servo signal pins float until the sketch starts, and a servo can twitch on a floating signal (the optional 10 kΩ pull-downs stop that). **Type `r` before you switch off:** the arm then rests upright, where the shoulder holds almost nothing, and the sketch restarts it there.

**Start-up.** The sketch keeps the pose, the joint trims and the claw trim on the ESP32 (NVS). After a reset (power-up, or the PC opening the serial port) it restarts each servo where it stopped, one at a time: claw, wrist, elbow, shoulder, base, 0.4 s apart. Nothing moves unless the arm was pushed or sagged while it was off; then that joint snaps back at full servo speed, which is why you park before switching off. If a re-flash changed the limits or trims, it then moves the arm slowly back inside them. The `k` trim survives re-flashing, but a re-flash with a different `GRIP_OPEN_DIR` or `GRIP_CLOSED_DEG` drops it.

**Angles.** Every command uses joint angles as the CAD defines them (`assembly_check.py`), not servo angles:

| Joint | Command | Range | 0 is | + is |
|---|---|---|---|---|
| Base | `b <deg>` | −90 … 90 | the arm along +X, out over the ESP32's USB wall | anticlockwise, seen from above |
| Shoulder | `s <deg>` | 0 … 180 | upper link horizontal towards +X; 90 = upright | up |
| Elbow | `e <deg>` | −150 … 30 | forearm in line with the upper link | up; − folds the forearm down, towards the desk |
| Wrist | `w <deg>` | −90 … 90 | claw in line with the forearm | fingertips up |
| Claw | `g <mm>` | 0 … 44 | closed | wider |

`c` puts every servo at its centre, the pose §4 fits the arm's horns in: base 0, shoulder 90, elbow −60, wrist 0, claw closed. The claw's pinion is the exception: it goes on last, pushed in through the cover with the jaws fully open at `g 44` (§4 steps 10–11). The elbow's window is −150 … +30 because its horn goes on with the forearm 60° below the upper link's line, so it spends its travel on the desk side. `ELBOW_MIN` and `ELBOW_MAX` near the top of the sketch narrow it; every joint's mapping (pin, pulses, direction, centre, limits) is one line of the `joints[]` table.

**Commands** (Serial Monitor at 115200, line ending "Newline"):

| Command | Does |
|---|---|
| `b`, `s`, `e`, `w` `<deg>` | one joint to an angle, clamped to its limits |
| `g <mm>` | claw opening, for an empty claw |
| `h <mm>` | hold an object that is `<mm>` wide (see Holding) |
| `r` | rest: park upright (see Parking) |
| `i <s>`, `i` | park after `<s>` seconds without a command (`i 0` = never); `i` alone shows it |
| `t`, `t <b\|s\|e\|w> <deg>`, `t save` | show the trims; set one; keep them on the ESP32 (see Trims) |
| `c` | every servo to its centre, claw closed: the pose §4 fits the arm's horns in |
| `f`, `k <deg>` | claw to its closed angle, like `g 0`; set that angle (§4 step 12) |
| `u <joint> <µs>` | a raw pulse for §4's end-stop test. It ignores the limits and the guard |
| `p` | print the angles; moves nothing |
| `x` | stop the move where it is; no later command resumes it |
| `m`, `?` | for a PC program (§6) |

A command without a valid number (`s`, `s abc`) is refused with `err`. While a move runs, `?` answers at once, `x` stops it, and one more command can wait for it to end.

**Moves** ramp up and down at 250 °/s² to 66.7 °/s, with every joint arriving at the same time and pulses in 1 µs steps (0.09°). With the arm straight out, the ramps ask the shoulder for about 45–65 N·mm and the yaw for 60–85 N·mm on top of their load, where a start in one step asked for 800–1 500 N·mm (deep review 03, SYS-06; inertia from `torque_budget.py`'s masses, 0–50 g payload). So the camera no longer shakes when a move ends. `SPEED` and `ACCEL` near the top of the sketch set them; keep `ACCEL` within 200–300. In vision code, still wait about 200 ms after a move before you grab a frame.

### Directions (first)

The sketch can't tell which way each servo turns, and the guard is only right when it knows. Set the directions before anything else, with the claw empty and the switch within reach.

1. Type `i 0` (no parking while you work), then `c`. The forearm now leans 60° to one side: that side is the front, +X.
2. Type `s 80`: the upper link must tip towards the front. Type `c`.
3. Type `e -70`: the forearm must fold further down. Type `c`.
4. Type `w -10`: the fingertips must drop. Type `c`.
5. Type `b 10`: seen from above, the arm must turn anticlockwise. Type `c`.
6. For each joint that went the other way, change its `dir` from `+1` to `-1` in the `joints[]` table, re-flash and check it again.

### Trims (calibration)

A horn goes onto its spline in steps of 14.4° (MG996R) or about 17–18° (MG90S), so a joint can sit up to 7–9° from the angle it was fitted at. At full reach that puts the fingertips up to 36 mm (base), 34 mm (shoulder), 22 mm (elbow) or 12 mm (wrist) from where the sketch thinks they are, and moves every limit and the guard with them (deep review 03, SYS-07). A trim corrects this: the angle the sketch adds to that joint before driving its servo. Use a square or a phone level (inclinometer mode).

1. Type `r`: the arm parks upright (shoulder 90, elbow 0, wrist 0).
2. **Shoulder.** Hold the square on the base's top plate against the upper link's edge, or the phone along the edge. If the link leans n° towards the front, type `t s n`; if it leans back, `t s -n`. Repeat until it is vertical.
3. **Elbow.** The forearm must continue the upper link's line, vertical. Check it the same way and set `t e`.
4. **Wrist.** The claw must continue the forearm's line. Check a finger blade's flat side and set `t w`.
5. **Base.** At `b 0` the upright's front face is parallel to the base's ±Y walls. On the base's top plate, measure from its +Y edge to the upright's front face near each end of the upright (they are 66 mm apart). One degree off makes the two differ by 1.2 mm. If the gap is smaller at the +X end, the arm is turned anticlockwise: type `t b -n`. If it is larger, type `t b n`.
6. **More than 3.6° on the base, shoulder or elbow:** turn that MG996R's horn half a turn on its part. On the 25-tooth spline the two positions are half a tooth (7.2°) apart, so one of them is within ±3.6°.
   - Type `c`.
   - **Shoulder or elbow:** undo the link's M3 × 14 clamp screw and take the link off its spline. Unscrew the double-arm horn from its pocket, turn it end-for-end and screw it back: the drilled holes still match.
   - **Base:** its Ø25 disc horn is screwed under the turntable, so it comes off with the turntable. Undo the turntable's M3 × 14 clamp screw from the top (an L-key reaches it past the upright) and lift the turntable off the spline. Turn the disc horn half a turn on the turntable's underside and screw it back into the same pilots: its 4 screws sit in opposite pairs (§4 step 3).
   - Push the link or the turntable back on at the spline position nearest its §4 fitting pose and refit the clamp screw. Type `t <joint> 0` and redo that joint's step.
7. `t` shows the trims. `t save` keeps them on the ESP32; without it, a reset brings back the last saved ones. Type `i 60` to switch parking back on.

The trims come before the limits and the guard, so those work on the real joint angles. A trim shortens its joint's window at one end, because the servo's own 0–180° doesn't move: with `t e 5` the elbow reaches −145, not −150.

### Guard: desk, base and turntable

Limiting each joint on its own doesn't keep the claw or the camera off the desk. And with the elbow folding to −150°, the forearm and the claw can also come down onto the base or the turntable. So before every move the sketch walks its path with a side view of the arm, every part a box measured from the CAD. The move ends early, ramping down to the last allowed point, where a part would come within 8 mm of:

- the desk (`blocked: desk`);
- the base (110 × 104 mm, turned with the yaw), the turntable disk or the support ring (`blocked: base`).

It checks every step again while the move runs. From a pose that is already too close, a move may only get clearer.

- **Checked against the CAD meshes** over 52 000 poses: shoulder 0–180, elbow −150–30, wrist ±90, claw closed and open, base contacts at yaw 0, ±45° and ±90°, the Brio with its right-angle plug and thumb screw (`firmware_test/guard_mesh_check.py`). No pose closer than 8 mm to the desk and no contact got through. The guard also blocks 0.4 % of the poses that clear the desk by 8 mm, and near the base 0.7–1.9 % that touch nothing.
- **Desk reach with the guard.** With the claw pointing straight down, the fingertips come to 11 mm above the desk (the ends of the tips stay 8 mm up) from 60 to 200 mm out along the arm. That is 103–217 mm from the yaw axis, because the fingertips sit 84 mm to its side, or 99–223 mm with the claw up to 5° off straight down. The elbow's −150° stop and the shoulder's 0° stop set those ends, not the guard. At yaw ±90° the near limit is 84 mm out along the arm (119 mm from the axis), because the jaws then pass the base's side wall. With the claw tilted further, the fingertips come within 16 mm of the desk from 90 mm (107 mm at yaw ±90°) to 271 mm from the yaw axis.
- **Why the top of this guide says 88–263 mm** (98–220 mm with the claw within 5° of straight down): those count every pose that touches nothing with the fingertips 0–8 mm above the desk. The guard keeps every part 8 mm off the desk and the base instead. With the claw near straight down that only lifts the fingertips 8 mm; the same stops set the ends. At other claw angles the guard also gives up the nearest poses, where the claw points down and back right beside the base's wall, and its far end is further out only because the fingertips are higher.
- **Without the Brio,** set `CAMERA_FITTED = false`: the wrist may then come closer to the desk.
- The guard takes the desk to be level with the underside of the base, which is screwed down on it. It knows nothing else on the desk, nor your hands.

**Check it** once the directions and trims are set:

1. Type `i 0`, `r`, `s 0` (the arm straight out), then `e -90`. It should stop with `blocked: desk` when the forearm is about 26° below horizontal (30° without the camera).
2. Type `r`, `e -150`, `w -30`, then `s 15`. It should stop with `blocked: base` at about `s 61` (the claw's front plate reaches 6 mm below its back face).
3. If either keeps going, type `x` and check the directions again. Type `r` and `i 60`.

### Holding something

The sketch can't feel an object, and an MG90S held stalled draws about 0.7 A and heats itself and the PETG around it within minutes (deep review 03, SYS-11).

- **Grip with `h`.** Measure the object, open the claw wider (`g`), then type `h` and its width, e.g. `h 20`. The claw closes to 1.5 mm under the width (`GRIP_SQUEEZE_MM`).
- **Squeeze limit.** Every move that closes the claw squeezes for at most 2 s (`GRIP_SQUEEZE_MS`). Then the servo eases off 1.5° (`GRIP_BACKOFF_DEG`, about 0.5 mm), holds there and prints `claw eased off to … mm`.
- **`g 0` (and `f`) is for an empty claw.** On an object it stays stalled, because easing off 0.5 mm doesn't reach the object's width.

**Claw scale:** type `g 40` and measure the gap between the grip faces with calipers. It should be 40 ± 1 mm. If not, the claw servo turns more or less than 180° between its `minUs` and `maxUs`: set `DEG_PER_MM` to 2.865 × 40 / (the measured gap) and re-flash.

### Parking

With the camera, holding the empty arm straight out takes 57–63 % of the shoulder MG996R's stall torque (sliced or solid parts, `torque_budget.py`), more than it can hold for long (deep review 03, SYS-02). Upright (shoulder 90, elbow 0, wrist 0) the shoulder holds about 2 N·mm.

- `r` parks now. The base and the claw stay as they are, so a held object stays held.
- After 60 s without a command (`IDLE_PARK_S`) the arm parks by itself and prints `idle 60 s: parking`. **So it can move on its own.**
- `i 120` changes the time and `i 0` switches it off. The ESP32 keeps the setting. Any command counts as activity, `?` too.

Then do the **proof tests** in each part's `spec.md` §8, for example 1 kg hung at the elbow axis for 1 minute with the shoulder holding (type `i 0` first). The claw's grip tests are there too. The strength verdicts rely on them, because there's no measured PETG data in `library/` yet. Record the results in each job's `inspection.md`.

## 6. Driving it from a PC, with the camera

The Brio plugs into your PC, and the ESP32's USB port takes commands from the same PC. `pc/arm_pc_control.py` is a starting point. Install its dependencies with `pip install pyserial opencv-python`. It uses the sketch's joint angles (§5). Positions are in mm from the yaw axis on the base's top plate: +X out over the USB wall, Z up, the desk at Z = −40.

- **Preview.** `python pc/arm_pc_control.py --port COM5 preview --object-mm 20 --focus 200` shows the camera with a crosshair.
  - Keys: `o` opens the claw, `c` grips an object of the `--object-mm` width, `[` and `]` move the wrist, `p` parks, `,` and `.` step the focus, `q` quits. Without `--object-mm`, `c` only reminds you to measure the object.
  - It asks the camera for MJPG at 1920 × 1080 and 30 fps, because uncompressed 1080p doesn't fit through USB 2.0, which many thin cables are. It prints the size it got.
  - Camera 0 is often a laptop's own camera: if the picture isn't the Brio's, use `--camera 1`.
- **Move.** `… move 0 60 -90 -50 20` moves every joint together (base, shoulder, elbow, wrist in degrees, claw in mm) and waits for `ok`. A move the guard ends early exits with `arm: blocked: desk` or `arm: blocked: base`.
- **Approach, grip, park.** `… approach 160 80 -25 --open 30` brings the fingertips to (160, 80, −25) from above.
  - It moves to 40 mm above the point with the claw open, then down in 10 mm steps.
  - The claw points straight down, or at most 45° off it where straight down is out of reach. So the camera stays at least 10 mm above the fingertips, and the claw meets the object before the camera does (deep review 03, SYS-11).
  - Then `… grip 20` holds a 20 mm object and `… park` parks.
- **In your own code,** `Arm(port)` gives `move()`, `status()`, `grip()`, `park()`, `approach()`, `idle_park()` and `stop()`. They use the sketch's `m`, `?`, `h`, `r`, `i` and `x`.
  - `move()` returns True when every joint arrived and False after `stop()`.
  - They raise `RuntimeError` when the sketch refuses (`err …`) or the guard ends the move (`blocked: …`), `TimeoutError` when the arm doesn't answer, and `ValueError` for a NaN or unreachable target.
  - `ik()`, `fingertip()` and `plan_approach()` do the kinematics, including the fingertips' 84 mm sideways offset from the yaw axis. `guard_margins()` is the sketch's own guard, for planning.
- **Keep one connection open** for a whole session, as the preview does, rather than running the script once per move. It opens the port with DTR and RTS off, which keeps most PCs from resetting the ESP32, but not all. After a reset the sketch restarts where the arm stopped, which takes about 2 s.
- **Parking.** The arm parks after 60 s without a command. If your program pauses longer and the arm must hold its pose, call `status()` now and then, or `idle_park(0)` and then `idle_park(60)` when it finishes (the sketch keeps the setting).

**Camera** (deep review 03, SYS-13):

- The camera is mounted turned 90° to the arm. With the claw level, "up" is at the right of the raw image; the preview rotates it upright.
- In Logi Tune, choose the **65° field of view**: the closest view of the jaws, where a 16 mm cube held between the fingertips fills about 8 % of the frame.
- **Check and lock the focus at about 83 mm**, the fingertips' distance from the lens. Logitech publishes no close-focus distance, and autofocus hunts on the jaws.
  1. Start the preview with `--focus 200`.
  2. Step it with `,` and `.` until the fingertips are sharp.
  3. Pass that value to `open_camera()` in your own code.
- **Crop the bottom 46 %.** The claw's own cover fills the bottom 44 % of the raw image at 65° (46 % at 90°): the right-hand side of the upright preview, past the orange line. In vision code, cut 46 % off with `crop_claw(frame)`, on the raw frame. If you use the 90° view, set `CLAW_ROWS` near the top of `arm_pc_control.py` to 0.48.

## 7. Safety

- Keep your fingers out of the claw and the elbow while the arm is powered. At stall the claw pushes 10.8 N per jaw (21.6 N into one jaw if the other is blocked), and an MG996R stalls at about 1 N·m.
- **The arm moves on its own:** it parks after 60 s without a command. Switch the 6 V off, or type `i 0`, before you reach into it.
- The switch on the 6 V lead is the emergency stop. `x` stops a move from the keyboard.
- The guard keeps the arm 8 mm off the desk, the base and the turntable, and off nothing else: not your hands, not the camera cable, not things on the desk. It is only right once the directions are set (§5), and `u` ignores it.
- Don't hold a servo stalled: it overheats, and so does the PETG near it. Hold objects with `h <width>`, and trim `k` so that `g 0` doesn't squeeze an empty claw. The sketch eases any squeeze off after 2 s, but a wrong width still leaves the claw servo stalled.
- Unplug the 6 V supply before working on the wiring.

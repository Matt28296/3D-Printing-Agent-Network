# Desktop robot arm: build guide

Robot 1 of 3 (then the tracked rover, then the hexapod). 4 joints plus a gripper, 5 hobby servos, ESP32 DevKit, 6 V supply, PETG.
Reach is 304 mm horizontal, the fingertip touches the desk from about 75 to 236 mm out, payload about 50 g.

## 1. Bill of materials

### Printed (PETG): 8 parts, one SD-card file each
| # | Part | Job | Print orientation |
|---|---|---|---|
| 1 | Base | `20261025-arm-base` | upside down (top plate on bed) |
| 2 | Turntable support ring | `20261025-arm-turntable-ring` | flat, tabs down |
| 3 | Turntable + shoulder upright | `20261025-arm-turntable` | disk on bed |
| 4 | Upper link (100 mm) | `20261025-arm-upper-link` | flat, horn pocket down |
| 5 | Forearm (90 mm) | `20261025-arm-forearm` | flat, horn pocket down |
| 6 | Gripper base + fixed jaw | `20261025-arm-gripper-base` | flat, horn pocket down |
| 7 | Moving jaw | `20261025-arm-gripper-jaw` | flat, horn pocket down |
| 8 | ESP32 cradle | `20261025-arm-esp32-cradle` | as it hangs (frame bottom down) |

Print times and filament for each part are in its `slice_stats.json` (see the summary table in `README.md` next to this file).

### Bought
| Qty | Item | Notes |
|---|---|---|
| 3 | MG996R servo (metal gear, 180°) | base, shoulder, elbow. Keep the bag: the **double-arm horn** and screws are used |
| 2 | SG90 micro servo (180°) | wrist, gripper. Keep the **single-arm horn** and screws |
| 1 | ESP32 DevKit (38-pin DevKitC or 30-pin DOIT) | pins soldered down |
| 1 | 6 V 5 A DC adapter, 5.5 × 2.1 mm plug | servo power. 5 A covers two MG996R stalling at once |
| 1 | 5.5 × 2.1 mm panel-mount DC jack (Ø11 mm thread) | goes in the base's −X wall |
| 1 | 1000 µF 10 V (or higher) electrolytic capacitor | across the servo supply, at the jack |
| 1 | 5 V buck module (e.g. MP1584 or LM2596, set to 5.0 V) | *optional*: runs the ESP32 from the 6 V supply without USB |
| ~15 | Female–female and female–male jumper wires, servo extension leads (2 × 30 cm) | the shoulder, elbow and wrist leads must reach the base |
| 3 | M3 × 6 self-tapping (pan head) | ring tabs (longer would reach the ESP32 under the plate) |
| 3 | M3 × 10 self-tapping (pan head) | cradle, from below into the counterbores (not longer: the boss pilots are 6 mm deep) |
| 3 | M3 × 16 screw + Ø9 (M3 large) washer | MG996R horn clamp screws: base, shoulder, elbow. Replace the short horn screw from the bag. |
| 2 | M2 × 12 screw + Ø6 washer | SG90 horn clamp screws: wrist, gripper |
| 4 | M3 × 50 (or #4 × 2") wood screws, or 2 desk clamps | **required**: base to desk or to a board. With the arm out, the arm tips the base over |
| — | Spiral cable wrap or zip ties, 4 rubber feet | tidy the servo leads along the links |

## 2. Before you print

1. **Measure your servos and horns.** The CAD uses nominal datasheet sizes (`tools/hobby_parts.py`). Measure body length and width, tab-hole spacing, shaft to near body end, the double-arm horn (hub Ø, centre-to-tip, tip width) and the SG90 arm horn. If anything differs by more than 0.3 mm, give the numbers to Claude; it updates `replace(MG996R, ...)` in each `model.py` and re-runs the pipeline.
2. Load PETG. The G-code is sliced with Prusa's stock **Prusament PETG** and **0.20 mm QUALITY** presets, on a smooth PEI sheet with glue stick or a release agent (PETG can bond too hard to bare smooth PEI).

## 3. Wiring

```
6 V adapter ─► DC jack ─┬─ 1000 µF (+ to +6 V) ─┐
                        ├─► servo V+ (red) × 5  │
                        └─► servo GND (brown) × 5 ─┴─► ESP32 GND   ← common ground is required
(optional) 6 V ─► 5 V buck ─► ESP32 5V/VIN pin          (or power the ESP32 from USB)

ESP32 GPIO ─► servo signal (orange/yellow)
  GPIO13  base yaw (MG996R)
  GPIO14  shoulder (MG996R)
  GPIO27  elbow (MG996R)
  GPIO26  wrist (SG90)
  GPIO25  gripper (SG90)
```

- Never power the servos from the ESP32's 5V/3V3 pins: the arm can draw several amps.
- Never connect the 6 V supply directly to the ESP32's 3V3 pin.
- Those GPIOs are not boot-strapping pins, so the board boots normally with the servos connected.
- Make a 5-way power bus (a small piece of stripboard, or Wago-style lever connectors) inside the base for V+ and GND.

## 4. Centre the servos, then assemble

The horns must go on with every servo at its centre position (90°), and the links in their neutral pose. Otherwise a joint's travel won't line up with the collision-free range.

1. Wire everything (section 3), flash `arm_test/arm_test.ino` (Arduino IDE, board "ESP32 Dev Module", library **ESP32Servo**), open the Serial Monitor at 115200 and type `c` to centre all five servos. Leave the power on while you fit the horns.
2. **Base:** screw the base to the desk or a board (4 × M3×50 wood screws through the corner pillars). Fit the cradle to the 3 bosses under the base top plate (M3×10 from below), drop the ESP32 in pins-down with its USB end against the +X wall slot. The cradle's −Y wall passes within 0.6–0.8 mm of the base servo's body: if your servo is wider than 19.7 mm, check that it still clears. Fit the DC jack, the capacitor and the power bus. Drop the base MG996R into the top-plate window, shaft up, and fix it with its 4 tab screws. Screw the ring on (3 × M3×6).
3. **Horns into the links:** press each horn into its pocket on the link's back face, double-arm horns along the link's long axis. Drill 1.5 mm pilots through two of the horn's arm holes into the plastic and screw the horn down with the small horn screws: they stop it turning. The **centre clamp screw** (M3×16 + washer on the big servos, M2×12 + washer on the small ones) goes in from the link's front face, through the link and the horn into the spline. It holds the link on, so tighten it firmly.
4. **Turntable, before the shoulder servo** (the servo body covers the centre hole once fitted): lay the base horn flat on the turntable's underside, centred on the Ø3.4 hole and pointing along X, and drill/screw it through two arm holes. Push it onto the base servo's spline with the upright facing **+X** and drive the M3×16 + washer from the top (a screwdriver with a shaft of 75 mm or more clears the upright). **Then** put the shoulder MG996R through the upright window from the front (+Y side), shaft facing forward, body horizontal, and fix it with 4 tab screws.
5. **Upper link:** fit the elbow MG996R in the link's far window (tabs on the front face, shaft forward). Push the link's horn onto the shoulder spline with the link pointing **straight up** (servo 90° = upright), then fit the clamp screw.
6. **Forearm:** fit the wrist SG90 in the forearm's far window, shaft forward. Push the forearm onto the elbow spline **in line with the upper link** (elbow 90° = straight).
7. **Gripper:** fit the gripper SG90 in the gripper base window. Push the gripper base onto the wrist spline **in line with the forearm**. Push the moving jaw onto the gripper spline with the jaws **closed**.
8. Run the leads down each link with spiral wrap, leaving slack at every joint, and through the base's cable slot to the bus and the ESP32.

## 5. First power-up and joint limits

Use the Serial Monitor commands in `arm_test.ino` to move one joint at a time (`s 100` sets the shoulder to 100°). The sketch clamps every joint to the limits found collision-free by the assembly check (`assembly_check.json`):

| Joint | Servo angle | Meaning |
|---|---|---|
| Base | 0–180 | yaw ±90° |
| Shoulder | 0–180 | 90 = upright; the link reaches horizontal at 0 or 180, depending on mounting side (check the direction with small moves first) |
| Elbow | 0–180 | 90 = straight (collision-free to ±140°, so the whole servo range is safe) |
| Wrist | 0–180 | 90 = straight (collision-free to ±130°) |
| Gripper | closed = 90, open = 90 ± 60 | test which direction opens first; the sketch's `GRIP_OPEN_DIR` sets it |

Then do the **proof tests** listed in each part's `spec.md` §8 (for example, 1 kg hung at the elbow axis for 1 minute with the shoulder holding). The strength verdicts rely on them, because there's no measured PETG data in `library/` yet. Record the results in each job's `inspection.md`.

## 6. Safety

- Keep fingers out of the gripper and the elbow while powered: an MG996R stalls at about 1 N·m.
- Don't hold a servo stalled for minutes: it overheats (and so does the PETG near it).
- Unplug the 6 V supply before working on the wiring.

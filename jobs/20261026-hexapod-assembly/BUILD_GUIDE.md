# Hexapod: build guide

Robot 3 of 3. Six identical 3-DOF legs on 18 MG90S servos, two PCA9685 servo drivers, ESP32, 2S LiPo. About 277 × 282 × 160 mm standing, ≈0.6 kg.

## 1. Bill of materials

### Printed (PETG)
| Part | Job | Qty per plate | Plates |
|---|---|---|---|
| Bottom body plate (with columns) | `20261026-hexapod-body-bottom` | 1 | 1 |
| Top plate / electronics deck | `20261026-hexapod-body-top` | 1 | 1 |
| Coxa bracket | `20261026-hexapod-coxa` | 6 | 1 |
| Femur | `20261026-hexapod-femur` | 6 | 1 |
| Tibia | `20261026-hexapod-tibia` | 6 | 1 |

Print times and filament: see `README.md` next to this file.

### Bought
| Qty | Item | Notes |
|---|---|---|
| 18 | MG90S metal-gear micro servo (180°) | keep the single-arm horns and screws |
| 2 | PCA9685 16-channel servo driver | solder the A0 jumper on one board: addresses 0x40 and 0x41 |
| 1 | ESP32 DevKit (38- or 30-pin), headers pins down | |
| 1 | 2S 1000 mAh LiPo, 20C or more, XT30 connector (≈70 × 35 × 18 mm) | charge only with a balance charger. A JST lead (≈5 A) is too small for 18 servos |
| 1 | UBEC: 2S-compatible input (≈5.5–26 V), 6 V output, 5 A continuous or more, 8–10 A preferred | servo rail: both PCA9685 V+ terminal blocks. Walking draws 3.3–4.7 A, with 10–14 A surges every gait frame. "HV" UBECs that need 3S or more won't hold 6 V on a 2S pack |
| 1 | MP1584 buck module, set to 5.3 V | ESP32 5V/VIN, through the Schottky diode below |
| 1 | Toggle or rocker switch rated 10 A DC or more | in the battery lead, after the fuse |
| 1 | 7.5 A blade fuse and an inline fuse holder (18 AWG) | in the LiPo + lead, before the switch |
| 1 | XT30 female pigtail, 18 AWG leads | from the LiPo's plug to the fuse and switch |
| 1 | LiPo voltage alarm (buzzer), 2S | plugs into the balance lead: beeps when a cell runs low. It is the only cut-off for the UBEC, the buck and the ESP32 |
| 1 + 1 + 1 | 100 kΩ and 33 kΩ resistors (1 %), 100 nF ceramic capacitor | battery voltage divider to GPIO35: the sketch stops walking on a flat pack |
| 1 | SS14 or 1N5817 Schottky diode | buck OUT+ to the ESP32's 5V pin: USB can't feed back into the LiPo side |
| 1 | 1000 µF 10 V capacitor, in addition to the one below | bulk capacitance on the servo rail: one across each PCA9685's V+ terminals (Adafruit: n × 100 µF, here 1800 µF) |
| 6 | Servo extension leads, 15 cm (20 cm if in doubt) | for the femur servos: their leads fall up to 31 mm short even by the deck-edge route. With the 6 for the tibias, 12 in all |
| 1 | 2S LiPo balance charger | the only way to charge the pack |
| 1 | LiPo charging bag | charge and store the pack in it |
| 1 | 1000 µF 10 V capacitor | across the servo rail |
| 12 + 6 | M2 × 12 screws (femur, tibia) and M2 × 10 screws (coxa), + 18 M2 washers (Ø6) | horn clamp screws (replace the short horn screw from each bag). The coxa hub has a 3 mm floor, so its screw is 2 mm shorter |
| 36 | M2 × 8 self-tapping screws | servo tab screws (the bag screws may be too short in the 4.5–7 mm plates) |
| 4 | M3 × 8 self-tapping screws | top plate onto the columns |
| 8 | M2.5 × 6 self-tapping screws | PCA9685 boards |
| — | velcro strap, zip ties, 6 servo extension leads (15 cm) for the tibia servos, jumper wires | |

## 2. Wiring

```
LiPo (XT30) ─► 7.5 A fuse ─► switch (10 A DC) ─┬─► UBEC 6 V ─► servo rail: each PCA9685's V+ / GND terminal block
                                                │               (1000 µF across each board's V+)
                                                ├─► MP1584 5.3 V ─► SS14 ─► ESP32 5V/VIN (≈ 5.0 V)
                                                └─► 100 kΩ ─┬─► ESP32 GPIO35 (battery voltage)
                                                            └─► 33 kΩ ─► GND   (100 nF across the 33 kΩ)
LiPo balance lead ─► voltage alarm
All grounds common. ESP32 3V3 ─► both PCA9685 VCC (logic). The header's V+ pin stays unconnected.
ESP32 GPIO21 (SDA) ─► both PCA9685 SDA      ESP32 GPIO22 (SCL) ─► both PCA9685 SCL

PCA9685 0x40 (left legs)                       PCA9685 0x41 (right legs)
  ch 0,1,2   left front: coxa, femur, tibia      ch 8,9,10  right front: coxa, femur, tibia
  ch 4,5,6   left middle                         ch 4,5,6   right middle
  ch 8,9,10  left rear                           ch 0,1,2   right rear
```

- **Channels:** mount both boards with their servo headers along the outer edge. Seen from outside, channel 0 is at the left end (Adafruit layout): the front of the left board, but the rear of the right board. So each board's front leg is on the channels at its front end. If your right board has channel 0 at its front, change `2 - (leg - 3)` to `leg - 3` in the sketch's `writeServo()` and swap those two rows above.
- **Lead routing:** run each leg's three leads up the outside of the body beside that leg and over the deck edge to the headers. Through the four corner slots every femur lead is 44–122 mm short, so this route replaces the slots in section 3, step 5. Every femur and every tibia servo needs a 15 cm extension (12 in all). Leave slack loops of about 30 mm at the coxa and 20 mm at the femur.
- Set the buck to **5.3 V** with a meter **before** connecting the ESP32: the Schottky drops about 0.3 V. The diode stops the PC's USB port from feeding back through the buck into the LiPo side, the UBEC and the servos while the switch is off.
- Never put the LiPo straight on the servo rail: 8.4 V would destroy the MG90S servos.
- **Fuse, switch and alarm:** the LiPo has no protection of its own. The fuse goes in the + lead before the switch: a short in the hand wiring can draw tens of amps. Keep the voltage alarm plugged into the balance lead whenever the pack is connected.
- Feed each board through its V+ terminal block, not the 6-pin header, and leave the header's V+ pin unconnected on the ESP32 side: Adafruit warns that joining VCC and V+ can damage the board.
- Keep the UBEC's ground leads short and thick to the boards' terminal blocks, and twist SDA and SCL each with a ground wire. Otherwise part of the servo return current runs through the ESP32's ground and the I²C header.
- The UBEC's 6 V is the MG90S's maximum rating. 5 V is gentler on the servos if you can spare about 20 % of the torque.

## 3. Centre the servos, then assemble

Fit every horn with its servo at 90° (centre), so each joint's travel lines up with the collision-free ranges in `assembly_plan.md`.

1. Wire one PCA9685 and the ESP32 on the bench, flash `hexapod_test/hexapod_test.ino` (library **Adafruit PWM Servo Driver**), type `c` in the Serial Monitor (115200) to centre all channels. Plug each servo in briefly to centre it before fitting its horn.
2. **Horns into the links:** press each single-arm horn into its pocket on the link's bed-side face, arm along the link. Pilot-drill 1.2 mm through the horn's outer arm hole into the plastic and fit one small horn screw (it stops rotation). The M2 × 12 centre screw + washer goes through the link into the spline later, when the link goes onto its servo.
3. **Body:** fix the six coxa MG90S under the bottom plate, bodies up through the windows, shafts down, tab screws (M2 × 8) into the pilots. Strap the LiPo on top of the plate between them.
4. **Legs (×6):**
   - femur servo into the coxa bracket's vertical plate (tabs on the face away from the body, shaft outward-tangential)
   - tibia servo into the femur's window (tabs on the front face)
   - tibia onto the tibia servo, pointing **straight down** (servo at 90°) with the femur level
   - femur onto the femur servo, pointing **straight out**
   - bracket onto the coxa servo, pointing **radially out** from the body centre
   
   Drive each clamp screw firmly (M2 × 10 on the coxae, M2 × 12 on the femurs and tibias).
5. **Top plate:** fit the PCA9685 boards on the posts (M2.5 × 6), the ESP32 in its seat (zip tie) and the buck at the front of the deck (double-sided tape). The UBEC goes on its side on the bottom plate, beside the LiPo (double-sided tape), clear of the middle coxa servo. Bring the 18 servo leads up through the 4 cable slots (tibia leads need the 15 cm extensions). Screw the top plate onto the columns (4 × M3 × 8).

## 4. First steps

Flash `hexapod_test/hexapod_test.ino` (Arduino IDE, board "ESP32 Dev Module" on the arduino-esp32 3.x core; library **Adafruit PWM Servo Driver**, which also installs Adafruit BusIO: accept the prompt). Hold the robot off the ground and power up. At power-up the legs start one at a time, 150 ms apart, so the 18 servos don't all surge at once. In the Serial Monitor:

| Command | Does |
|---|---|
| `c` | centre all 18 servos (90°): femurs level, tibias vertical. Fit and check the horns in this pose |
| `t <n> <deg>` | trim servo n by <deg>, ±20° in total. n = leg × 3 + joint: legs 0–5 = LF, LM, LR, RF, RM, RR; joints 0–2 = coxa, femur, tibia |
| `p` | print the trims: copy them into the sketch's `TRIM[]` table |
| `s` | stand in the neutral stance |
| `w` | walk forward |
| `x` | stop and stand, within one 25 ms gait frame |
| `o` | measure the PCA9685 clocks (below) |

- If a joint moves the wrong way, flip its sign in `DIR[]`. The sketch keeps neighbouring coxae from closing more than the 70° the assembly check allows, and the femurs within −70…+90° and the tibias within −80…+90°.
- **Clock calibration, once per board:** a PCA9685's oscillator is 25 MHz typical but anywhere from about 23 to 27 MHz, and every servo pulse is off by the same ratio. Jumper the left board's channel-15 signal pin to GPIO34 and type `o`; copy the printed value into `OSC_L`. Move the jumper to the right board, type `o`, copy into `OSC_R`, re-flash and remove the jumper.
- **Gait:** a tripod gait with inverse kinematics. Planted feet move straight back along the ground, so none slides, and each swing lands exactly where the next stroke starts: 30 mm stride, 20 mm lift, 0.5 s per cycle. Each tripod swings for 40 % of the cycle, so all six feet share the load at each hand-over. The neutral stance (femur and tibia angles) and the leg geometry sit in one block at the top of the sketch.
- **Battery:** the sketch reads the LiPo through the divider. When it reads below 6.6 V twice in a row (3.3 V per cell under load), the hexapod stops walking and won't walk again until restarted: switch off and charge. Expect about 11–16 minutes of walking per charge, the shorter figure on carpet.
- Walking also needs both boards to answer. With one board on the bench (section 3, step 1) the sketch says which is missing, and `c`, `s` and `t` still work.
- If a servo twitches each time the Serial Monitor opens (the ESP32 restarts while the boards keep their power), hold the boards' OE pin high during start-up.

Then do the proof tests in each part's `spec.md` §8 and record them in `inspection.md`.

## 5. Safety

- Charge the LiPo only with a balance charger, inside its LiPo bag, never unattended. Never charge or use a swollen pack. Store it at storage voltage (3.8–3.85 V per cell) and unplug it after use.
- MG90S servos stall at ≈2 kg·cm: keep fingers out of the knees while powered.
- Unplug the LiPo before any wiring change.

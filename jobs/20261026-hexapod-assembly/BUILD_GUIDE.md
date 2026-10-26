# Hexapod: build guide

Robot 3 of 3. Six identical 3-DOF legs on 18 MG90S servos, two PCA9685 servo drivers, ESP32, 2S LiPo. About 277 × 282 × 146 mm standing, ≈0.6 kg.

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
| 1 | 2S 1000 mAh LiPo (≈70 × 35 × 18 mm) with XT30/JST lead | charge only with a balance charger |
| 1 | 6 V 5 A UBEC | servo rail: both PCA9685 V+ terminals |
| 1 | MP1584 buck module set to 5.0 V | ESP32 5V/VIN |
| 1 | Toggle or rocker switch | in the battery lead |
| 1 | 1000 µF 10 V capacitor | across the servo rail |
| 18 | M2 × 12 screws + 18 M2 washers (Ø6) | horn clamp screws (replace the short horn screw from each bag) |
| 36 | M2 × 8 self-tapping screws | servo tab screws (the bag screws may be too short in the 4.5–7 mm plates) |
| 4 | M3 × 8 self-tapping screws | top plate onto the columns |
| 8 | M2.5 × 6 self-tapping screws | PCA9685 boards |
| — | velcro strap, zip ties, 6 servo extension leads (15 cm) for the tibia servos, jumper wires | |

## 2. Wiring

```
LiPo ─► switch ─┬─► UBEC 6 V ─► servo rail: PCA9685 #1 and #2 V+ / GND terminals (1000 µF across)
                └─► MP1584 5.0 V ─► ESP32 5V/VIN
All grounds common. ESP32 3V3 ─► both PCA9685 VCC (logic)
ESP32 GPIO21 (SDA) ─► both PCA9685 SDA      ESP32 GPIO22 (SCL) ─► both PCA9685 SCL

PCA9685 0x40 (left legs)            PCA9685 0x41 (right legs)
  ch 0,1,2  left front: coxa, femur, tibia    ch 0,1,2  right front
  ch 4,5,6  left middle                        ch 4,5,6  right middle
  ch 8,9,10 left rear                          ch 8,9,10 right rear
```

Set the buck to 5.0 V with a meter **before** connecting the ESP32. Never put the LiPo straight on the servo rail: 8.4 V would destroy the MG90S servos.

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
   
   Drive each M2 × 12 clamp screw firmly.
5. **Top plate:** fit the PCA9685 boards on the posts (M2.5 × 6), the ESP32 in its seat (zip tie), the UBEC and buck (double-sided tape). Bring the 18 servo leads up through the 4 cable slots (tibia leads need the 15 cm extensions). Screw the top plate onto the columns (4 × M3 × 8).

## 4. First steps

Hold the robot off the ground and power up. In the Serial Monitor:
- `c` centres everything; the legs should form the neutral stance (femurs level, tibias vertical)
- `t <ch> <deg>` trims one servo, `p` prints the trims; copy them into the sketch's `TRIM[]` table
- `s` stands up, `w` walks forward with a tripod gait, `x` stops

If a joint moves the wrong way, flip its sign in `DIR[]`. The sketch keeps neighbouring coxae from closing more than the 70° the assembly check allows.

Then do the proof tests in each part's `spec.md` §8 and record them in `inspection.md`.

## 5. Safety

- Charge the LiPo only with a balance charger, never unattended, and store it at storage voltage.
- MG90S servos stall at ≈2 kg·cm: keep fingers out of the knees while powered.
- Unplug the LiPo before any wiring change.

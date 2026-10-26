# Hexapod: build guide

Robot 3 of 3. Six identical 3-DOF legs on 18 MG90S servos, two PCA9685 servo drivers, ESP32, 2S LiPo. About 276 × 290 × 160 mm standing, ≈ 0.8 kg (round 3: 812 g estimated, 877 g with solid printed parts).

## 1. Bill of materials

### Printed (PETG)
| Part | Job | Qty per plate | Plates |
|---|---|---|---|
| Bottom body plate (with columns) | `20261026-hexapod-body-bottom` | 1 | 1 |
| Top plate / electronics deck | `20261026-hexapod-body-top` | 1 | 1 |
| Coxa bracket | `20261026-hexapod-coxa` | 6 | 1 |
| Femur | `20261026-hexapod-femur` | 6 | 1 |
| Tibia | `20261026-hexapod-tibia` | 6 | 1 |

Print times and filament: each job's `slice_stats.json` once it is sliced. Round 3 changed the bottom plate, the deck, the coxa bracket and the femur, so those four need slicing again.

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
| 12 | M2 × 12 pan-head machine screws + 12 M2 washers Ø6 | femur and tibia horn clamps (replace the short horn screw). If a bare servo's shaft thread bottoms before 6.5 mm, use M2 × 10 |
| 6 | M2 × 12 pan-head machine screws (M2 × 14 if the shaft thread is 7.5 mm deep or more) + 6 M3 penny washers Ø10 × 1 | coxa horn clamps: washer 1 + 6 mm floor, then the spline (strength round 1) |
| 12 | M2 × 12 pan-head machine screws + 24 M2 washers Ø5 + 12 M2 nuts | coxa servo tabs, through the 6 mm bottom plate: head and washer underneath, washer and nut on the tab |
| 12 | M2 × 10 self-tapping screws | femur servo tabs, 7.5 mm into the 10 mm coxa plate |
| 12 | M2 × 8 self-tapping screws | tibia servo tabs, from behind the femur |
| 18 | M1.7 × 5 screws (or M2 × 6 self-tapping with the horn hole opened to 2.0 mm) | horn anti-rotation screws, one per horn. Measure your horns' holes first |
| 4 | M3 × 8 self-tapping screws | top plate onto the columns |
| 8 | M2.5 × 6 self-tapping screws | PCA9685 boards |
| ≈ 30 | small zip ties (≤ 2.5 mm wide) | lead tie slots: bottom plate, coxa brackets, femurs, deck notches |
| — | velcro strap, zip ties, 6 servo extension leads (15 cm) for the tibia servos, jumper wires | |

Tools: needle file (6 servo tabs, step 4), 1.2 mm drill, small Phillips screwdriver, M2 nut driver or pliers, calipers.

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

Each servo's lead leaves its case at the **shaft end**. Round 3 makes every lead pass its plate (deep review B1):

- **Coxa and tibia servos go in reversed:** spline first, with their tabs on the plate's far face, so the case and lead never pass through the window.
- **Femur servos go in case first,** as before. Their lead passes through a notch at the window's outboard end, and the tab at that end needs its slit opened (step 4).

Fit every horn with its servo centred (90°): femur level, tibia perpendicular to the femur. The walking stance is a software offset from there (§4).

1. **Measure one MG90S** with calipers before printing:
   - body length and width: the CAD uses 22.8 × 12.2;
   - case bottom to tab underside (18.5);
   - tab underside to spline top (14.0);
   - tab-hole spacing (27.8);
   - how deep an M2 screw goes into a bare shaft before it stops (count the turns: 0.4 mm each).
   Tell Claude about any difference over **0.1 mm** in length or width, or over 0.3 mm elsewhere.
2. **Centre:** wire one PCA9685 and the ESP32 on the bench, with the servo rail powered as §2 shows (UBEC at 6 V, never the ESP32's 5 V). Flash `hexapod_test/hexapod_test.ino` (library **Adafruit PWM Servo Driver**) and type `c` in the Serial Monitor (115200) to centre all channels. Plug each servo in briefly to centre it, then leave it unpowered.
3. **Horns into the links:** press each single-arm horn into its pocket on the link's bed-side face, arm along the link. Pilot-drill 1.2 mm through the horn's outer arm hole into the plastic and fit one anti-rotation screw. The centre clamp screw goes in later, when the link goes onto its servo.
4. **Femur servos only (6):** with a needle file, open the slit from the tab hole to the tab end to **2.1 mm**, on the tab at the **shaft end**. That tab's screw sits 1.3 mm further out than its hole, beside the lead notch.
5. **Body (deck off, LiPo not fitted yet):**
   - Lower each coxa servo into its bottom-plate window from above, **spline first**. Its tabs rest on the plate's top face, its case stands inside the body and its lead points outboard.
   - Fix each tab with an M2 × 12 from below: washer, then the screw up through the plate and the tab, then a washer and a nut on the tab inside the body. Tighten to a firm stop.
6. **Legs (×6), on the bench, off the body.** With the leg on the body, a screwdriver on the femur or tibia clamp screw would run into the neighbouring leg, so do these screws now.
   - **Femur servo into the coxa bracket:** tabs on the **gusset face** of the vertical plate, shaft towards where the femur goes.
     1. Feed the lead's plug through the notch at the window's outboard end.
     2. Push the case through the window bottom first, the lead root sliding along the notch.
     3. Fit two M2 × 10, the outboard one through the filed slit.
   - **Tibia servo into the femur, reversed:** from the femur's **back** face (the face with the horn pocket), spline first, so the spline comes out of the front face and the lead points to the knee end. Fit two M2 × 8 from the back.
   - **Tibia** onto the tibia servo, **perpendicular to the femur** (servo centred).
   - **Femur** onto the femur servo, pointing **straight out** (servo centred).
   - For each clamp: hold the link so the shaft can't turn, and drive the screw **snug, about 0.05 N·m**. That is finger-tight on a small screwdriver plus a quarter turn; never "firmly", which pulls the washer through the floor. Femur and tibia: M2 × 12 + Ø6 washer.
   - **Leads:**
     - Zip-tie the tibia lead through the femur's tie slot, beside the horn.
     - Leave a **20 mm free loop** across the femur joint, below the femur axis, clear of the femur servo's horn.
     - Run it with the femur lead to the coxa bracket's tie slot (outer end of the vertical plate) and tie both there.
7. **Hang each leg on its coxa servo**, bracket pointing **radially out** (servo centred). Drive the M2 × 12 (or × 14) with its Ø10 penny washer from below, **snug**.
   - Route the femur and tibia leads **round the outside of the bracket arm**: never across the hub or through the 4 mm gap under the plate, where the tab screw heads are.
   - Leave a **30 mm free loop** and tie the leads at the bottom plate's tie slot beside that leg's window.
8. **Top plate:**
   - Fit the PCA9685 boards on the posts (M2.5 × 6), the ESP32 in its seat (zip tie), the buck on the deck (double-sided tape) and the main switch in the deck's Ø12 hole.
   - Stand the UBEC on its side on the bottom plate, beside the LiPo's left side (y 22–32, double-sided tape), clear of the middle coxa servo.
   - Strap the LiPo on now, and park its balance lead at the rear between the columns.
   - Bring each leg's three leads up the body's side beside that leg and through that leg's notch in the deck edge, to its board's channels. Tie them at the notch. The coxa servo's lead is already inside the body: bring it up beside the same notch.
   - Screw the top plate onto the columns (4 × M3 × 8).
9. **Check the centring:** hold the robot off the ground, power up and type `c`. A link pressed onto its spline, or a clamp screw driven, can turn a shaft. Any link more than half a spline tooth (≈ 9°) off its centre pose goes back on one tooth over before you trim.

**Replacing a servo:**
- **Coxa:** deck off, unplug the servo, take the leg off (one clamp screw from below), remove the two tab nuts and screws, lift the servo out upwards.
- **Femur:** take the leg off its spline and the femur off its servo, remove the two tab screws on the gusset face, and pull the case out through the window, its lead through the notch.
- **Tibia:** take the tibia off, remove the two tab screws behind the femur, and take the servo out backwards.

The self-tapping threads in the columns take a few cycles. If the deck comes off often, M3 heat-set inserts are the upgrade.

## 4. First steps

Hold the robot off the ground and power up. In the Serial Monitor:
- `c` centres every servo: femurs level, tibias perpendicular to them (the pose the horns were fitted in)
- `s` stands in the **walking stance: femur −4.7°, tibia −14.0°**. The tibias are tucked 18.7° in at the same body height, which keeps the femur and knee servos at about 40 % of stall instead of about 70 % at a 30 mm stride (`assembly_plan.md`, "Stance"). If your sketch still has `NEUTRAL_FEMUR`/`NEUTRAL_TIBIA` at 0, set them to −4.7 and −14.0 with the other constants in `assembly_plan.md`, "Firmware".
- `t <ch> <deg>` trims one servo, `p` prints the trims; copy them into the sketch's `TRIM[]` table
- `w` walks forward (tripod, 30 mm stride), `x` stops

If a joint moves the wrong way, flip its sign in `DIR[]`. Neighbouring coxae must not close by more than 60° in total (round-3 assembly check; `MAX_COXA` 30 is exactly that).

**Each leg hangs on its coxa servo's output shaft alone** (deep review SYS-6): never lift or carry the robot by a leg. Before the full build, do the leg proof test in the assembly `spec.md` §8 on one assembled leg. Then do the proof tests in each part's `spec.md` §8 and record them in `inspection.md`.

## 5. Safety

- Charge the LiPo only with a balance charger, never unattended, and store it at storage voltage.
- MG90S servos stall at ≈2 kg·cm: keep fingers out of the knees while powered.
- Unplug the LiPo before any wiring change.
- Never lift the robot by a leg: pick it up by the top plate.

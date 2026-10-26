# Hexapod: build guide

Robot 3 of 3. Six identical 3-DOF legs on 18 MG90S servos, two PCA9685 servo drivers, ESP32, 2S LiPo. About 276 × 290 × 160 mm standing, ≈ 0.9 kg (round 4: about 906 g, strength round 3's itemised estimate with the solid coxa brackets and the bigger bottom plate).

## 1. Bill of materials

### Printed (PETG)
| Part | Job | Qty per plate | Plates |
|---|---|---|---|
| Bottom body plate (with columns) | `20261026-hexapod-body-bottom` | 1 | 1 |
| Top plate / electronics deck | `20261026-hexapod-body-top` | 1 | 1 |
| Coxa bracket (solid, 100 % infill) | `20261026-hexapod-coxa` | 2 | 3 |
| Femur | `20261026-hexapod-femur` | 6 | 1 |
| Tibia | `20261026-hexapod-tibia` | 6 | 1 |

Print times and filament: each job's `slice_stats.json` once it is sliced. Round 3 changed the bottom plate, the deck, the coxa bracket and the femur, so those four need slicing again. Round 4 changed the bottom plate and the coxa bracket once more.

**Screw-strip check (26 Oct 2026).** The coxa bracket and the femur leave only 1.35–1.45 mm of plastic between each servo window and its screw holes, under the project's 1.8 mm rule. You chose to keep the design and check it on the first prints: print the **first coxa plate and the femur plate**, then fit one femur servo in a bracket and one tibia servo in a femur (step 6), drive both screws snug and look at the strips beside the screw holes. If one has turned white or cracked, stop and tell Claude **before printing the other two coxa plates**: the screw holes move out.

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
| 1 | XT30 **male** pigtail, 18 AWG leads (it mates with the LiPo's lead, which carries the female plug; check your pack) | from the LiPo's plug to the fuse and switch |
| 1 | LiPo voltage alarm (buzzer), 2S | plugs into the balance lead: beeps when a cell runs low. It is the only cut-off for the UBEC, the buck and the ESP32 |
| 1 + 1 + 1 | 100 kΩ and 33 kΩ resistors (1 %), 100 nF ceramic capacitor | battery voltage divider to GPIO35: the sketch stops walking on a flat pack |
| 1 | SS14 or 1N5817 Schottky diode | buck OUT+ to the ESP32's 5V pin: USB can't feed back into the LiPo side |
| 1 | 1000 µF 10 V capacitor, in addition to the one below | bulk capacitance on the servo rail: one across each PCA9685's V+ terminals (Adafruit: n × 100 µF, here 1800 µF) |
| 6 | Servo extension leads, 15 cm (20 cm if in doubt) | for the femur servos: their leads fall up to 31 mm short even by the deck-edge route. With the 6 for the tibias, 12 in all |
| 1 | 2S LiPo balance charger | the only way to charge the pack |
| 1 | LiPo charging bag | charge and store the pack in it |
| 1 | 1000 µF 10 V capacitor | across the servo rail |
| 12 | M2 × 12 pan-head machine screws + 12 M2 washers Ø6 | femur and tibia horn clamps (replace the short horn screw). If a bare servo's shaft thread bottoms before 6.5 mm, use M2 × 10 |
| 6 | M2 × 12 pan-head machine screws (M2 × 14 if the shaft thread is 7.5 mm deep or more) + 6 M3 penny washers Ø10 × 1 | coxa horn clamps: washer 1 + 6 mm floor, then the spline (strength round 1) |
| 12 | M2 × 14 pan-head machine screws + 24 M2 washers Ø5 + 12 M2 Nyloc nuts (nylon insert, DIN 985) | coxa servo tabs, through the 6 mm bottom plate: head and washer underneath, washer and Nyloc on the tab. × 14 so the thread comes through the Nyloc's nylon ring |
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
   - Fix each tab with an M2 × 14 from below: washer, then the screw up through the plate and the tab, then a washer and a Nyloc nut on the tab inside the body. The thread must come through the Nyloc's nylon ring.
   - Tighten each one **by feel, not to a torque setting**: run the nut down until both washers just clamp, then stop (about 0.045 N·m above the Nyloc's running torque). Keep the threads dry, no oil. Never tighten to a firm stop: the washer under the head bears on only 14 mm² of the plate (strength round 4). The Nyloc holds without preload.
6. **Legs (×6), on the bench, off the body.** With the leg on the body, a screwdriver on the femur or tibia clamp screw would run into the neighbouring leg, so do these screws now.
   - **Femur servo into the coxa bracket:** tabs on the **gusset face** of the vertical plate, shaft towards where the femur goes.
     1. Feed the lead's plug through the notch at the window's outboard end.
     2. Push the case through the window bottom first, the lead root sliding along the notch.
     3. Fit two M2 × 10, the outboard one through the filed slit. On the first bracket, do the screw-strip check (§1).
   - **Tibia servo into the femur, reversed:** from the femur's **back** face (the face with the horn pocket), spline first, so the spline comes out of the front face and the lead points to the knee end. Fit two M2 × 8 from the back. On the first femur, do the screw-strip check (§1).
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

Flash `hexapod_test/hexapod_test.ino` (Arduino IDE, board "ESP32 Dev Module" on the arduino-esp32 3.x core; library **Adafruit PWM Servo Driver**, which also installs Adafruit BusIO: accept the prompt). Hold the robot off the ground and power up. At power-up the legs start one at a time, 150 ms apart, so the 18 servos don't all surge at once. In the Serial Monitor:

| Command | Does |
|---|---|
| `c` | centre all 18 servos (90°): femurs level, tibias square to them (vertical). Fit and check the horns in this pose |
| `t <n> <deg>` | trim servo n by <deg>, ±20° in total. n = leg × 3 + joint: legs 0–5 = LF, LM, LR, RF, RM, RR; joints 0–2 = coxa, femur, tibia |
| `p` | print the trims: copy them into the sketch's `TRIM[]` table |
| `s` | stand in the walking stance: femur −4.7°, tibia −14.0° |
| `w` | walk forward |
| `x` | stop and stand, within one 25 ms gait frame |
| `o` | measure the PCA9685 clocks (below) |

- If a joint moves the wrong way, flip its sign in `DIR[]`. The sketch keeps neighbouring coxae from closing more than the 60° the round-3 assembly check allows (`MAX_COXA` 30), and the femurs within −70…+80° (the round-4 plate's edge meets a femur raised further) and the tibias within −80…+90°.
- **Stance:** the walking stance tucks the tibias 18.7° in at the same body height. At the round-4 mass (906 g) that keeps the femur and knee servos at about 44 % of stall instead of about 79 % at a 30 mm stride (`assembly_plan.md`, "Stance"). The constants sit in the sketch's neutral-stance block.
- **Clock calibration, once per board:** a PCA9685's oscillator is 25 MHz typical but anywhere from about 23 to 27 MHz, and every servo pulse is off by the same ratio. Jumper the left board's channel-15 signal pin to GPIO34 and type `o`; copy the printed value into `OSC_L`. Move the jumper to the right board, type `o`, copy into `OSC_R`, re-flash and remove the jumper.
- **Gait:** a tripod gait with inverse kinematics. Planted feet move straight back along the ground, so none slides, and each swing lands exactly where the next stroke starts: 30 mm stride, 20 mm lift, 0.5 s per cycle. Each tripod swings for 40 % of the cycle, so all six feet share the load at each hand-over. The neutral stance (femur and tibia angles) and the leg geometry sit in one block at the top of the sketch.
- **Battery:** the sketch reads the LiPo through the divider. When it reads below 6.6 V twice in a row (3.3 V per cell under load), the hexapod stops walking and won't walk again until restarted: switch off and charge. Expect about 11–16 minutes of walking per charge at the round-2 mass, the shorter figure on carpet. The round-4 robot is about 35 % heavier (≈ 0.91 kg), so expect less.
- Walking also needs both boards to answer. With one board on the bench (section 3, step 1) the sketch says which is missing, and `c`, `s` and `t` still work.
- If a servo twitches each time the Serial Monitor opens (the ESP32 restarts while the boards keep their power), hold the boards' OE pin high during start-up.

**Each leg hangs on its coxa servo's output shaft alone** (deep review SYS-6): never lift or carry the robot by a leg. Before the full build, do the leg proof test in the assembly `spec.md` §8 on one assembled leg. Then do the proof tests in each part's `spec.md` §8 and record them in `inspection.md`.

## 5. Safety

- Charge the LiPo only with a balance charger, inside its LiPo bag, never unattended. Never charge or use a swollen pack. Store it at storage voltage (3.8–3.85 V per cell) and unplug it after use.
- MG90S servos stall at ≈2 kg·cm: keep fingers out of the knees while powered.
- Unplug the LiPo before any wiring change.
- Never lift the robot by a leg: pick it up by the top plate.

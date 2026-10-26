# Tracked rover: build guide

Robot 2 of 3. Skid-steer tank with printed tracks on steel pins, 2 × N20 gear motors, TB6612FNG driver, ESP32, 2 × 18650 cells, HC-SR04 distance sensor. About 160 × 142 × 60 mm, 0.6 kg, ~170 mm/s. **Drop rating: 5 cm onto a hard floor.** It is not built to survive a fall off a desk.

## 1. Bill of materials

### Printed (PETG)
| Part | Job | Qty per plate | Plates |
|---|---|---|---|
| Chassis (tub) | `20261026-rover-chassis` | 1 | 1 |
| Lid / electronics deck | `20261026-rover-lid` | 1 | 1 |
| Drive sprocket | `20261026-rover-sprocket` | 2 | 1 |
| Idler | `20261026-rover-idler` | 2 | 1 |
| Road wheel | `20261026-rover-wheel` | 4 | 1 |
| Track link | `20261026-rover-track-link` | 34 | **2** (68 links) |

Print times and filament: see `README.md` next to this file.

### Bought
| Qty | Item | Notes |
|---|---|---|
| 2 | N20 gear motor, 6 V, 100 rpm, metal gearbox (GA12-N20), 3 mm D-shaft 10 mm long | the gearbox length varies with the ratio; measure yours |
| 1 | TB6612FNG motor-driver carrier (Pololu-size, with headers) | |
| 1 | ESP32 DevKit (38-pin DevKitC or 30-pin DOIT), headers soldered pins down | |
| 1 | 170-point mini breadboard, adhesive back | carries the TB6612 |
| 2 | 18650 Li-ion cells, **protected** (or a 2S BMS) | charge them outside the rover |
| 1 | 2 × 18650 series holder with leads (77 × 41 × 21 mm) | |
| 1 | MP1584 (or similar) buck module, set to **5.0 V before connecting** | feeds the ESP32 and the HC-SR04 |
| 1 | MTS-102 mini toggle switch (6 mm threaded bushing, Ø6.4 hole) | main power, in the rear wall |
| 1 | HC-SR04 ultrasonic sensor | 1 kΩ + 2 kΩ resistors for its ECHO line (5 V → 3.3 V) |
| 1 | 100 µF electrolytic capacitor | across the TB6612's VM and GND |
| 4 | M3 × 45 bolts (pan or socket head) | road-wheel axles, head inside the tub |
| 2 | M3 × 35 bolts | idler axles, head inside the tub |
| 6 + 6 + 12 | M3 nuts, M3 nyloc nuts, M3 washers | a nut in each wall trap, a washer each side of every wheel/idler, a nyloc outside |
| 4 | M3 × 10 self-tapping screws | lid |
| 2 | M2 × 4 set screws (or M2 × 6 self-tappers) | sprocket grub screws |
| 68 (+2 spare) | Ø2 × 24 mm steel dowel pins (ISO 2338 / 8734), or 2 mm silver-steel rod cut to 23.5 mm and deburred | track pins: gripped by each link's outer knuckles, running free in the next link's centre knuckle |
| — | 2 zip ties (motors), 2 small zip ties (ESP32), 1 velcro strap (20 mm), jumper wires, 22 AWG wire | |

## 2. Wiring

```
18650 × 2 (7.4 V) ─► switch ─┬─► TB6612 VM  (100 µF across VM–GND)
                             └─► MP1584 IN ─► 5.0 V ─┬─► ESP32 5V/VIN
                                                     └─► HC-SR04 VCC
GND: battery, TB6612 GND, buck, ESP32, HC-SR04 all common.
ESP32 3V3 ─► TB6612 VCC (logic)

ESP32 GPIO25 ─► PWMA   GPIO26 ─► AIN1   GPIO27 ─► AIN2   (left motor on A01/A02)
ESP32 GPIO14 ─► PWMB   GPIO33 ─► BIN1   GPIO32 ─► BIN2   (right motor on B01/B02)
ESP32 GPIO13 ─► STBY
ESP32 GPIO18 ─► HC-SR04 TRIG
HC-SR04 ECHO ─► 1 kΩ ─┬─► ESP32 GPIO19
                      └─► 2 kΩ ─► GND
```

None of those GPIOs is a boot-strapping pin. Never connect the 7.4 V pack to the ESP32's 3V3 pin. Set the buck to 5.0 V with a multimeter **before** connecting the ESP32.

## 3. Assembly

1. **Track chains.** Chain 34 links per side: a link's centre knuckle goes between the next link's two outer knuckles, grousers all facing out. Press a Ø2 steel pin through outer knuckle, centre knuckle and outer knuckle with a small vice or parallel pliers until it sits flush on both sides. The outer knuckles grip it and the centre knuckle runs free, so nothing needs gluing. Check every hinge flexes freely to about 40° both ways before moving on.
2. **Chassis hardware.** Press an M3 nut into each of the 4 road-wheel nut traps and the 2 idler nut slots on the outside of the walls. Push the bolts in from the inside, head inside: M3 × 45 for the road wheels, M3 × 35 for the idlers. Tighten the road-wheel bolts. Leave the idler bolts loose for now.
3. **Motors.** Solder leads to the motor terminals first. Drop each N20 into its cradle from above: gearbox between the cheeks, shaft pointing into the wall's journal, gearbox face against the journal boss, the can's end cap against the rear stop. Pull a zip tie through the tunnel under the cradle and round the can, and tighten it.
4. **Wheels.** On each bolt: washer, road wheel (or idler, hub towards the wall), washer, nyloc nut. Tighten the nyloc until the wheel has about 0.3 mm end play and still spins freely.
5. **Sprockets.** From outside, slide each sprocket's Ø10 hub into the wall's journal and press its D-bore onto the N20 shaft, lining the flat up first, until the hub stops 0.5 mm short of the gearbox face. The hub should turn freely in the journal. Tighten the M2 set screw onto the shaft's flat through the gap between the wall and the track.
6. **Tracks.** Wrap each 34-link loop round its sprocket, road wheels and idler, then join it with the last pin. Push the idler forward until the top run sags about 3–5 mm between sprocket and idler, then tighten the idler bolt's nut (inside) to lock the slot.
7. **Power.** Strap the battery holder to the floor with the velcro through the floor slots. Fit the toggle switch through the rear wall (nut outside). Fit the HC-SR04 behind the front wall with its transducers through the holes; a dab of hot glue holds the board.
8. **Lid.** Stick the mini breadboard on the front of the lid and push the TB6612 into it. Stick the buck module under the lid. Seat the ESP32 pins-down on its ledges and fix it with two small zip ties through the slots at its ends, across the pin-free ends of the board (never across the pin rows). Bring the motor, battery and sensor leads up through the cable hole and wire per section 2. Screw the lid on (4 × M3 × 10).

## 4. First drive

Flash `rover_test/rover_test.ino` (Arduino IDE, board "ESP32 Dev Module"). Prop the rover up so the tracks are off the ground, switch on, open the Serial Monitor at 115200 and type `f` (forward). If a track runs backwards, swap that motor's two wires at the TB6612. Commands: `f` / `b` / `l` / `r` / `s` (stop), `+` / `-` (speed), `a` (autonomous: drive forward and turn away from obstacles closer than 15 cm). The sketch caps the motor PWM at 80 %, because the 7.4 V pack is above the motors' 6 V rating.

Then do the proof tests in each part's `spec.md` §8 and record them in `inspection.md`: track chain under 4.5 kg, wheel bolt under 3 kg, motor stalls, and drops from 5 cm.

## 5. Safety

- Charge the 18650 cells outside the rover with a proper Li-ion charger; never short the holder leads.
- Switch off before working on the wiring.
- Don't let a motor stall for more than a few seconds.

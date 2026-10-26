# Tracked rover: build guide

Robot 2 of 3. Skid-steer tank with printed tracks, 2 × N20 gear motors, TB6612FNG driver, ESP32, 2 × 18650 cells, HC-SR04 distance sensor. About 160 × 142 × 60 mm, 0.5 kg, ~170 mm/s.

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
| 1 | KCD11 mini rocker switch (15 × 10 mm cut-out) | main power |
| 1 | HC-SR04 ultrasonic sensor | 1 kΩ + 2 kΩ resistors for its ECHO line (5 V → 3.3 V) |
| 1 | 100 µF electrolytic capacitor | across the TB6612's VM and GND |
| 6 | M3 × 40 bolts, 6 M3 nuts, 6 M3 nyloc nuts, 12 M3 washers | wheel and idler axles |
| 4 | M1.6 × 4 screws | N20 gearbox face to the wall (2 per motor) |
| 4 | M3 × 10 self-tapping screws | lid |
| 2 | M2 × 4 set screws (or M2 × 6 self-tappers) | sprocket grub screws |
| ~1.7 m | 1.75 mm filament | 68 track pins, 25 mm each |
| — | 2 zip ties, 1 velcro strap (20 mm), jumper wires, 22 AWG wire | |

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

1. **Pins.** Cut 68 pieces of 1.75 mm filament, 25 mm long. Chain 34 links per side: a link's centre knuckle goes between the next link's two outer knuckles, grousers all facing out. Push a pin through, then flatten both ends slightly with a warm soldering iron (or a drop of CA) so it can't walk out. Check the chain flexes freely.
2. **Chassis hardware.** Press an M3 nut into each of the 4 road-wheel nut traps and the 2 idler nut slots on the outside of the walls. Push the M3 × 40 bolts in from the inside, head inside. Tighten the road-wheel bolts; leave the idler bolts loose for now.
3. **Motors.** Put each N20 through from the inside: shaft through the wall hole, gearbox face flat on the wall. Fix it with 2 × M1.6 screws through the wall into the gearbox face. Zip-tie the can to its cradle through the groove. Solder leads to the motor terminals first.
4. **Wheels.** On each bolt: washer, road wheel (or idler, hub towards the wall), washer, nyloc nut. Tighten the nyloc until the wheel has ~0.3 mm end play and still spins freely.
5. **Sprockets.** Press a sprocket onto each N20 shaft, hub towards the wall, leaving 0.5 mm to the wall. Tighten the M2 grub screw on the shaft's flat.
6. **Tracks.** Wrap each 34-link loop round its sprocket, road wheels and idler, then join it with the last pin. Push the idler forward until the top run sags about 3–5 mm between sprocket and idler, then tighten the idler bolt's nut (inside) to lock the slot.
7. **Power.** Strap the battery holder to the floor with the velcro through the floor slots. Fit the rocker switch in the rear wall and the HC-SR04 behind the front wall (transducers through the holes; a dab of hot glue holds the board).
8. **Lid.** Stick the mini breadboard on the front of the lid and push the TB6612 into it. Stick the buck module under the lid. Seat the ESP32 pins-down on its ledges and zip-tie it through the two slots. Bring the motor, battery and sensor leads up through the cable hole and wire per section 2. Screw the lid on (4 × M3 × 10).

## 4. First drive

Flash `rover_test/rover_test.ino` (Arduino IDE, board "ESP32 Dev Module"). Prop the rover up so the tracks are off the ground, switch on, open the Serial Monitor at 115200 and type `f` (forward). If a track runs backwards, swap that motor's two wires at the TB6612. Commands: `f` / `b` / `l` / `r` / `s` (stop), `+` / `-` (speed), `a` (autonomous: drive forward and turn away from obstacles closer than 15 cm). The sketch caps the motor PWM at 80 %, because the 7.4 V pack is above the motors' 6 V rating.

Then do the proof tests in each part's `spec.md` §8 (track chain under 3 kg, wheel bolt under 2 kg, 30 cm drop, sprocket stall) and record them in `inspection.md`.

## 5. Safety

- Charge the 18650 cells outside the rover with a proper Li-ion charger; never short the holder leads.
- Switch off before working on the wiring.
- Don't let a motor stall for more than a few seconds.

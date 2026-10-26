# Tracked rover: build guide

Robot 2 of 3. Skid-steer tank with printed tracks on steel pins, 2 × N20 gear motors, TB6612FNG driver, ESP32, 2 × 18650 cells, HC-SR04 distance sensor. About 160 × 155 × 73 mm, 0.65 kg, about 145 mm/s on a straight run. **Drop rating: 5 cm onto a hard floor.** It is not built to survive a fall off a desk.

## 1. Bill of materials

### Printed (PETG)
| Part | Job | Qty per plate | Plates |
|---|---|---|---|
| Chassis (tub) | `20261026-rover-chassis` | 1 | 1 |
| Lid / electronics deck | `20261026-rover-lid` | 1 | 1 |
| Drive sprocket | `20261026-rover-sprocket` | 2 | 1 |
| Idler | `20261026-rover-idler` | 2 | 1 |
| Road wheel | `20261026-rover-wheel` | 2 | **2** |
| Track link | `20261026-rover-track-link` | 35 | **2** (68 links + 2 spare) |

Sliced on 26 Oct 2026 (each job's `slice_stats.json`, stock Prusa PETG profiles, 0.2 mm layers): lid 2.4 h / 34 g; sprockets 1.0 h / 8 g; idlers 1.0 h / 10 g (round 5, shorter hub); road wheels 2.3 h / 25 g per plate (2 plates: four on one plate would take 3.9 h, over the 3 h limit); track links 6.2 h / 45 g per plate (2 plates; build the 5-link test chain from plate 1 before printing plate 2). Chassis (round 6) 11.5 h / 142 g, one plate. Every plate goes on the smooth PEI sheet with a thin layer of glue stick (each job's `preflight.md`).

### Bought
| Qty | Item | Notes |
|---|---|---|
| 2 | N20 (GA12) gear motor: 6 V, 100 rpm (≈150:1), **LP or MP winding** (stall ≤ 0.7 A at 6 V), 9 mm metal gearbox, 3 mm D-shaft **10 mm long, measured from the flat gearbox face (at least 9.6 mm)**. For example, Pololu 150:1 Micro Metal Gearmotor LP or MP 6 V: its output shaft adds 10 mm to the body length | An 11 mm gearbox also fits. **Don't use a 9 mm shaft**: its end reaches only 1.5 mm into the sprocket's centre hole, and a 5 cm drop can then shear the ring between that hole and a screw slot. Measure from the flat metal face of the gearbox, not from the round bushing. Don't use an HP winding: it overloads the driver and the printed parts. Measure each motor's stall torque before the proof tests (chassis `spec.md` §8) |
| 1 | Pololu #1996 universal aluminium mounting hub for a 3 mm shaft, M3 holes (2-pack, with set screws) | One hub per sprocket. Its M3 set screw goes on the shaft's flat |
| 8 | M3 × 12 socket or button head screws | Sprocket disc to hub, 4 per side |
| 4 | M3 × 50 socket head cap screws, class 12.9, **fully threaded** | Road-wheel axles, head inside the tub. An ordinary ISO 4762 screw this long has only 18 mm of thread and never reaches the wall nut, so buy ones sold as fully threaded |
| 2 | M3 × 40 socket head cap screws, class 12.9, **fully threaded** | Idler axles, head inside the tub |
| 2 | M3 × 20 set screws, flat point (DIN 913) | Idler jack screws. Each cuts its own thread in the chassis |
| 6 | M3 nuts (DIN 934) | 4 in the road-wheel nut traps; 2 as the idler wall nuts, outside the wall on the nut plates |
| 6 | M3 nyloc nuts (DIN 985) | Outside each wheel and idler |
| 26 | M3 washers (ISO 7089, Ø7 × 0.5) | 12 for the running faces (one each side of every wheel and idler), 4 under the road-wheel bolt heads, 8 under the hub screws, 2 as thrust washers on the motor shafts |
| 4 | M3 penny washers (DIN 9021, Ø9 × 0.8) | 2 under the idler bolt heads, on the head plates; 2 under the idler wall nuts, on the nut plates |
| 4 | Idler clamp plates, **2 mm steel**, made (see below): **all four the same**, 20.6 × 10 mm with a 3.4 × 12 mm slot from 6 to 18 mm along | Cut from 14-gauge steel (1.9 mm) flat bar or sheet, sold as 14 ga at hardware stores like Princess Auto and Home Depot. Metric 2 mm flat bar or strip (10 × 2) also works. Don't use 1/8 in (3.2 mm) stock: a head plate would stand 1.2 mm proud of its recess and put the jack screw on the washer. Each idler bolt is clamped between two plates: a head plate inside the tub, in a recess in the idler block's face, and a nut plate outside, flat on the wall's outer face, standing on a printed lip between two printed end stops |
| 4 + 4 | M3 heat-set inserts (M3 × 5.7, for a Ø4.0 hole) + M3 × 8 screws | Lid columns. The lid comes off for every charge |
| 68 (+2 spare) | Ø2 × 24 mm steel dowel pins (ISO 2338 / 8734), or 2 mm silver-steel rod cut to 23.5 mm and deburred | Track pins: gripped by each link's outer knuckles, running free in the next link's centre knuckle |
| 1 | TB6612FNG motor-driver carrier (Pololu-size, with headers) | |
| 1 | ESP32 DevKit, headers soldered pins down: 38-pin DevKitC (54.4 × 27.9 mm) or 30-pin DOIT DevKit V1 (51.8 × 28.2 mm) | Boards shorter than about 49.5 mm don't reach the seat's ledge |
| 1 | 170-point mini breadboard, adhesive back | Carries the TB6612 |
| 2 | 18650 Li-ion cells: **protected** cells (about 70 mm long), or unprotected cells with a 2S BMS | Charge them outside the rover |
| 1 | 2 × 18650 series holder with leads, made for the cells you chose. Protected cells need a long holder; up to 80 × 41 × 21 mm fits | |
| (1) | 2S BMS | Only with unprotected cells |
| 1 | Two-bay Li-ion charger | |
| 1 | MP1584 (or similar) buck module, 22 × 17 × 4 mm, set to **5.0 V before connecting** | Feeds the ESP32 and the HC-SR04. It goes under the lid, on foam tape |
| 1 | MTS-102 mini toggle switch (M6 × 0.75 bushing, at least 6 mm of thread) | Main power, on the lid, lever up |
| 1 | HC-SR04 ultrasonic sensor | 1 kΩ + 2 kΩ resistors for its ECHO line (5 V → 3.3 V) |
| 1 | 100 µF electrolytic capacitor, 16 V or more | Across the TB6612's VM and GND |
| — | Zip ties: 2 at most 3.6 mm wide (motors); 2 at most 2.5 mm wide and **at least 150 mm long** (ESP32: each loop is about 98 mm, more than a 100 mm tie closes); 1 for the lid's tie bar. 1 velcro strap (20 mm), jumper wires, 22 AWG wire, heat-shrink, double-sided foam tape, hot glue, medium threadlocker, a few drops of light machine oil (sewing-machine or 3-in-1 oil) for the idler plates | |

### Making the idler plates
All four plates are the same: 20.6 × 10 × 2 mm, with a 3.4 mm wide, 12 mm long slot on the centre line from 6 mm to 18 mm along. That leaves 6 mm of steel at one end and 2.6 mm at the other; the 6 mm end always goes to the rear, towards the jack screw.
1. **Mark out** four plates on 10 mm wide bar (10 × 2 flat bar, or a 10 mm strip of 14-gauge sheet), each 20.6 mm long. Don't cut them off yet: the bar is easier to hold in the vice while you drill.
2. **Make each slot.** It is a closed slot, so a hacksaw can't reach it. Drill a row of holes along it, then file out the steel between them:
   - On the centre line, centre-punch four points 7.7, 10.6, 13.4 and 16.3 mm from the plate's end. The outer two are the slot's end centres, 8.6 mm apart.
   - Drill all four points 2.5 mm, leaving thin webs between the holes. Then open the two end holes to 3.4 mm (3.5 mm is fine): the 2.5 mm holes keep the bigger drill on its mark.
   - File away the thin webs between the holes with a flat needle file. Then file the sides straight until the slot is 3.4 mm wide along its whole length and an M3 bolt slides from end to end.
3. **Cut** the plates off the bar at 20.6 mm, then **deburr** every edge and both faces with a file, so each plate lies flat on the printed faces.
4. **Mark** the 6 mm end of each plate with a felt pen. It goes to the rear.
5. **Check** each plate on the printed chassis:
   - a head plate drops into the recess in the inside face of an idler block, flush with the face;
   - a nut plate stands on the lip on the outside of the wall, flat against the wall between the two end stops;
   - if a plate is tight between the recess ends or the stops, file its ends a little;
   - with both plates in place, an M3 bolt slides the full length of the slot in the wall.

### Tools
- 1.5 mm hex key, ball end, long arm: jack screws and hub set screws
- 2.5 mm hex key (an L-key, with an 18 mm short arm)
- 2.5 mm **ball-end** hex key (L-key, 18 mm short arm): the idler snug in step 3. A plain long arm (56 mm) doesn't fit between the idler blocks
- 5.5 mm open-end spanner, or flat-nose pliers: holds each idler wall nut while you snug its bolt
- Soldering iron, which also sets the inserts
- Small vice or parallel pliers: track pins
- Multimeter: setting the buck
- Kitchen scale and a 50 mm arm: motor stall torque, and feeling the idler bolts' snug
- Centre punch, drill with 3.4 mm (or 3.5 mm) and 2.5 mm bits, hacksaw, flat and needle files: the idler plates

### Bought: battery monitor and power protection
| Qty | Item | Notes |
|---|---|---|
| 1 + 1 + 1 | 100 kΩ and 33 kΩ resistors (1 %), 100 nF ceramic capacitor | battery voltage divider to GPIO34 (section 2): the sketch keeps the motors at 6 V or less and stops on a flat pack |
| 1 | SS14 or 1N5817 Schottky diode | from the buck's OUT+ to the ESP32's 5V pin (section 2). With it, set the buck to **5.3 V**, not 5.0 V |
| 2 | 100 nF ceramic capacitor | one soldered across each N20's terminals |

## 2. Wiring

```
18650 × 2 (7.4 V) ─► switch ─┬─► TB6612 VM  (100 µF, rated 16 V or more, across VM–GND)
                             ├─► MP1584 IN ─► 5.3 V ─► SS14 ─► ESP32 5V/VIN (≈ 5.0 V) ─► HC-SR04 VCC
                             └─► 100 kΩ ─┬─► ESP32 GPIO34 (battery voltage)
                                         └─► 33 kΩ ─► GND   (100 nF across the 33 kΩ)
GND: battery, TB6612 GND, buck, ESP32, HC-SR04, divider all common.
ESP32 3V3 ─► TB6612 VCC (logic)

ESP32 GPIO25 ─► PWMA   GPIO26 ─► AIN1   GPIO27 ─► AIN2   (left motor on A01/A02)
ESP32 GPIO14 ─► PWMB   GPIO33 ─► BIN1   GPIO32 ─► BIN2   (right motor on B01/B02)
ESP32 GPIO13 ─► STBY
ESP32 GPIO18 ─► HC-SR04 TRIG
HC-SR04 ECHO ─► 1 kΩ ─┬─► ESP32 GPIO19
                      └─► 2 kΩ ─► GND
N20 motors: a 100 nF ceramic capacitor soldered across each motor's terminals
```

- None of those GPIOs is a boot-strapping pin. GPIO34 is input-only and on ADC1, which suits the battery divider. Never connect the 7.4 V pack to the ESP32's 3V3 pin.
- Set the buck to **5.3 V** with a multimeter **before** connecting anything to its output. The Schottky drops about 0.3 V, so about 5.0 V reaches the ESP32 and the HC-SR04.
- The diode keeps USB and the battery apart. Without it, the PC's USB port feeds back through the buck into the motor supply while the switch is off, and `f` runs the motors from the PC. (Instead of the diode, a data-only USB adapter that blocks the 5 V line also works, used whenever the pack is in.)
- The divider turns 8.4 V into 2.08 V and draws about 60 µA, only while the switch is on.
- The 100 nF capacitors across the N20s quieten the noisiest parts on the board, right next to the HC-SR04 and the ESP32.
- Check the pack's polarity with a meter before the first switch-on: a cell put in backwards reverses the pack onto the TB6612 and the buck.
- The breadboard's spring contacts can lose contact on a vibrating chassis and reset the ESP32. If that happens, solder the TB6612 carrier to a strip of perfboard, or plug it into female headers.
- The HC-SR04 is a 5 V part triggered at 3.3 V. Most work; if `d` reads "nothing in range" facing a wall, fit an HC-SR04P or RCWL-1601 instead (3.3 V versions: power them from 3V3, no ECHO divider).

## 3. Assembly

**Before you start**
- **Check the bought parts against section 1:**
  - the axle bolts are threaded right up to the head;
  - each motor's gearbox is 9 or 11 mm long and its shaft 10 mm (at least 9.6 mm) from the flat gearbox face;
  - the hub's four holes sit 5.5–6.85 mm from its centre, which is the range the sprocket's slots cover.
- **Test-fit a motor in the chassis pocket.** The gearbox should slide in with light friction. If it binds, scrape the pocket's 45° faces lightly.
- **Test a short chain first.** Make a 5-link test chain from the first plate of links and do the track-link proof tests (its `spec.md` §8) before printing the second plate.

1. **Track chains.**
   - Chain 34 links per side: a link's centre knuckle goes between the next link's two outer knuckles, grousers all facing out.
   - Press a Ø2 steel pin through outer knuckle, centre knuckle and outer knuckle with a small vice or parallel pliers, until it sits flush on both sides. The outer knuckles grip it and the centre knuckle runs free, so nothing needs gluing.
   - Check every hinge flexes freely to about 40° both ways.
   - Leave each loop open (one pin out) for step 8.
2. **Inserts.** Set an M3 heat-set insert in each of the four lid columns with the soldering iron (about 230 °C for PETG). Press it in square and flush with the column top, and let it cool.
3. **Axle bolts.** Fit these first: later, a road-wheel bolt needs the battery out and an idler bolt needs the sensor out.
   - The part inside the tub is each bolt's **head**; its nut is outside.
   - **Road wheels.** Press an M3 nut into each of the 4 road-wheel nut traps in the outer face of the walls, flats up. From inside the tub, push an M3 × 50 with an M3 washer under its head through the boss and the wall, screw it into its nut until the head sits on its washer, and tighten it (2.5 mm key).
   - **Idler plates.** Fit the four plates (§1), each with its marked 6 mm end towards the rear (towards the jack-screw buttress). A dab of grease holds a plate in place while you fit the bolt.
     - Inside the tub: press a head plate into the recess in each idler block's face, flush with the face.
     - Outside: stand a nut plate on the printed lip on each wall's outer face, between the two end stops, flat against the wall.
     - Put a drop of light machine oil on each plate's exposed face round its slot, where its Ø9 washer will slide. **The oil is required:** with dry plates the jack screw needs about twice the push to slide the bolt, and it can strip its own thread in the chassis.
   - **Idler bolts.** From inside the tub, push an M3 × 40 with a Ø9 penny washer under its head through the head plate, the wall and the nut plate. Outside, put a Ø9 penny washer and then an M3 nut on its end, and spin the nut down onto the washer by hand.
   - **Snug each idler bolt at the rear end of its slot,** to about 0.04 N·m and no more:
     - Push the bolt to the rear end of its slot.
     - Outside, hold the nut with the 5.5 mm spanner (or flat-nose pliers). Nothing else is in the way yet.
     - Inside, put the **ball end** of the 2.5 mm ball-end key into the bolt head, the long arm tilted 18–25° up so it passes over the opposite idler block (there is only about 50 mm between the blocks), and twist the key by its **short** arm with two fingertips until the head stops turning. Stop there.
     - How light that is: 0.04 N·m is about 230 g pushed at the tip of the key's 18 mm short arm. Before you start, press the short arm's tip onto the kitchen scale until it reads 230 g, to feel it. Don't lever on the long arm, and don't use a screwdriver-style hex driver: a normal "snug" (0.3 N·m) clamps the plates so hard that the jack screw strips its thread when it tries to slide the bolt (step 8).
   - From now on only the jack screw moves the idler bolt (step 8). Don't turn the idler bolt heads or nuts again.
4. **Jack screws.** From behind, screw an M3 × 20 set screw into the hole in each idler buttress: the block behind the idler slot, inside the tub. Turn it with the 1.5 mm key until its tip touches the idler bolt head. It cuts its own thread in the first few turns.
5. **Motors.**
   - Solder leads at least 150 mm long to each N20 and heat-shrink the joints.
   - Turn the motor so its gearbox is a diamond, with a corner up. Lower it into its V-trough from above, the shaft pointing out through the wall. The gearbox fits the pocket only this way up.
   - Slide it outward along the trough until the gearbox face stops on the skin at the end of the pocket. The shaft and its bearing boss come out through the hole in the skin.
   - Pull a zip tie (at most 3.6 mm wide) through the tunnel under the trough and round the can. Lay the motor leads under the tie for strain relief.
   - Put the tie's head beside the can, not on top, because the toggle hangs above the right-hand motor. Tighten it.
6. **Hubs and sprockets.**
   - On each shaft: an M3 washer (the thrust washer), then the aluminium hub.
   - Push the motor outward, so the gearbox face is against the skin, and slide the hub in until it just touches the washer. The washer must still turn.
   - Turn the shaft so its flat faces the hub's set screw. Put a drop of medium threadlocker on the set screw and tighten it on the flat (1.5 mm key).
   - Check that the shaft end stands at least 2.1 mm proud of the hub's outer face (calipers' depth rod). If it is shorter, the motor's shaft is too short (§1).
   - **Measure the motor's stall torque now, with the hub on and the disc off** (chassis `spec.md` §8, test 2): screw the 50 mm arm to the hub and connect the motor's leads straight to the freshly charged pack for 1 s (that is 100 % PWM), with the arm pressing down on the kitchen scale. It must read ≤ 371 g. If it reads more, the motor isn't the specified type: don't fit the sprocket disc to it.
   - Bolt the sprocket disc to the hub through the slots: 4 × M3 × 12, each with a washer. The shaft end centres the disc in its middle hole.
   - Tighten the screws evenly (2.5 mm key) and spin the sprocket: it should run true.
7. **Wheels and idlers.**
   - On each road-wheel bolt: washer, road wheel (hub towards the wall), washer, nyloc. Tighten the nyloc until the wheel has about 0.3 mm of end play and still spins freely.
   - On each idler bolt, outside its wall nut: washer, idler (hub towards the wall), washer, nyloc, set the same way to about 0.3 mm of end play.
   - **While you turn an idler's nyloc, hold its bolt head still with the 2.5 mm key from inside the tub.** The nyloc drags the bolt round with it, and a fraction of a turn undoes the step-3 snug. Once the idler is on, the wall nut is behind its hub, and the snug can't be redone without taking the idler off again.
8. **Tracks.**
   - The idler bolts are snug at the rear of their slots (step 3), so the idlers are as far back as they go. If a jack screw's tip is pressing on its bolt head, back it off a turn.
   - Wrap each 34-link loop round its sprocket, road wheels and idler, grousers out. Close it with the last pin at the front of the idler, where nothing is in the way. Back up the inner outer knuckle with a small block while you press.
   - **Tension each track with its jack screw only.** Turn it in with the 1.5 mm key: it pushes the snug idler bolt forward, and the bolt slides along its two oiled plates. Stop when the top run sags 3–5 mm midway between the sprocket and the first road wheel; the top run rests on the road wheels, so read the sag in that 40 mm span. Don't go tighter, because tension costs drive torque.
   - Never loosen an idler bolt to move its idler, and never pull the idler forward by hand to tension the track. The jack screw holds the tension; the clamp is not counted on to hold anything.
   - **Witness mark.** Inside the tub, draw a fine pen line across the rim of each idler bolt's Ø9 head washer and onto the head plate beside it, at the washer's rear edge (the plate always shows at least 3 mm behind the washer). The head plate can't move in its recess, so if the bolt ever slides, the line breaks. It stays in view from above with the lid off.
9. **Sensor.**
   - Bend the HC-SR04's four pins 90° towards the rear.
   - Solder leads at least 150 mm long to the pins and heat-shrink them. If section 2 puts the ECHO divider in the lead, solder it in now.
   - Fit the board behind the front wall with its transducers through the holes. A dab of hot glue each side holds it.
10. **Battery.** Strap the battery holder to the floor with the velcro through the two floor slots, with the overlap under the floor.
11. **Lid.**
    - Stick the mini breadboard on the front of the lid and push the TB6612 into it. Stick the buck under the lid, beneath the breadboard, on foam tape.
    - Fit the toggle through its hole, lever up, with a nut each side of the deck. If the bushing is too short for both nuts, leave the inner nut off.
    - Push the jumpers onto the ESP32's pins. Then seat it pins-down on its ledges and fix it with two small zip ties through the slots at its ends: across the pin-free ends of the board, never across the pin rows. Pull them snug by hand only: a tie pulled tight with pliers can split the slot's inner wall (lid strength round 4).
    - Fold the ESP32's wires flat towards the cable slots, one layer deep. There are 5 mm between the jumper housings and the battery holder, and 3.5 mm over the strap.
    - Bring the motor, battery and sensor leads up through the two cable slots and zip-tie the bundle to the bar between them. Leave at least 150 mm of slack below, so the lid can lie beside the rover.
    - Wire per section 2, then screw the lid on: 4 × M3 × 8 into the inserts.
12. **Proof tests.** You measured each motor's stall torque in step 6, before its sprocket disc went on (chassis `spec.md` §8, test 2). Now do each part's `spec.md` §8 proof tests, then the system tests in this job's `spec.md` §8.

**Service**
- **Charging.** Undo the 4 lid screws and lift the lid aside on its leads. Take the cells out and charge them in the two-bay charger.
- **Re-tensioning.**
  - Take the lid off. The sensor and the idler bolt heads stay as they are.
  - Turn each jack screw in with the 1.5 mm ball-end key, from above and behind, within 25° of the screw's axis. It slides the snug idler bolt forward. Don't touch the idler bolt itself.
  - To slacken a track, back its jack screw off and push the idler back.
  - Redraw the witness marks (step 8) after re-tensioning.
- **Track wear.** When the idler reaches the front of its slot, take one link out. The idler goes back 5 mm, to near the middle of its slot.
- **Opening a track or replacing a link.**
  - Turn the track so the joint is at the front of the idler.
  - Back up the inner outer knuckle with a small block, and drift the pin inward with a Ø2 punch or press it with a small clamp.
- **Replacing a motor.**
  1. Take the lid off. Slacken the track and walk the chain off the sprocket.
  2. Take off the sprocket disc (4 screws). Loosen the hub's set screw and pull off the hub and the thrust washer.
  3. Cut the zip tie and unplug the leads at the breadboard.
  4. Slide the motor inward along its trough until the gearbox leaves the pocket, then lift it out.
- **Replacing an axle bolt.** A road-wheel bolt needs the battery out, and an idler bolt needs the sensor out and the idler off. Refit an idler bolt as in step 3: both plates in place and oiled, a Ø9 washer under the head and under the nut, the nut held with the spanner while you snug the head to 0.04 N·m with the key's short arm. Then refit the idler as in step 7, holding the head while you set the nyloc.

## 4. First drive

Flash `rover_test/rover_test.ino` (Arduino IDE, board "ESP32 Dev Module" on the arduino-esp32 3.x core; `analogWrite` needs 2.x or later). Prop the rover up so the tracks are off the ground, switch on, open the Serial Monitor at 115200 and type `f` (forward). If a track runs backwards, swap that motor's two wires at the TB6612.

| Command | Does |
|---|---|
| `f` / `b` / `l` / `r` | forward, back, left, right. A track that reverses stops for 80 ms first, to spare the gears and sprockets |
| `s` | stop (also ends autonomous mode) |
| `+` / `-` | faster or slower by 10 %, at once (30–100 %) |
| `a` | autonomous on/off: drive forward and turn away from obstacles closer than 15 cm. **On the floor only**: the sensor looks forward and can't see a table edge |
| `d` | print the distance and the battery voltage |

- **Motor voltage:** the 7.4 V pack (8.4 V full) is above the motors' 6 V rating. The sketch reads the pack through the divider once a second and caps the PWM so that the average motor voltage stays at 6 V or less: 182 of 255 on a full pack. With no reading (pack off, or no divider) it keeps that full-pack cap.
- **Flat pack:** when the pack reads below 6.4 V twice in a row (3.2 V per cell under load), the rover stops and won't drive again until restarted. Charge the cells then.
- **Sensor fault:** in autonomous mode, an HC-SR04 that gives no echo pulse at all (a loose wire) stops the rover instead of reading as "clear".
- The motor PWM runs at 20 kHz, above hearing.

Then do the proof tests in each part's `spec.md` §8 and record them in `inspection.md`: track chain under 4.5 kg, wheel bolt under 5 kg at the rim centre, motor stalls, and drops from 5 cm.

## 5. Safety

- Charge the 18650 cells outside the rover with a proper Li-ion charger; never short the holder leads.
- Switch off before working on the wiring.
- Don't let a motor stall for more than a few seconds.

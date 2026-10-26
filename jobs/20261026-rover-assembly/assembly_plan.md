# Assembly plan: tracked rover (ESP32, 2 × N20, printed tracks)

Robot 2 of 3 (after the desktop arm, before the hexapod). Architect: Claude, 2026-10-26.
The user chose the ESP32 and left motors, power and material to the designer.

## Decisions

| Item | Choice | Why |
|---|---|---|
| Layout | Skid-steer tank: one drive sprocket per side at the rear, a toothed idler at the front, two road wheels per side | Simple, turns on the spot, every part prints flat or axis-vertical |
| Drive | 2 × N20 6 V 100 rpm metal-gear motors, gearbox face screwed to the side wall, can on a cradle with a zip tie | Small, cheap, strong enough for a 0.5 kg rover: 10 N of track pull per side, ~170 mm/s |
| Driver | TB6612FNG carrier on a 170-point mini breadboard on the lid | 1.2 A per channel (N20 stall ≈0.6 A), 3.3 V logic matches the ESP32 |
| Controller | ESP32 DevKit (38- or 30-pin) pins-down in a seat on the lid | User's choice; female jumpers reach every pin through the window |
| Power | 2 × protected 18650 Li-ion in series (7.4 V nominal) in a holder strapped to the floor; mini rocker switch in the rear wall; MP1584 buck set to 5.0 V for the ESP32 | 2–3 h of driving; motors rated 6 V, so the test sketch caps PWM at 80 % |
| Sensor | HC-SR04 behind the front wall, transducers through two holes | Obstacle distance for a first autonomous program |
| Tracks | 34 printed links per side, 10 mm pitch, pinned with 1.75 mm filament; 10-tooth sprocket and idler (pitch radius 16.18); road wheels with 45° V-flanges | All printable on the MK3; pins cost nothing |
| Tension | Idler bolt in an 8 mm slot with a sliding captive nut: loosen, push the idler forward, tighten | Takes up pitch error and wear |
| Material | PETG throughout | Tough, wears acceptably at the pins |

## Shared frame (`rover_frame.py`; every model.py imports it)

X forward, Y left, Z up; ground at Z = 0 (grouser bottoms on the straight run); drive-sprocket axis at X = 0.

| Item | Value |
|---|---|
| Axle height (all wheels) | Z 20.68 = pitch radius 16.18 + half link 3 + grouser 1.5 |
| Sprocket → idler | 120 mm nominal (idler slot ±4) = (34 − 10) links × 10 / 2 |
| Road wheels | X 40 and 80 |
| Track centre planes | Y ±55; links 24 wide, inner edge 43 |
| Chassis | X −19 … 135, Y ±38, Z 8.68 … 48.68 (ground clearance 8.7) |
| N20 gearbox face | on the wall's inner face, Y ±35; shaft to Y ±45 |
| Lid | Z 48.68 … 51.68 |

## Printed pieces

| # | Job | Piece | Qty | Orientation |
|---|---|---|---|---|
| 1 | 20261026-rover-chassis | Tub with motor, wheel, battery, switch and sensor features | 1 | floor down |
| 2 | 20261026-rover-lid | Deck with ESP32 seat and breadboard area | 1 | flat |
| 3 | 20261026-rover-sprocket | Drive sprocket, D-bore + grub screw | 2 | disc down, hub up |
| 4 | 20261026-rover-idler | Toothed idler, round bore | 2 | disc down, hub up |
| 5 | 20261026-rover-wheel | Road wheel, V-flanges | 4 | outer flange down |
| 6 | 20261026-rover-track-link | Track link | 68 (2 plates of 34) | inner face down |

## Assembly check (`assembly_check.py` → `assembly_check.json`, `assembly_rover.png`)

Both 34-link loops placed pin by pin (13 on the bottom run, 5 round the idler, 12 on the top run, 4 round the sprocket), with every part and dummies of the motors, battery, HC-SR04, ESP32 (plus jumper housings) and breadboard. Round 1 found the run-out tooth grazing link 0's notch edge (2 mm³ per side); the tooth was slimmed and the notch lengthened. Now: **no collisions**, 7 teeth sit in link notches on every sprocket and idler, the track bottom is at Z 0, overall 160 × 142 × 60 mm.

## Status

| # | Piece | Status |
|---|---|---|
| 1–6 | all | modelled, built, mesh-checked, assembly-checked; DFM and strength review next |

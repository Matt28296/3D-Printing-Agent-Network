# Assembly plan: hexapod (18 × MG90S, ESP32 + 2 × PCA9685)

Robot 3 of 3 (after the arm and the rover). Architect: Claude, 2026-10-26.
The user chose the ESP32 and left servos, power and material to the designer.

## Decisions

| Item | Choice | Why |
|---|---|---|
| Layout | 6 identical 3-DOF legs (coxa, femur, tibia) on a two-plate body; legs at ±40°, ±90°, ±140° | Classic hexapod; identical legs = 3 part types printed 6 times |
| Servos | 18 × MG90S (metal-gear micro, ≈216 N·mm stall at 6 V) | Light enough that a tripod (3 legs) carries the ≈0.6 kg robot: ≈90 N·mm static at the femur |
| Servo drivers | 2 × PCA9685 16-channel boards (I²C, addresses 0x40 and 0x41) on the top plate | 18 channels; frees the ESP32's pins |
| Controller | ESP32 DevKit pins-down in a seat on the top plate | User's choice |
| Power | 2S 1000 mAh LiPo between the plates; 6 V 5 A UBEC for the servo rail; MP1584 at 5 V for the ESP32 | Light (≈65 g); MG90S rated 4.8–6 V |
| Leg geometry | coxa 32, femur 45, tibia 70 mm | Neutral stance: femur level, tibia vertical, body underside 49 mm up |
| Horn joints | SG90/MG90S single-arm horns in 2 mm pockets, clamped by an M2×12 centre screw + washer through the link | The arm's strength review showed the stock horn screw alone holds only the horn |
| Material | PETG | Low creep under the servos' constant holding load |

## Shared frame (`hex_frame.py`; every model.py imports it)

World: X forward, Y left, Z up, ground Z = 0, origin under the body centre. Coxa tab plane (bottom-plate underside) at Z 92.7 in the neutral stance. Leg frames S0 → C → S1 → F → S2 → T are defined in `hex_frame.py` and built by `leg_frames()` in `assembly_check.py`.

| Leg | Mount (x, y) | Angle |
|---|---|---|
| Left front / middle / rear | (60, 42) / (0, 52) / (−60, 42) | 40° / 90° / 140° |
| Right front / middle / rear | (60, −42) / (0, −52) / (−60, −42) | −40° / −90° / −140° |

## Printed pieces

| # | Job | Piece | Qty | Orientation |
|---|---|---|---|---|
| 1 | 20261026-hexapod-body-bottom | Bottom plate + 4 columns | 1 | flat, tab face down |
| 2 | 20261026-hexapod-body-top | Top plate / electronics deck | 1 | flat |
| 3 | 20261026-hexapod-coxa | Coxa bracket | 6 | horizontal plate down |
| 4 | 20261026-hexapod-femur | Femur | 6 | flat |
| 5 | 20261026-hexapod-tibia | Tibia | 6 | flat |

## Assembly check (`assembly_check.py` → `assembly_check.json`, `assembly_hexapod.png`)

Neutral stance: **no collisions**, all six foot tips at Z 0.0, overall 277 × 282 × 146 mm, body underside 49 mm above the ground.

| Sweep | Collision-free |
|---|---|
| All coxae together | −45° … +45° |
| Neighbouring legs turned towards each other (front/middle, middle/rear) | up to 35° each (70° closing) |
| Femur (tibia straight down) | −70° … +90° |
| Tibia (femur +30°) | −170° … 0° |

Gait software should keep neighbouring coxae from closing by more than 70° in total.

## Status

| # | Piece | Status |
|---|---|---|
| 1–5 | all | modelled, built, mesh-checked, assembly-checked; DFM and strength review next |

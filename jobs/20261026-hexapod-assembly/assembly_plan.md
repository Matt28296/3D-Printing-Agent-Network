# Assembly plan: hexapod (18 × MG90S, ESP32 + 2 × PCA9685)

Robot 3 of 3 (after the arm and the rover). Architect: Claude, 2026-10-26. Round 3: design-lead, 2026-10-26, after the
deep review (`docs/reviews/2026-10-26-deep-review/01-bought-parts.md`, `05-hexapod-system.md`) and strength round 1.
The user chose the ESP32 and left servos, power and material to the designer.

## Decisions

| Item | Choice | Why |
|---|---|---|
| Layout | 6 identical 3-DOF legs (coxa, femur, tibia) on a two-plate body; legs at ±40°, ±90°, ±140° | Classic hexapod; identical legs = 3 part types printed 6 times |
| Servos | 18 × MG90S (metal-gear micro, 216 N·mm stall at 6 V), with their own spec in `tools/hobby_parts.py` (B2): body 22.8 × 12.2, spline top 14.0 above the tab underside, case bottom 18.5 below | Light. Their torque margin is the robot's weak point: see "Stance" |
| Servo drivers | 2 × PCA9685 16-channel boards (I²C, addresses 0x40 and 0x41) on the top plate | 18 channels; frees the ESP32's pins |
| Controller | ESP32 DevKit pins-down in a seat on the top plate | User's choice |
| Power | 2S 1000 mAh LiPo between the plates; UBEC for the servo rail on its side beside the LiPo; MP1584 at 5 V for the ESP32 on the deck | Wiring and power belong to the electronics review (02) and its agent |
| Leg geometry | coxa 32, femur 45, tibia 70 mm | Servo centre: femur level, tibia perpendicular. Walking stance: tibias tucked 18.7° in (below) |
| Servo mounting (B1) | Coxa and tibia servos **reversed** (tabs on the plate's far face); femur servos **normal** with a lead notch | See "B1" below |
| Horn joints | SG90/MG90S single-arm horns in 2 mm pockets, clamped by an M2 centre screw + washer through the link, driven **snug (≈ 0.05 N·m)** | Strength round 1: at 0.1 N·m the washer pulls through the floor |
| Material | PETG | Low creep under the servos' constant holding load |

## B1: how each servo's lead passes its window (deep review 01)

No lead could pass its closed window. Each window now has one of the two fixes the review proposed:

| Window (×6 each) | Part | Fix | Why |
|---|---|---|---|
| Coxa servo | body-bottom (6 mm) | **Option 2, reversed**: lowered in from above, spline first; tabs on the plate's **top** face; case and lead stay inside the body (`lead='none'`) | The lead never crosses the plate. The bracket's back face is 4.1 mm under the plate (horn face 6.1). No notch or moved pilot in the strip outside the window, which is the plate's critical section (strength: SF 3.23 in the drop at T_BODY 6); option 1 would cut 1.6 mm into it and move a pilot into it |
| Femur servo | coxa vertical plate (10 mm) | **Option 1**: case through the window as before; lead notch 4.4 × 1.6 at the outboard end; outboard pilot moved 1.3 mm out; **file that tab's slit to 2.1 mm** (`lead='notch_shift_pilot'`) | Option 2 needs the link's back face clear of the plate's far face: it sits 10.1 − T_V beyond it. With the strength round's T_V 10 that is **0.1 mm**, so the femur would rub the plate. The 13 mm posts leave 9.4 mm past the moved pilot, so the plate needs no lengthening |
| Tibia servo | femur (7 mm) | **Option 2, reversed**: tabs on the femur's **back** face, upper case and spline through the window towards the tibia, case and lead behind the femur (`lead='none'`) | The tibia's back face is 3.1 mm off the femur's front face. The case (21 mm deep) clears the coxa bracket by ≥ 3.3 mm over the gait and ≥ 0.76 mm over the femur's whole −70…+90° (a 6 mm corner cut on the coxa plate). The tibia moves 9.5 mm closer to the femur: femur torsion drops and the foot sits 12.7 mm off the coxa line, not 22.2 |

So the builder files **6 tabs**, not 18 (one per femur servo, the tab at its shaft end).

## Shared frame (`hex_frame.py`; every model.py imports it)

World: X forward, Y left, Z up, ground Z = 0, origin under the body centre. `hex_frame.leg_frames()` builds each leg's frames
S0 → C → S1 → F → S2 → T and `hex_frame.ik()` inverts them (closed form; checked against the frames to 1e-13 mm).

| Quantity | Round 2 | Round 3 | Source |
|---|---|---|---|
| `LB` servo tab underside → link back face | 9.4 | **12.6** | B2: MG90S spline 14.0 above the tabs |
| `T_C` / `T_V` / `T_BODY` | 5 / 4.5 / 4 | **8 / 10 / 6** | Strength round 1 (coxa and body-bottom) |
| `Z_F` femur axis below the bracket's back face | 17 | **20** (= T_C + 12) | T_C 8 |
| Coxa tab underside (S0) above the plate underside | 0 | **8.5** (T_BODY + tab 2.5) | B1 option 2 |
| Plate underside → bracket back face (`PLATE_GAP`) | 9.4 | **4.1** | |
| Tibia servo tab underside (S2) on the femur | front face, F z 7 | **back face, F z −2.5** | B1 option 2 |
| Foot sideways from the coxa line (`FOOT_SIDE`) | 15.8 | **12.7** | |
| Plate underside above the ground | 96.4 | **94.1** | servo centre and walking stance alike |
| Lowest point (coxa vertical plates) above the ground | 49.2 | **49.0** | `assembly_check.json` |

| Leg | Mount (x, y) | Angle |
|---|---|---|
| Left front / middle / rear | (60, 42) / **(0, 56)** / (−60, 42) | 40° / 90° / 140° |
| Right front / middle / rear | (60, −42) / **(0, −56)** / (−60, −42) | −40° / −90° / −140° |

The middle legs moved out 4 mm (y ±52 → ±56): with the coxa tabs now on the plate top, their inner tabs and nuts would sit
where the UBEC stands beside the LiPo. The four columns moved in (x ±40 → ±36) for the same reason at the corner legs.

## Stance (SYS-1)

The femur servos are the robot's weak point. SYS-1 proposed tucking the tibias 15° in (femur −3°, tibia −12° in the
firmware's angles); the strength review proposed 18.7°, which puts the foot midway between the femur axis and the knee. Both
keep the body height when the femur drops a little. `stance_torques.py` walks both on the round-3 frames with the IK
straight-line gait and solves the three foot loads exactly on every tripod frame (lone leg up to 41.7 %).

Peak static torque of any planted leg, N·mm (% of the 216 N·mm stall), femur / knee:

| Robot mass | Stance | Tripod, standing | Gait 30 mm stride | Gait 40 mm stride |
|---|---|---|---|---|
| 683 g (strength basis) | SYS-1: femur −3.0°, tibia −12.0° | 74 / 50 | 81 (37 %) / 62 (29 %) | 84 (39 %) / 72 (33 %) |
| 683 g | **Strength: femur −4.7°, tibia −14.0°** | 62 / 62 | **70 (32 %) / 72 (33 %)** | **73 (34 %) / 82 (38 %)** |
| 812 g (round 3, printed) | SYS-1 | 88 / 59 | 96 (44 %) / 74 (34 %) | 100 (46 %) / 85 (39 %) |
| 812 g | **Strength** | 73 / 73 | **83 (38 %) / 86 (40 %)** | **87 (40 %) / 98 (45 %)** |
| 877 g (round 3, solid parts) | SYS-1 | 95 / 64 | 104 (48 %) / 80 (37 %) | 108 (50 %) / 92 (43 %) |
| 877 g | **Strength** | 79 / 79 | **89 (41 %) / 93 (43 %)** | **94 (43 %) / 106 (49 %)** |
| 683 g | Servo centre (femur 0, tibia 0), for reference | 123 / 0 | 128 (59 %) / 20 | 130 (60 %) / 27 |

**Chosen: the strength review's tuck at the same body height, femur −4.7°, tibia −14.0°** (`hex_frame.NEUTRAL_FEMUR/TIBIA`).
It has the lower peak at both strides and every mass, it balances femur and knee when standing, and it bends the coxa shaft
less (194 against 207 N·mm at 812 g). Walk at **30 mm** stride: 40 % of stall at the round-3 mass; the ×2 walking factor
stays under stall. Above the ~⅓-of-stall guideline, so watch the femur case temperature (assembly `spec.md` §8). If they run
hot, the review's options stand: 3.5 kg·cm-class micro servos (check the fit), or lighter parts.

Joint ranges in the gait (firmware angles), all inside the servo travel with ±20° of trim and inside the free sweeps:

| Stride | Coxa | Femur | Tibia |
|---|---|---|---|
| 30 mm | −15.9 … 15.0 | −12.0 … 22.7 | −38.5 … −6.4 |
| 40 mm | −21.0 … 19.5 | −14.9 … 22.7 | −38.9 … −3.0 |

## Mass

| Part | Qty | Solid volume (cm³) | Solid g (PETG 1.27) |
|---|---|---|---|
| Bottom plate | 1 | 111.7 | 141.9 |
| Deck | 1 | 35.3 | 44.8 |
| Coxa bracket | 6 | 23.3 | 29.6 each, 177.7 |
| Femur | 6 | 6.0 | 7.6 each, 45.4 |
| Tibia | 6 | 7.0 | 8.9 each, 53.5 |
| **Printed, solid** | | | **463** (round 2: 304) |

Robot: **812 g** with the deep review's printed fraction (0.76 of solid) and its bought list plus round 3's nuts, washers,
switch and six more servo extensions; **877 g** on the strength review's basis (solid parts). Round 2 was 662–683 g. The strength
set's coxa brackets add 116 g and the 6 mm bottom plate 46 g: every walking and servo load rises by 19–28 %, but the drop cases
are set by the servos' back-drive cap, not by mass.

## Assembly check (`assembly_check.py` → `assembly_check.json`, `assembly_hexapod.png`)

Bodies: both plates, 6 × (coxa, femur, tibia, 3 MG90S with gear boss, tab-screw hardware, horn clamp screws), LiPo, **UBEC
(50 × 10 × 20 on its side at y 22.5–32.5, x ±25, beside the LiPo)**, main switch body, ESP32 with jumper housings and bend
zone, 2 × PCA9685. Collision = overlap > 1 mm³.

| Pose | Result |
|---|---|
| Servo centre (femur level, tibia perpendicular) | no collisions, feet at Z 0 |
| **Walking stance** (femur −4.7°, tibia −14.0°) | **no collisions**, feet at Z 0, overall 276 × 290 × 160 mm |
| **IK gait, 30 mm stride, 20 mm lift, 20 frames** | **no collisions**; neighbouring coxae differ by ≤ 23.6° |
| **IK gait, 40 mm stride, 20 mm lift, 20 frames** | **no collisions**; neighbouring coxae differ by ≤ 32.6° |

| Sweep (from the servo centre) | Collision-free |
|---|---|
| All coxae together | −45° … +45° |
| Neighbouring legs turned towards each other | up to 30° each (60° closing; round 2: 35°) |
| Femur (tibia perpendicular) | −70° … +90° (tibia-servo case ≥ 0.76 mm from the coxa bracket) |
| Tibia, firmware angle (femur +30°) | −80° … +90° |

`MAX_COXA` 30 still keeps neighbours inside the 60° the check allows; the gait itself needs ≤ 33°.

## Firmware: neutral-stance constants (for `hexapod_test.ino`)

Another agent is rewriting the sketch (IK gait, PCA9685 clock, power, channel map); its version is not in this branch yet.
Its "NEUTRAL STANCE AND LEG GEOMETRY" block should read:

```
const float L_C = 32.0f, L_F = 45.0f, L_T = 70.0f;
const float Y_F = -13.5f;                 // unchanged
const float Z_F = 20.0f;                  // T_C 8 + 12 (was 17)
const float T_F = 7.0f, T_T = 7.0f;
const float LB = 12.6f;                   // MG90S own spec, B2 (was 9.4)
const float NEUTRAL_FEMUR = -4.7f;        // walking stance: tibias tucked 18.7° in at the same body height
const float NEUTRAL_TIBIA = -14.0f;
```

Two formulas outside that block change with the reversed tibia servo (tell that agent, or apply when merging):
- `footSide` = Y_F + 2·LB − TAB_T + T_T/2 = **12.7 mm** (TAB_T 2.5). Its current `Y_F + 2·LB + T_F + T_T/2` gives 22.2.
- The printed "body underside" is the bottom plate's underside: −footH0 + 4.1 = **94.1 mm** (was LB − footH0).
- Limits: FEMUR −70…+90 and TIBIA −80…+90 still hold; `MAX_COXA` 30 is at the new 60° neighbour limit.

## Interfaces and stack-ups (SYS-13, round 3)

| Interface | Value |
|---|---|
| Plate underside → coxa bracket back face | 4.1 mm; the outer tab screw's head + washer stand 1.9 mm proud: 2.2 mm clear |
| Coxa gear boss below the plate / to the bracket | 1.4 mm below / 2.7 mm clear |
| Link back face → servo gear boss (all joints) | 2.7 mm |
| Femur back face → coxa vertical plate's +y face | 12.6 mm (femur-servo tabs and heads take 4.1) |
| Tibia back face → femur front face | 3.1 mm (femur clamp washer + head 2.1 at the femur axis) |
| Tibia-servo case (behind the femur) → coxa bracket | ≥ 3.3 mm over the gait, ≥ 0.76 mm over the femur's −70…+90° |
| Coxa servo case top inside the body | 21 mm above the plate top (deck underside at 40) |
| Corner coxa inner tab + nut → column (r 4, fillet r 5.5) | 3.4 mm / 2.2 mm |
| UBEC → LiPo / middle coxa servo's inner nut | 5 mm (strap between) / 1.6 mm |
| Coxa tab screws (M2 × 12, washer, plate 6, tab 2.5, washer, nut) | 1.3 mm of thread past the nut |
| Femur-servo tab screws (M2 × 10) | 7.5 mm into the 10 mm plate |
| Tibia-servo tab screws (M2 × 8, from behind) | 5.5 mm into the 7 mm femur, tip 1.5 mm short of its front face |

## Printed pieces

| # | Job | Piece | Qty | Orientation |
|---|---|---|---|---|
| 1 | 20261026-hexapod-body-bottom | Bottom plate + 4 columns | 1 | flat, underside down |
| 2 | 20261026-hexapod-body-top | Top plate / electronics deck | 1 | flat |
| 3 | 20261026-hexapod-coxa | Coxa bracket | 6 | horizontal plate down |
| 4 | 20261026-hexapod-femur | Femur | 6 | flat, back face down |
| 5 | 20261026-hexapod-tibia | Tibia | 6 | flat |

## Status

| # | Piece | Status |
|---|---|---|
| 1–4 | bottom plate, deck, coxa, femur | round 3 modelled, built, mesh-checked, `cad_checks.py` pass, assembly-checked; DFM and strength review next |
| 5 | tibia | geometry unchanged; docs updated (loads, proof test, clamp torque) |

Open, for other owners: the channel map and wiring table (lead routing "up the deck edge beside each leg" through the deck's
notches; the femur leads probably need extensions, 05 SYS-4); the UBEC's size (the check allows 50 × 10 × 20 on its side; an
8–10 A unit needs a new check); the main switch (the deck has a Ø12 hole for a 12 mm-bushing toggle rated ≥ 10 A DC);
re-slicing all four changed parts.

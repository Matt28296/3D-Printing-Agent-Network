# Part spec: Hexapod (assembly of 20 printed parts)

Job: 20261026-hexapod-assembly · Written by: Architect; filled in round 3 by design-lead (deep review SYS-14) · Date: 2026-10-26 · Plan: [assembly_plan.md](assembly_plan.md) · Build: [BUILD_GUIDE.md](BUILD_GUIDE.md)

## 1. Function
A six-legged walker for indoor floors: 18 MG90S servos (3 per leg), ESP32 + 2 × PCA9685 on the top deck, 2S LiPo between the body plates. It stands, and walks a straight-line tripod gait (30 mm stride, 20 mm lift) on hard floors and low-pile carpet.

## 2. Envelope and interfaces
- Size standing (walking stance): 276 × 290 × 160 mm; bottom plate's underside 94.1 mm above the ground; lowest point (coxa brackets) 49.0 mm.
- Mass: ≈ 812 g (877 g with solid printed parts).
- Printed parts and their jobs: `assembly_plan.md` "Printed pieces". Shared frames and numbers: `hex_frame.py`.
- Servo mounting (deep review B1):
  - coxa and tibia servos reversed (tabs on the plate's far face);
  - femur servos in the normal way, with a lead notch and the outboard pilot moved 1.3 mm. The builder files that tab's slit to 2.1 mm.
- Fasteners: as `BUILD_GUIDE.md` §1.
  - Coxa tabs: M2 × 12 machine screws with washers and nuts.
  - Femur-servo tabs: M2 × 10 self-tapping.
  - Tibia-servo tabs: M2 × 8 self-tapping.
  - Horn clamps: M2 × 12 + Ø6 washer (femur, tibia) and M2 × 12–14 + Ø10 × 1 penny washer (coxa), all driven snug (≈ 0.05 N·m).
  - Deck: 4 × M3 × 8 self-tapping.

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Foot tips in the stance | Z 0 (all six) | ±2 | the trims absorb it (1° of femur = 0.8 mm at the foot) |
| Leg mounts | (±60, ±42) at ±40°, ±140°; (0, ±56) at ±90° | ±0.3 | `hex_frame.LEG_MOUNTS` |
| Coxa / femur / tibia lengths | 32 / 45 / 70 | ±0.3 | leg geometry |
| Bottom-plate underside → coxa bracket back face | 4.1 | ±0.5 | clearance (tab-screw heads stand 1.9 proud) |
| Servo windows (all 18) | 23.2 × 12.8 CAD (≈ 23.0 × 12.6 printed) for a 22.8 × 12.2 MG90S | +0.3/−0 | 0.1 end / 0.2 side clearance |

## 4. Loads
Robot-level loads the part specs are checked against (strength round 1): robot 662–683 g (round-3 geometry: 812–877 g, which raises every walking and servo load by 19–28 %); a tripod's lone-side leg carries 41–43 % → **2.90 N** sustained at its foot, **5.80 N** walking (×2); foot scrub µ 0.5; servo stalls 216 N·mm; a 3 N sideways shove; a 20 cm drop, capped at **19.2 N** per foot by the femur and knee servos back-driving. Servo torques in the walking stance: `assembly_plan.md` "Stance" (peak 87 / 98 N·mm femur / knee at 40 mm stride and 812 g; 83 / 86 at 30 mm).

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Standing on a tripod | 2.90 (683 g) – 3.32 (812 g) per lone foot | foot tip, up | sustained | minutes |
| Walking | 5.80 – 6.6 per foot | foot tip, up | cyclic | 10–15 min per charge |
| Coxa shaft bending (each leg hangs on its coxa servo) | 194 N·mm at 812 g in the walking stance | coxa horn | cyclic | — |
| 20 cm drop | 19.2 per foot (servo back-drive cap) | feet | short-term | — |

## 5. Environment
- Max temperature (°C): 40 ambient; MG90S cases must stay below 50 °C (§8)
- Outdoor / UV: no
- Chemicals, oils, moisture: none

## 6. Material
- Preferred or required: PETG for every printed part
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA (creep under the servos' holding load)

## 7. Quantity and time
- Quantity: 1 robot (20 printed parts)
- Max acceptable print time per batch (h): see each part's spec

## 8. Acceptance criteria (measurable)
- [ ] Assembly check clean: `assembly_check.json` `"clean": true` (stance, servo centre and the 30/40 mm gait, every frame)
- [ ] **Leg proof test (deep review SYS-6), on one assembled leg mounted on its coxa servo, before the full build:**
  1. Hang **680 g** (6.6 N, 2 × the round-3 tripod foot load; 570 g at the review's 662 g) at the foot for 10 min.
  2. Measure the foot's vertical play under ±1 N.
  3. Walk for 30 min and measure again.
  4. Pass: the play grows by less than 1 mm at the foot, with no clicking or skipped teeth.
  If it fails, the bracket needs a second support opposite the horn (see the coxa `design_brief.md`, "SYS-6").
- [ ] Stands 10 min on six legs, powered, with every femur servo case below 50 °C
- [ ] Walks 2 m on a hard floor and 1 m on low-pile carpet with under 10 % drift
- [ ] Walks 10 min or more per charge
- [ ] Survives the 20 cm drop (body-bottom `spec.md` §8)

## 9. Notes and open questions
None open for the printed parts. Wiring, the channel map, the UBEC's size and the switch belong to the electronics owner (`assembly_plan.md`, "Status").

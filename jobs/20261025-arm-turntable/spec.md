# Part spec: Turntable with shoulder upright

Job: 20261025-arm-turntable · Written by: Architect · Date: 2026-10-25 · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Ø96 × 8 mm disk whose flat underside sits on the base servo's double-arm horn (no pocket, so no bridge), with a 66 × 7 mm upright, root wedges and two 70 mm gussets that hold the shoulder MG996R horizontally (shaft +Y, axis at X 10.15, Z 60.5).

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 96 × 96 × 80.8 mm. Interfaces: Ø3.4 clamp-screw hole on the yaw axis; shoulder MG996R window 41.1 × 20.1 with 45° roof, 4 × Ø2.6 horizontal teardrop pilots.
- Fasteners used: Base horn: M3×16 centre screw + Ø9 washer from the top through the disk into the spline (clamps disk + horn), plus 2 small screws drilled through the horn's arm holes into the disk; shoulder servo: 4 tab screws. Drive the centre screw BEFORE fitting the shoulder servo (the servo body covers the hole).

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Clamp hole | Ø3.4 | +0.2/−0 | M3 clearance |
| Shoulder window | 41.1 × 20.1 | +0.3/−0 | clearance 0.2/side |
| Shoulder axis | X 10.15, Z 60.5 (assembly frame) | ±0.3 | position |

Servo dimensions are nominal (tools/hobby_parts.py). Measure your servos and horns first (body length/width, tab-hole spacing, shaft-to-end distance, double-arm horn hub Ø, arm length and tip width) and put any differences into `replace(MG996R, ...)` / `replace(SG90, ...)` in model.py. An optional fit coupon can be printed first.

## 4. Loads
Design loads come from the servos' datasheet stall torques (MG996R 1000 N·mm, SG90 160 N·mm at 6 V), because a stalled servo is the worst case the part sees, plus the arm's own weight with a 50 g payload. Round 2 adds the out-of-plane cases found by the strength review: the pitch servos give no resistance sideways, so a **base-yaw stall into a side obstacle** (swept over the joint ranges, up to 12 N at the fingertip) and a **5 N sideways hand push at the fingertip** load the printed plates and horn joints directly.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Shoulder servo stall reaction | 1000 N·mm about Y | 4 tab screws → upright (in its plane) | short-term | seconds |
| Base servo stall | 1000 N·mm about Z | horn slot walls (bearing) | short-term | seconds |
| Arm weight out of the upright plane | ≈100 N·mm about X static (×2 dynamic) | upright root + gussets | sustained | hours |
| Base-yaw stall / 5 N sideways hand push at the fingertip | up to 12 N at the fingertip, ≈300 mm lever | upright out of plane, base-horn joint | short-term | seconds |

## 5. Environment
- Max temperature the part will see (°C): 40 (indoor desk; servo cases reach ~45 °C under sustained stall, so do not stall the servos for minutes)
- Outdoor / UV: no
- Chemicals, oils, moisture: none

## 6. Material
- Preferred or required: PETG (Prusament PETG or equivalent), user left the choice to the designer
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA for the load-path parts (creeps under sustained servo-holding load); ABS/ASA (no enclosure needed for this job)

## 7. Quantity and time
- Quantity: 1
- Max acceptable print time per batch (h): 8

## 8. Acceptance criteria (measurable)
- [ ] Shoulder MG996R slides into the window and all 4 tab screws bite
- [ ] Base horn seats flat in its slot
- [ ] **Proof test:** (1) Assembled arm, shoulder servo powered and holding with the upper link horizontal: hang 1 kg at the elbow axis for 1 min. (2) Arm pointing straight up, servos unpowered: push 10 N (≈1 kg on a luggage scale) sideways (±Y) at the fingertip, 1 min each way, then repeat with the elbow at 90°. Pass: no cracks or whitening at the upright window corners, the tab pilots, the gusset toes or the upright–disk corner; the base horn doesn't lift off; the fingertip returns to within 1 mm.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

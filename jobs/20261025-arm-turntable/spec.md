# Part spec: Turntable with shoulder upright

Job: 20261025-arm-turntable · Written by: Architect · Date: 2026-10-25 · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Ø96 × 5 mm disk that sits on the base servo's double-arm horn (2 mm slot pocket underneath), with a 66 × 5 mm upright and two gussets that hold the shoulder MG996R horizontally (shaft +Y, axis at X 10.15, Z 60.5).

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 96 × 96 × 82.6 mm. Interfaces: double-arm horn slot (hub Ø11.5, tip-to-tip 41, depth 2) with Ø6.5 screw access; shoulder MG996R window 41.1 × 20.1 with 45° roof, 4 × Ø2.6 horizontal pilots.
- Fasteners used: Base horn: its centre screw through the Ø6.5 access hole, plus 2 small screws drilled through the horn's arm holes; shoulder servo: 4 tab screws

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Horn slot | hub Ø11.5, width 6.0 at tips, depth 2.0 | +0.2/−0 | horn locating, clearance 0.25/side |
| Shoulder window | 41.1 × 20.1 | +0.3/−0 | clearance 0.2/side |
| Shoulder axis | X 10.15, Z 60.5 (assembly frame) | ±0.3 | position |

Servo dimensions are nominal (tools/hobby_parts.py). Measure your servos and horns first (body length/width, tab-hole spacing, shaft-to-end distance, double-arm horn hub Ø, arm length and tip width) and put any differences into `replace(MG996R, ...)` / `replace(SG90, ...)` in model.py. An optional fit coupon can be printed first.

## 4. Loads
Design loads come from the servos' datasheet stall torques (MG996R 1000 N·mm, SG90 160 N·mm at 6 V), because a stalled servo is the worst case the part sees, plus the arm's own weight with a 50 g payload.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Shoulder servo stall reaction | 1000 N·mm about Y | 4 tab screws → upright (in its plane) | short-term | seconds |
| Base servo stall | 1000 N·mm about Z | horn slot walls (bearing) | short-term | seconds |
| Arm weight out of the upright plane | 2 N at 60 mm offset → 120 N·mm about X (×2 dynamic) | upright root + gussets | sustained | hours |

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
- [ ] **Proof test:** Assembled arm, shoulder servo powered and holding with the upper link horizontal: hang 1 kg at the elbow axis (≈1000 N·mm) for 1 min. Pass: no cracking at the upright root, gussets or pilots; servo may stall but nothing printed yields.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

# Part spec: Femur (×6)

Job: 20261026-hexapod-femur · Written by: Architect · Date: 2026-10-26 · Assembly: [20261026-hexapod-assembly](../20261026-hexapod-assembly/assembly_plan.md)

## 1. Function
7 mm flat plate from the femur MG90S horn to the knee (45 mm), carrying the tibia MG90S.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 64.9 × 19 × 7 mm. Interfaces: SG90-size arm-horn pocket + Ø2.4 clamp hole; MG90S window at x 45.
- Fasteners used: Femur horn: M2×12 centre screw + Ø6 washer + 1 arm screw; tibia servo: 2 tab screws (M2×8 self-tapping)

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Femur axis → knee | 45.0 | ±0.3 | leg geometry |

Servo dimensions are nominal: MG90S kept at the SG90 body size the arm parts were reviewed with (tools/hobby_parts.py). Makers list 22.5–22.8 × 12–12.2 mm, so measure your MG90S (body length and width, tab-hole spacing, shaft to near end, horn hub and arm) and give Claude any difference over 0.3 mm. The SG90 window ends have only 0.1 mm clearance each.

## 4. Loads
Design loads: MG90S stall ≈216 N·mm at 6 V; robot ≈0.6 kg (6 N) standing on 3 legs in a tripod gait → ≈2 N per foot, ×2 for walking dynamics → **4 N per foot**; femur horizontal and tibia vertical puts the foot 45 mm out from the femur axis and 77 mm out from the coxa axis; a **20 cm drop** onto the feet is taken as 3 × weight shared by 6 feet (≈3 N per foot, short-term), and a sideways shove of 3 N at a foot.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Foot load | 4 N at 45 mm (+ tibia) → ≈180 N·mm in plane | plate bending (19 mm deep section) | cyclic | hours |
| Femur stall | 216 N·mm | pocket bearing, in-plane bending | short-term | seconds |
| Sideways shove | 3 N at the foot, ≈90 mm lever | out-of-plane bending, horn clamp | short-term | seconds |

## 5. Environment
- Max temperature (°C): 40 (indoor floor; MG90S cases warm under load)
- Outdoor / UV: no
- Chemicals, oils, moisture: none

## 6. Material
- Preferred or required: PETG (designer's choice; the user left material to the designer)
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA (creep under constant servo-holding load); TPU only as optional foot socks

## 7. Quantity and time
- Quantity: 6
- Max acceptable print time per batch (h): 3

## 8. Acceptance criteria (measurable)
- [ ] Tibia MG90S fits; tab screws bite
- [ ] **Proof test:** Clamp the femur horn; hang 1 kg at the knee axis for 1 min, then push 3 N sideways at the end of the tibia. Pass: no cracks, no lift off the horn, no permanent set.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

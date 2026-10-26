# Part spec: Hexapod bottom body plate

Job: 20261026-hexapod-body-bottom · Written by: Architect · Date: 2026-10-26 · Assembly: [20261026-hexapod-assembly](../20261026-hexapod-assembly/assembly_plan.md)

## 1. Function
4 mm plate (hull of the six coxa-servo windows, 155 × 131 mm) that the six coxa MG90S hang under (tabs on its underside, shafts down), with four 30 mm columns for the top plate and two strap slots for the 2S LiPo that sits on it.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 155 × 131 × 44 mm (columns). Interfaces: 6 MG90S windows 22.9 × 12.8 with 2 Ø1.7 slotted pilots each, at the mounts in hex_frame.py; 4 columns Ø8 × 40 with r1.5 root fillets and Ø2.8 pilots at (±40, ±25) (hex_frame.COLUMNS, shared with the top plate); strap slots 22 × 3.
- Fasteners used: 12 × MG90S tab screws (servo bag) — use M2×8 self-tapping if the bag screws are short; 4 × M3×8 self-tapping (top plate onto the columns); 1 velcro strap for the LiPo

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Coxa servo windows | 22.7 × 12.6 printed | +0.3/−0 | 0.1 end / 0.2 side clearance |
| Mount positions | per hex_frame.LEG_MOUNTS | ±0.3 | leg spacing |
| Column height | 40.0 | ±0.3 | top-plate seat; room for the ESP32 leads above the LiPo |

Servo dimensions are nominal: MG90S kept at the SG90 body size the arm parts were reviewed with (tools/hobby_parts.py). Makers list 22.5–22.8 × 12–12.2 mm, so measure your MG90S (body length and width, tab-hole spacing, shaft to near end, horn hub and arm) and give Claude any difference over 0.3 mm. The SG90 window ends have only 0.1 mm clearance each.

## 4. Loads
Design loads: MG90S stall ≈216 N·mm at 6 V; robot ≈0.6 kg (6 N) standing on 3 legs in a tripod gait → ≈2 N per foot, ×2 for walking dynamics → **4 N per foot**; femur horizontal and tibia vertical puts the foot 45 mm out from the femur axis and 77 mm out from the coxa axis; a **20 cm drop** onto the feet is taken as 3 × weight shared by 6 feet (≈3 N per foot, short-term), and a sideways shove of 3 N at a foot.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Coxa stall reaction | 216 N·mm per servo | 2 tab screws into the plate | short-term | seconds |
| Standing weight | ≈6 N total through 3 coxa servos (tripod) | plate bending between mounts | sustained | hours |
| Drop (20 cm) | ≈18 N total through the 6 coxa mounts | tab screws, plate | short-term | seconds |

## 5. Environment
- Max temperature (°C): 40 (indoor floor; MG90S cases warm under load)
- Outdoor / UV: no
- Chemicals, oils, moisture: none

## 6. Material
- Preferred or required: PETG (designer's choice; the user left material to the designer)
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA (creep under constant servo-holding load); TPU only as optional foot socks

## 7. Quantity and time
- Quantity: 1
- Max acceptable print time per batch (h): 8

## 8. Acceptance criteria (measurable)
- [ ] All six MG90S fit their windows and their tab screws bite
- [ ] Top plate screws line up with the columns
- [ ] **Proof test:** Robot assembled and standing (servos powered, neutral stance): add 500 g on the top plate for 1 min, then drop it from 20 cm onto a carpeted floor 3 times. Pass: no cracks at the windows, pilots or columns, no servo tab lifting off the plate.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

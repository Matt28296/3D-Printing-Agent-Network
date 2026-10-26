# Part spec: Hexapod top plate / electronics deck

Job: 20261026-hexapod-body-top · Written by: Architect · Date: 2026-10-26 · Assembly: [20261026-hexapod-assembly](../20261026-hexapod-assembly/assembly_plan.md)

## 1. Function
3 mm deck (130 × 104 mm) on the four columns, carrying the ESP32 seat (pins down through a window), two PCA9685 servo drivers on M2.5 posts, the UBEC, and four cable slots for the 18 servo leads.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 130 × 104 × 8 mm. Interfaces: 4 × Ø3.6 holes on the columns at (±40, ±25); ESP32 seat 55.6 × 29.7 (ledges 2 above the deck); 8 posts Ø5.5 × 5 with Ø2.4 pilots on a 56 × 19 pattern at y ±34.5.
- Fasteners used: 4 × M3×8 self-tapping into the columns; 8 × M2.5×6 self-tapping for the PCA9685 boards; 1 zip tie for the ESP32

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| PCA9685 post pattern | 56 × 19 | ±0.2 | board holes |
| ESP32 pocket width | 29.7 | +0.3/−0 | 0.6 clearance |

Servo dimensions are nominal: MG90S kept at the SG90 body size the arm parts were reviewed with (tools/hobby_parts.py). Makers list 22.5–22.8 × 12–12.2 mm, so measure your MG90S (body length and width, tab-hole spacing, shaft to near end, horn hub and arm) and give Claude any difference over 0.3 mm. The SG90 window ends have only 0.1 mm clearance each.

## 4. Loads
Design loads: MG90S stall ≈216 N·mm at 6 V; robot ≈0.6 kg (6 N) standing on 3 legs in a tripod gait → ≈2 N per foot, ×2 for walking dynamics → **4 N per foot**; femur horizontal and tibia vertical puts the foot 45 mm out from the femur axis and 77 mm out from the coxa axis; a **20 cm drop** onto the feet is taken as 3 × weight shared by 6 feet (≈3 N per foot, short-term), and a sideways shove of 3 N at a foot.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Handling (picked up by the top plate) | 6 N robot weight through 4 screws | plate, screw pull-out | short-term | seconds |
| USB / jumper pull | 10 N | seat ledges, rails | short-term | seconds |

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
- Max acceptable print time per batch (h): 5

## 8. Acceptance criteria (measurable)
- [ ] Both PCA9685 boards sit on their posts
- [ ] ESP32 seats with jumpers on every pin
- [ ] **Proof test:** Lift the assembled robot by the top plate 5 times and plug/unplug USB 5 times. Pass: no cracks at the screw holes, posts or seat.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

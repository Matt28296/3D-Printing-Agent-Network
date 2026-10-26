# Part spec: Coxa bracket (×6)

Job: 20261026-hexapod-coxa · Written by: Architect · Date: 2026-10-26 · Assembly: [20261026-hexapod-assembly](../20261026-hexapod-assembly/assembly_plan.md)

## 1. Function
L-shaped bracket under the coxa MG90S horn: a hub plate round the horn and an arm (outside the femur's swing plane) out to a vertical plate that carries the femur MG90S with its axis horizontal and tangential, 32 mm out from the coxa axis.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 53 × 25 × 37.8 mm. Interfaces: SG90-size arm-horn pocket (2 deep, 3 mm floor) + Ø2.6 clamp hole on the bed face; MG90S window 22.9 × 12.6 CAD with a 45° roof and 2 teardrop pilots in the vertical plate (femur axis 17 below the back face); 45° × 5 mm root gusset on the tab side along the plate; r2.5 fillet where the arm leaves the hub.
- Fasteners used: Coxa horn: **M2×10** centre screw + Ø6 washer from below (0.5 washer + 3 mm floor + horn hub + spline thread; the femur and tibia use M2×12) + 1 small screw through the horn arm; femur servo: 2 tab screws (M2×8 self-tapping recommended)

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Coxa axis → femur axis | 32.0 radial | ±0.3 | leg geometry |
| Femur axis height | 17.0 below the back face | ±0.3 | leg geometry (stance: body-plate underside 96.4 above the ground) |

Servo dimensions are nominal: MG90S kept at the SG90 body size the arm parts were reviewed with (tools/hobby_parts.py). Makers list 22.5–22.8 × 12–12.2 mm, so measure your MG90S (body length and width, tab-hole spacing, shaft to near end, horn hub and arm) and give Claude any difference over 0.3 mm. The SG90 window ends have only 0.1 mm clearance each.

## 4. Loads
Design loads: MG90S stall ≈216 N·mm at 6 V; robot ≈0.6 kg (6 N) standing on 3 legs in a tripod gait → ≈2 N per foot, ×2 for walking dynamics → **4 N per foot**; femur horizontal and tibia vertical puts the foot 45 mm out from the femur axis and 77 mm out from the coxa axis; a **20 cm drop** onto the feet is taken as 3 × weight shared by 6 feet (≈3 N per foot, short-term), and a sideways shove of 3 N at a foot.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Foot load through the femur servo | 4 N at 77 mm from the coxa axis → ≈310 N·mm out of plane at the hub; 4 N at 45 mm → 180 N·mm on the vertical plate | hub clamp, arm, vertical-plate root | cyclic | hours |
| Femur stall reaction | 216 N·mm | 2 tab screws in the vertical plate | short-term | seconds |
| Coxa stall | 216 N·mm | horn pocket bearing | short-term | seconds |

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
- Max acceptable print time per batch (h): 6

## 8. Acceptance criteria (measurable)
- [ ] MG90S slides into the vertical-plate window; tab screws bite
- [ ] The femur swings ±70° without touching the arm
- [ ] **Proof test:** Clamp a coxa servo horn in a vice with the bracket and femur servo fitted; hang 1 kg (≈10 N) from the femur servo's horn for 1 min, then push 3 N sideways. Pass: no cracks at the vertical-plate root, the gussets or the pilots, no lift of the bracket off the horn.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

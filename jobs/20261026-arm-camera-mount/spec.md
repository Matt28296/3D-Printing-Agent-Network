# Part spec: Brio 4K camera mount (optional)

Job: 20261026-arm-camera-mount · Written by: Architect · Date: 2026-10-26 · Assembly: [20261025-robot-arm-assembly](../20261025-robot-arm-assembly/assembly_plan.md)

## 1. Function
Holds a Logitech Brio 4K (clip removed) on top of the claw, lens pointing along the fingers and tilted 30° down so the jaws sit near the middle of the picture. The camera's own 1/4"-20 thread takes a knurled thumb screw from under the seat; a rear lip stops it turning. Shares the cover's two top screws, so the claw works without it.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 40.5 × 50 × 24 mm side profile × width (print: 40.5 × 24 × 50). Interfaces: pad x 0–14 on the cover top (z 42–45.5); seat under the camera's bottom face (tilted 30°); lip 6 mm tall behind the camera; 1/4" slot Ø6.85 × 8 along the camera; 2 × Ø3.6 holes at (7, −23) and (7, 14).
- Fasteners used: 2 × M3×18 button heads (ISO 7380) through pad + cover into the bulkhead (they replace the cover's 2 × M3×10); 1 × 1/4"-20 × 3/8" knurled thumb screw (check the camera's thread depth: the screw may stand ≤ 5 mm above the 4 mm seat)

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Seat angle | 30° nose-down | ±1° | aims the camera |
| 1/4" slot | Ø6.85 printed, ±4 along y | +0.3/−0 | clearance |
| Lip to camera back | 0.3 | ±0.2 | anti-rotation |

Servo and camera dimensions are nominal (tools/hobby_parts.py, claw_frame.py). The MG90S is kept at the SG90 body size the arm was reviewed with; makers list 22.5–22.8 × 12–12.2 mm, so measure your MG90S (body length and width, tab-hole spacing, shaft to near end) and the double-arm horn (hub Ø, arm width near the hub), and give Claude any difference over 0.3 mm. Brio 4K: 27 × 102 × 27 mm, 63 g with its clip removed, 1/4"-20 thread centred on the bottom (Logitech quick-start guide); check the thread depth before choosing the screw.

## 4. Loads
Design loads come from the MG90S datasheet stall torque (≈216 N·mm at 6 V), the stalled servo being the worst case the claw sees: the pinion (pitch radius 9 mm) then pushes **24 N** into the racks, **12 N per jaw** when both jaws touch the object, or the full **24 N on one jaw** when an off-centre object stops one jaw first. Plus the arm cases kept from the arm's strength review: a **5 N sideways push** and a base-yaw stall of up to **12 N** at the fingertip. The end effector now weighs ≈148 g with the camera (claw ≈53 g printed + 2 × MG90S + Brio 63 g + screws), ×3 for arm accelerations; the Brio's USB cable can tug the camera with ≈10 N.

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Camera weight with arm accelerations | 0.62 N × 3 | seat cantilever from the pad | cyclic | hours |
| USB cable tug | 10 N at the camera end | thumb screw + lip, seat root | short-term | seconds |

## 5. Environment
- Max temperature the part will see (°C): 40 (indoor desk; MG90S cases warm under sustained grip)
- Outdoor / UV: no
- Chemicals, oils, moisture: none

## 6. Material
- Preferred or required: PETG (Prusament PETG or equivalent), user left the choice to the designer
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA for the load-path parts (creeps under sustained servo-holding load); ABS/ASA (no enclosure needed for this job)

## 7. Quantity and time
- Quantity: 1
- Max acceptable print time per batch (h): 2

## 8. Acceptance criteria (measurable)
- [ ] Camera sits flat on the seat against the lip
- [ ] Thumb screw reachable from below the seat with the mount fitted
- [ ] **Proof test:** Camera fitted, arm powered: run the arm through its fastest full-range sweep 10 times, then pull the camera's USB cable with 10 N (≈1 kg on a luggage scale) along each axis for 10 s. Pass: no crack at the seat root or the lip, the camera has not turned on the screw, and the screws are still tight.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

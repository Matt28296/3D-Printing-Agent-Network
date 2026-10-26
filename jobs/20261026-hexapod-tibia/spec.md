# Part spec: Tibia (×6)

Job: 20261026-hexapod-tibia · Written by: Architect · Date: 2026-10-26 (round 3: §2–4 and §8 updated by design-lead after strength round 1 and the deep review) · Assembly: [20261026-hexapod-assembly](../20261026-hexapod-assembly/assembly_plan.md)

## 1. Function
7 mm flat plate from the tibia MG90S horn to a rounded foot tip 70 mm away; tapers from a Ø18 hub to a Ø9 foot.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 79 × 18 × 7 mm.
  - Tibia horn: SG90/MG90S arm-horn pocket (2 deep, 5 mm floor) and a Ø2.6 CAD clamp hole.
  - In round 3 the tibia servo is mounted reversed on the femur, so the tibia's back face runs **3.1 mm** off the femur's front face. Keep it flat: nothing may stand proud of it.
- Fasteners used:
  - Tibia horn: **M2 × 12** centre screw (M2 × 10 if the shaft thread bottoms before 6.5 mm) + Ø6 washer, driven **snug, ≈ 0.05 N·m** (strength round 1), plus 1 anti-rotation screw through the horn arm.
  - Optional TPU or rubber sock over the foot.

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Knee → foot tip | 70.0 | ±0.3 | stance height |
| Floor under the horn pocket | 5.0 | ±0.2 | clamp pull-through |

The servo and horn dimensions come from the MG90S's own spec in `tools/hobby_parts.py` (deep review B2, S1); the horn pocket is unchanged by it.

## 4. Loads
Load cases as strength round 1 re-derived them (`strength.md`, "Load cases"); the earlier 0.6 kg and 4 N per foot were 40 % low (deep review SYS-2).

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Robot on a tripod (683 g, lone leg 41.5–43.3 %) | **2.90** up at the foot: mostly along the tibia, plus bending in the walking stance (tucked 18.7°) | foot tip | sustained (SF 4) | minutes |
| Walking (× 2) | **5.80** | foot tip | cyclic (SF 4) | hours |
| Foot scrub | µ 0.5 × 2.90, capped by the knee servo's stall | foot tip, across the tibia | cyclic (SF 4) | hours |
| Knee stall | 216 N·mm | horn pocket bearing | short-term (SF 3) | seconds |
| Sideways shove | 3 at the foot, 70 mm from the knee | out-of-plane bending at the hub, horn clamp | short-term (SF 3) | seconds |
| 20 cm drop | **19.2** per foot (servo back-drive cap), buckling | foot tip | short-term (SF 3) | impact |
| Assembly | M2 clamp screw snug 0.05 N·m ≈ 125 N preload | Ø6 washer on the 5 mm floor | short-term (SF 3) | — |

Round 3's walking stance tucks the tibia 18.7° in, so the foot load now bends the tibia: the knee holds up to 86–98 N·mm at the round-3 mass. The knee servo's stall still caps it at 216 N·mm, the case strength checked. Round-3 mass (812–877 g) raises the walking loads by 19–28 %.

## 5. Environment
- Max temperature (°C): 40 (indoor floor; MG90S cases warm under load)
- Outdoor / UV: no
- Chemicals, oils, moisture: none

## 6. Material
- Preferred or required: PETG (designer's choice; the user left material to the designer)
- On hand (from config/printer.json): PETG assumed; check before slicing
- Excluded: PLA (creep under constant servo-holding load); TPU only as optional foot socks

## 7. Quantity and time
- Quantity: 6, printed **3 per plate** (2 plates); 6 on one plate slices to about 3.9 h, over the limit
- Max acceptable print time per batch (h): 3

## 8. Acceptance criteria (measurable)
- [ ] Foot tips of all six legs touch the ground together in the walking stance (±2 mm)
- [ ] **Proof test (strength round 3):**
  1. **Set-up.** Fit the tibia on its horn on an MG90S clamped in a vice, with the M2 × 12 clamp screw **snug (0.05 N·m)**. Hold the tibia horizontal, with a stop on the far side of the hub so the servo gears do not carry the moment.
  2. **Load.** Hang **1 kg** from the foot tip for **1 min**.
  3. **Shove.** Push **6 N** sideways at the tip, each way, for 10 s (1.5 × the 4.0 N a coxa stall puts on the foot).

  Pass:
  - no cracks or whitening around the pocket or the arm-screw hole;
  - no gap over 0.2 mm (feeler gauge) between the tibia and the horn;
  - after unloading, the tip returns to within 0.5 mm of where it started.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

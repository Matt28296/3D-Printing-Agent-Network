# Part spec: Hexapod bottom body plate

Job: 20261026-hexapod-body-bottom · Written by: Architect · Date: 2026-10-26 (round 3: §1–4 and §8 updated by design-lead after strength round 1 and the deep review) · Assembly: [20261026-hexapod-assembly](../20261026-hexapod-assembly/assembly_plan.md)

## 1. Function
6 mm plate (hull of the six coxa-servo windows, 155 × 139 mm) that the six coxa MG90S hang through, shafts down. Each servo is mounted **reversed** (deep review B1, option 2): lowered in from above, spline first, with its tabs on the plate's top face and its case and lead inside the body. Four 40 mm columns carry the top plate, and two strap slots hold the 2S LiPo that sits on it.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 154.8 × 138.8 × 46.0 mm.
  - Coxa servos: 6 MG90S windows **23.2 × 12.8 CAD** at the mounts in `hex_frame.LEG_MOUNTS` (middle legs at y ±56).
  - Tab screws: 12 **Ø2.4 CAD** clearance holes for M2 machine screws, slotted 0.4 mm outward.
  - Columns: 4 × Ø8 × 40 with r1.5 root fillets and Ø2.8 CAD pilots at **(±36, ±25)** (`hex_frame.COLUMNS`, shared with the top plate).
  - LiPo: strap slots 22 × 3 at y ±20.
  - Leads: six 3.2 × 1.8 tie slots, one beside each window on the side the leads come up (SYS-5).
  - The coxa bracket's back face is **4.1 mm** below the underside.
- Fasteners used:
  - Coxa tabs: 12 × **M2 × 12 pan-head machine screws** from below, each with an M2 washer Ø5 under the head (on the underside) and an M2 washer Ø5 and **M2 nut** on the tab inside the body (strength round 1). The thread runs 1.3 mm past the nut.
  - Top plate: 4 × M3 × 8 self-tapping into the columns.
  - LiPo: 1 velcro strap.

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Plate thickness | 6.0 | ±0.2 | strength (strip outside each window) |
| Coxa servo windows | 23.0 × 12.6 printed (23.2 × 12.8 CAD) | +0.3/−0 | 0.1 end / 0.2 side clearance |
| Tab-screw clearance holes | Ø2.2 printed (Ø2.4 CAD) | +0.2/−0 | M2 clearance |
| Mount positions | per `hex_frame.LEG_MOUNTS` | ±0.3 | leg spacing |
| Column height / positions | 40.0 / (±36, ±25) | ±0.3 | top-plate seat; room for the ESP32 leads above the LiPo |

Servo dimensions are nominal. Since the deep review (B2, S1) the MG90S has its own spec in `tools/hobby_parts.py`:
- body 22.8 × 12.2 mm;
- spline top 14.0 mm above the tab underside;
- case bottom 18.5 mm below it;
- tab holes 27.8 mm apart.

Measure your MG90S (`BUILD_GUIDE.md` §3 step 1). Give Claude any difference over **0.1 mm** in body length or width, or over 0.3 mm elsewhere: the window ends have only 0.1 mm clearance each.

## 4. Loads
Load cases as strength round 1 re-derived them (`strength.md`, "Load cases"); the earlier 0.6 kg and 4 N per foot were 40 % low (deep review SYS-2).

| Case | Force (N) | Point and direction | Static / cyclic / sustained | Duration |
|---|---|---|---|---|
| Robot on a tripod (683 g, lone leg 41.5–43.3 %) | **2.90** up at a foot: the coxa servo's moment, 82 mm × F_up over the 27.8 mm tab spacing, on its two tab screws and the plate strip outside the window | coxa mounts | sustained (SF 4) | minutes |
| Walking (× 2) | **5.80** per foot | coxa mounts; plate mid-span on the tripod | cyclic (SF 4) | hours |
| Foot scrub | µ 0.5 × 2.90, capped by the servos' stall | coxa mounts | cyclic (SF 4) | hours |
| Servo stalls | 216 N·mm per joint; coxa stall straight into the tab screws | tab holes | short-term (SF 3) | seconds |
| Sideways shove | 3 at a foot, with 0–2.90 up | coxa mounts | short-term (SF 3) | seconds |
| 20 cm drop | **19.2** per foot (servo back-drive cap) + ≤ 6.2 inward; body inertia 17.2 g on 6 feet, 8.6 g on 3 | coxa mounts, plate mid-span, columns | short-term (SF 3) | impact |
| Handling | robot lifted by the top plate, × 2 | columns, deck screws | short-term (SF 3) | seconds |

**Reversed mounting (round 3):** the foot's upward force now lifts the coxa servo's tabs off the plate's top face, so the two tab screws carry the vertical load in tension as well as the moment. Strength round 1 checked them sitting on the underside, in bearing. The screw heads bear on the underside through Ø5 washers: 14 mm² against the M2 nut's 8.6 mm² that the check used. Re-check this load path.

Round-3 mass: 812 g (877 g with solid parts) raises every walking and servo load by 19–28 %; the drop is capped by the servos and does not change.

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
- [ ] All six MG90S drop into their windows spline first; the M2 × 12 screws pass the plate and the tab holes; the nuts tighten
- [ ] Top plate screws line up with the columns
- [ ] **Proof test (strength round 1, for the revised plate):**
  1. **Standing load:** stand the assembled robot on **all six feet** (servos powered, neutral stance) and add **500 g** on the top plate for 1 min. Each femur then holds ≈ 87 N·mm. Do not do this on a tripod: the femur servos would stall.
  2. **Drop test:** drop it from **20 cm** onto a carpeted floor 3 times, landing flat on 6 feet. Then drop it 3 more times, tilted so it lands on one side's 3 feet.

  Pass:
  - no cracks or whitening at the coxa windows, especially at the strip outside each window's outer end;
  - no cracks at the nut seats or the column roots;
  - no servo tab lifting off the plate (0.2 mm feeler gauge);
  - the nuts are still tight.

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

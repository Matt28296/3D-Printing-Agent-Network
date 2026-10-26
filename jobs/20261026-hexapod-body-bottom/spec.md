# Part spec: Hexapod bottom body plate

Job: 20261026-hexapod-body-bottom · Written by: Architect · Date: 2026-10-26 (round 3: §1–4 and §8 updated by design-lead after strength round 1 and the deep review; round 4: §1–4 and §8 after strength round 3) · Assembly: [20261026-hexapod-assembly](../20261026-hexapod-assembly/assembly_plan.md)

## 1. Function
6 mm plate (hull of the six coxa-servo windows plus an 8 mm margin, 166 × 147 mm) that the six coxa MG90S hang through, shafts down. Each servo is mounted **reversed** (deep review B1, option 2): lowered in from above, spline first, with its tabs on the plate's top face and its case and lead inside the body. Four Ø10 × 40 mm columns carry the top plate, and two strap slots hold the 2S LiPo that sits on it.

## 2. Envelope and interfaces
- Max size available (mm): MK3 bed 250 × 210 × 210
- Mating parts and their dimensions: 166.1 × 146.8 × 46.0 mm.
  - Coxa servos: 6 MG90S windows **23.2 × 12.8 CAD** at the mounts in `hex_frame.LEG_MOUNTS` (middle legs at y ±56). The strip outside each window's outboard end is **11.3 mm** deep (`MARGIN` 8, strength round 3).
  - Tab screws: 12 **Ø2.4 CAD** clearance holes for M2 machine screws, slotted 0.4 mm outward.
  - Columns: 4 × **Ø10** × 40 with r1.5 root fillets and Ø2.8 CAD pilots at **(±36, ±25)** (`hex_frame.COLUMNS`, shared with the top plate).
  - LiPo: strap slots 22 × 3 at y ±20.
  - Leads: six 3.2 × 1.8 tie slots, one beside each window on the side the leads come up (SYS-5).
  - The coxa bracket's back face is **4.1 mm** below the underside.
- Fasteners used:
  - Coxa tabs: 12 × **M2 × 14 pan-head machine screws** from below, each with an M2 washer Ø5 under the head (on the underside) and an M2 washer Ø5 and an **M2 Nyloc nut** (nylon insert, DIN 985) on the tab inside the body. Drive them **snug, at most 0.045 N·m** (strength round 3: the washer bears on 14.2 mm² of the plate's underside); the Nyloc holds the nut without preload. With the Nyloc modelled 3.0 mm tall the thread runs about 1.9 mm past it (M2 × 12 would stop short of its nylon ring).
  - Top plate: 4 × M3 × 8 self-tapping into the columns.
  - LiPo: 1 velcro strap.

## 3. Critical dimensions and tolerances
| Feature | Nominal (mm) | Tolerance | Fit type |
|---|---|---|---|
| Plate thickness | 6.0 | ±0.2 | strength (strip outside each window) |
| Strip outside each window's outboard end | 11.3 deep (`MARGIN` 8) | +0.3/−0 | strength (drop: the outboard tab screw pulls the strip up) |
| Coxa servo windows | 23.0 × 12.6 printed (23.2 × 12.8 CAD) | +0.3/−0 | 0.1 end / 0.2 side clearance |
| Tab-screw clearance holes | Ø2.2 printed (Ø2.4 CAD) | +0.2/−0 | M2 clearance |
| Mount positions | per `hex_frame.LEG_MOUNTS` | ±0.3 | leg spacing |
| Column diameter / height / positions | Ø10 / 40.0 / (±36, ±25) | ±0.3 | strength (handling); top-plate seat; room for the ESP32 leads above the LiPo |

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

Round 4: strength round 3 re-checked the reversed mount (rows 1–19) and itemised the robot at 840 g. Its change set (`MARGIN` 8, snug tab screws with Nyloc nuts, Ø10 columns, with the coxa's 100 % infill) was checked at **906 g**: lowest SF 3.22 (tab-screw washer bearing at 0.045 N·m); the strip in the drop 3.37.

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
- [ ] All six MG90S drop into their windows spline first; the M2 × 14 screws pass the plate and the tab holes; the thread comes through each Nyloc's nylon ring
- [ ] Top plate screws line up with the columns
- [ ] **Proof test (strength round 3, for the round-4 plate):**
  1. **Standing load:** stand the assembled robot on **all six feet** (servos powered, neutral stance) and add **500 g** on the top plate for 1 min. Each femur then holds ≈ 87 N·mm. Do not do this on a tripod: the femur servos would stall. It is harmless, but it loads the strip only to about 0.3 × walking, so it doesn't prove the strip.
  2. **Handling (new):** lift the robot by the deck and turn it on its side (deck vertical). Hold **1 min** with **0.8 kg** hung from the bottom plate's lower edge: about 2 × the static load on the columns.
  3. **Drop:** 3 × 20 cm landing flat on 6 feet, then 3 × 20 cm tilted onto one side's 3 feet, onto carpet. This is the strip's governing case (51 N uplift per mount).
     - Run it on **spare coxa servos**, or only after the leg test in the assembly spec §8 has passed (DR05 SYS-6).
     - Mark each nut with paint first.

  Pass:
  - no cracks or whitening at the coxa windows, especially the strip at each outboard screw and the window corners;
  - none at the column roots;
  - no servo tab lifting off the plate (0.2 mm feeler gauge);
  - no nut turned (paint marks).

## 9. Notes and open questions
None open. Shared frames, joint ranges and clearances: see the assembly plan and `assembly_check.json`.

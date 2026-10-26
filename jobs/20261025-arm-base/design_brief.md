# Design brief: Robot arm base

Job: 20261025-arm-base · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~70 °C (material-selection skill) still 30 °C above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Upside down: top plate on the bed. All wall openings have 45° roofs pointing at the desk side (up in print). Top plate in-plane loads run along the layers.

## Concept
Open-bottom box (110 × 104 × 40 mm) that holds the base-yaw MG996R (hanging through its top plate), the turntable support ring, the ESP32 cradle, the 5.5 × 2.1 mm DC panel jack and the USB access slot. Screws to the desk or sits on rubber feet.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Servo window | 41.1 × 20.1 | +0.3/−0 | clearance 0.2/side | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Lead notches (round 3) | 4.4 wide, 2.0 beyond each case end (printed), through the plate and that end's pad | +0.2/−0 | 4 × 1.3 mm lead ribbon; ≥ 1.8 CAD (≈ 2.0 printed) to the nearest pilot | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules; notch size from deep review 01 B1 (`MG996R.lead_notch_w/reach`) |
| Top plate at the far / near servo tab (round 5) | 7.5 / 5.5 (pads; 4.0 elsewhere) | +0.3/−0 | strength: plate round the tension screw's boss | none (heights) | links strength round 4 FIX rows (`strength_calc.py`) |
| Servo pilot holes | Ø2.6 | ±0.1 | self-tap M3/servo screw | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Servo pilot pattern | 48.5 × 10.0 | ±0.2 | matches MG996R tabs | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Cradle pilots (round 5) | Ø2.6, 7 deep from the boss end (1 mm into the plate) | ±0.1 / +0.5/−0 | M3 × 10 through the 4 mm cradle clamp: 1 mm short of the bottom | HOLE_COMP +0.2 on holes/pockets | deep review 01 N7, DFM round 4 note 1 |
| DC jack hole | Ø11.4 | +0.3/−0 | panel jack Ø11 thread | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Overall | 110 × 104 × 40 | ±0.5 | free | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: servo windows +0.4 total (SG90 window ends +0.2), horn pockets +0.5 total, M3 clearance Ø3.4, M2 clearance Ø2.4, self-tap pilots Ø2.6 (MG996R tab screws) and Ø1.5 (SG90 tab screws). Every hole and pocket also gets **HOLE_COMP = +0.2 mm** in CAD (fdm-design-rules default; no library row yet), applied in tools/hobby_parts.py cutters and each model.py. Horn joints: the horn's centre screw is replaced by a longer one + washer through the link, clamping link and horn onto the spline (strength round 1).

## Parameters exposed by model.py
HOLE_COMP, SERVO_CLR, BED_CHAMFER, BX, BY, H, WALL, PLATE_T, CORNER_R, PILLAR_D, PILLAR_HOLE, SERVO_BOSS_D, SERVO_BOSS_L, RING_PILOT_R, RING_PILOT_ANG, CRADLE_PILOTS, CRADLE_BOSS_D, CRADLE_BOSS_L, CRADLE_PILOT_DEPTH, PILOT, SERVO_XM, TAB_X_FAR, TAB_X_NEAR, PAD_T_FAR, PAD_T_NEAR, PAD_FAR, PAD_NEAR, USB_SLOT, USB_Y, USB_Z, JACK_D, JACK_Y, JACK_Z, CABLE_SLOT

## Risks
- Wall openings printed as overhangs → 45° roofs / teardrop pointing up in print
- Self-tapping pilots crack the plate → servo screw bosses lengthen the grip to 10 mm; PETG is tough
- The overturning moment bends the 4 mm plate round the tension-side tab screw (links strength round 4, SF 1.21) → 7.5 / 5.5 mm pads round the tabs (round 5)
- The pads crowd the ESP32 and its cradle → the near pad stops 2 mm short of the module's can and 4.5 mm above the cradle frame; `cad_checks.py` probes the board's whole envelope

## Round 3 (2026-10-26: deep reviews 01 B1/S3, 03 SYS-05/SYS-09/SYS-12)
- **Lead notches (B1).** The MG996R goes in from above, case bottom first, and its lead root crosses the 4 mm top plate: `servo_mount_cutter(lead="notch")` cuts a 4.4 × 2.0 mm (printed) notch at each case end (the MG996R's lead end is unverified), clipped to the top plate only. Below the plate the ribbon passes between the Ø6.5 bosses, which stand ≥ 3 mm off the centreline at the case end. Printed ligament from a notch to the nearest Ø2.6 pilot: 2.05 mm (the cutter's check); window end to pilot 2.4 mm. A vertical cut through the bed layer: no overhang.
- **Tab screws (S3):** 4 × M3 × 12 pan-head self-tapping + Ø7 washers, grommets and eyelets left out: 9 mm engaged in the 10 mm plate + boss.
- **Turntable on a disc horn, ring 0.4 mm under it (SYS-05):** the base now sees the arm's overturning moment through the ring and its 3 screws as well as through the servo tabs (spec §4: 692–832 N·mm arm straight out with the camera).
- **Build order (SYS-09):** built and wired upside down on the bench, screwed down last; the extension junctions sit outside the cable slot.
- **Stability (SYS-12):** with the round-3 claw and camera the robot is ≈0.70 kg; free-standing it tips with the arm out (SF 0.34–0.48), so the desk screws stay required, or a 200 × 200 × 0.4 kg board (SF ≥ 2.2) or 1.2 kg of ballast (SF 1.5).
- measure_holes: 10 × Ø2.8 (4 servo, 3 ring, 3 cradle pilots), 4 × Ø3.6 desk holes, the Ø11.6 jack teardrop.

## Round 5 (2026-10-26: links strength round 4, SF 1.21; DFM round 4 notes 1–3). Third design attempt
- **What failed.** The 4 mm top plate round the MG996R's tension-side tab boss, under the overturning moment carried by the servo path (ring ignored): yaw stall 1.21, weight ×2 1.87, hand push 1.60, shoulder stall on the desk 1.49, 20 N on the rim 1.74 (`strength.md` rows 4–16).
- **Change: two pads under the top plate** (`PAD_FAR`, `PAD_NEAR`), as the analyst's FIX rows asked. Nothing else in the base moves.
  - **Far tab** (x −34.4, 65 % of the moment): 7.5 mm (`PAD_T_FAR`). The pad runs from the −X wall to x −19.4 and covers |y| ≤ 20.5, at least 15 mm round both bosses. It stays 1.85 mm clear of the 150° ring pilot and 11.5 mm clear of the cable slot.
  - **Near tab** (x 14.1, 35 %): 5.5 mm (`PAD_T_NEAR`), x −0.9 … 29.1, y −20 … 18.
    - Towards the ESP32 (+y) the pad stops at y 18, 2 mm short of the module's can (y ≥ 20).
    - Its underside (Z −5.5) stands 4.5 mm above the cradle frame (Z −10) and 0.5 mm above the board's whole 4 mm parts envelope (PCB top Z −10). The only parts under the pad are the pin-row solder joints, about 3 mm below it.
  - **What still passes through:** the window, both lead notches and the four tab pilots go through plate + pad + boss (Z 0 … −10), so the lead's root passes as before.
    - The notches are now cut to the bosses' depth. Below the pads the notch footprint is open air, so this only removes the 0.01 mm sliver where the notch's outer corners graze the Ø6.5 bosses (round 4's four 0.01 mm "bridges"). mesh_check now reports none.
  - **Tab screws:** unchanged, M3 × 12 + Ø7 washer, 9 mm engaged in the 10 mm pilot. The pad takes the place of part of the boss.
- **Verification.** The analyst's own plate check (Roark circular plate, supported at a 14.85, load over the Ø6.5 boss, 65 / 35 % split), run in `strength_calc.py` on the round-5 masses (yaw-stall moment 2605 N·mm on the servo path). Kt 2.5 means fully sharp notch and window corners, the analyst's sensitivity; Kt 2.0 is their verdict value.

  | Case (required SF) | Far tab, 7.5 mm, Kt 2.5 | Near tab, 5.5 mm, Kt 2.5 | At Kt 2.0 | 4 mm plate (round 4, Kt 2.0) |
  |---|---|---|---|---|
  | Yaw stall (3) | **3.39** | **3.38** | 4.23 | 1.20 |
  | Hand push 5 N (3) | 4.51 | 4.50 | 5.62 | 1.60 |
  | Shoulder stall on the desk (3) | 4.18 | 4.17 | 5.21 | 1.48 |
  | 20 N on the rim (3) | 4.87 | 4.86 | 6.08 | 1.73 |
  | Weight ×2, sustained (4) | 5.18 | 5.18 | 6.47 | 1.84 |

  - **Step at the pad edge.** The pad's edge lies 15 mm from the boss (13 mm towards the ESP32). There the plate's tangential moment is about 27 % of its peak, which gives about half the boss-edge stress in the 4 mm plate. That is SF ≈ 8 with Kt 2 at the step.
  - **Other base rows are unchanged.** The lowest of them is the ring path under the yaw stall, 3.63.
- **Cradle pilots (deep review 01 N7, DFM note 1).**
  - `CRADLE_PILOT_DEPTH` 7: the pilots run from the boss end (Z −10) 1 mm into the plate (Z −3).
  - The M3 × 10 through the cradle's 4 mm clamp now ends 1 mm short of the bottom, and 3 mm of plate stays above.
  - The three cradle bosses lie outside both pads.
- **Notch tolerance (DFM note 3)** is now a row in the critical-dimension table.
- **Checks:** `cad_checks.py` (19 checks, exit 0) covers:
  - the pads' thickness and extent;
  - the notches through plate and pad, and the notch → pilot strip, 1.835 CAD at worst;
  - the pilots through 10 mm, and the cradle pilots' depth;
  - the ESP32 envelope (343 probes, all clear), the cradle bosses, the USB slot, the cable slot, the ring pilots and the jack.
  `assembly_check.py`: no collisions in any named pose. It includes the base against the cradle and the ESP32.
- **Mass.** +4.84 cm³: 94.5 cm³, 120 g solid (was 114). Print time about +10 min (last slice 8.1 h of the 10 h limit).

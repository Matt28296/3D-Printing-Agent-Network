# Design brief: Forearm (elbow → wrist, 90 mm)

Job: 20261025-arm-forearm · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~70 °C (material-selection skill) still 30 °C above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, FRONT face on the bed (horn pocket and, since round 5, the back-face ribs open upward: no bridge, no support). Bending along the layers.

## Concept
Flat 10 mm plate on the elbow servo's double-arm horn, carrying the wrist MG90S at 90 mm (round 3). Since round 5 the window rails carry 6 mm back-face ribs, joined by a cross-rib at the window's far end that gives the far tab screw a 16 mm pilot.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Elbow–wrist axis distance | 90.0 | ±0.3 | kinematics | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| MG90S window | 23.0 × 12.6 printed (23.2 × 12.8 CAD) | +0.3/−0 | 0.4 side / 0.2 end clearance on the 22.8 × 12.2 body | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules; body from deep review 01 S1 |
| Lead notch | 4.2 wide, 1.5 beyond the case end (printed) | +0.2/−0 | 3.6 × 1.2 mm lead ribbon | HOLE_COMP +0.2 on holes/pockets | deep review 01 B1 (`MG90S.lead_notch_w/reach`) |
| Screw strips (pilot → window / notch) | lead end 1.34, far end 1.45 CAD (≈ 1.55 / 1.65 printed) | as built | M2 self-tappers driven snug; under the 1.8 mm rule, **kept by the user's decision of 26 Oct 2026**, first-print screw-strip check in spec §8 | HOLE_COMP +0.2 on holes/pockets | user decision; strength round 4 strip table (SF ≥ 4.75) |
| Far tab pilot (round 5) | Ø1.5 printed, **round** (Ø1.7 CAD, no slot since round 6), x 70.6, 16 deep (10 plate + 6 cross-rib) | ≥ 14 deep | M2 × 16, 13.5 mm engaged, full thread circle | HOLE_COMP +0.2 on holes/pockets | links strength round 4 FIX (≥ 14 deep); round: links strength round 5 FIX |
| Lead-end tab pilot (round 6) | Ø1.5 printed, **round** (Ø1.7 CAD, no slot), x 99.7 (moved 1.3 mm out, round 3), 10 deep; 3.45 CAD to the plate end | as built | M2 × 12, 9.5 mm engaged, full thread circle | HOLE_COMP +0.2 on holes/pockets | links strength round 5 FIX |
| Rail ribs + cross-rib (round 5) | 6 deep on the back face; ribs as wide as the rails (6.6), x 66.9–101.1; cross-rib full width x 66.9–72.9; 45° run-out to x 60.9 | +0.3/−0 | strength: rails 6.6 × 16 | none | links strength round 4 FIX (6 mm; 4 mm gives 3.30) |

The round-2 SG90 rows (window 22.7 × 12.4, pilot-to-window wall 1.8 printed) no longer apply: the wrist servo is the MG90S since round 3.

Printed targets: servo windows +0.4 total (SG90 window ends +0.2), horn pockets +0.5 total, M3 clearance Ø3.4, M2 clearance Ø2.4, self-tap pilots Ø2.6 (MG996R tab screws) and Ø1.5 (SG90 tab screws). Every hole and pocket also gets **HOLE_COMP = +0.2 mm** in CAD (fdm-design-rules default; no library row yet), applied in tools/hobby_parts.py cutters and each model.py. Horn joints: the horn's centre screw is replaced by a longer one + washer through the link, clamping link and horn onto the spline (strength round 1).

## Parameters exposed by model.py
HORN_SERVO, WRIST, HOLE_COMP, L, T, HALF_W, X0, X1, CORNER_R, CLR, END_CLR, BED_CHAMFER, WIN_HW, WIN_X0, WIN_X1, FAR_PILOT_X, PILOT_SHIFT, LEAD_PILOT_X, PILOT_D, RIB_H, RIB_PAST, RIB_X1, BOSS_X0, FAR_SCREW_L, TAPER

## Risks
- SG90 pilot-to-window wall 1.55 mm (DFM round 1) → Ø1.5 printed pilot + 0.2 end clearance → 1.8 mm printed (round 2; superseded by the MG90S strips, kept by the user's decision with a first-print check)
- Sideways loads (strength round 1) → T 5→10, slot removed, centre-screw clamp
- Wrist tab screws pull out (strength round 2) → M2×12 self-tapping, 9.5 mm engaged; round 5: M2 × 16 at the far tab, 13.5 mm engaged in the cross-rib; round 6: both pilots round, so the whole thread circle engages
- The window rails carry the wrist servo's sideways moment past the window, because each MG90S tab screw acts as a pin (links strength round 4, SF 1.71) → 6 mm back-face ribs (round 5)
- Back-face ribs could meet the upper link, the elbow servo and its horn, or the screw heads on the upper link's front face when the elbow folds → they start 61 mm out from the elbow axis; measured clearance ≥ 10.2 mm over the elbow's −150…+30°

## Round 3 (2026-10-26: deep reviews 01 B1/B2/S1/S2/S4, 03 SYS-03/SYS-04/SYS-18)
- **The wrist servo is the MG90S (SYS-18, B2, S1):** its own spec, 22.8 × 12.2 body, case bottom 18.5 below the tabs, spline top 14.0 above them. Window 23.2 × 12.8 CAD (23.0 × 12.6 printed: 0.4 side, 0.2 end clearance).
- **Lead notch (B1, option 1):** `lead="notch_shift_pilot"`: a 4.2 × 1.5 mm (printed) notch at the shaft end (+x) and that end's pilot moved 1.3 mm out, to x 99.7. The builder files that tab's slit to 2.1 mm. Printed ligaments: notch → moved pilot 1.55 mm, far pilot → window 1.65 mm (set by the MG90S's 27.8 mm hole spacing on a 22.8 mm body), moved pilot → window 2.95 mm; the moved pilot's slot ends 3.0 mm from the plate end (X1 104). The two small ones (1.34 / 1.45 mm CAD) are under fdm-design-rules' 1.8 mm "4 perimeters" for structural walls. **The user decided on 26 Oct 2026 to keep them**, with the first-print screw-strip check in spec §8 (drive both tab screws snug, look for whitening or cracks; if either strip fails, the pilots move out, lead end 1.6 mm, far end 0.2 mm, and the forearm is reprinted). The links strength round 4 checked both strips at their real widths: lowest SF 4.75 (lead end) and 5.19 (far end), tear-out under the yaw stall.
- **Fasteners:** elbow clamp M3 × 14 + Ø9 × 0.8 washer (4.6 mm into the spline, S2); 2 × M2 × 6 through the horn arms (S4).
- **Fitting pose (SYS-03):** at the elbow servo's centre the forearm goes on 60° below the upper link's line, towards +X: the elbow's window is −150 … +30°, all of it free of self-collision (`assembly_check.json` elbow_window_deg).
- **Loads (SYS-04):** 161 N·mm (188 with 50 g) across the elbow shaft and 108 / 124 N·mm across the wrist shaft in every pose, from the camera and the round-3 claw (spec §4).
- measure_holes: Ø3.6 clamp hole (the MG90S pilots are slots; since round 6 they are round and measure Ø1.7).

## Round 5 (2026-10-26: links strength round 4, SF 1.71 rails and 2.40 far tab screw; DFM round 4). Third design attempt
- **What failed.**
  - The two 6.6 × 10 window rails at the window's far end, under the yaw stall: SF 1.71. Each MG90S tab has one screw on the centre line, so a tab row is a pin, and the rails carry 0.92 of the far-row moment.
  - The far tab screw's pull-out: M2 × 12, 9.5 mm engaged, SF 2.40.
- **Change 1: 6 mm ribs on both rails, on the back face** (`back_ribs()`).
  - **Width:** as wide as the rails (6.6), the inner faces continuing the window walls.
  - **Length:** from x 66.9 to 101.1, that is 6 mm before the window and 5 mm past its lead end.
  - **Lead end:** the ribs stop at x 101.1, before the r 7 corner would thin them to a sliver. Between them the lead end stays open: the MG90S lead leaves the case end on the centre line, 3.4 mm below the back face.
- **Change 2: a cross-rib under the far pilot.** It joins the two ribs at the window's far end, x 66.9 … 72.9, full width, 6 deep, flush with the window (`BOSS_X0`).
  - The far pilot (Ø1.7 CAD, still slotted 0.4 outward) now runs 16 mm deep: 10 plate + 6 cross-rib.
  - It takes an **M2 × 16** with 13.5 mm engaged (the strength FIX asked for ≥ 14 mm of pilot). The tip stops 2.5 mm short of the back.
  - The wall beyond the slot is 2.45 mm.
  - The lead-end screw stays M2 × 12: the strength review says no boss there, because the lead leaves the case end there.
  - The cross-rib and ribs run out at 45° towards the elbow (back face at x 60.9), so the plate has no step where its moment is largest.
- **The screw strips stay as the user decided** (1.340 / 1.445 mm CAD, measured by `cad_checks.py`). The far strip is now 16 mm deep instead of 10, which lowers its splitting stress for the longer screw.
- **Verification.** The analyst's `strength_calc.py`, re-run on the round-5 masses:

  | Check | Round 4 | Round 5 |
  |---|---|---|
  | Rails, yaw stall | 1.71 | **4.29** |
  | Rails, hand push | 3.03 | 7.68 |
  | Rails, weight ×2 (sustained) | 6.08 | 15.05 |
  | Far tab screw pull-out, yaw stall | 2.40 (M2 × 12) | **3.41** (M2 × 16, 13.5 engaged) |
  | Far tab screw pull-out, weight ×2 | 8.29 | 11.77 |

  - The forearm's lowest rows are then rows this round doesn't touch: the lead-end tab screw M2 × 12, 3.15 (yaw); x 15 over the horn pocket, 3.36; plate torsion, 4.82.
  - **Rib start.** Where the 45° run-out meets the plate (x 60.9), the moment is about 0.78 of that at x 30 (SF 8.47 there), so the plate stays above SF 4 even with Kt 2.5 at the run-out's foot.
- **Clearance.** The ribs and cross-rib sit at least 61 mm from the elbow axis on the forearm's back face, which faces the upper link. Measured with meshes over the elbow's −150…+30° in 5° steps, against:
  - the upper link (with its ribs);
  - the elbow MG996R with its double-arm horn;
  - the screw heads on the upper link's front face (the shoulder clamp's M3 × 14 head on its Ø9 washer, and the four elbow tab pan heads on Ø7 washers).

  Result: **≥ 10.2 mm**, closest at −150°. `assembly_check.py`: the elbow window is still −150…+30, the wrist ±90, and every named pose is free of collisions.
- **Brief (DFM round 4).** The strip justification now records the user's decision, not hobby_parts' 1.5 mm cutter default. The critical-dimension table carries the MG90S rows with spec §3's tolerances (note 2).
- **Checks:** `cad_checks.py` (16 checks, exit 0) covers:
  - size 129 × 26 × 16, the window, the notch and both strips;
  - the moved lead-end pilot, and the far pilot open through 16 mm;
  - the cross-rib (extent and the 2.45 wall), the ribs (depth, 6.60 wide, end at 101.1), the open lead end and the run-out.
- **Mass.** +3.60 cm³: 32.8 cm³, 42 g solid (was 37).

## Round 6 (2026-10-26: links strength round 5, MG90S tab screw pull-out 2.42 / 2.62). Fourth design attempt, user-approved fix
- **What failed.** `servo_mount_cutter` slots every micro-servo pilot 0.4 mm outward, so the printed pilot reached 1.15 mm from the screw axis against the M2 thread's 1.0: only 0.77 of the thread circle engaged. Yaw-stall pull-out: lead-end M2 × 12 **2.42**, far M2 × 16 **2.62** (round 5's 3.15 / 3.41 had assumed round pilots).
- **Change: both MG90S tab pilots round, Ø1.7 CAD** (`PILOT_D` = 1.5 printed + HOLE_COMP), exactly as the analyst's required change 1.
  - **Positions unchanged:** far pilot x 70.6 (`FAR_PILOT_X`), into the M2 × 16 cross-rib; lead-end pilot x 99.7 (`LEAD_PILOT_X`, moved 1.3 mm out, `PILOT_SHIFT`).
  - **How:** `wrist_cutter()` takes `servo_mount_cutter`'s window and lead notch, masks out its two slotted pilots and cuts round ones through the full 16 mm. `tools/hobby_parts.py` is unchanged.
  - **Analyst's what-if:** yaw-stall pull-out far M2 × 16 **3.41**, lead-end M2 × 12 **3.15**.
- **The user-accepted strips do not get smaller** (the slots ran away from them). Measured by `cad_checks.py`: lead end (notch → moved pilot) **1.340**, far end (far pilot → window) **1.445** in the plate and **1.445** in the cross-rib, as in round 5.
- **What grows.** The cross-rib wall beyond the far pilot: 2.45 → **2.85** (x 66.9–69.75). The plate end past the lead-end pilot: 3.05 → **3.45** CAD.
- **Printing.** Vertical holes, front face on the bed: mesh_check 0.0 % overhang, no bridges, no thin walls, bed contact 2875 mm².
- **Spec §8 (2).** The analyst's required change 2 (17 N at 83 mm, bar at 60°) is a spec change, not CAD; it is not made here.
- **Checks.** `cad_checks.py` (17 checks, exit 0): both pilots measure Ø1.7 round at x 70.6 / 99.7 (`measure_holes`), solid from each pilot's edge outward (no slot), the lead-end pilot 3.45 from the plate end, the far pilot open through 16 mm, the 2.85 cross-rib wall, and the strips as above.
- **Mass.** +0.02 cm³: 32.85 cm³.

# Design brief: Turntable support ring

Job: 20261025-arm-turntable-ring · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~70 °C (material-selection skill) still 30 °C above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, tabs on the bed. Compression in the wall runs across layers but in pure compression (layer bonding not loaded in tension).

## Concept
Ring (r 41–44, 16.1 mm tall since round 3) screwed to the base top plate under the turntable. A 0.4 mm running gap with PTFE tape (round 3; was 1.5) lets it share the arm's overturning moment with the base servo's output bearings.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Ring height | 16.1 | ±0.15 | 0.4 mm running gap to the turntable (≈ 0.3 with one layer of PTFE tape); sand the top to an even gap | none (a height: 0.2 mm layers end it at 16.0 or 16.2, inside the tolerance) | deep review 03 SYS-05: `TURNTABLE_Z` 16.5 − `RUN_GAP` 0.4 |
| Tab holes | Ø3.4 at r47.5 | ±0.2 | M3 clearance | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Washer relief (round 5) | Ø8 round each tab screw, from the tab's top up: wall 2.5 (r 41–43.5) over 3.7 mm there | +0.2/−0 | 0.5 mm clear of a Ø7 × 0.5 washer centred on the screw | none (clearance in CAD) | links strength round 4 FIX (Ø7 washer); clearance default from fdm-design-rules (free running ≥ 0.5) |

Printed targets: servo windows +0.4 total (SG90 window ends +0.2), horn pockets +0.5 total, M3 clearance Ø3.4, M2 clearance Ø2.4, self-tap pilots Ø2.6 (MG996R tab screws) and Ø1.5 (SG90 tab screws). Every hole and pocket also gets **HOLE_COMP = +0.2 mm** in CAD (fdm-design-rules default; no library row yet), applied in tools/hobby_parts.py cutters and each model.py. Horn joints: the horn's centre screw is replaced by a longer one + washer through the link, clamping link and horn onto the spline (strength round 1).

## Parameters exposed by model.py
HOLE_COMP, R_IN, R_OUT, TURNTABLE_Z, RUN_GAP, H, TAB_R, TAB_ANG, TAB_D, TAB_T, TAB_HOLE, WASHER_D, WASHER_CLR

## Risks
- Ring rubs the turntable, or leaves it unsupported → 0.4 mm running gap with one layer of PTFE tape on the top face (≈ 0.3 left). The gap depends on the base servo's disc-horn face height (16.5 mm above the top plate, nominal), so measure it before printing (spec §3). At assembly, sand the top where it rubs and add tape where it's loose (BUILD_GUIDE §4 step 4)
- The tab screws' pan heads creep into the 3 mm tabs and the clamp relaxes (links strength round 4, SF 2.26 sustained) → a Ø7 × 0.5 washer under each head (round 5), with a relief in the wall so it sits flat
- Only 2.5 mm of thread in the base's 4 mm plate (with the washer) → drive the three M3 × 6 snug, no harder; a longer screw would reach the ESP32 under the plate

## Round 3 (2026-10-26: deep review 03 SYS-05)
- **Running gap 1.5 → 0.4 mm** (H 15.0 → 16.1), with one layer of PTFE tape on the top face (≈0.3 mm left). The ring now works as a bearing: it catches the disk after 0.5° of tilt (was 1.95°, a 9.3 mm drop at full reach) and shares the arm's overturning moment (up to ≈19 N on its top at r 44, spec §4). Friction with PTFE ≈85 N·mm against the yaw servo's 1000 N·mm.
- **Fit:** sand the top to an even gap (feeler gauge at 8 points), because the servo shaft and the ring now share the load; a second layer of tape where the gap is big. The gap depends on the MG996R's horn-face height (16.5 mm above the top plate, nominal): measure it.
- This changes the ring's CAD (height), so the job reopens for DFM and strength.

## Round 5 (2026-10-26: links strength round 4, SF 2.26 against 4; DFM round 4 fix 1)
- **What failed (strength).** The M3 × 6 pan head (Ø5.5) bearing on the 3 mm tab at the 150 N snug preload. This is a sustained load, so the tab creeps and the screw works loose. Every load row passes, the lowest at 9.22.
- **Change: a Ø7 × 0.5 washer under each of the three pan heads** (BUILD_GUIDE §1, §4 step 1).
  - With the washer the analyst's row gives SF **4.72** (`strength_calc.py` FIX row, re-run on the round-5 geometry).
  - Their thread-in-the-base advisory row (2.5 mm engaged, about 130 N on the placeholder shear) is why the guide says "snug, no harder".
- **Fit, the one CAD change.** A Ø7 washer centred on the screw (r 47.5) reaches r 44.0, the wall's outer face, so it couldn't sit flat.
  - A vertical Ø8 relief round each screw, from the tab's top face up through the wall, leaves 0.5 mm all round the washer.
  - The wall there is 2.5 mm (r 41–43.5) over a 3.7 mm length; elsewhere it is 3.0. DFM's 1.8 mm minimum still holds.
  - The relief is a vertical cut: no overhang. mesh_check's 0.33 % is still only the bottom chamfer's 44–45° facets.
  - Volume −49 mm³ (13.28 cm³, 17 g solid).
  - Effect on the analyst's ring rows: the wall's bending and bearing scale at worst with 2.5 / 3, so the lowest load row, edgewise bending under the yaw stall, goes from 9.21 to ≥ 7.7 if its 32 mm segment lands on a relief.
- **Brief (DFM round 4 fix 1).** The critical-dimension table and the Risks line now carry the round-3 ring: 16.1 ± 0.15 mm with a 0.4 mm gap, as spec §3 and model.py have it.
- **Checks:** `cad_checks.py` (6 checks, exit 0) covers:
  - the height 16.1, matching the turntable's underside 16.5 − 0.4;
  - the 3.0 mm wall;
  - the tab holes matching the base's pilots;
  - at each tab, the washer seat flat on the tab and the washer's edge ≥ 0.5 mm clear of the wall, with the wall 2.50 there.

# Design brief: Turntable with shoulder upright

Job: 20261025-arm-turntable · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~70 °C (material-selection skill) still 30 °C above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Disk on the bed, upright vertical. All upright bending, in-plane and out of plane, puts stress across the layers (Z); the 7 mm upright, the 3 mm root wedges and the gussets (90 mm since round 5) size for that with the across-layer allowable. Disk bending runs along the layers.

## Concept
Ø96 × 8 mm disk whose flat underside sits on the base servo's Ø25 disc horn (round 3; no pocket, so no bridge), with a 66 × 7 mm upright, root wedges and two gussets (90 mm, cut off level with the upright's top: round 5) that hold the shoulder MG996R horizontally (shaft +Y, axis at X 10.15, Z 60.5). Four M2 × 8 self-tappers through the disc horn's own holes stop it turning (round 5).

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Clamp hole | Ø3.4 | +0.2/−0 | M3 clearance | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Shoulder window | 41.1 × 20.1 | +0.3/−0 | clearance 0.2/side | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Shoulder axis | X 10.15, Z 60.5 (assembly frame) | ±0.3 | position | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Lead notches (round 3) | 4.4 wide, 2.0 beyond each case end (printed), 45° top | +0.2/−0 | 4 × 1.3 mm lead ribbon; 1.775 CAD (≈ 1.97 printed) diagonal to the lower pilots | HOLE_COMP +0.2 on holes/pockets | deep review 01 B1; DFM round 4 #7 |
| Disk underside | Z 16.5 | ±0.2 | 0.4 mm over the support ring | none | spec §3; `horn_face_z(MG996R)` |
| Gussets (round 5) | 4 thick at \|X\| 28.5–32.5; 23 deep at the disk, GUSSET_H 90, cut off at Z 97.3 (4.4 deep there) | ±0.3 | strength: upright window region | none | links strength round 4 FIX |
| Disc-horn anti-rotation zone (round 5) | disk solid r 4–13 to 6 mm above its underside (6 mm of bottom solid layers) | min | 4 × M2 × 8 pilots drilled 6 deep through the disc's holes | none | links strength round 4 FIX; DFM round 4 note 4 |

Printed targets: servo windows +0.4 total (SG90 window ends +0.2), horn pockets +0.5 total, M3 clearance Ø3.4, M2 clearance Ø2.4, self-tap pilots Ø2.6 (MG996R tab screws) and Ø1.5 (SG90 tab screws). Every hole and pocket also gets **HOLE_COMP = +0.2 mm** in CAD (fdm-design-rules default; no library row yet), applied in tools/hobby_parts.py cutters and each model.py. Horn joints: the horn's centre screw is replaced by a longer one + washer through the link, clamping link and horn onto the spline (strength round 1).

## Parameters exposed by model.py
SERVO, HOLE_COMP, Z0, DISK_R, DISK_T, CLR, UP_T, UP_W, UP_Y, XS, ZS, WIN_HALF_H, ROOF_H, UP_TOP, GUSSET_T, GUSSET_X, GUSSET_LEN, GUSSET_H, ANTI_ROT_N, ANTI_ROT_L, DISC_HOLE_R_MIN, ANTI_ROT_PILOT_D, ANTI_ROT_PILOT_DEPTH, ANTI_ROT_ZONE, ROOT_FILLET, WASHER_CLEAR_X, BED_CHAMFER

## Risks
- Window roof cutting tab pilots (found in design, fixed by turning the servo horizontal; hobby_parts now refuses such roofs)
- Horn-slot ceiling bridge 10.6 mm (DFM round 1) → no pocket: horn flat on the bed face, clamped by the centre screw
- Upright root across layers → UP_T 7, root wedges, gussets with toes inside the disk (70 mm; 90 mm since round 5 for the window region)
- The disc horn's hole circle isn't known (no measurement, no datasheet) → the anti-rotation pilots are drilled through the horn's own holes at assembly, and the disk is solid wherever they can land (round 5)
- Self-tappers in infill hold poorly → `print_requirements.json` makes the bottom 6 mm of the disk solid (round 5)
- Horizontal pilots → teardrops pointing up
- Clamp washer on the root wedge (round 2) → front wedge stops at |X| ≥ 6

## Round 3 (2026-10-26: deep reviews 01 B1/S2/S3/S4, 03 SYS-04/SYS-05/SYS-09/SYS-16)
- **Disc horn (SYS-05).** The base servo's round Ø25 disc horn replaces the double-arm horn under the disk: it supports the disk ±12.5 mm in every direction instead of on the Ø11 hub across the arms. The disk's underside is flat, so the CAD doesn't change; the 2 anti-rotation screws (M2 × 6, S4) go through two of the disc's holes. Clamp: M3 × 14 socket head (ISO 4762, SYS-16: re-tightened with an L-key past the upright) + Ø9 × 0.8 washer, 4.6 mm into the spline (S2).
- **Lead notches (B1).** The shoulder MG996R goes in from the front (+Y) face, case bottom first; `lead="notch"` cuts a 4.4 × 2.0 mm (printed) notch at both case ends. The notch is a hole in a standing wall, so `_notch_tops()` adds a right triangle over each one: its ceiling rises at 45° from the notch's end wall to the window (the hexapod coxa's DFM round 3 failed a flat notch top). Ligaments (corrected in round 5, DFM round 4 note 1): the cutter's own check gives 2.05 mm printed notch → pilot, but it treats the pilot as a plain circle; the lower pilots' teardrop points aim at the notch, so the true minimum is 1.775 mm CAD (≈ 1.97 printed), a diagonal across about 4 layers; 45° top → upper pilot 1.788 CAD (≈ 1.99 printed). In every layer the wall is ≥ 2.2 mm. Pilots stay teardrops pointing up.
- **Tab screws (S3):** 4 × M3 × 12 pan-head self-tapping + Ø7 washers; 7 mm engaged, the tips stand 2 mm out of the back face at X ±24.25, clear of the gussets (|X| ≥ 28.5).
- **Orientation (SYS-09):** the upright's front face (+Y) is where the shoulder shaft comes out; at the base servo's centre it faces +Y, so the arm reaches out over the +X (USB) wall at yaw 0.
- **Loads (SYS-04):** the arm and camera hang outboard of the upright: 290 N·mm (335 with 50 g) about X at the upright's mid-plane in every pose, with the round-3 claw (spec §4; was ≈100 N·mm with the old gripper).
- measure_holes: 4 × Ø2.8 shoulder tab pilots (teardrops), Ø3.6 clamp hole.

## Round 5 (2026-10-26: links strength round 4, SF 2.00; DFM round 4 notes 1, 2, 4). Third design attempt
- **What failed.**
  - The disc horn's two M2 × 6 anti-rotation screws, in bearing under the base stall: SF 2.00 at the assumed r 9.
  - The upright's front face under the yaw-stall sweep: window bottom 2.80, lower pilot row 2.83.
- **Change 1: 4 × M2 × 8 anti-rotation screws** (were 2 × M2 × 6), through four of the disc horn's holes on one circle.
  - **Engagement:** 8 − 2.8 (disc) = 5.2 mm in the disk.
  - **Hole circle, how to choose it:**
    - Pick 4 holes in opposite pairs, at r ≥ 7 mm (`DISC_HOLE_R_MIN`).
    - The bearing SF scales with the number of screws × the hole-circle radius: 6.51 × n × r / 36.
    - Opposite pairs keep the screws on the same pilots when §5's trim turns the disc half a turn.
  - **Pilots work for any hole circle.** They are drilled at assembly, Ø1.5 through the horn's own holes, 6 mm into the 8 mm disk (`ANTI_ROT_PILOT_DEPTH`).
    - The disk underside is plain from r 4 to 13 (`ANTI_ROT_ZONE`; the disc is Ø25), so a pilot can land anywhere on any of the disc's circles.
    - `print_requirements.json` now asks for 30 bottom solid layers and `bottom_solid_min_thickness` 6.0. The bottom 6 mm of the disk is then solid, and each screw bites solid plastic over its whole 5.2 mm, not 1 mm of skin over 40 % gyroid (DFM round 4 note 4).
    - That costs about 25 g of PETG and about 0.5 h of print time (last slice 6.8 h of the 8 h limit). Weight under the yaw axis doesn't load the arm.
  - **The hole circle is assumed until measured.**
    - BUILD_GUIDE §2 step 1 now asks for the disc's holes: the number on each circle and its radius.
    - BUILD_GUIDE §4 step 3 gives the rule and what to do when the disc differs: 4 at r ≥ 7 mm (SF ≥ 5.1); 4 at r 5–7 is still SF ≥ 3.6; 3 at r ≥ 7 gives SF ≥ 3.8, but §5's half turn then needs fresh pilots; anything less, tell Claude before drilling.
- **Change 2: GUSSET_H 70 → 90**, as the analyst's FIX rows asked.
  - The hypotenuse would end above the upright's top (Z 97.3), so the gussets are cut off there, 4.4 mm deep.
  - Their outer face leans 14.3° from vertical: each layer is smaller than the one below, so there is no overhang.
  - Footprint unchanged: toe at r 47.76, inside the disk.
- **Verification.** The analyst's `strength_calc.py`, run on the round-5 masses and geometry (it reads GUSSET_H from model.py):

  | Check (yaw-stall sweep unless stated) | Round 4 | Round 5 |
  |---|---|---|
  | 4 × M2 × 8 bearing, at r 9 (assumed) | 2.00 (2 × M2 × 6) | **6.51** |
  | 4 × M2 × 8 bearing, at r 7 (worst likely) | 1.56 | **5.06** |
  | Window bottom (Z 50.6) | 2.80 | **3.26** |
  | Lower pilot row (Z 55.5) | 2.83 | **3.45** |
  | Notch level (Z 60.5) | 3.38 | 4.34 |
  | Root, front face / gusset toe | 8.94 / 4.19 | 9.05 / 4.26 |

  - Hand push at the window bottom and pilot row: 4.12 / 4.15. Weight ×2 (needs 4): 8.58 or above.
  - Every other row is unchanged or better. Every row reaches its required SF.
  - With a 15 kgf·cm clone MG996R the window bottom drops to 2.39. That is the analyst's sensitivity row, not a spec case.
- **Notch tops (DFM round 4 note 2).** Each 45° top now runs 0.02 mm past the notch's end, so its slope meets the cutter box's outer top corner. The two 0.02 × 7 mm flats at print z 46.3 are gone: mesh_check reports 0.0 % overhang and no bridges.
- **Checks:** `cad_checks.py` (14 checks, exit 0) covers:
  - the gusset profile at three heights, the cut-off at the top and the toe radius;
  - the anti-rotation zone (648 probes, all solid);
  - the window, the notches with their 45° tops, the pilots, the clamp hole and the washer gap in the front wedge.
  `assembly_check.py`: the shoulder is free of collisions over 0–180°.
- **Mass.** +1.54 cm³: 90.7 cm³, 115 g solid (was 113), before the solid bottom layers.

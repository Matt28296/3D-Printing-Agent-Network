# Design brief: Upper link (shoulder → elbow, 100 mm)

Job: 20261025-arm-upper-link · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~70 °C (material-selection skill) still 30 °C above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, FRONT face on the bed (the horn pocket and, since round 5, the back-face ribs open upward, so no bridge and no support). In-plane and out-of-plane bending run along the layers; horn-joint pull-out shears the layers, which the centre-screw clamp now carries.

## Concept
Flat 10 mm plate on the shoulder servo's double-arm horn, carrying the elbow MG996R at 100 mm. Since round 5 each window rail has a 6 mm rib on the back face, so the rails beside the elbow servo are 6.85 × 16.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Shoulder–elbow axis distance | 100.0 | ±0.3 | kinematics | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Horn slot | as turntable | +0.2/−0 | locating | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Elbow window | 41.1 × 20.1 | +0.3/−0 | clearance | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Lead notches (round 3) | 4.4 wide, 2.0 beyond each case end (printed) | +0.2/−0 | 4 × 1.3 mm lead ribbon; 1.84 CAD (≈ 2.04 printed) to the nearest pilot | HOLE_COMP +0.2 on holes/pockets | deep review 01 B1 (`MG996R.lead_notch_w/reach`); DFM round 4 note 3 |
| Rail ribs (round 5) | 6 deep on the back face, as wide as the rails (6.85: window wall to plate edge), full depth x 64.2–117, 27° run-out (`RIB_TAPER` 12) to x 52.2 | +0.3/−0 | strength: rails 6.85 × 16; rib root fed into the plate over 12 mm | none | links strength round 4 FIX (6 mm; 4 mm gives 2.93); run-out: links strength round 5 FIX (`RIB_TAPER` 6 → 12) |

Printed targets: servo windows +0.4 total (SG90 window ends +0.2), horn pockets +0.5 total, M3 clearance Ø3.4, M2 clearance Ø2.4, self-tap pilots Ø2.6 (MG996R tab screws) and Ø1.5 (SG90 tab screws). Every hole and pocket also gets **HOLE_COMP = +0.2 mm** in CAD (fdm-design-rules default; no library row yet), applied in tools/hobby_parts.py cutters and each model.py. Horn joints: the horn's centre screw is replaced by a longer one + washer through the link, clamping link and horn onto the spline (strength round 1).

## Parameters exposed by model.py
SERVO, HOLE_COMP, L, T, HALF_W, X0, X1, CORNER_R, CLR, BED_CHAMFER, WIN_HW, WIN_X0, WIN_X1, RIB_H, RIB_PAST, RIB_X0, RIB_TAPER, RIB_X1

## Risks
- Horn-slot bridge 10.6 mm (DFM round 1) → printed front-face down, pocket opens upward
- Sideways loads (strength round 1) → T 6→10, lightening slot removed, centre-screw clamp
- The window rails carry the elbow servo's sideways moment past the window, because each MG996R tab row acts as a pin (links strength round 4, SF 1.49) → 6 mm back-face ribs on both rails (round 5)
- Ribs behind the link could meet the turntable, the shoulder servo or its horn → they start 58 mm out from the shoulder axis (52.2 since round 6), outside anything on the turntable; measured clearance ≥ 11.9 mm over the shoulder's 0–180° (round 5); round 6: `assembly_check.py` re-run clean

## Round 3 (2026-10-26: deep reviews 01 B1/S2/S3/S4, 03 SYS-04)
- **Lead notches (B1).** The elbow MG996R goes in from the front face, case bottom first; `lead="notch"` cuts a 4.4 × 2.0 mm (printed) notch at both case ends through the 10 mm plate. Printed ligament to the nearest Ø2.6 pilot: 2.05 mm. The plate prints flat, so the notches are vertical cuts (no overhang).
- **Fasteners:** shoulder clamp M3 × 14 + Ø9 × 0.8 washer (8 mm floor: 4.6 mm into the spline, S2); 2 × M2 × 6 through the horn arms (S4); elbow tab screws 4 × M3 × 12 + Ø7 washers, 9 mm engaged (S3).
- **Loads (SYS-04):** the camera and the round-3 claw put 239 N·mm (278 with 50 g) across the shoulder shaft and 161 / 188 N·mm across the elbow shaft in every pose (spec §4).
- measure_holes: 4 × Ø2.8 elbow tab pilots, Ø3.6 clamp hole.

## Round 5 (2026-10-26: links strength round 4, SF 1.49; DFM round 4 note 3). Third design attempt
- **What failed.** The two 6.85 × 10 window rails at the window's far end, in out-of-plane bending: yaw stall 1.49, hand push 1.89.
  - Each MG996R tab has its two screws at the same x, so a tab row is a pin about the plate's y axis.
  - The near tab's force therefore travels back through the rails: 0.926 of the far-row moment.
- **Change: a 6 mm rib on each rail, on the back face** (`rail_ribs()`, `RIB_H` 6), as the analyst's FIX asked.
  - **Width:** exactly as wide as the rail. The inner face continues the window wall (y ±10.15), so the elbow servo still slides through. The outer face follows the plate edge, rounded corner included.
  - **Length:** full depth from 5 mm before the window's far end (x 64.2) to x 117. That is 6.5 mm past the window and 2.9 mm past the near pilot row, where the r 8 corner still leaves the rib 5.8 wide. At the shoulder end a 45° run-out reaches the back face at x 58.2, so there is no step on the loaded plate.
  - **What it leaves open:** the window, both lead notches and all four pilots, through 16 mm. The lead leaves the case end on the centre line, between the ribs.
  - **Printing:** the link prints front face down, so the ribs rise from the top face with no support. mesh_check: 0.0 % overhang, no bridges, no thin walls.
- **Verification.** The analyst's `strength_calc.py`, re-run on the round-5 masses: the rails as 6.85 × 16 (every term of the rail stress scales with (10 / 16)²).

  | Case | Round 4 | Round 5 |
  |---|---|---|
  | Yaw stall | 1.49 | **3.82** |
  | Hand push | 1.89 | **4.83** |
  | Weight ×2 (sustained) | 5.12 | **13.07** |

  - The far lead-notch section (x 67.4–69.5, 3.41 as a plain plate) and the far pilot row (x 65.6, 3.88) now sit inside the ribbed length. With the ribs the notch section's I rises 2450 → 6800 mm⁴ and its stress falls by about a third (about 5.1).
  - The link's lowest row is then x 15 over the horn pocket, untouched by this round: 3.42 under the yaw stall.
  - With a 15 kgf·cm clone MG996R the rails drop to 2.80 (analyst's sensitivity).
- **Clearance.**
  - The ribs sit behind the link at least 58 mm from the shoulder axis, and nothing on the turntable reaches there. Measured with meshes over the shoulder's 0–180° in 5° steps, including the shoulder servo with its double-arm horn, the upright's four tab-screw heads and the turntable clamp: **≥ 11.9 mm**.
  - The elbow horn is on the link's other side, 23.7 mm away along the shaft.
  - `assembly_check.py`: every named pose and the shoulder and elbow sweeps are free of collisions.
- **Notch tolerance (DFM note 3)** is now a row in the critical-dimension table.
- **Checks:** `cad_checks.py` (14 checks, exit 0) covers:
  - size 146 × 34 × 16, the clamp hole, the 4 pilots, the window and the notches;
  - the notch → pilot strip, 1.835 CAD;
  - the ribs: depth, rail depth 16.00 at the window's far end, width 6.85, extent, run-out, and nothing between them or at the shoulder end.
- **Mass.** +4.57 cm³: 44.1 cm³, 56 g solid (was 50). It moves the arm's worst static shoulder torque from 553 to 562 N·mm (camera, sliced; torque_budget.json).

## Round 6 (2026-10-26: links strength round 5, rib root SF 1.89). Fourth design attempt, user-approved fix
- **What failed.** The rib root: the ribs' force (106 N at x 64.2 under the yaw stall) passed into the plate across the layers through the 6 mm, 45° run-out. Interlayer shear 3.30 MPa against 6.25: yaw stall **1.89**, hand push 2.47, spec §8 bench test (2) **1.07**.
- **Change: `RIB_TAPER` 6 → 12**, exactly as the analyst's required change. Nothing else moves.
  - The ribs still reach full depth at x 64.2; the run-out now slopes at 27° and meets the back face at **x 52.2** (was 58.2). It is under 1 mm tall for its first 2 mm.
  - Analyst's what-if for 12: rib root yaw **3.78**, hand 4.94, weight ×2 13.2; §8 bench test **2.14**; turntable arm-up test 2.69; plain plate at the new foot 4.40.
- **Printing.** The run-out is a ramp rising in print (front face down), so no support. mesh_check: 0.0 % overhang, no bridges, no thin walls, bed contact 3881 mm² (unchanged).
- **Clearance.** The ribs now start 52.2 mm from the shoulder axis. `assembly_check.py` re-run (named poses and the shoulder sweep): clean.
- **Checks.** `cad_checks.py` (14 checks, exit 0): the run-out probe now checks `RIB_TAPER` 12, depth 3 at x 58.2, 1 at x 54.2 and 0 at x 52.2.
- **Mass.** +0.25 cm³: 44.3 cm³ (was 44.1).

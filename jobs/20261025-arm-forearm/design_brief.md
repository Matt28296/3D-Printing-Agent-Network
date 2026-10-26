# Design brief: Forearm (elbow → wrist, 90 mm)

Job: 20261025-arm-forearm · design-lead (Architect acting in this test run) · 2026-10-25

## Material
PETG. Tough, low creep compared with PLA (the arm holds servo load for hours), prints on an open-frame MK3S without an enclosure, softening point ~70 °C (material-selection skill) still 30 °C above the 40 °C service temperature. No library data for this spool yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, FRONT face on the bed (horn pocket opens upward, no bridge). Bending along the layers.

## Concept
Flat 10 mm plate on the elbow servo's double-arm horn, carrying the wrist MG90S at 90 mm (round 3; the SG90 rows below are the round-2 record).

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Elbow–wrist axis distance | 90.0 | ±0.3 | kinematics | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| SG90 window | 22.7 × 12.4 | +0.3/−0 | clearance 0.1/side at the ends | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| SG90 pilot-to-window wall | 1.8 printed | min | 4 perimeters | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: servo windows +0.4 total (SG90 window ends +0.2), horn pockets +0.5 total, M3 clearance Ø3.4, M2 clearance Ø2.4, self-tap pilots Ø2.6 (MG996R tab screws) and Ø1.5 (SG90 tab screws). Every hole and pocket also gets **HOLE_COMP = +0.2 mm** in CAD (fdm-design-rules default; no library row yet), applied in tools/hobby_parts.py cutters and each model.py. Horn joints: the horn's centre screw is replaced by a longer one + washer through the link, clamping link and horn onto the spline (strength round 1).

## Parameters exposed by model.py
HORN_SERVO, WRIST, HOLE_COMP, L, T, HALF_W, X0, X1, CORNER_R, CLR, END_CLR, BED_CHAMFER

## Risks
- SG90 pilot-to-window wall 1.55 mm (DFM round 1) → Ø1.5 printed pilot + 0.2 end clearance → 1.8 mm printed
- Sideways loads (strength round 1) → T 5→10, slot removed, centre-screw clamp
- Wrist SG90 tab screws pull out (strength round 2) → M2×12 self-tapping, 9.5 mm engaged

## Round 3 (2026-10-26: deep reviews 01 B1/B2/S1/S2/S4, 03 SYS-03/SYS-04/SYS-18)
- **The wrist servo is the MG90S (SYS-18, B2, S1):** its own spec, 22.8 × 12.2 body, case bottom 18.5 below the tabs, spline top 14.0 above them. Window 23.2 × 12.8 CAD (23.0 × 12.6 printed: 0.4 side, 0.2 end clearance).
- **Lead notch (B1, option 1):** `lead="notch_shift_pilot"`: a 4.2 × 1.5 mm (printed) notch at the shaft end (+x) and that end's pilot moved 1.3 mm out, to x 99.7. The builder files that tab's slit to 2.1 mm. Printed ligaments: notch → moved pilot 1.55 mm, far pilot → window 1.65 mm (set by the MG90S's 27.8 mm hole spacing on a 22.8 mm body), moved pilot → window 2.95 mm; the moved pilot's slot ends 3.0 mm from the plate end (X1 104). The two small ones are above hobby_parts' 1.5 mm minimum for a self-tapper and under the 1.8 mm "4 perimeters" rule: M2 × 12 self-tappers driven snug.
- **Fasteners:** elbow clamp M3 × 14 + Ø9 × 0.8 washer (4.6 mm into the spline, S2); 2 × M2 × 6 through the horn arms (S4).
- **Fitting pose (SYS-03):** at the elbow servo's centre the forearm goes on 60° below the upper link's line, towards +X: the elbow's window is −150 … +30°, all of it free of self-collision (`assembly_check.json` elbow_window_deg).
- **Loads (SYS-04):** 161 N·mm (188 with 50 g) across the elbow shaft and 108 / 124 N·mm across the wrist shaft in every pose, from the camera and the round-3 claw (spec §4).
- measure_holes: Ø3.6 clamp hole (the MG90S pilots are slots).

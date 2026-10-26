# Design brief: Femur (×6)

Job: 20261026-hexapod-femur · design-lead · 2026-10-26 · round 3: strength round 1 (NEEDS_TEST, snug clamp) and the deep review (B1, B2, SYS-1, SYS-5)

## Material
PETG for every hexapod part: tough, low creep under the servos' constant holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, horn pocket on the bed (bridge 7.9 mm). Bending in both directions runs along the layers. The window, pilots and tie slot are vertical through-cuts.

## Concept
7 mm flat plate from the femur MG90S horn to the knee (45 mm), carrying the tibia MG90S. Strength round 1 needs no geometry change (lowest SF 4.59, assembly case), on condition that the clamp screw is driven **snug (≈ 0.05 N·m)**. BUILD_GUIDE and spec §2 now say so.

## B1: the tibia servo's lead (option 2, reversed)
The lead leaves the case at its shaft end, 13.4 mm below the tabs, and a closed window can't pass it.

**Option 2 is used:** the tibia servo goes in from the femur's **back** face, spline first. Its tabs rest on the back face (the bed face), and its case and lead stay behind the femur, so the lead never crosses the plate. The window and the pilots are through-cuts, so the model is the same as before; only the servo turns round (`tibia_servo_cutter_loc` documents the frame, `lead="none"`). Why this option:
- **No filing** of these 6 tabs.
- **Room in front:** the tibia's back face sits **3.1 mm** off the femur's front face. The servo's gear boss pokes 0.4 mm out of the window, 2.7 mm from the tibia.
- **Less torsion:** the tibia moves 9.5 mm closer, so its mid-plane is 10.1 mm in front of the femur's (16.4 in strength's check). That cuts the torsion that set the femur's lowest service SF. The foot sits 12.7 mm off the coxa line instead of 22.2 (deep review SYS-8).
- **Room behind:**
  - The case now reaches 21 mm behind the femur, into the coxa bracket's plane.
  - Over the gait it stays ≥ 3.3 mm from the bracket.
  - Over the femur's whole −70 … +90° it stays ≥ 0.76 mm away, once the coxa plate's unloaded outer corner is cut (coxa `CORNER_CUT`).

The coxa plate (10 mm after strength round 1) can't take option 2, so the femur servos use option 1 there. The robot files 6 tabs in all.

## Critical dimensions
| Feature | Nominal | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Femur axis → knee | 45.0 | ±0.3 | leg geometry | — | hex_frame `L_F` |
| Tibia-servo window | 22.8 × 12.2 + 0.2 end / 0.4 side (23.0 × 12.6 printed) | +0.3/−0 | 0.1 end / 0.2 side clearance | HOLE_COMP +0.2 | default from fdm-design-rules (no library row) |
| Pilots | Ø1.5 + HOLE_COMP, slotted 0.4 outward | ±0.2 | M2 × 8 self-tapping, 5.5 mm engaged | HOLE_COMP | default |
| Clamp hole / horn pocket | Ø2.4 + HOLE_COMP / horn + 0.5 + HOLE_COMP, 2 deep | +0.2 | M2 clearance / horn locating | HOLE_COMP | default |

`cad_checks.py` proves each row on the built solid (7 checks, exit 0).

## Parameters exposed by model.py
HOLE_COMP, HALF_W, X0, PILOT_OUT, X1, CLR, END_CLR, LEAD, TIE_SLOT, TIE_XY, BED_CHAMFER (+ hex_frame.py: L_F, T_F, TIBIA_MOUNT)

## Lead tie point (SYS-5)
The 3.2 × 1.8 slot at (20, −6) sits between the horn pocket (ends at x 16.5) and the tibia servo's tab (x 23.4), 2.6 mm from the lower edge.
- The tibia lead runs along the femur's back face from its case at the knee end and is tied there.
- It then crosses the femur joint in a 20 mm loop, below the femur axis and clear of the femur servo's horn (deep review pinch point 2).

The slot takes 11 % off the in-plane second moment at x 20; strength had SF ≥ 25 there.

## Stance (SYS-1)
The femur servo is the robot's weak point. The firmware's walking stance tucks the tibia 18.7° in (femur −4.7°, tibia −14.0°), so the foot sits midway between the femur axis and the knee. Peak static femur torque in the gait is 83–87 N·mm (38–40 % of stall) at the round-3 mass of 812 g, against 126 in round 2's stance. Table: assembly plan, "Stance".

## Risks
- **SG90-size pilot wall:** 1.45 mm CAD to the window (≈ 1.65 printed), as reviewed on the arm.
- **Tibia-servo tab screws in pull-out** under a push towards the coxa (reversed): same magnitudes as checked (SF ≥ 6.9 in the drop).
- **Femur clamp head and washer stand 2.1 mm proud of the front face, which the tibia passes 3.1 mm away:** it only reaches them folded back past the femur axis, far outside the gait.
- **Print time:** round 2's slice of 6 femurs took 3.9 h against spec §7's 3 h, and round 3's femur is the same size. The slicing stage should print 4 + 2, or the user relaxes §7.

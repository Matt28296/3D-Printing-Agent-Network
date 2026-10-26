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
| Servo pilot holes | Ø2.6 | ±0.1 | self-tap M3/servo screw | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Servo pilot pattern | 48.5 × 10.0 | ±0.2 | matches MG996R tabs | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| DC jack hole | Ø11.4 | +0.3/−0 | panel jack Ø11 thread | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Overall | 110 × 104 × 40 | ±0.5 | free | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |

Printed targets: servo windows +0.4 total (SG90 window ends +0.2), horn pockets +0.5 total, M3 clearance Ø3.4, M2 clearance Ø2.4, self-tap pilots Ø2.6 (MG996R tab screws) and Ø1.5 (SG90 tab screws). Every hole and pocket also gets **HOLE_COMP = +0.2 mm** in CAD (fdm-design-rules default; no library row yet), applied in tools/hobby_parts.py cutters and each model.py. Horn joints: the horn's centre screw is replaced by a longer one + washer through the link, clamping link and horn onto the spline (strength round 1).

## Parameters exposed by model.py
HOLE_COMP, SERVO_CLR, BED_CHAMFER, BX, BY, H, WALL, PLATE_T, CORNER_R, PILLAR_D, PILLAR_HOLE, SERVO_BOSS_D, SERVO_BOSS_L, RING_PILOT_R, RING_PILOT_ANG, CRADLE_PILOTS, CRADLE_BOSS_D, CRADLE_BOSS_L, PILOT, USB_SLOT, USB_Y, USB_Z, JACK_D, JACK_Y, JACK_Z, CABLE_SLOT

## Risks
- Wall openings printed as overhangs → 45° roofs / teardrop pointing up in print
- Self-tapping pilots crack the plate → servo screw bosses lengthen the grip to 10 mm; PETG is tough

## Round 3 (2026-10-26: deep reviews 01 B1/S3, 03 SYS-05/SYS-09/SYS-12)
- **Lead notches (B1).** The MG996R goes in from above, case bottom first, and its lead root crosses the 4 mm top plate: `servo_mount_cutter(lead="notch")` cuts a 4.4 × 2.0 mm (printed) notch at each case end (the MG996R's lead end is unverified), clipped to the top plate only. Below the plate the ribbon passes between the Ø6.5 bosses, which stand ≥ 3 mm off the centreline at the case end. Printed ligament from a notch to the nearest Ø2.6 pilot: 2.05 mm (the cutter's check); window end to pilot 2.4 mm. A vertical cut through the bed layer: no overhang.
- **Tab screws (S3):** 4 × M3 × 12 pan-head self-tapping + Ø7 washers, grommets and eyelets left out: 9 mm engaged in the 10 mm plate + boss.
- **Turntable on a disc horn, ring 0.4 mm under it (SYS-05):** the base now sees the arm's overturning moment through the ring and its 3 screws as well as through the servo tabs (spec §4: 692–832 N·mm arm straight out with the camera).
- **Build order (SYS-09):** built and wired upside down on the bench, screwed down last; the extension junctions sit outside the cable slot.
- **Stability (SYS-12):** with the round-3 claw and camera the robot is ≈0.70 kg; free-standing it tips with the arm out (SF 0.34–0.48), so the desk screws stay required, or a 200 × 200 × 0.4 kg board (SF ≥ 2.2) or 1.2 kg of ballast (SF 1.5).
- measure_holes: 10 × Ø2.8 (4 servo, 3 ring, 3 cradle pilots), 4 × Ø3.6 desk holes, the Ø11.6 jack teardrop.

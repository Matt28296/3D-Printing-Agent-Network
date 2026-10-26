# Design brief: Rover lid / electronics deck

Job: 20261026-rover-lid · design-lead (round 3) · 2026-10-26

## Material
PETG for every rover part: tough against knocks, wears acceptably on steel pins, prints on an open-frame MK3S, softening point ~70 °C, well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, underside on the bed; seat ledges and rails rise from the top face. Deck bending is in the layer plane. The rail roots are the only across-layer section (strength round 2, lowest SF 3.27).

## Concept
A 3 mm deck screwed to the chassis's four insert columns. It carries:
- the ESP32 DevKit: pins down through a window, PCB on end ledges, held by zip ties over its pin-free ends;
- a 170-point mini breadboard with the TB6612FNG driver;
- the power toggle;
- two cable slots;
- the MP1584 buck, which hangs under the deck.

Round 3 (deep review 04):
- **Screws (S-09).** The screw holes moved to the chassis's new insert columns at (−13, ±32.5) and (102, ±32.5): `SCREWS = rover_frame.LID_SCREWS`, so the chassis and the lid can't disagree. They take M3 × 8 machine screws into heat-set inserts, so the lid can come off for every charge.
- **Toggle (S-06).** The MTS-102 moved from the rear wall to the deck at (0, −23), lever up.
  - It used to stick out about 20 mm behind the tracks, where the autonomous mode's blind reverse would hit it.
  - Now it sits beside the ESP32's USB end, inside the outline, and the switch body hangs into the tub at the rear.
  - The assembly check places it with both nuts and its lever. It collides with nothing; the battery holder starts at x 22.
- **Cable slots (S-10).** The Ø10 cable hole became two 10 × 10.5 slots at x 71–81, |y| 1.5–12, either side of a 3 mm tie bar.
  - The 15–17 jumpers pass in two groups.
  - The bundle is zip-tied to the bar, so lifting the lid doesn't pull on the N20 tabs or the breadboard contacts.
  - Corners are r2; the slot edges carry the hole compensation.
- **Buck (S-13).** Under the deck at x 85–107, on foam tape: one place, in every document.

## Critical dimensions
| Feature | Nominal (mm) | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| ESP32 pocket width | 29.7 | +0.3/−0 | 0.6 clearance | HOLE_COMP +0.2 on holes/pockets | default from fdm-design-rules (no library row) |
| Screw holes | Ø3.4 printed (Ø3.6 CAD) | +0.2/−0 | M3 clearance | HOLE_COMP +0.2 | default |
| Toggle hole | Ø6.2 printed (Ø6.4 CAD) | +0.2/−0 | M6 × 0.75 bushing | HOLE_COMP +0.2 | default |
| Cable slots | 10 × 10.5 | ±0.3 | Dupont housings, 3.6 mm diagonal each | +0.1 per edge | deep review 04 S-10 |

Printed targets for the whole rover: see the chassis brief.

## Parameters exposed by model.py
HOLE_COMP, T, CORNER_R, SCREWS, SCREW_D, BOARDS, USB_END_X, LEDGE_H, CLR, RAIL_W, HALF, ROW_KEEP, END_LEDGE, TIE_SLOT, TIE_FROM_END, BB_X0, CABLE_X, CABLE_Y, CABLE_R, SWITCH, SWITCH_D, BED_CHAMFER. `cad_checks.py` proves them on the geometry.

## Risks
- **Zip ties across the pin rows** would short or bend pins (DFM round 1). The ties cross the board 1.2 mm from its ends.
- **Jumper housings under the ESP32.**
  - The window spans both pin rows.
  - The housings end 5.0 mm above the battery holder, 3.5 mm above its strap (assembly check).
  - The BUILD_GUIDE has the wires folded flat towards the cable slots, one layer deep.
- **Toggle bushing too short for a nut on each side.** Fallback: inner nut off, body against the deck underside (spec §3).
- **Inserts pulling out of the columns.** Proof test 5 (lid refit ×5) and the lift-by-the-lid load of 3.2 N per screw.

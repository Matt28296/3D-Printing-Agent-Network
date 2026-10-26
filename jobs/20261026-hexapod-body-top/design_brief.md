# Design brief: Hexapod top plate / electronics deck

Job: 20261026-hexapod-body-top · design-lead · 2026-10-26 · round 3: deep review (SYS-4, SYS-10, SYS-14) and the round-3 frame

## Material
PETG for every hexapod part: tough, low creep under the servos' constant holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, underside on the bed: deck bending along the layers; the seat rails and the PCA9685 posts stand up from it. Every hole and notch is vertical; no overhangs or bridges.

## Concept
3 mm deck (130 × 104 mm) on the four columns. It carries:
- the ESP32 seat (pins down through a window);
- two PCA9685 boards on M2.5 posts, headers facing out to each side;
- the MP1584 buck;
- the main switch.

The UBEC is **not** on the deck: it stands on its side on the bottom plate, beside the LiPo. This corrects the round-2 text (deep review SYS-14).

Round 3 changes:

| Change | Why | Model |
|---|---|---|
| Screw holes follow the columns to (±36, ±25) | the bottom plate's columns moved, clear of the reversed coxa servos' tabs and nuts | `SCREWS = hex_frame.COLUMNS`; the heads stay 1.75 mm clear of the boards (asserted in `design()`) |
| 6 lead notches 10 × 5 at x −40, 0, 40 in both long edges, each with a tie slot | SYS-4: through the corner slots every femur lead was 44–122 mm short. Each leg's leads now come up the body's side beside that leg and over the edge to its board's channels | `LEAD_NOTCH_X`, `LEAD_NOTCH`, `NOTCH_TIE_DX`, `TIE_SLOT` |
| Ø12 main-switch hole at (−50, 0) | SYS-10: no part had a switch mount. Behind the ESP32's USB end, clear of the LiPo's end, the rear coxa servos and the cable slots below. 02-H4 asks for ≥ 10 A DC, which 12 mm-bushing toggles cover | `SWITCH_D`, `SWITCH_XY`. If the electrical BOM picks another switch, change these before printing |
| Cable slots driven by one parameter | DFM round 2 recommendation (the old `CABLE_SLOTS` was unused) | `CABLE_SLOTS`, `CABLE_SLOT_SIZE` |

The notches at x ±40 sit beside the cable slots (x 46–54), so strength's lowest handling section (through the slots at x 46) is unchanged. The notch at x 0 leaves 94 mm of the 104 mm width.

## Critical dimensions
| Feature | Nominal | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Column screw holes | Ø3.4 at (±36, ±25) | ±0.2 | M3 clearance | HOLE_COMP +0.2 | default from fdm-design-rules (no library row) |
| PCA9685 post pattern | 56 × 19 | ±0.2 | board holes | — | hobby_parts `PCA9685_HOLES` |
| ESP32 pocket width | 29.5 printed (29.7 CAD) | +0.3/−0 | 0.6 clearance | HOLE_COMP/2 per side | default |
| Switch hole | Ø12.0 printed | +0.3/−0 | 12 mm bushing | HOLE_COMP | default |

`cad_checks.py` proves each row on the built solid (8 checks, exit 0).

## Parameters exposed by model.py
HOLE_COMP, SIZE, CORNER_R, SCREWS, SCREW_D, BOARDS, USB_END_X, LEDGE_H, CLR, RAIL_W, ROW_KEEP, END_LEDGE, PCA_Y, POST_D, POST_H, POST_PILOT, CABLE_SLOTS, CABLE_SLOT_SIZE, LEAD_NOTCH_X, LEAD_NOTCH, TIE_SLOT, NOTCH_TIE_DX, SWITCH_D, SWITCH_XY, BED_CHAMFER (+ hex_frame.py: COLUMNS, T_TOP)

## Risks
- **Heavier robot below the deck in round 3:** handling SF ≈ 3.8 against 3 (estimate; strength to confirm).
- **Switch type not chosen by the electrical BOM yet:** `SWITCH_D` is a parameter.
- **Lead lengths:** the femur leads probably still need extensions (SYS-4). The channel map is another agent's.

# Design brief: Hexapod bottom body plate

Job: 20261026-hexapod-body-bottom · design-lead · 2026-10-26 · round 3: strength round 1 and the deep review (B1, B2, S14, SYS-5, SYS-6, SYS-10)

## Material
PETG for every hexapod part: tough, low creep under the servos' constant holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Flat, underside on the bed. Plate bending, pilot bearing and ligament tear-out run along the layers. The columns stand and bend across the layers at their r1.5 root fillets. All holes are vertical, and there are no overhangs or bridges (mesh_check: 0 %).

## Concept
A 6 mm plate (hull of the six coxa windows plus a 4 mm margin, 154.8 × 138.8 mm) under the body. It has:
- six reversed coxa servos, tabs on its top face;
- four Ø8 × 40 columns for the deck, with r1.5 root fillets;
- two LiPo strap slots;
- six lead tie slots.

Strength round 1's required changes are modelled as checked:

| # | Change | Model |
|---|---|---|
| 1 | T_BODY 4 → **6 mm** (strip outside each window: walking SF 3.84 → 7.24, drop 1.71 → 3.23) | `hex_frame.T_BODY` |
| 2 | Coxa tab screws: **M2 × 12 machine screws + washers + nuts** in **Ø2.4 CAD clearance holes** (drop: pull-out 1.94 → nut bearing 3.84, plug shear 7.76) | `TAB_SCREW_CLEAR` 2.2 + HOLE_COMP, slotted 0.4 outward by `servo_mount_cutter` |

## B1: the coxa servos' leads (option 2, reversed)
Each lead leaves its case at the shaft end, 13.4 mm below the tabs, and a closed window can't pass it.

**Option 2 is used:** the servo goes in from above, spline first, tabs on the plate's **top** face (`servo_cutter_loc` puts the cutter on the top face, `lead="none"`). Its case and lead stay inside the body, so the lead never crosses the plate. Why this option:
- **The plate's critical section stays whole.** The strip outside each window's outer end (7.3 mm deep, strength's lowest SF) keeps its full depth. Option 1 would cut a 1.6 mm notch into it and move a pilot 1.3 mm into it, which drops the strip below SF 3 unless the outline grows.
- **No tab filing** for these 6 servos.
- **The geometry has room:**
  - The coxa bracket's back face sits **4.1 mm** under the plate (horn face 6.1).
  - The gear boss pokes 1.4 mm through, 2.7 mm from the bracket.
  - The outer screw's head and washer stand 1.9 mm proud, 2.2 mm from the bracket at every coxa angle.
  - Inside, the case stands 21 mm above the plate top, under the deck at 40 mm.

What it moved:
- **Columns x ±40 → ±36** (`hex_frame.COLUMNS`). At ±40 the corner servos' inner tabs and nuts, now on the top face, would hit the column fillets (washer 0.35 mm from a column). At ±36: tab hardware 3.4 mm, tab end 2.2 mm from the r5.5 fillet foot. The LiPo still slides out between them (y ±19.5).
- **Middle legs y ±52 → ±56** (`hex_frame.LEG_MOUNTS`). The middle servos' inner tabs and nuts would otherwise stand where the UBEC goes beside the LiPo (S14). Now the UBEC (50 × 10 × 20 on its side, y 22.5–32.5) is 1.6 mm clear of them and 5 mm from the LiPo, with the strap between.
- **The load path:** the foot's upward force lifts the tabs off the plate, so the screws carry it in tension; spec §4 asks strength to re-check. The heads bear on the underside through Ø5 washers (14 mm²), more area than the nut the check used (8.6 mm²).

## Critical dimensions
| Feature | Nominal | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Plate | 6.0 | ±0.2 | strength | — | strength round 1 |
| Coxa windows | 22.8 × 12.2 + 0.2 end / 0.4 side (23.0 × 12.6 printed) | +0.3/−0 | 0.1 end / 0.2 side clearance | HOLE_COMP +0.2 | default from fdm-design-rules (no library row) |
| Tab-screw holes | Ø2.2 printed (Ø2.4 CAD), slotted 0.4 outward | +0.2 | M2 clearance | HOLE_COMP | default |
| Window → clearance-hole ligament | 1.1 CAD | — | tear-out (strength: SF ≥ 19 at 1.6) | — | — |
| Mount positions | `hex_frame.LEG_MOUNTS` | ±0.3 | leg spacing | — | hex_frame |
| Columns | Ø8 × 40 at (±36, ±25), Ø2.6 + HOLE_COMP pilots 10 deep | ±0.3 | M3 × 8 self-tapping | HOLE_COMP | default |

`cad_checks.py` proves each row on the built solid (11 checks, exit 0).

## Parameters exposed by model.py
HOLE_COMP, CLR, END_CLR, LEAD, TAB_SCREW_CLEAR, MARGIN, COLUMN_D, COLUMN_PILOT, PILOT_DEPTH, COLUMN_FILLET, STRAP, TIE_SLOT, TIE_UV, BED_CHAMFER (+ hex_frame.py: COLUMNS, COLUMN_H, COXA_MOUNT, LEG_MOUNTS, T_BODY)

## Leads (SYS-4, SYS-5)
- The coxa servo's own lead is inside the body: it goes straight up to the deck.
- The femur and tibia leads come off the bracket round the outside of its arm, never through the 4.1 mm gap. They are tied at the 3.2 × 1.8 slot beside each window, at (x 4, y −16) in that servo's frame, after a 30 mm free loop, then run up the body's side to that leg's notch in the deck.

## SYS-6
Each leg hangs on its coxa servo's shaft. The proof test is in the coxa and assembly specs (§8). A bump arc on the coxa bracket that lands on this plate's underside is proposed in the coxa brief. It would need this plate's outboard margin grown about 2 mm; not modelled until the leg test asks for it.

## Risks
- **Mass:** 141.9 g solid (round 2: 95.8). The plate's mid-span has SF ≥ 10 at 6 mm. If the femur servos run hot, lightening windows under the LiPo and fore and aft of it would save about 17 g.
- **Tab screws in tension (reversed mount):** washers under the heads; strength to re-check (spec §4).
- **Window → clearance-hole ligament 1.1 mm CAD:** the screw is located by the window, so the hole only clears it.
- **Print time:** ≈ 7.7 h, scaled by volume from round 2's 5.18 h slice, against `max_print_hours` 8.

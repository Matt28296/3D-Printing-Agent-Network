VERDICT: PASS

# DFM review (round 3): 20261026-hexapod-body-bottom

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26

**Inputs**
- This job: spec.md, design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json, print_requirements.json, slice_plan.json, strength.md (round 1), the round-2 review.
- Renders: all 5, regenerated with `tools/render.py` and viewed.
- Assembly job: assembly_plan.md (B1 table, interfaces), hex_frame.py, spec.md, BUILD_GUIDE.md, assembly_check.json (`clean: true`).
- Deep review: 01-bought-parts.md (B1, B2, S1, S14) and 05-hexapod-system.md (S1 body size, SYS-5, SYS-10). Also tools/hobby_parts.py.
- library/lessons.md: no entries.

**Probes:** trimesh `contains` on part.stl. u and v are each coxa servo's own axes (S0 x and S0 y); z is up from the underside.

**Outputs are current.**
- `build()` gives 111747.90 mm³ and a 154.8 × 138.8 × 46.0 bbox from (−77.4, −69.4, 0), the same as geometry.json.
- part.stl is one watertight body.
- `tools/mesh_check.py`, re-run in memory, gives exactly the committed mesh_check.json.
- cad_checks.py: 11/11 PASS, exit 0.

**What is new in round 3:**
- T_BODY 6;
- the coxa servos reversed (B1 option 2, `lead="none"`), so the lead never crosses the plate;
- 12 Ø2.4 CAD clearance slots for M2 × 12 machine screws with nuts;
- the middle legs moved to y ±56 and the columns to (±36, ±25);
- six SYS-5 tie slots.

All of them are vertical cuts in a flat plate, or columns standing on it.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits the bed with a 5 mm margin | PASS | 154.8 × 138.8 × 46.0 mm on 250 × 210: 47.6 and 35.6 mm a side |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, `watertight: true`, `min_z_mm: 0.0`. part.stl is 1 body |
| 3 | Orientation matches the brief | PASS | The underside is on the bed and the columns rise from the top (iso.png, front.png, right.png). The reversed servos' tabs rest on the top face |
| 4 | Load paths | PASS (justified) | Plate bending and the tab-hardware loads run along the layers. With the reversed mount, a foot's upward force pulls the tab screws. They are machine screws with nuts, so the load bears through the Ø5 washer under each head, not through threads in the plastic. Spec §4 and the brief hand this new path to strength. The columns bend across the layers at their r1.5 root fillets (handling SF 3.69 in strength round 1) |
| 5 | Bed contact | PASS | 17118.4 mm² of PETG |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | `overhang_pct` 0.0, `bridges: []`. The windows, the 12 clearance slots, the 6 tie slots and the strap slots are vertical through-cuts. The column fillets shrink as they rise (radius 5.115 at z 6.05, 4.38 at 6.5, 4.0 from 7.5), so they are not overhangs |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (note) | Plate 6.0 (cad_checks). Column wall (8 − 2.8)/2 = 2.6 (z 40: bore 34.6–37.4). Clearance slot to the outline 3.4 at z 3 (3.1 at z 0.1, chamfer) on all six mounts. Tie slots ≥ 5.3 from the outline across the servo axis and ≥ 3.6 along it, 8.6 from the window. `thin_wall_warnings: []`. Under 1.8: the window-to-slot ligament, **1.1 mm CAD** (≈ 1.3 printed), at both ends of every window (u runs: solid −18.2…−17.1 and 6.1…7.2). It is a solid web above 0.9, and the brief and cad_checks (≥ 1.0) record it. Machine screws in clearance don't cut into it. Strength round 1 had tear-out SF 25.9 at 1.60, about 17.8 scaled to 1.1. Strength should confirm |
| 8 | HOLE_COMP; horizontal holes | PASS | Windows 23.2 × 12.8 CAD (u −17.1…6.1, v ±6.4). Clearance slots Ø2.4 = `TAB_SCREW_CLEAR` 2.2 + 0.2, slotted 0.4 outward (u −21.0…−18.2 and 7.2…10.0). Column pilots Ø2.8 = 2.6 + 0.2. Tie slots 3.4 × 2.0 = 3.2 × 1.8 + 0.2. Every hole is vertical |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(bp.part, 0.0, 0.4)` on the blank (model.py:92). At y 0 the edge is at x −77.05 (z 0.05), −77.3 (z 0.3) and −77.4 (z 0.5). The window rims on the bed face aren't chamfered, but only the Ø11.8 gear boss passes the window's bottom 1.7 mm: the case top stands 1.7 mm above the underside (S0 8.5 − case top 6.8). The boss clears an elephant's-foot lip there, and `elefant_foot_compensation` is 0.2 |
| 10 | Internal corners on load paths filleted | PASS (justified) | Column roots r1.5 (probe in #6). The window corners are square, as the servo case needs. The plate bends in its own plane, along the layers, and strength round 1 carried them at Kt 2.5: the strip outside the window has SF 3.23 in the drop at T_BODY 6. Strap and tie slots are in low-stress areas |
| 11 | Fasteners per §4 | PASS | Coxa tabs: M2 × 12 pan head, Ø5 washer, 6 mm plate, 2.5 mm tab, Ø5 washer, nut. 0.3 + 6 + 2.5 + 0.3 + 1.6 = 10.7, so 1.3 mm of thread runs past the nut (spec §2, BUILD_GUIDE). There are washers under the head and the nut (rule §4, creep). The nuts are reached from above before the deck goes on. A corner servo's inner tab hardware is 3.4 mm from its column (assembly plan). Its slot is 3.2 mm beyond the column's fillet foot: the first void round each column on the top face is at r 8.7, the foot at r 5.5. Deck: M3 × 8 self-tapping into Ø2.8 CAD pilots 10 deep (bore z 36–46), 5 mm engaged |
| 12 | Spec §3 dimensions are named parameters | PASS | T_BODY 6.0 (hex_frame.py:74). Windows: SERVO + `CLR`/`END_CLR` (model.py:32) + `HOLE_COMP` (:31). `TAB_SCREW_CLEAR` 2.2 (:34). `LEG_MOUNTS` (hex_frame.py:71–72), `COLUMN_H` 40 and `COLUMNS` (±36, ±25) (:75–76). All have source comments. Spec §1–3 and the brief now give 23.2 × 12.8 CAD / 23.0 × 12.6 printed windows and 40 mm columns (round-2 fix 1) |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG ≈ 70 °C. At the 50 °C servo-case limit (assembly spec §8) the margin is exactly 20 °C. Before slicing: `materials_on_hand` in config/printer.json is empty |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

**The moved columns (±36, ±25):** each Ø8 × 40 column has an r1.5 root fillet (foot r 5.5) and a 10 mm pilot. No cut feature comes within 3.2 mm of the fillet foot. The LiPo still slides between the fillet feet: y ±19.5 against the pack's ±17.5.

## Required fixes

None.

## Round 2 fix checked

1. **Spec and brief state the windows the model makes: done.**
   - Spec §2: "23.2 × 12.8 CAD". Spec §3 and the brief: "23.0 × 12.6 printed (23.2 × 12.8 CAD)", +0.3/−0, 0.1 end / 0.2 side clearance.
   - The CLR 0.4 and END_CLR 0.2 now act on the MG90S's own 22.8 × 12.2 (S1), so text and model agree (probes in #8).
   - Spec §1 and the brief's concept say 40 mm columns.

Round-2 recommendations:
- **Lead exit:** solved by the reversed mount: the lead stays inside the body.
- **UBEC dummy:** now in assembly_check.py (50 × 10 × 20 at y 22.5–32.5), and the check is clean.
- **geometry.json `holes`:** a valid list now.

## Recommendations (not blocking)

Strength re-check of the reversed mount (spec §4 asks for it):
- **Tab screws:** in tension now.
- **Ø5 washer under each head:** its bearing ring reaches up to 0.2 mm past the window's end. A screw at the slot's window end puts the rim at u 5.9 against the window at 6.1.
- **The strip outside each window's outer end:** 7.3 mm deep (u 6.1 → 13.4). It now holds a 2.8 mm slot, which leaves 1.1 + 3.4 = 4.5 mm of plate on the slot's line.
- **The 1.1 mm ligament** (#7).

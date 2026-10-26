VERDICT: FAIL

# DFM review: 20261025-arm-esp32-cradle

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), base model.py, tools/hobby_parts.py, assembly_plan.md, library/lessons.md (no entries).
Outputs are current: `build()` gives 5990.6 mm³, matching geometry.json (5990.58 mm³).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 64 × 41.85 × 6 mm |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | The Z −16 face is on the bed and every ledge rises from it (iso.png) |
| 4 | Load paths | PASS | Non-structural. The 5 N jumper pull goes into the ledges in compression |
| 5 | Bed contact | PASS | 1176.4 mm² |
| 6 | Overhangs / bridges | PASS | `overhang_pct` 0.0, no bridges |
| 7 | Walls | PASS (note) | WALL 2.5. The USB-end ledge is 1.6 mm wide (x 49.4–51.0) and only supports the PCB end. That is above 0.9 mm and non-structural |
| 8 | Fit holes / HOLE_COMP | **FAIL** | No `HOLE_COMP`. Spec §3 sets the PCB pocket width at 29.5 **+0.3/−0**, and it prints about 0.2 mm narrow, which falls outside that tolerance (the 1.2 mm total clearance still lets the board in). The Ø3.4 M3 clearance holes are fine |
| 9 | Bottom edges chamfered | **FAIL** | `build()` returns `to_bed(design())` with no `chamfer_bottom` |
| 10 | Internal corners on load paths | PASS | Non-structural part |
| 11 | Fasteners | **FAIL** | The 3 × M3×8 screws (spec §2) pass through the 6.0 mm frame (`TOP − BOT`) into the base's Ø2.6 × 6 mm blind boss pilots, which leaves **2.0 mm of thread engagement**. A self-tapper's tapered lead is about 1 to 1.5 mm, so the screw has almost no full thread in the boss |
| 12 | Critical dims named | PASS | `HALF` (from CLR 0.6), `PCB_BOT = −11.6`, and `SCREWS` matches the base `CRADLE_PILOTS` [(−9.4, 18), (−9.4, 38), (40, 7.9)] |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C. Correct the brief's "~80 °C" |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

1. **Get at least 4 mm of screw engagement** (rule §4, checklist 11). Either counterbore the 3 holes from the bed side, Ø6.5 × 3.0 deep, so the heads seat at Z −13 and M3×8 then engages 5 mm (the counterbore ceiling is a 1.55 mm-wide annular bridge, which prints fine), or change spec §2 and the assembly plan to M3×10 (4 mm engagement; M3×12 would just reach the end of the 6 mm pilot).
2. **Chamfer the bed edges**: `to_bed(chamfer_bottom(design(), 0.4))` (rule §2 and §6, checklist 9).
3. **Apply `HOLE_COMP` to the pocket width**: `HALF = max(width)/2 + CLR + HOLE_COMP/2` (rule §3, checklist 8; spec §3 −0 tolerance).

## Notes (cross-part, design frame = base frame)

1. The USB-end ledge corner (49.5, 42.5) sits exactly on the base corner pillar's circle (centre (49.5, 46.5), r 4.0): 0.0 mm clearance, line to line. The cradle locates on Ø3.4 holes over Ø2.6 pilots, so it can shift ±0.4 mm into the pillar. Lower the ledge's y1 by 1 mm (`YC + ROW_KEEP + 2.5`).
2. The −Y wall (y ≥ 10.75, x −13 to 51, Z −16 to −10) runs beside the base servo body (y ≤ 9.85 nominal, plus 0.2 window float), leaving a 0.7 to 0.9 mm gap. A servo 1 mm wider than nominal, which the assembly plan says is possible, would touch it. Check this with your measured servo.
3. The USB plug has to pass the base slot (13 × 7 at Z −12 to −5, plus a 45° roof) with 1 mm between the board end (x 51) and the inner wall (x 52). Try your cable's plug overmold in the base slot before printing the cradle.

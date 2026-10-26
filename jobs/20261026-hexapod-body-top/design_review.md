VERDICT: PASS

# DFM review (round 2): 20261026-hexapod-body-top

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), the round-1 review, ../20261026-hexapod-assembly/{hex_frame.py, assembly_check.py, assembly_check.json, assembly_hexapod.png, assembly_plan.md, BUILD_GUIDE.md}, ../20261026-hexapod-body-bottom/model.py, tools/hobby_parts.py, library/lessons.md (no entries).

Outputs are current: `build()` gives 36653.8 mm³ and a 130 × 104 × 8 bbox, identical to geometry.json, and model.py (05:18:36 UTC) is older than part.stl (05:19:20).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 130 × 104 × 8 mm |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | The underside is on the bed. The seat, rails and posts rise from the top (iso.png, right.png) |
| 4 | Load paths | PASS | The handling lift through the 4 M3 heads bears on the 3 mm deck along the layers. A USB pull goes into the end ledge and the rails |
| 5 | Bed contact | PASS | 11270.9 mm² |
| 6 | Overhangs / bridges | PASS | `overhang_pct` 0.0, `bridges: []`. The 4 bridges at z 4.0 from round 1 (posts overhanging the merged screw holes) are gone |
| 7 | Walls | PASS (advisory) | Deck 3 mm. Rails 2.5 × 4.1 mm. Posts Ø5.5 with a Ø2.4 pilot leave a 1.55 mm wall, non-structural (brief). Screw hole to cable slot: 46 − 41.8 = 4.2 mm |
| 8 | HOLE_COMP / teardrops | PASS | Ø3.6 = `SCREW_D` 3.4 + 0.2 and Ø2.4 = `POST_PILOT` 2.2 + 0.2 (geometry.json holes). `HALF` 14.85 includes HOLE_COMP/2. There are no horizontal holes |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(top, 0.0, 0.4)` |
| 10 | Internal corners | PASS (advisory) | The post and rail roots are sharp, but the loads there are low (as in round 1) |
| 11 | Fasteners / fits | PASS | geometry.json lists column holes Ø3.6 at (±40, ±25) and post pilots Ø2.4 at (±28, ±25) and (±28, ±44). They are 12 mm apart and no holes merge (top.png, bottom.png). An M3 head with clearance (Ø6) clears the nearest post by 6.25 mm, the PCA9685 boards (x ±31.25) by 5.75 mm and the cable slots (x 46) by 3.0 mm, so the plate comes off with the boards fitted. The M3×8 self-tapping screws pass the 3 mm deck and engage 5 mm in the column pilots |
| 12 | Critical dims named | PASS | The PCA9685 post pattern 56 × 19 is `PCA9685_HOLES`. The ESP32 pocket width 29.7 is 2 × `HALF` (14.85). `SCREWS = COLUMNS` comes from hex_frame.py:40, which now drives both plates |
| 13 | Service temperature | PASS | 40 °C against PETG ≈ 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

**Assembly stack, ESP32 jumpers against the LiPo (spec §8): PASS.** Heights in the body frame, with the tab plane at 0:

| Level | Height (mm) |
|---|---|
| Deck underside (`T_BODY` 4 + `COLUMN_H` 40) | 44.0 |
| PCB underside (44 + 3 + 2) | 49.0 |
| Bottom of the jumper housings (49 − 16.5) | 32.5 |
| LiPo top | 22.0 |

That leaves **10.5 mm** for the leads (0.5 mm in round 1). assembly_check.py now adds a 10 mm bend zone under the housings (a 26.5 mm tall box, lines 95–96). Its bottom at 22.5 clears the LiPo dummy (top 22.01), and the stance has no collisions.

The velcro strap is not modelled. It crosses the LiPo at x ±11, under the middle of the pin rows. A strap about 1.5 mm thick leaves about 9 mm there, which is still within the 8–10 mm round 1 estimated a Dupont lead needs to bend.

## Required fixes

None.

## Round 1 fixes checked

1. PCA9685 posts against the column screws: **done.**
   - The column pattern moved to (±40, ±25) and is defined once in `hex_frame.COLUMNS` (hex_frame.py:40). This part uses it as `SCREWS = COLUMNS`, and the bottom plate imports it at model.py:18.
   - The holes are 12 mm from the posts, and the heads stay outside the boards (#11).
   - Both plates were rebuilt (05:19 UTC) and assembly_check.py was re-run (05:20 UTC, stance clear).
2. Room for the ESP32 jumper leads: **done.**
   - `COLUMN_H` 30 → 40 (hex_frame.py:39) gives 10.5 mm under the housings.
   - The bend zone is in the electronics dummy (assembly_check.py:95–96).
   - The bottom plate's columns have r1.5 root fillets.

## Recommendations

- Model the velcro strap (≈ 1.5 mm over the LiPo at x ±11) in assembly_check.py, or add 2 mm to `COLUMN_H`, if you want the full 10 mm of bend room over the strap.
- `CABLE_SLOTS = [(-46, 12), (46, 12)]` is unused, and its comment is wrong. `design()` hard-codes the slots (8 × 16 mm at x ±50, y ±22). Drive them from one parameter (rule §7).
- Spec §1 and the brief's concept say this deck carries the UBEC. BUILD_GUIDE.md (round 2) puts the UBEC on the bottom plate and the MP1584 buck on this deck. The buck's 22 × 17 mm fits at x ≈ 28–46, between the seat and the cable slots. Make the text agree.
- Spec §3's ESP32 pocket width of 29.7 is the CAD value. It prints at about 29.5, which is 0.6 mm per side over the 28.3 mm board. Label 29.7 as CAD, or give 29.5 as the printed target, so an inspection against "29.7 +0.3/−0" does not reject a good part.

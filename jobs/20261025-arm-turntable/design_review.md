VERDICT: FAIL

# DFM review (round 2): 20261025-arm-turntable

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), tools/hobby_parts.py (round 2), assembly_plan.md, library/lessons.md (no entries).
Outputs are current: `build()` gives 89389.4 mm³, matching geometry.json (89389.42 mm³). The geometry.json `holes` field still holds an error (toolsmith, advisory), so I measured the holes from model parameters and part.stl sections.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 96 × 96 × 80.8 mm |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | Disk down, upright vertical (iso.png, right.png) |
| 4 | Load paths | PASS (justified) | Shoulder torque acts in the upright's plane. The root bending across the layers is addressed with UP_T 7, 3 mm root wedges and 70 mm gussets (brief); strength-analyst owns the numbers |
| 5 | Bed contact | PASS | 7105.0 mm². The underside is now flat with no pocket (bottom.png) |
| 6 | Overhangs / bridges | PASS | `overhang_pct` 0.0 and `bridges` is empty. The gusset toe is at y = −12 − 23 = −35, so the corner is at r = √(32.5² + 35²) = 47.76 < 48 (top.png shows the toes inside the rim). The window has a 45° roof |
| 7 | Walls | PASS | DISK_T 8, UP_T 7, GUSSET_T 4. Window-to-pilot ligament is 2.25 mm (section at print z 39: solid from x 20.65 to 22.90). No region under 1.8 mm in sections at z 4, 8.5, 30 and 60 |
| 8 | HOLE_COMP / horizontal holes | PASS | `HOLE_COMP` 0.2 on the window (41.3 × 20.3 CAD), the pilots (Ø2.8 CAD) and the clamp hole (Ø3.6 CAD). The 4 horizontal pilots are teardrops pointing +Z (`pilot_teardrop="-y"`, where servo −y is world +Z). front.png shows the points up, and there are no downward faces in mesh_check |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(disk, Z0, 0.4)` |
| 10 | Internal corners on load paths | PASS | 3 mm 45° root wedges run the full 66 mm width on both faces (right.png) |
| 11 | Fasteners | **FAIL** | The spec §2 base-horn clamp is an "M3×16 centre screw + Ø9 washer from the top". The front root wedge runs from the upright face at y −5 to **y −2.0** at the disk top. A section along x = 0 at print z 8.25 has solid out to y −2.24, and the Ø3.6 clamp hole edge is at y −1.8. A Ø9 washer reaches y −4.5, where the wedge is about 2.5 mm tall, and even a bare M3 head (Ø5.5, y −2.75) lands on 0.75 mm of wedge. The washer and head cannot seat flat, so the clamp, which is now the only thing holding the disk on the horn axially, would sit tilted. top.png shows the hole touching the wedge band |
| 12 | Critical dims named | PASS | `XS` 10.15, `ZS` 60.5, `CLR`, `HOLE_COMP`, `Z0 = horn_face_z` = 16.5 |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

1. **Clear the clamp-screw seat** (rule §4, checklist 11). Interrupt the front root wedge for |x| ≤ 6 mm, which leaves a flat Ø12 seat around the hole: the washer reaches y −4.5 against the upright face at −5.0. The rest of the wedge (|x| 6–33) keeps the root relief. strength-analyst should confirm the root with the 12 mm gap. Alternative: specify a washer of Ø7 or less and still cut the wedge back to |x| ≥ 4.5.

## Round 1 → round 2

| Round-1 finding | Status | How I checked |
|---|---|---|
| Gusset toes overhung the disk (r 51.5) | Closed | Toe corner at r 47.76. No downward faces at print z 8. top.png |
| Horn-slot bridge 10.6 mm | Closed | The pocket was removed (`horn_pocket_cutter(..., depth=0)` cuts only the Ø3.6 clamp hole). `bridges` is empty |
| No HOLE_COMP | Closed | All cutters get `hole_comp=HOLE_COMP` |
| Round horizontal pilots | Closed | Teardrops pointing up (front.png). mesh_check overhang 0 |
| Sharp upright root | Closed | 3 mm 45° wedges on both faces (right.png) |
| Assembly order (centre screw under the shoulder servo) | Closed | Spec §2 now says "Drive the centre screw BEFORE fitting" the shoulder servo |

## Notes

1. Screwdriver access: with the driver on the axis at y 0, the 7 mm upright face is 5 mm away and rises 72.8 mm above the disk top. A driver handle (about Ø25) clears it only with a shaft of at least 75 mm, so say so in the assembly steps.
2. The MG996R tab-screw pilot (printed Ø2.6) is still unverified against the servo-bag screw.

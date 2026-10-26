VERDICT: PASS

# DFM review (round 3): 20261025-arm-turntable

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), tools/hobby_parts.py (round 2), assembly_plan.md, library/lessons.md (no entries).
Outputs are current: `build()` gives 89335.6 mm³, matching geometry.json (89335.6 mm³). The STL and renders are newer than model.py. The geometry.json `holes` field still holds an error (toolsmith, advisory), so I measured the holes from model parameters and part.stl sections.

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
| 10 | Internal corners on load paths | PASS | 3 mm 45° root wedges: the back one runs the full 66 mm, and the front one is in two pieces at 6 ≤ \|x\| ≤ 33, leaving a 12 mm gap at the clamp screw (top.png). strength-analyst should confirm the gap |
| 11 | Fasteners | PASS | Sections along y at print z 8.25 (0.25 above the disk top) end at y −4.99, the upright face, for x = 0, 4.5 and 5.9, and only reach −2.24 at x 6.5. The Ø9 clamp washer (y ≥ −4.5, \|x\| ≤ 4.5) seats on the flat disk top with 0.5 mm to the upright and 1.5 mm to the wedge ends. Shoulder tab pilots are teardrops through 7 mm |
| 12 | Critical dims named | PASS | `XS` 10.15, `ZS` 60.5, `CLR`, `HOLE_COMP`, `Z0 = horn_face_z` = 16.5 |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

None.

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

## Round 2 → round 3

| Round-2 finding | Status | How I checked |
|---|---|---|
| Ø9 washer and M3 head land on the front root wedge | Closed | `WASHER_CLEAR_X = 6.0`: the front wedge is built as two prisms from x −33 to −6 and from 6 to 33. Sections and top.png show a flat seat. mesh_check: `overhang_pct` 0.0, no bridges, watertight. A 1.8 mm opening test at z 8.5 and 30 finds no thin regions |

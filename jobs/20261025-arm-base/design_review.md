VERDICT: FAIL

# DFM review: 20261025-arm-base

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), tools/hobby_parts.py, assembly_plan.md, library/lessons.md (no entries yet).
Outputs are current: re-running `build()` gives 89961.0 mm³, the same as geometry.json (89961.03 mm³).
No measured library values exist yet, so the skill defaults apply (hole compensation +0.2 mm, PETG softening point about 70 °C).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 110 × 104 × 40 mm; geometry.json `fits_bed: true` |
| 2 | Single watertight solid, min Z = 0 | PASS | geometry.json `solids: 1`, `watertight: true`, `min_z_mm: 0.0` |
| 3 | Orientation matches brief | PASS | Printed upside down with the top plate on the bed: bottom.png shows the window, pilots and cable slot on the bed face, and iso.png shows the open side up |
| 4 | Load paths along layers | PASS | Top-plate loads are in-plane. A tab-screw pull-out pushes the Ø6.5 bosses into the plate, so the boss-to-plate layers are in compression |
| 5 | Bed contact | PASS | 10381.5 mm² (mesh_check). PETG, so no warping concern |
| 6 | Overhangs ≤45°, bridges ≤10 mm | PASS | `overhang_pct` 0.0. Widest bridge 1.21 mm (ring-pilot notch at z 5). The USB opening has a 45° roof pointing up (right.png). The jack is a teardrop pointing +Z in print (geometry.json arc 270° at (−53.5, 28, 20)) |
| 7 | Walls ≥1.8 mm, none <0.9 mm | PASS | WALL 3.0, PLATE_T 4.0. Servo bosses (6.5 − 2.6)/2 = 1.95, cradle bosses (7 − 2.6)/2 = 2.2, pillars (8 − 3.4)/2 = 2.3. `thin_wall_warnings` is empty |
| 8 | Fit holes use HOLE_COMP; horizontal holes teardrop | **FAIL** | model.py has no `HOLE_COMP` (grep finds no `HOLE_COMP` or `comp(`). Spec §3 sets the servo window at 41.1 × 20.1 **+0.3/−0**, the pilots at Ø2.6 **±0.1** and the jack at Ø11.4 **+0.3/−0**. With the default 0.2 mm undersize the print comes out at about 40.9 × 19.9 (0.2 total clearance instead of 0.4, against the "drops in without force" acceptance criterion), Ø2.4 pilots (outside ±0.1) and a Ø11.2 jack hole. The horizontal holes themselves are fine |
| 9 | Bottom edges chamfered | **FAIL** | `build()` returns `to_bed(Rot(180,0,0) * design())` with no `chamfer_bottom`. The bed face holds the servo window and the 7 pilot entries, so an elephant's-foot lip forms right at the window the servo drops into |
| 10 | Internal corners on load paths filleted | PASS (advisory) | The plate-to-wall and window corners are sharp, but the loads are low (1000 N·mm stall spread over 4 screws, 48.5 mm pattern) |
| 11 | Fasteners per §4 | PASS (notes) | Self-tapping into PETG is acceptable for a few assemblies. Servo grip 10 mm (plate 4 + boss 6), ring grip 4 mm, cradle pilots blind 6 mm. See notes 3 to 5 |
| 12 | Critical dims are named parameters | **FAIL** | The window clearance is a literal (`servo_mount_cutter(SERVO, PLATE_T + SERVO_BOSS_L, clearance=0.4)`), not a named parameter with a source. BX/BY/H/JACK_D/PILOT/SERVO are named |
| 13 | Service temp ≥20 °C below softening | PASS | 40 °C against PETG at about 70 °C (material-selection). The brief says "~80 °C"; correct it to about 70 °C |
| 14 | lessons.md | N/A | library/lessons.md has no entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

1. **Add `HOLE_COMP = 0.2` (default; replace it with `hole_comp_mm` from library/materials.csv once measured) and apply it to every fitted hole** (rule §3, checklist 8). Use window clearance `CLR + HOLE_COMP` (0.4 becomes 0.6 modelled), servo pilots via `replace(SERVO, screw_pilot_d=2.6 + HOLE_COMP)`, `PILOT = comp(2.6)` and `JACK_D = comp(11.4)`. Evidence: spec §3 tolerances −0 and ±0.1 against the 0.2 mm default undersize.
2. **Chamfer the bed edges**: `chamfer_bottom(to_bed(Rot(180, 0, 0) * design()), 0.4)` (rule §2 and §6, checklist 9). This also gives the servo window mouth a lead-in.
3. **Make the window clearance a named parameter** (`CLR = 0.4  # fdm-design-rules default, hobby_parts`) (rule §7, checklist 12).

## Notes (not blocking, fix while you are in there)

1. The cable slot (16 × 8 at x −40, y −40) clips the corner pillar at (−49.5, −46.5). Slot corner (−48, −44) is 2.9 mm from the pillar centre (r 4). The dark wedge in the slot in bottom.png shows it. This leaves 1.2 mm between the slot and the Ø3.4 desk-screw hole at plate level. Move the slot to about (−36, −38).
2. The ring pilot at 270° (0, −48) breaks 0.3 mm into the −Y inner wall: hole edge at y −49.3 against the wall at −49.0 (geometry.json centroid z 2.5 instead of 2.0 for the other two). The ring tab there also overhangs the base's outer face by 0.5 mm (ring bbox y min −52.5 against base ±52.0). Change `RING_PILOT_R` and the ring's `TAB_R` together to 47.
3. The desk-screw holes run through the full 40 mm pillar, so a desk screw has to be at least 50 mm long. State this in the BOM, or counterbore the holes from the top.
4. The Ø2.6 MG996R pilot assumes an M3-class screw. The tab screws in servo bags are often Ø2.3 to 2.6 self-tappers, which barely bite in a pilot that prints at about Ø2.4. Measure the screw and set `screw_pilot_d` to about 0.8 × its major diameter. Confirm on the arm-fit-test coupon.
5. Cross-part: the cradle's 3 × M3×8 screws pass through the 6 mm cradle into these 6 mm cradle bosses, which leaves only 2 mm of thread engagement. The fix belongs in the cradle (see its review).

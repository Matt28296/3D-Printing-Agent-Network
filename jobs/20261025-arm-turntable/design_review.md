VERDICT: FAIL

# DFM review: 20261025-arm-turntable

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), tools/hobby_parts.py, assembly_plan.md, library/lessons.md (no entries).
Outputs are current: `build()` gives 60649.8 mm³, matching geometry.json (60649.79 mm³).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 96 × 96 × 82.6 mm; `fits_bed: true` |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | Disk on the bed with the upright vertical and the gussets on −Y (iso.png, right.png) |
| 4 | Load paths | PASS (justified) | The shoulder torque acts in the upright's plane. The out-of-plane moment bends the root across the layers, and the brief justifies this with gussets. strength-analyst must confirm |
| 5 | Bed contact | PASS | 6743.4 mm² |
| 6 | Overhangs ≤45°, bridges ≤10 mm | **FAIL** | (a) **The gusset toes overhang the disk.** The gussets span x ±(28.5–32.5) and run out to y −40 at the disk top, but the disk radius is 48: the toe corner is at r = √(32.5² + 40²) = 51.5 (the mesh vertices give a max r of 51.54). That leaves two flat downward faces in mid-air at print z 5.0, each 4.0 × 4.68 mm and 11.9 mm² (mesh_check bridges 2 and 3, anchored on one side only). top.png and bottom.png show both toes sticking out past the rim. (b) **The horn-slot ceiling bridge is 10.6 mm, not 9.5 mm.** Just outside the Ø6.5 access hole (x = ±3.25), the first taper disc of `horn_pocket_cutter` (r 5.41 at x 2.19) is wider than the hub circle, so the longest strand anchored at both ends is 10.6 mm, both computed exactly and measured on a section of part.stl. That is over the 10 mm project rule. mesh_check reports the bounding-box span as 11.5 mm. The brief's and assembly plan's "longest strand 9.5 mm" leaves the taper discs out |
| 7 | Walls | PASS | UP_T 5, GUSSET_T 4, DISK_T 5. Ligament between the window and the tab pilots is 2.45 mm (section at print z 41: solid from x 20.55 to 23.00) |
| 8 | Fit holes / HOLE_COMP; horizontal holes | **FAIL** | No `HOLE_COMP` in model.py. Spec §3 sets the horn slot at **+0.2/−0** and the window at **+0.3/−0**, and both print about 0.2 mm under. The 4 shoulder-servo pilots (Ø2.6) are horizontal holes cut as plain cylinders (`servo_mount_cutter` makes `Cylinder`). Their arc tops are the downward faces at print z 41.9–42.3 and 51.9–52.3. They are not teardrop or flat-top |
| 9 | Bottom edges chamfered | PASS | `chamfer_bottom(design(), 0.4)` |
| 10 | Internal corners on load paths | **FAIL** | The root of the upright, which the brief names as the section loaded across the layers, is a sharp 90° internal corner on both faces (right.png, front.png). It has no fillet, and that is where the stress concentrates |
| 11 | Fasteners | PASS | Tab screws self-tap horizontally into the 5 mm upright, so pull-out runs in-plane |
| 12 | Critical dims named | PASS | `XS` = 10.15, `ZS` = 60.5 and `CLR` = 0.4 match spec §3. `Z0 = link_back_z(SERVO)` = 14.5 |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C. Correct the brief's "~80 °C" |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

1. **Keep the gussets inside the disk.** Change `GUSSET_LEN` from 30 to 24, so the toe is at y −34 and the corner at r = √(32.5² + 34²) = 47.0 < 48. The alternative is `DISK_R` ≥ 52 (rule §2 overhangs, checklist 6; evidence: mesh verts r 51.54, mesh_check bridges at z 5.0). strength-analyst then re-checks the shorter gusset.
2. **Keep the horn-slot ceiling strands ≤10 mm.** Either cap the arm-taper half-width at ≤5.0 mm in the slot cutter, so that every chord outside the Ø6.5 access hole is ≤10 mm (the hub circle alone gives 9.49 mm at x = 3.25), or justify the 10.6 mm in design_brief.md with bridge settings and prove it on the arm-fit-test coupon. The cutter lives in tools/hobby_parts.py (toolsmith or cad-engineer), and the same fix applies to upper-link and forearm (rule §2 bridges, checklist 6).
3. **Apply `HOLE_COMP` (0.2 default)** to the window (`CLR + HOLE_COMP`) and the horn slot (clearance 0.5 + HOLE_COMP) (rule §3, checklist 8; spec §3 −0 tolerances).
4. **Make the 4 horizontal pilots teardrop or flat-top**, for example `teardrop_cutter(2.6, …, axis="Y")` with the point up, instead of the round cylinders from `servo_mount_cutter` (rule §2, checklist 8).
5. **Fillet the upright root on both faces**, r ≥ 2 mm. A 45° fillet strip of about 3 mm prints without support (rule §2 internal corners, checklist 10).

## Notes

1. Assembly order: once the shoulder servo is fitted, its body (x ±20.35, z 50.65–70.35, y −32 to +4.5) sits directly above the Ø6.5 access hole, so the base horn's centre screw can no longer be reached. Fit the turntable to the base horn and drive the centre screw first, then mount the shoulder servo. Write this into the assembly instructions.
2. Any sag in the slot ceiling lowers the disk and eats into the ring's 1.5 mm running gap.
3. The MG996R tab-screw pilot (Ø2.6) is unverified against the actual servo-bag screw (see the base review, note 4).

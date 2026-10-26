VERDICT: FAIL

# DFM review (round 1): 20261026-hexapod-coxa

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), ../20261026-hexapod-assembly/{hex_frame.py, assembly_plan.md, assembly_check.py, assembly_check.json}, tools/hobby_parts.py, library/lessons.md (no entries). Section probes run on part.stl with trimesh (`mesh.contains` at the points quoted below).
Outputs are current: `build()` gives 7153.19 mm³, the same as geometry.json. model.py (21:45:26) is older than part.stl (21:45:28) and mesh_check.json (21:45:30). The geometry.json `holes` field still holds an error (toolsmith, advisory).

Values below are computed from the parameters, not from the comments. Several comments are wrong: PILOT_X is (−19.25, 8.55), not (−19.4, 8.4). VPLATE_X is 9.25…44.05, not 9.1…43.9. WIN_HALF is 6.3, not 6.4. `link_back_z` is 9.4, not 9.7 (hex_frame.py). That puts the femur at C y −4.1…2.9 (not −3.8…3.2), so the arm clears it by 2.4 mm, not 2.7.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 53.05 × 25.0 × 33.75 mm, `fits_bed: true` |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, `min_z_mm: 0.0` |
| 3 | Orientation matches brief | PASS | The horizontal plate is on the bed and the vertical plate stands up. The window roof and the pilot teardrops point +Z (front.png, iso.png). The roof is `"-y"` in the servo frame, and servo −y = C +z, which is up in print |
| 4 | Load paths | **FAIL** | The brief accepts cross-layer bending at the vertical-plate root because it has "4.5 mm plate + 6 mm 45° gussets". **No gussets exist.** In `design()` both gusset spans have negative length: xa = VPLATE_X[0] + 3 = 12.25 and xb = win_x0 − 3 = 12.20; xa = win_x1 + 3 = 41.10 and xb = VPLATE_X[1] − 3 = 41.05. The `if xb - xa > 1` test skips both. The mesh agrees: no solid at y −13.0, z 5.5 or at y −12.0, z 6.5 anywhere along x 9.5…44. right.png shows a bare L with a sharp inside corner. The window also reaches down to z 6.7 (Z_F − WIN_HALF), only 1.7 mm above the arm top at z 5.0 (section x 27: void z 6.7…30.3). Above z 6.7 the plate is just two posts, 5.95 × 4.5 mm each (z 13 section: solid 9.30–15.20 and 38.10–44.05, both broken by the pilots). Those posts carry the femur-stall couple and the sideways-shove bending, with tension across the layers, from the window's sharp bottom corners |
| 5 | Bed contact | PASS | 786.8 mm² of PETG, no warping concern |
| 6 | Overhangs / bridges | PASS (advisory) | `overhang_pct` 2.81. Horn-pocket bridge: 7.9 mm span at z 2.0 (≤ 10 mm). Roof 45°, pilot teardrops 45°. Advisory: there is a 3 × 3 mm bridge at z 4.99 (mesh_check). The square end of the vertical plate (x 41–44.05, y −18…−15) sits over the arm's r 3 corner. Probe: (43.8, −17.8) is void at z 4.9 and solid at z 5.2. It is a ~1.9 mm² unsupported patch, cosmetic |
| 7 | Walls | PASS | Vertical plate 4.5 mm. Pilot-to-window ligament 1.55–1.65 mm CAD (z 13 section), ≈ 1.8 mm printed, the same as the arm review accepted. Pilot-to-plate-end edge 2.25 mm. Horn-pocket floor 3.0 mm (T_C − 2). Hub wall at the horn tip 19 − 16.45 = 2.55 mm. `thin_wall_warnings: []` |
| 8 | HOLE_COMP / teardrops | PASS | `HOLE_COMP = HOLE_COMP_DEFAULT` (0.2) goes into both cutters: window 22.9 × 12.6 CAD, pilots Ø1.7, horn pocket +0.7, clamp hole Ø2.6. The horizontal pilots have `pilot_teardrop="-y"` (up). The window has a 45° roof |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(br, 0.0, 0.4)` on the blank, before the pocket is cut. The horn-pocket rim on the bed is not chamfered. Rely on `elefant_foot_compensation` (advisory) |
| 10 | Internal corners on load paths | **FAIL** | (a) The vertical-plate root (z 5) and the window's bottom corners (z 6.7) are sharp: no fillet and no gusset (right.png, front.png). (b) Where the hub meets the arm, at (x 19, y −6.5), there is a sharp re-entrant corner through the full 5 mm (top.png, bottom.png). All of the foot moment (≈ 310 N·mm, spec §4) passes it |
| 11 | Fasteners | **FAIL** | Femur-servo tab screws go into Ø1.7 horizontal pilots through 4.5 mm, which is fine. The **coxa centre screw does not suit this part**. Spec §2 gives an M2×12 plus a Ø6 washer, the same as femur and tibia. Here only 3.0 mm of plastic is above the pocket floor (T_C 5 − pocket 2), against 5.0 mm on femur and tibia. So 12 − 0.5 − 3.0 = **8.5 mm** of screw passes the horn's outer face, 2 mm more than on femur and tibia (6.5 mm). One screw length cannot suit both stacks. The screw risks bottoming in the spline bore before it clamps, and then the bracket is not clamped (spec §8: "no lift of the bracket off the horn") |
| 12 | Critical dims named | PASS | L_C = 32.0 and Z_F = T_C + 8 = 13.0 (hex_frame.py), as in spec §3. Servo numbers come from `MG90S`. CLR, END_CLR and HOLE_COMP are named |
| 13 | Service temperature | PASS | 40 °C against PETG ≈ 70 °C (30 °C margin) |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

Fits, checked from the numbers:
- The MG90S goes in from the +y side, case bottom first, along −y. The path is clear: the servo case is at C z 7…19, and the arm and hub top out at z 5.
- The femur-servo case sits at C z ≥ 7, 2.0 mm above the arm (z 5).
- The femur's rear end stays inside r ≈ 11 of its axis. The hub corner (19, 5) is 15.3 mm from the femur axis (32, 13).
- Spec §2 says the window is "22.9 × 12.8". The CAD window is **22.9 × 12.6**, which prints at about 22.7 × 12.4. A servo near the makers' 22.8 mm upper length will not go in (spec §3 already asks for a measurement).

## Required fixes

1. **Give the vertical plate real root support** (rule §2 internal corners; §1 cross-layer load; brief "6 mm 45° gussets"; evidence: the gusset spans in model.py are −0.05 mm, the mesh probe is empty and right.png shows a bare L). Two things constrain any gusset:
   - The femur-servo tabs occupy C x 10.55…42.75, y −13.5…−11.0, z 7…19.
   - The tibia servo sweeps C y ≥ −13.0 at radius ≥ 28.4 mm from the femur axis (32, 13).

   So a 6 mm gusset under the tabs would hit them. Do one of these, then re-run assembly_check.py:
   - (a) Lengthen VPLATE_X by ≥ 6.5 mm at each end. Put 6 mm gussets only outside the tab span (x < 10.0 and x > 43.3), keeping them inside r 27 of the femur axis.
   - (b) Raise the window. For example, Z_F = T_C + 12 gives a ≥ 5.7 mm solid band between the arm and the window. Add a full-length r ≥ 1.5 mm root fillet, or a ≤ 1.5 mm chamfer that stays below the tabs (z < 6.5 now).

   Also put the gusset x-limits on the **tab span**, not the window ±3 mm.
2. **Fillet the hub-to-arm re-entrant corner** at (19, −6.5) with r ≥ 2 mm (rule §2; top.png). It is on the full foot-moment path.
3. **Give the coxa its own centre-screw length** in spec §2 (rule §4, assembly). Size it from washer 0.5 + 3.0 mm floor + the measured spline thread depth below the horn face. That is about M2×8 to M2×10, not the femur's and tibia's M2×12. Or make the hub floor 5 mm (T_C 7) so all three joints share one screw.
4. Fix the stale numbers in model.py comments and spec §2 (window 22.9 × 12.6 CAD; PILOT_X, VPLATE_X, WIN_HALF, femur plane −4.1…2.9). Documentation only, but spec §2 is what a person checks against.

Advisory:
- The plate-end overhang over the arm's r 3 corner: square that arm corner, or end the plate 3 mm short.
- MG90S lead exit: the window has no wire notch and a printed end clearance of ≈ 0.1 mm. Check on a real servo that the lead and its strain relief pass through, before printing 6 copies.

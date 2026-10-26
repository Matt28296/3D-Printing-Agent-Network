VERDICT: FAIL

# DFM review (round 2): 20261025-arm-base

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png (all 5 viewed), tools/hobby_parts.py (round 2), cradle and ring model.py and spec.md, assembly_plan.md, library/lessons.md (no entries).
Outputs are current: `build()` gives 89697.2 mm³, matching geometry.json (89697.17 mm³). The renders are newer than model.py.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits bed with 5 mm margin | PASS | 110 × 104 × 40 mm; `fits_bed: true` |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, watertight, min Z 0 |
| 3 | Orientation matches brief | PASS | Upside down with the top plate on the bed (bottom.png, iso.png) |
| 4 | Load paths | PASS | Unchanged from round 1. Plate loads are in-plane, and tab-screw pull-out puts the boss-to-plate layers in compression |
| 5 | Bed contact | PASS | 10208.3 mm² |
| 6 | Overhangs / bridges | PASS | `overhang_pct` 0.0 and `bridges` is empty. The jack is a teardrop (geometry.json Ø11.6, axis X). The USB opening has a 45° roof (right.png) |
| 7 | Walls | PASS | Servo bosses (6.5 − 2.8)/2 = 1.85, cradle bosses (7 − 2.8)/2 = 2.1, pillars (8 − 3.6)/2 = 2.2, window-to-pilot ligament 24.25 − 20.65 − 1.4 = 2.2. `thin_wall_warnings` is empty |
| 8 | HOLE_COMP / horizontal holes | PASS | `HOLE_COMP = HOLE_COMP_DEFAULT` (0.2, sourced) is applied to every hole. geometry.json gives pilots Ø2.8, pillars Ø3.6 and jack Ø11.6. `servo_mount_cutter(..., hole_comp=HOLE_COMP)` makes the window 41.3 × 20.3 in CAD, which prints at about 41.1 × 20.1 (spec §3) |
| 9 | Bottom edges chamfered | PASS (note) | `chamfer_plane_edges(outer, 0.0, 0.4)` chamfers the bed-face outline. The window and pilot mouths on the bed are not chamfered, so rely on `elefant_foot_compensation` 0.2 there |
| 10 | Internal corners | PASS (advisory) | Unchanged; low loads |
| 11 | Fasteners | **FAIL** | Spec §2 calls for "3 × M3×12 for the cradle (from below, heads in counterbores)". The cradle's counterbores seat the heads at Z −14, so the screw tip reaches Z −2. This base's cradle pilots are blind, Ø2.8 from Z −11 to **−4** (`CRADLE_BOSS_L + 1` cylinder ending at the plate underside), so each screw would drive 2 mm into unpiloted plate. Only 2 mm of plate would remain under the bed face, so the screw bottoms out before the head clamps, or raises a bump on the top face |
| 12 | Critical dims named | **FAIL** | Round-1 fix 3 is still open: the window clearance is still the literal `servo_mount_cutter(SERVO, ..., clearance=0.4, ...)` and not a named, sourced parameter. Spec §3's 41.1 × 20.1 window depends on it |
| 13 | Service temperature | PASS | 40 °C against PETG at about 70 °C. The brief now says about 70 °C |
| 14 | lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | inputs/ is empty |

## Required fixes

1. **Make the cradle screw length agree with the pilot depth** (rule §4, checklist 11). Either change spec §2 (and the cradle spec and assembly plan) to **M3×10**, which puts the tip at Z −4 and engages the full 6 mm pilot, or deepen these pilots to Z −2. The second option leaves only 2 mm of plate under the bed face, so M3×10 is the better choice.
2. **Name the window clearance**: add `CLR = 0.4  # printed, fdm-design-rules default` and pass `clearance=CLR` (rule §7, checklist 12).

## Round 1 → round 2

| Round-1 finding | Status | How I checked |
|---|---|---|
| No HOLE_COMP (window, pilots, jack) | Closed | model.py `HOLE_COMP`. geometry.json hole diameters 2.8 / 3.6 / 11.6. hobby_parts adds `hole_comp` to the window |
| No bottom chamfer | Closed | `chamfer_plane_edges` on the blank (outline only, see item 9) |
| Window clearance literal | **Open** | model.py still passes `clearance=0.4` |
| Cable slot clipped the corner pillar | Closed | Slot is 14 × 8 at (−40, −36). Its nearest corner (−47, −40) is 6.96 mm from the pillar centre (−49.5, −46.5), so 2.96 mm clear of r 4. It is also outside the ring (nearest corner r 45.97 > R_OUT 44). bottom.png shows no wedge |
| Ring pilot into the wall / ring tab past the edge | Closed | Pilots are at r 47.5, and the 270° pilot edge is at y −48.9 against the wall at −49.0, so it no longer cuts the wall. The model.py comment says "1 mm off the inner wall", but it is actually 0.1 mm. The ring tab reaches y −52.0 = the base edge |
| Desk screw length | Closed | Spec now says M3×50 (or #4 × 2") |
| Cradle 2 mm engagement | Replaced | Now an overshoot (item 11) |

## Notes

1. The MG996R tab-screw pilot (printed Ø2.6) is still unverified against the actual servo-bag screw. Check it on the arm-fit-test coupon.
2. The ring screws are now M3×6, giving 3 mm of engagement in the 4 mm plate. That is acceptable, because the ring loads its tabs in compression and shear, not pull-out.
3. Advisory (toolsmith): `tools/cad_build.py`'s hole measurement still errors on turntable, upper-link, forearm, gripper-base and gripper-jaw.

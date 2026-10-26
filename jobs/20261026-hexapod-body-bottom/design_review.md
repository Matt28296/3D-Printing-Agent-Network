VERDICT: PASS

# DFM review (round 4): 20261026-hexapod-body-bottom

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26

**Inputs**
- This job: spec.md, design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json, print_requirements.json, slice_plan.json, status.json, log.md, and the round-3 design_review.md and strength.md.
- Renders: all 5, regenerated with `tools/render.py` and viewed.
- Assembly job: assembly_plan.md, hex_frame.py, assembly_check.json (`clean: true`), stance_torques.json, BUILD_GUIDE.md §1 and §3.
- Deep review 05-hexapod-system.md (SYS-5, SYS-6, SYS-10). Also `tools/hobby_parts.py` and config/printer.json.
- Skills: fdm-design-rules and material-selection. library/lessons.md: no entries.

**Probes:**
- build123d `is_inside` on the built solid;
- trimesh `contains` on part.stl, for the column fillet profile;
- the model's own outline polygon (`outline_points()`), for distances to the edge.

u and v are each coxa servo's own axes (S0 x and S0 y); z is up from the underside.

**Outputs are current.**
- `build()` gives 132039.87 mm³ and a 166.07 × 146.8 × 46.0 bbox from (−83.035, −73.4, 0), the same as geometry.json.
- part.stl is one watertight body (132034.98 mm³).
- `tools/mesh_check.py`, re-run in memory, gives exactly the committed mesh_check.json.
- cad_checks.py: 12/12 PASS, exit 0.

**What is new in round 4** (strength round 3's change set):
- `MARGIN` 4 → 8. The outline moves 4 mm out all round, and the strip outside each window's outboard end is 11.3 mm deep instead of 7.3.
- Columns Ø8 → Ø10, at the same (±36, ±25), with the r1.5 root fillets kept.
- Coxa tab screws M2 × 14 with Nyloc nuts, driven snug at ≤ 0.045 N·m (spec §2, BUILD_GUIDE §1 and §3 step 5).

All of them are vertical cuts in a flat plate, or columns standing on it.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits the bed with a 5 mm margin | PASS | 166.07 × 146.8 × 46.0 mm on 250 × 210: 42.0 and 31.6 mm a side. `fits_bed: true` |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, `watertight: true`, `min_z_mm: 0.0`. part.stl is 1 body |
| 3 | Orientation matches the brief | PASS | The underside is on the bed and the four Ø10 columns rise from the top (iso.png, front.png, right.png). The windows, screw slots, tie slots and strap slots are through-cuts (top.png, bottom.png) |
| 4 | Load paths | PASS (justified) | Unchanged. Plate bending, the strip outside each window and the tab-hardware loads run along the layers. The reversed servo's outboard screw pulls the strip up through the Ø5 washer under its head: a machine screw and nut, no threads in the plastic. The columns bend across the layers at their r1.5 root fillets; strength round 3 sized them Ø10 for the tipped-handling case |
| 5 | Bed contact | PASS | 19732.4 mm² of PETG (round 3: 17118.4) |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | `overhang_pct` 0.0, `bridges: []`. The Ø10 column fillets shrink as they rise: r 6.26 at 0.02 mm above the plate top, 5.61 at 0.3, 5.21 at 0.75, 5.0 from 1.6. So they are not overhangs |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (note) | Plate 6.0. Column wall round the pilot (10 − 2.8)/2 = 3.6 (round 3: 2.6). Strip 11.3 at v ±3 and ±6.35 on all six mounts (cad_checks; probed 11.30). Outboard slot end to the outline 7.4, 7.1 at z 0.1 on the chamfer, on all six (round 3: 3.4). Tie slots ≥ 7.74 from the outline at the corner mounts and 11.19 at the middle ones. On the top face, the corner servos' inner screw slots are 2.1 mm from the Ø10 fillet foot (first void round each column at r 8.62, foot r 6.5; round 3: 3.2). That is a gap in a continuous 6 mm plate, not a wall. **Under 1.8:** the window-to-slot ligament, 1.1 mm CAD at both ends of every window (u runs −18.2…−17.09 and 6.1…7.21). It is unchanged, recorded in the brief and cad_checks (≥ 1.0), and strength's tear-out row is at SF 34.6. `thin_wall_warnings: []` |
| 8 | HOLE_COMP; horizontal holes | PASS | Windows 23.2 × 12.8 CAD (cad_checks). Clearance slots Ø2.4 = `TAB_SCREW_CLEAR` 2.2 + 0.2, slotted 0.4 outward. Column pilots Ø2.8 = 2.6 + 0.2 (geometry.json). Tie slots 3.4 × 2.0. Every hole is vertical |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(bp.part, 0.0, BED_CHAMFER)` with 0.4 on the blank (model.py:97), so it follows the new outline. At y 0 the edge is at x −82.685 (z 0.05), −82.935 (z 0.3) and −83.035 from z 0.45. The window rims on the bed face aren't chamfered, as in round 3: only the Ø11.8 gear boss passes the window's bottom 1.7 mm, and `elefant_foot_compensation` is 0.2 |
| 10 | Internal corners on load paths filleted | PASS (justified) | Column roots r1.5 (profile in #6). The window corners are square, as the servo case needs. Strength carries them at Kt 2.5: the strip at the corners is at SF 3.39 in the drop. Strap and tie slots are in low-stress areas |
| 11 | Fasteners per §4 | PASS | Coxa tabs: M2 × 14 pan head, Ø5 washer, 6 mm plate, 2.5 mm tab, Ø5 washer, Nyloc (3.0 modelled). 0.3 + 6 + 2.5 + 0.3 + 3.0 = 12.1, so 1.9 mm of thread runs past the Nyloc (assembly_check.json `coxa_tab_stack`; spec §8's first criterion asks for it). Washers sit under the head and the nut (rule §4, creep). The Nyloc holds without preload, so nothing relies on preload in PETG (rule §4). Driven snug, ≤ 0.045 N·m (spec §2, BUILD_GUIDE §3 step 5); strength checks the washer bearing at that cap. The Nylocs go on from above before the deck; a corner servo's inner washer and Nyloc are 2.7 mm from the Ø10 column face (screw 10.2 mm from the column axis). Deck: M3 × 8 self-tapping into Ø2.8 CAD pilots 10 deep, 5 mm engaged |
| 12 | Spec §3 dimensions are named parameters | PASS | `MARGIN` 8 (model.py:38–39) and `COLUMN_D` 10 (:40–41), each with a strength round 3 source comment; `COLUMN_FILLET` 1.5, `TAB_SCREW_CLEAR` 2.2, `HOLE_COMP`; `T_BODY` 6.0, `COLUMNS` (±36, ±25) and `COLUMN_H` 40 (hex_frame.py:74–76). Spec §2–3 and the brief say 166.1 × 146.8 × 46.0, the 11.3 strip and Ø10 × 40 columns at (±36, ±25). cad_checks proves the size, the strip and the columns |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG ≈ 70 °C. At the 50 °C servo-case limit (assembly spec §8) the margin is exactly 20 °C. `materials_on_hand` in config/printer.json is still empty |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

## Required fixes

None.

## Round-3 fixes checked

- **DFM round 3** was PASS with no required fixes. Its recommendations went to strength round 3, which made them.
- **Strength round 3's change set**, the reason for this round:

| # | Change | Made |
|---|---|---|
| 1 | `MARGIN` 4 → 8 (strip 11.25 mm) | Yes: `MARGIN` 8; strip 11.3 on all six mounts (#7) |
| 2 | Tab screws snug ≤ 0.045 N·m with Nyloc nuts, in spec §2 and BUILD_GUIDE §3 step 5 instead of "a firm stop" | Yes: spec §2, BUILD_GUIDE §1 (12 M2 × 14, 24 Ø5 washers, 12 Nylocs) and §3 step 5 ("never tighten to a firm stop") |
| 3 | Columns Ø8 → Ø10, r1.5 fillets kept | Yes: `COLUMN_D` 10, `COLUMN_FILLET` 1.5 (#6) |
| — | Re-check the LiPo passage between the fillet feet | 37.0 mm at the plate top and 40.0 above the fillets, for the 35 mm pack: 1 mm a side at the very foot |
| — | Re-check the corner servos' inner tab nuts against the columns | 2.7 mm from the column, and the tab 1.2 mm from the fillet foot (assembly plan); the assembly check is clean |
| — | Re-run `assembly_check.py` | Clean (assembly plan, round 4) |
| 4 | Proof test into spec §8 | Yes: the handling hold, and the drop on spare servos with paint-marked nuts |

**The wider outline and the femur.** With the coxa swung 25–30°, a femur raised above 80° now meets the plate's edge (the assembly plan's round-4 probe). The gait keeps ≥ 4.1 mm, and the plan recommends `FEMUR_MAX` 80 in the sketch if such a pose is ever needed. That is not a fault in this part; it is noted for the firmware owner.

## Print settings: `print_requirements.json` against the brief

- 3 perimeters, 5 / 5 solid layers, 25 % gyroid, layer ≤ 0.2, PETG 230–250 / 80–90 °C, `max_print_hours` 8 (spec §7).
- It is unchanged since round 3, and strength's rows use exactly these settings.
- `slice_plan.json` agrees: 3 perimeters, 25 % gyroid, 1 copy.

## For slicing (not DFM failures)

- **Print time is at risk.** The plate grew to 132.0 cm³ (round 3: 111.7). The brief puts it at about 7.6 h (scaled by printed mass) to 9.1 h (scaled by solid volume) against `max_print_hours` 8, which the validator checks against the slice estimate. If it runs over, relaxing spec §7 is the user's call. The brief's lightening windows would also save time, but they would need a new strength check.
- **Bed release.** That is 19,700 mm² of PETG on smooth PEI, the only sheet in config/printer.json. PETG bonds hard to it, so use glue stick as a release layer (material-selection). Put it in preflight.md.

## Recommendations (not blocking)

- **Builder: hold the Nylocs, don't socket them.** Each tab hole is 2.5 mm from the servo's case wall, so the Ø5 washer and Nyloc sit right against the case. A socket nut driver won't fit beside it. Hold the Nyloc with pliers or a thin 4 mm spanner and turn the screw from below. BUILD_GUIDE §1 lists "M2 nut driver or pliers"; pliers is the one that works here.
- **Washer under each head.** At the screw's nominal position, the slot's window end, its rim reaches 0.2 mm past the window's end. Strength's washer-bearing row allows for it. No change is needed.

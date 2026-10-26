VERDICT: PASS

# DFM review (round 5): 20261025-arm-base

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26 · third design attempt

**Why it reopened.** Links strength round 4 failed the 4 mm top plate round the MG996R's tension-side tab boss, at SF 1.21 (log.md 13:06). Design round 5 changed three things (design_brief.md "Round 5"; model.py:40–49, 85–87, 37):
- it added two pads under the top plate, 7.5 mm at the far tab and 5.5 mm at the near tab;
- it cut the window, notches and pilots through the pads;
- it made the cradle pilots 7 mm deep.

**Inputs**
- This job: spec.md, design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json, slice_plan.json, log.md and the round-4 review.
- Renders: all 5, regenerated with `tools/render.py` and viewed.
- Assembly: `assembly_check.py` (ESP32 and cradle envelope).
- Skills: fdm-design-rules, material-selection, build123d-cad. library/lessons.md has no entries.

**Outputs are current.**
- `build()` run in memory gives 94469.63 mm³, a 110 × 104 × 40 bbox from (−55, −52, 0) and 1 solid. That matches geometry.json exactly.
- part.stl is watertight (94466.92 mm³).
- `tools/mesh_check.py` re-run gives the committed mesh_check.json.
- The volume is +4839.1 mm³ on round 4 (89630.57), which is the two pads minus the window, notch and boss overlaps (brief: +4.84 cm³). Nothing else moved.
- `cad_checks.py` re-run: 19/19 PASS.

**Method**
- Print frame: upside down, so design Z → print z = −Z and y → −y. The plate is at z 0–4, the near pad z 4–5.5, the far pad z 4–7.5, and the bosses up to z 10.
- Point-in-solid line scans of part.stl at 0.005 mm steps.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 110 × 104 × 40 mm, inside 240 × 200 × 210; `fits_bed: true` |
| 2 | One watertight solid, min Z 0 | PASS | `solids: 1`, `watertight: true`, bbox min z 0.0 |
| 3 | Orientation matches the brief | PASS | Upside down, top plate on the bed (`Rot(180, 0, 0)`, model.py:124). top.png shows both pads rising off the plate inside the box: the far one runs from the −X wall to x −19.4, the near one is x −0.9…29.1. Window, notches and pilots run through both. bottom.png (the bed face) is unchanged from round 4 |
| 4 | Load paths | PASS | The pads thicken the plate where it bends round the tab bosses. That is plate bending along the layers. Tab-screw pull-out puts the boss, pad and plate layers in compression. The pad's edge step is 15 mm from the bosses (13 mm towards the ESP32), at about 27 % of the peak moment (brief) |
| 5 | Bed contact | PASS | **The top plate's outer face prints down.** 10191.7 mm², the same as round 4: the pads are on the inside face, at print z ≥ 4, so they don't touch the bed |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | `overhang_pct` 0.0, `bridges: []`. Each pad is a prism standing on the plate: vertical sides, a flat top at print z 7.5 / 5.5, and nothing printed over a void. The notches, window and pilots are vertical cuts through plate + pad + boss. Round 4's four 0.01 mm "bridges" (notch corners grazing the bosses) are gone, because the notch cutter now runs the bosses' full depth (model.py:89–93) |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS | **Every hole the pads touch.** Scan at y 5, print z 6.5 (far pad): wall to the pilot −55.0…−35.8 (19.2), pilot to window −33.0…−30.8 (2.20). Scan at z 5.0 (near pad): window to pilot 10.5…12.7 (2.19), pilot to pad edge 15.5…29.1 (13.6). Above the near pad the boss wall is 1.84–1.85 (Ø6.5 round Ø2.8), as in round 4. Scans across y: the far pad is ±20.5 at x −34.4; the near pad is −18…20 at x 14.1 (print y, i.e. design −20…18). Between each pilot pair there is 7.2 mm of solid. Notch → pilot strip 1.835 CAD in plate and pads (`cad_checks`; round 4 measured 1.839). Cradle pilot Ø2.8 in a Ø7 boss: 2.1 wall, with 3.0 mm of plate left above the blind end. `thin_wall_warnings: []` |
| 8 | HOLE_COMP; horizontal holes | PASS | `HOLE_COMP` goes into `servo_mount_cutter` (model.py:93), the cradle pilots (:83) and the ring pilots (:99). CAD sizes: window 41.3 × 20.3, notches 4.6 × 2.1, pilots Ø2.8, which print as spec §3's 41.1 × 20.1, 4.4 × 2.0 and Ø2.6. The horizontal openings are unchanged: the jack is a teardrop pointing up in print, and the USB slot has a 45° roof (right.png) |
| 9 | Bottom edges chamfered | PASS (note) | `chamfer_plane_edges(outer, 0.0, 0.4)` (model.py:65). The hole mouths on the bed face rely on `elefant_foot_compensation` 0.2 (slice_plan.json), as in round 4 |
| 10 | Internal corners on load paths | PASS (advisory) | The pad-to-plate edges are sharp 90° steps (3.5 / 1.5 mm). They sit 15 mm from the bosses, where the analyst's step check gives SF ≈ 8 with Kt 2 (brief, "Step at the pad edge"). The notch and window corners are as accepted in round 4 |
| 11 | Fasteners per §4 | PASS | **Tab screws:** M3 × 12 pan head + Ø7 washer, 9 mm into a 10 mm through-pilot. The pad replaces part of the boss length, so the screws can't bottom out (cad_checks: open from Z 0.5 to −10.5). The washers spread the head load against creep. **Cradle:** the M3 × 10 through the 4 mm clamp reaches Z −4, so the 7 mm pilot (Z −10 … −3) gives 1 mm of margin with 3 mm of plate above. That closes round 4 note 1. **Ring:** M3 × 6 + Ø7 washer, 2.5 mm into the 4 mm plate. Each tip ends at Z −2.5, inside the plate, so none reaches a pad |
| 12 | Spec §3 dims are named parameters | PASS | `PAD_T_FAR` 7.5, `PAD_T_NEAR` 5.5, `PAD_FAR`, `PAD_NEAR` (model.py:44–49), all sourced to strength round 4. `CRADLE_PILOT_DEPTH` 7 (:37). These match spec §3's pad row (7.5 / 5.5, min) and the brief's table, which now carries the notch row (+0.2/−0) and the pad and cradle-pilot rows |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG at ≈ 70 °C. `materials_on_hand` is empty: check the spool |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

**The pads against the parts around them** (cad_checks.py, re-run):
- **ESP32.** The near pad stops at y 18, 2 mm short of the WROOM can (y ≥ 20). Its underside, at Z −5.5, is 0.5 mm above the board's 4 mm parts envelope (top Z −6) and 4.5 mm above the cradle frame (Z −10). None of 343 probes over the board's envelope hits base material.
- **Cradle bosses.** All three lie outside both pads (probe ring 0.1 mm outside each boss).
- **Other features.**
  - The 150° ring pilot is 1.85 mm outside the far pad in plan, and its screw stays in the plate.
  - The cable slot is 11.5 mm from the far pad.
  - The jack is at y −28, Z −20, clear of the far pad (|y| ≤ 20.5, Z −4 … −7.5).
- **Base servo.** The pads are cut flush with the window walls, so the MG996R case slides through a 7.5 / 5.5 mm-deep window. The lead root passes through notches cut to the full 10 mm.

## Required fixes

None.

## Notes (not blocking)

1. **Margin over the ESP32.** The 0.5 mm over the board's parts envelope assumes no top-side part under the pad is taller than 4 mm. On a DevKitC only the pin-row solder joints sit there, about 3 mm below the pad (brief). At assembly, check by eye that the board seats with the cradle fitted.
2. **Notch corners.** Round 4 note 2 is still optional: an r 0.5 on the notches' far corners would take the strip from 1.835 to about 2.0 CAD.

## Round 4 → round 5

| Item | Status | How I checked |
|---|---|---|
| Strength round 4: the 4 mm plate round the tab boss | Pads added, printable | #3, #6, #7: prisms on the plate, no overhang, walls round every hole ≥ 2.19 (bosses 1.84) |
| Round 4 note 1: cradle pilot depth | Closed | `CRADLE_PILOT_DEPTH` 7, 1 mm margin, 3 mm of plate left (#11) |
| Round 4 note 2: notch corners | Open, optional | Note 2 |
| Round 4 note 3: notch tolerance in the brief | Closed | Brief table row "Lead notches … +0.2/−0" |
| Round 4 #6: 0.01 mm slivers at the bosses | Closed | `bridges: []` |
| Round 4's passing items | Still pass | Bed face, wall openings, desk holes and pillars are unchanged; the volume change is the pads |

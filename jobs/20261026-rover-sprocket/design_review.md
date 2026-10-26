VERDICT: FAIL

# DFM review, round 2: 20261026-rover-sprocket

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/{iso,top,front,right,bottom}.png, print_requirements.json, rover_frame.py, tools/hobby_parts.py (`d_shaft_bore_cutter`, `gearmotor_dummy`, N20_100RPM), chassis model.py (journal), assembly_check.py/json, round-1 design_review.md and strength.md. The library is empty, so the defaults apply.
Outputs are current: a fresh in-memory `build()` gives 5 502.05 mm³ and 35.777 × 34.52 × 26.5, identical to geometry.json (its `holes` entry still errors; R5). Also read: assembly BUILD_GUIDE.md (step 5, sprockets).
Extra evidence: a probe script that places `gearmotor_dummy(N20_100RPM)` in the sprocket frame, intersects it with `design()`, and runs `is_inside` point tests.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit, 5 mm margin | PASS | 35.8 × 34.5 × 26.5 |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight true, min_z 0 |
| 3 | Orientation | PASS | Outer disc face down, hub up, as the brief says (iso.png, front.png) |
| 4 | Load paths vs layers | PASS (note) | Tooth bending, D-flat bearing and journal bearing all lie in the layer plane. But the Ø10 hub now carries the track load 17 mm from the disc into the journal, so hub bending puts axial stress across the layers. The brief doesn't say so (strength round 1, row 9: SF 8.15 at stall); add a line to the brief |
| 5 | Bed contact | PASS | 526 mm² |
| 6 | Overhangs, bridges | PASS | overhang_pct 0, no bridges. The set-screw pilot is a teardrop |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (note) | Hub (10 − 3.2)/2 = 3.4, and 3.9 at the flat. Tooth 2.7 at the root plus the 0.5 chamfers, about 1.9 at RP 16.18, tip 1.6 (an unloaded tip) |
| 8 | HOLE_COMP, teardrops | PASS | The D-bore comes from `d_shaft_bore_cutter(clearance 0.0, HOLE_COMP 0.2)`: Ø3.2 CAD with the flat 1.1 from the axis, vertical. The set-screw pilot is Ø1.6 + 0.2, horizontal, a teardrop pointing up in print (l.66–68; right.png) |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(s, DISC_HALF, 0.3)` l.58; bottom.png shows the bevel round the disc and teeth |
| 10 | Internal corners on load paths | PASS (note) | The tooth roots have 0.5 × 45° chamfers (l.43–45). At a 0.45 mm extrusion width this prints like the r 0.5 asked for in round 1. The chamfer starts 0.144 mm outside the disc circle (polygon corner at r 12.03), leaving a tiny ledge (R1). The hub-to-disc corner is sharp, but it carries only about a quarter of the moment at the shaft end (R2) |
| 11 | Fasteners | PASS (note) | An M2 set screw in an untapped Ø1.6 printed pilot, assembled once (§4). Its position is wrong: see item 16 |
| 12 | Spec §3 dims are named parameters | PASS | D-bore Ø3.0 / 2.5 printed (D_CLEARANCE 0.0 + HOLE_COMP). HUB_D 10 and RP 16.18 come from rover_frame |
| 13 | Service temp | PASS | 40 °C against about 70 °C for PETG |
| 14 | Lessons | N/A | None recorded |
| 15 | FreeCAD reference | N/A | None |
| 16 | Fits and assembly (cross-part) | **FAIL** | (a) **The hub end hits the N20's output bushing.** HUB_Z0_D puts the hub end at world y 32.0, 0.5 mm off the gearbox face (31.5). But the N20's Ø4 × 0.8 bushing (N20_100RPM boss_d, boss_h) reaches y 32.3. Probe: sprocket ∩ N20 dummy = 1.60 mm³, of which 1.42 mm³ is the bushing inside the hub end (y 32.0–32.3, r ≤ 2.0). assembly_check.py lists the whole motor/sprocket pair as an expected contact, so it can't see this. The rotating hub rubs the stationary bushing (chassis spec §8: "sprocket hubs turn freely"). (b) **The set screw misses the D-flat.** Its pilot is on +X: the point test at (+3, 0, z −14.5) is empty, while −X and ±Y are solid. The D-flat is on +Y: at z −18, (0, +1.3) is solid and (0, −1.3) and (+1.3, 0) are empty. So the screw lands on the round part of the shaft, 90° from the flat, and spec §2 ("onto the shaft flat"), §8 ("set screw bites the flat") and BUILD_GUIDE step 5 ("tighten the M2 set screw onto the shaft's flat") can't be met. top.png shows the flat at −Y after the flip; right.png shows the pilot facing +X |

## Required fixes

1. **Clear the N20 output bushing (rule §3: a running joint needs real clearance).** In the `BORE == "D"` branch only, so the idler stays as it is, cut a Ø4.7 CAD × 1.3 mm counterbore in the hub end: 4.0 bushing + 0.5 running clearance + 0.2 HOLE_COMP, and 0.8 bushing + a 0.5 gap. It opens upward in print, so it adds no overhang. Shaft engagement drops from 9.5 to 8.2 mm, so the strength-analyst should re-check the D-flat bearing. BUILD_GUIDE step 5 presses "until the hub stops 0.5 mm short of the gearbox face", but today the only stop is the bushing itself, and after the counterbore there is none. Give the guide a measurable press depth instead: for example, the disc's inner face 13.5 mm from the wall's outer face, with the motor pushed back against its rear stop. Evidence: the 1.42 mm³ overlap in item 16(a).
2. **Put the set screw on the flat (spec §2 and §8).** Turn the pilot and its teardrop box 90° so the pilot runs along +Y in the design frame, through the flat (3.9 mm of hub wall there). Keep the teardrop point toward −z, which is up in print. Evidence: item 16(b).

## Round 1 fixes checked

1. Clear the face-screw heads: **superseded.** There are no face screws now, but the new hub end meets the N20 bushing instead (fix 1).
2. Teardrop the set-screw pilot: **done** (l.66–68; right.png shows the point up). It is on the wrong side of the shaft (fix 2).
3. Chamfer the bed face: **done** (0.3 mm, l.58; bottom.png).
4. Tooth-root fillets: **done as 0.5 × 45° chamfers** (accepted; R1).

## Recommendations (not blocking)

- R1. Start the root chamfer on the disc circle. Use x = √(DISC_R² − (b + f)²) = 11.744 for the polygon's (DISC_R, ±(b + f)) points, so the CAD root has no 0.144 mm ledge and 99° micro-notch.
- R2. Fillet the hub-to-disc corner with r 1.5. It faces up in print, so it costs nothing.
- R3. GRUB_Y 40.5 puts the edge of the Ø2 screw exactly at the shaft end (y 41.5). At 40.0 it stays 0.5 mm on the shaft if your N20's shaft is a little short.
- R4. Print one sprocket and try the press fit and set screw on the real motor before printing the pair. There is no PETG fit-gauge data yet.
- R5. geometry.json `holes` still fails ("type NoneType doesn't define __round__"). Report it to toolsmith.

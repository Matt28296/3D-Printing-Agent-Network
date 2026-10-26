VERDICT: FAIL

# DFM review: 20261026-rover-sprocket

Reviewer: dfm-reviewer · 2026-10-26 · Inputs: spec.md, design_brief.md, model.py, geometry.json, mesh_check.json, renders/*.png, rover_frame.py, tools/hobby_parts.py (`d_shaft_bore_cutter`, N20_100RPM), assembly_check.py/json. The library is empty, so the defaults apply.

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Bed fit | PASS | 35.8 × 34.5 × 20.0 |
| 2 | One watertight solid, min Z 0 | PASS | solids 1, watertight, min_z 0 |
| 3 | Orientation | PASS | Outer disc face down, hub up (iso.png, front.png) |
| 4 | Load paths vs layers | PASS | Tooth bending and D-flat bearing both lie in the XY layer plane |
| 5 | Bed contact | PASS | 571 mm² |
| 6 | Overhangs, bridges | PASS | overhang_pct 0.2. The only bridge is the grub-hole top (span 0.24) |
| 7 | Walls | PASS (note) | Hub (11 − 3.3)/2 = 3.85 mm, and 5.5 − 1.15 = 4.35 at the flat. Tooth root 2.7, tip 1.6 (< 1.8), but about 1.9 at the pitch radius (16.18) where the knuckle bears |
| 8 | HOLE_COMP, teardrops | **FAIL** | D-bore: `d_shaft_bore_cutter(clearance 0.1, hole_comp 0.2)` gives Ø3.3 CAD with the flat 1.15 from the axis, which prints about Ø3.1 / 2.6 across the flat. That matches spec §3 and is vertical. But the M2 grub pilot (l.56) is a plain round Ø1.8 hole that is **horizontal** in print (front.png shows a round hole in the hub side) |
| 9 | Bottom edges chamfered | **FAIL** | `build()` = `to_bed(Rot(180,0,0)*design())`, with no chamfer. bottom.png shows sharp disc and tooth edges. The teeth run in the link notches with only 0.5 mm side clearance (DISC_HALF 3.5 vs NOTCH_HALF 4.0), and elephant's foot on the bed face eats into that |
| 10 | Internal corners on load paths | **FAIL** | Sharp tooth roots (l.37-44, the polygon tooth unioned onto the disc). Nominal root stress is 10 N × 6.5 mm / (7 × 2.7²/6) ≈ 7.6 MPa. With Kt 2 to 3 at a sharp root that is 15 to 23 MPa, cyclic, against the 25 MPa in-plane placeholder |
| 11 | Fasteners | PASS (note) | An M2 set screw goes into an untapped Ø1.6 printed pilot. This is acceptable for a part assembled once (§4); see R1 |
| 12 | Spec §3 dims | PASS (note) | D-bore Ø3.1 / 2.6 printed (above). Pitch radius RP comes from rover_frame. Note: 0.1 mm diametral and 0.05 mm radial at the flat is a snug fit, not the "press fit" spec §3 calls it. The grub screw and CA do the holding |
| 13 | Temperature | PASS | 40 °C service vs about 70 °C for PETG. The N20 gearbox runs warm; the hub is 0.5 mm from it |
| 14 | Lessons | N/A | None recorded |
| 15 | FreeCAD reference | N/A | None |
| 16 | Assembles with real hardware (cross-part) | **FAIL** | The hub end (Ø11, world Y ±38.5, HUB_GAP 0.5) overlaps the two M1.6 motor face-screw heads on the chassis outer face. Pan heads (dk 3.2, k 1.3) at r 4.5 reach Y ±39.3 and cover r 2.9 to 6.1, so the interference is 0.8 mm. assembly_check.py models no screws and skips the motor/sprocket pair (`if {kind(a), kind(c)} == {"motor","sprocket"}: continue`), so it could not see this |

## Required fixes

1. **Clear the face-screw heads (cross-part with the chassis, fix 6 there).** Pick one:
   - (a) Set the sprocket hub end at least 1.0 mm clear of the heads: HUB_Z0 → −(Y_T − (HALF_W_OUT + 2.3)) = −14.7. Shaft engagement drops from 6.5 to 4.7 mm (BORE_DEPTH 5.2), so the strength-analyst must re-check the D-flat bearing.
   - (b) Put Ø3.8 × 1.5 counterbores in the chassis wall.
   Do not do both. Note that the idler job reuses this model, so its hub moves too, which is harmless.
2. **Teardrop the grub pilot.** Swap the Cylinder at l.56 for a teardrop with its point toward the hub's free end. That is −Z in the design frame and +Z in print, after the 180° flip (rule §2, horizontal holes).
3. **Chamfer the bed face.** After the flip, add a 0.3 to 0.4 mm 45° chamfer on the bed-face edges of the disc and teeth (`chamfer_bottom`, rule §2 and §6). Alternatively, chamfer the outer disc face in `design()` before the teeth notch geometry.
4. **Fillet the tooth roots.** Use r 0.5, the largest that still clears the link: DISC_R = CHORD_IN − 0.5 leaves 0.5 mm of radial room, and the notch is about 3.95 mm long against a 2.7 mm tooth base. Re-run assembly_check afterwards (rule §2, internal corners on load paths).

## Recommendations (not blocking)

- R1. For a thread that survives re-assembly, add an M2 hex-nut trap: 4.0 AF + 0.25 + HOLE_COMP, 1.6 deep, in the hub wall. It fits between the bore (r 1.65) and the hub surface (r 5.5). Otherwise tap the pilot M2.
- R2. The toothed disc centre is 10 mm beyond the end of the N20 shaft and 20 mm from the gearbox face. Ask the strength-analyst to check the overhung radial load (10 N of track pull) on the N20 output bearing and on the 6.5 mm D-bore engagement.
- R3. No fit-gauge data exists for PETG yet. Print one sprocket and test it on the actual motor before printing the pair.

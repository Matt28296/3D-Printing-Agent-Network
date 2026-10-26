VERDICT: PASS

# DFM review (round 3): 20261026-hexapod-femur

Reviewer: dfm-reviewer (independent; did not design the part) · 2026-10-26

**Inputs**
- This job: spec.md, design_brief.md, model.py, cad_checks.py, geometry.json, mesh_check.json, print_requirements.json, slice_plan.json, strength.md (round 1).
- The previous review: round 1. The femur had no round-2 DFM review.
- Renders: all 5, regenerated with `tools/render.py` and viewed.
- Assembly job: assembly_plan.md (B1 table, interfaces), hex_frame.py, BUILD_GUIDE.md, assembly_check.json (`clean: true`).
- Deep review: 01-bought-parts.md (B1, B2, S1) and 05-hexapod-system.md (SYS-5). Also tools/hobby_parts.py.
- library/lessons.md: no entries.

**Probes:** trimesh `contains` on part.stl. Frame F, z up in print; the back face (z 0) is on the bed.

**Outputs are current.**
- `build()` gives 5962.85 mm³ and a 64.9 × 19.0 × 7.0 bbox from (−8, −9.5, 0), the same as geometry.json.
- part.stl is one watertight body.
- `tools/mesh_check.py`, re-run in memory, gives exactly the committed mesh_check.json.
- cad_checks.py: 7/7 PASS, exit 0.

**What is new in round 3:**
- the tibia servo is reversed (B1 option 2, `lead="none"`): tabs on the back face, which is the bed face;
- the window follows the MG90S's own 22.8 × 12.2 body (S1);
- a SYS-5 tie slot at (20, −6).

## Checklist

| # | Item | Result | Evidence |
|---|---|---|---|
| 1 | Fits the bed with a 5 mm margin | PASS | 64.9 × 19.0 × 7.0 mm |
| 2 | Single watertight solid, min Z = 0 | PASS | `solids: 1`, `watertight: true`, `min_z_mm: 0.0`. part.stl is 1 body |
| 3 | Orientation matches the brief | PASS | Flat, with the horn pocket on the bed face (bottom.png). The reversed tibia servo's tabs now seat on that same face, the flattest one on the part |
| 4 | Load paths | PASS (justified) | In-plane bending of the 19 mm deep section runs along the layers. The reversed servo's tab screws go in from the bed face, so a push towards the coxa loads them in pull-out (Z shear). The brief records this with the magnitudes already checked (SF ≥ 6.9 in the drop) |
| 5 | Bed contact | PASS | 707.1 mm² |
| 6 | Overhangs ≤ 45°, bridges ≤ 10 mm | PASS | `overhang_pct` 3.23. The only overhang is the horn-pocket ceiling: span 7.9 at z 2.0, over x −3.95…16.45. The window, pilots and tie slot are vertical through-cuts |
| 7 | Walls ≥ 1.8, none < 0.9 | PASS (note) | Rails 9.5 − 6.4 = 3.1 (x 39.5: solid to ±6.4). Floor under the pocket 5.0 (solid z 2–7). Outer pilot slot to the plate end 2.25 (y 0 row: void 52.55–54.65, end 56.9). Tie slot 2.5 from the edge (void y −7.0…−5.0), 2.65 from the inner pilot slot, 1.85 beyond the pocket's end. `thin_wall_warnings: []`. Under 1.8: the pilot-to-window ligaments, **1.45 mm CAD** each (y 0 row: solid 26.45–27.9 and 51.1–52.55), ≈ 1.65 printed. Round 1 had 1.62, and the 22.8 mm body (S1) took 0.15 at each end. They are solid, above 0.9 and above hobby_parts' 1.5 mm printed minimum for a self-tapper; the MG90S sets them. Strength should confirm |
| 8 | HOLE_COMP; horizontal holes | PASS | Window 23.2 × 12.8 CAD (x 27.9–51.1, y ±6.4). Pilots Ø1.7, slotted 0.4 outward (24.35–26.45 and 52.55–54.65). Pocket +0.7 and clamp Ø2.6 (geometry.json). Tie slot 3.4 × 2.0. Every hole is vertical |
| 9 | Bottom edges chamfered | PASS | `chamfer_plane_edges(f, 0.0, 0.4)` (model.py:49). The window's bed-face rim is where the reversed case enters; `elefant_foot_compensation` 0.2 (slice_plan.json) covers it |
| 10 | Internal corners on load paths filleted | PASS (advisory) | The window corners are square, as the servo needs, in the low-moment zone (round 1). The tie slot's corners are square at x 20. Strength had SF ≥ 25 there before the slot, and the brief says the slot takes 11 % of the section's second moment; strength to confirm |
| 11 | Fasteners per §4 | PASS | Tibia tab screws: M2 × 8 self-tapping from the back face, through the 2.5 mm tab, 5.5 mm engaged. The tip stops 1.5 mm short of the front face, which the tibia passes 3.1 mm away. The tab tips (x 55.6, y ±6.1) land on solid plate (it runs to x 55.91 at y ±6.1, z 0.05). Clamp: M2 × 12 with a Ø6 washer on the flat front face, snug (spec §2) |
| 12 | Spec §3 dimensions are named parameters | PASS (advisory) | L_F 45.0 (hex_frame.py:55). Window: SERVO + `CLR, END_CLR` (model.py:32) + `HOLE_COMP` (:27). `HALF_W` 9.5 for the 3.1 rails (:28, commented). Floor 5.0 = T_F 7 − HORN_DEPTH 2. `CLR, END_CLR` has no comment, but the brief's table gives the source |
| 13 | Service temperature ≥ 20 °C below softening | PASS | 40 °C against PETG ≈ 70 °C. Before slicing: `materials_on_hand` in config/printer.json is empty |
| 14 | Lessons in library/lessons.md | N/A | No entries |
| 15 | FreeCAD reference | N/A | No inputs/ folder |

## Required fixes

None.

## Round 1 notes checked

Round 1 had no required fixes.
- **Centre-screw stack:** spec §2 now says M2 × 12, or M2 × 10 if the shaft thread bottoms before 6.5 mm, driven snug (01 S2).
- **Tab-screw pull-out:** checked by strength round 1 (SF ≥ 6.9 in the drop, per the brief).
- **Lead exit through a window with ≈ 0.1 mm end clearance:** solved by the reversed mount. The lead stays behind the femur and no notch is needed (B1 table).

## Recommendations (not blocking)

- **Strength re-check:**
  - the 1.45 mm CAD pilot ligaments (round 1 used 1.62);
  - the tie slot at x 20;
  - the reversed tab screws in pull-out, at the round-3 mass.
- **Comment:** add a source comment on `CLR, END_CLR` (model.py:32).
- **Print layout:** slice_plan.json prints 6 per plate. Round 2's slice of six took 3.9 h against spec §7's 3 h. The brief proposes 4 + 2, which is the slicing stage's call. There is no DFM objection to either layout.

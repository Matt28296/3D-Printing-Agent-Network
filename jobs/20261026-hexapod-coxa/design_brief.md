# Design brief: Coxa bracket (×6)

Job: 20261026-hexapod-coxa · design-lead · 2026-10-26 · round 3: strength round 1, DFM round 2 and the deep review (B1, B2, SYS-5, SYS-6) · round 4: DFM round 3 and strength round 3 (below)

## Material
PETG for every hexapod part: tough, low creep under the servos' constant holding load, prints on an open-frame MK3S, softening point ~70 °C well above the 40 °C service. No library data yet, so strength uses the placeholder allowables (25 MPa in-plane, ×0.5 across layers).

## Orientation
Horizontal plate on the bed (the horn pocket on the bed face, bridge 7.9 mm), vertical plate standing with its window roof up.
- The hub's bending runs along the layers.
- The vertical plate's out-of-plane bending runs **across** the layers, at the posts beside the window and at the floor band under it. The orientation can't change: the horn pocket must be on the bed. So round 3 gives the plate the section strength round 1 asked for (below).
- Horizontal holes (pilots, reliefs, tie slot, lead notch) all get 45° tops. The lead notch's top was a flat 1.41 mm ledge anchored on one edge only, not a bridge (DFM round 3); round 4 gives it a 45° roof. The only real bridge is the horn pocket's 7.9 mm ceiling. mesh_check's other entries are sub-millimetre: the pilot slots' far-end arcs (0.17 mm span at z 20.85), which bridge themselves, and a 0.1 mm² patch at z 7.99 (DFM round 3: negligible).

## Concept
L-shaped bracket under the coxa MG90S horn: a hub plate round the horn and an arm out to a vertical plate that carries the femur MG90S, its axis horizontal and tangential, 32 mm out from the coxa axis. Strength round 1's required changes, all modelled as checked (one set, lowest SF 3.19):

| # | Change | Model |
|---|---|---|
| 1 | Vertical plate T_V 4.5 → **10**, grown towards −y (y −23.5 … −13.5); posts ≥ 12.5 → **13 mm**, grown outward (plate x 1.9 … 51.1); arm and hub to y −23.5; keep the R1 T-bone reliefs and the full-length gusset | `T_V` (hex_frame), `POST_W`, `VPLATE_X`, `HUB`, `ARM_Y`, `RELIEF_D`, gusset over `VPLATE_X` with the arm's far corners squared (r 0.5) |
| 2 | Femur-servo tab screws M2 × 8 → **M2 × 10** (7.5 mm engaged) | spec §2, BUILD_GUIDE |
| 3 | T_C 5 → **8** (6 mm floor under the horn) + **M3 penny washer Ø10 × 1** under the M2 centre screw | `T_C` (hex_frame), spec §2. Z_F = T_C + 12 = 20 |
| 4 | **45° ramp ≥ 8 mm** where the plate's inner end meets the hub | `RAMP` 8: foot at x −6.1 on the hub (corner radius `HUB_R` 2 so the foot lands on the hub) |

DFM round 2:
- fix 1: the R1 reliefs;
- fix 2: the full-length gusset with squared arm corners;
- fix 3: the comments now match `build()`, the docstring gives the femur plane as −0.9 … 6.1 and the arm's 5.6 mm clearance, and the horn screw is now right.

## Round 4: DFM round 3 and strength round 3

The user approved one more round with exactly the reviewers' fixes:

| # | Review | Change | Model / file |
|---|---|---|---|
| 1 | DFM round 3, fix 1 | **45° roof on the lead notch:** the right triangle (38.1, 22.2), (39.51, 22.2), (38.1, 23.61) in the x–z plane, cut through the plate (y −24.5 … −12.5). The notch is 4.4 at its end wall, opening at 45° to 5.8 at the window face. mesh_check's z 22.2 "bridge" is gone | `NOTCH_END_X`, `NOTCH_TOP`, `NOTCH_ROOF`, cut with `_prism_y`. Volume 23322.91 → 23312.97 mm³ |
| 2 | Strength round 3 | **Print solid: 100 % infill**, no geometry change. Lowest SF 2.91 → **4.22** (post roots, drop); horn clamp 4.92 | `print_requirements.json`: `fill_density` 100, pattern rectilinear (PrusaSlicer's solid pattern: gyroid isn't meant for 100 %, and the arm-claw-pinion uses rectilinear at 100 %) |
| 3 | Strength round 3 | **Proof test:** leg test first, then 2.8 kg on the femur-servo horn with the coxa servo clamped shaft up, a 6 N side push, the drop | spec §8 |
| 4 | DFM round 3 (print layout) | **2 brackets per plate**, 3 plates | spec §7 |

The roof changes no strength section (DFM round 3):
- its nearest point, (39.51, 22.2), is 2.25 mm from the moved pilot's hole, teardrop included;
- the 1.35 mm ligament at the notch's end wall is unchanged;
- the post keeps 11.6 mm at z 22.25, so the pilot row stays its smallest section.

**For slicing:** `slice_plan.json` is the slicing stage's file and still says 50 % gyroid and 6 copies. It needs 100 % rectilinear and 2 copies per plate.

## B1: the femur servo's lead (option 1)
The lead leaves the femur servo's case at its shaft end (outboard here). A closed window can't pass it.

**Option 2 (reversed) doesn't fit this plate.** The femur's back face would sit 12.6 − (2.5 + T_V) = **0.1 mm** beyond the plate's far face with T_V 10, so the femur would rub the plate. A thinner plate would need posts over 18 mm (strength's table) and a new check.

**So option 1:**
- `servo_mount_cutter(..., lead="notch_shift_pilot")`: a 4.4 × 1.6 notch at the window's outboard end, with a 45° roof since round 4 (`NOTCH_ROOF`), and the outboard pilot 1.3 mm further out (ligament 1.35 mm CAD, ≈ 1.55 printed, which hobby_parts requires to be ≥ 1.5).
- The builder files that tab's slit to 2.1 mm: **6 tabs for the robot**. The other two windows (bottom plate, femur) use option 2, so none of their 12 tabs needs filing.
- The 13 mm posts leave 9.4 mm past the moved pilot, so the plate needs no lengthening.
- The notch lies on the window's centreline at mid-height. That is 4 mm above the post root, the critical section, and it takes 1.6 of the post's 13 mm only at the pilot row (strength: SF 17.8 there in the drop).

## Critical dimensions
| Feature | Nominal | Tolerance | Fit | Compensation | Source |
|---|---|---|---|---|---|
| Coxa axis → femur axis | 32.0 radial | ±0.3 | leg geometry | — | hex_frame `L_C` |
| Femur axis depth | 20.0 below the back face | ±0.3 | leg geometry | — | hex_frame `Z_F` |
| Vertical plate / posts | 10.0 / 13.0 | +0.3/−0 | strength | — | strength round 1 |
| Horn floor | 6.0 | ±0.2 | strength | — | strength round 1 |
| Femur-servo window | 22.8 × 12.2 + 0.2 end / 0.4 side | +0.3/−0 | 0.1 end / 0.2 side clearance printed | HOLE_COMP +0.2 | default from fdm-design-rules (no library row) |
| Lead notch | 4.4 at the end wall, opening at 45° to 5.8 at the window face (4.2 + HOLE_COMP at the end wall); 1.5 + 0.1 past the case end | +0.3/−0 | lead passage | HOLE_COMP | hobby_parts MG90S lead data; 45° roof from DFM round 3 |
| Pilots | Ø1.5 + HOLE_COMP teardrops, outboard one +1.3 mm | ±0.2 | M2 self-tapping | HOLE_COMP | default from fdm-design-rules |
| Clamp hole | Ø2.4 + HOLE_COMP | +0.2 | M2 clearance | HOLE_COMP | default |

`cad_checks.py` proves each row on the built solid (17 checks, exit 0).

## Parameters exposed by model.py
HOLE_COMP, CLR, END_CLR, LEAD, POST_W, WIN_X, VPLATE_X, HUB, HUB_R, ARM_Y, WIN_HALF, ROOF, NOTCH_END_X, NOTCH_TOP, NOTCH_ROOF, VPLATE_H, GUSSET, RAMP, RELIEF_D, TIE_SLOT, TIE_XZ, CORNER_CUT, HUB_ARM_FILLET, BED_CHAMFER (+ hex_frame.py: L_C, T_C, T_V, Y_F, Z_F)

## Lead tie point (SYS-5)
A 1.8 × 3.2 slot with a 45° roof through the outer post at (x 47.5, z 30): above the pilot row, where the post carries almost no load (strength's sections are at the root and the pilot row).
- The femur lead (from the case's outboard end, behind the plate) and the tibia lead are tied there.
- They then run round the outside of the arm to the bottom plate's tie slot, with a 30 mm free loop, never across the hub (BUILD_GUIDE §3, step 7).

## Clearances (assembly check, round 3)
- The femur's back face is 12.6 mm from the plate's +y face.
- The arm clears the femur's plane by 5.6 mm.
- The femur swings −70 … +90° clear.
  - The reversed tibia servo's case (behind the femur, deep review B1 on the femur) passed within 0.16 mm of the plate's outer top corner at femur −40 … −60°.
  - The 6 mm 45° `CORNER_CUT` on that unloaded corner gives ≥ 3.3 mm there and ≥ 0.76 mm everywhere in the sweep.

## SYS-6: the leg hangs on the coxa servo's shaft
- **Proof test:** in spec §8 (with the assembly spec's version) and noted in BUILD_GUIDE §4. In the round-3 walking stance the shaft sees 194 N·mm at 812 g (163 at the review's 683 g; 187–203 in round 2's stance), and 216 N·mm at round 4's 906 g.
- **Cheap extra support (proposed, not modelled):** a bump arc on the bracket's back face, r 12–15 mm on the outboard side, 3.6 mm tall, so it sits 0.5 mm under the bottom plate (4.1 mm gap).
  - It clears both tab-screw heads (r ≤ 10.9 and ≥ 16.9) at every coxa angle.
  - It only touches when the shaft bends (drop, overload), and then carries the moment at r ≈ 13 mm instead of the servo's single bearing.
  - It needs the bottom plate's outboard margin grown about 2 mm to give it a landing.
  - The gap must be set at assembly (PTFE tape), because the horn-seating tolerance (±0.5 mm) is larger than the gap.
  - Decide after the leg proof test. A full second support opposite the horn would need a new body (deep review).

## Risks
- **Mass:** the bracket is 29.6 g solid (round 2: 10.3). Printed at 100 % it takes about 31 g of filament (strength round 3's layer model, calibrated to the slicer's weights; 22 g at 50 %), and the robot is about **906 g** with the bottom plate's round-4 changes (strength round 3). Femur / knee torque in the chosen stance at 906 g: 43 / 44 % of stall at 30 mm stride (assembly plan, "Stance").
- **Print time:** **2 per plate**, 3 plates (spec §7). At 100 % infill a plate of 2 (about 62 g) comes to roughly 4.9–6.3 h, scaled by filament mass from the round-2 hexapod slices (9.9–12.6 g/h), against `max_print_hours` 6. The slice decides; if it runs over, relaxing §7 is the user's call.
- **Window roof would cut the pilots on a short side:** roof on the long side (hobby_parts refuses the other).
- **Arm in the femur's plane:** arm kept at y ≤ −6.5.
- **Re-entrant hub/arm corner on the foot-moment path:** r2.5 fillet; hub step: 45° ramp.
- **Lead notch beside a moved pilot:** ligament 1.35 mm CAD. Check the slit on one servo before filing six.
- **For the strength re-check:** the geometry is the checked set plus the B1 notch, the moved pilot, the tie slot and the corner cut. The femur now carries the tibia 9.5 mm closer (femur option 2), which lowers the leg's torsion.

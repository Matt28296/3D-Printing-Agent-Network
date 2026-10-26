VERDICT: NEEDS_TEST

# Strength check: 20261026-hexapod-coxa (×6), round 4

Independent strength-analyst · 2026-10-26 · `python3 jobs/20261026-hexapod-coxa/strength_calc.py` (about 45 s;
needs build123d, trimesh and scipy, like `cad_checks.py`: CAD venv `/home/claude/.venv-cad`)

**Every row passes. The lowest SF is 4.22 (required 3)**, at the post roots in the 20 cm drop. The horn clamp, which
failed round 3 at 50 % infill (2.91), is at **4.92** now that the bracket prints solid.

- **The verdict is NEEDS_TEST, not PASS, only because the allowables are placeholders.** `library/materials.csv` has
  no PETG row.
- **The proof test in spec §8 is the one this check needs, and it stays as written.** Its 2.8 kg hang is exactly
  2 × walking at the round-4 mass (2.81 kg; see "Proof test").

## Round 3's required changes: all made

| Round 3 required | Round 4 | Checked |
|---|---|---|
| Print solid: `print_requirements.json` min `fill_density` 50 → 100 | `fill_density` 100, `fill_pattern` rectilinear (PrusaSlicer's solid pattern; gyroid is not meant for 100 %) | The layer model reads it: every section is now solid (as printed / solid = 1.000). Rows 2–34 |
| Spec §8's proof test replaced | spec §8 is round 3's test word for word | 2.8 kg = 2 × walking at 907 g (below) |
| DFM round 3, fix 1: 45° roof on the lead notch | `NOTCH_ROOF`; the volume fell by 9.94 mm³, exactly the roof prism (½ × 1.41² × 10 mm). Nothing else moved | New rows 18–20 |

Every result matches round 3's check of this change set at 906 g, to within the 1 g mass difference. Examples: clamp
4.92, post roots 4.22, tab screws 4.38, band 6.90, washer bearing 6.13.

## Load cases

The same block as round 3 and the bottom plate's round-4 check. `strength_calc.py` rebuilds it from:
- `hex_frame.py`: round-3 frames, walking stance femur −4.7°, tibia −14.0°, IK gait;
- `tools/hobby_parts.py`: MG90S, 216 N·mm stall, 13.4 g;
- the five `model.py`, built with build123d;
- each `print_requirements.json`.

**Robot mass: 907 g (8.90 N). This is my number.**
- **Printed parts: 400 g.** A slicer-like layer model, × 1.045 (calibrated on the four round-2 slices):
  - bottom plate 96.2 g;
  - deck 36.2 g;
  - 6 coxae × 30.9 g (100 % rectilinear);
  - 6 femurs × 6.6 g;
  - 6 tibias × 7.1 g.
- **Bought parts: 507 g.** Round 3's itemised list (BUILD_GUIDE §1), plus 1.3 g for the round-4 tab hardware: 12 M2 × 14
  screws instead of × 12, and Nyloc nuts instead of plain ones.
- **Against the plan's 906 g.** That is round 3's estimate of this same robot. The 1 g difference is the hardware.

| Case | Foot force | Poses | Duration, SF |
|---|---|---|---|
| Sustained | share × weight, up to **3.87 N** up | Every planted foot of every tripod-only frame of the 30 and 40 mm IK gaits, plus both neutral tripods: 102 feet. Shares solved exactly with the CG anywhere within ±3 mm of the centre: max **0.435** | sustained, 4 |
| Walking | × 2: up to **7.74 N** | same | cyclic, 4 |
| Foot friction | 3.87 N up + µ 0.5 in any horizontal direction, all servos within stall | the stance plus the 6 poses where a joint reaches its gait extreme | cyclic, 4 |
| Shove | 3 N in any horizontal direction, with 0 … 3.87 N up | same 7 poses | short-term, 3 |
| Servo stall (spec: one at a time) | Vertical, either way, until the first servo stalls. Or radial/tangential on top of 3.87 N up, until the first servo stalls. At the stance: 9.6 N vertical, 4.0 N tangential, 3.1 N radial. Plus 216 N·mm straight into the horn pocket | same 7 poses | short-term, 3 |
| 20 cm drop | Up to the back-drive cap, femur and knee at 2 × stall = 432 N·mm: **19.2 N** up at the stance (18.9–19.3 N over the 7 poses), with radial friction up to µ 0.5 within the cap | same 7 poses | short-term, 3 |
| Assembly | M2 horn-clamp screw snug, 0.05 N·m ≈ 125 N | — | short-term, 3 |

- Service temperature 40 °C against PETG's ≈ 70 °C: OK.
- Spec §4's table still states the 683 g basis (2.90 / 5.80 N); its notes give the later masses. These rows use the
  script's own loads at 907 g, as round 3 did.

## Assumptions

- **Printed construction**, from `print_requirements.json` on the 0.20 mm QUALITY profile:
  - Perimeter band 0.45 + 3 × 0.407 = **1.67 mm**; top and bottom skins 5 × 0.2 = **1.0 mm**.
  - The core is **100 % rectilinear infill**. At 100 % PrusaSlicer spaces the lines to fill the region completely,
    the same solid extrusion as the skins, which round 3 already counted as solid. So every section is solid as
    printed: the layer model gives as-printed / solid = 1.000 for the post roots, and a 235 mm² plug under the
    horn washer.
  - The placeholder in-plane allowable (25 MPa) is already knocked down. It covers solid infill's ±45° raster.
- **Section properties from the build123d solid.** The rastered sections agree with build123d's exact areas: post
  roots 283.0 against 283.0 mm², roof row 247.0 against 246.9 mm².
- **Femur servo on its two tab screws** (rounds 1–3's model):
  - it is a rigid body on the two screws;
  - its rocking moment splits between the posts by width;
  - yaw acts as opposite y-forces at the screws, 6.4 mm above the post roots;
  - the radial force bends each post in plane;
  - the in-plane moment and any pull load them axially.
  - The pilot row takes the rocking moment only when the tab pivots on its upper edge (z 26.1).
  - The case gets no credit in the window (0.1–0.2 mm clearance).
- **New in round 4: the outer post just above the notch roof** (z 22.3, 0.1 mm above the roof's lowest corner).
  - It is 11.65 mm wide with no hole. The pilot row below it has a net 9.5 mm (probed; 9.6 rastered).
  - It lies above the screw line (z 20). So the screw forces, the radial force and the axial loads all enter below
    it, and it carries only what the outer tab presses on the post above it.
  - Every such force is put at the tab's upper edge, 3.8 mm above the section. That means half the rocking
    couple's edge force (an upper bound: the outer post is the narrower, so it takes less) plus the whole yaw force.
  - Kt 2.5, the skill's sharp-corner value, at the roof's corner on the end wall. That corner is an obtuse 135°.
    Before the roof it was 90°.
- **Horn clamp** (round 3's model):
  - The joint tips on the horn hub's edge (r 3.6).
  - The screw holds the horizontal moment over 3.6 mm, plus any pull-off.
  - Capacity is the Ø10 washer's plug shear on the r 5 cylinder through the whole hub (z 0–8), against the
    interlayer shear allowable: 235 mm², 1470 N.
- **No bolt preload is counted for strength** (fdm-design-rules: PETG creeps). Preload enters only the assembly
  row.
- **The drop cap is an assumption.** A powered MG90S back-drives at about 2 × stall (spec, DR05). The drop test is on
  carpet.
- **The legs' own inertia in the drop is ignored.** It acts against the foot force at the horn and the posts, so this
  is conservative.
- **Kt:** 2.0 at the R1-relief post roots, holes and the band; 1.5 at the hub; 2.5 at the roof's corner.

## Allowables and sources

`library/materials.csv` has no rows, and `inputs/` has no printed-specimen datasheet. So these are the strength-checks
**placeholders**, and NEEDS_TEST is the best verdict possible.

| Quantity | Value (MPa) | Source |
|---|---|---|
| Tension or bending along the layers (XY) | 25 | placeholder, PETG |
| Across the layers (Z) | 12.5 | 0.5 × in-plane (placeholder) |
| Shear, in-plane / interlayer | 12.5 / 6.25 | 0.5 × normal (as every earlier hexapod, arm and rover check) |
| Bearing (compression) | 25 | in-plane value |
| 100 % rectilinear infill | as solid | see "Assumptions" |
| E | 1800 | placeholder |

## Results: the round-4 design as specified (as printed, 100 % rectilinear)

| # | Case | Section | Dir | Stress | Allow. | SF | Req. | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | coxa stall 216 N·mm | horn arm on the pocket wall (perimeters) | XY | 1.59 | 25.0 | 15.74 | 3 | OK |
| 2 | sustained 3.87 N | horn clamp: Ø10 washer pulled through the floor | Z shear | 0.27 | 6.25 | 23.41 | 4 | OK |
| 3 | walking 7.74 N | horn clamp | Z shear | 0.53 | 6.25 | 11.70 | 4 | OK |
| 4 | foot friction | horn clamp | Z shear | 0.47 | 6.25 | 13.37 | 4 | OK |
| 5 | shove | horn clamp | Z shear | 0.62 | 6.25 | 10.04 | 3 | OK |
| 6 | stall | horn clamp | Z shear | 0.68 | 6.25 | 9.25 | 3 | OK |
| 7 | drop 19.2 N | horn clamp (screw force 299 N; plug 1470 N) | Z shear | 1.27 | 6.25 | 4.92 | 3 | OK |
| 8 | drop | Ø10 washer bearing (299 N over 73 mm²) | bearing | 4.08 | 25.0 | 6.13 | 3 | OK |
| 9 | sustained | post roots z 13.7 (R1 reliefs, Kt 2.0) | Z | 0.56 | 12.5 | 22.25 | 4 | OK |
| 10 | walking | post roots | Z | 1.12 | 12.5 | 11.13 | 4 | OK |
| 11 | foot friction | post roots | Z | 1.37 | 12.5 | 9.13 | 4 | OK |
| 12 | shove | post roots | Z | 1.80 | 12.5 | 6.93 | 3 | OK |
| 13 | stall | post roots | Z | 2.33 | 12.5 | 5.35 | 3 | OK |
| **14** | **drop** | **post roots** | **Z** | **2.96** | **12.5** | **4.22** | **3** | **OK** |
| 15 | shove | post net section at the pilot row z 20 (Kt 2) | Z | 1.42 | 12.5 | 8.78 | 3 | OK |
| 16 | stall | pilot row | Z | 2.05 | 12.5 | 6.10 | 3 | OK |
| 17 | drop | pilot row | Z | 0.63 | 12.5 | 19.89 | 3 | OK |
| 18 | shove | **outer post above the notch roof z 22.3, 11.65 wide (round 4, Kt 2.5)** | Z | 1.04 | 12.5 | 11.97 | 3 | OK |
| 19 | stall | notch-roof section | Z | 1.19 | 12.5 | 10.48 | 3 | OK |
| 20 | drop | notch-roof section | Z | 0.25 | 12.5 | 50.02 | 3 | OK |
| 21 | sustained | femur-servo tab screw pull-out (M2 × 10, 7.5 mm engaged) | Z shear | 0.28 | 6.25 | 22.33 | 4 | OK |
| 22 | walking | tab screw pull-out | Z shear | 0.56 | 6.25 | 11.16 | 4 | OK |
| 23 | foot friction | tab screw pull-out | Z shear | 0.70 | 6.25 | 8.97 | 4 | OK |
| 24 | shove | tab screw pull-out | Z shear | 0.93 | 6.25 | 6.71 | 3 | OK |
| 25 | stall | tab screw pull-out | Z shear | 1.25 | 6.25 | 4.99 | 3 | OK |
| 26 | drop | tab screw pull-out | Z shear | 1.43 | 6.25 | 4.38 | 3 | OK |
| 27 | drop | tab pilot bearing | XY | 1.84 | 25.0 | 13.56 | 3 | OK |
| 28 | drop | moved outboard pilot → lead notch, 1.35 mm CAD ligament | Z shear | 0.18 | 6.25 | 35.10 | 3 | OK |
| 29 | walking | band under the window z 13.0, through the reliefs (Kt 2) | Z | 0.72 | 12.5 | 17.30 | 4 | OK |
| 30 | shove | band | Z | 0.96 | 12.5 | 13.00 | 3 | OK |
| 31 | drop | band | Z | 1.81 | 12.5 | 6.90 | 3 | OK |
| 32 | walking | hub + plate section x 6, outboard of the horn pivot (Kt 1.5) | XY | 0.23 | 25.0 | 108.80 | 4 | OK |
| 33 | drop | hub + plate section x 6 | XY | 0.56 | 25.0 | 44.65 | 3 | OK |
| 34 | assembly, snug 125 N | horn clamp: washer pull-through | Z shear | 0.53 | 6.25 | 11.76 | 3 | OK |

**Lowest SF 4.22 (required 3), at row 14.**

**The roof is not a weak point.** Its section sits above the screw line and is wider than the pilot row. At its
worst, the stall case, it is at 10.48. Every section the lead notch touches is well clear of 3: pilot row ≥ 6.10,
notch-to-pilot ligament 35.10, roof ≥ 10.48.

## Advisory (not in the verdict)

| Case | Section | SF |
|---|---|---|
| Drop with friction in **any** direction (tangential up to the coxa servo's back-drive), beyond the spec's radial case | post roots | 2.23 |
| same | femur-servo tab screw pull-out | 2.16 |
| same | horn clamp / notch roof | 3.90 / 20.79 |
| **Any combination** of stalled servos at once, beyond the spec's one-at-a-time case | pilot row | 3.00 (2.998) |
| same | post roots / notch roof / tab screws / clamp | 3.90 / 4.70 / 3.83 / 6.58 |
| Horn clamp screw driven "firm", 0.1 N·m (250 N) | washer pull-through | 5.88 |
| **Sliced as `slice_plan.json` still says (50 % gyroid)** | horn clamp in the drop (plug 139 mm² equivalent, not 235) | **2.91** |

- **The beyond-spec rows are round 3's residual risk.** Printing solid doesn't change them.
  - A tilted landing can drive a corner leg's foot sideways. The tilted drop in the proof test settles that risk.
  - If it cracks the post roots or pulls the tab screws, the next step is the coxa brief's second support: the
    bump arc under the bottom plate, or a support opposite the horn. More plate wouldn't fix that load path.
- **The last row is for the slicing stage.** `slice_plan.json` still says 50 % gyroid and 6 copies. The slice must
  follow `print_requirements.json` (min `fill_density` 100, `fill_pattern` rectilinear), which the validator
  enforces. Otherwise the clamp is back below 3.

## Proof test

The verdict is NEEDS_TEST (placeholder allowables). **Spec §8's proof test matches this check and needs no change.**

1. **Leg test first:** as in the assembly spec §8 (deep review SYS-6).
2. **Static, bracket:** the femur off, the coxa servo clamped shaft up, **2.8 kg** hung from the femur servo's horn on
   its shaft axis, for **1 min**.
   - At 907 g, 2 × walking at the stance foot is 15.5 N.
   - Hung from the horn instead, the same loads need 27.6 N for the post roots, 25.7 N for the tab screws and 27.0 N
     for the clamp. That is 2.81 kg; the spec's 2.8 kg is 1.00 × that.
   - At 2.8 kg (placeholder allowables): post roots SF 5.56, tab screws 5.22, horn clamp 6.02.
3. **Side push:** 6 N at the foot tip, each way, 10 s, servos powered in the walking stance. That is 1.5 × the
   4.0 N a coxa stall puts there.
4. **Drop:** the body-bottom spec §8 drop test, on carpet, on spare coxa servos or after step 1 has passed.

Pass, as spec §8 states:
- no whitening or cracks at the post roots, R1 reliefs, pilots, lead notch and its roof, gusset tip, ramp, or the
  floor round the washer;
- no gap over 0.2 mm (feeler gauge) between the bracket and the horn while loaded;
- after unloading, the horn returns within 0.3 mm of where it started (step 2) and the foot within 0.5 mm
  (steps 3–4).

## For slicing and print time (context)

- 30.9 g printed per bracket, against 22.1 g at 50 %.
- Two per plate at 100 % is about 4.9–6.3 h against the 6 h limit (spec §7, the brief's estimate). The slice decides
  that.
- The drop, the governing case, is capped by the servos and doesn't depend on mass.

## Servo torques (system context; not a printed-part row)

At 907 g, with the CG anywhere within ±3 mm, static over the 30/40 mm gaits:
- femur 101 N·mm (47 % of stall);
- knee 116 N·mm (54 %).

With × 2 walking that is 202 / 231 N·mm: the knee passes stall at the 40 mm stride. The coxa shaft sees 226 N·mm
static, 452 walking and 1075 in the drop. `stance_torques.json` (906 g, CG at the centre) has 92 / 96 at the 30 mm
stride and 97 / 109 at 40 mm. Walk at the 30 mm stride the plan chose, and watch the case temperatures (assembly
§8).

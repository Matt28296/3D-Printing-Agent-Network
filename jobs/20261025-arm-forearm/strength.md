VERDICT: FAIL

# Strength check: 20261025-arm-forearm (round 5, independent re-check)

strength-analyst (independent review: I did not design this part) · 2026-10-26 ·
`python3 jobs/20261025-arm-forearm/strength_calc.py` (plain Python, no build123d, about 10 s). It reads every link's
`model.py`, `tools/hobby_parts.py`, the claw's `claw_frame.py`, each part's `geometry.json` and the assembly's
`torque_budget.json`, sweeps 47 170 arm poses and prints the tables below.

## Summary

- **FAIL.** Lowest SF **1.71** (3 required): the two window rails beside the MG90S window, at the window's far end,
  under the yaw-stall sweep (pose s180 e-135 w-30, contact at the fingertips). The far MG90S tab screw also fails
  pull-out under the yaw stall: SF **2.40**.
- **The MG90S screw strips** (1.34 mm CAD at the lead end, 1.45 mm at the far end) pass every spec §4 case and every §8
  test. Their lowest SFs are **4.75** (lead end) and **5.19** (far end), both tear-out under the yaw-stall sweep. The §8
  first-print check (screws driven snug) gives 9.87 and 10.28. The round-4 SG90 row ("pilot-to-window ligament 1.80
  printed") is replaced by the strip table below.
- **Changes that pass** (details under "Required changes"):
  1. ribs on the back face along both rails, 6 mm deep (SF 4.29; 4 mm gives 3.30);
  2. a back-face boss under the far MG90S pilot and an M2 × 16 there, 13.5 mm engaged (SF 3.41).
- With both changes every row reaches its required SF. The best verdict is then NEEDS_TEST, because the allowables are
  placeholders.
- **Proof test:** §8 (2) as written loads the rails to 0.21 × and the far tab screw to 0.09 × their yaw-stall values.
  The replacement is under "Proof test".

## What changed since round 4

**Design changes this round**

- Wrist servo MG90S (216 N·mm), window 23.2 × 12.8 CAD at x 72.9–96.1.
- Lead notch at the shaft end, with the lead-end pilot moved 1.3 mm out to x 99.7. The far pilot is at x 70.6.
- The strips measured by the DFM review (round 4, on sections of `build()`):
  - lead end, notch end wall to the moved pilot: **1.340** CAD;
  - far end, window end to the far pilot: **1.450** CAD.
- The forearm is fitted 60° below the upper link (SYS-03), so the elbow window is -150 … +30. The sweep covers it.
- The claw and camera: 224.1 g beyond the wrist horn with solid parts. This is torque_budget's "camera, solid" upper
  bound; its sliced estimate is 208.6 g.
- The camera's sideways weight (SYS-04) acts in every pose: 108 N·mm about the wrist servo's case top and 161 N·mm about
  the elbow servo's.
- Elbow clamp M3 × 14 + Ø9 × 0.8 washer, 4.6 mm into the spline (01 S2).

**Method changes in this review**

- **New pose model.** The pose model is my own, but it reproduces `torque_budget.json` exactly:
  - end effector 224.1 g;
  - overhung moments 239 / 161 / 108 N·mm;
  - 692 N·mm on the base horn with the arm straight out.
- **Stall torque.** MG996R stall 1079 N·mm (11 kgf·cm datasheet, deep review 01 N1); the specs say 1000.
- **Contact points.** Yaw-stall and hand-push forces act at the fingertips and at either end of the camera (±51 mm off
  the claw axis). The fingertips governed every check on this part.

**Why the lowest SF fell from 3.78 (round 4) to 1.71**

1. **Window rails.** Round 4 treated the rails as advisory. It reasoned that the servo case, bolted at both tab rows,
   carries the out-of-plane moment across the window.
   - It cannot. Each MG90S tab has one screw on the plate's centre line, so a tab row is a pin about the plate's y axis.
     It cannot pass a moment.
   - By statics, the force at the near tab (x 99.7) must travel back to the far end through the rails.
   - At the window's far end (x 72.9) the rails therefore carry (99.7 − 72.9) / (99.7 − 70.6) = **0.92** of the moment
     at the far pilot row.
   - A preloaded tab pressing on the face would help a little. A tab-spring estimate gives 0.77 of the moment (SF 2.04,
     advisory), which still fails.
2. **Torsion split between the two tabs.** Each tab has a single screw and pries about its long edge (lever 6.1 mm).
   - The far tab's path is stiffer than the near tab's, which runs through the rails.
   - I put 70 % of the torsion on the far screw and 50 % on the near one. Round 4 split it equally.
3. **Loads.** The stall is now 1079 N·mm, and the end effector is 224 g instead of 172 g.

## Load cases

Spec §4 cases, all at 40 °C:

| Case | Load | Duration | How it is applied here |
|---|---|---|---|
| Elbow stall through the horn slot | 1079 N·mm | short-term | Horn-pocket wall bearing; in-plane bending of the full section |
| Distal weight + 50 g payload | ×2 dynamic | sustained | "Weight ×2" sweep, SF 4 |
| Wrist stall reaction | 216 N·mm + static claw weight | short-term | Far pilot bearing; both strips in tear-out |
| Camera + claw weight across the elbow shaft (SYS-04) | 161 N·mm static, in every pose | sustained | Part of the weight ×2 sweep: horn clamp and plate round the pocket |
| Wrist servo's sideways moment (SYS-04) | 108 N·mm static, in every pose | sustained | Part of the weight ×2 sweep: tab screws, rails and strips |
| Base-yaw stall into a side obstacle | F = 1079 / R, tangential, at the fingertips or a camera end | short-term | "Yaw-stall" sweep, SF 3 |
| Sideways hand push | 5 N along ±Y at the same points | short-term | "Hand push" sweep, SF 3 |
| Assembly | M2 × 12 tab screws driven snug | sustained | §8 screw-strip check: strips in splitting at 150 N |
| Spec §8 tests | as written in §8 | proof | Strip rows at SF 2 (the proof-load requirement) |

**How the sweep is set up**

- **Poses.** Shoulder 0–180, elbow -150 … +30, wrist ±90, in 5° steps. That gives 47 170 poses with the elbow, wrist
  and fingertips above the desk.
- **Yaw stall.** The force is scaled down wherever a pitch servo (1079, 1079 or 216 N·mm) would back-drive first.
- **Hand push.** The force is capped where the yaw servo would back-drive (1079 / |x|).
- **Combining with weight.** Both contact cases add the static weight, component by component, taking the worse sign of
  each.

**Elbow stall at the claw.** An elbow stall against an obstacle at the claw reaches the wrist tab screws only up to the
wrist's own stall. The MG90S back-drives at 216 N·mm, which is 2.6 N at the fingertips. The wrist-stall rows cover it.

## Assumptions

**Allowables, masses and loads**

- **Allowables:** placeholders, listed below.
- **Masses:**
  - each `geometry.json` volume × 1.27 g/cm³, as solid parts (the upper bound);
  - build123d centres of mass;
  - servos and horns from `hobby_parts.py`, plus cable allowances;
  - 50 g payload at the fingertips.
- **Dynamic factor:** ×2 on the weight, as the specs use. SYS-06's 250 °/s² ramps need only about ×1.1.

**Elbow-horn joint**

- The clamp tension needed is S = |M_y| / 17.5 + |M_x| / 5.5 + |F_z|. The link tilts on a horn-arm tip (17.5 mm) or
  on the hub edge (5.5 mm).
- The capacity is Ø9 washer pull-through on the 8 mm floor, π × 9 × 8 mm², against the interlayer shear allowable.
- The two M2 × 6 arm screws are not credited.
- The M3 thread in the metal spline (4.6 mm, 01 S2) is bought hardware. At most 233 N of clamp tension holds there
  easily, provided the screw does not bottom out (SYS-04: measure the depth).

**Plate sections**

- The sections are computed from the parameters and match the CAD within 0.4 %. Out-of-plane I:
  - x 15 over the 2 mm horn pocket, Kt 2 for the arm-screw hole: 1929;
  - x 30: 2167;
  - far pilot row, Kt 2: 2025;
  - rails: 1100 mm⁴.
- Plate torsion: τ = T / (α b t²), with α from Roark, taken against the interlayer shear allowable (conservative).

**Window rails** (6.6 × 10 each, Kt 2.5 at the sharp window corners)

- Out-of-plane bending: 0.921 of the far-row moment.
- Torsion frame action: the near tab's 50 % share crosses the window as opposite out-of-plane moments in the two rails,
  each T × L_window / (2 × 19.4).
- In-plane bending from M_z on the rails' in-plane section.
- All three are evaluated pose by pose.

**MG90S tab screws**

- One M2 × 12 per tab on the centre line, 9.5 mm engaged in the 10 mm plate, Ø1.5 printed pilot.
- Screw tension S = share × M_x / 6.1 + |M_y| / 30.0 + |F_z| / 2. The tab pries about its long edge (half the case
  width) and about its tip (30 mm lever).
- Share: 70 % on the far screw, 50 % on the near one. This comes from a stiffness estimate:
  - the rails as a frame: 2.1e5 N·mm/rad;
  - one tab prying: 0.4–2.2e5 N·mm/rad;
  - giving the far tab 54–67 % and the near tab 33–46 %;
  - both rounded up, so the two shares add to more than 100 % on purpose.
- Pull-out τ = S / (π × 1.5 × L), against the interlayer shear allowable. A vertical screw in a flat-printed plate also
  shears the layer interfaces.

**Screw strips**

- **Width.** The DFM CAD width, minus the 0.15 mm that the M2 thread (Ø2.0) cuts beyond the Ø1.7 CAD hole: **1.19**
  (lead end) and **1.30** (far end) are left intact.
  - Printed, the DFM review gives ≈1.3 / 1.4 mm intact, so these widths are 0.1 mm conservative.
- **Tear-out.**
  - The in-plane side load on the servo is put entirely on one screw, plus M_z over the 29.1 mm screw spacing.
  - It acts toward the strip on two shear planes, over the first two screw diameters (4 mm).
- **Splitting.**
  - The thread's radial push is p = S tan 30° / (π d_mean L), for a frictionless 60° thread.
  - It acts on a thick ring as wide as the strip round the thread (Lamé).
  - S is the 150 N snug preload plus the screw tension of the case (added, which is conservative).
  - 300 N (over-tightened) is a sensitivity row.
  - The thread-forming interference itself is not modelled: the spec's first-print check covers it.
- **Proof rows.** At a 1.5 × proof load the stress must stay inside the allowable / 2 (= 3 / 1.5).

**Temperature.** 40 °C, and servo cases up to 45 °C, against PETG softening at about 70 °C. The margin is 25 °C or more,
which is OK.

## Allowables and sources

`library/materials.csv` has only its header, and no job has a datasheet in `inputs/`. These are the strength-checks
**placeholder** values for PETG, so **NEEDS_TEST is the best verdict possible**.

| Quantity | Value | Source |
|---|---|---|
| Tension / bending along the layers (XY) | 25 MPa | strength-checks placeholder, PETG |
| Tension / bending across the layers (Z) | 12.5 MPa | placeholder × 0.5 |
| Shear in-plane / interlayer | 12.5 / 6.25 MPa | 0.5 × the normal value (Tresca), my assumption |
| Bearing (compression, any direction) | 25 MPa | in-plane value: compression does not open the layers |
| E, ν | 1800 MPa, 0.35 | skill table; ν assumed |
| Kt | 2.5 sharp window corner or notch; 2.0 hole | skill; agent rule Kt ≥ 2 |

Required SF: 3 short-term, 4 sustained or cyclic, and 2 at a 1.5 × proof load.

## Results (copied from `python3 strength_calc.py`)

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | elbow stall 1079 N.mm: horn-pocket wall bearing (arm flanks, triangular, 2 mm deep) | bearing | 1.97 | 25.00 | 12.67 | 3 | OK |
| 2 | elbow stall 1079 N.mm: in-plane bending, full section (M <= stall) | XY | 0.96 | 25.00 | 26.10 | 3 | OK |
| 3 | wrist stall 216 N.mm + static claw weight: far pilot bearing, F 11.6 N | bearing | 1.93 | 25.00 | 12.93 | 3 | OK |
| 4 | weight x2 (sustained): clamped elbow-horn joint: Ø9 washer pull-through, floor 8 (S 63 N; s60 e-75 w-90) | Z shear | 0.28 | 6.25 | 22.47 | 4 | OK |
| 5 | yaw-stall sweep: clamped elbow-horn joint: Ø9 washer pull-through, floor 8 (S 233 N; s150 e-95 w-70, fingertip) | Z shear | 1.03 | 6.25 | 6.06 | 3 | OK |
| 6 | hand push 5 N: clamped elbow-horn joint: Ø9 washer pull-through, floor 8 (S 142 N; s65 e-50 w75, fingertip) | Z shear | 0.63 | 6.25 | 9.99 | 3 | OK |
| 7 | weight x2 (sustained): x 15 over the pocket, out of plane (Kt 2 arm-screw hole; M 311) | XY | 1.68 | 25.00 | 14.85 | 4 | OK |
| 8 | yaw-stall sweep: x 15 over the pocket, out of plane (Kt 2 arm-screw hole; M 1374) | XY | 7.44 | 25.00 | 3.36 | 3 | OK |
| 9 | hand push 5 N: x 15 over the pocket, out of plane (Kt 2 arm-screw hole; M 947) | XY | 5.13 | 25.00 | 4.87 | 3 | OK |
| 10 | yaw-stall sweep: x 30 full section, out of plane (M 1279) | XY | 2.95 | 25.00 | 8.47 | 3 | OK |
| 11 | weight x2 (sustained): far MG90S pilot row x 70.6, out of plane (Kt 2; M 311; s0 e-90 w-90) | XY | 1.54 | 25.00 | 16.28 | 4 | OK |
| 12 | yaw-stall sweep: far MG90S pilot row x 70.6, out of plane (Kt 2; M 1022; s175 e-150 w-5, fingertip) | XY | 5.04 | 25.00 | 4.96 | 3 | OK |
| 13 | hand push 5 N: far MG90S pilot row x 70.6, out of plane (Kt 2; M 669; s65 e25 w0, fingertip) | XY | 3.30 | 25.00 | 7.57 | 3 | OK |
| 14 | weight x2 (sustained): window rails 2 x 6.6 at the far window end, tab screws as pins (Kt 2.5; s0 e-125 w-55) | XY | 4.11 | 25.00 | 6.08 | 4 | OK |
| 15 | yaw-stall sweep: window rails 2 x 6.6 at the far window end, tab screws as pins (Kt 2.5; s180 e-135 w-30, fingertip) | XY | 14.64 | 25.00 | 1.71 | 3 | **FAIL** |
| 16 | hand push 5 N: window rails 2 x 6.6 at the far window end, tab screws as pins (Kt 2.5; s45 e-100 w35, fingertip) | XY | 8.26 | 25.00 | 3.03 | 3 | OK |
| 17 | weight x2 (sustained): plate torsion, full width (T 311) | Z shear | 0.45 | 6.25 | 14.01 | 4 | OK |
| 18 | yaw-stall sweep: plate torsion, full width (T 903) | Z shear | 1.30 | 6.25 | 4.82 | 3 | OK |
| 19 | hand push 5 N: plate torsion, full width (T 572) | Z shear | 0.82 | 6.25 | 7.61 | 3 | OK |
| 20 | weight x2 (sustained): MG90S tab screw pull-out, far screw S 34 N (L 9.5, Ø1.5; s0 e-15 w-50) | Z shear | 0.75 | 6.25 | 8.29 | 4 | OK |
| 21 | yaw-stall sweep: MG90S tab screw pull-out, far screw S 117 N (L 9.5, Ø1.5; s145 e-85 w-75, fingertip) | Z shear | 2.60 | 6.25 | 2.40 | 3 | **FAIL** |
| 22 | hand push 5 N: MG90S tab screw pull-out, far screw S 70 N (L 9.5, Ø1.5; s65 e-50 w75, fingertip) | Z shear | 1.57 | 6.25 | 3.99 | 3 | OK |
| 23 | weight x2 (sustained): lead-end strip (notch -> moved pilot) 1.19 intact: tear-out toward the strip, side load 11.5 N | XY shear | 1.21 | 12.50 | 10.35 | 4 | OK |
| 24 | weight x2 (sustained): lead-end strip (notch -> moved pilot) 1.19: splitting, snug preload 150 N + screw tension 25 N | XY | 2.95 | 25.00 | 8.46 | 4 | OK |
| 25 | yaw-stall sweep: lead-end strip (notch -> moved pilot) 1.19 intact: tear-out toward the strip, side load 25.1 N | XY shear | 2.63 | 12.50 | 4.75 | 3 | OK |
| 26 | yaw-stall sweep: lead-end strip (notch -> moved pilot) 1.19: splitting, snug preload 150 N + screw tension 89 N | XY | 4.03 | 25.00 | 6.20 | 3 | OK |
| 27 | hand push 5 N: lead-end strip (notch -> moved pilot) 1.19 intact: tear-out toward the strip, side load 5.8 N | XY shear | 0.60 | 12.50 | 20.69 | 3 | OK |
| 28 | hand push 5 N: lead-end strip (notch -> moved pilot) 1.19: splitting, snug preload 150 N + screw tension 53 N | XY | 3.42 | 25.00 | 7.31 | 3 | OK |
| 29 | wrist stall 216 N.mm + static claw weight: lead-end strip (notch -> moved pilot) 1.19: tear-out, side load 7.1 N | XY shear | 0.75 | 12.50 | 16.66 | 3 | OK |
| 30 | weight x2 (sustained): far-end strip (window -> far pilot) 1.30 intact: tear-out toward the strip, side load 11.5 N | XY shear | 1.11 | 12.50 | 11.30 | 4 | OK |
| 31 | weight x2 (sustained): far-end strip (window -> far pilot) 1.30: splitting, snug preload 150 N + screw tension 34 N | XY | 2.98 | 25.00 | 8.39 | 4 | OK |
| 32 | yaw-stall sweep: far-end strip (window -> far pilot) 1.30 intact: tear-out toward the strip, side load 25.1 N | XY shear | 2.41 | 12.50 | 5.19 | 3 | OK |
| 33 | yaw-stall sweep: far-end strip (window -> far pilot) 1.30: splitting, snug preload 150 N + screw tension 117 N | XY | 4.32 | 25.00 | 5.79 | 3 | OK |
| 34 | hand push 5 N: far-end strip (window -> far pilot) 1.30 intact: tear-out toward the strip, side load 5.8 N | XY shear | 0.55 | 12.50 | 22.60 | 3 | OK |
| 35 | hand push 5 N: far-end strip (window -> far pilot) 1.30: splitting, snug preload 150 N + screw tension 70 N | XY | 3.57 | 25.00 | 7.01 | 3 | OK |
| 36 | wrist stall 216 N.mm + static claw weight: far-end strip (window -> far pilot) 1.30: tear-out, side load 11.6 N | XY shear | 1.12 | 12.50 | 11.21 | 3 | OK |
| 37 | yaw-stall sweep: lead-end pilot, side load along the strips: net section 1.19 + 2.90 (Kt 2) | XY | 3.06 | 25.00 | 8.16 | 3 | OK |
| 38 | spec §8 screw-strip check: M2 x 12 driven snug: lead-end strip (notch -> moved pilot) 1.19: splitting at 150 N | XY | 2.53 | 25.00 | 9.87 | 4 | OK |
| 39 | spec §8 proof (1): 1 kg at the wrist axis, in plane: lead-end strip (notch -> moved pilot) 1.19: tear-out, 9.8 N on one screw | XY shear | 1.03 | 12.50 | 12.13 | 2 | OK |
| 40 | spec §8 proof (2): 15 N along the wrist shaft: lead-end strip (notch -> moved pilot) 1.19: splitting, preload + 10.2 N | XY | 2.70 | 25.00 | 9.24 | 2 | OK |
| 41 | spec §8 proof (2): 7.5 N on a 95 mm lever: lead-end strip (notch -> moved pilot) 1.19: splitting, preload + 82 N | XY | 3.91 | 25.00 | 6.39 | 2 | OK |
| 42 | spec §8 screw-strip check: M2 x 12 driven snug: far-end strip (window -> far pilot) 1.30: splitting at 150 N | XY | 2.43 | 25.00 | 10.28 | 4 | OK |
| 43 | spec §8 proof (1): 1 kg at the wrist axis, in plane: far-end strip (window -> far pilot) 1.30: tear-out, 9.8 N on one screw | XY shear | 0.94 | 12.50 | 13.25 | 2 | OK |
| 44 | spec §8 proof (2): 15 N along the wrist shaft: far-end strip (window -> far pilot) 1.30: splitting, preload + 10.2 N | XY | 2.60 | 25.00 | 9.63 | 2 | OK |
| 45 | spec §8 proof (2): 7.5 N on a 95 mm lever: far-end strip (window -> far pilot) 1.30: splitting, preload + 82 N | XY | 3.76 | 25.00 | 6.66 | 2 | OK |
| 46 | spec §8 proof (2): 7.5 N on a 95 mm lever: MG90S tab screw pull-out, S 82 N | Z shear | 1.83 | 6.25 | 3.42 | 2 | OK |

**Lowest SF 1.71 (required 3) at: yaw-stall sweep: window rails 2 × 6.6 at the far window end (row 15).** Row 21 fails
too (2.40).

### Advisory rows (not in the verdict)

| Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | Why it is advisory |
|---|---|---|---|---|---|---|
| yaw-stall sweep: window rails with tab springs (0.77 of the row moment instead of 0.92) | XY | 12.24 | 25.00 | 2.04 | 3 | The most a preloaded tab might help; not relied on. It still fails |
| desk crash (SYS-11), wrist back-driven at 1040 N.mm: far-end strip 1.30: tear-out, 43 N | XY shear | 4.11 | 12.50 | 3.04 | 3 | A crash the firmware guard must prevent (SYS-11: 3–5 × the wrist stall); not a spec §4 case |
| desk crash (SYS-11): far pilot bearing, 43 N | bearing | 7.13 | 25.00 | 3.51 | 3 | as above |
| yaw-stall sweep, tab screws over-tightened to 300 N: lead-end strip (notch -> moved pilot) 1.19: splitting | XY | 6.56 | 25.00 | 3.81 | 3 | Sensitivity: twice the assumed snug preload |
| yaw-stall sweep, tab screws over-tightened to 300 N: far-end strip (window -> far pilot) 1.30: splitting | XY | 6.75 | 25.00 | 3.70 | 3 | as above |
| yaw-stall sweep, stock bag screws (≈5 mm engaged): MG90S tab screw pull-out | Z shear | 4.95 | 6.25 | 1.26 | 3 | Why the spec's M2 × 12 must stay: never use the short bag screws |
| yaw-stall sweep with a 15 kgf.cm clone MG996R: MG90S tab screw pull-out | Z shear | 3.55 | 6.25 | 1.76 | 3 | Sensitivity (01 N1): every yaw-stall load scales by 15 / 11 |

## The MG90S screw strips

This answers the coordinator's request: both strips at their real widths, under every spec §4 case and every §8 test that
runs through the tab screws.

| Case | Lead end: notch to moved pilot, 1.34 CAD / 1.19 intact | Far end: window to far pilot, 1.45 CAD / 1.30 intact | SF req |
|---|---|---|---|
| Weight ×2 (sustained): tear-out / splitting | 10.35 / 8.46 | 11.30 / 8.39 | 4 |
| Yaw-stall sweep: tear-out / splitting | **4.75** / 6.20 | **5.19** / 5.79 | 3 |
| Hand push 5 N: tear-out / splitting | 20.69 / 7.31 | 22.60 / 7.01 | 3 |
| Wrist stall 216 N·mm + claw weight: tear-out | 16.66 | 11.21 | 3 |
| Yaw stall, side load along the strips: net section (lead end, Kt 2) | 8.16 | (the far strip's other side is solid plate) | 3 |
| §8 screw-strip check, M2 × 12 driven snug (150 N): splitting | 9.87 | 10.28 | 4 |
| §8 proof (1), 1 kg at the wrist axis: tear-out | 12.13 | 13.25 | 2 |
| §8 proof (2), 15 N along the wrist shaft: splitting | 9.24 | 9.63 | 2 |
| §8 proof (2), 7.5 N on the 95 mm lever: splitting | 6.39 | 6.66 | 2 |
| Corrected proof (2) below, 19 N on a bar at 45°: splitting | 5.07 | 4.69 | 2 |
| Advisory: screws over-tightened to 300 N, yaw stall: splitting | 3.81 | 3.70 | 3 |
| Advisory: desk crash (SYS-11): tear-out | — | 3.04 | 3 |

Both strips pass every case, so the user's decision to keep them under the 1.8 mm rule holds on strength.

- **What the calculation cannot check.** Whether driving the M2 thread next to a 1.2–1.3 mm wall cracks it. That is a
  print-quality question, which the spec's first-print check answers.
- **Driving the screws.** Drive them only snug: twice the assumed preload still leaves SF 3.7.
- **A back-face boss under the far pilot** (required change 2) makes that strip deeper. Its splitting stress then falls
  with the longer engagement.

## Required changes (FAIL)

Run `python3 strength_calc.py` after each change. Every what-if below is evaluated pose by pose.

**1. Ribs on the back face along both window rails.**

- **Shape.** As wide as the rails (6.6 mm), along the whole window and at least 5 mm past each window end onto the full
  plate. They deepen the window's side walls on the back face.
- **Results:**

  | Rib depth | Yaw stall | Hand push | Weight ×2 |
  |---|---|---|---|
  | 4 mm (rails 6.6 × 14) | 3.30 | 5.90 | 11.66 |
  | **6 mm (rails 6.6 × 16), recommended** | **4.29** | 7.68 | 15.06 |
  | 8 mm | 5.39 | 9.70 | 18.85 |

- **Why 6 mm fits:**
  - The ribs stay inside the depth the MG90S case already uses: it stands 8.5 mm out of the back face here.
  - The forearm's back face is 14.5 mm above the upper link's front face, so 6 mm ribs keep 8.5 mm to it and 4.7 mm to
    the shoulder clamp's screw head. They clear it in every elbow position.
  - The MG90S lead leaves the case end on the centre line, between the ribs.
  - The forearm prints front face down, so the ribs print upward without supports.

**2. Far MG90S tab screw.**

- **Change.** Add a boss on the back face under the far pilot (x 70.6, on the centre line), cut flush by the window. It
  must be deep enough for an **M2 × 16** with 13.5 mm engaged, so the pilot needs to be at least 14 mm deep.
- **Result.** Yaw-stall pull-out goes 2.40 → **3.41** (weight ×2: 11.77). An M2 × 14 (11.5 mm engaged) gives only 2.91.
- **Rib option.** With 6 mm ribs, the boss can be a cross-rib that joins them at the window's far end.
- **The near (lead-end) screw stays M2 × 12.** It reaches SF 3.15 (S 89 N). Do not put a boss under it: the MG90S lead
  leaves the case end there, 3.4 mm below the back face.

**After both changes**

- Every row reaches its required SF, so the verdict becomes NEEDS_TEST.
- **Sensitivity.** If the base servo is a 15 kgf·cm clone, every yaw-stall load rises 36 %. The far screw would then
  drop to 2.50 and the 6 mm ribs to 3.15. Use datasheet MG996Rs, or ask for a re-check.

## Proof test (spec §8)

**Why §8 (2) as written does not prove the critical sections**

- **The 15 N push at the wrist axis** loads the rails to only 0.21 × their yaw-stall value, and the far tab screw to
  0.09 ×.
- **The 7.5 N push on a 95 mm lever** gives 712 N·mm, which is 0.83 × the yaw-stall torsion at the tab plane (856 N·mm).
  It is also bolted to the tab holes, so it bypasses the servo case and the tabs' prying.
- **Test (1)** (in plane) and the first-print screw-strip check are fine. Keep them.

Replace the §8 "Proof test" item with:

> **Proof test:** (1) Clamp the elbow horn in a vice, 1 kg at the wrist axis for 1 min (in the forearm's plane): no
> cracks, no set. (2) Same clamping, with the forearm plate vertical and the wrist MG90S fitted with its tab screws as
> built. Screw a flat bar (≥ 100 mm, wood or aluminium) to the wrist horn in place of the claw, and set it at 45° to the
> forearm in the forearm's plane. Push 19 N (≈1.9 kg on a luggage scale) along the wrist shaft, square to the plate, at
> 83 mm from the wrist axis, 1 min each way. Pass: no cracks or whitening at the window corners and rails, the horn
> pocket, the MG90S pilots or either screw strip; the MG90S tabs don't lift; the forearm doesn't lift off the horn; the
> bar end comes back to within 1 mm of where it started.

**What the replacement test does**

- **It replaces the claw with a bar**, so the claw's own parts are not loaded beyond their design.
- **Ratios at 19 N.** The script prints each check's test value over its yaw-stall value:

  | Check | Ratio |
  |---|---|
  | Rails | 1.58 |
  | Far tab screw | 1.53 |
  | Near tab screw | 1.60 |
  | Far pilot row | 1.46 |
  | x 15 | 1.85 |
  | Torsion | 1.24 |
  | Elbow-horn joint | 1.65 |

- **The strips** reach splitting SF 5.07 (lead end) and 4.69 (far end), against 2 required.
- **Why 45°.** Each critical check reaches 1.5 × at a different force and bar angle:

  | Bar angle | Rails at 1.5 × | Far screw at 1.5 × | Side effect |
  |---|---|---|---|
  | 0° (in line) | 20.4 N | 50.5 N | x 15 would reach 2.3 × |
  | 90° | 28.5 N | 17.1 N | |

  45° loads both critical checks together and keeps every other check under 2 ×.
- **The turntable and base test** (arm straight up, 11.5 N at the fingertips) loads this forearm to at most 1.44 ×, at
  x 15.
- **Run the tests only on the corrected part.** On the part as drawn, the rails would see SF 1.1 at this load.

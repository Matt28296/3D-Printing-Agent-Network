VERDICT: FAIL

# Strength check: 20261026-arm-claw-frame (round 2)

strength-analyst (independent review of the round-2 geometry) · 2026-10-26 ·
`python3 jobs/20261026-arm-claw-frame/strength_calc.py` (plain python3: reads `claw_frame.py`, this job's `model.py`,
`tools/cadlib.py` and `tools/hobby_parts.py` with `ast`, so no build123d is needed)

The round-1 fixes are in and they work: the 20 mm tail is gone, and the window corners are relieved. Four things fail now:

1. **The rail wall** fails worst: **SF 0.65**. Round 2 changed it from a block back to the bulkhead into a 4 mm wall. The
   jaws react the finger moment as a couple at the ends of each rack, so rack B pushes the wall backwards at one end. With
   the jaws open, that end is the wall's free corner. The wall's rack-side root is sharp, and its bending stress runs
   across the layers. With one jaw blocked it gives SF 0.65 (open) and 1.55 (closed); every full-close grip gives 1.30
   (cyclic). The brief's "≈0.9 MPa" spreads the push over all 64 mm of wall; at the end of a cocked rack it acts on about
   8 mm.
2. **The wrist clamp.** A 10 N USB tug at the plug, 91.6 mm above the horn face, bends the joint across the shaft with
   896 N·mm. The M2 clamp screw then carries 249 N, giving washer bearing SF 2.39 and floor punching SF 2.98. The added
   desk-crash case on the camera (13 N, SYS-11) gives 2.12 and 2.65.
3. **The bulkhead.** Under the same tug along +x, its root above the pad gives 2.70 at the sharp back corner. If the
   tug's twist arrives at one top screw (port off-centre), the strips beside the servo window give 1.32.
4. **The MG90S tab-pilot strips.** The user decided to keep them (26 Oct). Their rows are below, in their own table, as
   the coordinator asked.

## Round-1 fixes: made?

| Round-1 required change | Round 2 | Made? |
|---|---|---|
| Full-width wrist plate behind the bulkhead (REAR_HALF 32), 2 mm pad over x −8…4, clamp floor ≥ 6 | Full-width plate; pad PAD_T 2.3 over x −8…3.5; floor 6.3 | Yes. The clamp is M2 × 12 + Ø6 washer, not M2 × 14: 4.6 mm into the spline, as every horn clamp has since deep review 01 S2 |
| Window's lower corners relieved (r ≥ 1.5 or Ø3 dog-bones) | Ø3 teardrop reliefs (RELIEF_D 3) | Yes: Kt 2.5 → 1.5 at the window's lower corners |
| Re-run the assembly check for the wider plate | `assembly_check.json`: wrist −90…+90 collision-free, no hits | Yes |

## Load cases

The MG90S stalls at 216 N·mm (6 V). Through the 20-tooth pinion (pitch radius 10) that is **21.6 N on one rack** when
an off-centre object stops one jaw, or **10.8 N per jaw** when both jaws touch a free object. The designer's
10.8 N is correct as the free-object share.

| # | Case | Load | Point, direction | Type, SF req |
|---|---|---|---|---|
| 1 | Stall, one jaw blocked | 21.6 N on the grip face 3 mm from the tip (spec). Each rack takes it as a couple at its ends: R = 21.6 × 52.75 / span = 20.1 N (span 56.5, jaws closed) to 27.5 N (span 41.4, jaws 44 mm open: the rack's end is past the frame's edge) | Rack B: forward on the cover at one end, backward on the rail wall at the other | Short-term, 3 |
| 2 | Stall, both jaws, every full-close grip | 10.8 N per jaw: half of case 1 | As 1 | Cyclic, 4 |
| 3 | **Crash** (required): fingertips hit the desk and back-drive the wrist | 13 N at a fingertip, any direction in the arm plane (claw x-y). This is SYS-11's upper bound for the shoulder and elbow push. 13 × 83 = 1084 N·mm = 5 × the wrist's stall, the top of SYS-11's 3–5 × range, so the wrist's back-drive doesn't cap it lower | The lower finger is always pushed **towards closing**, which reverses its rack's couple | Short-term, 3 |
| 4 | Added: the claw opens against an obstacle | 21.6 N on one finger's outer face. Foreseeable (an internal grip, or a release inside a container); the firmware limits squeezes only on closing moves | Reversed couple, as case 3 | Short-term, 3 |
| 5 | USB cable tug (spec) | 10 N any direction at the right-angle plug's cable exit, 8 mm behind the camera's back, mid-height: G (−18.8, y_port, 91.6). The port position is unmeasured (01 S5), so y_port is anywhere within ±45 | Via the mount's 2 M3 screws into the bulkhead top, then through the wrist joint | Short-term, 3 |
| 6 | Added: the camera hits the desk (SYS-11: first contact in 37 % of crash poses) | 13 N along claw y at the Brio's end face (z 79.6). Almost no torque about the wrist axis, so nothing back-drives | Wrist joint, across the shaft | Short-term, 3 |
| 7 | Camera mass and inertia, moving start/stop | The firmware ramps at 250 °/s² to 66.7 °/s. At the camera this gives 2.37 m/s² tangential (yaw, shoulder and elbow together) plus 1.73 m/s² centripetal; with ×2 for servo tracking, ≤ 0.84 g dynamic. The spec's ×3 on the weight (1 g + 2 g) covers it, so ×3 is used: camera package 86 g, end effector 224 g (solid) | Bulkhead, wrist joint | Cyclic, 4 |
| 8 | SYS-04 overhung moment (spec) | 108 / 124 N·mm (0 / 50 g, `torque_budget.json`) × 1.3 moving | Wrist joint: clamp preload | Sustained, 4 |
| 9 | Handling and assembly | 5 N at the fingertip, any direction (spec; covered by case 3). M2 clamp snug, 100 N. Tab screws snug, 100 N, plus thread forming | Joint, tab pilots | Short-term 3 / sustained 4 |
| 10 | Claw-servo reaction | 216 N·mm about its shaft. One jaw blocked: 21.6 N + 7.9 N on the shaft, 17.6 mm in front of the tabs | Tab screws, window | Short-term, 3 |
| 11 | Added, as in the jaw and cover reports: yaw stall at a fingertip | 7.1 N out of the arm plane, the largest out-of-plane part of a base-yaw stall (1079 / (2 × 76)). It acts along the wrist axis, 83.35 mm from it | Wrist joint: 592 N·mm across the shaft, plus a 7.1 N pull | Short-term, 3 |

There is no drop case in this load set.

## Build direction and critical sections

The frame prints back face down, so its layers are z = const. Wrist-plate bending runs along the layers. The bulkhead and
the rail wall bend about their roots with the stress along z, across the layers. Pull-out and punching are taken as
interlayer shear.

- **Rail wall:** x 18.35–22.35 (4 thick), z 6–17.75, y ±32, loaded on its front face. Its front root corner (z 6) is
  sharp, Kt 2.5; the r 2 fillet is on the back, the compression side. The push acts at the wall's mid-height (lever
  5.9). It spreads at 45° to the root: b_eff = 2 + 5.9 + min(5.9, distance to the wall's end).
- **Wrist joint:** the frame rocks on the hub edge of the MG90S horn (r 3.6, as SYS-04). The M2 clamp takes M/3.6 once
  that exceeds its 100 N preload. The Ø6 washer (OD 6, printed hole 2.4) bears on 23.8 mm² of pad over a 6.3 mm floor;
  punching area π × 6 × 6.3. Torque goes through the horn's single arm (r 3.6–16.1 × 1.6, triangular contact).
- **Bulkhead root:** z 8.3, where the pad's top meets the bulkhead's back face. 64 × 6.5; the sharp back corner gives
  Kt 2.5.
- **Window strips:** at the window's lower corner, through the Ø3.2 relief, −y 13.3 × 6.5 and +y 24.3 × 6.5 (Kt 1.5).
  Each carries its own top screw's x-force over 27.65 mm, plus its width share of the moment of the force above the
  bulkhead top.
- **Tab-pilot strips (from the CAD dimensions):** 1.35 mm from the lead-end pilot (y 9.7) to the lead notch, 1.45 mm
  from the far pilot (y −19.4) to the window. Both print about 0.2 wider, at 1.55 and 1.65.

## Assumptions

- The camera loads reach the frame through the 2 top M3 screws, and the **bulkhead takes all of their moment**. The
  cover's portal path (top wall → lip → tie → lower piece → M2.5 screws) is about 2.5 × softer and would take about 30 %.
  With that share the bulkhead root gives 3.86, as a what-if line in the script.
- The rack cocks in its 0.25 mm gaps, so its end force lands within about 2 mm of its end.
- The wrist's back-drive torque is unmeasured. Case 3 uses the arm's push (13 N) instead.
- Tab-pilot strips: thread forming from an assumed 0.04 N·m forming torque (μ 0.25) gives p = 4.6 MPa. A 100 N snug
  clamp adds 1.7 MPa through the 30° flanks. The hoop stress at the pilot edge is taken as Lamé's peak for a ring as thin
  as the strip (conservative); the mean across the strip, p·r/w, is the lower bound.
- Friction in clamped joints is ignored.
- Service temperature is 40 °C against PETG softening at about 70 °C: OK. That holds only while no stall lasts more than
  a few seconds. The sketch eases off 2 s after a closing squeeze, but **not after an opening move that stalls**. A
  stalled MG90S (≈4 W) can heat this bulkhead towards its softening point within minutes (SYS-11).

## Allowables and sources

`library/materials.csv` has no measured row and there is no datasheet in `inputs/`. These are the strength-checks
**placeholder** PETG values, so NEEDS_TEST is the best possible verdict.

| Quantity | Value | Source |
|---|---|---|
| Along the layers (XY) | 25 MPa | Skill placeholder, PETG |
| Across the layers (Z) | 12.5 MPa | 0.5 × in-plane (skill) |
| Interlayer shear | 6.25 MPa | 0.5 × 12.5 (Tresca), as the arm and claw round-1 checks |
| Bearing, compression | 25 MPa | In-plane value |
| Kt | 2.5 sharp internal corner; 1.5 for r ≥ 0.25 h; 1.7 for r/h 0.15–0.25 | Skill; the last is a Peterson-based interpolation |

## Results (copied from `python3 strength_calc.py`)

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 1 | USB tug 10 N at the plug (z 91.6), across the shaft: washer bearing (M_t 896 N·mm → screw 249 N) | Ø6 washer on the pad, 23.8 mm² | Z comp | 10.48 | 25.00 | 2.39 | 3 | **FAIL** |
| 2 | USB tug 10 N at the plug (z 91.6), across the shaft: floor punching under the washer | Ø6 × 6.3 floor | Z shear | 2.10 | 6.25 | 2.98 | 3 | **FAIL** |
| 3 | Added: camera hits the desk, 13 N at its end (z 79.6): washer bearing (M_t 1009 N·mm → screw 280 N) | Ø6 washer on the pad, 23.8 mm² | Z comp | 11.80 | 25.00 | 2.12 | 3 | **FAIL** |
| 4 | Added: camera hits the desk, 13 N at its end (z 79.6): floor punching under the washer | Ø6 × 6.3 floor | Z shear | 2.36 | 6.25 | 2.65 | 3 | **FAIL** |
| 5 | Crash: 13 N in the arm plane at the fingertip (z ≤ 33.2): washer bearing (M_t 406 N·mm → screw 113 N) | Ø6 washer on the pad, 23.8 mm² | Z comp | 4.75 | 25.00 | 5.26 | 3 | OK |
| 6 | Crash: 13 N in the arm plane at the fingertip (z ≤ 33.2): floor punching under the washer | Ø6 × 6.3 floor | Z shear | 0.95 | 6.25 | 6.58 | 3 | OK |
| 7 | Weight ×3 incl. the 250 °/s² ramp (cyclic): 3 × the 50 g overhung moment: washer bearing (M_t 372 N·mm → screw 103 N) | Ø6 washer on the pad, 23.8 mm² | Z comp | 4.35 | 25.00 | 5.75 | 4 | OK |
| 8 | Weight ×3 incl. the 250 °/s² ramp (cyclic): 3 × the 50 g overhung moment: floor punching under the washer | Ø6 × 6.3 floor | Z shear | 0.87 | 6.25 | 7.18 | 4 | OK |
| 9 | SYS-04 overhung moment, 50 g, ×1.3 moving (sustained): washer bearing (M_t 161 N·mm → screw 100 N) | Ø6 washer on the pad, 23.8 mm² | Z comp | 4.21 | 25.00 | 5.94 | 4 | OK |
| 10 | SYS-04 overhung moment, 50 g, ×1.3 moving (sustained): floor punching under the washer | Ø6 × 6.3 floor | Z shear | 0.84 | 6.25 | 7.42 | 4 | OK |
| 11 | Wrist stall 216 N·mm (cyclic): horn arm on the pocket wall | Arm flank r 3.6–16.1 × 1.6 (mean, resultant at r 11.9) | XY | 0.91 | 25.00 | 27.62 | 4 | OK |
| 12 | Crash: 13 N at the fingertip x 83.3 back-drives the wrist (1084 N·mm, 5 × stall: the top of SYS-11's 3–5 ×): horn arm on the pocket wall | Arm flank r 3.6–16.1 × 1.6 (mean, resultant at r 11.9) | XY | 4.54 | 25.00 | 5.51 | 3 | OK |
| 13 | Stall, one jaw blocked, jaws 44 open: rack B's +y end at the rail's end, R 27.5 N | Rail wall root, front (sharp, Kt 2.5): b_eff 7.9, t 4.0, lever 5.9 | Z | 19.24 | 12.50 | **0.65** | 3 | **FAIL** |
| 14 | Stall, one jaw blocked, jaws closed: rack B's +y end at y 25.1, R 20.1 N | Rail wall root, front (sharp, Kt 2.5): b_eff 13.8, t 4.0, lever 5.9 | Z | 8.07 | 12.50 | 1.55 | 3 | **FAIL** |
| 15 | Stall, both jaws (cyclic), jaws 44 open: R 13.8 N at the rail's end | Rail wall root, front (sharp, Kt 2.5): b_eff 7.9, t 4.0, lever 5.9 | Z | 9.62 | 12.50 | 1.30 | 4 | **FAIL** |
| 16 | Crash 13 N pushes jaw B shut: rack B's −y end on the rail at y −31.4, R 12.8 N | Rail wall root, front (sharp, Kt 2.5): b_eff 8.5, t 4.0, lever 5.9 | Z | 8.34 | 12.50 | 1.50 | 3 | **FAIL** |
| 17 | Added: opening against an obstacle, jaw B: rack B's −y end at y −31.4, R 20.1 N | Rail wall root, front (sharp, Kt 2.5): b_eff 8.5, t 4.0, lever 5.9 | Z | 13.12 | 12.50 | 0.95 | 3 | **FAIL** |
| 18 | USB tug 10 N along +x at the plug: bulkhead root above the pad | 64 × 6.5 at z 8.3, back corner Kt 2.5 | Z | 4.62 | 12.50 | 2.70 | 3 | **FAIL** |
| 19 | Camera package 86 g ×3 along x (cyclic): bulkhead root above the pad | As above | Z | 1.00 | 12.50 | 12.44 | 4 | OK |
| 20 | USB tug 10 N along x, port at y −45 (twist 450 N·mm): −y strip | 13.3 × 6.5 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +15.9 N | Z | 9.50 | 12.50 | 1.32 | 3 | **FAIL** |
| 21 | USB tug 10 N along x, port at y −45 (twist 450 N·mm): +y strip | 24.3 × 6.5 at the window's lower corner (Ø3 relief, Kt 1.5), screw force −5.9 N | Z | 3.88 | 12.50 | 3.22 | 3 | OK |
| 22 | USB tug 10 N along x, port at y +45 (twist 450 N·mm): −y strip | 13.3 × 6.5 at the window's lower corner (Ø3 relief, Kt 1.5), screw force −8.4 N | Z | 6.15 | 12.50 | 2.03 | 3 | **FAIL** |
| 23 | USB tug 10 N along x, port at y +45 (twist 450 N·mm): +y strip | 24.3 × 6.5 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +18.4 N | Z | 6.90 | 12.50 | 1.81 | 3 | **FAIL** |
| 24 | Camera ×3 along x (cyclic): −y strip | 13.3 × 6.5 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +1.0 N | Z | 0.87 | 12.50 | 14.32 | 4 | OK |
| 25 | Camera ×3 along x (cyclic): +y strip | 24.3 × 6.5 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +1.6 N | Z | 0.83 | 12.50 | 15.06 | 4 | OK |
| 26 | One jaw blocked: tab screw pull-out 13 N (M2, 5.5 engaged) | Thread shear cylinder | Z shear | 0.38 | 6.25 | 16.53 | 3 | OK |
| 27 | USB tug 10 N along x at the plug: M3 × 18 pull-out from the bulkhead top, 66 N per screw | M3, 11.5 engaged | Z shear | 0.61 | 6.25 | 10.21 | 3 | OK |
| 28 | Stall, one jaw blocked: rack B pushes the cover's lower piece forward (27.5 N at z 11): M2.5 pull-out 101 N | M2.5, 7 engaged, 1.75 mm skins | Z shear | 1.83 | 6.25 | 3.41 | 3 | OK |
| 29 | Added: yaw stall 7.1 N along the wrist axis at the fingertip (x 83.3), pulling the claw off the horn: washer bearing (M_t 592 N·mm → screw 171 N) | Ø6 washer on the pad, 23.8 mm² | Z comp | 7.22 | 25.00 | 3.46 | 3 | OK |
| 30 | Added: yaw stall 7.1 N along the wrist axis at the fingertip (x 83.3), pulling the claw off the horn: floor punching under the washer | Ø6 × 6.3 floor | Z shear | 1.44 | 6.25 | 4.33 | 3 | OK |

**Lowest SF: 0.65 (required 3), the rail wall's root at its end. One jaw blocked, jaws open.**

Information rows (not in the verdict):

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 31 | Info: proof test, horn in a vice, one jaw blocked: 1736 N·mm through the pocket | As above | XY | 7.27 | 25.00 | 3.44 | 3 | OK |
| 32 | Info: same tug with the port at the centre: −y strip | 13.3 × 6.5 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +3.8 N | Z | 4.12 | 12.50 | 3.04 | 3 | OK |
| 33 | Info: same tug with the port at the centre: +y strip | 24.3 × 6.5 at the window's lower corner (Ø3 relief, Kt 1.5), screw force +6.2 N | Z | 3.95 | 12.50 | 3.17 | 3 | OK |

With the USB port within ±10 mm of the centre, the window strips give 2.35 (what-if line).

### MG90S tab-pilot strips (user decision, 26 Oct: strips kept, first-print check in spec §8)

These rows use the real MG90S geometry (`tools/hobby_parts.py`) and the strips' CAD widths. They don't decide the
verdict, which fails on the rows above. On their own they would: at the pilot's edge, the hand calculation can't show
the sustained SF of 4. The first-print check is therefore the acceptance, not a formality.

| # | Case | Section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|---|
| 34 | Screw driving, M2 × 8 snug (100 N) + thread forming (0.04 N·m), sustained: lead-end pilot to the lead notch | Strip 1.35 CAD / 1.55 printed; hoop stress at the pilot edge (Lamé peak), p 6.3 MPa | Z | 7.80 | 12.50 | 1.60 | 4 | **FAIL** |
| 35 | Same, mean hoop stress across the strip (p r / w): lead-end pilot to the lead notch | 1.55 printed | Z | 3.05 | 12.50 | 4.10 | 4 | OK |
| 36 | One jaw blocked: tab screw pulled with 13 N, its flank pressure added (short-term): lead-end pilot to the lead notch | Lamé peak, p 6.5 MPa | Z | 8.07 | 12.50 | 1.55 | 3 | **FAIL** |
| 37 | Screw driving, M2 × 8 snug (100 N) + thread forming (0.04 N·m), sustained: far-end pilot to the window | Strip 1.45 CAD / 1.65 printed; hoop stress at the pilot edge (Lamé peak), p 6.3 MPa | Z | 7.66 | 12.50 | 1.63 | 4 | **FAIL** |
| 38 | Same, mean hoop stress across the strip (p r / w): far-end pilot to the window | 1.65 printed | Z | 2.86 | 12.50 | 4.36 | 4 | OK |
| 39 | One jaw blocked: tab screw pulled with 13 N, its flank pressure added (short-term): far-end pilot to the window | Lamé peak, p 6.5 MPa | Z | 7.93 | 12.50 | 1.58 | 3 | **FAIL** |
| 40 | One jaw blocked: the case's end bears on the window's end (21.6 N): far-end pilot to the window | Bridge over the pilot, span 1.7, depth 1.65 | Z | 0.14 | 12.50 | 90.72 | 3 | OK |
| 41 | Claw stall reaction 216 N·mm: 7.4 N per tab screw along z (the strips lie beside this path) | Pilot wall bearing Ø1.5 × 5.5 | XY | 0.90 | 25.00 | 27.79 | 3 | OK |

What this means:

- The servo's own reactions barely load the strips (rows 40 and 41).
- **Driving the screw** is the case that matters. Its hoop stress runs along z, across the layers, so a split would open
  along a layer line from the pilot to the window or notch. The narrower strip, 1.35 mm at the lead end, is the one to
  watch.
- The pass criterion in §8 (no whitening, no crack) matches this failure mode.
- Drive the screws with dry threads and stop at the first firm resistance. A 0.06 N·m driver limit, or two fingers on a
  small screwdriver, keeps the clamp near the 100 N assumed here.
- There is no drop case in this load set.

## Required changes (each computed in the script's what-if lines)

1. **Rail wall** (`claw_frame.GUIDE_T`, shared with the cover's lip): any of these.
   - GUIDE_T 4 → 10 with the sharp root kept: SF 4.06; 5.95 under the opening stall.
   - GUIDE_T 8 plus an r 2 fillet at the front root, with a 2.5 × 45° chamfer along each rack's rear back edge to clear
     it: 4.33.
   - The block back to the bulkhead (x 10–22.35): 6.19.
   - GUIDE_T 8 with a sharp root is not enough: 2.60.
   - The rail stays below the claw servo's case (z ≤ 17.75 against 21.15), so all three fit.
2. **Wrist clamp:** an Ø8 washer instead of Ø6. Bearing 4.08 and punching 3.53 under the camera crash; 4.59 and 3.98
   under the tug. An Ø8 washer reaches x 4, past the bulkhead's back face at 3.5. Either relieve the bulkhead's back face
   to 0.6 mm deep over y ±4, or file the washer flat at x 3.4. A 7 mm floor raises punching to 3.92.
3. **Bulkhead root:** an r 1.5 fillet where the pad meets the bulkhead's back face. Kt 2.5 → 1.7 gives 3.98. At the
   washer's height it stops at x 3.12, which clears the washer at x ≤ 3.
4. **Window strips:** either structure or a system change.
   - **Structure:** a 6 mm rib behind each strip's outer edge (y −32…−26 and 26…32), 10 mm deep (x −6.5…3.5), from the
     pad to the bulkhead top: SF 3.87. An 8 mm rib gives 4.89; 6 × 8 mm gives 3.04. The ribs clear the claw servo
     (y −16.9…5.9), the clamp and the top screws.
   - **System:** tie the USB cable to the frame close to the wrist axis with a slack loop to the plug (SYS-10), and change
     the spec's tug point from "at the camera" to "at the tie". That is an Architect decision. Measuring the port alone
     isn't enough: within ±10 mm of the centre the strips still give 2.35.
5. Re-run this script and `assembly_check.py` after the changes. The rail and lip feed into the cover (separate report).

## Proof test

The spec's §8 test (7.5 N pushes at the fingertips) loads none of the governing items: the rail wall, the clamp washer
and the window strips. **Replace it with this**, valid once the changes above pass:

> **Proof test.** Claw fully assembled with the camera, wrist horn clamped in a vice, servo powered and holding.
> 1. Jaws at 30 mm: pull jaw B's fingertip (3 mm from the tip) away from jaw A with **32 N** (3.3 kg on a luggage scale,
>    1.5 × the one-jaw stall force), 10 s. Then push it towards jaw A with **32 N** (1.5 × the opening stall; 20 N,
>    1.5 × the 13 N crash, if the Architect drops that case), 10 s. Repeat with the jaws closed, pulling only. At 30 mm a
>    slipping servo can't run the rack out of mesh.
> 2. **15 N** (1.5 kg) on the Brio's USB plug, 10 s each along +x (towards the fingers), ±y and ±z.
> 3. **20 N** (1.5 × the 13 N desk hit) on the end face of the Brio, along its length, 10 s each way.
> 4. 7.5 N at the fingertips, sideways (±z) then ±y, 1 min each.
>
> Pass:
> - no crack or whitening at the rail wall's root (along it and at its ends), the horn pocket, the clamp washer's seat,
>   the bulkhead root, the window's corners and strips, or any screw pilot (the tab-pilot strips included);
> - the frame doesn't lift off the horn;
> - the fingertips return to within 0.5 mm.

Keep the screw-strip check that §8 already has.

VERDICT: NEEDS_TEST

# Strength check: 20261026-arm-claw-frame (round 4)

strength-analyst (independent review of the round-4 geometry) · 2026-10-26 ·
`python3 jobs/20261026-arm-claw-frame/strength_calc.py`. It is plain python3, run from the project root. It reads
`claw_frame.py`, this job's `model.py`, `tools/cadlib.py`, `tools/hobby_parts.py`, the assembly's `torque_budget.json`,
and this job's and the cover's `geometry.json`. No build123d.

## Summary

- **Every row passes. The verdict is NEEDS_TEST only because the allowables are placeholders.**
- **Lowest SF 3.03**: the cover's top M3 × 10 screws pulling out of the bulkhead top, with no camera mount, under the
  opening stall on jaw B (row 39).
  - This bound row stays in. My cover review finds that the anchor's preload, once it has crept away, no longer holds
    the post. The push then returns to the cover's top joint, as in round 3.
  - It passes either way.
- **Lowest SF of the frame's own load cases: 3.53**, floor punching under the Ø8 washer when the camera hits the desk
  (row 4). Unchanged.
- **The anchor pilot (round 4) passes every new row.**
  - Block's rack-side root with the pilot in its section: **5.93** (row 15). The pilot's own edge gives 2.0 × 0.98 MPa;
    the root face governs.
  - M3 × 45 pull-out on the 150 N snug preload: **4.42** (sustained, row 42). With the cover's lift: **4.14** (row 43).
  - Thread forming plus preload in the 2.65 mm walls: **3.77**, at installation (row 46).
  - The shank dragged +x by the whole push, if the cover's foot ever slides that far: bearing 16.7, wall tear-out 14.7,
    block bent the other way 5.83.
- **Spec §8 still matches,** with the cover's caveat: don't run step 1's opening push until the cover's fix is in (cover
  report). The pass criteria need round 3's wording update (DFM note 2).

## What changed since round 3

**Design (round 4)**
- One Ø2.7 CAD × 14 M3 pilot in the rail block's top at (18.35, 28), z 3.75–17.75. It takes the cover's M3 × 45 anchor,
  11.25 mm engaged.
- Walls round it: 2.65 to the front face and to the +y end, 7.5 behind, 6.65 towards −y. The floor is 3.75.

**Method (this review)**
- **Rail-block rows whose 45° spread reaches y 28 take the pilot out of the root section** (rows 15–17 and 21). The pilot
  crosses the root plane z 6. The stress is the worse of:
  - the rack-side face, Kt 2.5;
  - the pilot's edge, Kt 2.

  Round 3's what-if (5.93) is now a row.
- **New anchor rows:**
  - pull-out on the preload, with the lift, and with the lift alone once the preload has gone;
  - spec §8 proof pull-out;
  - thread-forming hoop and preload hoop in the 2.65 walls;
  - shank bearing, wall tear-out and block bending under an x drag bounded by the whole push: 27.0 N service, 34.2 N proof.
- **Forces come from my cover analysis** (cover strength_calc.py, round 4, worst of 64 variants):
  - foot held by friction: x 25.8 N, lift ≤ 10.1 N (12.7 N at the proof push);
  - preload gone: x 0 until the 0.2 mm hole clearance closes, which it does not below 40 N. The lift then rises to
    120.8 N (153.1 N at the proof push) as the cover rocks on its top joint.
- **Wrist moments are scaled ×1.0054** for the claw's +1.36 g since torque_budget.json: the cover's 8 mm post, less the
  pilot. The governing rows don't move by more than 0.01.

## Load cases

As round 3, plus the cover's anchor.

| # | Case | Load | Point, direction | Type, SF req |
|---|---|---|---|---|
| 1 | Stall, one jaw blocked | 21.6 N, 3 mm from the tip; rack couple R 19.8 N (closed) to 27.0 N (open) | Rack B back on the rail block at its +y end, over the pilot | Short-term, 3 |
| 2 | Stall, both jaws | half of 1 | As 1 | Cyclic, 4 |
| 3 | Crash | 13 N at a fingertip, reversed couple | Rail block at rack B's −y end; wrist joint | Short-term, 3 |
| 4 | Opening against an obstacle | 21.6 N, reversed | As 3; the cover's push → its anchor, or its top joint | Short-term, 3 |
| 5 | USB tug | 10 N any direction at the plug | Top M3 → bulkhead → wrist joint | Short-term, 3 |
| 6 | Camera hits the desk | 13 N along y at the Brio's end | Wrist joint | Short-term, 3 |
| 7 | Weight ×3 incl. the ramp | 3 × 134 N·mm | Wrist joint | Cyclic, 4 |
| 8 | SYS-04 overhung moment | 134 × 1.3 N·mm | Clamp preload | Sustained, 4 |
| 9 | Yaw stall at the fingertip | 7.1 N along the wrist axis | Wrist joint + pull | Short-term, 3 |
| 10 | **Cover anchor (new)** | M3 × 45 snug, 150 N; lift 10.1 N (120.8 N if the preload has gone); x drag ≤ 27.0 N | The pilot and the block round it | Sustained 4 / short-term 3 |
| 11 | Spec §8 proof | 32 N push, jaws 30: R 34.2 N | As 4 and 10 | Proof, 2 |

## Assumptions

- **Layers.** The frame prints back face down, so its layers are z = const. Pull-out and punching are interlayer shear.
  Bending about the block's, bulkhead's and ribs' roots crosses the layers. Hoop stress round a vertical pilot runs
  along them.
- **Anchor preload: 150 N** for "snug only (≤ 0.09 N·m)", as the cover analysis assumes.
- **Thread forming** uses the same flank pressure as the MG90S rows, p_form 4.6 MPa (40 N·mm for an M2 over 5.5 mm, the
  same 0.25 radial interference). It is taken as a short-term installation event that relaxes afterwards. Lamé ring of
  r_i 1.25 and a 2.75 mm printed wall: × 1.22.
- **Top-screw bound** (rows 39–40): all of the cover's overturning moment R (50 − 17.2) goes into the top M3s against the
  bulkhead's rear edge. My cover model gives less, because the anchor still holds z.
- **Temperature:** 40 °C against PETG at about 70 °C: OK.

## Allowables and sources

`library/materials.csv` has no measured row: **placeholder** PETG values, NEEDS_TEST at best.

| Quantity | Value | Source |
|---|---|---|
| Along the layers | 25 MPa | Skill placeholder |
| Across the layers | 12.5 MPa | 0.5 × in-plane |
| Shear in-plane / interlayer | 12.5 / 6.25 MPa | 0.5 × normal |
| Bearing | 25 MPa | In-plane value |
| Kt | 2.5 sharp; 2 at a hole; 1.5 / 1.7 at fillets | Skill |

## Results (from `strength_calc.py`; the script prints each row's full label)

| # | Case | Section | Dir | SF | SF req | OK? |
|---|---|---|---|---|---|---|
| 1 | USB tug: washer bearing | Ø8 washer on the pad | Z comp | 4.47 | 3 | OK |
| 2 | USB tug: floor punching | Ø8 × 6.3 | Z shear | 3.98 | 3 | OK |
| 3 | camera hits the desk: washer bearing | | Z comp | 3.97 | 3 | OK |
| 4 | **camera hits the desk: floor punching** | Ø8 × 6.3 | Z shear | **3.53** | 3 | OK |
| 5–6 | finger crash in the arm plane: washer / floor | | | 9.87 / 8.77 | 3 | OK |
| 7–8 | weight ×3 (cyclic): washer / floor | | | 9.99 / 8.88 | 4 | OK |
| 9–10 | SYS-04 ×1.3 (sustained): washer / floor | | | 11.13 / 9.90 | 4 | OK |
| 11–12 | yaw stall pulling the claw off the horn: washer / floor | | | 6.49 / 5.77 | 3 | OK |
| 13 | wrist stall (cyclic): horn arm on the pocket wall | | XY | 27.62 | 4 | OK |
| 14 | crash back-drives the wrist (5 × stall): pocket wall | | XY | 5.51 | 3 | OK |
| 15 | **stall, jaws open, rack B's +y end at the block's end: block root with the anchor pilot** | b_eff 7.9, I 1194 net; face Kt 2.5 2.11 / pilot edge Kt 2 0.98 MPa | Z | **5.93** | 3 | OK |
| 16 | stall, jaws closed, +y end at 25.1: block root with the pilot | b_eff 13.8 | Z | 14.54 | 3 | OK |
| 17 | both jaws (cyclic), open: block root with the pilot | | Z | 11.86 | 4 | OK |
| 18 | crash: rack B's −y end on the block | | Z | 14.54 | 3 | OK |
| 19 | opening against an obstacle, −y end at −31.4 | | Z | 9.26 | 3 | OK |
| 20 | opening against an obstacle, jaws open, −y end at −9.4 | | Z | 11.02 | 3 | OK |
| 21 | block root less the front pilot's overlap, with the anchor pilot | b_eff 6.9 | Z | 5.15 | 3 | OK |
| 22 | rack B on the skin over a front pilot | | XY | 20.09 | 3 | OK |
| 23–30 | bulkhead, ribs, fillet, relief, block top, rib back, torsion (USB tug, camera ×3) | as round 3 | Z | ≥ 4.63 | 3/4 | OK |
| 31–36 | window strips + ribs, USB tug at y ±45 / camera ×3 | | Z | ≥ 3.87 | 3/4 | OK |
| 37 | claw tab screw pull-out, 14 N | M2, 5.5 | Z shear | 15.64 | 3 | OK |
| 38 | USB tug: M3 × 18 pull-out from the bulkhead top | | Z shear | 10.21 | 3 | OK |
| 39 | **opening stall on jaw B: the cover's moment on its top M3 × 10 (bound if the anchor's preload has gone)** | M3, 7.0 | Z shear | **3.03** | 3 | OK |
| 40 | same, M3 × 18 with the camera mount | M3, 11.5 | Z shear | 4.97 | 3 | OK |
| 41 | rack B pushes the cover's lower piece: M2.5 pull-out | 11 | Z shear | 4.98 | 3 | OK |
| 42 | **new:** cover anchor snug, 150 N (sustained): pull-out | Ø3 × 11.25 | Z shear | **4.42** | 4 | OK |
| 43 | **new:** anchor preload + lift 10.1 N, opening stall | | Z shear | 4.14 | 3 | OK |
| 44 | **new:** anchor, preload gone: lift 120.8 N | | Z shear | 5.49 | 3 | OK |
| 45 | **new:** anchor at the spec §8 proof push, the worse of 162.7 / 153.1 N | | Z shear | 4.07 | 2 | OK |
| 46 | **new:** anchor driven, thread forming 4.6 + preload 0.82 MPa (short-term) | 2.65 CAD / 2.75 printed walls, Lamé × 1.22 | XY | **3.77** | 3 | OK |
| 47 | **new:** anchor preload alone (sustained) | | XY | 25.16 | 4 | OK |
| 48 | **new:** anchor dragged +x, 27.0 N: shank bearing | Ø3 × 6 | bearing | 16.67 | 3 | OK |
| 49 | **new:** same, tear-out of the 2.65 wall to the front face | 2 × 2.65 × 6 | XY shear | 14.73 | 3 | OK |
| 50 | **new:** same, block root bent +x by the pull at its top | b_eff 14.6, lever 11.75, Kt 2.5 | Z | 5.83 | 3 | OK |
| 51–53 | **new:** the same three at the proof push, 34.2 N | | | 13.16 / 11.62 / 4.60 | 2 | OK |

**Lowest SF 3.03 (row 39, the top-screw bound). The frame's own cases: 3.53 (row 4). The anchor's: 3.77 (row 46).**

Information rows (not in the verdict):
- the vice proof test through the pocket: 3.44;
- the USB tug with the port centred: 10.56 / 6.77.

**MG90S tab-pilot strips** (the user's decision of 26 Oct 2026, with the first-print check in spec §8) are unchanged and
stay in their own table:
- Lamé peak, sustained (forming + snug): 1.60 / 1.63 (req 4);
- short-term with the pull: 1.55 / 1.57 (req 3);
- mean hoop stress across the strip: 4.10 / 4.36.

That table is not part of this verdict, as in round 3.

## Proof test (spec §8)

- **It still matches.** The 1.5 × loads (32 N one-jaw pull and opening push, 15 N on the USB plug, 20 N on the Brio's
  end, 7.5 N at the fingertips) load every governing item here: the washer and floor, the rail block with the pilot, the
  ribs, the strips and the anchor (rows 45, 51–53, all ≥ 4.07).
- **Step 1's 32 N opening push on jaw B** loads this frame safely. On the as-built cover it can crack the cover's top wall
  once the anchor slips (cover report, proof SF 1.08). Run it only after the cover's fix.
- **The pass criteria still need round 3's wording update** (DFM note 2): "the rail block's rack-side root (along it and
  at its +y end)", "the rib roots on the pad and the washer relief's foot", "the washer lies flat on the pad". Add "the
  anchor pilot's mouth on the block top".

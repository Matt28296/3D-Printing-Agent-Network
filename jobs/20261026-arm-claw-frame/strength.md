VERDICT: FAIL

# Strength check: 20261026-arm-claw-frame (round 1)

strength-analyst · 2026-10-26 · `python3 strength_calc.py` (plain python3; reads `claw_frame.py`, this job's `model.py`,
`tools/hobby_parts.py` and the claw jobs' `geometry.json`)

The whole claw and the camera hang on the wrist horn through the **20 mm-wide tail of the wrist plate behind the
bulkhead** (x −8…4, y ±10). That tail contains the horn hub pocket and the clamp hole, and it fails in bending and torsion:
SF 0.84 under the 10 N USB-cable tug, 1.43 under the yaw-stall sweep, 2.67 under the 5 N hand push. The 4 mm floor
under the clamp washer also fails under the tug (2.26), and so do the servo-window corners (2.10). Everything else
passes. The changes under **Required changes** pass every row, computed in the script's what-if lines.

## Load cases

Claw servo: MG90S, 216 N·mm stall at 6 V. Pinion pitch radius 9 gives 24 N into the racks: all of it on one jaw when an
off-centre object blocks that jaw first, or 12 N per jaw when both touch. Mass beyond the wrist horn is 172 g with the
Brio (see the torque section), plus a 50 g payload.

| # | Case | Load | Point and direction | Type, SF req |
|---|---|---|---|---|
| 1 | Wrist stall through the horn pocket | 216 N·mm (MG90S) | pocket walls, bearing | short-term, 3 |
| 2 | Claw-servo stall reaction | 216 N·mm about claw x | 2 tab screws (horizontal pilots) in the bulkhead | short-term, 3 |
| 3 | One jaw blocked: shaft load | 24 N + 8.7 N separating, 13.4 mm in front of the tab face | servo tabs → bulkhead | short-term, 3 |
| 4 | Rack B thrust couple (one jaw blocked) | finger moment 1194 N·mm → 31.2 N at each rack end | lower rail face | short-term, 3 |
| 5 | Claw + camera + payload weight ×3 | 222 g × 3 g, CoG 35 mm outboard of the back face | wrist joint and tail, any direction in the arm plane | cyclic, 4 |
| 6 | Yaw-stall sweep (arm review) | fingertip force F = 1000/R, capped where a servo backdrives | wrist horn: T ≤ 58, Mt ≤ 650 N·mm | short-term, 3 |
| 7 | Hand push (arm review) | 5 N out of the arm plane at the fingertip | wrist horn: Mt 381 N·mm | short-term, 3 |
| 8 | **USB-cable tug (added)** | 10 N, any direction, at the Brio's end (−3.3, ±51, 64.2) | wrist joint, tail, bulkhead via the cover screws | short-term, 3 |
| 9 | Camera + mount + cover weight ×3 along x (added) | 2.4 N at the top screws | bulkhead root and window | cyclic, 4 |

The wrist servo (MG90S) cannot hold more than its 216 N·mm stall about its own axis (claw z). So a tug's moment about
that axis is capped at 216 N·mm. The other two components go through the clamped horn joint and are not capped.

## Build direction and critical sections

The frame prints back face down, so layers lie in planes z = const. Wrist-plate bending runs along the layers. Bulkhead
bending (stress along z) runs across them. Torsion and pull-out are conservatively taken as interlayer shear, as in the
arm jobs.

- **Tail at x 0**, through the clamp hole and the hub pocket: 20 × 6, minus the pocket (2 deep) and the Ø2.6 hole.
  A 93.8 mm², I 262 mm⁴ (CAD 93.6 / 261), Z 81 mm³. Kt 2 (hole). Torsion uses the thin-strip J of the grooved
  section, 798 mm⁴.
- **Clamped wrist-horn joint**: M2×12 with a Ø6 washer from the front face, plus 1 arm screw, over a 4 mm floor. Same
  model as the arm jobs: capacity 3028 N·mm transverse and 2149 N·mm torsion at the interlayer allowable.
- **Bulkhead**: root above the rail, 6 × 64, Z 384 mm³. Beside the servo window the strips are 15.2 + 25.9 wide, Z 247
  (CAD 247; 221 through the tab pilots). Window and rail-top corners are sharp, Kt 2.5.
- **Claw-servo tab pilots**: Ø1.5 printed, along x through the 6 mm bulkhead. Ligament to the window is 1.60 mm.

## Assumptions

- Masses come from the `geometry.json` volumes at solid PETG density (1.27 g/cm³), as in the arm jobs. Part CoGs are
  the build123d centres of mass of each `design()`.
- USB tug: 10 N at the camera's end, mid height, in every direction (3° grid). The cover is screwed on and is much
  stiffer than the bulkhead. It reacts the camera's moment as a z-couple between the top screws and the front plate.
  The bulkhead takes the x-shear at its top, plus the twist about the wrist axis (≤ 216, capped by the servo), as
  opposite forces at the two top screws on the narrow strip.
- Shaft load: the servo is held by its 2 tab screws alone. The case bearing in the window is ignored. Screws are M2×8
  self-tapping through the 2.5 mm tab, 5.5 mm engaged.
- The friction of clamped joints is ignored. The servo's own output bushing carries 25.5 N radial at 13 mm when one jaw
  is blocked. That is not a printed-part check, but note it: the MG90S is a micro servo.

## Allowables and sources

`library/materials.csv` has no measured row and there is no printed-specimen datasheet, so these are the strength-checks
**placeholder** PETG values. NEEDS_TEST is the best verdict possible even after the changes.

| Quantity | Value | Source |
|---|---|---|
| Tension/bending along the layers (XY) | 25 MPa | skill placeholder, PETG |
| Tension/bending across the layers (Z) | 12.5 MPa | placeholder × 0.5 |
| Shear in-plane / interlayer | 12.5 / 6.25 MPa | 0.5 × the normal value (Tresca), as in the arm jobs |
| Bearing, compression | 25 MPa | in-plane value |
| Kt | 2.5 sharp internal corner or window corner, 2 hole, 1.5 filleted (r ≥ 0.25 h) | skill |

Required SF is 3 for short-term loads and 4 for cyclic or sustained loads. Service temperature is 40 °C against PETG
softening at about 70 °C: OK.

## Results (copied from `python3 strength_calc.py`)

"Z shear" rows that combine bending and torsion (or the two moments at the clamped joint) are utilisation rows. The
stress column is 6.25 × utilisation, and SF = 1/utilisation.

| # | Case / section | Dir | Stress (MPa) | Allowable (MPa) | SF | SF req | OK? |
|---|---|---|---|---|---|---|---|
| 1 | wrist stall 216 N.mm: horn-pocket wall bearing | XY | 1.91 | 25.00 | 13.06 | 3 | OK |
| 2 | weight x3 (cyclic): clamped wrist-horn joint | Z shear | 0.82 | 6.25 | 7.60 | 4 | OK |
| 3 | weight x3 (cyclic): tail x 0 bending (Kt 2 clamp hole) + torsion | Z shear | 2.24 | 6.25 | 2.79 | 4 | **FAIL** |
| 4 | yaw-stall sweep: clamped wrist-horn joint (D6 washer + arm screw, floor 4) | Z shear | 1.49 | 6.25 | 4.19 | 3 | OK |
| 5 | yaw-stall sweep: tail x 0 (20 wide) bending (Kt 2 clamp hole) + torsion | Z shear | 4.38 | 6.25 | 1.43 | 3 | **FAIL** |
| 6 | hand push 5 N: clamped wrist-horn joint (D6 washer + arm screw, floor 4) | Z shear | 0.79 | 6.25 | 7.95 | 3 | OK |
| 7 | hand push 5 N: tail x 0 (20 wide) bending (Kt 2 clamp hole) + torsion | Z shear | 2.34 | 6.25 | 2.67 | 3 | **FAIL** |
| 8 | USB tug 10 N, worst direction: clamped wrist-horn joint | Z shear | 2.76 | 6.25 | 2.26 | 3 | **FAIL** |
| 9 | USB tug 10 N, worst direction: tail x 0 bending (Kt 2) + torsion | Z shear | 7.42 | 6.25 | 0.84 | 3 | **FAIL** |
| 10 | claw stall 216 N.mm: tab-pilot bearing (compression) | XY | 1.14 | 25.00 | 22.01 | 3 | OK |
| 11 | claw stall: pilot-to-window ligament 1.60 tear-out, full F toward the window (Z shear) | Z shear | 0.49 | 6.25 | 12.80 | 3 | OK |
| 12 | one jaw blocked: tab screw pull-out, 20.5 N (M2x8, L 5.5, Z shear) | Z shear | 0.79 | 6.25 | 7.91 | 3 | OK |
| 13 | one jaw blocked: bulkhead root above the rail, tab push (Z, Kt 2.5) | Z | 2.23 | 12.50 | 5.60 | 3 | OK |
| 14 | rack B back thrust 31.2 N on the rail face (3 mm contact x rack height) | XY | 1.54 | 25.00 | 16.23 | 3 | OK |
| 15 | camera + mount + cover weight x3 along x (cyclic): bulkhead root above the rail (Z, Kt 2.5) | Z | 0.49 | 12.50 | 25.65 | 4 | OK |
| 16 | camera + mount + cover weight x3 along x (cyclic): bulkhead at the window corners (Z, Kt 2.5) | Z | 0.67 | 12.50 | 18.78 | 4 | OK |
| 17 | USB tug 10 N along x at the top screws: bulkhead root above the rail (Z, Kt 2.5) | Z | 1.69 | 12.50 | 7.38 | 3 | OK |
| 18 | USB tug 10 N along x at the top screws + twist 216 on the narrow strip: bulkhead at the window corners (Z, Kt 2.5) | Z | 5.96 | 12.50 | 2.10 | 3 | **FAIL** |
| 19 | rack thrust 31.2 N on the front plate next to a front screw: M3x12 pull-out (L 9) | Z shear | 0.44 | 6.25 | 14.16 | 3 | OK |
| 20 | USB tug tips the camera mount back over the cover's rear edge: top screw pull-out 37 N (M3x18, L 11.5) | Z shear | 0.41 | 6.25 | 15.26 | 3 | OK |

**Lowest SF 0.84 (required 3): USB tug, tail at x 0 (bending + torsion).**

## Required changes (each computed in the script's what-if lines)

1. **Wrist plate behind the bulkhead (x −8…4): full width and 8 mm thick.** Set REAR_HALF 10 → 32 (no tail cutout),
   and add a 2 mm raised pad on the front face over x −8…4, so the floor under the clamp washer goes from 4 to 6 mm. Use
   an M2×14 clamp screw instead of M2×12. T_W and the rack-B track stay at 6, so nothing else in the claw moves. The pad
   sits under the claw servo's body (z ≥ 16.5) and the back face stays where it is, so it clears.
   - Tail: weight ×3 SF 2.79 → 22.8, sweeps 1.41 → 10.9, USB tug 0.84 → 6.97.
   - Clamped joint: USB tug 2.26 → 3.24, sweeps → 5.78.
   - Full width without the pad gives tail 3.94 but leaves the joint at 2.26, so both parts of the change are needed.
2. **Relieve the servo window's lower corners**: r ≥ 1.5 corner fillets, or Ø3 dog-bone reliefs so the MG90S still drops
   in. That takes Kt from 2.5 to 1.5. Row 18 (USB tug + twist at the window corners) goes from 2.10 to 3.50.
3. Re-run `assembly_check.py`. The wider plate sweeps a radius of 33 mm about the wrist axis at z 0…8. That is 2.6 mm
   clear of the wrist servo's case top, but check it.

The frame also carries the cover. The cover and jaw changes (separate reports) change the loads here only slightly.
Re-run this script after any change to `claw_frame.py`.

## Static servo torques, arm straight out horizontally (camera fitted), and payload rating

From the arm model with the claw-v2 end effector:

- Fingertip 76.15 mm in front of the wrist axis.
- 172 g beyond the wrist horn: claw parts 70.4 g, camera mount 11.2 g, claw MG90S 13.4 g, Brio 63 g + 1/4" screw 4 g,
  screws 6 g, horns 4 g.
- CoG 8.3 mm in front of the wrist axis. The Brio's CoG is 3.3 mm behind the wrist axis and 64 mm outboard of the claw's
  back face.
- The wrist servo is now an MG90S (13.4 g).

| Payload | Shoulder MG996R (stall 1000) | Elbow MG996R (stall 1000) | Wrist MG90S (stall 216) |
|---|---|---|---|
| 0 g | 495 N·mm (49 %) | 193 (19 %) | 14 (6 %) |
| 20 g | 547 (55 %) | 226 (23 %) | 29 (13 %) |
| 50 g | 625 (63 %) | 275 (27 %) | 51 (24 %) |
| *without the camera:* 0 / 20 / 50 g | 352 / 405 / 483 (35 / 40 / 48 %) | 128 / 160 / 209 | 17 / 32 / 55 |

The Architect's estimate was 420 / 471 / 548 N·mm. These figures are about 75 N·mm higher, because the end effector
comes to 172 g, not ≈148 g. The printed parts are counted at solid density (81.6 g including the camera mount), and the
wrist servo is now 4.4 g heavier.

**Payload rating.** Rule used: static shoulder torque at full horizontal reach ≤ 50 % of stall, so the ×2 dynamic factor
used in all the arm checks stays within the stall torque. The old gripper arm ran at 41 % with 50 g. With the Brio
fitted the shoulder is already at 49 % with no payload at full reach (266 mm from the shoulder axis).

- **Without the camera: 50 g** (48 %).
- **With the camera: 20 g, carried with the fingertip within ≈240 mm of the shoulder axis horizontally**. 50 g only
  within ≈210 mm. At full reach with the camera, carry nothing and move slowly.

The elbow (≤ 27 %) and wrist (≤ 24 %) have ample margin. The recommended claw changes add mass, so re-run this table
after the redesign.

## Proof test (after the changes; replaces the spec §8 test)

Claw fully assembled with the camera, wrist horn clamped in a vice.

1. 7.5 N (≈0.75 kg on a luggage scale) at the fingertips: sideways (±z), then up and down (±y), 1 min each. This is
   1.5 × the hand push.
2. **15 N (1.5 kg) on the Brio's USB plug end**, 1 min each: along the jaw travel (claw ±y), then away from the wrist
   (claw +z). This is 1.5 × the cable tug.

Pass:

- no cracks or whitening at the horn pocket, the clamp hole, the plate behind the bulkhead, the bulkhead root, the servo
  window corners or any screw pilot;
- the frame does not lift off the horn;
- the fingertips return to within 0.5 mm.

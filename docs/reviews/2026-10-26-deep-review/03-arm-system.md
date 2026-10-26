# Deep review 03: the robot arm as a machine

Desktop robot arm with the rack-and-pinion claw (v2) and the Brio 4K on the wrist. Independent system-level review, 2026-10-26.

This slice covers how the whole arm works: actuator torque, stability, kinematics, the camera's view, cables, assembly order, interfaces between parts and failure modes. Per-part printability and strength are in each job's `design_review.md` / `strength.md`. Bought-part dimensions are in [01-bought-parts.md](01-bought-parts.md), wiring and firmware in [02-electronics-firmware.md](02-electronics-firmware.md). Where 01 or 02 already covers a point, this report refers to it and adds only the machine-level consequence.

**Abbreviations used in the evidence:**

- `BG` = `jobs/20261025-robot-arm-assembly/BUILD_GUIDE.md`
- `AP` = `…/assembly_plan.md`
- `AC` = `…/assembly_check.py` / `.json`
- `CF` = `…/claw_frame.py`
- `INO` = `…/arm_test/arm_test.ino`
- `PC` = `…/pc/arm_pc_control.py`

## Verdict

**The arm can't be built as documented.**

The new claw has no assembly sequence that works (SYS-01):

- With the pinion on its servo, a jaw slid in from the open end of its slot meets the pinion 31 mm before its closed position. From there it needs 197° more pinion rotation, while the claw uses 140° of servo travel.
- The cover can't be fitted over jaws that are already meshed.
- Once forced together, the claw couldn't be taken apart for service.

Fix it in the same claw redesign that 01-B1 and 01-B2 already force, before any claw part is printed.

The rest of the machine is sound in layout but marginal at full reach:

- **Shoulder (SYS-02).** With the camera, the shoulder MG996R holds 42–54 % of its 6 V stall torque with the arm straight out. That is above a continuous-holding level even with no payload. The camera package costs about 60 g of payload at full reach, so payload has to be quoted by reach.
- **Elbow window (SYS-03).** With the elbow's 180° window centred on "straight", only a 117–218 mm band of the desk can be picked top-down. If the MG996R turns only the 120° that TowerPro quotes, the fingertips can't reach the desk at all. Re-centring the elbow window fixes both.
- **Turntable (SYS-05).** It has no real bearing: the base servo's shaft carries 0.5–0.65 N·m of overturning moment.
- **Camera load (SYS-04).** The camera roughly quadruples the out-of-plane load on the wrist servo.
- **Cheap paper fixes.** The other items are assembly-order, cable, tolerance and calibration issues, cheap to fix on paper now.

What works:

- The arm doesn't collide with itself anywhere inside the servo travel.
- The elbow (17–25 % of stall) and wrist (5–22 %) have ample margin.
- The camera sees both fingertips near the image centre over the whole 0–44 mm stroke, in all three FOV presets.

## Findings

Severity counts: **1 blocker, 10 should fix, 8 notes.**

| ID | Severity | Area | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| SYS-01 | **Blocker** | Assembly (claw) | The claw has no feasible assembly or service sequence. A jaw meets the fixed pinion 31 mm early and needs 197° more pinion rotation (57° beyond fully open); the second jaw can't go in at all; the cover can't pass fitted jaws | `BG:127–140`; slots open at one end only (cover `model.py:49–50`); mesh sweep: first contact at −31 mm; cover over jaws 73–210 mm³ overlap at every height | Make the front-plate hole a pinion pass-through (Ø ≥ 20.6 mm) and fit the pinion last, axially, with both jaws parked fully open. Checked: 0 mm³ against either jaw all the way in. Or split off the front plate |
| SYS-02 | Should fix | Torque | Shoulder margin with the camera. Straight out: 457 / 507 / 583 N·mm with 0 / 20 / 50 g (42 / 47 / 54 % of 1079 N·mm). Moving: ×1.4. Holding: ≈1.1–1.35 A against the 0.5–0.9 A running band. The camera package costs 157 N·mm ≈ 62 g of payload | Mass model from `slice_stats.json` + datasheets; `BG:6–8`; `AP:39` | Quote payload by reach (table in SYS-02); park upright when idle. For full-reach work: a shoulder counterbalance spring, a 20–25 kg·cm shoulder servo, or a lighter or relocated camera |
| SYS-03 | Should fix | Kinematics | Elbow ±90° centred on straight. Top-down desk picks only at in-plane x 117–218 mm. With 150° servo travel: 142–205 mm. With 120°: the fingertips never reach the desk | Workspace sweep inside the servo travel; `INO:24–30`; 02-A5, 02-A8 | Fit the forearm so servo 0–180 maps to elbow −150…+30°. Top-down picks then cover 32–218 mm (58–205 at 150°, 81–167 at 120°), and the documented pick pose becomes reachable |
| SYS-04 | Should fix | Loads / interfaces | The camera sits 64 mm outboard of the claw. It puts a pose-independent bending moment on every pitch servo shaft and horn joint: shoulder 169–204, elbow 109–132, wrist 69–81 N·mm (wrist without camera: 19). Across the hub, only the clamp screw holds it: 23–37 N of tension. Turntable spec still lists ≈100 N·mm (upright root now ≈205–250) | Overhung-moment calc; `20261025-arm-turntable/spec.md:29`; 01-S2 (clamp reach unverified) | Verify the clamp-screw engagement (01-S2) so every clamp has preload; re-torque after the first hours; use these moments in the round-4 strength checks; see SYS-02 for moving the camera |
| SYS-05 | Should fix | Stability / bearing | The turntable has no bearing. The base servo's output carries 518–654 N·mm overturning plus 4.9 N axial. 173–210 N·mm of it acts permanently about the double-arm horn's long axis, where the disk rests on the Ø11 hub only. The ring touches only after 1.95° of tilt (9.3 mm drop at the tip) | Turntable `model.py:3–8, 18`; ring `model.py:15–18`; `BG:111` | Use the MG996R's round Ø25 disc horn under the turntable (flat underside, no CAD change). Close the ring gap to 0.3–0.5 mm with PTFE tape or rollers: friction ≤ 200 N·mm at μ 0.3 |
| SYS-06 | Should fix | Dynamics | Every move starts and stops as a velocity step (66.7°/s from the first 15 ms), with integer-degree writes. Inertia 0.008–0.011 kg·m² (shoulder) and 0.011–0.015 (yaw) means +186–261 / +246–334 N·mm if the speed is reached in 50 ms. The servos saturate at each start; the camera shakes at each stop | `INO:51–66`; inertia calc | Trapezoidal profile at 200–300 °/s² (+28–57 N·mm); `writeMicroseconds()` (1° of shoulder = 4.8 mm at the tip) |
| SYS-07 | Should fix | Interfaces / calibration | Horns go on discrete spline positions: MG996R 25 teeth gives up to ±7.2°; the MG90S gives up to ≈±9°. No per-joint trim exists. Tip errors at full reach: base 36 mm sideways, shoulder 34, elbow 22, wrist 12 mm. Those errors also move every limit and 02-A4's desk guard | `BG:94–125`; `INO:111–114` (claw trim only) | Per-joint trims saved in NVS; a square/level calibration step; turn each MG996R double-arm horn end-for-end and keep the better fit (the two orientations are half a tooth apart, so ±3.6°) |
| SYS-08 | Should fix | Interfaces (claw) | Rack/pinion stack-up. Rack B is pushed onto the wrist plate (tight side): worst case −0.20 mm backlash, −0.30 tip clearance, ≈0 at RSS. Rack A floats 0.25 mm up to the top wall: up to 0.78 mm backlash, only 1.2 of the 2 mm working depth. The largest term is pinion eccentricity on the horn hub (0.3 mm diametral clearance) | `CF:37, 41`; pinion `model.py:25`; specs ±0.15 | Centre the pinion on the hub (≈0.1 mm fit); 0.3–0.4 mm total backlash; turn the pinion by hand through the full stroke before gluing or closing |
| SYS-09 | Should fix | Assembly order | Build-guide steps that contradict the CAD or each other: base screwed down before the cradle, ESP32 and bus go in from below; jack, capacitor and bus fitted to a powered system; "upright facing +X" should be +Y; claw servo "from behind" (its tabs can't pass the window); step 12 "redo step 9" | `BG:95–103, 112, 126, 143`; base `model.py:43`; claw-frame `model.py:6–8` | Reorder §4 (details below); fit the claw servo from the front, case bottom first |
| SYS-10 | Should fix | Cables | Lead lengths through every joint's range (best-case routing): claw ≈560, wrist ≈520, elbow ≈430, shoulder ≈260 mm. Yaw loop: 56 mm of slack stored under the disk rim, beside the ring-tab screw heads. 5 / 5 / 2.6 mm pinch gaps at the shoulder, elbow and wrist. The camera cable starts ≈100 mm outboard | Cable-path calc; base `model.py:30`; 01-S5, 01-S7 | 40–50 cm extensions for claw and wrist; junctions outside the base; the yaw loop hangs outside r 52; cross each joint outside the servo body; tie the USB cable at the wrist-plate tail |
| SYS-11 | Should fix | Failure modes | **Desk crash:** the Brio lands first in 37 % of desk-collision poses; the wrist MG90S back-drives at 2.8 N at the fingertips. **Claw stall:** every grasp at `g 0`, and the PC `c` key, holds the MG90S stalled (≈0.7 A, ≈4 W). **Boot:** the yaw swings first at full speed | Collision sweep; `PC:91`; `INO:71–83`; 02-A2, A4, A7, N-A2 | 02's guard and NVS pose; grip to width − 1–2 mm with a time limit; attach claw → wrist → elbow → shoulder → base; keep the camera above the claw in approach moves |
| SYS-12 | Note | Stability | Free-standing, the arm tips in every extended pose: CoM 18–37 mm past the edge straight out, 8–16 mm past it in mid-reach picks. The guide's mandatory screws are right | Tipping calc; `BG:52, 100` | Offer a board option (≥ 200 × 200 mm, ≥ 0.4 kg) or 0.5–0.9 kg of ballast |
| SYS-13 | Note | Camera | Fingertips at v +0.10…+0.15 of the half-height, u 0; open jaw tips at u ±0.42 / ±0.52 / ±0.66 (90 / 78 / 65° presets). The cover fills the bottom 37–41 % of the frame. Fingertips 72–81 mm from the lens; no published close-focus distance | Ray-cast of `CF:93–99` | Use the 65° preset; check and lock focus at ≈75 mm; crop the bottom 40 % in vision code |
| SYS-14 | Note | Torque | Margins that are fine: elbow 17–25 %, wrist 5–22 % of stall; no static load on yaw. The camera's CoM is 3 mm behind the wrist axis, so it balances the claw | Torque sweep | None |
| SYS-15 | Note | Claw force | A realistic stall grip is 6–8.5 N per jaw, not 12: the finger sits 35–53 mm from the rack, and the moment presses the rack onto the lip and the front plate. Still enough for ≈200 g by friction | Friction estimate | Keep 12 N as the safety figure; don't size grips on it |
| SYS-16 | Note | Serviceability | What comes apart to replace each servo. The yaw clamp screw can be re-tightened in place with a hex L-key if it is a socket head | Geometry | Specify ISO 4762 for the yaw M3 × 16 (`BG:45`) |
| SYS-17 | Note | Workspace | With s > 90 the arm reaches the desk behind the base, over the jack and the cable slot. The ESP32 USB cable leaves under the main pick zone. Camera plus plug make the arm ≈160 mm wide from the yaw axis | Sweep; base `model.py:28` | Keep those zones clear; right-angle USB plug |
| SYS-18 | Note | Docs vs CAD | Ring size, fastener count, stale servo-torque reference, end-effector mass, forearm "SG90", blank assembly spec, viewer demo poses | Details below | Correct the texts |
| SYS-19 | Note | Process | The five claw jobs already carry sliced G-code while their DESIGN gate is open. SYS-01 and 01-B2 will change their geometry | `status.json` (DESIGN, gate null); `part.gcode` 01:24 | Don't approve or print the claw G-code; re-slice after the redesign |

---

## Details

### SYS-01. Blocker: the claw can't be assembled, and couldn't be serviced

**What the guide says.** Assembly order in `BG:127–140`:

1. Step 9: the pinion goes on the claw servo at its closed angle (`f`).
2. Step 10: the cover goes on.
3. Step 11: each jaw slides into its channel from the open end of its neck slot: "push gently and wiggle until the teeth mesh. Keep pushing until the finger reaches the claw's centre line."

Slot A is open only at −y and slot B only at +y (cover `model.py:49–50`), so the jaws can only enter that way.

**Why it can't work.**

- The rack is 44 mm long (`CF:49`). At the closed pose, the part of rack A that leads during insertion (y +6 to +28) lies beyond the pinion, so it must travel through the mesh.
- **Mesh sweep** (jaw A moved along its insertion path, pinion fixed at the closed phase, manifold booleans):

  | Jaw A offset from closed (mm) | −40 | −32 | −31 | −30 | −20 | −10 | 0 |
  |---|---|---|---|---|---|---|---|
  | Overlap with the pinion (mm³) | 0 | 0 | 1.4 | 11.3 | 35.0 | 14.3 | 0 |

- From first contact at −31 mm, every millimetre needs the pinion to turn. That is 197° in the closing direction to reach the closed pose, or 57° (9 mm) beyond the fully open pose.
- **Servo travel available:** the claw is closed at ≈20° and open at ≈160° of the servo's 0–180°.
  - Even starting from 180°, the servo has only 160° left to the closed angle.
  - The jaws would stop ≈5.8 mm short each, leaving a gap of at least ≈12 mm.
  - Getting even that far means back-driving the MG90S into its end stop. ProtoSupplies warns this strips gears [3].
- **Second jaw:** once jaw A reaches its closed pose, its neck stops against the closed end of slot A. The pinion then can't turn in the closing direction, so jaw B can't be pushed in at all.

**Other orders fail too.**

- **Cover over fitted jaws:** the cover can't be lowered onto the frame with the jaws already meshed. It overlaps the necks by 73–210 mm³ at every height from 2 to 30 mm above its seat.
- **Cover slid along y:** 90–210 mm³ of overlap; one of the two slots always presents its closed end.
- **Pinion after the cover:** impossible, because the front-plate hole is Ø5 (`CF:75`).
- **Claw servo after the cover:** impossible. It can't come in from behind (its tabs are wider than the window, SYS-09), and the cover blocks the front.
- **Service:** the three parts lock each other.
  - The cover can't come off with the jaws in.
  - The jaws can't come out without the pinion turning 57° past fully open.
  - The pinion can't come out with the cover on.

  Step 12's "redo step 9 from `f`" (`BG:143`) is therefore impossible too.

**Fix A (smallest change): fit the pinion last, through the front plate.**

1. Set `ACCESS_D` to ≥ 20.6 mm: the pinion tip diameter of 20 mm plus clearance.
2. Assemble in this order:
   - frame;
   - claw servo;
   - with the bare spline, find which way opens: positive about claw +x;
   - cover and camera mount;
   - slide both jaws in by hand to the fully open position. Without the pinion they slide freely: 0 mm³ interference with the cover, frame or servo;
   - type `g 44`;
   - push the pinion, with its trimmed horn, axially into both racks;
   - fit the M2 × 10;
   - set the trim with `k`.
3. Checked with the meshes: from 14 mm out to fully seated, the pinion touches neither jaw (0.00 mm³ at every step). The only obstruction is the present Ø5 hole.
4. Nudge the jaws by up to half a tooth (1.6 mm) to match the pinion's phase.
5. Service is the same in reverse. The pinion comes out at any time, then the jaws, then the cover.
6. **Cost:** the Ø20.6 hole merges with both neck slots, so the claw's DFM and strength reviews must re-check the front plate.

**Fix B (stiffer): split the cover.**

- The top wall and lip become one part; the front plate becomes a separate part.
- With the front plate off, both racks slide axially into mesh at the closed pose.
- The front plate then goes on from the front, over closed neck slots. It must widen to about ±40 mm, because neck A reaches y −36 at 44 mm open.

**Either way:**

- Add an insertion-path check to `AC`: sweep each part along its insertion direction, in `BG` order. Static-pose checks can't see this class of error.
- Do this in the same redesign as 01-B2 (the MG90S spline sits ≈3 mm higher, pushing the pinion into the cover) and 01-B1 (servo leads can't pass the closed windows).

### SYS-02. Should fix: the shoulder carries the camera at 42–54 % of stall

**Mass model.**

- **Printed parts:** each job's sliced filament mass (`slice_stats.json`, per copy), with the centre of mass from its CAD solid.
- **Bought parts:** datasheet masses. Hardware and cable allowances are listed under Assumptions.
- **End effector beyond the wrist horn:** ≈165 g. That is the printed claw 60.1 g, mount 11.2 g, claw MG90S 13.4 g, Brio 63 g, thumb screw and screws ≈10 g, horns and cable ≈7 g.
- **Upper bound:** solid PETG density (1.27 g/cm³) instead of sliced masses gives 172 g. That matches the base `strength_calc.py`.

**Worst static gravity torque inside the servo travel.** Sliced masses. Stall at 6 V: MG996R 1079 N·mm, MG90S 216 N·mm [1][2].

| Joint | Camera, 0 g | Camera, 20 g | Camera, 50 g | No camera, 50 g | Worst pose |
|---|---|---|---|---|---|
| Shoulder (MG996R) | 457 (42 %) | 507 (47 %) | 583 (54 %) | 425 (39 %) | arm straight out |
| Elbow (MG996R) | 180 (17 %) | 211 (20 %) | 257 (24 %) | 186 (17 %) | forearm and claw level |
| Wrist (MG90S) | 12 (5 %) | 25 (11 %) | 44 (20 %) | 48 (22 %) | claw level |

With solid masses, the shoulder reads 500 / 551 / 626 N·mm (46 / 51 / 58 %).

**Continuous rating.**

- TowerPro gives no continuous torque. Its running current of 0.5–0.9 A against a 2.5 A stall at 6 V [1] puts normal running at ≤ ≈1/3 of stall.
- Holding the empty arm out with the camera already needs ≈1.06 A. With 50 g it needs ≈1.35 A. (Current taken as proportional to torque.)
- So holding at full reach is above the datasheet's running band even with no payload. That means a hot shoulder servo, and sag on clones that fall short of the datasheet torque (01-N1).

**Payload the shoulder allows**, sliced masses, payload 10 mm behind the fingertips:

| Configuration | ≤ 50 % stall, static | ≤ 50 % stall, ×1.3 moving | ≤ 1/3 stall, continuous |
|---|---|---|---|
| Camera, arm straight out | 33 g | none | none |
| No camera, arm straight out | 95 g | 46 g | 24 g |
| Camera, top-down carry at in-plane x 140–160 mm | 185 g | – | 46 g |
| Camera, top-down carry at x 160–180 mm | 130 g | – | 9 g |
| Camera, top-down carry at x 180–200 mm | 86 g | – | none |
| Camera, top-down carry at x 200–220 mm | 50 g | – | none |

"Top-down carry" means the claw vertical, the object 20–60 mm above the desk, and the best pose inside the current servo travel. Close in, the claw's friction grip limits payload to ≈200 g (SYS-15).

**What this means.**

- The camera package (Brio, mount, thumb screw, extra cable, ≈88 g) costs 157 N·mm at the shoulder at full reach. That is 15 % of stall, or ≈62 g of payload: more than the whole 50 g rating.
- `BG:8`'s "20 g at full reach with the camera" works out to 47 % static and ≈61 % while moving. That is fine for a short lift; it is not fine for holding.
- The claw-frame strength check, written during this review (`20261026-arm-claw-frame/strength.md`, torque section), reaches the same shoulder figure with solid masses: 495 N·mm, 49 % of 1000 N·mm. It rates 20 g within ≈240 mm of the shoulder axis. The table above adds the continuous-holding limit and the reach dependence.

**Fixes**

1. **Payload table.** Replace `BG:6–8` and `AP:39` with a payload-by-reach table like the one above.
2. **Park pose.** Use `s 90`, `e 90` (or the SYS-03 equivalent) when idle; the shoulder torque is then ≈0.
3. **Full-reach work**, if it matters, needs one of:
   - **A gravity-compensation spring at the shoulder.** A zero-free-length equivalent with k·a·h ≈ 460–510 N·mm cancels the cos θ gravity term. Example: a pin 20 mm out on the upper link's 25 mm tail (`X0 = −25`), anchored 30 mm below the shoulder axis on the upright, gives k ≈ 0.8 N/mm. It adds up to ≈40 N on the upright and the shoulder bearing, which the strength review must check.
   - **A 20–25 kg·cm standard-size servo for the shoulder only.** Check its body, tab spacing and spline against the 41.1 × 20.1 mm window and the horn pocket.
   - **A lighter camera** (USB board camera, ≈10–20 g) if eye-in-hand is a must. Or put the Brio on the turntable (eye-to-hand): that removes the 157 N·mm here and most of SYS-04.

### SYS-03. Should fix: re-centre the elbow window for desk work

`INO:24–30` gives every joint servo 0–180°. Centred on "straight", that is elbow ±90°. 02-A5 already corrects the quoted reach (`BG:4`, 76–260 mm) to ≈123–247 mm. The problem goes further: the elbow window wastes half its travel on upward bends that desk work never uses, and picks need a vertical claw.

**Desk reach.** Collision-free poses with the fingertips 0–5 mm above the desk, yaw 0, shoulder centred on upright:

| MG996R travel | Elbow window | Claw within 20° of vertical (in-plane x) | Any claw angle | Lowest fingertip possible |
|---|---|---|---|---|
| 180° (as the sketch assumes) | −90…+90 | 117–218 mm | 81–241 mm | 63 mm into the desk |
| 180° | **−150…+30** | **32–218 mm** | 1–241 mm | 63 mm into the desk |
| 150° | −75…+75 | 142–205 mm | 103–215 mm | 25 mm into the desk |
| 150° | −135…+15 | 58–205 mm | 24–215 mm | 37 mm into the desk |
| 120° (TowerPro's stated rotation, see 02-A8) | −60…+60 | **none** | **none** | **32 mm above the desk** |
| 120° | −120…0 | 81–167 mm | 59–170 mm | 13 mm into the desk |

The table comes from a 3° grid. A 1° search around the near limit gives 117 mm for the present window and 29 mm for the re-centred one.

**What re-centring buys.**

- Centred at −60°, the elbow window more than doubles the top-down pick zone.
- The arm still reaches the desk if your MG996R turns only 120–150°.
- `AC`'s own "pick from desk" pose (−30, 70, −120, −40) becomes reachable, and it is collision-free.
- `AC` found the elbow collision-free to ±170°, so −150° is safe for self-collision.

**Fix**

1. In §4 step 6, fit the forearm with the elbow servo at 90° and the forearm 60° below the upper link's line. Use a printed 60° gauge.
2. Change the elbow mapping everywhere (sketch, PC code, the guide's §5 table). In 02-A4's guard, `q2 = EL_SIGN * (e - 150)`.
3. Measure the real servo travel first (02-A8).

### SYS-04. Should fix: the camera's sideways weight on every pitch joint

**Why the camera loads every pitch joint.**

- Each link mounts on the front of the previous servo, so the arm plane steps outboard (`AP:37`). The claw's back face is at world Y 53.4.
- The Brio's centre of mass sits at Y ≈ 118, 64 mm further out (`CF:93–94`).
- Gravity is always perpendicular to the three horizontal pitch shafts, so this offset puts a bending moment on each output shaft and horn joint. The moment is the same in every pose.

**Moment** perpendicular to the shaft, about the servo's case-top bearing plane:

| Joint | No camera, 0 g | Camera, 0 g | Camera, 50 g | Camera's share | Hub radius | Clamp-screw tension, static |
|---|---|---|---|---|---|---|
| Shoulder | 80 | 169 | 204 | 86 | 5.5 | 31–37 N |
| Elbow | 41 | 109 | 132 | 67 | 5.5 | 20–24 N |
| Wrist | 19 | 69 | 81 | 50 | 3.6 | 19–23 N |

Moments in N·mm, hub radius in mm.

**How it is carried.**

- When a link is level, this moment acts along the horn's arms. Across them the link rests only on the horn hub, and the clamp screw holds it down.
- The screw needs a preload above these tensions (×1.3 while moving).
- That only works if the screw really clamps. 01-S2 shows that each clamp screw has to reach 5.0–6.9 mm into a spline thread whose depth is unknown. A screw that bottoms out leaves no preload, so the link rocks on its hub. Expect a wobbling camera view and creep in the PETG under the washer.

**Stale spec loads.** The turntable spec still lists "≈100 N·mm about X static" for the upright (`20261025-arm-turntable/spec.md:29`, old gripper, no camera). About the upright's mid-plane it is now ≈205 N·mm (0 g) to ≈250 N·mm (50 g). The round-4 strength checks of the turntable, upper link, forearm and claw frame must use the camera case.

**Fix**

- Settle 01-S2: measure each spline's screw-hole depth, then pick clamp lengths that stop ≥ 0.5 mm short.
- Re-torque the clamp screws after the first hours of use, because PETG relaxes.
- If the camera stays on the wrist, accept these loads. Otherwise see SYS-02, item 3.

### SYS-05. Should fix: the turntable runs on the servo shaft

**How the turntable is held.**

- The Ø96 disk sits only on the base servo's double-arm horn, clamped by one M3 screw (turntable `model.py:3–8`, `Z0 = 16.5` at line 18).
- The ring has a 1.5 mm gap at r 44 (ring `model.py:15–18`). It touches only after 1.95° of tilt, which is a 9.3 mm drop at a 273 mm reach.
- So in normal use, the MG996R's two output bearings [1], the plastic horn and the clamp screw carry everything.

**Loads on the base servo's output**

| Pose | Overturning moment | About the horn's long axis (hub support only) | Across the arms (±17.5 mm support) | Axial |
|---|---|---|---|---|
| Arm straight out, 0 g | 518 | 173 | 489 | 4.4 N |
| Arm straight out, 50 g | 654 | 210 | 619 | 4.9 N |
| Arm upright, 50 g | 213 | 210 | 36 | 4.9 N |

Moments in N·mm.

**Why the hub direction matters.**

- The 173–210 N·mm about the horn's long axis comes from the arm's sideways offset, so it is there in every pose.
- The guide lays the horn along the turntable's X (`BG:111`). The disk therefore rests on the Ø11 hub in that direction.
- The clamp screw then carries ≈31–38 N permanently, plus ×1.3 while moving.
- **Effects:**
  - the whole arm rocks on the hub and on the servo's bearing play;
  - the plastic horn creeps;
  - the ring stays out of contact, so it never acts as a bearing.

**Fixes**

1. **Disc horn.** Use the MG996R's round Ø25 disc horn under the turntable instead of the double arm. The disk's underside is flat (no pocket, turntable `model.py:67–68`), so only the drilled screw holes change. It supports the disk ±12.5 mm in every direction, 2.3 times the hub's lever.
2. **Ring as a bearing.** Cut `RUN_GAP` to 0.3–0.5 mm and add PTFE tape, or 3 small ball bearings as rollers on the ring top.
   - The friction torque is ≈μ times the overturning moment: ≈200 N·mm at μ 0.3, ≈65 N·mm with PTFE.
   - Either is acceptable against the yaw servo's 1079 N·mm, which carries no gravity load.
   - Sand to an even gap, because the servo shaft and the ring now share the load.
3. **Or** a lazy-susan bearing between the base and the disk.

### SYS-06. Should fix: moves start and stop as velocity steps

**What the sketch does.** `runMove()` (`INO:51–66`) interpolates linearly at 1° per 15 ms, which is 66.7°/s from the first step. It has no acceleration limit and writes whole degrees.

**Inertia, arm straight out with the camera:**

- shoulder 0.0081 kg·m² (0 g) and 0.0114 kg·m² (50 g);
- yaw 0.0107 and 0.0145 kg·m².

**Extra torque needed to reach 66.7°/s:**

| How fast | Shoulder | Yaw |
|---|---|---|
| In 50 ms (α ≈ 23 rad/s²) | +186–261 N·mm (×1.4 on 457–583) | +246–334 N·mm |
| In one 15 ms step (α ≈ 78 rad/s²) | +630–890 N·mm | +830–1130 N·mm (at or above stall) |
| With a 200 °/s² ramp (3.5 rad/s²) | +28–40 N·mm | +37–51 N·mm |

**Effects**

- The shoulder and yaw servos saturate at stall for the first tens of milliseconds of every move with the arm out. Expect current spikes (02-N-A1) and a lag, then an overshoot.
- At every stop, the end effector rings on the horn joints' play (SYS-04). The camera image shakes at the end of each move, which is exactly when vision needs a still frame.
- Whole-degree writes give 4.8 mm steps at the fingertips from the shoulder alone at full reach. The MG996R dead band is 5 µs ≈ 0.45° [1].

**Fix**

- Use a trapezoidal (or S-curve) profile in `runMove()` at 200–300 °/s², with the same 66.7°/s cruise.
- Write `servo.writeMicroseconds()` with 0.1° resolution.
- Wait ≈200 ms after `ok` before grabbing a frame.

### SYS-07. Should fix: horn indexing and no per-joint trims

**Spline steps.** Every horn is fitted with its servo at 90° and the link "straight up" or "in line" (`BG:94–125`). The spline only allows discrete positions:

- MG996R, 25 teeth: 14.4° steps, so up to ±7.2° off;
- MG90S-class micro servo, ≈20–21 teeth: ≈17–18° steps, so up to ≈±9° off.

**Worst fingertip error at full reach:**

| Joint | Error |
|---|---|
| Base | 7.2° × 284 mm = 36 mm sideways |
| Shoulder | 7.2° × 273 mm = 34 mm |
| Elbow | 7.2° × 173 mm = 22 mm |
| Wrist | 9° × 76 mm = 12 mm |

**What depends on it.**

- Every joint limit, the guide's angle tables, any PC kinematics, and 02-A4's desk guard (its margins are 8 mm) shift by the same angles.
- The sketch trims only the claw (`k`, `INO:111–114`).

**Fix**

1. **Trims.** Add per-joint trims (`t <joint> <deg>`), saved in NVS as 02-A7 does for the pose. Apply them before the clamps and the guard.
2. **Calibration step in §4.** Set the upper link vertical at `s 90` with a square or a phone level. Then the forearm in line at `e 90` (or at −60° per SYS-03), the claw in line at `w 90`, and the arm along +X at `b 90`.
3. **Horn flip.** For the three MG996R double-arm horns, try the horn turned end-for-end in its pocket and keep the better fit. On a 25-tooth spline the two orientations are half a tooth apart, so the residual drops to ±3.6°. The horn's screw holes are symmetric, so the drilled pilots still match.

### SYS-08. Should fix: rack and pinion stack-up

**Nominal.** Each member is 0.1 mm thinner (`CF:37`), giving 0.2 mm backlash and 0.25 mm tip clearance at the nominal centre distance.

**Which way each rack moves.** The separating force (tan 20° of the tooth load):

- pushes rack B down onto the wrist plate, which is fixed;
- lifts rack A through its 0.25 mm sliding clearance (`CF:41`) against the top wall.

**Contributors to the centre distance:**

- pinion eccentricity on the trimmed horn: up to 0.15 mm (the hub pocket prints 0.3 mm over, pinion `model.py:25` + `HOLE_COMP`);
- claw-servo axis: ±0.1 mm (set by the tab screws);
- wrist-plate top: ±0.15 mm (spec);
- rack pitch line to back face: ±0.15 mm (spec);
- top wall: ±0.15 mm (spec).

**Result**

| Rack | Worst-case centre distance | Backlash | Other effect |
|---|---|---|---|
| B (tight side) | −0.55 mm | −0.20 mm (binding) | Tip clearance −0.30 mm. RSS gives ≈0 backlash, so expect a tight spot once per pinion turn from the eccentricity |
| A (loose side) | +0.80 mm | ≈0.78 mm | Only 1.2 of the 2 mm working depth engaged; jaw-gap play up to ≈1 mm |

**Fix**

- Make the pinion's hub seat a light fit, ≈0.1 mm, so it centres. Glue only after a dry run.
- Raise the total backlash to 0.3–0.4 mm (each member 0.15–0.2 mm thinner); printed gears usually need it.
- Add an acceptance step before the cover goes on: turn the pinion by hand through the full stroke, with no tight spot.
- Re-run this stack-up after 01-B2 moves the pinion.

### SYS-09. Should fix: build-guide steps that contradict the CAD

- **Steps 1–2** (`BG:95–103`):
  - Step 1 says "wire everything… leave the power on while you fit the horns". Step 2 then fits the jack, the capacitor and the power bus into that powered system.
  - Step 2 screws the base to the desk first, and only then fits the cradle "M3×10 from below" and drops the ESP32 in.
  - The base is an open-bottom box (base `model.py:43`). Once it is screwed down, the cradle screws, the ESP32 and the bus are out of reach. So are the arm leads' connections at step 14.
  - **Fix:** build the whole base upside down on the bench, wire it, then power it and centre the servos. Screw it to the desk last. End the four arm leads in junctions outside the cable slot (SYS-10).
- **Step 4** (`BG:112`):
  - "Upright facing +X" is wrong: the upright's faces point ±Y (turntable `model.py:22`).
  - The CAD puts the shoulder shaft, which comes out of the upright's front face, towards +Y, so at `b 90` the arm reaches over the +X (USB) wall.
  - Mounted 90° off, the ±90° yaw range swings round to face the cable slot and the jack.
  - **Fix:** reword it as "the upright's front face, where the shoulder shaft will come out, towards +Y".
- **Step 8** (`BG:126`, also claw-frame `model.py:6–8`):
  - "Slide the claw MG90S through the bulkhead window from behind" can't work. The tabs span 32.2 mm and the window is 22.9 × 12.6 mm, and the CAD seats the tabs on the bulkhead's front face.
  - **Fix:** fit it from the front, case bottom first. Its lead must cross the window then (01-B1).
- **Step 12** (`BG:143`): "redo step 9 from `f`" means taking the pinion off. That needs Fix A of SYS-01.

### SYS-10. Should fix: cables through the joint ranges

01-S7 already shows that three leads need extensions. The method here follows the actual routing, as an estimate.

**Method.**

- Each lead is tied 6–14 mm from each joint axis, which is best practice and the best case.
- The free loop at each joint covers the largest distance between its two tie points over the servo travel, plus 30 % slack.
- Paths run from each servo's lead exit to the bus inside the base.

| Lead | Path | Stock lead | Extension needed (before spiral-wrap overhead) |
|---|---|---|---|
| Claw MG90S | ≈560 mm | 24–25 cm [3] | ≈310 mm |
| Wrist MG90S | ≈520 mm | 24–25 cm | ≈270 mm |
| Elbow MG996R | ≈430 mm | 30 cm [1] | ≈130 mm |
| Shoulder MG996R | ≈260 mm | 30 cm | none |

A 30 cm extension (01-S7) is marginal for the claw lead once spiral wrap and real tie points are added. Use 40–50 cm for the claw and the wrist.

**Yaw loop.**

- From a tie point at the turntable's rear rim to the cable slot at (−40, −36) (base `model.py:30`), the distance varies from 25 to 81 mm over ±90° of yaw.
- So ≈56 mm of slack has to be stored somewhere at the short end.
- Left to itself, it lies on the base top under the disk rim. That is where the ring-tab screw heads sit (r 47.5, Z 3–5.4, at 150° and 270°, either side of the slot at ≈222°) and where the ring's 1.5 mm gap is: snag points.
- **Fix:** tie the bundle to the upright's rear gusset and to a clip at the slot, so the loop hangs vertically outside r 52, never under the rim.

**Pinch gaps.** These are the gaps between each link's back face and the servo case behind it:

- shoulder: 5 mm (Y 9.5 vs 4.5);
- elbow: 5 mm;
- wrist: 2.6 mm (claw frame vs the MG90S case top).

The horns turn inside these gaps. Leads must cross each joint around the outside of the servo body, never through these gaps.

**Connectors.** Put the extension junctions on the turntable side or just outside the slot, not at moving joints. The 2.54 mm housings are bulky. This also solves SYS-09's access problem.

**Camera cable.**

- The port is on the camera's back (01-S5), ≈100 mm outboard of the claw's back face.
- A straight plug points backwards and outboard. Its end sits at Y ≈ 157 at the home pose. It adds little to desk collisions (6.3 % → 6.4 % of the servo box), but it leaves a 100–150 mm free span back to the wrist.
- **Tie point.** Tie the cable at the wrist-plate tail, ≤ 8 mm from the wrist axis, so wrist rotation only twists it.
  - A tug there loads the tail through a far shorter lever than a tug at the camera.
  - A tug at the camera is the case that `20261026-arm-claw-frame/strength.md` fails: SF 0.84 under a 10 N tug, in the same tail.
  - Leave a strain-relief loop between the plug and the tie, so the arm's own motion never pulls the plug.
- **Keep ties clear of the rack exits.** The racks stick 5.7 mm out of the cover's sides at 44 mm open (x 19.4–27.4). `BG:150` ("zip-tie it to the claw frame") should say where.
- **Cable stiffness.** A stiff USB-3 cable bent to R ≈ 30 mm at the wrist can push tens of N·mm on the wrist servo. That is comparable to its 12–44 N·mm gravity load. Use the thin cable `BG:56` suggests (1080p is enough, 02-A12).

### SYS-11. Should fix: failure modes in use

**Desk crashes** (firmware guard: 02-A4).

- **How often:** in a 26 011-pose sample of the servo travel, 1632 poses (6.3 %) put a part into the desk.
- **What hits first:** in 37 % of those poses the Brio touches first; the jaws take the rest. The Brio is the most expensive part, and it hangs on a 1/4" thread in its plastic body.
- **Near-level approaches are the trap.** With the claw level, the camera hangs 51 mm below the claw axis. At `s 0`, `e −30`, `w 0` the camera is 3.7 mm above the desk while the fingertips are still 19 mm up.
- **Forces in a crash:**
  - The shoulder and elbow can push 7–13 N into the desk at 80–150 mm lever.
  - The wrist MG90S back-drives as soon as the in-plane force at the fingertips exceeds 216 / 76 = 2.8 N.
  - So in any crash, the wrist gearbox and its plastic horn spline see 3–5× their stall torque. After them come the jaw tips (bevelled to ≈2.5 mm) and the necks.
  - If the base isn't screwed down, the whole arm topples (SYS-12), camera first.

**Claw stalled on an object.**

- `g 0` on an object, the `f` and `c` commands, and the PC preview's `c` key (`arm.claw(0.0)`, `PC:91`) all command full closure.
- The MG90S then holds at stall, ≈0.7 A [3] or ≈4 W at 6 V, for as long as the object is held.
- Within minutes that overheats the servo. It also softens the 6 mm PETG bulkhead its tabs are screwed to (PETG softens at ≈70 °C).
- 02-N-A2 gives the firmware rule: close to the object's width minus 2 mm.
- **Also:** make the PC key close to a measured width, and time-limit any squeeze, backing off 1–2° after ≈2 s.

**Boot snap** (02-A2, A7). The mechanical side:

- `setup()` (`INO:71–83`) attaches base → shoulder → elbow → wrist → claw, 300 ms apart, at full servo speed (MG996R ≈430 °/s at 6 V [1]).
- So the yaw swings first, with the arm still wherever it sagged during the reset.
- At 430 °/s the end of the extended arm moves at ≈1.5 m/s, with ≈0.3 J of kinetic energy about the shoulder.
- **Fix:** with 02-A7's stored pose, attach claw (open) → wrist → elbow → shoulder → base, and ramp (SYS-06).

**End stops.** `w 0` and `w 180` (500 / 2500 µs) can drive the wrist MG90S into its internal stop (02-A8). That is a continuous stall on the joint that also carries the camera.

### SYS-12. Note: free-standing stability

The whole robot is ≈665 g plus payload, on a 110 × 104 mm footprint. Free-standing, it tips in every extended pose:

| Pose | Centre of mass vs base edge |
|---|---|
| Arm straight out, yaw 0 | x 73 mm (0 g) / 87 mm (50 g), against the edge at 55 mm |
| Arm straight out, yaw ±90° | 23–37 mm past the 52 mm edge |
| Mid-reach top-down pick (s 20, e −60, w −50) | 8–16 mm past the edge |

The guide's "required" desk screws (`BG:52, 100`) are right. Uplift per screw is small.

For users who won't drill a desk, offer either:

- **A board:** screw the base to a board of at least 200 × 200 mm and 0.4 kg (12–18 mm plywood or MDF). The centre of mass then stays ≥ 40 mm inside the board's edge in every pose.
- **Ballast:** 0.5–0.9 kg fixed inside the base gives a safety factor of 1.5.

Put the rubber feet under the board, not under screwed pillars.

### SYS-13. Note: what the camera sees

**Method.** Ray-cast from the lens through the claw meshes:

- camera pose from `CF:93–99`, lens at the camera frame's (13.5, 0, 13.5);
- rectilinear 16:9 model;
- Logitech's angles: 82.1 × 52.2° at 90° diagonal, 70.4 × 43.3° at 78°, 58.1 × 34.7° at 65° [5].

**Image coordinates** (u = horizontal, v = vertical, both −1…+1):

| Point | 90° | 78° | 65° | Distance from lens |
|---|---|---|---|---|
| Fingertips, centre | u 0, v +0.10 | u 0, v +0.12 | u 0, v +0.15 | 76 mm |
| Jaw tips at 44 mm open | u ±0.42 | u ±0.52 | u ±0.66 | 81 mm |
| Object 30 mm beyond the tips | v +0.37 | v +0.46 | v +0.58 | 104 mm |
| Cover's top front edge (lower limit of the useful view) | v −0.17 | v −0.21 | v −0.27 | 27 mm |
| Share of the image filled by the cover | 40.7 % | 38.9 % | 37.0 % | – |
| A 16 mm cube held between the fingertips | 3.3 % | 5.1 % | 7.9 % | – |

**What this shows.**

- The jaws stay in view over the whole 0–44 mm stroke in every preset.
- They open across the image's long axis, a good use of the frame.
- The lower 37–41 % of every frame is the claw's own top wall.
- Between the fingers, only the top 3–4 mm of the grip faces is visible near the cover. The object is seen from above and in front.
- Logitech publishes no minimum focus distance (autofocus only [4][5]).

**Fix**

- Check that the fingertips at ≈75 mm are sharp, then lock the focus (Logi Tune, or the UVC focus control from OpenCV).
- Prefer the 65° preset.
- Mask the bottom 40 % of the frame in vision code.

### SYS-14. Note: margins that are fine

- **Elbow:** 180–257 N·mm, 17–24 % of stall.
- **Wrist:** 12–48 N·mm, 5–22 %.
- **Yaw:** no static load on a level desk. It needs only inertia torque (SYS-06).
- **Camera at the wrist:** its centre of mass is 3.25 mm behind the wrist axis. It nearly balances the claw: wrist torque 12 N·mm with the camera, 15 N·mm without.

### SYS-15. Note: realistic claw force

At 216 N·mm the pinion pushes 24 N in total, 12 N per rack (`BG:4`, `BG:182`). But the grip face is 35–53 mm in front of the rack and 9 mm off its pitch line. The resulting moments press the rack onto the lip and the front plate along its ≈38–44 mm guided length.

**Friction model** (PETG on PETG, μ 0.25–0.35):

- grip force per jaw ≈ 12 N / (1 + 2μ·e/L + small terms);
- e = finger offset, L = guided rack length.

**Result:** about 6–8.5 N per jaw at stall, lowest when gripping with the fingertips at full opening.

- There is no self-locking: the friction scales with the grip force, not the drive force.
- That is still enough for ≈200 g held by friction (μ 0.3), against the 50 g rating.
- Keep 12 N in §7 as the safety figure. The strength cases (24 N on one jaw) remain the right conservative load.

### SYS-16. Note: what has to come apart

| To replace | Steps |
|---|---|
| Claw servo or pinion (with SYS-01 Fix A) | camera (thumb screw) → M2 × 10 → pinion out through the front → jaws slid out → mount and cover (2 top, 2 front screws) → 2 tab screws → servo out to the front. Nothing on the wrist comes apart. Without Fix A: impossible without breaking parts |
| Wrist servo | all of the above, plus the claw servo, which covers the M2 × 12 wrist clamp (claw-frame `model.py:6`) → frame off → 2 × M2 × 12 tab screws in the forearm |
| Base servo | upper link (clamp) → shoulder servo (4 tab screws, it covers the yaw clamp) → turntable → 4 tab screws |

**Re-tightening the yaw clamp in place.** The shoulder servo body bottoms at Z 50.6, while the yaw clamp screw head is at Z ≈28.3. That 22 mm of headroom fits a 2.5 mm hex L-key coming in from the side. So specify a socket head (ISO 4762) for that M3 × 16; `BG:45` says only "M3 × 16 screw".

### SYS-17. Note: workspace

- **Plane offset.** The arm plane is 76 mm off the yaw axis (fingertips at Y 75.9). PC-side kinematics must include it. `PC` has no inverse kinematics yet.
- **Reaching behind the base.** With `s` past 90° the arm reaches the desk behind the base (in-plane x −61 to −221 mm), over the DC-jack wall and the cable slot. Keep that zone clear, or bound the shoulder in the guard.
- **ESP32 USB cable.** It leaves the +X wall at (55, 28) mm, 31.5 mm above the desk (base `model.py:28`), under the main pick zone near yaw 0. Route it sideways or use a right-angle plug.
- **Width.** The camera and its rigid back plug make the arm ≈160 mm wide from the yaw axis at the wrist. Keep walls and monitors ≥ 200 mm away on that side.

### SYS-18. Note: docs that contradict the CAD

01-N8 and 02 already cover the stale README and BOM text. The rest:

- **Ring size.** `AP:60` says "Support ring r 41–44.5, 13 tall". The CAD and the ring spec say r 41–44, 15 tall (ring `model.py:15–18`).
- **Fastener count.** `AP:18` lists "M2×12 + Ø6 washer (×2)". There is one M2 × 12 (wrist) and one M2 × 10 (pinion) (`BG:46–47`).
- **Servo-torque reference.** `AP:39` cites `20261026-arm-claw-frame/strength.md` as the reference for the servo torques. That file was only written during this review (round 1, FAIL), and `AP:39`'s own figures (420 / 470 / 550 N·mm) are below both it and SYS-02. Update `AP:39` from SYS-02.
- **End-effector mass.** The claw specs (claw-frame `spec.md:25, 32`) give ≈148 g. The sliced masses give ≈165 g (172 g solid).
- **Wrist servo name.** The forearm spec (`spec.md:6, 10–11, 17`) still calls the wrist servo an SG90 (160 N·mm). It is an MG90S (216 N·mm), so its tab-screw loads rise by 35 %.
- **Blank spec.** `jobs/20261025-robot-arm-assembly/spec.md` is still the blank template.
- **Viewer demo.** `viz_export.py:202–203` demo poses use elbow −95° to −105°, outside the viewer's own ±90° slider (`:196`) and the servo travel.
- **"Safe" ranges.** `BG:164–165` ("the whole servo range is safe", "the camera clears the arm in every pose") is true for self-collision only, not for the desk (02-A4, SYS-11).

### SYS-19. Note: claw G-code ahead of its gate

The five claw jobs already hold `part.gcode` and `validation.json` (01:24–01:25), sliced before any design review existed.

- Their `status.json` still shows stage DESIGN with no gate result.
- Their round-1 `design_review.md` and `strength.md`, written during this review, are all FAIL.
- The assembly README now says not to approve or print anything.

SYS-01 and 01-B2 will change the frame, cover, pinion and jaw geometry. Delete or re-slice these G-code files after the redesign, so a stale file can't reach the approval step.

---

## Method

All scripts were run from a scratch folder and aren't committed; this report is the only file changed. Python with build123d and trimesh (manifold booleans).

- **Kinematics.** `assembly_check.py`'s `place()` chain, with each job's `design()`. All 10 named poses reproduce `assembly_check.json`'s fingertip positions to 0.1 mm.
- **Torque.** Static gravity torque about each joint axis from everything beyond it. Worst case over the servo travel: shoulder 0–180°, elbow and wrist ±90°, in 5° steps.
- **Overhung moments.** Moment of the weight beyond each pitch joint about its case-top bearing plane, perpendicular to the shaft. Checked to be the same in other poses.
- **Desk and base collisions.** 26 011 poses (shoulder and elbow in 5° steps, wrist in 10°), with each moving part as a point cloud. They were tested against the desk plane and the base box. The turntable disk, upright and shoulder servo were checked as envelopes.
- **Reach tables.** 2–3° grids, fingertips within 5 mm of the desk, collision-free poses only.
- **Claw insertion.** Jaw A swept along −y in 0.5 mm steps against the pinion fixed at the closed phase. The cover was lowered and slid over fitted jaws. The pinion was pushed axially against jaws parked at 44 mm.
- **Camera.** Ray-cast, as in SYS-13.
- **Cables.** Straight-line runs between tie points, plus worst-case loop distances over each joint's travel, plus 30 %.

## Assumptions

- **Printed masses.** Sliced filament mass per copy, including brim; centre of mass from the CAD solid. Solid density (1.27 g/cm³) gives the upper bound.
- **Servos.**
  - MG996R: 55 g; 1079 N·mm (11 kgf·cm) stall, 2.5 A stall and 0.5–0.9 A running, all at 6 V; 0.14 s/60°; 5 µs dead band; double ball bearing; 30 cm lead [1].
  - MG90S: 13.4 g; 216 N·mm (2.2 kgf·cm) at 6 V; one bearing [2]. Stall ≈0.7 A and lead 24 cm, as measured by ProtoSupplies [3].
  - The servo's centre of mass is the centre of its body box.
- **Brio 4K.** 63 g, 27 × 102 × 27 mm, tripod thread in the camera body, 2.2 m cable [4][6]; FOV as in [5]; centre of mass at the box centre.
- **Hardware and cable allowances.**

  | Item | Mass |
  |---|---|
  | Horn + clamp screw + washer, each MG996R joint | 4.2 g |
  | Wrist horn + clamp | 1.2 g |
  | Pinion horn + screw | 1.0 g |
  | Claw and mount screws | 5 g |
  | Thumb screw | 5 g |
  | ESP32 | 10 g |
  | Jack, capacitor, bus and wiring in the base | 25 g |
  | Cable on the claw / forearm / upper link, with the camera | 5 / 7 / 9 g |
  | Cable on the claw / forearm / upper link, without the camera | 2 / 3 / 5 g |

- **Payload** sits 10 mm behind the fingertips, on the claw axis.
- **Rating criteria** (TowerPro publishes no continuous rating):
  - ≤ 50 % of the 6 V stall for short holds;
  - ≤ ≈1/3 of stall for continuous holding (running current ÷ stall current);
  - "modest acceleration" = ×1.3; the present velocity-step firmware ≈ ×1.4.
- **Servo travel.** 180° over 500–2500 µs, as the sketch assumes. SYS-03 also shows the 120° and 150° cases (02-A8).
- **Other.**
  - PETG-on-PETG friction μ 0.25–0.35.
  - Spline teeth: MG996R 25; MG90S-class ≈20–21.
  - Camera plug: straight, 50–75 mm out of the camera's back (01-S5).
- **Not modelled.** Link deflection and printed-part stresses (the per-part strength reviews), servo gear backlash, horn compliance, and the MG90S height correction of 01-B2. That correction moves the claw and camera ≈3 mm outboard, which slightly raises SYS-04's moments.

## Sources

1. TowerPro, MG996R datasheet (Cornell copy): https://people.ece.cornell.edu/land/courses/ece4760/FinalProjects/f2017/kmv48_rp625/kmv48_rp625/kmv48_rp625/MG996RTowerPro.pdf
2. TowerPro, MG90S datasheet (Braude copy): https://w3.braude.ac.il/wp-content/uploads/2021/03/MG90.pdf
3. ProtoSupplies, MG90S micro servo (measured currents, lead, travel): https://protosupplies.com/product/servo-motor-micro-mg90s/
4. Logitech, Brio 4K Ultra HD webcam quick-start guide (mass, size, cable, tripod thread on the camera): https://secure.logitech.com/assets/65031/2/brio-4k-ultra-hd-webcam.pdf
5. Logitech, BRIO specifications (diagonal, horizontal and vertical FOV; autofocus): https://hub.sync.logitech.com/brio/post/brio-specifications-BJKhhCqWmecRhPD
6. Logitech, Brio setup essentials and FAQs (tripod thread under the removed clip): https://hub.sync.logitech.com/brio/post/brio-brio-4k-setup-essentials-and-faqs-EZcOqEHN0fffbPX

# Deep review 05: the hexapod as a machine

Hexapod only (`jobs/20261026-hexapod-*`). Independent review, 2026-10-26.

This slice covers how the whole robot works:

- mass and servo torque;
- gait and kinematics;
- power;
- wiring as a mechanical layout;
- assembly order and servicing;
- interfaces between parts.

The other slices are elsewhere, and this report refers to them instead of repeating them:

- Per-part printability: each job's `design_review.md`.
- Printed-part strength: each job's `strength.md`.
- Bought parts and BOM: [01-bought-parts.md](01-bought-parts.md).
- Wiring and firmware: [02-electronics-firmware.md](02-electronics-firmware.md).

## Verdict

**The geometry works. The robot does not yet walk with margin.**

What works:

- The frames put all six feet on the ground.
- No leg touches a neighbour or the body, either in the test sketch's tripod gait or in a straight-line gait with strides up to 60 mm.
- The centre of gravity always stays at least 26 mm inside the support triangle, and at least 36 mm in the gait recommended here.

Why it lacks margin:

- **Torque.** The robot weighs about 662 g, not 0.6 kg. In a tripod, the leg that stands alone on its side carries 41 % of that weight. Each femur servo therefore holds 110–127 N·mm before any dynamic factor, which is 51–59 % of the MG90S's 216 N·mm stall. The specs' own ×2 walking factor takes that past stall. The specs' 4 N foot load is 40 % too low; the new strength reviews already use 2.90 / 5.80 N.
- **Test gait.** The test sketch walks by swinging only the coxae. That forces every planted foot to slide 18–20 mm per stroke and makes the robot crab about 12° to the right. On carpet, the servos resisting the slide reach 61–89 % of stall.

Most of this is a software fix: an inverse-kinematics (IK) gait with the tibias tucked 15° inward, at the same body height.

- Every joint stays inside the collision-free ranges.
- The slide disappears.
- Peak static servo torque falls to 78–90 N·mm (36–42 % of stall).

The build also stops at wiring. Routed through the four corner slots, as `BUILD_GUIDE.md` says, every femur lead is 44–122 mm short.

None of my findings blocks the build on its own. Two blockers in 01 must be cleared first:

- **B1:** no servo lead passes its window.
- **B2:** the MG90S spline sits about 3 mm higher than modelled.

B2 does not break the kinematics checked here: the critical poses keep at least 19.5 mm between legs.

**Count:** 0 blockers, 6 should fix, 8 notes.

## Findings

| ID | Severity | Area | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| SYS-1 | Should fix | Torque, stance | Static femur torque is 110–127 N·mm on the tripod leg that stands alone on its side: 51–59 % of stall, and 2.6–2.9 × the "1/5 of stall" guideline [4]. The specs' ×2 walking factor goes past stall (≈240 N·mm) | Mass 662 g (W 6.50 N). Lone-leg foot load 2.67–2.80 N (41 %). Femur 112.4 N·mm in the neutral tripod, 117.9 in the test gait, 126.6 in a 40 mm IK stride. Stall 216 N·mm [1] | Change the IK neutral stance: tibias tucked 15° in at the same height (femur −3°, tibia −12° in the sketch's terms). Peak static torque drops to 78–90 N·mm (36–42 %) at a 30–40 mm stride. If femurs still run hot, use 3.5 kg·cm-class servos [8] |
| SYS-2 | Note | Load basis | Every part spec uses 0.6 kg, 2 N per foot and ×2 = 4 N. The real figures are 2.8 N static and 5.6 N with ×2, which is 40 % more. The coxa hub moment is ≈440 N·mm, not 310. The new strength reviews already use 2.90 / 5.80 N, which agrees | §4 of every part spec, e.g. `coxa/spec.md:22,26`, `femur/spec.md:21`. `assembly_plan.md:11` says "≈90 N·mm". Each `strength.md` "Robot mass" row | Bring the five specs and the plan in line with the strength reviews' loads |
| SYS-3 | Should fix | Gait | The coxa-only sweep forces 18–20 mm of slide per planted foot per stroke. The body crabs 5 mm right per 24 mm step (≈12°) and yaws ±4° every step. On carpet, friction loads the resisting servos to 61–89 % of stall | `hexapod_test.ino:41–50, 81–82`. Planted-foot spacings change by up to 27.6 mm per stroke | Use an IK straight-line gait: stride 30–40 mm, lift 20 mm, 10–20 % double support. Checked collision-free (closest neighbour gap 25.0 mm). Coxa stays within ±20°, femur −12…+24°, tibia −37…+1° |
| SYS-4 | Should fix | Wiring layout | Through the four corner slots (guide step 5), every femur lead is 44–122 mm short. The middle legs' coxa leads are 21–41 mm short, and their tibia leads 28–37 mm short even with the 15 cm extensions. One board's channel order runs back to front | `BUILD_GUIDE.md:33, 66`. Slots at x ±50 (`body-top/model.py:74–76`). MG90S lead 24 cm [2] | Run each leg's leads up the deck edge beside that leg. Add 6 × 15 cm extensions for the femurs (12 in all). Put each board's front leg on the channels at that board's front end |
| SYS-5 | Should fix | Strain relief | No part has a tie point. The femur and tibia leads cross the coxa joint in the 9.4 mm gap under the plate, with 2.6 mm between the bracket and the servo case. The tibia lead crosses the femur joint beside the femur servo's horn | Coxa, femur and bottom-plate `model.py`: no tie slots. Only the deck has `TIE_SLOT` (`body-top/model.py:35`) | Add 3.2 × 1.8 tie slots: bottom-plate edge by each window, coxa bracket's outer plate end, femur near its horn. Leave free loops of ≈30 mm at the coxa and ≈20 mm at the femur |
| SYS-6 | Should fix | Coxa joint | Each leg hangs on its coxa servo's output shaft alone. The shaft sees 187–203 N·mm of bending in a static tripod (≈0.9 × the servo's own stall torque). In the 20 cm drop it sees 1.1–1.5 N·m, using the strength reviews' foot-load cap. No proof test loads a real servo | MG90S: "one bearing" [1]. `coxa/spec.md:47` clamps the horn in a vice instead. Drop cap 14.4–19.2 N per foot (`hexapod-femur/strength.md:55`) | Proof-test one assembled leg on its coxa servo. Do not run the bottom-plate drop test (`body-bottom/spec.md:48`) on the robot's own coxa servos. The tucked stance lowers the static moment to 156–161 N·mm. If the play grows, add a second support opposite the horn |
| SYS-7 | Should fix | Power | Walking draws 3.3–4.0 A on a hard floor and 3.8–4.7 A on carpet from a 5 A UBEC. Every 25 ms gait frame starts 10–14 A of servo current. Run time is 11–16 min | UBEC: 5 A continuous, 15 A burst [3]. MG90S stall 0.7 A at 5 V [2], up to 1.2 A at 6 V [5] | As 02 N-H4 (8–10 A rail, or one UBEC per board, ≈1000 µF per board) and 02 H3 (stagger the start). Use a pack rated 20 C or more (01 S15). The SYS-1/SYS-3 gait lowers the draw |
| SYS-8 | Note | Kinematics | The legs are rotated copies, not mirrored. Every foot sits 15.8 mm clockwise of its coxa line (22.2 mm with 01-B2's servo), so the left feet stand forward and the right feet back | `assembly_check.json` `feet_xy`; `hex_frame.py:31` | Harmless with IK. Otherwise turn the coxa zeros by 11.6°, or mirror the bracket for one side |
| SYS-9 | Note | Stability, clearance | Fine. Margin is at least 40.1 mm in the test gait and 35.7 mm in the recommended gait, and no parts touch. The "49 mm body underside" is really the coxa brackets; the plate is 96.4 mm up | Scripts below | Correct the wording (SYS-14) |
| SYS-10 | Note | Battery, switch, UBEC | The LiPo slides out between the columns (2 mm per side). There is no switch mount and no place for the balance lead. The UBEC (2.7–3.3 W of loss) sits 4.5 mm from the LiPo and 0.35–0.75 mm from a tab-screw tip | `viz_export.py:77`; DFM round 2 of the bottom plate | Cut a switch hole in the deck. Park the balance lead at the rear. Leave an air gap for the UBEC and add it to `assembly_check.py` |
| SYS-11 | Note | Assembly order | The order works. Building each leg off the body and hanging it on the coxa spline last keeps every clamp screw reachable. Some steps need rewording | `BUILD_GUIDE.md:55–66` | See details |
| SYS-12 | Note | Servicing | Each servo can be replaced (procedures in the details). Lifting the deck needs slack in 18 leads. M3 self-tapping screws in the PETG columns wear | `BUILD_GUIDE.md:66` | Heat-set inserts if the deck comes off often |
| SYS-13 | Note | Interfaces | Link-to-case, hub-to-screw and engagement stacks are fine. Clamp-screw depth is in 01 S2, window fit in 01 S1, lead exit in 01 B1 and spline height in 01 B2. B2 raises the body 3.2 mm and moves the feet 6.4 mm sideways, but leaves at least 19.5 mm between legs | `hobby_parts.py:96–103, 425`; `b2_sensitivity.py` | See details |
| SYS-14 | Note | Docs against CAD | The assembly `spec.md` is the blank template. `README.md` is missing. The mass, femur torque, "body underside", UBEC position and viewer gait disagree with the CAD and the sketch | See details | See details |

## Details

### SYS-1. Should fix: the femur servos hold 51–59 % of stall standing on a tripod

**Mass budget (≈662 g; the documents say ≈0.6 kg)**

| Group | g | Basis |
|---|---|---|
| Printed parts | 231 | Volumes from `geometry.json`, PETG 1.27 g/cm³. Walls of 3–4 × 0.45 mm and 1.0 mm top/bottom solid, the rest at the `print_requirements.json` infill. Solid would be 304 g |
| Of which: bottom plate / deck / 6 coxae / 6 femurs / 6 tibias | 64.8 / 36.2 / 51.5 / 38.0 / 40.9 | |
| 18 × MG90S | 241 | 13.4 g each [1] |
| Horns, clamp screws, washers, arm screws, 36 tab screws | 18 | |
| LiPo 2S 1000 mAh | 65 | `hobby_parts.py:429` |
| UBEC | 21 | Hobbywing UBEC 5A Air [3]. `hobby_parts` says 15 g |
| 2 × PCA9685, ESP32, MP1584, 1000 µF, switch | 36 | 9 g per board [6], 10 g, 2, 2, 4 |
| Power harness and jumpers; 6 servo extensions; strap, ties, tape; body screws | 50 | 17 + 18 + 8 + 7, estimated |
| **Total** | **662** | Centre of gravity at (−0.7, +0.8, 92.8) mm. Each leg is 64.9 g, 59 % of the robot |

**Why one leg carries 41 %**

- A tripod has two feet on one side and one foot on the other.
- The centre of gravity is about 92 mm from the line through the two feet.
- The lone foot is about 223 mm from that line.
- So the lone foot carries 92/223 ≈ 41 % of the weight, against 33 % if the load were shared equally.

**Static torques**

| Case | Most-loaded foot (N) | Femur (N·mm) | Tibia (N·mm) | Femur % of stall |
|---|---|---|---|---|
| Six legs down (W/6, indeterminate) | 1.08 | 49.0 | 3.6 | 23 % |
| Neutral tripod A {LF, LR, RM}: RM | 2.67 | 110.4 | 0 | 51 % |
| Neutral tripod B {LM, RF, RR}: LM | 2.72 | 112.4 | 0 | 52 % |
| Test gait, start of stroke | 2.80 | 117.9 | 0 | 55 % |
| IK straight line, current neutral, 40 mm stride | 2.80 | 126.6 | 42.7 | 59 % |
| Same, 60 mm stride | 2.80 | 137.5 | 68.9 | 64 % |
| ×2 walking factor from the specs | 5.6 | ≈240 | n/a | > 100 % |
| Tetrapod gait (4 feet down, equal stiffness) | 2.35–2.40 | ≈106–108 | n/a | 49–50 % |
| **Recommended: tibias tucked 15°, 30 mm stride** | 2.80 | **77.7** | **74.7** | **36 %** (tibia 35 %) |
| **Recommended: tibias tucked 15°, 40 mm stride** | 2.80 | **83.7** | **89.9** | **39 %** (tibia 42 %) |

**Reference points**

- Stall is 2.2 kgf·cm = 216 N·mm at 6 V [1].
- Robotis states that "stable motions are possible with robots designed for loads with 1/5 or less of the stall torque" [4]. For the MG90S that is 43 N·mm.
- Standing on six legs (23 %) is fine.
- Walking on a tripod at 51–64 % before dynamics is not: expect hot femur servos, sag at every tripod change and short gear life.

**What to change (software only)**

- Torque balance: neutral tuck angles at 30 mm stride (coxa zeros offset):

  | Tuck | 0° | −5° | −10° | −15° | −20° | −25° |
  |---|---|---|---|---|---|---|
  | Femur / tibia (N·mm) | 116 / 26 | 101 / 40 | 85 / 54 | 69 / 68 | 54 / 81 | 39 / 94 |

  The two balance at about −15°.
- Neutral pose in the sketch's convention: femur −3.0°, tibia −12.0°. This keeps the body underside at 96.4 mm and moves each foot ≈18 mm inward.
- Neutral feet then sit at LF (115.2, 67.7), LM (15.8, 110.8) and LR (−94.9, 91.9). The right legs are the same points turned 180°.
- Lowering the body does not help more: knee-up, 14 mm lower gives 81 / 97 N·mm.
- Leave the stance height as it is.

**Hardware options**

- Shortening the femur is only possible if the femur horn arm is turned to point backwards. The horn pocket and the tibia window are 11.8 mm apart.
- If femur cases still pass about 50 °C after 5 min of walking, fit 3.5 kg·cm-class micro servos (343 N·mm) to the femurs and tibias. Example: TowerPro MG92B, 13.8 g, 22.8 × 12 × 31 mm [8]. Its case and tab heights differ from the MG90S model, so check the fit first.

### SYS-2. Note: the design load in every part spec is 40 % low

The strength reviews written today already work from corrected loads:

- 683 g, an upper bound with solid parts;
- a lone-leg share of 41.5–43.3 %;
- 2.90 N sustained and 5.80 N walking.

Those agree with this review's 662 g (with infill), 2.8 N and 5.6 N. What remains is the text in the specs.

- **The specs' basis:** 0.6 kg, an equal share of 2 N per foot, ×2 = 4 N. This text is identical in every part spec's §4 (`coxa/spec.md:22`, `femur/spec.md:21`, `tibia/spec.md:21`, `body-bottom/spec.md:23`, `body-top/spec.md:22`).
- **The real loads:** 2.8 N static on the lone tripod leg (1.9 N on the paired legs), 5.6 N with ×2.
- **Load cases to give the strength analysts:**
  - **Coxa hub and horn joint, bending:** 5.6 N × 78.6 mm = **440 N·mm**. `coxa/spec.md:26` says 310. No servo limits this moment, because the coxa axis is vertical.
  - **Femur and tibia torque:** this would reach about 250 N·mm, but the servo yields at stall, so 216 N·mm is the ceiling. The specs already carry stall cases.
  - **Coxa vertical plate, out of plane:** the DFM's 126 N·mm at 4 N becomes ≈177 N·mm at 5.6 N.
- **Elsewhere:** `assembly_plan.md:11` "≈90 N·mm static at the femur" should read 110–127 N·mm.

**Fix:** update the five specs and the plan to the strength reviews' basis, so later DFM and strength rounds start from the right loads.

### SYS-3. Should fix: the test gait slides every planted foot 18–20 mm per stroke

**What the sketch does** (`hexapod_test.ino:41–50, 81–82`)

- Each tripod swings its coxae ±15° about each leg's own vertical axis.
- The planted legs sweep their coxae back by the same angle, with femur and tibia fixed.
- Each foot therefore moves on an arc around its own coxa axis. Arcs around six different centres cannot all match one rigid body motion.

**Results** (`loads.py`, `slip_leads.py`)

| Per stroke | Value |
|---|---|
| Change in spacing between planted feet | +27.3, −27.6 and −5.1 mm (pairs LM–RF, LM–RR, RF–RR) |
| Forced slide per foot, after the best rigid fit | 18.0–19.8 mm |
| Direction of slide | Middle legs: tangential (18.0 mm), so the coxa servo resists. Front and rear legs: mostly radial (16.5–18.8 mm, plus 6–8 mm tangential), so the femur and tibia resist |
| Best-fit body motion | 24.4 mm forward and 5.0 mm right every step: a heading 11.6° right, from the asymmetric foot layout in SYS-8. Yaw ±4.0°, alternating |

**Torque while a foot slides**

| µ (foot on floor) | Front/rear leg (1.9 N): tibia, femur | Middle leg (2.8 N): coxa |
|---|---|---|
| 0.3 (hard floor) | 40, 126 N·mm (femur 58 %) | 66 N·mm (31 %) |
| 0.6 (carpet) | 80, 165 N·mm (77 %) | 132 N·mm (61 %) |
| 0.8 (foot caught in pile) | 106, 192 N·mm (89 %) | 176 N·mm (81 %) |

**Also in the sketch**

- The loop stops at p = 0.9. The swing legs then land with a 3° coxa snap and a drop of 6.3 mm. See 02 H2.
- The tripods hand over within a single 25 ms frame, so the incoming tripod takes the load as an impact.

**Fix: an IK straight-line gait**

- Every planted foot moves parallel to the direction of travel at the same speed, so the spacing between planted feet is constant and nothing slides.
- Parameters checked here: the tucked neutral from SYS-1 (CAD unchanged, layout kept), stride 30–40 mm, lift 20 mm as a sine over the swing.
- **Joint ranges at 40 mm stride**, all inside the checked collision-free ranges:
  - coxa ±19.6°, so `MAX_COXA` = 30 still holds;
  - femur −12.3…+24.3°;
  - tibia −37.0…+0.7°.
  - Clamp the femur and tibia as in 02 N-H3.
- **Clearances:**
  - neighbouring coxae close by at most 35.4°, against the 70° the check allows;
  - mesh interference over 22 poses: none, closest neighbour gap 25.0 mm;
  - static margin at least 35.7 mm.
- **Longer strides:** 60 mm is also collision-free (gap 12.2 mm, checked with the coxa zeros offset as in SYS-8), but costs torque (98 / 121 N·mm) and margin (26.7 mm).
- **Higher lift:** the joint ranges allow 40–45 mm at the stroke ends. A carpet mode with a 30 mm lift is possible.
- **Hand-over:** add a 10–20 % double-support overlap so the incoming tripod takes the load gradually.

### SYS-4. Should fix: the servo leads cannot reach the boards by the documented route

**Method** (`leads_routed.py`)

- Lead length: 24 cm [2].
- The lead leaves each servo at the end away from the shaft, 2.5 mm above the case bottom, as in the repo's own model (`assembly_viz.py:190–194`).
- All three leads per leg exit towards the body. That is good.
- Runs go along the plates, plus 10 % for bends.
- Free loops: ±30° at the coxa (31 mm radius) and ±45° at the femur (20 mm radius).
- Header positions follow the Adafruit layout, with channel 0 at the left end seen from the header side.

**Spare length (+) or shortfall (−)**

| Route | Coxa leads | Femur leads | Tibia leads (with 15 cm extension) |
|---|---|---|---|
| Through the 4 corner slots (x ±50, y ±22), `BUILD_GUIDE.md:66` | −41…+49 (middle legs −21, −41) | **−44…−122** | −37…+35 (middle legs −28, −37) |
| Up the deck edge beside each leg | +49…+147 | −31…+47 | +54…+132 |

**Why the slots fail**

- The middle legs are at x = 0. Their leads must first run 50 mm along the body to reach a slot, then double back along the board.
- With both header rows facing outward, the two boards' channel numbers run in opposite directions along the robot. On one board (the right one, with the Adafruit layout), the front leg's channels 0–2 sit at the rear end. That adds about 40 mm to that leg's leads.

**Fix**

- Route each leg's three leads up the outside of the body beside that leg, over the deck edge to the headers. Add a notch or tie slot in the deck edge at each leg.
- Keep the slots only if you need them for the coxa leads.
- Add 6 × 15 cm extensions for the femur servos. With the existing six, that makes 12.
- Remap the channels so each board's front leg uses the channels at its front end. On the right board that means swapping channels 0–2 and 8–10 in `writeServo()`.
- Each estimate carries about ±30 mm. If in doubt, buy 20 cm extensions.

### SYS-5. Should fix: no strain relief, and two pinch points

**Pinch point 1: the coxa joint**

- The femur and tibia leads go from the turning bracket to the fixed body.
- The bracket's top face is 9.4 mm below the plate's underside.
- It is 2.6 mm from the coxa servo's case top and 5.6 mm from the tab-screw heads.
- A lead lying across the hub is dragged over the screw heads at every step (±15–20° of coxa travel) and can be trapped against the case top.

**Pinch point 2: the femur joint**

- The tibia servo's case reaches 8.9 mm behind the femur's back face (case bottom at C y −13.0, femur back face at −4.1). Its lead leaves about 6.4 mm behind that face.
- That puts the lead in the 9.4 mm space between the turning femur and the bracket's vertical plate, next to the femur servo's horn.

**Fix**

- Add tie slots (3.2 × 1.8 mm, like the deck's `TIE_SLOT`) at three places:
  - on the bottom plate's edge beside each coxa window;
  - at the outer end of the coxa bracket's vertical plate, above the gusset;
  - in the femur, about 10 mm from the horn.
- Route the femur and tibia leads round the outside of the bracket arm, not over the hub.
- Take the tibia lead along the femur's front face to the femur axis, then across in a free loop.
- Leave free loops of ≈30 mm at the coxa and ≈20 mm at the femur.
- Let the DFM reviewer place the slots: the coxa plate's posts are critical (coxa DFM #10).

### SYS-6. Should fix: the coxa servo's output shaft carries the whole leg

**Load**

- The bracket hangs on the coxa horn, with no support on the other side of the joint.
- Every vertical foot load becomes a bending moment on the MG90S output shaft. The lever is √(77² + 15.8²) = 78.6 mm.

| Case | Bending at the coxa horn (N·mm) |
|---|---|
| Six legs down | 77 |
| Static tripod, neutral / test gait / 40 mm IK stride | 187–191 / 200 / 203 |
| 20 cm drop at the spec's 3 × W over 6 feet (3.25 N) | ≈255 |
| 20 cm drop at the strength reviews' cap: femur and knee servos back-drive at 1.5–2 × stall, 14.4–19.2 N per foot (`hexapod-femur/strength.md:55, 61`) | **1130–1510** |
| Recommended tucked stance, 30–40 mm stride | 156–161 |

**Why it matters**

- The static tripod value is about 0.9 × the servo's own stall torque, applied sideways to a shaft that runs in "one bearing" [1].
- In a drop, the moment is 5–7 × stall. The coxa servo is then probably the weakest bought part in the leg.
- TowerPro publishes no side-load rating.
- The coxa proof test (`coxa/spec.md:47`) clamps the horn in a vice, so no test so far loads a real servo's shaft.
- The bottom plate's drop proof test (`body-bottom/spec.md:48`: three 20 cm drops onto carpet) would load all six coxa servos this way.

**Fix**

- **Proof test** on one assembled leg mounted on its coxa servo:
  1. Hang 570 g (5.6 N, ×2 the tripod foot load) at the foot for 10 min.
  2. Measure the foot's vertical play under ±1 N.
  3. Walk for 30 min and measure again.
  4. Pass: play grows by less than 1 mm at the foot, with no clicking or skipped teeth.
- **Drop test:** run the bottom plate's drop test with spare coxa servos, or replace it with a lower drop (5 cm) until a two-sided support exists.
- **If the proof test fails:** support the bracket on both sides of the joint, with the servo between two plates and a pivot pin opposite the horn. That means a new body.

### SYS-7. Should fix: the servo supply is near its limit when walking on carpet

**Model** (`power.py`)

- Holding current ∝ torque.
- Stall current 0.84 A (ProtoSupplies' 0.7 A at 5 V, scaled to 6 V [2]) to 1.2 A (upper bound [5]).
- 0.15 A per moving servo, 10 mA idle.
- Loads from SYS-1 and SYS-3.

**Draw and run time**

| State | Servo rail at 6 V (A) | Battery (A, C) | Run time on 800 mAh usable |
|---|---|---|---|
| Standing on six legs | 1.3–1.7 | 1.2–1.7 | 29–39 min |
| Walking, hard floor (µ 0.3) | 3.3–4.0 | 3.1–3.7 | 13–16 min |
| Walking, carpet (µ 0.6) | 3.8–4.7 | 3.5–4.4 | 11–14 min |
| Each 25 ms gait frame (12 servos start) | 10.1–14.4 for milliseconds | ≈9–13 | n/a |
| Power-on, all 18 at once (02 H3) | 15.1–21.6 | n/a | n/a |

**Against the hardware**

- **UBEC:** 5 A continuous, 15 A burst, over 90 % efficient [3].
  - On carpet it runs at 76–94 % of its continuous rating.
  - Its loss is 2.7–3.3 W.
- **1000 µF across the rail:** supplies 1 A for only 0.5 ms within a 0.5 V droop, so it does not cover the frame transients.
- **LiPo:** 3–4.4 C when walking and about 13.5 C at the UBEC's burst. Any pack rated 20 C or more is fine, but the BOM gives no rating (01 S15).

**Fix**

- As 02 N-H4: an 8–10 A rail, or one 5 A UBEC per board, plus about 1000 µF on each board.
- As 02 H3: stagger the start.
- The SYS-1 stance with the SYS-3 gait removes most of the friction current.
- Expect 10–15 min of walking per charge.
- Add a low-voltage alarm (02 H4).

### SYS-8. Note: the legs are rotated copies, so the stance is twisted

- Each coxa bracket carries its femur servo on the same side, so the femur, tibia and foot stack sideways along C +y:
  - femur back face at −4.1 mm;
  - tibia at 12.3–19.3 mm;
  - foot at **+15.8 mm**.
- Every foot therefore sits 15.8 mm clockwise of its coxa line (11.6°). The left feet stand 15.8 mm forward and the right feet 15.8 mm back (`assembly_check.json`: LM (15.8, 129), RM (−15.8, −129)).
- With 01-B2's servo heights, the offset becomes 22.2 mm (16.1°).
- **Effect on the test gait:** this layout is why it crabs right (SYS-3).
- **Effect on an IK gait:** none, because the feet are placed directly.
- **To square the stance:**
  - offset every coxa zero 11.6° anticlockwise seen from above (feet back on the left, forward on the right). That uses part of the coxa range: the front-left coxa reaches −35° at a 40 mm stride with the tibias tucked, so `MAX_COXA` would have to rise. Mesh-checked: gaps of 19.3 mm or more;
  - or print a mirrored coxa bracket for one side (3 + 3).

### SYS-9. Note: stability, clearance and collisions check out

**Static stability margin** (centre of gravity to the nearest support-triangle edge)

| Case | Margin |
|---|---|
| Neutral tripods | 59.6 and 61.7 mm |
| Test gait | 40.1 mm or more, worst at stroke start with the tripod alone |
| Recommended IK gait | 35.7 mm (40 mm stride), 39.7 mm (30 mm stride) |
| 60 mm stride | 26.7 mm |

- The centre of gravity is 92.8 mm high, so the robot tips at a sideways acceleration of 0.38–0.43 g.

**Collisions** (mesh interference, the same bodies and 1 mm³ tolerance as `assembly_check.py`)

| Gait | Poses | Contacts | Closest gap between neighbouring legs |
|---|---|---|---|
| Test gait | 20 | none | 26.7 mm |
| IK, 40 mm stride, layout kept | 22 | none | 25.0 mm |
| IK, 40 mm stride, coxa zeros offset | 22 | none | 19.3 mm |
| IK, 60 mm stride | 16 computed + 6 mirror images | none | 12.2 mm |
| 01-B2 servo, critical poses | 5 | none | 23.8 mm (test gait), 19.5 mm (recommended) |

Under the robot's 180° symmetry, "B swings at p" is "A swings at 1 − p" turned round. That is why the 60 mm row needs only 16 poses computed.

**Ground clearance**

- The lowest point is the coxa brackets' vertical plates, 49.2 mm above the ground.
- The body plate is at 96.4 mm and the coxa hubs at about 85 mm.
- "Body underside 49 mm" in the documents is misleading (SYS-14).

**Swing**

- The test gait lifts the feet 21.4 mm, enough for low-pile carpet.
- The foot moves 12 mm outward at the top of the swing and stays clear of everything.

### SYS-10. Note: battery access, switch and UBEC placement

**LiPo removal**

- The pack can slide out forwards or backwards between the columns, with 39 mm between the fillet feet against a 35 mm pack (bottom-plate DFM).
- It passes 0.5–10.5 mm under the ESP32's jumper zone.
- Keep the band y ±19.5 between the front columns free of leads.

**Missing mounts**

- No CAD has a switch mount. `hobby_parts` already has the KCD11 cut-out (15 × 10 mm); add it to the deck's rear edge.
- The balance lead has no defined place. Park it at the rear between the columns so the pack can charge in place.
- Fuse and switch rating: see 02 H4.

**UBEC placement** (`viz_export.py:77`: on its side, y 22–31, x −34…11, 20 mm tall)

- It is 4.5 mm from the LiPo and loses 2.7–3.3 W while walking.
- The tip of the left-middle coxa servo's inner tab screw stands 1.5 mm proud of the plate at y ≈ 32.4–32.75, 0.35–0.75 mm from the UBEC.
- The rear-left column's fillet foot is 0.5 mm from the UBEC's end.
- Keep an air gap to the pack, check the screw tip, and add a UBEC dummy to `assembly_check.py` (bottom-plate DFM).

### SYS-11. Note: the assembly order works; some steps need rewording

**Clamp-screw access: works**

- `BUILD_GUIDE.md:58–63` builds each leg off the body and hangs it on the coxa spline last. That keeps all 18 clamp screws reachable:
  - **Coxa:** from below, with nothing under the hub. The femur servo starts 15 mm out.
  - **Femur:** from its front face. The nearest obstruction is the tibia servo's tab, 23.5 mm from the screw.
  - **Tibia:** from its front face, the outermost face of the leg.
- Femur and tibia screws point at the neighbouring leg, 25–37 mm away. Driving them with the leg already on the body would put the screwdriver into that neighbour. Say so in step 4.

**Points to fix**

1. **Lead exit, steps 3–4:** pushing each servo through its window lead-first needs the fix in 01 B1.
2. **Femur-servo wording (`BUILD_GUIDE.md:59`):** "tabs on the face away from the body" is wrong. The vertical plate's faces point tangentially. Write: "tabs on the gusset face of the vertical plate, case through the window, shaft towards where the femur goes".
3. **Tibia wording (`BUILD_GUIDE.md:61`):** "pointing straight down … with the femur level" is written before the femur is on its servo. Write "perpendicular to the femur".
4. **Centring:** the servos are centred in step 1 and then stay unpowered. Pressing links on or driving the M2 clamp screw can turn a shaft. Hold the link while tightening, run `c` after step 5, and re-index any link more than half a spline tooth off (about 9°) before trimming.
5. **Step 1 power (`BUILD_GUIDE.md:55`):** the step does not say how V+ is powered on the bench. Use the UBEC at 6 V. Do not take servo power from the ESP32.
6. **LiPo timing:** step 3 straps the LiPo on before the legs. The robot is then flipped and handled with the pack in place, and the pack blocks lead routing. Strap it in step 5, just before the deck goes on.
7. **Horn anti-rotation screws:** not in the BOM. See 01 S4.

### SYS-12. Note: replacing a servo

Each replacement ends the same way: centre the new servo with `c`, fit the link at the nearest spline tooth, then trim with `t`/`p`.

**Coxa servo**

1. Turn the robot over.
2. Remove the M2 × 10 clamp screw from below and pull the leg off the spline. It hangs by its two leads.
3. Remove both tab screws. The outer one is only exposed with the bracket off.
4. Unplug the lead at the deck.
5. Push the servo out of its window, lead first (01 B1).

**Femur servo**

1. Take the leg off its coxa spline (one screw).
2. On the bench, remove the femur clamp screw and pull the femur off, with the tibia servo and tibia still on it.
3. Remove the two tab screws from the gusset side.
4. Take the servo out through the window.

**Tibia servo**

1. Remove the tibia clamp screw and take the tibia off. Its hub covers the outer tab screw.
2. Remove the two tab screws from the femur's front face.
3. Take the servo out through the femur window.

**Deck (top plate)**

- Four M3 × 8 screws hold it. Lifting it and setting it beside the body needs about 60 mm of slack in the 18 servo leads, the UBEC-to-V+ leads and the buck feed.
- The self-tapping threads in the PETG columns take a few cycles. If the deck comes off for every charge, use M3 heat-set inserts (a column-pilot change for the DFM loop).
- A battery swap does not need the deck off (SYS-10).

### SYS-13. Note: interfaces and stack-ups

| Interface | Value | Status |
|---|---|---|
| Link back face to servo case top (18 joints) | 2.6 mm (2.7 with 01-B2) | OK |
| Femur back face to coxa bracket arm | 2.4 mm (coxa DFM) | OK |
| Tibia servo case bottom to the coxa bracket's vertical-plate face (along the femur axis) | 0.5 mm (1.1 with 01-B2). Across the axis the servo sweeps radius ≥ 28.4 mm and the plate reaches 30.8 mm only at a femur angle of about −137°, far outside −70…+90° | OK, but tight. A horn pressed 0.5 mm deeper makes it touch |
| Coxa hub top to coxa tab-screw heads | 5.6 mm | OK |
| Foot-height stack per leg | LB 9.4 + Z_F 17 + L_T 70 = 96.4 mm (`hex_frame.py:44`). About ±0.5 mm per leg from printing and horn seating. 1° of femur trim = 0.8 mm at the foot | OK, the trims absorb it |
| Spline indexing | A link with its horn pinned fits in one-tooth steps, so up to about ±9° comes out in the trims. A 9° coxa trim also shifts that coxa's ±30° travel | OK |
| Clamp screws past the horn face | 6.5 mm, i.e. 5.9 mm into the MG90S's factory-tapped shaft [7]. Depth unverified | 01 S2: thread the screw into a bare shaft first. If it bottoms before 6 mm, use M2 × 10 (femur, tibia) and M2 × 8 (coxa), giving 3.9 mm of thread |
| M2 × 8 tab screws | 5.5 mm engaged. 1.5 mm proud inside the body (bottom plate), 1.0 mm proud on the coxa plate's outer face, 1.5 mm short of the femur's far face | OK. Mind the UBEC (SYS-10) |
| M3 × 8 deck screws / M2.5 × 6 board screws | 5.0 / 4.4 mm engaged | OK |
| Servo windows | Printed 22.7 × 12.4 mm against an MG90S of 22.8 × 12.2 mm | 01 S1 |
| Lead exit through the windows | Printed end clearance ≈ 0.1 mm | 01 B1 |
| Spline height | 3.2 mm higher than modelled. Body +3.2 mm (z_tab 99.6), foot offset 15.8 → 22.2 mm, link to case 2.7 mm, tibia servo to bracket 1.1 mm. Critical gait poses still collision-free, at least 19.5 mm apart (`b2_sensitivity.py`) | 01 B2 |

### SYS-14. Note: where the documents disagree with the CAD and the sketch

**The assembly job's `spec.md` is the blank template** (all 40 lines)

- Nothing states the robot's required surface, speed, run time or payload, so nothing tests them.
- Suggested robot-level acceptance tests:
  - stands 10 min on six legs with every femur case below 50 °C;
  - walks 2 m on a hard floor and 1 m on carpet with under 10 % drift;
  - walks 10 min or more per charge;
  - survives the 20 cm drop.

**Statements that disagree**

| Where | Says | Should say |
|---|---|---|
| `BUILD_GUIDE.md:16` | Print times are in `README.md` | `README.md` does not exist in the job folder |
| `BUILD_GUIDE.md:3` | ≈0.6 kg | ≈0.66 kg (SYS-1) |
| `assembly_plan.md:11` | ≈90 N·mm at the femur | 110–127 N·mm (SYS-1) |
| `assembly_plan.md:15, 40`; `viz_export.py:167` | Body underside 49 mm | 49 mm is the coxa brackets' lower edge; the body plate is at 96.4 mm |
| `body-top/spec.md:6`; `body-top/model.py:5` | The deck carries the UBEC | `BUILD_GUIDE.md:66` and `viz_export.py:77` put it on the bottom plate (also in the deck DFM) |
| `viz_export.py:151` | Viewer gait: period 1.6 s, swing 14°, lift 24°, tuck 18° | The sketch runs 15°, 25° and 10°, at about 0.5–0.9 s per cycle (02 N-H1, N-H5). The viewer shows a different gait from the robot's |
| `hex_frame.py:32–33` against `assembly_plan.md:21` | DFM round 1 "raised" the femur axis 4 mm / the axis sits "4 mm lower than round 1" | Both mean Z_F grew by 4 mm. Use one wording |

## How this was checked

**Read**

- `BUILD_GUIDE.md`, `assembly_plan.md`, `spec.md`, `hex_frame.py`, `assembly_check.py`, `assembly_check.json`, `viz_export.py` and `hexapod_test.ino`.
- The five part jobs' `spec.md`, `design_brief.md`, `model.py`, `geometry.json`, `print_requirements.json`, renders and DFM reviews.
- `tools/hobby_parts.py` and `tools/assembly_viz.py`.
- Reviews 01 and 02, and the hexapod `strength.md` files that appeared during this review, so as not to repeat their findings.

**Computed** with the project's own models. Nothing in the repo was changed.

- **Meshes:** each part's `design()` mesh, placed by `assembly_check.leg_frames`. The interference test is the same as `assembly_check.py`: manifold boolean, 1 mm³.
- **Gaps:** neighbouring-leg gaps from 2500 surface samples per leg.
- **Loads:** feet loads solved exactly for three supports. The centre of gravity includes every leg's pose.
- **IK:** solved numerically on `leg_frames`.

**Scripts** (read-only on the repo), in `/tmp/claude-0/-home-claude/50a131db-7c91-50e6-a869-32c6a4b19591/scratchpad/sysrev-hexapod/`:

| Script | Computes |
|---|---|
| `mass.py` | Printed masses |
| `loads.py` | Centre of gravity, foot loads, torques, margins and slide in the test gait |
| `gait_ik.py`, `scan.py` | IK gaits, stance scan and tetrapod loads |
| `collide.py` | Mesh interference and gaps |
| `slip_leads.py` | Slide split and friction torques |
| `leads_routed.py` | Lead lengths |
| `power.py` | Current and run time |
| `b2_sensitivity.py` | 01-B2 servo dimensions |

Results are saved as `*.json` next to them.

## Assumptions

**Masses**

- PETG 1.27 g/cm³.
- Printed mass from walls (3–4 × 0.45 mm), 1.0 mm top/bottom solid and the gyroid infill in each `print_requirements.json`: ±10 %.
- Harness, extension, strap and screw masses are estimates (≈50 g together).

**Loads**

- Quasi-static: vertical ground reactions on three feet, with dynamics quoted as a separate factor.
- Six-feet standing taken as an equal share (it is statically indeterminate).
- The tetrapod case uses equal-stiffness (least-norm) sharing.

**Servo**

- Stall 216 N·mm at 6 V [1].
- Holding current ∝ torque.
- Stall current 0.84–1.2 A at 6 V [2][5].
- 0.15 A while moving at gait speed.
- A servo yields at stall, so torques above stall mean sag, not breakage of the printed link.

**Friction** (foot on floor; not measured)

- 0.3 for PETG on wood or laminate.
- 0.6–0.8 on carpet, where the foot catches the pile.

**Gait**

- The IK gait: straight stance strokes along +X, a 20 mm sine lift, and the tucked neutral from SYS-1.
- Angles are in the sketch's convention after trims.

**Leads**

- Each lead exits at the far end of the case, 2.5 mm above the bottom (the repo's servo model).
- Lead length 24 cm [2].
- PCA9685 channel 0 at the left end seen from the header side (Adafruit layout). Check this on your own boards.
- Each length estimate is good to about ±30 mm.

**Dimensions**

- All CAD dimensions are nominal (`hobby_parts.py`). 01-B2's servo heights were run only as a sensitivity check.

## Sources

1. TowerPro MG90S datasheet (copy hosted by Braude College): <https://w3.braude.ac.il/wp-content/uploads/2021/03/MG90.pdf>. 13.4 g; 1.8 kgf·cm at 4.8 V and 2.2 kgf·cm at 6 V; 0.1 / 0.08 s per 60°; 4.8–6 V; "metal gear with one bearing". Cross-checked against [Components101](https://components101.com/motors/mg90s-metal-gear-servo-motor).
2. ProtoSupplies, MG90S: <https://protosupplies.com/product/servo-motor-micro-mg90s/>. Idle 10 mA, moving 120–250 mA, stall 700 mA (measured), lead 24 cm.
3. Hobbywing UBEC 5A Air: <https://hobbywingdirect.com/products/ubec-5a-air>. 5 A continuous, 15 A peak, over 90 % efficient, 21 g, 50 × 17 × 10 mm.
4. Robotis AX-12A e-Manual: <https://emanual.robotis.com/docs/en/dxl/ax/ax-12a/>. "Stable motions are possible with robots designed for loads with 1/5 or less of the stall torque."
5. Kpower, MG90S current draw: <https://www.kpower.com/insight_bldc/7870.html>. 1.2–1.6 A stall at 6 V. This is a vendor article and its own figures disagree, so it is used only as an upper bound.
6. Adafruit PCA9685 16-channel driver (product 815): <https://www.adafruit.com/product/815>. 9 g with headers and terminal block.
7. New Screwdriver, "Notes on Micro Servo Output Shaft": <https://newscrewdriver.com/2020/12/27/notes-on-micro-servo-output-shaft/>. The MG90S shaft is factory-tapped for a machine screw, and splines vary between batches.
8. The Pi Hut, TowerPro MG92B: <https://thepihut.com/collections/adafruit-robotics-cnc/products/towerpro-servo-motor-mg92b-metal-gear>. 3.1 kg·cm at 5 V and 3.5 kg·cm at 6 V, 13.8 g, 22.8 × 12 × 31 mm.

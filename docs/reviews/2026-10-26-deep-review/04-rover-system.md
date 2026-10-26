# Deep review 04: the tracked rover as a machine

Independent system-level review, 2026-10-26. Scope: how the whole rover works (drivetrain, tracks, stability, assembly order, serviceability, mechanical layout of the wiring, part-to-part interfaces and stack-ups, and the docs against the CAD). Not covered here: per-part printability (each job's `design_review.md`), printed-part strength (`strength.md`), bought-part dimensions and BOM (01-bought-parts.md) and wiring/firmware (02-electronics-firmware.md, cross-referenced where it overlaps).

## Verdict

As a machine the rover is sound. The drivetrain can drive, pivot-turn on tile, wood and carpet, and climb anything the tracks can grip. It is very stable: mass about 0.58 kg, centre of gravity 25.8 mm high and between the road wheels, tip-over angles of 65–69°. The track geometry closes exactly: 34 links fit the path with the idler at 120 mm, and the ±4 mm slot takes up the pin play now and lets you remove a link later. The tracks are well guided sideways: teeth ±0.5 mm in the link notch and V-flanges ±0.3 mm, with sprocket, idler and wheels all on Y 55. **It can't be built as documented, though.** The axle bolts in the BOM (M3 × 45 and M3 × 35, class 12.9, which in practice means ISO 4762 with only 18 mm of thread) never reach the nut traps in the walls. So the road wheels can't be clamped, the idler can't be locked and the track can't be tensioned (S-01). Most of the other problems sit at interfaces that `assembly_check.py` doesn't model:

- the sprocket hub rides on the N20's bearing boss, a 0.3 mm overlap that the check's "expected contact" rule hides;
- the set screw is 90° from the shaft flat;
- there is no room for the HC-SR04's connector;
- the toggle lever sticks out about 20 mm behind the tracks;
- the motor cradle has 0.8 mm of axial room for a motor whose length depends on the vendor;
- re-tensioning the track means taking off the lid and the hot-glued sensor, and every charge means taking off the lid.

Fix S-01 to S-07 before the chassis and sprocket are printed, because they change the BOM or the chassis and sprocket CAD. The rest are fixes to documentation, check coverage and serviceability.

**Count: 1 blocker, 12 should fix, 11 notes.**

## Findings

| ID | Severity | Area | Finding | Evidence | Fix |
|---|---|---|---|---|---|
| S-01 | **Blocker** | Interfaces, fasteners | Class-12.9 M3 × 45 and M3 × 35 bolts (ISO 4762, b = 18 mm) are threaded only on their last 18 mm, so they can't engage the wall trap nuts. Wheels can't be clamped, the idler can't be locked and the track can't be tensioned. | Head at y 32.0; trap nut y 35.4–38.0; thread starts at y 59.0 (×45) and y 49.0 (×35). `BUILD_GUIDE.md:32-33,62`, chassis `spec.md:11`, chassis `model.py:38,143-151` | BOM: **fully threaded** M3 × 45 / × 35, or M3 threaded rod cut to length with a nut in place of the head. Better: wheels and idlers on clamped sleeves (see details). |
| S-02 | Should fix | Track tension, service | The idler is locked by turning the bolt **head inside the tub**, not a nut. The HC-SR04 board sits over the slot, with 8 mm of room for an 18 mm key leg. There is no washer under the head, so PETG creep relaxes the clamp. | `BUILD_GUIDE.md:66` says "nut (inside)"; nut slot at chassis `model.py:151`; HC-SR04 PCB at x 116.4–118 over the slot at x 116–124 | Make the tension adjustable from outside (jack screw, or head outside with a sleeve). Add a washer under each head. Fix the wording. |
| S-03 | Should fix | Drivetrain interface | The sprocket hub end overlaps the N20 output boss by 0.30 mm (1.6 mm³). `assembly_check` hides it by exempting every motor/sprocket contact. The press depth "0.5 mm short" can't be seen or measured. | sprocket `model.py:31`; `hobby_parts.py:337` (boss 0.8 mm tall); `assembly_check.py:33,132`; `BUILD_GUIDE.md:63,65` | Counterbore the hub end Ø5.0 × 1.2. Give the press depth as "outer face 20.5 mm from the wall". Exempt only shaft ∩ bore in the check. |
| S-04 | Should fix | Drivetrain interface | The M2 set-screw hole points 90° away from the D-flat, so the screw bites the round part of the shaft. | sprocket `model.py:66` (`Rot(0, 90, 0)` puts the hole on +X); `hobby_parts.py:371` (flat on +Y); CAD probe; `BUILD_GUIDE.md:65` ("onto the shaft's flat") | Turn the hole to +Y, for example `Rot(-90, 0, 0)`, and move its teardrop square with it. |
| S-05 | Should fix | Layout, wiring | No room for the HC-SR04 connector. The board's bottom edge is 8.8 mm above the floor (its pins leave about 2 mm) and its top edge is 8.7 mm below the lid. A Dupont housing needs about 15 mm plus a bend. | chassis `model.py:54` (`SENSOR_Z` 30); board z 20–40, floor 11.18, lid 48.68; `assembly_check.py:86` (no header modelled) | Raise `SENSOR_Z` to about 38 with U-slots from the wall top, so the sensor drops in and the lid holds it. Or solder the leads to bent pins. Model the header in the check. |
| S-06 | Should fix | Layout, safety | The toggle lever is the rearmost point, about 20 mm behind the tracks. The autonomous mode reverses blind for 27–49 mm, so a knock switches the rover off or breaks the lever. | chassis `model.py:53,158`; `viz_export.py:77` with `assembly_viz.py:399-403`: lever tip at x −39.6, track rear at −19.9; `rover_test.ino:67` | Put the switch on the lid deck (lever up) or in a recess or hood so the lever stays forward of x −19. |
| S-07 | Should fix | Motor mounting | The cradle gives a 25.3 mm window for a 24.5 mm motor (0.8 mm float). The repo's detailed N20 model collides with the rear-stop posts (24.4 mm³ per motor), and gearbox length varies with the ratio. | chassis `model.py:47,116-121`; `rover_frame.py:40`; `assembly_viz.py:341-365` against `hobby_parts.py:341-353`; `BUILD_GUIDE.md:22` | Make the rear stop adjustable (set screw or shim clip) and widen the gap for the end cap to \|x\| < 4.5. Specify the length to measure. Collide the detailed model. |
| S-08 | Should fix | Drivetrain, loads | "N20 6 V 100 rpm" stall torque runs from 1.1 to 3.2 kg·cm depending on the vendor. At the 80 % cap that is 6.6–13.6 N of pull per side (up to about 22 N), against the 10 N design figure. The stall proof tests can exceed the 2 kg·cm gearbox limit. | `hobby_parts.py:338` (130 N·mm, no source); chassis `spec.md:24,52`; sprocket `spec.md:48`; Pololu and Phipps data (Sources) | Measure the stall torque with an arm and a kitchen scale before the proof tests. Set `PWM_CAP` so stall stays at or below 160 N·mm and 196 N·mm. Make the stall test 1 s. |
| S-09 | Should fix | Serviceability, power | Every charge means taking off the lid: 4 self-tappers into Ø2.6 printed pilots, with the lid tethered by about 10 wires. PETG pilots wear out after tens of cycles. | `BUILD_GUIDE.md:26,35,68`; chassis `model.py:48-49` | Heat-set M3 inserts in the columns with M3 × 8 screws, or a 2S BMS and a charge jack in the rear wall, or a floor hatch. |
| S-10 | Should fix | Wiring as mechanics | 15–17 Dupont jumpers pass through one Ø10 hole. Nothing relieves strain on the fragile N20 tabs or on the breadboard contacts when the lid comes off. The ESP32 jumpers sit 5 mm above the battery, about 3 mm at the velcro strap. | lid `model.py:39`; `BUILD_GUIDE.md:43-55,68`; `assembly_check.py:95-96` | Use a 10 × 24 slot with a tie bar under the lid. Tie the motor leads to the cans. Leave service loops of at least 150 mm. Say where the ECHO divider goes. |
| S-11 | Should fix | Process | The assembly job has no spec: `spec.md` is the blank template and `status.json` says kind "part". There are no system acceptance tests (turning, steps, free-running, run time). `BUILD_GUIDE` points to a `README.md` that doesn't exist. | `jobs/20261026-rover-assembly/spec.md:1-40`, `status.json`, `BUILD_GUIDE.md:17` | Write the system `spec.md` with the tests listed in S-11's details, and add or drop the README. |
| S-12 | Should fix | Verification | `assembly_check` is stale and narrow: the idler bolt is still 45 mm with the head outside; there are no bolts, nylocs or toggle in the collision set or the size; it uses the simple N20 dummy and an HC-SR04 with no header; it exempts every motor/sprocket contact. | `assembly_check.py:28,33-34,79,86-89,136-161`; `assembly_check.json` (142.0 mm wide) | Bring the check up to the current hardware (list in details). |
| S-13 | Should fix | Docs vs CAD | The docs contradict the CAD and each other: filament pins, face-screwed gearbox, rocker switch, N20 face at ±35, 0.5 kg / 10 N / 170 mm/s, buck location, "nut (inside)", the size, the zip-tie width, 23.5 mm pins. | `assembly_plan.md:11,12,14,16,31`; `BUILD_GUIDE.md:3,38,63,66,68`; lid `spec.md:6`; `viz_export.py:89` | One documentation pass (list in details). |
| S-14 | Note | Drivetrain, power | At the cap the rover makes 148–164 mm/s with no load and about 145 mm/s driving straight with light tension. The default `speedPct` 60 gives about 80–95 mm/s. Run time is 5–11 h, not 2–3 h. | `drivetrain.py` (scratch) | Update the plan and guide numbers. |
| S-15 | Note | Skid steer | Pivot turns work on tile, wood and carpet. L/B = 1.05, and only 0.72 on hard floors, where only the road wheels carry load. On carpet a turn needs 79 % of the available traction. | 0.36 / 0.41 / 1.56 N needed per track against 0.85 / 0.99 / 1.98 N of traction | None needed. Deep pile is the limit. |
| S-16 | Note | Track tension, friction | Pretension sets the losses: 0, 2, 5 and 10 N cost 2, 11, 25 and 48 % of stall torque, and the Ø10 PETG journal is two-thirds of that. The guide's 3–5 mm sag means about 0.1 N, which is good. But the top run rests on the road wheels (0.08 mm gap), so the sag must be read in a 40 mm span. | `wheel/model.py:19`; `rover_frame.py:25`; `BUILD_GUIDE.md:66` | Reword the span. Add a free-running start test. Grease the journal. |
| S-17 | Note | Track wear | 34 links fit exactly with the idler at 120. Pin play puts the taut idler at 120.0–123.4, which leaves 1.2–8 mm of wear reserve. Removing one link puts the idler back at 119, inside the slot. | `rover_frame.py:20-21`; link `model.py:25-26` | Add "remove a link at the slot end" to the guide, and print 2 spare links. |
| S-18 | Note | Stability, clearance | Mass is 577–599 g, CoG at x 58.4, z 25.8, with the load 54/46 % on the rear/front road wheels. Tip-over is 65–69° and grip runs out first (17°, 19°, 35°). Ground clearance is 8.7 mm, about 6 mm under the strap. Reversing, the rear corner meets steps of 8.7–12.5 mm before the track does. | `mass_cog.py`, `geom_checks.py` (scratch) | Run the strap in a floor channel and add holder end stops. |
| S-19 | Note | Sensor field of view | The tracks never enter the beam. The floor enters the ±15° cone 82–112 mm ahead, which is inside the 15 cm stop distance. For the table edge, see 02 R3. | chassis `model.py:54`; `rover_test.ino:11` | Raise the sensor (S-05) and tilt it up 5–8°. |
| S-20 | Note | Serviceability | Procedures to replace a link or a motor are missing. A link can only be opened at the idler front. Changing an axle bolt means taking out the battery or the sensor. | geometry in details | Add the procedures to the guide. |
| S-21 | Note | Envelope | The bolt tips and nylocs at y ±77 are the widest points (154 mm), 10 mm beyond the tracks. The road-wheel bolts clear their nylocs by only 1.5 mm. | stack in S-01 details | Use dome nylocs, specify DIN 985 nylocs and 0.5 mm washers, and update the stated size. |
| S-22 | Note | Interfaces | The journal and the motor cradle share no datum. If they are misaligned by more than 0.25 mm, the shaft takes load. Grit can get into the open journal. | chassis `model.py:42,111-121,141` | Lower the cradle by 0.3 mm so the journal sets the height. Use PTFE dry lube. |
| S-23 | Note | Track dynamics | The 10-tooth chordal action gives 4.9 % speed ripple (0.79 mm rise) at 16.7 Hz. Backlash is 2.06 mm (7.3°). Jumping a tooth needs 4.7 mm of lift, so derailment risk is low. | sprocket `model.py:28`; link `model.py:28-33` | None. Pause before reversals (02 N-R1). |
| S-24 | Note | Outside this slice | The chassis and wheel `slice_plan.json` overrides are below their `print_requirements.json` minimums (perimeters and infill), so the SLICE gate will fail them. | chassis plan: 4 perimeters / 25 % against 5 / 30 %; wheel plan: 3 perimeters against 5 | Slicing lead to align them. |

---

## Details

Frame used throughout: X forward, Y left, Z up, ground at Z 0, sprocket axle at X 0. Left side shown, right side mirrors. Numbers marked "computed" come from the scratch scripts listed at the end. They load the job `model.py` files and `rover_frame.py`, so they use the same geometry as the jobs.

### S-01. Blocker: the axle bolts can't reach the wall nuts

**Stack (computed, current design):**

| Item | Road wheel, M3 × 45 | Idler, M3 × 35 |
|---|---|---|
| Head (on the boss inner face) | y 32.0 | y 32.0 |
| Nut in the outer-face trap | y 35.4–38.0 | y 35.4–38.0 (slot) |
| Washer, part, washer | 38.0–38.5, wheel 38.5–71.0, 71.0–71.5 | 38.0–38.5, idler 38.5–58.5, 58.5–59.0 |
| Nyloc (DIN 985, 4 mm) | 71.5–75.5 | 59.0–63.0 |
| Bolt tip / past the nyloc | 77.0 / 1.5 mm | 67.0 / 4.0 mm |
| Thread start if ISO 4762 (b = 18) | **y 59.0, so the trap nut is not engaged** | **y 49.0, so the trap nut is not engaged** |

- "Class 12.9" in the chassis spec (`spec.md:11`) points to black socket-head cap screws (ISO 4762 / DIN 912). For M3 these carry b = 18 mm of thread at any length above about 25 mm ([ISO 4762 M3 × 40 table: b = 18](https://www.pgb-europe.com/en-gb/20624/socket-cap-screw-8-8-pt-iso4762-m-3x40)). Pan-head ISO 7045 screws of this length are also partly threaded.
- The trap nut sits 3.4–6.0 mm under the head, on the plain shank. Nothing clamps the bolt to the wall:
  - The bolt can tilt within the hole clearance: Ø3.4 printed hole on a Ø2.9–3.0 shank over 6 mm, about 4°. That moves the wheel centre about 1.5 mm.
  - The idler can't be locked in its slot. Track tension pulls it to the rear end of the slot, which gives 8 mm of slack (see S-17).
- You can't work around it with the outer nyloc: tightening it clamps the wheel or idler against the wall and stops it turning.

**Fix (pick one):**

1. **BOM change, smallest.** Use *fully threaded* M3 × 45 and M3 × 35 bolts: ISO 4017 / DIN 933 hex head, or "fully threaded" DIN 912 / DIN 7985. Or use M3 threaded rod (DIN 976) cut to 45 and 35 mm with a nut and washer where the head was. Class 8.8 or A2 is plenty at these loads.
2. **Better.** Bolt head outside. Each wheel and idler runs on a brass or steel sleeve, 3.2 ID × 5 OD and 0.3 mm longer than its hub. The bolt clamps the sleeve and washers against the wall into the trap nut, with a jam nut inside. Wheels then run on a smooth sleeve instead of a thread, the clamp is set from outside (which also fixes S-02), and end play is set by the sleeve length instead of by feel.

Either way, add a thread-engagement test to `assembly_check.py` (S-12).

### S-02. Should fix: the idler can't be re-tensioned without taking out the sensor

- **Wording.** `BUILD_GUIDE.md:66` says to "tighten the idler bolt's nut (inside)". In the CAD the nut slides in a hex slot in the *outer* face (chassis `model.py:151`) and the *head* is inside. The lock is made by turning the head with a 2.5 mm key.
- **Access, computed.**
  - The HC-SR04 PCB sits at x 116.4–118.0, right over the slot (x 116–124). Its transducers fill |y| 5–21 at z 22–38.
  - Between a transducer can and the socket-head face (|y| 29) there are 8 mm. The short leg of a 2.5 mm L-key is about 18 mm.
  - A ball-end key has to stay within about 25° of the bolt axis, so it runs into the PCB.
  - Step 6 (tracks) comes before step 7 (sensor), so the first tensioning works. Every later one means taking off the lid, with its wires attached, and the hot-glued sensor.
- **Creep.**
  - The BOM's 12 washers all go on running faces (`BUILD_GUIDE.md:34`), so the Ø5.5 head bears straight on PETG across a 3.6 mm slot.
  - The bearing area is about 10 mm², so a few hundred newtons of preload gives about 30 MPa. PETG creeps at that stress.
  - The clamp slowly relaxes, and track tension (up to about 2 × 14.9 N when reversing at stall) walks the idler back.
- **Fix.**
  - An outside adjuster: a slider in the slot carrying the idler bolt, pushed by an M3 jack screw through a boss on the front of the idler block. Or use S-01 option 2 (head outside, clamp from outside).
  - Add an M3 washer, or a 3 × 9 penny washer, under each idler head.
  - Fix the guide's wording.

### S-03. Should fix: the sprocket hub sits on the N20's bearing boss

- **Computed.**
  - Hub end at y 32.00 (sprocket `model.py:31`, 0.5 mm off the gearbox face at 31.5).
  - The N20 boss (Ø4, 0.8 mm tall, `hobby_parts.py:337`) reaches y 32.30. That is 0.30 mm of overlap, 1.6 mm³ in CAD.
  - `assembly_check.py:33,132` exempts every motorL/sprocketL and motorR/sprocketR overlap "because the shaft is a press fit". It also hides this overlap and any future hub-to-gearbox collision.
- **In practice.**
  - Pressing the sprocket on pushes the motor back onto its rear stop (0.3 mm), then the hub lands on the boss.
  - The sprocket ends up at the nominal Y 55, but its rotating hub rubs the stationary bushing boss.
  - "Until the hub stops 0.5 mm short of the gearbox face" (`BUILD_GUIDE.md:65`) can't be seen, because it happens inside the journal.
  - `BUILD_GUIDE.md:63` asks for the gearbox face against the journal boss *and* the end cap against the rear stop. With 0.8 mm of float, only one of those can be true.
- **Fix.**
  - Counterbore the hub end Ø5.0 × 1.2.
  - Specify the press depth as a measurement: "press until the sprocket's outer face is 20.5 mm from the wall's outer face". The disc outer face is at y 58.5 and the wall at 38.0, so a printed 20.5 mm gauge block works.
  - In the check, subtract the shaft from the motor dummy rather than exempting the whole pair.
  - Step 3 should say "push the motor back against the rear stop".

### S-04. Should fix: the set screw misses the flat

- In CAD, `Rot(0, 90, 0)` turns the grub-screw cylinder onto +X (sprocket `model.py:66`), but `d_shaft_bore_cutter` puts the flat on +Y (`hobby_parts.py:371`).
- Probes at the grub plane: the hole is open only at 0°, and the flat's material is at 90°.
- The D-form still carries the torque, but the screw marks the round part of the shaft and holds the sprocket axially less well. The guide says "onto the shaft's flat".
- **Fix:** use `Rot(-90, 0, 0)` so the hole runs along +Y, and move the teardrop square the same way (the point must still face up in print). Re-check with a probe like the one in `geom_checks.py`.

### S-05. Should fix: no room for the HC-SR04's connector

- The stock module's four pins come out of the board's bottom edge, pointing down. That is why it stands upright in a breadboard.
- **Computed.**
  - Board centred on the transducers (z 30), so its edges are at z 20 and 40.
  - Floor top at z 11.18 leaves 8.8 mm below the board. About 6–7 mm of that is pins, so about 2 mm is left.
  - Lid underside at 48.68 leaves 8.7 mm above the board.
  - A female Dupont housing covers the pins and runs about 8 mm past them, then needs a bend: about 17–18 mm in all.
  - The viewer's model has a straight header pointing back (`assembly_viz.py:334-336`). Its housings would end at x about 101, 2 mm from the battery holder at x 99.
  - `assembly_check.py:86` models the sensor as a bare PCB, so none of this shows.
- **Fix.**
  - Raise `SENSOR_Z` to about 38, which puts the board at z 28–48, just under the lid.
  - Cut the transducer holes as U-slots from the wall top. At that height a Ø16.6 teardrop breaks through the top edge anyway, and an open U-slot needs no bridge.
  - The sensor then drops in from above and a rib under the lid holds it. No glue is needed, it comes out easily (S-02) and there are about 17 mm under the board for straight jumpers. The beam also moves up (S-19).
  - If the sensor stays at z 30, tell the builder to bend the pins back and solder the leads before fitting it.

### S-06. Should fix: the toggle lever is the rearmost point of the rover

- **Computed with the viewer's MTS-102 model** (`assembly_viz.py:399-403`, placed by `viz_export.py:77`):
  - The lever tip is at x −39.6.
  - The track's rearmost point (grouser tips on the polygonal wrap) is x −19.9, and the rear wall x −19.0. So the lever sticks out about 20 mm behind the tracks.
  - Overall length becomes about 180 mm, not 160.
- In autonomous mode the rover backs up blind for 300 ms (`rover_test.ino:67`), which is 27–49 mm at 48–80 % PWM. The lever is what hits the furniture: the rover switches off, or the lever bends.
- The switch is missing from `assembly_check` and from the stated size.
- **Fix:**
  - Move the switch to the lid deck, lever up. The M6 bushing fits a 3 mm deck with a nut on each side, and the rear corner beside the ESP32's USB end has room.
  - Or put it in a pocket or hood in the rear wall so the lever stays at x −19 or forward of it.
  - Check that the MTS-102's bushing thread is long enough for the panel plus the outer nut. It wasn't verified here, and with the 4.5 mm wall it may be marginal.

### S-07. Should fix: the motor cradle is a 0.8 mm fit to a part whose length varies by vendor

- **The window.** The rear-stop posts end at y 6.7 (chassis `model.py:47,120`) and the journal boss face is at 32.0, which leaves 25.3 mm. The nominal motor (gearbox 9.0 + can 15.5, `hobby_parts.py:336`) is 24.5 mm, so it floats 0.8 mm.
- **Length varies.** The guide itself warns that "the gearbox length varies with the ratio" (`BUILD_GUIDE.md:22`).
- **The two N20 models disagree.**
  - The detailed model the viewer uses (`assembly_viz.py:341-365`) has a 1.4 mm plastic end cap of width ±4.5 and solder tabs at |x| 2.0–3.2.
  - Against that model the end cap overlaps the rear-stop posts (|x| 3.0–8.3) by **24.4 mm³ per motor**, and the tabs and leads touch them too (computed in `viz_parts_check.py`).
  - The collision check uses the simpler `gearmotor_dummy`, which has no end cap, so it reports nothing.
- A motor 0.8 mm or more longer than nominal won't seat; the viewer's model, at +1.4 mm, is already 0.6 mm too long. A shorter one floats.
- **Fix:**
  - Make the rear stop adjustable: an M3 set screw in a boss behind the can, bearing on the end-cap centre between the tabs, or a printed shim clip.
  - Open the gap between the posts to |x| < 4.5 for the end cap and tabs.
  - In the chassis spec, ask for "gearbox face to the farthest point of the end cap or terminals".
  - Collide the detailed model in `assembly_check`.

### S-08. Should fix: the motor torque isn't known, and the stall tests can break gearboxes

| Source for "6 V 100 rpm N20" | Stall at 6 V | At the 80 % cap, 7.4 V nominal (8.4 V full) | Pull per side |
|---|---|---|---|
| [Pololu 150:1 LP 6V, specs](https://www.pololu.com/product/1097/specs) (90 rpm, 0.36 A) | 1.1 kg·cm = 108 N·mm | 106 (121) N·mm | 6.6 (7.5) N |
| Project value, `hobby_parts.py:338` (no source given) | 130 N·mm | 128 (146) N·mm | 7.9 (9.0) N |
| [Phipps GA12-N20 6V 100RPM, product page](https://www.phippselectronics.com/product/ga12-n20-metal-gear-6v-100rpm-motor/) | 2.0 kg·cm = 196 N·mm | 194 (220) N·mm | 12.0 (13.6) N |
| [Phipps spec table, GA12-N20-200](https://phippselectronics.com/support/ga12-n20-metal-geared-motor-specifications) | 3.2 kg·cm = 314 N·mm | 310 (352) N·mm | 19 (22) N |

- **Design loads.** They assume 160 N·mm, about 10 N of pull and 14.9 N in the tight run (chassis `spec.md:24`). A strong variant at full charge exceeds that.
- **Gearbox limit.** Pololu limits these gearboxes to **2 kg·cm instantaneous** and warns that "stalls could damage the motor or gearbox" ([Pololu 1097](https://www.pololu.com/product/1097)).
- **The stall proof tests.** The chassis and sprocket tests (chassis `spec.md:52`, sprocket `spec.md:48`) stall both motors at 80 % for 3 s, five times. That can strip a strong motor's gearbox and overload the printed parts at the same time.
- **Fix:**
  - Measure your motor first. Clamp a 50 mm arm to the sprocket hub, stall it on a kitchen scale and read the grams: 160 N·mm is 326 g at 50 mm.
  - Set `PWM_CAP` so the stall stays at or below min(160 N·mm design, 196 N·mm gearbox). With 02's R1 battery-scaled cap, use the measured value.
  - Shorten the stall tests to 1 s.

### S-09. Should fix: charging means taking off the lid

- The cells are charged outside the rover (`BUILD_GUIDE.md:26`). Each charge means:
  1. Remove the four M3 × 10 self-tappers, which go into Ø2.6 printed pilots in Ø8 columns (chassis `model.py:48-49`).
  2. Lift the lid, which stays tethered by the motor, battery and sensor leads.
  3. Pull the cells.
- Re-driving self-tappers in PETG cuts fresh thread now and then. After a few tens of cycles the pilots strip.
- **Fix, any of:**
  - M3 heat-set inserts (5.7 mm long, Ø4.0–4.2 hole; the Ø8 column leaves about 2 mm of wall) with M3 × 8 machine screws.
  - A 2S BMS with a DC charge jack in the rear wall, so the cells stay in. That pairs with moving the switch in S-06.
  - A hatch in the floor under the holder.

### S-10. Should fix: one Ø10 hole for every wire, and no strain relief

- **Count through the cable hole** (lid `model.py:39`): 4 motor leads, VM and GND, 7 ESP32→TB6612 signals plus 3V3 and GND, and 2 more if the 1 k/2 k ECHO divider sits on the breadboard. That is **15–17 jumpers**.
- Every ESP32 wire crosses the deck: the ESP32's pins point down into the tub and the TB6612 sits on top.
- Each Dupont housing needs a 3.6 mm diagonal to pass. The last few won't go through a hole that's already 40 % full.
- **No strain relief anywhere.** The N20's solder tabs are the weak point of the motor, and breadboard contacts let go at 1–2 N. Lifting the lid pulls on both.
- **Under the lid.** The ESP32 jumper housings end 5 mm above the battery holder (`assembly_check.py:95-96`). The velcro strap over the holder (x 49.5–71.5) takes that to about 3 mm, so the wires get crushed.
- **Fix:**
  - A 10 × 24 mm slot, or two holes, with a zip-tie bar on the lid underside next to it.
  - Tie each motor's leads to its can with the cradle zip tie.
  - Leave at least 150 mm of lead from the tub so the lid can be flipped beside the rover.
  - Solder the ECHO divider into the lead and heat-shrink it, and say so in the guide.

### S-11. Should fix: no system spec and no system acceptance tests

- `jobs/20261026-rover-assembly/spec.md` is the unfilled template.
- `status.json` has `"kind": "part"` and stage SPEC.
- `BUILD_GUIDE.md:17` points to a `README.md` that doesn't exist.
- The part specs test parts; nothing tests the machine.

**Proposed system acceptance list for `spec.md`:**

1. Free-running: rover propped up, both tracks start and run at `speedPct` 30 (about 24 % PWM; see 02 N-R4). If one stalls, its track is too tight or its journal binds.
2. Straight run on tile: 2 m at the cap at 120 mm/s or more, drifting less than 10 % of the distance.
3. A 360° pivot turn on the household's thickest carpet without stalling.
4. Forward over a 12 mm step, both tracks.
5. A 20° carpet ramp, up and down.
6. Tension holds: after 30 min of driving the idler hasn't moved in its slot (mark it).
7. Run time: 2 h or more.
8. The 5 cm drops already in the part specs.

### S-12. Should fix: what `assembly_check.py` doesn't check

1. **Bolts.** `BOLT_L = 45` is used for the idler too, "head outside the wheel" (`:34`). The bolts are placed head-out from the trap (`:136-161`). The design now uses M3 × 35 idler bolts with heads inside at y 32.
2. **Missing parts.** Bolts, nylocs, washers and the toggle switch are not in the collision set or in `overall_mm`. Real size is about 180 × 154 × 60 mm, against 159.8 × 142.0 × 60.2 in `assembly_check.json`.
3. **Exemption.** `EXPECTED` (`:33`) exempts every motor/sprocket overlap, which hides S-03.
4. **Simple dummies.** The motor is the simple `gearmotor_dummy` (`:28,79`), which hides S-07. The HC-SR04 is a bare PCB (`:86-89`), which hides S-05.
5. **Fasteners not checked.** Nothing checks thread engagement or the protrusion past each nyloc, which hides S-01.

**Fix:** place the current fasteners and the toggle. Use the `assembly_viz` part geometry for the motor and sensor, with the header and housings. Subtract the shaft instead of exempting the pair. Add a fastener table check: thread start against each nut position, at least 1 mm past each nyloc.

### S-13. Should fix: documentation that contradicts the CAD or itself

| Where | Says | CAD / fact |
|---|---|---|
| `assembly_plan.md:11` | gearbox face screwed to the side wall; 0.5 kg; 10 N; about 170 mm/s | cradle with a zip tie, no screws; 0.58–0.60 kg; 6.6–7.9 N at the cap for documented motors (S-08); 148–164 mm/s no load, about 145 driving |
| `assembly_plan.md:12` | N20 stall about 0.6 A | 0.36 A (Pololu) to 1.0 A (Phipps table) |
| `assembly_plan.md:14` | mini rocker switch; 2–3 h | MTS-102 toggle; 5–11 h estimated (S-14) |
| `assembly_plan.md:16` | pinned with 1.75 mm filament | Ø2 × 24 steel dowels (`rover_frame.py:19`) |
| `assembly_plan.md:31` | N20 face at Y ±35, shaft to ±45 | ±31.5 and ±41.5 (`rover_frame.py:40`) |
| `BUILD_GUIDE.md:3` | about 160 × 142 × 60 mm | about 180 × 154 × 60 with the lever and bolt tips |
| `BUILD_GUIDE.md:38` | "2 zip ties (motors)" | the tunnel is 4 × 2 mm (chassis `model.py:46`), so ties must be 3.6 mm wide or less |
| `BUILD_GUIDE.md:63` | face against the boss **and** end cap against the stop | only one can touch (S-03, S-07) |
| `BUILD_GUIDE.md:66` | idler "nut (inside)" | head inside, nut in the outer slot (S-02) |
| `BUILD_GUIDE.md:68` / lid `spec.md:6` / `viz_export.py:89` | buck under the lid / on the deck with the breadboard / on top of the breadboard | pick one. Under the lid at x 70–95 above the battery has room. |
| part `spec.md` §3 (all six) | 2 mm rod cut to 23.5 mm | Ø2 × 24 dowels (fix already in flight) |
| sprocket `model.py:7` | D-bore takes 9 mm of the shaft | 9.5 mm in CAD and in sprocket `spec.md:6` |

### S-14. Note: drivetrain and power numbers

**Computed** with a linear torque–speed motor model at the average voltage (duty × pack), the hobby_parts motor unless stated, and losses from S-16:

| Case | Result |
|---|---|
| No-load chain speed at the cap (10 teeth × 10 mm per rev) | 148 (Pololu) to 164 mm/s at 7.4 V; up to 187 mm/s on a full pack |
| Straight on a hard floor, 2 N pretension | about 146 mm/s, 11 % of stall |
| Straight on carpet, 2 N pretension | about 142 mm/s, 14 % of stall |
| Default `speedPct` 60 (48 % PWM, about 3.5 V) | about 80–95 mm/s (98 mm/s with no load) |
| Slope, 30° on carpet | 34 % of stall, about 109 mm/s (grip, not torque, is the limit; S-18) |
| Run time, 2 × 2500 mAh (18 Wh) | 11 h cruising (1.6 W), 5 h hard use (3.7 W). The plan's 2–3 h is conservative. |

### S-15. Note: skid-steer turning works

- **Geometry.** Track gauge B = 110 mm. Ground contact is 12 links, with grousers spanning x 4–119, so L = 115 mm and L/B = 1.05, which is a good skid-steer ratio.
- **Load only under the road wheels.** The rims are 0.08 mm from the chain. The sprocket and idler discs are 1.29 mm above a straight run, and their teeth are narrower (1.94 mm at the pitch line) than the 4.0 mm gap between knuckles, so they can't carry vertical load. On hard floors the effective L is therefore 80 mm (L_eff/B = 0.72).
- **Pivot turn, one track forward and one back.** The pull each track needs is M_r / B:

| Surface (μ, μ_t) | Turning moment | Needed per track | Traction per track | L/B limit 2μ/μ_t | Motor load (Pololu / project / Phipps) |
|---|---|---|---|---|---|
| Tile (0.30) | 34 N·mm | 0.36 N | 0.85 N | 2.00 | 19 / 16 / 10 % of stall |
| Wood (0.35) | 39 N·mm | 0.41 N | 0.99 N | 2.00 | 20 / 16 / 11 % |
| Carpet (0.7, 0.9) | 146 N·mm | 1.56 N | 1.98 N | 1.56 | 40 / 33 / 22 %, 90–129 mm/s |

On carpet the turn uses 79 % of the available grip. Deep pile, where the track edges plough and μ_t rises above about 1.1, is where turns will start to stall. That is acceptable for an indoor test rover.

### S-16. Note: pretension, friction and the tension instruction

**Loss budget per sprocket, computed:**

- Journal: μ 0.4 × (T_top + T_bottom) × r 5 mm.
- Chain hinges: μ 0.25, Ø2 pins, 36° per articulation, four articulations per circuit.
- Idler and road-wheel bores on the bolts: μ 0.3.

| Pretension per run | Loss | Of which journal | Share of stall at the cap | Straight speed |
|---|---|---|---|---|
| 0 N | 3 N·mm | 0 N·mm | 2 % | 161 mm/s |
| 2 N | 14 N·mm | 8 N·mm | 11 % | 146 mm/s |
| 5 N (the strength files' assumption) | 32 N·mm | 20 N·mm | 25 % | 123 mm/s |
| 10 N | 62 N·mm | 40 N·mm | 48 % | 85 mm/s |

**The guide's "sag 3–5 mm".** It means very low tension, which suits the drive:

- The road-wheel rims sit 0.08 mm under the top run (`wheel/model.py:19` rim 13.10 against `rover_frame.py:25` 13.18). The top run rests on them, so the spans are 40 mm, not 120.
- 3–5 mm of sag in a 40 mm span is 0.6–1.7 mm of slack and a catenary tension of about 0.1 N.
- Read over 120 mm it would be 0.2–0.56 mm of slack and 0.7–1.1 N.

**Fixes:**

- Write "between the sprocket and the first road wheel".
- Add the free-running start test from S-11. It catches an over-tightened chain or a binding journal.
- Grease the journal with a dab of PTFE dry lube or silicone grease.

### S-17. Note: track length, wear reserve and link removal

**Loop length.** The pitch path is 2C + N·P = 2C + 100. At C = 120 that is exactly 340 = 34 × 10, so the chain has zero slack. The ±4 mm slot covers 332–348 mm.

**Taut loop with pin play, computed:**

| Hinge play (radial) | Pitch error | Taut loop | Idler at | Reserve to the slot end |
|---|---|---|---|---|
| 0.05 mm | −0.05 mm | 340.0 mm | 120.0 | 8.0 mm (2.4 %) |
| 0.10 mm (holes print on target) | 0 | 343.4 mm | 121.7 | 4.6 mm (1.4 %) |
| 0.15 mm (oversize holes) | +0.05 mm | 346.8 mm | 123.4 | 1.2 mm (0.4 %) |

**Removing a link.** Taking one link out (−10 mm) puts the idler back at 119.0 from the slot end, so the slot range (8 mm, more than half a pitch) supports link removal.

**Missing from the guide:**

- "When the idler reaches the front of its slot, remove one link."
- Spare links. The plan prints exactly 68, and only the pins have spares.

### S-18. Note: mass, CoG, stability and clearance

**Mass, computed** from voxelised CAD (shell = perimeters × 0.45 mm and solid layers × 0.2 mm; infill at the part's density) and the BOM:

| Group | Mass |
|---|---|
| Chassis (at the requirements' minimum settings) | 124 g |
| Lid | 28 g |
| Sprockets | 2 × 5.7 g |
| Idlers | 2 × 5.2 g |
| Road wheels | 4 × 12.5 g |
| Links | 68 × 1.3 g = 88 g |
| **Printed total** | **312 g** (287 g with the current slice plans) |
| Bought parts, including 68 steel pins (40 g) | 265 g |
| **Rover** | **577 g**, or 599 g with the 135 g battery in `hobby_parts.py:403`. Matches the docs' 0.58–0.6 kg. |

**CoG:** x 58.4, y 0.06, z 25.8 mm. The road wheels carry 54 % at x 40 and 46 % at x 80, about 1.5 N and 1.3 N per wheel.

**Each road wheel loads one or two links.** Each link touches the floor with 2 grousers of 5 × 4 mm, about 0.04 MPa. Between the wheels the hinged chain carries nothing.

**Tip-over and grip:**

- Tip-over angles: backward 65°, forward 67°, sideways 69°.
- Grip runs out long before that: 17° on tile, 19° on wood, 35° on carpet.
- At no point is motor torque the limit.

**Clearance:**

- Ground clearance is 8.68 mm.
- The velcro strap runs under the floor between the slots (chassis `model.py:155`), taking about 2–3 mm of that at x 49.5–71.5, and its hook side catches carpet. Fix: a 2 mm deep channel under the floor between the slots.
- The holder is held only by strap friction. Two printed end stops on the floor would stop it sliding in a corner drop.

**Steps:**

- Forward, the theoretical limit is under the idler axle height of 20.7 mm. Expect 12–15 mm with PETG grousers.
- The chassis front-bottom corner is 19.2 mm from the idler axle, inside the track profile (20.68), so it never meets the step first.
- The rear-bottom corner is 22.47 mm from the sprocket axle, outside the track profile. Reversing onto a step of 8.7–12.5 mm, the wall corner hits before the track, so reverse steps are limited to about 8.7 mm.

**Drop:** 5 cm means an impact speed of 0.99 m/s and 283 mJ. Strength is in the part reviews.

### S-19. Note: HC-SR04 field of view

- **Beam:** ±15° (HC-SR04 datasheet: "Measuring Angle 15 degree", [SparkFun copy](https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf)).
- **Sideways.** The transducers sit at y ±13. A 15° ray reaches the tracks' inner edge (y 43) 112 mm ahead, but the track nose ends only about 5 mm in front of the wall (x 139.9 against 135), so the tracks never enter the beam.
- **Upward.** The lid's front edge is 9 mm above the beam's top ray at the wall, so it is clear.
- **Downward.**
  - A −15° ray from the transducer's lower edge (z 22) meets the floor 82 mm ahead; from the centre (z 30), 112 mm ahead.
  - Both are inside `STOP_CM` 15 (`rover_test.ino:11`). On carpet and grouted tile the floor echo can stop the autonomous mode for no reason.
- **Fix.** Raising the sensor to z 38 (S-05) and tilting it up 5–8° moves the floor return beyond 150 mm.
- Drop-offs are 02 R3.

### S-20. Note: service procedures to add to the guide

**Close the loop, or replace a link, at the front of the idler.**

- The top run has only 5 mm inboard, between the wall (y 38) and the track's inner edge (y 43). A pin has to travel 18.75 mm inward to clear the centre knuckle.
- At the idler front (x about 135.4–136.2) nothing is inboard: the chassis ends at x 135, with 6 mm corner radii.
- Turn the track so the joint sits there. Back up the inner outer-knuckle with a small block, then drift the pin inward or press it in with a small clamp.

**Replace a motor:**

1. Lid off.
2. Loosen the idler (head inside; see S-02) and push it back, which gives up to 8 mm of slack.
3. Walk the chain off the sprocket teeth.
4. Loosen the set screw and pull the sprocket. The gearbox face stops against the journal boss, so the pull doesn't drag the motor out.
5. Cut the zip tie.
6. Unplug the leads at the breadboard.
7. Tilt the motor out shaft-last.

**Axle bolts.** A 48 mm bolt has to go in along Y from inside the tub. A road-wheel bolt therefore needs the battery out, and an idler bolt needs the HC-SR04 out. S-01 option 2 avoids both.

### S-21. Note: the widest points are the axle ends

- The road-wheel nylocs and bolt tips at y ±75.5–77.0 make the rover 154 mm wide. They sit 10 mm beyond the tracks' outer edge (67) and 6 mm beyond the wheel flanges (71).
- They scrape along walls and door frames first, and they take the first hit in a sideways tip.
- **Fix:** use dome (acorn) nylocs.
- **Nyloc margin.** The road-wheel bolts clear their DIN 985 nylocs by only 1.5 mm, three threads. A taller nyloc, or 0.8 mm washers instead of 0.5 mm, takes that below two threads. Specify DIN 985 and 0.5 mm (ISO 7089) washers.

### S-22. Note: journal and cradle alignment

- Two things set the shaft axis:
  - the journal, Ø10.7 CAD (about 10.5 printed) on a Ø10 hub, so 0.25 mm radial clearance (chassis `model.py:42,141`);
  - the cradle top, which supports the gearbox (`:116`), and the zip tie that holds the can down.
- They are printed features with no shared datum. The journal is a teardrop in a vertical wall; the cradle top is a horizontal face.
- If the journal prints more than 0.25 mm low, the hub bears on it and the N20 shaft takes the misalignment. That is the very load the journal was added to remove.
- **Fix:** lower the cradle top 0.3 mm so the gearbox can float and the journal sets the height.
- The journal is open to grit from the tracks. PTFE dry lube helps.

### S-23. Note: chordal action, backlash and derailment

- **Chordal action.** With 10 teeth the chain speed ripples 4.9 % and the bottom run rises 0.79 mm at 16.7 Hz (at 100 rpm). Expect audible buzz, but it does no harm.
- **Backlash.** The gap between knuckles is 4.00 mm and the tooth is 1.94 mm wide at the pitch line, so each tooth has 2.06 mm of backlash, 7.3° of sprocket rotation. Reversals clunk; see 02 N-R1.
- **Tooth jump.** It needs the knuckles to lift 4.71 mm over the tips, about 15 mm of slack on a 180° wrap. Even the worst case (idler at the rear of its slot) has only 8 mm.
- **Sideways guidance is coplanar.**
  - The sprocket, idler and road wheels all centre on y 55.0–55.3 (end play included).
  - Teeth are 7 mm in an 8 mm notch; flanges are 24.6 mm apart on a 24 mm link.
  - The flanges also guide the top run, overlapping its link sides by 2.9 mm.
  - A pin end is 2.4 mm from a flange cone.
- Derailment risk is low.

### S-24. Note: outside this slice, noticed in passing

`jobs/20261026-rover-chassis/slice_plan.json` overrides 4 perimeters and 25 % infill, against minimums of 5 and 30 % in its `print_requirements.json`. The wheel plan has 3 perimeters against a minimum of 5. The validator will fail both at SLICE, so align them before slicing.

---

## Assumptions

- **Geometry.** All of it comes from the job `model.py` files and `rover_frame.py` as of 2026-10-26 02:00 UTC, placed the way `assembly_check.py` places them. "Printed" sizes assume the project's HOLE_COMP of +0.2 mm (no library calibration exists yet).
- **Fasteners.**
  - ISO 4762 M3 has b = 18 mm of thread. If the builder's bolts happen to be fully threaded, S-01 reduces to a BOM wording fix.
  - Nylocs are DIN 985 (4 mm). Washers are ISO 7089 (Ø7 × 0.5).
- **Mass.**
  - PETG 1.27 g/cm³. Shell = perimeters × 0.45 mm; top and bottom = layers × 0.2 mm; infill at the stated density. Print-requirements minimums were used.
  - Bought parts: N20 10 g each (Pololu lists 9.5 g); protected 18650 47.5 g each; holder 18 g; ESP32 10 g; breadboard 10 g; HC-SR04 9 g; toggle 6 g; wires and jumpers 18 g; Ø2 × 24 steel pin 0.59 g each; M3 × 45 2.8 g; M3 × 35 2.3 g.
- **Motor.**
  - Linear torque–speed. No-load speed and stall torque scale with the average voltage (duty × pack). TB6612 drop and PWM current ripple are ignored.
  - Three datasheet brackets are used rather than one number, because "6 V 100 rpm N20" is not one motor.
- **Friction (typical dry values, not measured).**

| Pair or surface | Value used |
|---|---|
| PETG on PETG (journal) | 0.4 |
| PETG on steel | 0.3 |
| Hinge | 0.25 |
| Tile | μ = μ_t = 0.30 |
| Wood | μ = μ_t = 0.35 |
| Carpet | μ 0.7, μ_t 0.9 |
| Rolling | 0.02 on hard floors, 0.08 on carpet |

  The conclusions hold for ±30 % on these: turning works, grip limits slopes, and pretension dominates the losses.
- **Turning.** Pivot turn with uniform friction. On hard floors only the road wheels carry load; on carpet the pressure is uniform over 115 mm.
- **HC-SR04.**
  - Stock module: 4 pins pointing down past the board's bottom edge, about 6–7 mm, with the board centred on the transducers.
  - Beam ±15° from the datasheet's "measuring angle 15°".
- **Toggle switch.** Size and lever length come from the repo's viewer model (`assembly_viz.py:399-403`). The MTS-102 bushing length was not verified.
- **Pretension.** The guide's sag gives about 0.1–1 N. The strength files assume 5 N, which is conservative for strength and pessimistic for speed.
- **Not re-checked here.** Printability, part strength, bought-part dimensions (01) and electronics/firmware (02).

## Sources

- Pololu 150:1 Micro Metal Gearmotor LP 6V, specifications: https://www.pololu.com/product/1097/specs
- Pololu 150:1 LP 6V product page (2 kg·cm instantaneous torque limit; stall warning): https://www.pololu.com/product/1097
- Phipps Electronics, GA12-N20 metal gear 6V 100RPM motor: https://www.phippselectronics.com/product/ga12-n20-metal-gear-6v-100rpm-motor/
- Phipps Electronics, GA12-N20 metal geared motor specifications (table): https://phippselectronics.com/support/ga12-n20-metal-geared-motor-specifications
- HC-SR04 datasheet (SparkFun copy): https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf
- ISO 4762 M3 × 40 socket cap screw, dimension table (b = 18): https://www.pgb-europe.com/en-gb/20624/socket-cap-screw-8-8-pt-iso4762-m-3x40

## Scratch scripts (not in the repo)

- `/tmp/claude-0/-home-claude/50a131db-7c91-50e6-a869-32c6a4b19591/scratchpad/sysrev-rover/geom_checks.py`: hub/boss overlap, set-screw direction, HC-SR04 room, outline against the track profile, bolt stacks, idler-head access, toggle.
- `/tmp/claude-0/-home-claude/50a131db-7c91-50e6-a869-32c6a4b19591/scratchpad/sysrev-rover/mass_cog.py` (output in `mass_cog.json` and `mass_cog.log`): printed and bought masses, CoG.
- `/tmp/claude-0/-home-claude/50a131db-7c91-50e6-a869-32c6a4b19591/scratchpad/sysrev-rover/drivetrain.py` (output in `drivetrain.log`): pull, speed, losses, turning, slopes, steps, track length, sensor geometry, run time.
- `/tmp/claude-0/-home-claude/50a131db-7c91-50e6-a869-32c6a4b19591/scratchpad/sysrev-rover/viz_parts_check.py`: the viewer's detailed N20, toggle and HC-SR04 models against the chassis.

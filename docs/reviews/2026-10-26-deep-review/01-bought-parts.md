# Deep review 01: bought parts and bills of materials

Robot arm, tracked rover and hexapod. Independent review, 2026-10-26. This slice covers the bought parts:

- the nominal dimensions in `tools/hobby_parts.py` that the CAD depends on;
- electrical ratings against use;
- the fastener lists against the part thicknesses;
- missing items and battery safety;
- whether each BOM matches its CAD.

Wiring and firmware are in [02-electronics-firmware.md](02-electronics-firmware.md); where 02 already covers a point, this report only refers to it. The mechanical system reviews are separate.

## Summary

| ID | Robot | Finding | Severity |
|---|---|---|---|
| B1 | Arm, hexapod | No servo lead can pass its closed window (23 windows) | **Blocker** |
| B2 | Arm (claw, wrist), hexapod | The MG90S output sits ≈3 mm higher above its tabs than the CAD assumes; the claw pinion runs into the cover | **Blocker** |
| S1 | Arm, hexapod | The MG90S body is 22.8 × 12.2 mm; the printed windows are 22.7 × 12.4 mm | Should fix |
| S2 | Arm, hexapod | Horn clamp-screw lengths rest on unverified horn and spline data; the wrist M2 × 12 goes 1 mm deeper than the others | Should fix |
| S3 | Arm | MG996R tab screws: unspecified bag screws, Ø2.6 pilots, grommet holes with no washers | Should fix |
| S4 | Arm, hexapod | No screws listed for the horn anti-rotation holes (7 on the arm, 18 on the hexapod) | Should fix |
| S5 | Arm | The Brio's USB-C port is on its back, and the stock plug sticks out 50–75 mm | Should fix |
| S6 | Arm | The 1/4"-20 × 3/8" thumb screw goes 5.5 mm into the camera | Should fix |
| S7 | Arm | Three servo leads need extensions; the BOM lists two | Should fix |
| S8 | Arm | Power-bus parts are missing; servo power shouldn't run through Dupont jumpers | Should fix |
| S9 | Rover | "N20 6 V 100 rpm" doesn't define the motor: stall 0.36–1.6 A, gearbox 9 or 11 mm, shaft 9 or 10 mm | Should fix |
| S10 | Rover | The sprocket set screw meets the round side of the shaft, at its very end | Should fix |
| S11 | Rover | The axle bolts must be fully threaded; the idler bolt length differs between documents | Should fix |
| S12 | Rover | Protected 18650 cells (≈69.5 mm) may not fit a 65 mm holder; no charger is listed | Should fix |
| S13 | Rover | The HC-SR04's header and jumpers don't fit between floor and lid | Should fix |
| S14 | Hexapod | The UBEC must accept a 2S input; common "5 A HV" UBECs need 3S or more | Should fix |
| S15 | Hexapod | The LiPo line is incomplete: connector, C-rating, charger, bag | Should fix |
| N1 | Arm | MG996R cross-check: dimensions match; stall-current and torque figures vary | Note |
| N2 | Arm | Brio 4K: clip and thread confirmed; thread position, model variant, USB 2.0 cables | Note |
| N3 | Arm | DC jack: the CAD needs an 11 mm thread; the common jack is M8 | Note |
| N4 | All | ESP32 boards shorter than ≈49.5 mm don't seat in any of the three seats | Note |
| N5 | Rover | Small parts check out; 100 µF voltage, hot glue, dowel-pin length tolerance | Note |
| N6 | Hexapod | Small parts check out (PCA9685 board and holes, LiPo size, MG90S variants) | Note |
| N7 | All | Fastener lengths that check out; two are marginal | Note |
| N8 | All | Stale or contradictory BOM text | Note |

| Robot | Blocker | Should fix | Note |
|---|---|---|---|
| Robot arm | 2 (B1, B2) | 8 (S1–S8) | 6 (N1–N4, N7, N8) |
| Tracked rover | 0 | 5 (S9–S13) | 4 (N4, N5, N7, N8) |
| Hexapod | 2 (B1, B2) | 5 (S1, S2, S4, S14, S15) | 4 (N4, N6, N7, N8) |
| **Distinct findings** | **2** | **15** | **8** |

Shared findings are counted under each robot they affect.

## How this was checked

- **Read:** the three `BUILD_GUIDE.md`s and `assembly_plan.md`s, every part `spec.md` and `model.py` that a bought part touches, `tools/hobby_parts.py`, `claw_frame.py`, `rover_frame.py`, `hex_frame.py` and the three `assembly_check.py`s.
- **Derived numbers** (screw stacks, offsets, pilot ligaments, lead paths) came from a read-only script that parses `hobby_parts.py`: `/tmp/claude-0/-home-claude/50a131db-7c91-50e6-a869-32c6a4b19591/scratchpad/bom_numbers.py`.
- **Sources:** manufacturer pages and datasheets first (TowerPro, Logitech, Pololu, Adafruit, Hobbywing). Then distributor measurements, the OpenSCAD MCAD servo model and hobbyist teardowns. Each claim cites its source by number, e.g. [5].
- **TowerPro's letter tables.** TowerPro's pages give dimensions as letters A–F next to a drawing that is only an image, and I couldn't open the image. I mapped the letters using the MG996R, whose dimensions are known:
  - A = overall height to the spline top (42.7 against 42.9);
  - B = body length (40.9 against 40.7);
  - C = case height (37 against `case_top` 36.5);
  - D = width (20 against 19.7);
  - E = tab span (54 against 54.0);
  - F = case bottom to tab underside (26.8 against 27.0).

  The same mapping reproduces OpenSCAD's SG90 model to within 0.4 mm on A, B, C and E.
- **Unverified items:** where no text source exists, the item is marked unverified and needs calipers.

---

## Blockers

### B1. No servo lead can pass its closed window (all 23 windows)

**Where the lead leaves the case**

| Servo | End | Height above case bottom | Across the width | Lead at the exit | Evidence |
|---|---|---|---|---|---|
| SG90 | Output-shaft end | 4.5–5.7 mm | Centred | Flat 3-wire ribbon, 3.6 × 1.2 mm | OpenSCAD MCAD `towerprosg90` cable [5] |
| MG90S | Output-shaft end on every batch tested; the exact spot varies by batch | Not published: assume the SG90's, measure | As SG90 | As SG90 | 2 SG90 and 4 MG90S batches all had the wires on the side nearer the output shaft [6] |
| MG996R | **Unverified.** Standard servos usually exit low on the output-shaft end | Unverified | Assumed centred | ≈4 × 1.3 mm (3 wires, estimate) | The drawings and photos are image-only; check yours |

**Why the lead can't pass**

- Every window is a closed rectangle. The case goes in bottom-first, and the tabs stop on the plate.
- The lead's root is on the shaft-end face, 10–14 mm below the tab plane, so it crosses the whole plate thickness during insertion.
- At that moment the ribbon, 1.2 mm thick plus its bend, has to fit between the case end and the window's end wall.
- That gap is 0.1 mm printed in the MG90S windows (`END_CLR` 0.2) and 0.2 mm in the MG996R windows.
- **Threading the connector through first doesn't help:** the root itself still has to cross the window.
- **Inserting from the other face isn't possible:** the tabs can't pass the window.

**The 23 windows** (positions in each part's design frame)

| Part (job) | Servo | Plate | Lead end (shaft end of the case) | Near tab pilots | Lead passes? | Fix |
|---|---|---|---|---|---|---|
| Base top plate (`20261025-arm-base`) | MG996R | 4 mm (6 mm bosses under the pilots) | X +10.2 | (14.1, ±5) | No | Notch, through the 4 mm plate only |
| Turntable upright (`20261025-arm-turntable`) | MG996R | 7 mm | X +20.35, Z 60.5 | X 24.25, Z 55.5 / 65.5 | No | Notch with a 45° top |
| Upper link (`20261025-arm-upper-link`) | MG996R | 10 mm | x 110.2 | (114.1, ±5) | No | Notch |
| Forearm (`20261025-arm-forearm`) | MG90S | 10 mm | x 95.9 | (98.55, 0) | No | Option 1 |
| Claw bulkhead (`20261026-arm-claw-frame`) | MG90S | 6 mm | G y +5.9, z 22.5 | G y 8.55, z 22.5 | No | Option 1 or 2 |
| Body bottom ×6 (`20261026-hexapod-body-bottom`) | MG90S | 4 mm | Radial +5.9 (outboard end) | Radial +8.55 | No | Option 2 or 1 |
| Coxa vertical plate ×6 (`20261026-hexapod-coxa`) | MG90S | 4.5 mm | C x 37.9, z 17 | C x 40.55 | No | Option 2 or 1 |
| Femur ×6 (`20261026-hexapod-femur`) | MG90S | 7 mm | x 50.9 | (53.55, 0) | No | Option 2 or 1 |

**MG996R windows (3): a centred notch clears the pilots.**

- The MG996R has two pilots per tab, ±5 mm off the centreline and 3.9 mm beyond the case end.
- Cut a notch 4.4 mm wide (±2.2), reaching 2.0 mm beyond the case end, through the plate. These are printed sizes: add `HOLE_COMP` in the cutter.
- That leaves 2.1 mm to the nearest Ø2.6 pilot.
- **In the base,** cut it through the 4 mm top plate only. Below the plate the ribbon passes between the Ø6.5 bosses, which stand ≥2.4 mm off the centreline there.
- **In the turntable upright** the notch is a horizontal hole in a standing wall: give it a 45° top.
- **Until the lead end is confirmed** on your MG996R, notch both ends. The far-end pilots use the same ±5 mm pattern, so the second notch costs nothing.

**MG90S windows (20): no notch position avoids the near pilot.**

The micro servo has one pilot per tab, on the centreline, 2.65 mm beyond the case end, and the lead root is on that same centreline at that same end. The smallest notch that passes a 1.2 mm ribbon reaches 1.5 mm beyond the case end and leaves 0.4 mm of plastic between the notch and the Ø1.5 pilot. A self-tapping M2 would split it.

Two of the obvious workarounds don't help:

- **An open-ended window** at that end would run straight through the near pilot.
- **Threading the lead first** fails because the root still has to cross the window (above).

The options, smallest change first:

1. **Move the near pilot out by 1.3 mm,** to 3.95 mm beyond the case end.
   - This leaves a 1.6 mm ligament beside a notch 4.2 mm wide, reaching 1.5 mm beyond the case end.
   - The screw has to reach the moved pilot: open the slit that runs from each tab hole to the tab end to 2.1 mm wide with a needle file. MCAD's SG90 tab has a 1.3 mm slit [5]; check that yours has one.
   - Material left beyond the moved pilot: forearm 3.4 mm, claw bulkhead more than 20 mm, body bottom ≈3 mm, coxa plate and femur 1.3 mm. Lengthen those two plates by 1 mm.
   - Cost: a small file job on each of 20 servo tabs.
2. **Mount the servo the other way round:** tabs on the plate's far face, with the upper case and the spline going through the window.
   - The lead root then never crosses the plate, and the pilots stay as they are.
   - With the real MG90S height (B2), the horn face still ends 5–8 mm beyond plates of 4–7 mm. That works for the body bottom, coxa plate, femur and claw bulkhead, but not for the 10 mm forearm.
   - Every link offset changes, so the three assembly checks must be re-run. B2 forces that anyway.
3. **Keyhole:** run the notch into the near pilot, and replace the self-tapper with an M2 machine screw, washer and nut on the far face. This works only where the far face is free; in the 10 mm forearm the nut lands on the lead.
4. **No CAD change:** open the servo's bottom cover, unsolder the three wires, pass the case through, then resolder them with strain relief. Not recommended for 20 servos.

**Severity:** blocker. None of the 23 servos can be fitted as drawn without cutting its lead. Measure your servos' lead root (height, width, thickness) before choosing a fix, because it varies by batch [6].

### B2. The MG90S output sits ≈3 mm higher above its tabs than the CAD assumes

**Evidence**

- **The CAD:** `hobby_parts.py` gives the SG90, and so the MG90S, `case_top` 22.7, `total_h` 26.7 ("case bottom → top of output spline") and `tab_height` 15.9. That puts the spline top 10.8 mm above the tab underside, and `horn_face_z()` = 11.4.
- **OpenSCAD's MCAD SG90 model [5]** has the same 22.7 mm case and the same tab at 15.9 mm. But in that model 26.7 mm is the top of the round gear boss: a Ø4.6 spline continues 3.2 mm higher, to 29.9 mm. The spline top is therefore **14.0 mm** above the tab underside.
- **TowerPro's tables** (letters mapped as in "How this was checked"):
  - SG90: A 30.3, C 27, F 17 [4].
  - MG90S: A 32.5, C 28.4, F 18.5 [3][11].
  - For the MG90S, A − F puts the spline top **14.0 mm** above the tab underside, and F puts the case bottom 18.5 mm below the tabs (CAD: 15.9).
- **Measurements:**
  - ProtoSupplies measured the MG90S at 32 mm tall with the shaft [8].
  - The SG90's own overall height is 31 mm in its datasheet [12] and 29 mm at M5Stack [13], both well above the CAD's 26.7 mm.
  - A teardown found that the MG90S's larger metal-gear box sets its case bottom further out than the SG90's [6].
- **The MG996R is fine:** its CAD figures agree with TowerPro's (A − F = 15.9 both ways). The error is specific to the micro servo: the gear-boss top was read as the spline top.

**Impact**

- **Claw: blocker.**
  - The horn sets the pinion's position: `X_P0 = X_B + link_back_z(SERVO)`.
  - With the horn face 2.6–3.2 mm higher, the pinion spans x 22.0–30.6 instead of 19.4–27.4.
  - The cover's front plate starts at x 27.65, so the pinion overlaps it by 2.4–3.0 mm and the cover can't go on.
  - The racks, fixed at x 19.4–27.4, mesh with only 4.8–5.4 mm of the 8 mm face.
- **Wrist and hexapod: should fix.**
  - Every MG90S link sits about 3 mm further out along its servo axis, and every case reaches about 2.6 mm further behind its tab plane.
  - The hexapod's legs shift sideways by 3–6 mm, and its stance height changes.
  - The claw and the camera move 3 mm outboard.
  - The ranges in the three `assembly_check.json` files no longer hold.
- **Not affected:** how far each clamp screw reaches into the spline. That depends on the horn's web, not on the spline height (S2).

**Fix**

1. **Measure one MG90S with its horn pressed home:**
   - case bottom → tab underside;
   - tab thickness;
   - tab underside → spline top;
   - tab underside → horn outer face.
2. **Give the MG90S its own `ServoSpec`** instead of `replace(SG90, …)`. If the horn's offset above the spline isn't 0.6 mm, add a horn-offset field to the spec in place of the fixed +0.6 in `horn_face_z()`.
3. **Rebuild every MG90S part.** `claw_frame.py` derives the pinion, rails, cover and jaws from `link_back_z(SERVO)`, so the claw follows automatically.
4. **Re-run** the three assembly checks and the claw strength check: the claw grows by about 3 mm.

---

## Should fix

### S1. The MG90S body is 22.8 × 12.2 mm; the printed windows are 22.7 × 12.4 mm

**Evidence**

- **Published MG90S sizes:**
  - TowerPro: 22.8 × 12.2 × 28.5 mm overall, and its table gives B 22.8, D 12.4 [3].
  - Waveshare: 22.8 × 12.2 × 28.5 mm [10].
  - ProtoSupplies: 23 × 12 mm housing [8].
- **The CAD** uses 22.5 × 12.0 mm (the SG90 values).
- **The windows** are 22.9 × 12.6 mm in CAD, ≈22.7 × 12.4 mm printed: 0.1 mm clearance per end.

**Impact**

- A 22.8 mm body doesn't enter a 22.7 mm window.
- A 12.2–12.4 mm body leaves 0–0.1 mm per side.
- The guides only ask for new numbers when a size differs by more than 0.3 mm, so a 0.3 mm error passes that check.

**Fix**

- Put length 22.8 and width 12.2 in the new MG90S spec (B2). Measure the width: TowerPro's table says 12.4.
- In the guides, lower the threshold for length and width to 0.1 mm.

### S2. Horn clamp-screw lengths rest on unverified numbers; the wrist screw goes 1 mm deeper than the others

**Evidence:** `horn_face_z()` assumes the horn's outer face sits 0.6 mm above the end of the spline. On that assumption, each clamp screw reaches this far into the spline (screw length − washer − floor − 0.6):

| Joint | Screw | Floor above the horn | Into the spline |
|---|---|---|---|
| MG996R base, shoulder and elbow | M3 × 16 + Ø9 washer (0.8 mm) | 8 mm | 6.6 mm |
| Wrist (claw frame) | M2 × 12 + Ø6 washer (0.5 mm) | 4 mm | **6.9 mm** |
| Claw pinion | M2 × 10, no washer | 4.4 mm | 5.0 mm |
| Hexapod femur and tibia | M2 × 12 + washer | 5 mm | 5.9 mm |
| Hexapod coxa | M2 × 10 + washer | 3 mm | 5.9 mm |

- Neither horn's web thickness is published.
- Neither is the depth of the threaded hole in either servo's output shaft. The MG90S's shaft takes machine screws [7].
- The bags hold only one short centre screw each [14].
- If a clamp screw bottoms in the shaft, it stops clamping, and the strength review relies on that clamp.

**Fix**

1. **Measure the thread depth:** screw a long M2 (MG90S) or M3 (MG996R) into a bare shaft until it stops, and count the turns (0.4 or 0.5 mm each).
2. **Measure the web:** horn height minus spline engagement.
3. **Choose each screw** as washer + floor + web + (thread depth − 0.5 mm).
4. **Wrist:** on the present numbers, use an M2 × 10. It reaches 4.9 mm, in line with the pinion's.
5. **Buy assortments** (M2 × 8, 10, 12 and M3 × 12, 14, 16), so each length can be picked at assembly.

### S3. MG996R tab screws: the bag's screws are meant for grommets, and the CAD has none

**Evidence**

- **The bag:** 4 rubber grommets, 4 brass eyelets, 4 long flanged mounting screws of unstated size, and 1 short horn screw [14][15].
- **The CAD:**
  - the tabs sit flat on the plate (the servo frame's origin is the tab underside);
  - the printed pilots are Ø2.6 (`screw_pilot_d`);
  - the tab holes are Ø4.5, sized for grommets.

**Impact**

- With the grommets fitted, the servo sits about a millimetre higher and every link moves.
- Without them, two problems:
  - A screw meant to pass through an eyelet may be too thin to bite in a 2.6 mm pilot.
  - The screw's head bears on a thin ring around a 4.5 mm slotted hole.

**Fix:** list the tab screws explicitly: 12 × M3 × 12 pan-head self-tapping (ST2.9) and 12 × M3 washers (Ø7), with the grommets and eyelets left out. The lengths check out:

- **Base:** 4 mm plate + 6 mm boss → 9.5 mm engaged.
- **Upper link** (10 mm): 9.5 mm engaged.
- **Turntable upright** (7 mm): the tip stands 2.5 mm out of the back face at X ±24.25, clear of the gussets at |X| ≥ 28.5.

### S4. No screws are listed for the horn anti-rotation holes

**Evidence**

- **Arm guide, §4 step 3:** screw each horn down with "the small horn screws": two per MG996R joint, and one at the wrist (step 7).
- **Hexapod guide, §3 step 2:** fit one small horn screw per horn: 18 in all.
- **The bags** hold only the centre screw and the tab screws [14]; the micro servos' horn screw is a ≈2 mm self-tapper [18]. Neither BOM lists these screws.

**Fix**

- Add 7 screws to the arm BOM and 18 to the hexapod BOM.
- Size: M2 × 6 self-tapping with the horn hole drilled to 2.0 mm, or M1.4–M1.7 × 5 if the horn holes stay as they are.
- Measure the horn holes first: on micro horns they are small pushrod holes.

### S5. The Brio's USB-C port is on its back, and the stock plug sticks out 50–75 mm

**Evidence**

- **LanOC's review** puts the USB-C connection at the back of the BRIO and says the plug is long: the cord sticks out 2–3 inches behind the camera [41].
- **BUILD_GUIDE §4 step 13** says "Plug the USB cable into the camera's end".
- **The camera mount** puts a 6 mm lip 0.3 mm behind the camera's back.
- **The assembly check** models the Brio as a plain box, with no plug and no cable.

**Impact**

- The plug and cable leave the back of the camera, towards the wrist.
- Whether the plug clears the lip depends on where the port sits on the back.
- Nothing has checked a rigid 50–75 mm plug against the wrist's ±150° sweep.

**Fix**

1. Measure the port's position on the camera's back, and check it clears the 6 mm lip.
2. BOM: "thin USB-C right-angle (90°) to USB-A cable, 2 m or more".
3. Add the plug to the Brio dummy in the assembly check: about 12 × 8 × 25 mm with a right-angle plug.
4. In the guide, change "the camera's end" to "the back of the camera".

### S6. The 1/4"-20 × 3/8" thumb screw goes 5.5 mm into the camera

**Evidence**

- A 3/8" screw is 9.5 mm long under the head. Through the 4 mm seat, it enters the camera 5.5 mm.
- Camera makers keep tripod screws shorter than that: Sony asks for a screw under 5.5 mm [43].
- Logitech doesn't publish the Brio's socket depth, and the socket is in a plastic boss.

**Fix**

- Buy a 1/4"-20 × 5/16" thumb screw: 7.9 mm long, so 3.9 mm into the camera.
- Or keep the 3/8" screw with a 1.5 mm washer under its head.
- Measure the socket depth first, as the guide already says.

### S7. The arm needs three servo extensions, not two

**Evidence**

- **Lead lengths:**
  - MG996R: 30 cm (datasheet [1]) to 32 cm (TowerPro [2]).
  - MG90S: 24–25 cm [3][8].
- **Path from each servo to the bus in the base,** with a service loop at each joint and at the base yaw (rough estimate):

  | Servo | Path | Lead |
  |---|---|---|
  | Shoulder MG996R | ≈220 mm | 30–32 cm: enough |
  | Elbow MG996R | ≈320 mm | 30–32 cm: marginal |
  | Wrist MG90S | ≈460 mm | 24–25 cm: short |
  | Claw MG90S | ≈540 mm | 24–25 cm: short |

**Fix:** list three extensions: 2 × 30 cm (wrist and claw) and 1 × 15–30 cm (elbow).

### S8. Arm power bus: the parts are missing, and servo power shouldn't run through Dupont jumpers

**Evidence**

- Guide §3 says to make a 5-way power bus from stripboard or Wago-style lever connectors. Neither is in the BOM, and neither is any hook-up wire.
- The BOM's jumper wires would therefore carry V+ and GND for the MG996Rs, which stall at 2.5 A each [1].
- Servo plugs are rated about 3 A sustained [48], and thin jumpers carry less.

**Fix**

- Add stripboard with five 3-pin male header rows (G-V-S). Each servo then plugs straight onto the bus, and only its signal wire goes to the ESP32, on a jumper.
- Add 0.5–1 mm² (18–20 AWG) wire from the jack to the bus, and heat-shrink.
- The fuse and switch are covered in 02-A10.

### S9. "N20 6 V 100 rpm" doesn't define the motor

**Evidence**

- **Windings and torque:**
  - Pololu's 298:1 HP 6 V motor runs at 100 rpm and stalls at 1.6 A and 4.0 kg·cm (≈390 N·mm) [21].
  - Pololu's LP and MP 6 V windings stall at 0.36 A and 0.67 A [19].
  - Generic "6 V 100 rpm" N20 motors are sold with both 150:1 and 298:1 gearboxes [23][24].
- **Gearbox length:**
  - Pololu: 9 mm for every ratio except 1000:1, which is 12.5 mm [20].
  - Generic N20: 9 mm or 11 mm, depending on the ratio [22].
- **Output shaft:** 9 mm on Pololu motors [19], 10 mm on generic ones [23][24].
- **The CAD:** `gb_len` 9.0, `shaft_len` 10 and stall torque 130 N·mm; the rover's strength calc uses 160 N·mm at the battery pack. 02 assumes a stall of about 0.6 A.

**Impact**

- **An 11 mm gearbox doesn't fit:** the motor won't drop into the cradle, because the rear stop is 2 mm too close. The chassis would have to be re-modelled.
- **An HP motor overloads the driver:** on the 8.4 V pack with the 80 % PWM cap, it draws ≈1.8 A at stall. That is above the TB6612 carrier's continuous rating: 1 A (Pololu [25]), 1.2 A (Toshiba).
- **An HP motor overloads the strength calc:** its torque is 2.5–3 times the 160 N·mm used for the sprocket's D-bore, the hub and the track pins.
- **A 9 mm shaft** puts the set screw at the very end of the shaft (S10).

**Fix**

- BOM: "N20 (GA12), 6 V, 100 rpm (≈150:1), LP or MP winding (stall ≤ 0.7 A at 6 V), 9 mm gearbox, 3 mm D-shaft 10 mm long".
- If you already have motors, measure the gearbox and shaft before printing the chassis and the sprockets.

### S10. The sprocket set screw meets the round side of the shaft, at its very end

**Evidence**

- **Wrong side of the shaft:** in `20261026-rover-sprocket/model.py` the set-screw hole runs along +X (`Rot(0, 90, 0)`), but `d_shaft_bore_cutter` puts the shaft's flat on +Y. The screw meets the shaft 90° away from the flat.
- **At the very end:** `GRUB_Y` is 40.5, so the Ø2 screw spans y 39.5–41.5, and a 10 mm shaft ends at y 41.5 (31.5 + 10).
- **Bushing contact:** the N20's front bushing (Ø4 × 0.8 mm in `hobby_parts.py`) is taller than the 0.5 mm gap between the hub and the gearbox face. The hub therefore bears on the bushing, which doesn't turn.

**Impact**

- The screw marks the round part of the shaft instead of locking against the flat.
- With a 9 mm shaft, half the screw misses the shaft; with an 11 mm gearbox (S9), all of it does.
- The turning hub rubs on the fixed bushing.

**Fix**

- Turn the hole to +Y, onto the flat.
- Move it to y ≈ 39.5: still 0.6 mm clear of the wall, and 1 mm from the end of a 10 mm shaft.
- With a 9 mm shaft, leave the screw out and rely on the D-bore and a retaining compound.
- Make the hub-to-gearbox gap 1.0 mm, or counterbore the hub's end Ø5 × 1 mm.

### S11. The axle bolts must be fully threaded; the idler bolt length differs between documents

**Evidence**

- **Nut trap:** each bolt is drawn through an M3 nut trapped in the outer face of the wall: head inside at y 32, nut at y 35.6–38.
- **Partly threaded bolts:** M3 × 35 socket-head bolts to DIN 912 / ISO 4762 are commonly sold partly threaded [53], and so are the longer ones.
- **The stack lengths** (head at y 32, washer 0.5 mm, nyloc 4 mm):
  - Road wheel (out to y 71): needs ≥43.5 mm. An M3 × 45 stands 1.5 mm out of the nyloc: correct.
  - Idler (out to y 58.5): needs ≥31 mm. An M3 × 35 stands 4 mm out: correct.
- **Disagreements:** the BOM lists M3 × 35 for the idlers. The chassis spec ("6 × M3 × 45"), the idler spec and `assembly_check.py` use M3 × 45 for the idlers, which would stand 14 mm out.

**Impact:** on a partly threaded bolt, the thread runs out in the trapped nut. The bolt then jams with its head still short of the wall by the bolt's unthreaded length, so it can't be tightened.

**Fix**

- BOM: "fully threaded": DIN 933 / ISO 4017 hex head, or fully threaded socket head.
- Make the specs and the assembly check use M3 × 35 for the idlers.

### S12. Protected 18650 cells may not fit the holder, and no charger is listed

**Evidence**

- A typical 2 × 18650 holder (76 × 41 × 20 mm) is made for 65 mm cells [35].
- Protected button-top cells are about 69.5 mm long (Tenergy's figure) [36].
- The guide asks for protected cells or a 2S BMS, and says to charge outside the rover, but the BOM lists no charger.

**Fix**

- Buy a holder made for protected (≈70 mm) cells. Or use unprotected 65 mm cells with a 2S BMS, charged at 8.4 V through the BMS.
- Add a two-bay Li-ion charger to the BOM.
- A slightly longer holder still fits on the floor (x 22–102), clear of the columns and the bolt heads.

### S13. The HC-SR04's header and jumpers don't fit between floor and lid

**Evidence**

- The module's 4-pin header leaves along one long edge, and mounting brackets take it with the header facing up or down [31].
- In the chassis, the 20 mm board spans Z 20–40 (`SENSOR_Z` 30). That leaves 8.8 mm to the floor (11.2) and 8.7 mm to the lid (48.7).
- The pins plus Dupont housings need about 20 mm.
- The HC-SR04 dummy in the assembly check has no header.

**Fix**

- Before fitting, bend the four pins 90° towards the inside of the tub (there's 12 mm behind the board) and push the jumpers on horizontally. Or solder the leads on directly.
- Add the header to the dummy.

### S14. The UBEC must accept a 2S input

**Evidence**

- The BOM asks for a "6 V 5 A UBEC" and says nothing about its input range.
- Some common 5 A UBECs are high-voltage types. Hobbywing's 5A HV takes 8–42 V (3–10S) [38], so on a 2S pack (6.0–8.4 V) it won't hold its output. It also measures 48 × 27 × 9 mm and weighs 30 g.
- The CAD's `UBEC_6V_5A` is 45 × 20 × 9 mm and 15 g, and the UBEC isn't in the assembly check.

**Fix**

- BOM: "UBEC, 2S-compatible input (≈5.5–26 V), 6 V output, ≥5 A continuous, 8–10 A preferred". Each MG90S stalls at 0.7 A (measured [8]) to 1.2–1.6 A at 6 V [9]; for the current margin, see 02-H3 and 02's hexapod notes.
- Add the UBEC to the assembly check where the guide puts it: on its side, beside the LiPo.

### S15. The LiPo line is incomplete

**Evidence**

- The BOM lists a "2S 1000 mAh LiPo (≈70 × 35 × 18 mm) with XT30/JST lead" and a "toggle or rocker switch".
- A JST-RCY connector is rated about 5 A continuous [48]. An XT30 is rated 15 A continuous and 30 A peak [47].
- No C-rating, charger, LiPo bag or voltage alarm is listed. 02-H4 covers the alarm, the fuse and the switch rating.

**Fix**

- BOM: "2S 1000 mAh, ≥20C, XT30", plus an XT30 female pigtail with 18 AWG leads.
- Add a 2S balance charger and a LiPo charging bag.
- Any 20C 1000 mAh pack supplies 20 A. That is well above what an 8–10 A UBEC draws from it, about 7–9 A at 7.4 V.

---

## Notes

### N1. MG996R: dimensions match; stall-current and torque figures vary

- **Matches:**
  - 40.7 × 19.7 × 42.9 mm and 55 g [1].
  - TowerPro's table [2]: B 40.9, D 20, A 42.7, E 54 (tab span), F 26.8 (CAD 27.0), C 37 (CAD `case_top` 36.5).
  - 25-tooth spline [14].
- **Stall current:** the datasheet gives 2.5 A at 6 V [1], while TowerPro's current product page says 1.4 A [2]. Size the supply for 2.5 A.
- **Stall torque:** 11 kgf·cm at 6 V (1079 N·mm; the CAD uses 1000) [1]. Some listings claim 13–15 kg·cm [14][16]; a servo that strong would raise every strength load by 20–40 %.
- **Unverified:** the tab-hole spacing (48.5 × 10), the shaft-to-end distance (10.2) and the horn sizes (hub 11, 17.5 to the tip, tip 5.5, 2.8 thick). The guide's measuring step covers them, and the 4.5 mm tab holes give ±0.75 mm of play.
- **Supply:** 02 sizes the 6 V 5 A adapter: about 8.9 A with every servo stalled, about 2 A holding. I agree, so there is no separate finding here.

### N2. Brio 4K

- **Confirmed:**
  - The camera is 27 × 102 × 27 mm and weighs 63 g. The clip weighs 44 g and comes off.
  - The 1/4" tripod thread is in the bottom of the camera itself, not in the clip [39][40][41]. LanOC found it under the mount once the mount was pulled off.
  - The camera comes with a 2.2 m USB-C to USB-A cable.
- **Not published:**
  - where the thread sits along and across the bottom;
  - how deep it is.

  The seat's slot allows ±4 mm along the camera but nothing across it, and the lip leaves only 0.3 mm. Measure the thread's distance from the back face before printing.
- **Model:** "Brio 4K" must mean the original BRIO (102 × 27 × 27 mm). The MX Brio is 98 × 61.6 × 52.2 mm including its mount, and weighs 234 g with clip and cable [42]. It won't fit the seat.
- **Cable:** thin, flexible USB-C cables are usually USB 2.0, so the Brio will give 1080p, not 4K. That is enough for the vision loop.
- **`BRIO_EDGE_R`** (6.0) was estimated from photos: measure it.

### N3. DC jack: the CAD needs an 11 mm thread; the common jack is M8

- The base's jack hole is 11.4 mm, for an 11 mm thread.
- The common 5.5 × 2.1 mm panel jack (DC-022B) has an M8 thread: it needs a 7.8 mm hole, in a panel up to 3 mm thick [45].
- Name an 11 mm-thread jack rated at least 5 A in the BOM, or change `JACK_D` to 7.8 before printing the base.

### N4. ESP32 boards shorter than ≈49.5 mm don't seat

- **The CAD's two boards fit:**
  - DevKitC: 54.4 × 27.9 mm [33], the same as the CAD.
  - DOIT DevKit V1 30-pin: 51.8 × 28.2 mm [34], against 51.5 × 28.3 in the CAD. It still lands on the short board's ledge.
- **Shorter boards don't.** Some boards sold as "30-pin ESP32" are about 48 mm long. They miss the short board's ledge:
  - in the arm cradle, the ledge ends at x 2.0 but such a board ends at x 3.0;
  - in the rover and hexapod seats, the support starts 49 mm from the USB end.
- **Fix:** name the board in all three BOMs.

### N5. Rover small parts check out

- **Match the CAD:**
  - **TB6612 carrier:** 0.6 × 0.8 in (15.24 × 20.32 mm), 1.5 g. 1 A continuous and 3 A peak per channel (Pololu [25]); Toshiba rates the chip at 1.2 A and 3.2 A.
  - **MP1584 module:** 22 × 17 × 4 mm, 4.5–28 V in, 1.8 A typical and 3 A maximum out [26].
  - **HC-SR04:** 45 × 20 × 15 mm [30], Ø16 transducers 26 mm apart [31].
  - **MTS-102 toggle:** M6 × 0.75 bushing for a 6–6.5 mm hole [44]; the CAD prints 6.2 mm. Rated 6 A at 125 VAC with no published DC rating; the rover draws under 2 A.
- **Dowel pins:** 2 × 24 mm pins exist (ISO 8734 / DIN 6325 m6, and stainless ISO 2338) [46]. Their length tolerance is +0.5/−0, so "flush on both sides" can mean up to 0.5 mm proud. That still clears the road-wheel flanges, which leave 2 mm or more. If you can buy them, use the 24 mm pins rather than 23.5 mm cut rod; the track-link spec still says rod.
- **100 µF capacitor:** add "16 V or more": the pack reaches 8.4 V.
- **Hot glue** holds the HC-SR04 in the guide but isn't in the BOM.
- **Battery mass:** `BATT_2X18650` assumes 135 g. Two cells (≈94 g) and a 15–20 g holder come to about 110 g.

### N6. Hexapod small parts check out

- **PCA9685 board (Adafruit 815):** 62.5 × 25.4 × 3 mm, with 2.5 mm mounting holes [27][28].
  - The hole spacing isn't published. The board file's outline (−1.905…60.325 × −6.477…18.923 mm, corners r 3.175) puts holes on the corner centres 55.88 × 19.05 mm apart [29]. That matches the CAD's 56 × 19 within 0.12 mm.
  - Bridging A0 gives address 0x41, as the guide says [28].
  - Adafruit suggests n × 100 µF across V+, here 1800 µF [28]: add 470–1000 µF in each board's capacitor pad.
- **LiPo:** sizes vary, for example 56 × 30 × 19 mm and 57 g [37]. The strap slots and the 40 mm gap between the plates take that.
- **MG90S variants:** Waveshare lists 2.8 kg·cm at 6 V [10]; the CAD uses TowerPro's 2.2 [17]. A stronger servo raises every leg load by about 27 %.
- **Leads:** the MG90S lead is 24–25 cm, so the 15 cm extensions for the tibia servos are right.

### N7. Fastener lengths that check out; two are marginal

| Fastener | Through | Thread engaged | Verdict |
|---|---|---|---|
| Claw cover, top: M3 × 10 | 3 mm top wall | 7 mm of a 14 mm pilot | OK |
| Camera mount: M3 × 18 ISO 7380 | 3.5 mm pad + 3 mm wall | 11.5 mm of 14 mm | OK |
| Claw cover, front: M3 × 12 | 3 mm front plate | 9 mm of 10 mm | OK |
| Claw servo tabs: M2 × 8 | 2.5 mm tab | 5.5 mm in the 6 mm bulkhead | OK; less if your MG90S tab is thicker [6] |
| Wrist servo tabs: M2 × 12 | 2.5 mm tab | 9.5 mm in 10 mm | OK |
| Ring: M3 × 6 | 3 mm tab | 3 mm in the 4 mm plate | OK (thin, but the ring only catches) |
| Cradle: M3 × 10 | 4 mm clamp | 6.0 mm in a 6.0 mm pilot | **No margin:** a counterbore printed 0.2 mm short bottoms the screw |
| Desk: M3 × 50 | 40 mm pillar | 10 mm into wood | **Short bite:** #4 × 2¼" (57 mm) screws give 17 mm |
| Rover lid: M3 × 10 | 3 mm lid | 7 mm of 12 mm | OK |
| Rover road-wheel nyloc | — | bolt 1.5 mm out of the nut | OK |
| Hexapod servo tabs: M2 × 8 | 2.5 mm tab | 1.5 / 1 mm out of the 4 / 4.5 mm plates; 5.5 mm into the 7 mm femur | OK |
| Hexapod top plate: M3 × 8 | 3 mm plate | 5 mm of 10 mm | OK |
| PCA9685: M2.5 × 6 | 1.6 mm PCB | 4.4 mm in a 6 mm post pilot | OK |

### N8. Stale or contradictory BOM text

- **Rover `assembly_plan.md`** still says the tracks are pinned with 1.75 mm filament, the switch is a mini rocker, and the TB6612 gives 1.2 A against an N20 stall of ≈0.6 A. These are superseded by the steel pins, the MTS-102 and S9.
- **Rover guide, §3 step 6:** "tighten the idler bolt's nut (inside)". The nut is trapped outside the wall; you turn the bolt head, inside.
- **Arm guide, §4 step 8:** "Slide the claw MG90S through the bulkhead window from behind". Its tabs rest on the bulkhead's front face, so it goes in from the front, case first.
- **Arm `assembly_plan.md`:** the Horns and Fasteners rows still say SG90 and "M2×12 + Ø6 on SG90 joints". The forearm model still uses `SG90`: the numbers are the same today, but it must switch to the new MG90S spec (B2).
- **Arm `README.md`** still lists the superseded gripper and 8 printed parts.
- **`hobby_parts.py`:** `KCD11_SWITCH_CUTOUT` is no longer used; the chassis now takes the toggle switch.

---

## Missing items, by robot

| Robot | Parts | Tools |
|---|---|---|
| Arm | Power-bus stripboard, header rows and hook-up wire (S8); a third servo extension (S7); 7 horn screws (S4); 12 MG996R tab screws + 12 washers (S3); right-angle USB-C cable (S5); 1/4"-20 × 5/16" thumb screw (S6) | Phillips screwdriver with a shaft of 75 mm or more (already in the guide); 1.5 mm drill; flush cutters and a file (pinion horn); soldering iron |
| Rover | Li-ion charger; holder for protected cells (S12); hot glue; 100 µF ≥16 V (N5) | 0.9 mm hex key (M2 set screws); small vice or parallel pliers (track pins); multimeter (setting the buck); soldering iron |
| Hexapod | 2S balance charger, LiPo bag, XT30 pigtail (S15); voltage alarm, fuse, ≥10 A DC switch (02-H4); 18 horn screws (S4); double-sided tape (guide §3 step 5); capacitors in the PCA9685 pads (N6) | 1.2 mm drill; multimeter |

## Battery safety notes

**Rover (Li-ion).**

- The protection circuit in each protected cell is the rover's only protection against shorts and over-discharge. Never swap in unprotected cells without a BMS.
- Charge the cells in a proper charger, not in the rover, and never leave them charging unattended.
- Don't use a cell with a torn wrap or a dent.
- Check the polarity with a meter before the first switch-on, as 02 notes.

**Hexapod (LiPo).**

- The pack has no protection of its own, so fit the alarm, fuse and switch from 02-H4.
- Stop walking at 3.3–3.5 V per cell under load, and never let a cell drop below 3.0 V [49].
- Store the pack at 3.8–3.85 V per cell [50].
- Charge only with a balance charger, never unattended, and never charge or use a swollen pack [50].
- Unplug the pack after use.

## Sources

**Servos**

- [1] TowerPro, MG996R datasheet (Cornell mirror): https://people.ece.cornell.edu/land/courses/ece4760/FinalProjects/f2017/kmv48_rp625/kmv48_rp625/kmv48_rp625/MG996RTowerPro.pdf
- [2] TowerPro, MG996R product page (table A–F, 1.4 A stall, 32 cm lead): https://www.towerpro.com.tw/product/mg996r/
- [3] TowerPro, MG90S product page (22.8 × 12.2 × 28.5 mm, table A–F, 25 cm lead): https://www.towerpro.com.tw/product/mg90s-3/
- [4] TowerPro, SG90 product page (table A–F): https://www.towerpro.com.tw/product/sg90-7/
- [5] OpenSCAD MCAD, `servos.scad` (`towerprosg90`: body, gear boss, spline, tab, cable): https://raw.githubusercontent.com/openscad/MCAD/master/servos.scad
- [6] New Screwdriver, micro servo enclosure notes (lead exits nearer the output shaft; MG90S taller; tab thickness varies): https://newscrewdriver.com/2020/12/26/notes-on-micro-servo-enclosure/
- [7] New Screwdriver, micro servo output shaft notes (the MG90S shaft is tapped for machine screws): https://newscrewdriver.com/2020/12/27/notes-on-micro-servo-output-shaft/
- [8] ProtoSupplies, MG90S (measured 700 mA stall, 32 mm tall with shaft, 24 cm lead): https://protosupplies.com/product/servo-motor-micro-mg90s/
- [9] Kpower, MG90S current draw (1.2–1.6 A stall at 6 V): https://www.kpower.com/insight_bldc/7870.html
- [10] Waveshare, MG90S (22.8 × 12.2 × 28.5 mm, 2.8 kg·cm at 6 V): https://www.waveshare.com/MG90S-Servo.htm
- [11] Wiltronics, MG90S (TowerPro table A–F, horns and screws included): https://www.wiltronics.com.au/product/18712/micro-servo-metal-hears-2-5kg-cm-180deg-sg90s/
- [12] TowerPro SG90 datasheet (TAMS mirror): https://tams.informatik.uni-hamburg.de/lehre/2023ss/vorlesung/es/doc/sg90.pdf
- [13] M5Stack, SG90 (23 × 12.2 × 29 mm, 21T spline): https://docs.m5stack.com/en/accessory/SG90_Servo
- [14] Probots, MG996R (bag contents, 25T spline, 30 cm lead): https://probots.co.in/mg996r-13kg-metal-gear-servo-180.html
- [15] Maker Store, MG996R (arms, screws, grommets and ferrules; 2.5 A stall): https://www.makerstore.com.au/?p=3313
- [16] Kitronik, MG996R (13–15 kg/cm listing): https://kitronik.co.uk/products/2575-large-180-servo
- [17] Components101, MG90S: https://components101.com/motors/mg90s-metal-gear-servo-motor
- [18] Arduino forum, servo horn screw sizes: https://forum.arduino.cc/t/servo-arm-screw-mount-size/696481

**Motors and rover parts**

- [19] Pololu, micro metal gearmotors (9 mm D-shaft; LP/MP/HP stall at 6 V): https://www.pololu.com/category/60/micro-metal-gearmotors
- [20] Pololu, micro metal gearmotor dimensions (gearbox 9 mm, 12.5 mm for 1000:1): https://www.pololu.com/file/0J1487/pololu-micro-metal-gearmotors-rev-6-2.pdf
- [21] Pololu, 298:1 micro metal gearmotor HP 6 V (100 rpm, 4.0 kg·cm, 1.6 A): https://www.pololu.com/product/994
- [22] ineedmicromotors, N20 gear motor (gearbox 9 or 11 mm by ratio): https://ineedmicromotors.com/what-is-n20-gear-motor/
- [23] RobotShop, 6 V 298:1 micro metal gearmotor HP, 100 rpm (10 mm shaft): https://robotshop.com/products/e-s-motor-6v-2981-micro-metal-gearmotor-hp-100rpm
- [24] RobotShop, JGA12-N20 6 V 100 rpm (10 mm shaft): https://robotshop.com/products/aslong-motor-dc-6v-100rpm-3mm-shaft-mini-metal-gearwheel-gear-motor-n20-geared-motor
- [25] Pololu, TB6612FNG carrier (0.6 × 0.8 in; 1 A continuous, 3 A peak): https://www.pololu.com/product/713 and https://www.pololu.com/product/713/specs
- [26] MP1584 module (22 × 17 × 4 mm, 4.5–28 V, 1.8 A typical / 3 A maximum): https://45-in-1-sensor-kit.readthedocs.io/en/latest/41.mp1854en.html
- [30] SparkFun, HC-SR04 datasheet (45 × 20 × 15 mm): https://cdn.sparkfun.com/assets/a/8/9/c/a/HC-SR04-33_Datasheet.pdf
- [31] ProtoSupplies, HC-SR04 bracket (Ø16 holes 26 mm apart; header up or down): https://protosupplies.com/product/hcsr04-ultrasonic-range-finder-module-bracket/
- [35] Tayda, 2 × 18650 holder (76 × 41 × 20 mm, for 65 mm cells): https://www.taydaelectronics.com/2-x-18650-lithium-battery-holder-case-black-with-wire-leads.html
- [36] DigiKey forum, protected 18650 length (69.5 mm): https://forum.digikey.com/t/what-length-battery-does-this-fit-button-top/68267
- [44] EM, MTS-102 (M6 × 0.75 bushing, 6 A at 125 VAC): https://www.em.co.za/MTS-102 ; Jameco 66-1201: https://www.jameco.com/z/66-1201-Mini-Toggle-Switch-SPST-ON-OFF-6-Amps-125VAC-0-25-Inch-Mounting_2230328.html
- [46] McMaster-Carr, 2 mm dowel pins (24 mm in ISO 8734 and ISO 2338): https://www.mcmaster.com/products/dowel-pins/diameter~2-0000-mm/diameter~2-000-mm/diameter~2-mm ; Zoro, 2 × 24 mm DIN 6325 (length +0.5/−0): https://www.zoro.com/i/G3423598/
- [53] Accu, M3 × 35 DIN 912 socket head: listed as not fully threaded: https://accu-components.com/us/metric-cap-head-screws/386626-SSC-M3-35-12-9

**Controllers and hexapod parts**

- [27] Adafruit, PCA9685 16-channel driver (62.5 × 25.4 × 3 mm; reverse-polarity protection on the terminal block): https://www.adafruit.com/product/815
- [28] Adafruit, PCA9685 guide (A0 → 0x41; n × 100 µF; 2.5 mm holes): https://learn.adafruit.com/16-channel-pwm-servo-driver.md?view=all and https://learn.adafruit.com/16-channel-pwm-servo-driver/downloads
- [29] Adafruit, PCA9685 board files (outline and corner radius): https://github.com/adafruit/Adafruit-16-Channel-PWM-Servo-Driver-PCB
- [33] Grid Connect, ESP32-DevKitC-32E (54.4 × 27.9 mm): https://www.gridconnect.com/products/esp32-devkitc-32e-wroom-module-development-kit
- [34] Mischianti, DOIT ESP32 DevKit V1 (28.2 × 51.8 mm): https://www.mischianti.org/2021/02/17/doit-esp32-dev-kit-v1-high-resolution-pinout-and-specs/
- [37] Overlander, 2S 1000 mAh 30C (56 × 30 × 19 mm, 57 g): https://overlander.co.uk/lipo-batteries/lipo-batteries-1000mah-7-4v-2s-30c.html
- [38] Hobbywing, 5A HV UBEC manual (8–42 V input, 5 A / 7.5 A burst, 48 × 27 × 9 mm, 30 g): https://support.hobbywingdirect.com/hc/article_attachments/20213639826451
- [47] DigiKey forum, XT30 rating (15 A continuous, 30 A peak): https://forum.digikey.com/t/xt30-xt60-xt90-deans-connector-comparison/34551
- [48] Luton Model Boat Club, battery connectors (JST-RCY 5 A; servo plugs 3 A): https://lutonmodelboat.co.uk/files/BatteryConnectors.pdf

**Camera, jack and battery safety**

- [39] Logitech, 4K Pro webcam quick-start guide (27 × 102 × 27 mm, 63 g; clip 44 g; tripod thread on the camera's bottom; 2.2 m cable): https://logitech.com/assets/66128/4/logitech-4k-pro-webcam-qsg.pdf
- [40] Logitech, Brio / Brio 4K setup FAQ (remove the clip; thread on the bottom): https://hub.sync.logitech.com/brio/post/brio-brio-4k-setup-essentials-and-faqs-EZcOqEHN0fffbPX
- [41] LanOC, Logitech BRIO review (USB-C at the back with a long plug; thread under the clip): https://lanoc.org/review/photography/logitech-brio?showall=1
- [42] Logitech, MX Brio specification (98 × 61.6 × 52.2 mm, 234 g): https://support.logi.com/hc/en-ch/articles/18849231040023-Specification-MX-BRIO
- [43] Sony, tripod screw length (under 5.5 mm): https://helpguide.sony.net/ilc/2020/v1/en/contents/TP1000156794.html
- [45] Sigmanortec, DC-022B panel jack (7.8 mm hole, panel ≤3 mm): https://sigmanortec.ro/en/panel-female-jack-55x21mm-dc-022b
- [49] Grepow, LiPo discharge (never below 3.0 V per cell; stop at 3.3–3.5 V): https://www.grepow.com/blog/how-to-discharge-a-lipo-battery
- [50] Robocraze, LiPo safety (balance charging, never unattended, 3.8–3.85 V storage, swollen packs): https://robocraze.com/blogs/post/lipo-battery-safety-charging-storage-and-handling-guide

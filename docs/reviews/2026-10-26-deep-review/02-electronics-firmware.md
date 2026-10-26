# Deep review 02: wiring, power and firmware

Robot arm, tracked rover and hexapod. Independent review, 2026-10-26. This slice covers the electronics, power and firmware, plus the arm's PC script. Bought-part dimensions and the mechanical systems are in the other reviews.

## Summary

| Robot | Blocker | Should fix | Note |
|---|---|---|---|
| Robot arm (sketch + PC script) | 2 | 10 | 3 |
| Tracked rover | 0 | 4 | 6 |
| Hexapod | 0 | 6 | 7 |
| **Total** | **2** | **20** | **16** |

The five that matter most:

1. **Arm, blocker (A1).** `x` stops a move, but the next command of any kind, even `p`, finishes it.
2. **Arm, blocker (A2).** When `arm_pc_control.py` opens the serial port, the ESP32 resets. The sketch then sends every joint to its boot pose at full servo speed, and the `status` command reports that boot pose instead of where the arm was.
3. **Arm (A4).** Clamping each joint on its own doesn't keep the claw or the Brio off the desk. In the project's own collision model, 96 of 1183 poses inside the servo travel hit the desk. A guard, checked against that model, is given below.
4. **Hexapod (H1).** The sketch assumes the PCA9685 runs at 27 MHz. On a chip at the datasheet's 25 MHz every pulse is 8 % long: centre 1616 µs, and "180°" becomes 2698 µs, beyond the MG90S's end stop.
5. **Rover and hexapod (R1, H4).** No firmware reads the battery. The hexapod's LiPo has no protection at all: no BMS, no fuse and no low-voltage cut-off.

## How this was checked

- **Read:** the three `BUILD_GUIDE.md`s, each robot's `assembly_plan.md`, `assembly_check.json` and `assembly_check.py`, the three sketches, `pc/arm_pc_control.py`, `claw_frame.py`, `hex_frame.py` and the ESP32 cradle spec.
- **Compile:** no ESP32 toolchain is installed, so each sketch was built with g++ against a host shim of the Arduino-ESP32 API. Each was built twice: once as C++11 (core 2.x) and once as C++23 (core 3.x). The shim reproduces the parts of the real core that matter here:
  - the core's `constrain` macro and `map()`;
  - `String` with the `substring` rules of `WString.cpp`;
  - an ESP32Servo mock (values below 500 are degrees; pulses are clamped to min/max µs);
  - an `Adafruit_PWMServoDriver` mock that copies the library's prescale and `writeMicroseconds` arithmetic.

  All three sketches compile, with only conversion warnings. This catches C++ and logic errors. It doesn't catch ESP32 link errors or library-version problems.
- **Logic:** scripted serial sessions through each sketch. The results are quoted with each finding.
- **Arm kinematics:** I reused `assembly_check.py`'s own `place()` and `overlaps()` on a grid of poses inside the servo travel, with the Brio fitted. The grid sweeps the shoulder 0–180° in 15° steps, and the elbow and wrist ±90° in 15° and 30° steps, all in the check's frame. It ran 1183 poses with the claw closed and 1183 with it fully open at yaw 0, plus 3549 more at yaw 45°, 90° and −90°.
- **Fixes:** every firmware fix below was compiled and run in the same shims, in patched copies in the scratchpad (not in the repo). The PC fix was run against a fake serial port. OpenCV calls were checked on OpenCV 5.0.0.
- **Scratch files:**
  - `/tmp/claude-0/-home-claude/50a131db-7c91-50e6-a869-32c6a4b19591/scratchpad/inocheck2/`: shims, harnesses, `*_fixed.inc`, `pc_arm_proposed.py`.
  - `/tmp/claude-0/-home-claude/50a131db-7c91-50e6-a869-32c6a4b19591/scratchpad/armreach/`: the pose grids.

---

## 1. Robot arm

### A1. Blocker: `x` stops a move, but the next command resumes it

**Evidence**

- `arm_test.ino:63` returns `false` on `x` without changing any joint's `target`.
- `arm_test.ino:115–120` sends every command except `?`, `x` and `m` through `runMove()`, including `p`. `runMove()` drives every joint towards its stored target.

**Test**

- `s 0`, `x`, `p`: the shoulder stops at 89°, then `p` carries it on to 0° (500 µs).
- `s 0`, `x`, `e 100`: the elbow goes to 100°, and the shoulder also continues to 0°.

**Why it matters:** the guide (`BUILD_GUIDE.md:158`) and the sketch header (`arm_test.ino:17`) give `x` as the way to stop a wrong move. Typing `p` to see where the arm stopped, or moving another joint, finishes the move you stopped, for example into the desk.

**Fix:** make a stop forget the old targets, and make `p` print without moving.

```cpp
// runMove(), replacing line 63
if (Serial.available() && Serial.peek() == 'x') {
  Serial.read();
  for (int i = 0; i < N; i++) joints[i].target = joints[i].deg;          // a stop sticks
  clawMm = constrain(GRIP_OPEN_DIR * (joints[CLAW].deg - GRIP_CLOSED_DEG) / DEG_PER_MM, 0.0f, GRIP_MAX_MM);
  return false;
}
// loop(), before the command chain
if (cmd == 'p') { printAngles("angles b s e w | claw mm:"); return; }
```

### A2. Blocker for PC control (§6): opening the port resets the ESP32, and the sketch then snaps every joint to its boot pose

**Evidence**

- `arm_pc_control.py:29–30` opens the port with pyserial's defaults, then sleeps 2 s because "the ESP32 resets when the port opens".
- `arm_test.ino:75–81` then writes 90/90/90/90 and the compiled closed claw angle straight to the servos. There's no ramp, only 300 ms between joints.
- Espressif's esptool docs warn that "some OS and/or drivers may activate RTS and or DTR automatically when opening the serial port". On a DevKit those lines drive EN and GPIO0.

**Effect of each `python arm_pc_control.py … move …` or `… status`:**

- The servos get no pulses for up to about 1.7 s, and the shoulder can sag under the arm's weight.
- Each joint then jumps to 90° at full servo speed (about 0.14 s per 60° for an MG996R).
- The claw closes to the compiled `GRIP_CLOSED_DEG`, losing any `k` trim.
- `status` as a CLI command reports the boot pose, never where the arm was.
- Closing the port can toggle the lines again.

**Fix:** on both sides.

1. **PC:** open the port with DTR and RTS inactive, and wait for the banner instead of a fixed 2 s. The tested code is in A11. pyserial applies the line states at `open()` when they are set beforehand. Its issue #729 notes that a short glitch is still possible on POSIX, so step 2 is still needed.
2. **Firmware:** start where the arm stopped (A7), so a reset that still happens moves nothing.
3. **Usage:** keep one connection open for the whole session, as the preview mode does, rather than one process per move.

### A3. Should fix: a missing or bad number becomes 0, or NaN

**Evidence**

- `arm_test.ino:110`, `:112` and `:117` use `String::toFloat()`, which returns 0 for `""` and `"abc"`.
- `arm_test.ino:97–100` accepts `nan` from `sscanf`.

**Test**

- `s` alone drives the shoulder to 0°, which is horizontal.
- `k` alone sets the closed angle to 0°. That overcloses the claw by 20° (about 6 mm) into a stall.
- `b nan` is stored silently. The next `e 100` turns the base angle into NaN. `servo.write((int)roundf(NaN))` is an undefined conversion, which typically lands on a pulse limit: a full-speed jump to an end of travel.
- Python formats NaN as `nan`, so an inverse-kinematics bug on the PC reaches the arm as `m nan …`.

**Fix** (tested: all four cases are now refused with an `err` reply):

```cpp
bool parseNum(const String &s, float &v) {        // "s", "s abc" and "s nan" are refused
  char *end; v = strtof(s.c_str(), &end);
  return end != s.c_str() && *end == '\0' && std::isfinite(v);
}
// loop(), before the command chain; then use val instead of args.toFloat()
float val = 0;
if (strchr("bsewgk", cmd) && !parseNum(args, val)) { Serial.println("err need a number, e.g. s 100"); return; }
// in 'm', after sscanf:
for (int i = 0; i < 5; i++) if (!std::isfinite(v[i])) { Serial.println("err not a number"); return; }
```

### A4. Should fix: per-joint clamps don't keep the claw or the camera off the desk

**Evidence**

- `arm_test.ino:68` clamps each joint on its own to 0–180°.
- `BUILD_GUIDE.md:158` says the sketch "clamps every joint to the limits the assembly check found collision-free". But the check swept one joint at a time from neutral poses (`assembly_check.py:193–196`).

**Test:** the check's own meshes and `place()`, Brio fitted.

- **Claw closed, yaw 0:** 96 of 1183 poses inside the servo travel put the claw, jaws or Brio into the desk.
- **Claw open 44 mm, yaw 0:** 110 of 1183 poses do.
- **Two examples:**
  - Upper link horizontal, forearm 45° down: the jaws are 15 mm into the desk and the Brio overlaps it by 1070 mm³.
  - Upper link horizontal, forearm 90° down: the jaws are 63 mm into the desk.
- **Which command:** whether `s 0` or `s 180` is "horizontal towards the claw" depends on the mounting side (`BUILD_GUIDE.md:163`), so either one can start this.
- **Other yaws:** at yaw 45°, 90° and −90° the desk hits repeat, 96 per yaw.
- **Self-collision:** at yaw 0 no pose collides with the arm itself. At yaw ±90° there are four small grazes (1.3–5.5 mm³) of the claw cover on the base box, with the shoulder at 180° and the elbow at +90°.

**Fix:** a planar desk guard, checked at every 15 ms step in `runMove()`.

**Validation against the mesh model:**

- It let through **none** of the 494 colliding poses: 96 per yaw with the claw closed at four yaws, plus 110 with it open.
- It also blocks the four base grazes.
- It blocked 20 good poses in each 1183-pose grid, about 1.7 %.
- In the shim, `s 0` then `e 0` stops with `blocked: desk` at elbow 65°.

```cpp
// Angles in assembly_check's frame: shoulder 0 = upper link horizontal towards the fingertips' side, + up;
// elbow/wrist 0 = straight, + up. Set the signs once after assembly, with small moves:
const int SH_SIGN = +1;   // +1 if "s 0" puts the upper link horizontal on the claw's side, -1 if "s 180" does
const int EL_SIGN = +1;   // +1 if a larger "e" lifts the forearm
const int WR_SIGN = +1;   // +1 if a larger "w" lifts the claw
const bool CAMERA_FITTED = true;
const float DESK_Z = -40.0f;   // desk top relative to the base top plate (shoulder axis at +60.5)
bool poseSafe(float s, float e, float w, float gapMm) {
  float q1 = SH_SIGN > 0 ? s : 180.0f - s, q2 = EL_SIGN * (e - 90.0f), q3 = WR_SIGN * (w - 90.0f);
  float p1 = radians(q1), p2 = radians(q1 + q2), p3 = radians(q1 + q2 + q3);
  float ez = 60.5f + 100.0f * sinf(p1);            // elbow axis
  float wz = ez + 90.0f * sinf(p2);                // wrist axis
  float tz = wz + 73.0f * sinf(p3);                // between the fingertips
  float mz = wz + 40.0f * sinf(p3);                // middle of the claw
  float side = (gapMm / 2.0f + 12.0f) * fabsf(cosf(p3));   // jaws stick out either side of the claw axis
  return ez >= DESK_Z + 25 && wz >= DESK_Z + (CAMERA_FITTED ? 62 : 25) &&
         tz >= DESK_Z + 8 + side && mz >= DESK_Z + 8 + side;
}
float clawMmFromDeg(float d) { return constrain(GRIP_OPEN_DIR * (d - GRIP_CLOSED_DEG) / DEG_PER_MM, 0.0f, GRIP_MAX_MM); }
// runMove(): work out the next step first, check it, then write it
for (int k = 1; k <= steps; k++) {
  float nxt[N];
  for (int i = 0; i < N; i++) nxt[i] = start[i] + (joints[i].target - start[i]) * k / steps;
  bool stop = false;
  if (!poseSafe(nxt[1], nxt[2], nxt[3], clawMmFromDeg(nxt[CLAW]))) { Serial.println("blocked: desk"); stop = true; }
  else if (Serial.available() && Serial.peek() == 'x') { Serial.read(); stop = true; }
  if (stop) { for (int i = 0; i < N; i++) joints[i].target = joints[i].deg; clawMm = clawMmFromDeg(joints[CLAW].deg); return false; }
  for (int i = 0; i < N; i++) { joints[i].deg = nxt[i]; joints[i].servo.write((int)roundf(nxt[i])); }
  delay(STEP_MS);
}
```

Then change `BUILD_GUIDE.md:158` to say the sketch stops a move before the claw or camera reaches the desk.

### A5. Should fix: the documented desk reach and the "pick from desk" pose need angles the servos can't reach

**Evidence**

- `assembly_check.py:204–206` searches shoulder −30° to 180°, elbow −160° to 140° and wrist ±120°.
- The reported desk reach (`assembly_check.json:524–545`) uses shoulder −10° for the farthest point and elbow +130° for the nearest.
- The "pick from desk" pose (`assembly_check.json:127–142`) uses elbow −120°.
- With 180° servos centred as the guide says, the shoulder covers 0–180° and the elbow and wrist ±90°. That matches the plan's own "Use" column (`assembly_plan.md:45–50`).
- `BUILD_GUIDE.md:4` and `assembly_plan.md:52` quote 76–260 mm.

**Re-run inside the servo travel:** collision-free poses with the fingertips on the desk reach **123 to 247 mm** from the yaw axis.

- Nearest: q = 0/150/90/50.
- Farthest: q = 0/5/−40/−10.
- Four named poses are outside the servo travel: "pick from desk", both "elbow folded 150" poses and "camera over the arm (wrist −150)". They still prove clearance, but not reach.

**Fix**

- Quote about 125–245 mm in `BUILD_GUIDE.md:4` and `assembly_plan.md:52`.
- Limit `assembly_check.py`'s reach search and named poses to shoulder 0–180° and elbow/wrist −90° to +90°.

### A6. Should fix: the shoulder servo is on GPIO14, which outputs a PWM signal at boot

**Evidence:** `arm_test.ino:26`, `BUILD_GUIDE.md:77` and `:87`. Line 87 says the GPIOs are "not boot-strapping pins, so the board boots normally". GPIO14 isn't a strapping pin. But Random Nerd Tutorials' ESP32 pin reference lists it, with GPIO15, among the pins that output a PWM signal at boot. The shoulder carries the whole arm, so it is the worst joint to twitch at every reset.

**Fix**

- Move the shoulder to GPIO32. GPIO33, 18, 19 or 23 are also clean.
  - Sketch: `{"shoulder", 's', 32, …}`.
  - Guide line 77: `GPIO32  shoulder (MG996R)`.
- Keep GPIO 0, 2, 5, 12, 15 (strapping) and 34–39 (input-only) out of the servo map.

### A7. Should fix: every boot sends the joints to compiled defaults at full speed, and the claw trim is lost

**Evidence**

- `arm_test.ino:75–81`: the boot pose is 90/90/90/90 with the claw at the compiled 20°, with no ramp.
- `arm_test.ino:112`: the `k` trim lives in RAM only. `BUILD_GUIDE.md:145` asks you to copy it into the sketch by hand.

**Effect**

- Any reset snaps the arm: power-up, a brown-out, or opening the port from the PC (A2).
- If the trim was never copied into the sketch, every boot overcloses the claw into a stall. `BUILD_GUIDE.md` §7 warns that a stall overheats the MG90S.

**Fix:** save the pose in NVS (non-volatile storage) after every move and on a stop, and restore it at boot. Tested in the shim:

- The pose and the trim come back after a simulated power cycle.
- A re-flash with the other `GRIP_OPEN_DIR` drops the old trim. This matters because NVS survives re-flashing.

```cpp
#include <Preferences.h>
Preferences prefs;
void savePose() {                       // call at the end of runMove() and when a move stops
  float p[7] = {joints[0].deg, joints[1].deg, joints[2].deg, joints[3].deg, clawMm, GRIP_CLOSED_DEG, (float)GRIP_OPEN_DIR};
  prefs.putBytes("pose", p, sizeof p);
}
// setup(), replacing line 75
prefs.begin("arm", false);
float p[7];
if (prefs.getBytes("pose", p, sizeof p) == sizeof p) {
  if ((int)p[6] == GRIP_OPEN_DIR && std::isfinite(p[5])) {        // other claw direction: drop the old trim
    GRIP_CLOSED_DEG = constrain(p[5], 0.0f, 180.0f);
    if (std::isfinite(p[4])) clawMm = constrain(p[4], 0.0f, GRIP_MAX_MM);
  }
  for (int i = 0; i < CLAW; i++)
    if (std::isfinite(p[i])) joints[i].deg = joints[i].target = constrain(p[i], (float)joints[i].lo, (float)joints[i].hi);
}
joints[CLAW].deg = joints[CLAW].target = clawDeg(clawMm);
```

Add to `BUILD_GUIDE.md` §5:

- Send `c` before switching off.
- Power the ESP32 (USB) before the 6 V supply.
- Optionally, put a 10 kΩ pull-down on each servo signal. The pins float until `attach()`.

### A8. Should fix: every servo is assumed to give 0–180° over 500–2500 µs

**Evidence:** `arm_test.ino:23–30`. The sources disagree on the travel:

- TowerPro's MG996R datasheet gives a rotation of "approximately 120 degrees (60 in each direction)".
- ESP32Servo's own Sweep example attaches at 1000–2000 µs and notes that different servos need different min/max settings.
- ProtoSupplies measured the MG90S at 180° ±15°, with the usable range often a little less.

**Effect**

- A servo whose internal stop lies inside 500–2500 µs stalls at the end of its travel, at 2.5 A for an MG996R at 6 V.
- Its degrees also won't match the joint degrees that the limits and A4 assume. The claw's 3.18°/mm scale assumes the same.

**Fix:** find each servo's end stops before fitting its horn.

1. Add a temporary `u <joint> <µs>` command that calls `servo.writeMicroseconds()`.
2. Step out from 1500 µs until the servo stops moving or buzzes, then back off 30 µs.
3. Put those values into `minUs`/`maxUs`. 0–180 then stays inside the real travel.
4. Check the claw scale at `g 40` with calipers.

### A9. Should fix: drop the optional 5 V buck

**Evidence:** `BUILD_GUIDE.md:41` and `:73` add a buck from the 6 V supply, "or power the ESP32 from USB". `BUILD_GUIDE.md:82` sends the ESP32's USB to the PC for commands anyway. The buck causes four problems:

- **LM2596:** TI specifies the LM2596-5.0 for 7 V ≤ VIN ≤ 40 V, with a typical switch saturation of 1.16 V at 3 A. It can't hold 5 V from a 6 V supply.
- **MP1584:** its datasheet asks for an external bootstrap diode above 65 % duty, and 6 V to 5 V is 83 %. It also asks for VIN − VOUT above 3 V at light load.
- **Two supplies at once:** Espressif's DevKitC guide says USB, the 5V pin and the 3V3 pin are mutually exclusive supplies, "otherwise the board and/or the power supply source can be damaged".
- **Back-feed:** a buck's high-side switch has a body diode from SW to VIN. With the buck fitted, USB plugged in and the 6 V adapter unplugged, the PC's USB port feeds the servo rail at about 4 V. A command then moves servos on USB power.

**Fix:** remove the buck from the arm.

- The ESP32 runs from USB, which is plugged into the PC for §6 anyway.
- For standalone use, plug a USB phone charger into the ESP32's USB port.

### A10. Should fix: no fuse, no switch, and a jack that accepts any adapter

**Evidence:** `BUILD_GUIDE.md:38–40` and §3. The only way to switch off is to unplug (`BUILD_GUIDE.md:184`).

- A 9 V or 12 V adapter with the same 5.5 × 2.1 plug destroys the MG90S, which is rated 4.8–6.0 V. A 12 V one also exceeds the 10 V capacitor's rating.
- A centre-negative adapter reverses the electrolytic capacitor and the servos.

**Fix**

- A 5 A fuse (blade or polyfuse) after the jack.
- A rocker switch on the 6 V line, within reach. It becomes the emergency stop.
- A "6 V, centre +" label at the jack.
- Check the plug with a meter before the first connection.
- Optionally, a 6.5 V TVS diode (e.g. SMBJ6.5A) across the rail after the fuse, so a wrong adapter blows the fuse instead of the servos.

### A11. Should fix: the PC protocol can lose sync with the arm and can hang

**Evidence:** `arm_pc_control.py:33–55` and `arm_test.ino:63`, `:94`.

- **Stale replies:** an `x` sent while nothing moves makes the sketch print `stopped`. The next `move()` reads that line as its own reply and returns `False` while the arm is still moving. Tested: the real `ok` is left unread, so every later reply is one behind.
- **No overall deadline:** `readline()` only times out after 30 s of silence. A board that keeps printing, such as a boot loop or brown-out messages, hangs `_cmd()` and `move()` forever.
- **`err` looks like `stopped`:** an `err …` reply is returned as `False`, the same as `stopped`.
- **Hidden `x`:** the sketch only sees `x` when it is the first byte waiting, so a `?` sent during a move hides a following `x`.

**Fix** (tested against a fake port that answers like the fixed sketch: banner or none, a stale `stopped`, `blocked: desk`, NaN):

```python
import math, time   # at the top of the file

class Arm:
    def __init__(self, port: str, baud: int = 115200):
        import serial
        self.s = serial.Serial()                 # configure first, open last
        self.s.port, self.s.baudrate, self.s.timeout = port, baud, 0.2
        self.s.dtr = False                       # keep the auto-reset lines inactive when the port opens
        self.s.rts = False                       # (prevents the reset on most OS/driver combinations, not all)
        self.s.open()
        self._read_until(lambda l: l.startswith("arm_test ready"), 3.0, required=False)   # only after a reset
        self.status()                            # proves arm_test answers on this port

    def _read_until(self, done, seconds, required=True):
        end = time.monotonic() + seconds         # overall deadline, even if the board keeps talking
        while time.monotonic() < end:
            line = self.s.readline().decode(errors="replace").strip()
            if line and done(line):
                return line
        if required:
            raise TimeoutError("no reply from the arm")

    def _send(self, text):
        self.s.reset_input_buffer()              # drop stale lines (banner, an old "stopped")
        self.s.write((text + "\n").encode())

    def status(self):
        self._send("?")
        return tuple(float(p) for p in self._read_until(lambda l: l.startswith("pos "), 2.0).split()[1:])

    def move(self, base, shoulder, elbow, wrist, claw_mm, seconds=10.0):
        q = (base, shoulder, elbow, wrist, claw_mm)
        if not all(math.isfinite(v) for v in q):
            raise ValueError(f"refusing a non-finite target {q}")
        self._send(f"m {base:.0f} {shoulder:.0f} {elbow:.0f} {wrist:.0f} {claw_mm:.1f}")
        reply = self._read_until(lambda l: l in ("ok", "stopped") or l.startswith(("err", "blocked")), seconds)
        if reply.startswith(("err", "blocked")):
            raise RuntimeError(reply)
        return reply == "ok"
```

In the sketch, reply `idle` instead of `stopped` (line 94) to an `x` that arrives when nothing is moving.

### A12. Should fix: camera capture settings

**Evidence:** `arm_pc_control.py:67–77`.

- **Bandwidth:** without a format request, OpenCV may negotiate uncompressed YUY2. That needs 1920 × 1080 × 2 bytes × 30 fps ≈ 1 Gbit/s, but USB 2.0 carries 480 Mbit/s. The thin, flexible cable the BOM suggests (`BUILD_GUIDE.md:56`) is often USB 2.0 only, which makes the preview slow or black. MJPG fits.
- **Backend:** some Windows capture backends pick a format on their own; an OBS forum thread shows the Brio defaulting to NV12 that way.
- **Wrong camera:** index 0 is often a laptop's built-in camera. The script only suggests `--camera 1` when index 0 fails to open, not when it opens the wrong camera.
- **Early frames:** one failed `read()` ends the preview (line 77), and the first frames often fail while the camera starts.

**Fix**

```python
api = cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY
cap = cv2.VideoCapture(camera, api)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))   # before the size
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FPS, 30)
# in the loop: skip up to ~30 failed reads in a row before giving up, and print the size actually obtained once
```

**Checked on OpenCV 5.0.0:**

- Every `cv2` name the script uses still exists, including `VideoWriter_fourcc`.
- The default `--rotate ccw` does put the raw image's right edge at the top, as §6 describes. Check it once against the real mount.

### Notes (arm)

**N-A1. Supply size and voltage**

- Worst case with every servo stalled: 3 × 2.5 A (MG996R at 6 V, TowerPro) + 2 × 0.7 A (MG90S, measured) ≈ 8.9 A.
- Holding the arm out with the Brio takes about 2 A. That is an estimate: the shoulder holds at 42–55 % of stall torque, and current scales roughly with torque.
- So 5 A is enough once A4 keeps the arm out of the desk. If the adapter does current-limit, the arm drops.
- The MG90S is rated 4.8–6.0 V, so a 6 V adapter is at its limit. Measure its unloaded voltage; it should be 6.2 V or less.

**N-A2. Claw reporting and holding**

- `?` reports the mm you asked for (`arm_test.ino:47`, `:69`), not the mm the servo reached after a clamp or an `x`. Example: with `GRIP_OPEN_DIR = -1` and the closed angle left at 20, `g 44` drives the servo to 0°, which is 6 mm, and reports 44.0. Report `clawMmFromDeg(joints[CLAW].deg)` instead.
- Holding an object with `g 0` stalls the MG90S continuously. Instead, command the object's width minus 2 mm.

**N-A3. Wiring details**

- Run the 6 V from the jack to the bus in 20–22 AWG wire, not jumper wire.
- GPIO13, 14, 25, 26 and 27 are ADC2 pins. That is fine for servo outputs, but any future analog input must use ADC1 (GPIO32–39) once Wi-Fi is on.

**Checked and fine**

- The claw conversion: an 18-tooth module-1 pinion gives 180/(π·18) = 3.183° per mm of gap, so 44 mm takes 140° (matches `claw_frame.py:52`).
- `allocateTimer(0)` and `allocateTimer(1)` are both needed: ESP32Servo puts up to 4 channels on a timer, and there are 5 servos.
- Elbow and wrist travel of ±90° sits inside the collision-free ±170° and ±150°.
- The cradle keeps the pin rows clear for jumper housings.

*Outside my slice, flagged in passing:* `jobs/20261025-robot-arm-assembly/README.md` still describes the superseded gripper and "8 printed parts".

---

## 2. Tracked rover

### R1. Should fix: no battery monitoring, and the 80 % cap gives 6.7 V on a full pack

**Evidence:** `rover_test.ino:4` and `:10` (`PWM_CAP = 204`), and `BUILD_GUIDE.md:72`.

- On a full pack, 0.8 × 8.4 V = 6.72 V average on 6 V motors. At the nominal 7.4 V it is 5.9 V.
- Nothing reads the pack, so the rover drives until the cells' protection trips. On the usual DW01-type protection that is about 2.4–2.5 V per cell, the very bottom of the cells' range.

**Fix:** wire a divider and let the firmware set the cap from the measured voltage.

- **Divider:** 100 kΩ from the switched pack + to GPIO34 (ADC1, input-only), 33 kΩ to GND, and 100 nF across the 33 kΩ. It turns 8.4 V into 2.08 V and draws about 60 µA, only while switched on.
- **Code** (tested in the shim: cap 182 at 8.4 V, stop at 6.37 V):

```cpp
const int VBAT_PIN = 34;
const float VBAT_DIV = (100.0f + 33.0f) / 33.0f, VBAT_STOP = 6.4f, MOTOR_V = 6.0f;
int pwmCap = 182;                       // replaces PWM_CAP in motor()
float vbat() { uint32_t mv = 0; for (int i = 0; i < 8; i++) mv += analogReadMilliVolts(VBAT_PIN); return mv / 8.0f * VBAT_DIV / 1000.0f; }
// loop(), once a second:
float v = vbat();
pwmCap = constrain((int)(255 * MOTOR_V / v), 0, 255);   // average motor voltage <= 6 V whatever the charge
if (v < VBAT_STOP) { go(0, 0); autonomous = false; Serial.printf("battery %.2f V: stopped, charge the pack\n", v); }
```

### R2. Should fix: `+` and `-` don't change the speed until the next direction command

**Evidence:** `rover_test.ino:56–57` only change `speedPct`.

**Test:** `f`, then `-` six times: the PWM stays at 204 (80 %). So pressing `-` to slow down before an edge does nothing.

**Fix**

```cpp
int dirL = 0, dirR = 0;
void go(int l, int r) { dirL = l; dirR = r; drive(l, r); }      // use go() for f, b, l, r and s
case '+': speedPct = min(100, speedPct + 10); drive(dirL, dirR); break;
case '-': speedPct = max(30, speedPct - 10); drive(dirL, dirR); break;
```

### R3. Should fix: a missing echo reads as "clear", and the sensor can't see a table edge

**Evidence:** `rover_test.ino:33–34`.

- The module's manual says that with no obstacle the echo pulse lasts 38 ms. That is longer than the 25 ms `pulseIn` timeout, so `pulseIn` returns 0, which the sketch turns into 999 cm.
- A broken or unplugged ECHO wire also gives 0, so also 999 (the 2 kΩ pulls the line low).
- Autonomous mode then drives on blind.
- The HC-SR04 only looks forward, and the rover is rated for a 5 cm drop (`BUILD_GUIDE.md:3`).

**Fix:** tell the two cases apart, stop on a fault, and write "floor only" next to `a` in §4. Tested in the shim: the no-echo pulse gives 999, a missing pulse gives −1, a 10 cm target gives 10.

```cpp
// cm; 999 = nothing in range (the ~38 ms no-echo pulse); -1 = no echo pulse at all (wiring or sensor fault)
long distanceCm() {
  unsigned long t = micros();
  while (digitalRead(ECHO) == HIGH) if (micros() - t > 60000) return -1;   // the last echo never ended
  digitalWrite(TRIG, LOW); delayMicroseconds(2);
  digitalWrite(TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  t = micros();
  while (digitalRead(ECHO) == LOW) if (micros() - t > 5000) return -1;    // the echo line never rose
  unsigned long t1 = micros();
  while (digitalRead(ECHO) == HIGH) if (micros() - t1 > 40000) break;
  unsigned long us = micros() - t1;
  return us >= 30000 ? 999 : (long)(us / 58);
}
// autonomous: if (d < 0) { go(0, 0); autonomous = false; Serial.println("HC-SR04: no echo pulse, stopped"); }
```

### R4. Should fix: USB and the buck feed the ESP32 at the same time during the first drive

**Evidence:** `BUILD_GUIDE.md:44` (buck to the ESP32's 5V pin) and `:72` ("switch on, open the Serial Monitor").

- Espressif's rule of one supply at a time applies (see A9).
- With the main switch off and USB plugged in, USB feeds back through the MP1584's body diode into the switched battery net, which is the TB6612's VM. Typing `f` then runs the motors from the PC's USB port.

**Fix:** either of these.

- A Schottky diode (SS14 or 1N5817) from the buck's OUT+ to the ESP32's 5V pin, with the buck set to 5.3 V so about 5.0 V reaches the board.
- A data-only (VBUS-blocking) USB adapter whenever the pack is connected.

### Notes (rover)

**N-R1. Hard reversals.** The avoid manoeuvre goes from full forward straight to full reverse (`rover_test.ino:67–68`). At that moment the motor's back-EMF adds to the supply, roughly doubling the current, and the N20 gears and printed sprockets take the jolt. Put `drive(0, 0); delay(80);` before each reversal.

**N-R2. Decoupling**

- The 100 µF capacitor (`BUILD_GUIDE.md:31`) needs a voltage rating: 16 V or more on an 8.4 V pack.
- Solder 100 nF ceramic capacitors across each N20's terminals. The brushed motors are the noisiest part on the board, right next to the HC-SR04 and the ESP32.

**N-R3. Breadboard.** The 170-point breadboard (`BUILD_GUIDE.md:25`) carries motor current through spring contacts on a chassis that vibrates, so expect intermittent resets. Solder the TB6612 carrier to a strip of perfboard, or plug it into female headers.

**N-R4. PWM**

- `analogWrite` runs at about 1 kHz in arduino-esp32 by default, which you can hear from the N20s. 20 kHz is quieter and well inside the TB6612's 100 kHz maximum. On core 3.x: `analogWriteFrequency(PWMA, 20000)` and the same for PWMB.
- At `speedPct` 20 the duty is 16 %, about 1.2–1.3 V average. The motors probably won't start, so make 30 % the minimum.

**N-R5. HC-SR04 trigger at 3.3 V.** The module is a 5 V part. Most trigger from 3.3 V, but not all. If `d` reads 999 facing a wall, fit an HC-SR04P or RCWL-1601: they run at 3.3 V and need no divider.

**N-R6. Protection**

- Protected cells cut off a short. A bare 2S BMS does too; check its current limit.
- A cell put in backwards reverses the pack onto the TB6612 and the MP1584. Check polarity with a meter before the first switch-on.
- `assembly_plan.md:14` says "mini rocker switch" but the BOM says MTS-102 toggle. Pick one; both are fine at about 2 A.

**Checked and fine**

- TB6612 ratings vs the N20: VM 2.5–13.5 V and 1.2 A average (3.2 A peak) per channel, against an N20 stall of about 0.6 A at 6 V (about 0.85 A at 8.4 V).
- VCC from the 3V3 pin.
- Boot is safe: the TB6612's internal 200 kΩ pull-downs on STBY, IN and PWM keep the motors off while the ESP32 boots, so GPIO14's boot activity on PWMB is harmless here.
- The 1k/2k divider gives 3.33 V on ECHO.
- No strapping or input-only pins are used as outputs.

---

## 3. Hexapod

### H1. Should fix: the PCA9685 clock is hard-coded at 27 MHz, so pulses are 8 % long on a 25 MHz chip

**Evidence:** `hexapod_test.ino:56`.

- NXP's datasheet gives a typical 25 MHz with no tolerance.
- Adafruit's example puts in 27 MHz, but says the real value is "about 23–27 MHz" per chip and should be calibrated.
- The library's `writeMicroseconds` converts using the assumed clock.

**Test, with the library's arithmetic (prescale 131):**

| Real clock | Centre (1500 µs asked) | "180°" (2500 µs asked) | Frame rate |
|---|---|---|---|
| 27 MHz | 1496 µs | 2498 µs | 49.9 Hz |
| 25 MHz | 1616 µs | 2698 µs, past the MG90S end stop | 46.2 Hz |
| 23 MHz | 1756 µs | 2933 µs | 42.5 Hz |

The two boards differ from each other, so the left and right legs centre differently.

**Fix:** measure each board once with the ESP32 itself.

1. Jumper the board's channel-15 signal pin to GPIO34.
2. Type `o`.
3. Copy the printed value into `OSC_L` or `OSC_R`.

```cpp
uint32_t OSC_L = 25000000, OSC_R = 25000000;     // replace with the values 'o' prints
void calibrateOsc(Adafruit_PWMServoDriver &pca, const char *name) {
  pca.setPWM(15, 0, 2048);                       // 50 % square wave at the frame rate
  delay(100);
  unsigned long hi = pulseIn(34, HIGH, 50000), lo = pulseIn(34, LOW, 50000);
  pca.setPWM(15, 0, 0);
  if (!hi || !lo) { Serial.printf("%s: no signal on GPIO34\n", name); return; }
  double osc = 4096.0 * (pca.readPrescale() + 1) * 1e6 / (double)(hi + lo);
  Serial.printf("%s: frame %lu us -> OSC_%s = %.0f\n", name, hi + lo, name, osc);
}
// setup(), per board: pca.setOscillatorFrequency(OSC_x); pca.setPWMFreq(50);
```

### H2. Should fix: the gait loop never reaches p = 1.0

**Evidence:** `hexapod_test.ino:43`: `for (float p = 0; p <= 1.0; p += 0.1)`.

- Ten float additions of 0.1 give 1.0000001, so the loop runs 10 times and stops at p = 0.9.
- At that point the lifted legs end at coxa 12° (not 15°), with the femur still 7.7° up.
- The next phase then starts them at 15° and 0°: a 3° coxa snap and a 7.7° femur drop every half-cycle.

**Fix:** `for (int k = 0; k <= 10; k++) { float p = k / 10.0f; … }`

### H3. Should fix: all 18 servos start moving at the same instant

**Evidence:** `hexapod_test.ino:59` calls `stand()` straight after setup, which writes all 18 channels in one burst.

- The PCA9685's outputs are low from power-on (datasheet), so every servo is limp until that moment and then moves at full speed.
- 18 MG90S starting together draw several amps (about 0.7 A each at stall, as measured by ProtoSupplies) from a 5 A UBEC.

**Fix** (tested; start-up then takes 0.9 s):

```cpp
void stand(bool stagger = false) { for (int l = 0; l < 6; l++) { setLeg(l, 0, 0, 0); if (stagger) delay(150); } }
// setup(): stand(true);
```

### H4. Should fix: the LiPo has no protection: no cut-off, no fuse and no rated switch

**Evidence**

- `BUILD_GUIDE.md:24` lists a bare 2S LiPo.
- `BUILD_GUIDE.md:27` lists a "toggle or rocker switch" with no rating.
- §2 has no fuse, and the sketch reads no voltage.

**Why it matters**

- A LiPo has no protection circuit. Left switched on, the UBEC, MP1584 and ESP32 keep drawing after the servos weaken, and the pack goes far below 3.0 V per cell. After that it must not be charged.
- A short anywhere in the hand wiring can draw tens of amps.

**Fix**

- Plug a LiPo voltage alarm (buzzer) into the balance lead. No code needed; about €2.
- Fit a 7.5 A blade fuse in the battery lead, before the switch.
- Use a switch rated for at least 10 A DC.
- Add a divider to GPIO35 (100 kΩ / 33 kΩ + 100 nF, as in R1) and stop walking below 6.6 V, which is 3.3 V per cell under load:

```cpp
uint32_t mv = 0; for (int i = 0; i < 8; i++) mv += analogReadMilliVolts(35);
float v = mv / 8.0f * (133.0f / 33.0f) / 1000.0f;
if (v < 6.6f) { walking = false; Serial.printf("LiPo %.2f V: stopped, switch off and charge\n", v); }
```

### H5. Should fix: the `t` command can trim the wrong servo without saying so

**Evidence:** `hexapod_test.ino:71–72`.

**Test**

- `t5 3` trims channel 0 by 3.
- `t  7 2` (two spaces) trims channel 0 by 7.
- `t abc 9` trims channel 0 by 9.

You would then copy the wrong trims into `TRIM[]` (`BUILD_GUIDE.md:72`).

**Fix** (tested: all three cases now land on the right channel or are refused):

```cpp
int ch, d;
if (sscanf(line.c_str() + 1, "%d %d", &ch, &d) == 2 && ch >= 0 && ch < 18 && abs(TRIM[ch] + d) <= 20) {
  TRIM[ch] += d; writeServo(ch, 0);
} else Serial.println("usage: t <channel 0-17> <deg>, total trim within +-20");
```

### H6. Should fix: USB and the buck feed the ESP32 at the same time, as in R4

**Evidence:** `BUILD_GUIDE.md:39` and §4: power up, then use the Serial Monitor. The fix is the same as R4. Here the back-feed path reaches the UBEC's input.

### Notes (hexapod)

**N-H1. I²C load**

- The library's `writeMicroseconds` reads the prescale register over I²C on every call, so each 25 ms gait frame makes 36 transactions.
- At the ESP32's default 100 kHz that is about 19 ms of bus time (an estimate from the byte counts). Frames stretch to about 44 ms, and the 18 servos are updated across most of each frame instead of together.
- Fix:
  1. Call `Wire.setClock(400000)`.
  2. In setup, compute `ticksPerUs = osc / (1e6 × (prescale + 1))` once.
  3. Call `setPWM(ch, 0, lroundf(us * ticksPerUs))` instead of `writeMicroseconds`.

  Tested: 18 writes per frame and no reads.

**N-H2. Missing board.** `begin()` returns false when a board doesn't answer, but line 55 ignores it. If the A0 jumper is missing, both boards sit at 0x40, and the right legs get the left legs' commands.

```cpp
if (!pcaR.begin()) { Serial.println("PCA9685 0x41 not found: check the A0 jumper"); while (true) delay(1000); }
```

**N-H3. Femur and tibia limits.** Only the coxa is clamped (line 31).

- The check found the femur clear from −70° to +90°.
- It found the tibia clear from −170° to 0° in its own frame. That is −80° to +90° in the sketch's frame, where 0 is straight down (`jobs/20261026-hexapod-assembly/assembly_check.py:70–71`).
- Clamp `femur` to −70…90 and `tibia` to −80…90 in `setLeg()` before the gait code grows.

**N-H4. Servo rail**

- A 5 A UBEC covers the test gait: about 3 femurs holding at roughly 0.3 A each, plus 9 servos moving. It doesn't cover the start-up surge (H3) or stalls. 8–10 A gives margin.
- Feed each board through its terminal block, not through the 6-pin header.
- Adafruit's rule of thumb is n × 100 µF per board, which means about 1000 µF on each board, using the footprint provided. One 1000 µF for all 18 servos is thin.
- Adafruit warns that connecting VCC to V+ can damage the board. Leave the header's V+ pin unconnected on the ESP32 side.
- The UBEC's 6.0 V is the MG90S's maximum rating. 5 V is gentler on the servos if you can spare about 20 % of the torque.

**N-H5. Stop latency.** The sketch only reads `x` between whole gait cycles (two `step()` calls, about 0.5–0.9 s). `stand()` then snaps the legs from mid-stride. Check for `x` inside `step()`.

**N-H6. Ground and I²C.** The servo return current can split between the UBEC lead and the I²C header's GND, which runs through the ESP32. Keep the UBEC's ground leads short and thick to the boards' terminal blocks, and twist SDA and SCL each with a ground wire.

**N-H7. ESP32 reset while the boards stay powered.** `begin()` sets 1 kHz (the library default) before the sketch sets 50 Hz. For a few milliseconds the old duty counts come out as about 75 µs pulses at 1 kHz. Most servos ignore this. If a twitch shows each time the Serial Monitor opens, hold OE high during setup.

**Checked and fine**

- The channel map in `BUILD_GUIDE.md` §2 matches `writeServo()`.
- The tripods {LF, LR, RM} and {LM, RF, RR} are right.
- A ±30° coxa keeps neighbouring legs within the 70° the check allows.
- PCA9685 logic at 3.3 V puts the I²C pull-ups at 3.3 V, which is safe for the ESP32, and gives 3.3 V servo pulses.
- GPIO21/22 are the default I²C pins.

---

## 4. Cross-cutting

- **No sketch reads its supply.** When you add a battery input, use an ADC1 pin (GPIO32–39). ADC2 stops working once Wi-Fi is on.
- **All three guides share one power gap:** the ESP32 can be fed from a buck while it is also plugged into USB. Use one supply at a time (Espressif), or isolate them with a diode or a VBUS blocker (A9, R4, H6).
- **Library notes for the guides:**
  - Use ESP32Servo 3.x with the arduino-esp32 3.x core.
  - "Adafruit PWM Servo Driver" pulls in Adafruit BusIO; accept the dependency prompt.
  - The rover's `analogWrite` needs core 2.x or later.
- **Pin maps:** no strapping pins (0, 2, 5, 12, 15) and no input-only pins (34–39) are used as outputs. The arm's GPIO14 is the one boot-activity pin that matters (A6).

## Sources

- Espressif, [ESP32-DevKitC V4 user guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html): the three power options are mutually exclusive.
- Espressif esptool, [Boot mode selection](https://docs.espressif.com/projects/esptool/en/latest/esp32/advanced-topics/boot-mode-selection.html): DTR/RTS drive EN and GPIO0; some OS/drivers assert them when a port opens; strapping pins.
- Random Nerd Tutorials, [ESP32 pinout reference](https://randomnerdtutorials.com/esp32-pinout-reference-gpios/): GPIO14 outputs a PWM signal at boot; input-only pins; ADC2 and Wi-Fi.
- esp32.co.uk, [DevKitC V4 pinout and safe GPIOs](https://esp32.co.uk/esp32-devkitc-v4-pinout-diagram-safe-gpios/): strapping pins 0, 2, 5, 12 and 15; ADC2 shared with Wi-Fi.
- Espressif arduino-esp32, [LEDC API](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/ledc.html): `analogWriteFrequency(pin, freq)` on core 3.x.
- TowerPro, [MG996R datasheet](https://people.ece.cornell.edu/land/courses/ece4760/FinalProjects/f2017/kmv48_rp625/kmv48_rp625/kmv48_rp625/MG996RTowerPro.pdf): 4.8–7.2 V, 2.5 A stall at 6 V, about 120° rotation.
- ProtoSupplies, [MG90S](https://protosupplies.com/product/servo-motor-micro-mg90s/): 4.8–6 V, 700 mA stall (measured), 180° ±15°.
- ESP32Servo, [Sweep example](https://github.com/madhephaestus/ESP32Servo/blob/master/examples/Sweep/Sweep.ino) and [README mirror](https://gitee.com/xwillin/ESP32Servo): 1000–2000 µs default in the example, "different servos may require different min/max settings", values below 500 treated as degrees.
- NXP, [PCA9685 datasheet](https://nxp.com/docs/en/data-sheet/PCA9685.pdf): 25 MHz typical oscillator, prescale formula, outputs low at power-on, VDD 2.3–5.5 V, OE.
- Adafruit, [PCA9685 16-channel servo driver guide](https://learn.adafruit.com/16-channel-pwm-servo-driver.md?view=all): V+ vs VCC warning, n × 100 µF, OE pulled low, 10 kΩ I²C pull-ups to VCC.
- Adafruit, [PWM Servo Driver library source](https://github.com/adafruit/Adafruit-PWM-Servo-Driver-Library/blob/master/Adafruit_PWMServoDriver.cpp) and [servo example](https://github.com/adafruit/Adafruit-PWM-Servo-Driver-Library/blob/master/examples/servo/servo.ino): `begin()` sets 1 kHz; `writeMicroseconds()` reads the prescale every call; the oscillator is "about 23–27 MHz", calibrate it.
- Toshiba, [TB6612FNG datasheet](https://cdn-shop.adafruit.com/datasheets/TB6612FNG_datasheet_en_20121101.pdf): VM 2.5–13.5 V, 1.2 A average and 3.2 A peak, 200 kΩ internal pull-downs, 100 kHz PWM maximum.
- [HC-SR04 user manual](https://iarduino.ru/lib/HC-SR04.pdf): 5 V supply; a 38 ms echo pulse when nothing is detected; measurement cycle of at least 50 ms.
- TI, [LM2596 datasheet](https://hippo.fel.cvut.cz/katalog/pdf/2596.pdf): the 5.0 V version is specified from 7 V input; switch saturation 1.16 V typical.
- MPS, [MP1584 datasheet](https://www.monolithicpower.com/pub/media/document/MP1584_r1.1.pdf): 4.5–28 V input; external bootstrap diode above 65 % duty; VIN − VOUT above 3 V at light load.
- [pySerial API](https://pyserial.readthedocs.io/en/stable/pyserial_api.html) and [pyserial issue #729](https://github.com/pyserial/pyserial/issues/729): DTR/RTS set before `open()` are applied at open; a short glitch is still possible on POSIX.
- OBS forum, [Logitech Brio formats](https://obsproject.com/forum/threads/support-for-logitech-brio-4k-webcam.63104/post-273298): format and backend negotiation (NV12, YUY2, MJPEG) with the Brio.

// Desktop robot arm (claw v2): servo test, claw fitting and PC control for an ESP32 DevKit.
// Board: "ESP32 Dev Module" on the arduino-esp32 3.x core. Library: ESP32Servo 3.x (Library Manager).
// Serial Monitor at 115200, line ending "Newline".
//
// Commands for you:
//   c                 centre base/shoulder/elbow/wrist (90°) and close the claw: do this before fitting horns
//   f                 claw servo to its CLOSED angle: fit the pinion and slide the jaws in at this position
//   b|s|e|w <deg>     move base / shoulder / elbow / wrist to <deg> (0-180, clamped to its limits)
//   g <mm>            claw opening 0-44 mm (0 = closed)
//   k <deg>           trim the claw's closed angle (e.g. k 23) until the jaws just touch at g 0.
//                     The trim is saved on the ESP32: it survives power-off and re-flashing
//   u <j> <us>        servo end-stop test, before the horns go on: joint j (b s e w g) to a pulse of
//                     <us> (500-2500 µs), moved slowly like any other move (BUILD_GUIDE §4 step 1)
//   p                 print the current angles (moves nothing)
// Commands for a PC program (e.g. vision with the Brio, see arm_pc_control.py):
//   m <b> <s> <e> <w> <mm>   move all joints together. One reply when it ends: "ok" (every joint arrived),
//                     "stopped" (x), "blocked: desk" (the desk guard stopped it) or "err ..." (refused)
//   ?                 replies "pos <b> <s> <e> <w> <mm>", also during a move
//   x                 stop the current move where it is; it does not resume. Replies "idle" if nothing moves
// Joints move at most 1° per STEP_MS, so a wrong direction is easy to stop: send x or switch the 6 V off.
// Before every step the desk guard checks that the claw and the camera stay clear of the desk: set
// EL_SIGN, WR_SIGN and CAMERA_FITTED below once the arm is assembled (BUILD_GUIDE §5).
// The pose and the claw trim are saved in flash (NVS) after every move. After a reset (power-up, or the PC
// opening the port) the servos start where they stopped instead of jumping to 90°.

#include <ESP32Servo.h>
#include <Preferences.h>
#include <cmath>

struct Joint { const char *name; char key; int pin; int minUs; int maxUs; int lo; int hi; float deg; float target; Servo servo; };
enum MoveResult { ARRIVED, STOPPED, BLOCKED };

// Signal pins: no strapping pin (0, 2, 5, 12, 15), no input-only pin (34-39) and none that puts out a
// signal at boot. GPIO14 does, so the shoulder, which carries the whole arm, is on GPIO32.
// minUs/maxUs: the pulses for 0° and 180°. If u shows a servo reaching its end stop before 500 or 2500 µs,
// put the stop here, backed off by 30 µs (BUILD_GUIDE §4 step 1).
Joint joints[] = {
  {"base",     'b', 13, 500, 2500, 0, 180, 90, 90, Servo()},
  {"shoulder", 's', 32, 500, 2500, 0, 180, 90, 90, Servo()},
  {"elbow",    'e', 27, 500, 2500, 0, 180, 90, 90, Servo()},  // 90 = straight; clear of the arm itself to ±170° (assembly check)
  {"wrist",    'w', 26, 500, 2500, 0, 180, 90, 90, Servo()},  // 90 = straight; clear of the arm itself to ±150°
  {"claw",     'g', 25, 500, 2500, 0, 180, 20, 20, Servo()},  // MG90S; angle set from mm below
};
const int N = sizeof(joints) / sizeof(joints[0]);
const int CLAW = 4;

// Claw: rack and pinion, pitch radius 9 mm -> 3.18° of servo per mm of jaw gap, 0-44 mm in 140°.
const float DEG_PER_MM = 3.183;
const float GRIP_MAX_MM = 44.0;
int GRIP_OPEN_DIR = +1;          // +1: a bigger angle opens the claw. If "g 5" squeezes instead of opening, set -1
float GRIP_CLOSED_DEG = 20.0;    // with GRIP_OPEN_DIR -1 use about 160. k trims it at run time and saves the trim
const int STEP_MS = 15;
float clawMm = 0.0;              // the claw opening the servo has reached, mm

// Desk guard (review A4): a side view of the arm, checked before every 1° step. Angles as in assembly_check:
// shoulder 0 = upper link horizontal, + up; elbow and wrist 0 = straight, + up. The desk is level, so it
// doesn't matter which side "s 0" points to, only which way the elbow and wrist turn compared with the
// shoulder. Find out once after assembly, with small moves (BUILD_GUIDE §5): c, then s 60 (the arm leans
// towards the "s 0" side), then
const int EL_SIGN = +1;            // e 100: +1 if the forearm's end rises, -1 if it drops (then e 90)
const int WR_SIGN = +1;            // w 100: +1 if the fingertips rise, -1 if they drop (then w 90 and c)
const bool CAMERA_FITTED = true;   // false without the Brio: the wrist may then come closer to the desk
const float DESK_Z = -40.0f;       // desk top, relative to the base top plate (shoulder axis at +60.5)
const float RAD = 0.017453293f;

// Height (mm) of the arm's lowest point above where the guard lets it go; < 0 is too close to the desk.
// Checked against the assembly check's meshes (review A4): it let none of 494 desk hits through.
float deskMargin(float s, float e, float w, float gapMm) {
  float a1 = s * RAD, a2 = a1 + EL_SIGN * (e - 90.0f) * RAD, a3 = a2 + WR_SIGN * (w - 90.0f) * RAD;
  float ez = 60.5f + 100.0f * sinf(a1);                    // elbow axis
  float wz = ez + 90.0f * sinf(a2);                        // wrist axis
  float tz = wz + 73.0f * sinf(a3);                        // between the fingertips
  float mz = wz + 40.0f * sinf(a3);                        // middle of the claw
  float side = (gapMm / 2.0f + 12.0f) * fabsf(cosf(a3));   // the jaws stick out either side of the claw axis
  float m = min(ez - (DESK_Z + 25.0f), wz - (DESK_Z + (CAMERA_FITTED ? 62.0f : 25.0f)));
  return min(m, min(tz, mz) - (DESK_Z + 8.0f + side));
}

float clawDeg(float mm) { return GRIP_CLOSED_DEG + GRIP_OPEN_DIR * DEG_PER_MM * constrain(mm, 0.0f, GRIP_MAX_MM); }
float clawMmFromDeg(float d) { return constrain(GRIP_OPEN_DIR * (d - GRIP_CLOSED_DEG) / DEG_PER_MM + 0.0f, 0.0f, GRIP_MAX_MM); }   // + 0: no "-0.0"

int pulseUs(int i, float deg) { return joints[i].minUs + (int)lroundf((joints[i].maxUs - joints[i].minUs) * deg / 180.0f); }
void writeJoint(int i, float deg) { joints[i].deg = deg; joints[i].servo.writeMicroseconds(pulseUs(i, deg)); }

// Saved pose (NVS): b s e w, claw mm, closed angle, claw direction, and the closed angle compiled into this
// sketch. A re-flash that changes GRIP_OPEN_DIR or GRIP_CLOSED_DEG starts the claw closed at the new value.
Preferences prefs;
const int NSAVE = 8;
float saved[NSAVE];              // what is in NVS now, so an unchanged pose isn't written again
float closedCompiled;

void savePose() {
  float p[NSAVE] = {joints[0].deg, joints[1].deg, joints[2].deg, joints[3].deg, clawMm,
                    GRIP_CLOSED_DEG, (float)GRIP_OPEN_DIR, closedCompiled};
  if (memcmp(p, saved, sizeof p) == 0) return;
  prefs.putBytes("pose", p, sizeof p);
  memcpy(saved, p, sizeof p);
}

void restorePose() {
  closedCompiled = GRIP_CLOSED_DEG;
  prefs.begin("arm", false);
  float p[NSAVE];
  if (prefs.getBytes("pose", p, sizeof p) != sizeof p) return;     // first boot: 90° and the claw closed
  for (int i = 0; i < NSAVE; i++) if (!std::isfinite(p[i])) return;
  for (int i = 0; i < CLAW; i++) joints[i].deg = joints[i].target = constrain(p[i], (float)joints[i].lo, (float)joints[i].hi);
  if ((int)p[6] == GRIP_OPEN_DIR && p[7] == closedCompiled) {     // same claw set-up: keep the trim and the opening
    GRIP_CLOSED_DEG = constrain(p[5], 0.0f, 180.0f);
    clawMm = constrain(p[4], 0.0f, GRIP_MAX_MM);
  }
  memcpy(saved, p, sizeof p);
}

void printPos(const char *prefix) {
  Serial.print(prefix);
  for (int i = 0; i < CLAW; i++) { Serial.printf(" %.0f", joints[i].deg); }
  Serial.printf(" %.1f\n", clawMmFromDeg(joints[CLAW].deg));   // the opening reached, after any clamp or stop
}

String queued;                   // a command that arrived during a move: it runs when the move ends

// Called before every step: x stops the move (and drops a command waiting behind it), ? answers at once,
// anything else waits for the move to end. Returns true on x.
bool stopRequested() {
  while (Serial.available()) {
    String l = Serial.readStringUntil('\n');
    l.trim();
    if (l.length() == 0) continue;
    if (l.charAt(0) == 'x') { queued = ""; return true; }
    if (l.charAt(0) == '?') { printPos("pos"); continue; }
    if (queued.length() == 0) queued = l;
    else Serial.println("err busy: one command can wait, x stops");
  }
  return false;
}

// Move every joint towards its target, all arriving together, at most 1° per STEP_MS. Every step is checked
// against the desk before it is written. A stop (x or the guard) is final: the targets become where the
// joints are, so nothing later resumes the old move. The pose is saved at the end.
MoveResult runMove() {
  float start[N], maxd = 0;
  for (int i = 0; i < N; i++) { start[i] = joints[i].deg; maxd = max(maxd, fabsf(joints[i].target - start[i])); }
  int steps = (int)ceilf(maxd);
  float margin = deskMargin(start[1], start[2], start[3], clawMmFromDeg(start[CLAW]));
  MoveResult r = ARRIVED;
  for (int k = 1; k <= steps && r == ARRIVED; k++) {
    float nxt[N];
    for (int i = 0; i < N; i++) nxt[i] = start[i] + (joints[i].target - start[i]) * k / steps;
    float m = deskMargin(nxt[1], nxt[2], nxt[3], clawMmFromDeg(nxt[CLAW]));
    if (stopRequested()) r = STOPPED;
    else if (m < 0 && m < margin) r = BLOCKED;   // too close to the desk (or, from a pose already too close, closer)
    else {
      for (int i = 0; i < N; i++) writeJoint(i, nxt[i]);
      margin = m;
      delay(STEP_MS);
    }
  }
  for (int i = 0; i < N; i++) joints[i].target = joints[i].deg;
  clawMm = clawMmFromDeg(joints[CLAW].deg);
  savePose();
  return r;
}

void setJoint(int i, float deg) { joints[i].target = constrain(deg, (float)joints[i].lo, (float)joints[i].hi); }
void setClaw(float mm) { setJoint(CLAW, clawDeg(mm)); }

// Strict numbers: "s", "s abc" and "s nan" are refused instead of becoming 0 or NaN.
bool parseNum(const String &s, float &v) {
  const char *c = s.c_str();
  char *end;
  v = strtof(c, &end);
  return end != c && *end == '\0' && std::isfinite(v);
}

void setup() {
  Serial.begin(115200);
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  restorePose();                            // where the arm stopped (90° and the claw closed on the first boot)
  setClaw(clawMm);
  joints[CLAW].deg = joints[CLAW].target;
  clawMm = clawMmFromDeg(joints[CLAW].deg);
  for (int i = 0; i < N; i++) {
    joints[i].servo.setPeriodHertz(50);
    joints[i].servo.attach(joints[i].pin, joints[i].minUs, joints[i].maxUs);
    writeJoint(i, joints[i].deg);
    delay(300);                             // stagger start-up current
  }
  Serial.println("arm_test ready: c | f | b/s/e/w <deg> | g <mm> | k <deg> | u <j> <us> | p | m b s e w mm | ? | x");
  printPos("start b s e w | claw mm:");
}

void loop() {
  String line;
  if (queued.length()) { line = queued; queued = ""; }
  else if (Serial.available()) line = Serial.readStringUntil('\n');
  else return;
  line.trim();
  if (line.length() == 0) return;
  char cmd = line.charAt(0);
  String args = line.substring(1);
  args.trim();
  if (cmd == '?') { printPos("pos"); return; }
  if (cmd == 'x') { Serial.println("idle"); return; }                    // nothing is moving
  if (cmd == 'p') { printPos("angles b s e w | claw mm:"); return; }   // prints only, never moves
  if (cmd == 'm') {                                                      // m b s e w mm
    float v[5];
    if (sscanf(args.c_str(), "%f %f %f %f %f", &v[0], &v[1], &v[2], &v[3], &v[4]) != 5) { Serial.println("err need: m b s e w mm"); return; }
    for (int i = 0; i < 5; i++) if (!std::isfinite(v[i])) { Serial.println("err not a number"); return; }
    for (int i = 0; i < CLAW; i++) setJoint(i, v[i]);
    setClaw(v[4]);
    MoveResult r = runMove();
    Serial.println(r == ARRIVED ? "ok" : r == STOPPED ? "stopped" : "blocked: desk");
    return;
  }
  float val = 0;
  if (cmd && strchr("bsewgk", cmd) && !parseNum(args, val)) { Serial.println("err need a number, e.g. s 100"); return; }
  int uj = -1;
  if (cmd == 'c') {
    for (int i = 0; i < CLAW; i++) setJoint(i, 90);
    setClaw(0);
  } else if (cmd == 'f') {
    setClaw(0);
  } else if (cmd == 'g') {
    setClaw(val);
  } else if (cmd == 'k') {
    GRIP_CLOSED_DEG = constrain(val, 0.0f, 180.0f);
    setClaw(clawMm);
    Serial.printf("GRIP_CLOSED_DEG = %.1f (saved on the ESP32)\n", GRIP_CLOSED_DEG);
  } else if (cmd == 'u') {                                               // u <joint> <us>
    for (int i = 0; i < N; i++) if (joints[i].key == args.charAt(0)) uj = i;
    String us = args.substring(1);
    us.trim();
    if (uj < 0 || !parseNum(us, val)) { Serial.println("err need: u <b|s|e|w|g> <us>, e.g. u s 1500"); return; }
    val = constrain(val, (float)joints[uj].minUs, (float)joints[uj].maxUs);
    setJoint(uj, (val - joints[uj].minUs) * 180.0f / (joints[uj].maxUs - joints[uj].minUs));
  } else {
    bool found = false;
    for (int i = 0; i < CLAW; i++) if (joints[i].key == cmd) { setJoint(i, val); found = true; }
    if (!found) { Serial.println("unknown command"); return; }
  }
  MoveResult r = runMove();
  if (r != ARRIVED) Serial.println(r == STOPPED ? "stopped" : "blocked: desk");
  if (uj >= 0) Serial.printf("%s at %d us (%.1f deg)\n", joints[uj].name, pulseUs(uj, joints[uj].deg), joints[uj].deg);
  printPos("angles b s e w | claw mm:");
}

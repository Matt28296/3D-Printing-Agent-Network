// Desktop robot arm (claw v2): servo test, claw fitting and PC control for an ESP32 DevKit.
// Board: "ESP32 Dev Module". Library: ESP32Servo (Library Manager).
// Serial Monitor at 115200, line ending "Newline".
//
// Commands for you:
//   c                 centre base/shoulder/elbow/wrist (90°) and close the claw: do this before fitting horns
//   f                 claw servo to its CLOSED angle: fit the pinion and slide the jaws in at this position
//   b|s|e|w <deg>     move base / shoulder / elbow / wrist to <deg> (0-180, clamped to its limits)
//   g <mm>            claw opening 0-44 mm (0 = closed)
//   k <deg>           trim the claw's closed angle (e.g. k 23) until the jaws just touch at g 0;
//                     then copy the printed value into GRIP_CLOSED_DEG below
//   p                 print current angles
// Commands for a PC program (e.g. vision with the Brio, see arm_pc_control.py):
//   m <b> <s> <e> <w> <mm>   move all joints together; replies "ok" when every joint has arrived
//   ?                 replies "pos <b> <s> <e> <w> <mm>"
//   x                 stop the current move where it is
// Joints move at most 1° per STEP_MS, so a wrong direction is easy to stop: send x or unplug the 6 V supply.

#include <ESP32Servo.h>

struct Joint { const char *name; char key; int pin; int minUs; int maxUs; int lo; int hi; float deg; float target; Servo servo; };

// GPIO13/14/27/26/25 are not boot-strapping pins. MG996R and MG90S: ~500-2500 µs for 0-180°.
Joint joints[] = {
  {"base",     'b', 13, 500, 2500, 0, 180, 90, 90, Servo()},
  {"shoulder", 's', 14, 500, 2500, 0, 180, 90, 90, Servo()},
  {"elbow",    'e', 27, 500, 2500, 0, 180, 90, 90, Servo()},  // 90 = straight; collision-free to ±170° (assembly check)
  {"wrist",    'w', 26, 500, 2500, 0, 180, 90, 90, Servo()},  // 90 = straight; collision-free to ±150°
  {"claw",     'g', 25, 500, 2500, 0, 180, 20, 20, Servo()},  // MG90S; angle set from mm below
};
const int N = sizeof(joints) / sizeof(joints[0]);
const int CLAW = 4;

// Claw: rack and pinion, pitch radius 9 mm -> 3.18° of servo per mm of jaw gap, 0-44 mm in 140°.
const float DEG_PER_MM = 3.183;
const float GRIP_MAX_MM = 44.0;
int GRIP_OPEN_DIR = +1;          // +1: a bigger angle opens the claw. If "g 5" squeezes instead of opening, set -1
float GRIP_CLOSED_DEG = 20.0;    // with GRIP_OPEN_DIR -1 use about 160
const int STEP_MS = 15;
float clawMm = 0.0;

float clawDeg(float mm) { return GRIP_CLOSED_DEG + GRIP_OPEN_DIR * DEG_PER_MM * constrain(mm, 0.0f, GRIP_MAX_MM); }

void printAngles(const char *prefix) {
  Serial.print(prefix);
  for (int i = 0; i < CLAW; i++) { Serial.printf(" %.0f", joints[i].deg); }
  Serial.printf(" %.1f\n", clawMm);
}

// Move every joint towards its target; all joints arrive together. Returns false if stopped by 'x'.
bool runMove() {
  float maxd = 0;
  for (int i = 0; i < N; i++) maxd = max(maxd, fabsf(joints[i].target - joints[i].deg));
  int steps = (int)ceilf(maxd);
  float start[N];
  for (int i = 0; i < N; i++) start[i] = joints[i].deg;
  for (int k = 1; k <= steps; k++) {
    for (int i = 0; i < N; i++) {
      joints[i].deg = start[i] + (joints[i].target - start[i]) * k / steps;
      joints[i].servo.write((int)roundf(joints[i].deg));
    }
    delay(STEP_MS);
    if (Serial.available() && Serial.peek() == 'x') { Serial.read(); return false; }
  }
  return true;
}

void setJoint(int i, float deg) { joints[i].target = constrain(deg, (float)joints[i].lo, (float)joints[i].hi); }
void setClaw(float mm) { clawMm = constrain(mm, 0.0f, GRIP_MAX_MM); setJoint(CLAW, clawDeg(clawMm)); }

void setup() {
  Serial.begin(115200);
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  joints[CLAW].deg = joints[CLAW].target = GRIP_CLOSED_DEG;
  for (int i = 0; i < N; i++) {
    joints[i].servo.setPeriodHertz(50);
    joints[i].servo.attach(joints[i].pin, joints[i].minUs, joints[i].maxUs);
    joints[i].servo.write((int)joints[i].deg);
    delay(300);                             // stagger start-up current
  }
  Serial.println("arm_test ready: c | f | b/s/e/w <deg> | g <mm> | k <deg> | p | m b s e w mm | ? | x");
}

void loop() {
  if (!Serial.available()) return;
  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.length() == 0) return;
  char cmd = line.charAt(0);
  String args = line.substring(1);
  args.trim();
  if (cmd == '?') { printAngles("pos"); return; }
  if (cmd == 'x') { Serial.println("stopped"); return; }
  if (cmd == 'm') {                          // m b s e w mm
    float v[5];
    int n = sscanf(args.c_str(), "%f %f %f %f %f", &v[0], &v[1], &v[2], &v[3], &v[4]);
    if (n != 5) { Serial.println("err need: m b s e w mm"); return; }
    for (int i = 0; i < CLAW; i++) setJoint(i, v[i]);
    setClaw(v[4]);
    Serial.println(runMove() ? "ok" : "stopped");
    return;
  }
  if (cmd == 'c') {
    for (int i = 0; i < CLAW; i++) setJoint(i, 90);
    setClaw(0);
  } else if (cmd == 'f') {
    setClaw(0);
  } else if (cmd == 'g') {
    setClaw(args.toFloat());
  } else if (cmd == 'k') {
    GRIP_CLOSED_DEG = constrain(args.toFloat(), 0.0f, 180.0f);
    setClaw(clawMm);
    Serial.printf("GRIP_CLOSED_DEG = %.1f\n", GRIP_CLOSED_DEG);
  } else if (cmd != 'p') {
    bool found = false;
    for (int i = 0; i < CLAW; i++) if (joints[i].key == cmd) { setJoint(i, args.toFloat()); found = true; }
    if (!found) { Serial.println("unknown command"); return; }
  }
  runMove();
  printAngles("angles b s e w | claw mm:");
}

// Desktop robot arm: servo test and centring sketch for an ESP32 DevKit.
// Board: "ESP32 Dev Module". Library: ESP32Servo (Library Manager).
// Serial Monitor at 115200, line ending "Newline". Commands:
//   c            centre every joint (90°): do this before fitting the horns
//   b|s|e|w <deg> move base / shoulder / elbow / wrist to <deg> (0-180, clamped to its limits)
//   g <deg>      gripper opening 0-60° (0 = closed)
//   p            print current angles
// Joints move slowly (1° per STEP_MS) so a wrong direction is easy to stop: unplug the 6 V supply.

#include <ESP32Servo.h>

struct Joint { const char *name; char key; int pin; int minUs; int maxUs; int lo; int hi; int deg; Servo servo; };

// GPIO13/14/27/26/25 are not boot-strapping pins. MG996R and SG90 pulse range ~500-2500 µs for 0-180°.
Joint joints[] = {
  {"base",     'b', 13, 500, 2500, 0, 180, 90, Servo()},
  {"shoulder", 's', 14, 500, 2500, 0, 180, 90, Servo()},
  {"elbow",    'e', 27, 500, 2500, 0, 180, 90, Servo()},  // 90 = straight; collision-free to ±140° (assembly check)
  {"wrist",    'w', 26, 500, 2500, 0, 180, 90, Servo()},  // 90 = straight; collision-free to ±130°
  {"gripper",  'g', 25, 500, 2500, 30, 150, 90, Servo()}, // 90 = closed (horn fitted with the jaws closed)
};
const int N = sizeof(joints) / sizeof(joints[0]);
const int GRIP_OPEN_DIR = +1;   // set to -1 if the jaw closes harder instead of opening
const int STEP_MS = 15;

void moveTo(Joint &j, int target) {
  target = constrain(target, j.lo, j.hi);
  while (j.deg != target) {
    j.deg += (target > j.deg) ? 1 : -1;
    j.servo.write(j.deg);
    delay(STEP_MS);
  }
}

void printAngles() {
  for (int i = 0; i < N; i++) { Serial.printf("%s=%d ", joints[i].name, joints[i].deg); }
  Serial.println();
}

void setup() {
  Serial.begin(115200);
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  for (int i = 0; i < N; i++) {
    joints[i].servo.setPeriodHertz(50);
    joints[i].servo.attach(joints[i].pin, joints[i].minUs, joints[i].maxUs);
    joints[i].servo.write(joints[i].deg);   // start centred
    delay(300);                             // stagger start-up current
  }
  Serial.println("arm_test ready: c | b/s/e/w <deg> | g <0-60> | p");
}

void loop() {
  if (!Serial.available()) return;
  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.length() == 0) return;
  char cmd = line.charAt(0);
  int val = line.length() > 1 ? line.substring(1).toInt() : 0;
  if (cmd == 'c') {
    for (int i = 0; i < N; i++) moveTo(joints[i], 90);
  } else if (cmd == 'p') {
    // fall through to print
  } else if (cmd == 'g') {
    moveTo(joints[4], 90 + GRIP_OPEN_DIR * constrain(val, 0, 60));
  } else {
    bool found = false;
    for (int i = 0; i < 4; i++) if (joints[i].key == cmd) { moveTo(joints[i], val); found = true; }
    if (!found) { Serial.println("unknown command"); return; }
  }
  printAngles();
}

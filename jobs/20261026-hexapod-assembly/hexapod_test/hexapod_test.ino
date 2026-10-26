// Hexapod test sketch: centring, per-servo trims, stand, simple tripod walk.
// ESP32 + 2 × PCA9685 (0x40 left legs, 0x41 right legs). Library: "Adafruit PWM Servo Driver".
// Serial Monitor 115200, "Newline". Commands:
//   c              centre all 18 servos (90°)          s   stand (neutral stance)
//   t <ch> <deg>   trim servo <ch> (0-17) by <deg>     p   print trims
//   w              walk forward (tripod)               x   stop
// Channel n: leg = n / 3 (0 LF, 1 LM, 2 LR, 3 RF, 4 RM, 5 RR), joint = n % 3 (coxa, femur, tibia).

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pcaL(0x40), pcaR(0x41);

const int US_MIN = 500, US_MAX = 2500;   // MG90S 0-180°
int TRIM[18] = {0};                       // degrees, from 't' commands
// +1/-1 per joint so that + means: coxa = foot forward, femur = up, tibia = foot outward.
// Left and right coxae are mirrored; adjust any joint that moves the wrong way.
int DIR[18] = { +1, +1, +1,  +1, +1, +1,  +1, +1, +1,
                -1, +1, +1,  -1, +1, +1,  -1, +1, +1 };
const int MAX_COXA = 30;                  // keeps neighbours within the 70° the assembly check allows

void writeServo(int n, float deg) {       // deg relative to centre (0 = 90°)
  float a = constrain(90 + DIR[n] * deg + TRIM[n], 0, 180);
  int us = US_MIN + (US_MAX - US_MIN) * a / 180.0;
  int leg = n / 3, j = n % 3;
  int ch = (leg % 3) * 4 + j;             // 0,1,2 / 4,5,6 / 8,9,10
  (leg < 3 ? pcaL : pcaR).writeMicroseconds(ch, us);
}

void setLeg(int leg, float coxa, float femur, float tibia) {
  writeServo(leg * 3 + 0, constrain(coxa, -MAX_COXA, MAX_COXA));
  writeServo(leg * 3 + 1, femur);
  writeServo(leg * 3 + 2, tibia);
}

void stand() { for (int l = 0; l < 6; l++) setLeg(l, 0, 0, 0); }

bool walking = false;
const int TRIPOD_A[3] = {0, 2, 4}, TRIPOD_B[3] = {1, 3, 5};

void step(const int *lift, const int *push, float sw) {
  // lift, swing forward; the other tripod pushes back
  for (float p = 0; p <= 1.0; p += 0.1) {
    for (int i = 0; i < 3; i++) {
      setLeg(lift[i], -sw + 2 * sw * p, 25 * sin(p * PI), -10 * sin(p * PI));
      setLeg(push[i], sw - 2 * sw * p, 0, 0);
    }
    delay(25);
  }
}

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);
  pcaL.begin(); pcaR.begin();
  pcaL.setOscillatorFrequency(27000000); pcaR.setOscillatorFrequency(27000000);
  pcaL.setPWMFreq(50); pcaR.setPWMFreq(50);
  delay(10);
  stand();
  Serial.println("hexapod_test ready: c s t p w x");
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n'); line.trim();
    char c = line.length() ? line.charAt(0) : 0;
    if (c == 'c' || c == 's') { walking = false; stand(); }
    else if (c == 'w') walking = true;
    else if (c == 'x') { walking = false; stand(); }
    else if (c == 't') {
      int sp = line.indexOf(' ', 2);
      int ch = line.substring(2, sp).toInt(), d = line.substring(sp + 1).toInt();
      if (ch >= 0 && ch < 18) { TRIM[ch] += d; writeServo(ch, 0); }
    } else if (c == 'p') {
      Serial.print("int TRIM[18] = {");
      for (int i = 0; i < 18; i++) { Serial.print(TRIM[i]); Serial.print(i < 17 ? ", " : "};\n"); }
    }
  }
  if (walking) {
    // forward for left legs is +coxa, for right legs DIR[] flips it
    step(TRIPOD_A, TRIPOD_B, 15);
    step(TRIPOD_B, TRIPOD_A, 15);
  }
}

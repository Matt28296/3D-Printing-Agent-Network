// Hexapod test sketch: centring, per-servo trims, stand, and a tripod walk whose feet move in straight
// lines (inverse kinematics on the frames of hex_frame.py / assembly_check.leg_frames).
// ESP32 + 2 × PCA9685 (0x40 left legs, 0x41 right legs). Library: "Adafruit PWM Servo Driver" (it also
// installs Adafruit BusIO: accept the prompt). Serial Monitor 115200, "Newline". Commands:
//   c              centre all 18 servos (90°: femurs level, tibias vertical; fit the horns here)
//   s              stand in the neutral stance (NEUTRAL_FEMUR / NEUTRAL_TIBIA below)
//   t <n> <deg>    trim servo n (0-17) by <deg>        p   print trims
//   w              walk forward (tripod)               x   stop and stand (within one 25 ms gait frame)
//   o              measure the PCA9685 clocks: first jumper ONE board's channel-15 signal pin to GPIO34
// Servo n (as in t): leg = n / 3 (0 LF, 1 LM, 2 LR, 3 RF, 4 RM, 5 RR), joint = n % 3 (coxa, femur, tibia).
// PCA9685 channels: left board LF 0-2, LM 4-6, LR 8-10; right board RF 8-10, RM 4-6, RR 0-2. With both
// header rows facing outwards, each board's front leg is then on the channels at its front end.
// Battery: 100k/33k divider from the switched LiPo + to GPIO35. When it reads below 6.6 V twice in a row
// (3.3 V per cell under load) the hexapod stops walking and won't walk again until restarted.

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pcaL(0x40), pcaR(0x41);

// ===== NEUTRAL STANCE AND LEG GEOMETRY ==========================================================
// From hex_frame.py (mm, degrees). The gait, the stand and the body height (printed at start-up) are all
// worked out from this block.
const float L_C = 32.0f;                  // coxa axis -> femur axis (radial)
const float L_F = 45.0f;                  // femur axis -> knee axis
const float L_T = 70.0f;                  // knee axis -> foot tip
const float Y_F = -13.5f;                 // femur servo tab plane, sideways from the coxa line (coxa bracket y)
const float Z_F = 20.0f;                  // femur axis below the coxa bracket's back face (T_C 8 + 12; round 3)
const float T_F = 7.0f;                   // femur plate
const float T_T = 7.0f;                   // tibia plate
const float LB = 12.6f;                   // servo tab plane -> next link's back face (MG90S own spec, deep review 01-B2)
const float TAB_T = 2.5f;                 // MG90S mounting-tab thickness (the tibia servo is reversed: tabs on the femur's back face)
const float PLATE_GAP = 4.1f;             // bottom-plate underside -> coxa bracket's back face (coxa servos reversed, round 3)
const float MOUNT_DEG[6] = {40, 90, 140, -40, -90, -140};   // each leg's outward direction (LEG_MOUNTS), X forward, Y left
const float NEUTRAL_FEMUR = -4.7f;        // walking stance, this sketch's angles: 0 = femur level, + = up
const float NEUTRAL_TIBIA = -14.0f;       //   0 = tibia square to the femur (vertical), + = foot outward; tucked 18.7° in (deep review 05 SYS-1)
// ================================================================================================

// Gait: tripods {LF, LR, RM} and {LM, RF, RR}. Each foot moves back in a straight line on the ground,
// then swings forward with a sine lift. Each tripod swings for 40 % of the cycle, so all six feet are
// down for 10 % of the cycle at each hand-over and the landing tripod takes the load gradually.
const float STRIDE_MM = 30.0f;            // foot travel along the body per cycle (30-40 mm checked)
const float LIFT_MM = 20.0f;              // swing height
const int FRAME_MS = 25;
const int CYCLE_FRAMES = 20;              // 0.5 s per cycle
const int SWING_FRAMES = 8;               // frames from lift-off to touchdown (p = 0 ... 1)

// Each board's real oscillator. The datasheet's typical value is 25 MHz, but chips run from about 23 to
// 27 MHz, and every pulse is off by the same ratio (a 25 MHz chip set as 27 MHz gives pulses 8 % long).
// Measure each board with o and copy the printed value here.
uint32_t OSC_L = 25000000, OSC_R = 25000000;
float ticksPerUs[2];                      // PCA9685 counts per microsecond, per board (from its clock and prescale)

const int US_MIN = 500, US_MAX = 2500;   // MG90S 0-180°
int TRIM[18] = {0};                       // degrees, from 't' commands
// +1/-1 per joint so that + means: coxa = foot forward, femur = up, tibia = foot outward.
// Left and right coxae are mirrored; adjust any joint that moves the wrong way.
int DIR[18] = { +1, +1, +1,  +1, +1, +1,  +1, +1, +1,
                -1, +1, +1,  -1, +1, +1,  -1, +1, +1 };
const int MAX_COXA = 30;                  // keeps neighbours within the 60° the round-3 assembly check allows
const int FEMUR_MIN = -70, FEMUR_MAX = 90;   // assembly check: the femur is clear from -70° to +90°
const int TIBIA_MIN = -80, TIBIA_MAX = 90;   // assembly check: -170°..0° in its frame = -80°..+90° here
const int CAL_PIN = 34;                   // o: the measured board's channel 15, jumpered here
const int VBAT_PIN = 35;                  // ADC1, input-only: 100k from the switched LiPo +, 33k to GND, 100 nF across the 33k
const float VBAT_DIV = (100.0f + 33.0f) / 33.0f, VBAT_STOP = 6.6f;
const float RAD = 0.017453293f;
float lastDeg[18] = {0};                  // last angle sent to each servo (0 = servo centre)
float footSide, footR0, footH0;           // neutral foot: sideways (clockwise), radial and height from the coxa axis

void writeServo(int n, float deg) {       // deg relative to the servo's centre (0 = 90°)
  lastDeg[n] = deg;
  float a = constrain(90 + DIR[n] * deg + TRIM[n], 0, 180);
  float us = US_MIN + (US_MAX - US_MIN) * a / 180.0f;
  int leg = n / 3, j = n % 3, side = leg < 3 ? 0 : 1;
  int ch = (side == 0 ? leg : 2 - (leg - 3)) * 4 + j;   // left: front 0-2 ... rear 8-10; right: front 8-10 ... rear 0-2
  // setPWM with precomputed ticks: one I2C write per servo (writeMicroseconds would also read the prescale)
  (side == 0 ? pcaL : pcaR).setPWM(ch, 0, (uint16_t)lroundf(us * ticksPerUs[side]));
}

void setLeg(int leg, float coxa, float femur, float tibia) {
  writeServo(leg * 3 + 0, constrain(coxa, -MAX_COXA, MAX_COXA));
  writeServo(leg * 3 + 1, constrain(femur, FEMUR_MIN, FEMUR_MAX));
  writeServo(leg * 3 + 2, constrain(tibia, TIBIA_MIN, TIBIA_MAX));
}

// The neutral foot from the block above (leg_frames: coxa 0, femur NEUTRAL_FEMUR, tibia -90 + NEUTRAL_TIBIA).
void neutralFoot() {
  float f = NEUTRAL_FEMUR * RAD, ft = (NEUTRAL_FEMUR + NEUTRAL_TIBIA - 90.0f) * RAD;
  footR0 = L_C + L_F * cosf(f) + L_T * cosf(ft);
  footH0 = -Z_F + L_F * sinf(f) + L_T * sinf(ft);       // negative: below the coxa bracket's back face
  footSide = Y_F + 2 * LB - TAB_T + T_T / 2;            // 12.7 mm: the legs are rotated copies, not mirrored
}

// Inverse kinematics: foot moved by (dx, dy, dz) mm in body axes (X forward, Y left, Z up) from its neutral
// position -> this sketch's angles. Closed form on the frames of assembly_check.leg_frames.
void legIK(int leg, float dx, float dy, float dz, float &coxa, float &femur, float &tibia) {
  float a = MOUNT_DEG[leg] * RAD, ca = cosf(a), sa = sinf(a);
  float px = footR0 * ca + footSide * sa + dx, py = footR0 * sa - footSide * ca + dy;   // foot, from the coxa axis
  float r = sqrtf(max(px * px + py * py - footSide * footSide, 1.0f));                 // radial reach in the leg plane
  float c = a - atan2f(py, px) - atan2f(footSide, r);                                  // + = clockwise from above
  c = atan2f(sinf(c), cosf(c));
  float u = r - L_C, v = footH0 + dz + Z_F;                                            // foot from the femur axis
  float k = (u * u + v * v - L_F * L_F - L_T * L_T) / (2 * L_F * L_T);
  float t = -acosf(constrain(k, -1.0f, 1.0f));                                         // knee bends the foot down
  float f = atan2f(v, u) - atan2f(L_T * sinf(t), L_F + L_T * cosf(t));
  coxa = (leg < 3 ? c : -c) / RAD;        // + = foot forward on both sides
  femur = f / RAD;
  tibia = t / RAD + 90.0f;
}

// Every servo eases from its last angle to target[] over 0.2 s instead of snapping.
void easeTo(const float *target) {
  float from[18];
  memcpy(from, lastDeg, sizeof from);
  for (int k = 1; k <= 8; k++) {
    for (int n = 0; n < 18; n++) writeServo(n, from[n] + (target[n] - from[n]) * k / 8.0f);
    delay(FRAME_MS);
  }
  for (int n = 0; n < 18; n++) lastDeg[n] = target[n];
}

void centre() { float z[18] = {0}; easeTo(z); }

void stand() {
  float s[18];
  for (int l = 0; l < 6; l++) { s[l * 3] = 0; s[l * 3 + 1] = NEUTRAL_FEMUR; s[l * 3 + 2] = NEUTRAL_TIBIA; }
  easeTo(s);
}

// Power-up: the servos have been limp and all 18 would start at once, so the legs start one by one (0.9 s).
void standStaggered() { for (int l = 0; l < 6; l++) { setLeg(l, 0, NEUTRAL_FEMUR, NEUTRAL_TIBIA); delay(150); } }

bool walking = false;
bool battLow = false;                     // latched until restart: the LiPo needs charging
int gaitFrame = 0;                        // frames since w

// Foot offset from neutral, along the body, at frame tau of a tripod's cycle (tau 0 = lift-off).
void footPath(int tau, float stride, float &dx, float &dz) {
  if (tau <= SWING_FRAMES) {              // swing: p runs 0 ... 1.0, landing exactly at the stance start
    float p = (float)tau / SWING_FRAMES;
    dx = -stride / 2 + stride * p;
    dz = LIFT_MM * max(0.0f, sinf(p * (float)PI));
  } else {                                // stance: straight back along the ground at constant speed
    float q = (float)(tau - SWING_FRAMES) / (CYCLE_FRAMES - SWING_FRAMES);
    dx = stride / 2 - stride * q;
    dz = 0;
  }
}

// One gait frame for all six legs. The stride ramps up over the first cycle, so the walk starts from the
// neutral stance without a jump.
void walkFrame() {
  float stride = STRIDE_MM * min(1.0f, (float)gaitFrame / CYCLE_FRAMES);
  for (int leg = 0; leg < 6; leg++) {
    bool tripodA = (leg == 0 || leg == 2 || leg == 4);
    int tau = (gaitFrame + (tripodA ? 0 : CYCLE_FRAMES / 2)) % CYCLE_FRAMES;
    float dx, dz, c, f, t;
    footPath(tau, stride, dx, dz);
    legIK(leg, dx, 0, dz, c, f, t);
    setLeg(leg, c, f, t);
  }
  gaitFrame++;
  delay(FRAME_MS);
}

// o: measure a board's real clock from its frame period. Jumper the channel-15 signal pin of ONE board to
// GPIO34 (the other board then reports "no signal"), type o, and copy the value into OSC_L or OSC_R.
// The measured value is used at once, until the next restart.
void calibrateOsc(Adafruit_PWMServoDriver &pca, int side, const char *name) {
  pca.setPWM(15, 0, 2048);                // 50 % square wave at the frame rate
  delay(100);
  unsigned long hi = pulseIn(CAL_PIN, HIGH, 50000), lo = pulseIn(CAL_PIN, LOW, 50000);
  pca.setPWM(15, 0, 4096);                // channel 15 fully off again
  if (!hi || !lo) { Serial.printf("%s: no signal on GPIO34\n", name); return; }
  int pre = pca.readPrescale();
  double osc = 4096.0 * (pre + 1) * 1e6 / (double)(hi + lo);
  if (osc < 20e6 || osc > 30e6) { Serial.printf("%s: %.0f Hz can't be a PCA9685 clock: check the jumper\n", name, osc); return; }
  ticksPerUs[side] = (float)(osc / (1e6 * (pre + 1)));
  Serial.printf("%s: frame %lu us -> OSC_%s = %.0f\n", name, hi + lo, name, osc);
}

bool boardOk[2];

// A board that doesn't answer is reported and the walk is refused, but c, s and t still work on the other
// one (BUILD_GUIDE §3 step 1 centres the servos with one board on the bench). A missing A0 jumper puts both
// boards at 0x40: then 0x41 is missing, and 0x40's channels would drive both sides at once.
void setupBoard(Adafruit_PWMServoDriver &pca, uint32_t osc, int side, const char *name, int addr) {
  boardOk[side] = pca.begin();
  if (!boardOk[side]) {
    Serial.printf("PCA9685 %s (0x%02X) not found: check SDA/SCL, VCC and the A0 jumper. Walking is off\n", name, addr);
    ticksPerUs[side] = osc / (1e6f * 122);
    return;
  }
  pca.setOscillatorFrequency(osc);
  pca.setPWMFreq(50);
  ticksPerUs[side] = osc / (1e6f * (pca.readPrescale() + 1));
}

unsigned long lastBatt = 0;
int lowReadings = 0;

void checkBattery() {
  uint32_t mv = 0;
  for (int i = 0; i < 8; i++) mv += analogReadMilliVolts(VBAT_PIN);
  float v = mv / 8.0f * VBAT_DIV / 1000.0f;
  if (v < 3.0f) return;                   // no divider fitted, or the LiPo is switched off (USB only)
  lowReadings = v < VBAT_STOP ? lowReadings + 1 : 0;
  if (lowReadings >= 2 && !battLow) {     // twice in a row, about a second apart
    battLow = true;
    if (walking) { walking = false; stand(); }
    Serial.printf("LiPo %.2f V: low, walking is off. Switch off and charge it with a balance charger\n", v);
  }
}

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);
  setupBoard(pcaL, OSC_L, 0, "L", 0x40);
  setupBoard(pcaR, OSC_R, 1, "R", 0x41);
  Wire.setClock(400000);                  // 18 writes per gait frame: ~3 ms of bus time instead of ~12 ms
  pinMode(CAL_PIN, INPUT);
  neutralFoot();
  standStaggered();
  Serial.printf("hexapod_test ready: c s t p w x o   (body underside %.1f mm above the ground)\n", PLATE_GAP - footH0);
  checkBattery();
}

void loop() {
  if (millis() - lastBatt >= 1000) { lastBatt = millis(); checkBattery(); }
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n'); line.trim();
    char c = line.length() ? line.charAt(0) : 0;
    if (c == 'c') { walking = false; centre(); }
    else if (c == 's' || c == 'x') { walking = false; stand(); }
    else if (c == 'w') {
      if (battLow) Serial.println("LiPo low: charge it, then restart");
      else if (!boardOk[0] || !boardOk[1]) Serial.println("w needs both PCA9685 boards (0x40 and 0x41)");
      else if (!walking) { stand(); walking = true; gaitFrame = 0; }
    }
    else if (c == 'o') { calibrateOsc(pcaL, 0, "L"); calibrateOsc(pcaR, 1, "R"); }
    else if (c == 't') {
      int ch, d;
      if (sscanf(line.c_str() + 1, "%d %d", &ch, &d) == 2 && ch >= 0 && ch < 18 && abs(TRIM[ch] + d) <= 20) {
        TRIM[ch] += d;
        writeServo(ch, 0);
        Serial.printf("TRIM[%d] = %d\n", ch, TRIM[ch]);
      } else Serial.println("usage: t <servo 0-17> <deg>, total trim within +-20");
    } else if (c == 'p') {
      Serial.print("int TRIM[18] = {");
      for (int i = 0; i < 18; i++) { Serial.print(TRIM[i]); Serial.print(i < 17 ? ", " : "};\n"); }
    }
  }
  if (walking) walkFrame();               // one 25 ms frame per loop: x, s and c act within a frame
}

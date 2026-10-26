// Desktop robot arm (claw v2): servo test, calibration and PC control for an ESP32 DevKit.
// Board: "ESP32 Dev Module" on the arduino-esp32 3.x core. Library: ESP32Servo 3.x (Library Manager).
// Serial Monitor at 115200, line ending "Newline". BUILD_GUIDE.md §5 explains every command.
//
// Angles are JOINT angles in the CAD's convention (assembly_check.py's q_deg), not servo angles:
//   b  base yaw    -90..90   0 = the arm along +X, out over the ESP32's USB wall; + = anticlockwise from above
//   s  shoulder      0..180  0 = upper link horizontal towards +X; 90 = upright
//   e  elbow      -150..30   0 = forearm in line with the upper link; - = folded down, towards the desk
//   w  wrist       -90..90   0 = claw in line with the forearm; - = fingertips down
//   g  claw          0..44   opening between the grip faces, mm; 0 = closed
//
// Commands for you:
//   b|s|e|w <deg>  move one joint (clamped to its limits)           g <mm>  claw opening
//   h <mm>         hold an object <mm> wide: the claw closes to GRIP_SQUEEZE_MM under its width. Hold things
//                  with h, not g 0. Every move that closes the claw squeezes for at most GRIP_SQUEEZE_MS, then
//                  the servo eases off GRIP_BACKOFF_DEG
//   r              rest: park upright, where the shoulder holds about 0 N.mm. The arm also parks by itself
//                  after IDLE_PARK_S seconds without a command; i <s> changes that (i 0 = never), i shows it
//   t              show the joint trims; t <b|s|e|w> <deg> sets one; t save keeps them (BUILD_GUIDE §5)
//   c              every servo to its centre (90°) and the claw closed: the horn-fitting pose of BUILD_GUIDE §4
//   f              claw servo to its closed angle (fitting the pinion); k <deg> trims that angle (kept)
//   u <j> <us>     end-stop test, before the horns go on: one servo (b s e w g) to a raw pulse, moved slowly.
//                  It ignores the joint limits and the guard
//   p              print the joint angles (moves nothing)
// Commands for a PC program (pc/arm_pc_control.py):
//   m <b> <s> <e> <w> <mm>  move every joint together. One reply when it ends: "ok", "stopped" (x),
//                  "blocked: desk" or "blocked: base" (the guard ended it early), or "err ..." (refused)
//   ?              replies "pos <b> <s> <e> <w> <mm>", also during a move
//   x              stop the current move where it is; nothing resumes it. Replies "idle" if nothing moves
//
// Moves ramp up and down at ACCEL to SPEED, every joint arriving at the same time. Before a move starts, the
// guard looks along its path and ends it early, smoothly, where a part would come within GUARD_CLEAR mm of the
// desk, the base or the turntable; it checks every step again while the move runs. The guard is only right
// once every joint's dir is set (BUILD_GUIDE §5). The pose, the trims and the claw trim are kept in flash
// (NVS): after a reset (power-up, or the PC opening the port) each servo restarts where it stopped, claw first
// and base last.

#include <ESP32Servo.h>
#include <Preferences.h>
#include <cmath>

// ---- Claw: rack and pinion, pitch radius 9 mm: 3.18° of servo per mm of jaw gap, 0-44 mm in 140° -------------
const float DEG_PER_MM = 3.183;
const float GRIP_MAX_MM = 44.0;
int GRIP_OPEN_DIR = +1;          // +1: a bigger angle opens the claw. If "g 5" squeezes instead of opening, set -1
float GRIP_CLOSED_DEG = 20.0;    // with GRIP_OPEN_DIR -1 use about 160. k trims it at run time and keeps the trim
// Holding (deep review 03, SYS-11). A stalled MG90S draws about 0.7 A and heats itself and the PETG around it
// within minutes, and the sketch can't feel an object. So h closes GRIP_SQUEEZE_MM under the object's width,
// and every move that closes the claw squeezes for at most GRIP_SQUEEZE_MS before easing off GRIP_BACKOFF_DEG.
const float GRIP_SQUEEZE_MM = 1.5;          // 1-2 mm
const unsigned long GRIP_SQUEEZE_MS = 2000;
const float GRIP_BACKOFF_DEG = 1.5;         // 1-2°, about 0.5 mm

// ---- Joints: one table maps each servo to its joint ----------------------------------------------------------
//   servo angle (0-180°) = 90 + dir × (joint + trim − centre)      pulse = minUs + (maxUs − minUs) × servo / 180
// minUs, maxUs  the pulses for servo 0° and 180°. If the end-stop test (u, BUILD_GUIDE §4) finds a servo
//               stopping before 500 or 2500 µs, put the stop here, backed off by 30 µs
// dir           +1 if a longer pulse turns the joint the + way (see the top), -1 if not. Set in BUILD_GUIDE §5
// centre        the joint angle at the servo's centre, where BUILD_GUIDE §4 fits the horn
// lo, hi        the joint's limits. Each servo also stays inside its own 0-180°, so a trim shortens one end
// The claw's line gives its pin, pulses and mm limits; the GRIP_ values above map mm to its servo.
// Pins: no strapping pin (0, 2, 5, 12, 15), no input-only pin (34-39) and none that pulses at boot. GPIO14
// does, so the shoulder, which carries the whole arm, is on GPIO32.
const float ELBOW_MIN = -150, ELBOW_MAX = 30;    // the elbow's window: narrow it here if the collision check asks

struct Joint {
  const char *name; char key; int pin; int minUs; int maxUs; int dir; float centre; float lo; float hi;
  float trim;    // joint degrees added before the mapping: corrects the horn's spline step (t; kept in NVS)
  float cur;     // servo angle written now, degrees (float: pulses go out in whole µs = 0.09° steps)
  float goal;    // servo angle at the end of the move
  Servo servo;
  Joint(const char *n, char k, int p, int mn, int mx, int d, float c, float l, float h)
      : name(n), key(k), pin(p), minUs(mn), maxUs(mx), dir(d), centre(c), lo(l), hi(h), trim(0), cur(90), goal(90) {}
};
Joint joints[] = {
  // name       key pin minUs maxUs dir  centre   lo          hi
  {"base",     'b', 13,  500, 2500, +1,     0,   -90,         90},
  {"shoulder", 's', 32,  500, 2500, +1,    90,     0,        180},
  {"elbow",    'e', 27,  500, 2500, +1,   -60,  ELBOW_MIN, ELBOW_MAX},
  {"wrist",    'w', 26,  500, 2500, +1,     0,   -90,         90},
  {"claw",     'g', 25,  500, 2500, +1,     0,     0,  GRIP_MAX_MM},
};
const int N = sizeof(joints) / sizeof(joints[0]);
const int CLAW = 4;
const float TRIM_MAX = 15;       // a horn sits at most half a spline tooth off: 7.2° (MG996R), about 9° (MG90S)

// ---- Motion (SYS-06) ------------------------------------------------------------------------------------------
// A trapezoidal speed profile in servo degrees: ACCEL up to SPEED, cruise, ACCEL down. The joint with the longest
// way sets the timing and the others scale, so all arrive together.
const float SPEED = 66.7;        // servo degrees per second at cruise (the old 1° per 15 ms)
const float ACCEL = 250.0;       // servo degrees per second², 200-300: small start and stop torques, no camera shake
const int STEP_MS = 20;          // one step per 50 Hz servo frame
const float LOOK_DEG = 0.5;      // the guard's look-ahead checks the path every LOOK_DEG of the longest way
const int BOOT_GAP_MS = 400;     // between attaching one servo and the next

// ---- Rest (SYS-02): upright. Deep review 03's mass model gives the shoulder about 1 N.mm there ----------------
const float PARK_SHOULDER = 90, PARK_ELBOW = 0, PARK_WRIST = 0;   // the base and the claw stay as they are
const unsigned long IDLE_PARK_S = 60;    // park after this many seconds without a command; 0 = never.
                                         // i <s> changes it at run time and keeps it in flash

// ---- Guard: desk, base and turntable --------------------------------------------------------------------------
// A side view of the arm. Every moving part is a box in its link's frame, measured from the CAD meshes:
//   x  along the link from its joint axis       y  across it in the arm plane (+y = down with the link level)
//   Y  sideways from the vertical plane through the yaw axis along the arm (+Y at yaw 0): the links step outwards,
//      one servo in front of the other, so each part has its own Y range
// The guard keeps every box GUARD_CLEAR mm from the desk (below each box), from the turntable disk and ring
// (r 48 up to 24.5 mm above the base top: only boxes with Y below 48 + GUARD_CLEAR) and from the 110 × 104 mm
// base box, turned into the arm's frame for the current yaw. The upper link is left out of the base checks: its
// tail passes 8.8 mm over the disk at worst. Checked against the meshes, BUILD_GUIDE §5.
const bool CAMERA_FITTED = true;   // false without the Brio
const float GUARD_CLEAR = 8.0;     // mm
const float DESK_Z = -40.0;        // desk top, relative to the base top plate (the shoulder axis is at +60.5)
const float SHOULDER_X = 10.15, SHOULDER_Z = 60.5, UPPER_L = 100.0, FORE_L = 90.0;
const float BASE_HX = 55.0, BASE_HY = 52.0, DRUM_R = 48.0, DRUM_TOP = 24.5;

struct Part { int link; float x0, x1, y0, y1, Y0, Y1; int kind; };
// link 1 = upper link (from the shoulder axis), 2 = forearm (elbow axis), 3 = claw (wrist axis)
// kind 0 = fixed, 1 = the Brio (left out without it), 2/3/4 = racks / necks / finger blades, whose y grows with
// the claw's opening g: racks ±max(28.27 − g/2, 15.71 + g/2), necks ±(14 + g/2), blades ±(6 + g/2) (claw_frame.py)
const Part PARTS[] = {
  {1, -25.0,  121.0,  -17.0, 17.0,   -7.5,   35.4,  0},   // upper link and the elbow MG996R
  {2, -25.0,  104.0,  -13.0, 13.0,   34.0,   44.0,  0},   // forearm
  {2,  68.4,  100.6,   -6.1,  6.1,   25.5,   58.0,  0},   // wrist MG90S
  {3,  -8.5,   33.85, -32.0, 32.0,   56.6,   98.6,  0},   // claw frame, cover, pinion and claw MG90S
  {3, -26.55,  14.0,  -28.0, 22.0,   98.6,  122.7,  0},   // camera mount
  {3, -21.69,  15.19, -51.0, 51.0,  102.35, 139.23, 1},   // Brio 4K
  {3,  22.6,   30.6,    0.0,  0.0,   62.85,  95.35, 2},   // racks
  {3,  30.6,   42.35,   0.0,  0.0,   62.85,  95.35, 3},   // necks
  {3,  42.35,  79.35,   0.0,  0.0,   62.85,  95.35, 4},   // finger blades, out to the fingertips
};
const int NPARTS = sizeof(PARTS) / sizeof(PARTS[0]);
const float RAD = 0.017453293f;
const char *guardWhat = "desk";    // which check ended the last blocked move

// Signed separation between a rectangle (centre cx cz, unit axis ux uz, half sizes hx hy) and the box
// [bx0, bx1] × [bz0, bz1], by the separating-axis test: > 0 = the gap between them, < 0 = how deep they overlap.
float satGap(float cx, float cz, float ux, float uz, float hx, float hy, float bx0, float bx1, float bz0, float bz1) {
  const float vx = uz, vz = -ux;                       // the rectangle's y axis
  const float ax[4][2] = {{1, 0}, {0, 1}, {ux, uz}, {vx, vz}};
  const float bcx = (bx0 + bx1) / 2, bcz = (bz0 + bz1) / 2, bhx = (bx1 - bx0) / 2, bhz = (bz1 - bz0) / 2;
  float best = -1e9f;
  for (int k = 0; k < 4; k++) {
    float nx = ax[k][0], nz = ax[k][1];
    float d = fabsf((cx - bcx) * nx + (cz - bcz) * nz) - hx * fabsf(ux * nx + uz * nz) - hy * fabsf(vx * nx + vz * nz)
              - bhx * fabsf(nx) - bhz * fabsf(nz);
    best = max(best, d);
  }
  return best;
}

// The x range (along the arm) where the base box, grown by GUARD_CLEAR, overlaps sideways offsets Y0..Y1 at this
// yaw: the box's corners turned into the arm's frame, clipped to Y0 <= y <= Y1. false if they don't overlap.
bool baseSpan(float yawDeg, float Y0, float Y1, float &xa, float &xb) {
  const float c = cosf(yawDeg * RAD), s = sinf(yawDeg * RAD), A = BASE_HX + GUARD_CLEAR, B = BASE_HY + GUARD_CLEAR;
  const float X[4] = {A, -A, -A, A}, Yw[4] = {B, B, -B, -B};
  float px[8], py[8];
  int n = 4;
  for (int i = 0; i < 4; i++) { px[i] = X[i] * c + Yw[i] * s; py[i] = -X[i] * s + Yw[i] * c; }
  for (int side = 0; side < 2; side++) {
    float lim = side ? Y1 : Y0, qx[8], qy[8];
    int m = 0;
    for (int i = 0; i < n; i++) {
      int j = (i + 1) % n;
      bool in_i = side ? py[i] <= lim : py[i] >= lim, in_j = side ? py[j] <= lim : py[j] >= lim;
      if (in_i) { qx[m] = px[i]; qy[m] = py[i]; m++; }
      if (in_i != in_j) { float t = (lim - py[i]) / (py[j] - py[i]); qx[m] = px[i] + t * (px[j] - px[i]); qy[m] = lim; m++; }
    }
    n = m;
    for (int i = 0; i < n; i++) { px[i] = qx[i]; py[i] = qy[i]; }
    if (n == 0) return false;
  }
  xa = xb = px[0];
  for (int i = 1; i < n; i++) { xa = min(xa, px[i]); xb = max(xb, px[i]); }
  return true;
}

// The guard's two margins at a pose (joint degrees, claw opening in mm): mm beyond GUARD_CLEAR, < 0 = too close.
void guardMargins(float yaw, float sh, float el, float wr, float gapMm, float &desk, float &base) {
  const float ang[4] = {0, sh, sh + el, sh + el + wr};
  float ox[4], oz[4];
  ox[1] = SHOULDER_X;
  oz[1] = SHOULDER_Z;
  ox[2] = ox[1] + UPPER_L * cosf(ang[1] * RAD);
  oz[2] = oz[1] + UPPER_L * sinf(ang[1] * RAD);
  ox[3] = ox[2] + FORE_L * cosf(ang[2] * RAD);
  oz[3] = oz[2] + FORE_L * sinf(ang[2] * RAD);
  const float d = constrain(gapMm, 0.0f, GRIP_MAX_MM) / 2;
  desk = base = 1e9f;
  for (int p = 0; p < NPARTS; p++) {
    const Part &P = PARTS[p];
    if (P.kind == 1 && !CAMERA_FITTED) continue;
    float y0 = P.y0, y1 = P.y1;
    if (P.kind == 2) y1 = max(28.27f - d, 15.71f + d);
    else if (P.kind == 3) y1 = 14.0f + d;
    else if (P.kind == 4) y1 = 6.0f + d;
    if (P.kind >= 2) y0 = -y1;
    const int L = P.link;
    const float s = sinf(ang[L] * RAD), c = cosf(ang[L] * RAD);
    desk = min(desk, oz[L] + min(P.x0 * s, P.x1 * s) + min(-y0 * c, -y1 * c) - (DESK_Z + GUARD_CLEAR));
    if (L == 1) continue;
    const float hx = (P.x1 - P.x0) / 2, hy = (y1 - y0) / 2, mx = (P.x0 + P.x1) / 2, my = (y0 + y1) / 2;
    const float cx = ox[L] + mx * c + my * s, cz = oz[L] + mx * s - my * c;
    const float r = DRUM_R + GUARD_CLEAR;
    if (P.Y0 < r) {                                    // every guarded part has Y0 > 0
      float xh = sqrtf(r * r - P.Y0 * P.Y0);
      base = min(base, satGap(cx, cz, c, s, hx, hy, -xh, xh, DESK_Z, DRUM_TOP + GUARD_CLEAR));
    }
    float xa, xb;
    if (baseSpan(yaw, P.Y0, P.Y1, xa, xb)) base = min(base, satGap(cx, cz, c, s, hx, hy, xa, xb, DESK_Z, GUARD_CLEAR));
  }
}

// ---- Servo <-> joint ------------------------------------------------------------------------------------------
float servoFromJoint(int i, float q) {
  if (i == CLAW) return GRIP_CLOSED_DEG + GRIP_OPEN_DIR * DEG_PER_MM * q;
  return 90.0f + joints[i].dir * (q + joints[i].trim - joints[i].centre);
}
float jointFromServo(int i, float sv) {
  if (i == CLAW) return GRIP_OPEN_DIR * (sv - GRIP_CLOSED_DEG) / DEG_PER_MM;
  return joints[i].dir * (sv - 90.0f) + joints[i].centre - joints[i].trim;
}
float jointNow(int i) { return jointFromServo(i, joints[i].cur); }
// A joint's usable range: its limits, inside what its servo's 0-180° reaches with the current trim. So the trims
// come first, then the limits and the guard, which work on the true joint angles.
float jointLo(int i) { return max(joints[i].lo, min(jointFromServo(i, 0), jointFromServo(i, 180))); }
float jointHi(int i) { return min(joints[i].hi, max(jointFromServo(i, 0), jointFromServo(i, 180))); }
void setJoint(int i, float q) { joints[i].goal = servoFromJoint(i, constrain(q, jointLo(i), jointHi(i))); }

int pulseUs(int i, float sv) { return joints[i].minUs + (int)lroundf((joints[i].maxUs - joints[i].minUs) * sv / 180.0f); }
void writeServo(int i, float sv) {
  sv = constrain(sv, 0.0f, 180.0f);
  joints[i].cur = sv;
  joints[i].servo.writeMicroseconds(pulseUs(i, sv));
}

// ---- Saved state (NVS) ----------------------------------------------------------------------------------------
// "pose2": the five servo angles, so a reset restarts each servo exactly where it was whatever the trims, plus the
// claw's closed angle, its direction and the closed angle compiled into this sketch (a re-flash that changes
// GRIP_OPEN_DIR or GRIP_CLOSED_DEG drops the k trim). "trim": the four joint trims (t save). "idle": i.
Preferences prefs;
const int NSAVE = 8;
float saved[NSAVE];              // what is in NVS now, so an unchanged pose isn't written again
float closedCompiled;
bool trimsSaved = false;
unsigned long idleParkS = IDLE_PARK_S;

void savePose() {
  float p[NSAVE] = {joints[0].cur, joints[1].cur, joints[2].cur, joints[3].cur, joints[CLAW].cur,
                    GRIP_CLOSED_DEG, (float)GRIP_OPEN_DIR, closedCompiled};
  if (memcmp(p, saved, sizeof p) == 0) return;
  prefs.putBytes("pose2", p, sizeof p);
  memcpy(saved, p, sizeof p);
}

void restore() {
  closedCompiled = GRIP_CLOSED_DEG;
  joints[CLAW].cur = joints[CLAW].goal = GRIP_CLOSED_DEG;       // first boot: every servo centred, claw closed
  prefs.begin("arm", false);
  float t[4];
  if (prefs.getBytes("trim", t, sizeof t) == sizeof t) {
    bool ok = true;
    for (int i = 0; i < 4; i++) ok = ok && std::isfinite(t[i]) && fabsf(t[i]) <= TRIM_MAX;
    if (ok) { for (int i = 0; i < 4; i++) joints[i].trim = t[i]; trimsSaved = true; }
  }
  uint32_t s;
  if (prefs.getBytes("idle", &s, sizeof s) == sizeof s && s <= 86400) idleParkS = s;
  float p[NSAVE];
  bool v2 = prefs.getBytes("pose2", p, sizeof p) == sizeof p;
  if (!v2) {                                                    // the previous sketch kept the claw in mm
    if (prefs.getBytes("pose", p, sizeof p) != sizeof p) return;
    p[4] = p[5] + p[6] * DEG_PER_MM * p[4];
  }
  for (int i = 0; i < NSAVE; i++) if (!std::isfinite(p[i])) return;
  for (int i = 0; i < N; i++) joints[i].cur = joints[i].goal = constrain(p[i], 0.0f, 180.0f);
  if ((int)p[6] == GRIP_OPEN_DIR && p[7] == closedCompiled) GRIP_CLOSED_DEG = constrain(p[5], 0.0f, 180.0f);
  if (v2) memcpy(saved, p, sizeof p);
}

// ---- Output ---------------------------------------------------------------------------------------------------
float tidy(float v) { v = roundf(v * 10) / 10; return v == 0 ? 0 : v; }     // one decimal, never "-0.0"

void printPos(const char *prefix) {
  Serial.print(prefix);
  for (int i = 0; i < N; i++) Serial.printf(" %.1f", tidy(jointNow(i)));
  Serial.println();
}

void printTrims() {
  Serial.print("trims");
  for (int i = 0; i < CLAW; i++) Serial.printf(" %c %.1f", joints[i].key, tidy(joints[i].trim));
  Serial.println(trimsSaved ? " (saved)" : " (not saved: t save keeps them)");
}

// ---- Moving ---------------------------------------------------------------------------------------------------
enum MoveResult { ARRIVED, STOPPED, BLOCKED };
String queued;                   // a command that arrived during a move: it runs when the move ends
unsigned long lastCmd = 0;       // millis() of the last command, or the end of the last move
bool idleDone = false;           // the idle park ran (or wasn't needed) since the last command
bool squeezing = false;          // a closing claw eases off at squeezeAt
unsigned long squeezeAt = 0;

void printResult(MoveResult r) {
  if (r == STOPPED) Serial.println("stopped");
  else if (r == BLOCKED) Serial.printf("blocked: %s\n", guardWhat);
}

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

// A claw that closed eases off GRIP_BACKOFF_DEG once it has squeezed for GRIP_SQUEEZE_MS. Not guarded: it opens
// the jaws by about 0.25 mm a side, well inside GUARD_CLEAR, and a stalled servo is the bigger risk.
void serviceGrip() {
  if (!squeezing || (long)(millis() - squeezeAt) < 0) return;
  squeezing = false;
  writeServo(CLAW, joints[CLAW].cur + GRIP_OPEN_DIR * GRIP_BACKOFF_DEG);
  joints[CLAW].goal = joints[CLAW].cur;
  savePose();
  Serial.printf("claw eased off to %.1f mm\n", tidy(jointNow(CLAW)));
}

// Distance (servo degrees) covered t seconds into a way of length D, and the time the whole way takes.
float profileTime(float D) {
  const float da = SPEED * SPEED / ACCEL;              // what the ramps up and down cover at full speed
  return D >= da ? D / SPEED + SPEED / ACCEL : 2 * sqrtf(D / ACCEL);
}
float profileDist(float D, float t) {
  const float T = profileTime(D);
  if (t >= T) return D;
  const float ta = min(SPEED / ACCEL, T / 2), v = ACCEL * ta;    // ramp time; top speed (lower on a short way)
  if (t < ta) return 0.5f * ACCEL * t * t;
  if (t < T - ta) return 0.5f * ACCEL * ta * ta + v * (t - ta);
  return D - 0.5f * ACCEL * (T - t) * (T - t);
}

void poseAt(const float *start, const float *delta, float f, float *sv) {
  for (int i = 0; i < N; i++) sv[i] = delta[i] != 0 ? start[i] + delta[i] * f : joints[i].cur;
}
void marginsOf(const float *sv, float &desk, float &base) {
  guardMargins(jointFromServo(0, sv[0]), jointFromServo(1, sv[1]), jointFromServo(2, sv[2]), jointFromServo(3, sv[3]),
               jointFromServo(CLAW, sv[CLAW]), desk, base);
}
// One step of the guard's rule: a margin below 0 (too close) may not shrink. So a move may always get clearer.
bool stepAllowed(float desk, float base, float deskPrev, float basePrev) {
  if (desk < 0 && desk < deskPrev - 0.001f) { guardWhat = "desk"; return false; }
  if (base < 0 && base < basePrev - 0.001f) { guardWhat = "base"; return false; }
  return true;
}

// Move every joint from where it is to its goal on the speed profile. The guard first walks the path and, if it
// must stop, shortens the move so it ramps down at the last allowed point. A stop (x or the guard) is final: the
// goals become where the joints are, so nothing later resumes the old move. The pose is saved at the end.
MoveResult runMove(bool guarded = true) {
  float start[N], delta[N], sv[N], D = 0;
  for (int i = 0; i < N; i++) {
    start[i] = joints[i].cur;
    delta[i] = fabsf(joints[i].goal - start[i]) < 0.01f ? 0 : joints[i].goal - start[i];
    D = max(D, fabsf(delta[i]));
  }
  MoveResult r = ARRIVED;
  float deskPrev, basePrev, dm, bm, fEnd = 1;
  marginsOf(start, deskPrev, basePrev);
  if (guarded && D > 0) {
    const int n = (int)ceilf(D / LOOK_DEG);
    float dp = deskPrev, bp = basePrev;
    for (int k = 1; k <= n; k++) {
      poseAt(start, delta, (float)k / n, sv);
      marginsOf(sv, dm, bm);
      if (!stepAllowed(dm, bm, dp, bp)) { fEnd = (float)(k - 1) / n; r = BLOCKED; break; }
      dp = dm;
      bp = bm;
    }
  }
  const float way = D * fEnd, T = profileTime(way);
  const unsigned long t0 = millis();
  while (way > 0) {
    delay(STEP_MS);
    const float t = (millis() - t0) / 1000.0f;
    poseAt(start, delta, profileDist(way, t) / D, sv);
    if (stopRequested()) { r = STOPPED; break; }
    if (guarded) {                                     // the look-ahead makes this rare: it would stop at once
      marginsOf(sv, dm, bm);
      if (!stepAllowed(dm, bm, deskPrev, basePrev)) { r = BLOCKED; break; }
      deskPrev = dm;
      basePrev = bm;
    }
    for (int i = 0; i < N; i++) if (delta[i] != 0) writeServo(i, sv[i]);
    if (delta[CLAW] == 0) serviceGrip();
    if (t >= T) break;
  }
  const float closedBy = GRIP_OPEN_DIR * (start[CLAW] - joints[CLAW].cur);   // > 0: the claw closed
  for (int i = 0; i < N; i++) joints[i].goal = joints[i].cur;
  if (closedBy > 0.05f) { squeezing = true; squeezeAt = millis() + GRIP_SQUEEZE_MS; }
  else if (closedBy < -0.05f) squeezing = false;
  savePose();
  lastCmd = millis();
  return r;
}

MoveResult park() {
  setJoint(1, PARK_SHOULDER);
  setJoint(2, PARK_ELBOW);
  setJoint(3, PARK_WRIST);
  return runMove();
}

// Park after idleParkS seconds without a command. Its lines start with "idle" or "park", never with a reply
// a PC program waits for.
void serviceIdle() {
  if (!idleParkS || idleDone || queued.length() || Serial.available() || millis() - lastCmd < idleParkS * 1000UL) return;
  idleDone = true;
  bool there = fabsf(jointNow(1) - constrain(PARK_SHOULDER, jointLo(1), jointHi(1))) < 0.5f &&
               fabsf(jointNow(2) - constrain(PARK_ELBOW, jointLo(2), jointHi(2))) < 0.5f &&
               fabsf(jointNow(3) - constrain(PARK_WRIST, jointLo(3), jointHi(3))) < 0.5f;
  if (there) return;
  Serial.printf("idle %lu s: parking (i 0 turns this off)\n", idleParkS);
  MoveResult r = park();
  if (r == STOPPED) Serial.println("park stopped");
  else if (r == BLOCKED) Serial.printf("park blocked: %s\n", guardWhat);
  printPos("parked b s e w | claw mm:");
}

// ---- Commands -------------------------------------------------------------------------------------------------
// Strict numbers: "s", "s abc" and "s nan" are refused instead of becoming 0 or NaN.
bool parseNum(const String &s, float &v) {
  const char *c = s.c_str();
  char *end;
  v = strtof(c, &end);
  return end != c && *end == '\0' && std::isfinite(v);
}

void trimCommand(const String &a) {
  if (a.length() == 0) { printTrims(); return; }
  if (a == "save") {
    float t[4];
    for (int i = 0; i < 4; i++) t[i] = joints[i].trim;
    prefs.putBytes("trim", t, sizeof t);
    trimsSaved = true;
    printTrims();
    return;
  }
  int j = -1;
  for (int i = 0; i < CLAW; i++) if (joints[i].key == a.charAt(0)) j = i;
  String num = a.substring(1);
  num.trim();
  float v;
  if (j < 0 || !parseNum(num, v) || fabsf(v) > TRIM_MAX) { Serial.println("err need: t <b|s|e|w> <deg> (-15 to 15), t, or t save"); return; }
  const float q = jointNow(j);                         // the joint keeps its angle: its servo moves by the change
  joints[j].trim = v;
  trimsSaved = false;
  setJoint(j, q);
  printResult(runMove());
  printTrims();
  printPos("angles b s e w | claw mm:");
}

void idleCommand(const String &a) {
  float v;
  if (a.length()) {
    if (!parseNum(a, v) || v < 0 || v > 86400) { Serial.println("err need: i <seconds> (0 = never park)"); return; }
    idleParkS = (unsigned long)lroundf(v);
    uint32_t s = idleParkS;
    prefs.putBytes("idle", &s, sizeof s);
  }
  if (idleParkS) Serial.printf("idle park after %lu s\n", idleParkS);
  else Serial.println("idle park off");
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(50);                     // a command line arrives in well under 50 ms
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  restore();                                 // where each servo stopped (centred, claw closed, on the first boot)
  const int order[N] = {CLAW, 3, 2, 1, 0};   // claw, wrist, elbow, shoulder, base: the light joints hold first
  for (int k = 0; k < N; k++) {
    const int i = order[k];
    joints[i].servo.setPeriodHertz(50);
    joints[i].servo.attach(joints[i].pin, joints[i].minUs, joints[i].maxUs);
    writeServo(i, joints[i].cur);            // nothing moves unless the arm was moved or sagged while it was off
    delay(BOOT_GAP_MS);
  }
  Serial.println("arm_test ready: b s e w g h r i t c f k u p | m ? x");
  printPos("start b s e w | claw mm:");
  bool outside = false;                      // limits or trims changed since the pose was saved: ease it back
  for (int i = 0; i < N; i++) {
    const float q = jointNow(i), qc = constrain(q, jointLo(i), jointHi(i));
    if (fabsf(qc - q) > 0.05f) { setJoint(i, qc); outside = true; }
  }
  if (outside) {
    Serial.println("start pose outside the joint limits: moving into them");
    printResult(runMove());
    printPos("angles b s e w | claw mm:");
  }
  lastCmd = millis();
}

void loop() {
  serviceGrip();
  serviceIdle();
  String line;
  if (queued.length()) { line = queued; queued = ""; }
  else if (Serial.available()) line = Serial.readStringUntil('\n');
  else return;
  line.trim();
  if (line.length() == 0) return;
  lastCmd = millis();
  idleDone = false;
  const char cmd = line.charAt(0);
  String args = line.substring(1);
  args.trim();
  if (cmd == '?') { printPos("pos"); return; }
  if (cmd == 'x') { Serial.println("idle"); return; }                    // nothing is moving
  if (cmd == 'p') { printPos("angles b s e w | claw mm:"); return; }   // prints only, never moves
  if (cmd == 't') { trimCommand(args); return; }
  if (cmd == 'i') { idleCommand(args); return; }
  if (cmd == 'm') {                                                      // m b s e w mm
    float v[5];
    if (sscanf(args.c_str(), "%f %f %f %f %f", &v[0], &v[1], &v[2], &v[3], &v[4]) != 5) { Serial.println("err need: m b s e w mm"); return; }
    for (int i = 0; i < 5; i++) if (!std::isfinite(v[i])) { Serial.println("err not a number"); return; }
    for (int i = 0; i < N; i++) setJoint(i, v[i]);
    MoveResult r = runMove();
    if (r == ARRIVED) Serial.println("ok");
    else printResult(r);
    return;
  }
  float val = 0;
  if (cmd && strchr("bsewghk", cmd) && !parseNum(args, val)) { Serial.println("err need a number, e.g. s 100"); return; }
  int uj = -1;
  bool guarded = true;
  if (cmd == 'c') {
    for (int i = 0; i < CLAW; i++) setJoint(i, jointFromServo(i, 90));
    setJoint(CLAW, 0);
  } else if (cmd == 'f' || cmd == 'g') {
    setJoint(CLAW, cmd == 'f' ? 0 : val);
  } else if (cmd == 'h') {
    if (val <= 0 || val > GRIP_MAX_MM) { Serial.println("err need the object's width: h 1-44 (mm)"); return; }
    setJoint(CLAW, max(0.0f, val - GRIP_SQUEEZE_MM));
  } else if (cmd == 'k') {
    GRIP_CLOSED_DEG = constrain(val, 0.0f, 180.0f);
    setJoint(CLAW, 0);
  } else if (cmd == 'r') {
    setJoint(1, PARK_SHOULDER);
    setJoint(2, PARK_ELBOW);
    setJoint(3, PARK_WRIST);
  } else if (cmd == 'u') {                                               // u <joint> <us>
    for (int i = 0; i < N; i++) if (joints[i].key == args.charAt(0)) uj = i;
    String us = args.substring(1);
    us.trim();
    if (uj < 0 || !parseNum(us, val)) { Serial.println("err need: u <b|s|e|w|g> <us>, e.g. u s 1500"); return; }
    val = constrain(val, (float)joints[uj].minUs, (float)joints[uj].maxUs);
    joints[uj].goal = (val - joints[uj].minUs) * 180.0f / (joints[uj].maxUs - joints[uj].minUs);
    guarded = false;
  } else {
    bool found = false;
    for (int i = 0; i < CLAW; i++) if (joints[i].key == cmd) { setJoint(i, val); found = true; }
    if (!found) { Serial.println("unknown command: b s e w g h r i t c f k u p m ? x"); return; }
  }
  printResult(runMove(guarded));
  if (cmd == 'f') squeezing = false;                                     // hold the exact angle for fitting
  if (cmd == 'k') Serial.printf("GRIP_CLOSED_DEG = %.1f (kept on the ESP32)\n", GRIP_CLOSED_DEG);
  if (uj >= 0) Serial.printf("%s at %d us (servo %.1f deg; raw: no limits, no guard)\n", joints[uj].name, pulseUs(uj, joints[uj].cur), joints[uj].cur);
  printPos("angles b s e w | claw mm:");
}

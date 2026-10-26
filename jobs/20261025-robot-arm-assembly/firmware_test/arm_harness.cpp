// Scripted serial sessions through arm_test.ino, compiled for the PC against the shim in shim/.
// Each "boot" is a fresh copy of the sketch's globals (its own namespace) while the NVS store is shared, so a
// power cycle is: start the next namespace. Prints PASS / FAIL per check and exits 1 if any check failed.
// Build and run: see test_firmware.py (g++ -std=c++11 or c++23 -Ishim -DARM_INO='"<path>/arm_test.ino"').
#include "ESP32Servo.h"
#include "Preferences.h"
#include <cmath>
#include <map>
#include <string>

unsigned long g_ms = 0;
SerialShim Serial;
int ESP32PWM::timers = 0;
std::map<std::string, std::string> Preferences::store;
int Preferences::puts = 0;

#define BOOT(ns) namespace ns {
BOOT(b1)
#include ARM_INO
}
BOOT(b2)
#include ARM_INO
}
BOOT(b3)
#include ARM_INO
}
BOOT(b4)
#include ARM_INO
}
BOOT(b5)
#include ARM_INO
}
BOOT(b6)
#include ARM_INO
}
BOOT(b7)
#include ARM_INO
}
BOOT(b8)
#include ARM_INO
}
BOOT(b9)
#include ARM_INO
}
BOOT(b10)
#include ARM_INO
}
BOOT(b11)
#include ARM_INO
}
BOOT(b12)
#include ARM_INO
}

static int fails = 0, passes = 0;
static void check(bool ok, const std::string &what) {
  std::printf("  %s  %s\n", ok ? "PASS" : "FAIL", what.c_str());
  if (ok) passes++; else fails++;
}
static std::string fmt(const char *f, ...) {
  char b[512];
  va_list a;
  va_start(a, f);
  std::vsnprintf(b, sizeof b, f, a);
  va_end(a);
  return b;
}
static bool near(double a, double b, double tol) { return std::fabs(a - b) <= tol; }
static bool contains(const std::string &hay, const std::string &needle) { return hay.find(needle) != std::string::npos; }

// Feed timed input (ms after now, text), then run loop() until it is consumed and handled.
template <class F> static void session(F loopfn, std::vector<std::pair<unsigned long, std::string> > in) {
  unsigned long t0 = g_ms;
  for (auto &c : in) Serial.at(t0 + c.first, c.second);
  for (int guard = 0; guard < 2000000 && !Serial.idle(); guard++) {
    size_t p = Serial.pos;
    unsigned long m = g_ms;
    loopfn();
    if (Serial.pos == p && g_ms == m) g_ms += 1;                 // nothing arrived yet: let time pass
  }
  for (int i = 0; i < 5; i++) loopfn();                           // a command still waiting in the queue
}
// Let time pass with nothing typed (loop() runs every millisecond).
template <class F> static void idle_for(F loopfn, unsigned long ms) {
  unsigned long end = g_ms + ms;
  while (g_ms < end) { loopfn(); g_ms += 1; }
}
static std::string out_since(size_t mark) { return Serial.log.substr(mark); }
static void reset_world() {
  Serial = SerialShim();
  Preferences::store.clear();
  Preferences::puts = 0;
  g_ms = 0;
}
static double usToDeg(int us) { return (us - 500) * 180.0 / 2000.0; }

// Ideal trapezoid (servo degrees), independent of the sketch: speed V, acceleration A, way D, at time t
static double ideal(double D, double t, double V = 66.7, double A = 250.0) {
  double da = V * V / A, T = D >= da ? D / V + V / A : 2 * std::sqrt(D / A);
  if (t >= T) return D;
  double ta = std::min(V / A, T / 2), v = A * ta;
  if (t < ta) return 0.5 * A * t * t;
  if (t < T - ta) return 0.5 * A * ta * ta + v * (t - ta);
  return D - 0.5 * A * (T - t) * (T - t);
}
static double idealTime(double D, double V = 66.7, double A = 250.0) {
  return D >= V * V / A ? D / V + V / A : 2 * std::sqrt(D / A);
}

#define POSE(ns) std::printf("    -> joints b %.2f s %.2f e %.2f w %.2f claw %.2f mm | pulses %d %d %d %d %d us\n", \
  ns::jointNow(0), ns::jointNow(1), ns::jointNow(2), ns::jointNow(3), ns::jointNow(4), ns::joints[0].servo.us, \
  ns::joints[1].servo.us, ns::joints[2].servo.us, ns::joints[3].servo.us, ns::joints[4].servo.us)

int main() {
  // ------------------------------------------------------------------------------------------------------------
  std::printf("== Joint table, first boot, start-up order (SYS-11)\n");
  reset_world();
  b1::setup();
  int pins[] = {13, 32, 27, 26, 25};
  bool ok = true;
  for (int i = 0; i < 5; i++) ok = ok && b1::joints[i].servo.pin == pins[i];
  check(ok, "pins: base 13, shoulder 32, elbow 27, wrist 26, claw 25");
  int order[] = {4, 3, 2, 1, 0};
  ok = true;
  for (int k = 1; k < 5; k++) ok = ok && b1::joints[order[k]].servo.attach_ms - b1::joints[order[k - 1]].servo.attach_ms >= 400;
  check(ok, fmt("attach order claw, wrist, elbow, shoulder, base, 400 ms apart (at %ld %ld %ld %ld %ld ms)",
                b1::joints[4].servo.attach_ms, b1::joints[3].servo.attach_ms, b1::joints[2].servo.attach_ms,
                b1::joints[1].servo.attach_ms, b1::joints[0].servo.attach_ms));
  check(b1::joints[0].servo.first_us == 1500 && b1::joints[1].servo.first_us == 1500 && b1::joints[2].servo.first_us == 1500 &&
        b1::joints[3].servo.first_us == 1500 && b1::joints[4].servo.first_us == 722,
        "first boot: arm servos at their centre (1500 us), claw at its closed angle 20 deg (722 us)");
  check(near(b1::jointNow(0), 0, 1e-4) && near(b1::jointNow(1), 90, 1e-4) && near(b1::jointNow(2), -60, 1e-4) &&
        near(b1::jointNow(3), 0, 1e-4) && near(b1::jointNow(4), 0, 1e-4),
        "servo centres = joints (0, 90, -60, 0) and the claw closed: the horn-fitting pose of BUILD_GUIDE 4");

  std::printf("== Elbow window -150..+30 (SYS-03) and the other limits\n");
  session(b1::loop, {{0, "e -150\n"}});
  check(b1::joints[2].servo.us == 500 && near(b1::jointNow(2), -150, 0.01), fmt("e -150 -> servo 0 deg (%d us)", b1::joints[2].servo.us));
  session(b1::loop, {{0, "e -170\n"}});
  check(near(b1::jointNow(2), -150, 0.01), "e -170 is held at -150");
  session(b1::loop, {{0, "e 30\n"}});
  check(b1::joints[2].servo.us == 2500 && near(b1::jointNow(2), 30, 0.01), fmt("e 30 -> servo 180 deg (%d us)", b1::joints[2].servo.us));
  session(b1::loop, {{0, "e 60\n"}});
  check(near(b1::jointNow(2), 30, 0.01), "e 60 is held at 30");
  session(b1::loop, {{0, "e 0\n"}, {5000, "s 60\n"}, {10000, "b -45\n"}, {15000, "w -30\n"}});
  POSE(b1);
  check(b1::joints[2].servo.us == 2167 && b1::joints[1].servo.us == 1167 && b1::joints[0].servo.us == 1000 && b1::joints[3].servo.us == 1167,
        "e 0 -> servo 150 (2167 us), s 60 -> servo 60, b -45 -> servo 45, w -30 -> servo 60");
  session(b1::loop, {{0, "b -120\n"}, {5000, "w 100\n"}, {10000, "s -10\n"}});
  check(near(b1::jointNow(0), -90, 0.01) && near(b1::jointNow(3), 90, 0.01) && near(b1::jointNow(1), 0, 0.01),
        "b -120 -> -90, w 100 -> 90, s -10 -> 0 (limits)");
  reset_world();
  b2::joints[2].dir = -1;                    // an elbow servo that turns the other way
  b2::setup();
  session(b2::loop, {{0, "e -150\n"}});
  check(b2::joints[2].servo.us == 2500 && near(b2::jointNow(2), -150, 0.01), "elbow dir -1: e -150 -> servo 180 deg; the window is the same");

  // ------------------------------------------------------------------------------------------------------------
  std::printf("== Speed profile (SYS-06): trapezoid at 250 deg/s2 to 66.7 deg/s, whole-us pulses\n");
  reset_world();
  b3::setup();
  session(b3::loop, {{0, "r\n"}});                         // upright first
  b3::joints[1].servo.log.clear();
  unsigned long t0 = g_ms;
  session(b3::loop, {{0, "s 30\n"}});
  auto &L = b3::joints[1].servo.log;
  double maxErr = 0, maxStep = 0, maxAcc = 0;
  for (size_t k = 0; k < L.size(); k++) {
    double t = (L[k].ms - t0) / 1000.0, pos = 90 - usToDeg(L[k].us);   // servo degrees covered (shoulder dir +1)
    maxErr = std::max(maxErr, std::fabs(pos - ideal(60, t)));
    if (k > 0) maxStep = std::max(maxStep, std::fabs(usToDeg(L[k].us) - usToDeg(L[k - 1].us)));
  }
  for (size_t k = 8; k < L.size(); k += 1) {               // acceleration from positions 4 steps (80 ms) apart: the
    double a = (usToDeg(L[k].us) - 2 * usToDeg(L[k - 4].us) + usToDeg(L[k - 8].us)) / (0.08 * 0.08);   // 1 us rounding
    maxAcc = std::max(maxAcc, std::fabs(a));               // (0.09 deg) then adds at most about 28 deg/s2
  }
  double T = (L.back().ms - t0) / 1000.0;
  check(maxErr <= 0.1, fmt("s 90 -> 30 follows the ideal trapezoid within %.3f deg (<= 0.1)", maxErr));
  check(near(T, idealTime(60), 0.021), fmt("it takes %.3f s; the ideal profile takes %.3f s", T, idealTime(60)));
  check(maxStep <= 66.7 * 0.02 + 0.1, fmt("largest step %.3f deg per 20 ms (66.7 deg/s cruise = 1.334)", maxStep));
  check(maxAcc <= 250 * 1.15, fmt("largest acceleration %.0f deg/s2 (limit 250; 80 ms differences of 1 us pulses)", maxAcc));
  check(std::fabs(usToDeg(L[0].us) - 90) < 0.1, fmt("first step moves %.3f deg: no velocity step at the start", 90 - usToDeg(L[0].us)));
  b3::joints[1].servo.log.clear();
  t0 = g_ms;
  session(b3::loop, {{0, "s 29\n"}});
  T = (b3::joints[1].servo.log.back().ms - t0) / 1000.0;
  check(near(T, idealTime(1), 0.021), fmt("a 1 deg move is a triangle: %.3f s (ideal %.3f s)", T, idealTime(1)));
  b3::joints[1].servo.log.clear();
  session(b3::loop, {{0, "s 29.3\n"}});
  check(b3::joints[1].servo.us == 500 + (int)std::lround(2000 * 29.3 / 180) && contains(Serial.log, "29.3 0.0 0.0"),
        fmt("sub-degree: s 29.3 -> %d us, reported 29.3", b3::joints[1].servo.us));
  for (int i = 0; i < 5; i++) b3::joints[i].servo.log.clear();
  session(b3::loop, {{0, "m 30 60 -40 -20 20\n"}});
  unsigned long last[5];
  for (int i = 0; i < 5; i++) last[i] = b3::joints[i].servo.log.empty() ? 0 : b3::joints[i].servo.log.back().ms;
  check(last[0] == last[1] && last[1] == last[2] && last[2] == last[3] && last[3] == last[4],
        fmt("m: every joint's last step at the same time (%lu %lu %lu %lu %lu ms)", last[0], last[1], last[2], last[3], last[4]));

  // ------------------------------------------------------------------------------------------------------------
  std::printf("== x and the queue mid-move (review 02 A1, A11)\n");
  session(b3::loop, {{0, "r\n"}});
  session(b3::loop, {{0, "s 30\n"}, {400, "x\n"}});
  POSE(b3);
  double stopped = b3::jointNow(1);
  int stoppedUs = b3::joints[1].servo.us;
  check(stopped < 89 && stopped > 30, fmt("x stopped the shoulder part-way, at %.1f", stopped));
  session(b3::loop, {{0, "p\n"}, {100, "?\n"}});
  check(b3::joints[1].servo.us == stoppedUs, "p and ? move nothing");
  session(b3::loop, {{0, "w 10\n"}});
  check(b3::joints[1].servo.us == stoppedUs && near(b3::jointNow(3), 10, 0.01), "w 10 moves only the wrist: the stopped move doesn't resume");
  size_t mark = Serial.log.size();
  session(b3::loop, {{0, "x\n"}});
  check(contains(out_since(mark), "idle"), "x with nothing moving answers idle");
  session(b3::loop, {{0, "s 120\n"}, {300, "?\nx\n"}});
  check(b3::jointNow(1) < 119 && contains(Serial.log, "pos "), "? during a move answers at once, and the x behind it still stops");
  session(b3::loop, {{0, "s 60\n"}, {100, "e -50\n"}, {150, "w 20\n"}});
  check(near(b3::jointNow(1), 60, 0.01) && near(b3::jointNow(2), -50, 0.01) && near(b3::jointNow(3), 10, 0.01) &&
        contains(Serial.log, "err busy"), "a command typed during a move waits; a second one gets err busy");
  session(b3::loop, {{0, "m 0 90 -60 0 10\n"}, {100, "s 90\n"}, {200, "x\n"}});
  check(b3::joints[1].goal == b3::joints[1].cur && b3::jointNow(1) < 90, "x stops m and drops the command waiting behind it");

  // ------------------------------------------------------------------------------------------------------------
  std::printf("== Guard: desk and base\n");
  reset_world();
  b4::setup();
  session(b4::loop, {{0, "e 0\n"}, {5000, "s 0\n"}});
  check(near(b4::jointNow(1), 0, 0.01) && near(b4::jointNow(2), 0, 0.01), "the arm straight out, level: allowed");
  double elim = 0;                                         // the guard's own limit for this path, from guardMargins
  for (double e = 0; e > -90; e -= 0.01) {
    float d, bm;
    b4::guardMargins(0, 0, (float)e, 0, 0, d, bm);
    if (d < 0 || bm < 0) { elim = e; break; }
  }
  b4::joints[2].servo.log.clear();
  mark = Serial.log.size();
  session(b4::loop, {{0, "e -90\n"}});
  POSE(b4);
  auto &E = b4::joints[2].servo.log;
  double lastStep = E.size() > 1 ? std::fabs(usToDeg(E[E.size() - 1].us) - usToDeg(E[E.size() - 2].us)) : 0;
  check(contains(out_since(mark), "blocked: desk"), "s 0 then e -90: blocked: desk");
  check(b4::jointNow(2) >= elim - 0.01 && b4::jointNow(2) <= elim + 0.6,
        fmt("it ends at e %.2f, just short of the guard's limit %.2f", b4::jointNow(2), elim));
  check(lastStep < 0.3, fmt("and it ramps down to that point: last step %.3f deg (cruise 1.33)", lastStep));
  mark = Serial.log.size();
  session(b4::loop, {{0, "m 0 0 -90 0 0\n"}});
  std::string o = out_since(mark);
  check(contains(o, "blocked: desk") && !contains(o, "\nok"), "m into the desk: one reply, blocked: desk");
  session(b4::loop, {{0, "e 0\n"}});
  check(near(b4::jointNow(2), 0, 0.01), "moving away from the desk works");
  session(b4::loop, {{0, "s 90\n"}, {5000, "e -150\n"}, {10000, "w -30\n"}, {15000, "s 60\n"}});
  POSE(b4);
  mark = Serial.log.size();
  session(b4::loop, {{0, "s 15\n"}});
  POSE(b4);
  check(contains(out_since(mark), "blocked: base") && b4::jointNow(1) > 56 && b4::jointNow(1) < 59,
        fmt("elbow folded -150: lowering the shoulder stops at s %.1f with blocked: base (the claw by the base wall)", b4::jointNow(1)));
  session(b4::loop, {{0, "s 90\n"}});
  check(near(b4::jointNow(1), 90, 0.01), "and back up is allowed");
  // a pose already too close (restored from NVS) may only move to get clearer
  reset_world();
  {
    float p[8] = {90, 0, 105, 90, 20, 20, 1, 20};          // servo angles: shoulder 0, elbow -45, wrist 0
    Preferences::store["pose2"] = std::string((const char *)p, sizeof p);
  }
  b5::setup();
  float dm0, bm0;
  b5::guardMargins(0, b5::jointNow(1), b5::jointNow(2), b5::jointNow(3), 0, dm0, bm0);
  std::printf("    restored at s %.0f e %.0f w %.0f: desk margin %.1f mm\n", b5::jointNow(1), b5::jointNow(2), b5::jointNow(3), dm0);
  session(b5::loop, {{0, "e -55\n"}});
  check(near(b5::jointNow(2), -45, 0.01) && dm0 < 0, "from a pose already too close, e -55 (closer) is refused");
  session(b5::loop, {{0, "b 30\n"}, {4000, "e -20\n"}});
  check(near(b5::jointNow(0), 30, 0.01) && near(b5::jointNow(2), -20, 0.01), "b 30 (no closer) and e -20 (clearer) are allowed");

  // ------------------------------------------------------------------------------------------------------------
  std::printf("== Holding (SYS-11): h <width>, squeeze limit, ease-off\n");
  reset_world();
  b6::setup();
  session(b6::loop, {{0, "r\n"}, {5000, "g 40\n"}});
  mark = Serial.log.size();
  session(b6::loop, {{0, "h 20\n"}});
  check(near(b6::jointNow(4), 18.5, 0.06), fmt("h 20 closes to 18.5 mm (%.2f)", b6::jointNow(4)));
  idle_for(b6::loop, 1900);
  check(near(b6::jointNow(4), 18.5, 0.06), "still squeezing 1.9 s later");
  idle_for(b6::loop, 200);
  double eased = 18.5 + 1.5 / b6::DEG_PER_MM;
  check(near(b6::jointNow(4), eased, 0.06) && contains(out_since(mark), "claw eased off to 19.0 mm"),
        fmt("after 2 s it eases off 1.5 deg, to %.2f mm, and says so", b6::jointNow(4)));
  idle_for(b6::loop, 10000);
  check(near(b6::jointNow(4), eased, 0.06), "and holds there: one ease-off per squeeze");
  session(b6::loop, {{0, "g 40\n"}});
  session(b6::loop, {{0, "h 20\n"}});
  idle_for(b6::loop, 1000);
  b6::joints[0].servo.log.clear();
  b6::joints[4].servo.log.clear();
  session(b6::loop, {{0, "b 90\n"}});                       // 90 deg of yaw: 1.6 s, the squeeze limit falls inside it
  bool during = !b6::joints[4].servo.log.empty() && b6::joints[4].servo.log[0].ms < b6::joints[0].servo.log.back().ms;
  check(near(b6::jointNow(4), eased, 0.06) && during && near(b6::jointNow(0), 90, 0.01),
        "the ease-off also happens during a move that leaves the claw alone");
  session(b6::loop, {{0, "g 44\n"}});
  idle_for(b6::loop, 3000);
  check(near(b6::jointNow(4), 44, 0.06), "an opening move doesn't ease off");
  session(b6::loop, {{0, "g 0\n"}});
  idle_for(b6::loop, 3000);
  check(near(b6::jointNow(4), 1.5 / b6::DEG_PER_MM, 0.06), "g 0 squeezes at most 2 s too, then eases off 0.5 mm");
  session(b6::loop, {{0, "g 30\n"}, {3000, "f\n"}});
  idle_for(b6::loop, 3000);
  check(near(b6::jointNow(4), 1.5 / b6::DEG_PER_MM, 0.06), "f closes like g 0, squeeze limit included");
  mark = Serial.log.size();
  int clawUs = b6::joints[4].servo.us;
  session(b6::loop, {{0, "h 0\n"}, {10, "h 50\n"}, {20, "h abc\n"}});
  check(b6::joints[4].servo.us == clawUs && contains(out_since(mark), "err need the object's width"),
        "h 0, h 50, h abc are refused: the claw doesn't move");

  // ------------------------------------------------------------------------------------------------------------
  std::printf("== Rest and the idle park (SYS-02)\n");
  session(b6::loop, {{0, "m 20 40 -70 -30 10\n"}});
  session(b6::loop, {{0, "r\n"}});
  POSE(b6);
  check(near(b6::jointNow(1), 90, 0.01) && near(b6::jointNow(2), 0, 0.01) && near(b6::jointNow(3), 0, 0.01) &&
        near(b6::jointNow(0), 20, 0.01) && near(b6::jointNow(4), 10, 0.06),
        "r: shoulder 90, elbow 0, wrist 0 (upright); base and claw stay");
  session(b6::loop, {{0, "s 45\n"}});
  mark = Serial.log.size();
  idle_for(b6::loop, 59000);
  check(near(b6::jointNow(1), 45, 0.01), "no park before 60 s");
  idle_for(b6::loop, 5000);
  check(near(b6::jointNow(1), 90, 0.01) && contains(out_since(mark), "idle 60 s: parking"), "after 60 s without a command the arm parks and says so");
  size_t mark2 = Serial.log.size();
  idle_for(b6::loop, 120000);
  check(Serial.log.size() == mark2, "it parks once: nothing more while it stays idle");
  session(b6::loop, {{0, "s 45\n"}});
  for (int k = 0; k < 4; k++) { idle_for(b6::loop, 40000); session(b6::loop, {{0, "?\n"}}); }
  check(near(b6::jointNow(1), 45, 0.01), "? every 40 s counts as a command: no park");
  mark = Serial.log.size();
  session(b6::loop, {{0, "i 0\n"}});
  idle_for(b6::loop, 200000);
  check(near(b6::jointNow(1), 45, 0.01) && contains(out_since(mark), "idle park off"), "i 0: never parks");
  mark = Serial.log.size();
  session(b6::loop, {{0, "i -1\n"}, {10, "i abc\n"}, {20, "i\n"}});
  check(contains(out_since(mark), "err need: i <seconds>") && contains(out_since(mark), "idle park off"), "i -1 and i abc refused; i shows the setting");
  b7::setup();                                              // power cycle: i 0 is kept
  idle_for(b7::loop, 200000);
  check(b7::idleParkS == 0 && near(b7::jointNow(1), 45, 0.01), "i 0 survives a power cycle");
  session(b7::loop, {{0, "i 5\n"}});
  idle_for(b7::loop, 6000);
  check(near(b7::jointNow(1), 90, 0.01), "i 5: parks after 5 s");

  // ------------------------------------------------------------------------------------------------------------
  std::printf("== Trims (SYS-07): set, show, save; applied before the limits and the guard\n");
  reset_world();
  b8::setup();
  session(b8::loop, {{0, "r\n"}});
  int s0 = b8::joints[1].servo.us;
  mark = Serial.log.size();
  session(b8::loop, {{0, "t s 2\n"}});
  check(b8::joints[1].servo.us - s0 == 22 && near(b8::jointNow(1), 90, 1e-3),
        fmt("t s 2: the shoulder servo turns 2 deg (%+d us) while the joint still reads 90", b8::joints[1].servo.us - s0));
  check(contains(out_since(mark), "trims b 0.0 s 2.0 e 0.0 w 0.0 (not saved"), "t s 2 shows the trims, not saved yet");
  session(b8::loop, {{0, "t e -3.5\n"}, {5000, "t save\n"}});
  check(Preferences::store.count("trim") == 1 && contains(Serial.log, "e -3.5 w 0.0 (saved)"), "t save keeps them in NVS");
  mark = Serial.log.size();
  session(b8::loop, {{0, "t q 2\n"}, {10, "t s 20\n"}, {20, "t s abc\n"}, {30, "t\n"}});
  check(contains(out_since(mark), "err need: t <b|s|e|w>") && b8::joints[1].trim == 2, "t q 2, t s 20, t s abc refused; t shows");
  session(b8::loop, {{0, "e 30\n"}});
  check(near(b8::jointNow(2), 30, 0.01), "e trim -3.5: the elbow still reaches +30");
  session(b8::loop, {{0, "e -150\n"}});
  check(near(b8::jointNow(2), -146.5, 0.01) && b8::joints[2].servo.us == 500,
        fmt("but its servo end now stops it at %.1f: the trim shortens that end", b8::jointNow(2)));
  session(b8::loop, {{0, "e 0\n"}, {5000, "t s 7\n"}});
  int last_us[5];
  for (int i = 0; i < 5; i++) last_us[i] = b8::joints[i].servo.us;
  b9::setup();                                              // power cycle with an unsaved shoulder trim (7, saved 2)
  ok = true;
  for (int i = 0; i < 5; i++) ok = ok && b9::joints[i].servo.first_us == last_us[i];
  check(ok, "power cycle: every servo restarts at its last pulse (no jump), unsaved trim or not");
  check(b9::joints[1].trim == 2 && b9::joints[2].trim == -3.5f && near(b9::jointNow(1), 95, 0.01),
        "the saved trims come back (s 2, e -3.5); the unsaved 7 is gone, so s reads 95");
  // the guard works on the trimmed (true) angle: the desk limit is the same joint angle whatever the trim
  session(b9::loop, {{0, "t s 0\n"}, {5000, "e 0\n"}, {10000, "s 0\n"}, {15000, "e -90\n"}});
  double lim0 = b9::jointNow(2);
  session(b9::loop, {{0, "e 0\n"}, {5000, "t e 6\n"}, {10000, "e -90\n"}});
  check(near(b9::jointNow(2), lim0, 0.6) && b9::joints[2].trim == 6,
        fmt("with an elbow trim of 6 the guard stops the elbow at %.1f, as at %.1f without", b9::jointNow(2), lim0));

  // ------------------------------------------------------------------------------------------------------------
  std::printf("== NVS: pose restore, the previous sketch's pose, a changed claw set-up, a pose outside the limits\n");
  reset_world();
  {
    float p[8] = {90, 45, 100, 80, 10, 23, 1, 20};          // previous sketch: servo angles, claw in mm, trim 23
    Preferences::store["pose"] = std::string((const char *)p, sizeof p);
  }
  b10::setup();
  double clawSv = 23 + b10::DEG_PER_MM * 10;
  check(b10::joints[4].servo.first_us == 500 + (int)std::lround(2000 * clawSv / 180) && b10::joints[2].servo.first_us == 1611 &&
        near(b10::jointNow(2), -50, 0.01) && b10::GRIP_CLOSED_DEG == 23,
        fmt("previous sketch's pose: claw back at servo %.1f deg (%d us), elbow servo 100 = joint -50, k trim kept",
            clawSv, b10::joints[4].servo.first_us));
  session(b10::loop, {{0, "k 25\n"}});
  check(b10::GRIP_CLOSED_DEG == 25 && near(b10::jointNow(4), 0, 0.01) && contains(Serial.log, "GRIP_CLOSED_DEG = 25.0"),
        "k 25: new closed angle, claw closed at it");
  b11::GRIP_OPEN_DIR = -1;                                  // re-flashed with the other claw direction
  b11::GRIP_CLOSED_DEG = 160;
  b11::joints[2].hi = 20;                                   // and a narrower elbow window
  session(b10::loop, {{0, "r\n"}, {5000, "e 30\n"}});
  int el_us = b10::joints[2].servo.us, claw_us = b10::joints[4].servo.us;
  mark = Serial.log.size();
  b11::setup();
  check(b11::GRIP_CLOSED_DEG == 160 && b11::joints[4].servo.first_us == claw_us,
        "re-flash with GRIP_OPEN_DIR -1: the k trim is dropped, the claw servo restarts where it was");
  check(b11::joints[2].servo.first_us == el_us && near(b11::jointNow(2), 20, 0.01) &&
        contains(out_since(mark), "outside the joint limits"),
        "elbow saved at +30, limit now +20: it restarts at +30, then moves slowly to +20");

  // ------------------------------------------------------------------------------------------------------------
  std::printf("== Strict numbers (review 02 A3), u end-stop test, c\n");
  reset_world();
  b12::setup();
  mark = Serial.log.size();
  session(b12::loop, {{0, "s\n"}, {10, "s abc\n"}, {20, "s nan\n"}, {30, "k\n"}, {40, "b inf\n"},
                      {50, "m nan 90 -60 0 0\n"}, {60, "m 1 2 3\n"}, {70, "s 100 200\n"}, {80, "z\n"}});
  o = out_since(mark);
  check(near(b12::jointNow(1), 90, 1e-3) && b12::GRIP_CLOSED_DEG == 20 && near(b12::jointNow(0), 0, 1e-3) &&
        contains(o, "err need a number") && contains(o, "err not a number") && contains(o, "err need: m b s e w mm") &&
        contains(o, "unknown command"), "bad numbers and unknown commands are refused; nothing moved");
  session(b12::loop, {{0, "t s 3\n"}, {5000, "t w -4\n"}, {10000, "s 60\n"}, {15000, "c\n"}});
  check(b12::joints[0].servo.us == 1500 && b12::joints[1].servo.us == 1500 && b12::joints[2].servo.us == 1500 &&
        b12::joints[3].servo.us == 1500 && near(b12::jointNow(4), 0, 0.01), "c: every servo at 1500 us whatever the trims, claw closed");
  session(b12::loop, {{0, "u s 1234\n"}, {6000, "u e 3000\n"}, {12000, "u q 1500\n"}, {12100, "u s\n"}});
  check(b12::joints[1].servo.us == 1234 && b12::joints[2].servo.us == 2500 && contains(Serial.log, "err need: u <b|s|e|w|g>"),
        "u s 1234 -> 1234 us, u e 3000 -> 2500 us (maxUs), u q / u s refused");
  session(b12::loop, {{0, "u s 500\n"}});
  mark = Serial.log.size();
  session(b12::loop, {{0, "e -150\n"}});
  double guardedStop = b12::jointNow(2);
  session(b12::loop, {{0, "u e 500\n"}});
  check(contains(out_since(mark), "blocked:") && guardedStop > -140 && b12::joints[2].servo.us == 500,
        fmt("u ignores the guard: e -150 stops at %.0f (blocked), u e 500 goes to servo 0 (end-stop test, no horns yet)", guardedStop));

  std::printf("\n%s: %d passed, %d failed\n", fails ? "SOME ARM CHECKS FAILED" : "ALL ARM CHECKS PASSED", passes, fails);
  return fails ? 1 : 0;
}

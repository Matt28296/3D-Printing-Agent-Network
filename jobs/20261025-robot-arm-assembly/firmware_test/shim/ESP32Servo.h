// Stand-in for ESP32Servo 3.x: attach() clamps min/max to 500..2500 like the library, writeMicroseconds() clamps
// to them and is ignored before attach(). Every servo logs its pulses with their times, and attach() its time,
// so a harness can check the speed profile and the start-up order.
#pragma once
#include "Arduino.h"
struct ESP32PWM {
  static int timers;
  static void allocateTimer(int) { timers++; }
};
struct PulseLog { unsigned long ms; int us; };
class Servo {
 public:
  int pin = -1, mn = 544, mx = 2400, us = -1, first_us = -1;
  long attach_ms = -1;
  std::vector<PulseLog> log;
  void setPeriodHertz(int) {}
  int attach(int p, int lo, int hi) {
    pin = p; mn = lo < 500 ? 500 : lo; mx = hi > 2500 ? 2500 : hi; attach_ms = (long)g_ms;
    return 1;
  }
  void writeMicroseconds(int v) {
    if (pin < 0) return;                    // not attached: the library ignores it
    if (v < mn) v = mn;
    else if (v > mx) v = mx;
    us = v;
    if (first_us < 0) first_us = v;
    log.push_back(PulseLog{g_ms, v});
  }
};

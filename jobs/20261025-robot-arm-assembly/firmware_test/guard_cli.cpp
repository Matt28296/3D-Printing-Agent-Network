// The sketch's own guard as a filter: each stdin line "yaw shoulder elbow wrist gap_mm" (joint degrees) gives
// one stdout line "desk_margin base_margin" (mm beyond GUARD_CLEAR; < 0 = too close). Used by test_firmware.py
// to check that arm_test.ino and pc/arm_pc_control.py compute the same guard.
#include "ESP32Servo.h"
#include "Preferences.h"
#include <iostream>

unsigned long g_ms = 0;
SerialShim Serial;
int ESP32PWM::timers = 0;
std::map<std::string, std::string> Preferences::store;
int Preferences::puts = 0;
namespace sk {
#include ARM_INO
}
int main() {
  float yaw, s, e, w, g;
  while (std::cin >> yaw >> s >> e >> w >> g) {
    float d, b;
    sk::guardMargins(yaw, s, e, w, g, d, b);
    std::printf("%.4f %.4f\n", d, b);
  }
  return 0;
}

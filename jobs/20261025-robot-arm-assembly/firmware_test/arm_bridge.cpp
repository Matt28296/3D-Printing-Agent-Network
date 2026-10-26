// arm_test.ino behind a pipe, as a stand-in for the ESP32 on a serial port: each stdin line is a serial line to
// the sketch, its output goes to stdout. argv[1] = seconds of real time before setup() (a reset when the port
// opens). Moves take no real time: the sketch's clock only moves when it waits.
#include "ESP32Servo.h"
#include "Preferences.h"
#include <chrono>
#include <iostream>
#include <thread>

unsigned long g_ms = 0;
SerialShim Serial;
int ESP32PWM::timers = 0;
std::map<std::string, std::string> Preferences::store;
int Preferences::puts = 0;
namespace sk {
#include ARM_INO
}
int main(int argc, char **argv) {
  Serial.raw = true;
  double boot = argc > 1 ? std::atof(argv[1]) : 0;
  if (boot > 0) std::this_thread::sleep_for(std::chrono::milliseconds((long)(boot * 1000)));
  std::printf("ets Jun  8 2016 00:22:57\nrst:0x1 (POWERON_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)\n");   // ROM chatter
  sk::setup();
  std::fflush(stdout);
  std::string line;
  while (std::getline(std::cin, line)) {
    Serial.at(g_ms, line + "\n");
    while (Serial.available()) sk::loop();
    for (int i = 0; i < 3; i++) sk::loop();
    std::fflush(stdout);
  }
  return 0;
}

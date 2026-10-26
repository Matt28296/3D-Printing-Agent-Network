// Stand-in for the ESP32 Preferences (NVS) library: one store shared by every instance, so it survives a simulated
// power cycle (a fresh copy of the sketch's globals). getBytes() returns 0 unless the stored value has exactly the
// size asked for (the real one returns 0 when it is longer than the buffer). Counts writes.
#pragma once
#include <map>
#include "Arduino.h"
struct Preferences {
  static std::map<std::string, std::string> store;
  static int puts;
  bool begin(const char *, bool = false) { return true; }
  size_t putBytes(const char *k, const void *v, size_t n) {
    store[k] = std::string((const char *)v, n);
    puts++;
    return n;
  }
  size_t getBytes(const char *k, void *v, size_t n) {
    auto it = store.find(k);
    if (it == store.end() || it->second.size() != n) return 0;
    std::memcpy(v, it->second.data(), n);
    return n;
  }
};

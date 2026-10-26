// Host-side stand-in for the parts of the arduino-esp32 core that arm_test.ino uses, so the sketch can be
// compiled with g++ and driven by scripted serial sessions. It mirrors the real core where it matters:
// constrain() is the core's macro, min/max are std::min/std::max, String follows WString.cpp.
// Time is simulated: millis() only moves when the sketch calls delay(). Serial input arrives in timed chunks.
#pragma once
#include <algorithm>
#include <cmath>
#include <cstdarg>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <utility>
#include <vector>
using std::abs;
using std::max;
using std::min;
#define constrain(amt, low, high) ((amt) < (low) ? (low) : ((amt) > (high) ? (high) : (amt)))

extern unsigned long g_ms;                 // simulated millis()
inline void delay(unsigned long ms) { g_ms += ms; }
inline unsigned long millis() { return g_ms; }

class String {
 public:
  std::string s;
  String(const char *c = "") : s(c) {}
  String(const std::string &x) : s(x) {}
  void trim() {
    size_t a = s.find_first_not_of(" \t\r\n\f\v"), b = s.find_last_not_of(" \t\r\n\f\v");
    s = (a == std::string::npos) ? "" : s.substr(a, b - a + 1);
  }
  unsigned length() const { return (unsigned)s.size(); }
  char charAt(unsigned i) const { return i < s.size() ? s[i] : 0; }
  String substring(unsigned left) const { return substring(left, (unsigned)s.size()); }
  String substring(unsigned left, unsigned right) const {      // WString.cpp: swap, clamp
    if (left > right) std::swap(left, right);
    if (left >= s.size()) return String("");
    if (right > s.size()) right = (unsigned)s.size();
    return String(s.substr(left, right - left));
  }
  bool operator==(const char *c) const { return s == c; }
  const char *c_str() const { return s.c_str(); }
};

// Serial: input arrives at simulated times; output goes to stdout, each line prefixed with the time unless raw.
struct SerialShim {
  std::string in;
  size_t pos = 0;
  std::vector<std::pair<unsigned long, std::string> > pending;   // (arrival ms, text)
  bool bol = true, raw = false;
  std::string log;                                                 // everything printed, for the checks
  void at(unsigned long ms, const std::string &text) { pending.push_back(std::make_pair(ms, text)); }
  void pump() {
    for (size_t i = 0; i < pending.size();) {
      if (pending[i].first <= g_ms) { in += pending[i].second; pending.erase(pending.begin() + i); }
      else i++;
    }
  }
  bool idle() { pump(); return pos >= in.size() && pending.empty(); }
  void begin(long) {}
  void setTimeout(unsigned long) {}
  int available() { pump(); return (int)(in.size() - pos); }
  int read() { pump(); return pos < in.size() ? (unsigned char)in[pos++] : -1; }
  String readStringUntil(char c) {
    pump();
    size_t e = in.find(c, pos);
    std::string r = in.substr(pos, e == std::string::npos ? std::string::npos : e - pos);
    pos = (e == std::string::npos) ? in.size() : e + 1;
    return String(r);
  }
  void out(const char *x) {
    for (const char *p = x; *p; p++) {
      if (bol && !raw) { std::printf("    [%7lu ms] ", g_ms); bol = false; }
      std::putchar(*p);
      log += *p;
      if (*p == '\n') bol = true;
    }
  }
  void print(const char *x) { out(x); }
  void println(const char *x = "") { out(x); out("\n"); }
  int printf(const char *f, ...) __attribute__((format(printf, 2, 3))) {
    char b[512];
    va_list a;
    va_start(a, f);
    int r = std::vsnprintf(b, sizeof b, f, a);
    va_end(a);
    out(b);
    return r;
  }
};
extern SerialShim Serial;

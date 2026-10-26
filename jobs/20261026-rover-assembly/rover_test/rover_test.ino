// Tracked rover: drive test + simple obstacle avoidance. ESP32 + TB6612FNG + HC-SR04.
// Board: "ESP32 Dev Module" on the arduino-esp32 3.x core (analogWrite needs 2.x or later). No extra libraries.
// Serial Monitor 115200, line ending "Newline".
// Commands: f b l r s | + - (speed, takes effect at once) | a (autonomous on/off: on the floor only, the
//   sensor looks forward and can't see a table edge) | d (print distance and battery voltage)
// Motor voltage: the 2S Li-ion pack (6.4-8.4 V) is above the N20s' 6 V rating, so the PWM cap follows the
// measured pack voltage (divider on GPIO34) and the average motor voltage stays at or below 6 V. When the
// pack reads below 6.4 V twice in a row (3.2 V per cell under load) the rover stops and won't drive again
// until it is restarted with a charged pack.

const int PWMA = 25, AIN1 = 26, AIN2 = 27;   // left motor
const int PWMB = 14, BIN1 = 33, BIN2 = 32;   // right motor
const int STBY = 13;
const int TRIG = 18, ECHO = 19;              // ECHO through a 1k/2k divider
const int VBAT_PIN = 34;                     // ADC1, input-only: 100k from the switched pack +, 33k to GND, 100 nF across the 33k
const float VBAT_DIV = (100.0f + 33.0f) / 33.0f;
const float VBAT_STOP = 6.4f;                // 3.2 V per cell under load
const float MOTOR_V = 6.0f;                  // N20 rating: the average motor voltage never goes above this
const int PWM_HZ = 20000;                    // above hearing; the TB6612 takes up to 100 kHz
const int STOP_CM = 15;
const int MIN_SPEED = 30;                    // %: at less the N20s may not start

int speedPct = 60;       // of the cap
bool autonomous = false;
int pwmCap = 182;        // 255 x 6.0 V / 8.4 V: safe for a full pack until the first reading
int dirL = 0, dirR = 0;  // last direction command, so + and - apply at once
unsigned long lastBatt = 0;
int lowReadings = 0;
bool battLow = false;    // latched: the pack needs charging
bool battUnknown = false;

float vbat() {
  uint32_t mv = 0;
  for (int i = 0; i < 8; i++) mv += analogReadMilliVolts(VBAT_PIN);
  return mv / 8.0f * VBAT_DIV / 1000.0f;
}

void motor(int pwmPin, int in1, int in2, int value) {   // value -255..255
  value = constrain(value, -255, 255);
  digitalWrite(in1, value > 0);
  digitalWrite(in2, value < 0);
  analogWrite(pwmPin, map(abs(value), 0, 255, 0, pwmCap));
}

void drive(int left, int right) {   // -100..100 % of the current speed
  int s = map(speedPct, 0, 100, 0, 255);
  motor(PWMA, AIN1, AIN2, left * s / 100);
  motor(PWMB, BIN1, BIN2, right * s / 100);
}

// Every direction change goes through here. A track that reverses stops for 80 ms first: straight from
// full forward to full reverse the back-EMF roughly doubles the current and jolts the gears and sprockets.
void go(int left, int right) {
  if (battLow && (left || right)) { left = right = 0; Serial.println("battery low: charge the pack, then restart"); }
  if ((long)left * dirL < 0 || (long)right * dirR < 0) { drive(0, 0); delay(80); }
  dirL = left; dirR = right;
  drive(left, right);
}

// cm; 999 = nothing in range (the module's ~38 ms no-echo pulse); -1 = no echo pulse at all (wiring or sensor fault).
long distanceCm() {
  unsigned long t = micros();
  while (digitalRead(ECHO) == HIGH) if (micros() - t > 60000) return -1;   // the last echo never ended
  digitalWrite(TRIG, LOW); delayMicroseconds(2);
  digitalWrite(TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  t = micros();
  while (digitalRead(ECHO) == LOW) if (micros() - t > 5000) return -1;    // the echo line never rose
  unsigned long t1 = micros();
  while (digitalRead(ECHO) == HIGH) if (micros() - t1 > 40000) break;
  unsigned long us = micros() - t1;
  return us >= 30000 ? 999 : (long)(us / 58);
}

void checkBattery() {
  float v = vbat();
  if (v < 3.0f) {                            // pack switched off (USB only) or no divider: keep the full-pack cap
    if (!battUnknown) Serial.println("battery not measured: pack off, or no divider on GPIO34");
    battUnknown = true; pwmCap = 182; lowReadings = 0;
    return;
  }
  battUnknown = false;
  pwmCap = constrain((int)(255 * MOTOR_V / v), 0, 255);
  lowReadings = v < VBAT_STOP ? lowReadings + 1 : 0;
  if (lowReadings >= 2 && !battLow) {        // twice in a row: a start-up sag alone doesn't stop it
    battLow = true; autonomous = false; go(0, 0);
    Serial.printf("battery %.2f V: low, motors off. Charge the pack\n", v);
  }
}

void setup() {
  Serial.begin(115200);
  int outs[] = {PWMA, AIN1, AIN2, PWMB, BIN1, BIN2, STBY, TRIG};
  for (int p : outs) pinMode(p, OUTPUT);
  pinMode(ECHO, INPUT);
  go(0, 0);                                  // first analogWrite: attaches PWMA and PWMB to the LEDC
#if ESP_ARDUINO_VERSION_MAJOR >= 3
  analogWriteFrequency(PWMA, PWM_HZ);        // core 3.x: per pin, after the first analogWrite
  analogWriteFrequency(PWMB, PWM_HZ);
#else
  analogWriteFrequency(PWM_HZ);              // core 2.x: every analogWrite pin
#endif
  digitalWrite(STBY, HIGH);
  checkBattery();
  Serial.println("rover_test ready: f b l r s + - a d");
}

void loop() {
  if (millis() - lastBatt >= 1000) { lastBatt = millis(); checkBattery(); }
  if (Serial.available()) {
    char c = Serial.read();
    switch (c) {
      case 'f': go(100, 100); break;
      case 'b': go(-100, -100); break;
      case 'l': go(-100, 100); break;
      case 'r': go(100, -100); break;
      case 's': go(0, 0); autonomous = false; break;
      case '+': speedPct = min(100, speedPct + 10); drive(dirL, dirR); break;
      case '-': speedPct = max(MIN_SPEED, speedPct - 10); drive(dirL, dirR); break;
      case 'a':
        if (battLow) Serial.println("battery low: charge the pack, then restart");
        autonomous = !autonomous && !battLow;
        if (!autonomous) go(0, 0);
        break;
      case 'd': {
        long d = distanceCm();
        if (d < 0) Serial.print("no echo pulse (check the HC-SR04 wiring)");
        else if (d == 999) Serial.print("nothing in range");
        else Serial.printf("%ld cm", d);
        Serial.printf(", battery %.2f V\n", vbat());
        break;
      }
      default: return;
    }
    Serial.printf("speed %d%%  autonomous %s\n", speedPct, autonomous ? "on" : "off");
  }
  if (autonomous) {
    long d = distanceCm();
    if (d < 0) { go(0, 0); autonomous = false; Serial.println("HC-SR04 gives no echo pulse: stopped (check TRIG/ECHO wiring)"); }
    else if (d < STOP_CM) {
      go(-100, -100); delay(300);
      go(100, -100); delay(400);   // turn right a little
    } else {
      go(100, 100);
    }
    delay(60);
  }
}

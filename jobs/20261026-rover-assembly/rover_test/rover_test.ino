// Tracked rover: drive test + simple obstacle avoidance. ESP32 + TB6612FNG + HC-SR04.
// Board: "ESP32 Dev Module". No extra libraries. Serial Monitor 115200, line ending "Newline".
// Commands: f b l r s | + - (speed) | a (autonomous on/off) | d (print distance)
// PWM is capped at 80 %: the 2S Li-ion pack (7.4-8.4 V) is above the N20s' 6 V rating.

const int PWMA = 25, AIN1 = 26, AIN2 = 27;   // left motor
const int PWMB = 14, BIN1 = 33, BIN2 = 32;   // right motor
const int STBY = 13;
const int TRIG = 18, ECHO = 19;              // ECHO through a 1k/2k divider
const int PWM_CAP = 204;                     // 80 % of 255
const int STOP_CM = 15;

int speedPct = 60;      // of the cap
bool autonomous = false;

void motor(int pwmPin, int in1, int in2, int value) {   // value -255..255
  value = constrain(value, -255, 255);
  digitalWrite(in1, value > 0);
  digitalWrite(in2, value < 0);
  analogWrite(pwmPin, map(abs(value), 0, 255, 0, PWM_CAP));
}

void drive(int left, int right) {   // -100..100 % of the current speed
  int s = map(speedPct, 0, 100, 0, 255);
  motor(PWMA, AIN1, AIN2, left * s / 100);
  motor(PWMB, BIN1, BIN2, right * s / 100);
}

long distanceCm() {
  digitalWrite(TRIG, LOW); delayMicroseconds(2);
  digitalWrite(TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG, LOW);
  long us = pulseIn(ECHO, HIGH, 25000);   // ~4 m max
  return us == 0 ? 999 : us / 58;
}

void setup() {
  Serial.begin(115200);
  int outs[] = {PWMA, AIN1, AIN2, PWMB, BIN1, BIN2, STBY, TRIG};
  for (int p : outs) pinMode(p, OUTPUT);
  pinMode(ECHO, INPUT);
  digitalWrite(STBY, HIGH);
  drive(0, 0);
  Serial.println("rover_test ready: f b l r s + - a d");
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    switch (c) {
      case 'f': drive(100, 100); break;
      case 'b': drive(-100, -100); break;
      case 'l': drive(-100, 100); break;
      case 'r': drive(100, -100); break;
      case 's': drive(0, 0); autonomous = false; break;
      case '+': speedPct = min(100, speedPct + 10); break;
      case '-': speedPct = max(20, speedPct - 10); break;
      case 'a': autonomous = !autonomous; if (!autonomous) drive(0, 0); break;
      case 'd': Serial.printf("%ld cm\n", distanceCm()); break;
      default: return;
    }
    Serial.printf("speed %d%%  autonomous %s\n", speedPct, autonomous ? "on" : "off");
  }
  if (autonomous) {
    long d = distanceCm();
    if (d < STOP_CM) {
      drive(-100, -100); delay(300);
      drive(100, -100); delay(400);   // turn right a little
    } else {
      drive(100, 100);
    }
    delay(60);
  }
}

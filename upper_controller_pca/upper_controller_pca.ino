/*
========================================
ESP32 UPPER CONTROLLER
========================================
- LCD Face Controller
- Dual Hand Controller
- Neck Controller
- UART Controlled
- Direct ESP32 GPIO Servo Control
========================================
*/

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Adafruit_PWMServoDriver.h>

// ====================================
// LCD
// ====================================

LiquidCrystal_I2C lcd(0x27, 16, 2);

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);

struct SmoothServo {

  int currentAngle;
  int targetAngle;

  float speed; // degrees per update
};

SmoothServo servos[16];

void initServo(int channel, int startAngle, float speed = 1.5) {

  servos[channel].currentAngle = startAngle;
  servos[channel].targetAngle  = startAngle;
  servos[channel].speed = speed;

  pwm.setPWM(channel, 0, angleToPulse(startAngle));
}

// LEFT ARM
#define L_GRIP     0
#define L_SHOULDER 1
#define L_ELBOW    2
#define L_BASE     3

// RIGHT ARM
#define R_GRIP     12
#define R_SHOULDER 13
#define R_ELBOW    14
#define R_BASE     15

// NECK
#define NECK       8

#define SERVOMIN 110
#define SERVOMAX 490
#define SERVO_FREQ 50

int angleToPulse(int angle) {
  angle = constrain(angle, 0, 180);
  return map(angle, 0, 180, SERVOMIN, SERVOMAX);
}

void moveServo(int channel, int targetAngle) {

  servos[channel].targetAngle = constrain(targetAngle, 0, 180);
}

void updateServos() {

  for (int i = 0; i < 16; i++) {

    float current = servos[i].currentAngle;
    float target  = servos[i].targetAngle;

    float diff = target - current;

    // close enough
    if (abs(diff) < 0.2)
      continue;

    // easing movement
    float step = diff * 0.12;

    // limit max speed
    if (step > servos[i].speed)
      step = servos[i].speed;

    if (step < -servos[i].speed)
      step = -servos[i].speed;

    // minimum movement
    if (step > 0 && step < 0.15)
      step = 0.15;

    if (step < 0 && step > -0.15)
      step = -0.15;

    current += step;

    servos[i].currentAngle = current;

    pwm.setPWM(i, 0, angleToPulse((int)current));
  }
}
unsigned long lastServoUpdate = 0;

#define LEFT_UP_ANGLE      30
#define LEFT_CENTER_ANGLE  90
#define LEFT_DOWN_ANGLE    150

#define RIGHT_UP_ANGLE      150
#define RIGHT_CENTER_ANGLE  110
#define RIGHT_DOWN_ANGLE    30

#define LEFT_GRIP_OPEN   60
#define LEFT_GRIP_CLOSE  100

#define RIGHT_GRIP_OPEN   70
#define RIGHT_GRIP_CLOSE  90

#define LEFT_SHOULDER_EXTEND 40
#define LEFT_SHOULDER_CENTER 150

#define LEFT_ELBOW_EXTEND 160
#define LEFT_ELBOW_CENTER 120

#define RIGHT_SHOULDER_EXTEND 160
#define RIGHT_SHOULDER_CENTER 120

#define RIGHT_ELBOW_EXTEND 180
#define RIGHT_ELBOW_CENTER 120

// ====================================
// LCD CHARS
// ====================================

byte eye_open[8] = {
  0b00000,
  0b00000,
  0b01110,
  0b10001,
  0b10101,
  0b10001,
  0b01110,
  0b00000
};

byte eye_closed[8] = {
  0b00000,
  0b00000,
  0b00000,
  0b11111,
  0b00000,
  0b11111,
  0b00000,
  0b00000
};

byte mouth_happy[8] = {
  0b00000,
  0b00000,
  0b10001,
  0b01110,
  0b00000,
  0b00000,
  0b00000,
  0b00000
};

byte mouth_neutral[8] = {
  0b00000,
  0b00000,
  0b11111,
  0b00000,
  0b00000,
  0b00000,
  0b00000,
  0b00000
};

// ====================================
// SERIAL COMMAND BUFFER
// ====================================

String command = "";

// ====================================
// LCD FUNCTIONS
// ====================================

void showHappy() {

  lcd.clear();

  lcd.setCursor(5, 0);
  lcd.write(byte(0));

  lcd.setCursor(9, 0);
  lcd.write(byte(0));

  lcd.setCursor(7, 1);
  lcd.write(byte(2));
}

void showNeutral() {

  lcd.clear();

  lcd.setCursor(5, 0);
  lcd.write(byte(0));

  lcd.setCursor(10, 0);
  lcd.write(byte(0));

  lcd.setCursor(7, 1);
  lcd.write(byte(3));
}

void blinkEyes() {

  lcd.clear();

  lcd.setCursor(5, 0);
  lcd.write(byte(1));

  lcd.setCursor(10, 0);
  lcd.write(byte(1));

  lcd.setCursor(7, 1);
  lcd.write(byte(3));
}

// ====================================
// PROCESS COMMANDS
// ====================================

void processCommand(String cmd) {

  cmd.trim();

  // ==================================
  // IDENTIFICATION
  // ==================================

  if (cmd == "WHO_ARE_YOU") {

    Serial.println("SERVO_NODE");
    return;
  }

  // ==================================
  // HEARTBEAT
  // ==================================

  if (cmd == "PING") {

    Serial.println("PONG");
    return;
  }

  // ==================================
  // FACES
  // ==================================

  if (cmd == "FACE:HAPPY") {

    showHappy();
    return;
  }

  if (cmd == "FACE:NEUTRAL") {

    showNeutral();
    return;
  }

  if (cmd == "FACE:BLINK") {

    blinkEyes();
    return;
  }

  // ==================================
  // NECK
  // ==================================

  if (cmd.startsWith("NECK:")) {

    int angle = cmd.substring(5).toInt();

    angle = constrain(angle, 0, 180);

    moveServo(NECK, angle);

    return;
  }

  // ==================================
  // LEFT ROTATION
  // ==================================

  if (cmd == "ARM:LEFT_UP") {

    moveServo(L_BASE, LEFT_UP_ANGLE);
    return;
  }

  if (cmd == "ARM:LEFT_CENTER") {

    moveServo(L_BASE, LEFT_CENTER_ANGLE);
    return;
  }

  if (cmd == "ARM:LEFT_DOWN") {

    moveServo(L_BASE, LEFT_DOWN_ANGLE);
    return;
  }

  // ==================================
  // RIGHT ROTATION
  // ==================================

  if (cmd == "ARM:RIGHT_UP") {

    moveServo(R_BASE, RIGHT_UP_ANGLE);
    return;
  }

  if (cmd == "ARM:RIGHT_CENTER") {

    moveServo(R_BASE, RIGHT_CENTER_ANGLE);
    return;
  }

  if (cmd == "ARM:RIGHT_DOWN") {

    moveServo(R_BASE, RIGHT_DOWN_ANGLE);
    return;
  }

  // ==================================
  // LEFT GRIP
  // ==================================

  if (cmd == "ARM:LEFT_GRIP") {

    moveServo(L_GRIP, LEFT_GRIP_CLOSE);
    return;
  }

  if (cmd == "ARM:LEFT_RELEASE") {

    moveServo(L_GRIP, LEFT_GRIP_OPEN);
    return;
  }

  // ==================================
  // RIGHT GRIP
  // ==================================

  if (cmd == "ARM:RIGHT_GRIP") {

    moveServo(R_GRIP, RIGHT_GRIP_CLOSE);
    return;
  }

  if (cmd == "ARM:RIGHT_RELEASE") {

    moveServo(R_GRIP, RIGHT_GRIP_OPEN);
    return;
  }

  // ==================================
  // LEFT EXTEND
  // ==================================

  if (cmd == "ARM:LEFT_EXTEND") {

    moveServo(L_SHOULDER, LEFT_SHOULDER_EXTEND);
    moveServo(L_ELBOW, LEFT_ELBOW_EXTEND);

    return;
  }

  if (cmd == "ARM:LEFT_RETRACT") {

    moveServo(L_SHOULDER, LEFT_SHOULDER_CENTER);
    moveServo(L_ELBOW, LEFT_ELBOW_CENTER);

    return;
  }

  // ==================================
  // RIGHT EXTEND
  // ==================================

  if (cmd == "ARM:RIGHT_EXTEND") {

    moveServo(R_SHOULDER, RIGHT_SHOULDER_EXTEND);
    moveServo(R_ELBOW, RIGHT_ELBOW_EXTEND);

    return;
  }

  if (cmd == "ARM:RIGHT_RETRACT") {

    moveServo(R_SHOULDER, RIGHT_SHOULDER_CENTER);
    moveServo(R_ELBOW, RIGHT_ELBOW_CENTER);

    return;
  }

}

void setup() {

  Serial.begin(115200); 
  Wire.begin();
  Wire.setClock(400000);

  lcd.init();

  lcd.backlight();

  lcd.createChar(0, eye_open);
  lcd.createChar(1, eye_closed);
  lcd.createChar(2, mouth_happy);
  lcd.createChar(3, mouth_neutral);

  pwm.begin();
  pwm.setOscillatorFrequency(27000000);
  pwm.setPWMFreq(SERVO_FREQ);
  delay(10);

  // DEFAULT POSITIONS
  initServo(NECK, 90, 1.2);

  initServo(L_BASE, LEFT_CENTER_ANGLE, 1.5);
  initServo(R_BASE, RIGHT_CENTER_ANGLE, 1.5);

  initServo(L_GRIP, LEFT_GRIP_OPEN, 2.5);
  initServo(R_GRIP, RIGHT_GRIP_OPEN, 2.5);

  initServo(L_SHOULDER, LEFT_SHOULDER_CENTER, 1.0);
  initServo(R_SHOULDER, RIGHT_SHOULDER_CENTER, 1.0);

  initServo(L_ELBOW, LEFT_ELBOW_CENTER, 1.2);
  initServo(R_ELBOW, RIGHT_ELBOW_CENTER, 1.2);
  showNeutral();
}

// ====================================
// LOOP
// ====================================

void loop() {

  while (Serial.available()) {

    char c = Serial.read();

    if (c == '\n') {

      command.trim();

      if (command.length() > 0) {

        processCommand(command);
      }

      command = "";
    }

    else {

      command += c;
    }
  }

  if (millis() - lastServoUpdate >= 15) {

    lastServoUpdate = millis();

    updateServos();
  }
}
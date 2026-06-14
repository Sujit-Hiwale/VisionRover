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
#include <ESP32Servo.h>

// ====================================
// LCD
// ====================================

LiquidCrystal_I2C lcd(0x27, 16, 2);

// ====================================
// SERVOS
// ====================================

Servo leftGripServo;
Servo leftShoulderServo;
Servo leftElbowServo;
Servo leftBaseServo;

Servo rightGripServo;
Servo rightShoulderServo;
Servo rightElbowServo;
Servo rightBaseServo;

Servo neckServo;

// ====================================
// LEFT ARM PINS
// ====================================

#define LEFT_GRIP_PIN        13
#define LEFT_SHOULDER_PIN    12
#define LEFT_ELBOW_PIN       14
#define LEFT_BASE_PIN        27

// ====================================
// RIGHT ARM PINS
// ====================================

#define RIGHT_GRIP_PIN       26
#define RIGHT_SHOULDER_PIN   25
#define RIGHT_ELBOW_PIN      33
#define RIGHT_BASE_PIN       32

// ====================================
// NECK PIN
// ====================================

#define NECK_PIN             4

// ====================================
// ANGLES
// ====================================

#define LEFT_UP_ANGLE      30
#define LEFT_CENTER_ANGLE  90
#define LEFT_DOWN_ANGLE    130

#define RIGHT_UP_ANGLE      170
#define RIGHT_CENTER_ANGLE  110
#define RIGHT_DOWN_ANGLE    10

#define LEFT_GRIP_OPEN   117
#define LEFT_GRIP_CLOSE  100

#define RIGHT_GRIP_OPEN   90
#define RIGHT_GRIP_CLOSE  45

#define LEFT_SHOULDER_EXTEND 160
#define LEFT_SHOULDER_CENTER 100

#define LEFT_ELBOW_EXTEND 170
#define LEFT_ELBOW_CENTER 140

#define RIGHT_SHOULDER_EXTEND 160
#define RIGHT_SHOULDER_CENTER 120

#define RIGHT_ELBOW_EXTEND 170
#define RIGHT_ELBOW_CENTER 130

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

    neckServo.write(angle);

    return;
  }

  // ==================================
  // LEFT ROTATION
  // ==================================

  if (cmd == "ARM:LEFT_UP") {

    leftBaseServo.write(LEFT_UP_ANGLE);
    return;
  }

  if (cmd == "ARM:LEFT_CENTER") {

    leftBaseServo.write(LEFT_CENTER_ANGLE);
    return;
  }

  if (cmd == "ARM:LEFT_DOWN") {

    leftBaseServo.write(LEFT_DOWN_ANGLE);
    return;
  }

  // ==================================
  // RIGHT ROTATION
  // ==================================

  if (cmd == "ARM:RIGHT_UP") {

    rightBaseServo.write(RIGHT_UP_ANGLE);
    return;
  }

  if (cmd == "ARM:RIGHT_CENTER") {

    rightBaseServo.write(RIGHT_CENTER_ANGLE);
    return;
  }

  if (cmd == "ARM:RIGHT_DOWN") {

    rightBaseServo.write(RIGHT_DOWN_ANGLE);
    return;
  }

  // ==================================
  // LEFT GRIP
  // ==================================

  if (cmd == "ARM:LEFT_GRIP") {

    leftGripServo.write(LEFT_GRIP_CLOSE);
    return;
  }

  if (cmd == "ARM:LEFT_RELEASE") {

    leftGripServo.write(LEFT_GRIP_OPEN);
    return;
  }

  // ==================================
  // RIGHT GRIP
  // ==================================

  if (cmd == "ARM:RIGHT_GRIP") {

    rightGripServo.write(RIGHT_GRIP_CLOSE);
    return;
  }

  if (cmd == "ARM:RIGHT_RELEASE") {

    rightGripServo.write(RIGHT_GRIP_OPEN);
    return;
  }

  // ==================================
  // LEFT EXTEND
  // ==================================

  if (cmd == "ARM:LEFT_EXTEND") {

    leftShoulderServo.write(
      LEFT_SHOULDER_EXTEND
    );

    leftElbowServo.write(
      LEFT_ELBOW_EXTEND
    );

    return;
  }

  if (cmd == "ARM:LEFT_RETRACT") {

    leftShoulderServo.write(
      LEFT_SHOULDER_CENTER
    );

    leftElbowServo.write(
      LEFT_ELBOW_CENTER
    );

    return;
  }

  // ==================================
  // RIGHT EXTEND
  // ==================================

  if (cmd == "ARM:RIGHT_EXTEND") {

    rightShoulderServo.write(
      RIGHT_SHOULDER_EXTEND
    );

    rightElbowServo.write(
      RIGHT_ELBOW_EXTEND
    );

    return;
  }

  if (cmd == "ARM:RIGHT_RETRACT") {

    rightShoulderServo.write(
      RIGHT_SHOULDER_CENTER
    );

    rightElbowServo.write(
      RIGHT_ELBOW_CENTER
    );

    return;
  }
  
}

// ====================================
// SETUP
// ====================================

void setup() {

  Serial.begin(115200);

  // ==================================
  // LCD INIT
  // ==================================
  lcd.init();

  lcd.backlight();

  lcd.createChar(0, eye_open);
  lcd.createChar(1, eye_closed);
  lcd.createChar(2, mouth_happy);
  lcd.createChar(3, mouth_neutral);

  // ==================================
  // SERVO INIT
  // ==================================

  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  leftGripServo.attach(
    LEFT_GRIP_PIN
  );

  leftShoulderServo.attach(
    LEFT_SHOULDER_PIN
  );

  leftElbowServo.attach(
    LEFT_ELBOW_PIN
  );

  leftBaseServo.attach(
    LEFT_BASE_PIN
  );

  rightGripServo.attach(
    RIGHT_GRIP_PIN
  );

  rightShoulderServo.attach(
    RIGHT_SHOULDER_PIN
  );

  rightElbowServo.attach(
    RIGHT_ELBOW_PIN
  );

  rightBaseServo.attach(
    RIGHT_BASE_PIN
  );

  neckServo.attach(
    NECK_PIN
  );

  // ==================================
  // DEFAULT POSITIONS
  // ==================================

  neckServo.write(90);

  leftBaseServo.write(
    LEFT_CENTER_ANGLE
  );

  rightBaseServo.write(
    RIGHT_CENTER_ANGLE
  );

  leftGripServo.write(
    LEFT_GRIP_OPEN
  );

  rightGripServo.write(
    RIGHT_GRIP_OPEN
  );

  leftShoulderServo.write(LEFT_SHOULDER_CENTER);
  rightShoulderServo.write(RIGHT_SHOULDER_CENTER);

  leftElbowServo.write(LEFT_ELBOW_CENTER);
  rightElbowServo.write(RIGHT_ELBOW_CENTER);

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
}
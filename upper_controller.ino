/*
========================================
ESP32 UPPER NODE
========================================
Handles:
- LCD expressions
- PCA9685 servo driver
- Robotic arms
- Neck movement
- UART communication
========================================
*/

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Adafruit_PWMServoDriver.h>

// ================================
// LCD
// ================================
LiquidCrystal_I2C lcd(0x27, 16, 2);

// ================================
// PCA9685
// ================================
Adafruit_PWMServoDriver pca =
    Adafruit_PWMServoDriver(0x40);

// ================================
// UART COMMAND
// ================================
String command = "";

// ================================
// LEFT ARM CHANNELS
// ================================
#define LEFT_GRIP_CHANNEL 0
#define LEFT_SHOULDER_CHANNEL 1
#define LEFT_ELBOW_CHANNEL 2
#define LEFT_BASE_CHANNEL 3

// ================================
// RIGHT ARM CHANNELS
// ================================
#define RIGHT_GRIP_CHANNEL 12
#define RIGHT_SHOULDER_CHANNEL 13
#define RIGHT_ELBOW_CHANNEL 14
#define RIGHT_BASE_CHANNEL 15

// ================================
// NECK
// ================================
#define NECK_CHANNEL 8

// ================================
// ARM ANGLES
// ================================

#define LEFT_UP_ANGLE 30
#define LEFT_CENTER_ANGLE 90
#define LEFT_DOWN_ANGLE 130

#define RIGHT_UP_ANGLE 170
#define RIGHT_CENTER_ANGLE 110
#define RIGHT_DOWN_ANGLE 10

#define LEFT_GRIP_OPEN 117
#define LEFT_GRIP_CLOSE 100

#define RIGHT_GRIP_OPEN 90
#define RIGHT_GRIP_CLOSE 45

// ================================
// SETUP
// ================================
void setup() {

  Serial.begin(115200);

  // ==============================
  // LCD INIT
  // ==============================

  lcd.init();

  lcd.backlight();

  lcd.clear();

  lcd.setCursor(0,0);
  lcd.print("UPPER NODE");

  // ==============================
  // PCA9685 INIT
  // ==============================

  pca.begin();

  pca.setPWMFreq(50);

  delay(500);

  Serial.println("SERVO_NODE");

  showNeutral();
}

// ================================
// MAIN LOOP
// ================================
void loop() {

  while(Serial.available()) {

    char c = Serial.read();

    if(c == '\n') {

      command.trim();

      processCommand(command);

      command = "";
    }
    else {

      command += c;
    }
  }
}

// ================================
// PROCESS COMMAND
// ================================
void processCommand(String cmd) {

  Serial.print("CMD: ");
  Serial.println(cmd);

  // ==============================
  // NODE DISCOVERY
  // ==============================

  if(cmd == "WHO_ARE_YOU") {

    Serial.println("SERVO_NODE");
  }

  // ==============================
  // HEARTBEAT
  // ==============================

  else if(cmd == "PING") {

    Serial.println("PONG");
  }

  // ==============================
  // FACE EXPRESSIONS
  // ==============================

  else if(cmd == "FACE:HAPPY") {

    showHappy();
  }

  else if(cmd == "FACE:NEUTRAL") {

    showNeutral();
  }

  else if(cmd == "FACE:ANGRY") {

    showAngry();
  }

  else if(cmd == "FACE:TALKING") {

    showTalking();
  }

  else if(cmd == "FACE:SEARCHING") {

    showSearching();
  }

  else if(cmd == "FACE:FOUND") {

    showFound();
  }

  else if(cmd == "FACE:NOT_FOUND") {

    showNotFound();
  }

  else if(cmd == "FACE:BLINK") {

    showBlink();
  }

  else if(cmd == "FACE:CLEAR") {

    lcd.clear();
  }

  // ==============================
  // LEFT ARM
  // ==============================

  else if(cmd == "ARM:LEFT_UP") {

    moveServo(
        LEFT_BASE_CHANNEL,
        LEFT_UP_ANGLE
    );
  }

  else if(cmd == "ARM:LEFT_CENTER") {

    moveServo(
        LEFT_BASE_CHANNEL,
        LEFT_CENTER_ANGLE
    );
  }

  else if(cmd == "ARM:LEFT_DOWN") {

    moveServo(
        LEFT_BASE_CHANNEL,
        LEFT_DOWN_ANGLE
    );
  }

  else if(cmd == "ARM:LEFT_GRIP") {

    moveServo(
        LEFT_GRIP_CHANNEL,
        LEFT_GRIP_CLOSE
    );
  }

  else if(cmd == "ARM:LEFT_RELEASE") {

    moveServo(
        LEFT_GRIP_CHANNEL,
        LEFT_GRIP_OPEN
    );
  }

  // ==============================
  // RIGHT ARM
  // ==============================

  else if(cmd == "ARM:RIGHT_UP") {

    moveServo(
        RIGHT_BASE_CHANNEL,
        RIGHT_UP_ANGLE
    );
  }

  else if(cmd == "ARM:RIGHT_CENTER") {

    moveServo(
        RIGHT_BASE_CHANNEL,
        RIGHT_CENTER_ANGLE
    );
  }

  else if(cmd == "ARM:RIGHT_DOWN") {

    moveServo(
        RIGHT_BASE_CHANNEL,
        RIGHT_DOWN_ANGLE
    );
  }

  else if(cmd == "ARM:RIGHT_GRIP") {

    moveServo(
        RIGHT_GRIP_CHANNEL,
        RIGHT_GRIP_CLOSE
    );
  }

  else if(cmd == "ARM:RIGHT_RELEASE") {

    moveServo(
        RIGHT_GRIP_CHANNEL,
        RIGHT_GRIP_OPEN
    );
  }

  // ==============================
  // NECK
  // ==============================

  else if(cmd.startsWith("NECK:")) {

    String angleStr =
        cmd.substring(5);

    int angle = angleStr.toInt();

    angle = constrain(angle, 20, 160);

    moveServo(
        NECK_CHANNEL,
        angle
    );
  }
}

// ================================
// SERVO MOVEMENT
// ================================
void moveServo(
    int channel,
    int angle
) {

  int pulse = map(
      angle,
      0,
      180,
      102,
      512
  );

  pca.setPWM(
      channel,
      0,
      pulse
  );
}

// ================================
// EXPRESSIONS
// ================================
void showHappy() {

  lcd.clear();

  lcd.setCursor(4,0);
  lcd.print("^    ^");

  lcd.setCursor(6,1);
  lcd.print("\\__/");
}

void showNeutral() {

  lcd.clear();

  lcd.setCursor(4,0);
  lcd.print("-    -");

  lcd.setCursor(6,1);
  lcd.print("----");
}

void showAngry() {

  lcd.clear();

  lcd.setCursor(4,0);
  lcd.print(">    <");

  lcd.setCursor(6,1);
  lcd.print("____");
}

void showTalking() {

  lcd.clear();

  lcd.setCursor(4,0);
  lcd.print("o    o");

  lcd.setCursor(6,1);
  lcd.print("OOOO");
}

void showSearching() {

  lcd.clear();

  lcd.setCursor(4,0);
  lcd.print("o    O");

  lcd.setCursor(6,1);
  lcd.print("----");
}

void showFound() {

  lcd.clear();

  lcd.setCursor(4,0);
  lcd.print("^    ^");

  lcd.setCursor(6,1);
  lcd.print("\\OO/");
}

void showNotFound() {

  lcd.clear();

  lcd.setCursor(4,0);
  lcd.print("x    x");

  lcd.setCursor(6,1);
  lcd.print("____");
}

void showBlink() {

  lcd.clear();

  lcd.setCursor(4,0);
  lcd.print("-    -");

  lcd.setCursor(6,1);
  lcd.print("____");
}
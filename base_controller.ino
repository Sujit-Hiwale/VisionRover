/*
========================================
ESP32 Robot Base Controller
========================================
Controls:
- L298N motors
- 2 ultrasonic sensors
- UART communication with Pi
========================================
*/

// ================================
// MOTOR PINS
// ================================
#define IN1 26
#define IN2 27
#define IN3 14
#define IN4 12

// ================================
// FRONT ULTRASONIC
// ================================
#define TRIG_FRONT 5
#define ECHO_FRONT 18

// ================================
// REAR ULTRASONIC
// ================================
#define TRIG_REAR 19
#define ECHO_REAR 21

// ================================
// SAFETY DISTANCES
// ================================
const int FRONT_SAFE = 25;
const int REAR_SAFE  = 20;

// ================================
// GLOBALS
// ================================
String command = "";

char currentCommand = 'S';

unsigned long lastCommandTime = 0;

long frontDistance = 999;
long rearDistance  = 999;

// ================================
// SETUP
// ================================
void setup() {

  Serial.begin(115200);

  // Motor pins
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // Ultrasonic pins
  pinMode(TRIG_FRONT, OUTPUT);
  pinMode(ECHO_FRONT, INPUT);

  pinMode(TRIG_REAR, OUTPUT);
  pinMode(ECHO_REAR, INPUT);

  stopMotors();

  Serial.println("BASE_NODE");
}

// ================================
// MAIN LOOP
// ================================
void loop() {

  // ==============================
  // READ DISTANCES
  // ==============================

  frontDistance = getDistance(
      TRIG_FRONT,
      ECHO_FRONT
  );

  rearDistance = getDistance(
      TRIG_REAR,
      ECHO_REAR
  );

  // ==============================
  // READ UART
  // ==============================

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

  // ==============================
  // WATCHDOG
  // ==============================

  if(millis() - lastCommandTime > 1000) {

    stopMotors();

    currentCommand = 'S';
  }

  // ==============================
  // EXECUTE MOTION
  // ==============================

  executeCommand();

  delay(50);
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

    Serial.println("BASE_NODE");
  }

  // ==============================
  // HEARTBEAT
  // ==============================

  else if(cmd == "PING") {

    Serial.println("PONG");
  }

  // ==============================
  // MOVEMENT
  // ==============================

  else if(cmd == "F") {

    currentCommand = 'F';

    lastCommandTime = millis();
  }

  else if(cmd == "B") {

    currentCommand = 'B';

    lastCommandTime = millis();
  }

  else if(cmd == "L") {

    currentCommand = 'L';

    lastCommandTime = millis();
  }

  else if(cmd == "R") {

    currentCommand = 'R';

    lastCommandTime = millis();
  }

  else if(cmd == "S") {

    currentCommand = 'S';

    stopMotors();

    lastCommandTime = millis();
  }
}

// ================================
// EXECUTE COMMAND
// ================================
void executeCommand() {

  switch(currentCommand) {

    case 'F':

      if(frontDistance > FRONT_SAFE) {

        moveForward();
      }
      else {

        stopMotors();

        Serial.println("BLOCKED_FRONT");
      }

      break;

    case 'B':

      if(rearDistance > REAR_SAFE) {

        moveBackward();
      }
      else {

        stopMotors();

        Serial.println("BLOCKED_REAR");
      }

      break;

    case 'L':

      moveLeft();
      break;

    case 'R':

      moveRight();
      break;

    default:

      stopMotors();
      break;
  }
}

// ================================
// ULTRASONIC FUNCTION
// ================================
long getDistance(int trigPin, int echoPin) {

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);

  digitalWrite(trigPin, LOW);

  long duration = pulseIn(
      echoPin,
      HIGH,
      30000
  );

  // Timeout protection
  if(duration == 0) {
    return 999;
  }

  long distance = duration * 0.034 / 2;

  return distance;
}

// ================================
// MOTOR FUNCTIONS
// ================================
void stopMotors() {

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void moveForward() {

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void moveBackward() {

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void moveLeft() {

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void moveRight() {

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}
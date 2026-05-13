import RPi.GPIO as GPIO
import time

# ==============================
# MOTOR DRIVER PINS
# ==============================
IN1 = 26
IN2 = 19
IN3 = 13
IN4 = 6

# ==============================
# ULTRASONIC SENSOR PINS
# Sensor 1 -> TRIG=8  ECHO=11
# Sensor 2 -> TRIG=9  ECHO=10
# ==============================
TRIG1 = 8
ECHO1 = 11

TRIG2 = 9
ECHO2 = 10

# ==============================
# GPIO SETUP
# ==============================
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Motor pins
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# Ultrasonic pins
GPIO.setup(TRIG1, GPIO.OUT)
GPIO.setup(ECHO1, GPIO.IN)

GPIO.setup(TRIG2, GPIO.OUT)
GPIO.setup(ECHO2, GPIO.IN)

GPIO.output(TRIG1, False)
GPIO.output(TRIG2, False)

time.sleep(2)

# ==============================
# STOP MOTORS
# ==============================
def stop():
    print("🛑 Stopped")

    GPIO.output(IN1, 0)
    GPIO.output(IN2, 0)
    GPIO.output(IN3, 0)
    GPIO.output(IN4, 0)


# ==============================
# ULTRASONIC DISTANCE FUNCTION
# ==============================
def get_distance(trig, echo):

    # Send trigger pulse
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    start_time = time.time()
    stop_time = time.time()

    timeout = time.time()

    # Wait for echo HIGH
    while GPIO.input(echo) == 0:
        start_time = time.time()

        if time.time() - timeout > 0.03:
            return 999

    timeout = time.time()

    # Wait for echo LOW
    while GPIO.input(echo) == 1:
        stop_time = time.time()

        if time.time() - timeout > 0.03:
            return 999

    # Calculate distance
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2

    return round(distance, 2)


# ==============================
# CHECK SAFE DISTANCE
# ==============================
def is_safe():

    d1 = get_distance(TRIG1, ECHO1)
    d2 = get_distance(TRIG2, ECHO2)

    print(f"📏 Sensor1: {d1} cm")
    print(f"📏 Sensor2: {d2} cm")

    # Both sensors must be greater than 25 cm
    if d1 > 25 and d2 > 25:
        return True

    print("⚠️ Obstacle Detected!")
    stop()
    return False


# ==============================
# FORWARD
# ==============================
def forward(duration=None):

    if not is_safe():
        return

    print("🚗 Moving Forward")

    GPIO.output(IN1, 1)
    GPIO.output(IN2, 0)
    GPIO.output(IN3, 1)
    GPIO.output(IN4, 0)

    if duration:
        time.sleep(duration)
        stop()

# ==============================
# BACKWARD
# ==============================
def backward(duration=None):

    if not is_safe():
        return

    print("🔙 Moving Backward")

    GPIO.output(IN1, 0)
    GPIO.output(IN2, 1)
    GPIO.output(IN3, 0)
    GPIO.output(IN4, 1)

    if duration:
        time.sleep(duration)
        stop()

# ==============================
# LEFT
# ==============================
def left(duration=1):

    print("⬅️ Turning Left")

    GPIO.output(IN1, 0)
    GPIO.output(IN2, 1)
    GPIO.output(IN3, 1)
    GPIO.output(IN4, 0)

    time.sleep(duration)

    stop()


# ==============================
# RIGHT
# ==============================
def right(duration=0.4):

    print("➡️ Turning Right")

    GPIO.output(IN1, 1)
    GPIO.output(IN2, 0)
    GPIO.output(IN3, 0)
    GPIO.output(IN4, 1)

    time.sleep(duration)

    stop()
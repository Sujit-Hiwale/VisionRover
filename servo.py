print("🤖 Servo module loaded")

import time
import board
import busio
from adafruit_pca9685 import PCA9685

# ==============================
# PCA9685 Setup
# ==============================

# Initialize I2C
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize PCA9685
pca = PCA9685(i2c)
pca.frequency = 50   # Servo frequency

# ==============================
# LEFT HAND CHANNELS
# ==============================

LEFT_GRIP_CHANNEL = 0
LEFT_SHOULDER_CHANNEL = 1
LEFT_ELBOW_CHANNEL = 2
LEFT_BASE_CHANNEL = 3

# ==============================
# RIGHT HAND CHANNELS
# ==============================

RIGHT_GRIP_CHANNEL = 12
RIGHT_SHOULDER_CHANNEL = 13
RIGHT_ELBOW_CHANNEL = 14
RIGHT_BASE_CHANNEL = 15

# LEFT ARM

LEFT_GRIP_CLOSE = 45     # Closed position
LEFT_GRIP_OPEN = 90  # Open position

LEFT_UP_EXTEND = 120
LEFT_DOWN_EXTEND = 150

# RIGHT ARM

RIGHT_GRIP_CLOSE = 45
RIGHT_GRIP_OPEN = 90

RIGHT_UP_EXTEND = 60
RIGHT_DOWN_EXTEND = 30

# Neutral position
ARM_CENTER = 100

# Stronger extension positions

LEFT_UP_ANGLE = 10
LEFT_STRAIGHT_ANGLE = 90
LEFT_DOWN_ANGLE = 170

RIGHT_UP_ANGLE = 10
RIGHT_STRAIGHT_ANGLE = 90
RIGHT_DOWN_ANGLE = 170

# ==============================
# HEAD / NECK CHANNEL
# ==============================

NECK_CHANNEL = 8

NECK_MIN = 20
NECK_CENTER = 90
NECK_MAX = 160

# ==============================
# Helper Functions
# ==============================

def angle_to_duty(angle):
    """
    Convert servo angle to PCA9685 duty cycle
    """

    min_pulse = 500    # microseconds
    max_pulse = 2500   # microseconds

    pulse = min_pulse + (angle / 180.0) * (max_pulse - min_pulse)

    duty = int(pulse * 65535 / 20000)
    return duty

SMOOTH_MOVEMENT = True
SERVO_DELAY = 0.01
servo_positions = {}

def set_angle(channel, target):

    global servo_positions

    target = max(0, min(180, target))

    current = servo_positions.get(channel, target)

    if current == target:
        return

    if SMOOTH_MOVEMENT:

        step = 1 if target > current else -1

        for angle in range(current, target, step):

            pca.channels[channel].duty_cycle = angle_to_duty(angle)
            time.sleep(SERVO_DELAY)

    pca.channels[channel].duty_cycle = angle_to_duty(target)

    servo_positions[channel] = target

# ==============================
# Robotic Hand Functions
# ==============================

def initialize_robot():

    left_release()
    right_release()

    both_retract()

    left_rotate_center()
    right_rotate_center()

def left_grip():
    print("🦾 Gripping object")
    set_angle(LEFT_GRIP_CHANNEL, LEFT_GRIP_CLOSE)
    time.sleep(0.5)

def left_release():
    print("🪶 Releasing object")
    set_angle(LEFT_GRIP_CHANNEL, LEFT_GRIP_OPEN)
    time.sleep(0.5)

def right_grip():
    print("🦾 Right grip")
    set_angle(RIGHT_GRIP_CHANNEL, RIGHT_GRIP_CLOSE)
    time.sleep(0.5)

def right_release():
    print("🪶 Right release")
    set_angle(RIGHT_GRIP_CHANNEL, RIGHT_GRIP_OPEN)
    time.sleep(0.5)


def left_extend():
    print("📏 Left Extending arm")
    set_angle(LEFT_SHOULDER_CHANNEL, LEFT_UP_EXTEND)
    set_angle(LEFT_ELBOW_CHANNEL, LEFT_DOWN_EXTEND)
    time.sleep(0.7)

def right_extend():
    print("📏 Right Extending arm")
    set_angle(RIGHT_SHOULDER_CHANNEL, RIGHT_UP_EXTEND)
    set_angle(RIGHT_ELBOW_CHANNEL, RIGHT_DOWN_EXTEND)
    time.sleep(0.7)

def left_retract():
    print("🔙 Left Retracting arm")
    set_angle(LEFT_SHOULDER_CHANNEL, ARM_CENTER)
    set_angle(LEFT_ELBOW_CHANNEL, ARM_CENTER)
    time.sleep(0.7)

def right_retract():
    print("🔙 Right Retracting arm")
    set_angle(RIGHT_SHOULDER_CHANNEL, ARM_CENTER)
    set_angle(RIGHT_ELBOW_CHANNEL, ARM_CENTER)
    time.sleep(0.7)

def both_extend():
    left_extend()
    right_extend()

def both_retract():
    left_retract()
    right_retract()


def left_rotate_up():
    print("⬅️ Left Arm Up")
    set_angle(LEFT_BASE_CHANNEL, LEFT_UP_ANGLE)
    time.sleep(0.5)


def left_rotate_center():
    print("⬆️ Left Arm Center")
    set_angle(LEFT_BASE_CHANNEL, LEFT_STRAIGHT_ANGLE)
    time.sleep(0.5)

def left_rotate_down():
    print("➡️ Left Arm Down")
    set_angle(LEFT_BASE_CHANNEL, LEFT_DOWN_ANGLE)
    time.sleep(0.5)

def right_rotate_up():
    print("⬅️ Right Arm Up")
    set_angle(RIGHT_BASE_CHANNEL, RIGHT_UP_ANGLE)
    time.sleep(0.5)

def right_rotate_center():
    print("⬆️ Right Arm Center")
    set_angle(RIGHT_BASE_CHANNEL, RIGHT_STRAIGHT_ANGLE)
    time.sleep(0.5)

def right_rotate_down():
    print("➡️ Right Arm Down")
    set_angle(RIGHT_BASE_CHANNEL, RIGHT_DOWN_ANGLE)
    time.sleep(0.5)

def move_neck(target_angle):

    print(f"🦾 Moving neck to {target_angle}°")

    target_angle = max(NECK_MIN, min(NECK_MAX, target_angle))

    set_angle(NECK_CHANNEL, target_angle)

    time.sleep(0.3)
    
def rotate_neck(delta):

    current = servo_positions.get(NECK_CHANNEL, NECK_CENTER)

    target = current + delta

    target = max(NECK_MIN, min(NECK_MAX, target))

    print(f"🦾 Rotating neck to {target}°")

    set_angle(NECK_CHANNEL, target)

def cleanup():
    pca.deinit()

try:
    initialize_robot()

except KeyboardInterrupt:
    cleanup()
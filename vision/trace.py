import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
import vision_state
import time
from camera import get_latest_frame
from objDet import find_object
import motor
import servo
import robot_state

# =====================================
# CONFIG
# =====================================

FRAME_CENTER_X = 320

CENTER_THRESHOLD = 50

SEARCH_POSITIONS = [

    60,
    90,
    120,
    90
]

# =====================================
# CENTER OBJECT
# =====================================

def center_object(detection):

    center_x = detection["center"][0]

    diff = center_x - FRAME_CENTER_X

    # ================================
    # TURN LEFT
    # ================================

    if diff < -CENTER_THRESHOLD:

        print("⬅ Turning left")

        motor.left()

        time.sleep(0.15)

        motor.stop()

        return False

    # ================================
    # TURN RIGHT
    # ================================

    elif diff > CENTER_THRESHOLD:

        print("➡ Turning right")

        motor.right()

        time.sleep(0.15)

        motor.stop()

        return False

    # ================================
    # CENTERED
    # ================================

    print("✅ Target centered")

    return True

# =====================================
# APPROACH OBJECT
# =====================================

def approach_object(detection):

    x1, y1, x2, y2 = detection["box"]

    width = x2 - x1

    # =================================
    # ESTIMATED DISTANCE
    # =================================

    if width < 200:

        print("⬆ Moving forward")

        motor.forward()

        time.sleep(0.3)

        motor.stop()

        return False

    print("🛑 Reached object")

    motor.stop()

    return True

# =====================================
# TRACK OBJECT
# =====================================

def track_object(target_name):

    frame = get_latest_frame()

    if frame is None:
        return False

    detection = find_object(
        frame,
        target_name
    )

    if detection is None:

        print("❌ Lost target")

        return False

    if not center_object(detection):
        return False

    if not approach_object(detection):
        return False

    return True

# =====================================
# SCAN AREA
# =====================================

def scan_for_object(
    target_name,
    timeout=30,
    scan_delay=0.8
):

    print(
        f"🔎 Searching for {target_name}"
    )
    
    with vision_state.vision_lock:
        vision_state.active_mode = "object"

    start_time = time.time()

    try: 

        while True:

            if robot_state.interrupt_requested:
                motor.stop()
                return None

            # ============================
            # TIMEOUT
            # ============================

            if (
                time.time() - start_time
                > timeout
            ):

                print("⏰ Scan timeout")

                motor.stop()

                return None

            # ============================
            # NECK SCAN
            # ============================

            for angle in [45, 90, 135, 90]:

                print(
                    f"👀 Neck angle: {angle}"
                )

                servo.move_neck(angle)

                time.sleep(scan_delay)

                frame = get_latest_frame()

                if frame is None:
                    continue

                detection = find_object(
                    frame,
                    target_name
                )

                if detection:

                    print(
                        f"🎯 Found {target_name}"
                    )

                    return detection
                
            # ============================
            # BODY ROTATION
            # ============================

            print("🔄 Rotating body")

            motor.left()

            time.sleep(0.4)

            motor.stop()

            time.sleep(0.5)

    finally:
        with vision_state.vision_lock:
            vision_state.active_mode = "idle"
# =====================================
# FIND + REACH
# =====================================

def find_and_reach(
    target_name,
    timeout=30
):

    print(
        f"🚀 Searching for "
        f"{target_name}"
    )

    start_time = time.time()

    # =================================
    # SEARCH PHASE
    # =================================

    detection = scan_for_object(
        target_name
    )

    if detection is None:

        return None

    # =================================
    # TRACK + APPROACH
    # =================================

    while True:

        if robot_state.interrupt_requested:
            motor.stop()
            return None

        if time.time() - start_time > timeout:

            print("⏰ Timeout")

            motor.stop()

            return None

        reached = track_object(
            target_name
        )

        if reached:

            print(
                f"✅ Reached "
                f"{target_name}"
            )

            return True

        time.sleep(0.1)
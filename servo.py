import upperNode
import time
# =====================================
# NECK
# =====================================

NECK_CENTER = 90

def move_neck(angle):

    upperNode.send(
        f"NECK:{angle}"
    )

# =====================================
# INITIALIZE
# =====================================

def initialize_robot():

    move_neck(NECK_CENTER)

    both_retract()

    left_rotate_center()
    right_rotate_center()

    left_release()
    right_release()

# =====================================
# LEFT ARM ROTATION
# =====================================

def left_rotate_up():

    upperNode.send(
        "ARM:LEFT_UP"
    )

def left_rotate_center():

    upperNode.send(
        "ARM:LEFT_CENTER"
    )

def left_rotate_down():

    upperNode.send(
        "ARM:LEFT_DOWN"
    )

# =====================================
# RIGHT ARM ROTATION
# =====================================

def right_rotate_up():

    upperNode.send(
        "ARM:RIGHT_UP"
    )

def right_rotate_center():

    upperNode.send(
        "ARM:RIGHT_CENTER"
    )

def right_rotate_down():

    upperNode.send(
        "ARM:RIGHT_DOWN"
    )

# =====================================
# LEFT GRIP
# =====================================

def left_grip():

    upperNode.send(
        "ARM:LEFT_GRIP"
    )

def left_release():

    upperNode.send(
        "ARM:LEFT_RELEASE"
    )

# =====================================
# RIGHT GRIP
# =====================================

def right_grip():

    upperNode.send(
        "ARM:RIGHT_GRIP"
    )

def right_release():

    upperNode.send(
        "ARM:RIGHT_RELEASE"
    )

# =====================================
# LEFT EXTEND / RETRACT
# =====================================

def left_extend():

    upperNode.send(
        "ARM:LEFT_EXTEND"
    )

def left_retract():

    upperNode.send(
        "ARM:LEFT_RETRACT"
    )

# =====================================
# RIGHT EXTEND / RETRACT
# =====================================

def right_extend():

    upperNode.send(
        "ARM:RIGHT_EXTEND"
    )

def right_retract():

    upperNode.send(
        "ARM:RIGHT_RETRACT"
    )

# =====================================
# BOTH ARMS
# =====================================

def both_extend():

    left_extend()

    right_extend()

def both_retract():

    left_retract()

    right_retract()

def move_hands():

    try:

        # =================================
        # LEFT HAND SEQUENCE
        # =================================

        left_rotate_up()
        time.sleep(0.4)

        left_extend()
        time.sleep(0.4)

        left_grip()
        time.sleep(0.4)

        left_release()
        time.sleep(0.4)

        left_retract()
        time.sleep(0.4)

        left_rotate_center()
        time.sleep(0.4)

        # =================================
        # RIGHT HAND SEQUENCE
        # =================================

        right_rotate_up()
        time.sleep(0.4)

        right_extend()
        time.sleep(0.4)

        right_grip()
        time.sleep(0.4)

        right_release()
        time.sleep(0.4)

        right_retract()
        time.sleep(0.4)

        right_rotate_center()
        time.sleep(0.4)

    except Exception as e:

        print(
            f"Hand movement failed: {e}"
        )
from flask import Flask, request, jsonify
from datetime import datetime
import threading
import time
import re

from vision.face_greeting import face_monitor
from vision.camera import (
    get_latest_frame,
    start_camera
)

import motor
import servo
import internet
import smallFaces
import robot_state
from personality import handle_personality

# =====================================
# FLASK
# =====================================

app = Flask(__name__)

# =====================================
# ROBOT TASK STATE
# =====================================

current_task = None

task_lock = threading.Lock()

# =====================================
# LOG SYSTEM
# =====================================

logs = []

MAX_LOGS = 200

# =====================================
# LOGGING
# =====================================

def add_log(message):

    timestamp = datetime.now().strftime(
        "%H:%M:%S"
    )

    log_entry = f"[{timestamp}] {message}"

    logs.append(log_entry)

    if len(logs) > MAX_LOGS:
        logs.pop(0)

    print(log_entry)

# =====================================
# TASK HELPERS
# =====================================

def set_task(task_name):

    global current_task

    with task_lock:

        current_task = task_name

def clear_task():

    global current_task

    with task_lock:

        current_task = None

def get_task():

    with task_lock:

        return current_task

# =====================================
# EMERGENCY STOP
# =====================================

def emergency_stop():

    add_log("🛑 Emergency stop")

    robot_state.interrupt_requested = True

    try:
        motor.stop()
    except:
        pass

    try:
        servo.move_neck(
            servo.NECK_CENTER
        )
    except:
        pass

    try:
        smallFaces.neutral()
    except:
        pass

    clear_task()

# =====================================
# DANCE
# =====================================

def dance():

    try:

        set_task("dance")

        add_log("🕺 Dance started")

        try:
            smallFaces.happy()
        except:
            pass

        for _ in range(3):

            if robot_state.interrupt_requested:
                break

            try:
                servo.move_hands()
            except:
                pass

            try:
                motor.forward()
                time.sleep(0.5)

                motor.left()
                time.sleep(0.5)

                motor.right()
                time.sleep(0.5)

                motor.backward()
                time.sleep(0.5)

                motor.stop()

            except:
                pass

        try:
            smallFaces.neutral()
        except:
            pass

        add_log("✅ Dance completed")

    except Exception as e:

        add_log(
            f"❌ Dance error: {e}"
        )

    finally:

        robot_state.interrupt_requested = False

        clear_task()

# =====================================
# SIMPLE COMMANDS
# =====================================

# =====================================
# SIMPLE COMMANDS
# =====================================

SIMPLE_COMMANDS = {

    # ==============================
    # MOVEMENT
    # ==============================

    "forward": motor.forward,
    "backward": motor.backward,
    "left": motor.left,
    "right": motor.right,
    "stop": emergency_stop,

    # ==============================
    # HAND DEMO
    # ==============================

    "move hands": servo.move_hands,

    # ==============================
    # LEFT GRIP
    # ==============================

    "left grip": servo.left_grip,
    "left release": servo.left_release,

    # ==============================
    # RIGHT GRIP
    # ==============================

    "right grip": servo.right_grip,
    "right release": servo.right_release,

    # ==============================
    # LEFT EXTEND / RETRACT
    # ==============================

    "left extend": servo.left_extend,
    "left retract": servo.left_retract,

    # ==============================
    # RIGHT EXTEND / RETRACT
    # ==============================

    "right extend": servo.right_extend,
    "right retract": servo.right_retract,

    # ==============================
    # LEFT ROTATION
    # ==============================

    "left up": servo.left_rotate_up,
    "left center": servo.left_rotate_center,
    "left down": servo.left_rotate_down,
}

# =====================================
# BACKGROUND TASK
# =====================================

def run_background_task(
    task_name,
    function,
    *args
):

    def wrapper():

        try:

            set_task(task_name)

            robot_state.interrupt_requested = False

            function(*args)

        except Exception as e:

            add_log(
                f"❌ Task error: {e}"
            )

        finally:

            robot_state.interrupt_requested = False

            clear_task()

    thread = threading.Thread(
        target=wrapper,
        daemon=True
    )

    thread.start()

# =====================================
# HOME
# =====================================

@app.route('/')
def home():

    return jsonify({
        "status": "running",
        "task": get_task()
    })

# =====================================
# STATUS
# =====================================

@app.route('/status')
def status():

    return jsonify({

        "task": get_task(),

        "interrupted":
        robot_state.interrupt_requested
    })

# =====================================
# COMMAND
# =====================================

@app.route('/command', methods=['POST'])
def command():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "status": "error",
                "message": "No JSON"
            }), 400

        cmd = (
            data.get(
                "command",
                ""
            )
            .lower()
            .strip()
        )
        
        # =================================
        # REMOVE WAKE WORD
        # =================================

        match = re.search(r'\bmax\b', cmd, re.IGNORECASE)

        if not match:
            return jsonify({
                "status": "ignored",
                "message": "Wake word not detected"
            })

        cmd = cmd[match.end():].strip()

        if not cmd:
            return jsonify({
                "status": "ignored",
                "message": "No command after wake word"
            })

        add_log(f"📥 {cmd}")

        # =================================
        # STOP
        # =================================

        if cmd in [

            "ok",
            "okay",
            "stop",
            "cancel",
            "emergency stop",
            "stop everything"

        ]:

            emergency_stop()

            return jsonify({
                "status": "stopped"
            })

        # =================================
        # BUSY CHECK
        # =================================

        busy_task = get_task()

        if busy_task is not None:

            return jsonify({

                "status": "busy",

                "task": busy_task
            })

        # =================================
        # SIMPLE COMMANDS
        # =================================

        if cmd in SIMPLE_COMMANDS:

            try:

                SIMPLE_COMMANDS[cmd]()

            except Exception as e:

                add_log(
                    f"⚠️ Command issue: {e}"
                )

            return jsonify({

                "status": "executed",

                "command": cmd
            })

        elif handle_personality(cmd):

            return jsonify({
                "status": "success"
            })
        
        elif cmd == "dance":

            run_background_task(
                "dance",
                dance
            )

            return jsonify({
                "status": "started"
            })

        elif any(word in cmd for word in ["find", "search for", "look for"]):

            target = cmd

            for w in ["find", "search for", "look for"]:

                target = target.replace(w, "")

            target = target.strip().lower()

            from vision.objDet import find_object
            from vision.camera import get_latest_frame

            def object_search_task(target):

                add_log(f"🔍 Searching for: {target}")

                SEARCH_SERVO = 0   # PCA9685 channel

                while not robot_state.interrupt_requested:

                    # =====================================
                    # SCAN 0 -> 180
                    # =====================================

                    for angle in range(0, 181, 15):

                        if robot_state.interrupt_requested:
                            return

                        try:

                            servo.move_neck(angle)

                        except Exception as e:

                            add_log(
                                f"Servo error: {e}"
                            )

                        add_log(
                            f"Scanning angle: {angle}"
                        )

                        time.sleep(0.4)

                        frame = get_latest_frame()

                        if frame is None:
                            continue

                        detection = find_object(
                            frame,
                            target
                        )

                        # =====================================
                        # FOUND
                        # =====================================

                        if detection:

                            add_log(
                                f"✅ Found {target}"
                            )

                            add_log(
                                f"Confidence: {detection['confidence']}"
                            )

                            try:
                                motor.stop()
                            except:
                                pass

                            return

                    # =====================================
                    # OBJECT NOT FOUND
                    # TURN LEFT
                    # =====================================

                    add_log(
                        "↩️ Object not found, rotating robot"
                    )

                    try:

                        motor.left()

                        time.sleep(1)

                        motor.stop()

                    except Exception as e:

                        add_log(
                            f"Motor error: {e}"
                        )

                    time.sleep(0.5)

                add_log("🛑 Search interrupted")
            run_background_task(
                "vision_object_search",
                object_search_task,
                target
            )

            return jsonify({
                "status": "started",
                "target": target
            })

        # =================================
        # INTERNET SEARCH
        # =================================

        elif any(

            cmd.startswith(word)

            for word in [

                "what",
                "who",
                "where",
                "when",
                "why",
                "how",
                "tell me",
                "search"
            ]
        ):

            run_background_task(

                "internet_search",

                internet.assistant_search,

                cmd,

                True
            )

            return jsonify({
                "status": "started"
            })

        # =================================
        # UNKNOWN
        # =================================

        return jsonify({

            "status": "unknown",

            "command": cmd
        })

    except Exception as e:

        add_log(f"❌ ERROR: {e}")

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500

# =====================================
# LOGS
# =====================================

@app.route('/logs')
def get_logs():

    return jsonify({
        "logs": logs
    })

# =====================================
# MAIN
# =====================================

if __name__ == '__main__':

    print("🔥 Starting Robot Server")

    add_log(
        "🔥 Robot server booting"
    )

    try:

        servo.initialize_robot()

    except Exception as e:

        add_log(
            f"⚠️ Servo init skipped: {e}"
        )

    try:

        smallFaces.neutral()

    except Exception as e:

        add_log(
            f"⚠️ LCD init skipped: {e}"
        )

    add_log(
        "✅ Robot server running"
    )

    start_camera()
    
    def vision_loop():
        face_monitor(get_latest_frame)

    vision_thread = threading.Thread(
        target=vision_loop,
        daemon=True
    )

    vision_thread.start()

    print("👁 Vision system started")

    app.run(

        host='0.0.0.0',

        port=5000,

        debug=False,

        threaded=True
    )
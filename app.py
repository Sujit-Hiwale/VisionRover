from flask import Flask, request, jsonify
from datetime import datetime

import threading
import time

# =====================================
# ROBOT MODULES
# =====================================

import motor
import servo
import internet
import find
import smallFaces
import robot_state
import speak

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
# SAFE TASK SETTERS
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

    add_log("🛑 Emergency stop triggered")

    robot_state.interrupt_requested = True

    motor.stop()

    servo.move_neck(
        servo.NECK_CENTER
    )

    servo.left_rotate_center()
    servo.right_rotate_center()

    smallFaces.neutral()

    clear_task()

# =====================================
# DANCE MODE
# =====================================


def dance():

    try:

        set_task("dance")

        add_log("🕺 Dance mode started")

        smallFaces.happy()

        servo.left_release()
        servo.right_release()

        for _ in range(3):

            if robot_state.interrupt_requested:

                add_log(
                    "🛑 Dance interrupted"
                )

                break

            servo.left_rotate_up()
            servo.right_rotate_up()

            servo.move_neck(60)

            motor.forward(0.6)

            servo.left_rotate_up()
            servo.right_rotate_down()

            servo.move_neck(120)

            motor.left(0.3)

            time.sleep(0.3)

            servo.left_rotate_down()
            servo.right_rotate_up()

            servo.move_neck(40)

            motor.right(0.3)

            servo.left_rotate_down()
            servo.right_rotate_down()

            servo.move_neck(140)

            motor.backward(0.6)

        servo.left_rotate_center()
        servo.right_rotate_center()

        servo.move_neck(
            servo.NECK_CENTER
        )

        motor.stop()

        smallFaces.neutral()

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

SIMPLE_COMMANDS = {

    "forward": motor.forward,
    "backward": motor.backward,
    "left": motor.left,
    "right": motor.right,
    "stop": emergency_stop,

    "left grip": servo.left_grip,
    "left release": servo.left_release,

    "left extend": servo.left_extend,
    "left retract": servo.left_retract,

    "left arm up": servo.left_rotate_up,
    "left arm down": servo.left_rotate_down,
    "left arm center": servo.left_rotate_center,

    "right grip": servo.right_grip,
    "right release": servo.right_release,

    "right extend": servo.right_extend,
    "right retract": servo.right_retract,

    "right arm up": servo.right_rotate_up,
    "right arm down": servo.right_rotate_down,
    "right arm center": servo.right_rotate_center,

    "both extend": servo.both_extend,
    "both retract": servo.both_retract,

    "both grip": lambda: (
        servo.left_grip(),
        servo.right_grip()
    ),

    "both release": lambda: (
        servo.left_release(),
        servo.right_release()
    ),
}

# =====================================
# BACKGROUND TASK WRAPPER
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
# HOME ROUTE
# =====================================

@app.route('/')
def home():

    return jsonify({
        "status": "running",
        "task": get_task()
    })

# =====================================
# STATUS ROUTE
# =====================================

@app.route('/status', methods=['GET'])
def status():

    return jsonify({
        "task": get_task(),
        "interrupted": (
            robot_state.interrupt_requested
        )
    })

# =====================================
# COMMAND ROUTE
# =====================================

@app.route('/command', methods=['POST'])
def command():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "status": "error",
                "message": "No JSON received"
            }), 400

        cmd = (
            data.get(
                "command",
                ""
            )
            .lower()
            .strip()
        )

        if not cmd:

            return jsonify({
                "status": "error",
                "message": "Empty command"
            })

        add_log(f"📥 Command: {cmd}")

        # =====================================
        # GLOBAL STOP
        # =====================================

        if cmd in [
            "ok",
            "okay",
            "stop",
            "stop everything",
            "cancel",
            "emergency stop",
            "shutdown movement"
        ]:

            emergency_stop()

            return jsonify({
                "status": "stopped",
                "message": "Robot stopped"
            })

        # =====================================
        # BUSY CHECK
        # =====================================

        busy_task = get_task()

        if busy_task is not None:

            return jsonify({
                "status": "busy",
                "current_task": busy_task
            })

        # =====================================
        # SIMPLE COMMANDS
        # =====================================

        if cmd in SIMPLE_COMMANDS:

            SIMPLE_COMMANDS[cmd]()

            add_log(
                f"✅ Executed: {cmd}"
            )

            return jsonify({
                "status": "executed",
                "command": cmd
            })

        # =====================================
        # DANCE
        # =====================================

        elif cmd == "dance":

            run_background_task(
                "dance",
                dance
            )

            return jsonify({
                "status": "started",
                "task": "dance"
            })

        # =====================================
        # FIND / SEARCH
        # =====================================

        elif any(
            word in cmd
            for word in [
                "find",
                "look for",
                "search for"
            ]
        ):

            target = (
                cmd.replace(
                    "look for",
                    ""
                )
                .replace(
                    "search for",
                    ""
                )
                .replace(
                    "find",
                    ""
                )
                .strip()
            )

            if not target:

                return jsonify({
                    "status": "error",
                    "message": "No target specified"
                })

            add_log(
                f"🔍 Finding: {target}"
            )

            run_background_task(
                f"find:{target}",
                find.find,
                target
            )

            return jsonify({
                "status": "started",
                "task": "find",
                "target": target
            })

        # =====================================
        # INTERNET SEARCH
        # =====================================

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

            add_log(
                f"🌐 Internet search: {cmd}"
            )

            run_background_task(
                "internet_search",
                internet.assistant_search,
                cmd,
                True
            )

            return jsonify({
                "status": "started",
                "task": "internet_search"
            })

        # =====================================
        # UNKNOWN
        # =====================================

        else:

            add_log(
                f"❌ Unknown command: {cmd}"
            )

            return jsonify({
                "status": "unknown",
                "command": cmd
            })

    except Exception as e:

        add_log(f"❌ ERROR: {str(e)}")

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# =====================================
# LOG ROUTE
# =====================================

@app.route('/logs', methods=['GET'])
def get_logs():

    return jsonify({
        "logs": logs
    })

# =====================================
# MAIN
# =====================================

if __name__ == '__main__':

    print(
        "🔥 Starting Robot Server..."
    )

    add_log(
        "🔥 Robot server booting"
    )

    servo.initialize_robot()

    smallFaces.neutral()

    add_log(
        "✅ Robot initialized"
    )

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
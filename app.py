from flask import Flask, request, jsonify
from datetime import datetime

import motor
import servo
import internet
import find
import smallFaces
import time 

app = Flask(__name__)

# ==============================
# 🕺 DANCE MODE
# ==============================

def dance():

    add_log("🕺 Dance mode started")

    smallFaces.happy()

    # Open hands first
    servo.left_release()
    servo.right_release()

    # Dance loop
    for _ in range(3):

        # ---------------------------------
        # BOTH UP
        # ---------------------------------
        servo.left_rotate_up()
        servo.right_rotate_up()

        servo.move_neck(60)

        motor.forward(0.6)

        # ---------------------------------
        # LEFT UP / RIGHT DOWN
        # ---------------------------------
        servo.left_rotate_up()
        servo.right_rotate_down()

        servo.move_neck(120)

        motor.left(0.3)

        time.sleep(0.3)

        # ---------------------------------
        # LEFT DOWN / RIGHT UP
        # ---------------------------------
        servo.left_rotate_down()
        servo.right_rotate_up()

        servo.move_neck(40)

        motor.right(0.3)

        # ---------------------------------
        # BOTH DOWN
        # ---------------------------------
        servo.left_rotate_down()
        servo.right_rotate_down()

        servo.move_neck(140)

        motor.backward(0.6)

    # ---------------------------------
    # RESET ROBOT
    # ---------------------------------
    servo.left_rotate_center()
    servo.right_rotate_center()

    servo.move_neck(
        servo.NECK_CENTER
    )

    motor.stop()

    smallFaces.neutral()

    add_log("✅ Dance completed")

# ==============================
# SIMPLE COMMANDS
# ==============================

SIMPLE_COMMANDS = {

    # ==========================
    # 🚗 MOTOR CONTROL
    # ==========================

    "forward": motor.forward,
    "backward": motor.backward,
    "left": motor.left,
    "right": motor.right,
    "stop": motor.stop,

    # ==========================
    # 🤖 LEFT ARM
    # ==========================

    "left grip": servo.left_grip,
    "left release": servo.left_release,

    "left extend": servo.left_extend,
    "left retract": servo.left_retract,

    "left arm up": servo.left_rotate_up,
    "left arm down": servo.left_rotate_down,
    "left arm center": servo.left_rotate_center,

    # ==========================
    # 🤖 RIGHT ARM
    # ==========================

    "right grip": servo.right_grip,
    "right release": servo.right_release,

    "right extend": servo.right_extend,
    "right retract": servo.right_retract,

    "right arm up": servo.right_rotate_up,
    "right arm down": servo.right_rotate_down,
    "right arm center": servo.right_rotate_center,

    # ==========================
    # 🤖 BOTH ARMS
    # ==========================

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

    # ==========================
    # 🤖 COMPATIBILITY COMMANDS
    # ==========================

    "grip": servo.left_grip,
    "release": servo.left_release,

    "dance": dance,
}

# ==============================
# LOG SYSTEM
# ==============================

logs = []

def add_log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    logs.append(log_entry)
    print(log_entry)


# ==============================
# HOME ROUTE
# ==============================

@app.route('/')
def home():
    return "✅ Robot Server Running"


# ==============================
# COMMAND ROUTE
# ==============================

@app.route('/command', methods=['POST'])
def command():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON received"
            }), 400

        cmd = data.get("command", "").lower()

        add_log(f"📥 Command: {cmd}")
        
        # =====================================
        # 🛑 GLOBAL STOP
        # =====================================

        if cmd.strip() in [
            "ok", "okay", "stop",
            "stop everything",
            "emergency stop",
            "shutdown movement",
            "cancel"
        ]:
            add_log("🛑 Emergency stop triggered")

            # Stop motors
            motor.stop()

            # Optional:
            # Stop servos safely
            servo.left_rotate_center()
            servo.right_rotate_center()
            smallFaces.neutral()

            # Optional:
            # Stop speaking
            # speak.stop()

            return jsonify({
                "status": "stopped",
                "message": "All processes stopped"
            })

        # =====================================
        # 🚗 MOTOR CONTROL
        # =====================================

        if cmd in SIMPLE_COMMANDS:

            SIMPLE_COMMANDS[cmd]()

            add_log(f"✅ Executed: {cmd}")

            return jsonify({
                "status": "executed",
                "command": cmd
            })

        # =====================================
        # 👀 FIND / LOOK COMMAND
        # =====================================

        elif any(word in cmd for word in ["find", "look for", "search for"]):

            # Examples:
            # "find bottle"
            # "look for person"
            # "search for chair"

            target = (
                cmd.replace("look for", "")
                   .replace("search for", "")
                   .replace("find", "")
                   .strip()
            )

            if not target:

                return jsonify({
                    "status": "error",
                    "message": "No target specified"
                })

            add_log(f"👀 Finding: {target}")

            result = find.find(target)

            return jsonify({
                "status": "find_complete",
                "target": target,
                "found": result
            })
        # =====================================
        # 🌐 INTERNET QUERY
        # =====================================

        elif any(cmd.startswith(word) for word in [
            "what",
            "who",
            "where",
            "when",
            "why",
            "how",
            "tell me",
            "search"
        ]):

            add_log(f"🌐 Internet search: {cmd}")

            result = internet.assistant_search(
                query=cmd,
                voice=True
            )

            add_log(f"🌐 Result: {result}")

            return jsonify({
                "status": "internet",
                "response": result
            })

        # =====================================
        # ❌ UNKNOWN COMMAND
        # =====================================

        else:

            add_log("❌ Unknown command")

            return jsonify({
                "status": "unknown command",
                "command": cmd
            })
            smallFaces.neutral()

        return jsonify({
            "status": "executed",
            "command": cmd
        })

    except Exception as e:

        add_log(f"❌ ERROR: {str(e)}")

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ==============================
# LOG ROUTE
# ==============================

@app.route('/logs', methods=['GET'])
def get_logs():
    return jsonify({"logs": logs})


# ==============================
# MAIN
# ==============================

if __name__ == '__main__':

    print("🔥 Starting Robot Server...")

    servo.initialize_robot()

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
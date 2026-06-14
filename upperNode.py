import serial
import serial.tools.list_ports
import time
import threading
import json
import os

# ==============================
# CONFIG
# ==============================

BAUD = 115200

esp = None

servo_node_connected = False

servo_port = None

serial_lock = threading.Lock()

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PORTS_FILE = os.path.join(
    BASE_DIR,
    "node_ports.json"
)

def load_ports():

    if not os.path.exists(PORTS_FILE):
        return {}

    try:

        with open(PORTS_FILE, "r") as f:
            return json.load(f)

    except:
        return {}

def save_ports(data):

    with open(PORTS_FILE, "w") as f:

        json.dump(
            data,
            f,
            indent=2
        )

def try_port(port_name, expected_id):

    try:

        print(
            f"🔍 Checking {port_name}"
        )

        ser = serial.Serial(
            port_name,
            BAUD,
            timeout=2
        )

        # ESP32 reboot delay
        time.sleep(2)

        ser.reset_input_buffer()

        ser.write(
            b'WHO_ARE_YOU\n'
        )

        time.sleep(0.5)

        response = (
            ser.readline()
            .decode(errors='ignore')
            .strip()
        )

        print(
            f"📨 Response: {response}"
        )

        if response == expected_id:

            print(
                f"✅ {expected_id} found "
                f"on {port_name}"
            )

            return ser
        print(f"⚠️ Wrong device on {port_name}: {response}")
        ser.close()

    except Exception as e:

        print(
            f"❌ Failed on "
            f"{port_name}: {e}"
        )

    return None
       
# ==============================
# FIND NODE ONLY ONCE
# ==============================

def find_servo_node():

    ports_cache = load_ports()

    cached_port = ports_cache.get(
        "SERVO_NODE"
    )

    # ==========================
    # TRY CACHED PORT FIRST
    # ==========================

    if cached_port:

        print(
            f"🔄 Trying cached port "
            f"{cached_port}"
        )

        ser = try_port(
            cached_port,
            "SERVO_NODE"
        )

        if ser:
            return ser

        print(
            "⚠️ Cached port failed"
        )

    # ==========================
    # FALLBACK SCAN
    # ==========================

    print("🔍 Scanning all ports...")

    ports = [

        port

        for port in serial.tools
        .list_ports
        .comports()

        if port.device.startswith(
            "/dev/ttyACM"
        )
    ]

    for port in ports:

        ser = try_port(
            port.device,
            "SERVO_NODE"
        )

        if ser:

            ports_cache[
                "SERVO_NODE"
            ] = port.device

            save_ports(
                ports_cache
            )

            return ser

    return None

# ==============================
# CONNECT
# ==============================

def connect_servo_node():

    global esp
    global servo_node_connected
    global servo_port

    try:

        # ==================================
        # USE STORED PORT
        # ==================================

        if servo_port is not None:

            print(
                f"🔄 Reconnecting to "
                f"{servo_port}"
            )

            esp = serial.Serial(
                servo_port,
                BAUD,
                timeout=2
            )

            time.sleep(2)

        else:

            esp = find_servo_node()

        if esp is None:

            raise Exception(
                "SERVO_NODE not found"
            )

        servo_node_connected = True

        print(
            "✅ Servo node connected"
        )

        return True

    except Exception as e:

        print(
            f"❌ Servo node failed: {e}"
        )

        try:
            esp.close()
        except:
            pass

        esp = None

        servo_node_connected = False

        return False

# Initial connect
connect_servo_node()

# ==============================
# MONITOR
# ==============================

def monitor_connection():

    global esp
    global servo_node_connected

    while True:

        try:

            if esp is None or not esp.is_open:

                connect_servo_node()

            else:

                with serial_lock:

                    esp.reset_input_buffer()

                    esp.write(b'PING\n')

                    time.sleep(0.2)

                    response = (
                        esp.readline()
                        .decode(errors='ignore')
                        .strip()
                    )

                # Ignore occasional blanks
                if response not in [
                    "PONG",
                    ""
                ]:

                    raise Exception(
                        f"Bad heartbeat: "
                        f"{response}"
                    )

        except Exception as e:

            print(
                f"❌ Servo disconnected: {e}"
            )

            try:
                esp.close()
            except:
                pass

            esp = None

            servo_node_connected = False

        time.sleep(5)

threading.Thread(

    target=monitor_connection,

    daemon=True

).start()

# ==============================
# SEND
# ==============================

def send(cmd):

    global esp

    for attempt in range(3):

        try:

            if esp is None or not esp.is_open:

                if not connect_servo_node():

                    continue

            with serial_lock:

                esp.write(
                    f"{cmd}\n".encode()
                )

            return True

        except Exception as e:

            print(
                f"❌ Send failed: {e}"
            )

            try:
                esp.close()
            except:
                pass

            esp = None

            time.sleep(1)

    print(
        f"❌ Skipping: {cmd}"
    )

    return False
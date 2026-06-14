import serial
import time
import threading
import serial.tools.list_ports
import json
import os

# ==============================
# CONFIG
# ==============================

BAUD = 115200

esp = None

base_connected = False

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
# FIND BASE NODE
# ==============================

def find_base_node():

    ports_cache = load_ports()

    cached_port = ports_cache.get(
        "BASE_NODE"
    )

    if cached_port:

        print(
            f"🔄 Trying cached port "
            f"{cached_port}"
        )

        ser = try_port(
            cached_port,
            "BASE_NODE"
        )

        if ser:
            return ser

        print(
            "⚠️ Cached port failed"
        )
    
    print("🔍 Scanning all ports...")

    ports = [

        port

        for port in serial.tools
        .list_ports
        .comports()

        if port.device.startswith(
            "/dev/ttyUSB"
        )
    ]

    for port in ports:

        ser = try_port(
            port.device,
            "BASE_NODE"
        )

        if ser:

            ports_cache[
                "BASE_NODE"
            ] = port.device

            save_ports(
                ports_cache
            )

            return ser

    return None

def connect_esp():

    global esp
    global base_connected

    try:

        print(
            "🔍 Searching "
            "for BASE_NODE"
        )

        esp = find_base_node()

        if esp is None:

            raise Exception(
                "BASE_NODE not found"
            )

        print("✅ Base connected")

        base_connected = True

        return True

    except Exception as e:

        print(f"❌ Base connection failed: {e}")

        try:
            esp.close()
        except:
            pass

        esp = None

        base_connected = False

        return False

# ==============================
# INITIAL CONNECTION
# ==============================

connect_esp()

# ==============================
# MONITOR THREAD
# ==============================

def monitor_connection():

    global esp
    global base_connected

    while True:

        if esp is None or not esp.is_open:

            connect_esp()

        else:

            try:

                # Heartbeat
                with serial_lock:

                    esp.write(b'PING\n')

                    time.sleep(0.2)

                    response = (
                        esp.readline()
                        .decode(errors='ignore')
                        .strip()
                    )

                if response != "PONG":

                    esp.reset_input_buffer()
                    esp.reset_output_buffer()

                    raise Exception(
                        f"Heartbeat failed: "
                        f"{response}"
                    )

            except Exception as e:

                print(f"❌ Base disconnected: {e}")

                try:
                    esp.close()
                except:
                    pass

                esp = None

                base_connected = False

        time.sleep(5)

# Start monitor thread
threading.Thread(
    target=monitor_connection,
    daemon=True
).start()

# ==============================
# SEND COMMAND
# ==============================

def send(cmd):

    global esp

    for attempt in range(3):

        try:

            if esp is None or not esp.is_open:

                print(
                    f"🔄 Reconnecting "
                    f"(Attempt {attempt+1}/3)"
                )

                if not connect_esp():
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

    print("❌ Skipping command")

    return False
# ==============================
# MOVEMENT FUNCTIONS
# ==============================

def forward():
    send('F')

def backward():
    send('B')

def left(duration=None):

    send('L')

    if duration is not None:

        time.sleep(duration)

        stop()

def right(duration=None):

    send('R')

    if duration is not None:

        time.sleep(duration)

        stop()

def stop():
    send('S')
import serial
import serial.tools.list_ports
import time
import threading

from speak import speak

# ==============================
# CONFIG
# ==============================

BAUD = 115200

esp = None

servo_node_connected = False

last_spoken_state = None

# ==============================
# SPEAK STATE CHANGES
# ==============================

def speak_state(state):

    global last_spoken_state

    if last_spoken_state == state:
        return

    last_spoken_state = state

    speak(state)

# ==============================
# FIND SERVO NODE
# ==============================

def find_servo_node():

    ports = serial.tools.list_ports.comports()

    for port in ports:

        try:

            print(f"🔍 Checking {port.device}")

            ser = serial.Serial(
                port.device,
                BAUD,
                timeout=2
            )

            time.sleep(2)

            ser.reset_input_buffer()

            # Ask identity
            ser.write(b'WHO_ARE_YOU\n')

            time.sleep(0.5)

            response = (
                ser.readline()
                .decode()
                .strip()
            )

            print(f"📨 Response: {response}")

            if response == "SERVO_NODE":

                print(f"✅ SERVO_NODE found on {port.device}")

                return ser

            ser.close()

        except Exception as e:

            print(f"❌ Failed: {e}")

    return None

# ==============================
# CONNECT
# ==============================

def connect_servo_node():

    global esp
    global servo_node_connected

    try:

        esp = find_servo_node()

        if esp is None:

            raise Exception(
                "SERVO_NODE not found"
            )

        servo_node_connected = True

        print("✅ Servo node connected")

        speak_state("Arms connected")
        speak_state("LCD connected")

        return True

    except Exception as e:

        print(f"❌ Servo node failed: {e}")

        try:
            esp.close()
        except:
            pass

        esp = None

        if servo_node_connected:

            speak_state("Servo node disconnected")

        else:

            speak_state("Servo node not connected")

        servo_node_connected = False

        return False

# Initial connect
connect_servo_node()

# ==============================
# MONITOR THREAD
# ==============================

def monitor_connection():

    global esp
    global servo_node_connected

    while True:

        if esp is None or not esp.is_open:

            connect_servo_node()

        else:

            try:

                esp.write(b'PING\n')

                time.sleep(0.2)

                response = (
                    esp.readline()
                    .decode()
                    .strip()
                )

                if response != "PONG":

                    raise Exception(
                        "Heartbeat failed"
                    )

            except Exception as e:

                print(f"❌ Servo node disconnected: {e}")

                try:
                    esp.close()
                except:
                    pass

                esp = None

                servo_node_connected = False

                speak_state(
                    "Servo node disconnected"
                )

        time.sleep(5)

threading.Thread(
    target=monitor_connection,
    daemon=True
).start()

# ==============================
# SEND FUNCTION
# ==============================

def send(cmd):

    global esp

    if esp is None or not esp.is_open:

        print("🔄 Reconnecting SERVO_NODE")

        if not connect_servo_node():

            return False

    try:

        esp.write(f"{cmd}\n".encode())

        return True

    except Exception as e:

        print(f"❌ Send failed: {e}")

        return False
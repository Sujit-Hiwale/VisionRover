import serial
import time
import threading

from speak import speak

# ==============================
# CONFIG
# ==============================

PORT = '/dev/serial0'
BAUD = 115200

esp = None

base_connected = False

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
# CONNECT FUNCTION
# ==============================

def connect_esp():

    global esp
    global base_connected

    try:

        print(f"🔍 Connecting to base on {PORT}")

        esp = serial.Serial(
            PORT,
            BAUD,
            timeout=2
        )

        time.sleep(2)

        # Clear garbage
        esp.reset_input_buffer()

        # Ask identity
        esp.write(b'WHO_ARE_YOU\n')

        time.sleep(0.5)

        response = (
            esp.readline()
            .decode()
            .strip()
        )

        print(f"📨 Response: {response}")

        # Verify node
        if response != "BASE_NODE":

            print("❌ Wrong device connected")

            esp.close()

            esp = None

            base_connected = False

            speak_state("Base not connected")

            return False

        print("✅ Base connected")

        base_connected = True

        speak_state("Base connected")

        return True

    except Exception as e:

        print(f"❌ Base connection failed: {e}")

        try:
            esp.close()
        except:
            pass

        esp = None

        if base_connected:

            speak_state("Base disconnected")

        else:

            speak_state("Base not connected")

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

                print(f"❌ Base disconnected: {e}")

                try:
                    esp.close()
                except:
                    pass

                esp = None

                base_connected = False

                speak_state("Base disconnected")

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
    global base_connected

    # Auto reconnect
    if esp is None or not esp.is_open:

        print("🔄 Trying to reconnect base...")

        if not connect_esp():

            print("❌ Cannot send command")

            return False

    try:

        esp.write(f"{cmd}\n".encode())

        return True

    except Exception as e:

        print(f"❌ Send failed: {e}")

        try:
            esp.close()
        except:
            pass

        esp = None

        base_connected = False

        speak_state("Base disconnected")

        return False

# ==============================
# MOVEMENT FUNCTIONS
# ==============================

def forward():
    send('F')

def backward():
    send('B')

def left():
    send('L')

def right():
    send('R')

def stop():
    send('S')
import subprocess
import threading
import queue

import smallFaces

# ==============================
# SPEECH QUEUE
# ==============================

speech_queue = queue.Queue()

is_speaking = False

speech_lock = threading.Lock()

# ==============================
# SPEAK WORKER
# ==============================

def speech_worker():

    global is_speaking

    while True:

        text = speech_queue.get()

        if not text:
            continue

        with speech_lock:

            is_speaking = True
            print(f"🗣 Speaking: {text}")

            try:

                # Save current face
                previous_mode = (
                    smallFaces.current_mode
                )

                # Talking face
                smallFaces.set_mode(
                    "talking"
                )

                process = subprocess.Popen([
                    'espeak-ng',
                    '-s', '125',
                    '-p', '70',
                    '-a', '180',
                    text
                ])

                process.wait()

                # Restore face
                smallFaces.set_mode(
                    previous_mode
                )

            except Exception as e:

                print(
                    f"Speech error: {e}"
                )

            is_speaking = False

# ==============================
# START WORKER THREAD
# ==============================

threading.Thread(
    target=speech_worker,
    daemon=True
).start()

# ==============================
# PUBLIC SPEAK FUNCTION
# ==============================

def speak(text):

    if not text:
        return

    speech_queue.put(text)
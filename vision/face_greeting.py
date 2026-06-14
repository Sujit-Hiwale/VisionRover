import sys
import os

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)
import time
from vision import vision_controller, face_module
import speak

last_greeted = {}
COOLDOWN = 10

def greet(name):
    print(f"👋 Greeting {name}")
    speak.speak(f"Hello {name}")


def face_monitor(get_frame):

    print("👁 Face monitor started")

    while True:

        # -----------------------------
        # HARD BLOCK IF OBJECT MODE
        # -----------------------------
        if not vision_controller.can_run("face"):
            time.sleep(0.2)
            continue

        frame = get_frame()
        if frame is None:
            time.sleep(0.1)
            continue

        face = face_module.recognize_face(frame)

        if face is None:
            continue

        name = face["name"]
        now = time.time()

        if name not in last_greeted or now - last_greeted[name] > COOLDOWN:

            last_greeted[name] = now

            vision_controller.set_mode("face")

            greet(name)

            time.sleep(2)

            vision_controller.set_mode("idle")
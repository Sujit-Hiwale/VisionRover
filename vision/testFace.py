import cv2
import time
import threading

from vision.camera import (
    start_camera,
    get_latest_frame
)

from vision.face_greeting import face_monitor
from vision import face_module

print("📷 Starting camera")

start_camera()

time.sleep(2)

print("🚀 Starting face greeting test")

# =====================================
# START FACE MONITOR
# =====================================

vision_thread = threading.Thread(
    target=face_monitor,
    args=(get_latest_frame,),
    daemon=True
)

vision_thread.start()

print("👁 Face monitor thread started")

# =====================================
# DEBUG VIEW
# =====================================

while True:

    frame = get_latest_frame()

    if frame is None:

        print("❌ No frame")

        time.sleep(0.1)

        continue

    # -----------------------------
    # FACE RECOGNITION DEBUG
    # -----------------------------

    face = face_module.recognize_face(frame)

    if face is not None:

        print(f"✅ FACE DETECTED: {face}")

        name = face.get(
            "name",
            "Unknown"
        )

        cv2.putText(
            frame,
            f"Hello {name}",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

    else:

        print("❌ No face detected")

    # -----------------------------
    # SHOW CAMERA
    # -----------------------------

    cv2.imshow(
        "Face Debug View",
        frame
    )

    key = cv2.waitKey(1)

    if key == ord('q'):

        break

cv2.destroyAllWindows()
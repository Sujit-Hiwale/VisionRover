import cv2
import time
import sys
import os

# =====================================
# PATH FIX (so imports work anywhere)
# =====================================

sys.path.append(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

# =====================================
# IMPORT YOUR MODULES
# =====================================

from vision.camera import start_camera, get_latest_frame
from vision.trace import scan_for_object, track_object, find_and_reach

# =====================================
# CONFIG
# =====================================

TARGET = "bottle"

# =====================================
# START CAMERA
# =====================================

print("🚀 Starting camera...")
start_camera()

time.sleep(2)

print(f"🎯 Test target: {TARGET}")

# =====================================
# STATE
# =====================================

mode = "scan"   # scan → track → reach

detection = None

# =====================================
# MAIN LOOP
# =====================================

while True:

    frame = get_latest_frame()

    if frame is None:
        continue

    # =================================
    # MODE 1: SCANNING
    # =================================

    if mode == "scan":

        print("🔎 Scanning...")

        detection = scan_for_object(TARGET, timeout=10)

        if detection:

            print("🎯 Target found!")

            mode = "track"

        else:

            print("❌ Not found in scan cycle, retrying...")

            time.sleep(1)

    # =================================
    # MODE 2: TRACK + APPROACH
    # =================================

    elif mode == "track":

        print("📍 Tracking...")

        reached = track_object(TARGET)

        if reached:

            print("✅ Reached target!")

            mode = "done"

        time.sleep(0.1)

    # =================================
    # MODE 3: DONE
    # =================================

    elif mode == "done":

        print("🏁 Task complete")

        cv2.putText(
            frame,
            "TARGET REACHED",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

    # =================================
    # SHOW LIVE FEED
    # =================================

    cv2.putText(
        frame,
        f"MODE: {mode}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 0),
        2
    )

    cv2.imshow("TRACE TEST", frame)

    # =================================
    # EXIT
    # =================================

    key = cv2.waitKey(1)

    if key == ord("q"):
        break

# =====================================
# CLEANUP
# =====================================

cv2.destroyAllWindows()

print("🛑 Test stopped")
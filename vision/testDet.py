import cv2
import time
import os

from camera import (
    start_camera,
    stop_camera,
    get_latest_frame
)

from ultralytics import YOLO

# =====================================
# LOAD YOLO MODEL
# =====================================

print("🧠 Loading YOLO model...")

model = YOLO("yolov8n.pt")

print("✅ YOLO loaded")

# =====================================
# START CAMERA
# =====================================

print("🚀 Starting Vision Test")

start_camera()

# Give camera time to warm up
time.sleep(2)

# =====================================
# FPS TRACKING
# =====================================

prev_time = time.time()

# Prevent speech spam
last_spoken = ""

last_speak_time = 0

# =====================================
# MAIN LOOP
# =====================================

try:

    while True:

        # ================================
        # GET FRAME
        # ================================

        frame = get_latest_frame()

        if frame is None:
            continue

        # ================================
        # RUN YOLO DETECTION
        # ================================

        results = model(
            frame,
            verbose=False
        )

        detected_objects = []

        # ================================
        # PROCESS DETECTIONS
        # ================================

        for result in results:

            boxes = result.boxes

            for box in boxes:

                confidence = float(
                    box.conf[0]
                )

                # Ignore weak detections
                if confidence < 0.5:
                    continue

                class_id = int(
                    box.cls[0]
                )

                label = model.names[
                    class_id
                ]

                detected_objects.append(
                    label
                )

                # ================================
                # DRAW BOX
                # ================================

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                # ================================
                # DRAW LABEL
                # ================================

                cv2.putText(
                    frame,
                    f"{label} {confidence:.2f}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

        # ================================
        # SPEAK DETECTED OBJECTS
        # ================================

        current_time = time.time()

        if detected_objects:

            unique_objects = list(
                set(detected_objects)
            )

            objects_text = ", ".join(
                unique_objects
            )

            # Prevent repeated speech spam
            if (
                objects_text != last_spoken
                or current_time - last_speak_time > 5
            ):

                print(
                    f"🎯 Detected: {objects_text}"
                )

                os.system(
                    f'espeak "{objects_text}"'
                )

                last_spoken = objects_text

                last_speak_time = current_time

        # ================================
        # FPS DISPLAY
        # ================================

        current_fps_time = time.time()

        fps = 1 / (
            current_fps_time - prev_time
        )

        prev_time = current_fps_time

        cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        # ================================
        # HEADLESS MODE
        # ================================

        # No imshow on headless Pi
        time.sleep(0.01)

except KeyboardInterrupt:

    print("\n🛑 Stopping Vision Test")

# =====================================
# CLEANUP
# =====================================

stop_camera()

print("✅ Vision Test Stopped")
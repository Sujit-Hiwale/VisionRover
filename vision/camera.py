import cv2
import threading
import time

# =====================================
# CAMERA BUFFER
# =====================================

class CameraBuffer:

    def __init__(self):

        self.lock = threading.Lock()

        self.latest_frame = None

        self.running = False

camera_buffer = CameraBuffer()

# =====================================
# CAMERA THREAD
# =====================================

def _camera_worker():

    print("🎥 Camera thread started")

    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():

        print("❌ Failed to open camera")

        return

    while camera_buffer.running:

        success, frame = cap.read()

        if success:

            with camera_buffer.lock:

                camera_buffer.latest_frame = frame

        time.sleep(0.01)

    cap.release()

    print("🛑 Camera thread stopped")

# =====================================
# START CAMERA
# =====================================

def start_camera():

    if camera_buffer.running:
        return

    camera_buffer.running = True

    thread = threading.Thread(
        target=_camera_worker,
        daemon=True
    )

    thread.start()

# =====================================
# STOP CAMERA
# =====================================

def stop_camera():

    camera_buffer.running = False

# =====================================
# GET FRAME
# =====================================

def get_latest_frame():

    with camera_buffer.lock:

        if camera_buffer.latest_frame is None:
            return None

        return camera_buffer.latest_frame.copy()
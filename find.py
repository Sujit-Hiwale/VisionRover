from ultralytics import YOLO
import cv2
import time

# -----------------------------
# YOUR MODULES
# -----------------------------
import motor
import face
import smallFaces
import speak
import servo
import robot_state

# -----------------------------
# CONFIG
# -----------------------------
YOLO_SIZE = 320

YOLO_CONF = 0.45

DEBUG_VIEW = True

# -----------------------------
# SEARCH CONFIG
# -----------------------------
SCAN_ANGLES = [
    90,
    65,
    40,
    20,
    40,
    65,
    90,
    115,
    140,
    160,
    140,
    115,
    90
]

MAX_ROTATIONS = 8

CENTER_TOLERANCE = 60

CLOSE_WIDTH = 170

# -----------------------------
# LOAD YOLO
# -----------------------------
model = YOLO("yolo11n.pt")

# -----------------------------
# CAMERA
# -----------------------------
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)

cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

time.sleep(2)

# -----------------------------
# EXPRESSIONS
# -----------------------------
def set_expression(mode):

    expressions = {
        "searching": smallFaces.searching,
        "found": smallFaces.found,
        "not_found": smallFaces.not_found,
        "turning": smallFaces.turning,
    }

    expressions.get(
        mode,
        smallFaces.neutral
    )()

# -----------------------------
# CHECK INTERRUPT
# -----------------------------
def interrupted():

    if robot_state.interrupt_requested:

        print("🛑 Search interrupted")

        robot_state.interrupt_requested = False

        motor.stop()

        servo.move_neck(
            servo.NECK_CENTER
        )

        smallFaces.neutral()

        return True

    return False

# -----------------------------
# DETECT TARGET
# -----------------------------
def detect_target(target_name):

    ret, frame = cap.read()

    # =================================
    # ALWAYS SHOW CAMERA
    # =================================

    if DEBUG_VIEW:

        cv2.imshow(
            "Robot Vision",
            frame
        )

        cv2.waitKey(1)

    if not ret:
        return None

    target_name = target_name.lower()

    # -----------------------------
    # KNOWN FACE SEARCH
    # -----------------------------
    if face.is_known_person(
        target_name
    ):

        result = face.recognize_face(
            frame
        )

        if result is not None:

            recognized_name = (
                result["name"]
                .lower()
            )

            if recognized_name == target_name:

                x, y, w, h = (
                    result["box"]
                )

                center_x = x + w // 2

                return {
                    "found": True,
                    "center_x": center_x,
                    "width": w,
                    "type": "face"
                }

    # -----------------------------
    # GENERIC PERSON SEARCH
    # -----------------------------
    elif target_name == "person":

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = (
            face.face_detector
            .detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(80, 80)
            )
        )

        if len(faces) > 0:

            x, y, w, h = faces[0]

            center_x = x + w // 2

            return {
                "found": True,
                "center_x": center_x,
                "width": w,
                "type": "person"
            }

    # -----------------------------
    # YOLO OBJECT SEARCH
    # -----------------------------
    else:

        results = model(
            frame,
            imgsz=YOLO_SIZE,
            conf=YOLO_CONF,
            verbose=False
        )

        for r in results:

            for box in r.boxes:

                cls_id = int(
                    box.cls[0]
                )

                label = (
                    model.names[cls_id]
                    .lower()
                )

                confidence = float(
                    box.conf[0]
                )

                if confidence < YOLO_CONF:
                    continue

                if label == target_name:

                    x1, y1, x2, y2 = map(
                        int,
                        box.xyxy[0]
                    )

                    width = x2 - x1

                    center_x = (
                        x1 + x2
                    ) // 2

                    # -----------------------------
                    # DEBUG WINDOW
                    # -----------------------------
                    if DEBUG_VIEW:

                        annotated = (
                            results[0].plot()
                        )

                        cv2.imshow(
                            "Robot Vision",
                            annotated
                        )

                        cv2.waitKey(1)

                    return {
                        "found": True,
                        "center_x": center_x,
                        "width": width,
                        "type": "object"
                    }

    return None

# -----------------------------
# TRACK TARGET
# -----------------------------
def track_target(target_name):

    print(
        f"🎯 Tracking {target_name}"
    )

    announced_found = False

    while True:

        # -----------------------------
        # INTERRUPT
        # -----------------------------
        if interrupted():
            return False

        data = detect_target(
            target_name
        )

        # -----------------------------
        # LOST TARGET
        # -----------------------------
        if data is None:

            print("❌ Target lost")

            motor.stop()

            return False

        # -----------------------------
        # FOUND
        # -----------------------------
        if not announced_found:

            set_expression("found")

            speak.speak(
                f"{target_name} found"
            )

            announced_found = True

        center_x = data["center_x"]

        width = data["width"]

        error = center_x - 320

        # -----------------------------
        # ALIGN ROBOT
        # -----------------------------
        if error < -CENTER_TOLERANCE:

            print("⬅️ Target Left")

            motor.left(0.2)

        elif error > CENTER_TOLERANCE:

            print("➡️ Target Right")

            motor.right(0.2)

        else:

            motor.stop()

        # -----------------------------
        # MOVE FORWARD
        # -----------------------------
        if width < CLOSE_WIDTH:

            print(
                "🚗 Approaching target"
            )

            motor.forward()

        else:

            print("🛑 Target reached")

            motor.stop()

            return True

        time.sleep(0.1)

# -----------------------------
# SCAN AREA
# -----------------------------
def scan_area(target_name):

    set_expression("searching")

    print("🔍 Scanning area")

    for angle in SCAN_ANGLES:

        # -----------------------------
        # INTERRUPT
        # -----------------------------
        if interrupted():
            return False

        servo.move_neck(angle)

        time.sleep(0.25)

        data = detect_target(
            target_name
        )

        if data is not None:

            motor.stop()

            servo.move_neck(
                servo.NECK_CENTER
            )

            return True

    return False

# -----------------------------
# ROTATE BODY
# -----------------------------
def rotate_body():

    set_expression("turning")

    print("🔄 Rotating robot")

    motor.left(0.7)

    time.sleep(0.4)

    motor.stop()

# -----------------------------
# MAIN FIND FUNCTION
# -----------------------------
def find(target_name):

    target_name = (
        target_name
        .strip()
        .lower()
    )

    robot_state.interrupt_requested = False

    print(
        f"\n🔍 Looking for {target_name}"
    )

    speak.speak(
        f"Looking for {target_name}"
    )

    servo.move_neck(
        servo.NECK_CENTER
    )

    rotation_count = 0

    # -----------------------------
    # SEARCH LOOP
    # -----------------------------
    while rotation_count < MAX_ROTATIONS:

        # -----------------------------
        # INTERRUPT
        # -----------------------------
        if interrupted():
            return False

        found = scan_area(
            target_name
        )

        # -----------------------------
        # FOUND
        # -----------------------------
        if found:

            print(
                f"✅ {target_name} found"
            )

            return track_target(
                target_name
            )

        # -----------------------------
        # ROTATE BODY
        # -----------------------------
        rotate_body()

        rotation_count += 1

    # -----------------------------
    # NOT FOUND
    # -----------------------------
    motor.stop()

    servo.move_neck(
        servo.NECK_CENTER
    )

    set_expression("not_found")

    speak.speak(
        f"{target_name} not found"
    )

    print(
        f"❌ {target_name} not found"
    )

    return False

# -----------------------------
# STOP SEARCH
# -----------------------------
def stop_search():

    robot_state.interrupt_requested = True

# -----------------------------
# CLEANUP
# -----------------------------
def cleanup():

    print("🧹 Cleaning up")

    cap.release()

    cv2.destroyAllWindows()

    motor.stop()

# -----------------------------
# TEST
# -----------------------------
if __name__ == "__main__":

    try:

        print("✅ Find module loaded")

    except KeyboardInterrupt:

        print("🛑 Interrupted")

    finally:

        cleanup()
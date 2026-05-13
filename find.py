from ultralytics import YOLO
import cv2
import time

# -----------------------------
# Your Modules
# -----------------------------
import motor
import face
import smallFaces
import speak
import servo

# -----------------------------
# CONFIG
# -----------------------------
YOLO_SIZE = 320
YOLO_CONF = 0.45

SEARCH_TIMEOUT = 15

DEBUG_VIEW = False

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

# -----------------------------
# LOAD YOLO
# -----------------------------
model = YOLO("yolo11n.pt")

# -----------------------------
# CAMERA SETUP
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
# DETECT TARGET
# -----------------------------
def detect_target(target_name):

    ret, frame = cap.read()

    if not ret:
        return False

    target_name = target_name.lower()

    # ---------------------------------
    # YOLO INFERENCE
    # ---------------------------------
    results = model(
        frame,
        imgsz=YOLO_SIZE,
        conf=YOLO_CONF,
        verbose=False
    )

    found = False

    # ---------------------------------
    # OPTIONAL DEBUG DRAWING
    # ---------------------------------

    # Uncomment later if needed
    #
    # annotated = results[0].plot()
    #
    # cv2.imshow("Robot Vision", annotated)
    # cv2.waitKey(1)

    # ---------------------------------
    # FACE DETECTION
    # ONLY FOR PERSON
    # ---------------------------------
    if target_name == "person":

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = face.face_detector.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5
        )

        if len(faces) > 0:
            return True

    # ---------------------------------
    # YOLO OBJECT DETECTION
    # ---------------------------------
    for r in results:

        for box in r.boxes:

            cls_id = int(box.cls[0])

            label = model.names[cls_id].lower()

            confidence = float(box.conf[0])

            if confidence < YOLO_CONF:
                continue

            # Exact match only
            if target_name == label:

                found = True

                # ---------------------------------
                # OPTIONAL TARGET TRACKING
                # ---------------------------------

                # Uncomment later if needed

                # x1, y1, x2, y2 = map(
                #     int,
                #     box.xyxy[0]
                # )

                # object_x = (x1 + x2) // 2
                # frame_center = 320

                # error = object_x - frame_center

                # servo.rotate_neck(
                #     int(error * 0.03)
                # )

                break

        if found:
            break

    return found


# -----------------------------
# SCAN AREA
# -----------------------------
def scan_area(target_name):

    set_expression("searching")

    print("🔍 Scanning Area")

    start_time = time.time()

    for angle in SCAN_ANGLES:

        # Timeout protection
        if time.time() - start_time > SEARCH_TIMEOUT:
            break

        servo.move_neck(angle)

        # Small stabilization delay
        time.sleep(0.05)

        if detect_target(target_name):

            motor.stop()

            set_expression("found")

            print(f"✅ {target_name} found")

            speak.speak(f"{target_name} found")

            return True

    return False


# -----------------------------
# ROTATE BODY
# -----------------------------
def rotate_body():

    set_expression("turning")

    print("🔄 Rotating Robot")

    motor.left(0.8)

    time.sleep(0.3)


# -----------------------------
# MAIN FIND FUNCTION
# -----------------------------
def find(target_name):

    target_name = target_name.lower()

    print(f"\n🔍 Looking for {target_name}")

    speak.speak(f"Looking for {target_name}")

    set_expression("searching")

    servo.move_neck(
        servo.NECK_CENTER
    )

    # ---------------------------------
    # FRONT SEARCH
    # ---------------------------------
    found = scan_area(target_name)

    if found:

        servo.move_neck(
            servo.NECK_CENTER
        )

        return True

    # ---------------------------------
    # ROTATE BODY
    # ---------------------------------
    rotate_body()

    # ---------------------------------
    # SECOND SEARCH
    # ---------------------------------
    found = scan_area(target_name)

    if found:

        servo.move_neck(
            servo.NECK_CENTER
        )

        return True

    # ---------------------------------
    # NOT FOUND
    # ---------------------------------
    motor.stop()

    servo.move_neck(
        servo.NECK_CENTER
    )

    set_expression("not_found")

    speak.speak(f"{target_name} not found")

    print(f"❌ {target_name} not found")

    return False


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

        find("person")

    except KeyboardInterrupt:

        print("🛑 Interrupted")

    finally:

        cleanup()
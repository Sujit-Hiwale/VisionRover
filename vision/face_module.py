import cv2
import os
import json

# ==============================
# INIT
# ==============================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(BASE_DIR, "trainer.yml")
LABEL_PATH = os.path.join(BASE_DIR, "labels.json")

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

recognizer = cv2.face.LBPHFaceRecognizer_create()

recognizer_loaded = False

if os.path.exists(MODEL_PATH) and os.path.exists(LABEL_PATH):

    recognizer.read(MODEL_PATH)

    with open(LABEL_PATH, "r") as f:
        label_map = json.load(f)

    label_map = {int(k): v for k, v in label_map.items()}

    recognizer_loaded = True

else:
    print("Face model or labels not found")
    print("Expected:", MODEL_PATH)
    print("Expected:", LABEL_PATH)

# ==============================
# FACE RECOGNITION
# ==============================

def recognize_face(frame):

    if not recognizer_loaded:
        return None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(80, 80)
    )

    for (x, y, w, h) in faces:

        roi = gray[y:y+h, x:x+w]
        roi = cv2.resize(roi, (200, 200))

        try:
            label, conf = recognizer.predict(roi)

            if conf < 70:

                name = label_map.get(label, "Unknown")

                return {
                    "name": name,
                    "confidence": conf,
                    "box": (x, y, w, h)
                }

        except:
            pass

    return None


def detect_person(frame):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(
        gray,
        1.2,
        5,
        minSize=(80, 80)
    )

    if len(faces) == 0:
        return None

    x, y, w, h = faces[0]

    return {
        "center_x": x + w // 2,
        "width": w,
        "box": (x, y, w, h)
    }
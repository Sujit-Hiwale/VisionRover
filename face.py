import cv2
import json
import os

# ==============================
# FACE DETECTOR
# ==============================

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

# ==============================
# FACE RECOGNIZER
# ==============================

recognizer = cv2.face.LBPHFaceRecognizer_create()

MODEL_PATH = "trainer.yml"

LABEL_PATH = "labels.json"

recognizer_loaded = False

# ==============================
# LOAD TRAINED MODEL
# ==============================

if (
    os.path.exists(MODEL_PATH)
    and
    os.path.exists(LABEL_PATH)
):

    recognizer.read(MODEL_PATH)

    with open(LABEL_PATH, "r") as f:

        label_map = json.load(f)

    # Convert keys back to int
    label_map = {
        int(k): v
        for k, v in label_map.items()
    }

    recognizer_loaded = True

    print("✅ Face recognizer loaded")

else:

    label_map = {}

    print("⚠️ No trained face model found")

# ==============================
# GREET MEMORY
# ==============================

greeted_faces = set()

# ==============================
# RECOGNIZE FACE
# ==============================

def recognize_face(frame):

    if not recognizer_loaded:
        return None

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(80, 80)
    )

    for (x, y, w, h) in faces:

        face_roi = gray[
            y:y+h,
            x:x+w
        ]

        # Resize to match training
        face_roi = cv2.resize(
            face_roi,
            (200, 200)
        )

        try:

            label, confidence = (
                recognizer.predict(
                    face_roi
                )
            )

            # Lower confidence = better
            if confidence < 70:

                name = label_map.get(
                    label,
                    "Unknown"
                )

                return {
                    "name": name,
                    "confidence": confidence,
                    "box": (x, y, w, h)
                }

        except Exception as e:

            print(
                f"Recognition error: {e}"
            )

    return None

# ==============================
# CHECK IF PERSON EXISTS
# ==============================

def is_known_person(name):

    name = name.lower()

    for person in label_map.values():

        if person.lower() == name:
            return True

    return False
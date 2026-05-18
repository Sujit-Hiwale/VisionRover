import cv2
import os
import json
import numpy as np

# -----------------------------
# FACE DETECTOR
# -----------------------------
detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)

# -----------------------------
# CONFIG
# -----------------------------
FACE_DIR = "faces"

MIN_IMAGES = 10

FACE_SIZE = (200, 200)

BLUR_THRESHOLD = 100

# -----------------------------
# ASK PERSON NAME
# -----------------------------
person_name = input(
    "Enter person's name: "
).strip().lower()

if person_name == "":

    print("❌ Name cannot be empty")

    exit()

# -----------------------------
# CREATE FOLDER
# -----------------------------
person_path = os.path.join(
    FACE_DIR,
    person_name
)

os.makedirs(
    person_path,
    exist_ok=True
)

print(f"\n📁 Saving images to: {person_path}")

# -----------------------------
# CAMERA SETUP
# -----------------------------
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# -----------------------------
# IMAGE COUNTER
# -----------------------------
count = 0

print("\n===================================")
print("📸 CONTROLS")
print("SPACE = Capture Face")
print("ESC   = Finish")
print("===================================\n")

# -----------------------------
# CAPTURE LOOP
# -----------------------------
while True:

    ret, frame = cap.read()

    if not ret:

        print("❌ Camera Error")

        break

    display = frame.copy()

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    faces = detector.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(80, 80)
    )

    # -----------------------------
    # DRAW FACE BOXES
    # -----------------------------
    for (x, y, w, h) in faces:

        cv2.rectangle(
            display,
            (x, y),
            (x+w, y+h),
            (0, 255, 0),
            2
        )

    # -----------------------------
    # UI TEXT
    # -----------------------------
    cv2.putText(
        display,
        f"Captured: {count}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.putText(
        display,
        "SPACE = Capture | ESC = Finish",
        (10, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2
    )

    cv2.imshow(
        "Capture Faces",
        display
    )

    key = cv2.waitKey(1)

    # -----------------------------
    # SPACE KEY
    # -----------------------------
    if key == 32:

        if len(faces) == 0:

            print("❌ No face detected")

            continue

        # Use first detected face
        x, y, w, h = faces[0]

        # -----------------------------
        # FACE ROI
        # -----------------------------
        face_roi = gray[
            y:y+h,
            x:x+w
        ]

        # -----------------------------
        # RESIZE FACE
        # -----------------------------
        face_roi = cv2.resize(
            face_roi,
            FACE_SIZE
        )

        # -----------------------------
        # BLUR CHECK
        # -----------------------------
        blur_value = cv2.Laplacian(
            face_roi,
            cv2.CV_64F
        ).var()

        if blur_value < BLUR_THRESHOLD:

            print(
                f"❌ Blurry face "
                f"({blur_value:.2f})"
            )

            continue

        # -----------------------------
        # SAVE FACE
        # -----------------------------
        count += 1

        image_path = os.path.join(
            person_path,
            f"{count}.jpg"
        )

        cv2.imwrite(
            image_path,
            face_roi
        )

        print(f"✅ Saved {image_path}")

    # -----------------------------
    # ESC KEY
    # -----------------------------
    elif key == 27:

        break

# -----------------------------
# CLEANUP CAMERA
# -----------------------------
cap.release()

cv2.destroyAllWindows()

# -----------------------------
# CHECK IMAGE COUNT
# -----------------------------
if count < MIN_IMAGES:

    print("\n===================================")
    print("⚠️ WARNING")
    print(
        f"Only {count} images captured."
    )
    print(
        f"Recommended minimum: "
        f"{MIN_IMAGES}"
    )
    print("===================================\n")

# -----------------------------
# TRAIN MODEL
# -----------------------------
print("\n⚡ Training Model...")

recognizer = cv2.face.LBPHFaceRecognizer_create()

faces_data = []

labels = []

label_ids = {}

current_id = 0

# -----------------------------
# LOAD FACE DATA
# -----------------------------
for name in sorted(
    os.listdir(FACE_DIR)
):

    path = os.path.join(
        FACE_DIR,
        name
    )

    if not os.path.isdir(path):
        continue

    label_ids[current_id] = name

    print(f"\n📂 Loading: {name}")

    image_count = 0

    for image_name in os.listdir(path):

        image_path = os.path.join(
            path,
            image_name
        )

        img = cv2.imread(
            image_path,
            cv2.IMREAD_GRAYSCALE
        )

        if img is None:
            continue

        # Ensure correct size
        img = cv2.resize(
            img,
            FACE_SIZE
        )

        faces_data.append(img)

        labels.append(current_id)

        image_count += 1

    print(
        f"✅ Loaded "
        f"{image_count} images"
    )

    current_id += 1

# -----------------------------
# CHECK DATA
# -----------------------------
if len(faces_data) == 0:

    print("❌ No training data found")

    exit()

# -----------------------------
# TRAIN RECOGNIZER
# -----------------------------
recognizer.train(
    faces_data,
    np.array(labels)
)

# -----------------------------
# SAVE MODEL
# -----------------------------
recognizer.save(
    "trainer.yml"
)

# -----------------------------
# SAVE LABELS
# -----------------------------
with open(
    "labels.json",
    "w"
) as f:

    json.dump(
        label_ids,
        f,
        indent=4
    )

# -----------------------------
# DONE
# -----------------------------
print("\n===================================")
print("✅ TRAINING COMPLETE")
print(f"📸 Images Captured: {count}")
print(f"🧠 Faces Trained: {len(label_ids)}")
print("💾 trainer.yml saved")
print("💾 labels.json saved")
print("===================================")
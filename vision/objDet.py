import os
import json

from ultralytics import YOLO

# =====================================
# LOAD YOLO
# =====================================

print("🧠 Loading YOLO model...")

model = YOLO("yolov8n.pt")

print("✅ YOLO loaded")

# =====================================
# CACHE FILE
# =====================================

CACHE_FILE = "object_cache.json"

# =====================================
# LOAD CACHE
# =====================================

if os.path.exists(CACHE_FILE):

    with open(CACHE_FILE, "r") as f:

        object_cache = json.load(f)

else:

    object_cache = {}

# =====================================
# SAVE CACHE
# =====================================

def save_cache():

    with open(CACHE_FILE, "w") as f:

        json.dump(
            object_cache,
            f,
            indent=4
        )

# =====================================
# GET CLASS ID
# =====================================

def get_class_id(object_name):

    object_name = object_name.lower()

    # ================================
    # CACHE HIT
    # ================================

    if object_name in object_cache:

        return object_cache[object_name]

    # ================================
    # SEARCH YOLO NAMES
    # ================================

    for class_id, name in model.names.items():

        if name.lower() == object_name:

            object_cache[object_name] = class_id

            save_cache()

            print(
                f"💾 Cached: "
                f"{object_name} -> {class_id}"
            )

            return class_id

    print(
        f"❌ Object not found "
        f"in YOLO classes: {object_name}"
    )

    return None

# =====================================
# FIND OBJECT
# =====================================

def find_object(
    frame,
    target_name,
    confidence=0.5
):

    # ================================
    # GET CLASS ID
    # ================================

    class_id = get_class_id(
        target_name
    )

    if class_id is None:

        return None

    # ================================
    # RUN TARGETED DETECTION
    # ================================

    results = model(

        frame,

        classes=[class_id],

        conf=confidence,

        verbose=False
    )

    # ================================
    # PROCESS RESULTS
    # ================================

    for result in results:

        for box in result.boxes:

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            return {

                "label": target_name,

                "confidence": round(
                    float(box.conf[0]),
                    2
                ),

                "box": (
                    x1,
                    y1,
                    x2,
                    y2
                ),

                "center": (
                    center_x,
                    center_y
                )
            }

    return None

# =====================================
# DRAW RESULT
# =====================================

def draw_object(
    frame,
    detection
):

    if detection is None:
        return frame

    x1, y1, x2, y2 = detection["box"]

    label = detection["label"]

    confidence = detection["confidence"]

    center_x, center_y = detection["center"]

    # Bounding box
    import cv2

    cv2.rectangle(
        frame,
        (x1, y1),
        (x2, y2),
        (0, 255, 0),
        2
    )

    # Label
    cv2.putText(
        frame,
        f"{label} {confidence}",
        (x1, y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )

    # Center point
    cv2.circle(
        frame,
        (center_x, center_y),
        5,
        (0, 0, 255),
        -1
    )

    return frame
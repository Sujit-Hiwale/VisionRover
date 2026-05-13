# face.py

import cv2

# ---------------------------------
# FACE DETECTOR
# ---------------------------------
face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)
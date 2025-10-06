import cv2
import os
import numpy as np

img_path = "dataset/kunj/20250811_065936.jpg"
print("Image:", img_path)
img = cv2.imread(img_path)
print("Loaded:", img is not None)
if img is None:
    raise SystemExit("Image not found")
print("Shape:", img.shape)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
print("cascade:", cascade_path, "exists:", os.path.exists(cascade_path))
detector = cv2.CascadeClassifier(cascade_path)
params = [
    (1.1, 5, (60, 60)),
    (1.05, 5, (30, 30)),
    (1.01, 3, (20, 20)),
    (1.3, 3, (50, 50)),
]
for scale, neigh, minsize in params:
    faces = detector.detectMultiScale(
        gray, scaleFactor=scale, minNeighbors=neigh, minSize=minsize
    )
    print(f"scale={scale}, neigh={neigh}, minsize={minsize} -> faces:", len(faces))
    for x, y, w, h in faces:
        print(" ", x, y, w, h)

# Try resizing smaller image
h, w = gray.shape
for factor in [1.0, 0.75, 0.5, 0.25]:
    gs = cv2.resize(gray, (int(w * factor), int(h * factor)))
    faces = detector.detectMultiScale(
        gs, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )
    print(f"resize factor={factor} -> shape={gs.shape} faces={len(faces)}")

# Save a debug annotated image if any faces found
faces = detector.detectMultiScale(
    gray, scaleFactor=1.05, minNeighbors=4, minSize=(30, 30)
)
if len(faces) > 0:
    out = img.copy()
    for x, y, w, h in faces:
        cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imwrite("debug_detect.jpg", out)
    print("Wrote debug_detect.jpg")
else:
    print("No faces detected with moderate params; no debug image written")

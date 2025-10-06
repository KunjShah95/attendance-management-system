import cv2, os, pickle
import numpy as np

img_path = "dataset/kunj/20250811_065936.jpg"
img = cv2.imread(img_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
detector = cv2.CascadeClassifier(cascade_path)
faces = detector.detectMultiScale(
    gray, scaleFactor=1.05, minNeighbors=5, minSize=(30, 30)
)
print("faces found:", len(faces))
if len(faces) == 0:
    faces = detector.detectMultiScale(
        gray, scaleFactor=1.01, minNeighbors=3, minSize=(20, 20)
    )
    print("fallback faces:", len(faces))
if len(faces) == 0:
    raise SystemExit("No faces")
# pick largest face
faces_sorted = sorted(faces, key=lambda r: r[2] * r[3], reverse=True)
x, y, w, h = faces_sorted[0]
face_gray = gray[y : y + h, x : x + w]
# load recognizer
model_dir = "model"
trainer_path = os.path.join(model_dir, "trainer.yml")
labels_path = os.path.join(model_dir, "labels.pickle")
with open(labels_path, "rb") as f:
    labels = pickle.load(f)
print("labels keys sample:", list(labels.items())[:5])
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(trainer_path)
label_id, conf = recognizer.predict(face_gray)
print("predict -> label_id:", label_id, "conf:", conf)
name = labels.get(label_id, "unknown")
print("mapped name:", name)
cv2.imwrite("debug_face_crop.jpg", face_gray)
print("wrote debug_face_crop.jpg")

import os
import cv2
import argparse
from utils import load_labels, mark_attendance_db
import pickle
from pathlib import Path
import datetime

# constants
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"


def load_recognizer(model_dir="model"):
    trainer_path = os.path.join(model_dir, "trainer.yml")
    if not os.path.exists(trainer_path):
        raise RuntimeError(f"No trainer found at {trainer_path}. Run train.py first.")
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
    except AttributeError:
        raise RuntimeError("cv2.face not found. Install opencv-contrib-python.")
    recognizer.read(trainer_path)
    return recognizer


def run_live(
    model_dir="model", db_path="attendance.db", cam_index=0, confidence_threshold=70
):
    labels_path = os.path.join(model_dir, "labels.pickle")
    if not os.path.exists(labels_path):
        raise RuntimeError(
            f"No labels file found at {labels_path}. Run train.py first."
        )
    with open(labels_path, "rb") as f:
        labels_map = pickle.load(f)  # id -> name

    recognizer = load_recognizer(model_dir)
    detector = cv2.CascadeClassifier(CASCADE_PATH)
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera {cam_index}")

    print("[*] Starting camera. Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[!] Failed to read frame from camera.")
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
        )
        for x, y, w, h in faces:
            face_crop_gray = gray[y : y + h, x : x + w]
            try:
                label_id, confidence = recognizer.predict(face_crop_gray)
            except Exception:
                # In case of error from model, skip this face
                continue
            if label_id is not None and confidence < confidence_threshold:
                name = labels_map.get(label_id, f"ID_{label_id}")
                inserted = mark_attendance_db(label_id, name, db_path)
                text = f"{name} ({round(confidence, 1)})"
                color = (0, 255, 0)
                if inserted:
                    print(
                        f"[+] Attendance marked for {name} at {datetime.datetime.now().strftime('%H:%M:%S')}"
                    )
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(
                    frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2
                )
        cv2.imshow("Attendance", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model-dir",
        default="model",
        help="Directory where trainer.yml and labels.pickle are stored",
    )
    parser.add_argument("--db", default="attendance.db", help="SQLite DB path")
    parser.add_argument("--cam", default=0, type=int, help="Camera index")
    parser.add_argument(
        "--threshold",
        default=70,
        type=float,
        help="Confidence threshold (lower = stricter)",
    )
    args = parser.parse_args()
    run_live(args.model_dir, args.db, args.cam, args.threshold)

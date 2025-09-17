import requests
import os
from typing import List, Dict

API_BASE = os.getenv("API_BASE", "http://localhost:5000/api")


def get_students() -> List[Dict]:
    try:
        r = requests.get(f"{API_BASE}/students", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        # Fallback to local CSV if API not available
        from utils import load_students

        return load_students()


def get_attendance(date_str: str = None):
    try:
        params = {}
        if date_str:
            params["date"] = date_str
        r = requests.get(f"{API_BASE}/attendance", params=params, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception:
        from utils import get_attendance as local_get_attendance

        return local_get_attendance(date_str=date_str)


def send_absent_emails(smtp: Dict = None, date_str: str = None):
    payload = {}
    if smtp:
        payload["smtp"] = smtp
    if date_str:
        payload["date"] = date_str
    try:
        r = requests.post(f"{API_BASE}/send_absent_emails", json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def export_csv(date_str: str = None):
    try:
        params = {}
        if date_str:
            params["date"] = date_str
        r = requests.get(f"{API_BASE}/export_csv", params=params, timeout=10)
        r.raise_for_status()
        return r.content
    except Exception as e:
        return None


def recognize_and_mark(
    image_bytes, model_dir="model", db_path="attendance.db", threshold=70
):
    """Try to recognize faces in the uploaded image_bytes. If a face matches, mark attendance and return results list.
    Returns list of dicts: [{id, name, confidence, marked(bool)}]
    """
    try:
        import cv2
        import numpy as np
        import pickle
        from utils import load_labels, mark_attendance_db, ensure_dir
    except Exception as e:
        return {"error": f"Missing imaging dependencies: {e}"}

    # load labels and recognizer
    labels_path = os.path.join(model_dir, "labels.pickle")
    trainer_path = os.path.join(model_dir, "trainer.yml")
    if not os.path.exists(trainer_path) or not os.path.exists(labels_path):
        return {"error": "Trained model or labels not found. Run train.py first."}

    with open(labels_path, "rb") as f:
        labels = pickle.load(f)

    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(trainer_path)
    except Exception as e:
        return {"error": f"Failed to load recognizer: {e}"}

    # load image
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return {"error": "Could not decode uploaded image"}

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = detector.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
    )

    results = []
    if len(faces) == 0:
        return {"error": "No faces detected in image"}

    for x, y, w, h in faces:
        face_gray = gray[y : y + h, x : x + w]
        try:
            label_id, conf = recognizer.predict(face_gray)
        except Exception:
            label_id, conf = None, 999

        if label_id is not None and conf < threshold:
            name = labels.get(label_id, f"ID_{label_id}")
            marked = mark_attendance_db(label_id, name, db_path)
            results.append(
                {
                    "id": label_id,
                    "name": name,
                    "confidence": float(conf),
                    "marked": marked,
                }
            )
        else:
            results.append(
                {
                    "id": None,
                    "name": "Unknown",
                    "confidence": float(conf),
                    "marked": False,
                }
            )

    return results

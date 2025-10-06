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
    image_bytes,
    model_dir="model",
    db_path="attendance.db",
    threshold=70,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(60, 60),
):
    """Try to recognize faces in the uploaded image_bytes. If a face matches, mark attendance and return results list.
    Returns list of dicts: [{id, name, confidence, marked(bool)}]
    """
    try:
        import cv2
        import numpy as np
        import pickle
        from utils import load_labels, mark_attendance_db, ensure_dir, load_students
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
    # Dynamically compute a reasonable minSize based on image height to handle small camera_input frames
    try:
        ih, iw = gray.shape[:2]
        # target minimum face height ~8% of image height, bounded
        dyn_min = max(20, int(ih * 0.08))
        # if caller passed a small minSize, override with dynamic value
        if isinstance(minSize, tuple) and (
            minSize[0] < dyn_min or minSize[1] < dyn_min
        ):
            minSize = (dyn_min, dyn_min)
    except Exception:
        pass
    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    # Primary detection pass using provided parameters
    faces = detector.detectMultiScale(
        gray, scaleFactor=scaleFactor, minNeighbors=minNeighbors, minSize=minSize
    )

    # If no faces found, try a few fallback parameter sets (more permissive)
    if len(faces) == 0:
        fallback_params = [
            (1.05, 5, (30, 30)),
            (1.01, 3, (20, 20)),
            (1.3, 3, (50, 50)),
        ]
        for sf, mn, ms in fallback_params:
            faces = detector.detectMultiScale(
                gray, scaleFactor=sf, minNeighbors=mn, minSize=ms
            )
            if len(faces) > 0:
                # record chosen params for debug
                chosen_params = (sf, mn, ms)
                break
        else:
            chosen_params = None
    else:
        chosen_params = (scaleFactor, minNeighbors, minSize)

    results = []
    if len(faces) == 0:
        # No faces detected; return empty list (not an error) so callers can treat as 'no recognized faces'
        return []

    for x, y, w, h in faces:
        face_gray = gray[y : y + h, x : x + w]
        # Normalize face size for recognizer (helps LBPH matching stability)
        try:
            face_gray = cv2.resize(face_gray, (200, 200))
        except Exception:
            pass
        try:
            label_id, conf = recognizer.predict(face_gray)
        except Exception:
            label_id, conf = None, 999

        if label_id is not None and conf < threshold:
            # label_name comes from the labels.pickle mapping created during training
            label_name = labels.get(label_id, f"ID_{label_id}")

            # Attempt to find the corresponding student id from students.csv (or API via load_students)
            # Matching is tolerant: exact match OR substring match (handles 'kunj' vs 'kunjshah', trailing spaces, case differences)
            student_id = None
            student_name = None
            try:
                students_list = load_students()
            except Exception:
                students_list = []

            lname = label_name.strip().lower()
            for s in students_list:
                sname = str(s.get("name", "")).strip().lower()
                if not sname:
                    continue
                if lname == sname or lname in sname or sname in lname:
                    student_id = s.get("id")
                    student_name = s.get("name").strip()
                    break

            # If we couldn't find a matching student, fall back to using the recognizer label id
            if student_id is None:
                student_id = label_id
                student_name = label_name
                debug_note = f"Recognized label_id={label_id} ('{label_name}'), no CSV match; using label_id as id"
            else:
                debug_note = f"Recognized label_id={label_id} ('{label_name}') -> matched CSV id={student_id} name='{student_name}'"

            marked = mark_attendance_db(student_id, student_name, db_path)
            results.append(
                {
                    "id": student_id,
                    "name": student_name,
                    "confidence": float(conf),
                    "marked": marked,
                    "debug": f"{debug_note}; conf={conf:.1f} < {threshold}",
                }
            )
        # Skip unrecognized faces - don't add them to results

    return results

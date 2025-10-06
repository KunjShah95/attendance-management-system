import sys
import os
import time

print("=== Diagnostic script for attendance system ===")
print("Python executable:", sys.executable)
print("sys.path[0:5]:", sys.path[:5])

# OpenCV checks
try:
    import cv2

    print("OpenCV version:", cv2.__version__)
    print("cv2.face available:", hasattr(cv2, "face"))
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    print("Cascade path:", cascade_path)
    print("Cascade exists:", os.path.exists(cascade_path))
except Exception as e:
    print("OpenCV import error:", repr(e))
    cv2 = None

# Model files
try:
    base = os.path.dirname(os.path.abspath(__file__))
    model_dir = os.path.join(base, "model")
    print("Model dir:", model_dir)
    print("trainer.yml:", os.path.exists(os.path.join(model_dir, "trainer.yml")))
    print("labels.pickle:", os.path.exists(os.path.join(model_dir, "labels.pickle")))
except Exception as e:
    print("Model check error:", repr(e))

# Try VideoCapture if cv2 is present
if "cv2" in globals() and cv2 is not None:
    try:
        print("Attempting VideoCapture(0)...")
        cap = cv2.VideoCapture(0)
        time.sleep(0.5)
        if not cap or not cap.isOpened():
            print("VideoCapture(0) not available or cannot be opened")
        else:
            ret, frame = cap.read()
            print("VideoCapture read ret:", ret, "frame is None?", frame is None)
            cap.release()
    except Exception as e:
        print("VideoCapture error:", repr(e))

print("=== Diagnostics complete ===")

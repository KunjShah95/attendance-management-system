import os
from pprint import pprint

PROJECT_ROOT = os.path.dirname(__file__)
known_dir = os.path.join(PROJECT_ROOT, "dataset", "keshav", "kunj")
# choose an existing dataset folder
possible_students = [d for d in os.listdir(os.path.join(PROJECT_ROOT, "dataset"))]
if not possible_students:
    print("no student folders in dataset")
    raise SystemExit(1)
known_dir = os.path.join(PROJECT_ROOT, "dataset", possible_students[0])
files = [
    f
    for f in os.listdir(known_dir)
    if f.lower().endswith(".jpg") or f.lower().endswith(".png")
]
if not files:
    print("no files")
    raise SystemExit(1)
path = os.path.join(known_dir, files[0])
print("Using", path)
with open(path, "rb") as f:
    b = f.read()
from streamlit_utils import recognize_and_mark
from utils import get_attendance

res = recognize_and_mark(
    b,
    model_dir=os.path.join(PROJECT_ROOT, "model"),
    db_path=os.path.join(PROJECT_ROOT, "attendance.db"),
    threshold=1000,
)
# set a very large threshold to force any prediction to be considered match for testing
print("Result:")
pprint(res)
print("Attendance:")
pprint(get_attendance(db_path=os.path.join(PROJECT_ROOT, "attendance.db")))

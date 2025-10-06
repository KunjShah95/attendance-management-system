import csv
import pickle
import os
import sqlite3
import datetime

# Load students
students = []
with open("students.csv", newline="") as f:
    r = csv.DictReader(f)
    for row in r:
        students.append(
            {
                "id": int(row["id"]),
                "name": row["name"].strip(),
                "email": row["email"].strip(),
            }
        )

print("Students:", students)

# Load labels.pickle
labels_path = os.path.join("model", "labels.pickle")
if os.path.exists(labels_path):
    with open(labels_path, "rb") as f:
        labels = pickle.load(f)
else:
    labels = {}
print("Labels:", labels)

# Attendance rows for today
db_path = "attendance.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()
today = datetime.date.today().isoformat()
cur.execute("SELECT id,name,date,time FROM attendance WHERE date=?", (today,))
rows = cur.fetchall()
conn.close()
print("Attendance rows for", today, ":", rows)

attended_ids = {r[0] for r in rows}
absent = [s for s in students if s["id"] not in attended_ids]
print("Absent students (computed):", absent)

# Show mapping from label names to student ids via fuzzy match
label_to_student = {}
for lid, lname in labels.items():
    lname_norm = str(lname).strip().lower()
    match = None
    for s in students:
        sname = s["name"].strip().lower()
        if lname_norm == sname or lname_norm in sname or sname in lname_norm:
            match = s
            break
    label_to_student[lid] = match

print("Label -> matched student (if any):")
for k, v in label_to_student.items():
    print(k, "->", v)

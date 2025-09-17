import pickle
import os
import csv
import sqlite3
from datetime import date
import datetime
from typing import Dict
import smtplib
from email.message import EmailMessage


# Utility: Ensure a directory exists
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


# Utility: Save labels map as pickle
def save_labels(labels_map, path):
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "wb") as f:
        pickle.dump(labels_map, f)


def load_labels(path="model/labels.pickle"):
    """Load labels mapping (id -> name) from pickle file."""
    if not os.path.exists(path):
        return {}
    with open(path, "rb") as f:
        return pickle.load(f)


def ensure_db(db_path):
    # Dummy implementation, replace with actual DB initialization if needed
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS attendance
					 (id INTEGER, name TEXT, date TEXT, time TEXT)""")
        conn.commit()
        conn.close()


def mark_attendance_db(id_val: int, name: str, db_path: str = "attendance.db") -> bool:
    """Insert attendance for today if not already present. Returns True if inserted, False if already present."""
    ensure_db(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    today = date.today().isoformat()
    cur.execute(
        "SELECT 1 FROM attendance WHERE id = ? AND date = ? LIMIT 1", (id_val, today)
    )
    exists = cur.fetchone()
    if exists:
        conn.close()
        return False
    now = datetime.datetime.now().strftime("%H:%M:%S")
    cur.execute(
        "INSERT INTO attendance (id, name, date, time) VALUES (?, ?, ?, ?)",
        (id_val, name, today, now),
    )
    conn.commit()
    conn.close()
    return True


def get_attendance(db_path="attendance.db", date_str: str = None):
    ensure_db(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    if date_str is None:
        date_str = date.today().isoformat()
    cur.execute(
        "SELECT id, name, date, time FROM attendance WHERE date = ?", (date_str,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def load_students(csv_path="students.csv"):
    """Return list of dicts: [{id:int,name:str,email:str}, ...]"""
    if not os.path.exists(csv_path):
        return []
    out = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                out.append(
                    {
                        "id": int(r["id"]),
                        "name": r.get("name", "").strip(),
                        "email": r.get("email", "").strip(),
                    }
                )
            except Exception:
                continue
    return out


def send_email(smtp_config: Dict, to_email: str, subject: str, body: str):
    """Send a simple plaintext email using smtp_config dict with keys:
    host, port, user, pass, use_tls (bool)
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp_config.get("user")
    msg["To"] = to_email
    msg.set_content(body)

    host = smtp_config.get("host")
    port = int(smtp_config.get("port", 587))
    user = smtp_config.get("user")
    password = smtp_config.get("pass")
    use_tls = smtp_config.get("use_tls", True)

    if use_tls:
        server = smtplib.SMTP(host, port)
        server.ehlo()
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
        server.quit()
    else:
        server = smtplib.SMTP_SSL(host, port)
        server.login(user, password)
        server.send_message(msg)
        server.quit()


def send_absent_emails(
    smtp_config: Dict,
    csv_path: str = "students.csv",
    db_path: str = "attendance.db",
    date_str: str = None,
):
    """Sends email to students who are in students.csv but not in attendance table for date_str (defaults to today).
    Returns list of sent emails.
    """
    if date_str is None:
        date_str = date.today().isoformat()
    students = load_students(csv_path)
    attendance_rows = get_attendance(db_path, date_str)
    attended_ids = {r[0] for r in attendance_rows}
    sent = []
    for s in students:
        if s["id"] not in attended_ids and s["email"]:
            subject = f"Absent Notice for {date_str}"
            body = f"Hello {s['name']},\n\nYou were marked absent on {date_str}. If this is a mistake, please contact the administration.\n\nRegards,\nAttendance System"
            try:
                send_email(smtp_config, s["email"], subject, body)
                sent.append(s["email"])
            except Exception as e:
                # For a production system we would log details
                print(f"[!] Failed to send email to {s['email']}: {e}")
    return sent

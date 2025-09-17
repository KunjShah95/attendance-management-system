from flask import Flask, jsonify, request
from flask_cors import CORS
from utils import get_attendance, load_students, send_absent_emails, ensure_db
import os
import json
from dotenv import load_dotenv


load_dotenv()


app = Flask(__name__)
CORS(app)

# Serve frontend static files when built to frontend/dist
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "frontend", "dist")


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    # If the file exists in the dist folder, serve it; otherwise serve index.html
    if (
        os.path.exists(FRONTEND_DIST)
        and path != ""
        and os.path.exists(os.path.join(FRONTEND_DIST, path))
    ):
        return app.send_static_file(os.path.join("frontend", "dist", path))
    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_path):
        return open(index_path).read()
    return jsonify({"status": "API running"}), 200


DB_PATH = os.getenv("DB_PATH", "attendance.db")
STUDENTS_CSV = os.getenv("STUDENTS_CSV", "students.csv")


# Read SMTP config from request body or environment
SMTP_CONFIG = {
    "host": os.getenv("SMTP_HOST"),
    "port": os.getenv("SMTP_PORT"),
    "user": os.getenv("SMTP_USER"),
    "pass": os.getenv("SMTP_PASS"),
    "use_tls": os.getenv("SMTP_USE_TLS", "True").lower() in ("1", "true", "yes"),
}


@app.route("/api/attendance", methods=["GET"])
def api_get_attendance():
    date_str = request.args.get("date")
    rows = get_attendance(DB_PATH, date_str)
    result = [{"id": r[0], "name": r[1], "date": r[2], "time": r[3]} for r in rows]
    return jsonify(result)


@app.route("/api/students", methods=["GET"])
def api_get_students():
    students = load_students(STUDENTS_CSV)
    return jsonify(students)


@app.route("/api/send_absent_emails", methods=["POST"])
def api_send_absent_emails():
    body = request.json or {}
    smtp = body.get("smtp", SMTP_CONFIG)
    date_str = body.get("date")
    sent = send_absent_emails(smtp, STUDENTS_CSV, DB_PATH, date_str)
    return jsonify({"sent": sent})


@app.route("/api/export_csv", methods=["GET"])
def api_export_csv():
    import io
    import csv
    import sqlite3
    from flask import send_file

    date_str = request.args.get("date")
    fmt = request.args.get("format", "csv")
    ensure_db(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if date_str:
        cur.execute(
            "SELECT id, name, date, time FROM attendance WHERE date = ?", (date_str,)
        )
    else:
        cur.execute("SELECT id, name, date, time FROM attendance")
    rows = cur.fetchall()
    conn.close()

    if fmt == "excel" or fmt == "xlsx":
        try:
            import pandas as pd
        except Exception:
            return jsonify({"error": "pandas required for excel export"}), 500
        df = pd.DataFrame(rows, columns=["id", "name", "date", "time"])
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="attendance")
        output.seek(0)
        return send_file(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=f"attendance_{date_str or 'all'}.xlsx",
        )
    else:
        # CSV
        output = io.StringIO()
        w = csv.writer(output)
        w.writerow(["id", "name", "date", "time"])
        for r in rows:
            w.writerow(r)
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode("utf-8")),
            mimetype="text/csv",
            as_attachment=True,
            download_name=f"attendance_{date_str or 'all'}.csv",
        )

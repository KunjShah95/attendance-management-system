import streamlit as st
import pandas as pd
from datetime import date
from streamlit_utils import get_students, get_attendance, send_absent_emails, export_csv
import os
import time
import json

st.set_page_config(page_title=os.getenv("VITE_APP_TITLE", "Attendance Management"))
st.title("Attendance Management — Admin")

# SMTP config file path
SMTP_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "smtp_config.json"
)


def load_saved_smtp():
    try:
        if os.path.exists(SMTP_CONFIG_PATH):
            with open(SMTP_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        return None
    return None


def save_smtp(cfg: dict):
    try:
        with open(SMTP_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f)
        return True
    except Exception:
        return False


st.sidebar.header("Actions")
page = st.sidebar.selectbox(
    "Page", ["Dashboard", "Students", "Attendance", "Reports", "Settings"]
)

if page == "Dashboard":
    st.header("Dashboard")
    # Show which DB file we're using (helpful for debugging path issues)
    db_path_display = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "attendance.db"
    )
    st.caption(f"DB: `{db_path_display}`")
    today = st.date_input("Date", value=date.today())
    rows = get_attendance(today.isoformat())
    if not rows:
        st.info("No attendance recorded for this date yet.")
    else:
        df = pd.DataFrame(rows)
        df.columns = ["id", "name", "date", "time"]
        st.dataframe(df)

    if st.button("Export CSV for date"):
        content = export_csv(today.isoformat())
        if content:
            st.download_button(
                "Download CSV",
                data=content,
                file_name=f"attendance_{today.isoformat()}.csv",
            )
        else:
            st.error("Export not implemented or failed.")

elif page == "Students":
    st.header("Students")
    students = get_students()
    if not students:
        st.info("No students found.")
    else:
        df = pd.DataFrame(students)
        st.dataframe(df)

elif page == "Settings":
    st.header("Settings")
    st.subheader("SMTP Configuration")
    saved = load_saved_smtp() or {}
    s_host = st.text_input(
        "SMTP Host", value=saved.get("host", os.getenv("SMTP_HOST", ""))
    )
    s_port = st.text_input(
        "SMTP Port", value=saved.get("port", os.getenv("SMTP_PORT", "587"))
    )
    s_user = st.text_input(
        "SMTP User", value=saved.get("user", os.getenv("SMTP_USER", ""))
    )
    s_pass = st.text_input(
        "SMTP Password",
        type="password",
        value=saved.get("pass", os.getenv("SMTP_PASS", "")),
    )
    s_tls = st.checkbox("Use TLS", value=saved.get("use_tls", True))
    if st.button("Save SMTP Settings"):
        cfg = {
            "host": s_host,
            "port": s_port,
            "user": s_user,
            "pass": s_pass,
            "use_tls": s_tls,
        }
        ok = save_smtp(cfg)
        if ok:
            st.success("SMTP settings saved")
        else:
            st.error("Failed to save SMTP settings")

elif page == "Attendance":
    st.header("Attendance")
    date_sel = st.date_input("Date", value=date.today())
    rows = get_attendance(date_sel.isoformat())
    df = (
        pd.DataFrame(rows, columns=["id", "name", "date", "time"])
        if rows
        else pd.DataFrame()
    )
    st.dataframe(df)

    # --- Absent students UI ---
    st.markdown("---")
    st.subheader("Absent Students & Email Notifications")
    # load the master students list (API fallback to CSV)
    students = get_students()
    # build a map of present ids
    present_ids = {r[0] for r in rows} if rows else set()
    absent = [s for s in students if s.get("id") not in present_ids]

    if not students:
        st.info("No student roster available (check `students.csv` or API).")
    else:
        st.write(f"{len(absent)} student(s) absent on {date_sel.isoformat()}")
        # allow selecting multiple absentees to email
        absent_options = [
            f"{s['id']} - {s['name']} <{s.get('email', '')}>" for s in absent
        ]
        selected = st.multiselect(
            "Select absent students to notify", options=absent_options
        )

        # map label back to student dict
        sel_students = [
            absent[i] for i, opt in enumerate(absent_options) if opt in selected
        ]

        # Provide per-student send buttons and a bulk send
        cols = st.columns(3)
        if cols[0].button("Send to selected"):
            if not sel_students:
                st.warning("No students selected")
            else:
                smtp = load_saved_smtp() or {
                    "host": os.getenv("SMTP_HOST", ""),
                    "port": os.getenv("SMTP_PORT", "587"),
                    "user": os.getenv("SMTP_USER", ""),
                    "pass": os.getenv("SMTP_PASS", ""),
                    "use_tls": True,
                }
                sent = []
                failed = []
                from utils import send_email

                for s in sel_students:
                    if not s.get("email"):
                        failed.append((s, "no email"))
                        continue
                    subject = f"Absent Notice for {date_sel.isoformat()}"
                    body = f"Hello {s['name']},\n\nYou were marked absent on {date_sel.isoformat()}. If this is a mistake, please contact the administration.\n\nRegards,\nAttendance System"
                    try:
                        send_email(smtp, s["email"], subject, body)
                        sent.append(s["email"])
                    except Exception as e:
                        failed.append((s, str(e)))

                if sent:
                    st.success(f"Sent emails to: {', '.join(sent)}")
                if failed:
                    st.error(
                        f"Failed to send to: {', '.join([str(f[0].get('id')) for f in failed])}"
                    )

        # show a compact list with individual send buttons
        for s in absent:
            line = f"{s['id']} — {s['name']} — {s.get('email', '(no email)')}"
            c1, c2 = st.columns([6, 1])
            c1.write(line)
            btn_key = f"send_{s['id']}_{date_sel.isoformat()}"
            if c2.button("Send", key=btn_key):
                smtp = load_saved_smtp() or {
                    "host": os.getenv("SMTP_HOST", ""),
                    "port": os.getenv("SMTP_PORT", "587"),
                    "user": os.getenv("SMTP_USER", ""),
                    "pass": os.getenv("SMTP_PASS", ""),
                    "use_tls": True,
                }
                from utils import send_email

                try:
                    subject = f"Absent Notice for {date_sel.isoformat()}"
                    body = f"Hello {s['name']},\n\nYou were marked absent on {date_sel.isoformat()}. If this is a mistake, please contact the administration.\n\nRegards,\nAttendance System"
                    send_email(smtp, s.get("email", ""), subject, body)
                    st.success(f"Email sent to {s['name']} ({s.get('email')})")
                except Exception as e:
                    st.error(f"Failed to send email to {s['name']}: {e}")

    st.markdown("---")
    st.subheader("🔍 Automatic Face Detection")

    # show DB path for debugging
    db_path_display = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "attendance.db"
    )
    st.caption(f"DB: `{db_path_display}`")

    # Continuous face detection mode
    run_detection = st.checkbox("Enable Automatic Face Detection", value=False)

    if run_detection:
        st.info(
            "📹 Camera is active. Face detection will run automatically when faces are detected."
        )

        # Camera input for continuous monitoring
        camera_input = st.camera_input("Live Camera Feed", key="live_camera")

        threshold = st.slider(
            "Confidence threshold (lower = stricter)",
            min_value=30,
            max_value=150,
            value=70,
            key="auto_threshold",
        )

        # Camera debug detection parameters
        st.markdown("**Camera debug controls (adjust if faces are not detected)**")
        scale = st.number_input(
            "scaleFactor",
            value=1.1,
            min_value=1.01,
            max_value=2.0,
            step=0.01,
            format="%.2f",
        )
        neighbors = st.number_input(
            "minNeighbors", value=5, min_value=1, max_value=10, step=1
        )
        min_size_px = st.number_input(
            "minSize (px)", value=60, min_value=10, max_value=500, step=1
        )

        auto_send_absent = st.checkbox(
            "Automatically send absent emails for unrecognized faces",
            value=False,
            key="auto_absent",
        )

        # Status display and results
        status_placeholder = st.empty()
        results_placeholder = st.empty()
        event_log = st.empty()

        # maintain a short in-memory log for this session
        if "event_messages" not in st.session_state:
            st.session_state["event_messages"] = []

        if camera_input is not None:
            with st.spinner("Processing camera feed..."):
                try:
                    from streamlit_utils import recognize_and_mark

                    img_bytes = camera_input.getvalue()
                    start_time = time.time()

                    # Show captured frame for debugging with face overlay
                    try:
                        import cv2
                        import numpy as np

                        arr = np.frombuffer(img_bytes, np.uint8)
                        vis = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                        vis_rgb = cv2.cvtColor(vis, cv2.COLOR_BGR2RGB)

                        # Detect faces for overlay
                        gray = cv2.cvtColor(vis, cv2.COLOR_BGR2GRAY)
                        detector = cv2.CascadeClassifier(
                            cv2.data.haarcascades
                            + "haarcascade_frontalface_default.xml"
                        )
                        faces = detector.detectMultiScale(
                            gray,
                            scaleFactor=scale,
                            minNeighbors=neighbors,
                            minSize=(min_size_px, min_size_px),
                        )
                        for x, y, w, h in faces:
                            cv2.rectangle(
                                vis_rgb, (x, y), (x + w, y + h), (255, 0, 0), 2
                            )

                        st.image(
                            vis_rgb,
                            caption=f"Camera frame (preview) - {len(faces)} face(s) detected",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.write(f"Preview error: {e}")

                    # Process the camera frame
                    res = recognize_and_mark(
                        img_bytes,
                        threshold=threshold,
                        scaleFactor=scale,
                        minNeighbors=neighbors,
                        minSize=(min_size_px, min_size_px),
                    )

                    processing_time = time.time() - start_time

                    if isinstance(res, dict) and res.get("error"):
                        status_placeholder.error(f"❌ Detection Error: {res['error']}")
                        st.session_state["event_messages"].insert(
                            0, f"[{time.strftime('%H:%M:%S')}] Error: {res['error']}"
                        )
                    else:
                        # Count results - all returned results are recognized faces
                        present_count = len(res)

                        # Update status
                        if present_count > 0:
                            status_placeholder.success(
                                f"✅ Detected and recognized {present_count} face(s) - Attendance marked!"
                            )
                        else:
                            status_placeholder.info(
                                "👀 No recognized faces detected in current frame"
                            )

                        # Display detailed results
                        with results_placeholder.container():
                            st.write(f"**Processing Time:** {processing_time:.2f}s")
                            st.write(f"**Recognized Faces:** {present_count}")

                            if res:
                                for result in res:
                                    if result.get("marked"):
                                        st.success(
                                            f"✅ **{result['name']}** (ID: {result['id']}) - **PRESENT** (Confidence: {result['confidence']:.1f}%)"
                                        )
                                        st.session_state["event_messages"].insert(
                                            0,
                                            f"[{time.strftime('%H:%M:%S')}] Marked present: {result['name']} (id={result['id']})",
                                        )
                                    # No else block - unrecognized faces are not returned

                            # Auto-send absent emails functionality removed - now only uses dataset images

                        # Refresh attendance table
                        rows = get_attendance(date_sel.isoformat())
                        df = (
                            pd.DataFrame(rows, columns=["id", "name", "date", "time"])
                            if rows
                            else pd.DataFrame()
                        )
                        st.dataframe(df)

                    # Render compact event log (most recent 10)
                    event_log.write(
                        "\n".join(st.session_state.get("event_messages", [])[:10])
                    )

                except Exception as e:
                    status_placeholder.error(f"❌ Processing Error: {str(e)}")

        # Instructions
        st.markdown("---")
        st.markdown(
            """
        **How it works:**
        1. Enable "Automatic Face Detection" above
        2. Allow camera access when prompted
        3. The system will automatically detect and recognize faces in real-time
        4. Recognized students are marked present immediately
        5. Unrecognized faces can trigger absent email notifications (optional)
        """
        )

    else:
        st.info("👆 Enable automatic face detection to start real-time recognition")

    st.markdown("---")
    st.subheader("Send Absent Emails")
    smtp_host = st.text_input("SMTP Host", value=os.getenv("SMTP_HOST", ""))
    smtp_port = st.text_input("SMTP Port", value=os.getenv("SMTP_PORT", "587"))
    smtp_user = st.text_input("SMTP User", value=os.getenv("SMTP_USER", ""))
    smtp_pass = st.text_input(
        "SMTP Pass", type="password", value=os.getenv("SMTP_PASS", "")
    )
    use_tls = st.checkbox("Use TLS", value=True)

    if st.button("Send Absent Emails"):
        smtp = {
            "host": smtp_host,
            "port": smtp_port,
            "user": smtp_user,
            "pass": smtp_pass,
            "use_tls": use_tls,
        }
        res = send_absent_emails(smtp, date_sel.isoformat())
        if res and isinstance(res, dict) and res.get("error"):
            st.error(f"Failed: {res.get('error')}")
        else:
            st.success("Absent email routine invoked (see server logs)")

    st.markdown("---")
    st.subheader("Export Attendance")
    if st.button("Export CSV"):
        buf = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV", data=buf, file_name=f"attendance_{date_sel.isoformat()}.csv"
        )
    if st.button("Export Excel"):
        import io

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="attendance")
        st.download_button(
            "Download Excel",
            data=output.getvalue(),
            file_name=f"attendance_{date_sel.isoformat()}.xlsx",
        )
        st.markdown("---")
        st.subheader("Export Attendance")
        if st.button("Export CSV"):
            buf = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                data=buf,
                file_name=f"attendance_{date_sel.isoformat()}.csv",
            )
        if st.button("Export Excel"):
            import io

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="attendance")
            st.download_button(
                "Download Excel",
                data=output.getvalue(),
                file_name=f"attendance_{date_sel.isoformat()}.xlsx",
            )

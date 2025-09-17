import streamlit as st
import pandas as pd
from datetime import date
from streamlit_utils import get_students, get_attendance, send_absent_emails, export_csv
import os

st.set_page_config(page_title=os.getenv("VITE_APP_TITLE", "Attendance Management"))

st.title("Attendance Management — Admin")

st.sidebar.header("Actions")
page = st.sidebar.selectbox(
    "Page", ["Dashboard", "Students", "Attendance", "Reports", "Settings"]
)

if page == "Dashboard":
    st.header("Dashboard")
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

    st.markdown("---")
    st.subheader("Recognize From Image")
    uploaded = st.file_uploader(
        "Upload an image (jpg/png)", type=["jpg", "jpeg", "png"]
    )
    threshold = st.slider(
        "Confidence threshold (lower = stricter)", min_value=30, max_value=150, value=70
    )
    if uploaded is not None:
        img_bytes = uploaded.read()
        with st.spinner("Recognizing..."):
            res = None
            try:
                from streamlit_utils import recognize_and_mark

                res = recognize_and_mark(img_bytes, threshold=threshold)
            except Exception as e:
                res = {"error": str(e)}

        if isinstance(res, dict) and res.get("error"):
            st.error(res["error"])
        else:
            st.success("Recognition results:")
            st.json(res)
            # Refresh attendance table
            rows = get_attendance(date_sel.isoformat())
            df = (
                pd.DataFrame(rows, columns=["id", "name", "date", "time"])
                if rows
                else pd.DataFrame()
            )
            st.dataframe(df)

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
        if res and "sent" in res:
            st.success(f"Sent emails to: {res['sent']}")
        else:
            st.error(f"Failed: {res}")

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

elif page == "Reports":
    st.header("Reports")
    st.write("Reports will be added here.")

elif page == "Settings":
    st.header("Settings")
    st.write("Settings will be added here.")

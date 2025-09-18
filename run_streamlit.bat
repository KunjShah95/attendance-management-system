@echo off
python -m streamlit run "%~dp0streamlit_app.py" --server.headless true --server.port 8501 > "%~dp0streamlit.log" 2>&1
pause

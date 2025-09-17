import sys

try:
    import streamlit_utils
    import streamlit_app

    print("Imports OK")
except Exception as e:
    print("Import error:", e)
    sys.exit(1)

import os
import tempfile
import shutil
from utils import load_students, mark_attendance_db, ensure_db


def test_load_students():
    students = load_students("students.csv")
    assert isinstance(students, list)
    assert any(s["id"] == 1 for s in students)


def test_mark_attendance_db_tmpdb():
    # Create a temporary directory and use a db path that does not yet exist so ensure_db will create it
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, "test_attendance.db")
    try:
        # Ensure DB created and marking works
        ensure_db(path)
        marked = mark_attendance_db(9999, "Test User", db_path=path)
        assert marked is True
        # Marking again should return False (already present)
        marked2 = mark_attendance_db(9999, "Test User", db_path=path)
        assert marked2 is False
    finally:
        # cleanup
        shutil.rmtree(tmpdir)

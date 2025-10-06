# Attendance Management System

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)

Rebuilt, polished, and developer-friendly documentation for the Attendance Management System. This README is written so contributors at any level (students, juniors, seniors, maintainers) can understand, run, and contribute to the project.

Table of Contents
- About
- Key Features
- Quick Start
- Requirements
- Installation
- Configuration
- Usage
  - CLI / Script usage
  - Library usage
- Architecture (high-level)
- Data model (summary)
- Tests
- Contributing
- Troubleshooting
- License
- Maintainers

About

A lightweight Attendance Management System implemented in Python. The project focuses on simple CSV-based imports, reliable SQLite persistence, and clear utilities for marking and querying attendance. The repository is intentionally small so it's easy to read, extend, and reuse in classrooms or small organizations.

Key Features
- Import student rosters from CSV
- Mark attendance to a local SQLite database
- Idempotent attendance marking (won't double-mark the same person for the same day)
- Small, well-tested utilities and clear boundaries so contributors can easily extend the system

Quick Start (seconds)
1. Clone the repo:
   ```bash
   git clone https://github.com/KunjShah95/attendance-management-system.git
   cd attendance-management-system
   ```
2. Create a virtual environment and install dependencies (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   .\.venv\Scripts\activate  # Windows (PowerShell)
   pip install -r requirements.txt
   ```
3. Initialize the database and run a short demo:
   ```bash
   python -c "from utils import ensure_db, load_students, mark_attendance_db; ensure_db('attendance.db'); print('DB ready')"
   ```

Requirements
- Python 3.8+
- SQLite (bundled with Python)
- pip

Installation
Detailed install steps:
- Recommended: use a virtual environment
- Install dependencies if requirements.txt exists: `pip install -r requirements.txt`

Configuration
- Database path: by default, utilities use `attendance.db` in the repository root. You can pass a different path to functions that accept `db_path`.
- Students CSV format: The loader expects a CSV with at least the following columns (header row): `id,name,other(optional)`

Usage

CLI / Script usage
- The repo is designed to be imported as a small library or executed via small scripts. Example script usage (example/script.py):

```python
from utils import ensure_db, load_students, mark_attendance_db

ensure_db('attendance.db')
students = load_students('students.csv')
for s in students[:5]:
    mark_attendance_db(s['id'], s.get('name','Unknown'), db_path='attendance.db')
```

Library usage (importing core utilities)

- load_students(csv_path) -> list[dict]
- ensure_db(db_path) -> creates DB and tables if missing
- mark_attendance_db(id, name, db_path) -> bool (True if new mark, False if already marked or error)

Example:

```python
from utils import load_students, ensure_db, mark_attendance_db

ensure_db('attendance.db')
students = load_students('students.csv')
print('Loaded', len(students), 'students')
mark_attendance_db(1, 'Alice Example', db_path='attendance.db')
```

Architecture (high-level)
See docs/ARCHITECTURE.puml (PlantUML) for a visual diagram and docs/ARCHITECTURE.md for an explanation. High-level components:
- Import layer (CSV loader)
- Core services (attendance service, student service)
- Persistence (SQLite)
- Tests and CI

Data model (summary)
A simple attendance schema is recommended:
- students (id INTEGER PRIMARY KEY, name TEXT, extra JSON/NULL)
- attendance (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, date DATE, marked_at DATETIME, UNIQUE(student_id, date))

Tests
Run the existing tests with pytest:

```bash
python -m pytest -q
```

An example test (already present) verifies loader behavior and idempotent attendance marking by creating a temporary DB and calling ensure_db and mark_attendance_db.

Contributing
We welcome all contributions. To contribute:
1. Fork the repository
2. Create a descriptive branch: `git checkout -b feat/your-feature` or `fix/issue-number`
3. Add tests for new behavior
4. Run tests locally: `python -m pytest`
5. Open a PR with a clear description of the problem and solution

Guidelines
- Keep changes small and focused
- Write tests for new features and bug fixes
- Follow PEP8
- Document new public functions in the README or a docs folder

Troubleshooting
- If CSV import fails: verify header names and that the file is UTF-8 encoded
- If DB operations fail: check file permissions and that the path is writable

License
This repository is licensed under the MIT License. See LICENSE for details.

Maintainers
- Kunj Shah (@KunjShah95)

Acknowledgements
This README was rebuilt to be clear, accessible, and useful for contributors of all experience levels.

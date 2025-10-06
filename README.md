# Attendance Management System

![MIT License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)

A rebuilt, well-documented Attendance Management System focused on clarity and contribution. This README is written to be approachable for beginners and useful for senior developers.

====

Table of Contents

- Overview
- Quick Start
- Features
- Architecture
- Installation
- Usage
- Project Structure
- Development & Contributing
- Testing
- Deployment
- Roadmap
- License
- Contact

====

Overview

This repository implements a small, extensible attendance management system using Python and SQLite. Core responsibilities:

- Import student lists from CSV
- Mark attendance and persist to SQLite
- Provide utilities and tests suitable for extension into a web UI or CLI

Goals for the rebuild

- Clear documentation for contributors at all levels (students → experts)
- Simple, well-tested core utilities
- Easy-to-follow architecture diagram and extension points

Features

- CSV import/export for student records
- SQLite-backed attendance store
- Simple Python utilities that can be used as the core for a CLI or web service
- Unit tests and examples

Architecture (high-level)

See docs/ARCHITECTURE.puml for a PlantUML source and docs/ARCHITECTURE.md for an explanation and how to render it.

Quick Start (3 steps)

1) Clone the repo

```bash
git clone https://github.com/KunjShah95/attendance-management-system.git
cd attendance-management-system
```

2) Create a virtual environment & install dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt || echo "No requirements.txt found. This project uses only standard library by default."
```

3) Initialize database and run example

```bash
python -c "from utils import ensure_db; ensure_db('attendance.db'); print('DB ensured')"
```

Usage (examples)

- Load students from CSV

```python
from utils import load_students
students = load_students('students.csv')
print(len(students), 'students loaded')
```

- Ensure DB and mark attendance

```python
from utils import ensure_db, mark_attendance_db
ensure_db('attendance.db')
marked = mark_attendance_db(1234, 'Jane Doe', db_path='attendance.db')
if marked:
    print('Marked present')
else:
    print('Already marked or error')
```

Project Structure

- utils.py             # Core helper functions (CSV load, DB helpers, marking)
- tests/               # Unit tests
- docs/                # Architecture and developer docs
- students.csv.sample  # Example CSV file (if present)

Development & Contributing

All contributors are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch: git checkout -b feat/meaningful-name
3. Add tests for new behavior
4. Commit and open a Pull Request

Coding guidelines

- Follow PEP8
- Keep functions small and single-responsibility
- Write tests for new features

Testing

Run tests with pytest (if pytest is present):

```bash
python -m pytest -q
```

There are example tests in tests/test_utils.py that demonstrate expected behavior of load_students, ensure_db, and mark_attendance_db.

Deployment & Extending

This project is intentionally minimal to serve as a core library. Typical extension points:

- Add a lightweight Flask/FastAPI wrapper to expose attendance APIs
- Add a CLI using argparse or Click
- Add user authentication and web UI

Roadmap

- Improve CSV import validation
- Add configurable storage adapters (Postgres, MySQL)
- Add role-based access control and authentication

License

MIT License — see LICENSE file

Contact

Repository: https://github.com/KunjShah95/attendance-management-system
Owner: @KunjShah95

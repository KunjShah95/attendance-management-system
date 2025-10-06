# Architecture - Attendance Management System

This document explains the simple, extensible architecture used by this project. The visual diagram is available as `docs/ARCHITECTURE.puml` (PlantUML source). Use a PlantUML renderer to generate PNG/SVG diagrams from the `.puml` file.

Overview
The system is intentionally small and modular so students and new contributors can understand and extend it. It is divided into three layers:

1. Interface
   - CLI / scripts are the primary way to interact with the system in this repository. Optionally, a web UI can be added later which would call the same services.

2. Application (Business Logic)
   - Importer: handles reading student rosters from CSV and validating records.
   - Student Service: CRUD operations for students, validation and mapping.
   - Attendance Service: Idempotent attendance marking, reporting, and business rules.

3. Persistence
   - SQLite database holds student and attendance records. The schema is simple to avoid cognitive overhead when learning.

Data Flow
- A user runs a CLI script to import students. The importer parses CSV rows and calls the Student Service to persist or update students.
- To mark attendance, the CLI/script calls Attendance Service with `student_id` and `name` (name optional). The Attendance Service ensures the DB schema exists, checks for duplicate marking for the same date, and inserts a new attendance row only if needed.

Extensibility
- Replace SQLite with Postgres: swap the persistence layer and update `ensure_db` and connection helper functions.
- Add a Web UI or API: implement an HTTP layer that calls the same services (StudentSvc, AttendanceSvc) so business rules remain centralized.

Testing
- Unit tests should focus on services and edge cases: CSV malformed rows, duplicate attendance attempts, DB I/O errors.
- Integration tests (small) should create a temporary DB file (or in-memory DB) and assert full flows.

Operational Notes
- Backups: if you rely on attendance.db long-term, add a scheduled backup or migration to server-grade DB.
- Concurrency: SQLite is fine for light usage. For many concurrent writers, migrate to a client-server DB.

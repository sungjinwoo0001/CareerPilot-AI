
import sqlite3
import json

DB_NAME = "careerpilot.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            profile_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skill_gaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER,
            target_role TEXT,
            analysis_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roadmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER,
            roadmap_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER,
            question TEXT,
            answer TEXT,
            score REAL,
            feedback_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER,
            company TEXT,
            role TEXT,
            job_url TEXT,
            status TEXT,
            response TEXT,
            notes TEXT,
            applied_date TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_profile(name, profile):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO profiles (name, profile_data) VALUES (?, ?)",
        (name, json.dumps(profile))
    )

    profile_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return profile_id


def get_latest_profile():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, profile_data
        FROM profiles
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "name": row[1],
            "profile": json.loads(row[2])
        }

    return None


def save_skill_gap(profile_id, target_role, analysis):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO skill_gaps (profile_id, target_role, analysis_data) VALUES (?, ?, ?)",
        (profile_id, target_role, json.dumps(analysis))
    )

    conn.commit()
    conn.close()


def save_roadmap(profile_id, roadmap):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO roadmaps (profile_id, roadmap_data) VALUES (?, ?)",
        (profile_id, json.dumps(roadmap))
    )

    conn.commit()
    conn.close()


def save_interview(profile_id, question, answer, evaluation):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO interviews
        (profile_id, question, answer, score, feedback_data)
        VALUES (?, ?, ?, ?, ?)
    """, (
        profile_id,
        question,
        answer,
        evaluation.get("score", 0),
        json.dumps(evaluation)
    ))

    conn.commit()
    conn.close()


def save_application(profile_id, application):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO applications
        (profile_id, company, role, job_url, status, response, notes, applied_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        profile_id,
        application["company"],
        application["role"],
        application.get("job_url", ""),
        application.get("status", "Applied"),
        application.get("response", "Pending"),
        application.get("notes", ""),
        application.get("applied_date", "")
    ))

    conn.commit()
    conn.close()


def get_applications(profile_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT company, role, job_url, status, response, notes, applied_date
        FROM applications
        WHERE profile_id = ?
        ORDER BY rowid DESC
    """, (profile_id,))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "company": row[0],
            "role": row[1],
            "job_url": row[2],
            "status": row[3],
            "response": row[4],
            "notes": row[5],
            "applied_date": row[6]
        }
        for row in rows
    ]

def update_application_record(
    company, role, status, response, notes
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE applications
        SET status = ?, response = ?, notes = ?
        WHERE rowid = (
            SELECT MAX(rowid)
            FROM applications
            WHERE company = ? AND role = ?
        )
    """, (status, response, notes, company, role))

    conn.commit()
    conn.close()

def fix_application_database():
    conn = get_connection()
    cursor = conn.cursor()

    required_columns = {
        "profile_id": "INTEGER",
        "job_url": "TEXT",
        "status": "TEXT DEFAULT 'Applied'",
        "response": "TEXT DEFAULT 'Pending'",
        "notes": "TEXT",
        "applied_date": "TEXT"
    }

    columns = {
        row[1] for row in cursor.execute(
            "PRAGMA table_info(applications)"
        ).fetchall()
    }

    for column, definition in required_columns.items():
        if column not in columns:
            cursor.execute(
                f"ALTER TABLE applications ADD COLUMN {column} {definition}"
            )

    conn.commit()
    conn.close()

def fix_interview_database():
    conn = get_connection()
    cursor = conn.cursor()

    columns = {
        row[1] for row in cursor.execute(
            "PRAGMA table_info(interviews)"
        ).fetchall()
    }

    if "feedback_data" not in columns:
        cursor.execute(
            "ALTER TABLE interviews ADD COLUMN feedback_data TEXT"
        )

    conn.commit()
    conn.close()

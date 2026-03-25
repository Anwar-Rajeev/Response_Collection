import os
import sqlite3
import secrets
import string
from datetime import datetime
from typing import Dict, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "pulsecloud.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_code TEXT UNIQUE NOT NULL,
            question TEXT,
            is_active INTEGER DEFAULT 1,
            public_url TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            response_text TEXT NOT NULL,
            normalized_text TEXT NOT NULL,
            submitted_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        )
        """
    )
    conn.commit()
    conn.close()


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def generate_session_code(length: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def deactivate_all_sessions():
    conn = get_connection()
    conn.execute("UPDATE sessions SET is_active = 0, updated_at = ?", (_now(),))
    conn.commit()
    conn.close()


def create_session(question: str, public_url: Optional[str] = None) -> Dict:
    deactivate_all_sessions()
    conn = get_connection()
    cur = conn.cursor()
    session_code = generate_session_code()
    now = _now()
    cur.execute(
        """
        INSERT INTO sessions (session_code, question, is_active, public_url, created_at, updated_at)
        VALUES (?, ?, 1, ?, ?, ?)
        """,
        (session_code, question.strip(), public_url.strip() if public_url else None, now, now),
    )
    conn.commit()
    session_id = cur.lastrowid
    conn.close()
    return get_session_by_id(session_id)


def get_session_by_id(session_id: int) -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_active_session() -> Optional[Dict]:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM sessions WHERE is_active = 1 ORDER BY id DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_active_question(question: str):
    active = get_active_session()
    if not active:
        return
    conn = get_connection()
    conn.execute(
        "UPDATE sessions SET question = ?, updated_at = ? WHERE id = ?",
        (question.strip(), _now(), active["id"]),
    )
    conn.commit()
    conn.close()


def update_public_url(public_url: str):
    active = get_active_session()
    if not active:
        return
    conn = get_connection()
    conn.execute(
        "UPDATE sessions SET public_url = ?, updated_at = ? WHERE id = ?",
        (public_url.strip(), _now(), active["id"]),
    )
    conn.commit()
    conn.close()


def close_active_session():
    active = get_active_session()
    if not active:
        return
    conn = get_connection()
    conn.execute(
        "UPDATE sessions SET is_active = 0, updated_at = ? WHERE id = ?",
        (_now(), active["id"]),
    )
    conn.commit()
    conn.close()


def clear_active_question():
    active = get_active_session()
    if not active:
        return
    conn = get_connection()
    conn.execute(
        "UPDATE sessions SET question = '', updated_at = ? WHERE id = ?",
        (_now(), active["id"]),
    )
    conn.commit()
    conn.close()


def normalize_response(text: str) -> str:
    return " ".join(text.strip().lower().split())


def add_response(session_id: int, response_text: str):
    cleaned = response_text.strip()
    if not cleaned:
        raise ValueError("Response cannot be empty")
    normalized = normalize_response(cleaned)
    conn = get_connection()
    conn.execute(
        """
        INSERT INTO responses (session_id, response_text, normalized_text, submitted_at)
        VALUES (?, ?, ?, ?)
        """,
        (session_id, cleaned, normalized, _now()),
    )
    conn.commit()
    conn.close()


def get_responses(session_id: int) -> List[Dict]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM responses WHERE session_id = ? ORDER BY id DESC",
        (session_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def count_responses(session_id: int) -> int:
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) AS total FROM responses WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    conn.close()
    return int(row["total"]) if row else 0


def clear_responses(session_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM responses WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()


def clear_all_data():
    conn = get_connection()
    conn.execute("DELETE FROM responses")
    conn.execute("DELETE FROM sessions")
    conn.commit()
    conn.close()

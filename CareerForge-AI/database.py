import sqlite3, json
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "careerforge.db"

def connect():
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    with connect() as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            target_role TEXT NOT NULL,
            result_json TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )""")

def create_user(username, password_hash):
    try:
        with connect() as conn:
            conn.execute("INSERT INTO users(username,password_hash) VALUES (?,?)", (username, password_hash))
        return True
    except sqlite3.IntegrityError:
        return False

def find_user(username):
    with connect() as conn:
        return conn.execute("SELECT id,username,password_hash FROM users WHERE username=?", (username,)).fetchone()

def save_analysis(user_id, role, result):
    with connect() as conn:
        conn.execute("INSERT INTO analyses(user_id,target_role,result_json) VALUES (?,?,?)",
                     (user_id, role, json.dumps(result, ensure_ascii=False, default=str)))

def history_for_user(user_id, limit=30):
    with connect() as conn:
        return conn.execute("SELECT id,target_role,created_at FROM analyses WHERE user_id=? ORDER BY id DESC LIMIT ?",
                            (user_id, limit)).fetchall()

def get_analysis(user_id, analysis_id):
    with connect() as conn:
        row = conn.execute("SELECT result_json,target_role FROM analyses WHERE user_id=? AND id=?",
                           (user_id, analysis_id)).fetchone()
    if not row: return None
    return {"result": json.loads(row["result_json"]), "target_role": row["target_role"]}

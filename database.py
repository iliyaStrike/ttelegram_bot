import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
    code TEXT PRIMARY KEY,
    file_id TEXT,
    name TEXT
)
""")

conn.commit()


def add_file(code, file_id, name):
    cursor.execute(
        "INSERT OR REPLACE INTO files VALUES (?, ?, ?)",
        (code, file_id, name)
    )
    conn.commit()


def get_file(code):
    cursor.execute("SELECT file_id FROM files WHERE code=?", (code,))
    result = cursor.fetchone()
    return result[0] if result else None
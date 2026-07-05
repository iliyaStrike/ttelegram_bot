import sqlite3

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
    code TEXT PRIMARY KEY,
    file_id TEXT
)
""")

conn.commit()


def add_file(code, file_id):
    cursor.execute("INSERT OR REPLACE INTO files VALUES (?, ?)", (code, file_id))
    conn.commit()


def get_file(code):
    cursor.execute("SELECT file_id FROM files WHERE code=?", (code,))
    result = cursor.fetchone()
    return result[0] if result else None